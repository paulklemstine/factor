#!/usr/bin/env python3
"""
Hypothesis Testing Suite
========================
Experimental validation of the three new hypotheses:

  A: Quaternionic Smooth Number Conjecture
  B: Octonion Advantage Conjecture
  C: Hurwitz-LLL Gap Conjecture

Plus: scaling law experiments for optimal α and dimension growth.
"""

import random
import math
import time
from collections import defaultdict
from typing import Optional, Tuple, List


# ── Primality and factoring utilities ──

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i*i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

def random_prime(bits):
    while True:
        p = random.getrandbits(bits) | (1 << (bits-1)) | 1
        if is_prime(p): return p

def small_primes_up_to(B):
    sieve = [True] * (B+1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(B**0.5)+1):
        if sieve[i]:
            for j in range(i*i, B+1, i):
                sieve[j] = False
    return [i for i in range(2, B+1) if sieve[i]]

def is_B_smooth(n, B):
    """Check if n is B-smooth (all prime factors ≤ B)."""
    if n <= 1: return True
    for p in small_primes_up_to(min(B, int(n**0.5)+1)):
        while n % p == 0:
            n //= p
    return n <= B

def four_square_rep(n):
    isqrt_n = int(math.isqrt(n))
    for a in range(isqrt_n, -1, -1):
        ra = n - a*a
        if ra < 0: continue
        for b in range(int(math.isqrt(ra)), -1, -1):
            rb = ra - b*b
            if rb < 0: continue
            for c in range(int(math.isqrt(rb)), -1, -1):
                rc = rb - c*c
                if rc < 0: continue
                d = int(math.isqrt(rc))
                if d*d == rc:
                    return (a, b, c, d)
    return None

# ── LLL (minimal) ──

def gram_schmidt(basis):
    n, d = len(basis), len(basis[0])
    ortho = [list(v) for v in basis]
    mu = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i):
            dij = sum(ortho[i][k]*ortho[j][k] for k in range(d))
            djj = sum(ortho[j][k]**2 for k in range(d))
            if djj < 1e-15: continue
            mu[i][j] = dij/djj
            for k in range(d):
                ortho[i][k] -= mu[i][j]*ortho[j][k]
    return ortho, mu

def lll(basis, delta=0.99):
    basis = [list(v) for v in basis]
    n, d = len(basis), len(basis[0])
    def n2(v): return sum(x*x for x in v)
    ortho, mu = gram_schmidt(basis)
    k = 1
    while k < n:
        for j in range(k-1, -1, -1):
            if abs(mu[k][j]) > 0.5:
                r = round(mu[k][j])
                for i in range(d): basis[k][i] -= r*basis[j][i]
                ortho, mu = gram_schmidt(basis)
        if n2(ortho[k]) >= (delta - mu[k][k-1]**2)*n2(ortho[k-1]):
            k += 1
        else:
            basis[k], basis[k-1] = basis[k-1], basis[k]
            ortho, mu = gram_schmidt(basis)
            k = max(k-1, 1)
    return basis


# ── Hypothesis A: Quaternionic Smooth Number Conjecture ──

def test_hypothesis_A(max_N=5000, B_values=[5, 10, 20, 50]):
    """
    Test: Among integers with four-square reps N = a²+b²+c²+d²,
    how often are the partial sums a², a²+b², a²+b²+c² all B-smooth?

    Compare to the baseline smooth number density.
    """
    print(f"\n{'='*70}")
    print(f"  HYPOTHESIS A: Quaternionic Smooth Number Conjecture")
    print(f"  Testing N ∈ [2, {max_N}]")
    print(f"{'='*70}\n")

    for B in B_values:
        total = 0
        smooth_partial = 0
        smooth_baseline = 0

        for N in range(2, max_N + 1):
            rep = four_square_rep(N)
            if rep is None:
                continue
            a, b, c, d = rep
            total += 1

            # Check if N itself is B-smooth
            if is_B_smooth(N, B):
                smooth_baseline += 1

            # Check if all partial sums are B-smooth
            p1 = a*a
            p2 = a*a + b*b
            p3 = a*a + b*b + c*c
            if p1 > 0 and p2 > 0 and p3 > 0:
                if is_B_smooth(p1, B) and is_B_smooth(p2, B) and is_B_smooth(p3, B):
                    smooth_partial += 1

        rate_partial = smooth_partial / max(1, total) * 100
        rate_baseline = smooth_baseline / max(1, total) * 100

        u = math.log(max_N) / math.log(B) if B > 1 else float('inf')
        print(f"  B = {B:>3}: Partial-smooth = {rate_partial:>6.2f}%"
              f"  |  N-smooth = {rate_baseline:>6.2f}%"
              f"  |  u = {u:.2f}"
              f"  |  ratio = {rate_partial/max(0.01,rate_baseline):.2f}×")

    print(f"\n  If ratio > 1 consistently, partial smoothness exceeds baseline →")
    print(f"  supports Hypothesis A.\n")


# ── Hypothesis B: Octonion Advantage Conjecture ──

def test_hypothesis_B(bit_ranges=[(10, 200), (14, 150), (18, 100)]):
    """
    Test: For each bit size, compare success rates of dim-4 vs dim-8
    lattice factor extraction.
    """
    print(f"\n{'='*70}")
    print(f"  HYPOTHESIS B: Octonion Advantage Conjecture")
    print(f"{'='*70}\n")

    for bits, trials in bit_ranges:
        succ_4, succ_8 = 0, 0

        for _ in range(trials):
            p = random_prime(bits // 2)
            q = random_prime(bits // 2)
            while q == p:
                q = random_prime(bits // 2)
            N = p * q

            # Dimension 4 (quaternion)
            rep4 = four_square_rep(N)
            if rep4:
                scale = max(1, int(N**0.28))
                basis = [[scale if i==j else 0 for j in range(4)] + [rep4[i]]
                         for i in range(4)]
                basis.append([0]*4 + [N])
                red = lll(basis)
                for v in red:
                    g = math.gcd(sum(x*x for x in v[:4]), N)
                    if 1 < g < N:
                        succ_4 += 1
                        break

            # Dimension 8 (octonion)
            # Use greedy 8-square
            rem, comps = N, []
            for i in range(7):
                a = int(math.isqrt(rem))
                comps.append(a); rem -= a*a
                if rem == 0:
                    comps += [0]*(7-i); break
            else:
                a = int(math.isqrt(rem))
                if a*a == rem: comps.append(a)
                else: comps = None

            if comps and len(comps) == 8:
                scale = max(1, int(N**0.28))
                basis = [[scale if i==j else 0 for j in range(8)] + [comps[i]]
                         for i in range(8)]
                basis.append([0]*8 + [N])
                red = lll(basis)
                for v in red:
                    g = math.gcd(sum(x*x for x in v[:8]), N)
                    if 1 < g < N:
                        succ_8 += 1
                        break

        r4 = succ_4/trials*100
        r8 = succ_8/trials*100
        advantage = r8 / max(0.1, r4)
        print(f"  {bits:>2}-bit: Quat = {r4:>5.1f}%  |  Oct = {r8:>5.1f}%"
              f"  |  Advantage = {advantage:.2f}×"
              f"  |  log(N) ≈ {bits*0.693:.1f}")

    print(f"\n  If advantage grows with log(N) → supports Hypothesis B.\n")


# ── Hypothesis C: Hurwitz-LLL Gap ──

def test_hypothesis_C(bits=16, trials=300):
    """
    Test: Compare the Hermite factor of LLL on Hurwitz-structured
    lattices vs random lattices of the same dimension.
    """
    print(f"\n{'='*70}")
    print(f"  HYPOTHESIS C: Hurwitz-LLL Gap")
    print(f"  {bits}-bit, {trials} trials")
    print(f"{'='*70}\n")

    hermite_structured = []
    hermite_random = []

    for _ in range(trials):
        N = random_prime(bits // 2) * random_prime(bits // 2)

        # Structured (quaternion norm) lattice
        rep = four_square_rep(N)
        if rep is None:
            continue
        scale = max(1, int(N**0.28))
        basis_s = [[scale if i==j else 0 for j in range(4)] + [rep[i]]
                    for i in range(4)]
        basis_s.append([0]*4 + [N])
        red_s = lll(basis_s)

        det_s = abs(N * scale**4)  # determinant of structured lattice
        sv_s = math.sqrt(sum(x*x for x in red_s[0]))
        if det_s > 0 and sv_s > 0:
            hf_s = sv_s / (det_s ** (1/5))
            hermite_structured.append(hf_s)

        # Random lattice of same dimension and approximate determinant
        basis_r = [[random.randint(-int(N**0.3), int(N**0.3)) for _ in range(5)]
                    for _ in range(5)]
        # Make it have similar determinant by setting diagonal
        for i in range(4):
            basis_r[i][i] = scale
        basis_r[4][4] = N
        red_r = lll(basis_r)

        sv_r = math.sqrt(sum(x*x for x in red_r[0]))
        if sv_r > 0:
            hf_r = sv_r / (abs(N * scale**4) ** (1/5))
            hermite_random.append(hf_r)

    avg_s = sum(hermite_structured) / max(1, len(hermite_structured))
    avg_r = sum(hermite_random) / max(1, len(hermite_random))

    print(f"  Avg Hermite factor (structured): {avg_s:.4f}")
    print(f"  Avg Hermite factor (random):     {avg_r:.4f}")
    print(f"  Gap ratio: {avg_r/max(0.001, avg_s):.4f}")
    print(f"\n  If gap ratio > 1 → structured lattices reduce better,")
    print(f"  supporting Hypothesis C.\n")


# ── Scaling Law: Optimal α convergence ──

def test_alpha_convergence():
    """Track optimal α as bit size increases."""
    print(f"\n{'='*70}")
    print(f"  SCALING LAW: Optimal α vs Bit Size")
    print(f"{'='*70}\n")

    print(f"  {'Bits':>6} {'Best α':>8} {'Success':>10}")
    print(f"  {'-'*28}")

    for bits in [10, 14, 18, 22, 26]:
        trials = 150
        alphas = [0.20, 0.25, 0.28, 0.30, 0.33]
        best_a, best_r = 0, 0

        cases = []
        for _ in range(trials):
            p = random_prime(bits // 2)
            q = random_prime(bits // 2)
            while q == p:
                q = random_prime(bits // 2)
            cases.append(p * q)

        for alpha in alphas:
            succ = 0
            for N in cases:
                rep = four_square_rep(N)
                if not rep: continue
                sc = max(1, int(N**alpha))
                basis = [[sc if i==j else 0 for j in range(4)] + [rep[i]]
                         for i in range(4)]
                basis.append([0]*4 + [N])
                red = lll(basis)
                for v in red:
                    g = math.gcd(sum(x*x for x in v[:4]), N)
                    if 1 < g < N:
                        succ += 1; break
            rate = succ/trials*100
            if rate > best_r:
                best_r = rate; best_a = alpha

        print(f"  {bits:>6} {best_a:>8.2f} {best_r:>9.1f}%")

    print(f"\n  If best α → 0.25 as bits increase → supports Q1 conjecture.\n")


if __name__ == "__main__":
    random.seed(42)

    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║   Hypothesis Testing Suite — Quaternion/Octonion Factoring          ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    test_hypothesis_A(max_N=3000, B_values=[5, 10, 20, 50])
    test_hypothesis_B(bit_ranges=[(10, 200), (14, 150), (18, 100)])
    test_hypothesis_C(bits=16, trials=200)
    test_alpha_convergence()

    print("\n  All hypothesis tests complete.")
