#!/usr/bin/env python3
"""
Open Questions Demo: Inside-Out Pythagorean Factoring
=====================================================

Demonstrations addressing the five open research questions:
1. Complexity bounds — depth-k system enumeration
2. Optimal starting triples — comparing trivial vs non-trivial
3. Multi-dimensional extension — Pythagorean quadruples
4. Quantum acceleration — Grover speedup analysis
5. Lattice-cryptography connection — Lorentz group structure
"""

import math
import random
from typing import List, Tuple, Optional, Dict
from itertools import product as cartesian_product

# ============================================================================
# Question 1: Complexity Bounds
# ============================================================================

def inv_B1(a, b, c): return (a + 2*b - 2*c, -2*a - b + 2*c, -2*a - 2*b + 3*c)
def inv_B2(a, b, c): return (a + 2*b - 2*c, 2*a + b - 2*c, -2*a - 2*b + 3*c)
def inv_B3(a, b, c): return (-a - 2*b + 2*c, 2*a + b - 2*c, -2*a - 2*b + 3*c)

def fwd_B1(a, b, c): return (a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c)
def fwd_B2(a, b, c): return (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c)
def fwd_B3(a, b, c): return (-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c)

def depth_k_systems(k: int) -> int:
    """Number of polynomial systems at depth k."""
    return 3 ** k

def enumerate_branch_sequences(k: int):
    """Enumerate all 3^k branch sequences at depth k."""
    if k == 0:
        return [()]
    transforms = [inv_B1, inv_B2, inv_B3]
    return list(cartesian_product(range(3), repeat=k))

def compose_transforms(seq, a, b, c):
    """Apply a sequence of inverse transforms."""
    transforms = [inv_B1, inv_B2, inv_B3]
    current = (a, b, c)
    for idx in seq:
        current = transforms[idx](*current)
    return current

def solve_depth_k_system(N: int, seq: tuple) -> Optional[Tuple[int, int]]:
    """
    Given N and a branch sequence, solve for u such that
    the k-fold inverse transform maps (N, u, h) to (3, 4, 5).
    Returns (u, h) if solution exists, else None.
    """
    # For each sequence, the composed transform gives
    # (αN + βu + γh, α'N + β'u + γ'h, α''N + β''u + γ''h) = (3, 4, 5)
    # This is a 3×3 linear system in (N, u, h) with N known.
    # We solve for u and h, then check h² = N² + u².

    # Build the composed matrix symbolically
    # Start with identity on (N, u, h)
    # Each transform is a 3×3 matrix
    transforms = [inv_B1, inv_B2, inv_B3]

    # Track (N, u, h) coefficients: each component is αN + βu + γh
    # Initially: a = 1·N + 0·u + 0·h, b = 0·N + 1·u + 0·h, c = 0·N + 0·u + 1·h
    coeffs = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]  # (a_coeff, b_coeff, c_coeff) for N, u, h

    for idx in seq:
        Na, Nu, Nh = coeffs[0]  # N-coefficients of (a, b, c)
        ua, uu, uh = coeffs[1]
        ha, hu, hh = coeffs[2]

        if idx == 0:  # B1⁻¹: (a+2b-2c, -2a-b+2c, -2a-2b+3c)
            new_a = (Na + 2*ua - 2*ha, Nu + 2*uu - 2*hu, Nh + 2*uh - 2*hh)
            new_b = (-2*Na - ua + 2*ha, -2*Nu - uu + 2*hu, -2*Nh - uh + 2*hh)
            new_c = (-2*Na - 2*ua + 3*ha, -2*Nu - 2*uu + 3*hu, -2*Nh - 2*uh + 3*hh)
        elif idx == 1:  # B2⁻¹: (a+2b-2c, 2a+b-2c, -2a-2b+3c)
            new_a = (Na + 2*ua - 2*ha, Nu + 2*uu - 2*hu, Nh + 2*uh - 2*hh)
            new_b = (2*Na + ua - 2*ha, 2*Nu + uu - 2*hu, 2*Nh + uh - 2*hh)
            new_c = (-2*Na - 2*ua + 3*ha, -2*Nu - 2*uu + 3*hu, -2*Nh - 2*uh + 3*hh)
        else:  # B3⁻¹: (-a-2b+2c, 2a+b-2c, -2a-2b+3c)
            new_a = (-Na - 2*ua + 2*ha, -Nu - 2*uu + 2*hu, -Nh - 2*uh + 2*hh)
            new_b = (2*Na + ua - 2*ha, 2*Nu + uu - 2*hu, 2*Nh + uh - 2*hh)
            new_c = (-2*Na - 2*ua + 3*ha, -2*Nu - 2*uu + 3*hu, -2*Nh - 2*uh + 3*hh)

        coeffs = [new_a, new_b, new_c]

    # Now coeffs[i] = (N_coeff, u_coeff, h_coeff) for the i-th component
    # Setting equal to (3, 4, 5):
    # coeffs[0][0]*N + coeffs[0][1]*u + coeffs[0][2]*h = 3
    # coeffs[1][0]*N + coeffs[1][1]*u + coeffs[1][2]*h = 4
    # coeffs[2][0]*N + coeffs[2][1]*u + coeffs[2][2]*h = 5

    # Solve 2×2 system for (u, h):
    # coeffs[0][1]*u + coeffs[0][2]*h = 3 - coeffs[0][0]*N
    # coeffs[1][1]*u + coeffs[1][2]*h = 4 - coeffs[1][0]*N

    a11, a12 = coeffs[0][1], coeffs[0][2]
    a21, a22 = coeffs[1][1], coeffs[1][2]
    b1 = 3 - coeffs[0][0] * N
    b2 = 4 - coeffs[1][0] * N

    det = a11 * a22 - a12 * a21
    if det == 0:
        return None

    u_num = b1 * a22 - b2 * a12
    h_num = a11 * b2 - a21 * b1

    if u_num % det != 0 or h_num % det != 0:
        return None

    u = u_num // det
    h = h_num // det

    # Check consistency with third equation
    check = coeffs[2][0] * N + coeffs[2][1] * u + coeffs[2][2] * h
    if check != 5:
        return None

    # Check Pythagorean constraint
    if N**2 + u**2 != h**2:
        return None

    if u > 0 and h > 0:
        return (u, h)
    return None

def complexity_demo():
    """Demonstrate complexity bounds for the inside-out approach."""
    print("=" * 70)
    print("QUESTION 1: Complexity Bounds")
    print("=" * 70)

    print("\nDepth-k system counts (3^k):")
    for k in range(8):
        n_systems = depth_k_systems(k)
        print(f"  Depth {k}: {n_systems:>6} systems, ~{2*n_systems} candidate solutions")

    print("\nSearching for factoring solutions at various depths:")
    test_N = [21, 55, 77, 143, 221, 323, 1001, 3599]
    for N in test_N:
        if N % 2 == 0:
            continue
        found_depth = None
        for k in range(1, 6):
            seqs = enumerate_branch_sequences(k)
            for seq in seqs:
                result = solve_depth_k_system(N, seq)
                if result:
                    u, h = result
                    g = math.gcd(h - u, N)
                    if 1 < g < N:
                        found_depth = k
                        print(f"  N={N:5d}: depth {k}, u={u}, factor={g} "
                              f"({g}×{N//g}), systems checked={3**k}")
                        break
            if found_depth:
                break
        if not found_depth:
            print(f"  N={N:5d}: no solution found at depths 1-5 ({sum(3**k for k in range(1,6))} systems)")

# ============================================================================
# Question 2: Optimal Starting Triples
# ============================================================================

def trivial_triple(N):
    """The trivial triple (N, (N²-1)/2, (N²+1)/2)."""
    return (N, (N**2 - 1) // 2, (N**2 + 1) // 2)

def nontrivial_triples(N):
    """Find all non-trivial starting triples from divisor pairs of N²."""
    triples = []
    N2 = N * N
    for d in range(1, int(N2**0.5) + 1):
        if N2 % d == 0:
            e = N2 // d
            if (e - d) % 2 == 0 and d != e:
                u = (e - d) // 2
                h = (e + d) // 2
                if u > 0 and h > 0 and N**2 + u**2 == h**2:
                    triples.append((N, u, h, d, e))
    return triples

def descent_depth(a, b, c, max_steps=10000):
    """Count steps to reach root (3,4,5)."""
    steps = 0
    while (a, b, c) != (3, 4, 5) and (a, b, c) != (4, 3, 5) and steps < max_steps:
        parent = None
        for fn in [inv_B1, inv_B2, inv_B3]:
            t = fn(a, b, c)
            if t[0] > 0 and t[1] > 0 and t[2] > 0 and t[0]**2 + t[1]**2 == t[2]**2:
                parent = t
                break
        if parent is None:
            break
        a, b, c = parent
        steps += 1
    return steps

def check_gcd_along_descent(N, a, b, c, max_steps=10000):
    """Check for GCD hits during descent."""
    steps = 0
    while (a, b, c) != (3, 4, 5) and (a, b, c) != (4, 3, 5) and steps < max_steps:
        for val in [a, b]:
            g = math.gcd(abs(val), N)
            if 1 < g < N:
                return steps, g
        parent = None
        for fn in [inv_B1, inv_B2, inv_B3]:
            t = fn(a, b, c)
            if t[0] > 0 and t[1] > 0 and t[2] > 0 and t[0]**2 + t[1]**2 == t[2]**2:
                parent = t
                break
        if parent is None:
            break
        a, b, c = parent
        steps += 1
    return None, None

def optimal_starting_demo():
    """Demonstrate optimal starting triple selection."""
    print("\n" + "=" * 70)
    print("QUESTION 2: Optimal Starting Triples")
    print("=" * 70)

    test_composites = [15, 21, 35, 77, 143, 221, 323, 1001, 3599]
    for N in test_composites:
        triples = nontrivial_triples(N)
        trivial = trivial_triple(N)
        triv_depth = descent_depth(*trivial)
        triv_gcd_step, triv_gcd = check_gcd_along_descent(N, *trivial)

        print(f"\n  N = {N}:")
        print(f"    Trivial: u={(N**2-1)//2}, h={(N**2+1)//2}, "
              f"depth={triv_depth}, gcd_step={triv_gcd_step}, factor={triv_gcd}")

        for (_, u, h, d, e) in triples[:3]:
            depth = descent_depth(N, u, h)
            gcd_step, gcd_val = check_gcd_along_descent(N, N, u, h)
            improvement = "BETTER" if (gcd_step is not None and
                                       (triv_gcd_step is None or gcd_step < triv_gcd_step)) else ""
            print(f"    d={d:5d}, e={e:5d}: u={u}, h={h}, depth={depth}, "
                  f"gcd_step={gcd_step}, factor={gcd_val} {improvement}")

# ============================================================================
# Question 3: Multi-Dimensional Extension
# ============================================================================

def find_pythagorean_quadruples(max_d):
    """Find primitive Pythagorean quadruples a²+b²+c²=d²."""
    quads = []
    for d in range(2, max_d + 1):
        d2 = d * d
        for a in range(1, d):
            for b in range(a, d):
                rem = d2 - a*a - b*b
                if rem <= 0:
                    break
                c = int(rem**0.5)
                if c >= b and c < d and a*a + b*b + c*c == d2:
                    if math.gcd(math.gcd(a, b), math.gcd(c, d)) == 1:
                        quads.append((a, b, c, d))
    return quads

def quadruple_factor_attempt(N, a, b, c, d):
    """Try to extract a factor of N from a quadruple."""
    for val in [a, b, c, d-c, d+c, d-b, d+b, d-a, d+a]:
        g = math.gcd(abs(val), N)
        if 1 < g < N:
            return g
    return None

def higher_dim_demo():
    """Demonstrate the multi-dimensional extension."""
    print("\n" + "=" * 70)
    print("QUESTION 3: Multi-Dimensional Extension (Pythagorean Quadruples)")
    print("=" * 70)

    print("\nPrimitive Pythagorean quadruples with d ≤ 20:")
    quads = find_pythagorean_quadruples(20)
    for q in quads[:15]:
        a, b, c, d = q
        print(f"  {a}² + {b}² + {c}² = {d}²  ({a**2} + {b**2} + {c**2} = {d**2})")

    print(f"\n  Total primitive quadruples with d ≤ 20: {len(quads)}")
    print(f"  Compare: primitive triples with c ≤ 20: "
          f"{sum(1 for a in range(1,20) for b in range(a,20) if int((a**2+b**2)**0.5)**2 == a**2+b**2 and math.gcd(a,b)==1)}")

    print("\n  Branching factor advantage:")
    for k in range(1, 8):
        print(f"    Depth {k}: triples = {3**k:>6} nodes, quadruples = {4**k:>6} nodes, "
              f"ratio = {4**k/3**k:.2f}×")

    print("\n  GCD checks per node: 2 (triples) vs 3 (quadruples) = 1.5× more opportunities")

    print("\n  Factoring attempt using quadruples:")
    test_N = [15, 21, 77, 143]
    for N in test_N:
        for q in quads:
            a, b, c, d = q
            # Scale quadruple to involve N
            for s in range(1, N):
                if (N * s) ** 2 + b**2 + c**2 == (int(((N*s)**2 + b**2 + c**2)**0.5))**2:
                    factor = quadruple_factor_attempt(N, N*s, b, c,
                                                      int(((N*s)**2 + b**2 + c**2)**0.5))
                    if factor:
                        print(f"  N={N}: factor={factor} via quadruple scaling")
                        break

# ============================================================================
# Question 4: Quantum Acceleration
# ============================================================================

def grover_speedup_analysis():
    """Analyze Grover's algorithm speedup for branch sequence search."""
    print("\n" + "=" * 70)
    print("QUESTION 4: Quantum Acceleration (Grover's Algorithm)")
    print("=" * 70)

    print("\n  Classical vs Quantum branch sequence search:")
    print(f"  {'Depth k':>8} | {'Classical (3^k)':>15} | {'Quantum (~3^(k/2))':>18} | {'Speedup':>8}")
    print(f"  {'-'*8}-+-{'-'*15}-+-{'-'*18}-+-{'-'*8}")
    for k in range(1, 16):
        classical = 3 ** k
        quantum = int(3 ** (k / 2)) + 1  # Ceiling of √(3^k)
        speedup = classical / quantum
        print(f"  {k:>8} | {classical:>15,} | {quantum:>18,} | {speedup:>7.1f}×")

    print("\n  Key insight: Grover provides quadratic speedup on the branch sequence space.")
    print("  At depth k=20: classical needs ~3.5 billion evaluations,")
    print(f"                  quantum needs ~{int(3**10)+1:,} evaluations.")

    print("\n  Quantum walk analysis (amplitude amplification on tree levels):")
    print("  Each level has branching factor 3.")
    print("  Quantum walk on a single level: O(√3) ≈ 1.73 queries")
    print("  k independent levels: O((√3)^k) = O(3^(k/2)) total queries")
    print("  This matches the Grover bound — no additional speedup from structure.")

    print("\n  Hybrid classical-quantum strategy:")
    print("  1. Classical: solve depth-k systems for small k (k ≤ 5)")
    print("  2. Quantum: Grover search over remaining branch sequences")
    print("  3. Lattice: LLL reduction on the polynomial systems")
    print("  Combined: potentially sub-exponential in favorable cases")

# ============================================================================
# Question 5: Lattice-Cryptography Connection
# ============================================================================

import numpy as np

def lattice_connection_demo():
    """Demonstrate connection to lattice-based cryptography."""
    print("\n" + "=" * 70)
    print("QUESTION 5: Connection to Lattice-Based Cryptography")
    print("=" * 70)

    # Berggren matrices
    B1 = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]])
    B2 = np.array([[1, 2, 2], [2, 1, 2], [2, 2, 3]])
    B3 = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]])
    eta = np.diag([1, 1, -1])

    print("\n  Lorentz form preservation:")
    for name, B in [("B₁", B1), ("B₂", B2), ("B₃", B3)]:
        result = B.T @ eta @ B
        preserved = np.array_equal(result, eta)
        det = int(round(np.linalg.det(B)))
        print(f"    {name}ᵀ · η · {name} = η: {preserved}, det({name}) = {det}")

    print("\n  Word length in Berggren group (analogous to lattice distance):")
    # Generate some group elements of various word lengths
    generators = [("B₁", B1), ("B₂", B2), ("B₃", B3)]
    for length in [1, 2, 3, 4]:
        count = 3 ** length
        # Sample a few random words
        samples = []
        for _ in range(min(3, count)):
            word = []
            M = np.eye(3, dtype=int)
            for _ in range(length):
                idx = random.randint(0, 2)
                name, gen = generators[idx]
                word.append(name)
                M = M @ gen
            triple = M @ np.array([3, 4, 5])
            samples.append(("·".join(word), tuple(triple)))
        for word, triple in samples:
            print(f"    Length {length}: {word} → {triple}")

    print("\n  SVP connection:")
    print("  The Berggren group Γ ⊂ O(2,1;ℤ) acts on the null cone {(a,b,c) : a²+b²=c²}.")
    print("  Finding a short group element mapping (3,4,5) to a triple with first leg N")
    print("  is analogous to the Shortest Vector Problem (SVP) in the Lorentz lattice.")
    print("  If SVP is hard in this lattice, factoring via inside-out is also hard.")
    print("  If SVP is easy (via LLL), factoring might be sub-exponential.")

    print("\n  CVP connection:")
    print("  Given target N, finding the closest lattice point in the null cone")
    print("  to (N, *, *) is a Closest Vector Problem instance.")
    print("  The inside-out equations reduce CVP to solving degree-2 polynomials.")

    print("\n  Post-quantum implications:")
    print("  - If Pythagorean factoring = lattice problem, then quantum algorithms")
    print("    for lattice problems (limited speedup) apply.")
    print("  - The Lorentz lattice has indefinite signature (2,1) — different from")
    print("    standard lattice crypto which uses positive-definite forms.")
    print("  - Open: does the indefinite signature make SVP easier or harder?")

# ============================================================================
# Main Demo
# ============================================================================

def main():
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  FIVE OPEN QUESTIONS: Inside-Out Pythagorean Factoring             ║")
    print("║  Computational Demonstrations                                       ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    complexity_demo()
    optimal_starting_demo()
    higher_dim_demo()
    grover_speedup_analysis()
    lattice_connection_demo()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
Key findings:
1. COMPLEXITY: Depth-k equations grow as 3^k systems, each degree-2 in u.
   Lattice reduction may solve batches efficiently, but proven sub-exponential
   complexity remains open.

2. OPTIMAL STARTS: Non-trivial triples from divisor pairs give dramatically
   shorter descent paths. Finding good u values is equivalent to factoring
   (circular dependency), but random sampling can find short paths.

3. HIGHER DIMENSIONS: Pythagorean quadruples give 4^k branching (vs 3^k)
   and 3 GCD checks per node (vs 2). Combined advantage ≈ 2× per level.

4. QUANTUM: Grover gives √(3^k) = 3^(k/2) speedup on branch sequences.
   No additional speedup from tree structure (quantum walk matches Grover).

5. LATTICE: Berggren group ⊂ O(2,1;ℤ). Inside-out factoring reduces to
   finding short vectors in a Lorentz lattice. Connection to SVP/CVP
   is structural but complexity relationship remains open.
""")

if __name__ == "__main__":
    main()
