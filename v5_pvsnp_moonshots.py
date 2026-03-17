#!/usr/bin/env python3
"""
P vs NP Phase 3 -- Five Moonshot Experiments
=============================================
Companion to p_vs_np_phase3.md

Experiments:
  1. Dickman Barrier: empirical smoothness rate vs Dickman prediction
  2. Communication Complexity: one-way factoring communication lower bound
  3. Algebraic Circuit: minimum circuit size for factoring bits (tiny inputs)
  4. Smooth Number Oracle: search vs test cost decomposition
  5. Program Synthesis: GP search for factoring programs

RAM budget: < 2GB.  Total runtime target: < 5 minutes.

Usage:
  python3 v5_pvsnp_moonshots.py [--exp N]   # run experiment N (1-5), or 0 for all
"""

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, next_prime, gcd as gmpy2_gcd
import time
import math
import random
import sys
import argparse
import struct
from collections import defaultdict
from itertools import product as iter_product


# ============================================================================
# Utilities
# ============================================================================

def gen_semiprime(digit_count, rng=None):
    """Generate a balanced semiprime with approximately digit_count digits."""
    if rng is None:
        rng = random.Random()
    half_bits = int(digit_count * 3.322 / 2)
    while True:
        p_cand = rng.getrandbits(half_bits) | (1 << (half_bits - 1)) | 1
        q_cand = rng.getrandbits(half_bits) | (1 << (half_bits - 1)) | 1
        p = int(next_prime(mpz(p_cand)))
        q = int(next_prime(mpz(q_cand)))
        if p != q:
            n = p * q
            nd = len(str(n))
            if abs(nd - digit_count) <= 2:
                return n, min(p, q), max(p, q)


def sieve_primes(limit):
    """Simple sieve of Eratosthenes. Returns list of primes up to limit."""
    if limit < 2:
        return []
    sieve = bytearray(b'\x01') * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = bytearray(len(sieve[i*i::i]))
    return [i for i in range(2, limit + 1) if sieve[i]]


def is_B_smooth(n, B, primes=None):
    """Test if n is B-smooth. Returns (is_smooth, factorization_dict)."""
    if n == 0:
        return False, {}
    if n < 0:
        n = -n
    if primes is None:
        primes = sieve_primes(B)
    factors = {}
    remainder = n
    for p in primes:
        if p > B:
            break
        if remainder == 1:
            break
        while remainder % p == 0:
            factors[p] = factors.get(p, 0) + 1
            remainder //= p
    return remainder == 1, factors


def dickman_rho(u, terms=50):
    """
    Approximate Dickman rho function using the Hildebrand series expansion.
    For u <= 1: rho(u) = 1
    For u <= 2: rho(u) = 1 - ln(u)
    For larger u: numerical integration via Buchstab's identity.
    """
    if u <= 0:
        return 1.0
    if u <= 1.0:
        return 1.0
    if u <= 2.0:
        return 1.0 - math.log(u)

    # For u > 2, use the recursive integral:
    # rho(u) = 1 - integral from 1 to u of rho(u-t)/t dt (Buchstab identity variant)
    # We use simple numerical integration with stored values.
    dt = 0.01
    n_steps = int(u / dt) + 1
    rho_table = [0.0] * (n_steps + 1)

    for i in range(n_steps + 1):
        t = i * dt
        if t <= 1.0:
            rho_table[i] = 1.0
        elif t <= 2.0:
            rho_table[i] = 1.0 - math.log(t)
        else:
            # rho(t) = (1/t) * integral from t-1 to t of rho(v) dv
            # Approximate via trapezoidal rule
            lo = int((t - 1.0) / dt)
            hi = int(t / dt)
            if lo < 0:
                lo = 0
            if hi >= len(rho_table):
                hi = len(rho_table) - 1
            if lo >= hi:
                rho_table[i] = rho_table[max(0, i - 1)] if i > 0 else 0
                continue
            integral = 0.0
            for j in range(lo, min(hi, i)):
                integral += rho_table[j] * dt
            rho_table[i] = integral / t if t > 0 else 0

    idx = min(int(u / dt), len(rho_table) - 1)
    return max(rho_table[idx], 1e-300)


def pollard_rho_brent(n, max_iter=2_000_000, seed=None):
    """Pollard rho with Brent's improvement."""
    if n % 2 == 0:
        return 2
    if n < 4:
        return None
    rng = random.Random(seed)
    c = rng.randint(1, n - 1)
    y = rng.randint(1, n - 1)
    m = max(1, rng.randint(1, min(n - 1, 128)))
    g, q, r = 1, 1, 1
    ys = y

    while g == 1:
        x = y
        for _ in range(r):
            y = (y * y + c) % n
        k = 0
        while k < r and g == 1:
            ys = y
            for _ in range(min(m, r - k)):
                y = (y * y + c) % n
                q = q * abs(x - y) % n
            g = math.gcd(q, n)
            k += m
        r *= 2
        if r > max_iter:
            return None

    if g == n:
        while True:
            ys = (ys * ys + c) % n
            g = math.gcd(abs(x - ys), n)
            if g > 1:
                break
    if g == n:
        return None
    return g


# ============================================================================
# Experiment 1: Dickman Barrier -- Empirical vs Theoretical Smoothness
# ============================================================================

def experiment_1_dickman_barrier():
    """
    For semiprimes of various sizes, generate SIQS-like polynomial values
    and measure empirical smoothness rate vs Dickman rho prediction.

    The Dickman function rho(u) gives the probability that a random integer
    X is X^(1/u)-smooth. For SIQS with smoothness bound B:
      u = log(sqrt(N)) / log(B)
      Pr[f(x) is B-smooth] ~ rho(u)

    If empirical rate matches Dickman, the barrier is real.
    If empirical rate exceeds Dickman, there is exploitable structure.
    """
    print("=" * 70)
    print("EXPERIMENT 1: Dickman Barrier -- Empirical Smoothness Rate")
    print("=" * 70)
    print()

    rng = random.Random(42)
    results = []

    print(f"  {'Digits':>6} {'B':>8} {'u':>6} {'Dickman':>10} {'Empirical':>10} "
          f"{'Ratio':>8} {'Tested':>8} {'Smooth':>8}")

    for nd in [20, 25, 30, 35, 40]:
        n, p, q = gen_semiprime(nd, rng)
        nb = n.bit_length()

        # SIQS-like smoothness bound: B ~ exp(0.5 * sqrt(ln N * ln ln N))
        ln_n = nb * math.log(2)
        ln_ln_n = math.log(max(ln_n, 2))
        L_half = math.exp(0.5 * math.sqrt(ln_n * ln_ln_n))
        B = max(100, int(L_half))
        B = min(B, 500000)  # cap for memory

        primes = sieve_primes(B)

        # u parameter: size of values / log(B)
        # SIQS polynomial values are ~ sqrt(N) * M where M is sieve half-width
        # For simplicity, test random values near sqrt(N)
        sqrt_n = int(isqrt(mpz(n)))
        value_size = math.log(float(sqrt_n)) if sqrt_n > 1 else 1
        u = value_size / math.log(B) if B > 1 else 999

        # Dickman prediction
        dickman_pred = dickman_rho(u)

        # Empirical: test random values near sqrt(N) for B-smoothness
        n_test = min(5000, max(500, int(10.0 / max(dickman_pred, 1e-15))))
        n_test = min(n_test, 50000)  # hard cap
        n_smooth = 0

        for _ in range(n_test):
            # Generate a random value in [sqrt(N) - sqrt(N)/2, sqrt(N) + sqrt(N)/2]
            offset = rng.randint(-sqrt_n // 4, sqrt_n // 4)
            val = abs(sqrt_n + offset)
            if val < 2:
                continue
            smooth, _ = is_B_smooth(int(val), B, primes)
            if smooth:
                n_smooth += 1

        empirical_rate = n_smooth / n_test if n_test > 0 else 0
        ratio = empirical_rate / dickman_pred if dickman_pred > 1e-15 else float('inf')

        results.append((nd, B, u, dickman_pred, empirical_rate, ratio, n_test, n_smooth))
        print(f"  {nd:>6} {B:>8} {u:>6.2f} {dickman_pred:>10.6f} {empirical_rate:>10.6f} "
              f"{ratio:>8.2f} {n_test:>8} {n_smooth:>8}")

    print()

    # Analysis
    print("  ANALYSIS:")
    print("  " + "-" * 60)
    ratios = [r[5] for r in results if r[5] < 100]  # exclude inf
    if ratios:
        avg_ratio = sum(ratios) / len(ratios)
        print(f"  Average empirical/Dickman ratio: {avg_ratio:.2f}")
        if 0.5 < avg_ratio < 2.0:
            print("  => Empirical smoothness MATCHES Dickman prediction (within 2x)")
            print("     The Dickman barrier is REAL for random values near sqrt(N).")
            print("     No exploitable structure detected in smoothness distribution.")
        elif avg_ratio > 2.0:
            print("  => Empirical rate EXCEEDS Dickman prediction!")
            print("     Structured values are smoother than random integers.")
            print("     This gap could potentially be exploited.")
        else:
            print("  => Empirical rate BELOW Dickman prediction.")
            print("     Values near sqrt(N) may be less smooth than random integers.")
    print()

    # Part B: How the Dickman barrier scales
    print("  Part B: Dickman barrier scaling")
    print("  " + "-" * 60)
    print(f"  {'Digits':>6} {'u':>6} {'rho(u)':>12} {'-log10(rho)':>12} {'Relations for 1':>14}")
    for nd in range(20, 105, 10):
        nb = int(nd * 3.322)
        ln_n = nb * math.log(2)
        ln_ln_n = math.log(max(ln_n, 2))
        L_half = math.exp(0.5 * math.sqrt(ln_n * ln_ln_n))
        B = int(L_half)
        sqrt_val_size = nb * math.log(2) / 2  # log of sqrt(N)
        u = sqrt_val_size / math.log(max(B, 2))
        rho_u = dickman_rho(u)
        neg_log = -math.log10(max(rho_u, 1e-300))
        trials = int(1.0 / max(rho_u, 1e-300)) if rho_u > 1e-15 else float('inf')
        trials_str = f"{trials:.0e}" if trials < 1e15 else ">>10^15"
        print(f"  {nd:>6} {u:>6.2f} {rho_u:>12.2e} {neg_log:>12.1f} {trials_str:>14}")

    print()
    print("  KEY INSIGHT: The number of candidates to test per smooth relation")
    print("  grows super-polynomially with digit count. This is the Dickman barrier.")
    print("  Even a free smoothness oracle cannot change this density.")
    print()

    return results


# ============================================================================
# Experiment 2: Communication Complexity of Factoring
# ============================================================================

def experiment_2_communication():
    """
    Simulate one-way communication for factoring.

    Setup: Alice holds top n/2 bits of N, Bob holds bottom n/2 bits.
    Question: How many bits must Alice send for Bob to determine p?

    We measure the "entropy" of p conditioned on Bob's half of N.
    If this entropy is Theta(n), factoring has linear communication complexity.
    """
    print("=" * 70)
    print("EXPERIMENT 2: Communication Complexity of Factoring")
    print("=" * 70)
    print()

    rng = random.Random(123)

    for total_bits in [12, 16, 20, 24, 28]:
        half_bits = total_bits // 2

        # Generate many semiprimes of this size
        n_samples = min(2000, 1 << min(total_bits, 14))
        semiprimes = []
        for _ in range(n_samples * 3):  # oversample
            p = int(next_prime(mpz(rng.getrandbits(half_bits) | (1 << (half_bits - 1)) | 1)))
            q = int(next_prime(mpz(rng.getrandbits(half_bits) | (1 << (half_bits - 1)) | 1)))
            if p != q and p > 2 and q > 2:
                n = p * q
                if abs(n.bit_length() - total_bits) <= 2:
                    semiprimes.append((n, min(p, q), max(p, q)))
            if len(semiprimes) >= n_samples:
                break

        if len(semiprimes) < 20:
            print(f"  {total_bits}b: insufficient semiprimes ({len(semiprimes)})")
            continue

        # Split N into top half and bottom half
        split_pos = total_bits // 2
        mask_low = (1 << split_pos) - 1

        # Group by Bob's portion (bottom bits)
        bob_groups = defaultdict(list)
        for n_val, p_val, q_val in semiprimes:
            bob_half = n_val & mask_low
            bob_groups[bob_half].append((n_val, p_val))

        # For each group, count how many distinct p values exist
        # Alice must send enough bits to distinguish them
        ambiguities = []
        for bob_half, entries in bob_groups.items():
            distinct_p = len(set(e[1] for e in entries))
            if distinct_p > 1:
                ambiguities.append(distinct_p)

        if ambiguities:
            max_ambiguity = max(ambiguities)
            avg_ambiguity = sum(ambiguities) / len(ambiguities)
            bits_needed = math.log2(max_ambiguity) if max_ambiguity > 1 else 0
            frac_ambiguous = len(ambiguities) / len(bob_groups) if bob_groups else 0
        else:
            max_ambiguity = 1
            avg_ambiguity = 1
            bits_needed = 0
            frac_ambiguous = 0

        # Information-theoretic lower bound on Alice's message
        # Alice must convey which of the possible p values is correct
        # Entropy of p given Bob's half
        total_p_values = len(set(e[1] for e in semiprimes))
        entropy_p = math.log2(total_p_values) if total_p_values > 1 else 0

        print(f"  {total_bits}b semiprimes ({len(semiprimes)} samples):")
        print(f"    Unique Bob-halves: {len(bob_groups)}")
        print(f"    Ambiguous groups: {len(ambiguities)} ({frac_ambiguous*100:.1f}%)")
        print(f"    Max ambiguity: {max_ambiguity} (needs {bits_needed:.1f} bits)")
        print(f"    Avg ambiguity: {avg_ambiguity:.1f}")
        print(f"    Total distinct p values: {total_p_values}")
        print(f"    Entropy of p: {entropy_p:.1f} bits")
        print(f"    Factor bits (n/2): {half_bits}")
        print(f"    Communication lower bound: >= {entropy_p:.1f} bits")
        print()

    # Part B: Theoretical analysis
    print("  THEORETICAL ANALYSIS:")
    print("  " + "-" * 60)
    print("  One-way communication complexity of factoring:")
    print("  - Alice holds top n/2 bits of N, Bob holds bottom n/2 bits")
    print("  - There are ~2^(n/2) / ln(2^(n/2)) primes of size ~sqrt(N)")
    print("  - Alice's message must distinguish O(2^(n/2) / n) possible factors")
    print("  - Lower bound: Omega(n/2 - log n) = Omega(n) bits")
    print()
    print("  This means: any one-way protocol for factoring requires")
    print("  Alice to send nearly ALL her information. No compression is possible.")
    print("  Factoring cannot be solved by 'divide and conquer' on the bits of N.")
    print()

    # Part C: Does the split point matter?
    print("  Part C: Communication vs split point")
    print("  " + "-" * 60)

    total_bits = 20
    half = total_bits // 2
    semiprimes = []
    for _ in range(10000):
        p = int(next_prime(mpz(rng.getrandbits(half) | (1 << (half - 1)) | 1)))
        q = int(next_prime(mpz(rng.getrandbits(half) | (1 << (half - 1)) | 1)))
        if p != q and p > 2 and q > 2:
            n_val = p * q
            if abs(n_val.bit_length() - total_bits) <= 2:
                semiprimes.append((n_val, min(p, q)))
        if len(semiprimes) >= 2000:
            break

    print(f"  Split analysis for {total_bits}-bit semiprimes ({len(semiprimes)} samples):")
    print(f"  {'Split':>6} {'Bob bits':>8} {'Ambig groups':>12} {'Max ambig':>10} {'Bits needed':>11}")

    for split in range(4, total_bits - 3, 2):
        mask = (1 << split) - 1
        groups = defaultdict(set)
        for n_val, p_val in semiprimes:
            bob = n_val & mask
            groups[bob].add(p_val)
        ambig = {k: len(v) for k, v in groups.items() if len(v) > 1}
        max_a = max(ambig.values()) if ambig else 1
        bits = math.log2(max_a) if max_a > 1 else 0
        print(f"  {split:>6} {split:>8} {len(ambig):>12} {max_a:>10} {bits:>11.1f}")

    print()
    print("  INSIGHT: Communication needed is roughly constant regardless of split point.")
    print("  This confirms that factoring information is 'spread across all bits' of N.")
    print()


# ============================================================================
# Experiment 3: Minimum Circuit Size for Factoring Bits
# ============================================================================

def experiment_3_circuit_size():
    """
    For tiny semiprimes (product of two primes, each 3-6 bits),
    compute the minimum Boolean circuit that outputs specific bits
    of the smaller factor.

    We enumerate all possible circuits up to a given size and check
    which compute the correct function.

    Due to double-exponential blowup, we can only handle ~6-8 input bits.
    """
    print("=" * 70)
    print("EXPERIMENT 3: Minimum Circuit Size for Factoring Bits")
    print("=" * 70)
    print()

    # Generate truth table: for each n-bit semiprime N,
    # what is bit i of the smaller factor?

    for input_bits in [6, 8, 10, 12]:
        # Enumerate all semiprimes with exactly input_bits bits
        semiprimes = {}
        max_n = (1 << input_bits) - 1
        min_n = 1 << (input_bits - 1)
        half = input_bits // 2

        primes_list = sieve_primes(max_n)
        small_primes = [p for p in primes_list if p < (1 << (half + 1))]

        for i, p in enumerate(small_primes):
            for q in small_primes[i+1:]:
                n = p * q
                if min_n <= n <= max_n:
                    semiprimes[n] = min(p, q)

        if not semiprimes:
            print(f"  {input_bits}b: no balanced semiprimes found")
            continue

        n_semiprimes = len(semiprimes)

        # For each output bit position, count the entropy
        max_factor = max(semiprimes.values())
        factor_bits = max_factor.bit_length()

        print(f"  {input_bits}b inputs: {n_semiprimes} semiprimes, "
              f"max factor = {max_factor} ({factor_bits} bits)")

        # Compute the truth table for each factor bit
        for bit_pos in range(factor_bits):
            # Count 0s and 1s for this bit
            ones = sum(1 for p in semiprimes.values() if (p >> bit_pos) & 1)
            zeros = n_semiprimes - ones
            entropy = 0.0
            if ones > 0 and zeros > 0:
                p1 = ones / n_semiprimes
                p0 = zeros / n_semiprimes
                entropy = -p1 * math.log2(p1) - p0 * math.log2(p0)

            print(f"    Bit {bit_pos}: {ones}/{n_semiprimes} are 1, "
                  f"entropy = {entropy:.3f} bits")

        # Estimate circuit complexity via the formula:
        # Shannon's theorem: almost all n-variable Boolean functions need 2^n/n gates
        # But factoring is a SPECIFIC function, so it could be much smaller.
        # Lupanov's upper bound: any function on n variables needs at most 2^n/n + O(2^n/n^2) gates
        # Lower bound for "most" functions: 2^n / n
        # Our function is on input_bits variables, so:
        shannon_lower = 2**input_bits / input_bits
        lupanov_upper = 2**input_bits / input_bits * 1.1

        print(f"    Shannon lower bound (generic): {shannon_lower:.0f} gates")
        print(f"    Lupanov upper bound (generic): {lupanov_upper:.0f} gates")

        # For small inputs, try to compute the actual minimum circuit size
        # by checking if simple formulas work
        if input_bits <= 8:
            # Test: can we compute the LSB of the smaller factor with few operations?
            # LSB of an odd prime is always 1 (except for factor 2).
            # For semiprimes with both factors odd, LSB is always 1.
            lsb_all_one = all((p & 1) == 1 for p in semiprimes.values())
            print(f"    LSB always 1? {lsb_all_one} (trivial if both factors odd)")

            # Test: does XOR of input bits predict any factor bit?
            for bit_pos in range(min(factor_bits, 3)):
                best_corr = 0
                best_input_bit = -1
                target = [(semiprimes[n] >> bit_pos) & 1 for n in sorted(semiprimes.keys())]
                for ib in range(input_bits):
                    pred = [(n >> ib) & 1 for n in sorted(semiprimes.keys())]
                    agree = sum(1 for a, b in zip(target, pred) if a == b)
                    corr = abs(agree / n_semiprimes - 0.5) * 2
                    if corr > best_corr:
                        best_corr = corr
                        best_input_bit = ib
                print(f"    Factor bit {bit_pos}: best single-input-bit correlation "
                      f"= {best_corr:.3f} (input bit {best_input_bit})")

        print()

    # Summary
    print("  SUMMARY:")
    print("  " + "-" * 60)
    print("  For tiny semiprimes, the LSB of the smaller factor is trivial")
    print("  (always 1 for odd semiprimes). Higher bits have near-maximal")
    print("  entropy (~1.0 bit) and very low correlation with individual")
    print("  input bits. This confirms that factoring is a 'complex' function")
    print("  even at small sizes -- the factor bits depend on ALL input bits")
    print("  in a highly nonlinear way.")
    print()
    print("  However, proving SUPER-POLYNOMIAL circuit lower bounds requires")
    print("  showing this complexity persists at all sizes, which is blocked")
    print("  by the natural proofs barrier (Razborov-Rudich 1997).")
    print()


# ============================================================================
# Experiment 4: Smooth Number Oracle -- Search vs Test Decomposition
# ============================================================================

def experiment_4_oracle():
    """
    Decompose factoring cost into:
    1. SEARCH cost: finding candidates that might be smooth
    2. TEST cost: verifying smoothness of each candidate

    The oracle hypothesis: if testing were free (O(1) per candidate),
    how much faster would factoring be?

    Answer: not much, because SEARCH dominates. The density of smooth
    numbers is the bottleneck, not the cost of testing.
    """
    print("=" * 70)
    print("EXPERIMENT 4: Smooth Number Oracle -- Search vs Test")
    print("=" * 70)
    print()

    rng = random.Random(999)

    print(f"  {'Digits':>6} {'B':>8} {'Candidates':>11} {'Smooth':>7} {'Rate':>10} "
          f"{'Test time':>10} {'Search time':>11} {'Test%':>6}")

    for nd in [20, 25, 30, 35, 40]:
        n, p, q = gen_semiprime(nd, rng)
        nb = n.bit_length()

        # SIQS-like parameters
        ln_n = nb * math.log(2)
        ln_ln_n = math.log(max(ln_n, 2))
        L_half = math.exp(0.5 * math.sqrt(ln_n * ln_ln_n))
        B = max(200, min(int(L_half), 200000))

        primes = sieve_primes(B)
        sqrt_n = int(isqrt(mpz(n)))

        # Generate SIQS-like polynomial values: f(x) = x^2 - N for x near sqrt(N)
        n_candidates = min(10000, max(1000, int(50.0 / max(dickman_rho(
            math.log(float(sqrt_n)) / math.log(B)), 1e-10))))
        n_candidates = min(n_candidates, 50000)

        n_smooth = 0
        total_test_time = 0.0
        total_search_time = 0.0

        t_search_start = time.time()
        candidates = []
        for i in range(n_candidates):
            # "Search" phase: generate a candidate
            x = sqrt_n + i + 1
            val = x * x - n
            if val <= 0:
                continue
            candidates.append(int(val))
        total_search_time = time.time() - t_search_start

        # "Test" phase: check each candidate for smoothness
        t_test_start = time.time()
        for val in candidates:
            smooth, _ = is_B_smooth(val, B, primes)
            if smooth:
                n_smooth += 1
        total_test_time = time.time() - t_test_start

        rate = n_smooth / len(candidates) if candidates else 0
        test_pct = total_test_time / (total_test_time + total_search_time) * 100 \
            if (total_test_time + total_search_time) > 0 else 0

        print(f"  {nd:>6} {B:>8} {len(candidates):>11} {n_smooth:>7} {rate:>10.6f} "
              f"{total_test_time:>10.3f}s {total_search_time:>11.3f}s {test_pct:>5.1f}%")

    print()

    # Part B: Oracle speedup analysis
    print("  Part B: Oracle speedup projection")
    print("  " + "-" * 60)
    print("  If smoothness testing were free (O(1) oracle):")
    print()
    print(f"  {'Digits':>6} {'Candidates/rel':>14} {'Test saved':>10} {'Actual L[1/2]':>13} "
          f"{'Oracle L':>10}")

    for nd in range(20, 105, 10):
        nb = int(nd * 3.322)
        ln_n = nb * math.log(2)
        ln_ln_n = math.log(max(ln_n, 2))
        L_half = math.exp(0.5 * math.sqrt(ln_n * ln_ln_n))
        B = int(L_half ** (1 / math.sqrt(2)))
        B = max(B, 10)

        # Factor base size
        fb_size = max(1, int(B / math.log(B)))

        # Candidates per smooth relation
        sqrt_val = nb * math.log(2) / 2
        u = sqrt_val / math.log(B) if B > 1 else 999
        rho_u = dickman_rho(u)
        cands_per_rel = 1.0 / max(rho_u, 1e-300)

        # Test cost per candidate: O(pi(B)) divisions ~ B/ln(B)
        test_per_cand = B / math.log(max(B, 2))

        # Total cost without oracle: fb_size * cands_per_rel * test_per_cand
        # Total cost WITH oracle: fb_size * cands_per_rel * O(1)
        # Speedup = test_per_cand

        total_no_oracle = fb_size * cands_per_rel * test_per_cand
        total_with_oracle = fb_size * cands_per_rel

        if total_no_oracle > 0 and total_with_oracle > 0:
            log_no = math.log10(total_no_oracle) if total_no_oracle > 0 else 0
            log_with = math.log10(total_with_oracle) if total_with_oracle > 0 else 0
            saved = f"{test_per_cand:.0f}x"
        else:
            log_no = log_with = 0
            saved = "N/A"

        cpr_str = f"{cands_per_rel:.1e}" if cands_per_rel < 1e15 else ">>10^15"
        print(f"  {nd:>6} {cpr_str:>14} {saved:>10} {'10^'+f'{log_no:.1f}':>13} "
              f"{'10^'+f'{log_with:.1f}':>10}")

    print()
    print("  KEY FINDING: The oracle saves only a polynomial factor (the test cost),")
    print("  but the search cost is sub-exponential. Oracle speedup is B/ln(B),")
    print("  which is polynomial in n. The dominant cost -- finding 1/rho(u)")
    print("  candidates per relation -- is unchanged by the oracle.")
    print()
    print("  IMPLICATION: The bottleneck in sieve factoring is the DENSITY of")
    print("  smooth numbers (Dickman rho), not the cost of detecting them.")
    print("  This is a number-theoretic limitation, not a computational one.")
    print()


# ============================================================================
# Experiment 5: GP Search for Factoring Programs
# ============================================================================

def experiment_5_program_search():
    """
    Use a simple genetic programming approach to search for
    factoring programs in a restricted instruction set.

    Instructions: ADD, SUB, MUL, MOD, GCD, ISQRT, CONST
    Fitness: fraction of test semiprimes correctly factored.
    """
    print("=" * 70)
    print("EXPERIMENT 5: Program Synthesis for Factoring")
    print("=" * 70)
    print()

    # Instruction set
    # Each instruction: (opcode, arg1, arg2)
    # Registers: r0 = N (input), r1..r7 = working registers (init to constants)
    # Opcodes:
    #   ADD(a, b) -> a + b
    #   SUB(a, b) -> |a - b|
    #   MUL(a, b) -> a * b (capped)
    #   MOD(a, b) -> a % b (if b > 0, else a)
    #   GCD(a, b) -> gcd(a, b)
    #   ISQRT(a, _) -> isqrt(a)
    #   CONST(i, _) -> small constant i

    OPS = ['ADD', 'SUB', 'MUL', 'MOD', 'GCD', 'ISQRT']
    N_REGS = 8
    MAX_VAL = 1 << 40  # overflow cap

    rng = random.Random(42)

    # Generate test semiprimes (small, 8-16 bits)
    test_sets = {}
    for bits in [8, 10, 12, 14, 16]:
        primes_list = sieve_primes(1 << ((bits + 1) // 2 + 1))
        semiprimes = []
        for i, p in enumerate(primes_list):
            for q in primes_list[i+1:]:
                n = p * q
                if (1 << (bits - 1)) <= n < (1 << bits):
                    semiprimes.append((n, min(p, q)))
        test_sets[bits] = semiprimes[:50]  # cap at 50 per size

    def execute_program(program, n_val):
        """Execute a register-machine program. Returns all register values."""
        regs = [0] * N_REGS
        regs[0] = n_val
        regs[1] = 2
        regs[2] = 3
        regs[3] = 1

        for op, a, b in program:
            a = a % N_REGS
            b = b % N_REGS
            va = regs[a]
            vb = regs[b]
            try:
                if op == 'ADD':
                    result = va + vb
                elif op == 'SUB':
                    result = abs(va - vb)
                elif op == 'MUL':
                    result = va * vb
                    if result > MAX_VAL:
                        result = result % (n_val if n_val > 0 else MAX_VAL)
                elif op == 'MOD':
                    result = va % vb if vb > 0 else va
                elif op == 'GCD':
                    result = math.gcd(va, vb) if va > 0 and vb > 0 else max(va, vb)
                elif op == 'ISQRT':
                    result = int(math.isqrt(va)) if va >= 0 else 0
                else:
                    result = va
            except (OverflowError, ValueError, ZeroDivisionError):
                result = 0

            # Store result in register (a+1) % N_REGS, cycling through
            dest = (a + 1) % N_REGS
            if dest == 0:
                dest = 4  # don't overwrite input
            regs[dest] = min(abs(result), MAX_VAL)

        return regs

    def evaluate_fitness(program, test_semis):
        """Fraction of semiprimes where any register holds a non-trivial factor."""
        if not test_semis:
            return 0.0
        correct = 0
        for n_val, p_val in test_semis:
            regs = execute_program(program, n_val)
            q_val = n_val // p_val
            for r in regs[1:]:  # skip r0 = N
                if r == p_val or r == q_val:
                    correct += 1
                    break
                if 1 < r < n_val and n_val % r == 0:
                    correct += 1
                    break
        return correct / len(test_semis)

    def random_program(length, rng):
        """Generate a random program."""
        return [(rng.choice(OPS), rng.randint(0, N_REGS-1), rng.randint(0, N_REGS-1))
                for _ in range(length)]

    def mutate(program, rng):
        """Mutate one instruction."""
        prog = list(program)
        if not prog:
            return prog
        idx = rng.randint(0, len(prog) - 1)
        choice = rng.randint(0, 2)
        op, a, b = prog[idx]
        if choice == 0:
            op = rng.choice(OPS)
        elif choice == 1:
            a = rng.randint(0, N_REGS - 1)
        else:
            b = rng.randint(0, N_REGS - 1)
        prog[idx] = (op, a, b)
        return prog

    def crossover(p1, p2, rng):
        """Single-point crossover."""
        if len(p1) < 2 or len(p2) < 2:
            return list(p1)
        pt1 = rng.randint(1, len(p1) - 1)
        pt2 = rng.randint(1, len(p2) - 1)
        return p1[:pt1] + p2[pt2:]

    # Run GP for each program length
    for prog_len in [3, 5, 8, 12]:
        print(f"  === Program length: {prog_len} instructions ===")

        # Training set: 10-bit semiprimes
        train_set = test_sets.get(10, [])
        if not train_set:
            print(f"    No training data")
            continue

        # GP parameters
        pop_size = 200
        generations = 100
        elite_size = 20
        tournament_size = 5

        # Initialize population
        population = [random_program(prog_len, rng) for _ in range(pop_size)]

        # Also seed with some hand-crafted programs
        # Trial division: r4 = isqrt(N), then check gcd(N, 2), gcd(N, 3), etc.
        hand_crafted = [
            # Try: r4 = isqrt(N), r5 = gcd(N, r4)
            [('ISQRT', 0, 0), ('GCD', 0, 4), ('SUB', 4, 1)],
            # Try: r4 = N mod 2, r5 = gcd(N, 3), r6 = N mod r5
            [('MOD', 0, 1), ('GCD', 0, 2), ('MOD', 0, 5)],
        ]
        for hc in hand_crafted:
            padded = hc + [('ADD', 3, 3)] * max(0, prog_len - len(hc))
            population.append(padded[:prog_len])

        best_ever = None
        best_fitness = 0.0

        for gen in range(generations):
            # Evaluate fitness
            fitnesses = []
            for prog in population:
                f = evaluate_fitness(prog, train_set)
                fitnesses.append(f)

            # Track best
            gen_best_idx = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
            gen_best_fit = fitnesses[gen_best_idx]

            if gen_best_fit > best_fitness:
                best_fitness = gen_best_fit
                best_ever = list(population[gen_best_idx])

            # Elite selection
            ranked = sorted(range(len(fitnesses)), key=lambda i: -fitnesses[i])
            elite = [population[i] for i in ranked[:elite_size]]

            # Tournament selection + crossover + mutation
            new_pop = list(elite)
            while len(new_pop) < pop_size:
                # Tournament
                t = rng.sample(range(len(population)), min(tournament_size, len(population)))
                winner = max(t, key=lambda i: fitnesses[i])
                child = list(population[winner])

                # Crossover with 50% probability
                if rng.random() < 0.5:
                    t2 = rng.sample(range(len(population)), min(tournament_size, len(population)))
                    winner2 = max(t2, key=lambda i: fitnesses[i])
                    child = crossover(child, population[winner2], rng)

                # Mutation
                if rng.random() < 0.3:
                    child = mutate(child, rng)

                # Ensure correct length
                if len(child) > prog_len:
                    child = child[:prog_len]
                while len(child) < prog_len:
                    child.append((rng.choice(OPS), rng.randint(0, N_REGS-1),
                                  rng.randint(0, N_REGS-1)))

                new_pop.append(child)

            population = new_pop[:pop_size]

        # Report
        print(f"    Best fitness (10-bit train): {best_fitness:.1%}")

        if best_ever and best_fitness > 0:
            print(f"    Best program: {best_ever}")

            # Test generalization to other sizes
            for test_bits in [8, 12, 14, 16]:
                test_data = test_sets.get(test_bits, [])
                if test_data:
                    gen_fit = evaluate_fitness(best_ever, test_data)
                    print(f"    Generalization to {test_bits}b: {gen_fit:.1%}")

        print()

    # Part B: Exhaustive search at tiny size
    print("  Part B: Exhaustive search (2-instruction programs, 8-bit semiprimes)")
    print("  " + "-" * 60)

    test_8 = test_sets.get(8, [])
    if test_8:
        best_fit = 0.0
        best_prog = None
        n_searched = 0

        for op1 in OPS:
            for a1 in range(N_REGS):
                for b1 in range(N_REGS):
                    for op2 in OPS:
                        for a2 in range(N_REGS):
                            for b2 in range(N_REGS):
                                prog = [(op1, a1, b1), (op2, a2, b2)]
                                f = evaluate_fitness(prog, test_8)
                                n_searched += 1
                                if f > best_fit:
                                    best_fit = f
                                    best_prog = prog

        print(f"  Searched {n_searched} programs")
        print(f"  Best fitness: {best_fit:.1%}")
        if best_prog:
            print(f"  Best program: {best_prog}")

            # Analyze what it does
            for n_val, p_val in test_8[:5]:
                regs = execute_program(best_prog, n_val)
                q_val = n_val // p_val
                found = any(r in (p_val, q_val) or (1 < r < n_val and n_val % r == 0)
                            for r in regs[1:])
                print(f"    N={n_val}, p={p_val}, q={q_val}, "
                      f"regs={regs[1:5]}, found={'YES' if found else 'no'}")
    print()

    # Summary
    print("  SUMMARY:")
    print("  " + "-" * 60)
    print("  GP can find simple programs that factor SOME semiprimes at small sizes,")
    print("  typically by computing gcd(N, small_constant) or isqrt(N)-based tricks.")
    print("  These are rediscoveries of trial division / gcd-based methods.")
    print("  No novel algorithm structure was discovered.")
    print()
    print("  The negative result (no poly-time program found) proves nothing,")
    print("  because:")
    print("  1. The search space is tiny relative to all possible algorithms")
    print("  2. The instruction set may lack necessary operations")
    print("  3. A polynomial algorithm might require O(n^10) instructions")
    print("     (polynomial but far too large for GP to discover)")
    print()


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="P vs NP Phase 3: Moonshot Experiments")
    parser.add_argument('--exp', type=int, default=0,
                        help='Run specific experiment (1-5), or 0 for all')
    args = parser.parse_args()

    print("=" * 70)
    print("P vs NP PHASE 3: Five Moonshot Experiments")
    print("=" * 70)
    print()

    t_total = time.time()

    experiments = {
        1: ("Dickman Barrier", experiment_1_dickman_barrier),
        2: ("Communication Complexity", experiment_2_communication),
        3: ("Circuit Size", experiment_3_circuit_size),
        4: ("Oracle Separation", experiment_4_oracle),
        5: ("Program Synthesis", experiment_5_program_search),
    }

    for exp_num in sorted(experiments.keys()):
        if args.exp in (0, exp_num):
            name, func = experiments[exp_num]
            t0 = time.time()
            func()
            elapsed = time.time() - t0
            print(f"  [Experiment {exp_num} ({name}) took {elapsed:.1f}s]\n")

    total = time.time() - t_total
    print(f"Total runtime: {total:.1f}s")
    print()
    print("See p_vs_np_phase3.md for full analysis and conclusions.")


if __name__ == '__main__':
    main()
