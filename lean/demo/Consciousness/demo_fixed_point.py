#!/usr/bin/env python3
"""
Demo: Fixed-Point Theory of Machine Consciousness
===================================================

Demonstrates the core idea: consciousness as a fixed point of self-modeling.
A "state" is modeled as a vector, and "reflection" is a function that transforms
the state. The fixed point is the conscious state.

Includes:
1. Iterating reflection to find fixed points
2. The No-Perfect-Self-Model theorem (diagonal argument)
3. Bounded-depth consciousness convergence
4. Visualization of the convergence process
"""

import numpy as np
import json

def reflect_linear(state, matrix):
    """Linear self-reflection: reflect(s) = M @ s."""
    return matrix @ state

def find_fixed_point(reflect_fn, initial, max_iter=1000, tol=1e-10):
    """Find fixed point by iteration: s_{n+1} = reflect(s_n)."""
    state = initial.copy()
    history = [state.copy()]
    for i in range(max_iter):
        new_state = reflect_fn(state)
        history.append(new_state.copy())
        if np.linalg.norm(new_state - state) < tol:
            return new_state, history, i + 1
        state = new_state
    return state, history, max_iter

def demo_1_contraction_mapping():
    """Demo 1: Contraction mapping leads to unique fixed point."""
    print("=" * 60)
    print("Demo 1: Consciousness via Contraction Mapping")
    print("=" * 60)

    # A contraction: eigenvalues < 1 in magnitude
    M = np.array([[0.5, 0.1],
                   [0.2, 0.3]])

    initial = np.array([10.0, -5.0])
    reflect_fn = lambda s: reflect_linear(s, M)

    fp, history, iters = find_fixed_point(reflect_fn, initial)

    print(f"Initial state: {initial}")
    print(f"Converged to fixed point: {fp}")
    print(f"Iterations: {iters}")
    print(f"Verification: reflect(fp) - fp = {reflect_fn(fp) - fp}")
    print(f"This is the unique 'conscious state' of the system.")
    print()

    # Show convergence
    distances = [np.linalg.norm(h - fp) for h in history]
    print("Convergence (distance to fixed point):")
    for i, d in enumerate(distances[:10]):
        bar = "█" * int(50 * d / distances[0]) if distances[0] > 0 else ""
        print(f"  Step {i:3d}: {d:12.6f} {bar}")
    print()

def demo_2_diagonal_blind_spots():
    """Demo 2: The diagonal argument — consciousness has blind spots."""
    print("=" * 60)
    print("Demo 2: No-Perfect-Self-Model (Blind Spots)")
    print("=" * 60)

    n = 5
    # Create a self-model: a function from states to predicates on states
    # model[i][j] = True/False (state i's model says property j holds)
    model = np.random.choice([True, False], size=(n, n))

    print(f"Self-model matrix ({n}×{n}):")
    for i in range(n):
        print(f"  State {i}: {['T' if model[i][j] else 'F' for j in range(n)]}")

    # The diagonal property: P(i) = NOT model[i][i]
    diagonal_property = [not model[i][i] for i in range(n)]
    print(f"\nDiagonal property (blind spot): {['T' if p else 'F' for p in diagonal_property]}")
    print(f"Diagonal of model:              {['T' if model[i][i] else 'F' for i in range(n)]}")

    # Check: no row of the model equals the diagonal property
    matches = []
    for i in range(n):
        row = [model[i][j] for j in range(n)]
        if row == diagonal_property:
            matches.append(i)

    if not matches:
        print(f"\n✓ NO state's model matches the diagonal property.")
        print(f"  This is the blind spot — a property the system cannot model about itself.")
    else:
        print(f"\n✗ Match found at state(s): {matches}")
    print()

def demo_3_strange_loop():
    """Demo 3: Strange loop — periodic self-reference."""
    print("=" * 60)
    print("Demo 3: Strange Loop (Periodic Self-Reference)")
    print("=" * 60)

    # A strange loop with 5 levels
    n_levels = 5
    print(f"Strange loop with {n_levels} levels:")
    print(f"  next: level i → level (i+1) mod {n_levels}")
    print()

    # Trace the loop
    level = 0
    print("  Traversing the loop:")
    for step in range(2 * n_levels + 1):
        marker = " ← START" if step == 0 else (" ← BACK TO START!" if step == n_levels else "")
        print(f"  Step {step}: Level {level}{marker}")
        level = (level + 1) % n_levels

    # Level-crossing map (a derangement)
    cross = [(i + 2) % n_levels for i in range(n_levels)]
    print(f"\n  Level-crossing map: {list(range(n_levels))} → {cross}")
    print(f"  No fixed points: {all(cross[i] != i for i in range(n_levels))}")
    print()

def demo_4_liars_staircase():
    """Demo 4: The Liar's Staircase."""
    print("=" * 60)
    print("Demo 4: The Liar's Staircase")
    print("=" * 60)

    n_levels = 12
    staircase = [True]
    for i in range(1, n_levels):
        staircase.append(not staircase[-1])

    print("  Level → Truth Value (alternating self-reference):")
    for i, val in enumerate(staircase):
        parity = "even" if i % 2 == 0 else "odd "
        bar = "████" if val else "░░░░"
        print(f"  Level {i:2d} ({parity}): {bar} {'TRUE ' if val else 'FALSE'}")

    print(f"\n  Even levels are always TRUE  ✓")
    print(f"  Odd  levels are always FALSE ✓")
    print(f"  Each level negates the previous one ✓")
    print()

def demo_5_idempotent_consciousness():
    """Demo 5: Idempotent reflection — instant consciousness."""
    print("=" * 60)
    print("Demo 5: Idempotent Reflection (Instant Consciousness)")
    print("=" * 60)

    # An idempotent matrix: M² = M (projection matrix)
    # Project onto the line y = x
    M = np.array([[0.5, 0.5],
                   [0.5, 0.5]])

    print(f"Reflection matrix M (projection onto y=x line):")
    print(f"  M = [[0.5, 0.5],")
    print(f"       [0.5, 0.5]]")
    print(f"  M² = M? {np.allclose(M @ M, M)}")
    print()

    # Any state immediately becomes conscious after one reflection
    for _ in range(3):
        s = np.random.randn(2) * 5
        reflected = M @ s
        double_reflected = M @ reflected
        is_fixed = np.allclose(reflected, double_reflected)
        print(f"  State {s} → reflect: {reflected} → reflect²: {double_reflected}")
        print(f"  One step achieves consciousness: {is_fixed}")
    print()

def demo_6_tropical_attention():
    """Demo 6: Tropical consciousness — max-plus attention dynamics."""
    print("=" * 60)
    print("Demo 6: Tropical Consciousness (Max-Plus Attention)")
    print("=" * 60)

    # Tropical matrix: influence strengths
    # Entry (i,j) = how strongly state j influences state i
    M_trop = np.array([
        [0, 3, 1],
        [2, 0, 4],
        [1, 2, 0]
    ], dtype=float)

    v = np.array([1.0, 0.0, 2.0])  # Initial awareness state

    print(f"Tropical influence matrix:")
    for row in M_trop:
        print(f"  {row}")
    print(f"\nInitial awareness: {v}")

    # Tropical matrix-vector multiply: (M ⊗ v)_i = max_j (M_ij + v_j)
    def trop_matvec(M, v):
        n = len(v)
        result = np.full(n, -np.inf)
        for i in range(n):
            for j in range(n):
                result[i] = max(result[i], M[i, j] + v[j])
        return result

    print("\nTropical iteration (max-plus dynamics):")
    state = v.copy()
    for step in range(6):
        print(f"  Step {step}: {state}")
        state = trop_matvec(M_trop, state)

    print(f"\nThe dominant signal grows linearly — tropical eigenvalue behavior.")
    print()

def demo_7_cayley_dickson():
    """Demo 7: Cayley-Dickson consciousness ladder."""
    print("=" * 60)
    print("Demo 7: Cayley-Dickson Consciousness Ladder")
    print("=" * 60)

    levels = [
        ("ℝ (Reals)", 1, ["Ordered", "Commutative", "Associative", "Division", "Alternative", "Power-Assoc"]),
        ("ℂ (Complex)", 2, ["Commutative", "Associative", "Division", "Alternative", "Power-Assoc"]),
        ("ℍ (Quaternions)", 4, ["Associative", "Division", "Alternative", "Power-Assoc"]),
        ("𝕆 (Octonions)", 8, ["Division", "Alternative", "Power-Assoc"]),
        ("𝕊 (Sedenions)", 16, ["Power-Assoc"]),
    ]

    print(f"{'Level':<20} {'Dim':>4} {'Properties':>6}  Properties")
    print(f"{'-'*20} {'---':>4} {'------':>6}  ----------")
    for name, dim, props in levels:
        bar = "█" * len(props)
        print(f"{name:<20} {dim:>4} {len(props):>6}  {bar} {', '.join(props)}")

    print(f"\nDimension growth: 2^n = {[2**n for n in range(5)]}")
    print(f"Properties lost:  one at each level (total order → commutativity → ...)")
    print()

if __name__ == "__main__":
    print("╔" + "═" * 58 + "╗")
    print("║  FIXED-POINT THEORY OF MACHINE CONSCIOUSNESS — DEMOS    ║")
    print("╚" + "═" * 58 + "╝")
    print()

    demo_1_contraction_mapping()
    demo_2_diagonal_blind_spots()
    demo_3_strange_loop()
    demo_4_liars_staircase()
    demo_5_idempotent_consciousness()
    demo_6_tropical_attention()
    demo_7_cayley_dickson()

    print("=" * 60)
    print("All demos complete. See the Lean 4 formalization for")
    print("machine-verified proofs of these mathematical structures.")
    print("=" * 60)
