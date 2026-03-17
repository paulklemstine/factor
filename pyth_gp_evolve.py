#!/usr/bin/env python3
"""
Pythagorean Tree — Genetic Programming Heuristic Evolution

Phase 1 (OFFLINE): Evolve heuristic functions on small semiprimes (16-20b)
Phase 2 (FREEZE): Export best evolved heuristic as a fixed function
Phase 3 (BENCHMARK): Run frozen heuristic on harder problems (24-32b)

The GP evolves arithmetic expression trees over a feature vector.
Fitness = number of semiprimes factored + speed bonus.
"""

import math
import random
import time
import operator
import pickle
import json
from math import gcd, log
from collections import defaultdict

# ============================================================
# TREE INFRASTRUCTURE (minimal)
# ============================================================

B1 = ((2,-1),(1,0)); B2 = ((2,1),(1,0)); B3 = ((1,2),(0,1))
P1 = ((1,1),(0,2)); P2 = ((2,0),(1,-1)); P3 = ((2,0),(1,1))
F1 = ((3,-2),(1,-1)); F2 = ((3,2),(1,1)); F3 = ((1,4),(0,1))
FORWARD = [B1,B2,B3,P1,P2,P3,F1,F2,F3]
B1i = ((0,1),(-1,2)); B2i = ((0,1),(1,-2)); B3i = ((1,-2),(0,1))
ALL_MATS = FORWARD + [B1i, B2i, B3i]
N_FWD = 9; N_ALL = 12

def apply_mat(M, m, n):
    return M[0][0]*m + M[0][1]*n, M[1][0]*m + M[1][1]*n

def valid(m, n): return m > 0 and n >= 0 and m > n

def derived_values(m, n):
    if not valid(m, n): return []
    a = m*m-n*n; b = 2*m*n; c = m*m+n*n; d = m-n; s = m+n
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
# FEATURE EXTRACTION (fast version — 11 features)
# ============================================================

FEAT_NAMES = [
    'min_scent',       # min(N mod v / v) across derived values
    'min_log_scent',   # min(log(near+1)/log(v+1))
    'harmonic_scent',  # harmonic mean of scent values
    'min_quad_scent',  # min scent using v²
    'min_size_prox',   # min |log(v) - log(√N)| / log(√N)
    'depth_est',       # log(m+n+1) — proxy for tree depth
    'smooth_m',        # smoothness of m (small prime factors)
    'smooth_n',        # smoothness of n
    'n_children',      # number of valid children from this node
    'm_ratio',         # m / n
    'log_c',           # log(hypotenuse)
]
N_FEATS = len(FEAT_NAMES)

def extract_features(N, m, n):
    """Fast feature extraction — returns list of floats."""
    vals = derived_values(m, n)
    if not vals: return None

    log_N = log(N)
    log_sqrtN = log_N / 2
    scents = []; log_scents = []; size_proxs = []

    for v in vals:
        if v <= 1: continue
        r = N % v
        near = min(r, v - r)
        scents.append(near / v)
        log_scents.append(log(near + 1) / log(v + 1) if near > 0 else 0.0)
        size_proxs.append(abs(log(v) - log_sqrtN) / max(log_sqrtN, 1))

    if not scents: return None

    # Harmonic mean
    inv_sum = sum(1/s for s in scents if s > 0)
    harmonic = len(scents) / inv_sum if inv_sum > 0 else 1.0

    # Quad scent
    best_quad = 1.0
    for v in vals:
        if v <= 1: continue
        v2 = v * v
        if 1 < v2 < N:
            r2 = N % v2; s2 = min(r2, v2 - r2) / v2
            if s2 < best_quad: best_quad = s2

    # Smoothness
    def smooth(x):
        if x <= 1: return 0
        s = 0
        for p in [2,3,5,7,11,13]:
            while x % p == 0: s += 1; x //= p
        return s + (5 if x == 1 else 0)

    # Children count
    nc = sum(1 for M in ALL_MATS for (m2,n2) in [apply_mat(M,m,n)] if valid(m2,n2))

    c = m*m + n*n

    return [
        min(scents),          # min_scent
        min(log_scents),      # min_log_scent
        harmonic,             # harmonic_scent
        best_quad,            # min_quad_scent
        min(size_proxs),      # min_size_prox
        log(m + n + 1),       # depth_est
        smooth(m),            # smooth_m
        smooth(n),            # smooth_n
        nc,                   # n_children
        m / max(n, 1),        # m_ratio
        log(c) if c > 0 else 0,  # log_c
    ]


# ============================================================
# GP EXPRESSION TREES
# ============================================================

def safe_div(a, b): return a / b if abs(b) > 1e-10 else a
def safe_log(a): return log(abs(a) + 1e-10)

OPS = {
    '+': (operator.add, 2),
    '-': (operator.sub, 2),
    '*': (operator.mul, 2),
    '/': (safe_div, 2),
    'min': (min, 2),
    'max': (max, 2),
    'neg': (operator.neg, 1),
    'abs': (abs, 1),
    'log': (safe_log, 1),
    'sq': (lambda x: x*x, 1),
    'inv': (lambda x: 1/(x+1e-10), 1),
}

class Expr:
    """Expression tree node."""
    __slots__ = ['kind', 'op', 'children', 'feat_idx', 'const_val']

    def __init__(self, kind, op=None, children=None, feat_idx=None, const_val=None):
        self.kind = kind  # 'op', 'feat', 'const'
        self.op = op
        self.children = children or []
        self.feat_idx = feat_idx
        self.const_val = const_val

    def eval(self, feats):
        if self.kind == 'feat':
            return feats[self.feat_idx]
        if self.kind == 'const':
            return self.const_val
        fn, _ = OPS[self.op]
        try:
            args = [c.eval(feats) for c in self.children]
            r = fn(*args)
            if not math.isfinite(r): return 1.0
            return max(-1e6, min(1e6, r))
        except:
            return 1.0

    def depth(self):
        if self.kind != 'op': return 0
        return 1 + max((c.depth() for c in self.children), default=0)

    def size(self):
        if self.kind != 'op': return 1
        return 1 + sum(c.size() for c in self.children)

    def copy(self):
        if self.kind == 'feat': return Expr('feat', feat_idx=self.feat_idx)
        if self.kind == 'const': return Expr('const', const_val=self.const_val)
        return Expr('op', op=self.op, children=[c.copy() for c in self.children])

    def to_str(self):
        if self.kind == 'feat': return FEAT_NAMES[self.feat_idx]
        if self.kind == 'const': return f"{self.const_val:.3f}"
        args = ", ".join(c.to_str() for c in self.children)
        return f"{self.op}({args})"

    def to_dict(self):
        """Serialize to JSON-compatible dict."""
        if self.kind == 'feat': return {'k': 'f', 'i': self.feat_idx}
        if self.kind == 'const': return {'k': 'c', 'v': self.const_val}
        return {'k': 'o', 'op': self.op, 'ch': [c.to_dict() for c in self.children]}

    @staticmethod
    def from_dict(d):
        if d['k'] == 'f': return Expr('feat', feat_idx=d['i'])
        if d['k'] == 'c': return Expr('const', const_val=d['v'])
        return Expr('op', op=d['op'], children=[Expr.from_dict(c) for c in d['ch']])


def random_expr(max_depth=4):
    if max_depth <= 0 or random.random() < 0.3:
        if random.random() < 0.7:
            return Expr('feat', feat_idx=random.randrange(N_FEATS))
        else:
            return Expr('const', const_val=random.uniform(-2, 2))
    op = random.choice(list(OPS.keys()))
    _, arity = OPS[op]
    return Expr('op', op=op, children=[random_expr(max_depth-1) for _ in range(arity)])


def mutate(tree, rate=0.2):
    t = tree.copy()
    if random.random() < rate:
        return random_expr(3)
    if t.kind == 'op' and t.children:
        idx = random.randrange(len(t.children))
        t.children[idx] = mutate(t.children[idx], rate)
    elif t.kind == 'const':
        t.const_val += random.gauss(0, 0.5)
    return t


def crossover(t1, t2):
    c = t1.copy()
    d = t2.copy()
    if c.kind == 'op' and c.children and d.kind == 'op' and d.children:
        ci = random.randrange(len(c.children))
        di = random.randrange(len(d.children))
        c.children[ci] = d.children[di].copy()
    return c


# ============================================================
# FAST EVALUATION — greedy search with GP heuristic
# ============================================================

def gp_search(N, expr, max_steps=10000, time_limit=1.0):
    """Greedy+restart search using GP expression as heuristic."""
    t0 = time.time()
    m, n = 2, 1
    f = check_factor(N, m, n)
    if f: return f, 1

    visited = {(m, n)}
    nodes = 1
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
            nodes += 1
            if f: return f, nodes

            feats = extract_features(N, m2, n2)
            if feats is None: continue
            sc = expr.eval(feats)
            if sc < best_score:
                best_score = sc
                best_mn = (m2, n2)

        if best_mn is None or stale > 100:
            # Restart
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

    return None, nodes


def evaluate_fitness(expr, test_cases, time_per=0.5):
    """Fitness: solved count + node efficiency bonus."""
    solved = 0
    total_nodes = 0
    for N, p, q in test_cases:
        f, nodes = gp_search(N, expr, max_steps=20000, time_limit=time_per)
        total_nodes += nodes
        if f and 1 < f < N:
            solved += 1
    return solved + 0.0001 / (total_nodes + 1)


# ============================================================
# EVOLUTION
# ============================================================

def evolve(bits=18, pop_size=50, generations=30, n_train=10,
           time_per_case=0.3, seed=42):
    """Evolve GP heuristic. Returns best expression tree."""
    random.seed(seed)

    # Training cases (different seeds than benchmark)
    train = []
    for i in range(n_train):
        p, q, N = gen_semi(bits, seed=1000 + i)
        train.append((N, p, q))

    # Initialize population with some hand-seeded individuals
    pop = []

    # Seed 1: min_scent (baseline)
    pop.append(Expr('feat', feat_idx=0))

    # Seed 2: min_log_scent
    pop.append(Expr('feat', feat_idx=1))

    # Seed 3: min_quad_scent
    pop.append(Expr('feat', feat_idx=3))

    # Seed 4: 0.5*min_scent + 0.3*min_log_scent + 0.2*min_size_prox
    pop.append(Expr('op', op='+', children=[
        Expr('op', op='*', children=[
            Expr('const', const_val=0.5),
            Expr('feat', feat_idx=0)]),
        Expr('op', op='+', children=[
            Expr('op', op='*', children=[
                Expr('const', const_val=0.3),
                Expr('feat', feat_idx=1)]),
            Expr('op', op='*', children=[
                Expr('const', const_val=0.2),
                Expr('feat', feat_idx=4)])])
    ]))

    # Fill rest with random
    while len(pop) < pop_size:
        pop.append(random_expr(4))

    best_ever_fit = -1
    best_ever = None

    for gen in range(generations):
        t0 = time.time()

        # Evaluate
        fitness = [evaluate_fitness(e, train, time_per=time_per_case) for e in pop]

        # Track best
        idx_best = max(range(len(fitness)), key=lambda i: fitness[i])
        if fitness[idx_best] > best_ever_fit:
            best_ever_fit = fitness[idx_best]
            best_ever = pop[idx_best].copy()

        solved = int(best_ever_fit)
        elapsed = time.time() - t0
        print(f"  Gen {gen:>3}: best={best_ever_fit:.4f} ({solved}/{n_train})  "
              f"depth={best_ever.depth()} size={best_ever.size()}  [{elapsed:.1f}s]",
              flush=True)

        if solved >= n_train:
            print(f"  *** Perfect! ***")
            break

        # Selection + reproduction
        new_pop = [best_ever.copy()]  # elitism

        while len(new_pop) < pop_size:
            # Tournament of 3
            cands = random.sample(range(len(pop)), min(3, len(pop)))
            winner = max(cands, key=lambda i: fitness[i])

            if random.random() < 0.3 and len(new_pop) > 1:
                other = random.choice(new_pop)
                child = crossover(pop[winner], other)
            elif random.random() < 0.7:
                child = mutate(pop[winner], rate=0.25)
            else:
                child = random_expr(4)  # fresh blood

            if child.depth() > 8:
                child = random_expr(3)

            new_pop.append(child)

        pop = new_pop

    return best_ever


def validate_and_freeze(expr, bits_list=[16, 20, 24], n_trials=10, time_limit=5.0):
    """Validate evolved heuristic on multiple bit sizes, then freeze."""
    print(f"\n  Evolved heuristic: {expr.to_str()}")
    print(f"  Depth={expr.depth()}, Size={expr.size()}")

    for bits in bits_list:
        solved = 0
        total_nodes = 0
        t_total = 0.0
        for trial in range(n_trials):
            p, q, N = gen_semi(bits, seed=42 + trial)
            t0 = time.time()
            f, nodes = gp_search(N, expr, max_steps=100000, time_limit=time_limit)
            elapsed = time.time() - t0
            total_nodes += nodes
            t_total += elapsed
            if f and 1 < f < N: solved += 1

        avg_n = total_nodes / n_trials
        avg_t = t_total / n_trials
        print(f"  {bits}b: {solved}/{n_trials}  avg {avg_n:,.0f} nodes  {avg_t:.2f}s")

    # Freeze to JSON
    frozen = expr.to_dict()
    with open('evolved_heuristic.json', 'w') as f:
        json.dump(frozen, f, indent=2)
    print(f"\n  Frozen to evolved_heuristic.json")
    return frozen


if __name__ == "__main__":
    print("Pythagorean GP Heuristic Evolution")
    print("=" * 55)

    # Phase 1: Evolve at 16b (very fast iteration, ~5s/gen)
    print("\n--- Phase 1: Evolution at 16b ---")
    best16 = evolve(bits=16, pop_size=30, generations=20, n_train=5,
                    time_per_case=0.1, seed=42)

    # Phase 2: Evolve at 18b using 16b winner as seed
    print("\n--- Phase 2: Evolution at 18b ---")
    best18 = evolve(bits=18, pop_size=30, generations=20, n_train=5,
                    time_per_case=0.2, seed=123)

    # Phase 3: Validate and freeze
    print("\n--- Phase 3: Validation ---")
    print("\n  16b-evolved:")
    validate_and_freeze(best16, bits_list=[16, 20, 24], n_trials=10, time_limit=5.0)
    print("\n  18b-evolved:")
    validate_and_freeze(best18, bits_list=[16, 20, 24], n_trials=10, time_limit=5.0)
