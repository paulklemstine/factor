#!/usr/bin/env python3
"""
Inside-Out Root Search Factoring via Pythagorean Triple Trees
=============================================================

A Python implementation demonstrating the inside-out factoring method.

The core idea: Given an odd composite N, form the parametric triple (N, u, h)
where h² = N² + u². Apply inverse Berggren transforms (parent maps) to navigate
the Pythagorean triple tree toward the root (3,4,5). At each node, compute
gcd(leg, N) to detect nontrivial factors.

The "inside-out" insight: instead of searching the tree top-down (exponential),
write the root-reachability condition as polynomial equations in u and solve.
"""

import math
from typing import Optional, Tuple, List

# ============================================================================
# Section 1: The Three Inverse Berggren Transforms
# ============================================================================

def inv_B1(a: int, b: int, c: int) -> Tuple[int, int, int]:
    """Inverse Berggren transform B₁⁻¹."""
    return (a + 2*b - 2*c, -2*a - b + 2*c, -2*a - 2*b + 3*c)

def inv_B2(a: int, b: int, c: int) -> Tuple[int, int, int]:
    """Inverse Berggren transform B₂⁻¹."""
    return (a + 2*b - 2*c, 2*a + b - 2*c, -2*a - 2*b + 3*c)

def inv_B3(a: int, b: int, c: int) -> Tuple[int, int, int]:
    """Inverse Berggren transform B₃⁻¹."""
    return (-a - 2*b + 2*c, 2*a + b - 2*c, -2*a - 2*b + 3*c)

# ============================================================================
# Section 2: Parent Selection (Unique Valid Inverse)
# ============================================================================

def find_parent(a: int, b: int, c: int) -> Tuple[Tuple[int, int, int], str]:
    """
    Find the unique parent of a primitive Pythagorean triple (a, b, c).
    
    Returns the parent triple and the branch name.
    Exactly one of the three inverse transforms produces all-positive components.
    """
    candidates = [
        (inv_B1(a, b, c), "B1"),
        (inv_B2(a, b, c), "B2"),
        (inv_B3(a, b, c), "B3"),
    ]
    
    for (triple, name) in candidates:
        # For non-primitive or scaled triples, we check if the parent has
        # all positive entries and satisfies the Pythagorean equation
        a2, b2, c2 = triple
        if a2 > 0 and b2 > 0 and c2 > 0:
            assert a2**2 + b2**2 == c2**2, f"Parent doesn't satisfy Pythagorean: {triple}"
            return (triple, name)
    
    # If no positive parent found, try with absolute values
    for (triple, name) in candidates:
        a2, b2, c2 = abs(triple[0]), abs(triple[1]), abs(triple[2])
        if a2 > 0 and b2 > 0 and c2 > 0 and a2**2 + b2**2 == c2**2:
            return ((a2, b2, c2), name + "*")
    
    return ((a, b, c), "ROOT")

# ============================================================================
# Section 3: Descent to Root
# ============================================================================

def descend_to_root(a: int, b: int, c: int, max_steps: int = 1000) -> List[Tuple[int, int, int]]:
    """
    Descend from (a, b, c) to the root (3, 4, 5) using parent transforms.
    Returns the full path.
    """
    path = [(a, b, c)]
    current = (a, b, c)
    
    for _ in range(max_steps):
        if current == (3, 4, 5) or current == (4, 3, 5):
            break
        parent, branch = find_parent(*current)
        if parent == current:
            break
        path.append(parent)
        current = parent
    
    return path

# ============================================================================
# Section 4: The Trivial Triple
# ============================================================================

def trivial_triple(N: int) -> Tuple[int, int, int]:
    """
    Construct the trivial Pythagorean triple for odd N:
    (N, (N²-1)/2, (N²+1)/2)
    """
    assert N % 2 == 1 and N > 1
    b = (N**2 - 1) // 2
    c = (N**2 + 1) // 2
    assert N**2 + b**2 == c**2
    return (N, b, c)

# ============================================================================
# Section 5: Factor Extraction via GCD
# ============================================================================

def try_factor_from_triple(a: int, b: int, c: int, N: int) -> Optional[int]:
    """
    Try to extract a factor of N from a Pythagorean triple (a, b, c).
    Checks gcd of various quantities with N.
    """
    for val in [a, b, c-b, c+b, a-b, a+b, 2*b-2*c, 2*a-2*c]:
        g = math.gcd(abs(val), N)
        if 1 < g < N:
            return g
    return None

# ============================================================================
# Section 6: Inside-Out Factoring Algorithm
# ============================================================================

def inside_out_factor(N: int, verbose: bool = True) -> Optional[int]:
    """
    Factor N using the inside-out root search method.
    
    Algorithm:
    1. Construct the trivial triple (N, (N²-1)/2, (N²+1)/2)
    2. Descend toward root (3,4,5) via parent transforms
    3. At each node, check gcd(leg, N) for nontrivial factors
    4. Additionally, check the difference-of-squares: (c-b)(c+b) = a²
    """
    if N % 2 == 0:
        return 2
    if N < 3:
        return None
    
    # Step 1: Construct trivial triple
    a, b, c = trivial_triple(N)
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"INSIDE-OUT FACTORING: N = {N}")
        print(f"{'='*60}")
        print(f"Trivial triple: ({a}, {b}, {c})")
        print(f"Verify: {a}² + {b}² = {a**2 + b**2} = {c}² = {c**2}")
        print(f"c - b = {c - b} (always 1 for trivial triple)")
        print()
    
    # Step 2: Descend and check at each level
    current = (a, b, c)
    step = 0
    
    while current != (3, 4, 5) and current != (4, 3, 5) and step < 100:
        # Try factor extraction at current node
        factor = try_factor_from_triple(*current, N)
        if factor:
            if verbose:
                print(f"  Step {step}: FACTOR FOUND! gcd gives {factor}")
                print(f"  Triple: {current}")
                print(f"  N = {factor} × {N // factor}")
            return factor
        
        # Move to parent
        parent, branch = find_parent(*current)
        step += 1
        
        if verbose:
            print(f"  Step {step}: Branch {branch} → {parent}")
            if parent[2] > 0:
                print(f"    Hypotenuse: {current[2]} → {parent[2]} (decrease: {current[2] - parent[2]})")
        
        if parent == current:
            break
        current = parent
    
    # Final check at root
    factor = try_factor_from_triple(*current, N)
    if factor:
        if verbose:
            print(f"  At root: FACTOR FOUND! {factor}")
        return factor
    
    if verbose:
        print(f"\n  Reached root after {step} steps, no factor found via descent.")
    
    return None

# ============================================================================
# Section 7: The Root Equation Method (Inside-Out Quadratic)
# ============================================================================

def root_equation_factor(N: int, verbose: bool = True) -> Optional[int]:
    """
    Factor N using the inside-out root equation method.
    
    If (N, u, h) maps to (3,4,5) via B₂⁻¹, then:
    - u = N - 1
    - h = (4N + 3) / 3
    - The quadratic: 5N² - 8Nu - 20N + 5u² - 20u - 25 = 0
    
    For depth-1 paths via B₂⁻¹, this reduces to 2N(N-21) = 0,
    showing that N = 21 is the only composite reachable in one B₂⁻¹ step.
    
    For depth-2 and beyond, the equations become higher-degree polynomials
    in u, whose integer solutions correspond to valid factoring paths.
    """
    if verbose:
        print(f"\n{'='*60}")
        print(f"ROOT EQUATION METHOD: N = {N}")
        print(f"{'='*60}")
    
    # Depth 1: Check all three branches
    for branch_name, inv_fn in [("B1", inv_B1), ("B2", inv_B2), ("B3", inv_B3)]:
        # For (N, u, h) → (3, 4, 5), solve for u and h
        # From the hypotenuse equation: -2N - 2u + 3h = 5
        # From leg equations: depends on branch
        
        # For B₂⁻¹: N + 2u - 2h = 3 and 2N + u - 2h = 4
        # From these: u = N - 1, h = (4N+3)/3
        if branch_name == "B2":
            u = N - 1
            if (4*N + 3) % 3 == 0:
                h = (4*N + 3) // 3
                if N**2 + u**2 == h**2:
                    if verbose:
                        print(f"  Depth 1, {branch_name}: u={u}, h={h}")
                        print(f"  Triple: ({N}, {u}, {h})")
                    g = math.gcd(h - u, N)
                    if 1 < g < N:
                        if verbose:
                            print(f"  FACTOR: gcd(h-u, N) = gcd({h-u}, {N}) = {g}")
                            print(f"  N = {g} × {N // g}")
                        return g
        
        # For B₁⁻¹: N + 2u - 2h = 3 and -2N - u + 2h = 4
        # From these: u = 3N - 7, h = (4N - 5)/1... let me solve
        if branch_name == "B1":
            # N + 2u - 2h = 3  →  h = (N + 2u - 3)/2
            # -2N - u + 2h = 4  →  2h = 2N + u + 4  →  h = (2N + u + 4)/2
            # So N + 2u - 3 = 2N + u + 4  →  u = N + 7
            u = N + 7
            h_num = 2*N + u + 4
            if h_num % 2 == 0:
                h = h_num // 2
                if N**2 + u**2 == h**2:
                    if verbose:
                        print(f"  Depth 1, {branch_name}: u={u}, h={h}")
                    g = math.gcd(h - u, N)
                    if 1 < g < N:
                        if verbose:
                            print(f"  FACTOR: gcd(h-u, N) = gcd({h-u}, {N}) = {g}")
                        return g
        
        # For B₃⁻¹: -N - 2u + 2h = 3 and 2N + u - 2h = 4
        # From these: N + 2u - 2h = -3 and 2N + u - 2h = 4
        # Subtract: N - u = 7  →  u = N - 7
        if branch_name == "B3":
            u = N - 7
            if u > 0:
                h_num = 2*N + u - 4
                if h_num % 2 == 0 and h_num > 0:
                    h = h_num // 2
                    if N**2 + u**2 == h**2:
                        if verbose:
                            print(f"  Depth 1, {branch_name}: u={u}, h={h}")
                        g = math.gcd(h - u, N)
                        if 1 < g < N:
                            if verbose:
                                print(f"  FACTOR: gcd(h-u, N) = gcd({h-u}, {N}) = {g}")
                            return g
    
    if verbose:
        print("  No depth-1 solution found; would need depth ≥ 2.")
    
    return None

# ============================================================================
# Section 8: Grandparent Equations (Depth 2)
# ============================================================================

def grandparent_B2B2(a: int, b: int, c: int) -> Tuple[int, int, int]:
    """Compute the B₂⁻¹ ∘ B₂⁻¹ grandparent."""
    return (9*a + 8*b - 12*c, 8*a + 9*b - 12*c, -12*a - 12*b + 17*c)

def depth2_search(N: int, verbose: bool = True) -> Optional[int]:
    """
    Search for factors using depth-2 root equations.
    
    At depth 2, the grandparent maps (N, u, h) to (3, 4, 5):
    For B₂⁻¹ ∘ B₂⁻¹: (9N + 8u - 12h, 8N + 9u - 12h, -12N - 12u + 17h) = (3,4,5)
    
    This gives: 9N + 8u - 12h = 3, 8N + 9u - 12h = 4, -12N - 12u + 17h = 5
    Solving: u = N - 1, h = (17N + 12u + 5)/17... etc.
    """
    if verbose:
        print(f"\n  Depth-2 search for N = {N}")
    
    # For each of the 9 possible branch combinations
    inv_fns = [("B1", inv_B1), ("B2", inv_B2), ("B3", inv_B3)]
    
    for name1, fn1 in inv_fns:
        for name2, fn2 in inv_fns:
            # Compose: fn2(fn1(N, u, h)) = (3, 4, 5)
            # fn1(N, u, h) = (a', b', c') where a',b',c' are linear in N,u,h
            # Then fn2(a', b', c') = (3, 4, 5) gives 3 linear equations in N,u,h
            
            # Let's compute symbolically:
            # fn1 gives (α₁N + β₁u + γ₁h, α₂N + β₂u + γ₂h, α₃N + β₃u + γ₃h)
            # fn2 applied to that gives more linear combos
            # Setting equal to (3,4,5) gives 3 equations in 3 unknowns (N known, solve for u,h)
            
            # Just do it numerically: for each u from 1 to N, check if h is integer
            # This is O(N), but demonstrates the concept
            pass
    
    # Efficient version: solve the linear system directly
    # For B₂⁻¹ ∘ B₂⁻¹: we proved the grandparent is (9a+8b-12c, 8a+9b-12c, -12a-12b+17c)
    # Setting = (3,4,5): 9N + 8u - 12h = 3, 8N + 9u - 12h = 4, -12N - 12u + 17h = 5
    # From eq1 - eq2: N - u = -1 → u = N + 1
    # From eq3: h = (12N + 12u + 5) / 17 = (12N + 12(N+1) + 5) / 17 = (24N + 17) / 17
    
    u = N + 1
    if (24*N + 17) % 17 == 0:
        h = (24*N + 17) // 17
        if N**2 + u**2 == h**2:
            g = math.gcd(h - u, N)
            if verbose:
                print(f"    B₂∘B₂ depth-2: u={u}, h={h}, gcd(h-u,N)={g}")
            if 1 < g < N:
                return g
    
    return None

# ============================================================================
# Section 9: Combined Strategy
# ============================================================================

def factor_combined(N: int, verbose: bool = True) -> Optional[int]:
    """
    Combined factoring strategy using multiple approaches.
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"  COMBINED INSIDE-OUT FACTORING: N = {N}")
        print(f"{'='*70}")
    
    # Method 1: Root equation (depth 1)
    result = root_equation_factor(N, verbose=verbose)
    if result:
        return result
    
    # Method 2: Depth-2 equations
    result = depth2_search(N, verbose=verbose)
    if result:
        return result
    
    # Method 3: Full descent
    result = inside_out_factor(N, verbose=verbose)
    if result:
        return result
    
    # Method 4: Try different starting triples (m²-n², 2mn, m²+n²)
    if verbose:
        print("\n  Trying Euclid-parametric triples...")
    limit = min(int(N**0.5) + 10, 10000)
    for m in range(2, limit):
        for n in range(1, m):
            if math.gcd(m, n) == 1 and (m - n) % 2 == 1:
                a = m*m - n*n
                b = 2*m*n
                c = m*m + n*n
                # Check if this triple involves N
                g = math.gcd(a, N)
                if 1 < g < N:
                    if verbose:
                        print(f"    Found factor via (m,n)=({m},{n}): a={a}, gcd(a,N)={g}")
                    return g
                g = math.gcd(b, N)
                if 1 < g < N:
                    if verbose:
                        print(f"    Found factor via (m,n)=({m},{n}): b={b}, gcd(b,N)={g}")
                    return g
    
    return None

# ============================================================================
# Section 10: Demonstrations
# ============================================================================

def demo():
    """Run demonstrations of the inside-out factoring method."""
    
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║   INSIDE-OUT ROOT SEARCH FACTORING                         ║")
    print("║   Pythagorean Triple Tree Navigation                       ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    # Demo 1: Factor small composites
    print("\n" + "="*60)
    print("DEMO 1: Small Composites")
    print("="*60)
    
    test_numbers = [15, 21, 33, 35, 51, 77, 91, 143, 221, 323]
    for N in test_numbers:
        factor = inside_out_factor(N, verbose=False)
        if factor:
            print(f"  N = {N:5d} = {factor} × {N // factor}")
        else:
            print(f"  N = {N:5d}: no factor found via descent")
    
    # Demo 2: The special case N = 21
    print("\n" + "="*60)
    print("DEMO 2: N = 21 — The Depth-1 B₂ Case")
    print("="*60)
    print("21 = 3 × 7 is the unique composite reachable in one B₂⁻¹ step.")
    print("Triple: (21, 20, 29)")
    print("B₂⁻¹(21, 20, 29) = (3, 4, 5) ✓")
    print("h - u = 29 - 20 = 9, gcd(9, 21) = 3 → factor!")
    
    result = inv_B2(21, 20, 29)
    print(f"Verification: inv_B2(21, 20, 29) = {result}")
    
    # Demo 3: Descent path visualization
    print("\n" + "="*60)
    print("DEMO 3: Descent Path for N = 143 = 11 × 13")
    print("="*60)
    
    inside_out_factor(143, verbose=True)
    
    # Demo 4: Root equation method
    print("\n" + "="*60)
    print("DEMO 4: Root Equation Method")
    print("="*60)
    
    for N in [21, 33, 65, 77, 105]:
        root_equation_factor(N, verbose=True)
    
    # Demo 5: Grandparent formula verification
    print("\n" + "="*60)
    print("DEMO 5: Grandparent Formula Verification")
    print("="*60)
    
    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
    for (a, b, c) in triples:
        gp = grandparent_B2B2(a, b, c)
        direct = inv_B2(*inv_B2(a, b, c))
        print(f"  ({a},{b},{c}) → grandparent: {gp}")
        print(f"    Direct computation: {direct}")
        print(f"    Match: {gp == direct}")
        if gp[0] > 0 and gp[1] > 0 and gp[2] > 0:
            print(f"    Pythagorean: {gp[0]**2 + gp[1]**2 == gp[2]**2}")
    
    # Demo 6: Combined strategy on larger numbers
    print("\n" + "="*60)
    print("DEMO 6: Combined Strategy on Larger Composites")
    print("="*60)
    
    larger = [1001, 2021, 3599, 10001, 17389]
    for N in larger:
        factor = factor_combined(N, verbose=False)
        if factor:
            print(f"  N = {N:6d} = {factor} × {N // factor}")
        else:
            print(f"  N = {N:6d}: not factored")
    
    # Demo 7: The inside-out quadratic
    print("\n" + "="*60)
    print("DEMO 7: The Inside-Out Quadratic")
    print("="*60)
    print("For depth-1 via B₂⁻¹: 5N² - 8Nu - 20N + 5u² - 20u - 25 = 0")
    print("With u = N-1: reduces to 2N(N-21) = 0")
    print("So N = 21 is the unique solution!")
    for N in range(3, 50, 2):
        u = N - 1
        val = 5*N**2 - 8*N*u - 20*N + 5*u**2 - 20*u - 25
        if val == 0:
            print(f"  N = {N}: quadratic = 0 ✓  (h = {(4*N+3)//3})")

if __name__ == "__main__":
    demo()
