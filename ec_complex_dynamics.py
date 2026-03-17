#!/usr/bin/env python3
"""
EC Division via Complex Dynamics — Mandelbrot/Julia Set Analogies

Core insight: The Mandelbrot set's Böttcher coordinate Φ satisfies
    Φ(z² + c) = Φ(z)²
This LINEARIZES the doubling map in logarithmic coordinates:
    log Φ([2]z) = 2 · log Φ(z)

If an analogous function Ψ exists on an elliptic curve with
    Ψ([2]P) = Ψ(P)²
then log₂(Ψ(K)) / log₂(Ψ(G)) = k, solving the ECDLP.

This file tests whether such a function can be constructed or approximated.
"""

import sys
import time
import random
import math
import cmath
from collections import defaultdict

import gmpy2
from gmpy2 import mpz

from ecdlp_pythagorean import (
    ECPoint, FastCurve, secp256k1_curve,
    _SECP256K1_BETA, _SECP256K1_LAMBDA,
)

CURVE = secp256k1_curve()
G = CURVE.G
p = int(CURVE.p)
n = CURVE.n
BETA = _SECP256K1_BETA
LAMBDA = _SECP256K1_LAMBDA


# ===========================================================================
# Experiment A: Böttcher Coordinate Analogue
# ===========================================================================
def experiment_A_bottcher_analogue(num_trials=20, key_bits=32):
    """
    The Böttcher coordinate Φ(c) = lim_{n→∞} f_c^n(0)^{1/2^n} linearizes
    the Mandelbrot doubling map. We seek Ψ: E(F_p) → F_p* with Ψ([2]P) = Ψ(P)².

    If Ψ exists: log_Ψ(K) / log_Ψ(G) = k, solving ECDLP.

    Candidate Ψ functions to test:
    1. Ψ(P) = x(P)  — does x([2]P) relate to x(P)² ?
    2. Ψ(P) = x(P)/y(P)  — the "slope" parameter
    3. Ψ(P) = (x(P) - e_i) for 2-torsion points e_i
    4. Ψ(P) = formal group parameter t = -x/y near identity
    """
    print("=" * 70)
    print("EXPERIMENT A: Böttcher Coordinate Analogue")
    print(f"  Seeking Ψ with Ψ([2]P) = Ψ(P)²")
    print("=" * 70)

    # Half-point: [2]⁻¹ on E(F_p).  Since n is odd, [2]⁻¹ = [(n+1)/2]
    half = (n + 1) // 2

    print(f"\n  [2]⁻¹ = [(n+1)/2] = scalar multiplication by {half}")

    # Test candidate Ψ functions
    def test_psi(name, psi_func, num_samples=200):
        """Test if psi([2]P) ≡ psi(P)² mod p for random P."""
        matches = 0
        ratio_set = set()
        for _ in range(num_samples):
            k_val = random.randint(1, n - 1)
            P = CURVE.scalar_mult(k_val, G)
            P2 = CURVE.scalar_mult(2, P)  # [2]P

            psi_P = psi_func(P)
            psi_2P = psi_func(P2)

            if psi_P is None or psi_2P is None:
                continue

            psi_P_sq = psi_P * psi_P % p
            if psi_2P == psi_P_sq:
                matches += 1

            # Check if there's a constant ratio: Ψ([2]P) / Ψ(P)²
            if psi_P_sq != 0:
                ratio = psi_2P * pow(psi_P_sq, p - 2, p) % p
                ratio_set.add(ratio)

        # If ratio_set has exactly 1 element, Ψ([2]P) = c·Ψ(P)² for constant c
        if len(ratio_set) <= 3:
            print(f"    {name}: {matches}/{num_samples} exact, "
                  f"{len(ratio_set)} distinct ratios → NEARLY MULTIPLICATIVE!")
            return True, ratio_set
        else:
            print(f"    {name}: {matches}/{num_samples} exact, "
                  f"{len(ratio_set)} distinct ratios (random)")
            return False, ratio_set

    # Candidate 1: Ψ(P) = x(P)
    print(f"\n  --- Testing candidate Ψ functions ---")
    test_psi("x(P)", lambda P: P.x if not P.is_infinity else None)

    # Candidate 2: Ψ(P) = y(P)
    test_psi("y(P)", lambda P: P.y if not P.is_infinity else None)

    # Candidate 3: Ψ(P) = x/y (formal group parameter near identity)
    test_psi("x/y", lambda P: P.x * pow(P.y, p - 2, p) % p
             if not P.is_infinity and P.y != 0 else None)

    # Candidate 4: Ψ(P) = -x/y (formal group parameter t)
    test_psi("-x/y", lambda P: (-P.x * pow(P.y, p - 2, p)) % p
             if not P.is_infinity and P.y != 0 else None)

    # Candidate 5: Ψ(P) = x² (try quadratic)
    test_psi("x²", lambda P: P.x * P.x % p
             if not P.is_infinity else None)

    # Candidate 6: Ψ(P) = x³ + 7 = y²
    test_psi("y² = x³+7", lambda P: P.y * P.y % p
             if not P.is_infinity else None)

    # Candidate 7: Ψ(P) = x³
    test_psi("x³", lambda P: pow(P.x, 3, p)
             if not P.is_infinity else None)

    # The doubling formula: for y²=x³+7, [2](x,y):
    # λ = 3x²/(2y), x' = λ²-2x, y' = λ(x-x')-y
    # So x([2]P) = (3x²/(2y))² - 2x = 9x⁴/(4y²) - 2x = 9x⁴/(4(x³+7)) - 2x
    # This is a RATIONAL function of x, not a square. So x isn't multiplicative.

    # What about the Tate-Lichtenbaum pairing / Weil pairing approach?
    # The Weil pairing IS a Böttcher-like object: e_n(P,Q) is multiplicative
    # in both arguments. But computing it requires a point of order n
    # independent from G — which lives in F_{p^k} for large embedding degree k.

    print(f"\n  --- Theoretical analysis ---")
    print(f"  The doubling formula gives x([2]P) = 9x⁴/(4(x³+7)) - 2x")
    print(f"  This is a degree-4 rational map, NOT a square map.")
    print(f"  For Ψ([2]P) = Ψ(P)², we need Ψ to conjugate this to squaring.")
    print(f"  Such a Ψ would be a 'Schröder function' for the rational map.")
    print(f"\n  Over ℂ, the Schröder function exists near fixed points")
    print(f"  (Koenigs linearization). Over F_p, it may not converge.")
    print(f"  Let's try constructing it iteratively...")

    # Koenigs linearization: near a fixed point z₀ with multiplier μ=f'(z₀),
    # Ψ(z) = lim_{n→∞} f^n(z) / μ^n
    # Fixed points of the x-doubling map: x([2]P) = x(P)
    # This means [2]P = ±P, i.e., P = O (trivial) or [2]P = -P → [3]P = O
    # So the 3-torsion points are fixed points of the x-doubling map!

    print(f"\n  --- 3-torsion fixed points of x-doubling map ---")
    # [3]P = O means the division polynomial ψ₃(x) = 0
    # ψ₃(x) = 3x⁴ + 6ax² + 12bx - a²  (for y²=x³+ax+b)
    # For a=0, b=7: ψ₃(x) = 3x⁴ + 84x = 3x(x³ + 28)
    # So x=0 or x³ = -28 mod p

    # x = 0: y² = 7, y = √7 mod p
    y_sq = 7
    if pow(y_sq, (p - 1) // 2, p) == 1:
        y0 = pow(y_sq, (p + 1) // 4, p)
        P3_0 = ECPoint(0, int(y0))
        verify = CURVE.scalar_mult(3, P3_0)
        print(f"    3-torsion at x=0: ({0}, {y0})")
        print(f"    [3]P = {'O' if verify.is_infinity else f'({verify.x}, {verify.y})'}")
    else:
        print(f"    x=0: 7 is not a QR mod p")

    # x³ = -28 mod p
    neg28 = (-28) % p
    # Check if -28 is a cubic residue
    cr_test = pow(neg28, (p - 1) // 3, p)
    print(f"    x³ = -28: cubic residue test = {cr_test} (need 1)")

    if cr_test == 1:
        # Find cube root
        # For p ≡ 1 mod 3, use Adleman-Manders-Miller or find ω first
        # p-1 = 3^s · t with gcd(t,3)=1
        pm1 = p - 1
        s = 0
        t = pm1
        while t % 3 == 0:
            s += 1
            t //= 3
        print(f"    p-1 = 3^{s} · {t.bit_length()}-bit number")

        # Cube root via: x = (-28)^((t+1)//3) if 3|(t+1), otherwise more complex
        # Actually for p ≡ 1 mod 3: use Cipolla-like method
        # Simpler: (-28)^((2(p-1)/3 + 1)/3) ... let me just use discrete log
        # Or: find a non-cube g, then cube root = (-28)^a · g^b
        # Brute-force is fine for a one-time computation

        # Find a primitive cube root of unity ω first
        for g in range(2, 1000):
            omega = pow(g, (p - 1) // 3, p)
            if omega != 1:
                break
        print(f"    Cube root of unity ω = ...{omega % (10**20)}")

        # Now find one cube root of -28
        # Try: r = (-28)^((2*t + 1) // 3) ... complicated
        # Let's just use the fact that r³ ≡ -28 and try Tonelli-like approach
        # For the experiment, we can verify numerically
        # r = (-28)^(e) where 3e ≡ 1 mod (p-1)/3 ... no, this doesn't work simply

        # Alternative: directly compute using gmpy2
        r = int(gmpy2.powmod(gmpy2.mpz(neg28), gmpy2.mpz((2 * (p - 1) // 3 + 3) // 3), gmpy2.mpz(p)))
        if pow(r, 3, p) == neg28:
            print(f"    Cube root found: r³ ≡ -28 mod p ✓")
        else:
            # Try another exponent
            for exp_try in range(1, 100):
                r = int(gmpy2.powmod(gmpy2.mpz(neg28), gmpy2.mpz(exp_try * (p - 1) // 3 + 1), gmpy2.mpz(p)))
                if pow(r, 3, p) == neg28:
                    print(f"    Cube root found (exp={exp_try}): r³ ≡ -28 mod p ✓")
                    break
            else:
                # Brute force search using random
                found = False
                for _ in range(10000):
                    r = random.randint(2, p - 1)
                    if pow(r, 3, p) == neg28:
                        print(f"    Cube root found (random): r³ ≡ -28 mod p ✓")
                        found = True
                        break
                if not found:
                    print(f"    Could not find cube root (continuing without it)")
                    r = None

        if r is not None:
            # 3-torsion point at x=r
            y_sq_r = (r * r * r + 7) % p  # should be -28+7 = -21 mod p
            if pow(y_sq_r, (p - 1) // 2, p) == 1:
                y_r = pow(y_sq_r, (p + 1) // 4, p)
                P3_r = ECPoint(int(r), int(y_r))
                verify = CURVE.scalar_mult(3, P3_r)
                print(f"    3-torsion at x=r: verified [3]P = "
                      f"{'O' if verify.is_infinity else 'NOT O'}")

                # Compute the multiplier of the x-doubling map at this fixed point
                # f(x) = 9x⁴/(4(x³+7)) - 2x
                # f'(x) = d/dx [9x⁴/(4(x³+7)) - 2x]
                #        = [36x³·4(x³+7) - 9x⁴·12x²] / [4(x³+7)]² - 2
                #        = [144x³(x³+7) - 108x⁶] / [16(x³+7)²] - 2
                #        = [144x⁶ + 1008x³ - 108x⁶] / [16(x³+7)²] - 2
                #        = [36x⁶ + 1008x³] / [16(x³+7)²] - 2
                #        = x³(36x³ + 1008) / [16(x³+7)²] - 2

                x0 = r
                x03 = pow(x0, 3, p)
                num = x03 * (36 * x03 + 1008) % p
                den = 16 * pow((x03 + 7) % p, 2, p) % p
                multiplier = (num * pow(den, p - 2, p) - 2) % p

                print(f"\n    Multiplier μ = f'(x₀) at 3-torsion fixed point:")
                print(f"    μ = ...{multiplier % (10**20)}")
                print(f"    μ bits: {multiplier.bit_length()}")

                # For Koenigs linearization to work, we need |μ| ≠ 0,1
                # Over F_p, "≠ 0,1" means μ ∉ {0, 1}
                if multiplier not in (0, 1, p - 1):
                    print(f"    μ ∉ {{0, ±1}} → Koenigs linearization may exist!")

                    # Attempt: Ψ(x) = lim f^n(x) / μ^n
                    # Over F_p, there's no "limit" — but we can compute
                    # the truncated series Ψ_N(x) = f^N(x) / μ^N
                    # If it stabilizes, we have our Böttcher coordinate.

                    print(f"\n    --- Koenigs iteration Ψ_N(x) = f^N(x) / μ^N ---")
                    mu_inv = pow(multiplier, p - 2, p)

                    for trial in range(min(5, num_trials)):
                        k_val = random.randint(1, (1 << key_bits) - 1)
                        P = CURVE.scalar_mult(k_val, G)
                        x_curr = P.x

                        prev_psi = None
                        stabilized = False
                        for N in range(1, 30):
                            # Apply the x-doubling map
                            # x' = 9x⁴/(4(x³+7)) - 2x
                            x3 = pow(x_curr, 3, p)
                            x4 = x_curr * x3 % p
                            denom = 4 * (x3 + 7) % p
                            if denom % p == 0:
                                print(f"      Trial {trial}: hit singularity at N={N}")
                                break
                            x_next = (9 * x4 * pow(denom, p - 2, p) - 2 * x_curr) % p

                            # Ψ_N = x_next / μ^N  (relative to fixed point)
                            psi_N = (x_next - r) * pow(multiplier, (p - 2) * N, p) % p

                            if prev_psi is not None and psi_N == prev_psi:
                                print(f"      Trial {trial}: STABILIZED at N={N}! "
                                      f"Ψ = ...{psi_N % (10**10)}")
                                stabilized = True
                                break
                            prev_psi = psi_N
                            x_curr = x_next

                        if not stabilized:
                            print(f"      Trial {trial}: did not stabilize in 30 iterations")
                else:
                    print(f"    μ ∈ {{0, ±1}} → degenerate fixed point")

    print(f"\n  VERDICT: See analysis above for whether Koenigs linearization converges")
    return False


# ===========================================================================
# Experiment B: Halving Itinerary (External Angle Analogue)
# ===========================================================================
def experiment_B_halving_itinerary(num_trials=20, key_bits=32):
    """
    On the Mandelbrot boundary, the external angle θ has binary expansion
    that encodes the itinerary under θ → 2θ mod 1.

    EC analogue: the "halving map" [2]⁻¹ = [(n+1)/2] on E(F_p).
    Starting from K = k·G, repeatedly halve:
        K, [(n+1)/2]·K, [(n+1)/2]²·K, ...
    This sequence corresponds to:
        k·G, (k/2)·G, (k/4)·G, ...
    where division is mod n.

    The "itinerary" — which half of E each halved point falls in —
    encodes the binary digits of k (read from LSB).

    If we can define "which half" without knowing k, we recover k bit by bit.
    """
    print("=" * 70)
    print("EXPERIMENT B: Halving Itinerary (External Angle Analogue)")
    print(f"  Trials: {num_trials}, Key bits: {key_bits}")
    print("=" * 70)

    half_scalar = (n + 1) // 2  # [2]⁻¹ as scalar
    assert (2 * half_scalar) % n == 1, "[2]⁻¹ verification failed"

    print(f"\n  [2]⁻¹ = {half_scalar}")

    # The key question: can we determine if k is even or odd from K = k·G?
    # If k is even: k = 2m, so [2]⁻¹K = m·G where m < k/2
    # If k is odd:  k = 2m+1, so [2]⁻¹K = ((2m+1+n)/2)·G = ((2m+1+n)/2)·G
    #   Since n is odd, (2m+1+n)/2 = m + (n+1)/2, which is large (~n/2)
    #
    # So: if k is even, [2]⁻¹K has a "small" scalar
    #     if k is odd,  [2]⁻¹K has a "large" scalar (~n/2)
    # But we can't directly measure the scalar!

    # Test: does any coordinate-based test distinguish even vs odd k?
    print(f"\n  --- Parity detection tests ---")

    tests = {
        "x < p/2": lambda P: P.x < p // 2,
        "y < p/2": lambda P: P.y < p // 2,
        "x+y < p": lambda P: (P.x + P.y) < p,
        "x·y QR":  lambda P: pow(P.x * P.y % p, (p - 1) // 2, p) == 1,
        "x mod 3 == 0": lambda P: P.x % 3 == 0,
        "LSB(x)": lambda P: P.x & 1 == 0,
        "x³+7 < p/2": lambda P: (pow(P.x, 3, p) + 7) % p < p // 2,
    }

    for test_name, test_func in tests.items():
        correct = 0
        total = 0
        for _ in range(2000):
            k_val = random.randint(1, (1 << key_bits) - 1)
            K = CURVE.scalar_mult(k_val, G)
            if K.is_infinity:
                continue

            # Apply [2]⁻¹
            K_half = CURVE.scalar_mult(half_scalar, K)

            # The test: does test_func(K_half) predict k's LSB?
            prediction = test_func(K_half) if not K_half.is_infinity else False
            actual_lsb = k_val & 1

            # We check if the test correlates with parity
            if prediction == (actual_lsb == 0):
                correct += 1
            total += 1

        accuracy = correct / total if total > 0 else 0
        deviation = abs(accuracy - 0.5)
        marker = " ← !" if deviation > 0.02 else ""
        print(f"    {test_name:<20}: accuracy={accuracy:.4f}  "
              f"deviation={deviation:.4f}{marker}")

    # Deeper test: multi-bit itinerary
    print(f"\n  --- Multi-bit itinerary extraction ---")
    print(f"  Halving K repeatedly and recording x < p/2 for each step")

    for trial in range(min(5, num_trials)):
        k_val = random.randint(1, (1 << key_bits) - 1)
        K = CURVE.scalar_mult(k_val, G)

        itinerary = []
        Q = K
        for bit in range(key_bits):
            Q = CURVE.scalar_mult(half_scalar, Q)
            itinerary.append(1 if Q.x < p // 2 else 0)

        # Compare with actual binary digits of k
        actual_bits = [(k_val >> i) & 1 for i in range(key_bits)]

        matches = sum(1 for a, b in zip(itinerary, actual_bits) if a == b)
        print(f"    Trial {trial}: k={k_val:#x}")
        print(f"      Itinerary:  {''.join(map(str, itinerary[:20]))}")
        print(f"      Actual k:   {''.join(map(str, actual_bits[:20]))}")
        print(f"      Match: {matches}/{key_bits} = {matches/key_bits:.3f} "
              f"(0.500 = random)")

    # The fundamental problem: x < p/2 splits E(F_p) in HALF geometrically,
    # but not algebraically. The group structure and the coordinate structure
    # are "orthogonal" — this is precisely the discrete log assumption.

    print(f"\n  --- Why this doesn't work (theoretical) ---")
    print(f"  The halving map [2]⁻¹ permutes E(F_p) pseudo-randomly.")
    print(f"  Any coordinate-based partition (x < p/2, etc.) is 'geometric'")
    print(f"  while parity of k is 'algebraic'. These are independent")
    print(f"  unless the group law has exploitable geometric structure.")
    print(f"\n  This is exactly the Diffie-Hellman Decision Problem (DDH):")
    print(f"  DDH hardness ↔ no efficient geometric parity test exists.")

    return False


# ===========================================================================
# Experiment C: Julia Set Basins of Attraction
# ===========================================================================
def experiment_C_julia_basins(num_trials=20, key_bits=28):
    """
    Define a dynamical system on E(F_p) inspired by Julia set iteration.
    Map EC point to complex number, iterate z → z² + c, measure escape time.

    Hypothesis: escape time correlates with discrete log.
    """
    print("=" * 70)
    print("EXPERIMENT C: Julia Set Basins of Attraction")
    print(f"  Trials: {num_trials}, Key bits: {key_bits}")
    print("=" * 70)

    # Map EC point (x,y) to complex number z = (x/p) + i·(y/p) ∈ [0,1]²
    def ec_to_complex(P):
        return complex(P.x / p, P.y / p)

    # Also try: z = exp(2πi · x/p) — maps to unit circle
    def ec_to_circle(P):
        theta = 2 * math.pi * (P.x / p)
        return complex(math.cos(theta), math.sin(theta))

    # Mandelbrot iteration: z → z² + c
    def escape_time(z, c, max_iter=100, bailout=4.0):
        for i in range(max_iter):
            z = z * z + c
            if abs(z) > bailout:
                return i
        return max_iter

    # Test 1: Use G as c, K as z₀
    print(f"\n  --- Test 1: c = map(G), z₀ = map(K) ---")
    c_from_G = ec_to_complex(G)
    print(f"  c = {c_from_G}")

    escape_by_k = {}
    for trial in range(500):
        k_val = random.randint(1, (1 << key_bits) - 1)
        K = CURVE.scalar_mult(k_val, G)
        z0 = ec_to_complex(K)
        et = escape_time(z0, c_from_G)
        if et not in escape_by_k:
            escape_by_k[et] = []
        escape_by_k[et].append(k_val)

    # Check if escape time correlates with k
    print(f"  Escape time distribution:")
    for et in sorted(escape_by_k.keys())[:10]:
        ks = escape_by_k[et]
        mean_k = sum(ks) / len(ks)
        print(f"    t={et:3d}: {len(ks):3d} points, mean_k={mean_k:.1f}")

    # Pearson correlation between escape time and k
    all_et = []
    all_k = []
    for et, ks in escape_by_k.items():
        for k in ks:
            all_et.append(et)
            all_k.append(k)

    if len(all_et) > 2:
        mean_et = sum(all_et) / len(all_et)
        mean_k = sum(all_k) / len(all_k)
        cov = sum((e - mean_et) * (k - mean_k) for e, k in zip(all_et, all_k)) / len(all_et)
        std_et = math.sqrt(sum((e - mean_et) ** 2 for e in all_et) / len(all_et))
        std_k = math.sqrt(sum((k - mean_k) ** 2 for k in all_k) / len(all_k))
        r = cov / (std_et * std_k) if std_et > 0 and std_k > 0 else 0
        print(f"  Pearson r(escape_time, k) = {r:.6f}")

    # Test 2: Use x-coordinate directly as the dynamical variable
    print(f"\n  --- Test 2: Iterate x → x² + G.x mod p (in F_p) ---")

    def fp_escape(x0, c, p_val, max_iter=256):
        """'Escape time' in F_p: count until cycle detected or max_iter."""
        seen = {}
        x = x0
        for i in range(max_iter):
            if x in seen:
                return i, i - seen[x]  # time, cycle length
            seen[x] = i
            x = (x * x + c) % p_val
        return max_iter, 0

    # On F_p, iteration x → x² + c is a polynomial dynamical system.
    # It's the Pollard rho function! The cycle structure IS the basis
    # of Pollard's rho factoring and DLP algorithms.

    print(f"  (Note: this IS Pollard's rho iteration in disguise!)")

    cycle_lens = defaultdict(list)
    for trial in range(200):
        k_val = random.randint(1, (1 << key_bits) - 1)
        K = CURVE.scalar_mult(k_val, G)

        t, c_len = fp_escape(K.x, G.x, p, max_iter=1000)
        cycle_lens[c_len].append(k_val)

    print(f"  Cycle length distribution:")
    for cl in sorted(cycle_lens.keys())[:8]:
        ks = cycle_lens[cl]
        print(f"    cycle_len={cl}: {len(ks)} points")

    # Test 3: the REAL connection — Lattès maps
    print(f"\n  --- Test 3: Lattès map (the true EC-Mandelbrot bridge) ---")
    print(f"  A Lattès map is a rational map f: P¹ → P¹ that fits in:")
    print(f"      E --[2]--> E")
    print(f"      |    x     |    x")
    print(f"      v          v")
    print(f"      P¹ --f--> P¹")
    print(f"  where x is the x-coordinate projection.")
    print(f"  For y²=x³+7: f(x) = (x⁴-56x)/(4(x³+7)) = x-doubling map")
    print(f"  This IS a Mandelbrot-family map! Its Julia set = x(E(F_p))")

    # Compute the Lattès map explicitly
    def lattes_map(x_val):
        """The Lattès map f(x) = x([2]P) where P has x-coordinate x_val."""
        x3 = pow(x_val, 3, p)
        x4 = x_val * x3 % p
        num = (x4 - 56 * x_val) % p   # x⁴ - 8·7·x for b=7
        den = (4 * (x3 + 7)) % p      # 4(x³ + b)
        if den == 0:
            return None
        return num * pow(den, p - 2, p) % p

    # Verify: lattes_map(P.x) should equal [2]P.x
    print(f"\n  Verifying Lattès map...")
    for _ in range(5):
        k_val = random.randint(1, n - 1)
        P = CURVE.scalar_mult(k_val, G)
        P2 = CURVE.scalar_mult(2, P)
        lm = lattes_map(P.x)
        match = "✓" if lm == P2.x else "✗"
        print(f"    f(x(P)) = x([2]P)? {match}")

    # The Lattès map IS the correct formalization of "Mandelbrot for EC"
    # Its periodic points = x-coordinates of torsion points
    # Its Julia set (over ℂ) = the entire Riemann sphere (since E has good reduction)
    # Over F_p: iterating the Lattès map traces the doubling sequence

    # Key experiment: iterating the Lattès map on K.x and comparing with G.x
    print(f"\n  --- Lattès map orbit comparison ---")
    print(f"  Orbit of K.x under f should 'sync' with orbit of G.x at step k")

    for trial in range(min(5, num_trials)):
        k_val = random.randint(1, min((1 << 16) - 1, (1 << key_bits) - 1))
        K = CURVE.scalar_mult(k_val, G)

        # Orbit of K.x: f(K.x), f²(K.x), ... = x([4]K), x([8]K), ...
        # = x(2^i · k · G) for i = 1,2,...

        # Orbit of G.x: f(G.x), f²(G.x), ... = x([2]G), x([4]G), ...
        # = x(2^i · G) for i = 1,2,...

        # These orbits intersect when 2^i · k ≡ 2^j mod n for some i,j
        # i.e., when k ≡ 2^(j-i) mod n
        # This happens at j-i = log₂(k) mod ord_n(2)

        orbit_K = {}
        x = K.x
        for i in range(200):
            x_new = lattes_map(x)
            if x_new is None:
                break
            if x_new in orbit_K:
                break
            orbit_K[x_new] = i
            x = x_new

        # Check: at which step does G's orbit hit K's orbit?
        x = G.x
        sync_step = None
        for j in range(200):
            x_new = lattes_map(x)
            if x_new is None:
                break
            if x_new in orbit_K:
                i = orbit_K[x_new]
                sync_step = (j, i)
                break
            x = x_new

        if sync_step:
            j, i = sync_step
            # 2^(j+1) ≡ 2^(i+1) · k mod n
            # k ≡ 2^(j-i) mod n
            k_guess = pow(2, j - i, n)
            print(f"    Trial {trial}: k={k_val}, orbits sync at G_step={j}, K_step={i}")
            print(f"      k_guess = 2^{j-i} mod n = {k_guess}")
            print(f"      Correct? {k_guess == k_val or (n - k_guess) == k_val}")
        else:
            print(f"    Trial {trial}: k={k_val}, orbits did not sync in 200 steps")

    print(f"\n  VERDICT: The Lattès map correctly formalizes the EC-Mandelbrot connection.")
    print(f"  Orbit synchronization detects k only when k is a power of 2 (trivial case).")
    print(f"  For general k, the Lattès orbit comparison reduces to standard DLP methods.")
    return False


# ===========================================================================
# Experiment D: Escape Rate / Green's Function Analogue
# ===========================================================================
def experiment_D_greens_function(num_trials=20, key_bits=32):
    """
    The Green's function of the Mandelbrot set:
        G(c) = lim (1/2^n) · log|f^n(0)|

    measures escape rate and equals log|Φ(c)| (Böttcher coordinate).

    EC analogue: define a "height" function h on E(F_p) via the Lattès map.
    The canonical height ĥ(P) = lim (1/4^n) · h(x([2^n]P)) satisfies
        ĥ(kP) = k² · ĥ(P)

    If computable, this gives k² = ĥ(K)/ĥ(G), hence k = √(ĥ(K)/ĥ(G)).
    """
    print("=" * 70)
    print("EXPERIMENT D: Green's Function / Canonical Height")
    print(f"  Trials: {num_trials}, Key bits: {key_bits}")
    print("=" * 70)

    # The naive height: h(P) = log|x(P)|
    # Over F_p, we use the "p-adic height" or just the integer value.

    # The canonical height (Néron-Tate):
    # ĥ(P) = lim_{n→∞} h([2^n]P) / 4^n
    # satisfies ĥ(kP) = k² · ĥ(P)

    # Over ℝ or ℚ_p this converges. Over F_p, log(x) isn't well-defined
    # in the usual sense. But we can try:

    # Approach 1: Use the integer lift — treat x(P) as an integer in [0,p)
    # and compute h(P) = log(min(x, p-x)) as a "naive height"

    print(f"\n  --- Naive height h(P) = log₂(x(P)) ---")

    def naive_height(P):
        if P.is_infinity:
            return 0.0
        x = P.x
        # Use min(x, p-x) for symmetry
        return math.log2(min(x, p - x)) if min(x, p - x) > 0 else 0.0

    # Test: does h([2]P) ≈ 4·h(P) ?
    print(f"  Testing h([2]P) / h(P):")
    for _ in range(10):
        k_val = random.randint(1, n - 1)
        P = CURVE.scalar_mult(k_val, G)
        P2 = CURVE.scalar_mult(2, P)
        h_P = naive_height(P)
        h_2P = naive_height(P2)
        ratio = h_2P / h_P if h_P > 0 else float('inf')
        print(f"    h(P)={h_P:.2f}, h([2]P)={h_2P:.2f}, ratio={ratio:.4f} (want 4.0)")

    # Approach 2: Canonical height via iteration
    print(f"\n  --- Canonical height ĥ(P) = lim h([2^n]P) / 4^n ---")

    def canonical_height(P, num_iter=50):
        """Approximate canonical height by iterating the doubling map."""
        Q = P
        for i in range(num_iter):
            Q = CURVE.scalar_mult(2, Q)
        h = naive_height(Q)
        return h / (4.0 ** num_iter)

    # Test: does ĥ(kP) = k² · ĥ(P)?
    print(f"  Testing ĥ(kP) / ĥ(P):")
    for trial in range(10):
        k_val = random.randint(2, 1000)
        P = G
        kP = CURVE.scalar_mult(k_val, G)

        h_P = canonical_height(P)
        h_kP = canonical_height(kP)

        if h_P > 0:
            ratio = h_kP / h_P
            expected = k_val * k_val
            print(f"    k={k_val:4d}: ĥ(kG)/ĥ(G) = {ratio:.6e} "
                  f"(want {expected})")
        else:
            print(f"    k={k_val}: ĥ(G) = 0 (degenerate)")

    # Approach 3: p-adic valuation based height
    print(f"\n  --- p-adic inspired height ---")

    # In the p-adic world, v_p(x(P)) measures how "close to identity" P is.
    # For the formal group, v_p(t(P)) where t = -x/y.
    # Over F_p, we can use: how many leading zero bits does x(P) have?

    def padic_height(P):
        if P.is_infinity:
            return float('inf')
        # "Proximity to zero" in F_p: how small is min(x, p-x)?
        x = min(P.x, p - P.x)
        if x == 0:
            return float('inf')
        return 256 - x.bit_length()  # number of leading zeros in 256-bit repr

    print(f"  Leading-zero height of k·G for various k:")
    for k_val in [1, 2, 4, 8, 16, 100, 1000, n // 2, n - 1]:
        P = CURVE.scalar_mult(k_val % n, G)
        h = padic_height(P)
        print(f"    k={k_val:>20d}: padic_height = {h}")

    # Fundamental issue: over F_p, all heights are essentially constant
    # because the reduction mod p destroys the Archimedean/p-adic size info.
    print(f"\n  --- Theoretical analysis ---")
    print(f"  Over Q: ĥ(kP) = k²·ĥ(P) gives k² immediately.")
    print(f"  Over F_p: reduction mod p destroys the height information.")
    print(f"  The naive height h(P) = log₂(x(P)) is essentially random mod p.")
    print(f"  The canonical height collapses: h([2^n]P)/4^n → 0 or ∞")
    print(f"  because over F_p the sequence [2^n]P is periodic, not growing.")
    print(f"\n  The Green's function / Böttcher coordinate requires ARCHIMEDEAN")
    print(f"  or ULTRAMETRIC convergence. F_p has neither — it's a finite field.")
    print(f"  This is the deepest reason why 'Mandelbrot for EC' fails over F_p.")

    print(f"\n  VERDICT: Height functions collapse over finite fields.")
    print(f"  The k² relationship only works over number fields (Q, Q_p).")
    return False


# ===========================================================================
# Experiment E: Orbit Portraits and External Rays
# ===========================================================================
def experiment_E_orbit_portraits(num_trials=20, key_bits=24):
    """
    In Mandelbrot dynamics, external rays at rational angles land at
    specific points. The 'orbit portrait' — which rays land together —
    encodes the combinatorial structure.

    EC analogue: The Lattès map f(x) = x([2]P) has periodic orbits
    corresponding to torsion points. The "landing pattern" of the
    doubling orbit of K.x relative to these torsion markers
    encodes information about k.
    """
    print("=" * 70)
    print("EXPERIMENT E: Orbit Portraits and External Rays")
    print(f"  Trials: {num_trials}, Key bits: {key_bits}")
    print("=" * 70)

    # Compute small torsion x-coordinates as "landmarks"
    print(f"\n  --- Computing torsion landmarks ---")
    torsion_x = {}
    for m in range(2, 20):
        P = CURVE.scalar_mult((n // m) if n % m == 0 else 1, G)
        if not P.is_infinity:
            # m-torsion point: [m]P = O iff P = [(n/m)]G
            # Only works if m | n. Since n is prime, only m=1 and m=n work.
            pass

    # Since n is prime, E(F_p) has no non-trivial torsion subgroups.
    # Every point except O has order n. No landmarks!
    print(f"  n is prime → no torsion landmarks exist.")
    print(f"  Cannot define orbit portrait without reference points.")

    # Alternative: use ARBITRARY landmarks and see if the pattern encodes k
    print(f"\n  --- Arbitrary landmark encoding ---")
    print(f"  Partition F_p into m bins. Record which bin x([2^i]K) falls in.")
    print(f"  This gives a base-m 'address' for K's doubling orbit.")

    m_bins = 8  # partition into 8 sectors
    bin_size = p // m_bins

    for trial in range(min(5, num_trials)):
        k_val = random.randint(1, (1 << key_bits) - 1)
        K = CURVE.scalar_mult(k_val, G)

        # Record orbit bins
        orbit = []
        Q = K
        for step in range(key_bits):
            bin_idx = int(Q.x // bin_size) % m_bins
            orbit.append(bin_idx)
            Q = CURVE.scalar_mult(2, Q)

        # Compare with k's base-m digits
        k_digits = []
        kk = k_val
        for _ in range(key_bits):
            k_digits.append(kk % m_bins)
            kk //= m_bins

        matches = sum(1 for a, b in zip(orbit, k_digits) if a == b)
        expected = key_bits / m_bins

        print(f"    Trial {trial}: k={k_val}")
        print(f"      Orbit bins: {''.join(map(str, orbit[:16]))}")
        print(f"      k digits:   {''.join(map(str, k_digits[:16]))}")
        print(f"      Matches: {matches}/{key_bits} (expected random: {expected:.1f})")

    # The orbit portrait doesn't encode k because the bin partition
    # is geometric while k is algebraic.

    # But there's one more idea: the PERIOD of the doubling orbit
    print(f"\n  --- Doubling orbit period ---")
    print(f"  The orbit K, [2]K, [4]K, [8]K, ... has period ord_n(2)")

    ord_2 = 1
    pow2 = 2
    for i in range(1, 10000):
        if pow2 == 1:
            ord_2 = i
            break
        pow2 = pow2 * 2 % n
    if ord_2 == 1:
        # ord_n(2) is large — check if n-1 is divisible by 2
        print(f"  ord_n(2) > 10000 (too large to compute naively)")
        print(f"  n-1 = {n-1}")
        print(f"  n-1 is {'even' if (n-1) % 2 == 0 else 'odd'}")
        # Factor out powers of 2
        nm1 = n - 1
        v2 = 0
        while nm1 % 2 == 0:
            v2 += 1
            nm1 //= 2
        print(f"  n-1 = 2^{v2} · {nm1.bit_length()}-bit odd number")
        print(f"  So ord_n(2) | (n-1) and is at least > 10000")

        # The orbit period is the same for ALL points (since the group is cyclic)
        # So it leaks ZERO information about k.
    else:
        print(f"  ord_n(2) = {ord_2}")

    print(f"\n  VERDICT: Orbit portraits require torsion landmarks (none exist).")
    print(f"  Doubling orbit period is the same for all points → no info about k.")
    return False


# ===========================================================================
# Experiment F: Schröder Equation / Conjugacy to Linear Map
# ===========================================================================
def experiment_F_schroder(num_trials=10, key_bits=24):
    """
    The Schröder equation: Ψ(f(x)) = μ·Ψ(x) conjugates f to a linear map.
    If Ψ conjugates the Lattès map to multiplication by μ, then
    Ψ(K.x) = μ^(something) · Ψ(G.x), potentially revealing k.

    Over ℂ, Ψ exists near non-degenerate fixed points (Koenigs theorem).
    Over F_p, it may exist as a formal power series mod p.
    """
    print("=" * 70)
    print("EXPERIMENT F: Schröder Equation / Linearization")
    print(f"  Trials: {num_trials}, Key bits: {key_bits}")
    print("=" * 70)

    # The Lattès map for y²=x³+7:
    # f(x) = (x⁴ - 56x) / (4x³ + 28)
    # Wait, let me re-derive. Doubling formula for y²=x³+7:
    # λ = 3x²/(2y), x' = λ² - 2x = 9x⁴/(4y²) - 2x = 9x⁴/(4(x³+7)) - 2x
    # x' = (9x⁴ - 8x(x³+7)) / (4(x³+7))
    # x' = (9x⁴ - 8x⁴ - 56x) / (4(x³+7))
    # x' = (x⁴ - 56x) / (4(x³+7))
    # x' = (x⁴ - 56x) / (4x³ + 28)

    def f(x):
        """Lattès map: x-coord of [2]P given x-coord of P."""
        num = (pow(x, 4, p) - 56 * x) % p
        den = (4 * pow(x, 3, p) + 28) % p
        if den == 0:
            return None
        return num * pow(den, p - 2, p) % p

    # Verify
    print(f"\n  Verifying Lattès map f(x)...")
    for _ in range(5):
        k_val = random.randint(1, n - 1)
        P = CURVE.scalar_mult(k_val, G)
        P2 = CURVE.scalar_mult(2, P)
        fx = f(P.x)
        print(f"    f(x(P)) = x([2]P)? {'✓' if fx == P2.x else '✗'}")

    # Fixed points: f(x₀) = x₀
    # (x₀⁴ - 56x₀) / (4x₀³ + 28) = x₀
    # x₀⁴ - 56x₀ = x₀(4x₀³ + 28)
    # x₀⁴ - 56x₀ = 4x₀⁴ + 28x₀
    # -3x₀⁴ - 84x₀ = 0
    # x₀(-3x₀³ - 84) = 0
    # x₀ = 0 or x₀³ = -28

    print(f"\n  Fixed points of Lattès map:")
    print(f"    x₀ = 0: f(0) = {f(0)}, is fixed? {f(0) == 0}")

    # Multiplier at x₀=0:
    # f'(x) = d/dx [(x⁴-56x)/(4x³+28)]
    # = [(4x³-56)(4x³+28) - (x⁴-56x)(12x²)] / (4x³+28)²
    # At x=0:
    # = [(-56)(28) - 0] / (28)²
    # = -56·28 / 784 = -1568/784 = -2
    mu_0 = (-2) % p
    print(f"    Multiplier at x₀=0: μ = f'(0) = {(-2) % p} = -2 mod p")

    # μ = -2 is interesting! The Schröder function Ψ near x₀=0 satisfies:
    # Ψ(f(x)) = -2 · Ψ(x)
    # So Ψ(f^n(x)) = (-2)^n · Ψ(x)

    # Compute Schröder function as formal power series:
    # Ψ(x) = x + a₂x² + a₃x³ + ...
    # From Ψ(f(x)) = μ·Ψ(x), equate coefficients

    print(f"\n  --- Computing Schröder function Ψ(x) = x + a₂x² + ... mod p ---")
    print(f"  Ψ(f(x)) = -2·Ψ(x)")

    # f(x) = (x⁴ - 56x)/(4x³ + 28) near x=0
    # f(x) = -56x/28 + ... = -2x + ...  (confirms μ = -2)
    # f(x) = -2x · (1 - x³/56) / (1 + x³/7) ... expand as power series

    # Let's compute f(x) as a power series mod x^N
    # f(x) = (x⁴ - 56x) · (4x³ + 28)⁻¹
    # (4x³ + 28)⁻¹ = (1/28)(1 + 4x³/28)⁻¹ = (1/28)(1 - x³/7 + x⁶/49 - ...)

    inv28 = pow(28, p - 2, p)
    inv7 = pow(7, p - 2, p)

    # Compute first few terms of Schröder function
    # Ψ(x) = x + a₂x² + a₃x³ + a₄x⁴ + ...
    # We need to solve for a_i from Ψ(f(x)) = -2·Ψ(x)

    # f(x) power series (compute numerically for first ~10 terms)
    # f(x) = -2x + c₄x⁴ + c₇x⁷ + ... (only terms where exponent ≡ 1 mod 3)
    # Actually: f(x) = (x⁴-56x)/(4x³+28)
    # = (x⁴-56x)·(1/28)·(1-4x³/28+16x⁶/784-...)
    # = (x⁴-56x)/28 · (1-x³/7+x⁶/49-...)
    # = (-2x + x⁴/28) · (1-x³/7+x⁶/49-...)
    # = -2x + 2x⁴/7 + x⁴/28 - x⁷·(2/49-1/196) + ...
    # = -2x + (8+1)x⁴/28 + ...
    # = -2x + 9x⁴/28 + ...

    # Wait, let me be more careful
    # f(x) = (x⁴ - 56x) / (4x³ + 28)
    # Let u = x³/7, then 4x³+28 = 28(1+u)
    # f(x) = (x⁴ - 56x)/(28(1+u))
    # = (x⁴ - 56x)/28 · (1 - u + u² - u³ + ...)
    # = (x⁴/28 - 2x)(1 - x³/7 + x⁶/49 - ...)
    # Term by term:
    # Coeff of x¹: -2
    # Coeff of x⁴: 1/28 + (-2)(-1/7) = 1/28 + 2/7 = 1/28 + 8/28 = 9/28
    # Coeff of x⁷: (-2)(1/49) + (1/28)(-1/7) = -2/49 - 1/196 = (-8-1)/196 = -9/196

    c1 = (-2) % p
    c4 = 9 * pow(28, p - 2, p) % p
    c7 = (-9) * pow(196, p - 2, p) % p

    print(f"  f(x) = {c1}·x + {c4}·x⁴ + {c7}·x⁷ + ... (mod p)")

    # Schröder equation: Ψ(f(x)) = μ·Ψ(x) where μ = -2
    # Ψ(x) = x + a₄x⁴ + a₇x⁷ + ... (by symmetry, only x^(3k+1) terms)
    # Note: since f(x) = -2x + O(x⁴), and the gap is 3, the Schröder
    # function should have the same gap pattern.

    # Ψ(f(x)) = f(x) + a₄·f(x)⁴ + ...
    # = (-2x + c₄x⁴ + ...) + a₄(-2x)⁴ + ...
    # = -2x + c₄x⁴ + 16a₄x⁴ + ...
    # = -2x + (c₄ + 16a₄)x⁴ + ...
    #
    # μ·Ψ(x) = -2(x + a₄x⁴ + ...)
    # = -2x - 2a₄x⁴ + ...
    #
    # Equating x⁴: c₄ + 16a₄ = -2a₄
    # 18a₄ = -c₄
    # a₄ = -c₄/18

    a4 = (-c4) * pow(18, p - 2, p) % p
    print(f"  Ψ(x) = x + {a4}·x⁴ + ... (mod p)")

    # Now test: does Ψ help recover k?
    print(f"\n  --- Testing Schröder function for k recovery ---")
    print(f"  If Ψ linearizes f, then Ψ(x([2^n]K)) = (-2)^n · Ψ(x(K))")
    print(f"  And Ψ(x(K)) / Ψ(x(G)) should relate to k")

    for trial in range(min(5, num_trials)):
        k_val = random.randint(1, (1 << key_bits) - 1)
        K = CURVE.scalar_mult(k_val, G)
        K2 = CURVE.scalar_mult(2, K)

        # Evaluate Ψ (truncated to first 2 terms)
        psi_K = (K.x + a4 * pow(K.x, 4, p)) % p
        psi_K2 = (K2.x + a4 * pow(K2.x, 4, p)) % p
        psi_G = (G.x + a4 * pow(G.x, 4, p)) % p

        # Check: Ψ(f(K.x)) = -2 · Ψ(K.x) ?
        ratio = psi_K2 * pow(psi_K, p - 2, p) % p if psi_K != 0 else None
        kg_ratio = psi_K * pow(psi_G, p - 2, p) % p if psi_G != 0 else None

        print(f"    Trial {trial}: k={k_val}")
        print(f"      Ψ([2]K)/Ψ(K) = ...{ratio % (10**10) if ratio else 'undef'} "
              f"(want {(-2) % p} = -2 mod p)")
        print(f"      Ψ(K)/Ψ(G) = ...{kg_ratio % (10**10) if kg_ratio else 'undef'}")

    print(f"\n  --- Why truncated Ψ fails ---")
    print(f"  The Schröder series converges near x₀=0 in the p-adic metric.")
    print(f"  But G.x and K.x are NOT close to 0 — they're random in [0,p).")
    print(f"  The series needs O(p) terms to converge at non-infinitesimal x.")
    print(f"  Computing O(p) terms is as hard as brute-force ECDLP.")
    print(f"\n  KEY INSIGHT: The radius of convergence of Ψ around a fixed point")
    print(f"  is 'p-adically small' — only points in the formal group (with")
    print(f"  v_p(x/y) > 0) are in the convergence region. G and K are not.")

    print(f"\n  VERDICT: Schröder linearization exists formally but converges")
    print(f"  only in an infinitesimal neighborhood — useless for arbitrary points.")
    return False


# ===========================================================================
# Summary
# ===========================================================================
def run_all():
    print("\n" + "=" * 70)
    print("  COMPLEX DYNAMICS / MANDELBROT EXPERIMENTS FOR EC DIVISION")
    print("=" * 70 + "\n")

    experiments = [
        ("A: Böttcher Coordinate Analogue", experiment_A_bottcher_analogue),
        ("B: Halving Itinerary", experiment_B_halving_itinerary),
        ("C: Julia Set Basins", experiment_C_julia_basins),
        ("D: Green's Function / Height", experiment_D_greens_function),
        ("E: Orbit Portraits", experiment_E_orbit_portraits),
        ("F: Schröder Linearization", experiment_F_schroder),
    ]

    results = {}
    for name, func in experiments:
        print(f"\n{'#' * 70}")
        print(f"# {name}")
        print(f"{'#' * 70}\n")
        try:
            t0 = time.time()
            result = func()
            elapsed = time.time() - t0
            results[name] = (result, elapsed)
            print(f"\n  [Completed in {elapsed:.2f}s]\n")
        except Exception as e:
            results[name] = (None, 0)
            print(f"\n  [FAILED: {e}]\n")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"\n  {'Experiment':<40} {'Result':<12} {'Time'}")
    print(f"  {'-'*40} {'-'*12} {'-'*8}")
    for name, (result, elapsed) in results.items():
        status = "POSITIVE" if result else ("NEGATIVE" if result is not None else "ERROR")
        print(f"  {name:<40} {status:<12} {elapsed:.2f}s")

    print(f"\n  ═══ DEEP INSIGHT ═══")
    print(f"  The Mandelbrot set lives over ℂ (or ℝ), where convergence,")
    print(f"  continuity, and the Archimedean absolute value exist.")
    print(f"  Elliptic curves over F_p have NONE of these properties.")
    print(f"")
    print(f"  The Böttcher coordinate Φ linearizes z→z²+c because the")
    print(f"  dynamics 'escape to infinity' — a concept that doesn't")
    print(f"  exist in a finite field. Over F_p, every orbit is periodic.")
    print(f"")
    print(f"  The Lattès map IS the correct bridge: it's a rational map")
    print(f"  whose dynamics over ℂ are equivalent to EC doubling.")
    print(f"  But over F_p, its Schröder function (the linearizer) only")
    print(f"  converges in a p-adically tiny neighborhood of fixed points.")
    print(f"")
    print(f"  To make the Mandelbrot connection work, we would need to")
    print(f"  'lift' the problem from F_p to a setting with convergence:")
    print(f"    - ℚ_p (p-adics): formal group log works, but only near O")
    print(f"    - ℂ (complex):   Weierstrass ℘⁻¹ works, but needs lifting")
    print(f"    - ℝ (reals):     canonical height works, but loses mod p info")
    print(f"")
    print(f"  Each lifting attempt faces the same barrier: going from F_p")
    print(f"  to an infinite field loses the finite-field structure that")
    print(f"  makes the problem well-defined, while the finite field")
    print(f"  destroys the analytic structure that makes division possible.")
    print(f"")
    print(f"  This is the FUNDAMENTAL DUALITY at the heart of ECC security.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in "ABCDEF":
        exp = sys.argv[1]
        funcs = {
            'A': experiment_A_bottcher_analogue,
            'B': experiment_B_halving_itinerary,
            'C': experiment_C_julia_basins,
            'D': experiment_D_greens_function,
            'E': experiment_E_orbit_portraits,
            'F': experiment_F_schroder,
        }
        funcs[exp]()
    else:
        run_all()
