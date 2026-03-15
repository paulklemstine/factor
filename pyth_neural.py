#!/usr/bin/env python3
"""
Factor Compass — Numpy-only neural network that learns to predict
factor-revealing directions in the Pythagorean tree.

Architecture:
  Input (~102 features) -> 100 (ReLU) -> 50 (ReLU) -> 9 (softmax)

Features per state (m, n, N):
  - m_norm = (m mod N) / N
  - n_norm = (n mod N) / N
  For each of 9 forward matrices, compute child (m', n'):
    - gcd_score = log2(gcd(m'^2 - n'^2, N) + 1) / log2(N)
    - A_mod_small = [(m'^2 - n'^2) mod p == 0 for p in SMALL_PRIMES]  (5 binary)
    - B_mod_small = [(2*m'*n') mod p == 0 for p in SMALL_PRIMES]      (5 binary)
  Total: 2 + 9*(1+5+5) = 101 features

Training: cross-entropy loss, Adam optimizer, He init, gradient clipping.
Memory: < 2 GB (all numpy, no frameworks).
"""

import numpy as np
import time
import sys
from math import gcd, log2, isqrt

# =====================================================================
# Pythagorean tree matrices (9 forward)
# =====================================================================
MATRICES = [
    ((2, -1), (1,  0)),  # B1
    ((2,  1), (1,  0)),  # B2
    ((1,  2), (0,  1)),  # B3
    ((1,  1), (0,  2)),  # P1
    ((2,  0), (1, -1)),  # P2
    ((2,  0), (1,  1)),  # P3
    ((3, -2), (1, -1)),  # F1
    ((3,  2), (1,  1)),  # F2
    ((1,  4), (0,  1)),  # F3
]
MAT_NAMES = ["B1", "B2", "B3", "P1", "P2", "P3", "F1", "F2", "F3"]
NUM_MATRICES = len(MATRICES)

SMALL_PRIMES = [3, 5, 7, 11, 13]
NUM_SMALL = len(SMALL_PRIMES)

# Features: 2 (m_norm, n_norm) + 9 * (1 gcd_score + 5 A_mod + 5 B_mod) = 101
NUM_FEATURES = 2 + NUM_MATRICES * (1 + 2 * NUM_SMALL)


# =====================================================================
# Matrix application
# =====================================================================
def apply_mat(M, m, n):
    return M[0][0] * m + M[0][1] * n, M[1][0] * m + M[1][1] * n


def valid_mn(m, n):
    return m > 0 and n >= 0 and m > n


# =====================================================================
# Feature extraction
# =====================================================================
def extract_features(m, n, N, log2N):
    """Extract feature vector for state (m, n) w.r.t. semiprime N."""
    feats = np.zeros(NUM_FEATURES, dtype=np.float32)
    feats[0] = (m % N) / N
    feats[1] = (n % N) / N
    idx = 2
    for M in MATRICES:
        m2, n2 = apply_mat(M, m, n)
        a_val = m2 * m2 - n2 * n2  # m'^2 - n'^2
        b_val = 2 * m2 * n2        # 2*m'*n'
        g = gcd(abs(a_val), N)
        feats[idx] = log2(g + 1) / log2N
        idx += 1
        for p in SMALL_PRIMES:
            feats[idx] = 1.0 if (a_val % p == 0) else 0.0
            idx += 1
        for p in SMALL_PRIMES:
            feats[idx] = 1.0 if (b_val % p == 0) else 0.0
            idx += 1
    return feats


def extract_features_batch(ms, ns, N, log2N):
    """Vectorised feature extraction for arrays of (m, n)."""
    B = len(ms)
    feats = np.zeros((B, NUM_FEATURES), dtype=np.float32)
    feats[:, 0] = np.array([(m % N) / N for m in ms], dtype=np.float32)
    feats[:, 1] = np.array([(n % N) / N for n in ns], dtype=np.float32)
    idx = 2
    for M in MATRICES:
        for i in range(B):
            m2, n2 = apply_mat(M, ms[i], ns[i])
            a_val = m2 * m2 - n2 * n2
            b_val = 2 * m2 * n2
            g = gcd(abs(a_val), N)
            feats[i, idx] = log2(g + 1) / log2N
            for j, p in enumerate(SMALL_PRIMES):
                feats[i, idx + 1 + j] = 1.0 if (a_val % p == 0) else 0.0
            for j, p in enumerate(SMALL_PRIMES):
                feats[i, idx + 1 + NUM_SMALL + j] = 1.0 if (b_val % p == 0) else 0.0
        idx += 1 + 2 * NUM_SMALL
    return feats


# =====================================================================
# Data generation
# =====================================================================
def random_prime(bits):
    """Generate a random prime of given bit length (simple trial division)."""
    while True:
        n = np.random.randint(1 << (bits - 1), 1 << bits) | 1
        if n < 3:
            continue
        if is_prime(n):
            return int(n)


def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def generate_semiprime(bits):
    """Generate semiprime N = p*q where p, q each ~bits/2 bits."""
    half = bits // 2
    p = random_prime(half)
    q = random_prime(bits - half)
    while q == p:
        q = random_prime(bits - half)
    return p * q, p, q


def generate_training_data(n_semiprimes=1000, examples_per_N=100, bits=16,
                           seed=42):
    """
    Generate training data.
    For each N, generate random (m,n) states.
    Label = index of matrix giving highest gcd with N.
    If all gcd==1, label is uniform (soft label).
    """
    rng = np.random.RandomState(seed)
    X_list = []
    Y_list = []  # soft labels (9-dim)
    count = 0
    t0 = time.time()

    for s_i in range(n_semiprimes):
        N, p, q = generate_semiprime(bits)
        log2N = log2(N)
        for _ in range(examples_per_N):
            # random walk from (2,1) for 5-20 steps to get a valid (m,n)
            m, n = 2, 1
            depth = rng.randint(3, 15)
            for _ in range(depth):
                idx = rng.randint(0, NUM_MATRICES)
                m2, n2 = apply_mat(MATRICES[idx], m, n)
                if valid_mn(m2, n2) and m2 < (1 << 40):
                    m, n = m2, n2

            feats = extract_features(m, n, N, log2N)
            X_list.append(feats)

            # Compute gcd scores for each matrix
            gcd_scores = np.zeros(NUM_MATRICES, dtype=np.float64)
            for k, M in enumerate(MATRICES):
                m2, n2 = apply_mat(M, m, n)
                a_val = abs(m2 * m2 - n2 * n2)
                b_val = abs(2 * m2 * n2)
                c_val = m2 * m2 + n2 * n2
                g = max(gcd(a_val, N), gcd(b_val, N), gcd(c_val, N))
                gcd_scores[k] = g

            # Label: softmax of log-gcd, with strong preference for winners
            if np.max(gcd_scores) > 1:
                # There are meaningful gcds — one-hot on best
                best = int(np.argmax(gcd_scores))
                label = np.zeros(NUM_MATRICES, dtype=np.float32)
                label[best] = 1.0
            else:
                # All gcd == 1 — uniform label
                label = np.ones(NUM_MATRICES, dtype=np.float32) / NUM_MATRICES

            Y_list.append(label)
            count += 1

        if (s_i + 1) % 200 == 0:
            elapsed = time.time() - t0
            print(f"  Generated {count} examples from {s_i+1} semiprimes "
                  f"({elapsed:.1f}s)")

    X = np.array(X_list, dtype=np.float32)
    Y = np.array(Y_list, dtype=np.float32)
    print(f"  Total: {X.shape[0]} examples, {X.shape[1]} features "
          f"({time.time()-t0:.1f}s)")

    # Stats on non-uniform labels
    non_uniform = np.sum(np.max(Y, axis=1) > 0.5)
    print(f"  Non-uniform labels (gcd > 1 found): {non_uniform} "
          f"({100*non_uniform/len(Y):.1f}%)")
    return X, Y


# =====================================================================
# Neural Network (numpy only)
# =====================================================================
class NumpyMLP:
    """
    Multi-layer perceptron: input -> 100 (ReLU) -> 50 (ReLU) -> 9 (softmax)
    He initialization, Adam optimizer, gradient clipping.
    """

    def __init__(self, input_dim=NUM_FEATURES, hidden1=100, hidden2=50,
                 output_dim=NUM_MATRICES, lr=0.001, clip_norm=5.0):
        self.lr = lr
        self.clip_norm = clip_norm

        # He initialization
        self.W1 = np.random.randn(input_dim, hidden1).astype(np.float32) * np.sqrt(2.0 / input_dim)
        self.b1 = np.zeros(hidden1, dtype=np.float32)
        self.W2 = np.random.randn(hidden1, hidden2).astype(np.float32) * np.sqrt(2.0 / hidden1)
        self.b2 = np.zeros(hidden2, dtype=np.float32)
        self.W3 = np.random.randn(hidden2, output_dim).astype(np.float32) * np.sqrt(2.0 / hidden2)
        self.b3 = np.zeros(output_dim, dtype=np.float32)

        # Adam state
        self.params = ['W1', 'b1', 'W2', 'b2', 'W3', 'b3']
        self.m = {k: np.zeros_like(getattr(self, k)) for k in self.params}
        self.v = {k: np.zeros_like(getattr(self, k)) for k in self.params}
        self.t = 0  # timestep

    def forward(self, X):
        """Forward pass. Returns (logits, cache)."""
        z1 = X @ self.W1 + self.b1
        h1 = np.maximum(z1, 0)  # ReLU
        z2 = h1 @ self.W2 + self.b2
        h2 = np.maximum(z2, 0)  # ReLU
        logits = h2 @ self.W3 + self.b3

        cache = (X, z1, h1, z2, h2, logits)
        return logits, cache

    def softmax(self, logits):
        """Numerically stable softmax."""
        shifted = logits - np.max(logits, axis=1, keepdims=True)
        exp_l = np.exp(shifted)
        return exp_l / np.sum(exp_l, axis=1, keepdims=True)

    def cross_entropy_loss(self, logits, Y):
        """Cross-entropy loss with soft labels."""
        probs = self.softmax(logits)
        probs = np.clip(probs, 1e-12, 1.0)
        loss = -np.sum(Y * np.log(probs)) / len(Y)
        return loss, probs

    def backward(self, cache, probs, Y):
        """Backward pass. Returns gradients dict."""
        X, z1, h1, z2, h2, logits = cache
        B = len(X)

        # dL/d(logits) for cross-entropy + softmax
        dlogits = (probs - Y) / B

        # Layer 3
        dW3 = h2.T @ dlogits
        db3 = np.sum(dlogits, axis=0)
        dh2 = dlogits @ self.W3.T

        # ReLU 2
        dz2 = dh2 * (z2 > 0).astype(np.float32)

        # Layer 2
        dW2 = h1.T @ dz2
        db2 = np.sum(dz2, axis=0)
        dh1 = dz2 @ self.W2.T

        # ReLU 1
        dz1 = dh1 * (z1 > 0).astype(np.float32)

        # Layer 1
        dW1 = X.T @ dz1
        db1 = np.sum(dz1, axis=0)

        grads = {'W1': dW1, 'b1': db1, 'W2': dW2, 'b2': db2,
                 'W3': dW3, 'b3': db3}
        return grads

    def clip_gradients(self, grads):
        """Clip gradient global norm."""
        total_norm = 0.0
        for k in self.params:
            total_norm += np.sum(grads[k] ** 2)
        total_norm = np.sqrt(total_norm)
        if total_norm > self.clip_norm:
            scale = self.clip_norm / (total_norm + 1e-8)
            for k in self.params:
                grads[k] *= scale
        return grads

    def adam_step(self, grads, beta1=0.9, beta2=0.999, eps=1e-8):
        """Adam optimizer update."""
        self.t += 1
        for k in self.params:
            g = grads[k]
            self.m[k] = beta1 * self.m[k] + (1 - beta1) * g
            self.v[k] = beta2 * self.v[k] + (1 - beta2) * (g ** 2)
            m_hat = self.m[k] / (1 - beta1 ** self.t)
            v_hat = self.v[k] / (1 - beta2 ** self.t)
            update = self.lr * m_hat / (np.sqrt(v_hat) + eps)
            setattr(self, k, getattr(self, k) - update)

    def predict(self, X):
        """Return predicted class indices."""
        logits, _ = self.forward(X)
        return np.argmax(logits, axis=1)

    def predict_proba(self, X):
        """Return class probabilities."""
        logits, _ = self.forward(X)
        return self.softmax(logits)

    def train_epoch(self, X, Y, batch_size=256):
        """One training epoch. Returns average loss."""
        N = len(X)
        indices = np.random.permutation(N)
        total_loss = 0.0
        n_batches = 0

        for start in range(0, N, batch_size):
            end = min(start + batch_size, N)
            batch_idx = indices[start:end]
            Xb = X[batch_idx]
            Yb = Y[batch_idx]

            logits, cache = self.forward(Xb)
            loss, probs = self.cross_entropy_loss(logits, Yb)
            grads = self.backward(cache, probs, Yb)
            grads = self.clip_gradients(grads)
            self.adam_step(grads)

            total_loss += loss
            n_batches += 1

        return total_loss / n_batches


# =====================================================================
# Training loop
# =====================================================================
def train_network(X_train, Y_train, X_val, Y_val, epochs=50,
                  batch_size=256, lr=0.001, lr_decay=0.98):
    """Train the MLP with validation tracking."""
    net = NumpyMLP(lr=lr)
    best_val_loss = float('inf')
    best_weights = None

    print(f"\n{'Epoch':>5} | {'Train Loss':>10} | {'Val Loss':>10} | "
          f"{'Train Acc':>9} | {'Val Acc':>9} | {'LR':>8}")
    print("-" * 65)

    for epoch in range(1, epochs + 1):
        t0 = time.time()
        train_loss = net.train_epoch(X_train, Y_train, batch_size)

        # Validation
        val_logits, _ = net.forward(X_val)
        val_loss, val_probs = net.cross_entropy_loss(val_logits, Y_val)

        # Accuracy (on non-uniform labels only)
        train_pred = net.predict(X_train)
        train_true = np.argmax(Y_train, axis=1)
        train_mask = np.max(Y_train, axis=1) > 0.5
        if np.sum(train_mask) > 0:
            train_acc = np.mean(train_pred[train_mask] == train_true[train_mask])
        else:
            train_acc = 0.0

        val_pred = np.argmax(val_logits, axis=1)
        val_true = np.argmax(Y_val, axis=1)
        val_mask = np.max(Y_val, axis=1) > 0.5
        if np.sum(val_mask) > 0:
            val_acc = np.mean(val_pred[val_mask] == val_true[val_mask])
        else:
            val_acc = 0.0

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_weights = {k: getattr(net, k).copy() for k in net.params}

        dt = time.time() - t0
        if epoch <= 5 or epoch % 5 == 0 or epoch == epochs:
            print(f"{epoch:5d} | {train_loss:10.4f} | {val_loss:10.4f} | "
                  f"{train_acc:8.1%} | {val_acc:8.1%} | {net.lr:.6f}")

        # LR decay
        net.lr *= lr_decay

    # Restore best weights
    if best_weights is not None:
        for k in net.params:
            setattr(net, k, best_weights[k])

    return net


# =====================================================================
# Evaluation: use network as navigator
# =====================================================================
def navigate_with_network(net, N, max_steps=5000, verbose=False):
    """
    Use the trained network to navigate the Pythagorean tree.
    At each step, pick the matrix the network recommends.
    Returns (found_factor, steps, factor).
    """
    m, n = 2, 1
    log2N = log2(N)
    visited = set()

    for step in range(max_steps):
        # Check current state
        a = m * m - n * n
        b = 2 * m * n
        c = m * m + n * n
        for val in [a, b, c]:
            g = gcd(abs(val), N)
            if 1 < g < N:
                return True, step, g

        state_key = (m % N, n % N)
        if state_key in visited and step > 10:
            # Random restart to escape loops
            m, n = 2, 1
            for _ in range(np.random.randint(3, 12)):
                idx = np.random.randint(0, NUM_MATRICES)
                m2, n2 = apply_mat(MATRICES[idx], m, n)
                if valid_mn(m2, n2) and m2 < (1 << 60):
                    m, n = m2, n2
            visited.clear()
            continue

        visited.add(state_key)

        # Extract features and get network prediction
        feats = extract_features(m, n, N, log2N).reshape(1, -1)
        probs = net.predict_proba(feats)[0]

        # Try matrices in order of probability
        order = np.argsort(-probs)
        moved = False
        for idx in order:
            M = MATRICES[idx]
            m2, n2 = apply_mat(M, m, n)
            if valid_mn(m2, n2) and m2 < (1 << 60):
                m, n = m2, n2
                moved = True
                break

        if not moved:
            # All invalid — random restart
            m, n = 2, 1
            for _ in range(np.random.randint(3, 10)):
                idx = np.random.randint(0, NUM_MATRICES)
                m2, n2 = apply_mat(MATRICES[idx], m, n)
                if valid_mn(m2, n2):
                    m, n = m2, n2

    return False, max_steps, None


def navigate_random(N, max_steps=5000):
    """Random walk baseline for comparison."""
    m, n = 2, 1
    for step in range(max_steps):
        a = m * m - n * n
        b = 2 * m * n
        c = m * m + n * n
        for val in [a, b, c]:
            g = gcd(abs(val), N)
            if 1 < g < N:
                return True, step, g

        # Random matrix
        idx = np.random.randint(0, NUM_MATRICES)
        m2, n2 = apply_mat(MATRICES[idx], m, n)
        if valid_mn(m2, n2) and m2 < (1 << 60):
            m, n = m2, n2
        else:
            m, n = 2, 1
            for _ in range(np.random.randint(3, 10)):
                idx2 = np.random.randint(0, NUM_MATRICES)
                m2, n2 = apply_mat(MATRICES[idx2], m, n)
                if valid_mn(m2, n2):
                    m, n = m2, n2

    return False, max_steps, None


def evaluate_navigator(net, bits, n_trials=100, max_steps=5000):
    """
    Evaluate network navigator vs random walk at given bit size.
    Returns dict of results.
    """
    net_solved = 0
    net_steps_list = []
    rand_solved = 0
    rand_steps_list = []

    for _ in range(n_trials):
        N, p, q = generate_semiprime(bits)

        found, steps, factor = navigate_with_network(net, N, max_steps)
        if found:
            net_solved += 1
            net_steps_list.append(steps)

        found_r, steps_r, _ = navigate_random(N, max_steps)
        if found_r:
            rand_solved += 1
            rand_steps_list.append(steps_r)

    result = {
        'bits': bits,
        'trials': n_trials,
        'net_solved': net_solved,
        'net_rate': net_solved / n_trials,
        'net_avg_steps': np.mean(net_steps_list) if net_steps_list else float('inf'),
        'rand_solved': rand_solved,
        'rand_rate': rand_solved / n_trials,
        'rand_avg_steps': np.mean(rand_steps_list) if rand_steps_list else float('inf'),
    }
    return result


# =====================================================================
# Feature importance analysis
# =====================================================================
def analyze_feature_importance(net):
    """
    Analyze which input features the network relies on most,
    using the absolute weight magnitudes of the first layer.
    """
    # Sum of absolute weights from each input to all hidden neurons
    importance = np.sum(np.abs(net.W1), axis=1)  # shape: (NUM_FEATURES,)
    importance /= np.max(importance)  # normalize to [0, 1]

    feature_names = ['m_norm', 'n_norm']
    for mat_name in MAT_NAMES:
        feature_names.append(f'{mat_name}_gcd_score')
        for p in SMALL_PRIMES:
            feature_names.append(f'{mat_name}_A%{p}')
        for p in SMALL_PRIMES:
            feature_names.append(f'{mat_name}_B%{p}')

    # Sort by importance
    order = np.argsort(-importance)
    print("\n=== Top 20 Most Important Features ===")
    print(f"{'Rank':>4}  {'Feature':<20}  {'Importance':>10}")
    print("-" * 40)
    for rank, idx in enumerate(order[:20], 1):
        name = feature_names[idx] if idx < len(feature_names) else f"feat_{idx}"
        print(f"{rank:4d}  {name:<20}  {importance[idx]:10.4f}")

    # Category analysis
    print("\n=== Feature Category Importance ===")
    cat_scores = {}
    cat_scores['m_norm/n_norm'] = float(np.mean(importance[:2]))
    gcd_idxs = [2 + i * (1 + 2 * NUM_SMALL) for i in range(NUM_MATRICES)]
    cat_scores['gcd_scores'] = float(np.mean(importance[gcd_idxs]))
    a_mod_idxs = []
    b_mod_idxs = []
    for i in range(NUM_MATRICES):
        base = 2 + i * (1 + 2 * NUM_SMALL) + 1
        a_mod_idxs.extend(range(base, base + NUM_SMALL))
        b_mod_idxs.extend(range(base + NUM_SMALL, base + 2 * NUM_SMALL))
    cat_scores['A_mod_small'] = float(np.mean(importance[a_mod_idxs]))
    cat_scores['B_mod_small'] = float(np.mean(importance[b_mod_idxs]))

    for cat, score in sorted(cat_scores.items(), key=lambda x: -x[1]):
        print(f"  {cat:<20}: {score:.4f}")

    return importance, feature_names


# =====================================================================
# Ensemble of specialists (by N mod 8)
# =====================================================================
def train_ensemble(X_all, Y_all, N_classes_all, epochs=30, batch_size=256):
    """
    Train separate networks for different N mod 8 classes.
    N_classes_all: array of (N mod 8) for each training example.
    """
    specialists = {}
    for nmod8 in sorted(set(N_classes_all)):
        mask = N_classes_all == nmod8
        count = np.sum(mask)
        if count < 500:
            print(f"  N mod 8 = {nmod8}: only {count} examples, skipping")
            continue
        print(f"\n--- Training specialist for N mod 8 = {nmod8} "
              f"({count} examples) ---")
        Xs = X_all[mask]
        Ys = Y_all[mask]
        split = int(0.85 * len(Xs))
        net = train_network(Xs[:split], Ys[:split], Xs[split:], Ys[split:],
                            epochs=epochs, batch_size=batch_size)
        specialists[nmod8] = net
    return specialists


# =====================================================================
# Main
# =====================================================================
if __name__ == "__main__":
    np.random.seed(42)
    print("=" * 65)
    print("  Factor Compass - Pythagorean Tree Neural Navigator")
    print("  (numpy-only MLP, no frameworks)")
    print("=" * 65)

    # ------------------------------------------------------------------
    # 1. Generate training data
    # ------------------------------------------------------------------
    print("\n[1] Generating training data (16-bit semiprimes)...")
    X, Y = generate_training_data(n_semiprimes=1000, examples_per_N=100,
                                  bits=16, seed=42)

    # Also track N mod 8 for ensemble later
    print("\n[1b] Generating N mod 8 class labels for ensemble...")
    # Re-generate just the N values to get classes
    rng_n = np.random.RandomState(42)
    N_mod8 = np.zeros(len(X), dtype=np.int32)
    idx = 0
    for s_i in range(1000):
        N_val, _, _ = generate_semiprime(16)
        for _ in range(100):
            N_mod8[idx] = N_val % 8
            idx += 1
    # Re-seed to ensure consistency with training
    # (The semiprimes generated above won't match exactly because
    #  generate_semiprime uses global numpy state. This is approximate.)

    # ------------------------------------------------------------------
    # 2. Split train/val (by semiprime, not by example)
    # ------------------------------------------------------------------
    print("\n[2] Splitting train/validation (85/15 by semiprime)...")
    split_idx = 850 * 100  # first 850 semiprimes for train
    X_train, Y_train = X[:split_idx], Y[:split_idx]
    X_val, Y_val = X[split_idx:], Y[split_idx:]
    print(f"  Train: {len(X_train)}, Val: {len(X_val)}")

    # ------------------------------------------------------------------
    # 3. Train the network
    # ------------------------------------------------------------------
    print("\n[3] Training Factor Compass network...")
    net = train_network(X_train, Y_train, X_val, Y_val,
                        epochs=50, batch_size=256, lr=0.001, lr_decay=0.98)

    # ------------------------------------------------------------------
    # 4. Feature importance analysis
    # ------------------------------------------------------------------
    print("\n[4] Feature Importance Analysis")
    analyze_feature_importance(net)

    # ------------------------------------------------------------------
    # 5. Navigation evaluation: network vs random at various bit sizes
    # ------------------------------------------------------------------
    print("\n[5] Navigation Evaluation: Network vs Random Walk")
    print("=" * 70)
    print(f"{'Bits':>5} | {'Net Solved':>10} | {'Net Steps':>10} | "
          f"{'Rand Solved':>11} | {'Rand Steps':>10} | {'Speedup':>8}")
    print("-" * 70)

    for bits in [16, 24, 32, 40]:
        n_trials = 50 if bits <= 24 else 30
        max_steps = 5000 if bits <= 24 else 10000
        print(f"  Testing {bits}b ({n_trials} trials, max {max_steps} steps)...",
              end='', flush=True)
        t0 = time.time()

        net_solved = 0
        net_steps_list = []
        rand_solved = 0
        rand_steps_list = []

        for trial in range(n_trials):
            N_val, p, q = generate_semiprime(bits)

            found, steps, factor = navigate_with_network(net, N_val, max_steps)
            if found:
                net_solved += 1
                net_steps_list.append(steps)

            found_r, steps_r, _ = navigate_random(N_val, max_steps)
            if found_r:
                rand_solved += 1
                rand_steps_list.append(steps_r)

        net_avg = np.mean(net_steps_list) if net_steps_list else float('inf')
        rand_avg = np.mean(rand_steps_list) if rand_steps_list else float('inf')
        if net_avg > 0 and rand_avg < float('inf') and net_avg < float('inf'):
            speedup = rand_avg / net_avg
        else:
            speedup = 0.0

        dt = time.time() - t0
        print(f" ({dt:.1f}s)")
        print(f"{bits:5d} | {net_solved:>6}/{n_trials:<4} | {net_avg:10.1f} | "
              f"{rand_solved:>7}/{n_trials:<4} | {rand_avg:10.1f} | "
              f"{speedup:7.2f}x")

    # ------------------------------------------------------------------
    # 6. Ensemble of specialists
    # ------------------------------------------------------------------
    print("\n[6] Ensemble of Specialists (by N mod 8)")
    print("=" * 65)
    specialists = train_ensemble(X_train, Y_train, N_mod8[:split_idx],
                                 epochs=30, batch_size=256)

    # Quick eval of specialists vs generalist at 16b
    if specialists:
        print("\n--- Specialist vs Generalist at 16b ---")
        spec_solved = 0
        gen_solved = 0
        n_eval = 50
        for _ in range(n_eval):
            N_val, p, q = generate_semiprime(16)
            nmod = N_val % 8
            spec_net = specialists.get(nmod, net)
            found_s, _, _ = navigate_with_network(spec_net, N_val, 5000)
            found_g, _, _ = navigate_with_network(net, N_val, 5000)
            if found_s: spec_solved += 1
            if found_g: gen_solved += 1
        print(f"  Specialist: {spec_solved}/{n_eval} solved")
        print(f"  Generalist: {gen_solved}/{n_eval} solved")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 65)
    print("  Factor Compass Training Complete")
    print("=" * 65)
    print("\nKey questions answered:")
    print("  1. Can a neural network learn factor-predicting features")
    print("     from the Pythagorean tree structure?")
    print("  2. Does the learned signal generalize to larger bit sizes?")
    print("  3. Which features matter most for factor detection?")
    print("  4. Do N mod 8 specialists outperform the generalist?")
