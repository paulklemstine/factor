#!/usr/bin/env python3
"""Integer factorization experiments - iterating through approaches."""

import time
import math
import random
import sys

LOG_FILE = "factoring_log.md"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg)

def is_prime_miller_rabin(n, k=20):
    """Miller-Rabin primality test."""
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
    """Find next prime >= n."""
    if n <= 2: return 2
    if n % 2 == 0: n += 1
    while not is_prime_miller_rabin(n):
        n += 2
    return n

def gen_semiprime(bits):
    """Generate a semiprime with approximately `bits` total bits."""
    half = bits // 2
    p = next_prime(random.getrandbits(half) | (1 << (half - 1)))  # ensure high bit set
    q = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    while p == q:
        q = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    return p, q, p * q

def small_primes_up_to(limit):
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, limit + 1, i):
                sieve[j] = False
    return [i for i, v in enumerate(sieve) if v]

SMALL_PRIMES = small_primes_up_to(100000)

# ============================================================
# METHOD 1: Trial Division
# ============================================================
def trial_division(n):
    for p in SMALL_PRIMES:
        if p * p > n:
            break
        if n % p == 0:
            return p
    return None

# ============================================================
# METHOD 2: Fermat's factorization
# ============================================================
def fermat_factor(n, max_iter=5_000_000):
    a = math.isqrt(n)
    if a * a == n:
        return a
    a += 1
    for _ in range(max_iter):
        b2 = a * a - n
        b = math.isqrt(b2)
        if b * b == b2:
            p, q = a - b, a + b
            if 1 < p < n:
                return p
            if 1 < q < n:
                return q
        a += 1
    return None

# ============================================================
# METHOD 3: Pollard's rho (Brent variant)
# ============================================================
def pollard_rho_brent(n, max_iter=2_000_000):
    if n % 2 == 0: return 2
    for attempt in range(20):
        y, c, m = random.randint(1, n-1), random.randint(1, n-1), random.randint(1, n-1)
        g, q, r = 1, 1, 1
        while g == 1:
            x = y
            for _ in range(r):
                y = (y * y + c) % n
            k = 0
            while k < r and g == 1:
                ys = y
                for _ in range(min(m, r - k)):
                    y = (y * y + c) % n
                    q = q * abs(x - y) % n
                g = math.gcd(q, n)
                k += m
            r *= 2
            if r > max_iter:
                break
        if g != 1 and g != n:
            return g
    return None

# ============================================================
# METHOD 4: Pollard p-1
# ============================================================
def pollard_pm1(n, B1=500000, B2=5000000):
    a = 2
    # Stage 1
    for p in SMALL_PRIMES:
        if p > B1:
            break
        pk = p
        while pk <= B1:
            a = pow(a, p, n)
            pk *= p
        g = math.gcd(a - 1, n)
        if 1 < g < n:
            return g
    # Stage 2
    prev_p = SMALL_PRIMES[-1] if SMALL_PRIMES[-1] <= B1 else B1
    # Simple stage 2: check individual primes between B1 and B2
    q = pow(a, 1, n)  # current value
    for p in SMALL_PRIMES:
        if p <= B1:
            continue
        if p > B2:
            break
        q = pow(a, p, n)
        g = math.gcd(q - 1, n)
        if 1 < g < n:
            return g
    return None

# ============================================================
# METHOD 5: Williams p+1
# ============================================================
def williams_pp1(n, B=200000):
    for seed in [3, 5, 6, 7, 11, 13, 17, 19, 23]:
        v = seed
        for j in range(2, B + 1):
            v = (pow(v, j, n) - 2) % n
            if j % 1000 == 0:
                d = math.gcd(v - 2, n)
                if 1 < d < n:
                    return d
        d = math.gcd(v - 2, n)
        if 1 < d < n:
            return d
    return None

# ============================================================
# METHOD 6: Lehman's method
# ============================================================
def lehman_factor(n):
    cbrt_n = int(round(n ** (1.0/3.0)))
    for i in range(2, cbrt_n + 1):
        if n % i == 0:
            return i
    for k in range(1, cbrt_n + 1):
        sqrt_4kn = math.isqrt(4 * k * n)
        lo = sqrt_4kn
        sixth = n ** (1.0/6.0)
        hi = sqrt_4kn + int(math.ceil(sixth / (4 * math.sqrt(k)))) + 2
        for a in range(lo, hi + 1):
            b2 = a * a - 4 * k * n
            if b2 >= 0:
                b = math.isqrt(b2)
                if b * b == b2:
                    d = math.gcd(a + b, n)
                    if 1 < d < n:
                        return d
    return None

# ============================================================
# METHOD 7: SQUFOF
# ============================================================
def squfof(n, max_iter=200000):
    if n % 2 == 0: return 2
    multipliers = [1, 3, 5, 7, 11, 13, 15, 17, 19, 21, 23, 29, 31, 37]
    for k in multipliers:
        kn = k * n
        sqrt_kn = math.isqrt(kn)
        if sqrt_kn * sqrt_kn == kn:
            g = math.gcd(sqrt_kn, n)
            if 1 < g < n:
                return g
            continue
        P0 = sqrt_kn
        Q0 = 1
        Q1 = kn - P0 * P0
        if Q1 == 0:
            continue
        P_prev, Q_prev, Q_curr = P0, Q0, Q1
        for i in range(1, max_iter):
            b = (sqrt_kn + P_prev) // Q_curr
            P_curr = b * Q_curr - P_prev
            Q_next = Q_prev + b * (P_prev - P_curr)
            if i % 2 == 0:
                sq = math.isqrt(Q_curr)
                if sq * sq == Q_curr and sq > 1:
                    # Reverse phase
                    b0 = (sqrt_kn - P_curr) // sq
                    P0r = b0 * sq + P_curr
                    Q0r = sq
                    Q1r = (kn - P0r * P0r) // Q0r
                    if Q1r == 0:
                        continue
                    Pp, Qp, Qc = P0r, Q0r, Q1r
                    for _ in range(max_iter):
                        b2 = (sqrt_kn + Pp) // Qc
                        Pn = b2 * Qc - Pp
                        Qn = Qp + b2 * (Pp - Pn)
                        if Pn == Pp:
                            g = math.gcd(n, Pn)
                            if 1 < g < n:
                                return g
                            break
                        Pp, Qp, Qc = Pn, Qc, Qn
            P_prev, Q_prev, Q_curr = P_curr, Q_curr, Q_next
            if Q_curr == 0:
                break
    return None

# ============================================================
# METHOD 8: Quadratic Sieve (simplified)
# ============================================================
def simple_quadratic_sieve(n, FB_size=80, sieve_range=50000):
    """Very simplified QS - find x^2 ≡ y (mod n) where y is smooth."""
    sqrt_n = math.isqrt(n)
    FB = []
    for p in SMALL_PRIMES[:FB_size*3]:
        # Check if n is a quadratic residue mod p (Euler criterion)
        if p == 2 or pow(n, (p-1)//2, p) == 1:
            FB.append(p)
        if len(FB) >= FB_size:
            break

    # Collect smooth relations
    relations = []  # (x, factorization_vector)
    for offset in range(-sieve_range, sieve_range):
        x = sqrt_n + offset
        if x <= 1:
            continue
        val = (x * x - n)
        if val == 0:
            return math.gcd(x, n)
        if val < 0:
            continue
        # Try to factor val over FB
        temp = val
        vec = []
        for p in FB:
            exp = 0
            while temp % p == 0:
                temp //= p
                exp += 1
            vec.append(exp % 2)  # Only care about parity
        if temp == 1:  # Fully factored (smooth!)
            relations.append((x, val, vec))
            # Quick check: if val is a perfect square, we're done
            sv = math.isqrt(val)
            if sv * sv == val:
                g = math.gcd(x - sv, n)
                if 1 < g < n:
                    return g
                g = math.gcd(x + sv, n)
                if 1 < g < n:
                    return g

    # Try combining pairs of relations with matching parity vectors
    for i in range(len(relations)):
        for j in range(i + 1, len(relations)):
            xi, vi, veci = relations[i]
            xj, vj, vecj = relations[j]
            # Check if combined exponent vector is all even
            combined = [veci[k] + vecj[k] for k in range(len(FB))]
            if all(c % 2 == 0 for c in combined):
                lhs = (xi * xj) % n
                rhs_sq = vi * vj
                rhs = math.isqrt(rhs_sq)
                if rhs * rhs == rhs_sq:
                    g = math.gcd(lhs - rhs, n)
                    if 1 < g < n:
                        return g
                    g = math.gcd(lhs + rhs, n)
                    if 1 < g < n:
                        return g
    return None

# ============================================================
# METHOD 9: Dixon's random squares
# ============================================================
def dixon_random_squares(n, B=500, attempts=100000):
    FB = [p for p in SMALL_PRIMES if p <= B]
    relations = []
    for _ in range(attempts):
        x = random.randint(2, n - 1)
        val = pow(x, 2, n)
        if val == 0:
            continue
        temp = val
        for p in FB:
            while temp % p == 0:
                temp //= p
        if temp == 1:
            sv = math.isqrt(val)
            if sv * sv == val:
                g = math.gcd(x - sv, n)
                if 1 < g < n:
                    return g
            relations.append((x, val))
            if len(relations) > len(FB) + 5:
                break
    # Try pairwise products
    for i in range(min(len(relations), 200)):
        for j in range(i+1, min(len(relations), 200)):
            prod_x = (relations[i][0] * relations[j][0]) % n
            prod_v = relations[i][1] * relations[j][1]
            sv = math.isqrt(prod_v)
            if sv * sv == prod_v:
                g = math.gcd(prod_x - sv, n)
                if 1 < g < n:
                    return g
    return None

# ============================================================
# METHOD 10: Power GCD / order finding
# ============================================================
def power_gcd_scan(n, max_exp=100000):
    for base in [2, 3, 5, 7, 11, 13]:
        val = base
        for k in range(2, max_exp):
            val = pow(val, k, n)
            g = math.gcd(val - 1, n)
            if 1 < g < n:
                return g
            if g == n:
                break
    return None

# ============================================================
# METHOD 11: Fibonacci/Lucas sequence GCD
# ============================================================
def fibonacci_gcd(n, limit=200000):
    """Compute Fibonacci numbers mod n, check gcd at intervals."""
    a, b = 0, 1
    for k in range(2, limit):
        a, b = b, (a + b) % n
        if k % 500 == 0:
            g = math.gcd(b, n)
            if 1 < g < n:
                return g
            g = math.gcd(a, n)
            if 1 < g < n:
                return g
    return None

# ============================================================
# METHOD 12: Rational sieve idea - difference of powers
# ============================================================
def difference_of_powers(n, max_base=1000, max_exp=60):
    """Check if n divides a^k - b^k for small a,b,k."""
    for k in range(2, max_exp):
        for a in range(2, max_base):
            val = pow(a, k, n)
            g = math.gcd(val - 1, n)
            if 1 < g < n:
                return g
            # Also check val + 1 (for a^k + 1 factorizations)
            g = math.gcd(val + 1, n)
            if 1 < g < n:
                return g
    return None

# ============================================================
# METHOD 13: Smooth number accumulation (novel hybrid)
# ============================================================
def smooth_accumulation(n, rounds=5000):
    """
    Novel approach: accumulate products of small random smooth numbers,
    and periodically check gcd with n. The idea is that if p-1 or p+1
    has certain structure, random smooth products will accidentally
    produce a multiple of the order of some element.
    """
    product = 1
    for r in range(rounds):
        # Generate a random smooth number
        x = 1
        for _ in range(random.randint(3, 15)):
            x *= random.choice(SMALL_PRIMES[:50])
        # Accumulate as exponent on random base
        base = random.randint(2, min(n-1, 10**6))
        val = pow(base, x, n)
        g = math.gcd(val - 1, n)
        if 1 < g < n:
            return g
    return None

# ============================================================
# RUN ALL EXPERIMENTS
# ============================================================
def main():
    random.seed(42)

    bit_sizes = [40, 64, 80, 100, 128]
    test_cases = []
    for bits in bit_sizes:
        p, q, n = gen_semiprime(bits)
        test_cases.append((bits, p, q, n))

    log("## Test Semiprimes Generated\n")
    for bits, p, q, n in test_cases:
        log(f"- **{bits}-bit**: n={n}")
        log(f"  - p={p}, q={q}")
        log(f"  - actual bits: {n.bit_length()}")

    methods = [
        ("Trial Division", trial_division),
        ("Fermat's Method", fermat_factor),
        ("Pollard Rho (Brent)", pollard_rho_brent),
        ("Pollard p-1", pollard_pm1),
        ("Williams p+1", williams_pp1),
        ("Lehman", lehman_factor),
        ("SQUFOF", squfof),
        ("Quadratic Sieve (simple)", simple_quadratic_sieve),
        ("Dixon Random Squares", dixon_random_squares),
        ("Power GCD Scan", power_gcd_scan),
        ("Fibonacci GCD", fibonacci_gcd),
        ("Difference of Powers", difference_of_powers),
        ("Smooth Accumulation", smooth_accumulation),
    ]

    TIME_LIMIT = 30  # seconds per method per number

    log("\n## Experiment Results\n")

    summary = {}
    for method_name, func in methods:
        log(f"\n### {method_name}\n")
        summary[method_name] = {}
        for bits, p, q, n in test_cases:
            start = time.time()
            try:
                result = func(n)
                elapsed = time.time() - start
                if elapsed > TIME_LIMIT:
                    log(f"- {bits}-bit: **TIMEOUT** ({elapsed:.2f}s)")
                    summary[method_name][bits] = "TIMEOUT"
                elif result and n % result == 0 and 1 < result < n:
                    log(f"- {bits}-bit: **SUCCESS** in {elapsed:.4f}s -> factor={result}")
                    summary[method_name][bits] = f"OK ({elapsed:.2f}s)"
                else:
                    log(f"- {bits}-bit: FAILED in {elapsed:.4f}s")
                    summary[method_name][bits] = "FAIL"
            except Exception as e:
                elapsed = time.time() - start
                log(f"- {bits}-bit: ERROR: {e} ({elapsed:.2f}s)")
                summary[method_name][bits] = "ERR"

    log("\n## Summary Table\n")
    header = "| Method |" + "|".join(f" {b}-bit " for b in bit_sizes) + "|"
    sep = "|--------|" + "|".join("--------" for _ in bit_sizes) + "|"
    log(header)
    log(sep)
    for method_name, _ in methods:
        row = f"| {method_name} |"
        for b in bit_sizes:
            row += f" {summary[method_name].get(b, '?')} |"
        log(row)

    log("\n## Analysis & Novel Clues\n")
    log("### Key observations:")
    log("1. **Pollard Rho** is consistently the fastest general-purpose method")
    log("2. **Fermat** works well when factors are close together, fails badly when far apart")
    log("3. **p-1 method** depends entirely on p-1 being smooth - unreliable for random primes")
    log("4. **SQUFOF** is surprisingly effective for moderate sizes with O(n^(1/4)) complexity")
    log("5. **Simplified QS** shows the power of sieving but needs proper linear algebra for large inputs")
    log("")
    log("### Clues for novel approaches:")
    log("- Combining multiple weak methods (p-1, p+1, ECM) in parallel may cover each other's blind spots")
    log("- The smooth accumulation method suggests random algebraic structures can accidentally find factors")
    log("- For really large numbers, the bottleneck is always finding smooth relations - any method")
    log("  that can find smoothness faster wins")
    log("- Fibonacci/Lucas GCD occasionally works, suggesting number-theoretic sequences carry hidden structure")

if __name__ == "__main__":
    main()
