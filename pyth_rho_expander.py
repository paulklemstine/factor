#!/usr/bin/env python3
"""
Pythagorean Expander Rho vs Standard Rho — Step & Time Comparison
=================================================================
O(1) memory throughout (Brent's algorithm). No hash tables.

Methods:
  1. Standard Pollard rho:  f(x) = x^2 + c mod N, Brent cycle detection
  2. Tree rho:  Berggren walk on ratio r = m/n mod N, batch GCD every 100 steps
  3. Tree multi-value rho:  Same walk, accumulate diffs from A,B,C,m-n,m+n
     (5 independent fingerprints per step -> effective 5x birthday advantage)

The key insight: the Berggren matrices act as Mobius transforms on the projective
line P^1(Z/NZ). To get O(sqrt(p)) collisions we project to a SCALAR fingerprint
(e.g. m^2-n^2 mod N) which is many-to-one, creating random-map structure.

RESULTS (2026-03-15):
  The tree walk is dramatically WORSE than standard rho (100-1000x more steps).
  The Berggren Mobius transforms are bijections on P^1(Z/pZ), so the underlying
  walk has permutation-cycle length O(p), not O(sqrt(p)). The scalar projection
  (m^2-n^2) mod N does NOT create sufficient many-to-one collapsing.
  The expander mixing property helps distribute values but cannot overcome the
  fundamental O(p) cycle structure of the bijective walk.

  Bits | StdRho    TreeRho    MultiRho  | Tree/Std  Multi/Std
  20   |      62       966         62   |   15.58      1.00
  24   |     126      6392        510   |   50.73      4.05
  28   |     254     25074       3670   |   98.72     14.45
  32   |     482    104302      28574   |  216.39     59.28
  36   |     482    164554      57850   |  341.04    119.90
  40   |    1300   1304296     350760   | 1003.30    269.82
  44   |    3170   2607344     978880   |  822.51    308.79
  48   |    3720   2165870    1800812   |  582.22    484.09

  CONCLUSION: Tree rho is not viable. The expander property does not translate
  into a factoring advantage via Pollard-rho-style cycle detection.
"""

import gmpy2
from gmpy2 import mpz, gcd, next_prime
import random, time, statistics, sys

# Berggren generators as 2x2 matrices on (m,n)
MATS = ((2, -1, 1, 0), (2, 1, 1, 0), (1, 2, 0, 1))

def mat_step(m, n, N, idx):
    a, b, c, d = MATS[idx]
    return (a * m + b * n) % N, (c * m + d * n) % N

def make_semiprime(bits):
    half = bits // 2
    p = next_prime(mpz(random.getrandbits(half)) | (mpz(1) << (half - 1)))
    q = next_prime(mpz(random.getrandbits(half)) | (mpz(1) << (half - 1)))
    while q == p:
        q = next_prime(mpz(random.getrandbits(half)) | (mpz(1) << (half - 1)))
    return p * q, p, q

# ── Method 1: Standard Pollard Rho (Brent + batch GCD) ──────────────
def standard_rho(N, max_steps=4_000_000):
    N = mpz(N)
    c = mpz(random.randint(2, int(N) - 1))
    f = lambda x: (x * x + c) % N
    tort = hare = mpz(random.randint(2, int(N) - 1))
    steps = 0
    r = 1
    while steps < max_steps:
        tort = hare  # save tortoise
        for _ in range(r):
            hare = f(hare)
            steps += 1
        # batch compare hare vs tort
        k = 0
        while k < r and steps < max_steps:
            hare_save = hare
            prod = mpz(1)
            bound = min(100, r - k)
            for _ in range(bound):
                hare = f(hare)
                steps += 1
                prod = prod * ((tort - hare) % N) % N
            d = gcd(prod, N)
            if d != 1:
                if d == N:
                    hare = hare_save
                    while True:
                        hare = f(hare)
                        steps += 1
                        d = gcd((tort - hare) % N, N)
                        if d != 1:
                            break
                if 1 < d < N:
                    return steps, True
                return steps, False
            k += bound
        r *= 2
    return steps, False

# ── Method 2: Tree Rho (fingerprint = m^2-n^2 mod N) ────────────────
def tree_rho(N, max_steps=4_000_000):
    N = mpz(N)
    m_t = mpz(random.randint(2, int(N) - 1))
    n_t = mpz(random.randint(1, int(N) - 1))
    m_h, n_h = m_t, n_t

    def step(m, n):
        idx = int(m + n) % 3
        return mat_step(m, n, N, idx)

    def fp(m, n):
        return (m * m - n * n) % N

    steps = 0
    r = 1
    while steps < max_steps:
        m_t, n_t = m_h, n_h
        fp_t = fp(m_t, n_t)
        for _ in range(r):
            m_h, n_h = step(m_h, n_h)
            steps += 1
        k = 0
        while k < r and steps < max_steps:
            m_save, n_save = m_h, n_h
            prod = mpz(1)
            bound = min(100, r - k)
            for _ in range(bound):
                m_h, n_h = step(m_h, n_h)
                steps += 1
                diff = (fp_t - fp(m_h, n_h)) % N
                if diff == 0:
                    diff = N  # skip trivial
                prod = prod * diff % N
            d = gcd(prod, N)
            if d != 1:
                if d == N:
                    m_h, n_h = m_save, n_save
                    while True:
                        m_h, n_h = step(m_h, n_h)
                        steps += 1
                        d = gcd((fp_t - fp(m_h, n_h)) % N, N)
                        if d != 1:
                            break
                if 1 < d < N:
                    return steps, True
                return steps, False
            k += bound
        r *= 2
    return steps, False

# ── Method 3: Tree Multi-Value Rho (5 fingerprints per step) ────────
def tree_multi_rho(N, max_steps=4_000_000):
    N = mpz(N)
    m_t = mpz(random.randint(2, int(N) - 1))
    n_t = mpz(random.randint(1, int(N) - 1))
    m_h, n_h = m_t, n_t

    def step(m, n):
        idx = int(m + n) % 3
        return mat_step(m, n, N, idx)

    def vals(m, n):
        mm, nn = m * m, n * n
        return ((mm - nn) % N, (2 * m * n) % N, (mm + nn) % N,
                (m - n) % N, (m + n) % N)

    steps = 0
    r = 1
    while steps < max_steps:
        m_t, n_t = m_h, n_h
        v_t = vals(m_t, n_t)
        for _ in range(r):
            m_h, n_h = step(m_h, n_h)
            steps += 1
        k = 0
        while k < r and steps < max_steps:
            m_save, n_save = m_h, n_h
            prod = mpz(1)
            bound = min(100, r - k)
            for _ in range(bound):
                m_h, n_h = step(m_h, n_h)
                steps += 1
                v_h = vals(m_h, n_h)
                for a, b in zip(v_t, v_h):
                    diff = (a - b) % N
                    if diff != 0:
                        prod = prod * diff % N
            d = gcd(prod, N)
            if d != 1:
                if d == N:
                    m_h, n_h = m_save, n_save
                    while True:
                        m_h, n_h = step(m_h, n_h)
                        steps += 1
                        v_h = vals(m_h, n_h)
                        for a, b in zip(v_t, v_h):
                            diff = (a - b) % N
                            if diff != 0:
                                d = gcd(diff, N)
                                if 1 < d < N:
                                    return steps, True
                        if steps > max_steps:
                            return steps, False
                if 1 < d < N:
                    return steps, True
                return steps, False
            k += bound
        r *= 2
    return steps, False

# ── Benchmark Harness ────────────────────────────────────────────────
def run_experiment():
    bit_sizes = list(range(20, 65, 4))
    trials = 20
    print(f"{'Bits':>4} | {'StdRho':>10} {'TreeRho':>10} {'MultiRho':>10} | "
          f"{'Tree/Std':>8} {'Multi/Std':>9} | "
          f"{'StdTime':>8} {'TreeTime':>8} {'MultiTime':>9}")
    print("-" * 105)

    for bits in bit_sizes:
        std_steps, tree_steps, multi_steps = [], [], []
        std_times, tree_times, multi_times = [], [], []
        for _ in range(trials):
            N, p, q = make_semiprime(bits)

            t0 = time.time()
            s, ok = standard_rho(N)
            std_times.append(time.time() - t0)
            if ok: std_steps.append(s)

            t0 = time.time()
            s, ok = tree_rho(N)
            tree_times.append(time.time() - t0)
            if ok: tree_steps.append(s)

            t0 = time.time()
            s, ok = tree_multi_rho(N)
            multi_times.append(time.time() - t0)
            if ok: multi_steps.append(s)

        ms = statistics.median(std_steps) if std_steps else float('inf')
        mt = statistics.median(tree_steps) if tree_steps else float('inf')
        mm = statistics.median(multi_steps) if multi_steps else float('inf')
        ts = statistics.median(std_times)
        tt = statistics.median(tree_times)
        tm = statistics.median(multi_times)
        ratio_t = mt / ms if ms and ms != float('inf') else float('inf')
        ratio_m = mm / ms if ms and ms != float('inf') else float('inf')
        sr = f"{len(std_steps)}/{trials}"
        tr = f"{len(tree_steps)}/{trials}"
        mr = f"{len(multi_steps)}/{trials}"
        print(f"{bits:4d} | {ms:10.0f} {mt:10.0f} {mm:10.0f} | "
              f"{ratio_t:8.2f} {ratio_m:9.2f} | "
              f"{ts:7.4f}s {tt:7.4f}s {tm:8.4f}s  [{sr} {tr} {mr}]")
        sys.stdout.flush()

if __name__ == "__main__":
    run_experiment()
