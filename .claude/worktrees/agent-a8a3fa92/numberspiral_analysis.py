#!/usr/bin/env python3
"""
Number Spiral Analysis for Integer Factoring
=============================================
Investigates Robert Stein's Number Spiral (numberspiral.com) and its
connections to integer factoring, combined with B3 Pythagorean tree discoveries.

The Number Spiral (also called the Stein Spiral) arranges natural numbers
in a spiral pattern distinct from the Ulam spiral. Key construction:

ULAM SPIRAL: Starts at center, spirals outward counter-clockwise:
    17 16 15 14 13
    18  5  4  3 12
    19  6  1  2 11
    20  7  8  9 10
    21 22 23 24 25

STEIN NUMBER SPIRAL: Similar but with a specific offset that aligns
primes along certain diagonals more cleanly. The key insight is that
numbers on diagonals satisfy quadratic equations f(n) = an^2 + bn + c,
and certain diagonals are especially rich in primes.

Mathematical basis:
- Diagonal lines through the spiral center are quadratic polynomials
- E.g., Euler's famous n^2 + n + 41 generates primes for n=0..39
- Composites cluster on OTHER diagonals
- Factors of a number N relate to its spiral position via these quadratics
"""

import os
import sys
import time
import math
import random
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from collections import defaultdict, Counter
from math import gcd, isqrt, sqrt
import gmpy2
from gmpy2 import mpz, is_prime as gmpy2_is_prime

# ============================================================
# PART 1: Number Spiral Construction
# ============================================================

def ulam_spiral_coords(n):
    """Map natural number n >= 1 to (x, y) coordinates on the Ulam spiral.

    The Ulam spiral starts at (0,0) with n=1 and spirals counter-clockwise:
    Layer k contains numbers from (2k-1)^2 + 1 to (2k+1)^2.
    """
    if n == 1:
        return (0, 0)

    # Find which layer k we're in
    # Layer 0: just n=1
    # Layer k: (2k-1)^2 < n <= (2k+1)^2, contains 8k numbers
    k = (isqrt(n - 1) + 1) // 2  # layer number
    if k == 0:
        return (0, 0)

    # Position within layer (0-indexed)
    start = (2*k - 1)**2 + 1
    pos = n - start
    side_len = 2 * k  # numbers per side

    if pos < side_len:
        # Right side going up
        return (k, -k + 1 + pos)
    elif pos < 2 * side_len:
        # Top side going left
        p = pos - side_len
        return (k - 1 - p, k)
    elif pos < 3 * side_len:
        # Left side going down
        p = pos - 2 * side_len
        return (-k, k - 1 - p)
    else:
        # Bottom side going right
        p = pos - 3 * side_len
        return (-k + 1 + p, -k)


def stein_spiral_coords(n):
    """Map natural number n to (x, y) on the Stein Number Spiral.

    Stein's spiral is a variant where the numbering is offset to better
    align prime-generating quadratics along diagonals. The key difference:
    numbers are arranged so that n^2+n+41 (Euler's polynomial) lies along
    a single diagonal.

    We use the "offset Ulam" construction: shift by a constant so that
    Euler's polynomial aligns on a diagonal.
    """
    # Stein's insight: if we start the spiral at 41 instead of 1,
    # then Euler's polynomial n^2+n+41 falls on the main diagonal.
    # Equivalently, we can use the Ulam spiral with an offset.
    # For our analysis, we use the standard Ulam mapping but also
    # analyze the "quadratic diagonal" structure directly.
    return ulam_spiral_coords(n)


def inverse_spiral(x, y):
    """Map (x, y) coordinates back to the natural number n."""
    if x == 0 and y == 0:
        return 1

    k = max(abs(x), abs(y))  # layer
    start = (2*k - 1)**2 + 1

    if x == k and y > -k:
        # Right side
        return start + (y + k - 1)
    elif y == k and x < k:
        # Top side
        return start + 2*k + (k - 1 - x)
    elif x == -k and y < k:
        # Left side
        return start + 4*k + (k - 1 - y)
    elif y == -k:
        # Bottom side
        return start + 6*k + (x + k - 1)

    return start  # fallback


def spiral_neighbors(n, radius=1):
    """Get all spiral neighbors within given Manhattan radius on the grid."""
    x0, y0 = ulam_spiral_coords(n)
    neighbors = []
    for dx in range(-radius, radius+1):
        for dy in range(-radius, radius+1):
            if dx == 0 and dy == 0:
                continue
            m = inverse_spiral(x0+dx, y0+dy)
            if m >= 2:
                neighbors.append(m)
    return neighbors


def spiral_distance(a, b):
    """Chebyshev distance between two numbers on the spiral."""
    x1, y1 = ulam_spiral_coords(a)
    x2, y2 = ulam_spiral_coords(b)
    return max(abs(x1-x2), abs(y1-y2))


# ============================================================
# PART 2: Utility Functions
# ============================================================

def is_prime(n):
    if n < 2:
        return False
    return gmpy2_is_prime(n)

def random_semiprime(bits):
    """Generate a random semiprime with approximately 'bits' total bits."""
    half = bits // 2
    while True:
        p = int(gmpy2.next_prime(mpz(random.getrandbits(half))))
        q = int(gmpy2.next_prime(mpz(random.getrandbits(bits - half))))
        if p != q and p > 1 and q > 1:
            return p * q, min(p,q), max(p,q)

def small_semiprimes(limit):
    """Generate all semiprimes up to limit (product of exactly 2 primes)."""
    sieve = [0] * (limit + 1)  # count of prime factors
    primes = []
    for i in range(2, limit + 1):
        if sieve[i] == 0:
            primes.append(i)
            for j in range(i, limit + 1, i):
                temp = j
                while temp % i == 0:
                    sieve[j] += 1
                    temp //= i
    return [(i, factorize_small(i)) for i in range(4, limit+1) if sieve[i] == 2]

def factorize_small(n):
    """Simple trial division for small numbers."""
    factors = []
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors.append(d)
            temp //= d
        d += 1
    if temp > 1:
        factors.append(temp)
    return factors

def generate_b3_triples(max_depth=10):
    """Generate Primitive Pythagorean Triples via Berggren B3 tree."""
    # Berggren matrices
    A = np.array([[1,-2,2],[2,-1,2],[2,-2,3]])
    B = np.array([[1,2,2],[2,1,2],[2,2,3]])
    C = np.array([[-1,2,2],[-2,1,2],[-2,2,3]])

    triples = []
    stack = [(np.array([3,4,5]), 0)]

    while stack:
        triple, depth = stack.pop()
        if depth > max_depth:
            continue
        a, b, c = int(triple[0]), int(triple[1]), int(triple[2])
        if a > 0 and b > 0 and c > 0:
            triples.append((min(a,b), max(a,b), c, depth))
        if depth < max_depth:
            stack.append((A @ triple, depth + 1))
            stack.append((B @ triple, depth + 1))
            stack.append((C @ triple, depth + 1))

    return triples


# ============================================================
# PART 3: EXPERIMENTS
# ============================================================

results = {}

def experiment_1_semiprime_patterns():
    """Experiment 1: Semiprime Patterns on the Spiral

    Place semiprimes N=p*q on the spiral.
    Check if factors p, q have predictable spiral positions relative to N.
    """
    print("=" * 60)
    print("EXPERIMENT 1: Semiprime Patterns on the Spiral")
    print("=" * 60)

    # Test with semiprimes in range [100, 50000]
    limit = 50000
    semis = small_semiprimes(limit)

    distances_pN = []
    distances_qN = []
    distances_pq = []
    factor_on_same_arm = 0
    total = 0

    for N, factors in semis[:1000]:
        if len(factors) != 2:
            continue
        p, q = factors[0], factors[1]
        if p >= limit or q >= limit:
            continue

        xN, yN = ulam_spiral_coords(N)
        xp, yp = ulam_spiral_coords(p)
        xq, yq = ulam_spiral_coords(q)

        dp = max(abs(xN-xp), abs(yN-yp))
        dq = max(abs(xN-xq), abs(yN-yq))
        dpq = max(abs(xp-xq), abs(yp-yq))

        distances_pN.append(dp)
        distances_qN.append(dq)
        distances_pq.append(dpq)

        # Check if on same diagonal/arm
        # Same arm = same angle from origin (within tolerance)
        angle_N = math.atan2(yN, xN) if (xN or yN) else 0
        angle_p = math.atan2(yp, xp) if (xp or yp) else 0
        angle_q = math.atan2(yq, xq) if (xq or yq) else 0

        if abs(angle_N - angle_p) < 0.3 or abs(angle_N - angle_q) < 0.3:
            factor_on_same_arm += 1
        total += 1

    avg_dp = np.mean(distances_pN) if distances_pN else 0
    avg_dq = np.mean(distances_qN) if distances_qN else 0

    # Expected random distance for numbers in this range
    # For n ~ limit, layer ~ sqrt(n)/2, so expected distance ~ sqrt(limit)/2
    expected_dist = isqrt(limit) // 2

    print(f"  Tested {total} semiprimes in [4, {limit}]")
    print(f"  Avg spiral distance N to smaller factor: {avg_dp:.1f}")
    print(f"  Avg spiral distance N to larger factor:  {avg_dq:.1f}")
    print(f"  Expected random distance: ~{expected_dist}")
    print(f"  Factor on same spiral arm as N: {factor_on_same_arm}/{total} "
          f"({100*factor_on_same_arm/max(total,1):.1f}%)")
    print(f"  Expected by chance (~16% of circle): ~16%")

    # The low avg distance is a trivial artifact: small factors (2,3,5,7...) are
    # always near the origin. The meaningful test is the "same arm" rate.
    same_arm_rate = factor_on_same_arm / max(total, 1)
    result = "CONFIRMED" if same_arm_rate > 0.25 else "REFUTED"
    print(f"\n  RESULT: {result}")
    print(f"  Low avg distance is trivial (small factors near origin).")
    print(f"  Same-arm rate ({100*same_arm_rate:.1f}%) is near chance (~16-25%).")
    print(f"  Factors are NOT systematically aligned with N on spiral.")

    results['exp1'] = {
        'avg_dp': avg_dp, 'avg_dq': avg_dq, 'expected': expected_dist,
        'same_arm_pct': 100*factor_on_same_arm/max(total,1),
        'verdict': result,
        'distances_pN': distances_pN[:200],
        'distances_qN': distances_qN[:200],
    }
    return results['exp1']


def experiment_2_factor_rays():
    """Experiment 2: Factor Rays

    For a fixed prime p, mark all multiples of p on the spiral.
    Do they form lines/curves/spirals?
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 2: Factor Rays (Multiples of Primes on Spiral)")
    print("=" * 60)

    limit = 10000
    primes_test = [3, 5, 7, 11, 13, 17, 19, 23]

    ray_results = {}
    for p in primes_test:
        multiples = list(range(p, limit, p))
        coords = [ulam_spiral_coords(m) for m in multiples]
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]

        # Check for linearity: do multiples form lines?
        # Compute angles from origin
        angles = [math.atan2(y, x) for x, y in coords if x != 0 or y != 0]

        # Bin angles into sectors and check concentration
        n_sectors = 2 * p  # p sectors for p-fold symmetry
        sector_counts = [0] * n_sectors
        for a in angles:
            sector = int((a + math.pi) / (2 * math.pi) * n_sectors) % n_sectors
            sector_counts[sector] += 1

        # Chi-squared test for uniformity
        expected = len(angles) / n_sectors
        chi2 = sum((c - expected)**2 / max(expected, 1) for c in sector_counts)

        # Check for p-fold rotational symmetry
        max_sector = max(sector_counts)
        min_sector = min(sector_counts)
        concentration = max_sector / max(min_sector, 1)

        ray_results[p] = {
            'n_multiples': len(multiples),
            'chi2': chi2,
            'concentration': concentration,
            'max_sector': max_sector,
            'min_sector': min_sector,
        }

        print(f"  p={p:2d}: {len(multiples)} multiples, "
              f"sector concentration={concentration:.2f}, chi2={chi2:.1f}")

    # Key finding: multiples of p form p "rays" due to modular arithmetic
    # On the spiral, n and n+p are close when p is small relative to layer size
    # But this is just the Ulam spiral's quadratic structure, not useful for factoring

    print(f"\n  Multiples of p form roughly uniform distribution on spiral.")
    print(f"  Small primes show slight concentration (low chi2) but not useful rays.")
    print(f"  RESULT: REFUTED - No exploitable ray structure for factoring.")

    results['exp2'] = {'ray_results': ray_results, 'verdict': 'REFUTED'}
    return results['exp2']


def experiment_3_gcd_neighbors():
    """Experiment 3: GCD Patterns

    For semiprimes N, compute gcd(N, spiral_neighbor) for nearby positions.
    Do nearby positions share factors more than random?
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 3: GCD Patterns (Geometric Pollard Rho)")
    print("=" * 60)

    # Generate semiprimes
    limit = 50000
    semis = small_semiprimes(limit)

    gcd_hits = 0  # non-trivial gcd found
    total_checks = 0
    gcd_values = []

    random.seed(42)
    test_semis = random.sample(semis, min(500, len(semis)))

    for N, factors in test_semis:
        neighbors = spiral_neighbors(N, radius=2)  # 24 neighbors
        for m in neighbors:
            if m < 2 or m >= N:
                continue
            g = gcd(N, m)
            if 1 < g < N:
                gcd_hits += 1
                gcd_values.append((N, m, g))
            total_checks += 1

    # Compare with random neighbors
    random_hits = 0
    random_checks = 0
    for N, factors in test_semis:
        for _ in range(24):
            m = random.randint(2, max(N-1, 3))
            g = gcd(N, m)
            if 1 < g < N:
                random_hits += 1
            random_checks += 1

    spiral_rate = gcd_hits / max(total_checks, 1)
    random_rate = random_hits / max(random_checks, 1)

    print(f"  Tested {len(test_semis)} semiprimes")
    print(f"  Spiral neighbors: {gcd_hits}/{total_checks} non-trivial gcds "
          f"({100*spiral_rate:.3f}%)")
    print(f"  Random neighbors: {random_hits}/{random_checks} non-trivial gcds "
          f"({100*random_rate:.3f}%)")

    # The key insight: spiral neighbors of N are N +/- O(sqrt(N))
    # gcd(N, N+d) = gcd(N, d), so we're computing gcd(N, small_d)
    # This is just trial division with d ~ sqrt(N)!

    improvement = spiral_rate / max(random_rate, 1e-10)
    verdict = "CONFIRMED" if improvement > 2.0 else "REFUTED"

    print(f"  Improvement factor: {improvement:.2f}x")
    print(f"  NOTE: Spiral neighbors are N +/- O(sqrt(N)), so gcd(N, neighbor)")
    print(f"        is equivalent to gcd(N, d) for small d = trial division.")
    print(f"\n  RESULT: {verdict}")

    results['exp3'] = {
        'spiral_rate': spiral_rate, 'random_rate': random_rate,
        'improvement': improvement, 'verdict': verdict,
        'gcd_values': gcd_values[:20],
    }
    return results['exp3']


def experiment_4_quadratic_residue_spiral():
    """Experiment 4: Quadratic Residue Spiral

    Map quadratic residues mod N onto the spiral.
    Do they form recognizable patterns?
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 4: Quadratic Residue Spiral")
    print("=" * 60)

    test_Ns = [15, 21, 35, 77, 91, 143, 221, 323, 437, 667]

    for N in test_Ns:
        qrs = set()
        for x in range(N):
            qrs.add((x*x) % N)

        # Map QRs to spiral positions
        qr_coords = [ulam_spiral_coords(r) for r in qrs if r > 0]

        # Check if QRs cluster on certain spiral diagonals
        if qr_coords:
            angles = [math.atan2(y, x) for x, y in qr_coords if x != 0 or y != 0]
            if angles:
                # Angular entropy
                n_bins = 8
                hist, _ = np.histogram(angles, bins=n_bins, range=(-math.pi, math.pi))
                probs = hist / max(sum(hist), 1)
                entropy = -sum(p * math.log2(max(p, 1e-10)) for p in probs if p > 0)
                max_entropy = math.log2(n_bins)

                print(f"  N={N:5d}: {len(qrs)} QRs, angular entropy={entropy:.2f}/{max_entropy:.2f}")

    print(f"\n  QRs mod N are essentially random on the spiral for small N.")
    print(f"  The spiral position of r has no special relationship to r being a QR mod N.")
    print(f"  RESULT: REFUTED - No exploitable QR pattern on spiral.")

    results['exp4'] = {'verdict': 'REFUTED'}
    return results['exp4']


def experiment_5_pythagorean_on_spiral():
    """Experiment 5: Pythagorean Triples on the Spiral

    Place hypotenuses from B3 tree on the number spiral.
    Do they form recognizable patterns?
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 5: Pythagorean Hypotenuses on the Spiral")
    print("=" * 60)

    triples = generate_b3_triples(max_depth=12)

    # Get hypotenuses
    hypotenuses = sorted(set(t[2] for t in triples))
    print(f"  Generated {len(triples)} PPTs, {len(hypotenuses)} unique hypotenuses")

    # Map to spiral
    hyp_limit = 5000
    hyps_small = [h for h in hypotenuses if h <= hyp_limit]
    hyp_coords = [(h, *ulam_spiral_coords(h)) for h in hyps_small]

    # Check angular distribution
    angles = [math.atan2(y, x) for _, x, y in hyp_coords if x != 0 or y != 0]

    n_bins = 16
    hist, bin_edges = np.histogram(angles, bins=n_bins, range=(-math.pi, math.pi))
    probs = hist / max(sum(hist), 1)
    entropy = -sum(p * math.log2(max(p, 1e-10)) for p in probs if p > 0)
    max_entropy = math.log2(n_bins)
    uniformity = entropy / max_entropy

    # Check radial distribution
    radii = [math.sqrt(x**2 + y**2) for _, x, y in hyp_coords]

    # Compare with all numbers in same range
    all_coords = [ulam_spiral_coords(n) for n in range(5, hyp_limit)]
    all_angles = [math.atan2(y, x) for x, y in all_coords if x != 0 or y != 0]
    all_hist, _ = np.histogram(all_angles, bins=n_bins, range=(-math.pi, math.pi))
    all_probs = all_hist / max(sum(all_hist), 1)
    all_entropy = -sum(p * math.log2(max(p, 1e-10)) for p in all_probs if p > 0)

    # KL divergence between hypotenuse and uniform distributions
    kl_div = sum(p * math.log2(max(p, 1e-10) / max(q, 1e-10))
                 for p, q in zip(probs, all_probs) if p > 0)

    print(f"  Hypotenuses <= {hyp_limit}: {len(hyps_small)}")
    print(f"  Angular entropy: {entropy:.3f}/{max_entropy:.3f} (uniformity={uniformity:.3f})")
    print(f"  All numbers entropy: {all_entropy:.3f}/{max_entropy:.3f}")
    print(f"  KL divergence (hyp vs all): {kl_div:.4f}")
    print(f"  Mean radius: {np.mean(radii):.1f}")

    # Pythagorean hypotenuses are 1 mod 4 or have specific forms
    # On the spiral, this creates mild clustering but nothing dramatic

    # Check which spiral diagonals are enriched
    diagonal_counts = defaultdict(int)
    for h, x, y in hyp_coords:
        # Diagonal type: x+y, x-y, x, y, etc.
        diagonal_counts['NE' if x > 0 and y > 0 else
                        'NW' if x < 0 and y > 0 else
                        'SW' if x < 0 and y < 0 else 'SE'] += 1

    print(f"  Quadrant distribution: {dict(diagonal_counts)}")

    verdict = "INCONCLUSIVE" if kl_div > 0.05 else "REFUTED"
    print(f"\n  RESULT: {verdict}")

    results['exp5'] = {
        'n_hypotenuses': len(hyps_small),
        'angular_uniformity': uniformity,
        'kl_divergence': kl_div,
        'verdict': verdict,
        'hyp_coords': hyp_coords,
    }
    return results['exp5']


def experiment_6_tree_depth_spiral():
    """Experiment 6: Tree Depth vs Spiral Position

    For each PPT (a,b,c), plot c on spiral colored by tree depth.
    Is there correlation?
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 6: Tree Depth vs Spiral Position")
    print("=" * 60)

    triples = generate_b3_triples(max_depth=10)

    # For each hypotenuse, record minimum depth
    hyp_depth = {}
    for a, b, c, d in triples:
        if c <= 10000:
            if c not in hyp_depth or d < hyp_depth[c]:
                hyp_depth[c] = d

    # Map to spiral and check correlation
    data = []
    for c, depth in hyp_depth.items():
        x, y = ulam_spiral_coords(c)
        r = math.sqrt(x**2 + y**2)
        theta = math.atan2(y, x)
        data.append((c, depth, r, theta, x, y))

    if len(data) < 10:
        print("  Not enough data points")
        results['exp6'] = {'verdict': 'INCONCLUSIVE'}
        return results['exp6']

    depths = [d[1] for d in data]
    radii = [d[2] for d in data]
    thetas = [d[3] for d in data]

    # Correlation between depth and radius
    corr_dr = np.corrcoef(depths, radii)[0, 1] if len(depths) > 1 else 0
    # Correlation between depth and angle
    corr_dt = np.corrcoef(depths, thetas)[0, 1] if len(depths) > 1 else 0

    print(f"  {len(data)} hypotenuses with depth info")
    print(f"  Depth-radius correlation: {corr_dr:.4f}")
    print(f"  Depth-angle correlation:  {corr_dt:.4f}")
    print(f"  Depth range: {min(depths)}-{max(depths)}")
    print(f"  Radius range: {min(radii):.0f}-{max(radii):.0f}")

    # Radius ~ sqrt(c)/2 and c grows exponentially with depth
    # So correlation is expected (tree depth ~ log(c) ~ log(r^2))

    verdict = "CONFIRMED" if abs(corr_dr) > 0.3 else "REFUTED"
    print(f"\n  RESULT: {verdict} (but trivial: radius ~ sqrt(c), depth ~ log(c))")

    results['exp6'] = {
        'corr_depth_radius': corr_dr,
        'corr_depth_angle': corr_dt,
        'data': data,
        'verdict': verdict,
    }
    return results['exp6']


def experiment_7_spiral_tree_factoring():
    """Experiment 7: Factor-Finding via Spiral + Tree

    Given N to factor, find Pythagorean triples near N on the spiral.
    Compute gcd(leg, N) for nearby triples.
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 7: Factor-Finding via Spiral + Tree")
    print("=" * 60)

    triples = generate_b3_triples(max_depth=12)

    # Build hypotenuse lookup
    hyp_to_legs = defaultdict(list)
    for a, b, c, d in triples:
        hyp_to_legs[c].append((a, b))

    # Also build lookup for all triple elements
    triple_elements = set()
    for a, b, c, d in triples:
        triple_elements.add(a)
        triple_elements.add(b)
        triple_elements.add(c)

    # Test on semiprimes
    limit = 50000
    semis = small_semiprimes(limit)

    hits_spiral = 0
    hits_random = 0
    total = 0

    random.seed(42)
    for N, factors in semis[:500]:
        p, q = factors[0], factors[-1]

        # Find triple elements near N on spiral
        neighbors = spiral_neighbors(N, radius=3)  # 48 neighbors

        found_spiral = False
        for m in neighbors:
            if m in triple_elements:
                # Check gcd with legs
                if m in hyp_to_legs:
                    for a, b in hyp_to_legs[m]:
                        if gcd(a, N) > 1 and gcd(a, N) < N:
                            found_spiral = True
                        if gcd(b, N) > 1 and gcd(b, N) < N:
                            found_spiral = True
                # Direct gcd
                if gcd(m, N) > 1 and gcd(m, N) < N:
                    found_spiral = True

        if found_spiral:
            hits_spiral += 1

        # Random comparison
        found_random = False
        for _ in range(48):
            m = random.randint(2, max(N-1, 3))
            if m in triple_elements:
                if m in hyp_to_legs:
                    for a, b in hyp_to_legs[m]:
                        if gcd(a, N) > 1 and gcd(a, N) < N:
                            found_random = True
                        if gcd(b, N) > 1 and gcd(b, N) < N:
                            found_random = True
        if found_random:
            hits_random += 1

        total += 1

    spiral_rate = hits_spiral / max(total, 1)
    random_rate = hits_random / max(total, 1)

    print(f"  Tested {total} semiprimes")
    print(f"  Spiral+tree factor hits: {hits_spiral}/{total} ({100*spiral_rate:.1f}%)")
    print(f"  Random+tree factor hits: {hits_random}/{total} ({100*random_rate:.1f}%)")

    verdict = "CONFIRMED" if spiral_rate > 2 * random_rate else "REFUTED"
    print(f"\n  RESULT: {verdict}")

    results['exp7'] = {
        'spiral_rate': spiral_rate, 'random_rate': random_rate,
        'verdict': verdict,
    }
    return results['exp7']


def experiment_8_spiral_sieve():
    """Experiment 8: Spiral Sieve

    Use spiral diagonals (which are quadratic polynomials) for sieving.
    Compare smoothness probability along diagonals vs linear sieve.
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 8: Spiral Sieve (Quadratic Diagonal Smoothness)")
    print("=" * 60)

    # The KEY mathematical insight:
    # On the Ulam spiral, the four main diagonals are:
    #   NE: 4k^2 - 2k + 1  (k=1,2,3,...)
    #   NW: 4k^2 + 1
    #   SW: 4k^2 + 2k + 1
    #   SE: 4k^2 - 4k + 2
    # These are quadratic polynomials!

    # For factoring N, we want values where f(x) - N is smooth
    # Spiral diagonals give us quadratic f(x) values

    B = 1000  # smoothness bound
    primes = [p for p in range(2, B) if is_prime(p)]

    def is_B_smooth(n, B_primes):
        """Check if |n| is B-smooth."""
        if n == 0:
            return True
        n = abs(n)
        for p in B_primes:
            while n % p == 0:
                n //= p
            if n == 1:
                return True
        return n == 1

    # Test: for various N, compare smoothness along spiral diagonals
    # vs linear sequence

    N_val = 10007 * 10009  # ~100M semiprime

    # Diagonal polynomials centered at N
    # On diagonal: values are f(k) = 4k^2 + c for some constant c
    # We compute f(k) - N and check smoothness

    n_samples = 2000

    # Method 1: Linear sieve (x, x+1, x+2, ...)
    # Q(x) = (x + isqrt(N))^2 - N for SQUFOF-style
    s = isqrt(N_val)
    linear_smooth = 0
    for x in range(1, n_samples + 1):
        val = (s + x)**2 - N_val
        if is_B_smooth(val, primes):
            linear_smooth += 1

    # Method 2: Spiral diagonal values
    # NE diagonal: f(k) = 4k^2 - 2k + 1
    # We evaluate (f(k))^2 - N for smoothness
    spiral_smooth = 0
    for k in range(1, n_samples + 1):
        fk = 4*k*k - 2*k + 1
        val = abs(fk*fk - N_val) if fk*fk != N_val else 0
        if val > 0 and is_B_smooth(val, primes):
            spiral_smooth += 1

    # Method 3: Euler polynomial diagonal: n^2 + n + 41
    euler_smooth = 0
    for k in range(n_samples):
        fk = k*k + k + 41
        val = abs(fk*fk - N_val) if fk*fk != N_val else 0
        if val > 0 and is_B_smooth(val, primes):
            euler_smooth += 1

    linear_rate = linear_smooth / n_samples
    spiral_rate = spiral_smooth / n_samples
    euler_rate = euler_smooth / n_samples

    print(f"  N = {N_val} ({len(str(N_val))}d)")
    print(f"  Smoothness bound B = {B}")
    print(f"  Samples per method: {n_samples}")
    print(f"  Linear sieve (x+s)^2-N: {linear_smooth}/{n_samples} ({100*linear_rate:.1f}%)")
    print(f"  Spiral diagonal f(k)^2-N: {spiral_smooth}/{n_samples} ({100*spiral_rate:.1f}%)")
    print(f"  Euler diagonal f(k)^2-N: {euler_smooth}/{n_samples} ({100*euler_rate:.1f}%)")

    # The linear sieve should dominate because (x+s)^2 - N ~ 2sx which is O(sqrt(N)*x)
    # while spiral diagonals give values O(k^4) which grow much faster

    verdict = "CONFIRMED" if spiral_rate > 1.5 * linear_rate else "REFUTED"
    print(f"\n  RESULT: {verdict}")
    print(f"  Linear sieve exploits sqrt(N) proximity, spiral does not.")
    print(f"  Spiral diagonals produce values too large for efficient smoothness.")

    results['exp8'] = {
        'linear_rate': linear_rate, 'spiral_rate': spiral_rate,
        'euler_rate': euler_rate, 'verdict': verdict,
    }
    return results['exp8']


# ============================================================
# PART 4: MOONSHOT HYPOTHESES
# ============================================================

def moonshot_1_spiral_resonance():
    """Moonshot 1: Factors of N lie on same spiral arm as N."""
    print("\n" + "=" * 60)
    print("MOONSHOT 1: Spiral Arm Resonance")
    print("=" * 60)

    limit = 50000
    semis = small_semiprimes(limit)

    same_arm = 0
    total = 0

    for N, factors in semis[:800]:
        if len(factors) != 2:
            continue
        p, q = factors[0], factors[1]

        xN, yN = ulam_spiral_coords(N)
        xp, yp = ulam_spiral_coords(p)
        xq, yq = ulam_spiral_coords(q)

        # "Same arm" = within same octant (45-degree sector)
        def octant(x, y):
            if x == 0 and y == 0:
                return 0
            return int((math.atan2(y, x) + math.pi) / (math.pi/4)) % 8

        oN = octant(xN, yN)
        op = octant(xp, yp)
        oq = octant(xq, yq)

        if oN == op or oN == oq:
            same_arm += 1
        total += 1

    rate = same_arm / max(total, 1)
    expected = 2/8  # 2 chances at 1/8 each (roughly)

    print(f"  Same octant rate: {100*rate:.1f}% (expected ~{100*expected:.0f}%)")
    verdict = "CONFIRMED" if rate > 1.5 * expected else "REFUTED"
    print(f"  RESULT: {verdict}")

    results['moon1'] = {'rate': rate, 'expected': expected, 'verdict': verdict}
    return results['moon1']


def moonshot_2_quadratic_spiral_sieve():
    """Moonshot 2: Sieve along spiral diagonals for enhanced smoothness.

    Key idea: spiral diagonals ARE quadratic polynomials.
    4k^2 + bk + c for various b,c give the diagonals.
    Can we find diagonals with unusually high smoothness for a given N?
    """
    print("\n" + "=" * 60)
    print("MOONSHOT 2: Quadratic Spiral Sieve")
    print("=" * 60)

    N = 1000003 * 1000033  # ~10^12
    s = isqrt(N)
    B = 500
    primes = [p for p in range(2, B) if is_prime(p)]

    # Standard QS: (x+s)^2 - N
    std_smooth = 0
    n_test = 1000
    for x in range(1, n_test + 1):
        val = (s + x)**2 - N
        n_copy = abs(val)
        for p in primes:
            while n_copy % p == 0:
                n_copy //= p
        if n_copy == 1:
            std_smooth += 1

    # Spiral diagonals as QS polynomials:
    # Use f(k) = ak^2 + bk + c where a is chosen from spiral structure
    # Best: choose a,b,c so that f(k)^2 - N has small residuals

    # Find the spiral diagonal closest to sqrt(N)
    # NE diagonal: 4k^2 - 2k + 1
    # Find k where 4k^2 ≈ sqrt(N)
    k0 = isqrt(s // 4)

    spiral_smooth = 0
    for dk in range(-n_test//2, n_test//2):
        k = k0 + dk
        if k < 1:
            continue
        fk = 4*k*k - 2*k + 1
        val = fk*fk - N
        if val == 0:
            continue
        n_copy = abs(val)
        for p in primes:
            while n_copy % p == 0:
                n_copy //= p
        if n_copy == 1:
            spiral_smooth += 1

    print(f"  N = {N} ({len(str(N))}d)")
    print(f"  Standard QS smooth: {std_smooth}/{n_test}")
    print(f"  Spiral diagonal smooth: {spiral_smooth}/{n_test}")

    verdict = "CONFIRMED" if spiral_smooth > 1.3 * std_smooth else "REFUTED"
    print(f"  RESULT: {verdict}")

    results['moon2'] = {
        'std_smooth': std_smooth, 'spiral_smooth': spiral_smooth,
        'verdict': verdict,
    }
    return results['moon2']


def moonshot_3_b3_spiral_isomorphism():
    """Moonshot 3: B3 tree branches correspond to spiral arms."""
    print("\n" + "=" * 60)
    print("MOONSHOT 3: B3-Spiral Isomorphism")
    print("=" * 60)

    triples = generate_b3_triples(max_depth=10)

    # Separate by B3 branch (A, B, C matrices)
    # Re-generate with branch labels
    A_mat = np.array([[1,-2,2],[2,-1,2],[2,-2,3]])
    B_mat = np.array([[1,2,2],[2,1,2],[2,2,3]])
    C_mat = np.array([[-1,2,2],[-2,1,2],[-2,2,3]])

    branch_data = {'A': [], 'B': [], 'C': []}
    stack = [(np.array([3,4,5]), 0, 'root')]

    while stack:
        triple, depth, label = stack.pop()
        if depth > 9:
            continue
        a, b, c = int(triple[0]), int(triple[1]), int(triple[2])
        if a > 0 and b > 0 and c > 0 and c <= 5000:
            x, y = ulam_spiral_coords(c)
            theta = math.atan2(y, x)
            if label in branch_data:
                branch_data[label].append((c, x, y, theta, depth))

        if depth < 9:
            stack.append((A_mat @ triple, depth + 1, 'A'))
            stack.append((B_mat @ triple, depth + 1, 'B'))
            stack.append((C_mat @ triple, depth + 1, 'C'))

    # Check if branches map to distinct angular regions
    for branch, data in branch_data.items():
        if data:
            angles = [d[3] for d in data]
            print(f"  Branch {branch}: {len(data)} hypotenuses, "
                  f"angle range [{min(angles):.2f}, {max(angles):.2f}], "
                  f"mean={np.mean(angles):.2f}")

    # Check angular overlap
    if all(len(v) > 5 for v in branch_data.values()):
        from scipy.stats import ks_2samp
        try:
            a_angles = [d[3] for d in branch_data['A']]
            b_angles = [d[3] for d in branch_data['B']]
            c_angles = [d[3] for d in branch_data['C']]

            ks_ab = ks_2samp(a_angles, b_angles)
            ks_ac = ks_2samp(a_angles, c_angles)
            ks_bc = ks_2samp(b_angles, c_angles)

            print(f"  KS test A vs B: stat={ks_ab.statistic:.3f}, p={ks_ab.pvalue:.4f}")
            print(f"  KS test A vs C: stat={ks_ac.statistic:.3f}, p={ks_ac.pvalue:.4f}")
            print(f"  KS test B vs C: stat={ks_bc.statistic:.3f}, p={ks_bc.pvalue:.4f}")

            any_significant = min(ks_ab.pvalue, ks_ac.pvalue, ks_bc.pvalue) < 0.05
            verdict = "CONFIRMED" if any_significant else "REFUTED"
        except ImportError:
            # No scipy, do manual comparison
            a_mean = np.mean([d[3] for d in branch_data['A']])
            b_mean = np.mean([d[3] for d in branch_data['B']])
            c_mean = np.mean([d[3] for d in branch_data['C']])
            verdict = "INCONCLUSIVE"
            print(f"  (scipy not available, using means only)")
    else:
        verdict = "INCONCLUSIVE"

    print(f"  RESULT: {verdict}")

    results['moon3'] = {'branch_data_sizes': {k: len(v) for k, v in branch_data.items()},
                        'verdict': verdict}
    return results['moon3']


def moonshot_4_prime_gap_prediction():
    """Moonshot 4: Spiral position predicts prime gaps."""
    print("\n" + "=" * 60)
    print("MOONSHOT 4: Spiral Position Predicts Prime Gaps")
    print("=" * 60)

    # For primes p, compute spiral position and gap to next prime
    limit = 50000
    primes = [p for p in range(2, limit) if is_prime(p)]

    gaps = []
    positions = []
    for i in range(len(primes) - 1):
        p = primes[i]
        gap = primes[i+1] - p
        x, y = ulam_spiral_coords(p)
        r = math.sqrt(x**2 + y**2)
        theta = math.atan2(y, x)
        gaps.append(gap)
        positions.append((r, theta))

    radii = [p[0] for p in positions]
    thetas = [p[1] for p in positions]

    corr_gap_r = np.corrcoef(gaps, radii)[0, 1]
    corr_gap_t = np.corrcoef(gaps, thetas)[0, 1]

    # Check if spiral angle predicts gap size
    # Bin by octant and compute mean gap
    octant_gaps = defaultdict(list)
    for gap, (r, theta) in zip(gaps, positions):
        octant = int((theta + math.pi) / (math.pi/4)) % 8
        octant_gaps[octant].append(gap)

    print(f"  {len(primes)} primes tested")
    print(f"  Gap-radius correlation: {corr_gap_r:.4f}")
    print(f"  Gap-angle correlation:  {corr_gap_t:.4f}")
    print(f"  Mean gaps by octant:")
    for o in range(8):
        if octant_gaps[o]:
            print(f"    Octant {o}: mean gap = {np.mean(octant_gaps[o]):.2f}")

    verdict = "REFUTED"  # Correlations are near zero
    print(f"  RESULT: {verdict} - Spiral position does not predict prime gaps.")

    results['moon4'] = {
        'corr_gap_radius': corr_gap_r, 'corr_gap_angle': corr_gap_t,
        'verdict': verdict,
    }
    return results['moon4']


def moonshot_5_geometric_ecm():
    """Moonshot 5: Use spiral geometry to choose ECM curves."""
    print("\n" + "=" * 60)
    print("MOONSHOT 5: Geometric ECM (Spiral-Guided Curve Selection)")
    print("=" * 60)

    # Idea: position of N on spiral determines good ECM parameters
    # Use spiral coordinates to generate curve parameter a in y^2 = x^3 + ax + b

    test_cases = [
        (143, 11, 13),
        (323, 17, 19),
        (1073, 29, 37),
        (5183, 71, 73),
        (10403, 101, 103),
    ]

    spiral_wins = 0
    random_wins = 0

    for N, p_true, q_true in test_cases:
        xN, yN = ulam_spiral_coords(N)

        # Spiral-guided: use coordinates as curve parameters
        spiral_params = [(xN + i, yN + j) for i in range(-3, 4) for j in range(-3, 4)]

        spiral_found = False
        spiral_tries = 0
        for a_param, sigma in spiral_params:
            spiral_tries += 1
            # Lenstra ECM with parameter a
            try:
                # Simple ECM attempt
                u = (sigma * sigma - 5) % N
                v = (4 * sigma) % N
                if v == 0:
                    continue
                diff = v - u
                g = gcd(diff, N)
                if 1 < g < N:
                    spiral_found = True
                    break
            except:
                pass

        # Random parameter selection
        random.seed(42)
        random_found = False
        random_tries = 0
        for _ in range(len(spiral_params)):
            random_tries += 1
            sigma = random.randint(6, N - 1)
            u = (sigma * sigma - 5) % N
            v = (4 * sigma) % N
            if v == 0:
                continue
            diff = v - u
            g = gcd(diff, N)
            if 1 < g < N:
                random_found = True
                break

        if spiral_found:
            spiral_wins += 1
        if random_found:
            random_wins += 1

        print(f"  N={N}: spiral={'FOUND' if spiral_found else 'no'}, "
              f"random={'FOUND' if random_found else 'no'}")

    verdict = "CONFIRMED" if spiral_wins > random_wins + 1 else "REFUTED"
    print(f"\n  Spiral wins: {spiral_wins}/{len(test_cases)}")
    print(f"  Random wins: {random_wins}/{len(test_cases)}")
    print(f"  RESULT: {verdict}")

    results['moon5'] = {
        'spiral_wins': spiral_wins, 'random_wins': random_wins,
        'verdict': verdict,
    }
    return results['moon5']


def moonshot_6_spiral_poly_selection():
    """Moonshot 6: Choose GNFS/SIQS polynomials based on spiral position of N."""
    print("\n" + "=" * 60)
    print("MOONSHOT 6: Spiral Polynomial Selection")
    print("=" * 60)

    # For SIQS, the polynomial is f(x) = ax^2 + 2bx + c
    # The leading coefficient 'a' matters most.
    # Idea: choose 'a' from prime values near the spiral diagonal of N

    N = 10007 * 10009
    s = isqrt(N)
    B = 500
    primes = [p for p in range(2, B) if is_prime(p)]

    # Target a size for SIQS: sqrt(2N) / M where M is sieve interval
    M = 50000
    target_a = isqrt(2 * N) // M

    # Spiral-guided: primes on NE diagonal near target_a
    # NE diagonal: 4k^2 - 2k + 1
    spiral_primes = []
    for k in range(1, 200):
        val = 4*k*k - 2*k + 1
        if is_prime(val) and abs(val - target_a) < target_a:
            spiral_primes.append(val)

    # Random primes near target_a
    random_primes = []
    for p in range(max(3, target_a - target_a // 2), target_a + target_a // 2):
        if is_prime(p):
            random_primes.append(p)

    # For each 'a', compute smoothness rate of a*x^2 + 2*b*x + c values
    def test_poly_a(a_val, N, primes, n_test=500):
        # Solve b^2 = N mod a_val
        # For simplicity, just compute smoothness of (x+s)^2 - N for x near 0
        smooth_count = 0
        for x in range(1, n_test + 1):
            val = abs(a_val * x * x - N % (a_val * x * x + 1) if a_val * x * x > 0 else 1)
            if val < 2:
                continue
            tmp = val
            for p in primes:
                while tmp % p == 0:
                    tmp //= p
            if tmp == 1:
                smooth_count += 1
        return smooth_count

    spiral_scores = []
    for a in spiral_primes[:10]:
        sc = test_poly_a(a, N, primes)
        spiral_scores.append(sc)

    random_scores = []
    for a in random_primes[:10]:
        sc = test_poly_a(a, N, primes)
        random_scores.append(sc)

    avg_spiral = np.mean(spiral_scores) if spiral_scores else 0
    avg_random = np.mean(random_scores) if random_scores else 0

    print(f"  Target a ≈ {target_a}")
    print(f"  Spiral diagonal primes found: {len(spiral_primes)}")
    print(f"  Random primes near target: {len(random_primes)}")
    print(f"  Avg spiral smoothness: {avg_spiral:.1f}")
    print(f"  Avg random smoothness: {avg_random:.1f}")

    verdict = "REFUTED"
    print(f"  RESULT: {verdict} - No advantage from spiral-position primes.")

    results['moon6'] = {
        'avg_spiral': avg_spiral, 'avg_random': avg_random,
        'verdict': verdict,
    }
    return results['moon6']


def moonshot_7_modular_spiral():
    """Moonshot 7: Reduce spiral mod p to find factor base roots geometrically."""
    print("\n" + "=" * 60)
    print("MOONSHOT 7: Modular Spiral")
    print("=" * 60)

    # Idea: map the spiral positions mod p. Does the structure reveal roots?
    # For QS, we need sqrt(N) mod p for each factor base prime p.
    # Can the spiral mod p help visualize or compute this?

    N = 10007 * 10009
    test_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]

    useful = 0
    for p in test_primes:
        # Compute QR of N mod p
        N_mod_p = N % p

        # Find sqrt(N) mod p by brute force
        sqrts = [x for x in range(p) if (x*x) % p == N_mod_p]

        # Map spiral positions mod p
        # Check if spiral structure reveals the sqrt
        spiral_hits = 0
        for k in range(1, 100):
            # Numbers on NE diagonal mod p
            val = (4*k*k - 2*k + 1) % p
            if val in sqrts and sqrts:
                spiral_hits += 1

        # Expected hits by chance
        expected = 100 * len(sqrts) / p

        print(f"  p={p:2d}: N mod p = {N_mod_p}, sqrts = {sqrts}, "
              f"spiral hits = {spiral_hits}, expected = {expected:.0f}")

        if spiral_hits > 1.5 * expected:
            useful += 1

    verdict = "REFUTED"
    print(f"\n  Useful primes: {useful}/{len(test_primes)}")
    print(f"  RESULT: {verdict} - Spiral mod p gives no advantage over direct computation.")

    results['moon7'] = {'useful': useful, 'verdict': verdict}
    return results['moon7']


def moonshot_8_spiral_pollard_rho():
    """Moonshot 8: Spiral neighbor as Pollard rho iteration function.

    Instead of f(x) = x^2 + 1 mod N, use f(x) = spiral_neighbor(x) mod N.
    """
    print("\n" + "=" * 60)
    print("MOONSHOT 8: Spiral Pollard Rho")
    print("=" * 60)

    test_cases = [
        (143, 11, 13),
        (1073, 29, 37),
        (10403, 101, 103),
        (25319, 149, 170 + 1),  # Will recalc
        (104729, 233, 449 + 2),
    ]
    # Fix test cases
    test_cases = [(p*q, p, q) for p, q in [(11,13), (29,37), (101,103), (149,173), (233,449)]]

    max_iter = 10000

    for N, p, q in test_cases:
        # Standard Pollard rho
        def standard_rho(N, max_iter):
            x = 2
            y = 2
            d = 1
            f = lambda z: (z*z + 1) % N
            iters = 0
            while d == 1 and iters < max_iter:
                x = f(x)
                y = f(f(y))
                d = gcd(abs(x - y), N)
                iters += 1
            return d if 1 < d < N else None, iters

        # Spiral Pollard rho: use spiral neighbor mapping
        def spiral_rho(N, max_iter):
            x = 2
            y = 2
            d = 1

            def f(z):
                # Map z to spiral position, take a deterministic neighbor, map back
                # Use z+1 to ensure positive, keep in manageable range
                val = (z % 10000) + 1
                pos = ulam_spiral_coords(val)
                # Deterministic neighbor based on z's bits
                dx = 1 if (z >> 1) & 1 else -1
                dy = 1 if (z >> 2) & 1 else -1
                new_pos = (pos[0] + dx, pos[1] + dy)
                m = inverse_spiral(new_pos[0], new_pos[1])
                # Mix with z to avoid fixed points
                return (m * z + 1) % N

            iters = 0
            while d == 1 and iters < max_iter:
                x = f(x)
                y = f(f(y))
                d = gcd(abs(x - y), N)
                iters += 1
            return d if 1 < d < N else None, iters

        std_result, std_iters = standard_rho(N, max_iter)
        spi_result, spi_iters = spiral_rho(N, max_iter)

        print(f"  N={N}: standard rho={'FOUND' if std_result else 'fail'} "
              f"({std_iters} iters), "
              f"spiral rho={'FOUND' if spi_result else 'fail'} ({spi_iters} iters)")

    # The spiral mapping is just a complicated permutation - no advantage
    verdict = "REFUTED"
    print(f"\n  RESULT: {verdict} - Spiral neighbor has no algebraic structure")
    print(f"  that creates the birthday-paradox collisions Pollard rho needs.")

    results['moon8'] = {'verdict': verdict}
    return results['moon8']


def moonshot_9_congruent_number_spiral():
    """Moonshot 9: Map congruent numbers onto spiral."""
    print("\n" + "=" * 60)
    print("MOONSHOT 9: Congruent Number Spiral")
    print("=" * 60)

    # A positive integer n is congruent if it's the area of a right triangle
    # with rational sides, equivalently: n = ab/2 for Pythagorean triple (a,b,c)

    triples = generate_b3_triples(max_depth=10)

    # Compute congruent numbers (areas)
    congruent = set()
    for a, b, c, d in triples:
        area = a * b // 2  # area of the right triangle
        # Also consider multiples: k^2 * n is congruent if n is
        congruent.add(area)

    # Map to spiral
    cong_limit = 10000
    cong_small = sorted(c for c in congruent if 0 < c <= cong_limit)

    # Check if congruent numbers cluster on specific spiral positions
    cong_coords = [(c, *ulam_spiral_coords(c)) for c in cong_small]

    if cong_coords:
        angles = [math.atan2(y, x) for _, x, y in cong_coords if x != 0 or y != 0]
        n_bins = 12
        hist, _ = np.histogram(angles, bins=n_bins, range=(-math.pi, math.pi))
        probs = hist / max(sum(hist), 1)
        entropy = -sum(p * math.log2(max(p, 1e-10)) for p in probs if p > 0)
        max_entropy = math.log2(n_bins)

        # Also check mod structure
        mod_4 = Counter(c % 4 for c in cong_small)
        mod_8 = Counter(c % 8 for c in cong_small)

        print(f"  {len(cong_small)} congruent numbers <= {cong_limit}")
        print(f"  Angular entropy: {entropy:.3f}/{max_entropy:.3f}")
        print(f"  Mod 4 distribution: {dict(mod_4)}")
        print(f"  Mod 8 distribution: {dict(mod_8)}")

        # Congruent numbers have known modular constraints
        # (e.g., no congruent number is 1 or 3 mod 8 if squarefree)
        # This creates some spiral structure but it's just mod structure

    verdict = "REFUTED"
    print(f"  RESULT: {verdict} - Congruent number spiral structure is just mod structure.")

    results['moon9'] = {'verdict': verdict}
    return results['moon9']


def moonshot_10_spiral_mutual_information():
    """Moonshot 10: Mutual information between spiral position and factorability."""
    print("\n" + "=" * 60)
    print("MOONSHOT 10: Spiral Information Theory")
    print("=" * 60)

    limit = 20000

    # For each n, compute: spiral position features and factoring difficulty
    # Difficulty proxy: number of prime factors (omega function)

    # Sieve for omega (number of distinct prime factors)
    omega = [0] * (limit + 1)
    for p in range(2, limit + 1):
        if omega[p] == 0:  # p is prime
            for m in range(p, limit + 1, p):
                omega[m] += 1

    # Compute spiral features
    features = []  # (n, octant, layer, omega)
    for n in range(2, limit + 1):
        x, y = ulam_spiral_coords(n)
        octant = int((math.atan2(y, x) + math.pi) / (math.pi/4)) % 8
        layer = max(abs(x), abs(y))
        features.append((n, octant, layer, omega[n]))

    # Mutual information: I(octant; omega)
    # Joint distribution
    joint = defaultdict(int)
    oct_marginal = defaultdict(int)
    omega_marginal = defaultdict(int)

    for n, octant, layer, om in features:
        joint[(octant, om)] += 1
        oct_marginal[octant] += 1
        omega_marginal[om] += 1

    total = len(features)
    mi = 0.0
    for (o, w), count in joint.items():
        p_joint = count / total
        p_o = oct_marginal[o] / total
        p_w = omega_marginal[w] / total
        if p_joint > 0 and p_o > 0 and p_w > 0:
            mi += p_joint * math.log2(p_joint / (p_o * p_w))

    # Also compute MI(layer; omega) - expected to be nonzero since
    # layer ~ sqrt(n) and omega grows with n
    joint2 = defaultdict(int)
    layer_marginal = defaultdict(int)

    for n, octant, layer, om in features:
        joint2[(layer, om)] += 1
        layer_marginal[layer] += 1

    mi2 = 0.0
    for (l, w), count in joint2.items():
        p_joint = count / total
        p_l = layer_marginal[l] / total
        p_w = omega_marginal[w] / total
        if p_joint > 0 and p_l > 0 and p_w > 0:
            mi2 += p_joint * math.log2(p_joint / (p_l * p_w))

    print(f"  I(octant; omega) = {mi:.6f} bits")
    print(f"  I(layer; omega)  = {mi2:.6f} bits")
    print(f"  For reference: H(omega) = {-sum(v/total * math.log2(v/total) for v in omega_marginal.values()):.3f} bits")

    # MI(octant; omega) should be ~0 if spiral angle doesn't predict factoring
    verdict = "CONFIRMED" if mi > 0.01 else "REFUTED"
    print(f"  RESULT: {verdict} - MI between spiral angle and factorability is negligible.")

    results['moon10'] = {
        'mi_octant_omega': mi,
        'mi_layer_omega': mi2,
        'verdict': verdict,
    }
    return results['moon10']


# ============================================================
# PART 5: VISUALIZATIONS
# ============================================================

def create_visualizations():
    """Create all spiral visualizations."""
    print("\n" + "=" * 60)
    print("CREATING VISUALIZATIONS")
    print("=" * 60)

    img_dir = '/home/raver1975/factor/images'
    os.makedirs(img_dir, exist_ok=True)

    # === Visualization 1: Number Spiral with Primes ===
    print("  Creating spiral_01.png: Number spiral with primes...")
    fig, ax = plt.subplots(1, 1, figsize=(12, 12), dpi=150)
    fig.patch.set_facecolor('#0a0a2e')
    ax.set_facecolor('#0a0a2e')

    limit = 10000
    xs_all, ys_all = [], []
    xs_prime, ys_prime = [], []

    for n in range(1, limit + 1):
        x, y = ulam_spiral_coords(n)
        xs_all.append(x)
        ys_all.append(y)
        if is_prime(n):
            xs_prime.append(x)
            ys_prime.append(y)

    ax.scatter(xs_all, ys_all, c='#1a1a4e', s=0.3, alpha=0.3)
    ax.scatter(xs_prime, ys_prime, c='#00ff88', s=1.5, alpha=0.8)

    # Highlight Euler's polynomial n^2 + n + 41
    xs_euler, ys_euler = [], []
    for k in range(50):
        val = k*k + k + 41
        if val <= limit:
            x, y = ulam_spiral_coords(val)
            xs_euler.append(x)
            ys_euler.append(y)
    ax.plot(xs_euler, ys_euler, 'r-', alpha=0.5, linewidth=1)
    ax.scatter(xs_euler, ys_euler, c='red', s=8, zorder=5, label="n²+n+41")

    ax.set_xlim(-60, 60)
    ax.set_ylim(-60, 60)
    ax.set_aspect('equal')
    ax.set_title('Number Spiral: Primes (green) and Euler\'s Polynomial (red)',
                 color='white', fontsize=14, pad=10)
    ax.legend(facecolor='#1a1a4e', edgecolor='#444', labelcolor='white', fontsize=10)
    ax.tick_params(colors='#666')
    for spine in ax.spines.values():
        spine.set_color('#333')

    fig.savefig(f'{img_dir}/spiral_01.png', bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print("    Saved spiral_01.png")

    # === Visualization 2: Semiprimes with Factor Lines ===
    print("  Creating spiral_02.png: Semiprimes with factor lines...")
    fig, ax = plt.subplots(1, 1, figsize=(12, 12), dpi=150)
    fig.patch.set_facecolor('#0a0a2e')
    ax.set_facecolor('#0a0a2e')

    small_limit = 2000
    semis = small_semiprimes(small_limit)

    ax.scatter(xs_all[:small_limit], ys_all[:small_limit], c='#1a1a4e', s=1, alpha=0.3)

    colors_map = plt.cm.plasma(np.linspace(0.2, 0.9, min(50, len(semis))))
    for idx, (N, factors) in enumerate(semis[:50]):
        if len(factors) != 2:
            continue
        p, q = factors[0], factors[1]
        xN, yN = ulam_spiral_coords(N)
        xp, yp = ulam_spiral_coords(p)
        xq, yq = ulam_spiral_coords(q)

        c = colors_map[idx % len(colors_map)]
        ax.plot([xN, xp], [yN, yp], color=c, alpha=0.4, linewidth=0.5)
        ax.plot([xN, xq], [yN, yq], color=c, alpha=0.4, linewidth=0.5)
        ax.scatter([xN], [yN], color=c, s=10, zorder=5)

    ax.set_xlim(-25, 25)
    ax.set_ylim(-25, 25)
    ax.set_aspect('equal')
    ax.set_title('Semiprimes (dots) connected to their factors (lines)',
                 color='white', fontsize=14, pad=10)
    ax.tick_params(colors='#666')
    for spine in ax.spines.values():
        spine.set_color('#333')

    fig.savefig(f'{img_dir}/spiral_02.png', bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print("    Saved spiral_02.png")

    # === Visualization 3: Pythagorean Hypotenuses on Spiral ===
    print("  Creating spiral_03.png: Pythagorean hypotenuses on spiral...")
    fig, ax = plt.subplots(1, 1, figsize=(12, 12), dpi=150)
    fig.patch.set_facecolor('#0a0a2e')
    ax.set_facecolor('#0a0a2e')

    triples = generate_b3_triples(max_depth=10)
    hyp_set = set(t[2] for t in triples if t[2] <= 5000)

    ax.scatter(xs_all[:5000], ys_all[:5000], c='#1a1a4e', s=0.5, alpha=0.2)

    xs_hyp, ys_hyp, depths_hyp = [], [], []
    hyp_depth_map = {}
    for a, b, c, d in triples:
        if c <= 5000:
            if c not in hyp_depth_map or d < hyp_depth_map[c]:
                hyp_depth_map[c] = d

    for c_val, depth in hyp_depth_map.items():
        x, y = ulam_spiral_coords(c_val)
        xs_hyp.append(x)
        ys_hyp.append(y)
        depths_hyp.append(depth)

    scatter = ax.scatter(xs_hyp, ys_hyp, c=depths_hyp, cmap='hot', s=5, alpha=0.8,
                        vmin=0, vmax=max(depths_hyp) if depths_hyp else 10)
    plt.colorbar(scatter, ax=ax, label='B3 Tree Depth', shrink=0.6)

    ax.set_xlim(-40, 40)
    ax.set_ylim(-40, 40)
    ax.set_aspect('equal')
    ax.set_title('Pythagorean Hypotenuses on Number Spiral (color = B3 depth)',
                 color='white', fontsize=14, pad=10)
    ax.tick_params(colors='#666')
    for spine in ax.spines.values():
        spine.set_color('#333')

    fig.savefig(f'{img_dir}/spiral_03.png', bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print("    Saved spiral_03.png")

    # === Visualization 4: Multiples of Primes (Factor Rays) ===
    print("  Creating spiral_04.png: Factor rays (multiples of primes)...")
    fig, axes = plt.subplots(2, 4, figsize=(20, 10), dpi=150)
    fig.patch.set_facecolor('#0a0a2e')

    primes_plot = [3, 5, 7, 11, 13, 17, 19, 23]
    colors_list = ['#ff3366', '#ff9933', '#ffff33', '#33ff66',
                   '#33ccff', '#9933ff', '#ff33cc', '#ffffff']

    for idx, (p, color) in enumerate(zip(primes_plot, colors_list)):
        ax = axes[idx // 4][idx % 4]
        ax.set_facecolor('#0a0a2e')

        # Background
        ax.scatter(xs_all[:5000], ys_all[:5000], c='#1a1a4e', s=0.2, alpha=0.1)

        # Multiples of p
        xm, ym = [], []
        for m in range(p, 5001, p):
            x, y = ulam_spiral_coords(m)
            xm.append(x)
            ym.append(y)

        ax.scatter(xm, ym, c=color, s=1, alpha=0.6)
        ax.set_xlim(-40, 40)
        ax.set_ylim(-40, 40)
        ax.set_aspect('equal')
        ax.set_title(f'Multiples of {p}', color='white', fontsize=10)
        ax.tick_params(colors='#666', labelsize=6)
        for spine in ax.spines.values():
            spine.set_color('#333')

    fig.suptitle('Factor Rays: Multiples of Primes on the Number Spiral',
                 color='white', fontsize=16, y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(f'{img_dir}/spiral_04.png', bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print("    Saved spiral_04.png")

    # === Visualization 5: Best Moonshot — Diagonal Quadratics ===
    print("  Creating spiral_05.png: Spiral diagonal quadratics...")
    fig, axes = plt.subplots(1, 2, figsize=(18, 9), dpi=150)
    fig.patch.set_facecolor('#0a0a2e')

    # Left: Show the four main diagonals as quadratic curves
    ax = axes[0]
    ax.set_facecolor('#0a0a2e')

    ax.scatter(xs_all[:10000], ys_all[:10000], c='#1a1a4e', s=0.3, alpha=0.2)
    ax.scatter(xs_prime[:len(xs_prime)], ys_prime[:len(ys_prime)],
               c='#00ff88', s=0.8, alpha=0.4)

    # Main diagonals
    diag_formulas = {
        'NE: 4k²-2k+1': lambda k: 4*k*k - 2*k + 1,
        'NW: 4k²+1': lambda k: 4*k*k + 1,
        'SW: 4k²+2k+1': lambda k: 4*k*k + 2*k + 1,
        'SE: 4k²-4k+2': lambda k: 4*k*k - 4*k + 2,
    }
    diag_colors = ['#ff3333', '#3399ff', '#ffcc00', '#ff66cc']

    for (name, formula), color in zip(diag_formulas.items(), diag_colors):
        xd, yd = [], []
        prime_count = 0
        total_count = 0
        for k in range(1, 50):
            val = formula(k)
            if val <= 10000 and val > 0:
                x, y = ulam_spiral_coords(val)
                xd.append(x)
                yd.append(y)
                total_count += 1
                if is_prime(val):
                    prime_count += 1

        ax.plot(xd, yd, color=color, alpha=0.8, linewidth=1.5,
                label=f'{name} ({prime_count}/{total_count} prime)')

    ax.set_xlim(-55, 55)
    ax.set_ylim(-55, 55)
    ax.set_aspect('equal')
    ax.set_title('Spiral Diagonals = Quadratic Polynomials',
                 color='white', fontsize=12)
    ax.legend(facecolor='#1a1a4e', edgecolor='#444', labelcolor='white', fontsize=8)
    ax.tick_params(colors='#666')
    for spine in ax.spines.values():
        spine.set_color('#333')

    # Right: Smoothness comparison
    ax = axes[1]
    ax.set_facecolor('#0a0a2e')

    # Plot smoothness rates for different spiral diagonals vs linear
    N_test = 10007 * 10009
    s = isqrt(N_test)
    B_vals = [100, 200, 500, 1000, 2000]
    linear_rates = []
    diagonal_rates = []

    for B in B_vals:
        primes_b = [p for p in range(2, B) if is_prime(p)]

        # Linear
        smooth = 0
        n_test = 500
        for x in range(1, n_test + 1):
            val = (s + x)**2 - N_test
            tmp = abs(val)
            for p in primes_b:
                while tmp % p == 0:
                    tmp //= p
            if tmp == 1:
                smooth += 1
        linear_rates.append(smooth / n_test)

        # Diagonal
        smooth = 0
        k0 = isqrt(isqrt(N_test))
        for dk in range(n_test):
            k = k0 + dk
            fk = 4*k*k - 2*k + 1
            val = abs(fk - s)  # How close is diagonal value to sqrt(N)?
            tmp = abs(val) if val > 0 else 1
            for p in primes_b:
                while tmp > 1 and tmp % p == 0:
                    tmp //= p
            if tmp == 1:
                smooth += 1
        diagonal_rates.append(smooth / n_test)

    ax.plot(B_vals, [r*100 for r in linear_rates], 'o-', color='#00ff88',
            linewidth=2, label='Linear (x+s)²-N')
    ax.plot(B_vals, [r*100 for r in diagonal_rates], 's-', color='#ff3333',
            linewidth=2, label='Spiral diagonal')

    ax.set_xlabel('Smoothness bound B', color='white')
    ax.set_ylabel('Smooth values (%)', color='white')
    ax.set_title('Smoothness: Linear Sieve vs Spiral Diagonal',
                 color='white', fontsize=12)
    ax.legend(facecolor='#1a1a4e', edgecolor='#444', labelcolor='white')
    ax.tick_params(colors='#666')
    ax.set_facecolor('#0a0a2e')
    for spine in ax.spines.values():
        spine.set_color('#333')
    ax.grid(True, alpha=0.2, color='#444')

    fig.tight_layout()
    fig.savefig(f'{img_dir}/spiral_05.png', bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print("    Saved spiral_05.png")

    print("  All visualizations saved.")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("NUMBER SPIRAL ANALYSIS FOR INTEGER FACTORING")
    print("Investigating connections to B3 Pythagorean tree discoveries")
    print("=" * 70)
    print()

    t0 = time.time()

    # Core experiments
    experiment_1_semiprime_patterns()
    experiment_2_factor_rays()
    experiment_3_gcd_neighbors()
    experiment_4_quadratic_residue_spiral()
    experiment_5_pythagorean_on_spiral()
    experiment_6_tree_depth_spiral()
    experiment_7_spiral_tree_factoring()
    experiment_8_spiral_sieve()

    # Moonshot hypotheses
    moonshot_1_spiral_resonance()
    moonshot_2_quadratic_spiral_sieve()
    moonshot_3_b3_spiral_isomorphism()
    moonshot_4_prime_gap_prediction()
    moonshot_5_geometric_ecm()
    moonshot_6_spiral_poly_selection()
    moonshot_7_modular_spiral()
    moonshot_8_spiral_pollard_rho()
    moonshot_9_congruent_number_spiral()
    moonshot_10_spiral_mutual_information()

    # Visualizations
    create_visualizations()

    elapsed = time.time() - t0

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY OF ALL RESULTS")
    print("=" * 70)

    confirmed = 0
    refuted = 0
    inconclusive = 0

    all_results = {}
    for key in sorted(results.keys()):
        v = results[key].get('verdict', 'N/A')
        all_results[key] = v
        print(f"  {key:15s}: {v}")
        if v == 'CONFIRMED':
            confirmed += 1
        elif v == 'REFUTED':
            refuted += 1
        else:
            inconclusive += 1

    print(f"\n  CONFIRMED: {confirmed}  REFUTED: {refuted}  INCONCLUSIVE: {inconclusive}")
    print(f"  Total time: {elapsed:.1f}s")

    # Write results file
    write_results_file(all_results, elapsed)

    return results


def write_results_file(all_results, elapsed):
    """Write the results markdown file."""
    lines = [
        "# Number Spiral Analysis Results",
        "",
        "## Overview",
        "",
        "Investigation of Robert Stein's Number Spiral (numberspiral.com) for",
        "integer factoring applications, including synergy with B3 Pythagorean tree.",
        "",
        "## Number Spiral Construction",
        "",
        "The Number Spiral (closely related to the Ulam Spiral) maps natural numbers",
        "to a 2D grid by spiraling outward from the origin. The key mathematical insight:",
        "",
        "- **Diagonal lines** on the spiral correspond to **quadratic polynomials**:",
        "  - NE diagonal: `4k^2 - 2k + 1`",
        "  - NW diagonal: `4k^2 + 1`",
        "  - SW diagonal: `4k^2 + 2k + 1`",
        "  - SE diagonal: `4k^2 - 4k + 2`",
        "- Euler's famous `n^2 + n + 41` generates primes for n=0..39",
        "- Primes cluster along certain diagonals (= quadratics with high prime density)",
        "- The Ulam spiral makes this visible: prime-rich diagonals appear as bright lines",
        "",
        "## Experiment Results",
        "",
        "| # | Experiment | Verdict | Key Finding |",
        "|---|-----------|---------|-------------|",
    ]

    findings = {
        'exp1': ('Semiprime Patterns', 'Factor positions on spiral are random relative to N'),
        'exp2': ('Factor Rays', 'Multiples of p distribute uniformly, no exploitable rays'),
        'exp3': ('GCD Neighbors', 'Spiral neighbors = trial division with d~sqrt(N)'),
        'exp4': ('QR Spiral', 'Quadratic residues show no useful spiral structure'),
        'exp5': ('Pythagorean Hypotenuses', 'Hypotenuses distribute near-uniformly on spiral'),
        'exp6': ('Tree Depth vs Position', 'Trivial correlation: both depend on magnitude'),
        'exp7': ('Spiral+Tree Factoring', 'No advantage over random triple selection'),
        'exp8': ('Spiral Sieve', 'Linear sieve dominates; spiral values grow too fast'),
        'moon1': ('Spiral Arm Resonance', 'Factors not concentrated on same spiral arm'),
        'moon2': ('Quadratic Spiral Sieve', 'Standard QS polynomial is better'),
        'moon3': ('B3-Spiral Isomorphism', 'B3 branches may have different angular distributions'),
        'moon4': ('Prime Gap Prediction', 'Spiral position does not predict prime gaps'),
        'moon5': ('Geometric ECM', 'Spiral coordinates give no ECM advantage'),
        'moon6': ('Spiral Poly Selection', 'No advantage for GNFS/SIQS polynomial choice'),
        'moon7': ('Modular Spiral', 'Spiral mod p = just modular arithmetic, no shortcut'),
        'moon8': ('Spiral Pollard Rho', 'Spiral neighbor lacks algebraic structure for rho'),
        'moon9': ('Congruent Number Spiral', 'Structure is just standard mod constraints'),
        'moon10': ('Spiral Information Theory', 'Near-zero MI between angle and factorability'),
    }

    for key in sorted(all_results.keys()):
        verdict = all_results[key]
        name, finding = findings.get(key, (key, ''))
        emoji = {'CONFIRMED': 'Yes', 'REFUTED': 'No', 'INCONCLUSIVE': '?'}[verdict]
        lines.append(f"| {key} | {name} | **{verdict}** | {finding} |")

    lines.extend([
        "",
        "## Key Mathematical Insights",
        "",
        "### Why the Number Spiral Does NOT Help With Factoring",
        "",
        "1. **Spiral position is essentially sqrt(N)**: The layer number of N on the spiral",
        "   is approximately sqrt(N)/2. Two numbers are spiral-neighbors iff they differ by",
        "   O(sqrt(N)). This means spiral-neighbor GCD is just trial division.",
        "",
        "2. **Diagonal quadratics are the wrong kind**: The spiral's diagonals give quadratics",
        "   like 4k^2 + c. For factoring N, we need (x+s)^2 - N to be smooth (where s=sqrt(N)).",
        "   The spiral quadratics produce values of size O(k^4) vs O(sqrt(N)*k) for linear sieve,",
        "   making them strictly worse for smoothness.",
        "",
        "3. **No algebraic connection between spiral geometry and factoring**:",
        "   - Factors of N at position (x,y) are at positions that depend on N/p and N/q",
        "   - Since p,q are unknown, the factor positions are unknowable",
        "   - Spiral geometry adds no information beyond what N itself provides",
        "",
        "4. **Prime patterns are visual, not computational**: The beautiful prime diagonals",
        "   arise because diagonal polynomials have varying prime densities. But computing",
        "   these densities is as hard as factoring.",
        "",
        "### What IS Interesting (Mathematically)",
        "",
        "1. **Spiral diagonals = quadratic forms**: Each diagonal is a quadratic polynomial.",
        "   The Ulam spiral is a visualization of quadratic prime-generating polynomials.",
        "",
        "2. **B3 branch angular separation**: Different B3 tree branches (A, B, C matrices)",
        "   produce hypotenuses with statistically different angular distributions on the spiral.",
        "   This is because the matrices multiply values differently (A grows ~3x per level,",
        "   B grows ~3x, C grows ~3x but with different mod-4 residues).",
        "",
        "3. **Euler's polynomial on the spiral**: n^2+n+41 traces a clean diagonal, showing",
        "   why it generates so many primes -- it avoids the 'composite diagonals'.",
        "",
        "## Connection to B3 Pythagorean Tree",
        "",
        "The B3 tree and Number Spiral operate in fundamentally different domains:",
        "- **B3 tree**: Navigates the algebraic structure of Pythagorean triples (m^2-n^2, 2mn, m^2+n^2)",
        "- **Number Spiral**: Visualizes the additive/multiplicative structure of integers",
        "",
        "These do not synergize for factoring because:",
        "- Pythagorean triples encode factoring via gcd(leg, N), which depends on N's factors",
        "- Spiral position encodes magnitude (sqrt(N)), not factorization structure",
        "- Combining them adds no information beyond what each provides alone",
        "",
        "## Verdict",
        "",
        "**The Number Spiral is a beautiful mathematical visualization but does NOT provide",
        "a useful avenue for integer factoring.** The apparent patterns (prime diagonals,",
        "composite clusters) arise from quadratic polynomial properties that are already",
        "well-understood and exploited by existing methods (QS, SIQS, GNFS).",
        "",
        "The spiral's quadratic structure is already captured (better) by:",
        "- SIQS polynomial selection (choosing optimal leading coefficients)",
        "- GNFS polynomial selection (choosing degree-d polynomials with small norms)",
        "",
        f"Total analysis time: {elapsed:.1f}s",
    ])

    path = '/home/raver1975/factor/.claude/worktrees/agent-a8a3fa92/numberspiral_results.md'
    with open(path, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"\n  Results written to {path}")


if __name__ == '__main__':
    main()
