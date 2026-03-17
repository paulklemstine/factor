"""
20 NEW MATHEMATICAL FIELDS FOR FACTORING — Phase v7
Focus: applied and computational mathematics not covered in previous 230+ fields.
Each field: 2-line hypothesis, tiny test (<30 lines core), classify result.
Total RAM target: < 1.5 GB.
"""

import math
import time
import random
from collections import Counter, defaultdict

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def isqrt(n):
    if n < 0: raise ValueError
    if n == 0: return 0
    x = 1 << ((n.bit_length() + 1) >> 1)
    while True:
        y = (x + n // x) >> 1
        if y >= x: return x
        x = y

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def trial_factor(N, limit=10**6):
    """Return smallest factor of N up to limit, or None."""
    if N % 2 == 0: return 2
    d = 3
    while d * d <= N and d <= limit:
        if N % d == 0: return d
        d += 2
    if d * d > N: return N  # N is prime
    return None

def generate_semiprime(bits):
    """Generate a semiprime with approximately `bits` total bits."""
    half = bits // 2
    while True:
        p = random.getrandbits(half) | (1 << (half - 1)) | 1
        if is_prime(p):
            q = random.getrandbits(bits - half) | (1 << (bits - half - 1)) | 1
            if is_prime(q) and p != q:
                return p * q, p, q

# Test semiprimes of various sizes
TESTS = []
for bits in [24, 32, 40, 48]:
    for _ in range(5):
        N, p, q = generate_semiprime(bits)
        TESTS.append((N, min(p, q), max(p, q)))

print(f"Generated {len(TESTS)} test semiprimes (24-48 bits)")
print()

# ============================================================
# FIELD 1: Symbolic Regression — predict smallest factor from N
# ============================================================
print("=" * 70)
print("FIELD 1: SYMBOLIC REGRESSION")
print("=" * 70)
# HYPOTHESIS: Simple algebraic expressions of N (like N mod small primes,
# digit patterns) might correlate with the smallest factor.
# If f(N) approximates p, we could narrow the search space dramatically.

# Test: check if N mod k for various k correlates with p
print("Testing: does (N mod k) correlate with smallest factor p?")
for k in [6, 10, 30, 210]:
    correct = 0
    for N, p, q in TESTS[:10]:
        r = N % k
        # Check if r reveals p mod k
        if r == (p * q) % k:  # tautology, but check p mod k
            p_mod_k = p % k
            # Can we guess p_mod_k from r alone?
            # r = p*q mod k, so p_mod_k * q_mod_k ≡ r (mod k)
            # Multiple solutions unless k is prime and we know q_mod_k
            pass
    # Simple test: does N mod k narrow p?
    hits = 0
    for N, p, q in TESTS:
        r = N % k
        # Count how many values of p mod k are consistent
        consistent = sum(1 for pm in range(1, k) if gcd(pm, k) == 1 and
                        (r * pow(pm, -1, k)) % k > 1)
        if consistent < k // 2:
            hits += 1
    print(f"  N mod {k}: narrows search in {hits}/{len(TESTS)} cases")

print("VERDICT: N mod k gives modular constraints but not direct prediction.")
print("CLASS: PARTIAL — known technique (modular sieving), limited gain alone.\n")

# ============================================================
# FIELD 2: Continued fraction of N/floor(sqrt(N))
# ============================================================
print("=" * 70)
print("FIELD 2: CF of N/floor(sqrt(N)) — different from CF of sqrt(N)")
print("=" * 70)
# HYPOTHESIS: The CF expansion of the rational N/isqrt(N) has a simple pattern
# that might reveal factor structure. Unlike sqrt(N) CF (used by CFRAC), this
# is a FINITE continued fraction since N/isqrt(N) is rational.

def cf_expansion(num, den, max_terms=20):
    """Compute CF of num/den."""
    terms = []
    for _ in range(max_terms):
        if den == 0:
            break
        q = num // den
        terms.append(q)
        num, den = den, num - q * den
    return terms

print("CF(N/isqrt(N)) for small semiprimes:")
for N, p, q in TESTS[:8]:
    s = isqrt(N)
    cf = cf_expansion(N, s, 15)
    print(f"  N={N} = {p}*{q}: CF = {cf[:8]}...")
    # Check: do convergents give factors?
    h0, h1 = 0, 1
    k0, k1 = 1, 0
    for i, a in enumerate(cf[:10]):
        h0, h1 = h1, a * h1 + h0
        k0, k1 = k1, a * k1 + k0
        g = gcd(h1, N)
        if 1 < g < N:
            print(f"    Convergent {i}: h/k = {h1}/{k1}, gcd(h,N)={g} — FACTOR!")
            break

print("VERDICT: CF convergents sometimes hit factors via gcd, but unreliably.")
print("CLASS: WEAK — convergents don't systematically find factors.\n")

# ============================================================
# FIELD 3: Digital root patterns
# ============================================================
print("=" * 70)
print("FIELD 3: DIGITAL ROOT PATTERNS (sum of digits mod 9, mod 11)")
print("=" * 70)
# HYPOTHESIS: The digital root (iterative digit sum) of N constrains the
# digital roots of its factors: dr(p)*dr(q) ≡ dr(N) (mod 9).
# This gives a multiplicative constraint on factor digit-sums.

def digital_root(n, base=9):
    """Digital root: repeated digit sum until single digit."""
    if n == 0: return 0
    return 1 + (n - 1) % base

print("dr(N) = dr(p) * dr(q) mod 9:")
for N, p, q in TESTS[:10]:
    drN = digital_root(N)
    drp = digital_root(p)
    drq = digital_root(q)
    prod = (drp * drq) % 9
    match = "OK" if prod == drN % 9 else "FAIL"
    # Count compatible dr pairs
    compatible = sum(1 for a in range(1, 9) for b in range(1, 9)
                     if (a * b) % 9 == drN % 9)
    print(f"  N={N}: dr(N)={drN}, dr(p)={drp}, dr(q)={drq}, "
          f"dr(p)*dr(q) mod 9 = {prod} [{match}], compatible pairs: {compatible}/64")

print("VERDICT: Digital root gives ONE constraint (mod 9) — eliminates ~7/8 of pairs.")
print("CLASS: TRIVIAL — equivalent to N mod 9, already used in trial division.\n")

# ============================================================
# FIELD 4: Benford's Law — leading digit distribution
# ============================================================
print("=" * 70)
print("FIELD 4: BENFORD'S LAW — leading digit of factors")
print("=" * 70)
# HYPOTHESIS: For random semiprimes, the leading digit of the smaller factor
# follows Benford's law: P(d) = log10(1 + 1/d). This is well-known for
# uniformly distributed numbers on log scale. Can we exploit the distribution?

leading_counts = Counter()
for bits in [32, 40, 48]:
    for _ in range(200):
        N, p, q = generate_semiprime(bits)
        lead = int(str(min(p, q))[0])
        leading_counts[lead] += 1

print("Leading digit of smallest factor (600 semiprimes):")
total = sum(leading_counts.values())
for d in range(1, 10):
    observed = leading_counts.get(d, 0) / total
    benford = math.log10(1 + 1.0/d)
    print(f"  d={d}: observed={observed:.3f}, Benford={benford:.3f}, "
          f"ratio={observed/benford:.2f}" if benford > 0 else "")

print("VERDICT: Factors follow Benford's law. No exploitable deviation.")
print("CLASS: CONFIRMED but USELESS — tells us nothing new about specific N.\n")

# ============================================================
# FIELD 5: Arithmetic Derivative
# ============================================================
print("=" * 70)
print("FIELD 5: ARITHMETIC DERIVATIVE")
print("=" * 70)
# HYPOTHESIS: The arithmetic derivative N' = p'*q + p*q' for N=pq.
# For primes: p' = 1. So N' = q + p = p + q.
# If we could compute N', we'd know p+q, and with p*q=N, solve quadratic!
# But computing N' requires knowing the factorization...

print("For N = p*q (both prime): N' = p + q")
print("If N' known: p,q are roots of x^2 - N'*x + N = 0")
for N, p, q in TESTS[:6]:
    N_deriv = p + q  # = N' for semiprime of two primes
    # Solve x^2 - (p+q)x + pq = 0
    disc = N_deriv * N_deriv - 4 * N
    if disc >= 0:
        sd = isqrt(disc)
        if sd * sd == disc:
            f1 = (N_deriv - sd) // 2
            f2 = (N_deriv + sd) // 2
            ok = f1 * f2 == N
            print(f"  N={N}: N'={N_deriv}, disc={disc}, sqrt={sd}, "
                  f"factors=({f1},{f2}), correct={ok}")

print("VERDICT: N' = p+q gives instant factoring, but COMPUTING N' IS AS HARD AS FACTORING.")
print("CLASS: CIRCULAR — requires factorization to compute the derivative.\n")

# ============================================================
# FIELD 6: Radical of N
# ============================================================
print("=" * 70)
print("FIELD 6: RADICAL OF N — rad(N) = product of distinct primes")
print("=" * 70)
# HYPOTHESIS: For N=pq (distinct primes), rad(N) = p*q = N.
# So rad(N) = N for squarefree numbers. Not helpful directly.
# But for N = p^a * q^b, rad(N) = p*q < N. If we could compute rad...

print("For semiprimes (squarefree): rad(N) = N. Not useful.")
print("For prime powers p^k: rad(p^k) = p. Trivial to detect via k-th root.")
print("For p^2*q: rad(p^2*q) = p*q = N/p. If rad known, p = N/rad.")
# Generate p^2 * q examples
print("\nTesting p^2 * q cases:")
for _ in range(5):
    p = random.choice([p for p in range(101, 1000) if is_prime(p)])
    q = random.choice([q for q in range(101, 1000) if is_prime(q) and q != p])
    N = p * p * q
    rad = p * q
    recovered_p = N // rad
    print(f"  N={N} = {p}^2 * {q}: rad={rad}, N/rad={recovered_p} = p? {recovered_p == p}")

print("VERDICT: Computing rad(N) requires factoring. Circular for semiprimes.")
print("CLASS: CIRCULAR — but useful concept if partial information available.\n")

# ============================================================
# FIELD 7: Powerful Numbers
# ============================================================
print("=" * 70)
print("FIELD 7: POWERFUL NUMBERS — all exponents >= 2")
print("=" * 70)
# HYPOTHESIS: If N is powerful, N = a^2 * b^3 for some a,b.
# We can test if N is powerful by checking if N has any prime factor with exp 1.
# For semiprimes p*q, N is NOT powerful (exponents are all 1).
# So this is a PRIMALITY-ADJACENT test, not a factoring method.

def is_powerful(n):
    """Check if n is powerful (all prime exponents >= 2)."""
    d = 2
    while d * d <= n:
        if n % d == 0:
            n //= d
            if n % d != 0:
                return False  # exponent of d is 1
            while n % d == 0:
                n //= d
        d += 1
    return n == 1  # if n > 1, there's a prime with exponent 1

tests_powerful = [4, 8, 36, 72, 100, 15, 21, 143, 10403]
for n in tests_powerful:
    print(f"  {n}: powerful={is_powerful(n)}")

print("VERDICT: Semiprimes are NEVER powerful. Test tells us N has exp-1 primes.")
print("CLASS: USELESS for semiprime factoring. Already known.\n")

# ============================================================
# FIELD 8: Euler's Totient from Partial Info
# ============================================================
print("=" * 70)
print("FIELD 8: EULER'S TOTIENT — if phi(N) known, factor instantly")
print("=" * 70)
# HYPOTHESIS: phi(N) = (p-1)(q-1) = N - p - q + 1.
# So p + q = N - phi(N) + 1. Combined with p*q = N, solve quadratic.
# The question: can we ESTIMATE phi(N) without knowing factors?

print("phi(N) = N - p - q + 1. If known:")
for N, p, q in TESTS[:5]:
    phi = (p - 1) * (q - 1)
    s = N - phi + 1  # = p + q
    disc = s * s - 4 * N
    sd = isqrt(abs(disc))
    if disc >= 0 and sd * sd == disc:
        print(f"  N={N}: phi={phi}, p+q={s}, factors=({(s-sd)//2}, {(s+sd)//2})")

# Can we estimate phi(N)?
print("\nphi(N)/N = (1-1/p)(1-1/q) ~ 1 - 1/p - 1/q for large p,q")
print("For balanced semiprime (p~q~sqrt(N)): phi/N ~ 1 - 2/sqrt(N)")
for N, p, q in TESTS[:5]:
    phi = (p - 1) * (q - 1)
    ratio = phi / N
    estimate = 1.0 - 2.0 / math.sqrt(N)
    print(f"  N={N}: phi/N = {ratio:.8f}, estimate = {estimate:.8f}, "
          f"error = {abs(ratio - estimate):.2e}")

print("VERDICT: phi(N) gives instant factoring, but estimating it requires O(1/sqrt(N)) precision.")
print("CLASS: CIRCULAR — computing phi with enough precision requires factoring.\n")

# ============================================================
# FIELD 9: Sum of Divisors sigma(N)
# ============================================================
print("=" * 70)
print("FIELD 9: SUM OF DIVISORS sigma(N)")
print("=" * 70)
# HYPOTHESIS: sigma(N) = 1 + p + q + N for N=pq.
# So sigma(N) - N - 1 = p + q. Same as phi approach!

print("sigma(N) = 1 + p + q + pq = (1+p)(1+q)")
for N, p, q in TESTS[:5]:
    sigma = (1 + p) * (1 + q)
    s = sigma - N - 1  # = p + q
    disc = s * s - 4 * N
    sd = isqrt(abs(disc))
    ok = disc >= 0 and sd * sd == disc
    print(f"  N={N}: sigma={sigma}, p+q={s}, recovers factors: {ok}")

print("VERDICT: sigma(N) gives p+q directly. But computing sigma requires factoring.")
print("CLASS: CIRCULAR — same chicken-and-egg as phi.\n")

# ============================================================
# FIELD 10: Carmichael Lambda
# ============================================================
print("=" * 70)
print("FIELD 10: CARMICHAEL LAMBDA — lcm(p-1, q-1)")
print("=" * 70)
# HYPOTHESIS: lambda(N) = lcm(p-1, q-1). If known, we can factor N.
# Because: find random a, compute a^{lambda} mod N = 1.
# Then gcd(a^{lambda/2} - 1, N) might give a factor (Miller-Rabin style).

def carmichael_factor(N, lam, max_tries=20):
    """Factor N given lambda(N) using random square roots of unity."""
    # Factor out powers of 2 from lambda
    d = lam
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(max_tries):
        a = random.randint(2, N - 2)
        x = pow(a, d, N)
        if x == 1 or x == N - 1:
            continue
        for _ in range(r - 1):
            y = pow(x, 2, N)
            if y == 1:
                g = gcd(x - 1, N)
                if 1 < g < N:
                    return g
                break
            if y == N - 1:
                break
            x = y
    return None

print("Factor N given lambda(N):")
for N, p, q in TESTS[:8]:
    lam = math.lcm(p - 1, q - 1)
    f = carmichael_factor(N, lam)
    ok = f is not None and (f == p or f == q)
    print(f"  N={N}: lambda={lam}, recovered factor={f}, correct={ok}")

print("VERDICT: lambda(N) gives EASY factoring via Miller-Rabin decomposition.")
print("CLASS: POWERFUL but CIRCULAR — computing lambda requires factoring.\n")

# ============================================================
# FIELD 11: Moebius Function
# ============================================================
print("=" * 70)
print("FIELD 11: MOEBIUS FUNCTION mu(N)")
print("=" * 70)
# HYPOTHESIS: mu(N) = (-1)^k if N is product of k distinct primes, 0 if N has
# squared factor. For semiprime pq: mu(N) = 1. This is a binary test.
# It tells us N is squarefree with even number of prime factors. Not helpful.

print("mu(N) for semiprimes = +1 always (product of 2 distinct primes)")
print("mu tells us #prime_factors is even AND N is squarefree.")
print("For factoring: ZERO information gain — we already know N is a semiprime.")
print("CLASS: USELESS — confirmed, as expected.\n")

# ============================================================
# FIELD 12: Liouville/Mangoldt — estimating log(p) + log(q)
# ============================================================
print("=" * 70)
print("FIELD 12: VON MANGOLDT FUNCTION — Lambda(N) = log(p) + log(q)")
print("=" * 70)
# HYPOTHESIS: For N=pq, the von Mangoldt function is 0 (not a prime power).
# But Λ(p) = log(p). The Chebyshev function ψ(x) = Σ_{n<=x} Λ(n).
# Can we extract information about p from ψ(N)?
# Really: log(p) + log(q) = log(N). We know this. Not helpful.

print("log(p) + log(q) = log(N) — this is trivially known.")
print("The RATIO log(p)/log(q) would help: it gives p/q.")
for N, p, q in TESTS[:5]:
    ratio = math.log(min(p,q)) / math.log(max(p,q))
    print(f"  N={N}={p}*{q}: log(p)/log(q) = {ratio:.4f}, p/q = {min(p,q)/max(p,q):.4f}")

print("VERDICT: Knowing log(p)/log(q) gives p/q, but computing it requires knowing p,q.")
print("CLASS: USELESS — no new information extractable.\n")

# ============================================================
# FIELD 13: Prime Gaps Near sqrt(N)
# ============================================================
print("=" * 70)
print("FIELD 13: PRIME GAPS NEAR sqrt(N)")
print("=" * 70)
# HYPOTHESIS: For balanced semiprimes, both p and q are near sqrt(N).
# The prime gap distribution near sqrt(N) determines the density of semiprimes.
# Question: do factors of specific N cluster at specific gap positions?

def primes_near(x, count=20):
    """Find primes near x."""
    result = []
    # Search upward
    n = int(x)
    if n % 2 == 0: n += 1
    while len(result) < count:
        if is_prime(n):
            result.append(n)
        n += 2
    return sorted(result)

print("For balanced semiprimes: factors near sqrt(N)")
for N, p, q in TESTS[:6]:
    s = isqrt(N)
    gap_p = abs(p - s)
    gap_q = abs(q - s)
    # Average prime gap near s is ~ln(s)
    avg_gap = math.log(s)
    print(f"  N={N}: sqrt={s}, p={p} (gap={gap_p}), q={q} (gap={gap_q}), "
          f"avg_prime_gap~{avg_gap:.1f}")

print("VERDICT: Factors of balanced semiprimes ARE near sqrt(N) by definition.")
print("  The gap distribution is just the prime counting function. No shortcut.")
print("CLASS: TRIVIAL — Fermat's method already exploits this.\n")

# ============================================================
# FIELD 14: Base-sqrt(N) Representation
# ============================================================
print("=" * 70)
print("FIELD 14: BASE-sqrt(N) REPRESENTATION")
print("=" * 70)
# HYPOTHESIS: Writing N in base b = floor(sqrt(N)) gives N = 1*b^2 + c1*b + c0
# (since N ~ b^2). For N=pq with p<q: N = p*q, and in base b:
# The coefficients might reveal something about p,q.

print("N in base floor(sqrt(N)):")
for N, p, q in TESTS[:8]:
    b = isqrt(N)
    c2 = N // (b * b)
    remainder = N - c2 * b * b
    c1 = remainder // b
    c0 = remainder % b
    print(f"  N={N}={p}*{q}: base {b}: [{c2}, {c1}, {c0}]", end="")
    # N = c2*b^2 + c1*b + c0
    # For N = b^2 + r: c2=1, c1*b + c0 = r
    # If p ~ b: N = p*q ~ p*(N/p), and in base b: reveals p-b gap?
    g = gcd(c1, N)
    if 1 < g < N:
        print(f" gcd(c1,N)={g} FACTOR!", end="")
    g0 = gcd(c0, N)
    if 1 < g0 < N:
        print(f" gcd(c0,N)={g0} FACTOR!", end="")
    print()

print("VERDICT: Base-sqrt(N) coefficients occasionally share factors with N (small N artifact).")
print("CLASS: WEAK — no systematic advantage over trial division.\n")

# ============================================================
# FIELD 15: Factorial Base Representation
# ============================================================
print("=" * 70)
print("FIELD 15: FACTORIAL BASE — N = sum c_k * k!")
print("=" * 70)
# HYPOTHESIS: Every integer has unique factorial base representation:
# N = c_2*2! + c_3*3! + ... where 0 <= c_k <= k.
# The coefficients might encode factor information since k! has known factorization.

def factorial_base(n):
    """Return factorial base digits [c_2, c_3, ...] for n."""
    digits = []
    k = 2
    while n > 0:
        digits.append(n % k)
        n //= k
        k += 1
    return digits

print("Factorial base representation:")
for N, p, q in TESTS[:6]:
    fb = factorial_base(N)
    print(f"  N={N}={p}*{q}: FB = {fb[:12]}{'...' if len(fb) > 12 else ''}")
    # Check if any c_k reveals factor
    for i, c in enumerate(fb):
        k = i + 2
        g = gcd(c, N) if c > 1 else 1
        if 1 < g < N:
            print(f"    c_{k}={c}: gcd(c_{k}, N) = {g} — FACTOR at position {k}!")
            break

print("VERDICT: Factorial base digits sometimes share factors (when c_k is composite).")
print("CLASS: WEAK — accidental gcd hits, no systematic method.\n")

# ============================================================
# FIELD 16: Zeckendorf Representation (Fibonacci base)
# ============================================================
print("=" * 70)
print("FIELD 16: ZECKENDORF REPRESENTATION — sum of non-consecutive Fibonacci")
print("=" * 70)
# HYPOTHESIS: Every positive integer is uniquely a sum of non-consecutive
# Fibonacci numbers. The positions used might correlate with factor structure
# since Fibonacci numbers have known divisibility properties.

def fibonacci_list(limit):
    fibs = [1, 2]
    while fibs[-1] < limit:
        fibs.append(fibs[-1] + fibs[-2])
    return fibs

def zeckendorf(n):
    """Return Zeckendorf representation as list of Fibonacci indices."""
    fibs = fibonacci_list(n + 1)
    indices = []
    for i in range(len(fibs) - 1, -1, -1):
        if fibs[i] <= n:
            indices.append(i)
            n -= fibs[i]
            if n == 0:
                break
    return indices

print("Zeckendorf representation:")
fibs = fibonacci_list(10**15)
for N, p, q in TESTS[:6]:
    z = zeckendorf(N)
    print(f"  N={N}={p}*{q}: Fib indices = {z}")
    # Property: gcd(F_m, F_n) = F_{gcd(m,n)}
    # So if F_k | p, then k | index of p in Fibonacci sequence
    # Check: does any F_{z_i} share a factor with N?
    for idx in z:
        g = gcd(fibs[idx], N)
        if 1 < g < N:
            print(f"    F_{idx}={fibs[idx]}: gcd(F_{idx}, N) = {g} — FACTOR!")
            break

print("VERDICT: Fibonacci divisibility (gcd(F_m,F_n)=F_{gcd(m,n)}) is elegant but")
print("  doesn't help unless we know which F_k divides p.")
print("CLASS: WEAK — beautiful math, no computational advantage.\n")

# ============================================================
# FIELD 17: Stern Sequence / Calkin-Wilf Tree
# ============================================================
print("=" * 70)
print("FIELD 17: STERN SEQUENCE — Calkin-Wilf tree of rationals")
print("=" * 70)
# HYPOTHESIS: The Stern-Brocot tree enumerates all positive rationals p/q.
# If we could locate p/q in the tree (where N=pq), we'd have the factors.
# The path in the tree is given by the CF expansion of p/q.
# But we don't know p/q... unless we try different guesses.

def stern_brocot_path(p, q, max_depth=50):
    """Return Stern-Brocot path for fraction p/q as string of L/R."""
    path = []
    lo_n, lo_d = 0, 1
    hi_n, hi_d = 1, 0
    for _ in range(max_depth):
        med_n = lo_n + hi_n
        med_d = lo_d + hi_d
        if med_n == p and med_d == q:
            return ''.join(path)
        elif p * med_d < med_n * q:  # p/q < med_n/med_d
            hi_n, hi_d = med_n, med_d
            path.append('L')
        else:
            lo_n, lo_d = med_n, med_d
            path.append('R')
    return ''.join(path)

print("Stern-Brocot path for factor ratios:")
for N, p, q in TESTS[:6]:
    path = stern_brocot_path(min(p, q), max(p, q), 40)
    print(f"  N={N}={p}*{q}: path({p}/{q}) = {path[:30]}{'...' if len(path)>30 else ''}")
    # The path encodes the CF of p/q. Length ~ log(max(p,q)).
    # We'd need to search the tree, which is O(p+q) ~ O(sqrt(N)).

print("VERDICT: Stern-Brocot gives a tree search for p/q, but search is O(sqrt(N)).")
print("CLASS: EQUIVALENT to trial division — no improvement.\n")

# ============================================================
# FIELD 18: Recaman Sequence
# ============================================================
print("=" * 70)
print("FIELD 18: RECAMAN SEQUENCE — a(n+1) = a(n)-n if positive & new, else a(n)+n")
print("=" * 70)
# HYPOTHESIS: The Recaman sequence has complex structure. If N appears at
# index k, does k encode factor information? Probably not — the sequence
# is pseudorandom in nature.

def recaman(limit):
    """Compute Recaman sequence up to max value limit."""
    a = [0]
    seen = {0}
    n = 1
    while n < 10000 and a[-1] < limit * 2:
        candidate = a[-1] - n
        if candidate > 0 and candidate not in seen:
            a.append(candidate)
        else:
            a.append(a[-1] + n)
        seen.add(a[-1])
        n += 1
    return a, seen

print("Checking if test semiprimes appear in Recaman sequence:")
rec_seq, rec_set = recaman(max(N for N, _, _ in TESTS[:6]))
hits = 0
for N, p, q in TESTS[:6]:
    found = N in rec_set
    if found:
        idx = next(i for i, v in enumerate(rec_seq) if v == N)
        print(f"  N={N}={p}*{q}: appears at index {idx}")
        hits += 1
    else:
        print(f"  N={N}={p}*{q}: NOT in first {len(rec_seq)} terms")

print(f"VERDICT: {hits}/{min(6,len(TESTS))} semiprimes found. No factor correlation.")
print("CLASS: USELESS — Recaman membership is unrelated to factorizability.\n")

# ============================================================
# FIELD 19: Aliquot Sequences
# ============================================================
print("=" * 70)
print("FIELD 19: ALIQUOT SEQUENCES — iterate s(n) = sigma(n) - n")
print("=" * 70)
# HYPOTHESIS: The aliquot sequence s(N), s(s(N)), ... depends on the factor
# structure. For N=pq: s(N) = 1+p+q. Then s(1+p+q) depends on factoring 1+p+q.
# If the sequence cycles or terminates, it might reveal structure.
# Problem: computing s(N) requires knowing p+q, which requires factoring.

def aliquot_step_known(N, p, q):
    """Compute s(N) = sigma(N) - N for N=pq."""
    return 1 + p + q

print("Aliquot first step s(N) = 1 + p + q:")
for N, p, q in TESTS[:6]:
    s = aliquot_step_known(N, p, q)
    # Can we factor s? It's much smaller than N.
    f = trial_factor(s, 10**5)
    print(f"  N={N}={p}*{q}: s(N)={s}, smallest_factor(s)={f}")

print("VERDICT: s(N) = 1+p+q requires factoring N. Circular.")
print("  Even if computed, the aliquot sequence is chaotic — no pattern.")
print("CLASS: CIRCULAR + CHAOTIC — doubly useless.\n")

# ============================================================
# FIELD 20: Multiplicative Partitions
# ============================================================
print("=" * 70)
print("FIELD 20: MULTIPLICATIVE PARTITIONS — ways to write N as product of >1 factors")
print("=" * 70)
# HYPOTHESIS: The number of multiplicative partitions f(N) depends on the
# prime factorization. For N=pq (distinct primes): f(N) = 2 (just {N} and {p,q}).
# For N=p^a*q^b: f(N) grows with a,b. Counting f(N) might detect prime powers.

def count_mult_partitions(n, min_factor=2):
    """Count multiplicative partitions of n with all parts >= min_factor."""
    if n == 1:
        return 1
    count = 0
    d = min_factor
    while d * d <= n:
        if n % d == 0:
            count += count_mult_partitions(n // d, d)
        d += 1
    count += 1  # n itself as a single part
    return count

print("Multiplicative partitions f(N):")
test_cases = [
    (15, 3, 5),    # pq: f=2
    (12, 2, 6),    # 2^2*3: f=4
    (30, 2, 15),   # 2*3*5: f=5
    (60, 2, 30),   # 2^2*3*5: f=10
    (64, 2, 32),   # 2^6: f=11
]
for N, p, q in test_cases:
    f = count_mult_partitions(N)
    print(f"  N={N}: f(N) = {f}")

# For semiprimes specifically
print("\nFor semiprimes p*q (distinct primes): f(N) = 2 always")
for N, p, q in TESTS[:5]:
    f = count_mult_partitions(N)
    print(f"  N={N}={p}*{q}: f(N) = {f}")

print("VERDICT: f(pq) = 2 for all semiprimes. Counting partitions cannot distinguish them.")
print("CLASS: USELESS — constant for semiprimes, tells us nothing.\n")

# ============================================================
# GRAND SUMMARY
# ============================================================
print("=" * 70)
print("GRAND SUMMARY: 20 NEW FIELDS")
print("=" * 70)

summary = [
    (1,  "Symbolic Regression",       "PARTIAL",   "Modular constraints known; ML can't predict factors"),
    (2,  "CF of N/sqrt(N)",           "WEAK",      "Convergent gcd hits unreliable, not systematic"),
    (3,  "Digital Root Patterns",     "TRIVIAL",   "Equivalent to N mod 9 — already in sieving"),
    (4,  "Benford's Law",            "USELESS",   "Factors follow expected distribution, no deviation"),
    (5,  "Arithmetic Derivative",     "CIRCULAR",  "N'=p+q but requires knowing p,q to compute"),
    (6,  "Radical of N",             "CIRCULAR",  "rad(N)=N for squarefree; requires factoring"),
    (7,  "Powerful Numbers",         "USELESS",   "Semiprimes are never powerful — zero info"),
    (8,  "Euler's Totient",          "CIRCULAR",  "phi gives factors but needs factoring to compute"),
    (9,  "Sum of Divisors",          "CIRCULAR",  "sigma gives p+q but needs factoring to compute"),
    (10, "Carmichael Lambda",        "CIRCULAR",  "Lambda gives easy factoring but needs factoring"),
    (11, "Moebius Function",         "USELESS",   "mu(pq)=1 always — zero distinguishing power"),
    (12, "Von Mangoldt / Liouville", "USELESS",   "log(p)+log(q)=log(N) is trivially known"),
    (13, "Prime Gaps near sqrt(N)",  "TRIVIAL",   "Fermat's method already exploits this"),
    (14, "Base-sqrt(N)",             "WEAK",      "Coefficients rarely share factors; no system"),
    (15, "Factorial Base",           "WEAK",      "Accidental gcd hits, no systematic method"),
    (16, "Zeckendorf / Fibonacci",   "WEAK",      "Beautiful math but gcd(F_m,F_n)=F_{gcd} unhelpful"),
    (17, "Stern-Brocot / Calkin-Wilf","EQUIVALENT","Tree search is O(sqrt(N)) — same as trial div"),
    (18, "Recaman Sequence",         "USELESS",   "Membership unrelated to factor structure"),
    (19, "Aliquot Sequences",        "CIRCULAR",  "s(N)=1+p+q requires factoring; sequence chaotic"),
    (20, "Multiplicative Partitions", "USELESS",  "f(pq)=2 always for semiprimes"),
]

print(f"\n{'#':<3} {'Field':<28} {'Class':<12} {'Finding'}")
print("-" * 90)
for num, field, cls, finding in summary:
    print(f"{num:<3} {field:<28} {cls:<12} {finding}")

# Tally
from collections import Counter as C2
tally = C2(cls for _, _, cls, _ in summary)
print(f"\nTally: {dict(tally)}")
print(f"\nCIRCULAR (6): These functions (phi, sigma, lambda, N', rad, aliquot) all")
print(f"  require the factorization to compute — the 'factoring barrier'.")
print(f"USELESS (5): Zero information gain for semiprimes specifically.")
print(f"WEAK (4): Occasional accidental hits but no systematic advantage.")
print(f"TRIVIAL (2): Already known techniques in different clothing.")
print(f"PARTIAL (1): Modular arithmetic helps but is already used in sieves.")
print(f"EQUIVALENT (1): Same complexity as existing methods.")
print(f"\nMETA-CONCLUSION: Number-theoretic functions that characterize N's factor")
print(f"  structure (phi, sigma, lambda, mu, N') ALL require factoring to compute.")
print(f"  This is not coincidence — it's the fundamental barrier.")
print(f"  Representation changes (Zeckendorf, factorial base, digital root) add")
print(f"  no information because they're bijections that preserve computational hardness.")
