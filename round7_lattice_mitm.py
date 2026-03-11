#!/usr/bin/env python3
"""
Round 7: Lattice MITM + Residue Number System (RNS) Factoring

Two novel approaches to integer factorization:

Approach A: Lattice-based Meet-in-the-Middle
  Split each factor into low (mod 2^k) and high (// 2^k) parts with k = L/3.
  Bottom-up Hensel lifting gives ~2^(L/3) candidate (x_low, y_low) pairs.
  Top-down MSB estimation constrains x_high. The valid factorization corresponds
  to a short vector in a 2D lattice. We use exhaustive matching with hash joins
  to find it.

Approach B: Residue Number System (RNS) Factoring
  Represent factorization in multiple coprime moduli simultaneously.
  For small primes r1..rM, compute n mod ri, then enumerate x mod ri for each
  ri independently. CRT combines partial solutions. Cost is O(sum of ri) instead
  of exponential in bit length --- avoids carry entanglement entirely.

Uses only standard Python. Tests on semiprimes from 40 to 160 bits.
"""

import math
import random
import time
import itertools

LOG_FILE = "factoring_log.md"


def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg)


# ============================================================
# Utility functions
# ============================================================
def is_prime_miller_rabin(n, k=20):
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(k):
        a = random.randrange(2, n - 1) if n > 4 else 2
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
    if n <= 2:
        return 2
    if n % 2 == 0:
        n += 1
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


def isqrt(n):
    if n < 0:
        raise ValueError("Square root of negative number")
    if n == 0:
        return 0
    x = 1 << ((n.bit_length() + 1) // 2)
    while True:
        y = (x + n // x) // 2
        if y >= x:
            return x
        x = y


def small_primes_up_to(limit):
    """Sieve of Eratosthenes."""
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False
    return [i for i in range(2, limit + 1) if sieve[i]]


# ============================================================
# APPROACH A: Lattice-based Meet-in-the-Middle
# ============================================================
def lattice_mitm_factor(n, time_limit=60.0):
    """
    Lattice-based Meet-in-the-Middle factoring.

    1. Bottom-up: Hensel lift to get all (x_low, y_low) pairs mod 2^k
       where x_low * y_low ≡ n mod 2^k, with k ≈ L/3.
    2. Top-down: For each x_low, estimate x_high ≈ n / (y * 2^k).
       Since y ≈ n/x, and x = x_high * 2^k + x_low, we get
       x_high ≈ sqrt(n) / 2^k for balanced factors.
    3. Hash-join: Build a dictionary keyed by a "signature" derived from
       the top-down estimate. Match bottom-up candidates against it.

    The lattice interpretation: The point (x_low, x_high) must satisfy
    x_low + x_high * 2^k = x where x | n. This is a lattice point
    that is "short" relative to the lattice defined by the modular
    constraints.
    """
    L = n.bit_length()
    sqrt_n = isqrt(n)
    start_time = time.time()

    # Try multiple k values centered around L/3
    for k_offset in range(0, L // 3 + 1):
        for sign in [0, 1, -1]:
            k = max(4, L // 3 + sign * k_offset)
            if k < 4 or k >= L - 2:
                continue
            if time.time() - start_time > time_limit:
                return None

            result = _lattice_mitm_with_k(n, L, k, sqrt_n, start_time, time_limit)
            if result is not None:
                return result

    return None


def _hensel_lift(n, k, start_time, time_limit, max_states=500000):
    """
    Hensel lift to collect all valid (x_low, y_low) pairs mod 2^k
    such that x_low * y_low ≡ n mod 2^k, both odd, x_low <= y_low.

    Returns list of (x_low, y_low) pairs, or None on timeout/overflow.
    """
    # Start: x ≡ 1 mod 2 (odd)
    states = {1}

    for level in range(1, k):
        if time.time() - start_time > time_limit:
            return None

        mod_curr = 1 << level
        mod_next = 1 << (level + 1)
        n_mod = n % mod_next

        next_states = set()
        for x_low in states:
            for bit in [0, 1]:
                x_new = x_low + bit * mod_curr
                try:
                    x_inv = pow(x_new, -1, mod_next)
                except ValueError:
                    continue
                y_new = (n_mod * x_inv) % mod_next
                if y_new % 2 == 1:
                    # Symmetry: x_low <= y_low
                    if x_new <= y_new:
                        next_states.add(x_new)

        states = next_states
        if len(states) == 0:
            return []
        if len(states) > max_states:
            # Sample to keep manageable
            states = set(random.sample(list(states), max_states))

    # Build (x_low, y_low) pairs
    modulus = 1 << k
    n_mod = n % modulus
    pairs = []
    for x_low in states:
        try:
            x_inv = pow(x_low, -1, modulus)
        except ValueError:
            continue
        y_low = (n_mod * x_inv) % modulus
        if y_low % 2 == 1 and x_low <= y_low:
            pairs.append((x_low, y_low))
    return pairs


def _lattice_mitm_with_k(n, L, k, sqrt_n, start_time, time_limit):
    """
    Run lattice MITM with a specific k value.

    For each (x_low, y_low) pair from Hensel lifting:
      - x = x_high * 2^k + x_low, y = y_high * 2^k + y_low
      - x * y = n
      - From the algebraic relation:
        x_high * y_low + y_high * x_low + carry = (n >> k) - x_high * y_high * 2^k
      - For balanced factors, x ≈ sqrt(n), so x_high ≈ sqrt(n) / 2^k.
      - Given x_low, we can solve for x_high:
        If x = x_high * M + x_low divides n, then x_high = (x - x_low) / M
        and n / x must be an integer.

    Approach: For each x_low from Hensel, scan plausible x_high values.
    The key optimization: use the algebraic relation to solve for x_high
    in O(1) per x_low.

    x * y = n, x = a*M + r, y = b*M + s, r*s ≡ n mod M
    a*s + b*r + (r*s - n%M)/M = n >> k - a*b*M
    Given r and s = n*r^{-1} mod M:
      For each a: b = (n>>k - (r*s)>>k - a*s) / (r + a*M)
    """
    M = 1 << k
    n_low = n % M
    H = n >> k  # high part of n

    x_min = max(3, isqrt(isqrt(n)))  # rough lower bound
    x_max = sqrt_n

    a_min = max(0, x_min >> k)
    a_max = x_max >> k

    # Phase 1: Bottom-up Hensel
    pairs = _hensel_lift(n, k, start_time, time_limit)
    if pairs is None or len(pairs) == 0:
        return None

    # Phase 2: For each (x_low, y_low), solve algebraically for x_high
    for x_low, y_low in pairs:
        if time.time() - start_time > time_limit:
            return None

        Q = (x_low * y_low) >> k  # carry from low-order product

        # For each a (x_high), compute b (y_high):
        # a * y_low + b * x_low + a * b * M = H - Q
        # b * (x_low + a * M) = H - Q - a * y_low
        # b = (H - Q - a * y_low) / (x_low + a * M)

        for a in range(a_min, a_max + 1):
            num = H - Q - a * y_low
            den = x_low + a * M

            if den <= 0:
                continue
            if num < 0:
                break  # a too large

            if num % den == 0:
                b = num // den
                if b >= 0:
                    x = a * M + x_low
                    y = b * M + y_low
                    if x > 1 and y > 1 and x * y == n:
                        return min(x, y)

        # Also try with x_low and y_low swapped (since we enforced x_low <= y_low)
        x_low_s, y_low_s = y_low, x_low
        Q_s = (x_low_s * y_low_s) >> k

        for a in range(a_min, a_max + 1):
            num = H - Q_s - a * y_low_s
            den = x_low_s + a * M

            if den <= 0:
                continue
            if num < 0:
                break

            if num % den == 0:
                b = num // den
                if b >= 0:
                    x = a * M + x_low_s
                    y = b * M + y_low_s
                    if x > 1 and y > 1 and x * y == n:
                        return min(x, y)

    return None


# ============================================================
# APPROACH B: Residue Number System (RNS) Factoring
# ============================================================
def rns_factor(n, time_limit=60.0):
    """
    Residue Number System factoring.

    Key idea: Instead of working in binary (base 2) where carries entangle
    bits, represent the factorization modulo small coprime moduli.

    For each small prime r:
      n mod r = (x mod r) * (y mod r) mod r
      Enumerate all x_r in [0, r) such that x_r * y_r ≡ n mod r for some y_r.
      This gives at most r candidate values for (x mod r).

    Then use CRT to combine: if we have x mod r1, x mod r2, ..., x mod rM,
    and the product r1*r2*...*rM > sqrt(n), then x is uniquely determined.

    The cost per modulus is O(r) to enumerate, total O(sum of ri).
    The CRT combination requires trying all combinations of per-modulus
    candidates, which is the product of candidates per modulus.

    For a prime r, n mod r has at most 2 square roots if n is a QR mod r,
    and the factorization x*y ≡ n mod r has r-1 solutions for x (any
    nonzero x works, y = n*x^{-1} mod r). So per prime, there are r-1
    candidates for x mod r --- no pruning!

    HOWEVER: We can add constraints. If we know x < sqrt(n), this doesn't
    help modularly. But if we use MULTIPLE moduli and combine via CRT,
    most combinations will produce x > sqrt(n) and can be discarded.

    Better approach: Use the structure that x*y = n more carefully.
    For each prime r, the solutions for x mod r are {0, 1, 2, ..., r-1}
    minus {0} if gcd(n, r) = 1 (which it is for our semiprimes with large
    factors). So x mod r can be anything in {1, ..., r-1}.

    The RNS approach works better with a DIFFERENT constraint:
    Instead of x*y = n, use x + y = s (unknown sum) and x*y = n.
    Then x and y are roots of t^2 - s*t + n = 0.
    For each prime r: t^2 - s*t + n ≡ 0 mod r.
    The discriminant is s^2 - 4n. For this to have solutions mod r,
    we need s^2 - 4n to be a QR mod r.

    But s is unknown. Instead, enumerate s mod r: for each s_r in [0, r),
    check if s_r^2 - 4n is a QR mod r. About half the s_r values will work.
    This DOES give pruning: ~r/2 candidates per prime.

    With M primes, we get (r/2)^M combinations. We need the CRT product
    to exceed 2*sqrt(n), so product of ri > 2*sqrt(n).
    The number of combinations is prod(ri/2) ≈ prod(ri) / 2^M.
    If we use the first M primes, prod(ri) ≈ e^(rM) by prime number theorem,
    and we need this > 2*sqrt(n) = 2^(L/2+1).

    Refinement: For each prime r, the valid s mod r values are those where
    s^2 ≡ 4n mod r has a solution, i.e., 4n is a QR mod r, which is fixed.
    Actually s^2 - 4n ≡ 0 mod r means s^2 ≡ 4n mod r. So s ≡ ±2*sqrt(n) mod r.
    That's at most 2 values of s mod r per prime!

    This is powerful: with M primes and 2 candidates each, we get 2^M
    combinations. If prod(ri) > 2*sqrt(n), and 2^M is manageable, we win.

    For the first M primes: prod ~ primorial(p_M) ~ e^(p_M).
    Need e^(p_M) > n^(1/2), so p_M > L/2 * ln(2) ≈ 0.35 * L.
    For L = 128, p_M > 45, so about 14 primes (up to 47).
    Combinations: 2^14 = 16384. Very manageable!

    For L = 160, p_M > 56, about 16 primes. 2^16 = 65536. Still fine!
    """
    L = n.bit_length()
    start_time = time.time()

    # Quick check for small factors
    for p in range(2, min(10000, isqrt(n) + 1)):
        if n % p == 0:
            return p

    sqrt_n = isqrt(n)

    # Strategy: find s = x + y where x*y = n.
    # s^2 - 4n = (x-y)^2, so s^2 - 4n must be a perfect square.
    # For each prime r, s^2 ≡ 4n mod r. So s ≡ ±sqrt(4n) mod r.
    # If 4n is not a QR mod r, then r | (x - y) ... actually no,
    # it means there's no s mod r, which can't happen since s = x+y exists.
    # 4n mod r is always a QR mod r (since s exists and s^2 ≡ 4n mod r).

    # Collect primes and compute the two candidate s values mod each prime
    primes = small_primes_up_to(300)

    # Filter: skip primes that divide n
    primes = [r for r in primes if n % r != 0]

    # For each prime, find s mod r (at most 2 values)
    residues_per_prime = []  # list of (prime, [s_candidates])
    product = 1

    for r in primes:
        if time.time() - start_time > time_limit:
            return None

        n_mod_r = (4 * n) % r
        # Find square roots of n_mod_r mod r
        roots = []
        for t in range(r):
            if (t * t) % r == n_mod_r:
                roots.append(t)

        if len(roots) == 0:
            # This shouldn't happen if n = x*y with gcd(x*y, r) = 1
            # because s = x+y exists and s^2 ≡ 4n mod r.
            # But if it does, it means r divides one of the factors.
            # Check: gcd(n, r)
            g = math.gcd(n, r)
            if g > 1:
                return g
            # Shouldn't reach here
            continue

        residues_per_prime.append((r, roots))
        product *= r

        # Stop once product > 2*sqrt(n) (with safety margin)
        if product > 4 * sqrt_n:
            break

    if product <= sqrt_n:
        # Not enough primes to uniquely determine s
        # Fall back: extend with more primes or give up
        pass

    # Now combine via CRT: enumerate all combinations of residues
    # Each prime contributes at most 2 candidates, so total is 2^M
    M = len(residues_per_prime)
    total_combos = 1
    for _, roots in residues_per_prime:
        total_combos *= len(roots)

    if total_combos > 10_000_000:
        # Too many combinations, trim
        # Keep only primes with exactly 2 roots (most pruning)
        residues_per_prime_filtered = [(r, roots) for r, roots in residues_per_prime if len(roots) <= 2]
        # Recompute product
        product = 1
        for r, _ in residues_per_prime_filtered:
            product *= r
        residues_per_prime = residues_per_prime_filtered
        M = len(residues_per_prime)
        total_combos = 1
        for _, roots in residues_per_prime:
            total_combos *= len(roots)

    if total_combos > 10_000_000:
        return None

    # CRT combination
    # For efficiency, use incremental CRT
    moduli = [r for r, _ in residues_per_prime]
    candidates_list = [roots for _, roots in residues_per_prime]

    result = _crt_enumerate(n, sqrt_n, moduli, candidates_list, start_time, time_limit)
    return result


def _crt_combine(r1, m1, r2, m2):
    """
    Combine two CRT constraints: x ≡ r1 mod m1, x ≡ r2 mod m2.
    Returns (r, m) where x ≡ r mod m, m = lcm(m1, m2).
    Returns None if no solution exists.
    """
    g = math.gcd(m1, m2)
    if (r2 - r1) % g != 0:
        return None
    # Extended Euclidean
    m = m1 * m2 // g
    # x = r1 + m1 * t, need m1*t ≡ (r2 - r1) mod m2
    # t = (r2 - r1) / g * (m1/g)^{-1} mod (m2/g)
    m1g = m1 // g
    m2g = m2 // g
    diff = (r2 - r1) // g
    try:
        inv = pow(m1g, -1, m2g)
    except ValueError:
        return None
    t = (diff * inv) % m2g
    r = (r1 + m1 * t) % m
    return r, m


def _crt_enumerate(n, sqrt_n, moduli, candidates_list, start_time, time_limit):
    """
    Enumerate all CRT combinations incrementally.
    At each step, combine current partial solutions with next prime's candidates.
    Prune: s must satisfy s >= 2*sqrt(n) (since s = x+y >= 2*sqrt(x*y) = 2*sqrt(n))
    and s^2 - 4n must be a perfect square.
    """
    if not moduli:
        return None

    # Start with first prime's candidates
    # partial_solutions: list of (residue, modulus)
    partial = [(r, moduli[0]) for r in candidates_list[0]]

    for i in range(1, len(moduli)):
        if time.time() - start_time > time_limit:
            return None

        m2 = moduli[i]
        cands2 = candidates_list[i]
        new_partial = []

        for r1, m1 in partial:
            for r2 in cands2:
                combined = _crt_combine(r1, m1, r2, m2)
                if combined is not None:
                    new_partial.append(combined)

        partial = new_partial

        if len(partial) == 0:
            return None

        # Prune: check if any partial solution already yields a factor
        # Once modulus > 2*sqrt(n), s is uniquely determined
        current_mod = partial[0][1]
        if current_mod > 4 * sqrt_n:
            # s is determined; check each
            for s_val, mod_val in partial:
                if time.time() - start_time > time_limit:
                    return None
                # s = x + y, and s^2 - 4n = (x - y)^2
                # Try s_val and s_val + k*mod_val for small k
                for k_mult in range(0, max(1, (4 * sqrt_n) // mod_val + 2)):
                    s = s_val + k_mult * mod_val
                    if s < 2:
                        continue
                    disc = s * s - 4 * n
                    if disc < 0:
                        continue
                    sq = isqrt(disc)
                    if sq * sq == disc:
                        # x = (s + sq) / 2, y = (s - sq) / 2
                        if (s + sq) % 2 == 0:
                            x = (s + sq) // 2
                            y = (s - sq) // 2
                            if x > 1 and y > 1 and x * y == n:
                                return min(x, y)

            # If no solution found yet, the modulus might not be large enough
            # or we missed the right s range. Continue adding primes.

    # Final check: enumerate remaining candidates
    for s_val, mod_val in partial:
        if time.time() - start_time > time_limit:
            return None
        # s = x + y >= 2*sqrt(n), s is odd iff x+y is odd (one even one odd)
        # For our odd semiprimes, both factors are odd, so s is even.
        # Adjust s_val to be even
        s_start = s_val
        # s must be >= ceil(2*sqrt(n))
        min_s = 2 * isqrt(n)
        if min_s * min_s < 4 * n:
            min_s += 1
        # Find smallest s >= min_s with s ≡ s_val mod mod_val
        if s_start < min_s:
            diff = min_s - s_start
            steps = (diff + mod_val - 1) // mod_val
            s_start = s_val + steps * mod_val

        # s <= x_max + n/x_min. For x_min ~ n^(1/4), s <= n^(3/4) + n^(1/4)
        max_s = sqrt_n + n // max(2, isqrt(isqrt(n)))
        count = 0
        s = s_start
        while s <= max_s and count < 5_000_000:
            if time.time() - start_time > time_limit:
                return None
            disc = s * s - 4 * n
            if disc >= 0:
                sq = isqrt(disc)
                if sq * sq == disc:
                    if (s + sq) % 2 == 0:
                        x = (s + sq) // 2
                        y = (s - sq) // 2
                        if x > 1 and y > 1 and x * y == n:
                            return min(x, y)
            s += mod_val
            count += 1

    return None


# ============================================================
# Enhanced RNS: Use x mod r directly instead of s = x+y
# ============================================================
def rns_direct_factor(n, time_limit=60.0):
    """
    Direct RNS approach: for each small prime r, enumerate all possible
    x mod r values (where x*y ≡ n mod r). Then use CRT to reconstruct x.

    For prime r not dividing n: x can be any nonzero value mod r (since
    y = n*x^{-1} mod r is determined). That's r-1 candidates per prime.

    To prune: we also know x <= sqrt(n). After CRT reconstruction with
    modulus M = prod(ri), x mod M is determined. We need x mod M to
    correspond to a value x <= sqrt(n).

    The number of candidates is prod(ri - 1) which is huge.

    BETTER: Use the quadratic structure. x*y = n means x and y are roots of
    t^2 - (x+y)*t + n = 0 mod r. The sum x+y mod r is unknown, but
    the PRODUCT x*y mod r = n mod r is known.

    For factoring, the key insight is: we don't need to enumerate x mod r
    for ALL r. We only need primes where the number of candidates is SMALL.

    Special primes: r where n mod r = 0 means r | n, instant factor.
    Primes where n is a perfect square mod r: then x ≡ y mod r is possible
    (when x = y mod r), which means x ≡ ±sqrt(n) mod r. That's 2 candidates!

    But x ≠ y in general (unless p = q, but we ensure p ≠ q).
    Still, if n IS a QR mod r, it has 2 square roots ±a. Then x ≡ a or -a
    doesn't mean x ≡ a mod r; it means if x ≡ a then y ≡ a too, which
    requires x ≡ y mod r. This is true only if r | (x - y).

    Actually, we can use a different approach entirely:
    For each prime r, compute all DIVISORS of n mod r in Z/rZ.
    n mod r can be written as a product in r-1 ways (since any nonzero x
    works with y = n/x mod r). No pruning from multiplicative structure alone.

    The REAL RNS insight: use SMOOTH parts of factors.
    If p-1 or q-1 has a smooth factor, Pollard p-1 works.
    RNS analog: check if x ≡ 1 mod r for many small r (Pollard p-1 style).

    Let me implement a cleaner version that uses the sum-of-factors approach
    (Approach B from the problem statement) but with aggressive pruning.
    """
    L = n.bit_length()
    start_time = time.time()
    sqrt_n = isqrt(n)

    # Quick trial division
    for p in range(2, min(10000, sqrt_n + 1)):
        if n % p == 0:
            return p

    # Phase 1: For each small prime r, compute candidates for s = x + y mod r.
    # s^2 ≡ 4n mod r, so s ≡ ±2*sqrt(n mod r) mod r.
    # This gives exactly 0 or 2 candidates per prime (0 if 4n is not QR mod r,
    # but since s exists, 4n IS a QR mod r for all r not dividing n).

    primes = small_primes_up_to(500)
    primes = [r for r in primes if n % r != 0]

    prime_residues = []  # (prime, [candidates for s mod prime])
    product = 1
    target = 4 * sqrt_n  # We want product of primes > this

    for r in primes:
        if time.time() - start_time > time_limit:
            return None

        four_n_mod_r = (4 * n) % r
        # Find square roots of four_n_mod_r mod r
        roots = []
        # For small r, just brute force
        for t in range(r):
            if (t * t) % r == four_n_mod_r:
                roots.append(t)

        if len(roots) == 0:
            # r divides discriminant; skip or special handling
            continue

        if len(roots) > 2:
            # For prime r, there are at most 2 square roots
            # This shouldn't happen for prime r
            continue

        prime_residues.append((r, roots))
        product *= r

        if product > target:
            break

    if product <= sqrt_n:
        # Not enough coverage, can't uniquely determine s
        # Still try what we have
        pass

    M = len(prime_residues)

    # Phase 2: Incremental CRT enumeration with pruning
    # Each prime gives 2 candidates. Total: 2^M combinations.
    # Use incremental merging to keep the working set small.

    # Additional pruning: s = x + y is even (both factors odd for odd n)
    # and s >= 2*sqrt(n)

    moduli = [r for r, _ in prime_residues]
    cands = [roots for _, roots in prime_residues]

    # Incremental CRT
    partial = [(r % moduli[0], moduli[0]) for r in cands[0]] if M > 0 else []

    for i in range(1, M):
        if time.time() - start_time > time_limit:
            return None

        m2 = moduli[i]
        c2 = cands[i]
        new_partial = []

        for r1, m1 in partial:
            for r2 in c2:
                combined = _crt_combine(r1, m1, r2, m2)
                if combined is not None:
                    new_partial.append(combined)

        partial = new_partial
        if not partial:
            return None

        # Size check: warn if growing too large
        if len(partial) > 1_000_000:
            break

    # Phase 3: Check each CRT candidate
    for s_val, mod_val in partial:
        if time.time() - start_time > time_limit:
            return None

        # s must be even for odd semiprime (both factors odd)
        # Adjust: find s ≡ s_val mod mod_val that is even
        if mod_val % 2 == 0:
            # mod_val is even, s_val parity is fixed
            if s_val % 2 != 0:
                continue  # can't make it even
        else:
            # mod_val is odd; we can pick the even representative
            if s_val % 2 != 0:
                s_val += mod_val  # now even if mod_val is odd
                # actually s_val + mod_val changes parity since mod_val is odd

        # Find smallest s >= 2*sqrt(n)
        min_s = 2 * isqrt(n)
        if min_s * min_s < 4 * n:
            min_s += 1

        if s_val < min_s:
            if mod_val > 0:
                diff = min_s - s_val
                steps = (diff + mod_val - 1) // mod_val
                s_val = s_val + steps * mod_val
            else:
                continue

        # Ensure s is even
        if s_val % 2 != 0:
            s_val += mod_val
        if s_val % 2 != 0:
            # mod_val is also even; skip this candidate
            # Actually try both parities
            pass

        # Upper bound on s: roughly sqrt(n) + n/2 but practically ~2*sqrt(n) for balanced
        max_s = sqrt_n + n // max(3, isqrt(isqrt(n)))

        s = s_val
        count = 0
        while s <= max_s and count < 2_000_000:
            if time.time() - start_time > time_limit:
                return None
            disc = s * s - 4 * n
            if disc >= 0:
                sq = isqrt(disc)
                if sq * sq == disc:
                    if (s + sq) % 2 == 0:
                        x = (s + sq) // 2
                        y = (s - sq) // 2
                        if x > 1 and y > 1 and x * y == n:
                            return min(x, y)
            s += mod_val
            count += 1

    return None


# ============================================================
# Pollard Rho (baseline comparison)
# ============================================================
def pollard_rho_brent(n, time_limit=60.0):
    """Brent's improvement of Pollard's rho."""
    if n % 2 == 0:
        return 2
    if n == 1:
        return None
    start_time = time.time()
    for c in range(1, 200):
        if time.time() - start_time > time_limit:
            return None
        x = random.randint(2, n - 1)
        y = x
        d = 1
        q = 1
        r = 1
        while d == 1:
            if time.time() - start_time > time_limit:
                return None
            ys = y
            for _ in range(r):
                y = (y * y + c) % n
            k = 0
            while k < r and d == 1:
                qs = y
                batch = min(128, r - k)
                for _ in range(batch):
                    y = (y * y + c) % n
                    q = q * abs(x - y) % n
                d = math.gcd(q, n)
                k += batch
            r *= 2
            if d == 1:
                x = y
            elif d == n:
                # Backtrack
                d = 1
                y = qs
                while d == 1:
                    y = (y * y + c) % n
                    d = math.gcd(abs(x - y), n)
                if d == n:
                    break
        if 1 < d < n:
            return d
    return None


# ============================================================
# Combined: try all methods with time budgets
# ============================================================
def combined_factor(n, time_limit=60.0):
    """Try all methods in order of expected speed."""
    start = time.time()
    remaining = lambda: max(0.1, time_limit - (time.time() - start))

    # Quick trial division
    for p in range(2, min(100000, isqrt(n) + 1)):
        if n % p == 0:
            return p, "trial"

    # RNS (sum-of-factors approach)
    r = rns_factor(n, remaining() * 0.3)
    if r:
        return r, "rns"

    # Lattice MITM
    r = lattice_mitm_factor(n, remaining() * 0.4)
    if r:
        return r, "lattice_mitm"

    # Pollard rho as fallback
    r = pollard_rho_brent(n, remaining())
    if r:
        return r, "pollard_rho"

    return None, "none"


# ============================================================
# Main experiment runner
# ============================================================
def main():
    random.seed(2025)

    # Generate test semiprimes from 40 to 160 bits
    test_bits = [40, 50, 60, 64, 72, 80, 96, 100, 112, 128, 140, 150, 160]
    test_cases = []
    for bits in test_bits:
        p, q, n = gen_semiprime(bits)
        actual_bits = n.bit_length()
        test_cases.append((bits, actual_bits, p, q, n))

    TIME_LIMIT = 120  # per method per number

    log("\n\n---\n")
    log("## Round 7: Lattice MITM + RNS Factoring\n")
    log(f"Date: 2026-03-10 | Seed: 2025\n")

    log("### Concept\n")
    log("**Approach A (Lattice MITM):** Split factors into low/high parts at k=L/3 bits.")
    log("Hensel lifting gives candidate (x_low, y_low) pairs mod 2^k. For each,")
    log("solve algebraically for x_high: b = (H - Q - a*y_low) / (x_low + a*M).")
    log("This avoids brute-force search of x_high values.\n")
    log("**Approach B (RNS Factoring):** Represent s = x+y modulo small primes.")
    log("For each prime r, s^2 ≡ 4n mod r gives exactly 2 candidates for s mod r.")
    log("CRT combines these into O(2^M) candidates total. Check each via")
    log("discriminant test: s^2 - 4n must be a perfect square.\n")

    log("### Test Numbers\n")
    log("| Bits (target) | Bits (actual) | n | p | q |")
    log("|---|---|---|---|---|")
    for bits, actual_bits, p, q, n in test_cases:
        log(f"| {bits} | {actual_bits} | {n} | {p} | {q} |")

    # ---- Approach A: Lattice MITM ----
    log("\n### Approach A: Lattice-based Meet-in-the-Middle\n")
    lattice_results = []
    for bits, actual_bits, p, q, n in test_cases:
        start = time.time()
        try:
            result = lattice_mitm_factor(n, TIME_LIMIT)
            elapsed = time.time() - start
            if result and n % result == 0 and 1 < result < n:
                other = n // result
                status = f"- {bits}-bit ({actual_bits}): **SUCCESS** {elapsed:.4f}s -> {min(result, other)}"
                status += f"\n  verified: {n} = {min(result, other)} x {max(result, other)}"
                lattice_results.append(('success', elapsed, bits))
            elif elapsed >= TIME_LIMIT:
                status = f"- {bits}-bit ({actual_bits}): **TIMEOUT** ({elapsed:.1f}s)"
                lattice_results.append(('timeout', elapsed, bits))
            else:
                status = f"- {bits}-bit ({actual_bits}): FAILED ({elapsed:.2f}s)"
                lattice_results.append(('fail', elapsed, bits))
        except Exception as e:
            elapsed = time.time() - start
            status = f"- {bits}-bit ({actual_bits}): ERROR: {type(e).__name__}: {e} ({elapsed:.2f}s)"
            lattice_results.append(('error', elapsed, bits))
        log(status)

    # ---- Approach B: RNS Factoring ----
    log("\n### Approach B: RNS (Residue Number System) Factoring\n")
    rns_results = []
    for bits, actual_bits, p, q, n in test_cases:
        start = time.time()
        try:
            result = rns_factor(n, TIME_LIMIT)
            elapsed = time.time() - start
            if result and n % result == 0 and 1 < result < n:
                other = n // result
                status = f"- {bits}-bit ({actual_bits}): **SUCCESS** {elapsed:.4f}s -> {min(result, other)}"
                status += f"\n  verified: {n} = {min(result, other)} x {max(result, other)}"
                rns_results.append(('success', elapsed, bits))
            elif elapsed >= TIME_LIMIT:
                status = f"- {bits}-bit ({actual_bits}): **TIMEOUT** ({elapsed:.1f}s)"
                rns_results.append(('timeout', elapsed, bits))
            else:
                status = f"- {bits}-bit ({actual_bits}): FAILED ({elapsed:.2f}s)"
                rns_results.append(('fail', elapsed, bits))
        except Exception as e:
            elapsed = time.time() - start
            status = f"- {bits}-bit ({actual_bits}): ERROR: {type(e).__name__}: {e} ({elapsed:.2f}s)"
            rns_results.append(('error', elapsed, bits))
        log(status)

    # ---- RNS Direct (alternative) ----
    log("\n### Approach B2: RNS Direct (alternative enumeration)\n")
    rns2_results = []
    for bits, actual_bits, p, q, n in test_cases:
        start = time.time()
        try:
            result = rns_direct_factor(n, TIME_LIMIT)
            elapsed = time.time() - start
            if result and n % result == 0 and 1 < result < n:
                other = n // result
                status = f"- {bits}-bit ({actual_bits}): **SUCCESS** {elapsed:.4f}s -> {min(result, other)}"
                status += f"\n  verified: {n} = {min(result, other)} x {max(result, other)}"
                rns2_results.append(('success', elapsed, bits))
            elif elapsed >= TIME_LIMIT:
                status = f"- {bits}-bit ({actual_bits}): **TIMEOUT** ({elapsed:.1f}s)"
                rns2_results.append(('timeout', elapsed, bits))
            else:
                status = f"- {bits}-bit ({actual_bits}): FAILED ({elapsed:.2f}s)"
                rns2_results.append(('fail', elapsed, bits))
        except Exception as e:
            elapsed = time.time() - start
            status = f"- {bits}-bit ({actual_bits}): ERROR: {type(e).__name__}: {e} ({elapsed:.2f}s)"
            rns2_results.append(('error', elapsed, bits))
        log(status)

    # ---- Pollard Rho (baseline) ----
    log("\n### Baseline: Pollard Rho (Brent)\n")
    rho_results = []
    for bits, actual_bits, p, q, n in test_cases:
        start = time.time()
        try:
            result = pollard_rho_brent(n, TIME_LIMIT)
            elapsed = time.time() - start
            if result and n % result == 0 and 1 < result < n:
                other = n // result
                status = f"- {bits}-bit ({actual_bits}): **SUCCESS** {elapsed:.4f}s -> {min(result, other)}"
                status += f"\n  verified: {n} = {min(result, other)} x {max(result, other)}"
                rho_results.append(('success', elapsed, bits))
            elif elapsed >= TIME_LIMIT:
                status = f"- {bits}-bit ({actual_bits}): **TIMEOUT** ({elapsed:.1f}s)"
                rho_results.append(('timeout', elapsed, bits))
            else:
                status = f"- {bits}-bit ({actual_bits}): FAILED ({elapsed:.2f}s)"
                rho_results.append(('fail', elapsed, bits))
        except Exception as e:
            elapsed = time.time() - start
            status = f"- {bits}-bit ({actual_bits}): ERROR: {type(e).__name__}: {e} ({elapsed:.2f}s)"
            rho_results.append(('error', elapsed, bits))
        log(status)

    # ---- Combined approach ----
    log("\n### Combined (all methods with time budget)\n")
    combined_results = []
    for bits, actual_bits, p, q, n in test_cases:
        start = time.time()
        try:
            result, method = combined_factor(n, TIME_LIMIT)
            elapsed = time.time() - start
            if result and n % result == 0 and 1 < result < n:
                other = n // result
                status = f"- {bits}-bit ({actual_bits}): **SUCCESS** {elapsed:.4f}s via {method} -> {min(result, other)}"
                status += f"\n  verified: {n} = {min(result, other)} x {max(result, other)}"
                combined_results.append(('success', elapsed, bits))
            elif elapsed >= TIME_LIMIT:
                status = f"- {bits}-bit ({actual_bits}): **TIMEOUT** ({elapsed:.1f}s)"
                combined_results.append(('timeout', elapsed, bits))
            else:
                status = f"- {bits}-bit ({actual_bits}): FAILED ({elapsed:.2f}s)"
                combined_results.append(('fail', elapsed, bits))
        except Exception as e:
            elapsed = time.time() - start
            status = f"- {bits}-bit ({actual_bits}): ERROR: {type(e).__name__}: {e} ({elapsed:.2f}s)"
            combined_results.append(('error', elapsed, bits))
        log(status)

    # ---- Summary table ----
    log("\n### Results Summary\n")
    all_results = [
        ("Lattice MITM", lattice_results),
        ("RNS (sum s=x+y)", rns_results),
        ("RNS Direct", rns2_results),
        ("Pollard Rho", rho_results),
        ("Combined", combined_results),
    ]

    header = "| Method |"
    sep = "|--------|"
    for bits in test_bits:
        header += f" {bits}b |"
        sep += "------|"
    log(header)
    log(sep)

    for method_name, results in all_results:
        row = f"| {method_name:20s} |"
        for status, elapsed, bits in results:
            if status == 'success':
                row += f" {elapsed:.2f}s |"
            elif status == 'timeout':
                row += " T/O |"
            elif status == 'fail':
                row += " FAIL |"
            else:
                row += " ERR |"
        log(row)

    # ---- Analysis ----
    log("\n### Round 7 Analysis\n")
    log("**Approach A (Lattice MITM):**")
    log("The algebraic solve (given x_low from Hensel, solve for x_high in O(1))")
    log("reduces the inner loop to a single division check per (x_low, a) pair.")
    log("However, the number of Hensel states still grows as ~2^(k/2) at level k,")
    log("and the top-down range a_min..a_max is ~sqrt(n)/2^k. The total work is")
    log("still dominated by the product of these, which is O(sqrt(n)) in the worst case.")
    log("The algebraic formulation avoids the hash-table overhead of a traditional MITM")
    log("but doesn't fundamentally change the complexity.\n")

    log("**Approach B (RNS Factoring):**")
    log("The sum-of-factors representation s = x+y is elegant: for each small prime r,")
    log("s mod r has exactly 2 candidates (square roots of 4n mod r). With M primes,")
    log("this gives 2^M CRT combinations. The primorial grows fast, so M ~ 15-20 primes")
    log("suffice to cover sqrt(n) for 128-160 bit numbers. The 2^M combinations are")
    log("checked via the perfect-square discriminant test s^2 - 4n = d^2.")
    log("Key limitation: for balanced semiprimes, s is very close to 2*sqrt(n), so the")
    log("CRT modulus must be large enough to distinguish s from 2*sqrt(n). The step size")
    log("in the final enumeration (mod_val) determines how many candidates to check.\n")

    log("**Comparison to Pollard Rho:**")
    log("Pollard rho remains the practical winner due to its O(n^(1/4)) expected time")
    log("via the birthday paradox in Z/pZ. The RNS and lattice approaches, while")
    log("theoretically interesting, face the same fundamental barrier: without algebraic")
    log("group structure (as in ECM/rho) or smoothness conditions (as in QS/NFS),")
    log("the search space cannot be pruned below O(sqrt(n)).\n")

    log("**Key insight from RNS approach:**")
    log("The carry-free representation in RNS (each modulus is independent) DOES avoid")
    log("bit entanglement. But the lack of range pruning in modular arithmetic means")
    log("we trade one problem (carry propagation) for another (exponential CRT combinations).")
    log("The 2-candidate-per-prime trick via s = x+y keeps combinations manageable,")
    log("but the final step of searching s values is essentially equivalent to searching")
    log("near 2*sqrt(n), which is what Fermat's method does.\n")


if __name__ == "__main__":
    main()
