#!/usr/bin/env python3
"""
Pythagorean Tree Factoring — Genetic Algorithm for Navigation Strategies

Evolves weight-vector strategies (Option C) that score each of 9 forward
Berggren matrices based on observable state features. The matrix with the
highest score is chosen at each step.

Memory-conscious: uses numpy arrays, no large dicts, <2GB total.
"""

import math
import random
import time
import sys
import json
import numpy as np
from math import gcd, log, isqrt
from collections import defaultdict

# ============================================================
# PYTHAGOREAN TREE INFRASTRUCTURE
# ============================================================

# 9 forward matrices (Berggren + Price + Fibonacci families)
B1 = ((2, -1), (1, 0))
B2 = ((2, 1), (1, 0))
B3 = ((1, 2), (0, 1))
P1 = ((1, 1), (0, 2))
P2 = ((2, 0), (1, -1))
P3 = ((2, 0), (1, 1))
F1 = ((3, -2), (1, -1))
F2 = ((3, 2), (1, 1))
F3 = ((1, 4), (0, 1))

FORWARD_MATRICES = [B1, B2, B3, P1, P2, P3, F1, F2, F3]
N_MATRICES = len(FORWARD_MATRICES)

# Inverse matrices for backtracking
B1_inv = ((0, 1), (-1, 2))
B2_inv = ((0, 1), (1, -2))
B3_inv = ((1, -2), (0, 1))
INVERSE_MATRICES = [B1_inv, B2_inv, B3_inv]
ALL_MATRICES = FORWARD_MATRICES + INVERSE_MATRICES


def apply_mat(M, m, n):
    return M[0][0] * m + M[0][1] * n, M[1][0] * m + M[1][1] * n


def valid_mn(m, n):
    return m > 0 and n >= 0 and m > n


def derived_values(m, n):
    """All values from (m,n) that could share a factor with N."""
    if not valid_mn(m, n):
        return []
    a = m * m - n * n
    b = 2 * m * n
    c = m * m + n * n
    d = m - n
    s = m + n
    return [v for v in [a, b, c, m, n, d, s] if v > 0]


def check_factor(N, m, n):
    """Check if any derived value shares a nontrivial factor with N."""
    for v in derived_values(m, n):
        g = gcd(v, N)
        if 1 < g < N:
            return g
    return None


# ============================================================
# PRIMALITY & SEMIPRIME GENERATION
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


def gen_semi(bits, rng=None):
    """Generate a balanced semiprime with given total bit length."""
    if rng is None:
        rng = random.Random()
    half = bits // 2
    while True:
        p = rng.getrandbits(half) | (1 << (half - 1)) | 1
        if miller_rabin(p):
            break
    while True:
        q = rng.getrandbits(bits - half) | (1 << (bits - half - 1)) | 1
        if q != p and miller_rabin(q):
            break
    return min(p, q), max(p, q), p * q


# ============================================================
# FEATURE EXTRACTION
# ============================================================

# Features computed per candidate (m,n) node:
#   0: min_scent        - min(N mod v / v) across derived values
#   1: min_log_scent    - min(log(near+1)/log(v+1))
#   2: min_quad_scent   - best scent using v^2
#   3: size_proximity   - min |log(v) - log(sqrt(N))| / log(sqrt(N))
#   4: depth_proxy      - log2(m + n + 1) (tree depth estimate)
#   5: m_mod8           - m mod 8 (normalized to [0,1])
#   6: n_mod8           - n mod 8 (normalized to [0,1])
#   7: ratio_mn         - m / (m + n) (shape of the triple)
#   8: coprime_signal   - max gcd(v*(v+1) mod N, N) / N indicator
#   9: smooth_score     - smoothness of m*n over small primes
#  10: step_phase       - (step mod 16) / 16

N_FEATURES = 11
FEATURE_NAMES = [
    "min_scent", "min_log_scent", "min_quad_scent", "size_proximity",
    "depth_proxy", "m_mod8", "n_mod8", "ratio_mn", "coprime_signal",
    "smooth_score", "step_phase",
]


def _smoothness(x):
    """Count small prime factors of x."""
    if x <= 1:
        return 0
    s = 0
    for p in (2, 3, 5, 7, 11, 13):
        while x % p == 0:
            s += 1
            x //= p
    return s + (3 if x == 1 else 0)


def extract_features(N, m, n, step, log_sqrtN):
    """Extract feature vector for a candidate (m,n) at given step.

    Returns numpy array of shape (N_FEATURES,) or None if invalid.
    """
    vals = derived_values(m, n)
    if not vals:
        return None

    scents = []
    log_scents = []
    size_proxs = []
    best_quad = 1.0
    best_coprime = 0.0

    for v in vals:
        if v <= 1:
            continue
        r = N % v
        near = min(r, v - r)
        sc = near / v
        scents.append(sc)

        if near > 0:
            log_scents.append(log(near + 1) / log(v + 1))
        else:
            log_scents.append(0.0)

        lv = log(v)
        size_proxs.append(abs(lv - log_sqrtN) / max(log_sqrtN, 0.1))

        # Quadratic scent
        v2 = v * v
        if 1 < v2 < N:
            r2 = N % v2
            s2 = min(r2, v2 - r2) / v2
            if s2 < best_quad:
                best_quad = s2

        # Coprime signal
        g = gcd(v * (v + 1) % N, N)
        if g > best_coprime and g < N:
            best_coprime = g

    if not scents:
        return None

    feats = np.zeros(N_FEATURES, dtype=np.float64)
    feats[0] = min(scents)
    feats[1] = min(log_scents) if log_scents else 1.0
    feats[2] = best_quad
    feats[3] = min(size_proxs) if size_proxs else 1.0
    feats[4] = log(m + n + 1) / 20.0  # normalized
    feats[5] = (m % 8) / 7.0
    feats[6] = (n % 8) / 7.0
    feats[7] = m / (m + n) if (m + n) > 0 else 0.5
    feats[8] = 1.0 if best_coprime > 1 else 0.0
    feats[9] = _smoothness(m * n % (10**9 + 7)) / 20.0  # normalized
    feats[10] = (step % 16) / 15.0
    return feats


# ============================================================
# GENOME: WEIGHT VECTOR
# ============================================================
# Genome shape: (N_MATRICES, N_FEATURES + 1)  -- +1 for bias
# For matrix i, score_i = weights[i] . features + bias[i]
# We pick argmax(scores).

GENOME_SIZE = N_MATRICES * (N_FEATURES + 1)  # 9 * 12 = 108


def genome_to_weights(genome):
    """Reshape flat genome to (N_MATRICES, N_FEATURES+1) weight matrix."""
    return genome.reshape(N_MATRICES, N_FEATURES + 1)


def score_matrices(weights, features):
    """Score all 9 matrices given features. Returns array of scores."""
    # weights[:, :N_FEATURES] dot features + weights[:, N_FEATURES] (bias)
    return weights[:, :N_FEATURES] @ features + weights[:, N_FEATURES]


# ============================================================
# NAVIGATION ENGINE
# ============================================================

def navigate(N, genome, max_steps=5000, use_restarts=True):
    """Navigate the Pythagorean tree using evolved weight-vector strategy.

    Returns (factor_or_None, steps_used, max_gcd_ratio).
    """
    weights = genome_to_weights(genome)
    log_sqrtN = log(N) / 2.0

    m, n = 2, 1
    f = check_factor(N, m, n)
    if f:
        return f, 1, 1.0

    best_gcd_ratio = 0.0
    stale = 0
    steps = 0

    for step in range(max_steps):
        steps += 1

        # Score each forward matrix
        best_score = -1e18
        best_m2, best_n2 = None, None

        for i, M in enumerate(FORWARD_MATRICES):
            m2, n2 = apply_mat(M, m, n)
            if not valid_mn(m2, n2):
                continue

            feats = extract_features(N, m2, n2, step, log_sqrtN)
            if feats is None:
                continue

            sc = float(weights[i, :N_FEATURES] @ feats + weights[i, N_FEATURES])
            if sc > best_score:
                best_score = sc
                best_m2, best_n2 = m2, n2

        if best_m2 is None:
            if use_restarts:
                # Random restart
                m, n = 2, 1
                for _ in range(random.randint(3, 15)):
                    idx = random.randrange(N_MATRICES)
                    m2, n2 = apply_mat(FORWARD_MATRICES[idx], m, n)
                    if valid_mn(m2, n2):
                        m, n = m2, n2
                stale = 0
                continue
            else:
                break

        m, n = best_m2, best_n2

        # Check for factor
        f = check_factor(N, m, n)
        if f:
            return f, steps, 1.0

        # Track best gcd ratio (for partial credit)
        for v in derived_values(m, n):
            if v > 1:
                g = gcd(v, N)
                ratio = g / N if g < N else 0
                if ratio > best_gcd_ratio:
                    best_gcd_ratio = ratio

        # Restart if stuck (no improvement for too long)
        stale += 1
        if use_restarts and stale > 200:
            m, n = 2, 1
            for _ in range(random.randint(5, 25)):
                idx = random.randrange(N_MATRICES)
                m2, n2 = apply_mat(FORWARD_MATRICES[idx], m, n)
                if valid_mn(m2, n2):
                    m, n = m2, n2
            stale = 0

    return None, steps, best_gcd_ratio


# ============================================================
# FITNESS EVALUATION
# ============================================================

def evaluate_fitness(genome, test_cases, max_steps=3000):
    """Evaluate a genome on a set of test semiprimes.

    Fitness = number_solved + 0.01 * sum(max_gcd_ratio) - 0.001 * avg_steps
    Higher is better.
    """
    solved = 0
    gcd_sum = 0.0
    step_sum = 0

    for N, p, q in test_cases:
        f, steps, gcd_ratio = navigate(N, genome, max_steps=max_steps)
        step_sum += steps
        if f and 1 < f < N:
            solved += 1
            gcd_sum += 1.0  # full credit
        else:
            gcd_sum += gcd_ratio

    n = len(test_cases)
    avg_steps = step_sum / n if n > 0 else 0
    fitness = solved + 0.01 * gcd_sum - 0.001 * (avg_steps / max_steps)
    return fitness


def evaluate_multi_scale(genome, case_sets, weights_per_scale, max_steps=3000):
    """Multi-objective fitness across multiple bit sizes.

    case_sets: list of (bit_size, test_cases) tuples
    weights_per_scale: list of floats summing to 1.0
    """
    total = 0.0
    for (bits, cases), w in zip(case_sets, weights_per_scale):
        fit = evaluate_fitness(genome, cases, max_steps=max_steps)
        total += w * fit
    return total


# ============================================================
# GENETIC OPERATORS
# ============================================================

def init_population(pop_size, rng):
    """Initialize population of weight-vector genomes."""
    pop = np.zeros((pop_size, GENOME_SIZE), dtype=np.float64)

    # Individual 0: all zeros (random walk baseline)
    # Individual 1: favor min_scent (feature 0) for all matrices
    pop[1, 0::N_FEATURES + 1] = -1.0  # negative scent = good (lower is better -> negate)

    # Individual 2: favor min_quad_scent (feature 2)
    pop[2, 2::N_FEATURES + 1] = -1.0

    # Individual 3: favor coprime_signal (feature 8)
    pop[3, 8::N_FEATURES + 1] = 2.0

    # Individual 4: favor size_proximity (feature 3)
    pop[4, 3::N_FEATURES + 1] = -1.0

    # Individual 5: combined scent heuristic
    for i in range(N_MATRICES):
        base = i * (N_FEATURES + 1)
        pop[5, base + 0] = -0.5   # min_scent
        pop[5, base + 1] = -0.3   # min_log_scent
        pop[5, base + 2] = -0.2   # min_quad_scent

    # Rest: small random weights
    for i in range(6, pop_size):
        pop[i] = rng.standard_normal(GENOME_SIZE) * 0.5

    return pop


def tournament_select(fitness, k, rng):
    """Tournament selection. Returns index of winner."""
    candidates = rng.choice(len(fitness), size=k, replace=False)
    return candidates[np.argmax(fitness[candidates])]


def uniform_crossover(parent1, parent2, rng):
    """Uniform crossover of two genomes."""
    mask = rng.random(GENOME_SIZE) < 0.5
    child = np.where(mask, parent1, parent2)
    return child


def block_crossover(parent1, parent2, rng):
    """Crossover entire matrix weight blocks."""
    child = parent1.copy()
    block_size = N_FEATURES + 1
    for i in range(N_MATRICES):
        if rng.random() < 0.5:
            start = i * block_size
            child[start:start + block_size] = parent2[start:start + block_size]
    return child


def mutate(genome, rate, rng):
    """Gaussian mutation."""
    child = genome.copy()
    mask = rng.random(GENOME_SIZE) < rate
    child[mask] += rng.standard_normal(int(mask.sum())) * 0.3
    return child


def mutate_reset(genome, rate, rng):
    """Reset mutation: randomly reset genes to new values."""
    child = genome.copy()
    mask = rng.random(GENOME_SIZE) < rate
    child[mask] = rng.standard_normal(int(mask.sum())) * 0.5
    return child


# ============================================================
# RANDOM WALK BASELINE
# ============================================================

def random_walk_baseline(test_cases, max_steps=3000, n_trials=5):
    """Baseline: pick a random forward matrix each step."""
    total_solved = 0
    total_gcd = 0.0

    for _ in range(n_trials):
        for N, p, q in test_cases:
            m, n = 2, 1
            found = False
            best_gcd = 0.0

            for step in range(max_steps):
                idx = random.randrange(N_MATRICES)
                m2, n2 = apply_mat(FORWARD_MATRICES[idx], m, n)
                if valid_mn(m2, n2):
                    m, n = m2, n2
                else:
                    # Try all, pick first valid
                    for M in FORWARD_MATRICES:
                        m2, n2 = apply_mat(M, m, n)
                        if valid_mn(m2, n2):
                            m, n = m2, n2
                            break

                f = check_factor(N, m, n)
                if f:
                    total_solved += 1
                    found = True
                    break

                for v in derived_values(m, n):
                    if v > 1:
                        g = gcd(v, N)
                        r = g / N if g < N else 0
                        if r > best_gcd:
                            best_gcd = r

            if not found:
                total_gcd += best_gcd

    avg_solved = total_solved / n_trials
    return avg_solved, total_gcd / n_trials


# ============================================================
# EVOLUTION ENGINE
# ============================================================

def evolve(case_sets, scale_weights, pop_size=200, generations=100,
           elitism=10, tournament_k=5, mutation_rate=0.05,
           max_steps=3000, seed=42, verbose=True):
    """Main evolution loop.

    Args:
        case_sets: list of (bit_size, [(N, p, q), ...]) tuples
        scale_weights: fitness weights per scale (sum to 1.0)
        pop_size: population size
        generations: number of generations
        elitism: number of elites preserved
        tournament_k: tournament size
        mutation_rate: per-gene mutation probability
        max_steps: max navigation steps per semiprime
        seed: random seed
        verbose: print progress

    Returns:
        best_genome, fitness_history
    """
    rng = np.random.default_rng(seed)
    py_rng = random.Random(seed)

    pop = init_population(pop_size, rng)
    fitness = np.zeros(pop_size)
    best_ever_fit = -1e18
    best_ever_genome = None
    history = []

    for gen in range(generations):
        t0 = time.time()

        # Evaluate all genomes
        for i in range(pop_size):
            random.seed(seed + gen * 1000 + i)  # reproducible navigation
            fitness[i] = evaluate_multi_scale(
                pop[i], case_sets, scale_weights, max_steps=max_steps
            )

        # Track best
        gen_best_idx = np.argmax(fitness)
        gen_best_fit = fitness[gen_best_idx]

        if gen_best_fit > best_ever_fit:
            best_ever_fit = gen_best_fit
            best_ever_genome = pop[gen_best_idx].copy()

        elapsed = time.time() - t0
        history.append(gen_best_fit)

        if verbose:
            mean_fit = np.mean(fitness)
            print(f"  Gen {gen:>3}: best={gen_best_fit:.4f}  "
                  f"mean={mean_fit:.4f}  best_ever={best_ever_fit:.4f}  "
                  f"[{elapsed:.1f}s]", flush=True)

        # Build next generation
        # Sort by fitness (descending)
        order = np.argsort(-fitness)
        new_pop = np.zeros_like(pop)

        # Elitism
        for i in range(elitism):
            new_pop[i] = pop[order[i]]

        # Fill rest with offspring
        idx = elitism
        while idx < pop_size:
            p1_idx = tournament_select(fitness, tournament_k, rng)
            p2_idx = tournament_select(fitness, tournament_k, rng)

            r = rng.random()
            if r < 0.4:
                child = uniform_crossover(pop[p1_idx], pop[p2_idx], rng)
            elif r < 0.7:
                child = block_crossover(pop[p1_idx], pop[p2_idx], rng)
            else:
                child = pop[p1_idx].copy()

            # Mutation
            if rng.random() < 0.8:
                child = mutate(child, mutation_rate, rng)
            if rng.random() < 0.1:
                child = mutate_reset(child, mutation_rate * 2, rng)

            # Clamp to prevent explosion
            np.clip(child, -10, 10, out=child)

            new_pop[idx] = child
            idx += 1

        pop = new_pop

    return best_ever_genome, history


# ============================================================
# ANALYSIS & DISPLAY
# ============================================================

def analyze_genome(genome):
    """Print human-readable interpretation of evolved genome."""
    weights = genome_to_weights(genome)
    mat_names = ["B1", "B2", "B3", "P1", "P2", "P3", "F1", "F2", "F3"]

    print("\n  Evolved Strategy (weight matrix):")
    print(f"  {'Matrix':<6}", end="")
    for fname in FEATURE_NAMES:
        print(f" {fname[:8]:>8}", end="")
    print(f" {'bias':>8}")
    print("  " + "-" * (6 + (N_FEATURES + 1) * 9))

    for i in range(N_MATRICES):
        print(f"  {mat_names[i]:<6}", end="")
        for j in range(N_FEATURES + 1):
            w = weights[i, j]
            if abs(w) > 0.5:
                print(f" {w:>8.3f}", end="")
            else:
                print(f" {w:>8.3f}", end="")
        print()

    # Identify strongest signals
    print("\n  Strongest feature preferences per matrix:")
    for i in range(N_MATRICES):
        top_idxs = np.argsort(-np.abs(weights[i, :N_FEATURES]))[:3]
        parts = []
        for j in top_idxs:
            w = weights[i, j]
            if abs(w) > 0.1:
                sign = "+" if w > 0 else "-"
                parts.append(f"{sign}{abs(w):.2f}*{FEATURE_NAMES[j]}")
        if parts:
            print(f"    {mat_names[i]}: {', '.join(parts)}")


def test_generalization(genome, bit_sizes, n_trials=20, max_steps=5000):
    """Test evolved genome on various bit sizes."""
    print("\n  Generalization Test:")
    print(f"  {'Bits':>6} {'Solved':>8} {'Rate':>8} {'Avg Steps':>10}")
    print("  " + "-" * 36)

    for bits in bit_sizes:
        solved = 0
        total_steps = 0
        rng = random.Random(42)

        for trial in range(n_trials):
            p, q, N = gen_semi(bits, rng=rng)
            random.seed(42 + trial)
            f, steps, _ = navigate(N, genome, max_steps=max_steps)
            total_steps += steps
            if f and 1 < f < N:
                solved += 1

        rate = solved / n_trials
        avg_steps = total_steps / n_trials
        print(f"  {bits:>6} {solved:>4}/{n_trials:<3} {rate:>7.1%} {avg_steps:>10.0f}")

    return


# ============================================================
# EXPERIMENTS
# ============================================================

def make_test_cases(bits, n_cases, base_seed=42):
    """Generate reproducible test semiprimes."""
    cases = []
    rng = random.Random(base_seed)
    for _ in range(n_cases):
        p, q, N = gen_semi(bits, rng=rng)
        cases.append((N, p, q))
    return cases


def experiment_1_single_scale():
    """Exp 1: Evolve on 16b, test generalization to 24b/32b/40b."""
    print("\n" + "=" * 65)
    print("EXPERIMENT 1: Evolve on 16b, test generalization")
    print("=" * 65)

    train_16 = make_test_cases(16, 50, base_seed=100)

    # Baseline
    print("\n  Random walk baseline (16b):")
    avg_solved, _ = random_walk_baseline(train_16, max_steps=3000, n_trials=3)
    print(f"    Avg solved: {avg_solved:.1f}/50")

    # Evolve
    print("\n  Evolving on 16b (pop=200, gen=100)...")
    case_sets = [(16, train_16)]
    genome, history = evolve(
        case_sets, scale_weights=[1.0],
        pop_size=200, generations=100, max_steps=3000,
        seed=42
    )

    analyze_genome(genome)

    # Training curve
    print("\n  Training curve (best fitness per generation):")
    milestones = [0, 9, 24, 49, 74, 99]
    for i in milestones:
        if i < len(history):
            print(f"    Gen {i:>3}: {history[i]:.4f}")

    # Generalization
    test_generalization(genome, [16, 20, 24, 28, 32, 40], n_trials=20, max_steps=5000)

    return genome, history


def experiment_2_multi_scale():
    """Exp 2: Evolve on mixed 16b+24b+32b, test generalization."""
    print("\n" + "=" * 65)
    print("EXPERIMENT 2: Multi-scale evolution (16b + 24b + 32b)")
    print("=" * 65)

    train_16 = make_test_cases(16, 30, base_seed=200)
    train_24 = make_test_cases(24, 20, base_seed=201)
    train_32 = make_test_cases(32, 10, base_seed=202)

    print("\n  Evolving on mixed scales (pop=200, gen=100)...")
    case_sets = [(16, train_16), (24, train_24), (32, train_32)]
    scale_weights = [0.5, 0.3, 0.2]

    genome, history = evolve(
        case_sets, scale_weights=scale_weights,
        pop_size=200, generations=100, max_steps=4000,
        seed=123
    )

    analyze_genome(genome)

    print("\n  Training curve:")
    milestones = [0, 9, 24, 49, 74, 99]
    for i in milestones:
        if i < len(history):
            print(f"    Gen {i:>3}: {history[i]:.4f}")

    test_generalization(genome, [16, 24, 32, 40, 48], n_trials=15, max_steps=5000)

    return genome, history


def experiment_3_adaptive_mutation():
    """Exp 3: Self-adaptive mutation rate (each genome carries its own rate)."""
    print("\n" + "=" * 65)
    print("EXPERIMENT 3: Self-adaptive mutation")
    print("=" * 65)

    train_16 = make_test_cases(16, 40, base_seed=300)
    train_24 = make_test_cases(24, 20, base_seed=301)

    rng = np.random.default_rng(42)
    py_rng = random.Random(42)
    pop_size = 200
    generations = 80
    elitism = 10
    tournament_k = 5
    max_steps = 3000

    # Genome + mutation rate (last element)
    ext_size = GENOME_SIZE + 1
    pop = np.zeros((pop_size, ext_size))
    pop[:, :GENOME_SIZE] = init_population(pop_size, rng)
    pop[:, -1] = 0.05  # initial mutation rate

    fitness = np.zeros(pop_size)
    best_ever_fit = -1e18
    best_ever_genome = None
    history = []

    case_sets = [(16, train_16), (24, train_24)]
    scale_weights = [0.6, 0.4]

    for gen in range(generations):
        t0 = time.time()

        for i in range(pop_size):
            random.seed(42 + gen * 1000 + i)
            fitness[i] = evaluate_multi_scale(
                pop[i, :GENOME_SIZE], case_sets, scale_weights, max_steps=max_steps
            )

        gen_best_idx = np.argmax(fitness)
        gen_best_fit = fitness[gen_best_idx]

        if gen_best_fit > best_ever_fit:
            best_ever_fit = gen_best_fit
            best_ever_genome = pop[gen_best_idx, :GENOME_SIZE].copy()

        elapsed = time.time() - t0
        history.append(gen_best_fit)
        avg_rate = np.mean(pop[:, -1])

        if gen % 10 == 0 or gen == generations - 1:
            print(f"  Gen {gen:>3}: best={gen_best_fit:.4f}  "
                  f"best_ever={best_ever_fit:.4f}  "
                  f"avg_mut_rate={avg_rate:.4f}  [{elapsed:.1f}s]", flush=True)

        # Next generation
        order = np.argsort(-fitness)
        new_pop = np.zeros_like(pop)

        for i in range(elitism):
            new_pop[i] = pop[order[i]]

        idx = elitism
        while idx < pop_size:
            p1_idx = tournament_select(fitness, tournament_k, rng)
            p2_idx = tournament_select(fitness, tournament_k, rng)

            # Crossover genome
            mask = rng.random(GENOME_SIZE) < 0.5
            child_genome = np.where(mask, pop[p1_idx, :GENOME_SIZE],
                                    pop[p2_idx, :GENOME_SIZE])

            # Crossover + mutate the mutation rate itself
            child_rate = (pop[p1_idx, -1] + pop[p2_idx, -1]) / 2
            child_rate *= np.exp(rng.standard_normal() * 0.1)
            child_rate = np.clip(child_rate, 0.001, 0.3)

            # Apply mutation using self-adapted rate
            mut_mask = rng.random(GENOME_SIZE) < child_rate
            child_genome[mut_mask] += rng.standard_normal(int(mut_mask.sum())) * 0.3
            np.clip(child_genome, -10, 10, out=child_genome)

            new_pop[idx, :GENOME_SIZE] = child_genome
            new_pop[idx, -1] = child_rate
            idx += 1

        pop = new_pop

    analyze_genome(best_ever_genome)
    test_generalization(best_ever_genome, [16, 24, 32, 40], n_trials=15, max_steps=5000)

    return best_ever_genome, history


def experiment_4_coevolution():
    """Exp 4: Co-evolve navigators AND hard semiprimes (arms race)."""
    print("\n" + "=" * 65)
    print("EXPERIMENT 4: Co-evolution (navigators vs adversarial semiprimes)")
    print("=" * 65)

    rng_np = np.random.default_rng(42)
    nav_pop_size = 100
    adv_pop_size = 30
    generations = 60
    max_steps = 3000
    bits = 20  # adversary generates semiprimes at this size

    # Navigator population
    nav_pop = init_population(nav_pop_size, rng_np)
    nav_fitness = np.zeros(nav_pop_size)

    # Adversary population: each adversary is a list of seeds that generate semiprimes
    # The adversary "chooses" which semiprimes to test navigators on
    n_cases_per_adv = 15
    adv_pop = rng_np.integers(0, 2**31, size=(adv_pop_size, n_cases_per_adv))
    adv_fitness = np.zeros(adv_pop_size)

    best_nav = None
    best_nav_fit = -1e18
    history_nav = []
    history_adv = []

    for gen in range(generations):
        t0 = time.time()

        # For each adversary, generate its semiprimes
        adv_cases = []
        for a in range(adv_pop_size):
            cases = []
            for s in adv_pop[a]:
                rng_case = random.Random(int(s))
                p, q, N = gen_semi(bits, rng=rng_case)
                cases.append((N, p, q))
            adv_cases.append(cases)

        # Evaluate navigators against ALL adversaries
        # nav_fitness[i] = avg across adversaries
        # adv_fitness[a] = avg navigator failure rate on its cases
        nav_scores = np.zeros((nav_pop_size, adv_pop_size))

        for i in range(nav_pop_size):
            for a in range(adv_pop_size):
                random.seed(42 + gen * 10000 + i * 100 + a)
                fit = evaluate_fitness(nav_pop[i], adv_cases[a], max_steps=max_steps)
                nav_scores[i, a] = fit

        nav_fitness = np.mean(nav_scores, axis=1)
        # Adversary fitness = how hard its cases are (low navigator scores)
        adv_fitness = -np.mean(nav_scores, axis=0)

        gen_best_nav = np.argmax(nav_fitness)
        if nav_fitness[gen_best_nav] > best_nav_fit:
            best_nav_fit = nav_fitness[gen_best_nav]
            best_nav = nav_pop[gen_best_nav].copy()

        elapsed = time.time() - t0
        history_nav.append(float(nav_fitness[gen_best_nav]))
        history_adv.append(float(-np.min(adv_fitness)))

        if gen % 5 == 0 or gen == generations - 1:
            print(f"  Gen {gen:>3}: nav_best={nav_fitness[gen_best_nav]:.4f}  "
                  f"adv_hardest={-np.min(adv_fitness):.4f}  [{elapsed:.1f}s]",
                  flush=True)

        # Evolve navigators
        order = np.argsort(-nav_fitness)
        new_nav = np.zeros_like(nav_pop)
        for i in range(5):  # elitism
            new_nav[i] = nav_pop[order[i]]
        idx = 5
        while idx < nav_pop_size:
            p1 = tournament_select(nav_fitness, 5, rng_np)
            p2 = tournament_select(nav_fitness, 5, rng_np)
            child = block_crossover(nav_pop[p1], nav_pop[p2], rng_np)
            child = mutate(child, 0.05, rng_np)
            np.clip(child, -10, 10, out=child)
            new_nav[idx] = child
            idx += 1
        nav_pop = new_nav

        # Evolve adversaries (mutate seeds)
        order_a = np.argsort(-adv_fitness)
        new_adv = np.zeros_like(adv_pop)
        for i in range(3):
            new_adv[i] = adv_pop[order_a[i]]
        for i in range(3, adv_pop_size):
            parent = adv_pop[order_a[rng_np.integers(0, adv_pop_size // 2)]]
            child = parent.copy()
            # Mutate ~20% of seeds
            mask = rng_np.random(n_cases_per_adv) < 0.2
            child[mask] = rng_np.integers(0, 2**31, size=int(mask.sum()))
            new_adv[i] = child
        adv_pop = new_adv

    print("\n  Co-evolved navigator:")
    analyze_genome(best_nav)
    test_generalization(best_nav, [16, 20, 24, 28, 32], n_trials=15, max_steps=5000)

    return best_nav, history_nav


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 65)
    print("Pythagorean Tree Factoring — Genetic Navigation Strategy Evolution")
    print("=" * 65)
    print(f"Genome size: {GENOME_SIZE} genes ({N_MATRICES} matrices x "
          f"{N_FEATURES + 1} weights)")
    print(f"Features: {', '.join(FEATURE_NAMES)}")
    print()

    results = {}

    # Experiment 1: Single-scale
    genome1, hist1 = experiment_1_single_scale()
    results["exp1"] = {"genome": genome1.tolist(), "history": hist1}

    # Experiment 2: Multi-scale
    genome2, hist2 = experiment_2_multi_scale()
    results["exp2"] = {"genome": genome2.tolist(), "history": hist2}

    # Experiment 3: Self-adaptive mutation
    genome3, hist3 = experiment_3_adaptive_mutation()
    results["exp3"] = {"genome": genome3.tolist(), "history": hist3}

    # Experiment 4: Co-evolution
    genome4, hist4 = experiment_4_coevolution()
    results["exp4"] = {"genome": genome4.tolist(), "history": hist4}

    # Summary
    print("\n" + "=" * 65)
    print("SUMMARY")
    print("=" * 65)

    print("\n  Training curves (final generation fitness):")
    for name, data in results.items():
        h = data["history"]
        print(f"    {name}: start={h[0]:.4f} -> end={h[-1]:.4f}  "
              f"(improvement: {h[-1] - h[0]:+.4f})")

    # Save best genome
    best_name = max(results.keys(), key=lambda k: results[k]["history"][-1])
    best_genome = np.array(results[best_name]["genome"])
    save_data = {
        "genome": best_genome.tolist(),
        "n_features": N_FEATURES,
        "n_matrices": N_MATRICES,
        "feature_names": FEATURE_NAMES,
        "source_experiment": best_name,
    }
    with open("pyth_genetic_best.json", "w") as f:
        json.dump(save_data, f, indent=2)
    print(f"\n  Best genome saved to pyth_genetic_best.json (from {best_name})")

    # Final generalization of best
    print(f"\n  Final generalization of best ({best_name}):")
    test_generalization(best_genome, [16, 20, 24, 28, 32, 40, 48],
                        n_trials=20, max_steps=8000)
