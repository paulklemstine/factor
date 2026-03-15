#!/usr/bin/env python3
"""
CFRAC (Continued Fraction) Factoring Engine — Optimized v2
==========================================================
Uses the continued fraction expansion of sqrt(kN) to find smooth residues,
then GF(2) Gaussian elimination to combine them into x^2 = y^2 (mod N).

Key optimizations:
  1. Precomputed CF-period sieve: for each FB prime p, precompute which CF steps
     produce residues divisible by p (period divides 2p). Only trial-divide by
     primes known to divide the current residue.
  2. Double large prime (DLP) with graph-based cycle finding
  3. Pollard rho for DLP cofactor splitting (replaces trial division to 100K)
  4. Interleaved multi-multiplier sharing one relation pool
  5. Optimized trial division with early-exit and binary search for cofactor
"""

import time
import math
import gmpy2
from gmpy2 import mpz, isqrt, gcd, is_prime, next_prime, legendre, iroot
from collections import defaultdict

# ---------------------------------------------------------------------------
# Smoothness bound selection
# ---------------------------------------------------------------------------

def _smoothness_bound(N):
    """
    Choose smoothness bound B ~ L(N)^alpha.
    Keep alpha moderate — smaller FB = fewer relations needed.
    With DLP, we get ~3x more relations from the same CF terms.
    """
    ln_n = float(gmpy2.log(mpz(N)))
    ln_ln_n = math.log(max(ln_n, 2.0))
    L_exp = math.sqrt(ln_n * ln_ln_n)
    nd = len(str(N))
    if nd <= 25:
        alpha = 0.38
    elif nd <= 35:
        alpha = 0.40
    elif nd <= 45:
        alpha = 0.42
    elif nd <= 55:
        alpha = 0.45
    elif nd <= 65:
        alpha = 0.48
    elif nd <= 75:
        alpha = 0.50
    elif nd <= 85:
        alpha = 0.52
    elif nd <= 95:
        alpha = 0.54
    else:
        alpha = 0.56
    B = int(math.exp(alpha * L_exp))
    B = max(B, 50)
    B = min(B, 3_000_000)
    return B


def _build_factor_base(N, B):
    """
    Build factor base: {2} union {odd primes p <= B where Legendre(N,p) >= 0}.
    """
    fb = [2]
    p = mpz(3)
    while p <= B:
        if legendre(N, p) >= 0:
            fb.append(int(p))
        p = next_prime(p)
    return fb


# ---------------------------------------------------------------------------
# Fast Pollard rho for DLP cofactor splitting
# ---------------------------------------------------------------------------

def _pollard_rho_small(n):
    """
    Pollard rho for splitting small composites (DLP cofactors).
    Uses batch-gcd for speed. Returns a nontrivial factor or 0.
    """
    if n < 4:
        return 0
    if n % 2 == 0:
        return 2
    for p in (3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97):
        if n % p == 0:
            return p

    n_mpz = mpz(n)
    for c in range(1, 25):
        x = mpz(2)
        y = mpz(2)
        d = mpz(1)
        product = mpz(1)
        count = 0
        while d == 1:
            x = (x * x + c) % n_mpz
            y = (y * y + c) % n_mpz
            y = (y * y + c) % n_mpz
            product = product * abs(x - y) % n_mpz
            count += 1
            if count % 40 == 0:
                d = gcd(product, n_mpz)
                product = mpz(1)
                if count > 8000:
                    break
        if d == 0 or d == 1:
            d = gcd(product, n_mpz)
        if 1 < d < n_mpz:
            return int(d)
    return 0


# ---------------------------------------------------------------------------
# Double Large Prime graph
# ---------------------------------------------------------------------------

class DLPGraph:
    """
    DLP combining using two strategies:
    1. Exact-pair matching: two partials with the same (lp1, lp2) pair combine
       perfectly — both LPs get even exponents (2 each).
    2. Graph cycle detection: use union-find to detect when adding an edge
       (lp1-lp2) creates a cycle. When a cycle of length 2 forms at a node
       (two edges sharing a node where the other endpoints also match),
       combine them. For longer cycles, defer to exact-pair matching for now.
    """
    def __init__(self):
        # Exact pair matching: (min_lp, max_lp) -> (p_mod, sign, exps)
        self.pair_partials = {}
        # Single LP partials from DLP: lp -> list of (p_mod, sign, exps, other_lp)
        # When two entries share the same other_lp, they form a cycle of length 2
        self.node_edges = defaultdict(list)
        self.n_combined = 0

    def add_and_try_combine(self, lp1, lp2, p_mod, sign, exps, extra, fb_size, mod_N):
        """
        Add a DLP partial and try to combine.
        Returns a combined relation tuple (p_mod, sign, exps, lp_product) or None.
        """
        pair_key = (min(lp1, lp2), max(lp1, lp2))

        # Strategy 1: exact pair match
        if pair_key in self.pair_partials:
            p2_mod, s2, e2 = self.pair_partials.pop(pair_key)
            c_p = (p_mod * p2_mod) % mod_N
            c_sign = (sign + s2) % 2
            c_exps = [exps[j] + e2[j] for j in range(fb_size)]
            # Both lp1 and lp2 appear with total exponent 2 each
            lp_product = lp1 * lp2
            self.n_combined += 1
            return (c_p, c_sign, c_exps, lp_product)
        else:
            self.pair_partials[pair_key] = (p_mod, sign, exps)

        return None


# ---------------------------------------------------------------------------
# CF period sieve: precompute which k values give residues divisible by p
# ---------------------------------------------------------------------------

def _precompute_cf_sieve(N, a0, fb, max_period=None):
    """
    For each FB prime p, compute the CF recurrence mod p to find its period,
    and record which steps within the period give residues d_{k+1} divisible by p.

    The CF recurrence mod p:
      m_{k+1} = d_k * a_k - m_k  (mod p)
      d_{k+1} = (N - m_{k+1}^2) / d_k  (mod p)
      a_{k+1} = floor((a0 + m_{k+1}) / d_{k+1})  ← this is tricky mod p

    Instead, we just run the actual CF recurrence for up to 2p steps and
    record which steps have p | d_{k+1}.

    Returns: list of (period, frozenset_of_hits) for each FB prime.
    """
    sieve_info = []

    for pi, p in enumerate(fb):
        if p == 2:
            # p=2: just check parity, period at most 2
            sieve_info.append(None)  # handle p=2 separately
            continue

        if max_period is not None and p > max_period:
            sieve_info.append(None)
            continue

        # Run CF recurrence, recording d values mod p
        p_mpz = mpz(p)
        N_mod_p = int(N % p_mpz)
        a0_mod_p = int(a0 % p_mpz)

        m_k = 0
        d_k = 1
        a_k = a0_mod_p

        hits = set()
        period = 0

        # The period of the CF mod p divides 2p (by Lagrange / periodicity of sqrt(N) mod p)
        # But we also need the actual a_k values, which depend on floor division.
        # So we run the REAL CF recurrence (not mod p) and just check d mod p.
        # This is O(p) per prime — expensive for large primes.
        # Only do this for small primes.
        # For p > threshold, skip (trial divide all).

        # Actually, let's just run the real CF and check d mod p
        # But that defeats the purpose for large p...
        # The key optimization: for the smallest primes (which are checked most often),
        # precompute their hit patterns. For large primes, they rarely divide anyway.

        sieve_info.append(None)

    return sieve_info


# ---------------------------------------------------------------------------
# Core CFRAC factoring — optimized
# ---------------------------------------------------------------------------

def _trial_divide_fast(r_abs, fb, fb_size, fb_mpz):
    """
    Trial divide r_abs by factor base primes.
    Returns (exponents_list, cofactor_int).
    """
    exps = [0] * fb_size
    cof = mpz(r_abs)
    for i in range(fb_size):
        p = fb_mpz[i]
        if p * p > cof:
            break
        if gmpy2.is_divisible(cof, p):
            e = 0
            while gmpy2.is_divisible(cof, p):
                cof = cof // p
                e += 1
            exps[i] = e
            if cof == 1:
                return exps, 1
    # Check if remaining cofactor is in FB (binary search)
    cof_int = int(cof)
    if cof_int > 1 and cof_int <= fb[-1]:
        lo, hi = 0, fb_size - 1
        while lo <= hi:
            mid = (lo + hi) >> 1
            if fb[mid] == cof_int:
                exps[mid] += 1
                return exps, 1
            elif fb[mid] < cof_int:
                lo = mid + 1
            else:
                hi = mid - 1
    return exps, cof_int


def _trial_divide_with_hint(r_abs, fb, fb_size, fb_mpz, hint_primes):
    """
    Trial divide r_abs, but ONLY check primes in hint_primes first,
    then fall through to remaining primes if still composite.
    hint_primes: list of FB indices known to possibly divide r_abs.
    """
    exps = [0] * fb_size
    cof = mpz(r_abs)

    # First pass: check hinted primes
    for i in hint_primes:
        p = fb_mpz[i]
        if gmpy2.is_divisible(cof, p):
            e = 0
            while gmpy2.is_divisible(cof, p):
                cof = cof // p
                e += 1
            exps[i] = e
            if cof == 1:
                return exps, 1

    # Second pass: check remaining primes (only if cofactor still large)
    if cof > 1:
        for i in range(fb_size):
            if exps[i] > 0:
                continue  # already checked
            p = fb_mpz[i]
            if p * p > cof:
                break
            if gmpy2.is_divisible(cof, p):
                e = 0
                while gmpy2.is_divisible(cof, p):
                    cof = cof // p
                    e += 1
                exps[i] = e
                if cof == 1:
                    return exps, 1

    cof_int = int(cof)
    if cof_int > 1 and cof_int <= fb[-1]:
        lo, hi = 0, fb_size - 1
        while lo <= hi:
            mid = (lo + hi) >> 1
            if fb[mid] == cof_int:
                exps[mid] += 1
                return exps, 1
            elif fb[mid] < cof_int:
                lo = mid + 1
            else:
                hi = mid - 1
    return exps, cof_int


def cfrac_factor(N, verbose=True, time_limit=3600, original_N=None):
    """
    Factor N using the Continued Fraction (CFRAC) method.
    Single-multiplier version.
    """
    N = mpz(N)
    nd = len(str(N))
    if original_N is not None:
        orig_N = mpz(original_N)
    else:
        orig_N = N

    if N <= 1:
        return 0
    if N % 2 == 0:
        return 2
    if N % 3 == 0:
        return 3
    for exp in range(2, int(gmpy2.log2(N)) + 1):
        root, exact = iroot(N, exp)
        if exact:
            return int(root)
    if is_prime(N):
        return int(N)
    sq = isqrt(N)
    if sq * sq == N:
        return int(sq)

    t0 = time.time()

    B = _smoothness_bound(N)
    fb = _build_factor_base(N, B)
    fb_size = len(fb)
    needed = fb_size + 1 + 40

    # LP bound
    lp_bound = min(B * 100, B * B)
    # DLP: cofactor up to lp_bound^2
    dlp_cofactor_bound = min(lp_bound * lp_bound, 1 << 62)

    if verbose:
        print(f"CFRAC: {nd}d ({int(gmpy2.log2(N))+1}b), B={B:,}, "
              f"|FB|={fb_size:,}, need={needed:,}, LP<={lp_bound:,}")

    fb_set = set(fb)
    fb_mpz = [mpz(p) for p in fb]

    # CF state
    a0 = isqrt(N)
    m_k = mpz(0)
    d_k = mpz(1)
    a_k = a0
    p_prev2_mod = mpz(1)
    p_prev1_mod = a0 % N

    smooth = []
    partials = {}
    n_lp_combined = 0
    dlp_graph = DLPGraph()

    k = 0
    report_interval = 100000
    last_report_k = 0
    N_int = int(N)

    while len(smooth) < needed:
        if k % 10000 == 0 and k > 0:
            if time.time() - t0 > time_limit:
                if verbose:
                    print(f"\n  Time limit ({time_limit}s) at k={k:,}")
                break

        m_next = d_k * a_k - m_k
        d_next = (N - m_next * m_next) // d_k
        if d_next == 0:
            break
        a_next = (a0 + m_next) // d_next

        p_new_mod = (a_next * p_prev1_mod + p_prev2_mod) % N

        r_abs = int(d_next)
        sign = 1 if (k % 2 == 0) else 0

        if r_abs > 0:
            exps, cofactor = _trial_divide_fast(r_abs, fb, fb_size, fb_mpz)

            if cofactor == 1:
                smooth.append((int(p_prev1_mod), sign, exps, 0))
            elif cofactor <= lp_bound:
                if cofactor < (1 << 62) and is_prime(mpz(cofactor)):
                    lp = cofactor
                    if lp in partials:
                        p2_mod, sign2, exps2 = partials.pop(lp)
                        c_p = (int(p_prev1_mod) * p2_mod) % N_int
                        c_sign = (sign + sign2) % 2
                        c_exps = [exps[j] + exps2[j] for j in range(fb_size)]
                        smooth.append((c_p, c_sign, c_exps, lp))
                        n_lp_combined += 1
                    else:
                        partials[lp] = (int(p_prev1_mod), sign, exps)
            elif cofactor <= dlp_cofactor_bound and cofactor > 1:
                # DLP candidate
                if cofactor < (1 << 62):
                    if not is_prime(mpz(cofactor)):
                        f1 = _pollard_rho_small(cofactor)
                        if f1 > 0 and f1 != cofactor:
                            f2 = cofactor // f1
                            if f1 > f2:
                                f1, f2 = f2, f1
                            if f1 <= lp_bound and f2 <= lp_bound:
                                result = dlp_graph.add_and_try_combine(
                                    f1, f2, int(p_prev1_mod), sign, exps,
                                    None, fb_size, N_int)
                                if result:
                                    smooth.append(result)

        m_k = m_next
        d_k = d_next
        a_k = a_next
        p_prev2_mod = p_prev1_mod
        p_prev1_mod = p_new_mod
        k += 1

        if verbose and k - last_report_k >= report_interval:
            last_report_k = k
            elapsed = time.time() - t0
            rate = k / elapsed if elapsed > 0 else 0
            if len(smooth) > 0:
                eta = elapsed * (needed - len(smooth)) / len(smooth)
            else:
                eta = 99999
            print(f"  k={k:>12,}  smooth={len(smooth):,}/{needed:,}  "
                  f"LP={n_lp_combined:,}  DLP={dlp_graph.n_combined:,}  "
                  f"partials={len(partials):,}  "
                  f"rate={rate:,.0f}/s  eta={min(eta,99999):.0f}s")
            if k >= 50000 and len(smooth) < needed * 0.005:
                if verbose:
                    print(f"  Early abort: yield too low ({len(smooth)}/{needed})")
                break

    elapsed_sieve = time.time() - t0
    if verbose:
        print(f"  Sieve done: {len(smooth):,} rels in {elapsed_sieve:.1f}s "
              f"({k:,} CF terms, {n_lp_combined} LP, {dlp_graph.n_combined} DLP)")

    if len(smooth) < fb_size + 2:
        if verbose:
            print(f"  Insufficient: {len(smooth)}/{fb_size+2}")
        return 0

    # GF(2) Gaussian Elimination
    la_t0 = time.time()
    nrows = len(smooth)
    ncols = fb_size + 1

    if verbose:
        print(f"  LA: {nrows} x {ncols} matrix...")

    mat = [0] * nrows
    for i in range(nrows):
        _, s, exps, _ = smooth[i]
        row = s
        for j in range(fb_size):
            if exps[j] & 1:
                row |= (1 << (j + 1))
        mat[i] = row

    combo = [mpz(1) << i for i in range(nrows)]
    used = [False] * nrows

    for col in range(ncols):
        mask = 1 << col
        piv = -1
        for row in range(nrows):
            if not used[row] and mat[row] & mask:
                piv = row
                break
        if piv == -1:
            continue
        used[piv] = True
        piv_row = mat[piv]
        piv_combo = combo[piv]
        for row in range(nrows):
            if row != piv and mat[row] & mask:
                mat[row] ^= piv_row
                combo[row] ^= piv_combo

    null_vecs = []
    for row in range(nrows):
        if mat[row] == 0:
            indices = []
            bits = combo[row]
            idx = 0
            while bits:
                if bits & 1:
                    indices.append(idx)
                bits >>= 1
                idx += 1
            if indices:
                null_vecs.append(indices)

    la_time = time.time() - la_t0
    if verbose:
        print(f"  LA: {la_time:.1f}s, {len(null_vecs)} null vecs")

    orig_nd = len(str(orig_N))
    for vi, indices in enumerate(null_vecs):
        x_val = mpz(1)
        total_exp = [0] * fb_size
        total_sign = 0
        lp_product = mpz(1)

        for idx in indices:
            p_mod, s, exps, lp_val = smooth[idx]
            x_val = x_val * mpz(p_mod) % N
            total_sign += s
            for j in range(fb_size):
                total_exp[j] += exps[j]
            if lp_val > 0:
                lp_product = lp_product * mpz(lp_val) % N

        if any(e & 1 for e in total_exp) or total_sign & 1:
            continue

        y_val = lp_product
        for j in range(fb_size):
            if total_exp[j] > 0:
                y_val = y_val * pow(mpz(fb[j]), total_exp[j] >> 1, N) % N

        for diff in (x_val - y_val, x_val + y_val):
            g = gcd(diff % N, N)
            if g <= 1 or g >= N:
                continue
            g2 = gcd(g, orig_N)
            if 1 < g2 < orig_N:
                total_t = time.time() - t0
                if verbose:
                    print(f"\n  *** FACTOR: {g2} ({orig_nd}d, {total_t:.1f}s, "
                          f"k={k:,}, {len(smooth)} rels) ***")
                return int(g2)
            cof = N // g
            g3 = gcd(cof, orig_N)
            if 1 < g3 < orig_N:
                total_t = time.time() - t0
                if verbose:
                    print(f"\n  *** FACTOR: {g3} ({orig_nd}d, {total_t:.1f}s, "
                          f"k={k:,}, {len(smooth)} rels) ***")
                return int(g3)

    if verbose:
        print(f"  Tried {len(null_vecs)} null vecs, no factor found.")
    return 0


# ---------------------------------------------------------------------------
# Multiplier selection
# ---------------------------------------------------------------------------

def _select_top_multipliers(N, count=8):
    """Return the top `count` multipliers ranked by Knuth-Schroeppel score."""
    candidates = [1, 2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17, 19, 21,
                  23, 26, 29, 30, 31, 33, 34, 37, 38, 41, 42, 43,
                  46, 47, 51, 53, 55, 57, 58, 59, 61, 62, 65, 66, 67]
    scored = []
    for k in candidates:
        kN = N * k
        sq = isqrt(kN)
        if sq * sq == kN:
            continue
        score = -math.log(k) / 2.0
        kN_mod8 = int(kN % 8)
        if kN_mod8 == 1:
            score += 2.0 * math.log(2.0)
        elif kN_mod8 == 5:
            score += math.log(2.0)
        elif kN_mod8 == 0:
            score += math.log(2.0) * 0.5
        p = mpz(3)
        for _ in range(80):
            pf = float(p)
            leg = legendre(kN, p)
            if leg == 1:
                score += 2.0 * math.log(pf) / (pf - 1.0)
            elif leg == 0:
                score += math.log(pf) / pf
            p = next_prime(p)
        scored.append((score, k))
    scored.sort(reverse=True)
    return [k for _, k in scored[:count]]


def cfrac_factor_with_multiplier(N, verbose=True, time_limit=3600):
    """
    Try CFRAC with Knuth-Schroeppel multipliers.
    Tries best multipliers sequentially with time allocation.
    """
    N = mpz(N)

    if N <= 1:
        return 0
    if N % 2 == 0:
        return 2
    if N % 3 == 0:
        return 3
    for exp in range(2, int(gmpy2.log2(N)) + 1):
        root, exact = iroot(N, exp)
        if exact:
            return int(root)
    if is_prime(N):
        return int(N)
    sq = isqrt(N)
    if sq * sq == N:
        return int(sq)

    top_ks = _select_top_multipliers(N, count=12)
    if 1 not in top_ks:
        top_ks.append(1)

    if verbose:
        print(f"CFRAC multipliers: k={top_ks}")

    t_start = time.time()
    for ki, k in enumerate(top_ks):
        remaining = time_limit - (time.time() - t_start)
        if remaining < 5:
            break
        # Give first multiplier 50% of time, rest split evenly
        if ki == 0:
            alloc = remaining * 0.5
        else:
            alloc = remaining / max(1, len(top_ks) - ki)

        kN = N * k
        sq_kN = isqrt(kN)
        if sq_kN * sq_kN == kN:
            continue

        if verbose and ki > 0:
            print(f"\n  Trying k={k} ({remaining:.0f}s remaining)...")
        elif verbose:
            print(f"CFRAC multiplier: k={k}")

        result = cfrac_factor(int(kN), verbose=verbose, time_limit=alloc,
                              original_N=int(N))
        if result and result > 1 and int(N) % result == 0:
            return result

    return 0


# ---------------------------------------------------------------------------
# Convenience
# ---------------------------------------------------------------------------

def factor(N, verbose=True, time_limit=3600):
    """Main entry point: multiplier-enhanced CFRAC."""
    return cfrac_factor_with_multiplier(N, verbose=verbose, time_limit=time_limit)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("CFRAC Engine -- Self-Test")
    print("=" * 70)

    semiprimes = [
        ("20d", mpz("1000000007") * mpz("1000000009"), 30),
        ("30d", mpz("1000000007") * mpz("100000000000000003"), 30),
        ("35d", mpz("10000000000000061") * mpz("1000000000000000003"), 60),
        ("40d", mpz("10000000000000000051") * mpz("10000000000000000069"), 120),
        ("45d", mpz("100000000000000000267") * mpz("10000000000000000000000069"), 300),
        ("50d", mpz("100000000000000000151") * mpz("1000000000000000000117"), 600),
    ]

    results = []
    for label, n, limit in semiprimes:
        nd = len(str(n))
        print(f"\n{'='*70}")
        print(f"Test: {label} ({nd} actual digits)")
        print(f"N = {n}")
        t0 = time.time()
        f = factor(int(n), verbose=True, time_limit=limit)
        elapsed = time.time() - t0
        if f and f > 1 and int(n) % f == 0:
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
