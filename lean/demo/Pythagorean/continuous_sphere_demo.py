#!/usr/bin/env python3
"""
Continuous Sphere Optimization for Factor Discovery

Demonstrates:
1. Gradient descent on the sphere to find factor-revealing quadruples
2. Sphere packing density analysis
3. Integer point density on spheres of varying radii
4. Connection to representation numbers r_k(n)

Usage: python continuous_sphere_demo.py
"""

from math import gcd, isqrt, sqrt, pi, cos, sin, atan2, log
from collections import defaultdict
import random

# ============================================================
# §1. Integer Points on Spheres
# ============================================================

def count_representations_r3(n):
    """Count representations of n as a sum of 3 squares (r₃(n))."""
    count = 0
    s = isqrt(n)
    for a in range(-s, s + 1):
        rem1 = n - a * a
        if rem1 < 0: continue
        s2 = isqrt(rem1)
        for b in range(-s2, s2 + 1):
            rem2 = rem1 - b * b
            if rem2 < 0: continue
            c = isqrt(rem2)
            if c * c == rem2:
                count += 2 if c > 0 else 1  # ±c
    return count


def count_representations_r4(n):
    """Count representations of n as a sum of 4 squares (r₄(n))."""
    if n == 0:
        return 1
    count = 0
    s = isqrt(n)
    for a in range(-s, s + 1):
        rem1 = n - a * a
        if rem1 < 0: continue
        s2 = isqrt(rem1)
        for b in range(-s2, s2 + 1):
            rem2 = rem1 - b * b
            if rem2 < 0: continue
            s3 = isqrt(rem2)
            for c in range(-s3, s3 + 1):
                rem3 = rem2 - c * c
                if rem3 < 0: continue
                d = isqrt(rem3)
                if d * d == rem3:
                    count += 2 if d > 0 else 1
    return count


def jacobi_r4(n):
    """Jacobi's formula: r₄(n) = 8 * sum of divisors d of n where 4 ∤ d."""
    if n == 0: return 1
    total = 0
    for d in range(1, n + 1):
        if n % d == 0 and d % 4 != 0:
            total += d
    return 8 * total


def representation_density():
    """Analyze how integer point density grows with dimension."""
    print("\n=== Integer Point Density on Spheres ===")
    print(f"{'d²':>6} {'r₃(d²)':>8} {'r₄(d²)':>8} {'r₄ Jacobi':>10} {'Ratio r₄/r₃':>12}")
    print("-" * 48)

    for d in range(1, 16):
        n = d * d
        r3 = count_representations_r3(n)
        r4_actual = count_representations_r4(n) if n <= 100 else "—"
        r4_jacobi = jacobi_r4(n)

        if isinstance(r4_actual, int) and r3 > 0:
            ratio = r4_actual / r3
            print(f"{n:>6} {r3:>8} {r4_actual:>8} {r4_jacobi:>10} {ratio:>12.1f}")
        else:
            print(f"{n:>6} {r3:>8} {'—':>8} {r4_jacobi:>10} {'—':>12}")


# ============================================================
# §2. Gradient Descent on the Sphere (Continuous Relaxation)
# ============================================================

def soft_gcd_objective(x, N):
    """Smooth approximation of GCD-based factoring objective.

    We want to maximize the chance that gcd(round(d-c), N) is nontrivial.
    Smooth proxy: sum of cos(2π·(d-c)·p/N) for small primes p dividing N.
    When d-c is a multiple of a factor of N, this sum is maximized.
    """
    a, b, c = x  # on the sphere a²+b²+c² = d²
    d_val = sqrt(a*a + b*b + c*c)
    if d_val < 1:
        return -1e6

    score = 0
    dc = d_val - c
    for p in range(2, min(N, 50)):
        if N % p == 0:
            score += cos(2 * pi * dc / p) * 2
            score += cos(2 * pi * (d_val + c) / p)
    return score


def project_to_sphere(x, radius):
    """Project point x onto the sphere of given radius."""
    norm = sqrt(sum(xi*xi for xi in x))
    if norm < 1e-10:
        return [radius, 0, 0]
    scale = radius / norm
    return [xi * scale for xi in x]


def sphere_gradient_descent(N, d_target=None, steps=500, lr=0.5):
    """Gradient descent on the sphere to find factor-revealing quadruples."""
    if d_target is None:
        d_target = N + 1  # Start with a reasonable hypotenuse

    # Initialize random point on sphere of radius d_target
    random.seed(42 + N)
    x = [random.gauss(0, 1) for _ in range(3)]
    x = project_to_sphere(x, d_target)

    best_factor = None
    best_score = -1e10

    for step in range(steps):
        score = soft_gcd_objective(x, N)

        if score > best_score:
            best_score = score
            # Check integer neighbors
            for da in [-1, 0, 1]:
                for db in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        ia = round(x[0]) + da
                        ib = round(x[1]) + db
                        ic = round(x[2]) + dc
                        d2 = ia*ia + ib*ib + ic*ic
                        d_int = isqrt(d2)
                        if d_int*d_int == d2 and d_int > 0:
                            g1 = gcd(abs(d_int - ic), N)
                            g2 = gcd(abs(d_int + ic), N)
                            if 1 < g1 < N:
                                best_factor = g1
                            if 1 < g2 < N:
                                best_factor = g2

        # Numerical gradient
        eps = 0.01
        grad = []
        for i in range(3):
            x_plus = list(x)
            x_plus[i] += eps
            x_minus = list(x)
            x_minus[i] -= eps
            g = (soft_gcd_objective(x_plus, N) - soft_gcd_objective(x_minus, N)) / (2 * eps)
            grad.append(g)

        # Gradient step
        x = [x[i] + lr * grad[i] for i in range(3)]
        # Project back onto sphere
        x = project_to_sphere(x, d_target)

    return best_factor, best_score


def gradient_descent_demo():
    """Demo gradient descent factoring on the sphere."""
    print("\n=== Gradient Descent on Sphere for Factoring ===")
    print(f"{'N':>6} {'Factors':>12} {'GD Factor':>10} {'Score':>8}")
    print("-" * 40)

    targets = [15, 21, 33, 35, 51, 55, 77, 85, 91, 143]
    for N in targets:
        # Try multiple radii
        best_factor = None
        best_score = -1e10
        for d in range(N//2, N*2, max(1, N//4)):
            factor, score = sphere_gradient_descent(N, d_target=d, steps=200)
            if factor is not None:
                best_factor = factor
            if score > best_score:
                best_score = score

        # Get true factors
        factors = []
        for i in range(2, isqrt(N) + 1):
            if N % i == 0:
                factors.extend([i, N // i])
        factors = sorted(set(factors))

        f_str = str(best_factor) if best_factor else "—"
        print(f"{N:>6} {str(factors):>12} {f_str:>10} {best_score:>8.2f}")


# ============================================================
# §3. Sphere Packing Analysis
# ============================================================

def sphere_packing_analysis():
    """Analyze packing density relevant to factoring."""
    print("\n=== Sphere Packing and Factoring Density ===")
    print(f"{'Dim k':>6} {'Max Kissing':>12} {'Packing Density':>16} {'Factor Channels':>16}")
    print("-" * 54)

    # Known kissing numbers (exact or best known)
    kissing = {2: 6, 3: 12, 4: 24, 5: 40, 6: 72, 7: 126, 8: 240}
    # Approximate packing densities
    densities = {
        2: 0.9069, 3: 0.7405, 4: 0.6169,
        5: 0.4653, 6: 0.3729, 7: 0.2953, 8: 0.2537
    }

    for k in range(2, 9):
        kiss = kissing.get(k, "?")
        dens = densities.get(k, 0)
        channels = k - 1
        print(f"{k:>6} {kiss:>12} {dens:>16.4f} {channels:>16}")

    print(f"\n  Note: E₈ lattice (dim 8) has kissing number 240,")
    print(f"  providing the densest possible packing.")
    print(f"  This suggests dim 8 (octonion) may be optimal for factor channel density.")


# ============================================================
# §4. Coding Theory Connection
# ============================================================

def factoring_code_analysis():
    """Analyze the 'factoring code' for small composites."""
    print("\n=== Factoring Code Analysis ===")
    print("  For each N, the 'factoring code' C(N) is the set of quadruples")
    print("  that reveal at least one nontrivial factor via GCD cascade.")
    print()

    targets = [15, 21, 35, 77, 143]
    for N in targets:
        total_quads = 0
        revealing_quads = 0
        d_max = 50

        for d in range(1, d_max + 1):
            for a in range(0, d):
                for b in range(a, d):
                    rem = d*d - a*a - b*b
                    if rem < 0: break
                    c = isqrt(rem)
                    if c >= b and c*c == rem:
                        total_quads += 1
                        gcds = [
                            gcd(d - c, N), gcd(d + c, N),
                            gcd(d - b, N), gcd(d + b, N),
                            gcd(d - a, N), gcd(d + a, N),
                        ]
                        if any(1 < g < N and N % g == 0 for g in gcds):
                            revealing_quads += 1

        rate = revealing_quads / total_quads if total_quads > 0 else 0
        print(f"  N={N:>4}: {revealing_quads}/{total_quads} revealing quadruples"
              f" (rate = {rate:.3f})")


# ============================================================
# §5. Representation Number Verification
# ============================================================

def verify_jacobi():
    """Verify Jacobi's r₄(n) formula for small values."""
    print("\n=== Verification of Jacobi's Formula r₄(n) = 8·σ̃(n) ===")
    print(f"{'n':>4} {'r₄ (computed)':>14} {'r₄ (Jacobi)':>12} {'Match':>6}")
    print("-" * 40)

    for n in range(1, 21):
        r4_comp = count_representations_r4(n)
        r4_jac = jacobi_r4(n)
        match = "✓" if r4_comp == r4_jac else "✗"
        print(f"{n:>4} {r4_comp:>14} {r4_jac:>12} {match:>6}")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Continuous Sphere Optimization for Factor Discovery    ║")
    print("║  Gradient Descent, Packing, and Coding Theory           ║")
    print("╚══════════════════════════════════════════════════════════╝")

    representation_density()
    gradient_descent_demo()
    sphere_packing_analysis()
    factoring_code_analysis()
    verify_jacobi()

    print("\n" + "=" * 60)
    print("Continuous sphere demo complete.")
