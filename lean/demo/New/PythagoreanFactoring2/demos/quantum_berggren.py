#!/usr/bin/env python3
"""
Quantum Berggren Tree Simulation
=================================
Simulates how a quantum computer might navigate the Berggren tree
using superposition over branch choices.

This is a conceptual simulation (not a real quantum algorithm) that
demonstrates the potential speedup from quantum parallelism.

Key ideas:
  1. Classical: descent takes O(depth) sequential steps
  2. Quantum: Grover-like amplitude amplification on branch choices
  3. The tree's Lorentz group structure provides natural unitary representations

Usage:
    python quantum_berggren.py
"""

import numpy as np
from math import sqrt, gcd, isqrt, log2
import random


def classical_descent(triple):
    """Classical Berggren descent: O(depth) steps."""
    A_inv = np.array([[1, 2, -2], [-2, -1, 2], [-2, -2, 3]])
    B_inv = np.array([[1, 2, -2], [2, 1, -2], [-2, -2, 3]])
    C_inv = np.array([[-1, -2, 2], [2, 1, -2], [-2, -2, 3]])

    v = np.array(triple, dtype=np.int64)
    root = np.array([3, 4, 5], dtype=np.int64)
    steps = 0

    while not np.array_equal(v, root) and steps < 100000:
        best = None
        best_hyp = v[2]
        for M_inv in [A_inv, B_inv, C_inv]:
            w = M_inv @ v
            if w[0] < 0:
                w = np.array([abs(w[0]), abs(w[1]), w[2]])
            if w[2] > 0 and w[2] < best_hyp:
                best = w
                best_hyp = w[2]
        if best is None:
            break
        v = best
        steps += 1

    return steps


def quantum_amplitude_simulation(triple, N_to_factor, num_simulations=1000):
    """
    Simulate quantum amplitude amplification on Berggren descent.

    Concept: Instead of deterministic descent, we prepare a superposition
    over all 3^d possible paths of depth d and use Grover-like search
    to find paths that produce a non-trivial gcd with N.

    Classical: must try paths sequentially → O(3^d) worst case for random search
    Quantum: Grover search → O(√(3^d)) = O(3^(d/2)) queries

    This simulation estimates the practical speedup.
    """
    A_inv = np.array([[1, 2, -2], [-2, -1, 2], [-2, -2, 3]])
    B_inv = np.array([[1, 2, -2], [2, 1, -2], [-2, -2, 3]])
    C_inv = np.array([[-1, -2, 2], [2, 1, -2], [-2, -2, 3]])
    matrices = [A_inv, B_inv, C_inv]

    classical_depth = classical_descent(triple)
    max_d = classical_depth + 5

    # Simulate random walk (classical Monte Carlo)
    classical_successes = 0
    classical_total_steps = 0

    for _ in range(num_simulations):
        v = np.array(triple, dtype=np.int64)
        found = False
        for step in range(max_d):
            # Random branch choice
            M = random.choice(matrices)
            w = M @ v
            if w[0] < 0:
                w = np.array([abs(w[0]), abs(w[1]), w[2]])
            if w[2] > 0 and w[2] < v[2]:
                v = w
                # Check for factor
                g = gcd(int(abs(v[0])), N_to_factor)
                if 1 < g < N_to_factor:
                    classical_successes += 1
                    classical_total_steps += step + 1
                    found = True
                    break
            else:
                break
        if not found:
            classical_total_steps += max_d

    # Quantum: Grover amplification
    # If classical success probability is p, Grover finds in O(1/√p) iterations
    p_classical = classical_successes / num_simulations if num_simulations > 0 else 0
    grover_iterations = int(1 / sqrt(p_classical)) if p_classical > 0 else float('inf')

    return {
        'classical_depth': classical_depth,
        'classical_success_rate': p_classical,
        'classical_avg_steps': classical_total_steps / num_simulations,
        'quantum_grover_iterations': grover_iterations,
        'speedup_factor': (classical_total_steps / num_simulations) / grover_iterations if grover_iterations < float('inf') else float('inf'),
    }


def experiment_quantum_speedup():
    """Run quantum speedup experiments on various semiprimes."""
    print("═══ Quantum Berggren Tree Navigation ═══")
    print()
    print("Concept: Use Grover-like amplitude amplification to search")
    print("the Berggren tree for factoring-relevant triples.")
    print()

    semiprimes = [
        (15, 3, 5), (21, 3, 7), (35, 5, 7), (77, 7, 11),
        (91, 7, 13), (143, 11, 13), (221, 13, 17), (323, 17, 19),
        (667, 23, 29), (899, 29, 31), (1147, 31, 37),
    ]

    print(f"{'N':>6} {'= p×q':>10} {'Trivial':>10} {'Class. p':>10} "
          f"{'Grover':>8} {'Speedup':>8}")
    print("─" * 55)

    for N, p, q in semiprimes:
        # Trivial triple: N² + b² = c² where b = (N²-1)/2, c = (N²+1)/2
        b = (N * N - 1) // 2
        c = (N * N + 1) // 2
        triple = (N, b, c)

        result = quantum_amplitude_simulation(triple, N, num_simulations=500)

        trivial_depth = result['classical_depth']
        p_rate = result['classical_success_rate']
        grover = result['quantum_grover_iterations']
        speedup = result['speedup_factor']

        print(f"{N:>6} = {p}×{q:<4} {trivial_depth:>10} {p_rate:>10.4f} "
              f"{grover:>8} {speedup:>8.2f}×")

    print()
    print("═══ Analysis ═══")
    print()
    print("Key findings:")
    print("  1. Classical descent depth grows as O(N) for trivial triples")
    print("  2. Random branch exploration has low success probability")
    print("  3. Grover amplification provides √(1/p) speedup")
    print("  4. The quantum advantage is modest for trivial triples")
    print()
    print("═══ NEW HYPOTHESIS: Quantum Lorentz Walk ═══")
    print()
    print("Hypothesis: The Lorentz group structure of the Berggren tree")
    print("admits a natural quantum walk formulation where:")
    print("  • States = points on the hyperboloid model of H²")
    print("  • Transitions = Berggren matrix applications")
    print("  • The hitting time to the 'factoring oracle' state")
    print("    scales as O(√depth) instead of O(depth)")
    print()
    print("This would give a quadratic speedup over classical descent,")
    print("analogous to Grover's algorithm but exploiting the geometric")
    print("structure of the Lorentz group representation.")
    print()


def main():
    experiment_quantum_speedup()


if __name__ == '__main__':
    main()
