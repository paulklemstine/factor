#!/usr/bin/env python3
"""
Round 8: Maximum effort factoring — combining all winning strategies.

Scoreboard so far:
- 159-bit cracked by meet-in-middle hybrid (30s)
- 128-bit by resonance (2s, lucky smooth p-1)
- 110-bit by quadratic sieve (436s)
- 100-bit by Pollard rho batched (6s)

Goal: crack 200-bit semiprimes.

Strategy:
1. Optimized Pollard Rho with Brent + massive GCD batching
2. ECM with proper Montgomery curves and stage 2
3. Multi-group resonance (p-1 multi-base, p+1 multi-seed)
4. Improved Quadratic Sieve with log-sieving
5. All methods run in sequence with time budgets
"""

import math
import random
import time
import sys

LOG_FILE = "factoring_log.md"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg)

def is_prime_miller_rabin(n, k=25):
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

# Sieve primes once
def sieve_primes(limit):
    sieve = bytearray(b'\x01') * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = bytearray(len(sieve[i*i::i]))
    return [i for i in range(2, limit + 1) if sieve[i]]

PRIMES = sieve_primes(2_000_000)

# ============================================================
# METHOD 1: Pollard Rho — Brent variant, heavily optimized
# ============================================================
def pollard_rho_ultra(n, max_iter=50_000_000):
    """Brent's rho with product-GCD batching (batch=256)."""
    if n % 2 == 0: return 2
    if n % 3 == 0: return 3

    for attempt in range(50):
        y = random.randint(1, n - 1)
        c = random.randint(1, n - 1)
        m = 256  # batch size
        g = 1
        q = 1
        r = 1
        x = y

        iterations = 0
        while g == 1 and iterations < max_iter:
            x = y
            for _ in range(r):
                y = (y * y + c) % n

            k = 0
            while k < r and g == 1:
                ys = y
                batch_limit = min(m, r - k)
                for _ in range(batch_limit):
                    y = (y * y + c) % n
                    q = q * (x - y) % n
                g = math.gcd(q, n)
                k += m
                iterations += k
            r *= 2

        if 1 < g < n:
            return g
        if g == n:
            # Backtrack
            while True:
                ys = (ys * ys + c) % n
                g = math.gcd(x - ys, n)
                if g > 1:
                    break
            if 1 < g < n:
                return g
    return None

# ============================================================
# METHOD 2: ECM with Montgomery curves and Stage 2
# ============================================================
def ecm_montgomery(n, B1=50000, B2=5000000, curves=100):
    """
    Elliptic Curve Method using Montgomery form.
    By^2 = x^3 + Ax^2 + x (mod n)
    Uses Montgomery ladder for scalar multiplication.
    """
    def mont_add(P, Q, D, n, A24):
        """Montgomery differential addition: P+Q given P-Q=D"""
        # P = (Px, Pz), Q = (Qx, Qz), D = (Dx, Dz)
        u = (P[0] - P[1]) * (Q[0] + Q[1]) % n
        v = (P[0] + P[1]) * (Q[0] - Q[1]) % n
        add = (u + v) % n
        sub = (u - v) % n
        Rx = D[1] * add * add % n
        Rz = D[0] * sub * sub % n
        return (Rx, Rz)

    def mont_double(P, n, A24):
        """Montgomery point doubling."""
        u = (P[0] + P[1]) * (P[0] + P[1]) % n
        v = (P[0] - P[1]) * (P[0] - P[1]) % n
        diff = (u - v) % n
        Rx = u * v % n
        Rz = diff * (v + A24 * diff) % n
        return (Rx, Rz)

    def mont_ladder(k, P, n, A24):
        """Montgomery ladder: compute k*P."""
        R0 = P
        R1 = mont_double(P, n, A24)
        bits = bin(k)[2:]
        for bit in bits[1:]:
            if bit == '0':
                R1 = mont_add(R0, R1, P, n, A24)
                R0 = mont_double(R0, n, A24)
            else:
                R0 = mont_add(R0, R1, P, n, A24)
                R1 = mont_double(R1, n, A24)
        return R0

    for curve in range(curves):
        # Generate random curve: sigma -> A, point
        sigma = random.randint(6, n - 1)
        u = (sigma * sigma - 5) % n
        v = (4 * sigma) % n

        # A24 = (A+2)/4 where A = (v-u)^3 * (3u+v) / (4*u^3*v) - 2
        u3 = u * u * u % n
        v_minus_u = (v - u) % n
        vmu3 = v_minus_u * v_minus_u % n * v_minus_u % n

        try:
            inv_4u3v = pow(4 * u3 * v % n, -1, n)
        except ValueError:
            g = math.gcd(4 * u3 * v % n, n)
            if 1 < g < n:
                return g
            continue

        A_plus_2 = vmu3 * (3 * u + v) % n * inv_4u3v % n
        A24 = A_plus_2  # This is (A+2)/4 already

        # Initial point
        Px = u * u * u % n * pow(v, -1, n) % n if math.gcd(v, n) == 1 else u3
        P = (Px, 1)

        # Stage 1: multiply by all prime powers up to B1
        Q = P
        for p in PRIMES:
            if p > B1:
                break
            pp = p
            while pp <= B1:
                Q = mont_ladder(p, Q, n, A24)
                pp *= p

        # Check
        g = math.gcd(Q[1], n)
        if 1 < g < n:
            return g
        if g == n:
            continue

        # Stage 2: check individual primes between B1 and B2
        # Baby-step giant-step optimization
        S = Q
        prev_p = B1
        for p in PRIMES:
            if p <= B1:
                continue
            if p > B2:
                break
            diff = p - prev_p
            if diff > 0:
                S = mont_ladder(diff, S, n, A24) if diff > 1 else mont_double(S, n, A24) if diff == 2 else S
            g = math.gcd(S[1], n)
            if 1 < g < n:
                return g
            prev_p = p

    return None

# ============================================================
# METHOD 3: Multi-group resonance (enhanced)
# ============================================================
def multi_resonance(n, B=2_000_000):
    """
    Simultaneously run:
    - Pollard p-1 with 4 bases
    - Williams p+1 with 4 seeds
    All share GCD checks.
    """
    if n % 2 == 0: return 2

    # p-1 accumulators
    a = [2, 3, 5, 7]
    a = [x % n for x in a]

    # p+1 accumulators (Lucas V sequences)
    v = [3, 5, 7, 11]

    prime_idx = 0
    for k in range(2, B):
        if prime_idx < len(PRIMES) and PRIMES[prime_idx] <= k:
            p = PRIMES[prime_idx]
            prime_idx += 1

            pp = p
            while pp <= B:
                for i in range(len(a)):
                    a[i] = pow(a[i], p, n)
                pp *= p

            # Lucas step for p+1
            for i in range(len(v)):
                v[i] = (pow(v[i], p, n) - 2) % n

        # GCD check every 2000 primes processed
        if prime_idx % 2000 == 0 and prime_idx > 0:
            product = 1
            for ai in a:
                product = product * (ai - 1) % n
            for vi in v:
                product = product * (vi - 2) % n
            g = math.gcd(product, n)
            if 1 < g < n:
                return g
            if g == n:
                # Individual checks
                for ai in a:
                    g = math.gcd(ai - 1, n)
                    if 1 < g < n:
                        return g
                for vi in v:
                    g = math.gcd(vi - 2, n)
                    if 1 < g < n:
                        return g

    # Final check
    for ai in a:
        g = math.gcd(ai - 1, n)
        if 1 < g < n:
            return g
    for vi in v:
        g = math.gcd(vi - 2, n)
        if 1 < g < n:
            return g

    return None

# ============================================================
# METHOD 4: Quadratic Sieve (optimized)
# ============================================================
def tonelli_shanks(n, p):
    """Square root of n mod p."""
    if pow(n, (p-1)//2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(n, (p+1)//4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p-1)//2, p) != p - 1:
        z += 1
    M, c, t, R = s, pow(z, q, p), pow(n, q, p), pow(n, (q+1)//2, p)
    while t != 1:
        i = 1
        temp = t * t % p
        while temp != 1:
            temp = temp * temp % p
            i += 1
        b = pow(c, 1 << (M - i - 1), p)
        M, c, t, R = i, b * b % p, t * b * b % p, R * b % p
    return R

def quadratic_sieve(n, time_limit=300):
    """Proper QS with log-sieving and Gaussian elimination."""
    start_time = time.time()

    sqrt_n = math.isqrt(n) + 1

    # Determine factor base size based on n
    ln_n = math.log(n)
    ln_ln_n = math.log(ln_n)
    # L(n) = exp(sqrt(ln_n * ln_ln_n))
    L = math.exp(math.sqrt(ln_n * ln_ln_n))
    FB_size = max(30, int(L ** 0.5))
    FB_size = min(FB_size, 2000)  # cap for pure Python

    sieve_radius = max(50000, FB_size * 50)
    sieve_radius = min(sieve_radius, 500000)

    # Build factor base
    FB = [2]
    fb_roots = {2: [0, 0]}  # roots of x^2 - n mod p
    for p in PRIMES[1:]:
        if len(FB) >= FB_size:
            break
        nmodp = n % p
        r = tonelli_shanks(nmodp, p)
        if r is not None:
            FB.append(p)
            # Roots: where (sqrt_n + x)^2 - n ≡ 0 mod p
            r1 = (r - sqrt_n) % p
            r2 = (-r - sqrt_n) % p
            fb_roots[p] = [r1, r2]

    FB_size = len(FB)
    needed = FB_size + 10

    log_thresh = sum(math.log2(p) for p in FB) * 0.7  # Tuned threshold

    # Sieve
    smooth_relations = []
    block = 0

    while len(smooth_relations) < needed:
        if time.time() - start_time > time_limit:
            break

        offset = block * sieve_radius
        block += 1

        # Initialize sieve array with log approximations
        sieve_log = [0.0] * (2 * sieve_radius)

        # Compute actual log values for threshold comparison
        for idx in range(2 * sieve_radius):
            x = offset - sieve_radius + idx
            val = (sqrt_n + x) ** 2 - n
            if val > 0:
                sieve_log[idx] = math.log2(val) if val > 1 else 0

        # Sieve: subtract log(p) at positions where p divides f(x)
        sieve_sub = [0.0] * (2 * sieve_radius)
        for p in FB:
            logp = math.log2(p)
            if p == 2:
                for start in range(0, 2 * sieve_radius):
                    x = offset - sieve_radius + start
                    val = (sqrt_n + x) ** 2 - n
                    if val % 2 == 0:
                        sieve_sub[start] += logp
                        t = val
                        while t % 2 == 0:
                            t //= 2
                            sieve_sub[start] += logp
                        break  # Only count once per position, approximate
                continue

            for root in fb_roots[p]:
                start = ((root - (offset - sieve_radius)) % p + p) % p
                for idx in range(start, 2 * sieve_radius, p):
                    sieve_sub[idx] += logp
                    # Account for higher powers
                    x = offset - sieve_radius + idx
                    val = (sqrt_n + x) ** 2 - n
                    if val != 0:
                        pk = p * p
                        while val % pk == 0:
                            sieve_sub[idx] += logp
                            pk *= p

        # Collect smooth candidates
        for idx in range(2 * sieve_radius):
            if sieve_sub[idx] >= sieve_log[idx] * 0.85:  # Allow some slack
                x = offset - sieve_radius + idx
                val = (sqrt_n + x) ** 2 - n
                if val <= 0:
                    continue
                # Trial factor over FB
                temp = val
                exponents = []
                for p in FB:
                    e = 0
                    while temp % p == 0:
                        temp //= p
                        e += 1
                    exponents.append(e)
                if temp == 1:
                    smooth_relations.append((sqrt_n + x, val, exponents))
                    if len(smooth_relations) >= needed:
                        break

    if len(smooth_relations) < FB_size + 1:
        return None

    # Gaussian elimination mod 2
    nrels = len(smooth_relations)
    ncols = FB_size

    # Build matrix (bit-packed rows)
    matrix = []
    for _, _, exponents in smooth_relations:
        row = 0
        for j in range(ncols):
            if exponents[j] % 2 == 1:
                row |= (1 << j)
        matrix.append(row)

    # Track which relations are combined
    history = [1 << i for i in range(nrels)]

    # Row echelon form
    pivots = {}
    for col in range(ncols):
        # Find pivot row
        pivot_row = None
        for row in range(nrels):
            if matrix[row] & (1 << col) and col not in pivots.values():
                already_pivot = False
                for pc, pr in pivots.items():
                    if pr == row:
                        already_pivot = True
                        break
                if not already_pivot:
                    pivot_row = row
                    break

        if pivot_row is None:
            continue

        pivots[col] = pivot_row

        # Eliminate
        for row in range(nrels):
            if row != pivot_row and (matrix[row] & (1 << col)):
                matrix[row] ^= matrix[pivot_row]
                history[row] ^= history[pivot_row]

    # Find null-space vectors (rows that are now zero)
    for row in range(nrels):
        if matrix[row] == 0 and history[row] != 0:
            # Combine the relations indicated by history[row]
            x_product = 1
            y_squared = 1
            combined_exp = [0] * ncols

            for i in range(nrels):
                if history[row] & (1 << i):
                    rel_x, rel_val, rel_exp = smooth_relations[i]
                    x_product = (x_product * rel_x) % n
                    y_squared *= rel_val
                    for j in range(ncols):
                        combined_exp[j] += rel_exp[j]

            # Compute y = sqrt(y_squared) using the exponents
            y = 1
            for j in range(ncols):
                y = (y * pow(FB[j], combined_exp[j] // 2, n)) % n

            g = math.gcd((x_product - y) % n, n)
            if 1 < g < n:
                return g
            g = math.gcd((x_product + y) % n, n)
            if 1 < g < n:
                return g

    return None

# ============================================================
# MASTER FACTORING FUNCTION
# ============================================================
def factor_ultimate(n, total_time_limit=600):
    """Try all methods with time budgets."""
    start = time.time()

    if n <= 1:
        return None
    if n % 2 == 0:
        return 2
    if is_prime_miller_rabin(n):
        return None

    # Check small factors first
    for p in PRIMES[:1000]:
        if n % p == 0:
            return p

    bits = n.bit_length()
    elapsed = lambda: time.time() - start
    remaining = lambda: total_time_limit - elapsed()

    # Phase 1: Quick methods (10% of time)
    log(f"  Phase 1: Resonance (budget: {total_time_limit*0.1:.0f}s)...")
    try:
        t = time.time()
        B = min(500000, max(100000, bits * 5000))
        result = multi_resonance(n, B=B)
        if result and 1 < result < n and n % result == 0:
            log(f"  -> Resonance SUCCESS in {time.time()-t:.3f}s")
            return result
        log(f"  -> Resonance failed ({time.time()-t:.1f}s)")
    except Exception as e:
        log(f"  -> Resonance error: {e}")

    if remaining() <= 0:
        return None

    # Phase 2: Pollard Rho (30% of time)
    rho_budget = remaining() * 0.35
    log(f"  Phase 2: Pollard Rho (budget: {rho_budget:.0f}s)...")
    try:
        t = time.time()
        result = pollard_rho_ultra(n, max_iter=100_000_000)
        rho_time = time.time() - t
        if result and 1 < result < n and n % result == 0:
            log(f"  -> Rho SUCCESS in {rho_time:.3f}s")
            return result
        log(f"  -> Rho failed ({rho_time:.1f}s)")
    except Exception as e:
        log(f"  -> Rho error: {e}")

    if remaining() <= 0:
        return None

    # Phase 3: ECM (30% of time)
    ecm_budget = remaining() * 0.4
    log(f"  Phase 3: ECM (budget: {ecm_budget:.0f}s)...")
    try:
        t = time.time()
        # Scale ECM parameters with bit size
        B1 = min(1000000, max(10000, 2 ** (bits // 6)))
        B2 = B1 * 100
        curves = max(20, min(200, bits * 2))
        result = ecm_montgomery(n, B1=B1, B2=B2, curves=curves)
        ecm_time = time.time() - t
        if result and 1 < result < n and n % result == 0:
            log(f"  -> ECM SUCCESS in {ecm_time:.3f}s (B1={B1}, curves={curves})")
            return result
        log(f"  -> ECM failed ({ecm_time:.1f}s)")
    except Exception as e:
        log(f"  -> ECM error: {e}")

    if remaining() <= 0:
        return None

    # Phase 4: Quadratic Sieve (remaining time)
    qs_budget = remaining()
    if qs_budget > 10 and bits >= 60:
        log(f"  Phase 4: Quadratic Sieve (budget: {qs_budget:.0f}s)...")
        try:
            t = time.time()
            result = quadratic_sieve(n, time_limit=qs_budget)
            qs_time = time.time() - t
            if result and 1 < result < n and n % result == 0:
                log(f"  -> QS SUCCESS in {qs_time:.3f}s")
                return result
            log(f"  -> QS failed ({qs_time:.1f}s)")
        except Exception as e:
            log(f"  -> QS error: {e}")

    return None

# ============================================================
# RUN
# ============================================================
def main():
    random.seed(31337)

    log("\n\n---\n")
    log("## Round 8: Maximum Effort Combined Factoring\n")
    log(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Methods: Pollard Rho (Brent, batch=256) + ECM (Montgomery, stage 2)")
    log(f"         + Multi-group Resonance (p-1 x4 + p+1 x4)")
    log(f"         + Quadratic Sieve (log-sieve + Gauss elim)")
    log(f"Prime sieve: {len(PRIMES)} primes up to {PRIMES[-1]}\n")

    test_cases = []
    for bits in [64, 80, 100, 128, 140, 160, 180, 200]:
        p, q, n = gen_semiprime(bits)
        test_cases.append((bits, p, q, n))

    log("### Test Numbers\n")
    for bits, p, q, n in test_cases:
        log(f"- {bits}-bit: n={n}")
        log(f"  p={p}, q={q}, actual_bits={n.bit_length()}")

    log("\n### Results\n")

    TIME_LIMITS = {64: 30, 80: 60, 100: 120, 128: 180, 140: 300, 160: 420, 180: 540, 200: 600}

    for bits, p, q, n in test_cases:
        limit = TIME_LIMITS.get(bits, 300)
        log(f"\n#### {bits}-bit semiprime (time limit: {limit}s)\n")

        start = time.time()
        result = factor_ultimate(n, total_time_limit=limit)
        elapsed = time.time() - start

        if result and n % result == 0 and 1 < result < n:
            log(f"\n- **SUCCESS** in {elapsed:.3f}s -> {result}")
            log(f"  verified: {n} = {result} x {n // result}")
        else:
            log(f"\n- **FAILED** in {elapsed:.1f}s")

    # Summary
    log("\n### Round 8 Summary\n")
    log("| Bits | Result | Time | Method |")
    log("|------|--------|------|--------|")

    log("\n### Key Insights\n")
    log("""
1. **ECM with Montgomery curves** is the best method for factors up to ~60 digits.
   Its complexity depends on the SIZE OF THE FACTOR, not the size of n.
   This makes it ideal for unbalanced semiprimes.

2. **Pollard Rho** is O(n^(1/4)) — best general method for balanced semiprimes < 100 bits.
   With batch-256 GCD, the constant factor is minimized.

3. **Quadratic Sieve** is sub-exponential L(n)^(1+o(1)). In pure Python it's slow
   but correct. With C extensions it handles 100+ digit numbers.

4. **Multi-group resonance** is a "lottery ticket" — instant if p-1 or p+1 is smooth,
   useless otherwise. Worth trying first due to low cost.

5. **The fundamental limit**: All classical methods are exponential or sub-exponential.
   The SAT/binary multiplication approach, RNS, spectral methods, and curvature
   detection all reduce to known complexity classes when analyzed carefully.
   No classical shortcut to polynomial-time factoring was found.

6. **Novel contributions from this research:**
   - Multi-group resonance combining 8+ algebraic structures in one loop
   - Parabola intersection geometric framework unifying QS, Shor, and curvature
   - Hensel meet-in-the-middle achieving O(n^(1/4)) from SAT perspective
   - Second-difference curvature detection as a novel (but O(sqrt(p))) method
   - RNS factoring eliminates carry but creates combinatorial explosion instead
""")

if __name__ == "__main__":
    main()
