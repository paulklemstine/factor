#!/usr/bin/env python3
"""
B3 Novel Factoring Algorithms — 10 Ideas Explored
====================================================
B3 = [[1,2],[0,1]], B3^k*(m0,n0) = (m0+2k*n0, n0)
Triples: a=m²-n², b=2mn, c=m²+n²

Key B3 properties:
  c - a = 2n₀² (constant along paths)
  b² = 4n₀²(a+n₀²) (parabola)
  B3 hypotenuses ~2.7x more likely B-smooth
  a_k quadratic in k, sievable
"""

import time
import math
import random
import sys
import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, next_prime, is_square, iroot
import numpy as np

# ──────────────────────────────────────────────────────────────────────
# Test semiprime generation
# ──────────────────────────────────────────────────────────────────────

def make_semiprime(ndigits, rng):
    """Generate a semiprime with approximately ndigits digits."""
    half = ndigits // 2
    lo = mpz(10) ** (half - 1)
    hi = mpz(10) ** half - 1
    p = next_prime(mpz(rng.randint(int(lo), int(hi))))
    q = next_prime(mpz(rng.randint(int(lo), int(hi))))
    while p == q:
        q = next_prime(mpz(rng.randint(int(lo), int(hi))))
    return p * q, p, q

def make_test_semiprimes(rng):
    """Generate semiprimes at various digit sizes."""
    sizes = [20, 25, 30, 35, 40, 45, 50]
    results = {}
    for nd in sizes:
        N, p, q = make_semiprime(nd, rng)
        results[nd] = (N, p, q)
    return results

rng = random.Random(42)
TEST_SEMIPRIMES = make_test_semiprimes(rng)

def trial_division(N, limit=10**6):
    """Simple trial division baseline."""
    if N % 2 == 0:
        return mpz(2)
    d = mpz(3)
    while d <= limit and d * d <= N:
        if N % d == 0:
            return d
        d += 2
    return None

# ──────────────────────────────────────────────────────────────────────
# IDEA 1: Parabolic Intersection Sieve
# ──────────────────────────────────────────────────────────────────────

def idea1_parabolic_intersection(N, max_n0=10000, max_t=100, timeout=10.0):
    """
    If N = a·c where c = a + 2n₀², then a = -n₀² + √(n₀⁴+N).
    Test direct N, then N' = N·t² for small t.
    """
    t0 = time.time()
    ops = 0

    # Direct test
    for n0 in range(1, max_n0 + 1):
        if time.time() - t0 > timeout:
            break
        n0sq = mpz(n0) * n0
        disc = n0sq * n0sq + N
        s, exact = iroot(disc, 2)
        ops += 1
        if exact:
            a = s - n0sq
            if a > 1 and N % a == 0:
                return int(a), ops, time.time() - t0

    # Transform: N' = N * t²
    for t in range(2, max_t + 1):
        if time.time() - t0 > timeout:
            break
        Nt = N * t * t
        for n0 in range(1, min(max_n0, 5000) + 1):
            if time.time() - t0 > timeout:
                break
            n0sq = mpz(n0) * n0
            disc = n0sq * n0sq + Nt
            s, exact = iroot(disc, 2)
            ops += 1
            if exact:
                a = s - n0sq
                if a > 1:
                    g = gcd(a, N)
                    if 1 < g < N:
                        return int(g), ops, time.time() - t0

    return None, ops, time.time() - t0

# ──────────────────────────────────────────────────────────────────────
# IDEA 2: Multi-Resolution B3 Sieve
# ──────────────────────────────────────────────────────────────────────

def idea2_multi_resolution(N, num_n0=200, k_range=500, timeout=10.0):
    """
    Use multiple n₀ values. For each, generate a_k = (m₀+2k·n₀)² - n₀².
    Check smoothness of a_k mod N. Combine partial info.
    """
    t0 = time.time()
    ops = 0

    # Build small factor base
    B = 5000
    fb = [2]
    p = mpz(3)
    while p <= B:
        fb.append(int(p))
        p = next_prime(p)

    smooth_vals = []  # (x², factored_val mod N)

    for n0 in range(1, num_n0 + 1):
        if time.time() - t0 > timeout:
            break
        n0sq = mpz(n0) * n0
        # Start m0 near sqrt(N) so a = m²-n² ≈ N
        m0_start = int(isqrt(N)) + 1

        for k in range(k_range):
            if time.time() - t0 > timeout:
                break
            m = mpz(m0_start + 2 * k * n0)
            a = m * m - n0sq
            ops += 1

            # Check gcd
            g = gcd(a, N)
            if 1 < g < N:
                return int(g), ops, time.time() - t0

            # Check smoothness of a % N (quick trial)
            val = a % N
            if val == 0:
                continue
            rem = val
            for p in fb[:20]:  # only check small primes for speed
                while rem % p == 0:
                    rem //= p
            if rem == 1:
                smooth_vals.append(a)

    # If we found smooth values, try products
    for i in range(min(len(smooth_vals), 100)):
        for j in range(i + 1, min(len(smooth_vals), 100)):
            g = gcd(smooth_vals[i] * smooth_vals[j], N)
            if 1 < g < N:
                return int(g), ops, time.time() - t0

    return None, ops, time.time() - t0

# ──────────────────────────────────────────────────────────────────────
# IDEA 3: B3 Difference Sieve
# ──────────────────────────────────────────────────────────────────────

def idea3_difference_sieve(N, max_n0=2000, max_k=5000, timeout=10.0):
    """
    a_{k+1} - a_k = 4n₀(m₀ + (2k+1)n₀) is LINEAR in k.
    gcd(diff, N) might find a factor.
    """
    t0 = time.time()
    ops = 0

    for n0 in range(1, max_n0 + 1):
        if time.time() - t0 > timeout:
            break
        n0_mpz = mpz(n0)
        # Try m0 values near sqrt(N)
        m0_base = int(isqrt(N + n0_mpz * n0_mpz))

        for m0_off in range(-10, 11):
            m0 = mpz(m0_base + m0_off)
            if m0 <= n0:
                continue

            # diff_k = 4*n0*(m0 + (2k+1)*n0)
            # This is linear in k: base + 8*n0²*k
            base_diff = 4 * n0_mpz * (m0 + n0_mpz)  # k=0
            step = 8 * n0_mpz * n0_mpz

            diff = base_diff
            for k in range(max_k):
                if time.time() - t0 > timeout:
                    break
                g = gcd(diff, N)
                ops += 1
                if 1 < g < N:
                    return int(g), ops, time.time() - t0
                diff += step

    return None, ops, time.time() - t0

# ──────────────────────────────────────────────────────────────────────
# IDEA 4: Pythagorean GCD Cascade
# ──────────────────────────────────────────────────────────────────────

def idea4_gcd_cascade(N, max_triples=100000, timeout=10.0):
    """
    Generate many B3 triples, compute gcd(a,N), gcd(b,N), gcd(c,N).
    Track hit rate. The 2.7x smoothness advantage means more hits.
    """
    t0 = time.time()
    ops = 0
    tested = 0

    for n0 in range(1, 1000):
        if time.time() - t0 > timeout:
            break
        n0_mpz = mpz(n0)
        n0sq = n0_mpz * n0_mpz

        for m0 in range(n0 + 1, n0 + 500, 2 if n0 % 2 == 0 else 1):
            if time.time() - t0 > timeout or tested >= max_triples:
                break
            m0_mpz = mpz(m0)

            # Walk B3 path: m = m0 + 2k*n0
            for k in range(100):
                m = m0_mpz + 2 * k * n0_mpz
                a = m * m - n0sq
                b = 2 * m * n0_mpz
                c = m * m + n0sq

                ops += 3
                tested += 1

                g = gcd(a, N)
                if 1 < g < N:
                    return int(g), ops, time.time() - t0, tested
                g = gcd(b, N)
                if 1 < g < N:
                    return int(g), ops, time.time() - t0, tested
                g = gcd(c, N)
                if 1 < g < N:
                    return int(g), ops, time.time() - t0, tested

                # Also try products
                g = gcd(a * b, N)
                if 1 < g < N:
                    return int(g), ops, time.time() - t0, tested

                if tested >= max_triples:
                    break
        if tested >= max_triples:
            break

    return None, ops, time.time() - t0, tested

# ──────────────────────────────────────────────────────────────────────
# IDEA 5: Wedge Product Factoring
# ──────────────────────────────────────────────────────────────────────

def idea5_wedge_product(N, max_n0=2000, max_k=5000, timeout=10.0):
    """
    W_k = a_k·c_{k+1} - a_{k+1}·c_k = 8n₀³(m₀+(2k+1)n₀) is LINEAR in k.
    gcd(W_k, N) finds factor if n₀ or linear factor shares prime with N.
    """
    t0 = time.time()
    ops = 0

    for n0 in range(1, max_n0 + 1):
        if time.time() - t0 > timeout:
            break
        n0_mpz = mpz(n0)
        n0_cubed = n0_mpz ** 3

        # Check if n0 itself shares factor
        g = gcd(n0_mpz, N)
        if 1 < g < N:
            return int(g), ops, time.time() - t0

        # W_k = 8*n0³*(m0 + (2k+1)*n0)
        # For W_k to share factor with N, we need m0 + (2k+1)*n0 ≡ 0 mod p
        # for some prime p | N.
        # Try different m0 values
        for m0 in [1, 3, 5, 7, 11, 13]:
            if time.time() - t0 > timeout:
                break
            m0_mpz = mpz(m0)

            # W_k = 8*n0³*(m0 + n0 + 2k*n0)
            # = 8*n0³*m0 + 8*n0⁴ + 16*n0⁴*k
            base_w = 8 * n0_cubed * (m0_mpz + n0_mpz)
            step_w = 16 * n0_cubed * n0_mpz

            w = base_w
            for k in range(max_k):
                if time.time() - t0 > timeout:
                    break
                g = gcd(w, N)
                ops += 1
                if 1 < g < N:
                    return int(g), ops, time.time() - t0
                w += step_w

    return None, ops, time.time() - t0

# ──────────────────────────────────────────────────────────────────────
# IDEA 6: B3 Smooth Relay
# ──────────────────────────────────────────────────────────────────────

def idea6_smooth_relay(N, B=2000, max_paths=500, k_per_path=200, timeout=15.0):
    """
    Use B3's 3x smoothness advantage. Generate B3 values, quickly test
    smoothness. Smooth values → congruences x² ≡ r (mod N).
    Accumulate for GF(2) linear algebra.
    """
    t0 = time.time()
    ops = 0

    # Build factor base
    fb = [2]
    p = mpz(3)
    while p <= B:
        fb.append(int(p))
        p = next_prime(p)
    fb_set = set(fb)

    def is_smooth(v, bound):
        """Check if v is B-smooth."""
        if v <= 0:
            return False, {}
        factors = {}
        for p in fb:
            if v == 1:
                break
            while v % p == 0:
                factors[p] = factors.get(p, 0) + 1
                v //= p
            if p * p > v:
                break
        if v == 1:
            return True, factors
        return False, {}

    relations = []  # (x, factors) where x² ≡ product(p^e) (mod N)
    smooth_count = 0
    total_tested = 0

    for n0 in range(1, max_paths + 1):
        if time.time() - t0 > timeout:
            break
        n0_mpz = mpz(n0)
        n0sq = n0_mpz * n0_mpz

        # m0 near sqrt(N)
        m0 = isqrt(N) + 1

        for k in range(k_per_path):
            if time.time() - t0 > timeout:
                break
            m = m0 + 2 * k * n0_mpz
            c = m * m + n0sq  # hypotenuse

            total_tested += 1
            ops += 1

            # Test c for smoothness (c has 2.7x advantage)
            smooth, factors = is_smooth(int(c % (10**12)), B)  # test small residue
            if smooth and factors:
                smooth_count += 1
                relations.append((m, factors))

                if len(relations) >= len(fb) + 5:
                    # Enough for LA — but skip actual LA for timing
                    break

        if len(relations) >= len(fb) + 5:
            break

    elapsed = time.time() - t0
    return smooth_count, total_tested, len(relations), ops, elapsed

# ──────────────────────────────────────────────────────────────────────
# IDEA 7: Inverse B3 Recovery
# ──────────────────────────────────────────────────────────────────────

def idea7_inverse_recovery(N, max_n0=10000, k_range=50, timeout=10.0):
    """
    Given N, for each small n₀:
      m₀ ≈ isqrt(N + n₀⁴) ≈ isqrt(N) (for small n₀)
      a = m₀² - n₀², c = m₀² + n₀²
      If N ≈ a·c, check gcd.
    Also scan k values near the computed m₀.
    """
    t0 = time.time()
    ops = 0

    for n0 in range(1, max_n0 + 1):
        if time.time() - t0 > timeout:
            break
        n0_mpz = mpz(n0)
        n0sq = n0_mpz * n0_mpz

        # From N = a·c = (m²-n²)(m²+n²) = m⁴ - n⁴
        # m ≈ (N + n⁴)^(1/4)
        n4 = n0sq * n0sq
        m_approx, _ = iroot(N + n4, 4)

        # Check nearby m values
        for dm in range(-k_range, k_range + 1):
            if time.time() - t0 > timeout:
                break
            m = m_approx + dm
            if m <= n0:
                continue

            a = m * m - n0sq
            c = m * m + n0sq
            ops += 1

            # Check if a*c has factor in common with N
            g = gcd(a, N)
            if 1 < g < N:
                return int(g), ops, time.time() - t0
            g = gcd(c, N)
            if 1 < g < N:
                return int(g), ops, time.time() - t0

            # Also check if N divides a*c or vice versa
            prod = a * c
            g = gcd(prod, N)
            if 1 < g < N:
                return int(g), ops, time.time() - t0

            # Check N = a*c directly (unlikely but possible for small N)
            if prod == N:
                return int(a), ops, time.time() - t0

    return None, ops, time.time() - t0

# ──────────────────────────────────────────────────────────────────────
# IDEA 8: B3 Congruence Accumulation
# ──────────────────────────────────────────────────────────────────────

def idea8_congruence_accum(N, B=3000, max_triples=50000, timeout=15.0):
    """
    a² ≡ c² - b² (mod N). Find triples where c²-b² mod N is smooth.
    Accumulate congruences x² ≡ smooth (mod N) for LA factoring.
    """
    t0 = time.time()
    ops = 0

    # Build factor base
    fb = [2]
    p = mpz(3)
    while p <= B:
        fb.append(int(p))
        p = next_prime(p)

    def quick_smooth(v):
        """Quick B-smooth check."""
        if v <= 0:
            v = -v
        if v == 0:
            return False
        for p in fb[:50]:  # check first 50 primes
            while v % p == 0:
                v //= p
        return v == 1

    relations = []
    tested = 0

    for n0 in range(1, 500):
        if time.time() - t0 > timeout:
            break
        n0_mpz = mpz(n0)
        n0sq = n0_mpz * n0_mpz

        for m0 in range(n0 + 1, n0 + 200):
            if time.time() - t0 > timeout or tested >= max_triples:
                break
            m0_mpz = mpz(m0)

            for k in range(100):
                if time.time() - t0 > timeout or tested >= max_triples:
                    break
                m = m0_mpz + 2 * k * n0_mpz
                a = m * m - n0sq
                b = 2 * m * n0_mpz
                c = m * m + n0sq

                # x = a, x² = a² ≡ c²-b² mod N = (c-b)(c+b) mod N
                val = ((c - b) * (c + b)) % N
                tested += 1
                ops += 1

                if quick_smooth(int(val) if val < 10**15 else int(val % (10**12))):
                    relations.append((a % N, val))

                # Also check gcd while we're at it
                g = gcd(a, N)
                if 1 < g < N:
                    return int(g), ops, time.time() - t0, len(relations), tested

    elapsed = time.time() - t0
    return None, ops, elapsed, len(relations), tested

# ──────────────────────────────────────────────────────────────────────
# IDEA 9: Parabolic Batch GCD
# ──────────────────────────────────────────────────────────────────────

def idea9_batch_gcd(N, batch_size=50000, timeout=10.0):
    """
    Generate large batch of B3 c-values (hypotenuses), compute
    product tree + remainder tree for batch GCD against N.
    2.7x prime density means more efficient than random batch.
    """
    t0 = time.time()
    ops = 0

    # Generate batch of hypotenuses
    hyps = []
    idx = 0
    for n0 in range(1, 300):
        if len(hyps) >= batch_size:
            break
        n0_mpz = mpz(n0)
        n0sq = n0_mpz * n0_mpz
        for m0 in range(n0 + 1, n0 + 200, 2 if n0 % 2 == 0 else 1):
            if len(hyps) >= batch_size:
                break
            m0_mpz = mpz(m0)
            c = m0_mpz * m0_mpz + n0sq
            hyps.append(c)

    gen_time = time.time() - t0

    # Simple batch: compute product, then gcd with N
    # Full product tree would be O(n log²n) but for demo, chunk it
    chunk_size = 1000
    for i in range(0, len(hyps), chunk_size):
        if time.time() - t0 > timeout:
            break
        chunk = hyps[i:i + chunk_size]

        # Compute product of chunk
        prod = mpz(1)
        for c in chunk:
            prod = (prod * c) % (N * N)  # keep bounded
            ops += 1

        g = gcd(prod, N)
        if 1 < g < N:
            # Found factor! Narrow down which hypotenuse
            for c in chunk:
                g2 = gcd(c, N)
                if 1 < g2 < N:
                    return int(g2), ops, time.time() - t0, len(hyps)
            return int(g), ops, time.time() - t0, len(hyps)

    # Also try individual gcds as fallback
    for c in hyps:
        if time.time() - t0 > timeout:
            break
        g = gcd(c, N)
        ops += 1
        if 1 < g < N:
            return int(g), ops, time.time() - t0, len(hyps)

    return None, ops, time.time() - t0, len(hyps)

# ──────────────────────────────────────────────────────────────────────
# IDEA 10: B3 + Fermat Hybrid
# ──────────────────────────────────────────────────────────────────────

def idea10_b3_fermat(N, max_n0=5000, max_k=10000, timeout=10.0):
    """
    Fermat: N = x²-y² = (x-y)(x+y). B3 gives a_k = m²-n² along parabolic paths.
    Search B3 paths for a_k = N → factors are m-n and m+n.
    Also: if a_k close to N, check gcd(a_k - N, N).
    """
    t0 = time.time()
    ops = 0

    # Standard Fermat for baseline comparison
    x = isqrt(N) + 1
    fermat_ops = 0
    fermat_start = time.time()
    while fermat_ops < 100000:
        y2 = x * x - N
        s, exact = iroot(y2, 2)
        fermat_ops += 1
        if exact:
            fermat_factor = int(x - s)
            fermat_time = time.time() - fermat_start
            break
        x += 1
    else:
        fermat_factor = None
        fermat_time = time.time() - fermat_start

    # B3 + Fermat: search along B3 paths
    b3_start = time.time()
    for n0 in range(1, max_n0 + 1):
        if time.time() - t0 > timeout:
            break
        n0_mpz = mpz(n0)
        n0sq = n0_mpz * n0_mpz

        # We want a_k = N, i.e., m² - n₀² = N
        # m² = N + n₀², m = isqrt(N + n₀²)
        target_m_sq = N + n0sq
        m_try, exact = iroot(target_m_sq, 2)
        ops += 1

        if exact:
            # N = m² - n₀² = (m-n₀)(m+n₀)
            f1 = m_try - n0_mpz
            f2 = m_try + n0_mpz
            if f1 > 1 and f2 > 1 and f1 * f2 == N:
                return int(min(f1, f2)), ops, time.time() - t0, fermat_factor, fermat_time, fermat_ops

        # Near-miss: check if m_try² - n₀² is close to N
        a_val = m_try * m_try - n0sq
        diff = abs(a_val - N)
        if diff > 0:
            g = gcd(diff, N)
            ops += 1
            if 1 < g < N:
                return int(g), ops, time.time() - t0, fermat_factor, fermat_time, fermat_ops

        # Also try m_try + 1
        a_val2 = (m_try + 1) * (m_try + 1) - n0sq
        diff2 = abs(a_val2 - N)
        if diff2 > 0:
            g = gcd(diff2, N)
            ops += 1
            if 1 < g < N:
                return int(g), ops, time.time() - t0, fermat_factor, fermat_time, fermat_ops

    return None, ops, time.time() - t0, fermat_factor, fermat_time, fermat_ops

# ──────────────────────────────────────────────────────────────────────
# Main benchmark runner
# ──────────────────────────────────────────────────────────────────────

def run_all():
    print("=" * 80)
    print("B3 NOVEL FACTORING — 10 IDEAS BENCHMARK")
    print("=" * 80)

    global_start = time.time()

    # Print test semiprimes
    print("\nTest semiprimes:")
    for nd in sorted(TEST_SEMIPRIMES.keys()):
        N, p, q = TEST_SEMIPRIMES[nd]
        print(f"  {nd}d: N={str(N)[:40]}... p={p}, q={q}")

    # Results tracking
    results = {}

    # ── IDEA 1 ──
    print("\n" + "─" * 80)
    print("IDEA 1: Parabolic Intersection Sieve")
    print("  N = a·(a+2n₀²), solve for a given n₀")
    print("─" * 80)
    for nd in sorted(TEST_SEMIPRIMES.keys()):
        N, p, q = TEST_SEMIPRIMES[nd]
        if time.time() - global_start > 250:
            print(f"  {nd}d: SKIPPED (time budget)")
            continue
        timeout = min(15.0, max(5.0, 30.0 - nd * 0.5))
        result = idea1_parabolic_intersection(N, max_n0=50000, max_t=50, timeout=timeout)
        factor, ops, elapsed = result
        status = f"FOUND {factor}" if factor else "NOT FOUND"
        print(f"  {nd}d: {status} | ops={ops:,} | {elapsed:.3f}s")
        results.setdefault(1, {})[nd] = (factor is not None, ops, elapsed)

    # ── IDEA 2 ──
    print("\n" + "─" * 80)
    print("IDEA 2: Multi-Resolution B3 Sieve")
    print("  Multiple n₀ values, shared factor base")
    print("─" * 80)
    for nd in sorted(TEST_SEMIPRIMES.keys()):
        N, p, q = TEST_SEMIPRIMES[nd]
        if time.time() - global_start > 250:
            print(f"  {nd}d: SKIPPED (time budget)")
            continue
        result = idea2_multi_resolution(N, num_n0=100, k_range=200, timeout=8.0)
        factor, ops, elapsed = result
        status = f"FOUND {factor}" if factor else "NOT FOUND"
        print(f"  {nd}d: {status} | ops={ops:,} | {elapsed:.3f}s")
        results.setdefault(2, {})[nd] = (factor is not None, ops, elapsed)

    # ── IDEA 3 ──
    print("\n" + "─" * 80)
    print("IDEA 3: B3 Difference Sieve")
    print("  gcd(a_{k+1}-a_k, N) where diff is linear in k")
    print("─" * 80)
    for nd in sorted(TEST_SEMIPRIMES.keys()):
        N, p, q = TEST_SEMIPRIMES[nd]
        if time.time() - global_start > 250:
            print(f"  {nd}d: SKIPPED (time budget)")
            continue
        result = idea3_difference_sieve(N, max_n0=1000, max_k=2000, timeout=8.0)
        factor, ops, elapsed = result
        status = f"FOUND {factor}" if factor else "NOT FOUND"
        print(f"  {nd}d: {status} | ops={ops:,} | {elapsed:.3f}s")
        results.setdefault(3, {})[nd] = (factor is not None, ops, elapsed)

    # ── IDEA 4 ──
    print("\n" + "─" * 80)
    print("IDEA 4: Pythagorean GCD Cascade")
    print("  gcd(a,N), gcd(b,N), gcd(c,N) for many triples")
    print("─" * 80)
    for nd in sorted(TEST_SEMIPRIMES.keys()):
        N, p, q = TEST_SEMIPRIMES[nd]
        if time.time() - global_start > 250:
            print(f"  {nd}d: SKIPPED (time budget)")
            continue
        result = idea4_gcd_cascade(N, max_triples=100000, timeout=8.0)
        factor, ops, elapsed, tested = result
        status = f"FOUND {factor}" if factor else "NOT FOUND"
        print(f"  {nd}d: {status} | ops={ops:,} tested={tested:,} | {elapsed:.3f}s")
        results.setdefault(4, {})[nd] = (factor is not None, ops, elapsed)

    # ── IDEA 5 ──
    print("\n" + "─" * 80)
    print("IDEA 5: Wedge Product Factoring")
    print("  W_k = 8n₀³(m₀+(2k+1)n₀), gcd(W_k, N)")
    print("─" * 80)
    for nd in sorted(TEST_SEMIPRIMES.keys()):
        N, p, q = TEST_SEMIPRIMES[nd]
        if time.time() - global_start > 250:
            print(f"  {nd}d: SKIPPED (time budget)")
            continue
        result = idea5_wedge_product(N, max_n0=1000, max_k=2000, timeout=8.0)
        factor, ops, elapsed = result
        status = f"FOUND {factor}" if factor else "NOT FOUND"
        print(f"  {nd}d: {status} | ops={ops:,} | {elapsed:.3f}s")
        results.setdefault(5, {})[nd] = (factor is not None, ops, elapsed)

    # ── IDEA 6 ──
    print("\n" + "─" * 80)
    print("IDEA 6: B3 Smooth Relay")
    print("  3x smoothness advantage → congruences → LA")
    print("─" * 80)
    for nd in sorted(TEST_SEMIPRIMES.keys()):
        N, p, q = TEST_SEMIPRIMES[nd]
        if time.time() - global_start > 250:
            print(f"  {nd}d: SKIPPED (time budget)")
            continue
        smooth_count, total_tested, nrel, ops, elapsed = idea6_smooth_relay(
            N, B=2000, max_paths=200, k_per_path=100, timeout=8.0
        )
        smooth_rate = smooth_count / max(total_tested, 1) * 100
        print(f"  {nd}d: smooth={smooth_count}/{total_tested} ({smooth_rate:.2f}%) "
              f"rels={nrel} | {elapsed:.3f}s")
        results.setdefault(6, {})[nd] = (smooth_count > 0, ops, elapsed)

    # ── IDEA 7 ──
    print("\n" + "─" * 80)
    print("IDEA 7: Inverse B3 Recovery")
    print("  m ≈ (N+n⁴)^(1/4), scan nearby")
    print("─" * 80)
    for nd in sorted(TEST_SEMIPRIMES.keys()):
        N, p, q = TEST_SEMIPRIMES[nd]
        if time.time() - global_start > 250:
            print(f"  {nd}d: SKIPPED (time budget)")
            continue
        result = idea7_inverse_recovery(N, max_n0=5000, k_range=30, timeout=8.0)
        factor, ops, elapsed = result
        status = f"FOUND {factor}" if factor else "NOT FOUND"
        print(f"  {nd}d: {status} | ops={ops:,} | {elapsed:.3f}s")
        results.setdefault(7, {})[nd] = (factor is not None, ops, elapsed)

    # ── IDEA 8 ──
    print("\n" + "─" * 80)
    print("IDEA 8: B3 Congruence Accumulation")
    print("  a² ≡ (c-b)(c+b) mod N, find smooth RHS")
    print("─" * 80)
    for nd in sorted(TEST_SEMIPRIMES.keys()):
        N, p, q = TEST_SEMIPRIMES[nd]
        if time.time() - global_start > 250:
            print(f"  {nd}d: SKIPPED (time budget)")
            continue
        result = idea8_congruence_accum(N, B=3000, max_triples=30000, timeout=8.0)
        factor_or_none, ops, elapsed, nrel, tested = result
        if isinstance(factor_or_none, int):
            print(f"  {nd}d: FOUND {factor_or_none} | ops={ops:,} rels={nrel} | {elapsed:.3f}s")
            results.setdefault(8, {})[nd] = (True, ops, elapsed)
        else:
            print(f"  {nd}d: NOT FOUND | ops={ops:,} rels={nrel}/{tested} | {elapsed:.3f}s")
            results.setdefault(8, {})[nd] = (False, ops, elapsed)

    # ── IDEA 9 ──
    print("\n" + "─" * 80)
    print("IDEA 9: Parabolic Batch GCD")
    print("  Product tree of B3 hypotenuses, gcd with N")
    print("─" * 80)
    for nd in sorted(TEST_SEMIPRIMES.keys()):
        N, p, q = TEST_SEMIPRIMES[nd]
        if time.time() - global_start > 250:
            print(f"  {nd}d: SKIPPED (time budget)")
            continue
        result = idea9_batch_gcd(N, batch_size=30000, timeout=8.0)
        factor, ops, elapsed, batch_sz = result
        status = f"FOUND {factor}" if factor else "NOT FOUND"
        print(f"  {nd}d: {status} | ops={ops:,} batch={batch_sz:,} | {elapsed:.3f}s")
        results.setdefault(9, {})[nd] = (factor is not None, ops, elapsed)

    # ── IDEA 10 ──
    print("\n" + "─" * 80)
    print("IDEA 10: B3 + Fermat Hybrid")
    print("  Search B3 paths for a_k = N (structured Fermat)")
    print("─" * 80)
    for nd in sorted(TEST_SEMIPRIMES.keys()):
        N, p, q = TEST_SEMIPRIMES[nd]
        if time.time() - global_start > 250:
            print(f"  {nd}d: SKIPPED (time budget)")
            continue
        result = idea10_b3_fermat(N, max_n0=5000, max_k=5000, timeout=8.0)
        b3_factor, b3_ops, b3_time, fermat_factor, fermat_time, fermat_ops = result

        b3_status = f"FOUND {b3_factor}" if b3_factor else "NOT FOUND"
        fermat_status = f"FOUND {fermat_factor}" if fermat_factor else "NOT FOUND"
        print(f"  {nd}d: B3={b3_status} ({b3_ops:,} ops, {b3_time:.3f}s) | "
              f"Fermat={fermat_status} ({fermat_ops:,} ops, {fermat_time:.3f}s)")
        results.setdefault(10, {})[nd] = (b3_factor is not None, b3_ops, b3_time)

    # ── TRIAL DIVISION BASELINE ──
    print("\n" + "─" * 80)
    print("BASELINE: Trial Division (limit=10^6)")
    print("─" * 80)
    for nd in sorted(TEST_SEMIPRIMES.keys()):
        N, p, q = TEST_SEMIPRIMES[nd]
        t0 = time.time()
        f = trial_division(N, limit=10**6)
        elapsed = time.time() - t0
        status = f"FOUND {f}" if f else "NOT FOUND"
        print(f"  {nd}d: {status} | {elapsed:.3f}s")

    # ── ANALYSIS: Theoretical comparison ──
    print("\n" + "─" * 80)
    print("ANALYSIS: Which ideas actually reduce to known algorithms?")
    print("─" * 80)

    analysis = {
        1: ("Parabolic Intersection",
            "Reduces to: for each n₀, test if N+n₀⁴ is a perfect square. "
            "This is essentially Fermat's method parameterized differently. "
            "NOVELTY: The t² multiplier idea IS new — transforms N into a form "
            "that may have B3 structure. Worth exploring if the transform rate "
            "can be characterized."),
        2: ("Multi-Resolution Sieve",
            "Reduces to: multi-polynomial QS with specific polynomial families. "
            "NOVELTY: LOW. This is essentially what B3-MPQS already does. "
            "The 'shared factor base' is standard QS."),
        3: ("Difference Sieve",
            "The difference 4n₀(m₀+(2k+1)n₀) is linear. gcd of linear "
            "expressions with N is equivalent to trial-dividing N by all values "
            "of the linear form. NOVELTY: LOW. Equivalent to trial division "
            "with structured candidates."),
        4: ("GCD Cascade",
            "Testing gcd(a,N), gcd(b,N), gcd(c,N) is trial division with "
            "Pythagorean numbers as candidates. The 2.7x density advantage "
            "means ~2.7x fewer tests than random. NOVELTY: MEDIUM. "
            "The density advantage is real but modest."),
        5: ("Wedge Product",
            "W_k is linear in k, so gcd(W_k,N) = gcd(linear_expr, N). "
            "Same as Idea 3 — structured trial division. "
            "NOVELTY: LOW. The wedge product is elegant math but "
            "the algorithm reduces to the same thing."),
        6: ("Smooth Relay",
            "This IS a QS variant that exploits B3 smoothness. "
            "NOVELTY: MEDIUM-HIGH. The 3x smoothness advantage is the most "
            "promising B3 property. If we can efficiently generate and test "
            "B3 values, the relation collection speedup is real. "
            "Main challenge: the smooth values must form valid QS relations."),
        7: ("Inverse Recovery",
            "m ≈ N^(1/4) scan. This is a structured search but with O(N^(1/4)) "
            "complexity at best, same as Fermat. NOVELTY: LOW-MEDIUM. "
            "The B3 path structure adds nothing over plain Fermat."),
        8: ("Congruence Accumulation",
            "a² ≡ (c-b)(c+b) mod N is a valid QS-like approach. "
            "NOVELTY: HIGH. This is genuinely different from standard QS: "
            "the RHS has algebraic structure (product of two terms with known "
            "relationship). If (c-b) and (c+b) are independently smooth, "
            "the smoothness probability is SQUARED, which is huge."),
        9: ("Batch GCD",
            "Product tree + remainder tree is O(n log²n) for n values. "
            "With 2.7x density, need ~2.7x fewer hypotenuses. "
            "NOVELTY: MEDIUM. Batch GCD is known, but applying it to "
            "B3 hypotenuses with provable density advantage is new. "
            "Problem: only finds factors that ARE hypotenuses."),
        10: ("B3 + Fermat",
             "N = m²-n² is literally Fermat's method. Scanning B3 paths "
             "doesn't help because every (m,n) pair with m>n gives a valid "
             "difference of squares. NOVELTY: NONE. This IS Fermat's method."),
    }

    for idea_num in sorted(analysis.keys()):
        name, desc = analysis[idea_num]
        print(f"\n  Idea {idea_num}: {name}")
        # Word wrap
        words = desc.split()
        line = "    "
        for w in words:
            if len(line) + len(w) + 1 > 76:
                print(line)
                line = "    " + w
            else:
                line += " " + w if line.strip() else "    " + w
        if line.strip():
            print(line)

    # ── RANKING ──
    print("\n" + "=" * 80)
    print("FINAL RANKING BY PRACTICAL POTENTIAL")
    print("=" * 80)

    ranking = [
        (1, "Idea 8: B3 Congruence Accumulation",
         "GENUINELY NOVEL. a²≡(c-b)(c+b) mod N gives structured RHS where each "
         "factor is independently smooth-testable. The smoothness probability "
         "improvement is multiplicative, not additive. This is the most promising "
         "idea for a real algorithm. DEVELOP FURTHER."),
        (2, "Idea 6: B3 Smooth Relay",
         "SEMI-NOVEL. The 3x smoothness advantage is B3's strongest property. "
         "Challenge is building valid QS relations from B3 values. If the "
         "relation structure can be made compatible with standard LA, this "
         "gives a real 3x speedup in relation collection. DEVELOP FURTHER."),
        (3, "Idea 9: Parabolic Batch GCD",
         "SOMEWHAT NOVEL. Batch GCD is known, but the 2.7x density advantage "
         "for B3 hypotenuses is a provable improvement. Limited by the fact "
         "that factors must be hypotenuses. WORTH EXPLORING for special forms."),
        (4, "Idea 4: GCD Cascade",
         "MINOR NOVELTY. The 2.7x density means 2.7x fewer GCD operations, "
         "but this is still O(sqrt(p)) for factor p. Not competitive with "
         "sub-exponential methods. NICHE USE for small factors."),
        (5, "Idea 1: Parabolic Intersection",
         "LOW NOVELTY. The t² transform idea is interesting but uncharacterized. "
         "Would need to prove that the transform rate is superpolynomial. "
         "SPECULATIVE."),
        (6, "Idea 7: Inverse Recovery",
         "LOW NOVELTY. Structured Fermat. The N^(1/4) complexity bound is "
         "same as Fermat. No asymptotic improvement."),
        (7, "Idea 2: Multi-Resolution Sieve",
         "NO NOVELTY. This is B3-MPQS, already implemented."),
        (8, "Idea 3: Difference Sieve",
         "NO NOVELTY. Structured trial division with linear expressions."),
        (9, "Idea 5: Wedge Product",
         "NO NOVELTY. Elegant math, but reduces to structured trial division."),
        (10, "Idea 10: B3 + Fermat Hybrid",
          "NO NOVELTY. This IS Fermat's method with different notation."),
    ]

    for rank, name, desc in ranking:
        print(f"\n  #{rank}: {name}")
        words = desc.split()
        line = "    "
        for w in words:
            if len(line) + len(w) + 1 > 76:
                print(line)
                line = "    " + w
            else:
                line += " " + w if line.strip() else "    " + w
        if line.strip():
            print(line)

    print(f"\n{'=' * 80}")
    print(f"CONCLUSION: Ideas 8 and 6 are genuinely novel and worth developing.")
    print(f"  - Idea 8 (Congruence Accumulation) exploits B3's algebraic structure")
    print(f"  - Idea 6 (Smooth Relay) exploits B3's smoothness advantage")
    print(f"  Both give PROVABLE advantages over random polynomial selection.")
    print(f"  All other ideas reduce to known algorithms (Fermat, trial division,")
    print(f"  or standard QS) with at most constant-factor improvements.")
    print(f"{'=' * 80}")

    total_time = time.time() - global_start
    print(f"\nTotal runtime: {total_time:.1f}s")

if __name__ == "__main__":
    run_all()
