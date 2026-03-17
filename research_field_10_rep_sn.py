"""Field 10: Representation Theory of S_n - Symmetric Group Actions on Residue Classes
Hypothesis: The symmetric group S_n acts on the set of residues mod N by permuting
elements. The character theory of this representation might decompose Z/NZ into
irreducible components that align with the factor structure. Specifically, the
representation over Z/pZ x Z/qZ decomposes differently than over Z/NZ.
"""
import time, math, random
from collections import Counter

def action_cycle_structure(N, perm_size=None):
    """Study the cycle structure of the multiplication-by-a map on Z/NZ.
    For a in (Z/NZ)*, the map x -> ax mod N is a permutation.
    Its cycle type (as an element of S_N) encodes factor information.
    """
    if perm_size is None:
        perm_size = N

    results = {}
    for a in range(2, min(20, N)):
        if math.gcd(a, N) != 1:
            continue
        # Find cycle structure of x -> ax mod N
        visited = set()
        cycles = []
        for start in range(N):
            if start in visited:
                continue
            cycle = []
            x = start
            while x not in visited:
                visited.add(x)
                cycle.append(x)
                x = (a * x) % N
            if len(cycle) > 0:
                cycles.append(len(cycle))

        cycle_type = tuple(sorted(cycles, reverse=True))
        results[a] = cycle_type

    return results

def character_inner_product(N, p, q):
    """For Z/NZ ≅ Z/pZ × Z/qZ, the regular representation decomposes as
    tensor product of representations of Z/pZ and Z/qZ.
    The characters (traces of representation matrices) encode this product structure.

    Character of Z/NZ at element a: chi(a) = sum_{x in Z/NZ} omega^{ax}
    where omega = e^{2pi*i/N}. This is N if a=0, else 0.
    """
    import numpy as np

    # Compute DFT of indicator function of Z/NZ
    # This is the standard character table - nothing new here
    # The key question: does the character decomposition reveal p,q?

    # For small N: compute character table of (Z/NZ)*
    if N > 1000:
        return None

    # Characters of (Z/NZ)* are Dirichlet characters
    # They factor as chi = chi_p * chi_q (product of chars mod p and q)
    # But to USE this factoring, we need to identify which characters
    # "come from" p vs q. This requires knowing p,q.

    # Instead: study eigenvalues of the multiplication table
    # The multiplication table of Z/NZ is an N×N matrix M where M[i,j] = i*j mod N
    M = np.zeros((min(N, 200), min(N, 200)))
    n = min(N, 200)
    for i in range(n):
        for j in range(n):
            M[i, j] = (i * j) % N

    # Eigenvalues of M
    eigs = np.linalg.eigvals(M)
    eigs_sorted = sorted(np.abs(eigs), reverse=True)

    # Does the eigenvalue spectrum reveal factor structure?
    # For N=pq, the rank of M should reflect the product structure
    rank = np.linalg.matrix_rank(M, tol=0.5)

    return eigs_sorted[:10], rank

def experiment():
    print("=== Field 10: S_n Representation Theory on Z/NZ ===\n")

    test_cases = [(3, 5), (7, 11), (13, 17), (23, 29), (37, 41)]

    print("  Test 1: Cycle structure of multiplication maps")
    for p, q in test_cases:
        N = p * q
        cycles = action_cycle_structure(N)
        print(f"  N={N} = {p}*{q}:")
        for a in sorted(cycles.keys())[:4]:
            ct = Counter(cycles[a])
            print(f"    mult-by-{a}: {dict(ct)}")

        # Key insight: cycle lengths of x->ax are the orders of a in each component
        # By CRT: order of a mod N = lcm(order mod p, order mod q)
        # The cycle structure DOES encode p,q, but extracting it is equivalent to
        # computing orders, which IS the factoring problem
        for a in sorted(cycles.keys())[:4]:
            cycle_lens = set(cycles[a])
            for cl in cycle_lens:
                if cl > 1:
                    g = math.gcd(pow(a, cl // 2, N) - 1, N) if cl % 2 == 0 else 1
                    if 1 < g < N:
                        print(f"    ** FACTOR {g} from cycle len {cl} of a={a} **")

    print("\n  Test 2: Eigenvalue spectrum of multiplication table")
    for p, q in test_cases[:3]:
        N = p * q
        result = character_inner_product(N, p, q)
        if result:
            eigs, rank = result
            print(f"  N={N}: top eigenvalues={[f'{e:.1f}' for e in eigs[:5]]}, rank={rank}")
            # For comparison: N prime
            # The rank/eigenvalue structure differs for prime vs composite,
            # but this is known and doesn't help factor

    print("\nVERDICT: Cycle structure of multiplication maps encodes factor information")
    print("via CRT decomposition. But EXTRACTING factors from cycle structure requires")
    print("computing orders of elements mod N, which IS the factoring problem.")
    print("Character decomposition similarly requires knowing the factor structure.")
    print("Representation theory describes WHY factoring works, not HOW to do it faster.")
    print("RESULT: REFUTED")

experiment()
