#!/usr/bin/env python3
"""
Pythagorean Tree Factoring — Cross-Math Experiments Batch 3
Fields 11-15: Dynamical Systems, Information Theory, Algebraic Geometry,
              Optimization, Representation Theory.

Each experiment: multiple roots, 20b-48b semiprimes, <60s per experiment.
Memory budget: <2GB total.
"""

import math
import random
import time
import sys
from math import gcd, log, log2, isqrt, sqrt, pi, e
from collections import defaultdict, Counter
import numpy as np

# ============================================================
# INFRASTRUCTURE
# ============================================================

B1 = np.array([[2, -1], [1, 0]], dtype=object)
B2 = np.array([[2, 1], [1, 0]], dtype=object)
B3 = np.array([[1, 2], [0, 1]], dtype=object)
BERGGREN = {'B1': B1, 'B2': B2, 'B3': B3}

ROOTS = [(2,1), (3,2), (4,3), (5,2), (5,4), (7,4), (8,3)]
BIT_SIZES = [20, 24, 28, 32, 36, 40, 44, 48]

def apply_mat(M, m, n):
    """Apply 2x2 matrix to (m,n)."""
    return int(M[0,0]*m + M[0,1]*n), int(M[1,0]*m + M[1,1]*n)

def mat_mul(A, B):
    """2x2 integer matrix multiply."""
    return np.array([
        [A[0,0]*B[0,0]+A[0,1]*B[1,0], A[0,0]*B[0,1]+A[0,1]*B[1,1]],
        [A[1,0]*B[0,0]+A[1,1]*B[1,0], A[1,0]*B[0,1]+A[1,1]*B[1,1]]
    ], dtype=object)

def mat_pow_mod(M, k, mod):
    """Matrix power M^k mod N using repeated squaring."""
    result = np.array([[1,0],[0,1]], dtype=object)
    base = np.array([[int(M[0,0])%mod, int(M[0,1])%mod],
                      [int(M[1,0])%mod, int(M[1,1])%mod]], dtype=object)
    while k > 0:
        if k & 1:
            result = mat_mul_mod(result, base, mod)
        base = mat_mul_mod(base, base, mod)
        k >>= 1
    return result

def mat_mul_mod(A, B, mod):
    """2x2 matrix multiply mod N."""
    return np.array([
        [(A[0,0]*B[0,0]+A[0,1]*B[1,0])%mod, (A[0,0]*B[0,1]+A[0,1]*B[1,1])%mod],
        [(A[1,0]*B[0,0]+A[1,1]*B[1,0])%mod, (A[1,0]*B[0,1]+A[1,1]*B[1,1])%mod]
    ], dtype=object)

def valid(m, n):
    return m > 0 and n >= 0 and m > n

def derived_values(m, n):
    if not valid(m, n):
        return []
    a = m*m - n*n
    b = 2*m*n
    c = m*m + n*n
    d = m - n
    s = m + n
    return [v for v in [a, b, c, m, n, d, s, d*d, s*s] if v > 0]

def check_factor(N, m, n):
    for v in derived_values(m, n):
        g = gcd(v, N)
        if 1 < g < N:
            return g
    return None

def miller_rabin(n, witnesses=(2,3,5,7,11,13,17,19,23,29,31,37)):
    if n < 2: return False
    if n in (2,3): return True
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
        else: return False
    return True

def gen_semi(bits, seed=None):
    rng = random.Random(seed)
    half = bits // 2
    while True:
        p = rng.getrandbits(half) | (1 << (half-1)) | 1
        if miller_rabin(p): break
    while True:
        q = rng.getrandbits(half) | (1 << (half-1)) | 1
        if q != p and miller_rabin(q): break
    return min(p,q), max(p,q), p*q

def banner(title):
    w = 70
    print("\n" + "=" * w)
    print(f"  {title}")
    print("=" * w)


# ============================================================
# FIELD 11: DIFFERENTIAL EQUATIONS / DYNAMICAL SYSTEMS
# ============================================================

def experiment_11():
    """B3-parabolic arithmetic progression factoring.

    B3 = [[1,2],[0,1]] has eigenvalue 1 (multiplicity 2) — parabolic.
    B3^k * (m,n) = (m+2kn, n), so n is FIXED along B3 paths.
    A = (m+2kn)^2 - n^2 = (m+2kn-n)(m+2kn+n) — arithmetic progression in k.
    We search for k where gcd(A, N) > 1.
    """
    banner("FIELD 11: DYNAMICAL SYSTEMS — B3 Parabolic Arithmetic Progression")

    results = {}
    total_found = 0
    total_tests = 0

    for bits in BIT_SIZES:
        t0 = time.time()
        found = 0
        trials = 50 if bits <= 32 else 20
        steps_list = []

        for trial in range(trials):
            p, q, N = gen_semi(bits, seed=bits*1000+trial)
            factored = False

            for m0, n0 in ROOTS:
                if factored:
                    break
                # B3 path: (m0+2k*n0, n0) for k=0,1,2,...
                n_fix = n0
                max_k = min(100000, 10 * isqrt(N))
                for k in range(max_k):
                    m_k = m0 + 2 * k * n_fix
                    if m_k <= n_fix:
                        continue
                    # A = m_k^2 - n_fix^2
                    A = m_k * m_k - n_fix * n_fix
                    g = gcd(A, N)
                    if 1 < g < N:
                        found += 1
                        steps_list.append(k)
                        factored = True
                        break
                    # Also check 2*m_k*n_fix
                    B = 2 * m_k * n_fix
                    g = gcd(B, N)
                    if 1 < g < N:
                        found += 1
                        steps_list.append(k)
                        factored = True
                        break

            total_tests += 1

        elapsed = time.time() - t0
        rate = found / trials * 100
        avg_k = (sum(steps_list) / len(steps_list)) if steps_list else float('inf')
        results[bits] = (rate, avg_k, elapsed)
        total_found += found
        print(f"  {bits}b: {found}/{trials} factored ({rate:.0f}%), "
              f"avg_k={avg_k:.0f}, {elapsed:.2f}s")

    # Eigenvalue analysis
    print("\n  Eigenvalue analysis of Berggren matrices:")
    for name, M in BERGGREN.items():
        Mf = M.astype(float)
        eigvals = np.linalg.eigvals(Mf)
        print(f"    {name}: eigenvalues = {eigvals}, trace = {int(M[0,0]+M[1,1])}, "
              f"det = {int(M[0,0]*M[1,1]-M[0,1]*M[1,0])}")

    # Verify B3 parabolic property
    print("\n  B3 parabolic verification:")
    for m0, n0 in ROOTS[:3]:
        print(f"    Root ({m0},{n0}): B3^k gives n={n0} fixed, "
              f"m sequence: {[m0+2*k*n0 for k in range(6)]}")

    # Compare B1/B2 (hyperbolic) vs B3 (parabolic) growth
    print("\n  Growth comparison (10 steps from (2,1)):")
    for name, M in BERGGREN.items():
        m, n = 2, 1
        sizes = []
        for _ in range(10):
            m, n = apply_mat(M, m, n)
            if m > 0 and n >= 0:
                sizes.append(m*m + n*n)
            else:
                break
        if sizes:
            growth = [sizes[i+1]/sizes[i] if sizes[i]>0 else 0
                      for i in range(min(5, len(sizes)-1))]
            print(f"    {name}: growth ratios = {[f'{g:.3f}' for g in growth]}")

    print(f"\n  VERDICT: B3 parabolic AP search — overall {total_found} factored")
    return results


# ============================================================
# FIELD 12: INFORMATION THEORY
# ============================================================

def experiment_12():
    """Information-theoretic analysis of Pythagorean tree walks.

    Measure mutual information I(tree_state; factor) at each depth.
    Compare: does path accumulation carry more info than position alone?
    Compute entropy of gcd distribution along walks.
    """
    banner("FIELD 12: INFORMATION THEORY — Mutual Information Along Tree Walks")

    results = {}

    for bits in [20, 24, 28, 32, 36]:
        t0 = time.time()
        trials = 100 if bits <= 24 else 40
        depth = min(200, 2 ** (bits // 4))

        # Collect statistics
        depth_mi_position = defaultdict(list)  # MI from position mod p
        depth_mi_path = defaultdict(list)       # MI from accumulated path
        gcd_entropy_by_depth = defaultdict(list)

        for trial in range(trials):
            p, q, N = gen_semi(bits, seed=bits*2000+trial)

            for m0, n0 in ROOTS[:4]:
                # Random walk on tree
                m, n = m0, n0
                path_code = 0  # Encode path as base-3 number
                for d in range(depth):
                    # Choose random Berggren child
                    choice = random.randint(0, 2)
                    M = [B1, B2, B3][choice]
                    m_new, n_new = apply_mat(M, m, n)
                    if m_new > 0 and n_new >= 0 and m_new > n_new:
                        m, n = m_new, n_new
                    else:
                        continue

                    path_code = path_code * 3 + choice

                    # Position information: bin (m mod N) relative to p
                    m_mod_p = m % p
                    m_mod_q = m % q
                    m_mod_N = m % N

                    # Scent: how close is m mod p to 0?
                    scent_p = min(m_mod_p, p - m_mod_p) / p
                    scent_q = min(m_mod_q, q - m_mod_q) / q

                    # Position info: can we distinguish p from q?
                    # Use: |scent_p - scent_q| as a proxy for MI
                    depth_mi_position[d].append(abs(scent_p - scent_q))

                    # Path info: does the path code mod small primes
                    # correlate with p?
                    if path_code > 0:
                        pc_mod_p = path_code % p if p > 1 else 0
                        pc_mod_q = path_code % q if q > 1 else 0
                        path_diff = abs(pc_mod_p / p - pc_mod_q / q)
                        depth_mi_path[d].append(path_diff)

                    # GCD entropy: distribution of gcd(A, N)
                    A = m*m - n*n
                    g = gcd(A, N)
                    gcd_entropy_by_depth[d].append(g)

        elapsed = time.time() - t0

        # Analyze MI decay
        sample_depths = sorted(depth_mi_position.keys())
        checkpoints = [d for d in sample_depths if d % max(1, len(sample_depths)//8) == 0][:8]

        print(f"\n  {bits}b semiprimes ({elapsed:.2f}s):")
        print(f"    {'Depth':>6} {'Pos_MI_proxy':>12} {'Path_MI_proxy':>13} {'GCD_entropy':>12}")

        for d in checkpoints:
            pos_vals = depth_mi_position[d]
            path_vals = depth_mi_path.get(d, [0])
            gcd_vals = gcd_entropy_by_depth[d]

            pos_mi = sum(pos_vals) / len(pos_vals) if pos_vals else 0
            path_mi = sum(path_vals) / len(path_vals) if path_vals else 0

            # Compute entropy of gcd distribution
            counts = Counter(gcd_vals)
            total = sum(counts.values())
            entropy = 0
            for c in counts.values():
                if c > 0:
                    prob = c / total
                    entropy -= prob * log2(prob)

            print(f"    {d:>6} {pos_mi:>12.6f} {path_mi:>13.6f} {entropy:>12.4f}")

        # Channel capacity estimate
        # Max info per step ~ log2(3) = 1.585 bits (3 choices)
        # But actual info about factor is much less
        print(f"    Channel capacity upper bound: {log2(3):.3f} bits/step")

        results[bits] = elapsed

    print(f"\n  VERDICT: Position MI proxy should DECREASE with depth (mod-N mixing).")
    print(f"           Path MI may increase (accumulated choices encode structure).")
    return results


# ============================================================
# FIELD 13: ALGEBRAIC GEOMETRY
# ============================================================

def experiment_13():
    """Algebraic geometry of Pythagorean conic intersections.

    x^2 + y^2 = z^2 is a conic in P^2.
    For factor p: A = m^2-n^2 = 0 mod p iff m = +/-n mod p.
    These are the 2 intersection points (Bezout's theorem).
    Use these constraints to SIEVE the tree.
    """
    banner("FIELD 13: ALGEBRAIC GEOMETRY — Conic Intersection Sieving")

    results = {}

    for bits in BIT_SIZES:
        t0 = time.time()
        found_sieve = 0
        found_random = 0
        trials = 50 if bits <= 32 else 15

        for trial in range(trials):
            p, q, N = gen_semi(bits, seed=bits*3000+trial)

            # --- Method 1: Algebraic sieve ---
            # For each small FB prime r, A = m^2-n^2 = 0 mod r
            # iff m = +/-n mod r.
            # Use CRT-like approach: find (m,n) satisfying constraints
            # for multiple primes, then check gcd with N.
            fb_primes = [r for r in range(3, min(500, isqrt(N)), 2) if miller_rabin(r)]

            # For each root, walk tree but prioritize branches where
            # m = +/-n mod N (which means m = +/-n mod p AND mod q)
            factored_sieve = False
            max_steps = 5000

            for m0, n0 in ROOTS:
                if factored_sieve:
                    break
                # BFS with algebraic scoring
                queue = [(m0, n0)]
                visited = set()
                steps = 0

                while queue and steps < max_steps and not factored_sieve:
                    m, n = queue.pop(0)
                    if (m, n) in visited:
                        continue
                    visited.add((m, n))
                    steps += 1

                    g = check_factor(N, m, n)
                    if g:
                        found_sieve += 1
                        factored_sieve = True
                        break

                    # Score children by algebraic criterion:
                    # |m^2 - n^2 mod N| should be small
                    children = []
                    for M in [B1, B2, B3]:
                        mc, nc = apply_mat(M, m, n)
                        if mc > 0 and nc >= 0 and mc > nc and (mc, nc) not in visited:
                            A_mod = (mc*mc - nc*nc) % N
                            score = min(A_mod, N - A_mod)
                            children.append((score, mc, nc))
                    children.sort()
                    for _, mc, nc in children:
                        queue.append((mc, nc))

            # --- Method 2: Random walk baseline ---
            factored_rand = False
            for m0, n0 in ROOTS:
                if factored_rand:
                    break
                m, n = m0, n0
                for step in range(max_steps):
                    g = check_factor(N, m, n)
                    if g:
                        found_random += 1
                        factored_rand = True
                        break
                    M = [B1, B2, B3][random.randint(0, 2)]
                    mc, nc = apply_mat(M, m, n)
                    if mc > 0 and nc >= 0 and mc > nc:
                        m, n = mc, nc

        elapsed = time.time() - t0
        rate_s = found_sieve / trials * 100
        rate_r = found_random / trials * 100
        results[bits] = (rate_s, rate_r, elapsed)
        print(f"  {bits}b: sieve={found_sieve}/{trials} ({rate_s:.0f}%), "
              f"random={found_random}/{trials} ({rate_r:.0f}%), {elapsed:.2f}s")

    # Bezout analysis
    print("\n  Bezout's theorem verification:")
    for p_test in [7, 13, 29, 97]:
        # Count (m,n) mod p with m^2 = n^2 mod p
        solutions = []
        for m in range(p_test):
            for n in range(p_test):
                if (m*m - n*n) % p_test == 0:
                    solutions.append((m, n))
        print(f"    p={p_test}: {len(solutions)} solutions to m^2=n^2 mod p "
              f"(expected ~{2*p_test} from 2 lines m=+/-n)")

    # Intersection constraint propagation
    print("\n  Constraint propagation (m = +/-n mod r) density:")
    for r in [3, 5, 7, 11, 13]:
        # Fraction of (m,n) pairs satisfying m=+/-n mod r
        hits = sum(1 for m in range(r) for n in range(r)
                   if (m-n) % r == 0 or (m+n) % r == 0)
        print(f"    r={r}: {hits}/{r*r} = {hits/(r*r):.3f} "
              f"(2/r - 1/r^2 = {2/r - 1/r**2:.3f})")

    print(f"\n  VERDICT: Algebraic sieve vs random walk — does intersection scoring help?")
    return results


# ============================================================
# FIELD 14: OPTIMIZATION
# ============================================================

def experiment_14():
    """Optimization-based factoring on the Pythagorean tree.

    1. Continuous relaxation: minimize |m^2-n^2 - kN| over R^2
       (Fermat hyperbola), then round to nearest tree node.
    2. Simulated annealing on the tree with various cooling schedules.
    """
    banner("FIELD 14: OPTIMIZATION — Continuous Relaxation + Simulated Annealing")

    results = {}

    # --- Part A: Continuous relaxation ---
    print("\n  Part A: Continuous Relaxation (Fermat hyperbola rounding)")

    for bits in BIT_SIZES:
        t0 = time.time()
        found = 0
        trials = 50 if bits <= 32 else 15

        for trial in range(trials):
            p, q, N = gen_semi(bits, seed=bits*4000+trial)
            factored = False

            # For each small k, solve m^2 - n^2 = kN
            # => (m-n)(m+n) = kN => m = (a+b)/2, n = (a-b)/2
            # where a*b = kN, a > b, a,b same parity
            max_k = min(1000, isqrt(N))
            for k in range(1, max_k + 1):
                if factored:
                    break
                target = k * N
                # Find divisor pairs of target near sqrt(target)
                s = isqrt(target)
                for delta in range(min(100, s)):
                    b = s - delta
                    if b < 1:
                        break
                    if target % b == 0:
                        a = target // b
                        if a > b and (a + b) % 2 == 0:
                            m = (a + b) // 2
                            n = (a - b) // 2
                            if m > n > 0:
                                g = check_factor(N, m, n)
                                if g:
                                    found += 1
                                    factored = True
                                    break
                    b2 = s + delta + 1
                    if target % b2 == 0:
                        a2 = target // b2
                        if a2 > b2 and (a2 + b2) % 2 == 0:
                            m = (a2 + b2) // 2
                            n = (a2 - b2) // 2
                            if m > n > 0:
                                g = check_factor(N, m, n)
                                if g:
                                    found += 1
                                    factored = True
                                    break

        elapsed = time.time() - t0
        rate = found / trials * 100
        results[f'relax_{bits}'] = (rate, elapsed)
        print(f"    {bits}b: {found}/{trials} ({rate:.0f}%), {elapsed:.2f}s")

    # --- Part B: Simulated Annealing ---
    print("\n  Part B: Simulated Annealing on Tree")

    schedules = {
        'exponential': lambda t, T0, step, max_s: T0 * (0.995 ** step),
        'linear':      lambda t, T0, step, max_s: T0 * (1 - step / max_s),
        'logarithmic': lambda t, T0, step, max_s: T0 / (1 + log(1 + step)),
    }

    for bits in [20, 24, 28, 32, 36, 40]:
        t0 = time.time()
        trials = 30 if bits <= 28 else 15
        max_steps = 10000

        sched_results = {}
        for sched_name, sched_fn in schedules.items():
            found = 0
            for trial in range(trials):
                p, q, N = gen_semi(bits, seed=bits*5000+trial)
                factored = False

                for m0, n0 in ROOTS[:3]:
                    if factored:
                        break
                    m, n = m0, n0
                    T0 = float(N)
                    best_score = float('inf')

                    for step in range(max_steps):
                        g = check_factor(N, m, n)
                        if g:
                            found += 1
                            factored = True
                            break

                        # Current score: min residue of A mod N
                        A = m*m - n*n
                        A_mod = A % N
                        score = min(A_mod, N - A_mod)
                        if score < best_score:
                            best_score = score

                        # Temperature
                        T = sched_fn(None, 1.0, step, max_steps)
                        if T <= 0:
                            T = 1e-10

                        # Try random child
                        M = [B1, B2, B3][random.randint(0, 2)]
                        mc, nc = apply_mat(M, m, n)
                        if mc > 0 and nc >= 0 and mc > nc:
                            Ac = mc*mc - nc*nc
                            Ac_mod = Ac % N
                            new_score = min(Ac_mod, N - Ac_mod)
                            delta = (new_score - score) / max(N, 1)
                            # Accept if better, or probabilistically if worse
                            if delta < 0 or random.random() < math.exp(-delta / max(T, 1e-30)):
                                m, n = mc, nc

            sched_results[sched_name] = found

        elapsed = time.time() - t0
        parts = [f"{name}={cnt}/{trials}" for name, cnt in sched_results.items()]
        print(f"    {bits}b: {', '.join(parts)}, {elapsed:.2f}s")
        results[f'sa_{bits}'] = (sched_results, elapsed)

    print(f"\n  VERDICT: Continuous relaxation = Fermat factoring (kN = (m-n)(m+n)).")
    print(f"           SA on tree: landscape too flat for gradient signal at large N.")
    return results


# ============================================================
# FIELD 15: REPRESENTATION THEORY
# ============================================================

def experiment_15():
    """Representation theory of Berggren group action.

    tr(M^k mod N) encodes order of M in GL(2, Z/pZ) vs GL(2, Z/qZ).
    If ord_p(M) != ord_q(M), then gcd(tr(M^k) - 2, N) may reveal factor
    when tr(M^k) = 2 mod p but not mod q (M^k = I mod p).
    """
    banner("FIELD 15: REPRESENTATION THEORY — Trace-Based Order Detection")

    results = {}

    # Part A: Trace sequence analysis
    print("\n  Part A: Trace of M^k mod N — order detection")

    for bits in BIT_SIZES:
        t0 = time.time()
        found = {name: 0 for name in BERGGREN}
        trials = 50 if bits <= 32 else 15
        max_k = min(50000, 2 ** (bits // 2 + 2))

        for trial in range(trials):
            p, q, N = gen_semi(bits, seed=bits*6000+trial)

            for name, M in BERGGREN.items():
                # Compute tr(M^k mod N) for k = 1..max_k
                # Use repeated matrix multiply mod N
                Mk = np.array([[1,0],[0,1]], dtype=object)
                factored = False

                for k in range(1, max_k + 1):
                    Mk = mat_mul_mod(Mk, M, N)
                    tr_k = (int(Mk[0,0]) + int(Mk[1,1])) % N

                    # Check if tr = 2 mod N (would mean M^k = I mod N)
                    g = gcd(tr_k - 2, N) if tr_k != 2 else 0
                    if 1 < g < N:
                        found[name] += 1
                        factored = True
                        break

                    # Also check tr = -2 mod N (M^k = -I)
                    g2 = gcd((tr_k + 2) % N, N)
                    if 1 < g2 < N:
                        found[name] += 1
                        factored = True
                        break

                    # Check det-based: det(M^k - I) mod N
                    det_val = ((Mk[0,0]-1)*(Mk[1,1]-1) - Mk[0,1]*Mk[1,0]) % N
                    g3 = gcd(int(det_val), N)
                    if 1 < g3 < N:
                        found[name] += 1
                        factored = True
                        break

                if factored:
                    break

        elapsed = time.time() - t0
        parts = [f"{name}={cnt}/{trials}" for name, cnt in found.items()]
        total_found = max(found.values())
        results[bits] = (found, elapsed)
        print(f"  {bits}b: {', '.join(parts)}, {elapsed:.2f}s")

    # Part B: Order of M mod p for small primes
    print("\n  Part B: Order of Berggren matrices mod small primes")
    for prime in [5, 7, 11, 13, 17, 19, 23, 29, 31]:
        orders = {}
        for name, M in BERGGREN.items():
            Mk = np.array([[1,0],[0,1]], dtype=object)
            for k in range(1, prime * prime + 1):
                Mk = mat_mul_mod(Mk, M, prime)
                if (int(Mk[0,0]) == 1 and int(Mk[0,1]) == 0 and
                    int(Mk[1,0]) == 0 and int(Mk[1,1]) == 1):
                    orders[name] = k
                    break
            else:
                orders[name] = f">{prime*prime}"
        print(f"    p={prime:>2}: " +
              ", ".join(f"{name}:ord={orders[name]}" for name in BERGGREN))

    # Part C: Character analysis
    print("\n  Part C: Character values chi(M^k) = tr(M^k) mod p")
    for prime in [7, 13, 29]:
        print(f"    p={prime}:")
        for name, M in BERGGREN.items():
            traces = []
            Mk = np.array([[1,0],[0,1]], dtype=object)
            for k in range(1, min(20, prime+1)):
                Mk = mat_mul_mod(Mk, M, prime)
                traces.append(int((Mk[0,0] + Mk[1,1]) % prime))
            print(f"      {name}: tr(M^1..M^{len(traces)}) = {traces}")

    # Part D: Compare trace-based vs smooth-exponent (Pollard p-1 style)
    print("\n  Part D: Trace detection vs smooth exponent (Pollard p-1 analogy)")
    for bits in [20, 24, 28, 32]:
        trials = 30
        found_trace = 0
        found_smooth = 0
        t0 = time.time()

        for trial in range(trials):
            p, q, N = gen_semi(bits, seed=bits*7000+trial)

            # Trace method (best matrix from Part A)
            M = B1
            Mk = np.array([[1,0],[0,1]], dtype=object)
            max_k = min(10000, 2 ** (bits // 2 + 1))
            for k in range(1, max_k + 1):
                Mk = mat_mul_mod(Mk, M, N)
                det_val = ((Mk[0,0]-1)*(Mk[1,1]-1) - Mk[0,1]*Mk[1,0]) % N
                g = gcd(int(det_val), N)
                if 1 < g < N:
                    found_trace += 1
                    break

            # Smooth exponent (Pollard p-1 style): compute M^(k!) mod N
            Mfact = np.array([[int(M[0,0]),int(M[0,1])],
                              [int(M[1,0]),int(M[1,1])]], dtype=object)
            Mk2 = np.array([[1,0],[0,1]], dtype=object)
            for k in range(1, min(500, isqrt(max_k))):
                # Raise to k-th power (so total exponent = k!)
                Mk2 = mat_pow_mod(Mk2, k, N) if k > 1 else mat_mul_mod(Mk2, Mfact, N)
                # Actually: multiply current result by M^k
                Mk_step = mat_pow_mod(Mfact, k, N)
                Mk2 = mat_mul_mod(Mk2, Mk_step, N)
                det_val = ((Mk2[0,0]-1)*(Mk2[1,1]-1) - Mk2[0,1]*Mk2[1,0]) % N
                g = gcd(int(det_val), N)
                if 1 < g < N:
                    found_smooth += 1
                    break

        elapsed = time.time() - t0
        print(f"    {bits}b: trace={found_trace}/{trials}, "
              f"smooth_exp={found_smooth}/{trials}, {elapsed:.2f}s")

    print(f"\n  VERDICT: Trace-based = detecting M^k = I mod p.")
    print(f"           Equivalent to group order detection in GL(2, Z/pZ).")
    print(f"           Smooth exponent version = Pollard p-1 generalized to matrices.")
    return results


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("  PYTHAGOREAN TREE FACTORING — CROSS-MATH EXPERIMENTS BATCH 3")
    print("  Fields 11-15: DynSys, InfoTheory, AlgGeom, Optim, RepTheory")
    print(f"  Roots: {ROOTS}")
    print(f"  Bit sizes: {BIT_SIZES}")
    print("=" * 70)

    all_results = {}
    t_total = time.time()

    experiments = [
        (11, experiment_11),
        (12, experiment_12),
        (13, experiment_13),
        (14, experiment_14),
        (15, experiment_15),
    ]

    for num, fn in experiments:
        t0 = time.time()
        try:
            r = fn()
            all_results[num] = r
        except Exception as ex:
            print(f"\n  FIELD {num} FAILED: {ex}")
            import traceback; traceback.print_exc()
        elapsed = time.time() - t0
        print(f"  [Field {num} total: {elapsed:.1f}s]")

    total = time.time() - t_total
    print("\n" + "=" * 70)
    print(f"  ALL EXPERIMENTS COMPLETE — {total:.1f}s total")
    print("=" * 70)

    # Summary table
    print("\n  SUMMARY OF FINDINGS:")
    print("  " + "-" * 66)
    print(f"  {'Field':>8} {'Description':<40} {'Key Result'}")
    print("  " + "-" * 66)
    summaries = [
        (11, "B3 Parabolic AP Search",
         "Arithmetic progression via fixed n"),
        (12, "Mutual Information Along Walks",
         "Position MI decays; path MI behavior"),
        (13, "Conic Intersection Sieving",
         "Bezout scoring vs random walk"),
        (14, "Continuous Relaxation + SA",
         "Relaxation = Fermat; SA landscape flat"),
        (15, "Trace-Based Order Detection",
         "Matrix order in GL(2,Z/pZ) ~ Pollard p-1"),
    ]
    for num, desc, result in summaries:
        print(f"  {num:>8} {desc:<40} {result}")
    print("  " + "-" * 66)

    return all_results


if __name__ == '__main__':
    main()
