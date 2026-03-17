#!/usr/bin/env python3
"""
B3 Congruence Engine — CFRAC-based factoring with B3 smoothness ideas.

Uses continued fraction expansion of sqrt(N) to generate relations:
  P_k^2 ≡ r_k (mod N)  where |r_k| < 2*sqrt(N)

The convergent numerators P_k grow rapidly (wrapping mod N),
creating the CRT mixing needed for the congruence of squares method.

Novel elements:
- Direct trial division (no sieve arrays) — low memory
- Large prime variation for ~2x more relations
- Unlimited relations from the CF expansion
"""
import time, math, sys, random
import gmpy2
from gmpy2 import mpz, isqrt, gcd, is_prime, next_prime, legendre

def b3_congruence_factor(N, verbose=True, time_limit=600):
    N = mpz(N)
    nd = len(str(N))
    nb = int(gmpy2.log2(N)) + 1

    # Quick checks
    if N <= 1: return 0
    if N % 2 == 0: return 2
    for p in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        if N % p == 0: return int(p)
    if is_prime(N): return int(N)
    sq = isqrt(N)
    if sq * sq == N: return int(sq)

    t0 = time.time()
    N_int = int(N)

    # Parameters
    ln_n = float(gmpy2.log(N))
    ln_ln_n = math.log(max(ln_n, 2.0))
    L_exp = math.sqrt(ln_n * ln_ln_n)
    alpha = 0.55
    B = int(math.exp(alpha * L_exp))
    B = max(B, 500)
    B = min(B, 500_000)

    # Factor base
    fb = [2]
    p = mpz(3)
    while p <= B:
        if legendre(N, p) >= 0:
            fb.append(int(p))
        p = next_prime(p)
    fb_size = len(fb)
    needed = int(fb_size * 1.05) + 10
    lp_bound = min(B * 100, B * B)

    if verbose:
        print(f"B3-Congruence: {nd}d ({nb}b), B={B:,}, |FB|={fb_size:,}, "
              f"need={needed:,}, LP<={lp_bound:,}")

    smooth = []  # (x_mod_N, sign, exps)
    partials = {}
    n_lp = 0
    n_full = 0
    n_checked = 0

    # CF expansion of sqrt(N)
    sqrtN = isqrt(N)
    a0 = sqrtN

    # Track P_k mod N only (for x values), and P_k mod small primes for sieving
    P_prev_mod = mpz(1)
    P_curr_mod = a0 % N

    # CF state
    m_cf = mpz(0)
    d_cf = mpz(1)
    a_cf = a0

    half_N = N_int // 2
    report_interval = max(100, 5000 // max(1, nd // 5))

    while len(smooth) < needed:
        if time.time() - t0 > time_limit * 0.9:
            break

        # Next partial quotient
        m_cf = a_cf * d_cf - m_cf
        d_cf = (N - m_cf * m_cf) // d_cf
        if d_cf == 0:
            break
        a_cf = (a0 + m_cf) // d_cf

        # Update P_k mod N
        P_new_mod = (a_cf * P_curr_mod + P_prev_mod) % N
        P_prev_mod = P_curr_mod
        P_curr_mod = P_new_mod

        # Compute residue: r_k = P_k^2 mod N, adjusted to [-N/2, N/2]
        r_mod = int(pow(P_curr_mod, 2, N))
        if r_mod > half_N:
            r_k = r_mod - N_int  # negative
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

        # Direct GCD check
        g = int(gcd(mpz(abs(r_k)), N))
        if 1 < g < N_int:
            if verbose:
                print(f"\n  *** DIRECT FACTOR: {g} ({time.time()-t0:.1f}s) ***")
            return g

        # Trial divide |r_k| over FB
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

        # Check if cofactor is a FB prime
        if cof > 1 and cof <= B:
            for i in range(fb_size):
                if fb[i] == cof:
                    exps[i] += 1
                    cof = 1
                    break

        x_mod = int(P_curr_mod)

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

        # Progress
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

    # GF(2) Gaussian elimination
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

    # Factor extraction
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


# CLI
if __name__ == "__main__":
    def _gen(nd, rng):
        half = int(nd * 3.32 / 2)
        while True:
            p = int(next_prime(mpz(rng.getrandbits(half))))
            q = int(next_prime(mpz(rng.getrandbits(half))))
            if p != q:
                N = p * q
                if len(str(N)) >= nd - 1:
                    return N, p, q

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("B3-Congruence Quick Test")
        rng = random.Random(123)
        for nd in [15, 20, 25, 30, 35]:
            N, p, q = _gen(nd, rng)
            print(f"\n  {len(str(N))}d: N={N}")
            t0 = time.time()
            f = b3_congruence_factor(N, verbose=False, time_limit=120)
            elapsed = time.time() - t0
            ok = f and f > 1 and N % f == 0
            print(f"    {'PASS' if ok else 'FAIL'}: {elapsed:.1f}s")

    elif len(sys.argv) > 1 and sys.argv[1] == "bench":
        print("=" * 70)
        print("B3-Congruence Engine Benchmark")
        print("=" * 70)
        rng = random.Random(42)
        results = []
        for nd in [20, 25, 30, 35, 40, 45, 50, 55]:
            N, p, q = _gen(nd, rng)
            nd_actual = len(str(N))
            print(f"\n--- {nd_actual}d ---")
            t0 = time.time()
            f = b3_congruence_factor(N, verbose=True, time_limit=300)
            elapsed = time.time() - t0
            ok = f and f > 1 and N % f == 0
            results.append((nd_actual, elapsed, "PASS" if ok else "FAIL"))
            print(f"  {'PASS' if ok else 'FAIL'} in {elapsed:.1f}s")

        print(f"\n{'=' * 70}")
        print(f"{'Digits':>6} {'Time':>8} {'Result':>8}")
        for nd, t, r in results:
            print(f"{nd:>6} {t:>7.1f}s {r:>8}")

    elif len(sys.argv) > 1:
        N = int(sys.argv[1])
        tl = int(sys.argv[2]) if len(sys.argv) > 2 else 300
        f = b3_congruence_factor(N, verbose=True, time_limit=tl)
        if f and f > 1:
            print(f"\nResult: {N} = {f} * {N // f}")
        else:
            print(f"\nFailed")
    else:
        print("Usage: b3_congruence_engine.py test|bench|<N> [timeout]")
