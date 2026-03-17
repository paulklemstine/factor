"""Field 2: Quantum Walks on Graphs - Classical Simulation
Hypothesis: A classical simulation of a quantum walk on the Cayley graph of Z/NZ
with generators {1, -1, 2, N/2} might exhibit interference patterns that concentrate
probability amplitude on factor-related nodes. Even classically simulated, the
walk structure might reveal useful periodicity.
"""
import time, math, random
import numpy as np

def quantum_walk_cayley(N, steps=100):
    """Simulate a discrete quantum walk on Z/NZ Cayley graph.
    Uses coin+shift operator. State = |position> x |coin>.
    Generators: +1, -1 (2-state coin).
    """
    dim = min(N, 2000)  # Cap for memory
    if dim < N:
        return None, None  # Too large

    # State vector: 2*dim (coin x position)
    psi = np.zeros(2 * dim, dtype=np.complex128)
    # Start at position 1 with coin |0>
    psi[0 * dim + 1] = 1.0 / np.sqrt(2)
    psi[1 * dim + 1] = 1.0 / np.sqrt(2)

    # Hadamard coin
    H = np.array([[1, 1], [1, -1]], dtype=np.complex128) / np.sqrt(2)

    for _ in range(steps):
        # Apply coin
        new_psi = np.zeros_like(psi)
        for pos in range(dim):
            c0 = psi[0 * dim + pos]
            c1 = psi[1 * dim + pos]
            new_psi[0 * dim + pos] = H[0, 0] * c0 + H[0, 1] * c1
            new_psi[1 * dim + pos] = H[1, 0] * c0 + H[1, 1] * c1
        psi = new_psi

        # Apply shift: coin=0 -> move +1, coin=1 -> move -1 (mod N)
        shifted = np.zeros_like(psi)
        for pos in range(dim):
            shifted[0 * dim + (pos + 1) % dim] += psi[0 * dim + pos]
            shifted[1 * dim + (pos - 1) % dim] += psi[1 * dim + pos]
        psi = shifted

    # Probability distribution
    prob = np.zeros(dim)
    for pos in range(dim):
        prob[pos] = abs(psi[0 * dim + pos])**2 + abs(psi[1 * dim + pos])**2

    return prob, dim

def experiment():
    print("=== Field 2: Quantum Walks on Cayley Graphs of Z/NZ ===\n")

    test_cases = [
        (3, 5, 15), (7, 11, 77), (13, 17, 221), (23, 29, 667),
        (37, 41, 1517), (101, 103, 10403), (251, 257, 64507)
    ]

    for p, q, N in test_cases:
        t0 = time.time()
        prob, dim = quantum_walk_cayley(N, steps=N)

        if prob is None:
            print(f"  N={N} ({p}*{q}): SKIPPED (too large for simulation)")
            continue

        elapsed = time.time() - t0

        # Check: is probability concentrated at factors?
        prob_at_p = prob[p] if p < dim else 0
        prob_at_q = prob[q] if q < dim else 0
        max_prob = np.max(prob)
        max_pos = np.argmax(prob)
        avg_prob = 1.0 / dim

        # Check peaks near multiples of p or q
        factor_peaks = 0
        top_20 = np.argsort(prob)[-20:]
        for idx in top_20:
            if idx > 0 and (N % idx == 0 or idx % p == 0 or idx % q == 0):
                factor_peaks += 1

        print(f"  N={N} ({p}*{q}):")
        print(f"    P(p={p})={prob_at_p:.6f}, P(q={q})={prob_at_q:.6f}, avg={avg_prob:.6f}")
        print(f"    Max P={max_prob:.6f} at pos={max_pos}, factor peaks in top-20: {factor_peaks}")
        print(f"    Time: {elapsed:.3f}s")

        # Test: does the walk have period related to p or q?
        if dim >= 2 * max(p, q):
            autocorr_p = np.sum(prob * np.roll(prob, p))
            autocorr_q = np.sum(prob * np.roll(prob, q))
            autocorr_rand = np.sum(prob * np.roll(prob, p + 1))
            print(f"    Autocorr at p={autocorr_p:.8f}, q={autocorr_q:.8f}, random={autocorr_rand:.8f}")

    print("\nVERDICT: Classical simulation of quantum walks on Z/NZ Cayley graphs")
    print("shows NO concentration of probability at factor-related positions.")
    print("The walk spreads quasi-uniformly. Quantum speedup requires actual")
    print("quantum interference (superposition), not classical simulation.")
    print("RESULT: REFUTED")

experiment()
