#!/usr/bin/env python3
"""
B3 Arithmetic Progression Sieve — Pythagorean Tree Factoring

Key insight: B3 = [[1,2],[0,1]] is parabolic (eigenvalue 1, multiplicity 2).
B3^k * (m,n) = (m+2kn, n), so n is FIXED along B3 paths.

A_k = (m+2kn)² - n² = (m+2kn-n)(m+2kn+n)

For fixed (m₀, n₀), this is a QUADRATIC polynomial in k:
  A_k = 4n₀² k² + 4m₀n₀ k + (m₀² - n₀²)

This is EXACTLY the kind of polynomial QS sieves over!
We can sieve A_k for smoothness just like SIQS sieves Q(x).

Strategy:
1. For each root (m₀, n₀), generate the polynomial A_k = f(k)
2. Sieve f(k) for k = 0, 1, 2, ... using a factor base
3. Also sieve B_k = 2(m₀+2kn₀)n₀ = 2n₀m₀ + 4kn₀² (linear in k!)
4. Smooth A_k or B_k give relations for GF(2) linear algebra
5. Multiple roots = multiple polynomials (like MPQS!)

The B_k values are LINEAR in k — every B_k divisible by 2n₀.
And A_k is QUADRATIC in k with leading coeff 4n₀².

For sieving: for each FB prime p, A_k ≡ 0 (mod p) when
  4n₀²k² + 4m₀n₀k + (m₀²-n₀²) ≡ 0 (mod p)
This is a quadratic in k mod p — at most 2 roots.
So p divides A_k for k in 2 arithmetic progressions mod p!
"""

import time
import math
import gmpy2
from gmpy2 import mpz, isqrt, gcd, is_prime, next_prime, legendre
from collections import defaultdict


def _build_factor_base(N, B):
    """Primes p <= B where N is a QR (or p|N)."""
    fb = [2]
    p = mpz(3)
    while p <= B:
        if legendre(N, p) >= 0:
            fb.append(int(p))
        p = next_prime(p)
    return fb


def _sieve_roots_quadratic(a_coeff, b_coeff, c_coeff, p):
    """Find k mod p where a*k² + b*k + c ≡ 0 (mod p)."""
    # For p=2, just check k=0,1
    if p == 2:
        roots = []
        for k in range(2):
            if (a_coeff * k * k + b_coeff * k + c_coeff) % 2 == 0:
                roots.append(k)
        return roots

    # General: solve ak² + bk + c ≡ 0 (mod p)
    # Discriminant: b² - 4ac
    a, b, c = a_coeff % p, b_coeff % p, c_coeff % p
    if a == 0:
        # Linear: bk + c ≡ 0
        if b == 0:
            return list(range(p)) if c == 0 else []
        return [((-c) * pow(b, p - 2, p)) % p]

    disc = (b * b - 4 * a * c) % p
    if disc == 0:
        # Double root
        inv_2a = pow(2 * a % p, p - 2, p)
        return [((-b) * inv_2a) % p]

    # Check if disc is QR mod p
    if pow(disc, (p - 1) // 2, p) != 1:
        return []  # No roots

    # Tonelli-Shanks for sqrt(disc) mod p
    sqrt_disc = int(gmpy2.isqrt_rem(mpz(disc))[0])  # won't work for modular
    # Use pow for modular sqrt when p ≡ 3 mod 4
    if p % 4 == 3:
        sqrt_disc = pow(disc, (p + 1) // 4, p)
    else:
        # Tonelli-Shanks
        sqrt_disc = _tonelli_shanks(disc, p)
        if sqrt_disc is None:
            return []

    inv_2a = pow(2 * a % p, p - 2, p)
    r1 = ((-b + sqrt_disc) * inv_2a) % p
    r2 = ((-b - sqrt_disc) * inv_2a) % p
    if r1 == r2:
        return [r1]
    return [r1, r2]


def _tonelli_shanks(n, p):
    """Compute sqrt(n) mod p."""
    if pow(n, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    # Factor p-1 = Q * 2^S
    Q, S = p - 1, 0
    while Q % 2 == 0:
        Q //= 2
        S += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    M, c, t, R = S, pow(z, Q, p), pow(n, Q, p), pow(n, (Q + 1) // 2, p)
    while True:
        if t == 1:
            return R
        i = 1
        tmp = t * t % p
        while tmp != 1:
            tmp = tmp * tmp % p
            i += 1
        b = pow(c, 1 << (M - i - 1), p)
        M, c, t, R = i, b * b % p, t * b * b % p, R * b % p


def b3_sieve_factor(N, verbose=True, time_limit=3600):
    """
    Factor N using B3 arithmetic progression sieve.

    For each root (m₀,n₀), sieve the quadratic A_k = 4n₀²k² + 4m₀n₀k + (m₀²-n₀²)
    for smooth values, then do GF(2) linear algebra.
    """
    N = mpz(N)
    nd = len(str(N))

    # Quick checks
    if N <= 1: return 0
    if N % 2 == 0: return 2
    for p in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if N % p == 0: return int(p)
    if is_prime(N): return int(N)
    sq = isqrt(N)
    if sq * sq == N: return int(sq)

    t0 = time.time()

    # Parameter selection
    ln_n = float(gmpy2.log(N))
    ln_ln_n = math.log(max(ln_n, 2.0))
    L_exp = math.sqrt(ln_n * ln_ln_n)
    alpha = 0.45
    B = int(math.exp(alpha * L_exp))
    B = max(B, 100)
    B = min(B, 500_000)

    fb = _build_factor_base(N, B)
    fb_size = len(fb)
    needed = fb_size + 20

    # LP bound
    lp_bound = B * B

    if verbose:
        print(f"B3-Sieve: {nd}d ({int(gmpy2.log2(N))+1}b), B={B:,}, "
              f"|FB|={fb_size:,}, need={needed:,}")

    # Multiple roots — each gives a different polynomial
    roots = [
        (2, 1), (3, 2), (4, 1), (4, 3), (5, 2), (5, 4),
        (7, 2), (7, 4), (8, 3), (8, 5), (9, 2), (9, 4),
        (11, 2), (11, 4), (11, 6), (13, 2), (13, 4),
        (3, 1), (6, 1), (10, 1), (10, 3), (10, 7),
    ]

    # Collect relations across all roots
    smooth = []   # (x_plus_mod, x_minus_mod, sign, exponents, lp)
    partials = {} # lp -> (x_plus, x_minus, sign, exps)
    n_lp = 0
    total_k_tested = 0

    sieve_size = 100_000  # sieve window size

    fb_mpz = [mpz(p) for p in fb]

    for root_idx, (m0, n0) in enumerate(roots):
        if len(smooth) >= needed:
            break
        if time.time() - t0 > time_limit * 0.8:
            break

        g0 = int(gcd(mpz(m0), mpz(n0)))
        if g0 > 1:
            m0, n0 = m0 // g0, n0 // g0
        if m0 <= n0 or n0 <= 0:
            continue
        if (m0 - n0) % 2 == 0:
            continue

        # Polynomial coefficients: A_k = a*k² + b*k + c
        a_coeff = 4 * n0 * n0
        b_coeff = 4 * m0 * n0
        c_coeff = m0 * m0 - n0 * n0

        if verbose and root_idx < 5:
            print(f"  Root ({m0},{n0}): A_k = {a_coeff}k² + {b_coeff}k + {c_coeff}")

        # Precompute sieve: for each FB prime p, find k mod p where p | A_k
        sieve_starts = []
        for i, p in enumerate(fb):
            roots_mod_p = _sieve_roots_quadratic(a_coeff, b_coeff, c_coeff, p)
            sieve_starts.append(roots_mod_p)

        # Sieve in windows
        for window_start in range(0, 10 * sieve_size, sieve_size):
            if len(smooth) >= needed:
                break
            if time.time() - t0 > time_limit * 0.8:
                break

            # Initialize log sieve array
            sieve_log = [0.0] * sieve_size
            threshold = float(gmpy2.log2(mpz(abs(
                a_coeff * (window_start + sieve_size // 2) ** 2 +
                b_coeff * (window_start + sieve_size // 2) +
                c_coeff) + 1))) * 0.7

            # Sieve: add log(p) at positions where p | A_k
            for i, p in enumerate(fb):
                logp = math.log2(p)
                for r in sieve_starts[i]:
                    # First k >= window_start with k ≡ r (mod p)
                    start = r - window_start % p
                    if start < 0:
                        start += p
                    for pos in range(start, sieve_size, p):
                        sieve_log[pos] += logp

            # Check candidates that pass threshold
            for pos in range(sieve_size):
                if sieve_log[pos] < threshold:
                    continue

                k = window_start + pos
                total_k_tested += 1

                # Compute actual A_k
                m_k = m0 + 2 * k * n0
                A_val = m_k * m_k - n0 * n0
                if A_val <= 0:
                    continue

                # Quick factor check
                g = int(gcd(mpz(A_val), N))
                if 1 < g < int(N):
                    elapsed = time.time() - t0
                    if verbose:
                        print(f"\n  *** DIRECT FACTOR: {g} at root ({m0},{n0}) k={k} "
                              f"({elapsed:.1f}s) ***")
                    return g

                # Also check B_k = 2*m_k*n0
                B_val = 2 * m_k * n0
                g = int(gcd(mpz(B_val), N))
                if 1 < g < int(N):
                    elapsed = time.time() - t0
                    if verbose:
                        print(f"\n  *** DIRECT FACTOR via B: {g} ({elapsed:.1f}s) ***")
                    return g

                # Trial divide A_val for smooth relation
                sign = 0
                exps = [0] * fb_size
                cof = mpz(abs(A_val))
                if A_val < 0:
                    sign = 1

                for i in range(fb_size):
                    p = fb_mpz[i]
                    if p * p > cof:
                        break
                    if gmpy2.is_divisible(cof, p):
                        e = 0
                        while gmpy2.is_divisible(cof, p):
                            cof = cof // p
                            e += 1
                        exps[i] = e
                        if cof == 1:
                            break

                cofactor = int(cof)
                # Relation: A_k = m_k² - n₀²
                # We have A_k smooth. So m_k² ≡ n₀² + A_k (mod anything)
                # For QS-style: we want m_k² ≡ A_k (mod N) ISN'T right...
                # Actually: m_k² - n₀² = A_k. We store m_k and will
                # combine: product(m_k²) - product(n₀²+A_k) = 0
                # Better: store m_k*n₀ pair and use A_k = (m_k-n₀)(m_k+n₀)
                # The GF(2) step finds subset where product(A_k) = square.
                # Then product((m_k-n₀)(m_k+n₀)) = square = s²
                # And product(m_k-n₀) * product(m_k+n₀) = s²
                # x = product(m_k-n₀) mod N, y = s/product(m_k-n₀) mod N... complex.
                #
                # Simpler: just use A_k directly as the residue.
                # Store the pair (m_k+n₀, m_k-n₀) and their product A_k.
                # When product of A_k's is square:
                #   x = product(m_k+n₀) mod N
                #   y = product(m_k-n₀) mod N
                #   then x*y ≡ product(A_k) = square, so (x*y) = s²
                #   We need x*y ≡ s² mod N, and gcd(x-s, N) or gcd(y-s, N)
                # Actually simplest: x = product(m_k) mod N (not m_k+n₀)
                # x² ≡ product(m_k²) = product(A_k + n₀²) mod N... not clean.
                #
                # CLEANEST: store (m_k - n₀) mod N and (m_k + n₀) mod N separately.
                # When product of A_k = product((m_k-n₀)(m_k+n₀)) is a perfect square:
                #   s = sqrt(product(A_k))
                #   x = product(m_k+n₀) mod N, y = product(m_k-n₀) mod N
                #   x*y ≡ s² (mod N), so gcd(x*y - s², N) should be trivial
                #   BUT gcd(x - s, N) might work if x ≡ s (mod p) but not mod q
                x_plus = (m_k + n0) % int(N)
                x_minus = (m_k - n0) % int(N)
                x_mod = (x_plus * x_minus) % int(N)  # = A_k mod N

                if cofactor == 1:
                    smooth.append((x_plus, x_minus, sign, exps, 0))
                elif cofactor <= lp_bound and cofactor > 1:
                    if is_prime(mpz(cofactor)):
                        lp = cofactor
                        if lp in partials:
                            p2, m2, s2, e2 = partials.pop(lp)
                            cs = (sign + s2) % 2
                            ce = [exps[j] + e2[j] for j in range(fb_size)]
                            cp = (x_plus * p2) % int(N)
                            cm = (x_minus * m2) % int(N)
                            smooth.append((cp, cm, cs, ce, lp))
                            n_lp += 1
                        else:
                            partials[lp] = (x_plus, x_minus, sign, exps)

        if verbose:
            elapsed = time.time() - t0
            print(f"  Root ({m0},{n0}): {len(smooth)}/{needed} rels, "
                  f"{n_lp} LP, {total_k_tested:,} tested, {elapsed:.1f}s")

    elapsed_sieve = time.time() - t0
    if verbose:
        print(f"\n  Sieve done: {len(smooth):,} rels in {elapsed_sieve:.1f}s "
              f"({total_k_tested:,} candidates, {n_lp} LP)")

    if len(smooth) < fb_size + 2:
        if verbose:
            print(f"  Insufficient: {len(smooth)}/{fb_size+2}")
        return 0

    # GF(2) Gaussian Elimination
    nrows = len(smooth)
    ncols = fb_size + 1  # +1 for sign

    if verbose:
        print(f"  LA: {nrows} x {ncols}...")

    mat = [0] * nrows
    for i in range(nrows):
        _, _, s, exps, _ = smooth[i]
        row = s
        for j in range(fb_size):
            if exps[j] & 1:
                row |= (1 << (j + 1))
        mat[i] = row

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

    # Factor extraction
    # Each relation: A_k = (m_k-n₀)(m_k+n₀) is smooth.
    # x_mod stores A_k mod N = (m_k+n₀)(m_k-n₀) mod N.
    # When product of selected A_k values is a perfect square s²:
    #   product(A_k) mod N = product(x_mod) mod N
    #   s = sqrt(product(A_k)) computed from exponent vectors
    #   gcd(product(x_mod) - s, N) or gcd(product(x_mod) + s, N) → factor
    #
    # Actually the standard QS approach: x = product(m_k+n₀) mod N,
    # y = sqrt(product((m_k+n₀)(m_k-n₀))) mod N = product of FB primes^(exp/2).
    # But we don't store m_k+n₀ and m_k-n₀ separately.
    #
    # Simplest correct approach: x_mod = A_k mod N. When product is square:
    # product(A_k) ≡ s² (mod N), and s is computed from FB.
    # Try gcd(product(A_k) ± s, N). Since product(A_k) ≡ 0 mod N if we're lucky,
    # we need to track the product carefully.
    #
    # The issue is that A_k mod N is NOT m_k² mod N.
    # Let's just do: x = product of all A_k values mod N (the "raw" product).
    # y = the square root from FB exponents.
    # Then x ≡ y² (mod N) by construction. gcd(x-y, N) → factor.
    # Wait no: x = product(A_k) mod N, y² = product(A_k) (same thing).
    # So x = y². That's trivial.
    #
    # The REAL QS trick: x = product(m_k) mod N, y² = product(A_k + n₀²) =
    # product(m_k²). So x² = product(m_k²) = y⁴... still wrong.
    #
    # OK, back to basics. We need TWO different expressions for the same square:
    # product(A_k) = product((m_k-n₀)(m_k+n₀)) = [product(m_k-n₀)]*[product(m_k+n₀)]
    # When this product is a square s²:
    # Let X = product(m_k+n₀) mod N, Y = product(m_k-n₀) mod N.
    # X*Y ≡ s² (mod N). And s is known from the factorization.
    # Now: gcd(X - s, N) might work! Because X ≡ s mod p but X ≢ s mod q (or vice versa).

    n_factors_tried = 0
    for row in range(nrows):
        if mat[row] != 0:
            continue
        indices = []
        bits = combo[row]
        idx = 0
        while bits:
            if bits & 1:
                indices.append(idx)
            bits >>= 1
            idx += 1
        if not indices:
            continue

        total_exp = [0] * fb_size
        total_sign = 0
        lp_product = mpz(1)

        # X = product(m_k+n₀) mod N, Y = product(m_k-n₀) mod N
        X_val = mpz(1)
        Y_val = mpz(1)

        for idx in indices:
            xp, xm, s, exps, lp_val = smooth[idx]
            X_val = X_val * mpz(xp) % N
            Y_val = Y_val * mpz(xm) % N
            total_sign += s
            for j in range(fb_size):
                total_exp[j] += exps[j]
            if lp_val > 0:
                lp_product = lp_product * mpz(lp_val) % N

        if any(e & 1 for e in total_exp) or total_sign & 1:
            continue

        # s = sqrt(product(A_k)) from factorization = product of FB primes^(exp/2) * LP
        s_val = lp_product
        for j in range(fb_size):
            if total_exp[j] > 0:
                s_val = s_val * pow(mpz(fb[j]), total_exp[j] >> 1, N) % N

        # X_val = product(A_k) mod N, s_val² ≡ product(A_k) mod N
        # So X_val ≡ s_val² mod N. Try gcd(X_val - s_val², N)... trivial.
        # The problem is we need the SQRT of product(A_k) = s_val,
        # and a DIFFERENT expression for the same value.
        # In standard QS: x = product(Q_i + sqrt_N), y = sqrt(product(Q_i)).
        # Here we don't have that structure.
        #
        # ALTERNATIVE: use CFRAC-style relation.
        # Store p_k (CF convergent) where p_k² - N*q_k² = A_k.
        # Then product(p_k²) ≡ product(A_k) * product(N*q_k²)... messy.
        #
        # X_val * Y_val ≡ product(A_k) ≡ s_val² (mod N)
        # So X_val * Y_val = s_val². Try gcd(X_val - s_val, N), gcd(Y_val - s_val, N)
        # Also try gcd(X_val * Y_val - s_val * s_val, N) and other combinations
        n_factors_tried += 1
        for diff in (X_val - s_val, X_val + s_val, Y_val - s_val, Y_val + s_val,
                     X_val * Y_val - s_val * s_val % N):
            g = int(gcd(diff % N, N))
            if 1 < g < int(N):
                total_t = time.time() - t0
                if verbose:
                    print(f"\n  *** FACTOR: {g} ({nd}d, {total_t:.1f}s, "
                          f"{len(smooth)} rels, {n_factors_tried} vecs tried) ***")
                return g

    if verbose:
        print(f"  No factor from LA")
    return 0


# ---- CLI ----
if __name__ == "__main__":
    import sys
    import random

    if len(sys.argv) > 1 and sys.argv[1] == "bench":
        print("=" * 65)
        print("B3 Arithmetic Progression Sieve — Benchmark")
        print("=" * 65)

        rng = random.Random(42)
        for nd_target in [20, 25, 30, 35, 40, 45, 50]:
            half = nd_target // 2
            # Generate semiprime with target digit count
            while True:
                p = int(next_prime(mpz(rng.getrandbits(int(nd_target * 3.32 // 2)))))
                q = int(next_prime(mpz(rng.getrandbits(int(nd_target * 3.32 // 2)))))
                N_test = p * q
                if len(str(N_test)) >= nd_target - 1:
                    break

            print(f"\n--- {len(str(N_test))}d ---")
            t0 = time.time()
            f = b3_sieve_factor(N_test, verbose=True, time_limit=120)
            elapsed = time.time() - t0
            if f and f > 1 and N_test % f == 0:
                print(f"  OK: {f} in {elapsed:.1f}s")
            else:
                print(f"  FAIL in {elapsed:.1f}s")

    elif len(sys.argv) > 1:
        N = int(sys.argv[1])
        tl = int(sys.argv[2]) if len(sys.argv) > 2 else 300
        f = b3_sieve_factor(N, verbose=True, time_limit=tl)
        if f:
            print(f"Result: {N} = {f} * {N // f}")

    else:
        print("Usage: pyth_b3_sieve.py bench | pyth_b3_sieve.py <N> [time_limit]")
