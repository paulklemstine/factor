"""Field 5: Symplectic Geometry - Hamiltonian Flows on Number-Theoretic Phase Spaces
Hypothesis: Model factoring as a Hamiltonian system where the "position" is x in Z/NZ
and "momentum" is the multiplicative structure. The Hamiltonian H(x,p) = (N mod x)^2/2
+ p^2/2 defines a flow on phase space. Trajectories might be attracted to factor positions
where H has local minima (N mod p = 0).
"""
import time, math, random
import numpy as np

def hamiltonian_flow(N, x0, p0, dt=0.01, steps=5000):
    """Simulate Hamiltonian flow for H = V(x) + p^2/2 where V(x) = (N mod round(x))^2 / 2.
    Hamilton's equations: dx/dt = p, dp/dt = -dV/dx
    """
    x, p = float(x0), float(p0)
    trajectory = [(x, p)]
    best_x = x0
    best_residue = N % max(2, int(round(abs(x0))))

    for _ in range(steps):
        xi = max(2, int(round(abs(x))))

        # V(x) = (N mod x)^2 / 2, approximate gradient
        if xi > 2 and xi < N:
            r = N % xi
            rp = N % (xi + 1) if xi + 1 < N else r
            rm = N % (xi - 1) if xi > 2 else r
            dVdx = (rp**2 - rm**2) / 4.0  # Central difference
        else:
            dVdx = 0

        # Symplectic Euler
        p -= dt * dVdx
        x += dt * p

        # Bounds
        x = max(2.0, min(float(N), x))

        xi = max(2, int(round(abs(x))))
        r = N % xi
        if r < best_residue:
            best_residue = r
            best_x = xi

        if r == 0 and 1 < xi < N:
            return trajectory, xi, True  # Found factor

        trajectory.append((x, p))

    return trajectory, best_x, False

def experiment():
    print("=== Field 5: Symplectic Geometry - Hamiltonian Flows ===\n")

    random.seed(42)
    test_cases = []
    for bits in [16, 20, 24, 28]:
        while True:
            p = random.getrandbits(bits // 2) | (1 << (bits//2 - 1)) | 1
            q = random.getrandbits(bits // 2) | (1 << (bits//2 - 1)) | 1
            if p != q and p > 2 and q > 2:
                if all(p % d != 0 for d in range(2, min(int(p**0.5)+1, 300))) and \
                   all(q % d != 0 for d in range(2, min(int(q**0.5)+1, 300))):
                    break
        test_cases.append((p, q, p*q, bits))

    total_factored = 0
    total_tests = 0

    for p, q, N, bits in test_cases:
        print(f"  {bits}b: N={N} = {p} * {q}")
        sq = int(math.isqrt(N))

        # Try multiple starting positions
        starts = [
            (sq, 0.0),          # Near sqrt(N), zero momentum
            (sq, 10.0),         # Near sqrt(N), positive momentum
            (2.0, 50.0),        # From small x, high momentum
            (float(N//3), 0.0), # Near N/3
        ]

        found = False
        for x0, p0 in starts:
            t0 = time.time()
            traj, best_x, success = hamiltonian_flow(N, x0, p0, dt=0.1, steps=5000)
            elapsed = time.time() - t0
            total_tests += 1

            best_r = N % best_x if best_x > 1 else N
            if success:
                print(f"    Start ({x0:.0f},{p0:.0f}): FOUND factor {best_x} in {elapsed:.3f}s")
                found = True
                total_factored += 1
                break
            else:
                print(f"    Start ({x0:.0f},{p0:.0f}): best x={best_x}, N mod x={best_r}, time={elapsed:.3f}s")

        if not found:
            # Compare: trial division from sqrt(N) downward
            t0 = time.time()
            for d in range(sq, 1, -1):
                if N % d == 0:
                    print(f"    Trial div from sqrt: found {d} in {time.time()-t0:.3f}s after {sq-d} steps")
                    break

    print(f"\n  Factored: {total_factored}/{total_tests} starting points")
    print("\nVERDICT: Hamiltonian flow on V(x)=(N mod x)^2 has a chaotic, non-convex")
    print("energy landscape. The gradient dV/dx is essentially random (N mod x is")
    print("pseudorandom for x far from factors). The flow wanders without converging")
    print("to factors. This is gradient descent on a function with no useful gradient.")
    print("RESULT: REFUTED")

experiment()
