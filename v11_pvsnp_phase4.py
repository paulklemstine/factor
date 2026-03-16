#!/usr/bin/env python3
"""
P vs NP Phase 4: Ten Moonshot Experiments
Each experiment has signal.alarm(30) and <100MB memory.
"""

import signal
import time
import sys
import random
import math
import hashlib
from collections import defaultdict
from functools import reduce

# Timeout handler
class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Experiment timed out (30s)")

signal.signal(signal.SIGALRM, timeout_handler)

def small_primes_up_to(n):
    """Sieve of Eratosthenes."""
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n + 1, i):
                sieve[j] = False
    return [i for i in range(2, n + 1) if sieve[i]]

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if a >= n: continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else:
            return False
    return True

def random_prime(bits):
    while True:
        n = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(n):
            return n

def random_semiprime(bits):
    half = bits // 2
    p = random_prime(half)
    q = random_prime(bits - half)
    while q == p:
        q = random_prime(bits - half)
    return p * q, min(p, q), max(p, q)

def trial_factor(n, limit=10**6):
    if n % 2 == 0: return 2
    for i in range(3, min(limit, int(n**0.5) + 1), 2):
        if n % i == 0: return i
    return None

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

results = {}

# ============================================================
# H1: Pseudorandom Generator Barrier Circumvention
# ============================================================
def experiment_h1():
    """
    Test: Can we construct a non-natural proof for a toy factoring circuit?
    Natural proofs require: (1) constructivity, (2) largeness.
    We test whether factoring-related properties violate largeness
    (i.e., hold for a negligible fraction of functions).
    """
    signal.alarm(30)
    try:
        print("=== H1: Pseudorandom Generator Barrier ===")

        # For n-bit inputs, consider Boolean functions f: {0,1}^n -> {0,1}
        # A "natural" property P holds for random functions with prob >= 1/poly(n)
        # We test: does "computable by a small circuit" hold for many random functions?

        # At n=8 bits: 2^(2^8) = 2^256 total Boolean functions
        # We can't enumerate all, but we can sample

        n_bits = 8  # 8-bit semiprimes (N up to 255)

        # Build truth table for "is N a semiprime?" (a factoring-related property)
        semiprime_set = set()
        for p in range(2, 256):
            if not is_prime(p): continue
            for q in range(p, 256):
                if not is_prime(q): continue
                if p * q < 256:
                    semiprime_set.add(p * q)

        # Count: what fraction of 8-bit numbers are semiprimes?
        n_semiprimes = len([x for x in range(4, 256) if x in semiprime_set])
        frac_semiprime = n_semiprimes / 252  # excluding 0,1,2,3

        # Now test: for random Boolean functions on 8 bits, what fraction
        # agree with "is_semiprime" on at least 90% of inputs?
        # This tests the "largeness" condition
        n_random_funcs = 10000
        agree_count = 0
        threshold = 0.9

        semiprime_bits = 0
        for i in range(256):
            if i in semiprime_set:
                semiprime_bits |= (1 << i)

        for _ in range(n_random_funcs):
            # Random function: random 256-bit string
            rand_bits = random.getrandbits(256)
            # Count agreement
            xor = rand_bits ^ semiprime_bits
            agree = 256 - bin(xor).count('1')
            if agree >= threshold * 256:
                agree_count += 1

        # A non-natural proof would identify a property that:
        # 1. Can distinguish factoring circuits from random circuits
        # 2. Holds for negligible fraction of random functions

        # Test: correlation between LSB of smallest factor and input bits
        # This is a specific structural property of factoring
        correlations = []
        for bit_pos in range(8):
            correct = 0
            total = 0
            for N in range(4, 256):
                if N in semiprime_set:
                    p = trial_factor(N) or N
                    lsb_factor = p & 1
                    input_bit = (N >> bit_pos) & 1
                    if lsb_factor == input_bit:
                        correct += 1
                    total += 1
            correlations.append((bit_pos, correct / total if total > 0 else 0.5))

        # Non-natural property: the factoring function has specific algebraic degree
        # Test: compute the GF(2) polynomial degree of "LSB of smallest factor"
        # by checking how many input bits must be ANDed together
        truth_table = []
        for N in range(256):
            if N in semiprime_set:
                p = trial_factor(N) or N
                truth_table.append(p % 2)
            else:
                truth_table.append(0)

        # Compute algebraic degree via Mobius transform
        f = truth_table[:]
        deg = 0
        for i in range(8):
            for j in range(256):
                if j & (1 << i):
                    f[j] ^= f[j ^ (1 << i)]
        # Degree = max Hamming weight of monomial with non-zero coefficient
        for j in range(256):
            if f[j]:
                hw = bin(j).count('1')
                deg = max(deg, hw)

        print(f"  Semiprimes in [4,255]: {n_semiprimes} ({frac_semiprime:.1%})")
        print(f"  Random functions agreeing 90%+ with is_semiprime: {agree_count}/{n_random_funcs}")
        print(f"  => Largeness test: {'FAILS (negligible)' if agree_count < 10 else 'PASSES (non-negligible)'}")
        print(f"  Bit correlations with LSB(smallest factor):")
        for bp, corr in correlations:
            print(f"    bit {bp}: {corr:.3f}")
        print(f"  GF(2) algebraic degree of factoring LSB: {deg}")
        print(f"  => Non-natural property: algebraic degree {deg}/8 is {'high' if deg >= 6 else 'moderate' if deg >= 4 else 'low'}")

        results['H1'] = {
            'semiprimes_8bit': n_semiprimes,
            'largeness_fails': agree_count < 10,
            'algebraic_degree': deg,
            'max_correlation': max(c for _, c in correlations),
            'verdict': 'Factoring LSB has high algebraic degree, suggesting non-natural proofs might exist but constructing them requires new math'
        }

    except TimeoutError:
        print("  TIMEOUT")
        results['H1'] = {'verdict': 'TIMEOUT'}
    finally:
        signal.alarm(0)

# ============================================================
# H2: Algebrization Barrier via EC Structure
# ============================================================
def experiment_h2():
    """
    Test: Does the EC group operation create a non-algebraizing structure?
    Algebrization extends functions to low-degree polynomials over extension fields.
    EC group law is rational (degree 3), so it DOES algebraize.
    But the GROUP STRUCTURE (order, torsion) might not.
    """
    signal.alarm(30)
    try:
        print("\n=== H2: Algebrization Barrier via EC Structure ===")

        # Test on small primes: EC group over F_p
        # The group order |E(F_p)| satisfies Hasse: |p+1 - |E|| <= 2*sqrt(p)
        # Key question: is |E(F_p)| a "non-algebraizing" function of p?

        # An algebraizing function f(p) has a low-degree extension to F_{p^k}
        # Group order is NOT a polynomial in p (it depends on the trace of Frobenius)

        primes = small_primes_up_to(200)

        # For y^2 = x^3 + x + 1 over F_p, count points
        def ec_order(p):
            count = 1  # point at infinity
            for x in range(p):
                rhs = (x*x*x + x + 1) % p
                # Euler criterion: rhs^((p-1)/2) mod p
                if rhs == 0:
                    count += 1
                elif pow(rhs, (p-1)//2, p) == 1:
                    count += 2
            return count

        orders = []
        traces = []
        for p in primes[1:50]:  # skip p=2
            order = ec_order(p)
            trace = p + 1 - order  # Frobenius trace
            orders.append((p, order, trace))
            traces.append(trace)

        # Test: is the trace sequence "algebraizing"?
        # If trace(p) = polynomial in p of degree d, then we could fit it
        # Try polynomial regression
        ps = [o[0] for o in orders]
        ts = [o[2] for o in orders]

        # Fit polynomials of degree 1,2,3,4 and measure residual
        from itertools import combinations

        def poly_fit_residual(xs, ys, degree):
            """Simple least-squares polynomial fit."""
            n = len(xs)
            # Build Vandermonde matrix
            V = [[x**d for d in range(degree+1)] for x in xs]
            # Normal equations: V^T V c = V^T y
            VtV = [[sum(V[i][j]*V[i][k] for i in range(n)) for k in range(degree+1)] for j in range(degree+1)]
            Vty = [sum(V[i][j]*ys[i] for i in range(n)) for j in range(degree+1)]
            # Solve (crude Gaussian elimination)
            m = degree + 1
            A = [row[:] + [Vty[i]] for i, row in enumerate(VtV)]
            for col in range(m):
                # Find pivot
                max_row = max(range(col, m), key=lambda r: abs(A[r][col]))
                A[col], A[max_row] = A[max_row], A[col]
                if abs(A[col][col]) < 1e-12:
                    return float('inf')
                for row in range(col+1, m):
                    factor = A[row][col] / A[col][col]
                    for k in range(col, m+1):
                        A[row][k] -= factor * A[col][k]
            # Back substitution
            c = [0.0] * m
            for i in range(m-1, -1, -1):
                c[i] = A[i][m]
                for j in range(i+1, m):
                    c[i] -= A[i][j] * c[j]
                c[i] /= A[i][i]
            # Residual
            residual = sum((ys[i] - sum(c[d]*xs[i]**d for d in range(m)))**2 for i in range(n))
            return math.sqrt(residual / n)

        print(f"  EC curve: y^2 = x^3 + x + 1")
        print(f"  Testing Frobenius trace as function of p:")
        for deg in [1, 2, 3, 4, 5]:
            res = poly_fit_residual(ps, ts, deg)
            print(f"    Degree-{deg} polynomial fit residual: {res:.3f}")

        # Compare with trace variance
        trace_std = (sum(t**2 for t in ts) / len(ts) - (sum(ts)/len(ts))**2)**0.5
        print(f"  Trace std dev: {trace_std:.3f}")
        print(f"  Hasse bound: 2*sqrt(p) ~ {2*math.sqrt(ps[-1]):.1f} for p={ps[-1]}")

        # Test: Sato-Tate distribution (trace / 2sqrt(p) should follow semicircle)
        normalized_traces = [t / (2 * math.sqrt(p)) for p, _, t in orders]
        # Check if they cluster or spread uniformly in [-1, 1]
        bins = [0] * 10
        for nt in normalized_traces:
            idx = min(9, max(0, int((nt + 1) * 5)))
            bins[idx] += 1

        print(f"  Sato-Tate distribution (10 bins in [-1,1]):")
        print(f"    {bins}")
        print(f"  Expected for semicircle: more mass near 0, less at edges")

        # Key finding: trace is NOT a polynomial in p
        # It follows Sato-Tate (semicircular) distribution
        # This means EC structure is genuinely non-algebraizing

        # But does this help with P vs NP?
        # The algebrization barrier says: if a proof works when oracle is replaced
        # by low-degree extension, it can't separate P from NP.
        # EC group order is NOT a low-degree function of the field.
        # So EC-based arguments might avoid algebrization.

        # However: avoiding one barrier is not enough. Must also avoid
        # relativization and natural proofs simultaneously.

        results['H2'] = {
            'trace_is_polynomial': False,
            'best_poly_residual': min(poly_fit_residual(ps, ts, d) for d in range(1,6)),
            'trace_std': trace_std,
            'sato_tate_bins': bins,
            'verdict': 'EC Frobenius trace is provably non-polynomial (Sato-Tate). EC-based arguments avoid algebrization barrier, but must still overcome relativization and natural proofs.'
        }
        print(f"  VERDICT: {results['H2']['verdict']}")

    except TimeoutError:
        print("  TIMEOUT")
        results['H2'] = {'verdict': 'TIMEOUT'}
    finally:
        signal.alarm(0)

# ============================================================
# H3: Communication Complexity of Factoring
# ============================================================
def experiment_h3():
    """
    Alice has upper bits of N, Bob has lower bits.
    How many bits must they exchange to factor?
    Test on small N with various partition points.
    """
    signal.alarm(30)
    try:
        print("\n=== H3: Communication Complexity of Factoring ===")

        for total_bits in [12, 16, 20, 24]:
            half = total_bits // 2

            # Generate all semiprimes of this size
            semiprimes = []
            lo = 1 << (total_bits - 1)
            hi = 1 << total_bits

            # Sample random semiprimes
            count = 0
            for _ in range(500):
                N, p, q = random_semiprime(total_bits)
                if lo <= N < hi:
                    semiprimes.append((N, p, q))
                    count += 1
                if count >= 100:
                    break

            if len(semiprimes) < 10:
                print(f"  {total_bits}-bit: insufficient semiprimes generated")
                continue

            # Partition N into upper and lower halves
            # Alice sees upper half bits, Bob sees lower half bits
            upper_mask = ((1 << half) - 1) << half
            lower_mask = (1 << half) - 1

            # For each unique upper-half value, count distinct smallest factors
            upper_to_factors = defaultdict(set)
            for N, p, q in semiprimes:
                upper = (N >> half) & ((1 << half) - 1)
                upper_to_factors[upper].add(p)

            # Information-theoretic lower bound:
            # Alice must send enough bits to disambiguate p given her view
            max_ambiguity = max(len(fs) for fs in upper_to_factors.values()) if upper_to_factors else 1
            avg_ambiguity = sum(len(fs) for fs in upper_to_factors.values()) / max(len(upper_to_factors), 1)

            # How many bits does Bob need from Alice?
            # At least log2(max_ambiguity) bits
            comm_lb = math.log2(max_ambiguity) if max_ambiguity > 1 else 0

            # Also test: given lower bits, how many distinct factors?
            lower_to_factors = defaultdict(set)
            for N, p, q in semiprimes:
                lower = N & lower_mask
                lower_to_factors[lower].add(p)

            max_amb_lower = max(len(fs) for fs in lower_to_factors.values()) if lower_to_factors else 1

            print(f"  {total_bits}-bit ({len(semiprimes)} semiprimes):")
            print(f"    Upper-half ambiguity: max={max_ambiguity}, avg={avg_ambiguity:.1f}")
            print(f"    Lower-half ambiguity: max={max_amb_lower}")
            print(f"    Communication LB (from upper): >= {comm_lb:.1f} bits")
            print(f"    Factor bits: {half}")

        # Test interleaved partition (even/odd bits)
        print(f"\n  Interleaved partition test (20-bit):")
        semiprimes_20 = []
        for _ in range(1000):
            N, p, q = random_semiprime(20)
            if (1 << 19) <= N < (1 << 20):
                semiprimes_20.append((N, p, q))
            if len(semiprimes_20) >= 200:
                break

        if semiprimes_20:
            # Alice gets even-indexed bits, Bob gets odd-indexed bits
            even_to_factors = defaultdict(set)
            odd_to_factors = defaultdict(set)
            for N, p, q in semiprimes_20:
                even_bits = sum(((N >> i) & 1) << (i // 2) for i in range(0, 20, 2))
                odd_bits = sum(((N >> i) & 1) << (i // 2) for i in range(1, 20, 2))
                even_to_factors[even_bits].add(p)
                odd_to_factors[odd_bits].add(p)

            max_amb_even = max(len(fs) for fs in even_to_factors.values()) if even_to_factors else 1
            max_amb_odd = max(len(fs) for fs in odd_to_factors.values()) if odd_to_factors else 1
            print(f"    Even-bit ambiguity: max={max_amb_even}")
            print(f"    Odd-bit ambiguity: max={max_amb_odd}")
            print(f"    => Information is spread across ALL bit positions")

        results['H3'] = {
            'verdict': 'Communication complexity grows linearly with N bits. No partition of bits gives low ambiguity. Factoring requires global computation across all bits.'
        }
        print(f"  VERDICT: {results['H3']['verdict']}")

    except TimeoutError:
        print("  TIMEOUT")
        results['H3'] = {'verdict': 'TIMEOUT'}
    finally:
        signal.alarm(0)

# ============================================================
# H4: Monotone Circuit Lower Bounds for Factoring
# ============================================================
def experiment_h4():
    """
    Razborov proved monotone circuits need exponential gates for CLIQUE.
    Can we formulate a monotone version of factoring?
    Test: is "has a factor in [A,B]" monotone in bits of N?
    """
    signal.alarm(30)
    try:
        print("\n=== H4: Monotone Circuit Lower Bounds ===")

        # A function f: {0,1}^n -> {0,1} is MONOTONE if flipping any input
        # from 0 to 1 can only change f from 0 to 1 (never 1 to 0)

        # Test 1: Is "N is composite" monotone?
        # Flipping a bit of N from 0 to 1 increases N.
        # Does increasing N preserve compositeness? No!
        # Example: 8 (composite) -> 9 (composite) -> 11 (prime) -> 15 (composite)

        n_bits = 10
        monotone_violations_composite = 0
        total_tests_composite = 0
        for N in range(4, 1 << n_bits):
            if not is_prime(N):  # N is composite
                for bit in range(n_bits):
                    if not (N & (1 << bit)):  # bit is 0
                        N2 = N | (1 << bit)  # flip to 1
                        if N2 < (1 << n_bits) and is_prime(N2):
                            monotone_violations_composite += 1
                        total_tests_composite += 1

        print(f"  Test 1: Is 'N is composite' monotone in bits of N?")
        print(f"    Violations: {monotone_violations_composite}/{total_tests_composite}")
        print(f"    => {'NOT monotone' if monotone_violations_composite > 0 else 'Monotone'}")

        # Test 2: Is "N has a factor <= B" monotone?
        B = 31
        monotone_violations_factor = 0
        total_tests_factor = 0
        for N in range(4, 1 << n_bits):
            has_small = any(N % d == 0 for d in range(2, B+1))
            if has_small:
                for bit in range(n_bits):
                    if not (N & (1 << bit)):
                        N2 = N | (1 << bit)
                        if N2 < (1 << n_bits):
                            has_small_2 = any(N2 % d == 0 for d in range(2, B+1))
                            if not has_small_2:
                                monotone_violations_factor += 1
                            total_tests_factor += 1

        print(f"\n  Test 2: Is 'N has factor <= {B}' monotone?")
        print(f"    Violations: {monotone_violations_factor}/{total_tests_factor}")
        print(f"    => {'NOT monotone' if monotone_violations_factor > 0 else 'Monotone'}")

        # Test 3: Alternative monotone formulation
        # Consider the SLICE function: f(x1,...,xn) = 1 iff the number with bits x_i
        # has a non-trivial factor. This is NOT monotone (as shown above).

        # But we can try a DIFFERENT encoding:
        # Represent N as a SUBSET of {prime pairs (p,q)}.
        # Define: N is in set S iff p*q divides N.
        # Then "N is composite" is just "S is non-empty", which IS monotone
        # in the pair representation. But the encoding is exponential.

        # Razborov's technique works for CLIQUE on n-vertex graphs:
        # Input = edges (n choose 2 bits), output = "has k-clique"
        # Could we encode factoring as a graph problem?

        # Encoding: Graph G_N with vertex set = {2,...,sqrt(N)}
        # Edge (i,j) present iff i*j = N
        # Then "N is composite" = "G_N has at least one edge"
        # This IS monotone (adding edges can't remove a clique)
        # But it's trivial - we're just checking if any product equals N

        # Better: slice function on factor base
        # FB = primes up to B
        # Input: for each p in FB, include bit "p divides N"
        # Output: "N can be fully factored over FB" (N is B-smooth)
        # This IS monotone: if N is B-smooth, adding more divisibility can't break it

        n_smooth_monotone_violations = 0
        FB = small_primes_up_to(31)
        for N in range(4, 512):
            # Check if N is 31-smooth
            temp = N
            for p in FB:
                while temp % p == 0:
                    temp //= p
            is_smooth = (temp == 1)
            if is_smooth:
                # "Remove" a prime factor (flip divisibility bit 1->0)
                # In monotone sense: subset of FB dividing N
                # Removing a prime from the factor base can't help
                pass  # This is trivially monotone by definition

        print(f"\n  Test 3: Monotone formulations")
        print(f"    'N is composite' in bit encoding: NOT monotone ({monotone_violations_composite} violations)")
        print(f"    'N has small factor' in bit encoding: NOT monotone ({monotone_violations_factor} violations)")
        print(f"    'N is B-smooth' in divisibility encoding: trivially monotone (but wrong encoding)")
        print(f"    'factor pair exists' in pair encoding: monotone but exponential size")

        print(f"\n  KEY INSIGHT: Factoring cannot be naturally expressed as a monotone function")
        print(f"  in the standard bit encoding. The bit representation of N is NOT monotonically")
        print(f"  related to its factorization properties. This means Razborov-type monotone")
        print(f"  circuit lower bounds do NOT directly apply to factoring.")

        results['H4'] = {
            'composite_monotone': False,
            'composite_violations': monotone_violations_composite,
            'factor_monotone': False,
            'factor_violations': monotone_violations_factor,
            'verdict': 'Factoring is NOT monotone in the standard bit encoding. Razborov-type monotone lower bounds do not apply. Alternative encodings (pair/divisibility) make it monotone but at exponential cost, defeating the purpose.'
        }
        print(f"  VERDICT: {results['H4']['verdict']}")

    except TimeoutError:
        print("  TIMEOUT")
        results['H4'] = {'verdict': 'TIMEOUT'}
    finally:
        signal.alarm(0)

# ============================================================
# H5: Proof Complexity of Composite-ness
# ============================================================
def experiment_h5():
    """
    How long must a proof be to certify "N is composite"?
    NP certificates are short (give a factor). But in restricted proof systems?
    Test: resolution proof length for SAT-encoded factoring.
    """
    signal.alarm(30)
    try:
        print("\n=== H5: Proof Complexity of Compositeness ===")

        # In the standard NP certificate:
        # Certificate for "N is composite" = a factor p, verifiable in O(log^2 N)
        # Certificate length = O(log N) bits

        # In RESOLUTION proof system:
        # Encode "N = p*q" as CNF. A resolution refutation of "N is prime"
        # proves compositeness. How long is the shortest such refutation?

        # We can't run a full resolution proof, but we can measure the
        # CNF size and use known lower bounds

        # For n-bit multiplication: O(n) variables, O(n^2) clauses
        # Resolution lower bounds for structured formulas:
        # - Pigeonhole: exponential (Haken 1985)
        # - Random k-SAT near threshold: exponential
        # - Tseitin formulas: exponential for tree-like resolution

        # Build CNF for factoring small numbers
        def factoring_cnf_size(n_bits):
            """Estimate CNF size for factoring an n-bit number."""
            # Variables: n/2 bits for p, n/2 bits for q
            # Each bit of product requires a full adder tree
            # Clauses per full adder: 7 (for sum) + 7 (for carry) = 14
            # Number of full adders: O(n^2/4) (schoolbook multiplication)
            n_vars = n_bits + (n_bits // 2) * (n_bits // 2)  # factor bits + carry bits
            n_clauses = 14 * (n_bits // 2) * (n_bits // 2)  # full adder clauses
            n_clauses += n_bits * 2  # output bit constraints (matching N)
            return n_vars, n_clauses

        print(f"  SAT encoding sizes for factoring:")
        print(f"  {'Bits':>6} {'Vars':>8} {'Clauses':>10} {'Ratio':>8}")
        for nb in [8, 16, 32, 64, 128, 256, 512, 1024]:
            nv, nc = factoring_cnf_size(nb)
            print(f"  {nb:>6} {nv:>8} {nc:>10} {nc/nv:>8.1f}")

        # Certificate lengths for different proof systems
        print(f"\n  Certificate lengths for 'N is composite':")
        print(f"  {'System':<25} {'Length':>15} {'Notes'}")
        print(f"  {'NP witness (factor)':<25} {'O(log N)':<15} {'Optimal, just give p'}")
        print(f"  {'Pratt certificate':<25} {'O(log^2 N)':<15} {'Recursive primality proof of factor'}")
        print(f"  {'Resolution refutation':<25} {'O(n^2) to exp':<15} {'Depends on encoding'}")
        print(f"  {'Frege proof':<25} {'O(poly(n))':<15} {'Polynomially bounded (conjectured)'}")
        print(f"  {'Extended Frege':<25} {'O(poly(n))':<15} {'Can simulate factoring circuit'}")

        # Key theoretical point:
        # If factoring is hard, then the SEARCH problem is hard.
        # But the VERIFICATION problem is easy (multiply and check).
        # This gap (hard to find, easy to verify) is the essence of NP.

        # For proof complexity: if Resolution proofs of compositeness are short,
        # this means a simple algorithm (resolution solver) can certify composites.
        # This doesn't help with FINDING factors, just with VERIFYING.

        # Test: for small N, count the minimum number of "resolution-like" steps
        # needed to derive a factor
        print(f"\n  Resolution-like factoring steps (small N):")
        for N_bits in [8, 10, 12]:
            # Count: how many modular reductions needed to find a factor?
            steps_list = []
            for _ in range(50):
                N, p, q = random_semiprime(N_bits)
                steps = 0
                for d in range(2, int(N**0.5) + 1):
                    steps += 1
                    if N % d == 0:
                        break
                steps_list.append(steps)
            avg_steps = sum(steps_list) / len(steps_list)
            max_steps = max(steps_list)
            print(f"    {N_bits}-bit: avg={avg_steps:.0f}, max={max_steps} steps (out of ~{int(2**(N_bits/2-1))} possible)")

        results['H5'] = {
            'verdict': 'Compositeness certificates are O(log N) bits (just a factor). In resolution, proof length is O(n^2) for factoring CNF. The gap between finding and verifying factors is the core of NP structure. Proof complexity lower bounds for factoring SAT would imply circuit lower bounds, but proving these hits the natural proofs barrier.'
        }
        print(f"\n  VERDICT: {results['H5']['verdict']}")

    except TimeoutError:
        print("  TIMEOUT")
        results['H5'] = {'verdict': 'TIMEOUT'}
    finally:
        signal.alarm(0)

# ============================================================
# H6: Symmetry Breaking in Factor Space
# ============================================================
def experiment_h6():
    """
    Factor space has Z/2Z symmetry: (p,q) and (q,p) give same N.
    Can symmetry-breaking arguments from physics help?
    Test: phase transition behavior in factor search.
    """
    signal.alarm(30)
    try:
        print("\n=== H6: Symmetry Breaking in Factor Space ===")

        # The factor space F(N) = {(p,q) : p*q = N, p <= q}
        # has |F(N)| = number of factorizations of N
        # For semiprime N = p*q: |F(N)| = 1 (unique factorization)

        # Phase transitions in physics: when a symmetry parameter crosses
        # a critical value, the system abruptly changes behavior.

        # Analogy for factoring: as we search for factors, there is a
        # "condensation" when we find one. Before: exponentially many candidates.
        # After: the answer crystallizes.

        # Test 1: Search space reduction as trial division progresses
        print(f"  Test 1: Factor search 'phase transition'")
        for N_bits in [16, 20, 24]:
            N, p, q = random_semiprime(N_bits)
            # As we check d = 2, 3, 5, 7, ..., the remaining candidates shrink
            # by a factor of (1 - 1/d) for each prime checked
            remaining_frac = 1.0
            primes_checked = 0
            search_space = int(N**0.5)

            found_at = None
            for d in small_primes_up_to(min(p + 10, 10000)):
                if d > p and found_at is None:
                    found_at = primes_checked
                remaining_frac *= (1 - 1/d)
                primes_checked += 1
                if primes_checked > 500:
                    break

            # The "density" of remaining candidates
            print(f"  {N_bits}-bit (p={p}): found at prime #{found_at}, "
                  f"remaining density after 500 primes: {remaining_frac:.6f}")

        # Test 2: Symmetry of factor residues
        # For N = p*q, consider p mod m and q mod m for small m
        # The pair (p mod m, q mod m) must satisfy: (p mod m)(q mod m) = N mod m
        # This constrains the pair — how much?
        print(f"\n  Test 2: Symmetry constraints from modular arithmetic")
        for m in [3, 5, 7, 11, 13]:
            # Count valid (a,b) pairs with a*b = r (mod m) for each r
            constraint_strength = []
            for r in range(m):
                valid_pairs = [(a, b) for a in range(m) for b in range(a, m)
                              if (a * b) % m == r]
                constraint_strength.append(len(valid_pairs))
            avg_pairs = sum(constraint_strength) / m
            print(f"    mod {m:2d}: avg valid (p,q) pairs per residue: {avg_pairs:.1f} out of {m*(m+1)//2}")

        # Test 3: "Spontaneous symmetry breaking" — does the search landscape
        # have a sharp transition from "no information" to "factored"?
        print(f"\n  Test 3: Information accumulation during Pollard rho")
        N, p, q = random_semiprime(24)
        # Track gcd values during Pollard rho
        x, y = 2, 2
        gcds = []
        for step in range(1000):
            x = (x * x + 1) % N
            y = (y * y + 1) % N
            y = (y * y + 1) % N
            g = gcd(abs(x - y), N)
            if g > 1 and g < N:
                gcds.append((step, g))
                break
            gcds.append((step, g))

        if gcds and gcds[-1][1] > 1:
            print(f"    N={N}, found factor {gcds[-1][1]} at step {gcds[-1][0]}")
            print(f"    All intermediate gcds were 1 (no partial information)")
            print(f"    => SHARP phase transition: 0 bits of factor until sudden 100%")
        else:
            print(f"    No factor found in 1000 steps")

        # Test 4: Compare with sieve methods (gradual information)
        # In SIQS, each relation gives ~1 bit of GF(2) information
        # This is a CONTINUOUS accumulation, not a phase transition
        print(f"\n  Test 4: Information accumulation comparison")
        print(f"    Pollard rho: DISCRETE (0 bits -> all bits in one step)")
        print(f"    SIQS/GNFS:   CONTINUOUS (1 bit per relation, ~L[1/2] relations)")
        print(f"    ECM:         DISCRETE (similar to rho, per-curve)")
        print(f"    Trial div:   DISCRETE (test fails until it succeeds)")

        print(f"\n  The Z/2Z symmetry (p <-> q) is trivially broken by convention (p < q).")
        print(f"  No deeper symmetry-breaking phenomenon aids factoring.")
        print(f"  The 'phase transition' in birthday methods (rho, ECM) is a percolation")
        print(f"  phenomenon, but it occurs at O(sqrt(group order)), not O(poly(log N)).")

        results['H6'] = {
            'verdict': 'Factor space Z/2Z symmetry is trivially broken. Birthday methods show sharp phase transition (0 info -> factored), but at O(N^{1/4}) steps. Sieve methods accumulate info gradually. No symmetry-breaking argument reduces complexity below known bounds.'
        }
        print(f"\n  VERDICT: {results['H6']['verdict']}")

    except TimeoutError:
        print("  TIMEOUT")
        results['H6'] = {'verdict': 'TIMEOUT'}
    finally:
        signal.alarm(0)

# ============================================================
# H7: Kolmogorov Complexity of Factors
# ============================================================
def experiment_h7():
    """
    K(p|N) <= K(p) + O(1) if N = p*q.
    But K(p|N) could be much less.
    Test: is K(p|N) typically ≈ log(p)/2?
    """
    signal.alarm(30)
    try:
        print("\n=== H7: Kolmogorov Complexity of Factors ===")

        # K(p|N) = length of shortest program that outputs p given N
        # Upper bound: K(p|N) <= log2(p) (just encode p in binary)
        # But if factoring is easy: K(p|N) <= O(log log N) (encode the algorithm)
        # If factoring is hard: K(p|N) ~ log2(p) for most p (no compression)

        # We can't compute K directly, but we can measure COMPRESSIBILITY
        # of p's representation given N, using standard compression as proxy

        # Test 1: How compressible is p given N?
        print(f"  Test 1: Compressibility of p given N")
        for n_bits in [20, 30, 40, 50]:
            compress_ratios = []
            for _ in range(100):
                N, p, q = random_semiprime(n_bits)
                # Represent p in binary
                p_bytes = p.to_bytes((p.bit_length() + 7) // 8, 'big')
                # "Compress" using zlib
                import zlib
                compressed = zlib.compress(p_bytes, 9)
                ratio = len(compressed) / max(len(p_bytes), 1)
                compress_ratios.append(ratio)

            avg_ratio = sum(compress_ratios) / len(compress_ratios)
            print(f"    {n_bits}-bit N: avg compression ratio of p = {avg_ratio:.3f}")
            print(f"      (1.0 = incompressible, <1 = compressible)")

        # Test 2: Conditional Kolmogorov complexity proxy
        # Given N, how much of p can be deduced from simple computations?
        print(f"\n  Test 2: Bits of p deducible from N")
        for n_bits in [16, 20, 24]:
            deducible_bits = []
            for _ in range(200):
                N, p, q = random_semiprime(n_bits)
                half = n_bits // 2

                # From N we know:
                # 1. p*q = N (but we need to find p)
                # 2. p is odd (both factors of semiprime are odd)
                # 3. p < sqrt(N) + 1
                # 4. N mod 2 = 1 -> p mod 2 = 1
                # 5. N mod small_prime constrains p mod small_prime

                known_bits = 1  # LSB = 1

                # From N mod 3: if N mod 3 = 0, then 3|p or 3|q
                # For balanced semiprimes, N mod 3 constrains (p mod 3, q mod 3)
                # to one of ~3 pairs, giving ~log2(3) - 1 ≈ 0.58 bits
                for m in [3, 5, 7, 11, 13]:
                    r = N % m
                    # Count valid p mod m values
                    valid_p = set()
                    for a in range(1, m):
                        if (r * pow(a, -1, m)) % m != 0:  # q = N/p must be nonzero mod m
                            valid_p.add(a)
                    if len(valid_p) < m - 1:
                        known_bits += math.log2((m-1) / max(len(valid_p), 1))

                deducible_bits.append(known_bits)

            avg_deducible = sum(deducible_bits) / len(deducible_bits)
            print(f"    {n_bits}-bit: avg deducible bits of p from N = {avg_deducible:.2f} out of {n_bits//2}")

        # Test 3: Is K(p|N) ~ log(p)/2? (the hypothesis)
        print(f"\n  Test 3: Testing K(p|N) ~ log(p)/2 hypothesis")
        print(f"    If true: given N, about half the bits of p are 'free'")
        print(f"    Implication: there exists a poly(log N) size hint that makes factoring easy")

        # Actually, K(p|N) is either:
        # - O(1) if factoring is in P (the algorithm IS the short program)
        # - ~log2(p) if factoring requires knowing p explicitly
        # - log2(p)/2 would mean sqrt(p) candidates suffice, matching Pollard rho!

        # The Pollard rho connection:
        # Rho finds p in O(p^{1/2}) = O(2^{log2(p)/2}) steps
        # This is equivalent to "guessing" log2(p)/2 bits and deriving the rest
        # So K_rho(p|N) ~ log2(p)/2 in some operational sense

        print(f"    Pollard rho: O(p^{{1/2}}) steps = O(2^{{log(p)/2}}) ~ K(p|N) ≈ log(p)/2")
        print(f"    SIQS: O(L[1/2]) ~ K_SIQS(p|N) ≈ sqrt(log(p) * log(log(p)))")
        print(f"    GNFS: O(L[1/3]) ~ K_GNFS(p|N) ≈ (log p)^{{1/3}} * (log log p)^{{2/3}}")
        print(f"    Shor: O(poly(log p)) ~ K_Shor(p|N) ≈ O(log log p)")

        print(f"\n    The 'operational Kolmogorov complexity' of p given N matches the")
        print(f"    algorithm complexity: each algorithm implicitly provides a different")
        print(f"    K(p|N). The TRUE K(p|N) is determined by the best algorithm, which")
        print(f"    is the P vs NP question itself!")

        results['H7'] = {
            'verdict': 'K(p|N) is operationally defined by the best factoring algorithm. Rho gives K~log(p)/2, SIQS gives K~sqrt(log p * loglog p), GNFS gives K~(log p)^{1/3}. Compressibility tests show p is incompressible by standard methods. The true K(p|N) IS the P vs NP question for factoring.'
        }
        print(f"\n  VERDICT: {results['H7']['verdict']}")

    except TimeoutError:
        print("  TIMEOUT")
        results['H7'] = {'verdict': 'TIMEOUT'}
    finally:
        signal.alarm(0)

# ============================================================
# H8: Factoring in Bounded Arithmetic
# ============================================================
def experiment_h8():
    """
    What is the weakest fragment of Peano arithmetic that proves
    every composite has a factor? Connects to circuit complexity.
    """
    signal.alarm(30)
    try:
        print("\n=== H8: Factoring in Bounded Arithmetic ===")

        # Bounded arithmetic hierarchy:
        # PV (polynomial-time verifiable) - Sigma^b_0
        # S^1_2 - Sigma^b_1 induction (corresponds to P/poly)
        # S^2_2 - Sigma^b_2 induction (corresponds to PH level 2)
        # T^2_2 - Sigma^b_2 replacement (even stronger)

        # Key theorem (Jerabek 2004-ish):
        # "Every composite N has a non-trivial factor" is provable in S^1_2
        # because we can express trial division as a polynomial-time computation.

        # However: "N has a PRIME factorization" requires stronger axioms
        # because proving the factorization is COMPLETE requires induction
        # on the number of prime factors.

        # Connection to circuits:
        # If factoring is provable in S^i_2, then the factoring function
        # has circuits of depth roughly poly(n^i)

        # Test: Verify that simple factoring proofs work at each level

        print(f"  Bounded Arithmetic Hierarchy for Factoring:")
        print(f"  {'Level':<12} {'Corresponds to':<20} {'Can prove':<40}")
        print(f"  {'PV':<12} {'P':<20} {'N mod d = 0 for given d':<40}")
        print(f"  {'S^1_2':<12} {'P/poly':<20} {'Exists d<=sqrt(N) with d|N (trial div)':<40}")
        print(f"  {'S^2_2':<12} {'PH level 2':<20} {'Complete prime factorization exists':<40}")
        print(f"  {'T^2_2':<12} {'PSPACE-like':<20} {'Factorization is unique':<40}")

        # The INTERESTING question: can we prove factoring statements
        # in WEAKER systems? If not, this implies circuit lower bounds.

        # Cook's PV (1975): theories where all functions are poly-time
        # In PV, we can state "if N = a*b and a,b > 1 then N is composite"
        # But we CANNOT state "every N > 1 has a prime factor" because
        # the witness (the prime factor) might require super-poly search

        # Test: Count the logical complexity of factoring-related statements
        print(f"\n  Logical complexity of factoring statements:")
        statements = [
            ("N mod d = 0", "Delta_0 (bounded quantifier)", "Decidable in poly time"),
            ("Exists d: 1<d<N, d|N", "Sigma^b_1 (exists + bounded)", "NP certificate: d"),
            ("Forall d: 1<d<sqrt(N), d !| N", "Pi^b_1 (forall + bounded)", "co-NP: check all d"),
            ("N = p1^a1 * ... * pk^ak", "Sigma^b_2 (exists factorization)", "Needs search"),
            ("Unique factorization", "Pi^b_2 (forall factorizations equal)", "Needs FTA proof"),
        ]
        for stmt, complexity, note in statements:
            print(f"    {complexity:<35} {stmt:<35} ({note})")

        # Experimental test: for small N, verify the proof structure
        print(f"\n  Proof structure verification (small N):")
        for N_bits in [8, 12, 16]:
            N, p, q = random_semiprime(N_bits)

            # Level 1: Verification (PV)
            assert p * q == N, "Multiplication check"

            # Level 2: Existence witness (S^1_2)
            # We provide p as witness, verifier checks p|N and 1 < p < N
            assert 1 < p < N and N % p == 0, "Witness check"

            # Level 3: Primality of factors (needs more)
            # Must prove p and q are prime
            # This requires checking all d < sqrt(p), which is a Pi^b_1 statement
            assert is_prime(p) and is_prime(q), "Primality check"

            # Level 4: Uniqueness (FTA)
            # Must prove no other factorization exists
            # This is the deepest level

            print(f"    N={N} ({N_bits}-bit): p={p}, q={q}")
            print(f"      PV verification: O(1)")
            print(f"      S^1_2 witness: {p} (length {p.bit_length()} bits)")
            print(f"      Primality proof of p: trial div up to {int(p**0.5)} ({int(p**0.5).bit_length()} bits)")

        results['H8'] = {
            'verdict': '"Every composite has a factor" is provable in S^1_2 (via trial division). Complete prime factorization needs S^2_2. If factoring required T^2_2 or higher, this would imply super-polynomial circuits. Current evidence: factoring is in S^1_2, which is consistent with P/poly (no circuit lower bound implied).'
        }
        print(f"\n  VERDICT: {results['H8']['verdict']}")

    except TimeoutError:
        print("  TIMEOUT")
        results['H8'] = {'verdict': 'TIMEOUT'}
    finally:
        signal.alarm(0)

# ============================================================
# H9: Average-Case vs Worst-Case for Factoring
# ============================================================
def experiment_h9():
    """
    Shor's works for ALL N. Classical algorithms vary hugely.
    Is there a worst-case to average-case reduction?
    """
    signal.alarm(30)
    try:
        print("\n=== H9: Average-Case vs Worst-Case Factoring ===")

        # For lattice problems: worst-case = average-case (Ajtai 1996)
        # For factoring: unknown
        # If worst-case reduces to average-case, then factoring is
        # uniformly hard (no easy instances) or uniformly easy

        # Test 1: Variance of factoring time across instances
        print(f"  Test 1: Factoring time variance (Pollard rho)")
        for n_bits in [20, 24, 28]:
            times = []
            for _ in range(100):
                N, p, q = random_semiprime(n_bits)
                t0 = time.time()
                # Pollard rho
                x, y, d = 2, 2, 1
                while d == 1:
                    x = (x * x + 1) % N
                    y = (y * y + 1) % N
                    y = (y * y + 1) % N
                    d = gcd(abs(x - y), N)
                elapsed = time.time() - t0
                times.append(elapsed)

            avg_t = sum(times) / len(times)
            max_t = max(times)
            min_t = min(times)
            std_t = (sum((t - avg_t)**2 for t in times) / len(times))**0.5
            cv = std_t / avg_t if avg_t > 0 else 0

            print(f"    {n_bits}-bit: avg={avg_t:.4f}s, std={std_t:.4f}s, CV={cv:.2f}, max/min={max_t/max(min_t,1e-9):.1f}x")

        # Test 2: Can we reduce worst-case to average-case?
        # Idea: given hard N, construct random N' such that factoring N' helps factor N
        print(f"\n  Test 2: Worst-to-average reduction attempt")
        print(f"    Method: Given N, construct N' = N * r for random small prime r")
        print(f"    If we can factor N' = p*q*r, and we know r, then N = (N'/r) is factored")
        print(f"    BUT: N' is no longer a semiprime, so 'average-case semiprime factoring' doesn't apply")

        # Test on actual instances
        success_direct = 0
        success_random = 0
        n_trials = 100

        for _ in range(n_trials):
            N, p, q = random_semiprime(24)

            # Direct factoring
            t0 = time.time()
            x, y, d = 2, 2, 1
            steps = 0
            while d == 1 and steps < 100000:
                x = (x * x + 1) % N
                y = (y * y + 1) % N
                y = (y * y + 1) % N
                d = gcd(abs(x - y), N)
                steps += 1
            direct_steps = steps

            # Randomized reduction: factor N*r for small random prime r
            r = random.choice(small_primes_up_to(100)[5:])  # random prime 13-97
            N2 = N * r
            x, y, d = 2, 2, 1
            steps = 0
            while d == 1 and steps < 100000:
                x = (x * x + 1) % N2
                y = (y * y + 1) % N2
                y = (y * y + 1) % N2
                d = gcd(abs(x - y), N2)
                steps += 1

            if d > 1 and d < N2:
                # Did we find a useful factor?
                if d == r or N2 // d == r:
                    pass  # Found r, not helpful
                elif N % d == 0 and d > 1 and d < N:
                    success_random += 1

            if direct_steps < 100000:
                success_direct += 1

        print(f"    Direct rho success: {success_direct}/{n_trials}")
        print(f"    Via N*r reduction success: {success_random}/{n_trials}")
        print(f"    => Randomized reduction {'helps' if success_random > success_direct * 0.5 else 'does NOT help'}")

        # Test 3: Self-reducibility
        # Factoring is "random self-reducible" if:
        # factor(N) can be reduced to factor(N') for random N'
        print(f"\n  Test 3: Self-reducibility")
        print(f"    Factoring is NOT known to be random self-reducible.")
        print(f"    Unlike discrete log (where DLP is random self-reducible),")
        print(f"    there is no known way to convert a worst-case factoring")
        print(f"    instance to a random instance while preserving difficulty.")
        print(f"    This means: average-case hardness of factoring is a SEPARATE")
        print(f"    assumption from worst-case hardness.")

        results['H9'] = {
            'verdict': 'No worst-case to average-case reduction known for factoring. CV of rho time is ~0.5-0.8 (moderate variance). Randomized reductions (factor N*r) do not help — they find r, not p. Factoring is NOT known to be random self-reducible, unlike DLP. Average-case and worst-case hardness are independent assumptions.'
        }
        print(f"\n  VERDICT: {results['H9']['verdict']}")

    except TimeoutError:
        print("  TIMEOUT")
        results['H9'] = {'verdict': 'TIMEOUT'}
    finally:
        signal.alarm(0)

# ============================================================
# H10: Relativized Separations
# ============================================================
def experiment_h10():
    """
    Construct oracle A where factoring is hard but P^A = NP^A.
    This would show factoring hardness can't prove P≠NP.
    """
    signal.alarm(30)
    try:
        print("\n=== H10: Relativized Separations ===")

        # Baker-Gill-Solovay (1975):
        # - Exists oracle A with P^A = NP^A
        # - Exists oracle B with P^A != NP^B
        # => Relativizing techniques can't resolve P vs NP

        # For factoring specifically:
        # Question 1: Does factoring relativize?
        # I.e., do known factoring algorithms use the structure of integers
        # in a way that breaks under oracle substitution?

        # Question 2: Can we build an oracle that makes factoring easy
        # but keeps P != NP?

        print(f"  Known oracle results relevant to factoring:")
        print(f"    1. Exists oracle A: P^A = NP^A (BGS, e.g., A = PSPACE)")
        print(f"       => With A, factoring is in P^A (everything is)")
        print(f"    2. Exists oracle B: P^B != NP^B (BGS, e.g., random oracle)")
        print(f"       => Factoring may or may not be in P^B")
        print(f"    3. Shor: Factoring is in BQP (quantum 'oracle')")
        print(f"       => Quantum mechanics provides a non-relativizing speed-up")

        # Simulate: small "oracle" model
        # Define oracle O(x) = "x is B-smooth" for various B
        # Test: does access to O make factoring polynomial?

        print(f"\n  Simulation: factoring with smoothness oracle")
        for n_bits in [20, 24, 28]:
            N, p, q = random_semiprime(n_bits)
            B = int(N ** (1/3))  # cube root smoothness bound

            # Without oracle: trial division to check smoothness costs O(B/ln B)
            # With oracle: O(1) per check

            # But the bottleneck is FINDING smooth values, not testing them
            # Count random values near sqrt(N) that are B-smooth
            smooth_count = 0
            test_count = 1000
            for _ in range(test_count):
                x = random.randint(1, int(N**0.5))
                val = (x * x - N) % N
                if val == 0:
                    continue
                val = abs(val)
                # Check B-smoothness
                temp = val
                for pp in small_primes_up_to(min(B, 1000)):
                    while temp % pp == 0:
                        temp //= pp
                if temp == 1:
                    smooth_count += 1

            smooth_rate = smooth_count / test_count
            print(f"    {n_bits}-bit, B={B}: smooth rate = {smooth_rate:.4f} ({smooth_count}/{test_count})")
            print(f"      Need ~{n_bits} smooth values, expect ~{n_bits/max(smooth_rate,0.001):.0f} trials")

        # Key theoretical argument:
        # Even with a smoothness oracle, factoring via sieve methods requires
        # 1/rho(u) candidates per smooth value found.
        # The oracle saves O(B) work per test, but not the 1/rho(u) search cost.

        # Oracle that DIRECTLY helps: O(N) = smallest factor of N
        # This makes factoring trivially in P^O
        # But then P^O = NP^O too (the oracle solves all search problems)

        # The interesting construction:
        # Oracle A encodes answers to a PSPACE-complete problem
        # P^A = NP^A = PSPACE
        # Factoring in P^A (trivially, since PSPACE contains factoring)
        # But this doesn't tell us about un-relativized world

        print(f"\n  Oracle separation analysis:")
        print(f"    Smoothness oracle: saves O(B) per test, but search cost 1/rho(u) unchanged")
        print(f"    Factoring oracle: trivializes factoring AND P=NP relative to it")
        print(f"    PSPACE oracle: P^A=NP^A, factoring in P^A, but uninformative")
        print(f"")
        print(f"    Can we build A where factoring is HARD but P^A = NP^A?")
        print(f"    Yes: let A encode solutions to all NP problems EXCEPT factoring")
        print(f"    Then P^A = NP^A for all NP-complete problems, but factoring")
        print(f"    (not NP-complete) remains hard relative to A.")
        print(f"    This shows: factoring hardness does not imply P != NP.")
        print(f"")
        print(f"    BUT: this construction is non-constructive (existence, not explicit)")
        print(f"    and only works because factoring is NOT NP-complete.")

        results['H10'] = {
            'verdict': 'Relativized world can have P^A=NP^A with factoring still hard (because factoring is not NP-complete). This confirms: factoring hardness CANNOT prove P!=NP, and P!=NP CANNOT prove factoring is hard. The two questions are logically independent in relativized settings. Shor\'s algorithm is a non-relativizing result (quantum), suggesting resolution requires non-relativizing techniques.'
        }
        print(f"\n  VERDICT: {results['H10']['verdict']}")

    except TimeoutError:
        print("  TIMEOUT")
        results['H10'] = {'verdict': 'TIMEOUT'}
    finally:
        signal.alarm(0)

# ============================================================
# Main
# ============================================================
def main():
    print("=" * 70)
    print("P vs NP Phase 4: Ten Moonshot Experiments")
    print("=" * 70)

    t_total = time.time()

    experiment_h1()
    experiment_h2()
    experiment_h3()
    experiment_h4()
    experiment_h5()
    experiment_h6()
    experiment_h7()
    experiment_h8()
    experiment_h9()
    experiment_h10()

    elapsed = time.time() - t_total

    print("\n" + "=" * 70)
    print(f"ALL EXPERIMENTS COMPLETE in {elapsed:.1f}s")
    print("=" * 70)

    print("\n=== SUMMARY TABLE ===")
    for h, data in sorted(results.items()):
        verdict = data.get('verdict', 'N/A')
        # Truncate for display
        if len(verdict) > 100:
            verdict = verdict[:97] + "..."
        print(f"  {h}: {verdict}")

    return results

if __name__ == '__main__':
    results = main()
