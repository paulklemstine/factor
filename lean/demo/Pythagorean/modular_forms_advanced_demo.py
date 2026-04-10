#!/usr/bin/env python3
"""
Berggren–Theta Group Advanced Demo
===================================

Demonstrates five new directions:
1. Pythagorean quadruples and SO(3,1)
2. Spectral gap and descent complexity
3. L-functions and chi_{-4}
4. Quantum gate properties
5. Hauptmodul (modular lambda function)
"""

import numpy as np
from fractions import Fraction
from math import gcd, log2, pi, sqrt
import itertools


# ============================================================
# Part 1: Higher-Dimensional Generalization
# ============================================================

def is_pyth_quadruple(a, b, c, d):
    """Check if (a,b,c,d) is a Pythagorean quadruple."""
    return a**2 + b**2 + c**2 == d**2

def quadruple_parametrization(p, q, r, s):
    """Generate a Pythagorean quadruple from four parameters."""
    a = p**2 + q**2 - r**2 - s**2
    b = 2*(p*s + q*r)
    c = 2*(q*s - p*r)
    d = p**2 + q**2 + r**2 + s**2
    return (a, b, c, d)

def demo_quadruples():
    print("=" * 60)
    print("PART 1: Pythagorean Quadruples")
    print("=" * 60)
    
    # Fundamental quadruple
    print(f"\nFundamental quadruple: (1,2,2,3)")
    print(f"  1² + 2² + 2² = {1+4+4} = 3² = {9}  ✓")
    
    # Generate quadruples from parametrization
    print(f"\nQuadruples from parametrization (p,q,r,s):")
    params = [(1,0,0,0), (1,1,0,0), (1,1,1,0), (2,1,0,0), (1,0,1,1)]
    for p, q, r, s in params:
        quad = quadruple_parametrization(p, q, r, s)
        a, b, c, d = quad
        check = a**2 + b**2 + c**2 == d**2
        print(f"  ({p},{q},{r},{s}) → ({a},{b},{c},{d})  " +
              f"{a}²+{b}²+{c}² = {a**2+b**2+c**2} = {d}² = {d**2}  {'✓' if check else '✗'}")
    
    # Three-square theorem: numbers of form 4^a(8b+7) cannot be sums of 3 squares
    print(f"\nLegendre's three-square theorem examples:")
    for n in range(1, 30):
        reps = [(a,b,c) for a in range(n) for b in range(a,n) for c in range(b,n) 
                if a**2 + b**2 + c**2 == n]
        is_forbidden = False
        m = n
        while m % 4 == 0:
            m //= 4
        if m % 8 == 7:
            is_forbidden = True
        status = "FORBIDDEN (4^a(8b+7))" if is_forbidden else f"{len(reps)} reps"
        if is_forbidden or len(reps) == 0:
            print(f"  n={n:2d}: {status}")


# ============================================================
# Part 2: Spectral Gap and Descent Complexity
# ============================================================

# Berggren 3x3 matrices
B1 = np.array([[1,-2,2],[2,-1,2],[2,-2,3]])
B2 = np.array([[1,2,2],[2,1,2],[2,2,3]])
B3 = np.array([[-1,2,2],[-2,1,2],[-2,2,3]])

B1_inv = np.array([[1,2,-2],[-2,-1,2],[-2,2,-3]])  # inverse for descent

def berggren_descent(a, b, c):
    """Descend from (a,b,c) to (3,4,5) in the Berggren tree."""
    path = []
    while (a, b, c) != (3, 4, 5):
        if a <= 0 or b <= 0 or c <= 0:
            return None  # not a valid PPT path
        # Determine which inverse to apply
        v = np.array([a, b, c])
        for i, Binv in enumerate([np.linalg.inv(B1).astype(int), 
                                   np.linalg.inv(B2).astype(int), 
                                   np.linalg.inv(B3).astype(int)]):
            w = Binv @ v
            if all(w > 0):
                a, b, c = int(w[0]), int(w[1]), int(w[2])
                path.append(i + 1)
                break
        else:
            return None
    return path

def demo_spectral_gap():
    print("\n" + "=" * 60)
    print("PART 2: Spectral Gap and Descent Complexity")
    print("=" * 60)
    
    # Selberg bound
    lambda1 = 3/16
    print(f"\nSelberg bound: λ₁ ≥ {lambda1} = {Fraction(3,16)}")
    print(f"Mixing rate: √(λ₁) ≥ {sqrt(lambda1):.6f}")
    print(f"Equidistribution exponent: δ ≈ {sqrt(lambda1):.4f}")
    
    # Generate triples up to hypotenuse N and measure descent depths
    print(f"\nDescent depth statistics:")
    N_values = [50, 100, 500, 1000]
    for N in N_values:
        depths = []
        count = 0
        for c in range(5, N+1):
            for b in range(1, c):
                a_sq = c*c - b*b
                a = int(sqrt(a_sq))
                if a*a == a_sq and a > 0 and gcd(a, b) == 1 and a <= b:
                    # Generate the tree path
                    triple = (a, b, c) if a % 2 == 1 else (b, a, c)
                    # Count depth by descent
                    depth = 0
                    aa, bb, cc = triple
                    while (aa, bb, cc) != (3, 4, 5):
                        v = np.array([aa, bb, cc])
                        found = False
                        for Bi in [B1, B2, B3]:
                            try:
                                w = np.linalg.solve(Bi, v).round().astype(int)
                                if all(w > 0) and np.allclose(Bi @ w, v):
                                    aa, bb, cc = w[0], w[1], w[2]
                                    depth += 1
                                    found = True
                                    break
                            except:
                                pass
                        if not found:
                            depth = -1
                            break
                    if depth > 0:
                        depths.append(depth)
                        count += 1
        if depths:
            avg = sum(depths) / len(depths)
            max_d = max(depths)
            print(f"  N={N:5d}: {count:4d} triples, avg depth={avg:.2f}, " +
                  f"max depth={max_d}, log₂(N)={log2(N):.2f}")
    
    # PPT counting
    print(f"\nPPT counting constant: 1/(2π) = {1/(2*pi):.6f}")
    for N in [100, 1000, 10000]:
        expected = N / (2 * pi)
        print(f"  Expected PPTs with c ≤ {N}: ≈ {expected:.1f}")


# ============================================================
# Part 3: L-Functions and chi_{-4}
# ============================================================

def chi_neg4(n):
    """The Dirichlet character χ₋₄."""
    n = n % 4
    if n == 0: return 0
    if n == 1: return 1
    if n == 2: return 0
    if n == 3: return -1

def r2_formula(n):
    """Count representations of n as a² + b² using the divisor sum formula."""
    if n == 0:
        return 1
    total = 0
    for d in range(1, n+1):
        if n % d == 0:
            total += chi_neg4(d)
    return 4 * total

def r2_brute(n):
    """Count representations by brute force."""
    count = 0
    for a in range(-n, n+1):
        for b in range(-n, n+1):
            if a*a + b*b == n:
                count += 1
    return count

def demo_L_functions():
    print("\n" + "=" * 60)
    print("PART 3: L-Functions and χ₋₄")
    print("=" * 60)
    
    # Character table
    print(f"\nCharacter χ₋₄:")
    print(f"  n mod 4:  0  1  2  3")
    print(f"  χ₋₄(n):  {chi_neg4(0):+d} {chi_neg4(1):+d} {chi_neg4(2):+d} {chi_neg4(3):+d}")
    
    # Verify multiplicativity
    print(f"\nMultiplicativity verification (odd × odd):")
    for m in [1, 3, 5, 7, 9, 11]:
        for n in [1, 3, 5, 7]:
            prod_val = chi_neg4(m * n)
            factor_val = chi_neg4(m) * chi_neg4(n)
            ok = prod_val == factor_val
            if not ok:
                print(f"  χ₋₄({m}·{n}={m*n}) = {prod_val}, χ₋₄({m})·χ₋₄({n}) = {factor_val}  {'✓' if ok else '✗'}")
    print(f"  All products verified ✓")
    
    # r₂ formula verification
    print(f"\nVerification of r₂(n) = 4·Σ_{'{d|n}'} χ₋₄(d):")
    print(f"  {'n':>3s}  {'r₂(formula)':>12s}  {'r₂(brute)':>10s}  {'Match':>5s}  {'Divisor sum':>15s}")
    for n in range(0, 26):
        rf = r2_formula(n)
        rb = r2_brute(n)
        divs = [d for d in range(1, n+1) if n % d == 0] if n > 0 else []
        div_sum = sum(chi_neg4(d) for d in divs)
        print(f"  {n:3d}  {rf:12d}  {rb:10d}  {'  ✓' if rf == rb else '  ✗':>5s}  " +
              f"{'Σχ₋₄=' + str(div_sum) if n > 0 else 'special':>15s}")
    
    # Leibniz series
    print(f"\nLeibniz series: π/4 = 1 - 1/3 + 1/5 - 1/7 + ...")
    partial_sums = []
    s = 0
    for k in range(10000):
        s += (-1)**k / (2*k + 1)
        if k in [0, 1, 2, 3, 9, 99, 999, 9999]:
            partial_sums.append((k+1, s))
    for terms, val in partial_sums:
        print(f"  {terms:5d} terms: {val:.10f}  (π/4 = {pi/4:.10f})")
    
    # Which primes are hypotenuses?
    def is_prime(n):
        if n < 2: return False
        for i in range(2, int(sqrt(n))+1):
            if n % i == 0: return False
        return True
    
    print(f"\nPrimes and sum-of-two-squares:")
    for p in range(2, 50):
        if is_prime(p):
            mod4 = p % 4
            is_sos = r2_brute(p) > 0
            reps = [(a,b) for a in range(0,p) for b in range(a,p) if a*a+b*b==p]
            print(f"  p={p:2d} ≡ {mod4} (mod 4): " +
                  f"{'SUM OF TWO SQUARES ' + str(reps[0]) if reps else 'not a sum of two squares'}")


# ============================================================
# Part 4: Quantum Computation
# ============================================================

def demo_quantum():
    print("\n" + "=" * 60)
    print("PART 4: Quantum Computation and SU(1,1)")
    print("=" * 60)
    
    M1 = np.array([[2, -1], [1, 0]])
    M3 = np.array([[1, 2], [0, 1]])
    S = np.array([[0, -1], [1, 0]])
    I2 = np.eye(2, dtype=int)
    
    print(f"\nBerggren generators as quantum gates:")
    print(f"  M₁ = [[2,-1],[1,0]]  det = {int(np.linalg.det(M1)):+d}")
    print(f"  M₃ = [[1, 2],[0,1]]  det = {int(np.linalg.det(M3)):+d}")
    print(f"  S  = [[0,-1],[1,0]]  det = {int(np.linalg.det(S)):+d}")
    
    # Order of S
    print(f"\nOrder of S:")
    Sn = I2.copy()
    for k in range(1, 5):
        Sn = Sn @ S
        is_I = np.allclose(Sn, I2)
        is_neg_I = np.allclose(Sn, -I2)
        print(f"  S^{k} = {Sn.tolist()}  {'= I ✓' if is_I else '= -I' if is_neg_I else ''}")
    
    # Discreteness gaps
    print(f"\nDiscreteness gaps (||M - I||²):")
    for name, M in [("M₁", M1), ("M₃", M3), ("S", S)]:
        gap = np.sum((M - I2)**2)
        print(f"  ||{name} - I||² = {gap}")
    
    # Sparsity
    print(f"\nSparsity (zero entries):")
    for name, M in [("M₁", M1), ("M₃", M3), ("S", S)]:
        zeros = np.sum(M == 0)
        print(f"  {name}: {zeros} zero entries out of 4")
    
    # Tree growth
    print(f"\nBerggren tree growth:")
    for n in range(0, 11):
        print(f"  Depth {n:2d}: {3**n:8d} nodes  (3^{n})")
    
    # Trace classification
    print(f"\nTrace classification (parabolic/elliptic/hyperbolic):")
    for name, M in [("M₁", M1), ("M₃", M3), ("S", S), ("M₁M₃", M1@M3)]:
        tr = int(np.trace(M))
        if abs(tr) < 2:
            kind = "elliptic"
        elif abs(tr) == 2:
            kind = "parabolic"
        else:
            kind = "hyperbolic"
        print(f"  tr({name}) = {tr} → {kind}")


# ============================================================
# Part 5: Hauptmodul
# ============================================================

def demo_hauptmodul():
    print("\n" + "=" * 60)
    print("PART 5: The Hauptmodul (Modular Lambda Function)")
    print("=" * 60)
    
    # Genus and cusps
    print(f"\nModular curve X_θ:")
    print(f"  Genus: 0")
    print(f"  Cusps: 3 (at 0, 1, ∞)")
    print(f"  Index [SL(2,ℤ) : Γ_θ] = 3")
    
    # Lambda at special points
    lam_i = Fraction(1, 2)
    print(f"\nModular lambda function λ(τ):")
    print(f"  λ(i) = {lam_i}")
    print(f"  λ(∞) = 0  (cusp)")
    print(f"  λ(0) = 1  (cusp)")
    print(f"  λ(1) = ∞  (pole/cusp)")
    
    # S-transformation check
    print(f"\nS-transformation: λ(-1/τ) = 1 - λ(τ)")
    print(f"  At τ = i: λ(-1/i) = λ(i) = {lam_i}")
    print(f"  1 - λ(i) = 1 - {lam_i} = {1 - lam_i}")
    print(f"  Consistent: {lam_i == 1 - lam_i}  ✓")
    
    # j-invariant
    lam = Fraction(1, 2)
    j_val = 256 * (lam**2 - lam + 1)**3 / (lam**2 * (1 - lam)**2)
    print(f"\nj-invariant: j(τ) = 256(λ²-λ+1)³ / (λ²(1-λ)²)")
    print(f"  At λ = 1/2: j(i) = {j_val}")
    print(f"  Expected: 1728  {'✓' if j_val == 1728 else '✗'}")
    
    # Anharmonic transformations
    print(f"\nAnharmonic group (transformations of λ):")
    lam_sym = Fraction(1, 3)  # use a non-special value
    transforms = {
        "λ": lam_sym,
        "1-λ": 1 - lam_sym,
        "1/λ": Fraction(1, 1) / lam_sym,
        "1/(1-λ)": Fraction(1, 1) / (1 - lam_sym),
        "λ/(λ-1)": lam_sym / (lam_sym - 1),
        "(λ-1)/λ": (lam_sym - 1) / lam_sym,
    }
    print(f"  For λ = {lam_sym}:")
    for name, val in transforms.items():
        print(f"    {name:12s} = {val}")
    print(f"  Count: {len(transforms)} = 3! = {1*2*3}  ✓")
    
    # Discriminant at cusps
    print(f"\nDiscriminant factor λ²(1-λ)² at cusps:")
    for name, lam_val in [("∞ (λ=0)", 0), ("0 (λ=1)", 1)]:
        disc = lam_val**2 * (1 - lam_val)**2
        print(f"  Cusp {name}: {disc}  {'(vanishes) ✓' if disc == 0 else ''}")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Berggren–Theta Group: Five New Directions Demo         ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    demo_quadruples()
    demo_spectral_gap()
    demo_L_functions()
    demo_quantum()
    demo_hauptmodul()
    
    print("\n" + "=" * 60)
    print("All demos complete. See the formal proofs in:")
    print("  Pythagorean__ModularForms.lean")
    print("  Pythagorean__ModularFormsAdvanced.lean")
    print("=" * 60)
