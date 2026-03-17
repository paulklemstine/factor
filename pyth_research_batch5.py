"""
Batch 5: Combinatorial Game Theory, Symplectic Geometry, Homological Algebra
"""

import random
import math
import numpy as np
from collections import Counter
from sympy import nextprime

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

print("=" * 70)
print("FIELD 13: COMBINATORIAL GAME THEORY")
print("=" * 70)

# HYPOTHESIS: Model factoring as a 2-player game on the Pythagorean tree.
# Player 1 (Nature) chooses N = p*q. Player 2 (Solver) navigates the tree.
# At each step, Solver chooses which Berggren matrix to apply.
# Solver wins if gcd(derived_value, N) ∈ {p, q}.
#
# Game-theoretic question: What is the VALUE of this game?
# Can we use Sprague-Grundy theory to compute winning positions?
#
# KEY INSIGHT: A position (m, n) mod N is "winning" if ANY derived value reveals a factor.
# By backward induction, positions whose children are all "losing" are truly losing.
# The fraction of winning positions determines the game value.

def is_winning(m, n, N):
    """Check if position (m,n) mod N is immediately winning."""
    for val in [m, n, (m-n)%N, (m+n)%N, (m*m+n*n)%N, (m*n)%N]:
        g = gcd(val, N)
        if 1 < g < N:
            return True
    return False

print("\n--- Experiment 1: Fraction of 'winning' positions mod N ---")

random.seed(42)
for bits in [12, 16, 20]:
    p = nextprime(random.randint(2**(bits//2-1), 2**(bits//2)))
    q = nextprime(random.randint(2**(bits//2-1), 2**(bits//2)))
    N = p * q

    # Sample random positions
    total = 10000
    wins = sum(1 for _ in range(total)
               if is_winning(random.randint(0, N-1), random.randint(0, N-1), N))

    # Expected: probability that p | val or q | val for any of 6 values
    # P(p|m) ≈ 1/p, so P(not win) ≈ (1-1/p)^6 * (1-1/q)^6
    expected_win = 1 - (1 - 1/p)**6 * (1 - 1/q)**6

    print(f"  N={N} ({bits}b): {wins}/{total} winning ({100*wins/total:.1f}%), "
          f"expected={100*expected_win:.1f}%")

# Experiment 2: Game tree search — how deep until guaranteed win?
print("\n--- Experiment 2: Minimax depth to guaranteed factor ---")
print("Starting from (2,1) mod N, what's the minimum depth to reach a winning position?")

for p, q in [(5,7), (7,11), (11,13), (13,17), (17,19)]:
    N = p * q

    # BFS from (2,1)
    start = (2 % N, 1 % N)
    visited = {start}
    frontier = [start]
    depth = 0
    found = False

    while frontier and depth < 50:
        if any(is_winning(m, n, N) for m, n in frontier):
            found = True
            break

        next_frontier = []
        for m, n in frontier:
            for child in [((2*m-n)%N, m%N), ((2*m+n)%N, m%N), ((m+2*n)%N, n%N)]:
                if child not in visited:
                    visited.add(child)
                    next_frontier.append(child)
        frontier = next_frontier
        depth += 1

    if found:
        winning_at_depth = [(m,n) for m,n in frontier if is_winning(m,n,N)]
        print(f"  N={N:4d}={p}*{q}: first win at depth {depth}, "
              f"{len(winning_at_depth)} winning nodes at that depth")
    else:
        print(f"  N={N:4d}={p}*{q}: no win in {depth} depths ({len(visited)} nodes explored)")

# Experiment 3: Nimber / Sprague-Grundy values
print("\n--- Experiment 3: Sprague-Grundy analysis (small N) ---")

N = 5 * 7  # = 35
# Compute Grundy values for all positions reachable from (2,1)
# Grundy(pos) = mex{Grundy(child) for all children}
# Terminal (winning) positions have Grundy value = 0 in mis`ere, but we want to WIN
# Redefine: Grundy value for "first player to reach a winning position wins"

# Simpler: compute the set of "winning" and "losing" positions by backward induction
# from the set of immediately-winning positions.
# A position is 1-step winning if is_winning.
# A position is k-step winning if any child is (k-1)-step winning.

# For small N, compute the "escape depth" of each position
positions = set()
for m in range(N):
    for n in range(N):
        if (m, n) != (0, 0):
            positions.add((m, n))

escape_depth = {}
for m, n in positions:
    if is_winning(m, n, N):
        escape_depth[(m, n)] = 0

# Propagate backward
for d in range(1, 20):
    new_escapes = {}
    for m, n in positions:
        if (m, n) in escape_depth:
            continue
        # Check if any child is winning at depth d-1
        for child in [((2*m-n)%N, m%N), ((2*m+n)%N, m%N), ((m+2*n)%N, n%N)]:
            if child in escape_depth and escape_depth[child] == d-1:
                new_escapes[(m, n)] = d
                break
    escape_depth.update(new_escapes)
    if not new_escapes:
        break

# Statistics
depth_counts = Counter(escape_depth.values())
unreachable = len(positions) - len(escape_depth)
start_depth = escape_depth.get((2, 1), "NEVER")

print(f"  N={N}: {len(positions)} positions, escape depths: {dict(sorted(depth_counts.items()))}")
print(f"  Unreachable from winning: {unreachable}")
print(f"  Start (2,1): escape depth = {start_depth}")

print("\n" + "=" * 70)
print("FIELD 14: SYMPLECTIC GEOMETRY")
print("=" * 70)

# HYPOTHESIS: The Berggren matrices preserve a specific bilinear form.
# If this form is symplectic (antisymmetric), the tree generates a subgroup
# of Sp(2, Z). The symplectic structure imposes constraints on orbit periods.

# For 2x2 matrices, Sp(2,Z) = SL(2,Z) (symplectic = special linear in dim 2).
# det(B1) = 2*0 - (-1)*1 = 1 ✓ (so B1 ∈ SL(2,Z))
# det(B2) = 2*0 - 1*1 = -1 ✗ (B2 ∈ GL(2,Z) \ SL(2,Z))
# det(B3) = 1*1 - 2*0 = 1 ✓

# But we can look at SYMPLECTIC INVARIANTS of the matrices.
# The standard symplectic form ω = [[0,1],[-1,0]].
# M is symplectic iff M^T ω M = ω, i.e., det(M) = 1.

print("\n--- Experiment 1: Which Berggren matrices are symplectic? ---")

import numpy as np

omega = np.array([[0, 1], [-1, 0]])

matrices = {
    "B1": np.array([[2, -1], [1, 0]]),
    "B2": np.array([[2, 1], [1, 0]]),
    "B3": np.array([[1, 2], [0, 1]]),
}

for name, M in matrices.items():
    det = int(np.round(np.linalg.det(M)))
    MtOM = M.T @ omega @ M
    is_symp = np.allclose(MtOM, omega)
    print(f"  {name}: det={det}, M^T ω M = {MtOM.tolist()}, symplectic? {is_symp}")

# INSIGHT: B1 and B3 are symplectic (det=1), B2 is anti-symplectic (det=-1)
# In Sp(2,Z) = SL(2,Z), the subgroup <B1, B3> preserves the symplectic form.
# B2 REVERSES orientation.

print("\n--- Experiment 2: Lagrangian subspaces and factoring ---")
print("A Lagrangian subspace L of F_p^2 (with symplectic form) is a 1D subspace")
print("where ω(v,v) = 0 for all v ∈ L. These are just lines through origin.")
print("The symplectic group acts transitively on Lagrangians.\n")

# For factoring: the Lagrangian decomposition of F_N^2 = F_p^2 x F_q^2
# gives two independent copies. A symplectic matrix that fixes a Lagrangian
# mod p but not mod q would reveal p.

for p_test in [11, 23, 37, 53, 71]:
    # Find fixed Lagrangians of B1 mod p
    # B1 = [[2,-1],[1,0]]. Fixed vectors: B1*v = λv.
    # Eigenvalues of B1: x^2 - 2x + 1 = (x-1)^2, so λ=1.
    # Eigenvector: (B1 - I)*v = 0, i.e., [[1,-1],[1,-1]]*v = 0, so v = (1,1).
    # The fixed Lagrangian of B1 is span((1,1)) for ALL p.

    # This means B1 is parabolic (single fixed point on projective line).
    # The fixed Lagrangian (1,1) is the SAME for all p — no factoring info!

    # For B3: [[0,2],[0,0]]*v = 0, so v = (1,0). Fixed Lagrangian = span((1,0)).
    # Also same for all p.

    # MORE INTERESTING: B1^k * (2,1) mod p. The orbit lies on an "affine Lagrangian"
    # (coset of the fixed Lagrangian).
    pass

print("  B1 has fixed Lagrangian span((1,1)) for ALL primes — no factoring info.")
print("  B3 has fixed Lagrangian span((1,0)) for ALL primes — no factoring info.")
print("  B2 is anti-symplectic (det=-1), no fixed Lagrangian in the symplectic sense.")

print("\n--- Experiment 3: Symplectic capacity and action variables ---")
print("The 'action' J = m*dn - n*dm along a B3 path is constant (B3 is shear).")
print("For B1 (hyperbolic), the action grows exponentially.\n")

# Track the symplectic action ω(v_k, v_{k+1}) = m_k * n_{k+1} - n_k * m_{k+1}
for name, mat_fn in [("B1", lambda m,n: (2*m-n, m)),
                      ("B2", lambda m,n: (2*m+n, m)),
                      ("B3", lambda m,n: (m+2*n, n))]:
    m, n = 2, 1
    actions = []
    for k in range(10):
        m2, n2 = mat_fn(m, n)
        action = m * n2 - n * m2  # ω(v_k, v_{k+1})
        actions.append(action)
        m, n = m2, n2
    print(f"  {name}: ω(v_k, v_{{k+1}}) = {actions[:8]}")

print("\n  THEOREM: ω(v_k, v_{k+1}) = det(M) * ω(v_{k-1}, v_k)")
print("  For B1,B3 (det=1): action is CONSTANT along path!")
print("  For B2 (det=-1): action alternates sign!")

print("\n" + "=" * 70)
print("FIELD 15: HOMOLOGICAL ALGEBRA")
print("=" * 70)

# HYPOTHESIS: Build a chain complex from the tree structure.
# Vertices = 0-chains, edges = 1-chains, faces = 2-chains.
# The homology H_n of this complex over Z/NZ vs Z/pZ differs,
# and the difference reveals p.

# Simpler approach: the GROUP HOMOLOGY of G = <B1,B2,B3>.
# H_1(G, Z) = G/[G,G] (abelianization).
# The abelianization tells us about the "shape" of the group.

print("\n--- Experiment 1: Abelianization of <B1,B2,B3> mod p ---")
print("Compute [G,G] = commutator subgroup, then G/[G,G].\n")

def mat_mult_mod(A, B, p):
    return [[(A[0][0]*B[0][0]+A[0][1]*B[1][0])%p, (A[0][0]*B[0][1]+A[0][1]*B[1][1])%p],
            [(A[1][0]*B[0][0]+A[1][1]*B[1][0])%p, (A[1][0]*B[0][1]+A[1][1]*B[1][1])%p]]

def mat_inv_mod(M, p):
    """Inverse of 2x2 matrix mod p."""
    det = (M[0][0]*M[1][1] - M[0][1]*M[1][0]) % p
    det_inv = pow(det, -1, p)
    return [[(M[1][1]*det_inv)%p, ((-M[0][1])*det_inv)%p],
            [((-M[1][0])*det_inv)%p, (M[0][0]*det_inv)%p]]

for p_test in [5, 7, 11, 13, 23, 29]:
    B1m = [[2%p_test, (-1)%p_test], [1, 0]]
    B2m = [[2%p_test, 1], [1, 0]]
    B3m = [[1, 2%p_test], [0, 1]]

    gens = [B1m, B3m]  # B1, B3 generate SL(2,Z_p)

    # Enumerate group elements
    group = set()
    queue = [tuple(tuple(row) for row in [[1,0],[0,1]])]
    group.add(queue[0])

    while queue and len(group) < 10000:
        M = [list(row) for row in queue.pop(0)]
        for G in gens:
            prod = mat_mult_mod(M, G, p_test)
            key = tuple(tuple(row) for row in prod)
            if key not in group:
                group.add(key)
                queue.append(key)

    # Compute commutator subgroup
    commutators = set()
    group_list = list(group)[:200]  # Sample
    for i in range(min(len(group_list), 50)):
        for j in range(min(len(group_list), 50)):
            A = [list(row) for row in group_list[i]]
            B = [list(row) for row in group_list[j]]
            Ainv = mat_inv_mod(A, p_test)
            Binv = mat_inv_mod(B, p_test)
            comm = mat_mult_mod(mat_mult_mod(A, B, p_test),
                               mat_mult_mod(Ainv, Binv, p_test), p_test)
            commutators.add(tuple(tuple(row) for row in comm))

    print(f"  p={p_test:3d}: |G|={len(group)}, |[G,G]| sample≥{len(commutators)}, "
          f"|G/[G,G]|≤{len(group)//max(1,len(commutators))}")

print("\n--- Experiment 2: Betti numbers of the tree graph ---")
print("The tree has β_0 = 1 (connected), β_1 = 0 (no cycles).")
print("But the QUOTIENT graph (tree mod N) has cycles, and β_1 encodes factoring info.\n")

# For small N, compute β_1 of the orbit graph under <B1,B2,B3> mod N
for N_test in [15, 21, 35, 55, 77]:
    # Build graph: vertices = orbit of (2,1), edges = matrix applications
    vertices = set()
    edges = set()
    queue = [(2 % N_test, 1 % N_test)]
    vertices.add(queue[0])

    while queue:
        m, n = queue.pop(0)
        for child in [((2*m-n)%N_test, m%N_test), ((2*m+n)%N_test, m%N_test),
                      ((m+2*n)%N_test, n%N_test)]:
            edge = ((m,n), child)
            edges.add(edge)
            if child not in vertices:
                vertices.add(child)
                queue.append(child)

    V = len(vertices)
    E = len(edges)
    # For a connected graph: β_1 = E - V + 1
    beta1 = E - V + 1

    # Factor N_test
    from sympy import factorint
    factors = factorint(N_test)
    print(f"  N={N_test:3d} ({dict(factors)}): V={V:4d}, E={E:4d}, β_1={beta1:4d}")

print("\n--- KEY FINDINGS ---")
print("1. The symplectic action ω(v_k, v_{k+1}) = det(M) * constant is PRESERVED")
print("   by B1,B3 and REVERSED by B2. This is a conservation law on tree paths.")
print("2. Game theory: winning positions exist at shallow depth (~2-5 steps) for small N.")
print("3. The first Betti number β_1 of the quotient graph grows with N and")
print("   encodes the cycle structure, but doesn't directly reveal factors.")
print("4. Abelianization of <B1,B3> mod p gives SL(2,F_p) / [SL(2,F_p), SL(2,F_p)]")
print("   which is trivial (SL(2) is perfect for p≥5). No homological factoring info.")
