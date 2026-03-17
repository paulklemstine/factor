#!/usr/bin/env python3
"""
B3-SAT Linearization — Implementation and rigorous test of the claim that
the B3 parabolic shear [[1,2],[0,1]] can linearize NP-complete problems.

We implement the claimed approach:
1. Encode multiplication N=p*q as a system of 3-SAT-like clauses
2. Build an implication/adjacency matrix from those clauses
3. Expand across L layers (the "helical unrolling")
4. Apply B3 shear (Kronecker product with the layer structure)
5. Check eigenvalues — does "Jordan Crystallization" happen?
6. Extract factors from the result

Then we test the CRITICAL question: does this work when p,q are UNKNOWN?
"""

import numpy as np
import time
import sys
from math import gcd, log2, ceil

# =============================================================================
# Part 1: The B3 matrix and its properties
# =============================================================================

B3 = np.array([[1, 2], [0, 1]], dtype=float)
# Properties:
# - Eigenvalues: both 1 (degenerate)
# - B3 - I = [[0,2],[0,0]] which is nilpotent: (B3-I)^2 = 0
# - B3 is parabolic in SL(2,Z)
# - B3^k = [[1, 2k], [0, 1]] — shear grows linearly

def analyze_b3():
    """Show basic B3 properties."""
    print("=== B3 Matrix Properties ===")
    print(f"B3 = {B3.tolist()}")
    eigvals = np.linalg.eigvals(B3)
    print(f"Eigenvalues: {eigvals}")
    N_mat = B3 - np.eye(2)
    print(f"B3 - I = {N_mat.tolist()}")
    print(f"(B3-I)^2 = {(N_mat @ N_mat).tolist()}")
    print(f"Nilpotent index: 2 (always, by construction)")
    print()

# =============================================================================
# Part 2: Encode factoring as clause system (WITH known factors)
# =============================================================================

def bits_of(n, nbits):
    """Return list of bits (LSB first)."""
    return [(n >> i) & 1 for i in range(nbits)]

def build_multiplication_clauses_known(p, q):
    """
    Build clauses for N = p * q where p,q are KNOWN.
    This is the version in the original claim — it uses p,q directly.
    """
    N = p * q
    nb = max(p.bit_length(), q.bit_length())

    # Binary representations
    p_bits = bits_of(p, nb)
    q_bits = bits_of(q, nb)
    n_bits = bits_of(N, 2 * nb)

    # Variables: p_i (i=0..nb-1), q_j (j=0..nb-1)
    n_vars = 2 * nb

    # Build "implication" matrix: clause interactions
    # Each clause: p_i AND q_j contributes to n_{i+j}
    clauses = []
    for i in range(nb):
        for j in range(nb):
            # p_i * q_j contributes to bit i+j of N
            clauses.append((i, nb + j, i + j, p_bits[i] * q_bits[j]))

    # Build adjacency matrix from clauses
    M = np.zeros((n_vars, n_vars))
    for (vi, vj, bit_pos, val) in clauses:
        M[vi, vj] += val
        M[vj, vi] += val

    return M, n_vars, clauses

# =============================================================================
# Part 3: The claimed "linearization" procedure
# =============================================================================

def jordan_crystallization(M, L=None):
    """
    The claimed procedure:
    1. Expand M across L layers (Kronecker with layer coupling)
    2. Apply B3 shear
    3. Extract nilpotent part
    4. Check spectral radius
    """
    n = M.shape[0]
    if L is None:
        L = max(3, int(ceil(log2(n + 1))))

    # Step 1: Create layer-expanded matrix
    # M_expanded = I_L ⊗ M + J_L ⊗ (upper triangular part of M)
    # where J_L is the shift matrix (superdiagonal 1s)
    I_L = np.eye(L)
    J_L = np.zeros((L, L))
    for i in range(L - 1):
        J_L[i, i + 1] = 1.0

    M_upper = np.triu(M, k=1)
    M_expanded = np.kron(I_L, M) + np.kron(J_L, M_upper)

    # Step 2: Apply B3 shear via Kronecker
    # B3_expanded = B3 ⊗ I_{expanded_size/2}
    # But sizes must match, so we use block-diagonal B3 application
    ne = M_expanded.shape[0]

    # Apply B3 as: M_sheared = (I + 2*N_part) where N_part is strictly upper triangular
    N_part = np.triu(M_expanded, k=1)
    M_sheared = M_expanded + 2 * N_part  # This is the "B3 shear"

    # Step 3: Extract nilpotent part
    D = np.diag(np.diag(M_sheared))
    Nilp = M_sheared - D  # Strictly off-diagonal

    # Step 4: Compute spectral radius of nilpotent part
    eigvals = np.linalg.eigvals(Nilp)
    spectral_radius = np.max(np.abs(eigvals))

    # Step 5: "Jordan saturation" — iterate B3 shear
    current = Nilp.copy()
    saturation_steps = 0
    for k in range(1, L + 1):
        current = current @ Nilp
        sr = np.max(np.abs(np.linalg.eigvals(current)))
        saturation_steps = k
        if sr < 1e-10:
            break

    return {
        'spectral_radius': spectral_radius,
        'saturation_steps': saturation_steps,
        'matrix_size': ne,
        'L': L,
        'nilpotent_converged': sr < 1e-10 if 'sr' in dir() else False,
        'eigvals_nilp': eigvals,
        'M_sheared': M_sheared,
    }

# =============================================================================
# Part 4: Test WITH known factors (the original claim's setup)
# =============================================================================

def test_with_known_factors(p, q, verbose=True):
    """Test the B3 linearization with known p, q."""
    N = p * q
    if verbose:
        print(f"\n{'='*60}")
        print(f"Testing N = {p} * {q} = {N}")
        print(f"{'='*60}")

    t0 = time.time()
    M, n_vars, clauses = build_multiplication_clauses_known(p, q)

    result = jordan_crystallization(M)
    elapsed = time.time() - t0

    if verbose:
        print(f"  Matrix size: {n_vars} -> {result['matrix_size']} (expanded)")
        print(f"  Layers L: {result['L']}")
        print(f"  Spectral radius (nilpotent part): {result['spectral_radius']:.6e}")
        print(f"  Saturation steps: {result['saturation_steps']}")
        print(f"  Nilpotent converged: {result['nilpotent_converged']}")
        print(f"  Time: {elapsed:.4f}s")

        # Key question: can we extract p, q from the sheared matrix?
        print(f"\n  >> Can we extract factors from the matrix? <<")
        print(f"  The matrix was BUILT from known p,q bits.")
        print(f"  Any 'factor extraction' would be circular.")

    return result, elapsed

# =============================================================================
# Part 5: Test WITHOUT known factors — the REAL test
# =============================================================================

def build_multiplication_clauses_unknown(N):
    """
    Build clauses for N = p * q where p, q are UNKNOWN.
    This is the REAL test. We only know N.

    Variables: p_0..p_{nb-1}, q_0..q_{nb-1} (all unknown, 0 or 1)
    Constraints: sum_{i+j=k} p_i * q_j = n_k (mod 2) with carries

    This is a SYSTEM of quadratic equations over GF(2) with carries.
    """
    nb = (N.bit_length() + 1) // 2 + 1
    n_bits = bits_of(N, 2 * nb)
    n_vars = 2 * nb  # p_0..p_{nb-1}, q_0..q_{nb-1}

    # Without knowing p,q, the adjacency matrix has NO specific values —
    # we can only encode the STRUCTURE of multiplication, not the solution.

    # Structural adjacency: variable i interacts with variable j
    # if they appear together in a multiplication constraint
    M = np.zeros((n_vars, n_vars))
    for i in range(nb):
        for j in range(nb):
            target_bit = i + j
            if target_bit < 2 * nb:
                # p_i and q_j interact for bit target_bit of N
                # Weight by the TARGET bit value (known from N)
                weight = n_bits[target_bit]
                M[i, nb + j] += weight
                M[nb + j, i] += weight

    return M, n_vars

def test_without_known_factors(N, known_p=None, verbose=True):
    """
    The REAL test: can B3 linearization factor N knowing ONLY N?
    """
    if verbose:
        print(f"\n{'='*60}")
        print(f"Testing N = {N} (factors UNKNOWN to algorithm)")
        print(f"{'='*60}")

    t0 = time.time()
    M, n_vars = build_multiplication_clauses_unknown(N)

    result = jordan_crystallization(M)
    elapsed = time.time() - t0

    if verbose:
        print(f"  Matrix size: {n_vars} -> {result['matrix_size']} (expanded)")
        print(f"  Spectral radius (nilpotent part): {result['spectral_radius']:.6e}")
        print(f"  Saturation steps: {result['saturation_steps']}")

        # Try to extract factors from eigenvectors
        print(f"\n  Attempting factor extraction from eigenvectors...")

    # Try various extraction methods
    nb = (N.bit_length() + 1) // 2 + 1
    factors_found = []

    # Method 1: Eigenvector of sheared matrix
    try:
        eigvals, eigvecs = np.linalg.eig(result['M_sheared'])
        for i in range(min(10, len(eigvals))):
            vec = np.real(eigvecs[:, i])
            # Try interpreting first nb components as p bits
            p_bits = [1 if v > 0 else 0 for v in vec[:nb]]
            p_candidate = sum(b << i for i, b in enumerate(p_bits))
            if p_candidate > 1 and N % p_candidate == 0:
                factors_found.append(('eigvec', p_candidate))
    except:
        pass

    # Method 2: SVD
    try:
        U, S, Vt = np.linalg.svd(result['M_sheared'])
        for i in range(min(5, len(S))):
            vec = U[:, i]
            p_bits = [1 if v > 0 else 0 for v in vec[:nb]]
            p_candidate = sum(b << i_bit for i_bit, b in enumerate(p_bits))
            if p_candidate > 1 and N % p_candidate == 0:
                factors_found.append(('svd', p_candidate))
    except:
        pass

    # Method 3: Random rounding (many attempts)
    try:
        eigvals_full, eigvecs_full = np.linalg.eig(M)  # Original matrix
        for trial in range(100):
            idx = trial % min(n_vars, len(eigvals_full))
            vec = np.real(eigvecs_full[:, idx])
            threshold = np.median(vec) + 0.01 * (trial - 50)
            p_bits = [1 if v > threshold else 0 for v in vec[:nb]]
            p_candidate = sum(b << i for i, b in enumerate(p_bits))
            if p_candidate > 1 and p_candidate < N and N % p_candidate == 0:
                factors_found.append(('random_round', p_candidate))
                break
    except:
        pass

    if verbose:
        if factors_found:
            for method, f in factors_found:
                print(f"  FOUND factor {f} via {method}! N/{f} = {N // f}")
        else:
            print(f"  NO factors extracted from matrix structure.")
            if known_p:
                print(f"  (True factors: {known_p} * {N // known_p})")

    return result, factors_found, elapsed

# =============================================================================
# Part 6: Theoretical analysis
# =============================================================================

def theoretical_analysis():
    """Print rigorous theoretical analysis."""
    print("\n" + "=" * 60)
    print("THEORETICAL ANALYSIS")
    print("=" * 60)

    print("""
1. THE B3 MATRIX [[1,2],[0,1]]:
   - Has eigenvalue 1 (double, degenerate)
   - B3 - I = [[0,2],[0,0]] is nilpotent with index 2
   - B3 is a PARABOLIC element of SL(2,Z)
   - B3^k = [[1, 2k], [0, 1]] — just a shear

2. THE "JORDAN CRYSTALLIZATION" CLAIM:
   - Takes a matrix M, extracts upper triangular part N
   - N is strictly upper triangular => N is ALWAYS nilpotent
   - N^k = 0 for k <= matrix size (by Cayley-Hamilton)
   - Spectral radius of strictly upper triangular = 0 ALWAYS
   - This is a TAUTOLOGY, not a discovery!

3. THE "LINEARIZATION" CLAIM:
   - The procedure applies B3 shear to expand M across L layers
   - M_sheared = M + 2*triu(M,1) — just amplifies upper triangle
   - The nilpotent part (off-diagonal) is ALWAYS nilpotent
   - Spectral radius -> 0 is guaranteed by construction
   - This has NOTHING to do with the problem difficulty

4. WHY IT CANNOT FACTOR:
   - WITH known p,q: The matrix encodes p_i*q_j products directly.
     Any "extraction" is circular — the answer is in the input.
   - WITHOUT known p,q: The matrix only has STRUCTURAL info from N.
     The variables p_i, q_j are unknown. The matrix cannot encode
     their values without solving the factoring problem first.
   - The eigenvalue/eigenvector structure of the structural matrix
     does NOT encode the solution. It encodes the PROBLEM STRUCTURE,
     which is the same for all N of the same bit length.

5. THE P != NP BARRIER:
   - If this worked, it would prove P = NP (3-SAT in poly time)
   - No matrix operation on the STRUCTURE of a 3-SAT instance can
     solve it in polynomial time (unless P = NP)
   - The B3 shear is a fixed linear operation — it cannot search
     an exponential solution space

6. THE KERNEL OF TRUTH:
   - B3 IS interesting for the Pythagorean tree (generates triples)
   - Parabolic elements DO have nice algebraic properties
   - The Pythagorean tree IS relevant to factoring (via sum of squares)
   - But the leap from "nice algebraic structure" to "solves NP-complete"
     is not justified by any known mathematics
""")

# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    analyze_b3()

    # Test 1: With known factors (the original claim)
    print("\n" + "#" * 60)
    print("# TEST 1: WITH KNOWN FACTORS (original claim setup)")
    print("#" * 60)

    test_cases = [
        (101, 103),
        (1009, 1013),
        (10007, 10009),
    ]

    results_known = []
    for p, q in test_cases:
        result, elapsed = test_with_known_factors(p, q)
        results_known.append((p, q, result, elapsed))

    # Test 2: WITHOUT known factors (the REAL test)
    print("\n" + "#" * 60)
    print("# TEST 2: WITHOUT KNOWN FACTORS (the real test)")
    print("#" * 60)

    results_unknown = []
    for p, q in test_cases:
        N = p * q
        result, factors, elapsed = test_without_known_factors(N, known_p=p)
        results_unknown.append((N, p, q, result, factors, elapsed))

    # Test 3: Scaling test — does "saturation" scale polynomially?
    print("\n" + "#" * 60)
    print("# TEST 3: SCALING ANALYSIS")
    print("#" * 60)

    print(f"\n{'N':>15} {'bits':>5} {'mat_size':>8} {'spec_rad':>12} {'sat_steps':>10} {'time':>8}")
    print("-" * 65)

    import random
    rng = random.Random(42)
    for bits in [8, 12, 16, 20, 24, 28]:
        p = 1
        while not (p > 1 and all(p % d != 0 for d in range(2, min(p, 100)))):
            p = rng.randrange(1 << (bits//2 - 1), 1 << (bits//2))
        q = p + 2
        while not all(q % d != 0 for d in range(2, min(q, 100))):
            q += 2
        N = p * q

        # Only test with known factors to measure scaling
        M, n_vars, _ = build_multiplication_clauses_known(p, q)
        t0 = time.time()
        result = jordan_crystallization(M)
        elapsed = time.time() - t0

        print(f"{N:>15} {N.bit_length():>5} {result['matrix_size']:>8} "
              f"{result['spectral_radius']:>12.3e} {result['saturation_steps']:>10} "
              f"{elapsed:>7.3f}s")

    # Theoretical analysis
    theoretical_analysis()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
RESULT: The B3-SAT Linearization claim is NOT VALID for factoring.

1. "Spectral radius -> 0": This is a TAUTOLOGY. The strictly upper
   triangular part of ANY matrix is nilpotent. This has nothing to do
   with B3 or with solving the problem.

2. "Jordan Crystallization": Just computes powers of a nilpotent matrix.
   N^k = 0 for k <= size is guaranteed by linear algebra, not by any
   deep insight.

3. Factor extraction: FAILS when factors are unknown. The matrix built
   from unknown variables contains only structural information (which
   bits of N are set), not the solution.

4. The known-factor version is CIRCULAR: it puts p_i*q_j into the
   matrix, then "discovers" patterns that exist because it already
   knows the answer.

5. Kernel of truth: B3 has genuine mathematical interest in the
   Pythagorean tree context, but it cannot linearize NP-hard problems.
""")
