#!/usr/bin/env python3
"""
Quaternion-Descent Correspondence Demo

Demonstrates the connection between the Pythagorean quadruple descent tree
and the quaternion division algorithm.

Research Team PHOTON-4
"""

import math
from typing import Tuple, List, Optional
from dataclasses import dataclass


# ============================================================================
# Part 1: Integer Quaternion Arithmetic
# ============================================================================

@dataclass(frozen=True)
class IntQuat:
    """An integer quaternion a + bi + cj + dk"""
    re: int
    im_i: int
    im_j: int
    im_k: int

    def __repr__(self):
        parts = []
        if self.re != 0 or (self.im_i == 0 and self.im_j == 0 and self.im_k == 0):
            parts.append(str(self.re))
        for coeff, unit in [(self.im_i, 'i'), (self.im_j, 'j'), (self.im_k, 'k')]:
            if coeff == 1:
                parts.append(f'+{unit}' if parts else unit)
            elif coeff == -1:
                parts.append(f'-{unit}')
            elif coeff > 0:
                parts.append(f'+{coeff}{unit}' if parts else f'{coeff}{unit}')
            elif coeff < 0:
                parts.append(f'{coeff}{unit}')
        return ''.join(parts) if parts else '0'

    def __mul__(self, other: 'IntQuat') -> 'IntQuat':
        """Hamilton's quaternion multiplication"""
        a1, b1, c1, d1 = self.re, self.im_i, self.im_j, self.im_k
        a2, b2, c2, d2 = other.re, other.im_i, other.im_j, other.im_k
        return IntQuat(
            a1*a2 - b1*b2 - c1*c2 - d1*d2,
            a1*b2 + b1*a2 + c1*d2 - d1*c2,
            a1*c2 - b1*d2 + c1*a2 + d1*b2,
            a1*d2 + b1*c2 - c1*b2 + d1*a2
        )

    def __add__(self, other: 'IntQuat') -> 'IntQuat':
        return IntQuat(self.re + other.re, self.im_i + other.im_i,
                      self.im_j + other.im_j, self.im_k + other.im_k)

    def __neg__(self) -> 'IntQuat':
        return IntQuat(-self.re, -self.im_i, -self.im_j, -self.im_k)

    def __sub__(self, other: 'IntQuat') -> 'IntQuat':
        return self + (-other)

    def conj(self) -> 'IntQuat':
        """Quaternion conjugate"""
        return IntQuat(self.re, -self.im_i, -self.im_j, -self.im_k)

    def sqnorm(self) -> int:
        """Squared norm |q|² = a² + b² + c² + d²"""
        return self.re**2 + self.im_i**2 + self.im_j**2 + self.im_k**2

    def norm(self) -> float:
        """Norm |q|"""
        return math.sqrt(self.sqnorm())


# Special quaternions
SIGMA = IntQuat(1, 1, 1, 1)  # σ = 1+i+j+k
ONE = IntQuat(1, 0, 0, 0)
I = IntQuat(0, 1, 0, 0)
J = IntQuat(0, 0, 1, 0)
K = IntQuat(0, 0, 0, 1)


# ============================================================================
# Part 2: Euler Parametrization
# ============================================================================

def euler_param(q: IntQuat) -> Tuple[int, int, int, int]:
    """The Euler parametrization: quaternion → Pythagorean quadruple"""
    m, n, p, k = q.re, q.im_i, q.im_j, q.im_k
    a = m**2 + n**2 - p**2 - k**2
    b = 2 * (m*k + n*p)
    c = 2 * (n*k - m*p)
    d = m**2 + n**2 + p**2 + k**2  # = |q|²
    return (a, b, c, d)


def verify_euler(q: IntQuat) -> bool:
    """Verify that the Euler parametrization gives a valid quadruple"""
    a, b, c, d = euler_param(q)
    return a**2 + b**2 + c**2 == d**2


# ============================================================================
# Part 3: The R₁₁₁₁ Descent
# ============================================================================

def R1111(a: int, b: int, c: int, d: int) -> Tuple[int, int, int, int]:
    """Apply the reflection R₁₁₁₁"""
    return (d - b - c, d - a - c, d - a - b, 2*d - a - b - c)


def descent_step(a: int, b: int, c: int, d: int) -> Tuple[int, int, int, int]:
    """One step of the descent: reflect, abs, sort"""
    a1, b1, c1, d1 = R1111(a, b, c, d)
    spatial = sorted([abs(a1), abs(b1), abs(c1)])
    return (spatial[0], spatial[1], spatial[2], abs(d1))


def full_descent(a: int, b: int, c: int, d: int) -> List[Tuple[int, int, int, int]]:
    """Complete descent chain to the root"""
    chain = [(a, b, c, d)]
    while d > 1:
        prev = (a, b, c, d)
        a, b, c, d = descent_step(a, b, c, d)
        if (a, b, c, d) == prev:  # fixed point (non-primitive)
            break
        chain.append((a, b, c, d))
        if len(chain) > 100:
            break
    return chain


# ============================================================================
# Part 4: Quaternion Division Algorithm
# ============================================================================

def quat_nearest_round(q: IntQuat, divisor_norm: int) -> IntQuat:
    """Round a quaternion to the nearest integer quaternion (Lipschitz rounding)"""
    def nearest(x, n):
        return round(x / n)
    return IntQuat(
        nearest(q.re, divisor_norm),
        nearest(q.im_i, divisor_norm),
        nearest(q.im_j, divisor_norm),
        nearest(q.im_k, divisor_norm)
    )


def quat_div_sigma(alpha: IntQuat) -> Tuple[IntQuat, IntQuat]:
    """Divide alpha by sigma = 1+i+j+k using the Euclidean algorithm.
    Returns (quotient, remainder) such that alpha ≈ sigma * quotient + remainder
    and |remainder|² < |sigma|² = 4.
    """
    # Compute alpha * conj(sigma) / |sigma|²
    alpha_sigma_bar = alpha * SIGMA.conj()
    quotient = quat_nearest_round(alpha_sigma_bar, SIGMA.sqnorm())
    remainder = alpha - SIGMA * quotient
    return quotient, remainder


def quat_euclidean_descent(alpha: IntQuat, max_steps: int = 50) -> List[IntQuat]:
    """Run the quaternion Euclidean algorithm by repeatedly dividing by sigma"""
    chain = [alpha]
    current = alpha
    for _ in range(max_steps):
        if current.sqnorm() <= 1:
            break
        _, remainder = quat_div_sigma(current)
        if remainder.sqnorm() >= current.sqnorm():
            # Try dividing in the other order
            current_sigma_bar = current * SIGMA.conj()
            quotient = quat_nearest_round(current_sigma_bar, SIGMA.sqnorm())
            remainder = current - SIGMA * quotient
            if remainder.sqnorm() >= current.sqnorm():
                break
        current = remainder
        chain.append(current)
    return chain


# ============================================================================
# Part 5: Demonstrations
# ============================================================================

def demo_norm_multiplicativity():
    """Demonstrate that |pq|² = |p|²·|q|²"""
    print("=" * 60)
    print("DEMO 1: Quaternion Norm Multiplicativity")
    print("=" * 60)
    print()

    test_pairs = [
        (IntQuat(1, 2, 0, 1), IntQuat(2, 0, 1, 1)),
        (IntQuat(1, 1, 1, 0), IntQuat(0, 1, 1, 1)),
        (IntQuat(3, 1, 0, 2), IntQuat(1, 2, 3, 0)),
    ]

    for p, q in test_pairs:
        pq = p * q
        print(f"  p = {p}, |p|² = {p.sqnorm()}")
        print(f"  q = {q}, |q|² = {q.sqnorm()}")
        print(f"  pq = {pq}, |pq|² = {pq.sqnorm()}")
        print(f"  |p|²·|q|² = {p.sqnorm() * q.sqnorm()}")
        assert pq.sqnorm() == p.sqnorm() * q.sqnorm()
        print(f"  ✓ |pq|² = |p|²·|q|²")
        print()


def demo_euler_parametrization():
    """Demonstrate the Euler parametrization via quaternions"""
    print("=" * 60)
    print("DEMO 2: Euler Parametrization (Quaternion → Quadruple)")
    print("=" * 60)
    print()

    quaternions = [
        IntQuat(1, 0, 0, 0),  # → root
        IntQuat(1, 1, 0, 1),  # → (1, 2, 2, 3)
        IntQuat(1, 1, 1, 0),  # → (1, 2, -2, 3)
        IntQuat(1, 1, 1, 1),  # → σ itself
        IntQuat(2, 1, 0, 1),  # → larger
        IntQuat(1, 2, 1, 1),  # → (3, 4, 2, ?)
    ]

    for q in quaternions:
        quad = euler_param(q)
        a, b, c, d = quad
        valid = a**2 + b**2 + c**2 == d**2
        sorted_abs = tuple(sorted([abs(a), abs(b), abs(c)]) + [d])
        print(f"  α = {q}, |α|² = {q.sqnorm()}")
        print(f"    → quadruple: ({a}, {b}, {c}, {d})")
        print(f"    → sorted abs: {sorted_abs}")
        print(f"    → {a}² + {b}² + {c}² = {a**2} + {b**2} + {c**2} = {a**2+b**2+c**2}")
        print(f"    → {d}² = {d**2}")
        print(f"    → valid: {'✓' if valid else '✗'}")
        assert valid
        print()


def demo_descent_vs_division():
    """Show the parallel between quadruple descent and quaternion division"""
    print("=" * 60)
    print("DEMO 3: Descent Tree ↔ Quaternion Division")
    print("=" * 60)
    print()

    # Start with some quaternions and show their descent chains
    test_quats = [
        IntQuat(1, 1, 0, 1),   # → (1, 2, 2, 3)
        IntQuat(1, 2, 1, 1),   # → d = 7
        IntQuat(2, 1, 1, 1),   # → d = 7
        IntQuat(1, 2, 2, 0),   # → d = 9
    ]

    for q in test_quats:
        quad = euler_param(q)
        a, b, c, d = quad
        sa, sb, sc = sorted([abs(a), abs(b), abs(c)])

        print(f"  Quaternion α = {q}, |α|² = {q.sqnorm()}")
        print(f"  Euler quadruple: ({a}, {b}, {c}, {d})")
        print(f"  Sorted: ({sa}, {sb}, {sc}, {d})")

        # Quadruple descent
        chain = full_descent(sa, sb, sc, d)
        print(f"  Quadruple descent: ", end="")
        print(" → ".join(f"({a},{b},{c},{d})" for a,b,c,d in chain))

        # Quaternion division
        qchain = quat_euclidean_descent(q)
        print(f"  Quaternion norms: ", end="")
        print(" → ".join(f"|{q}|²={q.sqnorm()}" for q in qchain))
        print()


def demo_sigma_properties():
    """Demonstrate properties of σ = 1+i+j+k"""
    print("=" * 60)
    print("DEMO 4: Properties of σ = 1+i+j+k")
    print("=" * 60)
    print()

    print(f"  σ = {SIGMA}")
    print(f"  |σ|² = {SIGMA.sqnorm()}")
    print(f"  σ̄ = {SIGMA.conj()}")
    print(f"  σ·σ̄ = {SIGMA * SIGMA.conj()}")
    print(f"  σ² = {SIGMA * SIGMA}")
    print()

    # Minkowski vs quaternion norm
    s = (1, 1, 1, 1)
    eta_ss = s[0]**2 + s[1]**2 + s[2]**2 - s[3]**2
    print(f"  Minkowski vector s = (1,1,1,1)")
    print(f"  η(s,s) = 1² + 1² + 1² − 1² = {eta_ss}")
    print(f"  |σ|² = {SIGMA.sqnorm()}")
    print(f"  Ratio |σ|² / η(s,s) = {SIGMA.sqnorm()}/{eta_ss} = {SIGMA.sqnorm()/eta_ss}")
    print()

    # σ scales norms by 4
    test_quats = [IntQuat(1,0,0,0), IntQuat(1,1,0,0), IntQuat(1,1,1,0)]
    for q in test_quats:
        sq = SIGMA * q
        print(f"  α = {q}, |α|² = {q.sqnorm()}")
        print(f"  σ·α = {sq}, |σ·α|² = {sq.sqnorm()}")
        print(f"  4·|α|² = {4 * q.sqnorm()}")
        assert sq.sqnorm() == 4 * q.sqnorm()
        print(f"  ✓ |σ·α|² = 4·|α|²")
        print()


def demo_four_square_identity():
    """Demonstrate Euler's four-square identity as norm multiplicativity"""
    print("=" * 60)
    print("DEMO 5: Euler's Four-Square Identity")
    print("=" * 60)
    print()

    a1, b1, c1, d1 = 1, 2, 3, 4
    a2, b2, c2, d2 = 5, 6, 7, 8

    lhs = (a1**2 + b1**2 + c1**2 + d1**2) * (a2**2 + b2**2 + c2**2 + d2**2)

    # The quaternion product components
    r1 = a1*a2 - b1*b2 - c1*c2 - d1*d2
    r2 = a1*b2 + b1*a2 + c1*d2 - d1*c2
    r3 = a1*c2 - b1*d2 + c1*a2 + d1*b2
    r4 = a1*d2 + b1*c2 - c1*b2 + d1*a2

    rhs = r1**2 + r2**2 + r3**2 + r4**2

    print(f"  (a₁,b₁,c₁,d₁) = ({a1},{b1},{c1},{d1})")
    print(f"  (a₂,b₂,c₂,d₂) = ({a2},{b2},{c2},{d2})")
    print()
    print(f"  LHS = ({a1}²+{b1}²+{c1}²+{d1}²) × ({a2}²+{b2}²+{c2}²+{d2}²)")
    print(f"       = {a1**2+b1**2+c1**2+d1**2} × {a2**2+b2**2+c2**2+d2**2}")
    print(f"       = {lhs}")
    print()
    print(f"  Product components: ({r1}, {r2}, {r3}, {r4})")
    print(f"  RHS = {r1}² + {r2}² + {r3}² + {r4}²")
    print(f"       = {r1**2} + {r2**2} + {r3**2} + {r4**2}")
    print(f"       = {rhs}")
    print()
    assert lhs == rhs
    print(f"  ✓ Four-square identity verified!")
    print()

    # Same thing via quaternions
    p = IntQuat(a1, b1, c1, d1)
    q = IntQuat(a2, b2, c2, d2)
    pq = p * q
    print(f"  As quaternions: p = {p}, q = {q}")
    print(f"  pq = {pq}")
    print(f"  |p|² = {p.sqnorm()}, |q|² = {q.sqnorm()}, |pq|² = {pq.sqnorm()}")
    assert pq.sqnorm() == p.sqnorm() * q.sqnorm()
    print(f"  ✓ Norm multiplicativity!")


def demo_primitive_quadruples():
    """Show all primitive quadruples with d ≤ 25 and their quaternion sources"""
    print()
    print("=" * 60)
    print("DEMO 6: Primitive Quadruples and Quaternion Sources")
    print("=" * 60)
    print()

    N = 25
    quads = []
    for d in range(1, N + 1):
        for c in range(0, d + 1):
            for b in range(0, c + 1):
                for a in range(0, b + 1):
                    if a**2 + b**2 + c**2 == d**2:
                        g = math.gcd(math.gcd(a, b), math.gcd(c, d))
                        if g == 1:
                            quads.append((a, b, c, d))

    print(f"  Found {len(quads)} primitive quadruples with d ≤ {N}:")
    print()
    print(f"  {'Quadruple':<20} {'d':>4} {'Descent depth':>14} {'Root':>12}")
    print(f"  {'-'*20} {'-'*4} {'-'*14} {'-'*12}")

    for quad in quads:
        a, b, c, d = quad
        chain = full_descent(a, b, c, d)
        root = chain[-1]
        depth = len(chain) - 1
        print(f"  ({a:>2},{b:>2},{c:>2},{d:>2}){'':<8} {d:>4} {depth:>14} ({root[0]},{root[1]},{root[2]},{root[3]})")


def demo_descent_tree_visual():
    """Print a text visualization of the first few levels of the descent tree"""
    print()
    print("=" * 60)
    print("DEMO 7: Descent Tree (Text Visualization)")
    print("=" * 60)
    print()

    N = 30
    quads = []
    for d in range(1, N + 1):
        for c in range(0, d + 1):
            for b in range(0, c + 1):
                for a in range(0, b + 1):
                    if a**2 + b**2 + c**2 == d**2:
                        g = math.gcd(math.gcd(a, b), math.gcd(c, d))
                        if g == 1:
                            quads.append((a, b, c, d))

    # Build parent map
    parent_map = {}
    for quad in quads:
        a, b, c, d = quad
        if d == 1:
            parent_map[quad] = None
        else:
            chain = full_descent(a, b, c, d)
            if len(chain) >= 2:
                parent_map[quad] = chain[1]

    # Print tree
    def print_tree(node, prefix="", is_last=True):
        connector = "└── " if is_last else "├── "
        print(f"  {prefix}{connector}({node[0]},{node[1]},{node[2]},{node[3]})")
        children = [q for q in quads if parent_map.get(q) == node]
        children.sort(key=lambda x: x[3])
        for i, child in enumerate(children):
            extension = "    " if is_last else "│   "
            print_tree(child, prefix + extension, i == len(children) - 1)

    root = (0, 0, 1, 1)
    print(f"  Root: (0,0,1,1)")
    children = [q for q in quads if parent_map.get(q) == root]
    children.sort(key=lambda x: x[3])
    for i, child in enumerate(children):
        print_tree(child, "  ", i == len(children) - 1)


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  QUATERNION-DESCENT CORRESPONDENCE DEMO                 ║")
    print("║  Research Team PHOTON-4                                 ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    demo_norm_multiplicativity()
    demo_euler_parametrization()
    demo_descent_vs_division()
    demo_sigma_properties()
    demo_four_square_identity()
    demo_primitive_quadruples()
    demo_descent_tree_visual()

    print()
    print("All demos completed successfully! ✓")
