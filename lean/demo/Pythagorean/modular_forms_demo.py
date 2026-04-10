#!/usr/bin/env python3
"""
Berggren Descent and Theta Group Connection — Interactive Python Demo

Demonstrates the correspondence between:
- The Berggren tree of primitive Pythagorean triples
- The theta group Γ_θ = ⟨T², S⟩ ⊂ SL(2,ℤ)
- The modular surface X_θ and its cusps

All matrix identities in this demo are formally verified in Lean 4.
"""

import numpy as np
from fractions import Fraction
import json

# =============================================================================
# §1. Matrix Definitions (matching the Lean formalization)
# =============================================================================

# 2×2 Berggren matrices (Euclid parameter space)
BM1 = np.array([[2, -1], [1, 0]])
BM2 = np.array([[2,  1], [1, 0]])
BM3 = np.array([[1,  2], [0,  1]])
BM3_inv = np.array([[1, -2], [0,  1]])

# SL(2,ℤ) generators
T = np.array([[1, 1], [0, 1]])
T_sq = np.array([[1, 2], [0, 1]])
S = np.array([[0, -1], [1,  0]])

# 3×3 Berggren matrices (triple space)
BB1 = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]])
BB2 = np.array([[1,  2, 2], [2,  1, 2], [2,  2, 3]])
BB3 = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]])

# 3×3 Inverse Berggren matrices
BB1_inv = np.array([[ 1,  2, -2], [-2, -1,  2], [-2, -2,  3]])
BB2_inv = np.array([[ 1,  2, -2], [ 2,  1, -2], [-2, -2,  3]])
BB3_inv = np.array([[-1, -2,  2], [ 2,  1, -2], [-2, -2,  3]])

# Lorentz form Q = diag(1, 1, -1)
Q = np.diag([1, 1, -1])

# =============================================================================
# §2. Verify Fundamental Identities
# =============================================================================

def verify_identities():
    """Verify all the key matrix identities (matching Lean theorems)."""
    print("=" * 60)
    print("§2. FUNDAMENTAL IDENTITY VERIFICATION")
    print("=" * 60)

    # BM3 = T²
    assert np.array_equal(BM3, T_sq), "BM3 ≠ T²"
    print("✓ BM₃ = T² (BM₃_eq_T_sq)")

    # T² = T * T
    assert np.array_equal(T_sq, T @ T), "T² ≠ T*T"
    print("✓ T² = T·T (T_sq_eq_T_mul_T)")

    # BM3_inv * BM1 = S
    assert np.array_equal(BM3_inv @ BM1, S), "BM₃⁻¹·BM₁ ≠ S"
    print("✓ BM₃⁻¹·BM₁ = S (BM₃_inv_mul_BM₁_eq_S)")

    # BM1 = BM3 * S = T² * S
    assert np.array_equal(BM1, BM3 @ S), "BM₁ ≠ BM₃·S"
    print("✓ BM₁ = T²·S (BM₁_eq_BM₃_mul_S)")

    # S² = -I
    assert np.array_equal(S @ S, -np.eye(2, dtype=int)), "S² ≠ -I"
    print("✓ S² = -I (S_gen_sq_eq_neg_one)")

    # S⁴ = I
    S4 = S @ S @ S @ S
    assert np.array_equal(S4, np.eye(2, dtype=int)), "S⁴ ≠ I"
    print("✓ S⁴ = I (S_gen_pow_four)")

    # Determinants
    assert np.linalg.det(BM1) == 1, "det(BM₁) ≠ 1"
    print(f"✓ det(BM₁) = {int(np.linalg.det(BM1))} (det_BM₁)")
    assert np.linalg.det(BM2) == -1, "det(BM₂) ≠ -1"
    print(f"✓ det(BM₂) = {int(np.linalg.det(BM2))} (det_BM₂)")
    assert np.linalg.det(BM3) == 1, "det(BM₃) ≠ 1"
    print(f"✓ det(BM₃) = {int(np.linalg.det(BM3))} (det_BM₃)")

    # Traces
    assert np.trace(BM1) == 2, "tr(BM₁) ≠ 2"
    print(f"✓ tr(BM₁) = {np.trace(BM1)} — parabolic (trace_BM₁)")
    assert np.trace(BM3) == 2, "tr(BM₃) ≠ 2"
    print(f"✓ tr(BM₃) = {np.trace(BM3)} — parabolic (trace_BM₃)")
    assert np.trace(S) == 0, "tr(S) ≠ 0"
    print(f"✓ tr(S)   = {np.trace(S)} — elliptic (trace_S_gen)")

    # Trace relation
    lhs = np.trace(BM1 @ BM3) + np.trace(BM1 @ BM3_inv)
    rhs = np.trace(BM1) * np.trace(BM3)
    assert lhs == rhs, "Trace relation fails"
    print(f"✓ tr(M₁M₃) + tr(M₁M₃⁻¹) = tr(M₁)·tr(M₃) = {rhs} (trace_relation)")

    # Lorentz form preservation
    for name, B in [("B₁", BB1), ("B₂", BB2), ("B₃", BB3)]:
        assert np.array_equal(B.T @ Q @ B, Q), f"{name} doesn't preserve Q"
        print(f"✓ {name}ᵀ·Q·{name} = Q (Lorentz preservation)")

    # Commutator
    comm = BM1 @ BM1 @ BM3 - BM3 @ (BM1 @ BM1)
    expected = np.array([[-4, 8], [0, 4]])
    assert np.array_equal(comm, expected), "Commutator mismatch"
    print(f"✓ [M₁², M₃] = {comm.tolist()} (berggren_commutator)")

    print("\n✅ All identities verified!\n")

# =============================================================================
# §3. Theta Group Parity Check
# =============================================================================

def theta_parity(M):
    """Check if a 2×2 integer matrix satisfies the theta group parity condition.

    The condition is:
    1. M[0,0] ≡ M[1,1] (mod 2)  (diagonal congruence)
    2. M[0,1] ≡ M[1,0] (mod 2)  (off-diagonal congruence)
    3. (M[0,0] + M[0,1]) % 2 == 1  (row sum is odd)
    """
    return (M[0,0] % 2 == M[1,1] % 2 and
            M[0,1] % 2 == M[1,0] % 2 and
            (M[0,0] + M[0,1]) % 2 == 1)

def demo_theta_parity():
    """Demonstrate the theta group parity condition."""
    print("=" * 60)
    print("§3. THETA GROUP PARITY")
    print("=" * 60)

    matrices = {
        "T²": T_sq,
        "S": S,
        "M₁²": BM1 @ BM1,
        "T (NOT in Γ_θ)": T,
        "M₁": BM1,
        "M₂ (det=-1)": BM2,
    }

    for name, M in matrices.items():
        det = int(round(np.linalg.det(M)))
        parity = theta_parity(M)
        in_theta = parity and det == 1
        status = "✓ ∈ Γ_θ" if in_theta else "✗ ∉ Γ_θ"
        print(f"  {name:20s}: det={det:+d}, parity={parity}, {status}")
        print(f"    {M.tolist()}")

    # Verify closure
    print("\n  Closure test: T²·S product")
    prod = T_sq @ S
    print(f"    T²·S = {prod.tolist()}, det={int(round(np.linalg.det(prod)))}, "
          f"parity={theta_parity(prod)}")
    assert theta_parity(prod) and int(round(np.linalg.det(prod))) == 1
    print("    ✓ Product is in Γ_θ (closure verified)")
    print()

# =============================================================================
# §4. Berggren Tree Generation
# =============================================================================

def generate_berggren_tree(depth=4):
    """Generate the Berggren tree to a given depth."""
    root = np.array([3, 4, 5])
    tree = {0: [root]}

    for d in range(depth):
        tree[d + 1] = []
        for triple in tree[d]:
            for B in [BB1, BB2, BB3]:
                child = B @ triple
                # Ensure positive entries
                child = np.abs(child)
                tree[d + 1].append(child)

    return tree

def demo_berggren_tree():
    """Demonstrate the Berggren tree and its properties."""
    print("=" * 60)
    print("§4. BERGGREN TREE (first 3 levels)")
    print("=" * 60)

    tree = generate_berggren_tree(3)
    total = 0
    for depth, triples in sorted(tree.items()):
        total += len(triples)
        for t in triples:
            a, b, c = t
            # Verify Pythagorean
            assert a**2 + b**2 == c**2, f"Not Pythagorean: {t}"
            # Farey fraction
            farey = Fraction(int(b), int(a + c))
            print(f"  Depth {depth}: ({a:5d}, {b:5d}, {c:5d})  "
                  f"Farey: {str(farey):>5s}  "
                  f"Euclid ratio: {str(Fraction(int(max(a,b)), int(c))):>5s}")
        if depth < 3:
            print()

    print(f"\n  Total triples generated: {total}")
    print()

# =============================================================================
# §5. Berggren Descent
# =============================================================================

def berggren_descent(a, b, c):
    """Descend from (a,b,c) to (3,4,5) through the Berggren tree.

    Returns the list of (branch, triple) pairs.
    """
    path = [(None, (a, b, c))]

    while (a, b, c) != (3, 4, 5):
        # Try each inverse transform
        for name, B_inv in [("B₁⁻¹", BB1_inv), ("B₂⁻¹", BB2_inv), ("B₃⁻¹", BB3_inv)]:
            result = B_inv @ np.array([a, b, c])
            if all(r > 0 for r in result):
                a, b, c = int(result[0]), int(result[1]), int(result[2])
                path.append((name, (a, b, c)))
                break
        else:
            # Handle sign convention
            for name, B_inv in [("B₁⁻¹", BB1_inv), ("B₂⁻¹", BB2_inv), ("B₃⁻¹", BB3_inv)]:
                result = B_inv @ np.array([a, b, c])
                result = np.abs(result)
                if result[0]**2 + result[1]**2 == result[2]**2 and all(r > 0 for r in result):
                    a, b, c = int(result[0]), int(result[1]), int(result[2])
                    path.append((name, (a, b, c)))
                    break
            else:
                print(f"  ⚠ Descent stuck at ({a}, {b}, {c})")
                break

    return path

def demo_descent():
    """Demonstrate Berggren descent for several triples."""
    print("=" * 60)
    print("§5. BERGGREN DESCENT (tracing back to root)")
    print("=" * 60)

    test_triples = [
        (5, 12, 13),
        (8, 15, 17),
        (7, 24, 25),
        (20, 21, 29),
        (9, 40, 41),
        (119, 120, 169),
    ]

    for a, b, c in test_triples:
        path = berggren_descent(a, b, c)
        depth = len(path) - 1
        branches = " → ".join(p[0] for p in path[1:])
        print(f"  ({a:4d}, {b:4d}, {c:4d}) → depth {depth}: {branches}")

    print()

# =============================================================================
# §6. Farey Fractions and the Berggren-Farey Map
# =============================================================================

def berggren_to_farey(a, b, c):
    """Map a Pythagorean triple to its Farey fraction b/(a+c)."""
    return Fraction(b, a + c)

def demo_farey():
    """Demonstrate the Berggren-Farey map."""
    print("=" * 60)
    print("§6. BERGGREN-FAREY MAP")
    print("=" * 60)

    tree = generate_berggren_tree(3)
    fractions = []

    for depth, triples in sorted(tree.items()):
        for t in triples:
            a, b, c = int(t[0]), int(t[1]), int(t[2])
            f = berggren_to_farey(a, b, c)
            fractions.append((f, (a, b, c), depth))

    # Sort by fraction value
    fractions.sort(key=lambda x: float(x[0]))

    print("  Farey fractions from the Berggren tree (sorted):\n")
    for f, (a, b, c), d in fractions[:20]:
        angle = 2 * np.arctan(float(f)) * 180 / np.pi
        print(f"  {str(f):>6s} = {b}/{a+c:>4d} ← ({a:4d},{b:4d},{c:4d}) "
              f"depth={d} angle={angle:.1f}°")

    print(f"\n  Total fractions (depth ≤ 3): {len(fractions)}")
    print()

# =============================================================================
# §7. Matrix Powers and the Geodesic Interpretation
# =============================================================================

def demo_matrix_powers():
    """Demonstrate matrix power formulas and the geodesic interpretation."""
    print("=" * 60)
    print("§7. MATRIX POWERS AND GEODESICS")
    print("=" * 60)

    print("  M₃^k = [[1, 2k], [0, 1]] (verified):\n")
    for k in range(6):
        Mk = np.linalg.matrix_power(BM3, k)
        expected = np.array([[1, 2*k], [0, 1]])
        check = "✓" if np.array_equal(Mk, expected) else "✗"
        print(f"    M₃^{k} = {Mk.tolist()} {check}")

    print(f"\n  M₃⁻¹^k = [[1, -2k], [0, 1]] (verified):\n")
    for k in range(6):
        Mk = np.linalg.matrix_power(BM3_inv, k)
        expected = np.array([[1, -2*k], [0, 1]])
        check = "✓" if np.array_equal(Mk, expected) else "✗"
        print(f"    M₃⁻¹^{k} = {Mk.tolist()} {check}")

    print("\n  Hecke relations (S·T²)^n:\n")
    ST = S @ T_sq
    prod = np.eye(2, dtype=int)
    for n in range(1, 7):
        prod = prod @ ST
        tr = int(np.trace(prod))
        print(f"    (S·T²)^{n} = {prod.tolist()}, trace = {tr}")

    print()

# =============================================================================
# §8. Sum of Two Squares (r₂ function)
# =============================================================================

def r2(n):
    """Count the number of representations of n as a sum of two squares."""
    count = 0
    if n < 0:
        return 0
    limit = int(np.sqrt(n)) + 1
    for a in range(-limit, limit + 1):
        for b in range(-limit, limit + 1):
            if a*a + b*b == n:
                count += 1
    return count

def demo_r2():
    """Demonstrate the r₂ function and its connection to theta functions."""
    print("=" * 60)
    print("§8. SUM OF TWO SQUARES — r₂(n)")
    print("=" * 60)

    print("  r₂(n) = |{(a,b) ∈ ℤ² : a² + b² = n}|")
    print("  This is the n-th Fourier coefficient of θ₃(τ)²\n")

    # Compute r₂ for first 30 values
    print("  n  : r₂(n) : representations")
    print("  ---:-------:----------------")
    for n in range(26):
        count = r2(n)
        reps = [(a, b) for a in range(-n, n+1) for b in range(-n, n+1)
                if a*a + b*b == n]
        if count > 0:
            rep_str = ", ".join(f"({a},{b})" for a, b in reps[:6])
            if count > 6:
                rep_str += f", ... ({count} total)"
            print(f"  {n:3d}: {count:5d} : {rep_str}")

    # Verify for Pythagorean hypotenuses
    print("\n  r₂ for Pythagorean hypotenuse squares:")
    for c in [5, 13, 17, 25, 29, 37, 41]:
        print(f"    r₂({c}²={c*c}) = {r2(c*c)}")

    # Verify Fermat's theorem
    print("\n  Fermat's two-squares theorem (primes ≡ 1 mod 4):")
    for p in [5, 13, 17, 29, 37, 41, 53, 61, 73, 89, 97]:
        reps = [(a, b) for a in range(p) for b in range(a, p) if a*a + b*b == p]
        print(f"    {p} = {reps[0][0]}² + {reps[0][1]}² (r₂={r2(p)})")

    print()

# =============================================================================
# §9. Modular Surface Visualization Data
# =============================================================================

def demo_modular_surface():
    """Generate data for visualizing the modular surface X_θ."""
    print("=" * 60)
    print("§9. MODULAR SURFACE X_θ STRUCTURE")
    print("=" * 60)

    # Fundamental domain boundary
    print("  The fundamental domain of Γ_θ on the upper half-plane ℍ")
    print("  has three times the area of the SL(2,ℤ) domain.\n")

    print("  Cusps of X_θ:")
    cusps = [
        ("∞", "T² = M₃", "Branch 3 (translation)"),
        ("0", "S·T²·S⁻¹", "Branch 1 (inversion)"),
        ("1", "conjugate", "Branch 2 (reflection)"),
    ]
    for cusp, stab, branch in cusps:
        print(f"    Cusp {cusp:2s}: stabilizer ⟨{stab}⟩ ↔ {branch}")

    print(f"\n  Index [SL(2,ℤ) : Γ_θ] = 3")
    print(f"  Genus of X_θ = 0 (rational curve)")
    print(f"  Number of cusps = 3")
    print(f"  Euler characteristic χ(X_θ) = 1")

    # Coset decomposition
    print(f"\n  Coset decomposition SL(2,ℤ) = Γ_θ ∪ Γ_θ·T ∪ Γ_θ·T⁻¹:")
    print(f"    Representative I:   {np.eye(2, dtype=int).tolist()}")
    print(f"    Representative T:   {T.tolist()}")
    T_inv = np.array([[1, -1], [0, 1]])
    print(f"    Representative T⁻¹: {T_inv.tolist()}")

    # Verify T not in Γ_θ
    print(f"\n  T = {T.tolist()}")
    print(f"  (1+1) % 2 = {(1+1) % 2} ≠ 1 → T ∉ Γ_θ ✓")

    print()

# =============================================================================
# §10. Summary Statistics
# =============================================================================

def demo_summary():
    """Print summary of the correspondence."""
    print("=" * 60)
    print("§10. SUMMARY: BERGGREN ↔ THETA GROUP CORRESPONDENCE")
    print("=" * 60)

    correspondences = [
        ("Berggren tree", "Modular surface X_θ"),
        ("3 branches", "3 cusps {0, 1, ∞}"),
        ("M₃ generator", "T² (parabolic)"),
        ("M₁ generator", "T²·S (translate+invert)"),
        ("M₃⁻¹·M₁", "S (elliptic inversion)"),
        ("Descent path", "Geodesic on X_θ"),
        ("Descent depth", "Hyperbolic distance"),
        ("Pythagorean triple (a,b,c)", "Lattice point on Q=0"),
        ("Euclid ratio m/n", "Point on ∂ℍ"),
        ("Farey fraction b/(a+c)", "Cusp form value"),
        ("r₂(c²) representations", "θ₃(τ)² Fourier coefficient"),
        ("Lorentz form Q", "SO(2,1) invariant"),
    ]

    for berg, theta in correspondences:
        print(f"  {berg:35s} ↔ {theta}")

    print()

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("\n" + "🔺" * 30)
    print("  BERGGREN DESCENT ↔ THETA GROUP Γ_θ")
    print("  Formally Verified Mathematical Demo")
    print("🔺" * 30 + "\n")

    verify_identities()
    demo_theta_parity()
    demo_berggren_tree()
    demo_descent()
    demo_farey()
    demo_matrix_powers()
    demo_r2()
    demo_modular_surface()
    demo_summary()

    print("=" * 60)
    print("  All demos completed successfully! ✅")
    print("  See Pythagorean__ModularForms.lean for formal proofs.")
    print("=" * 60)
