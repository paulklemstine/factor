#!/usr/bin/env python3
"""
Berggren Tree Explorer
======================
Interactive demo that generates, visualizes, and explores the Berggren tree
of primitive Pythagorean triples.

Usage:
    python berggren_tree_explorer.py [--depth N] [--mode {tree,factor,pell,hyperbolic}]

Examples:
    python berggren_tree_explorer.py --depth 4 --mode tree
    python berggren_tree_explorer.py --mode factor --number 667
    python berggren_tree_explorer.py --mode pell --depth 10
    python berggren_tree_explorer.py --mode hyperbolic --depth 5
"""

import numpy as np
from math import gcd, isqrt, sqrt
from collections import deque
import argparse
import sys

# ─── Berggren Matrices ───────────────────────────────────────────────────────

# 3×3 matrices acting on (a, b, c)
A = np.array([[1, -2, 2],
              [2, -1, 2],
              [2, -2, 3]], dtype=int)

B = np.array([[1, 2, 2],
              [2, 1, 2],
              [2, 2, 3]], dtype=int)

C = np.array([[-1, 2, 2],
              [-2, 1, 2],
              [-2, 2, 3]], dtype=int)

# Inverse matrices for descent
A_inv = np.array([[1, 2, -2],
                  [-2, -1, 2],
                  [-2, -2, 3]], dtype=int)

B_inv = np.array([[1, 2, -2],
                  [2, 1, -2],
                  [-2, -2, 3]], dtype=int)

C_inv = np.array([[-1, -2, 2],
                  [2, 1, -2],
                  [-2, -2, 3]], dtype=int)

MATRICES = {'A': A, 'B': B, 'C': C}
INV_MATRICES = {'A': A_inv, 'B': B_inv, 'C': C_inv}

ROOT = np.array([3, 4, 5], dtype=int)

# Lorentz metric
Q = np.diag([1, 1, -1])


def lorentz_form(v):
    """Compute Q(v) = a² + b² - c²"""
    return v[0]**2 + v[1]**2 - v[2]**2


def verify_lorentz_preservation():
    """Verify all three matrices preserve the Lorentz form."""
    print("═══ Lorentz Form Preservation ═══")
    print(f"Q = diag(1, 1, -1)")
    for name, M in MATRICES.items():
        result = M.T @ Q @ M
        preserved = np.array_equal(result, Q)
        det = int(round(np.linalg.det(M)))
        print(f"  B_{name}ᵀ · Q · B_{name} = Q : {preserved}  (det = {det})")
    print()


# ─── Tree Generation ─────────────────────────────────────────────────────────

def generate_tree(max_depth):
    """Generate all Berggren tree nodes up to given depth."""
    nodes = []
    queue = deque()
    queue.append((ROOT, "", 0))  # (triple, path, depth)

    while queue:
        triple, path, depth = queue.popleft()
        a, b, c = int(triple[0]), int(triple[1]), int(triple[2])
        nodes.append({
            'triple': (a, b, c),
            'path': path if path else 'root',
            'depth': depth,
            'hypotenuse': c,
            'lorentz': a**2 + b**2 - c**2,
        })

        if depth < max_depth:
            for name, M in MATRICES.items():
                child = M @ triple
                # Ensure first leg is positive (C branch may negate)
                if child[0] < 0:
                    child = -child
                queue.append((child, path + name, depth + 1))

    return nodes


def print_tree(max_depth=3):
    """Print the Berggren tree in a formatted display."""
    print(f"═══ Berggren Tree (depth ≤ {max_depth}) ═══")
    print(f"{'Path':<12} {'Triple':<20} {'Hyp':>6} {'Q(a,b,c)':>10} {'a²+b²=c²':>10}")
    print("─" * 60)

    nodes = generate_tree(max_depth)
    for n in sorted(nodes, key=lambda x: (x['depth'], x['path'])):
        a, b, c = n['triple']
        check = "✓" if a**2 + b**2 == c**2 else "✗"
        print(f"{n['path']:<12} ({a}, {b}, {c}){'':<{max(0,16-len(f'({a}, {b}, {c})'))}} "
              f"{c:>6} {n['lorentz']:>10} {check:>10}")

    total = len(nodes)
    print(f"\nTotal triples: {total}")
    print(f"All satisfy a²+b²=c²: {all(n['lorentz'] == 0 for n in nodes)}")
    print()


# ─── Descent / Factoring ─────────────────────────────────────────────────────

def find_pythagorean_triples(N, max_triples=10):
    """Find Pythagorean triples with leg N using divisor enumeration."""
    triples = []
    N2 = N * N
    # N² = (c-b)(c+b), enumerate divisors d of N² with d < √(N²)
    for d in range(1, isqrt(N2) + 1):
        if N2 % d == 0:
            e = N2 // d
            if d < e and (d + e) % 2 == 0:
                b = (e - d) // 2
                c = (e + d) // 2
                if b > 0 and c > 0:
                    triples.append((N, b, c))
                    if len(triples) >= max_triples:
                        break
    return triples


def descend_to_root(triple):
    """Descend from a triple back to (3,4,5) using inverse Berggren matrices."""
    path = []
    v = np.array(triple, dtype=np.int64)
    steps = 0
    max_steps = 100000

    while not np.array_equal(v, ROOT) and steps < max_steps:
        # Try each inverse matrix
        candidates = {}
        for name, M_inv in INV_MATRICES.items():
            w = M_inv @ v
            # Valid child must have positive hypotenuse and be a PPT
            if w[2] > 0 and w[2] < v[2]:
                candidates[name] = w

        if not candidates:
            break

        # Choose the one with smallest hypotenuse
        best_name = min(candidates, key=lambda n: candidates[n][2])
        v = candidates[best_name]
        path.append(best_name)
        steps += 1

    return path, v


def factor_via_berggren(N):
    """Attempt to factor N using Berggren tree descent."""
    print(f"═══ Factoring N = {N} via Berggren Tree ═══")

    triples = find_pythagorean_triples(N)
    print(f"Found {len(triples)} Pythagorean triples with leg {N}:")

    results = []
    for i, (a, b, c) in enumerate(triples):
        print(f"\n  Triple #{i+1}: ({a}, {b}, {c})")
        print(f"    Verification: {a}² + {b}² = {a**2} + {b**2} = {a**2+b**2} = {c}² = {c**2} {'✓' if a**2+b**2==c**2 else '✗'}")
        print(f"    (c-b)(c+b) = {c-b} × {c+b} = {(c-b)*(c+b)} = {a}² = {a**2} {'✓' if (c-b)*(c+b)==a**2 else '✗'}")

        # Try GCD extraction
        g1 = gcd(a, c - b)
        g2 = gcd(a, c + b)
        if 1 < g1 < N:
            print(f"    ★ gcd({a}, {c-b}) = {g1} → factor found! {N} = {g1} × {N//g1}")
            results.append((g1, N // g1))
        if 1 < g2 < N:
            print(f"    ★ gcd({a}, {c+b}) = {g2} → factor found! {N} = {g2} × {N//g2}")
            results.append((g2, N // g2))

        # Descent
        path, final = descend_to_root((a, b, c))
        if np.array_equal(final, ROOT):
            print(f"    Descent path: {''.join(path)} (depth = {len(path)})")
        else:
            print(f"    Descent: {len(path)} steps → ({final[0]}, {final[1]}, {final[2]})")

        # Check GCDs along descent
        v = np.array([a, b, c], dtype=np.int64)
        for step, name in enumerate(path[:20]):  # Check first 20 steps
            M_inv = INV_MATRICES[name]
            v = M_inv @ v
            g = gcd(int(v[0]), N)
            if 1 < g < N:
                print(f"    ★ At descent step {step+1}: gcd(leg={v[0]}, {N}) = {g}")
                results.append((g, N // g))
                break

    if results:
        p, q = results[0]
        print(f"\n  ★★★ RESULT: {N} = {p} × {q} ★★★")
    else:
        print(f"\n  No non-trivial factors found (N may be prime)")
    print()
    return results


# ─── Pell Sequence ────────────────────────────────────────────────────────────

def pell_hypotenuses(n):
    """Generate the B-branch Pell hypotenuse sequence."""
    print(f"═══ B-Branch Pell Hypotenuses (first {n} terms) ═══")
    print("Recurrence: c_{n+2} = 6·c_{n+1} - c_n")
    print()

    seq = [5, 29]
    for i in range(2, n):
        seq.append(6 * seq[-1] - seq[-2])

    print(f"{'n':>4} {'c_n':>20} {'ratio c_{n}/c_{n-1}':>20} {'log₂(c_n)':>12}")
    print("─" * 60)
    for i, c in enumerate(seq):
        ratio = f"{c / seq[i-1]:.6f}" if i > 0 else "—"
        log2c = f"{np.log2(float(c)):.3f}" if c > 0 else "—"
        print(f"{i:>4} {c:>20} {ratio:>20} {log2c:>12}")

    golden = 3 + 2 * sqrt(2)
    print(f"\nGrowth rate: 3 + 2√2 ≈ {golden:.6f}")
    print(f"log₂(3+2√2) ≈ {np.log2(golden):.6f}")
    print(f"Depth to reach c ≈ 10^k: d ≈ k / {np.log10(golden):.4f}")
    print()
    return seq


# ─── Hyperbolic Mapping ──────────────────────────────────────────────────────

def hyperbolic_disk_points(max_depth=5):
    """Map Berggren tree nodes to the Poincaré disk model."""
    print(f"═══ Hyperbolic Disk Mapping (depth ≤ {max_depth}) ═══")
    nodes = generate_tree(max_depth)

    print(f"{'Path':<12} {'(a/c, b/c)':>20} {'r = √(a²+b²)/c':>18} {'Branch':>8}")
    print("─" * 60)

    points = []
    for n in sorted(nodes, key=lambda x: (x['depth'], x['path'])):
        a, b, c = n['triple']
        x, y = a / c, b / c
        r = sqrt(x**2 + y**2)
        branch = n['path'][0] if n['path'] != 'root' else '—'
        print(f"{n['path']:<12} ({x:>8.5f}, {y:>8.5f}) {r:>18.10f} {branch:>8}")
        points.append((x, y, n['path'], n['depth']))

    print(f"\nAll points lie on the unit circle (r = 1) since a²+b²=c²")
    print("In hyperbolic geometry, these tile the boundary of the Poincaré disk.")
    print()
    return points


# ─── Depth Spectrum Analysis ─────────────────────────────────────────────────

def depth_spectrum(max_depth=6):
    """Analyze hypotenuse growth rates along different branches."""
    print(f"═══ Depth Spectrum Analysis ═══")
    print()

    # Pure A-branch
    print("Pure A-branch (slow lane):")
    v = ROOT.copy()
    for d in range(max_depth + 1):
        print(f"  depth {d}: ({v[0]}, {v[1]}, {v[2]})  hyp = {v[2]}  √hyp ≈ {sqrt(v[2]):.2f}")
        v = A @ v
        if v[0] < 0:
            v = -v

    print()

    # Pure B-branch
    print("Pure B-branch (fast lane):")
    v = ROOT.copy()
    for d in range(max_depth + 1):
        ratio = f"  ratio = {v[2] / prev_c:.4f}" if d > 0 else ""
        print(f"  depth {d}: ({v[0]}, {v[1]}, {v[2]})  hyp = {v[2]}{ratio}")
        prev_c = v[2]
        v = B @ v

    print()

    # Pure C-branch
    print("Pure C-branch (mirror of A):")
    v = ROOT.copy()
    for d in range(max_depth + 1):
        print(f"  depth {d}: ({v[0]}, {v[1]}, {v[2]})  hyp = {v[2]}  √hyp ≈ {sqrt(v[2]):.2f}")
        v = C @ v
        if v[0] < 0:
            v = -v

    print()


# ─── Hypothesis Testing ──────────────────────────────────────────────────────

def test_factoring_hypothesis():
    """Test the Berggren factoring approach on semiprimes."""
    print("═══ Hypothesis Testing: Berggren Factoring on Semiprimes ═══")
    print()

    # Generate semiprimes from small odd primes
    primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    semiprimes = []
    for i, p in enumerate(primes):
        for q in primes[i+1:]:
            semiprimes.append((p * q, p, q))

    successes = 0
    total = 0
    results_table = []

    for N, p, q in semiprimes[:30]:  # Test first 30
        total += 1
        triples = find_pythagorean_triples(N, max_triples=5)
        found = False

        for a, b, c in triples:
            # Check direct GCD
            for val in [c - b, c + b, b]:
                g = gcd(a, val)
                if 1 < g < N:
                    found = True
                    break

            # Check descent GCDs
            if not found:
                path_steps, final = descend_to_root((a, b, c))
                v = np.array([a, b, c], dtype=np.int64)
                for name in path_steps[:50]:
                    M_inv = INV_MATRICES[name]
                    v = M_inv @ v
                    for leg in [int(v[0]), int(v[1])]:
                        g = gcd(abs(leg), N)
                        if 1 < g < N:
                            found = True
                            break
                    if found:
                        break

            if found:
                break

        if found:
            successes += 1
        results_table.append((N, p, q, found, len(triples)))

    print(f"{'N':>6} {'= p×q':>10} {'#triples':>9} {'factored':>9}")
    print("─" * 36)
    for N, p, q, found, nt in results_table:
        print(f"{N:>6} = {p}×{q:<4} {nt:>9} {'✓' if found else '✗':>9}")

    print(f"\nSuccess rate: {successes}/{total} = {100*successes/total:.1f}%")
    print()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Berggren Tree Explorer")
    parser.add_argument('--depth', type=int, default=3, help='Tree depth')
    parser.add_argument('--mode', choices=['tree', 'factor', 'pell', 'hyperbolic',
                                           'spectrum', 'verify', 'hypothesis', 'all'],
                        default='all', help='Exploration mode')
    parser.add_argument('--number', type=int, default=667, help='Number to factor')
    args = parser.parse_args()

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║        THE BERGGREN TREE EXPLORER                          ║")
    print("║  Pythagorean Triples × Lorentz Group × Integer Factoring   ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    if args.mode in ('verify', 'all'):
        verify_lorentz_preservation()

    if args.mode in ('tree', 'all'):
        print_tree(args.depth)

    if args.mode in ('spectrum', 'all'):
        depth_spectrum(min(args.depth, 8))

    if args.mode in ('pell', 'all'):
        pell_hypotenuses(min(args.depth + 5, 15))

    if args.mode in ('hyperbolic', 'all'):
        hyperbolic_disk_points(min(args.depth, 4))

    if args.mode in ('factor', 'all'):
        factor_via_berggren(args.number)

    if args.mode in ('hypothesis', 'all'):
        test_factoring_hypothesis()


if __name__ == '__main__':
    main()
