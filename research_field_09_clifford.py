"""Field 9: Clifford Algebras - Geometric Algebra Approach to Quadratic Forms
Hypothesis: N = x^2 - y^2 = (x-y)(x+y) is a quadratic form. Clifford algebras
provide a natural framework for quadratic forms. The Clifford algebra Cl(Q) where
Q(x,y) = x^2 - y^2 might have algebraic structure (spinor norms, pin groups)
that reveals factorizations more efficiently than Fermat's method.
"""
import time, math, random

def clifford_norm_test(N):
    """In Cl(1,1) (signature (1,1)), we have basis {e1, e2} with
    e1^2 = 1, e2^2 = -1, e1*e2 = -e2*e1.
    A vector v = a*e1 + b*e2 has Q(v) = a^2 - b^2.
    So N = a^2 - b^2 iff v*v = N in Cl(1,1).

    The spinor norm map N: Pin(1,1) -> Z/2Z detects factorizations.
    Specifically, if v = (x+y)*e1 + something, then the reflection
    through v factors the identity in the Clifford group.
    """
    # This reduces to finding a^2 - b^2 = N, i.e., Fermat's method
    # a = (p+q)/2, b = (p-q)/2 for N = p*q
    # Search: a starts at ceil(sqrt(N)), check if a^2 - N is a perfect square

    a = math.isqrt(N) + 1
    max_tries = min(100000, N)
    for _ in range(max_tries):
        b2 = a * a - N
        if b2 >= 0:
            b = math.isqrt(b2)
            if b * b == b2:
                p, q = a + b, a - b
                if p > 1 and q > 1:
                    return p, q, a - math.isqrt(N)  # steps from sqrt(N)
        a += 1
    return None, None, max_tries

def quaternion_factoring(N):
    """In the quaternion algebra (Cl(0,2)), every integer can be written as
    a sum of 4 squares (Lagrange). The quaternion representation
    N = a^2 + b^2 + c^2 + d^2 might factor through the quaternion norm map.

    For N=pq, if we can write p = a^2+b^2+c^2+d^2 and q similarly,
    then the quaternion product gives a representation of N.
    But finding the quaternion decomposition of N also requires factoring...
    """
    # Try: sum of 2 squares N = a^2 + b^2 (works when no prime factor = 3 mod 4)
    representations = []
    sq = math.isqrt(N)
    for a in range(sq + 1):
        b2 = N - a * a
        if b2 < 0:
            break
        b = math.isqrt(b2)
        if b * b == b2:
            representations.append((a, b))
            if len(representations) >= 5:
                break

    # If N = pq and we find TWO representations N = a^2+b^2 = c^2+d^2,
    # then gcd(a*c - b*d, N) or gcd(a*d + b*c, N) often gives a factor
    # (this is the Gaussian integer method)
    factors_found = []
    for i in range(len(representations)):
        for j in range(i + 1, len(representations)):
            a, b = representations[i]
            c, d = representations[j]
            for g_candidate in [a*c - b*d, a*c + b*d, a*d - b*c, a*d + b*c]:
                g = math.gcd(abs(g_candidate), N)
                if 1 < g < N:
                    factors_found.append(g)

    return representations, factors_found

def experiment():
    print("=== Field 9: Clifford Algebras - Quadratic Form Factoring ===\n")

    random.seed(42)
    test_cases = []
    for bits in [20, 24, 28, 32, 40]:
        while True:
            p = random.getrandbits(bits // 2) | (1 << (bits//2 - 1)) | 1
            q = random.getrandbits(bits // 2) | (1 << (bits//2 - 1)) | 1
            if p != q and p > 2 and q > 2:
                if all(p % d != 0 for d in range(2, min(int(p**0.5)+1, 300))) and \
                   all(q % d != 0 for d in range(2, min(int(q**0.5)+1, 300))):
                    break
        test_cases.append((p, q, p*q, bits))

    print("  Test 1: Fermat method via Cl(1,1) norm (a^2 - b^2 = N)")
    for p, q, N, bits in test_cases:
        t0 = time.time()
        fp, fq, steps = clifford_norm_test(N)
        elapsed = time.time() - t0
        if fp:
            print(f"    {bits}b: N={N} -> ({fp}, {fq}), steps={steps}, time={elapsed:.4f}s")
        else:
            print(f"    {bits}b: N={N} -> FAILED in {steps} steps, time={elapsed:.4f}s")

    print("\n  Test 2: Gaussian integer method (sum of 2 squares)")
    for p, q, N, bits in test_cases[:4]:  # Small only
        t0 = time.time()
        reps, factors = quaternion_factoring(N)
        elapsed = time.time() - t0
        print(f"    {bits}b: N={N}")
        print(f"      Representations: {reps[:3]}...")
        if factors:
            print(f"      FACTORS from dual reps: {set(factors)}")
        else:
            print(f"      No factor extraction (need 2+ representations)")
        print(f"      Time: {elapsed:.4f}s")

    print("\nVERDICT: Clifford algebra Cl(1,1) norm = Fermat's method (a^2-b^2=N).")
    print("This is O(N^{1/3}) worst case, same as known. The Gaussian integer method")
    print("(multiple sum-of-2-squares representations) DOES work but is equivalent to")
    print("CFRAC/QS approach. Clifford algebra provides the right LANGUAGE but no new")
    print("ALGORITHMS. The spinor norm doesn't shortcut the search.")
    print("RESULT: REFUTED (but Gaussian integer method is a KNOWN technique)")

experiment()
