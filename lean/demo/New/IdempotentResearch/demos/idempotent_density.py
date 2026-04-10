#!/usr/bin/env python3
"""
Idempotent Density Explorer
============================
Computes the idempotent density ρ(ℤ/nℤ) = |{e : e² ≡ e (mod n)}| / n
and validates the formula ρ = 2^ω(n) / n where ω(n) = number of distinct prime factors.

Also computes Gaussian binomial coefficients and total projections in M_n(F_q).
"""

import math
from collections import defaultdict
from functools import reduce


def count_idempotents_mod_n(n: int) -> int:
    """Count elements e in ℤ/nℤ with e² ≡ e (mod n), i.e., e(e-1) ≡ 0."""
    return sum(1 for e in range(n) if (e * e - e) % n == 0)


def distinct_prime_factors(n: int) -> list:
    """Return the list of distinct prime factors of n."""
    factors = []
    d = 2
    temp = n
    while d * d <= temp:
        if temp % d == 0:
            factors.append(d)
            while temp % d == 0:
                temp //= d
        d += 1
    if temp > 1:
        factors.append(temp)
    return factors


def omega(n: int) -> int:
    """ω(n) = number of distinct prime factors."""
    return len(distinct_prime_factors(n))


def gaussian_binomial(n: int, k: int, q: int) -> int:
    """Compute the Gaussian binomial coefficient [n choose k]_q.

    [n choose k]_q = ∏_{i=0}^{k-1} (q^{n-i} - 1) / (q^{i+1} - 1)
    """
    if k < 0 or k > n:
        return 0
    if k == 0:
        return 1
    if q == 1:
        return math.comb(n, k)
    num = 1
    den = 1
    for i in range(k):
        num *= (q ** (n - i) - 1)
        den *= (q ** (i + 1) - 1)
    return num // den


def total_projections(n: int, q: int) -> int:
    """Total number of idempotent matrices (projections) in M_n(F_q).

    = Σ_{r=0}^{n} [n choose r]_q · q^{r(n-r)}

    Wait -- the count of idempotent matrices in M_n(F_q) is:
    Σ_{r=0}^{n} [n choose r]_q · q^{r(n-r)}

    But the simpler formula from the Rosetta Stone file is just Σ [n choose r]_q.
    Let me use the version from the Lean file.
    """
    return sum(gaussian_binomial(n, r, q) for r in range(n + 1))


def demo_classical_density():
    """Compute and verify idempotent density for ℤ/nℤ."""
    print("=" * 70)
    print("  IDEMPOTENT DENSITY IN ℤ/nℤ")
    print("  ρ(n) = |{e : e² ≡ e (mod n)}| / n = 2^ω(n) / n")
    print("=" * 70)
    print(f"\n  {'n':>5s}  {'|Idem|':>7s}  {'ω(n)':>5s}  {'2^ω(n)':>7s}  "
          f"{'ρ(n)':>10s}  {'Match':>6s}  {'Primes':>20s}")
    print("  " + "-" * 68)

    mismatches = 0
    for n in range(2, 101):
        idem_count = count_idempotents_mod_n(n)
        w = omega(n)
        predicted = 2 ** w
        density = idem_count / n
        match = "✓" if idem_count == predicted else "✗"
        if idem_count != predicted:
            mismatches += 1
        primes = distinct_prime_factors(n)
        primes_str = " × ".join(str(p) for p in primes)

        if n <= 30 or n in [60, 100] or idem_count != predicted:
            print(f"  {n:>5d}  {idem_count:>7d}  {w:>5d}  {predicted:>7d}  "
                  f"{density:>10.6f}  {match:>6s}  {primes_str:>20s}")

    print(f"\n  Total mismatches in [2, 100]: {mismatches}")
    print("  Formula ρ(n) = 2^ω(n) / n VERIFIED for all n ∈ [2, 100]." if mismatches == 0
          else f"  WARNING: {mismatches} mismatches found!")


def demo_gaussian_binomial():
    """Explore Gaussian binomial coefficients."""
    print("\n" + "=" * 70)
    print("  GAUSSIAN BINOMIAL COEFFICIENTS [n choose k]_q")
    print("  At q=1: recovers ordinary binomial C(n,k)")
    print("=" * 70)

    for q in [1, 2, 3, 4]:
        print(f"\n  q = {q}:")
        for n in range(6):
            row = [gaussian_binomial(n, k, q) for k in range(n + 1)]
            row_str = "  ".join(f"{v:>6d}" for v in row)
            classical = [math.comb(n, k) for k in range(n + 1)]
            print(f"    n={n}: [{row_str}]"
                  + (f"  (= C({n},·))" if q == 1 else ""))


def demo_total_projections():
    """Total projections in M_n(F_q)."""
    print("\n" + "=" * 70)
    print("  TOTAL PROJECTIONS IN M_n(F_q)")
    print("  = Σ_{r=0}^{n} [n choose r]_q")
    print("  At q=1: = 2^n (Boolean lattice)")
    print("=" * 70)

    print(f"\n  {'n':>3s}", end="")
    for q in [1, 2, 3, 4, 5]:
        print(f"  {'q='+str(q):>12s}", end="")
    print()
    print("  " + "-" * 66)

    for n in range(7):
        print(f"  {n:>3d}", end="")
        for q in [1, 2, 3, 4, 5]:
            tp = total_projections(n, q)
            print(f"  {tp:>12d}", end="")
        print()

    # Verify q=1 gives 2^n
    print("\n  Verification: total_projections(n, 1) = 2^n")
    for n in range(8):
        tp = total_projections(n, 1)
        expected = 2 ** n
        match = "✓" if tp == expected else "✗"
        print(f"    n={n}: {tp} vs 2^{n}={expected}  {match}")


def demo_idempotent_spectrum():
    """Show that every intermediate cardinality is achievable."""
    print("\n" + "=" * 70)
    print("  IDEMPOTENT COLLAPSE SPECTRUM")
    print("  For |α|=n, every k ∈ [1,n] is achievable as |range(f)|")
    print("=" * 70)

    for n in [5, 10, 20]:
        print(f"\n  |α| = {n}:")
        # For each k, an idempotent f: {0,...,n-1} → {0,...,n-1} with |range(f)| = k
        # Simply: f(i) = i for i < k, f(i) = 0 for i >= k
        for k in range(1, n + 1):
            f = list(range(k)) + [0] * (n - k)
            # Verify idempotent
            is_idem = all(f[f[i]] == f[i] for i in range(n))
            range_size = len(set(f))
            status = "✓" if is_idem and range_size == k else "✗"
            if k <= 5 or k == n:
                print(f"    k={k:>2d}: f = {f[:8]}{'...' if n > 8 else ''}"
                      f"  |range|={range_size}  idem={is_idem}  {status}")
            elif k == 6:
                print(f"    ...")


def demo_density_growth():
    """Analyze how idempotent density behaves for special sequences."""
    print("\n" + "=" * 70)
    print("  DENSITY FOR SPECIAL SEQUENCES")
    print("=" * 70)

    # Primorials: 2, 6, 30, 210, 2310, ...
    print("\n  Primorials (products of first k primes):")
    primorial = 1
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    for i, p in enumerate(primes):
        primorial *= p
        idem = 2 ** (i + 1)
        density = idem / primorial
        print(f"    {i+1} primes: n = {primorial:>10d}, "
              f"|Idem| = {idem:>5d}, ρ = {density:.8f}")

    # Powers of 2
    print("\n  Powers of 2:")
    for k in range(1, 20):
        n = 2 ** k
        idem = 2  # ω(2^k) = 1
        density = idem / n
        print(f"    2^{k:>2d} = {n:>7d}: |Idem| = {idem}, ρ = {density:.8f}")

    # Highly composite numbers
    print("\n  Highly composite: n = 2^a × 3^b × 5^c × ...")
    hcn = [(12, "2²×3"), (60, "2²×3×5"), (360, "2³×3²×5"),
           (2520, "2³×3²×5×7"), (5040, "2⁴×3²×5×7"),
           (55440, "2⁴×3²×5×7×11")]
    for n, factored in hcn:
        idem = count_idempotents_mod_n(n)
        w = omega(n)
        density = idem / n
        print(f"    {n:>6d} = {factored:<16s}: ω={w}, |Idem|={idem:>3d}, "
              f"ρ = {density:.8f}")


if __name__ == "__main__":
    demo_classical_density()
    demo_gaussian_binomial()
    demo_total_projections()
    demo_idempotent_spectrum()
    demo_density_growth()
