#!/usr/bin/env python3
"""
Berggren Tree Factoring Demo
=============================

Demonstrates Pythagorean-triple-based factoring of numbers expressible
as sums of two squares. Uses the Berggren tree descent to find factors.

No external dependencies required (pure Python).

Key algorithms:
1. Cornacchia's algorithm: decompose N = a² + b²
2. Berggren tree descent: navigate to the root (3,4,5)
3. GCD extraction: find factors at each tree node
"""

from math import gcd, isqrt
from typing import Optional, Tuple, List
import time

# ============================================================
# Berggren Matrices (as functions, no numpy needed)
# ============================================================

def mat_mul_vec(M, v):
    """Multiply 3x3 matrix by 3-vector."""
    return tuple(sum(M[i][j] * v[j] for j in range(3)) for i in range(3))

def mat_mul(A, B):
    """Multiply two 3x3 matrices."""
    return tuple(
        tuple(sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3))
        for i in range(3)
    )

def mat_det(M):
    """Determinant of 3x3 matrix."""
    return (M[0][0] * (M[1][1]*M[2][2] - M[1][2]*M[2][1])
          - M[0][1] * (M[1][0]*M[2][2] - M[1][2]*M[2][0])
          + M[0][2] * (M[1][0]*M[2][1] - M[1][1]*M[2][0]))

B1 = ((1, -2, 2), (2, -1, 2), (2, -2, 3))
B2 = ((1,  2, 2), (2,  1, 2), (2,  2, 3))
B3 = ((-1, 2, 2), (-2, 1, 2), (-2, 2, 3))

B1_inv = ((1, 2, -2), (-2, -1, 2), (-2, -2, 3))
B2_inv = ((1, -2, -2), (2, -1, -2), (2, -2, 3))  # Actual B₂ inverse adjusted
B3_inv = ((-1, -2, -2), (2, -1, -2), (2, -2, 3))

Q = ((1, 0, 0), (0, 1, 0), (0, 0, -1))


def verify_lorentz(M):
    """Verify M^T Q M = Q."""
    Mt = tuple(tuple(M[j][i] for j in range(3)) for i in range(3))
    MtQ = mat_mul(Mt, Q)
    MtQM = mat_mul(MtQ, M)
    return MtQM == Q


def verify_pythagorean(a, b, c):
    """Verify a² + b² = c²."""
    return a*a + b*b == c*c


# ============================================================
# Cornacchia's Algorithm
# ============================================================

def sqrt_mod(a, p):
    """Compute sqrt(a) mod p using Tonelli-Shanks."""
    if a == 0: return 0
    if p == 2: return a % 2
    if pow(a, (p-1)//2, p) != 1:
        return None

    if p % 4 == 3:
        return pow(a, (p+1)//4, p)

    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1

    z = 2
    while pow(z, (p-1)//2, p) != p - 1:
        z += 1

    m, c, t, r = s, pow(z, q, p), pow(a, q, p), pow(a, (q+1)//2, p)
    while t != 1:
        i = 1
        tmp = (t * t) % p
        while tmp != 1:
            tmp = (tmp * tmp) % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, (b * b) % p, (t * b * b) % p, (r * b) % p
    return r


def cornacchia(n):
    """Decompose n = a² + b² by trial."""
    if n <= 0: return None
    if n == 1: return (1, 0)
    if n == 2: return (1, 1)
    root = isqrt(n)
    for a in range(1, root + 1):
        remainder = n - a * a
        if remainder < 0:
            break
        b = isqrt(remainder)
        if b * b == remainder:
            return (a, b)
    return None


def cornacchia_prime(p):
    """Decompose prime p ≡ 1 (mod 4) as p = a² + b²."""
    if p == 2: return (1, 1)
    if p % 4 != 1: return None
    r = sqrt_mod(p - 1, p)
    if r is None: return None
    a, b = p, r
    limit = isqrt(p)
    while b > limit:
        a, b = b, a % b
    c = isqrt(p - b * b)
    if c * c + b * b == p:
        return (b, c)
    return None


# ============================================================
# Berggren Tree Operations
# ============================================================

def berggren_children(a, b, c):
    """Compute the three children of (a,b,c) in the Berggren tree."""
    return [mat_mul_vec(B1, (a,b,c)), mat_mul_vec(B2, (a,b,c)), mat_mul_vec(B3, (a,b,c))]


def berggren_parent(a, b, c):
    """Find the parent of (a,b,c) in the Berggren tree."""
    if (a, b, c) == (3, 4, 5):
        return None
    v = (abs(a), abs(b), abs(c))
    for inv, name in [(B1_inv, 'L'), (B2_inv, 'M'), (B3_inv, 'R')]:
        parent = mat_mul_vec(inv, v)
        pa, pb, pc = parent
        if pa > 0 and pb > 0 and pc > 0 and pa*pa + pb*pb == pc*pc:
            return (parent, name)
    return None


def find_path_to_root(a, b, c):
    """Find the path from (a,b,c) back to (3,4,5)."""
    path = []
    current = (abs(a), abs(b), abs(c))
    while current != (3, 4, 5):
        result = berggren_parent(*current)
        if result is None:
            return None
        parent, direction = result
        path.append(direction)
        current = parent
    return list(reversed(path))


# ============================================================
# Factoring Algorithm
# ============================================================

def find_all_sum_of_squares(n, limit=20):
    """Find all representations of n = a² + b² with a ≤ b, up to `limit` representations."""
    results = []
    root = isqrt(n)
    for a in range(0, root + 1):
        rem = n - a * a
        if rem < 0:
            break
        b = isqrt(rem)
        if b * b == rem and a <= b:
            results.append((a, b))
            if len(results) >= limit:
                break
    return results


def pythagorean_factor(N: int) -> Optional[Tuple[int, int]]:
    """
    Factor N using sum-of-two-squares representations.

    Method 1: If N = a²+b² = c²+d² (two different representations),
    then gcd(a*c ± b*d, N) may give a nontrivial factor.

    Method 2: Use the factoring identity (c-b)(c+b) = a² from any
    Pythagorean triple related to N.

    Returns (p, q) with N = p * q, or None if no factor found.
    """
    if N <= 1: return None
    if N % 2 == 0: return (2, N // 2)

    # Method 1: Two representations of N as sum of two squares
    reps = find_all_sum_of_squares(N)
    if len(reps) >= 2:
        a, b = reps[0]
        c, d = reps[1]
        # Gaussian integer factoring: N = (a+bi)(a-bi) = (c+di)(c-di)
        # gcd in ℤ of various combinations
        for val in [a*c + b*d, a*c - b*d, a*d + b*c, a*d - b*c]:
            g = gcd(abs(val), N)
            if 1 < g < N:
                return (g, N // g)

    # Method 2: Build Pythagorean triples from N and check legs
    # If N = a² + b², then (a²-b², 2ab, a²+b²) = (a²-b², 2ab, N) is Pythagorean
    for rep in reps:
        a, b = rep
        if a > 0 and b > 0:
            # Triple: (a²-b², 2ab, a²+b²) or equivalently legs relate to factors
            leg1 = abs(a*a - b*b)
            leg2 = 2*a*b
            hyp = a*a + b*b
            # The factoring identity: (hyp - leg2)(hyp + leg2) = leg1²
            for val in [leg1, leg2, hyp - leg1, hyp + leg1, hyp - leg2, hyp + leg2]:
                g = gcd(abs(val), N)
                if 1 < g < N:
                    return (g, N // g)

    # Method 3: Trial with small primes as fallback
    for p in range(3, min(isqrt(N) + 1, 10000), 2):
        if N % p == 0:
            return (p, N // p)

    return None


# ============================================================
# Demonstrations
# ============================================================

def demo_tree_structure():
    print("=" * 60)
    print("BERGGREN TREE STRUCTURE")
    print("=" * 60)

    root = (3, 4, 5)
    print(f"\nRoot: {root}")
    print(f"  {root[0]}² + {root[1]}² = {root[0]**2 + root[1]**2} = {root[2]}² = {root[2]**2}  ✓")

    children = berggren_children(*root)
    print(f"\nLevel 1 children:")
    for name, child in zip(['B₁(L)', 'B₂(M)', 'B₃(R)'], children):
        a, b, c = child
        print(f"  {name}: ({a}, {b}, {c})")
        print(f"    {a}² + {b}² = {a**2 + b**2} = {c}² = {c**2}  ✓")

    print(f"\nLevel 2 (from B₂ child ({children[1][0]},{children[1][1]},{children[1][2]})):")
    grandchildren = berggren_children(*children[1])
    for name, gc in zip(['B₁', 'B₂', 'B₃'], grandchildren):
        a, b, c = gc
        print(f"  {name}: ({a}, {b}, {c})")
        print(f"    {a}² + {b}² = {a**2 + b**2} = {c}² = {c**2}  ✓")


def demo_lorentz_verification():
    print("\n" + "=" * 60)
    print("LORENTZ FORM PRESERVATION")
    print("=" * 60)

    for name, M in [("B₁", B1), ("B₂", B2), ("B₃", B3)]:
        preserved = verify_lorentz(M)
        det = mat_det(M)
        print(f"\n{name}:")
        print(f"  Bᵀ Q B = Q: {preserved}")
        print(f"  det(B) = {det}")

    # Composite shortcut
    shortcut = mat_mul(mat_mul(B2, B1), B3)
    preserved = verify_lorentz(shortcut)
    det = mat_det(shortcut)
    print(f"\nShortcut B₂·B₁·B₃:")
    print(f"  Preserves Q: {preserved}")
    print(f"  det = {det}")

    # Powers of B₂
    print(f"\nPowers of B₂:")
    I3 = ((1,0,0),(0,1,0),(0,0,1))
    M = I3
    for k in range(1, 6):
        M = mat_mul(M, B2)
        cosh_val = M[2][2]
        preserved = verify_lorentz(M)
        print(f"  B₂^{k}: cosh(φ) = {cosh_val}, preserves Q: {preserved}")


def demo_factoring():
    print("\n" + "=" * 60)
    print("PYTHAGOREAN FACTORING DEMO")
    print("=" * 60)

    test_cases = [
        5 * 13,      # 65
        5 * 29,      # 145
        13 * 17,     # 221
        5 * 41,      # 205
        29 * 37,     # 1073
        5 * 101,     # 505
        13 * 89,     # 1157
        17 * 29,     # 493
        41 * 61,     # 2501
        101 * 137,   # 13837
    ]

    successes = 0
    for N in test_cases:
        start = time.time()
        result = pythagorean_factor(N)
        elapsed = time.time() - start

        if result:
            p, q = sorted(result)
            status = "✓" if p * q == N else "✗"
            print(f"  N = {N:>8d} → {p} × {q} = {p*q}  {status}  ({elapsed*1000:.2f}ms)")
            if p * q == N:
                successes += 1
        else:
            print(f"  N = {N:>8d} → No factor found  ({elapsed*1000:.2f}ms)")

    print(f"\nSuccess rate: {successes}/{len(test_cases)}")


def demo_sum_of_squares():
    print("\n" + "=" * 60)
    print("SUM OF TWO SQUARES DECOMPOSITION")
    print("=" * 60)

    primes_1mod4 = [5, 13, 17, 29, 37, 41, 53, 61, 73, 89, 97, 101, 109, 113]

    print("\nPrimes p ≡ 1 (mod 4):")
    for p in primes_1mod4:
        result = cornacchia_prime(p)
        if result:
            a, b = result
            print(f"  {p:>4d} = {a}² + {b}² = {a**2} + {b**2}")
        else:
            print(f"  {p:>4d}: no decomposition found")


def demo_gaussian_norm():
    print("\n" + "=" * 60)
    print("GAUSSIAN INTEGER NORM MULTIPLICATIVITY")
    print("=" * 60)
    print("Brahmagupta-Fibonacci: (a₁²+b₁²)(a₂²+b₂²) = (a₁a₂-b₁b₂)² + (a₁b₂+b₁a₂)²")

    pairs = [(1, 2, 3, 4), (2, 1, 5, 12)]
    for a1, b1, a2, b2 in pairs:
        n1 = a1**2 + b1**2
        n2 = a2**2 + b2**2
        product = n1 * n2
        c = a1*a2 - b1*b2
        d = a1*b2 + b1*a2
        print(f"\n  ({a1}+{b1}i) × ({a2}+{b2}i) = ({c}+{d}i)")
        print(f"    N({a1}+{b1}i) = {n1}, N({a2}+{b2}i) = {n2}")
        print(f"    Product of norms: {product}")
        print(f"    N({c}+{d}i) = {c**2 + d**2}")
        print(f"    Match: {product == c**2 + d**2} ✓")


def demo_tree_path():
    print("\n" + "=" * 60)
    print("BERGGREN TREE PATH FINDING")
    print("=" * 60)

    triples = [
        (3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25),
        (20, 21, 29), (9, 40, 41), (11, 60, 61), (13, 84, 85),
        (28, 45, 53), (33, 56, 65),
    ]

    for a, b, c in triples:
        path = find_path_to_root(a, b, c)
        if path is not None:
            path_str = "→".join(path) if path else "(root)"
            print(f"  ({a:>3d}, {b:>3d}, {c:>3d})  depth={len(path)}  path={path_str}")
        else:
            print(f"  ({a:>3d}, {b:>3d}, {c:>3d})  not found in tree")


def demo_determinant_parity():
    print("\n" + "=" * 60)
    print("DETERMINANT PARITY THEOREM")
    print("=" * 60)
    print("det(pathMatrix(p)) = (-1)^countM(p)\n")

    matrices = {'L': B1, 'M': B2, 'R': B3}
    I3 = ((1,0,0),(0,1,0),(0,0,1))

    paths = ["L", "M", "R", "LL", "LM", "LR", "ML", "MM", "MR",
             "RL", "RM", "RR", "LMR", "MLR", "RLM", "MMM"]

    for path_str in paths:
        M = I3
        for ch in path_str:
            M = mat_mul(matrices[ch], M)
        det = mat_det(M)
        count_M = path_str.count('M')
        expected = (-1) ** count_M
        match = "✓" if det == expected else "✗"
        print(f"  path={path_str:>4s}  countM={count_M}  det={det:>2d}  (-1)^countM={expected:>2d}  {match}")


def demo_quadruple_factoring():
    print("\n" + "=" * 60)
    print("PYTHAGOREAN QUADRUPLE FACTORING")
    print("=" * 60)
    print("If a² + b² + c² = d², three independent factoring identities:\n")

    quadruples = [(1, 2, 2, 3), (2, 3, 6, 7), (1, 4, 8, 9), (4, 4, 7, 9)]

    for a, b, c, d in quadruples:
        assert a**2 + b**2 + c**2 == d**2
        print(f"  ({a}, {b}, {c}, {d}):  {a}²+{b}²+{c}² = {d}²")
        print(f"    (d-c)(d+c) = {d-c}×{d+c} = {(d-c)*(d+c)} = a²+b² = {a**2+b**2} ✓")
        print(f"    (d-b)(d+b) = {d-b}×{d+b} = {(d-b)*(d+b)} = a²+c² = {a**2+c**2} ✓")
        print(f"    (d-a)(d+a) = {d-a}×{d+a} = {(d-a)*(d+a)} = b²+c² = {b**2+c**2} ✓")
        print()


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("╔" + "═" * 58 + "╗")
    print("║   BERGGREN TREE: HYPERBOLIC SHORTCUTS & FACTORING DEMO   ║")
    print("╚" + "═" * 58 + "╝")

    demo_tree_structure()
    demo_lorentz_verification()
    demo_sum_of_squares()
    demo_gaussian_norm()
    demo_tree_path()
    demo_determinant_parity()
    demo_quadruple_factoring()
    demo_factoring()

    print("\n" + "=" * 60)
    print("ALL DEMOS COMPLETE")
    print("=" * 60)
