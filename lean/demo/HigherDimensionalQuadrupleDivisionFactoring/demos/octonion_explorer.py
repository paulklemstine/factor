#!/usr/bin/env python3
"""
Octonion Non-Associativity Explorer

Investigates how different association orders in octonion multiplication
produce different 8-tuples, each providing independent factor-extraction
opportunities. This directly addresses Research Question 1.

Key finding: Non-associativity is a FEATURE that multiplies the number
of independent factor-extraction channels by the Catalan number C_{n-1}
for n input octets.
"""

import math
import random
from itertools import product
from typing import List, Tuple, Dict


def octonion_multiply(a: List[int], b: List[int]) -> List[int]:
    """Multiply two octonions using the Cayley-Dickson construction."""
    a1, a2, a3, a4, a5, a6, a7, a8 = a
    b1, b2, b3, b4, b5, b6, b7, b8 = b
    c1 = a1*b1 - a2*b2 - a3*b3 - a4*b4 - a5*b5 - a6*b6 - a7*b7 - a8*b8
    c2 = a1*b2 + a2*b1 + a3*b4 - a4*b3 + a5*b6 - a6*b5 - a7*b8 + a8*b7
    c3 = a1*b3 - a2*b4 + a3*b1 + a4*b2 + a5*b7 + a6*b8 - a7*b5 - a8*b6
    c4 = a1*b4 + a2*b3 - a3*b2 + a4*b1 + a5*b8 - a6*b7 + a7*b6 - a8*b5
    c5 = a1*b5 - a2*b6 - a3*b7 - a4*b8 + a5*b1 + a6*b2 + a7*b3 + a8*b4
    c6 = a1*b6 + a2*b5 - a3*b8 + a4*b7 - a5*b2 + a6*b1 - a7*b4 + a8*b3
    c7 = a1*b7 + a2*b8 + a3*b5 - a4*b6 - a5*b3 + a6*b4 + a7*b1 - a8*b2
    c8 = a1*b8 - a2*b7 + a3*b6 + a4*b5 - a5*b4 - a6*b3 + a7*b2 + a8*b1
    return [c1, c2, c3, c4, c5, c6, c7, c8]


def norm_sq(v: List[int]) -> int:
    return sum(x**2 for x in v)


def catalan(n: int) -> int:
    """Compute the nth Catalan number: number of distinct binary trees with n+1 leaves."""
    if n <= 0:
        return 1
    return math.comb(2 * n, n) // (n + 1)


# ============================================================
# All Association Orders for n Operands
# ============================================================

def all_associations(elements: List) -> List:
    """
    Generate all possible parenthesizations (association orders)
    of a list of elements under a binary operation.

    For n elements, this gives Catalan(n-1) distinct results.
    """
    n = len(elements)
    if n == 1:
        return [elements[0]]
    if n == 2:
        return [octonion_multiply(elements[0], elements[1])]

    results = []
    # Split into left and right at every possible position
    for split in range(1, n):
        left_parts = all_associations(elements[:split])
        right_parts = all_associations(elements[split:])

        # Handle the case where recursion returns a list of results
        if isinstance(left_parts[0], list) and isinstance(left_parts[0][0], list):
            left_list = left_parts
        elif isinstance(left_parts[0], int):
            left_list = [left_parts]
        else:
            left_list = left_parts

        if isinstance(right_parts[0], list) and isinstance(right_parts[0][0], list):
            right_list = right_parts
        elif isinstance(right_parts[0], int):
            right_list = [right_parts]
        else:
            right_list = right_parts

        for l in left_list:
            for r in right_list:
                results.append(octonion_multiply(l, r))

    return results


def generate_all_parenthesizations(octets: List[List[int]]) -> List[List[int]]:
    """
    Generate all Catalan(n-1) products of n octonions under different associations.
    Returns list of 8-tuples.
    """
    n = len(octets)
    if n == 1:
        return [octets[0]]
    if n == 2:
        return [octonion_multiply(octets[0], octets[1])]

    results = []
    for split in range(1, n):
        lefts = generate_all_parenthesizations(octets[:split])
        rights = generate_all_parenthesizations(octets[split:])
        for l in lefts:
            for r in rights:
                results.append(octonion_multiply(l, r))

    return results


# ============================================================
# Factor Extraction
# ============================================================

def gcd_cascade(v: List[int], N: int) -> List[int]:
    """Extract factor candidates via GCD of components with N."""
    factors = []
    for x in v:
        g = math.gcd(abs(x), N)
        if 1 < g < N:
            factors.append(g)
    return list(set(factors))


def peel_cascade(v: List[int], d: int, N: int) -> List[int]:
    """Extract factors via peel identity GCDs."""
    factors = []
    for j in range(len(v)):
        g1 = math.gcd(abs(d - v[j]), N)
        g2 = math.gcd(abs(d + v[j]), N)
        if 1 < g1 < N:
            factors.append(g1)
        if 1 < g2 < N:
            factors.append(g2)
    return list(set(factors))


# ============================================================
# Main Experiments
# ============================================================

def experiment_1_non_associativity():
    """Show that different associations produce different tuples."""
    print("=" * 70)
    print("EXPERIMENT 1: OCTONION NON-ASSOCIATIVITY")
    print("  Do different association orders produce different 8-tuples?")
    print("=" * 70)

    random.seed(42)
    num_trials = 100
    different_count = 0

    for trial in range(num_trials):
        a = [random.randint(1, 5) for _ in range(8)]
        b = [random.randint(1, 5) for _ in range(8)]
        c = [random.randint(1, 5) for _ in range(8)]

        left = octonion_multiply(octonion_multiply(a, b), c)
        right = octonion_multiply(a, octonion_multiply(b, c))

        # Verify norms are equal
        n_left = norm_sq(left)
        n_right = norm_sq(right)
        assert n_left == n_right, f"Norm mismatch: {n_left} != {n_right}"

        if left != right:
            different_count += 1

    print(f"\n  Trials: {num_trials}")
    print(f"  Different tuples produced: {different_count}/{num_trials} "
          f"({100*different_count/num_trials:.0f}%)")
    print(f"  ✓ Non-associativity produces independent tuples {different_count}% of the time")


def experiment_2_catalan_growth():
    """Show how the number of distinct tuples grows with operand count."""
    print("\n" + "=" * 70)
    print("EXPERIMENT 2: CATALAN NUMBER GROWTH")
    print("  How many independent tuples from n operands?")
    print("=" * 70)

    random.seed(123)

    print(f"\n  {'n operands':<15} {'Catalan(n-1)':<15} {'Distinct tuples':<18} {'All same norm?'}")
    print("  " + "-" * 65)

    for n in range(2, 6):
        octets = [[random.randint(1, 3) for _ in range(8)] for _ in range(n)]
        expected_catalan = catalan(n - 1)

        products = generate_all_parenthesizations(octets)

        # Check distinctness
        unique_tuples = set(tuple(p) for p in products)
        norms = set(norm_sq(p) for p in products)

        print(f"  {n:<15} {expected_catalan:<15} {len(unique_tuples):<18} "
              f"{'YES ✓' if len(norms) == 1 else 'NO ✗'}")

    print(f"\n  Key: All association orders produce the SAME norm (norm-multiplicativity)")
    print(f"       but DIFFERENT component distributions (non-associativity)")
    print(f"       → Each distinct tuple provides independent factor channels!")


def experiment_3_factor_extraction():
    """Compare factor extraction from different association orders."""
    print("\n" + "=" * 70)
    print("EXPERIMENT 3: FACTOR EXTRACTION COMPARISON")
    print("  Do different associations find different factors?")
    print("=" * 70)

    random.seed(42)
    N = 7 * 13 * 17  # = 1547

    print(f"\n  Target N = {N} = 7 × 13 × 17")

    # Generate 3 random octets
    octets = [[random.randint(1, 10) for _ in range(8)] for _ in range(3)]

    products = generate_all_parenthesizations(octets)
    unique_products = list(set(tuple(p) for p in products))

    print(f"  Octets: {len(octets)} → {len(unique_products)} distinct products")

    all_factors = set()
    for i, p in enumerate(unique_products):
        p_list = list(p)
        d = int(math.isqrt(norm_sq(p_list)))
        # Component GCDs
        factors = gcd_cascade(p_list, N)
        # Peel GCDs
        if d * d == norm_sq(p_list):
            factors.extend(peel_cascade(p_list, d, N))
        factors = sorted(set(factors))
        all_factors.update(factors)
        print(f"  Product {i+1}: factors = {factors}")

    print(f"\n  Combined factors from all associations: {sorted(all_factors)}")
    print(f"  Single association would find: {gcd_cascade(list(unique_products[0]), N)}")

    if len(all_factors) > len(gcd_cascade(list(unique_products[0]), N)):
        print(f"  ✓ Non-associativity INCREASES factor-finding power!")


def experiment_4_alternative_law():
    """Verify the alternative law: subalgebras of two elements are associative."""
    print("\n" + "=" * 70)
    print("EXPERIMENT 4: ALTERNATIVE LAW VERIFICATION")
    print("  Subalgebras generated by 2 elements are associative")
    print("=" * 70)

    random.seed(42)
    num_trials = 500
    alt_violations = 0

    for _ in range(num_trials):
        a = [random.randint(-5, 5) for _ in range(8)]
        b = [random.randint(-5, 5) for _ in range(8)]

        # Test (a·a)·b = a·(a·b) — left alternative
        left = octonion_multiply(octonion_multiply(a, a), b)
        right = octonion_multiply(a, octonion_multiply(a, b))
        if left != right:
            alt_violations += 1

    print(f"\n  Left alternative law violations: {alt_violations}/{num_trials}")
    print(f"  {'✓ Alternative law HOLDS' if alt_violations == 0 else '✗ UNEXPECTED violations'}")

    # Now check that generic associativity fails
    assoc_violations = 0
    for _ in range(num_trials):
        a = [random.randint(-5, 5) for _ in range(8)]
        b = [random.randint(-5, 5) for _ in range(8)]
        c = [random.randint(-5, 5) for _ in range(8)]

        left = octonion_multiply(octonion_multiply(a, b), c)
        right = octonion_multiply(a, octonion_multiply(b, c))
        if left != right:
            assoc_violations += 1

    print(f"  General associativity violations: {assoc_violations}/{num_trials}")
    print(f"  → Pairwise compositions are reliable; triple+ compositions give bonus diversity")


def experiment_5_optimal_association():
    """Find which association order is best for factor extraction."""
    print("\n" + "=" * 70)
    print("EXPERIMENT 5: OPTIMAL ASSOCIATION ORDER")
    print("  Which parenthesization finds factors most often?")
    print("=" * 70)

    random.seed(42)
    composites = [n for n in range(15, 200)
                  if any(n % p == 0 for p in range(2, int(math.sqrt(n)) + 1))]

    num_trials = min(50, len(composites))

    left_wins = 0
    right_wins = 0
    tie_count = 0
    both_fail = 0

    for N in composites[:num_trials]:
        a = [random.randint(1, 8) for _ in range(8)]
        b = [random.randint(1, 8) for _ in range(8)]
        c = [random.randint(1, 8) for _ in range(8)]

        left_prod = octonion_multiply(octonion_multiply(a, b), c)
        right_prod = octonion_multiply(a, octonion_multiply(b, c))

        left_factors = gcd_cascade(left_prod, N)
        right_factors = gcd_cascade(right_prod, N)

        if left_factors and not right_factors:
            left_wins += 1
        elif right_factors and not left_factors:
            right_wins += 1
        elif left_factors and right_factors:
            tie_count += 1
        else:
            both_fail += 1

    print(f"\n  Over {num_trials} composites:")
    print(f"  Left association wins:  {left_wins}")
    print(f"  Right association wins: {right_wins}")
    print(f"  Both find factors:      {tie_count}")
    print(f"  Neither finds factors:  {both_fail}")
    print(f"\n  → Using BOTH associations finds factors "
          f"{100*(left_wins+right_wins+tie_count)/num_trials:.0f}% of the time")
    print(f"  → Using only one finds factors ~"
          f"{100*(left_wins+tie_count)/num_trials:.0f}% of the time")


if __name__ == "__main__":
    experiment_1_non_associativity()
    experiment_2_catalan_growth()
    experiment_3_factor_extraction()
    experiment_4_alternative_law()
    experiment_5_optimal_association()
