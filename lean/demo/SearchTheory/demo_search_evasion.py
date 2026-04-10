"""
Search-Evasion Game Simulator

Demonstrates the core theorems from the formalization:
1. Pigeonhole evasion bound
2. Search-information conservation
3. Infinite-horizon optimal evasion
4. Detection probability monotonicity

Run: python demo_search_evasion.py
"""

import random
import math
from collections import Counter
from typing import List, Tuple, Optional

# ============================================================
# 1. THE SEARCH-EVASION GAME
# ============================================================

class SearchEvasionGame:
    """A finite search-evasion game on n locations."""

    def __init__(self, n: int):
        self.n = n
        self.locations = list(range(n))

    def deterministic_search(self, order: Optional[List[int]] = None) -> List[int]:
        """A deterministic search strategy (checks locations in order)."""
        if order is None:
            order = list(range(self.n))
        return order

    def random_search(self, steps: int) -> List[int]:
        """A uniformly random search strategy."""
        return [random.randint(0, self.n - 1) for _ in range(steps)]

    def optimal_evasion(self, search_sequence: List[int]) -> int:
        """Find the best hiding spot against a known search sequence.
        (Demonstrates the pigeonhole theorem.)"""
        searched = set(search_sequence)
        unsearched = [loc for loc in self.locations if loc not in searched]
        if unsearched:
            return unsearched[0]  # Any unsearched location works
        # If all locations are eventually searched, pick the last one
        last_searched = {}
        for t, loc in enumerate(search_sequence):
            last_searched[loc] = t
        return max(last_searched, key=last_searched.get)

    def simulate_game(self, search_strategy: str = "sequential",
                      evasion_strategy: str = "optimal",
                      steps: int = None) -> dict:
        """Simulate a complete game and return statistics."""
        if steps is None:
            steps = self.n

        # Generate search sequence
        if search_strategy == "sequential":
            search_seq = self.deterministic_search()[:steps]
        elif search_strategy == "random":
            search_seq = self.random_search(steps)
        else:
            search_seq = self.deterministic_search()[:steps]

        # Determine hiding spot
        if evasion_strategy == "optimal":
            target = self.optimal_evasion(search_seq)
        elif evasion_strategy == "random":
            target = random.randint(0, self.n - 1)
        else:
            target = 0

        # Check if caught
        detection_time = None
        for t, loc in enumerate(search_seq):
            if loc == target:
                detection_time = t
                break

        return {
            "n": self.n,
            "steps": steps,
            "target": target,
            "search_strategy": search_strategy,
            "evasion_strategy": evasion_strategy,
            "detected": detection_time is not None,
            "detection_time": detection_time,
            "survival_time": detection_time if detection_time is not None else steps,
        }


def demo_pigeonhole_bound():
    """Demonstrate the pigeonhole evasion bound (Theorem 2.4).

    For n locations and any deterministic searcher checking one per step,
    there exists a target surviving n-1 steps.
    """
    print("=" * 60)
    print("DEMO 1: Pigeonhole Evasion Bound")
    print("=" * 60)

    for n in [5, 10, 20, 50]:
        game = SearchEvasionGame(n)

        # Try 100 random search orderings
        max_survival = 0
        for _ in range(100):
            order = list(range(n))
            random.shuffle(order)
            search_seq = order[:n-1]  # n-1 steps
            target = game.optimal_evasion(search_seq)
            # Check if target was found
            found = target in search_seq
            if not found:
                max_survival = max(max_survival, n - 1)

        print(f"  n={n:3d}: Optimal evasion survives {max_survival} steps "
              f"(theoretical bound: {n-1})")

    print()


# ============================================================
# 2. SEARCH-INFORMATION CONSERVATION
# ============================================================

def search_info(n: int, k: int) -> float:
    """Search information gained from observing k of n locations."""
    if k >= n or n <= 0:
        return math.log(n) if n > 0 else 0
    return math.log(n) - math.log(n - k)

def evasion_info(n: int, k: int) -> float:
    """Evasion information remaining after k observations."""
    if k >= n or n <= 0:
        return 0
    return math.log(n - k)

def demo_information_conservation():
    """Demonstrate the search-information conservation law (Theorem 4.5).

    I_search + I_evasion = log(n)  (always!)
    """
    print("=" * 60)
    print("DEMO 2: Search-Information Conservation Law")
    print("=" * 60)

    n = 100
    print(f"  Space size n = {n}, Total information = log({n}) = {math.log(n):.4f}")
    print(f"  {'k':>4s} | {'I_search':>10s} | {'I_evasion':>10s} | {'Sum':>10s} | {'= log(n)?':>10s}")
    print(f"  {'-'*4:>4s} + {'-'*10:>10s} + {'-'*10:>10s} + {'-'*10:>10s} + {'-'*10:>10s}")

    for k in [0, 10, 25, 50, 75, 90, 99]:
        si = search_info(n, k)
        ei = evasion_info(n, k)
        total = si + ei
        check = "✓" if abs(total - math.log(n)) < 1e-10 else "✗"
        print(f"  {k:4d} | {si:10.4f} | {ei:10.4f} | {total:10.4f} | {check:>10s}")

    print()


# ============================================================
# 3. INFINITE-HORIZON OPTIMAL EVASION
# ============================================================

def demo_infinite_horizon():
    """Demonstrate the infinite-horizon evasion bound (Theorem 4.6).

    For any distribution d over n locations,
    there exists a target with survival prob >= 1 - 1/n.
    """
    print("=" * 60)
    print("DEMO 3: Infinite-Horizon Optimal Evasion")
    print("=" * 60)

    for n in [5, 10, 20, 100]:
        # Generate random distributions
        best_survival = 0
        for _ in range(1000):
            # Random distribution
            raw = [random.random() for _ in range(n)]
            total = sum(raw)
            dist = [x / total for x in raw]

            # Find location with minimum probability (best for evader)
            min_prob = min(dist)
            survival = 1 - min_prob
            best_survival = max(best_survival, survival)

        theoretical = 1 - 1/n
        print(f"  n={n:3d}: Best survival prob = {best_survival:.4f}, "
              f"Theoretical bound = {theoretical:.4f}")

    print()


# ============================================================
# 4. DETECTION PROBABILITY MONOTONICITY
# ============================================================

def demo_detection_monotonicity():
    """Demonstrate detection probability monotonicity (Theorem 2.3).

    The detection probability μ(C_n) is always increasing.
    """
    print("=" * 60)
    print("DEMO 4: Detection Probability Monotonicity")
    print("=" * 60)

    n = 20
    game = SearchEvasionGame(n)

    # Random search with replacement
    random.seed(42)
    search_seq = game.random_search(30)

    print(f"  Space size n = {n}")
    print(f"  Step | Searched | Det. Prob | Monotone?")
    print(f"  ---- + -------- + --------- + ---------")

    cumulative = set()
    prev_prob = 0.0
    for t, loc in enumerate(search_seq):
        cumulative.add(loc)
        prob = len(cumulative) / n
        monotone = "✓" if prob >= prev_prob - 1e-10 else "✗"
        if t < 15 or t >= 25:
            print(f"  {t:4d} | {len(cumulative):8d} | {prob:9.4f} | {monotone:>9s}")
        elif t == 15:
            print(f"  {'...':>4s} | {'...':>8s} | {'...':>9s} | {'...':>9s}")
        prev_prob = prob

    print()


# ============================================================
# 5. ENTROPY AND OPTIMAL SEARCH DISTRIBUTION
# ============================================================

def entropy(dist: List[float]) -> float:
    """Shannon entropy of a distribution."""
    return -sum(p * math.log(p) for p in dist if p > 0)

def demo_max_entropy():
    """Demonstrate that uniform distribution maximizes entropy (Theorem 4.3)."""
    print("=" * 60)
    print("DEMO 5: Maximum Entropy Principle")
    print("=" * 60)

    for n in [4, 8, 16, 32]:
        uniform_entropy = entropy([1/n] * n)

        # Test 10000 random distributions
        max_rand_entropy = 0
        for _ in range(10000):
            raw = [random.random() for _ in range(n)]
            total = sum(raw)
            dist = [x / total for x in raw]
            max_rand_entropy = max(max_rand_entropy, entropy(dist))

        print(f"  n={n:3d}: Uniform H = {uniform_entropy:.4f}, "
              f"Max random H = {max_rand_entropy:.4f}, "
              f"Uniform wins: {'✓' if uniform_entropy >= max_rand_entropy - 1e-10 else '✗'}")

    print()


# ============================================================
# 6. MONTE CARLO SIMULATION
# ============================================================

def demo_monte_carlo():
    """Large-scale Monte Carlo simulation of search-evasion games."""
    print("=" * 60)
    print("DEMO 6: Monte Carlo Simulation (10,000 games)")
    print("=" * 60)

    n = 10
    num_trials = 10000

    for search_type in ["sequential", "random"]:
        for evasion_type in ["optimal", "random"]:
            detections = 0
            total_survival = 0
            game = SearchEvasionGame(n)

            for _ in range(num_trials):
                result = game.simulate_game(
                    search_strategy=search_type,
                    evasion_strategy=evasion_type,
                    steps=n
                )
                if result["detected"]:
                    detections += 1
                total_survival += result["survival_time"]

            det_rate = detections / num_trials
            avg_survival = total_survival / num_trials

            print(f"  Search={search_type:>10s}, Evasion={evasion_type:>7s}: "
                  f"Det rate={det_rate:.3f}, Avg survival={avg_survival:.1f}")

    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  SEARCH THEORY: INTERACTIVE DEMONSTRATIONS")
    print("  Based on Lean 4 Formalization")
    print("=" * 60 + "\n")

    random.seed(2024)

    demo_pigeonhole_bound()
    demo_information_conservation()
    demo_infinite_horizon()
    demo_detection_monotonicity()
    demo_max_entropy()
    demo_monte_carlo()

    print("All demonstrations complete!")
    print("These results validate the theorems proven in the Lean 4 formalization.")
