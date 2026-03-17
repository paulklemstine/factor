#!/usr/bin/env python3
"""
CFRAC + SIQS Hybrid Factoring Experiment
=========================================
Theory: 90% CFRAC relations (cheap) + 10% SIQS relations (expensive but diverse)
mixed in one GF(2) matrix should yield ~40% non-trivial null vectors because
the SIQS relations provide CRT mixing across different quadratic forms.

CFRAC: x² ≡ r (mod N) from continued fraction expansion of sqrt(N)
SIQS:  (ax+b)² ≡ g(x) (mod N) with square-free a from FB primes
"""

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, next_prime, jacobi, invert
import time
import math
import random

def make_semiprime(digits):
    """Create a semiprime with roughly `digits` total digits."""
    half = digits // 2
    p = next_prime(mpz(10)**(half - 1) + random.randint(0, 10**8))
    q = next_prime(p + random.randint(10**4, 10**6))
    return int(p), int(q), int(p * q)

def build_factor_base(N, B):
    """Build factor base: primes p <= B with jacobi(N, p) >= 0."""
    fb = [2]
    p = 3
    while p <= B:
        if jacobi(mpz(N), mpz(p)) >= 0:
            fb.append(p)
        p = int(next_prime(mpz(p)))
    return fb

def trial_divide(val, fb):
    """Trial divide val by factor base. Returns (sign, exponent_vector) or None."""
    v = val
    sign = 0
    if v < 0:
        v = -v
        sign = 1
    if v == 0:
        return None
    exps = [0] * len(fb)
    for i, p in enumerate(fb):
        while v % p == 0:
            v //= p
            exps[i] += 1
        if p * p > v:
            break
    if v == 1:
        return sign, exps
    return None  # not smooth

def cfrac_relations(N, fb, max_relations, max_iters=500000):
    """
    Collect relations from the continued fraction expansion of sqrt(N).
    Each convergent p_k/q_k satisfies: p_k² ≡ (-1)^k * r_k (mod N)
    where r_k is the CF remainder, which tends to be small.
    """
    N = mpz(N)
    sqrtN = isqrt(N)
    if sqrtN * sqrtN == N:
        return []  # perfect square

    relations = []
    # CF recurrence: sqrt(N) = a0 + 1/(a1 + 1/(a2 + ...))
    # We track P_k, Q_k (partial quotient state) and p_k, p_{k-1} (convergents)
    m, d, a0 = mpz(0), mpz(1), sqrtN
    a = a0
    p_prev, p_curr = mpz(1), a0  # convergent numerators mod N
    # q_prev, q_curr = mpz(0), mpz(1)  # not needed

    for it in range(max_iters):
        if len(relations) >= max_relations:
            break
        # CF step
        m = d * a - m
        d = (N - m * m) // d
        if d == 0:
            break
        a = (a0 + m) // d

        # Update convergent numerator mod N
        p_next = (a * p_curr + p_prev) % N
        p_prev, p_curr = p_curr, p_next

        # The relation: p_curr² ≡ ±d (mod N) ... actually we need the remainder
        # More precisely: p_curr² mod N gives a value, and we check if it's small
        r = int((p_curr * p_curr) % N)
        # Make it the smallest representative
        if r > int(N) // 2:
            r = r - int(N)

        result = trial_divide(r, fb)
        if result is not None:
            sign, exps = result
            relations.append(('cfrac', int(p_curr), sign, exps))

    return relations

def siqs_relations(N, fb, target_count=15, sieve_half=2000):
    """
    Collect a small number of SIQS relations.
    Pick square-free a from products of FB primes, solve b² ≡ N (mod a),
    sieve g(x) = a*x² + 2*b*x + c over a small range.
    """
    N_mpz = mpz(N)
    relations = []
    # Use single FB primes as 'a' for simplicity (they're square-free trivially)
    # Pick primes near sqrt(2N)/sieve_half for good polynomial values
    target_a = int(isqrt(2 * N_mpz)) // sieve_half

    # Find FB primes suitable as 'a'
    candidates = []
    for p in fb:
        if p < 7:
            continue
        # For single-prime a, we need N to be a QR mod p
        if jacobi(N_mpz, mpz(p)) == 1:
            candidates.append(p)

    if not candidates:
        return relations

    random.shuffle(candidates)
    attempts = 0

    for a in candidates:
        if len(relations) >= target_count:
            break
        attempts += 1
        if attempts > len(candidates):
            break

        a_mpz = mpz(a)
        # Solve b² ≡ N (mod a) using Tonelli-Shanks via gmpy2
        # gmpy2 doesn't have sqrtmod directly, use pow for prime a
        # b = N^((a+1)/4) mod a if a ≡ 3 mod 4, else use Tonelli-Shanks
        b_val = int(gmpy2.powmod(N_mpz, (a_mpz + 1) // 4, a_mpz))
        if a % 4 != 3:
            # Tonelli-Shanks for general case
            b_val = _tonelli_shanks(N, a)
            if b_val is None:
                continue

        # Verify
        if (b_val * b_val) % a != N % a:
            continue

        b_mpz = mpz(b_val)
        c = int((b_mpz * b_mpz - N_mpz) // a_mpz)

        # Sieve g(x) = a*x² + 2*b*x + c for x in [-sieve_half, sieve_half]
        for x in range(-sieve_half, sieve_half + 1):
            gx = a * x * x + 2 * b_val * x + c
            if gx == 0:
                continue
            result = trial_divide(gx, fb)
            if result is not None:
                sign, exps = result
                # The x-value for the relation: (a*x + b) mod N
                ax_val = int((a_mpz * x + b_mpz) % N_mpz)
                relations.append(('siqs', ax_val, sign, exps))
                if len(relations) >= target_count:
                    break

    return relations

def _tonelli_shanks(n, p):
    """Compute sqrt(n) mod p using Tonelli-Shanks."""
    n = n % p
    if n == 0:
        return 0
    if p == 2:
        return n
    # Factor out powers of 2 from p-1
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    # Find a non-residue
    z = 2
    while jacobi(mpz(z), mpz(p)) != -1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while True:
        if t == 1:
            return r
        # Find least i such that t^(2^i) = 1
        i, tmp = 1, (t * t) % p
        while tmp != 1:
            tmp = (tmp * tmp) % p
            i += 1
            if i >= m:
                return None
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, (b * b) % p, (t * b * b) % p, (r * b) % p

def solve_gf2(relations, fb, N):
    """
    Build GF(2) matrix from mixed relations, solve, extract factors.
    Returns list of (factor, vector_indices, types_in_vector).
    """
    N_mpz = mpz(N)
    nrows = len(relations)
    ncols = len(fb) + 1  # +1 for sign column

    # Build matrix as Python big-int bit vectors
    mat = []
    for rtype, xval, sign, exps in relations:
        row = sign  # bit 0 = sign
        for j, e in enumerate(exps):
            if e % 2 == 1:
                row |= (1 << (j + 1))
        mat.append(row)

    # Gaussian elimination with combination tracking
    combo = [1 << i for i in range(nrows)]
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

    # Extract null vectors
    results = []
    trivial = 0
    nontrivial = 0
    siqs_in_nontrivial = 0

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

    for indices in null_vecs:
        x_val = mpz(1)
        total_exp = [0] * len(fb)
        total_sign = 0
        types_in_vec = set()

        for idx in indices:
            rtype, ax, sign, exps = relations[idx]
            types_in_vec.add(rtype)
            x_val = x_val * mpz(ax) % N_mpz
            total_sign += sign
            for j in range(len(fb)):
                total_exp[j] += exps[j]

        if any(e % 2 != 0 for e in total_exp) or total_sign % 2 != 0:
            continue

        y_val = mpz(1)
        for j, e in enumerate(total_exp):
            if e > 0:
                y_val = y_val * pow(mpz(fb[j]), e // 2, N_mpz) % N_mpz

        found_factor = False
        for diff in [x_val - y_val, x_val + y_val]:
            g = gcd(diff % N_mpz, N_mpz)
            if 1 < g < N_mpz:
                nontrivial += 1
                has_siqs = 'siqs' in types_in_vec
                if has_siqs:
                    siqs_in_nontrivial += 1
                results.append((int(g), indices, types_in_vec))
                found_factor = True
                break

        if not found_factor:
            trivial += 1

    return results, len(null_vecs), trivial, nontrivial, siqs_in_nontrivial


def run_experiment(digits=30, num_trials=3):
    """Run the CFRAC+SIQS hybrid experiment."""
    print("=" * 70)
    print("CFRAC + SIQS Hybrid Factoring Experiment")
    print("=" * 70)

    for trial in range(num_trials):
        p, q, N = make_semiprime(digits)
        nd = len(str(N))
        print(f"\nTrial {trial+1}: N = {N}  ({nd} digits)")
        print(f"  True factors: {p} * {q}")

        # Factor base bound: L_N[1/2, 0.5] = exp(0.5 * sqrt(ln N * ln ln N))
        ln_N = math.log(N)
        B = int(math.exp(0.5 * math.sqrt(ln_N * math.log(ln_N))))
        B = max(B, 200)  # floor
        fb = build_factor_base(N, B)
        fb_size = len(fb)
        needed = fb_size + 20
        print(f"  B={B}, |FB|={fb_size}, need ~{needed} relations")

        # Phase 1: CFRAC relations (cheap)
        t0 = time.time()
        cfrac_rels = cfrac_relations(N, fb, needed, max_iters=1000000)
        t_cfrac = time.time() - t0
        print(f"  CFRAC: {len(cfrac_rels)} relations in {t_cfrac:.2f}s")

        # Phase 2: SIQS relations (small batch)
        t1 = time.time()
        siqs_target = max(5, fb_size // 10)
        siqs_rels = siqs_relations(N, fb, target_count=siqs_target, sieve_half=3000)
        t_siqs = time.time() - t1
        print(f"  SIQS:  {len(siqs_rels)} relations in {t_siqs:.2f}s (target={siqs_target})")

        # === Test 1: CFRAC only ===
        if len(cfrac_rels) >= fb_size + 1:
            res_c, nvecs_c, triv_c, nontriv_c, _ = solve_gf2(cfrac_rels, fb, N)
            pct_c = 100 * nontriv_c / max(1, nvecs_c)
            print(f"  CFRAC-only:  {nvecs_c} null vecs, {nontriv_c} non-trivial ({pct_c:.0f}%)"
                  f", {triv_c} trivial")
            if res_c:
                print(f"    -> Found factor: {res_c[0][0]}")
        else:
            print(f"  CFRAC-only:  insufficient relations ({len(cfrac_rels)}/{fb_size+1})")
            nvecs_c, nontriv_c, pct_c = 0, 0, 0

        # === Test 2: Hybrid (CFRAC + SIQS mixed) ===
        hybrid_rels = cfrac_rels + siqs_rels
        if len(hybrid_rels) >= fb_size + 1:
            res_h, nvecs_h, triv_h, nontriv_h, siqs_in = solve_gf2(hybrid_rels, fb, N)
            pct_h = 100 * nontriv_h / max(1, nvecs_h)
            print(f"  HYBRID:      {nvecs_h} null vecs, {nontriv_h} non-trivial ({pct_h:.0f}%)"
                  f", {triv_h} trivial")
            print(f"    -> {siqs_in}/{nontriv_h} non-trivial vecs contain SIQS relations")
            if res_h:
                print(f"    -> Found factor: {res_h[0][0]}")
        else:
            print(f"  HYBRID:      insufficient relations ({len(hybrid_rels)}/{fb_size+1})")

        # === Comparison ===
        if len(cfrac_rels) >= fb_size + 1 and len(hybrid_rels) >= fb_size + 1:
            delta = nontriv_h - nontriv_c
            print(f"  DELTA: hybrid has {delta:+d} more non-trivial vecs "
                  f"({pct_c:.0f}% -> {pct_h:.0f}%)")

    print("\n" + "=" * 70)
    print("Experiment complete.")


if __name__ == "__main__":
    random.seed(42)
    run_experiment(digits=30, num_trials=5)
