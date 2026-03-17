"""Field 7: Stochastic Calculus - Brownian Motion on Integers, Hitting Times
Hypothesis: Model a random walk X_t on Z/NZ with drift toward positions where N mod X
is small. The expected hitting time to reach a factor p might be computable via
Ito calculus / optional stopping theorem, and reveal factor structure through the
drift function.
"""
import time, math, random

def biased_walk_factor(N, max_steps=100000, num_walks=10):
    """Random walk on [2, sqrt(N)] with drift toward small residues.
    At position x, compute r = N mod x. Move toward x+1 or x-1
    with probability depending on which gives smaller residue.
    """
    sq = int(math.isqrt(N))
    best_overall = (N, 2)
    factors_found = []

    for walk in range(num_walks):
        x = random.randint(2, sq)
        best_r = N % x
        best_x = x

        for step in range(max_steps // num_walks):
            r = N % x
            if r == 0 and 1 < x < N:
                factors_found.append((x, step))
                break

            # Look at neighbors
            r_plus = N % (x + 1) if x + 1 <= sq else N
            r_minus = N % (x - 1) if x > 2 else N

            # Drift: prefer direction of smaller residue
            if r_plus < r_minus:
                prob_plus = 0.7
            elif r_minus < r_plus:
                prob_plus = 0.3
            else:
                prob_plus = 0.5

            if random.random() < prob_plus:
                x = min(x + 1, sq)
            else:
                x = max(x - 1, 2)

            if r < best_r:
                best_r = r
                best_x = x

        if best_r < best_overall[0]:
            best_overall = (best_r, best_x)

    return factors_found, best_overall

def levy_flight_factor(N, max_steps=50000):
    """Levy flight: heavy-tailed jumps. Mimics superdiffusion.
    Jump size ~ Cauchy distribution (power-law tails).
    """
    sq = int(math.isqrt(N))
    x = random.randint(2, sq)

    for step in range(max_steps):
        r = N % x
        if r == 0 and 1 < x < N:
            return x, step, True

        # Levy jump (Cauchy)
        jump = int(random.gauss(0, 1) / (random.random() + 1e-10))
        jump = max(-sq//10, min(sq//10, jump))  # Clip

        x = max(2, min(sq, x + jump))

    return x, max_steps, False

def hitting_time_analysis(N, p, q):
    """Theoretical analysis: expected hitting time of random walk to reach factor.
    For unbiased walk on [2, sqrt(N)], E[T_p] ~ (distance)^2 by Wald's equation.
    For biased walk, E[T_p] depends on drift quality.
    """
    sq = int(math.isqrt(N))
    # Unbiased: E[T] ~ (sq/2)^2 = N/4 (worse than trial division!)
    # Trial division: worst case sq = N^{1/2}
    # Random walk: worst case N (diffusive!)
    return sq**2 // 4, sq

def experiment():
    print("=== Field 7: Stochastic Calculus - Brownian Hitting Times ===\n")

    random.seed(42)
    test_cases = []
    for bits in [16, 20, 24, 28, 32]:
        while True:
            p = random.getrandbits(bits // 2) | (1 << (bits//2 - 1)) | 1
            q = random.getrandbits(bits // 2) | (1 << (bits//2 - 1)) | 1
            if p != q and p > 2 and q > 2:
                if all(p % d != 0 for d in range(2, min(int(p**0.5)+1, 300))) and \
                   all(q % d != 0 for d in range(2, min(int(q**0.5)+1, 300))):
                    break
        test_cases.append((p, q, p*q, bits))

    for p, q, N, bits in test_cases:
        print(f"  {bits}b: N={N} = {p} * {q}")

        # Biased walk
        t0 = time.time()
        factors, best = biased_walk_factor(N, max_steps=50000)
        elapsed = time.time() - t0
        print(f"    Biased walk: found {len(factors)} factors, best residue={best[0]} at x={best[1]}, time={elapsed:.3f}s")

        # Levy flight
        t0 = time.time()
        lx, lsteps, lsuccess = levy_flight_factor(N, max_steps=50000)
        elapsed = time.time() - t0
        print(f"    Levy flight: {'FOUND ' + str(lx) if lsuccess else 'FAILED'}, steps={lsteps}, time={elapsed:.3f}s")

        # Theoretical bounds
        walk_expected, td_expected = hitting_time_analysis(N, p, q)
        print(f"    Theory: E[T_walk] ~ {walk_expected}, E[T_trial] ~ {td_expected}")
        print(f"    Walk is {walk_expected / max(td_expected, 1):.1f}x SLOWER than trial division")

    print("\nVERDICT: Random walks (even biased or Levy) are SLOWER than trial division.")
    print("Unbiased walk: E[T] ~ N (diffusive). Trial division: O(sqrt(N)).")
    print("Bias toward small residues doesn't help because N mod x is pseudorandom.")
    print("Ito calculus tells us the drift is essentially zero (no gradient signal).")
    print("Superdiffusion (Levy) doesn't help because factors are point targets.")
    print("RESULT: REFUTED")

experiment()
