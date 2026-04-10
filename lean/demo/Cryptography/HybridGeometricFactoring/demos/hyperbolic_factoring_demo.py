#!/usr/bin/env python3
"""
Hyperbolic Geometry and Integer Factoring — Demonstration

This script demonstrates:
1. The divisor hyperbola and its hyperbolic-geometric interpretation
2. SL₂(ℤ) transformations and their connection to factoring
3. Farey sequence structure and divisor discovery
4. The orbit-hyperbola connection
5. Quadratic residue structure via CRT

Usage:
    python hyperbolic_factoring_demo.py
"""

import math
from fractions import Fraction
from collections import defaultdict


def divisors(n):
    """Return sorted list of divisors of n."""
    divs = []
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


def hyperbolic_distance(z1, z2):
    """
    Compute hyperbolic distance in the upper half-plane model.
    z = (x, y) represents x + iy with y > 0.
    cosh(d) = 1 + |z1 - z2|² / (2 · Im(z1) · Im(z2))
    """
    dx = z1[0] - z2[0]
    dy = z1[1] - z2[1]
    dist_sq = dx * dx + dy * dy
    cosh_d = 1 + dist_sq / (2 * z1[1] * z2[1])
    return math.acosh(cosh_d) if cosh_d >= 1 else 0


def divisor_hyperbola_analysis(n):
    """Analyze divisor pairs as points on the hyperbola xy = n."""
    print(f"\n{'='*60}")
    print(f"  Divisor Hyperbola Analysis for n = {n}")
    print(f"{'='*60}")

    divs = divisors(n)
    pairs = [(d, n // d) for d in divs if d <= n // d]

    print(f"\n  Divisor pairs (d, n/d) on hyperbola xy = {n}:")
    print(f"  √{n} ≈ {math.sqrt(n):.4f}\n")

    # Map to upper half-plane: z_d = d + i·(n/d)
    points = {}
    for d in divs:
        z = (float(d), float(n // d))
        points[d] = z
        dist_to_sqrt = abs(d - math.sqrt(n))
        print(f"    d={d:>6}  n/d={n//d:>6}  "
              f"z = {d} + {n//d}i  "
              f"|d-√n| = {dist_to_sqrt:.2f}")

    # Compute pairwise hyperbolic distances
    print(f"\n  Pairwise hyperbolic distances:")
    print(f"  {'d₁':<8} {'d₂':<8} {'d_H':<12} {'log(d₂/d₁)':<14} {'Ratio'}")
    print(f"  {'-'*52}")

    for i, d1 in enumerate(divs):
        for d2 in divs[i+1:]:
            z1 = points[d1]
            z2 = points[d2]
            hd = hyperbolic_distance(z1, z2)
            log_ratio = math.log(d2 / d1)
            print(f"  {d1:<8} {d2:<8} {hd:<12.4f} {log_ratio:<14.4f} {d2/d1:.4f}")


def sl2z_demo():
    """Demonstrate SL₂(ℤ) operations and their factoring connections."""
    print(f"\n{'='*60}")
    print(f"  SL₂(ℤ) and Factoring")
    print(f"{'='*60}")

    def mat_mul(A, B):
        """Multiply 2x2 matrices."""
        return [
            [A[0][0]*B[0][0] + A[0][1]*B[1][0], A[0][0]*B[0][1] + A[0][1]*B[1][1]],
            [A[1][0]*B[0][0] + A[1][1]*B[1][0], A[1][0]*B[0][1] + A[1][1]*B[1][1]]
        ]

    def det(M):
        return M[0][0]*M[1][1] - M[0][1]*M[1][0]

    def mobius(M, z):
        """Apply Möbius transformation M·z = (az+b)/(cz+d)."""
        a, b, c, d = M[0][0], M[0][1], M[1][0], M[1][1]
        # z = (x, y), complex number x + iy
        x, y = z
        denom = (c*x + d)**2 + (c*y)**2
        if denom == 0:
            return None
        real = ((a*x + b)*(c*x + d) + a*c*y*y) / denom
        imag = y * (a*d - b*c) / denom
        return (real, imag)

    # Key generators
    I = [[1, 0], [0, 1]]
    T = [[1, 1], [0, 1]]
    S = [[0, -1], [1, 0]]

    print(f"\n  Generators of SL₂(ℤ):")
    print(f"    I = [[1,0],[0,1]]  (identity, det = {det(I)})")
    print(f"    T = [[1,1],[0,1]]  (translation z → z+1, det = {det(T)})")
    print(f"    S = [[0,-1],[1,0]] (inversion z → -1/z, det = {det(S)})")

    # Demonstrate closure
    TS = mat_mul(T, S)
    ST = mat_mul(S, T)
    TST = mat_mul(T, mat_mul(S, T))
    print(f"\n  Products:")
    print(f"    TS = {TS}, det = {det(TS)}")
    print(f"    ST = {ST}, det = {det(ST)}")
    print(f"    TST = {TST}, det = {det(TST)}")

    # Show action on a point in H
    z = (0.5, 1.0)
    print(f"\n  Action on z = {z[0]} + {z[1]}i:")
    print(f"    T·z = {mobius(T, z)}")
    print(f"    S·z = {mobius(S, z)}")
    print(f"    TS·z = {mobius(TS, z)}")

    # Connection to continued fractions
    print(f"\n  Connection to continued fractions:")
    print(f"  The CF expansion [a₀; a₁, a₂, ...] corresponds to")
    print(f"  the SL₂(ℤ) word T^a₀ · S · T^a₁ · S · T^a₂ · ...")
    print(f"  Each convergent matrix has det = ±1.")

    # Example: CF of √7
    n = 7
    sqrt_n = math.isqrt(n)
    print(f"\n  Example: √{n} = [{sqrt_n}; ", end="")

    a0 = sqrt_n
    m, d, a = 0, 1, a0
    cf = [a0]
    for _ in range(8):
        m = d * a - m
        d = (n - m * m) // d
        if d == 0:
            break
        a = (a0 + m) // d
        cf.append(a)
    print(f"{', '.join(str(c) for c in cf[1:])}...]")

    # Build convergent matrices
    M = [[1, 0], [0, 1]]
    print(f"\n  Convergent matrices:")
    for k, ak in enumerate(cf[:6]):
        Tak = [[1, ak], [0, 1]] if k == 0 else mat_mul([[1, ak], [0, 1]], [[0, 1], [1, 0]])
        if k == 0:
            M = [[ak, 1], [1, 0]]
        else:
            M = [[ak * M[0][0] + (M[0][1] if k > 0 else 1),
                  M[0][0]],
                 [ak * M[1][0] + (M[1][1] if k > 0 else 0),
                  M[1][0]]]
        p, q = M[0][0], M[1][0]
        residue = p*p - n*q*q
        print(f"    k={k}: p/q = {p}/{q}, p²-nq² = {residue}")


def farey_sequence(N):
    """Generate the Farey sequence of order N."""
    fracs = set()
    for b in range(1, N + 1):
        for a in range(0, b + 1):
            if math.gcd(a, b) == 1:
                fracs.add(Fraction(a, b))
    return sorted(fracs)


def farey_demo(n):
    """Show Farey sequence connections to factoring."""
    print(f"\n{'='*60}")
    print(f"  Farey Fractions and Divisor Detection for n = {n}")
    print(f"{'='*60}")

    divs = divisors(n)
    N = min(n, 30)  # Farey order
    farey = farey_sequence(N)

    print(f"\n  Farey sequence F_{N} has {len(farey)} fractions.")
    print(f"  Divisors of {n}: {divs}")

    # Check which d/n appear in Farey sequence
    print(f"\n  Divisor fractions d/{n} in Farey sequences:")
    for d in divs:
        if d <= n:
            f = Fraction(d, n)
            print(f"    {d}/{n} = {f} (reduced), denominator = {f.denominator}")
            if f.denominator <= N:
                # Find neighbors in Farey sequence
                idx = None
                for i, fr in enumerate(farey):
                    if fr == f:
                        idx = i
                        break
                if idx is not None and 0 < idx < len(farey) - 1:
                    left = farey[idx - 1]
                    right = farey[idx + 1]
                    # Farey neighbor property: |ad - bc| = 1
                    det_left = abs(f.numerator * left.denominator - f.denominator * left.numerator)
                    det_right = abs(f.numerator * right.denominator - f.denominator * right.numerator)
                    print(f"      Left neighbor: {left}, |det| = {det_left}")
                    print(f"      Right neighbor: {right}, |det| = {det_right}")


def quadratic_residue_crt(p, q):
    """Demonstrate CRT for quadratic residues."""
    print(f"\n{'='*60}")
    print(f"  Quadratic Residues via CRT: n = {p} × {q} = {p*q}")
    print(f"{'='*60}")

    n = p * q

    # Find QRs mod p
    qr_p = set()
    for x in range(p):
        qr_p.add((x * x) % p)

    # Find QRs mod q
    qr_q = set()
    for x in range(q):
        qr_q.add((x * x) % q)

    # Find QRs mod n
    qr_n = set()
    for x in range(n):
        qr_n.add((x * x) % n)

    print(f"\n  QR mod {p}: {sorted(qr_p)}")
    print(f"  QR mod {q}: {sorted(qr_q)}")
    print(f"  |QR mod {n}| = {len(qr_n)}")
    print(f"  |QR mod {p}| × |QR mod {q}| = {len(qr_p)} × {len(qr_q)} = {len(qr_p) * len(qr_q)}")

    # Verify CRT: a is QR mod n iff a is QR mod p and QR mod q
    print(f"\n  CRT verification:")
    mismatches = 0
    for a in range(n):
        is_qr_n = a in qr_n
        is_qr_p = (a % p) in qr_p
        is_qr_q = (a % q) in qr_q
        is_qr_crt = is_qr_p and is_qr_q
        if is_qr_n != is_qr_crt:
            mismatches += 1
    print(f"  Mismatches: {mismatches} (should be 0)")
    print(f"  ✓ CRT decomposition verified!" if mismatches == 0 else f"  ✗ CRT failed!")

    # Show how QR structure reveals factoring
    print(f"\n  Factoring via QR counting:")
    print(f"  If n were prime, |QR mod n| = (n-1)/2 + 1 = {(n-1)//2 + 1}")
    print(f"  Actual |QR mod n| = {len(qr_n)}")
    print(f"  Ratio: {len(qr_n) / ((n-1)/2 + 1):.4f}")
    print(f"  Expected for n=pq: ≈ 1/4 · n = {n/4:.0f}, actual = {len(qr_n)}")


def orbit_hyperbola_demo(n):
    """Show orbits projected onto the divisor hyperbola."""
    print(f"\n{'='*60}")
    print(f"  Orbit-Hyperbola Projection for n = {n}")
    print(f"{'='*60}")

    divs = divisors(n)
    sqrt_n = math.sqrt(n)

    # Squaring orbit
    x = 2
    orbit = [x]
    for _ in range(20):
        x = (x * x) % n
        orbit.append(x)

    print(f"\n  Squaring orbit (x₀ = 2, mod {n}):")
    print(f"  {'k':<4} {'x^(2^k)':<10} {'gcd(x,n)':<10} {'Closest divisor':<16} {'Distance to √n'}")
    print(f"  {'-'*55}")

    for k, val in enumerate(orbit):
        g = math.gcd(val, n)
        closest_div = min(divs, key=lambda d: abs(d - val))
        dist = abs(val - sqrt_n)
        marker = " ← FACTOR!" if 1 < g < n else ""
        print(f"  {k:<4} {val:<10} {g:<10} {closest_div:<16} {dist:.2f}{marker}")

    # Pollard map orbit
    print(f"\n  Pollard map orbit (f(x) = x² + 1, x₀ = 2, mod {n}):")
    x = 2
    pollard_orbit = [x]
    for _ in range(20):
        x = (x * x + 1) % n
        pollard_orbit.append(x)

    for k, val in enumerate(pollard_orbit):
        g = math.gcd(val, n)
        if 1 < g < n:
            print(f"  k={k}: x = {val}, gcd(x, {n}) = {g} ← FACTOR!")
            print(f"  {n} = {g} × {n // g}")
            break


def main():
    print(f"╔{'═'*58}╗")
    print(f"║  Hybrid Geometric Factoring — Hyperbolic Methods Demo    ║")
    print(f"╚{'═'*58}╝")

    # Demo 1: Divisor hyperbola
    divisor_hyperbola_analysis(210)  # 2 × 3 × 5 × 7

    # Demo 2: SL₂(ℤ)
    sl2z_demo()

    # Demo 3: Farey
    farey_demo(30)

    # Demo 4: QR via CRT
    quadratic_residue_crt(7, 11)

    # Demo 5: Orbit-hyperbola
    orbit_hyperbola_demo(91)  # 7 × 13

    print(f"\n{'='*60}")
    print(f"  Demo complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
