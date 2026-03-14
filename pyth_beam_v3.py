#!/usr/bin/env python3
"""
Pythagorean Tree Factoring — Diversified Beam Search v3

Improvements over v2 (focused_28b.py):
1. Batch GCD: accumulate product of node values mod N, check gcd periodically
   (Pollard rho batch trick — catches factors individual checks miss)
2. Wider beam (500) with more aggressive diversity
3. Better restart: restart from best-scent-ever neighborhood, not pure random
4. Multi-root: start beams from many deep random points
5. Smooth-weighted scent: prefer nodes with smoother coordinates
"""

import math
import random
import time
from math import gcd
from collections import defaultdict

# === Tree matrices (3x3 on (A,B,C) triples) ===
BERGGREN = [
    [( 1,-2, 2), ( 2,-1, 2), ( 2,-2, 3)],
    [( 1, 2, 2), ( 2, 1, 2), ( 2, 2, 3)],
    [(-1, 2, 2), (-2, 1, 2), (-2, 2, 3)],
]
PRICE = [
    [( 1, 0, 0), ( 2, 1, 0), ( 2, 0, 1)],
    [(-1, 0, 2), (-2, 1, 2), (-2, 0, 3)],
    [( 1, 0, 2), ( 2, 1, 2), ( 2, 0, 3)],
]
UNIQUE_MATRICES = BERGGREN + PRICE

def mat_inverse_3x3(M):
    a, b, c = M[0]; d, e, f = M[1]; g, h, i_ = M[2]
    det = a*(e*i_ - f*h) - b*(d*i_ - f*g) + c*(d*h - e*g)
    if abs(det) != 1: return None
    return [
        [det*(e*i_ - f*h), det*(c*h - b*i_), det*(b*f - c*e)],
        [det*(f*g - d*i_), det*(a*i_ - c*g), det*(c*d - a*f)],
        [det*(d*h - e*g), det*(b*g - a*h), det*(a*e - b*d)],
    ]

INVERSE_MATRICES = [mat_inverse_3x3(M) for M in UNIQUE_MATRICES]
ALL_MATRICES = UNIQUE_MATRICES + INVERSE_MATRICES[:3]
N_MATRICES = len(ALL_MATRICES)

def mat_mul(M, v):
    a, b, c = v
    return (M[0][0]*a + M[0][1]*b + M[0][2]*c,
            M[1][0]*a + M[1][1]*b + M[1][2]*c,
            M[2][0]*a + M[2][1]*b + M[2][2]*c)

# === Primality ===
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

def generate_semiprime(bits_per_factor, seed=None):
    if seed is not None: random.seed(seed)
    while True:
        p = random.getrandbits(bits_per_factor) | (1 << (bits_per_factor - 1)) | 1
        if miller_rabin(p): break
    while True:
        q = random.getrandbits(bits_per_factor) | (1 << (bits_per_factor - 1)) | 1
        if q != p and miller_rabin(q): break
    return min(p, q), max(p, q), p * q


# === Scent functions ===

def check_factor(N, val):
    """Check if val shares a factor with N."""
    if val <= 0: return None
    g = gcd(int(val), int(N))
    if 1 < g < N:
        return g
    return None

def scent_basic(N, node):
    """Basic scent: min(N mod v / v) for relevant values."""
    A, B, C = node
    if A <= 0 or B <= 0 or C <= 0: return 1.0
    best = 1.0
    for base in [max(1, C - B), C + B, A, C, B]:
        if base <= 0: continue
        r = N % base
        s = min(r, base - r) / base
        if s < best: best = s
    return best

def check_and_scent(N, node):
    """Check for factor and compute scent."""
    A, B, C = node
    if A <= 0 or B <= 0 or C <= 0: return None, 1.0
    diff = max(1, C - B)
    summ = C + B
    for base in [diff, summ, A, C, B]:
        if base <= 0: continue
        g = gcd(int(base), int(N))
        if 1 < g < N: return g, 0.0
    return None, scent_basic(N, node)

def batch_product_value(N, node):
    """Compute a product of all useful values from a node, mod N.
    Used for batch GCD: gcd(product_of_many_nodes, N)."""
    A, B, C = node
    if A <= 0 or B <= 0 or C <= 0: return 1
    diff = max(1, C - B)
    summ = C + B
    prod = 1
    for v in [A, B, C, diff, summ]:
        if v > 0:
            prod = prod * v % N
    return prod


# === v3 Beam Search ===

def beam_search_v3(N, beam_width=500, max_steps=15000, time_limit=60.0,
                   n_clusters=12, forced_diversity_frac=0.25,
                   batch_gcd_interval=50, restart_patience=8):
    """
    Diversified Beam Search v3 with batch GCD.

    Key innovations:
    1. Batch GCD: accumulate product of node values mod N across batches
    2. More clusters (12) for finer diversity at larger bit sizes
    3. Smart restarts from best-scent neighborhoods
    4. Deeper multi-root initialization (up to depth 30)
    """
    t0 = time.time()
    log2_N = math.log2(N) if N > 1 else 1
    log2_sqrt_N = log2_N / 2

    def cluster_id(node):
        C = node[2]
        if C <= 0: return 0
        log2_C = math.log2(C)
        bucket = int(log2_C / max(log2_sqrt_N, 1) * n_clusters)
        return min(max(bucket, 0), n_clusters * 4)

    cluster_capacity = max(3, beam_width // n_clusters)
    forced_random_count = int(beam_width * forced_diversity_frac)
    greedy_count = beam_width - forced_random_count

    # === Multi-root initialization ===
    visited = set()
    root = (3, 4, 5)

    initial_nodes = set()
    # Many starting depths including deeper ones
    for start_depth in list(range(0, 20, 2)) + [20, 25, 30]:
        for _ in range(3):  # Multiple random walks per depth
            node = root
            for _ in range(start_depth):
                idx = random.randrange(6)
                child = mat_mul(UNIQUE_MATRICES[idx], node)
                if child[0] > 0 and child[1] > 0 and child[2] > 0:
                    node = child
            initial_nodes.add(node)

    beam = []
    batch_product = 1
    batch_count = 0
    best_scent_ever = (float('inf'), root)

    for node in initial_nodes:
        if node not in visited:
            visited.add(node)
            f, s = check_and_scent(N, node)
            if f: return f, 0, time.time() - t0
            beam.append((s, node))
            # Batch GCD accumulation
            batch_product = batch_product * batch_product_value(N, node) % N
            batch_count += 1
            if s < best_scent_ever[0]:
                best_scent_ever = (s, node)

    beam.sort(key=lambda x: x[0])
    prev_best = float('inf')
    stuck_count = 0
    total_nodes = len(visited)

    for step in range(max_steps):
        if time.time() - t0 > time_limit: break

        candidates = []
        for _, node in beam:
            for m_idx in range(N_MATRICES):
                new_node = mat_mul(ALL_MATRICES[m_idx], node)
                if new_node[0] <= 0 or new_node[1] <= 0 or new_node[2] <= 0:
                    continue
                if new_node in visited: continue
                visited.add(new_node)
                total_nodes += 1

                f, s = check_and_scent(N, new_node)
                if f: return f, step, time.time() - t0
                candidates.append((s, new_node))

                # Track best ever
                if s < best_scent_ever[0]:
                    best_scent_ever = (s, new_node)

                # Batch GCD accumulation
                batch_product = batch_product * batch_product_value(N, new_node) % N
                batch_count += 1

        if not candidates: break

        # Periodic batch GCD check
        if batch_count >= batch_gcd_interval:
            g = gcd(batch_product, N)
            if 1 < g < N:
                return g, step, time.time() - t0
            batch_product = 1
            batch_count = 0

        candidates.sort(key=lambda x: x[0])

        # === Diversified selection ===
        cluster_counts = defaultdict(int)
        greedy_beam = []
        overflow = []

        for s, node in candidates:
            cid = cluster_id(node)
            if cluster_counts[cid] < cluster_capacity and len(greedy_beam) < greedy_count:
                greedy_beam.append((s, node))
                cluster_counts[cid] += 1
            else:
                overflow.append((s, node))

        # Forced random diversity from overflow
        random_beam = []
        if overflow:
            sample_size = min(forced_random_count, len(overflow))
            random_beam = random.sample(overflow, sample_size)

        new_beam = greedy_beam + random_beam
        new_beam.sort(key=lambda x: x[0])
        beam = new_beam[:beam_width]

        # === Smart restart detection ===
        best_s = beam[0][0] if beam else float('inf')
        if best_s < 0.001 and abs(best_s - prev_best) < 1e-12:
            stuck_count += 1
            if stuck_count >= restart_patience:
                # Smart restart: explore neighborhood of best-scent-ever node
                fresh_nodes = []
                base_node = best_scent_ever[1]

                for _ in range(beam_width // 2):
                    # Start from best-ever and random-walk a few steps
                    node = base_node
                    walk_len = random.randint(3, 15)
                    for _ in range(walk_len):
                        idx = random.randrange(N_MATRICES)
                        child = mat_mul(ALL_MATRICES[idx], node)
                        if child[0] > 0 and child[1] > 0 and child[2] > 0:
                            node = child
                    if node not in visited:
                        visited.add(node)
                        total_nodes += 1
                        f, s2 = check_and_scent(N, node)
                        if f: return f, step, time.time() - t0
                        fresh_nodes.append((s2, node))
                        batch_product = batch_product * batch_product_value(N, node) % N
                        batch_count += 1

                # Also inject some pure random nodes for exploration
                for _ in range(beam_width // 4):
                    node = root
                    depth = random.randint(10, 35)
                    for _ in range(depth):
                        idx = random.randrange(N_MATRICES)
                        child = mat_mul(ALL_MATRICES[idx], node)
                        if child[0] > 0 and child[1] > 0 and child[2] > 0:
                            node = child
                    if node not in visited:
                        visited.add(node)
                        total_nodes += 1
                        f, s2 = check_and_scent(N, node)
                        if f: return f, step, time.time() - t0
                        fresh_nodes.append((s2, node))
                        batch_product = batch_product * batch_product_value(N, node) % N
                        batch_count += 1

                if fresh_nodes:
                    fresh_nodes.sort(key=lambda x: x[0])
                    keep = int(len(beam) * 0.5)
                    beam = beam[:keep] + fresh_nodes[:beam_width - keep]
                    beam.sort(key=lambda x: x[0])
                stuck_count = 0
        else:
            stuck_count = max(0, stuck_count - 1)

        prev_best = best_s

    # Final batch GCD check
    if batch_count > 0:
        g = gcd(batch_product, N)
        if 1 < g < N:
            return g, max_steps, time.time() - t0

    return None, max_steps, time.time() - t0


# === v2 baseline from research sprint ===

def beam_search_v2(N, beam_width=200, max_steps=8000, time_limit=20.0,
                   n_clusters=8, forced_diversity_frac=0.3):
    """v2 diversified beam (the previous best)."""
    t0 = time.time()
    log2_N = math.log2(N) if N > 1 else 1
    log2_sqrt_N = log2_N / 2

    def cluster_id(node):
        C = node[2]
        if C <= 0: return 0
        log2_C = math.log2(C)
        bucket = int(log2_C / max(log2_sqrt_N, 1) * n_clusters)
        return min(max(bucket, 0), n_clusters * 3)

    cluster_capacity = max(3, beam_width // n_clusters)
    forced_random_count = int(beam_width * forced_diversity_frac)
    greedy_count = beam_width - forced_random_count

    visited = set()
    root = (3, 4, 5)
    initial_nodes = set()
    for start_depth in [0, 2, 4, 6, 8, 10, 12, 15]:
        node = root
        for _ in range(start_depth):
            idx = random.randrange(6)
            child = mat_mul(UNIQUE_MATRICES[idx], node)
            if child[0] > 0 and child[1] > 0 and child[2] > 0:
                node = child
        initial_nodes.add(node)

    beam = []
    for node in initial_nodes:
        if node not in visited:
            visited.add(node)
            f, s = check_and_scent(N, node)
            if f: return f, 0, 0.0
            beam.append((s, node))
    beam.sort(key=lambda x: x[0])
    prev_best = float('inf')
    stuck_count = 0

    for step in range(max_steps):
        if time.time() - t0 > time_limit: break
        candidates = []
        for _, node in beam:
            for m_idx in range(N_MATRICES):
                new_node = mat_mul(ALL_MATRICES[m_idx], node)
                if new_node[0] <= 0 or new_node[1] <= 0 or new_node[2] <= 0: continue
                if new_node in visited: continue
                visited.add(new_node)
                f, s = check_and_scent(N, new_node)
                if f: return f, step, time.time() - t0
                candidates.append((s, new_node))
        if not candidates: break
        candidates.sort(key=lambda x: x[0])

        cluster_counts = defaultdict(int)
        greedy_beam = []
        overflow = []
        for s, node in candidates:
            cid = cluster_id(node)
            if cluster_counts[cid] < cluster_capacity and len(greedy_beam) < greedy_count:
                greedy_beam.append((s, node))
                cluster_counts[cid] += 1
            else:
                overflow.append((s, node))

        random_beam = []
        if overflow:
            random_beam = random.sample(overflow, min(forced_random_count, len(overflow)))

        new_beam = greedy_beam + random_beam
        new_beam.sort(key=lambda x: x[0])
        beam = new_beam[:beam_width]

        best_s = beam[0][0] if beam else float('inf')
        if best_s < 0.0001 and abs(best_s - prev_best) < 1e-10:
            stuck_count += 1
            if stuck_count >= 5:
                fresh = []
                for _ in range(beam_width // 3):
                    node = root
                    for _ in range(random.randint(8, 25)):
                        idx = random.randrange(N_MATRICES)
                        child = mat_mul(ALL_MATRICES[idx], node)
                        if child[0] > 0 and child[1] > 0 and child[2] > 0:
                            node = child
                    if node not in visited:
                        visited.add(node)
                        f, s2 = check_and_scent(N, node)
                        if f: return f, step, time.time() - t0
                        fresh.append((s2, node))
                if fresh:
                    fresh.sort(key=lambda x: x[0])
                    keep = int(len(beam) * 2/3)
                    beam = beam[:keep] + fresh[:beam_width - keep]
                    beam.sort(key=lambda x: x[0])
                stuck_count = 0
        else:
            stuck_count = max(0, stuck_count - 1)
        prev_best = best_s

    return None, max_steps, time.time() - t0


# === Test harness ===

def run_comparison(bits_list, n_trials=15, v3_time=60.0, v2_time=20.0):
    print(f"{'Bits':>5} | {'v2 (beam=200)':>15} | {'v3 (beam=500+batch)':>20} | {'Delta':>6}")
    print("-" * 60)

    results = {}
    for bits in bits_list:
        v2_solved = 0
        v3_solved = 0

        for trial in range(n_trials):
            p, q, N = generate_semiprime(bits, seed=42 + trial)

            # v2
            f2, _, t2 = beam_search_v2(N, beam_width=200, max_steps=8000,
                                         time_limit=v2_time)
            if f2 and 1 < f2 < N: v2_solved += 1

            # v3
            f3, _, t3 = beam_search_v3(N, beam_width=500, max_steps=15000,
                                         time_limit=v3_time)
            if f3 and 1 < f3 < N: v3_solved += 1

        results[bits] = (v2_solved, v3_solved)
        delta = v3_solved - v2_solved
        print(f"{bits:>5} | {v2_solved:>7}/{n_trials:<7} | {v3_solved:>10}/{n_trials:<9} | {delta:>+5}")

    return results


if __name__ == "__main__":
    print("Pythagorean Tree Factoring — v3 vs v2 Comparison")
    print("=" * 60)
    print(f"v3: beam=500, batch_gcd, smart restarts, 60s limit")
    print(f"v2: beam=200, diversified, 20s limit")
    print()

    results = run_comparison([20, 24, 28, 32], n_trials=15,
                              v3_time=60.0, v2_time=20.0)

    print()
    print("=" * 60)
    print("FINAL RESULTS")
    for bits, (v2, v3) in results.items():
        print(f"  {bits}b: v2={v2}/15, v3={v3}/15 ({v3-v2:+d})")
