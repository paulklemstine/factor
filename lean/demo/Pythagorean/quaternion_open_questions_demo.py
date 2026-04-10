#!/usr/bin/env python3
"""
Quaternion Descent Open Questions: Computational Demonstrations

Explores the five open questions about the Pythagorean quadruple descent tree:
1. Explicit isomorphism and variable branching via r₃(d²)
2. Hurwitz vs. Lipschitz descent depth comparison
3. Octonion integrality obstruction
4. Quantum gate synthesis / SU(2) integer points
5. Modular forms: r₃(n) values and three-square obstruction
"""

import math
from collections import defaultdict
from itertools import product as cart_product

# ============================================================
# Part 1: Quaternion Arithmetic
# ============================================================

class Quaternion:
    """Integer quaternion (Lipschitz integer)."""
    def __init__(self, w, x, y, z):
        self.w, self.x, self.y, self.z = w, x, y, z

    def sq_norm(self):
        return self.w**2 + self.x**2 + self.y**2 + self.z**2

    def __mul__(self, other):
        return Quaternion(
            self.w*other.w - self.x*other.x - self.y*other.y - self.z*other.z,
            self.w*other.x + self.x*other.w + self.y*other.z - self.z*other.y,
            self.w*other.y - self.x*other.z + self.y*other.w + self.z*other.x,
            self.w*other.z + self.x*other.y - self.y*other.x + self.z*other.w
        )

    def conj(self):
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def __repr__(self):
        return f"({self.w} + {self.x}i + {self.y}j + {self.z}k)"

SIGMA = Quaternion(1, 1, 1, 1)

def euler_from_quat(q):
    """Euler parametrization: quaternion → Pythagorean quadruple."""
    a = q.w**2 + q.x**2 - q.y**2 - q.z**2
    b = 2*(q.w*q.z + q.x*q.y)
    c = 2*(q.x*q.z - q.w*q.y)
    d = q.sq_norm()
    return (a, b, c, d)


# ============================================================
# Part 2: r₃(n) — Representations as sum of 3 squares
# ============================================================

def r3(n):
    """Count representations of n as sum of 3 squares (with signs and order)."""
    count = 0
    bound = int(math.isqrt(n))
    for a in range(-bound, bound+1):
        for b in range(-bound, bound+1):
            rem = n - a*a - b*b
            if rem < 0:
                continue
            c = int(math.isqrt(rem))
            if c*c == rem:
                count += 1
                if c > 0:
                    count += 1  # also -c
    return count


def is_three_square_obstructed(n):
    """Check if n = 4^a(8b+7) — cannot be sum of 3 squares."""
    m = n
    while m > 0 and m % 4 == 0:
        m //= 4
    return m % 8 == 7


# ============================================================
# Part 3: Descent Tree
# ============================================================

def R1111(a, b, c, d):
    """Apply the R₁₁₁₁ reflection."""
    return (d-b-c, d-a-c, d-a-b, 2*d-a-b-c)

def normalize(a, b, c, d):
    """Sort spatial components, take absolute values."""
    spatial = sorted([abs(a), abs(b), abs(c)])
    return (spatial[0], spatial[1], spatial[2], abs(d))

def descent_chain(a, b, c, d, max_steps=50):
    """Compute the descent chain to root."""
    chain = [(a, b, c, d)]
    for _ in range(max_steps):
        if d <= 1:
            break
        a2, b2, c2, d2 = R1111(a, b, c, d)
        a2, b2, c2, d2 = normalize(a2, b2, c2, d2)
        if d2 >= d or d2 <= 0:
            break
        chain.append((a2, b2, c2, d2))
        a, b, c, d = a2, b2, c2, d2
    return chain


def find_primitive_quadruples(max_d):
    """Find all primitive Pythagorean quadruples up to hypotenuse max_d."""
    quads = []
    for d in range(1, max_d+1):
        for c in range(0, d+1):
            for b in range(0, c+1):
                for a in range(0, b+1):
                    if a*a + b*b + c*c == d*d:
                        if math.gcd(math.gcd(a, b), math.gcd(c, d)) == 1:
                            quads.append((a, b, c, d))
    return quads


# ============================================================
# Part 4: Hurwitz vs. Lipschitz Comparison
# ============================================================

def lipschitz_descent_depth(d):
    """Upper bound on Lipschitz descent depth: log_{4/3}(d)."""
    if d <= 1:
        return 0
    return math.ceil(math.log(d) / math.log(4/3))

def hurwitz_descent_depth(d):
    """Upper bound on Hurwitz descent depth: log_2(d)."""
    if d <= 1:
        return 0
    return math.ceil(math.log2(d))


# ============================================================
# Part 5: Octonion Obstruction
# ============================================================

def check_octonion_obstruction():
    """Verify the integrality obstruction for Pythagorean 8-tuples."""
    print("\n=== Octonion Integrality Obstruction ===")
    print("For a reflection in (7,1)-space, we need 3 | (sum of spatial - temporal)")
    print("All-ones vector has Minkowski norm = 7·1 - 1 = 6")
    print()

    # Direct counterexample (same as in Lean proof)
    combo = (2, 3, 6, 0, 0, 0, 0)
    d = 7
    assert sum(x*x for x in combo) == d*d, "Not a Pythagorean 8-tuple!"
    eta = sum(combo) - d  # = 11 - 7 = 4
    print(f"  Counterexample: {combo + (d,)}")
    print(f"    Check: 2²+3²+6²+0²+0²+0²+0² = {sum(x*x for x in combo)} = {d}²")
    print(f"    η(x,s) = {eta}, 3 ∤ {eta}")
    print(f"    → The naive 8-dimensional descent FAILS")

    # A few more small counterexamples
    more = [(1,0,0,0,0,0,0,1), (0,1,0,0,0,0,0,1), (1,1,1,0,0,0,0,1)]
    for v in more:
        combo2 = v[:7]
        d2 = v[7]
        if sum(x*x for x in combo2) == d2*d2:
            e = sum(combo2) - d2
            if e % 3 != 0:
                print(f"  Also: {v}, η = {e}, 3 ∤ {e}")
    return [(combo, d, eta)]


# ============================================================
# Part 6: Quantum Gate Density
# ============================================================

def r4(n):
    """Count representations of n as sum of 4 squares."""
    count = 0
    bound = int(math.isqrt(n))
    for w in range(-bound, bound+1):
        for x in range(-bound, bound+1):
            rem2 = n - w*w - x*x
            if rem2 < 0:
                continue
            b2 = int(math.isqrt(rem2))
            for y in range(-b2, b2+1):
                rem3 = rem2 - y*y
                if rem3 < 0:
                    continue
                z = int(math.isqrt(rem3))
                if z*z == rem3:
                    count += 1
                    if z > 0:
                        count += 1
    return count


def angular_density(d):
    """Approximate angular density of integer quaternions at norm d."""
    if d == 0:
        return 0
    n = r4(d)
    # Surface area of S³ of radius √d is 2π²d
    return n / (2 * math.pi**2 * d)


# ============================================================
# Main Demonstrations
# ============================================================

def demo_q1_branching():
    """Question 1: Variable branching and r₃(d²)."""
    print("=" * 60)
    print("QUESTION 1: Variable Branching via r₃(d²)")
    print("=" * 60)

    quads = find_primitive_quadruples(50)
    branching = defaultdict(int)
    for q in quads:
        chain = descent_chain(*q)
        if len(chain) > 1:
            parent_d = chain[1][3]  # parent's hypotenuse
            branching[parent_d] += 1

    print(f"\n{'d':>4} | {'r₃(d²)':>8} | {'Branching':>10} | {'Quadruples at d':>16}")
    print("-" * 50)
    for d in range(1, 31):
        d_quads = [q for q in quads if q[3] == d]
        r3_val = r3(d*d)
        branch = branching.get(d, 0)
        if d_quads or branch > 0 or d <= 10:
            quad_str = ', '.join(str(q) for q in d_quads[:3])
            if len(d_quads) > 3:
                quad_str += f" ... (+{len(d_quads)-3} more)"
            print(f"{d:>4} | {r3_val:>8} | {branch:>10} | {quad_str}")


def demo_q2_hurwitz():
    """Question 2: Hurwitz vs. Lipschitz depth comparison."""
    print("\n" + "=" * 60)
    print("QUESTION 2: Hurwitz vs. Lipschitz Descent Depth")
    print("=" * 60)

    print(f"\n{'d':>8} | {'Lip. bound':>11} | {'Hurw. bound':>12} | {'Actual depth':>13} | {'Ratio':>6}")
    print("-" * 60)

    for d in [3, 7, 9, 11, 13, 25, 49, 100, 1000, 10000, 100000, 1000000]:
        lip = lipschitz_descent_depth(d)
        hur = hurwitz_descent_depth(d)

        # Compute actual depth for small d
        actual = "—"
        if d <= 100:
            quads_at_d = [(a,b,c,d) for a in range(d+1) for b in range(a,d+1)
                          for c in range(b,d+1)
                          if a*a+b*b+c*c == d*d and
                          math.gcd(math.gcd(a,b), math.gcd(c,d)) == 1]
            if quads_at_d:
                depths = [len(descent_chain(*q))-1 for q in quads_at_d]
                actual = str(max(depths))

        ratio = lip / hur if hur > 0 else float('inf')
        print(f"{d:>8} | {lip:>11} | {hur:>12} | {actual:>13} | {ratio:>6.2f}")

    print("\nConclusion: Hurwitz descent is ~2.4× shallower (log(4/3)/log(2) ≈ 2.41)")


def demo_q3_octonion():
    """Question 3: Octonion obstruction."""
    check_octonion_obstruction()

    print("\nComparison of norm values:")
    print(f"  Quadruples:  η(1,1,1,1) = 1+1+1-1 = 2  → divide by 1 → always integral")
    print(f"  8-tuples:    η(1,...,1) = 7-1 = 6       → divide by 3 → NOT always integral")
    print(f"\nAssociativity comparison:")
    print(f"  Quaternions: associative     → tree structure OK")
    print(f"  Octonions:   non-associative → tree structure BROKEN")


def demo_q4_quantum():
    """Question 4: Quantum gate synthesis."""
    print("\n" + "=" * 60)
    print("QUESTION 4: Quantum Gate Synthesis via Descent")
    print("=" * 60)

    print(f"\n{'d':>4} | {'r₄(d)':>6} | {'Angular density':>16} | {'Gate depth':>11}")
    print("-" * 50)
    for d in range(1, 21):
        r4_val = r4(d)
        density = angular_density(d)
        depth = hurwitz_descent_depth(d)
        print(f"{d:>4} | {r4_val:>6} | {density:>16.4f} | {depth:>11}")

    print("\nSolovay-Kitaev interpretation:")
    print("  • r₄(d) integer quaternions at norm d → r₄(d) exact SU(2) rotations")
    print("  • Angular spacing ≈ C/√d for constant C")
    print("  • Gate decomposition depth = descent depth = O(log d)")
    print("  • To approximate to precision ε: choose d ~ 1/ε², giving O(log(1/ε)) gates")


def demo_q5_modular():
    """Question 5: Modular forms and r₃(n)."""
    print("\n" + "=" * 60)
    print("QUESTION 5: Modular Forms — r₃(n) and Three-Square Obstruction")
    print("=" * 60)

    print("\nr₃(n) values (connected to modular forms of weight 3/2):")
    print(f"{'n':>4} | {'r₃(n)':>6} | {'Obstructed?':>12} | {'Note':>30}")
    print("-" * 60)
    for n in range(1, 31):
        r3_val = r3(n)
        obstructed = is_three_square_obstructed(n)
        note = ""
        if obstructed:
            note = f"4^a(8b+7) form"
        elif n == 1:
            note = "±1 in one coord"
        elif r3_val == 0:
            note = "⚠ zero but not obstructed?"
        print(f"{n:>4} | {r3_val:>6} | {'YES' if obstructed else 'no':>12} | {note:>30}")

    print("\nThree-square obstruction pattern:")
    obstructed_list = [n for n in range(1, 100) if is_three_square_obstructed(n)]
    print(f"  Obstructed n < 100: {obstructed_list}")
    print(f"  Pattern: 7, 15, 23, 28, 31, 39, ... = 4^a(8b+7)")

    print("\nClass number connection (for squarefree n ≡ 1,2 mod 4):")
    print("  r₃(n) = 12·h(-4n)")
    for n in [1, 2, 3, 5, 6, 10, 13, 14]:
        r3_val = r3(n)
        h = r3_val // 12  # class number
        print(f"  r₃({n}) = {r3_val} → h(-{4*n}) = {h}")


def demo_quaternion_euler():
    """Demonstrate the quaternion-Euler parametrization."""
    print("\n" + "=" * 60)
    print("QUATERNION → EULER PARAMETRIZATION")
    print("=" * 60)

    test_quats = [
        Quaternion(1, 0, 0, 0),
        Quaternion(1, 1, 0, 0),
        Quaternion(1, 1, 1, 0),
        Quaternion(1, 1, 0, 1),
        Quaternion(1, 1, 1, 1),
        Quaternion(2, 1, 0, 0),
        Quaternion(1, 2, 1, 1),
    ]

    print(f"\n{'Quaternion':>25} | {'|α|²':>5} | {'Euler (a,b,c,d)':>20} | {'Check':>8}")
    print("-" * 70)
    for q in test_quats:
        e = euler_from_quat(q)
        check = e[0]**2 + e[1]**2 + e[2]**2 == e[3]**2
        print(f"{str(q):>25} | {q.sq_norm():>5} | {str(e):>20} | {'✓' if check else '✗':>8}")


if __name__ == "__main__":
    print("╔" + "═" * 58 + "╗")
    print("║  Quaternion Descent: Five Open Questions — Demos         ║")
    print("╚" + "═" * 58 + "╝")

    demo_quaternion_euler()
    demo_q1_branching()
    demo_q2_hurwitz()
    demo_q3_octonion()
    demo_q4_quantum()
    demo_q5_modular()

    print("\n" + "=" * 60)
    print("All demonstrations complete.")
    print("=" * 60)
