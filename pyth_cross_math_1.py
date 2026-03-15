#!/usr/bin/env python3
"""
Pythagorean Tree Factoring — Cross-Mathematical Field Experiments

Five mathematical fields connected to Berggren tree factoring:
  1. Tropical Geometry (min-plus algebra)
  2. P-adic Numbers (valuation patterns)
  3. Ergodic Theory (time averages vs space averages)
  4. Knot Theory (braid words, Alexander polynomial)
  5. Coding Theory (conic codes, minimum distance)

Plus: alternative tree roots experiment across all fields.

Memory limit: 2GB. Each experiment < 60s. Uses gmpy2.
"""

import time
import random
import gmpy2
from gmpy2 import mpz, gcd, is_prime, next_prime, log2
from math import log, isqrt
from collections import defaultdict, Counter

# ============================================================
# INFRASTRUCTURE
# ============================================================

# Berggren matrices: map (m,n) -> child (m',n')
# B1: (2m-n, m), B2: (2m+n, m), B3: (m+2n, n)
def berggren_b1(m, n): return (2*m - n, m)
def berggren_b2(m, n): return (2*m + n, m)
def berggren_b3(m, n): return (m + 2*n, n)

BERGGREN = [berggren_b1, berggren_b2, berggren_b3]
BERGGREN_NAMES = ["B1", "B2", "B3"]

# Standard and alternative roots
ROOTS = [
    (2, 1),   # standard: (3,4,5)
    (3, 2),   # (5,12,13)
    (4, 1),   # (15,8,17)
    (4, 3),   # (7,24,25)
    (5, 2),   # (21,20,29)
    (5, 4),   # (9,40,41)
    (6, 1),   # (35,12,37)
    (7, 2),   # (45,28,53)
    (7, 4),   # (33,56,65) — not primitive (gcd=1 but 65=5*13)
    (8, 3),   # (55,48,73)
]

def triple_from_mn(m, n):
    """Pythagorean triple from generator (m,n): A=m^2-n^2, B=2mn, C=m^2+n^2."""
    m, n = mpz(m), mpz(n)
    return m*m - n*n, 2*m*n, m*m + n*n

def check_factor_mn(N, m, n):
    """Check if (m,n) node reveals a factor of N."""
    m, n = mpz(m), mpz(n)
    A = m*m - n*n
    B = 2*m*n
    C = m*m + n*n
    for v in [A, B, C, m-n, m+n, m, n]:
        if v <= 0:
            continue
        g = gcd(mpz(v), N)
        if 1 < g < N:
            return int(g)
    return None

def gen_semiprime(bits, rng=None):
    """Generate a semiprime N = p*q with p,q each ~bits/2 bits."""
    if rng is None:
        rng = random.Random()
    half = bits // 2
    while True:
        p = gmpy2.next_prime(mpz(rng.getrandbits(half)) | (mpz(1) << (half - 1)))
        q = gmpy2.next_prime(mpz(rng.getrandbits(half)) | (mpz(1) << (half - 1)))
        if p != q:
            return p * q, p, q

def bfs_tree(root_m, root_n, N, max_nodes):
    """BFS the Berggren tree from (root_m, root_n) mod N, return list of (m,n) nodes."""
    nodes = []
    queue = [(mpz(root_m), mpz(root_n))]
    visited = set()
    visited.add((int(root_m) % (1 << 30), int(root_n) % (1 << 30)))
    while queue and len(nodes) < max_nodes:
        m, n = queue.pop(0)
        nodes.append((m, n))
        for bfn in BERGGREN:
            cm, cn = bfn(m, n)
            if cm > 0 and cn > 0 and cm > cn:
                key = (int(cm) % (1 << 30), int(cn) % (1 << 30))
                if key not in visited:
                    visited.add(key)
                    queue.append((cm, cn))
    return nodes

def bfs_tree_mod(root_m, root_n, N, max_nodes):
    """BFS the Berggren tree mod N, return list of (m%N, n%N) plus original for GCD."""
    nodes = []
    queue = [(mpz(root_m) % N, mpz(root_n) % N)]
    visited = set()
    visited.add((int(queue[0][0]), int(queue[0][1])))
    while queue and len(nodes) < max_nodes:
        m, n = queue.pop(0)
        nodes.append((m, n))
        for bfn in BERGGREN:
            cm, cn = bfn(m, n)
            cm, cn = cm % N, cn % N
            key = (int(cm), int(cn))
            if key not in visited:
                visited.add(key)
                queue.append((cm, cn))
    return nodes

def random_walk(root_m, root_n, steps, N=None):
    """Random walk on Berggren tree. If N given, work mod N."""
    rng = random.Random(42)
    m, n = mpz(root_m), mpz(root_n)
    path = [(m, n)]
    for _ in range(steps):
        bfn = rng.choice(BERGGREN)
        cm, cn = bfn(m, n)
        if N is not None:
            cm, cn = cm % N, cn % N
        if cm > 0 and cn >= 0:
            m, n = cm, cn
        path.append((m, n))
    return path


# ============================================================
# FIELD 1: TROPICAL GEOMETRY
# ============================================================

def experiment_tropical(test_cases, max_time=55):
    """
    Tropical (min-plus) algebra on Berggren tree.

    In tropical semiring: a + b = min(a,b), a * b = a+b.
    Tropical Berggren: B1_trop(x,y) = (min(x+log2, y+log2-log(n)), ...) etc.

    We use log-valuations: for node (m,n), tropical coords = (log|m|, log|n|).
    Tropical Berggren maps become piecewise-linear.

    Test: Does the tropical period (orbit length in tropical space) mod p differ
    from mod q, revealing the factorization?
    """
    print("=" * 70)
    print("FIELD 1: TROPICAL GEOMETRY")
    print("=" * 70)

    t0 = time.time()
    results = {"factor_found": 0, "total": 0, "tropical_period_differs": 0}

    for bits, N, p, q in test_cases:
        if time.time() - t0 > max_time:
            break
        results["total"] += 1

        # Tropical coordinates: use log of absolute value
        # Tropical Berggren: B1(x,y) in tropical = piecewise linear map
        # We discretize by tracking integer approximations of log2

        best_root = None
        best_score = 0

        for root_m, root_n in ROOTS[:6]:
            # Compute tropical orbit: track floor(log2(m)), floor(log2(n))
            # but we work mod N, so use actual values
            m, n = mpz(root_m), mpz(root_n)

            # Tropical evaluation: for each node, compute
            # trop_val = min(v_2(A), v_2(B), v_2(C)) where v_2 = 2-adic valuation
            # This connects tropical geometry to p-adic (Field 2)
            trop_accum_mod_p = []
            trop_accum_mod_q = []

            walk_len = min(500, max(100, 50000 // bits))

            for step in range(walk_len):
                A = m*m - n*n
                B = 2*m*n
                C = m*m + n*n

                # Tropical valuation: v_2 (2-adic)
                def v2(x):
                    if x == 0: return 999
                    x = abs(int(x))
                    v = 0
                    while x % 2 == 0:
                        x //= 2
                        v += 1
                    return v

                tv = min(v2(A), v2(B), v2(C))

                # Track mod p and mod q separately (oracle, for analysis)
                trop_accum_mod_p.append(tv % int(p) if int(p) > 1 else 0)
                trop_accum_mod_q.append(tv % int(q) if int(q) > 1 else 0)

                # GCD check (the actual factoring attempt)
                g = check_factor_mn(N, m, n)
                if g:
                    results["factor_found"] += 1
                    best_root = (root_m, root_n)
                    break

                # Tropical-guided branching: pick child with highest tropical valuation
                children = []
                for bfn in BERGGREN:
                    cm, cn = bfn(m, n)
                    if cm > 0 and cn > 0 and cm > cn:
                        cA = cm*cm - cn*cn
                        ctv = v2(cA)
                        children.append((ctv, cm, cn))

                if children:
                    # Tropical heuristic: prefer high 2-adic valuation
                    children.sort(reverse=True)
                    _, m, n = children[0]
                else:
                    break

            # Check if tropical patterns differ mod p vs mod q
            if len(trop_accum_mod_p) > 10:
                avg_p = sum(trop_accum_mod_p) / len(trop_accum_mod_p)
                avg_q = sum(trop_accum_mod_q) / len(trop_accum_mod_q)
                score = abs(avg_p - avg_q)
                if score > best_score:
                    best_score = score
                    best_root = (root_m, root_n)

        if best_score > 0.5:
            results["tropical_period_differs"] += 1

    elapsed = time.time() - t0

    # Also test: tropical GCD — accumulate product of tropical-selected A values
    # and periodically GCD with N
    trop_gcd_successes = 0
    for bits, N, p, q in test_cases[:10]:
        if time.time() - t0 > max_time:
            break
        product = mpz(1)
        m, n = mpz(2), mpz(1)
        for step in range(1000):
            A = (m*m - n*n) % N
            if A == 0:
                break
            product = (product * A) % N
            if step % 50 == 49:
                g = gcd(product, N)
                if 1 < g < N:
                    trop_gcd_successes += 1
                    break
            # Navigate tropically
            children = []
            for bfn in BERGGREN:
                cm, cn = bfn(m, n)
                cm, cn = cm % N, cn % N
                if cm != 0 and cn != 0:
                    cA = (cm*cm - cn*cn) % N
                    # 2-adic valuation of cA mod N approximated by gcd with power of 2
                    g2 = gcd(cA, mpz(1) << 30)
                    children.append((int(g2), cm, cn))
            if children:
                children.sort(reverse=True)
                _, m, n = children[0]
            else:
                break

    print(f"\n  Results ({elapsed:.1f}s):")
    print(f"    Direct factor found: {results['factor_found']}/{results['total']}")
    print(f"    Tropical period differs (p vs q): {results['tropical_period_differs']}/{results['total']}")
    print(f"    Tropical-GCD product method: {trop_gcd_successes}/{min(10, len(test_cases))}")

    if results["factor_found"] > results["total"] * 0.3 or trop_gcd_successes > 3:
        verdict = "PROMISING"
    elif results["tropical_period_differs"] > results["total"] * 0.5:
        verdict = "PROMISING (theoretical signal)"
    else:
        verdict = "REJECTED"

    print(f"    Verdict: {verdict}")
    return verdict


# ============================================================
# FIELD 2: P-ADIC NUMBERS
# ============================================================

def experiment_padic(test_cases, max_time=55):
    """
    P-adic valuation analysis along Berggren tree paths.

    Key identity: v_p(m^2 - n^2) = v_p(m-n) + v_p(m+n) for odd p.

    Hypothesis: If p | N, then the p-adic valuations of tree nodes
    have a distinctive pattern that differs from generic primes.
    We can detect this without knowing p by looking at v_N patterns.

    Also test: p-adic limit of iterated Berggren — does the sequence
    converge in Z_p for the correct prime factor?
    """
    print("\n" + "=" * 70)
    print("FIELD 2: P-ADIC NUMBERS")
    print("=" * 70)

    t0 = time.time()
    results = {"factor_found": 0, "total": 0, "valuation_signal": 0}
    root_scores = defaultdict(list)

    for bits, N, p, q in test_cases:
        if time.time() - t0 > max_time:
            break
        results["total"] += 1

        found_this = False

        for root_m, root_n in ROOTS[:6]:
            m, n = mpz(root_m), mpz(root_n)

            # Track N-adic valuations: v_N(A) = how many times N divides A
            # This is 0 almost always, but v_p(A) and v_q(A) are more interesting
            # We approximate v_p by looking at gcd(A, N^k)

            val_pattern = []
            gcd_accum = mpz(1)
            walk_len = min(800, max(200, 80000 // bits))

            for step in range(walk_len):
                A = m*m - n*n
                B = 2*m*n

                # P-adic approach: accumulate gcd info
                # v_p(A) > 0 iff p | A, which means gcd(A, N) is divisible by p
                g = gcd(A, N)
                if 1 < g < N:
                    results["factor_found"] += 1
                    found_this = True
                    root_scores[(root_m, root_n)].append(step)
                    break

                # Track the p-adic "convergence" — does gcd(A_k - A_{k-1}, N) grow?
                if len(val_pattern) > 0:
                    diff = abs(A - val_pattern[-1])
                    if diff > 0:
                        gcd_accum = (gcd_accum * diff) % N
                        if step % 30 == 29:
                            g = gcd(gcd_accum, N)
                            if 1 < g < N:
                                results["factor_found"] += 1
                                found_this = True
                                root_scores[(root_m, root_n)].append(step)
                                break
                            gcd_accum = mpz(1)

                val_pattern.append(A)

                # Navigate: try all children, pick one with highest gcd(A_child, N)
                # (p-adic "closest to zero in Z_p")
                best_child = None
                best_gval = -1
                for bfn in BERGGREN:
                    cm, cn = bfn(m, n)
                    if cm > 0 and cn > 0 and cm > cn:
                        cA = cm*cm - cn*cn
                        gv = gcd(cA, N)
                        gvi = int(gv)
                        if gvi > best_gval:
                            best_gval = gvi
                            best_child = (cm, cn)

                if best_child:
                    m, n = best_child
                else:
                    break

            if found_this:
                break

        # P-adic convergence test: does the sequence m_k mod p converge?
        # (Oracle test with known p,q for analysis)
        if not found_this and len(val_pattern) > 10:
            # Check if A_k mod p stabilizes
            last_few_p = [int(v) % int(p) for v in val_pattern[-10:]]
            last_few_q = [int(v) % int(q) for v in val_pattern[-10:]]
            var_p = len(set(last_few_p))
            var_q = len(set(last_few_q))
            if var_p != var_q:
                results["valuation_signal"] += 1

    # P-adic difference method: for pairs of nodes, gcd(A_i - A_j, N)
    padic_diff_successes = 0
    for bits, N, p, q in test_cases[:10]:
        if time.time() - t0 > max_time:
            break
        nodes_A = []
        m, n = mpz(2), mpz(1)
        for step in range(300):
            A = (m*m - n*n) % N
            nodes_A.append(A)
            bfn = BERGGREN[step % 3]
            cm, cn = bfn(m, n)
            m, n = cm % N, cn % N
            if m == 0 or n == 0:
                break

        # Pairwise GCD of differences
        found = False
        product = mpz(1)
        count = 0
        for i in range(1, len(nodes_A)):
            diff = nodes_A[i] - nodes_A[i-1]
            if diff != 0:
                product = (product * diff) % N
                count += 1
                if count % 40 == 0:
                    g = gcd(product, N)
                    if 1 < g < N:
                        padic_diff_successes += 1
                        found = True
                        break
                    product = mpz(1)

    elapsed = time.time() - t0

    print(f"\n  Results ({elapsed:.1f}s):")
    print(f"    Direct factor found: {results['factor_found']}/{results['total']}")
    print(f"    P-adic valuation signal: {results['valuation_signal']}/{results['total']}")
    print(f"    P-adic difference method: {padic_diff_successes}/{min(10, len(test_cases))}")

    if root_scores:
        print(f"    Best roots (by avg steps to factor):")
        for root, steps in sorted(root_scores.items(), key=lambda x: sum(x[1])/len(x[1]))[:3]:
            print(f"      ({root[0]},{root[1]}): avg {sum(steps)/len(steps):.0f} steps, {len(steps)} successes")

    if results["factor_found"] > results["total"] * 0.3 or padic_diff_successes > 3:
        verdict = "PROMISING"
    elif results["valuation_signal"] > results["total"] * 0.4:
        verdict = "PROMISING (theoretical signal)"
    else:
        verdict = "REJECTED"

    print(f"    Verdict: {verdict}")
    return verdict


# ============================================================
# FIELD 3: ERGODIC THEORY
# ============================================================

def experiment_ergodic(test_cases, max_time=55):
    """
    Ergodic theory analysis of Berggren dynamics on (Z/NZ)^2.

    Birkhoff ergodic theorem: for ergodic systems, time average = space average.
    If the system is NOT ergodic mod p*q (e.g., it decomposes into orbits
    of different sizes mod p vs mod q), then the time average of f(m,n)
    deviates from uniform, and the deviation encodes factor information.

    Test observable: f(m,n) = (m^2 - n^2) mod N
    Compare empirical distribution to uniform.
    """
    print("\n" + "=" * 70)
    print("FIELD 3: ERGODIC THEORY")
    print("=" * 70)

    t0 = time.time()
    results = {"factor_found": 0, "total": 0, "nonuniform": 0}
    root_comparison = defaultdict(list)  # root -> list of (bits, factor_found_bool)

    for bits, N, p, q in test_cases:
        if time.time() - t0 > max_time:
            break
        results["total"] += 1

        best_root = None
        best_factor_step = float('inf')

        for root_m, root_n in ROOTS[:8]:
            m, n = mpz(root_m) % N, mpz(root_n) % N
            if m == 0 or n == 0:
                continue

            walk_len = min(2000, max(300, 100000 // bits))

            # Collect observable: A_k = (m_k^2 - n_k^2) mod N
            observables = []
            product = mpz(1)
            found = False

            for step in range(walk_len):
                A = (m*m - n*n) % N

                if A == 0:
                    g = gcd(m - n, N)
                    if 1 < g < N:
                        results["factor_found"] += 1
                        root_comparison[(root_m, root_n)].append((bits, True, step))
                        found = True
                        if step < best_factor_step:
                            best_factor_step = step
                            best_root = (root_m, root_n)
                        break
                    g = gcd(m + n, N)
                    if 1 < g < N:
                        results["factor_found"] += 1
                        root_comparison[(root_m, root_n)].append((bits, True, step))
                        found = True
                        break
                    break

                observables.append(int(A))

                # Ergodic factoring: accumulate product, periodic GCD
                product = (product * A) % N
                if step % 50 == 49:
                    g = gcd(product, N)
                    if 1 < g < N:
                        results["factor_found"] += 1
                        root_comparison[(root_m, root_n)].append((bits, True, step))
                        found = True
                        if step < best_factor_step:
                            best_factor_step = step
                            best_root = (root_m, root_n)
                        break
                    product = mpz(1)

                # Deterministic walk: cycle through B1, B2, B3
                bfn = BERGGREN[step % 3]
                cm, cn = bfn(m, n)
                m, n = cm % N, cn % N
                if m == 0 and n == 0:
                    break

            if not found:
                root_comparison[(root_m, root_n)].append((bits, False, walk_len))

            if found:
                break

        # Ergodic analysis: check if observables are non-uniform
        if len(observables) > 50:
            # Bucket into sqrt(N) bins is impractical; use small moduli
            for test_mod in [6, 10, 12, 30]:
                buckets = Counter()
                for a in observables:
                    buckets[a % test_mod] += 1
                expected = len(observables) / test_mod
                chi2 = sum((v - expected)**2 / expected for v in buckets.values())
                # High chi2 = non-uniform = ergodic breakdown = factor signal
                if chi2 > test_mod * 3:
                    results["nonuniform"] += 1
                    break

    elapsed = time.time() - t0

    print(f"\n  Results ({elapsed:.1f}s):")
    print(f"    Factor found (via ergodic walk): {results['factor_found']}/{results['total']}")
    print(f"    Non-uniform distribution detected: {results['nonuniform']}/{results['total']}")

    # Root comparison
    print(f"\n    Root comparison (success rate):")
    for root in ROOTS[:8]:
        entries = root_comparison.get(root, [])
        if entries:
            successes = sum(1 for _, found, _ in entries if found)
            avg_steps = sum(s for _, found, s in entries if found) / max(1, successes)
            print(f"      ({root[0]},{root[1]}): {successes}/{len(entries)} success"
                  f"  avg_steps={avg_steps:.0f}" if successes else
                  f"      ({root[0]},{root[1]}): {successes}/{len(entries)} success")

    if results["factor_found"] > results["total"] * 0.3:
        verdict = "PROMISING"
    elif results["nonuniform"] > results["total"] * 0.5:
        verdict = "PROMISING (ergodic signal)"
    else:
        verdict = "REJECTED"

    print(f"    Verdict: {verdict}")
    return verdict


# ============================================================
# FIELD 4: KNOT THEORY
# ============================================================

def experiment_knot(test_cases, max_time=55):
    """
    Knot/braid theory applied to Berggren tree paths.

    Each Berggren matrix is a generator: B1=s1, B2=s2, B3=s1*s2 (braid group B_3).
    A tree path = braid word. The braid closure has knot/link invariants.

    Alexander polynomial: computable from Burau matrix representation.
    The Burau matrix for 3-strand braids uses a parameter t.

    Hypothesis: Setting t = root of unity related to N might yield
    invariants that detect factors.

    Also: linking number of the path = algebraic sum of crossings,
    which equals #B1 - #B2 (exponent sum). Does this correlate with factoring?
    """
    print("\n" + "=" * 70)
    print("FIELD 4: KNOT THEORY")
    print("=" * 70)

    t0 = time.time()
    results = {"factor_found": 0, "total": 0, "linking_correlation": 0}

    # Reduced Burau matrices for 3-strand braid group generators
    # sigma_1 -> [[-t, 1], [0, 1]]
    # sigma_2 -> [[1, 0], [-t, -t]]
    # We map B1->sigma_1, B2->sigma_2, B3->sigma_1*sigma_2

    def burau_multiply_mod(A, B, N):
        """2x2 matrix multiply mod N."""
        return [
            [(A[0][0]*B[0][0] + A[0][1]*B[1][0]) % N,
             (A[0][0]*B[0][1] + A[0][1]*B[1][1]) % N],
            [(A[1][0]*B[0][0] + A[1][1]*B[1][0]) % N,
             (A[1][0]*B[0][1] + A[1][1]*B[1][1]) % N]
        ]

    def burau_sigma1(t, N):
        return [[(-t) % N, mpz(1)], [mpz(0), mpz(1)]]

    def burau_sigma2(t, N):
        return [[mpz(1), mpz(0)], [(-t) % N, (-t) % N]]

    for bits, N, p, q in test_cases:
        if time.time() - t0 > max_time:
            break
        results["total"] += 1

        found = False

        for root_m, root_n in ROOTS[:5]:
            m, n = mpz(root_m), mpz(root_n)

            walk_len = min(500, max(100, 30000 // bits))
            braid_word = []  # sequence of 0,1,2 for B1,B2,B3

            # Build the braid word by walking the tree
            for step in range(walk_len):
                g = check_factor_mn(N, m, n)
                if g:
                    results["factor_found"] += 1
                    found = True
                    break

                # Pick branch based on (m+n) mod 3 — deterministic
                branch = int((m + n) % 3)
                braid_word.append(branch)
                cm, cn = BERGGREN[branch](m, n)
                if cm > 0 and cn > 0 and cm > cn:
                    m, n = cm, cn
                else:
                    break

            if found:
                break

        if found:
            continue

        # Compute Burau matrix for the braid word, evaluate at different t values
        # If det(Burau - I) mod p = 0 but mod q != 0 (or vice versa),
        # then gcd(det, N) reveals a factor
        for t_val in [mpz(2), mpz(3), mpz(5), mpz(7), mpz(11), mpz(13)]:
            mat = [[mpz(1), mpz(0)], [mpz(0), mpz(1)]]  # identity

            s1 = burau_sigma1(t_val, N)
            s2 = burau_sigma2(t_val, N)
            s12 = burau_multiply_mod(s1, s2, N)
            generators = [s1, s2, s12]

            for b in braid_word[:200]:  # limit length for speed
                mat = burau_multiply_mod(mat, generators[b], N)

            # Alexander polynomial evaluated at t: det(Burau - I)
            det_val = ((mat[0][0] - 1) * (mat[1][1] - 1) - mat[0][1] * mat[1][0]) % N

            if det_val != 0:
                g = gcd(det_val, N)
                if 1 < g < N:
                    results["factor_found"] += 1
                    found = True
                    break

        # Linking number analysis: count B1,B2,B3 occurrences
        if braid_word:
            counts = Counter(braid_word)
            linking = counts.get(0, 0) - counts.get(1, 0)  # exponent sum proxy
            # Check if linking number mod small primes reveals info
            for sm in [3, 5, 7, 11]:
                if linking % sm == 0:
                    g = gcd(mpz(abs(linking)), N)
                    if 1 < g < N:
                        results["factor_found"] += 1
                        break

    # Test: does Alexander polynomial at t=2 correlate with factorability?
    alex_gcd_successes = 0
    for bits, N, p, q in test_cases[:10]:
        if time.time() - t0 > max_time:
            break
        # Random braid words of increasing length
        product = mpz(1)
        for length in range(10, 300, 10):
            rng = random.Random(length)
            word = [rng.randint(0, 2) for _ in range(length)]

            mat = [[mpz(1), mpz(0)], [mpz(0), mpz(1)]]
            s1 = burau_sigma1(mpz(2), N)
            s2 = burau_sigma2(mpz(2), N)
            s12 = burau_multiply_mod(s1, s2, N)
            gens = [s1, s2, s12]

            for b in word:
                mat = burau_multiply_mod(mat, gens[b], N)

            det_val = ((mat[0][0] - 1) * (mat[1][1] - 1) - mat[0][1] * mat[1][0]) % N
            if det_val != 0:
                product = (product * det_val) % N

        g = gcd(product, N)
        if 1 < g < N:
            alex_gcd_successes += 1

    elapsed = time.time() - t0

    print(f"\n  Results ({elapsed:.1f}s):")
    print(f"    Factor found (braid walk + Burau): {results['factor_found']}/{results['total']}")
    print(f"    Alexander poly GCD method: {alex_gcd_successes}/{min(10, len(test_cases))}")

    if results["factor_found"] > results["total"] * 0.3 or alex_gcd_successes > 3:
        verdict = "PROMISING"
    else:
        verdict = "REJECTED"

    print(f"    Verdict: {verdict}")
    return verdict


# ============================================================
# FIELD 5: CODING THEORY
# ============================================================

def experiment_coding(test_cases, max_time=55):
    """
    Error-correcting code perspective on Pythagorean tree.

    The tree generates codewords (A,B,C) in (Z/NZ)^3 on the "conic code"
    (the variety A^2 + B^2 = C^2 mod N).

    Properties to measure:
    - Minimum distance: min |c_i - c_j| for distinct codewords
    - Covering radius: how well the code covers (Z/NZ)^3
    - Syndrome: for a target value, what's the closest codeword?

    If the code has good distance properties, pairwise differences
    are more likely to share factors with N.
    """
    print("\n" + "=" * 70)
    print("FIELD 5: CODING THEORY")
    print("=" * 70)

    t0 = time.time()
    results = {"factor_found": 0, "total": 0, "good_distance": 0}
    root_distance_scores = defaultdict(list)

    for bits, N, p, q in test_cases:
        if time.time() - t0 > max_time:
            break
        results["total"] += 1

        found = False

        for root_m, root_n in ROOTS[:6]:
            # Generate codewords by BFS
            num_codewords = min(300, max(50, 20000 // bits))

            codewords = []
            m, n = mpz(root_m), mpz(root_n)
            queue = [(m, n)]
            visited = set()
            visited.add((int(m), int(n)))

            while queue and len(codewords) < num_codewords:
                m, n = queue.pop(0)
                A = (m*m - n*n) % N
                B = (2*m*n) % N
                C = (m*m + n*n) % N
                codewords.append((A, B, C))

                # Direct factor check
                for v in [A, B, C]:
                    if v != 0:
                        g = gcd(v, N)
                        if 1 < g < N:
                            results["factor_found"] += 1
                            found = True
                            break
                if found:
                    break

                for bfn in BERGGREN:
                    cm, cn = bfn(m, n)
                    if cm > 0 and cn > 0 and cm > cn:
                        key = (int(cm) % (1 << 25), int(cn) % (1 << 25))
                        if key not in visited:
                            visited.add(key)
                            queue.append((cm, cn))

            if found:
                break

            # Compute "distance" between codewords: gcd of differences
            # This is the coding-theory approach to multi-GCD
            product = mpz(1)
            gcd_checks = 0
            for i in range(min(len(codewords), 100)):
                for j in range(i+1, min(len(codewords), 100)):
                    dA = (codewords[i][0] - codewords[j][0]) % N
                    if dA != 0:
                        product = (product * dA) % N
                        gcd_checks += 1
                        if gcd_checks % 100 == 0:
                            g = gcd(product, N)
                            if 1 < g < N:
                                results["factor_found"] += 1
                                found = True
                                break
                            product = mpz(1)
                if found:
                    break

            if found:
                break

            # Minimum distance estimation (sample-based)
            if len(codewords) >= 10:
                min_dist = N
                sample_size = min(50, len(codewords))
                for i in range(sample_size):
                    for j in range(i+1, sample_size):
                        d = abs(codewords[i][0] - codewords[j][0])
                        if 0 < d < min_dist:
                            min_dist = d

                # Compare to expected minimum distance for random code
                # Random: ~ N / num_codewords^2
                expected_random = int(N) // (sample_size * sample_size) if sample_size > 0 else int(N)
                ratio = float(min_dist) / max(1, expected_random)
                root_distance_scores[(root_m, root_n)].append(ratio)

                if ratio > 2.0:
                    results["good_distance"] += 1

    # Syndrome decoding experiment: for each small prime s,
    # compute "syndrome" = sum of codewords mod s, check if it reveals factor
    syndrome_successes = 0
    for bits, N, p, q in test_cases[:10]:
        if time.time() - t0 > max_time:
            break
        m, n = mpz(2), mpz(1)
        syndrome_product = mpz(1)
        for step in range(500):
            A = (m*m - n*n) % N
            # Syndrome: A mod small prime, accumulated
            for s in [3, 7, 11, 13, 17, 19, 23]:
                residue = A % s
                if residue != 0:
                    syndrome_product = (syndrome_product * mpz(residue)) % N

            if step % 50 == 49:
                g = gcd(syndrome_product, N)
                if 1 < g < N:
                    syndrome_successes += 1
                    break
                syndrome_product = mpz(1)

            bfn = BERGGREN[step % 3]
            cm, cn = bfn(m, n)
            m, n = cm % N, cn % N
            if m == 0 and n == 0:
                break

    elapsed = time.time() - t0

    print(f"\n  Results ({elapsed:.1f}s):")
    print(f"    Factor found (code distance): {results['factor_found']}/{results['total']}")
    print(f"    Good distance (> 2x random): {results['good_distance']}/{results['total']}")
    print(f"    Syndrome decoding method: {syndrome_successes}/{min(10, len(test_cases))}")

    if root_distance_scores:
        print(f"\n    Root distance ratios (tree vs random code):")
        for root in ROOTS[:6]:
            scores = root_distance_scores.get(root, [])
            if scores:
                avg = sum(scores) / len(scores)
                print(f"      ({root[0]},{root[1]}): avg ratio = {avg:.2f}")

    if results["factor_found"] > results["total"] * 0.3 or syndrome_successes > 3:
        verdict = "PROMISING"
    elif results["good_distance"] > results["total"] * 0.5:
        verdict = "PROMISING (structural advantage)"
    else:
        verdict = "REJECTED"

    print(f"    Verdict: {verdict}")
    return verdict


# ============================================================
# DIFFERENT ROOTS EXPERIMENT (standalone)
# ============================================================

def experiment_roots(test_cases, max_time=55):
    """
    Compare factoring success across different tree roots.

    Standard root (2,1) gives the full primitive triple tree.
    Other roots start from different positions and may reach
    factor-revealing nodes faster.

    For each root, we do a BFS and random walk, counting
    how quickly we find factors.
    """
    print("\n" + "=" * 70)
    print("DIFFERENT ROOTS COMPARISON")
    print("=" * 70)

    t0 = time.time()

    # Extended roots list
    all_roots = ROOTS + [
        (9, 2),   # (77,36,85)
        (10, 1),  # (99,20,101)
        (10, 3),  # (91,60,109)
        (11, 4),  # (105,88,137)
    ]

    root_stats = {}
    for root in all_roots:
        root_stats[root] = {"successes": 0, "total_steps": 0, "attempts": 0}

    for bits, N, p, q in test_cases:
        if time.time() - t0 > max_time:
            break

        for root_m, root_n in all_roots:
            if time.time() - t0 > max_time:
                break

            root_stats[(root_m, root_n)]["attempts"] += 1
            m, n = mpz(root_m), mpz(root_n)

            walk_len = min(500, max(100, 30000 // bits))

            # Method 1: Deterministic BFS (limited)
            queue = [(m, n, 0)]
            visited = set()
            found = False

            for _ in range(walk_len):
                if not queue:
                    break
                m, n, depth = queue.pop(0)

                key = (int(m) % (1 << 25), int(n) % (1 << 25))
                if key in visited:
                    continue
                visited.add(key)

                g = check_factor_mn(N, m, n)
                if g:
                    root_stats[(root_m, root_n)]["successes"] += 1
                    root_stats[(root_m, root_n)]["total_steps"] += depth
                    found = True
                    break

                for bfn in BERGGREN:
                    cm, cn = bfn(m, n)
                    if cm > 0 and cn > 0 and cm > cn:
                        queue.append((cm, cn, depth + 1))

            # Method 2: Product-GCD walk mod N
            if not found:
                m, n = mpz(root_m) % N, mpz(root_n) % N
                product = mpz(1)
                for step in range(walk_len):
                    A = (m*m - n*n) % N
                    if A != 0:
                        product = (product * A) % N
                    if step % 40 == 39:
                        g = gcd(product, N)
                        if 1 < g < N:
                            root_stats[(root_m, root_n)]["successes"] += 1
                            root_stats[(root_m, root_n)]["total_steps"] += step
                            found = True
                            break
                        product = mpz(1)

                    bfn = BERGGREN[step % 3]
                    cm, cn = bfn(m, n)
                    m, n = cm % N, cn % N
                    if m == 0 and n == 0:
                        break

    elapsed = time.time() - t0

    print(f"\n  Results ({elapsed:.1f}s):")
    print(f"  {'Root':<10} {'Success':>8} {'Attempts':>9} {'Rate':>7} {'Avg Steps':>10}")
    print(f"  {'-'*48}")

    sorted_roots = sorted(root_stats.items(),
                          key=lambda x: x[1]["successes"] / max(1, x[1]["attempts"]),
                          reverse=True)

    for root, stats in sorted_roots:
        rate = stats["successes"] / max(1, stats["attempts"])
        avg_steps = stats["total_steps"] / max(1, stats["successes"])
        print(f"  ({root[0]},{root[1]}){'':<5} {stats['successes']:>8} {stats['attempts']:>9}"
              f" {rate:>6.1%} {avg_steps:>10.1f}" if stats["successes"] else
              f"  ({root[0]},{root[1]}){'':<5} {stats['successes']:>8} {stats['attempts']:>9}"
              f" {rate:>6.1%} {'N/A':>10}")

    # Determine if any non-standard root beats (2,1)
    std_rate = root_stats[(2,1)]["successes"] / max(1, root_stats[(2,1)]["attempts"])
    best_alt = None
    best_alt_rate = 0
    for root, stats in root_stats.items():
        if root == (2, 1):
            continue
        rate = stats["successes"] / max(1, stats["attempts"])
        if rate > best_alt_rate:
            best_alt_rate = rate
            best_alt = root

    print(f"\n    Standard root (2,1) success rate: {std_rate:.1%}")
    if best_alt:
        print(f"    Best alternative root {best_alt}: {best_alt_rate:.1%}")
        if best_alt_rate > std_rate * 1.1:
            verdict = f"CONFIRMED — root {best_alt} beats standard by {best_alt_rate/max(0.001,std_rate):.1f}x"
        elif best_alt_rate > std_rate * 0.9:
            verdict = "REJECTED — no significant advantage from alternative roots"
        else:
            verdict = "REJECTED — standard root (2,1) is best or tied"
    else:
        verdict = "REJECTED — no alternative roots tested"

    print(f"    Verdict: {verdict}")
    return verdict


# ============================================================
# MAIN
# ============================================================

def main():
    print("Pythagorean Tree Factoring -- Cross-Mathematical Field Experiments")
    print("=" * 70)

    rng = random.Random(2026_03_15)

    # Generate test semiprimes: 20b to 48b
    test_cases = []
    bit_sizes = [20, 24, 28, 32, 36, 40, 44, 48]
    cases_per_size = 5

    print("\nGenerating test semiprimes...")
    for bits in bit_sizes:
        for i in range(cases_per_size):
            N, p, q = gen_semiprime(bits, rng)
            test_cases.append((bits, N, p, q))
            if i == 0:
                print(f"  {bits}b: e.g. N={N} = {p} * {q}")

    print(f"\nTotal test cases: {len(test_cases)}")
    print(f"Bit range: {bit_sizes[0]}b to {bit_sizes[-1]}b")
    print(f"Roots to test: {ROOTS}")

    # Run all experiments
    verdicts = {}

    t_total = time.time()

    verdicts["Tropical Geometry"] = experiment_tropical(test_cases)
    verdicts["P-adic Numbers"] = experiment_padic(test_cases)
    verdicts["Ergodic Theory"] = experiment_ergodic(test_cases)
    verdicts["Knot Theory"] = experiment_knot(test_cases)
    verdicts["Coding Theory"] = experiment_coding(test_cases)
    verdicts["Alternative Roots"] = experiment_roots(test_cases)

    total_time = time.time() - t_total

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\n  Total time: {total_time:.1f}s\n")
    print(f"  {'Field':<25} {'Verdict'}")
    print(f"  {'-'*60}")
    for field, verdict in verdicts.items():
        print(f"  {field:<25} {verdict}")

    promising = sum(1 for v in verdicts.values() if "PROMISING" in v or "CONFIRMED" in v)
    rejected = sum(1 for v in verdicts.values() if "REJECTED" in v)
    print(f"\n  Promising: {promising}/{len(verdicts)}")
    print(f"  Rejected:  {rejected}/{len(verdicts)}")

    if promising > 0:
        print("\n  Next steps: Scale promising methods to 64b+ semiprimes.")
    else:
        print("\n  No field showed clear advantage. The Berggren tree structure")
        print("  does not appear to encode factor information via these invariants.")


if __name__ == "__main__":
    main()
