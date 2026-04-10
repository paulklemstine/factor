#!/usr/bin/env python3
"""
Pythagorean Tree Factoring Demo
================================
Demonstrates the connection between Pythagorean triples and integer factoring
via the Berggren tree and Euler's method.

Key theorems (all machine-verified in Lean 4):
- Brahmagupta-Fibonacci: (a²+b²)(c²+d²) = (ac-bd)² + (ad+bc)²
- Euler's factoring: two sum-of-squares representations → nontrivial factor
- Berggren tree: generates all primitive Pythagorean triples from (3,4,5)
"""

import math
from collections import deque


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


# =============================================================================
# Berggren Tree
# =============================================================================

# The three Berggren matrices
A = [[1, -2, 2], [2, -1, 2], [2, -2, 3]]
B = [[1,  2, 2], [2,  1, 2], [2,  2, 3]]
C = [[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]]


def mat_vec(M, v):
    """Multiply 3x3 matrix by 3-vector."""
    return [sum(M[i][j] * v[j] for j in range(3)) for i in range(3)]


def generate_berggren_tree(max_hyp=100, max_triples=50):
    """Generate Pythagorean triples via BFS on the Berggren tree."""
    triples = []
    queue = deque([(3, 4, 5)])

    while queue and len(triples) < max_triples:
        a, b, c = queue.popleft()
        if c > max_hyp:
            continue
        triples.append((min(a, b), max(a, b), c))

        for M in [A, B, C]:
            new = mat_vec(M, [a, b, c])
            na, nb, nc = abs(new[0]), abs(new[1]), abs(new[2])
            if nc <= max_hyp:
                queue.append((na, nb, nc))

    return sorted(set(triples))


# =============================================================================
# Sum of Two Squares Representations
# =============================================================================

def sum_of_two_squares(n):
    """Find all representations n = a² + b² with 0 < a ≤ b."""
    reps = []
    a = 1
    while a * a <= n // 2:
        b_sq = n - a * a
        b = int(math.isqrt(b_sq))
        if b * b == b_sq and a <= b:
            reps.append((a, b))
        a += 1
    return reps


def euler_factor(n):
    """
    Euler's factoring method: if n = a² + b² = c² + d² in two different ways,
    then gcd(a²-c², n) gives a nontrivial factor.

    Formally: (a-c)(a+c) = (d-b)(d+b)  [verified in Lean 4]
    """
    reps = sum_of_two_squares(n)
    if len(reps) < 2:
        return None

    a, b = reps[0]
    c, d = reps[1]

    # From the identity: (a-c)(a+c) = (d-b)(d+b)
    g1 = gcd(abs(a - c) * (a + c), n)
    g2 = gcd(abs(a + c), n)
    g3 = gcd(abs(d - b) * (d + b), n)

    for g in [g1, g2, g3]:
        if 1 < g < n:
            return g

    # Try Brahmagupta-Fibonacci approach
    # n² = (ac+bd)² + (ad-bc)² = (ac-bd)² + (ad+bc)²
    p1 = abs(a*c + b*d)
    q1 = abs(a*d - b*c)
    g4 = gcd(p1, n)
    if 1 < g4 < n:
        return g4

    return None


# =============================================================================
# Brahmagupta-Fibonacci Identity Demo
# =============================================================================

def brahmagupta_fibonacci_demo():
    """Demonstrate: (a²+b²)(c²+d²) = (ac-bd)² + (ad+bc)²"""
    print("=" * 60)
    print("BRAHMAGUPTA-FIBONACCI IDENTITY")
    print("(a²+b²)(c²+d²) = (ac-bd)² + (ad+bc)²")
    print("=" * 60)
    print()

    examples = [(1, 2, 3, 4), (2, 3, 5, 7), (3, 4, 5, 12)]
    for a, b, c, d in examples:
        lhs = (a**2 + b**2) * (c**2 + d**2)
        rhs1 = (a*c - b*d)**2 + (a*d + b*c)**2
        rhs2 = (a*c + b*d)**2 + (a*d - b*c)**2
        print(f"  ({a}²+{b}²)({c}²+{d}²) = {lhs}")
        print(f"    = ({a}·{c}-{b}·{d})² + ({a}·{d}+{b}·{c})² = {a*c-b*d}² + {a*d+b*c}² = {rhs1}")
        print(f"    = ({a}·{c}+{b}·{d})² + ({a}·{d}-{b}·{c})² = {a*c+b*d}² + {a*d-b*c}² = {rhs2}")
        assert lhs == rhs1 == rhs2
        print(f"    ✓ Verified!")
        print()


def berggren_tree_demo():
    """Show the Berggren tree structure."""
    print("=" * 60)
    print("BERGGREN TREE OF PYTHAGOREAN TRIPLES")
    print("=" * 60)
    print()
    print("Root: (3, 4, 5)")
    print()
    print("Tree structure (first 3 levels):")
    print("  (3,4,5)")

    root = [3, 4, 5]
    children_names = ['A', 'B', 'C']
    matrices = [A, B, C]

    for i, M in enumerate(matrices):
        child = mat_vec(M, root)
        ca, cb, cc = abs(child[0]), abs(child[1]), abs(child[2])
        sa, sb = min(ca, cb), max(ca, cb)
        # Verify Pythagorean
        assert sa**2 + sb**2 == cc**2
        print(f"    ├── {children_names[i]}: ({sa},{sb},{cc})  [{sa}²+{sb}²={cc}²  ✓]")

        for j, M2 in enumerate(matrices):
            grandchild = mat_vec(M2, child)
            ga, gb, gc = abs(grandchild[0]), abs(grandchild[1]), abs(grandchild[2])
            ga, gb = min(ga, gb), max(ga, gb)
            assert ga**2 + gb**2 == gc**2
            connector = "└" if j == 2 else "├"
            print(f"    │   {connector}── {children_names[i]}{children_names[j]}: ({ga},{gb},{gc})")

    print()
    print(f"All primitive triples with hypotenuse ≤ 100:")
    triples = generate_berggren_tree(100, 100)
    for i, (a, b, c) in enumerate(triples):
        print(f"  {i+1:>3}. ({a:>3}, {b:>3}, {c:>3})  {a}²+{b}²={a**2+b**2}={c}²={c**2}")
    print(f"  Total: {len(triples)} primitive triples")
    print()


def euler_factoring_demo():
    """Demonstrate Euler's factoring via sum-of-squares representations."""
    print("=" * 60)
    print("EULER'S FACTORING VIA SUM-OF-SQUARES")
    print("=" * 60)
    print()
    print("If N = a²+b² = c²+d² (two ways), then")
    print("  (a-c)(a+c) = (d-b)(d+b) → nontrivial factor")
    print()

    # Find composites with multiple sum-of-squares representations
    successes = 0
    print(f"{'N':>8} {'representations':<30} {'factor':>8} {'check':>12}")
    print("-" * 65)

    for n in range(5, 1000):
        reps = sum_of_two_squares(n)
        if len(reps) >= 2:
            factor = euler_factor(n)
            if factor:
                rep_str = ", ".join(f"{a}²+{b}²" for a, b in reps[:3])
                other = n // factor
                print(f"{n:>8} {rep_str:<30} {factor:>8} {factor}×{other}={factor*other:>5}")
                successes += 1
                if successes >= 20:
                    break

    print()
    print(f"Euler's method successfully factored {successes} composites")
    print()


def lorentz_form_demo():
    """Demonstrate that Berggren matrices preserve Q(a,b,c) = a²+b²-c²."""
    print("=" * 60)
    print("LORENTZ FORM PRESERVATION")
    print("Q(a,b,c) = a² + b² - c²")
    print("=" * 60)
    print()

    def lorentz_form(v):
        return v[0]**2 + v[1]**2 - v[2]**2

    root = [3, 4, 5]
    Q_root = lorentz_form(root)
    print(f"Root: Q(3,4,5) = 9 + 16 - 25 = {Q_root}")
    print()

    for name, M in [('A', A), ('B', B), ('C', C)]:
        child = mat_vec(M, root)
        Q_child = lorentz_form(child)
        print(f"  {name}·(3,4,5) = ({child[0]},{child[1]},{child[2]})")
        print(f"    Q = {child[0]}² + {child[1]}² - {child[2]}² = {Q_child}  {'✓' if Q_child == Q_root else '✗'}")

    print()
    print("The Berggren matrices preserve Q = 0 (the light cone),")
    print("embedding Pythagorean triple navigation into Lorentz geometry.")
    print()


if __name__ == "__main__":
    brahmagupta_fibonacci_demo()
    berggren_tree_demo()
    euler_factoring_demo()
    lorentz_form_demo()
