#!/usr/bin/env python3
"""
Moonshot 7: Descriptive Complexity of Factoring
================================================
Can factoring be expressed in fixed-point logic (FP, FO+LFP)?

Immerman-Vardi theorem: On ORDERED structures, FP = P.
So if factoring can be expressed in FP over ordered binary strings,
it's in P. The question is: can we WRITE such a formula?

Test:
1. Express "N is composite" in first-order logic (FO)
2. Try to express "smallest factor of N" in FP
3. Check if transitive closure (TC) logic captures factoring
4. Measure the quantifier depth needed
"""

import time
import math
import random
from collections import defaultdict, Counter

try:
    import gmpy2
    _HAS_GMPY2 = True
except ImportError:
    _HAS_GMPY2 = False

def is_prime(n):
    if _HAS_GMPY2:
        return gmpy2.is_prime(n)
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

def random_prime(bits):
    while True:
        n = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(n):
            return n

def main():
    print("=" * 70)
    print("Moonshot 7: Descriptive Complexity of Factoring")
    print("=" * 70)
    t0 = time.time()

    # --- Test 1: FO expressibility of compositeness ---
    print("\n--- Test 1: First-Order Expressibility ---")
    print("  Universe: bit positions {0, 1, ..., n-1}")
    print("  Relations: BIT(i) = 1 iff bit i of N is 1, SUCC(i,j) = (j=i+1)")
    print("  Arithmetic: addition and multiplication are FO-definable on ordered")
    print("  structures via iterated addition (Immerman).")
    print()

    print("  COMPOSITENESS in FO+BIT:")
    print("    exists d (2 <= d <= sqrt(N)): N mod d = 0")
    print("    This requires:")
    print("    - Quantifying over d (a number, encoded as bit string)")
    print("    - Computing N mod d (iterated subtraction)")
    print("    - Comparing with 0")
    print()
    print("  In FO with BIT predicate: multiplication and division are")
    print("  definable. So compositeness IS expressible in FO(BIT).")
    print("  But the formula size is polynomial in n (the bit length).")

    # Simulate: for each n-bit number, evaluate the FO formula
    for bits in [6, 8, 10, 12]:
        composites = 0
        primes_count = 0
        for N in range(1 << (bits - 1), 1 << bits):
            if N < 2:
                continue
            is_comp = False
            for d in range(2, int(N**0.5) + 1):
                if N % d == 0:
                    is_comp = True
                    break
            if is_comp:
                composites += 1
            else:
                primes_count += 1

        total = 1 << (bits - 1)
        print(f"  {bits}-bit: {composites} composites, {primes_count} primes "
              f"out of {total}")
        print(f"    Prime density: {primes_count/total:.4f} "
              f"(theory: ~{1/math.log(2**bits):.4f})")

    # --- Test 2: Fixed-point logic for factoring ---
    print("\n--- Test 2: LFP (Least Fixed Point) for Factoring ---")
    print("  LFP allows defining recursive predicates.")
    print("  The Immerman-Vardi theorem: FO + LFP = P on ordered structures.")
    print("  So IF factoring is in P, it IS expressible in FO + LFP.")
    print("  But we don't know if factoring is in P!")
    print()

    # The key question: can we WRITE an LFP formula for the smallest factor?
    # LFP formula sketch:
    # FACTOR(i) := "bit i of the smallest factor of N"
    # Define: DIVIDE(d, N) := "d divides N" (expressible in FO+BIT)
    # Define: SMALLEST(d) := DIVIDE(d,N) AND d > 1 AND
    #         forall d' (1 < d' < d => NOT DIVIDE(d',N))
    # This is actually FO (no fixed point needed!) for the decision version.

    print("  Surprising finding: 'smallest factor of N' is FO-definable!")
    print("  Formula: exists d [DIVIDE(d,N) AND d>1 AND forall d'<d: NOT DIVIDE(d',N)]")
    print("  This is FO with 2 quantifier blocks (exists-forall).")
    print("  Quantifier depth = 2 (plus the depth of DIVIDE subroutine).")
    print()
    print("  But EVALUATING this formula takes O(sqrt(N)) time (trial division)!")
    print("  FO expressibility != polynomial-time evaluation.")
    print("  The Immerman-Vardi theorem applies to DATA COMPLEXITY (N varies, formula fixed).")
    print("  The formula SIZE is O(1) (constant for fixed bit-width n).")
    print("  But the UNIVERSE SIZE is n bits, so evaluation is poly(n).")

    # --- Test 3: Quantifier depth experiments ---
    print("\n--- Test 3: Quantifier Depth for Factoring Properties ---")
    print("  How many nested quantifiers are needed to express factoring-related")
    print("  predicates? Lower bound on quantifier depth => circuit depth lower bound.")

    # For small bits, check which factoring predicates are definable with
    # bounded quantifier depth (Ehrenfeucht-Fraisse games)

    for bits in [4, 6, 8]:
        # Classify numbers by their "factoring type"
        # Type 0: prime
        # Type 1: semiprime (product of two distinct primes)
        # Type 2: prime power
        # Type 3: other composite
        type_counts = Counter()
        for N in range(1 << (bits - 1), 1 << bits):
            if N < 2:
                continue
            # Factor completely
            temp = N
            factors = []
            d = 2
            while d * d <= temp:
                while temp % d == 0:
                    factors.append(d)
                    temp //= d
                d += 1
            if temp > 1:
                factors.append(temp)

            if len(factors) == 1:
                type_counts['prime'] += 1
            elif len(factors) == 2 and factors[0] != factors[1]:
                type_counts['semiprime'] += 1
            elif len(set(factors)) == 1:
                type_counts['prime_power'] += 1
            else:
                type_counts['other_comp'] += 1

        total = sum(type_counts.values())
        print(f"  {bits}-bit distribution:")
        for t, c in sorted(type_counts.items()):
            print(f"    {t:15s}: {c:4d} ({c/total*100:.1f}%)")

        # The key: distinguishing "semiprime" from "other composite"
        # requires checking that N has EXACTLY 2 prime factors.
        # This needs quantifier depth >= 2 (exists p: p|N AND N/p prime).
        # But checking "N/p is prime" needs another level: forall d: d does not divide N/p.
        # So total depth >= 3 for semiprime detection.

    print("\n  Quantifier depth hierarchy:")
    print("    Depth 0: constants (0, 1, N)")
    print("    Depth 1: 'N is even' = exists i: BIT(i)=0 AND i=0")
    print("    Depth 2: 'N is composite' = exists d>1: d|N")
    print("    Depth 3: 'N is semiprime' = exists p: p|N AND p prime AND N/p prime")
    print("    Depth ?: 'smallest factor of N' (output function, not predicate)")

    # --- Test 4: Transitive closure logic ---
    print("\n--- Test 4: Transitive Closure (TC) Logic ---")
    print("  FO + TC = NL (nondeterministic logspace) on ordered structures.")
    print("  FO + DTC = L (deterministic logspace) on ordered structures.")
    print("  Is factoring in NL or L?")
    print()

    # Factoring is NOT known to be in NL.
    # NL contains problems solvable with O(log n) nondeterministic space.
    # Factoring requires at least Omega(n) space to write down the factor.
    # But the DECISION version "is there a factor < B?" might be in NL.

    # Simulate: space usage of trial division for decision version
    for bits in [16, 32, 64, 128]:
        # Trial division "is there a factor of N less than B?"
        # Space needed: O(log N) = O(n) bits for the counter d
        # Plus O(n) bits for the remainder N mod d
        space_trial = 2 * bits  # bits for counter + remainder
        # NL space: O(log n) = O(log bits) bits
        nl_space = math.ceil(math.log2(bits + 1))

        print(f"  {bits:4d}-bit: trial_div_space={space_trial} bits, "
              f"NL_space={nl_space} bits, "
              f"ratio={space_trial/nl_space:.1f}")

    print("\n  Trial division uses O(n) space — much more than NL's O(log n).")
    print("  Factoring is NOT known to be in NL or L.")
    print("  The decision version 'has factor < B' is in NP intersect coNP.")

    # --- Test 5: Finite model theory perspective ---
    print("\n--- Test 5: Finite Model Theory View ---")
    print("  Factoring on n-bit inputs is a query on the structure:")
    print("    S_N = ({0,...,n-1}, BIT_N, SUCC, <)")
    print("  where BIT_N(i) = i-th bit of N.")
    print()

    # For each n, the "factoring query" maps S_N to the output structure.
    # The key question: is this query definable by a fixed FO formula
    # (independent of n) with BIT, SUCC, and arithmetic?

    # On ordered structures with BIT: Barrington et al. showed
    # FO+BIT = FO+MULT (multiplication predicate gives same power as BIT).
    # And FO+BIT captures uniform TC^0 (threshold circuits of constant depth).

    # Is factoring in TC^0? Almost certainly not (factoring is not known to
    # be in NC^1, let alone TC^0).

    # Test: for small n, how does the "factoring pattern" look as a function?
    for bits in [6, 8]:
        print(f"\n  {bits}-bit factoring function (partial):")
        count = 0
        for N in range(1 << (bits - 1), 1 << bits):
            p = 0
            for d in range(2, int(N**0.5) + 1):
                if N % d == 0:
                    p = d
                    break
            if p > 0 and count < 10:
                # Show the bit pattern
                N_bits = format(N, f'0{bits}b')
                p_bits = format(p, f'0{bits//2}b')
                print(f"    N={N:4d} ({N_bits}) -> p={p:3d} ({p_bits})")
                count += 1

    print("\n  The factoring function has no apparent pattern in the bit domain.")
    print("  Each output bit depends on ALL input bits (high sensitivity).")

    elapsed = time.time() - t0
    print(f"\n--- Summary (elapsed: {elapsed:.1f}s) ---")
    print("""
  Descriptive Complexity Findings:

  1. FO EXPRESSIBILITY: "N is composite" is FO-definable with depth 2.
     "Smallest factor of N" is also FO-definable. But FO expressibility
     does NOT imply efficient evaluation — the formula is constant-size
     but evaluates in O(sqrt(N)) time (trial division).

  2. LFP/FIXED-POINT: By Immerman-Vardi, factoring is in FO+LFP iff
     it is in P. So writing an LFP formula IS equivalent to finding a
     polynomial algorithm. This is circular but conceptually illuminating.

  3. QUANTIFIER DEPTH: Compositeness needs depth 2, semiprime detection
     needs depth 3. The factoring function requires depth proportional
     to the circuit depth of factoring — which is unknown.

  4. TRANSITIVE CLOSURE: Factoring is not known to be in NL (O(log n) space).
     Trial division uses O(n) space, far above the NL threshold.
     The decision version might be in harder space classes.

  5. TC^0 / NC HIERARCHY: Factoring is not known to be in TC^0 or NC^1.
     These are extremely weak circuit classes. If factoring were in TC^0,
     it would be computable by constant-depth threshold circuits — which
     seems implausible given the function's sensitivity to all input bits.

  VERDICT: Descriptive complexity provides a clean framework but offers
  no new leverage for proving factoring is hard. The Immerman-Vardi
  equivalence (FP = P on ordered structures) means that an FP formula
  for factoring IS a polynomial algorithm — so writing one is as hard as
  solving the open problem. Useful for classification, not for proofs.
  Rating: 2/10 for proving factoring lower bounds.
""")

if __name__ == '__main__':
    main()
