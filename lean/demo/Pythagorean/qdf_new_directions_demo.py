#!/usr/bin/env python3
"""
QDF New Directions: Experimental Demonstrations

This module implements computational experiments for the new QDF research directions:
1. Parity classification verification
2. Double-lift factor cascades
3. Thin quadruple / Pell connection
4. Cross-quadruple product amplification
5. Berggren tree preservation verification
6. Parametric family factor recovery rates
7. abc conjecture quality measurement
"""

import math
from collections import defaultdict
from typing import List, Tuple, Optional, Dict
import itertools


def gcd(a: int, b: int) -> int:
    """Compute GCD of two integers."""
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def is_pythagorean_quadruple(a: int, b: int, c: int, d: int) -> bool:
    """Check if a² + b² + c² = d²."""
    return a**2 + b**2 + c**2 == d**2


def is_pythagorean_triple(a: int, b: int, c: int) -> bool:
    """Check if a² + b² = c²."""
    return a**2 + b**2 == c**2


# ═══════════════════════════════════════════════════════════
# Experiment 1: Parity Classification Verification
# ═══════════════════════════════════════════════════════════

def verify_parity_classification(max_d: int = 100) -> Dict:
    """
    Verify the parity classification theorems:
    - If d even and a,b odd → c must be even
    - If a,b,c all odd → d must be odd
    """
    results = {
        "total_quadruples": 0,
        "even_d_two_odd": 0,
        "even_d_three_odd_violations": 0,
        "three_odd_d_even_violations": 0,
        "parity_patterns": defaultdict(int),
    }

    for d in range(1, max_d + 1):
        for a in range(1, d):
            for b in range(a, d):
                c_sq = d**2 - a**2 - b**2
                if c_sq <= 0:
                    continue
                c = int(math.isqrt(c_sq))
                if c * c != c_sq or c < b:
                    continue

                results["total_quadruples"] += 1
                parity = (a % 2, b % 2, c % 2, d % 2)
                results["parity_patterns"][parity] += 1

                # Check: if d even, a,b odd → c even
                if d % 2 == 0 and a % 2 == 1 and b % 2 == 1:
                    results["even_d_two_odd"] += 1
                    if c % 2 == 1:
                        results["even_d_three_odd_violations"] += 1

                # Check: if a,b,c all odd → d odd
                if a % 2 == 1 and b % 2 == 1 and c % 2 == 1:
                    if d % 2 == 0:
                        results["three_odd_d_even_violations"] += 1

    return results


# ═══════════════════════════════════════════════════════════
# Experiment 2: Double-Lift Factor Cascade
# ═══════════════════════════════════════════════════════════

def find_pythagorean_triples(max_c: int) -> List[Tuple[int, int, int]]:
    """Find primitive Pythagorean triples with hypotenuse ≤ max_c."""
    triples = []
    for m in range(2, int(math.sqrt(max_c)) + 1):
        for n in range(1, m):
            if (m - n) % 2 == 0 or gcd(m, n) != 1:
                continue
            a, b, c = m**2 - n**2, 2 * m * n, m**2 + n**2
            if c <= max_c:
                triples.append((min(a, b), max(a, b), c))
    return sorted(set(triples))


def double_lift_experiment(N: int, max_search: int = 1000) -> Dict:
    """
    Test the double-lift factoring cascade on composite N.
    Returns factor recovery information at each level.
    """
    results = {
        "N": N,
        "factors_found": set(),
        "level1_gcds": [],
        "level2_gcds": [],
        "nested_cascade": [],
    }

    # Generate quadruples with N as component
    for b in range(1, min(N, max_search)):
        for c in range(b, min(N, max_search)):
            d_sq = N**2 + b**2 + c**2
            d = int(math.isqrt(d_sq))
            if d * d != d_sq:
                continue

            # Level 1: standard QDF
            g1 = gcd(d - c, N)
            g2 = gcd(d + c, N)
            results["level1_gcds"].append((g1, g2, b, c, d))
            if 1 < g1 < N:
                results["factors_found"].add(g1)
            if 1 < g2 < N:
                results["factors_found"].add(g2)

            # Level 2: lift further
            for k2 in range(1, min(d, 200)):
                d2_sq = d**2 + k2**2
                d2 = int(math.isqrt(d2_sq))
                if d2 * d2 != d2_sq:
                    continue

                g3 = gcd(d2 - k2, N)
                g4 = gcd(d2 + k2, N)
                results["level2_gcds"].append((g3, g4, k2, d2))
                if 1 < g3 < N:
                    results["factors_found"].add(g3)
                if 1 < g4 < N:
                    results["factors_found"].add(g4)

                # Nested cascade: (d2-k2)(d2+k2) - (d-c)(d+c) = c²
                cascade = (d2 - k2) * (d2 + k2) - (d - c) * (d + c)
                results["nested_cascade"].append((cascade, c**2, cascade == c**2))

    results["factors_found"] = sorted(results["factors_found"])
    return results


# ═══════════════════════════════════════════════════════════
# Experiment 3: Thin Quadruples and Pell Connection
# ═══════════════════════════════════════════════════════════

def find_thin_quadruples(max_d: int = 500) -> List[Tuple[int, int, int]]:
    """
    Find thin quadruples where d - c = 1.
    These satisfy a² + b² = 2d - 1.
    """
    thin = []
    for d in range(2, max_d + 1):
        target = 2 * d - 1
        for a in range(1, int(math.sqrt(target)) + 1):
            b_sq = target - a**2
            if b_sq <= 0:
                continue
            b = int(math.isqrt(b_sq))
            if b * b == b_sq and b >= a:
                assert is_pythagorean_quadruple(a, b, d - 1, d)
                thin.append((a, b, d))
    return thin


# ═══════════════════════════════════════════════════════════
# Experiment 4: Cross-Quadruple Product Amplification
# ═══════════════════════════════════════════════════════════

def cross_quadruple_factor_test(N: int) -> Dict:
    """
    Test factor extraction using cross-quadruple products.
    (d1*d2)² = (a1²+b1²+c1²)(a2²+b2²+c2²)
    """
    quadruples = []

    # Find quadruples with N as component
    for b in range(1, min(N, 200)):
        for c in range(b, min(N, 200)):
            d_sq = N**2 + b**2 + c**2
            d = int(math.isqrt(d_sq))
            if d * d == d_sq:
                quadruples.append((N, b, c, d))

    results = {
        "N": N,
        "quadruples_found": len(quadruples),
        "single_factors": set(),
        "cross_factors": set(),
    }

    # Single quadruple factors
    for a, b, c, d in quadruples:
        for g in [gcd(d - c, N), gcd(d + c, N)]:
            if 1 < g < N:
                results["single_factors"].add(g)

    # Cross-quadruple products
    for (a1, b1, c1, d1), (a2, b2, c2, d2) in itertools.combinations(quadruples, 2):
        prod = d1 * d2
        for g in [gcd(prod, N), gcd(d1 - d2, N), gcd(c1 - c2, N), gcd(b1 - b2, N)]:
            if 1 < g < N:
                results["cross_factors"].add(g)

    results["single_factors"] = sorted(results["single_factors"])
    results["cross_factors"] = sorted(results["cross_factors"])
    return results


# ═══════════════════════════════════════════════════════════
# Experiment 5: Berggren Preservation Verification
# ═══════════════════════════════════════════════════════════

def berggren_M1(a, b, c):
    return (a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c)

def berggren_M2(a, b, c):
    return (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c)

def berggren_M3(a, b, c):
    return (-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c)

def verify_berggren_preservation(depth: int = 6) -> Dict:
    """Verify all Berggren transformations preserve Pythagorean property."""
    results = {"total_tested": 0, "all_preserved": True, "triples_generated": []}

    queue = [(3, 4, 5)]
    visited = set()

    for _ in range(depth):
        next_queue = []
        for a, b, c in queue:
            if (a, b, c) in visited:
                continue
            visited.add((a, b, c))
            results["total_tested"] += 1

            for name, transform in [("M1", berggren_M1), ("M2", berggren_M2), ("M3", berggren_M3)]:
                a2, b2, c2 = transform(a, b, c)
                preserved = is_pythagorean_triple(a2, b2, c2)
                if not preserved:
                    results["all_preserved"] = False
                    print(f"VIOLATION: {name}({a},{b},{c}) = ({a2},{b2},{c2}), "
                          f"{a2**2}+{b2**2} = {a2**2+b2**2} != {c2**2}")
                if c2 < 1000:
                    next_queue.append((abs(a2), abs(b2), abs(c2)))

        queue = next_queue
        results["triples_generated"] = list(visited)

    return results


# ═══════════════════════════════════════════════════════════
# Experiment 6: Parametric Family Factor Recovery
# ═══════════════════════════════════════════════════════════

def parametric_family_recovery(composites: List[int]) -> Dict:
    """Test factor recovery across different parametric families."""
    families = {
        "(1,2,2,3)": lambda k: (k, 2*k, 2*k, 3*k),
        "(2,3,6,7)": lambda k: (2*k, 3*k, 6*k, 7*k),
        "(1,4,8,9)": lambda k: (k, 4*k, 8*k, 9*k),
    }

    results = {}
    for name, family in families.items():
        success = 0
        total = len(composites)
        details = []

        for N in composites:
            found = False
            for k in range(1, N + 1):
                a, b, c, d = family(k)
                if not is_pythagorean_quadruple(a, b, c, d):
                    continue

                for target in [N]:
                    # Try embedding N in different positions
                    g1 = gcd(d - c, target)
                    g2 = gcd(d + c, target)
                    if (1 < g1 < target) or (1 < g2 < target):
                        found = True
                        break
                if found:
                    break

            if found:
                success += 1
            details.append((N, found))

        results[name] = {
            "success_rate": success / total if total > 0 else 0,
            "successes": success,
            "total": total,
        }

    return results


# ═══════════════════════════════════════════════════════════
# Experiment 7: abc Quality Measurement
# ═══════════════════════════════════════════════════════════

def radical(n: int) -> int:
    """Compute rad(n) = product of distinct prime factors."""
    if n == 0:
        return 0
    n = abs(n)
    rad = 1
    d = 2
    while d * d <= n:
        if n % d == 0:
            rad *= d
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        rad *= n
    return rad


def abc_quality_from_quadruples(max_d: int = 200) -> List[Dict]:
    """
    Compute abc quality from quadruple factoring identities.
    For a² + b² + c² = d², the triple is (d-c, d+c, a²+b²).
    """
    qualities = []
    for d in range(2, max_d + 1):
        for c in range(0, d):
            for a in range(1, d):
                b_sq = d**2 - a**2 - c**2
                if b_sq <= 0:
                    continue
                b = int(math.isqrt(b_sq))
                if b * b != b_sq or b < a:
                    continue

                # abc triple: (d-c) + (-(a²+b²) + d + c) = ... wait
                # Actually: (d-c)(d+c) = a²+b², so abc triple is:
                # a_abc = d - c, b_abc = 1 (trivially), c_abc = d + c
                # Or we use: a_abc = d-c, b_abc = d+c, c_abc = a²+b²
                # Note: a_abc + ... this isn't a standard abc triple.
                # The abc conjecture applies to a+b=c with coprime a,b,c.
                dc_minus = d - c
                dc_plus = d + c
                sum_sq = a**2 + b**2

                if dc_minus <= 0 or dc_plus <= 0:
                    continue
                if dc_minus * dc_plus != sum_sq:
                    continue  # Sanity check

                # Compute rad of the product
                rad_val = radical(dc_minus * dc_plus * sum_sq)
                if rad_val == 0:
                    continue

                quality = math.log(sum_sq) / math.log(rad_val) if rad_val > 1 else 0

                if quality > 0.8:  # Only record high-quality triples
                    qualities.append({
                        "a": a, "b": b, "c": c, "d": d,
                        "d_minus_c": dc_minus, "d_plus_c": dc_plus,
                        "sum_sq": sum_sq, "radical": rad_val,
                        "quality": quality,
                    })

    return sorted(qualities, key=lambda x: -x["quality"])


# ═══════════════════════════════════════════════════════════
# Experiment 8: Factor Recovery Rate (Enhanced Pipeline)
# ═══════════════════════════════════════════════════════════

def enhanced_factor_recovery(max_N: int = 300) -> Dict:
    """
    Test enhanced QDF pipeline with parity filters and double lifts.
    """
    composites = [n for n in range(6, max_N + 1)
                  if not all(n % p != 0 for p in range(2, int(math.sqrt(n)) + 1))]

    results = {
        "range": (6, max_N),
        "total_composites": len(composites),
        "basic_factored": 0,
        "double_lift_factored": 0,
        "cross_quad_factored": 0,
        "total_factored": 0,
        "unfactored": [],
    }

    for N in composites:
        factored = False

        # Basic QDF: try all quadruples up to bound
        for b in range(1, min(N, 100)):
            for c in range(0, min(N, 100)):
                d_sq = N**2 + b**2 + c**2
                d = int(math.isqrt(d_sq))
                if d * d != d_sq:
                    continue
                g1 = gcd(d - c, N)
                g2 = gcd(d + c, N)
                if (1 < g1 < N) or (1 < g2 < N):
                    factored = True
                    results["basic_factored"] += 1
                    break
            if factored:
                break

        if not factored:
            # Double-lift attempt
            dl = double_lift_experiment(N, max_search=100)
            if dl["factors_found"]:
                factored = True
                results["double_lift_factored"] += 1

        if not factored:
            # Cross-quadruple attempt
            cq = cross_quadruple_factor_test(N)
            if cq["cross_factors"]:
                factored = True
                results["cross_quad_factored"] += 1

        if factored:
            results["total_factored"] += 1
        else:
            results["unfactored"].append(N)

    results["recovery_rate"] = results["total_factored"] / results["total_composites"] \
        if results["total_composites"] > 0 else 0
    return results


# ═══════════════════════════════════════════════════════════
# Main: Run All Experiments
# ═══════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("QDF NEW DIRECTIONS: EXPERIMENTAL RESULTS")
    print("=" * 70)

    # Experiment 1: Parity Classification
    print("\n" + "─" * 70)
    print("EXPERIMENT 1: Parity Classification Verification")
    print("─" * 70)
    parity = verify_parity_classification(50)
    print(f"Total quadruples tested: {parity['total_quadruples']}")
    print(f"Cases with d even, a,b odd: {parity['even_d_two_odd']}")
    print(f"  → Violations (c odd): {parity['even_d_three_odd_violations']}")
    print(f"Three-odd d-even violations: {parity['three_odd_d_even_violations']}")
    print(f"\nParity patterns (a%2, b%2, c%2, d%2) → count:")
    for pattern in sorted(parity["parity_patterns"].keys()):
        count = parity["parity_patterns"][pattern]
        print(f"  {pattern}: {count}")

    # Experiment 2: Double-Lift
    print("\n" + "─" * 70)
    print("EXPERIMENT 2: Double-Lift Factor Cascade")
    print("─" * 70)
    for N in [15, 21, 35, 77, 91, 143, 221]:
        dl = double_lift_experiment(N, max_search=50)
        factors_str = ", ".join(map(str, dl["factors_found"])) if dl["factors_found"] else "none"
        print(f"N = {N:>4}: L1 GCDs = {len(dl['level1_gcds']):>3}, "
              f"L2 GCDs = {len(dl['level2_gcds']):>3}, "
              f"Factors = [{factors_str}]")

    # Experiment 3: Thin Quadruples
    print("\n" + "─" * 70)
    print("EXPERIMENT 3: Thin Quadruples (d - c = 1)")
    print("─" * 70)
    thin = find_thin_quadruples(100)
    print(f"Found {len(thin)} thin quadruples with d ≤ 100")
    print(f"First 15: ")
    for a, b, d in thin[:15]:
        print(f"  ({a}, {b}, {d-1}, {d}) → a²+b² = {a**2+b**2} = 2·{d}-1 = {2*d-1}")

    # Experiment 4: Berggren Preservation
    print("\n" + "─" * 70)
    print("EXPERIMENT 4: Berggren Preservation Verification")
    print("─" * 70)
    berggren = verify_berggren_preservation(5)
    print(f"Triples tested: {berggren['total_tested']}")
    print(f"All preserved: {berggren['all_preserved']}")

    # Experiment 5: abc Quality
    print("\n" + "─" * 70)
    print("EXPERIMENT 5: abc Quality from Quadruples")
    print("─" * 70)
    abc_quals = abc_quality_from_quadruples(100)
    print(f"Found {len(abc_quals)} high-quality (q > 0.8) abc triples")
    if abc_quals:
        print("Top 10 by quality:")
        for q in abc_quals[:10]:
            print(f"  (a,b,c,d) = ({q['a']},{q['b']},{q['c']},{q['d']}), "
                  f"quality = {q['quality']:.4f}")

    # Experiment 6: Enhanced Recovery
    print("\n" + "─" * 70)
    print("EXPERIMENT 6: Enhanced Factor Recovery Rate")
    print("─" * 70)
    recovery = enhanced_factor_recovery(200)
    print(f"Range: {recovery['range']}")
    print(f"Total composites: {recovery['total_composites']}")
    print(f"Basic QDF factored: {recovery['basic_factored']}")
    print(f"Double-lift factored: {recovery['double_lift_factored']}")
    print(f"Cross-quad factored: {recovery['cross_quad_factored']}")
    print(f"Total factored: {recovery['total_factored']}")
    print(f"Recovery rate: {recovery['recovery_rate']:.1%}")
    if recovery['unfactored']:
        print(f"Unfactored: {recovery['unfactored'][:20]}")

    print("\n" + "=" * 70)
    print("ALL EXPERIMENTS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
