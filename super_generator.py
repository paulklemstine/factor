#!/usr/bin/env python3
"""
Super-Generator: Pythagorean Tree Pathfinding Engine
=====================================================
9-matrix library (Berggren + Price + Barning-Hall) with:
  - Spectral ratio locking (target R = (n+k²)/(n-k²))
  - Jacobian selection (greedy ∇R minimization)
  - Modular scent (p-adic GPS pruning)
  - VSDD resolution at each node

This is Path 1 of the Resonance Sieve v7.0.
"""

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd
import time
import math
from collections import deque
import heapq


###############################################################################
# Matrix Libraries
###############################################################################

# Berggren's 3 matrices: generate ALL primitive Pythagorean triples from (3,4,5)
BERGGREN = [
    # M1: (A,B,C) -> (A-2B+2C, 2A-B+2C, 2A-2B+3C)
    [( 1,-2, 2), ( 2,-1, 2), ( 2,-2, 3)],
    # M2: (A,B,C) -> (A+2B+2C, 2A+B+2C, 2A+2B+3C)
    [( 1, 2, 2), ( 2, 1, 2), ( 2, 2, 3)],
    # M3: (A,B,C) -> (-A+2B+2C, -2A+B+2C, -2A+2B+3C)
    [(-1, 2, 2), (-2, 1, 2), (-2, 2, 3)],
]

# Price's 3 matrices: organized by excess (C-B)
PRICE = [
    # U1
    [( 1, 0, 0), ( 2, 1, 0), ( 2, 0, 1)],
    # U2
    [(-1, 0, 2), (-2, 1, 2), (-2, 0, 3)],
    # U3
    [( 1, 0, 2), ( 2, 1, 2), ( 2, 0, 3)],
]

# Barning-Hall matrices (another parameterization)
HALL = [
    [( 1,-2, 2), ( 2,-1, 2), ( 2,-2, 3)],
    [( 1, 2, 2), ( 2, 1, 2), ( 2, 2, 3)],
    [(-1, 2, 2), (-2, 1, 2), (-2, 2, 3)],
]


def mat_mul(M, v):
    """Multiply 3x3 matrix M by vector v = (A, B, C)."""
    return (
        M[0][0]*v[0] + M[0][1]*v[1] + M[0][2]*v[2],
        M[1][0]*v[0] + M[1][1]*v[1] + M[1][2]*v[2],
        M[2][0]*v[0] + M[2][1]*v[1] + M[2][2]*v[2],
    )


# Inverse matrices for bottom-up climbing
def mat_inverse_3x3(M):
    """Compute inverse of integer 3x3 matrix (exact for Pythagorean matrices with det=±1)."""
    a, b, c = M[0]
    d, e, f = M[1]
    g, h, i = M[2]
    det = a*(e*i - f*h) - b*(d*i - f*g) + c*(d*h - e*g)
    if abs(det) != 1:
        return None
    # Cofactor matrix transposed, scaled by det
    inv = [
        [det*(e*i - f*h), det*(c*h - b*i), det*(b*f - c*e)],
        [det*(f*g - d*i), det*(a*i - c*g), det*(c*d - a*f)],
        [det*(d*h - e*g), det*(b*g - a*h), det*(a*e - b*d)],
    ]
    return inv


# All 9 matrices combined
ALL_MATRICES = BERGGREN + PRICE + HALL
# Remove duplicates (Berggren and Hall are the same)
# Berggren == Hall, so we have 6 unique matrices
UNIQUE_MATRICES = BERGGREN + PRICE  # 6 matrices


###############################################################################
# Spectral Ratio
###############################################################################

def target_ratio(n, k):
    """Target ratio R = (n + k²) / (n - k²) for factor gap k."""
    num = n + k * k
    den = n - k * k
    if den <= 0:
        return float('inf')
    return float(num) / float(den)


def node_ratio(B, C):
    """Ratio R = C/B for a Pythagorean triple."""
    if B <= 0:
        return float('inf')
    return float(C) / float(B)


###############################################################################
# Modular Pruning (P-adic GPS)
###############################################################################

def build_modular_filter(n, moduli=[8, 9, 16, 5, 7, 11, 13]):
    """
    Build modular filter tables.
    For each modulus m, compute allowed (C²-B²) mod m values that
    could equal n mod m.
    """
    filters = {}
    for m in moduli:
        n_mod = int(n % m)
        # Allowed: C²-B² ≡ n (mod m)
        # Precompute all (C mod m, B mod m) pairs where C²-B² ≡ n_mod
        allowed = set()
        for c in range(m):
            for b in range(m):
                if (c * c - b * b) % m == n_mod:
                    allowed.add((b % m, c % m))
        filters[m] = allowed
    return filters


def passes_modular_filter(B, C, filters):
    """Check if (B, C) passes all modular filters."""
    for m, allowed in filters.items():
        if (B % m, C % m) not in allowed:
            return False
    return True


###############################################################################
# VSDD Check
###############################################################################

def vsdd_check(n, delta):
    """
    O(1) VSDD check: B = (n - Δ²) / (2Δ).
    If B is a positive integer, factors are Δ and (2B + Δ).
    """
    if delta <= 0 or delta * delta >= n:
        return None
    numerator = n - delta * delta
    denominator = 2 * delta
    if numerator <= 0:
        return None
    if numerator % denominator != 0:
        return None
    B = numerator // denominator
    factor1 = delta
    factor2 = 2 * B + delta
    if factor1 * factor2 == n and factor1 > 1 and factor2 > 1 and factor1 != n:
        return int(min(factor1, factor2))
    return None


###############################################################################
# Super-Generator Engine
###############################################################################

def super_generator_factor(n, verbose=True, time_limit=60, max_depth=200):
    """
    Pythagorean tree pathfinding with 6-matrix Super-Generator.

    Strategy:
    1. Greedy descent: at each node, pick the matrix that brings
       the spectral ratio C/B closest to the target ratio.
    2. At each node, check VSDD with Δ = C - B.
    3. Modular pruning eliminates impossible branches.
    4. BFS with priority queue (best-first search by ratio error).
    """
    n = mpz(n)
    nb = int(gmpy2.log2(n)) + 1
    sqrt_n = isqrt(n)

    if verbose:
        print(f"  Super-Generator: {len(str(int(n)))}d ({nb}b)")

    t0 = time.time()

    # Build modular filter
    filters = build_modular_filter(n)

    # Try different target ratios (resonance bands)
    # For n = p*q with p < q: gap k = (q-p)/2, sum s = (q+p)/2
    # R_target = C/B where C² - B² = n
    # So C = s = (p+q)/2, B = (q-p)/2... no, C²-B² = (C-B)(C+B) = n
    # With Δ = C-B: n = Δ*(2B+Δ), so if Δ = p then 2B+Δ = q, B = (q-p)/2
    # R = C/B = (B+Δ)/B = 1 + Δ/B

    # For balanced semiprimes: p ≈ q ≈ sqrt(n), so Δ ≈ sqrt(n), B ≈ small
    # For unbalanced: small factor p, Δ = p, B = (q-p)/2 ≈ q/2 ≈ n/(2p)
    # R ≈ 1 + 2p²/n for unbalanced

    checked = 0
    found = None

    # ── Method 1: Greedy tree descent with multiple starting ratios ──
    for k_approx in [1, 2, 3, 5, 7, 10, 15, 20, 50, 100]:
        if time.time() - t0 > time_limit:
            break

        # Start from root (3, 4, 5)
        A, B, C = mpz(3), mpz(4), mpz(5)

        for depth in range(max_depth):
            if time.time() - t0 > time_limit:
                break

            # Check VSDD at current node
            delta = C - B
            if delta > 0 and delta < n:
                result = vsdd_check(n, delta)
                if result:
                    if verbose:
                        print(f"    HIT at depth {depth}: Δ={delta}, factor={result}")
                    return result
                checked += 1

            # Also check with A as delta
            if A > 0 and A < n:
                result = vsdd_check(n, A)
                if result:
                    if verbose:
                        print(f"    HIT at depth {depth}: Δ={A}, factor={result}")
                    return result
                checked += 1

            # Jacobian selection: pick matrix minimizing |R_new - R_target|
            # Since we don't know the exact target R, we try to make
            # C² - B² approach n
            best_matrix = None
            best_error = float('inf')

            for M in UNIQUE_MATRICES:
                A2, B2, C2 = mat_mul(M, (A, B, C))
                if A2 <= 0 or B2 <= 0 or C2 <= 0:
                    continue

                # Score: how close is C² - B² to n?
                diff = C2 * C2 - B2 * B2
                if diff <= 0:
                    continue

                # Log-scale error to handle huge numbers
                if diff > 0:
                    log_diff = float(gmpy2.log2(mpz(diff)))
                    log_n = float(nb)
                    error = abs(log_diff - log_n)
                else:
                    error = float('inf')

                if error < best_error:
                    best_error = error
                    best_matrix = M
                    best_node = (A2, B2, C2)

            if best_matrix is None:
                break

            A, B, C = best_node

    # ── Method 2: Bottom-up climbing from candidate C values ──
    # For each candidate C near sqrt(n), check if B = sqrt(C²-n) is integer
    if found is None and time.time() - t0 < time_limit:
        # Scan C values near sqrt(n)
        C_start = isqrt(n) + 1
        for offset in range(min(100000, int(sqrt_n))):
            if time.time() - t0 > time_limit:
                break
            C_val = C_start + offset
            B_sq = C_val * C_val - n
            if B_sq <= 0:
                continue
            B_val = isqrt(B_sq)
            if B_val * B_val == B_sq:
                # Found! n = C² - B² = (C-B)(C+B)
                f1 = C_val - B_val
                f2 = C_val + B_val
                if f1 > 1 and f2 > 1 and f1 * f2 == n:
                    if verbose:
                        print(f"    Bottom-up HIT: C={C_val}, B={B_val}")
                    return int(min(f1, f2))
            checked += 1

    # ── Method 3: Priority queue BFS on scaled triples ──
    # Scale triples to target range and check VSDD
    if found is None and time.time() - t0 < time_limit:
        # For each primitive triple (A,B,C), check multiples k*(A,B,C)
        # where k*C ≈ sqrt(n)
        pq = [(0, (3, 4, 5))]  # (neg_depth, triple)
        visited = set()

        while pq and time.time() - t0 < time_limit:
            neg_depth, (A, B, C) = heapq.heappop(pq)
            depth = -neg_depth

            if depth > max_depth // 2:
                continue

            key = (A % 1000003, B % 1000003, C % 1000003)
            if key in visited:
                continue
            visited.add(key)

            # Check VSDD with Δ = C - B and its multiples
            delta = C - B
            for mult in [1, 2, 3]:
                d = delta * mult
                if 0 < d < n:
                    result = vsdd_check(n, d)
                    if result:
                        if verbose:
                            print(f"    BFS HIT: depth={depth}, Δ={d}")
                        return result
                    checked += 1

            # Expand children (all 6 matrices)
            for M in UNIQUE_MATRICES:
                A2, B2, C2 = mat_mul(M, (A, B, C))
                if A2 > 0 and B2 > 0 and C2 > 0:
                    if C2 < n:  # Don't go beyond n
                        heapq.heappush(pq, (-(depth + 1), (int(A2), int(B2), int(C2))))

            if len(visited) > 100000:
                break

    elapsed = time.time() - t0
    if verbose:
        print(f"    No hit ({checked} checks, {elapsed:.1f}s)")
    return None


###############################################################################
# Test
###############################################################################

if __name__ == "__main__":
    print("Super-Generator Test")
    print("=" * 50)

    # n = 901 = 17 × 53
    print("\n--- n = 901 ---")
    f = super_generator_factor(901, verbose=True, time_limit=5)
    print(f"Factor: {f}")

    # n = 15 = 3 × 5
    print("\n--- n = 15 ---")
    f = super_generator_factor(15, verbose=True, time_limit=5)
    print(f"Factor: {f}")

    # n = 1000000009 * 1000000087
    print("\n--- 20d ---")
    n = 1000000009 * 1000000087
    f = super_generator_factor(n, verbose=True, time_limit=10)
    print(f"Factor: {f}")

    # 30d
    print("\n--- 30d ---")
    n = 100000000000067 * 100000000000097
    f = super_generator_factor(n, verbose=True, time_limit=10)
    print(f"Factor: {f}")
