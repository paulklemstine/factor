#!/usr/bin/env python3
"""
10 Genuinely New Pythagorean Triple Tree Experiments
=====================================================
Fields 141-150: angles NOT covered in prior 140 fields.
Each experiment: 3-line hypothesis, <40 lines code, <15s, <1GB RAM.
"""

import math, time, random, sys
from collections import Counter, defaultdict

# --- Berggren matrices on (m,n) generators ---
def B1(m, n): return (2*m - n, m)
def B2(m, n): return (2*m + n, m)
def B3(m, n): return (m + 2*n, n)

def triple(m, n):
    """Primitive Pythagorean triple from coprime (m,n), m>n>0, m-n odd."""
    return (m*m - n*n, 2*m*n, m*m + n*n)

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def is_smooth(n, B):
    """Check if |n| is B-smooth."""
    n = abs(n)
    if n == 0: return False
    for p in range(2, B+1):
        while n % p == 0:
            n //= p
    return n == 1

RESULTS = {}

# ============================================================
# FIELD 141: Pythagorean Triple DENSITY
# ============================================================
# Hypothesis: The number of primitive triples with c<X is ~X/(2*pi).
# For N=pq, does counting triples with c<N vs c<p,c<q reveal structure?
# If count(c<N)/N differs from 1/(2*pi), factors may affect density.

def experiment_141_density():
    t0 = time.time()
    # Count primitive triples with c <= X for various X
    # Generate tree BFS up to depth limit, count by hypotenuse
    max_depth = 18
    counts_by_c = Counter()
    stack = [(2, 1, 0)]  # (m, n, depth)
    total = 0
    while stack:
        m, n, d = stack.pop()
        a, b, c = triple(m, n)
        if c > 10**7:
            continue
        counts_by_c[c] = 1
        total += 1
        if d < max_depth:
            stack.append((*B1(m, n), d+1))
            stack.append((*B2(m, n), d+1))
            stack.append((*B3(m, n), d+1))

    # Check density at various X thresholds
    thresholds = [10**k for k in range(2, 8)]
    density_results = []
    cumulative = 0
    sorted_cs = sorted(counts_by_c.keys())
    idx = 0
    for X in thresholds:
        while idx < len(sorted_cs) and sorted_cs[idx] <= X:
            cumulative += 1
            idx += 1
        predicted = X / (2 * math.pi)
        ratio = cumulative / predicted if predicted > 0 else 0
        density_results.append((X, cumulative, predicted, ratio))

    # Now test: for N=p*q, does density(N) - density(p)*density(q) reveal info?
    p, q = 1009, 1013
    N = p * q
    # Count triples with c <= N, c <= p, c <= q from our data
    cnt_N = sum(1 for c in sorted_cs if c <= N)
    cnt_p = sum(1 for c in sorted_cs if c <= p)
    cnt_q = sum(1 for c in sorted_cs if c <= q)

    elapsed = time.time() - t0
    RESULTS[141] = {
        'name': 'Pythagorean Triple Density',
        'density_table': density_results,
        'ratio_at_1M': density_results[-2][3] if len(density_results) >= 2 else None,
        'composite_test': f'cnt(N={N})={cnt_N}, cnt(p={p})={cnt_p}, cnt(q={q})={cnt_q}, product={cnt_p*cnt_q}',
        'elapsed': elapsed
    }
    print(f"[141] Density: ratio actual/predicted at thresholds: {[(X, f'{r:.4f}') for X, _, _, r in density_results]}")
    print(f"  Composite: cnt(N)={cnt_N}, cnt(p)*cnt(q)={cnt_p*cnt_q}")
    print(f"  Time: {elapsed:.2f}s")
    return density_results

# ============================================================
# FIELD 142: Tree HEIGHT Statistics
# ============================================================
# Hypothesis: Triples deeper in the tree have smoother components.
# The tree inverse (path from root) gives depth. Deeper = more matrix
# multiplications = more algebraic structure = smoother a,b?

def tree_inverse(m, n):
    """Find path from root (2,1) to (m,n) by inverting Berggren matrices."""
    path = []
    while (m, n) != (2, 1):
        if m <= 0 or n <= 0 or (m == 1 and n == 1):
            return None  # Not in tree
        # Invert: B1^{-1}: (m,n) -> (n, 2n-m); B2^{-1}: (m,n) -> (n, 2n+m) -- wrong
        # Actually: B1(m,n)=(2m-n,m), so B1^{-1}(a,b) = (b, 2b-a)
        # B2(m,n)=(2m+n,m), so B2^{-1}(a,b) = (b, a-2b)  (needs a>2b)
        # B3(m,n)=(m+2n,n), so B3^{-1}(a,b) = (a-2b, b)  (needs a>2b)
        if n > 0 and 2*n - m > 0 and 2*n - m < n:
            # B1 inverse: parent = (n, 2n-m)
            path.append('B1')
            m, n = n, 2*n - m
        elif m > 2*n and n > 0:
            # Could be B2 or B3 inverse
            if m - 2*n > 0 and m - 2*n < n:
                # B2^{-1}: (n, m-2n)  [need m-2n < n, i.e., m < 3n]
                path.append('B2')
                m, n = n, m - 2*n
            else:
                # B3^{-1}: (m-2n, n)
                path.append('B3')
                m, n = m - 2*n, n
        elif m > n and 2*n > m:
            # B1 inverse candidate
            path.append('B1')
            m, n = n, 2*n - m
        else:
            return None
        if len(path) > 100:
            return None
    return list(reversed(path))

def experiment_142_height():
    t0 = time.time()
    # Generate triples at various depths, check smoothness of A=m^2-n^2
    B_smooth = 1000
    depth_smooth = defaultdict(lambda: [0, 0])  # depth -> [smooth_count, total]
    stack = [(2, 1, 0)]
    while stack:
        m, n, d = stack.pop()
        if d > 14:
            continue
        a, b, c = triple(m, n)
        if c > 10**8:
            continue
        sm = is_smooth(a, B_smooth)
        depth_smooth[d][1] += 1
        if sm:
            depth_smooth[d][0] += 1
        if d < 14:
            stack.append((*B1(m, n), d+1))
            stack.append((*B2(m, n), d+1))
            stack.append((*B3(m, n), d+1))

    elapsed = time.time() - t0
    table = []
    for d in sorted(depth_smooth.keys()):
        s, t = depth_smooth[d]
        rate = s/t if t > 0 else 0
        table.append((d, s, t, rate))

    RESULTS[142] = {
        'name': 'Tree Height Statistics',
        'table': table,
        'elapsed': elapsed
    }
    print(f"[142] Height vs Smoothness (B={B_smooth}):")
    for d, s, t, r in table:
        print(f"  depth {d:2d}: {s:5d}/{t:5d} = {r:.4f}")
    print(f"  Time: {elapsed:.2f}s")
    return table

# ============================================================
# FIELD 143: Sibling Relations
# ============================================================
# Hypothesis: Triples sharing a parent (siblings via B1,B2,B3) have
# algebraic relations. Specifically, gcd(a1*a2 - a3^2, N) or similar
# cross-sibling expressions might factor N.

def experiment_143_siblings():
    t0 = time.time()
    # For a composite N, generate siblings and check cross-relations
    primes_16b = [p for p in range(2**15, 2**15+200) if all(p%i for i in range(2, int(p**0.5)+1))]
    p, q = primes_16b[0], primes_16b[1]
    N = p * q

    found = 0
    tested = 0
    factor_methods = Counter()

    stack = [(2, 1, 0)]
    while stack and tested < 50000:
        m, n, d = stack.pop()
        if d > 12:
            continue
        # Generate 3 siblings
        m1, n1 = B1(m, n)
        m2, n2 = B2(m, n)
        m3, n3 = B3(m, n)
        a1 = m1*m1 - n1*n1
        a2 = m2*m2 - n2*n2
        a3 = m3*m3 - n3*n3
        b1, b2, b3 = 2*m1*n1, 2*m2*n2, 2*m3*n3

        # Test various cross-sibling expressions
        exprs = {
            'a1*a2-a3^2': a1*a2 - a3*a3,
            'a1+a2-a3': a1+a2-a3,
            'b1*b2-b3^2': b1*b2 - b3*b3,
            'a1*b2-a2*b1': a1*b2 - a2*b1,
            '(a1-a2)*(a2-a3)': (a1-a2)*(a2-a3),
        }
        for name, val in exprs.items():
            if val != 0:
                g = gcd(abs(val) % N, N) if N > 0 else 0
                tested += 1
                if 1 < g < N:
                    found += 1
                    factor_methods[name] += 1

        if d < 12:
            stack.append((*B1(m, n), d+1))
            stack.append((*B2(m, n), d+1))
            stack.append((*B3(m, n), d+1))

    elapsed = time.time() - t0
    RESULTS[143] = {
        'name': 'Sibling Relations',
        'N': N, 'p': p, 'q': q,
        'tested': tested, 'found': found,
        'methods': dict(factor_methods),
        'elapsed': elapsed
    }
    print(f"[143] Siblings: {found}/{tested} cross-sibling GCDs found factor of N={N}")
    if factor_methods:
        print(f"  Methods: {dict(factor_methods)}")
    print(f"  Time: {elapsed:.2f}s")
    return found

# ============================================================
# FIELD 144: Tree INVERSE Problem
# ============================================================
# Hypothesis: The path encoding (sequence of B1/B2/B3) from root to a
# triple contains structure related to factor of c. Specifically,
# path(c mod p) vs path(c mod q) should differ in computable ways.

def experiment_144_inverse():
    t0 = time.time()
    # Generate triples, find their paths, analyze path statistics
    path_stats = defaultdict(list)
    stack = [(2, 1, 0, '')]
    count = 0
    b1_frac_by_depth = defaultdict(list)
    b2_frac_by_depth = defaultdict(list)
    b3_frac_by_depth = defaultdict(list)

    while stack and count < 5000:
        m, n, d, path = stack.pop()
        if d > 10:
            continue
        a, b, c = triple(m, n)
        count += 1
        if d > 0:
            b1c = path.count('1')
            b2c = path.count('2')
            b3c = path.count('3')
            total = b1c + b2c + b3c
            # Does path composition correlate with smoothness?
            sm = is_smooth(a, 500)
            if sm:
                path_stats['smooth_b1'].append(b1c/total)
                path_stats['smooth_b2'].append(b2c/total)
            else:
                path_stats['nonsmooth_b1'].append(b1c/total)
                path_stats['nonsmooth_b2'].append(b2c/total)

        if d < 10:
            stack.append((*B1(m, n), d+1, path+'1'))
            stack.append((*B2(m, n), d+1, path+'2'))
            stack.append((*B3(m, n), d+1, path+'3'))

    # Compare path composition for smooth vs non-smooth
    results = {}
    for key in ['smooth_b1', 'smooth_b2', 'nonsmooth_b1', 'nonsmooth_b2']:
        vals = path_stats[key]
        results[key] = sum(vals)/len(vals) if vals else 0

    elapsed = time.time() - t0
    RESULTS[144] = {
        'name': 'Tree Inverse Problem',
        'smooth_b1_frac': results.get('smooth_b1', 0),
        'smooth_b2_frac': results.get('smooth_b2', 0),
        'nonsmooth_b1_frac': results.get('nonsmooth_b1', 0),
        'nonsmooth_b2_frac': results.get('nonsmooth_b2', 0),
        'n_smooth': len(path_stats.get('smooth_b1', [])),
        'n_nonsmooth': len(path_stats.get('nonsmooth_b1', [])),
        'elapsed': elapsed
    }
    print(f"[144] Tree Inverse: path composition for smooth vs nonsmooth A-values:")
    print(f"  Smooth   (n={results.get('smooth_b1',0):.0f}?): B1={results['smooth_b1']:.4f}, B2={results['smooth_b2']:.4f}")
    print(f"  Nonsmooth: B1={results['nonsmooth_b1']:.4f}, B2={results['nonsmooth_b2']:.4f}")
    print(f"  Time: {elapsed:.2f}s")

# ============================================================
# FIELD 145: Pythagorean ANGLES
# ============================================================
# Hypothesis: The angle theta = arctan(b/a) = arctan(2mn/(m^2-n^2))
# for tree triples. Mod p, these angles (as ratios b/a mod p) may
# cluster, revealing factor information via angular distribution.

def experiment_145_angles():
    t0 = time.time()
    p, q = 251, 257
    N = p * q

    # Collect angles (as b*a^{-1} mod N, mod p, mod q)
    angles_mod_p = []
    angles_mod_q = []
    angles_mod_N = []
    stack = [(2, 1, 0)]
    count = 0
    while stack and count < 20000:
        m, n, d = stack.pop()
        if d > 12:
            continue
        a, b, c = triple(m, n)
        count += 1
        # angle = b/a mod p (if a invertible)
        a_p = a % p
        if a_p != 0:
            # b * a^{-1} mod p
            angles_mod_p.append((b * pow(a_p, p-2, p)) % p)
        a_q = a % q
        if a_q != 0:
            angles_mod_q.append((b * pow(a_q, q-2, q)) % q)

        if d < 12:
            stack.append((*B1(m, n), d+1))
            stack.append((*B2(m, n), d+1))
            stack.append((*B3(m, n), d+1))

    # Check uniformity: chi-squared test
    def chi_sq(angles, mod):
        freq = Counter(angles)
        expected = len(angles) / mod
        return sum((freq.get(i, 0) - expected)**2 / expected for i in range(mod))

    chi_p = chi_sq(angles_mod_p, p)
    chi_q = chi_sq(angles_mod_q, q)
    # Under H0 (uniform), chi^2 ~ p-1 or q-1
    ratio_p = chi_p / (p - 1)
    ratio_q = chi_q / (q - 1)

    # Check for repeated angles (collisions)
    coll_p = sum(1 for v in Counter(angles_mod_p).values() if v > 1)
    coll_q = sum(1 for v in Counter(angles_mod_q).values() if v > 1)

    elapsed = time.time() - t0
    RESULTS[145] = {
        'name': 'Pythagorean Angles',
        'chi_p': chi_p, 'chi_q': chi_q,
        'ratio_p': ratio_p, 'ratio_q': ratio_q,
        'collisions_p': coll_p, 'collisions_q': coll_q,
        'n_angles': count,
        'elapsed': elapsed
    }
    print(f"[145] Angles: chi^2/df: mod p={ratio_p:.3f}, mod q={ratio_q:.3f}")
    print(f"  Collisions: mod p={coll_p}/{p}, mod q={coll_q}/{q}")
    print(f"  (ratio ~1 = uniform, >>1 = clustered)")
    print(f"  Time: {elapsed:.2f}s")

# ============================================================
# FIELD 146: Tree Automorphisms
# ============================================================
# Hypothesis: The tree has symmetries beyond just B1/B2/B3.
# Specifically: does swapping (a,b) in a triple (swapping m,n roles)
# create another tree element? Do tree-level symmetries preserve
# smoothness or factor-related properties?

def experiment_146_automorphisms():
    t0 = time.time()
    # Check: for each triple (a,b,c) in the tree, is (b,a,c) also in the tree?
    # Also check: (m,n) -> (n,m) -- does this give a valid tree element?
    tree_triples = set()
    tree_mn = {}
    stack = [(2, 1, 0)]
    while stack:
        m, n, d = stack.pop()
        if d > 10:
            continue
        a, b, c = triple(m, n)
        tree_triples.add((min(a,b), max(a,b), c))
        tree_mn[(m, n)] = d
        if d < 10:
            stack.append((*B1(m, n), d+1))
            stack.append((*B2(m, n), d+1))
            stack.append((*B3(m, n), d+1))

    # Check swap symmetry
    swap_in_tree = 0
    swap_total = 0
    for (m, n), d in list(tree_mn.items()):
        if n > 0 and m > n and (m - n) % 2 == 1 and gcd(m, n) == 1:
            swap_total += 1
            # (m,n) gives (m^2-n^2, 2mn, m^2+n^2)
            # Swapped triple would need m', n' such that m'^2-n'^2 = 2mn and 2m'n' = m^2-n^2
            # This requires solving: is (2mn, m^2-n^2, m^2+n^2) primitive? Yes, same c.
            # But is it in the tree? Check (min, max, c).
            a, b, c = triple(m, n)
            swapped = (min(b, a), max(b, a), c)
            if swapped in tree_triples:
                swap_in_tree += 1

    # Check negation symmetry: B1 and B3 relationship
    # B1(m,n)=(2m-n,m), B3(m,n)=(m+2n,n)
    # Are B1 and B3 conjugate under some automorphism?
    b1_vals = set()
    b3_vals = set()
    for (m, n) in list(tree_mn.keys())[:500]:
        a1 = B1(m,n)[0]**2 - B1(m,n)[1]**2
        a3 = B3(m,n)[0]**2 - B3(m,n)[1]**2
        b1_vals.add(a1)
        b3_vals.add(a3)
    overlap = len(b1_vals & b3_vals)

    elapsed = time.time() - t0
    RESULTS[146] = {
        'name': 'Tree Automorphisms',
        'swap_in_tree': swap_in_tree, 'swap_total': swap_total,
        'swap_rate': swap_in_tree/swap_total if swap_total else 0,
        'b1_b3_overlap': overlap,
        'b1_size': len(b1_vals), 'b3_size': len(b3_vals),
        'elapsed': elapsed
    }
    print(f"[146] Automorphisms: swap(a,b) in tree: {swap_in_tree}/{swap_total} = {swap_in_tree/swap_total if swap_total else 0:.4f}")
    print(f"  B1 A-values ∩ B3 A-values: {overlap} / {len(b1_vals)}")
    print(f"  Time: {elapsed:.2f}s")

# ============================================================
# FIELD 147: Generating Function
# ============================================================
# Hypothesis: The Dirichlet series F(s) = sum_{(a,b,c) primitive} c^{-s}
# has an Euler product related to L(s, chi_4). The residue or special
# values may encode factoring information.

def experiment_147_generating():
    t0 = time.time()
    # Compute partial sums of c^{-s} for s=1, 1.5, 2
    # Compare to known formula: sum = product over p≡1(4) of (1 - p^{-s})^{-1} * ...
    hypotenuses = []
    stack = [(2, 1, 0)]
    while stack:
        m, n, d = stack.pop()
        if d > 16:
            continue
        a, b, c = triple(m, n)
        if c < 10**6:
            hypotenuses.append(c)
        if d < 16:
            stack.append((*B1(m, n), d+1))
            stack.append((*B2(m, n), d+1))
            stack.append((*B3(m, n), d+1))

    hypotenuses.sort()
    # Dirichlet series partial sums
    for s in [1.0, 1.5, 2.0]:
        partial = sum(c**(-s) for c in hypotenuses)
        print(f"  F({s}) partial sum ({len(hypotenuses)} terms, c<10^6) = {partial:.6f}")

    # Check: do hypotenuses factor into primes ≡ 1 mod 4?
    p1mod4 = 0
    p3mod4 = 0
    for c in hypotenuses[:1000]:
        temp = c
        for pp in range(2, min(1000, temp+1)):
            while temp % pp == 0:
                if pp % 4 == 1:
                    p1mod4 += 1
                elif pp % 4 == 3:
                    p3mod4 += 1
                temp //= pp
            if temp == 1:
                break

    elapsed = time.time() - t0
    RESULTS[147] = {
        'name': 'Generating Function',
        'n_hypotenuses': len(hypotenuses),
        'p1mod4_factors': p1mod4, 'p3mod4_factors': p3mod4,
        'ratio_1mod4': p1mod4/(p1mod4+p3mod4) if (p1mod4+p3mod4) else 0,
        'elapsed': elapsed
    }
    print(f"[147] Generating function: hypotenuse prime factors: {p1mod4} ≡1(4), {p3mod4} ≡3(4)")
    print(f"  Ratio 1mod4: {p1mod4/(p1mod4+p3mod4) if (p1mod4+p3mod4) else 0:.4f} (expect ~1.0)")
    print(f"  Time: {elapsed:.2f}s")

# ============================================================
# FIELD 148: Pythagorean PRIMES (sum of two squares)
# ============================================================
# Hypothesis: Primes p ≡ 1 mod 4 have unique representation p=a^2+b^2.
# The tree navigates these representations. For N=pq, the tree
# representations of N (via Brahmagupta identity) might factor N.

def experiment_148_pyth_primes():
    t0 = time.time()
    # For primes p ≡ 1 mod 4, find the sum-of-two-squares representation
    # using Cornacchia/Fermat descent, then check if tree gives it
    def sum_two_squares(p):
        """Find a,b with a^2+b^2=p for prime p≡1(4)."""
        # Tonelli-Shanks for sqrt(-1) mod p
        r = pow(2, (p-1)//4, p)  # works if p ≡ 1 mod 4
        if (r*r) % p != p-1:
            # Try other bases
            for g in range(3, 100):
                r = pow(g, (p-1)//4, p)
                if (r*r) % p == p-1:
                    break
            else:
                return None
        # Fermat descent
        a, b = p, r
        limit = int(p**0.5)
        while b > limit:
            a, b = b, a % b
        return (b, int((p - b*b)**0.5))

    # Test: for N=p*q (both ≡ 1 mod 4), Brahmagupta gives two reps
    # N = (a1*a2 - b1*b2)^2 + (a1*b2 + a2*b1)^2
    # N = (a1*a2 + b1*b2)^2 + (a1*b2 - a2*b1)^2
    # GCD of the two A-values might give factor

    primes_1mod4 = []
    for pp in range(5, 5000):
        if pp % 4 == 1 and all(pp % i for i in range(2, int(pp**0.5)+1)):
            primes_1mod4.append(pp)
        if len(primes_1mod4) >= 100:
            break

    factored = 0
    tested = 0
    for i in range(50):
        p = primes_1mod4[2*i]
        q = primes_1mod4[2*i+1]
        N = p * q
        s_p = sum_two_squares(p)
        s_q = sum_two_squares(q)
        if s_p is None or s_q is None:
            continue
        a1, b1 = s_p
        a2, b2 = s_q
        # Two representations of N
        A1 = abs(a1*a2 - b1*b2)
        B1v = abs(a1*b2 + a2*b1)
        A2 = abs(a1*a2 + b1*b2)
        B2v = abs(a1*b2 - a2*b1)
        # GCD test
        tested += 1
        g1 = gcd(A1, A2)
        g2 = gcd(B1v, B2v)
        g3 = gcd(A1, B2v)
        g4 = gcd(A2, B1v)
        for g in [g1, g2, g3, g4]:
            gg = gcd(g, N)
            if 1 < gg < N:
                factored += 1
                break

    elapsed = time.time() - t0
    RESULTS[148] = {
        'name': 'Pythagorean Primes (sum of squares)',
        'factored': factored, 'tested': tested,
        'rate': factored/tested if tested else 0,
        'elapsed': elapsed
    }
    print(f"[148] Pyth Primes: {factored}/{tested} factored via two-representation GCD")
    print(f"  NOTE: This is the Brahmagupta-Fibonacci identity method")
    print(f"  Time: {elapsed:.2f}s")

# ============================================================
# FIELD 149: Cross-tree Correlations
# ============================================================
# Hypothesis: Values from B1 subtree, B2 subtree, B3 subtree have
# algebraic relations. Specifically: B1 gives APs (parabolic),
# B2 gives exponential growth, B3 gives APs. Cross-products
# B1_value * B3_value - B2_value^2 might have special structure.

def experiment_149_cross_tree():
    t0 = time.time()
    p, q = 10007, 10009
    N = p * q

    # Generate pure B1, B2, B3 paths from root
    def pure_path(op, depth):
        m, n = 2, 1
        vals = []
        for _ in range(depth):
            m, n = op(m, n)
            a = m*m - n*n
            vals.append((m, n, a))
        return vals

    b1_path = pure_path(B1, 30)
    b2_path = pure_path(B2, 30)
    b3_path = pure_path(B3, 30)

    # Cross correlations: a1[k]*a3[k] - a2[k]^2
    found = 0
    tested = 0
    for k in range(min(len(b1_path), len(b2_path), len(b3_path))):
        a1 = b1_path[k][2]
        a2 = b2_path[k][2]
        a3 = b3_path[k][2]
        cross = a1 * a3 - a2 * a2
        if cross != 0:
            g = gcd(abs(cross) % N, N)
            tested += 1
            if 1 < g < N:
                found += 1
        # Also try m-values
        m1 = b1_path[k][0]
        m2 = b2_path[k][0]
        m3 = b3_path[k][0]
        cross_m = m1 * m3 - m2 * m2
        if cross_m != 0:
            g = gcd(abs(cross_m) % N, N)
            tested += 1
            if 1 < g < N:
                found += 1

    # Also try: product of B1 and B3 values modulo N
    b1_prod = 1
    b3_prod = 1
    for k in range(20):
        b1_prod = (b1_prod * b1_path[k][2]) % N
        b3_prod = (b3_prod * b3_path[k][2]) % N
        g = gcd(abs(b1_prod - b3_prod), N)
        tested += 1
        if 1 < g < N:
            found += 1

    elapsed = time.time() - t0
    RESULTS[149] = {
        'name': 'Cross-tree Correlations',
        'found': found, 'tested': tested,
        'N': N,
        'elapsed': elapsed
    }
    print(f"[149] Cross-tree: {found}/{tested} cross-products found factor of N={N}")
    print(f"  Time: {elapsed:.2f}s")

# ============================================================
# FIELD 150: Tree mod Composite (CRT orbit)
# ============================================================
# Hypothesis: Walking the tree mod N=pq, the orbit has CRT structure:
# orbit(N) = orbit(p) x orbit(q). If we detect orbit SIZE mod N,
# it factors as lcm(size_p, size_q). Can we detect orbit collisions
# that reveal one orbit size without knowing p?

def experiment_150_tree_mod_composite():
    t0 = time.time()
    # Use Floyd cycle detection on tree walk mod N
    p, q = 1009, 1013
    N = p * q

    # Walk using B2 (hyperbolic, has interesting period structure)
    def walk_b2_mod(N, max_steps=100000):
        m, n = 2, 1
        tortoise_m, tortoise_n = 2, 1
        for step in range(1, max_steps):
            # Hare: 2 steps
            m, n = (2*m + n) % N, m % N
            m, n = (2*m + n) % N, m % N
            # Tortoise: 1 step
            tortoise_m, tortoise_n = (2*tortoise_m + tortoise_n) % N, tortoise_m % N
            if m == tortoise_m and n == tortoise_n and step > 1:
                return step
        return None

    period_N = walk_b2_mod(N)
    period_p = walk_b2_mod(p, 50000)
    period_q = walk_b2_mod(q, 50000)

    # Can we extract factor from period_N?
    factor_found = False
    if period_N:
        # period_N should = lcm(period_p, period_q)
        # Try: gcd(B2^k - I, N) for k = divisors of period_N
        m, n = 2, 1
        for k in range(1, min(period_N + 1, 5000)):
            m, n = (2*m + n) % N, m % N
            if m == 2 and n == 1:
                # Found period k mod N
                # Now check: does k have a factor that is period mod p or q?
                for d in range(1, int(k**0.5)+1):
                    if k % d == 0:
                        for dd in [d, k//d]:
                            # Check if B2^dd = I mod something
                            mm, nn = 2 % p, 1 % p
                            for _ in range(dd):
                                mm, nn = (2*mm + nn) % p, mm % p
                            if mm == 2 % p and nn == 1 % p:
                                factor_found = True
                break

    # Alternative: birthday attack on B2 walk mod N
    birthday_found = 0
    seen = {}
    m, n = 2, 1
    for step in range(10000):
        m, n = (2*m + n) % N, m % N
        key = (m, n)
        if key in seen:
            cycle_len = step - seen[key]
            g = gcd(cycle_len, N)
            if 1 < g < N:
                birthday_found += 1
            break
        seen[key] = step

    elapsed = time.time() - t0
    RESULTS[150] = {
        'name': 'Tree mod Composite (CRT orbit)',
        'period_N': period_N, 'period_p': period_p, 'period_q': period_q,
        'factor_from_period': factor_found,
        'birthday_found': birthday_found,
        'elapsed': elapsed
    }
    lcm_pq = None
    if period_p and period_q:
        lcm_pq = period_p * period_q // gcd(period_p, period_q)
    print(f"[150] Tree mod composite:")
    print(f"  period(N={N}) = {period_N}")
    print(f"  period(p={p}) = {period_p}, period(q={q}) = {period_q}, lcm = {lcm_pq}")
    print(f"  Match: {period_N == lcm_pq if (period_N and lcm_pq) else 'N/A'}")
    print(f"  Factor from period divisors: {factor_found}")
    print(f"  Birthday collision: {birthday_found}")
    print(f"  Time: {elapsed:.2f}s")

# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print("=" * 70)
    print("PYTHAGOREAN TRIPLE TREE: 10 NEW EXPERIMENTS (Fields 141-150)")
    print("=" * 70)

    experiment_141_density()
    print()
    experiment_142_height()
    print()
    experiment_143_siblings()
    print()
    experiment_144_inverse()
    print()
    experiment_145_angles()
    print()
    experiment_146_automorphisms()
    print()
    experiment_147_generating()
    print()
    experiment_148_pyth_primes()
    print()
    experiment_149_cross_tree()
    print()
    experiment_150_tree_mod_composite()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for fid in sorted(RESULTS.keys()):
        r = RESULTS[fid]
        print(f"  [{fid}] {r['name']}: {r.get('elapsed', 0):.2f}s")
