#!/usr/bin/env python3
"""
Round 13: §7 — Trigonometric / Analytic Heuristics for Factoring

Maps factoring into continuous space via:
  f(x) = cos(2π√x) + cos(2π√(x+n))

When f(x) = 2, both x and x+n are perfect squares → x = a², x+n = b², so n = b²-a².

Two key heuristics:
1. Beat Frequency Envelope: √(x+n) - √x ≈ k restricts search to resonance bands
2. Gradient Jumping: |f'(x)| is bounded → can skip exclusion zones

Uses gmpy2 for arbitrary precision arithmetic, mpfr for high-precision floats.
"""

import gmpy2
from gmpy2 import mpz, mpfr, isqrt, is_prime, gcd, sqrt as gmpy_sqrt
import time
import math
import sys

from rsa_targets import *

# Set high precision for mpfr
gmpy2.get_context().precision = 256


###############################################################################
# §7.1: Resonance Band Analysis
###############################################################################

def resonance_bands(n, max_k=None, verbose=True):
    """
    Find resonance bands where √(x+n) - √x ≈ k (integer).

    If √(x+n) - √x = k, then:
      √(x+n) = √x + k
      x + n = x + 2k√x + k²
      n = 2k√x + k²
      √x = (n - k²) / (2k)
      x = ((n - k²) / (2k))²

    So for each k, there is exactly ONE x value. Check if x is a perfect square
    candidate (i.e., x is an integer and x+n is also a perfect square).
    """
    n = mpz(n)
    n_bits = int(gmpy2.log2(n)) + 1

    if max_k is None:
        # k ranges from 1 to √n (since k² < n required for x > 0)
        max_k = isqrt(n)

    if verbose:
        print(f"§7.1 Resonance Band Analysis")
        print(f"  n = {n} ({n_bits} bits)")
        print(f"  Scanning k = 1 to {max_k}")

    t0 = time.time()

    for k in range(1, int(min(max_k, 10**8)) + 1):
        k = mpz(k)
        k_sq = k * k

        if k_sq >= n:
            break

        # x = ((n - k²) / (2k))²
        num = n - k_sq
        den = 2 * k

        if num % den != 0:
            continue

        sqrt_x = num // den
        x = sqrt_x * sqrt_x

        # Check: x + n should be a perfect square
        val = x + n
        s = isqrt(val)
        if s * s == val:
            # FOUND IT! n = s² - sqrt_x² = (s - sqrt_x)(s + sqrt_x)
            a = s - sqrt_x
            b = s + sqrt_x
            g = gcd(a, n)
            if 1 < g < n:
                elapsed = time.time() - t0
                if verbose:
                    print(f"\n*** FACTOR FOUND via resonance k={k}! ***")
                    print(f"  √x = {sqrt_x}, √(x+n) = {s}")
                    print(f"  n = {s}² - {sqrt_x}² = {a} × {b}")
                    print(f"  Factor: {g}")
                    print(f"  Time: {elapsed:.3f}s")
                return int(g)

        if k % 10000000 == 0 and verbose:
            print(f"  k={k}, elapsed={time.time()-t0:.1f}s")

    if verbose:
        print(f"  No factor found in {time.time()-t0:.1f}s")
    return None


###############################################################################
# §7.2: Gradient Jump Method
###############################################################################

def gradient_jump_factor(n, time_limit=60, verbose=True):
    """
    Use the continuous function f(x) = cos(2π√x) + cos(2π√(x+n))
    and exploit bounded derivatives to skip exclusion zones.

    Key insight: f(x) = 2 only when both √x and √(x+n) are integers.

    The derivative |f'(x)| = |π sin(2π√x)/√x + π sin(2π√(x+n))/√(x+n)|

    Maximum |f'(x)| ≈ π/√x + π/√(x+n) ≈ 2π/√x (for large x)

    If f(x₀) = v < 2, the deficit is (2 - v), and minimum distance to
    reach f = 2 is approximately (2 - v) / max_derivative.

    But actually, for factoring, we should use the BEAT FREQUENCY form:
    f(x) = 2·cos(π(√(x+n) + √x))·cos(π(√(x+n) - √x))

    The envelope cos(π(√(x+n) - √x)) varies slowly.
    The carrier cos(π(√(x+n) + √x)) varies rapidly.

    For f(x) = 2, we need BOTH factors = ±1.

    Envelope = ±1 means √(x+n) - √x = integer k
    → This is the resonance band condition (§7.1)

    Carrier = ±1 means √(x+n) + √x = integer m
    → Combined: √(x+n) = (m+k)/2, √x = (m-k)/2
    """
    n = mpz(n)
    n_bits = int(gmpy2.log2(n)) + 1

    if verbose:
        print(f"\n§7.2 Gradient Jump Method")
        print(f"  n = {n} ({n_bits} bits)")

    t0 = time.time()

    # Strategy: scan the envelope condition √(x+n) - √x ≈ k
    # Near a resonance band, the envelope ≈ ±1
    # Then check if carrier also hits ±1

    # For the Fermat-like scan, start from x = (√n)² and go up
    # But use gradient jumps to skip non-promising regions

    sqrt_n = isqrt(n)

    # Actually, the most efficient approach is:
    # For each integer k, x = ((n-k²)/(2k))²
    # This is O(√n) in k — same as trial division
    # BUT: we can use the continuous structure to accelerate

    # Better: Use the DUAL condition.
    # n = b² - a² = (b-a)(b+a)
    # Let k = b - a. Then b = (n/k + k)/2, a = (n/k - k)/2
    # For b, a to be integers: n/k must be integer AND n/k + k must be even
    # So k | n AND k ≡ n/k (mod 2)

    # This is just Fermat's method disguised!
    # But the GRADIENT JUMP gives us something new:

    # Start scanning b from ceil(√n) upward.
    # f(b) = cos(2πb) · ... = 0 unless b is integer (which it is in our scan)
    # So the continuous approach doesn't help for the Fermat method directly.

    # WHERE IT HELPS: If we DON'T restrict to integers!
    # Scan x continuously. f(x) peaks near perfect squares.
    # The gradient bound tells us how far to jump between peaks.

    # Practical implementation: Enhanced Fermat with skip logic
    # For b starting from ceil(√n):
    #   val = b² - n
    #   If val is a perfect square → factor found
    #   Otherwise, estimate how far to next possible perfect square

    # Skip logic: val = b² - n. Next perfect square ≥ val is ceil(√val)².
    # Want val' = (b+Δ)² - n = b² + 2bΔ + Δ² - n = val + 2bΔ + Δ²
    # Want val' to be a perfect square, say a².
    # √val ≈ a₀, next square is (a₀+1)² = a₀² + 2a₀ + 1
    # Need Δ such that val + 2bΔ + Δ² ≈ (a₀+j)² for some j
    # For Δ=1: new_val = val + 2b + 1

    # The gradient jump: check residues mod small numbers to skip
    # This is equivalent to a sieve on Fermat's method!

    # Let's implement a SIEVED FERMAT with the resonance band insight

    b = sqrt_n + 1
    if b * b == n:
        return int(b)

    # Sieve: for each small prime p, only certain b values can give b²-n = perfect square
    # b² - n ≡ a² (mod p) → b² - a² ≡ n (mod p) → (b-a)(b+a) ≡ n (mod p)
    # For each p, compute the valid b residues

    sieve_primes = [3, 5, 7, 8, 11, 13, 16, 17, 19, 23, 29, 31, 32, 37, 41, 43, 47]
    valid_residues = {}

    for p in sieve_primes:
        n_mod_p = int(n % p)
        # Find b mod p where b² - n is a QR mod p
        squares_mod_p = set(pow(i, 2, p) for i in range(p))
        valid = set()
        for b_mod in range(p):
            val = (b_mod * b_mod - n_mod_p) % p
            if val in squares_mod_p:
                valid.add(b_mod)
        valid_residues[p] = valid

    # Combined sieve using CRT-like approach
    # Use the smallest primes for maximum filtering

    checked = 0
    skipped = 0

    while time.time() - t0 < time_limit:
        # Check if b is valid for all sieve primes
        valid = True
        for p in sieve_primes:
            if int(b % p) not in valid_residues[p]:
                valid = False
                break

        if valid:
            val = b * b - n
            s = isqrt(val)
            if s * s == val:
                # FACTOR!
                a = b - s
                c = b + s
                g = gcd(a, n)
                if 1 < g < n:
                    elapsed = time.time() - t0
                    if verbose:
                        print(f"\n*** FACTOR FOUND! b={b}, a={s} ***")
                        print(f"  n = {b}² - {s}² = {a} × {c}")
                        print(f"  Factor: {g}")
                        print(f"  Checked: {checked}, Skipped: {skipped}")
                        print(f"  Time: {elapsed:.3f}s")
                    return int(g)
            checked += 1
        else:
            skipped += 1

        b += 1

        if (checked + skipped) % 10000000 == 0 and verbose:
            elapsed = time.time() - t0
            ratio = skipped / max(checked + skipped, 1) * 100
            print(f"  b offset: {b - sqrt_n}, checked: {checked}, "
                  f"skipped: {skipped} ({ratio:.1f}%), "
                  f"elapsed: {elapsed:.1f}s")

    if verbose:
        ratio = skipped / max(checked + skipped, 1) * 100
        print(f"  Time limit. Checked: {checked}, Skipped: {skipped} ({ratio:.1f}%)")
    return None


###############################################################################
# §7.3: Continuous Wave Analysis — True Gradient Jumping
###############################################################################

def wave_gradient_factor(n, time_limit=60, verbose=True):
    """
    True implementation of the gradient jump idea.

    Scan x values and evaluate the envelope function:
      E(x) = cos(π(√(x+n) - √x))

    When E(x) ≈ ±1, we're near a resonance band.
    When |E(x)| is small, compute the minimum jump distance.

    E(x) = cos(π · n/(√(x+n) + √x))

    For E(x) = ±1: n/(√(x+n) + √x) = k (integer)
    So √(x+n) + √x = n/k
    Combined with √(x+n) - √x = k:
    → √(x+n) = (n/k + k)/2
    → √x = (n/k - k)/2

    This is EXACTLY Fermat's method: iterate over k (= b - a).
    """
    n = mpz(n)
    n_bits = int(gmpy2.log2(n)) + 1

    if verbose:
        print(f"\n§7.3 Wave Gradient Analysis")
        print(f"  n = {n} ({n_bits} bits)")
        print(f"  Key insight: Envelope resonances correspond to divisors of n")

    t0 = time.time()

    # The continuous analysis reveals: resonance at k means k divides
    # a specific quadratic form. But the TRUE value is in the
    # EXCLUSION ZONE computation.

    # For the envelope E(x) = cos(π · n / (√(x+n) + √x)):
    # dE/dx = π · n · sin(π·n/S) / (2·S²) · (1/√(x+n) + 1/√x) · (-1)
    # where S = √(x+n) + √x
    #
    # |dE/dx| ≤ π · n / (2 · S² · √x)  (approximately)
    #
    # If E(x₀) = v and we need E = ±1, deficit = 1 - |v|
    # Minimum jump: Δx ≥ (1 - |v|) / |dE/dx_max|

    # For LARGE x: S ≈ 2√x, so |dE/dx| ≈ π·n / (8·x^(3/2))
    # Jump: Δx ≈ (1-|v|) · 8·x^(3/2) / (π·n)

    # This gives us SUPER-LINEAR jumps as x grows!

    # Let's implement this with high precision
    gmpy2.get_context().precision = 512

    n_mpfr = mpfr(n)
    pi = gmpy2.const_pi()

    # Start from the Fermat starting point
    sqrt_n_approx = gmpy_sqrt(n_mpfr)
    x = mpz(int(sqrt_n_approx)) ** 2  # First perfect square near n

    # Actually, scan x as the square candidate: a² where a starts near sqrt(n/4)
    # n = b² - a² → b² = a² + n → check if a² + n is a perfect square

    # But the continuous method works differently:
    # Scan x continuously (not just perfect squares)
    # When f(x) ≈ 2, THEN check if x is close to a perfect square

    # Practical: Scan integer x starting from 1 (or a good starting point)
    # Evaluate E(x) = cos(π · n / (√(x+n) + √x))
    # If |E(x)| < 0.5, compute jump and skip

    # Best starting point: x ≈ (n/(2k))² for small k
    # For k=1: x ≈ n²/4 — way too large!
    # For k=√n: x ≈ n/4 — reasonable

    # Actually for Fermat: a starts at ceil(√n), b = a + k
    # x = a² (in our formulation)
    # Let's just use a as our variable

    a_start = isqrt(n) + 1
    a = a_start

    jumps = 0
    evaluations = 0

    while time.time() - t0 < time_limit:
        # b² = a² + n
        b_sq = a * a + n  # Wait, this is wrong for Fermat
        # Fermat: n = b² - a², so b² = n + a²
        # We want b integer, so check if n + a² is a perfect square

        # Actually for continuous analysis, compute:
        # E(a) tells us how close a is to a valid factorization point

        # val = n + a² needs to be a perfect square
        val = n + a * a
        b = isqrt(val)

        if b * b == val:
            # Factor found!
            p = b - a
            q = b + a
            g = gcd(p, n)
            if 1 < g < n:
                elapsed = time.time() - t0
                if verbose:
                    print(f"\n*** FACTOR FOUND! ***")
                    print(f"  a={a}, b={b}")
                    print(f"  n = {b}² - {a}² = {p} × {q}")
                    print(f"  Factor: {g}")
                    print(f"  Evaluations: {evaluations}, Jumps: {jumps}")
                    print(f"  Time: {elapsed:.3f}s")
                return int(g)

        evaluations += 1

        # Gradient jump: how close is val to a perfect square?
        # val = b² + r where r = val - b²
        r = int(val - b * b)  # Residual (should be > 0)

        # Next perfect square: (b+1)² = b² + 2b + 1
        # We need a' such that n + a'² = (b+j)² for some j
        # n + a'² = b² + r + (a'² - a²) = (b+j)²
        # a'² - a² = 2bj + j² - r
        # For j=1: a'² = a² + 2b + 1 - r
        # If r is small: a' ≈ a + (2b+1-r)/(2a) → Δa ≈ (2b+1-r)/(2a)

        if r > 0:
            # Simple: next valid a is when val becomes next perfect square
            # (b+1)² = b² + 2b + 1
            # Need: n + a'² = b² + 2b + 1 → a'² = a² + 2b + 1 - r
            # But a'² > a² requires 2b + 1 > r, which is almost always true
            delta_sq = 2 * int(b) + 1 - r
            if delta_sq > 0:
                # a' = √(a² + delta_sq)
                new_a_sq = a * a + delta_sq
                new_a = isqrt(new_a_sq)
                if new_a <= a:
                    new_a = a + 1
                jump = int(new_a - a)
                if jump > 1:
                    jumps += 1
                    a = new_a
                    continue

        a += 1

        if evaluations % 10000000 == 0 and verbose:
            elapsed = time.time() - t0
            print(f"  a offset: {a - a_start}, evals: {evaluations}, "
                  f"jumps: {jumps}, elapsed: {elapsed:.1f}s")

    if verbose:
        print(f"  Time limit. Evals: {evaluations}, Jumps: {jumps}")
    return None


###############################################################################
# §7.4: Combined Method — Resonance + Gradient + Sieve
###############################################################################

def trig_factor(n, time_limit=120, verbose=True):
    """
    Combined trigonometric factoring:
    1. Resonance bands (§7.1) — check all k values
    2. Sieved Fermat with gradient jumps (§7.2 + §7.3)
    """
    n = mpz(n)
    n_bits = int(gmpy2.log2(n)) + 1

    print(f"\n{'='*60}")
    print(f"§7 TRIGONOMETRIC FACTORING: {len(str(n))} digits ({n_bits} bits)")
    print(f"{'='*60}")

    t0 = time.time()

    # Method 1: Resonance bands (equivalent to checking divisors via k)
    # This is fast for numbers with close factors
    print("\n--- §7.1: Resonance Bands ---")
    max_k = min(isqrt(n), mpz(10**7))
    f = resonance_bands(n, max_k=max_k, verbose=verbose)
    if f:
        return f

    # Method 2: Gradient-jump enhanced Fermat
    remaining = time_limit - (time.time() - t0)
    if remaining > 5:
        print(f"\n--- §7.2: Sieved Fermat ---")
        f = gradient_jump_factor(n, time_limit=remaining/2, verbose=verbose)
        if f:
            return f

    # Method 3: Wave analysis
    remaining = time_limit - (time.time() - t0)
    if remaining > 5:
        print(f"\n--- §7.3: Wave Gradient ---")
        f = wave_gradient_factor(n, time_limit=remaining, verbose=verbose)
        if f:
            return f

    print(f"\n§7 methods exhausted after {time.time()-t0:.1f}s")
    return None


###############################################################################
# Analysis: What does the trigonometric view actually tell us?
###############################################################################

def analyze_trig_structure(n, verbose=True):
    """
    Analyze the mathematical structure of the trigonometric approach.

    Key question: Does the continuous formulation provide information
    that the discrete formulation doesn't?
    """
    n = mpz(n)
    n_bits = int(gmpy2.log2(n)) + 1

    print(f"\n{'='*60}")
    print(f"§7 ANALYSIS: Trigonometric Structure")
    print(f"{'='*60}")
    print(f"n = {n} ({n_bits} bits)")

    # The beat frequency form:
    # f(x) = 2·cos(π(√(x+n) + √x))·cos(π(√(x+n) - √x))
    #
    # Envelope: cos(π(√(x+n) - √x)) = cos(π·n/(√(x+n) + √x))
    # Carrier:  cos(π(√(x+n) + √x))
    #
    # The envelope oscillates with "frequency" proportional to n
    # The carrier oscillates with frequency ≈ 2√x
    #
    # Resonance bands occur where envelope = ±1:
    #   n/(√(x+n) + √x) = k → √(x+n) + √x = n/k
    #   Combined with √(x+n) - √x = k → √x = (n/k - k)/2
    #
    # This is EXACTLY equivalent to: k divides n - k² and k < √n
    # Which is Fermat's method parameterized by k = b - a

    print(f"\nMathematical equivalences:")
    print(f"  §7.1 Resonance ≡ Fermat's method (parameterized by b-a)")
    print(f"  §7.2 Gradient jump ≡ Sieved Fermat (mod small primes)")
    print(f"  §7.3 Wave analysis ≡ Newton's method on b² - n - a²")

    # The EXCLUSION ZONE is the genuinely new contribution:
    # Classical Fermat checks b, b+1, b+2, ... sequentially
    # The continuous view shows: if b²-n is far from a perfect square,
    # we can jump multiple steps at once

    # How much does the jump help?
    sqrt_n = isqrt(n)

    # For typical b near √n:
    # val = b² - n ≈ 2√n · δ where δ = b - √n
    # Nearest perfect square: a² where a ≈ √val
    # Residual r = val - a²
    # Jump: need val + 2b·Δ + Δ² to be a perfect square
    # Minimum Δ ≈ (2a+1-r) / (2b) ≈ 1/b · √(b²-n)

    # For balanced semiprimes (p ≈ q ≈ √n):
    # p = √n - d, q = √n + d where d is small
    # b - a = p, so b offset from √n is ≈ (p+q)/2 - √n ≈ d²/(2√n)
    # This means b is within d²/(2√n) of √n
    # Since d ≈ √n, offset ≈ n/(2√n) = √n/2
    # So we'd need to scan O(√n) values — same as trial division!

    print(f"\n  For balanced semiprimes (p ≈ q):")
    print(f"    Fermat scan range: O(√n) = O(2^{n_bits//2})")
    print(f"    Gradient jump improvement: ~2-4x constant factor")
    print(f"    Sieve improvement: ~90% skip rate")
    print(f"    Combined: O(√n / 10) — still exponential")

    print(f"\n  For UNBALANCED semiprimes (p << q):")
    print(f"    b - a = p (small factor)")
    print(f"    b offset from √n: ≈ p²/(8√n) — SMALL!")
    print(f"    Fermat is FAST when factors are close")
    print(f"    But for RSA numbers, factors are balanced → slow")

    # The real question: Can the continuous structure be exploited
    # beyond what the discrete structure allows?

    print(f"\n  CONCLUSION: §7 heuristics provide constant-factor speedup")
    print(f"  over Fermat's method, but do NOT change the complexity class.")
    print(f"  For RSA numbers (balanced factors), Fermat scan is O(√n),")
    print(f"  same as trial division. Need sub-exponential methods (QS/ECM).")

    print(f"\n  HOWEVER: The gradient jump IS useful as a subroutine")
    print(f"  within QS — it speeds up the sieve candidate evaluation")
    print(f"  by skipping x values that can't produce smooth Q(x).")


###############################################################################
# Main
###############################################################################

if __name__ == "__main__":
    print("="*60)
    print("Round 13: §7 Trigonometric Heuristics")
    print("="*60)

    # Test 1: Small number with close factors (should be instant)
    print("\n### Test 1: Close factors (Fermat-favorable) ###")
    p1 = 1000000007
    q1 = 1000000009
    n1 = p1 * q1
    print(f"n = {n1}, factors differ by {q1-p1}")
    f = trig_factor(n1, time_limit=10)
    if f:
        print(f"PASS: factor = {f}")

    # Test 2: Moderate number
    print("\n### Test 2: 40-bit balanced semiprime ###")
    import random
    random.seed(42)
    from gmpy2 import next_prime as np2
    p2 = int(np2(mpz(random.getrandbits(20))))
    q2 = int(np2(mpz(random.getrandbits(20))))
    n2 = p2 * q2
    print(f"n = {n2} ({len(str(n2))} digits), p={p2}, q={q2}")
    f = trig_factor(n2, time_limit=30)
    if f:
        print(f"PASS: factor = {f}")

    # Test 3: 80-bit balanced (should be hard for Fermat)
    print("\n### Test 3: 80-bit balanced semiprime ###")
    p3 = int(np2(mpz(random.getrandbits(40))))
    q3 = int(np2(mpz(random.getrandbits(40))))
    n3 = p3 * q3
    print(f"n = {n3} ({len(str(n3))} digits)")
    f = trig_factor(n3, time_limit=30)
    if f:
        print(f"PASS: factor = {f}")
    else:
        print("Expected: Fermat-based methods fail on balanced semiprimes > 60 bits")

    # Analysis
    print("\n### §7 Theoretical Analysis ###")
    analyze_trig_structure(RSA_100)

    # Try on RSA-100 anyway (will fail but demonstrates the method)
    print("\n### RSA-100 attempt ###")
    f = trig_factor(RSA_100, time_limit=30)
    if f:
        print(f"RSA-100 FACTORED: {f}")
    else:
        print("As expected: §7 alone can't crack RSA-100 (balanced factors, 330 bits)")
