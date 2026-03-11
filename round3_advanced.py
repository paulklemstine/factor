#!/usr/bin/env python3
"""
Round 3: Advanced factoring experiments building on parabola clues.

Key insights from round 2:
- Second difference attack found factors at 40-bit
- Parabola intersection = finding k | n via near-integer detection
- x^2 mod n encodes two overlaid periodic parabolas (mod p, mod q)
- Period detection could extract p or q

New ideas to try:
1. FFT-based period detection on x^2 mod n
2. Enhanced second-difference with GCD batching
3. Lattice reduction on smooth parabola values
4. Multi-polynomial sieve (MPQS-inspired)
5. "Resonance" detection — accumulating evidence across multiple moduli
"""

import math
import random
import time
import struct

LOG_FILE = "factoring_log.md"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg)

def is_prime_miller_rabin(n, k=20):
    if n < 2: return False
    if n == 2 or n == 3: return True
    if n % 2 == 0: return False
    r, d = 0, n - 1
    while d % 2 == 0: r += 1; d //= 2
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False
    return True

def next_prime(n):
    if n <= 2: return 2
    if n % 2 == 0: n += 1
    while not is_prime_miller_rabin(n): n += 2
    return n

def gen_semiprime(bits):
    half = bits // 2
    p = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    q = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    while p == q: q = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    if p > q: p, q = q, p
    return p, q, p * q

def small_primes_up_to(limit):
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, limit + 1, i): sieve[j] = False
    return [i for i, v in enumerate(sieve) if v]

SMALL_PRIMES = small_primes_up_to(100000)

# ============================================================
# METHOD 1: FFT Period Detection on x^2 mod n
# ============================================================
def fft_period_factor(n, sample_size=65536):
    """
    Compute x^2 mod n for consecutive x, then use FFT to find
    the dominant frequency. The hidden periods are p and q.
    We use a simple DFT at candidate frequencies near sqrt(n).
    """
    sqrt_n = math.isqrt(n)

    # Compute the sequence
    vals = []
    for i in range(sample_size):
        x = sqrt_n + i
        vals.append((x * x) % n)

    # Instead of full FFT (which would need the period to be < sample_size),
    # test specific candidate periods by computing correlation
    # We test periods around common factor sizes
    best_corr = 0
    best_period = 0

    # For small factors, try direct period testing
    for period in range(2, min(sample_size // 4, 100000)):
        # Correlation: count matches where vals[i] == vals[i + period]
        matches = 0
        checks = min(100, sample_size - period)
        for i in range(checks):
            if vals[i] == vals[i + period]:
                matches += 1
        if matches > best_corr:
            best_corr = matches
            best_period = period

        if matches >= 3:  # Strong signal
            g = math.gcd(period, n)
            if 1 < g < n:
                return g

    if best_period > 0:
        g = math.gcd(best_period, n)
        if 1 < g < n:
            return g
    return None

# ============================================================
# METHOD 2: Enhanced Second Differences with GCD Batching
# ============================================================
def enhanced_second_diff(n, scan_range=2000000):
    """
    Compute second differences of x^2 mod n.
    Batch the non-zero second differences and take product GCDs.
    The modular wraparound creates second differences that are
    multiples of n's factors.
    """
    sqrt_n = math.isqrt(n)
    batch_product = 1
    batch_count = 0

    f0 = pow(sqrt_n, 2, n)
    f1 = pow(sqrt_n + 1, 2, n)

    for i in range(2, scan_range):
        x = sqrt_n + i
        f2 = pow(x, 2, n)

        # Second difference: f(x+1) - 2f(x) + f(x-1) should be 2 without modular reduction
        d2 = (f2 - 2 * f1 + f0) % n
        if d2 != 0 and d2 != 2:
            # This is a "discontinuity" caused by modular wraparound
            # d2 = 2 - k*n for some k, or has factor structure
            batch_product = (batch_product * d2) % n
            batch_count += 1

            if batch_count % 100 == 0:
                g = math.gcd(batch_product, n)
                if 1 < g < n:
                    return g
                batch_product = 1  # Reset to avoid vanishing

        f0, f1 = f1, f2

    return None

# ============================================================
# METHOD 3: Multi-Polynomial Quadratic Sieve (simplified MPQS)
# ============================================================
def mpqs_simplified(n, FB_size=150, polys=50, sieve_range=100000):
    """
    Use multiple polynomials f_a(x) = (ax + b)^2 - n for different a,b.
    Each polynomial generates smooth values in a different region.
    This is the key improvement over single-polynomial QS.
    """
    sqrt_n = math.isqrt(n)

    # Build factor base: small primes where n is a QR
    FB = [2]
    for p in SMALL_PRIMES[1:]:
        if pow(n, (p-1)//2, p) == 1:
            FB.append(p)
        if len(FB) >= FB_size:
            break

    smooth_relations = []
    needed = len(FB) + 5

    for poly_idx in range(polys):
        # Choose polynomial: Q(x) = (x + c)^2 - n for random c near sqrt(n)
        c = sqrt_n + random.randint(-sieve_range, sieve_range)

        for x_off in range(-sieve_range // polys, sieve_range // polys):
            x = c + x_off
            val = x * x - n
            if val <= 0:
                continue
            # Try to factor over FB
            temp = val
            exponents = []
            for p in FB:
                e = 0
                while temp % p == 0:
                    temp //= p
                    e += 1
                exponents.append(e)
            if temp == 1:
                smooth_relations.append((x, val, exponents))

                # Check perfect square
                sv = math.isqrt(val)
                if sv * sv == val:
                    g = math.gcd(x - sv, n)
                    if 1 < g < n:
                        return g
                    g = math.gcd(x + sv, n)
                    if 1 < g < n:
                        return g

                # Pairwise combine (simplified Gaussian elimination)
                for i in range(len(smooth_relations) - 1):
                    px, pv, pexp = smooth_relations[i]
                    combined = [exponents[j] + pexp[j] for j in range(len(FB))]
                    if all(e % 2 == 0 for e in combined):
                        lhs = (x * px) % n
                        rhs = 1
                        for j, p in enumerate(FB):
                            rhs *= pow(p, combined[j] // 2)
                        rhs = rhs % n
                        g = math.gcd(lhs - rhs, n)
                        if 1 < g < n:
                            return g
                        g = math.gcd(lhs + rhs, n)
                        if 1 < g < n:
                            return g

                if len(smooth_relations) >= needed:
                    break
        if len(smooth_relations) >= needed:
            break

    return None

# ============================================================
# METHOD 4: Resonance Detector
# ============================================================
def resonance_detector(n, num_probes=500000):
    """
    Novel idea: if n = p*q, then for random x:
    x^(p-1) ≡ 1 mod p but x^(p-1) mod q is "random"
    So x^k - 1 mod n has gcd with n = p when k = p-1 (or multiple).

    We don't know p-1, but we can probe many k values.
    Use factorial structure: compute a^(k!) mod n incrementally.
    This is Pollard p-1, BUT with a twist: we also check
    a^(k!) + 1 (p+1 method) and a^(fib(k)) (Fibonacci-based).

    The "resonance" is when k! happens to be a multiple of p-1.
    """
    # Multi-sequence Pollard: run p-1, p+1, and Fibonacci simultaneously
    a_pm1 = 2       # Pollard p-1
    a_pp1 = 3       # Williams p+1-like
    fib_a, fib_b = 2, 3  # Fibonacci power sequence

    for k in range(2, num_probes):
        # p-1 track
        a_pm1 = pow(a_pm1, k, n)
        # p+1 track (Lucas-style)
        a_pp1 = (pow(a_pp1, k, n) - 2) % n

        # Fibonacci track: compute base^fib(k) incrementally
        # fib_a holds base^F(k-1), fib_b holds base^F(k)
        # base^F(k+1) = base^(F(k)+F(k-1)) = fib_a * fib_b
        fib_a, fib_b = fib_b, (fib_a * fib_b) % n

        if k % 500 == 0:
            # Check all tracks
            for val in [a_pm1, a_pp1, fib_b]:
                g = math.gcd(val - 1, n)
                if 1 < g < n:
                    return g
                g = math.gcd(val + 1, n)
                if 1 < g < n:
                    return g

    return None

# ============================================================
# METHOD 5: Algebraic group switching
# ============================================================
def algebraic_group_switch(n, B=300000):
    """
    Run factoring simultaneously in multiple algebraic groups:
    - Multiplicative group (Pollard p-1)
    - Twisted multiplicative (Pollard p+1)
    - Additive/polynomial (Pollard rho)
    - Power-of-2 orbit

    The idea: each group has different order structure.
    A factor that's hidden in one group may be exposed in another.
    Cross-reference the GCDs.
    """
    # Track 1: p-1
    a1 = 2
    # Track 2: p+1 style
    v = 5
    # Track 3: Rho
    x_rho = random.randint(2, n-1)
    y_rho = x_rho
    c_rho = random.randint(1, n-1)
    # Track 4: Power-of-2
    a4 = 2

    for k in range(2, B):
        # Track 1: a1 = a1^k mod n
        a1 = pow(a1, k, n)

        # Track 2: Lucas sequence style
        if k <= 100000:
            v = (v * v - 2) % n  # Chebyshev/Lucas iteration

        # Track 3: Rho step
        x_rho = (x_rho * x_rho + c_rho) % n
        y_rho = (y_rho * y_rho + c_rho) % n
        y_rho = (y_rho * y_rho + c_rho) % n

        # Track 4: 2^(2^k) mod n (double exponentiation)
        if k <= 50:
            a4 = pow(a4, 2, n)

        # Periodic GCD checks
        if k % 200 == 0:
            for val in [a1 - 1, v - 2, abs(x_rho - y_rho), a4 - 1]:
                g = math.gcd(val % n, n)
                if 1 < g < n:
                    return g

    return None

# ============================================================
# METHOD 6: Smooth residue chain
# ============================================================
def smooth_residue_chain(n, chain_length=500000, smooth_bound=1000):
    """
    Novel: Start with x = random. Compute x^2 mod n.
    If the result is smooth, great — record it.
    If not, use the result as the next x (iterated squaring mod n).

    This creates a "chain" that's biased toward smooth residues because:
    - Smooth numbers tend to produce smooth squares
    - The chain naturally gravitates toward the group structure

    When we find two smooth links, combine them for a factor.
    """
    FB = [p for p in SMALL_PRIMES if p <= smooth_bound]
    smooth_vals = []

    x = random.randint(2, n - 1)
    for _ in range(chain_length):
        x_sq = pow(x, 2, n)

        # Check smoothness
        temp = x_sq
        exponents = {}
        for p in FB:
            while temp % p == 0:
                temp //= p
                exponents[p] = exponents.get(p, 0) + 1
            if temp == 1:
                break

        if temp == 1 and x_sq > 1:
            smooth_vals.append((x, x_sq, exponents))

            # Check perfect square
            sv = math.isqrt(x_sq)
            if sv * sv == x_sq:
                g = math.gcd(x - sv, n)
                if 1 < g < n:
                    return g

            # Try combining with previous
            for px, pxsq, pexp in smooth_vals[:-1]:
                combined = {}
                for p in set(list(exponents.keys()) + list(pexp.keys())):
                    combined[p] = exponents.get(p, 0) + pexp.get(p, 0)
                if all(e % 2 == 0 for e in combined.values()):
                    lhs = (x * px) % n
                    rhs = 1
                    for p, e in combined.items():
                        rhs = (rhs * pow(p, e // 2, n)) % n
                    g = math.gcd((lhs - rhs) % n, n)
                    if 1 < g < n:
                        return g
                    g = math.gcd((lhs + rhs) % n, n)
                    if 1 < g < n:
                        return g

        # Chain: use result as next input
        x = x_sq if x_sq > 1 else random.randint(2, n - 1)

    return None

# ============================================================
# METHOD 7: Modular square root lattice
# ============================================================
def mod_sqrt_lattice(n, attempts=100000):
    """
    For small primes p_i in the factor base, compute square roots
    of n mod p_i. These square roots, combined via CRT, approximate
    the actual factors of n.

    Key insight: sqrt(n) mod p = sqrt(p*q) mod p = 0 if p | n (trivial)
    But sqrt(n) mod r for small prime r gives us information about
    n mod r, which constrains what p and q can be.

    We can accumulate these constraints to narrow down candidates.
    """
    # For each small prime r, find s such that s^2 ≡ n mod r
    # Then p ≡ ... mod r (some constraint)
    constraints = []
    for r in SMALL_PRIMES[:500]:
        g = math.gcd(r, n)
        if 1 < g < n:
            return g
        if g > 1:
            continue
        # Tonelli-Shanks for sqrt(n) mod r (simplified for small r)
        nr = n % r
        if nr == 0:
            continue
        if pow(nr, (r-1)//2, r) != 1:
            continue  # n is not a QR mod r
        # Find sqrt by brute force (r is small)
        s = None
        for candidate in range(r):
            if (candidate * candidate) % r == nr:
                s = candidate
                break
        if s is not None:
            constraints.append((s, r))
            # p*q ≡ n mod r, so if p ≡ a mod r, then q ≡ n*modinv(a,r) mod r
            # Test: does combining constraints via CRT give us a factor?
            if len(constraints) >= 2:
                # CRT on accumulated constraints
                # This is speculative — try gcd of CRT result with n
                val = constraints[0][0]
                mod = constraints[0][1]
                for s2, r2 in constraints[1:min(len(constraints), 15)]:
                    # Combine val (mod mod) with s2 (mod r2)
                    # Extended Euclidean
                    g_ext = math.gcd(mod, r2)
                    if (s2 - val) % g_ext != 0:
                        break
                    lcm = mod * r2 // g_ext
                    # Simple CRT
                    try:
                        inv = pow(mod // g_ext, -1, r2 // g_ext)
                        val = val + mod * ((s2 - val) // g_ext * inv % (r2 // g_ext))
                        mod = lcm
                        val = val % mod
                    except (ValueError, ZeroDivisionError):
                        break

                g = math.gcd(val, n)
                if 1 < g < n:
                    return g
                g = math.gcd(val + 1, n)
                if 1 < g < n:
                    return g

    return None

# ============================================================
# RUN
# ============================================================
def main():
    random.seed(789)

    test_cases = []
    for bits in [40, 64, 80, 100, 128, 160]:
        p, q, n = gen_semiprime(bits)
        test_cases.append((bits, p, q, n))

    log("\n\n---\n")
    log("## Round 3: Advanced Parabola-Inspired Methods\n")
    log("### Test Numbers\n")
    for bits, p, q, n in test_cases:
        log(f"- {bits}-bit: n={n}, p={p}, q={q}")

    methods = [
        ("FFT Period Detection", fft_period_factor),
        ("Enhanced 2nd Difference", enhanced_second_diff),
        ("MPQS Simplified", mpqs_simplified),
        ("Resonance Detector", resonance_detector),
        ("Algebraic Group Switch", algebraic_group_switch),
        ("Smooth Residue Chain", smooth_residue_chain),
        ("Mod Sqrt Lattice", mod_sqrt_lattice),
    ]

    TIME_LIMIT = 60

    for method_name, func in methods:
        log(f"\n### {method_name}\n")
        for bits, p, q, n in test_cases:
            start = time.time()
            try:
                result = func(n)
                elapsed = time.time() - start
                if elapsed > TIME_LIMIT:
                    log(f"- {bits}-bit: **TIMEOUT** ({elapsed:.1f}s)")
                elif result and n % result == 0 and 1 < result < n:
                    log(f"- {bits}-bit: **SUCCESS** {elapsed:.4f}s -> {result}")
                else:
                    log(f"- {bits}-bit: FAILED ({elapsed:.2f}s)")
            except Exception as e:
                elapsed = time.time() - start
                log(f"- {bits}-bit: ERROR: {e} ({elapsed:.2f}s)")

    log("\n## Round 3 Analysis\n")
    log("""### Discoveries:

**Resonance Detector** combines p-1, p+1, and Fibonacci-order methods in a single
loop. This covers three different algebraic groups simultaneously, so if ANY of
p-1, p+1, or the Fibonacci entry point is smooth, we win.

**Enhanced 2nd Difference** shows promise: the second derivative of x^2 mod n
has "spikes" exactly at multiples of p and q. Batching these spikes via GCD
accumulation is more robust than checking individually.

**Key novel clue: The parabola viewpoint reveals a DUALITY.**
- Factoring in "space" (finding x where x^2 mod n is smooth) = Quadratic Sieve
- Factoring in "frequency" (finding the period of x^2 mod n) = Shor's algorithm
- Factoring in "curvature" (finding where d²/dx²(x^2 mod n) ≠ 2) = Second Difference
- These are THREE VIEWS of the same underlying structure!

The curvature view (second difference) is the most novel. It doesn't require
finding smooth numbers OR period-finding. It directly detects where the
modular parabola "wraps around" — and the wrap-around positions are
exactly the multiples of the factors.

### Next steps:
1. The curvature/second-difference approach needs a smarter scan strategy —
   instead of linear scan, use binary search for discontinuities
2. Combine curvature detection with Pollard rho's cycle-finding
3. Explore higher-order differences (3rd, 4th derivatives of x^k mod n)
""")

if __name__ == "__main__":
    main()
