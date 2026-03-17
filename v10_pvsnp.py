#!/usr/bin/env python3
"""
v10_pvsnp.py — P vs NP Investigation Phase 5
=============================================
Five genuinely NEW experiments probing the computational structure of factoring.

Exp 1: Circuit depth of factoring (Boolean circuit complexity)
Exp 2: Pseudorandom factoring oracle (PRG quality comparison)
Exp 3: Factoring as optimization landscape (fitness landscape analysis)
Exp 4: Entropy of factoring algorithm choices (Shannon entropy of decisions)
Exp 5: Kolmogorov complexity of factoring proofs (proof length scaling)

RAM budget: <1.5 GB throughout.
"""

import sys, os, time, math, random, struct, zlib, json, hashlib
import collections, itertools, functools
from typing import List, Tuple, Dict, Optional
import numpy as np
import gmpy2
from gmpy2 import mpz, isqrt, gcd, is_prime, next_prime

RESULTS = {}

# ─── Utility ────────────────────────────────────────────────────────────────

def random_prime(bits):
    """Generate a random prime of exactly `bits` bits."""
    while True:
        p = gmpy2.mpz_random(gmpy2.random_state(random.getrandbits(64)), mpz(1) << bits)
        p |= (mpz(1) << (bits - 1)) | 1
        if is_prime(p):
            return p

def make_semiprime(total_bits, balance=0.5):
    """Make N=p*q with total_bits bits."""
    p_bits = max(4, int(total_bits * balance))
    q_bits = total_bits - p_bits
    p = random_prime(p_bits)
    q = random_prime(q_bits)
    while p == q:
        q = random_prime(q_bits)
    return int(p * q), int(min(p, q)), int(max(p, q))

def trial_divide(N, limit=None):
    """Trial division up to limit. Returns (factor, steps) or (None, steps)."""
    if limit is None:
        limit = int(isqrt(N)) + 1
    steps = 0
    if N % 2 == 0:
        return 2, 1
    d = 3
    while d <= limit:
        steps += 1
        if N % d == 0:
            return d, steps
        d += 2
    return None, steps

def pollard_rho_instrumented(N, max_iter=500000):
    """Pollard rho returning (factor, iterations, choices_made).
    choices_made is a list of (x mod 256) values encountered — tracks randomness."""
    if N % 2 == 0:
        return 2, 1, [0]
    x = random.randint(2, N - 1)
    y = x
    c = random.randint(1, N - 1)
    d = 1
    choices = []
    iters = 0
    while d == 1 and iters < max_iter:
        x = (x * x + c) % N
        y = (y * y + c) % N
        y = (y * y + c) % N
        d = int(gcd(abs(x - y), N))
        choices.append(int(x) & 0xFF)
        iters += 1
    if d != N and d > 1:
        return int(d), iters, choices
    return None, iters, choices

def fmt_time(t):
    if t < 1:
        return f"{t*1000:.1f}ms"
    return f"{t:.2f}s"

# ═══════════════════════════════════════════════════════════════════════════════
# EXPERIMENT 1: Circuit Depth of Factoring
# ═══════════════════════════════════════════════════════════════════════════════
#
# For small N, build the Boolean circuit computing smallest_factor(N).
# We represent the circuit as a DAG of AND/OR/NOT gates.
# Measure depth (longest path) and width (max gates at any level).
# Key question: does depth grow poly or super-poly with bit length?

def exp1_circuit_depth():
    """Build Boolean circuits for smallest_factor(N) at various bit sizes."""
    print("\n" + "="*70)
    print("EXP 1: Circuit Depth of Factoring")
    print("="*70)

    results = []

    for nb in [4, 5, 6, 7, 8, 9, 10, 11, 12]:
        t0 = time.time()
        # For an nb-bit number N, smallest_factor needs ceil(nb/2) output bits.
        # We build a circuit that, for each candidate divisor d=2..2^(nb/2),
        # checks if d divides N, and outputs the smallest such d.
        #
        # Rather than building a full gate-level circuit (exponential in general),
        # we measure the STRUCTURE of the computation:
        # - Division N mod d requires O(nb^2) gates, depth O(nb)
        # - Comparison with zero: O(nb) gates, depth O(log nb)
        # - Priority encoder (pick smallest): O(2^(nb/2) * nb) gates
        #
        # We simulate this by counting actual operations for all N of nb bits.

        n_candidates = 1 << (nb // 2)  # divisors to check: 2..2^(nb/2)

        # For each nb-bit semiprime, measure the "depth" = position of smallest factor
        # in the search space (how deep into the circuit we must go)
        depths = []
        widths = []
        total_ops = []

        # Sample semiprimes of this size
        count = 0
        attempts = 0
        target = min(500, 1 << nb)

        for N in range(1 << (nb - 1), 1 << nb):
            if attempts > 10000:
                break
            attempts += 1
            # Check if N is a semiprime
            f = None
            for d in range(2, int(N**0.5) + 1):
                if N % d == 0:
                    f = d
                    break
            if f is None:
                continue
            q = N // f
            if not is_prime(q) or not is_prime(f):
                continue

            # Circuit depth proxy: number of division checks until we find factor
            # This corresponds to the depth of the "earliest matching" subcircuit
            depth = f - 1  # divisions checked: 2, 3, ..., f
            # Width: number of parallel division units = n_candidates
            width = n_candidates
            # Total ops: each division is O(nb^2) gates
            ops = depth * (nb * nb)

            depths.append(depth)
            widths.append(width)
            total_ops.append(ops)
            count += 1
            if count >= target:
                break

        if not depths:
            continue

        elapsed = time.time() - t0
        avg_depth = np.mean(depths)
        med_depth = np.median(depths)
        max_depth = np.max(depths)
        avg_width = np.mean(widths)
        avg_ops = np.mean(total_ops)

        # Theoretical: if depth grows as O(2^(nb/2)), super-poly
        # If depth grows as O(nb^k), polynomial
        # The KEY metric: log(avg_depth) / log(nb) gives the "polynomial exponent"
        # vs log(avg_depth) / nb gives exponential rate

        poly_exp = math.log(avg_depth + 1) / math.log(nb) if nb > 1 else 0
        exp_rate = math.log(avg_depth + 1) / nb if nb > 0 else 0

        row = {
            'bits': nb,
            'n_semiprimes': count,
            'avg_depth': avg_depth,
            'median_depth': med_depth,
            'max_depth': max_depth,
            'avg_width': avg_width,
            'avg_total_ops': avg_ops,
            'poly_exponent': poly_exp,
            'exp_rate': exp_rate,
            'time': elapsed
        }
        results.append(row)
        print(f"  {nb}b: avg_depth={avg_depth:.1f}, med={med_depth:.0f}, "
              f"max={max_depth}, poly_exp={poly_exp:.3f}, exp_rate={exp_rate:.4f}, "
              f"n={count}, {fmt_time(elapsed)}")

    # Fit growth model: depth ~ C * 2^(alpha * nb)
    if len(results) >= 3:
        bits_arr = np.array([r['bits'] for r in results])
        depth_arr = np.array([r['avg_depth'] for r in results])
        log_depth = np.log(depth_arr + 1)

        # Linear fit: log(depth) = a * nb + b  =>  depth ~ e^b * e^(a*nb)
        coeffs_exp = np.polyfit(bits_arr, log_depth, 1)
        # Polynomial fit: log(depth) = a * log(nb) + b  =>  depth ~ nb^a
        log_bits = np.log(bits_arr)
        coeffs_poly = np.polyfit(log_bits, log_depth, 1)

        # Residuals
        res_exp = np.sum((log_depth - np.polyval(coeffs_exp, bits_arr))**2)
        res_poly = np.sum((log_depth - np.polyval(coeffs_poly, log_bits))**2)

        fit_summary = {
            'exponential_rate': float(coeffs_exp[0]),
            'exponential_residual': float(res_exp),
            'polynomial_exponent': float(coeffs_poly[0]),
            'polynomial_residual': float(res_poly),
            'better_fit': 'polynomial' if res_poly < res_exp else 'exponential'
        }
        print(f"\n  Fit: exp rate={coeffs_exp[0]:.4f} (resid={res_exp:.4f}), "
              f"poly exp={coeffs_poly[0]:.3f} (resid={res_poly:.4f})")
        print(f"  Better fit: {fit_summary['better_fit']}")
    else:
        fit_summary = {}

    RESULTS['exp1_circuit_depth'] = {'data': results, 'fit': fit_summary}
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# EXPERIMENT 2: Pseudorandom Factoring Oracle
# ═══════════════════════════════════════════════════════════════════════════════
#
# If factoring were easy, could we build a better PRG?
# Compare: (a) BBS generator x_{i+1} = x_i^2 mod N (b) "factor-assisted" generators
# that use knowledge of p,q. Measure randomness quality via frequency test,
# runs test, and serial correlation.

def exp2_prg_oracle():
    """Compare PRG quality: BBS vs factor-assisted vs Python random."""
    print("\n" + "="*70)
    print("EXP 2: Pseudorandom Factoring Oracle")
    print("="*70)

    def frequency_test(bits):
        """Proportion of 1s — should be ~0.5."""
        if not bits:
            return 0.5
        return sum(bits) / len(bits)

    def runs_test(bits):
        """Number of runs (consecutive same bits) — measures independence."""
        if len(bits) < 2:
            return 0
        runs = 1
        for i in range(1, len(bits)):
            if bits[i] != bits[i-1]:
                runs += 1
        n = len(bits)
        expected_runs = (2 * n - 1) / 3
        return runs / expected_runs if expected_runs > 0 else 1.0

    def serial_correlation(bits):
        """Lag-1 autocorrelation."""
        if len(bits) < 10:
            return 0.0
        b = np.array(bits, dtype=float)
        b = b - b.mean()
        if np.std(b) < 1e-12:
            return 0.0
        corr = np.correlate(b[:-1], b[1:])[0] / (len(b) - 1) / (np.std(b)**2 + 1e-15)
        return float(corr)

    def chi2_byte_test(bits):
        """Chi-squared test on byte distribution."""
        if len(bits) < 80:
            return 0.0
        n_bytes = len(bits) // 8
        byte_counts = [0] * 256
        for i in range(n_bytes):
            val = 0
            for j in range(8):
                val = (val << 1) | bits[i * 8 + j]
            byte_counts[val] += 1
        expected = n_bytes / 256
        if expected < 0.01:
            return 0.0
        chi2 = sum((c - expected)**2 / expected for c in byte_counts)
        # Normalize: chi2/df where df=255
        return chi2 / 255

    def bbs_generate(N, seed, n_bits):
        """Blum-Blum-Shub PRG: x_{i+1} = x_i^2 mod N, output LSB."""
        x = seed % N
        if x < 2:
            x = 3
        bits = []
        for _ in range(n_bits):
            x = (x * x) % N
            bits.append(x & 1)
        return bits

    def factor_assisted_prg(N, p, q, seed, n_bits):
        """Factor-assisted PRG: uses CRT to compute x^2 mod N faster,
        and extracts MORE bits per iteration (floor(log2(log2(N))) bits)."""
        x = seed % N
        if x < 2:
            x = 3
        # With factoring, we know we can safely extract floor(log2(log2(N))) bits
        safe_bits = max(1, int(math.log2(max(1, math.log2(N + 1)))))
        bits = []
        mask = (1 << safe_bits) - 1
        while len(bits) < n_bits:
            # CRT-accelerated squaring
            xp = pow(x, 2, p)
            xq = pow(x, 2, q)
            # CRT reconstruction
            p_inv_q = int(gmpy2.invert(p, q))
            x = int(xp + p * ((p_inv_q * (xq - xp)) % q))
            for b in range(safe_bits):
                if len(bits) < n_bits:
                    bits.append((x >> b) & 1)
        return bits[:n_bits]

    def hash_prg(seed, n_bits):
        """Reference PRG: SHA-256 based (considered strong)."""
        bits = []
        counter = 0
        s = seed.to_bytes(32, 'big') if seed > 0 else b'\x00' * 32
        while len(bits) < n_bits:
            h = hashlib.sha256(s + counter.to_bytes(8, 'big')).digest()
            for byte in h:
                for b in range(8):
                    if len(bits) < n_bits:
                        bits.append((byte >> b) & 1)
            counter += 1
        return bits[:n_bits]

    results = []
    n_bits_gen = 8000  # bits to generate per test

    for nb in [32, 48, 64, 80, 96, 128]:
        t0 = time.time()
        # Generate Blum integer (p,q both 3 mod 4)
        while True:
            p = random_prime(nb // 2)
            if p % 4 == 3:
                break
        while True:
            q = random_prime(nb // 2)
            if q % 4 == 3 and q != p:
                break
        N = int(p * q)
        p, q = int(p), int(q)
        seed = random.randint(2, N - 1)

        # Generate bits from each method
        bbs_bits = bbs_generate(N, seed, n_bits_gen)
        fa_bits = factor_assisted_prg(N, p, q, seed, n_bits_gen)
        hash_bits = hash_prg(seed, n_bits_gen)

        elapsed = time.time() - t0

        # Evaluate each
        metrics = {}
        for name, bits in [('BBS', bbs_bits), ('FactorPRG', fa_bits), ('SHA256', hash_bits)]:
            freq = frequency_test(bits)
            runs = runs_test(bits)
            corr = serial_correlation(bits)
            chi2 = chi2_byte_test(bits)
            # Composite score: distance from ideal (freq=0.5, runs=1.0, corr=0.0, chi2=1.0)
            score = abs(freq - 0.5) + abs(runs - 1.0) + abs(corr) + abs(chi2 - 1.0) / 10
            metrics[name] = {
                'frequency': round(freq, 4),
                'runs_ratio': round(runs, 4),
                'serial_corr': round(corr, 6),
                'chi2_norm': round(chi2, 3),
                'composite_score': round(score, 4)
            }

        row = {'bits': nb, 'metrics': metrics, 'time': elapsed}
        results.append(row)

        print(f"  {nb}b N: BBS score={metrics['BBS']['composite_score']:.4f}, "
              f"FactorPRG={metrics['FactorPRG']['composite_score']:.4f}, "
              f"SHA256={metrics['SHA256']['composite_score']:.4f}, {fmt_time(elapsed)}")

    # Analysis: does factor knowledge improve PRG quality?
    bbs_scores = [r['metrics']['BBS']['composite_score'] for r in results]
    fa_scores = [r['metrics']['FactorPRG']['composite_score'] for r in results]
    sha_scores = [r['metrics']['SHA256']['composite_score'] for r in results]

    analysis = {
        'avg_bbs_score': np.mean(bbs_scores),
        'avg_factor_prg_score': np.mean(fa_scores),
        'avg_sha256_score': np.mean(sha_scores),
        'factor_knowledge_helps': bool(np.mean(fa_scores) < np.mean(bbs_scores)),
        'factor_prg_vs_bbs_ratio': np.mean(fa_scores) / (np.mean(bbs_scores) + 1e-10)
    }
    print(f"\n  Avg scores — BBS: {analysis['avg_bbs_score']:.4f}, "
          f"FactorPRG: {analysis['avg_factor_prg_score']:.4f}, "
          f"SHA256: {analysis['avg_sha256_score']:.4f}")
    print(f"  Factor knowledge helps PRG: {analysis['factor_knowledge_helps']}")

    RESULTS['exp2_prg_oracle'] = {'data': results, 'analysis': analysis}
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# EXPERIMENT 3: Factoring as Optimization Landscape
# ═══════════════════════════════════════════════════════════════════════════════
#
# For each N=pq, the function f(x) = N mod x has a sharp zero at x=p and x=q.
# Analyze this landscape: ruggedness, autocorrelation length, basin structure.
# Does landscape structure predict factoring difficulty?

def exp3_optimization_landscape():
    """Analyze the N mod x landscape for semiprimes."""
    print("\n" + "="*70)
    print("EXP 3: Factoring as Optimization Landscape")
    print("="*70)

    def landscape_metrics(N, p, q):
        """Compute landscape metrics for f(x) = N mod x, x=2..sqrt(N)."""
        sqrtN = int(isqrt(N))
        # Sample the landscape (full enumeration for small N, sampled for large)
        if sqrtN <= 5000:
            xs = list(range(2, sqrtN + 1))
        else:
            # Sample 5000 points uniformly + points near factors
            xs = sorted(set(
                list(range(2, min(500, sqrtN + 1))) +
                [random.randint(2, sqrtN) for _ in range(4000)] +
                list(range(max(2, p - 50), min(sqrtN, p + 51))) +
                list(range(max(2, q - 50), min(sqrtN, q + 51)))
            ))

        vals = [N % x for x in xs]
        n = len(vals)

        if n < 10:
            return None

        # 1. Ruggedness: number of local minima / total points
        local_mins = 0
        for i in range(1, n - 1):
            if vals[i] < vals[i-1] and vals[i] < vals[i+1]:
                local_mins += 1
        ruggedness = local_mins / n

        # 2. Autocorrelation length: how far until autocorrelation drops below 1/e
        vals_arr = np.array(vals, dtype=float)
        vals_centered = vals_arr - vals_arr.mean()
        var = np.var(vals_centered)
        if var < 1e-10:
            autocorr_length = 0
        else:
            max_lag = min(200, n // 2)
            autocorr_length = max_lag  # default if never drops
            for lag in range(1, max_lag):
                ac = np.mean(vals_centered[:n-lag] * vals_centered[lag:]) / var
                if ac < 1.0 / math.e:
                    autocorr_length = lag
                    break

        # 3. Basin of attraction for p: how wide is the valley around x=p?
        # Find the range [p-delta, p+delta] where f(x) < median(f)
        median_val = np.median(vals_arr)
        basin_left = 0
        basin_right = 0
        for delta in range(1, min(500, p - 1)):
            if N % (p - delta) < median_val:
                basin_left = delta
            else:
                break
        for delta in range(1, min(500, sqrtN - p + 1)):
            if N % (p + delta) < median_val:
                basin_right = delta
            else:
                break
        basin_width = basin_left + basin_right + 1

        # 4. Gradient signal: average |f(x+1) - f(x)| near factor vs far away
        near_grads = []
        far_grads = []
        for i in range(len(xs) - 1):
            grad = abs(vals[i+1] - vals[i])
            if abs(xs[i] - p) < 50 or abs(xs[i] - q) < 50:
                near_grads.append(grad)
            else:
                far_grads.append(grad)
        gradient_ratio = (np.mean(near_grads) / (np.mean(far_grads) + 1)
                          if near_grads and far_grads else 0)

        # 5. Global structure: coefficient of variation
        cv = float(np.std(vals_arr) / (np.mean(vals_arr) + 1))

        return {
            'ruggedness': round(ruggedness, 4),
            'autocorr_length': autocorr_length,
            'basin_width': basin_width,
            'gradient_ratio': round(gradient_ratio, 4),
            'coeff_variation': round(cv, 4),
            'n_local_mins': local_mins,
            'n_points': n
        }

    results = []
    for nb in [16, 20, 24, 28, 32, 36, 40, 44, 48]:
        t0 = time.time()
        trial_metrics = []
        n_trials = 30 if nb <= 32 else 15

        for _ in range(n_trials):
            N, p, q = make_semiprime(nb)
            m = landscape_metrics(N, p, q)
            if m:
                # Also measure actual factoring difficulty via Pollard rho
                f, iters, _ = pollard_rho_instrumented(N, max_iter=200000)
                m['rho_iters'] = iters if f else 200000
                m['rho_found'] = f is not None
                trial_metrics.append(m)

        if not trial_metrics:
            continue

        elapsed = time.time() - t0

        # Average metrics
        avg = {}
        for key in ['ruggedness', 'autocorr_length', 'basin_width', 'gradient_ratio',
                     'coeff_variation', 'rho_iters']:
            avg[key] = np.mean([m[key] for m in trial_metrics])

        # Correlations: does landscape predict difficulty?
        if len(trial_metrics) >= 5:
            rho_iters = np.array([m['rho_iters'] for m in trial_metrics])
            for metric_name in ['ruggedness', 'autocorr_length', 'basin_width', 'gradient_ratio']:
                metric_vals = np.array([m[metric_name] for m in trial_metrics])
                if np.std(metric_vals) > 1e-10 and np.std(rho_iters) > 1e-10:
                    corr = float(np.corrcoef(metric_vals, rho_iters)[0, 1])
                else:
                    corr = 0.0
                avg[f'corr_{metric_name}_vs_difficulty'] = round(corr, 3)

        row = {'bits': nb, 'n_trials': len(trial_metrics), 'avg_metrics': avg, 'time': elapsed}
        results.append(row)

        print(f"  {nb}b: rugged={avg['ruggedness']:.4f}, autocorr={avg['autocorr_length']:.1f}, "
              f"basin={avg['basin_width']:.1f}, grad_ratio={avg['gradient_ratio']:.3f}, "
              f"rho_iters={avg['rho_iters']:.0f}, {fmt_time(elapsed)}")

    # Overall correlation analysis
    if len(results) >= 3:
        bits_arr = np.array([r['bits'] for r in results])
        rugged_arr = np.array([r['avg_metrics']['ruggedness'] for r in results])
        basin_arr = np.array([r['avg_metrics']['basin_width'] for r in results])

        analysis = {
            'ruggedness_trend': float(np.polyfit(bits_arr, rugged_arr, 1)[0]),
            'basin_trend': float(np.polyfit(bits_arr, np.log(basin_arr + 1), 1)[0]),
            'landscape_increasingly_rugged': bool(np.polyfit(bits_arr, rugged_arr, 1)[0] > 0),
        }
        # Check per-instance correlations across all trials
        for key in ['corr_ruggedness_vs_difficulty', 'corr_basin_width_vs_difficulty',
                     'corr_gradient_ratio_vs_difficulty']:
            vals = [r['avg_metrics'].get(key, 0) for r in results if key in r['avg_metrics']]
            if vals:
                analysis[f'avg_{key}'] = round(np.mean(vals), 3)

        print(f"\n  Ruggedness trend: {analysis['ruggedness_trend']:.6f}/bit "
              f"({'increasing' if analysis['landscape_increasingly_rugged'] else 'decreasing'})")
        for key in ['avg_corr_ruggedness_vs_difficulty', 'avg_corr_basin_width_vs_difficulty']:
            if key in analysis:
                print(f"  {key}: {analysis[key]:.3f}")
    else:
        analysis = {}

    RESULTS['exp3_landscape'] = {'data': results, 'analysis': analysis}
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# EXPERIMENT 4: Entropy of Factoring Algorithm Choices
# ═══════════════════════════════════════════════════════════════════════════════
#
# Measure Shannon entropy of the internal state trajectory of Pollard rho.
# Higher entropy = more "randomness" consumed = harder instance.
# Compare: entropy vs actual difficulty (iterations).

def exp4_algorithm_entropy():
    """Measure Shannon entropy of factoring algorithm state trajectories."""
    print("\n" + "="*70)
    print("EXP 4: Entropy of Factoring Algorithm Choices")
    print("="*70)

    def shannon_entropy(sequence, alphabet_size=256):
        """Compute Shannon entropy of a discrete sequence in bits."""
        if not sequence:
            return 0.0
        counts = collections.Counter(sequence)
        n = len(sequence)
        entropy = 0.0
        for count in counts.values():
            if count > 0:
                p = count / n
                entropy -= p * math.log2(p)
        return entropy

    def trajectory_entropy_rate(sequence, block_size=2):
        """Entropy rate: H(X_n | X_{n-1}, ..., X_{n-k+1})."""
        if len(sequence) < block_size + 1:
            return shannon_entropy(sequence)
        # Joint entropy of blocks of size k+1
        blocks_k1 = [tuple(sequence[i:i+block_size+1]) for i in range(len(sequence) - block_size)]
        blocks_k = [tuple(sequence[i:i+block_size]) for i in range(len(sequence) - block_size + 1)]

        h_joint = shannon_entropy(blocks_k1)
        h_cond = shannon_entropy(blocks_k)
        return h_joint - h_cond  # H(X_n | past)

    def compression_entropy(sequence):
        """Empirical entropy via compression ratio."""
        if not sequence:
            return 0.0
        raw = bytes(sequence)
        compressed = zlib.compress(raw, 9)
        return len(compressed) * 8 / len(raw)  # bits per symbol

    results = []

    for nb in [16, 20, 24, 28, 32, 36, 40, 44, 48, 52]:
        t0 = time.time()
        entropies = []
        entropy_rates = []
        comp_entropies = []
        iterations_list = []
        n_trials = 50 if nb <= 36 else 20

        for _ in range(n_trials):
            N, p, q = make_semiprime(nb)
            factor, iters, choices = pollard_rho_instrumented(N)

            if not choices or len(choices) < 5:
                continue

            h = shannon_entropy(choices)
            h_rate = trajectory_entropy_rate(choices)
            h_comp = compression_entropy(choices)

            entropies.append(h)
            entropy_rates.append(h_rate)
            comp_entropies.append(h_comp)
            iterations_list.append(iters)

        if not entropies:
            continue

        elapsed = time.time() - t0

        # Correlation: entropy vs iterations
        if len(entropies) >= 5:
            corr_h_iters = float(np.corrcoef(entropies, iterations_list)[0, 1])
            corr_hrate_iters = float(np.corrcoef(entropy_rates, iterations_list)[0, 1])
            corr_hcomp_iters = float(np.corrcoef(comp_entropies, iterations_list)[0, 1])
        else:
            corr_h_iters = corr_hrate_iters = corr_hcomp_iters = 0.0

        row = {
            'bits': nb,
            'n_trials': len(entropies),
            'avg_entropy': round(np.mean(entropies), 3),
            'avg_entropy_rate': round(np.mean(entropy_rates), 3),
            'avg_comp_entropy': round(np.mean(comp_entropies), 3),
            'avg_iterations': round(np.mean(iterations_list), 1),
            'corr_entropy_vs_iters': round(corr_h_iters, 3),
            'corr_entropy_rate_vs_iters': round(corr_hrate_iters, 3),
            'corr_comp_entropy_vs_iters': round(corr_hcomp_iters, 3),
            'max_possible_entropy': round(math.log2(256), 3),  # 8.0 for byte alphabet
            'time': elapsed
        }
        results.append(row)

        print(f"  {nb}b: H={row['avg_entropy']:.3f}, H_rate={row['avg_entropy_rate']:.3f}, "
              f"H_comp={row['avg_comp_entropy']:.3f}, iters={row['avg_iterations']:.0f}, "
              f"corr(H,iters)={corr_h_iters:.3f}, {fmt_time(elapsed)}")

    # Trend analysis
    if len(results) >= 3:
        bits_arr = np.array([r['bits'] for r in results])
        h_arr = np.array([r['avg_entropy'] for r in results])
        corr_arr = np.array([r['corr_entropy_vs_iters'] for r in results])

        analysis = {
            'entropy_trend_per_bit': float(np.polyfit(bits_arr, h_arr, 1)[0]),
            'entropy_approaches_max': bool(np.mean(h_arr[-3:]) > 7.5),
            'avg_correlation': float(np.mean(corr_arr)),
            'entropy_predicts_difficulty': bool(abs(np.mean(corr_arr)) > 0.3),
        }
        print(f"\n  Entropy trend: {analysis['entropy_trend_per_bit']:.4f} bits/bit")
        print(f"  Avg corr(entropy, difficulty): {analysis['avg_correlation']:.3f}")
        print(f"  Entropy predicts difficulty: {analysis['entropy_predicts_difficulty']}")
    else:
        analysis = {}

    RESULTS['exp4_algorithm_entropy'] = {'data': results, 'analysis': analysis}
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# EXPERIMENT 5: Kolmogorov Complexity of Factoring Proofs
# ═══════════════════════════════════════════════════════════════════════════════
#
# The shortest "proof" that N=pq is just p (n/2 bits).
# But algorithms produce LONG proofs: Pollard rho generates a trajectory,
# SIQS generates many relations + matrix. Measure proof length vs problem size.
# Is there a minimum proof complexity?

def exp5_proof_complexity():
    """Measure the data generated (proof length) by factoring algorithms."""
    print("\n" + "="*70)
    print("EXP 5: Kolmogorov Complexity of Factoring Proofs")
    print("="*70)

    def trial_div_proof_length(N):
        """Proof = list of all divisions tried. Length in bits."""
        f, steps = trial_divide(N, limit=int(isqrt(N)) + 1)
        # Each step: one division (log2(N) bits for divisor)
        nb = N.bit_length()
        proof_bits = steps * nb  # each division check encoded as nb bits
        return f, steps, proof_bits

    def rho_proof_length(N):
        """Proof = full trajectory of (x, y, gcd) values."""
        f, iters, choices = pollard_rho_instrumented(N, max_iter=500000)
        nb = N.bit_length()
        # Each iteration: 3 values of nb bits (x, y, d)
        proof_bits = iters * 3 * nb
        return f, iters, proof_bits, choices

    def fermat_proof_length(N):
        """Fermat's method proof = sequence of (a, b^2) pairs tried."""
        a = int(isqrt(N))
        if a * a == N:
            return a, 0, 0
        a += 1
        steps = 0
        nb = N.bit_length()
        while steps < 500000:
            b2 = a * a - N
            steps += 1
            b = int(isqrt(b2))
            if b * b == b2:
                p = a + b
                q = a - b
                if q > 1:
                    proof_bits = steps * 2 * nb  # each step: (a, b^2) pair
                    return int(min(p, q)), steps, proof_bits
            a += 1
        return None, steps, steps * 2 * nb

    results = []

    for nb in [16, 20, 24, 28, 32, 36, 40, 44, 48]:
        t0 = time.time()
        trial_proofs = []
        rho_proofs = []
        fermat_proofs = []
        n_trials = 30 if nb <= 32 else 15

        for _ in range(n_trials):
            N, p, q = make_semiprime(nb)

            # Minimum proof: just p
            min_proof_bits = p.bit_length()

            # Trial division
            if nb <= 40:
                f, steps, proof_bits = trial_div_proof_length(N)
                if f:
                    trial_proofs.append({
                        'proof_bits': proof_bits,
                        'overhead': proof_bits / min_proof_bits,
                        'steps': steps
                    })

            # Pollard rho
            f, iters, proof_bits, choices = rho_proof_length(N)
            if f:
                # Also compute compressed proof length
                raw = bytes(choices)
                compressed_bits = len(zlib.compress(raw, 9)) * 8
                rho_proofs.append({
                    'proof_bits': proof_bits,
                    'compressed_proof_bits': compressed_bits,
                    'overhead': proof_bits / min_proof_bits,
                    'compressed_overhead': compressed_bits / min_proof_bits,
                    'steps': iters
                })

            # Fermat
            if nb <= 36:
                f, steps, proof_bits = fermat_proof_length(N)
                if f:
                    fermat_proofs.append({
                        'proof_bits': proof_bits,
                        'overhead': proof_bits / min_proof_bits,
                        'steps': steps
                    })

        elapsed = time.time() - t0

        row = {
            'bits': nb,
            'min_proof_bits': nb // 2,  # theoretic minimum
        }

        if trial_proofs:
            row['trial_avg_overhead'] = round(np.mean([p['overhead'] for p in trial_proofs]), 1)
            row['trial_avg_proof_bits'] = round(np.mean([p['proof_bits'] for p in trial_proofs]), 0)

        if rho_proofs:
            row['rho_avg_overhead'] = round(np.mean([p['overhead'] for p in rho_proofs]), 1)
            row['rho_avg_proof_bits'] = round(np.mean([p['proof_bits'] for p in rho_proofs]), 0)
            row['rho_compressed_overhead'] = round(np.mean([p['compressed_overhead'] for p in rho_proofs]), 1)
            row['rho_compressed_bits'] = round(np.mean([p['compressed_proof_bits'] for p in rho_proofs]), 0)

        if fermat_proofs:
            row['fermat_avg_overhead'] = round(np.mean([p['overhead'] for p in fermat_proofs]), 1)

        row['time'] = elapsed
        results.append(row)

        rho_oh = row.get('rho_avg_overhead', 0)
        rho_comp = row.get('rho_compressed_overhead', 0)
        trial_oh = row.get('trial_avg_overhead', 0)
        print(f"  {nb}b: min_proof={nb//2}b, rho_overhead={rho_oh:.1f}x, "
              f"rho_compressed={rho_comp:.1f}x, trial_overhead={trial_oh:.1f}x, "
              f"{fmt_time(elapsed)}")

    # Scaling analysis: how does proof overhead grow with bit size?
    if len(results) >= 3:
        bits_arr = np.array([r['bits'] for r in results])
        rho_entries = [(r['bits'], r['rho_avg_overhead']) for r in results if 'rho_avg_overhead' in r]
        if len(rho_entries) >= 3:
            rb = np.array([e[0] for e in rho_entries])
            ro = np.log(np.array([e[1] for e in rho_entries]))
            coeffs = np.polyfit(rb, ro, 1)
            analysis = {
                'rho_overhead_growth_rate': float(coeffs[0]),
                'rho_overhead_doubling_bits': round(math.log(2) / (coeffs[0] + 1e-10), 1),
            }
            # Compressed overhead
            comp_entries = [(r['bits'], r['rho_compressed_overhead'])
                           for r in results if 'rho_compressed_overhead' in r]
            if len(comp_entries) >= 3:
                cb = np.array([e[0] for e in comp_entries])
                co = np.log(np.array([e[1] for e in comp_entries]) + 1)
                coeffs_c = np.polyfit(cb, co, 1)
                analysis['compressed_overhead_growth_rate'] = float(coeffs_c[0])
                analysis['compression_helps'] = bool(coeffs_c[0] < coeffs[0])

            print(f"\n  Rho overhead growth: {analysis['rho_overhead_growth_rate']:.4f} (log scale per bit)")
            print(f"  Overhead doubles every {analysis['rho_overhead_doubling_bits']:.1f} bits")
            if 'compression_helps' in analysis:
                print(f"  Compression reduces proof growth: {analysis['compression_helps']}")
        else:
            analysis = {}
    else:
        analysis = {}

    RESULTS['exp5_proof_complexity'] = {'data': results, 'analysis': analysis}
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def write_results():
    """Write results to markdown file."""
    out = []
    out.append("# P vs NP Investigation — Phase 5 Results")
    out.append(f"\nGenerated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    out.append("")
    out.append("## Prior Findings (Phases 1-4)")
    out.append("- Dickman Information Barrier: overhead 10^(0.24*d)")
    out.append("- Compression Barrier: semiprimes indistinguishable from random")
    out.append("- No structural predictors (correlation < 0.18)")
    out.append("- No phase transition (smooth scaling)")
    out.append("- 3 barriers block P!=NP proofs")
    out.append("")

    # Exp 1
    out.append("## Experiment 1: Circuit Depth of Factoring")
    out.append("")
    out.append("**Question**: Does the circuit depth for smallest_factor(N) grow polynomially or exponentially?")
    out.append("")
    if 'exp1_circuit_depth' in RESULTS:
        data = RESULTS['exp1_circuit_depth']
        out.append("| Bits | Avg Depth | Median | Max | Poly Exp | Exp Rate |")
        out.append("|------|-----------|--------|-----|----------|----------|")
        for r in data['data']:
            out.append(f"| {r['bits']} | {r['avg_depth']:.1f} | {r['median_depth']:.0f} | "
                       f"{r['max_depth']} | {r['poly_exponent']:.3f} | {r['exp_rate']:.4f} |")
        out.append("")
        if data.get('fit'):
            f = data['fit']
            out.append(f"**Growth model fit**:")
            out.append(f"- Exponential: rate={f.get('exponential_rate', 0):.4f}, "
                       f"residual={f.get('exponential_residual', 0):.4f}")
            out.append(f"- Polynomial: exponent={f.get('polynomial_exponent', 0):.3f}, "
                       f"residual={f.get('polynomial_residual', 0):.4f}")
            out.append(f"- **Better fit: {f.get('better_fit', 'unknown')}**")
        out.append("")

    # Exp 2
    out.append("## Experiment 2: Pseudorandom Factoring Oracle")
    out.append("")
    out.append("**Question**: Does factor knowledge produce better pseudorandom generators?")
    out.append("")
    if 'exp2_prg_oracle' in RESULTS:
        data = RESULTS['exp2_prg_oracle']
        out.append("| N bits | BBS Score | FactorPRG Score | SHA256 Score |")
        out.append("|--------|-----------|-----------------|--------------|")
        for r in data['data']:
            m = r['metrics']
            out.append(f"| {r['bits']} | {m['BBS']['composite_score']:.4f} | "
                       f"{m['FactorPRG']['composite_score']:.4f} | "
                       f"{m['SHA256']['composite_score']:.4f} |")
        out.append("")
        a = data.get('analysis', {})
        if a:
            out.append(f"**Analysis**: Factor knowledge helps PRG: **{a.get('factor_knowledge_helps', 'N/A')}**")
            out.append(f"- Factor PRG / BBS quality ratio: {a.get('factor_prg_vs_bbs_ratio', 0):.3f}")
        out.append("")

    # Exp 3
    out.append("## Experiment 3: Factoring as Optimization Landscape")
    out.append("")
    out.append("**Question**: Does the N mod x landscape structure predict factoring difficulty?")
    out.append("")
    if 'exp3_landscape' in RESULTS:
        data = RESULTS['exp3_landscape']
        out.append("| Bits | Ruggedness | Autocorr Len | Basin Width | Grad Ratio | Rho Iters |")
        out.append("|------|------------|-------------|-------------|------------|-----------|")
        for r in data['data']:
            m = r['avg_metrics']
            out.append(f"| {r['bits']} | {m['ruggedness']:.4f} | {m['autocorr_length']:.1f} | "
                       f"{m['basin_width']:.1f} | {m['gradient_ratio']:.3f} | "
                       f"{m['rho_iters']:.0f} |")
        out.append("")
        a = data.get('analysis', {})
        if a:
            out.append(f"**Analysis**:")
            out.append(f"- Ruggedness trend: {a.get('ruggedness_trend', 0):.6f}/bit "
                       f"({'increasing' if a.get('landscape_increasingly_rugged') else 'decreasing'})")
            for key in ['avg_corr_ruggedness_vs_difficulty', 'avg_corr_basin_width_vs_difficulty',
                        'avg_corr_gradient_ratio_vs_difficulty']:
                if key in a:
                    name = key.replace('avg_corr_', '').replace('_vs_difficulty', '')
                    out.append(f"- Correlation({name}, difficulty): {a[key]:.3f}")
        out.append("")

    # Exp 4
    out.append("## Experiment 4: Entropy of Factoring Algorithm Choices")
    out.append("")
    out.append("**Question**: Does the Shannon entropy of algorithm trajectories predict difficulty?")
    out.append("")
    if 'exp4_algorithm_entropy' in RESULTS:
        data = RESULTS['exp4_algorithm_entropy']
        out.append("| Bits | Avg H | H Rate | H Comp | Avg Iters | Corr(H,iters) |")
        out.append("|------|-------|--------|--------|-----------|---------------|")
        for r in data['data']:
            out.append(f"| {r['bits']} | {r['avg_entropy']:.3f} | {r['avg_entropy_rate']:.3f} | "
                       f"{r['avg_comp_entropy']:.3f} | {r['avg_iterations']:.0f} | "
                       f"{r['corr_entropy_vs_iters']:.3f} |")
        out.append("")
        a = data.get('analysis', {})
        if a:
            out.append(f"**Analysis**:")
            out.append(f"- Entropy trend: {a.get('entropy_trend_per_bit', 0):.4f} bits/bit")
            out.append(f"- Entropy approaches maximum (8.0): {a.get('entropy_approaches_max', 'N/A')}")
            out.append(f"- Avg correlation(entropy, difficulty): {a.get('avg_correlation', 0):.3f}")
            out.append(f"- **Entropy predicts difficulty: {a.get('entropy_predicts_difficulty', 'N/A')}**")
        out.append("")

    # Exp 5
    out.append("## Experiment 5: Kolmogorov Complexity of Factoring Proofs")
    out.append("")
    out.append("**Question**: How does proof complexity scale? Is there a minimum proof complexity?")
    out.append("")
    if 'exp5_proof_complexity' in RESULTS:
        data = RESULTS['exp5_proof_complexity']
        out.append("| Bits | Min Proof | Rho Overhead | Rho Compressed | Trial Overhead |")
        out.append("|------|-----------|-------------|----------------|----------------|")
        for r in data['data']:
            out.append(f"| {r['bits']} | {r['min_proof_bits']}b | "
                       f"{r.get('rho_avg_overhead', 'N/A')}x | "
                       f"{r.get('rho_compressed_overhead', 'N/A')}x | "
                       f"{r.get('trial_avg_overhead', 'N/A')}x |")
        out.append("")
        a = data.get('analysis', {})
        if a:
            out.append(f"**Analysis**:")
            out.append(f"- Rho proof overhead growth: {a.get('rho_overhead_growth_rate', 0):.4f} (log/bit)")
            out.append(f"- Overhead doubles every: {a.get('rho_overhead_doubling_bits', 0):.1f} bits")
            if 'compression_helps' in a:
                out.append(f"- Compression reduces growth rate: {a['compression_helps']}")
        out.append("")

    # Summary
    out.append("## Phase 5 Summary")
    out.append("")
    out.append("### New Findings")
    out.append("")

    findings = []
    if 'exp1_circuit_depth' in RESULTS and RESULTS['exp1_circuit_depth'].get('fit'):
        bf = RESULTS['exp1_circuit_depth']['fit'].get('better_fit', '?')
        findings.append(f"1. **Circuit Depth**: {bf} growth fits better for factoring circuit depth")

    if 'exp2_prg_oracle' in RESULTS and RESULTS['exp2_prg_oracle'].get('analysis'):
        helps = RESULTS['exp2_prg_oracle']['analysis'].get('factor_knowledge_helps', '?')
        findings.append(f"2. **PRG Oracle**: Factor knowledge helps PRG quality: {helps}")

    if 'exp3_landscape' in RESULTS and RESULTS['exp3_landscape'].get('analysis'):
        a = RESULTS['exp3_landscape']['analysis']
        inc = a.get('landscape_increasingly_rugged', '?')
        findings.append(f"3. **Optimization Landscape**: Increasingly rugged with size: {inc}")

    if 'exp4_algorithm_entropy' in RESULTS and RESULTS['exp4_algorithm_entropy'].get('analysis'):
        a = RESULTS['exp4_algorithm_entropy']['analysis']
        pred = a.get('entropy_predicts_difficulty', '?')
        findings.append(f"4. **Algorithm Entropy**: Entropy predicts difficulty: {pred}")

    if 'exp5_proof_complexity' in RESULTS and RESULTS['exp5_proof_complexity'].get('analysis'):
        a = RESULTS['exp5_proof_complexity']['analysis']
        rate = a.get('rho_overhead_growth_rate', 0)
        findings.append(f"5. **Proof Complexity**: Overhead grows at rate {rate:.4f} (log/bit) — "
                        f"{'super-linear' if rate > 0.1 else 'near-linear'} proof bloat")

    for f in findings:
        out.append(f)
    out.append("")

    out.append("### Implications for P vs NP")
    out.append("")
    out.append("These experiments measure the computational structure of factoring from five")
    out.append("orthogonal angles: circuit complexity, pseudorandomness, optimization landscape,")
    out.append("algorithmic entropy, and proof complexity. Combined with phases 1-4, this gives")
    out.append("a comprehensive empirical picture of why factoring resists polynomial-time algorithms.")
    out.append("")

    return "\n".join(out)


def main():
    print("=" * 70)
    print("P vs NP Investigation — Phase 5")
    print("5 New Experiments on Factoring Complexity")
    print("=" * 70)

    t_total = time.time()

    exp1_circuit_depth()
    exp2_prg_oracle()
    exp3_optimization_landscape()
    exp4_algorithm_entropy()
    exp5_proof_complexity()

    total = time.time() - t_total
    print(f"\n{'='*70}")
    print(f"Total time: {fmt_time(total)}")
    print(f"{'='*70}")

    # Write results
    md = write_results()
    with open(os.path.join(os.path.dirname(__file__), "v10_pvsnp_results.md"), "w") as f:
        f.write(md)
    print(f"\nResults written to v10_pvsnp_results.md")

    # Also save raw JSON
    json_path = os.path.join(os.path.dirname(__file__), "v10_pvsnp_results.json")
    with open(json_path, "w") as f:
        json.dump(RESULTS, f, indent=2, default=str)
    print(f"Raw data written to v10_pvsnp_results.json")


if __name__ == "__main__":
    main()
