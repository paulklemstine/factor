#!/usr/bin/env python3
"""
Higher-Dimensional Pythagorean Factoring — Interactive Demo

Demonstrates:
1. Finding Pythagorean k-tuples for dimensions 3-8
2. GCD cascade factor extraction across multiple channels
3. Cross-collision factoring from shared hypotenuse tuples
4. Division algebra composition (Brahmagupta-Fibonacci, Euler, Degen)
5. Octonion non-associativity exploitation
6. Performance comparison across dimensions
"""

import math
import random
import itertools
from collections import defaultdict
from typing import List, Tuple, Optional, Dict


# ============================================================
# §1. Core Definitions
# ============================================================

def is_pythagorean_ktuple(v: List[int], d: int) -> bool:
    """Check if v is a Pythagorean k-tuple with hypotenuse d."""
    return sum(x**2 for x in v) == d**2


def find_pythagorean_triples(max_d: int) -> List[Tuple[int, int, int]]:
    """Find all primitive Pythagorean triples with hypotenuse ≤ max_d."""
    triples = []
    for m in range(2, int(math.sqrt(max_d)) + 1):
        for n in range(1, m):
            if (m - n) % 2 == 1 and math.gcd(m, n) == 1:
                a = m**2 - n**2
                b = 2 * m * n
                c = m**2 + n**2
                if c <= max_d:
                    triples.append((min(a, b), max(a, b), c))
    return sorted(set(triples))


def find_pythagorean_quadruples(max_d: int, limit: int = 1000) -> List[Tuple[int, int, int, int]]:
    """Find Pythagorean quadruples (a,b,c,d) with a²+b²+c²=d², d ≤ max_d."""
    quads = []
    for d in range(2, max_d + 1):
        d2 = d * d
        for a in range(0, d):
            a2 = a * a
            if a2 >= d2:
                break
            for b in range(a, d):
                b2 = b * b
                if a2 + b2 >= d2:
                    break
                rem = d2 - a2 - b2
                c = int(math.isqrt(rem))
                if c >= b and c * c == rem:
                    quads.append((a, b, c, d))
                    if len(quads) >= limit:
                        return quads
    return quads


def find_5tuples(max_d: int, limit: int = 500) -> List[Tuple[int, int, int, int, int]]:
    """Find Pythagorean 5-tuples (a₁,a₂,a₃,a₄,d) with Σaᵢ²=d², d ≤ max_d."""
    tuples = []
    for d in range(2, max_d + 1):
        d2 = d * d
        for a1 in range(0, d):
            if a1**2 >= d2:
                break
            for a2 in range(a1, d):
                s2 = a1**2 + a2**2
                if s2 >= d2:
                    break
                for a3 in range(a2, d):
                    s3 = s2 + a3**2
                    if s3 >= d2:
                        break
                    rem = d2 - s3
                    a4 = int(math.isqrt(rem))
                    if a4 >= a3 and a4 * a4 == rem:
                        tuples.append((a1, a2, a3, a4, d))
                        if len(tuples) >= limit:
                            return tuples
    return tuples


# ============================================================
# §2. GCD Cascade Factor Extraction
# ============================================================

def peel_identity(v: List[int], d: int, j: int) -> Tuple[int, int]:
    """Compute the peel identity for component j: returns (d - v[j], d + v[j])."""
    return (d - v[j], d + v[j])


def gcd_cascade(v: List[int], d: int, N: int) -> List[int]:
    """
    Extract factor candidates from a k-tuple via GCD cascade.
    Returns list of non-trivial factor candidates.
    """
    factors = []
    for j in range(len(v)):
        d_minus, d_plus = peel_identity(v, d, j)
        g1 = math.gcd(abs(d_minus), abs(N))
        g2 = math.gcd(abs(d_plus), abs(N))
        if 1 < g1 < abs(N):
            factors.append(g1)
        if 1 < g2 < abs(N):
            factors.append(g2)
    return list(set(factors))


def cross_collision_factors(v1: List[int], v2: List[int], N: int) -> List[int]:
    """
    Extract factors from cross-collision of two k-tuples sharing a hypotenuse.
    """
    factors = []
    k = len(v1)
    for i in range(k):
        diff = v1[i]**2 - v2[i]**2
        if diff != 0:
            g1 = math.gcd(abs(v1[i] - v2[i]), abs(N))
            g2 = math.gcd(abs(v1[i] + v2[i]), abs(N))
            if 1 < g1 < abs(N):
                factors.append(g1)
            if 1 < g2 < abs(N):
                factors.append(g2)
    return list(set(factors))


# ============================================================
# §3. Division Algebra Composition
# ============================================================

def brahmagupta_fibonacci(a: int, b: int, c: int, d: int) -> Tuple[int, int]:
    """
    Compose two sums of two squares: (a²+b²)(c²+d²) = (ac-bd)² + (ad+bc)²
    Returns (ac-bd, ad+bc).
    """
    return (a*c - b*d, a*d + b*c)


def euler_four_square(a: List[int], b: List[int]) -> List[int]:
    """
    Compose two sums of four squares via quaternion multiplication.
    (Σaᵢ²)(Σbᵢ²) = Σcᵢ² where c is the quaternion product.
    """
    a1, a2, a3, a4 = a
    b1, b2, b3, b4 = b
    c1 = a1*b1 - a2*b2 - a3*b3 - a4*b4
    c2 = a1*b2 + a2*b1 + a3*b4 - a4*b3
    c3 = a1*b3 - a2*b4 + a3*b1 + a4*b2
    c4 = a1*b4 + a2*b3 - a3*b2 + a4*b1
    return [c1, c2, c3, c4]


def degen_eight_square(a: List[int], b: List[int]) -> List[int]:
    """
    Compose two sums of eight squares via octonion multiplication.
    Returns the 8-component result.
    """
    a1, a2, a3, a4, a5, a6, a7, a8 = a
    b1, b2, b3, b4, b5, b6, b7, b8 = b
    c1 = a1*b1 - a2*b2 - a3*b3 - a4*b4 - a5*b5 - a6*b6 - a7*b7 - a8*b8
    c2 = a1*b2 + a2*b1 + a3*b4 - a4*b3 + a5*b6 - a6*b5 - a7*b8 + a8*b7
    c3 = a1*b3 - a2*b4 + a3*b1 + a4*b2 + a5*b7 + a6*b8 - a7*b5 - a8*b6
    c4 = a1*b4 + a2*b3 - a3*b2 + a4*b1 + a5*b8 - a6*b7 + a7*b6 - a8*b5
    c5 = a1*b5 - a2*b6 - a3*b7 - a4*b8 + a5*b1 + a6*b2 + a7*b3 + a8*b4
    c6 = a1*b6 + a2*b5 - a3*b8 + a4*b7 - a5*b2 + a6*b1 - a7*b4 + a8*b3
    c7 = a1*b7 + a2*b8 + a3*b5 - a4*b6 - a5*b3 + a6*b4 + a7*b1 - a8*b2
    c8 = a1*b8 - a2*b7 + a3*b6 + a4*b5 - a5*b4 - a6*b3 + a7*b2 + a8*b1
    return [c1, c2, c3, c4, c5, c6, c7, c8]


def verify_composition_identity(a: List[int], b: List[int], compose_fn) -> bool:
    """Verify that ||a||² · ||b||² = ||compose(a,b)||²."""
    norm_a = sum(x**2 for x in a)
    norm_b = sum(x**2 for x in b)
    c = compose_fn(a, b)
    norm_c = sum(x**2 for x in c)
    return norm_a * norm_b == norm_c


# ============================================================
# §4. Octonion Non-Associativity Exploitation
# ============================================================

def octonion_compose_left(a: List[int], b: List[int], c: List[int]) -> List[int]:
    """(a · b) · c — left-associated octonion triple product."""
    ab = degen_eight_square(a, b)
    return degen_eight_square(ab, c)


def octonion_compose_right(a: List[int], b: List[int], c: List[int]) -> List[int]:
    """a · (b · c) — right-associated octonion triple product."""
    bc = degen_eight_square(b, c)
    return degen_eight_square(a, bc)


def octonion_non_associativity_demo():
    """
    Demonstrate that different association orders produce different 8-tuples,
    each providing independent factor-extraction opportunities.
    """
    print("\n" + "=" * 70)
    print("§4. OCTONION NON-ASSOCIATIVITY EXPLOITATION")
    print("=" * 70)

    # Three random 8-tuples
    random.seed(42)
    a = [random.randint(1, 10) for _ in range(8)]
    b = [random.randint(1, 10) for _ in range(8)]
    c = [random.randint(1, 10) for _ in range(8)]

    print(f"\nInput a = {a}")
    print(f"Input b = {b}")
    print(f"Input c = {c}")

    norm_a = sum(x**2 for x in a)
    norm_b = sum(x**2 for x in b)
    norm_c = sum(x**2 for x in c)
    product_norm = norm_a * norm_b * norm_c

    left = octonion_compose_left(a, b, c)
    right = octonion_compose_right(a, b, c)

    norm_left = sum(x**2 for x in left)
    norm_right = sum(x**2 for x in right)

    print(f"\n(a·b)·c = {left}")
    print(f"a·(b·c) = {right}")
    print(f"\nNorm product = {product_norm}")
    print(f"||(a·b)·c||² = {norm_left}")
    print(f"||a·(b·c)||² = {norm_right}")
    print(f"\nNorms equal? {norm_left == norm_right == product_norm}")
    print(f"Tuples equal? {left == right}")

    if left != right:
        print(f"\n✓ NON-ASSOCIATIVITY CONFIRMED!")
        print(f"  Two DIFFERENT 8-tuples with the SAME norm — independent factor channels!")

        # Show factor extraction difference
        N = 2023 * 37  # Test target
        factors_left = gcd_cascade(left, int(math.isqrt(norm_left)), N)
        factors_right = gcd_cascade(right, int(math.isqrt(norm_right)), N)
        print(f"\n  Target N = {N} = 2023 × 37")
        print(f"  Factors from (a·b)·c: {factors_left}")
        print(f"  Factors from a·(b·c): {factors_right}")
        print(f"  Combined: {sorted(set(factors_left + factors_right))}")


# ============================================================
# §5. Lattice Reduction Simulation
# ============================================================

def simple_lattice_search(N: int, k: int, num_tries: int = 1000) -> List[Tuple[List[int], int]]:
    """
    Simulate lattice-reduction-based search for Pythagorean k-tuples.
    Uses random short vectors near the sphere as a simplified model.
    """
    results = []
    d_max = int(math.sqrt(N)) + 10

    for _ in range(num_tries):
        d = random.randint(2, d_max)
        d2 = d * d

        # Generate random (k-1)-tuple and check if it lies on the sphere
        v = [random.randint(-d, d) for _ in range(k - 1)]
        s = sum(x**2 for x in v)

        if s == d2:
            results.append((v, d))
        elif s < d2:
            # Try to complete the last component
            rem = d2 - sum(x**2 for x in v[:-1])
            if rem >= 0:
                c = int(math.isqrt(rem))
                if c * c == rem:
                    v[-1] = c
                    results.append((v, d))

    return results


# ============================================================
# §6. E₈ Lattice Connection
# ============================================================

def e8_root_vectors() -> List[List[int]]:
    """
    Generate the 240 root vectors of the E₈ lattice.
    These are:
    1. All permutations of (±1, ±1, 0, 0, 0, 0, 0, 0) — 112 vectors
    2. All vectors (±1/2, ..., ±1/2) with even number of minus signs — 128 vectors
    (We use doubled coordinates to stay in integers)
    """
    roots = []

    # Type 1: permutations of (±2, ±2, 0, 0, 0, 0, 0, 0) [doubled]
    for i in range(8):
        for j in range(i + 1, 8):
            for si in [-2, 2]:
                for sj in [-2, 2]:
                    v = [0] * 8
                    v[i] = si
                    v[j] = sj
                    roots.append(v)

    # Type 2: (±1, ±1, ±1, ±1, ±1, ±1, ±1, ±1) with even number of minus signs
    for signs in itertools.product([-1, 1], repeat=8):
        if sum(1 for s in signs if s == -1) % 2 == 0:
            roots.append(list(signs))

    return roots


def e8_kissing_number_demo():
    """Demonstrate E₈ lattice properties relevant to factoring."""
    print("\n" + "=" * 70)
    print("§6. E₈ LATTICE CONNECTION")
    print("=" * 70)

    roots = e8_root_vectors()
    print(f"\nE₈ root vectors generated: {len(roots)}")
    print(f"Expected kissing number: 240")

    # Verify norms (should all be 2 for type 2, 8 for type 1 in doubled coords)
    norms = set(sum(x**2 for x in v) for v in roots)
    print(f"Distinct norms²: {sorted(norms)}")

    # Count cross-collision pairs
    n = len(roots)
    cross_pairs = n * (n - 1) // 2
    print(f"\nCross-collision pairs from kissing vectors: C({n},2) = {cross_pairs}")
    print(f"Factor extraction channels per vector: 7")
    print(f"Total GCD operations: {n * 7 * 2}")

    # Demonstrate with a specific pair
    v1 = roots[0]
    v2 = roots[1]
    print(f"\nExample pair:")
    print(f"  v₁ = {v1}, ||v₁||² = {sum(x**2 for x in v1)}")
    print(f"  v₂ = {v2}, ||v₂||² = {sum(x**2 for x in v2)}")


# ============================================================
# §7. Neural Network Factor Prediction (Simplified Model)
# ============================================================

def feature_extraction(v: List[int], d: int, N: int) -> List[float]:
    """Extract features from a k-tuple for neural network input."""
    k = len(v)
    features = []

    # Normalized component magnitudes
    for x in v:
        features.append(abs(x) / d if d > 0 else 0)

    # GCD features
    for x in v:
        features.append(math.gcd(abs(x), abs(N)) / N if N > 0 else 0)

    # Parity features
    for x in v:
        features.append(x % 2)

    # Coprimality features
    for i in range(min(k, 4)):
        for j in range(i + 1, min(k, 4)):
            features.append(1.0 if math.gcd(abs(v[i]), abs(v[j])) == 1 else 0.0)

    # Distance from √(N/k)
    target_mag = math.sqrt(abs(N) / k) if k > 0 else 0
    for x in v:
        features.append(abs(abs(x) - target_mag) / (target_mag + 1))

    return features


def simple_factor_predictor(features: List[float]) -> float:
    """
    A hand-crafted heuristic predictor mimicking what a neural network learns.
    Returns estimated probability that the tuple reveals a factor.
    """
    score = 0.0

    # Components near √(N/k) are good
    k = len(features) // 5  # approximate
    dist_features = features[-k:] if k > 0 else []
    if dist_features:
        avg_dist = sum(dist_features) / len(dist_features)
        score += max(0, 1.0 - avg_dist) * 0.3

    # High GCD values are very good
    gcd_features = features[k:2*k] if k > 0 else []
    if gcd_features:
        max_gcd = max(gcd_features)
        score += max_gcd * 0.5

    # Coprime pairs are slightly good
    coprime_features = features[3*k:3*k+6] if len(features) > 3*k+6 else []
    if coprime_features:
        coprime_ratio = sum(coprime_features) / len(coprime_features)
        score += coprime_ratio * 0.2

    return min(1.0, max(0.0, score))


def neural_prediction_demo(N: int = 1001):
    """Demonstrate neural network factor prediction (simplified)."""
    print("\n" + "=" * 70)
    print("§7. NEURAL NETWORK FACTOR PREDICTION")
    print("=" * 70)

    print(f"\nTarget N = {N}")

    # Find actual factors
    actual_factors = []
    for p in range(2, int(math.sqrt(N)) + 1):
        if N % p == 0:
            actual_factors.append(p)
            actual_factors.append(N // p)
    print(f"Actual factors: {sorted(set(actual_factors))}")

    # Generate tuples and predict
    tuples_5 = find_5tuples(max_d=int(math.sqrt(N)) + 5, limit=50)
    if not tuples_5:
        print("No 5-tuples found in range.")
        return

    print(f"\nFound {len(tuples_5)} 5-tuples")
    print(f"\n{'Tuple':<30} {'Predicted':>10} {'Actual':>8} {'Factors Found'}")
    print("-" * 80)

    correct = 0
    total = min(20, len(tuples_5))
    for t in tuples_5[:total]:
        v = list(t[:4])
        d = t[4]
        features = feature_extraction(v, d, N)
        prediction = simple_factor_predictor(features)
        actual_gcd_factors = gcd_cascade(v, d, N)
        is_revealing = len(actual_gcd_factors) > 0

        pred_label = prediction > 0.3
        if pred_label == is_revealing:
            correct += 1

        tuple_str = f"({', '.join(str(x) for x in v)}, {d})"
        print(f"{tuple_str:<30} {prediction:>10.3f} {'YES' if is_revealing else 'no':>8} {actual_gcd_factors}")

    print(f"\nAccuracy: {correct}/{total} = {100*correct/total:.1f}%")


# ============================================================
# §8. Performance Comparison Across Dimensions
# ============================================================

def dimension_comparison(N_max: int = 200):
    """Compare factor recovery across dimensions 3, 4, 5."""
    print("\n" + "=" * 70)
    print("§8. DIMENSION COMPARISON")
    print("=" * 70)

    composites = []
    for n in range(6, N_max + 1):
        is_prime = all(n % p != 0 for p in range(2, int(math.sqrt(n)) + 1))
        if not is_prime:
            composites.append(n)

    print(f"\nTesting {len(composites)} composites in [{composites[0]}, {composites[-1]}]")

    results = {3: 0, 4: 0, 5: 0}

    for N in composites:
        # Dimension 3 (triples)
        for d in range(2, N + 1):
            d2 = d * d
            found_3 = False
            for a in range(0, d):
                b2 = d2 - a**2
                b = int(math.isqrt(b2))
                if b * b == b2 and b >= a:
                    factors = gcd_cascade([a, b], d, N)
                    if factors:
                        found_3 = True
                        break
            if found_3:
                break
        if found_3:
            results[3] += 1

        # Dimension 4 (quadruples)
        found_4 = False
        for d in range(2, N + 1):
            d2 = d * d
            for a in range(0, d):
                for b in range(a, d):
                    c2 = d2 - a**2 - b**2
                    if c2 < 0:
                        break
                    c = int(math.isqrt(c2))
                    if c >= b and c * c == c2:
                        factors = gcd_cascade([a, b, c], d, N)
                        if factors:
                            found_4 = True
                            break
                if found_4:
                    break
            if found_4:
                break
        if found_4:
            results[4] += 1

        # Dimension 5 (5-tuples)
        found_5 = False
        for d in range(2, N + 1):
            d2 = d * d
            for a in range(0, d):
                for b in range(a, d):
                    for c in range(b, d):
                        e2 = d2 - a**2 - b**2 - c**2
                        if e2 < 0:
                            break
                        e = int(math.isqrt(e2))
                        if e >= c and e * e == e2:
                            factors = gcd_cascade([a, b, c, e], d, N)
                            if factors:
                                found_5 = True
                                break
                    if found_5:
                        break
                if found_5:
                    break
            if found_5:
                break
        if found_5:
            results[5] += 1

    total = len(composites)
    print(f"\n{'Dimension':<12} {'Factors Found':<15} {'Success Rate'}")
    print("-" * 45)
    for k in [3, 4, 5]:
        print(f"k = {k:<8} {results[k]:<15} {100*results[k]/total:.1f}%")


# ============================================================
# §9. Composition Chain Demo
# ============================================================

def composition_chain_demo():
    """Demonstrate the division algebra composition chain ℝ → ℂ → ℍ → 𝕆."""
    print("\n" + "=" * 70)
    print("§9. DIVISION ALGEBRA COMPOSITION CHAIN")
    print("=" * 70)

    # ℂ: Brahmagupta-Fibonacci
    print("\n--- ℂ (Brahmagupta-Fibonacci) ---")
    a, b, c, d = 3, 4, 5, 12
    lhs = (a**2 + b**2) * (c**2 + d**2)
    r1, r2 = brahmagupta_fibonacci(a, b, c, d)
    rhs = r1**2 + r2**2
    print(f"({a}²+{b}²)({c}²+{d}²) = {lhs}")
    print(f"({r1})² + ({r2})² = {rhs}")
    print(f"Equal: {lhs == rhs} ✓")

    # ℍ: Euler four-square
    print("\n--- ℍ (Euler Four-Square) ---")
    q1 = [1, 2, 3, 4]
    q2 = [5, 6, 7, 8]
    lhs = sum(x**2 for x in q1) * sum(x**2 for x in q2)
    result = euler_four_square(q1, q2)
    rhs = sum(x**2 for x in result)
    print(f"||{q1}||² × ||{q2}||² = {lhs}")
    print(f"||{result}||² = {rhs}")
    print(f"Equal: {lhs == rhs} ✓")

    # 𝕆: Degen eight-square
    print("\n--- 𝕆 (Degen Eight-Square) ---")
    o1 = [1, 2, 3, 4, 5, 6, 7, 8]
    o2 = [8, 7, 6, 5, 4, 3, 2, 1]
    lhs = sum(x**2 for x in o1) * sum(x**2 for x in o2)
    result = degen_eight_square(o1, o2)
    rhs = sum(x**2 for x in result)
    print(f"||{o1}||² × ||{o2}||² = {lhs}")
    print(f"Result = {result}")
    print(f"||result||² = {rhs}")
    print(f"Equal: {lhs == rhs} ✓")

    # Verify all identities
    print("\n--- Verification of 1000 random compositions ---")
    random.seed(123)
    bf_ok = all(verify_composition_identity(
        [random.randint(-10, 10) for _ in range(2)],
        [random.randint(-10, 10) for _ in range(2)],
        lambda a, b: list(brahmagupta_fibonacci(a[0], a[1], b[0], b[1]))
    ) for _ in range(1000))
    print(f"Brahmagupta-Fibonacci (1000 tests): {'✓ ALL PASS' if bf_ok else '✗ FAIL'}")

    euler_ok = all(verify_composition_identity(
        [random.randint(-10, 10) for _ in range(4)],
        [random.randint(-10, 10) for _ in range(4)],
        euler_four_square
    ) for _ in range(1000))
    print(f"Euler Four-Square (1000 tests):      {'✓ ALL PASS' if euler_ok else '✗ FAIL'}")

    degen_ok = all(verify_composition_identity(
        [random.randint(-10, 10) for _ in range(8)],
        [random.randint(-10, 10) for _ in range(8)],
        degen_eight_square
    ) for _ in range(1000))
    print(f"Degen Eight-Square (1000 tests):     {'✓ ALL PASS' if degen_ok else '✗ FAIL'}")


# ============================================================
# §10. Channel Growth Analysis
# ============================================================

def channel_growth_analysis():
    """Analyze how factor channels and cross-collision pairs grow with dimension."""
    print("\n" + "=" * 70)
    print("§10. CHANNEL AND CROSS-COLLISION GROWTH")
    print("=" * 70)

    print(f"\n{'k':<6} {'Channels':<12} {'Cross Pairs':<14} {'Total GCDs':<12} {'Ratio'}")
    print("-" * 58)
    for k in range(3, 17):
        channels = k - 1
        cross = channels * (channels - 1) // 2
        total_gcds = 2 * channels
        ratio = cross / channels if channels > 0 else 0
        print(f"{k:<6} {channels:<12} {cross:<14} {total_gcds:<12} {ratio:.1f}")

    print("\nKey insight: Cross-collision pairs grow as O(k²) while channels grow as O(k).")
    print("This quadratic growth means higher dimensions provide disproportionately")
    print("more cross-collision opportunities.")


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 70)
    print("HIGHER-DIMENSIONAL PYTHAGOREAN FACTORING — INTERACTIVE DEMO")
    print("=" * 70)

    # §1: Basic tuple generation
    print("\n" + "=" * 70)
    print("§1. PYTHAGOREAN TUPLE GENERATION")
    print("=" * 70)

    triples = find_pythagorean_triples(50)
    print(f"\nPrimitive triples with hypotenuse ≤ 50: {len(triples)}")
    for t in triples[:5]:
        print(f"  {t}: {t[0]}² + {t[1]}² = {t[0]**2} + {t[1]**2} = {t[2]**2} = {t[2]}²")

    quads = find_pythagorean_quadruples(20, limit=10)
    print(f"\nQuadruples with hypotenuse ≤ 20: {len(quads)}")
    for q in quads[:5]:
        print(f"  {q}: {q[0]}²+{q[1]}²+{q[2]}² = {q[0]**2+q[1]**2+q[2]**2} = {q[3]}²")

    tuples5 = find_5tuples(10, limit=10)
    print(f"\n5-tuples with hypotenuse ≤ 10: {len(tuples5)}")
    for t in tuples5[:5]:
        s = sum(x**2 for x in t[:4])
        print(f"  {t}: Σaᵢ² = {s} = {t[4]}²")

    # §2: Factor extraction demo
    print("\n" + "=" * 70)
    print("§2. GCD CASCADE FACTOR EXTRACTION")
    print("=" * 70)

    N = 91  # = 7 × 13
    print(f"\nTarget N = {N} (= 7 × 13)")
    print(f"\nSearching for factor-revealing tuples...")

    for d in range(2, N + 1):
        d2 = d * d
        for a in range(0, d):
            for b in range(a, d):
                c2 = d2 - a**2 - b**2
                if c2 < 0:
                    break
                c = int(math.isqrt(c2))
                if c >= b and c * c == c2:
                    v = [a, b, c]
                    factors = gcd_cascade(v, d, N)
                    if factors:
                        print(f"  Quadruple ({a},{b},{c},{d}): Found factors {factors}")

    # §3-10: Run all demos
    composition_chain_demo()
    octonion_non_associativity_demo()
    e8_kissing_number_demo()
    channel_growth_analysis()
    neural_prediction_demo(N=1001)
    dimension_comparison(N_max=100)

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
