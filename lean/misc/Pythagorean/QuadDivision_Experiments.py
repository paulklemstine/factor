#!/usr/bin/env python3
"""
Quadruple Division Factoring Experiments
=========================================

Core research pipeline:
1. Start with N → build trivial Pythagorean triple with N as a leg
2. Lift triple to Pythagorean quadruple
3. Perform "4D division" — normalize/reduce the quadruple
4. Map the reduced quadruple back to a triple
5. Extract factor information from GCD cascades

We also explore the Berggren tree's self-loop structure and how
4D division creates new parent/child links in the tree graph.
"""

import math
from itertools import product
from collections import defaultdict
import json

# ─────────────────────────────────────────────────────────
# §1. TRIPLE CONSTRUCTION FROM N
# ─────────────────────────────────────────────────────────

def trivial_triple_from_N(N):
    """
    Build a Pythagorean triple (a, b, c) with N as one leg.
    
    For any integer N ≥ 1:
      - If N is odd and N ≥ 3: a=N, b=(N²-1)/2, c=(N²+1)/2
      - If N is even and N ≥ 4: a=N, b=(N/2)²-1, c=(N/2)²+1
      - Special cases: N=1 → (3,4,5) scaled; N=2 → (3,4,5) scaled
    
    Returns (a, b, c) with a² + b² = c².
    """
    if N < 3:
        # Embed N in a known triple
        if N == 1:
            return (3, 4, 5)  # N=1 doesn't form a primitive triple easily
        if N == 2:
            return (3, 4, 5)
    
    if N % 2 == 1:  # odd
        b = (N * N - 1) // 2
        c = (N * N + 1) // 2
        return (N, b, c)
    else:  # even
        m = N // 2
        b = m * m - 1
        c = m * m + 1
        return (N, b, c)

def all_triples_with_leg(N, max_search=10000):
    """Find all primitive Pythagorean triples with N as a leg, up to search bound."""
    triples = []
    # N = a: find b,c with a² + b² = c², i.e., c² - b² = N², (c-b)(c+b) = N²
    N2 = N * N
    for d in range(1, int(math.isqrt(N2)) + 1):
        if N2 % d == 0:
            e = N2 // d
            # c - b = d, c + b = e, need d < e and same parity
            if d < e and (d + e) % 2 == 0:
                c = (d + e) // 2
                b = (e - d) // 2
                if b > 0 and N*N + b*b == c*c:
                    g = math.gcd(math.gcd(N, b), c)
                    triples.append((N, b, c, g))
    return triples


# ─────────────────────────────────────────────────────────
# §2. TRIPLE ↔ QUADRUPLE CONVERSIONS
# ─────────────────────────────────────────────────────────

def triple_to_quadruple(a, b, c):
    """
    Lift a Pythagorean triple (a,b,c) with a²+b²=c² to quadruples.
    
    Method: find all (a,b,k,d) with a²+b²+k²=d².
    Since a²+b²=c², we need c²+k²=d², i.e., (d-k)(d+k)=c².
    
    Returns list of quadruples (a, b, k, d).
    """
    quads = []
    c2 = c * c
    # Factor c² = (d-k)(d+k)
    for divisor in range(1, c + 1):
        if c2 % divisor == 0:
            complement = c2 // divisor
            # d - k = divisor, d + k = complement
            if (divisor + complement) % 2 == 0 and divisor < complement:
                d = (divisor + complement) // 2
                k = (complement - divisor) // 2
                if k > 0:
                    assert a*a + b*b + k*k == d*d, f"Quad check failed: {a},{b},{k},{d}"
                    quads.append((a, b, k, d))
    return quads

def quadruple_to_triples(a, b, c, d):
    """
    Project a Pythagorean quadruple back to triples.
    
    a²+b²+c²=d² gives three projections:
    1. (a, b, √(c²+...))  — combine last two
    2. (a, c, √(b²+...))  — combine middle two  
    3. (b, c, √(a²+...))  — combine first two
    
    Plus: d²-c² = a²+b², so (a,b) pair with hypotenuse² = d²-c²
    """
    results = []
    # The key projection: a² + b² = d² - c² = (d-c)(d+c)
    s = a*a + b*b
    sq = int(math.isqrt(s))
    if sq * sq == s:
        results.append(('ab_proj', a, b, sq))
    
    # a² + c² = d² - b²
    s2 = a*a + c*c
    sq2 = int(math.isqrt(s2))
    if sq2 * sq2 == s2:
        results.append(('ac_proj', a, c, sq2))
    
    # b² + c² = d² - a²
    s3 = b*b + c*c
    sq3 = int(math.isqrt(s3))
    if sq3 * sq3 == s3:
        results.append(('bc_proj', b, c, sq3))
    
    return results


# ─────────────────────────────────────────────────────────
# §3. QUADRUPLE "DIVISION" — THE 4D REDUCTION
# ─────────────────────────────────────────────────────────

def quad_division(a, b, c, d):
    """
    "Divide" a quadruple by (1,1,1,1): extract common structure.
    
    Key idea: Find the GCD structure across components.
    g = gcd(a,b,c,d) gives the scaling factor.
    But more interesting: pairwise GCDs reveal factor bridges.
    
    Returns a dict of reduction data.
    """
    g_all = math.gcd(math.gcd(a, b), math.gcd(c, d))
    g_ab = math.gcd(a, b)
    g_ac = math.gcd(a, c)
    g_ad = math.gcd(a, d)
    g_bc = math.gcd(b, c)
    g_bd = math.gcd(b, d)
    g_cd = math.gcd(c, d)
    
    # The "reduced" quadruple
    if g_all > 0:
        red = (a // g_all, b // g_all, c // g_all, d // g_all)
    else:
        red = (a, b, c, d)
    
    # Difference-of-squares factoring
    diff_factor_dc = d - c  # (d-c)(d+c) = a² + b²
    sum_factor_dc = d + c
    
    # Cross GCDs with the target N (here, a)
    g_diff_a = math.gcd(abs(diff_factor_dc), abs(a)) if a != 0 else 0
    g_sum_a = math.gcd(abs(sum_factor_dc), abs(a)) if a != 0 else 0
    
    return {
        'original': (a, b, c, d),
        'g_all': g_all,
        'reduced': red,
        'pairwise_gcds': {
            'ab': g_ab, 'ac': g_ac, 'ad': g_ad,
            'bc': g_bc, 'bd': g_bd, 'cd': g_cd
        },
        'd-c': diff_factor_dc,
        'd+c': sum_factor_dc,
        'gcd(d-c, a)': g_diff_a,
        'gcd(d+c, a)': g_sum_a,
    }

def quad_division_factor_extraction(N):
    """
    Full pipeline: N → triple → quadruple → division → factor candidates.
    
    Collects all factor candidates found through quadruple division.
    """
    triple = trivial_triple_from_N(N)
    a, b, c = triple
    
    quads = triple_to_quadruple(a, b, c)
    
    factor_candidates = set()
    details = []
    
    for quad in quads:
        qa, qb, qc, qd = quad
        div_result = quad_division(qa, qb, qc, qd)
        
        # Collect nontrivial factor candidates
        for val in [div_result['g_all'], div_result['d-c'], div_result['d+c'],
                    div_result['gcd(d-c, a)'], div_result['gcd(d+c, a)']]:
            val = abs(val)
            if val > 1 and val < N and N % val == 0:
                factor_candidates.add(val)
        
        # Also check pairwise GCDs
        for key, val in div_result['pairwise_gcds'].items():
            if val > 1 and val < N and N % val == 0:
                factor_candidates.add(val)
        
        details.append(div_result)
    
    return {
        'N': N,
        'triple': triple,
        'num_quadruples': len(quads),
        'factor_candidates': sorted(factor_candidates),
        'actual_factors': [f for f in range(2, N) if N % f == 0],
        'details': details
    }


# ─────────────────────────────────────────────────────────
# §4. BERGGREN TREE AND SELF-LOOPS
# ─────────────────────────────────────────────────────────

def berggren_children(a, b, c):
    """Apply the three Berggren matrices to produce children."""
    return [
        (a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c),   # M₁
        (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c),    # M₂
        (-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c), # M₃
    ]

def berggren_parent(a, b, c):
    """
    Inverse Berggren: find the parent triple.
    The inverse matrices are:
    M₁⁻¹: (a - 2b + 2c, -2a + b + 2c, -2a + 2b + 3c) / ... no, let's use the known inverses.
    
    Actually, the inverse of each Berggren matrix sends child → parent.
    We try all three inverse matrices and pick the one that gives positive values.
    """
    # Inverse matrices (from Berggren's original work):
    candidates = [
        (a - 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c),
        (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c),   # Hmm, need correct inverses
        (-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c),
    ]
    # The correct inverse: try each Berggren matrix as inverse
    # The parent is found by applying inverse matrices until we get smaller values
    inv1 = (a + 2*b - 2*c, 2*a + b - 2*c, 2*a + 2*b - 3*c)
    inv2 = (a - 2*b - 2*c, -2*a + b + 2*c, -2*a + 2*b - 3*c)
    # Known correct inverse: for the standard matrices, the inverse is:
    # Parent = whichever of these gives all-positive and smaller hypotenuse
    results = []
    
    # The three inverse Berggren matrices:
    invs = [
        (a - 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c),  # wrong signs
    ]
    
    # Actually, let me use the well-known result: 
    # There are exactly 3 inverse matrices. A triple (a,b,c) is child of exactly one parent.
    # The parent is obtained by the matrix that yields all-positive and hypotenuse < c.
    
    # Standard approach: try reducing
    for sign_a, sign_b in [(1,1), (1,-1), (-1,1), (-1,-1)]:
        a2, b2 = sign_a * a, sign_b * b
        # Apply M₁⁻¹
        pa = a2 + 2*b2 - 2*c
        pb = 2*a2 + b2 - 2*c  
        pc = -2*a2 - 2*b2 + 3*c
        if pa > 0 and pb > 0 and pc > 0 and pc < c:
            if pa*pa + pb*pb == pc*pc:
                results.append((pa, pb, pc))
    
    return results if results else [(3, 4, 5)]  # Root fallback

def berggren_tree_bfs(max_depth=5):
    """Generate the Berggren tree to a given depth via BFS."""
    tree = {}
    queue = [(3, 4, 5, 0, "root")]
    
    while queue:
        a, b, c, depth, path = queue.pop(0)
        if depth > max_depth:
            continue
        tree[(a, b, c)] = {'depth': depth, 'path': path}
        
        children = berggren_children(a, b, c)
        for i, (ca, cb, cc) in enumerate(children):
            if ca > 0 and cb > 0 and cc > 0:
                child_path = path + f".M{i+1}"
                queue.append((ca, cb, cc, depth + 1, child_path))
    
    return tree

def find_triple_in_tree(target_a, target_b, target_c, tree):
    """Check if a triple appears in the pre-computed tree."""
    # Also check with swapped a,b
    for (a, b, c), info in tree.items():
        if c == target_c and set([a, b]) == set([target_a, target_b]):
            return info
    return None


# ─────────────────────────────────────────────────────────
# §5. QUADRUPLE-MEDIATED BERGGREN LINKS
# ─────────────────────────────────────────────────────────

def quadruple_berggren_bridge(N, tree, max_depth=4):
    """
    For a target N:
    1. Find all triples with N as a leg
    2. Lift each to quadruples
    3. Project quadruples back to (potentially different) triples
    4. Check if any of these new triples appear elsewhere in the Berggren tree
    5. Map the "teleportation links" — jumps in the tree mediated by 4D space
    
    This is the key experiment: does the quadruple lift create shortcuts/loops?
    """
    triples = all_triples_with_leg(N)
    bridges = []
    
    for (a, b, c, g) in triples:
        # Make it primitive
        ap, bp, cp = a // g, b // g, c // g
        
        # Find in tree
        source_info = find_triple_in_tree(ap, bp, cp, tree)
        
        # Lift to quadruples
        quads = triple_to_quadruple(a, b, c)
        
        for quad in quads:
            qa, qb, qc, qd = quad
            
            # Project back to triples (different projections)
            new_triples = quadruple_to_triples(qa, qb, qc, qd)
            
            for proj_type, ta, tb, tc in new_triples:
                # Normalize to primitive
                gt = math.gcd(math.gcd(abs(ta), abs(tb)), abs(tc))
                if gt > 0:
                    pta, ptb, ptc = abs(ta) // gt, abs(tb) // gt, abs(tc) // gt
                    # Ensure a < b < c ordering
                    if pta > ptb:
                        pta, ptb = ptb, pta
                    
                    target_info = find_triple_in_tree(pta, ptb, ptc, tree)
                    
                    if target_info and source_info:
                        bridges.append({
                            'source_triple': (ap, bp, cp),
                            'source_depth': source_info['depth'],
                            'source_path': source_info['path'],
                            'quadruple': quad,
                            'projection': proj_type,
                            'target_triple': (pta, ptb, ptc),
                            'target_depth': target_info['depth'],
                            'target_path': target_info['path'],
                            'depth_jump': abs(source_info['depth'] - target_info['depth']),
                        })
    
    return bridges


# ─────────────────────────────────────────────────────────
# §6. 4D NAVIGATION FOR FACTOR DISCOVERY
# ─────────────────────────────────────────────────────────

def quadruple_neighbors(a, b, c, d, step=1):
    """
    Navigate 4D quadruple space from a known point.
    Search nearby integer points that also satisfy the quadruple equation.
    """
    neighbors = []
    for da, db, dc, dd in product(range(-step, step+1), repeat=4):
        if da == 0 and db == 0 and dc == 0 and dd == 0:
            continue
        na, nb, nc, nd = a+da, b+db, c+dc, d+dd
        if na > 0 and nb > 0 and nc > 0 and nd > 0:
            if na*na + nb*nb + nc*nc == nd*nd:
                neighbors.append((na, nb, nc, nd))
    return neighbors

def gcd_cascade_from_quadruples(N, quads):
    """
    Given quadruples containing N, compute GCD cascades to find factors.
    
    For each pair of quadruples (a₁,b₁,c₁,d₁) and (a₂,b₂,c₂,d₂),
    compute cross-GCDs that might reveal factors of N.
    """
    factors_found = set()
    cascade_data = []
    
    for i in range(len(quads)):
        for j in range(i+1, len(quads)):
            q1 = quads[i]
            q2 = quads[j]
            
            # Cross-component GCDs
            cross_gcds = {}
            for idx1 in range(4):
                for idx2 in range(4):
                    g = math.gcd(abs(q1[idx1]), abs(q2[idx2]))
                    if g > 1 and g < N and N % g == 0:
                        cross_gcds[f"q1[{idx1}],q2[{idx2}]"] = g
                        factors_found.add(g)
            
            # Difference GCDs
            for idx in range(4):
                diff = abs(q1[idx] - q2[idx])
                if diff > 1 and diff < N and N % diff == 0:
                    factors_found.add(diff)
                summ = abs(q1[idx] + q2[idx])
                if summ > 1 and summ < N and N % summ == 0:
                    factors_found.add(summ)
            
            # d-c differences
            dc1 = q1[3] - q1[2]
            dc2 = q2[3] - q2[2]
            g_dc = math.gcd(abs(dc1), abs(dc2))
            if g_dc > 1 and g_dc < N and N % g_dc == 0:
                factors_found.add(g_dc)
            
            if cross_gcds:
                cascade_data.append({
                    'pair': (q1, q2),
                    'cross_gcds': cross_gcds
                })
    
    return factors_found, cascade_data


def navigate_4d_for_factors(N, max_rounds=5):
    """
    Full 4D navigation experiment:
    1. Start from trivial quadruples containing N
    2. Search local neighborhood in 4D
    3. Compute GCD cascades between old and new quadruples
    4. Iterate: use new quadruples as starting points
    """
    # Initial quadruples from trivial triple
    triple = trivial_triple_from_N(N)
    a, b, c = triple
    quads = triple_to_quadruple(a, b, c)
    
    if not quads:
        # Direct search: find any quadruple with N as component
        for b_try in range(1, N):
            for c_try in range(1, N + b_try):
                d2 = N*N + b_try*b_try + c_try*c_try
                d = int(math.isqrt(d2))
                if d*d == d2:
                    quads.append((N, b_try, c_try, d))
                    if len(quads) >= 5:
                        break
            if len(quads) >= 5:
                break
    
    all_factors = set()
    round_data = []
    
    known_quads = set(map(tuple, quads))
    
    for round_num in range(max_rounds):
        # GCD cascade on current set
        factors, cascade = gcd_cascade_from_quadruples(N, list(known_quads))
        all_factors.update(factors)
        
        # Navigate to neighbors
        new_quads = set()
        for q in list(known_quads)[:10]:  # Limit exploration
            neighbors = quadruple_neighbors(*q, step=2)
            for nq in neighbors:
                if nq not in known_quads:
                    new_quads.add(nq)
                    # Check if any component shares a factor with N
                    for comp in nq:
                        g = math.gcd(comp, N)
                        if g > 1 and g < N:
                            all_factors.add(g)
        
        round_data.append({
            'round': round_num,
            'num_quads': len(known_quads),
            'new_quads': len(new_quads),
            'factors_so_far': sorted(all_factors),
        })
        
        known_quads.update(new_quads)
        
        if all_factors:
            break  # Found factors
    
    return {
        'N': N,
        'factors_found': sorted(all_factors),
        'actual_factors': [f for f in range(2, N) if N % f == 0],
        'rounds': round_data,
        'total_quads_explored': len(known_quads),
    }


# ─────────────────────────────────────────────────────────
# §7. EXPERIMENT: FACTOR RECOVERY RATES
# ─────────────────────────────────────────────────────────

def run_factor_recovery_experiment(N_range=range(6, 200)):
    """
    Test the quadruple-division pipeline on a range of composite numbers.
    Record how often it recovers a nontrivial factor.
    """
    results = []
    successes = 0
    total_composite = 0
    
    for N in N_range:
        # Skip primes
        if all(N % i != 0 for i in range(2, int(math.isqrt(N)) + 1)):
            continue
        
        total_composite += 1
        result = quad_division_factor_extraction(N)
        
        found = len(result['factor_candidates']) > 0
        if found:
            successes += 1
        
        results.append({
            'N': N,
            'found_factors': result['factor_candidates'],
            'actual_factors': result['actual_factors'][:5],  # truncate
            'num_quadruples': result['num_quadruples'],
            'success': found,
        })
    
    return {
        'total_composite': total_composite,
        'successes': successes,
        'rate': successes / total_composite if total_composite > 0 else 0,
        'results': results,
    }


# ─────────────────────────────────────────────────────────
# §8. SHARED-FACTOR QUADRUPLE PAIRS
# ─────────────────────────────────────────────────────────

def find_shared_factor_quadruples(N, search_bound=500):
    """
    Find pairs of Pythagorean quadruples where components share factors with N.
    
    Hypothesis: if two quadruples (a₁,b₁,c₁,d₁) and (a₂,b₂,c₂,d₂) both
    have the same hypotenuse d, then gcd(a₁² - a₂², N) often reveals a factor.
    """
    # Collect quadruples by hypotenuse d
    quads_by_d = defaultdict(list)
    
    for d in range(2, search_bound):
        d2 = d * d
        for a in range(1, d):
            for b in range(a, d):
                rem = d2 - a*a - b*b
                if rem <= 0:
                    break
                c = int(math.isqrt(rem))
                if c >= b and c*c == rem:
                    quads_by_d[d].append((a, b, c, d))
    
    # Find shared-factor pairs
    shared_factor_pairs = []
    
    for d, quads in quads_by_d.items():
        if len(quads) < 2:
            continue
        
        for i in range(len(quads)):
            for j in range(i+1, len(quads)):
                q1, q2 = quads[i], quads[j]
                
                # Check cross-differences
                for idx in range(3):  # a, b, c components
                    diff = abs(q1[idx]**2 - q2[idx]**2)
                    if diff > 0:
                        g = math.gcd(diff, N)
                        if g > 1 and g < N and N % g == 0:
                            shared_factor_pairs.append({
                                'q1': q1, 'q2': q2,
                                'shared_d': d,
                                'factor_found': g,
                                'method': f'|a1²-a2²| cross at idx={idx}'
                            })
    
    return shared_factor_pairs


# ─────────────────────────────────────────────────────────
# MAIN: RUN ALL EXPERIMENTS
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("QUADRUPLE DIVISION FACTORING — EXPERIMENTAL RESULTS")
    print("=" * 70)
    
    # Experiment 1: Pipeline demo for specific N values
    print("\n" + "─" * 70)
    print("EXPERIMENT 1: Triple → Quadruple → Division Pipeline")
    print("─" * 70)
    
    test_Ns = [15, 21, 35, 77, 91, 143, 221, 323, 437, 667, 899, 1147]
    
    for N in test_Ns:
        result = quad_division_factor_extraction(N)
        status = "✓ FOUND" if result['factor_candidates'] else "✗ miss"
        print(f"  N={N:5d}: triple={result['triple']}, "
              f"#quads={result['num_quadruples']:3d}, "
              f"factors={result['factor_candidates']}, "
              f"actual={result['actual_factors'][:4]}  [{status}]")
    
    # Experiment 2: Factor recovery rates
    print("\n" + "─" * 70)
    print("EXPERIMENT 2: Factor Recovery Rates (N = 6..200)")
    print("─" * 70)
    
    recovery = run_factor_recovery_experiment(range(6, 201))
    print(f"  Composites tested: {recovery['total_composite']}")
    print(f"  Factors found:     {recovery['successes']}")
    print(f"  Recovery rate:     {recovery['rate']:.1%}")
    
    # Show some interesting cases
    print("\n  Notable successes:")
    for r in recovery['results']:
        if r['success'] and r['N'] > 20:
            print(f"    N={r['N']}: found {r['found_factors']}, actual {r['actual_factors']}")
            if len([x for x in recovery['results'] if x['success'] and x['N'] > 20]) > 15:
                break
    
    # Experiment 3: Berggren tree bridges
    print("\n" + "─" * 70)
    print("EXPERIMENT 3: Quadruple-Mediated Berggren Tree Bridges")
    print("─" * 70)
    
    tree = berggren_tree_bfs(max_depth=4)
    print(f"  Tree size (depth ≤ 4): {len(tree)} nodes")
    
    bridge_Ns = [15, 21, 35, 55, 77, 91]
    for N in bridge_Ns:
        bridges = quadruple_berggren_bridge(N, tree)
        if bridges:
            print(f"\n  N={N}: {len(bridges)} bridge(s) found!")
            for b in bridges[:3]:
                print(f"    {b['source_triple']} (depth {b['source_depth']}) "
                      f"→ [{b['projection']}] → "
                      f"{b['target_triple']} (depth {b['target_depth']}) "
                      f"[jump={b['depth_jump']}]")
        else:
            print(f"  N={N}: no bridges in tree depth ≤ 4")
    
    # Experiment 4: 4D Navigation
    print("\n" + "─" * 70)
    print("EXPERIMENT 4: 4D Navigation for Factor Discovery")
    print("─" * 70)
    
    nav_Ns = [15, 21, 35, 77, 143]
    for N in nav_Ns:
        nav = navigate_4d_for_factors(N, max_rounds=3)
        print(f"  N={N}: explored {nav['total_quads_explored']} quads, "
              f"found factors={nav['factors_found']}, "
              f"actual={nav['actual_factors'][:4]}")
    
    # Experiment 5: Shared-factor quadruple pairs
    print("\n" + "─" * 70)
    print("EXPERIMENT 5: Shared-Factor Quadruple Pairs")
    print("─" * 70)
    
    for N in [15, 21, 35]:
        pairs = find_shared_factor_quadruples(N, search_bound=100)
        if pairs:
            print(f"  N={N}: {len(pairs)} shared-factor pair(s)")
            for p in pairs[:3]:
                print(f"    q1={p['q1']}, q2={p['q2']}, "
                      f"factor={p['factor_found']}, method={p['method']}")
        else:
            print(f"  N={N}: no shared-factor pairs found (bound=100)")
    
    # Experiment 6: Data collection — which composites are easiest?
    print("\n" + "─" * 70)
    print("EXPERIMENT 6: Composites by Ease of Factoring via Quadruples")
    print("─" * 70)
    
    easy = [(r['N'], r['num_quadruples'], r['found_factors']) 
            for r in recovery['results'] if r['success']]
    hard = [(r['N'], r['num_quadruples']) 
            for r in recovery['results'] if not r['success']]
    
    print(f"  Easy composites ({len(easy)}):")
    for n, nq, ff in easy[:20]:
        print(f"    N={n:4d}: {nq:3d} quadruples, factors={ff}")
    
    print(f"\n  Hard composites (first 10 of {len(hard)}):")
    for n, nq in hard[:10]:
        print(f"    N={n:4d}: {nq:3d} quadruples")
    
    print("\n" + "=" * 70)
    print("EXPERIMENTS COMPLETE")
    print("=" * 70)
