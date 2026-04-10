#!/usr/bin/env python3
"""
Li Coefficients and Riemann Hypothesis Demo

Demonstrates the computation of Li coefficients and the connection
to the Riemann Hypothesis, corresponding to the spectral theory
results in Foundations.lean.
"""

import cmath
import math


def riemann_zeta_approx(s, num_terms=1000):
    """Approximate the Riemann zeta function using partial sum of the Dirichlet series.
    Only valid for Re(s) > 1."""
    if s.real <= 1:
        return None
    return sum(1.0 / n**s for n in range(1, num_terms + 1))


def li_coefficient_from_zeros(zeros, n):
    """Compute the n-th Li coefficient from a list of zeros rho:
    lambda_n = sum_rho [1 - (1 - 1/rho)^n]
    """
    total = 0
    for rho in zeros:
        if abs(rho) < 1e-15:
            continue
        w = 1 - 1/rho
        total += 1 - w**n
    return total


def known_riemann_zeros(count=20):
    """Return the first few known nontrivial zeros of the Riemann zeta function.
    These are 1/2 + i*t where t are the Gram points / known imaginary parts.
    Source: Tables of zeros computed by Odlyzko et al.
    """
    # Imaginary parts of the first 20 nontrivial zeros
    t_values = [
        14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
        37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
        52.970321, 56.446248, 59.347044, 60.831779, 65.112544,
        67.079811, 69.546402, 72.067158, 75.704691, 77.144840,
    ]
    zeros = []
    for t in t_values[:count]:
        zeros.append(complex(0.5, t))
        zeros.append(complex(0.5, -t))  # conjugate zero
    return zeros


def demonstrate_critical_line_property():
    """Demonstrate Theorem: critical_line_implies_unit_disk
    For rho on Re(s) = 1/2, |1 - 1/rho| <= 1."""
    print("=" * 60)
    print("CRITICAL LINE UNIT DISK PROPERTY")
    print("(Formally verified in Lean: critical_line_implies_unit_disk)")
    print("=" * 60)

    zeros = known_riemann_zeros(10)
    print(f"\n{'Zero rho':>25s}  |1 - 1/rho|  <= 1?")
    print("-" * 55)
    for rho in zeros:
        if rho.imag > 0:  # show only positive imaginary part
            w = 1 - 1/rho
            norm = abs(w)
            status = "YES" if norm <= 1.0 + 1e-10 else "NO"
            print(f"  {rho.real:.1f} + {rho.imag:.6f}i    {norm:.10f}   {status}")

    print("\nNote: |1 - 1/rho| = 1 exactly (not just <= 1) for zeros on Re(s) = 1/2.")
    print("This is because the map rho -> 1 - 1/rho sends the critical line to the unit circle.")


def compute_li_coefficients():
    """Compute Li coefficients from known zeros."""
    print("\n" + "=" * 60)
    print("LI COEFFICIENTS lambda_n")
    print("(Formally verified structure in Lean: li_positivity_from_critical_line)")
    print("=" * 60)

    zeros = known_riemann_zeros(20)

    print(f"\n  n   lambda_n (approx from first 20 zero pairs)   >0?")
    print("-" * 60)

    for n in range(1, 21):
        lam = li_coefficient_from_zeros(zeros, n)
        # Li coefficients should be real (imaginary parts from conjugate pairs cancel)
        lam_real = lam.real
        status = "YES" if lam_real > -1e-6 else "NO"
        print(f"  {n:2d}   {lam_real:15.6f}                              {status}")

    print("\nLi's criterion: RH is true if and only if lambda_n >= 0 for all n >= 1.")
    print("All lambda_n have been verified positive computationally up to n ~ 10^9.")


def spectral_analogy():
    """Demonstrate the spectral analogy: trace formula."""
    print("\n" + "=" * 60)
    print("SPECTRAL ANALOGY: TRACE FORMULA")
    print("(Formally verified in Lean: trace_eq_sum_diagonal)")
    print("=" * 60)

    # Create a small symmetric matrix as example
    import random
    random.seed(42)
    n = 5
    M = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            v = round(random.gauss(0, 1), 3)
            M[i][j] = v
            M[j][i] = v

    trace = sum(M[i][i] for i in range(n))
    print(f"\n  Example {n}x{n} symmetric matrix M:")
    for row in M:
        print(f"    [{', '.join(f'{x:7.3f}' for x in row)}]")
    print(f"\n  Tr(M) = sum of diagonal = {trace:.3f}")
    print(f"  (In the Hilbert-Polya approach, Tr(e^{{-tH}}) = sum of e^{{-t*eigenvalue}})")
    print(f"  This connects the operator spectrum to a 'partition function'.")


def main():
    print("=" * 60)
    print("  RIEMANN HYPOTHESIS: LI COEFFICIENTS DEMO")
    print("  Companion to formally verified results in Lean 4")
    print("=" * 60)

    demonstrate_critical_line_property()
    compute_li_coefficients()
    spectral_analogy()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("Our Lean formalization verifies:")
    print("  1. Zeros on Re(s)=1/2 map to the unit circle under rho -> 1-1/rho")
    print("  2. Unit circle property implies Li coefficient positivity")
    print("  3. The trace formula structure underlying the explicit formula")
    print("These are the structural foundations of Li's criterion for RH.")


if __name__ == "__main__":
    main()
