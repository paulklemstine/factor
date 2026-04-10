#!/usr/bin/env python3
"""
Tropical Neural Network Compilation Demo (pure Python, no dependencies)
=========================================================================
Demonstrates that ReLU neural networks are secretly computing in tropical algebra.

Key identity (machine-verified in Lean 4):
    ReLU(x) = max(x, 0) = x ⊕_T 0

where ⊕_T is tropical addition (max).
"""

import math
import random


# ============================================================================
# Tropical Semiring Operations
# ============================================================================

def trop_add(a, b):
    """Tropical addition: max(a, b)"""
    return max(a, b)


def trop_mul(a, b):
    """Tropical multiplication: a + b"""
    return a + b


def relu(x):
    """ReLU(x) = max(x, 0) = x ⊕_T 0"""
    return max(x, 0)


# ============================================================================
# Verify the Core Identity
# ============================================================================

def verify_core_identity(n_tests=1000):
    """Verify ReLU(x) = trop_add(x, 0) for random inputs."""
    print("=" * 65)
    print("  CORE IDENTITY: ReLU(x) = x ⊕_T 0")
    print("  (Machine-verified in Lean 4 as definitional equality: rfl)")
    print("=" * 65)

    random.seed(42)
    max_err = 0
    for _ in range(n_tests):
        x = random.gauss(0, 10)
        r = relu(x)
        t = trop_add(x, 0)
        max_err = max(max_err, abs(r - t))

    print(f"\n  Tested {n_tests} random inputs x ~ N(0, 10²)")
    print(f"  max |ReLU(x) - (x ⊕_T 0)|  = {max_err}")
    print(f"  Identity verified: {'YES ✓' if max_err == 0 else 'NO ✗'}")


# ============================================================================
# Tropical Semiring Axioms
# ============================================================================

def verify_semiring_axioms(n_tests=500):
    """Verify tropical semiring axioms numerically."""
    print("\n" + "=" * 65)
    print("  TROPICAL SEMIRING AXIOMS (all machine-verified in Lean 4)")
    print("=" * 65)

    random.seed(42)
    violations = {name: 0 for name in [
        "⊕ comm", "⊕ assoc", "⊕ idem",
        "⊙ comm", "⊙ assoc", "⊙ id",
        "⊙ distrib L", "⊙ distrib R"
    ]}

    for _ in range(n_tests):
        a = random.gauss(0, 5)
        b = random.gauss(0, 5)
        c = random.gauss(0, 5)

        # ⊕ commutative
        if abs(trop_add(a, b) - trop_add(b, a)) > 1e-15:
            violations["⊕ comm"] += 1

        # ⊕ associative
        if abs(trop_add(trop_add(a, b), c) - trop_add(a, trop_add(b, c))) > 1e-15:
            violations["⊕ assoc"] += 1

        # ⊕ idempotent
        if abs(trop_add(a, a) - a) > 1e-15:
            violations["⊕ idem"] += 1

        # ⊙ commutative
        if abs(trop_mul(a, b) - trop_mul(b, a)) > 1e-15:
            violations["⊙ comm"] += 1

        # ⊙ associative
        if abs(trop_mul(trop_mul(a, b), c) - trop_mul(a, trop_mul(b, c))) > 1e-10:
            violations["⊙ assoc"] += 1

        # ⊙ identity (0)
        if abs(trop_mul(a, 0) - a) > 1e-15:
            violations["⊙ id"] += 1

        # Left distribution
        if abs(trop_mul(a, trop_add(b, c)) - trop_add(trop_mul(a, b), trop_mul(a, c))) > 1e-15:
            violations["⊙ distrib L"] += 1

        # Right distribution
        if abs(trop_mul(trop_add(a, b), c) - trop_add(trop_mul(a, c), trop_mul(b, c))) > 1e-15:
            violations["⊙ distrib R"] += 1

    print(f"\n  {'Axiom':<20s}  {'Violations':<12s}  Status")
    print("  " + "-" * 45)
    for name, v in violations.items():
        print(f"  {name:<20s}  {v:<12d}  {'✓' if v == 0 else '✗'}")


# ============================================================================
# Maslov Sandwich
# ============================================================================

def maslov_sandwich_demo():
    """Demonstrate the Maslov sandwich: max(a,b) ≤ log(exp(a)+exp(b)) ≤ max(a,b)+ln(2)"""
    print("\n" + "=" * 65)
    print("  MASLOV SANDWICH THEOREM (Machine-Verified in Lean 4)")
    print("  max(a,b) ≤ log(exp(a) + exp(b)) ≤ max(a,b) + ln(2)")
    print("=" * 65)

    test_pairs = [(0, 0), (1, 2), (-3, 5), (10, 10), (-1, -1), (7, 3)]
    ln2 = math.log(2)

    print(f"\n  {'a':>6s}  {'b':>6s}  {'max(a,b)':>10s}  {'LSE(a,b)':>10s}  "
          f"{'max+ln2':>10s}  {'gap':>8s}")
    print("  " + "-" * 58)

    for a, b in test_pairs:
        mx = max(a, b)
        lse = math.log(math.exp(a) + math.exp(b))
        upper = mx + ln2
        gap = lse - mx

        lower_ok = mx <= lse + 1e-10
        upper_ok = lse <= upper + 1e-10

        print(f"  {a:>6.1f}  {b:>6.1f}  {mx:>10.4f}  {lse:>10.4f}  "
              f"{upper:>10.4f}  {gap:>8.4f}  {'✓' if lower_ok and upper_ok else '✗'}")

    print(f"\n  Maximum gap = ln(2) = {ln2:.6f}")
    print("  Gap equals ln(2) exactly when a = b (maximum uncertainty)")


# ============================================================================
# Tropical Quantum Gates
# ============================================================================

def tropical_gate_demo():
    """Demonstrate tropical quantum gates."""
    print("\n" + "=" * 65)
    print("  TROPICAL QUANTUM GATES")
    print("=" * 65)

    def trop_hadamard(a, b):
        return (max(a, b), max(a, b))

    def trop_cnot(a, b):
        return (a, a + b)

    def trop_phase(phi, a):
        return a + phi

    print("\n  Tropical Hadamard (IDEMPOTENT: H(H(a,b)) = H(a,b)):")
    for a, b in [(1, 3), (5, 2), (0, 0), (-1, 4)]:
        h1 = trop_hadamard(a, b)
        h2 = trop_hadamard(*h1)
        idem = h1 == h2
        print(f"    H({a},{b}) = {h1},  H²({a},{b}) = {h2}  "
              f"{'✓ idempotent' if idem else '✗ NOT idempotent'}")

    print("\n  Tropical CNOT (NOT self-inverse):")
    for a, b in [(1, 3), (5, 2), (0, 0)]:
        c1 = trop_cnot(a, b)
        c2 = trop_cnot(*c1)
        self_inv = c2 == (a, b)
        print(f"    CNOT({a},{b}) = {c1},  CNOT²({a},{b}) = {c2}  "
              f"{'self-inverse' if self_inv else 'NOT self-inverse'}")

    print("\n  Tropical Phase (= synaptic weight addition):")
    for phi in [0.5, 1.0, -0.3]:
        for a in [2.0, -1.0]:
            result = trop_phase(phi, a)
            print(f"    Phase({phi})({a}) = {result:.1f}")


# ============================================================================
# Winner-Take-All = Tropical Projection
# ============================================================================

def wta_demo():
    """Show that winner-take-all is an idempotent tropical projection."""
    print("\n" + "=" * 65)
    print("  WINNER-TAKE-ALL = TROPICAL PROJECTION (Idempotent)")
    print("=" * 65)

    def wta(vec):
        """Winner-take-all: max component gets 1, rest get 0."""
        m = max(vec)
        return tuple(1 if x == m else 0 for x in vec)

    test_vecs = [(3, 1, 2), (1, 5, 3), (2, 2, 7), (0, 0, 0), (4, 4, 1)]
    print(f"\n  {'Input':<20s}  {'WTA(x)':<20s}  {'WTA²(x)':<20s}  Idempotent?")
    print("  " + "-" * 65)
    for v in test_vecs:
        w1 = wta(v)
        w2 = wta(w1)
        print(f"  {str(v):<20s}  {str(w1):<20s}  {str(w2):<20s}  "
              f"{'✓' if w1 == w2 else '✗'}")


# ============================================================================
# Linear Region Count
# ============================================================================

def linear_region_demo():
    print("\n" + "=" * 65)
    print("  TROPICAL GEOMETRY: LINEAR REGIONS OF RELU NETWORKS")
    print("  A ReLU network's decision boundary is a tropical hypersurface")
    print("=" * 65)
    print("\n  Upper bound on linear regions: width^depth")
    print(f"\n  {'depth':>6s}  {'w=4':>10s}  {'w=8':>10s}  {'w=16':>10s}  {'w=32':>10s}")
    print("  " + "-" * 46)
    for d in range(1, 7):
        vals = [w**d for w in [4, 8, 16, 32]]
        print(f"  {d:>6d}  " + "  ".join(f"{v:>10d}" for v in vals))


def main():
    verify_core_identity()
    verify_semiring_axioms()
    maslov_sandwich_demo()
    tropical_gate_demo()
    wta_demo()
    linear_region_demo()

    print("\n" + "=" * 65)
    print("  SUMMARY")
    print("=" * 65)
    print("  • ReLU(x) = x ⊕_T 0  (tropical addition with identity)")
    print("  • Proof: rfl (definitional equality in Lean 4)")
    print("  • Tropical Hadamard is idempotent: H ∘ H = H")
    print("  • Winner-Take-All is idempotent: WTA ∘ WTA = WTA")
    print("  • Maslov sandwich: max ≤ LSE ≤ max + ln(2)")
    print("  • Decision boundaries = tropical hypersurfaces")
    print("=" * 65)


if __name__ == "__main__":
    main()
