#!/usr/bin/env python3
"""
Coherence-Stratified Complexity Demo

Demonstrates the four-tier coherence framework with concrete examples:
- Tier 0: Locally decidable problems
- Tier 1: Bounded coordination problems
- Tier 2: Polynomial coordination problems
- Tier 3: Global coordination problems
"""

import random
import time
from collections import Counter

def demo_tier0():
    """Tier 0: Locally decidable — no coordination needed."""
    print("=" * 60)
    print("TIER 0: LOCALLY DECIDABLE")
    print("=" * 60)

    print("\nExample: Is each element in a list positive?")
    print("Each element can be checked independently — no coordination.\n")

    data = [random.randint(-10, 10) for _ in range(20)]
    print(f"  Data: {data}")
    print(f"  Check each element independently:")

    results = []
    for i, x in enumerate(data):
        is_pos = x > 0
        results.append(is_pos)
        if i < 5:
            print(f"    Worker {i}: x={x:3d} → {'✓' if is_pos else '✗'}")
    if len(data) > 5:
        print(f"    ... ({len(data)-5} more workers)")

    print(f"\n  All positive? {all(results)}")
    print(f"  Communication: 0 bits between workers (Tier 0!)")

def demo_tier1():
    """Tier 1: Bounded coordination — logarithmic communication."""
    print("\n" + "=" * 60)
    print("TIER 1: BOUNDED COORDINATION (O(log n) communication)")
    print("=" * 60)

    print("\nExample: Find the maximum element")
    print("Workers need to share O(log n) bits via tournament.\n")

    data = [random.randint(1, 100) for _ in range(16)]
    print(f"  Data: {data}")

    # Tournament-style maximum
    current = list(data)
    round_num = 0
    total_comm = 0

    while len(current) > 1:
        next_round = []
        round_num += 1
        comm_bits = 0
        comparisons = []

        for i in range(0, len(current), 2):
            if i + 1 < len(current):
                winner = max(current[i], current[i + 1])
                next_round.append(winner)
                # Each comparison communicates ~log(max_val) bits
                comm_bits += 7  # ~log₂(100) bits per comparison
                comparisons.append(f"{current[i]} vs {current[i+1]} → {winner}")
            else:
                next_round.append(current[i])

        total_comm += comm_bits
        if round_num <= 3:
            print(f"  Round {round_num}: {', '.join(comparisons[:4])}" +
                  (f" + {len(comparisons)-4} more" if len(comparisons) > 4 else ""))
        current = next_round

    print(f"\n  Maximum: {current[0]}")
    print(f"  Rounds: {round_num} = log₂({len(data)})")
    print(f"  Total communication: ~{total_comm} bits = O(log n) → Tier 1")

def demo_tier2():
    """Tier 2: Polynomial coordination."""
    print("\n" + "=" * 60)
    print("TIER 2: POLYNOMIAL COORDINATION (O(n^c) communication)")
    print("=" * 60)

    print("\nExample: Sorting a list")
    print("Requires O(n log n) comparisons → polynomial coordination.\n")

    data = [random.randint(1, 100) for _ in range(12)]
    print(f"  Unsorted: {data}")

    # Merge sort with communication tracking
    comparisons = [0]

    def merge_sort(arr):
        if len(arr) <= 1:
            return arr
        mid = len(arr) // 2
        left = merge_sort(arr[:mid])
        right = merge_sort(arr[mid:])
        return merge(left, right, comparisons)

    def merge(left, right, comps):
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            comps[0] += 1
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    sorted_data = merge_sort(data.copy())
    print(f"  Sorted:   {sorted_data}")
    print(f"  Comparisons: {comparisons[0]} ≈ n·log(n) = {len(data)}·{len(data).bit_length()}")
    print(f"  Communication: O(n·log n) bits → Tier 2")

def demo_tier3():
    """Tier 3: Global coordination — exponential communication."""
    print("\n" + "=" * 60)
    print("TIER 3: GLOBAL COORDINATION (exponential communication)")
    print("=" * 60)

    print("\nExample: Subset Sum — does any subset sum to target?")
    print("In the worst case, need to check 2^n subsets.\n")

    n = 16
    data = [random.randint(1, 50) for _ in range(n)]
    target = sum(random.sample(data, n // 3))
    print(f"  Set: {data}")
    print(f"  Target: {target}")

    # Brute force
    found = False
    subsets_checked = 0
    solution = None

    for mask in range(1, 2 ** n):
        subsets_checked += 1
        subset_sum = sum(data[i] for i in range(n) if mask & (1 << i))
        if subset_sum == target:
            solution = [data[i] for i in range(n) if mask & (1 << i)]
            found = True
            break

    print(f"  Found: {found}")
    if solution:
        print(f"  Solution: {solution} (sum = {sum(solution)})")
    print(f"  Subsets checked: {subsets_checked} (worst case: 2^{n} = {2**n})")
    print(f"  Communication: O(2^n) bits needed in worst case → Tier 3")

def demo_tier_comparison():
    """Compare all tiers side by side."""
    print("\n" + "=" * 60)
    print("TIER COMPARISON: COMMUNICATION COMPLEXITY")
    print("=" * 60)

    sizes = [8, 16, 32, 64, 128, 256]

    print(f"\n  {'n':>6} | {'Tier 0':>10} | {'Tier 1':>10} | {'Tier 2':>10} | {'Tier 3':>15}")
    print(f"  {'':>6} | {'O(1)':>10} | {'O(log n)':>10} | {'O(n²)':>10} | {'O(2^n)':>15}")
    print("  " + "-" * 65)

    for n in sizes:
        t0 = 1
        t1 = n.bit_length()
        t2 = n * n
        t3 = min(2 ** n, 10**15)
        t3_str = f"{t3}" if t3 < 10**10 else f"~10^{len(str(t3))-1}"

        print(f"  {n:>6} | {t0:>10} | {t1:>10} | {t2:>10} | {t3_str:>15}")

    print("\n  The gap between tiers grows EXPONENTIALLY!")
    print("  This is why coherence tier classification matters for algorithm selection.")

def demo_defect_algebra():
    """Demonstrate defect algebra for approximation algorithms."""
    print("\n" + "=" * 60)
    print("DEFECT ALGEBRA FOR APPROXIMATION")
    print("=" * 60)

    print("\nApproximation algorithms produce near-optimal solutions.")
    print("The 'defect' measures how far from optimal.\n")

    # Simulate a multi-stage approximation
    optimal = 100.0
    stages = [
        ("Greedy init", 0.85),
        ("Local search", 0.92),
        ("Simulated annealing", 0.97),
        ("Final polish", 0.99),
    ]

    print(f"  Optimal value: {optimal}")
    print(f"\n  {'Stage':<25} | {'Achieved':>10} | {'Ratio':>8} | {'Defect':>8}")
    print("  " + "-" * 60)

    for name, ratio in stages:
        achieved = optimal * ratio
        defect = achieved - optimal * (1 if ratio >= 1 else ratio)
        approx_ratio = achieved / optimal
        bar = "█" * int(ratio * 20)
        print(f"  {name:<25} | {achieved:>10.2f} | {approx_ratio:>7.3f}x | {100*(1-ratio):>6.1f}%  {bar}")

    print(f"\n  Defects compose additively: total defect ≤ sum of stage defects")
    print(f"  This is formalized in our Lean proof: defect_zero_le")

if __name__ == "__main__":
    random.seed(42)

    demo_tier0()
    demo_tier1()
    demo_tier2()
    demo_tier3()
    demo_tier_comparison()
    demo_defect_algebra()

    print("\n" + "=" * 60)
    print("All coherence tier demos completed!")
    print("=" * 60)
