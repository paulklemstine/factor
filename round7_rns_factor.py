#!/usr/bin/env python3
"""
Round 7: RNS (Residue Number System) Based Factoring — Revised

CORE INSIGHT: Carry entanglement in binary multiplication causes exponential
state growth in SAT-based factoring. RNS eliminates carries entirely:
  (a*b) mod mi = ((a mod mi) * (b mod mi)) mod mi
Each modulus is independent — no carry propagation.

KEY IMPROVEMENT over v1: The naive approach gives mi-1 valid x residues per
prime modulus mi (almost no pruning). The real pruning comes from:
1. Combining x and y constraints: for each (x_i, y_i) pair, both x and y
   must be consistent across all moduli.
2. Aggressive range pruning at each CRT step: after combining k moduli with
   product M, if x ≡ r (mod M), the smallest valid x is r (or r+M, r+2M, ...),
   and we need 2 <= x <= sqrt(n). Fraction surviving ≈ sqrt(n)/M.
3. Tracking (x mod M, y mod M) pairs jointly, so both are CRT-consistent.

The critical transition: once M > sqrt(n), each (x mod M) uniquely determines
x in [2, sqrt(n)], giving a direct divisibility test.
"""

import math
import random
import time

LOG_FILE = "factoring_log.md"


def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg)


# ============================================================
# Miller-Rabin primality test and semiprime generation
# ============================================================
def is_prime_miller_rabin(n, k=20):
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def next_prime(n):
    if n <= 2:
        return 2
    if n % 2 == 0:
        n += 1
    while not is_prime_miller_rabin(n):
        n += 2
    return n


def gen_semiprime(bits):
    half = bits // 2
    p = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    q = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    while p == q:
        q = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    if p > q:
        p, q = q, p
    return p, q, p * q


# ============================================================
# Number theory helpers
# ============================================================
def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x1, y1 = extended_gcd(b % a, a)
    return g, y1 - (b // a) * x1, x1


def crt_two(r1, m1, r2, m2):
    """CRT for two congruences. Returns (solution, lcm) or None."""
    g, p, _ = extended_gcd(m1, m2)
    if (r2 - r1) % g != 0:
        return None
    lcm = m1 * m2 // g
    solution = (r1 + m1 * ((r2 - r1) // g) * p) % lcm
    return solution, lcm


def small_primes_list(count):
    """Generate first `count` primes."""
    primes = []
    candidate = 2
    while len(primes) < count:
        if all(candidate % p != 0 for p in primes):
            primes.append(candidate)
        candidate += 1
    return primes


# ============================================================
# RNS Factoring — Joint (x, y) tracking with range pruning
# ============================================================

def find_xy_pairs_mod_m(n_mod_m, m):
    """Find all (x_i, y_i) pairs where x_i * y_i ≡ n_mod_m (mod m).
    Both x_i, y_i in [1, m-1]. Returns list of (x_i, y_i)."""
    pairs = []
    for x_i in range(1, m):
        y_i = (n_mod_m * pow(x_i, -1, m)) % m
        if y_i >= 1:
            pairs.append((x_i, y_i))
    return pairs


def count_valid_in_range(r, M, lo, hi):
    """Count how many x ≡ r (mod M) satisfy lo <= x <= hi."""
    if lo > hi:
        return 0
    if r == 0:
        first = M if M >= lo else M * ((lo + M - 1) // M)
    else:
        # smallest x ≡ r (mod M) with x >= lo
        first = r + M * max(0, (lo - r + M - 1) // M)
    if first > hi:
        return 0
    return (hi - first) // M + 1


def rns_factor(n, max_time=60.0, verbose=False):
    """
    Factor n using RNS with joint (x,y) CRT tracking.

    For semiprime n = p*q with p <= q:
      - x ranges over [2, isqrt(n)]
      - y = n/x ranges over [isqrt(n), n/2]

    We track x mod M only (y is determined by n/x once x is known).
    But we use the modular constraint on y to filter: if x ≡ r (mod mi),
    then y ≡ n_i * r^{-1} (mod mi), and this y residue must also be
    consistent with the y-range. Since both x and y residues are determined
    by x alone (y_i is a function of x_i), we just track x residues.

    The real pruning: at each step, enumerate x ≡ x_val (mod M) in [2, isqrt(n)]
    and keep only residues where at least one such x exists in range.
    """
    start = time.time()
    isqrt_n = math.isqrt(n)

    if n < 4:
        return None, 0, {}

    # Trivial factor check with small primes
    all_primes = small_primes_list(80)
    for p in all_primes:
        if n % p == 0 and p < n:
            return p, time.time() - start, {"trivial": True, "prime": p}

    # Use odd primes as moduli (skip 2: n is odd so x,y both odd, mod 2 gives 1 residue always)
    moduli = [p for p in all_primes if p > 2]

    # For each modulus, get valid x residues
    mod_data = []
    for mi in moduli:
        n_mod_mi = n % mi
        # All x_i in [1, mi-1] are valid (for prime mi not dividing n)
        # since y_i = n * x_i^{-1} mod mi is always in [1, mi-1].
        # So the filtering comes from RANGE constraints, not modular constraints.
        valid_x = list(range(1, mi))  # all are valid for prime mi not dividing n
        mod_data.append((mi, valid_x))

    # Sort by modulus size (smallest first = fewest residues)
    # Already sorted since we use primes in order

    # Initialize candidates: set of x residues mod M
    # Start with mod 3: x can be 1 or 2 mod 3
    mi0, vx0 = mod_data[0]
    candidates = set(vx0)  # x residues mod mi0
    M = mi0

    stats = {
        "moduli_used": 1,
        "max_candidates": len(candidates),
        "total_crt_ops": 0,
        "final_M": M,
    }

    if verbose:
        print(f"  mod {mi0}: {len(candidates)} candidates, M={M}")

    for step_idx in range(1, len(mod_data)):
        elapsed = time.time() - start
        if elapsed > max_time:
            break

        mi, valid_x_i = mod_data[step_idx]
        new_candidates = set()

        for x_val in candidates:
            for r_i in valid_x_i:
                result = crt_two(x_val, M, r_i, mi)
                if result is None:
                    continue
                x_new, M_new = result
                stats["total_crt_ops"] += 1

                # Range check: does any x ≡ x_new (mod M_new) exist in [2, isqrt_n]?
                if x_new < 2:
                    # First valid is x_new + M_new * ceil((2 - x_new) / M_new)
                    first_valid = x_new + M_new * ((2 - x_new + M_new - 1) // M_new)
                else:
                    first_valid = x_new

                if first_valid > isqrt_n:
                    continue  # No valid x in range

                new_candidates.add(x_new)

        M_new_val = M * mi  # since primes are coprime
        M = M_new_val
        candidates = new_candidates
        stats["moduli_used"] = step_idx + 1
        stats["final_M"] = M

        if len(candidates) > stats["max_candidates"]:
            stats["max_candidates"] = len(candidates)

        if verbose:
            print(f"  mod {mi}: {len(candidates)} candidates, M={M}, "
                  f"ratio={len(candidates)/M:.6e}, elapsed={elapsed:.2f}s")

        if not candidates:
            break

        # If M > isqrt_n, each candidate uniquely determines x — check all
        if M > isqrt_n:
            for x_val in candidates:
                if x_val >= 2 and n % x_val == 0:
                    stats["checked_final"] = len(candidates)
                    return x_val, time.time() - start, stats
            # None worked — shouldn't happen for true semiprime with p <= sqrt(n)
            # But p might be > sqrt(n) if factors are unbalanced... try y
            for x_val in candidates:
                y_val = n // x_val if x_val > 0 and n % x_val == 0 else 0
                if y_val > 1 and x_val * y_val == n:
                    return min(x_val, y_val), time.time() - start, stats
            break

        # If candidate count is growing too large, cap it
        MAX_CAND = 2_000_000
        if len(candidates) > MAX_CAND:
            # Convert to list, keep those closest to isqrt_n (balanced factors)
            cand_list = sorted(candidates, key=lambda c: abs(c - (isqrt_n % M)))
            candidates = set(cand_list[:MAX_CAND])

    # Fallback: enumerate remaining candidates
    if candidates and M > 0:
        t_enum = time.time()
        checked = 0
        for x_val in candidates:
            x = x_val if x_val >= 2 else x_val + M
            while x <= isqrt_n:
                if n % x == 0:
                    stats["fallback_checked"] = checked
                    return x, time.time() - start, stats
                x += M
                checked += 1
                if checked % 1000000 == 0 and time.time() - start > max_time:
                    break
            if time.time() - start > max_time:
                break
        stats["fallback_checked"] = checked

    return None, time.time() - start, stats


# ============================================================
# Main
# ============================================================
def main():
    random.seed(7777)

    log("\n---\n")
    log("## Round 7: RNS (Residue Number System) Factoring — Revised")
    log("")
    log("**Method**: For each small prime modulus mi, all x in [1,mi-1] satisfy")
    log("x*y ≡ n (mod mi) for some y. The real pruning comes from **range constraints**:")
    log("after combining k moduli (product M), only x ≡ r (mod M) with r in [2, sqrt(n)]")
    log("survive. Once M > sqrt(n), x is uniquely determined and we test divisibility.")
    log("")

    bit_sizes = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120]
    results = []

    for bits in bit_sizes:
        p, q, n = gen_semiprime(bits)
        actual_bits = n.bit_length()

        log(f"### {bits}-bit semiprime (actual {actual_bits} bits)")
        log(f"- n = {n}")
        log(f"- p = {p}, q = {q}")

        factor_found, elapsed, stats = rns_factor(n, max_time=60.0, verbose=True)

        if factor_found is not None:
            other = n // factor_found
            success = (factor_found * other == n) and factor_found > 1 and other > 1
            log(f"- **Result**: {'SUCCESS' if success else 'WRONG'} in {elapsed:.4f}s")
            log(f"- Found factor: {factor_found} (other: {other})")
        else:
            success = False
            log(f"- **Result**: FAILED in {elapsed:.4f}s")

        log(f"- Stats: {stats}")
        log("")

        results.append({
            "bits": bits,
            "actual_bits": actual_bits,
            "success": success,
            "time": elapsed,
            "stats": stats,
        })

    # Summary
    log("### Summary Table")
    log("")
    log("| Bits | Actual | Result | Time (s) | Moduli Used | Max Candidates | CRT Ops | Final M bits |")
    log("|------|--------|--------|----------|-------------|----------------|---------|--------------|")
    for r in results:
        s = r["stats"]
        moduli_used = s.get("moduli_used", "?")
        max_cand = s.get("max_candidates", "?")
        crt_ops = s.get("total_crt_ops", "?")
        fm = s.get("final_M", 1)
        fm_bits = fm.bit_length() if isinstance(fm, int) else "?"
        status = "OK" if r["success"] else "FAIL"
        log(f"| {r['bits']} | {r['actual_bits']} | {status} | "
            f"{r['time']:.4f} | {moduli_used} | {max_cand} | {crt_ops} | {fm_bits} |")

    log("")
    log("### Analysis of State Counts")
    log("")
    log("**Candidate growth analysis:**")
    log("- For prime modulus mi, there are (mi-1) valid x residues per modulus.")
    log("- After combining k moduli, M = product(m1..mk) and candidates ≈ M * sqrt(n)/M = sqrt(n)")
    log("  because range pruning keeps only x values in [2, sqrt(n)], a fraction sqrt(n)/M of all residues.")
    log("- This means candidate count is approximately **constant** at ~sqrt(n)/2 after range pruning!")
    log("- The method converges when M > sqrt(n), at which point each residue maps to exactly one x.")
    log("- Total CRT operations ≈ sum over steps of (candidates_k * mi), which is O(sqrt(n) * sum(mi)).")
    log("")
    log("**Fundamental limitation:**")
    log("- RNS eliminates carry propagation but the combinatorial explosion is replaced by")
    log("  ~sqrt(n) candidate residues after range pruning — equivalent to trial division!")
    log("- The carry-free multiplication in RNS doesn't help because the SEARCH SPACE")
    log("  (number of valid factor candidates) is inherently ~sqrt(n) regardless of representation.")
    log("- Each CRT combination step does O(candidates * mi) work, similar to trial division's O(sqrt(n)).")
    log("")

    successes = sum(1 for r in results if r["success"])
    log(f"**Total: {successes}/{len(results)} factored successfully**")
    log("")


if __name__ == "__main__":
    main()
