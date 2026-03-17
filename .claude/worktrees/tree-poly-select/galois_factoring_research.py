#!/usr/bin/env python3
"""
Task #15: Galois Group Structure of N for Factoring Shortcuts

Explore whether Galois groups, class numbers, genus theory, and quadratic
form theory can reveal factoring information about semiprimes N=p*q.

Key experiments:
1. Jacobi symbol patterns for d=-1...-100 — do they leak factor info?
2. Cornacchia reverse — representing N as x^2 + d*y^2
3. Class number computation for small discriminants
4. Genus theory — genus characters as factoring oracle
5. Quadratic forms and ambiguous classes
6. Ring of integers structure mod N

Constraints: 30s timeout, <100MB RAM, use gmpy2.
"""

import time
import math
import random
import sys
from collections import defaultdict, Counter
import gmpy2
from gmpy2 import mpz, jacobi, is_prime, next_prime, isqrt, gcd, invert

TIMEOUT = 30.0
START = time.time()
RESULTS = []

def elapsed():
    return time.time() - START

def log(msg):
    RESULTS.append(msg)
    print(msg)

def make_semiprime(bits):
    """Generate a random semiprime N=p*q with p,q ~ bits/2 each."""
    half = bits // 2
    while True:
        p = gmpy2.next_prime(gmpy2.mpz_random(gmpy2.random_state(random.randint(0,2**32)), 2**half))
        q = gmpy2.next_prime(gmpy2.mpz_random(gmpy2.random_state(random.randint(0,2**32)), 2**half))
        if p != q and p.bit_length() >= half-1 and q.bit_length() >= half-1:
            return p, q, p * q

# ============================================================
# Experiment 1: Jacobi Symbol Patterns
# ============================================================
def exp1_jacobi_patterns():
    """
    For N=pq, jacobi(d, N) = jacobi(d, p) * jacobi(d, q).
    If jacobi(d, N) = -1, then d is QNR mod exactly one factor.
    Can we use patterns of jacobi(d, N) for d=-1...-100 to distinguish
    factors or narrow the search?
    """
    log("\n=== Experiment 1: Jacobi Symbol Patterns ===")

    for bits in [64, 128, 256]:
        p, q, N = make_semiprime(bits)
        log(f"\n  {bits}-bit semiprime: p={p}, q={q}")

        # Compute jacobi(d, N) for d = -1 to -100
        jac_N = []
        jac_p = []
        jac_q = []
        useful_d = []  # d where jacobi(d,N)=1 but jacobi(d,p)!=jacobi(d,q) is impossible
        split_d = []   # d where jacobi(d,N)=-1 (splits factors)

        for d in range(-1, -101, -1):
            jN = jacobi(d, N)
            jp = jacobi(d, p)
            jq = jacobi(d, q)
            jac_N.append(jN)
            jac_p.append(jp)
            jac_q.append(jq)

            if jN == -1:
                split_d.append(d)
            elif jN == 1:
                # jN=1 means jp=jq=1 or jp=jq=-1; both cases possible
                pass

        log(f"  jacobi(d,N)=-1 count: {len(split_d)}/100 (these split p,q)")
        log(f"  Expected ~50% splits for random p,q: {len(split_d)}%")

        # Key insight: when jacobi(d,N) = -1, we know one of p,q is QR and other QNR for d
        # But we don't know WHICH one. Can we use multiple d values together?

        # Try: find d1, d2 where jacobi(d1,N)=-1 and jacobi(d2,N)=-1
        # Then jacobi(d1*d2, N) = 1, and we can try to find sqrt(d1*d2) mod N
        # If we find it, gcd(sqrt - something, N) might factor N
        if len(split_d) >= 2:
            d1, d2 = split_d[0], split_d[1]
            prod = (d1 * d2) % N
            # jacobi(d1*d2, N) should be 1
            j_prod = jacobi(prod, N)
            log(f"  jacobi({d1}*{d2} mod N, N) = {j_prod} (should be 1)")

    # Analysis: Jacobi symbols alone give genus information but not factors
    log("\n  FINDING: Jacobi symbols give genus characters (which genus N belongs to)")
    log("  but cannot directly reveal factors — this IS genus theory.")
    log("  The information is: which primes split in Z[sqrt(d)] vs remain inert.")
    log("  This is exactly the info that class group methods exploit.")


# ============================================================
# Experiment 2: Cornacchia's Algorithm — Reverse Direction
# ============================================================
def exp2_cornacchia():
    """
    Cornacchia: given prime p with jacobi(-d, p) = 1, find x,y with x^2 + d*y^2 = p.
    For composite N=pq: if N = x^2 + d*y^2, then gcd constraints may factor N.

    Key idea: if N = x^2 + y^2 (d=1), and N=pq where p,q = 1 mod 4,
    then p = a^2+b^2 and q = c^2+d^2, and N = (ac-bd)^2 + (ad+bc)^2 = (ac+bd)^2 + (ad-bc)^2.
    Multiple representations => factor via gcd!
    """
    log("\n=== Experiment 2: Cornacchia Reverse (Sum of Squares) ===")

    def cornacchia(d, p):
        """Find x,y with x^2 + d*y^2 = p, or None."""
        if d <= 0 or d >= p:
            return None
        j = jacobi(-d, p)
        if j != 1:
            return None
        # Find sqrt(-d) mod p
        try:
            # Tonelli-Shanks via gmpy2
            r = gmpy2.powmod(-d, (p+1)//4, p) if p % 4 == 3 else _tonelli(-d % p, p)
            if (r*r) % p != (-d) % p:
                return None
        except:
            return None

        # Euclidean-like reduction
        r0, r1 = p, int(r)
        bound = isqrt(p)
        while r1 > bound:
            r0, r1 = r1, r0 % r1

        x = r1
        t = p - x*x
        if t % d != 0:
            return None
        y2 = t // d
        y = isqrt(y2)
        if y*y != y2:
            return None
        return (x, y)

    def _tonelli(n, p):
        """Tonelli-Shanks for sqrt(n) mod p."""
        n = n % p
        if n == 0:
            return 0
        if p % 4 == 3:
            return int(gmpy2.powmod(n, (p+1)//4, p))
        # General Tonelli-Shanks
        Q, S = p-1, 0
        while Q % 2 == 0:
            Q //= 2
            S += 1
        z = 2
        while jacobi(z, p) != -1:
            z += 1
        M, c, t, R = S, gmpy2.powmod(z, Q, p), gmpy2.powmod(n, Q, p), gmpy2.powmod(n, (Q+1)//2, p)
        while True:
            if t == 1:
                return int(R)
            i = 1
            tmp = (t*t) % p
            while tmp != 1:
                tmp = (tmp*tmp) % p
                i += 1
            b = gmpy2.powmod(c, 1 << (M-i-1), p)
            M, c, t, R = i, (b*b)%p, (t*b*b)%p, (R*b)%p

    # Test: find primes p,q = 1 mod 4, compute representations
    found_factor = 0
    tried = 0

    for trial in range(20):
        if elapsed() > 10:
            break
        # Generate p, q both 1 mod 4
        p = next_prime(random.randint(10**8, 10**9))
        while p % 4 != 1:
            p = next_prime(p)
        q = next_prime(random.randint(10**8, 10**9))
        while q % 4 != 1:
            q = next_prime(q)
        if p == q:
            continue
        N = p * q
        tried += 1

        # Both p,q are sum of two squares
        rep_p = cornacchia(1, int(p))
        rep_q = cornacchia(1, int(q))

        if rep_p and rep_q:
            a, b = rep_p
            c, d = rep_q
            # N = (ac-bd)^2 + (ad+bc)^2 = (ac+bd)^2 + (ad-bc)^2
            r1 = (a*c - b*d, a*d + b*c)
            r2 = (a*c + b*d, abs(a*d - b*c))

            # Verify
            assert r1[0]**2 + r1[1]**2 == N
            assert r2[0]**2 + r2[1]**2 == N

            # Factor from two representations!
            g = gcd(abs(r1[0] - r2[0]), N)
            if 1 < g < N:
                found_factor += 1
            else:
                g = gcd(abs(r1[0] + r2[0]), N)
                if 1 < g < N:
                    found_factor += 1
                else:
                    g = gcd(abs(r1[1] - r2[1]), N)
                    if 1 < g < N:
                        found_factor += 1

    log(f"  Cornacchia factor recovery: {found_factor}/{tried} (knowing p,q decompositions)")
    log(f"  FINDING: Two sum-of-squares representations of N always factor N (Theorem T28)")
    log(f"  BUT: finding the representations requires knowing the factors first!")
    log(f"  Cornacchia needs a PRIME input — cannot run on composite N directly.")
    log(f"  This is circular: need factors to get reps, need reps to get factors.")


# ============================================================
# Experiment 3: Class Number Computation
# ============================================================
def exp3_class_numbers():
    """
    Class number h(d) of Q(sqrt(d)) tells how many ideal classes exist.
    For d = -N (N=pq semiprime), h(-N) relates to factorization structure.

    Key question: does h(-4N) for semiprime N differ systematically from
    h(-4p) for prime p? If so, class number = factoring oracle.
    """
    log("\n=== Experiment 3: Class Number Computation ===")

    def class_number_naive(d):
        """Compute class number h(d) for negative fundamental discriminant d.
        Uses brute-force counting of reduced binary quadratic forms.
        Only works for small |d| (< 10^6)."""
        if d >= 0:
            return None
        # Make d a fundamental discriminant
        D = d
        if D % 4 not in (0, 1):
            D = 4 * d

        # Count reduced forms ax^2 + bxy + cy^2 with discriminant D = b^2 - 4ac
        # Reduced: |b| <= a <= c, and if |b|=a or a=c then b >= 0
        count = 0
        absD = abs(D)
        a_bound = isqrt(absD // 3) + 1

        for a in range(1, int(a_bound) + 1):
            for b in range(-a, a + 1):
                # D = b^2 - 4ac => c = (b^2 - D) / (4a)
                num = b * b - D
                if num % (4 * a) != 0:
                    continue
                c = num // (4 * a)
                if c < a:
                    continue
                if c < 0:
                    continue
                # Reduced form conditions
                if abs(b) > a:
                    continue
                if a == c and b < 0:
                    continue
                if abs(b) == a and b < 0:
                    continue
                count += 1

        return count

    # Compare class numbers for prime vs semiprime discriminants
    log("  Computing h(-d) for small primes and semiprimes...")

    prime_h = []
    semi_h = []

    primes_list = []
    p = mpz(5)
    while len(primes_list) < 50:
        if p % 4 == 3:  # fundamental discriminant -p when p=3 mod 4
            primes_list.append(int(p))
        p = next_prime(p)

    for pp in primes_list[:30]:
        if elapsed() > 15:
            break
        h = class_number_naive(-pp)
        if h is not None:
            prime_h.append((pp, h))

    # Small semiprimes with both factors 3 mod 4
    semis = []
    for p in [3, 7, 11, 19, 23, 31, 43, 47]:
        for q in [3, 7, 11, 19, 23, 31, 43, 47]:
            if p < q:
                N = p * q
                if N < 5000 and (N % 4 == 3 or N % 4 == 0):
                    semis.append((p, q, N))

    for p_f, q_f, N in semis[:20]:
        if elapsed() > 20:
            break
        h = class_number_naive(-N) if N % 4 == 3 else class_number_naive(-N)
        if h is not None:
            semi_h.append((N, f"{p_f}*{q_f}", h))

    log(f"  Prime discriminants (first 10):")
    for pp, h in prime_h[:10]:
        log(f"    h(-{pp}) = {h}")

    log(f"  Semiprime discriminants (first 10):")
    for N, factors, h in semi_h[:10]:
        log(f"    h(-{N}) = {h}  (N = {factors})")

    # Key analysis: class number formula h(-d) ~ sqrt(d)/pi * L(1, chi_d)
    # For d=pq, L(1, chi_{-pq}) = L(1, chi_{-p}) * L(1, chi_{-q}) * correction
    # But computing L-values is as hard as factoring!

    if prime_h and semi_h:
        avg_prime_h = sum(h for _, h in prime_h) / len(prime_h)
        avg_semi_h = sum(h for _, _, h in semi_h) / len(semi_h)
        log(f"\n  Average h for primes: {avg_prime_h:.1f}")
        log(f"  Average h for semiprimes: {avg_semi_h:.1f}")

    log("  FINDING: Class numbers grow as O(sqrt(|d|)) for both primes and semiprimes.")
    log("  The RATIO h(-pq) / (h(-p)*h(-q)) encodes factoring info,")
    log("  but computing h(-N) for large N requires O(sqrt(N)) work — same as trial division!")


# ============================================================
# Experiment 4: Genus Theory as Factoring Oracle
# ============================================================
def exp4_genus_theory():
    """
    Genus theory: for discriminant D, the genus group = Cl(D) / Cl(D)^2.
    The number of genera = 2^(t-1) where t = number of prime factors of D.

    Key question: can we determine t (and hence factorize D) from genus characters?
    """
    log("\n=== Experiment 4: Genus Theory ===")

    # Genus characters are products of Jacobi symbols
    # For D = -4N, the genus characters are chi_p(a) = (a/p) for odd primes p | N
    # and chi_{-4}(a) = (-1)^((a-1)/2) if 2 | N, etc.

    # The number of genera = 2^(t-1) where t = # distinct prime factors of |D|
    # So if N = pq (two prime factors), then D = -4pq has t=3 (including 2),
    # giving 4 genera.

    # Can we COUNT genera without factoring?
    # Genera = equivalence classes of forms under genus characters
    # But genus characters require knowing the factorization of D!

    for bits in [32, 64]:
        p, q, N = make_semiprime(bits)
        log(f"\n  {bits}-bit N={N} = {p} * {q}")

        # Number of genera for D = -4N = -4pq
        # t = number of prime divisors of 4pq = {2, p, q} = 3
        # genera = 2^(3-1) = 4
        log(f"  Theoretical genera count: 4 (for D=-4pq, t=3)")

        # Attempt to determine genus count from reduced forms
        # This requires enumerating forms, which is O(sqrt(N))
        if bits <= 32:
            D = -4 * int(N)
            absD = abs(D)

            # Group forms by genus character values
            forms_by_genus = defaultdict(list)
            a_bound = int(isqrt(absD // 3)) + 1
            form_count = 0

            for a in range(1, min(a_bound + 1, 500)):  # limit for speed
                if elapsed() > 25:
                    break
                for b in range(-a, a + 1):
                    num = b * b - D
                    if num % (4 * a) != 0:
                        continue
                    c = num // (4 * a)
                    if c < a or c < 0:
                        continue
                    if abs(b) > a:
                        continue
                    if a == c and b < 0:
                        continue
                    if abs(b) == a and b < 0:
                        continue

                    # Genus character: chi_p(a) and chi_q(a)
                    chi_p = jacobi(a, p)
                    chi_q = jacobi(a, q)
                    forms_by_genus[(chi_p, chi_q)].append((a, b, c))
                    form_count += 1

            log(f"  Forms found (a<500): {form_count}")
            log(f"  Genus distribution:")
            for genus, forms in sorted(forms_by_genus.items()):
                log(f"    chi=({genus[0]:+d},{genus[1]:+d}): {len(forms)} forms")

            # The genus characters USE the factorization — circular!
            # Without knowing p,q, we can't compute chi_p, chi_q separately

            # But: the NUMBER of genera can theoretically be determined
            # from the structure of Cl(D), specifically its 2-rank
            # 2-rank = t - 1 where t = number of prime divisors
            # For a semiprime 4pq: 2-rank = 2, so 4 genera
            # For a prime 4p: 2-rank = 1, so 2 genera
            # DISTINGUISHING these would reveal N is composite!

            # Attempt: count ambiguous forms (forms with a|b)
            ambiguous = 0
            for a in range(1, min(int(isqrt(absD)) + 1, 1000)):
                for b in [0, a]:  # ambiguous: b=0 or b=a
                    num = b * b - D
                    if num <= 0:
                        continue
                    if num % (4 * a) != 0:
                        continue
                    c = num // (4 * a)
                    if c >= a and c > 0:
                        ambiguous += 1

            log(f"  Ambiguous forms: {ambiguous}")
            log(f"  (For D=-4pq, expect 4 ambiguous forms; for D=-4p, expect 2)")

    log("\n  FINDING: Number of genera = 2^(t-1) where t = # prime factors of discriminant.")
    log("  Counting genera WOULD distinguish primes from semiprimes.")
    log("  BUT counting genera requires O(sqrt(|D|)) form enumeration — circular!")
    log("  The genus structure encodes factorization, but accessing it costs O(sqrt(N)).")


# ============================================================
# Experiment 5: Ambiguous Forms and Factor Extraction
# ============================================================
def exp5_ambiguous_forms():
    """
    Ambiguous binary quadratic forms (b=0 or b=a) correspond to factorizations.
    For D = -4N, each ambiguous form gives a divisor of N.
    Can we find ambiguous forms faster than O(sqrt(N))?
    """
    log("\n=== Experiment 5: Ambiguous Forms => Factor Extraction ===")

    for bits in [20, 24, 28, 32]:
        if elapsed() > 27:
            break
        p, q, N = make_semiprime(bits)
        D = -4 * int(N)
        absD = abs(D)
        log(f"\n  {bits}-bit N={N} = {p}*{q}, D={D}")

        # Find ALL ambiguous forms
        ambiguous_forms = []
        for a in range(1, int(isqrt(absD)) + 1):
            if elapsed() > 28:
                break
            # b = 0: need -D divisible by 4a, c = -D/(4a) >= a
            if absD % (4 * a) == 0:
                c = absD // (4 * a)
                if c >= a:
                    ambiguous_forms.append((a, 0, c))
            # b = a: need (a^2 - D) divisible by 4a => (a^2 + 4N) / 4a = a/4 + N/a
            # Only works if a divides 4N and a divides a^2 (always)
            num = a * a + absD
            if num % (4 * a) == 0:
                c = num // (4 * a)
                if c >= a:
                    ambiguous_forms.append((a, a, c))

        log(f"  Ambiguous forms found: {len(ambiguous_forms)}")

        # Each ambiguous form (a, 0, c) has D = -4ac, so ac = N
        # => a is a divisor of N! Factor found!
        factors_found = set()
        for a, b, c in ambiguous_forms:
            if b == 0:
                g = gcd(a, N)
                if 1 < g < N:
                    factors_found.add(int(g))
                g = gcd(c, N)
                if 1 < g < N:
                    factors_found.add(int(g))
            elif b == a:
                # (a^2 + 4N) / (4a) = c => check gcd(a, N)
                g = gcd(a, N)
                if 1 < g < N:
                    factors_found.add(int(g))

        if factors_found:
            log(f"  Factors extracted: {factors_found}")
        else:
            log(f"  No non-trivial factors from ambiguous forms (expected for large N)")

        log(f"  Search range: a up to sqrt(4N) = {int(isqrt(absD))}")

    log("\n  FINDING: Ambiguous forms with b=0 directly give divisors (a*c = N).")
    log("  But finding them requires scanning a = 1..sqrt(4N), which IS trial division!")
    log("  Ambiguous form enumeration = trial division in disguise.")
    log("  No shortcut: the algebraic structure doesn't reduce the search space.")


# ============================================================
# Experiment 6: Quadratic Residue Patterns Across Small Primes
# ============================================================
def exp6_qr_patterns():
    """
    For N=pq, the quadratic residuosity of small primes mod N depends on
    their residuosity mod p and mod q independently.
    Can we use the pattern of (a/N) for small a to extract information?

    Key insight: (a/N) = (a/p)(a/q). If we find a where (a/N) = +1 but
    a is not actually a QR mod N, then sqrt(a) mod N has 4 roots, and
    gcd(root - trial, N) may factor N.
    """
    log("\n=== Experiment 6: Quadratic Residue Patterns ===")

    for bits in [64, 128]:
        p, q, N = make_semiprime(bits)
        log(f"\n  {bits}-bit N, p={p}, q={q}")

        # Count how many small primes have jacobi(a,N) = +1
        # These fall into two categories:
        # (a/p)=+1, (a/q)=+1 — genuine QR mod N (has 4 sqrt's)
        # (a/p)=-1, (a/q)=-1 — pseudo-QR mod N (has 0 sqrt's mod p, 0 mod q, but 4 mod N?!)
        # Wait, no: if (a/p)=-1 and (a/q)=-1, then a is NOT a QR mod p or q,
        # so a is NOT a QR mod N. But jacobi(a,N) = (-1)(-1) = +1.
        # This is the JACOBI symbol being +1 but not actually a QR!

        genuine_qr = 0
        pseudo_qr = 0  # jacobi=+1 but not actually QR mod N
        total_plus1 = 0

        test_primes = []
        tp = mpz(2)
        while len(test_primes) < 200:
            test_primes.append(int(tp))
            tp = next_prime(tp)

        for a in test_primes:
            jN = jacobi(a, N)
            if jN == 1:
                total_plus1 += 1
                jp = jacobi(a, p)
                jq = jacobi(a, q)
                if jp == 1 and jq == 1:
                    genuine_qr += 1
                elif jp == -1 and jq == -1:
                    pseudo_qr += 1

        log(f"  Jacobi(a,N)=+1: {total_plus1}/200")
        log(f"    Genuine QR (both +1): {genuine_qr}")
        log(f"    Pseudo QR (both -1): {pseudo_qr}")
        log(f"    Ratio pseudo/total: {pseudo_qr}/{total_plus1} = {pseudo_qr/max(total_plus1,1):.2f}")

        # The pseudo-QRs are exactly the ones where finding a "sqrt" would factor N
        # But distinguishing genuine from pseudo QR is equivalent to factoring!
        # (This is the basis of the Goldwasser-Micali cryptosystem)

    log("\n  FINDING: ~50% of jacobi(a,N)=+1 are pseudo-QR (a is QNR mod both p,q).")
    log("  Distinguishing genuine QR from pseudo QR is EQUIVALENT to factoring N.")
    log("  This is the Quadratic Residuosity Assumption (QRA) — basis of GM encryption.")
    log("  No polynomial-time algorithm known to break QRA without factoring N.")


# ============================================================
# Experiment 7: Class Group and Factor Base Connection
# ============================================================
def exp7_class_group_sieve():
    """
    The class group Cl(D) for D = -4N connects to factoring via:
    - Prime ideals above small primes p form the "factor base" in NFS/QS
    - Relations in the class group = smooth relations in the sieve
    - The class group structure reveals the factorization

    Is the class group approach fundamentally different from sieving?
    """
    log("\n=== Experiment 7: Class Group ↔ Sieve Connection ===")

    log("  Theoretical analysis:")
    log("  - For D = -4N, ideal class group Cl(D) has order h(D) ~ sqrt(N)/pi * L(1,chi)")
    log("  - Factor base primes p with (D/p)=1 split as (p) = P*P' in O_K")
    log("  - P represents a class in Cl(D); finding RELATIONS among classes = smooth rels")
    log("  - Class group computation via relation lattice IS the quadratic sieve!")
    log("  ")
    log("  Specifically:")
    log("  - QS: find x with x^2 ≡ y (mod N), y smooth => relation")
    log("  - Class group: find ideals I with I = product of FB ideals => relation")
    log("  - These are THE SAME THING viewed differently!")
    log("  ")
    log("  The Hafner-McCurley class group algorithm:")
    log("  - Complexity: L[1/2, sqrt(2)] for imaginary quadratic fields")
    log("  - This is EXACTLY the QS complexity!")
    log("  - Not a coincidence: same mathematical structure, same algorithm")
    log("  ")
    log("  For D = disc(Q(sqrt(-N))):")
    log("  - h(D) computation via subexponential algorithms = sieve methods")
    log("  - No known class group algorithm beats L[1/3] (= NFS)")
    log("  ")
    log("  CONCLUSION: Class group computation IS sieving, viewed through algebraic lens.")
    log("  No escape from L[1/3] lower bound via this reformulation.")


# ============================================================
# Experiment 8: Ring of Integers Structure
# ============================================================
def exp8_ring_structure():
    """
    Z/NZ for N=pq has a non-trivial idempotent structure.
    CRT: Z/NZ ≅ Z/pZ × Z/qZ.
    Can we detect idempotents without knowing p,q?
    """
    log("\n=== Experiment 8: Idempotent Detection in Z/NZ ===")

    for bits in [32, 64]:
        p, q, N = make_semiprime(bits)
        log(f"\n  {bits}-bit N={N} = {p}*{q}")

        # Non-trivial idempotents: e^2 = e mod N, e not in {0, 1}
        # These exist iff N is composite
        # e = CRT(1, 0) or CRT(0, 1) — but computing CRT needs p,q!

        # Can we FIND idempotents by random search?
        # Probability of random element being idempotent: 2/(pq) ≈ 0 for large N

        # Alternative: if we had e with e^2=e mod N, then gcd(e, N) = p or q
        # But finding such e is as hard as factoring

        # The STRUCTURE tells us idempotents exist, but not how to find them

        # Attempt: compute a^(N-1) mod N for random a (Fermat witnesses)
        # Not idempotents, but related to structure
        witnesses = 0
        for _ in range(100):
            a = random.randint(2, int(N) - 2)
            r = gmpy2.powmod(a, N - 1, N)
            if r != 1:
                witnesses += 1
                # This a is a Fermat witness; gcd(a^((N-1)/2) - 1, N) might factor
                half = gmpy2.powmod(a, (N-1)//2, N)
                g = gcd(half - 1, N)
                if 1 < g < N:
                    log(f"    Factor found via Fermat witness! gcd={g}")
                    break
                g = gcd(half + 1, N)
                if 1 < g < N:
                    log(f"    Factor found via Fermat witness! gcd={g}")
                    break

        log(f"  Fermat witnesses: {witnesses}/100 (N is composite, so most a are witnesses)")
        log(f"  Finding idempotents directly: probability 2/N ≈ 0 for large N")

    log("\n  FINDING: Z/NZ has 4 idempotents {0, 1, e_p, e_q} where e_p = CRT(1,0).")
    log("  Finding non-trivial idempotents IS factoring (gcd(e,N) gives factor).")
    log("  Random search: probability 2/N per trial — exponentially unlikely.")
    log("  Miller-Rabin uses related idea but still probabilistic primality test, not factoring.")


# ============================================================
# Run all experiments
# ============================================================
log("=" * 70)
log("GALOIS GROUP STRUCTURE OF N FOR FACTORING SHORTCUTS")
log("=" * 70)

exp1_jacobi_patterns()
if elapsed() < 25: exp2_cornacchia()
if elapsed() < 25: exp3_class_numbers()
if elapsed() < 25: exp4_genus_theory()
if elapsed() < 25: exp5_ambiguous_forms()
if elapsed() < 25: exp6_qr_patterns()
if elapsed() < 25: exp7_class_group_sieve()
if elapsed() < 25: exp8_ring_structure()

log("\n" + "=" * 70)
log("MASTER FINDINGS")
log("=" * 70)
log("""
1. JACOBI SYMBOLS: Give genus characters but not individual factors. Information
   is algebraically available but computationally inaccessible without factoring.

2. CORNACCHIA (SUM OF SQUARES): Two representations of N => factor, but finding
   representations requires knowing factors. Circular.

3. CLASS NUMBERS: h(-N) encodes factoring info, but computing h(-N) costs O(sqrt(N))
   for naive methods, L[1/2] for subexponential methods — same as QS.

4. GENUS THEORY: Number of genera = 2^(t-1), reveals number of prime factors.
   But counting genera requires O(sqrt(N)) form enumeration. No shortcut.

5. AMBIGUOUS FORMS: Directly give divisors (a*c = N for form (a,0,c)).
   But enumerating them IS trial division.

6. QUADRATIC RESIDUOSITY: Distinguishing genuine QR from pseudo QR is EQUIVALENT
   to factoring (Quadratic Residuosity Assumption). Basis of GM cryptosystem.

7. CLASS GROUP ↔ SIEVE: Class group computation via relation lattice IS the
   quadratic sieve (same complexity L[1/2]). No escape from L[1/3] via NFS.

8. IDEMPOTENTS: Finding non-trivial idempotents in Z/NZ IS factoring.
   Random search has probability 2/N per trial.

OVERALL CONCLUSION:
Every Galois/algebraic approach to factoring REDUCES to one of:
- Trial division O(sqrt(N))
- Birthday/rho O(N^{1/4})
- Sieve methods L[1/2] or L[1/3]

The algebraic structure ENCODES the factorization but doesn't provide a faster
algorithm to ACCESS it. The information-theoretic barrier remains: extracting
log2(p) bits from N requires exponential (or at best subexponential) work.

No new factoring paradigm found. All paths lead back to known complexity classes.
""")

log(f"\nTotal time: {elapsed():.1f}s")
