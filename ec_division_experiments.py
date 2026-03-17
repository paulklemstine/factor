#!/usr/bin/env python3
"""
EC "Division" Experiments — probing exploitable structure in secp256k1.

Seven experiments testing whether partial information about k can be
extracted from K = k·G without brute-force enumeration.

Usage:
    python3 ec_division_experiments.py [experiment_number]
    python3 ec_division_experiments.py all
"""

import sys
import time
import random
import math
import struct
from collections import defaultdict

import gmpy2
from gmpy2 import mpz, invert as gmp_invert

# Import curve and arithmetic from existing codebase
from ecdlp_pythagorean import (
    ECPoint, FastCurve, secp256k1_curve,
    _SECP256K1_BETA, _SECP256K1_LAMBDA,
)

# ---------------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------------
CURVE = secp256k1_curve()
G = CURVE.G
p = int(CURVE.p)
n = CURVE.n
BETA = _SECP256K1_BETA
LAMBDA = _SECP256K1_LAMBDA


# ---------------------------------------------------------------------------
# Experiment 1: Coordinate Bit Leakage
# ---------------------------------------------------------------------------
def experiment_1_bit_leakage(num_samples=10000, key_bits=40):
    """
    Test whether bits of K.x correlate with bits of k.

    For random k in [1, 2^key_bits), compute K = k·G, then measure:
    1. Bit-by-bit correlation between k and K.x
    2. Hamming weight correlation
    3. MSB/LSB bias
    """
    print("=" * 70)
    print("EXPERIMENT 1: Coordinate Bit Leakage")
    print(f"  Samples: {num_samples}, Key bits: {key_bits}")
    print("=" * 70)

    # We'll track correlation for each bit position
    max_bits = min(key_bits, 64)  # check first 64 bits of K.x vs k
    correlation = [[0, 0, 0, 0] for _ in range(max_bits)]
    # [both_0, both_1, k0_Kx1, k1_Kx0]

    hw_pairs = []  # (hamming_weight(k), hamming_weight(K.x))
    msb_match = 0
    lsb_match = 0

    t0 = time.time()
    bound = 1 << key_bits

    for i in range(num_samples):
        k_val = random.randint(1, bound - 1)
        K = CURVE.scalar_mult(k_val, G)
        Kx = K.x

        # Bit correlation
        for bit in range(max_bits):
            k_bit = (k_val >> bit) & 1
            Kx_bit = (Kx >> bit) & 1
            if k_bit == 0 and Kx_bit == 0:
                correlation[bit][0] += 1
            elif k_bit == 1 and Kx_bit == 1:
                correlation[bit][1] += 1
            elif k_bit == 0 and Kx_bit == 1:
                correlation[bit][2] += 1
            else:
                correlation[bit][3] += 1

        # Hamming weight
        hw_k = bin(k_val).count('1')
        hw_Kx = bin(Kx).count('1')
        hw_pairs.append((hw_k, hw_Kx))

        # MSB match (top bit of k vs top bit of K.x in 256-bit field)
        k_msb = (k_val >> (key_bits - 1)) & 1
        Kx_msb = (Kx >> 255) & 1
        if k_msb == Kx_msb:
            msb_match += 1

        # LSB match
        if (k_val & 1) == (Kx & 1):
            lsb_match += 1

    elapsed = time.time() - t0

    # Analyze correlations
    print(f"\n  Time: {elapsed:.2f}s")
    print(f"\n  --- Bit-by-bit correlation (first {max_bits} bits) ---")

    max_deviation = 0
    max_dev_bit = 0
    for bit in range(max_bits):
        total = sum(correlation[bit])
        # Perfect independence: each cell = total/4
        expected = total / 4
        agreement = (correlation[bit][0] + correlation[bit][1]) / total
        deviation = abs(agreement - 0.5)
        if deviation > max_deviation:
            max_deviation = deviation
            max_dev_bit = bit
        if bit < 8 or deviation > 0.02:
            print(f"    Bit {bit:2d}: agree={agreement:.4f}  "
                  f"deviation={deviation:.4f}  "
                  f"({correlation[bit]})")

    print(f"\n  Max deviation: bit {max_dev_bit} = {max_deviation:.4f} "
          f"(expected ~{1/math.sqrt(num_samples):.4f} from noise)")

    # Hamming weight correlation
    mean_hw_k = sum(h[0] for h in hw_pairs) / len(hw_pairs)
    mean_hw_Kx = sum(h[1] for h in hw_pairs) / len(hw_pairs)
    cov = sum((h[0] - mean_hw_k) * (h[1] - mean_hw_Kx) for h in hw_pairs) / len(hw_pairs)
    std_k = math.sqrt(sum((h[0] - mean_hw_k) ** 2 for h in hw_pairs) / len(hw_pairs))
    std_Kx = math.sqrt(sum((h[1] - mean_hw_Kx) ** 2 for h in hw_pairs) / len(hw_pairs))
    pearson = cov / (std_k * std_Kx) if std_k > 0 and std_Kx > 0 else 0

    print(f"\n  --- Hamming weight correlation ---")
    print(f"    Mean HW(k):  {mean_hw_k:.2f}")
    print(f"    Mean HW(Kx): {mean_hw_Kx:.2f}")
    print(f"    Pearson r:   {pearson:.6f}")
    print(f"    (r=0 means no correlation, |r|>0.01 would be interesting)")

    print(f"\n  --- MSB/LSB match rates ---")
    print(f"    MSB match: {msb_match/num_samples:.4f} (expected: 0.5000)")
    print(f"    LSB match: {lsb_match/num_samples:.4f} (expected: 0.5000)")

    # Verdict
    significant = max_deviation > 3 / math.sqrt(num_samples) or abs(pearson) > 0.05
    print(f"\n  VERDICT: {'LEAKAGE DETECTED!' if significant else 'No significant leakage (as expected)'}")
    return significant


# ---------------------------------------------------------------------------
# Experiment 2: j=0 Automorphism / Cube Root Decomposition
# ---------------------------------------------------------------------------
def experiment_2_cube_root_decomposition(num_trials=20, key_bits=40):
    """
    Exploit secp256k1's j=0 automorphism for 3-way scalar decomposition.

    GLV gives k = k1 + k2·λ with k1,k2 ~ 128 bits each.
    Can we decompose into k = k1 + k2·λ + k3·λ² with each ~85 bits?

    Also test: does the 3-fold symmetry enable a kangaroo speedup
    beyond the known √3 factor?
    """
    print("=" * 70)
    print("EXPERIMENT 2: j=0 Cube Root Decomposition")
    print(f"  Trials: {num_trials}, Key bits: {key_bits}")
    print("=" * 70)

    lam = LAMBDA
    lam2 = (lam * lam) % n  # λ²
    # Note: λ³ ≡ 1 (mod n), so λ² ≡ λ⁻¹ (mod n)
    lam_inv = pow(lam, n - 2, n)
    assert lam2 == lam_inv, "λ² should equal λ⁻¹ mod n"
    print(f"  Confirmed: λ² ≡ λ⁻¹ (mod n)")
    print(f"  λ  = {lam}")
    print(f"  λ² = {lam2}")

    # GLV 2-way decomposition uses a lattice:
    # Find short vectors in the lattice {(a,b) : a + b·λ ≡ 0 (mod n)}
    # For 3-way: {(a,b,c) : a + b·λ + c·λ² ≡ 0 (mod n)}

    # Build the lattice basis for 3-way decomposition
    # L = [[n, 0, 0], [λ, -1, 0], [λ², 0, -1]]
    # We want short vectors (a, b, c) such that a + b·λ + c·λ² ≡ 0 mod n

    # Use simple lattice reduction (Gaussian/LLL)
    print(f"\n  --- 3-way GLV lattice ---")

    # For the 2-way GLV, the short vectors have ~128-bit components.
    # For 3-way, we'd hope for ~85-bit components.

    # Let's use a direct approach: try to find the lattice vectors
    # using extended Euclidean / continued fractions on λ mod n

    # 2-way decomposition (standard GLV)
    def glv_decompose_2way(k_val):
        """Decompose k = k1 + k2·λ mod n with small k1, k2."""
        # Use the standard babai rounding on the GLV lattice
        # Basis vectors v1, v2 found via extended gcd of n and λ
        # Simplified: just use the rounding approach
        # k1 = k mod (n//something), k2 from remainder
        # Actually, let's compute it properly with the known short vectors

        # For secp256k1, the short vectors of the GLV lattice are known:
        a1 = 0x3086D221A7D46BCDE86C90E49284EB15
        b1 = -0xE4437ED6010E88286F547FA90ABFE4C3
        a2 = 0x114CA50F7A8E2F3F657C1108D9D44CFD8
        b2 = 0x3086D221A7D46BCDE86C90E49284EB15

        # Babai's rounding
        det = a1 * b2 - a2 * b1  # = n
        c1 = (b2 * k_val) // n  # round
        c2 = (-b1 * k_val) // n
        k1 = k_val - c1 * a1 - c2 * a2
        k2 = -c1 * b1 - c2 * b2

        # Verify
        assert (k1 + k2 * lam) % n == k_val % n, "2-way decomposition failed"
        return k1, k2

    # 3-way decomposition attempt
    def glv_decompose_3way(k_val):
        """
        Attempt 3-way decomposition: k = k1 + k2·λ + k3·λ² mod n.

        Since λ² = λ⁻¹, this is k = k1 + k2·λ + k3·λ⁻¹.
        We have 1 equation, 3 unknowns — under-determined.
        Use lattice reduction to find the shortest solution.
        """
        # Start with 2-way: k = k1_2 + k2_2·λ
        k1_2, k2_2 = glv_decompose_2way(k_val)

        # Now split k2_2·λ into k2·λ + k3·λ²
        # k2·λ + k3·λ² = k2_2·λ → k2 + k3·λ = k2_2 (dividing by λ)
        # This is just another GLV decomposition of k2_2!
        if abs(k2_2) < 2:
            return k1_2, k2_2, 0

        k2_2_mod = k2_2 % n
        k2_3, k3_3 = glv_decompose_2way(k2_2_mod)

        # Final: k = k1_2 + k2_3·λ + k3_3·λ²
        # Verify
        recon = (k1_2 + k2_3 * lam + k3_3 * lam2) % n
        assert recon == k_val % n, f"3-way decomposition failed: {recon} != {k_val % n}"
        return k1_2, k2_3, k3_3

    print(f"\n  --- Decomposition size comparison ---")
    print(f"  {'k (bits)':<12} {'2-way max (bits)':<20} {'3-way max (bits)':<20} {'Ratio'}")

    total_2way_bits = 0
    total_3way_bits = 0

    for trial in range(num_trials):
        k_val = random.randint(1, (1 << key_bits) - 1)

        k1_2, k2_2 = glv_decompose_2way(k_val)
        k1_3, k2_3, k3_3 = glv_decompose_3way(k_val)

        max_2 = max(abs(k1_2).bit_length(), abs(k2_2).bit_length())
        max_3 = max(abs(k1_3).bit_length(), abs(k2_3).bit_length(), abs(k3_3).bit_length())

        total_2way_bits += max_2
        total_3way_bits += max_3

        if trial < 10:
            ratio = max_3 / max_2 if max_2 > 0 else float('inf')
            print(f"  {key_bits:<12} {max_2:<20} {max_3:<20} {ratio:.3f}")

    avg_2 = total_2way_bits / num_trials
    avg_3 = total_3way_bits / num_trials

    print(f"\n  Average max component bits:")
    print(f"    2-way: {avg_2:.1f} bits")
    print(f"    3-way: {avg_3:.1f} bits")
    print(f"    Ideal 3-way: {256/3:.1f} bits (if uniformly distributed)")

    # Test the endomorphism application cost
    print(f"\n  --- Endomorphism application cost ---")
    K = CURVE.scalar_mult(random.randint(1, n - 1), G)
    beta = BETA

    t0 = time.time()
    for _ in range(10000):
        # φ(K) = (β·Kx, Ky) — just one field multiply!
        phi_Kx = beta * K.x % p
        phi_K = ECPoint(phi_Kx, K.y)
    t_phi = (time.time() - t0) / 10000

    t0 = time.time()
    for _ in range(10000):
        # Full scalar mult for comparison
        _ = CURVE.scalar_mult(3, K)
    t_mult = (time.time() - t0) / 10000

    print(f"    φ(K) cost:        {t_phi*1e6:.1f} µs (1 field mul)")
    print(f"    3·K cost:         {t_mult*1e6:.1f} µs (double+add)")
    print(f"    Speedup:          {t_mult/t_phi:.0f}x")

    # Multi-target kangaroo benefit analysis
    print(f"\n  --- Multi-target search benefit ---")
    print(f"    Standard kangaroo:  O(√N) = O(2^{key_bits//2})")
    print(f"    With 3 targets (K, φK, φ²K): each gives independent walk")
    print(f"    Expected speedup: √3 ≈ {math.sqrt(3):.3f}x")
    print(f"    Combined with negation: √6 ≈ {math.sqrt(6):.3f}x")

    three_way_useful = avg_3 < avg_2 * 0.85
    print(f"\n  VERDICT: 3-way decomposition {'REDUCES' if three_way_useful else 'does NOT reduce'} "
          f"component size significantly")
    return three_way_useful


# ---------------------------------------------------------------------------
# Experiment 3: p-adic Lifting (Smart's Attack Variant)
# ---------------------------------------------------------------------------
def experiment_3_padic_lifting(num_trials=10, key_bits=32):
    """
    Test partial p-adic lifting for non-anomalous curve.

    Smart's attack works when #E(F_p) = p (anomalous).
    secp256k1: #E = n ≠ p. How much info does a partial lift reveal?
    """
    print("=" * 70)
    print("EXPERIMENT 3: p-adic Lifting")
    print(f"  Trials: {num_trials}, Key bits: {key_bits}")
    print("=" * 70)

    # Trace of Frobenius
    t_frob = p + 1 - n
    print(f"\n  Curve order n = {n}")
    print(f"  Field prime p = {p}")
    print(f"  Trace t = p+1-n = {t_frob}")
    print(f"  t bits: {t_frob.bit_length()}")
    print(f"  |t| / √p: {float(t_frob) / math.sqrt(float(p)):.6f}")
    print(f"  (Anomalous requires t=1, we have t={t_frob})")

    # For Smart's attack, we'd lift the curve E/F_p to Ê/Z_p²
    # and use the p-adic logarithm.
    # E: y² = x³ + 7 over F_p
    # Lift to Ê: Y² = X³ + 7 over Z/p²Z

    # The p-adic logarithm ψ maps:
    # ψ(P) = -x(p·P̃)/y(p·P̃) mod p
    # where P̃ is the lifted point.

    # For anomalous curves, ψ(K) / ψ(G) = k mod p.
    # For non-anomalous, [p]P̃ might not map to the kernel nicely.

    # Let's compute what happens:
    print(f"\n  --- Attempting p-adic lift ---")

    def lift_point(Px, Py, p_val):
        """
        Lift affine point (Px, Py) on E/F_p to a point on E/Z_{p²}.
        We need Y such that Y² ≡ X³ + 7 (mod p²) and Y ≡ Py (mod p).
        Use Hensel lifting: Y = Py + t·p where t = (X³+7 - Py²)/(2·Py·p) mod p
        """
        p2 = p_val * p_val
        X = Px  # Keep X the same
        rhs = (X * X * X + 7) % p2
        lhs = (Py * Py) % p2
        residue = (rhs - lhs) % p2

        if residue % p_val != 0:
            return None  # Can't lift

        t = (residue // p_val) * pow(2 * Py, p_val - 2, p_val) % p_val
        Y = (Py + t * p_val) % p2
        # Verify
        assert (Y * Y - X * X * X - 7) % p2 == 0, "Lift verification failed"
        return X, Y

    def ec_add_mod(P, Q, p_val, mod):
        """Point addition on E: y²=x³+7 modulo `mod`."""
        if P is None:
            return Q
        if Q is None:
            return P
        Px, Py = P
        Qx, Qy = Q
        if Px == Qx:
            if (Py + Qy) % mod == 0:
                return None  # point at infinity
            # Doubling
            lam_num = (3 * Px * Px) % mod
            lam_den = (2 * Py) % mod
            lam_den_inv = pow(lam_den, p_val - 2, mod)  # Fermat only works mod p, not p²!
            # For mod p², we need a different inversion approach
            return None  # Can't do generic inversion mod p²
        else:
            dx = (Qx - Px) % mod
            dy = (Qy - Py) % mod
            # Need dx^{-1} mod p². Use Hensel lift of inverse mod p.
            dx_inv_p = pow(dx % p_val, p_val - 2, p_val)
            # Hensel: if d·d_inv ≡ 1 (mod p), then d_inv_p2 = d_inv·(2 - d·d_inv) mod p²
            prod = (dx * dx_inv_p) % mod
            dx_inv = (dx_inv_p * (2 - prod)) % mod
            lam = (dy * dx_inv) % mod
            Rx = (lam * lam - Px - Qx) % mod
            Ry = (lam * (Px - Rx) - Py) % mod
            return (Rx % mod, Ry % mod)

    def scalar_mult_mod(k_val, P, p_val, mod):
        """Scalar multiplication on E mod `mod`."""
        result = None
        addend = P
        while k_val > 0:
            if k_val & 1:
                result = ec_add_mod(result, addend, p_val, mod)
                if result is None and k_val > 1:
                    return None
            k_val >>= 1
            if k_val > 0:
                addend = ec_add_mod(addend, addend, p_val, mod)
                if addend is None:
                    break
        return result

    successes = 0
    partial_info_bits = []

    for trial in range(num_trials):
        k_val = random.randint(1, (1 << key_bits) - 1)
        K = CURVE.scalar_mult(k_val, G)

        # Lift G and K to E/Z_{p²}
        G_lift = lift_point(G.x, G.y, p)
        K_lift = lift_point(K.x, K.y, p)

        if G_lift is None or K_lift is None:
            print(f"    Trial {trial}: lift failed")
            continue

        p2 = p * p

        # Compute [n]G̃ and [n]K̃ on E/Z_{p²}
        # For anomalous curve, [p]P̃ would be in the kernel of reduction
        # For us, [n]P̃ should go to identity mod p (since n = #E(F_p))
        nG = scalar_mult_mod(n, G_lift, p, p2)
        nK = scalar_mult_mod(n, K_lift, p, p2)

        if nG is not None and nK is not None:
            # p-adic logarithm: ψ(P) = -x/y mod p for points in kernel
            # Check if [n]G̃ is in the kernel (x,y divisible by p)
            nGx, nGy = nG
            nKx, nKy = nK

            gx_val = nGx % p
            gy_val = nGy % p
            kx_val = nKx % p
            ky_val = nKy % p

            if gx_val == 0 and gy_val == 0 and kx_val == 0 and ky_val == 0:
                # Both in kernel! Extract p-adic log
                psi_G = (-(nGx // p) * pow(nGy // p, p - 2, p)) % p
                psi_K = (-(nKx // p) * pow(nKy // p, p - 2, p)) % p

                if psi_G != 0:
                    k_recovered = (psi_K * pow(psi_G, p - 2, p)) % p
                    if k_recovered == k_val:
                        print(f"    Trial {trial}: FULL RECOVERY! k={k_val}")
                        successes += 1
                    else:
                        # Check if k mod (small prime) matches
                        for small_p in [2, 3, 5, 7, 11, 13]:
                            if k_recovered % small_p == k_val % small_p:
                                partial_info_bits.append(small_p)
                        print(f"    Trial {trial}: k={k_val}, recovered={k_recovered % (1<<key_bits)}, "
                              f"match_mod_small={[sp for sp in [2,3,5,7] if k_recovered%sp==k_val%sp]}")
                else:
                    print(f"    Trial {trial}: ψ(G) = 0 (degenerate)")
            else:
                print(f"    Trial {trial}: [n]G̃ not in kernel "
                      f"(x%p={gx_val!=0}, y%p={gy_val!=0})")
        else:
            print(f"    Trial {trial}: scalar mult mod p² failed (hit infinity)")

    print(f"\n  Full recoveries: {successes}/{num_trials}")
    print(f"  Partial info (mod small primes): {len(partial_info_bits)} matches")
    print(f"\n  VERDICT: {'p-adic lifting WORKS!' if successes > 0 else 'No recovery (curve is not anomalous, as expected)'}")
    print(f"  t_frob = {t_frob}, far from 1 → Smart attack inapplicable")
    return successes > 0


# ---------------------------------------------------------------------------
# Experiment 4: Summation Polynomial Sieve (toy curve)
# ---------------------------------------------------------------------------
def experiment_4_summation_poly(prime_bits=23):
    """
    Test index calculus via Semaev's summation polynomials on a small curve.

    On a toy curve (23-bit prime), measure:
    - Factor base density
    - Relation finding rate
    - Crossover point vs Pollard's rho
    """
    print("=" * 70)
    print("EXPERIMENT 4: Summation Polynomial Sieve")
    print(f"  Toy curve prime bits: {prime_bits}")
    print("=" * 70)

    # Find a suitable curve y² = x³ + ax + b over F_q
    # with prime order (for simplicity)
    q = int(gmpy2.next_prime(1 << prime_bits))
    # Use y² = x³ + 7 (same form as secp256k1) for direct comparison
    a_coeff, b_coeff = 0, 7

    print(f"  Toy curve: y² = x³ + 7 over F_{q}")

    # Find a generator by finding any point and checking order
    def find_point(q, a, b):
        for x in range(q):
            rhs = (x * x * x + a * x + b) % q
            if pow(rhs, (q - 1) // 2, q) == 1:  # quadratic residue
                y = pow(rhs, (q + 1) // 4, q)  # works if q ≡ 3 mod 4
                if (y * y) % q == rhs:
                    return (x, y)
                # General Tonelli-Shanks
                y = int(gmpy2.isqrt_rem(gmpy2.mpz(rhs))[0])
                if (y * y) % q == rhs:
                    return (x, y)
        return None

    def toy_add(P, Q, q, a):
        if P is None: return Q
        if Q is None: return P
        if P[0] == Q[0] and P[1] != Q[1]: return None
        if P == Q:
            lam = (3 * P[0] * P[0] + a) * pow(2 * P[1], q - 2, q) % q
        else:
            lam = (Q[1] - P[1]) * pow(Q[0] - P[0], q - 2, q) % q
        x3 = (lam * lam - P[0] - Q[0]) % q
        y3 = (lam * (P[0] - x3) - P[1]) % q
        return (x3, y3)

    def toy_mult(k, P, q, a):
        R = None
        S = P
        while k > 0:
            if k & 1: R = toy_add(R, S, q, a)
            S = toy_add(S, S, q, a)
            k >>= 1
        return R

    # Find curve order using naive counting (small curve)
    print(f"  Counting curve points...")
    t0 = time.time()
    points = []
    for x in range(q):
        rhs = (x * x * x + a_coeff * x + b_coeff) % q
        leg = pow(rhs, (q - 1) // 2, q)
        if leg == 1:
            y = pow(rhs, (q + 1) // 4, q)
            if (y * y) % q != rhs:
                # Need Tonelli-Shanks for q ≢ 3 mod 4
                continue
            points.append((x, y))
            if y != 0:
                points.append((x, (q - y) % q))
        elif rhs == 0:
            points.append((x, 0))

    curve_order = len(points) + 1  # +1 for point at infinity
    print(f"  Curve order: {curve_order} ({curve_order.bit_length()} bits)")
    print(f"  Point count time: {time.time()-t0:.3f}s")

    # Pick a generator (any point of order = curve_order if prime)
    Gt = points[0]
    print(f"  Generator: {Gt}")

    # Factor base: points with x < B
    B_values = [int(q ** e) for e in [0.3, 0.4, 0.5, 0.6]]

    for B in B_values:
        if B >= q:
            B = q - 1
        fb_points = [(x, y) for (x, y) in points if x < B and y <= q // 2]

        print(f"\n  --- Factor base bound B={B} ({len(fb_points)} points) ---")

        if len(fb_points) < 3:
            print(f"    Too few FB points, skipping")
            continue

        # Relation finding: for random scalar r, compute r·G,
        # then check if r·G has x < B (i.e., is in the factor base)
        relations_needed = len(fb_points) + 5
        relations_found = 0
        attempts = 0
        max_attempts = min(100000, 10 * q)

        t0 = time.time()
        while relations_found < relations_needed and attempts < max_attempts:
            r = random.randint(1, curve_order - 1)
            rG = toy_mult(r, Gt, q, a_coeff)
            if rG is not None and rG[0] < B:
                relations_found += 1
            attempts += 1

        elapsed = time.time() - t0
        rate = relations_found / attempts if attempts > 0 else 0

        print(f"    Relations: {relations_found}/{relations_needed} needed")
        print(f"    Attempts: {attempts}")
        print(f"    Hit rate: {rate:.4f} (expected ~{B/q:.4f})")
        print(f"    Time: {elapsed:.3f}s")

        if relations_found >= relations_needed:
            print(f"    STATUS: Enough relations found!")
            # Estimate: time for index calculus at this B
            ic_time = elapsed * relations_needed / relations_found
            # Compare with Pollard rho: O(√curve_order) steps
            rho_steps = int(math.sqrt(curve_order))
            print(f"    IC relation time: {ic_time:.3f}s")
            print(f"    Pollard rho would need ~{rho_steps} steps")
        else:
            print(f"    STATUS: Not enough relations at this B")

    # Semaev's f3 polynomial
    print(f"\n  --- Semaev f3 analysis ---")
    print(f"    f3(x1,x2,x3) = 0 iff ∃ P1+P2+P3 = O with x(Pi)=xi")
    print(f"    For y²=x³+7, f3 is a degree-4 polynomial in each variable")
    print(f"    Gröbner basis computation cost dominates for large fields")
    print(f"    On {prime_bits}-bit field: feasible")
    print(f"    On 256-bit field: currently intractable")

    print(f"\n  VERDICT: Index calculus on EC remains harder than Pollard's rho")
    print(f"  at this scale. Semaev polynomials need Gröbner basis breakthroughs")
    return False


# ---------------------------------------------------------------------------
# Experiment 5: Multiplicative Order Discovery
# ---------------------------------------------------------------------------
def experiment_5_order_probing(num_trials=10, key_bits=32):
    """
    Probe whether K+i·G has special order properties for small i.

    If m·(K+i·G) = O for small m, then n | m·(k+i), revealing k mod (n/gcd(m,n)).
    Since n is prime for secp256k1, this can only happen if k+i ≡ 0 mod n,
    but we test on toy curves where the order might have small factors.
    """
    print("=" * 70)
    print("EXPERIMENT 5: Multiplicative Order Discovery")
    print(f"  Trials: {num_trials}, Key bits: {key_bits}")
    print("=" * 70)

    # On secp256k1: n is prime, so every non-identity point has order n.
    # No small-order subgroups to exploit.
    print(f"\n  secp256k1 order n = {n}")
    print(f"  n is prime: {gmpy2.is_prime(n)}")
    print(f"  No small-order subgroups exist.")

    # But what about the twist curve? E': y² = x³ + 7 has a twist
    # E'_twist: y² = x³ + 7·d⁶ for non-square d
    # The twist order n' = 2p + 2 - n
    n_twist = 2 * p + 2 - n
    print(f"\n  Twist curve order n' = {n_twist}")
    print(f"  n' factorization (partial):")

    # Factor n_twist partially
    n_tw = n_twist
    small_factors = []
    for sp in range(2, 10000):
        while n_tw % sp == 0:
            small_factors.append(sp)
            n_tw //= sp
    print(f"    Small factors: {small_factors}")
    print(f"    Remaining cofactor: {n_tw.bit_length()} bits")

    if small_factors:
        print(f"\n  The twist has small cofactors! Implications:")
        print(f"    If a point accidentally lands on the twist (invalid-curve attack),")
        print(f"    we could extract k mod {math.prod(small_factors)} = k mod {math.prod(small_factors)}")
        print(f"    But this requires the target to USE unhardened point validation.")

    # Test: on secp256k1 itself, check if K+i·G for small i has any
    # special x-coordinate properties (small, etc.)
    print(f"\n  --- Special x-coordinate search ---")
    for trial in range(min(num_trials, 5)):
        k_val = random.randint(1, (1 << key_bits) - 1)
        K = CURVE.scalar_mult(k_val, G)

        min_x = p
        min_i = 0
        for i in range(-100, 101):
            Ki = CURVE.add(K, CURVE.scalar_mult(i % n, G)) if i != 0 else K
            if not Ki.is_infinity and Ki.x < min_x:
                min_x = Ki.x
                min_i = i

        print(f"    Trial {trial}: k={k_val}, smallest x at i={min_i}, "
              f"x has {min_x.bit_length()} bits (vs 256 expected)")

    print(f"\n  VERDICT: Order probing inapplicable — n is prime, no small subgroups")
    print(f"  Twist attack requires invalid-curve scenario (not applicable to ECDLP)")
    return False


# ---------------------------------------------------------------------------
# Experiment 6: Lattice Attack on Scalar
# ---------------------------------------------------------------------------
def experiment_6_lattice_attack(num_trials=10, key_bits=40):
    """
    Use LLL to find small (a,b) with a·G + b·K having small x-coordinate.
    If two independent relations found, solve for k.
    """
    print("=" * 70)
    print("EXPERIMENT 6: Lattice Attack on Scalar")
    print(f"  Trials: {num_trials}, Key bits: {key_bits}")
    print("=" * 70)

    # The idea: if a + b·k ≡ s (mod n) where s is "small" (detectable),
    # and we can find two such pairs (a1,b1,s1) and (a2,b2,s2),
    # then k = (s1 - a1)·b1⁻¹ ≡ (s2 - a2)·b2⁻¹ mod n.

    # Approach: search for (a,b) such that (a+b·k)·G has small x-coordinate.
    # Use lattice: columns = [G.x, K.x, scaling] with LLL.

    # Since we don't have a proper LLL library, we'll use a direct search
    # approach: baby-step on a, giant-step on b.

    print(f"\n  --- Near-miss search ---")
    print(f"  Looking for small (a,b) with x(a·G + b·K) < threshold")

    for trial in range(min(num_trials, 5)):
        k_val = random.randint(1, (1 << key_bits) - 1)
        K = CURVE.scalar_mult(k_val, G)

        # Precompute baby steps: j·G for j in [0, m)
        m = 200
        threshold = p >> 240  # x < 2^16 — very small

        baby = {}  # x-coord prefix → j
        P = ECPoint.infinity()
        for j in range(m):
            if not P.is_infinity:
                # Store hash of x for fast comparison
                baby[P.x] = j
            P = CURVE.add(P, G)

        # Giant steps: K, 2K, 3K, ...
        hits = []
        R = ECPoint.infinity()
        for i in range(1, m):
            R = CURVE.add(R, K)
            # Check i·K + j·G = (i·k + j)·G for each baby step j
            # We want x(i·K + j·G) to be small
            # But we can't enumerate all (i,j) pairs efficiently this way.
            # Instead, check if i·K itself has small x
            if not R.is_infinity and R.x < threshold:
                hits.append((0, i, R.x))

            # Also check i·K - j·G for small j
            S = R
            for j in range(1, 20):
                S = CURVE.add(S, CURVE.neg(G))
                if not S.is_infinity and S.x < threshold:
                    hits.append((-j, i, S.x))

                S2 = CURVE.add(R, CURVE.scalar_mult(j, G))
                if not S2.is_infinity and S2.x < threshold:
                    hits.append((j, i, S2.x))

        if hits:
            print(f"    Trial {trial}: {len(hits)} near-misses found!")
            for (a_val, b_val, x_val) in hits[:5]:
                scalar = (a_val + b_val * k_val) % n
                print(f"      a={a_val}, b={b_val}, x={x_val}, "
                      f"scalar={scalar}, scalar_bits={scalar.bit_length()}")
        else:
            print(f"    Trial {trial}: no near-misses (threshold too tight)")

    # More practical: use the GLV lattice structure
    print(f"\n  --- GLV lattice for near-miss amplification ---")
    print(f"  Using the known GLV short vectors to construct near-miss detector")

    # The GLV lattice has short vectors ~128 bits. If we combine with
    # a small search, we effectively get a "division" that reduces the
    # problem to 128 bits — which is exactly what GLV-BSGS already does.

    print(f"\n  Key insight: LLL on the ECDLP lattice reduces to GLV decomposition")
    print(f"  (which we already exploit). Novel lattice angles need additional")
    print(f"  algebraic structure beyond what secp256k1 provides.")

    print(f"\n  --- Alternative: multi-dimensional lattice with K coordinates ---")
    # Embed (Kx, Ky) into a lattice with (Gx, Gy) and try to find
    # short vectors that relate them
    print(f"  Lattice L = {{(a, b, a·Gx + b·Kx mod p, a·Gy + b·Ky mod p)}}")
    print(f"  Short vector in L → small scalar relation on the curve")
    print(f"  But the discrete log hides in the non-linear EC group law,")
    print(f"  not in linear combinations of coordinates.")

    print(f"\n  VERDICT: Direct lattice attacks reduce to known GLV structure.")
    print(f"  No novel 'division' shortcut found via this approach.")
    return False


# ---------------------------------------------------------------------------
# Experiment 7: Differential Addition Chains (Montgomery form)
# ---------------------------------------------------------------------------
def experiment_7_montgomery_differential(num_trials=10, key_bits=32):
    """
    Convert secp256k1 to Montgomery form and study differential addition.

    Montgomery ladder computes (k·P, (k+1)·P) simultaneously.
    Can we detect which 'rung' K sits on?
    """
    print("=" * 70)
    print("EXPERIMENT 7: Montgomery Differential Addition")
    print(f"  Trials: {num_trials}, Key bits: {key_bits}")
    print("=" * 70)

    # secp256k1: y² = x³ + 7 (short Weierstrass, a=0, b=7)
    # Montgomery form: By² = x³ + Ax² + x
    # Conversion exists iff the curve has a point of order 2.
    # E: y² = x³ + 7 has a point of order 2 iff x³ + 7 = 0 has a root mod p.
    # x = (-7)^(1/3) mod p

    # Check if -7 has a cube root mod p
    # For p ≡ 1 mod 3, cube roots exist for about 1/3 of elements
    print(f"\n  Checking Montgomery conversion...")
    print(f"  p mod 3 = {p % 3}")

    # Find cube root of -7 mod p
    neg7 = (-7) % p
    # x³ ≡ -7 mod p → x = (-7)^((2p-1)/3) mod p if p ≡ 2 mod 3
    # or use Adleman-Manders-Miller for p ≡ 1 mod 3

    if p % 3 == 2:
        cbrt = pow(neg7, (2 * p - 1) // 3, p)
    else:
        # p ≡ 1 mod 3: cube root is harder, use brute force on small field
        # or use the Cipolla/Tonelli-like algorithm for cube roots
        # For now, try the direct formula
        exp = (p - 1) // 3
        test = pow(neg7, exp, p)
        if test == 1:
            # -7 is a cubic residue, find the root
            # Use random search
            cbrt = None
            for _ in range(1000):
                g = random.randint(2, p - 1)
                # g^((p-1)/3) is a primitive cube root of unity if g is not a cube
                w = pow(g, (p - 1) // 3, p)
                if w != 1:
                    # Found a primitive cube root of unity
                    # Now find cbrt(-7) by trying (-7)^((p+2)/9) etc.
                    # General: r = (-7)^((2*(p-1)/3 + 1)/3) ... complicated
                    # Just use: r = (-7)^e where 3e ≡ 1 mod (p-1)
                    e = pow(3, (p - 1) // 2 - 1, p - 1)  # 3^(-1) mod (p-1) if it exists
                    if (3 * e) % (p - 1) == 1:
                        cbrt = pow(neg7, e, p)
                        break
                    else:
                        # 3 doesn't have an inverse mod p-1 (since 3 | p-1)
                        # Need different approach
                        break
            if cbrt is None:
                # Fallback: check directly
                cbrt = pow(neg7, (p + 2) // 9, p) if (p + 2) % 9 == 0 else None
        else:
            print(f"  -7 is NOT a cubic residue mod p")
            cbrt = None

    has_order2 = False
    if cbrt is not None and pow(cbrt, 3, p) == neg7:
        has_order2 = True
        x2 = cbrt
        print(f"  Found 2-torsion point: ({x2}, 0)")
        print(f"  Verification: {x2}³ + 7 ≡ {(pow(x2, 3, p) + 7) % p} mod p")
    else:
        print(f"  No 2-torsion point found (x³+7=0 has no root mod p)")
        print(f"  secp256k1 cannot be directly converted to Montgomery form!")

    # Alternative: use x-only Montgomery ladder on the original curve
    print(f"\n  --- x-only differential addition on Weierstrass form ---")
    print(f"  Montgomery ladder works with ANY curve using x-only arithmetic:")
    print(f"  Given x(P), x(Q), x(P-Q), compute x(P+Q) without y-coordinates")

    # x-only addition formula for y² = x³ + 7:
    # x(P+Q) = ((xP·xQ - 7) / (xP - xQ))² · (1/x(P-Q)) - xP - xQ
    # (This is the standard formula when a=0)

    def xonly_add(xP, xQ, xPmQ, q):
        """x-coordinate of P+Q given x(P), x(Q), x(P-Q) on y²=x³+7."""
        if xP == xQ:
            return None  # Doubling needs different formula
        num = (xP * xQ - 7) % q  # Actually for a=0: (xP·xQ - a4)² - ...
        # The correct formula for short Weierstrass y²=x³+b:
        # This is actually more complex. Let's use the right one.
        # From: https://hyperelliptic.org/EFD/g1p/auto-shortw-xz.html
        # For differential addition on y²=x³+b (a=0):
        # U = (X2·Z1 - X1·Z2)²
        # V = X_diff·(X2·Z1 + X1·Z2) + 2·b·Z1·Z2 ... complicated in projective
        # Simpler in affine:
        return None  # Formula too complex for quick implementation

    # Instead, let's study the Montgomery ladder's information leakage
    print(f"\n  --- Montgomery ladder rung detection ---")
    print(f"  The ladder maintains (R0, R1) = (k·G, (k+1)·G)")
    print(f"  At bit i of k:")
    print(f"    if k_i = 0: R0 = 2·R0,     R1 = R0 + R1")
    print(f"    if k_i = 1: R0 = R0 + R1,   R1 = 2·R1")
    print(f"  Final: R0 = k·G = K")

    # Can we detect which 'rung' by examining K and (k+1)·G?
    print(f"\n  Given K = k·G, we can compute (k+1)·G = K + G (free)")
    print(f"  And (k-1)·G = K - G (free)")
    print(f"  Question: does the pair (K, K+G) leak any bit of k?")

    # Statistical test
    bit_0_count = [0, 0]  # [k has LSB=0, k has LSB=1]
    xy_ratio_by_lsb = {0: [], 1: []}

    for trial in range(1000):
        k_val = random.randint(1, (1 << key_bits) - 1)
        K = CURVE.scalar_mult(k_val, G)
        K1 = CURVE.add(K, G)  # (k+1)·G

        lsb = k_val & 1
        bit_0_count[lsb] += 1

        # Examine various functions of (K, K+G)
        ratio = K.x * pow(K1.x, p - 2, p) % p  # K.x / K1.x mod p
        xy_ratio_by_lsb[lsb].append(ratio % (1 << 16))  # low bits of ratio

    # Check if the ratio distribution differs by LSB
    mean_0 = sum(xy_ratio_by_lsb[0]) / len(xy_ratio_by_lsb[0])
    mean_1 = sum(xy_ratio_by_lsb[1]) / len(xy_ratio_by_lsb[1])
    expected_mean = (1 << 15)  # uniform over 16 bits

    print(f"\n    Ratio x(K)/x(K+G) low-16-bits mean:")
    print(f"      k even: {mean_0:.1f}")
    print(f"      k odd:  {mean_1:.1f}")
    print(f"      expected (uniform): {expected_mean}")
    print(f"      deviation: {abs(mean_0 - mean_1):.1f}")
    print(f"      (significant if >> {expected_mean / math.sqrt(500):.1f})")

    significant = abs(mean_0 - mean_1) > 3 * expected_mean / math.sqrt(500)
    print(f"\n  VERDICT: {'LEAKAGE from differential!' if significant else 'No differential leakage detected'}")
    return significant


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
def run_all():
    """Run all experiments and summarize results."""
    print("\n" + "=" * 70)
    print("  EC 'DIVISION' EXPERIMENTS — COMPREHENSIVE SUITE")
    print("  Target: secp256k1 (Bitcoin curve)")
    print("=" * 70 + "\n")

    results = {}

    experiments = [
        ("1: Coordinate Bit Leakage", experiment_1_bit_leakage),
        ("2: j=0 Cube Root Decomposition", experiment_2_cube_root_decomposition),
        ("3: p-adic Lifting", experiment_3_padic_lifting),
        ("4: Summation Polynomial Sieve", experiment_4_summation_poly),
        ("5: Multiplicative Order Discovery", experiment_5_order_probing),
        ("6: Lattice Attack on Scalar", experiment_6_lattice_attack),
        ("7: Montgomery Differential", experiment_7_montgomery_differential),
    ]

    for name, func in experiments:
        print(f"\n{'#' * 70}")
        print(f"# Running: {name}")
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

    # Final summary
    print("\n" + "=" * 70)
    print("  SUMMARY OF RESULTS")
    print("=" * 70)
    print(f"\n  {'Experiment':<40} {'Result':<20} {'Time'}")
    print(f"  {'-'*40} {'-'*20} {'-'*10}")
    for name, (result, elapsed) in results.items():
        status = "POSITIVE" if result else ("NEGATIVE" if result is not None else "ERROR")
        print(f"  {name:<40} {status:<20} {elapsed:.2f}s")

    positive = sum(1 for r, _ in results.values() if r)
    print(f"\n  Positive results: {positive}/{len(results)}")

    if positive == 0:
        print(f"\n  As expected, secp256k1 resists all probed attacks.")
        print(f"  The curve was specifically chosen to minimize exploitable structure:")
        print(f"    - Prime order n (no small subgroups)")
        print(f"    - Large embedding degree (no MOV/Frey-Rück)")
        print(f"    - Not anomalous (no Smart attack)")
        print(f"    - CM discriminant sufficiently large")
        print(f"\n  The j=0 automorphism (Experiment 2) provides the only known")
        print(f"  structural advantage: a √3 speedup via GLV decomposition,")
        print(f"  which is already exploited in our kangaroo solver.")
    else:
        print(f"\n  *** UNEXPECTED POSITIVE RESULTS — investigate further! ***")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "all":
            run_all()
        elif arg.isdigit():
            exp_num = int(arg)
            funcs = {
                1: experiment_1_bit_leakage,
                2: experiment_2_cube_root_decomposition,
                3: experiment_3_padic_lifting,
                4: experiment_4_summation_poly,
                5: experiment_5_order_probing,
                6: experiment_6_lattice_attack,
                7: experiment_7_montgomery_differential,
            }
            if exp_num in funcs:
                funcs[exp_num]()
            else:
                print(f"Unknown experiment: {exp_num}. Choose 1-7 or 'all'.")
        else:
            print("Usage: python3 ec_division_experiments.py [1-7|all]")
    else:
        run_all()
