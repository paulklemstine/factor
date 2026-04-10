#!/usr/bin/env python3
"""
Berggren Tree Factoring Demo
============================
Explores the connection between Pythagorean triples and integer factoring.

Given an odd number n, we find Pythagorean triples (n, b, c) where n² + b² = c².
Each such triple corresponds to a factorization n² = (c-b)(c+b), where c-b and c+b
are a same-parity divisor pair. From these, we can extract factors of n.

Usage:
    python berggren_tree_factoring.py [number_to_factor]
"""

import math
import sys
from collections import defaultdict


def find_pythagorean_triples_with_leg(n: int, max_triples: int = 100) -> list:
    """Find Pythagorean triples (n, b, c) with n² + b² = c²."""
    triples = []
    n_sq = n * n
    # c - b = d, c + b = e, d*e = n², d < e, d ≡ e (mod 2)
    for d in range(1, int(math.isqrt(n_sq)) + 1):
        if n_sq % d != 0:
            continue
        e = n_sq // d
        if d >= e:
            continue
        if d % 2 != e % 2:
            continue
        b = (e - d) // 2
        c = (e + d) // 2
        if b > 0 and n * n + b * b == c * c:
            triples.append((n, b, c))
            if len(triples) >= max_triples:
                break
    return triples


def extract_factors(n: int, triples: list) -> set:
    """Extract non-trivial factors of n from Pythagorean triples."""
    factors = set()
    for (leg, b, c) in triples:
        d = c - b
        e = c + b
        # d * e = n²
        # gcd(n, d) and gcd(n, e) may give non-trivial factors
        g1 = math.gcd(n, d)
        g2 = math.gcd(n, e)
        for g in [g1, g2]:
            if 1 < g < n:
                factors.add(g)
                factors.add(n // g)
    return factors


def berggren_matrices():
    """The three Berggren matrices that generate primitive Pythagorean triples."""
    A = [[1, -2, 2], [2, -1, 2], [2, -2, 3]]
    B = [[1, 2, 2], [2, 1, 2], [2, 2, 3]]
    C = [[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]]
    return A, B, C


def mat_vec_mult(M, v):
    """Multiply a 3x3 matrix by a 3-vector."""
    return [sum(M[i][j] * v[j] for j in range(3)) for i in range(3)]


def generate_berggren_tree(max_hyp: int = 1000, max_depth: int = 20) -> list:
    """Generate primitive Pythagorean triples via the Berggren tree."""
    A, B, C = berggren_matrices()
    triples = []
    stack = [([3, 4, 5], 0)]

    while stack:
        triple, depth = stack.pop()
        a, b, c = triple
        if c > max_hyp or depth > max_depth:
            continue
        if a > 0 and b > 0:
            triples.append((min(a, b), max(a, b), c))
        for M in [A, B, C]:
            child = mat_vec_mult(M, triple)
            stack.append((child, depth + 1))

    return sorted(set(triples))


def demo_factoring():
    """Demonstrate Pythagorean triple factoring."""
    print("=" * 65)
    print("  BERGGREN TREE FACTORING DEMO")
    print("  Using Pythagorean triples to factor integers")
    print("=" * 65)

    # Example numbers to factor
    test_numbers = [15, 21, 35, 77, 91, 143, 221, 323, 437, 1001, 10403]

    if len(sys.argv) > 1:
        try:
            test_numbers = [int(sys.argv[1])]
        except ValueError:
            pass

    for n in test_numbers:
        if n % 2 == 0:
            print(f"\n  n = {n}: skipping (even number)")
            continue

        triples = find_pythagorean_triples_with_leg(n)
        factors = extract_factors(n, triples)

        print(f"\n  n = {n}")
        print(f"  Pythagorean triples with leg {n}: {len(triples)}")
        for t in triples[:5]:
            a, b, c = t
            d, e = c - b, c + b
            print(f"    ({a}, {b}, {c})  →  {a}² = {d} × {e}")
        if len(triples) > 5:
            print(f"    ... and {len(triples) - 5} more")

        if factors:
            print(f"  Factors found: {sorted(factors)}")
        elif n > 1:
            is_prime = all(n % i != 0 for i in range(2, int(math.isqrt(n)) + 1))
            if is_prime:
                print(f"  n = {n} is PRIME (exactly 1 triple, no non-trivial factors)")
            else:
                print(f"  No factors extracted (try more triples)")

    # Berggren tree statistics
    print("\n" + "=" * 65)
    print("  BERGGREN TREE STATISTICS")
    print("=" * 65)
    for max_hyp in [100, 500, 1000, 5000]:
        triples = generate_berggren_tree(max_hyp=max_hyp)
        print(f"  Primitive triples with hypotenuse ≤ {max_hyp:>5d}: {len(triples):>4d}")


def demo_primality_test():
    """A number n is prime iff it has exactly one Pythagorean triple with leg n."""
    print("\n" + "=" * 65)
    print("  PYTHAGOREAN PRIMALITY TEST")
    print("  An odd n > 1 is prime ⟺ exactly one triple with leg n")
    print("=" * 65)

    for n in range(3, 100, 2):
        triples = find_pythagorean_triples_with_leg(n)
        is_prime = all(n % i != 0 for i in range(2, int(math.isqrt(n)) + 1))
        triple_count = len(triples)
        predicted_prime = (triple_count == 1)

        if predicted_prime != is_prime:
            print(f"  MISMATCH at n={n}: {triple_count} triples, "
                  f"prime={is_prime}, predicted={predicted_prime}")
        elif n < 30 or is_prime:
            status = "PRIME" if is_prime else f"COMPOSITE ({triple_count} triples)"
            print(f"  n = {n:>3d}: {triple_count} triple(s) → {status}")


if __name__ == "__main__":
    demo_factoring()
    demo_primality_test()
