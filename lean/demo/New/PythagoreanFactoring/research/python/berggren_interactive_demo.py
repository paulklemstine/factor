#!/usr/bin/env python3
"""
Berggren-Lorentz Factoring: Interactive Demo

Run this script to interactively explore the Berggren tree and
attempt to factor composite numbers using the tree descent method.

Usage:
    python3 berggren_interactive_demo.py          # Interactive mode
    python3 berggren_interactive_demo.py 667      # Factor 667
    python3 berggren_interactive_demo.py --tree 5  # Show tree to depth 5
"""

import math
import sys
from collections import deque

# ─────────────────────────────────────────────────────────────────────────────
# Berggren Matrix Operations
# ─────────────────────────────────────────────────────────────────────────────

def berggren_A(a, b, c):
    return (a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c)

def berggren_B(a, b, c):
    return (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c)

def berggren_C(a, b, c):
    return (-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c)

def inv_berggren(a, b, c):
    """Try all three inverse matrices, return the one giving positive components."""
    candidates = [
        ((a + 2*b - 2*c, -2*a - b + 2*c, -2*a - 2*b + 3*c), 'A⁻¹'),
        ((a + 2*b - 2*c, 2*a + b - 2*c, -2*a - 2*b + 3*c), 'B⁻¹'),
        ((-a - 2*b + 2*c, 2*a + b - 2*c, -2*a - 2*b + 3*c), 'C⁻¹'),
    ]
    for (pa, pb, pc), name in candidates:
        if pa > 0 and pb > 0 and pc > 0 and pa**2 + pb**2 == pc**2:
            return (pa, pb, pc), name
    # Try with swapped legs
    a, b = b, a
    candidates2 = [
        ((a + 2*b - 2*c, -2*a - b + 2*c, -2*a - 2*b + 3*c), 'A⁻¹(swap)'),
        ((a + 2*b - 2*c, 2*a + b - 2*c, -2*a - 2*b + 3*c), 'B⁻¹(swap)'),
        ((-a - 2*b + 2*c, 2*a + b - 2*c, -2*a - 2*b + 3*c), 'C⁻¹(swap)'),
    ]
    for (pa, pb, pc), name in candidates2:
        if pa > 0 and pb > 0 and pc > 0 and pa**2 + pb**2 == pc**2:
            return (pa, pb, pc), name
    return None, None


# ─────────────────────────────────────────────────────────────────────────────
# Tree Descent Path
# ─────────────────────────────────────────────────────────────────────────────

def descend_to_root(a, b, c, verbose=True):
    """Ascend from (a,b,c) to root (3,4,5), printing each step."""
    if a % 2 == 0:
        a, b = b, a

    path = []
    step = 0

    if verbose:
        print(f"\n  {'Step':>4}  {'Triple':>25}  {'Hypotenuse':>12}  {'Matrix':>10}")
        print(f"  {'─'*4}  {'─'*25}  {'─'*12}  {'─'*10}")
        print(f"  {step:4d}  ({a:>7d}, {b:>7d}, {c:>7d})  {c:12d}  {'start':>10}")

    while (a, b, c) != (3, 4, 5) and (a, b, c) != (4, 3, 5):
        parent, name = inv_berggren(a, b, c)
        if parent is None:
            if verbose:
                print(f"  ⚠ Cannot find parent — not a primitive triple or at root")
            break
        a, b, c = parent
        step += 1
        path.append(name)
        if verbose and step <= 50:
            print(f"  {step:4d}  ({a:>7d}, {b:>7d}, {c:>7d})  {c:12d}  {name:>10}")
        if step > 10000:
            if verbose:
                print(f"  ⚠ Exceeded 10000 steps, stopping")
            break

    if verbose and step > 50:
        print(f"  ... ({step - 50} more steps) ...")

    return step, path


# ─────────────────────────────────────────────────────────────────────────────
# Factoring via Berggren Descent
# ─────────────────────────────────────────────────────────────────────────────

def factor_via_berggren(N, verbose=True):
    """
    Attempt to factor N using the Berggren tree approach.

    Method:
    1. Find all same-parity divisor pairs (d, e) of N²
    2. Each gives a Pythagorean triple (N, (e-d)/2, (e+d)/2)
    3. Ascend each triple through the tree
    4. At each node, check gcd(leg, N) for non-trivial factors
    """
    if verbose:
        print(f"\n{'═'*60}")
        print(f"  Factoring N = {N} via Berggren Tree Descent")
        print(f"{'═'*60}")

    if N % 2 == 0:
        if verbose:
            print(f"  N is even: {N} = 2 × {N//2}")
        return {2, N // 2}

    N_sq = N * N
    factors = set()
    triples_checked = 0

    # Find all same-parity divisor pairs of N²
    divisor_pairs = []
    for d in range(1, int(math.isqrt(N_sq)) + 1):
        if N_sq % d == 0:
            e = N_sq // d
            if d < e and d % 2 == e % 2:
                divisor_pairs.append((d, e))

    if verbose:
        print(f"\n  Same-parity divisor pairs of N² = {N_sq}: {len(divisor_pairs)}")

    for d, e in divisor_pairs:
        b = (e - d) // 2
        c = (e + d) // 2

        if verbose:
            print(f"\n  ┌─ Divisor pair (d={d}, e={e})")
            print(f"  │  Triple: ({N}, {b}, {c})")
            print(f"  │  Verify: {N}² + {b}² = {N**2 + b**2} = {c}² = {c**2}: {'✓' if N**2 + b**2 == c**2 else '✗'}")

        # Check this triple for factors
        for leg in [b, c - b, c + b]:
            g = math.gcd(abs(leg), N)
            if 1 < g < N:
                factors.add(g)
                factors.add(N // g)

        # Ascend through the tree
        current = (N, b, c) if N % 2 == 1 else (b, N, c)
        depth = 0
        while current != (3, 4, 5) and current != (4, 3, 5) and depth < 500:
            parent, name = inv_berggren(*current)
            if parent is None:
                # Try swapping
                current = (current[1], current[0], current[2])
                parent, name = inv_berggren(*current)
                if parent is None:
                    break
            current = parent
            depth += 1
            triples_checked += 1

            for leg in [current[0], current[1]]:
                g = math.gcd(abs(leg), N)
                if 1 < g < N:
                    factors.add(g)
                    factors.add(N // g)

    if verbose:
        print(f"\n  └─ Results:")
        print(f"     Triples checked: {triples_checked}")
        if factors:
            flist = sorted(factors)
            print(f"     Factors found: {flist}")
            print(f"     Verification: {' × '.join(map(str, flist[:2]))} = {flist[0] * flist[1]}")
        else:
            print(f"     No non-trivial factors found (N may be prime)")

    return factors


# ─────────────────────────────────────────────────────────────────────────────
# Tree Display
# ─────────────────────────────────────────────────────────────────────────────

def show_tree(max_depth=3):
    """Display the Berggren tree up to given depth."""
    print(f"\n{'═'*60}")
    print(f"  Berggren Tree (depth ≤ {max_depth})")
    print(f"{'═'*60}")

    queue = deque([(3, 4, 5, 0, "root")])
    by_depth = {}

    while queue:
        a, b, c, d, label = queue.popleft()
        if d > max_depth:
            continue
        if d not in by_depth:
            by_depth[d] = []
        by_depth[d].append((a, b, c, label))

        if d < max_depth:
            for fn, name in [(berggren_A, "A"), (berggren_B, "B"), (berggren_C, "C")]:
                na, nb, nc = fn(a, b, c)
                if na < 0: na = -na
                if nb < 0: nb = -nb
                queue.append((na, nb, nc, d + 1, f"{label}→{name}"))

    for d in sorted(by_depth.keys()):
        print(f"\n  Depth {d}: ({len(by_depth[d])} nodes)")
        for a, b, c, label in sorted(by_depth[d], key=lambda x: x[2]):
            ratio = a / c if c > 0 else 0
            print(f"    ({a:>7d}, {b:>7d}, {c:>7d})  a/c={ratio:.4f}  [{label}]")


# ─────────────────────────────────────────────────────────────────────────────
# Euclid Parameter Analysis
# ─────────────────────────────────────────────────────────────────────────────

def analyze_euclid_params(m, n):
    """Analyze a triple from its Euclid parameters."""
    if m <= n or n <= 0:
        print("  Error: need m > n > 0")
        return
    if math.gcd(m, n) != 1 or (m - n) % 2 == 0:
        print("  Error: need gcd(m,n)=1 and m-n odd")
        return

    a = m**2 - n**2
    b = 2 * m * n
    c = m**2 + n**2

    print(f"\n{'═'*60}")
    print(f"  Euclid Parameters: m={m}, n={n}")
    print(f"{'═'*60}")
    print(f"  Triple: ({a}, {b}, {c})")
    print(f"  Verify: {a}² + {b}² = {a**2} + {b**2} = {a**2 + b**2} = {c}² = {c**2}: "
          f"{'✓' if a**2 + b**2 == c**2 else '✗'}")
    print(f"  Hypotenuse: {c} ({c.bit_length()} bits)")
    print(f"  log₂(c) = {math.log2(c):.4f}")

    # Find depth by ascending
    depth, path = descend_to_root(a, b, c, verbose=False)
    print(f"  Berggren depth: {depth}")
    print(f"  Depth / log₂(c) = {depth / math.log2(c):.4f}")

    # Euclidean algorithm steps for (m, n)
    steps = 0
    x, y = m, n
    cf = []
    while y > 0:
        cf.append(x // y)
        x, y = y, x % y
        steps += 1
    print(f"  Euclidean algorithm steps for ({m}, {n}): {steps}")
    print(f"  Continued fraction of m/n: [{', '.join(map(str, cf))}]")
    print(f"  ⟹ Depth ≈ Euclidean steps (connection to continued fractions)")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '--tree':
            depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3
            show_tree(depth)
        elif sys.argv[1] == '--euclid':
            m, n = int(sys.argv[2]), int(sys.argv[3])
            analyze_euclid_params(m, n)
        else:
            N = int(sys.argv[1])
            factor_via_berggren(N)
        return

    # Interactive demo
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║     BERGGREN-LORENTZ FACTORING: INTERACTIVE DEMO           ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    print("\nCommands:")
    print("  factor <N>        - Factor N via Berggren descent")
    print("  tree <depth>      - Show Berggren tree to depth")
    print("  depth <a> <b> <c> - Find depth of triple (a,b,c)")
    print("  euclid <m> <n>    - Analyze triple from Euclid params")
    print("  quit              - Exit")

    while True:
        try:
            cmd = input("\n> ").strip().split()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not cmd:
            continue
        elif cmd[0] == 'quit':
            break
        elif cmd[0] == 'factor' and len(cmd) == 2:
            factor_via_berggren(int(cmd[1]))
        elif cmd[0] == 'tree':
            d = int(cmd[1]) if len(cmd) > 1 else 3
            show_tree(d)
        elif cmd[0] == 'depth' and len(cmd) == 4:
            a, b, c = int(cmd[1]), int(cmd[2]), int(cmd[3])
            if a**2 + b**2 == c**2:
                descend_to_root(a, b, c)
            else:
                print(f"  Not a Pythagorean triple: {a}² + {b}² = {a**2+b**2} ≠ {c}² = {c**2}")
        elif cmd[0] == 'euclid' and len(cmd) == 3:
            analyze_euclid_params(int(cmd[1]), int(cmd[2]))
        else:
            print("  Unknown command. Try: factor, tree, depth, euclid, quit")


if __name__ == "__main__":
    # If no args, run a quick demo
    if len(sys.argv) == 1:
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║     BERGGREN-LORENTZ FACTORING: QUICK DEMO                 ║")
        print("╚══════════════════════════════════════════════════════════════╝")

        # Demo: factor some composites
        for N in [15, 77, 221, 667, 1147, 3127]:
            factor_via_berggren(N, verbose=True)

        # Demo: Euclid parameter analysis
        print("\n\n" + "═"*60)
        print("EUCLID PARAMETER ANALYSIS")
        print("═"*60)
        for m, n in [(2,1), (5,2), (10,3), (20,1), (20,19)]:
            analyze_euclid_params(m, n)

        # Demo: show tree
        show_tree(3)
