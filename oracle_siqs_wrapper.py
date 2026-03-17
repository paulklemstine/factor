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
