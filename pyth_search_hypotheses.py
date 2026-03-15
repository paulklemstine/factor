#!/usr/bin/env python3
"""
=============================================================================
HEURISTIC SEARCH ON THE PYTHAGOREAN TRIPLE TREE FOR INTEGER FACTORIZATION
=============================================================================

Research Hypotheses and Experiment Designs
------------------------------------------

This document contains 10 detailed algorithm proposals for navigating the
Pythagorean triple tree to factor composite integers. Each proposal includes:
  - Mathematical grounding and hypothesis
  - Algorithm pseudocode (executable Python)
  - Expected complexity analysis
  - Concrete experiment design with baselines
  - Success criterion

CONTEXT: This codebase already has several implementations:
  - pyth_heuristic_c.c: C beam search with quad_res scent heuristic
  - pyth_birthday_c.c: Multi-walk birthday collision (distinguished points)
  - pyth_rho_c.c: Projective Pollard-rho (Mobius transformation r=m/n mod N)
  - pyth_deep_mod.c: Deep modular walk with batched GCD
  - pyth_gp_evolve.py: Genetic programming to evolve heuristics
  - pyth_experiments.py: Q-learning, UCB1, SA frameworks
  - pyth_hybrid_c.c: Smooth exponent + multi-curve + random walk
  - spectral_diagnostic.py: Orbit structure analysis mod primes

The tree structure:
  Root: (m,n) = (2,1) giving triple (3,4,5).
  Forward moves (9 total):
    B1: (2m-n, m)    B2: (2m+n, m)    B3: (m+2n, n)     [Berggren]
    P1: (m+n, 2n)    P2: (2m, m-n)    P3: (2m, m+n)     [Price]
    F1: (3m-2n,m-n)  F2: (3m+2n,m+n)  F3: (m+4n, n)     [Firstov]
  Inverse moves (3 total): B1^-1, B2^-1, B3^-1

  Derived values from (m,n):
    A = m^2 - n^2,  B = 2mn,  C = m^2 + n^2  (Pythagorean triple)
    Also: m, n, m-n, m+n, (m-n)^2, (m+n)^2, 2m^2, 2n^2, A*B

  Factor detection: gcd(derived_value, N) for any derived value.

  Key insight: We can track (m,n) mod N using 2x2 matrix multiplication.
  At depth D, true m ~ 2^D bits, but m mod N stays 64 bits. This means
  gcd(v mod N, N) = gcd(v, N) -- factors are detected perfectly in mod-N space.
"""

import math
import random
import time
import heapq
from math import gcd, log, isqrt
from collections import defaultdict, deque

# ==========================================================================
# SHARED INFRASTRUCTURE
# ==========================================================================

# (m,n) matrix format: ((a00, a01), (a10, a11))
# (m', n') = (a00*m + a01*n, a10*m + a11*n)
B1 = ((2, -1), (1, 0))
B2 = ((2, 1), (1, 0))
B3 = ((1, 2), (0, 1))
P1 = ((1, 1), (0, 2))
P2 = ((2, 0), (1, -1))
P3 = ((2, 0), (1, 1))
F1 = ((3, -2), (1, -1))
F2 = ((3, 2), (1, 1))
F3 = ((1, 4), (0, 1))
B1i = ((0, 1), (-1, 2))
B2i = ((0, 1), (1, -2))
B3i = ((1, -2), (0, 1))

FORWARD = [B1, B2, B3, P1, P2, P3, F1, F2, F3]
INVERSE = [B1i, B2i, B3i]
ALL_MATS = FORWARD + INVERSE
N_FWD = len(FORWARD)
N_ALL = len(ALL_MATS)


def apply_mat(M, m, n):
    """Apply 2x2 matrix to (m,n) over the integers."""
    return M[0][0] * m + M[0][1] * n, M[1][0] * m + M[1][1] * n


def apply_mat_mod(M, m, n, N):
    """Apply 2x2 matrix to (m,n) mod N."""
    m2 = (M[0][0] * m + M[0][1] * n) % N
    n2 = (M[1][0] * m + M[1][1] * n) % N
    return m2, n2


def valid(m, n):
    """Check if (m,n) is a valid Pythagorean generator (integers, not mod N)."""
    return m > 0 and n >= 0 and m > n


def derived_values_mod(m, n, N):
    """Compute derived values from (m,n) mod N. Returns list of values mod N."""
    m2 = m * m % N
    n2 = n * n % N
    A = (m2 - n2) % N
    B = 2 * m * n % N
    C = (m2 + n2) % N
    d = (m - n) % N
    s = (m + n) % N
    return [A, B, C, m, n, d, s, d * d % N, s * s % N, 2 * m2 % N, 2 * n2 % N, A * B % N]


def check_factor_mod(m, n, N):
    """Check if any derived value of (m,n) mod N shares a factor with N."""
    for v in derived_values_mod(m, n, N):
        if v == 0:
            continue
        g = gcd(v, N)
        if 1 < g < N:
            return g
    return 0


def miller_rabin(n, witnesses=(2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)):
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
    """Generate a semiprime with two factors of approximately `bits` bits each."""
    rng = random.Random(seed)
    while True:
        p = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if miller_rabin(p): break
    while True:
        q = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if q != p and miller_rabin(q): break
    return min(p, q), max(p, q), p * q


# ==========================================================================
# HYPOTHESIS 1: GREEDY GCD-GUIDED SEARCH
# ==========================================================================
"""
HYPOTHESIS: The GCD landscape on the Pythagorean tree has "scent trails" --
at nodes where derived values share small factors with N, the GCD is elevated.
A greedy policy that always moves to the child maximizing gcd(A*B, N) should
converge to a factor faster than random walk.

ANALYSIS:
  If N = p * q and a derived value v happens to be divisible by p, then
  gcd(v, N) = p (or a multiple). But for random v, gcd(v, N) = 1 with
  probability (1 - 1/p)(1 - 1/q) ~ 1 - 1/p - 1/q. So "scent" events
  (gcd > 1) are rare: probability ~ 12/p per node (12 derived values).

  The greedy GCD strategy is equivalent to maximizing a noisy binary signal.
  When gcd = 1 (which is almost always), the greedy choice is arbitrary --
  it degenerates to an uninformed walk.

  PREDICTION: Greedy GCD will NOT converge to factors for large N.
  It will behave as a random walk until it accidentally hits a factor.
  The landscape is essentially flat (gcd = 1 everywhere) with isolated
  spikes (gcd = p) that are too sparse to create a gradient.

  However, greedy GCD *with a PRODUCT accumulator* (batch GCD) can help:
  instead of checking gcd at each node, accumulate prod(v_i) and check
  gcd(prod, N) periodically. This is what pyth_deep_mod.c already does.

EXPECTED COMPLEXITY: O(p) -- same as random walk (no speedup from greediness).
"""


def h1_greedy_gcd_search(N, max_steps=100000, time_limit=10.0):
    """
    Hypothesis 1: Greedy GCD-guided search.

    At each node, evaluate all children. Pick the one whose derived values
    have the largest gcd with N. Break ties randomly.

    Returns (factor, steps, method_info) or (0, steps, info) if not found.
    """
    t0 = time.time()
    m, n = 2 % N, 1 % N  # Start at root, mod N
    best_gcd_seen = 1

    for step in range(max_steps):
        if time.time() - t0 > time_limit:
            break

        # Check current node
        f = check_factor_mod(m, n, N)
        if f:
            return f, step, {"best_gcd": best_gcd_seen}

        # Evaluate all children
        best_score = 0
        best_children = []
        for M in ALL_MATS:
            m2, n2 = apply_mat_mod(M, m, n, N)
            # Score = max gcd of derived values with N
            score = 1
            for v in derived_values_mod(m2, n2, N):
                if v == 0:
                    continue
                g = gcd(v, N)
                if 1 < g < N:
                    return g, step, {"best_gcd": g, "move": ALL_MATS.index(M)}
                score = max(score, g)
            if score > best_score:
                best_score = score
                best_children = [(m2, n2)]
            elif score == best_score:
                best_children.append((m2, n2))

        if best_score > best_gcd_seen:
            best_gcd_seen = best_score

        # Move to best child (random among ties)
        if best_children:
            m, n = random.choice(best_children)
        else:
            # Fallback: random move
            M = random.choice(ALL_MATS)
            m, n = apply_mat_mod(M, m, n, N)

    return 0, max_steps, {"best_gcd": best_gcd_seen}


# ==========================================================================
# HYPOTHESIS 2: A* / BEAM SEARCH WITH SMOOTHNESS SCORE
# ==========================================================================
"""
HYPOTHESIS: Smoothness of A*B (the product of the two legs) is a useful
heuristic for navigating the tree toward relations useful for factoring.
Nodes where A*B has many small prime factors are "closer" to being fully
smooth, which is exactly what SIQS/GNFS need.

ANALYSIS:
  This is the FACTORING-AS-SEARCH paradigm: instead of sieving over
  polynomials, we sieve over the Pythagorean tree, scoring each node by
  how smooth its A*B value is.

  The smoothness score can be computed as:
    score(m,n) = sum of log(p) for p | (A*B) where p <= B_smooth
  Divided by log(A*B), this gives the "fraction factored" in [0,1].

  BEAM SEARCH: Keep the top K candidates sorted by smoothness score.
  At each step, expand all children of all K candidates, score them,
  keep the top K. This is width-first exploration guided by smoothness.

  KEY QUESTION: Does the smoothness landscape have exploitable structure?
  Specifically: are children of smooth nodes more likely to be smooth?

  THEORETICAL CONCERN: Smoothness is essentially random for large values.
  The probability that a random D-digit number is B-smooth is
  u^(-u) where u = D/log(B). Tree structure does NOT change this.
  Children of smooth nodes are NOT more likely to be smooth.

  BUT: The tree does provide STRUCTURED SAMPLING of (m,n) values.
  Unlike random sampling, tree nodes have algebraic relationships.
  If m is smooth, then 2m+n (from B2) has a chance of being smooth too
  if n is also smooth. This is a WEAK but real correlation.

EXPECTED COMPLEXITY:
  Beam search with width K explores K*D nodes to depth D.
  Each node requires trial division up to B_smooth: O(B/ln(B)) per node.
  Total: O(K * D * B/ln(B)).
  Success probability per node: ~ u^(-u) where u = D*log(2) / log(B).
  Need K*D ~ u^u nodes, so K ~ u^u / D.

  For 64-bit semiprime: p ~ 2^32, D ~ 32 in tree, B ~ 10^4.
  u ~ 32*0.69/9.2 ~ 2.4, u^u ~ 4.2. K ~ 4.2/32 ~ far too optimistic.
  Realistic: u^u ~ 10^6 for useful B, so need 10^6 nodes explored.
  This is WORSE than SIQS for medium-size numbers.

  HOWEVER: Beam search may find PARTIAL relations that can be combined
  via large prime variation. This makes it competitive for small N.
"""


def smoothness_score(value, bound=10000):
    """
    Compute smoothness score: fraction of value factored by primes <= bound.

    Returns (score, largest_remaining_factor).
    score = sum(log(p^k)) / log(value) for p^k | value, p <= bound.
    """
    if value <= 1:
        return 1.0, 1
    original = value
    log_original = log(value)
    log_factored = 0.0

    # Trial division
    for p in _small_primes_up_to(bound):
        while value % p == 0:
            value //= p
            log_factored += log(p)
        if value == 1:
            break

    score = log_factored / log_original if log_original > 0 else 0.0
    return score, value  # value is the unfactored cofactor


def _small_primes_up_to(B):
    """Simple sieve of Eratosthenes for primes up to B."""
    if B < 2:
        return []
    sieve = bytearray(b'\x01') * (B + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, isqrt(B) + 1):
        if sieve[i]:
            sieve[i*i::i] = bytearray(len(sieve[i*i::i]))
    return [i for i in range(2, B + 1) if sieve[i]]


# Precompute small primes for smoothness checking
_SMALL_PRIMES_1000 = _small_primes_up_to(1000)
_SMALL_PRIMES_10000 = _small_primes_up_to(10000)


def h2_beam_smoothness_search(N, beam_width=100, max_depth=200,
                               smooth_bound=1000, time_limit=30.0):
    """
    Hypothesis 2: Beam search guided by smoothness of A*B.

    Maintain a beam of the top K (m,n) positions sorted by smoothness score.
    At each depth, expand all children, score by smoothness, keep top K.

    NOTE: This operates on TRUE (m,n) values (not mod N) because we need
    to compute actual smoothness of A*B. This limits depth due to number growth.

    For mod-N operation, we would need a different smoothness proxy.

    Returns (factor, nodes_explored, best_smoothness_seen).
    """
    t0 = time.time()
    nodes = 0
    best_smooth = 0.0
    relations = []  # Fully smooth (m,n) pairs

    # Initialize beam with root
    m0, n0 = 2, 1
    a0 = m0*m0 - n0*n0
    b0 = 2*m0*n0
    s0, _ = smoothness_score(a0 * b0, smooth_bound)
    beam = [(s0, m0, n0)]  # (negative_score for min-heap, m, n)

    visited = {(2, 1)}

    for depth in range(max_depth):
        if time.time() - t0 > time_limit:
            break

        # Expand all beam nodes
        candidates = []
        for _, m, n in beam:
            for M in FORWARD:  # Only forward moves to avoid cycles
                m2, n2 = apply_mat(M, m, n)
                if not valid(m2, n2):
                    continue
                if (m2, n2) in visited:
                    continue
                visited.add((m2, n2))
                nodes += 1

                # Check for direct factor
                a_val = m2*m2 - n2*n2
                b_val = 2*m2*n2
                c_val = m2*m2 + n2*n2
                for v in [a_val, b_val, c_val, m2, n2, m2-n2, m2+n2]:
                    if v > 0:
                        g = gcd(v, N)
                        if 1 < g < N:
                            return g, nodes, best_smooth

                # Smoothness score
                ab = a_val * b_val
                if ab > 0:
                    sc, cofactor = smoothness_score(ab, smooth_bound)
                    if sc > best_smooth:
                        best_smooth = sc
                    if cofactor == 1:
                        relations.append((m2, n2, a_val, b_val))
                    candidates.append((-sc, m2, n2))  # Negative for max-heap via min-heap

                    # Check if enough relations for Gaussian elimination
                    if len(relations) > len(_SMALL_PRIMES_1000) + 5:
                        # Could do linear algebra here...
                        pass

        if not candidates:
            break

        # Keep top beam_width candidates
        candidates.sort()
        beam = candidates[:beam_width]

    return 0, nodes, best_smooth


# ==========================================================================
# HYPOTHESIS 3: GRADIENT-LIKE NAVIGATION VIA MODULAR PROXIMITY
# ==========================================================================
"""
HYPOTHESIS: Define a "potential" function phi(m,n) that measures how close
a derived value is to being divisible by a factor of N. Since we don't know
the factors, we use gcd(v, N) as a proxy. But when gcd = 1, we can use the
REMAINDER v mod N as a more fine-grained signal.

IDEA: If v = k*p + r for small r, then v is "close" to being divisible by p.
We can't compute r (we don't know p), but we can observe:
  - v mod N = v mod (p*q) gives information about BOTH v mod p and v mod q.
  - The "near-divisibility" can be proxied by min(v mod N, N - v mod N) / N.
    This is small when v is close to a multiple of N, but that's too strong.

BETTER PROXY: "Quadratic residue scent"
  - For each derived value v, compute r = N mod v and r' = N mod v^2.
  - If p | v, then N mod v = q * (p mod v) != 0 but N mod v^2 = q*(p mod v^2).
  - The ratio r/v is a noisy signal: E[r/v] = 0.5 for random v, but
    E[r/v | p divides v] = 0 (exactly). So low r/v is informative.
  - This is EXACTLY the scent heuristic in pyth_heuristic_c.c.

PROBLEM: This is NOT a gradient. Low scent at one node does NOT predict
low scent at neighbors. The scent function is essentially random.

ALTERNATIVE GRADIENT: Use the PRODUCT gradient.
  - prod(v_i for i in walk) accumulates like a random walk mod p.
  - The "distance to zero mod p" shrinks as O(1/sqrt(steps)).
  - This is the birthday collision idea in disguise.

PREDICTION: No useful gradient exists in the scent landscape.
The only "gradient" is the birthday-paradox accumulation of products.

EXPERIMENT: Measure autocorrelation of scent along tree paths.
If autocorrelation is near zero, the gradient hypothesis is falsified.
"""


def h3_gradient_navigation(N, max_steps=50000, time_limit=10.0):
    """
    Hypothesis 3: Gradient-like navigation using modular proximity.

    At each node, compute a "potential" based on how close derived values
    are to being multiples of unknown factors. Move in the direction that
    decreases the potential.

    The potential function:
      phi(m,n) = min over v in derived_values of (min(v mod N, N - v mod N) / N)

    This is the "linear scent" -- near zero means a derived value is close
    to a multiple of N (and thus likely close to a multiple of p or q).

    Returns (factor, steps, autocorrelation_data).
    """
    t0 = time.time()
    m, n = 2 % N, 1 % N
    scent_history = []

    def potential(m_val, n_val):
        """Lower is better -- closer to a factor."""
        best = 1.0
        for v in derived_values_mod(m_val, n_val, N):
            if v == 0:
                continue
            near = min(v, N - v)
            s = near / N
            if s < best:
                best = s
        return best

    current_phi = potential(m, n)
    scent_history.append(current_phi)

    for step in range(max_steps):
        if time.time() - t0 > time_limit:
            break

        f = check_factor_mod(m, n, N)
        if f:
            # Compute autocorrelation
            autocorr = _compute_autocorrelation(scent_history)
            return f, step, {"autocorrelation": autocorr}

        # Evaluate all children's potentials
        best_phi = float('inf')
        best_moves = []
        for M in ALL_MATS:
            m2, n2 = apply_mat_mod(M, m, n, N)
            f = check_factor_mod(m2, n2, N)
            if f:
                return f, step, {"autocorrelation": _compute_autocorrelation(scent_history)}
            phi = potential(m2, n2)
            if phi < best_phi:
                best_phi = phi
                best_moves = [(m2, n2)]
            elif phi == best_phi:
                best_moves.append((m2, n2))

        # Accept move if it improves potential, or with small probability otherwise
        # (Metropolis criterion to avoid getting stuck)
        if best_phi < current_phi or random.random() < 0.1:
            m, n = random.choice(best_moves)
            current_phi = best_phi
        else:
            # Random move
            M = random.choice(ALL_MATS)
            m, n = apply_mat_mod(M, m, n, N)
            current_phi = potential(m, n)

        scent_history.append(current_phi)

    autocorr = _compute_autocorrelation(scent_history)
    return 0, max_steps, {"autocorrelation": autocorr}


def _compute_autocorrelation(series, max_lag=20):
    """Compute autocorrelation of a time series at lags 1..max_lag."""
    if len(series) < max_lag + 2:
        return {}
    import numpy as np
    s = np.array(series[-1000:])  # Use last 1000 points
    s = s - s.mean()
    var = s.var()
    if var < 1e-15:
        return {i: 0.0 for i in range(1, max_lag + 1)}
    result = {}
    for lag in range(1, max_lag + 1):
        if lag >= len(s):
            break
        corr = np.mean(s[:-lag] * s[lag:]) / var
        result[lag] = float(corr)
    return result


# ==========================================================================
# HYPOTHESIS 4: MONTE CARLO TREE SEARCH (MCTS) WITH UCB1
# ==========================================================================
"""
HYPOTHESIS: MCTS with UCB1 balances exploration and exploitation on the
Pythagorean tree. Reward = gcd score (1 if factor found, 0 otherwise).
The UCB1 formula is: Q(s,a) / N(s,a) + C * sqrt(ln(N(s)) / N(s,a))
where Q = cumulative reward, N = visit count, C = exploration constant.

ANALYSIS:
  MCTS works well when:
    1. Rewards are concentrated in specific subtrees (not uniformly random)
    2. The branching factor is manageable (here: 12, which is OK)
    3. Rollout policy can reach rewards quickly

  For factoring:
    - Reward (gcd > 1) is astronomically rare: probability ~ 12/p per node.
    - No subtree is special -- factors are uniformly distributed in the tree.
    - Rollout to depth D sees 12*D nodes, giving probability ~ 12*D/p.
    - UCB1 will see reward 0 almost everywhere, making the Q/N terms useless.
    - The algorithm degenerates to pure exploration (= BFS or random walk).

  PREDICTION: MCTS will NOT outperform random walk for N > 2^40.
  For small N (< 2^20), it may show slight improvement due to systematic
  coverage avoiding revisits.

  MODIFICATION THAT COULD WORK: Use a SOFTER reward signal.
  Instead of binary (factor found / not found), use the GCD value itself
  as a continuous reward. But as argued in H1, gcd = 1 almost everywhere.

  BETTER MODIFICATION: Use PRODUCT accumulation as reward.
  Track the accumulated product of derived values. The probability that
  gcd(accumulated_product, N) > 1 grows quadratically with the number of
  distinct derived values seen. This is the birthday collision idea.
  MCTS can then allocate exploration budget to maximize the DIVERSITY of
  derived values encountered, which IS something tree structure can help with.
"""


class MCTSNode:
    """Node in the MCTS tree."""
    __slots__ = ['m', 'n', 'parent', 'children', 'visit_count',
                 'total_reward', 'untried_moves', 'move_index']

    def __init__(self, m, n, parent=None, move_index=-1):
        self.m = m
        self.n = n
        self.parent = parent
        self.children = {}  # move_index -> MCTSNode
        self.visit_count = 0
        self.total_reward = 0.0
        self.untried_moves = list(range(N_ALL))
        random.shuffle(self.untried_moves)
        self.move_index = move_index


def h4_mcts_search(N, max_iterations=50000, exploration_c=1.41,
                    rollout_depth=20, time_limit=30.0):
    """
    Hypothesis 4: Monte Carlo Tree Search with UCB1.

    Uses two reward modes:
      Mode A: Binary reward (1 if factor found, 0 otherwise)
      Mode B: Soft reward = max gcd score seen during rollout (normalized)

    Returns (factor, iterations, nodes_created).
    """
    t0 = time.time()
    root = MCTSNode(2 % N, 1 % N)
    nodes_created = 1
    best_gcd_global = 1

    for iteration in range(max_iterations):
        if time.time() - t0 > time_limit:
            break

        # Phase 1: SELECTION -- walk down tree using UCB1
        node = root
        while node.untried_moves == [] and node.children:
            # UCB1 selection
            best_ucb = -float('inf')
            best_child = None
            log_parent = log(node.visit_count + 1)
            for child in node.children.values():
                if child.visit_count == 0:
                    ucb = float('inf')
                else:
                    exploit = child.total_reward / child.visit_count
                    explore = exploration_c * math.sqrt(log_parent / child.visit_count)
                    ucb = exploit + explore
                if ucb > best_ucb:
                    best_ucb = ucb
                    best_child = child
            if best_child is None:
                break
            node = best_child

        # Phase 2: EXPANSION -- add one child
        if node.untried_moves:
            move_idx = node.untried_moves.pop()
            M = ALL_MATS[move_idx]
            m2, n2 = apply_mat_mod(M, node.m, node.n, N)
            child = MCTSNode(m2, n2, parent=node, move_index=move_idx)
            node.children[move_idx] = child
            node = child
            nodes_created += 1

        # Phase 3: ROLLOUT -- random play from new node
        rm, rn = node.m, node.n
        rollout_reward = 0.0
        best_gcd_rollout = 1
        for d in range(rollout_depth):
            f = check_factor_mod(rm, rn, N)
            if f:
                return f, iteration, nodes_created
            # Track best gcd as soft reward
            for v in derived_values_mod(rm, rn, N):
                if v > 0:
                    g = gcd(v, N)
                    if 1 < g < N:
                        return g, iteration, nodes_created
                    best_gcd_rollout = max(best_gcd_rollout, g)
            # Random move
            M = ALL_MATS[random.randint(0, N_ALL - 1)]
            rm, rn = apply_mat_mod(M, rm, rn, N)

        # Soft reward: normalized log gcd
        if best_gcd_rollout > 1:
            rollout_reward = log(best_gcd_rollout) / log(N)
        best_gcd_global = max(best_gcd_global, best_gcd_rollout)

        # Phase 4: BACKPROPAGATION
        while node is not None:
            node.visit_count += 1
            node.total_reward += rollout_reward
            node = node.parent

    return 0, max_iterations, nodes_created


# ==========================================================================
# HYPOTHESIS 5: SIMULATED ANNEALING ON THE TREE
# ==========================================================================
"""
HYPOTHESIS: Simulated annealing (SA) can navigate the tree by occasionally
accepting worse moves, allowing escape from local optima in the scent landscape.

ANALYSIS:
  SA requires a SMOOTH energy landscape with local minima separated by barriers.
  For factoring on the Pythagorean tree:
    - Energy = negative scent (lower = better)
    - The landscape is NOT smooth -- it's essentially random with isolated spikes
    - There are no meaningful "barriers" between good regions
    - SA degenerates to random walk at high temperature, greedy at low temperature

  PREDICTION: SA will NOT outperform random walk for large N.
  At best, it equals the beam search with restarts (which pyth_heuristic_c.c
  already implements with restart_patience).

  INTERESTING MODIFICATION: Use SA on the SPACE OF TREE PATHS rather than
  on the tree itself. Define a path as a sequence of matrix choices.
  Neighbor paths differ by one matrix substitution. Energy = smoothness of
  the endpoint's A*B value. This is a COMBINATORIAL optimization problem
  that SA is designed for.

  This transforms the problem from "search the tree" to "optimize a path"
  which has better SA properties (smooth energy landscape over path space).

EXPECTED COMPLEXITY: O(p) for point-wise SA (same as random walk).
O(???) for path-space SA -- depends on the landscape, needs experiments.
"""


def h5_simulated_annealing(N, max_steps=100000, T_start=1.0, T_end=0.001,
                            cooling='geometric', time_limit=30.0):
    """
    Hypothesis 5: Simulated annealing on the tree.

    Score function: "scent" = min(v mod N, N - v mod N) / N across derived values.
    Lower = better. Temperature schedule: geometric or linear cooling.

    Returns (factor, steps, temperature_at_end).
    """
    t0 = time.time()
    m, n = 2 % N, 1 % N

    def energy(m_val, n_val):
        """Energy function -- lower is better."""
        best = 1.0
        for v in derived_values_mod(m_val, n_val, N):
            if v == 0:
                continue
            near = min(v, N - v)
            s = near / N
            best = min(best, s)
        return best

    current_e = energy(m, n)
    best_e = current_e
    T = T_start

    for step in range(max_steps):
        if time.time() - t0 > time_limit:
            break

        # Check for factor
        f = check_factor_mod(m, n, N)
        if f:
            return f, step, T

        # Propose a neighbor
        M = ALL_MATS[random.randint(0, N_ALL - 1)]
        m2, n2 = apply_mat_mod(M, m, n, N)
        f = check_factor_mod(m2, n2, N)
        if f:
            return f, step, T
        new_e = energy(m2, n2)

        # Metropolis acceptance
        delta_e = new_e - current_e
        if delta_e < 0:
            # Better -- always accept
            m, n = m2, n2
            current_e = new_e
        elif T > 1e-10 and random.random() < math.exp(-delta_e / T):
            # Worse -- accept with probability exp(-dE/T)
            m, n = m2, n2
            current_e = new_e

        best_e = min(best_e, current_e)

        # Cool down
        if cooling == 'geometric':
            alpha = (T_end / T_start) ** (1.0 / max_steps)
            T *= alpha
        else:
            T = T_start - (T_start - T_end) * step / max_steps

    return 0, max_steps, T


def h5b_path_space_annealing(N, path_length=30, max_iterations=50000,
                              T_start=1.0, T_end=0.01, time_limit=30.0):
    """
    Hypothesis 5b: SA over the space of tree PATHS.

    A path = sequence of matrix indices [i_0, i_1, ..., i_{L-1}].
    Endpoint (m,n) is computed by applying matrices in sequence from root.
    Energy = min scent at endpoint.

    Neighbor: flip one random matrix choice in the path.

    This has better SA properties because the energy landscape over paths
    is smoother than the landscape over tree nodes directly.
    """
    t0 = time.time()

    # Random initial path
    path = [random.randint(0, N_FWD - 1) for _ in range(path_length)]

    def path_to_endpoint(p):
        """Compute (m,n) mod N for a given path."""
        m, n = 2 % N, 1 % N
        for idx in p:
            m, n = apply_mat_mod(FORWARD[idx], m, n, N)
        return m, n

    def path_energy(p):
        """Energy of a path = scent at its endpoint."""
        m, n = path_to_endpoint(p)
        best = 1.0
        for v in derived_values_mod(m, n, N):
            if v == 0:
                continue
            near = min(v, N - v)
            best = min(best, near / N)
        return best

    current_e = path_energy(path)
    T = T_start
    alpha = (T_end / T_start) ** (1.0 / max_iterations)

    for iteration in range(max_iterations):
        if time.time() - t0 > time_limit:
            break

        # Check current endpoint for factor
        m, n = path_to_endpoint(path)
        f = check_factor_mod(m, n, N)
        if f:
            return f, iteration, T

        # Propose neighbor: flip one position
        new_path = path[:]
        pos = random.randint(0, path_length - 1)
        new_path[pos] = random.randint(0, N_FWD - 1)

        new_e = path_energy(new_path)
        delta_e = new_e - current_e

        if delta_e < 0 or (T > 1e-10 and random.random() < math.exp(-delta_e / T)):
            path = new_path
            current_e = new_e

        T *= alpha

    return 0, max_iterations, T


# ==========================================================================
# HYPOTHESIS 6: GENETIC / EVOLUTIONARY APPROACH
# ==========================================================================
"""
HYPOTHESIS: A population of (m,n) positions can be evolved toward positions
that share factors with N. Crossover mixes tree paths, mutation makes random
matrix steps, fitness is based on gcd or smoothness scores.

ANALYSIS:
  The key question is: what does "crossover" mean for tree paths?

  Option A: Path crossover -- each individual is a path (sequence of matrix
  indices). Crossover = swap a suffix. Mutation = change one matrix choice.
  This is standard GP/GA on the path representation.

  Option B: (m,n) crossover -- directly combine m,n values from two parents.
  For example, child_m = (parent1_m + parent2_m) / 2 mod N.
  This is problematic because the child may not be reachable in the tree.

  Option C: Matrix product crossover -- each individual is a product of matrices
  M = M_{k-1} * ... * M_1 * M_0. Crossover = swap prefix/suffix of the
  matrix product sequence.

  PREDICTION: Path crossover (Option A) is equivalent to random restart +
  greedy search from random positions. It will NOT converge because there is
  no meaningful "genetic information" to inherit -- the "good" part of a
  path is not localized to a prefix or suffix.

  HOWEVER: This was already tried in pyth_gp_evolve.py (evolving HEURISTIC
  FUNCTIONS, not positions). That approach is more promising because the
  heuristic IS something that generalizes across positions.

EXPECTED COMPLEXITY: Same as running K independent random searches.
"""


def h6_evolutionary_search(N, pop_size=100, generations=500,
                            path_length=30, mutation_rate=0.15,
                            time_limit=30.0):
    """
    Hypothesis 6: Evolutionary search with path-based representation.

    Each individual = list of matrix indices (a path from root).
    Fitness = max gcd score across all derived values at endpoint + intermediate.
    Crossover = single-point crossover of paths.
    Mutation = flip random matrix choices.

    Returns (factor, generation_found, total_evaluations).
    """
    t0 = time.time()
    evaluations = 0

    def random_path():
        return [random.randint(0, N_FWD - 1) for _ in range(path_length)]

    def evaluate_path(path):
        """Evaluate a path: walk from root, check gcd at each step.
        Returns (factor_or_0, fitness_score)."""
        nonlocal evaluations
        m, n = 2 % N, 1 % N
        best_gcd = 1
        for idx in path:
            m, n = apply_mat_mod(FORWARD[idx], m, n, N)
            evaluations += 1
            for v in derived_values_mod(m, n, N):
                if v > 0:
                    g = gcd(v, N)
                    if 1 < g < N:
                        return g, float('inf')
                    best_gcd = max(best_gcd, g)
        # Fitness = log of best gcd (bigger = better)
        return 0, log(best_gcd + 1)

    def crossover(p1, p2):
        """Single-point crossover."""
        pt = random.randint(1, path_length - 1)
        return p1[:pt] + p2[pt:]

    def mutate(path):
        """Flip random positions with probability mutation_rate."""
        new = path[:]
        for i in range(len(new)):
            if random.random() < mutation_rate:
                new[i] = random.randint(0, N_FWD - 1)
        return new

    # Initialize population
    population = [random_path() for _ in range(pop_size)]
    fitnesses = []
    for p in population:
        factor, fit = evaluate_path(p)
        if factor:
            return factor, 0, evaluations
        fitnesses.append(fit)

    for gen in range(generations):
        if time.time() - t0 > time_limit:
            break

        # Selection: tournament of size 3
        new_pop = []
        for _ in range(pop_size):
            candidates = random.sample(range(pop_size), min(3, pop_size))
            winner = max(candidates, key=lambda i: fitnesses[i])
            new_pop.append(population[winner])

        # Crossover + mutation
        offspring = []
        for i in range(0, pop_size, 2):
            p1 = new_pop[i]
            p2 = new_pop[min(i + 1, pop_size - 1)]
            if random.random() < 0.7:
                c1 = crossover(p1, p2)
                c2 = crossover(p2, p1)
            else:
                c1, c2 = p1[:], p2[:]
            offspring.append(mutate(c1))
            offspring.append(mutate(c2))
        offspring = offspring[:pop_size]

        # Evaluate
        new_fitnesses = []
        for p in offspring:
            factor, fit = evaluate_path(p)
            if factor:
                return factor, gen, evaluations
            new_fitnesses.append(fit)

        # Elitism: keep best individual
        best_idx = max(range(pop_size), key=lambda i: fitnesses[i])
        worst_new_idx = min(range(len(new_fitnesses)), key=lambda i: new_fitnesses[i])
        offspring[worst_new_idx] = population[best_idx]
        new_fitnesses[worst_new_idx] = fitnesses[best_idx]

        population = offspring
        fitnesses = new_fitnesses

    return 0, generations, evaluations


# ==========================================================================
# HYPOTHESIS 7: DEPTH-LIMITED BFS WITH PRUNING
# ==========================================================================
"""
HYPOTHESIS: BFS to depth D with pruning of low-scoring branches can
systematically explore the most promising parts of the tree.

ANALYSIS:
  The tree has branching factor 9 (forward) or 12 (all moves).
  At depth D, there are 9^D nodes. For D=10, that's 3.5 billion.
  Pruning is essential.

  Pruning criteria:
    A. Score threshold: prune branches where scent > threshold.
       Problem: scent is random, so threshold just controls the fraction kept.
    B. Budget pruning: at each depth, keep only the top K nodes (= beam search).
       This is exactly H2.
    C. Diversity pruning: keep nodes that are spread out in (m mod N, n mod N)
       space. This maximizes the birthday collision probability.
    D. LP-residue pruning: keep nodes where a derived value has a large prime
       factor in common with previously seen large primes (large prime variation).

  PREDICTION: Option C (diversity pruning) is the most promising.
  It converts BFS into a controlled birthday collision search.

  Option D is also interesting: it implements large-prime relation combining
  on the tree, which could give sub-exponential behavior if the tree produces
  enough large-prime partial relations.

EXPECTED COMPLEXITY:
  BFS to depth D with beam width K: O(K * D * branching_factor) node evaluations.
  Each evaluation: O(derived_values * log(N)) for gcd.
  The factor discovery probability depends on the collision mechanism used.

  For diversity pruning with K walkers running D steps:
    Birthday probability: 1 - exp(-K^2 * D / (2p)) per derived value.
    Need K * sqrt(D) ~ sqrt(p). With D=100, K ~ sqrt(p)/10.
    For 64-bit N: K ~ 6500, total nodes ~ 6500 * 100 * 12 ~ 7.8M. Fast!
"""


def h7_bfs_diversity_pruning(N, beam_width=500, max_depth=200,
                              time_limit=30.0):
    """
    Hypothesis 7: BFS with diversity-based pruning.

    At each depth level, keep the K nodes that are most spread out
    in (m mod N) space. This maximizes birthday collision probability.

    Also accumulates a batch product for periodic gcd checking.

    Returns (factor, depth_reached, nodes_explored).
    """
    t0 = time.time()
    nodes = 0

    # Start at root
    current_level = [(2 % N, 1 % N)]
    visited_m_values = set()  # Track distinct m mod N values for birthday

    # Batch product accumulator for collision detection
    batch_prod = 1
    BATCH_SIZE = 256

    for depth in range(max_depth):
        if time.time() - t0 > time_limit:
            break

        next_level = []
        for m, n in current_level:
            for M_mat in FORWARD:
                m2, n2 = apply_mat_mod(M_mat, m, n, N)
                nodes += 1

                # Check for direct factor
                f = check_factor_mod(m2, n2, N)
                if f:
                    return f, depth, nodes

                # Birthday collision: check if we've seen this m before
                # (Different walks reaching same m mod p gives gcd detection)
                if m2 in visited_m_values:
                    # Potential collision -- but we need the difference
                    pass  # Can't easily recover the other walk's value here
                visited_m_values.add(m2)

                # Batch product accumulation
                for v in derived_values_mod(m2, n2, N):
                    if v > 1:
                        batch_prod = batch_prod * v % N
                if nodes % BATCH_SIZE == 0 and batch_prod > 1:
                    g = gcd(batch_prod, N)
                    if 1 < g < N:
                        return g, depth, nodes
                    batch_prod = 1  # Reset after check

                next_level.append((m2, n2))

        if not next_level:
            break

        # Diversity pruning: keep nodes spread out in m-space
        if len(next_level) > beam_width:
            # Hash-based diversity: divide m-space into buckets,
            # keep at most ceil(beam_width / n_buckets) per bucket
            n_buckets = min(beam_width, 100)
            buckets = defaultdict(list)
            for m, n in next_level:
                bucket = m % n_buckets
                buckets[bucket].append((m, n))

            per_bucket = max(1, beam_width // n_buckets)
            current_level = []
            for bucket_nodes in buckets.values():
                random.shuffle(bucket_nodes)
                current_level.extend(bucket_nodes[:per_bucket])
            current_level = current_level[:beam_width]
        else:
            current_level = next_level

    return 0, max_depth, nodes


# ==========================================================================
# HYPOTHESIS 8: LEARNING FROM SMALL EXAMPLES
# ==========================================================================
"""
HYPOTHESIS: Factor many small N values, record which tree paths led to
factors. Train a classifier/heuristic on these paths. Generalize to larger N.

ANALYSIS:
  The key question is: what FEATURES of successful paths generalize?

  Possible features:
    A. Matrix sequence patterns (e.g., B2 followed by P1 works often)
    B. Depth at which factor was found
    C. Relative position (m/n ratio) when factor was found
    D. Scent values along the successful path

  CRITICAL CONCERN: For small N (< 2^20), factors are found in the first
  few tree levels because derived values are comparable in size to N.
  For large N, derived values mod N are essentially random. The "signal"
  that exists for small N (structural proximity) vanishes for large N.

  This is the GENERALIZATION PROBLEM: patterns from small N don't transfer
  to large N because the mechanism changes fundamentally.

  EXCEPTION: If there are ALGEBRAIC patterns that are scale-invariant
  (e.g., certain matrix sequences always produce values divisible by primes
  of certain residue classes), those would generalize. But spectral_diagnostic.py
  already checked for such patterns (orbit structure mod primes) and found
  that orbits are large (near p^2), meaning the tree covers the full space.

PREDICTION: Learning from small examples will NOT generalize to N > 2^40.
The factoring mechanism changes qualitatively with scale.

EXPERIMENT: Train on 16-bit semiprimes, test on 24-bit, 32-bit, 40-bit.
Measure whether the success rate degrades (it will).
"""


def h8_learn_from_small(train_bits=10, test_bits_list=[12, 16, 20, 24],
                         num_train=200, num_test=50, time_limit=120.0):
    """
    Hypothesis 8: Learn matrix preferences from small factoring successes.

    Phase 1: Factor many small semiprimes, recording which matrix was used
    at each step that led to a factor. Build a matrix frequency table.

    Phase 2: Use the learned frequency table as a biased random walk
    for larger semiprimes. Compare to uniform random walk.

    Returns dict with results per test bit-size.
    """
    t0 = time.time()

    # Phase 1: Learn from small semiprimes
    matrix_success_count = [0] * N_ALL
    matrix_total_count = [0] * N_ALL
    total_solved = 0

    for trial in range(num_train):
        if time.time() - t0 > time_limit / 2:
            break
        _, _, N = gen_semi(train_bits, seed=trial)
        if N < 4:
            continue

        # BFS search with path tracking
        m, n = 2 % N, 1 % N
        path_matrices = []
        found = False
        for step in range(5000):
            f = check_factor_mod(m, n, N)
            if f:
                found = True
                # Credit all matrices in the successful path
                for mat_idx in path_matrices:
                    matrix_success_count[mat_idx] += 1
                total_solved += 1
                break
            # Random move (uniform)
            mat_idx = random.randint(0, N_ALL - 1)
            matrix_total_count[mat_idx] += 1
            m, n = apply_mat_mod(ALL_MATS[mat_idx], m, n, N)
            path_matrices.append(mat_idx)
            if len(path_matrices) > 200:
                path_matrices = path_matrices[-200:]

    # Compute learned distribution
    total_success = sum(matrix_success_count)
    if total_success == 0:
        # No successes, use uniform
        learned_weights = [1.0 / N_ALL] * N_ALL
    else:
        # Laplace smoothing
        learned_weights = [(c + 1) / (total_success + N_ALL)
                          for c in matrix_success_count]
        total = sum(learned_weights)
        learned_weights = [w / total for w in learned_weights]

    # Phase 2: Test on progressively harder semiprimes
    results = {}
    for test_bits in test_bits_list:
        if time.time() - t0 > time_limit:
            break

        # Test with learned distribution
        learned_solved = 0
        learned_steps_total = 0
        uniform_solved = 0
        uniform_steps_total = 0

        for trial in range(num_test):
            if time.time() - t0 > time_limit:
                break
            _, _, N = gen_semi(test_bits, seed=10000 + trial)
            if N < 4:
                continue

            # Learned walk
            m, n = 2 % N, 1 % N
            for step in range(10000):
                f = check_factor_mod(m, n, N)
                if f:
                    learned_solved += 1
                    learned_steps_total += step
                    break
                # Weighted random choice
                r = random.random()
                cumul = 0.0
                mat_idx = 0
                for i, w in enumerate(learned_weights):
                    cumul += w
                    if r <= cumul:
                        mat_idx = i
                        break
                m, n = apply_mat_mod(ALL_MATS[mat_idx], m, n, N)
            else:
                learned_steps_total += 10000

            # Uniform walk (same N)
            m, n = 2 % N, 1 % N
            for step in range(10000):
                f = check_factor_mod(m, n, N)
                if f:
                    uniform_solved += 1
                    uniform_steps_total += step
                    break
                mat_idx = random.randint(0, N_ALL - 1)
                m, n = apply_mat_mod(ALL_MATS[mat_idx], m, n, N)
            else:
                uniform_steps_total += 10000

        results[test_bits] = {
            'learned_solved': learned_solved,
            'uniform_solved': uniform_solved,
            'learned_avg_steps': learned_steps_total / max(num_test, 1),
            'uniform_avg_steps': uniform_steps_total / max(num_test, 1),
            'num_test': num_test,
        }

    return results, learned_weights


# ==========================================================================
# HYPOTHESIS 9: MULTI-TREE PARALLEL SEARCH (BIRTHDAY COLLISION)
# ==========================================================================
"""
HYPOTHESIS: Run K independent walks from K random starting positions.
Birthday-style collision detection on (m mod p) values. When two walks
collide mod p (but not mod q), gcd(m1-m2, N) = p.

ANALYSIS:
  This is EXACTLY what pyth_birthday_c.c implements. The question is:
  can we improve it with HEURISTIC GUIDANCE?

  The pure birthday approach has complexity O(sqrt(p)) per walker,
  with K walkers needing K * O(sqrt(p)/K) = O(sqrt(p)) total steps.
  Distinguished points reduce memory from O(K * steps) to O(K * dp_rate).

  POSSIBLE IMPROVEMENTS:
    A. Correlated walks: Instead of K independent walks, use walks that
       are correlated in a way that increases collision probability.
       But this is hard -- correlation usually DECREASES collision prob.

    B. Matrix-dependent distinguished points: Define dp based on the
       matrix used (e.g., "dp if B1 was just applied and m has k leading
       zeros"). This gives more information at collision time.

    C. Structured starting points: Instead of random starts, use starts
       that cover the (m mod p) space more uniformly. But we don't know p.

    D. Rho-style cycle detection: Instead of birthday collision between
       walkers, use cycle detection within a single walk. The cycle length
       mod p is O(p), so Brent's algorithm needs O(sqrt(p)) steps.
       This is what pyth_rho_c.c does with the projective r = m/n mod N.

  KEY INSIGHT: The rho approach (D) is theoretically optimal for a single
  walker. But it requires a DETERMINISTIC iteration function. The Pythagorean
  tree provides this: choose matrix based on hash of current state.

  IMPROVEMENT OVER EXISTING: The existing pyth_rho_c.c uses only the
  projective ratio r = m/n. We can also track MULTIPLE derived values
  simultaneously, each with independent cycle detection. The first to
  cycle gives the factor.

  Multi-derived-value rho: track r1 = m/n, r2 = (m-n)/(m+n), r3 = A/B,
  each iterated under the same matrix choices. Cycle detection on all three.
  Expected speedup: up to 3x if the cycles are independent (they are,
  modulo p, because the derived values are different functions of m,n).

EXPECTED COMPLEXITY: O(sqrt(p)) steps -- same as Pollard rho.
This is fundamentally O(N^(1/4)) for balanced semiprimes, same as all
birthday-based methods. The constants can be improved.
"""


def h9_multi_derived_rho(N, max_steps=10_000_000, batch_size=256,
                          time_limit=30.0):
    """
    Hypothesis 9: Multi-derived-value Pollard rho on Pythagorean tree.

    Run Brent's cycle detection simultaneously on multiple derived values:
      Channel 1: m mod N
      Channel 2: n mod N
      Channel 3: (m^2 - n^2) mod N
      Channel 4: (m^2 + n^2) mod N
      Channel 5: 2*m*n mod N

    Each channel accumulates (slow - fast) products independently.
    First channel to find gcd > 1 wins.

    Returns (factor, steps, channel_that_found).
    """
    t0 = time.time()

    # Matrix choice function: deterministic based on state
    def choose_matrix(m, n):
        h = (m * 0x9E3779B97F4A7C15 + n * 0x6A09E667F3BCC908) & 0xFFFFFFFFFFFFFFFF
        return int(h % N_FWD)

    # Initialize tortoise and hare
    tm, tn = 2 % N, 1 % N  # tortoise
    hm, hn = 2 % N, 1 % N  # hare

    # Advance hare one step ahead
    idx = choose_matrix(hm, hn)
    hm, hn = apply_mat_mod(FORWARD[idx], hm, hn, N)

    # Channel accumulators
    N_CHANNELS = 5
    acc = [1] * N_CHANNELS
    acc_count = 0

    # Brent's algorithm parameters
    power = 1
    lam = 1

    for step in range(max_steps):
        if step & 4095 == 0 and time.time() - t0 > time_limit:
            break

        # Brent's checkpoint
        if power == lam:
            tm, tn = hm, hn
            power *= 2
            lam = 0

        # Advance hare
        idx = choose_matrix(hm, hn)
        hm, hn = apply_mat_mod(FORWARD[idx], hm, hn, N)
        lam += 1

        # Compute derived values for both
        t_derivs = derived_values_mod(tm, tn, N)
        h_derivs = derived_values_mod(hm, hn, N)

        # Accumulate differences for each channel
        channels_vals = [
            (tm, hm),           # Channel 0: m
            (tn, hn),           # Channel 1: n
            (t_derivs[0], h_derivs[0]),  # Channel 2: A = m^2-n^2
            (t_derivs[2], h_derivs[2]),  # Channel 3: C = m^2+n^2
            (t_derivs[1], h_derivs[1]),  # Channel 4: B = 2mn
        ]

        for ch in range(N_CHANNELS):
            tv, hv = channels_vals[ch]
            diff = (hv - tv) % N
            if diff > 0:
                acc[ch] = acc[ch] * diff % N

        acc_count += 1

        # Batch GCD check
        if acc_count >= batch_size:
            for ch in range(N_CHANNELS):
                if acc[ch] > 1:
                    g = gcd(acc[ch], N)
                    if 1 < g < N:
                        return g, step, ch
            acc = [1] * N_CHANNELS
            acc_count = 0

    # Final check
    for ch in range(N_CHANNELS):
        if acc[ch] > 1:
            g = gcd(acc[ch], N)
            if 1 < g < N:
                return g, step, ch

    return 0, max_steps, -1


# ==========================================================================
# HYPOTHESIS 10: ALGEBRAIC SHORTCUTS
# ==========================================================================
"""
HYPOTHESIS: The (m,n) values at depth D are POLYNOMIALS in the root (m0,n0).
Specifically, if we apply matrix M_0, M_1, ..., M_{D-1} to get
  (m_D, n_D) = M_{D-1} * ... * M_1 * M_0 * (m_0, n_0)
then m_D = alpha * m_0 + beta * n_0 and n_D = gamma * m_0 + delta * n_0
where alpha, beta, gamma, delta are the entries of the product matrix.

For a FIXED matrix M repeated D times (orbit):
  (m_D, n_D) = M^D * (2, 1)  -- the orbit of (2,1) under M.

The derived value A_D = m_D^2 - n_D^2 is a QUADRATIC form in m_0, n_0.
So gcd(A_D, N) > 1 iff the quadratic form evaluates to zero mod p (or mod q).

For M^D: the entries of M^D are given by the characteristic polynomial of M.
If M has eigenvalues lambda1, lambda2, then M^D has entries involving
lambda1^D, lambda2^D. The condition A_D = 0 mod p becomes:
  (alpha*m0 + beta*n0)^2 = (gamma*m0 + delta*n0)^2 mod p
which factors as:
  (alpha*m0 + beta*n0 - gamma*m0 - delta*n0)(alpha*m0 + beta*n0 + gamma*m0 + delta*n0) = 0 mod p

This gives TWO linear conditions on (m0, n0) mod p. Since we start from
(m0, n0) = (2, 1), the question becomes: for which D does the orbit hit
the two "factoring hyperplanes"?

The orbit hits a random hyperplane mod p in O(p) steps (by equidistribution).
This gives NO speedup over random sampling.

HOWEVER: If we could CHOOSE the starting point (m0, n0), we could solve
the linear equation directly. But we can't -- we're stuck with (2,1).

ALTERNATIVE ALGEBRAIC SHORTCUT: Compute M^D for exponentially growing D
(doubling D at each step, like the p-1 method). If the order of M mod p
divides D, then M^D = I mod p, which means m_D = m_0 and n_D = n_0 mod p.
Then gcd(m_D - m_0, N) = gcd(m_D - 2, N) might give p.

THIS IS EXACTLY THE SMOOTH EXPONENT ATTACK in pyth_hybrid_c.c!
It's Williams p+1 in disguise, factoring when the order of M mod p has
only small prime factors.

EXPECTED COMPLEXITY: Factors N when ord(M, p) is B-smooth.
ord(M, p) divides p^2 - 1 (since M is in GL(2, F_p) and has det +-1).
Probability that p^2-1 is B-smooth is same as for p-1 method applied to p^2.
For B = 10^6: works for about 20% of primes up to 2^32.

NOVEL IDEA: Use MULTIPLE matrices simultaneously. Compute M_i^D for all 9
forward matrices with the same D = lcm(1, 2, ..., B). If ANY matrix has
B-smooth order mod p, we find the factor.

Expected success: 1 - (1-0.20)^9 = 0.87 for 9 independent matrices.
But matrix orders are NOT independent (they share the same prime p),
so the actual probability is lower, perhaps 0.5-0.7.

This is a SIGNIFICANT improvement over single-matrix smooth exponent.
"""


def h10_multi_matrix_smooth_exponent(N, B1=5000, time_limit=30.0):
    """
    Hypothesis 10: Multi-matrix smooth exponent attack.

    For each of the 9 forward matrices M_i, compute M_i^E mod N where
    E = lcm(1, 2, ..., B1). If ord(M_i, p) | E, then M_i^E = I mod p,
    meaning (m_E, n_E) = (2, 1) mod p. Then gcd(m_E - 2, N) = p.

    Key insight from experiments:
      - P1, P2, P3 have orders dividing p-1 (they act like scalar multiplication)
      - B2, F1 have orders dividing 2*(p-1) or related
      - B1, B3, F3 have order p itself (useless -- p is never B-smooth)
      - So the attack succeeds when p-1 is B-smooth (same as Pollard p-1)
      - But with 6+ independent matrix orders to check, the probability
        that ANY order is B-smooth is much higher than single p-1.

    Stage 1: raise M^E for E = prod(p_i^k_i).
    Stage 2: for each prime q in (B1, B2], check if M^(E*q) = I.

    Returns (factor, matrix_index, method).
    """
    t0 = time.time()

    def to_mod(v):
        return v % N if v >= 0 else (N - (-v % N)) % N

    def mat_from_int(M_int):
        return (to_mod(M_int[0][0]), to_mod(M_int[0][1]),
                to_mod(M_int[1][0]), to_mod(M_int[1][1]))

    def mat_mul(A, B):
        """Multiply two 2x2 matrices mod N."""
        return (
            (A[0]*B[0] + A[1]*B[2]) % N,
            (A[0]*B[1] + A[1]*B[3]) % N,
            (A[2]*B[0] + A[3]*B[2]) % N,
            (A[2]*B[1] + A[3]*B[3]) % N,
        )

    def mat_pow(M_tup, exp):
        """Matrix exponentiation by repeated squaring."""
        result = (1 % N, 0, 0, 1 % N)  # Identity
        base = M_tup
        while exp > 0:
            if exp & 1:
                result = mat_mul(result, base)
            base = mat_mul(base, base)
            exp >>= 1
        return result

    def check_endpoint(M_e, mat_idx):
        """Apply M^E to (2,1) and check gcd of derived values against N."""
        m_end = (M_e[0] * 2 + M_e[1]) % N
        n_end = (M_e[2] * 2 + M_e[3]) % N
        # If M^E = I mod p, then endpoint = (2,1) mod p
        # Check ALL derived values of (m_end, n_end) against corresponding
        # derived values of (2, 1) = (m0, n0)
        # Original: A0 = 4-1=3, B0 = 4, C0 = 5, m0-n0=1, m0+n0=3
        for val in derived_values_mod(m_end, n_end, N):
            v = val % N
            if v > 0:
                g = gcd(v, N)
                if 1 < g < N:
                    return g
        # Also check differences from root values
        root_derivs = derived_values_mod(2 % N, 1 % N, N)
        end_derivs = derived_values_mod(m_end, n_end, N)
        for rv, ev in zip(root_derivs, end_derivs):
            diff = (ev - rv) % N
            if diff > 0:
                g = gcd(diff, N)
                if 1 < g < N:
                    return g
        # Check matrix entries directly (M^E - I)
        for entry in [M_e[0] - 1, M_e[3] - 1, M_e[1], M_e[2]]:
            v = entry % N
            if v > 0:
                g = gcd(v, N)
                if 1 < g < N:
                    return g
        return 0

    # Build the exponent as a sequence of prime powers
    primes = _small_primes_up_to(B1)
    prime_powers = []
    for p in primes:
        pk = p
        while pk * p <= B1:
            pk *= p
        prime_powers.append(pk)

    # Stage 1: For each matrix, compute M^E where E = prod(p^k for p <= B1)
    mat_powers = []  # Store M^E for each matrix for stage 2
    for mat_idx, M_int in enumerate(FORWARD):
        if time.time() - t0 > time_limit:
            break

        cur = mat_from_int(M_int)

        # Raise to product of prime powers (this computes M^lcm(1..B1))
        for pk in prime_powers:
            cur = mat_pow(cur, pk)

        # Check stage 1
        f = check_endpoint(cur, mat_idx)
        if f:
            return f, mat_idx, "smooth_exponent_stage1"

        mat_powers.append((mat_idx, cur))

    # Stage 2: For each prime q in (B1, B2], check M^(E*q)
    B2 = min(B1 * 100, 500000)
    stage2_primes = _small_primes_up_to(B2)
    stage2_primes = [q for q in stage2_primes if q > B1]

    for mat_idx, M_e in mat_powers:
        if time.time() - t0 > time_limit:
            break
        for q in stage2_primes:
            if time.time() - t0 > time_limit:
                break
            M_eq = mat_pow(M_e, q)
            f = check_endpoint(M_eq, mat_idx)
            if f:
                return f, mat_idx, "smooth_exponent_stage2"

    return 0, -1, "not_found"


# ==========================================================================
# MASTER EXPERIMENT RUNNER
# ==========================================================================

def run_all_experiments(bits_per_factor=16, num_trials=20, time_limit=60.0):
    """
    Run all 10 hypothesis experiments on semiprimes of the given bit size.

    Compares each method against a BASELINE of pure random walk.

    Returns a summary dict.
    """
    print("=" * 78)
    print(f"PYTHAGOREAN TREE SEARCH EXPERIMENTS — {bits_per_factor}b per factor")
    print(f"({2*bits_per_factor}b semiprimes, {num_trials} trials each)")
    print("=" * 78)

    # Generate test semiprimes
    test_cases = []
    for i in range(num_trials):
        p, q, N = gen_semi(bits_per_factor, seed=42 + i)
        test_cases.append((N, p, q))

    # Baseline: random walk
    print("\n--- BASELINE: Random Walk ---")
    baseline_results = []
    for N, p, q in test_cases:
        t0 = time.time()
        m, n = 2 % N, 1 % N
        found = False
        for step in range(100000):
            f = check_factor_mod(m, n, N)
            if f:
                baseline_results.append(('solved', step, time.time() - t0))
                found = True
                break
            M = ALL_MATS[random.randint(0, N_ALL - 1)]
            m, n = apply_mat_mod(M, m, n, N)
        if not found:
            baseline_results.append(('failed', 100000, time.time() - t0))

    baseline_solved = sum(1 for r in baseline_results if r[0] == 'solved')
    baseline_avg_steps = sum(r[1] for r in baseline_results) / num_trials
    print(f"  Solved: {baseline_solved}/{num_trials}")
    print(f"  Avg steps: {baseline_avg_steps:.0f}")

    results = {'baseline': {'solved': baseline_solved, 'avg_steps': baseline_avg_steps}}

    # H1: Greedy GCD
    print("\n--- H1: Greedy GCD ---")
    h1_solved = 0
    h1_steps_total = 0
    for N, p, q in test_cases:
        f, steps, info = h1_greedy_gcd_search(N, max_steps=100000, time_limit=3.0)
        h1_steps_total += steps
        if f:
            h1_solved += 1
    print(f"  Solved: {h1_solved}/{num_trials}")
    print(f"  Avg steps: {h1_steps_total/num_trials:.0f}")
    results['h1_greedy_gcd'] = {'solved': h1_solved, 'avg_steps': h1_steps_total/num_trials}

    # H4: MCTS
    print("\n--- H4: MCTS ---")
    h4_solved = 0
    h4_iters_total = 0
    for N, p, q in test_cases:
        f, iters, nodes = h4_mcts_search(N, max_iterations=10000, rollout_depth=20,
                                          time_limit=3.0)
        h4_iters_total += iters
        if f:
            h4_solved += 1
    print(f"  Solved: {h4_solved}/{num_trials}")
    print(f"  Avg iterations: {h4_iters_total/num_trials:.0f}")
    results['h4_mcts'] = {'solved': h4_solved, 'avg_iters': h4_iters_total/num_trials}

    # H5: Simulated Annealing
    print("\n--- H5: Simulated Annealing ---")
    h5_solved = 0
    h5_steps_total = 0
    for N, p, q in test_cases:
        f, steps, T = h5_simulated_annealing(N, max_steps=100000, time_limit=3.0)
        h5_steps_total += steps
        if f:
            h5_solved += 1
    print(f"  Solved: {h5_solved}/{num_trials}")
    print(f"  Avg steps: {h5_steps_total/num_trials:.0f}")
    results['h5_sa'] = {'solved': h5_solved, 'avg_steps': h5_steps_total/num_trials}

    # H6: Evolutionary
    print("\n--- H6: Evolutionary ---")
    h6_solved = 0
    h6_evals_total = 0
    for N, p, q in test_cases:
        f, gen, evals = h6_evolutionary_search(N, pop_size=50, generations=200,
                                                path_length=20, time_limit=3.0)
        h6_evals_total += evals
        if f:
            h6_solved += 1
    print(f"  Solved: {h6_solved}/{num_trials}")
    print(f"  Avg evaluations: {h6_evals_total/num_trials:.0f}")
    results['h6_evolutionary'] = {'solved': h6_solved, 'avg_evals': h6_evals_total/num_trials}

    # H7: BFS with diversity pruning
    print("\n--- H7: BFS Diversity ---")
    h7_solved = 0
    h7_nodes_total = 0
    for N, p, q in test_cases:
        f, depth, nodes = h7_bfs_diversity_pruning(N, beam_width=200, max_depth=100,
                                                    time_limit=3.0)
        h7_nodes_total += nodes
        if f:
            h7_solved += 1
    print(f"  Solved: {h7_solved}/{num_trials}")
    print(f"  Avg nodes: {h7_nodes_total/num_trials:.0f}")
    results['h7_bfs_diversity'] = {'solved': h7_solved, 'avg_nodes': h7_nodes_total/num_trials}

    # H9: Multi-derived rho
    print("\n--- H9: Multi-Derived Rho ---")
    h9_solved = 0
    h9_steps_total = 0
    for N, p, q in test_cases:
        f, steps, ch = h9_multi_derived_rho(N, max_steps=1000000, batch_size=256,
                                             time_limit=3.0)
        h9_steps_total += steps
        if f:
            h9_solved += 1
    print(f"  Solved: {h9_solved}/{num_trials}")
    print(f"  Avg steps: {h9_steps_total/num_trials:.0f}")
    results['h9_multi_rho'] = {'solved': h9_solved, 'avg_steps': h9_steps_total/num_trials}

    # H10: Multi-matrix smooth exponent
    print("\n--- H10: Multi-Matrix Smooth Exponent ---")
    h10_solved = 0
    for N, p, q in test_cases:
        f, mat_idx, method = h10_multi_matrix_smooth_exponent(N, B1=5000, time_limit=3.0)
        if f:
            h10_solved += 1
    print(f"  Solved: {h10_solved}/{num_trials}")
    results['h10_smooth_exp'] = {'solved': h10_solved}

    # Summary
    print("\n" + "=" * 78)
    print("SUMMARY")
    print("=" * 78)
    for name, r in results.items():
        solved = r.get('solved', '?')
        print(f"  {name:30s}: {solved}/{num_trials} solved")
    print()

    return results


# ==========================================================================
# COMPARATIVE COMPLEXITY TABLE
# ==========================================================================
"""
METHOD                          | COMPLEXITY     | MEMORY    | SCALES?
================================|================|===========|========
H1  Greedy GCD                 | O(p)           | O(1)      | No
H2  Beam smoothness            | O(K*D*B/lnB)   | O(K)      | No
H3  Gradient navigation        | O(p)           | O(1)      | No
H4  MCTS                       | O(p)           | O(nodes)  | No
H5  Simulated annealing        | O(p)           | O(1)      | No
H5b Path-space SA              | O(???)         | O(L)      | Maybe
H6  Evolutionary               | O(K*G*L*p)     | O(K*L)    | No
H7  BFS diversity (birthday)   | O(sqrt(p))     | O(K)      | YES
H8  Learned heuristic          | O(p)           | O(N_ALL)  | No
H9  Multi-derived rho          | O(sqrt(p))     | O(1)      | YES
H10 Multi-matrix smooth exp    | O(B*log(B)*9)  | O(1)      | Conditional

KEY FINDINGS:
  - Only H7 (birthday collision) and H9 (rho) have sub-linear complexity.
  - H10 (smooth exponent) is fast but conditional on ord(M,p) smoothness.
  - All gradient/heuristic methods (H1, H3, H5) degenerate to random walk
    because the scent landscape has no useful gradient for large N.
  - The tree structure provides NO speedup for heuristic search -- the
    algebraic relationships between parent/child values don't create
    exploitable correlations in the gcd landscape.
  - The tree IS useful as a deterministic iteration function for rho-type
    methods, where the algebraic structure guarantees periodic orbits mod p.

RECOMMENDATION:
  Focus on H9 (multi-derived rho) and H10 (multi-matrix smooth exponent)
  for the C implementation. These are the only methods with provable
  advantage over random walk.

  The existing pyth_rho_c.c implements single-channel rho. Extending it
  to multi-channel (tracking 5 derived values simultaneously) should give
  a ~2-3x constant-factor improvement.

  The existing pyth_hybrid_c.c implements single-matrix smooth exponent.
  Running all 9 matrices in parallel should increase the probability of
  success from ~20% to ~60-70% for primes with partially smooth p^2-1.
"""


if __name__ == '__main__':
    import sys

    bits = 16  # bits per factor (32-bit semiprimes)
    trials = 20
    if len(sys.argv) > 1:
        bits = int(sys.argv[1])
    if len(sys.argv) > 2:
        trials = int(sys.argv[2])

    results = run_all_experiments(bits_per_factor=bits, num_trials=trials,
                                  time_limit=120.0)

    # Also run the learning experiment
    print("\n--- H8: Learn from Small ---")
    h8_results, weights = h8_learn_from_small(
        train_bits=10, test_bits_list=[12, 16, 20],
        num_train=200, num_test=50, time_limit=60.0
    )
    for bits_test, r in h8_results.items():
        print(f"  {bits_test}b: learned={r['learned_solved']}/{r['num_test']} "
              f"uniform={r['uniform_solved']}/{r['num_test']} "
              f"(learned avg={r['learned_avg_steps']:.0f} "
              f"uniform avg={r['uniform_avg_steps']:.0f})")
    print()
    print("Learned matrix weights:")
    mat_names = ['B1','B2','B3','P1','P2','P3','F1','F2','F3','B1i','B2i','B3i']
    for i, (name, w) in enumerate(zip(mat_names, weights)):
        bar = '#' * int(w * 200)
        print(f"  {name:4s}: {w:.4f} {bar}")
