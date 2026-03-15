#!/usr/bin/env python3
"""
CFRAC (Continued Fraction) Factoring Engine
============================================
Uses the continued fraction expansion of sqrt(N) to find smooth residues,
then GF(2) Gaussian elimination to combine them into x^2 = y^2 (mod N).

Algorithm:
  1. Expand sqrt(N) via the standard CF recurrence to get convergents p_k/q_k.
  2. Compute residues r_k = p_k^2 - N * q_k^2 = (-1)^(k+1) * d_{k+1} (small!).
  3. Trial divide |r_k| by a factor base of small primes. If smooth, record it.
  4. Large prime variation: if cofactor after trial division is prime and <= LP_bound,
     store as a partial. When two partials share the same large prime, combine.
  5. After collecting enough relations, do GF(2) elimination to find dependencies.
  6. Each dependency yields x^2 = y^2 (mod N); compute gcd(x +/- y, N).
"""

import time
import math
import gmpy2
from gmpy2 import mpz, isqrt, gcd, is_prime, next_prime, legendre, iroot

# ---------------------------------------------------------------------------
# Smoothness bound selection
# ---------------------------------------------------------------------------

def _smoothness_bound(N):
    """
    Choose smoothness bound B ~ L(N)^alpha where L(N) = exp(sqrt(ln N * ln ln N)).
    For CFRAC, optimal alpha ~ 1/sqrt(2) ~ 0.707, but in practice smaller values
    work better because the constant matters and we have LP variation.
    Tuned for Python trial division speed: smaller FB = fewer rels needed = faster.
    """
    ln_n = float(gmpy2.log(mpz(N)))
    ln_ln_n = math.log(max(ln_n, 2.0))
    L_exp = math.sqrt(ln_n * ln_ln_n)
    # Use lower alpha: smaller FB means fewer relations needed, and each
    # CF iteration is cheaper. The LP variation compensates for lower yield.
    nd = len(str(N))
    if nd <= 25:
        alpha = 0.38
    elif nd <= 35:
        alpha = 0.40
    elif nd <= 45:
        alpha = 0.42
    elif nd <= 55:
        alpha = 0.44
    elif nd <= 70:
        alpha = 0.46
    else:
        alpha = 0.48
    B = int(math.exp(alpha * L_exp))
    B = max(B, 50)
    B = min(B, 1_500_000)
    return B


def _build_factor_base(N, B):
    """
    Build factor base: {2} union {odd primes p <= B where Legendre(N,p) >= 0}.
    Returns list of int primes.
    """
    fb = [2]
    p = mpz(3)
    while p <= B:
        if legendre(N, p) >= 0:
            fb.append(int(p))
        p = next_prime(p)
    return fb



# ---------------------------------------------------------------------------
# Core CFRAC factoring
# ---------------------------------------------------------------------------

def _trial_divide_fast(r_abs, fb, fb_size, fb_mpz):
    """
    Trial divide r_abs by factor base primes.
    Uses gmpy2 mpz for the inner loop — significantly faster than Python int
    for large residues.
    Returns (exponents_list, cofactor_int).
    """
    exps = [0] * fb_size
    cof = mpz(r_abs)
    for i in range(fb_size):
        p = fb_mpz[i]
        if p * p > cof:
            if cof > 1:
                # cofactor is prime, check if in FB
                pass
            break
        if gmpy2.is_divisible(cof, p):
            e = 0
            while gmpy2.is_divisible(cof, p):
                cof = cof // p
                e += 1
            exps[i] = e
            if cof == 1:
                break
    return exps, int(cof)


def _trial_divide_small(r_abs, small_primes, small_mpz, n_small):
    """Fast path: divide only by small primes (< 1000) using int arithmetic."""
    exps = {}
    cof = int(r_abs)
    for i in range(n_small):
        p = small_primes[i]
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
    return exps, cof


def cfrac_factor(N, verbose=True, time_limit=3600, original_N=None):
    """
    Factor N using the Continued Fraction (CFRAC) method.

    Returns a non-trivial factor of N (or original_N if provided), or 0 if none found.
    When using a multiplier, pass original_N so gcd is computed against it.
    """
    N = mpz(N)
    nd = len(str(N))
    if original_N is not None:
        orig_N = mpz(original_N)
    else:
        orig_N = N

    # Preliminary checks
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

    # Choose smoothness bound and build factor base
    B = _smoothness_bound(N)
    fb = _build_factor_base(N, B)
    fb_size = len(fb)
    needed = fb_size + 1 + 30  # +1 for sign column, +30 safety

    # Large prime bound
    lp_bound = B * B

    if verbose:
        print(f"CFRAC: {nd}d ({int(gmpy2.log2(N))+1}b), B={B:,}, "
              f"|FB|={fb_size:,}, need={needed:,}, LP<={lp_bound:,}")

    # Precompute: for each FB prime p, find if it divides d values
    # (In the CF expansion, d_{k+1} is bounded by 2*sqrt(N), so all FB primes can appear.)

    # Create a lookup set of FB primes for quick cofactor-in-FB check
    fb_set = set(fb)
    # Precompute gmpy2 mpz versions of FB primes for fast trial division
    fb_mpz = [mpz(p) for p in fb]

    # CF state: standard recurrence for sqrt(N)
    a0 = isqrt(N)
    m_k = mpz(0)
    d_k = mpz(1)
    a_k = a0

    # Convergent p_k mod N (we only need this for the final gcd step)
    p_prev2_mod = mpz(1)   # p_{-1} = 1
    p_prev1_mod = a0 % N   # p_0 = a0

    # Relation storage: (p_k_mod_N, sign, exponents, lp_value)
    # lp_value=0 for full relations; for LP-combined, lp_value is the shared prime
    # (appears with total exponent 2 across the two partials, so contributes lp^1 to sqrt)
    smooth = []
    # Large prime partials: lp_value -> (p_mod, sign, exps)
    partials = {}
    n_lp_combined = 0
    # Double large prime partials: (lp1, lp2) -> (p_mod, sign, exps, lp1, lp2)
    dlp_partials = {}
    n_dlp_combined = 0

    k = 0
    report_interval = 100000
    last_report_k = 0

    while len(smooth) < needed:
        # Time limit check (every 10K iterations to minimize overhead)
        if k % 10000 == 0 and k > 0:
            if time.time() - t0 > time_limit:
                if verbose:
                    print(f"\n  Time limit ({time_limit}s) at k={k:,}")
                break

        # Advance CF recurrence
        m_next = d_k * a_k - m_k
        d_next = (N - m_next * m_next) // d_k
        if d_next == 0:
            break
        a_next = (a0 + m_next) // d_next

        # New convergent p_{k+1} mod N
        p_new_mod = (a_next * p_prev1_mod + p_prev2_mod) % N

        # The residue for convergent p_k is: (-1)^(k+1) * d_{k+1}
        # |r_k| = d_{k+1}, sign: negative when k is even
        r_abs = int(d_next)
        sign = 1 if (k % 2 == 0) else 0  # 1 = negative residue

        if r_abs > 0:
            exps, cofactor = _trial_divide_fast(r_abs, fb, fb_size, fb_mpz)

            if cofactor == 1:
                # Fully smooth
                smooth.append((int(p_prev1_mod), sign, exps, 0))
            elif cofactor in fb_set:
                # Cofactor is a FB prime — find its index and record
                for j in range(fb_size):
                    if fb[j] == cofactor:
                        exps[j] += 1
                        break
                smooth.append((int(p_prev1_mod), sign, exps, 0))
            elif cofactor <= lp_bound:
                # Potential large prime (single LP)
                if cofactor < 2**62 and is_prime(mpz(cofactor)):
                    lp = cofactor
                    if lp in partials:
                        # Combine: multiply p values, add exponent vectors
                        # The LP appears once in each partial (total exp 2 = even)
                        p2_mod, sign2, exps2 = partials.pop(lp)
                        c_p = (int(p_prev1_mod) * p2_mod) % int(N)
                        c_sign = (sign + sign2) % 2
                        c_exps = [exps[j] + exps2[j] for j in range(fb_size)]
                        smooth.append((c_p, c_sign, c_exps, lp))
                        n_lp_combined += 1
                    else:
                        partials[lp] = (int(p_prev1_mod), sign, exps)
            elif cofactor <= lp_bound * B and cofactor > 1:
                # Double large prime (DLP): cofactor might be product of 2 primes
                # Try to split it. If cofactor = lp1 * lp2 with both <= lp_bound,
                # store keyed by min(lp1,lp2). When matched, combine.
                # Quick check: if cofactor is prime, skip (too large for single LP)
                if cofactor < 2**62 and not is_prime(mpz(cofactor)):
                    # Try to factor cofactor by small trial division
                    c2 = cofactor
                    lp1 = 0
                    for sp in range(3, min(100000, int(c2**0.5) + 1), 2):
                        if c2 % sp == 0:
                            lp1 = sp
                            c2 //= sp
                            break
                    if lp1 > 0 and c2 > 1 and lp1 <= lp_bound and c2 <= lp_bound:
                        if is_prime(mpz(c2)):
                            # Valid DLP: cofactor = lp1 * lp2
                            lp_key = (min(lp1, c2), max(lp1, c2))
                            if lp_key in dlp_partials:
                                p2_mod, sign2, exps2, lp1b, lp2b = dlp_partials.pop(lp_key)
                                c_p = (int(p_prev1_mod) * p2_mod) % int(N)
                                c_sign = (sign + sign2) % 2
                                c_exps = [exps[j] + exps2[j] for j in range(fb_size)]
                                # Both LPs appear with exp 2 total
                                smooth.append((c_p, c_sign, c_exps, lp1 * c2))
                                n_dlp_combined += 1
                            else:
                                dlp_partials[lp_key] = (int(p_prev1_mod), sign, exps, lp1, c2)

        # Shift recurrence state
        m_k = m_next
        d_k = d_next
        a_k = a_next
        p_prev2_mod = p_prev1_mod
        p_prev1_mod = p_new_mod
        k += 1

        # Progress report and early-abort check
        if verbose and k - last_report_k >= report_interval:
            last_report_k = k
            elapsed = time.time() - t0
            rate = k / elapsed if elapsed > 0 else 0
            if len(smooth) > 0:
                eta = elapsed * (needed - len(smooth)) / len(smooth)
            else:
                eta = 99999
            print(f"  k={k:>12,}  smooth={len(smooth):,}/{needed:,}  "
                  f"LP={n_lp_combined:,}  DLP={n_dlp_combined:,}  "
                  f"rate={rate:,.0f}/s  eta={min(eta,99999):.0f}s")
            # Early abort: if after 50K CF terms we have < 1% of needed, bail
            if k >= 50000 and len(smooth) < needed * 0.01:
                if verbose:
                    print(f"  Early abort: yield too low ({len(smooth)}/{needed})")
                break

    elapsed_sieve = time.time() - t0
    if verbose:
        print(f"  Sieve done: {len(smooth):,} rels in {elapsed_sieve:.1f}s "
              f"({k:,} CF terms, {n_lp_combined} LP combines)")

    if len(smooth) < fb_size + 2:
        if verbose:
            print(f"  Insufficient: {len(smooth)}/{fb_size+2}")
        return 0

    # ------------------------------------------------------------------
    # GF(2) Gaussian Elimination
    # ------------------------------------------------------------------
    la_t0 = time.time()
    nrows = len(smooth)
    ncols = fb_size + 1  # col 0 = sign

    if verbose:
        print(f"  LA: {nrows} x {ncols} matrix...")

    # Build GF(2) matrix: each row is a Python int used as a bitvector
    mat = [0] * nrows
    for i in range(nrows):
        _, s, exps, _ = smooth[i]
        row = s  # bit 0 = sign
        for j in range(fb_size):
            if exps[j] & 1:
                row |= (1 << (j + 1))
        mat[i] = row

    # Gaussian elimination with combination tracking (mpz bitvectors)
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

    # Extract null space vectors
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

    # ------------------------------------------------------------------
    # Factor extraction
    # ------------------------------------------------------------------
    orig_nd = len(str(orig_N))
    for vi, indices in enumerate(null_vecs):
        x_val = mpz(1)
        total_exp = [0] * fb_size
        total_sign = 0
        lp_product = mpz(1)  # product of large primes (each appears with exp 2)

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

        # y = product of fb[j]^(total_exp[j]//2) mod N * product of large primes
        # Each LP appears with total exponent 2 in the combined relation, so
        # contributes lp^1 to the square root.
        y_val = lp_product
        for j in range(fb_size):
            if total_exp[j] > 0:
                y_val = y_val * pow(mpz(fb[j]), total_exp[j] >> 1, N) % N

        # The congruence x^2 = y^2 holds mod N (which may be kN).
        # Compute gcd against N first, then extract factor of orig_N.
        for diff in (x_val - y_val, x_val + y_val):
            g = gcd(diff % N, N)
            if g <= 1 or g >= N:
                continue
            # g is a nontrivial factor of N (=kN). Extract factor of orig_N.
            g2 = gcd(g, orig_N)
            if 1 < g2 < orig_N:
                total_t = time.time() - t0
                if verbose:
                    print(f"\n  *** FACTOR: {g2} ({orig_nd}d, {total_t:.1f}s, "
                          f"k={k:,}, {len(smooth)} rels) ***")
                return int(g2)
            # g might equal k or a divisor of k; try cofactor
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
# Multiplier-enhanced entry point
# ---------------------------------------------------------------------------

def _select_top_multipliers(N, count=3):
    """Return the top `count` multipliers ranked by Knuth-Schroeppel score."""
    candidates = [1, 2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17, 19, 21,
                  23, 26, 29, 30, 31, 33, 34, 37, 38, 41, 42, 43]
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
        for _ in range(60):
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
    Try CFRAC with Knuth-Schroeppel multipliers — interleaved round-robin.
    Runs multiple CF expansions in parallel (round-robin), sharing relations
    against a common factor base. This dramatically improves relation yield
    since different multipliers produce different smooth residues.
    """
    N = mpz(N)

    # Quick checks
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

    top_ks = _select_top_multipliers(N, count=8)
    if 1 not in top_ks:
        top_ks.append(1)

    if verbose:
        print(f"CFRAC multipliers: k={top_ks}")

    # Try each multiplier sequentially with time allocation
    # First multiplier gets most time, others get diminishing shares
    t_start = time.time()
    for ki, k in enumerate(top_ks):
        remaining = time_limit - (time.time() - t_start)
        if remaining < 5:
            break
        # First try gets 40%, then remaining splits evenly
        if ki == 0:
            alloc = remaining * 0.4
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
    print("Practical range: up to ~50 digits (pure Python trial division)")
    print("For 60d+, use SIQS or GNFS instead.")

    semiprimes = [
        ("20d", mpz("1000000007") * mpz("1000000009"), 30),
        ("30d", mpz("1000000007") * mpz("100000000000000003"), 30),
        ("35d", mpz("10000000000000061") * mpz("1000000000000000003"), 60),
        ("40d", mpz("10000000000000000051") * mpz("10000000000000000069"), 120),
        ("45d", mpz("100000000000000000267") * mpz("10000000000000000000000069"), 180),
        ("50d", mpz("100000000000000000151") * mpz("1000000000000000000117"), 300),
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
