#!/usr/bin/env python3
"""
Round 11: Base-Hopping Sieve with ALL §6 Heuristics (Standalone Factoring Method)

The idea: Use multi-base modular constraints to determine x mod M for
progressively larger M, until M > sqrt(n) and x is fully determined.

Implementation:
  1. §6 Mod 8 lock-in: n mod 8 -> valid (x mod 8, y mod 8) pairs
  2. §6 Mod 16 lock-in: extend to mod 16, lock in 4 lowest bits
  3. §6 Mod 9 digital root: n mod 9 -> (x mod 9, y mod 9), CRT to mod 144
  4. §6 Mod 4 constraint: if n ≡ 3 mod 4, enforce parity split
  5. §4 Progressive base-hopping: primes 5,7,11,13,...
  6. Range pruning: at each step prune candidates outside [2, sqrt(n)]
  7. Track "state count curve" to measure complexity reduction

Key question: Does base-hopping + range pruning reduce enumeration below sqrt(n)?
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
# Primality and semiprime generation
# ============================================================
def is_prime_miller_rabin(n, k=25):
    if n < 2: return False
    if n == 2 or n == 3: return True
    if n % 2 == 0: return False
    r, d = 0, n - 1
    while d % 2 == 0: r += 1; d //= 2
    for _ in range(k):
        a = random.randrange(2, n - 1) if n > 4 else 2
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else:
            return False
    return True

def next_prime(n):
    if n <= 2: return 2
    if n % 2 == 0: n += 1
    while not is_prime_miller_rabin(n):
        n += 2
    return n

def gen_semiprime(bits):
    half = bits // 2
    p = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    q = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    while p == q:
        q = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    if p > q: p, q = q, p
    return p, q, p * q

# ============================================================
# CRT utilities
# ============================================================
def extended_gcd(a, b):
    old_r, r = a, b
    old_s, s = 1, 0
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
    return old_r, old_s, (old_r - old_s * a) // b if b else 0

def crt_two(r1, m1, r2, m2):
    """Combine x == r1 (mod m1) and x == r2 (mod m2). Returns (solution, lcm) or (None, None)."""
    g, p, _ = extended_gcd(m1, m2)
    if (r2 - r1) % g != 0:
        return None, None
    lcm = m1 * m2 // g
    sol = (r1 + m1 * ((r2 - r1) // g) * p) % lcm
    return sol, lcm

# ============================================================
# Base-Hopping Sieve
# ============================================================
def count_valid_x_in_range(x_mod, M, lo, hi):
    """Count integers x in [lo, hi] with x == x_mod (mod M)."""
    if lo > hi:
        return 0
    first = lo + (x_mod - lo % M) % M
    if first > hi:
        return 0
    return (hi - first) // M + 1

def basehop_factor(n, time_limit=120.0):
    """
    Base-Hopping Sieve: use multi-base modular constraints to narrow
    factor candidates via CRT, then enumerate survivors.
    Returns (factor, state_curve) or (None, state_curve).
    """
    t0 = time.time()
    isqrt_n = math.isqrt(n)

    # state_curve: list of (base_desc, modulus_M, num_crt_candidates, num_x_values)
    state_curve = []

    # Candidates: set of (x_res, y_res) tuples, all sharing same modulus M_cur
    # Using a set for automatic deduplication

    # ----------------------------------------------------------------
    # Step 1: §6 Mod 8 lock-in
    # ----------------------------------------------------------------
    M_cur = 8
    n_mod = n % M_cur
    candidates = set()
    for a in range(1, M_cur):
        for b in range(a, M_cur):
            if (a * b) % M_cur == n_mod:
                candidates.add((a, b))
                if a != b:
                    candidates.add((b, a))

    x_count = sum(count_valid_x_in_range(xr, M_cur, 2, isqrt_n) for xr, yr in candidates)
    state_curve.append(("mod8", M_cur, len(candidates), x_count))

    # ----------------------------------------------------------------
    # Step 2: §6 Mod 16 lock-in (extend mod 8 -> mod 16)
    # ----------------------------------------------------------------
    M_new = 16
    n16 = n % M_new
    new_cands = set()
    for (xr, yr) in candidates:
        for dx in range(2):
            x16 = xr + dx * 8
            for dy in range(2):
                y16 = yr + dy * 8
                if (x16 * y16) % M_new == n16:
                    new_cands.add((x16, y16))

    candidates = new_cands
    M_cur = M_new
    x_count = sum(count_valid_x_in_range(xr, M_cur, 2, isqrt_n) for xr, yr in candidates)
    state_curve.append(("mod16", M_cur, len(candidates), x_count))

    # ----------------------------------------------------------------
    # Step 3: §6 Mod 9 digital root + CRT to mod 144
    # ----------------------------------------------------------------
    n9 = n % 9
    pairs_9 = []
    for a in range(1, 9):
        for b in range(a, 9):
            if (a * b) % 9 == n9:
                pairs_9.append((a, b))
                if a != b:
                    pairs_9.append((b, a))

    new_cands = set()
    for (x16, y16) in candidates:
        for (x9, y9) in pairs_9:
            xc, xm = crt_two(x16, 16, x9, 9)
            if xc is None:
                continue
            yc, ym = crt_two(y16, 16, y9, 9)
            if yc is None:
                continue
            if (xc * yc) % xm == n % xm:
                new_cands.add((xc, yc))

    candidates = new_cands
    M_cur = 144  # lcm(16, 9)
    x_count = sum(count_valid_x_in_range(xr, M_cur, 2, isqrt_n) for xr, yr in candidates)
    state_curve.append(("mod144(16*9)", M_cur, len(candidates), x_count))

    # ----------------------------------------------------------------
    # Step 4: §6 Mod 4 constraint
    # ----------------------------------------------------------------
    if n % 4 == 3:
        filtered = set()
        for (xr, yr) in candidates:
            if (xr % 4 == 1 and yr % 4 == 3) or (xr % 4 == 3 and yr % 4 == 1):
                filtered.add((xr, yr))
        candidates = filtered
        x_count = sum(count_valid_x_in_range(xr, M_cur, 2, isqrt_n) for xr, yr in candidates)
        state_curve.append(("mod4_filter", M_cur, len(candidates), x_count))

    if time.time() - t0 > time_limit:
        return None, state_curve

    # ----------------------------------------------------------------
    # Step 5: §4 Progressive base-hopping with primes
    # ----------------------------------------------------------------
    primes = [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
              53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
              101, 103, 107, 109, 113, 127, 131, 137, 139, 149,
              151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199,
              211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269,
              271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337,
              347, 349, 353, 359, 367, 373, 379, 383, 389, 397,
              401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461,
              463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541]

    ENUM_THRESHOLD = 10_000_000   # switch to direct enumeration
    MAX_CRT_CANDIDATES = 200_000  # bail if CRT list exceeds this

    for p in primes:
        if time.time() - t0 > time_limit:
            break
        if not candidates:
            break

        # Precompute pairs mod p
        np_ = n % p
        pairs_p = []
        for a in range(1, p):
            for b in range(a, p):
                if (a * b) % p == np_:
                    pairs_p.append((a, b))
                    if a != b:
                        pairs_p.append((b, a))

        # Estimate new candidate count; skip if it would explode
        est_new = len(candidates) * len(pairs_p)
        # Each pair has ~1/p chance of surviving CRT product check,
        # but pessimistically check time
        if est_new > 50_000_000:
            # Too expensive to even iterate; log and skip
            state_curve.append((f"SKIP_p={p}", M_cur, len(candidates),
                                sum(count_valid_x_in_range(xr, M_cur, 2, isqrt_n) for xr, yr in candidates)))
            continue

        new_cands = set()
        M_new = M_cur * p  # since primes are coprime to M_cur

        tcheck = time.time()
        for (xr, yr) in candidates:
            if time.time() - t0 > time_limit:
                break
            for (xp, yp) in pairs_p:
                xc, xm = crt_two(xr, M_cur, xp, p)
                if xc is None:
                    continue
                yc, ym = crt_two(yr, M_cur, yp, p)
                if yc is None:
                    continue
                # Verify product constraint mod new modulus
                if (xc * yc) % xm == n % xm:
                    # Range pruning
                    if count_valid_x_in_range(xc, xm, 2, isqrt_n) > 0:
                        new_cands.add((xc, yc))

            # Periodic bail check
            if len(new_cands) > MAX_CRT_CANDIDATES and time.time() - tcheck > 5:
                break

        candidates = new_cands
        M_cur = M_new

        x_count = sum(count_valid_x_in_range(xr, M_cur, 2, isqrt_n) for xr, yr in candidates)
        state_curve.append((f"+p={p}", M_cur, len(candidates), x_count))

        # M > sqrt(n): each candidate gives at most 1 x; just test them
        if M_cur > isqrt_n:
            for (xr, yr) in candidates:
                if 2 <= xr <= isqrt_n and n % xr == 0:
                    return xr, state_curve
            return None, state_curve

        # Switch to direct enumeration when candidate x count is small enough
        if 0 < x_count <= ENUM_THRESHOLD:
            for (xr, yr) in candidates:
                if time.time() - t0 > time_limit:
                    return None, state_curve
                if xr < 2:
                    start_k = (2 - xr + M_cur - 1) // M_cur
                else:
                    start_k = 0
                x = xr + start_k * M_cur
                while x <= isqrt_n:
                    if time.time() - t0 > time_limit:
                        return None, state_curve
                    if n % x == 0:
                        return x, state_curve
                    x += M_cur
            return None, state_curve

        # If too many CRT candidates, stop adding bases
        if len(candidates) > MAX_CRT_CANDIDATES:
            state_curve.append(("BAIL_TOO_MANY", M_cur, len(candidates), x_count))
            break

    # ----------------------------------------------------------------
    # Final enumeration of remaining candidates
    # ----------------------------------------------------------------
    if candidates:
        x_count = sum(count_valid_x_in_range(xr, M_cur, 2, isqrt_n) for xr, yr in candidates)
        for (xr, yr) in candidates:
            if time.time() - t0 > time_limit:
                return None, state_curve
            if xr < 2:
                start_k = (2 - xr + M_cur - 1) // M_cur
            else:
                start_k = 0
            x = xr + start_k * M_cur
            while x <= isqrt_n:
                if time.time() - t0 > time_limit:
                    return None, state_curve
                if n % x == 0:
                    return x, state_curve
                x += M_cur

    return None, state_curve

# ============================================================
# Main test harness
# ============================================================
def main():
    random.seed(33333)

    log("")
    log("=" * 78)
    log("# Round 11: Base-Hopping Sieve with ALL Sec.6 Heuristics")
    log("=" * 78)
    log("")
    log("**Method**: Multi-base modular constraints -> CRT -> range pruning -> enumerate")
    log("")
    log("Stages: mod8 -> mod16 -> mod144(CRT 16,9) -> mod4 filter -> progressive primes")
    log("")

    bit_sizes = [30, 40, 50, 60, 64, 72, 80, 90, 96, 100, 112, 128]
    TIME_LIMIT = 120.0

    # Store results for detailed curves later
    results = []

    log("| Bits | n (hex) | p | q | Found | Time (s) | Final M | CRT Cands | x-Vals | x/sqrt(n) | Result |")
    log("|------|---------|---|---|-------|----------|---------|-----------|--------|-----------|--------|")

    for bits in bit_sizes:
        p_true, q_true, n = gen_semiprime(bits)
        isqrt_n = math.isqrt(n)

        t0 = time.time()
        factor_found, state_curve = basehop_factor(n, time_limit=TIME_LIMIT)
        elapsed = time.time() - t0

        if factor_found and n % factor_found == 0 and factor_found > 1:
            result = "FACTORED"
        else:
            factor_found = None
            result = "TIMEOUT" if elapsed >= TIME_LIMIT - 1 else "FAILED"

        if state_curve:
            last = state_curve[-1]
            final_m = last[1]
            final_crt = last[2]
            final_x = last[3]
            ratio = final_x / isqrt_n if isqrt_n > 0 else float('inf')
        else:
            final_m = 1; final_crt = 0; final_x = 0; ratio = 0

        n_hex = hex(n)[:18] + ("..." if len(hex(n)) > 18 else "")
        ff_str = str(factor_found) if factor_found else "-"

        log(f"| {bits:>4} | {n_hex} | {p_true} | {q_true} | {ff_str} | {elapsed:>8.3f} | {final_m} | {final_crt} | {final_x} | {ratio:.6e} | {result} |")

        results.append((bits, p_true, q_true, n, isqrt_n, state_curve, factor_found, elapsed, result))

    log("")
    log("### State Count Curves (detailed)")
    log("")

    # Show detailed curves for all tests from the same run (no re-run needed)
    for (bits, p_true, q_true, n, isqrt_n, state_curve, factor_found, elapsed, result) in results:
        log(f"#### {bits}-bit semiprime: n={n}, p={p_true}, q={q_true}, sqrt(n)={isqrt_n}")
        log(f"| Step | Modulus M | CRT Cands | x-Values | x/sqrt(n) |")
        log(f"|------|-----------|-----------|----------|-----------|")

        for (desc, M, crt_c, x_v) in state_curve:
            ratio = x_v / isqrt_n if isqrt_n > 0 else 0
            log(f"| {desc} | {M} | {crt_c} | {x_v} | {ratio:.6e} |")
        log("")

    # ----------------------------------------------------------------
    # Analysis
    # ----------------------------------------------------------------
    log("### Analysis: Does Base-Hopping Beat sqrt(n)?")
    log("")
    log("The key metric is x/sqrt(n) - the ratio of candidate x-values after")
    log("base-hopping to the naive trial division count of sqrt(n).")
    log("")
    log("- If ratio << 1: base-hopping provides genuine speedup over trial division")
    log("- If ratio ~ 1: base-hopping provides no net benefit (Conservation of Complexity)")
    log("")
    log("**Theoretical analysis**: For each prime p added, the number of valid")
    log("(a,b) pairs mod p with a*b = n mod p is exactly (p-1) (each a in 1..p-1")
    log("has a unique b = n*a^{-1} mod p). So adding prime p multiplies CRT")
    log("candidate count by (p-1) while multiplying M by p. The x-values per")
    log("candidate drop from sqrt(n)/M_old to sqrt(n)/M_new = sqrt(n)/(M_old*p).")
    log("Total x-values: (old_cands * (p-1)) * sqrt(n)/(M_old*p)")
    log("             = old_total_x * (p-1)/p")
    log("")
    log("So each prime p reduces total enumeration by factor (p-1)/p.")
    log("After k primes, total = sqrt(n) * prod((p_i-1)/p_i)")
    log("                     = sqrt(n) * prod(1 - 1/p_i)")
    log("                     ~ sqrt(n) / ln(P)  by Mertens' theorem")
    log("")
    log("This is the SIEVE OF ERATOSTHENES reduction -- logarithmic, not exponential.")
    log("The CRT candidate count grows as prod(p_i-1) ~ P/ln(P), consuming O(P)")
    log("memory, while x-values shrink as sqrt(n)/P * prod(p_i-1) ~ sqrt(n)/ln(P).")
    log("")
    log("**Conclusion**: Base-hopping is mathematically equivalent to trial division")
    log("with a wheel sieve. It reduces work by O(1/ln(P)) but cannot achieve")
    log("sub-sqrt(n) enumeration. This confirms Sec.5 Conservation of Complexity:")
    log("each base contributes O(log p) bits of information about the factors,")
    log("requiring O(sqrt(n)^{1-epsilon}) bases to fully determine them,")
    log("and the bookkeeping (CRT candidates) grows to absorb the savings.")
    log("")
    log("=" * 78)

if __name__ == "__main__":
    main()
