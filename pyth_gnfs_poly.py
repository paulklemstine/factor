#!/usr/bin/env python3
"""
Pythagorean B2 polynomial for GNFS: feasibility experiment
===========================================================
Hypothesis: f(x) = x^2 - 2x - 1 (char poly of B2 matrix, root 1+sqrt(2))
might give smaller algebraic norms than standard base-m polynomials.

For f(x)=x^2-2x-1 to work in GNFS on N, we need m with f(m)≡0 (mod N),
i.e. m^2-2m-1≡0 (mod N), so m = 1 + sqrt(2) mod N (requires Jacobi(N+2,N)=1
and ability to compute sqrt mod composite — which requires factoring N!).

We test on semiprimes where we know the factors, compute m via CRT.
"""

import gmpy2
from gmpy2 import mpz, isqrt, gcd, is_prime, next_prime, iroot, jacobi
import math
import time
import random

# Import standard GNFS poly selection for comparison
from gnfs_engine import base_m_poly

def tonelli_shanks(n, p):
    """Square root of n mod prime p, or None."""
    n = n % p
    if n == 0:
        return 0
    if gmpy2.legendre(n, p) != 1:
        return None
    if p % 4 == 3:
        return int(pow(mpz(n), (p + 1) // 4, p))
    # Factor out powers of 2 from p-1
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while gmpy2.legendre(z, p) != -1:
        z += 1
    M, c, t, R = s, pow(mpz(z), q, p), pow(mpz(n), q, p), pow(mpz(n), (q + 1) // 2, p)
    while True:
        if t == 1:
            return int(R)
        i = 1
        tmp = (t * t) % p
        while tmp != 1:
            tmp = (tmp * tmp) % p
            i += 1
        b = pow(c, 1 << (M - i - 1), p)
        M, c, t, R = i, (b * b) % p, (t * b * b) % p, (R * b) % p

def find_m_for_b2_poly(N, p, q):
    """Find m such that m^2 - 2m - 1 ≡ 0 (mod N) using known factors p, q.
    Requires sqrt(2) mod p and mod q, then CRT."""
    # Need sqrt(2) mod p and mod q
    sp = tonelli_shanks(2, p)
    sq = tonelli_shanks(2, q)
    if sp is None or sq is None:
        return None  # 2 is not QR mod one of the factors
    # m = 1 + sqrt(2) mod p, mod q; combine via CRT
    # There are 4 solutions (±sqrt mod p, ±sqrt mod q)
    results = []
    for spp in [sp, p - sp]:
        for sqq in [sq, q - sq]:
            mp = (1 + spp) % p
            mq = (1 + sqq) % q
            # CRT: m = mp + p * ((mq - mp) * p^{-1} mod q)
            p_inv = int(gmpy2.invert(mpz(p), mpz(q)))
            m = int(mp + p * (((mq - mp) * p_inv) % q))
            if m < 0:
                m += int(N)
            results.append(m)
    return results

def alg_norm_b2(a, b):
    """Algebraic norm for f(x)=x^2-2x-1: Norm(a-b*alpha) = a^2 - 2ab - b^2."""
    return abs(a * a - 2 * a * b - b * b)

def alg_norm_standard(a, b, coeffs, d):
    """Algebraic norm for standard poly: |sum c_i * a^i * b^(d-i)|."""
    val = sum(coeffs[i] * a**i * b**(d - i) for i in range(d + 1))
    return abs(val)

def rat_norm(a, b, m):
    """Rational norm: |a - b*m|."""
    return abs(a - b * m)

def measure_norms(label, coeffs, d, m, N, sieve_A=50000, n_samples=2000):
    """Measure average log-norm at random sieve points."""
    rng = random.Random(42)
    log_alg_sum = 0.0
    log_rat_sum = 0.0
    count = 0
    for _ in range(n_samples):
        a = rng.randint(-sieve_A, sieve_A)
        b = rng.randint(1, sieve_A)
        if gcd(a, b) != 1:
            continue
        if d == 2:
            an = alg_norm_b2(a, b)
        else:
            an = alg_norm_standard(a, b, coeffs, d)
        rn = rat_norm(a, b, m)
        if an > 0 and rn > 0:
            log_alg_sum += math.log10(an)
            log_rat_sum += math.log10(rn)
            count += 1
    if count == 0:
        return None
    return {
        'label': label,
        'avg_log10_alg_norm': log_alg_sum / count,
        'avg_log10_rat_norm': log_rat_sum / count,
        'avg_log10_combined': (log_alg_sum + log_rat_sum) / count,
        'samples': count,
    }

def generate_semiprime(nd):
    """Generate a semiprime of roughly nd digits with balanced factors."""
    half = nd // 2
    lo = mpz(10) ** (half - 1)
    hi = mpz(10) ** half
    while True:
        p = gmpy2.next_prime(lo + mpz(random.randint(0, int(hi - lo))))
        q = gmpy2.next_prime(lo + mpz(random.randint(0, int(hi - lo))))
        if p != q:
            N = p * q
            if len(str(int(N))) >= nd - 1:
                return int(N), int(p), int(q)

def run_experiment():
    print("=" * 72)
    print("Pythagorean B2 Polynomial for GNFS: Norm Comparison Experiment")
    print("=" * 72)
    print()
    print("B2 poly: f(x) = x^2 - 2x - 1, root alpha = 1+sqrt(2)")
    print("Algebraic norm: |a^2 - 2ab - b^2|  (discriminant 8)")
    print()

    random.seed(2026)

    for nd in [30, 40, 50, 60, 80]:
        print(f"--- {nd}-digit semiprime ---")
        # Try up to 10 semiprimes to find one where B2 poly works
        found = False
        for attempt in range(20):
            N, p, q = generate_semiprime(nd)
            ms = find_m_for_b2_poly(N, p, q)
            if ms is not None:
                found = True
                break
        if not found:
            print(f"  Could not find semiprime where 2 is QR mod both factors.\n")
            continue

        # Pick the m that gives smallest rational norm
        best_m = min(ms, key=lambda m: abs(m - int(isqrt(mpz(N)))))

        # B2 polynomial measurement
        b2_coeffs = [-1, -2, 1]  # -1 - 2x + x^2
        res_b2 = measure_norms("B2 (x^2-2x-1)", b2_coeffs, 2, best_m, N)

        # Standard GNFS polynomial
        std = base_m_poly(N)
        if 'factor' in std:
            print(f"  Trivially factored!\n")
            continue
        res_std = measure_norms(
            f"Standard d={std['d']}", std['f_coeffs'], std['d'], std['m'], N
        )

        print(f"  N = {str(N)[:30]}...  ({len(str(N))}d)")
        print(f"  B2 poly m = {best_m} (mod N root of x^2-2x-1)")
        print(f"  Std poly m = {std['m']}, degree {std['d']}")
        print()
        if res_b2:
            print(f"  {'Metric':<28} {'B2 (deg 2)':>14} {'Std (deg '+str(std['d'])+')':>14} {'Winner':>10}")
            print(f"  {'-'*28} {'-'*14} {'-'*14} {'-'*10}")
            for key, label in [
                ('avg_log10_alg_norm', 'Avg log10(alg norm)'),
                ('avg_log10_rat_norm', 'Avg log10(rat norm)'),
                ('avg_log10_combined', 'Avg log10(combined)'),
            ]:
                v_b2 = res_b2[key]
                v_std = res_std[key]
                winner = "B2" if v_b2 < v_std else "Standard"
                print(f"  {label:<28} {v_b2:>14.2f} {v_std:>14.2f} {winner:>10}")
        print()

        # Key insight: for degree-2 B2, rational m is huge (~N), so |a - bm| is huge
        print(f"  ** Rational m for B2: ~{math.log10(best_m):.1f} digits")
        print(f"  ** Rational m for std: ~{math.log10(std['m']):.1f} digits")
        print(f"  ** B2 alg norm is O(A^2), std alg norm is O(A^{std['d']}*coeff)")
        print()

    print("=" * 72)
    print("ANALYSIS")
    print("=" * 72)
    print("""
The B2 polynomial f(x)=x^2-2x-1 has a FUNDAMENTAL problem for GNFS:

1. DEGREE TOO LOW: For an N of nd digits, degree-2 means m ~ N^(1/2),
   so the rational norm |a - b*m| ~ b * N^(1/2) is ENORMOUS.
   Standard GNFS uses degree d=5 giving m ~ N^(1/5), much smaller.

2. THE TRADEOFF: B2's algebraic norm |a^2 - 2ab - b^2| is tiny (just
   depends on sieve coords, ~A^2), but the rational norm kills it.
   Combined norm = alg * rat determines smoothness probability.

3. COMBINED NORM: B2 combined ~ A^2 * b*N^(1/2) vs Standard ~ A^d * coeff * b*N^(1/d)
   For N=10^80, d=5: std combined ~ A^5 * A * 10^16 = A^6 * 10^16
                      B2 combined  ~ A^2 * A * 10^40 = A^3 * 10^40
   At A=50000: B2 = 10^(3*4.7+40) = 10^54, Std = 10^(6*4.7+16) = 10^44
   Standard wins by 10 orders of magnitude!

4. SQUARE ROOT REQUIREMENT: Finding m requires sqrt(2) mod N, which
   requires knowing the factorization — a chicken-and-egg problem.
   (We cheated by using known p, q in this experiment.)

CONCLUSION: The B2 polynomial is NOT viable for GNFS. The degree-2
constraint forces m ~ sqrt(N), making rational norms far too large.
The small algebraic norms cannot compensate. Standard degree-5 polys
win decisively for 80d+ numbers.

HOWEVER: The Pythagorean structure might help in OTHER ways:
- Pre-factored algebraic norms (a^2-2ab-b^2 factors via Pythagorean triples)
- Lattice structure for sieve optimization within standard GNFS
- Special polynomial families where coefficients have Pythagorean relationships
""")

if __name__ == '__main__':
    run_experiment()
