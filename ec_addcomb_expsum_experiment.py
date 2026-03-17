#!/usr/bin/env python3
"""
Deep Research: Additive Combinatorics & Exponential Sums for ECDLP

AREA 1: Sum-Product Phenomenon (Bourgain-Katz-Tao)
  - Measure expansion |S+S|/|S| and |S*S|/|S| for S = {x(i*G)}
  - Sumset birthday attack: check if x(P) - x(i*G) in S
  - Compare to random sets

AREA 2: Exponential Sums (Weil Bounds)
  - Partial exponential sums T(a) = sum e^{2pi i x(iG) a/p}
  - Check for peaks near target scalar k
  - Fourier concentration analysis

Memory < 200MB, 30s alarm per trial.
"""

import signal
import time
import math
import random
import sys
import os

# Add parent dir
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ecdlp_pythagorean import EllipticCurve, ECPoint, FastCurve, secp256k1_curve


# ---- Timeout helper ----
class TimeoutError(Exception):
    pass

def alarm_handler(signum, frame):
    raise TimeoutError("Trial timed out")

signal.signal(signal.SIGALRM, alarm_handler)


# ---- Small curve factory ----
def make_small_curve(order_approx):
    """
    Create a small curve y^2 = x^3 + ax + b (mod p) with known generator
    and order, for testing. Uses Weierstrass form over small primes.
    """
    # Use well-known small curves for reproducibility
    small_curves = [
        # (a, b, p, Gx, Gy, order)
        (2, 3, 97, 3, 6, 100),
        (1, 6, 199, 2, 11, 197),
        (3, 7, 503, 2, 8, 499),
        (2, 3, 1009, 7, 81, 1028),
        (1, 1, 2017, 5, 9, 2014),
        (7, 2, 5003, 2, 7, 4969),
        (3, 1, 10007, 2, 3, 10016),
        (1, 3, 50021, 2, 5, 50044),
        (2, 7, 100003, 3, 10, 99982),
    ]

    # Pick the one closest to order_approx
    best = min(small_curves, key=lambda c: abs(c[5] - order_approx))
    a, b, p, gx, gy, n = best

    # Verify generator is on curve
    E = EllipticCurve(a, b, p)
    G = ECPoint(gx, gy)
    if not E.is_on_curve(G):
        # Find a valid point by trial
        for x in range(p):
            rhs = (x*x*x + a*x + b) % p
            # Euler criterion
            if pow(rhs, (p-1)//2, p) == 1:
                y = pow(rhs, (p+1)//4, p) if p % 4 == 3 else _tonelli_shanks(rhs, p)
                G = ECPoint(x, y)
                if E.is_on_curve(G):
                    gx, gy = x, y
                    break

    # Find actual order of G by brute force for small curves
    if n < 200000:
        Q = G
        actual_order = 1
        while not Q.is_infinity:
            Q = E.add(Q, G)
            actual_order += 1
            if actual_order > 2 * p:
                break
        n = actual_order

    E_with_gen = EllipticCurve(a, b, p, G=G, n=n)
    return E_with_gen


def _tonelli_shanks(n, p):
    """Square root mod p via Tonelli-Shanks."""
    if pow(n, (p-1)//2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(n, (p+1)//4, p)
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p-1)//2, p) != p-1:
        z += 1
    m = s
    c = pow(z, q, p)
    t = pow(n, q, p)
    r = pow(n, (q+1)//2, p)
    while True:
        if t == 1:
            return r
        i = 1
        tmp = (t * t) % p
        while tmp != 1:
            tmp = (tmp * tmp) % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p


def find_curve_with_generator(p):
    """Find curve y^2 = x^3 + ax + b over F_p with a generator of large order."""
    for a in range(1, 20):
        for b in range(1, 20):
            # Check discriminant
            disc = (4*a*a*a + 27*b*b) % p
            if disc == 0:
                continue
            E = EllipticCurve(a, b, p)
            # Find a point
            for x in range(p):
                rhs = (x*x*x + a*x + b) % p
                if pow(rhs, (p-1)//2, p) == 1:
                    if p % 4 == 3:
                        y = pow(rhs, (p+1)//4, p)
                    else:
                        y = _tonelli_shanks(rhs, p)
                    if y is None:
                        continue
                    G = ECPoint(x, y)
                    if not E.is_on_curve(G):
                        continue
                    # Find order
                    Q = G
                    order = 1
                    while not Q.is_infinity:
                        Q = E.add(Q, G)
                        order += 1
                        if order > 2*p:
                            break
                    if order > p // 2:  # want large-order generator
                        return EllipticCurve(a, b, p, G=G, n=order)
    return None


# =====================================================================
# AREA 1: Sum-Product Expansion Measurement
# =====================================================================

def measure_sum_product(E, M=None):
    """
    For S = {x(i*G) : i=1..M}, compute:
      - |S+S|/|S|  (additive expansion)
      - |S*S|/|S|  (multiplicative expansion)
      - Compare to random subset of F_p of same size
    """
    p = E.p
    G = E.G
    n = E.n

    if M is None:
        M = min(n - 1, 500)  # cap for speed

    # Generate x-coordinates
    S = set()
    x_list = []
    Q = G
    for i in range(1, M + 1):
        if Q.is_infinity:
            break
        x = Q.x
        S.add(x)
        x_list.append(x)
        Q = E.add(Q, G)

    S_size = len(S)
    if S_size < 5:
        return None

    # Compute S+S and S*S
    sum_set = set()
    prod_set = set()
    for x1 in S:
        for x2 in S:
            sum_set.add((x1 + x2) % p)
            if x2 != 0:
                prod_set.add((x1 * x2) % p)

    ss_ratio = len(sum_set) / S_size
    pp_ratio = len(prod_set) / S_size

    # Compare to random set of same size
    R = set(random.sample(range(1, p), min(S_size, p - 1)))
    R_list = list(R)
    rsum = set()
    rprod = set()
    for x1 in R_list:
        for x2 in R_list:
            rsum.add((x1 + x2) % p)
            if x2 != 0:
                rprod.add((x1 * x2) % p)

    rs_ratio = len(rsum) / len(R)
    rp_ratio = len(rprod) / len(R)

    return {
        'S_size': S_size,
        'sum_set_size': len(sum_set),
        'prod_set_size': len(prod_set),
        'SS_ratio': ss_ratio,
        'PP_ratio': pp_ratio,
        'random_SS_ratio': rs_ratio,
        'random_PP_ratio': rp_ratio,
        'p': p,
        'order': n,
    }


# =====================================================================
# AREA 1b: Sumset Birthday Attack
# =====================================================================

def sumset_birthday_attack(E, k_target, M=None):
    """
    Sumset birthday attack:
    1. Store S = {x(i*G) : i=1..M} in a dict mapping x -> i
    2. For each i in 1..M, check if x(P) - x(i*G) mod p is in S
    3. If found, we have x(i*G) + x(j*G) = x(P) — this gives a CANDIDATE relation

    NOTE: x(i*G) + x(j*G) = x(P) does NOT directly give k = i+j in general,
    because x-coord addition != point addition. But it's a structural relation
    worth investigating.

    Returns (found, ops_count, details)
    """
    p = E.p
    G = E.G
    n = E.n
    P = E.scalar_mult(k_target, G)

    if M is None:
        M = min(int(math.isqrt(n)) * 2, 50000)

    xP = P.x

    # Build table: x(i*G) -> i
    x_to_i = {}
    Q = G
    for i in range(1, M + 1):
        if Q.is_infinity:
            Q = E.add(Q, G)
            continue
        x_to_i[Q.x] = i
        Q = E.add(Q, G)

    # Check if xP - x(iG) is in the table (additive relation)
    add_hits = []
    for xi, i_val in list(x_to_i.items()):
        target = (xP - xi) % p
        if target in x_to_i:
            j_val = x_to_i[target]
            add_hits.append((i_val, j_val, 'sum'))

        # Also check product: xP / x(iG) mod p
        if xi != 0:
            target_m = (xP * pow(xi, p - 2, p)) % p
            if target_m in x_to_i:
                j_val = x_to_i[target_m]
                add_hits.append((i_val, j_val, 'prod'))

    # Check: do any (i,j) pairs actually give k?
    true_hits = []
    for (i_val, j_val, rel_type) in add_hits:
        # Check various relationships
        for candidate_k in [i_val + j_val, abs(i_val - j_val),
                           (i_val * j_val) % n, i_val ^ j_val]:
            if candidate_k == k_target:
                true_hits.append((i_val, j_val, rel_type, candidate_k))

    return {
        'M': M,
        'table_size': len(x_to_i),
        'xcoord_hits': len(add_hits),
        'true_hits': true_hits,
        'k_target': k_target,
        'found_k': len(true_hits) > 0,
        'sample_hits': add_hits[:10],  # first few for inspection
    }


# =====================================================================
# AREA 1c: Enhanced Birthday via x-coord structure
# =====================================================================

def xcoord_structure_analysis(E, M=None):
    """
    Analyze the algebraic structure of x-coordinates:
    - For P1 + P2 = P3 on the curve, what's the relation between x1, x2, x3?
    - x3 = lambda^2 - x1 - x2 where lambda = (y2-y1)/(x2-x1)
    - So x3 + x1 + x2 = lambda^2
    - This means: x1 + x2 + x3 = ((y2-y1)/(x2-x1))^2
    - The SUM of x-coords of P1, P2, P1+P2 equals a perfect square in F_p!

    Measure: how often does x(iG) + x(jG) + x((i+j)G) = perfect square mod p?
    (Answer: ALWAYS, by the addition formula — but this algebraic constraint
     might be exploitable.)
    """
    p = E.p
    G = E.G
    n = E.n

    if M is None:
        M = min(n - 1, 200)

    # Precompute points
    points = {}
    Q = G
    for i in range(1, M + 1):
        if not Q.is_infinity:
            points[i] = Q
        Q = E.add(Q, G)

    # Verify the x-sum = square relation
    verified = 0
    total = 0
    quadratic_residues = 0

    sample_size = min(500, M * (M - 1) // 2)
    pairs = []
    for i in range(1, M + 1):
        for j in range(i + 1, M + 1):
            if i + j < M and i in points and j in points and (i + j) in points:
                pairs.append((i, j))
                if len(pairs) >= sample_size:
                    break
        if len(pairs) >= sample_size:
            break

    for (i, j) in pairs:
        Pi = points[i]
        Pj = points[j]
        Pij = points[i + j]
        total += 1

        x_sum = (Pi.x + Pj.x + Pij.x) % p
        # Check if x_sum is a quadratic residue
        if pow(x_sum, (p - 1) // 2, p) == 1:
            quadratic_residues += 1

        # Verify it equals lambda^2
        if Pi.x != Pj.x:
            dy = (Pj.y - Pi.y) % p
            dx = (Pj.x - Pi.x) % p
            dx_inv = pow(dx, p - 2, p)
            lam = dy * dx_inv % p
            lam_sq = lam * lam % p
            if lam_sq == x_sum:
                verified += 1

    return {
        'total_pairs': total,
        'lambda_sq_verified': verified,
        'qr_count': quadratic_residues,
        'qr_fraction': quadratic_residues / total if total > 0 else 0,
        'verified_fraction': verified / total if total > 0 else 0,
    }


# =====================================================================
# AREA 2: Exponential Sum Analysis
# =====================================================================

def exponential_sum_analysis(E, k_target, num_freqs=50, M=None):
    """
    Compute partial exponential sums:
      T(a) = sum_{i=0}^{M-1} exp(2*pi*i * x(i*G) * a / p)

    For various 'frequencies' a, measure |T(a)|.
    Check if certain a values show peaks that correlate with k.

    Theory: Weil bound says |T(a)| <= 2*sqrt(p) for complete sums.
    For partial sums over M < n terms, we expect |T(a)| ~ sqrt(M)
    (random walk). Deviations indicate structure.
    """
    import cmath

    p = E.p
    G = E.G
    n = E.n

    if M is None:
        M = min(int(math.isqrt(n)) * 2, 10000)

    # Generate x-coordinates
    x_coords = []
    Q = G
    for i in range(1, M + 1):
        if Q.is_infinity:
            x_coords.append(0)
        else:
            x_coords.append(Q.x)
        Q = E.add(Q, G)

    # Compute T(a) for various frequencies
    results = []
    sqrt_M = math.sqrt(M)
    two_pi = 2 * math.pi

    # Test specific frequencies related to k_target
    test_freqs = list(range(1, num_freqs + 1))
    # Add frequencies related to k_target
    if k_target < p:
        test_freqs.append(k_target)
        if k_target > 1:
            test_freqs.append(pow(k_target, p - 2, p) % p)  # k^{-1} mod p

    for a in test_freqs:
        if a >= p:
            continue
        # Compute T(a) = sum exp(2*pi*i * x_j * a / p)
        total = complex(0, 0)
        for x in x_coords:
            phase = two_pi * ((x * a) % p) / p
            total += cmath.exp(1j * phase)

        magnitude = abs(total)
        normalized = magnitude / sqrt_M  # normalized by sqrt(M); expect ~1 for random

        results.append({
            'a': a,
            'magnitude': magnitude,
            'normalized': normalized,
            'is_k_related': (a == k_target or (k_target > 1 and a == pow(k_target, p - 2, p) % p)),
        })

    # Sort by magnitude
    results.sort(key=lambda r: -r['magnitude'])

    # Statistics
    magnitudes = [r['normalized'] for r in results]
    mean_norm = sum(magnitudes) / len(magnitudes)
    max_norm = max(magnitudes)
    k_related = [r for r in results if r['is_k_related']]
    k_rank = None
    for idx, r in enumerate(results):
        if r['is_k_related']:
            k_rank = idx + 1
            break

    return {
        'M': M,
        'num_freqs': len(results),
        'mean_normalized': mean_norm,
        'max_normalized': max_norm,
        'sqrt_M': sqrt_M,
        'weil_bound': 2 * math.sqrt(p),
        'k_related_results': k_related,
        'k_rank_in_magnitudes': k_rank,
        'top_5': results[:5],
        'k_target': k_target,
    }


# =====================================================================
# AREA 2b: Fourier Concentration / Peak Detection
# =====================================================================

def fourier_peak_detection(E, k_target, M=None):
    """
    More targeted: compute the "inner product" of the walk with a test signal.

    For each candidate k', compute:
      C(k') = sum_{i=1}^{M} delta(x(i*G), x(k'*G))

    This is just checking if x(k'*G) appears among {x(i*G): i=1..M}.
    That's the trivial BSGS. Instead, look at APPROXIMATE matches:

      C(k') = sum_{i=1}^{M} cos(2*pi * (x(i*G) - x(k'*G)) / p)

    Peak at C(k') when i*G is near k'*G (in x-coordinate).
    Scan k' in a range around estimated k to see if C(k') peaks at k.
    """
    import cmath

    p = E.p
    G = E.G
    n = E.n
    P = E.scalar_mult(k_target, G)

    if M is None:
        M = min(int(math.isqrt(n)), 5000)

    # Generate x-coordinates of walk
    x_walk = []
    Q = G
    for i in range(1, M + 1):
        if not Q.is_infinity:
            x_walk.append(Q.x)
        else:
            x_walk.append(0)
        Q = E.add(Q, G)

    two_pi = 2 * math.pi
    xP = P.x

    # Compute C(k') for k' near k_target
    window = min(50, n // 10)
    k_start = max(1, k_target - window)
    k_end = min(n - 1, k_target + window)

    correlations = []
    for k_prime in range(k_start, k_end + 1):
        Pk = E.scalar_mult(k_prime, G)
        if Pk.is_infinity:
            continue
        xk = Pk.x
        # Correlation
        c_val = sum(math.cos(two_pi * ((x - xk) % p) / p) for x in x_walk)
        correlations.append((k_prime, c_val))

    if not correlations:
        return {'error': 'no correlations computed'}

    # Find peak
    correlations.sort(key=lambda x: -x[1])
    peak_k = correlations[0][0]

    # Find rank of true k
    k_rank = None
    k_corr = None
    for idx, (k, c) in enumerate(correlations):
        if k == k_target:
            k_rank = idx + 1
            k_corr = c
            break

    return {
        'M': M,
        'window_size': k_end - k_start + 1,
        'peak_k': peak_k,
        'peak_corr': correlations[0][1],
        'k_target': k_target,
        'k_rank': k_rank,
        'k_corr': k_corr,
        'found_at_peak': peak_k == k_target,
        'top_5': correlations[:5],
        'mean_corr': sum(c for _, c in correlations) / len(correlations),
    }


# =====================================================================
# AREA 2c: Gauss Sum Structure
# =====================================================================

def gauss_sum_structure(E, M=None):
    """
    Compute character sums over the EC group:
      S(a) = sum_{i=1}^{M} legendre(x(i*G), p) * exp(2*pi*i * i*a / n)

    This mixes the Legendre symbol (quadratic character of x-coords)
    with the group structure. By Weil bounds, complete sums satisfy
    |S| <= 2*sqrt(p), but partial sums might show structure.

    Measure: distribution of |S(a)| for a = 1..A
    """
    import cmath

    p = E.p
    G = E.G
    n = E.n

    if M is None:
        M = min(n - 1, 2000)

    # Generate x-coords and their Legendre symbols
    legendres = []
    Q = G
    for i in range(1, M + 1):
        if Q.is_infinity:
            legendres.append(0)
        else:
            leg = pow(Q.x, (p - 1) // 2, p)
            if leg == p - 1:
                leg = -1
            legendres.append(leg)
        Q = E.add(Q, G)

    # Compute character sums
    two_pi = 2 * math.pi
    A = min(100, n - 1)
    sums = []

    for a in range(1, A + 1):
        total = complex(0, 0)
        for i, leg in enumerate(legendres):
            phase = two_pi * ((i + 1) * a) / n
            total += leg * cmath.exp(1j * phase)
        mag = abs(total)
        sums.append((a, mag))

    magnitudes = [s[1] for s in sums]
    mean_mag = sum(magnitudes) / len(magnitudes)
    max_mag = max(magnitudes)
    sqrt_M = math.sqrt(M)

    return {
        'M': M,
        'num_sums': len(sums),
        'mean_magnitude': mean_mag,
        'max_magnitude': max_mag,
        'sqrt_M': sqrt_M,
        'weil_bound_2sqrtp': 2 * math.sqrt(p),
        'ratio_mean_to_sqrtM': mean_mag / sqrt_M,
        'ratio_max_to_sqrtM': max_mag / sqrt_M,
        'top_5': sorted(sums, key=lambda x: -x[1])[:5],
    }


# =====================================================================
# Main experiment driver
# =====================================================================

def run_experiments():
    print("=" * 70)
    print("DEEP RESEARCH: Additive Combinatorics & Exponential Sums for ECDLP")
    print("=" * 70)

    # Test on curves of increasing size
    test_primes = [101, 503, 1009, 5003, 10007, 50021]

    # ---- EXPERIMENT 1: Sum-Product Expansion ----
    print("\n" + "=" * 70)
    print("EXPERIMENT 1: Sum-Product Expansion (Bourgain-Katz-Tao)")
    print("=" * 70)
    print(f"{'p':>8} {'|S|':>6} {'|S+S|/|S|':>10} {'|S*S|/|S|':>10} "
          f"{'rand S+S':>10} {'rand S*S':>10} {'sum adv':>8} {'prod adv':>8}")
    print("-" * 80)

    for p in test_primes:
        signal.alarm(30)
        try:
            E = find_curve_with_generator(p)
            if E is None:
                print(f"{p:>8} -- no curve found")
                continue
            M = min(E.n - 1, min(300, int(math.sqrt(p))))
            result = measure_sum_product(E, M=M)
            if result is None:
                continue
            adv_s = result['SS_ratio'] / result['random_SS_ratio'] if result['random_SS_ratio'] > 0 else 0
            adv_p = result['PP_ratio'] / result['random_PP_ratio'] if result['random_PP_ratio'] > 0 else 0
            print(f"{p:>8} {result['S_size']:>6} {result['SS_ratio']:>10.2f} "
                  f"{result['PP_ratio']:>10.2f} {result['random_SS_ratio']:>10.2f} "
                  f"{result['random_PP_ratio']:>10.2f} {adv_s:>8.3f} {adv_p:>8.3f}")
        except TimeoutError:
            print(f"{p:>8} -- TIMEOUT")
        except Exception as e:
            print(f"{p:>8} -- ERROR: {e}")
        finally:
            signal.alarm(0)

    # ---- EXPERIMENT 2: x-coord Structure (lambda^2 verification) ----
    print("\n" + "=" * 70)
    print("EXPERIMENT 2: x-Coordinate Algebraic Structure")
    print("  x(P1) + x(P2) + x(P1+P2) = lambda^2 mod p")
    print("=" * 70)
    print(f"{'p':>8} {'pairs':>8} {'verified':>10} {'QR frac':>10}")
    print("-" * 50)

    for p in test_primes[:4]:  # smaller curves only
        signal.alarm(30)
        try:
            E = find_curve_with_generator(p)
            if E is None:
                continue
            result = xcoord_structure_analysis(E, M=min(100, E.n - 1))
            print(f"{p:>8} {result['total_pairs']:>8} "
                  f"{result['verified_fraction']:>10.4f} {result['qr_fraction']:>10.4f}")
        except TimeoutError:
            print(f"{p:>8} -- TIMEOUT")
        except Exception as e:
            print(f"{p:>8} -- ERROR: {e}")
        finally:
            signal.alarm(0)

    # ---- EXPERIMENT 3: Sumset Birthday Attack ----
    print("\n" + "=" * 70)
    print("EXPERIMENT 3: Sumset Birthday Attack")
    print("  Store S={x(iG)}, check if x(P)-x(iG) in S")
    print("=" * 70)
    print(f"{'p':>8} {'k':>8} {'M':>6} {'x-hits':>8} {'true hits':>10} {'found k':>8}")
    print("-" * 60)

    for p in test_primes:
        signal.alarm(30)
        try:
            E = find_curve_with_generator(p)
            if E is None:
                continue
            # Random secret k
            k = random.randint(2, E.n - 2)
            M = min(int(math.isqrt(E.n)) * 2, 5000)
            result = sumset_birthday_attack(E, k, M=M)
            print(f"{p:>8} {k:>8} {result['M']:>6} {result['xcoord_hits']:>8} "
                  f"{len(result['true_hits']):>10} {'YES' if result['found_k'] else 'no':>8}")
            if result['true_hits']:
                for hit in result['true_hits'][:3]:
                    print(f"         -> i={hit[0]}, j={hit[1]}, type={hit[2]}, k_cand={hit[3]}")
        except TimeoutError:
            print(f"{p:>8} -- TIMEOUT")
        except Exception as e:
            print(f"{p:>8} -- ERROR: {e}")
        finally:
            signal.alarm(0)

    # ---- EXPERIMENT 4: Exponential Sums ----
    print("\n" + "=" * 70)
    print("EXPERIMENT 4: Exponential Sum Analysis")
    print("  T(a) = sum exp(2*pi*i * x(jG)*a/p), check for peaks")
    print("=" * 70)
    print(f"{'p':>8} {'M':>6} {'mean |T|/sqrtM':>15} {'max |T|/sqrtM':>15} "
          f"{'k-rank':>8} {'k-norm':>10}")
    print("-" * 70)

    for p in test_primes:
        signal.alarm(30)
        try:
            E = find_curve_with_generator(p)
            if E is None:
                continue
            k = random.randint(2, E.n - 2)
            M = min(int(math.isqrt(E.n)) * 2, 3000)
            result = exponential_sum_analysis(E, k, num_freqs=80, M=M)
            k_norm = '--'
            k_rank = '--'
            if result['k_related_results']:
                k_norm = f"{result['k_related_results'][0]['normalized']:.3f}"
            if result['k_rank_in_magnitudes'] is not None:
                k_rank = str(result['k_rank_in_magnitudes'])
            print(f"{p:>8} {result['M']:>6} {result['mean_normalized']:>15.3f} "
                  f"{result['max_normalized']:>15.3f} {k_rank:>8} {k_norm:>10}")
        except TimeoutError:
            print(f"{p:>8} -- TIMEOUT")
        except Exception as e:
            print(f"{p:>8} -- ERROR: {e}")
        finally:
            signal.alarm(0)

    # ---- EXPERIMENT 5: Fourier Peak Detection ----
    print("\n" + "=" * 70)
    print("EXPERIMENT 5: Fourier Peak Detection (Correlation near k)")
    print("  C(k') = sum cos(2pi*(x(iG)-x(k'G))/p), window around k")
    print("=" * 70)
    print(f"{'p':>8} {'k':>8} {'M':>6} {'peak_k':>8} {'found':>6} {'k_rank':>8} {'mean_C':>10}")
    print("-" * 65)

    for p in test_primes[:4]:  # expensive, do fewer
        signal.alarm(30)
        try:
            E = find_curve_with_generator(p)
            if E is None:
                continue
            k = random.randint(max(2, E.n // 4), min(E.n - 2, 3 * E.n // 4))
            result = fourier_peak_detection(E, k, M=min(200, int(math.isqrt(E.n))))
            if 'error' in result:
                print(f"{p:>8} -- {result['error']}")
                continue
            print(f"{p:>8} {k:>8} {result['M']:>6} {result['peak_k']:>8} "
                  f"{'YES' if result['found_at_peak'] else 'no':>6} "
                  f"{result['k_rank'] if result['k_rank'] else '--':>8} "
                  f"{result['mean_corr']:>10.3f}")
        except TimeoutError:
            print(f"{p:>8} -- TIMEOUT")
        except Exception as e:
            print(f"{p:>8} -- ERROR: {e}")
        finally:
            signal.alarm(0)

    # ---- EXPERIMENT 6: Gauss Sum Structure ----
    print("\n" + "=" * 70)
    print("EXPERIMENT 6: Gauss Sum / Character Sum Structure")
    print("  S(a) = sum legendre(x(iG)) * exp(2pi*i*ia/n)")
    print("=" * 70)
    print(f"{'p':>8} {'M':>6} {'mean|S|':>10} {'max|S|':>10} {'sqrtM':>8} "
          f"{'mean/sqrtM':>12} {'max/sqrtM':>12}")
    print("-" * 75)

    for p in test_primes:
        signal.alarm(30)
        try:
            E = find_curve_with_generator(p)
            if E is None:
                continue
            M = min(E.n - 1, 1500)
            result = gauss_sum_structure(E, M=M)
            print(f"{p:>8} {result['M']:>6} {result['mean_magnitude']:>10.2f} "
                  f"{result['max_magnitude']:>10.2f} {result['sqrt_M']:>8.2f} "
                  f"{result['ratio_mean_to_sqrtM']:>12.4f} "
                  f"{result['ratio_max_to_sqrtM']:>12.4f}")
        except TimeoutError:
            print(f"{p:>8} -- TIMEOUT")
        except Exception as e:
            print(f"{p:>8} -- ERROR: {e}")
        finally:
            signal.alarm(0)

    # ---- EXPERIMENT 7: Larger curve test (2^20 range) ----
    print("\n" + "=" * 70)
    print("EXPERIMENT 7: Larger Curve (~2^20 order)")
    print("=" * 70)

    signal.alarm(30)
    try:
        # Use a prime near 2^20
        big_p = 1048583  # prime near 2^20
        E = find_curve_with_generator(big_p)
        if E is None:
            print("Could not find curve with large-order generator")
        else:
            print(f"Curve: y^2 = x^3 + {E.a}x + {E.b} over F_{E.p}, order={E.n}")
            k = random.randint(2, E.n - 2)
            P = E.scalar_mult(k, E.G)

            # Sum-product (small M due to O(M^2) for S+S)
            M_sp = min(500, int(math.isqrt(E.n)))
            print(f"\n  Sum-product expansion (M={M_sp}):")
            sp = measure_sum_product(E, M=M_sp)
            if sp:
                print(f"    |S|={sp['S_size']}, |S+S|/|S|={sp['SS_ratio']:.2f}, "
                      f"|S*S|/|S|={sp['PP_ratio']:.2f}")
                print(f"    Random: |S+S|/|S|={sp['random_SS_ratio']:.2f}, "
                      f"|S*S|/|S|={sp['random_PP_ratio']:.2f}")

            # Sumset birthday
            M_sb = min(2000, int(math.isqrt(E.n)) * 2)
            print(f"\n  Sumset birthday (M={M_sb}, k={k}):")
            sb = sumset_birthday_attack(E, k, M=M_sb)
            print(f"    x-coord hits: {sb['xcoord_hits']}, true hits: {len(sb['true_hits'])}")
            if sb['true_hits']:
                print(f"    FOUND k! Hits: {sb['true_hits'][:3]}")

            # Exponential sums
            M_es = min(2000, int(math.isqrt(E.n)) * 2)
            print(f"\n  Exponential sums (M={M_es}):")
            es = exponential_sum_analysis(E, k, num_freqs=100, M=M_es)
            print(f"    Mean |T|/sqrt(M)={es['mean_normalized']:.3f}, "
                  f"max |T|/sqrt(M)={es['max_normalized']:.3f}")
            if es['k_rank_in_magnitudes']:
                print(f"    k-related freq rank: {es['k_rank_in_magnitudes']}/{es['num_freqs']}")

    except TimeoutError:
        print("  TIMEOUT on large curve")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        signal.alarm(0)

    # ---- Summary ----
    print("\n" + "=" * 70)
    print("SUMMARY & CONCLUSIONS")
    print("=" * 70)
    print("""
AREA 1 (Sum-Product / Additive Combinatorics):
  - The Bourgain-Katz-Tao theorem guarantees expansion in EITHER sum or
    product sets. For EC x-coordinates, we measure whether the expansion
    differs from random sets of the same size.
  - If EC x-coords show LESS expansion than random -> they have hidden
    structure that might be exploitable.
  - If they show SAME expansion -> no advantage over random birthday attack.
  - The sumset birthday attack x(P)-x(iG) in S tests if additive structure
    in x-coordinates creates exploitable collisions beyond birthday bound.

AREA 2 (Exponential Sums):
  - Weil bound limits complete character sums to O(sqrt(p)).
  - For partial sums over M terms, random walk gives |T| ~ sqrt(M).
  - If k-related frequencies show ABOVE-AVERAGE magnitude, there's
    exploitable Fourier concentration.
  - If they're indistinguishable from average -> no spectral shortcut.

KEY QUESTION: Do x-coordinates of {iG} behave like random elements of F_p,
or does the group structure create exploitable correlations?
""")


if __name__ == '__main__':
    run_experiments()
