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

    # L(n) = exp(c * (log n)^(1/3) * (log log n)^(2/3))
    ln_n = nb * math.log(2)
    ln_ln_n = math.log(ln_n) if ln_n > 1 else 1.0
    L = math.exp(0.5 * (ln_n ** (1/3)) * (ln_ln_n ** (2/3)))

    # Factor base bounds scale as L^(2/3)
    fb_bound = int(L ** 0.667)
    fb_bound = max(fb_bound, 10000)
    fb_bound = min(fb_bound, 50_000_000)  # cap for memory

    # Sieve region
    A = max(fb_bound * 10, 1_000_000)
    B_max = max(fb_bound // 10, 1000)

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


def sieve_line(b, A, m, f_coeffs, rat_fb, alg_fb, rat_bound, alg_bound):
    """
    Sieve one line (fixed b) for a in [-A, A].

    For each prime p in rational FB:
      Mark positions where p | (a + b*m), i.e., a ≡ -b*m (mod p)
    For each (p, r) in algebraic FB:
      Mark positions where p | norm_alg(a,b), i.e., a ≡ -b*r (mod p)

    Returns list of (a, b) pairs where both norms are smooth.
    """
    size = 2 * A + 1

    # Rational sieve array (log approximation)
    rat_log = np.zeros(size, dtype=np.float32)
    # Algebraic sieve array
    alg_log = np.zeros(size, dtype=np.float32)

    # Sieve rational side
    for p in rat_fb:
        if p == 0:
            continue
        log_p = math.log(p)
        # a ≡ -b*m (mod p)
        start = int((-b * m) % p)
        # Map to array index: a ranges from -A to A, index = a + A
        idx = (start - (-A)) % p  # first position >= 0
        while idx < size:
            rat_log[idx] += log_p
            idx += p

    # Sieve algebraic side
    for p, r in alg_fb:
        if p == 0:
            continue
        log_p = math.log(p)
        # a ≡ -b*r (mod p)
        start = int((-b * r) % p)
        idx = (start - (-A)) % p
        while idx < size:
            alg_log[idx] += log_p
            idx += p

    # Threshold: both sides must account for enough of the norm
    rat_thresh = math.log(rat_bound) * 0.7
    alg_thresh = math.log(alg_bound) * 0.7

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
# Top-Level: GNFS Factor (Work in Progress)
###############################################################################

def gnfs_factor(n, verbose=True, time_limit=3600):
    """
    Factor n using the General Number Field Sieve.

    Currently implements:
    - Polynomial selection (base-m)
    - Factor base construction
    - Basic line sieve

    TODO:
    - Full trial division to verify smooth pairs
    - GF(2) matrix construction from exponent vectors
    - Block Lanczos LA
    - Square root phase
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

    # Step 4: Line sieve
    t_sieve = time.time()
    relations = []
    A = min(params['A'], 500000)  # cap for memory

    # Estimate norm bounds for threshold
    rat_bound = A * abs(m) + 1
    alg_bound = int(norm_algebraic(A, 1, f_coeffs))

    for b in range(1, params['B_max'] + 1):
        if time.time() - t0 > time_limit:
            break

        pairs = sieve_line(b, A, m, f_coeffs, rat_fb, alg_fb,
                          rat_bound, alg_bound)
        relations.extend(pairs)

        if verbose and b % 100 == 0:
            elapsed = time.time() - t0
            print(f"    [b={b}] {len(relations)} relations ({elapsed:.1f}s)")

        if len(relations) >= needed:
            break

    sieve_time = time.time() - t_sieve
    if verbose:
        print(f"    Sieve: {len(relations)} relations in {sieve_time:.1f}s")
        print(f"    (LA and sqrt phases not yet implemented)")

    # TODO: Trial division to verify and build exponent vectors
    # TODO: Block Lanczos over GF(2)
    # TODO: Square root phase

    return None  # Not yet complete


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
