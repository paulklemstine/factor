#!/usr/bin/env python3
"""Pythagorean tree multi-GCD factoring for arbitrary-size N (pure Python)."""
import math, random, time, sys

FORWARD_MATS = [
    (2, -1, 1,  0),  (2,  1, 1,  0),  (1,  2, 0,  1),
    (1,  1, 0,  2),  (2,  0, 1, -1),  (2,  0, 1,  1),
    (3, -2, 1, -1),  (3,  2, 1,  1),  (1,  4, 0,  1),
]

def mat_apply(M, m, n, N):
    a00, a01, a10, a11 = M
    return (a00 * m + a01 * n) % N, (a10 * m + a11 * n) % N

def pyth_factor_bigint(N, K=512, time_limit_s=120, verbose=True):
    """Multi-GCD birthday collision on Pythagorean tree, pure Python."""
    if N < 4:
        return 0, 0.0
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47):
        if N % p == 0 and N // p > 1:
            return p, 0.0

    t0 = time.time()
    rng = random.Random()

    # Initialize K walks from random positions
    walks = []
    for i in range(K):
        m, n = 2, 1
        for _ in range(3 + rng.randint(0, 24)):
            m, n = mat_apply(FORWARD_MATS[rng.randint(0, 8)], m, n, N)
        walks.append((m, n))

    rounds = 0
    while True:
        elapsed = time.time() - t0
        if elapsed >= time_limit_s:
            break

        # Advance all walks
        for i in range(K):
            m, n = walks[i]
            m, n = mat_apply(FORWARD_MATS[rng.randint(0, 8)], m, n, N)
            walks[i] = (m, n)

        rounds += 1

        # Pairwise batch GCD (subsample for speed)
        prod = 1
        count = 0
        # Check all pairs for small K, subsample for large K
        pairs = min(K * (K - 1) // 2, 2000)
        checked = set()
        for _ in range(pairs):
            i = rng.randint(0, K - 1)
            j = rng.randint(0, K - 2)
            if j >= i: j += 1
            key = (min(i,j), max(i,j))
            if key in checked: continue
            checked.add(key)

            dm = (walks[i][0] - walks[j][0]) % N
            if dm != 0:
                prod = prod * dm % N
                count += 1
            dn = (walks[i][1] - walks[j][1]) % N
            if dn != 0:
                prod = prod * dn % N
                count += 1

            if count >= 32:
                g = math.gcd(prod, N)
                if 1 < g < N:
                    elapsed = time.time() - t0
                    if verbose:
                        print(f"  Found factor in {elapsed:.1f}s, {rounds} rounds, {K} walks")
                    return g, elapsed
                if g == N:
                    # Overshot - check individual
                    for ii in range(K):
                        for jj in range(ii+1, K):
                            d = (walks[ii][0] - walks[jj][0]) % N
                            if d:
                                g2 = math.gcd(d, N)
                                if 1 < g2 < N:
                                    return g2, time.time() - t0
                prod = 1
                count = 0

        if count > 0:
            g = math.gcd(prod, N)
            if 1 < g < N:
                return g, time.time() - t0

        if verbose and rounds % 100 == 0:
            print(f"  Round {rounds}, {time.time()-t0:.1f}s...", flush=True)

    return 0, time.time() - t0


if __name__ == "__main__":
    sys.path.insert(0, "/home/raver1975/factor")
    from rsa_targets import MILESTONES

    print("=" * 70)
    print("RSA Targets — Pythagorean Tree Multi-GCD (2-min timeout)")
    print("=" * 70)

    results = []
    for name, (N, digits, bits, status) in sorted(MILESTONES.items(), key=lambda x: x[1][1]):
        print(f"\n{name} ({digits}d / {bits}b) — {status}")
        f, elapsed = pyth_factor_bigint(N, K=256, time_limit_s=120, verbose=True)
        if f > 1 and f < N and N % f == 0:
            print(f"  => FACTORED: {f}  [{elapsed:.1f}s]")
            results.append((name, digits, bits, elapsed, True))
        else:
            print(f"  => Not factored in {elapsed:.1f}s")
            results.append((name, digits, bits, elapsed, False))
        sys.stdout.flush()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for name, digits, bits, elapsed, solved in results:
        tag = f"SOLVED ({elapsed:.1f}s)" if solved else f"FAIL ({elapsed:.1f}s)"
        print(f"  {name:>10s} ({digits:3d}d / {bits:4d}b): {tag}")

    # Pick lowest unsolved for 1-hour run
    unsolved = [(n, d, b) for n, d, b, e, s in results if not s]
    if unsolved:
        pick = unsolved[0]
        print(f"\nLowest unsolved: {pick[0]} ({pick[1]}d)")
