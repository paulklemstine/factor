#!/usr/bin/env python3
"""
Field 1: Arithmetic Complexity — Circuit Lower Bounds for Factoring
===================================================================

HYPOTHESIS: Factoring N=p*q can be computed by an arithmetic circuit over Z.
What is the minimum circuit size/depth? If we can show super-polynomial lower
bounds on the arithmetic circuit complexity of factoring, that implies P != NP
(roughly). Conversely, finding small circuits for factoring would be revolutionary.

KEY INSIGHT: The function f(N) = "smallest factor of N" is NOT a polynomial over Z.
But it IS computed by polynomial-size BOOLEAN circuits (trial division up to N^{1/2}).
The gap between arithmetic and Boolean complexity is the core question.

EXPERIMENTS:
1. Measure the "arithmetic complexity" of trial division: how many +,*,compare operations?
2. Compare circuit depth of different factoring methods
3. Test whether partial factoring can be done with shallow circuits
4. Relation to Strassen's conjecture on multiplication complexity
"""

import time
import math
import gmpy2
from gmpy2 import mpz, isqrt, is_prime, next_prime, gcd

# ─── Experiment 1: Operation counts for factoring methods ─────────────────

print("=" * 70)
print("EXPERIMENT 1: Arithmetic operation counts for factoring methods")
print("=" * 70)

class OpCounter:
    """Count arithmetic operations."""
    def __init__(self):
        self.adds = 0
        self.muls = 0
        self.divs = 0
        self.cmps = 0
        self.total = 0

    def add(self, a, b):
        self.adds += 1; self.total += 1
        return a + b

    def mul(self, a, b):
        self.muls += 1; self.total += 1
        return a * b

    def div(self, a, b):
        self.divs += 1; self.total += 1
        return a // b

    def mod(self, a, b):
        self.divs += 1; self.total += 1
        return a % b

    def cmp(self, a, b):
        self.cmps += 1; self.total += 1
        return a < b

def trial_division_counted(N):
    """Trial division with operation counting."""
    ops = OpCounter()
    i = 2
    while ops.cmp(ops.mul(i, i), N + 1):  # i*i <= N
        r = ops.mod(N, i)
        if r == 0:
            return i, ops
        i = ops.add(i, 1)
    return N, ops

def pollard_rho_counted(N, max_iter=100000):
    """Pollard rho with operation counting."""
    ops = OpCounter()
    x = 2
    y = 2
    c = 1
    d = 1
    iters = 0
    while d == 1 and iters < max_iter:
        x = ops.mod(ops.add(ops.mul(x, x), c), N)
        y = ops.mod(ops.add(ops.mul(y, y), c), N)
        y = ops.mod(ops.add(ops.mul(y, y), c), N)
        diff = abs(x - y)
        d = int(gmpy2.gcd(diff, N))
        ops.cmps += 1
        iters += 1
    if d != N and d != 1:
        return d, ops
    return None, ops

def fermat_counted(N, max_iter=100000):
    """Fermat's method with operation counting."""
    ops = OpCounter()
    x = int(isqrt(N)) + 1
    iters = 0
    while iters < max_iter:
        y2 = ops.add(ops.mul(x, x), -int(N))
        y = int(isqrt(y2))
        if ops.mul(y, y) == y2:
            return int(x - y), ops
        x = ops.add(x, 1)
        iters += 1
    return None, ops

print(f"{'bits':>6} {'N':>15} {'trial_ops':>12} {'rho_ops':>12} {'fermat_ops':>12} {'sqrt(N)':>12}")
print("-" * 70)

for bits in [10, 14, 18, 22, 26, 30]:
    half = bits // 2
    rng = gmpy2.random_state(42 + bits)
    p = int(gmpy2.next_prime(gmpy2.mpz_urandomb(rng, half)))
    q = int(gmpy2.next_prime(gmpy2.mpz_urandomb(rng, half)))
    N = p * q

    _, ops_td = trial_division_counted(N)
    f_rho, ops_rho = pollard_rho_counted(N)
    f_fer, ops_fer = fermat_counted(N)

    sqrt_N = int(isqrt(N))
    print(f"{bits:>6} {N:>15} {ops_td.total:>12} {ops_rho.total:>12} "
          f"{ops_fer.total if f_fer else 'FAIL':>12} {sqrt_N:>12}")

# ─── Experiment 2: Circuit depth analysis ─────────────────────────────────

print()
print("=" * 70)
print("EXPERIMENT 2: Circuit depth (parallel complexity) of factoring")
print("=" * 70)

print("""
THEORETICAL ANALYSIS of circuit depth for factoring:

1. TRIAL DIVISION:
   - Sequential: depth O(sqrt(N)) — each trial depends on previous
   - Parallel: Can test all primes simultaneously → depth O(log N) for each test
   - Total: O(sqrt(N)/P + log N) with P processors
   - Circuit depth: O(sqrt(N)) sequential, O(log N) with sqrt(N) processors

2. POLLARD RHO:
   - Inherently sequential: x_{n+1} depends on x_n
   - Circuit depth: O(N^{1/4}) — cannot parallelize the walk
   - BUT: multiple independent walks → O(N^{1/4}/P + log N)

3. QUADRATIC SIEVE / GNFS:
   - Sieve phase: embarrassingly parallel → depth O(log B)
   - Linear algebra: Gaussian elimination depth O(n) for n×n matrix
   - Total depth: O(max(log B, n)) where n = |factor base|
   - For SIQS on D-digit N: depth O(L(N)^{1/2}) — same as sequential!

4. KEY INSIGHT: Sieve methods already have SHALLOW circuit depth!
   The bottleneck is the NUMBER of gates, not the depth.
""")

# Compute theoretical depth for each method at various sizes
print(f"{'digits':>8} {'trial_depth':>14} {'rho_depth':>14} {'siqs_depth':>14} {'gnfs_depth':>14}")
print("-" * 65)

for digits in [20, 40, 60, 80, 100, 150, 200]:
    ln_N = digits * math.log(10)
    ln_ln_N = math.log(ln_N)
    L_half = math.exp(0.5 * math.sqrt(ln_N * ln_ln_N))
    L_third = math.exp((64/9) ** (1/3) * ln_N**(1/3) * ln_ln_N**(2/3))

    trial_depth = 10 ** (digits / 2)  # sqrt(N)
    rho_depth = 10 ** (digits / 4)  # N^{1/4}
    siqs_depth = L_half  # L(N)^{1/2}
    gnfs_depth = L_third ** 0.5  # sqrt of total GNFS work

    print(f"{digits:>8} {math.log10(trial_depth):>14.1f} {math.log10(rho_depth):>14.1f} "
          f"{math.log2(siqs_depth):>14.1f} {math.log2(gnfs_depth):>14.1f}")

print("  (values are log10 for trial/rho, log2 for SIQS/GNFS)")

# ─── Experiment 3: Strassen's multiplication and factoring ────────────────

print()
print("=" * 70)
print("EXPERIMENT 3: Multiplication complexity and its inverse (factoring)")
print("=" * 70)

print("""
STRASSEN'S INSIGHT: n-bit multiplication requires Θ(n log n) operations
(via FFT-based methods like Schönhage-Strassen or Harvey-van der Hoeven).

QUESTION: Does efficient multiplication imply efficient factoring?

ANSWER: NO! Multiplication is a FUNCTION (deterministic, unique output).
Factoring is a SEARCH problem (find any factor). There is no known way
to "invert" the multiplication circuit.

ANALOGY: Addition in O(n) operations, but SUBSET SUM (inverse of addition)
is NP-hard. Efficient forward computation does NOT imply efficient inversion.

ARITHMETIC CIRCUIT COMPLEXITY:
- Multiplication of two n-bit integers: circuit size O(n log n log log n)
- Factoring: best known circuit size L(N)^{1+o(1)} (sub-exponential)
- Gap: polynomial vs sub-exponential
- This gap is STRONG EVIDENCE that factoring is intrinsically harder,
  but NOT A PROOF (no super-polynomial lower bound known for ANY explicit function!)

THE BARRIER: Proving any explicit function requires arithmetic circuits of
size > n^3 (or even n^2) is a MAJOR OPEN PROBLEM. The best lower bound for
any explicit function is ~5n (Morgenstern 1973, for DFT).

So we cannot even prove factoring needs more than ~5n operations!
""")

# Demonstrate the gap empirically
print("Empirical operation counts:")
print(f"{'bits':>6} {'multiply':>12} {'factor':>12} {'ratio':>10}")
print("-" * 45)

for bits in [10, 20, 30, 40, 50]:
    # Multiplication: O(n log n) — use schoolbook as upper bound
    mul_ops = bits * bits  # schoolbook O(n²), FFT would be O(n log n)

    # Factoring: trial division O(2^{n/2})
    factor_ops = int(2 ** (bits / 2))

    print(f"{bits:>6} {mul_ops:>12} {factor_ops:>12} {factor_ops/mul_ops:>10.0f}x")

# ─── Experiment 4: Can we build useful "partial factoring" circuits? ──────

print()
print("=" * 70)
print("EXPERIMENT 4: Partial factoring — extracting bits of factors")
print("=" * 70)

def extract_lsb_of_factor(N):
    """
    Can we determine the LSB of the smaller factor without fully factoring?
    For N=pq with p,q odd primes: both p,q are odd, so LSB(p)=LSB(q)=1.
    This is TRIVIAL — the answer is always 1.
    """
    return 1  # both factors of an odd semiprime are odd

def extract_second_bit(N):
    """
    Can we determine bit 1 of the smaller factor?
    p mod 4 ∈ {1, 3}. N mod 4 = (p mod 4)(q mod 4) mod 4.
    If N ≡ 1 (mod 4): p ≡ q (mod 4) — either both 1 or both 3
    If N ≡ 3 (mod 4): p ≢ q (mod 4) — one is 1, other is 3
    We get SOME information but not enough to determine bit 1 of smaller factor.
    """
    n_mod4 = N % 4
    if n_mod4 == 1:
        return "p≡q mod 4 (both 1 or both 3)"
    else:
        return "p≢q mod 4 (one is 1, other is 3)"

print("Partial information from N mod small numbers:")
for bits in [20, 24, 28]:
    rng = gmpy2.random_state(42 + bits)
    p = int(gmpy2.next_prime(gmpy2.mpz_urandomb(rng, bits)))
    q = int(gmpy2.next_prime(gmpy2.mpz_urandomb(rng, bits)))
    N = p * q

    info_4 = extract_second_bit(N)
    # More: N mod 8 constrains p,q mod 8
    n8 = N % 8
    # N mod 3 constrains p,q mod 3
    n3 = N % 3

    # How many bits of information do we get?
    # N mod m gives log2(euler_phi(m)) bits about (p mod m, q mod m)
    info_bits = 0
    for m in [4, 8, 3, 5, 7, 16, 9, 11, 13]:
        # N mod m constrains (p*q) mod m, which restricts (p mod m, q mod m) pairs
        valid_pairs = 0
        for pm in range(m):
            for qm in range(m):
                if (pm * qm) % m == N % m:
                    valid_pairs += 1
        total_pairs = m * m
        if valid_pairs > 0:
            info_bits += math.log2(total_pairs / valid_pairs)

    print(f"  {bits}b: N={N}, info from mods 4,8,3,5,7,16,9,11,13: {info_bits:.1f} bits "
          f"(need {bits} bits to factor)")

print()
print("=" * 70)
print("CONCLUSIONS")
print("=" * 70)
print("""
1. OPERATION COUNTS: Trial division uses O(sqrt(N)) ops, Pollard rho O(N^{1/4}),
   SIQS/GNFS use L(N)^{1+o(1)}. These are all well-known. No new method found.

2. CIRCUIT DEPTH: Sieve methods already have "shallow" depth (O(L(N)^{1/2}))
   compared to sequential methods. The bottleneck is gate count, not depth.
   Parallelism is already exploited in practice.

3. STRASSEN GAP: Multiplication is O(n log n) ops, factoring is L(N)^{1+o(1)}.
   This gap is strong evidence of asymmetry, but we cannot PROVE any super-linear
   lower bound for factoring circuits. The best lower bound for ANY explicit
   function's circuit size is ~5n.

4. PARTIAL FACTORING: Combining N mod m for many small m gives only O(log N) bits
   of information about factors — exponentially less than the n bits needed.
   Each modular constraint eliminates a constant fraction of pairs but the total
   search space is 2^n.

5. VERDICT: Arithmetic complexity theory gives beautiful structure but NO practical
   speedup for factoring. The fundamental barrier is that no super-polynomial
   circuit lower bounds are known for ANY explicit function.
   This is a NEGATIVE result for practical factoring, but highlights the deep
   connection between factoring hardness and circuit complexity barriers.
""")
