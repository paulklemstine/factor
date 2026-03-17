"""Field 4: Ergodic Theory - Mixing Times of Multiplicative Systems mod N
Hypothesis: The multiplicative map x -> ax mod N has mixing properties that depend
on the factorization of N. Specifically, the mixing time (how fast the orbit
{a^k mod N} becomes equidistributed) might reveal factor structure via discrepancy
in convergence rates for different generators a.
"""
import time, math, random

def multiplicative_orbit(a, N, max_steps=10000):
    """Compute orbit of a under x -> a*x mod N, starting from 1."""
    seen = {}
    x = 1
    orbit = [x]
    for step in range(1, max_steps):
        x = (a * x) % N
        if x in seen:
            return orbit, seen[x], step  # orbit, cycle_start, cycle_len
        seen[x] = step
        orbit.append(x)
    return orbit, -1, max_steps

def mixing_discrepancy(orbit, N, num_bins=20):
    """Measure how uniformly the orbit covers [0, N)."""
    bins = [0] * num_bins
    for x in orbit:
        bins[int(x * num_bins / N)] += 1
    expected = len(orbit) / num_bins
    if expected == 0:
        return float('inf')
    discrepancy = sum(abs(b - expected) for b in bins) / (len(orbit))
    return discrepancy

def experiment():
    print("=== Field 4: Ergodic Theory - Mixing Times mod N ===\n")

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

        # Test multiple generators
        generators = [2, 3, 5, 7, 11, 13]
        results = []

        for a in generators:
            if math.gcd(a, N) > 1:
                # Generator shares a factor - instant win
                g = math.gcd(a, N)
                print(f"    a={a}: gcd(a,N)={g} -- TRIVIAL FACTOR (this is trial division)")
                continue

            t0 = time.time()
            orbit, cyc_start, cyc_end = multiplicative_orbit(a, N)
            orbit_len = len(orbit)

            # Order of a mod N
            order = cyc_end - cyc_start if cyc_start >= 0 else orbit_len

            # Mixing quality
            disc = mixing_discrepancy(orbit[:min(1000, len(orbit))], N)

            # Key test: does order mod N relate to order mod p or mod q?
            # By CRT: ord_N(a) = lcm(ord_p(a), ord_q(a))
            # If we could detect that ord_N factors as lcm of two orders,
            # we could factor N. But detecting this requires knowing ord_N first.
            elapsed = time.time() - t0

            results.append((a, order, disc))
            print(f"    a={a}: order={order}, discrepancy={disc:.4f}, time={elapsed:.4f}s")

        # Test: do different generators reveal factor structure?
        if len(results) >= 2:
            orders = [r[1] for r in results]
            # GCD of pairs of (a^ord - 1, N) might reveal factors
            for i in range(len(results)):
                for j in range(i+1, len(results)):
                    a1, ord1, _ = results[i]
                    a2, ord2, _ = results[j]
                    g = math.gcd(ord1, ord2)
                    if g > 1:
                        # Try: gcd(a^(ord/g) - 1, N)
                        half_ord = ord1 // 2 if ord1 % 2 == 0 else ord1
                        val = pow(a1, half_ord, N) - 1
                        factor = math.gcd(val, N)
                        if 1 < factor < N:
                            print(f"    ** FACTOR from order halving: {factor} **")

    print("\nVERDICT: Mixing times and orbit discrepancies are determined by")
    print("multiplicative orders mod N. Computing orders IS the factoring problem")
    print("(equivalent to period-finding). Ergodic properties don't shortcut this.")
    print("The mixing time approach reduces to Shor's algorithm (without quantum).")
    print("RESULT: REFUTED")

experiment()
