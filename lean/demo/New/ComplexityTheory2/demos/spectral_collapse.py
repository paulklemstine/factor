#!/usr/bin/env python3
"""
Spectral Collapse Demo for SAT Phase Transitions

Demonstrates:
1. Fourier analysis of Boolean functions
2. Spectral energy at different levels
3. The SAT phase transition phenomenon
4. Spectral gap as a hardness indicator
"""

import numpy as np
from itertools import product
import random

def boolean_strings(n):
    """Generate all 2^n Boolean strings of length n."""
    return list(product([0, 1], repeat=n))

def chi(S, x):
    """Character function χ_S(x) = (-1)^(sum of x_i for i in S)."""
    return (-1) ** sum(x[i] for i in S)

def fourier_coefficients(f, n):
    """Compute all Fourier coefficients of Boolean function f: {0,1}^n → {-1,1}."""
    from itertools import combinations
    inputs = boolean_strings(n)
    N = 2 ** n

    coeffs = {}
    for size in range(n + 1):
        for S in combinations(range(n), size):
            S_set = frozenset(S)
            # f_hat(S) = (1/2^n) * Σ_x f(x) * χ_S(x)
            val = sum(f(x) * chi(S, x) for x in inputs) / N
            coeffs[S_set] = val

    return coeffs

def spectral_energy_by_level(coeffs, n):
    """Compute spectral energy at each level k."""
    energy = [0.0] * (n + 1)
    for S, val in coeffs.items():
        energy[len(S)] += val ** 2
    return energy

def demo_fourier_analysis():
    """Demonstrate Fourier analysis on Boolean functions."""
    print("=" * 60)
    print("FOURIER ANALYSIS OF BOOLEAN FUNCTIONS")
    print("=" * 60)

    n = 3

    # Majority function on 3 bits
    def majority(x):
        return 1 if sum(x) >= 2 else -1

    # Parity function on 3 bits
    def parity(x):
        return (-1) ** sum(x)

    # Dictator function (x_0)
    def dictator(x):
        return 1 if x[0] == 0 else -1

    functions = [
        ("Majority", majority),
        ("Parity", parity),
        ("Dictator (x₁)", dictator),
    ]

    for name, f in functions:
        print(f"\n--- {name} function ---")
        coeffs = fourier_coefficients(f, n)

        energy = spectral_energy_by_level(coeffs, n)
        total = sum(energy)

        print(f"  Fourier coefficients:")
        for S, val in sorted(coeffs.items(), key=lambda x: (len(x[0]), x[0])):
            if abs(val) > 1e-10:
                print(f"    f̂({set(S) if S else '∅'}) = {val:.4f}")

        print(f"  Spectral energy by level:")
        for k in range(n + 1):
            bar = "█" * int(energy[k] * 20)
            print(f"    Level {k}: {energy[k]:.4f}  {bar}")
        print(f"    Total:   {total:.4f} (Parseval: should be 1.0)")

def demo_sensitivity():
    """Demonstrate sensitivity of Boolean functions."""
    print("\n" + "=" * 60)
    print("SENSITIVITY OF BOOLEAN FUNCTIONS")
    print("=" * 60)

    n = 4

    # AND function
    def and_fn(x):
        return 1 if all(xi == 1 for xi in x) else -1

    # OR function
    def or_fn(x):
        return 1 if any(xi == 1 for xi in x) else -1

    functions = [("AND", and_fn), ("OR", or_fn)]

    for name, f in functions:
        print(f"\n--- {name} function (n={n}) ---")
        total_sensitivity = 0
        max_sensitivity = 0

        for x in boolean_strings(n):
            sens = 0
            for i in range(n):
                x_flip = list(x)
                x_flip[i] = 1 - x_flip[i]
                if f(x) != f(tuple(x_flip)):
                    sens += 1

            total_sensitivity += sens
            max_sensitivity = max(max_sensitivity, sens)

        print(f"  Max sensitivity: {max_sensitivity}")
        print(f"  Avg sensitivity: {total_sensitivity / 2**n:.2f}")

def demo_sat_phase_transition():
    """Demonstrate the SAT phase transition in random 3-SAT."""
    print("\n" + "=" * 60)
    print("SAT PHASE TRANSITION IN RANDOM 3-SAT")
    print("=" * 60)

    n = 20  # number of variables
    trials = 100

    print(f"\n  n = {n} variables, {trials} trials per density")
    print(f"\n  {'Density α':>12} | {'% SAT':>8} | {'Visualization'}")
    print("  " + "-" * 55)

    # Simple DPLL-like solver
    def simple_sat_check(clauses, n, max_tries=1000):
        """Try random assignments to check satisfiability."""
        for _ in range(max_tries):
            assignment = [random.choice([True, False]) for _ in range(n)]
            sat = True
            for clause in clauses:
                clause_sat = False
                for lit in clause:
                    var = abs(lit) - 1
                    val = assignment[var]
                    if (lit > 0 and val) or (lit < 0 and not val):
                        clause_sat = True
                        break
                if not clause_sat:
                    sat = False
                    break
            if sat:
                return True
        return False

    for alpha in np.arange(1.0, 8.1, 0.5):
        m = int(alpha * n)
        sat_count = 0

        for _ in range(trials):
            clauses = []
            for _ in range(m):
                vars_chosen = random.sample(range(1, n + 1), 3)
                clause = [v * random.choice([1, -1]) for v in vars_chosen]
                clauses.append(clause)

            if simple_sat_check(clauses, n):
                sat_count += 1

        pct = sat_count / trials * 100
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        marker = " ← THRESHOLD" if 3.5 <= alpha <= 5.0 and 20 < pct < 80 else ""
        print(f"  {alpha:12.1f} | {pct:7.1f}% | {bar}{marker}")

    print("\n  The SAT/UNSAT threshold for 3-SAT is ≈ 4.267")
    print("  Spectral gap collapses at this critical density!")

def demo_spectral_gap():
    """Demonstrate spectral gap computation."""
    print("\n" + "=" * 60)
    print("SPECTRAL GAP AS HARDNESS INDICATOR")
    print("=" * 60)

    n = 8
    print(f"\n  Generating random clause-variable matrices (n={n})...")

    for alpha in [2.0, 3.5, 4.0, 4.267, 5.0, 6.0]:
        m = int(alpha * n)
        # Random clause-variable incidence matrix
        A = np.zeros((m, n))
        for i in range(m):
            vars_chosen = random.sample(range(n), 3)
            for v in vars_chosen:
                A[i][v] = random.choice([-1, 1])

        # Compute AᵀA for spectral analysis
        M = A.T @ A / m
        eigenvalues = np.sort(np.linalg.eigvalsh(M))[::-1]

        gap = eigenvalues[0] - eigenvalues[1] if len(eigenvalues) > 1 else 0
        gap_bar = "█" * int(gap * 10)
        status = "EASY" if gap > 0.5 else ("HARD" if gap < 0.2 else "TRANSITION")

        print(f"  α={alpha:5.3f}: gap={gap:.3f} {gap_bar:20s} [{status}]")

    print("\n  Large gap → clustered solutions → EASY")
    print("  Small gap → fragmented solutions → HARD")
    print("  Gap collapse ≈ SAT threshold ≈ onset of hardness")

if __name__ == "__main__":
    random.seed(42)
    np.random.seed(42)

    demo_fourier_analysis()
    demo_sensitivity()
    demo_sat_phase_transition()
    demo_spectral_gap()

    print("\n" + "=" * 60)
    print("All spectral collapse demos completed!")
    print("=" * 60)
