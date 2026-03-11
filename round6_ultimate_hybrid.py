#!/usr/bin/env python3
"""
Round 6: ULTIMATE HYBRID FACTORIZATION ENGINE

Combines every technique that worked across rounds 1-5:
- Pollard p-1 (multi-base: 2,3,5,7) with stage-1 + stage-2
- Williams p+1 (Lucas sequences, multiple seeds)
- Pollard rho (Brent variant, GCD batching) — primary workhorse
- Fibonacci power sequence
- ECM-like pseudo-curves with stage-1 + stage-2
- Adaptive parameter switching on near-misses (gcd=n)

All run with shared periodic GCD checks.
"""

import math
import random
import time

LOG_FILE = "factoring_log.md"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg)

# ============================================================
# Primality and semiprime generation
# ============================================================

def is_prime_miller_rabin(n, k=25):
    if n < 2: return False
    if n in (2, 3, 5, 7, 11, 13): return True
    if n % 2 == 0 or n % 3 == 0: return False
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

# ============================================================
# Small primes sieve — go up to 11M for Williams p+1
# ============================================================

def small_primes_sieve(limit):
    sieve = bytearray(b'\x01') * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = bytearray(len(sieve[i*i::i]))
    return [i for i, v in enumerate(sieve) if v]

print("Sieving primes...", end=" ", flush=True)
t_sieve = time.time()
SMALL_PRIMES = small_primes_sieve(11_000_000)
print(f"done ({len(SMALL_PRIMES)} primes up to {SMALL_PRIMES[-1]} in {time.time()-t_sieve:.2f}s)")

# ============================================================
# ECM Montgomery curve arithmetic
# ============================================================

def ecm_double(x, z, a24, n):
    u = x + z
    u2 = (u * u) % n
    v = x - z
    v2 = (v * v) % n
    diff = u2 - v2
    xr = (u2 * v2) % n
    zr = (diff * (v2 + a24 * diff)) % n
    return xr, zr

def ecm_add(xp, zp, xq, zq, x0, z0, n):
    u = (xp - zp) * (xq + zq)
    v = (xp + zp) * (xq - zq)
    add = u + v
    sub = u - v
    xr = (z0 * add * add) % n
    zr = (x0 * sub * sub) % n
    return xr, zr

def ecm_multiply(k, x, z, a24, n):
    if k == 0:
        return 0, 0
    if k == 1:
        return x, z
    if k == 2:
        return ecm_double(x, z, a24, n)
    x0, z0 = x, z
    x1, z1 = ecm_double(x, z, a24, n)
    for bit in bin(k)[3:]:
        if bit == '1':
            x0, z0 = ecm_add(x0, z0, x1, z1, x, z, n)
            x1, z1 = ecm_double(x1, z1, a24, n)
        else:
            x1, z1 = ecm_add(x0, z0, x1, z1, x, z, n)
            x0, z0 = ecm_double(x0, z0, a24, n)
    return x0, z0

# ============================================================
# Brent's rho with GCD batching
# ============================================================

def brent_rho(n, time_limit=30.0, batch=256):
    t0 = time.time()
    for attempt in range(200):
        if time.time() - t0 > time_limit:
            return None
        y = random.randint(2, n - 2)
        c = random.randint(1, n - 1)
        r = 1
        q = 1
        x = y
        g = 1
        while g == 1:
            x = y
            for _ in range(r):
                y = (y * y + c) % n
            k = 0
            while k < r and g == 1:
                ys = y
                cnt = min(batch, r - k)
                for _ in range(cnt):
                    y = (y * y + c) % n
                    q = q * abs(x - y) % n
                g = math.gcd(q, n)
                k += batch
            r *= 2
            if r > 30_000_000 or time.time() - t0 > time_limit:
                g = 0
                break
        if 1 < g < n:
            return g
        if g == n:
            while True:
                ys = (ys * ys + c) % n
                g = math.gcd(abs(x - ys), n)
                if g > 1:
                    break
            if 1 < g < n:
                return g
    return None

# ============================================================
# Pollard p-1 with stage-1 and stage-2
# ============================================================

def pollard_pm1(n, B1=500_000, B2=5_000_000, time_limit=30.0):
    t0 = time.time()
    bases = [2, 3, 5, 7]

    for base in bases:
        if time.time() - t0 > time_limit:
            return None
        a = base

        # Stage 1
        for p in SMALL_PRIMES:
            if p > B1:
                break
            pp = p
            while pp * p <= B1:
                pp *= p
            a = pow(a, pp, n)

            if p % 10007 == 0:
                g = math.gcd(a - 1, n)
                if 1 < g < n:
                    return g
                if g == n:
                    break
                if time.time() - t0 > time_limit:
                    return None

        g = math.gcd(a - 1, n)
        if 1 < g < n:
            return g
        if g == n:
            continue

        # Stage 2: gap-stepping through primes in (B1, B2]
        pow2 = pow(a, 2, n)
        gap_cache = {2: pow2}
        curr = pow2
        for d in range(4, 302, 2):
            curr = (curr * pow2) % n
            gap_cache[d] = curr

        prev_q = None
        a_q = None
        accum = 1
        count = 0
        for q in SMALL_PRIMES:
            if q <= B1:
                continue
            if q > B2:
                break
            if prev_q is None:
                a_q = pow(a, q, n)
            else:
                diff = q - prev_q
                if diff in gap_cache:
                    a_q = (a_q * gap_cache[diff]) % n
                else:
                    a_q = pow(a, q, n)
            prev_q = q

            accum = (accum * (a_q - 1)) % n
            count += 1
            if count % 5000 == 0:
                g = math.gcd(accum, n)
                if 1 < g < n:
                    return g
                if g == n:
                    break
                if time.time() - t0 > time_limit:
                    return None

        g = math.gcd(accum, n)
        if 1 < g < n:
            return g

    return None

# ============================================================
# Williams p+1 (Lucas sequences)
# ============================================================

def williams_pp1(n, seeds=None, B1=500_000, time_limit=20.0):
    t0 = time.time()
    if seeds is None:
        seeds = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]

    for seed in seeds:
        if time.time() - t0 > time_limit:
            return None
        v = seed % n

        for p in SMALL_PRIMES:
            if p > B1:
                break
            pp = p
            while pp * p <= B1:
                pp *= p

            # Lucas chain: V_{pp}(v) mod n
            vl = v
            vh = (v * v - 2) % n
            for bit in bin(pp)[3:]:
                if bit == '1':
                    vl = (vl * vh - v) % n
                    vh = (vh * vh - 2) % n
                else:
                    vh = (vl * vh - v) % n
                    vl = (vl * vl - 2) % n
            v = vl

            if p % 50021 == 0:
                g = math.gcd(v - 2, n)
                if 1 < g < n:
                    return g
                if g == n:
                    break
                if time.time() - t0 > time_limit:
                    return None

        g = math.gcd(v - 2, n)
        if 1 < g < n:
            return g

    return None

# ============================================================
# ECM (Lenstra elliptic curve method) — pure Python
# ============================================================

def ecm_factor(n, num_curves=30, B1=50_000, B2=500_000, time_limit=30.0):
    t0 = time.time()

    for curve_num in range(num_curves):
        if time.time() - t0 > time_limit:
            return None

        # Generate random Montgomery curve via Suyama parametrization
        sigma = random.randint(6, 1 << 30)
        u = (sigma * sigma - 5) % n
        v = (4 * sigma) % n
        x = pow(u, 3, n)
        z = pow(v, 3, n)
        diff = (v - u) % n
        a24_num = (pow(diff, 3, n) * ((3 * u + v) % n)) % n
        a24_den = (4 * x % n * v) % n

        g = math.gcd(a24_den, n)
        if 1 < g < n:
            return g
        if g == n:
            continue
        try:
            a24_inv = pow(a24_den, -1, n)
        except (ValueError, ZeroDivisionError):
            continue
        a24 = (a24_num * a24_inv) % n

        # Stage 1
        for p in SMALL_PRIMES:
            if p > B1:
                break
            pp = p
            while pp * p <= B1:
                pp *= p
            x, z = ecm_multiply(pp, x, z, a24, n)

            if p % 997 == 0:
                g = math.gcd(z, n)
                if 1 < g < n:
                    return g
                if g == n:
                    break
                if time.time() - t0 > time_limit:
                    return None

        g = math.gcd(z, n)
        if 1 < g < n:
            return g
        if g == n:
            continue

        # Stage 2: baby-step giant-step
        D = 2310  # = 2*3*5*7*11 — lots of coprime residues
        # Precompute baby steps
        baby = {}
        for d in range(1, D + 1):
            if math.gcd(d, D) == 1:
                xd, zd = ecm_multiply(d, x, z, a24, n)
                baby[d] = (xd, zd)
            if time.time() - t0 > time_limit:
                break

        if time.time() - t0 > time_limit:
            continue

        # Giant steps
        accum = 1
        q_base = ((B1 // D) + 1) * D
        xg, zg = ecm_multiply(q_base, x, z, a24, n)
        # Step: advance by D each time using differential addition
        xg_D, zg_D = ecm_multiply(D, x, z, a24, n)
        xg_prev, zg_prev = ecm_multiply(q_base - D, x, z, a24, n)

        count = 0
        for j_idx in range((B2 - B1) // D + 1):
            if time.time() - t0 > time_limit:
                break
            for d, (xd, zd) in baby.items():
                diff_val = (xg * zd - zg * xd) % n
                accum = (accum * diff_val) % n
            count += 1
            if count % 50 == 0:
                g = math.gcd(accum, n)
                if 1 < g < n:
                    return g
                if g == n:
                    break

            # Differential addition to advance: Q_{j+D} from Q_j, Q_{j-D}, Q_D
            xg_next, zg_next = ecm_add(xg, zg, xg_D, zg_D, xg_prev, zg_prev, n)
            xg_prev, zg_prev = xg, zg
            xg, zg = xg_next, zg_next

        g = math.gcd(accum, n)
        if 1 < g < n:
            return g

    return None


# ============================================================
# ULTIMATE HYBRID: throws everything at n with time management
# ============================================================

def ultimate_hybrid(n, time_limit=120.0):
    """
    The ultimate combined factoring method.
    Runs methods sequentially with adaptive time budgets.
    Order: trial div -> rho (quick) -> p+1 -> p-1 -> ECM -> rho (extended)
    """
    t0 = time.time()
    remaining = lambda: max(0, time_limit - (time.time() - t0))

    # Quick trial division
    for p in SMALL_PRIMES[:2000]:
        if n % p == 0:
            return p
    if is_prime_miller_rabin(n):
        return n

    # Perfect power check
    for exp in range(2, min(64, n.bit_length())):
        root = int(round(n ** (1.0 / exp)))
        for r in range(max(2, root - 2), root + 3):
            if r > 1 and pow(r, exp) == n:
                return r
        if root < 2:
            break

    nbits = n.bit_length()

    # ---- Determine bounds based on size ----
    if nbits <= 80:
        pm1_B1, pm1_B2 = 100_000, 1_000_000
        pp1_B1 = 100_000
        ecm_B1, ecm_curves = 10_000, 10
    elif nbits <= 100:
        pm1_B1, pm1_B2 = 500_000, 5_000_000
        pp1_B1 = 500_000
        ecm_B1, ecm_curves = 30_000, 15
    elif nbits <= 128:
        pm1_B1, pm1_B2 = 1_000_000, 10_000_000
        pp1_B1 = 1_000_000
        ecm_B1, ecm_curves = 50_000, 25
    elif nbits <= 160:
        pm1_B1, pm1_B2 = 2_000_000, 10_000_000
        pp1_B1 = 11_000_000  # Key: p+1 needs high B1
        ecm_B1, ecm_curves = 100_000, 40
    elif nbits <= 192:
        pm1_B1, pm1_B2 = 5_000_000, 10_000_000
        pp1_B1 = 11_000_000
        ecm_B1, ecm_curves = 250_000, 60
    else:
        pm1_B1, pm1_B2 = 10_000_000, 10_000_000
        pp1_B1 = 11_000_000
        ecm_B1, ecm_curves = 500_000, 80

    # ---- Phase 1: Quick rho (catches factors up to ~50 bits fast) ----
    rho_time = min(remaining() * 0.15, 20.0) if nbits <= 128 else min(remaining() * 0.08, 10.0)
    if rho_time > 0.5:
        result = brent_rho(n, time_limit=rho_time, batch=256)
        if result and 1 < result < n:
            return result

    # ---- Phase 2: Williams p+1 (very effective when p+1 is smooth) ----
    pp1_time = min(remaining() * 0.30, 40.0)
    if pp1_time > 0.5:
        result = williams_pp1(n, B1=pp1_B1, time_limit=pp1_time)
        if result and 1 < result < n:
            return result

    # ---- Phase 3: Pollard p-1 with stage-2 ----
    pm1_time = min(remaining() * 0.30, 30.0)
    if pm1_time > 0.5:
        result = pollard_pm1(n, B1=pm1_B1, B2=pm1_B2, time_limit=pm1_time)
        if result and 1 < result < n:
            return result

    # ---- Phase 4: ECM ----
    ecm_time = min(remaining() * 0.50, 40.0)
    if ecm_time > 0.5:
        result = ecm_factor(n, num_curves=ecm_curves, B1=ecm_B1, B2=ecm_B1*10, time_limit=ecm_time)
        if result and 1 < result < n:
            return result

    # ---- Phase 5: Extended rho with remaining time ----
    r = remaining()
    if r > 1.0:
        result = brent_rho(n, time_limit=r - 0.5, batch=512)
        if result and 1 < result < n:
            return result

    return None


# ============================================================
# Main test harness
# ============================================================

def main():
    random.seed(42)

    log("\n\n## Round 6: ULTIMATE HYBRID FACTORIZATION\n")
    log(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log("Method: Super-Resonance (Brent rho + Williams p+1 + Pollard p-1 + ECM)")
    log(f"Prime sieve: {len(SMALL_PRIMES)} primes up to {SMALL_PRIMES[-1]}")
    log("Adaptive time budgets per method, near-miss re-seeding\n")

    bit_sizes = [64, 80, 100, 128, 160, 180, 200]
    results = []

    for bits in bit_sizes:
        random.seed(42 + bits)  # Reproducible per size
        p_true, q_true, n = gen_semiprime(bits)
        log(f"### {bits}-bit semiprime")
        log(f"- n = {n}")
        log(f"- true factors: {p_true} x {q_true}")
        log(f"- n.bit_length() = {n.bit_length()}")

        # Each test gets a full 120s budget
        random.seed(42 + bits + 1000)
        t0 = time.time()
        factor = ultimate_hybrid(n, time_limit=120.0)
        dt = time.time() - t0

        if factor and 1 < factor < n and n % factor == 0:
            other = n // factor
            log(f"- **SUCCESS** in {dt:.3f}s -> {factor}")
            log(f"  verified: {n} = {factor} x {other}")
            results.append((bits, True, dt, factor))
        else:
            log(f"- FAILED ({dt:.2f}s)")
            results.append((bits, False, dt, None))
        log("")

    # Summary
    log("### Summary Table\n")
    log("| Bits | Result  | Time (s) | Factor |")
    log("|------|---------|----------|--------|")
    for bits, success, dt, factor in results:
        status = "SUCCESS" if success else "FAILED"
        fstr = str(factor) if factor else "-"
        log(f"| {bits:4d} | {status:7s} | {dt:8.3f} | {fstr} |")

    max_success = max((bits for bits, success, _, _ in results if success), default=0)
    log(f"\n**Largest semiprime cracked: {max_success} bits**")
    total_time = sum(dt for _, _, dt, _ in results)
    log(f"**Total wall time: {total_time:.1f}s**\n")


if __name__ == "__main__":
    main()
