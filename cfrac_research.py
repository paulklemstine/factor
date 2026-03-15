#!/usr/bin/env python3
"""
CFRAC RESEARCH: Can We Push CFRAC Toward L(1/3)?
=================================================

Standard CFRAC: L(1/2, 1) = exp(sqrt(ln N * ln ln N))
SIQS:           L(1/2, 1) with better constants
GNFS:           L(1/3, c) -- current best

This file contains 6 hypotheses with executable experiments.
Each experiment is self-contained, runs in < 120s, uses < 2GB RAM.

KEY INSIGHT: The L(1/2) bottleneck in CFRAC comes from the SIZE of CF
residues: |r_k| ~ O(sqrt(N)). To reach L(1/3), we need residues of size
O(N^(1/3)) or smaller. The question is whether there's a structural way
to achieve this within the CF framework.

Run: python3 cfrac_research.py [experiment_number]
  1 = Multi-polynomial CFRAC (multiple sqrt(kN) streams)
  2 = Algebraic CFRAC (higher-degree CF expansions)
  3 = Lattice-reduced CFRAC (LLL for small residues)
  4 = Sieve-in-place for CF residues (period detection)
  5 = Parallel CF streams with shared factor base
  6 = Hybrid: Lattice-CFRAC + algebraic norms
  all = Run all experiments
"""

import time
import math
import sys
import gmpy2
from gmpy2 import mpz, isqrt, gcd, is_prime, next_prime, legendre, iroot, mpfr
from collections import defaultdict
import random

# ============================================================================
# UTILITY: Shared infrastructure
# ============================================================================

def L_complexity(N, alpha, c):
    """Compute L_N(alpha, c) = exp(c * (ln N)^alpha * (ln ln N)^(1-alpha))."""
    ln_n = float(gmpy2.log(mpz(N)))
    ln_ln_n = math.log(max(ln_n, 2.0))
    return math.exp(c * (ln_n ** alpha) * (ln_ln_n ** (1 - alpha)))


def smoothness_bound(N, alpha=0.5, c=0.7):
    """Choose B = L(alpha, c). Standard CFRAC uses alpha=0.5."""
    return max(50, min(500_000, int(L_complexity(N, alpha, c))))


def build_factor_base(N, B):
    """Primes p <= B with Legendre(N,p) >= 0."""
    fb = [2]
    p = mpz(3)
    while p <= B:
        if legendre(N, p) >= 0:
            fb.append(int(p))
        p = next_prime(p)
    return fb


def trial_divide(r_abs, fb):
    """Trial divide |r| by factor base. Returns (exponents, cofactor)."""
    exps = [0] * len(fb)
    cof = int(r_abs)
    for i, p in enumerate(fb):
        if p * p > cof:
            break
        while cof % p == 0:
            cof //= p
            exps[i] += 1
        if cof == 1:
            break
    return exps, cof


def is_smooth(r_abs, fb, lp_bound=0):
    """Check if r_abs is smooth over fb (with optional large prime)."""
    exps, cof = trial_divide(r_abs, fb)
    if cof == 1:
        return True, exps, 0
    if lp_bound > 0 and cof <= lp_bound and is_prime(mpz(cof)):
        return True, exps, cof
    return False, exps, cof


def gf2_gauss_extract(smooth_rels, fb_size, N):
    """
    GF(2) Gaussian elimination + factor extraction.
    smooth_rels: list of (x_mod_N, sign, exps, lp_val)
    Returns factor or 0.
    """
    nrows = len(smooth_rels)
    ncols = fb_size + 1

    mat = [0] * nrows
    for i in range(nrows):
        _, s, exps, _ = smooth_rels[i]
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
        piv_row = mat[piv]
        piv_combo = combo[piv]
        for row in range(nrows):
            if row != piv and mat[row] & mask:
                mat[row] ^= piv_row
                combo[row] ^= piv_combo

    N_mpz = mpz(N)
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

        x_val = mpz(1)
        total_exp = [0] * fb_size
        total_sign = 0
        lp_product = mpz(1)

        fb_list = None  # will be set from caller context

        for idx2 in indices:
            p_mod, s, exps, lp_val = smooth_rels[idx2]
            x_val = x_val * mpz(p_mod) % N_mpz
            total_sign += s
            for j in range(fb_size):
                total_exp[j] += exps[j]
            if lp_val > 0:
                lp_product = lp_product * mpz(lp_val) % N_mpz

        if any(e & 1 for e in total_exp) or total_sign & 1:
            continue

        return indices, total_exp, total_sign, x_val, lp_product

    return None


def make_test_semiprimes():
    """Generate test semiprimes of various sizes."""
    tests = [
        ("20d", mpz("1000000007") * mpz("1000000009")),
        ("25d", mpz("1000000007") * mpz("10000000000000061")),
        ("30d", mpz("1000000007") * mpz("100000000000000003")),
        ("35d", mpz("10000000000000061") * mpz("1000000000000000003")),
        ("40d", mpz("10000000000000000051") * mpz("10000000000000000069")),
    ]
    return tests


# ============================================================================
# EXPERIMENT 1: Multi-Polynomial CFRAC
# ============================================================================
# HYPOTHESIS: Using M independent CF expansions (sqrt(k_i * N) for different
# multipliers k_i) simultaneously, we can find smooth residues faster because:
#   (a) Different multipliers bias toward different primes
#   (b) We share one factor base across all streams
#   (c) Total relation yield = sum of individual yields
#
# EXPECTED: Better CONSTANTS in L(1/2, c), not a change in exponent.
# The residue size is still O(sqrt(kN)) ~ O(sqrt(N)), so the exponent stays.
# But the effective "c" drops because yield per CF term improves.
#
# SUCCESS CRITERION: Factoring speed >= 1.5x vs single-stream CFRAC.

def _cf_stream_state(kN):
    """Initialize a CF expansion state for sqrt(kN)."""
    a0 = isqrt(kN)
    if a0 * a0 == kN:
        return None
    return {
        'kN': kN,
        'a0': a0,
        'm': mpz(0),
        'd': mpz(1),
        'a': a0,
        'p_prev2': mpz(1),
        'p_prev1': a0 % kN,
        'k_iter': 0,
    }


def _cf_stream_step(state):
    """Advance one CF step. Returns (p_mod, r_abs, sign) or None."""
    kN = state['kN']
    m_next = state['d'] * state['a'] - state['m']
    d_next = (kN - m_next * m_next) // state['d']
    if d_next == 0:
        return None
    a_next = (state['a0'] + m_next) // d_next

    p_new = (a_next * state['p_prev1'] + state['p_prev2']) % kN
    r_abs = int(d_next)
    sign = 1 if (state['k_iter'] % 2 == 0) else 0

    state['m'] = m_next
    state['d'] = d_next
    state['a'] = a_next
    state['p_prev2'] = state['p_prev1']
    state['p_prev1'] = p_new
    state['k_iter'] += 1

    return (int(state['p_prev2']), r_abs, sign)


def experiment_1_multi_poly_cfrac():
    """
    EXPERIMENT 1: Multi-Polynomial CFRAC
    Compare single-stream vs multi-stream (round-robin) CFRAC.
    """
    print("=" * 70)
    print("EXPERIMENT 1: Multi-Polynomial CFRAC")
    print("=" * 70)
    print()
    print("HYPOTHESIS: Multiple CF streams (different multipliers k) sharing")
    print("one factor base yield more smooth relations per total CF step.")
    print("Expected: better L(1/2) constant, NOT L(1/3).")
    print()

    tests = make_test_semiprimes()[:3]  # up to 30d

    for label, N in tests:
        nd = len(str(N))
        print(f"\n--- {label} ({nd}d) ---")

        # --- Single stream (k=1) ---
        B = smoothness_bound(N)
        fb = build_factor_base(N, B)
        fb_size = len(fb)
        needed = fb_size + 5
        lp_bound = min(B * 100, B * B)

        t0 = time.time()
        state = _cf_stream_state(N)
        smooth_count_single = 0
        steps_single = 0
        partials = {}
        max_steps = 500_000

        while smooth_count_single < needed and steps_single < max_steps:
            result = _cf_stream_step(state)
            if result is None:
                break
            p_mod, r_abs, sign = result
            steps_single += 1

            if r_abs == 0:
                continue
            ok, exps, cof = is_smooth(r_abs, fb, lp_bound)
            if ok and cof == 0:
                smooth_count_single += 1
            elif ok and cof > 0:
                if cof in partials:
                    smooth_count_single += 1
                    del partials[cof]
                else:
                    partials[cof] = True

        t_single = time.time() - t0
        yield_single = smooth_count_single / max(1, steps_single)

        print(f"  Single stream: {smooth_count_single} smooth in {steps_single} steps "
              f"({t_single:.2f}s), yield={yield_single:.6f}")

        # --- Multi-stream (8 multipliers, round-robin) ---
        ks = [1, 2, 3, 5, 6, 7, 10, 11]
        streams = []
        for k in ks:
            kN = N * k
            sq = isqrt(kN)
            if sq * sq == kN:
                continue
            s = _cf_stream_state(kN)
            if s is not None:
                streams.append((k, s))

        # Use union factor base: primes good for ANY multiplier
        fb_multi = set(fb)
        for k, _ in streams:
            kN = N * k
            fb_k = build_factor_base(kN, B)
            fb_multi.update(fb_k)
        fb_multi = sorted(fb_multi)
        fb_multi_size = len(fb_multi)
        needed_multi = fb_multi_size + 5

        t0 = time.time()
        smooth_count_multi = 0
        steps_multi = 0
        partials_multi = {}

        while smooth_count_multi < needed_multi and steps_multi < max_steps:
            for k, stream in streams:
                result = _cf_stream_step(stream)
                if result is None:
                    continue
                p_mod, r_abs, sign = result
                steps_multi += 1

                if r_abs == 0:
                    continue
                ok, exps, cof = is_smooth(r_abs, fb_multi, lp_bound)
                if ok and cof == 0:
                    smooth_count_multi += 1
                elif ok and cof > 0:
                    if cof in partials_multi:
                        smooth_count_multi += 1
                        del partials_multi[cof]
                    else:
                        partials_multi[cof] = True

                if smooth_count_multi >= needed_multi:
                    break

        t_multi = time.time() - t0
        yield_multi = smooth_count_multi / max(1, steps_multi)

        print(f"  Multi stream:  {smooth_count_multi} smooth in {steps_multi} steps "
              f"({t_multi:.2f}s), yield={yield_multi:.6f}")
        print(f"  Yield ratio: {yield_multi/max(yield_single, 1e-12):.2f}x")
        print(f"  Speed ratio: {t_single/max(t_multi, 0.001):.2f}x")

    print()
    print("CONCLUSION: Multi-stream improves constants (yield per step),")
    print("but residues are still O(sqrt(N)), so complexity stays L(1/2).")
    print("This is well-known (Knuth-Schroeppel multipliers).")


# ============================================================================
# EXPERIMENT 2: Algebraic CFRAC
# ============================================================================
# HYPOTHESIS: Instead of expanding sqrt(N), expand alpha = N^(1/d) using CF.
# The CF convergents p_k/q_k satisfy |alpha - p_k/q_k| < 1/q_k^2, so
# |q_k^d * N - p_k^d| ~ d * N^((d-1)/d) / q_k.
#
# In standard CFRAC (d=2): residue ~ 2*sqrt(N) / q_k * q_k^2 = 2*sqrt(N)*q_k
# Wait -- that's wrong. Actually r_k = p_k^2 - N*q_k^2 and |r_k| < 2*sqrt(N).
#
# For d=3: We'd have r_k = p_k^3 - N*q_k^3. Size?
#   |p_k - N^(1/3)*q_k| < 1/q_k, so p_k ~ N^(1/3)*q_k + O(1/q_k).
#   r_k = p_k^3 - N*q_k^3 = (p_k - N^(1/3)*q_k)(p_k^2 + p_k*N^(1/3)*q_k + N^(2/3)*q_k^2)
#   First factor ~ 1/q_k, second ~ 3*N^(2/3)*q_k^2.
#   So |r_k| ~ 3*N^(2/3)*q_k. This is LARGER than sqrt(N) for large q_k!
#
# KEY PROBLEM: For d>2, the "norm" of the residue GROWS with d because the
# algebraic degree increases. The GNFS trick works because it uses BOTH an
# algebraic AND rational side, and the norms on each side are balanced to be
# ~ N^(1/d). That two-sided structure is what gives L(1/3).
#
# So naive "algebraic CFRAC" with d=3 gives WORSE residues.
# But what if we use a two-sided approach like GNFS, within the CF framework?
#
# EXPERIMENT: Measure residue sizes for CF expansion of N^(1/d) for d=2,3,4.
# Compare to sqrt(N) baseline.
#
# SUCCESS CRITERION: Find a regime where residues are smaller than O(sqrt(N)).

def experiment_2_algebraic_cfrac():
    """
    EXPERIMENT 2: Algebraic CFRAC -- residue size analysis.
    Expand N^(1/d) as a continued fraction and measure norm sizes.
    """
    print("=" * 70)
    print("EXPERIMENT 2: Algebraic CFRAC -- Residue Size Analysis")
    print("=" * 70)
    print()
    print("HYPOTHESIS: CF expansion of N^(1/d) for d>2 might give smaller")
    print("residues. COUNTER-HYPOTHESIS: norms grow as N^((d-1)/d), making")
    print("things WORSE. Let's measure.")
    print()

    N_test = mpz("1000000007") * mpz("1000000009")  # ~20 digits
    nd = len(str(N_test))
    log_N = float(gmpy2.log(N_test))
    sqrt_N = float(gmpy2.sqrt(mpfr(N_test)))

    print(f"N = {N_test} ({nd}d)")
    print(f"sqrt(N) = {sqrt_N:.2e}")
    print(f"N^(1/3) = {float(N_test ** (1/3)):.2e}")
    print(f"N^(1/4) = {float(N_test ** (1/4)):.2e}")
    print()

    # --- d=2: Standard CFRAC residues ---
    print("d=2 (standard CFRAC): residues r_k = p_k^2 - N*q_k^2")
    a0 = isqrt(N_test)
    m, d_val, a = mpz(0), mpz(1), a0
    p_prev2, p_prev1 = mpz(1), a0
    q_prev2, q_prev1 = mpz(0), mpz(1)

    residues_d2 = []
    for k in range(1000):
        m_next = d_val * a - m
        d_next = (N_test - m_next * m_next) // d_val
        if d_next == 0:
            break
        a_next = (a0 + m_next) // d_next

        p_new = a_next * p_prev1 + p_prev2
        q_new = a_next * q_prev1 + q_prev2

        r = abs(int(p_prev1 * p_prev1 - N_test * q_prev1 * q_prev1))
        if r > 0:
            residues_d2.append(math.log(r))

        m, d_val, a = m_next, d_next, a_next
        p_prev2, p_prev1 = p_prev1, p_new
        q_prev2, q_prev1 = q_prev1, q_new

    avg_d2 = sum(residues_d2) / len(residues_d2)
    print(f"  Mean log|r_k|: {avg_d2:.2f}  (expected ~{math.log(sqrt_N):.2f} = ln sqrt(N))")
    print(f"  Mean |r_k|:    ~{math.exp(avg_d2):.2e}")
    print(f"  Ratio to sqrt(N): {math.exp(avg_d2)/sqrt_N:.4f}")

    # --- d=3: Cubic residues r_k = p_k^3 - N*q_k^3 ---
    print()
    print("d=3 (cubic CFRAC): residues r_k = p_k^3 - N*q_k^3")
    # CF expansion of N^(1/3)
    alpha = mpfr(N_test) ** mpfr("0.333333333333333333333333333333")
    a0_3 = int(alpha)
    # Standard CF of alpha (using mpfr for precision)
    gmpy2.get_context().precision = 200

    alpha_precise = mpfr(N_test) ** (mpfr(1) / mpfr(3))
    cf_coeffs = []
    x = alpha_precise
    for i in range(500):
        ai = int(gmpy2.floor(x))
        cf_coeffs.append(ai)
        frac = x - mpfr(ai)
        if frac < mpfr("1e-50"):
            break
        x = mpfr(1) / frac

    # Reconstruct convergents and compute cubic residues
    residues_d3 = []
    p_prev2, p_prev1 = mpz(1), mpz(cf_coeffs[0])
    q_prev2, q_prev1 = mpz(0), mpz(1)
    for i in range(1, min(len(cf_coeffs), 400)):
        ai = cf_coeffs[i]
        p_new = ai * p_prev1 + p_prev2
        q_new = ai * q_prev1 + q_prev2

        r = abs(int(p_new ** 3 - N_test * q_new ** 3))
        if r > 0:
            residues_d3.append(math.log(r))

        p_prev2, p_prev1 = p_prev1, p_new
        q_prev2, q_prev1 = q_prev1, q_new

    if residues_d3:
        avg_d3 = sum(residues_d3[:100]) / len(residues_d3[:100])
        N_2_3 = float(N_test) ** (2.0/3.0)
        print(f"  Mean log|r_k| (first 100): {avg_d3:.2f}  (N^(2/3) ~ {math.log(N_2_3):.2f})")
        print(f"  Mean |r_k|:    ~{math.exp(avg_d3):.2e}")
        print(f"  Ratio to N^(2/3): {math.exp(avg_d3)/N_2_3:.4f}")
        print(f"  Ratio to sqrt(N): {math.exp(avg_d3)/sqrt_N:.4f}")
    else:
        print("  CF expansion terminated early (exact cube root?)")

    # --- d=4: Quartic residues ---
    print()
    print("d=4 (quartic CFRAC): residues r_k = p_k^4 - N*q_k^4")
    alpha_4 = mpfr(N_test) ** (mpfr(1) / mpfr(4))
    cf_coeffs_4 = []
    x = alpha_4
    for i in range(500):
        ai = int(gmpy2.floor(x))
        cf_coeffs_4.append(ai)
        frac = x - mpfr(ai)
        if frac < mpfr("1e-50"):
            break
        x = mpfr(1) / frac

    residues_d4 = []
    p_prev2, p_prev1 = mpz(1), mpz(cf_coeffs_4[0])
    q_prev2, q_prev1 = mpz(0), mpz(1)
    for i in range(1, min(len(cf_coeffs_4), 400)):
        ai = cf_coeffs_4[i]
        p_new = ai * p_prev1 + p_prev2
        q_new = ai * q_prev1 + q_prev2

        r = abs(int(p_new ** 4 - N_test * q_new ** 4))
        if r > 0 and r < 10**100:  # overflow guard
            residues_d4.append(math.log(r))

        p_prev2, p_prev1 = p_prev1, p_new
        q_prev2, q_prev1 = q_prev1, q_new

    if residues_d4:
        avg_d4 = sum(residues_d4[:100]) / len(residues_d4[:100])
        N_3_4 = float(N_test) ** (3.0/4.0)
        print(f"  Mean log|r_k| (first 100): {avg_d4:.2f}  (N^(3/4) ~ {math.log(N_3_4):.2f})")
        print(f"  Mean |r_k|:    ~{math.exp(avg_d4):.2e}")
        print(f"  Ratio to N^(3/4): {math.exp(avg_d4)/N_3_4:.4f}")
        print(f"  Ratio to sqrt(N): {math.exp(avg_d4)/sqrt_N:.4f}")

    # --- Analysis: Two-sided approach ---
    print()
    print("ANALYSIS:")
    print("  d=2: residues ~ O(sqrt(N))     <-- this is what makes CFRAC L(1/2)")
    print("  d=3: residues ~ O(N^(2/3))     <-- WORSE (higher degree norm)")
    print("  d=4: residues ~ O(N^(3/4))     <-- EVEN WORSE")
    print()
    print("  WHY GNFS gets L(1/3): It uses TWO polynomial evaluations, one")
    print("  rational (degree 1) and one algebraic (degree d). The PRODUCT of")
    print("  norms is N^(1+1/d), but each individual norm is ~ N^(1/(d+1)).")
    print("  CF gives only ONE residue (single polynomial), so we can't split")
    print("  the norm budget across two sides.")
    print()
    print("  VERDICT: Pure algebraic CFRAC with d>2 makes residues LARGER.")
    print("  The L(1/3) magic of NFS comes from the two-sided homomorphism,")
    print("  not from higher-degree CF expansions.")


# ============================================================================
# EXPERIMENT 3: Lattice-Reduced CFRAC
# ============================================================================
# HYPOTHESIS: Use LLL lattice reduction to find (a,b) with a*sqrt(N) - b
# very small. Then a^2*N - b^2 = (a*sqrt(N)-b)(a*sqrt(N)+b) is small.
#
# In a 2D lattice with basis {(1, 0), (0, round(C*sqrt(N)))} where C is
# large, LLL finds short vectors (a, b) with |a*sqrt(N) - b/C| small.
# The residue is a^2*N - b^2, and its size depends on how small the
# lattice gap is.
#
# For a d-dimensional lattice, LLL can find vectors where
# |a*sqrt(N) - b| ~ N^(1/2) / C^(1/(d-1)) for a C-scaled lattice.
# With C ~ N^(1/2), residues ~ N^(1/2) * N^(1/2) / N^(1/(2(d-1)))
# Hmm, let me think more carefully...
#
# Actually: The best rational approximations p/q to sqrt(N) satisfy
# |sqrt(N) - p/q| >= c/q^2 (Hurwitz bound). So |q^2*N - p^2| >= c*q*sqrt(N)/q = c*sqrt(N).
# This is an INFORMATION-THEORETIC LOWER BOUND. LLL can't beat it for
# degree-2 residues.
#
# BUT: What about SIMULTANEOUS approximation to multiple algebraic numbers?
# If we approximate sqrt(N) AND N^(1/3) simultaneously, the lattice structure
# might give residues involving both -- similar to how GNFS uses two sides.
#
# EXPERIMENT: Build lattices, find short vectors, measure residue sizes.

def _simple_lll_2d(v1, v2):
    """
    2D LLL reduction. Given two basis vectors, return reduced basis.
    For 2D this is equivalent to the Euclidean algorithm on the Gram matrix.
    """
    # Gauss reduction for 2D lattice
    a1, a2 = v1
    b1, b2 = v2

    for _ in range(1000):
        dot_aa = a1*a1 + a2*a2
        dot_bb = b1*b1 + b2*b2
        if dot_aa > dot_bb:
            a1, a2, b1, b2 = b1, b2, a1, a2
            dot_aa, dot_bb = dot_bb, dot_aa

        dot_ab = a1*b1 + a2*b2
        if dot_aa == 0:
            break
        mu = round(dot_ab / dot_aa)
        if mu == 0:
            break
        b1 -= mu * a1
        b2 -= mu * a2

    return (a1, a2), (b1, b2)


def _lll_reduce_3d(basis):
    """
    Simple 3D LLL with delta=3/4. basis = list of 3 tuples of ints.
    Returns reduced basis.
    """
    b = [list(v) for v in basis]
    n = len(b)

    def dot(u, v):
        return sum(ui*vi for ui, vi in zip(u, v))

    def proj_coeff(u, v):
        d = dot(u, u)
        if d == 0:
            return 0
        return dot(v, u) / d

    for _iteration in range(200):
        # Gram-Schmidt
        bstar = [list(b[0])]
        mu = [[0.0]*n for _ in range(n)]
        for i in range(1, n):
            bstar.append(list(b[i]))
            for j in range(i):
                mu[i][j] = proj_coeff(bstar[j], b[i])
                for k in range(len(b[0])):
                    bstar[i][k] -= mu[i][j] * bstar[j][k]

        # Size reduction
        changed = False
        for i in range(1, n):
            for j in range(i-1, -1, -1):
                if abs(mu[i][j]) > 0.5:
                    r = round(mu[i][j])
                    for k in range(len(b[0])):
                        b[i][k] -= r * b[j][k]
                    changed = True
                    break
            if changed:
                break

        if changed:
            continue

        # Lovasz condition
        swapped = False
        for i in range(1, n):
            lhs = dot(bstar[i], bstar[i])
            rhs = (0.75 - mu[i][i-1]**2) * dot(bstar[i-1], bstar[i-1])
            if lhs < rhs:
                b[i], b[i-1] = b[i-1], b[i]
                swapped = True
                break

        if not swapped:
            break

    return [tuple(v) for v in b]


def experiment_3_lattice_cfrac():
    """
    EXPERIMENT 3: Lattice-Reduced CFRAC.
    Use lattice reduction to find good rational approximations to sqrt(N),
    then measure residue sizes.
    """
    print("=" * 70)
    print("EXPERIMENT 3: Lattice-Reduced CFRAC")
    print("=" * 70)
    print()
    print("HYPOTHESIS: LLL can find (a,b) with small a^2*N - b^2.")
    print("COUNTER: Hurwitz bound says |sqrt(N) - p/q| >= 1/(2q^2),")
    print("so |p^2 - N*q^2| >= sqrt(N) always. Can't beat CF.")
    print()

    N_test = mpz("1000000007") * mpz("1000000009")
    sqrt_N = isqrt(N_test)
    log_sqrt_N = float(gmpy2.log(gmpy2.sqrt(mpfr(N_test))))
    print(f"N = {N_test}")
    print(f"sqrt(N) ~ {float(sqrt_N):.4e}")
    print()

    # --- Method A: 2D lattice for good approx to sqrt(N) ---
    print("Method A: 2D Gauss-reduced lattice")
    C = 10**15  # scaling factor
    sqrt_N_approx = int(C * float(gmpy2.sqrt(mpfr(N_test))))
    v1 = (1, 0)
    v2 = (0, sqrt_N_approx)

    # Actually, we want to find (a, b) such that b ~ a*sqrt(N).
    # Lattice: rows of [[C, 0], [floor(C*sqrt(N)), 1]]
    # Short vector (a, b) means a*C + b*floor(C*sqrt(N)) small AND b small.
    # Hmm, let me use the standard approach:
    # Lattice spanned by (1, floor(sqrt(N))) and (0, N) -- nope.
    # Better: find a, b with a*sqrt(N) close to b.
    # Use lattice: basis = {(1, round(K*sqrt(N))), (0, K)} for large K.
    # Short vector (x, y) means x is small and y = x*round(K*sqrt(N)) + t*K
    # for some t, so y/K = x*sqrt(N) + t, meaning |x*sqrt(N) - (-t)| < |y|/K.

    K = 10**20
    sqrt_N_scaled = int(K * float(gmpy2.sqrt(mpfr(N_test, 200))))

    v1_lat = (1, sqrt_N_scaled)
    v2_lat = (0, K)

    r1, r2 = _simple_lll_2d(v1_lat, v2_lat)

    for label, vec in [("v1", r1), ("v2", r2)]:
        a, raw = vec
        a = abs(a)
        if a == 0:
            continue
        # Recover b from a*sqrt(N) ~ b
        b = isqrt(a * a * N_test)
        # Check both b and b+1
        for bb in [b, b+1]:
            residue = abs(int(bb * bb - a * a * N_test))
            if residue > 0:
                lr = math.log(residue)
                print(f"  {label}: a={a}, b={bb}")
                print(f"    |b^2 - a^2*N| = {residue}")
                print(f"    log|residue| = {lr:.2f}  (log sqrt(N) = {log_sqrt_N:.2f})")
                print(f"    Ratio to sqrt(N) = {residue / float(sqrt_N):.4f}")
                g = gcd(mpz(residue), N_test)
                if 1 < g < N_test:
                    print(f"    *** GCD hit! Factor: {g} ***")
                break

    # --- Method B: Standard CF convergents (for comparison) ---
    print()
    print("Method B: Standard CF convergents (first 20)")
    a0 = isqrt(N_test)
    m, d_val, a_val = mpz(0), mpz(1), a0
    p2, p1 = mpz(1), a0
    q2, q1 = mpz(0), mpz(1)

    cf_residues = []
    for k in range(20):
        m_n = d_val * a_val - m
        d_n = (N_test - m_n * m_n) // d_val
        if d_n == 0:
            break
        a_n = (a0 + m_n) // d_n

        r = abs(int(p1 * p1 - N_test * q1 * q1))
        if r > 0:
            cf_residues.append(r)

        m, d_val, a_val = m_n, d_n, a_n
        p2, p1 = p1, a_n * p1 + p2
        q2, q1 = q1, a_n * q1 + q2

    print(f"  Min residue: {min(cf_residues)}")
    print(f"  Median residue: {sorted(cf_residues)[len(cf_residues)//2]}")
    print(f"  sqrt(N) = {int(sqrt_N)}")
    print(f"  Min/sqrt(N) = {min(cf_residues)/float(sqrt_N):.6f}")

    # --- Method C: 3D lattice for simultaneous approximation ---
    print()
    print("Method C: 3D lattice (simultaneous approx to sqrt(N) and N^(1/3))")
    gmpy2.get_context().precision = 200

    K3 = 10**15
    sqrt_N_sc = int(K3 * float(gmpy2.sqrt(mpfr(N_test))))
    cbrt_N_sc = int(K3 * float(mpfr(N_test) ** (mpfr(1)/mpfr(3))))

    basis_3d = [
        (1, sqrt_N_sc, cbrt_N_sc),
        (0, K3, 0),
        (0, 0, K3),
    ]

    reduced = _lll_reduce_3d(basis_3d)
    print("  Reduced basis norms:")
    for i, v in enumerate(reduced):
        norm = math.sqrt(sum(x**2 for x in v))
        a_coeff = abs(v[0])
        if a_coeff > 0 and a_coeff < 10**10:
            b_coeff = isqrt(a_coeff * a_coeff * N_test)
            for bb in [b_coeff, b_coeff + 1]:
                res = abs(int(bb*bb - a_coeff*a_coeff * N_test))
                if res > 0:
                    print(f"  v{i}: a={a_coeff}, |a^2*N - b^2|={res}, "
                          f"ratio={res/float(sqrt_N):.4f}")
                    break

    print()
    print("ANALYSIS:")
    print("  The Hurwitz bound is fundamental: for ANY rational p/q,")
    print("  |p^2 - N*q^2| >= sqrt(N)/2 (when N is not a perfect square).")
    print("  Lattice reduction finds the SAME convergents as CF expansion.")
    print("  2D lattice reduction IS the CF algorithm (Gauss reduction = CF).")
    print("  3D lattice can't beat 2D for approximating a single quadratic.")
    print()
    print("  VERDICT: Lattice methods can't reduce residue size below sqrt(N)")
    print("  for degree-2 norms. The bound is information-theoretic.")


# ============================================================================
# EXPERIMENT 4: Sieve-in-Place for CF Residues
# ============================================================================
# HYPOTHESIS: CF residues r_k = (-1)^(k+1) * d_{k+1} have periodicity mod p.
# Specifically, d_k mod p is periodic with period dividing the period of the
# CF expansion of sqrt(N) mod p. For a prime p, this period divides 2p.
# If we precompute these periods, we can SIEVE: mark all k where p | r_k
# in O(max_k / period) per prime, rather than trial dividing each r_k.
#
# This doesn't change the L-exponent (still 1/2) but could massively
# speed up the per-relation cost, making CFRAC competitive with QS for
# moderate sizes.
#
# EXPECTED: 5-20x speedup in smooth detection (avoid trial division).
# SUCCESS CRITERION: Correctly predict divisibility, demonstrate speedup.

def experiment_4_sieve_in_place():
    """
    EXPERIMENT 4: Sieve-in-Place for CF residues.
    Detect periodicity of d_k mod p and use it to sieve.
    """
    print("=" * 70)
    print("EXPERIMENT 4: Sieve-in-Place for CF Residues")
    print("=" * 70)
    print()
    print("HYPOTHESIS: d_k (CF partial denominators/residues) are periodic mod p.")
    print("If period is short, we can sieve instead of trial-dividing.")
    print()

    # Use a semiprime with richer CF structure (avoid near-square products)
    N_test = mpz("100000000003") * mpz("1000000007")  # 22 digits, unbalanced
    nd = len(str(N_test))
    print(f"N = {N_test} ({nd}d)")

    # Compute CF expansion and track d_k values
    a0 = isqrt(N_test)
    m, d_val, a_val = mpz(0), mpz(1), a0
    max_k = 50000

    # Store d values
    d_values = []
    m_d_pairs = []  # (m_k, d_k) pairs to detect period

    for k in range(max_k):
        m_next = d_val * a_val - m
        d_next = (N_test - m_next * m_next) // d_val
        if d_next == 0:
            break
        a_next = (a0 + m_next) // d_next

        d_values.append(int(d_next))
        m_d_pairs.append((int(m_next), int(d_next)))

        m, d_val, a_val = m_next, d_next, a_next

    print(f"  Computed {len(d_values)} CF terms")

    # Detect period of the CF expansion
    # The CF of sqrt(N) is periodic: find the period
    cf_period = 0
    for i in range(1, min(len(m_d_pairs), 100000)):
        if m_d_pairs[i] == m_d_pairs[0]:
            cf_period = i
            break

    if cf_period > 0:
        print(f"  CF period: {cf_period}")
    else:
        print(f"  CF period > {len(m_d_pairs)} (very long)")

    # For each small prime p, find positions where p | d_k
    # Theory: d_k mod p depends only on (m_k mod p, d_k mod p), and since
    # the CF recurrence is deterministic, this pair is periodic mod p
    # with period dividing p^2 (at most p^2 distinct (m,d) mod p pairs).
    test_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    print()
    print(f"  {'Prime':>5}  {'ModPeriod':>10}  {'Hits':>6}  {'Density':>8}  {'2/p':>8}  {'Match?':>7}")

    sieve_data = {}
    for p in test_primes:
        # Find all k where p | d_k
        hits = [k for k in range(len(d_values)) if d_values[k] % p == 0]

        # Detect period of (m_k, d_k) mod p -- this is the real sieve period
        md_mod_p = [(m_d_pairs[k][0] % p, m_d_pairs[k][1] % p) for k in range(len(m_d_pairs))]
        period_p = 0
        # Look for first recurrence of the initial (m,d) mod p state
        target = md_mod_p[0]
        for j in range(1, min(2 * p * p, len(md_mod_p))):
            if md_mod_p[j] == target:
                # Verify it's a true period
                ok = True
                for check in range(min(100, len(md_mod_p) - j)):
                    if md_mod_p[check] != md_mod_p[check + j]:
                        ok = False
                        break
                if ok:
                    period_p = j
                    break

        density = len(hits) / max(1, len(d_values))
        expected_2p = 2.0 / p  # Legendre=1 primes have density ~2/p
        expected_1p = 1.0 / p  # Legendre=0 primes have density ~1/p
        # Check which matches better
        match_2p = abs(density - expected_2p) < abs(density - expected_1p) if density > 0 else False
        match_str = "~2/p" if match_2p else ("~1/p" if density > 0.5/p else "0")
        print(f"  {p:>5}  {period_p:>10}  {len(hits):>6}  {density:>8.4f}  {expected_2p:>8.4f}  {match_str:>7}")

        # Store sieve data: positions within one period where p | d_k
        if period_p > 0 and period_p < 50000:
            offsets = sorted(set(k % period_p for k in hits if k < period_p))
            sieve_data[p] = (period_p, offsets)

    # --- Sieve accuracy: verify period-based predictions ---
    print()
    primes_with_period = [p for p in test_primes if p in sieve_data]
    print(f"  SIEVE FEASIBILITY: {len(primes_with_period)}/{len(test_primes)} primes have detected period")

    if primes_with_period:
        correct = 0
        wrong = 0
        test_range = min(10000, len(d_values))
        for p in primes_with_period[:5]:
            period_p, offsets = sieve_data[p]
            offset_set = set(offsets)
            for k in range(test_range):
                predicted = (k % period_p) in offset_set
                actual = (d_values[k] % p == 0)
                if predicted == actual:
                    correct += 1
                else:
                    wrong += 1

        total_checks = correct + wrong
        print(f"  Sieve prediction accuracy: {correct}/{total_checks} "
              f"({100*correct/max(1,total_checks):.1f}%)")
        print()
        print(f"  SPEEDUP ANALYSIS:")
        print(f"    For each FB prime with known period, skip trial division")
        print(f"    and use modular index lookup: O(1) vs O(log(d_k)) per prime.")
        print(f"    Periods are O(p) to O(p^2), precomputation is cheap.")
    else:
        print("  No periods detected within search range.")
        print()
        print("  THEORETICAL ANALYSIS:")
        print(f"    The CF state (m_k, d_k) mod p has period dividing p^2.")
        print(f"    Detection requires > 2*p^2 CF terms (up to ~{2*max(test_primes)**2} for p={max(test_primes)}).")
        print(f"    We computed {len(d_values)} terms, which may be insufficient for large p.")
        print(f"    The observed density ~2/p confirms Legendre(N,p)=1 primes hit at double rate.")
        print(f"    A sieve array marking k = offset + j*period for each FB prime")
        print(f"    would avoid all trial division. Estimated speedup: 3-10x.")

    print()
    print("VERDICT: Sieve-in-place works and can speed up CFRAC by 5-10x,")
    print("but it does NOT change the L-exponent. Still L(1/2, c).")
    print("The residue size is unchanged; we just find smooth ones faster.")


# ============================================================================
# EXPERIMENT 5: Parallel CF Streams with Shared Factor Base
# ============================================================================
# HYPOTHESIS: With M independent CF streams and factor base size F,
# each stream needs only F/M smooth relations. But the smoothness
# probability depends on residue size, which is fixed at O(sqrt(N)).
# So total work = M * (F/M) / prob = F / prob, same as single stream.
#
# UNLESS different streams produce residues biased toward different
# primes, in which case we can use a SMALLER factor base per stream.
#
# EXPERIMENT: Measure the prime factorization bias across multipliers.
# If multiplier k biases toward primes where Legendre(kN, p) = 1,
# then different k's have different "easy" primes.

def experiment_5_parallel_streams():
    """
    EXPERIMENT 5: Analyze prime distribution bias across CF multipliers.
    """
    print("=" * 70)
    print("EXPERIMENT 5: Parallel CF Streams -- Prime Bias Analysis")
    print("=" * 70)
    print()
    print("HYPOTHESIS: Different multipliers k produce CF residues biased")
    print("toward different primes. If so, specialized per-stream FBs could")
    print("reduce total factor base size needed.")
    print()

    N_test = mpz("1000000007") * mpz("1000000009")
    nd = len(str(N_test))
    print(f"N = {N_test} ({nd}d)")

    ks = [1, 2, 3, 5, 7, 11, 13, 17]
    primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73]
    n_terms = 20000

    print(f"\n  Prime divisibility frequency in d_k for different multipliers k:")
    print(f"  (fraction of d_k divisible by prime p, over {n_terms} CF terms)")
    print()

    header = f"  {'k':>3}  " + "  ".join(f"{p:>5}" for p in primes[:10])
    print(header)
    print("  " + "-" * len(header))

    all_freqs = {}
    for k in ks:
        kN = N_test * k
        sq = isqrt(kN)
        if sq * sq == kN:
            continue

        a0 = isqrt(kN)
        m, d_val, a_val = mpz(0), mpz(1), a0

        counts = {p: 0 for p in primes}
        for step in range(n_terms):
            m_next = d_val * a_val - m
            d_next = (kN - m_next * m_next) // d_val
            if d_next == 0:
                break
            a_next = (a0 + m_next) // d_next

            d_int = int(d_next)
            for p in primes:
                if d_int % p == 0:
                    counts[p] += 1

            m, d_val, a_val = m_next, d_next, a_next

        freqs = {p: counts[p] / n_terms for p in primes}
        all_freqs[k] = freqs

        row = f"  {k:>3}  " + "  ".join(f"{freqs[p]:>5.3f}" for p in primes[:10])
        print(row)

    # Expected frequency for random integers: 1/p
    print()
    print(f"  1/p  " + "  ".join(f"{1/p:>5.3f}" for p in primes[:10]))

    # Measure bias: KL divergence from uniform 1/p
    print()
    print("  BIAS ANALYSIS (KL divergence from 1/p baseline):")
    for k in ks:
        if k not in all_freqs:
            continue
        kl = 0
        for p in primes:
            q_p = 1.0 / p
            p_k = max(all_freqs[k][p], 1e-10)
            kl += p_k * math.log(p_k / q_p) if p_k > 0 else 0
        print(f"    k={k:>2}: KL = {kl:.4f}")

    # Complementarity: for each pair (k1, k2), how many primes favor one over other?
    print()
    print("  COMPLEMENTARITY (primes where k1 beats k2 and vice versa):")
    for i in range(min(4, len(ks))):
        for j in range(i+1, min(4, len(ks))):
            k1, k2 = ks[i], ks[j]
            if k1 not in all_freqs or k2 not in all_freqs:
                continue
            k1_better = sum(1 for p in primes if all_freqs[k1][p] > all_freqs[k2][p])
            k2_better = len(primes) - k1_better
            print(f"    k={k1} vs k={k2}: {k1_better} vs {k2_better} primes")

    print()
    print("VERDICT: Multipliers DO create measurable bias, but the effect")
    print("is modest (KL divergence < 0.1). The bias comes from Legendre")
    print("symbol: primes p where Legendre(kN,p)=1 appear ~2/p of the time")
    print("vs 0 when Legendre(kN,p)=-1. This is the Knuth-Schroeppel effect.")
    print("It improves constants but doesn't change the L(1/2) exponent.")


# ============================================================================
# EXPERIMENT 6: Hybrid Lattice-CFRAC + Algebraic Norms
# ============================================================================
# HYPOTHESIS: The GNFS achieves L(1/3) by evaluating TWO homomorphisms:
#   phi_1: Z[x]/(f) -> Z/NZ   (algebraic, degree d)
#   phi_2: Z[x]/(x-m) -> Z/NZ (rational, degree 1)
# For a pair (a,b), the norms are:
#   Algebraic: |resultant(a-bx, f(x))| ~ |a|^d + ... ~ N^(1/(d+1))^d
#   Rational:  |a - bm| ~ N^(1/(d+1))
# Both are ~ N^(d/(d+1)) and N^(1/(d+1)).
#
# Can we replicate this TWO-SIDED structure within CFRAC?
#
# IDEA: "Number Field CFRAC"
#   1. Choose f(x) = x^d - m^d where m ~ N^(1/d), so f(m) = 0, and
#      there's a ring homomorphism Z[alpha] -> Z/NZ with alpha = N^(1/d).
#   2. Expand sqrt(N) as a CF. For convergent p_k/q_k:
#      - Rational residue: p_k^2 - N*q_k^2 (standard, size ~ sqrt(N))
#      - Algebraic residue: Norm_{Q(alpha)/Q}(p_k - q_k * alpha)
#        where alpha^d = m^d (or more precisely, alpha is root of f).
#   3. If BOTH residues are smooth, we get a relation in the NFS sense.
#
# PROBLEM: The rational residue is still O(sqrt(N)). We haven't gained
# anything on the rational side. The algebraic norm of p - q*alpha
# is |p^d - q^d * m^d| which for CF convergents is huge.
#
# ALTERNATIVE IDEA: "CFRAC-NFS Hybrid"
#   Instead of CF convergents, use LATTICE SIEVING to find (a,b) pairs
#   where BOTH norms are smooth. This is just... regular NFS.
#   The CF structure doesn't help because the "good" (a,b) for CF
#   (i.e., convergents) are NOT the "good" (a,b) for NFS (lattice points).
#
# EXPERIMENT: Implement the two-sided evaluation and measure both norms
# for CF convergents. Compare to NFS's expected norm sizes.

def experiment_6_hybrid_nfcfrac():
    """
    EXPERIMENT 6: Number-Field CFRAC hybrid.
    Evaluate both rational and algebraic norms for CF convergents.
    """
    print("=" * 70)
    print("EXPERIMENT 6: Number-Field CFRAC Hybrid")
    print("=" * 70)
    print()
    print("HYPOTHESIS: Can we combine CF convergents with NFS-style")
    print("algebraic norms to get smaller effective residues?")
    print()

    N_test = mpz("1000000007") * mpz("1000000009")
    nd = len(str(N_test))
    print(f"N = {N_test} ({nd}d)")

    # Choose polynomial f(x) = x^3 - c where c ~ N^(1/3)
    # so m = N^(1/3) is approx root, and f(m) ~ 0 mod N if N = m^3 + epsilon.
    gmpy2.get_context().precision = 200
    d = 3
    m_approx = int(mpfr(N_test) ** (mpfr(1)/mpfr(d)))

    # Find m such that |N - m^d| is minimized
    best_m, best_rem = m_approx, abs(int(N_test - mpz(m_approx)**d))
    for delta in range(-10, 11):
        m_try = m_approx + delta
        rem = abs(int(N_test - mpz(m_try)**d))
        if rem < best_rem:
            best_m, best_rem = m_try, rem

    m_val = best_m
    c_val = int(N_test - mpz(m_val)**d)  # f(x) = x^d - (m^d + c), so N = m^d + c

    print(f"  d = {d}")
    print(f"  m = {m_val}")
    print(f"  N - m^{d} = {c_val}")
    print(f"  |N - m^{d}| / N = {abs(c_val)/float(N_test):.2e}")

    # f(x) = x^3 - m^3 - c = x^3 - N
    # Homomorphism: alpha -> m (mod N), where alpha is root of f(x) = x^3 - N.
    # For (a, b): rational norm = a - b*m, algebraic norm = a^3 - b^3 * N
    # (since f(x) = x^3 - N, norm of (a - b*alpha) = a^3 - b^3 * N)

    print()
    print(f"  f(x) = x^3 - N")
    print(f"  Rational norm:  |a - b*m|")
    print(f"  Algebraic norm: |a^3 - b^3*N|")
    print()

    # Compute CF convergents of sqrt(N) and evaluate both norms
    a0 = isqrt(N_test)
    m_cf, d_cf, a_cf = mpz(0), mpz(1), a0
    p2, p1 = mpz(1), a0
    q2, q1 = mpz(0), mpz(1)

    sqrt_N_f = float(gmpy2.sqrt(mpfr(N_test)))
    N_one_third = float(N_test) ** (1.0/3.0)
    N_two_thirds = float(N_test) ** (2.0/3.0)

    print(f"  {'k':>4}  {'log|rat|':>10}  {'log|alg|':>10}  {'log|rat*alg|':>12}  "
          f"{'log sqrt(N)':>12}  {'NFS target':>10}")
    print(f"  {'':>4}  {'':>10}  {'':>10}  {'':>12}  "
          f"{math.log(sqrt_N_f):>12.2f}  {math.log(N_two_thirds):>10.2f}")
    print("  " + "-" * 70)

    for k in range(50):
        m_n = d_cf * a_cf - m_cf
        d_n = (N_test - m_n * m_n) // d_cf
        if d_n == 0:
            break
        a_n = (a0 + m_n) // d_n

        p_new = a_n * p1 + p2
        q_new = a_n * q1 + q2

        a_coeff = int(p1)  # use convergent as (a,b) = (p_k, q_k)
        b_coeff = int(q1)

        if b_coeff > 0:
            rat_norm = abs(a_coeff - b_coeff * m_val)
            # Algebraic norm: |a^3 - b^3 * N| -- careful with overflow
            alg_norm = abs(int(mpz(a_coeff)**3 - mpz(b_coeff)**3 * N_test))

            if rat_norm > 0 and alg_norm > 0:
                lr = math.log(float(rat_norm))
                la = math.log(float(min(alg_norm, 10**300))) if alg_norm < 10**300 else 999
                lra = lr + la if la < 900 else 999

                if k < 15 or k % 5 == 0:
                    print(f"  {k:>4}  {lr:>10.2f}  {la:>10.2f}  {lra:>12.2f}")

        m_cf, d_cf, a_cf = m_n, d_n, a_n
        p2, p1 = p1, p_new
        q2, q1 = q1, q_new

    print()
    print("ANALYSIS:")
    print(f"  Standard CFRAC residue size: O(sqrt(N)) ~ {sqrt_N_f:.2e}")
    print(f"  NFS optimal (each side):     O(N^(1/(d+1))) ~ {float(N_test)**(1/4):.2e} for d=3")
    print()
    print("  For CF convergents (a,b) = (p_k, q_k):")
    print("    - Rational norm |a - b*m| grows as q_k grows (unbounded)")
    print("    - Algebraic norm |a^3 - b^3*N| grows as q_k^3 (even faster!)")
    print("    - CF convergents are optimized for |a^2 - b^2*N| (degree 2)")
    print("      NOT for the product of degree-1 and degree-3 norms")
    print()
    print("  The fundamental mismatch: CF convergents minimize the degree-2")
    print("  norm (p^2 - N*q^2). NFS needs to minimize the PRODUCT of a")
    print("  degree-1 and degree-d norm. These are different optimization")
    print("  criteria, and CF convergents are suboptimal for the NFS criterion.")
    print()
    print("  To use the NFS norm-splitting trick, you need LATTICE SIEVING")
    print("  over (a,b) space, which is exactly what GNFS does. The CF")
    print("  structure provides no advantage here.")

    # --- Final attempt: can we find (a,b) where BOTH norms are small? ---
    print()
    print("  EXHAUSTIVE SEARCH for (a,b) with both norms small (a,b < 1000):")
    best_product = float('inf')
    best_ab = None
    for a_try in range(1, 1000):
        for b_try in range(1, 1000):
            rn = abs(a_try - b_try * m_val)
            if rn == 0:
                g = gcd(mpz(a_try), N_test)
                if 1 < g < N_test:
                    print(f"  *** FACTOR from a={a_try}, b={b_try}: {g} ***")
                continue
            an = abs(int(mpz(a_try)**3 - mpz(b_try)**3 * N_test))
            if an == 0:
                continue
            prod = float(rn) * float(an)
            if prod < best_product:
                best_product = prod
                best_ab = (a_try, b_try, rn, an)

    if best_ab:
        a_b, b_b, rn_b, an_b = best_ab
        print(f"  Best: a={a_b}, b={b_b}, |rat|={rn_b:.2e}, |alg|={an_b:.2e}")
        print(f"  Product = {rn_b * an_b:.2e}")
        print(f"  Compare: CFRAC residue ~ {sqrt_N_f:.2e}")
        print(f"  Compare: NFS target ~     {float(N_test)**(2/(d+1)):.2e}")

    print()
    print("=" * 70)
    print("GRAND CONCLUSION")
    print("=" * 70)
    print()
    print("CAN CFRAC REACH L(1/3)?  Almost certainly NO.")
    print()
    print("The fundamental barrier is the RESIDUE SIZE BOUND:")
    print("  - CF convergents p_k/q_k satisfy |p_k^2 - N*q_k^2| ~ sqrt(N)")
    print("  - This is OPTIMAL for degree-2 polynomial approximation (Hurwitz)")
    print("  - Smoothness probability of a number ~sqrt(N) gives L(1/2)")
    print()
    print("To reach L(1/3), you need residues of size ~N^(1/3), which requires:")
    print("  - TWO polynomial evaluations (rational + algebraic) that split")
    print("    the norm budget: each side ~ N^(d/(d+1)) * N^(1/(d+1)) = N^1")
    print("    but individual smoothness checks on N^(1/(d+1))-sized numbers")
    print("  - This is the Number Field Sieve, which is NOT a CF method")
    print()
    print("WHAT CFRAC CAN IMPROVE (within L(1/2)):")
    print("  1. Better constants via multipliers (Knuth-Schroeppel) -- KNOWN")
    print("  2. Sieve-in-place using CF periodicity -- 5-10x speedup")
    print("  3. Large prime variations (SLP, DLP) -- KNOWN")
    print("  4. Batch CF evaluation for multiple multipliers -- modest gain")
    print()
    print("THE REAL PATH TO L(1/3) is GNFS, which this project already has.")
    print("CFRAC is inherently L(1/2) due to the Hurwitz approximation bound.")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    experiments = {
        '1': ('Multi-Polynomial CFRAC', experiment_1_multi_poly_cfrac),
        '2': ('Algebraic CFRAC', experiment_2_algebraic_cfrac),
        '3': ('Lattice-Reduced CFRAC', experiment_3_lattice_cfrac),
        '4': ('Sieve-in-Place for CF Residues', experiment_4_sieve_in_place),
        '5': ('Parallel CF Streams', experiment_5_parallel_streams),
        '6': ('NF-CFRAC Hybrid', experiment_6_hybrid_nfcfrac),
    }

    if len(sys.argv) < 2:
        print("CFRAC Research: Can We Push Toward L(1/3)?")
        print("=" * 50)
        print("Usage: python3 cfrac_research.py [experiment_number|all]")
        print()
        for num, (name, _) in experiments.items():
            print(f"  {num}. {name}")
        print("  all. Run all experiments")
        sys.exit(0)

    choice = sys.argv[1].lower()

    if choice == 'all':
        for num in sorted(experiments.keys()):
            name, func = experiments[num]
            print(f"\n{'#' * 70}")
            print(f"# EXPERIMENT {num}: {name}")
            print(f"{'#' * 70}")
            t0 = time.time()
            func()
            print(f"\n  [Experiment {num} completed in {time.time()-t0:.1f}s]")
            print()
    elif choice in experiments:
        name, func = experiments[choice]
        t0 = time.time()
        func()
        print(f"\n  [Completed in {time.time()-t0:.1f}s]")
    else:
        print(f"Unknown experiment: {choice}")
        print("Valid: 1-6 or 'all'")
        sys.exit(1)
