#!/usr/bin/env python3
"""
v34_giant_zeros_push.py — Push beyond 10^12 to find the highest possible zeros.
Continuation of v34_giant_zeros.py.
"""

import time
import math
import numpy as np
from mpmath import mp, mpf, mpc, pi as mppi, log as mplog
from mpmath import loggamma, im

mp.dps = 30

def riemann_siegel_theta(t):
    """theta(t) = Im(loggamma(1/4 + it/2)) - t/2 * log(pi)"""
    return float(im(loggamma(mpf('0.25') + mpc(0, t/2)))) - t/2 * math.log(math.pi)

def Z_function_rs(t):
    """Riemann-Siegel Z-function with numpy vectorization + remainder."""
    t_f = float(t)
    N = int(math.sqrt(t_f / (2 * math.pi)))
    if N < 1:
        N = 1

    theta = riemann_siegel_theta(t_f)

    ns = np.arange(1, N + 1, dtype=np.float64)
    phases = theta - t_f * np.log(ns)
    terms = np.cos(phases) / np.sqrt(ns)
    main_sum = 2.0 * np.sum(terms)

    # Riemann-Siegel remainder
    p = math.sqrt(t_f / (2 * math.pi)) - N
    cos_denom = math.cos(2 * math.pi * p)
    if abs(cos_denom) > 1e-10:
        C0 = math.cos(2 * math.pi * (p*p - p - 1.0/16.0)) / cos_denom
        remainder = (-1)**(N - 1) * (t_f / (2 * math.pi))**(-0.25) * C0
    else:
        remainder = 0.0

    return main_sum + remainder

def gram_point(n):
    """Find Gram point g_n where theta(g_n) = n * pi."""
    if n < 10:
        t = 10.0 + n * 2.0
    else:
        t = 2 * math.pi * math.exp(1 + math.log(n) - math.log(math.log(n + 2) + 1))
    target = n * math.pi
    for _ in range(100):
        theta = riemann_siegel_theta(t)
        deriv = math.log(t / (2 * math.pi)) / 2.0
        if abs(deriv) < 1e-30:
            break
        dt = (theta - target) / deriv
        t -= dt
        if abs(dt) < 1e-8:
            break
    return t

def find_zero_bisect(t_low, t_high, tol=1e-8, max_iter=80):
    """Bisect to find a zero of Z between t_low and t_high."""
    z_low = Z_function_rs(t_low)
    z_high = Z_function_rs(t_high)
    if z_low * z_high > 0:
        return None
    for _ in range(max_iter):
        t_mid = (t_low + t_high) / 2.0
        if t_high - t_low < tol:
            break
        z_mid = Z_function_rs(t_mid)
        if z_mid * z_low < 0:
            t_high = t_mid
            z_high = z_mid
        else:
            t_low = t_mid
            z_low = z_mid
    return (t_low + t_high) / 2.0

def N_of_T(T):
    """Number of zeros with 0 < Im(s) < T."""
    if T <= 0:
        return 0
    return T / (2 * math.pi) * math.log(T / (2 * math.pi * math.e)) + 7.0 / 8.0

def scan_gram_zeros(t_center, num_points, label=""):
    """Scan around t_center using Gram points to find zeros."""
    theta_center = riemann_siegel_theta(t_center)
    n_center = int(theta_center / math.pi)

    zeros_found = []
    t0 = time.time()

    gram_pts = []
    for i in range(num_points + 1):
        n = n_center - num_points // 2 + i
        if n < 0:
            continue
        gp = gram_point(n)
        gram_pts.append((n, gp))

    z_vals = []
    for n, gp in gram_pts:
        z = Z_function_rs(gp)
        z_vals.append((n, gp, z))

    for i in range(len(z_vals) - 1):
        n1, t1, z1 = z_vals[i]
        n2, t2, z2 = z_vals[i + 1]
        if z1 * z2 < 0:
            zero = find_zero_bisect(t1, t2)
            if zero is not None:
                ordinal = N_of_T(zero)
                zeros_found.append({'t': zero, 'ordinal': ordinal})

    elapsed = time.time() - t0

    if zeros_found:
        highest = max(zeros_found, key=lambda z: z['t'])
        print(f"  {label}: {len(zeros_found)} zeros, highest t = {highest['t']:.6f}, "
              f"ordinal ~{highest['ordinal']:,.0f}, time={elapsed:.1f}s")
    else:
        print(f"  {label}: NO zeros found ({elapsed:.1f}s)")

    return zeros_found, elapsed

# ════════════════════════════════════════════════════════════════
# PUSH BEYOND 10^12
# ════════════════════════════════════════════════════════════════
results = []
total_start = time.time()

heights = [
    (1e12, 10, "t=10^12 (TRILLION)"),
    (1e13, 8, "t=10^13 (10 TRILLION)"),
    (1e14, 6, "t=10^14 (100 TRILLION)"),
    (1e15, 5, "t=10^15 (QUADRILLION)"),
    (1e16, 4, "t=10^16 (10 QUADRILLION)"),
    (1e17, 3, "t=10^17"),
    (1e18, 3, "t=10^18 (QUINTILLION)"),
    (1e19, 3, "t=10^19"),
    (1e20, 3, "t=10^20"),
]

print("=" * 70)
print("  GIANT ZERO PUSH — Going beyond 10^12")
print("=" * 70)

for height, npts, label in heights:
    elapsed_total = time.time() - total_start
    if elapsed_total > 500:  # 500s budget
        print(f"\n  Time budget exhausted ({elapsed_total:.0f}s). Stopping.")
        break

    rs_terms = int(math.sqrt(height / (2 * math.pi)))
    print(f"\n  {label} — RS terms: {rs_terms:,}")

    # Check if numpy array would exceed ~1GB RAM
    mem_bytes = rs_terms * 8 * 3  # 3 arrays: ns, phases, terms
    mem_mb = mem_bytes / 1e6
    if mem_mb > 1500:
        print(f"    SKIP: would need {mem_mb:.0f}MB for RS arrays")
        continue

    zeros, elapsed = scan_gram_zeros(height, npts, label)
    if zeros:
        highest = max(zeros, key=lambda z: z['t'])
        results.append({
            'height': height, 't': highest['t'], 'ordinal': highest['ordinal'],
            'time': elapsed, 'label': label, 'count': len(zeros),
            'rs_terms': rs_terms
        })

# ════════════════════════════════════════════════════════════════
# CHUNKED RS for very large t (avoid huge arrays)
# ════════════════════════════════════════════════════════════════

def Z_function_rs_chunked(t, chunk_size=500000):
    """RS Z-function with chunked numpy to limit RAM."""
    t_f = float(t)
    N = int(math.sqrt(t_f / (2 * math.pi)))
    if N < 1:
        N = 1

    theta = riemann_siegel_theta(t_f)
    main_sum = 0.0

    for start in range(1, N + 1, chunk_size):
        end = min(start + chunk_size, N + 1)
        ns = np.arange(start, end, dtype=np.float64)
        phases = theta - t_f * np.log(ns)
        terms = np.cos(phases) / np.sqrt(ns)
        main_sum += np.sum(terms)

    main_sum *= 2.0

    p = math.sqrt(t_f / (2 * math.pi)) - N
    cos_denom = math.cos(2 * math.pi * p)
    if abs(cos_denom) > 1e-10:
        C0 = math.cos(2 * math.pi * (p*p - p - 1.0/16.0)) / cos_denom
        remainder = (-1)**(N - 1) * (t_f / (2 * math.pi))**(-0.25) * C0
    else:
        remainder = 0.0

    return main_sum + remainder

def scan_gram_zeros_chunked(t_center, num_points, label=""):
    """Gram scan using chunked RS for very high t."""
    theta_center = riemann_siegel_theta(t_center)
    n_center = int(theta_center / math.pi)

    zeros_found = []
    t0 = time.time()

    gram_pts = []
    for i in range(num_points + 1):
        n = n_center - num_points // 2 + i
        if n < 0:
            continue
        gp = gram_point(n)
        gram_pts.append((n, gp))

    z_vals = []
    for n, gp in gram_pts:
        z = Z_function_rs_chunked(gp)
        z_vals.append((n, gp, z))

    for i in range(len(z_vals) - 1):
        n1, t1, z1 = z_vals[i]
        n2, t2, z2 = z_vals[i + 1]
        if z1 * z2 < 0:
            # For bisection, use chunked too
            tl, th = t1, t2
            zl, zh = z1, z2
            for _ in range(50):
                tm = (tl + th) / 2.0
                if th - tl < 1e-6:
                    break
                zm = Z_function_rs_chunked(tm)
                if zm * zl < 0:
                    th, zh = tm, zm
                else:
                    tl, zl = tm, zm
            zero = (tl + th) / 2.0
            ordinal = N_of_T(zero)
            zeros_found.append({'t': zero, 'ordinal': ordinal})

    elapsed = time.time() - t0

    if zeros_found:
        highest = max(zeros_found, key=lambda z: z['t'])
        print(f"  {label}: {len(zeros_found)} zeros, highest t = {highest['t']:.6f}, "
              f"ordinal ~{highest['ordinal']:,.0f}, time={elapsed:.1f}s")
    else:
        print(f"  {label}: NO zeros found ({elapsed:.1f}s)")

    return zeros_found, elapsed


# Continue with chunked RS for heights where array would be too large
elapsed_total = time.time() - total_start
if elapsed_total < 500:
    chunked_heights = []
    for height, npts, label in heights:
        rs_terms = int(math.sqrt(height / (2 * math.pi)))
        mem_mb = rs_terms * 8 * 3 / 1e6
        if mem_mb > 1500:
            chunked_heights.append((height, npts, label))

    for height, npts, label in chunked_heights:
        elapsed_total = time.time() - total_start
        if elapsed_total > 500:
            break
        rs_terms = int(math.sqrt(height / (2 * math.pi)))
        print(f"\n  {label} (CHUNKED) — RS terms: {rs_terms:,}")
        zeros, elapsed = scan_gram_zeros_chunked(height, min(npts, 3), label + " [chunked]")
        if zeros:
            highest = max(zeros, key=lambda z: z['t'])
            results.append({
                'height': height, 't': highest['t'], 'ordinal': highest['ordinal'],
                'time': elapsed, 'label': label, 'count': len(zeros),
                'rs_terms': rs_terms
            })

# ════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ════════════════════════════════════════════════════════════════
total_time = time.time() - total_start

print("\n" + "=" * 70)
print("  FINAL RESULTS — Giant Zero Push")
print("=" * 70)

for r in results:
    exp = int(math.log10(r['height']))
    print(f"  10^{exp}: t = {r['t']:.6f}  ordinal ~{r['ordinal']:,.0f}  "
          f"RS terms={r['rs_terms']:,}  ({r['time']:.1f}s)")

if results:
    best = max(results, key=lambda r: r['t'])
    print(f"\n  === HIGHEST ZERO FOUND ===")
    print(f"  t = {best['t']:.10f}")
    print(f"  Ordinal: ~{best['ordinal']:,.0f}")
    print(f"  Height: 10^{math.log10(best['height']):.0f}")
    print(f"  RS terms: {best['rs_terms']:,}")
    print(f"  Time for this height: {best['time']:.1f}s")

print(f"\n  Total time: {total_time:.1f}s")

# Write combined results
with open("/home/raver1975/factor/.claude/worktrees/agent-a386e459/v34_push_results.json", "w") as f:
    import json
    json.dump(results, f, indent=2, default=str)
