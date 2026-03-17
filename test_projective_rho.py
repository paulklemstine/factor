#!/usr/bin/env python3
"""
Focused test: Projective Rho vs Standard Rho
=============================================
Does the Pythagorean-tree Mobius walk on P^1(Z/NZ) achieve O(sqrt(p))?
Compare directly against standard Pollard rho (x -> x^2 + c mod N).
"""

import gmpy2
from gmpy2 import mpz, gcd, invert, next_prime, is_prime
import math
import time
import random
from collections import defaultdict

BERGGREN_2x2 = [
    ((2, -1), (1, 0)),
    ((2, 1), (1, 0)),
    ((1, 2), (0, 1)),
    ((1, 0), (2, 1)),
    ((0, 1), (1, 2)),
    ((-1, 2), (0, 1)),
    ((1, -2), (0, 1)),
    ((0, 1), (-1, 2)),
    ((2, -1), (0, 1)),
]


def standard_pollard_rho(N):
    """Standard Pollard rho: x -> x^2 + c mod N, Brent's cycle detection, batch GCD."""
    N = int(N)
    if N % 2 == 0:
        return 2, 1
    c = random.randint(1, N - 1)
    x = random.randint(2, N - 1)
    y = x
    product = 1
    steps = 0

    power = 1
    batch = 0

    while True:
        # Move hare
        y = (y * y + c) % N
        steps += 1

        diff = abs(y - x) % N
        if diff == 0:
            # Cycle with no factor — retry with different c
            c = random.randint(1, N - 1)
            x = random.randint(2, N - 1)
            y = x
            power = 1
            continue

        product = product * diff % N
        batch += 1

        if batch >= 128:
            g = math.gcd(product, N)
            if g == N:
                # Overshot — go back and check one by one
                # (simplified: just retry)
                product = 1
                batch = 0
                c = random.randint(1, N - 1)
                x = random.randint(2, N - 1)
                y = x
                power = 1
                continue
            if g > 1:
                return g, steps
            product = 1
            batch = 0

        # Brent: update tortoise at powers of 2
        if steps == power:
            x = y
            power *= 2

        if steps > 10_000_000:
            return None, steps

    return None, steps


def projective_rho_v1(N):
    """
    Projective rho: walk on P^1(Z/NZ) via Mobius transformations.
    State r = m/n mod N. Matrix chosen by hash of r.
    Brent cycle detection + batch GCD.
    """
    N = int(N)

    def step(r):
        # Hash-based matrix selection using multiplicative hash
        h = (r * 2654435769) % (1 << 32)
        mat_idx = (h >> 28) % 9
        (a, b), (c, d) = BERGGREN_2x2[mat_idx]

        num = (a * r + b) % N
        den = (c * r + d) % N

        if den == 0:
            return r + 1  # nudge away from singularity

        g = math.gcd(den, N)
        if 1 < g < N:
            return -g  # found factor

        den_inv = int(invert(mpz(den), mpz(N)))
        return (num * den_inv) % N

    x = 2  # initial r = m/n = 2/1
    y = 2
    product = 1
    steps = 0
    power = 1
    batch = 0

    while steps < 10_000_000:
        y = step(y)
        steps += 1

        if isinstance(y, int) and y < 0:
            return -y, steps

        diff = abs(y - x) % N
        if diff == 0:
            # Degenerate — restart with different seed
            y = random.randint(2, N - 1)
            x = y
            power = steps + 1
            continue

        product = product * diff % N
        batch += 1

        if batch >= 128:
            g = math.gcd(product, N)
            if g == N:
                product = 1
                batch = 0
                y = random.randint(2, N - 1)
                x = y
                power = steps + 1
                continue
            if g > 1:
                return g, steps
            product = 1
            batch = 0

        if steps == power:
            x = y
            power *= 2

    # Final check
    if batch > 0:
        g = math.gcd(product, N)
        if 1 < g < N:
            return g, steps
    return None, steps


def projective_rho_v2_2d(N):
    """
    2D version: track (m, n) mod N and use m-coordinate for collision.
    The state space mod p is (Z/pZ)^2 ~ p^2 elements.
    Birthday on the m-coordinate alone gives O(sqrt(p^2)) = O(p).
    But birthday on the PAIR (m, n) also gives O(p).

    However, if we project to ratio r = m*n^-1 mod N, we get 1D.
    This is v1 above. This v2 tests whether 2D walk with m-only
    birthday is worse (as theory predicts).
    """
    N = int(N)

    m, n = 2, 1
    mx, nx = 2, 1
    product = 1
    steps = 0
    power = 1
    batch = 0

    while steps < 10_000_000:
        # Hash-based matrix selection
        h = (m * 2654435769 + n * 0x517CC1B7) % (1 << 32)
        mat_idx = (h >> 28) % 9
        (a, b), (c, d) = BERGGREN_2x2[mat_idx]
        m, n = (a * m + b * n) % N, (c * m + d * n) % N
        steps += 1

        # Birthday collision on m-coordinate
        diff = abs(m - mx) % N
        if diff > 0:
            product = product * diff % N
            batch += 1

            if batch >= 128:
                g = math.gcd(product, N)
                if g == N:
                    product = 1
                    batch = 0
                    m = random.randint(2, N - 1)
                    n = random.randint(1, N - 1)
                    mx, nx = m, n
                    power = steps + 1
                    continue
                if g > 1:
                    return g, steps
                product = 1
                batch = 0

        if steps == power:
            mx, nx = m, n
            power *= 2

    if batch > 0:
        g = math.gcd(product, N)
        if 1 < g < N:
            return g, steps
    return None, steps


def generate_semiprimes(half_bits, count=10):
    """Generate random semiprimes with factors of approximately half_bits bits each."""
    results = []
    lo = 1 << (half_bits - 1)
    hi = 1 << half_bits
    for _ in range(count):
        p = int(next_prime(mpz(random.randint(lo, hi))))
        # Make q close to p (balanced)
        q = int(next_prime(mpz(p + random.randint(2, max(3, p // 5)))))
        while q == p:
            q = int(next_prime(mpz(q)))
        results.append((p * q, min(p, q), max(p, q)))
    return results


def run_comparison():
    print("=" * 80)
    print("PROJECTIVE RHO vs STANDARD RHO: Head-to-Head Comparison")
    print("=" * 80)
    print()

    # Test across bit sizes
    bit_sizes = [12, 14, 16, 18, 20, 22, 24]
    samples_per_size = 10

    results = defaultdict(lambda: defaultdict(list))

    for half_bits in bit_sizes:
        semiprimes = generate_semiprimes(half_bits, samples_per_size)
        nbits = 2 * half_bits

        for N, p, q in semiprimes:
            sqrt_p = math.sqrt(p)

            # Standard rho
            t0 = time.time()
            factor_std, steps_std = standard_pollard_rho(N)
            time_std = time.time() - t0
            if factor_std and 1 < factor_std < N:
                results[nbits]['std_steps'].append(steps_std)
                results[nbits]['std_ratio'].append(steps_std / sqrt_p)
            else:
                results[nbits]['std_steps'].append(float('inf'))
                results[nbits]['std_ratio'].append(float('inf'))

            # Projective rho v1 (1D)
            t0 = time.time()
            factor_proj, steps_proj = projective_rho_v1(N)
            time_proj = time.time() - t0
            if factor_proj and 1 < factor_proj < N:
                results[nbits]['proj_steps'].append(steps_proj)
                results[nbits]['proj_ratio'].append(steps_proj / sqrt_p)
            else:
                results[nbits]['proj_steps'].append(float('inf'))
                results[nbits]['proj_ratio'].append(float('inf'))

            # 2D walk (m-coordinate birthday)
            t0 = time.time()
            factor_2d, steps_2d = projective_rho_v2_2d(N)
            time_2d = time.time() - t0
            if factor_2d and 1 < factor_2d < N:
                results[nbits]['2d_steps'].append(steps_2d)
                results[nbits]['2d_ratio'].append(steps_2d / sqrt_p)
            else:
                results[nbits]['2d_steps'].append(float('inf'))
                results[nbits]['2d_ratio'].append(float('inf'))

    # Print results
    print(f"{'Bits':>4s} | {'Standard Rho':^30s} | {'Projective Rho (1D)':^30s} | {'2D Walk (m-birthday)':^30s}")
    print(f"{'':>4s} | {'steps/√p':>10s} {'succ':>5s} {'med':>8s} | {'steps/√p':>10s} {'succ':>5s} {'med':>8s} | {'steps/√p':>10s} {'succ':>5s} {'med':>8s}")
    print("-" * 110)

    for nbits in sorted(results.keys()):
        for method, key in [("std", "std"), ("proj", "proj"), ("2d", "2d")]:
            ratios = results[nbits][f'{key}_ratio']
            finite = [r for r in ratios if r < float('inf')]
            steps_list = results[nbits][f'{key}_steps']
            finite_steps = [s for s in steps_list if s < float('inf')]

        def fmt(key):
            ratios = results[nbits][f'{key}_ratio']
            finite = [r for r in ratios if r < float('inf')]
            steps_list = results[nbits][f'{key}_steps']
            finite_steps = [s for s in steps_list if s < float('inf')]
            if finite:
                mean_r = sum(finite) / len(finite)
                med_s = sorted(finite_steps)[len(finite_steps) // 2]
                succ = f"{len(finite)}/{len(ratios)}"
                return f"{mean_r:10.1f} {succ:>5s} {med_s:>8.0f}"
            else:
                return f"{'FAIL':>10s} {'0/'+str(len(ratios)):>5s} {'---':>8s}"

        print(f"{nbits:4d} | {fmt('std')} | {fmt('proj')} | {fmt('2d')}")

    print()
    print("INTERPRETATION:")
    print("  - Standard Rho steps/sqrt(p) should be ~constant (typically 2-5)")
    print("  - Projective Rho (1D) steps/sqrt(p) should also be ~constant if O(sqrt(p))")
    print("  - 2D Walk steps/sqrt(p) should GROW if it's O(p) not O(sqrt(p))")
    print()
    print("  If Projective Rho ratio is bounded and comparable to Standard Rho,")
    print("  the Pythagorean Mobius walk is a legitimate O(sqrt(p)) method.")
    print("  If it's much larger or grows, the Mobius walk has poor mixing.")


if __name__ == "__main__":
    run_comparison()
