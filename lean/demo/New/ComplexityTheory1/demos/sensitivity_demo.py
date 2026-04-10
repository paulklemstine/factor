#!/usr/bin/env python3
"""
Boolean Function Sensitivity Demo

Interactive exploration of sensitivity, certificate complexity,
and influence for Boolean functions on small numbers of variables.

This demonstrates the concepts formalized in BooleanFunctions.lean.
"""

import itertools
from typing import Callable, List, Tuple, Set


def all_inputs(n: int) -> List[Tuple[bool, ...]]:
    """Generate all 2^n Boolean inputs of length n."""
    return list(itertools.product([False, True], repeat=n))


def flip_bit(x: Tuple[bool, ...], i: int) -> Tuple[bool, ...]:
    """Flip bit i of input x."""
    return tuple(not v if j == i else v for j, v in enumerate(x))


def hamming_weight(x: Tuple[bool, ...]) -> int:
    """Count the number of True bits."""
    return sum(1 for b in x if b)


def hamming_distance(x: Tuple[bool, ...], y: Tuple[bool, ...]) -> int:
    """Count the number of differing positions."""
    return sum(1 for a, b in zip(x, y) if a != b)


# ---- Boolean Function Examples ----

def parity(x: Tuple[bool, ...]) -> bool:
    """XOR of all bits: True if odd number of True bits."""
    return hamming_weight(x) % 2 == 1


def majority(x: Tuple[bool, ...]) -> bool:
    """True if more than half the bits are True."""
    return hamming_weight(x) > len(x) // 2


def and_fn(x: Tuple[bool, ...]) -> bool:
    """AND: True only if all bits are True."""
    return all(x)


def or_fn(x: Tuple[bool, ...]) -> bool:
    """OR: True if any bit is True."""
    return any(x)


def threshold_k(k: int):
    """Returns a threshold function: True if weight >= k."""
    def f(x: Tuple[bool, ...]) -> bool:
        return hamming_weight(x) >= k
    f.__name__ = f"threshold_{k}"
    return f


# ---- Complexity Measures ----

def sensitivity_at(f: Callable, x: Tuple[bool, ...]) -> int:
    """Sensitivity of f at input x: number of bits whose flip changes f(x)."""
    n = len(x)
    return sum(1 for i in range(n) if f(flip_bit(x, i)) != f(x))


def sensitivity(f: Callable, n: int) -> int:
    """Maximum sensitivity over all inputs."""
    return max(sensitivity_at(f, x) for x in all_inputs(n))


def block_sensitivity_at(f: Callable, x: Tuple[bool, ...]) -> int:
    """Block sensitivity at x: max number of disjoint sensitive blocks."""
    n = len(x)
    best = 0
    # Try all partitions into disjoint blocks (exponential, only for small n)
    for num_blocks in range(n, 0, -1):
        # Check if we can find num_blocks disjoint sensitive blocks
        found = _find_disjoint_blocks(f, x, n, num_blocks)
        if found:
            best = max(best, num_blocks)
            break
    return best


def _find_disjoint_blocks(f, x, n, target, used=None, count=0):
    """Recursively find disjoint sensitive blocks."""
    if used is None:
        used = set()
    if count == target:
        return True
    for size in range(1, n - len(used) + 1):
        available = [i for i in range(n) if i not in used]
        for block in itertools.combinations(available, size):
            # Flip the block
            y = list(x)
            for i in block:
                y[i] = not y[i]
            y = tuple(y)
            if f(y) != f(x):
                new_used = used | set(block)
                if _find_disjoint_blocks(f, x, n, target, new_used, count + 1):
                    return True
    return False


def block_sensitivity(f: Callable, n: int) -> int:
    """Maximum block sensitivity over all inputs."""
    return max(block_sensitivity_at(f, x) for x in all_inputs(n))


def certificate_complexity_at(f: Callable, x: Tuple[bool, ...]) -> int:
    """Minimum certificate size at x."""
    n = len(x)
    # Try all subsets from smallest to largest
    for size in range(n + 1):
        for cert in itertools.combinations(range(n), size):
            cert_set = set(cert)
            # Check if cert determines f(x)
            is_cert = True
            for y in all_inputs(n):
                if all(y[i] == x[i] for i in cert_set):
                    if f(y) != f(x):
                        is_cert = False
                        break
            if is_cert:
                return size
    return n


def certificate_complexity(f: Callable, n: int) -> int:
    """Maximum certificate complexity over all inputs."""
    return max(certificate_complexity_at(f, x) for x in all_inputs(n))


def influence_of(f: Callable, n: int, i: int) -> float:
    """Influence of coordinate i on function f."""
    inputs = all_inputs(n)
    count = sum(1 for x in inputs if f(flip_bit(x, i)) != f(x))
    return count / len(inputs)


def total_influence(f: Callable, n: int) -> float:
    """Total influence = sum of individual influences."""
    return sum(influence_of(f, n, i) for i in range(n))


# ---- Visualization ----

def print_truth_table(f: Callable, n: int, name: str = "f"):
    """Print the truth table of a Boolean function."""
    print(f"\nTruth table for {name} on {n} variables:")
    print("-" * (n + 10))
    header = " ".join(f"x{i}" for i in range(n)) + f"  {name}"
    print(header)
    print("-" * (n + 10))
    for x in all_inputs(n):
        bits = " ".join("1" if b else "0" for b in x)
        val = "1" if f(x) else "0"
        print(f" {bits}   {val}")


def analyze_function(f: Callable, n: int, name: str = "f"):
    """Comprehensive analysis of a Boolean function."""
    print(f"\n{'='*60}")
    print(f"Analysis of {name} on {n} variables")
    print(f"{'='*60}")

    if n <= 4:
        print_truth_table(f, n, name)

    s = sensitivity(f, n)
    print(f"\nSensitivity: s({name}) = {s}")

    # Show sensitivity at each input
    if n <= 4:
        print(f"\nSensitivity at each input:")
        for x in all_inputs(n):
            bits = "".join("1" if b else "0" for b in x)
            sa = sensitivity_at(f, x)
            sensitive_bits = [i for i in range(n) if f(flip_bit(x, i)) != f(x)]
            print(f"  s({bits}) = {sa}  sensitive bits: {sensitive_bits}")

    if n <= 5:
        bs = block_sensitivity(f, n)
        print(f"\nBlock sensitivity: bs({name}) = {bs}")

    if n <= 4:
        cc = certificate_complexity(f, n)
        print(f"Certificate complexity: C({name}) = {cc}")

    print(f"\nInfluence of each coordinate:")
    for i in range(n):
        inf = influence_of(f, n, i)
        print(f"  Inf_{i}({name}) = {inf:.4f}")

    ti = total_influence(f, n)
    print(f"\nTotal influence: I({name}) = {ti:.4f}")

    # Verify s ≤ C (our Theorem sensitivityAt_le_certificate)
    if n <= 4:
        print(f"\nVerification: s = {s} ≤ C = {cc}  ✓" if s <= cc else f"\n⚠ s > C!")

    print(f"\nKey bounds:")
    print(f"  s({name}) ≤ n = {n}: {s} ≤ {n}  ✓" if s <= n else f"  ⚠ s > n!")
    print(f"  I({name}) ≤ n = {n}: {ti:.4f} ≤ {n}  ✓" if ti <= n else f"  ⚠ I > n!")


# ---- VC Dimension Demo ----

def shatters(family: List[Set[int]], target: Set[int]) -> bool:
    """Check if a family of sets shatters the target set."""
    target_list = sorted(target)
    needed = set()
    for subset_bits in range(2 ** len(target_list)):
        subset = frozenset(target_list[j] for j in range(len(target_list))
                          if subset_bits & (1 << j))
        needed.add(subset)

    achieved = set()
    for S in family:
        intersection = frozenset(target & S)
        achieved.add(intersection)

    return needed <= achieved


def vc_dimension(family: List[Set[int]], universe_size: int) -> int:
    """Compute the VC dimension of a family of sets."""
    best = 0
    for size in range(universe_size + 1):
        found = False
        for target in itertools.combinations(range(universe_size), size):
            if shatters(family, set(target)):
                found = True
                best = size
                break
        if not found:
            break
    return best


def sauer_shelah_bound(n: int, d: int) -> int:
    """Compute the Sauer-Shelah bound: sum of C(n,i) for i = 0..d."""
    from math import comb
    return sum(comb(n, i) for i in range(d + 1))


def demo_vc_dimension():
    """Demonstrate VC dimension and Sauer-Shelah bound."""
    print(f"\n{'='*60}")
    print("VC Dimension and Sauer-Shelah Demo")
    print(f"{'='*60}")

    # Example: intervals on {0,1,...,7}
    n = 8
    intervals = []
    for a in range(n):
        for b in range(a, n):
            intervals.append(set(range(a, b + 1)))

    d = vc_dimension(intervals, n)
    bound = sauer_shelah_bound(n, d)

    print(f"\nFamily: all intervals on {{0,...,{n-1}}}")
    print(f"Number of sets: {len(intervals)}")
    print(f"VC dimension: {d}")
    print(f"Sauer-Shelah bound (d={d}): {bound}")
    print(f"|Family| ≤ bound: {len(intervals)} ≤ {bound}  ✓" if len(intervals) <= bound else "⚠")

    # Weak polynomial bound: (m+1)^d
    from math import comb
    for m in range(d, 15):
        ss = sum(comb(m, i) for i in range(d + 1))
        weak = (m + 1) ** d
        print(f"  m={m:2d}: Σ C(m,i) = {ss:6d},  (m+1)^d = {weak:6d},  ratio = {ss/weak:.4f}")


# ---- Sunflower Demo ----

def find_sunflower(family: List[Set[int]], p: int) -> Tuple[List[Set[int]], Set[int]]:
    """Find a sunflower of size p in the family (brute force)."""
    for combo in itertools.combinations(range(len(family)), p):
        sets = [family[i] for i in combo]
        # Check if they form a sunflower
        # Core = intersection of all sets
        core = sets[0].copy()
        for s in sets[1:]:
            core &= s
        # Petals must be pairwise disjoint
        petals = [s - core for s in sets]
        is_sunflower = True
        for i in range(len(petals)):
            for j in range(i + 1, len(petals)):
                if petals[i] & petals[j]:
                    is_sunflower = False
                    break
            if not is_sunflower:
                break
        if is_sunflower:
            return sets, core
    return [], set()


def demo_sunflower():
    """Demonstrate the sunflower structure."""
    print(f"\n{'='*60}")
    print("Sunflower Demo")
    print(f"{'='*60}")

    family = [
        {1, 2, 3},
        {1, 4, 5},
        {1, 6, 7},
        {2, 4, 6},
        {3, 5, 7}
    ]

    print(f"\nFamily of sets:")
    for i, s in enumerate(family):
        print(f"  S_{i} = {s}")

    flower, core = find_sunflower(family, 3)
    if flower:
        print(f"\nFound 3-sunflower with core {core}:")
        for s in flower:
            petal = s - core
            print(f"  {s}  (petal: {petal})")
    else:
        print("\nNo 3-sunflower found.")


# ---- Main ----

def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     Boolean Function Complexity Theory — Python Demo      ║")
    print("║                                                            ║")
    print("║  Demonstrating concepts from the Lean 4 formalization      ║")
    print("╚════════════════════════════════════════════════════════════╝")

    n = 4  # Small enough for exhaustive analysis

    # Analyze key Boolean functions
    analyze_function(parity, n, "PARITY")
    analyze_function(majority, n, "MAJORITY")
    analyze_function(and_fn, n, "AND")
    analyze_function(or_fn, n, "OR")
    analyze_function(threshold_k(2), n, "THRESHOLD_2")

    # Compare complexity measures
    print(f"\n{'='*60}")
    print("Comparison of Complexity Measures (n=4)")
    print(f"{'='*60}")
    print(f"{'Function':<15} {'s':>4} {'bs':>4} {'C':>4} {'I':>8}")
    print("-" * 40)

    functions = [
        (parity, "PARITY"),
        (majority, "MAJORITY"),
        (and_fn, "AND"),
        (or_fn, "OR"),
        (threshold_k(2), "THRESH_2"),
    ]

    for f, name in functions:
        s = sensitivity(f, n)
        bs = block_sensitivity(f, n)
        cc = certificate_complexity(f, n)
        ti = total_influence(f, n)
        print(f"{name:<15} {s:4d} {bs:4d} {cc:4d} {ti:8.4f}")

    print(f"\nKey relationships (verified in Lean 4):")
    print(f"  • s(f) ≤ n for all f          (sensitivityAt_le)")
    print(f"  • s(f) ≤ C(f)                 (sensitivityAt_le_certificate)")
    print(f"  • 0 ≤ Inf_i(f) ≤ 1            (influence_nonneg, influence_le_one)")
    print(f"  • s(PARITY) = n               (sensitivity_parity_allfalse)")

    # VC dimension demo
    demo_vc_dimension()

    # Sunflower demo
    demo_sunflower()


if __name__ == "__main__":
    main()
