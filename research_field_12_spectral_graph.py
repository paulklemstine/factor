"""Field 12: Spectral Graph Theory - Cayley Graphs of Z/NZ, Eigenvalue Gaps
Hypothesis: The Cayley graph of (Z/NZ, S) with generating set S has spectral properties
(eigenvalue gap, expansion) that depend on the factorization of N. For N=pq, the
graph decomposes as a tensor product of Cayley graphs of Z/pZ and Z/qZ. The spectral
gap might be detectable and could reveal factor sizes.
"""
import time, math, random
import numpy as np

def cayley_adjacency(N, generators):
    """Build adjacency matrix of Cayley graph Cay(Z/NZ, S)."""
    n = min(N, 500)  # Cap for memory
    A = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for g in generators:
            j = (i + g) % N
            if j < n:
                A[i, j] = 1
            j = (i - g) % N
            if j < n:
                A[i, j] = 1
    return A

def spectral_analysis(N, generators=[1, 2]):
    """Compute eigenvalues of Cayley graph and look for spectral gap."""
    if N > 500:
        return None, None, None

    A = cayley_adjacency(N, generators)
    eigs = np.sort(np.real(np.linalg.eigvalsh(A)))[::-1]

    # Spectral gap = lambda_1 - lambda_2
    gap = eigs[0] - eigs[1] if len(eigs) > 1 else 0

    # For Cayley graph of Z/NZ with generator {1,-1}:
    # eigenvalues are 2*cos(2*pi*k/N) for k=0,...,N-1
    # Spectral gap = 2 - 2*cos(2*pi/N) ~ 2*(pi/N)^2 for large N
    theoretical_gap = 2 - 2 * math.cos(2 * math.pi / N)

    return eigs, gap, theoretical_gap

def compare_prime_vs_composite(max_n=200):
    """Compare spectral gaps of Cayley graphs for primes vs composites."""
    primes = [n for n in range(5, max_n) if all(n % d != 0 for d in range(2, int(n**0.5)+1))]
    composites = [n for n in range(6, max_n) if not all(n % d != 0 for d in range(2, int(n**0.5)+1))]
    semiprimes = []
    for n in composites:
        factors = []
        temp = n
        for d in range(2, n):
            if temp % d == 0:
                factors.append(d)
                temp //= d
                if temp == 1:
                    break
        if len(factors) == 2 and factors[0] > 1 and factors[1] > 1:
            semiprimes.append(n)

    generators = [1]

    prime_gaps = []
    for p in primes[:30]:
        _, gap, _ = spectral_analysis(p, generators)
        if gap is not None:
            prime_gaps.append((p, gap))

    semiprime_gaps = []
    for n in semiprimes[:30]:
        _, gap, _ = spectral_analysis(n, generators)
        if gap is not None:
            semiprime_gaps.append((n, gap))

    return prime_gaps, semiprime_gaps

def tensor_product_test(p, q):
    """For N=pq, Cay(Z/NZ, {1}) should decompose as tensor product
    of Cay(Z/pZ, {1}) and Cay(Z/qZ, {1}).
    Eigenvalues of tensor product = products of eigenvalues.
    """
    N = p * q
    if N > 500:
        return None

    eigs_N, _, _ = spectral_analysis(N, [1])
    eigs_p, _, _ = spectral_analysis(p, [1])
    eigs_q, _, _ = spectral_analysis(q, [1])

    if eigs_N is None or eigs_p is None or eigs_q is None:
        return None

    # Tensor product eigenvalues
    tensor_eigs = sorted([ep + eq for ep in eigs_p for eq in eigs_q], reverse=True)

    # Compare (they should match up to reordering)
    # Actually for Cayley graph of Z/NZ ≅ Z/pZ × Z/qZ, the adjacency matrix
    # decomposes as A_p ⊗ I_q + I_p ⊗ A_q (Kronecker sum, not product)
    return eigs_N[:5], tensor_eigs[:5]

def experiment():
    print("=== Field 12: Spectral Graph Theory - Cayley Graphs ===\n")

    print("  Test 1: Spectral gap comparison (prime vs semiprime)")
    t0 = time.time()
    prime_gaps, semiprime_gaps = compare_prime_vs_composite(150)
    elapsed = time.time() - t0

    avg_prime_gap = np.mean([g for _, g in prime_gaps]) if prime_gaps else 0
    avg_semi_gap = np.mean([g for _, g in semiprime_gaps]) if semiprime_gaps else 0

    print(f"    Primes (n={len(prime_gaps)}): avg spectral gap = {avg_prime_gap:.6f}")
    print(f"    Semiprimes (n={len(semiprime_gaps)}): avg spectral gap = {avg_semi_gap:.6f}")
    print(f"    Ratio: {avg_semi_gap/avg_prime_gap:.4f}" if avg_prime_gap > 0 else "")
    print(f"    Time: {elapsed:.3f}s")

    print(f"\n    Sample prime gaps: {[(n, f'{g:.4f}') for n, g in prime_gaps[:5]]}")
    print(f"    Sample semiprime gaps: {[(n, f'{g:.4f}') for n, g in semiprime_gaps[:5]]}")

    # Key insight: spectral gap of Cay(Z/NZ, {1}) = 2 - 2*cos(2pi/N) ~ (2pi/N)^2
    # This depends ONLY on N, not on its factorization!
    print("\n    Key insight: spectral gap of Cay(Z/NZ, {1}) = 2 - 2cos(2pi/N)")
    print("    This depends ONLY on N, NOT on factorization.")
    print("    For same-sized N: gap(prime) ≈ gap(semiprime)")

    print("\n  Test 2: Tensor product decomposition")
    for p, q in [(3, 5), (5, 7), (7, 11), (11, 13)]:
        result = tensor_product_test(p, q)
        if result:
            eigs_N, tensor_eigs = result
            print(f"    N={p*q} = {p}*{q}:")
            print(f"      Direct eigs:  {[f'{e:.2f}' for e in eigs_N]}")
            print(f"      Tensor eigs:  {[f'{e:.2f}' for e in tensor_eigs]}")

    print("\nVERDICT: Spectral gap of Cayley graph Cay(Z/NZ, {1}) depends only on N,")
    print("not on its factorization. For other generating sets, the eigenvalues")
    print("CAN encode factor information (via tensor decomposition), but extracting")
    print("this requires eigenvalue computation on an N-dimensional matrix, which is")
    print("O(N^3) -- far worse than trial division O(sqrt(N)).")
    print("RESULT: REFUTED")

experiment()
