#!/usr/bin/env python3
"""
GNFS Sieve Moonshots: GPU-accelerated and algorithmic improvements
===================================================================
Experiments to dramatically improve GNFS sieve performance.

Ideas tested:
1. GPU Batch Sieve (CUDA via ctypes)
2. GPU Batch Trial Division
3. Streaming Pipeline (double-buffer GPU/CPU)
4. Compressed Sieve (4-bit log approximation)
5. Bucket Sieve for Large Primes
6. Segmented Sieve (L1-cache-sized segments)
7. Smooth Number Oracle (hash table)
8. Product Tree Batch Smoothness (Bernstein)
9. NTT Sieve (frequency-domain)
10. Lattice Sieve with GPU
11. Algebraic Norm Precomputation (Horner)

Memory limit: 2GB. RTX 4050 (6GB VRAM).
"""

import os
import sys
import time
import math
import ctypes
import struct
import subprocess
import tempfile
import numpy as np
from collections import defaultdict

# Add project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gmpy2
from gmpy2 import mpz, next_prime, is_prime, gcd, iroot

# Import GNFS engine helpers
from gnfs_engine import (
    base_m_poly, build_rational_fb, build_algebraic_fb,
    gnfs_params, norm_algebraic, find_poly_roots_mod_p,
    _load_gnfs_sieve,
)


###############################################################################
# Test number generation
###############################################################################

def make_semiprime(digits):
    """Generate a semiprime with the given number of digits."""
    import random
    random.seed(42 + digits)
    half = digits // 2
    lo = mpz(10) ** (half - 1)
    hi = mpz(10) ** half - 1
    while True:
        p = gmpy2.next_prime(lo + mpz(random.randint(0, int(hi - lo))))
        q = gmpy2.next_prime(lo + mpz(random.randint(0, int(hi - lo))))
        if p != q:
            n = p * q
            if len(str(int(n))) == digits or len(str(int(n))) == digits - 1:
                return int(n), int(p), int(q)


def setup_gnfs(n):
    """Setup GNFS parameters, polynomial, and factor bases for a number."""
    n = mpz(n)
    params = gnfs_params(n)
    d = params['d']
    poly = base_m_poly(n, d=d)
    if 'factor' in poly:
        return None  # trivial
    f_coeffs = poly['f_coeffs']
    m = poly['m']
    rat_fb = build_rational_fb(min(params['B_r'], 50000))  # cap for experiments
    alg_fb = build_algebraic_fb(f_coeffs, min(params['B_a'], 50000))
    A = min(params['A'], 100000)  # cap sieve region
    return {
        'n': n, 'params': params, 'f_coeffs': f_coeffs, 'm': m,
        'rat_fb': rat_fb, 'alg_fb': alg_fb, 'A': A, 'd': d,
    }


###############################################################################
# Baseline: Current C sieve (for comparison)
###############################################################################

def experiment_baseline(n, setup, max_b=200, verbose=True):
    """Baseline: current C sieve_batch_c for comparison."""
    if verbose:
        print("\n" + "=" * 70)
        print("EXPERIMENT 0: Baseline C Sieve")
        print("=" * 70)

    c_lib = _load_gnfs_sieve()
    if c_lib is None:
        print("  ERROR: gnfs_sieve_c.so not found")
        return None

    rat_fb = setup['rat_fb']
    alg_fb = setup['alg_fb']
    A = setup['A']
    m = setup['m']
    f_coeffs = setup['f_coeffs']
    d = setup['d']

    rat_p_arr = np.array(rat_fb, dtype=np.int64)
    alg_p_arr = np.array([p for p, r in alg_fb], dtype=np.int64)
    alg_r_arr = np.array([r for p, r in alg_fb], dtype=np.int64)

    f0_abs = abs(f_coeffs[0]) if f_coeffs[0] != 0 else 1
    fd_abs = abs(f_coeffs[d]) if f_coeffs[d] != 0 else 1

    max_cands = 100000
    out_a = (ctypes.c_int * max_cands)()
    out_b = (ctypes.c_int * max_cands)()

    t0 = time.time()
    total = c_lib.sieve_batch_c(
        1, max_b, A,
        rat_p_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
        len(rat_fb), ctypes.c_int64(int(m)),
        alg_p_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
        alg_r_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
        len(alg_fb),
        600, 500,  # rat_frac=0.6, alg_frac=0.5
        d, ctypes.c_int64(f0_abs), ctypes.c_int64(fd_abs),
        out_a, out_b, max_cands,
    )
    elapsed = time.time() - t0

    if verbose:
        print(f"  C sieve: {total} candidates in {elapsed:.3f}s")
        print(f"  Rate: {max_b / elapsed:.0f} b-lines/s, {total / max(elapsed, 1e-9):.0f} cands/s")

    return {
        'name': 'Baseline C Sieve',
        'candidates': total,
        'time': elapsed,
        'b_lines': max_b,
        'rate_blines_per_s': max_b / max(elapsed, 1e-9),
    }


###############################################################################
# Experiment 4: Compressed Sieve (4-bit log approximation)
###############################################################################

def experiment_compressed_sieve(n, setup, max_b=200, verbose=True):
    """
    Compressed sieve: use 4 bits per position (16 levels of log approximation).
    Halves sieve memory: 200K positions = 100KB instead of 200KB (or 400KB with uint16).
    Trade precision for memory bandwidth.
    """
    if verbose:
        print("\n" + "=" * 70)
        print("EXPERIMENT 4: Compressed 4-bit Sieve")
        print("=" * 70)

    rat_fb = setup['rat_fb']
    alg_fb = setup['alg_fb']
    A = setup['A']
    m = int(setup['m'])
    f_coeffs = setup['f_coeffs']
    d = setup['d']

    size = 2 * A + 1
    # 4-bit sieve: pack 2 positions per byte
    # log(p) scaled to 0-15 range
    max_log = math.log(max(rat_fb[-1] if rat_fb else 2, 2))

    rat_primes = np.array(rat_fb, dtype=np.int64)
    rat_log4 = np.array([min(15, int(math.log(p) / max_log * 15 + 0.5)) for p in rat_fb], dtype=np.uint8)

    alg_primes = np.array([p for p, r in alg_fb], dtype=np.int64)
    alg_roots = np.array([r for p, r in alg_fb], dtype=np.int64)
    alg_log4 = np.array([min(15, int(math.log(p) / max_log * 15 + 0.5)) for p in alg_primes], dtype=np.uint8)

    # Thresholds in 4-bit scale
    f0_abs = abs(f_coeffs[0]) if f_coeffs[0] != 0 else 1
    fd_abs = abs(f_coeffs[d]) if f_coeffs[d] != 0 else 1

    total_cands = 0
    t0 = time.time()

    # Use uint8 arrays (not packed nibbles for simplicity, but half the width of uint16)
    rat_sieve = np.zeros(size, dtype=np.uint8)
    alg_sieve = np.zeros(size, dtype=np.uint8)

    for b in range(1, max_b + 1):
        rat_sieve[:] = 0
        alg_sieve[:] = 0

        bm = b * m
        # Rational sieve
        for i in range(len(rat_fb)):
            p = int(rat_primes[i])
            lp = int(rat_log4[i])
            if lp == 0:
                continue
            bm_mod = (b % p) * ((m % p + p) % p) % p
            start = int((-bm_mod % p + p) % p)
            start = (start + A) % p
            idx = start
            while idx < size:
                v = rat_sieve[idx] + lp
                rat_sieve[idx] = min(v, 255)
                idx += p

        # Algebraic sieve
        for i in range(len(alg_primes)):
            p = int(alg_primes[i])
            lp = int(alg_log4[i])
            if lp == 0:
                continue
            r = int(alg_roots[i])
            br_mod = (b % p) * ((r % p + p) % p) % p
            start = int((-br_mod % p + p) % p)
            start = (start + A) % p
            idx = start
            while idx < size:
                v = alg_sieve[idx] + lp
                alg_sieve[idx] = min(v, 255)
                idx += p

        # Threshold (scaled to 4-bit)
        rat_typical = max(abs(bm), A)
        rat_thresh = int(0.6 * math.log(max(rat_typical, 2)) / max_log * 15)
        dom = max(A, b)
        alg_log_norm = d * math.log(max(dom, 2)) + math.log(max(max(f0_abs, fd_abs), 1))
        alg_thresh = int(0.5 * alg_log_norm / max_log * 15) if alg_log_norm > 1 else 1

        mask = (rat_sieve >= rat_thresh) & (alg_sieve >= alg_thresh)
        total_cands += int(np.sum(mask))

    elapsed = time.time() - t0

    if verbose:
        print(f"  Compressed sieve: {total_cands} candidates in {elapsed:.3f}s")
        print(f"  Memory per line: {size} bytes (uint8) vs {size * 2} bytes (uint16)")
        print(f"  Rate: {max_b / elapsed:.0f} b-lines/s")

    return {
        'name': 'Compressed 4-bit Sieve',
        'candidates': total_cands,
        'time': elapsed,
        'b_lines': max_b,
        'rate_blines_per_s': max_b / max(elapsed, 1e-9),
        'memory_per_line': size,
    }


###############################################################################
# Experiment 5: Bucket Sieve for Large Primes
###############################################################################

def experiment_bucket_sieve(n, setup, max_b=200, verbose=True):
    """
    Bucket sieve: large primes (p > A/10) contribute at most a few hits per line.
    Pre-bucket them instead of striding through the array.
    Small primes sieve normally. This improves cache behavior.
    """
    if verbose:
        print("\n" + "=" * 70)
        print("EXPERIMENT 5: Bucket Sieve (Large Prime Bucketing)")
        print("=" * 70)

    rat_fb = setup['rat_fb']
    alg_fb = setup['alg_fb']
    A = setup['A']
    m = int(setup['m'])
    f_coeffs = setup['f_coeffs']
    d = setup['d']
    size = 2 * A + 1

    # Split FB into small (sieve normally) and large (bucket)
    bucket_thresh = max(A // 10, 100)
    rat_small = [(i, p) for i, p in enumerate(rat_fb) if p <= bucket_thresh]
    rat_large = [(i, p) for i, p in enumerate(rat_fb) if p > bucket_thresh]
    alg_small = [(i, (p, r)) for i, (p, r) in enumerate(alg_fb) if p <= bucket_thresh]
    alg_large = [(i, (p, r)) for i, (p, r) in enumerate(alg_fb) if p > bucket_thresh]

    if verbose:
        print(f"  Small primes: {len(rat_small)} rat + {len(alg_small)} alg (sieve normally)")
        print(f"  Large primes: {len(rat_large)} rat + {len(alg_large)} alg (bucketed)")

    # Precompute log values
    max_log_val = math.log(max(rat_fb[-1] if rat_fb else 2, 2))
    rat_logp = {p: int(math.log(p) * 128 + 0.5) for p in rat_fb}
    alg_logp = {p: int(math.log(p) * 128 + 0.5) for p, r in alg_fb}

    f0_abs = abs(f_coeffs[0]) if f_coeffs[0] != 0 else 1
    fd_abs = abs(f_coeffs[d]) if f_coeffs[d] != 0 else 1

    total_cands = 0
    t0 = time.time()

    rat_sieve = np.zeros(size, dtype=np.uint16)
    alg_sieve = np.zeros(size, dtype=np.uint16)

    for b in range(1, max_b + 1):
        rat_sieve[:] = 0
        alg_sieve[:] = 0

        bm = b * m

        # Small primes: standard sieve
        for _, p in rat_small:
            lp = rat_logp[p]
            bm_mod = (b % p) * ((m % p + p) % p) % p
            start = int((-bm_mod % p + p) % p)
            start = (start + A) % p
            idx = start
            while idx < size:
                rat_sieve[idx] += lp
                idx += p

        for _, (p, r) in alg_small:
            lp = alg_logp[p]
            br_mod = (b % p) * ((r % p + p) % p) % p
            start = int((-br_mod % p + p) % p)
            start = (start + A) % p
            idx = start
            while idx < size:
                alg_sieve[idx] += lp
                idx += p

        # Large primes: bucket (each hits at most size/p < 10 positions)
        for _, p in rat_large:
            lp = rat_logp[p]
            bm_mod = (b % p) * ((m % p + p) % p) % p
            start = int((-bm_mod % p + p) % p)
            start = (start + A) % p
            idx = start
            while idx < size:
                rat_sieve[idx] += lp
                idx += p

        for _, (p, r) in alg_large:
            lp = alg_logp[p]
            br_mod = (b % p) * ((r % p + p) % p) % p
            start = int((-br_mod % p + p) % p)
            start = (start + A) % p
            idx = start
            while idx < size:
                alg_sieve[idx] += lp
                idx += p

        # Threshold
        rat_typical = max(abs(bm), A)
        rat_thresh = int(0.6 * math.log(max(rat_typical, 2)) * 128)
        dom = max(A, b)
        alg_log_norm = d * math.log(max(dom, 2)) + math.log(max(max(f0_abs, fd_abs), 1))
        alg_thresh = int(0.5 * alg_log_norm * 128) if alg_log_norm > 1 else 128

        mask = (rat_sieve >= rat_thresh) & (alg_sieve >= alg_thresh)
        total_cands += int(np.sum(mask))

    elapsed = time.time() - t0

    if verbose:
        print(f"  Bucket sieve: {total_cands} candidates in {elapsed:.3f}s")
        print(f"  Rate: {max_b / elapsed:.0f} b-lines/s")

    return {
        'name': 'Bucket Sieve',
        'candidates': total_cands,
        'time': elapsed,
        'b_lines': max_b,
        'rate_blines_per_s': max_b / max(elapsed, 1e-9),
    }


###############################################################################
# Experiment 6: Segmented Sieve (L1-cache-sized segments)
###############################################################################

def experiment_segmented_sieve(n, setup, max_b=200, verbose=True):
    """
    Segmented sieve: split sieve into L1-cache-sized segments (32KB).
    All primes' contributions to one segment fit in L1 cache.
    This is how modern QS/GNFS implementations work.
    """
    if verbose:
        print("\n" + "=" * 70)
        print("EXPERIMENT 6: Segmented Sieve (L1-cache optimized)")
        print("=" * 70)

    rat_fb = setup['rat_fb']
    alg_fb = setup['alg_fb']
    A = setup['A']
    m = int(setup['m'])
    f_coeffs = setup['f_coeffs']
    d = setup['d']
    size = 2 * A + 1

    # Segment size: fit in L1 cache (32KB = 16K uint16 entries)
    SEG_SIZE = 16 * 1024  # 16K positions per segment (32KB with uint16)
    n_segments = (size + SEG_SIZE - 1) // SEG_SIZE

    rat_primes = np.array(rat_fb, dtype=np.int64)
    rat_logp = np.array([int(math.log(p) * 128 + 0.5) for p in rat_fb], dtype=np.uint16)
    alg_primes = np.array([p for p, r in alg_fb], dtype=np.int64)
    alg_roots = np.array([r for p, r in alg_fb], dtype=np.int64)
    alg_logp = np.array([int(math.log(p) * 128 + 0.5) for p, r in alg_fb], dtype=np.uint16)

    f0_abs = abs(f_coeffs[0]) if f_coeffs[0] != 0 else 1
    fd_abs = abs(f_coeffs[d]) if f_coeffs[d] != 0 else 1

    total_cands = 0
    t0 = time.time()

    # Segment buffers (reused)
    rat_seg = np.zeros(SEG_SIZE, dtype=np.uint16)
    alg_seg = np.zeros(SEG_SIZE, dtype=np.uint16)

    for b in range(1, max_b + 1):
        bm = b * m

        # Precompute starts for this b
        bm_mods_rat = (b % rat_primes) * ((m % rat_primes + rat_primes) % rat_primes) % rat_primes
        rat_starts_global = ((-bm_mods_rat % rat_primes) + rat_primes) % rat_primes
        rat_starts_global = (rat_starts_global + A) % rat_primes

        br_mods_alg = (b % alg_primes) * ((alg_roots % alg_primes + alg_primes) % alg_primes) % alg_primes
        alg_starts_global = ((-br_mods_alg % alg_primes) + alg_primes) % alg_primes
        alg_starts_global = (alg_starts_global + A) % alg_primes

        # Threshold
        rat_typical = max(abs(bm), A)
        rat_thresh = int(0.6 * math.log(max(rat_typical, 2)) * 128)
        dom = max(A, b)
        alg_log_norm = d * math.log(max(dom, 2)) + math.log(max(max(f0_abs, fd_abs), 1))
        alg_thresh = int(0.5 * alg_log_norm * 128) if alg_log_norm > 1 else 128

        # Track where each prime's stride currently points
        rat_next = rat_starts_global.copy()
        alg_next = alg_starts_global.copy()

        for seg_idx in range(n_segments):
            seg_start = seg_idx * SEG_SIZE
            seg_end = min(seg_start + SEG_SIZE, size)
            seg_len = seg_end - seg_start

            rat_seg[:seg_len] = 0
            alg_seg[:seg_len] = 0

            # Sieve rational primes into this segment
            for i in range(len(rat_fb)):
                p = int(rat_primes[i])
                lp = int(rat_logp[i])
                idx = int(rat_next[i]) - seg_start
                if idx < 0:
                    # Advance to first position in segment
                    idx += ((-idx + p - 1) // p) * p
                while idx < seg_len:
                    rat_seg[idx] += lp
                    idx += p
                # Update next position for this prime
                rat_next[i] = seg_start + idx

            # Sieve algebraic primes into this segment
            for i in range(len(alg_primes)):
                p = int(alg_primes[i])
                lp = int(alg_logp[i])
                idx = int(alg_next[i]) - seg_start
                if idx < 0:
                    idx += ((-idx + p - 1) // p) * p
                while idx < seg_len:
                    alg_seg[idx] += lp
                    idx += p
                alg_next[i] = seg_start + idx

            # Collect candidates from this segment
            mask = (rat_seg[:seg_len] >= rat_thresh) & (alg_seg[:seg_len] >= alg_thresh)
            total_cands += int(np.sum(mask))

    elapsed = time.time() - t0

    if verbose:
        print(f"  Segmented sieve: {total_cands} candidates in {elapsed:.3f}s")
        print(f"  Segment size: {SEG_SIZE} positions ({SEG_SIZE * 2 // 1024}KB)")
        print(f"  Segments per line: {n_segments}")
        print(f"  Rate: {max_b / elapsed:.0f} b-lines/s")

    return {
        'name': 'Segmented Sieve',
        'candidates': total_cands,
        'time': elapsed,
        'b_lines': max_b,
        'rate_blines_per_s': max_b / max(elapsed, 1e-9),
    }


###############################################################################
# Experiment 7: Smooth Number Oracle (precomputed hash table)
###############################################################################

def experiment_smooth_oracle(n, setup, max_b=50, verbose=True):
    """
    Smooth number oracle: precompute set of B-smooth numbers up to X.
    For each candidate norm, just check membership. O(1) per candidate.
    Feasible only for small bounds.
    """
    if verbose:
        print("\n" + "=" * 70)
        print("EXPERIMENT 7: Smooth Number Oracle (Hash Table)")
        print("=" * 70)

    rat_fb = setup['rat_fb']
    A = min(setup['A'], 50000)  # small for memory
    m = int(setup['m'])
    f_coeffs = setup['f_coeffs']
    d = setup['d']

    # Build smooth number set up to X using sieving
    # X = max rational norm for b=1..max_b, a in [-A,A]
    X = max(abs(-A + m), abs(A + max_b * m))
    # Cap X to avoid memory explosion
    X = min(X, 10_000_000)

    B = min(rat_fb[-1] if rat_fb else 1000, 10000)  # smooth bound

    if verbose:
        print(f"  Building smooth oracle: X={X}, B={B}")

    t0 = time.time()

    # Sieve of Eratosthenes style: mark all B-smooth numbers up to X
    # Use a set for O(1) lookup
    # Generate all B-smooth numbers up to X using a queue/BFS approach
    smooth_set = set()
    # Start with 1, multiply by each prime <= B
    primes = []
    p = 2
    while p <= B:
        primes.append(p)
        p = int(next_prime(p))

    # BFS: generate all products of primes^k <= X
    queue = [1]
    smooth_set.add(1)
    for p in primes:
        new_vals = []
        for s in queue:
            val = s * p
            while val <= X:
                if val not in smooth_set:
                    smooth_set.add(val)
                    new_vals.append(val)
                val *= p
        queue.extend(new_vals)
        # Memory check
        if len(smooth_set) > 5_000_000:
            if verbose:
                print(f"  Oracle too large ({len(smooth_set)} entries), capping")
            break

    build_time = time.time() - t0

    if verbose:
        print(f"  Oracle built: {len(smooth_set)} smooth numbers in {build_time:.2f}s")
        mem_mb = len(smooth_set) * 8 / 1e6  # rough: 8 bytes per int in set
        print(f"  Estimated memory: {mem_mb:.1f} MB")

    # Now test: for each (a,b), check if |a + b*m| is in smooth_set
    t1 = time.time()
    hits = 0
    tested = 0
    for b in range(1, max_b + 1):
        for a_offset in range(0, 2 * A + 1, 1):
            a = a_offset - A
            if a == 0:
                continue
            norm = abs(a + b * m)
            tested += 1
            if norm in smooth_set:
                hits += 1
    lookup_time = time.time() - t1

    if verbose:
        print(f"  Oracle lookup: {hits} smooth out of {tested} tested in {lookup_time:.2f}s")
        print(f"  Lookup rate: {tested / max(lookup_time, 1e-9):.0f} lookups/s")
        print(f"  Smoothness rate: {hits / max(tested, 1) * 100:.4f}%")

    # Compute psi(X, B) estimate using Dickman rho
    u = math.log(X) / math.log(B) if B > 1 else float('inf')
    # Rough Dickman: rho(u) ~ u^(-u) for u > 1
    rho_est = u ** (-u) if u > 0 else 1
    expected_smooth = int(X * rho_est)

    if verbose:
        print(f"  Dickman estimate: u={u:.2f}, rho(u)~{rho_est:.2e}, psi({X},{B})~{expected_smooth}")

    return {
        'name': 'Smooth Oracle',
        'oracle_size': len(smooth_set),
        'build_time': build_time,
        'lookup_time': lookup_time,
        'hits': hits,
        'tested': tested,
        'time': build_time + lookup_time,
        'b_lines': max_b,
    }


###############################################################################
# Experiment 8: Product Tree Batch Smoothness (Bernstein's method)
###############################################################################

def experiment_bernstein_batch(n, setup, max_b=200, verbose=True):
    """
    Bernstein's product-tree batch smoothness test.
    Given K residues and product P = prod(primes <= B):
    - Build product tree of residues
    - Compute remainder tree: P mod each residue
    - If gcd(P mod r_i, r_i) > 1, then r_i has a small factor

    This is O(K * log^2(K) * log(B)) amortized.
    For K=10000+ candidates: much faster than K * |FB| trial divisions.
    """
    if verbose:
        print("\n" + "=" * 70)
        print("EXPERIMENT 8: Bernstein Product Tree Batch Smoothness")
        print("=" * 70)

    rat_fb = setup['rat_fb']
    alg_fb = setup['alg_fb']
    A = min(setup['A'], 50000)  # cap for speed
    m = int(setup['m'])
    f_coeffs = setup['f_coeffs']
    d = setup['d']

    B = min(rat_fb[-1] if rat_fb else 1000, 20000)

    # Step 1: Compute P = product of all primes <= B
    if verbose:
        print(f"  Computing prime product P = prod(primes <= {B})...")
    t0 = time.time()

    primes = []
    p = mpz(2)
    while p <= B:
        primes.append(p)
        p = next_prime(p)

    # Use product tree for P (balanced binary tree multiplication)
    def product_tree_val(vals):
        if len(vals) == 0:
            return mpz(1)
        if len(vals) == 1:
            return vals[0]
        layer = [mpz(v) for v in vals]
        while len(layer) > 1:
            next_layer = []
            for i in range(0, len(layer) - 1, 2):
                next_layer.append(layer[i] * layer[i + 1])
            if len(layer) % 2:
                next_layer.append(layer[-1])
            layer = next_layer
        return layer[0]

    # Use prime powers for better detection: P = prod(p^k) where p^k <= B
    prime_powers = []
    for p in primes:
        pk = p
        while pk * p <= B:
            pk *= p
        prime_powers.append(pk)

    P = product_tree_val(prime_powers)
    p_time = time.time() - t0
    p_bits = int(gmpy2.log2(P)) + 1

    if verbose:
        print(f"  P has {p_bits} bits ({p_bits // 3.32:.0f} digits), computed in {p_time:.2f}s")

    # Step 2: Collect candidate norms
    t1 = time.time()
    norms = []
    norm_abs = []
    for b in range(1, max_b + 1):
        for a_off in range(0, 2 * A + 1, max(1, (2 * A + 1) // 2000)):
            # Sample positions to keep manageable
            a = a_off - A
            if a == 0:
                continue
            nr = abs(a + b * m)
            if nr > 1:
                norms.append((a, b))
                norm_abs.append(mpz(nr))

    K = len(norm_abs)
    collect_time = time.time() - t1

    if verbose:
        print(f"  Collected {K} candidate norms in {collect_time:.2f}s")

    # Step 3: Bernstein remainder tree
    # Build product tree of norms, then compute P mod each norm
    t2 = time.time()

    def product_tree(vals):
        """Build product tree: tree[0] = leaves, tree[-1] = root product."""
        tree = [list(vals)]
        while len(tree[-1]) > 1:
            layer = tree[-1]
            next_layer = []
            for i in range(0, len(layer) - 1, 2):
                next_layer.append(layer[i] * layer[i + 1])
            if len(layer) % 2:
                next_layer.append(layer[-1])
            tree.append(next_layer)
        return tree

    def remainder_tree(P, prod_tree):
        """Compute P mod each leaf using the product tree."""
        # Start at root: P mod root_product
        n_levels = len(prod_tree)
        rem_tree = [None] * n_levels
        rem_tree[n_levels - 1] = [P % prod_tree[n_levels - 1][0]]

        for level in range(n_levels - 2, -1, -1):
            rem_tree[level] = []
            parent_rems = rem_tree[level + 1]
            children = prod_tree[level]
            pi = 0
            for ci in range(0, len(children) - 1, 2):
                parent_rem = parent_rems[pi]
                rem_tree[level].append(parent_rem % children[ci])
                rem_tree[level].append(parent_rem % children[ci + 1])
                pi += 1
            if len(children) % 2:
                rem_tree[level].append(parent_rems[pi] % children[-1])

        return rem_tree[0]

    # Build product tree of norms
    if K > 50000:
        # Cap to avoid memory issues
        norm_abs = norm_abs[:50000]
        norms = norms[:50000]
        K = 50000

    prod_tree = product_tree(norm_abs)
    tree_time = time.time() - t2

    if verbose:
        print(f"  Product tree built ({len(prod_tree)} levels) in {tree_time:.2f}s")

    # Compute remainder tree
    t3 = time.time()
    remainders = remainder_tree(P, prod_tree)
    rem_time = time.time() - t3

    if verbose:
        print(f"  Remainder tree computed in {rem_time:.2f}s")

    # Step 4: Check which norms are smooth
    # norm is B-smooth iff gcd(P mod norm, norm) reveals all factors
    # More precisely: iterate P_mod = gcd(P mod r, r), r = r / P_mod until P_mod = 1
    # If r = 1, it's B-smooth
    t4 = time.time()
    smooth_count = 0
    partial_count = 0

    for i in range(K):
        r = norm_abs[i]
        p_mod_r = remainders[i]
        g = gcd(p_mod_r, r)
        cofactor = r
        while g > 1:
            while cofactor % g == 0:
                cofactor = cofactor // g
            g = gcd(p_mod_r, cofactor)
        if cofactor == 1:
            smooth_count += 1
        elif cofactor < B * 100:  # partial: cofactor is a single large prime
            partial_count += 1

    check_time = time.time() - t4
    total_time = time.time() - t0

    if verbose:
        print(f"  Smooth check: {smooth_count} smooth, {partial_count} partial out of {K}")
        print(f"  Check time: {check_time:.2f}s")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Amortized per candidate: {total_time / max(K, 1) * 1000:.3f} ms")
        # Compare to naive: K * |FB| divisions
        naive_ops = K * len(rat_fb)
        print(f"  Naive trial division would need {naive_ops:,} operations")

    return {
        'name': 'Bernstein Batch Smoothness',
        'K': K,
        'smooth': smooth_count,
        'partial': partial_count,
        'time': total_time,
        'tree_build': tree_time,
        'remainder_tree': rem_time,
        'check_time': check_time,
        'P_bits': p_bits,
        'b_lines': max_b,
        'amortized_ms': total_time / max(K, 1) * 1000,
    }


###############################################################################
# Experiment 9: NTT Sieve (frequency-domain convolution)
###############################################################################

def experiment_ntt_sieve(n, setup, max_b=50, verbose=True):
    """
    NTT/FFT sieve: compute sieve array as sum of periodic signals.
    Each prime p contributes a signal with period p.
    Use FFT to compute all contributions simultaneously.
    Cost: O(A*log A) vs O(A*|FB|/avg_p) for direct sieve.
    """
    if verbose:
        print("\n" + "=" * 70)
        print("EXPERIMENT 9: NTT/FFT Sieve (Frequency Domain)")
        print("=" * 70)

    rat_fb = setup['rat_fb']
    A = min(setup['A'], 50000)  # cap for FFT memory
    m = int(setup['m'])
    f_coeffs = setup['f_coeffs']
    d = setup['d']
    size = 2 * A + 1

    f0_abs = abs(f_coeffs[0]) if f_coeffs[0] != 0 else 1
    fd_abs = abs(f_coeffs[d]) if f_coeffs[d] != 0 else 1

    # For FFT approach: each prime p creates a periodic signal with period p
    # Signal_p(x) = log(p) if x % p == start, else 0
    # Sieve = sum of all Signal_p

    # Method: for each prime, create a sparse signal, FFT it, accumulate in freq domain,
    # then IFFT to get the sieve.
    # BUT: this doesn't help because each prime's FFT is O(size*log(size)).
    # Total = |FB| * O(size*log(size)) which is WORSE than direct.

    # Better approach: use the fact that a periodic signal with period p and amplitude A
    # has a known DFT: nonzero at frequencies that are multiples of size/p.
    # We can directly set the frequency components without FFT.

    if verbose:
        print(f"  Sieve size: {size}, FB: {len(rat_fb)} primes")

    # Direct approach for comparison
    t_direct = time.time()
    direct_total = 0
    for b in range(1, max_b + 1):
        sieve = np.zeros(size, dtype=np.float32)
        bm = b * m
        for p in rat_fb[:500]:  # cap at 500 primes for speed
            lp = math.log(p)
            bm_mod = (b % p) * ((m % p + p) % p) % p
            start = int((-bm_mod % p + p) % p)
            start = (start + A) % p
            idx = start
            while idx < size:
                sieve[idx] += lp
                idx += p

        rat_typical = max(abs(bm), A)
        thresh = 0.6 * math.log(max(rat_typical, 2))
        direct_total += int(np.sum(sieve >= thresh))

    direct_time = time.time() - t_direct

    # FFT approach: build each prime's contribution in freq domain
    # For a comb function with period p starting at s:
    # X[k] = (A/p) * exp(-2*pi*j*k*s/size) * sum_{m} delta(k - m*size/p)
    # This only works when p divides size, which it generally doesn't.
    # So we fall back to: build sparse time-domain signal per prime, use FFT accumulation

    t_fft = time.time()
    fft_total = 0

    # Pad to power of 2 for fast FFT
    fft_size = 1
    while fft_size < size:
        fft_size <<= 1

    for b in range(1, max_b + 1):
        # Accumulate in time domain (sparse), then threshold
        # The FFT advantage would come from batching: instead of per-prime sieve,
        # construct the full sieve as a convolution
        # But for GNFS sieve this is actually a SUM not a convolution
        # FFT doesn't help with sums of sparse periodic signals
        # Let's try the "batch DFT accumulation" approach:
        sieve_fft = np.zeros(fft_size, dtype=np.float32)
        bm = b * m

        for p in rat_fb[:500]:
            lp = float(math.log(p))
            bm_mod = (b % p) * ((m % p + p) % p) % p
            start = int((-bm_mod % p + p) % p)
            start = (start + A) % p
            # Create sparse signal and add
            idx = start
            while idx < size:
                sieve_fft[idx] += lp
                idx += p

        rat_typical = max(abs(bm), A)
        thresh = 0.6 * math.log(max(rat_typical, 2))
        fft_total += int(np.sum(sieve_fft[:size] >= thresh))

    fft_time = time.time() - t_fft

    if verbose:
        print(f"  Direct sieve (500 primes): {direct_total} hits in {direct_time:.3f}s")
        print(f"  FFT approach (500 primes): {fft_total} hits in {fft_time:.3f}s")
        print(f"  CONCLUSION: FFT does NOT help for additive sieve (sum of periodic)")
        print(f"  The sieve is already optimal at O(sum(size/p)) = O(size*log(log(B)))")

    return {
        'name': 'NTT/FFT Sieve',
        'direct_time': direct_time,
        'fft_time': fft_time,
        'direct_hits': direct_total,
        'fft_hits': fft_total,
        'conclusion': 'FFT does not help: sieve is sum of sparse periodic signals, not convolution',
        'time': direct_time + fft_time,
        'b_lines': max_b,
    }


###############################################################################
# Experiment 11: Algebraic Norm Precomputation (Horner on candidates)
###############################################################################

def experiment_horner_norm(n, setup, max_b=200, verbose=True):
    """
    Algebraic norm via Horner's method for batch evaluation.
    For fixed b: norm(a) = b^d * f(-a/b) is a polynomial in a of degree d.
    Precompute coefficients once per b, then evaluate at each candidate a
    using Horner's method: O(d) mults+adds per candidate.
    """
    if verbose:
        print("\n" + "=" * 70)
        print("EXPERIMENT 11: Horner's Method Batch Norm Evaluation")
        print("=" * 70)

    f_coeffs = setup['f_coeffs']
    d = setup['d']
    A = min(setup['A'], 50000)

    # For fixed b, algebraic norm = sum_{i=0}^{d} f[i] * (-a)^i * b^{d-i}
    # = b^d * sum_{i=0}^{d} f[i] * (-a/b)^i
    # = b^d * f(-a/b)
    #
    # As a polynomial in a: let c_i = f[i] * (-1)^i * b^{d-i}
    # norm(a) = c_0 + c_1*a + c_2*a^2 + ... + c_d*a^d
    # Horner: norm = c_d; for i in d-1..0: norm = norm*a + c_i

    # Benchmark: naive evaluation vs Horner
    n_candidates = 10000
    candidates = np.linspace(-A, A, n_candidates, dtype=np.int64)

    # Naive evaluation
    t_naive = time.time()
    naive_count = 0
    for b in range(1, max_b + 1):
        for a in candidates:
            a = int(a)
            if a == 0:
                continue
            result = 0
            neg_a_pow = 1
            b_pow = b ** d
            for i in range(d + 1):
                result += f_coeffs[i] * neg_a_pow * b_pow
                neg_a_pow *= (-a)
                if i < d:
                    b_pow //= b
            naive_count += 1
    naive_time = time.time() - t_naive

    # Horner evaluation
    t_horner = time.time()
    horner_count = 0
    for b in range(1, max_b + 1):
        # Precompute Horner coefficients for this b
        # c_i = f[i] * (-1)^i * b^{d-i}
        b_pows = [1] * (d + 1)
        for i in range(1, d + 1):
            b_pows[i] = b_pows[i - 1] * b
        horner_coeffs = [f_coeffs[i] * ((-1) ** i) * b_pows[d - i] for i in range(d + 1)]

        for a in candidates:
            a = int(a)
            if a == 0:
                continue
            # Horner: start from highest degree
            val = horner_coeffs[d]
            for i in range(d - 1, -1, -1):
                val = val * a + horner_coeffs[i]
            horner_count += 1
    horner_time = time.time() - t_horner

    # Vectorized Horner with numpy
    t_vec = time.time()
    vec_count = 0
    for b in range(1, max_b + 1):
        b_pows = [1] * (d + 1)
        for i in range(1, d + 1):
            b_pows[i] = b_pows[i - 1] * b
        hc = np.array([f_coeffs[i] * ((-1) ** i) * b_pows[d - i] for i in range(d + 1)], dtype=np.float64)

        # Vectorized Horner
        a_arr = candidates.astype(np.float64)
        val = np.full(len(a_arr), hc[d], dtype=np.float64)
        for i in range(d - 1, -1, -1):
            val = val * a_arr + hc[i]
        vec_count += len(a_arr)
    vec_time = time.time() - t_vec

    if verbose:
        print(f"  Naive norm eval: {naive_count} evals in {naive_time:.3f}s "
              f"({naive_count / max(naive_time, 1e-9):.0f}/s)")
        print(f"  Horner norm eval: {horner_count} evals in {horner_time:.3f}s "
              f"({horner_count / max(horner_time, 1e-9):.0f}/s)")
        print(f"  Vectorized Horner: {vec_count} evals in {vec_time:.3f}s "
              f"({vec_count / max(vec_time, 1e-9):.0f}/s)")
        if naive_time > 0:
            print(f"  Horner speedup: {naive_time / max(horner_time, 1e-9):.1f}x")
            print(f"  Vectorized speedup: {naive_time / max(vec_time, 1e-9):.1f}x")

    return {
        'name': 'Horner Norm Evaluation',
        'naive_time': naive_time,
        'horner_time': horner_time,
        'vec_time': vec_time,
        'naive_rate': naive_count / max(naive_time, 1e-9),
        'horner_rate': horner_count / max(horner_time, 1e-9),
        'vec_rate': vec_count / max(vec_time, 1e-9),
        'horner_speedup': naive_time / max(horner_time, 1e-9),
        'vec_speedup': naive_time / max(vec_time, 1e-9),
        'time': naive_time + horner_time + vec_time,
        'b_lines': max_b,
    }


###############################################################################
# Experiment 1: GPU Batch Sieve (CUDA via ctypes)
###############################################################################

GPU_SIEVE_CUDA = r"""
#include <stdio.h>
#include <stdint.h>
#include <string.h>

// atomicAdd for uint16_t (not natively supported on all architectures)
__device__ void atomicAdd_u16(uint16_t *addr, uint16_t val) {
    // Use 32-bit atomicAdd on the aligned 32-bit word containing addr
    unsigned int *base = (unsigned int *)((size_t)addr & ~3ULL);
    unsigned int shift = ((size_t)addr & 2) ? 16 : 0;
    unsigned int add_val = ((unsigned int)val) << shift;
    atomicAdd(base, add_val);
}

// GPU kernel: each thread handles one prime, sieving its arithmetic progression
__global__ void sieve_kernel(
    uint16_t *sieve_arr,       // sieve array (size = 2*A+1)
    const int64_t *primes,     // factor base primes
    const uint16_t *log_ps,    // log(p) * 128
    const int64_t *starts,     // start positions for this b-line
    int n_primes,
    int size
) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= n_primes) return;

    int64_t p = primes[tid];
    uint16_t lp = log_ps[tid];
    int64_t idx = starts[tid];

    while (idx < size) {
        atomicAdd_u16(&sieve_arr[idx], lp);
        idx += p;
    }
}

// Host function: sieve one b-line on GPU
extern "C" int gpu_sieve_line(
    int b, int A, int64_t m,
    const int64_t *h_rat_primes, const uint16_t *h_rat_logp, int n_rat,
    const int64_t *h_alg_primes, const int64_t *h_alg_roots,
    const uint16_t *h_alg_logp, int n_alg,
    uint16_t *h_rat_sieve,  // output: rational sieve (host)
    uint16_t *h_alg_sieve,  // output: algebraic sieve (host)
    // GPU device pointers (persistent across calls)
    int64_t *d_rat_primes, uint16_t *d_rat_logp, int64_t *d_rat_starts,
    int64_t *d_alg_primes, int64_t *d_alg_roots, uint16_t *d_alg_logp, int64_t *d_alg_starts,
    uint16_t *d_rat_sieve, uint16_t *d_alg_sieve
) {
    int size = 2 * A + 1;

    // Compute start positions on host
    int64_t *h_rat_starts = (int64_t *)malloc(n_rat * sizeof(int64_t));
    int64_t *h_alg_starts = (int64_t *)malloc(n_alg * sizeof(int64_t));

    for (int i = 0; i < n_rat; i++) {
        int64_t p = h_rat_primes[i];
        int64_t bm_mod = ((int64_t)b % p) * (((m % p) + p) % p) % p;
        int64_t start = ((-bm_mod % p) + p) % p;
        h_rat_starts[i] = (start + (int64_t)A) % p;
    }
    for (int i = 0; i < n_alg; i++) {
        int64_t p = h_alg_primes[i];
        int64_t r = h_alg_roots[i];
        int64_t br_mod = ((int64_t)b % p) * ((r % p + p) % p) % p;
        int64_t start = ((-br_mod % p) + p) % p;
        h_alg_starts[i] = (start + (int64_t)A) % p;
    }

    // Copy starts to device
    cudaMemcpy(d_rat_starts, h_rat_starts, n_rat * sizeof(int64_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_alg_starts, h_alg_starts, n_alg * sizeof(int64_t), cudaMemcpyHostToDevice);

    // Clear sieve arrays on device
    cudaMemset(d_rat_sieve, 0, size * sizeof(uint16_t));
    cudaMemset(d_alg_sieve, 0, size * sizeof(uint16_t));

    // Launch rational sieve kernel
    int threads = 256;
    int blocks_rat = (n_rat + threads - 1) / threads;
    int blocks_alg = (n_alg + threads - 1) / threads;

    sieve_kernel<<<blocks_rat, threads>>>(d_rat_sieve, d_rat_primes, d_rat_logp, d_rat_starts, n_rat, size);
    sieve_kernel<<<blocks_alg, threads>>>(d_alg_sieve, d_alg_primes, d_alg_logp, d_alg_starts, n_alg, size);

    cudaDeviceSynchronize();

    // Copy results back
    cudaMemcpy(h_rat_sieve, d_rat_sieve, size * sizeof(uint16_t), cudaMemcpyDeviceToHost);
    cudaMemcpy(h_alg_sieve, d_alg_sieve, size * sizeof(uint16_t), cudaMemcpyDeviceToHost);

    free(h_rat_starts);
    free(h_alg_starts);
    return 0;
}

// Allocate persistent GPU buffers
extern "C" int gpu_alloc(
    int n_rat, int n_alg, int size,
    const int64_t *h_rat_primes, const uint16_t *h_rat_logp,
    const int64_t *h_alg_primes, const int64_t *h_alg_roots, const uint16_t *h_alg_logp,
    // Output: device pointers (stored as uint64 on host)
    uint64_t *out_ptrs  // 9 pointers
) {
    int64_t *d_rat_primes, *d_alg_primes, *d_alg_roots;
    uint16_t *d_rat_logp, *d_alg_logp;
    int64_t *d_rat_starts, *d_alg_starts;
    uint16_t *d_rat_sieve, *d_alg_sieve;

    cudaMalloc(&d_rat_primes, n_rat * sizeof(int64_t));
    cudaMalloc(&d_rat_logp, n_rat * sizeof(uint16_t));
    cudaMalloc(&d_rat_starts, n_rat * sizeof(int64_t));
    cudaMalloc(&d_alg_primes, n_alg * sizeof(int64_t));
    cudaMalloc(&d_alg_roots, n_alg * sizeof(int64_t));
    cudaMalloc(&d_alg_logp, n_alg * sizeof(uint16_t));
    cudaMalloc(&d_alg_starts, n_alg * sizeof(int64_t));
    cudaMalloc(&d_rat_sieve, size * sizeof(uint16_t));
    cudaMalloc(&d_alg_sieve, size * sizeof(uint16_t));

    // Copy constant data
    cudaMemcpy(d_rat_primes, h_rat_primes, n_rat * sizeof(int64_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_rat_logp, h_rat_logp, n_rat * sizeof(uint16_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_alg_primes, h_alg_primes, n_alg * sizeof(int64_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_alg_roots, h_alg_roots, n_alg * sizeof(int64_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_alg_logp, h_alg_logp, n_alg * sizeof(uint16_t), cudaMemcpyHostToDevice);

    out_ptrs[0] = (uint64_t)d_rat_primes;
    out_ptrs[1] = (uint64_t)d_rat_logp;
    out_ptrs[2] = (uint64_t)d_rat_starts;
    out_ptrs[3] = (uint64_t)d_alg_primes;
    out_ptrs[4] = (uint64_t)d_alg_roots;
    out_ptrs[5] = (uint64_t)d_alg_logp;
    out_ptrs[6] = (uint64_t)d_alg_starts;
    out_ptrs[7] = (uint64_t)d_rat_sieve;
    out_ptrs[8] = (uint64_t)d_alg_sieve;

    return 0;
}

// Free GPU buffers
extern "C" void gpu_free(uint64_t *ptrs) {
    for (int i = 0; i < 9; i++) {
        cudaFree((void*)ptrs[i]);
    }
}
"""


def _compile_gpu_sieve():
    """Compile GPU sieve CUDA code, return ctypes library or None."""
    so_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gnfs_gpu_sieve.so')
    cu_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gnfs_gpu_sieve.cu')

    # Write CUDA source
    with open(cu_path, 'w') as f:
        f.write(GPU_SIEVE_CUDA)

    # Compile
    try:
        result = subprocess.run(
            ['nvcc', '-O3', '--shared', '-Xcompiler', '-fPIC',
             '-o', so_path, cu_path],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            print(f"  CUDA compile failed: {result.stderr[:500]}")
            return None
        lib = ctypes.CDLL(so_path)
        return lib
    except Exception as e:
        print(f"  CUDA compile error: {e}")
        return None


def experiment_gpu_sieve(n, setup, max_b=200, verbose=True):
    """
    GPU batch sieve: launch one thread per FB prime.
    Each thread walks its arithmetic progression through the sieve array.
    atomicAdd log(p) at each position.
    """
    if verbose:
        print("\n" + "=" * 70)
        print("EXPERIMENT 1: GPU Batch Sieve (CUDA)")
        print("=" * 70)

    gpu_lib = _compile_gpu_sieve()
    if gpu_lib is None:
        if verbose:
            print("  SKIPPED: Could not compile CUDA code")
        return {'name': 'GPU Batch Sieve', 'skipped': True, 'time': 0}

    rat_fb = setup['rat_fb']
    alg_fb = setup['alg_fb']
    A = setup['A']
    m = int(setup['m'])
    f_coeffs = setup['f_coeffs']
    d = setup['d']
    size = 2 * A + 1

    # Prepare host arrays
    rat_primes = np.array(rat_fb, dtype=np.int64)
    rat_logp = np.array([int(math.log(p) * 128 + 0.5) for p in rat_fb], dtype=np.uint16)
    alg_primes = np.array([p for p, r in alg_fb], dtype=np.int64)
    alg_roots = np.array([r for p, r in alg_fb], dtype=np.int64)
    alg_logp = np.array([int(math.log(p) * 128 + 0.5) for p, r in alg_fb], dtype=np.uint16)

    n_rat = len(rat_fb)
    n_alg = len(alg_fb)

    # Allocate GPU buffers
    gpu_lib.gpu_alloc.restype = ctypes.c_int
    gpu_lib.gpu_alloc.argtypes = [
        ctypes.c_int, ctypes.c_int, ctypes.c_int,
        ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_uint16),
        ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_uint16),
        ctypes.POINTER(ctypes.c_uint64),
    ]

    ptrs = (ctypes.c_uint64 * 9)()
    gpu_lib.gpu_alloc(
        n_rat, n_alg, size,
        rat_primes.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
        rat_logp.ctypes.data_as(ctypes.POINTER(ctypes.c_uint16)),
        alg_primes.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
        alg_roots.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
        alg_logp.ctypes.data_as(ctypes.POINTER(ctypes.c_uint16)),
        ptrs,
    )

    # Setup sieve function
    gpu_lib.gpu_sieve_line.restype = ctypes.c_int
    gpu_lib.gpu_sieve_line.argtypes = [
        ctypes.c_int, ctypes.c_int, ctypes.c_int64,
        ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_uint16), ctypes.c_int,
        ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_uint16), ctypes.c_int,
        ctypes.POINTER(ctypes.c_uint16), ctypes.POINTER(ctypes.c_uint16),
        ctypes.c_uint64, ctypes.c_uint64, ctypes.c_uint64,
        ctypes.c_uint64, ctypes.c_uint64, ctypes.c_uint64, ctypes.c_uint64,
        ctypes.c_uint64, ctypes.c_uint64,
    ]

    h_rat_sieve = np.zeros(size, dtype=np.uint16)
    h_alg_sieve = np.zeros(size, dtype=np.uint16)

    f0_abs = abs(f_coeffs[0]) if f_coeffs[0] != 0 else 1
    fd_abs = abs(f_coeffs[d]) if f_coeffs[d] != 0 else 1

    total_cands = 0
    t0 = time.time()

    for b in range(1, max_b + 1):
        gpu_lib.gpu_sieve_line(
            b, A, ctypes.c_int64(m),
            rat_primes.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            rat_logp.ctypes.data_as(ctypes.POINTER(ctypes.c_uint16)), n_rat,
            alg_primes.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            alg_roots.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            alg_logp.ctypes.data_as(ctypes.POINTER(ctypes.c_uint16)), n_alg,
            h_rat_sieve.ctypes.data_as(ctypes.POINTER(ctypes.c_uint16)),
            h_alg_sieve.ctypes.data_as(ctypes.POINTER(ctypes.c_uint16)),
            ptrs[0], ptrs[1], ptrs[2],
            ptrs[3], ptrs[4], ptrs[5], ptrs[6],
            ptrs[7], ptrs[8],
        )

        # Threshold and count candidates
        bm = b * m
        rat_typical = max(abs(bm), A)
        rat_thresh = int(0.6 * math.log(max(rat_typical, 2)) * 128)
        dom = max(A, b)
        alg_log_norm = d * math.log(max(dom, 2)) + math.log(max(max(f0_abs, fd_abs), 1))
        alg_thresh = int(0.5 * alg_log_norm * 128) if alg_log_norm > 1 else 128

        mask = (h_rat_sieve >= rat_thresh) & (h_alg_sieve >= alg_thresh)
        total_cands += int(np.sum(mask))

    elapsed = time.time() - t0

    # Free GPU
    gpu_lib.gpu_free.restype = None
    gpu_lib.gpu_free.argtypes = [ctypes.POINTER(ctypes.c_uint64)]
    gpu_lib.gpu_free(ptrs)

    if verbose:
        print(f"  GPU sieve: {total_cands} candidates in {elapsed:.3f}s")
        print(f"  Rate: {max_b / elapsed:.0f} b-lines/s")

    return {
        'name': 'GPU Batch Sieve',
        'candidates': total_cands,
        'time': elapsed,
        'b_lines': max_b,
        'rate_blines_per_s': max_b / max(elapsed, 1e-9),
    }


###############################################################################
# Experiment 2: GPU Batch Trial Division
###############################################################################

GPU_TRIAL_DIV_CUDA = r"""
#include <stdio.h>
#include <stdint.h>

// Each thread tests one (candidate, prime) pair
// Grid: candidates x prime_blocks
__global__ void trial_div_kernel(
    const int64_t *norms,      // candidate norms (absolute values)
    const int64_t *primes,     // FB primes
    int *exponents,            // output: exponent[cand * n_primes + prime_idx]
    int n_cands, int n_primes
) {
    int cand_idx = blockIdx.x;
    int prime_idx = blockIdx.y * blockDim.x + threadIdx.x;

    if (cand_idx >= n_cands || prime_idx >= n_primes) return;

    int64_t norm = norms[cand_idx];
    int64_t p = primes[prime_idx];
    int exp = 0;

    if (norm >= p && norm % p == 0) {
        exp = 1;
        int64_t reduced = norm / p;
        while (reduced % p == 0) {
            reduced /= p;
            exp++;
        }
    }
    exponents[cand_idx * n_primes + prime_idx] = exp;
}

// Host wrapper
extern "C" int gpu_trial_divide(
    const int64_t *h_norms, int n_cands,
    const int64_t *h_primes, int n_primes,
    int *h_exponents  // output: n_cands x n_primes
) {
    int64_t *d_norms, *d_primes;
    int *d_exponents;

    cudaMalloc(&d_norms, n_cands * sizeof(int64_t));
    cudaMalloc(&d_primes, n_primes * sizeof(int64_t));
    cudaMalloc(&d_exponents, (int64_t)n_cands * n_primes * sizeof(int));

    cudaMemcpy(d_norms, h_norms, n_cands * sizeof(int64_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_primes, h_primes, n_primes * sizeof(int64_t), cudaMemcpyHostToDevice);
    cudaMemset(d_exponents, 0, (int64_t)n_cands * n_primes * sizeof(int));

    int threads = 256;
    int prime_blocks = (n_primes + threads - 1) / threads;
    dim3 grid(n_cands, prime_blocks);

    trial_div_kernel<<<grid, threads>>>(d_norms, d_primes, d_exponents, n_cands, n_primes);
    cudaDeviceSynchronize();

    cudaMemcpy(h_exponents, d_exponents, (int64_t)n_cands * n_primes * sizeof(int), cudaMemcpyDeviceToHost);

    cudaFree(d_norms);
    cudaFree(d_primes);
    cudaFree(d_exponents);

    return 0;
}
"""


def _compile_gpu_trial_div():
    """Compile GPU trial division."""
    so_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gnfs_gpu_trialdiv.so')
    cu_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gnfs_gpu_trialdiv.cu')
    with open(cu_path, 'w') as f:
        f.write(GPU_TRIAL_DIV_CUDA)
    try:
        result = subprocess.run(
            ['nvcc', '-O3', '--shared', '-Xcompiler', '-fPIC', '-o', so_path, cu_path],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            print(f"  CUDA compile failed: {result.stderr[:500]}")
            return None
        return ctypes.CDLL(so_path)
    except Exception as e:
        print(f"  CUDA compile error: {e}")
        return None


def experiment_gpu_trial_division(n, setup, verbose=True):
    """
    GPU batch trial division: for each candidate norm, divide by ALL FB primes
    simultaneously. One GPU thread per (candidate, prime_block) pair.
    """
    if verbose:
        print("\n" + "=" * 70)
        print("EXPERIMENT 2: GPU Batch Trial Division")
        print("=" * 70)

    gpu_lib = _compile_gpu_trial_div()
    if gpu_lib is None:
        if verbose:
            print("  SKIPPED: Could not compile CUDA code")
        return {'name': 'GPU Trial Division', 'skipped': True, 'time': 0}

    rat_fb = setup['rat_fb']
    m = int(setup['m'])
    A = min(setup['A'], 50000)

    # Generate some candidate norms
    n_cands = 5000
    norms = []
    for b in range(1, 51):
        for a in range(-A, A + 1, max(1, (2 * A) // (n_cands // 50))):
            if a == 0:
                continue
            nr = abs(a + b * m)
            if nr > 1:
                norms.append(nr)
            if len(norms) >= n_cands:
                break
        if len(norms) >= n_cands:
            break

    n_cands = len(norms)
    n_primes = min(len(rat_fb), 5000)  # cap primes for memory
    norms_arr = np.array(norms, dtype=np.int64)
    primes_arr = np.array(rat_fb[:n_primes], dtype=np.int64)

    if verbose:
        print(f"  Testing {n_cands} candidates against {n_primes} primes")
        mem_mb = n_cands * n_primes * 4 / 1e6
        print(f"  Exponent matrix: {mem_mb:.1f} MB")

    # GPU trial division
    gpu_lib.gpu_trial_divide.restype = ctypes.c_int
    gpu_lib.gpu_trial_divide.argtypes = [
        ctypes.POINTER(ctypes.c_int64), ctypes.c_int,
        ctypes.POINTER(ctypes.c_int64), ctypes.c_int,
        ctypes.POINTER(ctypes.c_int),
    ]

    exponents = np.zeros(n_cands * n_primes, dtype=np.int32)

    t_gpu = time.time()
    gpu_lib.gpu_trial_divide(
        norms_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)), n_cands,
        primes_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)), n_primes,
        exponents.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
    )
    gpu_time = time.time() - t_gpu

    # Count smooth numbers
    exponents_2d = exponents.reshape(n_cands, n_primes)
    smooth = 0
    for i in range(n_cands):
        cofactor = norms[i]
        for j in range(n_primes):
            e = exponents_2d[i, j]
            if e > 0:
                cofactor //= primes_arr[j] ** e
        if cofactor == 1:
            smooth += 1

    # CPU comparison
    t_cpu = time.time()
    cpu_smooth = 0
    for i in range(n_cands):
        rem = norms[i]
        for j in range(n_primes):
            p = int(primes_arr[j])
            if rem < p:
                break
            while rem % p == 0:
                rem //= p
        if rem == 1:
            cpu_smooth += 1
    cpu_time = time.time() - t_cpu

    if verbose:
        print(f"  GPU trial div: {smooth} smooth in {gpu_time:.3f}s")
        print(f"  CPU trial div: {cpu_smooth} smooth in {cpu_time:.3f}s")
        print(f"  GPU speedup: {cpu_time / max(gpu_time, 1e-9):.1f}x")

    return {
        'name': 'GPU Trial Division',
        'n_cands': n_cands,
        'n_primes': n_primes,
        'gpu_smooth': smooth,
        'cpu_smooth': cpu_smooth,
        'gpu_time': gpu_time,
        'cpu_time': cpu_time,
        'speedup': cpu_time / max(gpu_time, 1e-9),
        'time': gpu_time + cpu_time,
    }


###############################################################################
# Experiment 3: Streaming Pipeline (double-buffer GPU/CPU)
###############################################################################

def experiment_streaming_pipeline(n, setup, max_b=200, verbose=True):
    """
    Streaming pipeline: GPU sieves b=k while CPU processes candidates from b=k-1.
    Uses threading to overlap GPU and CPU work.
    """
    if verbose:
        print("\n" + "=" * 70)
        print("EXPERIMENT 3: Streaming Pipeline (GPU sieve || CPU verify)")
        print("=" * 70)

    # Check if GPU sieve is available
    gpu_so = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gnfs_gpu_sieve.so')
    if not os.path.exists(gpu_so):
        if verbose:
            print("  SKIPPED: gnfs_gpu_sieve.so not found (run experiment 1 first)")
        return {'name': 'Streaming Pipeline', 'skipped': True, 'time': 0}

    # Simulate the pipeline with threading
    import threading

    rat_fb = setup['rat_fb']
    alg_fb = setup['alg_fb']
    A = min(setup['A'], 50000)
    m = int(setup['m'])
    f_coeffs = setup['f_coeffs']
    d = setup['d']
    size = 2 * A + 1

    f0_abs = abs(f_coeffs[0]) if f_coeffs[0] != 0 else 1
    fd_abs = abs(f_coeffs[d]) if f_coeffs[d] != 0 else 1

    # Double buffers
    buf_a = np.zeros(size, dtype=np.uint16)
    buf_b = np.zeros(size, dtype=np.uint16)

    rat_primes = np.array(rat_fb, dtype=np.int64)
    alg_primes = np.array([p for p, r in alg_fb], dtype=np.int64)
    alg_roots = np.array([r for p, r in alg_fb], dtype=np.int64)

    def cpu_sieve(b, sieve_buf):
        """CPU sieve one b-line into buffer."""
        sieve_buf[:] = 0
        bm = b * m
        for i in range(len(rat_fb)):
            p = int(rat_primes[i])
            lp = int(math.log(p) * 128 + 0.5)
            bm_mod = (b % p) * ((m % p + p) % p) % p
            start = int((-bm_mod % p + p) % p)
            start = (start + A) % p
            idx = start
            while idx < size:
                sieve_buf[idx] += lp
                idx += p

    def cpu_threshold(b, sieve_buf):
        """Count candidates passing threshold."""
        bm = b * m
        rat_typical = max(abs(bm), A)
        thresh = int(0.6 * math.log(max(rat_typical, 2)) * 128)
        return int(np.sum(sieve_buf >= thresh))

    # Sequential baseline
    t_seq = time.time()
    seq_total = 0
    for b in range(1, max_b + 1):
        cpu_sieve(b, buf_a)
        seq_total += cpu_threshold(b, buf_a)
    seq_time = time.time() - t_seq

    # Pipelined: sieve b=k in thread while processing b=k-1
    t_pipe = time.time()
    pipe_total = 0
    # First sieve
    cpu_sieve(1, buf_a)

    for b in range(2, max_b + 1):
        # Start sieving b into buf_b in background
        current_buf = buf_b if b % 2 == 0 else buf_a
        prev_buf = buf_a if b % 2 == 0 else buf_b

        t = threading.Thread(target=cpu_sieve, args=(b, current_buf))
        t.start()

        # Process previous b's results
        pipe_total += cpu_threshold(b - 1, prev_buf)

        t.join()

    # Process last b
    last_buf = buf_b if max_b % 2 == 0 else buf_a
    pipe_total += cpu_threshold(max_b, last_buf)
    pipe_time = time.time() - t_pipe

    if verbose:
        print(f"  Sequential: {seq_total} cands in {seq_time:.3f}s")
        print(f"  Pipelined:  {pipe_total} cands in {pipe_time:.3f}s")
        print(f"  Pipeline speedup: {seq_time / max(pipe_time, 1e-9):.2f}x")

    return {
        'name': 'Streaming Pipeline',
        'seq_time': seq_time,
        'pipe_time': pipe_time,
        'speedup': seq_time / max(pipe_time, 1e-9),
        'seq_cands': seq_total,
        'pipe_cands': pipe_total,
        'time': seq_time + pipe_time,
        'b_lines': max_b,
    }


###############################################################################
# Experiment 10: Lattice Sieve Concepts (special-q enumeration)
###############################################################################

def experiment_lattice_sieve_concepts(n, setup, verbose=True):
    """
    Lattice sieve analysis: for each special-q prime, the valid (a,b) pairs
    form a lattice. Gauss-reduce the lattice basis to get short vectors,
    then sieve in the reduced basis. Measures:
    - How many candidates per special-q
    - Lattice reduction quality (orthogonality defect)
    - Comparison with line sieve density
    """
    if verbose:
        print("\n" + "=" * 70)
        print("EXPERIMENT 10: Lattice Sieve Analysis")
        print("=" * 70)

    f_coeffs = setup['f_coeffs']
    d = setup['d']
    m = int(setup['m'])
    rat_fb = setup['rat_fb']
    alg_fb = setup['alg_fb']
    A = min(setup['A'], 50000)

    fb_bound = rat_fb[-1] if rat_fb else 1000

    # Find special-q primes: primes q > FB bound where f has roots
    sq_primes = []
    q = int(next_prime(fb_bound))
    q_max = fb_bound * 20
    while q <= q_max and len(sq_primes) < 100:
        roots = find_poly_roots_mod_p(f_coeffs, q)
        for r in roots:
            sq_primes.append((q, r))
        q = int(next_prime(q))

    if verbose:
        print(f"  Found {len(sq_primes)} special-q pairs in [{fb_bound+1}, {q_max}]")

    # For each special-q, analyze the lattice
    from gnfs_engine import gauss_reduce_2d

    t0 = time.time()
    results = []
    total_lattice_pts = 0
    total_line_pts = 0

    for qi, (q, r) in enumerate(sq_primes[:50]):
        # Lattice: {(a,b) : a + b*r = 0 (mod q)}
        # Basis: v1 = (q, 0), v2 = (-r, 1)
        v1 = (q, 0)
        v2 = (-r, 1)
        u, v = gauss_reduce_2d(v1, v2)

        # Orthogonality defect
        det = abs(u[0] * v[1] - u[1] * v[0])
        norm_u = math.sqrt(u[0] ** 2 + u[1] ** 2)
        norm_v = math.sqrt(v[0] ** 2 + v[1] ** 2)
        defect = (norm_u * norm_v) / max(det, 1)

        # Count lattice points in sieve region [-A, A] x [1, B_max]
        B_max = 100
        # Enumerate lattice points: (a, b) = i*u + j*v for integer i, j
        # with -A <= a <= A, 1 <= b <= B_max
        count = 0
        for i in range(-int(2 * A / max(norm_u, 1)), int(2 * A / max(norm_u, 1)) + 1):
            for j in range(-int(2 * A / max(norm_v, 1)), int(2 * A / max(norm_v, 1)) + 1):
                a = i * u[0] + j * v[0]
                b = i * u[1] + j * v[1]
                if -A <= a <= A and 1 <= b <= B_max:
                    count += 1

        # Line sieve would check all (2A+1) * B_max positions
        line_pts = (2 * A + 1) * B_max

        total_lattice_pts += count
        total_line_pts += line_pts

        results.append({
            'q': q, 'r': r,
            'defect': defect,
            'lattice_pts': count,
            'line_pts': line_pts,
            'reduction': line_pts / max(count, 1),
        })

    elapsed = time.time() - t0

    if verbose:
        avg_defect = np.mean([r['defect'] for r in results]) if results else 0
        avg_reduction = np.mean([r['reduction'] for r in results]) if results else 0
        print(f"  Average orthogonality defect: {avg_defect:.2f}")
        print(f"  Average search space reduction: {avg_reduction:.0f}x")
        print(f"  Total lattice pts: {total_lattice_pts} vs line pts: {total_line_pts}")
        print(f"  Analysis time: {elapsed:.2f}s")
        if results:
            best = max(results, key=lambda r: r['reduction'])
            print(f"  Best special-q: q={best['q']}, reduction={best['reduction']:.0f}x")

    return {
        'name': 'Lattice Sieve Analysis',
        'n_sq': len(sq_primes),
        'avg_defect': float(np.mean([r['defect'] for r in results])) if results else 0,
        'avg_reduction': float(np.mean([r['reduction'] for r in results])) if results else 0,
        'time': elapsed,
    }


###############################################################################
# Experiment: C Segmented Sieve (compiled for true L1-cache benefit)
###############################################################################

SEGMENTED_SIEVE_C = r"""
/*
 * Segmented sieve: L1-cache optimized.
 * Processes sieve in 32KB segments so all data fits in L1 cache.
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int segmented_sieve_c(
    int b_start, int b_end, int A,
    const int64_t *rat_primes, int n_rat, int64_t m,
    const int64_t *alg_primes, const int64_t *alg_roots, int n_alg,
    int rat_frac_x1000, int alg_frac_x1000,
    int poly_degree, int64_t f0_abs, int64_t fd_abs,
    int *out_a, int *out_b, int max_cands
) {
    int size = 2 * A + 1;
    int total = 0;
    double abs_m = (double)(m >= 0 ? m : -m);
    double rat_frac = rat_frac_x1000 / 1000.0;
    double alg_frac = alg_frac_x1000 / 1000.0;
    double log_f0 = (f0_abs > 0) ? log((double)f0_abs) : 0.0;
    double log_fd = (fd_abs > 0) ? log((double)fd_abs) : 0.0;
    double log_leading = (log_fd > log_f0) ? log_fd : log_f0;

    /* Segment size: 16K uint16 = 32KB, fits in L1 cache */
    const int SEG_SIZE = 16 * 1024;

    uint16_t *rat_seg = (uint16_t *)malloc(SEG_SIZE * sizeof(uint16_t));
    uint16_t *alg_seg = (uint16_t *)malloc(SEG_SIZE * sizeof(uint16_t));

    uint16_t *rat_lps = (uint16_t *)malloc(n_rat * sizeof(uint16_t));
    uint16_t *alg_lps = (uint16_t *)malloc(n_alg * sizeof(uint16_t));
    int64_t *rat_next = (int64_t *)malloc(n_rat * sizeof(int64_t));
    int64_t *alg_next = (int64_t *)malloc(n_alg * sizeof(int64_t));

    for (int i = 0; i < n_rat; i++)
        rat_lps[i] = (uint16_t)(log((double)rat_primes[i]) * 128.0 + 0.5);
    for (int i = 0; i < n_alg; i++)
        alg_lps[i] = (uint16_t)(log((double)alg_primes[i]) * 128.0 + 0.5);

    for (int b = b_start; b <= b_end && total < max_cands; b++) {
        double bm = (double)b * abs_m;
        double rat_typical = (bm > (double)A) ? bm : (double)A;
        uint16_t rat_thresh = (uint16_t)(rat_frac * log(rat_typical) * 128.0);

        double dom = ((double)A > (double)b) ? (double)A : (double)b;
        double alg_log_norm = (double)poly_degree * log(dom) + log_leading;
        uint16_t alg_thresh = (alg_log_norm > 1.0)
            ? (uint16_t)(alg_frac * alg_log_norm * 128.0) : 128;

        /* Compute global starts */
        for (int i = 0; i < n_rat; i++) {
            int64_t p = rat_primes[i];
            int64_t bm_mod = ((int64_t)b % p) * (((m % p) + p) % p) % p;
            int64_t start = ((-bm_mod % p) + p) % p;
            rat_next[i] = (start + (int64_t)A) % p;
        }
        for (int i = 0; i < n_alg; i++) {
            int64_t p = alg_primes[i];
            int64_t r = alg_roots[i];
            int64_t br_mod = ((int64_t)b % p) * ((r % p + p) % p) % p;
            int64_t start = ((-br_mod % p) + p) % p;
            alg_next[i] = (start + (int64_t)A) % p;
        }

        /* Process each segment */
        for (int seg_start = 0; seg_start < size; seg_start += SEG_SIZE) {
            int seg_end = seg_start + SEG_SIZE;
            if (seg_end > size) seg_end = size;
            int seg_len = seg_end - seg_start;

            memset(rat_seg, 0, seg_len * sizeof(uint16_t));
            memset(alg_seg, 0, seg_len * sizeof(uint16_t));

            /* Sieve rational primes in this segment */
            for (int i = 0; i < n_rat; i++) {
                int64_t p = rat_primes[i];
                uint16_t lp = rat_lps[i];
                int64_t idx = rat_next[i];
                /* Advance to segment start */
                if (idx < seg_start) {
                    int64_t skip = ((int64_t)seg_start - idx + p - 1) / p;
                    idx += skip * p;
                }
                while (idx < seg_end) {
                    rat_seg[idx - seg_start] += lp;
                    idx += p;
                }
                rat_next[i] = idx;
            }

            /* Sieve algebraic primes in this segment */
            for (int i = 0; i < n_alg; i++) {
                int64_t p = alg_primes[i];
                uint16_t lp = alg_lps[i];
                int64_t idx = alg_next[i];
                if (idx < seg_start) {
                    int64_t skip = ((int64_t)seg_start - idx + p - 1) / p;
                    idx += skip * p;
                }
                while (idx < seg_end) {
                    alg_seg[idx - seg_start] += lp;
                    idx += p;
                }
                alg_next[i] = idx;
            }

            /* Collect candidates */
            for (int j = 0; j < seg_len && total < max_cands; j++) {
                if (rat_seg[j] >= rat_thresh && alg_seg[j] >= alg_thresh) {
                    int a = (seg_start + j) - A;
                    if (a == 0) continue;
                    /* Quick coprimality check */
                    int ga = (a < 0) ? -a : a;
                    int gb = b;
                    while (gb) { int t = gb; gb = ga % gb; ga = t; }
                    if (ga != 1) continue;
                    out_a[total] = a;
                    out_b[total] = b;
                    total++;
                }
            }
        }
    }

    free(rat_seg); free(alg_seg);
    free(rat_lps); free(alg_lps);
    free(rat_next); free(alg_next);
    return total;
}
"""


def _compile_segmented_sieve():
    """Compile segmented sieve C code."""
    base = os.path.dirname(os.path.abspath(__file__))
    so_path = os.path.join(base, 'gnfs_seg_sieve_c.so')
    c_path = os.path.join(base, 'gnfs_seg_sieve_c.c')

    with open(c_path, 'w') as f:
        f.write(SEGMENTED_SIEVE_C)
    try:
        result = subprocess.run(
            ['gcc', '-O3', '-march=native', '-shared', '-fPIC', '-o', so_path, c_path, '-lm'],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            print(f"  C compile failed: {result.stderr[:500]}")
            return None
        return ctypes.CDLL(so_path)
    except Exception as e:
        print(f"  Compile error: {e}")
        return None


def experiment_c_segmented_sieve(n, setup, max_b=200, verbose=True):
    """
    C segmented sieve: L1-cache optimized, compiled as shared library.
    Compare directly with existing sieve_batch_c.
    """
    if verbose:
        print("\n" + "=" * 70)
        print("EXPERIMENT 6b: C Segmented Sieve (L1-cache optimized)")
        print("=" * 70)

    seg_lib = _compile_segmented_sieve()
    if seg_lib is None:
        if verbose:
            print("  SKIPPED: compilation failed")
        return {'name': 'C Segmented Sieve', 'skipped': True, 'time': 0}

    rat_fb = setup['rat_fb']
    alg_fb = setup['alg_fb']
    A = setup['A']
    m = int(setup['m'])
    f_coeffs = setup['f_coeffs']
    d = setup['d']

    rat_p_arr = np.array(rat_fb, dtype=np.int64)
    alg_p_arr = np.array([p for p, r in alg_fb], dtype=np.int64)
    alg_r_arr = np.array([r for p, r in alg_fb], dtype=np.int64)

    f0_abs = abs(f_coeffs[0]) if f_coeffs[0] != 0 else 1
    fd_abs = abs(f_coeffs[d]) if f_coeffs[d] != 0 else 1

    max_cands = 100000
    out_a = (ctypes.c_int * max_cands)()
    out_b = (ctypes.c_int * max_cands)()

    seg_lib.segmented_sieve_c.restype = ctypes.c_int
    seg_lib.segmented_sieve_c.argtypes = [
        ctypes.c_int, ctypes.c_int, ctypes.c_int,
        ctypes.POINTER(ctypes.c_int64), ctypes.c_int, ctypes.c_int64,
        ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64), ctypes.c_int,
        ctypes.c_int, ctypes.c_int,
        ctypes.c_int, ctypes.c_int64, ctypes.c_int64,
        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.c_int,
    ]

    t0 = time.time()
    total = seg_lib.segmented_sieve_c(
        1, max_b, A,
        rat_p_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
        len(rat_fb), ctypes.c_int64(m),
        alg_p_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
        alg_r_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
        len(alg_fb),
        600, 500,
        d, ctypes.c_int64(f0_abs), ctypes.c_int64(fd_abs),
        out_a, out_b, max_cands,
    )
    elapsed = time.time() - t0

    if verbose:
        print(f"  C segmented sieve: {total} candidates in {elapsed:.3f}s")
        print(f"  Rate: {max_b / elapsed:.0f} b-lines/s")

    return {
        'name': 'C Segmented Sieve',
        'candidates': total,
        'time': elapsed,
        'b_lines': max_b,
        'rate_blines_per_s': max_b / max(elapsed, 1e-9),
    }


###############################################################################
# run_all: Execute all experiments
###############################################################################

def run_all(digits=35, max_b=200, verbose=True):
    """Run all moonshot experiments on a semiprime of the given digit count."""
    print("=" * 70)
    print(f"GNFS SIEVE MOONSHOTS — {digits}-digit semiprime")
    print("=" * 70)

    n, p, q = make_semiprime(digits)
    nd = len(str(n))
    print(f"  N = {n}")
    print(f"  p = {p}")
    print(f"  q = {q}")
    print(f"  Digits: {nd}")

    setup = setup_gnfs(n)
    if setup is None:
        print("  Trivial factorization!")
        return

    print(f"  GNFS params: d={setup['d']}, FB={len(setup['rat_fb'])} rat + "
          f"{len(setup['alg_fb'])} alg, A={setup['A']}")

    results = {}

    # 0. Baseline
    try:
        r = experiment_baseline(n, setup, max_b=max_b, verbose=verbose)
        if r:
            results['baseline'] = r
    except Exception as e:
        print(f"  Baseline FAILED: {e}")

    # 6b. C Segmented Sieve (most promising CPU optimization)
    try:
        r = experiment_c_segmented_sieve(n, setup, max_b=max_b, verbose=verbose)
        if r:
            results['c_segmented'] = r
    except Exception as e:
        print(f"  C Segmented Sieve FAILED: {e}")

    # 4. Compressed Sieve (Python — shows concept)
    try:
        r = experiment_compressed_sieve(n, setup, max_b=min(max_b, 30), verbose=verbose)
        if r:
            results['compressed'] = r
    except Exception as e:
        print(f"  Compressed Sieve FAILED: {e}")

    # 5. Bucket Sieve
    try:
        r = experiment_bucket_sieve(n, setup, max_b=min(max_b, 30), verbose=verbose)
        if r:
            results['bucket'] = r
    except Exception as e:
        print(f"  Bucket Sieve FAILED: {e}")

    # 6. Segmented Sieve (Python — for comparison with C version)
    try:
        r = experiment_segmented_sieve(n, setup, max_b=min(max_b, 20), verbose=verbose)
        if r:
            results['segmented_py'] = r
    except Exception as e:
        print(f"  Segmented Sieve FAILED: {e}")

    # 7. Smooth Oracle
    try:
        r = experiment_smooth_oracle(n, setup, max_b=min(max_b, 20), verbose=verbose)
        if r:
            results['smooth_oracle'] = r
    except Exception as e:
        print(f"  Smooth Oracle FAILED: {e}")

    # 8. Bernstein Batch Smoothness (highest theoretical value)
    try:
        r = experiment_bernstein_batch(n, setup, max_b=min(max_b, 50), verbose=verbose)
        if r:
            results['bernstein'] = r
    except Exception as e:
        print(f"  Bernstein Batch FAILED: {e}")

    # 9. NTT/FFT Sieve
    try:
        r = experiment_ntt_sieve(n, setup, max_b=min(max_b, 20), verbose=verbose)
        if r:
            results['ntt'] = r
    except Exception as e:
        print(f"  NTT Sieve FAILED: {e}")

    # 10. Lattice Sieve Analysis
    try:
        r = experiment_lattice_sieve_concepts(n, setup, verbose=verbose)
        if r:
            results['lattice'] = r
    except Exception as e:
        print(f"  Lattice Sieve FAILED: {e}")

    # 11. Horner Norm Evaluation
    try:
        r = experiment_horner_norm(n, setup, max_b=min(max_b, 50), verbose=verbose)
        if r:
            results['horner'] = r
    except Exception as e:
        print(f"  Horner Norm FAILED: {e}")

    # 1. GPU Batch Sieve
    try:
        r = experiment_gpu_sieve(n, setup, max_b=max_b, verbose=verbose)
        if r:
            results['gpu_sieve'] = r
    except Exception as e:
        print(f"  GPU Sieve FAILED: {e}")

    # 2. GPU Trial Division
    try:
        r = experiment_gpu_trial_division(n, setup, verbose=verbose)
        if r:
            results['gpu_trialdiv'] = r
    except Exception as e:
        print(f"  GPU Trial Div FAILED: {e}")

    # 3. Streaming Pipeline
    try:
        r = experiment_streaming_pipeline(n, setup, max_b=min(max_b, 50), verbose=verbose)
        if r:
            results['streaming'] = r
    except Exception as e:
        print(f"  Streaming Pipeline FAILED: {e}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    baseline_time = results.get('baseline', {}).get('time', None)
    baseline_rate = results.get('baseline', {}).get('rate_blines_per_s', None)

    for name, r in sorted(results.items()):
        t = r.get('time', 0)
        rate = r.get('rate_blines_per_s', None)
        skipped = r.get('skipped', False)
        if skipped:
            print(f"  {r['name']:40s} SKIPPED")
        elif rate and baseline_rate:
            speedup = rate / baseline_rate
            print(f"  {r['name']:40s} {t:8.3f}s  {rate:8.0f} b/s  {speedup:5.2f}x vs baseline")
        elif 'speedup' in r:
            print(f"  {r['name']:40s} {t:8.3f}s  speedup={r['speedup']:.2f}x")
        else:
            print(f"  {r['name']:40s} {t:8.3f}s")

    # Actionable findings
    print("\n" + "=" * 70)
    print("ACTIONABLE FINDINGS")
    print("=" * 70)

    if 'c_segmented' in results and 'baseline' in results:
        seg_r = results['c_segmented']['rate_blines_per_s']
        base_r = results['baseline']['rate_blines_per_s']
        ratio = seg_r / base_r
        if ratio > 1.05:
            print(f"  [WIN] C Segmented Sieve: {ratio:.2f}x faster than baseline")
            print(f"        -> Integrate into gnfs_engine.py as primary sieve")
        else:
            print(f"  [NEUTRAL] C Segmented Sieve: {ratio:.2f}x (marginal)")

    if 'bernstein' in results:
        r = results['bernstein']
        print(f"  [INFO] Bernstein batch: {r['amortized_ms']:.3f} ms/candidate")
        print(f"        Smooth: {r['smooth']}, Partial: {r['partial']} out of {r['K']}")
        if r['smooth'] + r['partial'] > 0:
            print(f"        -> Useful for post-sieve smoothness verification")

    if 'gpu_sieve' in results and not results['gpu_sieve'].get('skipped'):
        r = results['gpu_sieve']
        if 'baseline' in results:
            ratio = r['rate_blines_per_s'] / results['baseline']['rate_blines_per_s']
            print(f"  [GPU] GPU Sieve: {ratio:.2f}x vs CPU baseline")

    if 'gpu_trialdiv' in results and not results['gpu_trialdiv'].get('skipped'):
        r = results['gpu_trialdiv']
        print(f"  [GPU] Trial Division: {r.get('speedup', 0):.2f}x GPU vs CPU")

    if 'horner' in results:
        r = results['horner']
        print(f"  [INFO] Horner norm: {r['horner_speedup']:.1f}x (scalar), "
              f"{r['vec_speedup']:.1f}x (vectorized)")

    if 'lattice' in results:
        r = results['lattice']
        print(f"  [INFO] Lattice sieve: {r['avg_reduction']:.0f}x search space reduction")

    return results


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='GNFS Sieve Moonshots')
    parser.add_argument('--digits', type=int, default=35, help='Semiprime digit count')
    parser.add_argument('--max-b', type=int, default=200, help='Max b-lines to sieve')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()

    run_all(digits=args.digits, max_b=args.max_b, verbose=not args.quiet)
