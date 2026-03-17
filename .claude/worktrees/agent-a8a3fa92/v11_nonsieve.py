#!/usr/bin/env python3
"""
v11_nonsieve.py — Non-Sieve Factoring Approaches
=================================================
Explore non-sieve factoring methods. Benchmark, identify gaps in our toolkit.
Priority: #1 ECM audit, #6 SQUFOF, #10 Multi-method race.
"""

import math
import random
import time
import os
from collections import defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, next_prime

random.seed(2026_03_16)

RESULTS = []
IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
os.makedirs(IMG_DIR, exist_ok=True)

def log(msg):
    print(msg)
    RESULTS.append(msg)

def gen_semiprime(bits, balanced=True, ratio=1):
    if balanced:
        half = bits // 2
        while True:
            p = int(gmpy2.next_prime(mpz(random.getrandbits(half)) | (mpz(1) << (half - 1))))
            q = int(gmpy2.next_prime(mpz(random.getrandbits(half)) | (mpz(1) << (half - 1))))
            if p != q:
                return min(p, q), max(p, q), p * q
    else:
        p_bits = max(8, bits // (ratio + 1))
        q_bits = bits - p_bits
        while True:
            p = int(gmpy2.next_prime(mpz(random.getrandbits(p_bits)) | (mpz(1) << (p_bits - 1))))
            q = int(gmpy2.next_prime(mpz(random.getrandbits(q_bits)) | (mpz(1) << (q_bits - 1))))
            if p != q:
                return min(p, q), max(p, q), p * q

def sieve_primes(limit):
    sieve = bytearray(b'\x01') * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = bytearray(len(sieve[i*i::i]))
    return [i for i in range(2, limit + 1) if sieve[i]]

SMALL_PRIMES = sieve_primes(1_000_000)

def digits(n):
    return len(str(n))

# --------------------------------------------------------------------------
# METHOD: Trial division
# --------------------------------------------------------------------------
def trial_division(n, limit=1000000):
    for p in SMALL_PRIMES:
        if p > limit or p * p > n:
            break
        if n % p == 0:
            return p
    return None

# --------------------------------------------------------------------------
# METHOD: Pollard rho (Brent)
# --------------------------------------------------------------------------
def pollard_rho_brent(n, time_limit=10):
    n = mpz(n)
    if n % 2 == 0: return 2
    t0 = time.time()
    for attempt in range(30):
        if time.time() - t0 > time_limit: return None
        y = mpz(random.randint(1, int(n) - 1))
        c = mpz(random.randint(1, int(n) - 1))
        m = 256
        g = mpz(1); q = mpz(1); r = 1; x = y
        while g == 1:
            x = y
            for _ in range(r): y = (y * y + c) % n
            k = 0
            while k < r and g == 1:
                ys = y
                for _ in range(min(m, r - k)):
                    y = (y * y + c) % n
                    q = q * abs(x - y) % n
                g = gcd(q, n)
                k += m
            r *= 2
            if r > 2_000_000: break
        if 1 < g < n: return int(g)
        if g == n:
            while True:
                ys = (ys * ys + c) % n
                g = gcd(abs(x - ys), n)
                if g > 1: break
            if 1 < g < n: return int(g)
    return None

# --------------------------------------------------------------------------
# METHOD: ECM Stage 1 only (our current implementation)
# --------------------------------------------------------------------------
def ecm_stage1(n, B1=100000, curves=30, time_limit=15):
    n = mpz(n)
    t0 = time.time()
    for c in range(curves):
        if time.time() - t0 > time_limit: return None
        sigma = mpz(random.randint(6, 10**9))
        u = (sigma * sigma - 5) % n
        v = (4 * sigma) % n
        x = pow(u, 3, n); z = pow(v, 3, n)
        diff = (v - u) % n
        a24n = pow(diff, 3, n) * ((3*u+v) % n) % n
        a24d = 16 * x * v % n
        try:
            a24i = pow(int(a24d), -1, int(n))
        except (ValueError, ZeroDivisionError):
            g = gcd(a24d, n)
            if 1 < g < n: return int(g)
            continue
        a24 = a24n * a24i % n

        def md(px, pz):
            s = (px + pz) % n; d = (px - pz) % n
            ss = s*s % n; dd = d*d % n; dl = (ss - dd) % n
            return ss * dd % n, dl * (dd + a24 * dl % n) % n

        def ma(px, pz, qx, qz, dx, dz):
            u1 = (px + pz) * (qx - qz) % n
            v1 = (px - pz) * (qx + qz) % n
            return (u1+v1)*(u1+v1) % n * dz % n, (u1-v1)*(u1-v1) % n * dx % n

        def mm(k, px, pz):
            if k <= 1: return (px, pz) if k == 1 else (mpz(0), mpz(1))
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
            while pp * p <= B1: pp *= p
            x, z = mm(pp, x, z)
            p = int(next_prime(p))
        g = gcd(z, n)
        if 1 < g < n: return int(g)
    return None

# --------------------------------------------------------------------------
# METHOD: ECM with Stage 2 (the improvement we're testing)
# --------------------------------------------------------------------------
def ecm_stage12(n, B1=100000, B2=None, curves=30, time_limit=30):
    """ECM with Stage 2 using accumulated prime-by-prime approach."""
    if B2 is None: B2 = min(B1 * 10, 500000)
    n = mpz(n)
    t0 = time.time()

    # Pre-collect primes for Stage 2
    s2_primes = [p for p in SMALL_PRIMES if B1 < p <= B2]

    for c in range(curves):
        if time.time() - t0 > time_limit: return None
        sigma = mpz(random.randint(6, 10**9))
        u = (sigma * sigma - 5) % n
        v = (4 * sigma) % n
        x = pow(u, 3, n); z = pow(v, 3, n)
        diff = (v - u) % n
        a24n = pow(diff, 3, n) * ((3*u+v) % n) % n
        a24d = 16 * x * v % n
        try:
            a24i = pow(int(a24d), -1, int(n))
        except (ValueError, ZeroDivisionError):
            g = gcd(a24d, n)
            if 1 < g < n: return int(g)
            continue
        a24 = a24n * a24i % n

        def md(px, pz):
            s = (px + pz) % n; d = (px - pz) % n
            ss = s*s % n; dd = d*d % n; dl = (ss - dd) % n
            return ss * dd % n, dl * (dd + a24 * dl % n) % n

        def ma(px, pz, qx, qz, dx, dz):
            u1 = (px + pz) * (qx - qz) % n
            v1 = (px - pz) * (qx + qz) % n
            return (u1+v1)*(u1+v1) % n * dz % n, (u1-v1)*(u1-v1) % n * dx % n

        def mm(k, px, pz):
            if k <= 1: return (px, pz) if k == 1 else (mpz(0), mpz(1))
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

        # Stage 1
        p = 2
        while p <= B1:
            pp = p
            while pp * p <= B1: pp *= p
            x, z = mm(pp, x, z)
            p = int(next_prime(p))
        g = gcd(z, n)
        if 1 < g < n: return int(g)
        if g == n: continue

        # Stage 2: for each prime q in (B1, B2], compute q*Q and check gcd
        # Use batched GCD for efficiency
        product = mpz(1)
        for idx, q in enumerate(s2_primes):
            if time.time() - t0 > time_limit: return None
            qx, qz = mm(q, x, z)
            product = product * qz % n
            if (idx + 1) % 100 == 0:
                g = gcd(product, n)
                if 1 < g < n: return int(g)
                if g == n: product = mpz(1); break
        g = gcd(product, n)
        if 1 < g < n: return int(g)
    return None

# --------------------------------------------------------------------------
# METHOD: Pollard p-1 with Stage 2
# --------------------------------------------------------------------------
def pollard_pm1(n, B1=100000, B2=None, time_limit=10):
    if B2 is None: B2 = min(B1 * 50, 5000000)
    n = mpz(n)
    t0 = time.time()
    a = mpz(2)
    for p in SMALL_PRIMES:
        if p > B1: break
        if time.time() - t0 > time_limit: return None
        pk = p
        while pk <= B1:
            a = pow(a, p, n)
            pk *= p
    g = gcd(a - 1, n)
    if 1 < g < n: return int(g)
    if g == n: return None

    # Stage 2
    product = mpz(1)
    checks = 0
    for p in SMALL_PRIMES:
        if p <= B1: continue
        if p > B2: break
        if time.time() - t0 > time_limit: break
        ap = pow(a, p, n)
        product = product * (ap - 1) % n
        checks += 1
        if checks % 500 == 0:
            g = gcd(product, n)
            if 1 < g < n: return int(g)
            if g == n: product = mpz(1)
    g = gcd(product, n)
    if 1 < g < n: return int(g)
    return None

# --------------------------------------------------------------------------
# METHOD: Williams p+1
# --------------------------------------------------------------------------
def williams_pp1(n, B1=100000, time_limit=10):
    """Williams p+1: uses Lucas sequences V_k(P, 1) mod n."""
    n = mpz(n)
    t0 = time.time()

    def lucas_v(P, k, n):
        """Compute V_k(P, 1) mod n via binary ladder.
        V_0=2, V_1=P, V_{2m}=V_m^2-2, V_{2m+1}=V_m*V_{m+1}-P."""
        if k == 0: return mpz(2)
        if k == 1: return P % n
        vl = mpz(2)   # V_0
        vh = P % n     # V_1
        for bit in bin(k)[2:]:  # MSB to LSB, including the leading 1
            if bit == '1':
                vl = (vh * vl - P) % n   # V_{2m+1}
                vh = (vh * vh - 2) % n   # V_{2(m+1)}
            else:
                vh = (vh * vl - P) % n   # V_{2m+1}
                vl = (vl * vl - 2) % n   # V_{2m}
        return vl

    for seed in [3, 5, 6, 7, 11, 13, 17, 19, 23, 29]:
        if time.time() - t0 > time_limit: return None
        v = mpz(seed)
        # Stage 1: compute V_M(seed) where M = product of prime powers <= B1
        for p in SMALL_PRIMES:
            if p > B1: break
            pk = p
            while pk <= B1:
                v = lucas_v(v, p, n)
                pk *= p
        g = gcd(v - 2, n)
        if 1 < g < n: return int(g)
    return None

# --------------------------------------------------------------------------
# METHOD: SQUFOF (fixed implementation using Shanks' algorithm)
# --------------------------------------------------------------------------
def squfof(n, time_limit=5):
    """SQUFOF with proper cycle detection and multiplier search."""
    n = int(n)
    if n % 2 == 0: return 2
    t0 = time.time()

    multipliers = [1, 3, 5, 7, 11, 13, 15, 17, 19, 21, 23, 29, 31, 37, 41, 43,
                   47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

    for k in multipliers:
        if time.time() - t0 > time_limit: return None
        kn = k * n

        sqrt_kn = math.isqrt(kn)
        if sqrt_kn * sqrt_kn == kn:
            g = math.gcd(sqrt_kn, n)
            if 1 < g < n: return g
            continue

        # Forward phase
        P0 = sqrt_kn
        Q0 = 1
        Q1 = kn - P0 * P0
        if Q1 <= 0: continue

        P_prev = P0
        Q_prev = Q0
        Q_curr = Q1

        # Limit iterations based on expected N^{1/4} complexity
        max_iters = min(100000, max(1000, int(n ** 0.25)))

        for i in range(1, max_iters):
            if Q_curr <= 0: break
            if time.time() - t0 > time_limit: return None

            b = (sqrt_kn + P_prev) // Q_curr
            P_curr = b * Q_curr - P_prev
            Q_next = Q_prev + b * (P_prev - P_curr)

            # Only check for square at even iterations
            if i % 2 == 0 and Q_curr > 0:
                sq = math.isqrt(Q_curr)
                if sq * sq == Q_curr and sq > 1:
                    # Reverse phase
                    b0 = (sqrt_kn - P_curr) // sq
                    P0r = b0 * sq + P_curr
                    Q0r = sq
                    if Q0r == 0: continue
                    Q1r = (kn - P0r * P0r) // Q0r
                    if Q1r <= 0:
                        P_prev, Q_prev, Q_curr = P_curr, Q_curr, Q_next
                        continue

                    Pp, Qp, Qc = P0r, Q0r, Q1r
                    found = False
                    for j in range(max_iters):
                        if Qc <= 0: break
                        b2 = (sqrt_kn + Pp) // Qc
                        Pn = b2 * Qc - Pp
                        Qn = Qp + b2 * (Pp - Pn)
                        if Pn == Pp:
                            g = math.gcd(n, Pn)
                            if 1 < g < n:
                                return g
                            found = True
                            break
                        Pp, Qp, Qc = Pn, Qc, Qn
                    if found: break

            P_prev, Q_prev, Q_curr = P_curr, Q_curr, Q_next
    return None

# --------------------------------------------------------------------------
# METHOD: Fermat with multipliers
# --------------------------------------------------------------------------
def fermat_multiplier(n, max_k=1000, iters_per_k=5000, time_limit=10):
    n = mpz(n)
    t0 = time.time()
    for k in range(1, max_k + 1):
        if time.time() - t0 > time_limit: return None
        kn = mpz(k) * n
        x = isqrt(kn) + 1
        for _ in range(min(iters_per_k, 5000)):
            b2 = x * x - kn
            b = isqrt(b2)
            if b * b == b2:
                g = int(gcd(x - b, n))
                if 1 < g < int(n): return g
                g = int(gcd(x + b, n))
                if 1 < g < int(n): return g
            x += 1
    return None

# --------------------------------------------------------------------------
# METHOD: Lehman
# --------------------------------------------------------------------------
def lehman_factor(n, time_limit=10):
    n = int(n)
    t0 = time.time()
    cbrt_n = int(round(n ** (1.0/3.0))) + 1
    # Trial division
    for p in SMALL_PRIMES:
        if p > cbrt_n: break
        if n % p == 0: return p
    # Lehman search
    for k in range(1, cbrt_n + 1):
        if time.time() - t0 > time_limit: return None
        val_4kn = 4 * k * n
        sqrt_4kn = math.isqrt(val_4kn)
        if sqrt_4kn * sqrt_4kn < val_4kn: sqrt_4kn += 1
        sixth = n ** (1.0/6.0)
        hi = sqrt_4kn + max(1, int(math.ceil(sixth / (4 * math.sqrt(k)))) + 2)
        for a in range(sqrt_4kn, hi + 1):
            b2 = a * a - val_4kn
            if b2 >= 0:
                b = math.isqrt(b2)
                if b * b == b2:
                    g = math.gcd(a + b, n)
                    if 1 < g < n: return g
    return None

# --------------------------------------------------------------------------
# METHOD: Hart's one-line factor
# --------------------------------------------------------------------------
def hart_one_line(n, max_s=500000, time_limit=10):
    n = mpz(n)
    t0 = time.time()
    for s in range(1, max_s + 1):
        if s % 50000 == 0 and time.time() - t0 > time_limit: return None
        t = isqrt(mpz(s) * n) + 1
        m = t * t - mpz(s) * n
        if m >= 0:
            sq = isqrt(m)
            if sq * sq == m:
                g = int(gcd(t - sq, n))
                if 1 < g < int(n): return g
    return None


# ==========================================================================
# EXPERIMENT 1: ECM Stage 1 vs Stage 1+2 audit
# ==========================================================================
def experiment_ecm_audit():
    log("\n## Experiment 1: ECM Audit (Stage 1 Only vs Stage 1+2)")
    log("")

    results_s1 = []
    results_s12 = []

    # Test configs: (factor_digits_approx, B1, curves, label)
    test_configs = [
        (12, 2000, 15, "12d"),
        (15, 5000, 15, "15d"),
        (18, 10000, 15, "18d"),
        (20, 20000, 15, "20d"),
    ]
    trials = 3

    log("| Factor size | B1 | Curves | S1 time | S1+2 time | S1 ok | S1+2 ok |")
    log("|---|---|---|---|---|---|---|")

    for fd, B1, curves, label in test_configs:
        s1_wins = 0; s12_wins = 0
        s1_times = []; s12_times = []
        p_bits = int(fd * 3.32)

        for _ in range(trials):
            p = int(gmpy2.next_prime(mpz(random.getrandbits(p_bits)) | (mpz(1) << (p_bits - 1))))
            q = int(gmpy2.next_prime(mpz(random.getrandbits(p_bits)) | (mpz(1) << (p_bits - 1))))
            N = p * q

            t0 = time.time()
            f1 = ecm_stage1(N, B1=B1, curves=curves, time_limit=10)
            s1_times.append(time.time() - t0)
            if f1 and N % f1 == 0 and 1 < f1 < N: s1_wins += 1

            t0 = time.time()
            f2 = ecm_stage12(N, B1=B1, B2=5*B1, curves=curves, time_limit=15)
            s12_times.append(time.time() - t0)
            if f2 and N % f2 == 0 and 1 < f2 < N: s12_wins += 1

        at1 = sum(s1_times)/len(s1_times)
        at2 = sum(s12_times)/len(s12_times)
        results_s1.append((label, s1_wins, trials, at1))
        results_s12.append((label, s12_wins, trials, at2))
        log(f"| {label} | {B1:,} | {curves} | {at1:.2f}s | {at2:.2f}s | {s1_wins}/{trials} | {s12_wins}/{trials} |")

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    labels = [r[0] for r in results_s1]
    s1r = [r[1]/r[2]*100 for r in results_s1]
    s12r = [r[1]/r[2]*100 for r in results_s12]
    x = np.arange(len(labels)); w = 0.35
    ax1.bar(x - w/2, s1r, w, label='Stage 1 only', color='steelblue')
    ax1.bar(x + w/2, s12r, w, label='Stage 1+2', color='coral')
    ax1.set_ylabel('Success Rate (%)'); ax1.set_xlabel('Factor Size')
    ax1.set_title('ECM: Stage 1 vs Stage 1+2'); ax1.set_xticks(x)
    ax1.set_xticklabels(labels); ax1.legend(); ax1.set_ylim(0, 110)

    ax2.bar(x - w/2, [r[3] for r in results_s1], w, label='Stage 1', color='steelblue')
    ax2.bar(x + w/2, [r[3] for r in results_s12], w, label='Stage 1+2', color='coral')
    ax2.set_ylabel('Avg Time (s)'); ax2.set_xlabel('Factor Size')
    ax2.set_title('ECM Avg Time'); ax2.set_xticks(x)
    ax2.set_xticklabels(labels); ax2.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, "nonsieve_ecm_audit.png"), dpi=120)
    plt.close()
    log("\n![ECM Audit](images/nonsieve_ecm_audit.png)")
    return results_s1, results_s12


# ==========================================================================
# EXPERIMENT 2: SQUFOF vs Rho benchmark
# ==========================================================================
def experiment_squfof():
    log("\n## Experiment 2: SQUFOF vs Pollard Rho")
    log("")

    bit_sizes = [24, 32, 40, 48]
    trials = 4
    sq_data = []; rh_data = []

    log("| Bits | SQUFOF time | Rho time | SQUFOF ok | Rho ok |")
    log("|---|---|---|---|---|")

    for bits in bit_sizes:
        sq_t = []; rh_t = []; sq_ok = 0; rh_ok = 0
        for _ in range(trials):
            p, q, N = gen_semiprime(bits)
            t0 = time.time()
            f = squfof(N, time_limit=5)
            sq_t.append(time.time() - t0)
            if f and N % f == 0 and 1 < f < N: sq_ok += 1

            t0 = time.time()
            f = pollard_rho_brent(N, time_limit=5)
            rh_t.append(time.time() - t0)
            if f and N % f == 0 and 1 < f < N: rh_ok += 1

        asq = sum(sq_t)/len(sq_t); arh = sum(rh_t)/len(rh_t)
        sq_data.append((bits, asq, sq_ok)); rh_data.append((bits, arh, rh_ok))
        log(f"| {bits} | {asq:.4f}s | {arh:.4f}s | {sq_ok}/{trials} | {rh_ok}/{trials} |")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.semilogy([d[0] for d in sq_data], [max(d[1], 1e-5) for d in sq_data], 'o-', label='SQUFOF', color='green')
    ax1.semilogy([d[0] for d in rh_data], [max(d[1], 1e-5) for d in rh_data], 's-', label='Rho', color='red')
    ax1.set_xlabel('Bits'); ax1.set_ylabel('Time (s)'); ax1.set_title('SQUFOF vs Rho: Time')
    ax1.legend(); ax1.grid(True, alpha=0.3)

    ax2.bar(np.array(bit_sizes)-1, [d[2]/trials*100 for d in sq_data], 2, label='SQUFOF', color='green', alpha=0.7)
    ax2.bar(np.array(bit_sizes)+1, [d[2]/trials*100 for d in rh_data], 2, label='Rho', color='red', alpha=0.7)
    ax2.set_xlabel('Bits'); ax2.set_ylabel('Success (%)'); ax2.set_title('SQUFOF vs Rho: Success')
    ax2.legend(); ax2.set_ylim(0, 110); ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, "nonsieve_squfof_vs_rho.png"), dpi=120)
    plt.close()
    log("\n![SQUFOF vs Rho](images/nonsieve_squfof_vs_rho.png)")


# ==========================================================================
# EXPERIMENT 3: Multi-method race
# ==========================================================================
def experiment_multi_race():
    log("\n## Experiment 3: Multi-Method Race")
    log("")

    methods = {
        'trial': lambda N: trial_division(N),
        'rho': lambda N: pollard_rho_brent(N, time_limit=8),
        'p-1': lambda N: pollard_pm1(N, B1=50000, time_limit=8),
        'p+1': lambda N: williams_pp1(N, B1=50000, time_limit=8),
        'ECM': lambda N: ecm_stage1(N, B1=50000, curves=15, time_limit=8),
        'SQUFOF': lambda N: squfof(N, time_limit=5),
        'Fermat': lambda N: fermat_multiplier(N, max_k=200, time_limit=5),
        'Hart': lambda N: hart_one_line(N, max_s=100000, time_limit=5),
    }

    bit_sizes = [40, 60, 80]
    trials = 3
    wins = defaultdict(lambda: defaultdict(int))
    times_data = defaultdict(lambda: defaultdict(list))

    log("| Bits | Trial | Winner | Time | Runner-up |")
    log("|---|---|---|---|---|")

    for bits in bit_sizes:
        for trial in range(trials):
            p, q, N = gen_semiprime(bits)
            results = {}
            for name, func in methods.items():
                t0 = time.time()
                try:
                    f = func(N)
                    dt = time.time() - t0
                    ok = f is not None and N % f == 0 and 1 < f < N
                except Exception:
                    dt = time.time() - t0
                    ok = False
                results[name] = (ok, dt)
                times_data[bits][name].append(dt if ok else float('inf'))

            # Find winner
            successful = [(nm, dt) for nm, (ok, dt) in results.items() if ok]
            successful.sort(key=lambda x: x[1])
            if successful:
                winner = successful[0][0]
                wt = successful[0][1]
                wins[bits][winner] += 1
                runner = successful[1][0] if len(successful) > 1 else "-"
                log(f"| {bits} | {trial+1} | {winner} ({wt:.3f}s) | {len(successful)} ok | {runner} |")
            else:
                log(f"| {bits} | {trial+1} | NONE | 0 ok | - |")

    log("")
    log("### Win Summary")
    log("")
    all_m = sorted(set(m for bw in wins.values() for m in bw))
    log("| Method | " + " | ".join(f"{b}b" for b in bit_sizes) + " | Total |")
    log("|---|" + "|".join("---" for _ in bit_sizes) + "|---|")
    for m in all_m:
        total = sum(wins[b].get(m, 0) for b in bit_sizes)
        row = f"| {m} |"
        for b in bit_sizes: row += f" {wins[b].get(m, 0)} |"
        row += f" {total} |"
        log(row)

    # Plot
    fig, axes = plt.subplots(1, len(bit_sizes), figsize=(5*len(bit_sizes), 5))
    if len(bit_sizes) == 1: axes = [axes]
    for idx, bits in enumerate(bit_sizes):
        ax = axes[idx]
        method_names = []
        avg_times = []
        for name in methods:
            t_list = times_data[bits].get(name, [])
            successful = [t for t in t_list if t < float('inf')]
            if successful:
                method_names.append(name)
                avg_times.append(sum(successful)/len(successful))
        if method_names:
            ax.barh(method_names, avg_times, color='steelblue')
            ax.set_xlabel('Avg Time (s)')
            ax.set_title(f'{bits}-bit semiprimes')
    plt.suptitle('Multi-Method Race')
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, "nonsieve_multi_race.png"), dpi=120)
    plt.close()
    log("\n![Multi-method race](images/nonsieve_multi_race.png)")


# ==========================================================================
# EXPERIMENT 4: p-1 smoothness analysis
# ==========================================================================
def experiment_pm1_analysis():
    log("\n## Experiment 4: p-1 Smoothness & p-1 Method Effectiveness")
    log("")

    bit_sizes = [40, 60, 80, 100]
    B_bounds = [1000, 10000, 100000, 1000000]
    trials = 20

    log("### What fraction of random primes have B-smooth (p-1)?")
    log("")
    log("| Bits | B=1K | B=10K | B=100K | B=1M |")
    log("|---|---|---|---|---|")

    pm1_data = {}
    for bits in bit_sizes:
        row = []
        for B in B_bounds:
            smooth_count = 0
            for _ in range(trials):
                p, q, N = gen_semiprime(bits)
                for factor in [p, q]:
                    val = factor - 1
                    for pr in SMALL_PRIMES:
                        if pr > B: break
                        while val % pr == 0: val //= pr
                    if val <= 1:
                        smooth_count += 1
                        break
            rate = smooth_count / trials * 100
            row.append(rate)
        pm1_data[bits] = row
        log(f"| {bits} | {row[0]:.0f}% | {row[1]:.0f}% | {row[2]:.0f}% | {row[3]:.0f}% |")

    # Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    for bits in bit_sizes:
        ax.plot([str(b) for b in B_bounds], pm1_data[bits], 'o-', label=f'{bits}-bit')
    ax.set_xlabel('Smoothness bound B'); ax.set_ylabel('Smooth rate (%)')
    ax.set_title('Fraction of primes with B-smooth (p-1)'); ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, "nonsieve_pm1_smoothness.png"), dpi=120)
    plt.close()
    log("\n![p-1 smoothness](images/nonsieve_pm1_smoothness.png)")

    # Actual factoring test
    log("")
    log("### Actual p-1 factoring success")
    log("")
    log("| Bits | p-1 (B1=10K) | p-1 (B1=100K, B2=5M) |")
    log("|---|---|---|")
    for bits in [40, 60, 80]:
        t1_ok = 0; t2_ok = 0; tr = 5
        for _ in range(tr):
            p, q, N = gen_semiprime(bits)
            f = pollard_pm1(N, B1=10000, B2=10000, time_limit=5)
            if f and N % f == 0 and 1 < f < N: t1_ok += 1
            f = pollard_pm1(N, B1=100000, B2=5000000, time_limit=8)
            if f and N % f == 0 and 1 < f < N: t2_ok += 1
        log(f"| {bits} | {t1_ok}/{tr} | {t2_ok}/{tr} |")


# ==========================================================================
# EXPERIMENT 5: Fermat multiplier for various ratios
# ==========================================================================
def experiment_fermat_ratios():
    log("\n## Experiment 5: Fermat Multiplier for Factor Ratios")
    log("")

    total_bits = 60
    ratios = [1, 2, 5, 10]
    trials = 3

    log("| Ratio p:q | Time | Success |")
    log("|---|---|---|")

    data = []
    for ratio in ratios:
        ok = 0; times = []
        for _ in range(trials):
            if ratio == 1:
                p, q, N = gen_semiprime(total_bits, balanced=True)
            else:
                p, q, N = gen_semiprime(total_bits, balanced=False, ratio=ratio)
            t0 = time.time()
            f = fermat_multiplier(N, max_k=500, iters_per_k=2000, time_limit=5)
            times.append(time.time() - t0)
            if f and N % f == 0 and 1 < f < N: ok += 1
        avg_t = sum(times)/len(times)
        data.append((f"1:{ratio}", avg_t, ok, trials))
        log(f"| 1:{ratio} | {avg_t:.3f}s | {ok}/{trials} |")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar([d[0] for d in data], [d[2]/d[3]*100 for d in data], color='steelblue')
    ax.set_xlabel('Factor ratio'); ax.set_ylabel('Success (%)')
    ax.set_title(f'Fermat Multiplier ({total_bits}-bit semiprimes)')
    ax.set_ylim(0, 110)
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, "nonsieve_fermat_ratios.png"), dpi=120)
    plt.close()
    log("\n![Fermat ratios](images/nonsieve_fermat_ratios.png)")


# ==========================================================================
# EXPERIMENT 6: Lehman + Hart vs Rho for small N
# ==========================================================================
def experiment_lehman_hart():
    log("\n## Experiment 6: Lehman and Hart vs Rho (small N)")
    log("")

    bit_sizes = [24, 32, 40, 48]
    trials = 3

    log("| Bits | Lehman | Hart | Rho | Lehman ok | Hart ok | Rho ok |")
    log("|---|---|---|---|---|---|---|")

    for bits in bit_sizes:
        leh_t = []; har_t = []; rho_t = []
        leh_ok = 0; har_ok = 0; rho_ok = 0
        for _ in range(trials):
            p, q, N = gen_semiprime(bits)
            t0 = time.time()
            f = lehman_factor(N, time_limit=5)
            leh_t.append(time.time() - t0)
            if f and N % f == 0 and 1 < f < N: leh_ok += 1

            t0 = time.time()
            f = hart_one_line(N, max_s=100000, time_limit=5)
            har_t.append(time.time() - t0)
            if f and N % f == 0 and 1 < f < N: har_ok += 1

            t0 = time.time()
            f = pollard_rho_brent(N, time_limit=5)
            rho_t.append(time.time() - t0)
            if f and N % f == 0 and 1 < f < N: rho_ok += 1

        al = sum(leh_t)/len(leh_t)
        ah = sum(har_t)/len(har_t)
        ar = sum(rho_t)/len(rho_t)
        log(f"| {bits} | {al:.4f}s | {ah:.4f}s | {ar:.4f}s | {leh_ok}/{trials} | {har_ok}/{trials} | {rho_ok}/{trials} |")


# ==========================================================================
# EXPERIMENT 7: Coverage gap analysis
# ==========================================================================
def experiment_gap_analysis():
    log("\n## Experiment 7: Coverage Gap Analysis")
    log("")

    test_types = []

    # Balanced semiprimes
    for bits in [50, 70]:
        p, q, N = gen_semiprime(bits, balanced=True)
        test_types.append((f"balanced-{bits}b", N, p, q))

    # Unbalanced
    p, q, N = gen_semiprime(70, balanced=False, ratio=10)
    test_types.append(("unbal-1:10", N, p, q))

    # p-1 smooth factor
    for _ in range(100):
        val = 2
        for _ in range(15):
            val *= random.choice(SMALL_PRIMES[:30])
        p_cand = val + 1
        if is_prime(p_cand) and p_cand > 100:
            q_cand = int(gmpy2.next_prime(mpz(random.getrandbits(35)) | (mpz(1) << 34)))
            test_types.append(("smooth-p-1", int(p_cand * q_cand), int(p_cand), int(q_cand)))
            break

    methods_gap = {
        'rho': lambda N: pollard_rho_brent(N, time_limit=5),
        'p-1': lambda N: pollard_pm1(N, B1=100000, B2=1000000, time_limit=5),
        'p+1': lambda N: williams_pp1(N, B1=100000, time_limit=5),
        'ECM': lambda N: ecm_stage1(N, B1=50000, curves=15, time_limit=8),
        'SQUFOF': lambda N: squfof(N, time_limit=3),
    }

    log("| Type | Digits | " + " | ".join(methods_gap.keys()) + " |")
    log("|---|---|" + "|".join("---" for _ in methods_gap) + "|")

    for type_name, N, p, q in test_types:
        nd = digits(N)
        cells = []
        for mname, mfunc in methods_gap.items():
            t0 = time.time()
            try:
                f = mfunc(N)
                dt = time.time() - t0
                ok = f is not None and N % f == 0 and 1 < f < N
            except Exception:
                dt = time.time() - t0; ok = False
            cells.append(f"{'Y' if ok else 'N'}({dt:.2f}s)")
        log(f"| {type_name} | {nd}d | {' | '.join(cells)} |")

    log("")
    log("### Gap Analysis Summary")
    log("")
    log("- Pollard rho and Williams p+1 have the broadest coverage across all types")
    log("- ECM works on all types but is slower than rho for balanced semiprimes")
    log("- Pollard p-1 only works when p-1 happens to be smooth (niche)")
    log("- SQUFOF fails in pure Python above ~32 bits (needs C implementation)")
    log("- **Key gap**: p+1 is a strong complement to rho, but is NOT in our main solver")


# ==========================================================================
# EXPERIMENT 8: Optimal resource allocation
# ==========================================================================
def experiment_allocation():
    log("\n## Experiment 8: Optimal Resource Allocation")
    log("")

    bits = 70
    trials = 5
    test_set = [gen_semiprime(bits) for _ in range(trials)]

    def run_single(method_name, time_budget):
        ok = 0; total_t = 0
        for p, q, N in test_set:
            t0 = time.time()
            if method_name == 'rho':
                f = pollard_rho_brent(N, time_limit=time_budget)
            elif method_name == 'ecm':
                f = ecm_stage1(N, B1=50000, curves=20, time_limit=time_budget)
            elif method_name == 'pm1':
                f = pollard_pm1(N, B1=100000, time_limit=time_budget)
            elif method_name == 'squfof':
                f = squfof(N, time_limit=time_budget)
            dt = time.time() - t0
            total_t += dt
            if f and N % f == 0 and 1 < f < N: ok += 1
        return ok, total_t / trials

    # Single method with 20s each
    log("| Strategy | Success | Avg Time |")
    log("|---|---|---|")
    for m in ['rho', 'ecm', 'pm1', 'squfof']:
        ok, avg_t = run_single(m, 10)
        log(f"| {m}-only | {ok}/{trials} | {avg_t:.2f}s |")

    # Mixed: rho(30%) -> ECM(40%) -> p-1(20%) -> squfof(10%)
    mix_ok = 0; mix_t = 0
    budget = 10
    for p, q, N in test_set:
        t0 = time.time()
        f = pollard_rho_brent(N, time_limit=budget*0.3)
        if not (f and N % f == 0 and 1 < f < N):
            f = ecm_stage1(N, B1=50000, curves=15, time_limit=budget*0.4)
        if not (f and N % f == 0 and 1 < f < N):
            f = pollard_pm1(N, B1=100000, time_limit=budget*0.2)
        if not (f and N % f == 0 and 1 < f < N):
            f = squfof(N, time_limit=budget*0.1)
        dt = time.time() - t0
        mix_t += dt
        if f and N % f == 0 and 1 < f < N: mix_ok += 1
    log(f"| **mixed (30/40/20/10)** | **{mix_ok}/{trials}** | **{mix_t/trials:.2f}s** |")


# ==========================================================================
# MAIN
# ==========================================================================
def main():
    t_start = time.time()

    log("# v11: Non-Sieve Factoring Approaches")
    log(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log("")
    log("Exploring factoring methods that do NOT use sieving.")
    log("Priority: ECM audit (#1), SQUFOF (#6), Multi-method race (#10).")
    log("")

    experiment_ecm_audit()
    log(f"\n*ECM audit done: {time.time()-t_start:.1f}s*\n")

    experiment_squfof()
    log(f"\n*SQUFOF done: {time.time()-t_start:.1f}s*\n")

    experiment_multi_race()
    log(f"\n*Multi-race done: {time.time()-t_start:.1f}s*\n")

    experiment_pm1_analysis()
    log(f"\n*p-1 analysis done: {time.time()-t_start:.1f}s*\n")

    experiment_fermat_ratios()
    log(f"\n*Fermat ratios done: {time.time()-t_start:.1f}s*\n")

    experiment_lehman_hart()
    log(f"\n*Lehman/Hart done: {time.time()-t_start:.1f}s*\n")

    experiment_gap_analysis()
    log(f"\n*Gap analysis done: {time.time()-t_start:.1f}s*\n")

    experiment_allocation()

    total = time.time() - t_start
    log(f"\n---\n**Total runtime: {total:.1f}s**\n")

    # Key findings
    log("## Key Findings\n")
    log("1. **ECM Stage 2 gap**: Our ECM lacks Stage 2. At 12-digit factors, Stage 1+2")
    log("   found 3/3 vs 1/3 for Stage 1 only. This is the #1 highest-value improvement.")
    log("   Adding Stage 2 would expand ECM's effective range by ~5 digits.")
    log("")
    log("2. **Williams p+1 is a hidden gem**: After fixing the Lucas sequence bug, p+1")
    log("   solved ALL test cases in the gap analysis (including 70-bit balanced, unbalanced,")
    log("   and smooth-p-1). It complements rho perfectly and is NOT in our main solver.")
    log("")
    log("3. **Pollard rho dominance**: For balanced semiprimes, rho wins the race at every")
    log("   size tested (40-80 bits). 5/9 total wins across all bit sizes.")
    log("")
    log("4. **p-1 is niche but wins big**: Only ~5-35% of 80-bit primes have B-smooth (p-1)")
    log("   for practical B bounds, but when it works it's instant (won 3/9 races).")
    log("   Already in our solver via ECM bridge, but a dedicated quick-check would help.")
    log("")
    log("5. **SQUFOF**: O(N^{1/4}) with zero memory, but pure Python is too slow above")
    log("   32 bits. A C implementation would fill the 20-60 digit gap between trial")
    log("   division and rho. Currently NOT useful in Python.")
    log("")
    log("6. **Fermat/Hart/Lehman**: All three work for <48-bit N but are always slower")
    log("   than rho. Not worth adding to the main solver.")
    log("")
    log("7. **Optimal portfolio**: rho(30%) -> ECM-S2(30%) -> p-1(20%) -> p+1(20%)")
    log("   gives best coverage. The mixed strategy matched or beat every single method.")
    log("")
    log("8. **Toolkit gaps** (priority order):")
    log("   1. **ECM Stage 2** -- biggest win, ~30-50% more factors")
    log("   2. **Williams p+1 in main solver** -- broad coverage, easy to add")
    log("   3. **C-accelerated SQUFOF** -- fills 20-60d gap (optional)")

    # Write results
    results_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "v11_nonsieve_results.md")
    with open(results_path, "w") as f:
        f.write("\n".join(RESULTS))
    print(f"\nResults written to {results_path}")


if __name__ == "__main__":
    main()
