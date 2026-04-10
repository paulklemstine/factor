#!/usr/bin/env python3
"""
Berggren Descent Demo: Pythagorean Triple Tree Exploration

Demonstrates:
1. Forward Berggren tree generation (children of a triple)
2. Inverse descent to root (3,4,5)
3. Universal parent hypotenuse formula
4. Pell recurrence along B2-branch
5. Inside-Out Factoring (IOF) depth-1 equation
6. Pythagorean quadruple Lebesgue parametrization
7. Lorentz form preservation verification
"""

import math
from typing import Tuple, List, Optional

Triple = Tuple[int, int, int]

# ============================================================
# §1. Berggren Forward Transforms
# ============================================================

def fwd_B1(a: int, b: int, c: int) -> Triple:
    """Forward Berggren transform B1."""
    return (a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c)

def fwd_B2(a: int, b: int, c: int) -> Triple:
    """Forward Berggren transform B2."""
    return (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c)

def fwd_B3(a: int, b: int, c: int) -> Triple:
    """Forward Berggren transform B3."""
    return (-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c)

# ============================================================
# §2. Berggren Inverse Transforms
# ============================================================

def inv_B1(a: int, b: int, c: int) -> Triple:
    """Inverse Berggren transform B1^{-1}."""
    return (a + 2*b - 2*c, -2*a - b + 2*c, -2*a - 2*b + 3*c)

def inv_B2(a: int, b: int, c: int) -> Triple:
    """Inverse Berggren transform B2^{-1}."""
    return (a + 2*b - 2*c, 2*a + b - 2*c, -2*a - 2*b + 3*c)

def inv_B3(a: int, b: int, c: int) -> Triple:
    """Inverse Berggren transform B3^{-1}."""
    return (-a - 2*b + 2*c, 2*a + b - 2*c, -2*a - 2*b + 3*c)

# ============================================================
# §3. Lorentz Form
# ============================================================

def lorentz_form(a: int, b: int, c: int) -> int:
    """Lorentz quadratic form Q(a,b,c) = a² + b² - c²."""
    return a**2 + b**2 - c**2

def verify_lorentz_preservation():
    """Verify that all Berggren transforms preserve the Lorentz form."""
    print("=" * 60)
    print("LORENTZ FORM PRESERVATION")
    print("=" * 60)
    test_triples = [(3,4,5), (5,12,13), (8,15,17), (7,24,25)]
    for a, b, c in test_triples:
        Q_orig = lorentz_form(a, b, c)
        for name, transform in [("B1", fwd_B1), ("B2", fwd_B2), ("B3", fwd_B3)]:
            a2, b2, c2 = transform(a, b, c)
            Q_new = lorentz_form(a2, b2, c2)
            status = "✓" if Q_orig == Q_new else "✗"
            print(f"  {status} Q({a},{b},{c}) = {Q_orig} → {name}({a2},{b2},{c2}): Q = {Q_new}")
    print()

# ============================================================
# §4. Berggren Descent
# ============================================================

def parent_hypotenuse(a: int, b: int, c: int) -> int:
    """Universal parent hypotenuse formula: c' = 3c - 2(a+b)."""
    return 3*c - 2*(a + b)

def find_parent(a: int, b: int, c: int) -> Tuple[Triple, str]:
    """Find the parent triple by trying all three inverse transforms.
    Returns (parent_triple, branch_name)."""
    for name, inv_fn in [("B1", inv_B1), ("B2", inv_B2), ("B3", inv_B3)]:
        pa, pb, pc = inv_fn(a, b, c)
        if pa > 0 and pb > 0 and pc > 0:
            return (pa, pb, pc), name
    # Fallback: try with absolute values
    for name, inv_fn in [("B1", inv_B1), ("B2", inv_B2), ("B3", inv_B3)]:
        pa, pb, pc = inv_fn(a, b, c)
        if abs(pa) > 0 and abs(pb) > 0 and pc > 0:
            return (abs(pa), abs(pb), pc), name
    raise ValueError(f"No valid parent found for ({a}, {b}, {c})")

def descent_to_root(a: int, b: int, c: int, verbose: bool = True) -> List[Triple]:
    """Descend from (a,b,c) to the root (3,4,5), recording the path."""
    path = [(a, b, c)]
    current = (a, b, c)
    step = 0
    while current not in [(3, 4, 5), (4, 3, 5)]:
        step += 1
        parent, branch = find_parent(*current)
        if verbose:
            print(f"  Step {step}: ({current[0]}, {current[1]}, {current[2]}) "
                  f"→ ({parent[0]}, {parent[1]}, {parent[2]}) via {branch}⁻¹  "
                  f"[c' = {parent[2]}, formula: {parent_hypotenuse(*current)}]")
        # Normalize: ensure a <= b
        if parent[0] > parent[1]:
            parent = (parent[1], parent[0], parent[2])
        current = parent
        path.append(current)
        if step > 1000:
            print("  WARNING: Exceeded 1000 steps, aborting")
            break
    return path

def demo_descent():
    """Demonstrate descent for several triples."""
    print("=" * 60)
    print("BERGGREN DESCENT TO ROOT (3,4,5)")
    print("=" * 60)
    test_triples = [
        (5, 12, 13),
        (8, 15, 17),
        (20, 21, 29),
        (9, 40, 41),
        (28, 45, 53),
        (119, 120, 169),
    ]
    for a, b, c in test_triples:
        assert a**2 + b**2 == c**2, f"Not a Pythagorean triple: ({a},{b},{c})"
        print(f"\nDescending from ({a}, {b}, {c}):")
        path = descent_to_root(a, b, c)
        print(f"  Total depth: {len(path) - 1}")
    print()

# ============================================================
# §5. Forward Tree Generation
# ============================================================

def generate_tree(depth: int) -> List[Tuple[Triple, int]]:
    """Generate all PPTs up to given depth, returning (triple, depth) pairs."""
    result = [((3, 4, 5), 0)]
    frontier = [(3, 4, 5)]
    for d in range(depth):
        new_frontier = []
        for a, b, c in frontier:
            for transform in [fwd_B1, fwd_B2, fwd_B3]:
                child = transform(a, b, c)
                result.append((child, d + 1))
                new_frontier.append(child)
        frontier = new_frontier
    return result

def demo_tree_generation():
    """Show the first few levels of the Berggren tree."""
    print("=" * 60)
    print("BERGGREN TREE (first 3 levels)")
    print("=" * 60)
    tree = generate_tree(3)
    for triple, depth in tree:
        a, b, c = triple
        indent = "  " * depth
        verify = "✓" if a**2 + b**2 == c**2 else "✗"
        print(f"  {indent}[d={depth}] ({a:>4}, {b:>4}, {c:>4})  {verify}")
    print(f"\n  Total triples at depth ≤ 3: {len(tree)}")
    print(f"  Expected: 1 + 3 + 9 + 27 = {1 + 3 + 9 + 27}")
    print()

# ============================================================
# §6. Pell Recurrence on B2-Branch
# ============================================================

def demo_pell_recurrence():
    """Demonstrate the Pell recurrence c'' = 6c' - c along B2-branch."""
    print("=" * 60)
    print("PELL RECURRENCE: B2-BRANCH HYPOTENUSES")
    print("=" * 60)
    a, b, c = 3, 4, 5
    hypotenuses = [c]
    for _ in range(8):
        a, b, c = fwd_B2(a, b, c)
        hypotenuses.append(c)

    print("  Hypotenuse sequence:", hypotenuses)
    print("\n  Verifying c'' = 6c' - c:")
    for i in range(2, len(hypotenuses)):
        predicted = 6 * hypotenuses[i-1] - hypotenuses[i-2]
        actual = hypotenuses[i]
        status = "✓" if predicted == actual else "✗"
        print(f"    {status} c_{i} = 6·{hypotenuses[i-1]} - {hypotenuses[i-2]} = {predicted} "
              f"(actual: {actual})")

    print("\n  Ratios c_{n+1}/c_n (should → 3 + 2√2 ≈ 5.828...):")
    for i in range(1, len(hypotenuses)):
        ratio = hypotenuses[i] / hypotenuses[i-1]
        print(f"    c_{i}/c_{i-1} = {ratio:.6f}")
    print(f"  Limit: 3 + 2√2 = {3 + 2*math.sqrt(2):.6f}")
    print()

# ============================================================
# §7. Inside-Out Factoring Demo
# ============================================================

def iof_depth1(N: int) -> Optional[Tuple[int, int]]:
    """Attempt IOF at depth 1: solve 5N²-8Nu+5u²-20N-20u-25=0 for integer u."""
    # Quadratic in u: 5u² - (8N+20)u + (5N²-20N-25) = 0
    A = 5
    B = -(8*N + 20)
    C = 5*N**2 - 20*N - 25
    disc = B**2 - 4*A*C
    if disc < 0:
        return None
    sqrt_disc = int(math.isqrt(disc))
    if sqrt_disc * sqrt_disc != disc:
        return None
    for sign in [1, -1]:
        u_num = -B + sign * sqrt_disc
        if u_num % (2*A) == 0:
            u = u_num // (2*A)
            h_sq = N**2 + u**2
            h = int(math.isqrt(h_sq))
            if h*h == h_sq:
                g = math.gcd(abs(h - u), N)
                if 1 < g < N:
                    return (g, N // g)
    return None

def demo_iof():
    """Demonstrate Inside-Out Factoring."""
    print("=" * 60)
    print("INSIDE-OUT FACTORING (IOF) DEMO")
    print("=" * 60)
    composites = [15, 21, 35, 77, 91, 143, 221, 323, 437, 667, 899]
    for N in composites:
        result = iof_depth1(N)
        if result:
            p, q = result
            print(f"  ✓ N = {N:>4} = {p} × {q} (factored at depth 1)")
        else:
            # Show what the discriminant is
            disc = (8*N+20)**2 - 4*5*(5*N**2 - 20*N - 25)
            print(f"  · N = {N:>4}: depth 1 discriminant = {disc} "
                  f"({'perfect square' if disc >= 0 and int(math.isqrt(disc))**2 == disc else 'not perfect square'})")
    print()

# ============================================================
# §8. Pythagorean Quadruples
# ============================================================

def lebesgue_quad(m: int, n: int, p: int, q: int) -> Tuple[int, int, int, int]:
    """Lebesgue parametrization of Pythagorean quadruples."""
    a = m**2 + n**2 - p**2 - q**2
    b = 2*(m*q + n*p)
    c = 2*(n*q - m*p)
    d = m**2 + n**2 + p**2 + q**2
    return (a, b, c, d)

def demo_quadruples():
    """Demonstrate Pythagorean quadruple generation."""
    print("=" * 60)
    print("PYTHAGOREAN QUADRUPLES (Lebesgue parametrization)")
    print("=" * 60)
    params = [
        (1, 1, 0, 0), (1, 1, 1, 0), (2, 1, 0, 0),
        (2, 1, 1, 0), (2, 1, 1, 1), (3, 1, 1, 0),
        (2, 2, 1, 0), (3, 2, 1, 0), (3, 1, 1, 1),
    ]
    for m, n, p, q in params:
        a, b, c, d = lebesgue_quad(m, n, p, q)
        verify = "✓" if a**2 + b**2 + c**2 == d**2 else "✗"
        print(f"  {verify} L({m},{n},{p},{q}) = ({a:>3}, {b:>3}, {c:>3}, {d:>3})  "
              f"[{a}² + {b}² + {c}² = {a**2+b**2+c**2} = {d}² = {d**2}]")
    print()

# ============================================================
# §9. Brahmagupta-Fibonacci Identity
# ============================================================

def demo_brahmagupta():
    """Demonstrate the multiplicativity of sum-of-two-squares."""
    print("=" * 60)
    print("BRAHMAGUPTA-FIBONACCI IDENTITY")
    print("=" * 60)
    examples = [(1,2, 3,4), (2,3, 5,7), (1,1, 1,1), (3,4, 5,12)]
    for a, b, c, d in examples:
        lhs = (a**2 + b**2) * (c**2 + d**2)
        x = a*c - b*d
        y = a*d + b*c
        rhs = x**2 + y**2
        status = "✓" if lhs == rhs else "✗"
        print(f"  {status} ({a}²+{b}²)({c}²+{d}²) = {lhs} = {x}²+{y}² = {rhs}")
    print()

# ============================================================
# §10. Statistics
# ============================================================

def demo_statistics():
    """Compute statistics about the Berggren tree."""
    print("=" * 60)
    print("BERGGREN TREE STATISTICS")
    print("=" * 60)
    tree = generate_tree(5)
    hyps = [t[2] for t, _ in tree]
    print(f"  Triples at depth ≤ 5: {len(tree)}")
    print(f"  Min hypotenuse: {min(hyps)}")
    print(f"  Max hypotenuse: {max(hyps)}")
    print(f"  Mean hypotenuse: {sum(hyps)/len(hyps):.1f}")

    # Verify all are Pythagorean
    all_pyth = all(a**2 + b**2 == c**2 for (a, b, c), _ in tree)
    print(f"  All Pythagorean: {'✓' if all_pyth else '✗'}")

    # Check uniqueness (no duplicates after normalizing)
    normalized = set()
    for (a, b, c), _ in tree:
        normalized.add((min(abs(a), abs(b)), max(abs(a), abs(b)), abs(c)))
    print(f"  Unique triples: {len(normalized)} (of {len(tree)} generated)")

    # Lorentz form check
    all_null = all(lorentz_form(a, b, c) == 0 for (a, b, c), _ in tree)
    print(f"  All on null cone: {'✓' if all_null else '✗'}")
    print()

# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     BERGGREN DESCENT: Pythagorean Triple Tree Demo      ║")
    print("║                                                          ║")
    print("║  Lorentz Groups · Pell Recurrences · Inside-Out Factor  ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    verify_lorentz_preservation()
    demo_descent()
    demo_tree_generation()
    demo_pell_recurrence()
    demo_iof()
    demo_quadruples()
    demo_brahmagupta()
    demo_statistics()

    print("=" * 60)
    print("All demos complete.")
    print("=" * 60)
