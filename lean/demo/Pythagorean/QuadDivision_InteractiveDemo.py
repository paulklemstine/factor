#!/usr/bin/env python3
"""
Quadruple Division Factoring — Interactive Demo
=================================================

A comprehensive demonstration of the QDF pipeline:
  N → Triple → Quadruple → 4D Division → Factor Extraction

Also explores Berggren tree bridges and 4D navigation.

Usage:
  python3 QuadDivision_InteractiveDemo.py          # Run all demos
  python3 QuadDivision_InteractiveDemo.py 143       # Factor a specific N
  python3 QuadDivision_InteractiveDemo.py --tree 5  # Berggren tree to depth 5
"""

import math
import sys
from collections import defaultdict
from itertools import combinations


# ═══════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════

def trivial_triple(N):
    """Construct a Pythagorean triple with N as a leg."""
    if N < 3:
        return (3, 4, 5)
    if N % 2 == 1:
        b = (N * N - 1) // 2
        c = (N * N + 1) // 2
        return (N, b, c)
    else:
        m = N // 2
        return (N, m * m - 1, m * m + 1)


def all_triples_with_leg(N, max_c=None):
    """Find all Pythagorean triples with N as a leg."""
    if max_c is None:
        max_c = N * N
    triples = []
    N2 = N * N
    for d in range(1, int(math.isqrt(N2)) + 1):
        if N2 % d == 0:
            e = N2 // d
            if d < e and (d + e) % 2 == 0:
                c = (d + e) // 2
                b = (e - d) // 2
                if b > 0 and c <= max_c:
                    triples.append((N, b, c))
    return triples


def lift_to_quadruples(a, b, c):
    """Lift triple (a,b,c) to all quadruples (a,b,k,d)."""
    quads = []
    c2 = c * c
    for div in range(1, c + 1):
        if c2 % div == 0:
            comp = c2 // div
            if (div + comp) % 2 == 0 and div < comp:
                d = (div + comp) // 2
                k = (comp - div) // 2
                if k > 0:
                    quads.append((a, b, k, d))
    return quads


def project_quadruple(a, b, c, d):
    """Project quadruple back to triples via all three pair-projections."""
    triples = []
    for name, x, y in [("ab", a, b), ("ac", a, c), ("bc", b, c)]:
        s = x * x + y * y
        r = int(math.isqrt(s))
        if r * r == s and r > 0:
            triples.append((name, x, y, r))
    return triples


def factor_via_quadruple(N, quad):
    """Extract factor candidates from a single quadruple."""
    a, b, c, d = quad
    candidates = set()

    # d-c and d+c GCD method
    dc = d - c
    dpc = d + c
    for val in [dc, dpc]:
        g = math.gcd(abs(val), abs(N))
        if 1 < g < abs(N):
            candidates.add(g)

    # Global GCD
    g_all = math.gcd(math.gcd(abs(a), abs(b)), math.gcd(abs(c), abs(d)))
    if 1 < g_all < abs(N) and N % g_all == 0:
        candidates.add(g_all)

    # Pairwise GCDs with N
    for comp in [a, b, c, d, dc, dpc, a*a + b*b]:
        g = math.gcd(abs(comp), abs(N))
        if 1 < g < abs(N):
            candidates.add(g)

    return candidates


def cross_quad_factors(N, quads):
    """Extract factors from pairs of quadruples."""
    factors = set()
    for i in range(len(quads)):
        for j in range(i + 1, len(quads)):
            q1, q2 = quads[i], quads[j]
            # Cross-component differences
            for idx in range(4):
                diff = abs(q1[idx] - q2[idx])
                summ = abs(q1[idx] + q2[idx])
                for v in [diff, summ]:
                    g = math.gcd(v, N)
                    if 1 < g < N:
                        factors.add(g)
            # Cross square differences
            for idx in range(4):
                sq_diff = abs(q1[idx]**2 - q2[idx]**2)
                if sq_diff > 0:
                    g = math.gcd(sq_diff, N)
                    if 1 < g < N:
                        factors.add(g)
    return factors


def full_pipeline(N, verbose=True):
    """Run the complete QDF pipeline on N."""
    if verbose:
        print(f"\n{'═' * 60}")
        print(f"  QDF PIPELINE: N = {N}")
        print(f"{'═' * 60}")

    # Step 1: Triple
    triple = trivial_triple(N)
    a, b, c = triple
    if verbose:
        print(f"\n  ① Triple: ({a}, {b}, {c})")
        print(f"     Check: {a}² + {b}² = {a*a + b*b} = {c}² = {c*c} ✓")

    # Also find all triples with N as leg
    all_trips = all_triples_with_leg(N, max_c=N*N//2)
    if verbose and len(all_trips) > 1:
        print(f"     ({len(all_trips)} total triples with {N} as a leg)")

    # Step 2: Lift to quadruples
    all_quads = []
    for trip in all_trips[:5]:  # Use up to 5 triples
        quads = lift_to_quadruples(*trip)
        all_quads.extend(quads)

    if verbose:
        print(f"\n  ② Quadruples: {len(all_quads)} found")
        for q in all_quads[:5]:
            print(f"     ({q[0]}, {q[1]}, {q[2]}, {q[3]})  "
                  f"check: {sum(x*x for x in q[:3])} = {q[3]**2} ✓")
        if len(all_quads) > 5:
            print(f"     ... and {len(all_quads) - 5} more")

    # Step 3: Factor extraction
    all_factors = set()
    methods = defaultdict(set)

    for q in all_quads:
        single_factors = factor_via_quadruple(N, q)
        for f in single_factors:
            all_factors.add(f)
            methods[f].add(f"single-quad {q}")

    cross_factors = cross_quad_factors(N, all_quads[:20])
    for f in cross_factors:
        all_factors.add(f)
        methods[f].add("cross-quad")

    # Step 4: Project back to triples
    bridge_triples = set()
    for q in all_quads[:10]:
        projs = project_quadruple(*q)
        for name, x, y, r in projs:
            # Normalize
            g = math.gcd(math.gcd(abs(x), abs(y)), abs(r))
            if g > 0:
                bridge_triples.add((abs(x)//g, abs(y)//g, abs(r)//g))

    if verbose:
        print(f"\n  ③ Factor Extraction:")
        if all_factors:
            for f in sorted(all_factors):
                print(f"     Factor {f} found via: {list(methods[f])[:2]}")
        else:
            print(f"     No nontrivial factors found")

        print(f"\n  ④ Berggren Bridges (projected triples):")
        for t in sorted(bridge_triples)[:8]:
            print(f"     ({t[0]}, {t[1]}, {t[2]})")

        actual = [f for f in range(2, N) if N % f == 0]
        print(f"\n  Result: found {sorted(all_factors)}, actual factors: {actual[:6]}")
        if all_factors:
            print(f"  ✅ SUCCESS")
        else:
            print(f"  ❌ No factors found through pipeline")

    return sorted(all_factors)


# ═══════════════════════════════════════════════════════════
# BERGGREN TREE EXPLORATION
# ═══════════════════════════════════════════════════════════

def berggren_matrices(a, b, c):
    """Apply Berggren matrices M₁, M₂, M₃."""
    return [
        ("M₁", a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c),
        ("M₂", a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c),
        ("M₃", -a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c),
    ]


def build_berggren_tree(max_depth=4):
    """Build the Berggren tree as a dict."""
    tree = {}
    queue = [(3, 4, 5, 0, "R")]

    while queue:
        a, b, c, depth, path = queue.pop(0)
        if depth > max_depth:
            continue
        key = (a, b, c)
        tree[key] = {"depth": depth, "path": path}

        if depth < max_depth:
            for name, ca, cb, cc in berggren_matrices(a, b, c):
                if ca > 0 and cb > 0 and cc > 0:
                    queue.append((ca, cb, cc, depth + 1, path + "." + name))

    return tree


def find_bridges(N, tree):
    """Find 4D bridges for a given N."""
    triples = all_triples_with_leg(N, max_c=50000)
    bridges = []

    for a, b, c in triples:
        g = math.gcd(math.gcd(a, b), c)
        prim = (a // g, b // g, c // g)

        # Check both orderings
        source = tree.get(prim) or tree.get((prim[1], prim[0], prim[2]))
        if not source:
            continue

        quads = lift_to_quadruples(a, b, c)
        for q in quads:
            projs = project_quadruple(*q)
            for proj_name, x, y, r in projs:
                gt = math.gcd(math.gcd(abs(x), abs(y)), abs(r))
                if gt > 0:
                    pt = (abs(x)//gt, abs(y)//gt, abs(r)//gt)
                    target = tree.get(pt) or tree.get((pt[1], pt[0], pt[2]))
                    if target and pt != prim and (pt[1], pt[0], pt[2]) != prim:
                        bridges.append({
                            "source": prim,
                            "target": pt,
                            "via_quad": q,
                            "source_depth": source["depth"],
                            "target_depth": target["depth"],
                            "jump": abs(source["depth"] - target["depth"]),
                        })
    return bridges


def demo_berggren_bridges():
    """Demonstrate Berggren tree bridges."""
    print(f"\n{'═' * 60}")
    print(f"  BERGGREN TREE BRIDGE EXPLORATION")
    print(f"{'═' * 60}")

    tree = build_berggren_tree(max_depth=5)
    print(f"\n  Tree size (depth ≤ 5): {len(tree)} nodes")
    print(f"  Sample nodes:")
    for (a, b, c), info in sorted(tree.items(), key=lambda x: x[1]["depth"])[:12]:
        print(f"    ({a:3d}, {b:3d}, {c:3d})  depth={info['depth']}  path={info['path']}")

    print(f"\n  Bridge Search:")
    for N in [15, 21, 35, 55, 77, 91, 105, 143, 221]:
        bridges = find_bridges(N, tree)
        if bridges:
            print(f"\n  N={N}: {len(bridges)} bridge(s)")
            for b in bridges[:3]:
                print(f"    {b['source']} (d={b['source_depth']}) "
                      f"→ {b['target']} (d={b['target_depth']}) "
                      f"[jump={b['jump']}] via {b['via_quad']}")
        else:
            print(f"  N={N}: no bridges found")


# ═══════════════════════════════════════════════════════════
# STATISTICAL ANALYSIS
# ═══════════════════════════════════════════════════════════

def run_statistics(lo=6, hi=500):
    """Comprehensive statistical analysis."""
    print(f"\n{'═' * 60}")
    print(f"  STATISTICAL ANALYSIS: N ∈ [{lo}, {hi}]")
    print(f"{'═' * 60}")

    results = {"success": [], "fail": [], "partial": []}
    total_composite = 0

    for N in range(lo, hi + 1):
        if all(N % i != 0 for i in range(2, int(math.isqrt(N)) + 1)):
            continue  # prime
        total_composite += 1

        actual = set(f for f in range(2, N) if N % f == 0)
        found = set(full_pipeline(N, verbose=False))

        if found >= actual:
            results["success"].append(N)
        elif found:
            results["partial"].append(N)
        else:
            results["fail"].append(N)

    total = total_composite
    full = len(results["success"])
    partial = len(results["partial"])
    fail = len(results["fail"])
    any_success = full + partial

    print(f"\n  Total composites: {total}")
    print(f"  Full factorization:    {full:4d}  ({full/total*100:.1f}%)")
    print(f"  Partial (≥1 factor):   {partial:4d}  ({partial/total*100:.1f}%)")
    print(f"  Any success:           {any_success:4d}  ({any_success/total*100:.1f}%)")
    print(f"  No factors found:      {fail:4d}  ({fail/total*100:.1f}%)")

    if results["fail"]:
        print(f"\n  Hard cases (no factors found):")
        for n in results["fail"][:20]:
            actual = [f for f in range(2, n) if n % f == 0]
            print(f"    N={n}: factors={actual[:4]}")

    return results


# ═══════════════════════════════════════════════════════════
# QUADRUPLE SPACE NAVIGATION DEMO
# ═══════════════════════════════════════════════════════════

def demo_4d_navigation():
    """Demonstrate 4D quadruple space navigation."""
    print(f"\n{'═' * 60}")
    print(f"  4D QUADRUPLE SPACE NAVIGATION")
    print(f"{'═' * 60}")

    test_cases = [
        (15, "= 3 × 5"),
        (35, "= 5 × 7"),
        (77, "= 7 × 11"),
        (143, "= 11 × 13"),
        (221, "= 13 × 17"),
    ]

    for N, desc in test_cases:
        print(f"\n  N = {N} {desc}")

        # Find all quadruples containing N
        quads = []
        triple = trivial_triple(N)
        quads.extend(lift_to_quadruples(*triple))

        # Also find quadruples where N is any component
        for b in range(1, min(N * 2, 200)):
            for c in range(b, min(N * 3, 300)):
                d2 = N * N + b * b + c * c
                d = int(math.isqrt(d2))
                if d * d == d2 and d > 0:
                    quads.append((N, b, c, d))

        quads = list(set(quads))[:30]
        print(f"    Found {len(quads)} quadruples with N={N}")

        # GCD analysis
        factors = set()
        for q in quads:
            for comp in q:
                g = math.gcd(comp, N)
                if 1 < g < N:
                    factors.add(g)
            dc = q[3] - q[2]
            g = math.gcd(abs(dc), N)
            if 1 < g < N:
                factors.add(g)
            dpc = q[3] + q[2]
            g = math.gcd(abs(dpc), N)
            if 1 < g < N:
                factors.add(g)

        print(f"    Factors from components: {sorted(factors)}")

        # Cross-quad analysis
        cross_f = cross_quad_factors(N, quads)
        print(f"    Factors from cross-quads: {sorted(cross_f)}")


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--tree":
            depth = int(sys.argv[2]) if len(sys.argv) > 2 else 4
            demo_berggren_bridges()
        elif sys.argv[1] == "--stats":
            hi = int(sys.argv[2]) if len(sys.argv) > 2 else 200
            run_statistics(6, hi)
        elif sys.argv[1] == "--nav":
            demo_4d_navigation()
        else:
            N = int(sys.argv[1])
            full_pipeline(N)
    else:
        # Run all demos
        print("╔════════════════════════════════════════════════════════════╗")
        print("║   QUADRUPLE DIVISION FACTORING — COMPLETE DEMO SUITE     ║")
        print("╚════════════════════════════════════════════════════════════╝")

        # Demo 1: Pipeline on selected numbers
        print("\n\n" + "▓" * 60)
        print("  DEMO 1: QDF Pipeline Examples")
        print("▓" * 60)

        for N in [15, 21, 77, 143, 323, 437]:
            full_pipeline(N)

        # Demo 2: Berggren bridges
        print("\n\n" + "▓" * 60)
        print("  DEMO 2: Berggren Tree Bridges")
        print("▓" * 60)
        demo_berggren_bridges()

        # Demo 3: 4D navigation
        print("\n\n" + "▓" * 60)
        print("  DEMO 3: 4D Navigation")
        print("▓" * 60)
        demo_4d_navigation()

        # Demo 4: Statistics
        print("\n\n" + "▓" * 60)
        print("  DEMO 4: Statistical Analysis (N ∈ [6, 300])")
        print("▓" * 60)
        run_statistics(6, 300)

        print("\n\n" + "═" * 60)
        print("  ALL DEMOS COMPLETE")
        print("═" * 60)
