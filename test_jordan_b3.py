#!/usr/bin/env python3
"""
Test the B3-MPQS Jordan Crystallization paper claims.

The paper claims:
1. Construct logic matrix M for ripple-carry multiplier of N=p*q
2. Apply temporal unrolling (L layers) to eliminate cycles
3. Apply B3 shear S = I + 2N (nilpotent shift)
4. The result has a large Jordan block ("Jordan Saturation")
5. When saturation > 85%, backward substitution recovers p, q
6. Complexity: O(L * bits^3) — polynomial time

We test:
A. Does the Jordan block actually encode p and q?
B. Can backward substitution recover factors?
C. Does it scale beyond 14 bits?
"""

import numpy as np
import time
import sys
from scipy import linalg as sp_linalg


def build_multiplier_matrix(n_bits_p, n_bits_q):
    """
    Build the logic matrix M for an n_bits_p x n_bits_q ripple-carry multiplier.

    Variables: p bits (p0..p_{np-1}), q bits (q0..q_{nq-1}),
               partial products, carries, output bits.

    Each row of M represents a linear dependency between variables.
    Since AND (partial products) is nonlinear, we encode it as a
    bilinear constraint: pp_{i,j} = p_i * q_j.

    For the linear part (XOR/addition), we build the adjacency matrix
    of the carry-ripple DAG.
    """
    total_bits = n_bits_p + n_bits_q
    n_pp = n_bits_p * n_bits_q  # partial products
    n_carries = max(0, total_bits - 1)  # carry bits
    n_outputs = total_bits  # output bits (N)

    dim = n_bits_p + n_bits_q + n_pp + n_carries + n_outputs

    # Variable indexing
    p_start = 0
    q_start = n_bits_p
    pp_start = n_bits_p + n_bits_q
    carry_start = pp_start + n_pp
    out_start = carry_start + n_carries

    M = np.zeros((dim, dim), dtype=np.float64)

    # Partial product dependencies: pp_{i,j} depends on p_i and q_j
    for i in range(n_bits_p):
        for j in range(n_bits_q):
            pp_idx = pp_start + i * n_bits_q + j
            M[pp_idx, p_start + i] = 1.0
            M[pp_idx, q_start + j] = 1.0

    # Column addition: for each output bit position k,
    # sum the partial products where i+j=k, plus carry_in
    # output_k = sum XOR carry
    for k in range(total_bits):
        out_idx = out_start + k
        # Partial products contributing to column k
        for i in range(n_bits_p):
            j = k - i
            if 0 <= j < n_bits_q:
                pp_idx = pp_start + i * n_bits_q + j
                M[out_idx, pp_idx] = 1.0
        # Carry in from column k-1
        if k > 0 and (k - 1) < n_carries:
            M[out_idx, carry_start + k - 1] = 1.0
        # Carry out to column k+1
        if k < n_carries:
            carry_idx = carry_start + k
            for i in range(n_bits_p):
                j = k - i
                if 0 <= j < n_bits_q:
                    pp_idx = pp_start + i * n_bits_q + j
                    M[carry_idx, pp_idx] = 0.5  # carry weight
            if k > 0 and (k - 1) < n_carries:
                M[carry_idx, carry_start + k - 1] = 0.5

    return M, dim, {
        'p_start': p_start, 'q_start': q_start,
        'pp_start': pp_start, 'carry_start': carry_start,
        'out_start': out_start, 'n_bits_p': n_bits_p,
        'n_bits_q': n_bits_q, 'total_bits': total_bits,
    }


def temporal_unroll(M, dim, L):
    """
    Temporal unrolling: expand dim x dim matrix into (dim*L) x (dim*L)
    by creating L copies with inter-layer connections.

    Layer l feeds into layer l+1 via M.
    This converts feedback cycles into a feed-forward DAG.
    """
    big_dim = dim * L
    # Memory check: big_dim^2 * 8 bytes
    mem_bytes = big_dim * big_dim * 8
    if mem_bytes > 4_000_000_000:  # 4GB limit
        raise MemoryError(f"Matrix would use {mem_bytes/1e9:.1f}GB — too large")

    U = np.zeros((big_dim, big_dim), dtype=np.float64)

    for l in range(L - 1):
        row_off = (l + 1) * dim
        col_off = l * dim
        U[row_off:row_off + dim, col_off:col_off + dim] = M

    return U, big_dim


def apply_b3_shear(U, big_dim):
    """
    Apply the B3 shear: S = I + 2*N where N is the nilpotent part.
    The paper claims this "aligns carry bit drift."

    Since U is already nilpotent (strictly lower triangular after unrolling),
    the shear is S = I + 2*U.
    """
    S = np.eye(big_dim) + 2.0 * U
    return S


def jordan_analysis(M_transformed, big_dim):
    """
    Compute Jordan normal form and measure "saturation."

    Jordan Saturation = (largest Jordan block size) / big_dim * 100%
    """
    # For large matrices, eigenvalue decomposition is more practical
    eigenvalues = np.linalg.eigvals(M_transformed)

    # For nilpotent matrices, all eigenvalues should be ~0
    spectral_radius = np.max(np.abs(eigenvalues))

    # Jordan block size: for a nilpotent matrix N, the largest Jordan block
    # size equals the nilpotency index (smallest k where N^k = 0)
    N_mat = M_transformed - np.eye(big_dim)  # extract nilpotent part

    # Find nilpotency index
    power = np.eye(big_dim)
    max_block = 0
    for k in range(1, big_dim + 1):
        power = power @ N_mat
        norm = np.linalg.norm(power, ord='fro')
        if norm < 1e-10:
            max_block = k
            break
    else:
        max_block = big_dim

    saturation = max_block / big_dim * 100.0
    return spectral_radius, max_block, saturation


def try_backward_substitution(M_transformed, big_dim, N_val, info, L):
    """
    The paper claims backward substitution on the Jordan chain recovers p, q.
    Try it and see if we can extract factors.
    """
    n_bits_p = info['n_bits_p']
    n_bits_q = info['n_bits_q']
    total_bits = info['total_bits']
    dim = big_dim // L

    # Set output bits to N's binary representation in the last layer
    b = np.zeros(big_dim)
    last_layer = (L - 1) * dim
    for bit in range(total_bits):
        if N_val & (1 << bit):
            b[last_layer + info['out_start'] + bit] = 1.0

    # Try to solve: M_transformed @ x = b (or least squares)
    try:
        x, residuals, rank, sv = np.linalg.lstsq(M_transformed, b, rcond=None)
    except np.linalg.LinAlgError:
        return None, None

    # Extract p and q from the first layer
    p_bits = x[info['p_start']:info['p_start'] + n_bits_p]
    q_bits = x[info['q_start']:info['q_start'] + n_bits_q]

    # Round to binary
    p_val = 0
    for i in range(n_bits_p):
        if p_bits[i] > 0.5:
            p_val |= (1 << i)

    q_val = 0
    for i in range(n_bits_q):
        if q_bits[i] > 0.5:
            q_val |= (1 << i)

    return p_val, q_val


def test_factoring(N, p_true, q_true, L=30, verbose=True):
    """
    Full test of the paper's claims for a given semiprime N = p * q.
    """
    n_bits_p = p_true.bit_length()
    n_bits_q = q_true.bit_length()
    total_bits = N.bit_length()

    if verbose:
        print(f"\n{'='*60}")
        print(f"N = {N} = {p_true} x {q_true}")
        print(f"Bits: p={n_bits_p}, q={n_bits_q}, N={total_bits}")
        print(f"Layers: L={L}")

    t0 = time.time()

    # Step 1: Build multiplier matrix
    M, dim, info = build_multiplier_matrix(n_bits_p, n_bits_q)
    if verbose:
        print(f"Step 1: Multiplier matrix: {dim}x{dim}")

    # Step 2: Temporal unrolling
    try:
        U, big_dim = temporal_unroll(M, dim, L)
    except MemoryError as e:
        if verbose:
            print(f"  ABORT: {e}")
        return False, 0, 0, 0

    if verbose:
        print(f"Step 2: Unrolled: {big_dim}x{big_dim} "
              f"({big_dim*big_dim*8/1e6:.0f} MB)")

    # Step 3: Apply B3 shear
    S = apply_b3_shear(U, big_dim)
    if verbose:
        print(f"Step 3: B3 shear applied")

    # Step 4: Jordan analysis
    spectral_radius, max_block, saturation = jordan_analysis(S, big_dim)
    if verbose:
        print(f"Step 4: Spectral radius = {spectral_radius:.6f}")
        print(f"        Max Jordan block = {max_block}")
        print(f"        Jordan Saturation = {saturation:.2f}%")

    # Step 5: Backward substitution
    p_found, q_found = try_backward_substitution(S, big_dim, N, info, L)

    elapsed = time.time() - t0

    success = False
    if p_found and q_found:
        product = p_found * q_found
        if product == N:
            success = True
            if verbose:
                print(f"Step 5: FACTORED! p={p_found}, q={q_found} ({elapsed:.2f}s)")
        else:
            if verbose:
                print(f"Step 5: Got p={p_found}, q={q_found}, "
                      f"but {p_found}*{q_found}={product} != {N}")
                # Also try swapping and other combinations
                if p_found * q_true == N or q_found * p_true == N:
                    print(f"  (Partial match found)")
    else:
        if verbose:
            print(f"Step 5: Backward substitution failed ({elapsed:.2f}s)")

    return success, saturation, max_block, elapsed


# ===== Main =====
if __name__ == "__main__":
    print("=" * 60)
    print("Testing B3-MPQS Jordan Crystallization Paper")
    print("=" * 60)

    # Test 1: The paper's own example
    print("\n--- TEST 1: Paper's example (N=10403 = 101 * 103) ---")
    test_factoring(10403, 101, 103, L=30)

    # Test 2: Smaller example to verify
    print("\n--- TEST 2: Tiny (N=15 = 3 * 5) ---")
    test_factoring(15, 3, 5, L=10)

    # Test 3: Another small one
    print("\n--- TEST 3: Small (N=143 = 11 * 13) ---")
    test_factoring(143, 11, 13, L=15)

    # Test 4: Scale up slightly
    print("\n--- TEST 4: Medium (N=10007 * 10009 = 100160063) ---")
    test_factoring(100160063, 10007, 10009, L=10)

    # Test 5: Does saturation actually help?
    print("\n--- TEST 5: Saturation vs L for N=10403 ---")
    for L in [5, 10, 15, 20, 30, 50]:
        success, sat, block, t = test_factoring(10403, 101, 103, L=L, verbose=False)
        status = "FACTORED" if success else "FAILED"
        print(f"  L={L:3d}: sat={sat:.1f}%, block={block}, "
              f"time={t:.2f}s — {status}")

    # Test 6: Scaling test — does it work for larger N?
    print("\n--- TEST 6: Scaling test ---")
    import random
    from gmpy2 import next_prime, mpz
    rng = random.Random(42)

    for target_bits in [8, 12, 16, 20, 24]:
        half = target_bits // 2
        p = int(next_prime(mpz(rng.getrandbits(half))))
        q = int(next_prime(mpz(rng.getrandbits(half))))
        N = p * q
        actual_bits = N.bit_length()

        # Use L proportional to bits for "fair" test
        L = min(30, max(5, actual_bits))

        success, sat, block, t = test_factoring(N, p, q, L=L, verbose=False)
        status = "FACTORED" if success else "FAILED"
        print(f"  {actual_bits:2d}b (N={N}): sat={sat:.1f}%, "
              f"time={t:.2f}s — {status}")

    print("\n" + "=" * 60)
    print("CONCLUSION: Does Jordan Crystallization factor semiprimes?")
    print("=" * 60)
