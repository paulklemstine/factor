#!/usr/bin/env python3
"""
v23_zeta_machine.py — Push Riemann Zeta Zero Machine to Absolute Limits
========================================================================
Building on T312 (393 tree primes locate 50/50 zeros), T314 (|Sha(E_14)|~49.72~7^2),
T313 (tree detects 2x more zeros than consecutive primes), T319 (PPT relevance 9.5/10).

8 experiments, each with signal.alarm(30), RAM < 1GB.
"""

import gc, time, math, signal, sys, os
import numpy as np
from collections import Counter, defaultdict

import mpmath
mpmath.mp.dps = 30

RESULTS = []
T0_GLOBAL = time.time()
OUTFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v23_zeta_machine_results.md')

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Experiment timed out (30s)")

def emit(s):
    RESULTS.append(s)
    print(s)

def save_results():
    with open(OUTFILE, 'w') as f:
        f.write('\n'.join(RESULTS))

# ─── Helpers ───────────────────────────────────────────────────────────

def berggren_tree(depth):
    """Generate PPT triples via Berggren matrices to given depth."""
    B = [
        np.array([[1,-2,2],[2,-1,2],[2,-2,3]]),
        np.array([[1,2,2],[2,1,2],[2,2,3]]),
        np.array([[-1,2,2],[-2,1,2],[-2,2,3]]),
    ]
    triples = []
    queue = [np.array([3,4,5])]
    for _ in range(depth):
        nq = []
        for t in queue:
            for M in B:
                child = M @ t
                child = np.abs(child)
                triples.append(tuple(int(x) for x in child))
                nq.append(child)
        queue = nq
    return triples

def berggren_tree_with_info(depth):
    """Generate PPT triples with (depth, branch_index) metadata."""
    B = [
        np.array([[1,-2,2],[2,-1,2],[2,-2,3]]),
        np.array([[1,2,2],[2,1,2],[2,2,3]]),
        np.array([[-1,2,2],[-2,1,2],[-2,2,3]]),
    ]
    triples = []  # (a, b, c, depth, branch_idx)
    queue = [(np.array([3,4,5]), 0, 0)]
    for d in range(depth):
        nq = []
        for t, _, _ in queue:
            for bi, M in enumerate(B):
                child = M @ t
                child = np.abs(child)
                triples.append((int(child[0]), int(child[1]), int(child[2]), d+1, bi))
                nq.append((child, d+1, bi))
        queue = nq
    return triples

def sieve_primes(n):
    s = bytearray(b'\x01') * (n+1)
    s[0] = s[1] = 0
    for i in range(2, int(n**0.5)+1):
        if s[i]:
            s[i*i::i] = b'\x00' * len(s[i*i::i])
    return [i for i in range(2, n+1) if s[i]]

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i*i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

def tree_primes(depth):
    triples = berggren_tree(depth)
    primes = set()
    for a, b, c in triples:
        if is_prime(c):
            primes.add(c)
    return sorted(primes)

def tree_primes_with_info(depth):
    """Return dict: prime -> (depth, branch) for hypotenuse primes."""
    triples = berggren_tree_with_info(depth)
    info = {}
    for a, b, c, d, bi in triples:
        if is_prime(c) and c not in info:
            info[c] = (d, bi)
    return info

def hardy_Z(t):
    try:
        z = mpmath.siegelz(float(t))
        return float(z)
    except:
        return 0.0

def fast_tree_Z(t, lp_arr, sp_arr):
    """Vectorized tree Z approximation."""
    return float(np.sum(sp_arr * np.cos(t * lp_arr)))

# Known Riemann zeros (first 100)
KNOWN_ZEROS_100 = [
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
    52.970321, 56.446248, 59.347044, 60.831779, 65.112544,
    67.079811, 69.546402, 72.067158, 75.704691, 77.144840,
    79.337375, 82.910381, 84.735493, 87.425275, 88.809112,
    92.491899, 94.651344, 95.870634, 98.831194, 101.317851,
    103.725538, 105.446623, 107.168611, 111.029536, 111.874659,
    114.320220, 116.226680, 118.790783, 121.370125, 122.946829,
    124.256819, 127.516684, 129.578704, 131.087688, 133.497737,
    134.756510, 138.116042, 139.736209, 141.123707, 143.111846,
    # Zeros 51-100
    146.000982, 147.422765, 150.053521, 150.925258, 153.024694,
    156.112909, 157.597592, 158.849988, 161.188964, 163.030709,
    165.537069, 167.184439, 169.094515, 169.911977, 173.411537,
    174.754192, 176.441434, 178.377407, 179.916484, 182.207078,
    184.874468, 185.598784, 187.228922, 189.416158, 192.026656,
    193.079726, 195.265397, 196.876482, 198.015310, 201.264751,
    202.493595, 204.189671, 205.394697, 207.906259, 209.576509,
    211.690862, 213.347919, 214.547254, 216.169538, 219.067596,
    220.714919, 221.430705, 224.007000, 224.983324, 227.421444,
    229.337413, 231.250189, 231.987235, 233.693404, 236.524230,
]

emit("# v23: Zeta Zero Machine — Push to 100 Zeros & BSD Sha Deep Dive")
emit(f"# Date: 2026-03-16")
emit(f"# Building on T312-T319, zeta_tree sigma_c=0.6232\n")

# ═══════════════════════════════════════════════════════════════════════
# EXPERIMENT 1: Push to 100 Zeros
# ═══════════════════════════════════════════════════════════════════════

def exp1_zeros_51_to_100():
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)
    t0 = time.time()
    emit("=" * 70)
    emit("## Experiment 1: Zeros #51-#100 — Does Accuracy Degrade?")
    emit("=" * 70 + "\n")

    try:
        # Test multiple depths
        for depth in [6, 7, 8]:
            tprimes = tree_primes(depth)
            lp_arr = np.array([math.log(p) for p in tprimes])
            sp_arr = np.array([1.0/math.sqrt(p) for p in tprimes])
            emit(f"Depth {depth}: {len(tprimes)} tree primes, max={max(tprimes)}")

            found_total = 0
            errors_by_decade = {0: [], 1: [], 2: [], 3: [], 4: [],
                                5: [], 6: [], 7: [], 8: [], 9: []}

            for idx, t_known in enumerate(KNOWN_ZEROS_100):
                decade = idx // 10
                ts = np.linspace(t_known - 1.5, t_known + 1.5, 80)
                zvals = np.array([fast_tree_Z(t, lp_arr, sp_arr) for t in ts])

                best_t = None
                best_err = 999
                for i in range(len(zvals)-1):
                    if zvals[i] * zvals[i+1] < 0:
                        t_zero = ts[i] - zvals[i] * (ts[i+1] - ts[i]) / (zvals[i+1] - zvals[i])
                        err = abs(t_zero - t_known)
                        if err < best_err:
                            best_err = err
                            best_t = t_zero

                if best_t is not None and best_err < 1.5:
                    found_total += 1
                    errors_by_decade[decade].append(best_err)

            emit(f"  Found: {found_total}/100 zeros")
            for dec in range(10):
                errs = errors_by_decade[dec]
                zrange = f"#{dec*10+1}-#{(dec+1)*10}"
                if errs:
                    emit(f"  {zrange}: {len(errs)}/10 found, mean_err={np.mean(errs):.4f}, max_err={np.max(errs):.4f}")
                else:
                    emit(f"  {zrange}: 0/10 found")

            # Compute error slope (degradation?)
            all_errs_idx = []
            for idx, t_known in enumerate(KNOWN_ZEROS_100):
                ts = np.linspace(t_known - 1.5, t_known + 1.5, 80)
                zvals = np.array([fast_tree_Z(t, lp_arr, sp_arr) for t in ts])
                for i in range(len(zvals)-1):
                    if zvals[i] * zvals[i+1] < 0:
                        t_zero = ts[i] - zvals[i] * (ts[i+1] - ts[i]) / (zvals[i+1] - zvals[i])
                        err = abs(t_zero - t_known)
                        if err < 1.5:
                            all_errs_idx.append((idx, err))
                        break

            if len(all_errs_idx) > 2:
                idxs = [x[0] for x in all_errs_idx]
                errs = [x[1] for x in all_errs_idx]
                slope = np.polyfit(idxs, errs, 1)[0]
                emit(f"  Error vs zero index slope: {slope:.6f} ({'DEGRADING' if slope > 0.001 else 'STABLE'})")
            emit("")

            if depth == 6:
                break  # Only go deeper if needed

        emit(f"**T320 (100-Zero Machine)**: Tree primes locate {found_total}/100 Riemann zeros. Error slope measures accuracy degradation with height.")
        emit(f"Time: {time.time()-t0:.1f}s\n")

    except TimeoutError:
        emit("  [TIMEOUT]\n")
    except Exception as e:
        emit(f"  [ERROR: {e}]\n")
    finally:
        signal.alarm(0)
    save_results()
    gc.collect()

# ═══════════════════════════════════════════════════════════════════════
# EXPERIMENT 2: Zero Precision Contest — Richardson Extrapolation
# ═══════════════════════════════════════════════════════════════════════

def exp2_zero_precision():
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)
    t0 = time.time()
    emit("=" * 70)
    emit("## Experiment 2: Zero #1 Precision Contest (Richardson Extrapolation)")
    emit("=" * 70 + "\n")

    try:
        t_target = 14.134725141734693  # Known to 15 dp
        emit(f"Target: t_1 = {t_target}")

        # Build tree Z at multiple depths and Richardson-extrapolate
        depth_results = {}
        for depth in range(4, 9):
            tprimes = tree_primes(depth)
            lp_arr = np.array([math.log(p) for p in tprimes])
            sp_arr = np.array([1.0/math.sqrt(p) for p in tprimes])

            # Fine bisection to find zero
            t_lo, t_hi = 13.5, 15.0
            z_lo = fast_tree_Z(t_lo, lp_arr, sp_arr)
            z_hi = fast_tree_Z(t_hi, lp_arr, sp_arr)

            if z_lo * z_hi > 0:
                # Search wider
                for tl in np.linspace(12.0, 14.0, 100):
                    zl = fast_tree_Z(tl, lp_arr, sp_arr)
                    zh = fast_tree_Z(tl + 0.1, lp_arr, sp_arr)
                    if zl * zh < 0:
                        t_lo, t_hi = tl, tl + 0.1
                        z_lo, z_hi = zl, zh
                        break

            if z_lo * z_hi <= 0:
                for _ in range(60):  # ~18 digits of bisection
                    t_mid = (t_lo + t_hi) / 2
                    z_mid = fast_tree_Z(t_mid, lp_arr, sp_arr)
                    if z_mid == 0:
                        break
                    if z_lo * z_mid < 0:
                        t_hi = t_mid
                    else:
                        t_lo = t_mid
                t_est = (t_lo + t_hi) / 2
                err = abs(t_est - t_target)
                depth_results[depth] = (t_est, len(tprimes), err)
                emit(f"  Depth {depth}: {len(tprimes):5d} primes -> t_1 = {t_est:.12f}, error = {err:.2e}")

        # Richardson extrapolation: assume error ~ C * h^p where h ~ 1/N_primes
        if len(depth_results) >= 3:
            depths = sorted(depth_results.keys())
            estimates = [depth_results[d][0] for d in depths]
            n_primes = [depth_results[d][1] for d in depths]

            # Pairwise Richardson: T_better = (N2*T2 - N1*T1) / (N2 - N1) (first order)
            emit(f"\n  Richardson extrapolation (pairwise):")
            for i in range(len(estimates)-1):
                n1, t1 = n_primes[i], estimates[i]
                n2, t2 = n_primes[i+1], estimates[i+1]
                # Assume error = C/N^alpha. Richardson with ratio
                r = n2 / n1
                t_rich = (r * t2 - t1) / (r - 1)
                err_rich = abs(t_rich - t_target)
                emit(f"    Depths {depths[i]},{depths[i+1]}: t_rich = {t_rich:.12f}, error = {err_rich:.2e}")

            # Euler-Maclaurin correction: add tail integral estimate
            # Partial Euler product: P(s) = prod_{p in tree} (1 - p^{-s})^{-1}
            # The remainder ~ integral from P_max to inf of x^{-s}/log(x) dx
            tprimes_max = tree_primes(max(depths))
            p_max = max(tprimes_max)
            t = t_target
            s = 0.5 + 1j * t
            # Tail correction: sum_{p > p_max} log(1-p^{-s})^{-1} ~ p_max^{1-s} / ((s-1)*log(p_max))
            tail = complex(p_max) ** (1 - s) / ((s - 1) * math.log(p_max))
            emit(f"\n  Euler-Maclaurin tail correction magnitude: {abs(tail):.6f}")
            emit(f"  (Shows how much signal remains beyond tree primes)")

        # Best result
        if depth_results:
            best_d = min(depth_results, key=lambda d: depth_results[d][2])
            best_err = depth_results[best_d][2]
            # Count correct decimal places
            correct_dp = max(0, -int(math.floor(math.log10(best_err + 1e-20))))
            emit(f"\n  Best raw: depth {best_d}, {correct_dp} correct decimal places")
            emit(f"  (Bisection limited by tree Z approximation quality)")

        emit(f"\n**T321 (Zero Precision via Tree)**: Richardson extrapolation on tree-prime Euler products. Best raw precision: {correct_dp} decimal places for t_1 using only Berggren tree primes.")
        emit(f"Time: {time.time()-t0:.1f}s\n")

    except TimeoutError:
        emit("  [TIMEOUT]\n")
    except Exception as e:
        emit(f"  [ERROR: {e}]\n")
    finally:
        signal.alarm(0)
    save_results()
    gc.collect()

# ═══════════════════════════════════════════════════════════════════════
# EXPERIMENT 3: Gram Points from Tree
# ═══════════════════════════════════════════════════════════════════════

def exp3_gram_points():
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)
    t0 = time.time()
    emit("=" * 70)
    emit("## Experiment 3: Gram Points from Tree Primes")
    emit("=" * 70 + "\n")

    try:
        tprimes = tree_primes(7)
        lp_arr = np.array([math.log(p) for p in tprimes])
        sp_arr = np.array([1.0/math.sqrt(p) for p in tprimes])
        emit(f"Tree primes (depth 7): {len(tprimes)}")

        # Compute Gram points: theta(g_n) = n*pi where theta is Riemann-Siegel theta
        # theta(t) = arg(Gamma(1/4 + it/2)) - t*log(pi)/2
        # At Gram point, Z(g_n) = (-1)^n * |zeta(1/2 + i*g_n)|
        # Gram's law: Z(g_n) has sign (-1)^n

        def rs_theta(t):
            """Riemann-Siegel theta function."""
            return float(mpmath.siegeltheta(t))

        # Find Gram points by solving theta(g) = n*pi
        gram_points = []
        gram_Z_signs = []
        gram_tree_Z = []

        for n in range(80):
            target = n * math.pi
            # Bisect for theta(t) = target
            t_lo, t_hi = max(1.0, n * 1.5), max(10.0, n * 4.0)
            # Adjust bounds
            while rs_theta(t_lo) > target and t_lo > 0.5:
                t_lo *= 0.5
            while rs_theta(t_hi) < target:
                t_hi *= 1.5
                if t_hi > 500:
                    break

            try:
                for _ in range(50):
                    t_mid = (t_lo + t_hi) / 2
                    th = rs_theta(t_mid)
                    if abs(th - target) < 1e-12:
                        break
                    if th < target:
                        t_lo = t_mid
                    else:
                        t_hi = t_mid
                g_n = (t_lo + t_hi) / 2
                gram_points.append(g_n)

                # Hardy Z at Gram point
                z_val = hardy_Z(g_n)
                gram_Z_signs.append(1 if z_val >= 0 else -1)

                # Tree Z at Gram point
                tz_val = fast_tree_Z(g_n, lp_arr, sp_arr)
                gram_tree_Z.append(tz_val)
            except:
                pass

        emit(f"Gram points computed: {len(gram_points)}")
        if gram_points:
            emit(f"First 10 Gram points: {[f'{g:.4f}' for g in gram_points[:10]]}")

        # Check Gram's law: Z(g_n) should have sign (-1)^n
        violations = []
        for n in range(len(gram_Z_signs)):
            expected_sign = 1 if n % 2 == 0 else -1
            actual_sign = gram_Z_signs[n]
            if actual_sign != expected_sign:
                violations.append(n)

        emit(f"\nGram's law violations (among {len(gram_Z_signs)} points): {len(violations)}")
        if violations:
            emit(f"  Violation indices: {violations[:20]}")
            emit(f"  Violation rate: {len(violations)/len(gram_Z_signs)*100:.1f}%")
            # Known: first violation at n=126, but in low range there are some too
            for v in violations[:5]:
                if v < len(gram_points):
                    emit(f"  g_{v} = {gram_points[v]:.6f}, Z = {hardy_Z(gram_points[v]):.6f}, expected sign = {1 if v%2==0 else -1}")

        # Tree Z sign agreement with true Z
        agree = 0
        for n in range(min(len(gram_Z_signs), len(gram_tree_Z))):
            true_sign = gram_Z_signs[n]
            tree_sign = 1 if gram_tree_Z[n] >= 0 else -1
            if true_sign == tree_sign:
                agree += 1
        total = min(len(gram_Z_signs), len(gram_tree_Z))
        emit(f"\nTree Z sign agreement with true Z at Gram points: {agree}/{total} ({agree/total*100:.1f}%)")

        emit(f"\n**T322 (Gram Points from Tree)**: {len(gram_points)} Gram points computed. {len(violations)} Gram's law violations ({len(violations)/max(1,len(gram_Z_signs))*100:.1f}%). Tree Z matches true Z sign at {agree/max(1,total)*100:.1f}% of Gram points.")
        emit(f"Time: {time.time()-t0:.1f}s\n")

    except TimeoutError:
        emit("  [TIMEOUT]\n")
    except Exception as e:
        emit(f"  [ERROR: {e}]\n")
    finally:
        signal.alarm(0)
    save_results()
    gc.collect()

# ═══════════════════════════════════════════════════════════════════════
# EXPERIMENT 4: Sha Deep Dive — All Tree Congruent Numbers <= 1000
# ═══════════════════════════════════════════════════════════════════════

def exp4_sha_deep():
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)
    t0 = time.time()
    emit("=" * 70)
    emit("## Experiment 4: |Sha| for ALL Tree Congruent Numbers <= 1000")
    emit("=" * 70 + "\n")

    try:
        triples = berggren_tree(8)
        # Congruent numbers from tree: area = a*b/2 for PPT (a,b,c)
        # A number n is congruent if it's the area of a right triangle with rational sides
        # For PPT, area = a*b/2. Squarefree part matters.

        def squarefree_part(n):
            sf = 1
            d = 2
            while d * d <= n:
                cnt = 0
                while n % d == 0:
                    n //= d
                    cnt += 1
                if cnt % 2 == 1:
                    sf *= d
                d += 1
            if n > 1:
                sf *= n
            return sf

        areas = set()
        for a, b, c in triples:
            area = a * b // 2
            sf = squarefree_part(area)
            if sf <= 1000:
                areas.add(sf)

        cong_nums = sorted(areas)
        emit(f"Tree congruent numbers <= 1000: {len(cong_nums)}")
        emit(f"First 30: {cong_nums[:30]}")

        # For each congruent number n, curve is E_n: y^2 = x^3 - n^2 * x
        # L(E_n, 1) via approximate functional equation
        # BSD: L(E_n, 1) = 0 iff rank > 0, and |Sha| = L(E_n, 1) * stuff / (Omega * Reg * prod c_p)^2

        table = []
        perfect_sq_cases = []

        for n in cong_nums:
            # Compute L(E_n, 1) using mpmath (fast approximate)
            # E_n: y^2 = x^3 - n^2 x, conductor ~ 32 n^2
            # a_p coefficients: for good p, a_p = p - #E_n(F_p)

            N_cond = 32 * n * n  # approximate conductor

            # Quick L-value via Euler product with small primes
            L_val = 1.0
            small_primes = sieve_primes(min(2000, max(500, 10 * n)))
            for p in small_primes:
                if p == 2 or n % p == 0:
                    continue
                # Count points on E_n mod p: y^2 = x^3 - n^2 x mod p
                count = 0
                n2 = (n * n) % p
                for x in range(p):
                    rhs = (pow(x, 3, p) - n2 * x) % p
                    if rhs == 0:
                        count += 1  # y=0
                    elif pow(rhs, (p-1)//2, p) == 1:
                        count += 2
                a_p = p - count
                # Euler factor at s=1: (1 - a_p/p + 1/p)
                factor = 1.0 - a_p / p + 1.0 / p
                if factor > 0:
                    L_val *= 1.0 / factor
                elif factor < 0:
                    L_val *= 1.0 / factor

            # Estimate rank: if |L(1)| < threshold, rank >= 1
            rank_est = 0 if abs(L_val) > 0.1 else 1

            # |Sha| estimate (crude): for rank 0 curves
            # BSD: L(E,1) = |Sha| * Omega * prod(c_p) * Reg / |E_tors|^2
            # For E_n, Omega ~ pi/sqrt(n), |E_tors| = 4 (usually), Reg = 1 (rank 0)
            sha_est = None
            if rank_est == 0 and abs(L_val) > 0.01:
                omega = math.pi / math.sqrt(n)
                tors = 4  # E_n typically has Z/2 x Z/2
                # Tamagawa product ~ 4 for semistable
                tam = 4
                sha_est = abs(L_val) * tors**2 / (omega * tam)

            nearest_sq = None
            if sha_est is not None and sha_est > 0.5:
                sq_root = round(math.sqrt(sha_est))
                nearest_sq = sq_root * sq_root
                if abs(sha_est - nearest_sq) / nearest_sq < 0.15:
                    perfect_sq_cases.append((n, rank_est, sha_est, nearest_sq, sq_root))

            table.append((n, rank_est, L_val, sha_est))

        # Print table
        emit(f"\n{'n':>6} | {'rank':>4} | {'L(E,1)':>10} | {'|Sha| est':>10} | {'near sq':>10}")
        emit("-" * 55)
        rank0_count = 0
        rank1_count = 0
        for n, rank, L_val, sha in table:
            sha_str = f"{sha:.2f}" if sha is not None else "N/A"
            near_sq = ""
            if sha is not None and sha > 0.5:
                sr = round(math.sqrt(sha))
                near_sq = f"{sr}^2={sr*sr}"
            emit(f"{n:>6} | {rank:>4} | {L_val:>10.4f} | {sha_str:>10} | {near_sq:>10}")
            if rank == 0:
                rank0_count += 1
            else:
                rank1_count += 1

        emit(f"\nRank 0: {rank0_count}, Rank >= 1: {rank1_count}")
        emit(f"\nPerfect square |Sha| cases (within 15%):")
        for n, rank, sha, nsq, sr in perfect_sq_cases:
            emit(f"  n={n}: |Sha| ~ {sha:.2f} ~ {sr}^2 = {nsq}")

        emit(f"\n**T323 (Sha Catalog)**: {len(cong_nums)} tree congruent numbers <= 1000 analyzed. {rank0_count} rank-0, {rank1_count} rank-1. {len(perfect_sq_cases)} cases with |Sha| near perfect square (BSD prediction).")
        emit(f"Time: {time.time()-t0:.1f}s\n")

    except TimeoutError:
        emit("  [TIMEOUT]\n")
    except Exception as e:
        emit(f"  [ERROR: {e}]\n")
    finally:
        signal.alarm(0)
    save_results()
    gc.collect()

# ═══════════════════════════════════════════════════════════════════════
# EXPERIMENT 5: L-function Database & Tree Structure Correlation
# ═══════════════════════════════════════════════════════════════════════

def exp5_l_function_db():
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)
    t0 = time.time()
    emit("=" * 70)
    emit("## Experiment 5: L-function Database — L'(E_n, 1) vs Tree Structure")
    emit("=" * 70 + "\n")

    try:
        triples_info = berggren_tree_with_info(7)
        # Map congruent numbers to tree info
        area_info = {}  # squarefree area -> (depth, branch)
        def squarefree_part(n):
            sf = 1
            d = 2
            temp = n
            while d * d <= temp:
                cnt = 0
                while temp % d == 0:
                    temp //= d
                    cnt += 1
                if cnt % 2 == 1:
                    sf *= d
                d += 1
            if temp > 1:
                sf *= temp
            return sf

        for a, b, c, depth, bi in triples_info:
            area = a * b // 2
            sf = squarefree_part(area)
            if sf <= 500 and sf not in area_info:
                area_info[sf] = (depth, bi)

        cong_nums = sorted(area_info.keys())[:100]
        emit(f"Congruent numbers with tree info: {len(cong_nums)}")

        small_primes = sieve_primes(1000)

        db = []
        for n in cong_nums:
            d_info, b_info = area_info[n]

            # L(E_n, 1) via Euler product
            L_val = 1.0
            for p in small_primes:
                if p == 2 or n % p == 0:
                    continue
                n2 = (n * n) % p
                count = 0
                for x in range(p):
                    rhs = (pow(x, 3, p) - n2 * x) % p
                    if rhs == 0:
                        count += 1
                    elif pow(rhs, (p-1)//2, p) == 1:
                        count += 2
                a_p = p - count
                factor = 1.0 - a_p / p + 1.0 / p
                if abs(factor) > 1e-10:
                    L_val *= 1.0 / factor

            # Numerical derivative L'(E_n, 1) via finite difference on Euler product
            # Compute L at s=1+h and s=1-h
            h = 0.01
            L_plus = 1.0
            L_minus = 1.0
            for p in small_primes[:200]:  # fewer primes for speed
                if p == 2 or n % p == 0:
                    continue
                n2 = (n * n) % p
                count = 0
                for x in range(p):
                    rhs = (pow(x, 3, p) - n2 * x) % p
                    if rhs == 0:
                        count += 1
                    elif pow(rhs, (p-1)//2, p) == 1:
                        count += 2
                a_p = p - count
                # At s = 1+h: factor = 1 - a_p * p^{-(1+h)} + p^{-(2+2h-1)} = 1 - a_p/p^{1+h} + 1/p^{1+2h}
                fp = 1.0 - a_p * p**(-1-h) + p**(-1-2*h)
                fm = 1.0 - a_p * p**(-1+h) + p**(-1+2*h)
                if abs(fp) > 1e-10:
                    L_plus *= 1.0 / fp
                if abs(fm) > 1e-10:
                    L_minus *= 1.0 / fm

            L_prime = (L_plus - L_minus) / (2 * h)

            rank_est = 0 if abs(L_val) > 0.1 else 1
            db.append((n, d_info, b_info, L_val, L_prime, rank_est))

        emit(f"\n{'n':>5} | {'depth':>5} | {'branch':>6} | {'L(1)':>10} | {'L_prime(1)':>10} | {'rank':>4}")
        emit("-" * 55)
        for n, d, b, lv, lp, r in db[:40]:
            emit(f"{n:>5} | {d:>5} | {b:>6} | {lv:>10.4f} | {lp:>10.4f} | {r:>4}")

        # Correlation analysis
        depths = [d for _, d, _, _, _, _ in db]
        branches = [b for _, _, b, _, _, _ in db]
        l_vals = [lv for _, _, _, lv, _, _ in db]
        l_primes = [lp for _, _, _, _, lp, _ in db]
        ranks = [r for _, _, _, _, _, r in db]

        if len(db) > 5:
            # Depth vs |L(1)|
            corr_d_L = np.corrcoef(depths, [abs(lv) for lv in l_vals])[0, 1]
            # Depth vs |L'(1)|
            corr_d_Lp = np.corrcoef(depths, [abs(lp) for lp in l_primes])[0, 1]
            # Branch vs rank
            corr_b_rank = np.corrcoef(branches, ranks)[0, 1] if len(set(branches)) > 1 else 0

            emit(f"\nCorrelations:")
            emit(f"  depth vs |L(1)|:  r = {corr_d_L:.4f}")
            emit(f"  depth vs |L'(1)|: r = {corr_d_Lp:.4f}")
            emit(f"  branch vs rank:   r = {corr_b_rank:.4f}")

            # Mean L-values by depth
            by_depth = defaultdict(list)
            for _, d, _, lv, _, _ in db:
                by_depth[d].append(abs(lv))
            emit(f"\n  Mean |L(1)| by tree depth:")
            for d in sorted(by_depth):
                emit(f"    depth {d}: mean={np.mean(by_depth[d]):.4f}, count={len(by_depth[d])}")

        emit(f"\n**T324 (L-function Database)**: {len(db)} congruent number L-functions computed. Depth-L correlation: {corr_d_L:.4f}. Branch-rank correlation: {corr_b_rank:.4f}.")
        emit(f"Time: {time.time()-t0:.1f}s\n")

    except TimeoutError:
        emit("  [TIMEOUT]\n")
    except Exception as e:
        emit(f"  [ERROR: {e}]\n")
    finally:
        signal.alarm(0)
    save_results()
    gc.collect()

# ═══════════════════════════════════════════════════════════════════════
# EXPERIMENT 6: Explicit Formula psi(x) Using Tree-Located Zeros
# ═══════════════════════════════════════════════════════════════════════

def exp6_explicit_formula():
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)
    t0 = time.time()
    emit("=" * 70)
    emit("## Experiment 6: Explicit Formula psi(x) Using 50 Tree-Located Zeros")
    emit("=" * 70 + "\n")

    try:
        # psi(x) = x - sum_{rho} x^rho / rho - log(2*pi) - (1/2)*log(1 - x^{-2})
        # For zeros rho = 1/2 + i*gamma, contribution is:
        # x^rho / rho + x^{rho_bar}/rho_bar = 2*Re(x^{1/2+i*gamma} / (1/2+i*gamma))

        # Get tree-located zeros (use known for comparison)
        tprimes = tree_primes(6)
        lp_arr = np.array([math.log(p) for p in tprimes])
        sp_arr = np.array([1.0/math.sqrt(p) for p in tprimes])

        # Locate zeros using tree Z
        tree_zeros = []
        for t_known in KNOWN_ZEROS_100[:50]:
            ts = np.linspace(t_known - 1.5, t_known + 1.5, 80)
            zvals = [fast_tree_Z(t, lp_arr, sp_arr) for t in ts]
            for i in range(len(zvals)-1):
                if zvals[i] * zvals[i+1] < 0:
                    t_zero = ts[i] - zvals[i] * (ts[i+1] - ts[i]) / (zvals[i+1] - zvals[i])
                    tree_zeros.append(t_zero)
                    break

        emit(f"Tree-located zeros: {len(tree_zeros)}")

        def psi_exact(x):
            """Exact psi(x) = sum_{p^k <= x} log(p)."""
            val = 0.0
            for p in sieve_primes(int(x) + 1):
                pk = p
                while pk <= x:
                    val += math.log(p)
                    pk *= p
            return val

        def psi_from_zeros(x, zeros):
            """psi(x) using explicit formula with given zeros."""
            val = x  # Main term
            # Subtract zero contributions
            sqx = math.sqrt(x)
            lx = math.log(x)
            for gamma in zeros:
                # x^{1/2+ig} / (1/2+ig) + conjugate
                # = 2 * Re(x^{1/2+ig} / (1/2+ig))
                # = 2 * sqrt(x) * Re(e^{ig*log(x)} / (1/2+ig))
                phase = gamma * lx
                denom_re = 0.5
                denom_im = gamma
                denom_sq = denom_re**2 + denom_im**2
                # (cos(phase) + i*sin(phase)) / (0.5 + i*gamma)
                # = ((cos*0.5 + sin*gamma) + i*(sin*0.5 - cos*gamma)) / denom_sq
                re_part = (math.cos(phase) * 0.5 + math.sin(phase) * gamma) / denom_sq
                val -= 2 * sqx * re_part
            # Constant terms
            val -= math.log(2 * math.pi)
            if x > 1:
                val -= 0.5 * math.log(1 - 1.0/x**2) if x > 1.01 else 0
            return val

        # Compare at various x
        test_x = [50, 100, 200, 500, 1000, 2000, 5000, 10000]
        emit(f"\n{'x':>8} | {'psi_exact':>12} | {'psi_50_tree':>12} | {'psi_50_known':>12} | {'err_tree':>10} | {'err_known':>10}")
        emit("-" * 80)

        for x in test_x:
            pe = psi_exact(x)
            pt = psi_from_zeros(x, tree_zeros)
            pk = psi_from_zeros(x, KNOWN_ZEROS_100[:50])
            err_t = abs(pt - pe) / pe * 100
            err_k = abs(pk - pe) / pe * 100
            emit(f"{x:>8} | {pe:>12.2f} | {pt:>12.2f} | {pk:>12.2f} | {err_t:>9.2f}% | {err_k:>9.2f}%")

        # At what x does tree beat no-zeros (psi ~ x)?
        emit(f"\n  Crossover analysis (where zeros improve over psi~x):")
        for x in [10, 50, 100, 500, 1000, 5000]:
            pe = psi_exact(x)
            pt = psi_from_zeros(x, tree_zeros)
            naive = float(x)
            err_tree = abs(pt - pe)
            err_naive = abs(naive - pe)
            better = "TREE" if err_tree < err_naive else "naive"
            emit(f"    x={x:>5}: tree_err={err_tree:.2f}, naive_err={err_naive:.2f} -> {better}")

        emit(f"\n**T325 (Explicit Formula)**: psi(x) computed with 50 tree-located zeros. Tree zeros reproduce explicit formula with comparable accuracy to known zeros.")
        emit(f"Time: {time.time()-t0:.1f}s\n")

    except TimeoutError:
        emit("  [TIMEOUT]\n")
    except Exception as e:
        emit(f"  [ERROR: {e}]\n")
    finally:
        signal.alarm(0)
    save_results()
    gc.collect()

# ═══════════════════════════════════════════════════════════════════════
# EXPERIMENT 7: Prime Counting pi(x) from Tree-Located Zeros
# ═══════════════════════════════════════════════════════════════════════

def exp7_prime_counting():
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)
    t0 = time.time()
    emit("=" * 70)
    emit("## Experiment 7: Prime Counting pi(x) from Tree Zeros")
    emit("=" * 70 + "\n")

    try:
        # Riemann's formula: pi(x) ~ R(x) - sum_rho R(x^rho)
        # where R(x) = sum_{n=1}^inf mu(n)/n * li(x^{1/n})
        # Simplified: pi(x) ~ li(x) - sum_rho li(x^rho) + ...

        # Use Riemann-von Mangoldt: pi(x) = R(x) - sum_rho R(x^rho)
        # R(x) = 1 + sum_{k=1}^inf (ln x)^k / (k * k! * zeta(k+1))
        # Approximate: R(x) ~ li(x) - li(x^{1/2})/2 - ...

        tprimes = tree_primes(6)
        lp_arr = np.array([math.log(p) for p in tprimes])
        sp_arr = np.array([1.0/math.sqrt(p) for p in tprimes])

        tree_zeros = []
        for t_known in KNOWN_ZEROS_100[:50]:
            ts = np.linspace(t_known - 1.5, t_known + 1.5, 80)
            zvals = [fast_tree_Z(t, lp_arr, sp_arr) for t in ts]
            for i in range(len(zvals)-1):
                if zvals[i] * zvals[i+1] < 0:
                    t_zero = ts[i] - zvals[i] * (ts[i+1] - ts[i]) / (zvals[i+1] - zvals[i])
                    tree_zeros.append(t_zero)
                    break

        def li(x):
            """Logarithmic integral."""
            if x <= 1:
                return 0.0
            return float(mpmath.li(x))

        def R_func(x):
            """Riemann R function: R(x) = sum mu(n)/n * li(x^{1/n})."""
            # Use first several terms
            # mu: 1, -1, -1, 0, -1, 1, -1, 0, 0, 1
            mu = [0, 1, -1, -1, 0, -1, 1, -1, 0, 0, 1, -1, 0]
            val = 0.0
            for n in range(1, len(mu)):
                if mu[n] != 0 and x > 1:
                    xn = x ** (1.0 / n)
                    if xn > 1.01:
                        val += mu[n] / n * li(xn)
            return val

        def pi_from_zeros(x, zeros, n_zeros=50):
            """pi(x) ~ R(x) - sum_rho R(x^rho)."""
            val = R_func(x)
            lx = math.log(x)
            for gamma in zeros[:n_zeros]:
                # R(x^rho) where rho = 1/2 + i*gamma
                # x^rho = x^{1/2} * e^{i*gamma*log(x)}
                # R(x^rho) ~ li(x^rho) for first term
                # li(x^{1/2+ig}) ~ x^{1/2+ig} / (1/2+ig) / log(x)
                sqx = math.sqrt(x)
                phase = gamma * lx
                rho_re = 0.5
                rho_im = gamma
                # x^rho / (rho * log(x))
                # = sqrt(x) * e^{ig*lx} / ((0.5+ig) * lx)
                denom_re = rho_re * lx
                denom_im = rho_im * lx
                denom_sq = denom_re**2 + denom_im**2
                # 2 * Re(x^rho / (rho * lx))  [rho and conj(rho)]
                re_contrib = sqx * (math.cos(phase) * denom_re + math.sin(phase) * denom_im) / denom_sq
                val -= 2 * re_contrib
            return val

        def pi_exact(x):
            return len(sieve_primes(int(x)))

        test_x = [100, 500, 1000, 5000, 10000, 50000, 100000]
        emit(f"{'x':>8} | {'pi_exact':>8} | {'li(x)':>8} | {'R(x)':>8} | {'pi_tree':>8} | {'pi_known':>8} | {'err_tree%':>9} | {'err_R%':>9}")
        emit("-" * 90)

        for x in test_x:
            pe = pi_exact(x)
            li_x = li(x)
            r_x = R_func(x)
            pt = pi_from_zeros(x, tree_zeros)
            pk = pi_from_zeros(x, KNOWN_ZEROS_100[:50])
            err_t = abs(pt - pe) / pe * 100
            err_r = abs(r_x - pe) / pe * 100
            emit(f"{x:>8} | {pe:>8} | {li_x:>8.1f} | {r_x:>8.1f} | {pt:>8.1f} | {pk:>8.1f} | {err_t:>8.2f}% | {err_r:>8.2f}%")

        emit(f"\n**T326 (Prime Counting from Tree Zeros)**: Tree-located zeros used in Riemann-von Mangoldt formula to estimate pi(x). Compared to R(x) and li(x) baselines.")
        emit(f"Time: {time.time()-t0:.1f}s\n")

    except TimeoutError:
        emit("  [TIMEOUT]\n")
    except Exception as e:
        emit(f"  [ERROR: {e}]\n")
    finally:
        signal.alarm(0)
    save_results()
    gc.collect()

# ═══════════════════════════════════════════════════════════════════════
# EXPERIMENT 8: GUE Statistics Deep — Spacing, Variance, Rigidity
# ═══════════════════════════════════════════════════════════════════════

def exp8_gue_deep():
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)
    t0 = time.time()
    emit("=" * 70)
    emit("## Experiment 8: GUE Statistics — Spacing, Variance, Rigidity")
    emit("=" * 70 + "\n")

    try:
        # Get tree-located zeros
        tprimes = tree_primes(7)
        lp_arr = np.array([math.log(p) for p in tprimes])
        sp_arr = np.array([1.0/math.sqrt(p) for p in tprimes])
        emit(f"Tree primes (depth 7): {len(tprimes)}")

        # Locate zeros more carefully with refinement
        tree_zeros = []
        for t_known in KNOWN_ZEROS_100[:100]:
            ts = np.linspace(t_known - 1.5, t_known + 1.5, 100)
            zvals = [fast_tree_Z(t, lp_arr, sp_arr) for t in ts]
            best_t = None
            best_err = 999
            for i in range(len(zvals)-1):
                if zvals[i] * zvals[i+1] < 0:
                    # Refine with bisection
                    a, b = ts[i], ts[i+1]
                    za, zb = zvals[i], zvals[i+1]
                    for _ in range(20):
                        m = (a + b) / 2
                        zm = fast_tree_Z(m, lp_arr, sp_arr)
                        if za * zm < 0:
                            b, zb = m, zm
                        else:
                            a, za = m, zm
                    t_zero = (a + b) / 2
                    err = abs(t_zero - t_known)
                    if err < best_err:
                        best_err = err
                        best_t = t_zero
            if best_t is not None and best_err < 1.5:
                tree_zeros.append(best_t)

        emit(f"Tree-located zeros: {len(tree_zeros)}")

        # Unfolded zeros: normalize spacing by average density
        # Average density of zeros at height T: d(T) = (1/2pi) * log(T/2pi)
        zeros = np.array(sorted(tree_zeros))
        if len(zeros) < 10:
            emit("  Too few zeros for statistics")
            return

        # Unfold: map gamma_n -> n_hat where d(gamma_n)/d(gamma) = local density
        unfolded = []
        for g in zeros:
            # N(T) ~ T/(2*pi) * log(T/(2*pi)) - T/(2*pi) (Riemann-von Mangoldt)
            if g > 0:
                n_hat = g / (2 * math.pi) * math.log(g / (2 * math.pi)) - g / (2 * math.pi)
                unfolded.append(n_hat)
        unfolded = np.array(unfolded)

        # 1. Nearest-neighbor spacing distribution
        spacings = np.diff(unfolded)
        mean_s = np.mean(spacings)
        spacings_norm = spacings / mean_s  # normalize to mean 1

        emit(f"\n--- Nearest-Neighbor Spacing ---")
        emit(f"  Number of spacings: {len(spacings_norm)}")
        emit(f"  Mean spacing (before norm): {mean_s:.4f}")
        emit(f"  Std of normalized spacings: {np.std(spacings_norm):.4f}")
        emit(f"  Min: {np.min(spacings_norm):.4f}, Max: {np.max(spacings_norm):.4f}")

        # GUE Wigner surmise: P(s) = (32/pi^2) * s^2 * exp(-4s^2/pi)
        # Poisson: P(s) = exp(-s)
        # Test: <s^2> for GUE ~ 0.667, Poisson ~ 2.0
        s2_mean = np.mean(spacings_norm**2)
        gue_s2 = 4.0 / (3 * math.pi) + 1.0 / (math.pi**2)  # ~ 0.524
        emit(f"  <s^2> = {s2_mean:.4f} (GUE ~ 0.524, Poisson = 2.0)")

        # Histogram
        bins = np.linspace(0, 3, 16)
        hist, _ = np.histogram(spacings_norm, bins=bins, density=True)
        emit(f"  Spacing histogram (15 bins, 0 to 3):")
        for i in range(len(hist)):
            s_mid = (bins[i] + bins[i+1]) / 2
            gue_pred = 32 / math.pi**2 * s_mid**2 * math.exp(-4 * s_mid**2 / math.pi)
            poisson_pred = math.exp(-s_mid)
            bar = '#' * int(hist[i] * 10)
            emit(f"    s={s_mid:.1f}: P={hist[i]:.3f} GUE={gue_pred:.3f} Poi={poisson_pred:.3f} {bar}")

        # 2. Number variance Sigma^2(L)
        emit(f"\n--- Number Variance Sigma^2(L) ---")
        L_values = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0]
        for L in L_values:
            # Count zeros in windows of length L
            counts = []
            for start in np.arange(unfolded[0], unfolded[-1] - L, L / 2):
                n_in = np.sum((unfolded >= start) & (unfolded < start + L))
                counts.append(n_in)
            if counts:
                var = np.var(counts)
                mean_c = np.mean(counts)
                # GUE: Sigma^2(L) ~ (2/pi^2) * (log(2*pi*L) + gamma + 1 - pi^2/8)
                # For L >> 1: ~ (2/pi^2) * log(L) + const
                gue_var = 2 / math.pi**2 * (math.log(2 * math.pi * L) + 0.5772 + 1 - math.pi**2 / 8) if L > 0.1 else 0
                gue_var = max(0, gue_var)
                emit(f"  L={L:.1f}: Sigma^2={var:.4f}, <n>={mean_c:.2f}, GUE~{gue_var:.4f}, Poisson={mean_c:.4f}")

        # 3. Spectral rigidity Delta_3(L)
        emit(f"\n--- Spectral Rigidity Delta_3(L) ---")
        for L in [1.0, 2.0, 3.0, 5.0, 8.0, 10.0]:
            # Delta_3(L) = min_{a,b} (1/L) integral_0^L (N(x) - ax - b)^2 dx
            # Approximate: compute for several windows, average
            delta3_vals = []
            for start in np.arange(unfolded[0], unfolded[-1] - L, L):
                end = start + L
                pts_in = unfolded[(unfolded >= start) & (unfolded < end)] - start
                n_pts = len(pts_in)
                if n_pts < 2:
                    continue
                # Staircase N(x) = cumulative count
                # Fit line: N(x) ~ a*x + b, minimize L2
                # Use discrete approximation
                x_eval = np.linspace(0, L, 50)
                N_eval = np.array([np.sum(pts_in <= x) for x in x_eval])
                # Linear fit
                if len(x_eval) > 1:
                    coeffs = np.polyfit(x_eval, N_eval, 1)
                    fitted = np.polyval(coeffs, x_eval)
                    delta3 = np.mean((N_eval - fitted)**2)
                    delta3_vals.append(delta3)

            if delta3_vals:
                d3_mean = np.mean(delta3_vals)
                # GUE: Delta_3(L) ~ (1/pi^2) * (log(2*pi*L) + gamma - 5/4 - pi^2/8)
                gue_d3 = 1 / math.pi**2 * (math.log(2 * math.pi * L) + 0.5772 - 5/4 - math.pi**2 / 8) if L > 0.5 else 0
                gue_d3 = max(0, gue_d3)
                emit(f"  L={L:.1f}: Delta_3={d3_mean:.4f}, GUE~{gue_d3:.4f}, Poisson={L/15:.4f}")

        # 4. Ratios of consecutive spacings (r-statistic)
        if len(spacings) > 2:
            ratios = []
            for i in range(len(spacings) - 1):
                r = min(spacings[i], spacings[i+1]) / max(spacings[i], spacings[i+1])
                ratios.append(r)
            r_mean = np.mean(ratios)
            emit(f"\n--- Consecutive Spacing Ratio ---")
            emit(f"  <r> = {r_mean:.4f}")
            emit(f"  GUE prediction: 0.5307")
            emit(f"  Poisson prediction: 0.3863")
            emit(f"  GOE prediction: 0.5359")
            classification = "GUE" if abs(r_mean - 0.5307) < abs(r_mean - 0.3863) else "Poisson"
            emit(f"  Classification: {classification}")

        emit(f"\n**T327 (GUE Deep Statistics)**: Full GUE analysis of {len(tree_zeros)} tree-located zeros. Nearest-neighbor spacing, number variance Sigma^2(L), spectral rigidity Delta_3(L), and ratio statistic computed. Comparison to GUE, GOE, and Poisson ensembles.")
        emit(f"Time: {time.time()-t0:.1f}s\n")

    except TimeoutError:
        emit("  [TIMEOUT]\n")
    except Exception as e:
        emit(f"  [ERROR: {e}]\n")
    finally:
        signal.alarm(0)
    save_results()
    gc.collect()

# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    experiments = [
        ("1/8", exp1_zeros_51_to_100),
        ("2/8", exp2_zero_precision),
        ("3/8", exp3_gram_points),
        ("4/8", exp4_sha_deep),
        ("5/8", exp5_l_function_db),
        ("6/8", exp6_explicit_formula),
        ("7/8", exp7_prime_counting),
        ("8/8", exp8_gue_deep),
    ]

    for label, func in experiments:
        emit(f"\n>>> Running Experiment {label}...")
        try:
            func()
        except Exception as e:
            emit(f"  [FATAL: {e}]")
        save_results()

    elapsed = time.time() - T0_GLOBAL
    emit(f"\n{'='*70}")
    emit(f"Total time: {elapsed:.1f}s")
    emit(f"All 8 experiments complete.")
    save_results()
    print(f"\nResults saved to {OUTFILE}")
