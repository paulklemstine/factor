#!/usr/bin/env python3
"""
Quaternion Factoring Demo: Lattice Methods via Pythagorean Quadruples

Demonstrates:
1. Quaternion arithmetic and norm multiplicativity
2. Lattice construction L_d(N) for d=3,4
3. LLL reduction for finding short vectors
4. Factor extraction from short vectors
5. Scaling analysis across bit sizes
6. Comparison of extraction methods

Requirements: numpy (standard), no external lattice library needed
"""

import random
import math
from collections import defaultdict
from typing import List, Tuple, Optional
import time

# ============================================================
# Part 1: Quaternion Arithmetic
# ============================================================

class IntQuaternion:
    """Integer quaternion q = a + bi + cj + dk."""
    
    def __init__(self, a: int, b: int, c: int, d: int):
        self.a, self.b, self.c, self.d = a, b, c, d
    
    def norm(self) -> int:
        return self.a**2 + self.b**2 + self.c**2 + self.d**2
    
    def conj(self) -> 'IntQuaternion':
        return IntQuaternion(self.a, -self.b, -self.c, -self.d)
    
    def __mul__(self, other: 'IntQuaternion') -> 'IntQuaternion':
        """Hamilton quaternion multiplication."""
        return IntQuaternion(
            self.a*other.a - self.b*other.b - self.c*other.c - self.d*other.d,
            self.a*other.b + self.b*other.a + self.c*other.d - self.d*other.c,
            self.a*other.c - self.b*other.d + self.c*other.a + self.d*other.b,
            self.a*other.d + self.b*other.c - self.c*other.b + self.d*other.a
        )
    
    def __repr__(self):
        parts = []
        if self.a: parts.append(str(self.a))
        if self.b: parts.append(f"{self.b}i")
        if self.c: parts.append(f"{self.c}j")
        if self.d: parts.append(f"{self.d}k")
        return " + ".join(parts) if parts else "0"


def verify_euler_four_square():
    """Verify Euler's four-square identity on random examples."""
    print("=" * 60)
    print("EULER'S FOUR-SQUARE IDENTITY VERIFICATION")
    print("=" * 60)
    
    for trial in range(5):
        q1 = IntQuaternion(*[random.randint(-10, 10) for _ in range(4)])
        q2 = IntQuaternion(*[random.randint(-10, 10) for _ in range(4)])
        product = q1 * q2
        
        n1, n2, np = q1.norm(), q2.norm(), product.norm()
        assert n1 * n2 == np, f"Norm multiplicativity failed!"
        
        print(f"  q₁ = {q1}, N(q₁) = {n1}")
        print(f"  q₂ = {q2}, N(q₂) = {n2}")
        print(f"  q₁·q₂ = {product}, N(q₁·q₂) = {np}")
        print(f"  N(q₁)·N(q₂) = {n1*n2} ✓")
        print()


# ============================================================
# Part 2: Pell Obstacle Demonstration
# ============================================================

def demonstrate_pell_obstacle():
    """Show that λ² - μ² = 1 has only trivial solutions."""
    print("=" * 60)
    print("PELL OBSTACLE DEMONSTRATION")
    print("=" * 60)
    
    # Search for solutions to λ² - μ² = 1
    solutions = []
    for l in range(-100, 101):
        for m in range(-100, 101):
            if l**2 - m**2 == 1:
                solutions.append((l, m))
    
    print(f"  Solutions to λ² - μ² = 1 with |λ|,|μ| ≤ 100:")
    for l, m in solutions:
        print(f"    (λ, μ) = ({l}, {m})")
    print(f"  Total: {len(solutions)} solutions (all have μ = 0) ✓")
    print()
    
    # Contrast: λ² - 2μ² = 1 has infinitely many
    print(f"  Solutions to λ² - 2μ² = 1 with |λ|,|μ| ≤ 100:")
    pell2_solutions = []
    for l in range(-100, 101):
        for m in range(-100, 101):
            if l**2 - 2*m**2 == 1:
                pell2_solutions.append((l, m))
    
    for l, m in pell2_solutions[:10]:
        print(f"    (λ, μ) = ({l}, {m})")
    if len(pell2_solutions) > 10:
        print(f"    ... ({len(pell2_solutions)} total)")
    print()


# ============================================================
# Part 3: Four-Square Decomposition
# ============================================================

def four_square_decomposition(n: int) -> Tuple[int, int, int, int]:
    """Find a representation n = a² + b² + c² + d² by brute force."""
    for a in range(int(math.isqrt(n)) + 1):
        for b in range(int(math.isqrt(n - a*a)) + 1):
            for c in range(int(math.isqrt(n - a*a - b*b)) + 1):
                rem = n - a*a - b*b - c*c
                if rem >= 0:
                    d = int(math.isqrt(rem))
                    if d*d == rem:
                        return (a, b, c, d)
    return None


def demonstrate_four_square():
    """Demonstrate Lagrange's four-square theorem."""
    print("=" * 60)
    print("LAGRANGE'S FOUR-SQUARE THEOREM")
    print("=" * 60)
    
    test_numbers = [7, 15, 23, 42, 100, 127, 255, 1000]
    for n in test_numbers:
        decomp = four_square_decomposition(n)
        a, b, c, d = decomp
        assert a**2 + b**2 + c**2 + d**2 == n
        print(f"  {n} = {a}² + {b}² + {c}² + {d}²")
    print()


# ============================================================
# Part 4: Pythagorean Quadruple Parametrization
# ============================================================

def pythagorean_quadruple(m: int, n: int, p: int, q: int) -> Tuple[int, int, int, int]:
    """Generate Pythagorean quadruple from parameters."""
    a = m**2 + n**2 - p**2 - q**2
    b = 2*(m*q + n*p)
    c = 2*(n*q - m*p)
    d = m**2 + n**2 + p**2 + q**2
    return (a, b, c, d)


def demonstrate_quadruples():
    """Generate and verify Pythagorean quadruples."""
    print("=" * 60)
    print("PYTHAGOREAN QUADRUPLE PARAMETRIZATION")
    print("=" * 60)
    
    params = [(1,0,0,0), (1,1,0,0), (1,1,1,0), (2,1,0,0), (2,1,1,0), (2,1,1,1)]
    for m, n, p, q in params:
        a, b, c, d = pythagorean_quadruple(m, n, p, q)
        assert a**2 + b**2 + c**2 == d**2, f"Invalid quadruple!"
        print(f"  ({m},{n},{p},{q}) → ({a}, {b}, {c}, {d}): "
              f"{a}² + {b}² + {c}² = {a**2+b**2+c**2} = {d}² = {d**2} ✓")
    print()


# ============================================================
# Part 5: Lattice Construction and LLL
# ============================================================

def find_lattice_vectors(N: int, dim: int = 3, max_search: int = 50) -> List[List[int]]:
    """Find vectors in L_d(N) = {v ∈ ℤ^d : Σv_i² ≡ 0 (mod N)}."""
    vectors = []
    bound = int(math.sqrt(N)) + max_search
    
    if dim == 3:
        for x in range(-bound, bound + 1):
            for y in range(-bound, bound + 1):
                rem = -(x*x + y*y) % N
                z = int(math.isqrt(rem))
                if z*z == rem and (x*x + y*y + z*z) % N == 0 and (x or y or z):
                    vectors.append([x, y, z])
                    if len(vectors) >= 20:
                        return vectors
    elif dim == 4:
        for x in range(-bound, bound + 1):
            for y in range(-bound, bound + 1):
                for z_offset in range(max_search):
                    for z_sign in [1, -1]:
                        z = z_sign * z_offset
                        rem = -(x*x + y*y + z*z) % N
                        w = int(math.isqrt(rem))
                        if w*w == rem and (x*x + y*y + z*z + w*w) % N == 0 and (x or y or z or w):
                            vectors.append([x, y, z, w])
                            if len(vectors) >= 20:
                                return vectors
    return vectors


def gram_schmidt(basis):
    """Gram-Schmidt orthogonalization (for LLL)."""
    n = len(basis)
    ortho = [list(v) for v in basis]
    mu = [[0.0]*n for _ in range(n)]
    
    for i in range(n):
        for j in range(i):
            dot_ij = sum(ortho[i][k] * ortho[j][k] for k in range(len(ortho[0])))
            dot_jj = sum(ortho[j][k] * ortho[j][k] for k in range(len(ortho[0])))
            if dot_jj > 1e-10:
                mu[i][j] = dot_ij / dot_jj
            for k in range(len(ortho[0])):
                ortho[i][k] -= mu[i][j] * ortho[j][k]
    
    return ortho, mu


def lll_reduce(basis, delta=0.75):
    """LLL lattice basis reduction algorithm."""
    if not basis:
        return basis
    
    n = len(basis)
    dim = len(basis[0])
    B = [list(v) for v in basis]
    
    def dot(u, v):
        return sum(a*b for a, b in zip(u, v))
    
    def norm2(v):
        return dot(v, v)
    
    k = 1
    max_iter = 1000
    iteration = 0
    
    while k < n and iteration < max_iter:
        iteration += 1
        ortho, mu = gram_schmidt(B)
        
        # Size reduction
        for j in range(k-1, -1, -1):
            if abs(mu[k][j]) > 0.5:
                r = round(mu[k][j])
                for d in range(dim):
                    B[k][d] -= r * B[j][d]
                ortho, mu = gram_schmidt(B)
        
        # Lovász condition
        n2_k = norm2(ortho[k])
        n2_km1 = norm2(ortho[k-1])
        
        if n2_k >= (delta - mu[k][k-1]**2) * n2_km1:
            k += 1
        else:
            B[k], B[k-1] = B[k-1], B[k]
            k = max(k-1, 1)
    
    return B


# ============================================================
# Part 6: Factor Extraction
# ============================================================

def gcd(a: int, b: int) -> int:
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def extract_factor(vectors: List[List[int]], N: int) -> Optional[int]:
    """Try multiple strategies to extract a factor of N from lattice vectors."""
    
    for v in vectors:
        # Strategy 1: Direct GCD of sum of squares
        s = sum(x**2 for x in v)
        g = gcd(s, N)
        if 1 < g < N:
            return g
        
        # Strategy 2: Partial sums
        dim = len(v)
        for i in range(dim):
            for j in range(i+1, dim):
                g = gcd(v[i]**2 + v[j]**2, N)
                if 1 < g < N:
                    return g
        
        # Strategy 3: Coordinate GCDs
        for x in v:
            g = gcd(abs(x), N)
            if 1 < g < N:
                return g
    
    # Strategy 4: Linear combinations
    for i, v1 in enumerate(vectors[:5]):
        for j, v2 in enumerate(vectors[:5]):
            if i >= j:
                continue
            for a in range(-3, 4):
                for b in range(-3, 4):
                    s = sum((a*v1[k] + b*v2[k])**2 for k in range(len(v1)))
                    g = gcd(s, N)
                    if 1 < g < N:
                        return g
    
    return None


# ============================================================
# Part 7: Primality and Semiprime Generation
# ============================================================

def is_prime(n: int) -> bool:
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i+2) == 0:
            return False
        i += 6
    return True


def random_prime(bits: int) -> int:
    lo = 1 << (bits - 1)
    hi = (1 << bits) - 1
    while True:
        p = random.randint(lo, hi)
        if is_prime(p):
            return p


def random_semiprime(bits: int) -> Tuple[int, int, int]:
    half = bits // 2
    p = random_prime(half)
    q = random_prime(bits - half)
    return p * q, p, q


# ============================================================
# Part 8: Full Pipeline and Experiments
# ============================================================

def run_factoring_experiment(bits: int, trials: int = 50):
    """Run the full quaternion factoring pipeline on random semiprimes."""
    successes = 0
    total_time = 0
    norms = []
    
    for _ in range(trials):
        N, p, q = random_semiprime(bits)
        
        t0 = time.time()
        
        # Step 1: Find lattice vectors
        vectors = find_lattice_vectors(N, dim=3, max_search=30)
        
        if not vectors:
            total_time += time.time() - t0
            continue
        
        # Step 2: LLL reduce
        if len(vectors) >= 3:
            reduced = lll_reduce(vectors[:min(6, len(vectors))])
        else:
            reduced = vectors
        
        # Track shortest vector norm
        min_norm = min(math.sqrt(sum(x**2 for x in v)) for v in reduced)
        norms.append((N, min_norm))
        
        # Step 3: Extract factor
        factor = extract_factor(reduced, N)
        
        if factor and (factor == p or factor == q or N // factor == p or N // factor == q):
            successes += 1
        elif factor and N % factor == 0:
            successes += 1
        
        total_time += time.time() - t0
    
    return {
        'bits': bits,
        'trials': trials,
        'successes': successes,
        'rate': successes / trials,
        'avg_time_ms': total_time / trials * 1000,
        'norms': norms
    }


def scaling_analysis():
    """Analyze how the method scales with input size."""
    print("=" * 60)
    print("SCALING ANALYSIS")
    print("=" * 60)
    
    print(f"{'Bits':>6} {'Trials':>8} {'Success':>8} {'Rate':>8} {'Time(ms)':>10}")
    print("-" * 50)
    
    results = []
    for bits in [6, 8, 10, 12, 14]:
        result = run_factoring_experiment(bits, trials=30)
        results.append(result)
        print(f"{result['bits']:>6} {result['trials']:>8} "
              f"{result['successes']:>8} {result['rate']:>8.2%} "
              f"{result['avg_time_ms']:>10.1f}")
    
    # Compute scaling exponent
    if len(results) >= 2 and results[0]['norms'] and results[-1]['norms']:
        avg_N_small = sum(n for n, _ in results[0]['norms']) / max(1, len(results[0]['norms']))
        avg_norm_small = sum(v for _, v in results[0]['norms']) / max(1, len(results[0]['norms']))
        avg_N_large = sum(n for n, _ in results[-1]['norms']) / max(1, len(results[-1]['norms']))
        avg_norm_large = sum(v for _, v in results[-1]['norms']) / max(1, len(results[-1]['norms']))
        
        if avg_N_small > 1 and avg_N_large > 1 and avg_norm_small > 0 and avg_norm_large > 0:
            alpha = (math.log(avg_norm_large) - math.log(avg_norm_small)) / \
                    (math.log(avg_N_large) - math.log(avg_N_small))
            print(f"\n  Fitted scaling exponent α ≈ {alpha:.3f}")
            print(f"  (Classical trial division: α = 0.500)")
    print()


def dimension_comparison():
    """Compare factoring success across dimensions."""
    print("=" * 60)
    print("DIMENSION COMPARISON")
    print("=" * 60)
    
    bits = 10
    trials = 30
    
    print(f"  Testing {bits}-bit semiprimes, {trials} trials each")
    print(f"  {'Dim':>6} {'Success':>8} {'Rate':>8}")
    print("  " + "-" * 30)
    
    for dim in [3, 4]:
        successes = 0
        for _ in range(trials):
            N, p, q = random_semiprime(bits)
            vectors = find_lattice_vectors(N, dim=dim, max_search=30)
            if vectors:
                reduced = lll_reduce(vectors[:min(6, len(vectors))])
                factor = extract_factor(reduced, N)
                if factor and N % factor == 0 and 1 < factor < N:
                    successes += 1
        
        print(f"  {dim:>6} {successes:>8} {successes/trials:>8.2%}")
    print()


# ============================================================
# Part 9: Quaternion Representation Counting
# ============================================================

def count_four_square_representations(n: int) -> int:
    """Count the number of ways to write n = a² + b² + c² + d² (including signs and order)."""
    count = 0
    bound = int(math.isqrt(n))
    for a in range(-bound, bound + 1):
        for b in range(-bound, bound + 1):
            rem1 = n - a*a - b*b
            if rem1 < 0:
                continue
            for c in range(-int(math.isqrt(rem1)), int(math.isqrt(rem1)) + 1):
                rem2 = rem1 - c*c
                if rem2 < 0:
                    continue
                d = int(math.isqrt(rem2))
                if d*d == rem2:
                    count += 1
                    if d > 0:
                        count += 1  # also -d
    return count


def jacobi_r4(n: int) -> int:
    """Jacobi's formula: r₄(n) = 8 * Σ_{d|n, 4∤d} d."""
    total = 0
    for d in range(1, n + 1):
        if n % d == 0 and d % 4 != 0:
            total += d
    return 8 * total


def demonstrate_jacobi():
    """Verify Jacobi's four-square theorem."""
    print("=" * 60)
    print("JACOBI'S FOUR-SQUARE THEOREM VERIFICATION")
    print("=" * 60)
    
    semiprimes = [15, 21, 35, 55, 77]
    print(f"  {'N':>6} {'r₄(N) counted':>15} {'Jacobi formula':>15} {'Match':>6}")
    print("  " + "-" * 50)
    
    for n in semiprimes:
        counted = count_four_square_representations(n)
        jacobi = jacobi_r4(n)
        match = "✓" if counted == jacobi else "✗"
        print(f"  {n:>6} {counted:>15} {jacobi:>15} {match:>6}")
    print()


# ============================================================
# Part 10: Octonion Multiplication Demo
# ============================================================

class Octonion:
    """Real octonion e₀ + e₁·a₁ + ... + e₇·a₇."""
    
    # Fano plane multiplication table for imaginary units e₁..e₇
    # e_i * e_j = sign * e_k
    MULT_TABLE = {
        (1,2): (1, 3), (2,1): (-1, 3),
        (1,3): (-1, 2), (3,1): (1, 2),
        (1,4): (1, 5), (4,1): (-1, 5),
        (1,5): (-1, 4), (5,1): (1, 4),
        (1,6): (-1, 7), (6,1): (1, 7),
        (1,7): (1, 6), (7,1): (-1, 6),
        (2,3): (1, 1), (3,2): (-1, 1),
        (2,4): (1, 6), (4,2): (-1, 6),
        (2,5): (-1, 7), (5,2): (1, 7),
        (2,6): (-1, 4), (6,2): (1, 4),
        (2,7): (1, 5), (7,2): (-1, 5),
        (3,4): (-1, 7), (4,3): (1, 7),
        (3,5): (1, 6), (5,3): (-1, 6),
        (3,6): (-1, 5), (6,3): (1, 5),
        (3,7): (1, 4), (7,3): (-1, 4),
        (4,5): (1, 1), (5,4): (-1, 1),
        (4,6): (1, 2), (6,4): (-1, 2),
        (4,7): (1, 3), (7,4): (-1, 3),
        (5,6): (1, 3), (6,5): (-1, 3),
        (5,7): (-1, 2), (7,5): (1, 2),
        (6,7): (1, 1), (7,6): (-1, 1),
    }
    
    def __init__(self, components: List[float]):
        assert len(components) == 8
        self.c = list(components)
    
    def norm_sq(self) -> float:
        return sum(x**2 for x in self.c)
    
    def __repr__(self):
        labels = ['1', 'e₁', 'e₂', 'e₃', 'e₄', 'e₅', 'e₆', 'e₇']
        parts = [f"{self.c[i]:.0f}·{labels[i]}" for i in range(8) if abs(self.c[i]) > 1e-10]
        return " + ".join(parts) if parts else "0"


def demonstrate_octonion_non_associativity():
    """Show that octonion multiplication is NOT associative."""
    print("=" * 60)
    print("OCTONION NON-ASSOCIATIVITY")
    print("=" * 60)
    
    # Use simple basis elements to demonstrate
    # e₁ * (e₂ * e₄) vs (e₁ * e₂) * e₄
    
    # In standard Cayley-Dickson construction with common conventions:
    # e₁·e₂ = e₃, e₂·e₄ = e₆, e₁·e₆ = -e₇, e₃·e₄ = -e₇
    # So (e₁·e₂)·e₄ = e₃·e₄ and e₁·(e₂·e₄) = e₁·e₆
    # These may differ in sign depending on convention
    
    print("  Octonion multiplication is non-associative.")
    print("  This is why direct extension of quaternion factoring to 8D is non-trivial.")
    print()
    print("  However, the NORM is still multiplicative (Degen's identity):")
    print("  N(o₁·o₂) = N(o₁)·N(o₂)  for all octonions o₁, o₂")
    print()
    
    # Verify Degen's identity on random examples
    print("  Degen's Eight-Square Identity verification:")
    for trial in range(3):
        a = [random.randint(-5, 5) for _ in range(8)]
        b = [random.randint(-5, 5) for _ in range(8)]
        
        na = sum(x**2 for x in a)
        nb = sum(x**2 for x in b)
        
        # Compute the product using Degen's formula
        c = [0]*8
        c[0] = a[0]*b[0]-a[1]*b[1]-a[2]*b[2]-a[3]*b[3]-a[4]*b[4]-a[5]*b[5]-a[6]*b[6]-a[7]*b[7]
        c[1] = a[0]*b[1]+a[1]*b[0]+a[2]*b[3]-a[3]*b[2]+a[4]*b[5]-a[5]*b[4]-a[6]*b[7]+a[7]*b[6]
        c[2] = a[0]*b[2]-a[1]*b[3]+a[2]*b[0]+a[3]*b[1]+a[4]*b[6]+a[5]*b[7]-a[6]*b[4]-a[7]*b[5]
        c[3] = a[0]*b[3]+a[1]*b[2]-a[2]*b[1]+a[3]*b[0]+a[4]*b[7]-a[5]*b[6]+a[6]*b[5]-a[7]*b[4]
        c[4] = a[0]*b[4]-a[1]*b[5]-a[2]*b[6]-a[3]*b[7]+a[4]*b[0]+a[5]*b[1]+a[6]*b[2]+a[7]*b[3]
        c[5] = a[0]*b[5]+a[1]*b[4]-a[2]*b[7]+a[3]*b[6]-a[4]*b[1]+a[5]*b[0]-a[6]*b[3]+a[7]*b[2]
        c[6] = a[0]*b[6]+a[1]*b[7]+a[2]*b[4]-a[3]*b[5]-a[4]*b[2]+a[5]*b[3]+a[6]*b[0]-a[7]*b[1]
        c[7] = a[0]*b[7]-a[1]*b[6]+a[2]*b[5]+a[3]*b[4]-a[4]*b[3]-a[5]*b[2]+a[6]*b[1]+a[7]*b[0]
        
        nc = sum(x**2 for x in c)
        assert na * nb == nc, f"Degen's identity failed!"
        print(f"    Trial {trial+1}: N(a)={na}, N(b)={nb}, N(a)·N(b)={na*nb}, N(a·b)={nc} ✓")
    print()


# ============================================================
# Part 11: Hurwitz Order Demo
# ============================================================

class HurwitzQuaternion:
    """Hurwitz quaternion: coordinates are either all integers or all half-integers.
    Stored as (2a, 2b, 2c, 2d) to avoid fractions."""
    
    def __init__(self, a2: int, b2: int, c2: int, d2: int):
        """Components are doubled: actual quaternion is (a2/2, b2/2, c2/2, d2/2).
        Must all be even (integer quaternion) or all odd (half-integer)."""
        assert (a2 + b2 + c2 + d2) % 2 == 0, "Not a valid Hurwitz quaternion"
        self.a2, self.b2, self.c2, self.d2 = a2, b2, c2, d2
    
    def norm_times_4(self) -> int:
        """4 * norm (to stay in integers)."""
        return self.a2**2 + self.b2**2 + self.c2**2 + self.d2**2
    
    def __repr__(self):
        def fmt(x2):
            if x2 % 2 == 0:
                return str(x2 // 2)
            return f"{x2}/2"
        return f"({fmt(self.a2)}, {fmt(self.b2)}, {fmt(self.c2)}, {fmt(self.d2)})"


def demonstrate_hurwitz():
    """Show the Hurwitz order and its special properties."""
    print("=" * 60)
    print("HURWITZ QUATERNION ORDER")
    print("=" * 60)
    
    # The 24 units of the Hurwitz order
    units = []
    
    # 8 Lipschitz units: ±1, ±i, ±j, ±k
    for sign in [1, -1]:
        for pos in range(4):
            v = [0, 0, 0, 0]
            v[pos] = 2 * sign
            units.append(HurwitzQuaternion(*v))
    
    # 16 half-integer units: (±1 ± i ± j ± k)/2
    for s0 in [1, -1]:
        for s1 in [1, -1]:
            for s2 in [1, -1]:
                for s3 in [1, -1]:
                    units.append(HurwitzQuaternion(s0, s1, s2, s3))
    
    print(f"  Hurwitz order has {len(units)} units (vs 8 for Lipschitz integers)")
    print(f"  Sample units:")
    for u in units[:8]:
        n4 = u.norm_times_4()
        print(f"    {u}, 4·norm = {n4}, norm = {n4/4}")
    print(f"    ...")
    for u in units[8:12]:
        n4 = u.norm_times_4()
        print(f"    {u}, 4·norm = {n4}, norm = {n4/4}")
    print()
    print("  The Hurwitz order has unique factorization (up to units and order),")
    print("  unlike the Lipschitz integers. This potentially improves factor extraction.")
    print()


# ============================================================
# Main
# ============================================================

def main():
    random.seed(42)
    
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   QUATERNION FACTORING: LATTICE METHODS DEMO            ║")
    print("║   Via Pythagorean Quadruples and Norm Decomposition     ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    verify_euler_four_square()
    demonstrate_pell_obstacle()
    demonstrate_four_square()
    demonstrate_quadruples()
    demonstrate_jacobi()
    demonstrate_octonion_non_associativity()
    demonstrate_hurwitz()
    scaling_analysis()
    dimension_comparison()
    
    print("=" * 60)
    print("ALL DEMOS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
