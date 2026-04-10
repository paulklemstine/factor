#!/usr/bin/env python3
"""
Visualization demo for the Berggren tree and hyperbolic shortcuts.
Generates terminal-based visualization of the tree structure and factoring results.
"""

import numpy as np
from math import gcd

# Berggren matrices
B1 = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]], dtype=np.int64)
B2 = np.array([[1,  2, 2], [2,  1, 2], [2,  2, 3]], dtype=np.int64)
B3 = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]], dtype=np.int64)

ROOT = np.array([3, 4, 5], dtype=np.int64)
MATRICES = [B1, B2, B3]
BRANCH_LABELS = ["L", "M", "R"]


def generate_tree(depth):
    """Generate tree as nested dict."""
    def build(triple, d):
        a, b, c = triple
        node = {
            'triple': (int(a), int(b), int(c)),
            'children': []
        }
        if d < depth:
            for M in MATRICES:
                child = M @ triple
                node['children'].append(build(child, d + 1))
        return node
    return build(ROOT, 0)


def print_tree(node, prefix="", is_last=True, branch_name="root"):
    """Pretty-print the Berggren tree."""
    connector = "└── " if is_last else "├── "
    a, b, c = node['triple']
    dos = f"({c}-{b})({c}+{b}) = {c-b}×{c+b} = {(c-b)*(c+b)} = {a}²"
    g = gcd(c - b, a) if a > 0 else 0
    factor_info = f"  gcd({c-b},{a})={g}" if g > 1 and g < a else ""

    print(f"{prefix}{connector}[{branch_name}] ({a}, {b}, {c}){factor_info}")

    child_prefix = prefix + ("    " if is_last else "│   ")
    for i, child in enumerate(node['children']):
        is_last_child = (i == len(node['children']) - 1)
        print_tree(child, child_prefix, is_last_child, BRANCH_LABELS[i])


def demo_middle_branch_factoring():
    """Show the middle branch factoring sequence."""
    print("\n" + "=" * 70)
    print("Middle Branch Factoring Sequence")
    print("=" * 70)

    v = ROOT.copy()
    for i in range(8):
        a, b, c = v
        d1, d2 = c - b, c + b
        g = gcd(d1, a)

        bar_len = min(50, a // max(g, 1))
        bar = "█" * min(bar_len, 50)

        factors = []
        if g > 1 and g < a:
            factors.append(f"{g}")
        g2 = gcd(d2, a)
        if g2 > 1 and g2 < a:
            factors.append(f"{g2}")

        factor_str = f" → factors: {', '.join(factors)}" if factors else " → trivial"
        print(f"  n={i}: ({a:>8}, {b:>8}, {c:>8}) | {a} = ", end="")

        if factors:
            print(f"{' × '.join(str(f) for f in sorted(set(int(f) for f in factors)))}" +
                  f" × {a // int(factors[0])}" if factors else f"{a}")
        else:
            print(f"{a} (prime or trivial)")

        v = B2 @ v


def demo_chebyshev():
    """Visualize the Chebyshev recurrence."""
    print("\n" + "=" * 70)
    print("Chebyshev Recurrence: c_{n+1} = 6·c_n - c_{n-1}")
    print("=" * 70)

    v = ROOT.copy()
    hyps = []
    for i in range(10):
        hyps.append(int(v[2]))
        v = B2 @ v

    print(f"\n  {'n':>3}  {'c_n':>15}  {'6c_{n-1} - c_{n-2}':>20}  {'ratio c_n/c_{n-1}':>18}")
    print("  " + "-" * 60)
    for i, h in enumerate(hyps):
        if i >= 2:
            predicted = 6 * hyps[i-1] - hyps[i-2]
            ratio = h / hyps[i-1]
            check = "✓" if predicted == h else "✗"
            print(f"  {i:>3}  {h:>15}  {predicted:>20} {check}  {ratio:>18.10f}")
        elif i == 1:
            ratio = h / hyps[i-1]
            print(f"  {i:>3}  {h:>15}  {'—':>20}   {ratio:>18.10f}")
        else:
            print(f"  {i:>3}  {h:>15}  {'—':>20}   {'—':>18}")

    print(f"\n  Golden ratio of hyperbolic tree: 3 + 2√2 ≈ {3 + 2*2**0.5:.10f}")
    print(f"  Limiting ratio c_n/c_{'{n-1}'}: {hyps[-1]/hyps[-2]:.10f}")


if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  Berggren Tree Visualization                                       ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    print("\nBerggren Tree (depth 2):")
    tree = generate_tree(2)
    print_tree(tree)

    demo_middle_branch_factoring()
    demo_chebyshev()
