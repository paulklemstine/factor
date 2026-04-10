#!/usr/bin/env python3
"""
Energy Estimates Demo for Navier-Stokes Analysis

Demonstrates the Gronwall inequality, energy decay, and Young's inequality
with epsilon, corresponding to the formally verified results in Foundations.lean.
"""

import math


def gronwall_demo():
    """Demonstrate the discrete Gronwall inequality."""
    print("=" * 60)
    print("DISCRETE GRONWALL INEQUALITY")
    print("(Formally verified in Lean: discrete_gronwall)")
    print("=" * 60)

    c = 0.1  # growth rate
    a0 = 1.0  # initial value
    N = 30

    # Simulate a sequence satisfying a(n+1) <= (1+c) * a(n)
    # with some randomness below the bound
    import random
    random.seed(123)

    a_actual = [a0]
    a_bound = [a0]

    for n in range(N):
        # Actual sequence: grows at rate <= (1+c) with some slack
        factor = 1 + c * random.uniform(0.3, 1.0)
        a_actual.append(factor * a_actual[-1])
        # Gronwall bound
        a_bound.append((1 + c) ** (n + 1) * a0)

    print(f"\n  Parameters: c = {c}, a(0) = {a0}")
    print(f"  Gronwall bound: a(n) <= (1 + {c})^n * {a0}")
    print(f"\n  {'n':>4s}  {'a(n) actual':>12s}  {'(1+c)^n*a0':>12s}  {'Bound holds?':>12s}")
    print("  " + "-" * 50)

    for n in range(0, N + 1, 3):
        holds = "YES" if a_actual[n] <= a_bound[n] + 1e-10 else "NO"
        print(f"  {n:4d}  {a_actual[n]:12.4f}  {a_bound[n]:12.4f}  {holds:>12s}")


def energy_decay_demo():
    """Demonstrate energy decay with viscous dissipation."""
    print("\n" + "=" * 60)
    print("ENERGY DECAY (VISCOUS DISSIPATION)")
    print("(Formally verified in Lean: energy_decay_discrete)")
    print("=" * 60)

    nu = 0.05  # viscosity parameter
    E0 = 10.0  # initial energy
    N = 50

    E_actual = [E0]
    E_bound = [E0]

    import random
    random.seed(456)

    for n in range(N):
        # Actual energy: decays at rate (1-nu) with some fluctuation
        decay = (1 - nu) * (1 - 0.02 * random.random())
        E_actual.append(decay * E_actual[-1])
        E_bound.append((1 - nu) ** (n + 1) * E0)

    print(f"\n  Parameters: nu = {nu}, E(0) = {E0}")
    print(f"  Bound: E(n) <= (1 - {nu})^n * {E0}")
    print(f"\n  {'n':>4s}  {'E(n) actual':>12s}  {'Bound':>12s}  {'Ratio':>8s}")
    print("  " + "-" * 45)

    for n in range(0, N + 1, 5):
        ratio = E_actual[n] / E_bound[n] if E_bound[n] > 0 else 0
        print(f"  {n:4d}  {E_actual[n]:12.6f}  {E_bound[n]:12.6f}  {ratio:8.4f}")

    print(f"\n  After {N} steps:")
    print(f"    Actual energy: {E_actual[-1]:.8f}")
    print(f"    Bound:         {E_bound[-1]:.8f}")
    print(f"    Ratio:         {E_actual[-1]/E_bound[-1]:.4f}")


def youngs_inequality_demo():
    """Demonstrate Young's inequality with epsilon."""
    print("\n" + "=" * 60)
    print("YOUNG'S INEQUALITY WITH EPSILON")
    print("(Formally verified in Lean: youngs_inequality_eps)")
    print("=" * 60)

    print("\n  Statement: a*b <= (eps/2)*a^2 + (1/(2*eps))*b^2")
    print("\n  This is crucial for absorbing nonlinear terms in PDE estimates.")
    print("  By choosing eps, we trade off between the two quadratic terms.\n")

    a, b = 3.0, 5.0
    ab = a * b

    print(f"  For a = {a}, b = {b}: a*b = {ab}")
    print(f"\n  {'eps':>8s}  {'eps/2*a^2':>12s}  {'1/(2eps)*b^2':>14s}  {'Sum':>8s}  {'>=ab?':>6s}")
    print("  " + "-" * 56)

    for eps in [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]:
        term1 = eps / 2 * a**2
        term2 = 1 / (2 * eps) * b**2
        total = term1 + term2
        holds = "YES" if total >= ab - 1e-10 else "NO"
        print(f"  {eps:8.2f}  {term1:12.4f}  {term2:14.4f}  {total:8.4f}  {holds:>6s}")

    # Optimal epsilon
    eps_opt = b / a
    term1_opt = eps_opt / 2 * a**2
    term2_opt = 1 / (2 * eps_opt) * b**2
    print(f"\n  Optimal eps = b/a = {eps_opt:.4f}")
    print(f"  At optimal: both terms equal {term1_opt:.4f}, sum = {term1_opt + term2_opt:.4f} = a*b = {ab}")
    print(f"  (Equality holds at the optimal epsilon)")


def am_gm_demo():
    """Demonstrate AM-GM inequality."""
    print("\n" + "=" * 60)
    print("AM-GM INEQUALITY")
    print("(Formally verified in Lean: am_gm_two)")
    print("=" * 60)

    print("\n  Statement: a*b <= (a^2 + b^2)/2 for a, b >= 0")
    print("\n  Proof: (a - b)^2 >= 0 implies a^2 + b^2 >= 2ab\n")

    pairs = [(1, 1), (2, 3), (0, 5), (1, 10), (3, 3), (7, 2)]
    print(f"  {'a':>4s}  {'b':>4s}  {'a*b':>8s}  {'(a^2+b^2)/2':>14s}  {'Gap':>8s}")
    print("  " + "-" * 44)
    for a, b in pairs:
        ab = a * b
        bound = (a**2 + b**2) / 2
        gap = bound - ab
        print(f"  {a:4d}  {b:4d}  {ab:8.1f}  {bound:14.1f}  {gap:8.1f}")

    print(f"\n  The gap is always (a-b)^2/2 >= 0, with equality iff a = b.")


def navier_stokes_energy_balance():
    """Demonstrate the energy balance in Navier-Stokes."""
    print("\n" + "=" * 60)
    print("NAVIER-STOKES ENERGY BALANCE ILLUSTRATION")
    print("=" * 60)

    print("""
  The incompressible Navier-Stokes equations:

    du/dt + (u . grad)u = -grad(p) + nu * laplacian(u)
    div(u) = 0

  Energy identity (formally, after integrating):

    d/dt ||u||^2 + 2*nu*||grad(u)||^2 = 0
         ^^^^^^^^   ^^^^^^^^^^^^^^^^^^^
         kinetic     viscous dissipation
         energy

  This means:  E(t+dt) ≈ E(t) - 2*nu*||grad(u)||^2 * dt

  The challenge: controlling the NONLINEAR term (u.grad)u
  requires interpolation inequalities (Young's, Sobolev, etc.)

  In 3D, the critical estimate is:
    |integral(u . grad(u) . u)| <= C * ||u||^(1/2) * ||grad(u)||^(3/2) * ||u||
    
  Using Young's inequality with epsilon (verified in Lean!):
    <= eps * ||grad(u)||^2 + C(eps) * ||u||^6

  When eps < 2*nu, the gradient term is absorbed, giving energy control.
  But the ||u||^6 term can blow up... this is the open problem!
""")


def main():
    print("=" * 60)
    print("  NAVIER-STOKES ENERGY ESTIMATES DEMO")
    print("  Companion to formally verified results in Lean 4")
    print("=" * 60)

    gronwall_demo()
    energy_decay_demo()
    youngs_inequality_demo()
    am_gm_demo()
    navier_stokes_energy_balance()


if __name__ == "__main__":
    main()
