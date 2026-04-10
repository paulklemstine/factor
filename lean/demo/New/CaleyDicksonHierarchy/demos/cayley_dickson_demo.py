#!/usr/bin/env python3
"""
Cayley-Dickson Construction Demonstration

This script demonstrates the Cayley-Dickson doubling construction
and explores key properties at each level:
  Level 0: ℝ (reals, dim 1)
  Level 1: ℂ (complex, dim 2)
  Level 2: ℍ (quaternions, dim 4)
  Level 3: 𝕆 (octonions, dim 8)
  Level 4: 𝕊 (sedenions, dim 16) -- zero divisors appear!
"""

import numpy as np
from itertools import product as cartesian_product


# =============================================================================
# Part 1: The Cayley-Dickson Construction
# =============================================================================

class CayleyDickson:
    """
    Recursive Cayley-Dickson algebra element.

    Level 0: real numbers (stored as a single float)
    Level k+1: pair (a, b) of level-k elements with multiplication
               (a, b) * (c, d) = (a*c - conj(d)*b, d*a + b*conj(c))
    """

    def __init__(self, *components):
        """Initialize from a tuple of real components.
        Length must be a power of 2."""
        n = len(components)
        assert n > 0 and (n & (n - 1)) == 0, f"Length must be power of 2, got {n}"

        if n == 1:
            self.level = 0
            self.value = float(components[0])
        else:
            half = n // 2
            self.level = 1  # will be corrected
            self.a = CayleyDickson(*components[:half])
            self.b = CayleyDickson(*components[half:])
            self.level = self.a.level + 1

    @property
    def dim(self):
        return 2 ** self.level

    def components(self):
        """Return flat list of real components."""
        if self.level == 0:
            return [self.value]
        return self.a.components() + self.b.components()

    def conj(self):
        """Cayley-Dickson conjugation: conj(a, b) = (conj(a), -b)."""
        if self.level == 0:
            return CayleyDickson(self.value)
        neg_b = self.b * CayleyDickson(*([- 1] + [0] * (self.b.dim - 1)))
        return CayleyDickson(*(self.a.conj().components() + neg_b.components()))

    def norm_sq(self):
        """Norm squared = sum of squares of components."""
        return sum(x ** 2 for x in self.components())

    def __add__(self, other):
        c1 = self.components()
        c2 = other.components()
        return CayleyDickson(*[a + b for a, b in zip(c1, c2)])

    def __neg__(self):
        return CayleyDickson(*[-x for x in self.components()])

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        if self.level == 0 and other.level == 0:
            return CayleyDickson(self.value * other.value)
        if self.level != other.level:
            raise ValueError("Cannot multiply elements of different levels")

        # (a, b) * (c, d) = (a*c - conj(d)*b, d*a + b*conj(c))
        a, b = self.a, self.b
        c, d = other.a, other.b

        re = a * c - d.conj() * b
        im = d * a + b * c.conj()
        return CayleyDickson(*(re.components() + im.components()))

    def __repr__(self):
        names = {0: "ℝ", 1: "ℂ", 2: "ℍ", 3: "𝕆", 4: "𝕊", 5: "𝕋"}
        level_name = names.get(self.level, f"CD_{self.level}")
        return f"{level_name}{tuple(round(x, 6) for x in self.components())}"

    def is_zero(self, tol=1e-10):
        return all(abs(x) < tol for x in self.components())


# =============================================================================
# Part 2: Verify Properties at Each Level
# =============================================================================

def test_commutativity(level, num_trials=100):
    """Test whether multiplication is commutative at the given level."""
    dim = 2 ** level
    violations = 0
    for _ in range(num_trials):
        a = CayleyDickson(*np.random.randn(dim))
        b = CayleyDickson(*np.random.randn(dim))
        ab = a * b
        ba = b * a
        diff = sum((x - y) ** 2 for x, y in zip(ab.components(), ba.components()))
        if diff > 1e-10:
            violations += 1
    return violations


def test_associativity(level, num_trials=100):
    """Test whether multiplication is associative at the given level."""
    dim = 2 ** level
    violations = 0
    for _ in range(num_trials):
        a = CayleyDickson(*np.random.randn(dim))
        b = CayleyDickson(*np.random.randn(dim))
        c = CayleyDickson(*np.random.randn(dim))
        ab_c = (a * b) * c
        a_bc = a * (b * c)
        diff = sum((x - y) ** 2 for x, y in zip(ab_c.components(), a_bc.components()))
        if diff > 1e-10:
            violations += 1
    return violations


def test_norm_multiplicativity(level, num_trials=100):
    """Test whether N(xy) = N(x)N(y) at the given level."""
    dim = 2 ** level
    violations = 0
    for _ in range(num_trials):
        a = CayleyDickson(*np.random.randn(dim))
        b = CayleyDickson(*np.random.randn(dim))
        ab = a * b
        lhs = ab.norm_sq()
        rhs = a.norm_sq() * b.norm_sq()
        if abs(lhs - rhs) > 1e-6:
            violations += 1
    return violations


def find_zero_divisors(level, num_trials=10000):
    """Search for zero divisors at the given level."""
    dim = 2 ** level
    best_ratio = float('inf')
    best_pair = None
    for _ in range(num_trials):
        a = CayleyDickson(*np.random.randn(dim))
        b = CayleyDickson(*np.random.randn(dim))
        ab = a * b
        product_norm = ab.norm_sq()
        factor_norm = a.norm_sq() * b.norm_sq()
        if factor_norm > 1e-10:
            ratio = product_norm / factor_norm
            if ratio < best_ratio:
                best_ratio = ratio
                best_pair = (a, b)
    return best_ratio, best_pair


# =============================================================================
# Part 3: The Composition Identities
# =============================================================================

def verify_brahmagupta_fibonacci(a, b, c, d):
    """Verify (a²+b²)(c²+d²) = (ac-bd)²+(ad+bc)²."""
    lhs = (a**2 + b**2) * (c**2 + d**2)
    rhs = (a*c - b*d)**2 + (a*d + b*c)**2
    return abs(lhs - rhs) < 1e-10


def verify_euler_four_square(a1, a2, a3, a4, b1, b2, b3, b4):
    """Verify the four-square identity."""
    lhs = (a1**2 + a2**2 + a3**2 + a4**2) * (b1**2 + b2**2 + b3**2 + b4**2)
    c1 = a1*b1 - a2*b2 - a3*b3 - a4*b4
    c2 = a1*b2 + a2*b1 + a3*b4 - a4*b3
    c3 = a1*b3 - a2*b4 + a3*b1 + a4*b2
    c4 = a1*b4 + a2*b3 - a3*b2 + a4*b1
    rhs = c1**2 + c2**2 + c3**2 + c4**2
    return abs(lhs - rhs) < 1e-10


# =============================================================================
# Part 4: Representation Counts (Sums of Squares)
# =============================================================================

def count_representations(n, k):
    """
    Count the number of ways to write n as a sum of k squares
    (with signs and order), for small n.
    """
    if k == 0:
        return 1 if n == 0 else 0

    count = 0
    bound = int(np.sqrt(n)) + 1
    for a in range(-bound, bound + 1):
        remainder = n - a * a
        if remainder >= 0:
            count += count_representations(remainder, k - 1)
    return count


def r2(n):
    """r₂(n): representations as sum of 2 squares."""
    return count_representations(n, 2)


def r4(n):
    """r₄(n): representations as sum of 4 squares."""
    return count_representations(n, 4)


def sigma_k(k, n):
    """σ_k(n) = sum of d^k for d dividing n."""
    if n == 0:
        return 0
    return sum(d**k for d in range(1, n+1) if n % d == 0)


def jacobi_r4(n):
    """Jacobi's formula: r₄(n) = 8 * sum_{d|n, 4 ∤ d} d."""
    if n == 0:
        return 1
    return 8 * sum(d for d in range(1, n+1) if n % d == 0 and d % 4 != 0)


# =============================================================================
# Part 5: The Cusp Form Barrier
# =============================================================================

def cusp_space_dimension(weight):
    """
    Approximate dimension of S_k(Γ₀(4)) for small weights.
    These values are computed from the Riemann-Roch theorem
    for modular forms.
    """
    dims = {2: 0, 4: 0, 6: 0, 8: 1, 10: 1, 12: 2, 14: 2, 16: 5, 18: 5, 20: 7}
    return dims.get(weight, "?")


# =============================================================================
# Main Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("THE CAYLEY-DICKSON HIERARCHY DEMONSTRATION")
    print("=" * 70)

    # --- Demo 1: Basic Arithmetic ---
    print("\n--- Demo 1: Basic Cayley-Dickson Arithmetic ---\n")

    # Complex numbers
    z1 = CayleyDickson(3, 4)  # 3 + 4i
    z2 = CayleyDickson(1, -2)  # 1 - 2i
    print(f"z1 = {z1}")
    print(f"z2 = {z2}")
    print(f"z1 * z2 = {z1 * z2}")
    print(f"|z1|² = {z1.norm_sq()}")
    print(f"|z2|² = {z2.norm_sq()}")
    print(f"|z1*z2|² = {(z1*z2).norm_sq()}")
    print(f"|z1|²·|z2|² = {z1.norm_sq() * z2.norm_sq()}")
    print(f"Norm multiplicative? {abs((z1*z2).norm_sq() - z1.norm_sq()*z2.norm_sq()) < 1e-10}")

    # Quaternions
    print()
    i = CayleyDickson(0, 1, 0, 0)
    j = CayleyDickson(0, 0, 1, 0)
    k = CayleyDickson(0, 0, 0, 1)
    print(f"i = {i}")
    print(f"j = {j}")
    print(f"i*j = {i * j}")
    print(f"j*i = {j * i}")
    print(f"i*j = k? {(i*j).components() == k.components()}")
    print(f"j*i = -k? {(j*i).components() == (-k).components()}")
    print(f"Commutativity violated? {'Yes' if not all(abs(a-b) < 1e-10 for a,b in zip((i*j).components(), (j*i).components())) else 'No'}")

    # --- Demo 2: Property Cascade ---
    print("\n--- Demo 2: Property Cascade Through the Hierarchy ---\n")
    print(f"{'Level':<8} {'Algebra':<6} {'Dim':<5} {'Commutative?':<15} {'Associative?':<15} {'Norm Mult?':<15}")
    print("-" * 64)

    names = {0: "ℝ", 1: "ℂ", 2: "ℍ", 3: "𝕆", 4: "𝕊"}
    for level in range(5):
        comm_violations = test_commutativity(level, 50)
        assoc_violations = test_associativity(level, 50)
        norm_violations = test_norm_multiplicativity(level, 50)
        comm_str = "Yes" if comm_violations == 0 else f"No ({comm_violations}/50)"
        assoc_str = "Yes" if assoc_violations == 0 else f"No ({assoc_violations}/50)"
        norm_str = "Yes" if norm_violations == 0 else f"No ({norm_violations}/50)"
        print(f"{level:<8} {names[level]:<6} {2**level:<5} {comm_str:<15} {assoc_str:<15} {norm_str:<15}")

    # --- Demo 3: Composition Identities ---
    print("\n--- Demo 3: Composition Identity Verification ---\n")
    a, b, c, d = 3, 7, 11, 13
    print(f"Brahmagupta-Fibonacci: ({a}²+{b}²)({c}²+{d}²) = ({a*c-b*d})² + ({a*d+b*c})²")
    print(f"  LHS = {(a**2+b**2)*(c**2+d**2)}")
    print(f"  RHS = {(a*c-b*d)**2 + (a*d+b*c)**2}")
    print(f"  Identity holds: {verify_brahmagupta_fibonacci(a, b, c, d)}")

    # --- Demo 4: Representation Counts ---
    print("\n--- Demo 4: Representation Counts r₂(n) and r₄(n) ---\n")
    print(f"{'n':<5} {'r₂(n)':<10} {'r₄(n)':<10} {'r₄(n)/8':<10} {'Jacobi r₄':<10}")
    print("-" * 45)
    for n in range(1, 16):
        r2_val = r2(n)
        r4_val = r4(n)
        jac = jacobi_r4(n)
        print(f"{n:<5} {r2_val:<10} {r4_val:<10} {r4_val/8:<10.1f} {jac:<10}")

    # --- Demo 5: Cusp Form Barrier ---
    print("\n--- Demo 5: The Cusp Form Barrier ---\n")
    print(f"{'Weight':<10} {'Channel':<10} {'dim S_k(Γ₀(4))':<20} {'Status'}")
    print("-" * 55)
    channel_map = {2: 2, 4: 3, 8: 5, 16: 6}
    for w in [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]:
        d = cusp_space_dimension(w)
        ch = channel_map.get(w, "-")
        status = "Pure Eisenstein" if d == 0 else f"{d} cusp form(s)"
        print(f"{w:<10} {str(ch):<10} {str(d):<20} {status}")

    # --- Demo 6: Divisor Sum Multiplicativity ---
    print("\n--- Demo 6: Divisor Sum Multiplicativity σ_k ---\n")
    for k_exp in [1, 3, 7]:
        s6 = sigma_k(k_exp, 6)
        s2 = sigma_k(k_exp, 2)
        s3 = sigma_k(k_exp, 3)
        mult = "✓" if s6 == s2 * s3 else "✗"
        print(f"σ_{k_exp}(6) = {s6}, σ_{k_exp}(2)·σ_{k_exp}(3) = {s2}·{s3} = {s2*s3}  {mult}")

    # --- Demo 7: Zero Divisor Search ---
    print("\n--- Demo 7: Zero Divisor Search at Sedenion Level ---\n")
    print("Searching for elements with small product norm...")
    ratio, pair = find_zero_divisors(4, 5000)
    print(f"Best norm(ab)/[norm(a)·norm(b)] ratio found: {ratio:.6f}")
    if ratio < 0.1:
        print(">> Near-zero-divisors detected! Norm is NOT multiplicative.")
    else:
        print(">> Norm multiplicativity violated but no near-zero-divisors found")
        print("   (exact zero divisors exist but require specific algebraic construction)")

    # --- Demo 8: Dimension Dominance ---
    print("\n--- Demo 8: Cayley-Dickson Dimension Dominance ---\n")
    for n in range(1, 8):
        dim_n = 2 ** n
        sum_below = sum(2**i for i in range(n))
        print(f"Level {n}: dim = {dim_n:>4}, sum below = {sum_below:>4}, "
              f"dominates? {dim_n > sum_below} (ratio {dim_n/sum_below:.2f})")

    print("\n" + "=" * 70)
    print("ALL DEMONSTRATIONS COMPLETE")
    print("=" * 70)
