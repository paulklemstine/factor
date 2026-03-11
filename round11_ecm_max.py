#!/usr/bin/env python3
"""
Round 11: Maximum ECM Push — targeting 180-200 bit semiprimes.

Previous record: 160-bit (ECM, 164s, round 8/9).

Key improvements over round 9:
1. Suyama parameterization with correct A24 = (A+2)/4 for torsion Z/12Z
2. Montgomery ladder with proper differential addition
3. Stage 2 with baby-step giant-step using wheel D=2310 (2*3*5*7*11)
4. Proper giant step via differential addition (NOT recomputing mont_ladder)
5. Batch GCD accumulation every 100 giant steps
6. Optimal B1/B2/curves from GMP-ECM research tables
7. Quick pre-pass: Pollard rho + multi-group resonance (p-1/p+1)
8. Sieve primes up to 11M for Stage 1
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
# Utility: Miller-Rabin, prime generation, semiprime generation
# ============================================================
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

def sieve_primes(limit):
    """Sieve of Eratosthenes up to limit."""
    sieve = bytearray(b'\x01') * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = bytearray(len(sieve[i*i::i]))
    return [i for i in range(2, limit + 1) if sieve[i]]

# ============================================================
# Montgomery curve arithmetic (X:Z projective coordinates)
# ============================================================
def mont_double(x, z, a24, n):
    """Montgomery curve doubling: 2P from P, using (A+2)/4."""
    s = (x + z) % n
    d = (x - z) % n
    s2 = s * s % n
    d2 = d * d % n
    diff = (s2 - d2) % n
    rx = s2 * d2 % n
    rz = diff * (d2 + a24 * diff) % n
    return rx, rz

def mont_add(x1, z1, x2, z2, dx, dz, n):
    """Montgomery differential addition: P1+P2 given P1-P2=(dx,dz)."""
    u = (x1 - z1) * (x2 + z2) % n
    v = (x1 + z1) * (x2 - z2) % n
    add = (u + v) % n
    sub = (u - v) % n
    rx = dz * (add * add % n) % n
    rz = dx * (sub * sub % n) % n
    return rx, rz

def mont_ladder(k, px, pz, a24, n):
    """Montgomery ladder scalar multiplication: k*P."""
    if k == 0: return 0, 1
    if k == 1: return px, pz
    if k == 2: return mont_double(px, pz, a24, n)
    r0x, r0z = px, pz
    r1x, r1z = mont_double(px, pz, a24, n)
    for bit in bin(k)[3:]:  # skip '0b1'
        if bit == '0':
            r1x, r1z = mont_add(r0x, r0z, r1x, r1z, px, pz, n)
            r0x, r0z = mont_double(r0x, r0z, a24, n)
        else:
            r0x, r0z = mont_add(r0x, r0z, r1x, r1z, px, pz, n)
            r1x, r1z = mont_double(r1x, r1z, a24, n)
    return r0x, r0z

def mont_mul_int(k, px, pz, a24, n):
    """Multiply point by small integer k using addition chain."""
    if k <= 2:
        if k == 0: return 0, 1
        if k == 1: return px, pz
        return mont_double(px, pz, a24, n)
    return mont_ladder(k, px, pz, a24, n)

# ============================================================
# Wheel D=2310 for Stage 2
# ============================================================
D_WHEEL = 2310  # 2 * 3 * 5 * 7 * 11

def compute_wheel_residues(D):
    """Compute residues coprime to D in [1, D)."""
    residues = []
    for r in range(1, D):
        if math.gcd(r, D) == 1:
            residues.append(r)
    return residues

WHEEL_RESIDUES = compute_wheel_residues(D_WHEEL)

# ============================================================
# ECM with Suyama parameterization + Stage 2 BSGS
# ============================================================
def ecm_suyama(n, B1, B2, max_curves, primes, time_limit=None):
    """
    ECM with:
    - Suyama curve parameterization (torsion Z/12Z)
    - Montgomery ladder for Stage 1
    - Baby-step giant-step Stage 2 with wheel D=2310
    - Batch GCD every 100 giant steps
    """
    start_time = time.time()

    for curve_num in range(max_curves):
        elapsed = time.time() - start_time
        if time_limit and elapsed > time_limit:
            return None

        # === Suyama parameterization ===
        sigma = random.randint(6, n - 1)
        u = (sigma * sigma - 5) % n
        v = (4 * sigma) % n

        # A24 = (v-u)^3 * (3u+v) / (16*u^3*v)  which equals (A+2)/4
        u3 = u * u % n * u % n
        v_minus_u = (v - u) % n
        vm3 = v_minus_u * v_minus_u % n * v_minus_u % n  # (v-u)^3
        three_u_plus_v = (3 * u + v) % n

        denom = 16 * u3 % n * v % n
        try:
            inv_denom = pow(denom, -1, n)
        except (ValueError, ZeroDivisionError):
            g = math.gcd(denom % n, n)
            if 1 < g < n:
                return g
            continue

        a24 = vm3 * three_u_plus_v % n * inv_denom % n

        # Initial point P = (u^3 : v^3)
        px = u3 % n
        pz = v * v % n * v % n

        # === Stage 1: multiply Q by all prime powers up to B1 ===
        qx, qz = px, pz
        for p in primes:
            if p > B1:
                break
            # Multiply by p^e where p^e <= B1
            pp = p
            while pp <= B1:
                qx, qz = mont_ladder(p, qx, qz, a24, n)
                pp *= p

        g = math.gcd(qz % n, n)
        if 1 < g < n:
            return g
        if g == n:
            continue  # curve killed the point

        # === Stage 2: baby-step giant-step with wheel D=2310 ===
        if B2 <= B1:
            continue

        # Baby steps: compute d*Q for each d in WHEEL_RESIDUES
        # We need multiples up to D_WHEEL. Build them via an addition chain.
        # First compute small multiples: 1Q, 2Q, then d*Q for all needed d.
        q1x, q1z = qx, qz  # 1*Q
        q2x, q2z = mont_double(qx, qz, a24, n)  # 2*Q

        # Store all multiples up to D_WHEEL that we need
        # Use a simple approach: compute i*Q for i=1..max(WHEEL_RESIDUES)
        # via differential addition: (i+1)*Q from i*Q, (i-1)*Q, and 1*Q
        max_r = WHEEL_RESIDUES[-1]  # max residue value
        mult = {}
        mult[1] = (q1x, q1z)
        mult[2] = (q2x, q2z)

        # Build up to max_r using differential addition chain
        # i*Q + 1*Q = (i+1)*Q with difference (i-1)*Q
        prev_x, prev_z = q1x, q1z  # (i-1)*Q for i=2 -> 1*Q
        curr_x, curr_z = q2x, q2z  # i*Q for i=2 -> 2*Q
        for i in range(3, max_r + 1):
            next_x, next_z = mont_add(curr_x, curr_z, q1x, q1z, prev_x, prev_z, n)
            mult[i] = (next_x, next_z)
            prev_x, prev_z = curr_x, curr_z
            curr_x, curr_z = next_x, next_z

        # Extract baby step table: only the wheel residues
        baby = {}
        for r in WHEEL_RESIDUES:
            if r in mult:
                baby[r] = mult[r]

        # Also need D*Q for the giant step
        # Compute via mont_ladder (only done once)
        dqx, dqz = mont_ladder(D_WHEEL, qx, qz, a24, n)

        # Starting giant step position: round B1 up to next multiple of D
        m_start = (B1 // D_WHEEL) + 1
        m_end = (B2 // D_WHEEL) + 1

        # Compute m_start * D * Q using mont_ladder (once)
        base_x, base_z = mont_ladder(m_start * D_WHEEL, qx, qz, a24, n)

        # For differential giant step: we need (m_start-1)*D*Q too
        # So we can do: next = base + D*Q with diff = prev
        # Actually need two consecutive: base and base_prev
        if m_start > 1:
            prev_base_x, prev_base_z = mont_ladder((m_start - 1) * D_WHEEL, qx, qz, a24, n)
        else:
            prev_base_x, prev_base_z = 0, 1

        # Batch product for GCD
        product = 1
        giant_count = 0

        for m in range(m_start, m_end + 1):
            if time_limit and time.time() - start_time > time_limit:
                # Final GCD check before timeout
                g = math.gcd(product, n)
                if 1 < g < n:
                    return g
                return None

            # For each wheel residue r, the candidate prime is m*D + r
            # We check if base_point (= m*D*Q) and baby[r] (= r*Q) give a factor
            # The value to accumulate: X(m*D*Q) * Z(r*Q) - X(r*Q) * Z(m*D*Q)
            for r in WHEEL_RESIDUES:
                candidate = m * D_WHEEL + r
                if candidate <= B1 or candidate > B2:
                    continue
                bx, bz = baby[r]
                diff_val = (base_x * bz - bx * base_z) % n
                product = product * diff_val % n

            giant_count += 1

            # Batch GCD every 100 giant steps
            if giant_count % 100 == 0:
                g = math.gcd(product, n)
                if 1 < g < n:
                    return g
                if g == n:
                    # Accumulated too much — lost the factor. Try narrowing.
                    product = 1

            # Giant step: advance base by D*Q using differential addition
            new_x, new_z = mont_add(base_x, base_z, dqx, dqz,
                                    prev_base_x, prev_base_z, n)
            prev_base_x, prev_base_z = base_x, base_z
            base_x, base_z = new_x, new_z

        # Final GCD
        if product != 1:
            g = math.gcd(product, n)
            if 1 < g < n:
                return g

    return None

# ============================================================
# Pollard Rho (Brent variant, batched GCD)
# ============================================================
def pollard_rho(n, time_limit=30):
    """Brent's improvement of Pollard rho with batch GCD."""
    if n % 2 == 0: return 2
    start = time.time()
    for attempt in range(50):
        if time.time() - start > time_limit:
            return None
        y = random.randint(1, n - 1)
        c = random.randint(1, n - 1)
        m = 256
        g, q, r = 1, 1, 1
        x = y
        while g == 1:
            if time.time() - start > time_limit:
                return None
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
            if r > 50_000_000:
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
# Multi-group resonance: p-1 (bases 2,3,5,7) + p+1 (seeds 3,5,7)
# ============================================================
def multi_resonance(n, primes, B=2_000_000, time_limit=10):
    """
    Combined p-1 (4 bases) + p+1 (3 seeds) for quick factor detection.
    Catches primes p where p-1 or p+1 is B-smooth.
    """
    start = time.time()
    # p-1 bases
    a = [2, 3, 5, 7]
    # p+1 seeds (Lucas sequences)
    v = [3, 5, 7]

    product = 1
    for idx, p in enumerate(primes):
        if p > B:
            break
        if time.time() - start > time_limit:
            break
        pk = p
        while pk <= B:
            # p-1: a_i = a_i^p mod n
            for i in range(4):
                a[i] = pow(a[i], p, n)
            # p+1: Lucas V sequence: V_{kp} from V_k
            # V_{mn} uses: V_m(V_n) where V_m(x) is Chebyshev-like
            # V_{kp}(P) = V_p(V_k(P)), and V_p(x) = pow(x, p) mod n (for Lucas)
            # Actually for p+1: we use V_k where V_{i+1} = P*V_i - V_{i-1}
            # Scalar mult in Lucas: V_{2k} = V_k^2 - 2, V_{2k+1} = V_k*V_{k+1} - P
            for i in range(3):
                v[i] = lucas_chain(v[i], p, n)
            pk *= p

        # Periodic GCD check
        if idx % 2000 == 0 and idx > 0:
            product = 1
            for ai in a:
                product = product * (ai - 1) % n
            for vi in v:
                product = product * (vi - 2) % n
            g = math.gcd(product, n)
            if 1 < g < n:
                return g
            if g == n:
                # Try individual
                for ai in a:
                    g = math.gcd(ai - 1, n)
                    if 1 < g < n: return g
                for vi in v:
                    g = math.gcd(vi - 2, n)
                    if 1 < g < n: return g

    # Final check
    product = 1
    for ai in a:
        product = product * (ai - 1) % n
    for vi in v:
        product = product * (vi - 2) % n
    g = math.gcd(product, n)
    if 1 < g < n:
        return g
    if g == n:
        for ai in a:
            g = math.gcd(ai - 1, n)
            if 1 < g < n: return g
        for vi in v:
            g = math.gcd(vi - 2, n)
            if 1 < g < n: return g
    return None

def lucas_chain(v_val, k, n):
    """Compute V_k(v_val) mod n using the Lucas chain (binary method).
    V_0 = 2, V_1 = v_val, V_{i+1} = v_val * V_i - V_{i-1}.
    This computes the k-th term of V starting from V_1 = v_val."""
    if k == 0: return 2
    if k == 1: return v_val
    # Binary Lucas chain
    vl = v_val  # V_1
    vh = (v_val * v_val - 2) % n  # V_2
    bits = bin(k)[3:]  # skip '0b1'
    for bit in bits:
        if bit == '0':
            vh = (vl * vh - v_val) % n  # V_{2m+1} = V_m * V_{m+1} - P
            vl = (vl * vl - 2) % n       # V_{2m} = V_m^2 - 2
        else:
            vl = (vl * vh - v_val) % n   # V_{2m+1} = V_m * V_{m+1} - P
            vh = (vh * vh - 2) % n        # V_{2m+2} = V_{m+1}^2 - 2
    return vl

# ============================================================
# Master factoring function
# ============================================================
def factor_master(n, total_budget=600, primes=None):
    """
    Multi-phase factoring:
    1. Trial division (tiny factors)
    2. Pollard rho (30s budget)
    3. Multi-group resonance p-1/p+1 (10s budget)
    4. ECM with Suyama + Stage 2 BSGS (remaining budget)
    """
    start = time.time()
    remaining = lambda: total_budget - (time.time() - start)
    bits = n.bit_length()

    # Phase 0: trial division
    for p in primes[:10000]:
        if n % p == 0:
            return p

    # Phase 1: Pollard rho (30s)
    rho_budget = min(30, remaining() * 0.1)
    log(f"  Phase 1: Pollard rho ({rho_budget:.0f}s budget)...")
    t = time.time()
    r = pollard_rho(n, time_limit=rho_budget)
    if r and 1 < r < n and n % r == 0:
        log(f"    -> Rho SUCCESS {time.time()-t:.3f}s -> {r}")
        return r
    log(f"    -> Rho: no factor ({time.time()-t:.1f}s)")

    if remaining() < 5:
        return None

    # Phase 2: Multi-group resonance (10s)
    res_budget = min(10, remaining() * 0.05)
    log(f"  Phase 2: Multi-group resonance ({res_budget:.0f}s budget)...")
    t = time.time()
    r = multi_resonance(n, primes, B=2_000_000, time_limit=res_budget)
    if r and 1 < r < n and n % r == 0:
        log(f"    -> Resonance SUCCESS {time.time()-t:.3f}s -> {r}")
        return r
    log(f"    -> Resonance: no factor ({time.time()-t:.1f}s)")

    if remaining() < 10:
        return None

    # Phase 3: ECM — the main event
    # Optimal parameters from GMP-ECM research
    # Factor size estimate: bits/2 (balanced semiprime)
    factor_bits = bits // 2
    if factor_bits <= 40:
        B1, B2, curves = 100_000, 10_000_000, 50
    elif factor_bits <= 50:
        B1, B2, curves = 250_000, 25_000_000, 100
    elif factor_bits <= 55:
        B1, B2, curves = 500_000, 50_000_000, 150
    elif factor_bits <= 65:
        B1, B2, curves = 1_000_000, 100_000_000, 200
    elif factor_bits <= 70:
        B1, B2, curves = 1_000_000, 100_000_000, 200
    elif factor_bits <= 80:
        B1, B2, curves = 3_000_000, 300_000_000, 500
    elif factor_bits <= 90:
        B1, B2, curves = 3_000_000, 300_000_000, 500
    elif factor_bits <= 100:
        B1, B2, curves = 11_000_000, 1_100_000_000, 1000
    else:
        B1, B2, curves = 11_000_000, 1_100_000_000, 2000

    ecm_budget = remaining()
    log(f"  Phase 3: ECM (B1={B1:,}, B2={B2:,}, up to {curves} curves, {ecm_budget:.0f}s)...")
    log(f"    Target factor size: ~{factor_bits} bits")
    t = time.time()

    # Run ECM in stages: try smaller B1 first for quick wins, then ramp up
    # Stage A: quick scan with smaller B1
    if factor_bits >= 70 and ecm_budget > 60:
        quick_B1 = B1 // 10
        quick_B2 = B2 // 10
        quick_curves = min(50, curves)
        quick_budget = min(ecm_budget * 0.15, 60)
        log(f"    Quick scan: B1={quick_B1:,}, B2={quick_B2:,}, {quick_curves} curves, {quick_budget:.0f}s...")
        r = ecm_suyama(n, quick_B1, quick_B2, quick_curves, primes, time_limit=quick_budget)
        if r and 1 < r < n and n % r == 0:
            log(f"    -> ECM quick scan SUCCESS {time.time()-t:.3f}s -> {r}")
            return r
        log(f"    Quick scan: no factor ({time.time()-t:.1f}s)")

    ecm_budget = remaining()
    if ecm_budget < 10:
        return None

    log(f"    Full ECM: B1={B1:,}, B2={B2:,}, {curves} curves, {ecm_budget:.0f}s...")
    t2 = time.time()
    r = ecm_suyama(n, B1, B2, curves, primes, time_limit=ecm_budget)
    if r and 1 < r < n and n % r == 0:
        log(f"    -> ECM SUCCESS {time.time()-t2:.3f}s (total {time.time()-t:.3f}s)")
        return r
    log(f"    -> ECM: no factor ({time.time()-t:.1f}s total)")

    return None

# ============================================================
# Main: generate test cases, run factoring
# ============================================================
def main():
    random.seed(77777)

    log("\n\n---\n")
    log("## Round 11: ECM Maximum Push (180-200 bit target)\n")
    log(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log("")
    log("Improvements: Suyama parameterization, Montgomery ladder,")
    log("Stage 2 BSGS with wheel D=2310, proper giant step differential")
    log("addition, batch GCD, multi-group resonance pre-pass.")
    log("")

    # Sieve primes up to 11M
    log("Sieving primes up to 11,000,000...")
    t0 = time.time()
    PRIMES = sieve_primes(11_000_000)
    log(f"Sieved {len(PRIMES):,} primes up to {PRIMES[-1]:,} in {time.time()-t0:.1f}s")
    log("")

    # Generate test semiprimes
    test_cases = []
    for bits in [100, 128, 140, 160, 180, 200]:
        p, q, n = gen_semiprime(bits)
        test_cases.append((bits, p, q, n))

    log("### Test Semiprimes\n")
    for bits, p, q, n in test_cases:
        log(f"- **{bits}-bit**: n = {n}")
        log(f"  p = {p} ({p.bit_length()} bits)")
        log(f"  q = {q} ({q.bit_length()} bits)")
    log("")

    # Time budgets
    TIME_LIMITS = {
        100: 60,
        128: 120,
        140: 180,
        160: 300,
        180: 600,
        200: 900,
    }

    log("### Factoring Results\n")

    results = {}
    for bits, p, q, n in test_cases:
        budget = TIME_LIMITS[bits]
        log(f"\n#### {bits}-bit semiprime (budget: {budget}s)\n")

        t_start = time.time()
        result = factor_master(n, total_budget=budget, primes=PRIMES)
        elapsed = time.time() - t_start

        if result and n % result == 0 and 1 < result < n:
            other = n // result
            log(f"\n  **SUCCESS** in {elapsed:.3f}s")
            log(f"  Factor: {result}")
            log(f"  Verify: {result} x {other} = {n} ({'OK' if result * other == n else 'MISMATCH'})")
            results[bits] = ("SUCCESS", elapsed)
        else:
            log(f"\n  **FAILED** after {elapsed:.1f}s")
            results[bits] = ("FAILED", elapsed)
        log("")

    # Summary
    log("\n### Round 11 Summary\n")
    log("| Bits | Result  | Time     |")
    log("|------|---------|----------|")
    for bits in [100, 128, 140, 160, 180, 200]:
        if bits in results:
            status, elapsed = results[bits]
            if status == "SUCCESS":
                log(f"| {bits}  | SUCCESS | {elapsed:.1f}s |")
            else:
                log(f"| {bits}  | FAILED  | {elapsed:.1f}s |")
    log("")
    log("Previous record: 160-bit (ECM, 164s, round 8).")
    best_success = max((b for b in results if results[b][0] == "SUCCESS"), default=0)
    if best_success:
        log(f"New record: {best_success}-bit (ECM, {results[best_success][1]:.1f}s).")
    else:
        log("No new record set.")
    log("")

if __name__ == "__main__":
    main()
