#!/usr/bin/env python3
"""
Ergodic Theory & Stochastic Calculus experiments for ECDLP.

AREA 1: Doubling orbit discrepancy on EC — does the sequence {x(2^i P)}
         leak information about the discrete log k?

AREA 2: Optimal jump distribution for kangaroo walks — what 64-jump
         distribution minimizes expected collision time?

Pure Python + gmpy2.  Memory < 200 MB.  Each trial alarm-guarded at 30s.
"""

import time
import math
import random
import signal
import sys
import statistics
from collections import defaultdict

import gmpy2
from gmpy2 import mpz

# ---------------------------------------------------------------------------
# Import EC primitives from the project
# ---------------------------------------------------------------------------
sys.path.insert(0, "/home/raver1975/factor")
from ecdlp_pythagorean import (
    ECPoint, EllipticCurve, FastCurve, secp256k1_curve,
)


# ---------------------------------------------------------------------------
# Timeout helper
# ---------------------------------------------------------------------------
class TimeoutError(Exception):
    pass

def _alarm_handler(signum, frame):
    raise TimeoutError("Trial timed out")

signal.signal(signal.SIGALRM, _alarm_handler)


# ===================================================================
#  AREA 1 — Ergodic / Doubling-Orbit Discrepancy
# ===================================================================

def doubling_orbit_xcoords(curve, P, L):
    """Return x-coordinates of P, 2P, 4P, ..., 2^L * P (normalised to [0,1))."""
    p = int(curve.p)
    xs = []
    Q = P
    for _ in range(L + 1):
        xs.append(int(Q.x) / p)
        Q = curve.double(Q)
    return xs


def ks_test_uniform(samples):
    """Kolmogorov-Smirnov statistic vs U[0,1)."""
    n = len(samples)
    ss = sorted(samples)
    D = 0.0
    for i, v in enumerate(ss):
        d1 = abs(v - i / n)
        d2 = abs(v - (i + 1) / n)
        D = max(D, d1, d2)
    return D


def serial_correlation(xs):
    """Lag-1 serial correlation coefficient."""
    n = len(xs)
    if n < 3:
        return 0.0
    m = sum(xs) / n
    c0 = sum((x - m) ** 2 for x in xs) / n
    if c0 == 0:
        return 0.0
    c1 = sum((xs[i] - m) * (xs[i + 1] - m) for i in range(n - 1)) / (n - 1)
    return c1 / c0


def gap_test(xs, alpha=0.25, beta=0.75):
    """Mean gap length (runs outside [alpha, beta])."""
    gaps = []
    g = 0
    for x in xs:
        if alpha <= x <= beta:
            gaps.append(g)
            g = 0
        else:
            g += 1
    if not gaps:
        return 0.0
    return sum(gaps) / len(gaps)


def spectral_test_r2(xs):
    """Simple spectral test: |sum exp(2 pi i x_j)|^2 / n for the fundamental freq."""
    n = len(xs)
    re = sum(math.cos(2 * math.pi * x) for x in xs)
    im = sum(math.sin(2 * math.pi * x) for x in xs)
    return (re * re + im * im) / n


def area1_small_curve_test():
    """
    Test on a small curve where we can enumerate everything.
    Compare structured k (small, smooth) vs random k.
    """
    print("=" * 70)
    print("AREA 1a: Doubling orbit test on SMALL curve (toy, p ~ 1e4)")
    print("=" * 70)

    # Use a small curve: y^2 = x^3 + 7 mod p, find a suitable p
    for p_cand in range(10007, 11000):
        if gmpy2.is_prime(p_cand):
            p = p_cand
            break
    curve = EllipticCurve(a=0, b=7, p=p)
    G = curve.find_generator()
    if G is None:
        print("  Could not find generator for small curve, skipping.")
        return {}

    # Find order of G by brute force (small curve)
    Q = G
    order = 1
    for i in range(1, p + 2):
        Q = curve.add(Q, G)
        if Q.is_infinity:
            order = i + 1
            break
    print(f"  Curve: y^2 = x^3 + 7 mod {p}, G order = {order}")

    L = min(80, order - 2)  # orbit length

    # Structured k values (small, smooth)
    structured_ks = [2, 3, 5, 7, 8, 12, 16, 24, 32, 48, 64, 100, 128, 256]
    structured_ks = [k for k in structured_ks if 1 < k < order]

    # Random k values
    rng = random.Random(42)
    random_ks = [rng.randint(order // 4, 3 * order // 4) for _ in range(20)]

    results = {"structured": [], "random": []}

    for label, ks in [("structured", structured_ks), ("random", random_ks)]:
        for k in ks:
            P = curve.scalar_mult(k, G)
            xs = doubling_orbit_xcoords(curve, P, L)
            ks_stat = ks_test_uniform(xs)
            sc = serial_correlation(xs)
            gt = gap_test(xs)
            sp = spectral_test_r2(xs)
            results[label].append({
                "k": k, "KS": ks_stat, "serial_corr": sc,
                "gap": gt, "spectral": sp
            })

    for label in ["structured", "random"]:
        ks_vals = [r["KS"] for r in results[label]]
        sc_vals = [r["serial_corr"] for r in results[label]]
        sp_vals = [r["spectral"] for r in results[label]]
        print(f"\n  {label.upper()} k (n={len(results[label])}):")
        print(f"    KS stat:       mean={statistics.mean(ks_vals):.4f}  std={statistics.stdev(ks_vals) if len(ks_vals)>1 else 0:.4f}")
        print(f"    Serial corr:   mean={statistics.mean(sc_vals):.4f}  std={statistics.stdev(sc_vals) if len(sc_vals)>1 else 0:.4f}")
        print(f"    Spectral R2:   mean={statistics.mean(sp_vals):.4f}  std={statistics.stdev(sp_vals) if len(sp_vals)>1 else 0:.4f}")

    return results


def area1_secp256k1_test():
    """
    Test on secp256k1: compute doubling orbit of P = kG for structured vs random k.
    L=100 doublings.  Compare KS, serial correlation, spectral.
    """
    print("\n" + "=" * 70)
    print("AREA 1b: Doubling orbit test on secp256k1 (L=100)")
    print("=" * 70)

    curve = secp256k1_curve()
    n = curve.n
    L = 100

    # Structured k: small integers, powers of 2, smooth numbers
    structured_ks = [2, 3, 5, 7, 16, 64, 256, 1024, 2**20, 2**30,
                     2 * 3 * 5 * 7 * 11, 2**10 * 3**5]
    # Random k: large random values
    rng = random.Random(123)
    random_ks = [rng.randint(2**200, 2**255) for _ in range(12)]

    results = {"structured": [], "random": []}

    for label, ks in [("structured", structured_ks), ("random", random_ks)]:
        for k in ks:
            signal.alarm(30)
            try:
                P = curve.scalar_mult(k, curve.G)
                xs = []
                Q = P
                p_int = int(curve.p)
                for i in range(L + 1):
                    xs.append(int(Q.x) / p_int)
                    Q = curve.double(Q)
                ks_stat = ks_test_uniform(xs)
                sc = serial_correlation(xs)
                sp = spectral_test_r2(xs)
                results[label].append({
                    "k": k, "KS": ks_stat, "serial_corr": sc, "spectral": sp
                })
            except TimeoutError:
                print(f"  TIMEOUT for k={k}")
            finally:
                signal.alarm(0)

    for label in ["structured", "random"]:
        if not results[label]:
            continue
        ks_vals = [r["KS"] for r in results[label]]
        sc_vals = [r["serial_corr"] for r in results[label]]
        sp_vals = [r["spectral"] for r in results[label]]
        print(f"\n  {label.upper()} k (n={len(results[label])}):")
        print(f"    KS stat:       mean={statistics.mean(ks_vals):.4f}  std={statistics.stdev(ks_vals) if len(ks_vals)>1 else 0:.4f}")
        print(f"    Serial corr:   mean={statistics.mean(sc_vals):.4f}  std={statistics.stdev(sc_vals) if len(sc_vals)>1 else 0:.4f}")
        print(f"    Spectral R2:   mean={statistics.mean(sp_vals):.4f}  std={statistics.stdev(sp_vals) if len(sp_vals)>1 else 0:.4f}")

    # Detailed per-k comparison
    print("\n  Per-k detail (first 5 of each):")
    for label in ["structured", "random"]:
        print(f"    {label.upper()}:")
        for r in results[label][:5]:
            k_str = str(r["k"])[:30]
            print(f"      k={k_str:>30s}  KS={r['KS']:.4f}  sc={r['serial_corr']:.4f}  sp={r['spectral']:.4f}")

    return results


# ===================================================================
#  AREA 2 — Stochastic / Optimal Jump Distribution for Kangaroo
# ===================================================================

def rho_walk_collision(N, jumps, max_steps, rng):
    """
    Simulate a Pollard-kangaroo-style walk on Z/NZ using distinguished points.

    Tame walker starts at N//2 (middle of [0,N]), walks right.
    Wild walker starts at random point in [0,N], walks right.
    Both use: x -> x + jumps[h(x) % num_jumps]  (mod N)

    When a walker hits a distinguished point (low bits = 0), it stores
    (position -> total_distance). If both walkers hit the same DP,
    we have a collision and can recover the difference.

    Returns the total number of steps (both walkers combined).
    """
    num_jumps = len(jumps)
    mean_jump = sum(jumps) // num_jumps

    # DP frequency: expect ~sqrt(N) steps, store ~sqrt(sqrt(N)) DPs
    dp_bits = max(1, int(math.log2(max(2, N ** 0.25))))
    dp_mask = (1 << dp_bits) - 1

    def step_fn(x):
        j = ((x * 2654435761) >> 16) % num_jumps
        return (x + jumps[j]) % N

    # Tame: starts at N//2, walks for ~sqrt(N) steps, recording DPs
    tame_start = N // 2
    tame_pos = tame_start
    tame_dist = 0
    dp_table = {}  # pos -> (dist, "T"|"W")

    wild_start = rng.randint(0, N - 1)
    wild_pos = wild_start
    wild_dist = 0

    for s in range(1, max_steps + 1):
        # Alternate tame and wild steps
        # Tame step
        j = ((tame_pos * 2654435761) >> 16) % num_jumps
        tame_dist += jumps[j]
        tame_pos = (tame_pos + jumps[j]) % N
        if (tame_pos & dp_mask) == 0:
            if tame_pos in dp_table:
                tag = dp_table[tame_pos][1]
                if tag == "W":
                    return 2 * s
            dp_table[tame_pos] = (tame_dist, "T")

        # Wild step
        j = ((wild_pos * 2654435761) >> 16) % num_jumps
        wild_dist += jumps[j]
        wild_pos = (wild_pos + jumps[j]) % N
        if (wild_pos & dp_mask) == 0:
            if wild_pos in dp_table:
                tag = dp_table[wild_pos][1]
                if tag == "T":
                    return 2 * s
            dp_table[wild_pos] = (wild_dist, "W")

    return max_steps


def generate_jump_distribution(dist_type, num_jumps, mean_jump):
    """
    Generate a set of jump sizes for given distribution type.
    All distributions are normalized so that the average jump ~ mean_jump.
    This ensures fair comparison across distribution shapes.
    """
    if dist_type == "powers_of_2":
        # Standard Pollard: 2^0, 2^1, ..., 2^(r-1) where 2^r ~ 2*mean
        r = max(1, int(math.log2(max(1, 2 * mean_jump))))
        raw = [1 << (i * r // num_jumps) for i in range(num_jumps)]

    elif dist_type == "uniform":
        # Uniform spacing from 1 to 2*mean
        raw = [max(1, int(2 * mean_jump * (i + 1) / num_jumps))
               for i in range(num_jumps)]

    elif dist_type == "geometric":
        # Geometric progression from 1 to 2*mean
        ratio = (2 * mean_jump) ** (1.0 / max(1, num_jumps - 1))
        raw = [max(1, int(ratio ** i)) for i in range(num_jumps)]

    elif dist_type == "levy_like":
        # Heavy-tailed: most jumps small, a few very large, capped at 4*mean
        raw = []
        for i in range(num_jumps):
            # Pareto-like: j ~ (i+1)^2
            raw.append(max(1, int(mean_jump * 0.02 * (i + 1) ** 2)))
        cap = 4 * mean_jump
        raw = [min(j, cap) for j in raw]

    elif dist_type == "entropy_max":
        # Entropy-maximizing: all jumps equal (max entropy for fixed mean)
        raw = [mean_jump] * num_jumps

    elif dist_type == "gaussian_like":
        # Jumps concentrated around mean, Gaussian-shaped
        raw = []
        for i in range(num_jumps):
            z = (i - num_jumps / 2) / (num_jumps / 6)
            w = math.exp(-z * z / 2)
            raw.append(max(1, int(mean_jump * w * 2)))

    else:
        raise ValueError(f"Unknown dist_type: {dist_type}")

    # Normalize so average ~ mean_jump
    avg = sum(raw) / len(raw)
    if avg > 0:
        scale = mean_jump / avg
        raw = [max(1, int(j * scale)) for j in raw]
    return raw


def area2_jump_distribution_comparison():
    """
    Simulate kangaroo walks with different jump distributions.
    Measure mean collision steps for N = 2^20 .. 2^28.
    """
    print("\n" + "=" * 70)
    print("AREA 2a: Jump distribution comparison (kangaroo on Z/NZ)")
    print("=" * 70)

    dist_types = ["powers_of_2", "uniform", "geometric",
                  "levy_like", "entropy_max", "gaussian_like"]
    num_jumps = 64
    rng = random.Random(999)

    # Header
    header = f"{'N bits':>7s}  {'trials':>6s}"
    for dt in dist_types:
        header += f"  {dt:>14s}"
    print(f"\n  {header}")
    print("  " + "-" * len(header))

    all_results = {}

    for nbits in [14, 16, 18, 20, 22]:
        trials_per_config = max(200, 2000 >> max(0, (nbits - 16) // 2))
        signal.alarm(30)
        try:
            N = 1 << nbits
            mean_jump = int(N ** 0.5)
            max_steps = int(50 * N ** 0.5)
            row = f"{nbits:>7d}  {trials_per_config:>6d}"

            for dt in dist_types:
                jumps = generate_jump_distribution(dt, num_jumps, mean_jump)
                steps_list = []
                for _ in range(trials_per_config):
                    s = rho_walk_collision(N, jumps, max_steps, rng)
                    steps_list.append(s)
                mean_steps = statistics.mean(steps_list)
                ratio = mean_steps / (N ** 0.5)
                row += f"  {ratio:>14.3f}"
                all_results.setdefault(dt, []).append((nbits, mean_steps, ratio))

            print(f"  {row}")
        except TimeoutError:
            print(f"  TIMEOUT at {nbits} bits")
            break
        finally:
            signal.alarm(0)

    print("\n  (Values shown are mean_steps / sqrt(N) — lower is better)")

    return all_results


def area2_gradient_descent_optimal():
    """
    Use gradient descent to find the optimal 64-jump distribution
    that minimizes expected collision time on Z/NZ for N=2^22.
    """
    print("\n" + "=" * 70)
    print("AREA 2b: Gradient descent for optimal 64-jump distribution")
    print("=" * 70)

    N = 1 << 16
    num_jumps = 64
    trials = 500
    max_steps = int(50 * N ** 0.5)
    rng = random.Random(7777)

    def evaluate(jumps, n_trials):
        total = 0
        r = random.Random(42)  # fixed seed for fair comparison
        for _ in range(n_trials):
            s = rho_walk_collision(N, jumps, max_steps, r)
            total += s
        return total / n_trials

    # Start with powers of 2, capped at N
    log_N = math.log(N)
    log_jumps = [min(math.log(max(1, 1 << i)), log_N) for i in range(num_jumps)]

    best_jumps = [max(1, min(N, int(math.exp(lj)))) for lj in log_jumps]
    best_score = evaluate(best_jumps, trials)
    print(f"  Initial (powers_of_2): mean_steps={best_score:.1f}, ratio={best_score / N**0.5:.3f}")

    # Coordinate descent: perturb each jump size, keep if improvement
    lr = 0.3
    for iteration in range(5):
        signal.alarm(30)
        try:
            improved = 0
            for j_idx in range(num_jumps):
                for direction in [+1, -1]:
                    new_log = log_jumps.copy()
                    new_log[j_idx] = min(new_log[j_idx] + direction * lr, log_N)
                    new_jumps = [max(1, min(N, int(math.exp(lj)))) for lj in new_log]
                    score = evaluate(new_jumps, trials)
                    if score < best_score:
                        best_score = score
                        best_jumps = new_jumps
                        log_jumps = new_log
                        improved += 1
            print(f"  Iter {iteration}: mean_steps={best_score:.1f}, ratio={best_score / N**0.5:.3f}, improved={improved}")
            if improved == 0:
                lr *= 0.5
        except TimeoutError:
            print(f"  TIMEOUT at iteration {iteration}")
            break
        finally:
            signal.alarm(0)

    # Show the optimal distribution
    print(f"\n  Best ratio: {best_score / N**0.5:.3f}")
    print(f"  Jump sizes (sorted): {sorted(best_jumps)[:10]} ... {sorted(best_jumps)[-5:]}")

    # Compare with theory: optimal mean = sqrt(N), geometric spread
    mean_j = sum(best_jumps) / len(best_jumps)
    median_j = sorted(best_jumps)[len(best_jumps) // 2]
    max_j = max(best_jumps)
    min_j = min(best_jumps)
    print(f"  Jump stats: mean={mean_j:.0f}, median={median_j}, min={min_j}, max={max_j}")
    print(f"  sqrt(N) = {N**0.5:.0f}  (N = 2^16 = {N})")

    return best_jumps, best_score


def area2_bounded_vs_unbounded():
    """
    Test if the optimal jump distribution differs for bounded [0, N] vs unbounded search.
    In bounded search, the target is known to be in [0, N].
    In 'unbounded', we use a larger space but same target range.
    """
    print("\n" + "=" * 70)
    print("AREA 2c: Bounded vs unbounded search space")
    print("=" * 70)

    num_jumps = 64
    trials = 500
    rng = random.Random(2222)

    for nbits in [20, 24]:
        N = 1 << nbits
        mean_jump = int(N ** 0.5)
        max_steps = int(5 * N ** 0.5)

        # Bounded: search in [0, N]
        jumps_pow2 = [1 << i for i in range(num_jumps)]

        # "Bounded-aware": jumps capped at N/4
        cap = N // 4
        jumps_capped = [min(1 << i, cap) for i in range(num_jumps)]

        # Small jumps only (< sqrt(N))
        jumps_small = [max(1, (i + 1) * mean_jump // num_jumps) for i in range(num_jumps)]

        signal.alarm(30)
        try:
            for label, jumps in [("powers_of_2", jumps_pow2),
                                  ("capped_N/4", jumps_capped),
                                  ("small_sqrt", jumps_small)]:
                steps_list = []
                for _ in range(trials):
                    s = rho_walk_collision(N, jumps, max_steps, rng)
                    steps_list.append(s)
                mean_s = statistics.mean(steps_list)
                print(f"  N=2^{nbits}, {label:>14s}: mean_steps={mean_s:.0f}, ratio={mean_s / N**0.5:.3f}")
        except TimeoutError:
            print(f"  TIMEOUT at {nbits} bits")
        finally:
            signal.alarm(0)
        print()


# ===================================================================
#  MAIN
# ===================================================================

def main():
    t0 = time.time()
    print("Ergodic Theory & Stochastic Calculus for ECDLP")
    print("=" * 70)

    # --- AREA 1 ---
    print("\n*** AREA 1: Doubling Orbit Discrepancy ***\n")
    r1a = area1_small_curve_test()
    r1b = area1_secp256k1_test()

    # --- AREA 2 ---
    print("\n\n*** AREA 2: Optimal Jump Distribution ***\n")
    r2a = area2_jump_distribution_comparison()
    r2b = area2_gradient_descent_optimal()
    r2c = area2_bounded_vs_unbounded()

    elapsed = time.time() - t0

    # --- Summary ---
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print("\nAREA 1 (Ergodic / Doubling Orbit):")
    print("  H_ERGODIC hypothesis: Can the doubling orbit discrepancy")
    print("  distinguish structured k from random k?")
    if r1a:
        s_ks = statistics.mean([r["KS"] for r in r1a.get("structured", [])]) if r1a.get("structured") else 0
        r_ks = statistics.mean([r["KS"] for r in r1a.get("random", [])]) if r1a.get("random") else 0
        diff = abs(s_ks - r_ks)
        print(f"  Small curve: structured KS={s_ks:.4f} vs random KS={r_ks:.4f}, diff={diff:.4f}")
        if diff < 0.05:
            print("  -> NO significant difference detected (as expected by theory)")
        else:
            print(f"  -> Difference of {diff:.4f} detected — investigate further")

    if r1b:
        s_ks = statistics.mean([r["KS"] for r in r1b.get("structured", [])]) if r1b.get("structured") else 0
        r_ks = statistics.mean([r["KS"] for r in r1b.get("random", [])]) if r1b.get("random") else 0
        diff = abs(s_ks - r_ks)
        print(f"  secp256k1:   structured KS={s_ks:.4f} vs random KS={r_ks:.4f}, diff={diff:.4f}")
        if diff < 0.05:
            print("  -> NO significant difference (orbit is pseudorandom regardless of k)")
        else:
            print(f"  -> Difference of {diff:.4f} — but L=100 is very short, likely noise")

    print("\nAREA 2 (Stochastic / Jump Distribution):")
    print("  H_STOCH hypothesis: Is there a jump distribution better than")
    print("  powers-of-2 for kangaroo collision?")
    if r2a:
        # Find best distribution at largest N tested
        for dt, vals in r2a.items():
            if vals:
                last = vals[-1]
                print(f"    {dt:>14s}: ratio={last[2]:.3f} at {last[0]}b")

    print(f"\n  Total runtime: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
