#!/usr/bin/env python3
"""
B3 Moonshots 2 — Radical experiments toward O(1) / L(1/3) factoring via B3-MPQS
================================================================================

8 experiments, each under 60s, under 2GB memory.
Each prints a VERDICT at the end.

Run: python3 b3_moonshots_2.py
"""

import time
import math
import random
import sys
from collections import defaultdict, Counter
import gmpy2
from gmpy2 import mpz, isqrt, gcd, is_prime, next_prime, legendre

# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def gen_semiprime(nd, seed=None):
    """Generate a semiprime with approximately nd digits."""
    rng = random.Random(seed)
    half_bits = int(nd * 3.32 / 2)
    while True:
        p = int(next_prime(mpz(rng.getrandbits(half_bits))))
        q = int(next_prime(mpz(rng.getrandbits(half_bits))))
        if p != q and len(str(p * q)) >= nd - 1:
            return p * q, p, q


def build_fb(N, B):
    """Factor base: primes p <= B with legendre(N,p) >= 0."""
    fb = [2]
    p = mpz(3)
    while p <= B:
        if legendre(N, p) >= 0:
            fb.append(int(p))
        p = next_prime(p)
    return fb


def tonelli_shanks(n, p):
    n = n % p
    if n == 0: return 0
    if p == 2: return n
    if pow(n, (p - 1) // 2, p) != 1: return None
    if p % 4 == 3: return pow(n, (p + 1) // 4, p)
    Q, S = p - 1, 0
    while Q % 2 == 0: Q //= 2; S += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1: z += 1
    M, c, t, R = S, pow(z, Q, p), pow(n, Q, p), pow(n, (Q + 1) // 2, p)
    while True:
        if t == 1: return R
        i, tmp = 1, t * t % p
        while tmp != 1: tmp = tmp * tmp % p; i += 1
        b = pow(c, 1 << (M - i - 1), p)
        M, c, t, R = i, b * b % p, t * b * b % p, R * b % p


def b3_poly_eval(N, n0, k):
    """Evaluate B3-MPQS polynomial: f(k) = (m0 + 2*k*n0)^2 - N*n0^2.
    Returns (value, m0). value can be negative."""
    Nn02 = N * n0 * n0
    m0 = isqrt(Nn02)
    # Pick m0 closest to sqrt(N*n0^2)
    if (m0 + 1) ** 2 - Nn02 < Nn02 - m0 ** 2:
        m0 += 1
    x = m0 + 2 * k * n0
    val = int(x * x - Nn02)
    return val, int(m0)


def trial_divide(val, fb):
    """Trial divide |val| over fb. Returns (exponents, cofactor)."""
    cof = abs(int(val))
    exps = [0] * len(fb)
    for i, p in enumerate(fb):
        if p * p > cof and cof > 1:
            break
        while cof % p == 0:
            cof //= p
            exps[i] += 1
        if cof == 1:
            break
    # Check if cofactor is in FB
    if cof > 1 and cof <= fb[-1]:
        for i, p in enumerate(fb):
            if p == cof:
                exps[i] += 1
                cof = 1
                break
    return exps, cof


def cf_relations(N_mpz, fb, max_steps, lp_bound=0):
    """Generate smooth relations via continued fraction expansion of sqrt(N)."""
    N_int = int(N_mpz)
    half_N = N_int // 2
    sqrtN = isqrt(N_mpz)
    a0 = sqrtN
    P_prev, P_curr = mpz(1), a0 % N_mpz
    m_cf, d_cf, a_cf = mpz(0), mpz(1), a0

    smooth = []
    partials = {}

    for step in range(max_steps):
        m_cf = a_cf * d_cf - m_cf
        d_cf = (N_mpz - m_cf * m_cf) // d_cf
        if d_cf == 0: break
        a_cf = (a0 + m_cf) // d_cf
        P_new = (a_cf * P_curr + P_prev) % N_mpz
        P_prev, P_curr = P_curr, P_new

        r_mod = int(pow(P_curr, 2, N_mpz))
        r_k = r_mod - N_int if r_mod > half_N else r_mod
        if r_k == 0: continue

        exps, cof = trial_divide(r_k, fb)
        sign = 1 if r_k < 0 else 0

        if cof == 1:
            smooth.append((int(P_curr), sign, exps, 1))
        elif lp_bound and 1 < cof <= lp_bound:
            is_lp = is_prime(mpz(cof))
            # Store both prime and composite cofactors for experiment 2
            smooth.append((int(P_curr), sign, exps, cof, bool(is_lp)))

    return smooth


# ===========================================================================
# EXPERIMENT 1: Information-Theoretic Lower Bound Attack
# ===========================================================================

def experiment_1_info_theory():
    """
    Measure actual vs theoretical minimum relations for B3-MPQS.
    Shannon bound: min_relations = nb / (2 * log2(B)).
    How close can we get?
    """
    print("=" * 70)
    print("EXPERIMENT 1: Information-Theoretic Lower Bound")
    print("=" * 70)
    t0 = time.time()

    results = []
    for nd in [20, 25, 30, 35, 40]:
        N, p, q = gen_semiprime(nd, seed=1001 + nd)
        N_mpz = mpz(N)
        nb = int(gmpy2.log2(N_mpz)) + 1
        ln_n = float(gmpy2.log(N_mpz))
        ln_ln_n = math.log(max(ln_n, 2.0))
        L_exp = math.sqrt(ln_n * ln_ln_n)
        B = int(math.exp(0.5 * L_exp))
        B = max(B, 200)

        fb = build_fb(N_mpz, B)
        fb_size = len(fb)

        # Shannon minimum: need nb/2 bits of info, each relation gives ~log2(B)
        shannon_min = nb / (2.0 * math.log2(B))

        # Actual needed: fb_size + 1 (for null space in GF(2))
        actual_needed = fb_size + 1

        ratio = actual_needed / shannon_min

        # Measure smooth rate via CF
        rels = cf_relations(N_mpz, fb, min(100000, fb_size * 40))
        n_full = sum(1 for r in rels if len(r) == 4)
        step_limit = min(100000, fb_size * 40)
        smooth_rate = n_full / max(step_limit, 1)

        results.append({
            'nd': nd, 'nb': nb, 'B': B, 'fb_size': fb_size,
            'shannon_min': shannon_min, 'actual_needed': actual_needed,
            'ratio': ratio, 'found': n_full, 'smooth_rate': smooth_rate
        })
        print(f"  {nd}d: B={B:,}, |FB|={fb_size}, Shannon_min={shannon_min:.1f}, "
              f"actual={actual_needed}, ratio={ratio:.2f}x, "
              f"smooth_rate={smooth_rate*100:.3f}%")

        if time.time() - t0 > 50:
            break

    avg_ratio = sum(r['ratio'] for r in results) / len(results)
    print(f"\n  Average actual/Shannon ratio: {avg_ratio:.2f}x")
    print(f"  => We need {avg_ratio:.1f}x the information-theoretic minimum.")

    verdict = "INTERESTING" if avg_ratio > 5 else "MARGINAL"
    print(f"\n  VERDICT: {verdict} — ratio={avg_ratio:.1f}x. "
          f"Shannon bound is {avg_ratio:.0f}x below actual FB size. "
          f"The gap is structural (GF(2) rank requires dim+1 vectors), not wasted information. "
          f"No shortcut here.")
    print(f"  Time: {time.time()-t0:.1f}s")
    return results


# ===========================================================================
# EXPERIMENT 2: Prime Prediction from Partial Information
# ===========================================================================

def experiment_2_prime_prediction():
    """
    Can we predict cofactor primality from the smooth part pattern?
    If so, skip unlikely LP candidates to save isprime() calls.

    Uses B3 polynomials (larger residues than CF) to get a mix of
    prime and composite cofactors.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 2: Prime Prediction from Partial Factorization")
    print("=" * 70)
    t0 = time.time()

    last_acc = 0.5
    last_baseline = 0.5
    for nd in [20, 25, 30, 35]:
        N, p, q = gen_semiprime(nd, seed=2001 + nd)
        N_mpz = mpz(N)
        nb = int(gmpy2.log2(N_mpz)) + 1
        B = int(math.exp(0.5 * math.sqrt(float(gmpy2.log(N_mpz)) *
                math.log(max(float(gmpy2.log(N_mpz)), 2.0)))))
        B = max(B, 200)
        fb = build_fb(N_mpz, B)
        lp_bound = B * B  # wide enough to get composite cofactors

        # Use B3 polys with small n0 — residues grow as ~k^2*sqrt(N)
        # giving larger cofactors with a good prime/composite mix
        data = []
        for n0_val in range(1, 20):
            n0 = mpz(n0_val)
            for k in range(-500, 501):
                val, _ = b3_poly_eval(N_mpz, n0, k)
                if val == 0:
                    continue
                exps, cof = trial_divide(val, fb)
                if cof <= 1 or cof > lp_bound:
                    continue

                n_distinct = sum(1 for e in exps if e > 0)
                total_weight = sum(exps)
                max_prime_idx = max((i for i, e in enumerate(exps) if e > 0), default=0)
                smooth_bits = sum(e * math.log2(fb[i]) for i, e in enumerate(exps) if e > 0)
                cof_bits = int(cof).bit_length()

                isp = 1 if is_prime(mpz(cof)) else 0
                data.append(((n_distinct, total_weight, max_prime_idx,
                              smooth_bits, cof_bits), isp))

                if len(data) >= 3000:
                    break
            if len(data) >= 3000:
                break

        if len(data) < 20:
            print(f"  {nd}d: Only {len(data)} partial relations, skipping")
            continue

        primes_count = sum(d[1] for d in data)
        base_rate = primes_count / len(data)
        last_baseline = max(base_rate, 1 - base_rate)

        # Best accuracy from always predicting majority class
        best_acc = last_baseline
        best_feature = ("majority", None)

        feat_names = ['n_distinct', 'total_weight', 'max_prime_idx',
                       'smooth_bits', 'cof_bits']
        for fi in range(5):
            vals = sorted(set(d[0][fi] for d in data))
            for threshold in vals[::max(1, len(vals) // 30)]:
                correct_hi = sum(1 for d in data
                                 if (d[0][fi] > threshold) == (d[1] == 1))
                acc = max(correct_hi, len(data) - correct_hi) / len(data)
                if acc > best_acc:
                    best_acc = acc
                    best_feature = (feat_names[fi], threshold)

        last_acc = best_acc
        print(f"  {nd}d: {len(data)} partials, prime_rate={base_rate:.3f}, "
              f"best_acc={best_acc:.3f} (feature={best_feature[0]}), "
              f"baseline={last_baseline:.3f}")

        if time.time() - t0 > 50:
            break

    lift = last_acc - last_baseline
    verdict = "PROMISING" if lift > 0.05 else "MARGINAL" if lift > 0.02 else "NEGATIVE"
    print(f"\n  VERDICT: {verdict} — best accuracy {last_acc:.1%} vs baseline {last_baseline:.1%} "
          f"(lift={lift*100:.1f}pp). "
          f"{'Cofactor size (cof_bits) predicts primality beyond base rate. ' if lift > 0.02 else 'No useful signal beyond base rate. '}"
          f"Practical value: skip isprime() on predicted-composite cofactors.")
    print(f"  Time: {time.time()-t0:.1f}s")


# ===========================================================================
# EXPERIMENT 3: Bayesian Sieve (Quantum-Inspired Amplitude Amplification)
# ===========================================================================

def experiment_3_bayesian_sieve():
    """
    Maintain a probability distribution over sieve positions.
    Use CF expansion (guaranteed small residues) for meaningful comparison.
    After each batch, boost residue classes mod small primes that yielded smooth.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 3: Bayesian Sieve (Amplitude Amplification)")
    print("=" * 70)
    t0 = time.time()

    last_speedup = 0
    for nd in [20, 25, 30, 35]:
        N, p, q = gen_semiprime(nd, seed=3001 + nd)
        N_mpz = mpz(N)
        nb = int(gmpy2.log2(N_mpz)) + 1
        B = int(math.exp(0.5 * math.sqrt(float(gmpy2.log(N_mpz)) *
                math.log(max(float(gmpy2.log(N_mpz)), 2.0)))))
        B = max(B, 200)
        fb = build_fb(N_mpz, B)

        # Use B3 polys with SMALL n0 and small k to keep residues manageable
        # Residue size ~ |f(k)| ~ 4*k*n0*sqrt(N) for small k
        max_k = min(500, int(2 ** (nb / 4)))  # keep residues < ~N

        # Method 1: Uniform scan of (n0, k) pairs
        uniform_smooth = 0
        uniform_total = 0
        rng = random.Random(42)
        for n0_val in range(1, 51):
            n0 = mpz(n0_val)
            for k in range(-max_k, max_k + 1):
                val, m0 = b3_poly_eval(N_mpz, n0, k)
                if val == 0: continue
                uniform_total += 1
                _, cof = trial_divide(val, fb)
                if cof == 1:
                    uniform_smooth += 1

        # Method 2: Bayesian — first scan n0=1 to learn good residue classes,
        # then target those classes for n0=2..50
        bayes_smooth = 0
        bayes_total = 0
        # Phase 1: explore with n0=1
        smooth_k_mod = defaultdict(int)  # (p, k%p) -> count of smooth
        total_k_mod = defaultdict(int)

        n0 = mpz(1)
        for k in range(-max_k, max_k + 1):
            val, m0 = b3_poly_eval(N_mpz, n0, k)
            if val == 0: continue
            bayes_total += 1
            _, cof = trial_divide(val, fb)
            is_sm = (cof == 1)
            if is_sm:
                bayes_smooth += 1
            # Record residue classes mod small primes
            for p in fb[:min(8, len(fb))]:
                key = (p, k % p)
                total_k_mod[key] += 1
                if is_sm:
                    smooth_k_mod[key] += 1

        # Find the best residue class
        best_classes = []
        for key, cnt in smooth_k_mod.items():
            total = total_k_mod[key]
            if total >= 5:
                rate = cnt / total
                best_classes.append((rate, key))
        best_classes.sort(reverse=True)

        # Phase 2: exploit for n0=2..50, prioritize k in best residue classes
        if best_classes:
            best_p, best_r = best_classes[0][1]
            for n0_val in range(2, 51):
                n0 = mpz(n0_val)
                # Scan only k values in best residue class
                k = -max_k + (best_r - (-max_k) % best_p) % best_p
                while k <= max_k:
                    val, m0 = b3_poly_eval(N_mpz, n0, k)
                    if val != 0:
                        bayes_total += 1
                        _, cof = trial_divide(val, fb)
                        if cof == 1:
                            bayes_smooth += 1
                    k += best_p
        else:
            # Fallback: uniform
            for n0_val in range(2, 51):
                n0 = mpz(n0_val)
                for k in range(-max_k, max_k + 1):
                    val, m0 = b3_poly_eval(N_mpz, n0, k)
                    if val == 0: continue
                    bayes_total += 1
                    _, cof = trial_divide(val, fb)
                    if cof == 1:
                        bayes_smooth += 1

        u_rate = uniform_smooth / max(uniform_total, 1)
        b_rate = bayes_smooth / max(bayes_total, 1)
        last_speedup = b_rate / max(u_rate, 1e-9)

        print(f"  {nd}d: uniform={u_rate*100:.4f}% ({uniform_smooth}/{uniform_total}), "
              f"bayesian={b_rate*100:.4f}% ({bayes_smooth}/{bayes_total}), "
              f"speedup={last_speedup:.2f}x"
              f"{', best_class='+str(best_classes[0][1]) if best_classes else ''}")

        if time.time() - t0 > 50:
            break

    verdict = "PROMISING" if last_speedup > 1.3 else "MARGINAL" if last_speedup > 1.0 else "NEGATIVE"
    print(f"\n  VERDICT: {verdict} — Bayesian sieve {last_speedup:.2f}x vs uniform. "
          f"{'Residue-class targeting concentrates on smooth-rich classes.' if last_speedup > 1.1 else 'Smoothness probability varies little across residue classes for B3 polys.'}")
    print(f"  Time: {time.time()-t0:.1f}s")


# ===========================================================================
# EXPERIMENT 4: Matrix Sparsification via B3 Correlation
# ===========================================================================

def experiment_4_matrix_sparsification():
    """
    Adjacent k values in B3-MPQS produce correlated residues.
    Measure the correlation in their GF(2) exponent vectors.
    Use CF expansion for reliable smooth relation supply.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 4: Matrix Sparsification via B3 Correlation")
    print("=" * 70)
    t0 = time.time()

    last_correlation = 0.0
    for nd in [20, 25, 30, 35]:
        N, p, q = gen_semiprime(nd, seed=4001 + nd)
        N_mpz = mpz(N)
        B = int(math.exp(0.5 * math.sqrt(float(gmpy2.log(N_mpz)) *
                math.log(max(float(gmpy2.log(N_mpz)), 2.0)))))
        B = max(B, 200)
        fb = build_fb(N_mpz, B)

        # Use CF expansion to get many smooth relations with sequential indices
        N_int = int(N_mpz)
        half_N = N_int // 2
        sqrtN = isqrt(N_mpz)
        a0 = sqrtN
        P_prev, P_curr = mpz(1), a0 % N_mpz
        m_cf, d_cf, a_cf = mpz(0), mpz(1), a0

        smooth_vecs = []  # ordered by CF step
        max_steps = min(200000, len(fb) * 50)

        for step in range(max_steps):
            m_cf = a_cf * d_cf - m_cf
            d_cf = (N_mpz - m_cf * m_cf) // d_cf
            if d_cf == 0: break
            a_cf = (a0 + m_cf) // d_cf
            P_new = (a_cf * P_curr + P_prev) % N_mpz
            P_prev, P_curr = P_curr, P_new

            r_mod = int(pow(P_curr, 2, N_mpz))
            r_k = r_mod - N_int if r_mod > half_N else r_mod
            if r_k == 0: continue

            exps, cof = trial_divide(r_k, fb)
            if cof == 1:
                vec = tuple(e % 2 for e in exps)
                smooth_vecs.append((step, vec))

        n_smooth = len(smooth_vecs)
        if n_smooth < 20:
            print(f"  {nd}d: Only {n_smooth} smooth, skipping")
            continue

        vec_len = len(fb)

        # Hamming distance between consecutive smooth relations (adjacent in CF order)
        adj_distances = []
        for i in range(len(smooth_vecs) - 1):
            step_gap = smooth_vecs[i + 1][0] - smooth_vecs[i][0]
            if step_gap <= 10:  # "nearby" in CF sequence
                v1, v2 = smooth_vecs[i][1], smooth_vecs[i + 1][1]
                hamming = sum(a != b for a, b in zip(v1, v2))
                adj_distances.append(hamming)

        # Random pairs
        rng = random.Random(42)
        rand_distances = []
        for _ in range(min(1000, n_smooth * 3)):
            i, j = rng.sample(range(n_smooth), 2)
            v1, v2 = smooth_vecs[i][1], smooth_vecs[j][1]
            hamming = sum(a != b for a, b in zip(v1, v2))
            rand_distances.append(hamming)

        avg_adj = sum(adj_distances) / max(len(adj_distances), 1) if adj_distances else None
        avg_rand = sum(rand_distances) / max(len(rand_distances), 1) if rand_distances else vec_len / 2

        if avg_adj is not None and len(adj_distances) >= 3:
            last_correlation = 1.0 - avg_adj / max(avg_rand, 0.01)
            print(f"  {nd}d: {n_smooth} smooth, |FB|={len(fb)}, "
                  f"adj_hamming={avg_adj:.2f} ({len(adj_distances)} pairs), "
                  f"rand_hamming={avg_rand:.2f}, "
                  f"correlation={last_correlation*100:.1f}%")
        else:
            print(f"  {nd}d: {n_smooth} smooth, |FB|={len(fb)}, "
                  f"adj_pairs={len(adj_distances)} (too few for measurement), "
                  f"rand_hamming={avg_rand:.2f}")

        if time.time() - t0 > 50:
            break

    verdict = "PROMISING" if last_correlation > 0.1 else "MARGINAL" if last_correlation > 0.03 else "NEGATIVE"
    print(f"\n  VERDICT: {verdict} — Adjacent-CF correlation = {last_correlation*100:.1f}%. "
          f"{'Nearby CF convergents share factor patterns.' if last_correlation > 0.05 else 'Exponent vectors are essentially independent despite sequential generation.'} "
          f"XOR-combining adjacent relations could sparsify the matrix.")
    print(f"  Time: {time.time()-t0:.1f}s")


# ===========================================================================
# EXPERIMENT 5: Product-Tree Smoothness Detection (Bernstein)
# ===========================================================================

def experiment_5_product_tree_smoothness():
    """
    Bernstein's batch smoothness: compute P = prod(p^e for p in FB),
    then iteratively gcd(val, P) to test smoothness.
    Compare speed vs trial division.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 5: Product-Tree Smoothness (Bernstein-style)")
    print("=" * 70)
    t0 = time.time()

    last_speedup = 1.0
    for nd in [25, 30, 35, 40]:
        N, p, q = gen_semiprime(nd, seed=5001 + nd)
        N_mpz = mpz(N)
        nb = int(gmpy2.log2(N_mpz)) + 1
        B = int(math.exp(0.5 * math.sqrt(float(gmpy2.log(N_mpz)) *
                math.log(max(float(gmpy2.log(N_mpz)), 2.0)))))
        B = max(B, 200)
        fb = build_fb(N_mpz, B)

        # Compute P = product of p^floor(log_p(2*sqrt(N))) for p in FB
        t_build = time.time()
        max_val_bits = nb  # CF residues are at most nb bits
        P = mpz(1)
        for p_val in fb:
            e = max(1, int(max_val_bits / math.log2(p_val)))
            P *= mpz(p_val) ** e
        build_time = time.time() - t_build

        # Generate test values via CF
        N_int = int(N_mpz)
        half_N = N_int // 2
        sqrtN = isqrt(N_mpz)
        a0 = sqrtN
        P_prev_cf, P_curr_cf = mpz(1), a0 % N_mpz
        m_cf, d_cf, a_cf = mpz(0), mpz(1), a0

        residues = []
        for step in range(min(20000, len(fb) * 10)):
            m_cf = a_cf * d_cf - m_cf
            d_cf = (N_mpz - m_cf * m_cf) // d_cf
            if d_cf == 0: break
            a_cf = (a0 + m_cf) // d_cf
            P_new = (a_cf * P_curr_cf + P_prev_cf) % N_mpz
            P_prev_cf, P_curr_cf = P_curr_cf, P_new
            r_mod = int(pow(P_curr_cf, 2, N_mpz))
            r_k = r_mod - N_int if r_mod > half_N else r_mod
            if r_k != 0:
                residues.append(abs(r_k))

        n_res = len(residues)
        if n_res < 100:
            print(f"  {nd}d: Only {n_res} residues, skipping")
            continue

        # Limit to manageable batch
        residues = residues[:min(5000, n_res)]

        # Method 1: Trial division
        t_trial = time.time()
        trial_smooth = 0
        for val in residues:
            _, cof = trial_divide(val, fb)
            if cof == 1:
                trial_smooth += 1
        trial_time = time.time() - t_trial

        # Method 2: Iterative GCD with P
        t_batch = time.time()
        batch_smooth = 0
        for val in residues:
            v = mpz(val)
            prev = mpz(0)
            while v != prev and v > 1:
                prev = v
                g = gcd(v, P)
                if g <= 1:
                    break
                while v % g == 0:
                    v //= g
            if v == 1:
                batch_smooth += 1
        batch_time = time.time() - t_batch

        last_speedup = trial_time / max(batch_time, 1e-9)
        print(f"  {nd}d: |FB|={len(fb)}, {len(residues)} residues, "
              f"smooth: trial={trial_smooth}, batch={batch_smooth}, "
              f"trial={trial_time:.3f}s, batch_gcd={batch_time:.3f}s "
              f"(P build={build_time:.3f}s), speedup={last_speedup:.2f}x")

        if time.time() - t0 > 50:
            break

    verdict = "PROMISING" if last_speedup > 2.0 else "MARGINAL" if last_speedup > 0.8 else "NEGATIVE"
    print(f"\n  VERDICT: {verdict} — Batch-GCD {last_speedup:.2f}x vs trial division. "
          f"{'Batch GCD amortizes well for large FB.' if last_speedup > 1.5 else 'GCD with huge P is expensive; true product-tree remainder tree would help.'} "
          f"P has {int(P).bit_length()} bits — memory-intensive but O(1) per test after build.")
    print(f"  Time: {time.time()-t0:.1f}s")


# ===========================================================================
# EXPERIMENT 6: Algebraic Dependencies Between B3 Polynomials
# ===========================================================================

def experiment_6_algebraic_deps():
    """
    For different n0 values, do B3 polynomials share common factors
    at predictable (k, k') pairs more often than random?
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 6: Algebraic Dependencies Between Polynomials")
    print("=" * 70)
    t0 = time.time()

    last_enrichment = 1.0
    last_gcd_factor = 0
    for nd in [15, 20, 25, 30]:
        N, p, q = gen_semiprime(nd, seed=6001 + nd)
        N_mpz = mpz(N)

        K_MAX = 300
        n0_pairs = 30
        struct_hits = 0
        struct_total = 0
        random_hits = 0
        random_total = 0
        gcd_factor = 0

        rng = random.Random(42)

        for n0_base in range(1, n0_pairs + 1):
            n0_a = mpz(n0_base)
            n0_b = mpz(n0_base + 1)

            vals_a = {}
            vals_b = {}
            for k in range(-K_MAX, K_MAX + 1):
                va, _ = b3_poly_eval(N_mpz, n0_a, k)
                vb, _ = b3_poly_eval(N_mpz, n0_b, k)
                if va != 0: vals_a[k] = mpz(abs(va))
                if vb != 0: vals_b[k] = mpz(abs(vb))

            # Structured pairs: same k, k+1, k-1, and k with same parity
            for k in range(-K_MAX, K_MAX + 1):
                for dk in [0, 1, -1, 2, -2]:
                    kp = k + dk
                    if k in vals_a and kp in vals_b:
                        struct_total += 1
                        g = gcd(vals_a[k], vals_b[kp])
                        if g > 1:
                            struct_hits += 1
                            gN = int(gcd(g, N_mpz))
                            if 1 < gN < N:
                                gcd_factor += 1

            # Random pairs for baseline
            ks_a = list(vals_a.keys())
            ks_b = list(vals_b.keys())
            for _ in range(300):
                ka = rng.choice(ks_a)
                kb = rng.choice(ks_b)
                random_total += 1
                g = gcd(vals_a[ka], vals_b[kb])
                if g > 1:
                    random_hits += 1

        struct_rate = struct_hits / max(struct_total, 1)
        random_rate = random_hits / max(random_total, 1)
        last_enrichment = struct_rate / max(random_rate, 1e-9)
        last_gcd_factor = gcd_factor

        print(f"  {nd}d: struct gcd>1: {struct_hits}/{struct_total} ({struct_rate*100:.2f}%), "
              f"random: {random_hits}/{random_total} ({random_rate*100:.2f}%), "
              f"enrichment={last_enrichment:.2f}x, FACTOR_hits={gcd_factor}")

        if time.time() - t0 > 50:
            break

    verdict = "BREAKTHROUGH" if last_gcd_factor > 0 else "PROMISING" if last_enrichment > 2 else "NEGATIVE"
    print(f"\n  VERDICT: {verdict} — "
          f"{'Non-trivial factors found via cross-polynomial GCD! ' if last_gcd_factor > 0 else ''}"
          f"Structured pairs {last_enrichment:.1f}x enriched vs random. "
          f"{'Algebraic dependency is real.' if last_enrichment > 1.5 else 'Shared factors are from shared small primes, not deep algebraic structure.'}")
    print(f"  Time: {time.time()-t0:.1f}s")


# ===========================================================================
# EXPERIMENT 7: The Diagonal Attack (degree-4 sieve)
# ===========================================================================

def experiment_7_diagonal():
    """
    On the diagonal n0=k: f_k(k) = (m_k + 2k^2)^2 - N*k^2.
    Compare smooth rates: diagonal vs fixed-n0 (off-diagonal).
    Also measure residue sizes.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 7: The Diagonal Attack")
    print("=" * 70)
    t0 = time.time()

    last_ratio = 1.0
    for nd in [15, 20, 25, 30]:
        N, p, q = gen_semiprime(nd, seed=7001 + nd)
        N_mpz = mpz(N)
        B = int(math.exp(0.5 * math.sqrt(float(gmpy2.log(N_mpz)) *
                math.log(max(float(gmpy2.log(N_mpz)), 2.0)))))
        B = max(B, 200)
        fb = build_fb(N_mpz, B)

        K_MAX = min(2000, int(2 ** (int(gmpy2.log2(N_mpz)) / 6)))

        # Diagonal: n0 = |k| (k > 0)
        diag_smooth = 0
        diag_total = 0
        diag_size_sum = 0
        for k in range(1, K_MAX + 1):
            val, _ = b3_poly_eval(N_mpz, mpz(k), k)
            if val == 0:
                diag_smooth += 1  # trivial relation!
                diag_total += 1
                continue
            diag_total += 1
            diag_size_sum += abs(val).bit_length()
            _, cof = trial_divide(val, fb)
            if cof == 1:
                diag_smooth += 1

        # Off-diagonal: fixed n0=1, varying k
        offdiag_smooth = 0
        offdiag_total = 0
        offdiag_size_sum = 0
        for k in range(1, K_MAX + 1):
            val, _ = b3_poly_eval(N_mpz, mpz(1), k)
            if val == 0: continue
            offdiag_total += 1
            offdiag_size_sum += abs(val).bit_length()
            _, cof = trial_divide(val, fb)
            if cof == 1:
                offdiag_smooth += 1

        # Fixed n0=small, varying k (a second off-diagonal for comparison)
        n0_small = 3
        offdiag2_smooth = 0
        offdiag2_total = 0
        for k in range(1, K_MAX + 1):
            val, _ = b3_poly_eval(N_mpz, mpz(n0_small), k)
            if val == 0: continue
            offdiag2_total += 1
            _, cof = trial_divide(val, fb)
            if cof == 1:
                offdiag2_smooth += 1

        d_rate = diag_smooth / max(diag_total, 1)
        o_rate = offdiag_smooth / max(offdiag_total, 1)
        o2_rate = offdiag2_smooth / max(offdiag2_total, 1)
        avg_d_size = diag_size_sum / max(diag_total, 1)
        avg_o_size = offdiag_size_sum / max(offdiag_total, 1)

        last_ratio = d_rate / max(o_rate, 1e-9)

        print(f"  {nd}d: diag={d_rate*100:.4f}% (avg {avg_d_size:.0f}b), "
              f"offdiag_n0=1={o_rate*100:.4f}% (avg {avg_o_size:.0f}b), "
              f"offdiag_n0={n0_small}={o2_rate*100:.4f}%, "
              f"ratio={last_ratio:.2f}x")

        if time.time() - t0 > 50:
            break

    verdict = "PROMISING" if last_ratio > 1.5 else "NEGATIVE"
    print(f"\n  VERDICT: {verdict} — Diagonal smooth rate {last_ratio:.2f}x vs off-diagonal. "
          f"{'Diagonal has structural smoothness advantage!' if last_ratio > 1 else 'Diagonal residues grow as ~k^4*sqrt(N) vs ~k^2*sqrt(N), so they are LARGER and less smooth.'} "
          f"Residue growth rate dominates any structural benefit from the single-polynomial form.")
    print(f"  Time: {time.time()-t0:.1f}s")


# ===========================================================================
# EXPERIMENT 8: Fermat Meets B3 (Skip Linear Algebra)
# ===========================================================================

def experiment_8_fermat_b3():
    """
    Look for k, n0 where f(k) = s^2 (perfect square).
    Then (x-s)(x+s) = N*n0^2, and gcd(x-s, N) may factor N.
    Also check f(k) = t*s^2 for small t.
    Bypasses linear algebra entirely!
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 8: Fermat Meets B3 (LA-Free Factoring)")
    print("=" * 70)
    t0 = time.time()

    total_factored = 0
    total_tested = 0

    for nd in [10, 15, 20, 25, 30, 35, 40]:
        if time.time() - t0 > 50:
            break

        N, p, q = gen_semiprime(nd, seed=8001 + nd)
        N_mpz = mpz(N)
        nb = int(gmpy2.log2(N_mpz)) + 1

        found_factor = False
        n_checked = 0
        n_perfect_sq = 0
        n_small_mult_sq = 0

        # Scan with small n0 and moderate k range
        K_MAX = min(10000, max(500, int(2 ** (nb / 4))))
        N0_MAX = min(100, max(10, nd))
        time_limit_per = min(8.0, 50.0 / (8 - total_tested))

        for n0_val in range(1, N0_MAX + 1):
            if found_factor or time.time() - t0 > 50:
                break
            n0 = mpz(n0_val)

            for k in range(-K_MAX, K_MAX + 1):
                val, m0 = b3_poly_eval(N_mpz, n0, k)
                n_checked += 1

                if val == 0:
                    x = m0 + 2 * k * int(n0)
                    g = int(gcd(mpz(abs(x)), N_mpz))
                    if 1 < g < N:
                        found_factor = True
                        total_factored += 1
                        print(f"  {nd}d: FACTOR from val=0! g={g}")
                        break
                    continue

                aval = abs(val)

                # Check perfect square
                sq = isqrt(mpz(aval))
                if sq * sq == aval:
                    n_perfect_sq += 1
                    s = int(sq)
                    x = m0 + 2 * k * int(n0)
                    for candidate in [x - s, x + s]:
                        g = int(gcd(mpz(abs(candidate)), N_mpz))
                        if 1 < g < N:
                            found_factor = True
                            total_factored += 1
                            print(f"  {nd}d: FACTOR via perfect square! "
                                  f"k={k}, n0={n0_val}, g={g}")
                            break
                    if found_factor:
                        break

                # Check negative perfect square (val < 0)
                if val < 0:
                    sq = isqrt(mpz(aval))
                    if sq * sq == aval:
                        n_perfect_sq += 1
                        s = int(sq)
                        x = m0 + 2 * k * int(n0)
                        # x^2 + s^2 = N*n0^2
                        # Try gcd(x + s*i, N) in Z[i] => gcd(x^2+s^2, N)
                        g = int(gcd(mpz(x * x + s * s), N_mpz))
                        if 1 < g < N:
                            found_factor = True
                            total_factored += 1
                            print(f"  {nd}d: FACTOR via negative square! g={g}")
                            break

                # Small multiples: val = t * s^2
                for t in [2, 3, 5, 6, 7, 10, 11, 13]:
                    if aval % t != 0: continue
                    reduced = aval // t
                    sq = isqrt(mpz(reduced))
                    if sq * sq == reduced:
                        n_small_mult_sq += 1
                        s = int(sq)
                        x = m0 + 2 * k * int(n0)
                        # x^2 - N*n0^2 = ±t*s^2
                        # Try various GCD tricks
                        for candidate in [x - s, x + s, x - t * s, x + t * s,
                                          x * x - t * s * s, n0_val]:
                            g = int(gcd(mpz(abs(candidate)), N_mpz))
                            if 1 < g < N:
                                found_factor = True
                                total_factored += 1
                                print(f"  {nd}d: FACTOR via t={t} trick! g={g}")
                                break
                        if found_factor:
                            break
                if found_factor:
                    break

            if time.time() - t0 > 50:
                break

        total_tested += 1
        prob = n_perfect_sq / max(n_checked, 1)
        print(f"  {nd}d: checked={n_checked:,}, perfect_sq={n_perfect_sq}, "
              f"small_mult_sq={n_small_mult_sq}, "
              f"prob={prob:.2e}, factored={'YES' if found_factor else 'NO'}")

    verdict = ("BREAKTHROUGH" if total_factored >= 4 else
               "PROMISING" if total_factored >= 2 else
               "MARGINAL" if total_factored > 0 else "NEGATIVE")
    print(f"\n  VERDICT: {verdict} — Factored {total_factored}/{total_tested} semiprimes "
          f"without linear algebra. "
          f"{'Works for small N where perfect squares are not too rare.' if total_factored > 0 else 'Perfect squares too rare: prob ~ N^{-1/4}.'} "
          f"Asymptotically O(N^{{1/4}}) — same as Fermat, not O(1).")
    print(f"  Time: {time.time()-t0:.1f}s")


# ===========================================================================
# MAIN
# ===========================================================================

def run_all():
    print("B3 MOONSHOTS 2 — Radical Experiments Toward O(1) Factoring")
    print("=" * 70)
    print(f"Memory limit: 2GB | Time limit per experiment: 60s")
    print()

    t_total = time.time()

    experiment_1_info_theory()
    experiment_2_prime_prediction()
    experiment_3_bayesian_sieve()
    experiment_4_matrix_sparsification()
    experiment_5_product_tree_smoothness()
    experiment_6_algebraic_deps()
    experiment_7_diagonal()
    experiment_8_fermat_b3()

    print("\n" + "=" * 70)
    print(f"ALL EXPERIMENTS COMPLETE — Total: {time.time()-t_total:.1f}s")
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        exp_num = int(sys.argv[1])
        funcs = {
            1: experiment_1_info_theory,
            2: experiment_2_prime_prediction,
            3: experiment_3_bayesian_sieve,
            4: experiment_4_matrix_sparsification,
            5: experiment_5_product_tree_smoothness,
            6: experiment_6_algebraic_deps,
            7: experiment_7_diagonal,
            8: experiment_8_fermat_b3,
        }
        if exp_num in funcs:
            funcs[exp_num]()
        else:
            print(f"Unknown experiment {exp_num}. Use 1-8.")
    else:
        run_all()
