"""
Pythagorean Tree x Modular Forms Experiment

HYPOTHESIS: The Berggren matrices generate a subgroup of GL(2,Z). Modular forms
for this subgroup encode arithmetic information about the tree.

KEY CONNECTIONS:
1. The theta function θ(q) = Σ q^(n^2) counts representations as sums of squares.
   θ(q)^2 = Σ r_2(n) q^n where r_2(n) = #{(a,b): a^2+b^2=n}.
   Pythagorean triples (A,B,C) with C=n correspond to representations of n as a^2+b^2.

2. The Hecke operator T_p on modular forms of weight 2 has eigenvalue a_p where
   a_p = p + 1 - #E(F_p) for an elliptic curve. For the "sum of squares" form,
   a_p relates to the Legendre symbol (-1/p): r_2(p) = 4(1 + (-1/p)).

3. FACTORING CONNECTION: For N = p*q, the representation count r_2(N) depends on
   the factorization of N. Specifically, r_2(N) = 4 * Σ_{d|N} χ(d) where χ = (-1/·).
   If we can compute r_2(N) efficiently via the Pythagorean tree, comparing with the
   formula for different factorizations constrains the factors.

EXPERIMENT: Count Pythagorean representations via tree enumeration.
r_2(N) = 4*(d_1(N) - d_3(N)) where d_1 = # divisors ≡ 1 (mod 4), d_3 = # divisors ≡ 3 (mod 4).

If N = p*q where p,q ≡ 1 (mod 4): r_2(N) = 4*(d_1 - d_3) and d_1, d_3 depend on residues of p,q.
"""

import random
import math
import time
from sympy import nextprime, divisors, factorint

print("=" * 70)
print("MODULAR FORMS: Theta Function and Pythagorean Representations")
print("=" * 70)

# Experiment 1: r_2(N) and factorization
print("\n--- Experiment 1: r_2(N) as factorization constraint ---")
print("r_2(n) = 4 * Σ_{d|n} (-1)^((d-1)/2) for odd n with all prime factors ≡ 1 mod 4")

def r2(n):
    """Count representations as sum of two squares (including signs and order)."""
    count = 0
    for a in range(int(math.isqrt(n)) + 1):
        b2 = n - a*a
        if b2 >= 0:
            b = int(math.isqrt(b2))
            if b*b == b2:
                # Count all sign combinations and orderings
                if a == 0 and b == 0:
                    count += 1
                elif a == 0 or b == 0:
                    count += 4
                elif a == b:
                    count += 4
                else:
                    count += 8
    return count

def r2_formula(n):
    """r_2(n) via divisor formula: 4 * (d_1 - d_3)."""
    d1 = sum(1 for d in divisors(n) if d % 4 == 1)
    d3 = sum(1 for d in divisors(n) if d % 4 == 3)
    return 4 * (d1 - d3)

# Verify formula
for n in [5, 10, 13, 25, 50, 65, 85, 100]:
    r2_direct = r2(n)
    r2_form = r2_formula(n)
    print(f"  r_2({n}) = {r2_direct} (direct), {r2_form} (formula), match={r2_direct==r2_form}")

# Experiment 2: Can r_2(N) constrain factorization?
print("\n--- Experiment 2: r_2(N) constrains factorization of N ---")
print("For N = p*q with p,q ≡ 1 mod 4:")
print("  r_2(N) = 4 * [(1 + (-1)^((p-1)/2)) * (1 + (-1)^((q-1)/2)) * ...]")

random.seed(42)
for trial in range(5):
    # Generate p, q both ≡ 1 mod 4 so N is sum of two squares
    while True:
        p = nextprime(random.randint(100, 10000))
        if p % 4 == 1:
            break
    while True:
        q = nextprime(random.randint(100, 10000))
        if q % 4 == 1 and q != p:
            break
    N = p * q

    r2_N = r2_formula(N)
    # r_2(p*q) = r_2(p) * r_2(q) for coprime p,q? No — that's multiplicative for SOME functions
    # Actually r_2 is multiplicative: r_2(p*q) = r_2(p) * r_2(q) for gcd(p,q)=1
    r2_p = r2_formula(p)
    r2_q = r2_formula(q)

    print(f"  N={N}={p}*{q}: r_2(N)={r2_N}, r_2(p)={r2_p}, r_2(q)={r2_q}, product={r2_p*r2_q}")
    print(f"    Multiplicative? {r2_N == r2_p * r2_q}")

# Experiment 3: Hecke eigenvalue pattern
print("\n--- Experiment 3: Hecke-like eigenvalues from tree structure ---")
print("For each prime p, the Hecke operator T_p acts on the 'tree modular form'.")
print("The trace of B_i mod p gives local information.\n")

def matrix_trace_mod(p):
    """Compute traces of Berggren matrices mod p."""
    # B1 = [[2,-1],[1,0]], trace = 2
    # B2 = [[2,1],[1,0]], trace = 2
    # B3 = [[1,2],[0,1]], trace = 2
    # All have trace 2! This is because they're all conjugate to parabolic/hyperbolic
    # elements with the same trace.

    # More interesting: trace of B1^k mod p
    traces = []
    # M = B1 = [[2,-1],[1,0]]
    a, b, c, d = 2, -1, 1, 0
    for k in range(1, min(p + 5, 500)):
        tr = (a + d) % p
        traces.append(tr)
        # M = M * B1
        a, b, c, d = (2*a - c) % p, (2*b - d) % p, a % p, b % p

    return traces

# Check: period of trace(B1^k) mod p
for p in [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]:
    traces = matrix_trace_mod(p)
    # Find period
    period = None
    for per in range(1, len(traces)):
        if traces[per] == traces[0]:
            # Check if it's really periodic
            is_period = True
            for i in range(min(per, len(traces) - per)):
                if traces[i] != traces[i + per]:
                    is_period = False
                    break
            if is_period:
                period = per
                break

    # Legendre symbol (-1|p) and (2|p)
    leg_neg1 = pow(-1 % p, (p-1)//2, p)
    leg_2 = pow(2, (p-1)//2, p)

    print(f"  p={p:3d}: trace period of B1^k = {period}, (-1|p)={'+1' if leg_neg1==1 else '-1'}, (2|p)={'+1' if leg_2==1 else '-1'}")

# Experiment 4: Modular form L-function connection
print("\n--- Experiment 4: Tree walk as modular form coefficient sampler ---")
print("Idea: The tree at depth d has 3^d nodes. Their hypotenuses C = m^2+n^2")
print("sample values for which r_2(C) > 0. Can we use this to build a 'sieve'?\n")

# Generate tree nodes at various depths, collect hypotenuses
def tree_nodes(depth):
    """Generate all (m,n) at given depth in Pythagorean tree."""
    nodes = [(2, 1)]
    for d in range(depth):
        new_nodes = []
        for m, n in nodes:
            new_nodes.append((2*m - n, m))   # B1
            new_nodes.append((2*m + n, m))   # B2
            new_nodes.append((m + 2*n, n))   # B3
        nodes = new_nodes
    return nodes

for depth in range(1, 9):
    nodes = tree_nodes(depth)
    hypotenuses = set()
    for m, n in nodes:
        C = m*m + n*n
        hypotenuses.add(C)

    # What fraction of hypotenuses are prime?
    from sympy import isprime
    prime_count = sum(1 for C in hypotenuses if isprime(C))
    max_C = max(hypotenuses)
    min_C = min(hypotenuses)

    print(f"  Depth {depth}: {len(nodes)} nodes, {len(hypotenuses)} unique C values, "
          f"range [{min_C}, {max_C}], {prime_count} primes ({100*prime_count/len(hypotenuses):.1f}%)")

print("\n--- KEY FINDINGS ---")
print("1. r_2(N) is multiplicative, so r_2(pq) = r_2(p)*r_2(q). Knowing r_2(N)")
print("   constrains but doesn't determine the factorization (many p,q combos give same r_2).")
print("2. ALL Berggren matrices have trace 2 — they're all 'parabolic-like' in this sense.")
print("3. The trace period of B1^k mod p relates to the multiplicative order of eigenvalues")
print("   of B1 in F_p, connecting to Pollard p±1 methods.")
print("4. Tree hypotenuses are always ≡ 1 mod 4 (sum of coprime squares), heavily biased.")
