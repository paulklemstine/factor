#!/usr/bin/env python3
"""
ULTRA-DEEP ZIG-ZAG Pythagorean Tree Factoring

Algorithm:
  Phase 1: Jump astronomically deep via matrix exponentiation mod N
  Phase 2: Zig-zag — alternate climbing up (inverse matrices) and branching down
  Phase 3: Multi-start with different seed matrices

All arithmetic mod N using gmpy2 for speed.
"""

import gmpy2
import time
import random
import sys
from gmpy2 import mpz, gcd, invert

# ─── Berggren matrices (forward: parent→child) ───
# B1 = [[1,-2,2],[2,-1,2],[2,-2,3]]  but we only need (m,n) form
# For (m,n) pairs, the 3 Berggren child maps are:
#   B1: (m,n) → (2m-n, m)
#   B2: (m,n) → (2m+n, m)
#   B3: (m,n) → (m+2n, n)
#
# Inverse maps (child→parent):
#   B1⁻¹: (m,n) → (n, 2n-m)
#   B2⁻¹: (m,n) → (n, m-2n)
#   B3⁻¹: (m,n) → (m-2n, n)

# As 2x2 matrices on column vector [m; n]:
FORWARD_MATRICES = [
    ((mpz(2), mpz(-1)), (mpz(1), mpz(0))),   # B1: [2,-1; 1,0]
    ((mpz(2), mpz(1)),  (mpz(1), mpz(0))),    # B2: [2,1; 1,0]
    ((mpz(1), mpz(2)),  (mpz(0), mpz(1))),    # B3: [1,2; 0,1]
]

INVERSE_MATRICES = [
    ((mpz(0), mpz(1)),  (mpz(-1), mpz(2))),   # B1⁻¹: [0,1; -1,2]
    ((mpz(0), mpz(1)),  (mpz(1), mpz(-2))),    # B2⁻¹: [0,1; 1,-2]  — fixed sign
    ((mpz(1), mpz(-2)), (mpz(0), mpz(1))),     # B3⁻¹: [1,-2; 0,1]
]


def mat_mul_mod(A, B, N):
    """Multiply two 2x2 matrices mod N."""
    return (
        ((A[0][0]*B[0][0] + A[0][1]*B[1][0]) % N, (A[0][0]*B[0][1] + A[0][1]*B[1][1]) % N),
        ((A[1][0]*B[0][0] + A[1][1]*B[1][0]) % N, (A[1][0]*B[0][1] + A[1][1]*B[1][1]) % N),
    )


def mat_vec_mod(M, v, N):
    """Multiply 2x2 matrix by 2-vector mod N."""
    return ((M[0][0]*v[0] + M[0][1]*v[1]) % N,
            (M[1][0]*v[0] + M[1][1]*v[1]) % N)


def mat_pow_mod(M, exp, N):
    """Matrix exponentiation by repeated squaring, mod N."""
    result = ((mpz(1), mpz(0)), (mpz(0), mpz(1)))  # identity
    base = M
    while exp > 0:
        if exp & 1:
            result = mat_mul_mod(result, base, N)
        base = mat_mul_mod(base, base, N)
        exp >>= 1
    return result


def check_gcds(m, n, N):
    """Check all derived Pythagorean values for nontrivial gcd with N.
    Returns factor if found, else 0."""
    # Core values
    for val in (m, n, (m - n) % N, (m + n) % N):
        if val == 0:
            continue
        g = gcd(val, N)
        if 1 < g < N:
            return g

    # Pythagorean triple values: A = m²-n², B = 2mn, C = m²+n²
    m2 = m * m % N
    n2 = n * n % N
    A = (m2 - n2) % N
    B = (2 * m * n) % N
    C = (m2 + n2) % N
    for val in (A, B, C):
        if val == 0:
            continue
        g = gcd(val, N)
        if 1 < g < N:
            return g
    return mpz(0)


def build_seed_matrices(count=9):
    """Build diverse seed matrices from products of Berggren matrices."""
    seeds = []
    # Single matrices
    for M in FORWARD_MATRICES:
        seeds.append(M)
    if count <= 3:
        return seeds[:count]
    # Products of pairs
    for i in range(3):
        for j in range(3):
            if len(seeds) >= count:
                return seeds
            if i != j:
                # Use identity N=0 for building — will re-reduce later
                P = ((FORWARD_MATRICES[i][0][0]*FORWARD_MATRICES[j][0][0] + FORWARD_MATRICES[i][0][1]*FORWARD_MATRICES[j][1][0],
                      FORWARD_MATRICES[i][0][0]*FORWARD_MATRICES[j][0][1] + FORWARD_MATRICES[i][0][1]*FORWARD_MATRICES[j][1][1]),
                     (FORWARD_MATRICES[i][1][0]*FORWARD_MATRICES[j][0][0] + FORWARD_MATRICES[i][1][1]*FORWARD_MATRICES[j][1][0],
                      FORWARD_MATRICES[i][1][0]*FORWARD_MATRICES[j][0][1] + FORWARD_MATRICES[i][1][1]*FORWARD_MATRICES[j][1][1]))
                seeds.append(P)
    return seeds[:count]


def zigzag_factor(N, jump_depth=None, U=100, D=10, max_rounds=10000,
                  num_starts=3, time_limit=60.0, verbose=False):
    """
    Zig-zag Pythagorean tree factoring.

    Parameters:
        N           - number to factor
        jump_depth  - depth to jump via matrix exponentiation (default: 2^64)
        U           - steps to climb UP per zig-zag round
        D           - steps to go DOWN per zig-zag round
        max_rounds  - max zig-zag rounds per starting point
        num_starts  - number of different starting matrices to try
        time_limit  - wall-clock time limit in seconds
        verbose     - print progress
    """
    N = mpz(N)
    if N < 4:
        return 0, 0.0, 0

    # Trivial checks
    for p in (2, 3, 5, 7, 11, 13):
        if N % p == 0 and N // p > 1:
            return int(p), 0.0, 0

    if jump_depth is None:
        jump_depth = 1 << 64

    t0 = time.time()
    seeds = build_seed_matrices(num_starts)
    total_checks = 0
    rng = random.Random(42)

    for si, seed_mat in enumerate(seeds):
        if time.time() - t0 > time_limit:
            break

        # Phase 1: Jump deep
        # Reduce seed matrix mod N
        M = ((seed_mat[0][0] % N, seed_mat[0][1] % N),
             (seed_mat[1][0] % N, seed_mat[1][1] % N))

        # Compute M^jump_depth mod N
        Mpow = mat_pow_mod(M, jump_depth, N)

        # Apply to root (m=2, n=1)
        m, n = mat_vec_mod(Mpow, (mpz(2), mpz(1)), N)

        if verbose:
            elapsed = time.time() - t0
            print(f"  Start {si}: jumped to depth 2^{jump_depth.bit_length()-1 if isinstance(jump_depth, int) and jump_depth > 0 else '?'}, "
                  f"m={m % (10**8)}... n={n % (10**8)}... ({elapsed:.3f}s)")

        # Check initial point
        g = check_gcds(m, n, N)
        total_checks += 1
        if g:
            return int(g), time.time() - t0, total_checks

        # Phase 2: Zig-zag
        for rnd in range(max_rounds):
            if time.time() - t0 > time_limit:
                break

            # Climb UP: apply random inverse matrices
            for _ in range(U):
                idx = rng.randint(0, 2)
                inv = INVERSE_MATRICES[idx]
                m, n = mat_vec_mod(inv, (m, n), N)

                g = check_gcds(m, n, N)
                total_checks += 1
                if g:
                    return int(g), time.time() - t0, total_checks

            # Branch DOWN: apply random forward matrices
            for _ in range(D):
                idx = rng.randint(0, 2)
                fwd = FORWARD_MATRICES[idx]
                m, n = mat_vec_mod(fwd, (m, n), N)

                g = check_gcds(m, n, N)
                total_checks += 1
                if g:
                    return int(g), time.time() - t0, total_checks

        if verbose:
            print(f"  Start {si}: exhausted {max_rounds} rounds, {total_checks} checks")

    return 0, time.time() - t0, total_checks


def generate_semiprime(bits, rng=None):
    """Generate a semiprime of approximately `bits` total bits."""
    if rng is None:
        rng = random.Random()
    half = bits // 2
    while True:
        p = gmpy2.next_prime(mpz(rng.getrandbits(half)) | (mpz(1) << (half - 1)))
        q = gmpy2.next_prime(mpz(rng.getrandbits(half)) | (mpz(1) << (half - 1)))
        if p != q:
            N = p * q
            if N.bit_length() >= bits - 1:
                return N, p, q


def benchmark():
    """Run benchmark across bit sizes, jump depths, zig-zag ratios, and start counts."""
    bit_sizes = [32, 40, 48, 56, 64]
    jump_depths = [1 << 32, 1 << 64, 1 << 128, 1 << 256]
    zz_ratios = [(100, 10), (50, 50), (10, 100)]
    start_counts = [1, 3, 9]

    trials_per = 5
    time_limit_per = 30.0  # seconds per trial
    rng = random.Random(12345)

    print("=" * 90)
    print("ULTRA-DEEP ZIG-ZAG Pythagorean Tree Factoring — Benchmark")
    print("=" * 90)
    print()

    # ── Part 1: Vary jump depth (fixed U=100, D=10, starts=3) ──
    print("─" * 90)
    print("Part 1: Effect of Jump Depth  (U=100, D=10, starts=3)")
    print(f"{'Bits':>6}  {'JumpDepth':>12}  {'Solved':>8}  {'AvgTime':>10}  {'AvgChecks':>12}")
    print("─" * 90)

    for bits in bit_sizes:
        # Pre-generate semiprimes for fair comparison
        test_cases = [generate_semiprime(bits, rng) for _ in range(trials_per)]

        for jd in jump_depths:
            solved = 0
            total_time = 0.0
            total_checks = 0

            for N, p, q in test_cases:
                f, elapsed, checks = zigzag_factor(
                    N, jump_depth=jd, U=100, D=10,
                    max_rounds=5000, num_starts=3,
                    time_limit=time_limit_per
                )
                total_time += elapsed
                total_checks += checks
                if f > 1 and (N % f == 0):
                    solved += 1

            jd_label = f"2^{jd.bit_length()-1}"
            avg_t = total_time / trials_per
            avg_c = total_checks // trials_per
            print(f"{bits:>6}  {jd_label:>12}  {solved}/{trials_per:>5}  {avg_t:>9.3f}s  {avg_c:>12}")

    print()

    # ── Part 2: Vary zig-zag ratio (fixed jump=2^64, starts=3) ──
    print("─" * 90)
    print("Part 2: Effect of Zig-Zag Ratio  (jump=2^64, starts=3)")
    print(f"{'Bits':>6}  {'U/D':>10}  {'Solved':>8}  {'AvgTime':>10}  {'AvgChecks':>12}")
    print("─" * 90)

    for bits in bit_sizes:
        test_cases = [generate_semiprime(bits, rng) for _ in range(trials_per)]

        for U, D in zz_ratios:
            solved = 0
            total_time = 0.0
            total_checks = 0

            for N, p, q in test_cases:
                f, elapsed, checks = zigzag_factor(
                    N, jump_depth=(1 << 64), U=U, D=D,
                    max_rounds=5000, num_starts=3,
                    time_limit=time_limit_per
                )
                total_time += elapsed
                total_checks += checks
                if f > 1 and (N % f == 0):
                    solved += 1

            ratio_label = f"{U}/{D}"
            avg_t = total_time / trials_per
            avg_c = total_checks // trials_per
            print(f"{bits:>6}  {ratio_label:>10}  {solved}/{trials_per:>5}  {avg_t:>9.3f}s  {avg_c:>12}")

    print()

    # ── Part 3: Vary number of starts (fixed jump=2^64, U=100, D=10) ──
    print("─" * 90)
    print("Part 3: Effect of Multi-Start Count  (jump=2^64, U=100, D=10)")
    print(f"{'Bits':>6}  {'Starts':>8}  {'Solved':>8}  {'AvgTime':>10}  {'AvgChecks':>12}")
    print("─" * 90)

    for bits in bit_sizes:
        test_cases = [generate_semiprime(bits, rng) for _ in range(trials_per)]

        for ns in start_counts:
            solved = 0
            total_time = 0.0
            total_checks = 0

            for N, p, q in test_cases:
                f, elapsed, checks = zigzag_factor(
                    N, jump_depth=(1 << 64), U=100, D=10,
                    max_rounds=5000, num_starts=ns,
                    time_limit=time_limit_per
                )
                total_time += elapsed
                total_checks += checks
                if f > 1 and (N % f == 0):
                    solved += 1

            avg_t = total_time / trials_per
            avg_c = total_checks // trials_per
            print(f"{bits:>6}  {ns:>8}  {solved}/{trials_per:>5}  {avg_t:>9.3f}s  {avg_c:>12}")

    print()

    # ── Part 4: Best config vs baseline ──
    print("─" * 90)
    print("Part 4: Best Config Summary  (jump=2^64, U=50, D=50, starts=3)")
    print(f"{'Bits':>6}  {'Solved':>8}  {'AvgTime':>10}  {'AvgChecks':>12}")
    print("─" * 90)

    for bits in bit_sizes:
        test_cases = [generate_semiprime(bits, rng) for _ in range(trials_per)]
        solved = 0
        total_time = 0.0
        total_checks = 0

        for N, p, q in test_cases:
            f, elapsed, checks = zigzag_factor(
                N, jump_depth=(1 << 64), U=50, D=50,
                max_rounds=10000, num_starts=3,
                time_limit=time_limit_per
            )
            total_time += elapsed
            total_checks += checks
            if f > 1 and (N % f == 0):
                solved += 1

        avg_t = total_time / trials_per
        avg_c = total_checks // trials_per
        print(f"{bits:>6}  {solved}/{trials_per:>5}  {avg_t:>9.3f}s  {avg_c:>12}")

    print()
    print("=" * 90)
    print("Benchmark complete.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Quick single test
        N = mpz(sys.argv[2]) if len(sys.argv) > 2 else mpz(1000000007) * mpz(1000000009)
        print(f"Factoring N = {N} ({N.bit_length()} bits)")
        f, t, checks = zigzag_factor(N, verbose=True, time_limit=30)
        if f:
            print(f"  Factor: {f}, cofactor: {N // f}, time: {t:.3f}s, checks: {checks}")
        else:
            print(f"  No factor found in {t:.3f}s, {checks} checks")
    else:
        benchmark()
