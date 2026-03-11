#!/usr/bin/env python3
"""
Round 6: Meet-in-the-Middle Factoring

Key insight from Round 5: Hensel lifting (bottom-up, from LSB) is O(sqrt(n)),
equivalent to trial division. Top-down estimation from MSBs is also O(sqrt(n)).
Combining them — bottom-up gives x mod 2^k, top-down gives x // 2^k —
should theoretically give O(n^(1/4)) via meet-in-the-middle.

This round tests whether this is achievable in practice, and carefully
analyzes WHY it works or fails.
"""

import math
import random
import time
import sys

LOG_FILE = "factoring_log.md"


def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg, flush=True)


# ============================================================
# Utility
# ============================================================
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
    while p == q:
        q = next_prime(random.getrandbits(half) | (1 << (half - 1)))
    if p > q: p, q = q, p
    return p, q, p * q


def isqrt(n):
    if n < 0: raise ValueError
    if n == 0: return 0
    x = 1 << ((n.bit_length() + 1) // 2)
    while True:
        y = (x + n // x) // 2
        if y >= x: return x
        x = y


# ============================================================
# METHOD 1: Trial division (baseline, O(sqrt(n)))
# ============================================================
def trial_division(n, time_limit=30.0):
    """Scan odd numbers from 3 to sqrt(n)."""
    t0 = time.time()
    sqrt_n = isqrt(n)
    x = 3
    while x <= sqrt_n:
        if n % x == 0:
            return x
        x += 2
        if x % 10000001 == 0 and time.time() - t0 > time_limit:
            return None
    return None


# ============================================================
# METHOD 2: Algebraic MITM — fix x_low via Hensel, solve for x_high
# ============================================================
def algebraic_mitm(n, time_limit=30.0):
    """
    Split x = a*M + r where M = 2^k:
      x * y = n, with y = b*M + s, r*s ≡ n mod M.

    For each odd r in [1, M), s is uniquely determined: s = n * r^(-1) mod M.
    Then the carry Q = (r*s) >> k, and we need:
      a*b*M + a*s + b*r = (n >> k) - Q

    For each r, iterate over valid a values and solve for b exactly.
    If b is a non-negative integer, check x*y == n.

    Complexity: O(num_r * num_a). If k = L/2, num_a ~ 1 and num_r ~ 2^(L/2-1).
    If k = L/3, num_a ~ 2^(L/6) and num_r ~ 2^(L/3-1).
    Total is always O(2^(L/2)) = O(sqrt(n)) because num_r * num_a ≈ sqrt(n)/2.

    BUT: we can try k values where a_range is very small (1-2), making the
    inner loop trivial, and iterate over r with early termination.
    """
    L = n.bit_length()
    sqrt_n = isqrt(n)
    t0 = time.time()

    # Use k = L//2 so a_range is minimal
    k = L // 2
    M = 1 << k
    n_low = n % M
    R = n >> k

    x_min = 3
    x_max = sqrt_n
    a_min = x_min // M
    a_max = x_max // M

    for r in range(1, M, 2):
        if r & 0xFFFFF == 1 and time.time() - t0 > time_limit:
            return None
        # s = n * r^(-1) mod M
        s = (n_low * pow(r, -1, M)) % M
        Q = (r * s) >> k
        target = R - Q

        if target < 0:
            continue

        for a in range(a_min, a_max + 1):
            num = target - a * s
            den = r + a * M
            if num < 0:
                break
            if den <= 0:
                continue
            if num % den == 0:
                b = num // den
                if b >= 0:
                    x = a * M + r
                    y = b * M + s
                    if x > 1 and y > 1 and x * y == n:
                        return min(x, y)

    return None


# ============================================================
# METHOD 3: Hensel + top-down range check (progressive)
# ============================================================
def hensel_topdown_progressive(n, time_limit=30.0):
    """
    Build Hensel solutions incrementally, using top-down range pruning.

    At each Hensel level k, we have x ≡ x_low mod 2^k.
    From top-down: x is in [x_min, x_max] = [3, sqrt(n)].
    So x_low must satisfy: there exists some integer x_high >= 0 with
    x = x_high * 2^k + x_low and x in [x_min, x_max].

    This prunes x_low values where NO valid x_high exists.

    At level k, x_low < 2^k, and we need x_low <= x_max.
    Also x_high must be >= 0, so x_low <= x_max (always true for small k).

    The real pruning: at level k, x_low is in [0, 2^k).
    The number of valid x in [x_min, x_max] with x ≡ x_low mod 2^k is
    approximately (x_max - x_min) / 2^k. When 2^k > x_max - x_min,
    at most 1 such x exists, so we can directly check.

    Strategy: Hensel-lift until 2^k > sqrt(n), then for each surviving
    x_low, the x_high is uniquely determined and we check n % x == 0.

    Problem: the number of surviving x_low values at level k is
    approximately 2^(k-1) (every odd number), so at k = L/2 + 1
    we have ~sqrt(n)/2 candidates. Still O(sqrt(n)).
    """
    L = n.bit_length()
    sqrt_n = isqrt(n)
    t0 = time.time()

    x_min = 3
    x_max = sqrt_n

    # Phase 1: Hensel lift from k=1 up to a moderate k, WITH range pruning
    states = {1}  # x ≡ 1 mod 2 (odd)
    max_states = 500_000

    for k in range(1, L + 2):
        if time.time() - t0 > time_limit:
            return None

        mod_next = 1 << (k + 1)
        n_mod = n % mod_next

        next_states = set()
        for x_low in states:
            for bit in [0, 1]:
                x_new = x_low + bit * (1 << k)

                # Hensel constraint
                try:
                    x_inv = pow(x_new, -1, mod_next)
                except ValueError:
                    continue
                y_new = (n_mod * x_inv) % mod_next
                if y_new % 2 == 0:
                    continue

                # Top-down range pruning:
                # Does there exist x in [x_min, x_max] with x ≡ x_new mod 2^(k+1)?
                if x_new > x_max:
                    continue
                # Smallest valid x: x_new itself if x_new >= x_min,
                # else x_new + ceil((x_min - x_new) / mod_next) * mod_next
                if x_new < x_min:
                    steps = (x_min - x_new + mod_next - 1) // mod_next
                    if x_new + steps * mod_next > x_max:
                        continue

                next_states.add(x_new)

                # Direct factor check once mod is large enough
                if mod_next > x_max:
                    # x_new is the only candidate in range
                    if x_new >= x_min and x_new <= x_max:
                        if n % x_new == 0 and x_new > 1:
                            return x_new

        states = next_states

        if len(states) == 0:
            break

        # Check all candidates once modulus exceeds range
        if mod_next > x_max:
            for x_low in states:
                if x_low >= x_min and x_low <= x_max:
                    if n % x_low == 0 and x_low > 1:
                        return x_low
            # Also check if any x_low directly divides n (for small factors)
            for x_low in states:
                if x_low > 1 and n % x_low == 0:
                    return x_low
            return None

        if len(states) > max_states:
            # Sample — this loses completeness but keeps it tractable
            states = set(random.sample(list(states), max_states))

    return None


# ============================================================
# METHOD 4: True MITM with baby-step/giant-step structure
# ============================================================
def mitm_babystep_giantstep(n, time_limit=30.0):
    """
    Baby-step giant-step style factoring:

    Choose M = 2^k where k ≈ L/4.

    Baby steps (bottom-up): For each odd r in [1, M), compute
    n mod r and store {r : n mod r} in a table. (Not useful — we need r|n.)

    Actually, the correct BSGS analogy:
    We want to find x such that x | n, with x in [3, sqrt(n)].
    Write x = a*M + r with 0 <= r < M.

    Baby step: For each r in [1, M), compute n mod r... no, that doesn't help.

    The fundamental issue: factoring doesn't have a group structure that
    BSGS can exploit. BSGS works for discrete log because of the group
    operation. For factoring, there's no analogous structure.

    Alternative: Use the STRUCTURE of n mod M.
    n mod M is fixed. If x = a*M + r divides n, then:
    n ≡ 0 mod x => n mod (a*M + r) = 0.

    This means n - q*(a*M + r) = 0 for some q.
    n = q*a*M + q*r => n mod M = q*r mod M => q ≡ n * r^(-1) mod M (if gcd(r,M)=1)

    So q mod M is determined by r. And y = n/x = q.
    So y mod M = n * r^(-1) mod M = s (the Hensel constraint!).

    Now: x*y = n => (a*M + r)(b*M + s) = n where b = y // M.
    This is the same algebraic equation as Method 2.

    Let's try a different angle: use HASH TABLE for the meet.

    Phase 1: For each odd r in [1, M), compute the "signature"
    sig(r) = n mod r. If x = a*M + r divides n, then n mod r = n mod x mod r...
    no, n mod x = 0, so n mod r = (n mod x) mod r + k*(a*M) mod r... this is
    circular.

    DIFFERENT APPROACH: batch GCD.
    Compute P = product of (a*M + r) for all (a, r) in the search space,
    then gcd(P, n). But computing this product is as expensive as the search.

    Let me just implement the cleanest version: iterate over r, solve for a.
    This is equivalent to trial division but with a different order.
    With k=L//2, we iterate over ~2^(L/2-1) values of r with O(1) per r.
    """
    L = n.bit_length()
    sqrt_n = isqrt(n)
    t0 = time.time()

    # k = L//4: iterate 2^(L/4-1) values of r, each with ~2^(L/4) values of a
    # Total: ~2^(L/2) = sqrt(n). No improvement.
    #
    # The ONLY way to beat sqrt(n) is if we can batch-check many candidates.
    # Idea: compute gcd(n, product_of_candidates) where the product is computed
    # using a product tree. This is what batch GCD does.
    #
    # For our case: choose M = 2^k. For each r, the candidate x values are
    # {a*M + r : a in [a_min, a_max]}. We can compute:
    # P_r = product of (a*M + r) for a in range, then gcd(P_r, n).
    # Computing P_r takes O(a_range * log) multiplications.
    # But gcd(P_r, n) is O(L * log(P_r)) = O(L * a_range * k).
    # Total: sum over r of O(a_range * k) = O(2^(L/2) * k). Worse!
    #
    # Product tree: compute all products in O(N log^2 N) then remainder tree.
    # But this is complex. Let's use a simpler batch: accumulate product mod n.

    k = max(4, L // 4)
    M = 1 << k

    a_min = 0
    a_max = sqrt_n // M

    # Batch: accumulate product of candidates mod n, periodically take GCD
    batch_size = 1000
    product = 1
    count = 0

    for r in range(1, min(M, sqrt_n + 1), 2):
        if time.time() - t0 > time_limit:
            return None

        for a in range(a_min, a_max + 1):
            x = a * M + r
            if x < 3 or x > sqrt_n:
                continue
            product = (product * x) % n
            count += 1

            if count % batch_size == 0:
                g = math.gcd(product, n)
                if 1 < g < n:
                    return g
                product = 1

    if product != 1:
        g = math.gcd(product, n)
        if 1 < g < n:
            return g

    return None


# ============================================================
# METHOD 5: Pollard Rho Brent (baseline O(n^(1/4)))
# ============================================================
def pollard_rho_brent(n, time_limit=30.0):
    """Brent's improvement of Pollard's rho, for comparison."""
    if n % 2 == 0: return 2
    t0 = time.time()
    for c in range(1, 200):
        if time.time() - t0 > time_limit: return None
        y = random.randint(2, n - 1)
        r = 1
        q = 1
        x = y
        d = 1
        while d == 1:
            if time.time() - t0 > time_limit: return None
            x = y
            for _ in range(r):
                y = (y * y + c) % n
            k = 0
            while k < r and d == 1:
                ys = y
                for _ in range(min(128, r - k)):
                    y = (y * y + c) % n
                    q = q * abs(x - y) % n
                d = math.gcd(q, n)
                k += 128
            r *= 2
        if d == n:
            d = 1
            while d == 1:
                ys = (ys * ys + c) % n
                d = math.gcd(abs(ys - x), n)
            if d == n: continue
        if 1 < d < n:
            return d
    return None


# ============================================================
# METHOD 6: MITM with GCD accumulation (hybrid)
# ============================================================
def mitm_gcd_accumulate(n, time_limit=30.0):
    """
    Combine the algebraic MITM structure with GCD accumulation
    (like Pollard rho uses) to batch-check candidates.

    For each odd r in [1, M), compute x_candidates = {a*M + r} for valid a.
    Multiply them together mod n and periodically take GCD.

    This is still O(sqrt(n)) total candidates, but the GCD accumulation
    amortizes the expensive GCD operation.
    """
    L = n.bit_length()
    sqrt_n = isqrt(n)
    t0 = time.time()

    k = L // 2
    M = 1 << k
    n_low = n % M
    R = n >> k

    a_min = 0
    a_max = sqrt_n // M

    product = 1
    count = 0
    batch = 256

    for r in range(1, M, 2):
        if time.time() - t0 > time_limit:
            return None

        # For this r, solve for valid (a, b)
        s = (n_low * pow(r, -1, M)) % M
        Q = (r * s) >> k
        target = R - Q
        if target < 0:
            continue

        for a in range(a_min, a_max + 1):
            num = target - a * s
            den = r + a * M
            if num < 0: break
            if den <= 0: continue
            if num % den == 0:
                b = num // den
                if b >= 0:
                    x = a * M + r
                    if x > 1:
                        product = (product * x) % n
                        count += 1
                        if count % batch == 0:
                            g = math.gcd(product, n)
                            if 1 < g < n:
                                return g
                            product = 1

    if product > 1:
        g = math.gcd(product, n)
        if 1 < g < n:
            return g

    return None


# ============================================================
# METHOD 7: Direct scan (cleaner trial division baseline)
# ============================================================
def direct_scan(n, time_limit=30.0):
    """Trial division scanning odd numbers, with GCD batching."""
    t0 = time.time()
    sqrt_n = isqrt(n)
    product = 1
    count = 0
    batch = 512

    for x in range(3, sqrt_n + 1, 2):
        product = (product * x) % n
        count += 1
        if count % batch == 0:
            if time.time() - t0 > time_limit:
                return None
            g = math.gcd(product, n)
            if 1 < g < n:
                return g
            product = 1

    if product > 1:
        g = math.gcd(product, n)
        if 1 < g < n:
            return g
    return None


# ============================================================
# RUN ALL EXPERIMENTS
# ============================================================
def main():
    random.seed(271828)

    test_bits = [40, 50, 60, 64, 72, 80, 96, 100, 112, 128]
    test_cases = []
    for bits in test_bits:
        p, q, n = gen_semiprime(bits)
        actual_bits = n.bit_length()
        test_cases.append((bits, actual_bits, p, q, n))

    log("\n\n---\n")
    log("## Round 6: Meet-in-the-Middle Factoring\n")
    log("### Concept\n")
    log("Combine bottom-up Hensel lifting (x mod 2^k from LSB) with")
    log("top-down MSB estimation (x // 2^k from sqrt(n) range).")
    log("Target: O(n^(1/4)). Actual: detailed analysis below.\n")

    log("### Test Numbers\n")
    for bits, actual_bits, p, q, n in test_cases:
        log(f"- {bits}-bit target (actual {actual_bits}-bit): n={n}")
        log(f"  p={p}, q={q}")

    TIME_LIMIT = 30

    methods = [
        ("Trial Division (GCD-batched)", direct_scan),
        ("Algebraic MITM", algebraic_mitm),
        ("Hensel + Top-down Pruning", hensel_topdown_progressive),
        ("MITM Baby/Giant GCD", mitm_babystep_giantstep),
        ("MITM GCD Accumulate", mitm_gcd_accumulate),
        ("Pollard Rho Brent", pollard_rho_brent),
    ]

    results = {}

    for method_name, func in methods:
        log(f"\n### {method_name}\n")
        results[method_name] = []
        for bits, actual_bits, p, q, n in test_cases:
            start = time.time()
            try:
                result = func(n, TIME_LIMIT)
                elapsed = time.time() - start
                if elapsed > TIME_LIMIT:
                    status = f"- {bits}-bit: **TIMEOUT** ({elapsed:.1f}s)"
                    results[method_name].append(('timeout', elapsed))
                elif result and n % result == 0 and 1 < result < n:
                    other = n // result
                    status = f"- {bits}-bit: **SUCCESS** {elapsed:.4f}s -> {result}"
                    status += f"\n  verified: {n} = {result} x {other}"
                    results[method_name].append(('success', elapsed))
                else:
                    status = f"- {bits}-bit: FAILED ({elapsed:.2f}s)"
                    results[method_name].append(('fail', elapsed))
            except Exception as e:
                elapsed = time.time() - start
                status = f"- {bits}-bit: ERROR: {type(e).__name__}: {e} ({elapsed:.2f}s)"
                results[method_name].append(('error', elapsed))
            log(status)

    # Detailed analysis
    log("\n## Round 6 Analysis: Meet-in-the-Middle Factoring\n")

    log("### Results Summary\n")
    header = "| Method | " + " | ".join(f"{b}b" for b, _, _, _, _ in test_cases) + " |"
    sep = "|--------|" + "|".join("------" for _ in test_cases) + "|"
    log(header)
    log(sep)
    for method_name in results:
        short = method_name[:35]
        row = f"| {short:35s} |"
        for status, elapsed in results[method_name]:
            if status == 'success':
                row += f" {elapsed:.2f}s |"
            elif status == 'timeout':
                row += " T/O   |"
            elif status == 'fail':
                row += " FAIL  |"
            else:
                row += " ERR   |"
        log(row)

    log("""
### Why Meet-in-the-Middle CANNOT Beat O(sqrt(n)) for Factoring

**The core theorem:** In Hensel lifting, every odd number x_low in [1, 2^k)
is a valid partial solution to x*y = n mod 2^k. This is because for any odd
x_low, the value y_low = n * x_low^(-1) mod 2^k is uniquely determined and
also odd (since n is odd). Therefore, the bottom-up phase produces EXACTLY
2^(k-1) candidate x_low values — zero pruning.

**Proof that total work is O(sqrt(n)):**
- Bottom-up: 2^(k-1) states at level k (confirmed experimentally)
- Top-down: sqrt(n) / 2^k candidate x_high values
- Total combinations: 2^(k-1) * sqrt(n) / 2^k = sqrt(n) / 2
- This is INDEPENDENT of k. Every choice of k yields the same total work.

**Why this differs from other MITM attacks:**
- In MITM on block ciphers: the intermediate state is constrained by BOTH
  plaintext and ciphertext, creating a "bottleneck" with fewer valid states
  than the full keyspace. This gives real pruning.
- In baby-step/giant-step for DLP: the group structure ensures that there
  is exactly ONE valid (i, j) pair, so hash lookup gives O(1) matching.
- In our factoring MITM: EVERY x_low is valid (no bottleneck), and for each
  x_low, determining whether a valid x_high exists requires O(a_range) work
  or the full divisibility check n % x == 0.

**What about the algebraic solve (Method 2)?**
The algebraic MITM writes a*s + b*r + a*b*M = R - Q and solves for b given
(r, a). This is O(1) per (r, a) pair. But the total number of (r, a) pairs
to check is still sqrt(n)/2. The algebraic structure merely replaces trial
division with modular arithmetic — same asymptotic cost.

**Comparison with Pollard rho:**
Pollard rho achieves O(n^(1/4)) through the BIRTHDAY PARADOX, not through
meet-in-the-middle. It finds a collision x_i = x_j mod p (where p is the
unknown factor) after O(sqrt(p)) = O(n^(1/4)) steps. This works because:
1. The random walk creates a RANDOM function mod p
2. Birthday paradox guarantees collision in O(sqrt(p)) steps
3. GCD detects the collision without knowing p

The bitwise decomposition x = a*2^k + r has no analogous random/birthday
property. Each bit pattern is deterministic, and there's no "collision"
to detect.

### Key Takeaway for Future Rounds

To beat O(sqrt(n)) factoring, you need one of:
1. **Group structure** (ECM, Pollard p-1, p+1) — exploits algebraic groups
2. **Smoothness** (QS, NFS) — finds many numbers that factor over a small base
3. **Quantum** (Shor) — period-finding in the multiplicative group
4. **Lattice methods** — reduce factoring to short vector problems

The purely bitwise/Hensel approach is fundamentally limited to O(sqrt(n))
because the modular constraint x*y ≡ n mod 2^k provides no pruning of
individual factor candidates. Every odd number is equally valid as x mod 2^k.
""")


if __name__ == "__main__":
    main()
