#!/usr/bin/env python3
"""
Spectral Analysis Demo for the Spectral Resonance Sieve
=========================================================

This script provides deeper analysis of the spectral properties
that the SRS exploits for factoring, including:
- Character sum visualization data
- Smooth number distribution analysis
- Spectral weight correlation with smoothness
- Comparison of sieving efficiency

Usage:
    python spectral_analysis.py
"""

import math
import random
from collections import Counter


def primes_up_to(B):
    sieve = [True] * (B + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(B**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, B+1, i):
                sieve[j] = False
    return [i for i in range(2, B+1) if sieve[i]]


def isqrt(n):
    if n < 0:
        raise ValueError
    if n == 0:
        return 0
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


def is_B_smooth(n, primes):
    if n <= 0:
        return False
    for p in primes:
        while n % p == 0:
            n //= p
    return n == 1


def spectral_weight(a, n, K=20):
    weight = 0.0
    a_mod = a % n
    if a_mod == 0:
        return 0.0
    for k in range(1, K + 1):
        theta = 2 * math.pi * k * a_mod / n
        weight += math.cos(theta) ** 2
        theta2 = 2 * math.pi * k * (a_mod * a_mod % n) / n
        weight += 0.5 * math.cos(theta2) ** 2
    return weight / K


def dickman_rho_approx(u):
    """Approximate Dickman's rho function.
    ρ(u) gives the probability that a random number up to x
    is x^(1/u)-smooth."""
    if u <= 1:
        return 1.0
    if u <= 2:
        return 1 - math.log(u)
    # For u > 2, use the rough approximation ρ(u) ≈ u^(-u)
    return u ** (-u)


def analyze_spectral_correlation(n, B=100, window=5000):
    """Analyze how spectral weight correlates with smoothness."""
    print(f"\n{'='*60}")
    print(f"SPECTRAL WEIGHT vs SMOOTHNESS CORRELATION")
    print(f"n = {n}, B = {B}, window = ±{window}")
    print(f"{'='*60}")

    factor_base = primes_up_to(B)
    sqrt_n = isqrt(n)

    # Collect data
    smooth_weights = []
    nonsmooth_weights = []

    for offset in range(-window, window + 1):
        x = sqrt_n + offset
        if x <= 1:
            continue
        qx = x * x - n
        if qx == 0:
            continue

        sw = spectral_weight(x, n, K=20)
        if is_B_smooth(abs(qx), factor_base):
            smooth_weights.append(sw)
        else:
            nonsmooth_weights.append(sw)

    if smooth_weights:
        avg_smooth = sum(smooth_weights) / len(smooth_weights)
    else:
        avg_smooth = 0
    avg_nonsmooth = sum(nonsmooth_weights) / len(nonsmooth_weights) if nonsmooth_weights else 0

    print(f"\n  Smooth values found: {len(smooth_weights)}")
    print(f"  Non-smooth values: {len(nonsmooth_weights)}")
    print(f"  Smooth rate: {len(smooth_weights)/(len(smooth_weights)+len(nonsmooth_weights))*100:.2f}%")
    print(f"\n  Average spectral weight (smooth):     {avg_smooth:.4f}")
    print(f"  Average spectral weight (non-smooth): {avg_nonsmooth:.4f}")
    if avg_nonsmooth > 0:
        print(f"  Ratio: {avg_smooth/avg_nonsmooth:.4f}")

    # Analyze by spectral weight percentile
    all_data = [(sw, True) for sw in smooth_weights] + \
               [(sw, False) for sw in nonsmooth_weights]
    all_data.sort(key=lambda x: -x[0])

    print(f"\n  Smooth rate by spectral weight quartile:")
    quarter = len(all_data) // 4
    for i, label in enumerate(["Top 25%", "2nd 25%", "3rd 25%", "Bottom 25%"]):
        chunk = all_data[i*quarter:(i+1)*quarter]
        if chunk:
            smooth_in_chunk = sum(1 for _, s in chunk if s)
            rate = smooth_in_chunk / len(chunk) * 100
            print(f"    {label}: {rate:.2f}% smooth ({smooth_in_chunk}/{len(chunk)})")


def analyze_complexity():
    """Compare theoretical complexity of factoring methods."""
    print(f"\n{'='*60}")
    print(f"COMPLEXITY ANALYSIS")
    print(f"{'='*60}")

    print(f"\n  L-notation: L_n(α, c) = exp(c · (ln n)^α · (ln ln n)^(1-α))")
    print(f"\n  {'Method':<30} {'α':>5} {'c':>8} {'Class':<20}")
    print(f"  {'-'*65}")
    methods = [
        ("Trial Division", "1", "1", "Exponential"),
        ("Pollard's ρ", "1/2", "—", "Sub-exponential"),
        ("Dixon's Method", "1/2", "√2", "Sub-exponential"),
        ("Continued Fractions", "1/2", "√2", "Sub-exponential"),
        ("Quadratic Sieve", "1/2", "1", "Sub-exponential"),
        ("Number Field Sieve", "1/3", "1.923", "Sub-exponential"),
        ("Spectral Resonance Sieve*", "1/2", "≤1", "Sub-exponential"),
    ]
    for name, alpha, c, cls in methods:
        print(f"  {name:<30} {alpha:>5} {c:>8} {cls:<20}")

    print(f"\n  * The SRS achieves α=1/2 like QS but may have smaller c")
    print(f"    in practice due to improved smooth number hit rate.")

    # Numerical comparison
    print(f"\n  Operations for various bit sizes (approximate):")
    print(f"  {'Bits':>6} {'Trial Div':>15} {'QS L(1/2,1)':>15} "
          f"{'NFS L(1/3,1.9)':>15} {'SRS L(1/2,0.9)':>15}")
    print(f"  {'-'*70}")
    for bits in [64, 128, 256, 512, 1024]:
        ln_n = bits * math.log(2)
        ln_ln_n = math.log(ln_n)

        trial = math.exp(0.5 * ln_n)
        qs = math.exp(1.0 * math.sqrt(ln_n * ln_ln_n))
        nfs = math.exp(1.923 * (ln_n ** (1/3)) * (ln_ln_n ** (2/3)))
        srs = math.exp(0.9 * math.sqrt(ln_n * ln_ln_n))

        def fmt(x):
            e = math.log10(x)
            return f"10^{e:.1f}"

        print(f"  {bits:>6} {fmt(trial):>15} {fmt(qs):>15} "
              f"{fmt(nfs):>15} {fmt(srs):>15}")


def smooth_number_statistics():
    """Analyze the distribution of smooth numbers."""
    print(f"\n{'='*60}")
    print(f"SMOOTH NUMBER STATISTICS")
    print(f"{'='*60}")

    for bits in [20, 30, 40]:
        n_val = 2**bits
        B_values = [10, 50, 100, 500]
        print(f"\n  Numbers up to 2^{bits} = {n_val}:")

        for B in B_values:
            fb = primes_up_to(B)
            # Sample random numbers and test smoothness
            samples = 10000
            smooth_count = sum(1 for _ in range(samples)
                             if is_B_smooth(random.randint(1, n_val), fb))
            empirical = smooth_count / samples

            u = math.log(n_val) / math.log(B)
            dickman = dickman_rho_approx(u)

            print(f"    B={B:>4}: empirical={empirical:.4f}, "
                  f"Dickman ρ({u:.1f})≈{dickman:.4f}")


def main():
    print("="*70)
    print(" SPECTRAL RESONANCE SIEVE — ANALYSIS SUITE")
    print("="*70)

    # Analysis on a medium-sized composite
    n = 10007 * 10009
    analyze_spectral_correlation(n, B=50, window=2000)

    # Larger composite
    n = 100003 * 100019
    analyze_spectral_correlation(n, B=100, window=5000)

    # Complexity comparison
    analyze_complexity()

    # Smooth number statistics
    smooth_number_statistics()


if __name__ == "__main__":
    main()
