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


###############################################################################
# Phase 4: GF(2) Linear Algebra (Gaussian Elimination)
###############################################################################

def gf2_gaussian_elimination(relations, ncols_rat, ncols_alg, num_qc=0):
    """
    Build GF(2) matrix from relations and find null space vectors.

    Each relation has:
      - rational exponent vector (sign + exps_rat)
      - algebraic exponent vector (exps_alg)
      - quadratic character vector (qc_bits) — ensures algebraic square

    Matrix columns = 1 (sign) + ncols_rat + ncols_alg + num_qc.
    """
    nrows = len(relations)
    ncols = 1 + ncols_rat + ncols_alg + num_qc

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
        # Quadratic characters
        qc_bits = rel.get('qc_bits', [])
        for j, bit in enumerate(qc_bits):
            if bit:
                row |= (1 << (j + 1 + ncols_rat + ncols_alg))
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
    if p < 1000000:
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
    Returns list of d coefficients [c_0, c_1, ..., c_{d-1}].
    """
    d = len(f_coeffs) - 1
    # Pad inputs to length d
    a = list(a) + [0] * max(0, d - len(a))
    b = list(b) + [0] * max(0, d - len(b))

    # Standard polynomial multiplication
    result = [0] * (2 * d - 1)
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
        result[k] = 0
        for i in range(d):
            result[k - d + i] -= c * f_coeffs[i]

    return result[:d]


def _compute_exact_product(relations, indices, f_coeffs):
    """Compute ∏(a_i + b_i·x) mod f(x) with exact integer arithmetic."""
    d = len(f_coeffs) - 1
    product = [1] + [0] * (d - 1)  # constant 1

    for idx in indices:
        rel = relations[idx]
        a_val, b_val = rel['a'], rel['b']
        linear = [a_val, b_val] + [0] * (d - 2)  # a + b*x
        product = _poly_mul_mod_zx(product, linear, f_coeffs)

    return product


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
    """Find a prime q where f has no roots mod q (irreducible for degree 3)."""
    p = int(next_prime(min_p))
    for _ in range(100000):
        roots = find_poly_roots_mod_p(f_coeffs, p)
        if len(roots) == 0:
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

    # Coefficient bound for sqrt
    f_norm = max(abs(c) for c in f_coeffs) + 1
    coeff_bound = int(isqrt(mpz(max_P))) * f_norm ** d + 1
    target = mpz(2) * mpz(coeff_bound) + 1

    # Step 2: Find inert prime
    q = _find_inert_prime(f_coeffs, min_p=100)
    if q is None:
        return

    # Step 3: Compute sqrt in F_q[x]/(f(x))
    s0 = _sqrt_in_fqd(P, f_coeffs, q)
    if s0 is None:
        # P not a QR in this field — product is not a perfect square
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

    while modulus < target:
        new_modulus = modulus * modulus  # quadratic convergence

        # Compute residual: (P - s²) in Z[x]/(f(x)), then divide by modulus
        s2 = _poly_mul_mod_zx(s, s, f_coeffs)
        residual = [(P[i] - s2[i]) for i in range(d)]

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

    # Step 5: Balanced reduction
    half = modulus // 2
    s_balanced = [c - modulus if c > half else c for c in s]

    # Verify: s² = P exactly
    s2 = _poly_mul_mod_zx(s_balanced, s_balanced, f_coeffs)
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

    # Try negation (the other sign)
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

        # Rational square root: x = (-1)^(s/2) · Π p_j^{e_j/2} mod n
        x_val = mpz(1)
        for j, e in enumerate(total_rat):
            if e > 0:
                x_val = (x_val * pow(mpz(rat_fb[j]), e // 2, n)) % n
        if (total_sign // 2) % 2 == 1:
            x_val = (-x_val) % n

        # Algebraic square root via Couveignes: try all sign combinations
        for y_val in algebraic_square_root(
                relations, indices, f_coeffs, m, n, splitting_primes):
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

    # Quadratic character primes (ensure algebraic product is a true square)
    num_qc = 20
    qc_primes = build_qc_primes(f_coeffs, num_qc=num_qc, min_p=50000)

    needed = len(rat_fb) + len(alg_fb) + num_qc + 10
    if verbose:
        print(f"    Need {needed} relations (incl. {num_qc} QC columns)")

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

            # Both sides smooth — compute QC bits and store
            qc_bits = compute_qc_vector(a, b_val, qc_primes)
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

    sieve_time = time.time() - t_sieve
    if verbose:
        print(f"    Sieve+verify: {len(verified_relations)}/{needed} in {sieve_time:.1f}s")

    if len(verified_relations) < needed:
        if verbose:
            print(f"    Insufficient relations ({len(verified_relations)}/{needed})")
        return None

    # Step 5: GF(2) Linear Algebra
    la_t0 = time.time()
    ncols_total = 1 + len(rat_fb) + len(alg_fb) + num_qc
    if verbose:
        print(f"    LA: {len(verified_relations)} x {ncols_total}")

    null_vecs = gf2_gaussian_elimination(
        verified_relations, len(rat_fb), len(alg_fb), num_qc=num_qc)

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
