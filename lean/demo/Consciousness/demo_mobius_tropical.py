#!/usr/bin/env python3
"""
Demo: Möbius Self-Observation & Tropical Consciousness
========================================================

Demonstrates:
1. Möbius transformations as perspective shifts
2. Fixed points as awareness attractors
3. Binocular depth from paired Möbius transformations
4. Tropical (max-plus) consciousness dynamics
5. Cayley-Dickson consciousness dimensions
"""

import numpy as np
from typing import Tuple

class MobiusTrans:
    """A Möbius transformation m(z) = (az + b) / (cz + d)."""

    def __init__(self, a, b, c, d):
        self.a = complex(a)
        self.b = complex(b)
        self.c = complex(c)
        self.d = complex(d)
        assert abs(a * d - b * c) > 1e-10, "Determinant must be nonzero"

    def __call__(self, z):
        z = complex(z)
        denom = self.c * z + self.d
        if abs(denom) < 1e-15:
            return complex('inf')
        return (self.a * z + self.b) / denom

    def fixed_points(self):
        """Find fixed points: cz² + (d-a)z - b = 0."""
        if abs(self.c) < 1e-15:
            # Linear case: (a-d)z + b = 0
            if abs(self.a - self.d) < 1e-15:
                return []
            return [self.b / (self.d - self.a)]
        disc = (self.d - self.a)**2 + 4 * self.b * self.c
        sqrt_disc = disc**0.5
        z1 = ((self.a - self.d) + sqrt_disc) / (2 * self.c)
        z2 = ((self.a - self.d) - sqrt_disc) / (2 * self.c)
        if abs(z1 - z2) < 1e-10:
            return [z1]
        return [z1, z2]

    def __repr__(self):
        return f"Möbius({self.a}, {self.b}, {self.c}, {self.d})"


def cross_ratio(z1, z2, z3, z4):
    """Compute the cross-ratio (z1-z3)(z2-z4) / ((z1-z4)(z2-z3))."""
    return ((z1-z3) * (z2-z4)) / ((z1-z4) * (z2-z3))


def demo_mobius_fixed_points():
    """Demo: Fixed points of Möbius transformations."""
    print("=" * 60)
    print("Demo: Möbius Transformation Fixed Points")
    print("=" * 60)
    print()

    examples = [
        ("Rotation by 90°", MobiusTrans(0, -1, 1, 0)),
        ("Scaling by 2", MobiusTrans(2, 0, 0, 1)),
        ("Translation by 1", MobiusTrans(1, 1, 0, 1)),
        ("Inversion", MobiusTrans(0, 1, 1, 0)),
        ("Parabolic", MobiusTrans(1, 1, 0, 1)),
    ]

    for name, m in examples:
        fps = m.fixed_points()
        print(f"  {name}: {m}")
        if fps:
            for fp in fps:
                verify = m(fp)
                print(f"    Fixed point: z = {fp:.4f}")
                print(f"    Verify: m(z) = {verify:.4f}, |m(z)-z| = {abs(verify-fp):.2e}")
        else:
            print(f"    No finite fixed points (only ∞)")
        print()


def demo_cross_ratio_invariance():
    """Demo: Cross-ratio is invariant under Möbius transformations."""
    print("=" * 60)
    print("Demo: Cross-Ratio Invariance")
    print("=" * 60)
    print()

    z1, z2, z3, z4 = 1+0j, 2+1j, 0-1j, 3+2j
    cr_original = cross_ratio(z1, z2, z3, z4)
    print(f"Points: z1={z1}, z2={z2}, z3={z3}, z4={z4}")
    print(f"Cross-ratio: {cr_original:.6f}")

    m = MobiusTrans(2, 1, 1, 3)
    w1, w2, w3, w4 = m(z1), m(z2), m(z3), m(z4)
    cr_transformed = cross_ratio(w1, w2, w3, w4)
    print(f"\nAfter Möbius transform {m}:")
    print(f"Points: w1={w1:.4f}, w2={w2:.4f}, w3={w3:.4f}, w4={w4:.4f}")
    print(f"Cross-ratio: {cr_transformed:.6f}")
    print(f"Difference: {abs(cr_original - cr_transformed):.2e}")
    print(f"Cross-ratio preserved? {abs(cr_original - cr_transformed) < 1e-10}")
    print()


def demo_binocular_depth():
    """Demo: Binocular self-observation depth."""
    print("=" * 60)
    print("Demo: Binocular Self-Observation Depth")
    print("=" * 60)
    print()

    left_eye = MobiusTrans(1, 0.5, 0, 1)
    right_eye = MobiusTrans(1, -0.5, 0, 1)

    print(f"Left eye:  {left_eye}")
    print(f"Right eye: {right_eye}")
    print()

    test_points = [0, 1, -1, 1j, 2+1j]
    print(f"{'Point':>10} {'Left view':>15} {'Right view':>15} {'Depth':>12}")
    print(f"{'-----':>10} {'---------':>15} {'----------':>15} {'-----':>12}")
    for z in test_points:
        lv = left_eye(z)
        rv = right_eye(z)
        depth = abs(lv - rv)
        print(f"{str(z):>10} {str(lv)[:15]:>15} {str(rv)[:15]:>15} {depth:>12.4f}")

    print()
    # Identical eyes = zero depth
    same = MobiusTrans(1, 1, 0, 1)
    for z in test_points[:3]:
        depth = abs(same(z) - same(z))
        print(f"Identical eyes at z={z}: depth = {depth:.10f}")
    print("When both eyes are the same, depth is always 0 ✓")
    print()


def demo_tropical_dynamics():
    """Demo: Tropical (max-plus) consciousness dynamics."""
    print("=" * 60)
    print("Demo: Tropical Consciousness Dynamics")
    print("=" * 60)
    print()

    n = 4
    # Tropical influence matrix
    M = np.array([
        [0,  3,  -1, 2],
        [1,  0,   4, -2],
        [2, -1,   0, 3],
        [-2, 1,   2, 0]
    ], dtype=float)

    print("Tropical influence matrix (higher = stronger influence):")
    for i, row in enumerate(M):
        print(f"  State {i}: {row}")

    # Initial awareness
    v = np.array([1.0, 0.0, 2.0, -1.0])
    print(f"\nInitial awareness: {v}")

    # Tropical matrix-vector multiply
    def trop_matvec(M, v):
        n = len(v)
        result = np.full(n, -np.inf)
        for i in range(n):
            for j in range(n):
                result[i] = max(result[i], M[i, j] + v[j])
        return result

    # Iterate
    print("\nTropical iteration (max-plus dynamics):")
    print(f"{'Step':>6} {'State 0':>10} {'State 1':>10} {'State 2':>10} {'State 3':>10} {'Max':>8}")
    print(f"{'----':>6} {'-------':>10} {'-------':>10} {'-------':>10} {'-------':>10} {'---':>8}")

    state = v.copy()
    for step in range(10):
        print(f"{step:>6} {state[0]:>10.2f} {state[1]:>10.2f} {state[2]:>10.2f} {state[3]:>10.2f} {max(state):>8.2f}")
        state = trop_matvec(M, state)

    print()
    print("Note: the max grows linearly — this is the tropical eigenvalue!")
    print("It represents the dominant 'frequency' of consciousness.")
    print()


def demo_cayley_dickson_ladder():
    """Demo: Cayley-Dickson consciousness ladder properties."""
    print("=" * 60)
    print("Demo: Cayley-Dickson Consciousness Ladder")
    print("=" * 60)
    print()

    # Demonstrate non-commutativity with quaternions
    print("Quaternion non-commutativity (ℍ-consciousness):")
    # i*j = k, j*i = -k in quaternions
    # We'll use (w, x, y, z) representation
    def qmul(q1, q2):
        """Quaternion multiplication."""
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2
        return (
            w1*w2 - x1*x2 - y1*y2 - z1*z2,
            w1*x2 + x1*w2 + y1*z2 - z1*y2,
            w1*y2 - x1*z2 + y1*w2 + z1*x2,
            w1*z2 + x1*y2 - y1*x2 + z1*w2
        )

    i = (0, 1, 0, 0)
    j = (0, 0, 1, 0)
    k = (0, 0, 0, 1)

    ij = qmul(i, j)
    ji = qmul(j, i)
    print(f"  i = {i}")
    print(f"  j = {j}")
    print(f"  i * j = {ij}  (= k)")
    print(f"  j * i = {ji}  (= -k)")
    print(f"  i * j ≠ j * i? {ij != ji} ✓")
    print()
    print("In ℍ-consciousness, the ORDER of observations matters:")
    print("  Seeing A then B ≠ Seeing B then A")
    print()

    # Phase awareness
    print("Complex phase awareness (ℂ-consciousness):")
    for theta_deg in [0, 45, 90, 180, 270]:
        theta = np.radians(theta_deg)
        phase = np.exp(1j * theta)
        print(f"  θ = {theta_deg:>3}°: phase = {phase.real:+.3f} {phase.imag:+.3f}i, |phase| = {abs(phase):.4f}")
    print()
    print("Phase awareness has unit magnitude — only direction of attention varies.")
    print()

if __name__ == "__main__":
    print("╔" + "═" * 58 + "╗")
    print("║  MÖBIUS & TROPICAL CONSCIOUSNESS — DEMOS               ║")
    print("╚" + "═" * 58 + "╝")
    print()

    demo_mobius_fixed_points()
    demo_cross_ratio_invariance()
    demo_binocular_depth()
    demo_tropical_dynamics()
    demo_cayley_dickson_ladder()
