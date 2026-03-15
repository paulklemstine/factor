#!/usr/bin/env python3
"""
B3-MPQS Moonshot Experiments — Searching for sub-L(1/2) breakthroughs.
=====================================================================

Each experiment tests a hypothesis about exploiting B3 parabolic structure
to accelerate factoring beyond classical MPQS limits.

Memory limit: 2GB. Each experiment: <60 seconds.
"""

import time, math, random, sys
from collections import defaultdict, Counter
import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, next_prime, legendre, invert

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def gen_semiprime(nd, seed=None):
    """Generate an nd-digit semiprime N = p*q with balanced factors."""
    rng = random.Random(seed)
    half_bits = int(nd * 3.32 / 2)
    while True:
        p = int(next_prime(mpz(rng.getrandbits(half_bits))))
        q = int(next_prime(mpz(rng.getrandbits(half_bits))))
        if p != q:
            N = p * q
            if len(str(N)) >= nd - 1:
                return N, p, q


def make_factor_base(N, B):
    """Build factor base of primes <= B with legendre(N,p) >= 0."""
    fb = [2]
    p = mpz(3)
    while p <= B:
        if legendre(N, p) >= 0:
            fb.append(int(p))
        p = next_prime(p)
    return fb


def trial_divide(val, fb, B):
    """Trial divide |val| over fb. Returns (cofactor, exponent_list)."""
    cof = abs(val)
    exps = [0] * len(fb)
    for i, p in enumerate(fb):
        if p * p > cof:
            break
        if cof % p == 0:
            e = 0
            while cof % p == 0:
                cof //= p
                e += 1
            exps[i] = e
            if cof == 1:
                break
    if cof > 1 and cof <= B:
        for i, p in enumerate(fb):
            if p == cof:
                exps[i] += 1
                cof = 1
                break
    return cof, exps


def b3_polynomial(N, n0):
    """
    B3 polynomial for given n0:
      m0 = round(n0 * sqrt(N))
      f(k) = (m0 + 2*k*n0)^2 - N * n0^2
    Returns (m0, n0, a, b, c) where f(k) = a*k^2 + b*k + c
      a = 4*n0^2, b = 4*m0*n0, c = m0^2 - N*n0^2
    """
    N = int(N)
    n0 = int(n0)
    sqrtN = int(isqrt(mpz(N)))
    # m0 = round(n0 * sqrt(N))
    m0 = int((mpz(n0) * mpz(sqrtN * 2 + 1) + 1) // 2)  # approx
    # Better: m0 = isqrt(N * n0^2) rounded
    Nn02 = mpz(N) * mpz(n0) * mpz(n0)
    sq = int(isqrt(Nn02))
    if (sq + 1) * (sq + 1) - Nn02 < Nn02 - sq * sq:
        m0 = sq + 1
    else:
        m0 = sq

    a = 4 * n0 * n0
    b = 4 * m0 * n0
    c = m0 * m0 - N * n0 * n0
    return m0, n0, a, b, c


def eval_b3(N, n0, k):
    """Evaluate f(k) = (m0 + 2*k*n0)^2 - N*n0^2 and the x value."""
    m0, n0_v, a, bcoef, c = b3_polynomial(N, n0)
    x_k = m0 + 2 * k * n0_v
    fk = x_k * x_k - N * n0_v * n0_v
    return fk, x_k, n0_v


# ===========================================================================
# EXPERIMENT 1: Resonance Between Polynomials
# ===========================================================================

def experiment_1_resonance(nd=35, num_polys=500, sieve_range=2000):
    """
    Do partial relations from different n0 polynomials combine at rates
    higher than random expectation?
    """
    print("=" * 70)
    print("EXPERIMENT 1: RESONANCE BETWEEN POLYNOMIALS")
    print("=" * 70)
    t0 = time.time()

    N, p, q = gen_semiprime(nd, seed=101)
    print(f"N = {N} ({len(str(N))}d)")

    ln_n = float(gmpy2.log(mpz(N)))
    ln_ln_n = math.log(max(ln_n, 2.0))
    B = int(math.exp(0.55 * math.sqrt(ln_n * ln_ln_n)))
    B = max(B, 300)
    B = min(B, 50000)
    fb = make_factor_base(N, B)
    lp_bound = B * 100
    print(f"B={B}, |FB|={len(fb)}, LP bound={lp_bound}")

    # Collect partial relations (single large prime) from many polynomials
    partials_by_poly = defaultdict(list)  # n0 -> [(lp, k)]
    all_lps = Counter()
    n0_values = list(range(1, num_polys + 1))

    for n0 in n0_values:
        m0, _, a, bcoef, c = b3_polynomial(N, n0)
        for k in range(-sieve_range, sieve_range + 1):
            fk = a * k * k + bcoef * k + c
            if fk == 0:
                continue
            cof, exps = trial_divide(fk, fb, B)
            if 1 < cof <= lp_bound and is_prime(mpz(cof)):
                partials_by_poly[n0].append(cof)
                all_lps[cof] += 1

    total_partials = sum(len(v) for v in partials_by_poly.values())
    print(f"Total partials: {total_partials} from {len(partials_by_poly)} polys")

    # Count cross-polynomial LP matches
    cross_matches = 0
    self_matches = 0
    lp_to_polys = defaultdict(list)
    for n0, lps in partials_by_poly.items():
        for lp in lps:
            lp_to_polys[lp].append(n0)

    for lp, poly_list in lp_to_polys.items():
        n = len(poly_list)
        if n < 2:
            continue
        unique_polys = set(poly_list)
        if len(unique_polys) > 1:
            cross_matches += n * (n - 1) // 2  # upper bound
        same_count = Counter(poly_list)
        for cnt in same_count.values():
            if cnt >= 2:
                self_matches += cnt * (cnt - 1) // 2

    # Random expectation: if LPs were uniformly distributed
    unique_lps = len(lp_to_polys)
    if total_partials > 0 and unique_lps > 0:
        avg_per_lp = total_partials / unique_lps
        random_cross = unique_lps * avg_per_lp * (avg_per_lp - 1) / 2
    else:
        random_cross = 0

    print(f"\nLarge primes seen: {unique_lps}")
    print(f"Cross-poly LP matches: {cross_matches}")
    print(f"Self-poly LP matches: {self_matches}")
    print(f"Random expectation (matches): {random_cross:.0f}")
    if random_cross > 0:
        ratio = (cross_matches + self_matches) / random_cross
        print(f"Actual/Random ratio: {ratio:.3f}")
    else:
        ratio = 0

    elapsed = time.time() - t0
    print(f"\nTime: {elapsed:.1f}s")

    if ratio > 1.5:
        verdict = "PROMISING — LP sharing significantly above random"
    elif ratio > 1.1:
        verdict = "MARGINAL — slight LP correlation detected"
    else:
        verdict = "NEGATIVE — LP sharing matches random expectation"
    print(f"VERDICT: {verdict}")
    return ratio


# ===========================================================================
# EXPERIMENT 2: Structured Polynomial Families
# ===========================================================================

def experiment_2_structured_families(nd=30, sieve_range=5000):
    """
    Do algebraically special n0 sequences produce higher smooth rates
    than random n0 values?
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 2: STRUCTURED POLYNOMIAL FAMILIES")
    print("=" * 70)
    t0 = time.time()

    N, p, q = gen_semiprime(nd, seed=202)
    print(f"N = {N} ({len(str(N))}d)")

    ln_n = float(gmpy2.log(mpz(N)))
    ln_ln_n = math.log(max(ln_n, 2.0))
    B = int(math.exp(0.55 * math.sqrt(ln_n * ln_ln_n)))
    B = max(B, 200)
    B = min(B, 20000)
    fb = make_factor_base(N, B)
    lp_bound = B * 100
    print(f"B={B}, |FB|={len(fb)}")

    # Generate different families of n0
    families = {}

    # Family 1: Sequential (baseline)
    families["sequential"] = list(range(1, 201))

    # Family 2: Fibonacci
    fibs = [1, 2]
    while fibs[-1] < 10000:
        fibs.append(fibs[-1] + fibs[-2])
    families["fibonacci"] = fibs[:200]

    # Family 3: CF convergent denominators of sqrt(N)
    sqrtN = isqrt(mpz(N))
    cf_denoms = []
    h_prev, h_curr = mpz(0), mpz(1)
    m_cf, d_cf, a_cf = mpz(0), mpz(1), sqrtN
    for _ in range(400):
        m_cf = a_cf * d_cf - m_cf
        d_cf_new = (mpz(N) - m_cf * m_cf) // d_cf
        if d_cf_new == 0:
            break
        d_cf = d_cf_new
        a_cf = (sqrtN + m_cf) // d_cf
        h_new = a_cf * h_curr + h_prev
        h_prev = h_curr
        h_curr = h_new
        denom = int(h_curr) % 100000
        if denom > 0:
            cf_denoms.append(denom)
    families["cf_convergents"] = cf_denoms[:200] if cf_denoms else list(range(1, 201))

    # Family 4: Primes
    primes_list = []
    pp = mpz(2)
    for _ in range(200):
        primes_list.append(int(pp))
        pp = next_prime(pp)
    families["primes"] = primes_list

    # Family 5: Random
    rng = random.Random(999)
    families["random"] = [rng.randint(1, 10000) for _ in range(200)]

    # Family 6: n0 where |c| = |m0^2 - N*n0^2| is minimized (Pell-like)
    # These have smallest initial residue
    scored = []
    for n0 in range(1, 2001):
        _, _, _, _, c = b3_polynomial(N, n0)
        scored.append((abs(c), n0))
    scored.sort()
    families["pell_like"] = [n0 for _, n0 in scored[:200]]

    # Measure smooth rate for each family
    results = {}
    for name, n0_list in families.items():
        smooth_count = 0
        partial_count = 0
        total_tested = 0

        for n0 in n0_list[:100]:  # limit for speed
            m0, _, a, bcoef, c = b3_polynomial(N, n0)
            for k in range(-sieve_range // 2, sieve_range // 2 + 1):
                fk = a * k * k + bcoef * k + c
                if fk == 0:
                    continue
                total_tested += 1
                cof, exps = trial_divide(fk, fb, B)
                if cof == 1:
                    smooth_count += 1
                elif 1 < cof <= lp_bound and is_prime(mpz(cof)):
                    partial_count += 1

        rate_full = smooth_count / max(total_tested, 1) * 100
        rate_all = (smooth_count + partial_count) / max(total_tested, 1) * 100
        results[name] = (rate_full, rate_all, total_tested, smooth_count, partial_count)
        print(f"  {name:20s}: full={rate_full:.4f}%  +LP={rate_all:.4f}%  "
              f"({smooth_count}F+{partial_count}LP / {total_tested})")

    elapsed = time.time() - t0
    print(f"\nTime: {elapsed:.1f}s")

    # Find best
    best_name = max(results, key=lambda n: results[n][1])
    best_rate = results[best_name][1]
    base_rate = results["sequential"][1]
    improvement = best_rate / max(base_rate, 0.0001)
    print(f"\nBest family: {best_name} ({best_rate:.4f}% vs baseline {base_rate:.4f}%)")
    print(f"Improvement: {improvement:.2f}x")

    if improvement > 2.0:
        verdict = "BREAKTHROUGH — structured family >2x better than random"
    elif improvement > 1.3:
        verdict = "PROMISING — structured family >1.3x improvement"
    else:
        verdict = "NEGATIVE — no family significantly outperforms sequential"
    print(f"VERDICT: {verdict}")
    return results


# ===========================================================================
# EXPERIMENT 3: The Free Relation Theorem
# ===========================================================================

def experiment_3_free_relations(nd=35, max_n0=10000):
    """
    How often is the base residue r0 = m0^2 - N*n0^2 prime or small prime power?
    These give 'almost free' single-prime relations.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 3: FREE RELATION THEOREM")
    print("=" * 70)
    t0 = time.time()

    N, p, q = gen_semiprime(nd, seed=303)
    print(f"N = {N} ({len(str(N))}d)")

    ln_n = float(gmpy2.log(mpz(N)))
    ln_ln_n = math.log(max(ln_n, 2.0))
    B = int(math.exp(0.55 * math.sqrt(ln_n * ln_ln_n)))
    B = max(B, 300)
    fb = make_factor_base(N, B)
    print(f"B={B}, |FB|={len(fb)}")

    # For each n0, compute r0 = m0^2 - N*n0^2 (the k=0 residue)
    prime_r0 = 0
    smooth_r0 = 0
    small_r0 = 0  # |r0| < B
    semifree = 0  # r0 has only 1-2 prime factors from FB
    total = 0
    size_sum = 0.0

    for n0 in range(1, max_n0 + 1):
        _, _, _, _, c = b3_polynomial(N, n0)
        r0 = c  # = m0^2 - N*n0^2
        if r0 == 0:
            continue
        total += 1
        ar0 = abs(r0)
        size_sum += math.log2(max(ar0, 1))

        if ar0 < B:
            small_r0 += 1

        if ar0 > 1 and is_prime(mpz(ar0)):
            prime_r0 += 1
            continue

        cof, exps = trial_divide(r0, fb, B)
        nz = sum(1 for e in exps if e > 0)
        if cof == 1:
            smooth_r0 += 1
        if cof == 1 and nz <= 2:
            semifree += 1

    avg_bits = size_sum / max(total, 1)
    print(f"\nScanned {total} values of n0")
    print(f"Average |r0| size: {avg_bits:.1f} bits")
    print(f"  |r0| < B (trivially smooth): {small_r0} ({small_r0/max(total,1)*100:.2f}%)")
    print(f"  |r0| is prime: {prime_r0} ({prime_r0/max(total,1)*100:.2f}%)")
    print(f"  r0 fully smooth over FB: {smooth_r0} ({smooth_r0/max(total,1)*100:.2f}%)")
    print(f"  r0 smooth with <=2 FB primes: {semifree} ({semifree/max(total,1)*100:.2f}%)")

    # Expected: |r0| ~ sqrt(N)/n0 for small n0, so for n0~1 it's ~sqrt(N) which is huge
    # For large n0, |r0| ~ O(1) by Pell equation theory

    # Find n0 values with smallest |r0|
    print(f"\nSmallest |r0| values:")
    smallest = []
    for n0 in range(1, min(max_n0 + 1, 50001)):
        _, _, _, _, c = b3_polynomial(N, n0)
        smallest.append((abs(c), n0, c))
    smallest.sort()
    for i in range(min(15, len(smallest))):
        ac, n0, c = smallest[i]
        if ac == 0:
            print(f"  n0={n0}: r0=0 (PERFECT!)")
        else:
            bits = int(math.log2(max(ac, 1))) + 1
            is_p = "PRIME" if is_prime(mpz(ac)) else ""
            cof, _ = trial_divide(c, fb, B)
            sm = "SMOOTH" if cof == 1 else f"cof={cof}"
            print(f"  n0={n0}: |r0|={ac} ({bits}b) {sm} {is_p}")

    elapsed = time.time() - t0
    print(f"\nTime: {elapsed:.1f}s")

    free_rate = (smooth_r0 + small_r0) / max(total, 1) * 100
    if free_rate > 5.0:
        verdict = "PROMISING — significant free relation rate"
    elif free_rate > 1.0:
        verdict = "MARGINAL — some free relations, may help"
    else:
        verdict = "NEGATIVE — free relations too rare to exploit"
    print(f"VERDICT: {verdict}")
    return free_rate


# ===========================================================================
# EXPERIMENT 4: Lattice Sieve on B3 Polynomials
# ===========================================================================

def experiment_4_lattice_sieve(nd=35, num_special_q=200):
    """
    Use special-q lattice sieve on B3 polynomials.
    For large prime q dividing f(k0), sieve the sublattice.
    Compare yield vs linear sieve.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 4: LATTICE SIEVE ON B3 POLYNOMIALS")
    print("=" * 70)
    t0 = time.time()

    N, p, q_factor = gen_semiprime(nd, seed=404)
    print(f"N = {N} ({len(str(N))}d)")

    ln_n = float(gmpy2.log(mpz(N)))
    ln_ln_n = math.log(max(ln_n, 2.0))
    B = int(math.exp(0.55 * math.sqrt(ln_n * ln_ln_n)))
    B = max(B, 300)
    B = min(B, 30000)
    fb = make_factor_base(N, B)
    lp_bound = B * 100
    print(f"B={B}, |FB|={len(fb)}")

    n0 = 1
    m0, _, a, bcoef, c = b3_polynomial(N, n0)
    sieve_range = 50000

    # LINEAR SIEVE baseline
    linear_smooth = 0
    linear_partial = 0
    linear_tested = 0

    for k in range(-sieve_range, sieve_range + 1):
        fk = a * k * k + bcoef * k + c
        if fk == 0:
            continue
        linear_tested += 1
        cof, exps = trial_divide(fk, fb, B)
        if cof == 1:
            linear_smooth += 1
        elif 1 < cof <= lp_bound and is_prime(mpz(cof)):
            linear_partial += 1

    linear_total = linear_smooth + linear_partial
    linear_rate = linear_total / max(linear_tested, 1)
    print(f"\nLinear sieve: {linear_total} rels ({linear_smooth}F+{linear_partial}LP) "
          f"from {linear_tested} candidates = {linear_rate*100:.4f}%")

    # LATTICE SIEVE: pick special-q primes, sieve sublattice
    # For each special q, find k0 where f(k0) ≡ 0 (mod q), then
    # sieve k = k0 + j*q for j in range
    lattice_smooth = 0
    lattice_partial = 0
    lattice_tested = 0

    # Pick special-q: medium-large primes from lp range
    sq_min = B + 1
    sq_max = min(B * 50, lp_bound)
    special_qs = []
    sq_p = next_prime(mpz(sq_min))
    while len(special_qs) < num_special_q and sq_p < sq_max:
        special_qs.append(int(sq_p))
        sq_p = next_prime(sq_p)

    for sq in special_qs:
        # Solve f(k) ≡ 0 (mod sq): a*k^2 + b*k + c ≡ 0 (mod sq)
        # disc = b^2 - 4*a*c
        disc = (bcoef * bcoef - 4 * a * c) % sq
        if disc < 0:
            disc += sq
        # Tonelli-Shanks for sqrt(disc) mod sq
        if legendre(disc, sq) < 1:
            continue
        sqrt_disc = int(gmpy2.isqrt_rem(mpz(disc))[0])  # not correct for mod
        # Use gmpy2 for modular sqrt
        try:
            sqrt_d = int(gmpy2.powmod(mpz(disc), mpz((sq + 1) // 4), mpz(sq)))
            if (sqrt_d * sqrt_d) % sq != disc % sq:
                # sq is not 3 mod 4, skip for simplicity
                continue
        except:
            continue

        inv_2a = int(invert(mpz(2 * a % sq), mpz(sq)))
        k0_1 = ((-bcoef + sqrt_d) * inv_2a) % sq
        k0_2 = ((-bcoef - sqrt_d) * inv_2a) % sq

        for k0 in set([k0_1, k0_2]):
            # Sieve along sublattice k = k0 + j*sq
            j_range = sieve_range // sq
            for j in range(-j_range, j_range + 1):
                k = k0 + j * sq
                if abs(k) > sieve_range:
                    continue
                fk = a * k * k + bcoef * k + c
                if fk == 0:
                    continue
                lattice_tested += 1
                # Divide out sq first
                fk_reduced = fk // sq if fk % sq == 0 else fk
                cof, exps = trial_divide(fk_reduced, fb, B)
                if cof == 1:
                    lattice_smooth += 1
                elif 1 < cof <= lp_bound and is_prime(mpz(cof)):
                    lattice_partial += 1

    lattice_total = lattice_smooth + lattice_partial
    lattice_rate = lattice_total / max(lattice_tested, 1)
    print(f"Lattice sieve: {lattice_total} rels ({lattice_smooth}F+{lattice_partial}LP) "
          f"from {lattice_tested} candidates = {lattice_rate*100:.4f}%")

    if linear_rate > 0:
        speedup = lattice_rate / linear_rate
    else:
        speedup = 0
    print(f"\nLattice/Linear hit rate ratio: {speedup:.2f}x")

    elapsed = time.time() - t0
    print(f"Time: {elapsed:.1f}s")

    if speedup > 5.0:
        verdict = "BREAKTHROUGH — lattice sieve vastly better per candidate"
    elif speedup > 2.0:
        verdict = "PROMISING — lattice sieve meaningfully concentrates smooths"
    elif speedup > 1.0:
        verdict = "MARGINAL — slight improvement from lattice structure"
    else:
        verdict = "NEGATIVE — lattice sieve no better than linear"
    print(f"VERDICT: {verdict}")
    return speedup


# ===========================================================================
# EXPERIMENT 5: Double Polynomial Sieve
# ===========================================================================

def experiment_5_double_poly(nd=30, num_polys=50, sieve_range=2000):
    """
    Sieve products f_{n1}(k1) * f_{n2}(k2). If the product is smooth,
    we get a relation even if neither individual value is smooth.
    Smoothness probability of product: should be L(1/4) if each is L(1/2).
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 5: DOUBLE POLYNOMIAL SIEVE")
    print("=" * 70)
    t0 = time.time()

    N, p, q = gen_semiprime(nd, seed=505)
    print(f"N = {N} ({len(str(N))}d)")

    ln_n = float(gmpy2.log(mpz(N)))
    ln_ln_n = math.log(max(ln_n, 2.0))
    B = int(math.exp(0.55 * math.sqrt(ln_n * ln_ln_n)))
    B = max(B, 200)
    B = min(B, 15000)
    fb = make_factor_base(N, B)
    lp_bound = B * 100
    print(f"B={B}, |FB|={len(fb)}")

    # Single-poly smooth rate
    single_smooth = 0
    single_partial = 0
    single_total = 0
    residues_by_poly = {}

    for n0 in range(1, num_polys + 1):
        m0, _, a, bcoef, c = b3_polynomial(N, n0)
        poly_residues = []
        for k in range(-sieve_range // 2, sieve_range // 2 + 1):
            fk = a * k * k + bcoef * k + c
            if fk == 0:
                continue
            single_total += 1
            cof, exps = trial_divide(fk, fb, B)
            if cof == 1:
                single_smooth += 1
            elif 1 < cof <= lp_bound and is_prime(mpz(cof)):
                single_partial += 1
            poly_residues.append((k, fk, cof, exps))
        residues_by_poly[n0] = poly_residues

    single_rate = (single_smooth + single_partial) / max(single_total, 1)
    print(f"Single-poly: {single_smooth}F+{single_partial}LP / {single_total} "
          f"= {single_rate*100:.4f}%")

    # Double-poly: for pairs of polys, check if product of their cofactors
    # (after partial factoring) is smooth
    # This is the key insight: if cof1 * cof2 is smooth, we get a relation
    double_extra = 0
    double_tested = 0

    # Sample pairs to avoid O(n^4) blowup
    rng = random.Random(42)
    poly_keys = list(residues_by_poly.keys())
    max_pairs = 200
    pairs_tested = 0

    for _ in range(min(max_pairs, len(poly_keys) * (len(poly_keys) - 1) // 2)):
        n1, n2 = rng.sample(poly_keys, 2)
        res1 = residues_by_poly[n1]
        res2 = residues_by_poly[n2]
        # Sample residues from each
        sample_size = min(200, len(res1), len(res2))
        s1 = rng.sample(res1, sample_size)
        s2 = rng.sample(res2, sample_size)

        for k1, fk1, cof1, exp1 in s1:
            if cof1 == 1 or cof1 > lp_bound:
                continue
            for k2, fk2, cof2, exp2 in s2[:20]:  # limit inner loop
                if cof2 == 1 or cof2 > lp_bound:
                    continue
                double_tested += 1
                product_cof = cof1 * cof2
                # Trial divide the product cofactor
                pcof, pexps = trial_divide(product_cof, fb, B)
                if pcof == 1:
                    double_extra += 1

        pairs_tested += 1

    if double_tested > 0:
        double_rate = double_extra / double_tested
    else:
        double_rate = 0
    print(f"\nDouble-poly cofactor products: {double_extra} smooth / {double_tested} tested "
          f"= {double_rate*100:.4f}%")

    elapsed = time.time() - t0
    print(f"Time: {elapsed:.1f}s")

    if double_rate > 0.01:
        verdict = "PROMISING — product smoothness rate exploitable"
    elif double_rate > 0.001:
        verdict = "MARGINAL — some product smoothness, low rate"
    else:
        verdict = "NEGATIVE — product cofactors rarely smooth"
    print(f"VERDICT: {verdict}")
    return double_rate


# ===========================================================================
# EXPERIMENT 6: Self-Initializing B3 (SIBS)
# ===========================================================================

def experiment_6_self_initializing(nd=35, sieve_range=50000):
    """
    When n0 -> n0+1, how much do sieve roots change?
    If the change is O(1) per FB prime, we can update incrementally.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 6: SELF-INITIALIZING B3 (SIBS)")
    print("=" * 70)
    t0 = time.time()

    N, p, q = gen_semiprime(nd, seed=606)
    print(f"N = {N} ({len(str(N))}d)")

    ln_n = float(gmpy2.log(mpz(N)))
    ln_ln_n = math.log(max(ln_n, 2.0))
    B = int(math.exp(0.55 * math.sqrt(ln_n * ln_ln_n)))
    B = max(B, 300)
    B = min(B, 30000)
    fb = make_factor_base(N, B)
    print(f"B={B}, |FB|={len(fb)}")

    # For each FB prime p, sieve root satisfies:
    #   a*k^2 + b*k + c ≡ 0 (mod p)
    # where a=4n0^2, b=4m0*n0, c=m0^2-N*n0^2
    # When n0 -> n0+1: a' = 4(n0+1)^2 = a + 8n0 + 4
    # So Δa = 8n0+4, which is small relative to a for large n0.

    # Measure: time to compute roots from scratch vs incremental update
    n0_start = 100
    num_polys = 500

    # Method 1: Full recomputation for each n0
    t_full_start = time.time()
    roots_full = []
    for n0 in range(n0_start, n0_start + num_polys):
        m0, _, a, bcoef, c = b3_polynomial(N, n0)
        poly_roots = []
        for pidx, pp in enumerate(fb[:200]):  # first 200 primes for speed
            # Solve a*k^2 + b*k + c ≡ 0 (mod pp)
            a_mod = a % pp
            b_mod = bcoef % pp
            c_mod = c % pp
            if a_mod == 0:
                if b_mod != 0:
                    try:
                        k_root = (-c_mod * int(invert(mpz(b_mod), mpz(pp)))) % pp
                        poly_roots.append(k_root)
                    except:
                        pass
                continue
            disc = (b_mod * b_mod - 4 * a_mod * c_mod) % pp
            if disc < 0:
                disc += pp
            if pp == 2:
                for k in range(2):
                    if (a_mod * k * k + b_mod * k + c_mod) % 2 == 0:
                        poly_roots.append(k)
            elif legendre(disc, pp) >= 0:
                try:
                    sqrt_d = int(gmpy2.powmod(mpz(disc), mpz((pp + 1) // 4), mpz(pp)))
                    if (sqrt_d * sqrt_d) % pp == disc:
                        inv_2a = int(invert(mpz(2 * a_mod), mpz(pp)))
                        r1 = ((-b_mod + sqrt_d) * inv_2a) % pp
                        r2 = ((-b_mod - sqrt_d) * inv_2a) % pp
                        poly_roots.append(r1)
                        if r1 != r2:
                            poly_roots.append(r2)
                except:
                    pass
        roots_full.append(poly_roots)
    t_full = time.time() - t_full_start

    # Method 2: Incremental update
    # When n0 -> n0+1: Δa = 8n0+4, Δb depends on Δm0
    # m0 changes by roughly sqrt(N) (since m0 ≈ n0*sqrt(N))
    # So b = 4*m0*n0 changes by ~4*(sqrt(N)*n0 + m0) which is large
    # Key insight: the DISCRIMINANT disc = b^2-4ac = 16*N*n0^4 (always!)
    # because disc = (4m0n0)^2 - 4*(4n0^2)*(m0^2-Nn0^2)
    #             = 16m0^2n0^2 - 16n0^2m0^2 + 16Nn0^4
    #             = 16Nn0^4
    # So disc mod p = 16*N*(n0^4 mod p)  — HIGHLY STRUCTURED!

    t_inc_start = time.time()
    roots_inc = []
    # Precompute 16*N mod p for each FB prime
    disc_base = [(16 * int(mpz(N) % mpz(pp))) % pp for pp in fb[:200]]

    for n0 in range(n0_start, n0_start + num_polys):
        m0, _, a, bcoef, c = b3_polynomial(N, n0)
        poly_roots = []
        for pidx, pp in enumerate(fb[:200]):
            a_mod = a % pp
            b_mod = bcoef % pp
            if a_mod == 0:
                continue
            if pp == 2:
                c_mod = c % 2
                for k in range(2):
                    if (a_mod * k * k + b_mod * k + c_mod) % 2 == 0:
                        poly_roots.append(k)
                continue
            # disc = 16*N*n0^4 mod p
            n0_mod = n0 % pp
            disc = (disc_base[pidx] * pow(n0_mod, 4, pp)) % pp
            if legendre(disc, pp) < 1:
                continue
            try:
                sqrt_d = int(gmpy2.powmod(mpz(disc), mpz((pp + 1) // 4), mpz(pp)))
                if (sqrt_d * sqrt_d) % pp != disc:
                    continue
                inv_2a = int(invert(mpz(2 * a_mod), mpz(pp)))
                r1 = ((-b_mod + sqrt_d) * inv_2a) % pp
                r2 = ((-b_mod - sqrt_d) * inv_2a) % pp
                poly_roots.append(r1)
                if r1 != r2:
                    poly_roots.append(r2)
            except:
                pass
        roots_inc.append(poly_roots)
    t_inc = time.time() - t_inc_start

    print(f"\nFull recomputation: {t_full:.3f}s for {num_polys} polys")
    print(f"Incremental (disc shortcut): {t_inc:.3f}s for {num_polys} polys")
    speedup = t_full / max(t_inc, 0.0001)
    print(f"Speedup: {speedup:.2f}x")

    # Key finding: disc = 16*N*n0^4
    print(f"\n*** KEY ALGEBRAIC IDENTITY: disc = 16*N*n0^4 (mod p) ***")
    print(f"This means the quadratic residuosity is determined solely by")
    print(f"legendre(N, p) and n0 mod p — independent of m0!")

    # Verify
    verify_ok = 0
    verify_total = 0
    for n0 in range(1, 100):
        m0, _, a, bcoef, c = b3_polynomial(N, n0)
        for pp in fb[1:50]:  # skip 2
            disc_actual = (bcoef * bcoef - 4 * a * c) % pp
            disc_formula = (16 * N * pow(n0, 4, pp)) % pp
            verify_total += 1
            if disc_actual % pp == disc_formula % pp:
                verify_ok += 1
    print(f"Identity verification: {verify_ok}/{verify_total} correct")

    elapsed = time.time() - t0
    print(f"\nTime: {elapsed:.1f}s")

    if speedup > 2.0 and verify_ok == verify_total:
        verdict = "PROMISING — disc=16Nn0^4 identity verified, enables faster root updates"
    elif verify_ok == verify_total:
        verdict = "CONFIRMED — algebraic identity holds, speedup modest"
    else:
        verdict = "ERROR — identity verification failed"
    print(f"VERDICT: {verdict}")
    return speedup


# ===========================================================================
# EXPERIMENT 7: Number Field B3 (NF-B3) — Complexity Probe
# ===========================================================================

def experiment_7_number_field_b3(nd=30):
    """
    Investigate if B3 polynomials admit a number field sieve interpretation.
    The B3 polynomial f(k) = 4n0^2*k^2 + 4m0*n0*k + (m0^2-N*n0^2) has
    root alpha = (-m0 ± sqrt(N)*n0) / (2*n0) in Q(sqrt(N)).

    If we can simultaneously sieve rational AND algebraic norms of elements
    a + b*alpha in Z[alpha], we might achieve L(1/3) complexity.

    Probe: measure algebraic norm sizes and smoothness rates.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 7: NUMBER FIELD B3 (NF-B3)")
    print("=" * 70)
    t0 = time.time()

    N, p, q = gen_semiprime(nd, seed=707)
    print(f"N = {N} ({len(str(N))}d)")

    ln_n = float(gmpy2.log(mpz(N)))
    ln_ln_n = math.log(max(ln_n, 2.0))
    B = int(math.exp(0.55 * math.sqrt(ln_n * ln_ln_n)))
    B = max(B, 200)
    B = min(B, 15000)
    fb = make_factor_base(N, B)
    print(f"B={B}, |FB|={len(fb)}")

    # B3 polynomial: f(k) = 4n0^2 * k^2 + 4m0*n0 * k + (m0^2 - N*n0^2)
    # Define the number field Q(alpha) where alpha is a root of f.
    # Norm of (a - b*alpha) in this field:
    #   N_{Q(alpha)/Q}(a - b*alpha) = a^2 - a*b*(-sum of roots) + b^2*(product of roots)
    #   = a^2 + a*b*(m0/n0) + b^2*(m0^2 - N*n0^2)/(4n0^2)
    # The rational side: a - b*m, where m = m0/(2n0) approximately
    #
    # For GNFS-like approach:
    #   Rational norm: |a - b * m_rational|
    #   Algebraic norm: |N_K(a - b*alpha)| = |f_d * b^d * f(a/b)| for degree-d poly
    #   For degree 2: |4n0^2 * (a^2/b^0) ...| — but this gives same size as MPQS

    # The critical question: can we make DEGREE > 2 B3 polynomials?
    # Key idea: compose B3 maps! B3^k gives higher-degree polynomials in k.

    # Test: measure norm sizes for degree-2 B3 vs random quadratic
    n0 = 1
    m0, _, a, bcoef, c = b3_polynomial(N, n0)

    # Rational norm: |a_val - b_val * (m0 // n0)|
    # Algebraic norm: f(a_val/b_val) * (leading coeff) * b_val^2
    m_rational = m0  # since n0=1

    # Compare sizes
    rat_sizes = []
    alg_sizes = []
    both_smooth = 0
    total = 0

    for a_val in range(-500, 501):
        for b_val in range(1, 101):
            total += 1
            rat_norm = abs(a_val - b_val * m_rational)
            alg_norm = abs(a * a_val * a_val + bcoef * a_val * b_val + c * b_val * b_val)

            if rat_norm == 0 or alg_norm == 0:
                continue

            rat_bits = int(math.log2(max(rat_norm, 1))) + 1
            alg_bits = int(math.log2(max(alg_norm, 1))) + 1
            rat_sizes.append(rat_bits)
            alg_sizes.append(alg_bits)

            # Check both smooth
            rat_cof, _ = trial_divide(rat_norm, fb, B)
            if rat_cof != 1:
                continue
            alg_cof, _ = trial_divide(alg_norm, fb, B)
            if alg_cof == 1:
                both_smooth += 1

    avg_rat = sum(rat_sizes) / max(len(rat_sizes), 1)
    avg_alg = sum(alg_sizes) / max(len(alg_sizes), 1)
    nb = int(gmpy2.log2(mpz(N))) + 1

    print(f"\nAvg rational norm: {avg_rat:.1f} bits (N is {nb} bits)")
    print(f"Avg algebraic norm: {avg_alg:.1f} bits")
    print(f"Both smooth: {both_smooth} / {total} = {both_smooth/max(total,1)*100:.4f}%")

    # GNFS comparison: for degree d, algebraic norm ~ N^(1/d), rational ~ N^(1/d)
    # Degree 2: norms ~ N^(1/2) = same as QS
    # Degree 3 would give norms ~ N^(1/3) — but B3 is inherently degree 2
    print(f"\nDegree-2 algebraic norm ~ N^(1/2) = {nb//2} bits (actual avg: {avg_alg:.0f})")
    print(f"For L(1/3) we need degree >= 3, giving norms ~ N^(1/3) = {nb//3} bits")
    print(f"Gap: {avg_alg - nb//3:.0f} bits — this is the L(1/2)->L(1/3) barrier")

    # Can we construct degree-3 B3 polynomials?
    # B3^2: (m,n) -> (m+2n, n) -> (m+4n, n)
    # x_0 = m^2 - N*n^2, x_1 = (m+2n)^2 - N*n^2, x_2 = (m+4n)^2 - N*n^2
    # Product: x_0*x_1*x_2 is degree 6 in m, or degree 2 in k if k parametrizes shifts
    # Not helpful — still degree 2 in the sieve variable

    print(f"\nDegree-3 construction attempt:")
    print(f"  B3 parabolic gives f(k) = 4n0^2*k^2 + ... which is ALWAYS degree 2")
    print(f"  Composing B3 maps does NOT increase polynomial degree")
    print(f"  For NF-B3 to work, we need a non-obvious degree-3+ construction")

    elapsed = time.time() - t0
    print(f"\nTime: {elapsed:.1f}s")

    verdict = ("THEORETICALLY BLOCKED — B3 is inherently degree 2, giving L(1/2). "
               "Need novel degree-3+ construction for L(1/3).")
    print(f"VERDICT: {verdict}")
    return avg_alg


# ===========================================================================
# EXPERIMENT 8: Batch Smoothness Detection
# ===========================================================================

def experiment_8_batch_smoothness(nd=35, num_polys=200, sieve_range=1000):
    """
    Batch smoothness: compute product tree of residues, then GCD with
    product of primes. This amortizes smoothness detection cost.

    Bernstein's batch algorithm: O(n log^2 n) for n values vs O(n * B) naive.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 8: BATCH SMOOTHNESS DETECTION")
    print("=" * 70)
    t0 = time.time()

    N, p, q = gen_semiprime(nd, seed=808)
    print(f"N = {N} ({len(str(N))}d)")

    ln_n = float(gmpy2.log(mpz(N)))
    ln_ln_n = math.log(max(ln_n, 2.0))
    B = int(math.exp(0.55 * math.sqrt(ln_n * ln_ln_n)))
    B = max(B, 300)
    B = min(B, 30000)
    fb = make_factor_base(N, B)
    print(f"B={B}, |FB|={len(fb)}")

    # Collect residues from multiple polynomials
    residues = []
    for n0 in range(1, num_polys + 1):
        m0, _, a, bcoef, c = b3_polynomial(N, n0)
        for k in range(-sieve_range // 2, sieve_range // 2 + 1):
            fk = a * k * k + bcoef * k + c
            if fk != 0:
                residues.append((n0, k, abs(fk)))

    total_residues = len(residues)
    print(f"Total residues: {total_residues}")

    # Method 1: Naive trial division
    t_naive_start = time.time()
    naive_smooth = 0
    for _, _, r in residues:
        cof, _ = trial_divide(r, fb, B)
        if cof == 1:
            naive_smooth += 1
    t_naive = time.time() - t_naive_start
    print(f"\nNaive trial division: {naive_smooth} smooth, {t_naive:.3f}s")

    # Method 2: Batch GCD (Bernstein-style product tree)
    # Build product of all FB primes raised to floor(log_p(2^bits))
    t_batch_start = time.time()

    # Compute primorial^e where e = log_p(max_residue)
    max_residue_bits = max(int(math.log2(max(r for _, _, r in residues))) + 1, 1)

    # Product of p^(floor(log_p(2^bits))) for each FB prime
    # This is the "smooth part detector"
    primorial = mpz(1)
    for pp in fb:
        e = max(1, max_residue_bits // max(int(math.log2(pp)), 1))
        primorial *= mpz(pp) ** e

    # Now for each residue, gcd(residue, primorial) extracts the smooth part
    # But computing gcd with a huge primorial is slow. Use product tree instead.

    # Product tree approach: build tree of residues, then remainder tree with primorial
    # For simplicity, use batched GCD: split residues into chunks
    chunk_size = 500
    batch_smooth = 0

    for start in range(0, len(residues), chunk_size):
        chunk = residues[start:start + chunk_size]
        # Product of chunk residues
        prod = mpz(1)
        for _, _, r in chunk:
            prod *= mpz(r)

        # GCD with primorial — extracts the part that's B-smooth
        g = gcd(prod, primorial)

        # Now check individual residues against g
        for _, _, r in chunk:
            r_mpz = mpz(r)
            # Extract smooth part via GCD
            smooth_part = gcd(r_mpz, g)
            cof = r_mpz
            while True:
                g2 = gcd(cof, smooth_part)
                if g2 == 1:
                    break
                cof //= g2
            # Repeat to remove all prime powers
            for _ in range(max_residue_bits):
                g2 = gcd(cof, primorial)
                if g2 <= 1:
                    break
                cof //= g2
            if cof == 1:
                batch_smooth += 1

    t_batch = time.time() - t_batch_start
    print(f"Batch GCD: {batch_smooth} smooth, {t_batch:.3f}s")

    # Method 3: Remainder tree (proper Bernstein algorithm)
    # Build product tree bottom-up, then remainder tree top-down
    t_rem_start = time.time()

    # Take a manageable subset
    subset = [mpz(abs(r)) for _, _, r in residues[:5000]]

    def product_tree(values):
        """Build product tree bottom-up."""
        if len(values) == 0:
            return [[mpz(1)]]
        tree = [values]
        while len(tree[-1]) > 1:
            level = tree[-1]
            new_level = []
            for i in range(0, len(level), 2):
                if i + 1 < len(level):
                    new_level.append(level[i] * level[i + 1])
                else:
                    new_level.append(level[i])
            tree.append(new_level)
        return tree

    def remainder_tree(prod_tree, M):
        """Top-down remainder tree: compute M mod each leaf."""
        n_levels = len(prod_tree)
        rem = [None] * n_levels
        rem[n_levels - 1] = [M % prod_tree[n_levels - 1][0]]
        for level in range(n_levels - 2, -1, -1):
            rem[level] = []
            for i in range(len(prod_tree[level])):
                parent_idx = i // 2
                parent_rem = rem[level + 1][parent_idx]
                rem[level].append(parent_rem % prod_tree[level][i])
        return rem[0]

    if len(subset) > 0:
        ptree = product_tree(subset)
        remainders = remainder_tree(ptree, primorial)

        rem_smooth = 0
        for i, r in enumerate(subset):
            if r <= 1:
                continue
            # primorial mod r_i tells us the smooth part
            g_val = gcd(remainders[i], r)
            cof = r
            while True:
                g2 = gcd(cof, g_val)
                if g2 <= 1:
                    break
                cof //= g2
            # Iterate to remove all prime powers
            for _ in range(5):
                g2 = gcd(cof, primorial)
                if g2 <= 1:
                    break
                cof //= g2
            if cof == 1:
                rem_smooth += 1

        t_rem = time.time() - t_rem_start
        print(f"Remainder tree: {rem_smooth} smooth (of {len(subset)}), {t_rem:.3f}s")
    else:
        t_rem = 0
        rem_smooth = 0

    # Compare throughput
    naive_rate = total_residues / max(t_naive, 0.001)
    batch_rate = total_residues / max(t_batch, 0.001)
    print(f"\nThroughput: naive={naive_rate:.0f}/s, batch={batch_rate:.0f}/s")
    if t_naive > 0:
        speedup = t_naive / max(t_batch, 0.001)
    else:
        speedup = 0
    print(f"Batch/Naive speedup: {speedup:.2f}x")

    elapsed = time.time() - t0
    print(f"\nTime: {elapsed:.1f}s")

    if speedup > 3.0:
        verdict = "PROMISING — batch smoothness significantly faster"
    elif speedup > 1.5:
        verdict = "MARGINAL — batch gives modest speedup in Python"
    else:
        verdict = "NEGATIVE — overhead dominates in Python (C would differ)"
    print(f"VERDICT: {verdict}")
    print(f"NOTE: In C with GMP, batch GCD should be ~10-50x faster than trial division")
    return speedup


# ===========================================================================
# RUN ALL
# ===========================================================================

def run_all():
    """Run all 8 moonshot experiments and summarize."""
    print("*" * 70)
    print("B3-MPQS MOONSHOT EXPERIMENTS")
    print(f"Searching for sub-L(1/2) breakthroughs")
    print("*" * 70)

    results = {}
    experiments = [
        ("1. Resonance Between Polynomials", experiment_1_resonance),
        ("2. Structured Polynomial Families", experiment_2_structured_families),
        ("3. Free Relation Theorem", experiment_3_free_relations),
        ("4. Lattice Sieve on B3", experiment_4_lattice_sieve),
        ("5. Double Polynomial Sieve", experiment_5_double_poly),
        ("6. Self-Initializing B3 (SIBS)", experiment_6_self_initializing),
        ("7. Number Field B3 (NF-B3)", experiment_7_number_field_b3),
        ("8. Batch Smoothness Detection", experiment_8_batch_smoothness),
    ]

    for name, func in experiments:
        print(f"\n{'#' * 70}")
        print(f"# RUNNING: {name}")
        print(f"{'#' * 70}")
        try:
            t0 = time.time()
            result = func()
            elapsed = time.time() - t0
            results[name] = (result, elapsed)
            if elapsed > 55:
                print(f"WARNING: Experiment took {elapsed:.1f}s (near 60s limit)")
        except Exception as e:
            print(f"EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            results[name] = (None, 0)

    # Summary
    print("\n" + "=" * 70)
    print("MOONSHOT SUMMARY")
    print("=" * 70)
    for name, (result, elapsed) in results.items():
        status = "OK" if result is not None else "FAIL"
        print(f"  {name}: {status} ({elapsed:.1f}s)")

    print("\nKEY FINDINGS:")
    print("  - Exp 6 discovered: disc = 16*N*n0^4 (algebraic identity for fast root updates)")
    print("  - Exp 7 shows: B3 is inherently degree-2 -> L(1/2) barrier is fundamental")
    print("  - Exp 4 tests whether lattice sieve concentrates smooths")
    print("  - Exp 2/3 probe whether special n0 families give free/cheap relations")
    print("  - Exp 5 tests if product-smoothness gives L(1/4) rate")
    print("  - Exp 8 tests batch smoothness as an engineering speedup")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        exp_num = int(sys.argv[1])
        funcs = {
            1: experiment_1_resonance,
            2: experiment_2_structured_families,
            3: experiment_3_free_relations,
            4: experiment_4_lattice_sieve,
            5: experiment_5_double_poly,
            6: experiment_6_self_initializing,
            7: experiment_7_number_field_b3,
            8: experiment_8_batch_smoothness,
        }
        if exp_num in funcs:
            funcs[exp_num]()
        else:
            print(f"Unknown experiment: {exp_num}. Choose 1-8.")
    else:
        run_all()
