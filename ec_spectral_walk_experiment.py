#!/usr/bin/env python3
"""
Experiment: Spectral Gap Expander Walk for ECDLP Kangaroo on secp256k1.

Hypothesis H_SPECTRAL:
  Using Berggren-matrix-driven jumps (with provable spectral gap 0.33 and
  O(log p) mixing) gives 1.1-1.3x fewer steps to collision than a standard
  random walk with a flat jump table.

Method:
  1. Standard kangaroo: jump index = x % 64, flat table of 64 random-ish distances
  2. Berggren kangaroo: branch = hash(x) % 3, apply Berggren matrix to per-kangaroo
     (m,n) state, use hypotenuse c = m^2 + n^2 (mod reduction) as jump distance.
     The key insight: (m,n) state is derived deterministically from the walk point,
     so two walks colliding at the same EC point take the same subsequent steps.

  We compare STEP COUNTS (not wall time) at 28b, 32b, 36b with 5 trials each.
"""

import sys
import os
import signal
import math
import random
import hashlib
from collections import defaultdict

# Add parent dir to path for imports
sys.path.insert(0, '/home/raver1975/factor')
from ecdlp_pythagorean import secp256k1_curve, ECPoint, FastCurve

# Timeout handler
class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Trial timed out")

signal.signal(signal.SIGALRM, timeout_handler)

# ---------------------------------------------------------------------------
# Berggren matrices on (m, n) -> (m', n')
# ---------------------------------------------------------------------------
# B1: (m',n') = (2m - n, m)         — actually use the standard 2x2 on (m,n)
# Using the standard Berggren matrices that act on (m, n) coprime pairs:
#   B1 = [[2, -1], [1,  0]]
#   B2 = [[2,  1], [1,  0]]
#   B3 = [[1,  2], [0,  1]]
BERGGREN = [
    ((2, -1), (1, 0)),   # B1
    ((2,  1), (1, 0)),   # B2
    ((1,  2), (0, 1)),   # B3
]

def apply_berggren(mat, m, n):
    """Apply Berggren matrix to (m, n). Returns (m', n')."""
    (a, b), (c, d) = mat
    return (a * m + b * n, c * m + d * n)

def berggren_hash(x_int, num_branches=3):
    """Deterministic branch selection from EC point x-coordinate."""
    # Use a few bits from a hash for good mixing
    h = hashlib.md5(x_int.to_bytes(32, 'big')).digest()
    return h[0] % num_branches

# ---------------------------------------------------------------------------
# Standard Kangaroo (step-counting version)
# ---------------------------------------------------------------------------

def kangaroo_standard(curve, G, P, k_true, search_bound, max_steps=None):
    """
    Standard Pollard kangaroo with flat jump table.
    Returns (steps, found) where steps = total EC additions performed.
    """
    n = curve.n
    half_bound = search_bound // 2

    # Build a flat jump table: 64 entries, geometrically spaced
    num_jumps = 64
    mean_jump = max(1, int(math.isqrt(half_bound)) // 4)
    # Lévy-like spread (matches what the real solver uses)
    jumps = []
    for i in range(num_jumps):
        # Exponential spread from mean_jump/32 to mean_jump*32
        scale = 2 ** ((i - num_jumps // 2) * 10.0 / num_jumps)
        jumps.append(max(1, int(mean_jump * scale)))

    # Precompute jump_i * G
    jump_points = [curve.scalar_mult(j, G) for j in jumps]

    # DP criterion
    D = max(1, search_bound.bit_length() // 4)
    dp_mask = (1 << D) - 1

    # Tame: starts at half_bound//2
    tame_pos = half_bound // 2
    tame_point = curve.scalar_mult(tame_pos, G)

    # Wild: starts at P
    wild_pos = 0
    wild_point = P

    dp_table = {}
    steps = 0

    if max_steps is None:
        max_steps = 16 * int(math.isqrt(half_bound)) + 10000

    for _ in range(max_steps):
        # Tame step
        ji = tame_point.x % num_jumps if not tame_point.is_infinity else 0
        tame_pos += jumps[ji]
        tame_point = curve.add(tame_point, jump_points[ji])
        steps += 1

        if not tame_point.is_infinity and (tame_point.x & dp_mask) == 0:
            key = tame_point.x
            if key in dp_table:
                stored_pos, stored_tame = dp_table[key]
                if not stored_tame:
                    k_cand = (tame_pos - stored_pos) % n
                    if k_cand == k_true or (n - k_cand) % n == k_true:
                        return steps, True
            dp_table[key] = (tame_pos, True)

        # Wild step
        ji = wild_point.x % num_jumps if not wild_point.is_infinity else 0
        wild_pos += jumps[ji]
        wild_point = curve.add(wild_point, jump_points[ji])
        steps += 1

        if not wild_point.is_infinity and (wild_point.x & dp_mask) == 0:
            key = wild_point.x
            if key in dp_table:
                stored_pos, stored_tame = dp_table[key]
                if stored_tame:
                    k_cand = (stored_pos - wild_pos) % n
                    if k_cand == k_true or (n - k_cand) % n == k_true:
                        return steps, True
            dp_table[key] = (wild_pos, False)

    return steps, False

# ---------------------------------------------------------------------------
# Berggren Spectral Kangaroo (step-counting version)
# ---------------------------------------------------------------------------

def kangaroo_berggren(curve, G, P, k_true, search_bound, max_steps=None):
    """
    Kangaroo with Berggren-matrix-driven jumps.

    Each kangaroo has a (m, n) state. At each step:
      1. branch = hash(point.x) % 3
      2. (m, n) = B_{branch} * (m, n)
      3. jump_distance = (m^2 + n^2) mod scale_bound
      4. Step forward by jump_distance

    The (m, n) state is reset from the point's x-coordinate periodically
    to ensure determinism (two walks at the same point produce the same jump).

    KEY DESIGN: The (m, n) state must be a function of the current EC point only
    (not walk history), otherwise two merging walks would diverge. We derive
    (m, n) from x each step.
    """
    n_order = curve.n
    half_bound = search_bound // 2
    mean_jump = max(1, int(math.isqrt(half_bound)) // 4)

    # We need deterministic jumps from x alone. So at each step:
    # 1. Derive (m, n) from x
    # 2. Pick branch from x
    # 3. Apply Berggren matrix to get (m', n')
    # 4. Jump distance = (m'^2 + n'^2) scaled to mean_jump

    # Precompute a cache of jump points (we'll compute on-the-fly for new distances)
    # To keep memory bounded, we use a small LRU-like approach
    jump_cache = {}
    cache_hits = 0
    cache_misses = 0

    def get_jump(point):
        """Compute jump distance and jump point from EC point deterministically."""
        nonlocal cache_hits, cache_misses
        if point.is_infinity:
            # Fallback: small fixed jump
            dist = mean_jump
            if dist not in jump_cache:
                jump_cache[dist] = curve.scalar_mult(dist, G)
            return dist, jump_cache[dist]

        x = point.x
        # Derive (m, n) from x: use different bit ranges
        # m = bits [0:64], n = bits [64:128], ensure coprime-ish
        m_raw = (x & 0xFFFFFFFFFFFFFFFF) | 1  # ensure odd
        n_raw = ((x >> 64) & 0xFFFFFFFFFFFFFFFF) | 1
        m_init = max(2, m_raw % 10000)
        n_init = max(1, n_raw % 10000)

        # Pick branch
        branch = berggren_hash(x)
        mat = BERGGREN[branch]
        m2, n2 = apply_berggren(mat, m_init, n_init)

        # Hypotenuse
        hyp = m2 * m2 + n2 * n2

        # Scale to reasonable jump distance (around mean_jump, with spread)
        # Use log-scale mapping: jump in [mean_jump/32, mean_jump*32]
        # The hypotenuse varies widely, so mod into a reasonable range
        log_range = 10  # 2^10 = 1024x spread
        bucket = hyp % (1 << log_range)
        scale = 2 ** ((bucket / (1 << log_range) - 0.5) * log_range)
        dist = max(1, int(mean_jump * scale))

        if dist in jump_cache:
            cache_hits += 1
            return dist, jump_cache[dist]

        cache_misses += 1
        jp = curve.scalar_mult(dist, G)
        # Bound cache size
        if len(jump_cache) < 2000:
            jump_cache[dist] = jp
        return dist, jp

    # DP criterion
    D = max(1, search_bound.bit_length() // 4)
    dp_mask = (1 << D) - 1

    # Tame
    tame_pos = half_bound // 2
    tame_point = curve.scalar_mult(tame_pos, G)

    # Wild
    wild_pos = 0
    wild_point = P

    dp_table = {}
    steps = 0

    if max_steps is None:
        max_steps = 16 * int(math.isqrt(half_bound)) + 10000

    for _ in range(max_steps):
        # Tame step
        dist, jp = get_jump(tame_point)
        tame_pos += dist
        tame_point = curve.add(tame_point, jp)
        steps += 1

        if not tame_point.is_infinity and (tame_point.x & dp_mask) == 0:
            key = tame_point.x
            if key in dp_table:
                stored_pos, stored_tame = dp_table[key]
                if not stored_tame:
                    k_cand = (tame_pos - stored_pos) % n_order
                    if k_cand == k_true or (n_order - k_cand) % n_order == k_true:
                        return steps, True
            dp_table[key] = (tame_pos, True)

        # Wild step
        dist, jp = get_jump(wild_point)
        wild_pos += dist
        wild_point = curve.add(wild_point, jp)
        steps += 1

        if not wild_point.is_infinity and (wild_point.x & dp_mask) == 0:
            key = wild_point.x
            if key in dp_table:
                stored_pos, stored_tame = dp_table[key]
                if stored_tame:
                    k_cand = (stored_pos - wild_pos) % n_order
                    if k_cand == k_true or (n_order - k_cand) % n_order == k_true:
                        return steps, True
            dp_table[key] = (wild_pos, False)

    return steps, False

# ---------------------------------------------------------------------------
# Berggren v2: Precomputed table variant (fairer comparison)
# ---------------------------------------------------------------------------

def kangaroo_berggren_table(curve, G, P, k_true, search_bound, max_steps=None):
    """
    Berggren-driven jump TABLE (not per-step scalar mult).

    Build 64 jump distances using Berggren matrices applied iteratively,
    creating a table with the spectral-gap-guaranteed mixing distribution.
    Then use standard kangaroo with this table.

    This isolates the effect of the Berggren distribution from the overhead
    of per-step scalar multiplication.
    """
    n_order = curve.n
    half_bound = search_bound // 2
    mean_jump = max(1, int(math.isqrt(half_bound)) // 4)
    num_jumps = 64

    # Generate 64 jump distances by walking Berggren tree from (2,1)
    # Use all 3 branches at each level, BFS to get diverse hypotenuses
    m_state, n_state = 2, 1
    hyps = []
    queue = [(2, 1)]
    seen = set()
    while len(hyps) < num_jumps * 4 and queue:
        next_q = []
        for m, nn in queue:
            for mat in BERGGREN:
                m2, n2 = apply_berggren(mat, m, nn)
                m2, n2 = abs(m2), abs(n2)
                if m2 <= 0 or n2 <= 0:
                    continue
                hyp = m2 * m2 + n2 * n2
                if hyp not in seen:
                    seen.add(hyp)
                    hyps.append(hyp)
                    if len(next_q) < 500:  # bound BFS width
                        next_q.append((m2, n2))
        queue = next_q

    hyps.sort()
    # Select 64 with geometric spacing
    if len(hyps) > num_jumps:
        ratio = len(hyps) / num_jumps
        selected = [hyps[min(int(i * ratio), len(hyps) - 1)] for i in range(num_jumps)]
    else:
        selected = hyps[:num_jumps]
        while len(selected) < num_jumps:
            selected.append(selected[-1] * 2)

    # Scale to desired mean
    cur_mean = sum(selected) / len(selected)
    scale = mean_jump / max(1, cur_mean)
    jumps = [max(1, int(h * scale)) for h in selected]

    # Precompute jump points
    jump_points = [curve.scalar_mult(j, G) for j in jumps]

    # DP criterion
    D = max(1, search_bound.bit_length() // 4)
    dp_mask = (1 << D) - 1

    # Tame
    tame_pos = half_bound // 2
    tame_point = curve.scalar_mult(tame_pos, G)

    # Wild
    wild_pos = 0
    wild_point = P

    dp_table = {}
    steps = 0

    if max_steps is None:
        max_steps = 16 * int(math.isqrt(half_bound)) + 10000

    for _ in range(max_steps):
        # Tame step - use Berggren hash for index selection
        if not tame_point.is_infinity:
            ji = berggren_hash(tame_point.x, num_jumps)
        else:
            ji = 0
        tame_pos += jumps[ji]
        tame_point = curve.add(tame_point, jump_points[ji])
        steps += 1

        if not tame_point.is_infinity and (tame_point.x & dp_mask) == 0:
            key = tame_point.x
            if key in dp_table:
                stored_pos, stored_tame = dp_table[key]
                if not stored_tame:
                    k_cand = (tame_pos - stored_pos) % n_order
                    if k_cand == k_true or (n_order - k_cand) % n_order == k_true:
                        return steps, True
            dp_table[key] = (tame_pos, True)

        # Wild step
        if not wild_point.is_infinity:
            ji = berggren_hash(wild_point.x, num_jumps)
        else:
            ji = 0
        wild_pos += jumps[ji]
        wild_point = curve.add(wild_point, jump_points[ji])
        steps += 1

        if not wild_point.is_infinity and (wild_point.x & dp_mask) == 0:
            key = wild_point.x
            if key in dp_table:
                stored_pos, stored_tame = dp_table[key]
                if stored_tame:
                    k_cand = (stored_pos - wild_pos) % n_order
                    if k_cand == k_true or (n_order - k_cand) % n_order == k_true:
                        return steps, True
            dp_table[key] = (wild_pos, False)

    return steps, False

# ---------------------------------------------------------------------------
# Walk autocorrelation measurement
# ---------------------------------------------------------------------------

def measure_autocorrelation(curve, G, search_bound, method='standard', num_steps=2000):
    """
    Measure autocorrelation of jump indices over a walk.
    Low autocorrelation = good mixing = independent steps.
    """
    half_bound = search_bound // 2
    pos = half_bound // 2
    point = curve.scalar_mult(pos, G)

    mean_jump = max(1, int(math.isqrt(half_bound)) // 4)
    num_jumps = 64

    if method == 'standard':
        # Build flat table
        jumps = []
        for i in range(num_jumps):
            scale = 2 ** ((i - num_jumps // 2) * 10.0 / num_jumps)
            jumps.append(max(1, int(mean_jump * scale)))
        jump_points = [curve.scalar_mult(j, G) for j in jumps]
    else:
        # Berggren table
        hyps = []
        queue = [(2, 1)]
        seen = set()
        while len(hyps) < num_jumps * 4 and queue:
            next_q = []
            for m, nn in queue:
                for mat in BERGGREN:
                    m2, n2 = apply_berggren(mat, m, nn)
                    m2, n2 = abs(m2), abs(n2)
                    if m2 <= 0 or n2 <= 0:
                        continue
                    hyp = m2 * m2 + n2 * n2
                    if hyp not in seen:
                        seen.add(hyp)
                        hyps.append(hyp)
                        if len(next_q) < 500:
                            next_q.append((m2, n2))
            queue = next_q
        hyps.sort()
        ratio = max(1, len(hyps) / num_jumps)
        selected = [hyps[min(int(i * ratio), len(hyps) - 1)] for i in range(num_jumps)]
        cur_mean = sum(selected) / len(selected)
        sc = mean_jump / max(1, cur_mean)
        jumps = [max(1, int(h * sc)) for h in selected]
        jump_points = [curve.scalar_mult(j, G) for j in jumps]

    indices = []
    for _ in range(num_steps):
        if method == 'standard':
            ji = point.x % num_jumps if not point.is_infinity else 0
        else:
            ji = berggren_hash(point.x, num_jumps) if not point.is_infinity else 0
        indices.append(ji)
        pos += jumps[ji]
        point = curve.add(point, jump_points[ji])

    # Compute lag-1 autocorrelation
    if len(indices) < 2:
        return 0.0
    mean_idx = sum(indices) / len(indices)
    var = sum((x - mean_idx) ** 2 for x in indices)
    if var == 0:
        return 1.0
    cov1 = sum((indices[i] - mean_idx) * (indices[i + 1] - mean_idx)
               for i in range(len(indices) - 1))
    autocorr = cov1 / var
    return autocorr

# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment():
    print("=" * 72)
    print("EXPERIMENT: Spectral Gap Expander Walk for ECDLP Kangaroo")
    print("=" * 72)
    print()
    print("H_SPECTRAL: Berggren-matrix-driven jumps (spectral gap 0.33,")
    print("O(log p) mixing) should give 1.1-1.3x fewer steps than flat table.")
    print()

    curve = secp256k1_curve()
    G = curve.G
    n = curve.n

    bit_sizes = [28, 32, 36]
    num_trials = 5
    timeout_sec = 30

    results = defaultdict(lambda: defaultdict(list))

    for bits in bit_sizes:
        search_bound = 1 << bits
        print(f"\n{'─' * 72}")
        print(f"  Testing {bits}-bit search space (bound = 2^{bits} = {search_bound})")
        print(f"  Expected sqrt steps ~ {int(math.isqrt(search_bound))}")
        print(f"{'─' * 72}")

        for trial in range(num_trials):
            # Generate random k in [1, search_bound)
            k = random.randint(1, search_bound - 1)
            P = curve.scalar_mult(k, G)

            print(f"\n  Trial {trial + 1}/{num_trials}: k = {k} ({k.bit_length()}b)")

            # --- Standard kangaroo ---
            signal.alarm(timeout_sec)
            try:
                steps_std, found_std = kangaroo_standard(
                    curve, G, P, k, search_bound)
                signal.alarm(0)
                if found_std:
                    results[bits]['standard'].append(steps_std)
                    print(f"    Standard:       {steps_std:>8d} steps  [OK]")
                else:
                    print(f"    Standard:       FAILED ({steps_std} steps, not found)")
            except TimeoutError:
                signal.alarm(0)
                print(f"    Standard:       TIMEOUT ({timeout_sec}s)")
            except Exception as e:
                signal.alarm(0)
                print(f"    Standard:       ERROR: {e}")

            # --- Berggren table kangaroo ---
            signal.alarm(timeout_sec)
            try:
                steps_bt, found_bt = kangaroo_berggren_table(
                    curve, G, P, k, search_bound)
                signal.alarm(0)
                if found_bt:
                    results[bits]['berggren_table'].append(steps_bt)
                    print(f"    Berggren table: {steps_bt:>8d} steps  [OK]")
                else:
                    print(f"    Berggren table: FAILED ({steps_bt} steps, not found)")
            except TimeoutError:
                signal.alarm(0)
                print(f"    Berggren table: TIMEOUT ({timeout_sec}s)")
            except Exception as e:
                signal.alarm(0)
                print(f"    Berggren table: ERROR: {e}")

            # --- Berggren per-step kangaroo (only at 28b due to scalar mult cost) ---
            if bits <= 28:
                signal.alarm(timeout_sec)
                try:
                    steps_bp, found_bp = kangaroo_berggren(
                        curve, G, P, k, search_bound)
                    signal.alarm(0)
                    if found_bp:
                        results[bits]['berggren_perstep'].append(steps_bp)
                        print(f"    Berggren step:  {steps_bp:>8d} steps  [OK]")
                    else:
                        print(f"    Berggren step:  FAILED ({steps_bp} steps, not found)")
                except TimeoutError:
                    signal.alarm(0)
                    print(f"    Berggren step:  TIMEOUT ({timeout_sec}s)")
                except Exception as e:
                    signal.alarm(0)
                    print(f"    Berggren step:  ERROR: {e}")

    # --- Summary ---
    print(f"\n\n{'=' * 72}")
    print("RESULTS SUMMARY")
    print(f"{'=' * 72}")

    for bits in bit_sizes:
        search_bound = 1 << bits
        sqrt_n = int(math.isqrt(search_bound))
        print(f"\n  {bits}-bit (sqrt(N) = {sqrt_n}):")

        for method in ['standard', 'berggren_table', 'berggren_perstep']:
            data = results[bits][method]
            if not data:
                continue
            mean_s = sum(data) / len(data)
            std_s = (sum((x - mean_s) ** 2 for x in data) / max(1, len(data) - 1)) ** 0.5
            ratio = mean_s / sqrt_n
            print(f"    {method:20s}: mean={mean_s:8.0f}  std={std_s:8.0f}  "
                  f"ratio_to_sqrt={ratio:.2f}  n={len(data)}")

    # Compute speedup ratios
    print(f"\n\n{'=' * 72}")
    print("SPEEDUP ANALYSIS (steps_standard / steps_berggren_table)")
    print(f"{'=' * 72}")

    for bits in bit_sizes:
        std_data = results[bits]['standard']
        berg_data = results[bits]['berggren_table']
        if std_data and berg_data:
            std_mean = sum(std_data) / len(std_data)
            berg_mean = sum(berg_data) / len(berg_data)
            speedup = std_mean / berg_mean if berg_mean > 0 else float('inf')
            print(f"  {bits}b: standard={std_mean:.0f}  berggren={berg_mean:.0f}  "
                  f"speedup={speedup:.3f}x")
        else:
            print(f"  {bits}b: insufficient data (std={len(std_data)}, berg={len(berg_data)})")

    # --- Autocorrelation ---
    print(f"\n\n{'=' * 72}")
    print("WALK AUTOCORRELATION (lag-1)")
    print(f"{'=' * 72}")
    print("  Lower = better mixing (0 = perfectly random, 1 = deterministic)")

    for bits in [28, 32]:
        search_bound = 1 << bits
        print(f"\n  {bits}-bit:")
        signal.alarm(timeout_sec)
        try:
            ac_std = measure_autocorrelation(curve, G, search_bound, 'standard', 1000)
            signal.alarm(0)
            print(f"    Standard:       {ac_std:.4f}")
        except (TimeoutError, Exception) as e:
            signal.alarm(0)
            print(f"    Standard:       ERROR: {e}")

        signal.alarm(timeout_sec)
        try:
            ac_berg = measure_autocorrelation(curve, G, search_bound, 'berggren', 1000)
            signal.alarm(0)
            print(f"    Berggren table: {ac_berg:.4f}")
        except (TimeoutError, Exception) as e:
            signal.alarm(0)
            print(f"    Berggren table: ERROR: {e}")

    # --- Verdict ---
    print(f"\n\n{'=' * 72}")
    print("VERDICT")
    print(f"{'=' * 72}")

    all_speedups = []
    for bits in bit_sizes:
        std_data = results[bits]['standard']
        berg_data = results[bits]['berggren_table']
        if std_data and berg_data:
            speedup = (sum(std_data) / len(std_data)) / (sum(berg_data) / len(berg_data))
            all_speedups.append(speedup)

    if all_speedups:
        avg_speedup = sum(all_speedups) / len(all_speedups)
        if avg_speedup >= 1.1:
            print(f"  H_SPECTRAL CONFIRMED: avg speedup = {avg_speedup:.3f}x (>= 1.1x)")
            print("  Berggren spectral walk reduces step count meaningfully.")
        elif avg_speedup >= 1.02:
            print(f"  H_SPECTRAL MARGINAL: avg speedup = {avg_speedup:.3f}x (1.02-1.10x)")
            print("  Small improvement, likely within noise for these sample sizes.")
        elif avg_speedup >= 0.95:
            print(f"  H_SPECTRAL REJECTED: avg speedup = {avg_speedup:.3f}x (within noise)")
            print("  No meaningful difference. Jump source does not matter for convergence.")
        else:
            print(f"  H_SPECTRAL REJECTED: avg speedup = {avg_speedup:.3f}x (WORSE)")
            print("  Berggren walk is slower. Spectral gap does not help kangaroo.")

        print()
        print("  Analysis:")
        print("  - Pollard kangaroo convergence depends on birthday paradox (collision")
        print("    probability), which is determined by the number of DISTINCT points")
        print("    visited, not the walk's mixing properties.")
        print("  - Spectral gap guarantees rapid mixing of the (m,n) state, but the")
        print("    kangaroo's convergence rate is already O(sqrt(N)) regardless of")
        print("    jump distribution (as long as walks are non-degenerate).")
        print("  - The constant factor depends on jump SPREAD (Levy vs uniform),")
        print("    not on the algebraic source of jump distances.")
    else:
        print("  INSUFFICIENT DATA to evaluate hypothesis.")


if __name__ == '__main__':
    run_experiment()
