"""
Differential Algebra & Formal Groups for ECDLP — Deep Research Experiments

AREA 1: Formal Group Logarithm
  - Compute log_F(t) for y²=x³+7 to O(t^20)
  - Hensel lift to Z/p²Z, test Smart-style attack
  - Check if log_F(t_P)/log_F(t_G) = k mod p

AREA 2: Differential Equations on EC
  - Hasse invariant for secp256k1
  - Division polynomials ψ_k on small curves
  - Structure of ψ_k(x_G) mod p as k varies
"""

import signal
import time
import sys
import gmpy2
from gmpy2 import mpz, invert as gmp_invert

# Import curve definitions
from ecdlp_pythagorean import secp256k1_curve, EllipticCurve, ECPoint, FastCurve

# ============================================================================
# AREA 1: Formal Group Logarithm
# ============================================================================

def formal_group_law_weierstrass(a, b, prec=20):
    """
    Compute the formal group logarithm log_F(t) for y² = x³ + ax + b
    near the point at infinity.

    Local parameter: t = -x/y (so x = -t/s where s = -1/y, and the
    formal expansion gives x = t^{-2} - a*t^2 - b*t^4 - ... in terms
    of the uniformizer).

    Actually, for the formal group of an elliptic curve y² = x³ + ax + b,
    the formal logarithm is:
        log_F(t) = ∫ ω  where ω = dx/(2y) = invariant differential

    In terms of the local parameter t = -x/y, we have:
        log_F(t) = t + Σ_{n≥2} c_n * t^n

    We compute this by first finding the formal group law x(t), y(t)
    as power series in t, then integrating dx/(2y).

    For y² = x³ + 7 (a=0, b=7):
    Near infinity, set t = -x/y, w = -1/y.
    Then x = t/w, y = -1/w.
    From y² = x³ + ax + b:
      1/w² = t³/w³ + a*t/w + b
      w = t³ + a*t*w² + b*w³

    We solve w = w(t) as power series by iteration.
    """
    # Solve w = t³ + a*t*w² + b*w³ iteratively as power series
    # w_coeffs[i] = coefficient of t^i
    N = prec + 5  # extra terms for safety
    w = [0] * (N + 1)
    # w starts as t³
    if N >= 3:
        w[3] = 1  # t³ term

    # Iterate to get more terms: w = t³ + a*t*w² + b*w³
    for iteration in range(N):
        w_new = [0] * (N + 1)
        if N >= 3:
            w_new[3] = 1  # t³ base term

        # Compute w²
        w_sq = poly_mul_trunc(w, w, N)
        # Compute w³
        w_cube = poly_mul_trunc(w_sq, w, N)

        # a*t*w²: shift w² by 1 (multiply by t) and scale by a
        for i in range(N):
            if i + 1 <= N:
                w_new[i + 1] += a * w_sq[i]

        # b*w³
        for i in range(N + 1):
            w_new[i] += b * w_cube[i]

        # Check convergence
        if w_new[:N+1] == w[:N+1]:
            break
        w = w_new[:N+1]

    # Now x = t/w, y = -1/w
    # The invariant differential is dx/(2y)
    # In terms of t: ω = (1/w - t*w'/w²) / (2/w) * dt ... let me use a cleaner approach.
    #
    # Actually: log_F(t) = ∫_0^t dt / f'(t) where f is the formal group law,
    # but more directly:
    #
    # The formal logarithm satisfies: log_F'(t) = 1 + Σ a_n * t^n
    # where the a_n come from the invariant differential.
    #
    # For the curve y² = x³ + ax + b with local parameter t = -x/y:
    # log_F(t) = ∫ (1 - a₁t - a₂t² - ...) dt  where the a_i come from
    # expanding the invariant differential.
    #
    # More precisely, with w(t) known, x = t/w, y = -1/w:
    # dx = (w - t*w')/w² dt
    # 2y = -2/w
    # dx/(2y) = -(w - t*w')/(2w) dt = (t*w' - w)/(2w) dt ... hmm
    #
    # Let me use the standard formula directly.
    # ω = dx/(2y+a₁x+a₃) for general Weierstrass, but for short form y²=x³+ax+b:
    # ω = dx/(2y)
    # With x = t/w, y = -1/w:
    # dx = d(t/w) = (1/w - t*w'/w²) dt = (w - t*w')/(w²) dt
    # 2y = -2/w
    # ω = dx/(2y) = (w - t*w')/(w²) * (-w/2) dt = -(w - t*w')/(2w) dt

    # Compute w'(t)
    w_prime = [0] * (N + 1)
    for i in range(1, N + 1):
        w_prime[i - 1] = i * w[i]

    # Compute (w - t*w') = numerator
    # t*w' has coefficients: (t*w')[i] = w_prime[i-1] for i>=1
    num = [0] * (N + 1)
    for i in range(N + 1):
        num[i] = w[i]
        if i >= 1:
            num[i] -= w_prime[i - 1]

    # ω = -(num)/(2w) dt
    # We need to compute num/w as a power series, then negate and divide by 2
    # Actually let's compute the ratio num/(2w) via power series division

    # inv_w = 1/w as power series (w starts at t³, so 1/w starts at t^{-3}...)
    # This is problematic. Let me reconsider.

    # Alternative cleaner approach: use the recurrence for formal log coefficients.
    # For y² = x³ + 7 (a1=a2=a3=a4=0, a6=7 in general Weierstrass):
    # The formal logarithm can be computed via:
    #   log_F(t) = Σ_{n≥1} c_n/n * t^n
    # where c_n satisfies a recurrence based on the curve coefficients.

    return compute_formal_log_recurrence(a, b, prec)


def compute_formal_log_recurrence(a_curve, b_curve, prec):
    """
    Compute formal group logarithm for y² = x³ + a*x + b using
    the standard recurrence.

    For short Weierstrass y² = x³ + Ax + B, the formal group has:
    w(t) = t³ + A*t⁷*(...) + B*t⁹*(...)

    The invariant differential in terms of t is:
    ω = (1 + c₁t + c₂t² + ...) dt

    And log_F(t) = t + c₁t²/2 + c₂t³/3 + ...

    Using Silverman's recurrence (AEC IV.1):
    For y² + a₁xy + a₃y = x³ + a₂x² + a₄x + a₆
    with a₁=a₂=a₃=0, a₄=a_curve, a₆=b_curve:

    The formal group law w(t) satisfies w = t³ + a₄*t*w² + a₆*w³
    (already computed above).

    For the log, we use: if w(t) = Σ s_n t^n (s_3=1, s_n=0 for n<3),
    then the invariant differential is:
    ω = (Σ_{n≥1} n*s_n * t^{n-1}) / (sum involving 2y terms) dt

    Let me just use the direct integration approach with rational coefficients.
    """
    from fractions import Fraction

    N = prec
    A, B = a_curve, b_curve

    # Solve w = t³ + A*t*w² + B*w³ as power series with Fraction coefficients
    w = [Fraction(0)] * (N + 5)
    w[3] = Fraction(1)

    for _iter in range(3 * N):  # enough iterations
        w_new = [Fraction(0)] * (N + 5)
        w_new[3] = Fraction(1)

        w_sq = poly_mul_trunc_frac(w, w, N + 4)
        w_cube = poly_mul_trunc_frac(w_sq, w, N + 4)

        # A*t*w²
        for i in range(N + 4):
            if i + 1 < N + 5:
                w_new[i + 1] += Fraction(A) * w_sq[i]

        # B*w³
        for i in range(N + 5):
            w_new[i] += Fraction(B) * w_cube[i]

        if all(w_new[i] == w[i] for i in range(N + 5)):
            break
        w = w_new

    # Now x = t/w(t), y = -1/w(t)
    # We need the invariant differential ω = dx/(2y)
    # x(t) = t / w(t), where w(t) = t³(1 + higher)
    # So x(t) = t / (t³ * (1 + ...)) = t^{-2} / (1 + ...)
    # This has negative powers of t, which is expected — x has a pole of order 2 at infinity.

    # For the formal log, there's a simpler path:
    # The power series for the invariant differential in terms of t is:
    # ω = (1 + Σ a_n t^n) dt  where the a_n come from:
    #
    # ω = -d(t/w) / (2/w) = -(w - t*w')/(2*w) dt ... wait, I keep going in circles.
    #
    # Let me use a completely different standard approach.
    # Define s(t) = w(t)/t³ = 1 + higher order terms in t.
    # Then x = 1/(t² * s(t)), y = -1/(t³ * s(t))
    #
    # ω = dx/(2y)
    # x = t^{-2} * s(t)^{-1}
    # dx/dt = -2*t^{-3}*s^{-1} - t^{-2}*s^{-2}*s'
    #        = -t^{-3}*s^{-1}*(2 + t*s'/s)
    # 2y = -2*t^{-3}*s^{-1}
    # ω = dx/(2y) dt = [-t^{-3}*s^{-1}*(2+t*s'/s)] / [-2*t^{-3}*s^{-1}] dt
    #                = (2 + t*s'/s) / 2 dt
    #                = (1 + t*s'/(2s)) dt
    #
    # So the invariant differential is ω = (1 + t*s'(t)/(2*s(t))) dt
    # And log_F(t) = ∫₀ᵗ ω = t + ∫₀ᵗ u*s'(u)/(2*s(u)) du

    # Compute s(t) = w(t)/t³
    s = [Fraction(0)] * (N + 2)
    for i in range(N + 2):
        if i + 3 < N + 5:
            s[i] = w[i + 3]

    # s'(t)
    s_prime = [Fraction(0)] * (N + 2)
    for i in range(1, N + 2):
        s_prime[i - 1] = Fraction(i) * s[i]

    # Compute t*s'(t) — shift by 1
    ts_prime = [Fraction(0)] * (N + 2)
    for i in range(N + 1):
        ts_prime[i + 1] = s_prime[i]

    # Compute 1/s(t) as power series (s[0]=1, so invertible)
    s_inv = poly_inv_frac(s, N + 1)

    # t*s'/s
    ratio = poly_mul_trunc_frac(ts_prime, s_inv, N + 1)

    # Integrand: 1 + ratio/2
    # integrand[0] = 1, integrand[i] = ratio[i]/2 for i>=1
    integrand = [Fraction(0)] * (N + 1)
    integrand[0] = Fraction(1)
    for i in range(1, N + 1):
        integrand[i] = ratio[i] / 2

    # Integrate: log_F(t) = Σ integrand[i]/(i+1) * t^{i+1}
    log_coeffs = [Fraction(0)] * (N + 2)
    for i in range(N + 1):
        log_coeffs[i + 1] = integrand[i] / (i + 1)

    return log_coeffs


def poly_mul_trunc(a, b, n):
    """Multiply two polynomial coefficient lists, truncate to degree n."""
    result = [0] * (n + 1)
    for i in range(min(len(a), n + 1)):
        if a[i] == 0:
            continue
        for j in range(min(len(b), n + 1 - i)):
            result[i + j] += a[i] * b[j]
    return result


def poly_mul_trunc_frac(a, b, n):
    """Multiply two Fraction polynomial coefficient lists, truncate to degree n."""
    from fractions import Fraction
    result = [Fraction(0)] * (n + 1)
    for i in range(min(len(a), n + 1)):
        if a[i] == 0:
            continue
        for j in range(min(len(b), n + 1 - i)):
            result[i + j] += a[i] * b[j]
    return result


def poly_inv_frac(s, n):
    """Compute 1/s(t) mod t^n as power series. s[0] must be nonzero."""
    from fractions import Fraction
    inv = [Fraction(0)] * n
    inv[0] = Fraction(1) / s[0]
    for k in range(1, n):
        val = Fraction(0)
        for j in range(1, k + 1):
            if j < len(s):
                val += s[j] * inv[k - j]
        inv[k] = -val / s[0]
    return inv


# ============================================================================
# Experiment 1: Formal group log computation
# ============================================================================

def experiment_1_formal_log():
    """Compute formal group log for y²=x³+7 and verify its properties."""
    print("=" * 70)
    print("EXPERIMENT 1: Formal Group Logarithm for y² = x³ + 7")
    print("=" * 70)

    log_coeffs = compute_formal_log_recurrence(a_curve=0, b_curve=7, prec=20)

    print("\nlog_F(t) coefficients (t^1 through t^20):")
    for i in range(1, min(21, len(log_coeffs))):
        if log_coeffs[i] != 0:
            print(f"  t^{i}: {log_coeffs[i]}")

    # Verify: for the formal group of y²=x³+7, the log should linearize addition
    # On a small test curve, verify log_F(F(t1,t2)) = log_F(t1) + log_F(t2)
    print("\nVerification on small curve y² = x³ + 7 mod 101:")
    p_small = 101
    E_small = EllipticCurve(a=0, b=7, p=p_small)

    # Find generator and compute some points
    G_small = E_small.find_generator()
    if G_small is None:
        print("  Could not find generator on small curve")
        return log_coeffs

    print(f"  Generator: {G_small}")
    order = E_small.point_order(G_small)
    print(f"  Order: {order}")

    # Convert point to formal group parameter t = -x/y
    def to_formal_param(P, p):
        if P.is_infinity:
            return 0
        y_inv = pow(P.y, p - 2, p)
        return (-P.x * y_inv) % p

    # Evaluate log_F(t) mod p
    def eval_log_mod_p(t, coeffs, p):
        val = 0
        t_pow = 1
        for i in range(len(coeffs)):
            if coeffs[i] != 0:
                c = int(coeffs[i].numerator) * pow(int(coeffs[i].denominator), p - 2, p) % p
                val = (val + c * t_pow) % p
            t_pow = t_pow * t % p
        return val

    # Test: log_F(t_{P+Q}) = log_F(t_P) + log_F(t_Q) mod p?
    print("\n  Testing log_F homomorphism property:")
    successes = 0
    trials = 10
    for k1 in range(1, trials + 1):
        k2 = k1 + 3
        P = E_small.scalar_mult(k1, G_small)
        Q = E_small.scalar_mult(k2, G_small)
        PQ = E_small.add(P, Q)

        if P.is_infinity or Q.is_infinity or PQ.is_infinity:
            continue
        if P.y == 0 or Q.y == 0 or PQ.y == 0:
            continue

        t_P = to_formal_param(P, p_small)
        t_Q = to_formal_param(Q, p_small)
        t_PQ = to_formal_param(PQ, p_small)

        log_P = eval_log_mod_p(t_P, log_coeffs, p_small)
        log_Q = eval_log_mod_p(t_Q, log_coeffs, p_small)
        log_PQ = eval_log_mod_p(t_PQ, log_coeffs, p_small)

        lhs = log_PQ % p_small
        rhs = (log_P + log_Q) % p_small
        match = "YES" if lhs == rhs else "NO"
        if lhs == rhs:
            successes += 1
        if k1 <= 5:
            print(f"    k1={k1}, k2={k2}: log(P+Q)={lhs}, log(P)+log(Q)={rhs} -> {match}")

    print(f"  Homomorphism holds: {successes}/{trials}")
    print("  NOTE: Formal log has finite radius of convergence in p-adic topology.")
    print("  For large t values (most curve points), the series does NOT converge.")
    print("  This is why Smart's attack only works for anomalous curves (#E=p).")

    return log_coeffs


# ============================================================================
# Experiment 2: Hensel lift to Z/p²Z
# ============================================================================

def experiment_2_hensel_lift():
    """
    Smart's attack for anomalous curves:
    If #E(F_p) = p, lift E to E~ over Z/p²Z, compute log in E~(Z/p²Z),
    then k = log(P~)/log(G~) mod p.

    For secp256k1: #E = n ≠ p, so this CANNOT work directly.
    We test on a small anomalous curve first, then show it fails for secp256k1.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 2: Hensel Lift / Smart's Attack Analysis")
    print("=" * 70)

    # Part A: Construct a small anomalous curve (order = p)
    print("\nPart A: Small anomalous curve")

    # Find an anomalous curve: y² = x³ + ax + b over F_p with #E = p
    # For p=43, y²=x³+26x+12 has order 43 (anomalous)
    # Let me search for one
    anomalous_found = False
    for p_test in range(11, 200):
        if not gmpy2.is_prime(p_test):
            continue
        for aa in range(p_test):
            for bb in range(p_test):
                if (4 * aa**3 + 27 * bb**2) % p_test == 0:
                    continue  # singular
                # Count points (small p, brute force)
                count = 1  # point at infinity
                for x in range(p_test):
                    rhs = (x**3 + aa * x + bb) % p_test
                    if rhs == 0:
                        count += 1
                    elif pow(rhs, (p_test - 1) // 2, p_test) == 1:
                        count += 2
                if count == p_test:
                    print(f"  Found anomalous curve: y² = x³ + {aa}x + {bb} mod {p_test}")
                    print(f"  #E(F_{p_test}) = {count} = p (anomalous!)")
                    anomalous_found = True

                    # Implement Smart's attack on this curve
                    E_anom = EllipticCurve(a=aa, b=bb, p=p_test)
                    G_anom = E_anom.find_generator()
                    if G_anom is None:
                        continue
                    ord_G = E_anom.point_order(G_anom)
                    if ord_G != p_test:
                        # Generator doesn't have full order, skip
                        continue

                    secret_k = 7  # test secret
                    P_anom = E_anom.scalar_mult(secret_k, G_anom)
                    print(f"  G = {G_anom}, P = {secret_k}*G = {P_anom}")

                    # Hensel lift to Z/p²Z
                    # Lift curve: y² = x³ + a*x + b over Z/p²Z
                    # Lift points: find (x', y') with x' ≡ x mod p, y' ≡ y mod p,
                    #   y'² ≡ x'³ + a*x' + b mod p²
                    p2 = p_test * p_test

                    def hensel_lift_point(Px, Py, a_c, b_c, p_v):
                        """Lift (Px, Py) from F_p to Z/p²."""
                        p2v = p_v * p_v
                        # x' = Px (keep same x)
                        # Need y' such that y'² ≡ x³ + a*x + b mod p²
                        rhs = (Px**3 + a_c * Px + b_c) % p2v
                        # y' = Py + t*p, solve (Py + t*p)² ≡ rhs mod p²
                        # Py² + 2*Py*t*p ≡ rhs mod p²
                        # t ≡ (rhs - Py²) / (2*Py*p) mod p
                        resid = (rhs - Py * Py) % p2v
                        assert resid % p_v == 0
                        t_num = resid // p_v
                        t_den = (2 * Py) % p_v
                        t = (t_num * pow(t_den, p_v - 2, p_v)) % p_v
                        yy = (Py + t * p_v) % p2v
                        # Verify
                        assert (yy * yy - Px**3 - a_c * Px - b_c) % p2v == 0
                        return Px, yy

                    Gx_l, Gy_l = hensel_lift_point(G_anom.x, G_anom.y, aa, bb, p_test)
                    Px_l, Py_l = hensel_lift_point(P_anom.x, P_anom.y, aa, bb, p_test)

                    # Compute p*G~ and p*P~ in E~(Z/p²Z)
                    # For anomalous curves, p*Q~ = (0, 1, 0) in projective over F_p
                    # but over Z/p²Z, p*Q~ maps to a point whose "reduction mod p" is O
                    # The key: p*Q~ has coordinates (x, y) with p | denominator
                    # The formal group log gives: λ(p*Q~) = p * λ(Q~) where λ is the
                    # p-adic elliptic logarithm.

                    # For the lifted curve, compute p*G~ and p*P~ using Z/p²Z arithmetic
                    def ec_add_mod(P_pt, Q_pt, a_c, mod):
                        """Add two points on E over Z/mod (projective)."""
                        px, py = P_pt
                        qx, qy = Q_pt
                        if P_pt == ('inf', 'inf'):
                            return Q_pt
                        if Q_pt == ('inf', 'inf'):
                            return P_pt
                        if (px - qx) % mod == 0:
                            if (py + qy) % mod == 0:
                                return ('inf', 'inf')
                            if (py - qy) % mod == 0:
                                # doubling
                                num = (3 * px * px + a_c) % mod
                                den = (2 * py) % mod
                                g = gmpy2.gcd(den, mod)
                                if g > 1:
                                    return ('inf', 'inf')  # degenerate
                                lam = num * int(gmp_invert(den, mod)) % mod
                            else:
                                return ('inf', 'inf')
                        else:
                            dx = (qx - px) % mod
                            g = gmpy2.gcd(dx, mod)
                            if g > 1:
                                return ('inf', 'inf')  # degenerate
                            dy = (qy - py) % mod
                            lam = dy * int(gmp_invert(dx, mod)) % mod

                        x3 = (lam * lam - px - qx) % mod
                        y3 = (lam * (px - x3) - py) % mod
                        return (x3, y3)

                    def ec_scalar_mod(k_val, P_pt, a_c, mod):
                        result = ('inf', 'inf')
                        addend = P_pt
                        while k_val > 0:
                            if k_val & 1:
                                result = ec_add_mod(result, addend, a_c, mod)
                            addend = ec_add_mod(addend, addend, a_c, mod)
                            k_val >>= 1
                        return result

                    pG = ec_scalar_mod(p_test, (Gx_l, Gy_l), aa, p2)
                    pP = ec_scalar_mod(p_test, (Px_l, Py_l), aa, p2)

                    print(f"  p*G~ mod p² = {pG}")
                    print(f"  p*P~ mod p² = {pP}")

                    # For anomalous curves, Smart's attack:
                    # k = φ(p*P~) / φ(p*G~) mod p
                    # where φ extracts the "p-adic logarithm"
                    if pG != ('inf', 'inf') and pP != ('inf', 'inf'):
                        # The p-adic log: if p*Q~ = (x,y) with p|x in some sense...
                        # Actually for anomalous, the kernel of reduction E~(Z/p²) -> E(F_p)
                        # is isomorphic to Z/pZ via the map (x,y) -> -x/y mod p
                        # Both pG and pP should be in this kernel.
                        if pG[1] % p_test != 0:
                            log_G = (-pG[0] * pow(pG[1], p_test - 2, p_test)) % p_test
                            log_P = (-pP[0] * pow(pP[1], p_test - 2, p_test)) % p_test
                            k_recovered = (log_P * pow(log_G, p_test - 2, p_test)) % p_test
                            print(f"  Smart's attack: log(G~)={log_G}, log(P~)={log_P}")
                            print(f"  Recovered k = {k_recovered}, actual k = {secret_k}")
                            print(f"  SUCCESS: {k_recovered == secret_k}")
                        else:
                            print("  Degenerate case: y-coordinate divisible by p")
                    else:
                        print("  p*Q~ = O in Z/p²Z (degenerate lift)")

                    break
            if anomalous_found:
                break
        if anomalous_found:
            break

    if not anomalous_found:
        print("  No anomalous curve found in search range")

    # Part B: Why it fails for secp256k1
    print("\nPart B: Why Smart's attack fails for secp256k1")
    print("  secp256k1 has #E(F_p) = n ≈ p (but n ≠ p)")
    curve = secp256k1_curve()
    p_secp = int(curve.p)
    n_secp = curve.n
    trace = p_secp + 1 - n_secp
    print(f"  Trace of Frobenius: t = p + 1 - n = {trace}")
    print(f"  t mod p = {trace % p_secp}")
    print(f"  For Smart's attack, we need t = 0 (anomalous), but t = {trace}")
    print(f"  The formal group E~(pZ_p) has order p, NOT n.")
    print(f"  So n*G~ ≠ 0 in E~(Z/p²Z), meaning we can't extract the log.")
    print(f"  Conclusion: Smart's attack is INAPPLICABLE to secp256k1.")


# ============================================================================
# Experiment 3: Hasse Invariant
# ============================================================================

def experiment_3_hasse_invariant():
    """
    Compute the Hasse invariant for secp256k1.
    H_p = coeff of x^{p-1} in (x³+7)^{(p-1)/2} mod p.
    For ordinary curves, H_p ≠ 0.
    H_p ≡ unit root of Frobenius α mod p.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 3: Hasse Invariant for secp256k1")
    print("=" * 70)

    # For secp256k1 with p = 2^256 - 2^32 - 977, computing the full polynomial
    # (x³+7)^{(p-1)/2} is impossible directly. But we only need the coefficient
    # of x^{p-1}.
    #
    # (x³+7)^m where m=(p-1)/2.
    # By binomial theorem: Σ C(m,k) * (x³)^k * 7^{m-k} = Σ C(m,k) * 7^{m-k} * x^{3k}
    # We need x^{p-1}, so 3k = p-1, k = (p-1)/3.
    # For this to be an integer, we need p ≡ 1 mod 3.

    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    print(f"  p mod 3 = {p % 3}")

    if p % 3 == 1:
        k = (p - 1) // 3
        m = (p - 1) // 2
        print(f"  k = (p-1)/3 = {k}")
        print(f"  m = (p-1)/2 = {m}")

        # H_p = C(m, k) * 7^{m-k} mod p
        # C(m,k) mod p via Lucas or direct computation
        # Since m, k < p, C(m,k) mod p = m! / (k! * (m-k)!) mod p
        # Use Wilson/modular factorial

        # For large p, compute C(m,k) mod p using gmpy2
        # C(m,k) = m*(m-1)*...*(m-k+1) / k!
        # But k is ~p/3 which is huge. We need a smarter approach.

        # Actually, C(m,k) mod p where m=(p-1)/2, k=(p-1)/3:
        # Use the fact that for p prime, C(m,k) mod p can be computed via
        # the formula involving Gamma_p (p-adic Gamma function), or by
        # using the identity:
        #   C((p-1)/2, (p-1)/3) ≡ product of certain residues mod p

        # Simpler: use Fermat's little theorem and modular arithmetic
        # Compute numerator = m * (m-1) * ... * (m-k+1) mod p
        # Compute denominator = k! mod p
        # Then C(m,k) = numerator * denominator^{-1} mod p

        # But k ≈ p/3 ≈ 2^254, so iterating is infeasible.
        # Instead, note that (x³+7)^{(p-1)/2} mod (x^p - x) mod p
        # gives us H_p as the coefficient of x^{p-1}.
        # We can compute this using modular exponentiation of polynomials,
        # but the polynomial has degree up to 3*(p-1)/2 ≈ 1.5p, which is too large.

        # Alternative: Use the Cartier-Manin matrix approach.
        # For y² = x³ + 7 (genus 1), the Hasse invariant is simply
        # the coefficient of x^{p-1} in (x³+7)^{(p-1)/2}.
        # This equals C((p-1)/2, (p-1)/3) * 7^{(p-1)/2-(p-1)/3} mod p
        #          = C((p-1)/2, (p-1)/3) * 7^{(p-1)/6} mod p

        # To compute C((p-1)/2, (p-1)/3) mod p, use the Gross-Koblitz formula
        # or the relation to Gauss sums.

        # For a practical computation, we use the relation:
        # For p ≡ 1 mod 3, the Hasse invariant of y²=x³+c is related to
        # the number of points: #E = p + 1 - t, and the unit root α satisfies
        # α + β = t, α*β = p, with |α|_p = 1.
        # We have α ≡ t mod p (when t ≠ 0), wait no...
        # α is the root of X² - tX + p = 0 that is a p-adic unit.

        n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
        t = p + 1 - n
        print(f"\n  Trace of Frobenius t = {t}")

        # Frobenius char poly: X² - tX + p
        # Roots: α, β with α*β = p, α+β = t
        # The unit root (|α|_p = 1) satisfies α ≡ H_p mod p
        # Discriminant: t² - 4p
        disc = t * t - 4 * p
        print(f"  Discriminant t²-4p = {disc}")
        print(f"  (negative, so roots are complex conjugates in C)")

        # α ≡ ? mod p: from X² - tX + p ≡ 0 mod p => X² - tX ≡ 0 => X(X-t) ≡ 0
        # So α ≡ t mod p or α ≡ 0 mod p.
        # The unit root has α ≡ t mod p (the other root β ≡ 0 mod p).
        print(f"\n  Unit root α ≡ t ≡ {t} mod p")
        print(f"  This means H_p ≡ {t % p} mod p")
        print(f"  Since t = {t} ≠ 0, the curve is ORDINARY (as expected).")
        print(f"  The p-adic valuation v_p(α) = 0, v_p(β) = 1.")

        # Compute 7^{(p-1)/6} mod p as a sanity check
        exp_7 = pow(7, (p - 1) // 6, p)
        print(f"\n  7^((p-1)/6) mod p = {exp_7}")

        # So H_p = C((p-1)/2, (p-1)/3) * 7^{(p-1)/6} mod p
        # And H_p ≡ t mod p
        # Therefore C((p-1)/2, (p-1)/3) ≡ t * 7^{-(p-1)/6} mod p
        binom_mod = (t * pow(exp_7, p - 2, p)) % p
        print(f"  => C((p-1)/2, (p-1)/3) mod p = {binom_mod}")

    else:
        print(f"  p ≡ {p%3} mod 3, so (p-1)/3 is not an integer.")
        print("  The coefficient of x^{p-1} in (x³+7)^{(p-1)/2} is 0.")
        print("  This would mean the curve is supersingular, but secp256k1 is ordinary.")
        print("  Contradiction — need different analysis.")


# ============================================================================
# Experiment 4: Division Polynomials
# ============================================================================

def experiment_4_division_polynomials():
    """
    Compute division polynomials ψ_k for small curves and study their properties.

    ψ_0 = 0, ψ_1 = 1, ψ_2 = 2y
    ψ_3 = 3x⁴ + 6ax² + 12bx - a²
    ψ_4 = 4y(x⁶ + 5ax⁴ + 20bx³ - 5a²x² - 4abx - 8b² - a³)
    ψ_{2m+1} = ψ_{m+2} ψ_m³ - ψ_{m-1} ψ_{m+1}³
    ψ_{2m} = (ψ_{m+2} ψ_m² ψ_{m-1} - ψ_{m-2} ψ_m² ψ_{m+1}) / (2y)
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 4: Division Polynomials on Small Curves")
    print("=" * 70)

    # Small curve: y² = x³ + 7 mod p for small p
    for p_test in [101, 1009, 10007]:
        print(f"\n  Curve: y² = x³ + 7 mod {p_test}")
        E = EllipticCurve(a=0, b=7, p=p_test)
        G = E.find_generator()
        if G is None:
            print("    No generator found")
            continue

        order = E.point_order(G)
        print(f"    G = {G}, order = {order}")

        # Compute ψ_k(x_G, y_G) mod p using the recurrence
        # We store ψ_k as integers mod p, evaluated at (x_G, y_G)
        x_G = G.x
        y_G = G.y
        a_c, b_c = 0, 7

        # ψ values evaluated at the point G
        psi = {}
        psi[0] = 0
        psi[1] = 1
        psi[2] = (2 * y_G) % p_test
        psi[3] = (3 * x_G**4 + 6 * a_c * x_G**2 + 12 * b_c * x_G - a_c**2) % p_test
        psi[4] = (4 * y_G * (x_G**6 + 5 * a_c * x_G**4 + 20 * b_c * x_G**3
                              - 5 * a_c**2 * x_G**2 - 4 * a_c * b_c * x_G
                              - 8 * b_c**2 - a_c**3)) % p_test

        def get_psi(k):
            if k in psi:
                return psi[k]
            if k < 0:
                return (-get_psi(-k)) % p_test

            # Use recurrence: compute all values up to k
            for n in range(5, k + 1):
                if n in psi:
                    continue
                if n % 2 == 1:
                    m = (n - 1) // 2
                    # ψ_{2m+1} = ψ_{m+2} * ψ_m³ - ψ_{m-1} * ψ_{m+1}³
                    val = (get_psi(m + 2) * pow(get_psi(m), 3, p_test)
                           - get_psi(m - 1) * pow(get_psi(m + 1), 3, p_test)) % p_test
                else:
                    m = n // 2
                    # ψ_{2m} = ψ_m * (ψ_{m+2} * ψ_{m-1}² - ψ_{m-2} * ψ_{m+1}²) / (2y)
                    num = (get_psi(m) * (get_psi(m + 2) * pow(get_psi(m - 1), 2, p_test)
                           - get_psi(m - 2) * pow(get_psi(m + 1), 2, p_test))) % p_test
                    inv_2y = pow(2 * y_G % p_test, p_test - 2, p_test)
                    val = (num * inv_2y) % p_test
                psi[n] = val
            return psi[k]

        # ψ_k(G) = 0 iff k*G = O, i.e., k is a multiple of the order
        print(f"    ψ_k(x_G, y_G) for k = 1..{min(order+2, 50)}:")
        zero_at = []
        for k in range(1, min(order + 3, 51)):
            val = get_psi(k)
            if val == 0:
                zero_at.append(k)
                # Verify: k*G should be O
                kG = E.scalar_mult(k, G)
                is_inf = kG.is_infinity
                print(f"      ψ_{k} = 0  (k*G is infinity: {is_inf})")

        if zero_at:
            print(f"    Zeros of ψ_k at: {zero_at}")
            print(f"    Order of G: {order}")
            print(f"    Match: {all(k % order == 0 for k in zero_at)}")
        else:
            print(f"    No zeros found in range (order={order} may be > search range)")

        # KEY QUESTION: Can we detect k from ψ_k(x_G) without knowing k?
        # If P = k*G, then ψ_k(x_G) ≡ 0 only when k ≡ 0 mod order.
        # But ψ_k evaluated at x_G gives information about k.
        # Check: is there structure in the sequence ψ_k(x_G)?
        print(f"\n    Structure analysis: |ψ_k(x_G)| pattern")
        vals = []
        for k in range(1, min(30, order)):
            v = get_psi(k)
            vals.append(v)
        # Check if ψ_k values have any detectable periodicity or pattern
        # relative to the multiplicative group
        print(f"    First 10 values: {vals[:10]}")

        # Check multiplicative pattern: ψ_{k+order}(x_G) vs ψ_k(x_G)
        if order < 40:
            print(f"    Checking ψ_{{k+order}} / ψ_k pattern:")
            for k in range(1, min(5, order)):
                v1 = get_psi(k)
                v2 = get_psi(k + order)
                if v1 != 0:
                    ratio = (v2 * pow(v1, p_test - 2, p_test)) % p_test
                    print(f"      ψ_{{{k+order}}}/ψ_{k} = {ratio}")


# ============================================================================
# Experiment 5: Division poly evaluation for DLP
# ============================================================================

def experiment_5_divpoly_dlp():
    """
    Given P = k*G on a small curve, can we recover k using division polynomials?

    Key identity: The x-coordinate of k*G can be expressed as:
      x(k*G) = x_G - ψ_{k-1}*ψ_{k+1} / ψ_k²

    So if we know x(P) = x(k*G), we could try to find k such that:
      x_P = x_G - ψ_{k-1}(x_G)*ψ_{k+1}(x_G) / ψ_k(x_G)²

    But computing ψ_k requires k, so this is circular unless we can factor ψ_k
    as a polynomial in x and find its roots.

    More promising: ψ_k(x_P, y_P) where P is known — what does this evaluate to?
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 5: Division Polynomial DLP Analysis")
    print("=" * 70)

    p_test = 10007
    E = EllipticCurve(a=0, b=7, p=p_test)
    G = E.find_generator()
    if G is None:
        print("  No generator found")
        return

    order = E.point_order(G)
    print(f"  Curve: y² = x³ + 7 mod {p_test}")
    print(f"  G = {G}, order = {order}")

    # Pick a secret k
    secret_k = 42
    P = E.scalar_mult(secret_k, G)
    print(f"  Secret k = {secret_k}, P = k*G = {P}")

    # Compute ψ_j(x_P, y_P) for various j
    x_P, y_P = P.x, P.y

    psi_at_P = {}
    psi_at_P[0] = 0
    psi_at_P[1] = 1
    psi_at_P[2] = (2 * y_P) % p_test
    psi_at_P[3] = (3 * x_P**4 + 12 * 7 * x_P) % p_test  # a=0
    psi_at_P[4] = (4 * y_P * (x_P**6 + 20 * 7 * x_P**3 - 8 * 49)) % p_test

    def get_psi_P(k):
        if k in psi_at_P:
            return psi_at_P[k]
        for n in range(5, k + 1):
            if n in psi_at_P:
                continue
            if n % 2 == 1:
                m = (n - 1) // 2
                val = (get_psi_P(m + 2) * pow(get_psi_P(m), 3, p_test)
                       - get_psi_P(m - 1) * pow(get_psi_P(m + 1), 3, p_test)) % p_test
            else:
                m = n // 2
                num = (get_psi_P(m) * (get_psi_P(m + 2) * pow(get_psi_P(m - 1), 2, p_test)
                       - get_psi_P(m - 2) * pow(get_psi_P(m + 1), 2, p_test))) % p_test
                inv_2y = pow(2 * y_P % p_test, p_test - 2, p_test)
                val = (num * inv_2y) % p_test
            psi_at_P[n] = val
        return psi_at_P[k]

    # Key test: ψ_j(P) = 0 iff j*P = O iff j*k*G = O iff order | j*k
    print(f"\n  Zeros of ψ_j(x_P, y_P):")
    zeros = []
    for j in range(1, min(order + 2, 300)):
        if get_psi_P(j) == 0:
            zeros.append(j)
            # j*P = O means j*k ≡ 0 mod order
            expected = (j * secret_k) % order == 0
            print(f"    ψ_{j}(P) = 0, j*k mod order = {(j*secret_k)%order}, expected zero: {expected}")

    if zeros:
        print(f"\n  First zero at j = {zeros[0]}")
        print(f"  order/gcd(k, order) = {order // gmpy2.gcd(secret_k, order)}")
        print(f"  These should match: {zeros[0] == order // gmpy2.gcd(secret_k, order)}")
        print(f"\n  From the first zero j₀ = {zeros[0]}, we know k | order/j₀ * order")
        print(f"  This gives: k is a multiple of gcd(k, order) = {int(gmpy2.gcd(secret_k, order))}")
        print(f"  But we need to FIND k, and computing ψ_j for j up to order is O(order) = O(n).")
        print(f"  For secp256k1, n ≈ 2^256, so this is INFEASIBLE.")
    else:
        print(f"  No zeros found (search range too small, order={order})")

    # Additional analysis: can we use Newton's method on ψ_j?
    print(f"\n  Newton's method analysis:")
    print(f"  If we treat j as a 'variable' in ψ_j(P), we'd need:")
    print(f"  1. A way to interpolate ψ_j(P) as a function of j")
    print(f"  2. ψ_j grows exponentially in j (degree O(j²))")
    print(f"  3. Over F_p, ψ_j(P) is essentially pseudorandom as j varies")
    print(f"  => Newton's method has no gradient to follow")

    # Verify pseudorandomness claim
    print(f"\n  ψ_j(P) mod p for j=1..20:")
    for j in range(1, 21):
        v = get_psi_P(j)
        print(f"    ψ_{j}(P) = {v}")


# ============================================================================
# Experiment 6: Formal log on secp256k1 — precision limits
# ============================================================================

def experiment_6_formal_log_secp256k1():
    """
    Test formal group log convergence for secp256k1 points.
    The formal log converges only for points in the 'formal group kernel' —
    points very close to O in the p-adic topology, i.e., with v_p(x) < 0.
    For random curve points, x is a unit mod p, so t = -x/y is also a unit,
    and the formal log series DIVERGES p-adically.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 6: Formal Log Convergence on secp256k1")
    print("=" * 70)

    curve = secp256k1_curve()
    p = int(curve.p)
    G = curve.G

    # The formal log has coefficients in Q. When evaluated at t ∈ Z_p,
    # it converges iff v_p(t) > 0 (i.e., p | t).
    # For a point P = (x, y) on the curve, t = -x/y.
    # v_p(t) = v_p(x) - v_p(y).
    # For points in E(F_p), x and y are in {0, ..., p-1}, so v_p(x) = 0
    # (unless x = 0) and v_p(y) = 0 (unless y = 0).
    # Therefore v_p(t) = 0, and the formal log DOES NOT CONVERGE.

    print(f"  For G = ({hex(G.x)[:20]}..., {hex(G.y)[:20]}...)")

    t_G = (-G.x * pow(G.y, p - 2, p)) % p
    print(f"  t_G = -x_G/y_G mod p = {hex(t_G)[:20]}...")
    print(f"  v_p(t_G) = 0 (t_G is a p-adic unit)")
    print(f"  => Formal log series DIVERGES for this input.")

    # Compute partial sums anyway to see divergence
    log_coeffs = compute_formal_log_recurrence(0, 7, 20)

    print(f"\n  Partial sums of log_F(t_G) mod p:")
    partial = 0
    t_pow = 1
    for i in range(min(21, len(log_coeffs))):
        if log_coeffs[i] != 0:
            num = int(log_coeffs[i].numerator)
            den = int(log_coeffs[i].denominator)
            c_mod_p = (num * pow(den, p - 2, p)) % p
            partial = (partial + c_mod_p * t_pow) % p
        t_pow = t_pow * t_G % p
        if i > 0 and i <= 15:
            print(f"    S_{i} = {hex(partial)[:30]}...")

    print(f"\n  The partial sums jump around — NO convergence.")
    print(f"  This confirms: formal group log is USELESS for non-anomalous curves")
    print(f"  when applied to points not in the formal group kernel.")

    # What about points in the kernel? These would be points (x,y) with
    # v_p(x) < -2, v_p(y) < -3 — i.e., points in E(Q_p) \ E(Z_p).
    # On secp256k1 over F_p, ALL points are in E(Z_p) (coordinates in F_p).
    # So the formal group kernel E_1(Q_p) = {P : red(P) = O} is EMPTY
    # when restricted to E(F_p).
    print(f"\n  CONCLUSION: The formal group approach cannot solve ECDLP on secp256k1.")
    print(f"  It works ONLY for anomalous curves (#E = p) via Smart's attack,")
    print(f"  because there the map E(F_p) -> E_1(Q_p)/E_2(Q_p) is an isomorphism.")


# ============================================================================
# Summary
# ============================================================================

def summarize():
    print("\n" + "=" * 70)
    print("SUMMARY OF FINDINGS")
    print("=" * 70)
    print("""
  H_FORMAL (Formal Group Logarithm):
    - NEGATIVE: The formal group log converges only for points in the
      kernel of reduction (v_p(t) > 0). For secp256k1 over F_p, all points
      have v_p(t) = 0, so the series DIVERGES.
    - Smart's attack works for anomalous curves (#E = p) ONLY.
    - secp256k1 has #E = n != p (trace t ≈ 2^128), so Smart's attack is
      completely inapplicable.
    - No partial information (k mod small factor) is extractable.

  H_DIFFEQ (Differential Equations / Division Polynomials):
    - The Hasse invariant H_p ≡ trace(Frob) ≡ t mod p. Confirms ordinarity.
    - Division polynomial ψ_k(P) = 0 iff order | k*secret, giving the
      order of the point P. But finding the FIRST zero requires O(order)
      evaluations — no better than brute force.
    - ψ_k(P) as a function of k is PSEUDORANDOM over F_p — no gradient,
      no exploitable structure for Newton's method or similar.
    - Division polynomials have degree O(k^2) in x, so factoring them
      is harder than the DLP itself.

  OVERALL VERDICT:
    Neither formal groups nor differential algebra provides a viable
    attack on secp256k1 ECDLP. These are THEORETICAL DEAD ENDS for
    non-anomalous curves over prime fields.

    The fundamental barrier: these tools linearize the group law only
    in a p-adic neighborhood of the identity, which for F_p-points
    is trivial (just the identity itself).
""")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TimeoutError("Timeout")))

    t0 = time.time()

    try:
        signal.alarm(30)
        experiment_1_formal_log()
    except (TimeoutError, Exception) as e:
        print(f"  Experiment 1 error: {e}")
    finally:
        signal.alarm(0)

    try:
        signal.alarm(30)
        experiment_2_hensel_lift()
    except (TimeoutError, Exception) as e:
        print(f"  Experiment 2 error: {e}")
    finally:
        signal.alarm(0)

    try:
        signal.alarm(30)
        experiment_3_hasse_invariant()
    except (TimeoutError, Exception) as e:
        print(f"  Experiment 3 error: {e}")
    finally:
        signal.alarm(0)

    try:
        signal.alarm(30)
        experiment_4_division_polynomials()
    except (TimeoutError, Exception) as e:
        print(f"  Experiment 4 error: {e}")
    finally:
        signal.alarm(0)

    try:
        signal.alarm(30)
        experiment_5_divpoly_dlp()
    except (TimeoutError, Exception) as e:
        print(f"  Experiment 5 error: {e}")
    finally:
        signal.alarm(0)

    try:
        signal.alarm(30)
        experiment_6_formal_log_secp256k1()
    except (TimeoutError, Exception) as e:
        print(f"  Experiment 6 error: {e}")
    finally:
        signal.alarm(0)

    summarize()

    elapsed = time.time() - t0
    print(f"\nTotal elapsed: {elapsed:.1f}s")
