#!/usr/bin/env python3
"""
Pythagorean Tree Path Search — v3 Focused Heuristics

Top findings from v1/v2:
- quad_res wins beam search (N mod v² check)
- coprime wins greedy_restart (gcd(v*(v+1), N) check)
- beam_restart is better than plain beam
- composite/combined are decent but not #1

v3: Combine winners, add new ideas, test at 24b+ with fewer heuristics.
"""

import math
import random
import time
from math import gcd, log, isqrt
import heapq

# === 2×2 matrices on (m,n) column vectors ===
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
B1_inv = ((0, 1), (-1, 2))
B2_inv = ((0, 1), (1, -2))
B3_inv = ((1, -2), (0, 1))
INVERSE_MATRICES = [B1_inv, B2_inv, B3_inv]
ALL_MATRICES = FORWARD_MATRICES + INVERSE_MATRICES
N_MOVES = len(ALL_MATRICES)


def apply_mat(M, m, n):
    return M[0][0]*m + M[0][1]*n, M[1][0]*m + M[1][1]*n

def valid_mn(m, n):
    return m > 0 and n >= 0 and m > n


def derived_values(m, n):
    """All values from (m,n) that could share factor with N."""
    if not valid_mn(m, n):
        return []
    a = m*m - n*n
    b = 2*m*n
    c = m*m + n*n
    d = m - n
    s = m + n
    return [v for v in [a, b, c, m, n, d, s, d*d, s*s] if v > 0]


def check_factor(N, m, n):
    for v in derived_values(m, n):
        g = gcd(v, N)
        if 1 < g < N:
            return g
    return None


# ============================================================
# TOP HEURISTICS — focused set
# ============================================================

def h_quad_res(N, m, n):
    """Winner from v2: checks N mod v and N mod v² for quadratic proximity."""
    vals = derived_values(m, n)
    if not vals: return 1.0
    best = 1.0
    for v in vals:
        if v <= 1: continue
        r = N % v
        s1 = min(r, v - r) / v
        v2 = v * v
        if v2 > 0 and v2 < N:  # only if v² < N, otherwise v² mod N is not useful
            r2 = N % v2
            s2 = min(r2, v2 - r2) / v2
            s = min(s1, s2 * 0.8)
        else:
            s = s1
        if s < best: best = s
    return best


def h_coprime(N, m, n):
    """Runner-up from v2: checks gcd(v*(v+1), N) for consecutive product."""
    vals = derived_values(m, n)
    if not vals: return 1.0
    best = 1.0
    for v in vals:
        r = N % v
        near = min(r, v - r)
        s = near / v if v > 0 else 1.0
        if s < best: best = s
        if v > 1:
            g = gcd(v * (v + 1) % N, N)
            if 1 < g < N: return -1.0
    return best


def h_super(N, m, n):
    """Super-heuristic: combine quad_res + coprime + size weighting."""
    vals = derived_values(m, n)
    if not vals: return 1.0

    log_sqrtN = log(N) / 2
    best = 1.0
    best_size_weighted = 1.0

    for v in vals:
        if v <= 1: continue
        r = N % v
        s1 = min(r, v - r) / v

        # Quadratic check
        v2 = v * v
        if 1 < v2 < N:
            r2 = N % v2
            s2 = min(r2, v2 - r2) / v2
            s = min(s1, s2 * 0.8)
        else:
            s = s1

        if s < best: best = s

        # Size weighting: values near √N are most informative
        if v > 1:
            lv = log(v)
            size_w = 1.0 / (1.0 + abs(lv - log_sqrtN) / max(log_sqrtN, 1))
            sw = s * (2.0 - size_w)
            if sw < best_size_weighted: best_size_weighted = sw

        # Coprime consecutive product check
        g = gcd(v * (v + 1) % N, N)
        if 1 < g < N: return -1.0

    return best * 0.6 + best_size_weighted * 0.4


def h_super2(N, m, n):
    """Super2: quad_res + multi-k modular check + log-residue rank."""
    vals = derived_values(m, n)
    if not vals: return 1.0

    best_raw = 1.0
    best_log = 1.0

    for v in vals:
        if v <= 1: continue

        # Basic + quadratic
        r = N % v
        s1 = min(r, v - r) / v
        v2 = v * v
        if 1 < v2 < N:
            r2 = N % v2
            s2 = min(r2, v2 - r2) / v2
            s = min(s1, s2 * 0.85)
        else:
            s = s1
        if s < best_raw: best_raw = s

        # Log-residue rank
        near = min(r, v - r)
        if near > 0:
            lr = log(near + 1) / log(v + 1)
            if lr < best_log: best_log = lr

        # Multi-k: check small multiples
        for k in (2, 3):
            kv = k * v
            if kv > 0:
                rk = N % kv
                sk = min(rk, kv - rk) / kv
                if sk < best_raw: best_raw = sk

        # Coprime check
        g = gcd(v * (v + 1) % N, N)
        if 1 < g < N: return -1.0

    return best_raw * 0.5 + best_log * 0.5


def h_power_tower(N, m, n):
    """Power tower: check N mod v^k for k=1,2,3 — higher powers amplify signal."""
    vals = derived_values(m, n)
    if not vals: return 1.0
    best = 1.0
    for v in vals:
        if v <= 1: continue
        vk = v
        for k in range(1, 4):
            if vk >= N: break
            r = N % vk
            sk = min(r, vk - r) / vk
            # Higher powers get a bonus (smaller effective score)
            score = sk * (0.9 ** (k - 1))
            if score < best: best = score
            vk *= v

        # Coprime consecutive
        g = gcd(v * (v + 1) % N, N)
        if 1 < g < N: return -1.0
    return best


def h_difference_pairs(N, m, n):
    """Check gcd(v_i - v_j, N) for pairs of derived values.
    Birthday-like: if two values ≡ mod p, their difference is divisible by p."""
    vals = derived_values(m, n)
    if not vals: return 1.0

    # Standard scent first
    best = 1.0
    for v in vals:
        if v <= 1: continue
        r = N % v
        s = min(r, v - r) / v
        if s < best: best = s

    # Pairwise differences
    product = 1
    count = 0
    for i in range(len(vals)):
        for j in range(i+1, len(vals)):
            diff = abs(vals[i] - vals[j])
            if diff > 0:
                product = product * diff % N
                count += 1
                if count >= 20:
                    g = gcd(product, N)
                    if 1 < g < N: return -1.0
                    product = 1
                    count = 0
    if count > 0:
        g = gcd(product, N)
        if 1 < g < N: return -1.0

    return best


def h_accumulator(N, m, n, _state={}):
    """Stateful heuristic: accumulates a running product of all derived values
    seen across the search. Checks gcd(product, N) periodically.
    This is a Pollard-rho-like accumulation on the tree."""
    vals = derived_values(m, n)
    if not vals: return 1.0

    # Standard scent
    best = 1.0
    for v in vals:
        if v <= 1: continue
        r = N % v
        s = min(r, v - r) / v
        if s < best: best = s

    # Accumulate product (mod N)
    key = N
    if key not in _state:
        _state[key] = {'prod': 1, 'count': 0}
    st = _state[key]

    for v in vals:
        if v > 1:
            st['prod'] = st['prod'] * (v % N) % N
            st['count'] += 1

    if st['count'] >= 100:
        g = gcd(st['prod'], N)
        if 1 < g < N: return -2.0  # found via accumulation!
        st['prod'] = 1
        st['count'] = 0

    return best


HEURISTICS = {
    'quad_res':   h_quad_res,
    'coprime':    h_coprime,
    'super':      h_super,
    'super2':     h_super2,
    'power':      h_power_tower,
    'diff_pairs': h_difference_pairs,
    'accumulator': h_accumulator,
}


# ============================================================
# SEARCH STRATEGIES
# ============================================================

def beam_search(N, heuristic_fn, beam_width=30, max_steps=100000, time_limit=30.0):
    t0 = time.time()
    root = (2, 1)
    f = check_factor(N, *root)
    if f: return f, 0, time.time() - t0

    beam = [(heuristic_fn(N, *root), root)]
    visited = {root}
    nodes = 0

    for step in range(max_steps):
        if time.time() - t0 > time_limit: break
        candidates = []
        for _, (m, n) in beam:
            for M in ALL_MATRICES:
                m2, n2 = apply_mat(M, m, n)
                if not valid_mn(m2, n2): continue
                if (m2, n2) in visited: continue
                visited.add((m2, n2))
                nodes += 1
                f = check_factor(N, m2, n2)
                if f: return f, nodes, time.time() - t0
                score = heuristic_fn(N, m2, n2)
                candidates.append((score, (m2, n2)))
        if not candidates: break
        candidates.sort()
        beam = candidates[:beam_width]
    return None, nodes, time.time() - t0


def beam_restart(N, heuristic_fn, beam_width=30, max_steps=100000,
                 time_limit=30.0, patience=300):
    t0 = time.time()
    root = (2, 1)
    f = check_factor(N, *root)
    if f: return f, 0, time.time() - t0

    best_ever = float('inf')
    stale = 0
    beam = [(heuristic_fn(N, *root), root)]
    visited = {root}
    nodes = 0

    for step in range(max_steps):
        if time.time() - t0 > time_limit: break
        candidates = []
        for _, (m, n) in beam:
            for M in ALL_MATRICES:
                m2, n2 = apply_mat(M, m, n)
                if not valid_mn(m2, n2): continue
                if (m2, n2) in visited: continue
                visited.add((m2, n2))
                nodes += 1
                f = check_factor(N, m2, n2)
                if f: return f, nodes, time.time() - t0
                score = heuristic_fn(N, m2, n2)
                candidates.append((score, (m2, n2)))
        if not candidates or stale >= patience:
            m, n = 2, 1
            for _ in range(random.randint(8, 35)):
                idx = random.randrange(len(FORWARD_MATRICES))
                m2, n2 = apply_mat(FORWARD_MATRICES[idx], m, n)
                if valid_mn(m2, n2): m, n = m2, n2
            beam = [(heuristic_fn(N, m, n), (m, n))]
            stale = 0
            continue
        candidates.sort()
        beam = candidates[:beam_width]
        if beam[0][0] < best_ever:
            best_ever = beam[0][0]
            stale = 0
        else:
            stale += 1
    return None, nodes, time.time() - t0


def greedy_restart(N, heuristic_fn, max_steps=200000, time_limit=30.0, patience=150):
    t0 = time.time()
    m, n = 2, 1
    f = check_factor(N, m, n)
    if f: return f, 0, time.time() - t0

    visited = {(m, n)}
    best_ever = float('inf')
    stale = 0
    nodes = 0

    for step in range(max_steps):
        if time.time() - t0 > time_limit: break
        best_score = float('inf')
        best_mn = None
        for M in ALL_MATRICES:
            m2, n2 = apply_mat(M, m, n)
            if not valid_mn(m2, n2): continue
            if (m2, n2) in visited: continue
            f = check_factor(N, m2, n2)
            nodes += 1
            if f: return f, nodes, time.time() - t0
            score = heuristic_fn(N, m2, n2)
            if score < best_score:
                best_score = score
                best_mn = (m2, n2)
        if best_mn is None or stale >= patience:
            m, n = 2, 1
            for _ in range(random.randint(5, 30)):
                idx = random.randrange(len(FORWARD_MATRICES))
                m2, n2 = apply_mat(FORWARD_MATRICES[idx], m, n)
                if valid_mn(m2, n2): m, n = m2, n2
            visited.add((m, n))
            stale = 0
            continue
        m, n = best_mn
        visited.add((m, n))
        if best_score < best_ever:
            best_ever = best_score
            stale = 0
        else:
            stale += 1
    return None, nodes, time.time() - t0


# ============================================================
# BENCHMARKING
# ============================================================

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


def race(bits, n_trials, search_fn, time_limit, beam_width=30, label=""):
    results = {name: {'solved': 0, 'nodes': 0, 'time': 0.0} for name in HEURISTICS}

    for trial in range(n_trials):
        p, q, N = gen_semi(bits, seed=42 + trial)
        for name, hfn in HEURISTICS.items():
            # Reset accumulator state
            if hasattr(hfn, '__code__') and '_state' in hfn.__code__.co_varnames:
                h_accumulator.__defaults__[0].clear()

            if search_fn == 'beam':
                f, nodes, elapsed = beam_search(N, hfn, beam_width=beam_width,
                                                 time_limit=time_limit)
            elif search_fn == 'beam_restart':
                f, nodes, elapsed = beam_restart(N, hfn, beam_width=beam_width,
                                                  time_limit=time_limit)
            elif search_fn == 'greedy_restart':
                f, nodes, elapsed = greedy_restart(N, hfn, time_limit=time_limit)
            else:
                f, nodes, elapsed = beam_search(N, hfn, beam_width=beam_width,
                                                 time_limit=time_limit)

            results[name]['nodes'] += nodes
            results[name]['time'] += elapsed
            if f and 1 < f < N:
                results[name]['solved'] += 1

        # Progress indicator
        print(f"  trial {trial+1}/{n_trials} done", flush=True)

    return results


def show(results, n_trials, bits, label):
    print(f"\n{'Heuristic':<14} | {'Solved':>8} | {'Avg Nodes':>10} | {'Avg Time':>10}")
    print("-" * 55)
    ranked = sorted(results.items(), key=lambda x: (-x[1]['solved'], x[1]['nodes']))
    for name, r in ranked:
        avg_n = r['nodes'] / n_trials
        avg_t = r['time'] / n_trials
        print(f"{name:<14} | {r['solved']:>4}/{n_trials:<3} | {avg_n:>10,.0f} | {avg_t:>8.2f}s")


if __name__ == "__main__":
    print("Pythagorean Tree Heuristic Race — v3 (focused)")
    print("=" * 55)

    # 20b warmup
    print(f"\n--- 20b beam_restart (bw=30, 10s) ---")
    r = race(20, 10, 'beam_restart', 10.0, beam_width=30)
    show(r, 10, 20, 'beam_restart')

    # 24b — the real test
    print(f"\n--- 24b beam_restart (bw=30, 30s) ---")
    r = race(24, 10, 'beam_restart', 30.0, beam_width=30)
    show(r, 10, 24, 'beam_restart')

    # 24b greedy restart
    print(f"\n--- 24b greedy_restart (30s) ---")
    r = race(24, 10, 'greedy_restart', 30.0)
    show(r, 10, 24, 'greedy_restart')

    # 28b — pushing the limit
    print(f"\n--- 28b beam_restart (bw=50, 60s) ---")
    r = race(28, 10, 'beam_restart', 60.0, beam_width=50)
    show(r, 10, 28, 'beam_restart')
