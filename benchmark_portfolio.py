#!/usr/bin/env python3
"""
Benchmark: Old portfolio (rho + ECM_S1) vs New (rho + p-1 + p+1 + ECM_S1+S2)

Tests 50 random semiprimes:
  - 30d balanced factors
  - 30d with 1:10 factor ratio (unbalanced)
  - 40d balanced factors
"""

import gmpy2
from gmpy2 import mpz, is_prime, next_prime, gcd
import time
import random
import sys

sys.path.insert(0, '/home/raver1975/factor')

from resonance_v7 import (
    ecm_factor, pollard_pm1, williams_pp1, _SMALL_PRIMES
)


# ============================================================
# Pollard rho (Brent variant) — shared by both portfolios
# ============================================================
def pollard_rho(n, max_iter=5_000_000):
    """Brent's improvement of Pollard rho."""
    n = mpz(n)
    if n % 2 == 0:
        return 2
    for attempt in range(20):
        y = mpz(random.randint(1, int(n) - 1))
        c = mpz(random.randint(1, int(n) - 1))
        m = 256
        g, q, r = mpz(1), mpz(1), 1
        x = y
        while g == 1:
            x = y
            for _ in range(r):
                y = (y * y + c) % n
            k = 0
            while k < r and g == 1:
                ys = y
                for _ in range(min(m, r - k)):
                    y = (y * y + c) % n
                    q = q * abs(x - y) % n
                g = gcd(q, n)
                k += m
            r *= 2
            if r > max_iter:
                break
        if 1 < g < n:
            return int(g)
        if g == n:
            while True:
                ys = (ys * ys + c) % n
                g = gcd(abs(x - ys), n)
                if g > 1:
                    break
            if 1 < g < n:
                return int(g)
    return None


# ============================================================
# ECM Stage 1 only (the OLD portfolio version)
# ============================================================
def ecm_factor_s1_only(n, B1=1000000, curves=100, verbose=False):
    """ECM with Stage 1 only — the old implementation."""
    n = mpz(n)
    for c in range(curves):
        sigma = mpz(random.randint(6, 10**9))
        u = (sigma * sigma - 5) % n
        v = (4 * sigma) % n
        x = pow(u, 3, n)
        z = pow(v, 3, n)
        diff = (v - u) % n
        a24n = pow(diff, 3, n) * ((3*u+v) % n) % n
        a24d = 16 * x * v % n
        try:
            a24i = pow(int(a24d), -1, int(n))
        except Exception:
            g = gcd(a24d, n)
            if 1 < g < n:
                return int(g)
            continue
        a24 = a24n * a24i % n

        def md(px, pz):
            s = (px + pz) % n; d = (px - pz) % n
            ss = s * s % n; dd = d * d % n; dl = (ss - dd) % n
            return ss * dd % n, dl * (dd + a24 * dl % n) % n

        def ma(px, pz, qx, qz, dx, dz):
            u1 = (px + pz) * (qx - qz) % n
            v1 = (px - pz) * (qx + qz) % n
            return (u1 + v1) * (u1 + v1) % n * dz % n, (u1 - v1) * (u1 - v1) % n * dx % n

        def mm(k, px, pz):
            if k <= 1:
                return (px, pz) if k == 1 else (mpz(0), mpz(1))
            r0x, r0z = px, pz
            r1x, r1z = md(px, pz)
            for bit in bin(k)[3:]:
                if bit == '1':
                    r0x, r0z = ma(r0x, r0z, r1x, r1z, px, pz)
                    r1x, r1z = md(r1x, r1z)
                else:
                    r1x, r1z = ma(r0x, r0z, r1x, r1z, px, pz)
                    r0x, r0z = md(r0x, r0z)
            return r0x, r0z

        p = 2
        while p <= B1:
            pp = p
            while pp * p <= B1:
                pp *= p
            x, z = mm(pp, x, z)
            p = int(next_prime(p))
        g = gcd(z, n)
        if 1 < g < n:
            return int(g)
    return None


# ============================================================
# Portfolio wrappers
# ============================================================

def old_portfolio(N, time_limit=60):
    """Old: rho + ECM Stage 1."""
    t0 = time.time()
    nd = len(str(N))

    # Rho first
    f = pollard_rho(N, max_iter=2_000_000)
    if f and 1 < f < N:
        return f, time.time() - t0, "rho"

    if time.time() - t0 > time_limit:
        return None, time.time() - t0, "timeout"

    # ECM Stage 1 — run curves one-at-a-time to respect time limit
    ecm_B1 = min(1000000, max(10000, 10 ** (nd // 5)))
    max_curves = min(200, max(30, nd * 2))
    for batch_start in range(0, max_curves, 10):
        if time.time() - t0 > time_limit:
            return None, time.time() - t0, "timeout"
        batch = min(10, max_curves - batch_start)
        f = ecm_factor_s1_only(N, B1=ecm_B1, curves=batch)
        if f and 1 < f < N:
            return f, time.time() - t0, "ecm_s1"

    return None, time.time() - t0, "failed"


def new_portfolio(N, time_limit=60):
    """New: rho + p-1 + p+1 + ECM Stage 1+2."""
    t0 = time.time()
    nd = len(str(N))

    # Rho first (same as old)
    f = pollard_rho(N, max_iter=2_000_000)
    if f and 1 < f < N:
        return f, time.time() - t0, "rho"

    if time.time() - t0 > time_limit:
        return None, time.time() - t0, "timeout"

    # Pollard p-1 (fast — a few seconds at most)
    pm1_B1 = min(500000, max(50000, 10 ** (nd // 6)))
    f = pollard_pm1(N, B1=pm1_B1, B2=pm1_B1 * 10, verbose=False)
    if f and 1 < f < N:
        return f, time.time() - t0, "p-1"

    if time.time() - t0 > time_limit:
        return None, time.time() - t0, "timeout"

    # Williams p+1 (use fewer seeds to limit time)
    pp1_B1 = min(200000, max(50000, 10 ** (nd // 6)))
    f = williams_pp1(N, B1=pp1_B1, B2=pp1_B1 * 10, max_seeds=5, verbose=False)
    if f and 1 < f < N:
        return f, time.time() - t0, "p+1"

    if time.time() - t0 > time_limit:
        return None, time.time() - t0, "timeout"

    # ECM Stage 1 + Stage 2 — run in batches to respect time limit
    ecm_B1 = min(1000000, max(10000, 10 ** (nd // 5)))
    ecm_B2 = 100 * ecm_B1
    max_curves = min(200, max(30, nd * 2))
    for batch_start in range(0, max_curves, 10):
        if time.time() - t0 > time_limit:
            return None, time.time() - t0, "timeout"
        batch = min(10, max_curves - batch_start)
        f = ecm_factor(N, B1=ecm_B1, B2=ecm_B2, curves=batch, verbose=False)
        if f and 1 < f < N:
            return f, time.time() - t0, "ecm_s1s2"

    return None, time.time() - t0, "failed"


# ============================================================
# Semiprime generators
# ============================================================

def gen_balanced(digits):
    """Generate semiprime with balanced factors (roughly equal size)."""
    half = digits // 2
    while True:
        p = int(next_prime(mpz(random.randint(10**(half-1), 10**half - 1))))
        q = int(next_prime(mpz(random.randint(10**(half-1), 10**half - 1))))
        if p != q:
            N = p * q
            if len(str(N)) >= digits - 1:
                return N, min(p, q), max(p, q)


def gen_unbalanced(digits, ratio=10):
    """Generate semiprime where one factor is ~ratio times smaller."""
    # small factor has digits/ratio_factor digits
    small_d = max(3, digits // (1 + ratio // 3))
    large_d = digits - small_d
    while True:
        p = int(next_prime(mpz(random.randint(10**(small_d-1), 10**small_d - 1))))
        q = int(next_prime(mpz(random.randint(10**(large_d-1), 10**large_d - 1))))
        N = p * q
        if len(str(N)) >= digits - 1:
            return N, min(p, q), max(p, q)


# ============================================================
# Main benchmark
# ============================================================

if __name__ == "__main__":
    random.seed(2026_03_16)

    TIME_LIMIT = 60  # seconds per factorization

    categories = [
        ("30d balanced", lambda: gen_balanced(30), 20),
        ("30d unbalanced (1:10)", lambda: gen_unbalanced(30, ratio=10), 15),
        ("40d balanced", lambda: gen_balanced(40), 15),
    ]

    print("=" * 80)
    print("PORTFOLIO BENCHMARK")
    print("Old: rho + ECM(S1)  vs  New: rho + p-1 + p+1 + ECM(S1+S2)")
    print(f"Time limit per factorization: {TIME_LIMIT}s")
    print("=" * 80)

    total_old_wins = 0
    total_new_wins = 0
    total_old_time = 0.0
    total_new_time = 0.0
    total_old_found = 0
    total_new_found = 0
    total_tests = 0

    for cat_name, gen_func, count in categories:
        print(f"\n{'='*80}")
        print(f"Category: {cat_name} ({count} tests)")
        print(f"{'='*80}")
        print(f"{'#':>3} {'Digits':>6} {'Old':>12} {'Old_t':>8} {'New':>12} {'New_t':>8} {'Winner':>8}")
        print("-" * 70)

        cat_old_found = 0
        cat_new_found = 0
        cat_old_time = 0.0
        cat_new_time = 0.0

        for i in range(count):
            N, p, q = gen_func()
            nd = len(str(N))

            # Use same random state for fairness (reset seed per test)
            state = random.getstate()

            # Old portfolio
            random.setstate(state)
            f_old, t_old, method_old = old_portfolio(N, time_limit=TIME_LIMIT)
            old_ok = f_old is not None

            # New portfolio
            random.setstate(state)
            f_new, t_new, method_new = new_portfolio(N, time_limit=TIME_LIMIT)
            new_ok = f_new is not None

            if old_ok:
                cat_old_found += 1
            if new_ok:
                cat_new_found += 1
            cat_old_time += t_old
            cat_new_time += t_new

            if new_ok and not old_ok:
                winner = "NEW"
                total_new_wins += 1
            elif old_ok and not new_ok:
                winner = "OLD"
                total_old_wins += 1
            elif new_ok and old_ok:
                winner = "new" if t_new < t_old else "old" if t_old < t_new else "tie"
                if t_new < t_old:
                    total_new_wins += 1
                elif t_old < t_new:
                    total_old_wins += 1
            else:
                winner = "both_fail"

            m_old = method_old if old_ok else "FAIL"
            m_new = method_new if new_ok else "FAIL"
            print(f"{i+1:3d} {nd:6d}d {m_old:>12s} {t_old:7.2f}s {m_new:>12s} {t_new:7.2f}s {winner:>8s}")

        total_old_found += cat_old_found
        total_new_found += cat_new_found
        total_old_time += cat_old_time
        total_new_time += cat_new_time
        total_tests += count

        print(f"\n  Category summary:")
        print(f"    Old: {cat_old_found}/{count} found in {cat_old_time:.1f}s total")
        print(f"    New: {cat_new_found}/{count} found in {cat_new_time:.1f}s total")

    # Final summary
    print(f"\n{'='*80}")
    print("FINAL SUMMARY")
    print(f"{'='*80}")
    print(f"  Total tests:     {total_tests}")
    print(f"  Old portfolio:   {total_old_found}/{total_tests} found, {total_old_time:.1f}s total")
    print(f"  New portfolio:   {total_new_found}/{total_tests} found, {total_new_time:.1f}s total")
    print(f"  New wins:        {total_new_wins}")
    print(f"  Old wins:        {total_old_wins}")
    print(f"  New found extra: {total_new_found - total_old_found}")
    if total_old_time > 0:
        print(f"  Speedup:         {total_old_time / max(total_new_time, 0.01):.2f}x")
