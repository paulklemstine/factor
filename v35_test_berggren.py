#!/usr/bin/env python3
"""
v35_test_berggren.py — Benchmark Berggren resonance p-1/p+1 pre-sieve
======================================================================
Compare pipeline WITH vs WITHOUT berggren_pm1 on 20 semiprimes (30-60 digits).

Pipeline WITHOUT: p-1 -> p+1 -> gaussian_pm1 -> ECM
Pipeline WITH:    p-1 -> p+1 -> gaussian_pm1 -> berggren_pm1 -> ECM

Measures: factors found by each method, total time, berggren-unique finds.
"""

import gmpy2
from gmpy2 import mpz, next_prime, is_prime
import time
import random

from resonance_v7 import (
    pollard_pm1, williams_pp1, gaussian_pm1, berggren_pm1, ecm_factor,
    _SMALL_PRIMES
)

random.seed(2026_03_17)


def random_prime(bits):
    while True:
        n = mpz(random.getrandbits(bits))
        n |= (1 << (bits - 1)) | 1
        if is_prime(n):
            return int(n)


def make_semiprime(digits):
    bits = int(digits * 3.3219)
    b1 = bits // 2
    b2 = bits - b1
    p = random_prime(b1)
    q = random_prime(b2)
    while p == q:
        q = random_prime(b2)
    return p * q, min(p, q), max(p, q)


def max_prime_factor(n):
    n = abs(int(n))
    if n <= 1:
        return 1
    largest = 1
    for p in _SMALL_PRIMES:
        if p * p > n:
            break
        while n % p == 0:
            largest = p
            n //= p
    if n > 1:
        largest = n
    return largest


def run_pipeline_without(n, B1):
    """p-1 -> p+1 -> gaussian -> ECM."""
    t0 = time.time()
    f = pollard_pm1(n, B1=B1, B2=B1*10, verbose=False)
    if f and 1 < f < n:
        return f, "p-1", time.time() - t0
    f = williams_pp1(n, B1=B1, B2=B1*10, max_seeds=6, verbose=False)
    if f and 1 < f < n:
        return f, "p+1", time.time() - t0
    f = gaussian_pm1(n, B1=B1, B2=B1*10, verbose=False)
    if f and 1 < f < n:
        return f, "gauss", time.time() - t0
    f = ecm_factor(n, B1=B1, B2=100*B1, curves=30, verbose=False)
    if f and 1 < f < n:
        return f, "ECM", time.time() - t0
    return None, "FAIL", time.time() - t0


def run_pipeline_with(n, B1):
    """p-1 -> p+1 -> gaussian -> berggren -> ECM."""
    t0 = time.time()
    f = pollard_pm1(n, B1=B1, B2=B1*10, verbose=False)
    if f and 1 < f < n:
        return f, "p-1", time.time() - t0
    f = williams_pp1(n, B1=B1, B2=B1*10, max_seeds=6, verbose=False)
    if f and 1 < f < n:
        return f, "p+1", time.time() - t0
    f = gaussian_pm1(n, B1=B1, B2=B1*10, verbose=False)
    if f and 1 < f < n:
        return f, "gauss", time.time() - t0
    f = berggren_pm1(n, B1=B1, verbose=False)
    if f and 1 < f < n:
        return f, "berggren", time.time() - t0
    f = ecm_factor(n, B1=B1, B2=100*B1, curves=30, verbose=False)
    if f and 1 < f < n:
        return f, "ECM", time.time() - t0
    return None, "FAIL", time.time() - t0


# =========================================================================
# TEST 1: Standalone on smooth-factor semiprimes
# =========================================================================
def test_smooth_factors():
    print("=" * 72)
    print("TEST 1: Berggren vs competitors on SMOOTH-factor semiprimes")
    print("=" * 72)

    random.seed(999)
    q = int(next_prime(10**20))
    B1 = 100000

    # Generate p-1 smooth primes
    smooth_p = []
    for _ in range(500):
        m = 1
        for pp in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]:
            m *= pp ** random.randint(0, 3)
        if 10**12 < m < 10**20:
            cand = m + 1
            if is_prime(cand):
                smooth_p.append(("p-1", int(cand)))
            cand = m - 1
            if is_prime(cand):
                smooth_p.append(("p+1", int(cand)))
    random.shuffle(smooth_p)
    smooth_p = smooth_p[:20]

    berg_found = pm1_found = pp1_found = gauss_found = 0
    berg_unique = 0

    for stype, p in smooth_p:
        n = p * q
        fb = berggren_pm1(n, B1=B1, verbose=False)
        fp = pollard_pm1(n, B1=B1, B2=B1 * 10, verbose=False)
        fw = williams_pp1(n, B1=B1, B2=B1 * 10, max_seeds=6, verbose=False)
        fg = gaussian_pm1(n, B1=B1, B2=B1 * 10, verbose=False)

        b = fb is not None and n % fb == 0
        p1 = fp is not None and n % fp == 0
        w = fw is not None and n % fw == 0
        g = fg is not None and n % fg == 0

        if b: berg_found += 1
        if p1: pm1_found += 1
        if w: pp1_found += 1
        if g: gauss_found += 1
        if b and not p1 and not w and not g: berg_unique += 1

        nd = len(str(n))
        print(f"  {nd}d {stype} smooth: berg={'Y' if b else 'n'}"
              f" p-1={'Y' if p1 else 'n'} p+1={'Y' if w else 'n'}"
              f" gauss={'Y' if g else 'n'}")

    total = len(smooth_p)
    print(f"\n  Results ({total} tests):")
    print(f"    Berggren:  {berg_found}/{total}")
    print(f"    Pollard:   {pm1_found}/{total}")
    print(f"    Williams:  {pp1_found}/{total}")
    print(f"    Gaussian:  {gauss_found}/{total}")
    print(f"    Berggren unique (no other found): {berg_unique}")


# =========================================================================
# TEST 2: Pipeline comparison on random semiprimes
# =========================================================================
def test_pipeline():
    print("\n" + "=" * 72)
    print("TEST 2: Pipeline comparison on 20 random semiprimes (30-60d)")
    print("=" * 72)

    random.seed(2026_03_17)
    semiprimes = []
    for nd in range(30, 62, 2):  # 30,32,...,60 => 16
        n, p, q = make_semiprime(nd)
        semiprimes.append((nd, n, p, q))
    for nd in [35, 42, 48, 55]:
        n, p, q = make_semiprime(nd)
        semiprimes.append((nd, n, p, q))
    semiprimes.sort(key=lambda x: x[0])

    def get_B1(nd):
        return min(500000, max(50000, 10 ** (nd // 6)))

    print(f"\n{'Digits':>6s} | {'WITHOUT berggren':^28s} | {'WITH berggren':^28s} | Note")
    print("-" * 95)

    mc_wo = {}; mc_w = {}
    tt_wo = 0; tt_w = 0
    berg_unique = 0

    for nd, n, p, q in semiprimes:
        B1 = get_B1(nd)

        random.seed(nd * 1000 + 1)
        f1, m1, t1 = run_pipeline_without(n, B1)
        mc_wo[m1] = mc_wo.get(m1, 0) + 1
        tt_wo += t1

        random.seed(nd * 1000 + 1)
        f2, m2, t2 = run_pipeline_with(n, B1)
        mc_w[m2] = mc_w.get(m2, 0) + 1
        tt_w += t2

        note = ""
        if m2 == "berggren":
            if m1 == "FAIL":
                note = "BERGGREN UNIQUE!"
                berg_unique += 1
            else:
                note = "berggren faster"

        ok1 = "FOUND" if f1 else "FAIL"
        ok2 = "FOUND" if f2 else "FAIL"
        print(f"  {nd:3d}d  | {ok1:5s} {m1:8s} {t1:6.2f}s   "
              f"| {ok2:5s} {m2:8s} {t2:6.2f}s   | {note}")

    found_wo = sum(1 for _, f, _, _ in
                   [(nd, run_pipeline_without(n, get_B1(nd))[0], None, None)
                    for nd, n, _, _ in []] if f)

    found_wo = sum(1 for k, v in mc_wo.items() if k != "FAIL" for _ in range(v))
    found_w = sum(1 for k, v in mc_w.items() if k != "FAIL" for _ in range(v))

    print(f"\n  WITHOUT: {found_wo}/{len(semiprimes)} found, {tt_wo:.1f}s total")
    print(f"  Methods: {mc_wo}")
    print(f"\n  WITH:    {found_w}/{len(semiprimes)} found, {tt_w:.1f}s total")
    print(f"  Methods: {mc_w}")
    print(f"\n  Berggren unique finds: {berg_unique}")
    if tt_wo > 0:
        print(f"  Time ratio (with/without): {tt_w / tt_wo:.2f}x")


# =========================================================================
# TEST 3: Timing comparison (berggren overhead)
# =========================================================================
def test_timing():
    print("\n" + "=" * 72)
    print("TEST 3: Berggren timing overhead")
    print("=" * 72)

    random.seed(777)

    for nd in [30, 40, 50, 60]:
        n, p, q = make_semiprime(nd)
        B1 = min(500000, max(50000, 10 ** (nd // 6)))

        t0 = time.time()
        berggren_pm1(n, B1=B1, verbose=False)
        tb = time.time() - t0

        t0 = time.time()
        pollard_pm1(n, B1=B1, B2=B1 * 10, verbose=False)
        tp = time.time() - t0

        t0 = time.time()
        williams_pp1(n, B1=B1, B2=B1 * 10, max_seeds=6, verbose=False)
        tw = time.time() - t0

        t0 = time.time()
        gaussian_pm1(n, B1=B1, B2=B1 * 10, verbose=False)
        tg = time.time() - t0

        print(f"  {nd}d B1={B1:>7d}: berg={tb:.2f}s  p-1={tp:.2f}s"
              f"  p+1={tw:.2f}s  gauss={tg:.2f}s"
              f"  | berg/p-1={tb/tp:.1f}x  berg/p+1={tb/tw:.2f}x")


# =========================================================================
# TEST 4: Seed effectiveness analysis
# =========================================================================
def test_seeds():
    print("\n" + "=" * 72)
    print("TEST 4: Which Berggren seeds are most effective")
    print("=" * 72)

    random.seed(555)
    seed_params = [3, 5, 7, 4, 6, 9]
    seed_hits = [0] * len(seed_params)
    total_tests = 0

    # Build smooth-factor semiprimes
    q = int(next_prime(10**18))
    for _ in range(100):
        m = 1
        for pp in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]:
            m *= pp ** random.randint(0, 2)
        if m < 10**10 or m > 10**18:
            continue
        cand = m + 1
        if not is_prime(cand):
            cand = m - 1
            if not is_prime(cand):
                continue
        p = int(cand)
        n = mpz(p * q)
        total_tests += 1
        B1 = 50000

        for si, P in enumerate(seed_params):
            v = mpz(P)
            for pp in _SMALL_PRIMES:
                if pp > B1:
                    break
                pk = pp
                while pk * pp <= B1:
                    pk *= pp
                # Lucas chain
                if pk == 0:
                    continue
                vl = v
                vh = (v * v - 2) % n
                for bit in bin(pk)[3:]:
                    if bit == '1':
                        vl = (vl * vh - v) % n
                        vh = (vh * vh - 2) % n
                    else:
                        vh = (vl * vh - v) % n
                        vl = (vl * vl - 2) % n
                v = vl

            g = gmpy2.gcd(v - 2, n)
            if 1 < g < n:
                seed_hits[si] += 1

    print(f"\n  {total_tests} smooth-factor semiprimes, B1=50000:")
    for i, P in enumerate(seed_params):
        bar = "#" * seed_hits[i]
        print(f"    P={P}: {seed_hits[i]:3d}/{total_tests} {bar}")


if __name__ == "__main__":
    print("v35_test_berggren.py -- Berggren Resonance p-1/p+1 Benchmark")
    print("=" * 72)

    test_smooth_factors()
    test_timing()
    test_pipeline()
    test_seeds()

    print("\n" + "=" * 72)
    print("DONE")
