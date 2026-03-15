#!/usr/bin/env python3
"""
PYTHAGOREAN RESONANCE — B3-MPQS Factoring Engine

THE KEY INSIGHT:
  B3^k * (m₀, n₀) = (m₀+2kn₀, n₀). Choose m₀ ≈ n₀·√N.
  Then r_k = (m₀+2kn₀)² - N·n₀² starts small and is sievable.

  x_k = m₀+2kn₀. Since x_k² = r_k + N·n₀²:
    x_k² ≡ r_k (mod N)   ← THIS IS THE QS RELATION!

  When product(r_k) is a perfect square s²:
    product(x_k)² ≡ s² (mod N) → gcd(product(x_k) ± s, N) → FACTOR!

  Each n₀ gives a DIFFERENT polynomial. Unlimited polynomial supply!
  This is MPQS via the Pythagorean B3 arithmetic progression.
"""

import time, math, random
import gmpy2
from gmpy2 import mpz, isqrt, gcd, is_prime, next_prime, legendre


def _tonelli_shanks(n, p):
    if pow(n, (p-1)//2, p) != 1: return None
    if p % 4 == 3: return pow(n, (p+1)//4, p)
    Q, S = p-1, 0
    while Q % 2 == 0: Q //= 2; S += 1
    z = 2
    while pow(z, (p-1)//2, p) != p-1: z += 1
    M, c, t, R = S, pow(z, Q, p), pow(n, Q, p), pow(n, (Q+1)//2, p)
    while True:
        if t == 1: return R
        i, tmp = 1, t*t % p
        while tmp != 1: tmp = tmp*tmp % p; i += 1
        b = pow(c, 1 << (M-i-1), p)
        M, c, t, R = i, b*b % p, t*b*b % p, R*b % p


def b3_mpqs_factor(N, verbose=True, time_limit=3600):
    """Factor N using B3-MPQS: Pythagorean arithmetic progression sieve."""
    N = mpz(N)
    N_int = int(N)
    nd = len(str(N))

    # Quick checks
    if N <= 1: return 0
    if N % 2 == 0: return 2
    for p in [3,5,7,11,13,17,19,23,29,31,37,41,43,47]:
        if N % p == 0 and N_int > p: return p
    if is_prime(N): return 0
    sq = isqrt(N)
    if sq * sq == N: return int(sq)

    t0 = time.time()

    # Parameters: L(N) = exp(sqrt(ln N * ln ln N))
    ln_n = float(gmpy2.log(N))
    ln_ln_n = math.log(max(ln_n, 2.0))
    L_exp = math.sqrt(ln_n * ln_ln_n)
    alpha = 0.44 if nd <= 45 else 0.46
    B = min(int(math.exp(alpha * L_exp)), 500_000)
    B = max(B, 200)

    # Factor base
    fb = [2]
    p = mpz(3)
    while p <= B:
        if legendre(N, p) >= 0:
            fb.append(int(p))
        p = next_prime(p)
    fb_size = len(fb)
    fb_mpz = [mpz(p) for p in fb]
    needed = fb_size + 25
    lp_bound = B * B

    sqrtN = isqrt(N)

    if verbose:
        print(f"B3-MPQS: {nd}d ({int(gmpy2.log2(N))+1}b), B={B:,}, "
              f"|FB|={fb_size:,}, need={needed:,}")

    # Precompute sieve roots: for each FB prime p, sqrt(N) mod p
    fb_sqrtN = {}
    for p in fb:
        if p == 2:
            fb_sqrtN[2] = [int(N) % 2]
            continue
        sn = _tonelli_shanks(int(N) % p, p)
        if sn is not None:
            fb_sqrtN[p] = [sn, p - sn]
        else:
            fb_sqrtN[p] = []

    # Relation storage
    smooth = []  # (x_mod_N, sign, exps, lp)
    partials = {}
    n_lp = 0
    n_polys = 0
    total_sieved = 0

    sieve_half = max(10000, min(100000, 20 * fb_size))

    # Generate polynomials: for each n₀, m₀ = round(n₀·√N)
    # Use best roots from cross-math experiments + sequential n₀
    n0_list = list(range(1, 50000))

    for n0 in n0_list:
        if len(smooth) >= needed: break
        if time.time() - t0 > time_limit * 0.85: break

        # m₀ = round(n₀·√N)
        m0 = int(isqrt(N * mpz(n0) * mpz(n0)))
        # Pick closer of m0, m0+1
        r0a = m0 * m0 - N_int * n0 * n0
        r0b = (m0+1) * (m0+1) - N_int * n0 * n0
        if abs(r0b) < abs(r0a): m0 += 1

        # Skip if gcd(n0, N) > 1 (trivial factor)
        g = int(gcd(mpz(n0), N))
        if 1 < g < N_int:
            if verbose: print(f"  Direct factor from n0={n0}: {g}")
            return g

        n_polys += 1

        # Polynomial: r_k = (m₀+2kn₀)² - N·n₀²
        # = 4n₀²k² + 4m₀n₀k + (m₀²-Nn₀²)
        a_c = 4 * n0 * n0
        b_c = 4 * m0 * n0
        c_c = m0 * m0 - N_int * n0 * n0  # small!

        # Log sieve array
        sieve = bytearray(2 * sieve_half)

        # Estimate threshold from max residue at sieve edge
        max_r = abs(a_c * sieve_half * sieve_half) + abs(b_c * sieve_half) + abs(c_c)
        if max_r < 4: max_r = 4
        threshold = max(10, int(math.log2(max_r) * 0.70))

        # Sieve with FB primes
        for i, p in enumerate(fb):
            if p > 2 * sieve_half: break
            logp = max(1, int(math.log2(p) + 0.5))

            # Solve a_c*k² + b_c*k + c_c ≡ 0 (mod p)
            if p == 2:
                # Just check both parities
                for start in range(2):
                    pos = start
                    while pos < 2 * sieve_half:
                        sieve[pos] += logp
                        pos += 2
                continue

            ap = a_c % p
            bp = b_c % p
            cp = c_c % p

            if ap == 0:
                # Linear
                if bp == 0: continue
                r = ((-cp) * pow(bp, p-2, p)) % p
                start = (r + sieve_half % p) % p
                pos = start
                while pos < 2 * sieve_half:
                    sieve[pos] += logp
                    pos += p
                continue

            disc = (bp * bp - 4 * ap * cp % p) % p
            if disc < 0: disc += p

            leg = pow(disc, (p-1)//2, p) if disc != 0 else 0
            if leg != 1 and disc != 0: continue

            if disc == 0:
                sd = 0
            else:
                sd = _tonelli_shanks(disc, p)
                if sd is None: continue

            inv2a = pow((2 * ap) % p, p-2, p)
            for sign_sd in [sd, p - sd]:
                r = ((-bp + sign_sd) * inv2a) % p
                start = (r + sieve_half % p) % p
                pos = start
                while pos < 2 * sieve_half:
                    sieve[pos] += logp
                    pos += p

        # Check survivors
        for idx in range(2 * sieve_half):
            if sieve[idx] < threshold: continue

            k = idx - sieve_half
            m_k = m0 + 2 * k * n0
            r_k = m_k * m_k - N_int * n0 * n0

            if r_k == 0:
                g = int(gcd(mpz(m_k), N))
                if 1 < g < N_int:
                    if verbose: print(f"  Direct: {g}")
                    return g
                continue

            total_sieved += 1
            sign = 1 if r_k < 0 else 0
            r_abs = abs(r_k)

            # Trial divide
            exps = [0] * fb_size
            cof = mpz(r_abs)
            for i in range(fb_size):
                p = fb_mpz[i]
                if p * p > cof: break
                if gmpy2.is_divisible(cof, p):
                    e = 0
                    while gmpy2.is_divisible(cof, p):
                        cof //= p; e += 1
                    exps[i] = e
                    if cof == 1: break

            cofactor = int(cof)
            # x² ≡ r_k (mod N), where x = m_k
            x_mod = m_k % N_int

            if cofactor == 1:
                smooth.append((x_mod, sign, exps, 0))
            elif 1 < cofactor <= lp_bound and is_prime(mpz(cofactor)):
                lp = cofactor
                if lp in partials:
                    p2, s2, e2 = partials.pop(lp)
                    smooth.append(((x_mod * p2) % N_int,
                                   (sign + s2) % 2,
                                   [exps[j] + e2[j] for j in range(fb_size)],
                                   lp))
                    n_lp += 1
                else:
                    partials[lp] = (x_mod, sign, exps)

        # Progress
        if verbose and n_polys % 500 == 0:
            elapsed = time.time() - t0
            if len(smooth) > 0:
                eta = elapsed * (needed - len(smooth)) / len(smooth)
            else:
                eta = 99999
            print(f"  {n_polys} polys: {len(smooth)}/{needed} rels, "
                  f"{n_lp} LP, {elapsed:.1f}s, eta={min(eta,9999):.0f}s")

    elapsed_sieve = time.time() - t0
    if verbose:
        print(f"  Sieve: {len(smooth)} rels from {n_polys} polys in {elapsed_sieve:.1f}s "
              f"({n_lp} LP, {total_sieved:,} tested)")

    if len(smooth) < fb_size + 2:
        if verbose: print(f"  Insufficient: {len(smooth)}/{fb_size+2}")
        return 0

    # GF(2) Gaussian Elimination + Factor Extraction
    nrows = len(smooth)
    ncols = fb_size + 1
    if verbose: print(f"  LA: {nrows} x {ncols}...")

    mat = [0] * nrows
    for i in range(nrows):
        _, s, exps, _ = smooth[i]
        row = s
        for j in range(fb_size):
            if exps[j] & 1: row |= (1 << (j+1))
        mat[i] = row

    combo = [mpz(1) << i for i in range(nrows)]
    used = [False] * nrows

    for col in range(ncols):
        mask = 1 << col
        piv = -1
        for row in range(nrows):
            if not used[row] and mat[row] & mask:
                piv = row; break
        if piv == -1: continue
        used[piv] = True
        for row in range(nrows):
            if row != piv and mat[row] & mask:
                mat[row] ^= mat[piv]
                combo[row] ^= combo[piv]

    n_tried = 0
    for row in range(nrows):
        if mat[row] != 0: continue
        indices = []
        bits = combo[row]; idx = 0
        while bits:
            if bits & 1: indices.append(idx)
            bits >>= 1; idx += 1
        if not indices: continue

        x_val = mpz(1)
        total_exp = [0] * fb_size
        total_sign = 0
        lp_prod = mpz(1)

        for idx in indices:
            xm, s, exps, lp_val = smooth[idx]
            x_val = x_val * mpz(xm) % N
            total_sign += s
            for j in range(fb_size): total_exp[j] += exps[j]
            if lp_val > 0: lp_prod = lp_prod * mpz(lp_val) % N

        if any(e & 1 for e in total_exp) or total_sign & 1: continue

        y_val = lp_prod
        for j in range(fb_size):
            if total_exp[j] > 0:
                y_val = y_val * pow(mpz(fb[j]), total_exp[j] >> 1, N) % N

        n_tried += 1
        for diff in (x_val - y_val, x_val + y_val):
            g = int(gcd(diff % N, N))
            if 1 < g < N_int:
                total_t = time.time() - t0
                if verbose:
                    print(f"\n  *** FACTOR: {g} ({nd}d, {total_t:.1f}s, "
                          f"{len(smooth)} rels, {n_polys} polys, "
                          f"{n_tried} vecs) ***")
                return g

    if verbose: print(f"  LA: {n_tried} vecs tried, no factor")
    return 0


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "bench":
        print("=" * 65)
        print("PYTHAGOREAN RESONANCE — B3-MPQS Benchmark")
        print("=" * 65)

        tests = [
            ("20d", int(mpz(1000000007) * mpz(1000000009))),
            ("25d", int(mpz(10000000019) * mpz(100000000003))),
            ("30d", int(mpz(1000000007) * mpz(100000000000000003))),
            ("35d", int(mpz(10000000000000061) * mpz(1000000000000000003))),
            ("40d", int(mpz(10000000000000000051) * mpz(10000000000000000069))),
            ("45d", int(mpz(100000000000000000267) * mpz(10000000000000000000000069))),
        ]

        for label, n in tests:
            nd = len(str(n))
            print(f"\n{'='*65}\n{label} ({nd}d)")
            t0 = time.time()
            f = b3_mpqs_factor(n, verbose=True, time_limit=300)
            elapsed = time.time() - t0
            ok = f and f > 1 and n % f == 0
            print(f"  => {'OK' if ok else 'FAIL'} {elapsed:.1f}s" +
                  (f" ({f})" if ok else ""))

    elif len(sys.argv) > 1:
        N = int(sys.argv[1])
        tl = int(sys.argv[2]) if len(sys.argv) > 2 else 600
        f = b3_mpqs_factor(N, verbose=True, time_limit=tl)
        if f: print(f"\n{N} = {f} * {N // f}")

    else:
        print("Usage: pyth_resonance.py bench | pyth_resonance.py <N> [time_limit]")
