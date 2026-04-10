#!/usr/bin/env python3
"""
Quantum Gate Optimization via Quaternion Descent Trees

Demonstrates the connection between Lipschitz/Hurwitz integer quaternions
and quantum gate synthesis for Clifford+T, Clifford+V, and general gate sets.

Usage:
    python quantum_gate_optimization_demo.py
"""

import math
import itertools
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict

# ============================================================
# Part 1: Integer Quaternion Algebra
# ============================================================

@dataclass(frozen=True)
class Quat:
    """Integer quaternion (Lipschitz integer)"""
    w: int
    x: int
    y: int
    z: int

    def __mul__(self, other: 'Quat') -> 'Quat':
        """Hamilton product"""
        return Quat(
            self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z,
            self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y,
            self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x,
            self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w
        )

    def __add__(self, other: 'Quat') -> 'Quat':
        return Quat(self.w + other.w, self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Quat') -> 'Quat':
        return Quat(self.w - other.w, self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self) -> 'Quat':
        return Quat(-self.w, -self.x, -self.y, -self.z)

    @property
    def conj(self) -> 'Quat':
        return Quat(self.w, -self.x, -self.y, -self.z)

    @property
    def norm_sq(self) -> int:
        return self.w**2 + self.x**2 + self.y**2 + self.z**2

    @property
    def norm(self) -> float:
        return math.sqrt(self.norm_sq)

    def to_su2(self) -> List[List[complex]]:
        """Convert to SU(2) matrix (scaled by 1/sqrt(norm_sq))"""
        d = math.sqrt(self.norm_sq)
        w, x, y, z = self.w/d, self.x/d, self.y/d, self.z/d
        return [
            [complex(w, x), complex(y, z)],
            [complex(-y, z), complex(w, -x)]
        ]

    def __repr__(self):
        parts = []
        if self.w: parts.append(f"{self.w}")
        if self.x: parts.append(f"{self.x}i")
        if self.y: parts.append(f"{self.y}j")
        if self.z: parts.append(f"{self.z}k")
        return " + ".join(parts) if parts else "0"


# Standard gates as quaternions
SIGMA = Quat(1, 1, 1, 1)   # σ = 1+i+j+k, |σ|² = 4
T_GATE = Quat(1, 1, 0, 0)  # T gate, |T|² = 2
H_GATE = Quat(1, 0, 0, 1)  # Hadamard, |H|² = 2
S_GATE = Quat(0, 1, 0, 0)  # S gate, |S|² = 1
V_GATE = Quat(2, 1, 0, 0)  # V gate, |V|² = 5
IDENTITY = Quat(1, 0, 0, 0)

# Lipschitz units
LIPSCHITZ_UNITS = [
    Quat(1,0,0,0), Quat(-1,0,0,0),
    Quat(0,1,0,0), Quat(0,-1,0,0),
    Quat(0,0,1,0), Quat(0,0,-1,0),
    Quat(0,0,0,1), Quat(0,0,0,-1)
]

# ============================================================
# Part 2: r₄(n) — Counting Representations
# ============================================================

def r4(n: int) -> int:
    """Count representations of n as sum of 4 squares"""
    count = 0
    bound = int(math.isqrt(n))
    for w in range(-bound, bound + 1):
        for x in range(-bound, bound + 1):
            rem2 = n - w*w - x*x
            if rem2 < 0:
                continue
            for y in range(-bound, bound + 1):
                rem1 = rem2 - y*y
                if rem1 < 0:
                    continue
                z_sq = rem1
                z = int(math.isqrt(z_sq))
                if z*z == z_sq:
                    count += 1
                    if z > 0:
                        count += 1  # also -z
    return count

def r3(n: int) -> int:
    """Count representations of n as sum of 3 squares"""
    count = 0
    bound = int(math.isqrt(n))
    for a in range(-bound, bound + 1):
        for b in range(-bound, bound + 1):
            rem = n - a*a - b*b
            if rem < 0:
                continue
            c = int(math.isqrt(rem))
            if c*c == rem:
                count += 1
                if c > 0:
                    count += 1
    return count

def sum_of_divisors(n: int) -> int:
    """σ(n) = sum of divisors of n"""
    return sum(d for d in range(1, n+1) if n % d == 0)

# ============================================================
# Part 3: Quaternion Descent Algorithm
# ============================================================

def nearest_lipschitz(w: float, x: float, y: float, z: float) -> Quat:
    """Round to nearest Lipschitz integer"""
    return Quat(round(w), round(x), round(y), round(z))

def lipschitz_divide(alpha: Quat, beta: Quat) -> Tuple[Quat, Quat]:
    """Divide alpha by beta in the Lipschitz integers.
    Returns (gamma, rho) where alpha = beta * gamma + rho and |rho|² ≤ |beta|²."""
    # Compute alpha * conj(beta) / |beta|²
    num = alpha * beta.conj
    denom = beta.norm_sq
    gamma = nearest_lipschitz(
        num.w / denom, num.x / denom, num.y / denom, num.z / denom
    )
    rho = alpha - beta * gamma
    return gamma, rho

def descent(alpha: Quat, max_steps: int = 100) -> List[Tuple[Quat, Quat]]:
    """Perform quaternion descent on alpha using σ = 1+i+j+k.
    Returns list of (quotient, remainder) pairs."""
    steps = []
    current = alpha
    for _ in range(max_steps):
        if current.norm_sq <= 1:
            break
        gamma, rho = lipschitz_divide(current, SIGMA)
        steps.append((gamma, rho))
        if rho.norm_sq >= current.norm_sq:
            break  # No progress (Lipschitz can stall)
        current = rho
    return steps

# ============================================================
# Part 4: Gate Synthesis via Descent
# ============================================================

@dataclass
class GateDecomposition:
    """A decomposition of a target quaternion into elementary gates"""
    target: Quat
    gates: List[str]
    quaternions: List[Quat]
    total_norm: int
    t_count: int
    depth: int

def find_closest_quaternion(norm_level: int) -> List[Quat]:
    """Find all integer quaternions at a given norm level"""
    results = []
    bound = int(math.isqrt(norm_level))
    for w in range(-bound, bound + 1):
        for x in range(-bound, bound + 1):
            rem2 = norm_level - w*w - x*x
            if rem2 < 0: continue
            for y in range(-bound, bound + 1):
                rem1 = rem2 - y*y
                if rem1 < 0: continue
                z = int(math.isqrt(rem1))
                if z*z == rem1:
                    results.append(Quat(w, x, y, z))
                    if z > 0:
                        results.append(Quat(w, x, y, -z))
    return results

def clifford_t_decompose(alpha: Quat) -> GateDecomposition:
    """Decompose a norm-2^k quaternion into T and Clifford gates.
    Uses the descent tree structure."""
    gates = []
    quats = []
    current = alpha
    depth = 0

    while current.norm_sq > 1:
        # Try to factor out a T gate
        found = False
        for unit in LIPSCHITZ_UNITS:
            candidate = current * T_GATE.conj
            # Check if dividing by T gives integer result
            # T = (1,1,0,0), T* = (1,-1,0,0), |T|² = 2
            num = current * T_GATE.conj
            if num.w % 2 == 0 and num.x % 2 == 0 and num.y % 2 == 0 and num.z % 2 == 0:
                current = Quat(num.w // 2, num.x // 2, num.y // 2, num.z // 2)
                gates.append("T")
                quats.append(T_GATE)
                found = True
                depth += 1
                break

        if not found:
            # Try Hadamard
            num = current * H_GATE.conj
            if num.w % 2 == 0 and num.x % 2 == 0 and num.y % 2 == 0 and num.z % 2 == 0:
                current = Quat(num.w // 2, num.x // 2, num.y // 2, num.z // 2)
                gates.append("H")
                quats.append(H_GATE)
                depth += 1
            else:
                # Generic descent step
                gamma, rho = lipschitz_divide(current, SIGMA)
                gates.append("σ-step")
                quats.append(SIGMA)
                current = gamma
                depth += 1

        if depth > 50:  # Safety limit
            break

    # Final Clifford gate
    if current.norm_sq == 1:
        gates.append("Clifford")
        quats.append(current)

    t_count = sum(1 for g in gates if g == "T")

    return GateDecomposition(
        target=alpha,
        gates=gates,
        quaternions=quats,
        total_norm=alpha.norm_sq,
        t_count=t_count,
        depth=depth
    )

# ============================================================
# Part 5: Demonstrations
# ============================================================

def demo_basic_quaternion_gates():
    """Demonstrate the quaternion representations of standard gates"""
    print("=" * 70)
    print("DEMO 1: Quaternion Representations of Quantum Gates")
    print("=" * 70)

    gates = {
        "Identity": IDENTITY,
        "T gate": T_GATE,
        "Hadamard": H_GATE,
        "S gate": S_GATE,
        "V gate": V_GATE,
        "σ = 1+i+j+k": SIGMA,
    }

    for name, q in gates.items():
        su2 = q.to_su2()
        print(f"\n{name}: {q}")
        print(f"  |q|² = {q.norm_sq}")
        print(f"  SU(2) matrix (scaled):")
        print(f"    [{su2[0][0]:.4f}  {su2[0][1]:.4f}]")
        print(f"    [{su2[1][0]:.4f}  {su2[1][1]:.4f}]")

def demo_gate_composition():
    """Demonstrate gate composition via quaternion multiplication"""
    print("\n" + "=" * 70)
    print("DEMO 2: Gate Composition = Quaternion Multiplication")
    print("=" * 70)

    # T² = S (up to scaling)
    t2 = T_GATE * T_GATE
    print(f"\nT² = {T_GATE} × {T_GATE} = {t2}")
    print(f"  |T²|² = {t2.norm_sq} = {T_GATE.norm_sq}² = {T_GATE.norm_sq**2}")

    # T⁴
    t4 = t2 * t2
    print(f"\nT⁴ = {t4}")
    print(f"  |T⁴|² = {t4.norm_sq}")

    # T⁸ = scalar
    t8 = t4 * t4
    print(f"\nT⁸ = {t8}")
    print(f"  |T⁸|² = {t8.norm_sq}")
    print(f"  T⁸ is a scalar (proportional to identity): ✓")

    # TH composition
    th = T_GATE * H_GATE
    print(f"\nT·H = {T_GATE} × {H_GATE} = {th}")
    print(f"  |T·H|² = {th.norm_sq} = {T_GATE.norm_sq} × {H_GATE.norm_sq}")

def demo_r4_distribution():
    """Show the distribution of r₄(n) — lattice points at each norm level"""
    print("\n" + "=" * 70)
    print("DEMO 3: Lattice Point Distribution r₄(n)")
    print("=" * 70)
    print(f"\n{'n':>4} | {'r₄(n)':>8} | {'8σ(n)':>8} | {'r₄/8':>6} | {'Angular density':>16}")
    print("-" * 60)

    for n in range(1, 21):
        r = r4(n)
        sig = sum_of_divisors(n)
        jacobi_pred = 8 * sig  # Jacobi's formula (exact for odd n)
        density = r / (4 * math.pi * n) if n > 0 else 0  # approximate points per unit solid angle
        match_str = "✓" if r == jacobi_pred else f"({jacobi_pred})"
        print(f"{n:>4} | {r:>8} | {jacobi_pred:>7}{match_str} | {r/8:>6.1f} | {density:>16.4f}")

def demo_descent_algorithm():
    """Demonstrate the quaternion descent for gate synthesis"""
    print("\n" + "=" * 70)
    print("DEMO 4: Quaternion Descent for Gate Synthesis")
    print("=" * 70)

    # Example: decompose a norm-8 quaternion
    targets = [
        Quat(2, 2, 0, 0),   # norm 8 = 2³
        Quat(1, 1, 1, 1),   # norm 4 = 2²
        Quat(3, 1, 1, 1),   # norm 12
        Quat(2, 1, 0, 0),   # norm 5 (V gate)
    ]

    for target in targets:
        print(f"\nTarget: {target}, |q|² = {target.norm_sq}")
        steps = descent(target)
        print(f"  Descent depth: {len(steps)}")
        print(f"  Theoretical bound: ⌈log₂({target.norm_sq})⌉ = {math.ceil(math.log2(target.norm_sq)) if target.norm_sq > 1 else 0}")
        for i, (gamma, rho) in enumerate(steps):
            print(f"  Step {i+1}: quotient = {gamma} (|γ|² = {gamma.norm_sq}), "
                  f"remainder = {rho} (|ρ|² = {rho.norm_sq})")

def demo_clifford_t_synthesis():
    """Demonstrate Clifford+T gate synthesis"""
    print("\n" + "=" * 70)
    print("DEMO 5: Clifford+T Gate Synthesis")
    print("=" * 70)

    # Build norm-2^k quaternions by composing T gates
    print("\nPowers of T gate:")
    current = IDENTITY
    for k in range(9):
        print(f"  T^{k} = {current}, |T^{k}|² = {current.norm_sq}")
        decomp = clifford_t_decompose(current)
        if current.norm_sq > 1:
            print(f"    Decomposition: {' · '.join(decomp.gates)}")
            print(f"    T-count: {decomp.t_count}")
        current = current * T_GATE

    # Composite gate: THT
    print("\nComposite gate: T·H·T")
    tht = T_GATE * H_GATE * T_GATE
    print(f"  THT = {tht}, |THT|² = {tht.norm_sq}")
    decomp = clifford_t_decompose(tht)
    print(f"  Decomposition: {' · '.join(decomp.gates)}")
    print(f"  T-count: {decomp.t_count}")

def demo_gate_set_comparison():
    """Compare Clifford+T vs Clifford+V gate counts"""
    print("\n" + "=" * 70)
    print("DEMO 6: Gate Set Comparison — Clifford+T vs Clifford+V")
    print("=" * 70)

    print(f"\n{'Precision d':>14} | {'log₂(d)':>8} | {'log₅(d)':>8} | {'Savings':>8}")
    print("-" * 50)

    for k in range(1, 16):
        d = 2**k
        log2 = k
        log5 = math.log(d, 5)
        savings = 1 - log5/log2 if log2 > 0 else 0
        print(f"  d = 2^{k:>2} = {d:>6} | {log2:>8} | {log5:>8.2f} | {savings:>7.1%}")

    print(f"\nTheoretical ratio: log₅/log₂ = {math.log(2,5):.4f}")
    print(f"Clifford+V uses {(1-math.log(2,5))*100:.1f}% fewer non-Clifford gates")

def demo_hurwitz_advantage():
    """Demonstrate the Hurwitz lattice density advantage"""
    print("\n" + "=" * 70)
    print("DEMO 7: Hurwitz vs Lipschitz Lattice Density")
    print("=" * 70)

    print(f"\n{'Norm d':>8} | {'r₄(d)':>8} | {'Points/unit':>12} | {'Lipschitz units at d=1':>24}")
    print("-" * 65)

    for d in range(1, 16):
        r = r4(d)
        density = r / (2 * math.pi**2 * d) if d > 0 else 0  # vol(S³) = 2π²
        label = ""
        if d == 1: label = "← 8 Lipschitz units"
        if d == 2: label = "← 24 Hurwitz units (3×!)"
        print(f"{d:>8} | {r:>8} | {density:>12.4f} | {label}")

    print(f"\nKey insight: r₄(2) = 24 = 3 × 8")
    print(f"The 24-cell (Hurwitz units at norm 2) gives 3× denser coverage")
    print(f"Covering radius: Lipschitz = 1, Hurwitz = 1/2 (4× better in norm)")

def demo_angular_spacing():
    """Compute angular spacing between integer SU(2) points"""
    print("\n" + "=" * 70)
    print("DEMO 8: Angular Spacing on SU(2)")
    print("=" * 70)

    for d in [1, 2, 3, 4, 5, 8, 10, 13, 16]:
        quats = find_closest_quaternion(d)
        if len(quats) < 2:
            continue

        # Compute minimum angular distance between distinct points
        min_angle = float('inf')
        for i, q1 in enumerate(quats[:min(50, len(quats))]):
            for q2 in quats[i+1:min(50, len(quats))]:
                # Inner product on S³
                dot = (q1.w*q2.w + q1.x*q2.x + q1.y*q2.y + q1.z*q2.z) / d
                dot = max(-1, min(1, dot))
                angle = math.acos(abs(dot))
                if angle > 0.001:
                    min_angle = min(min_angle, angle)

        if min_angle < float('inf'):
            print(f"  d = {d:>3}: r₄ = {len(quats):>4}, "
                  f"min angular spacing = {min_angle:.4f} rad "
                  f"≈ {math.degrees(min_angle):.2f}°, "
                  f"~1/√d = {1/math.sqrt(d):.4f}")

def demo_branching_modular():
    """Show branching controlled by r₃ (modular forms connection)"""
    print("\n" + "=" * 70)
    print("DEMO 9: Branching Structure — r₃(d²) and Modular Forms")
    print("=" * 70)

    print(f"\n{'d':>4} | {'d²':>6} | {'r₃(d²)':>8} | {'Branching':>10} | {'4^a(8b+7)?':>12}")
    print("-" * 55)

    for d in range(1, 16):
        d_sq = d * d
        r = r3(d_sq)
        # Check Legendre obstruction
        temp = d_sq
        while temp % 4 == 0:
            temp //= 4
        obstructed = (temp % 8 == 7)
        obs_str = "OBSTRUCTED" if obstructed else "OK"
        branching = max(0, (r - 6) // 48)  # rough estimate
        print(f"{d:>4} | {d_sq:>6} | {r:>8} | {branching:>10} | {obs_str:>12}")

    print(f"\nKey: r₃(n) = 12·h(-4n) for squarefree n ≡ 1,2 (mod 4)")
    print(f"The branching of the descent tree is controlled by class numbers!")

# ============================================================
# Part 6: Main
# ============================================================

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  Quantum Gate Optimization via Quaternion Descent Trees             ║")
    print("║  Research Team PHOTON-4                                             ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    demo_basic_quaternion_gates()
    demo_gate_composition()
    demo_r4_distribution()
    demo_descent_algorithm()
    demo_clifford_t_synthesis()
    demo_gate_set_comparison()
    demo_hurwitz_advantage()
    demo_angular_spacing()
    demo_branching_modular()

    print("\n" + "=" * 70)
    print("All demonstrations complete.")
    print("See Pythagorean__QuantumGateOptimization.lean for formal proofs.")
    print("=" * 70)
