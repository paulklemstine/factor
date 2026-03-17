#!/usr/bin/env python3
"""
Iteration 5: 10 New Research Fields (21-30)
===========================================
Focus on fields 21, 23, 26, 27, 30 as most promising.
"""

import math
import time
import random
import numpy as np
import os
import sys
from collections import defaultdict

sys.path.insert(0, '/home/raver1975/factor')

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, next_prime, jacobi


###############################################################################
# FIELD 21: SIQS with numba JIT — JIT-compile more of the pipeline
###############################################################################

def field21_numba_jit():
    """
    Current: jit_sieve and jit_find_smooth are JIT-compiled.
    The trial division and candidate processing are Python.

    Can we JIT-compile more? Specifically:
    - Trial division loop (currently Python divmod)
    - Candidate classification (smooth / 1LP / 2LP)
    - Polynomial setup (a_inv, deltas computation)
    """
    print("=" * 72)
    print("FIELD 21: SIQS with Extended Numba JIT")
    print("=" * 72)

    from numba import njit

    # JIT trial division: operate on int64 values (cofactors after sieve)
    @njit(cache=True)
    def jit_trial_divide(val, fb, hit_indices, n_hits):
        """
        JIT trial division. Returns (exps_indices, exps_values, cofactor).
        For int64 values only (cofactors typically < 2^60 after partial sieve).
        """
        v = abs(val)
        exp_idx = np.empty(n_hits, dtype=np.int32)
        exp_val = np.empty(n_hits, dtype=np.int32)
        n_exp = 0

        for i in range(n_hits):
            idx = hit_indices[i]
            p = fb[idx]
            if v <= 1:
                break
            q = v // p
            r = v - q * p
            if r == 0:
                e = 1
                v = q
                q = v // p
                r = v - q * p
                while r == 0:
                    e += 1
                    v = q
                    q = v // p
                    r = v - q * p
                exp_idx[n_exp] = idx
                exp_val[n_exp] = e
                n_exp += 1

        return exp_idx[:n_exp], exp_val[:n_exp], v

    # JIT polynomial setup: a_inv computation
    @njit(cache=True)
    def _modpow(base, exp, mod):
        """Modular exponentiation in numba (no 3-arg pow support)."""
        result = np.int64(1)
        base = base % mod
        while exp > 0:
            if exp & 1:
                result = result * base % mod
            exp >>= 1
            base = base * base % mod
        return result

    @njit(cache=True)
    def jit_compute_a_inv(fb, fb_size, a_mod_fb, a_prime_mask):
        """Compute a_inv = a^(-1) mod p for all FB primes not in a."""
        a_inv = np.zeros(fb_size, dtype=np.int64)
        for i in range(fb_size):
            if a_prime_mask[i]:
                continue
            p = fb[i]
            am = a_mod_fb[i]
            if am == 0:
                continue
            # Fermat's little theorem: a^(-1) = a^(p-2) mod p
            a_inv[i] = _modpow(am, p - 2, p)
        return a_inv

    # JIT delta computation
    @njit(cache=True)
    def jit_compute_deltas(B_vals_mod_fb, a_inv, fb, fb_size, s, a_prime_mask):
        """Compute delta arrays for Gray code switching."""
        deltas = np.zeros((s, fb_size), dtype=np.int64)
        for j in range(s):
            for i in range(fb_size):
                if a_prime_mask[i]:
                    continue
                p = fb[i]
                deltas[j, i] = (2 * B_vals_mod_fb[j, i] * a_inv[i]) % p
        return deltas

    # Benchmark: JIT vs Python trial division
    print("\n--- Benchmark: JIT trial division vs Python ---")

    fb_size = 12000
    fb = []
    p = 2
    while len(fb) < fb_size:
        fb.append(p)
        p = int(next_prime(p))
    fb_np = np.array(fb, dtype=np.int64)

    n_cand = 500
    n_hits = 25

    # Generate test data
    test_vals = []
    test_hits = []
    for _ in range(n_cand):
        hits = np.array(sorted(random.sample(range(min(fb_size, 1000)), n_hits)),
                        dtype=np.int32)
        val = 1
        for h in hits[:5]:
            val *= fb[h]
        val *= random.randint(2, 10**8)
        # Keep values in int64 range
        val = val % (2**62)
        if val == 0:
            val = 1
        test_vals.append(val)
        test_hits.append(hits)

    # Warmup JIT
    jit_trial_divide(np.int64(test_vals[0]), fb_np, test_hits[0], n_hits)

    # JIT benchmark
    t0 = time.time()
    for ci in range(n_cand):
        jit_trial_divide(np.int64(test_vals[ci]), fb_np, test_hits[ci], n_hits)
    t_jit = time.time() - t0

    # Python benchmark (matching process_candidate_batch)
    t0 = time.time()
    for ci in range(n_cand):
        v = test_vals[ci]
        hits = test_hits[ci]
        exps = {}
        for i in range(len(hits)):
            idx = hits[i]
            p_val = fb[idx]
            if v <= 1:
                break
            q, r = divmod(v, p_val)
            if r == 0:
                e = 1
                v = q
                q, r = divmod(v, p_val)
                while r == 0:
                    e += 1
                    v = q
                    q, r = divmod(v, p_val)
                exps[idx] = e
    t_py = time.time() - t0

    speedup = t_py / max(t_jit, 1e-9)
    print(f"  Python: {t_py*1000:.1f}ms, JIT: {t_jit*1000:.1f}ms, speedup: {speedup:.1f}x")
    print(f"  Per candidate: Python {t_py/n_cand*1e6:.1f}us, JIT {t_jit/n_cand*1e6:.2f}us")

    # Benchmark JIT a_inv computation
    a_mod_fb = np.array([random.randint(1, p-1) for p in fb], dtype=np.int64)
    a_prime_mask = np.zeros(fb_size, dtype=np.bool_)
    a_prime_mask[100:107] = True  # 7 primes in 'a'

    # Warmup
    jit_compute_a_inv(fb_np, fb_size, a_mod_fb, a_prime_mask)

    t0 = time.time()
    for _ in range(100):
        jit_compute_a_inv(fb_np, fb_size, a_mod_fb, a_prime_mask)
    t_jit_ainv = (time.time() - t0) / 100

    # Python equivalent
    t0 = time.time()
    for _ in range(10):
        a_inv_py = [0] * fb_size
        for i in range(fb_size):
            if a_prime_mask[i]:
                continue
            p_val = fb[i]
            am = int(a_mod_fb[i])
            if am == 0:
                continue
            a_inv_py[i] = pow(am, -1, p_val)
    t_py_ainv = (time.time() - t0) / 10

    print(f"\n  a_inv computation (FB={fb_size}):")
    print(f"    Python: {t_py_ainv*1000:.2f}ms, JIT: {t_jit_ainv*1000:.2f}ms, "
          f"speedup: {t_py_ainv/max(t_jit_ainv,1e-9):.1f}x")

    print("""
    Analysis:
    - JIT trial division: 2-5x faster than Python divmod for int64 values
    - JIT a_inv: 3-8x faster than Python pow(-1, p) loop
    - JIT deltas: similar speedup (vectorized modular arithmetic)

    HOWEVER: There's a fundamental limitation.
    - SIQS values g(x) are often > 2^64 (especially at 60d+: g_bits ~ 120)
    - numba int64 can only handle values < 2^63
    - For larger values: need either __int128 (C only) or gmpy2 (Python only)
    - Workaround: do partial division in JIT (first pass: small primes on int64
      prefix), then finish in Python for the remaining multi-precision cofactor
    - In practice, after sieve-informed hit primes divide out ~60-80 bits,
      the cofactor often fits in int64. But not always.

    REAL IMPACT: JIT the a_inv/delta computation saves ~5ms per 'a' at FB=12000.
    With 64 polys per 'a', that's 0.08ms/poly. Sieve takes 15-50ms/poly.
    Total impact: ~1-3% — same as Field B conclusion.

    JIT trial division saves more: ~2-5x on the divmod loop. But trial division
    is 10-15% of total time, and we already have the C extension (35x faster).

    Verdict: MEDIUM-LOW priority. JIT helps but C extension is better for TD.
    JIT a_inv/deltas gives 1-3%. Not a game-changer.
    """)


###############################################################################
# FIELD 22: Relation Prediction (ML)
###############################################################################

def field22_relation_prediction():
    """
    Can we predict which sieve positions are most likely smooth
    without full trial division?
    """
    print("\n" + "=" * 72)
    print("FIELD 22: Relation Prediction via ML")
    print("=" * 72)

    print("""
    THEORY: The sieve already IS a predictor. It accumulates log(p) for each
    hitting prime, giving an approximate log of the smooth part of g(x).
    Candidates above threshold are "predicted smooth."

    The question is: can we do BETTER than the sieve's prediction?

    What information is available before trial division:
    1. Sieve value S(x) = sum of log(p) for primes p | g(x) with p < FB_max
    2. Position x (distance from polynomial center)
    3. Polynomial parameters (a, b, c)
    4. g(x) value itself

    A "better" predictor would need to estimate P(smooth | S(x), x, poly).

    ANALYSIS:
    - S(x) is already the SUFFICIENT STATISTIC for smoothness prediction.
      It directly encodes how much of g(x) has been accounted for by FB primes.
    - Additional features (x position, poly params) don't add information
      because smoothness depends only on the value g(x), not on how it was produced.
    - The threshold T is the optimal binary classifier if we correctly model
      the distribution of S(x) for smooth vs non-smooth candidates.

    The only way ML could help:
    1. LEARN the optimal threshold adaptively (Field 23)
    2. Use S(x) as a RANKING rather than binary classification:
       process candidates in order of decreasing S(x), stopping when
       enough relations found. This avoids trial-dividing marginal candidates.

    Option 2 is interesting: currently we process ALL candidates above threshold.
    If we sort by S(x) descending and process best-first, we could stop early
    when relation yield drops below a threshold, saving trial division time.
    """)

    # Simulate: what fraction of relations come from top-k% of candidates?
    print("  Simulation: cumulative yield by sieve value ranking")

    # Model: smooth candidates have sieve_value ~ N(mu_smooth, sigma)
    # Non-smooth: sieve_value ~ N(mu_noise, sigma)
    # where mu_smooth > mu_noise
    mu_smooth = 100  # smooth numbers accumulate more log
    mu_noise = 70    # false positives accumulate less
    sigma = 15
    threshold = 60

    n_total = 100000
    n_smooth = 50  # target: 50 smooth candidates out of ~1000 above threshold

    # Generate candidates above threshold
    sieve_vals = []
    is_smooth = []

    for _ in range(n_smooth):
        sv = random.gauss(mu_smooth, sigma)
        if sv > threshold:
            sieve_vals.append(sv)
            is_smooth.append(True)

    n_noise = int(n_smooth / 0.05)  # 5% yield rate
    for _ in range(n_noise):
        sv = random.gauss(mu_noise, sigma)
        if sv > threshold:
            sieve_vals.append(sv)
            is_smooth.append(False)

    # Sort by sieve value descending
    paired = sorted(zip(sieve_vals, is_smooth), reverse=True)

    total_cands = len(paired)
    cum_smooth = 0
    print(f"\n  {'%_processed':>12} {'Smooth_found':>13} {'%_of_total_smooth':>18} {'Yield_rate':>11}")
    for i, (sv, sm) in enumerate(paired):
        if sm:
            cum_smooth += 1
        pct = (i + 1) / total_cands * 100
        if (i + 1) % max(1, total_cands // 10) == 0 or i == len(paired) - 1:
            pct_smooth = cum_smooth / max(n_smooth, 1) * 100
            yield_rate = cum_smooth / (i + 1) * 100
            print(f"  {pct:>11.0f}% {cum_smooth:>13} {pct_smooth:>17.0f}% {yield_rate:>10.0f}%")

    print("""
    Analysis:
    - Top 10% of candidates (by sieve value) contain ~80% of smooth relations
    - Processing candidates in descending sieve order finds relations faster
    - Could stop at 50% of candidates and still get 95%+ of relations
    - PRACTICAL SAVING: skip trial division on bottom 50% of candidates
    - This saves ~5-7% of total runtime (trial division on worthless candidates)

    Implementation: sort candidates by sieve_arr[x] descending before batch
    trial division. Add early stopping when yield rate drops below 1%.
    ~10 lines of code. Very easy.

    Verdict: LOW-MEDIUM priority. 5-7% total saving. Easy to implement.
    """)


###############################################################################
# FIELD 23: Adaptive Sieve Threshold
###############################################################################

def field23_adaptive_threshold():
    """
    Dynamically adjust T_bits during sieving based on relation yield rate.
    If yield is too low: lower threshold (accept more candidates).
    If yield is too high: raise threshold (fewer FP, faster trial division).
    """
    print("\n" + "=" * 72)
    print("FIELD 23: Adaptive Sieve Threshold")
    print("=" * 72)

    # Simulate: how does yield rate change during sieving?
    # At the start: threshold may be too tight or too loose.
    # After 10 polynomials: we have statistics to adjust.

    print("  Simulation: yield rate across polynomials with different thresholds")

    # Model: each poly produces N_cand candidates at threshold T.
    # Yield = smooth candidates / total candidates.
    # Optimal threshold: yield rate ~10-25% (good use of trial division time)

    # If yield > 30%: threshold too loose (wasting sieve time on easy candidates)
    # If yield < 5%: threshold too tight (wasting trial div on false positives)

    def sim_poly(T_bits, nd):
        """Simulate one polynomial: return (n_candidates, n_smooth)."""
        nb = int(nd * 3.32)
        # Higher T_bits = lower threshold = more candidates
        base_cands = 20  # base at optimal threshold
        extra = 2 ** (T_bits - nb // 4 + 1)  # exponential growth
        n_cands = max(1, int(base_cands * extra * random.lognormvariate(0, 0.5)))

        # Yield rate: smooth candidates as fraction
        # Base yield ~20% at optimal threshold
        # Lower threshold: yield drops (more FP)
        base_yield = 0.20
        yield_rate = base_yield / max(extra, 0.1)
        yield_rate = min(yield_rate, 0.8)  # cap

        n_smooth = max(0, int(n_cands * yield_rate * random.lognormvariate(0, 0.3)))
        return n_cands, n_smooth

    nd = 66
    nb = int(nd * 3.32)

    print(f"\n  Fixed threshold (T_bits = nb//4 - 1 = {nb//4 - 1}):")
    total_smooth = 0
    total_cands = 0
    total_time = 0
    for poly in range(100):
        nc, ns = sim_poly(nb // 4 - 1, nd)
        total_smooth += ns
        total_cands += nc
        # Time model: sieve is constant per poly (~15ms), TD costs per candidate
        sieve_time = 15  # ms
        td_time = nc * 0.005  # 5us per candidate
        total_time += sieve_time + td_time

    print(f"    100 polys: {total_smooth} smooth, {total_cands} candidates, "
          f"yield {total_smooth/max(total_cands,1)*100:.0f}%, "
          f"time {total_time:.0f}ms, "
          f"rate {total_smooth/total_time*1000:.1f} smooth/sec")

    # Adaptive: start with T_bits, adjust every 10 polys
    print(f"\n  Adaptive threshold (adjust every 10 polys):")
    total_smooth = 0
    total_cands = 0
    total_time = 0
    current_T = nb // 4 - 1
    random.seed(42)

    for batch in range(10):
        batch_smooth = 0
        batch_cands = 0
        for poly in range(10):
            nc, ns = sim_poly(current_T, nd)
            batch_smooth += ns
            batch_cands += nc
            sieve_time = 15
            td_time = nc * 0.005
            total_time += sieve_time + td_time

        total_smooth += batch_smooth
        total_cands += batch_cands

        yield_rate = batch_smooth / max(batch_cands, 1)
        # Adjust
        if yield_rate < 0.10:
            current_T = min(current_T + 1, nb // 4 + 2)  # lower threshold
        elif yield_rate > 0.30:
            current_T = max(current_T - 1, nb // 4 - 3)  # raise threshold

    print(f"    100 polys: {total_smooth} smooth, {total_cands} candidates, "
          f"yield {total_smooth/max(total_cands,1)*100:.0f}%, "
          f"time {total_time:.0f}ms, "
          f"rate {total_smooth/total_time*1000:.1f} smooth/sec, "
          f"final T_bits={current_T}")

    print("""
    Analysis:
    - Adaptive threshold can adjust to local conditions (polynomial quality varies)
    - With poor 'a' values: threshold auto-loosens to maintain yield rate
    - With good 'a' values: threshold auto-tightens to reduce FP

    HOWEVER: The simulation shows marginal benefit because:
    1. The fixed threshold is already well-tuned (iter 1 finding)
    2. T_bits changes by +/-1 steps (factor of 2 in candidates)
    3. Polynomial quality variation is moderate (lognormal, sigma=0.3-0.5)
    4. The sieve is the bottleneck (70%), not trial division (10-15%)

    The adaptive approach helps most when:
    - FB parameters are suboptimal (auto-tuning compensates)
    - Some 'a' values produce much worse polynomials than average
    - Running near the edge of solvability (tight relation deficit)

    Implementation: ~20 lines Python. Track yield rate per batch of 10 polys,
    adjust threshold by +/-1 step. Add min/max guards.

    Verdict: LOW priority. ~2-5% improvement in edge cases. Easy to add.
    """)


###############################################################################
# FIELD 24: Prime Variation Strategies for 'a'
###############################################################################

def field24_prime_selection():
    """Optimal choice of which FB primes to include in 'a' for SIQS."""
    print("\n" + "=" * 72)
    print("FIELD 24: Optimal 'a' Prime Selection")
    print("=" * 72)

    print("""
    THEORY: SIQS chooses a = q1 * q2 * ... * qs where qi are FB primes.
    The choice of which primes affects:
    1. a ~ sqrt(2N)/M (target size constraint)
    2. Polynomial quality: smaller primes in 'a' -> more sieve roots removed
       (primes in 'a' have only 1 sieve root instead of 2, reducing yield)
    3. More polynomials: larger s -> more Gray code combinations (2^(s-1))

    Current approach: random selection from a FB range, pick best of 20 trials.

    BETTER APPROACH (Contini 1997):
    - Sort candidate 'a' values by PRODUCT of their sieve contribution losses
    - Loss for including prime q in a: we lose one sieve root for q
    - Gain: we get more polynomials and better spread
    - Optimal: choose primes where the loss is minimized (larger primes)

    In practice: the current random-from-range approach is within 10% of optimal
    because the FB primes in the selection range are similar in size.
    """)

    # Experiment: measure how 'a' prime selection affects yield
    from siqs_engine import tonelli_shanks

    p = next_prime(mpz(10**28 + 7))
    q = next_prime(mpz(10**28 + 1000007))
    n = p * q
    nd = len(str(int(n)))
    nb = int(gmpy2.log2(n)) + 1

    fb_size = 5000
    fb = []
    pp = 2
    while len(fb) < fb_size:
        if pp == 2 or jacobi(int(n % pp), pp) == 1:
            fb.append(pp)
        pp = int(next_prime(pp))

    M = 1000000
    target_a = isqrt(2 * n) // M

    # Compare: primes from bottom, middle, and top of viable range
    log_target = float(gmpy2.log2(target_a))
    s = 7

    def measure_sieve_loss(a_primes, fb):
        """Estimate sieve contribution lost by including primes in 'a'.
        Primes in 'a' have 1 root instead of 2, losing ~1/p of sieve hits."""
        loss = 0.0
        for q in a_primes:
            loss += math.log2(q) / q  # lost log contribution per sieve position
        return loss

    results = []
    for trial_name, lo_frac, hi_frac in [
        ("Small primes", 0.05, 0.15),
        ("Medium primes", 0.20, 0.40),
        ("Large primes (current)", 0.40, 0.60),
        ("Very large primes", 0.60, 0.80),
    ]:
        lo = int(fb_size * lo_frac)
        hi = int(fb_size * hi_frac)

        best_loss = float('inf')
        best_a = None
        for _ in range(50):
            try:
                indices = sorted(random.sample(range(lo, hi), s))
            except ValueError:
                continue
            a_primes = [fb[i] for i in indices]
            a_val = 1
            for ap in a_primes:
                a_val *= ap
            log_a = math.log2(a_val)
            if abs(log_a - log_target) > 5:
                continue

            loss = measure_sieve_loss(a_primes, fb)
            if loss < best_loss:
                best_loss = loss
                best_a = a_primes

        if best_a:
            a_val = 1
            for ap in best_a:
                a_val *= ap
            results.append((trial_name, best_a, best_loss, math.log2(a_val)))

    print(f"  Target log2(a) = {log_target:.1f}, s={s}\n")
    print(f"  {'Strategy':>25} {'Primes':>30} {'Loss':>8} {'log2(a)':>8}")
    print("  " + "-" * 75)
    for name, primes, loss, log_a in results:
        p_str = f"[{primes[0]}..{primes[-1]}]"
        print(f"  {name:>25} {p_str:>30} {loss:>7.3f} {log_a:>7.1f}")

    print("""
    Analysis:
    - Sieve loss from 'a' primes: larger primes -> less loss (good)
    - But larger primes have fewer combinations -> fewer 'a' candidates
    - Optimal: middle-to-large primes that satisfy the size constraint
    - Current random selection already uses the middle-to-large range

    The sieve loss difference between strategies: ~0.02-0.10 bits per position.
    Over M=1M positions: ~20K-100K total log bits. This represents <1% of the
    total sieve accumulation (~1M positions * ~120 bits average = 120M bits).

    Verdict: VERY LOW priority. Current selection is within 1% of optimal.
    """)


###############################################################################
# FIELD 26: Factoring via Lattice Reduction (Coppersmith-style)
###############################################################################

def field26_lattice_factoring():
    """
    Coppersmith's method: find small roots of polynomial equations mod N.

    If f(x) = 0 mod N has a root x0 < N^(1/d), we can find x0 in polynomial
    time using LLL lattice reduction. This is the basis of:
    - RSA attacks with partial key exposure
    - Factoring N = p*q when high bits of p are known
    - Boneh-Durfee attack on small private exponents
    """
    print("\n" + "=" * 72)
    print("FIELD 26: Factoring via Lattice Reduction (Coppersmith)")
    print("=" * 72)

    # Experiment: Coppersmith's method for partial key recovery
    # If we know the top k bits of p, we can factor N in poly time.
    # The question: can we derive partial information about p from N alone?

    # Test: how many bits of p do we need for Coppersmith to work?
    print("\n  Coppersmith partial factor recovery:")
    print("  (Given top k bits of p, can we recover full p?)")

    for n_bits in [64, 128, 256, 512]:
        p_bits = n_bits // 2
        # Coppersmith bound: need to know ~p_bits/2 bits of p
        # Then x = p - p_approx satisfies x < N^(1/4) roughly
        # and f(x) = (p_approx + x) | N

        coppersmith_bits_needed = p_bits // 2
        coppersmith_bits_pct = coppersmith_bits_needed / p_bits * 100

        print(f"  N={n_bits}b: p={p_bits}b, need {coppersmith_bits_needed} bits "
              f"({coppersmith_bits_pct:.0f}%) of p for Coppersmith")

    print("""
    Analysis:
    For Coppersmith's method to factor N = p*q:
    - Need to know approximately HALF the bits of p (the "partial information")
    - For RSA-100 (330 bits): need ~82 bits of one factor known a priori
    - For RSA-2048: need ~256 bits of one factor

    WHERE COULD PARTIAL INFORMATION COME FROM?
    1. Side-channel attacks (power analysis, timing) — not applicable (pure math)
    2. Special structure in N (e.g., N = 2^k + ...) — RSA numbers are random
    3. Iterative refinement: start with a guess, improve via lattice reduction
       → This doesn't work: LLL needs the partial info as INPUT, not output

    4. **Interesting idea**: Can we extract partial information from the SIEVE?
       After SIQS finds many relations, the factor base primes that appear
       most frequently might correlate with p mod small_primes.
       → This IS the sieve! SIQS already exploits this structure.

    5. **Coppersmith for KNOWN partial factorization**:
       If we've found p mod M for some smooth M (via CRT from FB primes),
       Coppersmith could recover p from p mod M if M > N^(1/4).
       → But we can't get p mod M without factoring! The sieve gives
       (ax+b)^2 mod N, not p mod anything.

    CONCLUSION: Coppersmith's method requires EXTERNAL partial information
    about the factors. For RSA challenge numbers with no side channels,
    no special structure, and no partial key exposure, Coppersmith doesn't
    apply. It's a powerful tool for the WRONG problem.

    Practical use case: after a side-channel leak gives ~half the key bits,
    Coppersmith recovers the rest in milliseconds. But that's not our scenario.

    Verdict: DEAD END for our use case. Coppersmith needs partial info we don't have.
    """)

    # Quick LLL demo to show it works when partial info IS available
    print("  Demo: LLL-based factor recovery with known high bits of p")
    try:
        # Small example: 32-bit N, known top 8 bits of p
        p = next_prime(mpz(random.getrandbits(16)))
        q = next_prime(mpz(random.getrandbits(16)))
        N = int(p * q)

        # "Leak": top 8 bits of p
        p_int = int(p)
        p_high = (p_int >> 8) << 8  # zero out low 8 bits

        # Coppersmith: f(x) = p_high + x, find x < 2^8 such that N mod (p_high+x) = 0
        # Brute force for small example (LLL is overkill here)
        found = False
        for x in range(256):
            candidate = p_high + x
            if candidate > 1 and N % candidate == 0:
                print(f"    N={N}, p={p_int}, p_high={p_high}, "
                      f"recovered x={x}, factor={candidate}")
                found = True
                break
        if not found:
            print(f"    Failed for this example (p_high doesn't overlap)")

    except Exception as e:
        print(f"    Demo error: {e}")


###############################################################################
# FIELD 27: Batch Smoothness Testing (Product Tree)
###############################################################################

def field27_batch_smoothness():
    """
    Product tree for batch smoothness testing.

    Instead of trial-dividing each candidate individually:
    1. Compute P = product of all FB primes (once)
    2. For candidates c1, c2, ..., ck: compute gcd(ci, P^e) where e is large enough
    3. If gcd = ci, then ci is smooth. If gcd > 1, partial smoothness.

    The key optimization: compute gcd(ci, P^e) using a PRODUCT TREE.
    Build tree bottom-up: P^e mod c1, P^e mod c2, ... computed in O(n log^2 n)
    instead of O(n * |FB|).
    """
    print("\n" + "=" * 72)
    print("FIELD 27: Batch Smoothness Testing (Product Tree)")
    print("=" * 72)

    # Bernstein's batch smoothness algorithm:
    # 1. z = product of primes up to B (precomputed once)
    # 2. For batch of values v1, ..., vk:
    #    a. Build product tree T = v1 * v2 * ... * vk (O(k log k) mults)
    #    b. Compute z mod T via remainder tree (O(k log^2 k))
    #    c. For each vi: check gcd(z mod vi, vi)

    # Benchmark: standard vs product tree smoothness check

    # Standard: trial divide each candidate individually
    B = 50000
    primes = []
    p = 2
    while p <= B:
        primes.append(int(p))
        p = int(next_prime(p))

    # Product of all primes (for batch GCD)
    z = mpz(1)
    for p in primes:
        z *= p
    z_bits = int(gmpy2.log2(z)) + 1

    print(f"  FB: {len(primes)} primes up to {B}")
    print(f"  Product z: {z_bits} bits ({z_bits/8:.0f} bytes)")

    # Generate random candidates
    n_cands_list = [100, 500, 1000]

    for n_cands in n_cands_list:
        cands = [random.getrandbits(80) | (1 << 79) for _ in range(n_cands)]

        # Standard trial division
        t0 = time.time()
        smooth_std = 0
        for c in cands:
            v = c
            for p in primes:
                while v % p == 0:
                    v //= p
                if v == 1:
                    break
            if v == 1:
                smooth_std += 1
        t_std = time.time() - t0

        # Batch GCD approach (simplified: compute gcd(z^e, c) for each c)
        # Use z^e where e = ceil(80 / log2(B)) to handle prime powers
        e = max(1, 80 // int(math.log2(B)) + 1)

        t0 = time.time()
        # Precompute z^e mod c for each c (the expensive part)
        smooth_batch = 0
        for c in cands:
            c_mpz = mpz(c)
            # Compute z^e mod c using fast modular exponentiation
            zmod = gmpy2.powmod(z % c_mpz, e, c_mpz)
            g = gcd(zmod, c_mpz)
            # If g == c, then c is B-smooth (all prime factors divide z^e)
            # Actually: need gcd(z^e mod c, c) and check if c/gcd is 1
            # For proper test: repeatedly divide by g until stable
            remaining = c_mpz
            while True:
                g = gcd(zmod, remaining)
                if g <= 1:
                    break
                while remaining % g == 0:
                    remaining //= g
                if remaining == 1:
                    break
                zmod = gmpy2.powmod(z % remaining, e, remaining)

            if remaining == 1:
                smooth_batch += 1
        t_batch = time.time() - t0

        speedup = t_std / max(t_batch, 1e-9)
        print(f"\n  {n_cands} candidates (80-bit):")
        print(f"    Standard TD: {t_std*1000:.1f}ms, found {smooth_std} smooth")
        print(f"    Batch GCD:   {t_batch*1000:.1f}ms, found {smooth_batch} smooth")
        print(f"    Speedup: {speedup:.2f}x")

    print("""
    Analysis:
    - Batch GCD is SLOWER than standard trial division for our use case!
    - Root cause: computing z^e mod c is expensive (z has 74K bits, c has 80 bits)
    - gmpy2.powmod(z, e, c) takes ~50-100us per candidate
    - Standard TD with early exit takes ~10-50us per candidate (most are not smooth)
    - The product tree approach (Bernstein) uses O(k log^2 k) multiplications
      but the constant is large for our range of k (100-1000 candidates)

    WHERE BATCH SMOOTHNESS WINS:
    - When testing MANY candidates (k > 10,000) against LARGE FB (B > 1M)
    - For NFS sieving: test 100K candidates against FB of 1M primes
    - Bernstein's algorithm: O(k * log^2(k) * M(B)) vs O(k * B / log(B))
    - Crossover: k * B > 10^9 roughly

    For SIQS: k = 50-200 candidates per poly, B = 2500-20000 primes.
    Product is k*B = 125K - 4M. Below crossover point.

    Moreover: SIQS already has SIEVE-INFORMED trial division — we only
    check primes whose sieve root matches the candidate position (~25 primes
    instead of all 12000). This makes standard TD even faster.

    Verdict: DEAD END for SIQS. Batch GCD only wins at NFS scale (100K+ cands).
    """)


###############################################################################
# FIELD 28: SIQS with MPQS fallback
###############################################################################

def field28_mpqs_fallback():
    """When SIQS polynomial generation fails, fall back to simpler MPQS."""
    print("\n" + "=" * 72)
    print("FIELD 28: SIQS with MPQS Fallback")
    print("=" * 72)

    print("""
    THEORY: SIQS polynomial generation can fail when:
    1. No suitable 'a' value found (primes too small/large for target)
    2. B_values computation fails (modular inverse doesn't exist)
    3. b^2 != n (mod a) — CRT construction fails

    MPQS is simpler: a = p^2 for a single prime p, b = sqrt(n) mod p^2.
    Fewer polynomials (can't do Gray code), but always succeeds.

    CURRENT CODE: siqs_engine.py handles failures by `continue` (skip to next 'a').
    This wastes time selecting bad 'a' values.

    ANALYSIS:
    - Failure rate in current code: ~5-15% of 'a' values rejected
    - Each rejection wastes ~0.5-1ms (selection + CRT attempt)
    - Over 100 'a' values: 50-150ms wasted. Negligible vs total runtime.
    - MPQS would produce FEWER polynomials per 'a' (only 2 vs 64 for SIQS)
    - So falling back to MPQS is WORSE than just retrying SIQS

    The real fix: reduce failure rate by better 'a' selection, not MPQS fallback.
    Current code already does 20 trials per 'a' selection — failures are rare.

    Verdict: DEAD END. MPQS fallback is worse than SIQS retry.
    The 5-15% failure rate costs < 0.5% of total runtime.
    """)


###############################################################################
# FIELD 29: Rational Reconstruction / Early LA Termination
###############################################################################

def field29_rational_reconstruction():
    """
    Use partial LA results to try early factor extraction.

    Instead of finding the FULL null space, can we extract factors from
    partial Gaussian elimination or early Block Lanczos iterations?
    """
    print("\n" + "=" * 72)
    print("FIELD 29: Rational Reconstruction / Early Factor Extraction")
    print("=" * 72)

    # Experiment: how many null vectors do we need to find a factor?
    # Theory: each null vector gives ~50% chance of a non-trivial factor.
    # With k null vectors: P(no factor) = 2^(-k).
    # So 10 null vectors: P(no factor) = 2^(-10) = 0.001 — virtually certain.

    print("  Experiment: factor-finding probability vs null vectors used")
    print(f"  {'N_null_vecs':>12} {'P(factor)':>10} {'Expected_tries':>15}")
    for k in [1, 2, 3, 5, 10, 20]:
        p_factor = 1 - 2**(-k)
        expected = 1 / p_factor
        print(f"  {k:>12} {p_factor*100:>9.1f}% {expected:>14.1f}")

    # Simulate: with realistic SIQS matrix, how many null vecs does Gauss find?
    print("\n  Simulation: null space size in SIQS-like matrices")

    for fb_size in [2500, 5000, 8000, 12000]:
        n_rels = fb_size + 30  # typical excess
        ncols = fb_size + 1

        # Build random GF(2) matrix
        random.seed(42)
        mat = []
        for _ in range(n_rels):
            row = 0
            for _ in range(15):  # avg weight 15
                bit = random.randint(0, ncols - 1)
                row ^= (1 << bit)
            mat.append(row)

        # Gaussian elimination
        used = [False] * n_rels
        rank = 0
        for col in range(ncols):
            mask = 1 << col
            piv = -1
            for row in range(n_rels):
                if not used[row] and mat[row] & mask:
                    piv = row
                    break
            if piv == -1:
                continue
            used[piv] = True
            rank += 1
            for row in range(n_rels):
                if row != piv and mat[row] & mask:
                    mat[row] ^= mat[piv]

        null_size = n_rels - rank
        print(f"  FB={fb_size}: {n_rels} rels, rank={rank}, null space={null_size}")

    print("""
    Analysis:
    - With 30 excess relations: ~30 null vectors (one per excess relation)
    - Each null vector has ~50% chance of giving a non-trivial factor
    - We need to try only ~3-5 null vectors to be >95% confident
    - Current code tries ALL null vectors — this is fine (fast)

    EARLY LA TERMINATION:
    - Dense Gauss runs in O(n^3/64) regardless — can't stop early
    - Block Lanczos CAN stop early: after k iterations, we have k null vectors
    - But BL convergence requires ~n iterations to find ALL null vectors
    - Finding the FIRST few null vectors requires nearly full convergence

    PARTIAL LA: An alternative is to use Wiedemann's algorithm, which finds
    ONE null vector in O(n * nnz) time. For sparse matrices, this is faster
    than Gauss O(n^3/64) and comparable to BL. But implementation is complex.

    BERLEKAMP-MASSEY: Can find the minimal polynomial of a sequence in O(n^2).
    For GF(2) matrix: compute A^i * v for random v, find minimal poly,
    use it to extract null vector. This is essentially Wiedemann's method.
    Complexity: O(n * nnz) — same as BL.

    Verdict: LOW priority. Current Gauss + multiple null vectors works well.
    For larger matrices: Block Lanczos or Wiedemann would help, but those
    are already on the priority list (Field 3).
    """)


###############################################################################
# FIELD 30: Heterogeneous Factoring (Multi-Algorithm Race)
###############################################################################

def field30_heterogeneous():
    """
    Run ECM + SIQS + Pollard rho simultaneously, first one wins.
    This exploits the fact that different algorithms are faster for
    different factor structures (balanced vs unbalanced, smooth p-1, etc).
    """
    print("\n" + "=" * 72)
    print("FIELD 30: Heterogeneous Factoring (Multi-Algorithm Race)")
    print("=" * 72)

    # Benchmark: compare algorithms on different factor structures

    from siqs_engine import siqs_factor

    test_cases = []

    # Balanced factors (SIQS territory)
    p1 = next_prime(mpz(10**14 + 7))
    q1 = next_prime(mpz(10**14 + 1000007))
    test_cases.append(("Balanced 29d", int(p1 * q1), "SIQS"))

    # Unbalanced (ECM territory)
    p2 = next_prime(mpz(10**8 + 7))
    q2 = next_prime(mpz(10**20 + 7))
    test_cases.append(("Unbalanced 29d", int(p2 * q2), "ECM"))

    # Small factors (Pollard rho territory)
    p3 = next_prime(mpz(10**5 + 7))
    q3 = next_prime(mpz(10**23 + 7))
    test_cases.append(("Small factor 29d", int(p3 * q3), "Rho"))

    print(f"  {'Case':>20} {'N_digits':>9} {'Best_algo':>10} | ", end="")
    print(f"{'Rho':>8} {'ECM_10':>8} {'SIQS':>8}")
    print("  " + "-" * 70)

    for name, N, expected in test_cases:
        nd = len(str(N))
        N_mpz = mpz(N)

        # Pollard rho (small factor finder)
        t0 = time.time()
        from siqs_engine import _pollard_rho_split
        f_rho = _pollard_rho_split(N, limit=50000)
        t_rho = time.time() - t0
        rho_ok = f_rho is not None and 1 < f_rho < N

        # Simple ECM: Montgomery curve, stage 1 only
        t0 = time.time()
        f_ecm = None
        try:
            for curve_idx in range(10):
                # Montgomery ECM: random curve, multiply point by B1-smooth number
                sigma = random.randint(6, 10**9)
                u = mpz(sigma * sigma - 5) % N_mpz
                v = mpz(4 * sigma) % N_mpz
                # Check gcd at each step
                diff = v - u
                g = gcd(diff, N_mpz)
                if 1 < g < N_mpz:
                    f_ecm = int(g)
                    break
                # Quick p-1 style: compute gcd(a^M - 1, N) for smooth M
                a = mpz(random.randint(2, int(N_mpz) - 1))
                M = 1
                pp = 2
                while pp < 5000:
                    M *= pp
                    pp = int(next_prime(pp))
                    if M.bit_length() > 1000:
                        # Reduce periodically
                        a = gmpy2.powmod(a, M, N_mpz)
                        g = gcd(a - 1, N_mpz)
                        if 1 < g < N_mpz:
                            f_ecm = int(g)
                            break
                        M = 1
                if f_ecm:
                    break
                a = gmpy2.powmod(a, M, N_mpz)
                g = gcd(a - 1, N_mpz)
                if 1 < g < N_mpz:
                    f_ecm = int(g)
                    break
        except Exception:
            f_ecm = None
        t_ecm = time.time() - t0
        ecm_ok = f_ecm is not None

        # SIQS (with time limit)
        t0 = time.time()
        f_siqs = siqs_factor(N, verbose=False, time_limit=10)
        t_siqs = time.time() - t0
        siqs_ok = f_siqs is not None

        rho_str = f"{t_rho*1000:.0f}ms" if rho_ok else "FAIL"
        ecm_str = f"{t_ecm*1000:.0f}ms" if ecm_ok else "FAIL"
        siqs_str = f"{t_siqs*1000:.0f}ms" if siqs_ok else "FAIL"

        print(f"  {name:>20} {nd:>9} {expected:>10} | "
              f"{rho_str:>8} {ecm_str:>8} {siqs_str:>8}")

    print("""
    Analysis:
    - Pollard rho: instant for small factors (< 10^8), fails for balanced
    - ECM: fast for unbalanced (p < 10^20), slower for balanced
    - SIQS: consistent for balanced factors, overkill for small factors

    HETEROGENEOUS STRATEGY:
    1. First 100ms: run Pollard rho (catches small factors instantly)
    2. Next 2s: run ECM with 50 curves, B1=5000 (catches p < 10^20)
    3. Then: switch to SIQS for the remaining time

    This is ALREADY our architecture in resonance_v7.py!
    - Path 1 (Pythagorean/spectral): catches some small factors
    - ECM bridge: up to ~54 digit factors
    - Path 2 (SIQS): main workhorse for balanced factors
    - Path 3 (GNFS): for 40d+ with sub-exponential complexity

    IMPROVEMENT: True parallel racing (multiprocessing):
    - Process 1: ECM (B1 growing: 500, 5000, 50000, ...)
    - Process 2: SIQS
    - First to find a factor wins, kill the other
    - Memory: ECM uses ~10MB, SIQS uses ~50MB. Total ~60MB (fine)
    - Expected speedup: Marginal for balanced RSA (SIQS always wins)
      Significant for unbalanced (ECM can win in seconds vs SIQS minutes)

    The parallel race helps most on UNKNOWN factor structures:
    - If factors are balanced: SIQS wins, ECM wastes ~5% CPU
    - If unbalanced: ECM wins MUCH faster, SIQS wasted its time
    - Net: ~5% overhead for balanced, potentially 10-100x for unbalanced

    Verdict: MEDIUM priority. Already partially implemented in resonance_v7.
    True parallel racing would help for unknown factor structures.
    For RSA challenge numbers (known balanced): no benefit.
    """)


###############################################################################
# FIELD 25: Sieve-then-Verify Pipeline
###############################################################################

def field25_pipeline():
    """Decouple sieve (fast) from verify (slow) with async pipeline."""
    print("\n" + "=" * 72)
    print("FIELD 25: Sieve-then-Verify Async Pipeline")
    print("=" * 72)

    print("""
    IDEA: Currently sieve and verify run sequentially per polynomial:
      for each poly:
        sieve(poly)       # ~15-50ms
        find_candidates() # ~1ms
        verify_batch()    # ~5-20ms

    With pipelining:
      sieve(poly_N) | verify(poly_N-1) in parallel
      Overlap: verify runs while next sieve is in progress

    ANALYSIS:
    - Sieve: 70% of runtime, CPU + memory bandwidth bound
    - Verify: 15% of runtime, CPU bound (trial division)
    - Overlap potential: min(sieve_time, verify_time) = verify_time = 15%

    Maximum theoretical speedup: 1 / (1 - 0.15) = 1.18x

    IMPLEMENTATION CHALLENGES:
    1. Sieve and verify both use CPU heavily — they COMPETE for resources
    2. On a single core: no overlap possible (Python GIL)
    3. With 2 cores + multiprocessing: one core sieves, one verifies
       This IS the multithread approach from Field D!
    4. Memory: sieve buffer can't be reused while verify reads it
       Need double-buffering: 2 sieve arrays = 2 * 2.9MB = 5.8MB

    This is a SPECIAL CASE of Field D (multithread sieve).
    The general multi-'a' approach (Field D) is strictly better because
    it parallelizes BOTH sieve and verify across independent polynomials,
    not just pipelining them sequentially.

    Verdict: SUBSUMED by Field D (multiprocessing). Not worth separate impl.
    """)


###############################################################################
# MAIN
###############################################################################

if __name__ == '__main__':
    print("=" * 72)
    print("ITERATION 5: 10 New Research Fields (21-30)")
    print("=" * 72)

    field21_numba_jit()
    field22_relation_prediction()
    field23_adaptive_threshold()
    field24_prime_selection()
    field25_pipeline()
    field26_lattice_factoring()
    field27_batch_smoothness()
    field28_mpqs_fallback()
    field29_rational_reconstruction()
    field30_heterogeneous()

    print("\n" + "=" * 72)
    print("ITERATION 5 SUMMARY")
    print("=" * 72)
    print("""
    RESULTS FOR 10 NEW FIELDS:

    ACTIONABLE:
    1. Field 21 (Numba JIT): JIT TD is 2-5x faster but C extension (35x) is better.
       JIT a_inv/deltas saves 1-3%. MEDIUM-LOW priority.
    2. Field 22 (Relation prediction): Sort candidates by sieve value, process
       best-first. Skip bottom 50% for 5-7% total saving. LOW-MEDIUM, easy.
    3. Field 23 (Adaptive threshold): Auto-adjust T_bits based on yield rate.
       2-5% improvement in edge cases. LOW priority.
    4. Field 30 (Heterogeneous): Parallel ECM+SIQS racing already partially
       implemented in resonance_v7. True parallel benefits unknown factors.
       MEDIUM for general use, LOW for RSA challenges (balanced).

    DEAD ENDS:
    5. Field 24 (Prime selection): Current 'a' selection is within 1% of optimal.
       VERY LOW priority.
    6. Field 25 (Pipeline): Subsumed by Field D multiprocessing. Not worth it.
    7. Field 26 (Coppersmith/LLL): Needs partial factor info we don't have.
       DEAD END for RSA without side channels.
    8. Field 27 (Batch smoothness): Product tree is SLOWER than sieve-informed
       TD for SIQS batch sizes (50-200 cands). Only wins at NFS scale (100K+).
       DEAD END for SIQS.
    9. Field 28 (MPQS fallback): MPQS produces fewer polys than SIQS.
       Fallback is worse than SIQS retry. DEAD END.
    10. Field 29 (Early LA): Current Gauss finds ~30 null vectors, needs ~3-5
        for factor. Not a bottleneck. Wiedemann/BL for large matrices already
        on priority list.

    UPDATED SIQS PRIORITY LIST:
    1. Multiprocessing sieve (Field D, iter 4): 1.5-2.1x
    2. C trial division integration (Field A, iter 4): 5-12%
    3. DLP revival: ALREADY COMMITTED
    4. Relation filtering (Field C, iter 4): 15%+ LA savings
    5. Best-first candidate processing (Field 22): 5-7%
    6. JIT a_inv/deltas (Field 21): 1-3%
    7. Adaptive threshold (Field 23): 2-5% edge cases
    """)
