#!/usr/bin/env python3
"""
Stern-Brocot Tree Demo

Demonstrates the properties formalized in New/New__SternBrocot.lean:
1. The mediant adjacency invariant (bc - ad = 1)
2. Every positive rational appears exactly once
3. Finding a rational in the tree (connection to continued fractions)
"""

from fractions import Fraction
from math import gcd


def mediant(left, right):
    """Compute the mediant of two fractions a/b and c/d as (a+c, b+d)."""
    return (left[0] + right[0], left[1] + right[1])


def stern_brocot_path(p, q, max_depth=100):
    """
    Find the path to p/q in the Stern-Brocot tree.
    Returns a string of 'L' and 'R' directions.
    
    This corresponds to the `navigate` function in the Lean formalization.
    """
    assert p > 0 and q > 0 and gcd(p, q) == 1, "Need positive coprime integers"
    
    left = (0, 1)   # 0/1
    right = (1, 0)  # 1/0
    path = []
    
    for _ in range(max_depth):
        med = mediant(left, right)
        if med == (p, q):
            return ''.join(path), med
        elif p * med[1] < q * med[0]:  # p/q < med
            path.append('L')
            right = med
        else:  # p/q > med
            path.append('R')
            left = med
    
    return ''.join(path), mediant(left, right)


def verify_adjacency(left, right):
    """
    Verify the adjacency invariant: b*c - a*d = 1.
    This is the key property proved in `adjacency_invariant` in Lean.
    """
    a, b = left
    c, d = right
    return b * c - a * d == 1


def generate_tree(depth=4):
    """Generate the Stern-Brocot tree to a given depth."""
    if depth == 0:
        return None
    
    def build(left, right, d):
        if d == 0:
            return None
        med = mediant(left, right)
        # Verify the adjacency invariant at every node
        adj_left = verify_adjacency(left, med)
        adj_right = verify_adjacency(med, right)
        return {
            'value': med,
            'fraction': f"{med[0]}/{med[1]}",
            'adjacency_left': adj_left,
            'adjacency_right': adj_right,
            'left': build(left, med, d - 1),
            'right': build(med, right, d - 1),
        }
    
    return build((0, 1), (1, 0), depth)


def print_tree(node, prefix="", is_left=True, is_root=True):
    """Pretty-print the Stern-Brocot tree."""
    if node is None:
        return
    
    connector = "" if is_root else ("├── " if is_left else "└── ")
    adj_status = "✓" if (node['adjacency_left'] and node['adjacency_right']) else "✗"
    print(f"{prefix}{connector}{node['fraction']} [adj: {adj_status}]")
    
    new_prefix = prefix + ("" if is_root else ("│   " if is_left else "    "))
    if node['left'] or node['right']:
        if node['left']:
            print_tree(node['left'], new_prefix, True, False)
        if node['right']:
            print_tree(node['right'], new_prefix, False, False)


def stern_sequence(n):
    """
    Compute the Stern diatomic sequence s(n).
    s(0) = 0, s(1) = 1
    s(2n) = s(n), s(2n+1) = s(n) + s(n+1)
    
    Consecutive terms s(n)/s(n+1) enumerate all positive rationals.
    """
    if n == 0:
        return 0
    if n == 1:
        return 1
    if n % 2 == 0:
        return stern_sequence(n // 2)
    else:
        return stern_sequence(n // 2) + stern_sequence(n // 2 + 1)


def demo():
    print("=" * 60)
    print("STERN-BROCOT TREE DEMO")
    print("Demonstrating properties formalized in Lean 4")
    print("=" * 60)
    
    # Demo 1: Tree generation with adjacency verification
    print("\n1. STERN-BROCOT TREE (depth 4)")
    print("   Each node shows the adjacency invariant (bc-ad=1) status")
    print()
    tree = generate_tree(depth=4)
    print_tree(tree)
    
    # Demo 2: Finding rationals in the tree
    print("\n\n2. FINDING RATIONALS IN THE TREE")
    print("   (path corresponds to continued fraction expansion)")
    print()
    
    test_fractions = [(1, 2), (2, 3), (3, 5), (7, 11), (22, 7), (355, 113)]
    for p, q in test_fractions:
        if gcd(p, q) != 1:
            continue
        path, node = stern_brocot_path(p, q)
        f = Fraction(p, q)
        print(f"   {p}/{q} = {float(f):.6f}")
        print(f"   Path: {path}")
        print(f"   Verified: node = {node[0]}/{node[1]} {'✓' if node == (p,q) else '✗'}")
        print()
    
    # Demo 3: Stern's diatomic sequence
    print("3. STERN'S DIATOMIC SEQUENCE")
    print("   s(n)/s(n+1) enumerates all positive rationals")
    print()
    N = 20
    seq = [stern_sequence(i) for i in range(N + 1)]
    print(f"   s(0..{N}) = {seq}")
    print()
    print("   Consecutive ratios s(n)/s(n+1):")
    for i in range(1, N):
        if seq[i + 1] > 0:
            f = Fraction(seq[i], seq[i + 1])
            print(f"   s({i})/s({i+1}) = {seq[i]}/{seq[i+1]} = {f}")
    
    # Demo 4: Adjacency invariant verification
    print("\n\n4. ADJACENCY INVARIANT VERIFICATION")
    print("   Verifying bc - ad = 1 at 1000 random paths")
    print()
    
    import random
    random.seed(42)
    all_valid = True
    for trial in range(1000):
        left = (0, 1)
        right = (1, 0)
        depth = random.randint(1, 20)
        for _ in range(depth):
            med = mediant(left, right)
            if not verify_adjacency(left, med) or not verify_adjacency(med, right):
                all_valid = False
                break
            if random.random() < 0.5:
                right = med
            else:
                left = med
    
    print(f"   All 1000 random paths satisfy adjacency invariant: {'✓' if all_valid else '✗'}")
    print()
    print("   This corresponds to the theorem `adjacency_invariant` in Lean:")
    print("   theorem adjacency_invariant (p : Path) (a b c d : ℕ)")
    print("       (h : b * c = a * d + 1) :")
    print("       let (a', b', c', d') := navigateBounds p (a, b, c, d)")
    print("       b' * c' = a' * d' + 1")


if __name__ == "__main__":
    demo()
