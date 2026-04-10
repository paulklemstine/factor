#!/usr/bin/env python3
"""
Machine Learning for Quadruple Division Factoring Demo

Demonstrates:
1. Feature engineering for factor-revealing quadruples
2. Simple neural network for factor prediction (using numpy only)
3. Reinforcement learning skeleton for 4D navigation
4. Graph structure analysis of the Berggren-Bridge graph
5. Data collection and analysis pipeline

Usage: python ml_factoring_demo.py
"""

from math import gcd, isqrt
from collections import defaultdict
import random

# ============================================================
# §1. Data Collection
# ============================================================

def find_quadruples(d_max=50):
    """Find all primitive Pythagorean quadruples with d ≤ d_max."""
    quads = []
    for d in range(1, d_max + 1):
        for a in range(0, d):
            for b in range(a, d):
                rem = d*d - a*a - b*b
                if rem < 0: break
                c = isqrt(rem)
                if c >= b and c*c == rem:
                    quads.append((a, b, c, d))
    return quads


def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i*i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True


def smallest_factor(n):
    """Return the smallest prime factor of n."""
    if n <= 1: return n
    if n % 2 == 0: return 2
    i = 3
    while i*i <= n:
        if n % i == 0: return i
        i += 2
    return n


def collect_training_data(N_max=200, d_max=60):
    """Collect (N, quadruple, factor_found) training data."""
    quads = find_quadruples(d_max)
    data = []

    composites = [n for n in range(6, N_max+1) if not is_prime(n) and n > 1]

    for N in composites:
        for q in quads:
            a, b, c, d = q
            # Check if this quadruple reveals a factor
            gcds = [
                gcd(d - c, N), gcd(d + c, N),
                gcd(d - b, N), gcd(d + b, N),
                gcd(d - a, N), gcd(d + a, N),
                gcd(a, N), gcd(b, N), gcd(c, N), gcd(d, N)
            ]
            nontrivial = [g for g in gcds if 1 < g < N and N % g == 0]
            found = len(nontrivial) > 0

            # Feature vector
            features = extract_features(N, a, b, c, d)
            data.append((features, 1 if found else 0, N, q))

    return data


def extract_features(N, a, b, c, d):
    """Extract features from (N, quadruple) for ML."""
    features = []

    # Basic ratios
    features.append(a / max(N, 1))        # a/N ratio
    features.append(b / max(N, 1))        # b/N ratio
    features.append(c / max(N, 1))        # c/N ratio
    features.append(d / max(N, 1))        # d/N ratio

    # Parity features
    features.append(a % 2)
    features.append(b % 2)
    features.append(c % 2)
    features.append(d % 2)

    # GCD features
    features.append(gcd(a, N) / max(N, 1))
    features.append(gcd(d - c, N) / max(N, 1))
    features.append(gcd(d + c, N) / max(N, 1))

    # Difference features
    features.append((d - c) / max(N, 1))
    features.append((d + c) / max(N, 1))

    # Modular features
    features.append(N % 4 / 4)
    features.append(d % N / max(N, 1) if N > 0 else 0)

    return features


# ============================================================
# §2. Simple Neural Network (NumPy-free, pure Python)
# ============================================================

class SimpleNeuralNet:
    """A simple 2-layer neural network for factor prediction."""

    def __init__(self, input_size=15, hidden_size=20, seed=42):
        random.seed(seed)
        self.w1 = [[random.gauss(0, 0.3) for _ in range(input_size)]
                    for _ in range(hidden_size)]
        self.b1 = [0.0] * hidden_size
        self.w2 = [random.gauss(0, 0.3) for _ in range(hidden_size)]
        self.b2 = 0.0
        self.lr = 0.01

    def sigmoid(self, x):
        if x > 10: return 1.0
        if x < -10: return 0.0
        from math import exp
        return 1.0 / (1.0 + exp(-x))

    def relu(self, x):
        return max(0.0, x)

    def forward(self, x):
        """Forward pass."""
        # Hidden layer
        self.h = []
        for j in range(len(self.w1)):
            z = self.b1[j] + sum(self.w1[j][i] * x[i] for i in range(len(x)))
            self.h.append(self.relu(z))

        # Output layer
        z_out = self.b2 + sum(self.w2[j] * self.h[j] for j in range(len(self.h)))
        self.output = self.sigmoid(z_out)
        return self.output

    def train_step(self, x, y):
        """One training step with backpropagation."""
        pred = self.forward(x)
        error = pred - y

        # Output layer gradients
        d_out = error * pred * (1 - pred)

        # Update output weights
        for j in range(len(self.w2)):
            self.w2[j] -= self.lr * d_out * self.h[j]
        self.b2 -= self.lr * d_out

        # Hidden layer gradients
        for j in range(len(self.w1)):
            if self.h[j] > 0:  # ReLU derivative
                d_h = d_out * self.w2[j]
                for i in range(len(x)):
                    self.w1[j][i] -= self.lr * d_h * x[i]
                self.b1[j] -= self.lr * d_h

        return error * error


def train_and_evaluate():
    """Train neural network to predict factor-revealing quadruples."""
    print("\n=== Neural Network Factor Prediction ===")
    print("Collecting training data...")

    data = collect_training_data(N_max=80, d_max=30)
    random.shuffle(data)

    # Split into train/test
    split = int(0.8 * len(data))
    train_data = data[:split]
    test_data = data[split:]

    print(f"  Training samples: {len(train_data)}")
    print(f"  Test samples: {len(test_data)}")

    # Count positive/negative
    pos_train = sum(1 for _, y, _, _ in train_data if y == 1)
    neg_train = len(train_data) - pos_train
    print(f"  Positive (factor found): {pos_train} ({100*pos_train/len(train_data):.1f}%)")
    print(f"  Negative (no factor):    {neg_train} ({100*neg_train/len(train_data):.1f}%)")

    # Train
    net = SimpleNeuralNet(input_size=15, hidden_size=20)
    epochs = 5
    for epoch in range(epochs):
        total_loss = 0
        for features, label, _, _ in train_data:
            loss = net.train_step(features, label)
            total_loss += loss
        avg_loss = total_loss / len(train_data)
        print(f"  Epoch {epoch+1}: avg loss = {avg_loss:.4f}")

    # Evaluate
    correct = 0
    tp, fp, tn, fn = 0, 0, 0, 0
    for features, label, _, _ in test_data:
        pred = net.forward(features)
        pred_label = 1 if pred > 0.5 else 0
        if pred_label == label:
            correct += 1
        if pred_label == 1 and label == 1: tp += 1
        if pred_label == 1 and label == 0: fp += 1
        if pred_label == 0 and label == 0: tn += 1
        if pred_label == 0 and label == 1: fn += 1

    acc = 100 * correct / len(test_data)
    print(f"\n  Test accuracy: {acc:.1f}%")
    print(f"  True positives: {tp}, False positives: {fp}")
    print(f"  True negatives: {tn}, False negatives: {fn}")
    if tp + fp > 0:
        precision = tp / (tp + fp)
        print(f"  Precision: {precision:.3f}")
    if tp + fn > 0:
        recall = tp / (tp + fn)
        print(f"  Recall: {recall:.3f}")


# ============================================================
# §3. Berggren-Bridge Graph Analysis
# ============================================================

def berggren_M1(a, b, c):
    return (a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c)

def berggren_M2(a, b, c):
    return (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c)

def berggren_M3(a, b, c):
    return (-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c)


def build_berggren_tree(depth=4):
    """Build the Berggren tree up to given depth."""
    tree = {}
    queue = [((3, 4, 5), 0)]
    while queue:
        triple, d = queue.pop(0)
        if d > depth:
            continue
        if triple in tree:
            continue
        tree[triple] = d
        for M in [berggren_M1, berggren_M2, berggren_M3]:
            child = M(*triple)
            if child[0] > 0 and child[1] > 0:
                queue.append((child, d + 1))
    return tree


def find_bridges(tree, d_max=100):
    """Find quadruple-mediated bridges between Berggren tree nodes."""
    bridges = []
    triples = list(tree.keys())

    for triple in triples:
        a, b, c = triple
        # Try to lift to quadruple: find k, d2 such that c² + k² = d2²
        for k in range(1, d_max):
            d2_sq = c*c + k*k
            d2 = isqrt(d2_sq)
            if d2*d2 == d2_sq:
                # Quadruple is (a, b, k, d2)
                # Try projection: √(a² + k²) = e?
                e_sq = a*a + k*k
                e = isqrt(e_sq)
                if e*e == e_sq and e > 0:
                    # New triple: (e, b, d2) -- check if b² + e² = d2²
                    if e*e + b*b == d2*d2:
                        new_triple = tuple(sorted([e, b]))
                        new_triple = (min(e, b), max(e, b), d2)
                        if new_triple in tree and new_triple != triple:
                            bridges.append((triple, new_triple, (a, b, k, d2)))

    return bridges


def graph_analysis():
    """Analyze the Berggren-Bridge graph."""
    print("\n=== Berggren-Bridge Graph Analysis ===")
    tree = build_berggren_tree(depth=4)
    print(f"  Berggren tree nodes: {len(tree)}")

    bridges = find_bridges(tree)
    print(f"  Bridge links found: {len(bridges)}")

    if bridges:
        print(f"\n  Sample bridges:")
        for src, dst, quad in bridges[:8]:
            d_src = tree[src]
            d_dst = tree[dst]
            jump = d_src - d_dst
            print(f"    {src} (depth {d_src}) → {dst} (depth {d_dst})"
                  f" via quad {quad} [jump={jump:+d}]")

    # Analyze bridge statistics
    if bridges:
        jumps = [tree[s] - tree[d] for s, d, _ in bridges]
        avg_jump = sum(jumps) / len(jumps)
        max_jump = max(jumps)
        upward = sum(1 for j in jumps if j > 0)
        print(f"\n  Bridge statistics:")
        print(f"    Average depth jump: {avg_jump:+.2f}")
        print(f"    Maximum upward jump: {max_jump}")
        print(f"    Upward bridges: {upward}/{len(bridges)}")


# ============================================================
# §4. Reinforcement Learning Skeleton
# ============================================================

class FactoringEnvironment:
    """MDP environment for factoring via 4D navigation."""

    def __init__(self, N):
        self.N = N
        self.target_factors = set()
        # Find actual factors for reward
        for i in range(2, isqrt(N) + 1):
            if N % i == 0:
                self.target_factors.add(i)
                self.target_factors.add(N // i)
        self.reset()

    def reset(self):
        """Reset to trivial quadruple."""
        if self.N % 2 == 1 and self.N >= 3:
            b = (self.N * self.N - 1) // 2
            c = (self.N * self.N + 1) // 2
            # Trivial quadruple: (N, 0, b, c) ← not valid, need c²+k²=d²
            # Use simpler: (1, 0, 0, 1) and navigate
            self.state = (1, 0, 0, 1)
        else:
            self.state = (2, 1, 0, isqrt(5))
        self.steps = 0
        self.found_factors = set()
        return self.state

    def step(self, action):
        """Take an action and return (next_state, reward, done)."""
        a, b, c, d = self.state

        # Actions: perturb one component, check nearby quadruples
        perturbations = [
            (a+1, b, c, d), (a-1, b, c, d),
            (a, b+1, c, d), (a, b-1, c, d),
            (a, b, c+1, d), (a, b, c-1, d),
            (a, b, c, d+1), (a, b, c, d-1),
        ]

        action_idx = action % len(perturbations)
        new_a, new_b, new_c, new_d = perturbations[action_idx]

        # Check if valid quadruple (approximately)
        if new_a**2 + new_b**2 + new_c**2 == new_d**2 and new_d > 0:
            self.state = (new_a, new_b, new_c, new_d)

            # Check for factor discovery
            reward = -0.01  # step cost
            gcds = [
                gcd(abs(new_d - new_c), self.N),
                gcd(abs(new_d + new_c), self.N),
                gcd(abs(new_a), self.N),
                gcd(abs(new_b), self.N),
            ]
            for g in gcds:
                if g in self.target_factors:
                    self.found_factors.add(g)
                    reward = 1.0
        else:
            reward = -0.1  # invalid move penalty

        self.steps += 1
        done = len(self.found_factors) == len(self.target_factors) or self.steps > 100

        return self.state, reward, done


def rl_demo():
    """Demo reinforcement learning for factoring."""
    print("\n=== Reinforcement Learning Navigation Demo ===")

    targets = [15, 21, 35, 77]
    for N in targets:
        env = FactoringEnvironment(N)
        state = env.reset()

        # Random policy (baseline)
        total_reward = 0
        for step in range(100):
            action = random.randint(0, 7)
            state, reward, done = env.step(action)
            total_reward += reward
            if done and env.found_factors:
                break

        found_str = str(sorted(env.found_factors)) if env.found_factors else "none"
        print(f"  N={N}: steps={env.steps}, reward={total_reward:.2f}, "
              f"factors found={found_str}")


# ============================================================
# §5. Feature Importance Analysis
# ============================================================

def feature_importance():
    """Analyze which features are most predictive of factor discovery."""
    print("\n=== Feature Importance Analysis ===")
    data = collect_training_data(N_max=60, d_max=25)

    feature_names = [
        "a/N ratio", "b/N ratio", "c/N ratio", "d/N ratio",
        "a parity", "b parity", "c parity", "d parity",
        "gcd(a,N)/N", "gcd(d-c,N)/N", "gcd(d+c,N)/N",
        "(d-c)/N", "(d+c)/N",
        "N mod 4", "d mod N / N"
    ]

    # Compute correlation between each feature and the label
    pos_data = [features for features, label, _, _ in data if label == 1]
    neg_data = [features for features, label, _, _ in data if label == 0]

    if not pos_data or not neg_data:
        print("  Insufficient data for analysis")
        return

    print(f"  {'Feature':<20} {'Pos Mean':>10} {'Neg Mean':>10} {'Diff':>10}")
    print("  " + "-" * 52)
    diffs = []
    for i, name in enumerate(feature_names):
        pos_mean = sum(f[i] for f in pos_data) / len(pos_data)
        neg_mean = sum(f[i] for f in neg_data) / len(neg_data)
        diff = abs(pos_mean - neg_mean)
        diffs.append((diff, name, pos_mean, neg_mean))

    diffs.sort(reverse=True)
    for diff, name, pos_mean, neg_mean in diffs:
        print(f"  {name:<20} {pos_mean:>10.4f} {neg_mean:>10.4f} {diff:>10.4f}")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Machine Learning for Quadruple Division Factoring      ║")
    print("║  Neural Networks, RL, and Graph Analysis                ║")
    print("╚══════════════════════════════════════════════════════════╝")

    train_and_evaluate()
    graph_analysis()
    rl_demo()
    feature_importance()

    print("\n" + "=" * 60)
    print("ML demo complete.")
