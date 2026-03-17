#!/usr/bin/env python3
"""
Pythagorean Smooth Factor — Multiplier-enhanced CFRAC with smoothness analysis.

RESULTS SUMMARY (2026-03-15):

  Smoothness advantage (vs single-k Fermat, 30K samples):
    Multi-k Fermat (B3 walk):  2-5x better  (residues half the bit-size)
    CF expansion sqrt(N):      30-60x better (residues ~sqrt(N) not ~j*sqrt(N))
    CF expansion sqrt(kN):     20-82x better (best k via Knuth-Schroeppel)
    Random x^2 mod N:          0 smooths     (residues ~N bits, hopeless)

  Factoring benchmark (vs B3-CFRAC baseline):
    20d: 0.02s (0.8x)   28d: 0.87s (1.6x faster)
    22d: 0.05s (1.1x)    30d: 2.41s (1.4x faster)
    24d: 0.09s (1.1x)    33d: 13.0s (0.9x)
    26d: 0.35s (0.8x)    35d: 17.3s (0.9x)
                          38d: 110s  (B3 FAILS, PythSmooth succeeds!)

  KEY FINDING: The Pythagorean B3 walk's smoothness advantage (3-276x in Z)
  does NOT directly transfer to factoring mod N. The advantage of A=(m-n)(m+n)
  being smooth in Z is irrelevant when we need smoothness of x^2 mod N.

  WHAT DOES HELP: Knuth-Schroeppel multiplier selection (choosing k so that
  kN has many small quadratic residues) provides 1.4-1.6x speedup at 28-30d
  and enables factoring at 38d where the baseline fails.

  The CF expansion provides the real smoothness engine (30-80x vs Fermat),
  and multiplier selection is the practical lever.

Two components:
1. FACTORING: CFRAC with Knuth-Schroeppel multiplier selection.
   CF expansion of sqrt(kN) generates P_k^2 mod kN residues.
   Trial division + large prime variation + GF(2) Gauss elimination.

2. ANALYSIS: compare_smooth_rates() measures empirical smoothness across
   Fermat, multi-k Fermat, CF, and random methods.
"""

import time
import math
import sys
import random
import gmpy2
from gmpy2 import mpz, isqrt, gcd, is_prime, next_prime, legendre


def pyth_smooth_factor(N, verbose=True, time_limit=300):
    """Factor N using multiplier-enhanced CFRAC."""
    N = mpz(N)
    nd = len(str(N))
    nb = int(gmpy2.log2(N)) + 1
    N_int = int(N)

    # Quick checks
    if N <= 1: return 0
    if N % 2 == 0: return 2
    for p in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        if N % p == 0: return int(p)
    if is_prime(N): return int(N)
    sq = isqrt(N)
    if sq * sq == N: return int(sq)

    t0 = time.time()

    # Parameters
    ln_n = float(gmpy2.log(N))
    ln_ln_n = math.log(max(ln_n, 2.0))
    L_exp = math.sqrt(ln_n * ln_ln_n)
    alpha = 0.55
    B = int(math.exp(alpha * L_exp))
    B = max(B, 500)
    B = min(B, 500_000)

    # Knuth-Schroeppel multiplier selection
    # Score k by sum of log(p)/p for small primes p where (kN/p) = 0 or 1
    best_k = 1
    best_score = -1
    for k in range(1, 100):
        kN = k * N_int
        # Skip if kN is a perfect square
        skN = isqrt(mpz(kN))
        if skN * skN == kN:
            continue
        score = 0.0
        p = 2
        while p <= min(B, 200):
            kN_mod_p = kN % p
            if kN_mod_p == 0:
                score += math.log(p) / p * 2  # bonus for p | kN
            elif pow(kN_mod_p, (p - 1) // 2, p) <= 1 if p > 2 else True:
                score += math.log(p) / p
            p = int(next_prime(mpz(p)))
        # Penalize large k slightly (larger residues)
        score -= 0.5 * math.log(k) if k > 1 else 0
        if score > best_score:
            best_score = score
            best_k = k

    k = best_k
    kN = mpz(k * N_int)

    # Factor base for kN
    fb = [2]
    p = mpz(3)
    while p <= B:
        if legendre(kN, p) >= 0:
            fb.append(int(p))
        p = next_prime(p)
    fb_size = len(fb)
    needed = int(fb_size * 1.05) + 10
    lp_bound = min(B * 100, B * B)
    fb_set = set(fb)

    if verbose:
        print(f"PythSmooth CFRAC: {nd}d ({nb}b), k={k}, B={B:,}, "
              f"|FB|={fb_size:,}, need={needed:,}")

    smooth = []
    partials = {}
    n_full = 0
    n_lp = 0
    n_checked = 0
    half_kN = int(kN) // 2

    # CF expansion of sqrt(kN)
    sqrtKN = isqrt(kN)
    a0 = sqrtKN
    P_prev_mod = mpz(1)
    P_curr_mod = a0 % kN
    m_cf = mpz(0)
    d_cf = mpz(1)
    a_cf = a0

    report_interval = max(100, 5000 // max(1, nd // 5))

    while len(smooth) < needed:
        if time.time() - t0 > time_limit * 0.9:
            break

        # Next partial quotient
        m_cf = a_cf * d_cf - m_cf
        d_cf = (kN - m_cf * m_cf) // d_cf
        if d_cf == 0:
            break
        a_cf = (a0 + m_cf) // d_cf

        P_new_mod = (a_cf * P_curr_mod + P_prev_mod) % kN
        P_prev_mod = P_curr_mod
        P_curr_mod = P_new_mod

        # Residue: P_k^2 mod kN, centered
        r_mod = int(pow(P_curr_mod, 2, kN))
        kN_int = int(kN)
        if r_mod > half_kN:
            r_k = r_mod - kN_int
        else:
            r_k = r_mod

        if r_k == 0:
            g = int(gcd(P_curr_mod, N))
            if 1 < g < N_int:
                if verbose:
                    print(f"\n  *** PERFECT: {g} ({time.time()-t0:.1f}s) ***")
                return g
            continue

        n_checked += 1

        # Direct GCD
        g = int(gcd(mpz(abs(r_k)), N))
        if 1 < g < N_int:
            if verbose:
                print(f"\n  *** DIRECT: {g} ({time.time()-t0:.1f}s) ***")
            return g

        # Trial divide
        sign = 1 if r_k < 0 else 0
        cof = abs(r_k)
        exps = [0] * fb_size
        for i in range(fb_size):
            p2 = fb[i]
            if p2 * p2 > cof:
                break
            if cof % p2 == 0:
                e = 0
                while cof % p2 == 0:
                    cof //= p2
                    e += 1
                exps[i] = e
                if cof == 1:
                    break

        if cof > 1 and cof <= B and cof in fb_set:
            for i in range(fb_size):
                if fb[i] == cof:
                    exps[i] += 1
                    cof = 1
                    break

        # x value for the congruence: P_curr_mod, but we need mod N not mod kN
        x_mod = int(P_curr_mod % N)

        if cof == 1:
            smooth.append((x_mod, sign, exps))
            n_full += 1
        elif 1 < cof <= lp_bound and is_prime(mpz(cof)):
            lp = cof
            if lp in partials:
                x2, s2, e2 = partials.pop(lp)
                cs = (sign + s2) % 2
                ce = [exps[j] + e2[j] for j in range(fb_size)]
                lp_inv = int(gmpy2.invert(mpz(lp), N))
                cx = (x_mod * x2 % N_int) * lp_inv % N_int
                smooth.append((cx, cs, ce))
                n_lp += 1
            else:
                partials[lp] = (x_mod, sign, exps)

        if verbose and n_checked % report_interval == 0:
            elapsed = time.time() - t0
            rate = len(smooth) / max(elapsed, 0.01)
            eta = (needed - len(smooth)) / max(rate, 0.001)
            print(f"  CF step {n_checked}: {len(smooth)}/{needed} "
                  f"({n_full}F+{n_lp}LP), "
                  f"rate={rate:.1f}/s eta={min(eta, 99999):.0f}s [{elapsed:.0f}s]")

    elapsed_collect = time.time() - t0
    if verbose:
        print(f"\n  Collected: {len(smooth):,} ({n_full}F+{n_lp}LP) "
              f"in {elapsed_collect:.1f}s")
        print(f"  {n_checked:,} CF steps")
        if n_checked > 0:
            print(f"  Smooth rate: {(n_full + n_lp) / max(n_checked, 1) * 100:.3f}%")

    if len(smooth) < fb_size + 2:
        if verbose:
            print(f"  Insufficient: {len(smooth)}/{fb_size + 2}")
        return 0

    # --- GF(2) GAUSSIAN ELIMINATION ---
    nrows = len(smooth)
    ncols = fb_size + 1
    if verbose:
        print(f"  LA: {nrows} x {ncols}")

    la_t0 = time.time()
    mat = []
    for _, sign, exps in smooth:
        row = sign
        for j, e in enumerate(exps):
            if e % 2 == 1:
                row |= (1 << (j + 1))
        mat.append(row)

    combo = [mpz(1) << i for i in range(nrows)]
    used = [False] * nrows
    for col in range(ncols):
        mask = 1 << col
        piv = -1
        for row in range(nrows):
            if not used[row] and mat[row] & mask:
                piv = row
                break
        if piv == -1:
            continue
        used[piv] = True
        for row in range(nrows):
            if row != piv and mat[row] & mask:
                mat[row] ^= mat[piv]
                combo[row] ^= combo[piv]

    null_vecs = []
    for row in range(nrows):
        if mat[row] == 0:
            indices = []
            bits = combo[row]
            idx = 0
            while bits:
                if bits & 1:
                    indices.append(idx)
                bits >>= 1
                idx += 1
            if indices:
                null_vecs.append(indices)

    if verbose:
        print(f"  LA: {time.time() - la_t0:.1f}s, {len(null_vecs)} null vecs")

    # --- FACTOR EXTRACTION ---
    for indices in null_vecs:
        x_val = mpz(1)
        total_exp = [0] * fb_size
        total_sign = 0
        for idx in indices:
            xk, sign, exps = smooth[idx]
            x_val = x_val * mpz(xk) % N
            total_sign += sign
            for j in range(fb_size):
                total_exp[j] += exps[j]

        if any(e % 2 != 0 for e in total_exp) or total_sign % 2 != 0:
            continue

        y_val = mpz(1)
        for j, e in enumerate(total_exp):
            if e > 0:
                y_val = y_val * pow(mpz(fb[j]), e // 2, N) % N

        for diff in [x_val - y_val, x_val + y_val]:
            g = int(gcd(diff % N, N))
            if 1 < g < N_int:
                total_t = time.time() - t0
                if verbose:
                    print(f"\n  *** FACTOR: {g} ({nd}d, {total_t:.1f}s, "
                          f"{len(smooth)} rels [{n_full}F+{n_lp}LP]) ***")
                return g

    if verbose:
        print(f"  {len(null_vecs)} null vecs, no factor")
    return 0


def compare_smooth_rates(N, B=1000, n_samples=50000):
    """Compare smoothness rates across methods."""
    N = int(N)
    sqrtN = int(isqrt(mpz(N)))
    half_N = N // 2

    fb = []
    p = mpz(2)
    while p <= B:
        fb.append(int(p))
        p = next_prime(p)

    def is_b_smooth(val):
        if val == 0: return False
        v = abs(val)
        for pp in fb:
            if pp * pp > v: break
            while v % pp == 0: v //= pp
            if v == 1: return True
        return v <= B

    # --- Method 1: Fermat single-k ---
    n_smooth_fermat = 0
    sizes_fermat = []
    for j in range(n_samples):
        m = sqrtN + 1 + j
        r = m * m - N
        if is_b_smooth(r): n_smooth_fermat += 1
        if j < 100: sizes_fermat.append(r.bit_length())

    # --- Method 2: Random x^2 mod N ---
    rng = random.Random(42)
    n_smooth_random = 0
    sizes_random = []
    for _ in range(n_samples):
        x = rng.randrange(2, N)
        r = pow(x, 2, N)
        if r > half_N: r = r - N
        if is_b_smooth(abs(r)): n_smooth_random += 1
        if _ < 100: sizes_random.append(abs(r).bit_length())

    # --- Method 3: Multi-k Fermat (Pythagorean multipliers) ---
    n_smooth_multik = 0
    count_multik = 0
    max_k = 50
    per_k = n_samples // max_k
    for k in range(1, max_k + 1):
        kN = k * N
        sk = int(isqrt(mpz(kN)))
        for j in range(per_k):
            m = sk + 1 + j
            r = m * m - kN
            if is_b_smooth(r): n_smooth_multik += 1
            count_multik += 1

    # --- Method 4: CF expansion of sqrt(N) using d_cf as residue ---
    n_smooth_cf = 0
    sqN = isqrt(mpz(N))
    a0 = sqN
    m_cf = mpz(0); d_cf = mpz(1); a_cf = a0
    cf_steps = min(n_samples, 50000)
    for _ in range(cf_steps):
        m_cf = a_cf * d_cf - m_cf
        d_cf = (mpz(N) - m_cf * m_cf) // d_cf
        if d_cf == 0: break
        a_cf = (a0 + m_cf) // d_cf
        r_val = int(d_cf)
        if is_b_smooth(r_val): n_smooth_cf += 1

    # --- Method 5: CF expansion of sqrt(kN) with best Knuth-Schroeppel k ---
    best_k = 1; best_score = -1
    for k in range(1, 50):
        kN_t = k * N
        score = 0.0
        pp = 2
        while pp <= min(B, 100):
            kN_mod = kN_t % pp
            if kN_mod == 0:
                score += math.log(pp) / pp * 2
            elif pp == 2 or pow(kN_mod, (pp-1)//2, pp) <= 1:
                score += math.log(pp) / pp
            pp = int(next_prime(mpz(pp)))
        score -= 0.3 * math.log(k) if k > 1 else 0
        if score > best_score: best_score = score; best_k = k

    n_smooth_mkcf = 0
    kN_best = mpz(best_k * N)
    sqkN = isqrt(kN_best)
    a0b = sqkN
    m_cf = mpz(0); d_cf = mpz(1); a_cf = a0b
    for _ in range(cf_steps):
        m_cf = a_cf * d_cf - m_cf
        d_cf = (kN_best - m_cf * m_cf) // d_cf
        if d_cf == 0: break
        a_cf = (a0b + m_cf) // d_cf
        r_val = int(d_cf)
        if is_b_smooth(r_val): n_smooth_mkcf += 1

    nd = len(str(N))
    print(f"\n=== Smoothness: {nd}d N, B={B}, {n_samples} samples ===")
    print(f"  Fermat k=1:    {n_smooth_fermat:>6}/{n_samples} = "
          f"{n_smooth_fermat/n_samples*100:.4f}%  "
          f"(avg residue ~{sum(sizes_fermat)//max(len(sizes_fermat),1)}b)")
    print(f"  Random x^2:    {n_smooth_random:>6}/{n_samples} = "
          f"{n_smooth_random/n_samples*100:.4f}%  "
          f"(avg residue ~{sum(sizes_random)//max(len(sizes_random),1)}b)")
    print(f"  Multi-k Fermat:{n_smooth_multik:>6}/{count_multik} = "
          f"{n_smooth_multik/max(count_multik,1)*100:.4f}%")
    print(f"  CF sqrt(N):    {n_smooth_cf:>6}/{cf_steps} = "
          f"{n_smooth_cf/cf_steps*100:.4f}%")
    print(f"  CF sqrt({best_k}N):  {n_smooth_mkcf:>6}/{cf_steps} = "
          f"{n_smooth_mkcf/cf_steps*100:.4f}%  (best k={best_k})")

    if n_smooth_fermat > 0:
        print(f"\n  Advantage ratios vs Fermat k=1:")
        print(f"    Multi-k: {n_smooth_multik/max(n_smooth_fermat,1):.1f}x")
        print(f"    CF:      {n_smooth_cf/max(n_smooth_fermat,1):.1f}x")
        print(f"    CF(kN):  {n_smooth_mkcf/max(n_smooth_fermat,1):.1f}x")


def benchmark():
    """Benchmark Pythagorean smooth factoring vs b3_congruence."""
    rng = random.Random(2026)

    print("=" * 70)
    print("PYTHAGOREAN SMOOTH FACTOR — CFRAC + MULTIPLIER BENCHMARK")
    print("=" * 70)

    # Smoothness analysis
    print("\n--- SMOOTHNESS RATE ANALYSIS ---")
    for nd in [20, 25, 30]:
        half = nd * 332 // 200
        p = int(next_prime(mpz(rng.getrandbits(half))))
        q = int(next_prime(mpz(rng.getrandbits(half))))
        N = p * q
        B_test = max(200, int(math.exp(0.5 * math.sqrt(math.log(N) * math.log(math.log(N))))))
        B_test = min(B_test, 5000)
        compare_smooth_rates(N, B=B_test, n_samples=10000)

    # Factoring benchmark: pyth_smooth vs b3_congruence
    print("\n\n--- FACTORING BENCHMARK ---")
    try:
        from b3_congruence_engine import b3_congruence_factor
        has_b3 = True
    except ImportError:
        has_b3 = False

    print(f"{'Digits':>6} {'PythSmooth':>12} {'B3-CFRAC':>12} {'Speedup':>8}")
    print("-" * 45)

    results = []
    for nd in [20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40]:
        half = nd * 332 // 200
        p = int(next_prime(mpz(rng.getrandbits(half))))
        q = int(next_prime(mpz(rng.getrandbits(half))))
        N = p * q
        actual_nd = len(str(N))

        # PythSmooth
        t0 = time.time()
        f1 = pyth_smooth_factor(N, verbose=False, time_limit=120)
        t_pyth = time.time() - t0
        ok1 = "OK" if (f1 > 1 and N % f1 == 0) else "FAIL"

        # B3-CFRAC
        t_b3 = -1
        ok2 = "N/A"
        if has_b3:
            t0 = time.time()
            f2 = b3_congruence_factor(N, verbose=False, time_limit=120)
            t_b3 = time.time() - t0
            ok2 = "OK" if (f2 > 1 and N % f2 == 0) else "FAIL"

        speedup = f"{t_b3/t_pyth:.2f}x" if t_b3 > 0 and t_pyth > 0 else "N/A"
        print(f"{actual_nd:>6} {t_pyth:>7.2f}s {ok1:>4} "
              f"{t_b3:>7.2f}s {ok2:>4} {speedup:>8}")
        results.append((actual_nd, t_pyth, ok1, t_b3, ok2))

        if t_pyth > 60 and t_b3 > 60:
            print("  (stopping)")
            break

    print("\n--- SUMMARY ---")
    for nd, tp, ok1, tb, ok2 in results:
        sp = f"{tb/tp:.2f}x" if tb > 0 and tp > 0 else "N/A"
        print(f"  {nd}d: PythSmooth={tp:.2f}s[{ok1}]  B3={tb:.2f}s[{ok2}]  speedup={sp}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "bench":
            benchmark()
        elif sys.argv[1] == "smooth":
            rng = random.Random(2026)
            for nd in [20, 25, 30, 35]:
                half = nd * 332 // 200
                p = int(next_prime(mpz(rng.getrandbits(half))))
                q = int(next_prime(mpz(rng.getrandbits(half))))
                N = p * q
                B_test = max(200, int(math.exp(0.5 * math.sqrt(math.log(N) * math.log(math.log(N))))))
                compare_smooth_rates(N, B=B_test, n_samples=30000)
        else:
            N = mpz(sys.argv[1])
            f = pyth_smooth_factor(N)
            if f > 1:
                print(f"\nResult: {N} = {f} * {N // f}")
            else:
                print(f"\nFailed to factor {N}")
    else:
        benchmark()
