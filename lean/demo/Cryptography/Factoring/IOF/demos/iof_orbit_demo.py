#!/usr/bin/env python3
"""
IOF Orbit Demo: Visualize squaring orbits and smooth number detection.

This demo illustrates the core mechanics of Integer Orbit Factoring (IOF):
1. Squaring orbit computation: x → x² → x⁴ → x⁸ → ... (mod n)
2. Smooth number detection in orbit elements
3. Congruence of squares extraction
4. GCD-based factor recovery

Usage:
    python iof_orbit_demo.py
"""

import math
from collections import Counter


def is_b_smooth(n, B):
    """Check if n is B-smooth (all prime factors ≤ B)."""
    if n <= 1:
        return True, {}
    factors = {}
    temp = n
    for p in range(2, B + 1):
        while temp % p == 0:
            factors[p] = factors.get(p, 0) + 1
            temp //= p
    return temp == 1, factors


def squaring_orbit(x, n, max_steps=100):
    """Compute the squaring orbit: x, x², x⁴, x⁸, ... mod n."""
    orbit = [x % n]
    current = x % n
    for _ in range(max_steps):
        current = pow(current, 2, n)
        if current in orbit:
            orbit.append(current)
            break
        orbit.append(current)
    return orbit


def find_smooth_relations(n, B, num_starts=20, max_orbit_len=50):
    """Find IOF smooth relations by exploring squaring orbits."""
    relations = []
    factor_base = [p for p in range(2, B + 1) if all(p % i != 0 for i in range(2, int(p**0.5) + 1)) or p == 2]

    for start in range(2, 2 + num_starts):
        orbit = squaring_orbit(start, n, max_orbit_len)
        for k, val in enumerate(orbit):
            residue = pow(start, 2**(k), n)
            # Check if residue is B-smooth
            smooth, factors = is_b_smooth(residue if residue > 0 else n, B)
            if smooth and residue > 0:
                relations.append({
                    'a': start,
                    'power': 2**k,
                    'a_powered': pow(start, 2**k, n),
                    'residue': residue,
                    'factors': factors,
                    'orbit_step': k
                })

    return relations, factor_base


def combine_relations_gf2(relations, factor_base):
    """Try to find a GF(2)-null combination of exponent vectors."""
    if len(relations) <= len(factor_base):
        return None

    # Build exponent matrix mod 2
    matrix = []
    for rel in relations:
        row = [rel['factors'].get(p, 0) % 2 for p in factor_base]
        matrix.append(row)

    # Simple: look for a pair with identical exponent vectors mod 2
    for i in range(len(relations)):
        for j in range(i + 1, len(relations)):
            if matrix[i] == matrix[j]:
                return (i, j)

    # Look for a zero row (already a perfect square)
    for i in range(len(relations)):
        if all(v == 0 for v in matrix[i]):
            return (i,)

    return None


def iof_factor(n, B=None, verbose=True):
    """
    Attempt to factor n using IOF (Integer Orbit Factoring).

    Parameters:
        n: The number to factor
        B: Smoothness bound (auto-selected if None)
        verbose: Print detailed output
    """
    if B is None:
        # Optimal B ≈ exp(sqrt(ln(n) * ln(ln(n))))
        ln_n = math.log(n)
        B = max(10, int(math.exp(math.sqrt(ln_n * math.log(ln_n)))) // 2)

    if verbose:
        print(f"=" * 60)
        print(f"IOF Factoring: n = {n}")
        print(f"Smoothness bound B = {B}")
        print(f"=" * 60)

    # Step 1: Explore squaring orbits
    if verbose:
        print(f"\n--- Step 1: Exploring Squaring Orbits ---")

    for start in [2, 3, 5, 7]:
        orbit = squaring_orbit(start, n, 10)
        if verbose:
            print(f"  Orbit of {start}: {' → '.join(str(x) for x in orbit[:8])}" +
                  (f" → ..." if len(orbit) > 8 else ""))

    # Step 2: Find smooth relations
    if verbose:
        print(f"\n--- Step 2: Finding Smooth Relations ---")

    relations, factor_base = find_smooth_relations(n, B, num_starts=50, max_orbit_len=30)

    if verbose:
        print(f"  Factor base: {factor_base}")
        print(f"  Found {len(relations)} smooth relations")
        for i, rel in enumerate(relations[:10]):
            print(f"    [{i}] a={rel['a']}, step={rel['orbit_step']}, "
                  f"residue={rel['residue']}, factors={dict(rel['factors'])}")

    if len(relations) < 2:
        if verbose:
            print(f"  Not enough smooth relations found. Try larger B.")
        return None

    # Step 3: GF(2) linear algebra
    if verbose:
        print(f"\n--- Step 3: GF(2) Linear Algebra ---")

    combo = combine_relations_gf2(relations, factor_base)

    if combo is None:
        if verbose:
            print(f"  No suitable combination found. Try more relations.")
        return None

    if verbose:
        print(f"  Found combination: indices {combo}")

    # Step 4: GCD extraction
    if verbose:
        print(f"\n--- Step 4: GCD Extraction ---")

    if len(combo) == 1:
        rel = relations[combo[0]]
        x = rel['a_powered']
        y_sq = rel['residue']
        y = int(math.isqrt(y_sq))
        if y * y != y_sq:
            if verbose:
                print(f"  Perfect square check failed.")
            return None
    else:
        i, j = combo
        rel_i, rel_j = relations[i], relations[j]
        x = (rel_i['a_powered'] * rel_j['a_powered']) % n
        # Combined residue should be a perfect square
        combined = rel_i['residue'] * rel_j['residue']
        y = int(math.isqrt(combined))
        if y * y != combined:
            if verbose:
                print(f"  Combined residue {combined} is not a perfect square.")
            # Still try GCD
            y = int(math.isqrt(combined))

    g1 = math.gcd(x - y, n)
    g2 = math.gcd(x + y, n)

    if verbose:
        print(f"  x = {x}, y = {y}")
        print(f"  gcd(x-y, n) = gcd({x-y}, {n}) = {g1}")
        print(f"  gcd(x+y, n) = gcd({x+y}, {n}) = {g2}")

    for g in [g1, g2]:
        if 1 < g < n:
            if verbose:
                print(f"\n  ✓ Found nontrivial factor: {g}")
                print(f"  ✓ {n} = {g} × {n // g}")
            return g

    if verbose:
        print(f"  Trivial factors only. Retry with different parameters.")
    return None


def demo_orbit_structure():
    """Demonstrate the orbit structure and CRT decomposition."""
    print("\n" + "=" * 60)
    print("DEMO 1: Orbit Structure and CRT Decomposition")
    print("=" * 60)

    p, q = 7, 11
    n = p * q  # 77

    print(f"\nn = {p} × {q} = {n}")
    print(f"\nSquaring orbits mod {n} decompose via CRT into")
    print(f"orbits mod {p} × orbits mod {q}:")

    for start in [2, 3, 5, 10]:
        orbit_n = squaring_orbit(start, n, 20)
        orbit_p = squaring_orbit(start % p, p, 20)
        orbit_q = squaring_orbit(start % q, q, 20)

        print(f"\n  Start = {start}:")
        print(f"    mod {n}: {' → '.join(str(x) for x in orbit_n[:8])}")
        print(f"    mod {p}:  {' → '.join(str(x) for x in orbit_p[:8])}")
        print(f"    mod {q}: {' → '.join(str(x) for x in orbit_q[:8])}")
        print(f"    CRT check: {start} mod {p} = {start % p}, mod {q} = {start % q}")

    # Show period relationship
    print(f"\n  Orbit periods:")
    for start in [2, 3, 5]:
        orbit_n = squaring_orbit(start, n, 100)
        orbit_p = squaring_orbit(start % p, p, 100)
        orbit_q = squaring_orbit(start % q, q, 100)

        # Find periods (crude)
        def find_period(orbit):
            for i in range(len(orbit)):
                for j in range(i + 1, len(orbit)):
                    if orbit[i] == orbit[j]:
                        return j - i
            return len(orbit)

        per_n = find_period(orbit_n)
        per_p = find_period(orbit_p)
        per_q = find_period(orbit_q)
        print(f"    start={start}: period_n={per_n}, period_p={per_p}, "
              f"period_q={per_q}, lcm(p,q)={math.lcm(per_p, per_q)}")


def demo_smooth_numbers():
    """Demonstrate smooth number detection in orbits."""
    print("\n" + "=" * 60)
    print("DEMO 2: Smooth Number Detection in Squaring Orbits")
    print("=" * 60)

    n = 15 * 17  # 255
    B = 7
    print(f"\nn = {n}, B = {B}")
    print(f"Factor base: primes ≤ {B} = {{2, 3, 5, 7}}")

    for start in [2, 3, 7, 11, 13]:
        orbit = squaring_orbit(start, n, 15)
        print(f"\n  Orbit of {start} mod {n}:")
        for k, val in enumerate(orbit[:10]):
            smooth, factors = is_b_smooth(val, B)
            status = f"✓ {B}-smooth = {dict(factors)}" if smooth and val > 1 else \
                     f"✓ trivial" if val <= 1 else "✗ not smooth"
            print(f"    step {k}: {start}^(2^{k}) ≡ {val} (mod {n})  {status}")


def demo_factoring():
    """Demonstrate full IOF factoring on several examples."""
    print("\n" + "=" * 60)
    print("DEMO 3: Full IOF Factoring")
    print("=" * 60)

    test_cases = [
        (77, "7 × 11"),
        (221, "13 × 17"),
        (323, "17 × 19"),
        (1147, "31 × 37"),
        (10403, "101 × 103"),
    ]

    for n, expected in test_cases:
        print(f"\n{'─' * 50}")
        print(f"Target: {n} (expected: {expected})")
        result = iof_factor(n, verbose=True)
        if result is None:
            # Try with different B values
            for B in [10, 20, 30, 50]:
                result = iof_factor(n, B=B, verbose=False)
                if result:
                    print(f"  Found with B={B}: {n} = {result} × {n // result}")
                    break


def demo_complexity():
    """Demonstrate the L-notation complexity scaling."""
    print("\n" + "=" * 60)
    print("DEMO 4: Complexity Scaling (L-notation)")
    print("=" * 60)

    print(f"\nL_n[1/2, c] = exp(c · √(ln n · ln ln n))")
    print(f"\n{'Bits':>6} {'n (approx)':>15} {'L[1/2,1]':>15} {'L[1/2,√2]':>15} {'√n':>15}")
    print(f"{'─' * 6} {'─' * 15} {'─' * 15} {'─' * 15} {'─' * 15}")

    for bits in [64, 128, 256, 512, 1024, 2048, 4096]:
        ln_n = bits * math.log(2)
        ln_ln_n = math.log(ln_n) if ln_n > 0 else 1

        L_half_1 = math.exp(math.sqrt(ln_n * ln_ln_n))
        L_half_sqrt2 = math.exp(math.sqrt(2) * math.sqrt(ln_n * ln_ln_n))
        sqrt_n = 2 ** (bits / 2)

        def fmt(x):
            e = math.log10(x) if x > 0 else 0
            return f"10^{e:.1f}"

        print(f"{bits:>6} {fmt(2**bits):>15} {fmt(L_half_1):>15} {fmt(L_half_sqrt2):>15} {fmt(sqrt_n):>15}")

    print(f"\nNote: L[1/2, c] is sub-exponential — grows faster than polynomial")
    print(f"but much slower than exponential (√n).")


if __name__ == "__main__":
    print("╔" + "═" * 58 + "╗")
    print("║  Integer Orbit Factoring (IOF) — Interactive Demo        ║")
    print("║  Demonstrating orbit structure, smooth sieves, and       ║")
    print("║  sub-exponential factoring complexity                    ║")
    print("╚" + "═" * 58 + "╝")

    demo_orbit_structure()
    demo_smooth_numbers()
    demo_factoring()
    demo_complexity()

    print("\n" + "=" * 60)
    print("All demos completed successfully!")
    print("=" * 60)
