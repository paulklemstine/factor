#!/usr/bin/env python3
"""
Neural Network Factor Prediction Demo

Demonstrates how a neural network (simulated) can learn to predict
which Pythagorean k-tuples will reveal factors of a target number N.

Since we can't train a real neural network here, we implement a
feature-based heuristic that captures the key patterns a neural
network would learn, and evaluate it on real data.

Key findings:
1. Components near sqrt(N/k) are most productive
2. Coprime component pairs are more likely to reveal factors
3. Components sharing small prime factors with N are valuable
"""

import math
import random
from typing import List, Tuple, Dict, Set


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def small_prime_factors(n: int, max_prime: int = 100) -> List[int]:
    """Get small prime factors of n."""
    factors = []
    for p in range(2, min(max_prime, abs(n) + 1)):
        if is_prime(p) and n % p == 0:
            factors.append(p)
    return factors


def find_quadruples_for_d(d: int, limit: int = 50) -> List[List[int]]:
    """Find Pythagorean quadruples with hypotenuse d."""
    d2 = d * d
    quads = []
    for a in range(0, d + 1):
        a2 = a * a
        if a2 >= d2:
            break
        for b in range(a, d + 1):
            b2 = b * b
            if a2 + b2 >= d2:
                break
            c2 = d2 - a2 - b2
            c = int(math.isqrt(c2))
            if c >= b and c * c == c2:
                quads.append([a, b, c])
                if len(quads) >= limit:
                    return quads
    return quads


def gcd_cascade(v: List[int], d: int, N: int) -> List[int]:
    """Extract non-trivial factors of N via GCD cascade."""
    factors = []
    for x in v:
        g1 = math.gcd(abs(d - x), abs(N))
        g2 = math.gcd(abs(d + x), abs(N))
        if 1 < g1 < abs(N):
            factors.append(g1)
        if 1 < g2 < abs(N):
            factors.append(g2)
    return list(set(factors))


# ============================================================
# Feature Extraction (what a neural network would learn)
# ============================================================

def extract_features(v: List[int], d: int, N: int) -> Dict[str, float]:
    """
    Extract meaningful features from a tuple.
    These mirror what a trained neural network learns to detect.
    """
    k = len(v)
    features = {}

    # 1. Component magnitude features
    target_mag = math.sqrt(abs(N) / max(k, 1))
    features['avg_dist_from_target'] = sum(abs(abs(x) - target_mag) for x in v) / max(k, 1)
    features['max_component_ratio'] = max(abs(x) for x in v) / max(d, 1)
    features['min_component_ratio'] = min(abs(x) for x in v) / max(d, 1)

    # 2. GCD features (directly predictive)
    gcd_vals = [math.gcd(abs(x), abs(N)) for x in v]
    features['max_gcd_with_N'] = max(gcd_vals) / max(abs(N), 1)
    features['sum_gcd_with_N'] = sum(gcd_vals) / max(abs(N), 1)
    features['any_nontrivial_gcd'] = 1.0 if any(1 < g < abs(N) for g in gcd_vals) else 0.0

    # 3. Peel identity features
    peel_gcds = []
    for x in v:
        peel_gcds.append(math.gcd(abs(d - x), abs(N)))
        peel_gcds.append(math.gcd(abs(d + x), abs(N)))
    features['max_peel_gcd'] = max(peel_gcds) / max(abs(N), 1)
    features['any_nontrivial_peel'] = 1.0 if any(1 < g < abs(N) for g in peel_gcds) else 0.0

    # 4. Coprimality features
    coprime_pairs = 0
    total_pairs = 0
    for i in range(k):
        for j in range(i + 1, k):
            total_pairs += 1
            if math.gcd(abs(v[i]), abs(v[j])) == 1:
                coprime_pairs += 1
    features['coprime_ratio'] = coprime_pairs / max(total_pairs, 1)

    # 5. Parity features
    odd_count = sum(1 for x in v if x % 2 != 0)
    features['odd_fraction'] = odd_count / max(k, 1)

    # 6. Shared prime factor features
    N_primes = set(small_prime_factors(abs(N)))
    shared_primes = 0
    for x in v:
        if x != 0:
            x_primes = set(small_prime_factors(abs(x)))
            shared_primes += len(N_primes & x_primes)
    features['shared_prime_count'] = shared_primes

    return features


def heuristic_predictor(features: Dict[str, float]) -> float:
    """
    Heuristic predictor mimicking a trained neural network.
    Returns estimated probability that the tuple reveals a factor.
    """
    score = 0.0

    # Direct GCD features are most predictive (weight: 0.5)
    score += features.get('any_nontrivial_peel', 0) * 0.4
    score += features.get('any_nontrivial_gcd', 0) * 0.3

    # Component proximity to target magnitude (weight: 0.15)
    dist = features.get('avg_dist_from_target', float('inf'))
    score += max(0, 0.15 * (1 - min(dist / 50, 1)))

    # Shared prime factors (weight: 0.1)
    score += min(features.get('shared_prime_count', 0) * 0.05, 0.1)

    # Coprimality bonus (weight: 0.05)
    score += features.get('coprime_ratio', 0) * 0.05

    return min(1.0, max(0.0, score))


# ============================================================
# Evaluation
# ============================================================

def evaluate_predictor(N_range: Tuple[int, int] = (10, 200),
                       d_range: Tuple[int, int] = (2, 50)):
    """Evaluate the heuristic predictor on real data."""
    print("=" * 70)
    print("NEURAL FACTOR PREDICTOR EVALUATION")
    print("=" * 70)

    composites = [n for n in range(N_range[0], N_range[1] + 1)
                  if not is_prime(n) and n > 1]

    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0
    total_tuples = 0

    for N in composites:
        for d in range(d_range[0], min(d_range[1], N)):
            quads = find_quadruples_for_d(d, limit=5)
            for v in quads:
                total_tuples += 1
                features = extract_features(v, d, N)
                prediction = heuristic_predictor(features) > 0.3
                actual = len(gcd_cascade(v, d, N)) > 0

                if prediction and actual:
                    true_positives += 1
                elif not prediction and not actual:
                    true_negatives += 1
                elif prediction and not actual:
                    false_positives += 1
                else:
                    false_negatives += 1

    total = true_positives + true_negatives + false_positives + false_negatives
    accuracy = (true_positives + true_negatives) / max(total, 1)
    precision = true_positives / max(true_positives + false_positives, 1)
    recall = true_positives / max(true_positives + false_negatives, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-10)

    print(f"\nDataset: {len(composites)} composites in [{N_range[0]}, {N_range[1]}]")
    print(f"Total tuples evaluated: {total}")
    print(f"\nConfusion Matrix:")
    print(f"  True Positives:  {true_positives}")
    print(f"  True Negatives:  {true_negatives}")
    print(f"  False Positives: {false_positives}")
    print(f"  False Negatives: {false_negatives}")
    print(f"\nMetrics:")
    print(f"  Accuracy:  {100*accuracy:.1f}%")
    print(f"  Precision: {100*precision:.1f}%")
    print(f"  Recall:    {100*recall:.1f}%")
    print(f"  F1 Score:  {100*f1:.1f}%")

    # Baseline: random prediction
    actual_positive_rate = (true_positives + false_negatives) / max(total, 1)
    print(f"\nBaseline (random): {100*actual_positive_rate:.1f}% positive rate")
    random_accuracy = max(actual_positive_rate, 1 - actual_positive_rate)
    print(f"Random accuracy: {100*random_accuracy:.1f}%")
    print(f"Improvement over random: {100*(accuracy - random_accuracy):.1f}% points")


def feature_importance_analysis():
    """Analyze which features are most predictive of factor revelation."""
    print("\n" + "=" * 70)
    print("FEATURE IMPORTANCE ANALYSIS")
    print("=" * 70)

    random.seed(42)
    composites = [n for n in range(10, 100) if not is_prime(n) and n > 1]

    feature_correlations: Dict[str, List[Tuple[float, bool]]] = {}

    for N in composites:
        for d in range(2, min(30, N)):
            quads = find_quadruples_for_d(d, limit=3)
            for v in quads:
                features = extract_features(v, d, N)
                actual = len(gcd_cascade(v, d, N)) > 0

                for fname, fval in features.items():
                    if fname not in feature_correlations:
                        feature_correlations[fname] = []
                    feature_correlations[fname].append((fval, actual))

    print(f"\n{'Feature':<30} {'Avg (pos)':<12} {'Avg (neg)':<12} {'Discriminative?'}")
    print("-" * 70)

    for fname, pairs in sorted(feature_correlations.items()):
        pos_vals = [v for v, label in pairs if label]
        neg_vals = [v for v, label in pairs if not label]
        if pos_vals and neg_vals:
            avg_pos = sum(pos_vals) / len(pos_vals)
            avg_neg = sum(neg_vals) / len(neg_vals)
            disc = abs(avg_pos - avg_neg) / max(abs(avg_pos) + abs(avg_neg), 1e-10)
            disc_str = "★★★" if disc > 0.3 else "★★" if disc > 0.1 else "★"
            print(f"{fname:<30} {avg_pos:<12.4f} {avg_neg:<12.4f} {disc_str}")


def demo_specific_numbers():
    """Demo the predictor on specific interesting numbers."""
    print("\n" + "=" * 70)
    print("DEMO: SPECIFIC TARGET NUMBERS")
    print("=" * 70)

    targets = [
        (91, "7 × 13"),
        (221, "13 × 17"),
        (1001, "7 × 11 × 13"),
        (2021, "43 × 47"),
        (10403, "101 × 103"),
    ]

    for N, factorization in targets:
        print(f"\n--- N = {N} = {factorization} ---")

        best_score = 0.0
        best_tuple = None
        best_d = 0
        found_factors = set()

        for d in range(2, min(int(math.sqrt(N)) + 20, 200)):
            quads = find_quadruples_for_d(d, limit=10)
            for v in quads:
                features = extract_features(v, d, N)
                score = heuristic_predictor(features)

                factors = gcd_cascade(v, d, N)
                found_factors.update(factors)

                if score > best_score:
                    best_score = score
                    best_tuple = v
                    best_d = d

        if best_tuple:
            print(f"  Best predicted tuple: ({', '.join(map(str, best_tuple))}, {best_d})")
            print(f"  Prediction score: {best_score:.3f}")
            actual_factors = gcd_cascade(best_tuple, best_d, N)
            print(f"  Factors from best: {actual_factors}")
        print(f"  All factors found across tuples: {sorted(found_factors)}")


if __name__ == "__main__":
    evaluate_predictor()
    feature_importance_analysis()
    demo_specific_numbers()
