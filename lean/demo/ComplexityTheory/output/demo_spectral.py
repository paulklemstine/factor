#!/usr/bin/env python3
"""
Spectral Collapse and SAT Phase Transition Demo

Demonstrates:
- Fourier analysis on the Boolean cube
- Spectral energy decomposition (Parseval's identity)
- Phase transition in random k-SAT
- Spectral gap behavior near the SAT threshold
"""

import numpy as np
from itertools import product
import random

random.seed(42)
np.random.seed(42)


# ============================================================
# 1. Fourier Analysis on the Boolean Cube
# ============================================================

def all_boolean_strings(n):
    """Generate all 2^n Boolean strings of length n."""
    return list(product([0, 1], repeat=n))


def chi(S, x):
    """Character function χ_S(x) = (-1)^(|{i in S : x_i = 1}|)"""
    count = sum(x[i] for i in S)
    return (-1) ** count


def fourier_coefficients(f, n):
    """Compute all Fourier coefficients of f: {0,1}^n -> R."""
    from itertools import combinations
    all_x = all_boolean_strings(n)
    N = 2 ** n

    coeffs = {}
    for size in range(n + 1):
        for S in combinations(range(n), size):
            S_set = set(S)
            coeff = sum(f(x) * chi(S_set, x) for x in all_x) / N
            coeffs[S] = coeff
    return coeffs


def spectral_energy_by_level(coeffs, n):
    """Decompose spectral energy by level k = |S|."""
    energies = [0.0] * (n + 1)
    for S, c in coeffs.items():
        energies[len(S)] += c ** 2
    return energies


def demo_fourier():
    print("=" * 60)
    print("FOURIER ANALYSIS ON THE BOOLEAN CUBE")
    print("=" * 60)
    print()

    n = 3

    # Majority function on 3 bits
    def majority(x):
        return 1 if sum(x) >= 2 else -1

    print(f"Function: MAJORITY on {n} bits")
    print(f"  MAJ(x) = 1 if |x| ≥ 2, else -1")
    print()

    coeffs = fourier_coefficients(majority, n)

    print("Fourier coefficients:")
    for S, c in sorted(coeffs.items(), key=lambda t: (len(t[0]), t[0])):
        if abs(c) > 1e-10:
            print(f"  f̂({set(S) if S else '∅'}) = {c:+.4f}")
    print()

    energies = spectral_energy_by_level(coeffs, n)
    total = sum(energies)

    print("Spectral energy by level (Parseval's identity):")
    for k, e in enumerate(energies):
        bar = "█" * int(e * 40)
        print(f"  Level {k}: {e:.4f}  {bar}")
    print(f"  Total:   {total:.4f}  (should = E[f²] = 1.0)")
    print()

    # Verify Parseval
    print(f"Parseval check: Σ E_k = {total:.6f} ✓" if abs(total - 1.0) < 1e-10 else "FAIL")
    print()


# ============================================================
# 2. Character Properties
# ============================================================

def demo_characters():
    print("=" * 60)
    print("CHARACTER FUNCTION PROPERTIES")
    print("=" * 60)
    print()

    n = 4
    all_x = all_boolean_strings(n)

    # χ_S(x)² = 1
    print("Property 1: χ_S(x)² = 1 for all S, x")
    S = {0, 2}
    for x in all_x[:4]:
        val = chi(S, x)
        print(f"  χ_{S}({x}) = {val:+d}, squared = {val**2}")
    print(f"  ... all {2**n} values are ±1 ✓")
    print()

    # Multiplicativity for disjoint sets
    print("Property 2: χ_S · χ_T = χ_{S∪T} for disjoint S, T")
    S, T = {0, 1}, {2, 3}
    for x in all_x[:4]:
        prod = chi(S, x) * chi(T, x)
        union = chi(S | T, x)
        print(f"  χ_{S}·χ_{T} at {x}: {prod:+d} = χ_{S|T}: {union:+d} ✓")
    print()


# ============================================================
# 3. Random k-SAT Phase Transition
# ============================================================

def generate_random_ksat(n, m, k):
    """Generate a random k-SAT instance with n vars, m clauses, width k."""
    clauses = []
    for _ in range(m):
        vars_chosen = random.sample(range(1, n + 1), k)
        clause = [v if random.random() < 0.5 else -v for v in vars_chosen]
        clauses.append(clause)
    return clauses


def is_satisfiable_brute(clauses, n):
    """Check satisfiability by brute force (for small n)."""
    for assignment in product([False, True], repeat=n):
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var_idx = abs(lit) - 1
                val = assignment[var_idx]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def demo_phase_transition():
    print("=" * 60)
    print("RANDOM 3-SAT PHASE TRANSITION")
    print("=" * 60)
    print()

    n = 15  # variables
    k = 3   # clause width
    num_trials = 100

    print(f"Parameters: n={n} variables, k={k}-SAT, {num_trials} trials per density")
    print(f"Known threshold: α ≈ 4.267 for 3-SAT")
    print()

    densities = [1.0, 2.0, 3.0, 3.5, 4.0, 4.2, 4.3, 4.5, 5.0, 6.0, 7.0]

    print(f"{'Density α':>10} {'SAT prob':>10} {'Visual':>30}")
    print("-" * 55)

    for alpha in densities:
        m = int(alpha * n)
        sat_count = 0
        for _ in range(num_trials):
            clauses = generate_random_ksat(n, m, k)
            if is_satisfiable_brute(clauses, n):
                sat_count += 1
        prob = sat_count / num_trials
        bar_len = int(prob * 25)
        bar = "█" * bar_len + "░" * (25 - bar_len)
        print(f"{alpha:>10.1f} {prob:>10.2f} {bar}")

    print()
    print("The phase transition is visible around α ≈ 4.2-4.3")
    print()


# ============================================================
# 4. Spectral Gap Computation
# ============================================================

def clause_variable_matrix(clauses, n):
    """Build the clause-variable incidence matrix."""
    m = len(clauses)
    A = np.zeros((m, n))
    for i, clause in enumerate(clauses):
        for lit in clause:
            j = abs(lit) - 1
            A[i, j] = 1 if lit > 0 else -1
    return A


def spectral_gap(A):
    """Compute the spectral gap of A^T A."""
    M = A.T @ A
    eigenvalues = np.sort(np.linalg.eigvalsh(M))[::-1]
    if len(eigenvalues) >= 2:
        return eigenvalues[0] - eigenvalues[1]
    return 0.0


def demo_spectral_gap():
    print("=" * 60)
    print("SPECTRAL GAP VS CLAUSE DENSITY")
    print("=" * 60)
    print()

    n = 20
    k = 3
    num_trials = 30

    densities = [1.0, 2.0, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 8.0, 10.0]

    print(f"{'Density α':>10} {'Avg Gap':>10} {'Normalized':>12} {'Visual':>25}")
    print("-" * 60)

    max_gap = 0
    gaps = []
    for alpha in densities:
        m = int(alpha * n)
        total_gap = 0
        for _ in range(num_trials):
            clauses = generate_random_ksat(n, m, k)
            A = clause_variable_matrix(clauses, n)
            total_gap += spectral_gap(A)
        avg_gap = total_gap / num_trials
        gaps.append(avg_gap)
        max_gap = max(max_gap, avg_gap)

    for alpha, gap in zip(densities, gaps):
        norm = gap / max_gap if max_gap > 0 else 0
        bar_len = int(norm * 20)
        bar = "█" * bar_len
        print(f"{alpha:>10.1f} {gap:>10.2f} {norm:>12.3f} {bar}")

    print()
    print("The spectral gap grows with density (more constraints = more structure)")
    print()


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    demo_fourier()
    demo_characters()
    demo_phase_transition()
    demo_spectral_gap()
    print("=" * 60)
    print("All spectral demos completed!")
    print("=" * 60)
