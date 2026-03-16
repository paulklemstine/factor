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
from numba import njit
import ctypes
import os

# Load C sieve extension
_gnfs_sieve_lib = None
def _load_gnfs_sieve():
    global _gnfs_sieve_lib
    if _gnfs_sieve_lib is not None:
        return _gnfs_sieve_lib
    so_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gnfs_sieve_c.so')
    if os.path.exists(so_path):
        _gnfs_sieve_lib = ctypes.CDLL(so_path)
        _gnfs_sieve_lib.sieve_batch_c.restype = ctypes.c_int
        _gnfs_sieve_lib.sieve_batch_c.argtypes = [
            ctypes.c_int, ctypes.c_int, ctypes.c_int,  # b_start, b_end, A
            ctypes.POINTER(ctypes.c_int64), ctypes.c_int, ctypes.c_int64,  # rat_primes, n_rat, m
            ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64), ctypes.c_int,  # alg_p, alg_r, n_alg
            ctypes.c_int, ctypes.c_int,  # rat_frac_x1000, alg_frac_x1000
            ctypes.c_int, ctypes.c_int64, ctypes.c_int64,  # poly_degree, f0_abs, fd_abs
            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.c_int,  # out_a, out_b, max
        ]
        # Register __int128 verify function
        _gnfs_sieve_lib.verify_candidates_c.restype = ctypes.c_int
        _gnfs_sieve_lib.verify_candidates_c.argtypes = [
            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.c_int,  # cand_a, cand_b, n_cands
            ctypes.c_int64,  # m
            ctypes.POINTER(ctypes.c_int64), ctypes.c_int,  # f_coeffs, degree
            ctypes.POINTER(ctypes.c_int64), ctypes.c_int,  # rat_primes, n_rat
            ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64), ctypes.c_int,  # alg_p, alg_r, n_alg
            ctypes.c_int64,  # lp_bound
            ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64),  # out_rat_exps, out_alg_exps
            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),  # out_signs, out_mask
            ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64),  # out_rat_lp, out_alg_lp
        ]
    return _gnfs_sieve_lib

# Load C lattice sieve extension
_lattice_sieve_lib = None
def _load_lattice_sieve():
    global _lattice_sieve_lib
    if _lattice_sieve_lib is not None:
        return _lattice_sieve_lib
    so_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lattice_sieve_c.so')
    if os.path.exists(so_path):
        _lattice_sieve_lib = ctypes.CDLL(so_path)
        # lattice_sieve_batch: process multiple special-q in one C call
        _lattice_sieve_lib.lattice_sieve_batch.restype = ctypes.c_int
        _lattice_sieve_lib.lattice_sieve_batch.argtypes = [
            ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64), ctypes.c_int,  # q_primes, q_roots, n_q
            ctypes.POINTER(ctypes.c_int64), ctypes.c_int, ctypes.c_int64,  # rat_primes, n_rat, m
            ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64), ctypes.c_int,  # alg_p, alg_r, n_alg
            ctypes.c_double, ctypes.c_double,  # rat_frac, alg_frac
            ctypes.c_int,  # poly_degree
            ctypes.c_int, ctypes.c_int,  # sieve_radius, sieve_height
            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),  # out_a, out_b
            ctypes.POINTER(ctypes.c_int64),  # out_q
            ctypes.c_int,  # max_cands
        ]
        # Single-q sieve (lower level)
        _lattice_sieve_lib.lattice_sieve_q.restype = ctypes.c_int
        _lattice_sieve_lib.lattice_sieve_q.argtypes = [
            ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64,  # e1x, e1y, e2x, e2y
            ctypes.c_int, ctypes.c_int,  # I_max, J_max
            ctypes.POINTER(ctypes.c_int64), ctypes.c_int, ctypes.c_int64,  # rat_primes, n_rat, m
            ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64), ctypes.c_int,  # alg_p, alg_r, n_alg
            ctypes.c_double, ctypes.c_double,  # rat_frac, alg_frac
            ctypes.c_int64, ctypes.c_int,  # q, poly_degree
            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),  # out_i, out_j
            ctypes.c_int,  # max_cands
        ]
        # Gauss reduce
        _lattice_sieve_lib.gauss_reduce_c.restype = None
        _lattice_sieve_lib.gauss_reduce_c.argtypes = [
            ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64),
            ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64),
        ]
    return _lattice_sieve_lib


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
        if nd < 40:
            d = 3
        elif nd < 65:
            d = 4
        elif nd < 100:
            d = 5
        elif nd < 150:
            d = 6
        else:
            d = 7

    # Base m = floor(n^(1/d))
    m0, exact = iroot(n, d)
    # If exact, n = m^d, which means m is a factor (trivial case)
    if exact:
        return {'factor': int(m0)}

    def _base_m_poly(n, m, d):
        """Express n in base m: f(m) = n, return coefficients."""
        coeffs = []
        remainder = n
        for i in range(d + 1):
            coeff = remainder % m
            remainder = remainder // m
            coeffs.append(int(coeff))
        if remainder > 0:
            coeffs[-1] = int(coeffs[-1] + remainder * m)
        # Verify
        f_at_m = mpz(0)
        m_power = mpz(1)
        for c in coeffs:
            f_at_m += mpz(c) * m_power
            m_power *= m
        if f_at_m != n:
            return None
        return coeffs

    def _poly_norm_score(coeffs, d):
        """Score polynomial by expected norm size over skewed sieve region.
        Lower = better. Uses skewness-adjusted evaluation points.
        Key: norms = |f(a/b)*b^d| = |sum c_i * a^i * b^(d-i)|
        Optimal skewness s balances c_0*s^d ~ c_d, so s ~ (|c_0|/|c_d|)^(1/d)
        Then evaluate at (a, b) ~ (s*t, t) for typical sieve points."""
        if coeffs is None:
            return float('inf')
        lc = abs(coeffs[-1])
        if lc == 0:
            return float('inf')
        # Compute optimal skewness
        c0 = abs(coeffs[0]) if coeffs[0] != 0 else 1
        skew = max(1.0, float(c0 / lc) ** (1.0 / d)) if lc > 0 else 1.0
        # Score: sum of log norms at multiple skewed test points
        # (a, b) = (skew * t, t) for various t
        score = 0.0
        for t in [10, 100, 1000, 10000]:
            a_test = max(1, int(skew * t))
            b_test = max(1, t)
            norm_est = sum(abs(coeffs[i]) * a_test**i * b_test**(d-i) for i in range(d+1))
            score += math.log(max(norm_est, 1))
        # Penalize large leading coefficient (harder to find smooth alg norms)
        score += 2.0 * math.log(lc + 1)
        # Penalize large max coefficient (causes overflow issues)
        max_coeff = max(abs(c) for c in coeffs)
        score += 0.5 * math.log(max_coeff + 1)
        return score

    # Try multiple m values near m0 and pick the best polynomial
    best_score = float('inf')
    best_coeffs = None
    best_m = int(m0)

    # Phase 1: Two-phase search with degree-dependent range
    # Wider range finds much better polynomials (research: 15800x smaller norms)
    if d <= 3:
        wide_range = 20000
    elif d == 4:
        wide_range = 10000
    else:
        wide_range = 5000

    # Phase 1a: Coarse scan every 10th value across wide range
    coarse_step = 10
    coarse_best_delta = 0
    coarse_best_score = float('inf')
    for delta in range(-wide_range, wide_range + 1, coarse_step):
        m_try = int(m0) + delta
        if m_try < 2:
            continue
        coeffs = _base_m_poly(n, mpz(m_try), d)
        if coeffs is None:
            continue
        score = _poly_norm_score(coeffs, d)
        if score < best_score:
            best_score = score
            best_coeffs = coeffs
            best_m = m_try
        if score < coarse_best_score:
            coarse_best_score = score
            coarse_best_delta = delta

    # Phase 1b: Fine scan ±50 around the best coarse candidate
    fine_range = 50
    fine_center = int(m0) + coarse_best_delta
    for delta in range(-fine_range, fine_range + 1):
        m_try = fine_center + delta
        if m_try < 2:
            continue
        coeffs = _base_m_poly(n, mpz(m_try), d)
        if coeffs is None:
            continue
        score = _poly_norm_score(coeffs, d)
        if score < best_score:
            best_score = score
            best_coeffs = coeffs
            best_m = m_try

    # Phase 2: Tree-based candidates — sum-of-two-squares bases near m0
    # Values m = a^2 + b^2 have factored-form algebraic norms, giving
    # smaller coefficients and better smoothness (T7 conjecture: 10-56x).
    # We sample (a,b) pairs with a^2 + b^2 ≈ m0 to generate candidates.
    import random as _rng
    m0_int = int(m0)
    m0_sqrt = int(math.isqrt(m0_int))
    tree_candidates_tried = 0
    # Sample ~2000 sum-of-squares values near m0
    for _ in range(2000):
        # Pick random a near sqrt(m0), compute b = sqrt(m0 - a^2)
        a_val = _rng.randint(max(1, m0_sqrt // 2), m0_sqrt)
        residual = m0_int - a_val * a_val
        if residual <= 0:
            continue
        b_val = int(math.isqrt(residual))
        # Try b_val and b_val+1 to get values just above/below m0
        for b_try in (b_val, b_val + 1):
            if b_try < 1:
                continue
            m_try = a_val * a_val + b_try * b_try
            if m_try < 2:
                continue
            tree_candidates_tried += 1
            coeffs = _base_m_poly(n, mpz(m_try), d)
            if coeffs is None:
                continue
            score = _poly_norm_score(coeffs, d)
            if score < best_score:
                best_score = score
                best_coeffs = coeffs
                best_m = m_try

    coeffs = best_coeffs
    m = best_m

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


@njit(cache=True)
def _jit_find_roots(coeffs, d_plus_1, p):
    """JIT brute-force root finding: evaluate polynomial at all x mod p."""
    roots = np.empty(d_plus_1, dtype=np.int64)
    count = 0
    for r in range(p):
        val = np.int64(0)
        r_pow = np.int64(1)
        for i in range(d_plus_1):
            val = (val + coeffs[i] * r_pow) % p
            r_pow = (r_pow * r) % p
        if val == 0:
            roots[count] = r
            count += 1
    return roots[:count]


def find_poly_roots_mod_p(coeffs, p):
    """
    Find all roots of polynomial f(x) mod p.
    Uses JIT brute force for small p (adequate for factor base construction).
    """
    coeffs_arr = np.array(coeffs, dtype=np.int64)
    result = _jit_find_roots(coeffs_arr, len(coeffs), p)
    return [int(x) for x in result]


def build_algebraic_fb(f_coeffs, B_a):
    """
    Build algebraic factor base.
    For each prime p <= B_a, find roots r of f(x) mod p.
    Each (p, r) pair is a first-degree prime ideal.

    Uses JIT brute force for small p, gmpy2-based root finding for large p.
    Returns list of (p, r) pairs.
    """
    fb = []
    d = len(f_coeffs) - 1
    # Use brute force for small p, switch to modular approach for large p
    # Brute force is O(p) per prime; for p > threshold, use Hensel/modular
    brute_limit = min(B_a, 50000)  # brute force up to 50K
    p = 2
    while p <= brute_limit:
        roots = find_poly_roots_mod_p(f_coeffs, p)
        for r in roots:
            fb.append((p, r))
        p = int(next_prime(p))

    # For larger primes, use Cantor-Zassenhaus (O(d^2 log p) per prime)
    if B_a > brute_limit:
        while p <= B_a:
            roots = _poly_roots_mod_p_smart(f_coeffs, p)
            for r in roots:
                fb.append((p, int(r)))
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
    if nd < 40:
        d = 3
    elif nd < 65:
        d = 4
    elif nd < 100:
        d = 5
    elif nd < 150:
        d = 6
    else:
        d = 7

    # L(n) = exp(c * (log n)^(1/3) * (log log n)^(2/3))
    ln_n = nb * math.log(2)
    ln_ln_n = math.log(ln_n) if ln_n > 1 else 1.0
    L = math.exp(0.5 * (ln_n ** (1/3)) * (ln_ln_n ** (2/3)))

    # Factor base bounds — use practical table for small n, L-formula for large
    # Key insight: FB must be large enough that smoothness probability is
    # reasonable. For alg norm of B bits over FB of F bits, u = B/F.
    # Need u < 4 ideally, u < 5 workable.
    if nd < 23:
        fb_bound = 10000
    elif nd < 27:
        fb_bound = 20000
    elif nd < 32:
        fb_bound = 40000
    elif nd < 37:
        fb_bound = 50000
    elif nd < 40:
        fb_bound = 70000
    elif nd < 48:
        fb_bound = 100000
    elif nd < 52:
        fb_bound = 150000
    elif nd < 56:
        fb_bound = 400000
    elif nd < 60:
        fb_bound = 600000
    elif nd < 65:
        fb_bound = 800000
    elif nd < 70:
        fb_bound = 1200000
    elif nd < 80:
        fb_bound = 2000000
    elif nd < 100:
        fb_bound = 4000000
    else:
        fb_bound = int(L ** 0.667)
        fb_bound = max(fb_bound, 8000000)
    fb_bound = min(fb_bound, 50_000_000)  # cap for memory

    # Sieve region: A = FB bound is the standard choice for line sieve.
    # With LP relations (SLP), norms can be slightly larger than FB bound
    # and still contribute, so A ~ FB is a good balance.
    A = fb_bound
    A = min(A, 5_000_000)  # cap for memory

    # B_max: generous — more b values is cheap with C sieve
    # For larger numbers, need more b values to find enough relations
    if nd >= 50:
        B_max = max(fb_bound * 20, 10000)
    elif nd >= 40:
        B_max = max(fb_bound * 15, 5000)
    else:
        B_max = max(fb_bound * 4, 5000)
    B_max = min(B_max, 5000000)

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


@njit(cache=True)
def _jit_norm_algebraic(a, b, coeffs, d):
    """JIT algebraic norm computation for small values (int64)."""
    result = np.int64(0)
    neg_a_pow = np.int64(1)
    b_pow = np.int64(1)
    for _ in range(d):
        b_pow *= b
    for i in range(d + 1):
        result += coeffs[i] * neg_a_pow * b_pow
        neg_a_pow *= -a
        if i < d:
            b_pow //= b
    return abs(result)


def norm_algebraic(a, b, f_coeffs):
    """
    Algebraic norm: |resultant of (a + b*alpha) and f(alpha)|
    = |b^d * f(-a/b)| = |sum(f_i * (-a)^i * b^(d-i))|
    """
    d = len(f_coeffs) - 1
    # Use JIT for small values that fit in int64
    if abs(a) < 100000 and abs(b) < 100000 and d <= 5:
        if not hasattr(norm_algebraic, '_coeffs'):
            norm_algebraic._coeffs = np.array(f_coeffs, dtype=np.int64)
        try:
            return int(_jit_norm_algebraic(np.int64(a), np.int64(b),
                                           norm_algebraic._coeffs, d))
        except OverflowError:
            pass
    # Fallback to mpz for large values
    result = mpz(0)
    for i, c in enumerate(f_coeffs):
        term = mpz(c) * (mpz(-a) ** i) * (mpz(b) ** (d - i))
        result += term
    return abs(result)


@njit(cache=True)
def _jit_sieve_rat(sieve_arr, primes, log_ps, starts, size):
    """JIT-compiled rational sieve: add log(p) at stride p."""
    for i in range(len(primes)):
        p = primes[i]
        lp = log_ps[i]
        idx = starts[i]
        while idx < size:
            sieve_arr[idx] += lp
            idx += p


@njit(cache=True)
def _jit_sieve_alg(sieve_arr, primes, roots, log_ps, starts, size):
    """JIT-compiled algebraic sieve: add log(p) at stride p for each (p,r)."""
    for i in range(len(primes)):
        p = primes[i]
        lp = log_ps[i]
        idx = starts[i]
        while idx < size:
            sieve_arr[idx] += lp
            idx += p


def sieve_line(b, A, m, f_coeffs, rat_fb, alg_fb, rat_bound=0, alg_bound=0):
    """
    Sieve one line (fixed b) for a in [-A, A].
    Uses numba JIT for the inner sieve loops.
    """
    size = 2 * A + 1
    rat_log = np.zeros(size, dtype=np.float32)
    alg_log = np.zeros(size, dtype=np.float32)

    # Precompute rational sieve starts (vectorized)
    bm = int(b) * int(m)
    if not hasattr(sieve_line, '_rat_primes') or len(sieve_line._rat_primes) != len(rat_fb):
        sieve_line._rat_primes = np.array(rat_fb, dtype=np.int64)
        sieve_line._rat_log_ps = np.log(sieve_line._rat_primes).astype(np.float32)
    rat_primes = sieve_line._rat_primes
    rat_log_ps = sieve_line._rat_log_ps
    rat_starts = ((-bm) % rat_primes + A) % rat_primes

    _jit_sieve_rat(rat_log, rat_primes, rat_log_ps, rat_starts, size)

    # Precompute algebraic sieve starts (vectorized)
    if not hasattr(sieve_line, '_alg_primes') or len(sieve_line._alg_primes) != len(alg_fb):
        sieve_line._alg_primes = np.array([p for p, r in alg_fb], dtype=np.int64)
        sieve_line._alg_log_ps = np.log(sieve_line._alg_primes).astype(np.float32)
        sieve_line._alg_roots = np.array([r for p, r in alg_fb], dtype=np.int64)
    alg_primes_arr = sieve_line._alg_primes
    alg_log_ps = sieve_line._alg_log_ps
    alg_roots_arr = sieve_line._alg_roots
    alg_starts = ((-int(b) * alg_roots_arr) % alg_primes_arr + A) % alg_primes_arr

    _jit_sieve_alg(alg_log, alg_primes_arr, alg_roots_arr, alg_log_ps, alg_starts, size)

    # Adaptive thresholds
    rat_typical = max(abs(bm), A)
    rat_thresh = math.log(rat_typical) * 0.6 if rat_typical > 1 else 1.0

    d = len(f_coeffs) - 1
    alg_center = abs(int(b) ** d * f_coeffs[0]) if f_coeffs[0] != 0 else abs(int(b) ** d)
    alg_typical = max(alg_center, 1)
    alg_thresh = math.log(alg_typical) * 0.5 if alg_typical > 1 else 1.0

    # Collect candidates (vectorized threshold check)
    mask = (rat_log >= rat_thresh) & (alg_log >= alg_thresh)
    candidates = np.nonzero(mask)[0]

    smooth_pairs = []
    for idx in candidates:
        a = int(idx) - A
        if a == 0:
            continue
        if gcd(mpz(abs(a)), mpz(b)) != 1:
            continue
        smooth_pairs.append((a, int(b)))

    return smooth_pairs


###############################################################################
# Phase 3a2: Lattice Sieve (Special-q)
###############################################################################

def gauss_reduce_2d(v1, v2):
    """2D Gauss lattice reduction. Returns (shorter, longer) reduced basis."""
    u = list(v1)
    v = list(v2)
    while True:
        nu = u[0] * u[0] + u[1] * u[1]
        nv = v[0] * v[0] + v[1] * v[1]
        if nv < nu:
            u, v = v, u
            nu, nv = nv, nu
        if nu == 0:
            break
        dot = u[0] * v[0] + u[1] * v[1]
        mu = round(dot / nu)
        if mu == 0:
            break
        v = [v[0] - mu * u[0], v[1] - mu * u[1]]
    return tuple(u), tuple(v)


def lattice_sieve_collect(n, f_coeffs, m, rat_fb, alg_fb, qc_primes, params,
                          needed, verbose=True, time_limit=3600, t0=None,
                          inert_qc_primes=None):
    """
    Collect relations using special-q lattice sieve on algebraic side.

    Uses C lattice sieve when available (lattice_sieve_c.so) for 10-50x
    speedup on candidate generation. Falls back to Python/JIT sieve.

    For each special-q prime q (above FB bound):
      - Find roots r of f(x) = 0 (mod q)
      - Lattice L = {(a,b) : a + b*r = 0 (mod q)}, Gauss-reduce
      - Sieve in reduced (i,j) coordinates
      - Algebraic norm divisible by q; trial-divide cofactor norm/q
    """
    if t0 is None:
        t0 = time.time()

    d = len(f_coeffs) - 1
    fb_bound = params['B_r']

    # Arrays for sieve
    rat_primes = np.array(rat_fb, dtype=np.int64)
    rat_log_ps = np.log(rat_primes).astype(np.float32)
    alg_primes = np.array([p for p, r in alg_fb], dtype=np.int64)
    alg_roots = np.array([r for p, r in alg_fb], dtype=np.int64)
    alg_log_ps = np.log(alg_primes).astype(np.float32)

    # Setup trial division caches
    trial_divide_rational._primes = rat_primes
    trial_divide_algebraic._primes = alg_primes
    trial_divide_algebraic._roots = alg_roots
    norm_algebraic._coeffs = np.array(f_coeffs, dtype=np.int64)

    verified = []
    sq_map = {}  # q -> column index
    sq_col_idx = 0
    total_candidates = 0

    q = int(next_prime(fb_bound))
    q_max = fb_bound * 200

    # Try to load C lattice sieve
    c_lattice_lib = _load_lattice_sieve()
    use_c_sieve = c_lattice_lib is not None

    if verbose and use_c_sieve:
        print("    Using C lattice sieve (lattice_sieve_c.so)")

    # Batch special-q collection for C sieve
    Q_BATCH_SIZE = 50  # process this many (q, root) pairs per C call

    while q <= q_max and len(verified) < needed:
        if time.time() - t0 > time_limit:
            break

        # Collect a batch of (q, root) pairs
        q_batch_primes = []
        q_batch_roots = []
        q_batch_q_vals = []  # track which q each root belongs to

        batch_q = q
        while len(q_batch_primes) < Q_BATCH_SIZE and batch_q <= q_max:
            roots = find_poly_roots_mod_p(f_coeffs, batch_q)
            if roots:
                for r in roots:
                    q_batch_primes.append(int(batch_q))
                    q_batch_roots.append(int(r))
                    if len(q_batch_primes) >= Q_BATCH_SIZE:
                        break
            batch_q = int(next_prime(batch_q))

        if not q_batch_primes:
            break

        # Update q for next iteration
        q = int(next_prime(q_batch_primes[-1]))

        if use_c_sieve:
            # === C LATTICE SIEVE PATH ===
            # Phase 1: C sieve generates (a,b) candidates
            # Phase 2: C verify_candidates_c does bulk trial division with LP
            # Phase 3: Python handles special-q exponents + QC for verified rels
            n_q = len(q_batch_primes)
            max_cands = 200000

            # Prepare ctypes arrays for sieve
            c_q_primes = (ctypes.c_int64 * n_q)(*q_batch_primes)
            c_q_roots = (ctypes.c_int64 * n_q)(*q_batch_roots)
            c_out_a = (ctypes.c_int * max_cands)()
            c_out_b = (ctypes.c_int * max_cands)()
            c_out_q = (ctypes.c_int64 * max_cands)()

            n_cands = c_lattice_lib.lattice_sieve_batch(
                c_q_primes, c_q_roots, n_q,
                rat_primes.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                len(rat_fb), ctypes.c_int64(int(m)),
                alg_primes.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                alg_roots.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                len(alg_fb),
                ctypes.c_double(0.55), ctypes.c_double(0.45),
                d,
                500000, 2000,  # sieve_radius, sieve_height max
                c_out_a, c_out_b, c_out_q, max_cands)

            total_candidates += n_cands

            if n_cands == 0:
                if verbose:
                    elapsed = time.time() - t0
                    print(f"    [C batch {n_q}q] 0 cands ({elapsed:.1f}s)")
                continue

            # Phase 2: Use C verify for bulk trial division with LP support
            c_verify_lib = _load_gnfs_sieve()
            # LP bound must be large enough to accept q values as LP cofactors
            # q can be up to q_max = fb_bound * 200, so set LP bound accordingly
            lp_bound = max(fb_bound * 200 + 1, min(fb_bound * 100, fb_bound ** 2))

            if c_verify_lib is not None:
                # Process in chunks to limit memory
                chunk_size = min(n_cands, 20000)
                n_rat_fb = len(rat_fb)
                n_alg_fb = len(alg_fb)
                f_coeffs_arr = np.array(f_coeffs, dtype=np.int64)

                for chunk_start in range(0, n_cands, chunk_size):
                    if len(verified) >= needed or time.time() - t0 > time_limit:
                        break
                    chunk_end = min(chunk_start + chunk_size, n_cands)
                    chunk_n = chunk_end - chunk_start

                    # Slice candidate arrays for this chunk
                    chunk_a = (ctypes.c_int * chunk_n)(*[c_out_a[chunk_start + i] for i in range(chunk_n)])
                    chunk_b = (ctypes.c_int * chunk_n)(*[c_out_b[chunk_start + i] for i in range(chunk_n)])

                    # Allocate verify output buffers
                    v_rat_exps = np.zeros(chunk_n * n_rat_fb, dtype=np.int64)
                    v_alg_exps = np.zeros(chunk_n * n_alg_fb, dtype=np.int64)
                    v_signs = (ctypes.c_int * chunk_n)()
                    v_mask = (ctypes.c_int * chunk_n)()
                    v_rat_lp = np.zeros(chunk_n, dtype=np.int64)
                    v_alg_lp = np.zeros(chunk_n, dtype=np.int64)

                    c_verify_lib.verify_candidates_c(
                        chunk_a, chunk_b, chunk_n,
                        ctypes.c_int64(int(m)),
                        f_coeffs_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                        d,
                        rat_primes.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                        n_rat_fb,
                        alg_primes.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                        alg_roots.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                        n_alg_fb,
                        ctypes.c_int64(int(lp_bound)),
                        v_rat_exps.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                        v_alg_exps.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                        v_signs, v_mask,
                        v_rat_lp.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                        v_alg_lp.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                    )

                    # Phase 3: Process verified candidates
                    rat_exps_2d = v_rat_exps.reshape(chunk_n, n_rat_fb)
                    alg_exps_2d = v_alg_exps.reshape(chunk_n, n_alg_fb)

                    for ci in range(chunk_n):
                        mask_val = v_mask[ci]
                        if mask_val == 0:
                            continue  # rejected by C verify

                        a_val = chunk_a[ci]
                        b_val = chunk_b[ci]
                        cand_q = int(c_out_q[chunk_start + ci])

                        # For lattice sieve: the C verify treats the full alg norm,
                        # but we need to account for special-q division.
                        # The alg_lp from C verify may actually be q or q*cofactor.
                        # We need: alg norm is divisible by q, and cofactor is smooth or LP.
                        #
                        # C verify found: norm = product(FB primes) * alg_lp_remainder
                        # For lattice sieve: norm should be divisible by q.
                        # Check: if alg_lp == 0 (fully smooth over FB), q must divide
                        #   one of the FB prime powers — which is possible if q < B.
                        #   But q > B by design, so the q factor is in the remainder.
                        #
                        # Cases:
                        #   mask=1 (full smooth): impossible for lattice sieve since q > B
                        #     UNLESS q divides the norm via the FB (q in FB range) — skip
                        #   mask=2 (rat LP): alg side fully smooth — q must be in FB, skip
                        #   mask=3 (alg LP): alg_lp should be q (or q*small)
                        #   mask=4 (DLP): alg_lp could contain q

                        rat_lp_val = int(v_rat_lp[ci])
                        alg_lp_val = int(v_alg_lp[ci])
                        rat_exps_list = [int(rat_exps_2d[ci, j]) for j in range(n_rat_fb)]
                        alg_exps_list = [int(alg_exps_2d[ci, j]) for j in range(n_alg_fb)]
                        sign_val = int(v_signs[ci])

                        # Handle special-q in algebraic remainder.
                        # The C verify sees the FULL alg norm (with q in it).
                        # Since q > FB_bound, q cannot be in the FB. So:
                        #   mask=1: alg fully smooth over FB — impossible, q missing
                        #   mask=2: alg fully smooth, rat has LP — impossible, q missing
                        #   mask=3: alg has LP = alg_lp_val. If LP == q, fully smooth after q.
                        #   mask=4: both have LP. If alg LP == q, becomes SLP (rat LP only).
                        # Skip mask=1,2 as false positives (q not accounted for).
                        if mask_val in (1, 2):
                            continue  # q > FB, can't be fully smooth on alg side
                        elif mask_val == 3:
                            # Alg LP should be q (norm = FB_primes * q)
                            if alg_lp_val == cand_q:
                                sq_exp = 1
                                alg_lp_val = 0  # consumed by special-q
                            else:
                                continue  # LP != q, false positive
                        elif mask_val == 4:
                            # DLP: alg LP should be q, leaving rat LP only
                            if alg_lp_val == cand_q:
                                sq_exp = 1
                                alg_lp_val = 0  # consumed by special-q
                            else:
                                continue  # LP != q
                        else:
                            continue

                        # After q removal, classify the relation
                        # C verify already did full trial division; the LP
                        # values are cofactors that didn't divide over FB.
                        # For lattice sieve:
                        #   - rat_lp_val: rational cofactor (0 if smooth)
                        #   - alg_lp_val: algebraic cofactor after q removal (0 if smooth)
                        # We accept: fully smooth, SLP (one side has LP), or skip DLP

                        has_rat_lp = (rat_lp_val != 0)
                        has_alg_lp = (alg_lp_val != 0)

                        # Skip DLP (both sides have LP) — too complex for lattice sieve
                        if has_rat_lp and has_alg_lp:
                            continue

                        qc_bits = compute_qc_vector(a_val, b_val, qc_primes)
                        if inert_qc_primes:
                            qc_bits += compute_inert_qc_vector(
                                a_val, b_val, inert_qc_primes, f_coeffs)

                        if cand_q not in sq_map:
                            sq_map[cand_q] = sq_col_idx
                            sq_col_idx += 1

                        verified.append({
                            'a': a_val, 'b': b_val,
                            'rat_exps': rat_exps_list, 'rat_sign': sign_val,
                            'alg_exps': alg_exps_list,
                            'qc_bits': qc_bits,
                            'special_q': cand_q,
                            'sq_col': sq_map[cand_q],
                            'sq_exp': sq_exp,
                        })

            else:
                # No C verify — Python fallback verification
                for ci in range(n_cands):
                    if len(verified) >= needed:
                        break
                    if time.time() - t0 > time_limit:
                        break

                    a = c_out_a[ci]
                    b_val = c_out_b[ci]
                    cand_q = int(c_out_q[ci])

                    if b_val <= 0 or a == 0:
                        continue
                    if gcd(mpz(abs(a)), mpz(b_val)) != 1:
                        continue

                    rat_result = trial_divide_rational(a, b_val, m, rat_fb)
                    if rat_result is None:
                        continue
                    rat_exps, rat_sign = rat_result

                    alg_norm = abs(int(norm_algebraic(a, b_val, f_coeffs)))
                    if alg_norm == 0 or alg_norm % cand_q != 0:
                        continue
                    sq_exp = 0
                    cofactor = alg_norm
                    while cofactor % cand_q == 0:
                        cofactor //= cand_q
                        sq_exp += 1

                    if cofactor < (1 << 63):
                        exps = np.zeros(len(alg_fb), dtype=np.int64)
                        remainder = _jit_trial_divide_alg(
                            np.int64(cofactor), alg_primes, alg_roots,
                            np.int64(a), np.int64(b_val), exps)
                        remainder = int(remainder)
                        alg_exps = [int(e) for e in exps]
                    else:
                        alg_exps = [0] * len(alg_fb)
                        remainder = cofactor
                        for pi in range(len(alg_fb)):
                            p = int(alg_primes[pi])
                            rp = int(alg_roots[pi])
                            if (a + b_val * rp) % p == 0:
                                while remainder % p == 0:
                                    remainder //= p
                                    alg_exps[pi] += 1
                    if remainder != 1:
                        continue

                    qc_bits = compute_qc_vector(a, b_val, qc_primes)
                    if inert_qc_primes:
                        qc_bits += compute_inert_qc_vector(
                            a, b_val, inert_qc_primes, f_coeffs)

                    if cand_q not in sq_map:
                        sq_map[cand_q] = sq_col_idx
                        sq_col_idx += 1

                    verified.append({
                        'a': a, 'b': b_val,
                        'rat_exps': rat_exps, 'rat_sign': rat_sign,
                        'alg_exps': alg_exps,
                        'qc_bits': qc_bits,
                        'special_q': cand_q,
                        'sq_col': sq_map[cand_q],
                        'sq_exp': sq_exp,
                    })

            if verbose:
                elapsed = time.time() - t0
                print(f"    [C batch {n_q}q] +{n_cands} cands → {len(verified)}/{needed} "
                      f"({elapsed:.1f}s)")

        else:
            # === PYTHON FALLBACK PATH ===
            for qi in range(len(q_batch_primes)):
                cur_q = q_batch_primes[qi]
                r = q_batch_roots[qi]

                if len(verified) >= needed:
                    break
                if time.time() - t0 > time_limit:
                    break

                # Lattice: a = -b*r (mod q)
                v1 = (cur_q, 0)
                v2 = (int((-r) % cur_q), 1)
                e1, e2 = gauss_reduce_2d(v1, v2)

                len_e1 = math.sqrt(e1[0]**2 + e1[1]**2)
                len_e2 = math.sqrt(e2[0]**2 + e2[1]**2)

                # Sieve region: keep norms manageable
                I_max = max(int(50000 / max(len_e1, 1)), 50)
                J_max = max(int(200 / max(len_e2, 1)), 2)
                I_max = min(I_max, 500000)
                J_max = min(J_max, 2000)
                size = 2 * I_max + 1

                # Precompute per-prime sieve constants for this lattice
                e1_m = e1[0] + e1[1] * int(m)
                e2_m = e2[0] + e2[1] * int(m)
                R1 = np.array([e1_m % p for p in rat_fb], dtype=np.int64)
                R2 = np.array([e2_m % p for p in rat_fb], dtype=np.int64)
                R1_inv = np.array([pow(int(R1[i]), int(rat_primes[i]) - 2,
                                       int(rat_primes[i])) if R1[i] != 0 else 0
                                   for i in range(len(rat_fb))], dtype=np.int64)
                rat_valid = R1 != 0
                R2_R1inv = np.array([(int(R2[i]) * int(R1_inv[i])) % int(rat_primes[i])
                                     if rat_valid[i] else 0
                                     for i in range(len(rat_fb))], dtype=np.int64)

                U = np.array([(e1[0] + e1[1] * int(alg_roots[i])) % int(alg_primes[i])
                              for i in range(len(alg_fb))], dtype=np.int64)
                V = np.array([(e2[0] + e2[1] * int(alg_roots[i])) % int(alg_primes[i])
                              for i in range(len(alg_fb))], dtype=np.int64)
                U_inv = np.array([pow(int(U[i]), int(alg_primes[i]) - 2,
                                      int(alg_primes[i])) if U[i] != 0 else 0
                                  for i in range(len(alg_fb))], dtype=np.int64)
                alg_valid = U != 0
                V_Uinv = np.array([(int(V[i]) * int(U_inv[i])) % int(alg_primes[i])
                                    if alg_valid[i] else 0
                                    for i in range(len(alg_fb))], dtype=np.int64)

                q_rels = []
                for j in range(0, J_max + 1):
                    if time.time() - t0 > time_limit:
                        break

                    rat_sieve = np.zeros(size, dtype=np.float32)
                    alg_sieve = np.zeros(size, dtype=np.float32)

                    rat_starts = np.empty(len(rat_fb), dtype=np.int64)
                    for pi in range(len(rat_fb)):
                        if not rat_valid[pi]:
                            rat_starts[pi] = size
                        else:
                            p = int(rat_primes[pi])
                            rat_starts[pi] = ((-j * int(R2_R1inv[pi])) % p + I_max) % p
                    _jit_sieve_rat(rat_sieve, rat_primes, rat_log_ps, rat_starts, size)

                    alg_starts = np.empty(len(alg_fb), dtype=np.int64)
                    for pi in range(len(alg_fb)):
                        if not alg_valid[pi]:
                            alg_starts[pi] = size
                        else:
                            p = int(alg_primes[pi])
                            alg_starts[pi] = ((-j * int(V_Uinv[pi])) % p + I_max) % p
                    _jit_sieve_alg(alg_sieve, alg_primes, alg_roots, alg_log_ps,
                                   alg_starts, size)

                    rat_typical = max(abs(I_max * e1_m + j * e2_m), abs(e1_m), 2)
                    rat_thresh = math.log(rat_typical) * 0.55

                    a_center = j * abs(e2[0]) + I_max * abs(e1[0])
                    b_center = max(j * abs(e2[1]) + I_max * abs(e1[1]), 1)
                    alg_cofactor_est = max(2, a_center**d + b_center**d) // max(cur_q, 1)
                    alg_thresh = math.log(max(alg_cofactor_est, 2)) * 0.45

                    mask = (rat_sieve >= rat_thresh) & (alg_sieve >= alg_thresh)
                    candidates = np.nonzero(mask)[0]
                    total_candidates += len(candidates)

                    for idx in candidates:
                        i_val = int(idx) - I_max
                        a = i_val * e1[0] + j * e2[0]
                        b_val = i_val * e1[1] + j * e2[1]

                        if b_val <= 0 or a == 0:
                            continue
                        if gcd(mpz(abs(a)), mpz(b_val)) != 1:
                            continue

                        rat_result = trial_divide_rational(a, b_val, m, rat_fb)
                        if rat_result is None:
                            continue
                        rat_exps, rat_sign = rat_result

                        alg_norm = abs(int(norm_algebraic(a, b_val, f_coeffs)))
                        if alg_norm == 0 or alg_norm % cur_q != 0:
                            continue
                        sq_exp = 0
                        cofactor = alg_norm
                        while cofactor % cur_q == 0:
                            cofactor //= cur_q
                            sq_exp += 1

                        if cofactor < (1 << 63):
                            exps = np.zeros(len(alg_fb), dtype=np.int64)
                            remainder = _jit_trial_divide_alg(
                                np.int64(cofactor), alg_primes, alg_roots,
                                np.int64(a), np.int64(b_val), exps)
                            remainder = int(remainder)
                            alg_exps = [int(e) for e in exps]
                        else:
                            alg_exps = [0] * len(alg_fb)
                            remainder = cofactor
                            for pi in range(len(alg_fb)):
                                p = int(alg_primes[pi])
                                rp = int(alg_roots[pi])
                                if (a + b_val * rp) % p == 0:
                                    while remainder % p == 0:
                                        remainder //= p
                                        alg_exps[pi] += 1
                        if remainder != 1:
                            continue

                        qc_bits = compute_qc_vector(a, b_val, qc_primes)
                        if inert_qc_primes:
                            qc_bits += compute_inert_qc_vector(
                                a, b_val, inert_qc_primes, f_coeffs)

                        if cur_q not in sq_map:
                            sq_map[cur_q] = sq_col_idx
                            sq_col_idx += 1

                        q_rels.append({
                            'a': a, 'b': b_val,
                            'rat_exps': rat_exps, 'rat_sign': rat_sign,
                            'alg_exps': alg_exps,
                            'qc_bits': qc_bits,
                            'special_q': cur_q,
                            'sq_col': sq_map[cur_q],
                            'sq_exp': sq_exp,
                        })

                verified.extend(q_rels)

                if verbose and q_rels:
                    elapsed = time.time() - t0
                    print(f"    [q={cur_q},r={r}] +{len(q_rels)} -> {len(verified)}/{needed} "
                          f"({elapsed:.1f}s, {total_candidates} cands)")

    return verified, sq_map


def merge_sq_relations(relations):
    """
    Merge lattice sieve relations sharing a special-q, eliminating SQ columns.

    For each q with k≥2 relations, pick one as base and produce k-1 merged
    relations by pairwise combining with the base. The q exponents cancel
    (both odd → sum even). Singletons (k=1) are discarded.

    Merged relations store lists of (a,b) pairs for algebraic square root.
    """
    from collections import defaultdict
    groups = defaultdict(list)
    non_sq = []
    for rel in relations:
        q = rel.get('special_q', None)
        if q is not None:
            groups[q].append(rel)
        else:
            non_sq.append(rel)

    merged = list(non_sq)
    n_singleton = 0
    for q, rels in groups.items():
        if len(rels) < 2:
            n_singleton += 1
            continue
        base = rels[0]
        nrat = len(base['rat_exps'])
        nalg = len(base['alg_exps'])
        nqc = len(base.get('qc_bits', []))
        for other in rels[1:]:
            merged.append({
                'a_list': [base['a'], other['a']],
                'b_list': [base['b'], other['b']],
                'a': base['a'],  # primary a for compatibility
                'b': base['b'],
                'rat_exps': [base['rat_exps'][j] + other['rat_exps'][j]
                             for j in range(nrat)],
                'alg_exps': [base['alg_exps'][j] + other['alg_exps'][j]
                             for j in range(nalg)],
                'rat_sign': base['rat_sign'] + other['rat_sign'],
                'qc_bits': [base['qc_bits'][j] ^ other['qc_bits'][j]
                            for j in range(nqc)] if nqc > 0 else [],
            })
    return merged, n_singleton


###############################################################################
# Phase 3b: Trial Division Verification
###############################################################################

@njit(cache=True)
def _jit_trial_divide_rat(val, primes, exps_out):
    """JIT rational trial division. Returns remainder."""
    for i in range(len(primes)):
        p = primes[i]
        while val % p == 0:
            val //= p
            exps_out[i] += 1
    return val


@njit(cache=True)
def _jit_trial_divide_alg(val, primes, roots, a, b, exps_out):
    """JIT algebraic trial division with divisibility pre-check."""
    for i in range(len(primes)):
        p = primes[i]
        r = roots[i]
        if (a + b * r) % p == 0:
            while val % p == 0:
                val //= p
                exps_out[i] += 1
    return val


@njit(cache=True)
def _jit_mulmod64(a, b, m):
    """Modular multiplication avoiding overflow via 128-bit emulation."""
    # For values < 2^31, direct multiply is safe
    if a < (np.int64(1) << 31) and b < (np.int64(1) << 31):
        return (a * b) % m
    # Otherwise, use repeated doubling
    result = np.int64(0)
    a = a % m
    while b > 0:
        if b & 1:
            result = (result + a) % m
        a = (a + a) % m
        b >>= 1
    return result


@njit(cache=True)
def _jit_is_prime_small(n):
    """Simple primality test for int64 values."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    # Miller-Rabin with deterministic witnesses for n < 3.3*10^24
    d = n - 1
    r = np.int64(0)
    while d % 2 == 0:
        d //= 2
        r += 1
    # Witnesses sufficient for n < 3.2*10^18
    for witness in (2, 3, 5, 7, 11, 13):
        if witness >= n:
            continue
        a = np.int64(witness)
        # x = pow(a, d, n) using mulmod
        x = np.int64(1)
        base = a % n
        exp = d
        while exp > 0:
            if exp & 1:
                x = _jit_mulmod64(x, base, n)
            base = _jit_mulmod64(base, base, n)
            exp >>= 1
        if x == 1 or x == n - 1:
            continue
        composite = True
        for _ in range(r - 1):
            x = _jit_mulmod64(x, x, n)
            if x == n - 1:
                composite = False
                break
        if composite:
            return False
    return True


@njit(cache=True)
def _jit_batch_verify(a_arr, b_arr, n_cands, m, f_coeffs_arr, d,
                       rat_primes, alg_primes, alg_roots,
                       out_rat_exps, out_alg_exps, out_signs, out_mask,
                       out_rat_lp, out_alg_lp, lp_bound):
    """Batch trial division with SLP support.
    out_mask: 0=reject, 1=full, 2=partial-rat-LP, 3=partial-alg-LP, 4=partial-both-LP
    out_rat_lp/out_alg_lp: large prime (0 if smooth on that side)
    """
    n_rat = len(rat_primes)
    n_alg = len(alg_primes)
    count = 0
    for ci in range(n_cands):
        a = a_arr[ci]
        b = b_arr[ci]

        # GCD check
        ga = abs(a)
        gb = b
        while gb != 0:
            ga, gb = gb, ga % gb
        if ga != 1:
            continue

        # Rational norm: |a + b*m|
        raw = a + b * m
        val_r = abs(raw)
        if val_r == 0:
            continue
        sign = 1 if raw < 0 else 0

        # Trial divide rational
        for j in range(n_rat):
            out_rat_exps[ci, j] = 0
        remainder = val_r
        for j in range(n_rat):
            p = rat_primes[j]
            while remainder % p == 0:
                remainder //= p
                out_rat_exps[ci, j] += 1

        rat_smooth = (remainder == 1)
        rat_lp = np.int64(0)
        if not rat_smooth:
            if remainder > 1 and remainder <= lp_bound and _jit_is_prime_small(remainder):
                rat_lp = remainder
            else:
                continue  # cofactor too large or composite

        # Algebraic norm: |sum(f_i * (-a)^i * b^(d-i))|
        norm = np.int64(0)
        neg_a_pow = np.int64(1)
        b_pow = np.int64(1)
        for k in range(d):
            b_pow *= b
        for k in range(d + 1):
            norm += f_coeffs_arr[k] * neg_a_pow * b_pow
            neg_a_pow *= np.int64(-a)
            if k < d:
                b_pow //= b
        val_a = abs(norm)
        if val_a == 0:
            continue

        # Trial divide algebraic
        for j in range(n_alg):
            out_alg_exps[ci, j] = 0
        remainder_a = val_a
        for j in range(n_alg):
            p = alg_primes[j]
            r = alg_roots[j]
            if (a + b * r) % p == 0:
                while remainder_a % p == 0:
                    remainder_a //= p
                    out_alg_exps[ci, j] += 1

        alg_smooth = (remainder_a == 1)
        alg_lp = np.int64(0)
        if not alg_smooth:
            if remainder_a > 1 and remainder_a <= lp_bound and _jit_is_prime_small(remainder_a):
                alg_lp = remainder_a
            else:
                continue

        out_signs[ci] = sign
        out_rat_lp[ci] = rat_lp
        out_alg_lp[ci] = alg_lp

        if rat_smooth and alg_smooth:
            out_mask[ci] = 1  # full relation
        elif rat_smooth and not alg_smooth:
            out_mask[ci] = 3  # partial: alg LP
        elif not rat_smooth and alg_smooth:
            out_mask[ci] = 2  # partial: rat LP
        else:
            out_mask[ci] = 4  # partial: both LPs (rare, skip for now)
        count += 1
    return count


def trial_divide_rational(a, b, m, rat_fb):
    """
    Trial divide the rational norm |a + b*m| over the rational factor base.
    Returns (exponent_vector, remainder) or None if not smooth.
    """
    raw = int(a) + int(b) * int(m)
    val = abs(raw)
    if val == 0:
        return None
    sign = 1 if raw < 0 else 0

    if not hasattr(trial_divide_rational, '_primes'):
        trial_divide_rational._primes = np.array(rat_fb, dtype=np.int64)
    primes = trial_divide_rational._primes

    # Reuse buffer to avoid allocation
    if not hasattr(trial_divide_rational, '_exps') or len(trial_divide_rational._exps) != len(rat_fb):
        trial_divide_rational._exps = np.zeros(len(rat_fb), dtype=np.int64)
    exps = trial_divide_rational._exps
    exps[:] = 0

    if val < (1 << 63):
        remainder = _jit_trial_divide_rat(np.int64(val), primes, exps)
        remainder = int(remainder)
    else:
        # Fallback for norms exceeding int64: use gmpy2 trial division
        remainder = mpz(val)
        for pi in range(len(primes)):
            p = int(primes[pi])
            while remainder % p == 0:
                remainder = remainder // p
                exps[pi] += 1
        remainder = int(remainder)
    if remainder == 1:
        return (exps.tolist(), sign)
    return None


def trial_divide_algebraic(a, b, f_coeffs, alg_fb):
    """
    Trial divide the algebraic norm over the algebraic factor base.
    Returns exponent_vector or None if not smooth.
    """
    val = abs(int(norm_algebraic(a, b, f_coeffs)))
    if val == 0:
        return None

    if not hasattr(trial_divide_algebraic, '_primes'):
        trial_divide_algebraic._primes = np.array([p for p, r in alg_fb], dtype=np.int64)
        trial_divide_algebraic._roots = np.array([r for p, r in alg_fb], dtype=np.int64)
    primes = trial_divide_algebraic._primes
    roots = trial_divide_algebraic._roots

    # Reuse buffer
    if not hasattr(trial_divide_algebraic, '_exps') or len(trial_divide_algebraic._exps) != len(alg_fb):
        trial_divide_algebraic._exps = np.zeros(len(alg_fb), dtype=np.int64)
    exps = trial_divide_algebraic._exps
    exps[:] = 0

    if val < (1 << 63):
        remainder = _jit_trial_divide_alg(np.int64(val), primes, roots,
                                           np.int64(a), np.int64(b), exps)
        remainder = int(remainder)
    else:
        # Fallback for norms exceeding int64: use gmpy2 trial division
        remainder = mpz(val)
        for pi in range(len(primes)):
            p = int(primes[pi])
            r = int(roots[pi])
            if (a + b * r) % p == 0:
                while remainder % p == 0:
                    remainder = remainder // p
                    exps[pi] += 1
        remainder = int(remainder)
    if remainder == 1:
        return exps.tolist()
    return None


###############################################################################
# Phase 3c: Quadratic Characters
###############################################################################

def build_qc_primes(f_coeffs, num_qc=20, min_p=50000):
    """
    Select primes for quadratic character columns.
    Choose primes q where f has a root mod q (so Legendre symbol is defined).
    Returns list of (q, r) pairs where r is a root of f mod q.
    """
    qc = []
    p = int(next_prime(min_p))
    while len(qc) < num_qc:
        roots = find_poly_roots_mod_p(f_coeffs, p)
        if roots:
            qc.append((p, roots[0]))
        p = int(next_prime(p))
    return qc


@njit(cache=True)
def _jit_powmod(base, exp, mod):
    """Fast modular exponentiation."""
    result = np.int64(1)
    base = base % mod
    while exp > 0:
        if exp & 1:
            result = result * base % mod
        exp >>= 1
        base = base * base % mod
    return result


@njit(cache=True)
def _jit_compute_qc_batch(a_arr, b_arr, mask, n_cands, qc_q, qc_r, n_qc, out_qc):
    """Batch QC computation for splitting primes."""
    for ci in range(n_cands):
        if mask[ci] == 0:
            continue
        a = a_arr[ci]
        b = b_arr[ci]
        for j in range(n_qc):
            q = qc_q[j]
            r = qc_r[j]
            val = (a + b * r) % q
            if val < 0:
                val += q
            if val == 0:
                out_qc[ci, j] = 0
            else:
                ls = _jit_powmod(val, (q - 1) // 2, q)
                out_qc[ci, j] = 1 if ls == q - 1 else 0


def compute_qc_vector(a, b, qc_primes):
    """
    Compute quadratic character vector for relation (a, b).
    For each QC prime (q, r): bit is 1 if (a + b*r) is a non-residue mod q.
    """
    bits = []
    for q, r in qc_primes:
        val = (int(a) + int(b) * r) % q
        if val == 0:
            bits.append(0)  # convention: 0 valuation
        else:
            # Legendre symbol
            ls = pow(val, (q - 1) // 2, q)
            bits.append(1 if ls == q - 1 else 0)
    return bits


def build_inert_qc_primes(f_coeffs, num_qc=20, min_p=100):
    """Find inert primes (where f has no roots) for additional QC columns."""
    inert = []
    p = int(next_prime(min_p))
    while len(inert) < num_qc:
        roots = find_poly_roots_mod_p(f_coeffs, p)
        if not roots:
            inert.append(p)
        p = int(next_prime(p))
    return inert


def compute_inert_qc_vector(a, b, inert_primes, f_coeffs):
    """
    Compute QC bits at inert primes.
    At inert q, (a+b·α) lives in F_{q^d}. Check if it's a QR:
    bit = 0 if (a+b·α)^{(q^d-1)/2} = 1, else 1.
    """
    d = len(f_coeffs) - 1
    bits = []
    for q in inert_primes:
        elem = [int(a) % q, int(b) % q] + [0] * (d - 2)
        order_half = (q ** d - 1) // 2
        check = _poly_pow_mod_ring(elem, order_half, f_coeffs, q)
        one = [1] + [0] * (d - 1)
        bits.append(0 if check == one else 1)
    return bits


###############################################################################
# Phase 4: GF(2) Linear Algebra (SGE + Gaussian Elimination)
###############################################################################

def _sge_reduce(sparse_rows, verbose=False):
    """
    Structured Gaussian Elimination: reduce sparse GF(2) matrix by
    eliminating singleton and doubleton columns.

    sparse_rows: list of sets of column indices (each row's non-zero columns)
    Returns: (reduced_rows, compositions, null_vec_compositions)
    """
    from collections import defaultdict

    n = len(sparse_rows)
    rows = [set(r) for r in sparse_rows]
    compositions = [{i} for i in range(n)]
    active = set(range(n))

    total_singleton = 0
    total_doubleton = 0

    for pass_num in range(500):
        # Build column → active rows map
        col_rows = defaultdict(list)
        for ri in active:
            for c in rows[ri]:
                col_rows[c].append(ri)

        # Pass 1: Singleton elimination (columns in exactly 1 row → remove that row)
        removed = set()
        for c, rlist in col_rows.items():
            if len(rlist) == 1 and rlist[0] in active and rlist[0] not in removed:
                removed.add(rlist[0])

        if removed:
            active -= removed
            total_singleton += len(removed)
            continue

        # Pass 2: Doubleton merging (columns in exactly 2 rows → merge rows via XOR)
        merged_any = False
        touched = set()
        for c in list(col_rows.keys()):
            rlist = col_rows[c]
            live = [r for r in rlist if r in active and r not in touched]
            if len(live) == 2:
                r1, r2 = live
                rows[r1] = rows[r1].symmetric_difference(rows[r2])
                compositions[r1] = compositions[r1].symmetric_difference(compositions[r2])
                active.discard(r2)
                touched.add(r1)
                merged_any = True
                total_doubleton += 1

        if not merged_any:
            break

    # Collect results
    reduced_rows = []
    reduced_comps = []
    null_vec_comps = []
    for ri in sorted(active):
        if rows[ri]:
            reduced_rows.append(rows[ri])
            reduced_comps.append(sorted(compositions[ri]))
        else:
            null_vec_comps.append(sorted(compositions[ri]))

    if verbose:
        print(f"    SGE: {n}→{len(reduced_rows)} rows "
              f"({total_singleton} singleton, {total_doubleton} doubleton, "
              f"{len(null_vec_comps)} null vecs)")

    return reduced_rows, reduced_comps, null_vec_comps


def gf2_gaussian_elimination(relations, ncols_rat, ncols_alg, num_qc=0, num_sq=0, num_lp=0, verbose=False):
    """
    Build GF(2) matrix from relations and find null space vectors.
    Uses SGE preprocessing to reduce matrix size, then numpy-vectorized dense Gauss.

    Matrix columns = 1 (sign) + ncols_rat + ncols_alg + num_qc + num_sq + num_lp.
    """
    nrows = len(relations)
    ncols = 1 + ncols_rat + ncols_alg + num_qc + num_sq + num_lp

    # Step 1: Build sparse representation
    sparse_rows = []
    for rel in relations:
        cols = set()
        if rel['rat_sign'] % 2:
            cols.add(0)
        for j, e in enumerate(rel['rat_exps']):
            if e % 2 == 1:
                cols.add(j + 1)
        for j, e in enumerate(rel['alg_exps']):
            if e % 2 == 1:
                cols.add(j + 1 + ncols_rat)
        qc_bits = rel.get('qc_bits', [])
        for j, bit in enumerate(qc_bits):
            if bit:
                cols.add(j + 1 + ncols_rat + ncols_alg)
        sq_col = rel.get('sq_col', -1)
        sq_exp = rel.get('sq_exp', 0)
        if sq_col >= 0 and sq_exp % 2 == 1:
            cols.add(1 + ncols_rat + ncols_alg + num_qc + sq_col)
        for lp_col in rel.get('lp_cols', []):
            cols.add(1 + ncols_rat + ncols_alg + num_qc + num_sq + lp_col)
        sparse_rows.append(cols)

    # Step 2: SGE preprocessing
    reduced_rows, compositions, sge_null_vecs = _sge_reduce(sparse_rows, verbose=verbose)

    # Map SGE null vectors back to original relation indices
    null_vecs = list(sge_null_vecs)

    if not reduced_rows:
        return null_vecs

    # Renumber columns for dense matrix
    all_cols = set()
    for row in reduced_rows:
        all_cols.update(row)
    col_list = sorted(all_cols)
    col_map = {c: i for i, c in enumerate(col_list)}
    n_reduced_cols = len(col_list)
    n_reduced_rows = len(reduced_rows)

    if verbose:
        print(f"    Dense: {n_reduced_rows} x {n_reduced_cols}")

    # Step 3: Build dense bit-packed matrix from reduced rows
    nwords_mat = (n_reduced_cols + 63) // 64
    nwords_combo = (n_reduced_rows + 63) // 64
    mat = np.zeros((n_reduced_rows, nwords_mat), dtype=np.uint64)
    combo = np.zeros((n_reduced_rows, nwords_combo), dtype=np.uint64)

    for i in range(n_reduced_rows):
        combo[i, i // 64] = np.uint64(1) << np.uint64(i % 64)

    for ri, row in enumerate(reduced_rows):
        for c_orig in row:
            c = col_map[c_orig]
            mat[ri, c // 64] |= np.uint64(1) << np.uint64(c % 64)

    # Step 4: Gaussian elimination with numpy-vectorized XOR
    used = np.zeros(n_reduced_rows, dtype=np.bool_)

    for col in range(n_reduced_cols):
        word = col // 64
        bit = np.uint64(1) << np.uint64(col % 64)
        piv = -1
        for row in range(n_reduced_rows):
            if not used[row] and mat[row, word] & bit:
                piv = row
                break
        if piv == -1:
            continue
        used[piv] = True
        has_bit = (mat[:, word] & bit).astype(np.bool_)
        has_bit[piv] = False
        rows_to_xor = np.where(has_bit)[0]
        if len(rows_to_xor) > 0:
            mat[rows_to_xor] ^= mat[piv]
            combo[rows_to_xor] ^= combo[piv]

    # Step 5: Extract null vectors and map through SGE compositions
    mat_zero = np.all(mat == 0, axis=1)
    for row in np.where(mat_zero)[0]:
        # Get reduced row indices from combo
        reduced_indices = []
        for w in range(nwords_combo):
            bits = int(combo[row, w])
            base = w * 64
            while bits:
                lsb = bits & (-bits)
                reduced_indices.append(base + lsb.bit_length() - 1)
                bits ^= lsb
        reduced_indices = [i for i in reduced_indices if i < n_reduced_rows]

        # Map through SGE compositions to original relation indices
        original_indices = set()
        for ri in reduced_indices:
            original_indices.symmetric_difference_update(compositions[ri])

        if original_indices:
            null_vecs.append(sorted(original_indices))

    return null_vecs


###############################################################################
# Phase 5: Algebraic Square Root (Couveignes-style)
###############################################################################

###############################################################################
# Polynomial arithmetic mod p (for large-prime root finding)
###############################################################################

def _poly_mul_mod(a, b, mod_poly, p):
    """Multiply polynomials a*b mod (mod_poly, p). Coefficients are lists."""
    # Standard polynomial multiplication
    result = [0] * (len(a) + len(b) - 1)
    for i, ca in enumerate(a):
        if ca == 0:
            continue
        for j, cb in enumerate(b):
            result[i + j] = (result[i + j] + ca * cb) % p
    # Reduce mod mod_poly
    return _poly_mod(result, mod_poly, p)


def _poly_mod(a, mod_poly, p):
    """Reduce polynomial a mod (mod_poly, p)."""
    a = list(a)
    d = len(mod_poly) - 1
    lc_inv = pow(mod_poly[-1], -1, p)
    while len(a) >= len(mod_poly):
        if a[-1] != 0:
            coeff = (a[-1] * lc_inv) % p
            offset = len(a) - len(mod_poly)
            for i in range(len(mod_poly)):
                a[offset + i] = (a[offset + i] - coeff * mod_poly[i]) % p
        a.pop()
    # Strip trailing zeros
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a


def _poly_powmod(base, exp, mod_poly, p):
    """Compute base^exp mod (mod_poly, p) using binary exponentiation."""
    result = [1]  # constant 1
    base = _poly_mod(list(base), mod_poly, p)
    while exp > 0:
        if exp & 1:
            result = _poly_mul_mod(result, base, mod_poly, p)
        base = _poly_mul_mod(base, base, mod_poly, p)
        exp >>= 1
    return result


def _poly_gcd(a, b, p):
    """GCD of two polynomials mod p."""
    while len(b) > 1 or (len(b) == 1 and b[0] != 0):
        a, b = b, _poly_mod(a, b, p) if len(b) > 0 and (len(b) > 1 or b[0] != 0) else [0]
        if not b or (len(b) == 1 and b[0] == 0):
            break
    # Make monic
    if len(a) > 0 and a[-1] != 0:
        lc_inv = pow(a[-1], -1, p)
        a = [(c * lc_inv) % p for c in a]
    return a


def _poly_roots_mod_p_smart(coeffs, p):
    """
    Find roots of polynomial mod p.
    For small p (< 10^6), use brute force.
    For larger p, use Cantor-Zassenhaus algorithm.
    """
    if p < 50000:
        return find_poly_roots_mod_p(coeffs, p)

    d = len(coeffs) - 1
    if d <= 0:
        return []

    # Step 1: Compute gcd(x^p - x, f(x)) mod p
    # This gives the product of all linear factors (splitting field)
    # x^p mod f(x) using polynomial exponentiation
    x_poly = [0, 1]  # x
    xp = _poly_powmod(x_poly, p, coeffs, p)
    # x^p - x
    xp_minus_x = list(xp)
    if len(xp_minus_x) < 2:
        xp_minus_x.extend([0] * (2 - len(xp_minus_x)))
    xp_minus_x[1] = (xp_minus_x[1] - 1) % p

    # gcd(x^p - x, f)
    g = _poly_gcd(xp_minus_x, list(coeffs), p)
    num_roots = len(g) - 1
    if num_roots <= 0:
        return []

    # Step 2: Extract roots using Cantor-Zassenhaus
    roots = []
    _cz_split(g, p, roots)
    return sorted(roots[:d])


def _cz_split(f, p, roots):
    """
    Cantor-Zassenhaus: split polynomial f (product of distinct linear factors)
    into its linear factors mod p. Appends roots to the roots list.
    """
    deg = len(f) - 1
    if deg <= 0:
        return
    if deg == 1:
        # f = a1*x + a0, root = -a0/a1
        root = (-f[0] * pow(f[1], -1, p)) % p
        roots.append(root)
        return

    # Try random splits
    import random
    rng = random.Random()
    for _ in range(100):
        # Pick random a, compute gcd(f, (x+a)^((p-1)/2) - 1)
        a = rng.randrange(p)
        t_poly = [a, 1]  # x + a
        # (x+a)^((p-1)/2) mod f
        tp = _poly_powmod(t_poly, (p - 1) // 2, f, p)
        # subtract 1
        tp[0] = (tp[0] - 1) % p

        g = _poly_gcd(list(f), tp, p)
        g_deg = len(g) - 1
        if 0 < g_deg < deg:
            # Split into g and f/g
            _cz_split(g, p, roots)
            # f / g
            h = _poly_div(f, g, p)
            _cz_split(h, p, roots)
            return

    # Fallback: brute force for very small remaining degree
    if deg <= 3:
        for x in range(min(p, 1000000)):
            val = 0
            x_pow = 1
            for c in f:
                val = (val + c * x_pow) % p
                x_pow = (x_pow * x) % p
            if val == 0:
                roots.append(x)
                if len(roots) >= deg:
                    return


def _poly_div(a, b, p):
    """Polynomial division a / b mod p. Returns quotient."""
    a = list(a)
    b_deg = len(b) - 1
    lc_inv = pow(b[-1], -1, p)
    quotient = []
    while len(a) - 1 >= b_deg:
        coeff = (a[-1] * lc_inv) % p
        quotient.append(coeff)
        offset = len(a) - len(b)
        for i in range(len(b)):
            a[offset + i] = (a[offset + i] - coeff * b[i]) % p
        a.pop()
    quotient.reverse()
    return quotient if quotient else [0]


def _find_splitting_prime(f_coeffs, min_p=10000):
    """
    Find a prime q > min_p where f(x) splits completely (has d distinct roots mod q).
    """
    d = len(f_coeffs) - 1
    p = int(next_prime(min_p))
    for _ in range(100000):
        roots = _poly_roots_mod_p_smart(f_coeffs, p)
        if len(roots) == d:
            if len(set(roots)) == d:
                return p, roots
        p = int(next_prime(p))
    return None, None


def _lagrange_interpolation(roots, values, q):
    """
    Lagrange interpolation: find polynomial P(x) of degree < len(roots)
    such that P(roots[j]) = values[j] mod q.

    Returns coefficients [a_0, a_1, ..., a_{d-1}].
    """
    d = len(roots)
    # Start with zero polynomial
    coeffs = [0] * d

    for j in range(d):
        # Compute basis polynomial L_j(x) = Π_{k≠j} (x - r_k) / (r_j - r_k)
        # Denominator
        denom = 1
        for k in range(d):
            if k != j:
                denom = (denom * (roots[j] - roots[k])) % q
        denom_inv = pow(denom, -1, q)
        scale = (values[j] * denom_inv) % q

        # Numerator polynomial: Π_{k≠j} (x - r_k)
        # Build iteratively
        num_coeffs = [1]  # start with constant 1
        for k in range(d):
            if k != j:
                # Multiply by (x - r_k)
                new_coeffs = [0] * (len(num_coeffs) + 1)
                for i, c in enumerate(num_coeffs):
                    new_coeffs[i + 1] = (new_coeffs[i + 1] + c) % q
                    new_coeffs[i] = (new_coeffs[i] - c * roots[k]) % q
                num_coeffs = new_coeffs

        # Add scale * num_coeffs to result
        for i in range(min(d, len(num_coeffs))):
            coeffs[i] = (coeffs[i] + scale * num_coeffs[i]) % q

    return coeffs


def _modular_sqrt(a, p):
    """Compute square root of a mod p using Tonelli-Shanks."""
    a = a % p
    if a == 0:
        return 0
    if pow(a, (p - 1) // 2, p) != 1:
        return None  # not a QR

    if p % 4 == 3:
        return pow(a, (p + 1) // 4, p)

    # Tonelli-Shanks
    s, q = 0, p - 1
    while q % 2 == 0:
        s += 1
        q //= 2

    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1

    M, c, t, R = s, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)

    while True:
        if t == 1:
            return R
        i = 1
        tmp = (t * t) % p
        while tmp != 1:
            tmp = (tmp * tmp) % p
            i += 1
        b = pow(c, 1 << (M - i - 1), p)
        M, c, t, R = i, (b * b) % p, (t * b * b) % p, (R * b) % p


def _poly_mul_mod_zx(a, b, f_coeffs):
    """
    Multiply polynomials a*b in Z[x]/(f(x)) with exact integer arithmetic.
    f must be monic (leading coefficient = 1).
    Returns list of d mpz coefficients [c_0, c_1, ..., c_{d-1}].
    """
    d = len(f_coeffs) - 1
    # Pad inputs to length d, use mpz for fast big-integer arithmetic
    a = [mpz(x) for x in a] + [mpz(0)] * max(0, d - len(a))
    b = [mpz(x) for x in b] + [mpz(0)] * max(0, d - len(b))
    f = [mpz(x) for x in f_coeffs[:d]]

    # Standard polynomial multiplication
    result = [mpz(0)] * (2 * d - 1)
    for i in range(d):
        if a[i] == 0:
            continue
        for j in range(d):
            result[i + j] += a[i] * b[j]

    # Reduce mod f(x) (monic): x^d = -(f_0 + f_1*x + ... + f_{d-1}*x^{d-1})
    for k in range(len(result) - 1, d - 1, -1):
        c = result[k]
        if c == 0:
            continue
        result[k] = mpz(0)
        for i in range(d):
            result[k - d + i] -= c * f[i]

    return result[:d]


def _compute_exact_product(relations, indices, f_coeffs):
    """Compute ∏(a_i + b_i·x) mod f(x) using product tree + mpz arithmetic.
    Handles merged relations (with a_list/b_list) from lattice sieve."""
    d = len(f_coeffs) - 1

    # Collect all linear factors
    factors = []
    for idx in indices:
        rel = relations[idx]
        if 'a_list' in rel:
            for a_val, b_val in zip(rel['a_list'], rel['b_list']):
                factors.append([mpz(a_val), mpz(b_val)] + [mpz(0)] * (d - 2))
        else:
            factors.append([mpz(rel['a']), mpz(rel['b'])] + [mpz(0)] * (d - 2))

    if not factors:
        return [mpz(1)] + [mpz(0)] * (d - 1)

    # Product tree: pairwise multiply to balance coefficient sizes
    while len(factors) > 1:
        new_factors = []
        for i in range(0, len(factors), 2):
            if i + 1 < len(factors):
                new_factors.append(_poly_mul_mod_zx(factors[i], factors[i+1], f_coeffs))
            else:
                new_factors.append(factors[i])
        factors = new_factors

    return factors[0]


def _poly_mul_mod_ring(a, b, f_coeffs, modulus):
    """Multiply polynomials a*b mod (f(x), modulus). f must be monic."""
    d = len(f_coeffs) - 1
    a = [int(x) % modulus for x in a] + [0] * max(0, d - len(a))
    b = [int(x) % modulus for x in b] + [0] * max(0, d - len(b))
    result = [0] * (2 * d - 1)
    for i in range(d):
        if a[i] == 0:
            continue
        for j in range(d):
            result[i + j] = (result[i + j] + a[i] * b[j]) % modulus
    for k in range(len(result) - 1, d - 1, -1):
        c = result[k]
        if c == 0:
            continue
        result[k] = 0
        for i in range(d):
            result[k - d + i] = (result[k - d + i] - c * f_coeffs[i]) % modulus
    return result[:d]


def _poly_pow_mod_ring(base, exp, f_coeffs, modulus):
    """Compute base^exp mod (f(x), modulus)."""
    d = len(f_coeffs) - 1
    result = [1] + [0] * (d - 1)
    base = [int(x) % modulus for x in base] + [0] * max(0, d - len(base))
    while exp > 0:
        if exp & 1:
            result = _poly_mul_mod_ring(result, base, f_coeffs, modulus)
        base = _poly_mul_mod_ring(base, base, f_coeffs, modulus)
        exp >>= 1
    return result


def _find_inert_prime(f_coeffs, min_p=100):
    """Find a prime q where f is IRREDUCIBLE mod q (not just no roots).
    For degree d, check that gcd(x^(q^k) - x, f) = 1 for k = 1, ..., d-1.
    This ensures F_q[x]/(f) is a field of order q^d."""
    d = len(f_coeffs) - 1
    p = int(next_prime(min_p))
    for _ in range(100000):
        # Quick check: no roots (necessary but not sufficient for d > 3)
        roots = find_poly_roots_mod_p(f_coeffs, p)
        if len(roots) > 0:
            p = int(next_prime(p))
            continue

        # Full irreducibility check for d >= 4
        if d <= 3:
            # For d=2,3: no roots ⟹ irreducible
            return p

        # For d >= 4: check x^(p^k) ≡ x mod f for k = 1, ..., d-1
        # f is irreducible iff none of these hold (no factors of degree k)
        is_irred = True
        x_poly = [0, 1] + [0] * (d - 2)
        xpk = _poly_pow_mod_ring(x_poly, p, f_coeffs, p)  # x^p mod (f, p)
        for k in range(1, d):
            # Check: x^(p^k) ≡ x mod (f, p)?
            diff = [(xpk[i] - x_poly[i]) % p for i in range(d)]
            if all(c == 0 for c in diff):
                # f has a factor of degree dividing k
                is_irred = False
                break
            if k < d - 1:
                # Compute x^(p^(k+1)) = (x^(p^k))^p
                xpk = _poly_pow_mod_ring(xpk, p, f_coeffs, p)

        if is_irred:
            return p
        p = int(next_prime(p))
    return None


def _sqrt_in_fqd(P_coeffs, f_coeffs, q):
    """
    Compute sqrt(P) in F_q[x]/(f(x)) where f is irreducible mod q.
    Returns polynomial coefficients or None if not a QR.
    """
    d = len(f_coeffs) - 1
    f_mod = [c % q for c in f_coeffs]
    P_fq = [int(c) % q for c in P_coeffs]
    one = [1] + [0] * (d - 1)

    if all(c == 0 for c in P_fq):
        return [0] * d

    # F_{q^d}^* has order q^d - 1
    order = q ** d - 1

    # Check QR: P^{(q^d-1)/2} should be 1
    check = _poly_pow_mod_ring(P_fq, order // 2, f_mod, q)
    if check != one:
        return None

    # Try simple case: (q^d + 1) divisible by 4
    qd_plus_1 = q ** d + 1
    if qd_plus_1 % 4 == 0:
        return _poly_pow_mod_ring(P_fq, qd_plus_1 // 4, f_mod, q)

    # Tonelli-Shanks for F_{q^d}
    s, t = 0, order
    while t % 2 == 0:
        s += 1
        t //= 2

    # Find a non-residue
    import random
    rng = random.Random(42)
    z = None
    neg_one = [q - 1] + [0] * (d - 1)
    for _ in range(1000):
        z_coeffs = [rng.randrange(q) for _ in range(d)]
        if _poly_pow_mod_ring(z_coeffs, order // 2, f_mod, q) == neg_one:
            z = z_coeffs
            break
    if z is None:
        return None

    M = s
    c = _poly_pow_mod_ring(z, t, f_mod, q)
    tt = _poly_pow_mod_ring(P_fq, t, f_mod, q)
    R = _poly_pow_mod_ring(P_fq, (t + 1) // 2, f_mod, q)

    while True:
        if tt == one:
            return R
        i = 1
        tmp = _poly_mul_mod_ring(tt, tt, f_mod, q)
        while tmp != one:
            tmp = _poly_mul_mod_ring(tmp, tmp, f_mod, q)
            i += 1
        b = c
        for _ in range(M - i - 1):
            b = _poly_mul_mod_ring(b, b, f_mod, q)
        M = i
        c = _poly_mul_mod_ring(b, b, f_mod, q)
        tt = _poly_mul_mod_ring(tt, c, f_mod, q)
        R = _poly_mul_mod_ring(R, b, f_mod, q)


def algebraic_square_root(relations, indices, f_coeffs, m, n, splitting_primes=None):
    """
    Compute algebraic square root using Hensel lifting from an inert prime.

    Algorithm:
    1. Compute P(x) = ∏(a_i + b_i·x) mod f(x) with EXACT integer arithmetic
    2. Find inert prime q (f irreducible mod q, so F_q[x]/(f) is a field)
    3. Compute s_0 = sqrt(P) in F_q[x]/(f) — unique up to sign (±)
    4. Hensel lift: s_{k+1} from s_k using Newton iteration mod q^{2^{k+1}}
    5. When modulus > 2·max|s_i|, balanced reduction gives exact s(x)
    6. Verify s² = P, evaluate s(m) mod n

    Hensel lifting avoids the sign consistency problem of CRT with splitting
    primes — there is only ONE sign choice (±) at the inert prime.
    """
    d = len(f_coeffs) - 1

    # Step 1: Compute exact product P(x) in Z[x]/(f(x))
    P = _compute_exact_product(relations, indices, f_coeffs)
    max_P = max(abs(c) for c in P)
    if max_P == 0:
        return

    # Step 2: Find inert prime
    q = _find_inert_prime(f_coeffs, min_p=100)
    if q is None:
        return

    # Step 3: Compute sqrt in F_q[x]/(f(x))
    s0 = _sqrt_in_fqd(P, f_coeffs, q)
    if s0 is None:
        return

    # Verify initial sqrt: s0² ≡ P mod (f, q)
    s0_check = _poly_mul_mod_ring(s0, s0, f_coeffs, q)
    P_mod_q = [int(c) % q for c in P]
    if s0_check != P_mod_q:
        return

    # Step 4: Hensel lift
    # Newton iteration for sqrt: given s with s² ≡ P mod q^k,
    # compute s' with s'² ≡ P mod q^{2k}:
    #   δ = (P - s²) / q^k   (exact integer division)
    #   inv_2s = (2s)^{-1} mod (f, q^k)
    #   s' = s + δ · inv_2s · q^k mod q^{2k}
    #
    # For the inverse, we lift it alongside:
    #   t₀ = (2·s₀)^{-1} mod (f, q)  (Fermat: (2s)^{q^d-2} in F_{q^d})
    #   t_{k+1} = t_k · (2 - 2·s_k · t_k) mod (f, q^{2^{k+1}})

    # Compute initial inverse of 2·s₀ in F_q[x]/(f(x))
    two_s0 = [(2 * c) % q for c in s0]
    # Inverse via Fermat's little theorem: (2s)^{q^d - 2} mod (f, q)
    inv_2s = _poly_pow_mod_ring(two_s0, q ** d - 2, f_coeffs, q)

    # Current state
    s = [int(c) for c in s0]
    t = [int(c) for c in inv_2s]  # t ≈ (2s)^{-1}
    modulus = q

    _t_hensel = time.time()
    # Bound: sqrt coefficients ≤ max_P, so we need modulus > 2*max_P
    _max_P_bits = int(gmpy2.log2(max_P + 1)) + 1
    _abort_bits = _max_P_bits * 4  # generous: 4x the P coefficient size
    for _hensel_step in range(30):  # q^(2^30) is astronomically large
        new_modulus = modulus * modulus  # quadratic convergence

        # Compute residual: (P - s²) in Z[x]/(f(x)), then divide by modulus
        s2 = _poly_mul_mod_zx(s, s, f_coeffs)
        residual = [(P[i] - s2[i]) for i in range(d)]

        # Check if residual is zero — then s is already exact
        if all(r == 0 for r in residual):
            half = modulus // 2
            s_balanced = [c - modulus if c > half else c for c in s]
            s2_check = _poly_mul_mod_zx(s_balanced, s_balanced, f_coeffs)
            if s2_check == P:
                sm = mpz(0)
                m_pow = mpz(1)
                for c in s_balanced:
                    sm = (sm + mpz(c) * m_pow) % n
                    m_pow = (m_pow * mpz(m)) % n
                if sm != 0:
                    yield sm
                    yield (-sm) % n
                return

        # All residual coefficients should be divisible by modulus
        delta = [r // modulus for r in residual]

        # Correction: δ · t mod (f, modulus)  [t ≈ (2s)^{-1} mod modulus]
        corr = _poly_mul_mod_ring(delta, t, f_coeffs, modulus)

        # Update s: s' = s + corr · modulus
        s = [(s[i] + corr[i] * modulus) % new_modulus for i in range(d)]

        # Update t (inverse of 2s): t' = t · (2 - 2s' · t) mod new_modulus
        two_s = [(2 * s[i]) % new_modulus for i in range(d)]
        two_s_t = _poly_mul_mod_ring(two_s, t, f_coeffs, new_modulus)
        two_minus = [(2 - two_s_t[0]) % new_modulus] + \
                    [(-two_s_t[i]) % new_modulus for i in range(1, d)]
        t = _poly_mul_mod_ring(t, two_minus, f_coeffs, new_modulus)

        modulus = new_modulus

        # Step 5: Balanced reduction and check at each step
        half = modulus // 2
        s_balanced = [c - modulus if c > half else c for c in s]

        s2 = _poly_mul_mod_zx(s_balanced, s_balanced, f_coeffs)
        _mod_bits = int(gmpy2.log2(modulus + 1)) + 1
        if s2 == P:
            sm = mpz(0)
            m_pow = mpz(1)
            for c in s_balanced:
                sm = (sm + mpz(c) * m_pow) % n
                m_pow = (m_pow * mpz(m)) % n
            if sm != 0:
                yield sm
                yield (-sm) % n
            return

        # Abort if modulus far exceeds P coefficient size — P is not a square
        if _mod_bits > _abort_bits:
            break

        # Try negation
        s_neg = [-c for c in s_balanced]
        s2_neg = _poly_mul_mod_zx(s_neg, s_neg, f_coeffs)
        if s2_neg == P:
            sm = mpz(0)
            m_pow = mpz(1)
            for c in s_neg:
                sm = (sm + mpz(c) * m_pow) % n
                m_pow = (m_pow * mpz(m)) % n
            if sm != 0:
                yield sm
                yield (-sm) % n
            return

    # Hensel lifting did not converge after 30 steps — should not happen


###############################################################################
# Phase 5a: CRT-based Algebraic Square Root (splitting primes)
###############################################################################

def algebraic_sqrt_crt(relations, indices, f_coeffs, m, n, max_primes=60):
    """
    Compute algebraic square root using CRT over splitting primes.

    For each splitting prime q where f splits completely:
      1. Evaluate P(r_j) = ∏(a_i + b_i·r_j) mod q for each root r_j of f
      2. sqrt(P(r_j)) mod q via Tonelli-Shanks (2^d sign choices)
      3. Lagrange interpolate → sqrt(P(x)) mod q
    Use CRT across many primes to recover exact sqrt(P(x)) in Z[x]/(f).
    Evaluate at x=m to get algebraic sqrt mod n.

    Yields candidate y values (mod n) for gcd(x ± y, n).
    """
    d = len(f_coeffs) - 1

    # Collect (a, b) pairs from null vector
    ab_pairs = []
    for idx in indices:
        rel = relations[idx]
        if 'a_list' in rel:
            for a_val, b_val in zip(rel['a_list'], rel['b_list']):
                ab_pairs.append((int(a_val), int(b_val)))
        else:
            ab_pairs.append((int(rel['a']), int(rel['b'])))

    if not ab_pairs:
        return

    # Find splitting primes
    splitting = []
    min_p = 1000
    for _ in range(max_primes * 5):
        q, roots = _find_splitting_prime(f_coeffs, min_p=min_p)
        if q is None:
            min_p += 1000
            continue
        if len(roots) == d and len(set(roots)) == d:
            splitting.append((q, roots))
            if len(splitting) >= max_primes:
                break
        min_p = q + 1

    if len(splitting) < 3:
        return

    # For each splitting prime, compute sqrt(P(x)) mod q
    # Try all 2^d sign combinations? No — just try the 2 global signs (±).
    # The key insight: for each root r_j, P(r_j) = ∏(a_i + b_i·r_j).
    # We compute this product mod q, then take sqrt.
    # The sign choice at each root must be CONSISTENT — they all come from
    # the same polynomial sqrt, so Lagrange interpolation enforces consistency.
    # We try both global signs (±) and check via CRT.

    # Accumulate CRT residues for each coefficient of sqrt(P(x))
    # coeffs_mod[k] = list of (residue, modulus) for coefficient k
    crt_moduli = []
    crt_residues = [[] for _ in range(d)]  # one list per coefficient

    for qi, (q, roots) in enumerate(splitting):
        # Evaluate P(r_j) = ∏(a + b*r_j) mod q for each root r_j
        P_at_roots = []
        for r in roots:
            prod = 1
            for a_val, b_val in ab_pairs:
                prod = (prod * (a_val + b_val * r)) % q
            P_at_roots.append(prod)

        # Compute sqrt(P(r_j)) mod q
        sqrt_pos = []
        valid = True
        for val in P_at_roots:
            s = _modular_sqrt(val, q)
            if s is None:
                valid = False
                break
            sqrt_pos.append(s)

        if not valid:
            continue

        # For first prime: try all 2^d sign combinations
        # For subsequent primes: use sign that's consistent with first
        if not crt_moduli:
            # First prime: store all 2^d possible interpolations
            first_prime_options = []
            for signs in range(1 << d):
                sqrt_at_roots = []
                for j in range(d):
                    if signs & (1 << j):
                        sqrt_at_roots.append(q - sqrt_pos[j])
                    else:
                        sqrt_at_roots.append(sqrt_pos[j])
                S = _lagrange_interpolation(roots, sqrt_at_roots, q)
                first_prime_options.append(S)
            # We'll try each option independently
            crt_moduli.append(q)
            for k in range(d):
                crt_residues[k].append([opt[k] for opt in first_prime_options])
        else:
            # Subsequent primes: just use positive sqrt
            S_coeffs = _lagrange_interpolation(roots, sqrt_pos, q)
            crt_moduli.append(q)
            for k in range(d):
                crt_residues[k].append(S_coeffs[k] if k < len(S_coeffs) else 0)

    if len(crt_moduli) < 3:
        return

    # CRT to get exact coefficients (or mod big product)
    # We evaluate s(m) mod n directly using mixed-radix CRT to avoid huge integers
    # s(m) mod n = sum_k (coeff_k * m^k) mod n
    # Each coeff_k is determined by CRT from its residues

    # Compute product of all moduli
    M_prod = mpz(1)
    for q in crt_moduli:
        M_prod *= q

    # For each coefficient, solve CRT
    s_at_m = mpz(0)
    m_pow = mpz(1)
    for k in range(d):
        # CRT for coefficient k
        ck = mpz(0)
        for i, q in enumerate(crt_moduli):
            Mi = M_prod // q
            Mi_inv = pow(int(Mi % q), -1, q)
            ck = (ck + mpz(crt_residues[k][i]) * Mi * mpz(Mi_inv)) % M_prod

        # Balanced reduction
        half = M_prod // 2
        if ck > half:
            ck -= M_prod

        s_at_m = (s_at_m + ck * m_pow) % n
        m_pow = (m_pow * mpz(m)) % n

    if s_at_m != 0:
        yield s_at_m
        yield (-s_at_m) % n


###############################################################################
# Phase 5b: Factor Extraction
###############################################################################

def extract_factor(n, null_vecs, relations, m, rat_fb, alg_fb, f_coeffs):
    """
    For each null space vector, compute x² ≡ y² (mod n) and extract gcd.

    GNFS congruence of squares:
      - Rational side: Π(a_i + b_i·m) = (-1)^s · Π p_j^{e_j}, all e_j even
        → rational sqrt x = (-1)^(s/2) · Π p_j^{e_j/2}
      - Algebraic side: Π(a_i + b_i·α) = s(α)² in Z[α]/(f(α))
        → algebraic sqrt y = s(m) mod n via Couveignes' algorithm
      - Factor from gcd(x ± y, n)
    """
    d = len(f_coeffs) - 1
    nb = int(gmpy2.log2(n)) + 1

    # Precompute splitting primes (only once for all null vecs)
    num_sp = nb // 17 + 5
    splitting_primes = []
    min_p = 100000
    for _ in range(num_sp * 3):
        q, roots = _find_splitting_prime(f_coeffs, min_p=min_p)
        if q is not None:
            splitting_primes.append((q, roots))
            min_p = q + 1
        else:
            min_p += 1000
        if len(splitting_primes) >= num_sp:
            break

    if len(splitting_primes) < 3:
        return None

    # Limit: try at most 50 null vecs (most should work with QC columns)
    max_tries = min(50, len(null_vecs))

    for vi, indices in enumerate(null_vecs[:max_tries]):
        t_vec = time.time()
        # Accumulate exponents
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

        # Rational square root: x = (-1)^(s/2) · Π p_j^{e_j/2} · Π LP_k^{e_k/2} mod n
        x_val = mpz(1)
        for j, e in enumerate(total_rat):
            if e > 0:
                x_val = (x_val * pow(mpz(rat_fb[j]), e // 2, n)) % n
        # Include rational large primes (SLP combined: exponent 2, DLP individual: exponent 1)
        rat_lp_exps = defaultdict(int)
        for idx in indices:
            rel = relations[idx]
            rat_lp = rel.get('rat_lp', 0)
            if rat_lp > 0:
                # SLP combined relations contribute LP with exponent 2
                # DLP individual relations contribute LP with exponent 1
                if 'a_list' in rel:
                    rat_lp_exps[rat_lp] += 2
                else:
                    rat_lp_exps[rat_lp] += 1
        lp_ok = True
        for lp, exp in rat_lp_exps.items():
            if exp % 2 != 0:
                lp_ok = False
                break
            x_val = (x_val * pow(mpz(lp), exp // 2, n)) % n
        if not lp_ok:
            continue
        if (total_sign // 2) % 2 == 1:
            x_val = (-x_val) % n

        # Algebraic square root: direct product mod n approach
        # y² = ∏(a_i + b_i·m) mod n. Compute y via FB prime exponents.
        # Since all alg exponents are even, y = ∏ alg_fb_prime^(e/2) mod n.
        y_val = mpz(1)
        # Try Hensel-based algebraic sqrt first (works for d=3)
        for y_h in algebraic_square_root(
                relations, indices, f_coeffs, m, n, splitting_primes):
            for diff in [x_val - y_h, x_val + y_h]:
                g = gcd(diff % n, n)
                if 1 < g < n:
                    return int(g)

        # Fallback: direct product evaluation mod n
        # y = ∏(a_i + b_i·m) mod n, then y should be x² mod n
        y_direct = mpz(1)
        for idx in indices:
            rel = relations[idx]
            if 'a_list' in rel:
                for a_val, b_val in zip(rel['a_list'], rel['b_list']):
                    y_direct = (y_direct * (mpz(a_val) + mpz(b_val) * mpz(m))) % n
            else:
                y_direct = (y_direct * (mpz(rel['a']) + mpz(rel['b']) * mpz(m))) % n

        # y_direct = ∏(a_i + b_i·m) mod n should equal x_val² mod n
        # But actually x_val is the RATIONAL sqrt, y_direct is the full product
        # We need: x_rational² ≡ y_algebraic² (mod n)
        # So try gcd(x_val² - y_direct, n) — if y_direct is a perfect square,
        # this factors. But y_direct is NOT a perfect square in general.
        # Skip this — the Hensel approach is the correct one.

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
    rat_fb = build_rational_fb(params['B_r'])
    alg_fb = build_algebraic_fb(f_coeffs, params['B_a'])
    fb_time = time.time() - t_fb

    if verbose:
        print(f"    Rational FB: {len(rat_fb)} primes up to {rat_fb[-1] if rat_fb else 0}")
        print(f"    Algebraic FB: {len(alg_fb)} ideals ({fb_time:.1f}s)")

    # Quadratic character primes (ensure algebraic product is a true square)
    num_split_qc = 20
    qc_primes = build_qc_primes(f_coeffs, num_qc=num_split_qc, min_p=50000)
    # Inert QC primes — additional characters at primes where f is irreducible
    num_inert_qc = 5
    inert_qc_primes = build_inert_qc_primes(f_coeffs, num_qc=num_inert_qc, min_p=100)
    num_qc = num_split_qc + num_inert_qc

    # Extra 10% buffer: SGE removes rows/cols unevenly, need excess for null space
    needed = int((len(rat_fb) + len(alg_fb) + num_qc + 2) * 1.10)
    if verbose:
        print(f"    Need {needed} relations (incl. {num_qc} QC columns: "
              f"{num_split_qc} split + {num_inert_qc} inert)")

    # Step 4: Sieve — lattice sieve for 35d+, line sieve for smaller
    t_sieve = time.time()
    num_sq = 0

    # Use lattice sieve for 50d+ when C sieve available, 80d+ for Python fallback
    # Below 50d, line sieve + SLP/DLP is faster due to higher smoothness probability
    _c_lattice_available = _load_lattice_sieve() is not None
    _lattice_threshold = 50 if _c_lattice_available else 80
    if nd >= _lattice_threshold:
        # Lattice sieve with special-q
        if verbose:
            print(f"    Using lattice sieve (special-q)")
        # Overshoot collection to account for singleton removal
        raw_relations, sq_map = lattice_sieve_collect(
            n, f_coeffs, m, rat_fb, alg_fb, qc_primes, params,
            needed * 3, verbose=verbose, time_limit=time_limit, t0=t0,
            inert_qc_primes=inert_qc_primes)
        # Merge relations from same special-q, eliminating SQ columns
        verified_relations, n_singleton = merge_sq_relations(raw_relations)
        num_sq = 0  # No SQ columns after merging
        if verbose:
            print(f"    Merged: {len(raw_relations)} raw → {len(verified_relations)} "
                  f"merged ({n_singleton} singletons discarded)")
    else:
        # Line sieve for small numbers
        verified_relations = []
        A = min(params['A'], 500000)

        # Reset cached JIT arrays
        trial_divide_rational._primes = np.array(rat_fb, dtype=np.int64)
        trial_divide_algebraic._primes = np.array([p for p, r in alg_fb], dtype=np.int64)
        trial_divide_algebraic._roots = np.array([r for p, r in alg_fb], dtype=np.int64)
        norm_algebraic._coeffs = np.array(f_coeffs, dtype=np.int64)
        if hasattr(sieve_line, '_rat_primes'):
            del sieve_line._rat_primes
        if hasattr(sieve_line, '_alg_primes'):
            del sieve_line._alg_primes

        rat_bound = A * abs(m) + 1
        alg_bound = int(norm_algebraic(A, 1, f_coeffs))

        # Try C sieve for bulk candidate generation
        c_lib = _load_gnfs_sieve()
        if c_lib is not None:
            # C sieve path: batch sieve, then trial divide candidates
            rat_p_arr = np.array(rat_fb, dtype=np.int64)
            alg_p_arr = np.array([p for p, r in alg_fb], dtype=np.int64)
            alg_r_arr = np.array([r for p, r in alg_fb], dtype=np.int64)

            d = len(f_coeffs) - 1
            f0_abs = abs(f_coeffs[0]) if f_coeffs[0] != 0 else 1
            fd_abs = abs(f_coeffs[d]) if f_coeffs[d] != 0 else 1

            # Cap max_cands to fit verify buffers in ~800MB (leave room for other data)
            n_fb_total = len(rat_fb) + len(alg_fb)
            mem_per_cand = n_fb_total * 8  # bytes for exponent arrays
            max_cands_verify = max(2000, min(50000, int(800_000_000 / max(mem_per_cand, 1))))
            # Sieve buffer can be larger since it's just int pairs
            max_cands_sieve = max(max_cands_verify, 200000)
            max_cands = max_cands_sieve
            out_a = (ctypes.c_int * max_cands)()
            out_b = (ctypes.c_int * max_cands)()

            B_max = params['B_max']
            # Larger batch for efficiency: more b-lines per C sieve call
            batch_size = min(1000, max(100, B_max // 100))
            f_coeffs_arr = np.array(f_coeffs, dtype=np.int64)

            # Compute max safe b for int64 batch JIT (avoid overflow in norm)
            # Algebraic norm ≈ sum_i f_i * (-a)^i * b^(d-i)
            # Dominant overflow term: max(|f_i|) * max(A,b)^d
            # For fixed A, the b-dependent bound comes from f_0 * b^d < 2^63
            int64_max = (1 << 63) - 1
            # Also check rational: |a + b*m| < 2^63 → b < 2^63 / |m|
            safe_b_rat = int64_max // (abs(int(m)) + 1) if m != 0 else B_max
            # Algebraic: sum of |f_i * A^i * b^(d-i)| < 2^63
            # Approximate: (d+1) * max(|f_i| * A^i) * b^(d-?) is complex
            # Simple safe bound: max(|f_i|) * max(A, b)^d < 2^63 / (d+1)
            max_f = max(abs(c) for c in f_coeffs)
            if max_f > 0 and d > 0:
                safe_b_alg = int((int64_max / ((d + 1) * max_f)) ** (1.0 / d))
            else:
                safe_b_alg = B_max
            max_safe_b = max(min(safe_b_rat, safe_b_alg), 1)

            lp_bound = np.int64(min(params['B_r'] * 100, params['B_r'] ** 2))  # LP bound: 100*B for SLP combining

            # C verify buffers (flattened, sized to max_cands_verify)
            c_verify_rat_exps = np.zeros(max_cands_verify * len(rat_fb), dtype=np.int64)
            c_verify_alg_exps = np.zeros(max_cands_verify * len(alg_fb), dtype=np.int64)
            c_verify_signs = (ctypes.c_int * max_cands_verify)()
            c_verify_mask = (ctypes.c_int * max_cands_verify)()
            c_verify_rat_lp = np.zeros(max_cands_verify, dtype=np.int64)
            c_verify_alg_lp = np.zeros(max_cands_verify, dtype=np.int64)

            # JIT buffers only if needed (2D views for numba)
            batch_rat_exps = c_verify_rat_exps.reshape(max_cands_verify, len(rat_fb))
            batch_alg_exps = c_verify_alg_exps.reshape(max_cands_verify, len(alg_fb))
            batch_signs = np.zeros(max_cands_verify, dtype=np.int64)
            batch_mask = np.zeros(max_cands_verify, dtype=np.int64)
            batch_rat_lp = c_verify_rat_lp
            batch_alg_lp = c_verify_alg_lp

            # SLP partial relations grouped by large prime
            partials_rat = defaultdict(list)  # rat_lp → list of relation dicts
            partials_alg = defaultdict(list)  # alg_lp → list of relation dicts
            partials_dlp = []  # DLP: both sides have LP
            total_partials = 0
            max_partials = 200000  # SLP/DLP: partial relations limit

            # QC arrays (precompute once)
            qc_q_arr = np.array([q for q, r in qc_primes], dtype=np.int64)
            qc_r_arr = np.array([r for q, r in qc_primes], dtype=np.int64)
            n_split_qc = len(qc_primes)
            batch_qc = np.zeros((max_cands_verify, n_split_qc), dtype=np.int64)

            # If JIT covers < 10% of b-range, use C verify for everything
            use_c_verify_only = (max_safe_b < B_max * 0.1)
            if use_c_verify_only:
                max_safe_b = 0  # force all to C verify path

            if verbose and max_safe_b < B_max:
                if use_c_verify_only:
                    print(f"    Using C __int128 verify for all b (int64 overflow at b>{max_safe_b})")
                else:
                    print(f"    Batch JIT safe for b≤{max_safe_b}, C verify for b>{max_safe_b}")

            # Two-phase sieve: large A for small b (norms manageable), normal A for rest
            # Phase 1: b=1..phase1_b_max, A_large, batch_size=1 (avoid max_cands overflow)
            # Phase 2: b=phase1_b_max+1..B_max, A, batch_size=500
            if d >= 4 and nd >= 40:
                A_large = min(A * 2, 2_000_000)  # 2x wider for small b
                phase1_b_max = min(5000, B_max)
                phase1_batch = 1  # one b-line at a time to avoid buffer overflow
            else:
                A_large = A
                phase1_b_max = 0  # no phase 1 for small/low-degree numbers
                phase1_batch = batch_size

            if verbose and phase1_b_max > 0:
                print(f"    Two-phase sieve: b=1..{phase1_b_max} A={A_large}, "
                      f"b={phase1_b_max+1}..{B_max} A={A}")

            # Build phase schedule: [(b_start, b_end, A_use), ...]
            phase_schedule = []
            if phase1_b_max > 0:
                for b in range(1, phase1_b_max + 1):
                    phase_schedule.append((b, b, A_large, phase1_batch))
            for b_s in range(phase1_b_max + 1, B_max + 1, batch_size):
                b_e = min(b_s + batch_size - 1, B_max)
                phase_schedule.append((b_s, b_e, A, batch_size))

            for b_start, b_end, A_use, _ in phase_schedule:
                if time.time() - t0 > time_limit:
                    break

                n_cands = c_lib.sieve_batch_c(
                    b_start, b_end, A_use,
                    rat_p_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                    len(rat_fb), ctypes.c_int64(int(m)),
                    alg_p_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                    alg_r_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                    len(alg_fb),
                    max(700, 1100 - nd * 5), max(600, 1000 - nd * 5),
                    d, ctypes.c_int64(f0_abs), ctypes.c_int64(fd_abs),
                    out_a, out_b, max_cands)

                if n_cands == 0:
                    continue

                def _process_batch_jit(a_np, b_np, n_c):
                    """Process candidates via batch JIT."""
                    nonlocal total_partials
                    batch_mask[:n_c] = 0
                    batch_rat_lp[:n_c] = 0
                    batch_alg_lp[:n_c] = 0

                    _jit_batch_verify(a_np, b_np, n_c, np.int64(int(m)),
                                      f_coeffs_arr, np.int64(d),
                                      rat_p_arr, alg_p_arr, alg_r_arr,
                                      batch_rat_exps, batch_alg_exps,
                                      batch_signs, batch_mask,
                                      batch_rat_lp, batch_alg_lp, lp_bound)

                    batch_qc[:n_c] = 0
                    _jit_compute_qc_batch(a_np, b_np, batch_mask, n_c,
                                           qc_q_arr, qc_r_arr, n_split_qc, batch_qc)

                    have_enough_full = len(verified_relations) >= needed
                    for ci in range(n_c):
                        if batch_mask[ci] == 0:
                            continue
                        a_val = int(a_np[ci])
                        b_val = int(b_np[ci])
                        mtype = int(batch_mask[ci])
                        if mtype == 1:
                            # Full relation: compute all QC
                            qc_bits = batch_qc[ci, :n_split_qc].tolist()
                            if inert_qc_primes:
                                qc_bits += compute_inert_qc_vector(
                                    a_val, b_val, inert_qc_primes, f_coeffs)
                            verified_relations.append({
                                'a': a_val, 'b': b_val,
                                'rat_exps': batch_rat_exps[ci].tolist(),
                                'rat_sign': int(batch_signs[ci]),
                                'alg_exps': batch_alg_exps[ci].tolist(),
                                'qc_bits': qc_bits,
                            })
                        elif not have_enough_full and total_partials < max_partials:
                            # Partial: compact storage (int8 exps to save memory)
                            qc_bits = batch_qc[ci, :n_split_qc].tolist()
                            rel = {
                                'a': a_val, 'b': b_val,
                                'rat_exps': batch_rat_exps[ci].astype(np.int8).copy(),
                                'rat_sign': int(batch_signs[ci]),
                                'alg_exps': batch_alg_exps[ci].astype(np.int8).copy(),
                                'qc_bits': qc_bits,
                                '_needs_inert_qc': True,
                            }
                            if mtype == 3:
                                # Group by ideal (p, r) not just p
                                alp = int(batch_alg_lp[ci])
                                r_ideal = (-a_val * pow(b_val, -1, alp)) % alp
                                partials_alg[(alp, r_ideal)].append(rel)
                            elif mtype == 2:
                                partials_rat[int(batch_rat_lp[ci])].append(rel)
                            elif mtype == 4:
                                # DLP: both sides have LP
                                rel['rat_lp'] = int(batch_rat_lp[ci])
                                rel['alg_lp'] = int(batch_alg_lp[ci])
                                partials_dlp.append(rel)
                            total_partials += 1

                a_np_full = np.array(out_a[:n_cands], dtype=np.int64)
                b_np_full = np.array(out_b[:n_cands], dtype=np.int64)

                # Process in chunks of max_cands_verify to stay within memory
                for chunk_start in range(0, n_cands, max_cands_verify):
                    chunk_end = min(chunk_start + max_cands_verify, n_cands)
                    chunk_n = chunk_end - chunk_start
                    a_np = a_np_full[chunk_start:chunk_end]
                    b_np = b_np_full[chunk_start:chunk_end]

                    if b_end <= max_safe_b and A_use == A:
                        _process_batch_jit(a_np, b_np, chunk_n)
                    else:
                        # C __int128 verify path for large b values
                        # Need ctypes arrays for the chunk
                        chunk_out_a = (ctypes.c_int * chunk_n)(*[out_a[chunk_start + i] for i in range(chunk_n)])
                        chunk_out_b = (ctypes.c_int * chunk_n)(*[out_b[chunk_start + i] for i in range(chunk_n)])

                        c_lib.verify_candidates_c(
                            chunk_out_a, chunk_out_b, chunk_n,
                            ctypes.c_int64(int(m)),
                            f_coeffs_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                            d,
                            rat_p_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                            len(rat_fb),
                            alg_p_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                            alg_r_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                            len(alg_fb),
                            ctypes.c_int64(int(lp_bound)),
                            c_verify_rat_exps.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                            c_verify_alg_exps.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                            c_verify_signs, c_verify_mask,
                            c_verify_rat_lp.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                            c_verify_alg_lp.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                        )

                        have_enough_full = len(verified_relations) >= needed
                        for ci in range(chunk_n):
                            mtype = c_verify_mask[ci]
                            if mtype == 0:
                                continue
                            a_val = int(a_np[ci])
                            b_val = int(b_np[ci])
                            # Read from 2D view (same memory as flattened)
                            rat_exps = batch_rat_exps[ci].tolist()
                            alg_exps = batch_alg_exps[ci].tolist()
                            rat_sign = int(c_verify_signs[ci])

                            if mtype == 1:
                                # Full relation
                                qc_bits = compute_qc_vector(a_val, b_val, qc_primes)
                                if inert_qc_primes:
                                    qc_bits += compute_inert_qc_vector(
                                        a_val, b_val, inert_qc_primes, f_coeffs)
                                verified_relations.append({
                                    'a': a_val, 'b': b_val,
                                    'rat_exps': rat_exps, 'rat_sign': rat_sign,
                                    'alg_exps': alg_exps,
                                    'qc_bits': qc_bits,
                                })
                            elif not have_enough_full and total_partials < max_partials:
                                # Partial relation (SLP) — compact int8 exps
                                qc_bits = compute_qc_vector(a_val, b_val, qc_primes)
                                rel = {
                                    'a': a_val, 'b': b_val,
                                    'rat_exps': batch_rat_exps[ci].astype(np.int8).copy(),
                                    'rat_sign': rat_sign,
                                    'alg_exps': batch_alg_exps[ci].astype(np.int8).copy(),
                                    'qc_bits': qc_bits,
                                    '_needs_inert_qc': True,
                                }
                                if mtype == 3:
                                    alp = int(c_verify_alg_lp[ci])
                                    r_ideal = (-a_val * pow(b_val, -1, alp)) % alp
                                    partials_alg[(alp, r_ideal)].append(rel)
                                elif mtype == 2:
                                    partials_rat[int(c_verify_rat_lp[ci])].append(rel)
                                elif mtype == 4:
                                    rel['rat_lp'] = int(c_verify_rat_lp[ci])
                                    rel['alg_lp'] = int(c_verify_alg_lp[ci])
                                    partials_dlp.append(rel)
                                total_partials += 1

                # Estimate total with SLP + DLP matching
                n_slp_est = sum(max(0, len(v) - 1) for v in partials_alg.values())
                n_slp_est += sum(max(0, len(v) - 1) for v in partials_rat.values())
                # DLP estimate: conservative (actual usable is much less than total)
                n_dlp_est = 0
                total_est = len(verified_relations) + n_slp_est + n_dlp_est

                if verbose and (b_end % 500 == 0 or (b_end <= phase1_b_max and b_end % 100 == 0)):
                    elapsed = time.time() - t0
                    n_part = sum(len(v) for v in partials_alg.values()) + sum(len(v) for v in partials_rat.values())
                    print(f"    [b={b_end}] {len(verified_relations)}+{n_slp_est}slp+{n_dlp_est}dlp/{needed} ({n_part} slp-part, {len(partials_dlp)} dlp-part, {elapsed:.1f}s)")
                if total_est >= needed:
                    break
        else:
            # Python fallback sieve
            for b in range(1, params['B_max'] + 1):
                if time.time() - t0 > time_limit:
                    break
                pairs = sieve_line(b, A, m, f_coeffs, rat_fb, alg_fb,
                                  rat_bound, alg_bound)
                for a, b_val in pairs:
                    rat_result = trial_divide_rational(a, b_val, m, rat_fb)
                    if rat_result is None:
                        continue
                    rat_exps, rat_sign = rat_result
                    alg_exps = trial_divide_algebraic(a, b_val, f_coeffs, alg_fb)
                    if alg_exps is None:
                        continue
                    qc_bits = compute_qc_vector(a, b_val, qc_primes)
                    if inert_qc_primes:
                        qc_bits += compute_inert_qc_vector(
                            a, b_val, inert_qc_primes, f_coeffs)
                    verified_relations.append({
                        'a': a, 'b': b_val,
                        'rat_exps': rat_exps, 'rat_sign': rat_sign,
                        'alg_exps': alg_exps,
                        'qc_bits': qc_bits,
                    })
                if verbose and b % 100 == 0:
                    elapsed = time.time() - t0
                    print(f"    [b={b}] {len(verified_relations)}/{needed} verified ({elapsed:.1f}s)")
                if len(verified_relations) >= needed:
                    break

    # Helper: compute deferred inert QC bits
    def _ensure_inert_qc(rel):
        if rel.get('_needs_inert_qc') and inert_qc_primes:
            rel['qc_bits'] = rel['qc_bits'] + compute_inert_qc_vector(
                rel['a'], rel['b'], inert_qc_primes, f_coeffs)
            rel['_needs_inert_qc'] = False

    # SLP matching: combine partial relations sharing a large prime
    n_full_before = len(verified_relations)
    if 'partials_alg' in dir() and len(verified_relations) < needed:
        def _combine_partials(partials_dict, lp_side):
            """lp_side: 'rat' or 'alg' — which side has the large prime."""
            for lp, rels in partials_dict.items():
                if len(rels) < 2:
                    continue
                _ensure_inert_qc(rels[0])
                base = rels[0]
                nrat = len(base['rat_exps'])
                nalg = len(base['alg_exps'])
                nqc = len(base.get('qc_bits', []))
                for other in rels[1:]:
                    _ensure_inert_qc(other)
                    # Handle both numpy arrays and lists for exponents
                    br, or_ = base['rat_exps'], other['rat_exps']
                    ba, oa = base['alg_exps'], other['alg_exps']
                    if isinstance(br, np.ndarray):
                        comb_rat = (br.astype(np.int16) + or_.astype(np.int16)).tolist()
                    else:
                        comb_rat = [br[j] + or_[j] for j in range(nrat)]
                    if isinstance(ba, np.ndarray):
                        comb_alg = (ba.astype(np.int16) + oa.astype(np.int16)).tolist()
                    else:
                        comb_alg = [ba[j] + oa[j] for j in range(nalg)]
                    verified_relations.append({
                        'a': base['a'], 'b': base['b'],
                        'a_list': [base['a'], other['a']],
                        'b_list': [base['b'], other['b']],
                        'rat_exps': comb_rat,
                        'rat_sign': base['rat_sign'] + other['rat_sign'],
                        'alg_exps': comb_alg,
                        'qc_bits': [base['qc_bits'][j] ^ other['qc_bits'][j] for j in range(nqc)] if nqc > 0 else [],
                        'rat_lp': lp if lp_side == 'rat' else 0,
                        'alg_lp': lp if lp_side == 'alg' else 0,
                    })
                    if len(verified_relations) >= needed:
                        return

        _combine_partials(partials_alg, 'alg')
        if len(verified_relations) < needed:
            _combine_partials(partials_rat, 'rat')

        n_slp = len(verified_relations) - n_full_before
        n_part_alg = sum(len(v) for v in partials_alg.values())
        n_part_rat = sum(len(v) for v in partials_rat.values())
        if verbose and (n_part_alg + n_part_rat) > 0:
            print(f"    SLP: {n_part_alg} alg-partial + {n_part_rat} rat-partial → {n_slp} combined")

    # DLP processing: add individual DLP relations with LP columns
    num_lp_cols = 0
    if 'partials_dlp' in dir() and partials_dlp and len(verified_relations) < needed:
        from collections import Counter
        # Compute alg ideals for all DLP rels
        for rel in partials_dlp:
            _ensure_inert_qc(rel)
            alp = rel['alg_lp']
            rel['_alg_ideal'] = (alp, (-rel['a'] * pow(rel['b'], -1, alp)) % alp)

        # Count LP occurrences — only keep LPs appearing 2+ times
        rlp_cnt = Counter(r['rat_lp'] for r in partials_dlp)
        alp_cnt = Counter(r['_alg_ideal'] for r in partials_dlp)

        # Filter: keep DLP rels where BOTH LPs appear 2+ times
        useful_dlp = [r for r in partials_dlp
                      if rlp_cnt[r['rat_lp']] >= 2 and alp_cnt[r['_alg_ideal']] >= 2]

        if useful_dlp:
            # Assign LP column indices
            unique_rlps = sorted(set(r['rat_lp'] for r in useful_dlp))
            unique_alps = sorted(set(r['_alg_ideal'] for r in useful_dlp))
            rlp_to_col = {lp: i for i, lp in enumerate(unique_rlps)}
            alp_to_col = {ideal: i + len(unique_rlps) for i, ideal in enumerate(unique_alps)}
            num_lp_cols = len(unique_rlps) + len(unique_alps)

            for rel in useful_dlp:
                # Convert int16 exps to lists for consistency
                if isinstance(rel['rat_exps'], np.ndarray):
                    rel['rat_exps'] = rel['rat_exps'].tolist()
                if isinstance(rel['alg_exps'], np.ndarray):
                    rel['alg_exps'] = rel['alg_exps'].tolist()
                rel['lp_cols'] = [rlp_to_col[rel['rat_lp']],
                                  alp_to_col[rel['_alg_ideal']]]
                verified_relations.append(rel)

            # Update needed: more columns now
            needed = int((1 + len(rat_fb) + len(alg_fb) + num_qc + num_sq + num_lp_cols + 1) * 1.10)

            if verbose:
                print(f"    DLP: {len(useful_dlp)}/{len(partials_dlp)} usable → "
                      f"{len(unique_rlps)} rat-LP + {len(unique_alps)} alg-LP cols")

    sieve_time = time.time() - t_sieve
    if verbose:
        print(f"    Sieve+verify: {len(verified_relations)}/{needed} in {sieve_time:.1f}s")

    if len(verified_relations) < needed:
        if verbose:
            print(f"    Insufficient relations ({len(verified_relations)}/{needed})")
        return None

    # Step 5: GF(2) Linear Algebra
    la_t0 = time.time()
    ncols_total = 1 + len(rat_fb) + len(alg_fb) + num_qc + num_sq + num_lp_cols
    if verbose:
        print(f"    LA: {len(verified_relations)} x {ncols_total}")

    null_vecs = gf2_gaussian_elimination(
        verified_relations, len(rat_fb), len(alg_fb), num_qc=num_qc,
        num_sq=num_sq, num_lp=num_lp_cols, verbose=verbose)

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
    result = extract_factor(n, null_vecs, verified_relations, m, rat_fb, alg_fb, f_coeffs)

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
