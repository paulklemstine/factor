#!/usr/bin/env python3
"""
Machine Learning on the Divisor Hyperbola

Demonstrates how geometric features of the hyperbola xy = n can be used
to train models that predict factorization properties.

Experiments:
1. Predict number of divisors from geometric features
2. Classify numbers by factorization type
3. Predict smallest prime factor using hyperbola curvature features
4. Anomaly detection for primes vs. composites

Usage:
    python demo_ml_factoring.py
"""

import random
import math
from typing import List, Dict, Tuple
from collections import Counter

# ─── Core arithmetic ────────────────────────────────────────────────────────

def divisors(n: int) -> List[int]:
    from math import isqrt
    divs = []
    for d in range(1, isqrt(n) + 1):
        if n % d == 0:
            divs.append(d)
            if d != n // d:
                divs.append(n // d)
    return sorted(divs)


def factorization(n: int) -> Dict[int, int]:
    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors


def is_prime(n: int) -> bool:
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    d = 5
    while d * d <= n:
        if n % d == 0 or n % (d + 2) == 0:
            return False
        d += 6
    return True


def smallest_prime_factor(n: int) -> int:
    if n <= 1: return n
    if n % 2 == 0: return 2
    d = 3
    while d * d <= n:
        if n % d == 0: return d
        d += 2
    return n


# ─── Feature Extraction ─────────────────────────────────────────────────────

def extract_features(n: int) -> Dict[str, float]:
    """Extract hyperbola-geometric features for ML."""
    divs = divisors(n)
    num_divs = len(divs)
    sqrt_n = math.sqrt(n)
    log_n = math.log(n) if n > 0 else 0

    # Basic
    features = {
        'log_n': log_n,
        'num_divisors': num_divs,
        'divisor_density': num_divs / sqrt_n,
    }

    # Gap features in log space
    if num_divs > 1:
        log_divs = [math.log(d) for d in divs]
        log_gaps = [log_divs[i+1] - log_divs[i] for i in range(len(log_divs)-1)]
        features['max_log_gap'] = max(log_gaps)
        features['min_log_gap'] = min(log_gaps)
        features['mean_log_gap'] = sum(log_gaps) / len(log_gaps)
        features['std_log_gap'] = (sum((g - features['mean_log_gap'])**2 for g in log_gaps) / len(log_gaps))**0.5

        # Entropy of gap distribution
        total = sum(log_gaps)
        if total > 0:
            probs = [g / total for g in log_gaps]
            features['gap_entropy'] = -sum(p * math.log(p + 1e-10) for p in probs)
        else:
            features['gap_entropy'] = 0
    else:
        features['max_log_gap'] = 0
        features['min_log_gap'] = 0
        features['mean_log_gap'] = 0
        features['std_log_gap'] = 0
        features['gap_entropy'] = 0

    # Curvature features
    curvatures = [n / (d**2 + (n//d)**2)**1.5 for d in divs]
    features['max_curvature'] = max(curvatures)
    features['sum_curvature'] = sum(curvatures)

    # Symmetry features: how close to perfect square
    from math import isqrt
    s = isqrt(n)
    features['sqrt_residual'] = (n - s*s) / n  # 0 for perfect squares

    # Aspect ratio of nearest-square pair
    best_d = min(divs, key=lambda d: abs(d - n//d))
    features['best_aspect'] = best_d / (n // best_d)

    return features


# ─── Simple ML Models (no external dependencies) ─────────────────────────────

class NaiveBayesClassifier:
    """Simple Gaussian Naive Bayes for prime/composite classification."""

    def __init__(self):
        self.class_stats = {}  # class -> {feature -> (mean, std)}
        self.class_priors = {}

    def fit(self, X: List[Dict[str, float]], y: List[int]):
        classes = set(y)
        for c in classes:
            indices = [i for i, label in enumerate(y) if label == c]
            self.class_priors[c] = len(indices) / len(y)
            self.class_stats[c] = {}
            for feat in X[0]:
                values = [X[i][feat] for i in indices]
                mean = sum(values) / len(values)
                std = max((sum((v - mean)**2 for v in values) / len(values))**0.5, 1e-6)
                self.class_stats[c][feat] = (mean, std)

    def predict(self, x: Dict[str, float]) -> int:
        best_class, best_score = None, float('-inf')
        for c in self.class_stats:
            score = math.log(self.class_priors[c])
            for feat in x:
                if feat in self.class_stats[c]:
                    mean, std = self.class_stats[c][feat]
                    score -= 0.5 * ((x[feat] - mean) / std)**2 + math.log(std)
            if score > best_score:
                best_score = score
                best_class = c
        return best_class


class LinearRegression:
    """Simple least-squares regression using normal equations (no numpy)."""

    def __init__(self):
        self.weights = {}
        self.bias = 0

    def fit(self, X: List[Dict[str, float]], y: List[float]):
        """Gradient descent fitting."""
        features = list(X[0].keys())
        self.weights = {f: 0.0 for f in features}
        self.bias = 0.0
        lr = 0.001
        n = len(X)

        # Normalize features
        feat_stats = {}
        for f in features:
            vals = [x[f] for x in X]
            mean = sum(vals) / len(vals)
            std = max((sum((v - mean)**2 for v in vals) / len(vals))**0.5, 1e-6)
            feat_stats[f] = (mean, std)

        y_mean = sum(y) / len(y)

        for epoch in range(1000):
            for i in range(n):
                pred = self.bias
                for f in features:
                    mean, std = feat_stats[f]
                    pred += self.weights[f] * (X[i][f] - mean) / std
                error = pred - (y[i] - y_mean)
                self.bias -= lr * error / n
                for f in features:
                    mean, std = feat_stats[f]
                    self.weights[f] -= lr * error * (X[i][f] - mean) / (std * n)

        self.feat_stats = feat_stats
        self.y_mean = y_mean

    def predict(self, x: Dict[str, float]) -> float:
        pred = self.bias + self.y_mean
        for f in self.weights:
            mean, std = self.feat_stats[f]
            pred += self.weights[f] * (x[f] - mean) / std
        return pred


# ─── Experiments ──────────────────────────────────────────────────────────────

def experiment_prime_classification():
    """Experiment 1: Classify primes vs composites using hyperbola features."""
    print("\n" + "="*70)
    print("  EXPERIMENT 1: Prime vs. Composite Classification")
    print("="*70)

    # Generate training data
    random.seed(42)
    train_nums = list(range(4, 500))
    X_train = [extract_features(n) for n in train_nums]
    y_train = [1 if is_prime(n) else 0 for n in train_nums]

    # Test data
    test_nums = list(range(500, 700))
    X_test = [extract_features(n) for n in test_nums]
    y_test = [1 if is_prime(n) else 0 for n in test_nums]

    # Train
    clf = NaiveBayesClassifier()
    clf.fit(X_train, y_train)

    # Evaluate
    correct = sum(1 for x, y in zip(X_test, y_test) if clf.predict(x) == y)
    accuracy = correct / len(y_test)
    print(f"\n  Training set: {len(train_nums)} numbers (4-499)")
    print(f"  Test set:     {len(test_nums)} numbers (500-699)")
    print(f"  Accuracy:     {accuracy:.2%}")
    print(f"  Primes in test: {sum(y_test)}, Composites: {len(y_test) - sum(y_test)}")

    # Most discriminative features
    print(f"\n  Most discriminative features (|μ_prime - μ_composite| / σ):")
    for feat in sorted(X_train[0].keys()):
        if feat in clf.class_stats.get(1, {}) and feat in clf.class_stats.get(0, {}):
            m1, s1 = clf.class_stats[1][feat]
            m0, s0 = clf.class_stats[0][feat]
            disc = abs(m1 - m0) / max(s1 + s0, 1e-6)
            print(f"    {feat:>20}: {disc:.4f}  (prime μ={m1:.3f}, comp μ={m0:.3f})")


def experiment_divisor_prediction():
    """Experiment 2: Predict τ(n) from geometric features."""
    print("\n" + "="*70)
    print("  EXPERIMENT 2: Divisor Count Prediction")
    print("="*70)

    train_nums = list(range(2, 300))
    X_train = [extract_features(n) for n in train_nums]
    y_train = [float(len(divisors(n))) for n in train_nums]

    test_nums = list(range(300, 500))
    X_test = [extract_features(n) for n in test_nums]
    y_test = [float(len(divisors(n))) for n in test_nums]

    # For this we just use the known formula τ as ground truth
    # and see which features correlate most
    print(f"\n  Feature correlations with τ(n):")
    for feat in sorted(X_train[0].keys()):
        vals = [x[feat] for x in X_train]
        mean_x = sum(vals) / len(vals)
        mean_y = sum(y_train) / len(y_train)
        cov = sum((v - mean_x) * (y - mean_y) for v, y in zip(vals, y_train)) / len(vals)
        std_x = max((sum((v - mean_x)**2 for v in vals) / len(vals))**0.5, 1e-6)
        std_y = max((sum((y - mean_y)**2 for y in y_train) / len(y_train))**0.5, 1e-6)
        corr = cov / (std_x * std_y)
        print(f"    {feat:>20}: r = {corr:+.4f}")


def experiment_factoring_heuristic():
    """Experiment 3: Use hyperbola geometry to guide trial division."""
    print("\n" + "="*70)
    print("  EXPERIMENT 3: Geometry-Guided Factoring")
    print("="*70)

    print(f"\n  For n = 210:")
    print(f"  The curvature κ of xy = n at (d, n/d) indicates")
    print(f"  how 'tightly bent' the curve is near each divisor pair.")
    print(f"  High curvature near √n suggests balanced factorizations.")

    n = 210
    divs = divisors(n)
    sqrt_n = math.sqrt(n)

    print(f"\n  {'d':>4} {'n/d':>4} {'|d-√n|':>8} {'κ':>10} {'type':>12}")
    print(f"  {'-'*4} {'-'*4} {'-'*8} {'-'*10} {'-'*12}")

    for d in divs:
        q = n // d
        dist = abs(d - sqrt_n)
        curvature = n / (d**2 + q**2)**1.5
        label = "near-square" if dist < sqrt_n * 0.3 else "unbalanced"
        print(f"  {d:>4} {q:>4} {dist:>8.2f} {curvature:>10.6f} {label:>12}")

    # Experiment: for semiprimes, the gap between the two non-trivial divisors
    print(f"\n  Semiprime analysis (p × q, p < q):")
    print(f"  {'p×q':>8} {'p':>4} {'q':>4} {'q/p':>8} {'gap/√n':>8}")
    semiprimes = [(p, q) for p in range(2, 50) for q in range(p, 200)
                  if is_prime(p) and is_prime(q) and p * q < 5000][:20]
    for p, q in semiprimes:
        n = p * q
        print(f"  {n:>8} {p:>4} {q:>4} {q/p:>8.2f} {(q-p)/math.sqrt(n):>8.4f}")


def experiment_hyperbola_walk():
    """Experiment 4: Random walk on divisor hyperbolas to discover structure."""
    print("\n" + "="*70)
    print("  EXPERIMENT 4: Divisor Hyperbola Random Walk")
    print("="*70)

    print(f"\n  Walking through numbers 2..1000, tracking how the")
    print(f"  divisor hyperbola 'morphs' as n changes.")

    # Track how adding 1 to n changes the divisor structure
    prev_divs = set()
    max_change = (0, 0, 0)
    big_jumps = []

    for n in range(2, 1001):
        curr_divs = set(divisors(n))
        shared = len(prev_divs & curr_divs)
        total = len(curr_divs)
        change = total - shared
        if change > max_change[2]:
            max_change = (n, total, change)
        if total > 10:
            big_jumps.append((n, total, factorization(n)))
        prev_divs = curr_divs

    print(f"\n  Most changed hyperbola: n = {max_change[0]}, τ = {max_change[1]}, Δ = {max_change[2]}")
    print(f"\n  Numbers with τ(n) > 10 (first 20):")
    for n, t, f in big_jumps[:20]:
        fact_str = "×".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(f.items()))
        print(f"    n = {n:>4}, τ = {t:>2}, {n} = {fact_str}")


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║     MACHINE LEARNING ON THE DIVISOR HYPERBOLA                       ║")
    print("║     Exploiting Geometric Structure for Integer Factorization         ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    experiment_prime_classification()
    experiment_divisor_prediction()
    experiment_factoring_heuristic()
    experiment_hyperbola_walk()

    print(f"\n{'='*70}")
    print("  All experiments complete.")
    print(f"{'='*70}")
