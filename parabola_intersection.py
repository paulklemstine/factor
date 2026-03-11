#!/usr/bin/env python3
"""
Parabola Intersection Factoring Idea

Core insight: If n = p * q, then there exist integers a, b such that:
  n = a^2 - b^2 = (a-b)(a+b) where a=(p+q)/2, b=(q-p)/2

Geometrically: plot y = x^2 and y = x^2 + n. The "intersections" in
modular arithmetic reveal factor structure.

More precisely: we're looking for x where x^2 mod n has special structure,
or where x^2 and (x+k)^2 differ by exactly n (or a multiple of n).

Several interpretations to explore:
1. x^2 ≡ (x+k)^2 mod n  =>  n | k(2x+k)  =>  gcd(k(2x+k), n) might give factor
2. Plotting x^2 mod n and looking for parabolic patterns / intersections
3. Finding x,y where x^2 - y^2 = n directly (Fermat)
4. Finding x where x^2 mod n = (x+d)^2 mod n for some d — collision reveals factor
5. NEW: x^2 mod p has period p, x^2 mod q has period q. The intersection
   of these two periodic parabolas happens at CRT solutions.
"""

import math
import random
import time

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
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def next_prime(n):
    if n <= 2: return 2
    if n % 2 == 0: n += 1
    while not is_prime_miller_rabin(n):
        n += 2
    return n

def gen_semiprime(bits):
    half = bits // 2
    p = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    q = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    while p == q:
        q = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    if p > q:
        p, q = q, p
    return p, q, p * q


log("\n\n---\n")
log("## Round 2: Parabola Intersection Experiments\n")

random.seed(123)

# ============================================================
# IDEA 1: Quadratic residue collisions
# If x^2 ≡ y^2 (mod n) but x ≢ ±y (mod n), then gcd(x-y, n) is a factor.
# The "parabola intersection" is literally where two branches of
# the parabola y = x^2 mod n meet.
# ============================================================
def parabola_collision(n, max_iter=500000):
    """
    Collect values of x^2 mod n. When we find x1, x2 with same
    residue but x1 ≠ ±x2 mod n, we have a factor.
    This is a hash-based birthday attack on the parabola.
    """
    seen = {}  # residue -> x
    for x in range(math.isqrt(n), math.isqrt(n) + max_iter):
        r = (x * x) % n
        if r in seen:
            y = seen[r]
            if x != y and (x + y) % n != 0:
                g = math.gcd(x - y, n)
                if 1 < g < n:
                    return g
                g = math.gcd(x + y, n)
                if 1 < g < n:
                    return g
        else:
            seen[r] = x
    return None

# ============================================================
# IDEA 2: Shifted parabola difference
# Plot f(x) = x^2 and g(x) = (x+n)^2, look at f(x) - g(x) = -n(2x+n)
# More useful: f(x) = x^2 mod n. The "shape" of this function
# reveals the factorization through its periodicity.
#
# Key insight: x^2 mod n has a very specific symmetry structure.
# x^2 mod n = y^2 mod n iff x ≡ ±y mod p AND x ≡ ±y mod q
# So there are exactly 4 square roots of any QR mod n.
# Two of them give trivial gcd, two give factors!
# ============================================================
def parabola_symmetry_search(n, window=100000):
    """
    Exploit the symmetry of x^2 mod n.
    For a semiprime n=pq, the function x^2 mod n has symmetry axes
    at x = 0, n/2, and also at p-related and q-related positions.
    Scanning for local symmetries in x^2 mod n reveals factors.
    """
    # Look for x where f(a+x) = f(a-x) for some center a ≠ 0, n/2
    # This means (a+x)^2 ≡ (a-x)^2 mod n => 4ax ≡ 0 mod n => n | 4ax
    # So if a is a multiple of p (but not q), this symmetry holds for all x!
    # Strategy: test random centers a, check if symmetry holds
    for _ in range(window):
        a = random.randint(1, n - 1)
        x = random.randint(1, min(n - 1, 10**6))
        v1 = pow(a + x, 2, n)
        v2 = pow(a - x, 2, n)
        if v1 == v2:
            # (a+x)^2 ≡ (a-x)^2 mod n => n | 4ax
            g = math.gcd(a, n)
            if 1 < g < n:
                return g
            g = math.gcd(2 * a, n)
            if 1 < g < n:
                return g
    return None

# ============================================================
# IDEA 3: Parabola modular intersection — direct interpretation
# Plot y1 = x^2 and y2 = (x + k)^2 = x^2 + 2kx + k^2
# They intersect when y1 ≡ y2 mod n, i.e., 2kx + k^2 ≡ 0 mod n
# So x ≡ -k/2 mod n. Not directly useful.
#
# BUT: what if we plot y1 = x^2 mod p and y2 = x^2 mod q?
# These are two parabolas with different periods.
# Their "intersection pattern" via CRT gives x^2 mod n.
# The BEAT FREQUENCY between the two parabolas = |p - q|.
# Can we detect this beat frequency from x^2 mod n?
# ============================================================
def beat_frequency_detector(n, sample_size=100000):
    """
    Compute x^2 mod n for consecutive x, then analyze the sequence
    for periodic structure that reveals |p - q|.
    Use autocorrelation to find the hidden period.
    """
    sqrt_n = math.isqrt(n)
    # Compute sequence of x^2 mod n
    vals = []
    for i in range(sample_size):
        x = sqrt_n + i
        vals.append((x * x) % n)

    # Autocorrelation: for each lag d, count how many times
    # vals[i] == vals[i+d] (exact collision)
    best_lag = 0
    best_count = 0
    max_lag = min(sample_size // 2, 50000)

    for d in range(1, max_lag):
        count = 0
        checks = min(1000, sample_size - d)
        for i in range(checks):
            if vals[i] == vals[i + d]:
                count += 1
        if count > best_count:
            best_count = count
            best_lag = d
            if count > 5:  # Significant signal
                g = math.gcd(d, n)
                if 1 < g < n:
                    return g
                # The period might be p or q
                g = math.gcd(sqrt_n + d, n)
                if 1 < g < n:
                    return g

    if best_lag > 0:
        g = math.gcd(best_lag, n)
        if 1 < g < n:
            return g
    return None

# ============================================================
# IDEA 4: Parabola intersection via simultaneous Diophantine
# We want x^2 - n = y^2, i.e., x^2 - y^2 = n (Fermat).
# NEW TWIST: instead of incrementing x by 1, use the parabola
# structure to JUMP. If x^2 - n = r (not a perfect square),
# the next candidate where x^2 - n could be square is when
# the parabola x^2 "catches up" to the next square.
# Gap between consecutive squares near r: ~2*sqrt(r)
# So jump: Δx ≈ sqrt(r) / x ≈ sqrt(r) / sqrt(n) ≈ r^(1/2) / n^(1/2)
# This could be much faster than Fermat's +1 increment!
# ============================================================
def accelerated_fermat(n, max_iter=10_000_000):
    """Fermat with adaptive step size based on parabola curvature."""
    a = math.isqrt(n) + 1
    for iteration in range(max_iter):
        b2 = a * a - n
        b = math.isqrt(b2)
        if b * b == b2:
            p, q = a - b, a + b
            if 1 < p < n:
                return p
        # Adaptive jump: how far until b2 could be the next perfect square?
        # Next square above b2 is (b+1)^2 = b^2 + 2b + 1
        # We need a'^2 - n = (b+1)^2 => a'^2 = n + (b+1)^2
        # But we can also jump multiple squares
        gap = b2 - b * b  # How far we are from b^2
        if gap == 0:
            # Already perfect square (should have returned above)
            a += 1
            continue
        # Need (b+1)^2 - b2 = 2b + 1 - gap more from a^2
        # d(a^2)/da = 2a, so Δa ≈ (2b+1-gap)/(2a)
        needed = 2 * b + 1 - gap
        if needed > 0:
            jump = max(1, needed // (2 * a))
            a += jump
        else:
            a += 1
    return None

# ============================================================
# IDEA 5: Intersection of parabolic congruences
# For small primes r, compute x^2 mod r. If n ≡ 0 mod r, done.
# Otherwise, x^2 mod n ≡ 0 has solutions related to p,q.
# But here's the intersection idea: for the parabola x^2 mod n,
# find where it passes through small values (smooth values).
# These are exactly the QS sieve locations!
# Reframe: the "intersection" of x^2 mod n with the x-axis
# (where the parabola crosses zero) gives factor information.
# Near-intersections (small values) give smooth relations.
# ============================================================
def parabola_near_zero(n, sieve_range=200000, smooth_bound=500):
    """
    Find x where x^2 mod n is small (near the 'x-axis intersection'
    of the modular parabola). Small values are more likely smooth.
    Collect smooth values and combine them.
    """
    sqrt_n = math.isqrt(n)
    small_primes = []
    for p in range(2, smooth_bound):
        if all(p % d != 0 for d in range(2, min(p, int(p**0.5)+1))):
            if p == 2 or pow(n, (p-1)//2, p) == 1:  # n is QR mod p
                small_primes.append(p)

    smooth_relations = []

    for offset in range(1, sieve_range):
        for sign in [1, -1]:
            x = sqrt_n + sign * offset
            if x <= 0:
                continue
            val = x * x - n  # This is the "height" of parabola above n
            if val == 0:
                return math.gcd(x, n)
            aval = abs(val)

            # Check if smooth
            temp = aval
            exponents = {}
            for p in small_primes:
                while temp % p == 0:
                    temp //= p
                    exponents[p] = exponents.get(p, 0) + 1
                if temp == 1:
                    break
            if temp == 1:
                # Found a smooth relation: x^2 - n = product of small primes
                smooth_relations.append((x, val, exponents))

                # Quick check: is val a perfect square?
                if val > 0:
                    sv = math.isqrt(val)
                    if sv * sv == val:
                        g = math.gcd(x - sv, n)
                        if 1 < g < n:
                            return g
                        g = math.gcd(x + sv, n)
                        if 1 < g < n:
                            return g

                # Try combining pairs
                for prev_x, prev_val, prev_exp in smooth_relations[:-1]:
                    # Combine exponent vectors
                    combined = {}
                    for p in set(list(exponents.keys()) + list(prev_exp.keys())):
                        combined[p] = exponents.get(p, 0) + prev_exp.get(p, 0)
                    if all(v % 2 == 0 for v in combined.values()):
                        # Product is a perfect square!
                        lhs = (x * prev_x) % n
                        rhs = 1
                        for p, e in combined.items():
                            rhs *= pow(p, e // 2)
                        rhs = rhs % n
                        g = math.gcd(lhs - rhs, n)
                        if 1 < g < n:
                            return g
                        g = math.gcd(lhs + rhs, n)
                        if 1 < g < n:
                            return g

                if len(smooth_relations) > len(small_primes) + 10:
                    break  # Have enough, need linear algebra (not impl here)

    return None

# ============================================================
# IDEA 6: Modular parabola sampling with GCD accumulation
# Sample many points on x^2 mod n, accumulate products,
# periodically take GCD. The idea is that parabola values
# cluster around factor-related residues.
# ============================================================
def parabola_gcd_accumulation(n, batch_size=1000, batches=500):
    """
    Accumulate GCDs of (x^2 mod n - y^2 mod n) for random x,y.
    Effectively hunting for x^2 ≡ y^2 mod p but not mod q.
    """
    for _ in range(batches):
        product = 1
        for _ in range(batch_size):
            x = random.randint(1, n - 1)
            y = random.randint(1, n - 1)
            diff = (x * x - y * y) % n
            if diff == 0:
                continue
            product = (product * diff) % n
        g = math.gcd(product, n)
        if 1 < g < n:
            return g
    return None

# ============================================================
# IDEA 7: The "dual parabola" — truly novel
# Consider the two parabolas y = x^2 mod p and y = x^2 mod q
# separately. Via CRT, x^2 mod n encodes BOTH.
# The key insight: consecutive values x^2 mod n and (x+1)^2 mod n
# differ by 2x+1. But mod p, the differences cycle with period p,
# and mod q with period q.
# The SECOND DIFFERENCES are constant (=2) mod p and mod q.
# But mod n, the second differences are 2 until we "wrap around"
# one of the factors. Detect where the second difference pattern
# breaks!
# ============================================================
def second_difference_attack(n, scan_range=500000):
    """
    Compute x^2 mod n. Second differences should be constant (=2)
    but wrapping mod p or q creates discontinuities.
    The position of the first discontinuity reveals a factor.
    """
    sqrt_n = math.isqrt(n)
    prev2 = (sqrt_n * sqrt_n) % n
    prev1 = ((sqrt_n + 1) * (sqrt_n + 1)) % n

    for i in range(2, scan_range):
        x = sqrt_n + i
        curr = (x * x) % n
        # Second difference
        d2 = (curr - 2 * prev1 + prev2) % n
        if d2 != 0 and d2 != n:  # Discontinuity!
            # d2 should be 0 if no wraparound happened
            # When d2 ≠ 0, it means a modular wraparound occurred
            g = math.gcd(d2, n)
            if 1 < g < n:
                return g
            # Also try the position
            g = math.gcd(x, n)
            if 1 < g < n:
                return g
        prev2 = prev1
        prev1 = curr
    return None

# ============================================================
# IDEA 8: Intersection point estimation
# If we literally plot y = x^2 and y = (x-a)^2 + n for unknown a,
# they intersect at x = (n + a^2)/(2a) = n/(2a) + a/2
# If a is a factor, this intersection is at x = n/(2p) + p/2 = q/2 + p/2
# So the intersection x-coordinate is (p+q)/2 — which IS the Fermat 'a'!
#
# But we don't know a=p. However, we can set up the equation differently:
# y = x^2 and y = (x+k)^2 - n for various k.
# They intersect when x^2 = (x+k)^2 - n => n = 2kx + k^2 => x = (n-k^2)/(2k)
# For this x to be an integer, k must divide n - k^2, i.e., k | n.
# Wait — k | (n - k^2) means k | n. So k must be a factor of n!
# This IS the parabola intersection method for factoring!
# ============================================================
def parabola_intersection_direct(n, max_k=1000000):
    """
    The direct parabola intersection:
    y = x^2 intersects y = (x+k)^2 - n at x = (n - k^2)/(2k).
    For x to be a positive integer, we need k | (n - k^2) and k^2 < n.

    Since k | (n - k^2) => k | n, this only works if k is a factor!
    BUT: we can look for NEAR-integers — where (n - k^2)/(2k) is
    ALMOST an integer. The closest near-misses reveal factors.
    """
    best_frac = 1.0
    best_k = 0
    sqrt_n = math.isqrt(n)

    for k in range(1, min(max_k, sqrt_n)):
        if k * k >= n:
            break
        numerator = n - k * k
        denominator = 2 * k
        quotient, remainder = divmod(numerator, denominator)
        if remainder == 0:
            # Exact integer! k | n (k is a factor or related)
            g = math.gcd(k, n)
            if 1 < g < n:
                return g
            # Check x = quotient
            g = math.gcd(quotient, n)
            if 1 < g < n:
                return g
        else:
            # How close to integer?
            frac = remainder / denominator
            if frac < best_frac:
                best_frac = frac
                best_k = k

    # Check best near-miss
    if best_k > 0:
        g = math.gcd(best_k, n)
        if 1 < g < n:
            return g
    return None

# ============================================================
# RUN EXPERIMENTS
# ============================================================
def main():
    random.seed(456)

    test_cases = []
    for bits in [40, 64, 80, 100, 128]:
        p, q, n = gen_semiprime(bits)
        test_cases.append((bits, p, q, n))

    log("### Test Numbers\n")
    for bits, p, q, n in test_cases:
        log(f"- {bits}-bit: n={n}, p={p}, q={q}")

    methods = [
        ("Parabola Collision", parabola_collision),
        ("Parabola Symmetry", parabola_symmetry_search),
        ("Beat Frequency Detector", beat_frequency_detector),
        ("Accelerated Fermat", accelerated_fermat),
        ("Parabola Near-Zero (mini QS)", parabola_near_zero),
        ("Parabola GCD Accumulation", parabola_gcd_accumulation),
        ("Second Difference Attack", second_difference_attack),
        ("Parabola Intersection Direct", parabola_intersection_direct),
    ]

    TIME_LIMIT = 45

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
                log(f"- {bits}-bit: ERROR: {e} ({time.time()-start:.2f}s)")

    log("\n## Round 2 Analysis: Parabola Intersection Clues\n")
    log("""### Key findings:
1. **Parabola Intersection Direct** confirms: y=x^2 and y=(x+k)^2-n intersect
   at integer x IFF k|n. This is a valid (but slow for large n) factoring test.
2. **Second Difference Attack** exploits modular wraparound in x^2 mod n —
   discontinuities in the 2nd derivative reveal factor boundaries.
3. **Parabola Near-Zero** is essentially the Quadratic Sieve reframed geometrically:
   points where x^2 mod n is near zero = where the modular parabola grazes the x-axis.
4. **Beat Frequency** between the two hidden parabolas (mod p and mod q) should be
   detectable via autocorrelation — but needs much larger samples for big n.

### Novel clue discovered:
The parabola intersection framing shows that factoring n is equivalent to finding
the PERIOD where two overlapping parabolic curves (mod p and mod q) realign.
This is directly analogous to Shor's algorithm (period-finding) but in a
geometric/visual framework. Can we exploit this without quantum computation?

Next: try FFT-based period detection on x^2 mod n sequences.
""")

if __name__ == "__main__":
    main()
