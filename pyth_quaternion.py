#!/usr/bin/env python3
"""
Quaternion Extensions of Pythagorean Tree for Integer Factoring
==============================================================

8 experiments exploring whether quaternion algebra (sum-of-4-squares,
Hurwitz integers, Brahmagupta-Fibonacci identity) can help factor N=p*q.

Each experiment tests on semiprimes at 20b, 32b, 48b, 64b.
Memory limit: 2GB. Time limit: 120s per experiment.
"""

import math
import random
import time
import sys
from math import gcd, isqrt, log2
from collections import defaultdict
from itertools import product as iprod

# ============================================================
# UTILITIES
# ============================================================

def miller_rabin(n, witnesses=(2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)):
    if n < 2: return False
    if n in (2, 3): return True
    if n % 2 == 0: return False
    r, d = 0, n - 1
    while d % 2 == 0: r += 1; d //= 2
    for a in witnesses:
        if a >= n: continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1: break
        else:
            return False
    return True

def gen_semi(bits, seed=42):
    rng = random.Random(seed)
    while True:
        p = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if miller_rabin(p): break
    while True:
        q = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if q != p and miller_rabin(q): break
    return min(p, q), max(p, q), p * q

def is_perfect_square(n):
    if n < 0: return False, 0
    if n == 0: return True, 0
    r = isqrt(n)
    if r * r == n: return True, r
    return False, 0

def tonelli_shanks(n, p):
    """Compute sqrt(n) mod p. Returns None if no square root."""
    if pow(n, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        r = pow(n, (p + 1) // 4, p)
        return r
    # Factor out powers of 2 from p-1
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    # Find a non-residue
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while True:
        if t == 1:
            return r
        i = 1
        tmp = t * t % p
        while tmp != 1:
            tmp = tmp * tmp % p
            i += 1
        b = c
        for _ in range(m - i - 1):
            b = b * b % p
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p

def sqrt_mod_n(a, n):
    """Find x such that x^2 ≡ a (mod n), or None. Works for prime n."""
    return tonelli_shanks(a % n, n)

# ============================================================
# SEMIPRIME TEST CASES
# ============================================================

BIT_SIZES = [20, 32, 48, 64]

def get_test_cases():
    """Generate test semiprimes at various bit sizes."""
    cases = []
    for b in BIT_SIZES:
        half = b // 2
        p, q, N = gen_semi(half, seed=b * 137 + 7)
        cases.append((b, p, q, N))
    return cases

# ============================================================
# EXPERIMENT 1: Four-Square Representations via Tree
# ============================================================

def four_square_decompose(n, max_outer=200):
    """Find a,b,c,d >= 0 with a^2+b^2+c^2+d^2 = n.
    Uses a greedy algorithm: subtract largest square, recurse.
    Bounded search to avoid hanging on large n."""
    if n == 0:
        return (0, 0, 0, 0)
    r = isqrt(n)
    a_start = r
    a_end = max(r - max_outer, 0)
    for a in range(a_start, a_end, -1):
        rem1 = n - a * a
        if rem1 < 0: continue
        r2 = isqrt(rem1)
        b_end = max(r2 - max_outer, -1)
        for b in range(min(r2, a), b_end, -1):
            rem2 = rem1 - b * b
            if rem2 < 0: continue
            r3 = isqrt(rem2)
            c_end = max(r3 - max_outer, -1)
            for c in range(min(r3, b), c_end, -1):
                rem3 = rem2 - c * c
                if rem3 < 0: continue
                ok, d = is_perfect_square(rem3)
                if ok and d <= c:
                    return (a, b, c, d)
    # Fallback: try random
    rng = random.Random(n % (2**31))
    for _ in range(500):
        a = rng.randint(0, r)
        rem1 = n - a*a
        if rem1 < 0: continue
        b = rng.randint(0, isqrt(rem1))
        rem2 = rem1 - b*b
        if rem2 < 0: continue
        c = rng.randint(0, isqrt(rem2))
        rem3 = rem2 - c*c
        if rem3 < 0: continue
        ok, d = is_perfect_square(rem3)
        if ok:
            return tuple(sorted([a, b, c, d], reverse=True))
    return None

# Berggren-like 4D transformations that preserve sum-of-4-squares structure
# If q = (a,b,c,d) and N(q) = a^2+b^2+c^2+d^2, quaternion multiplication
# by unit quaternions preserves the norm.
# The 24 Hurwitz units are: ±1, ±i, ±j, ±k, (±1±i±j±k)/2
# We use left-multiplication by various elements.

def quat_mult(q1, q2):
    """Multiply two quaternions (a,b,c,d) representing a+bi+cj+dk."""
    a1, b1, c1, d1 = q1
    a2, b2, c2, d2 = q2
    return (
        a1*a2 - b1*b2 - c1*c2 - d1*d2,
        a1*b2 + b1*a2 + c1*d2 - d1*c2,
        a1*c2 - b1*d2 + c1*a2 + d1*b2,
        a1*d2 + b1*c2 - c1*b2 + d1*a2,
    )

def quat_norm(q):
    return q[0]*q[0] + q[1]*q[1] + q[2]*q[2] + q[3]*q[3]

def quat_conj(q):
    return (q[0], -q[1], -q[2], -q[3])

def experiment1(cases, max_time=25):
    """Four-Square Tree: start from decompositions, apply quaternion
    transformations, check if any derived value shares a factor with N."""
    print("\n" + "="*70)
    print("EXPERIMENT 1: Four-Square Representations via Quaternion Tree")
    print("="*70)
    print("Idea: Decompose N as a^2+b^2+c^2+d^2, apply quaternion")
    print("multiplications to generate new 4-tuples, check gcd with N.")

    # Some small quaternions to multiply by (non-unit, to change norm)
    multipliers = [
        (1, 1, 0, 0), (1, 0, 1, 0), (1, 0, 0, 1),
        (2, 1, 0, 0), (1, 1, 1, 0), (1, 1, 1, 1),
        (2, 1, 1, 0), (3, 1, 0, 0), (2, 2, 1, 0),
    ]

    results = []
    for bits, p, q, N in cases:
        t0 = time.time()
        found = None
        # Get initial 4-square decomposition of N
        decomp = four_square_decompose(N)
        if decomp is None:
            print(f"  {bits}b: Could not decompose N={N}")
            results.append((bits, False, 0, 0))
            continue

        a, b, c, d = decomp
        # Also try decompositions of small multiples of N
        queue = [decomp]
        for k in range(2, 20):
            dk = four_square_decompose(k * N)
            if dk is not None:
                queue.append(dk)

        checked = 0
        visited = set()
        while queue and time.time() - t0 < max_time / len(cases):
            cur = queue.pop(0)
            key = tuple(sorted([abs(x) for x in cur]))
            if key in visited:
                continue
            visited.add(key)

            # Check all components for gcd with N
            for v in cur:
                if v != 0:
                    g = gcd(abs(v), N)
                    if 1 < g < N:
                        found = g
                        break
            if found:
                break

            # Also check pairwise sums/differences
            vals = list(cur)
            for i in range(4):
                for j in range(i+1, 4):
                    for v in [vals[i]+vals[j], abs(vals[i]-vals[j]),
                              vals[i]*vals[j]]:
                        if v > 0:
                            g = gcd(v, N)
                            if 1 < g < N:
                                found = g
                                break
                    if found: break
                if found: break
            if found: break

            checked += 1
            # Generate children by quaternion multiplication
            for m in multipliers[:5]:
                child = quat_mult(cur, m)
                queue.append(child)
                # Also try conjugate multiplication
                child2 = quat_mult(m, cur)
                queue.append(child2)

            if checked > 5000:
                break

        elapsed = time.time() - t0
        if found:
            print(f"  {bits}b: FACTORED N={N} = {found} * {N//found} "
                  f"in {elapsed:.3f}s ({checked} nodes)")
        else:
            print(f"  {bits}b: No factor found ({checked} nodes, {elapsed:.3f}s)")
        results.append((bits, found is not None, checked, elapsed))

    success = sum(1 for _, ok, _, _ in results if ok)
    print(f"\n  Result: {success}/{len(results)} factored")
    if success == 0:
        print("  Verdict: REJECTED — quaternion tree walk does not efficiently")
        print("  produce values sharing factors with N.")
    elif success <= 2:
        print("  Verdict: PROMISING for small N, but scaling unclear.")
    else:
        print("  Verdict: CONFIRMED — works at multiple scales!")
    return results


# ============================================================
# EXPERIMENT 2: Quaternion GCD for Factoring
# ============================================================

def hurwitz_gcd(a, b, max_iter=200):
    """Euclidean algorithm in Hurwitz integers (approximately).
    We use the nearest-integer division. Bounded iterations to avoid hangs."""
    iters = 0
    while quat_norm(b) > 0 and iters < max_iter:
        # Compute a * conj(b) / norm(b)
        bc = quat_conj(b)
        prod = quat_mult(a, bc)
        nb = quat_norm(b)
        if nb == 0:
            break
        # Round to nearest integer quaternion
        quot = tuple(round(x / nb) for x in prod)
        # remainder = a - quot * b
        qb = quat_mult(quot, b)
        rem = tuple(a[i] - qb[i] for i in range(4))
        old_norm = quat_norm(b)
        new_norm = quat_norm(rem)
        if new_norm >= old_norm:
            break  # Not making progress
        a, b = b, rem
        iters += 1
    return a

def experiment2(cases, max_time=25):
    """Quaternion GCD: Compute Hurwitz GCD of quaternions with norm N."""
    print("\n" + "="*70)
    print("EXPERIMENT 2: Quaternion GCD for Factoring")
    print("="*70)
    print("Idea: Find quaternions q1,q2 with norms related to N,")
    print("compute Hurwitz GCD — norm of GCD might be a factor of N.")

    results = []
    for bits, p, q_factor, N in cases:
        t0 = time.time()
        found = None
        attempts = 0

        # Strategy: create quaternions whose norms are multiples of N
        # Then their GCD in Hurwitz integers might reveal factors
        decomp = four_square_decompose(N)
        if decomp is None:
            print(f"  {bits}b: Could not decompose N")
            results.append((bits, False, 0, 0))
            continue

        rng = random.Random(bits * 31)
        max_attempts = 500
        while attempts < max_attempts and time.time() - t0 < max_time / len(cases):
            # Generate random quaternion with norm = k*N for small k
            k = rng.randint(1, 10)
            dk = four_square_decompose(k * N)
            if dk is None:
                attempts += 1
                continue

            # Also try another decomposition
            k2 = rng.randint(1, 10)
            dk2 = four_square_decompose(k2 * N)
            if dk2 is None:
                attempts += 1
                continue

            # Compute Hurwitz GCD
            g = hurwitz_gcd(dk, dk2)
            ng = quat_norm(g)
            if ng > 1:
                gv = gcd(ng, N)
                if 1 < gv < N:
                    found = gv
                    break
                # Also check components
                for v in g:
                    if v != 0:
                        gv = gcd(abs(v), N)
                        if 1 < gv < N:
                            found = gv
                            break
                if found: break
            attempts += 1

        elapsed = time.time() - t0
        if found:
            print(f"  {bits}b: FACTORED N={N} = {found} * {N//found} "
                  f"in {elapsed:.3f}s ({attempts} attempts)")
        else:
            print(f"  {bits}b: No factor found ({attempts} attempts, {elapsed:.3f}s)")
        results.append((bits, found is not None, attempts, elapsed))

    success = sum(1 for _, ok, _, _ in results if ok)
    print(f"\n  Result: {success}/{len(results)} factored")
    if success == 0:
        print("  Verdict: REJECTED — Hurwitz GCD does not reveal factors")
        print("  without already knowing a factor-norm quaternion.")
    elif success <= 2:
        print("  Verdict: PROMISING but needs refinement.")
    else:
        print("  Verdict: CONFIRMED!")
    return results


# ============================================================
# EXPERIMENT 3: Quaternion Walks mod N
# ============================================================

def experiment3(cases, max_time=25):
    """Random quaternion multiplication walks mod N, tracking norms."""
    print("\n" + "="*70)
    print("EXPERIMENT 3: Quaternion Walks mod N")
    print("="*70)
    print("Idea: Random walk via quaternion multiplication mod N.")
    print("Track norm = a^2+b^2+c^2+d^2 mod N. Check gcd(norm, N).")
    print("Norm is multiplicative => this is multiplicative walk on Z/NZ.")

    # Fixed step quaternions
    steps = [
        (2, 1, 0, 0), (1, 2, 0, 0), (1, 0, 2, 0), (1, 0, 0, 2),
        (1, 1, 1, 0), (1, 1, 0, 1), (1, 0, 1, 1), (2, 1, 1, 0),
        (3, 2, 1, 0), (5, 3, 1, 1),
    ]
    step_norms = [quat_norm(s) for s in steps]

    results = []
    for bits, p, q_factor, N in cases:
        t0 = time.time()
        found = None
        rng = random.Random(bits * 53)

        # Start from a random quaternion mod N
        state = tuple(rng.randint(0, min(N-1, 10**9)) % N for _ in range(4))
        norm_acc = sum(x*x for x in state) % N

        max_steps = min(200000, int(2 * N**0.25))  # Birthday bound ~ N^(1/4)
        norms_seen = {}
        checked = 0

        while checked < max_steps and time.time() - t0 < max_time / len(cases):
            # Pick a random step
            idx = rng.randint(0, len(steps) - 1)
            step = steps[idx]

            # Quaternion multiply mod N
            a1, b1, c1, d1 = state
            a2, b2, c2, d2 = step
            state = (
                (a1*a2 - b1*b2 - c1*c2 - d1*d2) % N,
                (a1*b2 + b1*a2 + c1*d2 - d1*c2) % N,
                (a1*c2 - b1*d2 + c1*a2 + d1*b2) % N,
                (a1*d2 + b1*c2 - c1*b2 + d1*a2) % N,
            )

            norm = (state[0]*state[0] + state[1]*state[1] +
                    state[2]*state[2] + state[3]*state[3]) % N

            # Check gcd of norm with N
            g = gcd(norm, N)
            if 1 < g < N:
                found = g
                break

            # Check individual components
            for v in state:
                if v > 0:
                    g = gcd(v, N)
                    if 1 < g < N:
                        found = g
                        break
            if found: break

            # Birthday: check if we've seen this norm before
            if norm in norms_seen:
                diff = abs(checked - norms_seen[norm])
                g = gcd(diff, N)
                if 1 < g < N:
                    found = g
                    break
            norms_seen[norm] = checked

            checked += 1
            # Memory guard
            if len(norms_seen) > 500000:
                norms_seen.clear()

        elapsed = time.time() - t0
        if found:
            print(f"  {bits}b: FACTORED N={N} = {found} * {N//found} "
                  f"in {elapsed:.3f}s ({checked} steps)")
        else:
            print(f"  {bits}b: No factor found ({checked} steps, {elapsed:.3f}s)")
        results.append((bits, found is not None, checked, elapsed))

    success = sum(1 for _, ok, _, _ in results if ok)
    print(f"\n  Result: {success}/{len(results)} factored")
    if success == 0:
        print("  Verdict: REJECTED — quaternion walk mod N is essentially")
        print("  a multiplicative random walk; no better than Pollard rho.")
    elif success <= 2:
        print("  Verdict: PROMISING for small N.")
    else:
        print("  Verdict: CONFIRMED!")
    return results


# ============================================================
# EXPERIMENT 4: Sum-of-Two-Squares Certificate
# ============================================================

def cornacchia(n):
    """Find (x, y) with x^2 + y^2 = n, or None.
    Works when n is prime ≡ 1 (mod 4)."""
    if n == 2:
        return (1, 1)
    if n % 4 == 3:
        return None
    # Find sqrt(-1) mod n
    r = tonelli_shanks(n - 1, n)
    if r is None:
        return None
    # Euclidean algorithm
    a, b = n, r
    limit = isqrt(n)
    while b > limit:
        a, b = b, a % b
    # Check if n - b^2 is a perfect square
    rem = n - b * b
    ok, c = is_perfect_square(rem)
    if ok:
        return (b, c)
    return None

def experiment4(cases, max_time=25):
    """Sum-of-two-squares certificate: represent N as sum of two squares
    in multiple ways and extract factors from the differences."""
    print("\n" + "="*70)
    print("EXPERIMENT 4: Sum-of-Two-Squares Certificate")
    print("="*70)
    print("Idea: If N = a^2+b^2 = c^2+d^2 (two representations),")
    print("then gcd(a±c, N) might reveal a factor. [Fermat's method variant]")

    results = []
    for bits, p, q_factor, N in cases:
        t0 = time.time()
        found = None

        # N = p*q. For N to be sum of 2 squares, need p ≡ 1 (mod 4) AND q ≡ 1 (mod 4)
        # (or one of them is 2). Check:
        if p % 4 == 3 and q_factor % 4 == 3:
            print(f"  {bits}b: N={N}, p≡3, q≡3 mod 4 => N not sum of 2 squares. SKIP.")
            results.append((bits, False, 0, 0))
            continue

        # Find representations by brute force (for small N) or Cornacchia-like
        reps = []
        limit = isqrt(N)
        # Brute force: try a from sqrt(N) downward
        search_limit = min(limit, 100000)
        for a in range(limit, max(limit - search_limit, 0), -1):
            rem = N - a * a
            if rem < 0:
                continue
            ok, b = is_perfect_square(rem)
            if ok and b <= a:
                reps.append((a, b))
                if len(reps) >= 2:
                    break
            if time.time() - t0 > max_time / len(cases):
                break

        if len(reps) >= 2:
            a1, b1 = reps[0]
            a2, b2 = reps[1]
            # Try various gcds
            for x in [a1 - a2, a1 + a2, b1 - b2, b1 + b2,
                       a1*b2 - a2*b1, a1*b2 + a2*b1,
                       a1*a2 - b1*b2, a1*a2 + b1*b2]:
                if x != 0:
                    g = gcd(abs(x), N)
                    if 1 < g < N:
                        found = g
                        break

        elapsed = time.time() - t0
        if found:
            print(f"  {bits}b: FACTORED N={N} = {found} * {N//found} "
                  f"in {elapsed:.3f}s, reps={reps[:2]}")
        else:
            nreps = len(reps)
            print(f"  {bits}b: Found {nreps} representations, no factor ({elapsed:.3f}s)")
        results.append((bits, found is not None, len(reps), elapsed))

    success = sum(1 for _, ok, _, _ in results if ok)
    print(f"\n  Result: {success}/{len(results)} factored")
    if success >= 3:
        print("  Verdict: CONFIRMED — two-representation method works!")
    elif success > 0:
        print("  Verdict: PROMISING — works for small N where brute-force")
        print("  can find two representations. Needs efficient rep-finding for large N.")
    else:
        print("  Verdict: REJECTED — cannot find two representations efficiently.")
    return results


# ============================================================
# EXPERIMENT 5: Brahmagupta-Fibonacci Identity for Factoring
# ============================================================

def experiment5(cases, max_time=25):
    """Brahmagupta-Fibonacci: If N = a^2+b^2 and we know sqrt(-1) mod N,
    we can find two representations and factor via gcd."""
    print("\n" + "="*70)
    print("EXPERIMENT 5: Brahmagupta-Fibonacci Identity for Factoring")
    print("="*70)
    print("Idea: Find sqrt(-1) mod N (via CRT of sqrt(-1) mod p, mod q).")
    print("Then Cornacchia on (N, r) where r = sqrt(-1) mod N gives a rep.")
    print("Different r values give different reps => gcd factors N.")
    print("CATCH: Finding sqrt(-1) mod N requires factoring N... unless")
    print("we can find it by other means (e.g., random search).")

    results = []
    for bits, p, q_factor, N in cases:
        t0 = time.time()
        found = None

        # Check if -1 is a QR mod p and mod q
        if p % 4 == 3 or q_factor % 4 == 3:
            print(f"  {bits}b: p or q ≡ 3 mod 4, sqrt(-1) mod N doesn't exist. SKIP.")
            results.append((bits, False, 0, 0))
            continue

        # We "cheat" to find sqrt(-1) mod N using CRT (to validate the method)
        # In practice, finding sqrt(-1) mod N without factoring is the hard part.
        r_p = tonelli_shanks(p - 1, p)
        r_q = tonelli_shanks(q_factor - 1, q_factor)
        if r_p is None or r_q is None:
            print(f"  {bits}b: Could not find sqrt(-1). SKIP.")
            results.append((bits, False, 0, 0))
            continue

        # CRT gives 4 roots: (±r_p, ±r_q)
        # p_inv mod q and q_inv mod p
        p_inv = pow(p, -1, q_factor)
        q_inv = pow(q_factor, -1, p)

        roots = []
        for sp in [r_p, p - r_p]:
            for sq in [r_q, q_factor - r_q]:
                r = (sp * q_factor * q_inv + sq * p * p_inv) % N
                roots.append(r)

        # For each root, run Cornacchia-like algorithm
        reps = []
        for r in roots:
            # Euclidean algorithm on (N, r)
            a, b = N, r % N
            limit = isqrt(N)
            while b > limit:
                a, b = b, a % b
            rem = N - b * b
            ok, c = is_perfect_square(rem)
            if ok:
                reps.append((b, c))

        # Try gcd between different representations
        if len(reps) >= 2:
            for i in range(len(reps)):
                for j in range(i + 1, len(reps)):
                    a1, b1 = reps[i]
                    a2, b2 = reps[j]
                    for x in [a1 - a2, a1 + a2, b1 - b2, b1 + b2,
                               a1*b2 - a2*b1, a1*b2 + a2*b1]:
                        if x != 0:
                            g = gcd(abs(x), N)
                            if 1 < g < N:
                                found = g
                                break
                    if found: break
                if found: break

        elapsed = time.time() - t0
        if found:
            print(f"  {bits}b: FACTORED N={N} = {found} * {N//found} "
                  f"in {elapsed:.3f}s ({len(reps)} reps from {len(roots)} roots)")
        else:
            print(f"  {bits}b: {len(reps)} reps from {len(roots)} roots, "
                  f"no factor ({elapsed:.3f}s)")
        results.append((bits, found is not None, len(reps), elapsed))

    success = sum(1 for _, ok, _, _ in results if ok)
    print(f"\n  Result: {success}/{len(results)} factored")
    print("  NOTE: This 'cheats' by using CRT (requires knowing p,q).")
    print("  The REAL question: can we find sqrt(-1) mod N without factoring?")
    if success >= 2:
        print("  Verdict: CONFIRMED (math works) — but finding sqrt(-1) mod N")
        print("  is equivalent to factoring, so this is CIRCULAR.")
    else:
        print("  Verdict: REJECTED even with cheating.")
    return results


# ============================================================
# EXPERIMENT 6: Quaternion Tree Walk with Norm Tracking
# ============================================================

def experiment6(cases, max_time=25):
    """Quaternion tree walk: multiplicative norm tracking = Pollard rho?"""
    print("\n" + "="*70)
    print("EXPERIMENT 6: Quaternion Norm Walk = Pollard Rho?")
    print("="*70)
    print("Idea: N(q1*q2) = N(q1)*N(q2). So quaternion multiplication")
    print("gives multiplicative walk on norms. Compare to Pollard rho.")

    results = []
    for bits, p, q_factor, N in cases:
        t0 = time.time()
        found = None

        # Pollard rho on the norm
        # f(x) = x^2 + c mod N (classic rho)
        rng = random.Random(bits * 97)
        c = rng.randint(1, N - 1)
        x = rng.randint(2, N - 1)
        y = x
        steps = 0
        max_steps = min(500000, int(3 * N**0.25))

        # Brent's improvement
        r, q_acc, m = 1, 1, 1
        ys = x
        while steps < max_steps and time.time() - t0 < max_time / len(cases):
            y_old = y
            for _ in range(r):
                y = (y * y + c) % N
            k = 0
            while k < r and not found:
                ys = y
                for _ in range(min(m, r - k)):
                    y = (y * y + c) % N
                    q_acc = q_acc * abs(x - y) % N
                    steps += 1
                g = gcd(q_acc, N)
                if 1 < g < N:
                    found = g
                    break
                if g == N:
                    # Backtrack
                    while True:
                        ys = (ys * ys + c) % N
                        g = gcd(abs(x - ys), N)
                        if g > 1:
                            if g < N:
                                found = g
                            break
                    break
                k += m
            x = y_old
            x = (x * x + c) % N  # advance x
            r *= 2

        elapsed = time.time() - t0

        # Now do the same but with quaternion norm walk
        t1 = time.time()
        found_q = None
        state = (rng.randint(1, 100), rng.randint(1, 100),
                 rng.randint(1, 100), rng.randint(1, 100))
        step_q = (2, 1, 1, 0)  # norm = 6
        norm = quat_norm(state) % N
        # Floyd cycle detection on the norm
        slow_norm = norm
        fast_state = state
        fast_norm = norm
        steps_q = 0
        max_steps_q = min(500000, int(3 * N**0.25))
        while steps_q < max_steps_q and time.time() - t1 < max_time / len(cases):
            # Advance slow by 1
            state = tuple(x % N for x in quat_mult(state, step_q))
            slow_norm = sum(x*x for x in state) % N

            # Advance fast by 2
            fast_state = tuple(x % N for x in quat_mult(fast_state, step_q))
            fast_state = tuple(x % N for x in quat_mult(fast_state, step_q))
            fast_norm = sum(x*x for x in fast_state) % N

            g = gcd(abs(slow_norm - fast_norm), N) if slow_norm != fast_norm else 0
            if 1 < g < N:
                found_q = g
                break
            steps_q += 1

        elapsed_q = time.time() - t1

        rho_str = f"Rho: {'YES' if found else 'NO'} in {elapsed:.3f}s/{steps} steps"
        quat_str = f"QNorm: {'YES' if found_q else 'NO'} in {elapsed_q:.3f}s/{steps_q} steps"
        print(f"  {bits}b: {rho_str} | {quat_str}")

        results.append((bits, found is not None, found_q is not None, elapsed, elapsed_q))

    rho_wins = sum(1 for r in results if r[1])
    quat_wins = sum(1 for r in results if r[2])
    print(f"\n  Rho: {rho_wins}/{len(results)} | Quat Norm: {quat_wins}/{len(results)}")
    print("  Verdict: Quaternion norm walk is just multiplicative iteration.")
    print("  It reduces to Pollard rho with extra overhead. REJECTED as novel method.")
    return results


# ============================================================
# EXPERIMENT 7: Cornacchia's Algorithm on N (not p)
# ============================================================

def experiment7(cases, max_time=25):
    """Run Cornacchia on composite N: Euclidean algorithm with random
    starting values, looking for x^2 + y^2 = N representations."""
    print("\n" + "="*70)
    print("EXPERIMENT 7: Cornacchia's Algorithm on Composite N")
    print("="*70)
    print("Idea: Run Euclidean algo on (N, r) for random r.")
    print("When remainder drops below sqrt(N), check if N-r^2 is a square.")
    print("If N = p*q with p,q ≡ 1 mod 4, this can find representations.")

    results = []
    for bits, p, q_factor, N in cases:
        t0 = time.time()
        found = None
        reps = []
        rng = random.Random(bits * 71)
        attempts = 0
        max_attempts = min(50000, N)

        limit = isqrt(N)
        while attempts < max_attempts and time.time() - t0 < max_time / len(cases):
            # Pick random r
            r = rng.randint(1, N - 1)
            # Euclidean algorithm
            a, b = N, r
            while b > limit:
                a, b = b, a % b
            # Check if N - b^2 is a perfect square
            rem = N - b * b
            if rem >= 0:
                ok, c = is_perfect_square(rem)
                if ok:
                    rep = (max(b, c), min(b, c))
                    if rep not in reps:
                        reps.append(rep)
                        # Check if we can factor from two reps
                        if len(reps) >= 2:
                            for i in range(len(reps)):
                                for j in range(i+1, len(reps)):
                                    a1, b1 = reps[i]
                                    a2, b2 = reps[j]
                                    for x in [a1-a2, a1+a2, b1-b2, b1+b2,
                                              a1*b2-a2*b1, a1*b2+a2*b1]:
                                        if x != 0:
                                            g = gcd(abs(x), N)
                                            if 1 < g < N:
                                                found = g
                                                break
                                    if found: break
                                if found: break
                            if found: break
            attempts += 1

        elapsed = time.time() - t0
        if found:
            print(f"  {bits}b: FACTORED N={N} = {found} * {N//found} "
                  f"in {elapsed:.3f}s ({len(reps)} reps, {attempts} attempts)")
        else:
            print(f"  {bits}b: Found {len(reps)} reps, no factor "
                  f"({attempts} attempts, {elapsed:.3f}s)")
        results.append((bits, found is not None, len(reps), elapsed))

    success = sum(1 for _, ok, _, _ in results if ok)
    print(f"\n  Result: {success}/{len(results)} factored")
    if success >= 2:
        print("  Verdict: CONFIRMED — random Cornacchia on composite N")
        print("  can find multiple representations and factor via gcd!")
        print("  Efficiency: ~O(N^(1/2)) random trials to find 2 reps.")
    elif success > 0:
        print("  Verdict: PROMISING for small N. Finding reps is O(sqrt(N)) expected.")
    else:
        print("  Verdict: REJECTED — cannot find representations efficiently.")
    return results


# ============================================================
# EXPERIMENT 8: Jacobi's Four-Square Theorem
# ============================================================

def sigma_odd(n):
    """Sum of divisors of n that are not divisible by 4."""
    # Remove factors of 4: sigma_odd(n) = sum_{d|n, 4 nmid d} d
    s = 0
    for d in range(1, isqrt(n) + 1):
        if n % d == 0:
            if d % 4 != 0:
                s += d
            other = n // d
            if other != d and other % 4 != 0:
                s += other
    return s

def count_four_square_reps_brute(n):
    """Count r_4(n) = number of ordered representations (a,b,c,d) in Z^4
    with a^2+b^2+c^2+d^2 = n (a,b,c,d can be negative or zero).
    Brute force; only feasible for small n."""
    count = 0
    r = isqrt(n)
    for a in range(-r, r + 1):
        a2 = a * a
        rem1 = n - a2
        if rem1 < 0: continue
        r2 = isqrt(rem1)
        for b in range(-r2, r2 + 1):
            rem2 = rem1 - b * b
            if rem2 < 0: continue
            r3 = isqrt(rem2)
            for c in range(-r3, r3 + 1):
                rem3 = rem2 - c * c
                if rem3 < 0: continue
                ok, d = is_perfect_square(rem3)
                if ok:
                    # d and -d both count (unless d=0)
                    count += 1 if d == 0 else 2
    return count

def experiment8(cases, max_time=25):
    """Jacobi's theorem: r_4(N) = 8*sigma(N) where sigma = sum of odd divisors.
    If we could count r_4(N), we'd get sigma(N) = 1+p+q+N => p+q => factor!"""
    print("\n" + "="*70)
    print("EXPERIMENT 8: Jacobi's Four-Square Theorem")
    print("="*70)
    print("Idea: r_4(N) = 8*sigma_odd(N). For N=p*q (both odd primes),")
    print("sigma_odd(N) = (1+p)(1+q) = 1+p+q+N.")
    print("So if we COUNT four-square reps, we get p+q, and can solve")
    print("the quadratic x^2 - (p+q)x + N = 0 to get p and q.")
    print("QUESTION: Can we count r_4(N) without factoring?")

    results = []

    # First verify the formula on a tiny semiprime
    print("\n  Verifying Jacobi formula on small semiprimes first...")
    for tp, tq in [(3, 5), (7, 11), (13, 17), (5, 13)]:
        tn = tp * tq
        r4_brute = count_four_square_reps_brute(tn)
        so = sigma_odd(tn)
        r4_formula = 8 * so
        match = "OK" if r4_brute == r4_formula else "FAIL"
        print(f"    N={tn}={tp}*{tq}: r4_brute={r4_brute}, 8*sigma_odd={r4_formula} [{match}]")
        if r4_brute == r4_formula:
            # Extract factors
            s_val = so - 1 - tn  # = p + q
            disc = s_val * s_val - 4 * tn
            ok, dv = is_perfect_square(disc)
            if ok and dv > 0:
                pf = (s_val + dv) // 2
                qf = (s_val - dv) // 2
                if pf * qf == tn:
                    print(f"      => sigma_odd={so}, p+q={s_val}, factors: {qf}*{pf}")

    print()
    # Now test on our actual cases
    for bits, p, q_factor, N in cases:
        t0 = time.time()
        found = None

        # Theoretical sigma_odd
        so_theory = sigma_odd(N) if N < 10**8 else None
        # For N=p*q (both odd primes), sigma_odd(N) = 1 + p + q + N
        so_from_factors = 1 + p + q_factor + N
        r4_theory = 8 * so_from_factors

        if N < 5000:
            r4_counted = count_four_square_reps_brute(N)
            match = r4_counted == r4_theory
            print(f"  {bits}b: r_4(N={N}) = {r4_counted}, theory = {r4_theory} "
                  f"[{'MATCH' if match else 'MISMATCH'}]")
            if match:
                sigma = r4_counted // 8
                s = sigma - 1 - N
                disc = s * s - 4 * N
                ok, d = is_perfect_square(disc)
                if ok:
                    p_found = (s + d) // 2
                    q_found = (s - d) // 2
                    if p_found * q_found == N:
                        found = min(p_found, q_found)
                        print(f"         => p+q={s}, factors: {q_found}*{p_found}")
        else:
            print(f"  {bits}b: N={N} ({bits} bits). Brute-force r_4 is O(N^{{3/2}}).")
            print(f"         sigma_odd(N) = {so_from_factors} (requires knowing p,q).")
            print(f"         Computing sigma_odd without factoring IS factoring.")

        elapsed = time.time() - t0
        if found:
            print(f"         FACTORED in {elapsed:.3f}s!")
        results.append((bits, found is not None, 0, elapsed))

    success = sum(1 for _, ok, _, _ in results if ok)
    print(f"\n  Result: {success}/{len(results)} factored")
    print("  Verdict: CONFIRMED mathematically — Jacobi's theorem gives")
    print("  an exact formula. BUT counting r_4(N) is O(N^{3/2}),")
    print("  which is WORSE than trial division O(N^{1/2}).")
    print("  This is a CIRCULAR method: counting is harder than factoring.")
    return results


# ============================================================
# MAIN
# ============================================================

def main():
    print("="*70)
    print("QUATERNION EXTENSIONS OF PYTHAGOREAN TREE FOR FACTORING")
    print("="*70)
    print(f"Testing on semiprimes at {BIT_SIZES} bits")

    cases = get_test_cases()
    print("\nTest semiprimes:")
    for bits, p, q, N in cases:
        print(f"  {bits}b: N = {N} = {p} * {q}")

    all_results = {}

    t_total = time.time()

    all_results['exp1'] = experiment1(cases)
    all_results['exp2'] = experiment2(cases)
    all_results['exp3'] = experiment3(cases)
    all_results['exp4'] = experiment4(cases)
    all_results['exp5'] = experiment5(cases)
    all_results['exp6'] = experiment6(cases)
    all_results['exp7'] = experiment7(cases)
    all_results['exp8'] = experiment8(cases)

    total_time = time.time() - t_total

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    verdicts = {
        'exp1': ("Four-Square Tree Walk", "Tests quaternion tree navigation"),
        'exp2': ("Quaternion GCD", "Hurwitz integer Euclidean algorithm"),
        'exp3': ("Quaternion Walks mod N", "Random quaternion multiplication"),
        'exp4': ("Sum-of-Two-Squares", "Multiple representations => gcd"),
        'exp5': ("Brahmagupta-Fibonacci", "CRT sqrt(-1) => representations"),
        'exp6': ("Norm Walk = Rho?", "Quaternion norm is multiplicative"),
        'exp7': ("Cornacchia on N", "Random Euclidean on composite"),
        'exp8': ("Jacobi Four-Square", "Count reps => sigma => factors"),
    }

    for key in sorted(verdicts.keys()):
        name, desc = verdicts[key]
        res = all_results[key]
        if key == 'exp6':
            # exp6 has (bits, rho_ok, quat_ok, ...) — evaluate quaternion method (r[2])
            successes = sum(1 for r in res if r[2])
            rho_successes = sum(1 for r in res if r[1])
            total = len(res)
            status = "REJECTED"
            extra = f" (Pollard rho: {rho_successes}/{total})"
        else:
            successes = sum(1 for r in res if r[1])
            total = len(res)
            status = "CONFIRMED" if successes >= 3 else ("PROMISING" if successes > 0 else "REJECTED")
            extra = ""
        print(f"  {key}: {name:30s} {successes}/{total} factored  [{status}]{extra}")
        print(f"         {desc}")

    print(f"\nTotal time: {total_time:.1f}s")
    print("\nKey insights:")
    print("  1. Quaternion norm is multiplicative => norm walks reduce to")
    print("     multiplicative iteration on Z/NZ, i.e., Pollard rho.")
    print("  2. Sum-of-two-squares (Exp 4,5,7): TWO representations of N")
    print("     as a^2+b^2 immediately factor N via gcd. The hard part is")
    print("     finding representations, which requires sqrt(-1) mod N.")
    print("  3. Jacobi's theorem (Exp 8): Counting r_4(N) gives sigma(N)")
    print("     which factors N, but counting is harder than factoring.")
    print("  4. The fundamental barrier: quaternion/Gaussian structure")
    print("     encodes factorization, but ACCESSING it requires")
    print("     information equivalent to knowing the factors.")


if __name__ == "__main__":
    main()
