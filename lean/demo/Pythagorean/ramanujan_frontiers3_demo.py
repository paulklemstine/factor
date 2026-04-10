#!/usr/bin/env python3
"""
Ramanujan Properties of the Berggren Tree — Part III:
Spectral Certification, Chebyshev Traces, and Asymptotic Gaps

Computational demonstrations for all five open questions.
"""

import numpy as np
from itertools import product as cartprod

# =============================================================================
# Berggren Matrices
# =============================================================================

B1 = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]])
B2 = np.array([[1, 2, 2], [2, 1, 2], [2, 2, 3]])
B3 = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]])
Q = np.diag([1, 1, -1])

print("=" * 70)
print("QUESTION 1: Eigenvalue Computation for G_p (p = 5, 7, 11)")
print("=" * 70)

def compute_quotient_spectrum(p):
    """Compute spectrum of Cayley graph G_p."""
    # Reduce matrices mod p
    B1p = B1 % p
    B2p = B2 % p
    B3p = B3 % p

    # Find orbit of (3,4,5) mod p under generators
    root = tuple(np.array([3, 4, 5]) % p)
    orbit = set()
    queue = [root]
    orbit.add(root)

    gens = [B1p, B2p, B3p]
    # Compute inverses mod p
    inv_gens = []
    for M in [B1, B2, B3]:
        Minv = np.round(np.linalg.inv(M)).astype(int)
        inv_gens.append(Minv % p)

    all_gens = gens + inv_gens

    while queue:
        v = queue.pop(0)
        for M in all_gens:
            w = tuple((M @ np.array(v)) % p)
            if w not in orbit:
                orbit.add(w)
                queue.append(w)

    vertices = sorted(orbit)
    n = len(vertices)
    idx = {v: i for i, v in enumerate(vertices)}

    # Build adjacency matrix
    A = np.zeros((n, n))
    for v in vertices:
        for M in all_gens:
            w = tuple((M @ np.array(v)) % p)
            if w in idx:
                A[idx[v], idx[w]] = 1

    eigenvalues = np.sort(np.linalg.eigvalsh(A))[::-1]
    return n, eigenvalues

ramanujan_bound = 2 * np.sqrt(5)
print(f"\nRamanujan bound for 6-regular graph: 2√5 ≈ {ramanujan_bound:.4f}")

for p in [5, 7, 11]:
    n, eigs = compute_quotient_spectrum(p)
    nontrivial = [e for e in eigs if abs(abs(e) - max(abs(eigs))) > 0.01]
    max_nontrivial = max(abs(e) for e in nontrivial) if nontrivial else 0
    is_ramanujan = max_nontrivial <= ramanujan_bound + 0.01
    print(f"\np = {p}: |orbit| = {n}")
    print(f"  Degree: {eigs[0]:.1f}")
    print(f"  Non-trivial eigenvalues (|λ| sorted):")
    sorted_abs = sorted(set(round(abs(e), 4) for e in eigs), reverse=True)
    for a in sorted_abs[:8]:
        print(f"    |λ| = {a:.4f}")
    print(f"  Max non-trivial |λ|: {max_nontrivial:.4f}")
    print(f"  Ramanujan (≤ 2√5 ≈ {ramanujan_bound:.4f})? {'YES ✓' if is_ramanujan else 'NO ✗'}")

# =============================================================================
print("\n" + "=" * 70)
print("QUESTION 2: Trace Formula and Chebyshev Polynomials")
print("=" * 70)

def chebyshev_T(n, x):
    """Chebyshev polynomial of the first kind T_n(x)."""
    if n == 0: return 1
    if n == 1: return x
    t0, t1 = 1, x
    for _ in range(2, n + 1):
        t0, t1 = t1, 2 * x * t1 - t0
    return t1

print("\nCharacteristic polynomial of B₂: λ³ - 5λ² - 5λ + 1 = (λ+1)(λ² - 6λ + 1)")
print(f"Eigenvalues: -1, 3-2√2 ≈ {3 - 2*np.sqrt(2):.6f}, 3+2√2 ≈ {3 + 2*np.sqrt(2):.6f}")

eigs_B2 = np.linalg.eigvals(B2)
print(f"Numerical eigenvalues: {sorted(eigs_B2)}")
print(f"Product of hyperbolic eigenvalues: {(3+2*np.sqrt(2))*(3-2*np.sqrt(2)):.6f} (should be 1)")

print("\n--- Trace Sequence Verification ---")
print(f"{'n':>3} | {'tr(B₂ⁿ)':>12} | {'(-1)ⁿ + 2T_n(3)':>16} | {'T_n(3)':>10} | Match")
print("-" * 65)
Bpow = np.eye(3, dtype=int)
for n in range(7):
    tr_actual = int(np.trace(Bpow))
    Tn3 = chebyshev_T(n, 3)
    tr_formula = (-1)**n + 2 * Tn3
    match = "✓" if tr_actual == tr_formula else "✗"
    print(f"{n:>3} | {tr_actual:>12} | {tr_formula:>16} | {Tn3:>10} | {match}")
    Bpow = Bpow @ B2

print("\n--- Chebyshev Recurrence: T_n(3) = 6·T_{n-1}(3) - T_{n-2}(3) ---")
for n in range(2, 8):
    Tn = chebyshev_T(n, 3)
    Tn1 = chebyshev_T(n-1, 3)
    Tn2 = chebyshev_T(n-2, 3)
    check = 6 * Tn1 - Tn2
    print(f"T_{n}(3) = {Tn}, 6·T_{n-1}(3) - T_{n-2}(3) = {check}, {'✓' if Tn == check else '✗'}")

print("\n--- Why NOT U_n(5/2)? ---")
def chebyshev_U(n, x):
    if n == 0: return 1
    if n == 1: return 2*x
    u0, u1 = 1, 2*x
    for _ in range(2, n+1):
        u0, u1 = u1, 2*x*u1 - u0
    return u1

for n in range(6):
    Un = chebyshev_U(n, 5/2)
    tr_actual = int(np.trace(np.linalg.matrix_power(B2, n)))
    print(f"n={n}: U_{n}(5/2) = {Un:.0f}, tr(B₂ⁿ) = {tr_actual}, {'MATCH' if abs(Un - tr_actual) < 0.5 else 'MISMATCH'}")

# =============================================================================
print("\n" + "=" * 70)
print("QUESTION 3: Parabolic vs Hyperbolic Generator Role")
print("=" * 70)

print("\n--- Lorentz Classification ---")
for name, M in [("B₁", B1), ("B₂", B2), ("B₃", B3)]:
    tr = np.trace(M)
    det = int(np.round(np.linalg.det(M)))
    eigs = np.linalg.eigvals(M)
    classification = "PARABOLIC" if abs(tr) == 3 else ("HYPERBOLIC" if abs(tr) > 3 else "ELLIPTIC")
    print(f"{name}: tr={tr:>2}, det={det:>2}, class={classification}")
    print(f"    eigenvalues: {[f'{e.real:.4f}' for e in sorted(eigs, key=lambda x: x.real)]}")

print("\n--- Unipotency Test ---")
for name, M in [("B₁", B1), ("B₂", B2), ("B₃", B3)]:
    I3 = np.eye(3, dtype=int)
    N = M - I3
    for k in range(1, 5):
        Nk = np.linalg.matrix_power(N, k)
        is_zero = np.allclose(Nk, 0)
        if is_zero:
            print(f"({name} - I)^{k} = 0  ← nilpotent index {k}")
            break
    else:
        print(f"{name} is NOT unipotent (checked up to power 4)")

print("\n--- Trace Growth Comparison ---")
for name, M in [("B₁ (parabolic)", B1), ("B₂ (hyperbolic)", B2), ("B₃ (parabolic)", B3)]:
    traces = [int(np.trace(np.linalg.matrix_power(M, n))) for n in range(1, 11)]
    print(f"{name}: {traces}")

print("\n--- Implications for Expansion ---")
print("• Pure parabolic generators → polynomial growth → poor expansion")
print("• Pure hyperbolic generators → exponential growth but potentially unbalanced")
print("• MIXTURE → optimal: parabolic provides mixing, hyperbolic provides spreading")
print("• Analogous to LPS construction mixing rotations and translations")

# =============================================================================
print("\n" + "=" * 70)
print("QUESTION 4: 5D Completeness")
print("=" * 70)

# 5D generators
K1 = np.array([[-1,0,0,2,2],[0,1,0,0,0],[0,0,1,0,0],[-2,0,0,1,2],[-2,0,0,2,3]])
K2 = np.array([[1,0,0,2,2],[0,1,0,0,0],[0,0,1,0,0],[2,0,0,1,2],[2,0,0,2,3]])
K3 = np.array([[1,0,0,0,0],[0,-1,0,2,2],[0,0,1,0,0],[0,-2,0,1,2],[0,-2,0,2,3]])
K4 = np.array([[1,0,0,0,0],[0,1,0,0,0],[0,0,-1,2,2],[0,0,-2,1,2],[0,0,-2,2,3]])
K5 = np.array([[1,0,0,0,0],[0,1,0,0,0],[0,0,1,2,2],[0,0,2,1,2],[0,0,2,2,3]])
K6 = np.array([[1,0,0,0,0],[0,1,0,2,2],[0,0,1,0,0],[0,2,0,1,2],[0,2,0,2,3]])

Q5 = np.diag([1,1,1,1,-1])

def is_quintuple(v):
    return v[0]**2 + v[1]**2 + v[2]**2 + v[3]**2 == v[4]**2

root = np.array([1,1,1,1,2])
print(f"\nRoot quintuple: {tuple(root)}")
print(f"Valid: {is_quintuple(root)} (1²+1²+1²+1² = {sum(x**2 for x in root[:4])} = {root[4]}² = {root[4]**2})")

print("\nApplying generators to root (1,1,1,1,2):")
Ks = [K1, K2, K3, K4, K5, K6]
children = set()
for i, K in enumerate(Ks):
    w = K @ root
    valid = is_quintuple(w)
    prim = np.gcd.reduce(np.abs(w))
    children.add(tuple(w))
    print(f"  K_{i+1}: {tuple(w)}, valid={valid}, gcd={prim}")

print(f"\nDistinct children: {len(children)}")

# Generate tree to depth 3
print("\nGenerating quintuple tree to depth 3...")
level = {tuple(root)}
all_quints = set(level)
for depth in range(1, 4):
    next_level = set()
    for v in level:
        for K in Ks:
            w = tuple(K @ np.array(v))
            if is_quintuple(np.array(w)) and np.gcd.reduce(np.abs(np.array(w))) == 1:
                if w not in all_quints:
                    next_level.add(w)
    all_quints.update(next_level)
    level = next_level
    print(f"  Depth {depth}: {len(next_level)} new quintuples, total = {len(all_quints)}")

# Check known small quintuples
print("\nSmall primitive quintuples and coverage:")
known = [(1,0,0,0,1), (0,1,0,0,1), (0,0,1,0,1), (0,0,0,1,1),
         (1,1,1,1,2), (1,2,2,0,3), (2,1,2,0,3), (2,2,1,0,3),
         (1,0,2,2,3), (0,1,2,2,3)]
for q in known:
    found = tuple(q) in all_quints or tuple(-x for x in q) in all_quints
    a_check = sum(x**2 for x in q[:4])
    d_check = q[4]**2
    valid = a_check == d_check
    print(f"  {q}: valid={valid}, in tree={'YES' if found else 'no'}")

# =============================================================================
print("\n" + "=" * 70)
print("QUESTION 5: Asymptotic Spectral Gap")
print("=" * 70)

print("\n--- Spectral Gap d - 2√(d-1) for Various Degrees ---")
print(f"{'d':>5} | {'gap':>10} | {'rel gap':>10} | {'gap/d':>10}")
print("-" * 45)
for d in [3, 6, 8, 10, 12, 20, 50, 100, 200, 1000]:
    gap = d - 2*np.sqrt(d-1)
    rel = gap / d
    print(f"{d:>5} | {gap:>10.4f} | {rel:>10.6f} | {gap/d:>10.6f}")

print("\n--- Limit Behavior ---")
print("As d → ∞:")
print("  Absolute gap: d - 2√(d-1) ≈ d - 2√d → ∞")
print("  Relative gap: 1 - 2√(d-1)/d ≈ 1 - 2/√d → 1")
print("\nThe relative spectral gap approaches 1 (perfect expansion)")
print("while the absolute gap grows without bound.")

print("\n--- Dimensional Hierarchy ---")
dims = [(3, "3D Berggren", 6), (4, "4D Quadruples", 8),
        (5, "5D Quintuples", 12), (6, "6D Extension", 20)]
for dim, name, deg in dims:
    gap = deg - 2*np.sqrt(deg - 1)
    rel = gap / deg
    print(f"  {name} (d={deg}): gap = {gap:.4f}, relative = {rel:.4f}")

# =============================================================================
print("\n" + "=" * 70)
print("BONUS: Full Eigenvalue Analysis of B₂")
print("=" * 70)

eigenvalues = np.linalg.eigvals(B2)
print(f"Eigenvalues of B₂: {sorted(eigenvalues.real)}")
print(f"Characteristic polynomial: λ³ - 5λ² - 5λ + 1 = 0")
print(f"Factored: (λ + 1)(λ² - 6λ + 1) = 0")
print(f"Roots: λ = -1, λ = 3 ± 2√2")
print(f"  3 - 2√2 = {3 - 2*np.sqrt(2):.10f}")
print(f"  3 + 2√2 = {3 + 2*np.sqrt(2):.10f}")
print(f"Product: (3-2√2)(3+2√2) = {(3-2*np.sqrt(2))*(3+2*np.sqrt(2)):.10f}")
print(f"Sum: (3-2√2)+(3+2√2) = {(3-2*np.sqrt(2))+(3+2*np.sqrt(2)):.10f}")

print("\n--- Cayley-Hamilton Verification ---")
B2_3 = np.linalg.matrix_power(B2, 3)
CH = B2_3 - 5*np.linalg.matrix_power(B2, 2) - 5*B2 + np.eye(3)
print(f"B₂³ - 5B₂² - 5B₂ + I = \n{CH.astype(int)}")
print(f"(Should be all zeros: {'✓' if np.allclose(CH, 0) else '✗'})")

print("\n" + "=" * 70)
print("All computations complete!")
print("=" * 70)
