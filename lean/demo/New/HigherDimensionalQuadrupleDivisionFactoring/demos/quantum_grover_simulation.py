#!/usr/bin/env python3
"""
Quantum k-Tuple Search Simulation

Simulates the Grover speedup for searching over k-dimensional
navigation space in the context of Quadruple Division Factoring.

Key question: Does Grover search over k-dimensional navigation
space provide a k-dependent speedup?

Answer: Grover provides O(√M) speedup where M is the search space size.
For k-tuples with components in [0, B], M = B^(k-1). So the quantum
speedup is O(B^{(k-1)/2}) queries vs O(B^{k-1}) classical, giving
a quadratic speedup INDEPENDENT of k. The k-dependence enters only
through the classical baseline, not through additional quantum advantage.
"""

import math
import random
from typing import List, Tuple, Optional

def classical_search_cost(B: int, k: int) -> int:
    """Classical brute-force search over k-tuples with components in [0,B]."""
    return B ** (k - 1)

def grover_search_cost(B: int, k: int) -> float:
    """Grover search cost: O(√M) where M = B^(k-1)."""
    return math.sqrt(B ** (k - 1))

def success_probability_per_query(B: int, k: int, num_solutions: int) -> float:
    """Probability that a random k-tuple reveals a factor."""
    M = B ** (k - 1)
    return num_solutions / M if M > 0 else 0

def grover_iterations_needed(M: int, num_solutions: int) -> int:
    """Number of Grover iterations for optimal success probability."""
    if num_solutions <= 0 or M <= 0:
        return 0
    return max(1, int(math.pi / 4 * math.sqrt(M / num_solutions)))

def simulate_classical_search(N: int, B: int, k: int) -> Tuple[bool, int]:
    """Simulate classical random search for factor-revealing k-tuple."""
    queries = 0
    max_queries = min(B ** (k-1), 100000)

    for _ in range(max_queries):
        queries += 1
        # Random k-tuple
        components = [random.randint(0, B) for _ in range(k-1)]
        sq_sum = sum(c**2 for c in components)
        d = int(math.isqrt(sq_sum))
        if d * d != sq_sum or d == 0:
            continue

        # Check GCD channels
        for c in components:
            for sign in [-1, 1]:
                g = math.gcd(d + sign * c, N)
                if 1 < g < N:
                    return True, queries

    return False, queries

def run_quantum_analysis():
    """Analyze quantum speedup across dimensions."""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  Quantum k-Tuple Search: Grover Speedup Analysis           ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    B = 100  # component bound
    print(f"\nComponent bound B = {B}")
    print(f"\n{'k':>3} | {'Classical M':>12} | {'Grover √M':>12} | {'Speedup':>10} | {'log₂ speedup':>12}")
    print("-" * 60)

    for k in range(3, 12):
        M = classical_search_cost(B, k)
        G = grover_search_cost(B, k)
        speedup = M / G if G > 0 else float('inf')
        log_speedup = math.log2(speedup) if speedup > 0 else 0
        print(f"{k:>3} | {M:>12.2e} | {G:>12.2e} | {speedup:>10.2e} | {log_speedup:>11.1f}")

    print("\n--- Key Insight ---")
    print("The Grover speedup is always exactly √M regardless of k.")
    print("In log scale: log₂(speedup) = (k-1)/2 · log₂(B)")
    print(f"For B={B}: log₂(speedup) = (k-1)/2 · {math.log2(B):.1f} = {math.log2(B)/2:.1f}·(k-1)")
    print("\nConclusion: Grover provides a QUADRATIC speedup at every dimension.")
    print("The k-dependence enters through the size of the search space,")
    print("not through additional quantum parallelism.")

    print("\n\n--- Monte Carlo Validation ---")
    print("Simulating classical search for small composites...")

    test_cases = [
        (15, 3), (15, 4), (15, 5),
        (21, 3), (21, 4), (21, 5),
        (35, 3), (35, 4), (35, 5),
    ]

    print(f"\n{'N':>4} | {'k':>3} | {'Found':>5} | {'Avg Queries':>11} | {'Est. Grover':>11}")
    print("-" * 50)

    for N, k in test_cases:
        trials = 50
        total_queries = 0
        successes = 0
        for _ in range(trials):
            found, q = simulate_classical_search(N, 20, k)
            total_queries += q
            if found:
                successes += 1

        avg_q = total_queries / trials
        est_grover = math.sqrt(avg_q) if avg_q > 0 else 0
        print(f"{N:>4} | {k:>3} | {successes:>4}{'✓' if successes > 0 else '✗'} | {avg_q:>10.1f} | {est_grover:>10.1f}")

if __name__ == "__main__":
    random.seed(42)
    run_quantum_analysis()
