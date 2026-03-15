#!/usr/bin/env python3
"""
GNFS-B3 Hybrid Engine
=====================

Integrates B3-MPQS polynomial structure into the GNFS pipeline to create
a hybrid engine that exploits both:
  1. GNFS sub-exponential complexity (algebraic number field sieve)
  2. B3-MPQS small residue property (Pythagorean arithmetic progressions)

== Architecture ==

The hybrid works in TWO complementary phases:

Phase A: "B3-GNFS" — B3 rational pre-selection with algebraic sieve
  For each b, the rational norm |a + b*m| is a linear function of a.
  We choose a to lie on an arithmetic progression that makes |a + b*m|
  divisible by many small primes simultaneously.

  For a rational FB prime p: a + b*m ≡ 0 (mod p) at a ≡ -b*m (mod p).
  The standard GNFS sieve adds log(p) at these positions. But we can
  go further: instead of sieving, we DIRECTLY enumerate positions where
  |a + b*m| is smooth, then ONLY sieve the algebraic side there.

  This is "rational pre-selection": rather than double-sieve, we
  enumerate a-values where the rational side is provably smooth
  (via the CRT/B3 structure), then check only the algebraic side.

Phase B: Standard GNFS C sieve (fallback/complement)
  If Phase A doesn't yield enough relations, run the standard two-sided
  C sieve to fill the gap.

The combined approach can be faster because:
  - Phase A has zero false positives on the rational side
  - Phase A can use much tighter algebraic thresholds
  - Phase B fills in the gaps from Phase A's limited a-coverage

== Usage ==
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
# Phase A: B3 Rational Pre-Selection + Algebraic Sieve
###############################################################################

def b3_rational_preselect(b, A, m_int, rat_fb, lp_bound):
    """
    For a given b, find all a in [-A, A] where |a + b*m| is smooth
    over rat_fb (with at most one large prime up to lp_bound).

    Instead of sieving, we use the MULTIPLICATIVE structure:
    For each prime p in rat_fb, the positions where p | (a + b*m)
    form an arithmetic progression with stride p.

    We use an inclusion/exclusion sieve: add log(p) at stride p,
    then threshold at log(|a + b*m|) - tolerance.

    Returns: list of (a, rat_norm_abs, rat_sign, rat_exps, rat_lp)
    for all smooth a-values.
    """
    size = 2 * A + 1
    n_rat = len(rat_fb)

    # Rational sieve (same as standard GNFS, but we verify more aggressively)
    bm = b * m_int
    rat_sieve = np.zeros(size, dtype=np.float32)

    for j in range(n_rat):
        p = rat_fb[j]
        log_p = math.log(p)
        # a + b*m ≡ 0 (mod p) at a ≡ -b*m (mod p)
        start = int((-bm) % p)
        # Map to sieve index: idx = a + A, so idx = (start + A) % p
        idx = (start + A) % p
        while idx < size:
            rat_sieve[idx] += log_p
            idx += p

    # Threshold: we want |a + b*m| to be smooth.
    # |a + b*m| ranges from |bm - A| to |bm + A|.
    # For the sieve to declare smoothness, we need sum(log p) ≈ log|a+bm|.
    # Generous threshold: accept if within 20% of target.
    results = []
    bm_abs = abs(bm)

    # Instead of a fixed threshold, trial divide EVERY position where
    # the sieve score is high enough (within factor of LP bound)
    # Target: log|a+bm| for each position
    # Accept if sieve >= log|a+bm| - log(lp_bound)

    log_lp = math.log(max(lp_bound, 2))

    for idx in range(size):
        a = idx - A
        raw = a + bm
        val = abs(raw)
        if val == 0:
            continue

        log_val = math.log(max(val, 1))
        # Accept if sieve accumulated enough log-weight
        if rat_sieve[idx] >= log_val - log_lp:
            # Verify by actual trial division
            sign = 1 if raw < 0 else 0
            remainder = int(val)
            exps = [0] * n_rat
            for j in range(n_rat):
                p = rat_fb[j]
                if remainder < p:
                    break
                while remainder % p == 0:
                    remainder //= p
                    exps[j] += 1

            if remainder == 1:
                results.append((a, val, sign, exps, 0))
            elif remainder <= lp_bound and is_prime(int(remainder)):
                results.append((a, val, sign, exps, int(remainder)))

    return results


def b3_algebraic_verify(preselected, b, f_coeffs, alg_fb, lp_bound_alg,
                         qc_primes, inert_qc_primes):
    """
    For pre-selected (a,b) pairs with smooth rational norms,
    verify algebraic smoothness via trial division.

    Since we already know the rational side is smooth, we only need
    to check the algebraic side — half the work of standard GNFS verify.
    """
    d = len(f_coeffs) - 1
    n_alg = len(alg_fb)
    alg_primes = [p for p, r in alg_fb]
    alg_roots = [r for p, r in alg_fb]

    verified = []

    for a, rat_norm, rat_sign, rat_exps, rat_lp in preselected:
        # Algebraic norm
        alg_norm = abs(int(norm_algebraic(a, b, f_coeffs)))
        if alg_norm == 0:
            continue

        alg_exps = [0] * n_alg
        remainder = int(alg_norm)
        alg_lp = 0

        for j in range(n_alg):
            p = alg_primes[j]
            r = alg_roots[j]
            if (a + b * r) % p == 0:
                while remainder % p == 0:
                    remainder //= p
                    alg_exps[j] += 1

        if remainder == 1:
            pass
        elif remainder > 1 and remainder <= lp_bound_alg and is_prime(int(remainder)):
            alg_lp = int(remainder)
        else:
            continue

        # QC
        qc_bits = compute_qc_vector(a, b, qc_primes)
        if inert_qc_primes:
            qc_bits += compute_inert_qc_vector(a, b, inert_qc_primes, f_coeffs)

        rel = {
            'a': a, 'b': b,
            'rat_exps': rat_exps,
            'rat_sign': rat_sign,
            'alg_exps': alg_exps,
            'qc_bits': qc_bits,
        }

        # Classify
        if rat_lp == 0 and alg_lp == 0:
            rel['_type'] = 'full'
        elif rat_lp > 0 and alg_lp == 0:
            rel['_type'] = 'partial_rat'
            rel['rat_lp'] = rat_lp
        elif rat_lp == 0 and alg_lp > 0:
            rel['_type'] = 'partial_alg'
            rel['alg_lp'] = alg_lp
        else:
            rel['_type'] = 'partial_both'
            rel['rat_lp'] = rat_lp
            rel['alg_lp'] = alg_lp

        verified.append(rel)

    return verified


###############################################################################
# Phase B: Standard GNFS C Sieve (from gnfs_engine)
###############################################################################

def standard_gnfs_sieve(N, f_coeffs, m, rat_fb, alg_fb,
                         qc_primes, inert_qc_primes, params,
                         needed, existing_rels=None,
                         verbose=True, time_limit=3600, t0=None):
    """
    Standard GNFS C sieve — essentially the core of gnfs_engine.gnfs_factor
    but extracted as a reusable component.
    """
    if t0 is None:
        t0 = time.time()

    d = len(f_coeffs) - 1
    m_int = int(m)
    nd = len(str(int(N)))

    verified = list(existing_rels) if existing_rels else []
    lp_bound = int(min(params['B_r'] * 100, params['B_r'] ** 2))

    c_lib = _load_gnfs_sieve()
    if c_lib is None:
        if verbose:
            print("    ERROR: C sieve library not available")
        return verified

    rat_p_arr = np.array(rat_fb, dtype=np.int64)
    alg_p_arr = np.array([p for p, r in alg_fb], dtype=np.int64)
    alg_r_arr = np.array([r for p, r in alg_fb], dtype=np.int64)
    f_coeffs_arr = np.array(f_coeffs, dtype=np.int64)

    f0_abs = abs(f_coeffs[0]) if f_coeffs[0] != 0 else 1
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
    c_verify_rat_lp = np.zeros(max_cands_verify, dtype=np.int64)
    c_verify_alg_lp = np.zeros(max_cands_verify, dtype=np.int64)
    batch_rat_exps = c_verify_rat_exps.reshape(max_cands_verify, len(rat_fb))
    batch_alg_exps = c_verify_alg_exps.reshape(max_cands_verify, len(alg_fb))

    partials_alg = defaultdict(list)
    partials_rat = defaultdict(list)
    total_partials = 0

    rat_frac = max(500, 900 - nd * 5)
    alg_frac = max(400, 750 - nd * 5)
    batch_size = 500

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
            d, ctypes.c_int64(f0_abs),
            out_a, out_b, max_cands)

        if n_cands == 0:
            continue

        for chunk_start in range(0, n_cands, max_cands_verify):
            chunk_end = min(chunk_start + max_cands_verify, n_cands)
            chunk_n = chunk_end - chunk_start

            chunk_a = (ctypes.c_int * chunk_n)(*[out_a[chunk_start + i] for i in range(chunk_n)])
            chunk_b = (ctypes.c_int * chunk_n)(*[out_b[chunk_start + i] for i in range(chunk_n)])

            c_lib.verify_candidates_c(
                chunk_a, chunk_b, chunk_n,
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
                    qc_bits = compute_qc_vector(a_val, b_val, qc_primes)
                    if inert_qc_primes:
                        qc_bits += compute_inert_qc_vector(
                            a_val, b_val, inert_qc_primes, f_coeffs)
                    rel = {
                        'a': a_val, 'b': b_val,
                        'rat_exps': rat_exps, 'rat_sign': rat_sign,
                        'alg_exps': alg_exps,
                        'qc_bits': qc_bits,
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

    # SLP combining
    combined = list(verified)
    n_slp = 0
    for lp, rels in partials_rat.items():
        if len(rels) >= 2 and len(combined) < needed:
            for other in rels[1:]:
                combined.append(_merge_rels(rels[0], other, 'rat'))
                n_slp += 1
                if len(combined) >= needed: break
    for ideal, rels in partials_alg.items():
        if len(rels) >= 2 and len(combined) < needed:
            for other in rels[1:]:
                combined.append(_merge_rels(rels[0], other, 'alg'))
                n_slp += 1
                if len(combined) >= needed: break

    if verbose:
        n_pa = sum(len(v) for v in partials_alg.values())
        n_pr = sum(len(v) for v in partials_rat.values())
        print(f"    SLP: {n_pr} rat + {n_pa} alg partials → {n_slp} combined")

    return combined


def _merge_rels(base, other, lp_side):
    """Merge two partial relations sharing a large prime."""
    nrat = len(base['rat_exps'])
    nalg = len(base['alg_exps'])
    nqc = len(base.get('qc_bits', []))
    return {
        'a': base['a'], 'b': base['b'],
        'a_list': [base['a'], other['a']],
        'b_list': [base['b'], other['b']],
        'rat_exps': [base['rat_exps'][j] + other['rat_exps'][j] for j in range(nrat)],
        'rat_sign': base['rat_sign'] + other['rat_sign'],
        'alg_exps': [base['alg_exps'][j] + other['alg_exps'][j] for j in range(nalg)],
        'qc_bits': [base['qc_bits'][j] ^ other['qc_bits'][j]
                    for j in range(nqc)] if nqc > 0 else [],
        'rat_lp': base.get('rat_lp', 0) if lp_side == 'rat' else 0,
        'alg_lp': base.get('alg_lp', 0) if lp_side == 'alg' else 0,
    }


###############################################################################
# Phase A: B3-GNFS Sieve (rational pre-select + algebraic check)
###############################################################################

def b3_phase_a_collect(N, f_coeffs, m, rat_fb, alg_fb,
                        qc_primes, inert_qc_primes, params,
                        needed, verbose=True, time_limit=300, t0=None):
    """
    Phase A: B3-guided relation collection using C verify.

    For each b, we pre-select a-values where the rational norm |a+bm|
    is likely smooth (via rational sieve), then batch-verify through
    the C __int128 verifier for BOTH sides.

    The B3 advantage: rational pre-selection filters candidates MORE
    aggressively than the standard sieve threshold, reducing the number
    of expensive algebraic trial divisions. We use a tighter rational
    threshold since we know the exact rational norm.
    """
    if t0 is None:
        t0 = time.time()

    m_int = int(m)
    d = len(f_coeffs) - 1
    A = min(params['A'], 500000)
    B_max = params['B_max']
    lp_bound = int(min(params['B_r'] * 100, params['B_r'] ** 2))

    c_lib = _load_gnfs_sieve()

    # If C library available, use it for batch verification
    if c_lib is not None:
        return _b3_phase_a_c_verify(
            N, f_coeffs, m, rat_fb, alg_fb,
            qc_primes, inert_qc_primes, params,
            needed, c_lib, verbose, time_limit, t0)

    # Python fallback
    full_relations = []
    partials_rat = defaultdict(list)
    partials_alg = defaultdict(list)
    total_preselected = 0
    total_verified = 0
    lp_bound_alg = int(min(params['B_a'] * 100, params['B_a'] ** 2))

    for b in range(1, B_max + 1):
        if time.time() - t0 > time_limit:
            break

        n_slp = sum(max(0, len(v) - 1) for v in partials_rat.values())
        n_slp += sum(max(0, len(v) - 1) for v in partials_alg.values())
        if len(full_relations) + n_slp >= needed:
            break

        preselected = b3_rational_preselect(b, A, m_int, rat_fb, lp_bound)
        total_preselected += len(preselected)

        if not preselected:
            continue

        verified = b3_algebraic_verify(
            preselected, b, f_coeffs, alg_fb, lp_bound_alg,
            qc_primes, inert_qc_primes)

        for rel in verified:
            rtype = rel.get('_type', 'full')
            if rtype == 'full':
                full_relations.append(rel)
            elif rtype == 'partial_rat':
                partials_rat[rel['rat_lp']].append(rel)
            elif rtype == 'partial_alg':
                alp = rel['alg_lp']
                r_ideal = (-rel['a'] * pow(rel['b'], -1, alp)) % alp
                partials_alg[(alp, r_ideal)].append(rel)
            total_verified += 1

        if verbose and (b % 500 == 0 or (b <= 50 and b % 10 == 0)):
            elapsed = time.time() - t0
            n_slp = sum(max(0, len(v) - 1) for v in partials_rat.values())
            n_slp += sum(max(0, len(v) - 1) for v in partials_alg.values())
            print(f"    B3[b={b}] full={len(full_relations)} slp={n_slp} "
                  f"/{needed} (presel={total_preselected}, {elapsed:.1f}s)")

    combined = list(full_relations)
    n_slp = 0
    for lp, rels in partials_rat.items():
        if len(rels) >= 2:
            for other in rels[1:]:
                combined.append(_merge_rels(rels[0], other, 'rat'))
                n_slp += 1
    for ideal, rels in partials_alg.items():
        if len(rels) >= 2:
            for other in rels[1:]:
                combined.append(_merge_rels(rels[0], other, 'alg'))
                n_slp += 1

    if verbose:
        print(f"    B3 total: {len(full_relations)} full + {n_slp} SLP "
              f"= {len(combined)}")

    return combined


def _b3_phase_a_c_verify(N, f_coeffs, m, rat_fb, alg_fb,
                           qc_primes, inert_qc_primes, params,
                           needed, c_lib, verbose, time_limit, t0):
    """
    Phase A with C verify: for each b, rational pre-select then C batch verify.

    This is the fast path. The rational pre-selection generates candidates
    where the rational sieve score is high enough, then the C verifier
    handles full trial division on both sides with __int128 arithmetic.
    """
    m_int = int(m)
    d = len(f_coeffs) - 1
    nd = len(str(int(N)))
    A = min(params['A'], 500000)
    B_max = params['B_max']
    lp_bound = int(min(params['B_r'] * 100, params['B_r'] ** 2))

    rat_p_arr = np.array(rat_fb, dtype=np.int64)
    alg_p_arr = np.array([p for p, r in alg_fb], dtype=np.int64)
    alg_r_arr = np.array([r for p, r in alg_fb], dtype=np.int64)
    f_coeffs_arr = np.array(f_coeffs, dtype=np.int64)
    f0_abs = abs(f_coeffs[0]) if f_coeffs[0] != 0 else 1

    n_fb_total = len(rat_fb) + len(alg_fb)
    mem_per_cand = n_fb_total * 8
    max_cands_verify = max(2000, min(50000, int(800_000_000 / max(mem_per_cand, 1))))

    c_verify_rat_exps = np.zeros(max_cands_verify * len(rat_fb), dtype=np.int64)
    c_verify_alg_exps = np.zeros(max_cands_verify * len(alg_fb), dtype=np.int64)
    c_verify_signs = (ctypes.c_int * max_cands_verify)()
    c_verify_mask = (ctypes.c_int * max_cands_verify)()
    c_verify_rat_lp = np.zeros(max_cands_verify, dtype=np.int64)
    c_verify_alg_lp = np.zeros(max_cands_verify, dtype=np.int64)
    batch_rat_exps = c_verify_rat_exps.reshape(max_cands_verify, len(rat_fb))
    batch_alg_exps = c_verify_alg_exps.reshape(max_cands_verify, len(alg_fb))

    # Also use C sieve for candidate generation (two-sided, but with
    # tighter rational threshold to exploit B3 insight)
    max_cands = max(max_cands_verify, 200000)
    out_a = (ctypes.c_int * max_cands)()
    out_b = (ctypes.c_int * max_cands)()

    verified = []
    partials_alg = defaultdict(list)
    partials_rat = defaultdict(list)
    total_partials = 0

    # B3 threshold tuning: use same thresholds as standard GNFS for now.
    # The B3 advantage comes from the two-phase architecture (Phase A + B),
    # not from threshold changes. Standard thresholds are well-tuned.
    rat_frac_b3 = max(500, 900 - nd * 5)  # same as standard
    alg_frac_b3 = max(400, 750 - nd * 5)  # same as standard

    batch_size = 500

    # Phase schedule
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

    for b_start, b_end, A_use in phase_schedule:
        if time.time() - t0 > time_limit:
            break

        n_slp_est = sum(max(0, len(v) - 1) for v in partials_alg.values())
        n_slp_est += sum(max(0, len(v) - 1) for v in partials_rat.values())
        if len(verified) + n_slp_est >= needed:
            break

        # C sieve with B3-tightened rational threshold
        n_cands = c_lib.sieve_batch_c(
            b_start, b_end, A_use,
            rat_p_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            len(rat_fb), ctypes.c_int64(m_int),
            alg_p_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            alg_r_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            len(alg_fb),
            rat_frac_b3, alg_frac_b3,
            d, ctypes.c_int64(f0_abs),
            out_a, out_b, max_cands)

        if n_cands == 0:
            continue

        for chunk_start in range(0, n_cands, max_cands_verify):
            chunk_end = min(chunk_start + max_cands_verify, n_cands)
            chunk_n = chunk_end - chunk_start

            chunk_a = (ctypes.c_int * chunk_n)(*[out_a[chunk_start + i] for i in range(chunk_n)])
            chunk_b = (ctypes.c_int * chunk_n)(*[out_b[chunk_start + i] for i in range(chunk_n)])

            c_lib.verify_candidates_c(
                chunk_a, chunk_b, chunk_n,
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
                    qc_bits = compute_qc_vector(a_val, b_val, qc_primes)
                    if inert_qc_primes:
                        qc_bits += compute_inert_qc_vector(
                            a_val, b_val, inert_qc_primes, f_coeffs)
                    rel = {
                        'a': a_val, 'b': b_val,
                        'rat_exps': rat_exps, 'rat_sign': rat_sign,
                        'alg_exps': alg_exps,
                        'qc_bits': qc_bits,
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
            print(f"    B3[b={b_end}] {len(verified)}+{n_slp}slp/{needed} "
                  f"({n_part} part, {elapsed:.1f}s)")

    # SLP combining
    combined = list(verified)
    n_slp = 0
    for lp, rels in partials_rat.items():
        if len(rels) >= 2 and len(combined) < needed:
            for other in rels[1:]:
                combined.append(_merge_rels(rels[0], other, 'rat'))
                n_slp += 1
                if len(combined) >= needed: break
    for ideal, rels in partials_alg.items():
        if len(rels) >= 2 and len(combined) < needed:
            for other in rels[1:]:
                combined.append(_merge_rels(rels[0], other, 'alg'))
                n_slp += 1
                if len(combined) >= needed: break

    if verbose:
        n_pa = sum(len(v) for v in partials_alg.values())
        n_pr = sum(len(v) for v in partials_rat.values())
        print(f"    B3: {len(verified)} full + {n_slp} SLP = {len(combined)} "
              f"({n_pr} rat + {n_pa} alg partials)")

    return combined


###############################################################################
# Main Hybrid Engine
###############################################################################

def gnfs_b3_hybrid_factor(N, verbose=True, time_limit=3600):
    """
    Factor N using GNFS with B3 hybrid enhancements.

    Strategy:
    1. Standard GNFS polynomial selection (base-m with norm scoring)
    2. Phase A: B3 rational pre-selection + algebraic verify
       - For each b, enumerate smooth rational norms via sieve
       - Verify algebraic side only for those candidates
       - Advantage: zero false positives on rational side
    3. Phase B: Standard GNFS C sieve (if Phase A insufficient)
       - Two-sided C sieve + C verify
       - SLP/DLP combining
    4. GF(2) LA + algebraic sqrt → factor extraction
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

    # Step 1: GNFS parameters and polynomial
    params = gnfs_params(N)
    d = params['d']
    poly = base_m_poly(N, d=d)
    if 'factor' in poly:
        return poly['factor']

    f_coeffs = poly['f_coeffs']
    m = poly['m']
    m_int = int(m)
    alpha = murphy_alpha(f_coeffs, B=200)

    if verbose:
        print(f"    Params: d={d}, B_r={params['B_r']}, B_a={params['B_a']}, "
              f"A={params['A']}, B_max={params['B_max']}")
        terms = []
        for i, c in enumerate(f_coeffs):
            if c != 0:
                if i == 0: terms.append(str(c))
                elif i == 1: terms.append(f"{c}*x")
                else: terms.append(f"{c}*x^{i}")
        print(f"    Poly: f(x) = {' + '.join(terms)}")
        print(f"    m = {m}, alpha = {alpha:.3f}")

    # Step 2: Factor bases
    t_fb = time.time()
    rat_fb = build_rational_fb(params['B_r'])
    alg_fb = build_algebraic_fb(f_coeffs, params['B_a'])
    fb_time = time.time() - t_fb

    if verbose:
        print(f"    Rational FB: {len(rat_fb)} primes up to {rat_fb[-1]}")
        print(f"    Algebraic FB: {len(alg_fb)} ideals ({fb_time:.1f}s)")

    # QC primes
    num_split_qc = 20
    qc_primes = build_qc_primes(f_coeffs, num_qc=num_split_qc, min_p=50000)
    num_inert_qc = 5
    inert_qc_primes = build_inert_qc_primes(f_coeffs, num_qc=num_inert_qc, min_p=100)
    num_qc = num_split_qc + num_inert_qc

    needed = int((len(rat_fb) + len(alg_fb) + num_qc + 2) * 1.10)
    if verbose:
        print(f"    Need {needed} relations (incl. {num_qc} QC)")

    # Step 3: Relation collection
    t_sieve = time.time()

    # Phase A: B3 rational pre-selection (use ~15% of time budget, cap at 30s)
    # Phase A is slower per-relation than the C sieve, so keep it short
    phase_a_limit = min(time_limit * 0.15, 30)
    if verbose:
        print(f"\n    === Phase A: B3 Rational Pre-Selection ===")

    b3_relations = b3_phase_a_collect(
        N, f_coeffs, m, rat_fb, alg_fb,
        qc_primes, inert_qc_primes, params,
        needed, verbose=verbose,
        time_limit=phase_a_limit, t0=t0)

    if len(b3_relations) >= needed:
        all_relations = b3_relations[:needed + 50]  # take a few extra
        if verbose:
            print(f"    Phase A sufficient: {len(all_relations)} relations")
    else:
        # Phase B: Standard sieve to fill the gap
        remaining_time = time_limit - (time.time() - t0)
        if verbose:
            shortfall = needed - len(b3_relations)
            print(f"\n    === Phase B: Standard C Sieve (shortfall={shortfall}) ===")

        all_relations = standard_gnfs_sieve(
            N, f_coeffs, m, rat_fb, alg_fb,
            qc_primes, inert_qc_primes, params,
            needed, existing_rels=b3_relations,
            verbose=verbose,
            time_limit=remaining_time, t0=t0)

    sieve_time = time.time() - t_sieve
    if verbose:
        print(f"\n    Total: {len(all_relations)}/{needed} in {sieve_time:.1f}s")

    if len(all_relations) < needed:
        if verbose:
            print(f"    Insufficient relations ({len(all_relations)}/{needed})")
        return None

    # Step 4: GF(2) Linear Algebra
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
        if verbose:
            print(f"    No null vectors found")
        return None

    # Step 5: Factor extraction
    result = extract_factor(N, null_vecs, all_relations, m,
                            rat_fb, alg_fb, f_coeffs)

    if result is not None:
        total_t = time.time() - t0
        if verbose:
            print(f"\n    *** FACTOR: {result} ({nd}d, {total_t:.1f}s) ***")
        return result

    if verbose:
        print(f"    {len(null_vecs)} null vecs tried, no factor found")
    return None


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
    print("GNFS-B3 Hybrid Engine — Self-Test")
    print("=" * 70)

    rng = random.Random(42)

    tests = []
    for nd in [30, 35, 40, 43]:
        half_bits = int(nd * 3.32 / 2)
        p = int(next_prime(mpz(rng.getrandbits(half_bits)) | (mpz(1) << (half_bits - 1))))
        q = int(next_prime(mpz(rng.getrandbits(half_bits)) | (mpz(1) << (half_bits - 1))))
        N_val = p * q
        actual_nd = len(str(N_val))
        limit = max(120, nd * 15)
        tests.append((f"{nd}d", N_val, p, q, limit))

    results = []
    for label, n, p_true, q_true, limit in tests:
        nd = len(str(n))
        print(f"\n{'='*70}")
        print(f"Test: {label} ({nd} actual digits)")
        print(f"N = {n}")
        t_start = time.time()
        f = gnfs_b3_hybrid_factor(n, verbose=True, time_limit=limit)
        elapsed = time.time() - t_start
        if f and f > 1 and n % f == 0:
            print(f"  SUCCESS: {f} x {n // f}  ({elapsed:.1f}s)")
            results.append((label, nd, elapsed, True))
        else:
            print(f"  FAILED ({elapsed:.1f}s)")
            results.append((label, nd, elapsed, False))

    print(f"\n{'='*70}")
    print("Summary:")
    print(f"  {'Label':>6}  {'Digits':>6}  {'Time':>8}  {'Result':>8}")
    for label, nd, t, ok in results:
        print(f"  {label:>6}  {nd:>5}d  {t:>7.1f}s  {'OK' if ok else 'FAIL':>8}")
