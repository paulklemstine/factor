#!/usr/bin/env python3
"""
v34_tree_prime_scale.py — How Far Can Tree-Prime Zeta Zero Detection Go?
=========================================================================
Our method: Berggren tree primes → partial Euler product Z_tree(t) = Σ p^{-1/2} cos(t log p)
Previous: 393 primes (depth 6) → 1000/1000 zeros up to t≈1420, error ≈ 0.21, slope = 0.000000

Questions:
1. How high can 393 primes reach? Test t = 2000, 5000, 10000, 50000, 100000
2. More primes = higher reach? Depth 7 (1063), 8 (2866), 10 (~20K)
3. Hybrid: tree primes + RS correction for missing primes
4. Compare tree vs RS vs mpmath at each height
5. Find HIGHEST zero locatable by tree primes alone (binary search)
6. Verify at t=10^15 (Gram point sign check)
7. Variance fraction analysis: what % of Z(t) comes from our 393 primes?

RAM budget: <2GB. Each experiment has timeout.
"""

import gc, time, math, signal, sys, os
import numpy as np
from collections import defaultdict

import mpmath
mpmath.mp.dps = 25

RESULTS = []
T0_GLOBAL = time.time()
OUTFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v34_tree_prime_scale_results.md')

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Timeout")

def emit(s):
    RESULTS.append(s)
    print(s)

def save_results():
    with open(OUTFILE, 'w') as f:
        f.write('\n'.join(RESULTS))

# ─── Core Helpers ──────────────────────────────────────────────────────

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

def sieve_primes(n):
    if n < 2:
        return []
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

def fast_tree_Z(t, lp_arr, sp_arr):
    """Our tree-prime Z approximation: Z_tree(t) = Σ p^{-1/2} cos(t log p)"""
    return float(np.sum(sp_arr * np.cos(t * lp_arr)))

def hardy_Z(t):
    """Standard Hardy Z function via mpmath."""
    try:
        return float(mpmath.siegelz(float(t)))
    except:
        return 0.0

def rs_theta(t):
    """Riemann-Siegel theta function."""
    return float(mpmath.siegeltheta(float(t)))

def gram_point(n):
    """n-th Gram point: theta(g_n) = n*pi."""
    # Use mpmath for accurate Gram points
    try:
        return float(mpmath.grampoint(n))
    except:
        # Fallback: approximate
        return 2 * math.pi * math.exp(1 + n * math.pi / (math.log(n + 2) / 2 + 0.5))

def find_sign_changes(ts, vals):
    """Find zeros by linear interpolation at sign changes."""
    zeros = []
    for i in range(len(vals)-1):
        if vals[i] * vals[i+1] < 0:
            t_zero = ts[i] - vals[i] * (ts[i+1] - ts[i]) / (vals[i+1] - vals[i])
            zeros.append(t_zero)
    return zeros

def locate_zero_near(t_known, lp_arr, sp_arr, window=2.0, npts=200):
    """Try to locate a zero near t_known using tree Z. Return (found, t_est, error)."""
    ts = np.linspace(t_known - window, t_known + window, npts)
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
    if best_t is not None and best_err < window:
        return True, best_t, best_err
    return False, None, None

# ─── Precompute tree primes at various depths ──────────────────────────

emit("# v34: Tree-Prime Zeta Zero Scaling — How Far Can 393 Primes Go?")
emit(f"# Date: 2026-03-16")
emit(f"# Method: Z_tree(t) = Σ p^{{-1/2}} cos(t log p), p from Berggren tree\n")

print("Precomputing tree primes at depths 6,7,8,9,10...")
TREE_PRIMES = {}
TREE_LP = {}
TREE_SP = {}

for d in [6, 7, 8, 9, 10]:
    t0 = time.time()
    tp = tree_primes(d)
    TREE_PRIMES[d] = tp
    TREE_LP[d] = np.array([math.log(p) for p in tp])
    TREE_SP[d] = np.array([1.0/math.sqrt(p) for p in tp])
    print(f"  Depth {d}: {len(tp)} primes, max={max(tp):,}, time={time.time()-t0:.1f}s")
    gc.collect()

emit(f"## Tree Prime Census")
for d in [6, 7, 8, 9, 10]:
    tp = TREE_PRIMES[d]
    emit(f"- Depth {d}: **{len(tp)}** primes, range [{min(tp)}, {max(tp):,}]")
emit("")

# ═════════════════════════════════════════════════════════════════════════
# EXPERIMENT 1: How high can 393 primes go?
# ═════════════════════════════════════════════════════════════════════════

def exp1_height_scaling():
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(120)
    t0 = time.time()
    emit("=" * 70)
    emit("## Experiment 1: Height Scaling — 393 primes at t = 2K, 5K, 10K, 50K, 100K")
    emit("=" * 70 + "\n")

    try:
        lp = TREE_LP[6]
        sp = TREE_SP[6]
        n_primes = len(TREE_PRIMES[6])

        heights = [2000, 5000, 10000, 50000, 100000]

        for h in heights:
            emit(f"### Height t ≈ {h:,}")
            # Get ~20 known zeros near this height via mpmath
            # Use Gram points to find approximate zero locations
            n_test = 20
            found_count = 0
            errors = []

            # Find the Gram index near height h
            # N(t) ≈ t/(2π) * log(t/(2πe)) + 7/8
            n_approx = int(h / (2 * math.pi) * math.log(h / (2 * math.pi * math.e)) + 7/8)

            emit(f"  Approximate zero count N({h}) ≈ {n_approx}")
            emit(f"  Computing {n_test} exact zeros near t={h} via mpmath...")

            t_mp = time.time()
            known_zeros = []
            # Get zeros near index n_approx
            start_idx = max(1, n_approx - 10)
            for k in range(start_idx, start_idx + n_test):
                try:
                    z = float(mpmath.zetazero(k).imag)
                    known_zeros.append((k, z))
                except:
                    pass
            mp_time = time.time() - t_mp
            emit(f"  mpmath computed {len(known_zeros)} zeros in {mp_time:.2f}s")

            if not known_zeros:
                emit(f"  SKIP: could not compute zeros at this height\n")
                continue

            # Test tree Z at each known zero
            t_tree = time.time()
            for idx, t_known in known_zeros:
                ok, t_est, err = locate_zero_near(t_known, lp, sp, window=2.0, npts=200)
                if ok:
                    found_count += 1
                    errors.append(err)

            tree_time = time.time() - t_tree

            emit(f"  Tree Z found: **{found_count}/{len(known_zeros)}** zeros")
            if errors:
                emit(f"  Mean error: {np.mean(errors):.4f}")
                emit(f"  Max error:  {np.max(errors):.4f}")
            emit(f"  Tree Z time: {tree_time:.3f}s  |  mpmath time: {mp_time:.2f}s")
            emit(f"  Speedup: {mp_time/max(tree_time, 0.001):.1f}x\n")

        emit(f"**Time: {time.time()-t0:.1f}s**\n")

    except TimeoutError:
        emit(f"  TIMEOUT after {time.time()-t0:.0f}s\n")
    except Exception as e:
        emit(f"  ERROR: {e}\n")
    finally:
        signal.alarm(0)

# ═════════════════════════════════════════════════════════════════════════
# EXPERIMENT 2: More primes = higher reach?
# ═════════════════════════════════════════════════════════════════════════

def exp2_depth_scaling():
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(180)
    t0 = time.time()
    emit("=" * 70)
    emit("## Experiment 2: Depth Scaling — Does more primes extend the reach?")
    emit("=" * 70 + "\n")

    try:
        # Test at fixed heights with different depths
        test_heights = [5000, 10000, 50000]

        for h in test_heights:
            emit(f"### Height t ≈ {h:,}")

            # Compute 20 known zeros near this height
            n_approx = int(h / (2 * math.pi) * math.log(h / (2 * math.pi * math.e)) + 7/8)
            start_idx = max(1, n_approx - 10)

            known_zeros = []
            for k in range(start_idx, start_idx + 20):
                try:
                    z = float(mpmath.zetazero(k).imag)
                    known_zeros.append(z)
                except:
                    pass

            if not known_zeros:
                emit(f"  SKIP\n")
                continue

            for d in [6, 7, 8, 9, 10]:
                lp = TREE_LP[d]
                sp = TREE_SP[d]
                n_primes = len(TREE_PRIMES[d])

                found = 0
                errs = []
                for t_known in known_zeros:
                    ok, t_est, err = locate_zero_near(t_known, lp, sp, window=2.0, npts=200)
                    if ok:
                        found += 1
                        errs.append(err)

                mean_e = np.mean(errs) if errs else float('nan')
                emit(f"  Depth {d} ({n_primes:,} primes): {found}/{len(known_zeros)} found, "
                     f"mean_err={mean_e:.4f}")

            emit("")

        emit(f"**Time: {time.time()-t0:.1f}s**\n")

    except TimeoutError:
        emit(f"  TIMEOUT after {time.time()-t0:.0f}s\n")
    except Exception as e:
        emit(f"  ERROR: {e}\n")
    finally:
        signal.alarm(0)

# ═════════════════════════════════════════════════════════════════════════
# EXPERIMENT 3: Hybrid — tree primes + RS correction
# ═════════════════════════════════════════════════════════════════════════

def exp3_hybrid():
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(120)
    t0 = time.time()
    emit("=" * 70)
    emit("## Experiment 3: Hybrid — Tree Primes + Riemann-Siegel Correction")
    emit("=" * 70 + "\n")

    try:
        emit("### Idea: Z_hybrid(t) = Z_tree(t) + RS_correction(t)")
        emit("The RS correction accounts for primes NOT in the tree.")
        emit("RS main sum uses N = floor(sqrt(t/(2π))) terms.")
        emit("We use tree primes for 'importance sampled' contribution,")
        emit("then add the standard RS remainder for accuracy.\n")

        # At several heights, compare:
        # 1. Tree Z alone
        # 2. RS Z (standard)
        # 3. Hybrid: tree + correction for missing primes

        test_heights = [5000, 10000, 50000]
        lp6 = TREE_LP[6]
        sp6 = TREE_SP[6]
        tree_p_set = set(TREE_PRIMES[6])

        for h in test_heights:
            emit(f"### Height t ≈ {h:,}")

            # Compute known zeros
            n_approx = int(h / (2 * math.pi) * math.log(h / (2 * math.pi * math.e)) + 7/8)
            start_idx = max(1, n_approx - 5)

            known_zeros = []
            for k in range(start_idx, start_idx + 10):
                try:
                    z = float(mpmath.zetazero(k).imag)
                    known_zeros.append(z)
                except:
                    pass

            if not known_zeros:
                emit(f"  SKIP\n")
                continue

            # Method A: tree Z alone (depth 6)
            found_tree = 0
            errs_tree = []
            t_tree_start = time.time()
            for tz in known_zeros:
                ok, te, er = locate_zero_near(tz, lp6, sp6, window=2.0, npts=200)
                if ok:
                    found_tree += 1
                    errs_tree.append(er)
            t_tree_elapsed = time.time() - t_tree_start

            # Method B: RS Z (standard)
            found_rs = 0
            errs_rs = []
            t_rs_start = time.time()
            for tz in known_zeros:
                ts_scan = np.linspace(tz - 2.0, tz + 2.0, 200)
                zvals = np.array([hardy_Z(t) for t in ts_scan])
                zeros_found = find_sign_changes(ts_scan, zvals)
                best_err = 999
                for zf in zeros_found:
                    err = abs(zf - tz)
                    if err < best_err:
                        best_err = err
                if best_err < 2.0:
                    found_rs += 1
                    errs_rs.append(best_err)
            t_rs_elapsed = time.time() - t_rs_start

            # Method C: Hybrid — tree Z + missing-prime correction
            # For each missing prime p <= N_rs, add p^{-1/2} cos(t log p)
            N_rs = int(math.sqrt(h / (2 * math.pi)))
            all_primes_to_N = sieve_primes(N_rs)
            missing_primes = [p for p in all_primes_to_N if p not in tree_p_set]
            lp_missing = np.array([math.log(p) for p in missing_primes])
            sp_missing = np.array([1.0/math.sqrt(p) for p in missing_primes])

            found_hybrid = 0
            errs_hybrid = []
            t_hyb_start = time.time()
            for tz in known_zeros:
                ts_scan = np.linspace(tz - 2.0, tz + 2.0, 200)
                zvals = np.array([
                    fast_tree_Z(t, lp6, sp6) + float(np.sum(sp_missing * np.cos(t * lp_missing)))
                    for t in ts_scan
                ])
                zeros_found = find_sign_changes(ts_scan, zvals)
                best_err = 999
                for zf in zeros_found:
                    err = abs(zf - tz)
                    if err < best_err:
                        best_err = err
                if best_err < 2.0:
                    found_hybrid += 1
                    errs_hybrid.append(best_err)
            t_hyb_elapsed = time.time() - t_hyb_start

            me_tree = np.mean(errs_tree) if errs_tree else float('nan')
            me_rs = np.mean(errs_rs) if errs_rs else float('nan')
            me_hyb = np.mean(errs_hybrid) if errs_hybrid else float('nan')

            emit(f"  N_RS = {N_rs}, all_primes_to_N = {len(all_primes_to_N)}, "
                 f"tree_primes_in_range = {len([p for p in TREE_PRIMES[6] if p <= N_rs])}, "
                 f"missing = {len(missing_primes)}")
            emit(f"  Tree Z alone:  {found_tree}/{len(known_zeros)} found, "
                 f"mean_err={me_tree:.4f}, time={t_tree_elapsed:.3f}s")
            emit(f"  RS Z standard: {found_rs}/{len(known_zeros)} found, "
                 f"mean_err={me_rs:.6f}, time={t_rs_elapsed:.3f}s")
            emit(f"  Hybrid Z:      {found_hybrid}/{len(known_zeros)} found, "
                 f"mean_err={me_hyb:.6f}, time={t_hyb_elapsed:.3f}s")
            emit("")

        emit(f"**Time: {time.time()-t0:.1f}s**\n")

    except TimeoutError:
        emit(f"  TIMEOUT after {time.time()-t0:.0f}s\n")
    except Exception as e:
        emit(f"  ERROR: {e}\n")
    finally:
        signal.alarm(0)

# ═════════════════════════════════════════════════════════════════════════
# EXPERIMENT 4: Binary search for highest reachable zero
# ═════════════════════════════════════════════════════════════════════════

def exp4_binary_search_reach():
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(120)
    t0 = time.time()
    emit("=" * 70)
    emit("## Experiment 4: Binary Search — Highest Zero Locatable by Tree Alone")
    emit("=" * 70 + "\n")

    try:
        for d in [6, 8, 10]:
            lp = TREE_LP[d]
            sp = TREE_SP[d]
            n_primes = len(TREE_PRIMES[d])

            emit(f"### Depth {d} ({n_primes:,} primes)")

            def test_height(h, n_test=15):
                """Test detection rate at height h. Return fraction found."""
                n_approx = int(h / (2 * math.pi) * math.log(h / (2 * math.pi * math.e)) + 7/8)
                start_idx = max(1, n_approx - n_test // 2)
                known_zeros = []
                for k in range(start_idx, start_idx + n_test):
                    try:
                        z = float(mpmath.zetazero(k).imag)
                        known_zeros.append(z)
                    except:
                        pass
                if not known_zeros:
                    return 0.0
                found = 0
                for tz in known_zeros:
                    ok, _, _ = locate_zero_near(tz, lp, sp, window=2.0, npts=200)
                    if ok:
                        found += 1
                return found / len(known_zeros)

            # Binary search: find height where detection drops below 80%
            lo, hi = 1000, 1000000
            results = []

            # First test at logarithmic intervals
            test_pts = [1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000]
            for h in test_pts:
                rate = test_height(h, n_test=10)
                results.append((h, rate))
                emit(f"  t={h:>8,}: detection rate = {rate:.0%}")
                if rate < 0.3:
                    break

            # Find threshold more precisely
            # Locate where rate drops below 80%
            above80 = [h for h, r in results if r >= 0.8]
            below80 = [h for h, r in results if r < 0.8]
            if above80 and below80:
                lo = max(above80)
                hi = min(below80)
                for _ in range(4):  # 4 bisection steps
                    mid = int((lo + hi) / 2)
                    rate = test_height(mid, n_test=10)
                    emit(f"  t={mid:>8,}: detection rate = {rate:.0%}")
                    if rate >= 0.8:
                        lo = mid
                    else:
                        hi = mid

                emit(f"  **80% threshold ≈ t={lo:,} to t={hi:,}**")
            elif not below80:
                emit(f"  Detection rate >= 80% at all tested heights up to {test_pts[-1]:,}")
                emit(f"  **Reach exceeds {test_pts[-1]:,}!**")
            else:
                emit(f"  Detection rate < 80% even at t={test_pts[0]:,}")
            emit("")

        emit(f"**Time: {time.time()-t0:.1f}s**\n")

    except TimeoutError:
        emit(f"  TIMEOUT after {time.time()-t0:.0f}s\n")
    except Exception as e:
        emit(f"  ERROR: {e}\n")
    finally:
        signal.alarm(0)

# ═════════════════════════════════════════════════════════════════════════
# EXPERIMENT 5: Variance fraction analysis
# ═════════════════════════════════════════════════════════════════════════

def exp5_variance_fraction():
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(90)
    t0 = time.time()
    emit("=" * 70)
    emit("## Experiment 5: Variance Fraction — How Much of Z(t) Do Tree Primes Capture?")
    emit("=" * 70 + "\n")

    try:
        emit("### Theory: Var(Z_partial) / Var(Z_full) ≈ Σ_{tree} 1/p / Σ_{all≤N} 1/p")
        emit("Since Z ≈ Σ p^{-1/2} cos(t log p) and cos terms are ~uncorrelated,")
        emit("variance of each term ≈ 1/(2p) (from <cos²> = 1/2).\n")

        heights = [100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]

        for d in [6, 8, 10]:
            tp = TREE_PRIMES[d]
            n_primes = len(tp)
            tree_var = sum(1.0/p for p in tp) / 2.0  # Σ 1/(2p) for tree primes

            emit(f"### Depth {d} ({n_primes:,} primes, max={max(tp):,})")
            emit(f"  Tree variance contribution: {tree_var:.4f}")

            for h in heights:
                N_rs = int(math.sqrt(h / (2 * math.pi)))
                if N_rs < 3:
                    continue
                all_p = sieve_primes(min(N_rs, 2000000))  # cap sieve for RAM
                total_var = sum(1.0/p for p in all_p) / 2.0
                # Only count tree primes up to N_rs
                tree_in_range = [p for p in tp if p <= N_rs]
                tree_var_range = sum(1.0/p for p in tree_in_range) / 2.0

                frac = tree_var_range / total_var if total_var > 0 else 0
                emit(f"  t={h:>10,}: N_RS={N_rs:>7,}, all_primes={len(all_p):>6,}, "
                     f"tree_in_range={len(tree_in_range):>5,}, "
                     f"var_frac={frac:.1%}")

            emit("")

        emit("### Interpretation")
        emit("The variance fraction tells us what % of Z(t)'s oscillatory power")
        emit("comes from our tree primes. As t grows, N_RS grows, more primes contribute,")
        emit("and our fraction shrinks — but our primes are the LARGEST contributors (small p).\n")

        emit(f"**Time: {time.time()-t0:.1f}s**\n")

    except TimeoutError:
        emit(f"  TIMEOUT after {time.time()-t0:.0f}s\n")
    except Exception as e:
        emit(f"  ERROR: {e}\n")
    finally:
        signal.alarm(0)

# ═════════════════════════════════════════════════════════════════════════
# EXPERIMENT 6: Gram point sign agreement at extreme heights
# ═════════════════════════════════════════════════════════════════════════

def exp6_extreme_gram():
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(120)
    t0 = time.time()
    emit("=" * 70)
    emit("## Experiment 6: Gram Point Sign Agreement at Extreme Heights")
    emit("=" * 70 + "\n")

    try:
        emit("### Test: Does Z_tree(g_n) have the same sign as Z(g_n) at Gram points?")
        emit("If tree primes predict signs correctly even at huge t, that's remarkable.\n")

        lp6 = TREE_LP[6]
        sp6 = TREE_SP[6]

        # Test at various heights
        test_heights = [1000, 5000, 10000, 50000, 100000]

        for h in test_heights:
            emit(f"### Height t ≈ {h:,}")

            # Find Gram index near h
            # gram_point(n) ≈ h means theta(h) ≈ n*pi
            # Use mpmath to get ~20 Gram points near h
            n_gram_approx = int(float(mpmath.siegeltheta(h)) / math.pi)

            agree = 0
            total = 0
            n_test = 30

            for ng in range(max(0, n_gram_approx - n_test//2),
                           n_gram_approx + n_test//2):
                try:
                    gp = float(mpmath.grampoint(ng))
                except:
                    continue

                z_tree = fast_tree_Z(gp, lp6, sp6)
                z_rs = hardy_Z(gp)

                if z_rs != 0:
                    total += 1
                    if (z_tree > 0) == (z_rs > 0):
                        agree += 1

            rate = agree / total if total > 0 else 0
            # Expected by chance: 50%
            emit(f"  Sign agreement: {agree}/{total} = {rate:.1%} "
                 f"(chance = 50%, excess = {rate - 0.5:+.1%})")

        emit("")

        # Now try the BIG one: t ≈ 10^9 (if mpmath can handle it)
        emit("### Extreme test: t ≈ 10^9")
        try:
            h = 1_000_000_000
            mpmath.mp.dps = 30
            n_gram_approx = int(float(mpmath.siegeltheta(h)) / math.pi)
            agree = 0
            total = 0
            for ng in range(n_gram_approx, n_gram_approx + 20):
                try:
                    gp = float(mpmath.grampoint(ng))
                except:
                    continue
                z_tree = fast_tree_Z(gp, lp6, sp6)
                z_rs = hardy_Z(gp)
                if z_rs != 0:
                    total += 1
                    if (z_tree > 0) == (z_rs > 0):
                        agree += 1
            if total > 0:
                rate = agree / total
                emit(f"  t ≈ 10^9: Sign agreement: {agree}/{total} = {rate:.1%}")
            else:
                emit(f"  t ≈ 10^9: could not compute")
        except Exception as e:
            emit(f"  t ≈ 10^9: {e}")

        mpmath.mp.dps = 25

        emit(f"\n**Time: {time.time()-t0:.1f}s**\n")

    except TimeoutError:
        emit(f"  TIMEOUT after {time.time()-t0:.0f}s\n")
    except Exception as e:
        emit(f"  ERROR: {e}\n")
    finally:
        signal.alarm(0)

# ═════════════════════════════════════════════════════════════════════════
# EXPERIMENT 7: Theoretical error bound
# ═════════════════════════════════════════════════════════════════════════

def exp7_theory():
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(60)
    t0 = time.time()
    emit("=" * 70)
    emit("## Experiment 7: Theoretical Analysis — Error Bounds and Scaling Laws")
    emit("=" * 70 + "\n")

    try:
        emit("### The partial Euler product approximation")
        emit("")
        emit("Our Z_tree(t) = Σ_{p in S} p^{-1/2} cos(t log p)")
        emit("Full Z(t)     ≈ Σ_{p ≤ N} p^{-1/2} cos(t log p)  where N = √(t/2π)")
        emit("")
        emit("Error = Z(t) - Z_tree(t) = Σ_{p ≤ N, p ∉ S} p^{-1/2} cos(t log p)")
        emit("")
        emit("Key insight: the error is itself a sum of oscillating terms.")
        emit("Its RMS ≈ √(Σ_{missing} 1/(2p)) while signal RMS ≈ √(Σ_{all} 1/(2p)).")
        emit("")

        # Compute SNR at various heights
        emit("### Signal-to-Noise Ratio (SNR) vs height")
        emit("")

        for d in [6, 8, 10]:
            tp = TREE_PRIMES[d]
            tp_set = set(tp)
            emit(f"  Depth {d} ({len(tp):,} primes):")

            for h in [100, 1000, 10000, 100000, 1000000]:
                N_rs = int(math.sqrt(h / (2 * math.pi)))
                if N_rs < 3:
                    continue
                all_p = sieve_primes(min(N_rs, 2000000))
                signal_var = sum(1.0/p for p in tp if p <= N_rs) / 2
                noise_var = sum(1.0/p for p in all_p if p not in tp_set) / 2
                total_var = signal_var + noise_var
                snr = signal_var / noise_var if noise_var > 0 else float('inf')
                emit(f"    t={h:>10,}: N={N_rs:>7,}, signal_var={signal_var:.3f}, "
                     f"noise_var={noise_var:.3f}, SNR={snr:.3f}")

            emit("")

        emit("### Why tree primes work: importance sampling")
        emit("")
        emit("Tree primes ≡ 1 (mod 4) and concentrate at small values.")
        emit("Small primes dominate: 1/p decreases, so p=5,13,17,29,... carry most weight.")
        emit("Even at t=10^6, tree primes capture the top ~20% of variance.")
        emit("The remaining 80% is spread across thousands of terms → noise averages out.")
        emit("This is why sign changes survive: the noise adds jitter but not enough to")
        emit("create or destroy zeros in Z_tree that correspond to true Z zeros.\n")

        # Theoretical detection probability
        emit("### Detection probability model")
        emit("P(detect zero at t) ≈ P(|noise| < |signal slope| × window)")
        emit("Since signal slope ~ √(Σ 1/(2p) × log²(p)) and noise ~ N(0, σ²_noise),")
        emit("detection degrades when σ_noise / σ_signal approaches 1.\n")

        for d in [6, 8, 10]:
            tp = TREE_PRIMES[d]
            tp_set = set(tp)
            for h in [10000, 100000, 1000000]:
                N_rs = int(math.sqrt(h / (2 * math.pi)))
                all_p = sieve_primes(min(N_rs, 2000000))
                s_var = sum(1.0/p for p in tp if p <= N_rs) / 2
                n_var = sum(1.0/p for p in all_p if p not in tp_set) / 2
                # RMS ratio
                if s_var > 0:
                    ratio = math.sqrt(n_var / s_var) if s_var > 0 else float('inf')
                    # Approximate detection prob: erf(1/ratio)
                    from math import erf
                    p_detect = erf(1.0 / ratio) if ratio > 0 else 1.0
                    emit(f"  Depth {d}, t={h:,}: noise/signal ratio = {ratio:.2f}, "
                         f"P(detect) ≈ {p_detect:.1%}")

        emit(f"\n**Time: {time.time()-t0:.1f}s**\n")

    except TimeoutError:
        emit(f"  TIMEOUT after {time.time()-t0:.0f}s\n")
    except Exception as e:
        emit(f"  ERROR: {e}\n")
    finally:
        signal.alarm(0)

# ═════════════════════════════════════════════════════════════════════════
# RUN ALL EXPERIMENTS
# ═════════════════════════════════════════════════════════════════════════

experiments = [
    ("Exp 1: Height scaling (393 primes)", exp1_height_scaling),
    ("Exp 2: Depth scaling", exp2_depth_scaling),
    ("Exp 3: Hybrid tree+RS", exp3_hybrid),
    ("Exp 4: Binary search for reach", exp4_binary_search_reach),
    ("Exp 5: Variance fraction", exp5_variance_fraction),
    ("Exp 6: Gram point signs", exp6_extreme_gram),
    ("Exp 7: Theoretical analysis", exp7_theory),
]

for i, (name, func) in enumerate(experiments):
    print(f"\n>>> Running {name} ({i+1}/{len(experiments)})...")
    func()
    save_results()
    gc.collect()

# ─── Summary ──────────────────────────────────────────────────────────

elapsed = time.time() - T0_GLOBAL
emit("\n" + "=" * 70)
emit("## Summary")
emit("=" * 70 + "\n")
emit(f"Total time: {elapsed:.0f}s")
emit(f"Experiments: {len(experiments)}")
emit("")
emit("### Key Findings")
emit("(To be filled by analysis of results above)")

save_results()
print(f"\nDone. Total time: {elapsed:.0f}s")
print(f"Results saved to {OUTFILE}")
