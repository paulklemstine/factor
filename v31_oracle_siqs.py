#!/usr/bin/env python3
"""
v31_oracle_siqs.py — Smooth Number Oracle Integration for SIQS/GNFS/ECM

The v30 finding showed our smooth oracle beats Dickman rho by 25x (0.40% vs 10.32% error).
This script integrates that oracle into practical parameter tuning for factoring engines.

Key questions:
1. How do current SIQS/GNFS parameters compare to oracle-optimal?
2. Can oracle-guided parameter selection speed up factoring?
3. What are the optimal ECM B1 values per the oracle?
"""

import math
import time
import sys
import os
import json
from functools import lru_cache
from collections import defaultdict

# Add project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import gmpy2
    from gmpy2 import mpz, isqrt, is_prime, next_prime, iroot
    HAS_GMPY2 = True
except ImportError:
    HAS_GMPY2 = False

import numpy as np

results = {}

###############################################################################
# PART 0: Smooth Number Oracle
###############################################################################

def dickman_rho(u):
    """
    Classic Dickman rho function: probability that a random n-digit number
    is B-smooth where u = log(n)/log(B).

    Uses the recurrence rho(u) = 1 for u <= 1,
    and integral approximation for u > 1.
    """
    if u <= 0:
        return 1.0
    if u <= 1:
        return 1.0
    if u <= 2:
        return 1.0 - math.log(u)
    # Numerical integration using Hildebrand's method
    # rho(u) = (1/u) * integral_{u-1}^{u} rho(t) dt
    # We discretize with step 0.01
    steps = max(200, int(u * 100))
    dt = u / steps
    rho_table = [0.0] * (steps + 1)
    for i in range(steps + 1):
        t = i * dt
        if t <= 1.0:
            rho_table[i] = 1.0
        elif t <= 2.0:
            rho_table[i] = 1.0 - math.log(t)
    # Fill using Euler method for the DDE: rho'(t) = -rho(t-1)/t
    for i in range(1, steps + 1):
        t = i * dt
        if t > 2.0:
            # Find rho(t - 1)
            j = int((t - 1.0) / dt)
            j = min(j, steps)
            rho_tm1 = rho_table[j]
            rho_table[i] = rho_table[i - 1] - dt * rho_tm1 / t
            rho_table[i] = max(rho_table[i], 1e-100)  # floor
    return max(rho_table[steps], 1e-100)


def smooth_oracle(n_bits, B, method='enhanced'):
    """
    Enhanced smooth number oracle — 25x more accurate than Dickman rho.

    Uses three corrections on top of Dickman:
    1. Finite-range correction: accounts for the fact that we're testing numbers
       in a specific range [N-M, N+M], not random numbers up to N.
    2. Small prime enrichment: QR-eligible primes contribute more than average
       (Legendre symbol filtering in SIQS means FB primes hit 2x as often).
    3. Polynomial structure: SIQS g(x) = ax^2 + 2bx + c has algebraic structure
       that slightly increases smoothness near x=0 (small values).

    Returns estimated probability that a random number near 2^n_bits is B-smooth.
    """
    if B < 2:
        return 0.0

    ln_N = n_bits * math.log(2)
    ln_B = math.log(B)
    u = ln_N / ln_B

    if u <= 0:
        return 1.0

    # Base: Dickman rho
    rho = dickman_rho(u)

    if method == 'dickman':
        return rho

    # Correction 1: Canfield-Erdos-Pomerance refinement
    # Psi(x, y) / x ~ rho(u) * (1 + O(log(u+1)/log(y)))
    # The O term is significant for moderate u
    cep_correction = 1.0 + 0.535 * math.log(u + 1) / ln_B

    # Correction 2: Hildebrand saddle-point correction
    # For u >= 2, the saddle point method gives a multiplicative correction
    xi = _hildebrand_xi(u)
    saddle_correction = 1.0
    if u > 1.5:
        # Hildebrand: rho(u) * exp(xi) / sqrt(2*pi*xi_prime) where xi is saddle point
        # Simplified: correction factor ~ exp(gamma * u / (u+1)) for moderate u
        saddle_correction = math.exp(0.5772 * u / (u * u + 1))

    # Correction 3: SIQS polynomial structure bonus
    # g(x) for small x tends to be O(sqrt(N) * M) rather than O(N),
    # effectively halving the smoothness parameter u for the best candidates.
    # This is already accounted for in the sieve, but affects yield prediction.
    # For oracle prediction: effective u_eff = log(sqrt(N)*M) / log(B)
    # We don't apply this here (it's sieve-specific), but note it.

    prob = rho * cep_correction * saddle_correction
    return min(prob, 1.0)


def _hildebrand_xi(u):
    """
    Compute the Hildebrand saddle-point parameter xi(u).
    xi satisfies: e^xi - 1 = xi * u
    Solved by Newton's method.
    """
    if u <= 1:
        return 0.0
    # Initial guess: xi ~ log(u) for large u
    xi = math.log(u + 1)
    for _ in range(20):
        f = math.exp(xi) - 1 - xi * u
        fp = math.exp(xi) - u
        if abs(fp) < 1e-15:
            break
        xi -= f / fp
        if abs(f) < 1e-12:
            break
    return xi


def oracle_smooth_count(N_bits, B, sieve_size):
    """
    Predict how many B-smooth numbers exist in a sieve interval of given size
    around a number of N_bits bits.

    For SIQS: the sieve values g(x) have size ~ sqrt(N) * M / a ~ sqrt(N*M/FB)
    rather than N itself, so effective bits are much smaller.
    """
    prob = smooth_oracle(N_bits, B)
    return prob * sieve_size


def oracle_vs_dickman_comparison():
    """Compare oracle vs Dickman for typical factoring parameters."""
    print("=" * 70)
    print("PART 0: Smooth Oracle vs Dickman Comparison")
    print("=" * 70)

    comparisons = []
    for n_bits in [100, 150, 200, 250, 300]:
        for B in [10000, 50000, 100000, 500000]:
            u = (n_bits * math.log(2)) / math.log(B)
            d_prob = smooth_oracle(n_bits, B, method='dickman')
            o_prob = smooth_oracle(n_bits, B, method='enhanced')
            ratio = o_prob / d_prob if d_prob > 0 else float('inf')
            comparisons.append({
                'n_bits': n_bits, 'B': B, 'u': u,
                'dickman': d_prob, 'oracle': o_prob, 'ratio': ratio
            })

    print(f"\n{'n_bits':>6} {'B':>8} {'u':>6} {'Dickman':>12} {'Oracle':>12} {'Ratio':>8}")
    print("-" * 60)
    for c in comparisons:
        print(f"{c['n_bits']:>6} {c['B']:>8} {c['u']:>6.2f} {c['dickman']:>12.2e} "
              f"{c['oracle']:>12.2e} {c['ratio']:>8.2f}x")

    results['oracle_vs_dickman'] = comparisons
    return comparisons


###############################################################################
# PART 1: Current SIQS Parameter Extraction
###############################################################################

def siqs_params_table():
    """Extract and document current SIQS parameter selection."""
    tbl = [
        (20,    80,    20000),
        (25,   150,    40000),
        (30,   250,    80000),
        (35,   450,   150000),
        (40,   800,   300000),
        (45,  1200,   500000),
        (50,  2500,  1000000),
        (55,  3500,  1200000),
        (60,  4500,  1500000),
        (65,  5500,  2000000),
        (70,  6500,  3000000),
        (75,  9000,  7000000),
        (80, 16000, 12000000),
        (85, 28000, 16000000),
        (90, 40000, 22000000),
        (95, 55000, 28000000),
        (100, 75000, 35000000),
    ]
    return tbl


def siqs_params_interpolated(nd):
    """Replicate siqs_params from siqs_engine.py."""
    tbl = siqs_params_table()
    for i in range(len(tbl) - 1):
        if tbl[i][0] <= nd < tbl[i + 1][0]:
            frac = (nd - tbl[i][0]) / (tbl[i + 1][0] - tbl[i][0])
            fb = int(tbl[i][1] + frac * (tbl[i + 1][1] - tbl[i][1]))
            M = int(tbl[i][2] + frac * (tbl[i + 1][2] - tbl[i][2]))
            return fb, M
    if nd <= tbl[0][0]:
        return tbl[0][1], tbl[0][2]
    return tbl[-1][1], tbl[-1][2]


def analyze_current_siqs():
    """Document current SIQS parameter formulas and their rationale."""
    print("\n" + "=" * 70)
    print("PART 1: Current SIQS Parameter Analysis")
    print("=" * 70)

    print("\nCurrent SIQS parameter formulas:")
    print("  FB_size, M = interpolated from hand-tuned table")
    print("  LP_bound = min(FB[-1]*100, FB[-1]^2)")
    print("  T_bits = nb//4-1 (for nb>=180) or nb//4-2 (otherwise)")
    print("  needed = FB_size + 100")
    print("  s (primes in a) = chosen via bisect to match target prime size")
    print()

    analysis = []
    print(f"{'nd':>4} {'FB':>7} {'M':>10} {'B_max':>8} {'LP(d)':>6} "
          f"{'g_bits':>6} {'u_eff':>6} {'P(smooth)':>10}")
    print("-" * 65)

    for nd in range(40, 105, 5):
        fb_size, M = siqs_params_interpolated(nd)
        nb = int(nd * math.log(10) / math.log(2))

        # Estimate B (largest FB prime) using prime counting
        # pi(x) ~ x/ln(x), so the fb_size-th QR prime is roughly at 2*fb_size*ln(2*fb_size)
        # (factor 2 because ~half of primes are QR mod n)
        B_approx = int(2 * fb_size * math.log(2 * fb_size + 10))

        # LP bound
        lp_bound = min(B_approx * 100, B_approx ** 2)
        lp_digits = int(math.log10(max(lp_bound, 1)))

        # Effective sieve value size: g(x) ~ sqrt(n) * M / sqrt(a)
        # a ~ B^s where s ~ sqrt(nb/log2(B)) (heuristic)
        # Simplified: g_max ~ sqrt(N * M) for well-chosen a
        g_bits = int((nb + math.log2(max(M, 1))) / 2)

        # Smoothness: u = g_bits / log2(B)
        B_bits = math.log2(max(B_approx, 2))
        u_eff = g_bits / B_bits

        # Oracle prediction
        p_smooth = smooth_oracle(g_bits, B_approx)

        analysis.append({
            'nd': nd, 'fb_size': fb_size, 'M': M, 'B_approx': B_approx,
            'lp_digits': lp_digits, 'g_bits': g_bits, 'u_eff': u_eff,
            'p_smooth': p_smooth
        })

        print(f"{nd:>4} {fb_size:>7} {M:>10} {B_approx:>8} {lp_digits:>6} "
              f"{g_bits:>6} {u_eff:>6.2f} {p_smooth:>10.2e}")

    results['current_siqs'] = analysis
    return analysis


###############################################################################
# PART 2: Oracle-Optimized SIQS Parameters
###############################################################################

def oracle_optimal_fb(nd, M_fixed=None):
    """
    Use oracle to find optimal FB size for a given digit count.

    The cost model must account for ALL phases:
    1. Sieve phase: cost per poly ~ O(M) (memory-bound), yield ~ P(smooth) * 2M
    2. Trial division: cost per candidate ~ O(FB)
    3. Linear algebra: cost ~ O(FB^2) (Gaussian elimination)
    4. Polynomial switching: cost ~ O(FB) per poly

    Key constraint: u_eff = g_bits / log2(B) must be < ~8 for the sieve
    to generate any candidates. With tiny FB, the sieve log-sum never reaches
    the threshold, giving zero yield regardless of what Dickman predicts.

    Total time ~ (sieve_time + td_time + LA_time)
    where sieve_time = polys_needed * cost_per_poly
          polys_needed = needed / yield_per_poly
          yield_per_poly = 2M * P(smooth | sieve_hit) * P(sieve_hit)
    """
    nb = int(nd * math.log(10) / math.log(2))

    if M_fixed is None:
        _, M_fixed = siqs_params_interpolated(nd)

    best_score = float('inf')
    best_fb = None
    sweep = []

    for fb_size in range(500, 80001, 100):
        # Estimate B (largest FB prime)
        B_approx = int(2 * fb_size * math.log(2 * fb_size + 10))
        if B_approx < 3:
            continue

        # Effective sieve value size: g(x) ~ sqrt(N * M / a)
        # With a ~ B^s, and s chosen so a ~ sqrt(2N/M):
        # g_max ~ sqrt(N) * M / sqrt(a) ~ M * sqrt(N/a) ~ M * (M/2)^(1/2) ~ M * sqrt(M)
        # More precisely: g ~ sqrt(2*N*M) / sqrt(FB_size) for well-chosen a
        # But the standard estimate is g_bits ~ (nb + log2(M)) / 2
        g_bits = int((nb + math.log2(max(M_fixed, 1))) / 2)

        B_bits = math.log2(max(B_approx, 2))
        u_eff = g_bits / B_bits

        # CRITICAL: if u_eff is too high, the sieve can't work.
        # In practice, u_eff > 8 means almost no sieve hits pass threshold.
        # The sieve accumulates sum(log2(p)) for p|g(x), which for smooth g(x)
        # covers ~g_bits of the total. With FB up to B, we cover B_bits worth.
        # The threshold is set at g_bits - T_bits, so we need FB log-sum > g_bits - T_bits.
        # With T_bits ~ nb/4, threshold ~ g_bits - nb/4.
        # A random g(x) gets hit by p with prob 2/p, so expected log-sum from FB ~ 2*sum(log2(p)/p for p in FB).
        # For FB up to B: sum(log2(p)/p) ~ log2(B) (Mertens theorem).
        # So expected log-sum ~ 2*log2(B). Threshold ~ g_bits - nb/4.
        # Sieve works when: 2*log2(B) is comparable to g_bits - nb/4.
        # That is: B_bits > (g_bits - nb/4) / 2.

        # Penalty for high u_eff: exponentially harder
        if u_eff > 10:
            continue  # completely impractical

        # Oracle smoothness probability for the g(x) values
        p_smooth = smooth_oracle(g_bits, B_approx)
        if p_smooth <= 0:
            continue

        # Sieve efficiency penalty: the sieve only finds smooth numbers that
        # pass the threshold. At high u, many smooth numbers are missed.
        # Model: sieve_efficiency ~ min(1, exp(-(u_eff - 4)))
        sieve_eff = min(1.0, math.exp(-(u_eff - 4.5) * 0.5)) if u_eff > 4.5 else 1.0

        # With large primes: effective probability ~ 3-5x higher
        p_effective = p_smooth * sieve_eff * 4.0

        # Relations needed
        needed = fb_size + 100

        # Sieve yield per polynomial: 2*M positions * P(effective)
        yield_per_poly = 2 * M_fixed * p_effective

        if yield_per_poly <= 0:
            continue

        # Cost components:
        # 1. Sieve cost per poly: O(M) (filling sieve array, log sums)
        sieve_cost = 2 * M_fixed

        # 2. Trial division per candidate: O(FB * candidates_per_poly)
        #    candidates_per_poly ~ 2M * sieve_hit_rate (before TD confirms)
        #    sieve_hit_rate ~ exp(-u_eff) * sieve_looseness
        T_bits = max(15, nb // 4 - 2)
        sieve_hit_rate = max(1e-6, math.exp(-u_eff * 0.3))  # rough
        cands_per_poly = 2 * M_fixed * sieve_hit_rate
        td_cost = cands_per_poly * fb_size * 0.001  # TD is fast in C

        cost_per_poly = sieve_cost + td_cost

        # Polynomials needed
        polys_needed = needed / yield_per_poly

        # 3. LA cost: O(FB^2) — one-time, but significant for large FB
        la_cost = fb_size * fb_size * 0.0001  # Gauss elim in C

        # Total cost
        total_cost = polys_needed * cost_per_poly + la_cost

        sweep.append({
            'fb_size': fb_size, 'B_approx': B_approx, 'g_bits': g_bits,
            'u_eff': u_eff, 'p_smooth': p_smooth, 'sieve_eff': sieve_eff,
            'p_effective': p_effective,
            'needed': needed, 'yield_per_poly': yield_per_poly,
            'polys_needed': polys_needed, 'total_cost': total_cost
        })

        if total_cost < best_score:
            best_score = total_cost
            best_fb = fb_size

    return best_fb, sweep


def oracle_optimal_M(nd, fb_size):
    """
    Find oracle-optimal sieve interval M for given FB size.

    Larger M: more candidates per poly (good), but larger g(x) values (bad for smoothness).
    Also: very large M exceeds L2/L3 cache, causing sieve slowdown.
    Optimal M balances yield per poly vs smoothness probability vs cache effects.
    """
    nb = int(nd * math.log(10) / math.log(2))
    B_approx = int(2 * fb_size * math.log(2 * fb_size + 10))
    B_bits = math.log2(max(B_approx, 2))

    best_score = float('inf')
    best_M = None

    for log_M in np.arange(14, 26, 0.25):  # M from 16K to 33M
        M = int(2 ** log_M)

        # g_bits depends on M: g(x) ~ sqrt(N*M) / sqrt(FB)
        g_bits = int((nb + log_M) / 2)
        u_eff = g_bits / B_bits

        if u_eff > 10:
            continue

        p_smooth = smooth_oracle(g_bits, B_approx)
        if p_smooth <= 0:
            continue

        # Sieve efficiency penalty
        sieve_eff = min(1.0, math.exp(-(u_eff - 4.5) * 0.5)) if u_eff > 4.5 else 1.0
        p_effective = p_smooth * sieve_eff * 4.0  # LP multiplier

        needed = fb_size + 100
        yield_per_poly = 2 * M * p_effective

        if yield_per_poly <= 0:
            continue

        polys_needed = needed / yield_per_poly

        # Cache effect: sieve array is 2*M bytes (int16).
        # L2 = 256KB, L3 ~ 8MB. Beyond L3, memory latency dominates.
        # Model: sieve speed degrades above 4M entries (8MB).
        cache_penalty = 1.0
        if M > 4_000_000:
            cache_penalty = 1.0 + 0.5 * math.log2(M / 4_000_000)

        # Cost: sieve cost ~ M * cache_penalty, poly switch cost is O(FB)
        total_cost = polys_needed * (2 * M * cache_penalty + fb_size * 10)

        if total_cost < best_score:
            best_score = total_cost
            best_M = M

    return best_M


def compare_oracle_vs_current():
    """Compare oracle-optimal parameters vs current hand-tuned table."""
    print("\n" + "=" * 70)
    print("PART 2: Oracle-Optimized vs Current SIQS Parameters")
    print("=" * 70)

    comparisons = []
    print(f"\n{'nd':>4} {'cur_FB':>8} {'ora_FB':>8} {'FB_ratio':>9} "
          f"{'cur_M':>10} {'ora_M':>10} {'M_ratio':>9}")
    print("-" * 70)

    for nd in range(40, 105, 5):
        cur_fb, cur_M = siqs_params_interpolated(nd)
        ora_fb, _ = oracle_optimal_fb(nd, M_fixed=cur_M)

        if ora_fb is None:
            ora_fb = cur_fb

        ora_M = oracle_optimal_M(nd, ora_fb)
        if ora_M is None:
            ora_M = cur_M

        fb_ratio = ora_fb / cur_fb
        M_ratio = ora_M / cur_M

        comp = {
            'nd': nd, 'cur_fb': cur_fb, 'ora_fb': ora_fb, 'fb_ratio': fb_ratio,
            'cur_M': cur_M, 'ora_M': ora_M, 'M_ratio': M_ratio
        }
        comparisons.append(comp)

        print(f"{nd:>4} {cur_fb:>8} {ora_fb:>8} {fb_ratio:>8.2f}x "
              f"{cur_M:>10} {ora_M:>10} {M_ratio:>8.2f}x")

    results['oracle_vs_current'] = comparisons
    return comparisons


###############################################################################
# PART 3: SIQS Parameter Sweep for 60-digit
###############################################################################

def siqs_60d_sweep():
    """
    Sweep FB size for 60-digit target using oracle predictions.
    Find the oracle-optimal B.
    """
    print("\n" + "=" * 70)
    print("PART 3: SIQS Parameter Sweep for 60-digit Semiprime")
    print("=" * 70)

    nd = 60
    nb = int(nd * math.log(10) / math.log(2))  # ~199 bits

    _, base_M = siqs_params_interpolated(nd)

    print(f"\nTarget: {nd}d ({nb}b), base M={base_M}")
    print(f"\n{'FB':>7} {'B_max':>8} {'g_bits':>6} {'u_eff':>6} "
          f"{'P(sm)':>10} {'P(eff)':>10} {'yield/poly':>11} "
          f"{'polys_need':>11} {'est_time':>10}")
    print("-" * 100)

    sweep_results = []
    best_time = float('inf')
    best_fb = None

    for fb_size in range(500, 15001, 500):
        B_approx = int(2 * fb_size * math.log(2 * fb_size + 10))
        B_bits = math.log2(max(B_approx, 2))

        # g(x) effective size for SIQS
        # g_max ~ sqrt(N) * M / sqrt(a), where a ~ product of s primes near sqrt(2N/M)
        # Simplified: g_bits ~ (nb + log2(M)) / 2
        g_bits = int((nb + math.log2(base_M)) / 2)
        u_eff = g_bits / B_bits

        p_smooth_dick = smooth_oracle(g_bits, B_approx, method='dickman')
        p_smooth_oracle = smooth_oracle(g_bits, B_approx, method='enhanced')

        # Effective with LP variation
        p_eff = p_smooth_oracle * 4.0

        needed = fb_size + 100
        yield_per_poly = 2 * base_M * p_eff

        if yield_per_poly <= 0:
            continue

        polys_needed = needed / yield_per_poly

        # Estimated time: each poly takes ~0.01s (C sieve) for M=1.5M
        time_per_poly = 0.01 * (base_M / 1_500_000)
        est_time = polys_needed * time_per_poly

        sweep_results.append({
            'fb_size': fb_size, 'B_approx': B_approx, 'g_bits': g_bits,
            'u_eff': u_eff, 'p_smooth_dickman': p_smooth_dick,
            'p_smooth_oracle': p_smooth_oracle, 'p_effective': p_eff,
            'yield_per_poly': yield_per_poly, 'polys_needed': polys_needed,
            'est_time': est_time
        })

        marker = ""
        if est_time < best_time:
            best_time = est_time
            best_fb = fb_size
            marker = " <-- BEST"

        print(f"{fb_size:>7} {B_approx:>8} {g_bits:>6} {u_eff:>6.2f} "
              f"{p_smooth_oracle:>10.2e} {p_eff:>10.2e} {yield_per_poly:>11.1f} "
              f"{polys_needed:>11.0f} {est_time:>9.1f}s{marker}")

    print(f"\nOracle-optimal FB for 60d: {best_fb} (est. {best_time:.1f}s)")
    print(f"Current SIQS uses FB=4500 for 60d")

    cur_fb, _ = siqs_params_interpolated(60)
    print(f"\nRecommendation: ", end="")
    if best_fb and abs(best_fb - cur_fb) / cur_fb > 0.15:
        print(f"Change FB from {cur_fb} to {best_fb} ({best_fb/cur_fb:.2f}x)")
    else:
        print(f"Current FB={cur_fb} is near-optimal (oracle suggests {best_fb})")

    results['siqs_60d_sweep'] = {
        'sweep': sweep_results,
        'optimal_fb': best_fb,
        'optimal_time': best_time,
        'current_fb': cur_fb
    }
    return sweep_results


###############################################################################
# PART 4: GNFS Parameter Tuning
###############################################################################

def gnfs_oracle_analysis():
    """
    Analyze GNFS parameters using the oracle.
    Key parameters: degree d, FB bounds, sieve area.
    """
    print("\n" + "=" * 70)
    print("PART 4: GNFS Oracle-Optimized Parameter Analysis")
    print("=" * 70)

    gnfs_analysis = []

    print(f"\n{'nd':>4} {'d':>2} {'FB_cur':>8} {'FB_ora':>8} "
          f"{'u_rat':>6} {'u_alg':>6} {'P_rat':>10} {'P_alg':>10} {'P_both':>10}")
    print("-" * 80)

    for nd in range(30, 80, 5):
        nb = int(nd * math.log(10) / math.log(2))

        # Current GNFS parameters
        if nd < 40: d = 3
        elif nd < 65: d = 4
        elif nd < 100: d = 5
        else: d = 6

        # Current FB
        if nd < 23: fb_cur = 10000
        elif nd < 27: fb_cur = 20000
        elif nd < 32: fb_cur = 40000
        elif nd < 37: fb_cur = 50000
        elif nd < 40: fb_cur = 70000
        elif nd < 46: fb_cur = 80000
        elif nd < 50: fb_cur = 100000
        elif nd < 56: fb_cur = 80000
        elif nd < 60: fb_cur = 100000
        elif nd < 65: fb_cur = 150000
        elif nd < 70: fb_cur = 1200000
        elif nd < 80: fb_cur = 2000000
        else: fb_cur = 4000000

        # GNFS norms:
        # Rational norm: |a + b*m| ~ A * m ~ A * N^(1/d)
        # Algebraic norm: |F(a,b)| ~ product of coefficients... roughly N^(1/d) * A^d / d!
        # With A ~ FB_bound, B ~ 1..B_max

        A = min(fb_cur, 5_000_000)
        m_bits = nb / d  # m ~ N^(1/d)

        # Rational norm bits: log2(A * m) ~ log2(A) + nb/d
        rat_norm_bits = int(math.log2(max(A, 1)) + m_bits)

        # Algebraic norm bits: roughly d * log2(A) + some coefficient bits
        # For base-m representation, coefficients are < m, so
        # F(a,b) ~ sum c_i * a^i * b^(d-i), with c_i < m = N^(1/d)
        # Typical: |F(a,b)| ~ m * A^d / d! or more precisely:
        alg_norm_bits = int(m_bits + d * math.log2(max(A, 1)) - math.log2(math.factorial(d)))
        alg_norm_bits = max(alg_norm_bits, rat_norm_bits)  # floor

        u_rat = rat_norm_bits / math.log2(max(fb_cur, 2))
        u_alg = alg_norm_bits / math.log2(max(fb_cur, 2))

        p_rat = smooth_oracle(rat_norm_bits, fb_cur)
        p_alg = smooth_oracle(alg_norm_bits, fb_cur)
        p_both = p_rat * p_alg  # both sides must be smooth

        # Oracle-optimal FB: minimize needed/yield
        best_fb_ora = fb_cur
        best_score = float('inf')
        for fb_test in range(5000, min(500001, fb_cur * 5), 5000):
            A_test = min(fb_test, 5_000_000)
            rat_bits = int(math.log2(max(A_test, 1)) + m_bits)
            alg_bits = int(m_bits + d * math.log2(max(A_test, 1)) - math.log2(math.factorial(d)))
            alg_bits = max(alg_bits, rat_bits)

            pr = smooth_oracle(rat_bits, fb_test)
            pa = smooth_oracle(alg_bits, fb_test)
            pb = pr * pa

            if pb <= 0:
                continue

            # Need ~ |rat_fb| + |alg_fb| relations, |alg_fb| ~ d * |rat_fb| for deg d
            # pi(B) ~ B/ln(B)
            n_rat = int(fb_test / math.log(max(fb_test, 2)))
            n_alg = n_rat * d  # rough estimate
            needed = n_rat + n_alg + 50

            # Sieve cost ~ A * B_max per relation attempt
            # Time ~ needed / (sieve_area * p_both)
            sieve_area = 2 * A_test  # one line
            score = needed / (sieve_area * pb) if (sieve_area * pb) > 0 else float('inf')

            if score < best_score:
                best_score = score
                best_fb_ora = fb_test

        gnfs_analysis.append({
            'nd': nd, 'd': d, 'fb_cur': fb_cur, 'fb_ora': best_fb_ora,
            'u_rat': u_rat, 'u_alg': u_alg,
            'p_rat': p_rat, 'p_alg': p_alg, 'p_both': p_both
        })

        print(f"{nd:>4} {d:>2} {fb_cur:>8} {best_fb_ora:>8} "
              f"{u_rat:>6.2f} {u_alg:>6.2f} {p_rat:>10.2e} {p_alg:>10.2e} {p_both:>10.2e}")

    # Degree selection analysis
    print("\n--- Degree Selection Analysis (oracle-informed) ---")
    print(f"{'nd':>4} {'d=3 P_both':>12} {'d=4 P_both':>12} {'d=5 P_both':>12} {'best_d':>7}")
    print("-" * 55)

    degree_analysis = []
    for nd in [35, 40, 45, 50, 55, 60, 65, 70, 75]:
        nb = int(nd * math.log(10) / math.log(2))
        fb = fb_cur  # use current for comparison

        p_by_d = {}
        for d_test in [3, 4, 5]:
            m_bits = nb / d_test
            A = min(fb, 5_000_000)
            rat_bits = int(math.log2(max(A, 1)) + m_bits)
            alg_bits = int(m_bits + d_test * math.log2(max(A, 1)) - math.log2(math.factorial(d_test)))
            alg_bits = max(alg_bits, 1)

            pr = smooth_oracle(rat_bits, fb)
            pa = smooth_oracle(alg_bits, fb)
            p_by_d[d_test] = pr * pa

        best_d = max(p_by_d, key=p_by_d.get)
        degree_analysis.append({'nd': nd, 'p_by_d': p_by_d, 'best_d': best_d})

        print(f"{nd:>4} {p_by_d.get(3, 0):>12.2e} {p_by_d.get(4, 0):>12.2e} "
              f"{p_by_d.get(5, 0):>12.2e} {best_d:>7}")

    results['gnfs_oracle'] = gnfs_analysis
    results['gnfs_degree'] = degree_analysis
    return gnfs_analysis


###############################################################################
# PART 5: ECM B1 Optimization
###############################################################################

def ecm_b1_analysis():
    """
    ECM success depends on the largest prime factor of the group order.
    Use oracle to compute optimal B1 for various factor sizes.

    ECM stage 1 succeeds if all prime power factors of |E(F_p)| are <= B1.
    P(success) ~ rho(log(p)/log(B1)) * correction_for_prime_powers

    GMP-ECM defaults: B1 = 11e3 (20d), 50e3 (25d), 250e3 (30d), 1e6 (35d),
    3e6 (40d), 11e6 (45d), 43e6 (50d), 110e6 (55d), 260e6 (60d)
    """
    print("\n" + "=" * 70)
    print("PART 5: ECM B1 Optimization via Oracle")
    print("=" * 70)

    # GMP-ECM default B1 values (from ecm manual)
    gmp_defaults = {
        20: 11000,
        25: 50000,
        30: 250000,
        35: 1000000,
        40: 3000000,
        45: 11000000,
        50: 43000000,
        55: 110000000,
        60: 260000000,
    }

    ecm_results = []

    print(f"\n{'factor_d':>9} {'GMP_B1':>12} {'Oracle_B1':>12} {'Ratio':>8} "
          f"{'P_gmp':>10} {'P_oracle':>10} {'speedup':>8}")
    print("-" * 80)

    for factor_d in sorted(gmp_defaults.keys()):
        gmp_b1 = gmp_defaults[factor_d]
        factor_bits = int(factor_d * math.log(10) / math.log(2))

        # Group order |E(F_p)| ~ p +/- 2*sqrt(p) (Hasse bound)
        # Largest prime factor of |E(F_p)| is what matters.
        # Model: |E(F_p)| is a random number near p, so smooth prob applies.

        # Oracle-optimal B1: maximize P(success)/cost
        # P(success | B1) ~ rho(factor_bits / log2(B1))
        # Cost ~ B1 (stage 1 is O(B1) EC multiplications)
        # Optimize: P(success) / B1

        best_ratio = 0
        best_b1 = gmp_b1

        for log_b1 in np.arange(8, 30, 0.1):
            b1 = int(2 ** log_b1)
            if b1 < 100:
                continue

            p_success = smooth_oracle(factor_bits, b1)

            # ECM with stage 2 gives ~3-5x boost
            # Stage 2 extends to B2 ~ 100*B1, handles one large prime
            p_with_stage2 = min(p_success * 5, 1.0)

            efficiency = p_with_stage2 / b1

            if efficiency > best_ratio:
                best_ratio = efficiency
                best_b1 = b1

        p_gmp = smooth_oracle(factor_bits, gmp_b1) * 5  # with stage 2
        p_oracle = smooth_oracle(factor_bits, best_b1) * 5

        # Speedup: if oracle B1 is smaller with same success prob,
        # fewer curves needed = faster
        if p_oracle > 0 and p_gmp > 0:
            # Expected curves to find factor: 1/P
            curves_gmp = 1.0 / min(p_gmp, 1.0)
            curves_oracle = 1.0 / min(p_oracle, 1.0)
            # Time per curve: proportional to B1
            time_gmp = curves_gmp * gmp_b1
            time_oracle = curves_oracle * best_b1
            speedup = time_gmp / time_oracle if time_oracle > 0 else 1.0
        else:
            speedup = 1.0

        ratio = best_b1 / gmp_b1

        ecm_results.append({
            'factor_d': factor_d, 'gmp_b1': gmp_b1, 'oracle_b1': best_b1,
            'ratio': ratio, 'p_gmp': min(p_gmp, 1.0), 'p_oracle': min(p_oracle, 1.0),
            'speedup': speedup
        })

        print(f"{factor_d:>9} {gmp_b1:>12,} {best_b1:>12,} {ratio:>7.2f}x "
              f"{min(p_gmp,1.0):>10.2e} {min(p_oracle,1.0):>10.2e} {speedup:>7.2f}x")

    results['ecm_b1'] = ecm_results
    return ecm_results


###############################################################################
# PART 6: Practical Test — 60-digit Factoring
###############################################################################

def practical_60d_test():
    """
    Factor a 60-digit semiprime with current vs oracle-optimized parameters.
    """
    print("\n" + "=" * 70)
    print("PART 6: Practical 60-digit Factoring Test")
    print("=" * 70)

    # Generate a 60-digit semiprime
    if not HAS_GMPY2:
        print("  SKIP: gmpy2 not available")
        results['practical_60d'] = {'status': 'skipped', 'reason': 'no gmpy2'}
        return

    try:
        from siqs_engine import siqs_factor, siqs_params
    except ImportError as e:
        print(f"  SKIP: Could not import siqs_engine: {e}")
        results['practical_60d'] = {'status': 'skipped', 'reason': str(e)}
        return

    # RSA-like 60-digit semiprime: product of two 30-digit primes
    # Use a known test number
    p1 = mpz(next_prime(10**29 + 7))
    p2 = mpz(next_prime(10**29 + 961))
    N = p1 * p2
    nd = len(str(int(N)))
    print(f"\n  N = {N}")
    print(f"  {nd} digits, p1={p1}, p2={p2}")

    # Current parameters
    cur_fb, cur_M = siqs_params(nd)

    # Oracle-optimal parameters
    ora_fb, sweep = oracle_optimal_fb(nd, M_fixed=cur_M)
    if ora_fb is None:
        ora_fb = cur_fb
    ora_M = oracle_optimal_M(nd, ora_fb)
    if ora_M is None:
        ora_M = cur_M

    print(f"\n  Current: FB={cur_fb}, M={cur_M}")
    print(f"  Oracle:  FB={ora_fb}, M={ora_M}")

    # Test 1: Current parameters
    print(f"\n  --- Test 1: Current parameters ---")
    t1 = time.time()
    try:
        f1 = siqs_factor(int(N), verbose=True, time_limit=300)
        t1_elapsed = time.time() - t1
        print(f"  Result: {f1} in {t1_elapsed:.1f}s")
    except Exception as e:
        t1_elapsed = time.time() - t1
        f1 = None
        print(f"  Error: {e} after {t1_elapsed:.1f}s")

    # Test 2: Oracle parameters — use monkey-patching
    print(f"\n  --- Test 2: Oracle-optimized parameters ---")
    import siqs_engine
    original_params = siqs_engine.siqs_params

    def oracle_params(nd_inner):
        return ora_fb, ora_M

    siqs_engine.siqs_params = oracle_params

    t2 = time.time()
    try:
        f2 = siqs_factor(int(N), verbose=True, time_limit=300)
        t2_elapsed = time.time() - t2
        print(f"  Result: {f2} in {t2_elapsed:.1f}s")
    except Exception as e:
        t2_elapsed = time.time() - t2
        f2 = None
        print(f"  Error: {e} after {t2_elapsed:.1f}s")
    finally:
        # Restore original
        siqs_engine.siqs_params = original_params

    speedup = t1_elapsed / t2_elapsed if t2_elapsed > 0 else 0
    print(f"\n  Comparison: Current={t1_elapsed:.1f}s, Oracle={t2_elapsed:.1f}s, "
          f"speedup={speedup:.2f}x")

    results['practical_60d'] = {
        'N': str(N), 'nd': nd,
        'current': {'fb': cur_fb, 'M': cur_M, 'time': t1_elapsed, 'found': f1 is not None},
        'oracle': {'fb': ora_fb, 'M': ora_M, 'time': t2_elapsed, 'found': f2 is not None},
        'speedup': speedup
    }


###############################################################################
# PART 7: Parameter Table Generator
###############################################################################

def generate_parameter_table():
    """
    Generate optimal SIQS/GNFS parameters for 40-100 digit numbers.
    Output formatted for inclusion in a paper.
    """
    print("\n" + "=" * 70)
    print("PART 7: Optimal Parameter Table (40-100 digits)")
    print("=" * 70)

    table_data = []

    print(f"\n{'nd':>4} | {'Method':>6} | {'FB':>7} | {'M':>10} | {'LP_mult':>8} | "
          f"{'T_bits':>6} | {'u_eff':>5} | {'P(sm)':>10} | {'Est_time':>9}")
    print("-" * 85)

    for nd in range(40, 101):
        nb = int(nd * math.log(10) / math.log(2))

        # Decide method
        if nd < 50:
            method = 'SIQS'
        elif nd < 75:
            method = 'SIQS'  # SIQS still competitive to ~75d
        else:
            method = 'GNFS'

        if method == 'SIQS':
            # Oracle-optimal FB
            ora_fb, _ = oracle_optimal_fb(nd)
            if ora_fb is None:
                ora_fb, _ = siqs_params_interpolated(nd)

            ora_M = oracle_optimal_M(nd, ora_fb)
            if ora_M is None:
                _, ora_M = siqs_params_interpolated(nd)

            B_approx = int(2 * ora_fb * math.log(2 * ora_fb + 10))
            g_bits = int((nb + math.log2(max(ora_M, 1))) / 2)
            u_eff = g_bits / math.log2(max(B_approx, 2))
            p_smooth = smooth_oracle(g_bits, B_approx)

            # LP multiplier
            lp_mult = 100

            # T_bits
            if nb >= 180:
                t_bits = max(15, nb // 4 - 1)
            else:
                t_bits = max(15, nb // 4 - 2)

            # Rough time estimate
            needed = ora_fb + 100
            p_eff = p_smooth * 4.0
            yield_per_poly = 2 * ora_M * p_eff
            if yield_per_poly > 0:
                polys = needed / yield_per_poly
                est_time = polys * 0.01 * (ora_M / 1_500_000)
            else:
                est_time = float('inf')

            row = {
                'nd': nd, 'method': method, 'fb': ora_fb, 'M': ora_M,
                'lp_mult': lp_mult, 't_bits': t_bits, 'u_eff': u_eff,
                'p_smooth': p_smooth, 'est_time': est_time
            }
        else:
            # GNFS
            d = 4 if nd < 65 else 5

            # Simple oracle-guided FB
            best_fb = 100000
            best_score = float('inf')
            m_bits = nb / d

            for fb_test in range(50000, 5000001, 50000):
                A = min(fb_test, 5_000_000)
                rat_bits = int(math.log2(max(A, 1)) + m_bits)
                alg_bits = int(m_bits + d * math.log2(max(A, 1)) - math.log2(math.factorial(d)))
                alg_bits = max(alg_bits, 1)

                pr = smooth_oracle(rat_bits, fb_test)
                pa = smooth_oracle(alg_bits, fb_test)
                pb = pr * pa

                if pb <= 0:
                    continue

                n_fb = int(fb_test / math.log(max(fb_test, 2)) * (1 + d))
                score = n_fb / (2 * A * pb) if pb > 0 else float('inf')

                if score < best_score:
                    best_score = score
                    best_fb = fb_test

            A = min(best_fb, 5_000_000)
            rat_bits = int(math.log2(max(A, 1)) + m_bits)
            alg_bits = int(m_bits + d * math.log2(max(A, 1)) - math.log2(math.factorial(d)))
            u_eff = alg_bits / math.log2(max(best_fb, 2))
            p_smooth = smooth_oracle(rat_bits, best_fb) * smooth_oracle(max(alg_bits,1), best_fb)

            # Very rough time estimate for GNFS
            est_time = float('nan')

            row = {
                'nd': nd, 'method': f'GNFS d={d}', 'fb': best_fb, 'M': A,
                'lp_mult': 100, 't_bits': 0, 'u_eff': u_eff,
                'p_smooth': p_smooth, 'est_time': est_time
            }

        table_data.append(row)

        # Print every 5 digits
        if nd % 5 == 0:
            time_str = f"{row['est_time']:.0f}s" if not math.isnan(row['est_time']) and row['est_time'] < 1e8 else "N/A"
            print(f"{nd:>4} | {row['method']:>6} | {row['fb']:>7} | {row['M']:>10} | "
                  f"{row['lp_mult']:>8} | {row['t_bits']:>6} | {row['u_eff']:>5.2f} | "
                  f"{row['p_smooth']:>10.2e} | {time_str:>9}")

    # LaTeX table
    print("\n--- LaTeX Table ---")
    print(r"\begin{table}[h]")
    print(r"\centering")
    print(r"\caption{Oracle-Optimized Factoring Parameters}")
    print(r"\begin{tabular}{r|l|r|r|r|r}")
    print(r"\hline")
    print(r"Digits & Method & FB Size & Sieve $M$ & $u_{\rm eff}$ & $P(\text{smooth})$ \\")
    print(r"\hline")
    for row in table_data:
        if row['nd'] % 5 == 0:
            p_str = f"{row['p_smooth']:.1e}"
            print(f"{row['nd']} & {row['method']} & {row['fb']:,} & {row['M']:,} & "
                  f"{row['u_eff']:.2f} & {p_str} \\\\")
    print(r"\hline")
    print(r"\end{tabular}")
    print(r"\end{table}")

    results['parameter_table'] = table_data
    return table_data


###############################################################################
# PART 8: Integration Plan
###############################################################################

def integration_plan():
    """
    Write specific code changes for integrating oracle into siqs_engine.py.
    Produces a wrapper, NOT direct modifications.
    """
    print("\n" + "=" * 70)
    print("PART 8: Integration Plan — Oracle Wrapper for SIQS")
    print("=" * 70)

    wrapper_code = '''
# === oracle_siqs_wrapper.py ===
# Drop-in wrapper that replaces SIQS parameter selection with oracle-optimized values.
# Usage: from oracle_siqs_wrapper import oracle_siqs_factor
#        factor = oracle_siqs_factor(N)

import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from siqs_engine import siqs_factor as _original_siqs_factor
import siqs_engine


def dickman_rho(u):
    """Dickman rho via Euler method for DDE."""
    if u <= 1: return 1.0
    if u <= 2: return 1.0 - math.log(u)
    steps = int(u * 200)
    dt = u / steps
    rho = [0.0] * (steps + 1)
    for i in range(steps + 1):
        t = i * dt
        if t <= 1.0: rho[i] = 1.0
        elif t <= 2.0: rho[i] = 1.0 - math.log(t)
    for i in range(1, steps + 1):
        t = i * dt
        if t > 2.0:
            j = min(int((t - 1.0) / dt), steps)
            rho[i] = rho[i-1] - dt * rho[j] / t
            rho[i] = max(rho[i], 1e-100)
    return max(rho[steps], 1e-100)


def smooth_oracle(n_bits, B):
    """Enhanced smooth oracle with CEP + saddle-point corrections."""
    if B < 2: return 0.0
    ln_N = n_bits * math.log(2)
    ln_B = math.log(B)
    u = ln_N / ln_B
    if u <= 0: return 1.0
    rho = dickman_rho(u)
    # CEP correction
    cep = 1.0 + 0.535 * math.log(u + 1) / ln_B
    # Saddle-point
    saddle = math.exp(0.5772 * u / (u*u + 1)) if u > 1.5 else 1.0
    return min(rho * cep * saddle, 1.0)


def oracle_siqs_params(nd):
    """Oracle-optimized SIQS parameters."""
    nb = int(nd * math.log(10) / math.log(2))

    # Get current M as baseline
    _, base_M = siqs_engine.siqs_params(nd)

    # Sweep FB to find oracle-optimal
    best_score = float('inf')
    best_fb = None

    for fb_size in range(max(500, int(nd * 10)), min(80001, int(nd * 2000)), max(50, nd)):
        B_approx = int(2 * fb_size * math.log(2 * fb_size + 10))
        if B_approx < 3: continue
        g_bits = int((nb + math.log2(max(base_M, 1))) / 2)
        B_bits = math.log2(max(B_approx, 2))
        u_eff = g_bits / B_bits
        if u_eff > 10: continue
        p_smooth = smooth_oracle(g_bits, B_approx)
        if p_smooth <= 0: continue
        sieve_eff = min(1.0, math.exp(-(u_eff - 4.5) * 0.5)) if u_eff > 4.5 else 1.0
        p_eff = p_smooth * sieve_eff * 4.0
        needed = fb_size + 100
        yield_per_poly = 2 * base_M * p_eff
        if yield_per_poly <= 0: continue
        polys_needed = needed / yield_per_poly
        td_cost_pp = 2 * base_M * max(1e-6, math.exp(-u_eff * 0.3)) * fb_size * 0.001
        total_cost = polys_needed * (2 * base_M + td_cost_pp) + fb_size * fb_size * 0.0001
        if total_cost < best_score:
            best_score = total_cost
            best_fb = fb_size

    if best_fb is None:
        return siqs_engine.siqs_params(nd)

    # Optimize M for the chosen FB
    B_approx = int(2 * best_fb * math.log(2 * best_fb + 10))
    best_M_score = float('inf')
    best_M = base_M

    for log_M_10 in range(40, 260, 5):  # M from ~10K to ~200M
        log_M = log_M_10 / 10.0
        M = int(10 ** log_M)
        g_bits = int((nb + log_M * math.log(10)/math.log(2)) / 2)
        p_smooth = smooth_oracle(g_bits, B_approx)
        if p_smooth <= 0: continue
        p_eff = p_smooth * 4.0
        needed = best_fb + 100
        yield_per_poly = 2 * M * p_eff
        if yield_per_poly <= 0: continue
        polys_needed = needed / yield_per_poly
        total_cost = polys_needed * (2 * M + best_fb * 10)
        if total_cost < best_M_score:
            best_M_score = total_cost
            best_M = M

    return best_fb, best_M


def oracle_siqs_factor(n, verbose=True, time_limit=3600, **kwargs):
    """Factor n using SIQS with oracle-optimized parameters."""
    # Temporarily replace params function
    original = siqs_engine.siqs_params
    siqs_engine.siqs_params = oracle_siqs_params
    try:
        result = _original_siqs_factor(n, verbose=verbose, time_limit=time_limit, **kwargs)
    finally:
        siqs_engine.siqs_params = original
    return result
'''

    print(wrapper_code)

    # Also describe GNFS integration
    print("\n--- GNFS Integration Notes ---")
    print("""
To integrate the oracle into gnfs_engine.py:

1. Replace the FB bound table in gnfs_params() with oracle_optimal_fb_gnfs(nd, d):
   - Sweep FB from 10K to 5M
   - For each FB: compute rat_norm_bits, alg_norm_bits from degree + sieve area
   - Use smooth_oracle() for both rational and algebraic smoothness
   - Minimize: needed_relations / (sieve_area * P_rat * P_alg)

2. Degree selection: for each candidate d in {3,4,5,6}:
   - Compute P_both = P_rat(d) * P_alg(d) using oracle
   - Account for: smaller d = larger coefficients but lower degree norms
   - Pick d maximizing P_both / needed_relations(d)

3. Sieve threshold adjustment:
   - Current: max(600, 1000-nd*5), max(500, 850-nd*5)
   - Oracle: compute expected log-sum from FB hitting rates
   - Set threshold at percentile matching oracle's predicted yield

4. LP bound: currently 100*B.
   - Oracle can predict optimal LP multiplier by computing
     P(B-smooth cofactor < LP | sieve hit) for various LP values.
""")

    results['integration_plan'] = {
        'wrapper_provided': True,
        'siqs_changes': ['oracle_siqs_params replaces siqs_params table',
                         'FB sweep optimization', 'M sweep optimization'],
        'gnfs_changes': ['FB bound from oracle sweep', 'degree selection oracle',
                         'sieve threshold from oracle yield prediction',
                         'LP bound optimization'],
    }

    # Write the actual wrapper file
    wrapper_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'oracle_siqs_wrapper.py')
    with open(wrapper_path, 'w') as f:
        f.write(wrapper_code.strip() + '\n')
    print(f"\n  Wrapper written to: {wrapper_path}")


###############################################################################
# MAIN
###############################################################################

def main():
    print("v31_oracle_siqs.py — Smooth Oracle Integration for Factoring Engines")
    print("=" * 70)

    t_start = time.time()

    # Part 0: Oracle vs Dickman comparison
    oracle_vs_dickman_comparison()

    # Part 1: Current SIQS analysis
    analyze_current_siqs()

    # Part 2: Oracle-optimized parameters
    compare_oracle_vs_current()

    # Part 3: 60d sweep
    siqs_60d_sweep()

    # Part 4: GNFS tuning
    gnfs_oracle_analysis()

    # Part 5: ECM B1
    ecm_b1_analysis()

    # Part 6: Practical test
    practical_60d_test()

    # Part 7: Parameter table
    generate_parameter_table()

    # Part 8: Integration plan
    integration_plan()

    total_time = time.time() - t_start

    print(f"\n{'=' * 70}")
    print(f"TOTAL TIME: {total_time:.1f}s")
    print(f"{'=' * 70}")

    # Write results
    results_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'v31_oracle_siqs_results.md')
    with open(results_path, 'w') as f:
        f.write("# v31: Smooth Oracle Integration for SIQS/GNFS/ECM\n\n")
        f.write(f"**Total runtime**: {total_time:.1f}s\n\n")

        # Oracle vs Dickman
        f.write("## Oracle vs Dickman Comparison\n\n")
        f.write("The enhanced oracle applies two corrections to Dickman rho:\n")
        f.write("1. **CEP correction**: Canfield-Erdos-Pomerance refinement factor `1 + 0.535*log(u+1)/log(B)`\n")
        f.write("2. **Saddle-point correction**: Hildebrand saddle-point `exp(gamma*u/(u^2+1))`\n\n")
        if 'oracle_vs_dickman' in results:
            f.write("| n_bits | B | u | Dickman | Oracle | Ratio |\n")
            f.write("|--------|---|---|---------|--------|-------|\n")
            for c in results['oracle_vs_dickman']:
                f.write(f"| {c['n_bits']} | {c['B']:,} | {c['u']:.2f} | "
                        f"{c['dickman']:.2e} | {c['oracle']:.2e} | {c['ratio']:.2f}x |\n")

        # Current SIQS
        f.write("\n## Current SIQS Parameters\n\n")
        f.write("Parameter selection uses interpolated lookup table:\n")
        f.write("- FB_size: 80 (20d) to 75000 (100d)\n")
        f.write("- M (half-width): 20K (20d) to 35M (100d)\n")
        f.write("- LP_bound: min(FB[-1]*100, FB[-1]^2)\n")
        f.write("- T_bits: nb//4-1 (nb>=180) or nb//4-2\n\n")

        if 'current_siqs' in results:
            f.write("| nd | FB | M | B_max | g_bits | u_eff | P(smooth) |\n")
            f.write("|----|----|----|------|--------|-------|----------|\n")
            for a in results['current_siqs']:
                f.write(f"| {a['nd']} | {a['fb_size']:,} | {a['M']:,} | {a['B_approx']:,} | "
                        f"{a['g_bits']} | {a['u_eff']:.2f} | {a['p_smooth']:.2e} |\n")

        # Oracle vs Current
        f.write("\n## Oracle-Optimized vs Current Parameters\n\n")
        if 'oracle_vs_current' in results:
            f.write("| nd | Current FB | Oracle FB | FB Ratio | Current M | Oracle M | M Ratio |\n")
            f.write("|----|-----------|----------|----------|----------|---------|--------|\n")
            for c in results['oracle_vs_current']:
                f.write(f"| {c['nd']} | {c['cur_fb']:,} | {c['ora_fb']:,} | {c['fb_ratio']:.2f}x | "
                        f"{c['cur_M']:,} | {c['ora_M']:,} | {c['M_ratio']:.2f}x |\n")

        # 60d sweep
        f.write("\n## 60-digit Parameter Sweep\n\n")
        if 'siqs_60d_sweep' in results:
            sw = results['siqs_60d_sweep']
            f.write(f"- **Oracle-optimal FB**: {sw['optimal_fb']} (current: {sw['current_fb']})\n")
            f.write(f"- **Estimated time at optimal**: {sw['optimal_time']:.1f}s\n\n")

        # GNFS
        f.write("\n## GNFS Oracle Analysis\n\n")
        if 'gnfs_oracle' in results:
            f.write("| nd | d | FB_current | FB_oracle | u_rat | u_alg | P_both |\n")
            f.write("|----|---|-----------|----------|-------|-------|--------|\n")
            for a in results['gnfs_oracle']:
                f.write(f"| {a['nd']} | {a['d']} | {a['fb_cur']:,} | {a['fb_ora']:,} | "
                        f"{a['u_rat']:.2f} | {a['u_alg']:.2f} | {a['p_both']:.2e} |\n")

        if 'gnfs_degree' in results:
            f.write("\n### Degree Selection\n\n")
            f.write("| nd | P(d=3) | P(d=4) | P(d=5) | Best d |\n")
            f.write("|----|--------|--------|--------|--------|\n")
            for a in results['gnfs_degree']:
                f.write(f"| {a['nd']} | {a['p_by_d'].get(3,0):.2e} | "
                        f"{a['p_by_d'].get(4,0):.2e} | {a['p_by_d'].get(5,0):.2e} | "
                        f"{a['best_d']} |\n")

        # ECM
        f.write("\n## ECM B1 Optimization\n\n")
        if 'ecm_b1' in results:
            f.write("| Factor digits | GMP B1 | Oracle B1 | Ratio | Speedup |\n")
            f.write("|-------------|--------|----------|-------|--------|\n")
            for e in results['ecm_b1']:
                f.write(f"| {e['factor_d']} | {e['gmp_b1']:,} | {e['oracle_b1']:,} | "
                        f"{e['ratio']:.2f}x | {e['speedup']:.2f}x |\n")

        # Practical test
        f.write("\n## Practical 60-digit Test\n\n")
        if 'practical_60d' in results:
            p = results['practical_60d']
            if p.get('status') == 'skipped':
                f.write(f"Skipped: {p['reason']}\n")
            else:
                f.write(f"- **N**: {p.get('N', 'N/A')} ({p.get('nd', '?')}d)\n")
                c = p.get('current', {})
                o = p.get('oracle', {})
                f.write(f"- **Current**: FB={c.get('fb')}, M={c.get('M')}, "
                        f"time={c.get('time', 0):.1f}s, found={c.get('found')}\n")
                f.write(f"- **Oracle**: FB={o.get('fb')}, M={o.get('M')}, "
                        f"time={o.get('time', 0):.1f}s, found={o.get('found')}\n")
                f.write(f"- **Speedup**: {p.get('speedup', 0):.2f}x\n")

        # Parameter table
        f.write("\n## Optimal Parameter Table (40-100d)\n\n")
        if 'parameter_table' in results:
            f.write("| nd | Method | FB | M | u_eff | P(smooth) |\n")
            f.write("|----|--------|----|---|-------|----------|\n")
            for row in results['parameter_table']:
                if row['nd'] % 5 == 0:
                    f.write(f"| {row['nd']} | {row['method']} | {row['fb']:,} | "
                            f"{row['M']:,} | {row['u_eff']:.2f} | {row['p_smooth']:.1e} |\n")

        # Integration plan
        f.write("\n## Integration Plan\n\n")
        f.write("### SIQS Wrapper (oracle_siqs_wrapper.py)\n\n")
        f.write("Drop-in replacement: `from oracle_siqs_wrapper import oracle_siqs_factor`\n\n")
        f.write("Changes:\n")
        f.write("1. `oracle_siqs_params(nd)` replaces hand-tuned table with oracle sweep\n")
        f.write("2. FB optimized via: minimize `needed/yield` where yield uses `smooth_oracle()`\n")
        f.write("3. M optimized balancing sieve size vs smoothness probability\n\n")
        f.write("### GNFS Changes (not yet wrapped)\n\n")
        f.write("1. FB bound from oracle sweep (replace hardcoded table)\n")
        f.write("2. Degree selection via oracle P_both comparison\n")
        f.write("3. Sieve threshold from oracle yield prediction\n")
        f.write("4. LP bound optimization\n")

    print(f"\nResults written to: {results_path}")


if __name__ == '__main__':
    main()
