#!/usr/bin/env python3
"""
Pythagorean Quadruple Factoring Framework — Interactive Demo

Demonstrates the core concepts:
1. Finding Pythagorean quadruples
2. The three peel channels
3. Collision-based factor extraction
4. Lebesgue parametrisation
5. Energy conservation verification
6. Multi-representation collision search
"""

from math import gcd, isqrt
from itertools import combinations
from collections import defaultdict
import random


# ============================================================
# Core data structures
# ============================================================

class PythagoreanQuadruple:
    """A tuple (a, b, c, d) with a² + b² + c² = d²."""

    def __init__(self, a: int, b: int, c: int, d: int):
        self.a, self.b, self.c, self.d = a, b, c, d
        assert a**2 + b**2 + c**2 == d**2, f"Not a Pythagorean quadruple: {a}²+{b}²+{c}²≠{d}²"

    def __repr__(self):
        return f"PQ({self.a}, {self.b}, {self.c}, {self.d})"

    # --- The Three Peel Channels ---

    def peel_a(self):
        """(d-a)(d+a) = b² + c²"""
        return (self.d - self.a, self.d + self.a, self.b**2 + self.c**2)

    def peel_b(self):
        """(d-b)(d+b) = a² + c²"""
        return (self.d - self.b, self.d + self.b, self.a**2 + self.c**2)

    def peel_c(self):
        """(d-c)(d+c) = a² + b²"""
        return (self.d - self.c, self.d + self.c, self.a**2 + self.b**2)

    def all_peels(self):
        return [self.peel_a(), self.peel_b(), self.peel_c()]

    # --- Energy ---

    def kinetic_energy(self):
        return self.a**2 + self.b**2 + self.c**2

    def potential_energy(self):
        return self.d**2

    def binding_energies(self):
        return [self.d**2 - self.a**2, self.d**2 - self.b**2, self.d**2 - self.c**2]

    # --- GCD Factoring Channels ---

    def gcd_channels(self, N: int):
        """Compute gcd(peel_factor, N) for all 6 peel factors."""
        results = []
        for minus, plus, prod in self.all_peels():
            g1 = gcd(minus, N)
            g2 = gcd(plus, N)
            g3 = gcd(prod, N)
            for g in [g1, g2, g3]:
                if 1 < g < N:
                    results.append(g)
        return results


# ============================================================
# Finding quadruples
# ============================================================

def find_quadruples(d_max: int):
    """Find all Pythagorean quadruples with hypotenuse ≤ d_max."""
    quads = []
    for d in range(1, d_max + 1):
        d2 = d * d
        for a in range(0, d):
            for b in range(a, d):
                rem = d2 - a**2 - b**2
                if rem < b**2:
                    break
                c = isqrt(rem)
                if c >= b and c * c == rem:
                    quads.append(PythagoreanQuadruple(a, b, c, d))
    return quads


def find_quadruples_for_d(d: int):
    """Find all Pythagorean quadruples with a specific hypotenuse d."""
    quads = []
    d2 = d * d
    for a in range(0, d):
        for b in range(a, d):
            rem = d2 - a**2 - b**2
            if rem < b**2:
                break
            c = isqrt(rem)
            if c >= b and c * c == rem:
                quads.append(PythagoreanQuadruple(a, b, c, d))
    return quads


# ============================================================
# Lebesgue parametrisation
# ============================================================

def lebesgue(m: int, n: int, p: int):
    """Generate a Pythagorean quadruple from Lebesgue parameters."""
    a = m**2 + n**2 - p**2
    b = 2 * m * p
    c = 2 * n * p
    d = m**2 + n**2 + p**2
    return PythagoreanQuadruple(a, b, c, d)


# ============================================================
# Collision-based factoring
# ============================================================

def collision_factor(q1: PythagoreanQuadruple, q2: PythagoreanQuadruple, N: int):
    """Extract factors from two quadruples with the same hypotenuse."""
    assert q1.d == q2.d, "Quadruples must share hypotenuse"
    factors = set()

    # Cross-collision from peel differences
    for p1 in q1.all_peels():
        for p2 in q2.all_peels():
            g = gcd(p1[2], p2[2])
            if 1 < g < N:
                factors.add(g)
            g = gcd(abs(p1[0] - p2[0]), N)
            if 1 < g < N:
                factors.add(g)
            g = gcd(abs(p1[1] - p2[1]), N)
            if 1 < g < N:
                factors.add(g)

    # Direct component differences
    for v1, v2 in [(q1.a, q2.a), (q1.b, q2.b), (q1.c, q2.c)]:
        g = gcd(abs(v1 - v2), N)
        if 1 < g < N:
            factors.add(g)
        g = gcd(v1 + v2, N)
        if 1 < g < N:
            factors.add(g)

    return factors


def quadruple_factor(N: int, d_max: int = None):
    """
    Attempt to factor N using the quadruple collision method.

    Strategy:
    1. Find quadruples with hypotenuse related to N
    2. Use peel channels and collisions to extract factors
    """
    if d_max is None:
        d_max = isqrt(N) + 1

    # Strategy 1: Direct peel channel search
    for d in range(2, min(d_max, N)):
        quads = find_quadruples_for_d(d)
        for q in quads:
            factors = q.gcd_channels(N)
            if factors:
                return factors[0], N // factors[0]

        # Strategy 2: Collision between multiple representations
        if len(quads) >= 2:
            for q1, q2 in combinations(quads, 2):
                factors = collision_factor(q1, q2, N)
                if factors:
                    f = factors.pop()
                    return f, N // f

    return None, None


# ============================================================
# Demo: Channel count verification
# ============================================================

def demo_channel_counts():
    """Verify channel count formulas for different dimensions."""
    print("=" * 60)
    print("CHANNEL COUNT VERIFICATION")
    print("=" * 60)
    print(f"{'k':>4} | {'Peel':>6} | {'Cross':>6} | {'GCD':>6} | {'Total':>6}")
    print("-" * 40)
    for k in [2, 3, 4, 8]:
        peel = k
        cross = k * (k - 1) // 2  # C(k, 2)
        gcd_ch = k
        total = peel + cross + gcd_ch
        print(f"{k:>4} | {peel:>6} | {cross:>6} | {gcd_ch:>6} | {total:>6}")
    print()


# ============================================================
# Demo: Peel channels
# ============================================================

def demo_peel_channels():
    """Demonstrate the three peel channels on concrete examples."""
    print("=" * 60)
    print("PEEL CHANNEL DEMONSTRATION")
    print("=" * 60)

    examples = [
        (1, 2, 2, 3),
        (3, 4, 12, 13),
        (1, 4, 8, 9),
        (4, 4, 7, 9),
    ]

    for a, b, c, d in examples:
        q = PythagoreanQuadruple(a, b, c, d)
        print(f"\nQuadruple: ({a}, {b}, {c}, {d})")
        print(f"  Verification: {a}² + {b}² + {c}² = {a**2} + {b**2} + {c**2} = {a**2+b**2+c**2} = {d}² = {d**2}")

        for name, (minus, plus, prod) in [("a", q.peel_a()), ("b", q.peel_b()), ("c", q.peel_c())]:
            print(f"  Peel-{name}: (d-{name})(d+{name}) = {minus} × {plus} = {minus*plus} = {prod}")

        print(f"  Kinetic energy: {q.kinetic_energy()}")
        print(f"  Potential energy: {q.potential_energy()}")
        print(f"  K = Φ²: {q.kinetic_energy()} = {q.potential_energy()} ✓" if q.kinetic_energy() == q.potential_energy() else "  ERROR!")
        print(f"  Binding energies: {q.binding_energies()} (sum = {sum(q.binding_energies())} = 2d² = {2*d**2})")
    print()


# ============================================================
# Demo: Collision factoring
# ============================================================

def demo_collision_factoring():
    """Demonstrate collision-based factor extraction."""
    print("=" * 60)
    print("COLLISION FACTORING DEMONSTRATION")
    print("=" * 60)

    # Example: d = 9 has two representations
    q1 = PythagoreanQuadruple(1, 4, 8, 9)
    q2 = PythagoreanQuadruple(4, 4, 7, 9)

    print(f"\nTwo quadruples with d = 9:")
    print(f"  q1 = {q1}")
    print(f"  q2 = {q2}")

    print(f"\n  Peel-a of q1: (9-1)(9+1) = 8 × 10 = {8*10}")
    print(f"  Peel-a of q2: (9-4)(9+4) = 5 × 13 = {5*13}")
    print(f"  gcd(80, 65) = {gcd(80, 65)}")

    # Larger example
    print(f"\n--- Multi-representation search for d up to 30 ---")
    reps = defaultdict(list)
    for d in range(1, 31):
        quads = find_quadruples_for_d(d)
        if len(quads) >= 2:
            reps[d] = quads

    for d, quads in sorted(reps.items()):
        print(f"\n  d = {d}: {len(quads)} representations")
        for q in quads:
            print(f"    {q}")
        if len(quads) >= 2:
            q1, q2 = quads[0], quads[1]
            for p1 in q1.all_peels():
                for p2 in q2.all_peels():
                    g = gcd(p1[2], p2[2])
                    if g > 1:
                        print(f"    → gcd({p1[2]}, {p2[2]}) = {g}")
    print()


# ============================================================
# Demo: Lebesgue parametrisation
# ============================================================

def demo_lebesgue():
    """Demonstrate the Lebesgue parametrisation."""
    print("=" * 60)
    print("LEBESGUE PARAMETRISATION")
    print("=" * 60)

    for m in range(1, 5):
        for n in range(1, 5):
            for p in range(1, 5):
                a = m**2 + n**2 - p**2
                if a > 0:
                    q = lebesgue(m, n, p)
                    print(f"  L({m},{n},{p}) → {q}  (d = {m}²+{n}²+{p}² = {m**2+n**2+p**2})")
    print()


# ============================================================
# Demo: Gravity-Energy product identity
# ============================================================

def demo_gravity_energy_product():
    """Verify the gravity-energy product identity on examples."""
    print("=" * 60)
    print("GRAVITY-ENERGY PRODUCT IDENTITY")
    print("=" * 60)
    print("  (d-a)(d+a)(d-b)(d+b)(d-c)(d+c) = (b²+c²)(a²+c²)(a²+b²)")

    quads = find_quadruples(20)
    for q in quads[:10]:
        a, b, c, d = q.a, q.b, q.c, q.d
        lhs = (d-a)*(d+a) * (d-b)*(d+b) * (d-c)*(d+c)
        rhs = (b**2+c**2) * (a**2+c**2) * (a**2+b**2)
        status = "✓" if lhs == rhs else "✗"
        print(f"  {q}: LHS={lhs}, RHS={rhs} {status}")
    print()


# ============================================================
# Demo: Factoring integers
# ============================================================

def demo_factoring():
    """Demonstrate quadruple-based factoring on small composites."""
    print("=" * 60)
    print("QUADRUPLE-BASED FACTORING")
    print("=" * 60)

    composites = [15, 21, 35, 77, 91, 143, 221, 323, 437, 667, 899, 1001]

    for N in composites:
        p, q = quadruple_factor(N, d_max=50)
        if p is not None:
            print(f"  {N} = {p} × {q}")
        else:
            print(f"  {N}: no factor found (d_max too small)")
    print()


# ============================================================
# Demo: Euler four-square identity
# ============================================================

def demo_euler_identity():
    """Verify Euler's four-square identity."""
    print("=" * 60)
    print("EULER'S FOUR-SQUARE IDENTITY")
    print("=" * 60)

    a1, a2, a3, a4 = 1, 2, 3, 4
    b1, b2, b3, b4 = 5, 6, 7, 8

    lhs = (a1**2+a2**2+a3**2+a4**2) * (b1**2+b2**2+b3**2+b4**2)

    c1 = a1*b1 - a2*b2 - a3*b3 - a4*b4
    c2 = a1*b2 + a2*b1 + a3*b4 - a4*b3
    c3 = a1*b3 - a2*b4 + a3*b1 + a4*b2
    c4 = a1*b4 + a2*b3 - a3*b2 + a4*b1

    rhs = c1**2 + c2**2 + c3**2 + c4**2

    print(f"  ({a1}²+{a2}²+{a3}²+{a4}²) × ({b1}²+{b2}²+{b3}²+{b4}²)")
    print(f"  = {a1**2+a2**2+a3**2+a4**2} × {b1**2+b2**2+b3**2+b4**2}")
    print(f"  = {lhs}")
    print(f"  = {c1}² + {c2}² + {c3}² + {c4}²")
    print(f"  = {c1**2} + {c2**2} + {c3**2} + {c4**2}")
    print(f"  = {rhs}")
    print(f"  Identity holds: {lhs == rhs} ✓" if lhs == rhs else "  ERROR!")
    print()


# ============================================================
# Demo: Representation density
# ============================================================

def demo_representation_density():
    """Show how r₃(N) grows with N."""
    print("=" * 60)
    print("REPRESENTATION DENSITY r₃(N)")
    print("=" * 60)
    print(f"  {'N':>6} | {'r₃(N)':>6} | {'√N':>8} | {'Density':>10}")
    print("  " + "-" * 40)

    for N in [10, 50, 100, 200, 500, 1000, 2000, 5000]:
        count = 0
        for a in range(0, isqrt(N) + 1):
            for b in range(a, isqrt(N - a**2) + 1):
                rem = N - a**2 - b**2
                if rem < 0:
                    break
                c = isqrt(rem)
                if c >= b and c * c == rem:
                    count += 1
        sqrtN = N ** 0.5
        density = count / sqrtN if sqrtN > 0 else 0
        print(f"  {N:>6} | {count:>6} | {sqrtN:>8.2f} | {density:>10.4f}")
    print()


# ============================================================
# Demo: Smooth peel analysis
# ============================================================

def is_smooth(n: int, B: int) -> bool:
    """Check if n is B-smooth (all prime factors ≤ B)."""
    if n <= 1:
        return True
    for p in range(2, B + 1):
        while n % p == 0:
            n //= p
    return n == 1


def demo_smooth_peels():
    """Find quadruples with smooth peel components."""
    print("=" * 60)
    print("SMOOTH PEEL ANALYSIS (B=10)")
    print("=" * 60)

    B = 10
    smooth_count = 0
    total_count = 0

    quads = find_quadruples(50)
    for q in quads:
        total_count += 1
        peels = q.all_peels()
        smooth_peels = []
        for minus, plus, prod in peels:
            if is_smooth(abs(minus), B) and is_smooth(abs(plus), B):
                smooth_peels.append((minus, plus))

        if smooth_peels:
            smooth_count += 1
            if smooth_count <= 15:
                print(f"  {q}: smooth peels = {smooth_peels}")

    print(f"\n  Total quadruples (d ≤ 50): {total_count}")
    print(f"  With B={B}-smooth peels: {smooth_count} ({100*smooth_count/total_count:.1f}%)")
    print()


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  PYTHAGOREAN QUADRUPLE FACTORING FRAMEWORK — DEMO      ║")
    print("║  Gravity, Energy, and the Arithmetic of Spheres        ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    demo_channel_counts()
    demo_peel_channels()
    demo_collision_factoring()
    demo_lebesgue()
    demo_gravity_energy_product()
    demo_euler_identity()
    demo_factoring()
    demo_representation_density()
    demo_smooth_peels()

    print("All demos completed successfully!")
