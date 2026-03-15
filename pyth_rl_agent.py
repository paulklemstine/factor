#!/usr/bin/env python3
"""
Pythagorean Tree RL Agent for Integer Factoring
================================================
Train an RL agent on SMALL semiprimes (16-24 bit) to learn which Berggren
matrix to apply at each (m,n) node. Test if learned policy GENERALIZES
to larger semiprimes (32-48 bit).

The critical question: can the agent learn a gradient toward factors that
random walk cannot see?

Algorithms implemented (numpy only, no TF/PyTorch):
  1. Tabular Q-Learning (discretized state)
  2. Linear Q-Learning (feature-based)
  3. Neural Q-Network (2-layer MLP, numpy)
  4. REINFORCE Policy Gradient

Memory budget: <2GB total.
"""

import numpy as np
import random
import time
import sys
from math import gcd, log2, log, isqrt
from collections import defaultdict

# ============================================================
# PYTHAGOREAN TREE INFRASTRUCTURE
# ============================================================

# Berggren (m,n) matrices — operate on the (m,n) parameterization
# where a = m^2 - n^2, b = 2mn, c = m^2 + n^2
B1 = ((2, -1), (1, 0))
B2 = ((2, 1), (1, 0))
B3 = ((1, 2), (0, 1))

# Price matrices
P1 = ((1, 1), (0, 2))
P2 = ((2, 0), (1, -1))
P3 = ((2, 0), (1, 1))

# Fibonacci matrices
F1 = ((3, -2), (1, -1))
F2 = ((3, 2), (1, 1))
F3 = ((1, 4), (0, 1))

FORWARD = [B1, B2, B3, P1, P2, P3, F1, F2, F3]

# Inverse Berggren matrices (for climbing back up)
B1i = ((0, 1), (-1, 2))
B2i = ((0, 1), (1, -2))
B3i = ((1, -2), (0, 1))
INVERSE = [B1i, B2i, B3i]

ALL_MATS = FORWARD + INVERSE
N_ACTIONS = len(ALL_MATS)  # 12 actions

ACTION_NAMES = [
    "B1", "B2", "B3", "P1", "P2", "P3", "F1", "F2", "F3",
    "B1i", "B2i", "B3i"
]


def apply_mat(M, m, n):
    """Apply 2x2 matrix to (m, n)."""
    return M[0][0] * m + M[0][1] * n, M[1][0] * m + M[1][1] * n


def valid(m, n):
    """Check if (m, n) is a valid Pythagorean generator: m > n >= 0."""
    return m > 0 and n >= 0 and m > n


def derived_values(m, n):
    """Compute all derived values from (m, n) that might share a factor with N."""
    if not valid(m, n):
        return []
    a = m * m - n * n
    b = 2 * m * n
    c = m * m + n * n
    d = m - n
    s = m + n
    return [v for v in [a, b, c, m, n, d, s, d * d, s * s] if v > 0]


def check_factor(N, m, n):
    """Check if any derived value from (m,n) shares a nontrivial factor with N."""
    for v in derived_values(m, n):
        g = gcd(v, N)
        if 1 < g < N:
            return g
    return None


def max_gcd(N, m, n):
    """Return the largest gcd of any derived value with N."""
    best = 1
    for v in derived_values(m, n):
        g = gcd(v, N)
        if g > best and g < N:
            best = g
    return best


# ============================================================
# SEMIPRIME GENERATION
# ============================================================

def miller_rabin(n, witnesses=(2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)):
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for a in witnesses:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def gen_semi(bits):
    """Generate a semiprime with each factor having `bits` bits."""
    half = bits // 2
    if half < 3:
        half = 3
    while True:
        p = random.getrandbits(half) | (1 << (half - 1)) | 1
        if miller_rabin(p):
            break
    while True:
        q = random.getrandbits(half) | (1 << (half - 1)) | 1
        if q != p and miller_rabin(q):
            break
    return min(p, q), max(p, q), p * q


# ============================================================
# FEATURE EXTRACTION
# ============================================================

# Small primes for quadratic residue features
SMALL_PRIMES = [3, 5, 7, 11, 13, 17, 19, 23]


def extract_features(N, m, n):
    """
    Extract a feature vector from state (m, n, N).
    Returns numpy array of ~40 floats in [0, 1] range.
    """
    features = []

    # 1. Normalized position (2 features)
    m_mod = (m % N) / N
    n_mod = (n % N) / N
    features.extend([m_mod, n_mod])

    # 2. Derived values mod N, normalized (5 features)
    a = m * m - n * n
    b = 2 * m * n
    c = m * m + n * n
    d = m - n
    s = m + n
    for v in [a, b, c, d, s]:
        if v > 0:
            features.append((v % N) / N)
        else:
            features.append(0.0)

    # 3. GCD proximity — log scale (1 feature)
    # Combined gcd of all derived values
    combined = a * b * d * s if (a > 0 and b > 0 and d > 0 and s > 0) else 1
    if combined > 0:
        g = gcd(abs(combined), N)
    else:
        g = 1
    log_N = max(log2(N), 1.0)
    gcd_feat = log2(max(g, 1)) / log_N
    features.append(gcd_feat)

    # 4. Individual gcd features (5 features)
    for v in [a, b, c, d, s]:
        if v > 0:
            g = gcd(v, N)
            features.append(log2(max(g, 1)) / log_N)
        else:
            features.append(0.0)

    # 5. Quadratic residue features: a mod p, b mod p (16 features)
    for p in SMALL_PRIMES:
        features.append((a % p) / p if a > 0 else 0.0)
        features.append((b % p) / p if b > 0 else 0.0)

    # 6. Ratio features: m/n approx (2 features)
    if n > 0:
        ratio = m / n
        features.append(min(ratio / 10.0, 1.0))  # capped
        features.append((ratio % 1.0))  # fractional part
    else:
        features.extend([1.0, 0.0])

    # 7. Size features (2 features)
    features.append(min(log2(max(m, 1)) / log_N, 1.0))
    features.append(min(log2(max(n, 1)) / log_N, 1.0))

    # 8. Parity features (4 features)
    features.append(float(m % 2))
    features.append(float(n % 2))
    features.append(float(a % 2) if a > 0 else 0.0)
    features.append(float(b % 2) if b > 0 else 0.0)

    return np.array(features, dtype=np.float64)


N_FEATURES = 37  # Count of features above


# ============================================================
# RANDOM WALK BASELINE
# ============================================================

def random_walk_factor(N, max_steps=5000):
    """Random walk baseline: pick random action each step."""
    m, n = 2, 1  # Start at primitive triple (3, 4, 5)
    for step in range(max_steps):
        f = check_factor(N, m, n)
        if f is not None:
            return f, step + 1
        # Random action
        for _ in range(10):
            idx = random.randint(0, N_ACTIONS - 1)
            m2, n2 = apply_mat(ALL_MATS[idx], m, n)
            if valid(m2, n2):
                m, n = m2, n2
                break
    return None, max_steps


# ============================================================
# ENVIRONMENT
# ============================================================

class PythTreeEnv:
    """Pythagorean Tree factoring environment."""

    def __init__(self, N, max_steps=5000):
        self.N = N
        self.max_steps = max_steps
        self.reset()

    def reset(self):
        self.m, self.n = 2, 1
        self.step_count = 0
        self.prev_gcd = 1
        self.done = False
        self.factor = None
        return self._get_state()

    def _get_state(self):
        return extract_features(self.N, self.m, self.n)

    def step(self, action):
        """Take action, return (next_state, reward, done, info)."""
        if self.done:
            return self._get_state(), 0.0, True, {}

        self.step_count += 1

        # Apply matrix
        M = ALL_MATS[action]
        m2, n2 = apply_mat(M, self.m, self.n)

        if not valid(m2, n2):
            # Invalid move — stay put, small penalty
            reward = -0.5
            state = self._get_state()
            if self.step_count >= self.max_steps:
                self.done = True
            return state, reward, self.done, {"invalid": True}

        self.m, self.n = m2, n2

        # Check for factor
        f = check_factor(self.N, self.m, self.n)
        if f is not None:
            self.factor = f
            self.done = True
            reward = 1000.0
            return self._get_state(), reward, True, {"factor": f}

        # Reward shaping: reward improvement in max gcd
        cur_gcd = max_gcd(self.N, self.m, self.n)
        if cur_gcd > self.prev_gcd:
            reward = 1.0
            self.prev_gcd = cur_gcd
        else:
            reward = -0.1  # time penalty

        if self.step_count >= self.max_steps:
            self.done = True

        return self._get_state(), reward, self.done, {}


# ============================================================
# ALGORITHM 1: TABULAR Q-LEARNING
# ============================================================

class TabularQLearner:
    """Q-learning with discretized state space."""

    def __init__(self, n_bins=8, n_features=N_FEATURES, n_actions=N_ACTIONS,
                 lr=0.1, gamma=0.99, epsilon=0.3):
        self.n_bins = n_bins
        self.n_features = n_features
        self.n_actions = n_actions
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        # Use a dict to avoid exponential memory with many bins
        self.q_table = defaultdict(lambda: np.zeros(n_actions))
        self.stats = {"updates": 0}

    def _discretize(self, state):
        """Discretize continuous state to bins. Use only first 13 features to keep table small."""
        key_feats = state[:13]
        bins = np.clip((key_feats * self.n_bins).astype(int), 0, self.n_bins - 1)
        return tuple(bins)

    def select_action(self, state, greedy=False):
        key = self._discretize(state)
        if not greedy and random.random() < self.epsilon:
            return random.randint(0, self.n_actions - 1)
        q_vals = self.q_table[key]
        return int(np.argmax(q_vals))

    def update(self, state, action, reward, next_state, done):
        key = self._discretize(state)
        next_key = self._discretize(next_state)
        q_val = self.q_table[key][action]
        if done:
            target = reward
        else:
            target = reward + self.gamma * np.max(self.q_table[next_key])
        self.q_table[key][action] += self.lr * (target - q_val)
        self.stats["updates"] += 1

    def table_size(self):
        return len(self.q_table)


# ============================================================
# ALGORITHM 2: LINEAR Q-LEARNING
# ============================================================

class LinearQLearner:
    """Q(s,a) = w_a . phi(s) — one weight vector per action."""

    def __init__(self, n_features=N_FEATURES, n_actions=N_ACTIONS,
                 lr=0.001, gamma=0.99, epsilon=0.3):
        self.n_features = n_features
        self.n_actions = n_actions
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        # One weight vector per action + bias
        self.weights = np.zeros((n_actions, n_features + 1))

    def _phi(self, state):
        """Feature vector with bias."""
        return np.append(state, 1.0)

    def q_values(self, state):
        phi = self._phi(state)
        return self.weights @ phi

    def select_action(self, state, greedy=False):
        if not greedy and random.random() < self.epsilon:
            return random.randint(0, self.n_actions - 1)
        return int(np.argmax(self.q_values(state)))

    def update(self, state, action, reward, next_state, done):
        phi = self._phi(state)
        q_val = self.weights[action] @ phi
        if done:
            target = reward
        else:
            target = reward + self.gamma * np.max(self.q_values(next_state))
        td_error = target - q_val
        # Clip gradient to prevent explosion
        grad = td_error * phi
        grad = np.clip(grad, -10.0, 10.0)
        self.weights[action] += self.lr * grad


# ============================================================
# ALGORITHM 3: NEURAL Q-NETWORK (numpy MLP)
# ============================================================

class NumpyMLP:
    """Simple 2-layer MLP: input -> hidden(64) -> ReLU -> output(n_actions)."""

    def __init__(self, n_in, n_hidden, n_out, lr=0.0005):
        self.lr = lr
        # Xavier initialization
        self.W1 = np.random.randn(n_hidden, n_in) * np.sqrt(2.0 / n_in)
        self.b1 = np.zeros(n_hidden)
        self.W2 = np.random.randn(n_out, n_hidden) * np.sqrt(2.0 / n_hidden)
        self.b2 = np.zeros(n_out)

    def forward(self, x):
        """Forward pass, return output and cache for backprop."""
        z1 = self.W1 @ x + self.b1
        a1 = np.maximum(z1, 0)  # ReLU
        z2 = self.W2 @ a1 + self.b2
        cache = (x, z1, a1)
        return z2, cache

    def backward(self, dout, cache):
        """Backward pass from output gradient."""
        x, z1, a1 = cache
        # Output layer
        dW2 = np.outer(dout, a1)
        db2 = dout
        da1 = self.W2.T @ dout
        # ReLU
        dz1 = da1 * (z1 > 0).astype(float)
        dW1 = np.outer(dz1, x)
        db1 = dz1
        # Clip gradients
        for g in [dW1, db1, dW2, db2]:
            np.clip(g, -5.0, 5.0, out=g)
        # SGD update
        self.W1 -= self.lr * dW1
        self.b1 -= self.lr * db1
        self.W2 -= self.lr * dW2
        self.b2 -= self.lr * db2


class NeuralQLearner:
    """DQN with experience replay, numpy only."""

    def __init__(self, n_features=N_FEATURES, n_actions=N_ACTIONS,
                 n_hidden=64, lr=0.0005, gamma=0.99, epsilon=0.3,
                 replay_size=10000, batch_size=32):
        self.n_actions = n_actions
        self.gamma = gamma
        self.epsilon = epsilon
        self.batch_size = batch_size
        self.net = NumpyMLP(n_features, n_hidden, n_actions, lr=lr)
        # Experience replay buffer (circular)
        self.replay = []
        self.replay_size = replay_size
        self.replay_idx = 0

    def select_action(self, state, greedy=False):
        if not greedy and random.random() < self.epsilon:
            return random.randint(0, self.n_actions - 1)
        q_vals, _ = self.net.forward(state)
        return int(np.argmax(q_vals))

    def store(self, state, action, reward, next_state, done):
        exp = (state.copy(), action, reward, next_state.copy(), done)
        if len(self.replay) < self.replay_size:
            self.replay.append(exp)
        else:
            self.replay[self.replay_idx % self.replay_size] = exp
        self.replay_idx += 1

    def train_batch(self):
        if len(self.replay) < self.batch_size:
            return
        batch = random.sample(self.replay, self.batch_size)
        for s, a, r, s2, done in batch:
            q_vals, cache = self.net.forward(s)
            if done:
                target = r
            else:
                q2, _ = self.net.forward(s2)
                target = r + self.gamma * np.max(q2)
            # Gradient only on the chosen action
            dout = np.zeros(self.n_actions)
            td_error = target - q_vals[a]
            dout[a] = -td_error  # MSE gradient = -(target - predicted)
            self.net.backward(dout, cache)


# ============================================================
# ALGORITHM 4: REINFORCE (Policy Gradient)
# ============================================================

class ReinforceAgent:
    """REINFORCE with linear softmax policy: pi(a|s) = softmax(W . phi(s))."""

    def __init__(self, n_features=N_FEATURES, n_actions=N_ACTIONS,
                 lr=0.001, gamma=0.99):
        self.n_features = n_features
        self.n_actions = n_actions
        self.lr = lr
        self.gamma = gamma
        self.weights = np.zeros((n_actions, n_features + 1))
        self.trajectory = []  # (state, action, reward)

    def _phi(self, state):
        return np.append(state, 1.0)

    def _softmax(self, logits):
        logits = logits - np.max(logits)  # stability
        e = np.exp(logits)
        return e / (e.sum() + 1e-12)

    def select_action(self, state, greedy=False):
        phi = self._phi(state)
        logits = self.weights @ phi
        probs = self._softmax(logits)
        if greedy:
            return int(np.argmax(probs))
        return int(np.random.choice(self.n_actions, p=probs))

    def store_step(self, state, action, reward):
        self.trajectory.append((state, action, reward))

    def update(self):
        """Update weights using trajectory returns."""
        if not self.trajectory:
            return
        T = len(self.trajectory)
        # Compute discounted returns
        returns = np.zeros(T)
        G = 0.0
        for t in range(T - 1, -1, -1):
            G = self.trajectory[t][2] + self.gamma * G
            returns[t] = G
        # Normalize returns
        if T > 1:
            std = returns.std()
            if std > 1e-8:
                returns = (returns - returns.mean()) / std

        # Policy gradient update
        for t in range(T):
            state, action, _ = self.trajectory[t]
            phi = self._phi(state)
            logits = self.weights @ phi
            probs = self._softmax(logits)
            # d log pi(a|s) / d W_a = phi * (1 - pi(a)) for chosen action
            # d log pi(a|s) / d W_j = -phi * pi(j)      for other actions
            grad = np.outer(-probs, phi)  # all actions
            grad[action] += phi  # correction for chosen action
            # Clip gradient
            np.clip(grad, -5.0, 5.0, out=grad)
            self.weights += self.lr * returns[t] * grad

        self.trajectory = []


# ============================================================
# TRAINING LOOP
# ============================================================

def train_agent(agent_type="neural", train_bits=16, n_episodes=2000,
                max_steps=3000, n_epochs=1, verbose=True):
    """
    Train an RL agent on semiprimes of `train_bits` size.
    Returns the trained agent and training stats.
    """
    if agent_type == "tabular":
        agent = TabularQLearner(n_bins=8, lr=0.1, gamma=0.95, epsilon=0.4)
    elif agent_type == "linear":
        agent = LinearQLearner(lr=0.0005, gamma=0.95, epsilon=0.3)
    elif agent_type == "neural":
        agent = NeuralQLearner(n_hidden=64, lr=0.0003, gamma=0.95,
                               epsilon=0.4, replay_size=20000, batch_size=32)
    elif agent_type == "reinforce":
        agent = ReinforceAgent(lr=0.0003, gamma=0.95)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")

    history = []  # (epoch, episode, solved, steps)

    for epoch in range(n_epochs):
        # Decay epsilon over epochs
        if hasattr(agent, "epsilon"):
            agent.epsilon = max(0.05, 0.4 - 0.35 * epoch / max(n_epochs - 1, 1))

        solved = 0
        total_steps = 0

        for ep in range(n_episodes):
            _, _, N = gen_semi(train_bits)
            env = PythTreeEnv(N, max_steps=max_steps)
            state = env.reset()
            ep_reward = 0.0
            ep_steps = 0

            while not env.done:
                action = agent.select_action(state)
                next_state, reward, done, info = env.step(action)

                if agent_type == "reinforce":
                    agent.store_step(state, action, reward)
                elif agent_type == "neural":
                    agent.store(state, action, reward, next_state, done)
                    if ep_steps % 4 == 0:
                        agent.train_batch()
                else:
                    agent.update(state, action, reward, next_state, done)

                state = next_state
                ep_reward += reward
                ep_steps += 1

            if agent_type == "reinforce":
                agent.update()

            if env.factor is not None:
                solved += 1
            total_steps += ep_steps
            history.append((epoch, ep, env.factor is not None, ep_steps))

            # Progress
            if verbose and (ep + 1) % max(1, n_episodes // 10) == 0:
                rate = solved / (ep + 1)
                avg_s = total_steps / (ep + 1)
                extra = ""
                if agent_type == "tabular":
                    extra = f" table={agent.table_size()}"
                print(f"  Epoch {epoch} Ep {ep+1}/{n_episodes}: "
                      f"solve_rate={rate:.3f} avg_steps={avg_s:.0f}"
                      f" eps={getattr(agent, 'epsilon', 'N/A')}{extra}")

    return agent, history


# ============================================================
# EVALUATION
# ============================================================

def evaluate(agent, test_bits, n_tests=200, max_steps=5000, label="Agent"):
    """Evaluate agent and random baseline on semiprimes of given bit size."""
    agent_solved = 0
    agent_steps_list = []
    rand_solved = 0
    rand_steps_list = []

    for i in range(n_tests):
        _, _, N = gen_semi(test_bits)

        # Agent
        env = PythTreeEnv(N, max_steps=max_steps)
        state = env.reset()
        while not env.done:
            action = agent.select_action(state, greedy=True)
            state, _, done, _ = env.step(action)
        if env.factor is not None:
            agent_solved += 1
            agent_steps_list.append(env.step_count)
        else:
            agent_steps_list.append(max_steps)

        # Random baseline
        f, steps = random_walk_factor(N, max_steps=max_steps)
        if f is not None:
            rand_solved += 1
            rand_steps_list.append(steps)
        else:
            rand_steps_list.append(max_steps)

    agent_rate = agent_solved / n_tests
    rand_rate = rand_solved / n_tests
    agent_avg = np.mean(agent_steps_list)
    rand_avg = np.mean(rand_steps_list)

    speedup = rand_avg / max(agent_avg, 1)

    print(f"\n{'='*60}")
    print(f" {label} | {test_bits}-bit semiprimes | {n_tests} tests")
    print(f"{'='*60}")
    print(f"  Agent:  solve_rate={agent_rate:.3f}  avg_steps={agent_avg:.0f}")
    print(f"  Random: solve_rate={rand_rate:.3f}  avg_steps={rand_avg:.0f}")
    print(f"  Speedup: {speedup:.2f}x")
    if agent_rate > rand_rate + 0.05:
        print(f"  >>> AGENT BEATS RANDOM by {agent_rate - rand_rate:.3f} <<<")
    elif rand_rate > agent_rate + 0.05:
        print(f"  Random wins by {rand_rate - agent_rate:.3f}")
    else:
        print(f"  Roughly tied.")
    print()

    return {
        "bits": test_bits,
        "agent_rate": agent_rate,
        "rand_rate": rand_rate,
        "agent_avg_steps": agent_avg,
        "rand_avg_steps": rand_avg,
        "speedup": speedup,
    }


# ============================================================
# LEARNING CURVE PLOT (ASCII)
# ============================================================

def ascii_plot(history, window=100, title="Learning Curve"):
    """Print an ASCII learning curve (solve rate vs episode)."""
    # Compute rolling solve rate
    solved_flags = [1 if h[2] else 0 for h in history]
    n = len(solved_flags)
    if n < window:
        window = max(1, n)

    rates = []
    for i in range(0, n, window):
        chunk = solved_flags[i:i + window]
        rates.append(sum(chunk) / len(chunk))

    if not rates:
        return

    print(f"\n{title}")
    print(f"{'Episode':>10} | Solve Rate")
    print("-" * 45)
    max_bar = 40
    for i, r in enumerate(rates):
        ep = (i + 1) * window
        bar_len = int(r * max_bar)
        bar = "#" * bar_len + "." * (max_bar - bar_len)
        print(f"{ep:>10} | {bar} {r:.3f}")
    print()


def action_distribution(agent, test_bits=16, n_tests=50, max_steps=1000):
    """Show which actions the agent prefers."""
    counts = np.zeros(N_ACTIONS)
    for _ in range(n_tests):
        _, _, N = gen_semi(test_bits)
        env = PythTreeEnv(N, max_steps=max_steps)
        state = env.reset()
        while not env.done:
            action = agent.select_action(state, greedy=True)
            counts[action] += 1
            state, _, _, _ = env.step(action)

    total = counts.sum()
    if total == 0:
        return
    print("\nAction Distribution (greedy policy):")
    print("-" * 45)
    for i, name in enumerate(ACTION_NAMES):
        pct = counts[i] / total * 100
        bar = "#" * int(pct / 2)
        print(f"  {name:>4}: {pct:5.1f}% {bar}")
    print()


# ============================================================
# MAIN: FULL EXPERIMENT
# ============================================================

if __name__ == "__main__":
    random.seed(42)
    np.random.seed(42)

    TRAIN_BITS = 16
    TEST_BITS_LIST = [16, 24, 32, 40]
    N_TRAIN_EPISODES = 3000
    MAX_STEPS_TRAIN = 2000
    MAX_STEPS_TEST = 5000
    N_TEST = 100

    # Choose agent type: "tabular", "linear", "neural", "reinforce"
    # Run all four and compare
    agent_types = ["tabular", "linear", "neural", "reinforce"]

    results_all = {}

    for atype in agent_types:
        print(f"\n{'#'*70}")
        print(f"# TRAINING: {atype.upper()} agent on {TRAIN_BITS}-bit semiprimes")
        print(f"{'#'*70}")

        t0 = time.time()
        agent, history = train_agent(
            agent_type=atype,
            train_bits=TRAIN_BITS,
            n_episodes=N_TRAIN_EPISODES,
            max_steps=MAX_STEPS_TRAIN,
            n_epochs=1,
            verbose=True,
        )
        train_time = time.time() - t0
        print(f"\nTraining time: {train_time:.1f}s")

        # Learning curve
        ascii_plot(history, window=N_TRAIN_EPISODES // 20,
                   title=f"{atype.upper()} Learning Curve")

        # Action distribution
        action_distribution(agent, test_bits=TRAIN_BITS)

        # Evaluate on multiple bit sizes
        results_all[atype] = {}
        for tb in TEST_BITS_LIST:
            print(f"\nEvaluating {atype} on {tb}-bit...")
            res = evaluate(
                agent, test_bits=tb,
                n_tests=N_TEST,
                max_steps=MAX_STEPS_TEST,
                label=f"{atype.upper()}"
            )
            results_all[atype][tb] = res

    # ============================================================
    # SUMMARY TABLE
    # ============================================================
    print(f"\n{'='*80}")
    print(f" FINAL SUMMARY: Trained on {TRAIN_BITS}-bit, tested on various sizes")
    print(f"{'='*80}")
    print(f"{'Agent':<12} {'Bits':>4} {'Agent%':>7} {'Random%':>8} "
          f"{'AgentSteps':>11} {'RandSteps':>10} {'Speedup':>8}")
    print("-" * 80)

    for atype in agent_types:
        for tb in TEST_BITS_LIST:
            r = results_all[atype][tb]
            print(f"{atype:<12} {tb:>4} {r['agent_rate']:>7.1%} "
                  f"{r['rand_rate']:>8.1%} {r['agent_avg_steps']:>11.0f} "
                  f"{r['rand_avg_steps']:>10.0f} {r['speedup']:>7.2f}x")
        print()

    # THE CRITICAL QUESTION
    print("=" * 80)
    print("CRITICAL QUESTION: Does any agent beat random at LARGER sizes?")
    print("=" * 80)
    for atype in agent_types:
        for tb in [32, 40]:
            if tb in results_all[atype]:
                r = results_all[atype][tb]
                delta = r["agent_rate"] - r["rand_rate"]
                if delta > 0.05:
                    print(f"  YES: {atype} beats random at {tb}b by "
                          f"{delta:.1%} (agent {r['agent_rate']:.1%} vs "
                          f"random {r['rand_rate']:.1%})")
                elif delta < -0.05:
                    print(f"  NO:  {atype} LOSES to random at {tb}b by "
                          f"{-delta:.1%}")
                else:
                    print(f"  TIE: {atype} ~= random at {tb}b "
                          f"(delta={delta:+.1%})")
    print()
    print("If YES at 32b+: There IS a learnable gradient. Worth pursuing.")
    print("If NO at all:   No computable gradient exists. Confirmed dead end.")
