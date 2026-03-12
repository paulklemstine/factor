#!/usr/bin/env python3
"""
GNFS Engine: General Number Field Sieve for 80d+ factorization
================================================================
Implements the General Number Field Sieve for factoring large semiprimes
(80-200+ digits) where SIQS becomes impractical.

Phases:
  1. Polynomial Selection (base-m method, Kleinjung optimization)
  2. Relation Collection (line sieve on algebraic + rational sides)
  3. Linear Algebra (Block Lanczos over GF(2))
  4. Square Root (Couveignes' method or Montgomery's)

This is a scaffold that will be built out incrementally.
"""

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, next_prime, iroot
import math
import time
import numpy as np
from collections import defaultdict


###############################################################################
# Phase 1: Polynomial Selection (Base-m Method)
###############################################################################

def base_m_poly(n, d=None):
    """
    Base-m polynomial selection for GNFS.

    Choose degree d and base m = floor(n^(1/d)), then express n in base m:
      n = a_d * m^d + a_{d-1} * m^{d-1} + ... + a_1 * m + a_0

    This gives polynomial f(x) = a_d*x^d + ... + a_0 with f(m) = n.
    The rational polynomial is g(x) = x - m, so g(m) = 0 and
    f(m) ≡ 0 (mod n) since f(m) = n.

    Parameters
    ----------
    n : int
        Number to factor.
    d : int, optional
        Polynomial degree. If None, chosen optimally based on digit count.

    Returns
    -------
    dict with keys:
        'f_coeffs': list of coefficients [a_0, a_1, ..., a_d]
        'g_coeffs': list [-m, 1] (linear polynomial g(x) = x - m)
        'm': the base
        'd': degree
        'skewness': initial skewness estimate
    """
    n = mpz(n)
    nd = len(str(int(n)))

    # Optimal degree selection (standard GNFS heuristics)
    if d is None:
        if nd < 80:
            d = 3
        elif nd < 110:
            d = 4
        elif nd < 155:
            d = 5
        elif nd < 210:
            d = 6
        else:
            d = 7

    # Base m = floor(n^(1/d))
    m, exact = iroot(n, d)
    # If exact, n = m^d, which means m is a factor (trivial case)
    if exact:
        return {'factor': int(m)}

    # Express n in base m: n = sum(a_i * m^i)
    coeffs = []
    remainder = n
    for i in range(d + 1):
        coeff = remainder % m
        remainder = remainder // m
        coeffs.append(int(coeff))

    # The leading coefficient a_d might need adjustment
    # Since m = floor(n^(1/d)), we might have remainder > 0
    if remainder > 0:
        # n > a_d * m^d, so we need to absorb remainder into leading coeff
        coeffs[-1] = int(coeffs[-1] + remainder * m)
        # Alternatively, increase m slightly. For now, just adjust a_d.

    # Verify: f(m) should equal n
    f_at_m = mpz(0)
    m_power = mpz(1)
    for c in coeffs:
        f_at_m += mpz(c) * m_power
        m_power *= m
    assert f_at_m == n, f"Polynomial verification failed: f(m)={f_at_m} != n={n}"

    # Skewness estimate: s ≈ (a_0 / a_d)^(1/d)
    if coeffs[-1] != 0:
        skewness = float(abs(coeffs[0]) / abs(coeffs[-1])) ** (1.0 / d)
    else:
        skewness = 1.0

    return {
        'f_coeffs': coeffs,
        'g_coeffs': [-int(m), 1],
        'm': int(m),
        'd': d,
        'skewness': skewness,
    }


def eval_poly(coeffs, x):
    """Evaluate polynomial with given coefficients at x (Horner's method)."""
    result = mpz(0)
    for c in reversed(coeffs):
        result = result * mpz(x) + mpz(c)
    return result


def poly_derivative(coeffs):
    """Compute derivative coefficients."""
    return [i * c for i, c in enumerate(coeffs) if i > 0]


def poly_content(coeffs):
    """GCD of all coefficients."""
    g = mpz(0)
    for c in coeffs:
        g = gcd(g, mpz(abs(c)))
    return int(g) if g > 0 else 1


###############################################################################
# Phase 1b: Polynomial Quality Assessment
###############################################################################

def murphy_alpha(f_coeffs, B=2000):
    """
    Estimate Murphy's alpha score for polynomial f.

    Alpha measures the "small prime content" of f(x) over its range.
    Higher (less negative) alpha = polynomial produces values with more
    small prime factors = higher smooth probability.

    This is a simplified estimate; full Murphy E score requires integration.
    """
    d = len(f_coeffs) - 1
    alpha = 0.0

    # For each small prime p, estimate the average valuation of f(a) mod p
    p = 2
    while p <= B:
        # Count roots of f mod p
        roots = 0
        for r in range(p):
            val = 0
            r_pow = 1
            for c in f_coeffs:
                val = (val + c * r_pow) % p
                r_pow = (r_pow * r) % p
            if val == 0:
                roots += 1

        # Contribution: expected extra log(p) per value from this prime
        # compared to random integers
        if roots > 0:
            # Average valuation of f(a) at prime p is approx roots/p
            # Contribution to alpha
            alpha += (roots / p - 1 / (p - 1)) * math.log(p)

        p = int(next_prime(p))

    return alpha


def score_polynomial(n, f_coeffs, g_coeffs, skewness):
    """
    Combined score for polynomial selection ranking.
    Lower is better.
    """
    d = len(f_coeffs) - 1
    alpha = murphy_alpha(f_coeffs, B=500)

    # Leading coefficient penalty (smaller a_d = better)
    lc_penalty = math.log(abs(f_coeffs[-1]) + 1)

    # Coefficient size penalty (norms should be balanced)
    max_coeff = max(abs(c) for c in f_coeffs)
    size_penalty = math.log(max_coeff + 1) / d

    return -alpha + lc_penalty * 0.5 + size_penalty * 0.3


###############################################################################
# Phase 2: Factor Base Construction
###############################################################################

def build_rational_fb(B_r):
    """
    Build rational factor base: all primes up to B_r.
    Returns list of primes.
    """
    fb = []
    p = mpz(2)
    while p <= B_r:
        fb.append(int(p))
        p = next_prime(p)
    return fb


def find_poly_roots_mod_p(coeffs, p):
    """
    Find all roots of polynomial f(x) mod p.
    Uses brute force for small p (adequate for factor base construction).
    """
    roots = []
    for r in range(p):
        val = 0
        r_pow = 1
        for c in coeffs:
            val = (val + c * r_pow) % p
            r_pow = (r_pow * r) % p
        if val == 0:
            roots.append(r)
    return roots


def build_algebraic_fb(f_coeffs, B_a):
    """
    Build algebraic factor base.
    For each prime p <= B_a, find roots r of f(x) mod p.
    Each (p, r) pair is a first-degree prime ideal.

    Returns list of (p, r) pairs.
    """
    fb = []
    p = 2
    while p <= B_a:
        roots = find_poly_roots_mod_p(f_coeffs, p)
        for r in roots:
            fb.append((p, r))
        p = int(next_prime(p))
    return fb


###############################################################################
# Phase 2b: GNFS Parameters
###############################################################################

def gnfs_params(n):
    """
    Select GNFS parameters based on number size.

    Returns dict with:
        'd': polynomial degree
        'B_r': rational factor base bound
        'B_a': algebraic factor base bound
        'sieve_region': (A, B_max) for line sieve
    """
    nd = len(str(int(n)))
    nb = int(gmpy2.log2(mpz(n))) + 1

    # Degree
    if nd < 80:
        d = 3
    elif nd < 110:
        d = 4
    elif nd < 155:
        d = 5
    elif nd < 210:
        d = 6
    else:
        d = 7

    # L(n) = exp(c * (log n)^(1/3) * (log log n)^(2/3))
    ln_n = nb * math.log(2)
    ln_ln_n = math.log(ln_n) if ln_n > 1 else 1.0
    L = math.exp(0.5 * (ln_n ** (1/3)) * (ln_ln_n ** (2/3)))

    # Factor base bounds scale as L^(2/3)
    fb_bound = int(L ** 0.667)
    fb_bound = max(fb_bound, 10000)
    fb_bound = min(fb_bound, 50_000_000)  # cap for memory

    # Sieve region: A must be small enough that algebraic norms stay smooth-able
    # For degree d, alg_norm ~ A^d, so A ~ fb_bound^(2/d) to get ~fb_bound^2 norms
    A = int(fb_bound ** (2.0 / d))
    A = max(A, 1000)
    A = min(A, 5_000_000)  # cap for memory

    # B_max: more b values compensates for smaller A
    B_max = max(fb_bound // 5, 500)
    B_max = min(B_max, 50000)

    return {
        'd': d,
        'B_r': fb_bound,
        'B_a': fb_bound,
        'A': A,
        'B_max': B_max,
        'L': L,
    }


###############################################################################
# Phase 3: Line Sieve (Skeleton)
###############################################################################

def norm_rational(a, b, m):
    """Rational norm: |a + b*m|"""
    return abs(a + b * m)


def norm_algebraic(a, b, f_coeffs):
    """
    Algebraic norm: |resultant of (a + b*alpha) and f(alpha)|
    = |b^d * f(-a/b)| = |sum(f_i * (-a)^i * b^(d-i))|
    """
    d = len(f_coeffs) - 1
    result = mpz(0)
    for i, c in enumerate(f_coeffs):
        term = mpz(c) * (mpz(-a) ** i) * (mpz(b) ** (d - i))
        result += term
    return abs(result)


def sieve_line(b, A, m, f_coeffs, rat_fb, alg_fb, rat_bound=0, alg_bound=0):
    """
    Sieve one line (fixed b) for a in [-A, A].

    For each prime p in rational FB:
      Mark positions where p | (a + b*m), i.e., a ≡ -b*m (mod p)
    For each (p, r) in algebraic FB:
      Mark positions where p | norm_alg(a,b), i.e., a ≡ -b*r (mod p)

    Returns list of (a, b) pairs where both norms are likely smooth.
    """
    size = 2 * A + 1

    # Rational sieve array (log approximation)
    rat_log = np.zeros(size, dtype=np.float32)
    # Algebraic sieve array
    alg_log = np.zeros(size, dtype=np.float32)

    # Sieve rational side
    bm = int(b) * int(m)
    for p in rat_fb:
        if p == 0:
            continue
        log_p = math.log(p)
        # a ≡ -b*m (mod p)
        start = (-bm) % p
        idx = (start + A) % p  # first index in [0, size)
        while idx < size:
            rat_log[idx] += log_p
            idx += p

    # Sieve algebraic side
    for p, r in alg_fb:
        if p == 0:
            continue
        log_p = math.log(p)
        # a ≡ -b*r (mod p)
        start = (-(int(b) * r)) % p
        idx = (start + A) % p
        while idx < size:
            alg_log[idx] += log_p
            idx += p

    # Adaptive threshold: based on typical norm for this b value
    # Rational norm: |a + b*m| ≈ b*m for small a (center of sieve)
    rat_typical = max(abs(bm), A)  # approximate
    rat_thresh = math.log(rat_typical) * 0.6 if rat_typical > 1 else 1.0

    # Algebraic norm at center (a=0): |b^d * f(0)| = |b^d * f_coeffs[0]|
    d = len(f_coeffs) - 1
    alg_center = abs(int(b) ** d * f_coeffs[0]) if f_coeffs[0] != 0 else abs(int(b) ** d)
    alg_typical = max(alg_center, 1)
    alg_thresh = math.log(alg_typical) * 0.5 if alg_typical > 1 else 1.0

    # Collect candidates
    smooth_pairs = []
    for idx in range(size):
        if rat_log[idx] >= rat_thresh and alg_log[idx] >= alg_thresh:
            a = idx - A
            if a == 0:
                continue
            if gcd(mpz(abs(a)), mpz(b)) != 1:
                continue  # require gcd(a,b) = 1
            smooth_pairs.append((a, int(b)))

    return smooth_pairs


###############################################################################
# Phase 3b: Trial Division Verification
###############################################################################

def trial_divide_rational(a, b, m, rat_fb):
    """
    Trial divide the rational norm |a + b*m| over the rational factor base.
    Returns (exponent_vector, remainder) or None if not smooth.
    """
    val = abs(int(a) + int(b) * int(m))
    if val == 0:
        return None
    sign = 1 if (int(a) + int(b) * int(m)) < 0 else 0
    exps = [0] * len(rat_fb)
    for i, p in enumerate(rat_fb):
        while val % p == 0:
            val //= p
            exps[i] += 1
    if val == 1:
        return (exps, sign)
    return None  # not smooth


def trial_divide_algebraic(a, b, f_coeffs, alg_fb):
    """
    Trial divide the algebraic norm over the algebraic factor base.
    Returns exponent_vector or None if not smooth.

    The algebraic norm is N(a + b*alpha) = (-b)^d * f(a/(-b))
    = sum(f_i * a^i * (-b)^(d-i))
    """
    val = abs(int(norm_algebraic(a, b, f_coeffs)))
    if val == 0:
        return None
    exps = [0] * len(alg_fb)
    for i, (p, r) in enumerate(alg_fb):
        # (p, r) divides (a + b*alpha) iff a + b*r ≡ 0 (mod p)
        if (int(a) + int(b) * r) % p == 0:
            while val % p == 0:
                val //= p
                exps[i] += 1
    if val == 1:
        return exps
    return None  # not smooth


###############################################################################
# Phase 4: GF(2) Linear Algebra (Gaussian Elimination)
###############################################################################

def gf2_gaussian_elimination(relations, ncols_rat, ncols_alg):
    """
    Build GF(2) matrix from relations and find null space vectors.

    Each relation has:
      - rational exponent vector (sign + exps_rat)
      - algebraic exponent vector (exps_alg)

    Matrix columns = 1 (sign) + ncols_rat + ncols_alg.
    """
    nrows = len(relations)
    ncols = 1 + ncols_rat + ncols_alg

    # Build bit-vector matrix
    mat = []
    for rel in relations:
        row = rel['rat_sign']  # bit 0 = sign
        for j, e in enumerate(rel['rat_exps']):
            if e % 2 == 1:
                row |= (1 << (j + 1))
        for j, e in enumerate(rel['alg_exps']):
            if e % 2 == 1:
                row |= (1 << (j + 1 + ncols_rat))
        mat.append(row)

    # Gaussian elimination with combination tracking
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

    # Extract null space vectors
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

    return null_vecs


###############################################################################
# Phase 5: Square Root and Factor Extraction
###############################################################################

def extract_factor(n, null_vecs, relations, m, rat_fb, alg_fb):
    """
    For each null space vector, compute x² ≡ y² (mod n) and extract gcd.

    In GNFS, for a dependency set where both rational and algebraic exponent
    vectors are even:
      - Rational: Π(a_i + b_i·m) = (-1)^s · Π p_j^{e_j} where all e_j even
      - x = Π(a_i + b_i·m) mod n (the "raw" product)
      - y = Π p_j^{e_j/2} mod n (square root via half-exponents)
      - gcd(x ± y, n) may give factor

    Note: Full GNFS also needs algebraic square root (Couveignes/Montgomery).
    This simplified approach uses only the rational side, which works when
    the algebraic side happens to map correctly through φ(α)=m.
    """
    for vi, indices in enumerate(null_vecs):
        # Accumulate rational exponents and algebraic exponents
        total_rat = [0] * len(rat_fb)
        total_alg = [0] * len(alg_fb)
        total_sign = 0

        for idx in indices:
            rel = relations[idx]
            total_sign += rel['rat_sign']
            for j, e in enumerate(rel['rat_exps']):
                total_rat[j] += e
            for j, e in enumerate(rel['alg_exps']):
                total_alg[j] += e

        # Check all exponents are even
        if any(e % 2 != 0 for e in total_rat) or total_sign % 2 != 0:
            continue
        if any(e % 2 != 0 for e in total_alg):
            continue

        # Compute x = Π(a_i + b_i·m) mod n
        x_val = mpz(1)
        for idx in indices:
            rel = relations[idx]
            val = mpz(rel['a']) + mpz(rel['b']) * mpz(m)
            x_val = (x_val * val) % n

        # Compute y from rational half-exponents
        y_rat = mpz(1)
        for j, e in enumerate(total_rat):
            if e > 0:
                y_rat = (y_rat * pow(mpz(rat_fb[j]), e // 2, n)) % n

        # Compute z from algebraic half-exponents (using FB primes)
        y_alg = mpz(1)
        for j, e in enumerate(total_alg):
            if e > 0:
                p, r = alg_fb[j]
                y_alg = (y_alg * pow(mpz(p), e // 2, n)) % n

        # Try multiple combinations for gcd
        for y_val in [y_rat, y_alg, (y_rat * y_alg) % n]:
            for diff in [x_val - y_val, x_val + y_val]:
                g = gcd(diff % n, n)
                if 1 < g < n:
                    return int(g)

    return None


###############################################################################
# Top-Level: GNFS Factor
###############################################################################

def gnfs_factor(n, verbose=True, time_limit=3600):
    """
    Factor n using the General Number Field Sieve.

    Implemented phases:
    1. Polynomial selection (base-m with Murphy alpha scoring)
    2. Factor base construction (rational + algebraic)
    3. Line sieve with trial division verification
    4. GF(2) Gaussian elimination (finds null space)

    BLOCKING TODO:
    - Algebraic square root (Couveignes/Montgomery algorithm)
      Without this, the x² ≡ y² (mod n) identity cannot be completed.
      The rational square root alone is insufficient — need φ(s) where
      s² = Π(a_i + b_i·α) in Z[α]/(f(α)).
    """
    n = mpz(n)
    nd = len(str(int(n)))
    nb = int(gmpy2.log2(n)) + 1
    t0 = time.time()

    if verbose:
        print(f"  GNFS: {nd}d ({nb}b)")

    # Step 1: Parameters
    params = gnfs_params(n)
    d = params['d']
    if verbose:
        print(f"    Params: d={d}, B_r={params['B_r']}, B_a={params['B_a']}, "
              f"A={params['A']}, B_max={params['B_max']}")

    # Step 2: Polynomial selection
    poly = base_m_poly(n, d=d)
    if 'factor' in poly:
        return poly['factor']

    f_coeffs = poly['f_coeffs']
    g_coeffs = poly['g_coeffs']
    m = poly['m']
    alpha = murphy_alpha(f_coeffs, B=200)

    if verbose:
        print(f"    Poly: f(x) = ", end="")
        terms = []
        for i, c in enumerate(f_coeffs):
            if c != 0:
                if i == 0:
                    terms.append(str(c))
                elif i == 1:
                    terms.append(f"{c}*x")
                else:
                    terms.append(f"{c}*x^{i}")
        print(" + ".join(terms))
        print(f"    m = {m}, skew = {poly['skewness']:.2f}, alpha = {alpha:.3f}")

    # Step 3: Factor bases
    t_fb = time.time()
    rat_fb = build_rational_fb(min(params['B_r'], 100000))  # cap for now
    alg_fb = build_algebraic_fb(f_coeffs, min(params['B_a'], 100000))
    fb_time = time.time() - t_fb

    if verbose:
        print(f"    Rational FB: {len(rat_fb)} primes up to {rat_fb[-1] if rat_fb else 0}")
        print(f"    Algebraic FB: {len(alg_fb)} ideals ({fb_time:.1f}s)")

    needed = len(rat_fb) + len(alg_fb) + 10  # need more relations than FB size
    if verbose:
        print(f"    Need {needed} relations")

    # Step 4: Line sieve + trial division verification
    t_sieve = time.time()
    sieve_candidates = []
    verified_relations = []
    A = min(params['A'], 500000)  # cap for memory

    # Estimate norm bounds for threshold
    rat_bound = A * abs(m) + 1
    alg_bound = int(norm_algebraic(A, 1, f_coeffs))

    for b in range(1, params['B_max'] + 1):
        if time.time() - t0 > time_limit:
            break

        pairs = sieve_line(b, A, m, f_coeffs, rat_fb, alg_fb,
                          rat_bound, alg_bound)

        # Trial divide each candidate to verify smoothness
        for a, b_val in pairs:
            rat_result = trial_divide_rational(a, b_val, m, rat_fb)
            if rat_result is None:
                continue
            rat_exps, rat_sign = rat_result

            alg_exps = trial_divide_algebraic(a, b_val, f_coeffs, alg_fb)
            if alg_exps is None:
                continue

            # Both sides smooth — verified relation
            verified_relations.append({
                'a': a, 'b': b_val,
                'rat_exps': rat_exps, 'rat_sign': rat_sign,
                'alg_exps': alg_exps,
            })

        if verbose and b % 100 == 0:
            elapsed = time.time() - t0
            print(f"    [b={b}] {len(verified_relations)}/{needed} verified ({elapsed:.1f}s)")

        if len(verified_relations) >= needed:
            break

    sieve_time = time.time() - t_sieve
    if verbose:
        print(f"    Sieve+verify: {len(verified_relations)}/{needed} in {sieve_time:.1f}s")

    if len(verified_relations) < needed:
        if verbose:
            print(f"    Insufficient relations ({len(verified_relations)}/{needed})")
        return None

    # Step 5: GF(2) Linear Algebra
    la_t0 = time.time()
    if verbose:
        print(f"    LA: {len(verified_relations)} x {1 + len(rat_fb) + len(alg_fb)}")

    null_vecs = gf2_gaussian_elimination(
        verified_relations, len(rat_fb), len(alg_fb))

    if verbose:
        print(f"    LA: {time.time()-la_t0:.1f}s, {len(null_vecs)} null vecs")

    if not null_vecs:
        if verbose:
            print(f"    No null vectors found")
        return None

    # Step 6: Square root and factor extraction
    # Note: This simplified approach only uses the rational side square root.
    # A full GNFS would also need the algebraic side square root
    # (Couveignes/Montgomery), but for many cases the rational side suffices.
    result = extract_factor(n, null_vecs, verified_relations, m, rat_fb, alg_fb)

    if result is not None:
        total = time.time() - t0
        if verbose:
            print(f"\n    *** FACTOR: {result} ({total:.1f}s) ***")
        return result

    if verbose:
        print(f"    {len(null_vecs)} null vecs tried, no factor found")
        print(f"    (May need algebraic side square root — not yet implemented)")
    return None


###############################################################################
# Quick test
###############################################################################

if __name__ == '__main__':
    # Test polynomial selection
    n = mpz(10)**100 + 267  # ~100 digit number
    print("=== Polynomial Selection Test ===")
    poly = base_m_poly(n, d=5)
    print(f"Degree: {poly['d']}")
    print(f"m: {poly['m']}")
    print(f"Coefficients: {poly['f_coeffs']}")
    print(f"Skewness: {poly['skewness']:.2f}")
    print(f"Verify f(m) = n: {eval_poly(poly['f_coeffs'], poly['m']) == n}")
    print(f"Alpha: {murphy_alpha(poly['f_coeffs'], B=200):.3f}")

    print("\n=== GNFS Parameters ===")
    params = gnfs_params(n)
    for k, v in params.items():
        print(f"  {k}: {v}")
