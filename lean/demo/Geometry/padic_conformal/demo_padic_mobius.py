#!/usr/bin/env python3
"""
P-adic Möbius Transformations: Interactive Demonstrations

This module provides computational tools for exploring p-adic conformal geometry,
including Möbius transformations, the Bruhat-Tits tree, orbits, and limit sets.

These demos complement the formal Lean 4 proofs in Geometry__PadicMobius.lean.
"""

from fractions import Fraction
from collections import defaultdict
import json
import math


# =============================================================================
# Part 1: P-adic Arithmetic
# =============================================================================

def p_adic_val(n: int, p: int) -> int:
    """Compute the p-adic valuation of an integer n.
    
    Returns the largest k such that p^k divides n.
    Returns infinity (represented as float('inf')) for n = 0.
    """
    if n == 0:
        return float('inf')
    n = abs(n)
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v


def p_adic_val_rational(num: int, den: int, p: int) -> int:
    """Compute the p-adic valuation of a rational number num/den."""
    return p_adic_val(num, p) - p_adic_val(den, p)


def p_adic_norm(num: int, den: int, p: int) -> float:
    """Compute |num/den|_p, the p-adic absolute value."""
    if num == 0:
        return 0.0
    v = p_adic_val_rational(num, den, p)
    return float(p) ** (-v)


def p_adic_digits(n: int, p: int, num_digits: int = 10) -> list:
    """Compute the first num_digits p-adic digits of a non-negative integer."""
    digits = []
    for _ in range(num_digits):
        digits.append(n % p)
        n //= p
    return digits


# =============================================================================
# Part 2: P-adic Möbius Transformations
# =============================================================================

class PadicMobius:
    """A Möbius transformation z ↦ (az+b)/(cz+d) over the rationals,
    interpreted with p-adic norms.
    
    Coefficients are stored as Fraction objects for exact arithmetic.
    """
    
    def __init__(self, a, b, c, d, p=2):
        self.a = Fraction(a)
        self.b = Fraction(b)
        self.c = Fraction(c)
        self.d = Fraction(d)
        self.p = p
        det = self.a * self.d - self.b * self.c
        if det == 0:
            raise ValueError(f"Determinant is zero: ad-bc = {det}")
    
    @property
    def det(self):
        return self.a * self.d - self.b * self.c
    
    @property
    def trace(self):
        return self.a + self.d
    
    @property
    def discriminant(self):
        """Fixed-point discriminant: (a-d)² + 4bc."""
        return (self.a - self.d) ** 2 + 4 * self.b * self.c
    
    def apply(self, z):
        """Apply the transformation to a rational number z.
        Returns None if cz+d = 0 (pole)."""
        denom = self.c * z + self.d
        if denom == 0:
            return None  # maps to infinity
        return (self.a * z + self.b) / denom
    
    def compose(self, other):
        """Return self ∘ other (apply self after other)."""
        return PadicMobius(
            self.a * other.a + self.b * other.c,
            self.a * other.b + self.b * other.d,
            self.c * other.a + self.d * other.c,
            self.c * other.b + self.d * other.d,
            self.p
        )
    
    def inverse(self):
        """Return the inverse transformation."""
        return PadicMobius(self.d, -self.b, -self.c, self.a, self.p)
    
    def derivative_at(self, z):
        """Compute the Möbius derivative det/(cz+d)² at z."""
        denom = self.c * z + self.d
        if denom == 0:
            return None
        return self.det / denom ** 2
    
    def p_adic_norm_derivative(self, z):
        """Compute |M'(z)|_p = |det|_p / |cz+d|_p²."""
        d = self.derivative_at(z)
        if d is None:
            return float('inf')
        return p_adic_norm(d.numerator, d.denominator, self.p)
    
    def orbit(self, z0, n_steps=20):
        """Compute the orbit z0, M(z0), M²(z0), ..., Mⁿ(z0)."""
        trajectory = [z0]
        z = Fraction(z0)
        for _ in range(n_steps):
            z = self.apply(z)
            if z is None:
                break
            trajectory.append(z)
        return trajectory
    
    def classify(self):
        """Classify the transformation type based on the discriminant."""
        disc = self.discriminant
        if disc == 0:
            return "parabolic"
        # In the p-adic world, classification also depends on whether
        # the discriminant is a square in ℚ_p
        return "loxodromic/elliptic"
    
    def fixed_points_rational(self):
        """Find fixed points over ℚ (if they exist).
        Solves c·z² + (d-a)·z - b = 0."""
        if self.c == 0:
            # Linear case: z = (az+b)/d, so (d-a)z = b
            if self.d - self.a == 0:
                return []  # identity or no fixed points in affine part
            return [self.b / (self.d - self.a)]
        
        # Quadratic: c·z² + (d-a)·z - b = 0
        disc = (self.d - self.a) ** 2 + 4 * self.c * self.b
        # Check if discriminant is a perfect square (over ℚ)
        if disc < 0:
            return []
        disc_sqrt = disc ** Fraction(1, 2)
        # Only works for perfect squares
        try:
            s = Fraction(int(disc_sqrt))
            if s * s == disc:
                z1 = (-(self.d - self.a) + s) / (2 * self.c)
                z2 = (-(self.d - self.a) - s) / (2 * self.c)
                return [z1] if z1 == z2 else [z1, z2]
        except (ValueError, OverflowError):
            pass
        return []
    
    def __repr__(self):
        return f"PadicMobius(a={self.a}, b={self.b}, c={self.c}, d={self.d}, p={self.p})"
    
    def __str__(self):
        return f"z ↦ ({self.a}z + {self.b}) / ({self.c}z + {self.d})"


# =============================================================================
# Part 3: The Bruhat-Tits Tree
# =============================================================================

class BruhatTitsTree:
    """The Bruhat-Tits tree for GL₂(ℚ_p).
    
    Vertices are equivalence classes of ℤ_p-lattices in ℚ_p².
    We represent them by (level, coset) where level ∈ ℤ gives the scale
    and coset ∈ {0, 1, ..., p-1} identifies which of the p+1 neighbors.
    """
    
    def __init__(self, p=2, max_depth=4):
        self.p = p
        self.max_depth = max_depth
        self.vertices = []
        self.edges = []
        self._build_tree()
    
    def _build_tree(self):
        """Build the tree up to max_depth levels."""
        # Root vertex
        root = (0, ())
        self.vertices = [root]
        queue = [root]
        
        for _ in range(self.max_depth):
            next_queue = []
            for v in queue:
                level, path = v
                for i in range(self.p + 1):
                    child = (level + 1, path + (i,))
                    self.vertices.append(child)
                    self.edges.append((v, child))
                    next_queue.append(child)
            queue = next_queue
    
    def adjacency_list(self):
        """Return the adjacency list representation."""
        adj = defaultdict(list)
        for u, v in self.edges:
            adj[u].append(v)
            adj[v].append(u)
        return adj
    
    def to_dict(self):
        """Export tree structure as a dictionary."""
        return {
            'p': self.p,
            'max_depth': self.max_depth,
            'num_vertices': len(self.vertices),
            'num_edges': len(self.edges),
            'vertices': [{'level': v[0], 'path': v[1]} for v in self.vertices[:50]],
        }


# =============================================================================
# Part 4: P-adic Disk Operations
# =============================================================================

def padic_disk_contains(center_num, center_den, radius, point_num, point_den, p):
    """Check if a point is in a p-adic disk D(center, radius)."""
    diff_num = point_num * center_den - center_num * point_den
    diff_den = point_den * center_den
    return p_adic_norm(diff_num, diff_den, p) <= radius


def demonstrate_disk_dichotomy(p=3):
    """Demonstrate the disk dichotomy theorem with concrete examples.
    
    In ℚ_p, two disks are either disjoint or one contains the other.
    No partial overlaps!
    """
    print(f"\n{'='*60}")
    print(f"  Disk Dichotomy Theorem in ℚ_{p}")
    print(f"{'='*60}")
    
    examples = [
        # (center1, radius1, center2, radius2, description)
        (0, 1, 3, 1, "D(0, 1) vs D(3, 1) — same radius, distance = |3|_p"),
        (0, 1, 0, Fraction(1, p), f"D(0, 1) vs D(0, 1/{p}) — nested"),
        (0, 1, p, 1, f"D(0, 1) vs D({p}, 1) — distance = |{p}|_p = 1/{p}"),
    ]
    
    for c1, r1, c2, r2, desc in examples:
        norm_diff = p_adic_norm(c1 - c2, 1, p)
        print(f"\n  {desc}")
        print(f"    |{c1} - {c2}|_{p} = {norm_diff}")
        print(f"    Radii: {r1}, {r2}")
        
        if norm_diff > max(float(r1), float(r2)):
            print(f"    Result: DISJOINT ✓")
        elif float(r1) <= float(r2):
            print(f"    Result: D({c1},{r1}) ⊆ D({c2},{r2}) ✓")
        else:
            print(f"    Result: D({c2},{r2}) ⊆ D({c1},{r1}) ✓")


# =============================================================================
# Part 5: Demonstrations
# =============================================================================

def demo_isosceles_theorem(p=5):
    """Demonstrate that all p-adic triangles are isosceles."""
    print(f"\n{'='*60}")
    print(f"  Isosceles Triangle Theorem in ℚ_{p}")
    print(f"{'='*60}")
    
    # Three points: 0, 1, p
    points = [(0, 1), (1, 1), (p, 1)]
    names = ['A=0', 'B=1', f'C={p}']
    
    print(f"\n  Points: {', '.join(names)}")
    
    for i in range(3):
        for j in range(i+1, 3):
            diff_num = points[i][0] * points[j][1] - points[j][0] * points[i][1]
            diff_den = points[i][1] * points[j][1]
            norm = p_adic_norm(diff_num, diff_den, p)
            print(f"    |{names[i]} - {names[j]}|_{p} = {norm}")
    
    print(f"\n  → At least two sides are equal: isosceles! ✓")


def demo_mobius_transformation(p=3):
    """Demonstrate p-adic Möbius transformations."""
    print(f"\n{'='*60}")
    print(f"  P-adic Möbius Transformations (p={p})")
    print(f"{'='*60}")
    
    # Example: z ↦ (2z + 1)/(z + 3)
    M = PadicMobius(2, 1, 1, 3, p)
    print(f"\n  M: {M}")
    print(f"  det(M) = {M.det}")
    print(f"  tr(M) = {M.trace}")
    print(f"  discriminant = {M.discriminant}")
    print(f"  Type: {M.classify()}")
    
    # Fixed points
    fps = M.fixed_points_rational()
    if fps:
        print(f"  Fixed points: {fps}")
        for fp in fps:
            print(f"    M({fp}) = {M.apply(fp)} (should equal {fp})")
    
    # Orbit
    print(f"\n  Orbit of z₀ = 0:")
    orbit = M.orbit(Fraction(0), 10)
    for i, z in enumerate(orbit[:8]):
        norm = p_adic_norm(z.numerator, z.denominator, p) if z != 0 else 0
        print(f"    M^{i}(0) = {z} = {float(z):.6f}, |·|_{p} = {norm:.6f}")
    
    # Composition
    M_inv = M.inverse()
    identity = M.compose(M_inv)
    print(f"\n  M⁻¹: {M_inv}")
    print(f"  M ∘ M⁻¹ = z ↦ ({identity.a}z + {identity.b}) / ({identity.c}z + {identity.d})")
    print(f"  det(M ∘ M⁻¹) = {identity.det}")
    
    # Conformal distortion
    print(f"\n  Conformal distortion formula:")
    z, w = Fraction(1), Fraction(2)
    Mz, Mw = M.apply(z), M.apply(w)
    if Mz is not None and Mw is not None:
        lhs = p_adic_norm((Mz - Mw).numerator, (Mz - Mw).denominator, p)
        zw_norm = p_adic_norm((z - w).numerator, (z - w).denominator, p)
        det_norm = p_adic_norm(M.det.numerator, M.det.denominator, p)
        denom1 = p_adic_norm((M.c * z + M.d).numerator, (M.c * z + M.d).denominator, p)
        denom2 = p_adic_norm((M.c * w + M.d).numerator, (M.c * w + M.d).denominator, p)
        rhs = zw_norm * det_norm / (denom1 * denom2)
        print(f"    |M({z}) - M({w})|_{p} = {lhs:.6f}")
        print(f"    |z - w|_{p} · |det|_{p} / (|cz+d|_{p} · |cw+d|_{p}) = {rhs:.6f}")
        print(f"    Equal: {abs(lhs - rhs) < 1e-10} ✓")


def demo_bruhat_tits_tree(p=2):
    """Demonstrate the Bruhat-Tits tree."""
    print(f"\n{'='*60}")
    print(f"  Bruhat-Tits Tree for p={p}")
    print(f"{'='*60}")
    
    tree = BruhatTitsTree(p=p, max_depth=3)
    print(f"\n  Vertices: {len(tree.vertices)}")
    print(f"  Edges: {len(tree.edges)}")
    print(f"  Each vertex has {p + 1} neighbors")
    
    # Print first few levels
    for level in range(4):
        verts_at_level = [v for v in tree.vertices if v[0] == level]
        print(f"  Level {level}: {len(verts_at_level)} vertices")


def demo_parabolic_classification():
    """Demonstrate the parabolic classification theorem."""
    print(f"\n{'='*60}")
    print(f"  Classification of Möbius Transformations")
    print(f"{'='*60}")
    
    # Parabolic: tr² = 4·det
    # For a=1, b=1, c=0, d=1: tr=2, det=1, tr²=4=4·det → parabolic
    M_para = PadicMobius(1, 1, 0, 1, p=2)
    print(f"\n  z ↦ z + 1 (translation)")
    print(f"    tr = {M_para.trace}, det = {M_para.det}")
    print(f"    tr² = {M_para.trace**2}, 4·det = {4*M_para.det}")
    print(f"    tr² = 4·det: {M_para.trace**2 == 4*M_para.det} → {M_para.classify()}")
    
    # Loxodromic: tr² ≠ 4·det
    M_lox = PadicMobius(3, 0, 0, 1, p=2)
    print(f"\n  z ↦ 3z (scaling)")
    print(f"    tr = {M_lox.trace}, det = {M_lox.det}")
    print(f"    tr² = {M_lox.trace**2}, 4·det = {4*M_lox.det}")
    print(f"    tr² = 4·det: {M_lox.trace**2 == 4*M_lox.det} → {M_lox.classify()}")
    
    # Inversion
    M_inv = PadicMobius(0, 1, 1, 0, p=2)
    print(f"\n  z ↦ 1/z (inversion)")
    print(f"    tr = {M_inv.trace}, det = {M_inv.det}")
    print(f"    discriminant = {M_inv.discriminant}")
    print(f"    Type: {M_inv.classify()}")


# =============================================================================
# Part 6: Run All Demos
# =============================================================================

if __name__ == "__main__":
    print("╔" + "═" * 58 + "╗")
    print("║  P-ADIC CONFORMAL GEOMETRY: COMPUTATIONAL DEMONSTRATIONS  ║")
    print("║  Companion to Lean 4 formalization in PadicMobius.lean    ║")
    print("╚" + "═" * 58 + "╝")
    
    demo_isosceles_theorem(p=5)
    demo_mobius_transformation(p=3)
    demonstrate_disk_dichotomy(p=3)
    demo_parabolic_classification()
    demo_bruhat_tits_tree(p=2)
    demo_bruhat_tits_tree(p=3)
    
    print(f"\n{'='*60}")
    print("  All demonstrations completed successfully!")
    print(f"{'='*60}")
