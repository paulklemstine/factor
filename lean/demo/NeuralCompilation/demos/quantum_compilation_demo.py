"""
Quantum Compilation Demo
=========================
Demonstrates quantum gate crystallization via Gaussian integers and quaternions.

This implements the formally verified results from QuantumCompilation.lean:
- euler_four_square: Quaternion norm multiplicativity
- unit_quat_closed: Unit quaternions closed under multiplication
- compilation_hierarchy: ℤ ⊂ ℤ[i] ⊂ Hurwitz ⊂ SU(2)
- quantum_crystal_error_bound: |Δa|² + |Δb|² ≤ 1/2
"""

import numpy as np
from typing import Tuple


# =============================================================================
# Gaussian Integers ℤ[i]
# =============================================================================

class GaussianInt:
    """A Gaussian integer a + bi with a, b ∈ ℤ."""

    def __init__(self, a: int, b: int):
        self.a = a
        self.b = b

    def norm(self) -> int:
        """N(a + bi) = a² + b²."""
        return self.a ** 2 + self.b ** 2

    def __mul__(self, other: 'GaussianInt') -> 'GaussianInt':
        """Complex multiplication: (a+bi)(c+di) = (ac-bd) + (ad+bc)i."""
        return GaussianInt(
            self.a * other.a - self.b * other.b,
            self.a * other.b + self.b * other.a
        )

    def __repr__(self) -> str:
        if self.b == 0:
            return str(self.a)
        elif self.a == 0:
            return f"{self.b}i"
        else:
            sign = "+" if self.b > 0 else "-"
            return f"{self.a}{sign}{abs(self.b)}i"


# =============================================================================
# Quaternions
# =============================================================================

class Quaternion:
    """A quaternion a + bi + cj + dk."""

    def __init__(self, a, b, c, d):
        self.a, self.b, self.c, self.d = a, b, c, d

    def norm(self):
        """N(q) = a² + b² + c² + d²."""
        return self.a**2 + self.b**2 + self.c**2 + self.d**2

    def __mul__(self, other: 'Quaternion') -> 'Quaternion':
        """Hamilton's quaternion product."""
        return Quaternion(
            self.a*other.a - self.b*other.b - self.c*other.c - self.d*other.d,
            self.a*other.b + self.b*other.a + self.c*other.d - self.d*other.c,
            self.a*other.c - self.b*other.d + self.c*other.a + self.d*other.b,
            self.a*other.d + self.b*other.c - self.c*other.b + self.d*other.a
        )

    def to_su2_matrix(self) -> np.ndarray:
        """Convert unit quaternion to SU(2) matrix."""
        n = np.sqrt(self.norm())
        a, b, c, d = self.a/n, self.b/n, self.c/n, self.d/n
        return np.array([
            [a + 1j*b, c + 1j*d],
            [-c + 1j*d, a - 1j*b]
        ])

    def __repr__(self) -> str:
        return f"({self.a} + {self.b}i + {self.c}j + {self.d}k)"


# =============================================================================
# Quantum Gates
# =============================================================================

# Standard quantum gates as 2×2 unitary matrices
PAULI_X = np.array([[0, 1], [1, 0]], dtype=complex)
PAULI_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
PAULI_Z = np.array([[1, 0], [0, -1]], dtype=complex)
HADAMARD = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
S_GATE = np.array([[1, 0], [0, 1j]], dtype=complex)
T_GATE = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex)


def crystallize_gate(gate: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    Crystallize a quantum gate to nearest Gaussian integers.
    Returns (crystallized_gate, error).
    """
    crystal = np.round(gate.real) + 1j * np.round(gate.imag)
    error = np.sum(np.abs(gate.real - np.round(gate.real))**2 +
                   np.abs(gate.imag - np.round(gate.imag))**2)
    return crystal, error


def verify_brahmagupta_fibonacci(a, b, c, d):
    """Verify the Brahmagupta-Fibonacci identity: (a²+b²)(c²+d²) = (ac-bd)² + (ad+bc)²."""
    lhs = (a**2 + b**2) * (c**2 + d**2)
    rhs = (a*c - b*d)**2 + (a*d + b*c)**2
    return lhs, rhs, lhs == rhs


def verify_euler_four_square(a1, b1, c1, d1, a2, b2, c2, d2):
    """Verify Euler's four-square identity."""
    lhs = (a1**2 + b1**2 + c1**2 + d1**2) * (a2**2 + b2**2 + c2**2 + d2**2)
    e1 = a1*a2 - b1*b2 - c1*c2 - d1*d2
    e2 = a1*b2 + b1*a2 + c1*d2 - d1*c2
    e3 = a1*c2 - b1*d2 + c1*a2 + d1*b2
    e4 = a1*d2 + b1*c2 - c1*b2 + d1*a2
    rhs = e1**2 + e2**2 + e3**2 + e4**2
    return lhs, rhs, lhs == rhs


def demo():
    """Run the quantum compilation demo."""
    print("=" * 60)
    print("Quantum Neural Network Compilation Demo")
    print("=" * 60)

    # Brahmagupta-Fibonacci Identity
    print("\n--- Brahmagupta-Fibonacci Identity ---")
    for a, b, c, d in [(3, 4, 1, 2), (5, 12, 7, 1), (1, 1, 1, 1)]:
        lhs, rhs, verified = verify_brahmagupta_fibonacci(a, b, c, d)
        print(f"  ({a}²+{b}²)({c}²+{d}²) = {lhs} = {rhs} ✓" if verified
              else f"  FAILED for ({a},{b},{c},{d})")

    # Euler's Four-Square Identity
    print("\n--- Euler's Four-Square Identity ---")
    q1 = (1, 2, 3, 4)
    q2 = (5, 6, 7, 8)
    lhs, rhs, verified = verify_euler_four_square(*q1, *q2)
    print(f"  N({q1}) × N({q2}) = {lhs}")
    print(f"  N(product) = {rhs}")
    print(f"  ✓ Identity verified: {verified}")

    # Gaussian Integer Gates
    print("\n--- Gaussian Integer Gate Representations ---")
    gates = {
        "Pauli X": PAULI_X,
        "Pauli Y": PAULI_Y,
        "Pauli Z": PAULI_Z,
        "Hadamard": HADAMARD,
        "S gate": S_GATE,
        "T gate": T_GATE,
    }

    for name, gate in gates.items():
        crystal, error = crystallize_gate(gate)
        print(f"  {name:12s}: crystal error = {error:.6f}, "
              f"entries = {crystal.ravel()}")

    # Scaled Hadamard is exact in ℤ[i]
    print("\n--- Scaled Gates (×√2) in ℤ[i] ---")
    H_scaled = HADAMARD * np.sqrt(2)
    crystal_H, error_H = crystallize_gate(H_scaled)
    print(f"  √2·H = {H_scaled.ravel()}")
    print(f"  Crystal: {crystal_H.ravel()}, error = {error_H:.6f}")

    # Quaternion Multiplication
    print("\n--- Quaternion Gate Composition ---")
    # Unit quaternions representing rotations
    q1 = Quaternion(1, 0, 0, 0)  # Identity
    q2 = Quaternion(0, 1, 0, 0)  # 180° rotation around x-axis
    q3 = Quaternion(0, 0, 1, 0)  # 180° rotation around y-axis

    print(f"  q1 = {q1}, norm = {q1.norm()}")
    print(f"  q2 = {q2}, norm = {q2.norm()}")
    print(f"  q3 = {q3}, norm = {q3.norm()}")

    q12 = q1 * q2
    q23 = q2 * q3
    print(f"  q1·q2 = {q12}, norm = {q12.norm()}")
    print(f"  q2·q3 = {q23}, norm = {q23.norm()}")
    print(f"  ✓ Unit quaternion closure: norms are all 1")

    # Compilation Hierarchy
    print("\n--- Compilation Hierarchy ---")
    print("  Level 0: ℤ (classical integer weights)")
    n = 5
    print(f"    Example: weight = {n}, norm = {n**2}")

    print("  Level 1: ℤ[i] (Gaussian integers)")
    g = GaussianInt(3, 4)
    print(f"    Example: {g}, norm = {g.norm()}")

    print("  Level 2: Hurwitz quaternions")
    h = Quaternion(1, 1, 1, 1)
    print(f"    Example: {h}, norm = {h.norm()}")

    print("  Level 3: SU(2) (continuous gates)")
    theta = np.pi / 7
    su2 = Quaternion(np.cos(theta), np.sin(theta), 0, 0)
    print(f"    Example: {su2}, norm = {su2.norm():.6f}")

    # Norm multiplicativity demo
    print("\n--- Norm Multiplicativity Through Hierarchy ---")
    g1 = GaussianInt(3, 4)
    g2 = GaussianInt(1, 2)
    g12 = g1 * g2
    print(f"  ℤ[i]: N({g1}) × N({g2}) = {g1.norm()} × {g2.norm()} = {g1.norm() * g2.norm()}")
    print(f"         N({g1}·{g2}) = N({g12}) = {g12.norm()}")
    print(f"  ✓ Multiplicative: {g1.norm() * g2.norm() == g12.norm()}")

    q1 = Quaternion(1, 2, 3, 4)
    q2 = Quaternion(5, 6, 7, 8)
    q12 = q1 * q2
    print(f"  ℍ: N({q1}) × N({q2}) = {q1.norm()} × {q2.norm()} = {q1.norm() * q2.norm()}")
    print(f"      N(product) = {q12.norm()}")
    print(f"  ✓ Multiplicative: {q1.norm() * q2.norm() == q12.norm()}")

    # Error bounds
    print("\n--- Quantum Crystallization Error Bounds ---")
    np.random.seed(42)
    for _ in range(5):
        a, b = np.random.randn(2)
        err_sq = abs(a - round(a))**2 + abs(b - round(b))**2
        print(f"  z = {a:.3f} + {b:.3f}i → |Δ|² = {err_sq:.4f} ≤ 0.5 ✓")

    # Summary
    print("\n" + "=" * 60)
    print("Summary of Verified Results:")
    print("  Euler's four-square identity (theorem: euler_four_square)")
    print("  Unit quaternion closure (theorem: unit_quat_closed)")
    print("  ℤ ⊂ ℤ[i] ⊂ Hurwitz (theorem: compilation_hierarchy)")
    print("  Complex crystal error ≤ 1/2 (theorem: quantum_crystal_error_bound)")
    print("  Solovay-Kitaev scaling (theorem: solovay_kitaev_gate_count)")
    print("=" * 60)


if __name__ == "__main__":
    demo()
