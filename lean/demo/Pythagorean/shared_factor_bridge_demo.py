#!/usr/bin/env python3
"""
Shared Factor Bridge: Pythagorean Quadruples and Integer Factoring

This demo explores the connection between Pythagorean quadruples (a²+b²+c²=d²)
and integer factoring, implementing the Three-Channel Framework and
Sphere Collision analysis.

Key demonstrations:
1. Finding all Pythagorean quadruples for a given d
2. Three-channel factoring analysis
3. Sphere collision factor extraction
4. Parametric generation and factor revelation
5. Multi-representation GCD factoring
"""

import math
from itertools import combinations
from collections import defaultdict
from typing import List, Tuple, Optional


def find_quadruples(d: int) -> List[Tuple[int, int, int, int]]:
    """Find all Pythagorean quadruples (a, b, c, d) with given d.
    Returns sorted list with a <= b <= c."""
    quads = []
    d2 = d * d
    for c in range(0, d):
        rem = d2 - c * c
        for b in range(0, int(math.isqrt(rem)) + 1):
            a2 = rem - b * b
            if a2 < 0:
                break
            a = int(math.isqrt(a2))
            if a * a == a2 and a <= b and b <= c:
                quads.append((a, b, c, d))
    return sorted(quads)


def three_channel_analysis(a: int, b: int, c: int, d: int):
    """Perform three-channel factoring analysis on a quadruple."""
    print(f"\n{'='*60}")
    print(f"Three-Channel Analysis for ({a}, {b}, {c}, {d})")
    print(f"Verification: {a}² + {b}² + {c}² = {a**2} + {b**2} + {c**2} = {a**2+b**2+c**2} = {d}² = {d**2}")
    print(f"{'='*60}")

    channels = [
        ("Channel 1 (d±c)", d - c, d + c, a**2 + b**2),
        ("Channel 2 (d±b)", d - b, d + b, a**2 + c**2),
        ("Channel 3 (d±a)", d - a, d + a, b**2 + c**2),
    ]

    for name, minus, plus, sos in channels:
        print(f"\n  {name}:")
        print(f"    ({d}-{c if 'c' in name else b if 'b' in name else a})({d}+{c if 'c' in name else b if 'b' in name else a}) = {minus} × {plus} = {minus * plus}")
        print(f"    Sum of squares = {sos}")
        print(f"    Factors: {minus} × {plus}")

        # Check if these factors give useful info about d
        g = math.gcd(minus, d)
        if 1 < g < d:
            print(f"    ★ NONTRIVIAL GCD with d: gcd({minus}, {d}) = {g}")
            print(f"      → d = {g} × {d // g}")

    return channels


def sphere_collision_analysis(d: int, quads: List[Tuple[int, int, int, int]]):
    """Analyze collisions between quadruples on the same sphere."""
    if len(quads) < 2:
        print(f"\nOnly {len(quads)} quadruple(s) for d={d}, need ≥2 for collision analysis.")
        return

    print(f"\n{'='*60}")
    print(f"Sphere Collision Analysis for d = {d}")
    print(f"Found {len(quads)} quadruples on the sphere of radius {d}")
    print(f"{'='*60}")

    for q in quads:
        print(f"  ({q[0]}, {q[1]}, {q[2]}, {q[3]})")

    for i, j in combinations(range(len(quads)), 2):
        q1, q2 = quads[i], quads[j]
        a1, b1, c1 = q1[0], q1[1], q1[2]
        a2, b2, c2 = q2[0], q2[1], q2[2]

        print(f"\n  Pair: ({a1},{b1},{c1}) vs ({a2},{b2},{c2})")

        # Verify sphere cross identity
        lhs = (a1 + a2) * (a1 - a2)
        rhs = (b2 + b1) * (b2 - b1) + (c2 + c1) * (c2 - c1)
        print(f"    Cross Identity: ({a1}+{a2})({a1}-{a2}) = ({b2}+{b1})({b2}-{b1}) + ({c2}+{c1})({c2}-{c1})")
        print(f"    LHS = {lhs}, RHS = {rhs}, Match: {lhs == rhs}")

        # Cross-GCD analysis
        for name, v1, v2 in [("d-c", d - c1, d - c2), ("d+c", d + c1, d + c2),
                              ("d-b", d - b1, d - b2), ("d+b", d + b1, d + b2)]:
            g = math.gcd(abs(v1), abs(v2))
            if g > 1:
                gd = math.gcd(g, d)
                print(f"    gcd({name}: {v1}, {v2}) = {g}", end="")
                if 1 < gd < d:
                    print(f" → gcd with d = {gd} → d = {gd} × {d // gd} ★")
                else:
                    print()


def parametric_factor_revelation(m: int, n: int, p: int, q: int):
    """Demonstrate how the parametrization reveals factor structure."""
    a = m**2 + n**2 - p**2 - q**2
    b = 2 * (m * q + n * p)
    c = 2 * (n * q - m * p)
    d = m**2 + n**2 + p**2 + q**2

    print(f"\n{'='*60}")
    print(f"Parametric Factor Revelation: (m,n,p,q) = ({m},{n},{p},{q})")
    print(f"{'='*60}")
    print(f"  Quadruple: ({a}, {b}, {c}, {d})")
    print(f"  Verification: {a}² + {b}² + {c}² = {a**2 + b**2 + c**2} = {d}² = {d**2}: {a**2 + b**2 + c**2 == d**2}")
    print(f"\n  Factor Revelation:")
    print(f"    m² + n² = {m**2 + n**2}")
    print(f"    p² + q² = {p**2 + q**2}")
    print(f"    d = (m²+n²) + (p²+q²) = {m**2 + n**2} + {p**2 + q**2} = {d}")

    # Gaussian integer connection
    alpha_norm = m**2 + n**2
    beta_norm = p**2 + q**2
    print(f"\n  Gaussian Integer Connection:")
    print(f"    α = {m} + {n}i, |α|² = {alpha_norm}")
    print(f"    β = {p} + {q}i, |β|² = {beta_norm}")
    print(f"    d = |α|² + |β|² = {alpha_norm + beta_norm}")

    if alpha_norm > 1 and beta_norm > 1:
        g = math.gcd(alpha_norm, beta_norm)
        if g > 1:
            print(f"    ★ gcd(|α|², |β|²) = {g} — shared Gaussian factor!")


def multi_rep_factoring(N: int):
    """Attempt to factor N using multiple sum-of-three-squares representations."""
    print(f"\n{'='*60}")
    print(f"Multi-Representation Factoring Attempt: N = {N}")
    print(f"{'='*60}")

    # Find representations of N² as sum of 3 squares
    d = N
    quads = find_quadruples(d)

    if len(quads) == 0:
        print(f"  No representations found for d = {N}.")
        return

    print(f"  Found {len(quads)} quadruples for d = {N}:")
    for q in quads:
        print(f"    ({q[0]}, {q[1]}, {q[2]}, {q[3]})")

    # Try all pairs
    factors_found = set()
    for i, j in combinations(range(len(quads)), 2):
        q1, q2 = quads[i], quads[j]

        # Try various GCD combinations
        for v1, v2, desc in [
            (d - q1[2], d - q2[2], "d-c"),
            (d + q1[2], d + q2[2], "d+c"),
            (d - q1[1], d - q2[1], "d-b"),
            (d + q1[1], d + q2[1], "d+b"),
            (q1[0]**2 + q1[1]**2, q2[0]**2 + q2[1]**2, "a²+b²"),
        ]:
            for val in [v1, v2, math.gcd(abs(v1), abs(v2))]:
                g = math.gcd(abs(val), d)
                if 1 < g < d:
                    factors_found.add(g)

    if factors_found:
        print(f"\n  ★ FACTORS FOUND: {sorted(factors_found)}")
        for f in sorted(factors_found):
            print(f"    {N} = {f} × {N // f}")
    else:
        # Try individual channel analysis
        for q in quads:
            a, b, c = q[0], q[1], q[2]
            for val in [d - c, d + c, d - b, d + b, d - a, d + a]:
                g = math.gcd(abs(val), d)
                if 1 < g < d:
                    factors_found.add(g)
        if factors_found:
            print(f"\n  ★ FACTORS FOUND (single channel): {sorted(factors_found)}")
            for f in sorted(factors_found):
                print(f"    {N} = {f} × {N // f}")
        else:
            print(f"\n  No nontrivial factors found through this method.")


def factor_table(max_d: int = 50):
    """Generate a table showing quadruple counts and factoring success."""
    print(f"\n{'='*60}")
    print(f"Pythagorean Quadruple Census and Factor Analysis (d ≤ {max_d})")
    print(f"{'='*60}")
    print(f"{'d':>4} | {'#Quads':>6} | {'Factorization':>20} | {'Channels reveal factors?':>25}")
    print(f"{'-'*4}-+-{'-'*6}-+-{'-'*20}-+-{'-'*25}")

    for d in range(1, max_d + 1):
        quads = find_quadruples(d)
        if not quads:
            continue

        # Factor d
        factors = []
        n = d
        for p in range(2, int(math.isqrt(n)) + 1):
            while n % p == 0:
                factors.append(p)
                n //= p
        if n > 1:
            factors.append(n)
        fact_str = " × ".join(map(str, factors)) if len(factors) > 1 else "prime" if d > 1 else "1"

        # Check if channels reveal factors
        revealed = set()
        for q in quads:
            a, b, c = q[0], q[1], q[2]
            for val in [d - c, d + c, d - b, d + b, d - a, d + a]:
                g = math.gcd(abs(val), d)
                if 1 < g < d:
                    revealed.add(g)

        reveal_str = str(sorted(revealed)) if revealed else "—"
        print(f"{d:>4} | {len(quads):>6} | {fact_str:>20} | {reveal_str:>25}")


def brahmagupta_demo():
    """Demonstrate the Brahmagupta-Fibonacci identity and its two representations."""
    print(f"\n{'='*60}")
    print(f"Brahmagupta–Fibonacci: Two Representations from Factoring")
    print(f"{'='*60}")

    examples = [(1, 2, 3, 4), (2, 1, 1, 3), (3, 2, 5, 1)]
    for a, b, c, d in examples:
        N = (a**2 + b**2) * (c**2 + d**2)
        rep1 = ((a*c - b*d)**2 + (a*d + b*c)**2)
        rep2 = ((a*c + b*d)**2 + (a*d - b*c)**2)

        print(f"\n  ({a}²+{b}²)({c}²+{d}²) = {a**2+b**2} × {c**2+d**2} = {N}")
        print(f"  Rep 1: ({a*c-b*d})² + ({a*d+b*c})² = {(a*c-b*d)**2} + {(a*d+b*c)**2} = {rep1}")
        print(f"  Rep 2: ({a*c+b*d})² + ({a*d-b*c})² = {(a*c+b*d)**2} + {(a*d-b*c)**2} = {rep2}")

        # Factor from two reps
        x, y = abs(a*c - b*d), abs(a*d + b*c)
        u, v = abs(a*c + b*d), abs(a*d - b*c)
        if (x, y) != (u, v) and (x, y) != (v, u):
            g1 = math.gcd(abs(x - u), abs(y - v)) if abs(x-u) + abs(y-v) > 0 else 0
            g2 = math.gcd(abs(x + u), abs(y + v)) if abs(x+u) + abs(y+v) > 0 else 0
            print(f"  Two-rep factor extraction: gcd(|{x}-{u}|, |{y}-{v}|) = {g1}")
            if g1 > 1:
                print(f"  ★ Nontrivial GCD = {g1} divides {N}: {N} = {g1} × {N // g1}")


# ============================================================
# MAIN DEMO
# ============================================================

if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  SHARED FACTOR BRIDGE: Pythagorean Quadruples & Factoring ║")
    print("╚════════════════════════════════════════════════════════════╝")

    # 1. Basic quadruples and three-channel analysis
    three_channel_analysis(1, 2, 2, 3)
    three_channel_analysis(2, 3, 6, 7)
    three_channel_analysis(1, 4, 8, 9)

    # 2. Sphere collision analysis
    for d in [9, 15, 21, 25, 30]:
        quads = find_quadruples(d)
        sphere_collision_analysis(d, quads)

    # 3. Parametric factor revelation
    parametric_factor_revelation(2, 1, 1, 1)
    parametric_factor_revelation(3, 1, 2, 1)
    parametric_factor_revelation(2, 3, 1, 1)

    # 4. Multi-representation factoring
    for N in [15, 21, 35, 45, 63, 77, 105]:
        multi_rep_factoring(N)

    # 5. Factor table
    factor_table(50)

    # 6. Brahmagupta demo
    brahmagupta_demo()

    print("\n" + "="*60)
    print("Demo complete. See SharedFactorBridge_ResearchPaper.md for full theory.")
    print("="*60)
