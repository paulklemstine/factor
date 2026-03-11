#!/usr/bin/env python3
"""
Round 8b: Multi-Base Long Multiplication Factoring

KEY INSIGHT: Binary long multiplication has carry entanglement.
But in different bases, the carry structure is DIFFERENT.
Information that is "entangled" in one base may be "free" in another.

Approach:
1. Convert n to multiple bases (2, 3, 5, 7, 10, etc.)
2. In each base B, the LOWEST digit of x and y is constrained:
   x_0 * y_0 ≡ n_0 (mod B)
   This gives us x mod B and y mod B (small enumeration).
3. For the SECOND digit, we get x mod B^2 and y mod B^2.
4. COMBINING across bases via CRT:
   From base 2: x mod 2^k
   From base 3: x mod 3^k
   Combined: x mod (2^k * 3^k) = x mod 6^k
   This is EXPONENTIALLY more information per digit processed!

5. The beauty: in base B, the first digit gives x mod B with O(B) work.
   Across M coprime bases, CRT gives x mod (B1*B2*...*BM).
   When this product > sqrt(n), we've found x.

   Cost: O(B1 + B2 + ... + BM) per digit level
   vs. binary alone: O(2^k) for k digits.

   This is essentially a STRUCTURED version of RNS that tracks carry properly!

6. CRUCIAL DIFFERENCE from pure RNS: we process digit-by-digit (with carries)
   in EACH base, so we maintain the constraint structure. But we combine
   across bases using CRT for the carry-free benefit.
"""

import math
import random
import time
from itertools import product as iterproduct

LOG_FILE = "factoring_log.md"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg)

def is_prime_miller_rabin(n, k=25):
    if n < 2: return False
    if n == 2 or n == 3: return True
    if n % 2 == 0: return False
    r, d = 0, n - 1
    while d % 2 == 0: r += 1; d //= 2
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False
    return True

def next_prime(n):
    if n <= 2: return 2
    if n % 2 == 0: n += 1
    while not is_prime_miller_rabin(n): n += 2
    return n

def gen_semiprime(bits):
    half = bits // 2
    p = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    q = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    while p == q: q = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    if p > q: p, q = q, p
    return p, q, p * q

def to_base(n, base):
    """Convert n to digits in given base (LSB first)."""
    if n == 0: return [0]
    digits = []
    while n > 0:
        digits.append(n % base)
        n //= base
    return digits

def from_base(digits, base):
    """Convert digits (LSB first) back to integer."""
    result = 0
    for i in range(len(digits) - 1, -1, -1):
        result = result * base + digits[i]
    return result

def extended_gcd(a, b):
    if a == 0: return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x

def crt_two(r1, m1, r2, m2):
    """CRT for two congruences: x ≡ r1 mod m1, x ≡ r2 mod m2."""
    g, p, q = extended_gcd(m1, m2)
    if (r2 - r1) % g != 0:
        return None, None  # No solution
    lcm = m1 * m2 // g
    sol = (r1 + m1 * ((r2 - r1) // g) * p) % lcm
    return sol, lcm

# ============================================================
# METHOD 1: Single-digit multi-base (Hensel level 1 across bases)
# ============================================================
def multibase_digit1(n, bases=None):
    """
    For each base B, find all (x0, y0) where x0 * y0 ≡ n mod B.
    Combine across bases via CRT to narrow down x mod (product of bases).
    """
    if bases is None:
        bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

    # For each base, find valid (x0, y0) pairs
    per_base_solutions = {}
    for B in bases:
        nB = n % B
        solutions = []
        for x0 in range(1, B):  # x0 != 0 (factors > 0)
            for y0 in range(x0, B):  # y0 >= x0 (symmetry breaking)
                if (x0 * y0) % B == nB:
                    solutions.append((x0, y0))
        per_base_solutions[B] = solutions

    # Progressive CRT: combine bases one at a time
    # Start with all solutions from first base
    candidates = []
    first_base = bases[0]
    for x0, y0 in per_base_solutions[first_base]:
        candidates.append((x0, first_base, y0, first_base))
        # (x_val, x_mod, y_val, y_mod)

    sqrt_n = math.isqrt(n)

    for base_idx in range(1, len(bases)):
        B = bases[base_idx]
        new_candidates = []

        for x_val, x_mod, y_val, y_mod in candidates:
            for x0_b, y0_b in per_base_solutions[B]:
                # Combine x_val mod x_mod with x0_b mod B
                x_combined, x_new_mod = crt_two(x_val, x_mod, x0_b, B)
                if x_combined is None:
                    continue
                y_combined, y_new_mod = crt_two(y_val, y_mod, y0_b, B)
                if y_combined is None:
                    continue

                # Size pruning: x and y should be <= sqrt(n) * 2 (roughly)
                # More precisely: x * y = n, so x <= n and y <= n
                # But if x_new_mod > sqrt(n), x_combined IS x (mod is larger than value)
                if x_new_mod > sqrt_n:
                    # x is determined! Check if it divides n.
                    if x_combined > 1 and x_combined < n and n % x_combined == 0:
                        return x_combined
                    if y_combined > 1 and y_combined < n and n % y_combined == 0:
                        return y_combined
                    continue  # Skip if not a factor

                new_candidates.append((x_combined, x_new_mod, y_combined, y_new_mod))

        candidates = new_candidates

        # Prune: remove candidates where x * y can't possibly equal n
        pruned = []
        for x_val, x_mod, y_val, y_mod in candidates:
            # x is x_val + k * x_mod for some k >= 0
            # Minimum x: x_val (if x_val > 0) else x_mod
            x_min = x_val if x_val > 0 else x_mod
            # Maximum y for this x_min: n / x_min
            if x_min > 0:
                y_max = n // x_min + 1
                # y is y_val + j * y_mod, minimum y is y_val or y_mod
                y_min = y_val if y_val > 0 else y_mod
                # Check feasibility
                if x_min <= n and y_min <= n:
                    pruned.append((x_val, x_mod, y_val, y_mod))
        candidates = pruned

        log(f"    After base {B}: {len(candidates)} candidates, modulus={x_mod if candidates else '?'}")

        if len(candidates) == 0:
            break
        if len(candidates) > 1_000_000:
            # Too many — prune harder
            candidates = candidates[:1_000_000]

    # Final: check remaining candidates
    for x_val, x_mod, y_val, y_mod in candidates[:100000]:
        if x_mod > sqrt_n:
            if x_val > 1 and n % x_val == 0:
                return x_val
        else:
            # Enumerate x = x_val + k * x_mod
            x = x_val if x_val > 0 else x_mod
            while x <= sqrt_n:
                if x > 1 and n % x == 0:
                    return x
                x += x_mod

    return None

# ============================================================
# METHOD 2: Multi-level Hensel in each base, then CRT
# ============================================================
def multibase_hensel(n, bases=None, levels=None):
    """
    For each base B, do Hensel lifting: find x mod B^k for increasing k.
    Then combine across bases via CRT.

    In base B, lifting from level k to k+1:
    Given x*y ≡ n mod B^k, find x*y ≡ n mod B^(k+1).
    x = x_k + a * B^k, y = y_k + b * B^k where a,b ∈ {0,...,B-1}
    (x_k + a*B^k)(y_k + b*B^k) ≡ n mod B^(k+1)
    x_k*y_k + (a*y_k + b*x_k)*B^k ≡ n mod B^(k+1)
    So: a*y_k + b*x_k ≡ (n - x_k*y_k)/B^k mod B
    """
    if bases is None:
        bases = [2, 3, 5, 7, 11, 13]
    if levels is None:
        # How many levels per base? Enough that B^levels > n^(1/(2*len(bases)))
        target_per_base = math.log(n) / (2 * len(bases))
        levels = {B: max(2, int(math.ceil(target_per_base / math.log(B)))) for B in bases}

    sqrt_n = math.isqrt(n)

    # For each base, compute solutions mod B^levels[B]
    per_base_solutions = {}  # base -> list of (x_mod_val, y_mod_val, modulus)

    for B in bases:
        L = levels[B]
        modulus = B

        # Level 0: x0 * y0 ≡ n mod B
        nB = n % B
        solutions = []
        for x0 in range(B):
            for y0 in range(B):
                if (x0 * y0) % B == nB:
                    solutions.append((x0, y0))

        # Hensel lift through levels
        for lev in range(1, L):
            new_mod = modulus * B
            n_mod = n % new_mod
            new_solutions = []

            for x_k, y_k in solutions:
                residual = (n_mod - x_k * y_k)
                if residual % modulus != 0:
                    continue  # Shouldn't happen if previous level was correct
                r = (residual // modulus) % B

                # Need: a*y_k + b*x_k ≡ r mod B
                for a in range(B):
                    for b in range(B):
                        if (a * y_k + b * x_k) % B == r:
                            x_new = x_k + a * modulus
                            y_new = y_k + b * modulus
                            if (x_new * y_new) % new_mod == n_mod:
                                new_solutions.append((x_new, y_new))

            solutions = new_solutions
            modulus = new_mod

            if not solutions:
                break

        per_base_solutions[B] = [(x, y, modulus) for x, y in solutions]
        log(f"    Base {B}: {len(solutions)} solutions mod {modulus}")

    # Now combine across bases via CRT
    # Start with solutions from first base
    if not per_base_solutions[bases[0]]:
        return None

    combined = [(x, y, m) for x, y, m in per_base_solutions[bases[0]]]

    for base_idx in range(1, len(bases)):
        B = bases[base_idx]
        if B not in per_base_solutions or not per_base_solutions[B]:
            continue

        new_combined = []
        for x1, y1, m1 in combined:
            for x2, y2, m2 in per_base_solutions[B]:
                x_c, x_m = crt_two(x1, m1, x2, m2)
                if x_c is None:
                    continue
                y_c, y_m = crt_two(y1, m1, y2, m2)
                if y_c is None:
                    continue

                # Check if modulus is large enough to determine factors
                if x_m > sqrt_n:
                    if x_c > 1 and x_c < n and n % x_c == 0:
                        return x_c
                    if y_c > 1 and y_c < n and n % y_c == 0:
                        return y_c
                else:
                    new_combined.append((x_c, y_c, x_m))

        combined = new_combined
        log(f"    After combining base {B}: {len(combined)} candidates")

        if len(combined) > 500_000:
            combined = combined[:500_000]  # Cap

        if not combined:
            break

    # Final verification
    for x_val, y_val, mod in combined[:100000]:
        if mod > sqrt_n:
            if x_val > 1 and n % x_val == 0:
                return x_val
            if y_val > 1 and n % y_val == 0:
                return y_val
        else:
            x = x_val
            while x <= sqrt_n and x > 0:
                if n % x == 0:
                    return x
                x += mod

    return None

# ============================================================
# METHOD 3: Base-2 Hensel + CRT with small prime moduli
# ============================================================
def hensel_crt_hybrid(n, hensel_bits=20, small_primes=None):
    """
    Hybrid: do Hensel lifting in base 2 up to 2^hensel_bits,
    then independently solve n ≡ x*y mod p for small primes p,
    and combine via CRT.

    This gives x mod (2^hensel_bits * p1 * p2 * ...) which could
    exceed sqrt(n) with enough primes.
    """
    if small_primes is None:
        small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

    sqrt_n = math.isqrt(n)

    # Step 1: Hensel lift in base 2
    mod2 = 1 << hensel_bits
    n_mod = n % mod2

    # Find all x mod 2^hensel_bits where x * y ≡ n mod 2^hensel_bits
    # for some y. This means: for each odd x in [1, mod2), compute
    # y = n * x^(-1) mod 2^hensel_bits. If y is also odd, it's valid.
    hensel_solutions = []
    for trial in range(1, mod2, 2):  # Only odd x
        try:
            y_mod = (n_mod * pow(trial, -1, mod2)) % mod2
            if y_mod % 2 == 1:  # y must be odd too
                if trial <= y_mod:  # symmetry breaking
                    hensel_solutions.append((trial, y_mod))
        except ValueError:
            continue

    log(f"    Hensel base-2 ({hensel_bits} bits): {len(hensel_solutions)} solutions")

    if not hensel_solutions:
        return None

    # Step 2: For each small prime p, find x mod p
    prime_solutions = {}
    for p in small_primes:
        g = math.gcd(p, n)
        if 1 < g < n:
            return g  # Lucky!
        np = n % p
        sols = []
        for x0 in range(1, p):
            y0 = (np * pow(x0, -1, p)) % p
            if y0 > 0:
                sols.append((x0, y0))
        prime_solutions[p] = sols

    # Step 3: Progressive CRT combining Hensel + primes
    # Start with Hensel solutions
    candidates = [(x, y, mod2) for x, y in hensel_solutions]

    for p in small_primes:
        if p not in prime_solutions:
            continue

        new_candidates = []
        for x_val, y_val, x_mod in candidates:
            for x_p, y_p in prime_solutions[p]:
                x_c, x_m = crt_two(x_val, x_mod, x_p, p)
                if x_c is None:
                    continue
                y_c, y_m = crt_two(y_val, x_mod, y_p, p)
                if y_c is None:
                    continue

                if x_m > sqrt_n:
                    if x_c > 1 and x_c < n and n % x_c == 0:
                        return x_c
                    if y_c > 1 and y_c < n and n % y_c == 0:
                        return y_c
                else:
                    new_candidates.append((x_c, y_c, x_m))

        candidates = new_candidates
        log(f"    +prime {p}: {len(candidates)} candidates, mod={candidates[0][2] if candidates else '?'}")

        if not candidates:
            break
        if len(candidates) > 2_000_000:
            candidates = candidates[:2_000_000]

    # Final check
    for x_val, y_val, mod in candidates[:500000]:
        if mod > sqrt_n:
            if x_val > 1 and n % x_val == 0:
                return x_val
        else:
            x = x_val if x_val > 0 else mod
            count = 0
            while x <= sqrt_n and count < 1000:
                if n % x == 0 and x > 1:
                    return x
                x += mod
                count += 1

    return None

# ============================================================
# METHOD 4: Multi-base column-by-column (unified)
# ============================================================
def multibase_column_unified(n, bases=None, max_states=1_000_000):
    """
    Process MULTIPLE bases simultaneously, column by column.
    At each step, advance the base with the FEWEST current states
    (most constrained). This is like running multiple SAT solvers
    and cross-referencing their partial results.

    After each advance in any base, CRT-combine with other bases
    to check if we've determined enough.
    """
    if bases is None:
        bases = [2, 3, 5, 7]

    sqrt_n = math.isqrt(n)

    # State per base: dict of carry -> list of (x_mod, y_mod)
    base_states = {}
    base_moduli = {}

    for B in bases:
        nB = n % B
        states = {}  # carry -> [(x_val, y_val)]
        for x0 in range(B):
            for y0 in range(B):
                prod = x0 * y0
                if prod % B == nB:
                    carry = prod // B
                    if carry not in states:
                        states[carry] = []
                    states[carry].append((x0, y0))
        base_states[B] = states
        base_moduli[B] = B

    # Iterate: advance the most constrained base
    for iteration in range(200):
        # Find base with fewest total states
        best_base = None
        min_states = float('inf')
        for B in bases:
            total = sum(len(v) for v in base_states[B].values())
            if total < min_states and total > 0:
                min_states = total
                best_base = B

        if best_base is None:
            break

        B = best_base
        old_mod = base_moduli[B]
        new_mod = old_mod * B
        n_digit = (n // old_mod) % B  # Next digit of n in this base

        new_states = {}
        for old_carry, solutions in base_states[B].items():
            for x_val, y_val in solutions:
                # Lift: x = x_val + a * old_mod, y = y_val + b * old_mod
                # Column sum for this level involves cross products + carry
                for a in range(B):
                    for b in range(B):
                        x_new = x_val + a * old_mod
                        y_new = y_val + b * old_mod

                        # Compute the column contribution at this level
                        # The full product mod new_mod should equal n mod new_mod
                        if (x_new * y_new) % new_mod == n % new_mod:
                            new_carry = (x_new * y_new) // new_mod
                            if new_carry not in new_states:
                                new_states[new_carry] = []
                            new_states[new_carry].append((x_new, y_new))

        base_states[B] = new_states
        base_moduli[B] = new_mod

        total_states = sum(len(v) for v in new_states.values())
        log(f"    Base {B} level {iteration}: {total_states} states, mod={new_mod}")

        if total_states == 0:
            break
        if total_states > max_states:
            # Prune: keep only states with smallest carries
            sorted_carries = sorted(new_states.keys())
            pruned = {}
            count = 0
            for c in sorted_carries:
                if count + len(new_states[c]) <= max_states:
                    pruned[c] = new_states[c]
                    count += len(new_states[c])
                else:
                    pruned[c] = new_states[c][:max_states - count]
                    count = max_states
                    break
            base_states[B] = pruned

        # Cross-reference: try CRT between bases
        # Get a solution from each base and combine
        for B2 in bases:
            if B2 == B:
                continue
            m1 = base_moduli[B]
            m2 = base_moduli[B2]
            # Get first solution from each
            for carry1, sols1 in base_states[B].items():
                for x1, y1 in sols1[:10]:
                    for carry2, sols2 in base_states[B2].items():
                        for x2, y2 in sols2[:10]:
                            x_c, x_m = crt_two(x1 % m1, m1, x2 % m2, m2)
                            if x_c is None:
                                continue
                            if x_m > sqrt_n:
                                if x_c > 1 and x_c < n and n % x_c == 0:
                                    return x_c

        # Check if any single base has determined the answer
        for B2 in bases:
            if base_moduli[B2] > sqrt_n:
                for carry, sols in base_states[B2].items():
                    for x_val, y_val in sols:
                        if x_val > 1 and x_val < n and n % x_val == 0:
                            return x_val
                        if y_val > 1 and y_val < n and n % y_val == 0:
                            return y_val

    return None

# ============================================================
# RUN
# ============================================================
def main():
    random.seed(42424242)

    log("\n\n---\n")
    log("## Round 8b: Multi-Base Long Multiplication Factoring\n")
    log(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log("""
### Core Idea

Binary long multiplication has carry entanglement. But different bases
have DIFFERENT carry structures. By solving the factorization in multiple
bases independently and combining via CRT, we can potentially bypass
the entanglement barrier.

Key insight: In base B, the first digit gives x mod B with O(B²) work.
Across M coprime bases, CRT gives x mod (B1*B2*...*BM).
When this product > sqrt(n), x is fully determined.
""")

    test_cases = []
    for bits in [30, 40, 50, 60, 64, 72, 80, 96, 100]:
        p, q, n = gen_semiprime(bits)
        test_cases.append((bits, p, q, n))

    log("### Test Numbers\n")
    for bits, p, q, n in test_cases:
        log(f"- {bits}-bit: n={n}, p={p}, q={q}")

    methods = [
        ("Multi-base Digit-1 CRT", multibase_digit1),
        ("Multi-base Hensel + CRT", multibase_hensel),
        ("Hensel-CRT Hybrid (base2 + primes)", hensel_crt_hybrid),
        ("Multi-base Column Unified", multibase_column_unified),
    ]

    TIME_LIMIT = 120

    for method_name, func in methods:
        log(f"\n### {method_name}\n")
        for bits, p, q, n in test_cases:
            log(f"  {bits}-bit:")
            start = time.time()
            try:
                result = func(n)
                elapsed = time.time() - start
                if elapsed > TIME_LIMIT:
                    log(f"  - **TIMEOUT** ({elapsed:.1f}s)")
                elif result and n % result == 0 and 1 < result < n:
                    log(f"  - **SUCCESS** {elapsed:.4f}s -> {result}")
                    log(f"    verified: {n} = {result} x {n // result}")
                else:
                    log(f"  - FAILED ({elapsed:.2f}s)")
            except Exception as e:
                elapsed = time.time() - start
                log(f"  - ERROR: {type(e).__name__}: {e} ({elapsed:.2f}s)")

    log("""
### Multi-Base Analysis

**The fundamental question:** Does multi-base factoring reduce complexity?

Analysis of state counts:
- Single base B, k digits: O(B^k) states (from carry enumeration)
- M bases, 1 digit each: O(B1 * B2 * ... * BM) CRT combinations
- But each base independently has O(Bi) solutions per digit

The key tradeoff:
- More bases = larger CRT modulus (good: determines x faster)
- More bases = more CRT combinations (bad: exponential in M)
- Each base's Hensel lifting has O(B²) branching per level

**Critical insight:** The multi-base approach is equivalent to
Hensel lifting in base B1*B2*...*BM directly! The CRT combination
step creates the same number of solutions as direct lifting in
the composite base.

However, the multi-base approach has one advantage: **independent pruning**
in each base before CRT combination can reduce the search space.
If base-B constraints eliminate 50% of candidates, and base-B' eliminates
another 50%, the combined pruning is 75% — multiplicative benefit.

This is exactly what the RNS approach attempted, with the same limitation:
the total number of CRT combinations grows exponentially with the number
of bases, matching the carry-entanglement growth in binary.

**The carry entanglement barrier is BASE-INDEPENDENT.**
It's a fundamental property of integer multiplication, not an artifact
of binary representation. Changing bases reorganizes the computation
but doesn't reduce its inherent complexity.
""")

if __name__ == "__main__":
    main()
