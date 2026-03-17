#!/usr/bin/env python3
"""
Pythagorean Tree Factoring — AI/ML Experiment Suite

Experiments using ideas from:
1. Genetic Programming (GP) — evolve heuristic functions
2. Q-Learning — learn state→action value table
3. Feature extraction — rich feature vectors for each (m,n) node
4. UCB1 / Monte Carlo Tree Search — balance exploration/exploitation
5. Simulated Annealing — escape local optima
6. Bayesian Optimization — learn which tree regions are promising

Each experiment is self-contained with its own benchmark.
"""

import math
import random
import time
import operator
from math import gcd, log, isqrt
from collections import defaultdict
import heapq

# ============================================================
# TREE INFRASTRUCTURE
# ============================================================

B1 = ((2, -1), (1, 0))
B2 = ((2, 1), (1, 0))
B3 = ((1, 2), (0, 1))
P1 = ((1, 1), (0, 2))
P2 = ((2, 0), (1, -1))
P3 = ((2, 0), (1, 1))
F1 = ((3, -2), (1, -1))
F2 = ((3, 2), (1, 1))
F3 = ((1, 4), (0, 1))
FORWARD = [B1, B2, B3, P1, P2, P3, F1, F2, F3]
B1i = ((0, 1), (-1, 2))
B2i = ((0, 1), (1, -2))
B3i = ((1, -2), (0, 1))
INVERSE = [B1i, B2i, B3i]
ALL_MATS = FORWARD + INVERSE
N_FWD = len(FORWARD)
N_ALL = len(ALL_MATS)

def apply_mat(M, m, n):
    return M[0][0]*m + M[0][1]*n, M[1][0]*m + M[1][1]*n

def valid(m, n):
    return m > 0 and n >= 0 and m > n

def derived_values(m, n):
    if not valid(m, n): return []
    a = m*m - n*n; b = 2*m*n; c = m*m + n*n
    d = m-n; s = m+n
    return [v for v in [a, b, c, m, n, d, s, d*d, s*s] if v > 0]

def check_factor(N, m, n):
    for v in derived_values(m, n):
        g = gcd(v, N)
        if 1 < g < N: return g
    return None

def miller_rabin(n, witnesses=(2,3,5,7,11,13,17,19,23,29,31,37)):
    if n < 2: return False
    if n in (2, 3): return True
    if n % 2 == 0: return False
    r, d = 0, n - 1
    while d % 2 == 0: r += 1; d //= 2
    for a in witnesses:
        if a >= n: continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True

def gen_semi(bits, seed=None):
    if seed is not None: random.seed(seed)
    while True:
        p = random.getrandbits(bits) | (1 << (bits-1)) | 1
        if miller_rabin(p): break
    while True:
        q = random.getrandbits(bits) | (1 << (bits-1)) | 1
        if q != p and miller_rabin(q): break
    return min(p,q), max(p,q), p*q


# ============================================================
# FEATURE EXTRACTION (shared across experiments)
# ============================================================

def extract_features(N, m, n):
    """Extract a rich feature vector from node (m,n) relative to N.
    Returns dict of named features."""
    vals = derived_values(m, n)
    if not vals:
        return None

    log_N = log(N)
    log_sqrtN = log_N / 2
    f = {}

    # Basic scent features
    scents = []
    log_scents = []
    size_proxs = []
    for v in vals:
        if v <= 1: continue
        r = N % v
        near = min(r, v - r)
        scent = near / v
        scents.append(scent)

        if near > 0:
            log_scents.append(log(near + 1) / log(v + 1))
        else:
            log_scents.append(0.0)

        lv = log(v)
        size_proxs.append(abs(lv - log_sqrtN) / max(log_sqrtN, 1))

    if not scents:
        return None

    f['min_scent'] = min(scents)
    f['mean_scent'] = sum(scents) / len(scents)
    f['max_scent'] = max(scents)
    f['min_log_scent'] = min(log_scents) if log_scents else 1.0
    f['mean_log_scent'] = sum(log_scents) / len(log_scents) if log_scents else 1.0

    # Harmonic mean of scent
    inv_sum = sum(1/s for s in scents if s > 0)
    f['harmonic_scent'] = len(scents) / inv_sum if inv_sum > 0 else 1.0

    # Size proximity
    f['min_size_prox'] = min(size_proxs) if size_proxs else 2.0
    f['mean_size_prox'] = sum(size_proxs) / len(size_proxs) if size_proxs else 2.0

    # Quadratic residue features
    best_quad = 1.0
    for v in vals:
        if v <= 1: continue
        v2 = v * v
        if 1 < v2 < N:
            r2 = N % v2
            s2 = min(r2, v2 - r2) / v2
            if s2 < best_quad: best_quad = s2
    f['min_quad_scent'] = best_quad

    # Tree structure features
    f['log_m'] = log(m) if m > 0 else 0
    f['log_n'] = log(n) if n > 0 else 0
    f['depth_est'] = log(m + n + 1)  # proxy for tree depth
    f['m_over_n'] = m / max(n, 1)

    # Smoothness of m, n
    def smoothness(x):
        if x <= 1: return 0
        score = 0
        for p in [2, 3, 5, 7, 11, 13]:
            while x % p == 0: score += 1; x //= p
        return score + (5 if x == 1 else 0)
    f['smooth_m'] = smoothness(m)
    f['smooth_n'] = smoothness(n)

    # Number of valid children
    n_valid = sum(1 for M in ALL_MATS
                  for (m2, n2) in [apply_mat(M, m, n)]
                  if valid(m2, n2))
    f['n_valid_children'] = n_valid

    return f


# ============================================================
# EXPERIMENT 1: GENETIC PROGRAMMING
# Evolve arithmetic expression trees as heuristic functions
# ============================================================

# GP primitives
def safe_div(a, b):
    return a / b if abs(b) > 1e-10 else a

def safe_log(a):
    return log(abs(a) + 1e-10)

GP_FUNCS = {
    'add': (operator.add, 2),
    'sub': (operator.sub, 2),
    'mul': (operator.mul, 2),
    'div': (safe_div, 2),
    'min': (min, 2),
    'max': (max, 2),
    'neg': (operator.neg, 1),
    'abs': (abs, 1),
    'log': (safe_log, 1),
    'sq': (lambda x: x*x, 1),
}

# Feature names used as terminals
FEATURE_NAMES = ['min_scent', 'mean_scent', 'min_log_scent', 'harmonic_scent',
                 'min_quad_scent', 'min_size_prox', 'depth_est', 'smooth_m',
                 'n_valid_children']

class GPTree:
    """Expression tree for genetic programming."""
    def __init__(self, op=None, children=None, terminal=None, const=None):
        self.op = op           # function name from GP_FUNCS
        self.children = children or []
        self.terminal = terminal  # feature name
        self.const = const     # constant value

    def evaluate(self, features):
        if self.terminal is not None:
            return features.get(self.terminal, 0.0)
        if self.const is not None:
            return self.const
        func, arity = GP_FUNCS[self.op]
        try:
            args = [c.evaluate(features) for c in self.children[:arity]]
            result = func(*args)
            if not math.isfinite(result):
                return 1.0
            return max(-1e6, min(1e6, result))
        except:
            return 1.0

    def depth(self):
        if self.terminal is not None or self.const is not None:
            return 0
        return 1 + max((c.depth() for c in self.children), default=0)

    def __repr__(self):
        if self.terminal: return self.terminal
        if self.const is not None: return f"{self.const:.3f}"
        args = ", ".join(str(c) for c in self.children)
        return f"{self.op}({args})"

    def copy(self):
        if self.terminal: return GPTree(terminal=self.terminal)
        if self.const is not None: return GPTree(const=self.const)
        return GPTree(op=self.op, children=[c.copy() for c in self.children])


def random_gp_tree(max_depth=4):
    """Generate random GP expression tree."""
    if max_depth <= 0 or random.random() < 0.3:
        if random.random() < 0.7:
            return GPTree(terminal=random.choice(FEATURE_NAMES))
        else:
            return GPTree(const=random.uniform(-2, 2))

    op = random.choice(list(GP_FUNCS.keys()))
    _, arity = GP_FUNCS[op]
    children = [random_gp_tree(max_depth - 1) for _ in range(arity)]
    return GPTree(op=op, children=children)


def mutate_gp(tree, rate=0.2):
    """Mutate a GP tree."""
    t = tree.copy()
    if random.random() < rate:
        return random_gp_tree(3)
    if t.children:
        idx = random.randrange(len(t.children))
        t.children[idx] = mutate_gp(t.children[idx], rate)
    return t


def crossover_gp(t1, t2):
    """Subtree crossover."""
    c = t1.copy()
    donor = t2.copy()
    # Find random subtree in c and replace with random subtree from donor
    if c.children and donor.children:
        idx = random.randrange(len(c.children))
        if donor.children:
            didx = random.randrange(len(donor.children))
            c.children[idx] = donor.children[didx].copy()
    elif not c.children:
        return donor.copy()
    return c


def gp_to_heuristic(tree):
    """Convert GP tree to heuristic function."""
    def heuristic(N, m, n):
        feats = extract_features(N, m, n)
        if feats is None: return 1.0
        return tree.evaluate(feats)
    return heuristic


def evaluate_gp_fitness(tree, test_cases, time_per_case=2.0):
    """Evaluate a GP tree on test cases. Fitness = number solved + speed bonus."""
    hfn = gp_to_heuristic(tree)
    solved = 0
    total_nodes = 0
    for N, p, q in test_cases:
        f, nodes = gp_greedy_search(N, hfn, max_steps=50000, time_limit=time_per_case)
        total_nodes += nodes
        if f and 1 < f < N:
            solved += 1
    # Fitness: solved count + speed bonus (fewer nodes = better)
    return solved + 0.001 / (total_nodes + 1)


def gp_greedy_search(N, hfn, max_steps=50000, time_limit=2.0):
    """Quick greedy search for GP evaluation."""
    t0 = time.time()
    m, n = 2, 1
    f = check_factor(N, m, n)
    if f: return f, 1
    visited = {(m, n)}
    stale = 0
    for step in range(max_steps):
        if time.time() - t0 > time_limit: break
        best_score = float('inf')
        best_mn = None
        for M in ALL_MATS:
            m2, n2 = apply_mat(M, m, n)
            if not valid(m2, n2): continue
            if (m2, n2) in visited: continue
            f = check_factor(N, m2, n2)
            if f: return f, step
            score = hfn(N, m2, n2)
            if score < best_score:
                best_score = score
                best_mn = (m2, n2)
        if best_mn is None or stale > 100:
            m, n = 2, 1
            for _ in range(random.randint(5, 20)):
                idx = random.randrange(N_FWD)
                m2, n2 = apply_mat(FORWARD[idx], m, n)
                if valid(m2, n2): m, n = m2, n2
            visited.add((m, n))
            stale = 0
            continue
        m, n = best_mn
        visited.add((m, n))
        stale += 1
    return None, step if 'step' in dir() else 0


def run_gp_experiment(bits=20, pop_size=30, generations=20, n_test=5):
    """Run GP evolution to discover heuristic functions."""
    print(f"\n{'='*60}")
    print(f"  EXPERIMENT 1: Genetic Programming ({bits}b)")
    print(f"  Pop={pop_size}, Gen={generations}, Tests={n_test}")
    print(f"{'='*60}")

    # Generate test cases
    test_cases = []
    for i in range(n_test):
        p, q, N = gen_semi(bits, seed=100 + i)
        test_cases.append((N, p, q))

    # Initialize population
    population = [random_gp_tree(4) for _ in range(pop_size)]

    best_fitness = -1
    best_tree = None

    for gen in range(generations):
        t0 = time.time()
        # Evaluate fitness
        fitness = []
        for tree in population:
            fit = evaluate_gp_fitness(tree, test_cases, time_per_case=1.0)
            fitness.append(fit)

        # Best
        idx_best = max(range(len(fitness)), key=lambda i: fitness[i])
        if fitness[idx_best] > best_fitness:
            best_fitness = fitness[idx_best]
            best_tree = population[idx_best].copy()

        elapsed = time.time() - t0
        solved_count = int(best_fitness)
        print(f"  Gen {gen:>3}: best={best_fitness:.4f} ({solved_count}/{n_test} solved) "
              f" [{elapsed:.1f}s]  tree_depth={best_tree.depth()}", flush=True)

        if solved_count >= n_test:
            print(f"  *** Perfect score! ***")
            break

        # Selection + reproduction
        # Tournament selection
        new_pop = [best_tree.copy()]  # elitism
        while len(new_pop) < pop_size:
            # Tournament of 3
            candidates = random.sample(range(len(population)), min(3, len(population)))
            winner = max(candidates, key=lambda i: fitness[i])

            if random.random() < 0.3 and len(new_pop) > 1:
                # Crossover
                other = random.randrange(len(new_pop))
                child = crossover_gp(population[winner], new_pop[other])
            else:
                child = mutate_gp(population[winner], rate=0.3)

            # Bloat control
            if child.depth() > 8:
                child = random_gp_tree(4)

            new_pop.append(child)

        population = new_pop

    # Final evaluation on NEW test cases
    print(f"\n  Best evolved heuristic: {best_tree}")
    final_test = [(gen_semi(bits, seed=200 + i)) for i in range(10)]
    final_cases = [(N, p, q) for p, q, N in final_test]
    final_fit = evaluate_gp_fitness(best_tree, final_cases, time_per_case=3.0)
    print(f"  Validation: {int(final_fit)}/10 solved")

    return best_tree


# ============================================================
# EXPERIMENT 2: Q-LEARNING
# Learn Q(state, action) table for tree navigation
# ============================================================

def state_key(N, m, n):
    """Discretize state for Q-table.
    Use scent bucket + depth bucket + direction."""
    vals = derived_values(m, n)
    if not vals: return (0, 0, 0)

    # Scent bucket (0-9)
    best_scent = 1.0
    for v in vals:
        r = N % v
        s = min(r, v - r) / v
        if s < best_scent: best_scent = s
    scent_bucket = min(9, int(-math.log10(best_scent + 1e-10)))

    # Depth bucket (0-5)
    depth = min(5, int(math.log2(m + n + 1)))

    # m/n ratio bucket (0-4)
    ratio = min(4, int(m / max(n, 1)))

    return (scent_bucket, depth, ratio)


def run_q_learning(bits=20, n_episodes=200, n_test=10):
    """Q-learning to learn tree navigation policy."""
    print(f"\n{'='*60}")
    print(f"  EXPERIMENT 2: Q-Learning ({bits}b)")
    print(f"  Episodes={n_episodes}")
    print(f"{'='*60}")

    Q = defaultdict(lambda: [0.0] * N_ALL)  # Q[state][action]
    alpha = 0.1   # learning rate
    gamma = 0.95  # discount
    epsilon = 0.5 # exploration rate

    # Training episodes
    solved_window = []
    for episode in range(n_episodes):
        p, q, N = gen_semi(bits, seed=300 + episode)
        m, n = 2, 1
        visited = {(m, n)}

        total_reward = 0
        found = False

        for step in range(5000):
            state = state_key(N, m, n)

            # Epsilon-greedy action selection
            if random.random() < epsilon:
                action = random.randrange(N_ALL)
            else:
                action = max(range(N_ALL), key=lambda a: Q[state][a])

            # Take action
            M = ALL_MATS[action]
            m2, n2 = apply_mat(M, m, n)

            if not valid(m2, n2) or (m2, n2) in visited:
                # Invalid move — penalty
                reward = -0.1
                # Stay in place, pick random valid child
                valid_moves = []
                for ai, Mi in enumerate(ALL_MATS):
                    mi, ni = apply_mat(Mi, m, n)
                    if valid(mi, ni) and (mi, ni) not in visited:
                        valid_moves.append((ai, mi, ni))
                if valid_moves:
                    action, m2, n2 = random.choice(valid_moves)
                else:
                    break  # stuck
            else:
                reward = 0.0

            # Check for factor
            f = check_factor(N, m2, n2)
            if f and 1 < f < N:
                reward = 10.0
                found = True

            # Compute scent improvement as reward signal
            old_vals = derived_values(m, n)
            new_vals = derived_values(m2, n2)
            old_filtered = [v for v in old_vals if v > 1]
            new_filtered = [v for v in new_vals if v > 1]
            if old_filtered and new_filtered:
                old_scent = min(min(N % v, v - N % v) / v for v in old_filtered)
                new_scent = min(min(N % v, v - N % v) / v for v in new_filtered)
                if new_scent < old_scent:
                    reward += 0.5  # scent improved
                else:
                    reward -= 0.1  # scent worsened

            total_reward += reward

            # Q-update
            next_state = state_key(N, m2, n2)
            best_next = max(Q[next_state])
            Q[state][action] += alpha * (reward + gamma * best_next - Q[state][action])

            m, n = m2, n2
            visited.add((m, n))

            if found: break

        solved_window.append(1 if found else 0)
        if len(solved_window) > 20: solved_window.pop(0)

        # Decay epsilon
        epsilon = max(0.05, epsilon * 0.995)

        if (episode + 1) % 20 == 0:
            rate = sum(solved_window) / len(solved_window)
            print(f"  Episode {episode+1:>4}: solve_rate={rate:.0%}  "
                  f"Q_states={len(Q)}  eps={epsilon:.3f}", flush=True)

    # Test phase
    print(f"\n  Testing learned policy...")
    solved = 0
    for trial in range(n_test):
        p, q, N = gen_semi(bits, seed=400 + trial)
        m, n = 2, 1
        visited = {(m, n)}
        for step in range(20000):
            state = state_key(N, m, n)
            # Greedy action
            action = max(range(N_ALL), key=lambda a: Q[state][a])
            M = ALL_MATS[action]
            m2, n2 = apply_mat(M, m, n)
            if not valid(m2, n2) or (m2, n2) in visited:
                # Pick best valid
                best_a, best_mn = None, None
                best_q = -float('inf')
                for ai, Mi in enumerate(ALL_MATS):
                    mi, ni = apply_mat(Mi, m, n)
                    if valid(mi, ni) and (mi, ni) not in visited:
                        if Q[state][ai] > best_q:
                            best_q = Q[state][ai]
                            best_a = ai
                            best_mn = (mi, ni)
                if best_mn is None: break
                m2, n2 = best_mn
            f = check_factor(N, m2, n2)
            if f and 1 < f < N:
                solved += 1
                break
            m, n = m2, n2
            visited.add((m, n))

    print(f"  Q-Learning: {solved}/{n_test} solved at {bits}b")
    return Q


# ============================================================
# EXPERIMENT 3: UCB1 TREE SEARCH (MCTS-lite)
# Balance exploration and exploitation
# ============================================================

def run_ucb1_search(bits=20, n_trials=10, time_limit=10.0):
    """UCB1-guided search: each move (matrix) has visit count + reward.
    Balances exploring underused moves vs exploiting high-scent moves."""
    print(f"\n{'='*60}")
    print(f"  EXPERIMENT 3: UCB1 Tree Search ({bits}b)")
    print(f"{'='*60}")

    solved = 0
    total_nodes = 0

    for trial in range(n_trials):
        p, q, N = gen_semi(bits, seed=42 + trial)
        t0 = time.time()

        # Per-depth-per-action stats
        # Key: (depth_bucket, action) → (visits, total_reward)
        stats = defaultdict(lambda: [0, 0.0])
        C = 1.4  # exploration constant

        m, n = 2, 1
        visited = {(m, n)}
        nodes = 1
        found = False
        stale = 0

        for step in range(200000):
            if time.time() - t0 > time_limit: break

            depth = min(10, int(math.log2(m + n + 1)))

            # UCB1 action selection
            total_visits = sum(stats[(depth, a)][0] for a in range(N_ALL))
            log_total = math.log(total_visits + 1)

            best_ucb = -float('inf')
            best_action = None
            best_mn = None

            for ai, M in enumerate(ALL_MATS):
                m2, n2 = apply_mat(M, m, n)
                if not valid(m2, n2): continue
                if (m2, n2) in visited: continue

                vis, rew = stats[(depth, ai)]
                if vis == 0:
                    ucb = float('inf')  # unexplored → always try
                else:
                    ucb = rew / vis + C * math.sqrt(log_total / vis)

                if ucb > best_ucb:
                    best_ucb = ucb
                    best_action = ai
                    best_mn = (m2, n2)

            if best_mn is None:
                # Restart
                m, n = 2, 1
                for _ in range(random.randint(5, 25)):
                    idx = random.randrange(N_FWD)
                    m2, n2 = apply_mat(FORWARD[idx], m, n)
                    if valid(m2, n2): m, n = m2, n2
                visited.add((m, n))
                stale = 0
                continue

            m2, n2 = best_mn
            nodes += 1

            # Check factor
            f = check_factor(N, m2, n2)
            if f and 1 < f < N:
                found = True
                break

            # Compute reward = scent improvement
            old_best = 1.0
            for v in derived_values(m, n):
                if v > 1:
                    r = N % v
                    s = min(r, v - r) / v
                    if s < old_best: old_best = s

            new_best = 1.0
            for v in derived_values(m2, n2):
                if v > 1:
                    r = N % v
                    s = min(r, v - r) / v
                    if s < new_best: new_best = s

            # Reward: scent improvement (positive if better)
            reward = 1.0 if new_best < old_best else 0.0

            stats[(depth, best_action)][0] += 1
            stats[(depth, best_action)][1] += reward

            m, n = m2, n2
            visited.add((m, n))

        if found: solved += 1
        total_nodes += nodes
        elapsed = time.time() - t0
        print(f"  t{trial:>2}: {'Y' if found else 'n'}  {nodes:>10,}n  {elapsed:.1f}s", flush=True)

    print(f"  UCB1: {solved}/{n_trials} at {bits}b  ({total_nodes/n_trials:.0f} avg nodes)")
    return solved


# ============================================================
# EXPERIMENT 4: SIMULATED ANNEALING
# Accept worse moves with decreasing probability
# ============================================================

def run_simulated_annealing(bits=20, n_trials=10, time_limit=10.0):
    """SA: start hot (accept bad moves), cool down (greedy).
    Temperature schedule controls exploration/exploitation tradeoff."""
    print(f"\n{'='*60}")
    print(f"  EXPERIMENT 4: Simulated Annealing ({bits}b)")
    print(f"{'='*60}")

    solved = 0
    total_nodes = 0

    for trial in range(n_trials):
        p, q, N = gen_semi(bits, seed=42 + trial)
        t0 = time.time()

        m, n = 2, 1
        visited = {(m, n)}
        nodes = 1
        found = False

        # Current scent (energy)
        best_scent = 1.0
        for v in derived_values(m, n):
            if v > 1:
                r = N % v
                s = min(r, v - r) / v
                if s < best_scent: best_scent = s
        current_energy = best_scent

        T0 = 0.5   # initial temperature
        T_min = 0.001
        cooling = 0.9999

        T = T0

        for step in range(500000):
            if time.time() - t0 > time_limit: break

            # Pick random move
            action = random.randrange(N_ALL)
            M = ALL_MATS[action]
            m2, n2 = apply_mat(M, m, n)

            if not valid(m2, n2) or (m2, n2) in visited:
                T *= cooling
                continue

            nodes += 1
            f = check_factor(N, m2, n2)
            if f and 1 < f < N:
                found = True
                break

            # Compute energy of new state
            new_energy = 1.0
            for v in derived_values(m2, n2):
                if v > 1:
                    r = N % v
                    s = min(r, v - r) / v
                    if s < new_energy: new_energy = s

            # Accept or reject
            delta = new_energy - current_energy
            if delta < 0:
                # Better — always accept
                accept = True
            elif T > T_min:
                # Worse — accept with probability exp(-delta/T)
                accept = random.random() < math.exp(-delta / T)
            else:
                accept = False

            if accept:
                m, n = m2, n2
                visited.add((m, n))
                current_energy = new_energy
            T *= cooling

        if found: solved += 1
        total_nodes += nodes
        elapsed = time.time() - t0
        print(f"  t{trial:>2}: {'Y' if found else 'n'}  {nodes:>10,}n  {elapsed:.1f}s  "
              f"T_final={T:.6f}", flush=True)

    print(f"  SA: {solved}/{n_trials} at {bits}b  ({total_nodes/n_trials:.0f} avg nodes)")
    return solved


# ============================================================
# EXPERIMENT 5: WEIGHTED RANDOM WALK
# Simple but effective: probability of choosing move ∝ exp(-scent/τ)
# ============================================================

def run_weighted_random(bits=20, n_trials=10, time_limit=10.0):
    """Weighted random walk: P(move) ∝ exp(-score(child) / temperature).
    Not greedy, not random — in between. Good diversity + guidance."""
    print(f"\n{'='*60}")
    print(f"  EXPERIMENT 5: Weighted Random Walk ({bits}b)")
    print(f"{'='*60}")

    solved = 0
    total_nodes = 0

    for trial in range(n_trials):
        p, q, N = gen_semi(bits, seed=42 + trial)
        t0 = time.time()
        m, n = 2, 1
        nodes = 1
        found = False

        tau = 0.1  # temperature for softmax

        for step in range(500000):
            if time.time() - t0 > time_limit: break

            # Evaluate all children
            children = []
            for M in ALL_MATS:
                m2, n2 = apply_mat(M, m, n)
                if not valid(m2, n2): continue
                nodes += 1
                f = check_factor(N, m2, n2)
                if f and 1 < f < N:
                    found = True
                    break
                # Score
                best_s = 1.0
                for v in derived_values(m2, n2):
                    if v > 1:
                        r = N % v
                        s = min(r, v - r) / v
                        if s < best_s: best_s = s
                # Also quad check
                for v in derived_values(m2, n2):
                    if v <= 1: continue
                    v2 = v * v
                    if 1 < v2 < N:
                        r2 = N % v2
                        s2 = min(r2, v2 - r2) / v2
                        if s2 * 0.8 < best_s: best_s = s2 * 0.8
                children.append((best_s, m2, n2))

            if found: break
            if not children:
                # Restart
                m, n = 2, 1
                for _ in range(random.randint(5, 25)):
                    idx = random.randrange(N_FWD)
                    m2, n2 = apply_mat(FORWARD[idx], m, n)
                    if valid(m2, n2): m, n = m2, n2
                continue

            # Softmax selection
            scores = [c[0] for c in children]
            min_s = min(scores)
            max_s = max(scores)
            # Normalize to [0, 1] then softmax
            if max_s > min_s:
                norm = [(s - min_s) / (max_s - min_s) for s in scores]
            else:
                norm = [0.0] * len(scores)

            weights = [math.exp(-s / tau) for s in norm]
            total_w = sum(weights)
            if total_w == 0:
                idx = random.randrange(len(children))
            else:
                r = random.random() * total_w
                cumulative = 0
                idx = 0
                for i, w in enumerate(weights):
                    cumulative += w
                    if cumulative >= r:
                        idx = i
                        break

            _, m, n = children[idx]

        if found: solved += 1
        total_nodes += nodes
        elapsed = time.time() - t0
        print(f"  t{trial:>2}: {'Y' if found else 'n'}  {nodes:>10,}n  {elapsed:.1f}s", flush=True)

    print(f"  Weighted: {solved}/{n_trials} at {bits}b  ({total_nodes/n_trials:.0f} avg nodes)")
    return solved


# ============================================================
# EXPERIMENT 6: POLYNOMIAL FEATURE REGRESSION
# Learn weights for feature vector → score mapping
# ============================================================

def run_feature_regression(bits=20, n_trials=10, time_limit=10.0):
    """Learn linear weights for features using on-policy gradient.
    Score = w · features. Update w based on whether scent improved."""
    print(f"\n{'='*60}")
    print(f"  EXPERIMENT 6: Feature Weight Learning ({bits}b)")
    print(f"{'='*60}")

    # Initialize weights
    feat_names = ['min_scent', 'mean_scent', 'min_log_scent', 'harmonic_scent',
                  'min_quad_scent', 'min_size_prox', 'depth_est', 'smooth_m',
                  'n_valid_children']
    weights = {f: random.gauss(0, 0.5) for f in feat_names}
    lr = 0.01

    def score_fn(N, m, n):
        feats = extract_features(N, m, n)
        if feats is None: return 1.0
        return sum(weights.get(f, 0) * feats.get(f, 0) for f in feat_names)

    # Training phase
    print("  Training phase (50 episodes)...")
    for episode in range(50):
        p, q, N = gen_semi(bits, seed=500 + episode)
        m, n = 2, 1
        visited = {(m, n)}

        for step in range(2000):
            # Get all valid children with features
            children = []
            for M in ALL_MATS:
                m2, n2 = apply_mat(M, m, n)
                if not valid(m2, n2): continue
                if (m2, n2) in visited: continue
                f = check_factor(N, m2, n2)
                if f and 1 < f < N: break
                feats = extract_features(N, m2, n2)
                if feats is None: continue
                sc = sum(weights.get(f, 0) * feats.get(f, 0) for f in feat_names)
                children.append((sc, m2, n2, feats))
            else:
                if not children:
                    m, n = 2, 1
                    for _ in range(random.randint(5, 15)):
                        idx = random.randrange(N_FWD)
                        m2, n2 = apply_mat(FORWARD[idx], m, n)
                        if valid(m2, n2): m, n = m2, n2
                    visited.add((m, n))
                    continue
                # Pick best
                children.sort()
                chosen = children[0]
                _, m2, n2, chosen_feats = chosen

                # Reward signal: did scent improve?
                old_scent = 1.0
                for v in derived_values(m, n):
                    if v > 1:
                        r = N % v; s = min(r, v-r)/v
                        if s < old_scent: old_scent = s
                new_scent = chosen_feats.get('min_scent', 1.0)

                reward = 1.0 if new_scent < old_scent else -0.5

                # Update weights: push towards features that led to reward
                for f in feat_names:
                    fv = chosen_feats.get(f, 0)
                    weights[f] += lr * reward * fv

                m, n = m2, n2
                visited.add((m, n))
                continue
            break  # found factor

    # Print learned weights
    print("  Learned weights:")
    for f in sorted(feat_names, key=lambda f: abs(weights[f]), reverse=True):
        print(f"    {f:<20}: {weights[f]:>8.4f}")

    # Test phase
    print(f"\n  Testing learned policy...")
    solved = 0
    total_nodes = 0
    for trial in range(n_trials):
        p, q, N = gen_semi(bits, seed=42 + trial)
        t0 = time.time()
        m, n = 2, 1
        visited = {(m, n)}
        nodes = 1
        found = False
        stale = 0

        for step in range(100000):
            if time.time() - t0 > time_limit: break
            best_score = float('inf')
            best_mn = None
            for M in ALL_MATS:
                m2, n2 = apply_mat(M, m, n)
                if not valid(m2, n2): continue
                if (m2, n2) in visited: continue
                nodes += 1
                f = check_factor(N, m2, n2)
                if f and 1 < f < N:
                    found = True
                    break
                sc = score_fn(N, m2, n2)
                if sc < best_score:
                    best_score = sc
                    best_mn = (m2, n2)
            else:
                if best_mn is None or stale > 150:
                    m, n = 2, 1
                    for _ in range(random.randint(5, 25)):
                        idx = random.randrange(N_FWD)
                        m2, n2 = apply_mat(FORWARD[idx], m, n)
                        if valid(m2, n2): m, n = m2, n2
                    visited.add((m, n))
                    stale = 0
                    continue
                m, n = best_mn
                visited.add((m, n))
                stale += 1
                continue
            if found: break

        if found: solved += 1
        total_nodes += nodes
        elapsed = time.time() - t0
        print(f"  t{trial:>2}: {'Y' if found else 'n'}  {nodes:>10,}n  {elapsed:.1f}s", flush=True)

    print(f"  Feature Regression: {solved}/{n_trials} at {bits}b")
    return weights


# ============================================================
# MAIN: RUN ALL EXPERIMENTS
# ============================================================

if __name__ == "__main__":
    print("Pythagorean Tree Factoring — AI/ML Experiment Suite")
    print("=" * 60)

    bits = 20  # Start at 20b for fast iteration

    # Run all experiments
    run_ucb1_search(bits=bits, n_trials=10, time_limit=10.0)
    run_simulated_annealing(bits=bits, n_trials=10, time_limit=10.0)
    run_weighted_random(bits=bits, n_trials=10, time_limit=10.0)
    run_feature_regression(bits=bits, n_trials=10, time_limit=10.0)
    run_q_learning(bits=bits, n_episodes=100, n_test=10)
    run_gp_experiment(bits=bits, pop_size=20, generations=15, n_test=5)
