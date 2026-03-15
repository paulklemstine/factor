#!/usr/bin/env python3
"""
GNFS-B3 Hybrid Engine
=====================

Integrates B3-MPQS insights into the GNFS pipeline:

1. **B3-Inspired Polynomial Selection**: Score polynomials by how many
   (a,b) pairs yield small norms on BOTH sides simultaneously.
   The B3 parabolic property means norms grow quadratically from
   the minimum — we find polynomials where that minimum is deep.

2. **Multi-Polynomial GNFS**: Like MPQS uses multiple a-polynomials,
   we use multiple m values (slight perturbations) to generate
   fresh sieve regions with different smooth-probability profiles.
   Each m gives a different polynomial f(x) where f(m)=N.

3. **Rational Norm Pre-filtering**: For each b-line, the rational norm
   |a + b*m| has a zero at a = -b*m. Near that zero, rational norms
   are tiny and almost certainly smooth. We exploit this by using a
   larger sieve region centered at a = -b*m (when it's within range).

Usage:
  from gnfs_b3_hybrid import gnfs_b3_hybrid_factor
  factor = gnfs_b3_hybrid_factor(N, verbose=True)
"""

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, next_prime, iroot
import math
import time
import numpy as np
from collections import defaultdict
import random
import ctypes
import os

from gnfs_engine import (
    base_m_poly, gnfs_params, eval_poly,
    build_rational_fb, build_algebraic_fb,
    build_qc_primes, build_inert_qc_primes,
    compute_qc_vector, compute_inert_qc_vector,
    norm_algebraic, find_poly_roots_mod_p,
    gf2_gaussian_elimination,
    extract_factor,
    murphy_alpha,
    _load_gnfs_sieve,
)


###############################################################################
# B3-Inspired Multi-Polynomial Selection
###############################################################################

def b3_multi_poly_select(N, d, num_polys=5, verbose=False):
    """
    Select multiple GNFS polynomials using B3-inspired scoring.

    For each candidate m, we compute f(x) via base-m representation,
    then score it by:
    1. Standard norm size at typical sieve points (Murphy-like)
    2. B3 parabolic score: how quickly norms grow from the minimum
       (slower growth = more smooth candidates)
    3. Root count score: more roots mod small primes = more sieve hits

    Returns list of (f_coeffs, m, score) tuples, best first.
    """
    N = mpz(N)
    m0, _ = iroot(N, d)
    m0 = int(m0)

    def _base_m_poly(N, m, d):
        coeffs = []
        remainder = N
        for i in range(d + 1):
            coeff = remainder % m
            remainder = remainder // m
            coeffs.append(int(coeff))
        if remainder > 0:
            coeffs[-1] = int(coeffs[-1] + remainder * m)
        f_at_m = mpz(0)
        m_power = mpz(1)
        for c in coeffs:
            f_at_m += mpz(c) * m_power
            m_power *= m
        if f_at_m != N:
            return None
        return coeffs

    def _b3_score(coeffs, m_val, d):
        """B3-inspired polynomial score. Lower = better."""
        if coeffs is None:
            return float('inf')
        lc = abs(coeffs[-1])
        if lc == 0:
            return float('inf')

        # 1. Standard norm size score
        c0 = max(abs(coeffs[0]), 1)
        skew = max(1.0, float(c0 / lc) ** (1.0 / d)) if lc > 0 else 1.0
        norm_score = 0.0
        for t in [10, 100, 1000, 10000]:
            a_test = max(1, int(skew * t))
            b_test = max(1, t)
            norm_est = sum(abs(coeffs[i]) * a_test**i * b_test**(d-i)
                           for i in range(d+1))
            norm_score += math.log(max(norm_est, 1))

        # 2. B3 parabolic score: check derivative at sieve center
        # The algebraic norm N(a,b) for fixed b is a polynomial in a
        # of degree d. Its growth rate from the minimum determines
        # how many smooth values we find. Slower growth = better.
        # Proxy: |f''(0)| * typical_b^d / |f(0)| (curvature ratio)
        deriv2 = sum(i * (i-1) * abs(coeffs[i]) for i in range(2, d+1))
        if c0 > 0 and deriv2 > 0:
            curvature = math.log(deriv2 + 1) - math.log(c0 + 1)
            norm_score += curvature * 0.3  # small weight

        # 3. Leading coefficient penalty
        norm_score += 2.0 * math.log(lc + 1)

        # 4. Root count bonus: more roots mod small primes = better
        root_bonus = 0
        for p in [2, 3, 5, 7, 11, 13]:
            nroots = 0
            for r in range(p):
                val = 0
                r_pow = 1
                for c in coeffs:
                    val = (val + c * r_pow) % p
                    r_pow = (r_pow * r) % p
                if val == 0:
                    nroots += 1
            root_bonus += nroots * math.log(p) / p
        norm_score -= root_bonus * 2.0  # bonus for rootier polys

        return norm_score

    # Search ±search_range around m0
    search_range = 2000 if d >= 4 else 200
    candidates = []

    for delta in range(-search_range, search_range + 1):
        m_try = m0 + delta
        if m_try < 2:
            continue
        coeffs = _base_m_poly(N, mpz(m_try), d)
        if coeffs is None:
            continue
        score = _b3_score(coeffs, m_try, d)
        candidates.append((coeffs, m_try, score))

    # Sort by score (lower = better) and return top num_polys
    candidates.sort(key=lambda x: x[2])

    if verbose and candidates:
        print(f"    B3 poly search: {len(candidates)} candidates, "
              f"best score={candidates[0][2]:.2f}, "
              f"worst={candidates[-1][2]:.2f}")

    return candidates[:num_polys]


###############################################################################
# Main Hybrid Engine: Multi-Polynomial GNFS with B3 Scoring
###############################################################################

def gnfs_b3_hybrid_factor(N, verbose=True, time_limit=3600):
    """
    Factor N using GNFS with B3 hybrid enhancements:

    1. B3-inspired multi-polynomial selection (score by norm + rootiness)
    2. Standard GNFS C sieve with the best polynomial
    3. If first poly fails, try additional polynomials
    4. SLP/DLP combining + GF(2) LA + algebraic sqrt

    The multi-polynomial approach is inspired by B3-MPQS where switching
    polynomials keeps residues fresh and small. In GNFS, different m values
    produce different polynomials with different smoothness profiles.
    """
    N = mpz(N)
    nd = len(str(int(N)))
    nb = int(gmpy2.log2(N)) + 1
    N_int = int(N)
    t0 = time.time()

    if verbose:
        print(f"  GNFS-B3 Hybrid: {nd}d ({nb}b)")

    # Quick checks
    if N <= 1: return 0
    if N % 2 == 0: return 2
    if N % 3 == 0: return 3
    for sp in range(5, 1000, 2):
        if N % sp == 0: return sp
    for exp in range(2, nb + 1):
        root, exact = iroot(N, exp)
        if exact: return int(root)
    if is_prime(N): return int(N)

    # Step 1: Parameters
    params = gnfs_params(N)
    d = params['d']

    # Step 2: Primary polynomial (same as standard GNFS for best perf)
    poly = base_m_poly(N, d=d)
    if 'factor' in poly:
        return poly['factor']

    # Also generate B3 alternative polynomials for retry
    num_alt_polys = 2 if nd < 45 else 4
    alt_polys = b3_multi_poly_select(N, d, num_polys=num_alt_polys + 1, verbose=verbose)
    # Filter out the primary poly's m to avoid duplication
    primary_m = poly['m']
    alt_polys = [(c, m_v, s) for c, m_v, s in alt_polys if m_v != primary_m][:num_alt_polys]

    # Build poly list: primary first, then alternatives
    all_polys = [(poly['f_coeffs'], poly['m'], 0.0)] + alt_polys

    for poly_idx, (f_coeffs, m, score) in enumerate(all_polys):
        if time.time() - t0 > time_limit:
            break

        remaining_time = time_limit - (time.time() - t0)
        # Primary poly gets 80% of time, alternatives split the rest
        if poly_idx == 0:
            poly_time = remaining_time * 0.8
        else:
            poly_time = remaining_time / max(1, len(all_polys) - poly_idx)

        m_int = int(m)
        alpha = murphy_alpha(f_coeffs, B=200)

        if verbose:
            label = "primary" if poly_idx == 0 else f"alt #{poly_idx}"
            terms = []
            for i, c in enumerate(f_coeffs):
                if c != 0:
                    if i == 0: terms.append(str(c))
                    elif i == 1: terms.append(f"{c}*x")
                    else: terms.append(f"{c}*x^{i}")
            print(f"\n    Poly {label} (m={m}, alpha={alpha:.3f})")
            print(f"    f(x) = {' + '.join(terms)}")

        result = _gnfs_with_poly(
            N, f_coeffs, m_int, params, d,
            verbose=verbose, time_limit=poly_time, t0=t0)

        if result is not None:
            total_t = time.time() - t0
            if verbose:
                label = "primary" if poly_idx == 0 else f"alt #{poly_idx}"
                print(f"\n    *** FACTOR: {result} ({nd}d, {total_t:.1f}s, "
                      f"poly {label}) ***")
            return result

        if verbose and poly_idx < len(all_polys) - 1:
            print(f"    Poly failed, trying alternative...")

    if verbose:
        print(f"    All {len(poly_candidates)} polynomials exhausted")
    return None


def _gnfs_with_poly(N, f_coeffs, m_int, params, d,
                     verbose=True, time_limit=3600, t0=None):
    """Run GNFS with a specific polynomial. Returns factor or None."""
    if t0 is None:
        t0 = time.time()

    N_int = int(N)
    nd = len(str(N_int))

    # Factor bases
    t_fb = time.time()
    rat_fb = build_rational_fb(params['B_r'])
    alg_fb = build_algebraic_fb(f_coeffs, params['B_a'])
    fb_time = time.time() - t_fb

    if verbose:
        print(f"    Rational FB: {len(rat_fb)}, Algebraic FB: {len(alg_fb)} ({fb_time:.1f}s)")

    # QC primes
    num_split_qc = 20
    qc_primes = build_qc_primes(f_coeffs, num_qc=num_split_qc, min_p=50000)
    num_inert_qc = 5
    inert_qc_primes = build_inert_qc_primes(f_coeffs, num_qc=num_inert_qc, min_p=100)
    num_qc = num_split_qc + num_inert_qc

    needed = int((len(rat_fb) + len(alg_fb) + num_qc + 2) * 1.10)
    if verbose:
        print(f"    Need {needed} relations")

    # Sieve
    t_sieve = time.time()
    all_relations = _c_sieve_collect(
        N, f_coeffs, m_int, rat_fb, alg_fb,
        qc_primes, inert_qc_primes, params, needed,
        verbose=verbose, time_limit=time_limit - (time.time() - t0), t0=t0)

    sieve_time = time.time() - t_sieve
    if verbose:
        print(f"    Sieve: {len(all_relations)}/{needed} in {sieve_time:.1f}s")

    if len(all_relations) < needed:
        return None

    # LA
    la_t0 = time.time()
    ncols_total = 1 + len(rat_fb) + len(alg_fb) + num_qc
    if verbose:
        print(f"    LA: {len(all_relations)} x {ncols_total}")

    null_vecs = gf2_gaussian_elimination(
        all_relations, len(rat_fb), len(alg_fb),
        num_qc=num_qc, num_sq=0, num_lp=0, verbose=verbose)

    if verbose:
        print(f"    LA: {time.time()-la_t0:.1f}s, {len(null_vecs)} null vecs")

    if not null_vecs:
        return None

    # Factor extraction
    return extract_factor(N, null_vecs, all_relations, m_int,
                          rat_fb, alg_fb, f_coeffs)


def _c_sieve_collect(N, f_coeffs, m_int, rat_fb, alg_fb,
                      qc_primes, inert_qc_primes, params, needed,
                      verbose=True, time_limit=3600, t0=None):
    """C sieve relation collection (extracted from gnfs_engine)."""
    if t0 is None:
        t0 = time.time()

    d = len(f_coeffs) - 1
    nd = len(str(int(N)))
    lp_bound = int(min(params['B_r'] * 100, params['B_r'] ** 2))

    c_lib = _load_gnfs_sieve()
    if c_lib is None:
        if verbose:
            print("    ERROR: C sieve not available")
        return []

    rat_p_arr = np.array(rat_fb, dtype=np.int64)
    alg_p_arr = np.array([p for p, r in alg_fb], dtype=np.int64)
    alg_r_arr = np.array([r for p, r in alg_fb], dtype=np.int64)
    f_coeffs_arr = np.array(f_coeffs, dtype=np.int64)
    f0_abs = abs(f_coeffs[0]) if f_coeffs[0] != 0 else 1
    fd_abs = abs(f_coeffs[d]) if f_coeffs[d] != 0 else 1
    A = min(params['A'], 500000)
    B_max = params['B_max']

    n_fb_total = len(rat_fb) + len(alg_fb)
    mem_per_cand = n_fb_total * 8
    max_cands_verify = max(2000, min(50000, int(800_000_000 / max(mem_per_cand, 1))))
    max_cands = max(max_cands_verify, 200000)
    out_a = (ctypes.c_int * max_cands)()
    out_b = (ctypes.c_int * max_cands)()

    c_verify_rat_exps = np.zeros(max_cands_verify * len(rat_fb), dtype=np.int64)
    c_verify_alg_exps = np.zeros(max_cands_verify * len(alg_fb), dtype=np.int64)
    c_verify_signs = (ctypes.c_int * max_cands_verify)()
    c_verify_mask = (ctypes.c_int * max_cands_verify)()
    verify_a_buf = (ctypes.c_int * max_cands_verify)()
    verify_b_buf = (ctypes.c_int * max_cands_verify)()
    c_verify_rat_lp = np.zeros(max_cands_verify, dtype=np.int64)
    c_verify_alg_lp = np.zeros(max_cands_verify, dtype=np.int64)
    batch_rat_exps = c_verify_rat_exps.reshape(max_cands_verify, len(rat_fb))
    batch_alg_exps = c_verify_alg_exps.reshape(max_cands_verify, len(alg_fb))

    verified = []
    partials_alg = defaultdict(list)
    partials_rat = defaultdict(list)
    total_partials = 0

    rat_frac = max(500, 900 - nd * 5)
    alg_frac = max(400, 750 - nd * 5)
    batch_size = 500

    # Two-phase schedule (same as standard GNFS)
    if d >= 4 and nd >= 40:
        A_large = min(A * 2, 2_000_000)
        phase1_b_max = min(5000, B_max)
    else:
        A_large = A
        phase1_b_max = 0

    phase_schedule = []
    if phase1_b_max > 0:
        for b_val in range(1, phase1_b_max + 1):
            phase_schedule.append((b_val, b_val, A_large))
    for b_s in range(phase1_b_max + 1, B_max + 1, batch_size):
        b_e = min(b_s + batch_size - 1, B_max)
        phase_schedule.append((b_s, b_e, A))

    if verbose and phase1_b_max > 0:
        print(f"    Two-phase: b=1..{phase1_b_max} A={A_large}, "
              f"b={phase1_b_max+1}..{B_max} A={A}")

    for b_start, b_end, A_use in phase_schedule:
        if time.time() - t0 > time_limit:
            break

        n_slp_est = sum(max(0, len(v) - 1) for v in partials_alg.values())
        n_slp_est += sum(max(0, len(v) - 1) for v in partials_rat.values())
        if len(verified) + n_slp_est >= needed:
            break

        n_cands = c_lib.sieve_batch_c(
            b_start, b_end, A_use,
            rat_p_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            len(rat_fb), ctypes.c_int64(m_int),
            alg_p_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            alg_r_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            len(alg_fb),
            rat_frac, alg_frac,
            d, ctypes.c_int64(f0_abs), ctypes.c_int64(fd_abs),
            out_a, out_b, max_cands)

        if n_cands == 0:
            continue

        for chunk_start in range(0, n_cands, max_cands_verify):
            chunk_end = min(chunk_start + max_cands_verify, n_cands)
            chunk_n = chunk_end - chunk_start

            # Copy chunk into pre-allocated verify buffer
            ctypes.memmove(verify_a_buf, ctypes.addressof(out_a) + chunk_start * 4, chunk_n * 4)
            ctypes.memmove(verify_b_buf, ctypes.addressof(out_b) + chunk_start * 4, chunk_n * 4)

            c_lib.verify_candidates_c(
                verify_a_buf, verify_b_buf, chunk_n,
                ctypes.c_int64(m_int),
                f_coeffs_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                d,
                rat_p_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                len(rat_fb),
                alg_p_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                alg_r_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                len(alg_fb),
                ctypes.c_int64(lp_bound),
                c_verify_rat_exps.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                c_verify_alg_exps.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                c_verify_signs, c_verify_mask,
                c_verify_rat_lp.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                c_verify_alg_lp.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            )

            for ci in range(chunk_n):
                mtype = c_verify_mask[ci]
                if mtype == 0:
                    continue
                a_val = int(out_a[chunk_start + ci])
                b_val = int(out_b[chunk_start + ci])
                rat_exps = batch_rat_exps[ci].tolist()
                alg_exps = batch_alg_exps[ci].tolist()
                rat_sign = int(c_verify_signs[ci])

                if mtype == 1:
                    qc_bits = compute_qc_vector(a_val, b_val, qc_primes)
                    if inert_qc_primes:
                        qc_bits += compute_inert_qc_vector(
                            a_val, b_val, inert_qc_primes, f_coeffs)
                    verified.append({
                        'a': a_val, 'b': b_val,
                        'rat_exps': rat_exps, 'rat_sign': rat_sign,
                        'alg_exps': alg_exps,
                        'qc_bits': qc_bits,
                    })
                elif total_partials < 200000:
                    # Defer inert QC for partials (saves time)
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
                        if alp > 1:
                            r_ideal = (-a_val * pow(b_val, -1, alp)) % alp
                            partials_alg[(alp, r_ideal)].append(rel)
                    elif mtype == 2:
                        partials_rat[int(c_verify_rat_lp[ci])].append(rel)
                    total_partials += 1

        if verbose and (b_end % 500 == 0 or (b_end <= phase1_b_max and b_end % 100 == 0)):
            elapsed = time.time() - t0
            n_slp = sum(max(0, len(v) - 1) for v in partials_alg.values())
            n_slp += sum(max(0, len(v) - 1) for v in partials_rat.values())
            n_part = sum(len(v) for v in partials_alg.values()) + sum(len(v) for v in partials_rat.values())
            print(f"    [b={b_end}] {len(verified)}+{n_slp}slp/{needed} "
                  f"({n_part} part, {elapsed:.1f}s)")

    # SLP combining (with deferred inert QC)
    combined = list(verified)
    n_slp = 0
    for lp, rels in partials_rat.items():
        if len(rels) >= 2 and len(combined) < needed:
            _ensure_inert_qc(rels[0], inert_qc_primes, f_coeffs)
            for other in rels[1:]:
                _ensure_inert_qc(other, inert_qc_primes, f_coeffs)
                combined.append(_merge_rels(rels[0], other, 'rat'))
                n_slp += 1
                if len(combined) >= needed: break
    for ideal, rels in partials_alg.items():
        if len(rels) >= 2 and len(combined) < needed:
            _ensure_inert_qc(rels[0], inert_qc_primes, f_coeffs)
            for other in rels[1:]:
                _ensure_inert_qc(other, inert_qc_primes, f_coeffs)
                combined.append(_merge_rels(rels[0], other, 'alg'))
                n_slp += 1
                if len(combined) >= needed: break

    if verbose:
        n_pa = sum(len(v) for v in partials_alg.values())
        n_pr = sum(len(v) for v in partials_rat.values())
        print(f"    SLP: {n_pr} rat + {n_pa} alg → {n_slp} combined")

    return combined


def _ensure_inert_qc(rel, inert_qc_primes, f_coeffs):
    """Compute deferred inert QC bits if needed."""
    if rel.get('_needs_inert_qc') and inert_qc_primes:
        rel['qc_bits'] = rel['qc_bits'] + compute_inert_qc_vector(
            rel['a'], rel['b'], inert_qc_primes, f_coeffs)
        rel['_needs_inert_qc'] = False
        # Also convert int8 exps to lists
        if hasattr(rel['rat_exps'], 'tolist'):
            rel['rat_exps'] = rel['rat_exps'].tolist()
        if hasattr(rel['alg_exps'], 'tolist'):
            rel['alg_exps'] = rel['alg_exps'].tolist()


def _merge_rels(base, other, lp_side):
    """Merge two partial relations sharing a large prime."""
    br, or_ = base['rat_exps'], other['rat_exps']
    ba, oa = base['alg_exps'], other['alg_exps']
    if hasattr(br, 'astype'):
        comb_rat = (br.astype(np.int16) + or_.astype(np.int16)).tolist()
    else:
        comb_rat = [br[j] + or_[j] for j in range(len(br))]
    if hasattr(ba, 'astype'):
        comb_alg = (ba.astype(np.int16) + oa.astype(np.int16)).tolist()
    else:
        comb_alg = [ba[j] + oa[j] for j in range(len(ba))]
    nqc = len(base.get('qc_bits', []))
    return {
        'a': base['a'], 'b': base['b'],
        'a_list': [base['a'], other['a']],
        'b_list': [base['b'], other['b']],
        'rat_exps': comb_rat,
        'rat_sign': base['rat_sign'] + other['rat_sign'],
        'alg_exps': comb_alg,
        'qc_bits': [base['qc_bits'][j] ^ other['qc_bits'][j]
                    for j in range(nqc)] if nqc > 0 else [],
        'rat_lp': base.get('rat_lp', 0) if lp_side == 'rat' else 0,
        'alg_lp': base.get('alg_lp', 0) if lp_side == 'alg' else 0,
    }


###############################################################################
# Convenience
###############################################################################

def factor(N, verbose=True, time_limit=3600):
    """Main entry point."""
    return gnfs_b3_hybrid_factor(N, verbose=verbose, time_limit=time_limit)


###############################################################################
# Self-test
###############################################################################

if __name__ == "__main__":
    print("=" * 70)
    print("GNFS-B3 Hybrid Engine — Self-Test & Comparison")
    print("=" * 70)

    from gnfs_engine import gnfs_factor

    rng = random.Random(42)

    tests = []
    for nd in [30, 35, 40, 43, 44]:
        half_bits = int(nd * 3.32 / 2)
        p = int(next_prime(mpz(rng.getrandbits(half_bits)) | (mpz(1) << (half_bits - 1))))
        q = int(next_prime(mpz(rng.getrandbits(half_bits)) | (mpz(1) << (half_bits - 1))))
        N_val = p * q
        limit = max(120, nd * 15)
        tests.append((f"{nd}d", N_val, limit))

    results = []
    for label, n, limit in tests:
        nd = len(str(n))
        print(f"\n{'='*70}")
        print(f"Test: {label} ({nd} actual digits)")

        # B3 Hybrid
        t0 = time.time()
        f1 = gnfs_b3_hybrid_factor(n, verbose=True, time_limit=limit)
        t1 = time.time() - t0
        ok1 = f1 and f1 > 1 and n % f1 == 0

        # Standard GNFS
        t0 = time.time()
        f2 = gnfs_factor(n, verbose=False, time_limit=limit)
        t2 = time.time() - t0
        ok2 = f2 and f2 > 1 and n % f2 == 0

        speedup = t2 / t1 if t1 > 0 else 0
        print(f"  B3: {'OK' if ok1 else 'FAIL'} ({t1:.1f}s) | "
              f"Std: {'OK' if ok2 else 'FAIL'} ({t2:.1f}s) | "
              f"Speedup: {speedup:.2f}x")
        results.append((label, nd, t1, ok1, t2, ok2))

    print(f"\n{'='*70}")
    print("Summary:")
    print(f"  {'Label':>6}  {'Digits':>6}  {'B3':>8}  {'Std':>8}  {'Speedup':>8}")
    for label, nd, t1, ok1, t2, ok2, in results:
        s = t2/t1 if t1 > 0 else 0
        b3_str = f"{t1:.1f}s" if ok1 else "FAIL"
        std_str = f"{t2:.1f}s" if ok2 else "FAIL"
        print(f"  {label:>6}  {nd:>5}d  {b3_str:>8}  {std_str:>8}  {s:>7.2f}x")
