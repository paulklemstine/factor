#!/usr/bin/env python3
"""
Hyperbolic Shortcuts Through the Berggren Tree: Factoring Demo

Demonstrates how Pythagorean triples from the Berggren tree can factor composite
numbers via the difference-of-squares identity: (c-b)(c+b) = a².

Usage:
    python demo_factoring.py [number_to_factor]
"""

import numpy as np
from math import gcd, isqrt
from typing import List, Tuple, Optional
import sys

# ─── Berggren Matrices ───────────────────────────────────────────────────────

B1 = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]], dtype=np.int64)  # Left
B2 = np.array([[1,  2, 2], [2,  1, 2], [2,  2, 3]], dtype=np.int64)  # Middle
B3 = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]], dtype=np.int64)  # Right

# Inverse matrices (Lorentz adjoint: B⁻¹ = Q Bᵀ Q)
B1_inv = np.array([[1, 2, -2], [-2, -1, 2], [-2, -2, 3]], dtype=np.int64)
B2_inv = np.array([[1, 2, -2], [2, 1, -2], [-2, -2, 3]], dtype=np.int64)
B3_inv = np.array([[-1, -2, 2], [2, 1, -2], [-2, -2, 3]], dtype=np.int64)

ROOT = np.array([3, 4, 5], dtype=np.int64)

BRANCH_NAMES = {0: "Left (B₁)", 1: "Middle (B₂)", 2: "Right (B₃)"}
MATRICES = [B1, B2, B3]
INV_MATRICES = [B1_inv, B2_inv, B3_inv]


# ─── Core Functions ──────────────────────────────────────────────────────────

def lorentz_form(v):
    """Q(a,b,c) = a² + b² - c². Zero iff Pythagorean."""
    return int(v[0]**2 + v[1]**2 - v[2]**2)


def is_pythagorean(v):
    """Check if (a,b,c) is a Pythagorean triple."""
    return lorentz_form(v) == 0


def factor_via_dos(a, b, c):
    """
    Factor a using the difference-of-squares identity:
    (c-b)(c+b) = a², so gcd(c-b, a) may be a nontrivial factor.
    """
    d1 = c - b
    d2 = c + b
    g1 = gcd(d1, a)
    g2 = gcd(d2, a)
    return {
        'a': a, 'b': b, 'c': c,
        'c_minus_b': d1, 'c_plus_b': d2,
        'product': d1 * d2,  # should equal a²
        'gcd_cmb_a': g1,
        'gcd_cpb_a': g2,
        'factor1': g1 if 1 < g1 < a else None,
        'factor2': g2 if 1 < g2 < a else None,
    }


def generate_tree_bfs(max_depth=5):
    """Generate all triples in the Berggren tree up to a given depth."""
    triples = [(ROOT, [])]  # (triple, path)
    result = [(ROOT.copy(), [])]

    for depth in range(max_depth):
        new_triples = []
        for triple, path in triples:
            for i, M in enumerate(MATRICES):
                child = M @ triple
                child_path = path + [i]
                new_triples.append((child, child_path))
                result.append((child.copy(), child_path))
        triples = new_triples

    return result


def middle_branch_sequence(n_steps=10):
    """Generate the all-middle-branch sequence: 5, 29, 169, 985, ..."""
    v = ROOT.copy()
    sequence = [v.copy()]
    for _ in range(n_steps):
        v = B2 @ v
        sequence.append(v.copy())
    return sequence


def shortcut_matrix(path):
    """Compute the composite matrix for a given path (list of 0,1,2)."""
    result = np.eye(3, dtype=np.int64)
    for d in path:
        result = MATRICES[d] @ result
    return result


def fast_shortcut_power(matrix, n):
    """Compute matrix^n via repeated squaring (O(log n) multiplications)."""
    if n == 0:
        return np.eye(3, dtype=np.int64)
    if n == 1:
        return matrix.copy()
    if n % 2 == 0:
        half = fast_shortcut_power(matrix, n // 2)
        return half @ half
    else:
        return matrix @ fast_shortcut_power(matrix, n - 1)


def ascend_to_root(triple):
    """
    Ascend the Berggren tree from a given primitive triple back to (3,4,5).
    Returns the path taken (in reverse).
    """
    v = np.array(triple, dtype=np.int64)
    path = []
    max_iter = 1000

    while not np.array_equal(v, ROOT) and max_iter > 0:
        max_iter -= 1
        # Try each inverse matrix; the correct one gives all-positive entries
        found = False
        for i, M_inv in enumerate(INV_MATRICES):
            parent = M_inv @ v
            if all(parent > 0):
                v = parent
                path.append(i)
                found = True
                break
        if not found:
            break

    return path[::-1], np.array_equal(v, ROOT)


def find_triples_with_leg(n, max_depth=8):
    """
    Search the Berggren tree for triples with first leg = n or second leg = n.
    Returns a list of (triple, path) pairs.
    """
    results = []
    stack = [(ROOT.copy(), [])]

    while stack:
        triple, path = stack.pop()
        if len(path) > max_depth:
            continue

        a, b, c = triple
        if abs(a) == n or abs(b) == n:
            results.append((triple.copy(), path[:]))

        # Prune: if hypotenuse is too large, skip
        if c > 10 * n * n:
            continue

        for i, M in enumerate(MATRICES):
            child = M @ triple
            stack.append((child, path + [i]))

    return results


# ─── Demo Functions ──────────────────────────────────────────────────────────

def demo_basic():
    """Demonstrate basic Berggren tree properties."""
    print("=" * 70)
    print("DEMO 1: Berggren Tree Basics")
    print("=" * 70)

    print(f"\nRoot triple: {ROOT} → {ROOT[0]}² + {ROOT[1]}² = {ROOT[0]**2} + {ROOT[1]**2} = {ROOT[2]**2} = {ROOT[2]}²")
    print(f"Lorentz form Q(3,4,5) = {lorentz_form(ROOT)}")

    print("\nThree children of (3, 4, 5):")
    for i, (M, name) in enumerate(zip(MATRICES, BRANCH_NAMES.values())):
        child = M @ ROOT
        a, b, c = child
        print(f"  {name}: ({a}, {b}, {c})  →  {a}² + {b}² = {a**2} + {b**2} = {c**2} = {c}²  ✓")

    print("\nLorentz form preserved:")
    Q = np.diag([1, 1, -1])
    for i, (M, name) in enumerate(zip(MATRICES, BRANCH_NAMES.values())):
        preserved = np.array_equal(M.T @ Q @ M, Q)
        det = int(np.linalg.det(M).round())
        print(f"  {name}: Bᵢᵀ Q Bᵢ = Q? {preserved}  det = {det}")


def demo_shortcuts():
    """Demonstrate hyperbolic shortcuts."""
    print("\n" + "=" * 70)
    print("DEMO 2: Hyperbolic Shortcuts")
    print("=" * 70)

    print("\nMiddle branch sequence (B₂ⁿ applied to root):")
    seq = middle_branch_sequence(8)
    for i, v in enumerate(seq):
        a, b, c = v
        print(f"  n={i}: ({a:>8}, {b:>8}, {c:>8})  hyp_ratio = {c/seq[max(0,i-1)][2]:.4f}" if i > 0
              else f"  n={i}: ({a:>8}, {b:>8}, {c:>8})")

    print("\nChebyshev recurrence c_{n+1} = 6c_n - c_{n-1}:")
    hyps = [v[2] for v in seq]
    for i in range(2, min(7, len(hyps))):
        predicted = 6 * hyps[i-1] - hyps[i-2]
        actual = hyps[i]
        print(f"  c_{i} = 6·{hyps[i-1]} - {hyps[i-2]} = {predicted} {'✓' if predicted == actual else '✗'}")

    print(f"\nFast shortcut: B₂^{20} via repeated squaring:")
    B2_20 = fast_shortcut_power(B2, 20)
    triple_20 = B2_20 @ ROOT
    a, b, c = triple_20
    print(f"  Triple at depth 20: ({a}, {b}, {c})")
    print(f"  Hypotenuse has {len(str(c))} digits")
    print(f"  Is Pythagorean? {a**2 + b**2 == c**2}")


def demo_factoring():
    """Demonstrate factoring via Pythagorean triples."""
    print("\n" + "=" * 70)
    print("DEMO 3: Factoring via Pythagorean Triples")
    print("=" * 70)

    examples = [
        (21, 20, 29, "B₂ applied to (3,4,5)"),
        (119, 120, 169, "B₂² applied to (3,4,5)"),
        (697, 696, 985, "B₂³ applied to (3,4,5)"),
    ]

    for a, b, c, desc in examples:
        result = factor_via_dos(a, b, c)
        print(f"\n  Triple ({a}, {b}, {c}) — {desc}")
        print(f"    ({c}-{b})({c}+{b}) = {result['c_minus_b']}×{result['c_plus_b']} = {result['product']} = {a}²")
        print(f"    gcd({result['c_minus_b']}, {a}) = {result['gcd_cmb_a']}", end="")
        if result['factor1']:
            print(f"  → factor {result['factor1']} found! ({a} = {result['factor1']} × {a // result['factor1']})")
        else:
            print(f"  (trivial)")
        print(f"    gcd({result['c_plus_b']}, {a}) = {result['gcd_cpb_a']}", end="")
        if result['factor2']:
            print(f"  → factor {result['factor2']} found! ({a} = {result['factor2']} × {a // result['factor2']})")
        else:
            print(f"  (trivial)")


def demo_factoring_search(n=None):
    """Search for Pythagorean triples that factor a given number."""
    if n is None:
        n = 91  # = 7 × 13

    print(f"\n" + "=" * 70)
    print(f"DEMO 4: Searching for Triples to Factor {n}")
    print("=" * 70)

    triples = find_triples_with_leg(n, max_depth=6)

    if not triples:
        print(f"  No triples found with leg = {n} in search depth")
        return

    print(f"  Found {len(triples)} triples with leg = {n}:")
    for triple, path in triples:
        a, b, c = triple
        path_str = "→".join(["L", "M", "R"][d] for d in path) if path else "root"

        if abs(a) == n:
            result = factor_via_dos(abs(a), abs(b), c)
        else:
            result = factor_via_dos(abs(b), abs(a), c)

        target = result['a']
        f1, f2 = result['factor1'], result['factor2']
        factors_str = ""
        if f1:
            factors_str += f"  → found factor {f1}"
        if f2:
            factors_str += f"  → found factor {f2}"
        if not f1 and not f2:
            factors_str = "  (trivial factors only)"

        print(f"  ({a}, {b}, {c}) path={path_str}")
        print(f"    ({c}-{abs(b)})({c}+{abs(b)}) = {c-abs(b)}×{c+abs(b)} = {(c-abs(b))*(c+abs(b))} = {target}²")
        print(f"    gcd({c-abs(b)}, {target}) = {result['gcd_cmb_a']}, gcd({c+abs(b)}, {target}) = {result['gcd_cpb_a']}{factors_str}")


def demo_tree_ascent():
    """Demonstrate ascending the tree to find the root."""
    print("\n" + "=" * 70)
    print("DEMO 5: Tree Ascent via Inverse Matrices")
    print("=" * 70)

    test_triples = [
        (5, 12, 13),
        (8, 15, 17),
        (7, 24, 25),
        (20, 21, 29),
        (9, 40, 41),
    ]

    for triple in test_triples:
        path, success = ascend_to_root(triple)
        path_str = "→".join(["L", "M", "R"][d] for d in path)
        status = "✓" if success else "✗"
        print(f"  {triple} → path = {path_str} [{status}]")

    # Verify round-trip
    print("\n  Round-trip verification:")
    path = [1, 0, 2, 1]  # M→L→R→M
    mat = shortcut_matrix(path)
    triple = mat @ ROOT
    recovered_path, success = ascend_to_root(triple)
    print(f"    Original path: {'→'.join(['L','M','R'][d] for d in path)}")
    print(f"    Triple: {tuple(triple)}")
    print(f"    Recovered path: {'→'.join(['L','M','R'][d] for d in recovered_path)}")
    print(f"    Match: {path == recovered_path}")


def demo_lorentz_geometry():
    """Demonstrate the Lorentz geometry connection."""
    print("\n" + "=" * 70)
    print("DEMO 6: Lorentz Geometry")
    print("=" * 70)

    Q = np.diag([1, 1, -1])

    print("\n  The Lorentz metric Q = diag(1, 1, -1)")
    print(f"  Q² = I? {np.array_equal(Q @ Q, np.eye(3, dtype=int))}")

    print("\n  Berggren matrices as Lorentz isometries:")
    for i, (M, name) in enumerate(zip(MATRICES, BRANCH_NAMES.values())):
        result = M.T @ Q @ M
        print(f"    {name}: Bᵢᵀ Q Bᵢ = {'Q ✓' if np.array_equal(result, Q) else 'not Q ✗'}")

    print("\n  Lorentz adjoint formula (B⁻¹ = Q Bᵀ Q):")
    for i, (M, M_inv, name) in enumerate(zip(MATRICES, INV_MATRICES, BRANCH_NAMES.values())):
        adjoint = Q @ M.T @ Q
        print(f"    {name}: Q Bᵀ Q = B⁻¹? {np.array_equal(adjoint, M_inv)}")
        print(f"    B · B⁻¹ = I? {np.array_equal(M @ M_inv, np.eye(3, dtype=int))}")


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  Hyperbolic Shortcuts Through the Berggren Tree: Factoring Demo    ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    demo_basic()
    demo_shortcuts()
    demo_factoring()

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 91
    demo_factoring_search(n)

    demo_tree_ascent()
    demo_lorentz_geometry()

    print("\n" + "=" * 70)
    print("All demos complete.")
    print("=" * 70)
