#!/usr/bin/env python3
"""
Factoring Research v5: 20 Radically Different Moonshot Paradigms
Each: 3-line hypothesis, tiny experiment (<40 lines, <1GB RAM, <10s), classify.
"""

import math, time, random, sys
from collections import defaultdict

# Test semiprimes of increasing size
TEST_NS = [
    (15, 3, 5),           # 4-bit
    (143, 11, 13),        # 8-bit
    (10573, 89, 119),     # ~14-bit  (89*119=10591, fix below)
    (100127, 293, 341),   # ~17-bit  (fix below)
]
# Use verified semiprimes
TEST_NS = []
for bits in [8, 16, 24, 32, 40]:
    random.seed(bits)
    from sympy import nextprime, isprime
    p = nextprime(random.randint(2**(bits//2-1), 2**(bits//2)))
    q = nextprime(p + random.randint(1, 2**(bits//2-1)))
    TEST_NS.append((p * q, p, q))

results = {}

def timed(func, *args, timeout=10.0):
    t0 = time.time()
    try:
        r = func(*args)
        return r, time.time() - t0
    except Exception as e:
        return str(e), time.time() - t0

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

# ============================================================
# 1. ANALOG COMPUTING: ODE solver for factoring
# Hypothesis: Encode N=p*q as x*y=N with ODE dx/dt = -grad(E), E=(xy-N)^2+(x+y-S)^2
# If we guess S ~ sqrt(N)*2, the ODE basin of attraction might find integer solutions.
# Continuous relaxation might bypass discrete search barriers.
# ============================================================
def exp1_analog_ode(N, p_true, q_true):
    # Simple gradient descent on E = (x*y - N)^2
    # Start near sqrt(N), use continuous relaxation
    x = math.isqrt(N) + 0.5
    y = N / x
    lr = 1e-6 / max(1, N)
    best_gcd = 1
    for step in range(10000):
        # Gradient of (xy - N)^2 w.r.t. x
        residual = x * y - N
        dx = 2 * residual * y
        dy = 2 * residual * x
        x -= lr * dx
        y -= lr * dy
        # Check nearby integers
        for xi in [int(x), int(x)+1]:
            if xi > 1 and N % xi == 0:
                return xi
        if abs(residual) < 0.5:
            xi = round(x)
            if xi > 1 and N % xi == 0:
                return xi
    return None

# ============================================================
# 2. DNA COMPUTING (simulated): Complementary binding
# Hypothesis: Represent trial divisors as binary "strands". Hybridization score =
# number of matching bits with N's remainder pattern. High scores = near-factors.
# ============================================================
def exp2_dna_binding(N, p_true, q_true):
    nbits = N.bit_length()
    target_bits = bin(N)[2:]
    best_score, best_d = 0, None
    # Generate random "DNA strands" (trial divisors)
    for _ in range(5000):
        d = random.randint(2, max(3, int(N**0.5)))
        r = N % d
        # "Binding score" = how close remainder is to 0
        score = nbits - r.bit_length() if r > 0 else nbits * 2
        if r == 0:
            return d
        if score > best_score:
            best_score, best_d = score, d
    return best_d if best_d and N % best_d == 0 else None

# ============================================================
# 3. OPTICAL INTERFEROMETRY (simulated): DFT-based factoring
# Hypothesis: Compute DFT of f(k) = exp(2*pi*i*k*N/d) for trial d.
# When d | N, constructive interference (peak). Detect via threshold.
# ============================================================
def exp3_optical_interference(N, p_true, q_true):
    import cmath
    limit = max(3, int(N**0.5) + 1)
    # Sample frequencies — look for constructive interference
    best_d, best_mag = 2, 0
    for d in range(2, min(limit, 5000)):
        # Interference pattern: sum of exp(2*pi*i*k*N/d) for k=0..d-1
        # This equals d if d|N, else 0 (geometric series)
        phase = 2 * math.pi * (N % d) / d
        # Shortcut: magnitude is |sin(d*phase/2)/sin(phase/2)| when phase != 0
        if N % d == 0:
            return d
        mag = abs(math.sin(d * phase / 2) / math.sin(phase / 2)) if abs(math.sin(phase / 2)) > 1e-15 else d
        if mag > best_mag:
            best_mag, best_d = mag, d
    return None

# ============================================================
# 4. THERMODYNAMIC COMPUTING: Free energy minimization
# Hypothesis: Define E(x) = (N mod x)^2 / N. At low "temperature", Boltzmann
# distribution concentrates on factors. Simulated annealing but with physical motivation.
# ============================================================
def exp4_thermodynamic(N, p_true, q_true):
    x = random.randint(2, max(3, int(N**0.5)))
    E = (N % x) ** 2
    T = N * 0.1  # High initial temperature
    best = x
    for step in range(10000):
        T *= 0.999  # Cool
        x_new = x + random.choice([-2, -1, 1, 2])
        if x_new < 2:
            continue
        E_new = (N % x_new) ** 2
        if E_new == 0:
            return x_new
        dE = E_new - E
        if dE < 0 or (T > 0 and random.random() < math.exp(-dE / max(T, 1e-30))):
            x, E = x_new, E_new
    return None

# ============================================================
# 5. SOCIAL NETWORK / COMMUNITY DETECTION on factor base graph
# Hypothesis: Build graph where nodes=primes, edges=co-occurrence in smooth residues.
# Community structure might reveal factor-aligned vs cofactor-aligned primes.
# ============================================================
def exp5_community_detection(N, p_true, q_true):
    # Build factor base
    primes = []
    for p in range(2, min(200, N)):
        if all(p % d != 0 for d in range(2, int(p**0.5)+1)) and p > 1:
            primes.append(p)
    # Build co-occurrence graph
    cooccur = defaultdict(int)
    for x in range(1, min(5000, N)):
        r = (x * x - N) if x * x > N else (N - x * x)
        factors_found = []
        temp = abs(r)
        for p in primes:
            if temp % p == 0:
                factors_found.append(p)
                while temp % p == 0:
                    temp //= p
        for i, a in enumerate(factors_found):
            for b in factors_found[i+1:]:
                cooccur[(a,b)] += 1
    # Check which primes divide p or q
    p_primes = [p for p in primes if p_true % p == 0 or (p_true - 1) % p == 0]
    q_primes = [p for p in primes if q_true % p == 0 or (q_true - 1) % p == 0]
    # Check if community structure separates them
    return {"p_associated": p_primes[:5], "q_associated": q_primes[:5],
            "edges": len(cooccur), "separation": len(set(p_primes) & set(q_primes)) == 0}

# ============================================================
# 6. EVOLUTIONARY / GENETIC ALGORITHM on factor bit strings
# Hypothesis: Crossover on bit representations of trial factors creates offspring
# that inherit "good bits" from parents with low N%x fitness.
# ============================================================
def exp6_genetic(N, p_true, q_true):
    nbits = (N.bit_length() + 1) // 2 + 1
    pop_size = 100
    pop = [random.randint(2, max(3, int(N**0.5))) for _ in range(pop_size)]
    for gen in range(200):
        # Fitness: lower remainder = better
        fitness = [(N % x if x > 1 else N, x) for x in pop]
        fitness.sort()
        if fitness[0][0] == 0 and fitness[0][1] > 1:
            return fitness[0][1]
        # Selection: top 50%
        parents = [x for _, x in fitness[:pop_size//2]]
        # Crossover + mutation
        children = []
        for _ in range(pop_size):
            p1, p2 = random.choice(parents), random.choice(parents)
            # Single-point crossover on bits
            cp = random.randint(1, nbits - 1)
            mask = (1 << cp) - 1
            child = (p1 & mask) | (p2 & ~mask)
            # Mutation
            if random.random() < 0.1:
                bit = random.randint(0, nbits - 1)
                child ^= (1 << bit)
            if child > 1:
                children.append(child)
        pop = children if children else pop
    return None

# ============================================================
# 7. SWARM INTELLIGENCE: Ant Colony Optimization
# Hypothesis: Ants deposit pheromone on bit positions. Bits that frequently appear
# in low-remainder candidates accumulate pheromone, guiding the swarm to factors.
# ============================================================
def exp7_ant_colony(N, p_true, q_true):
    nbits = (N.bit_length() + 1) // 2 + 1
    pheromone = [1.0] * nbits  # Pheromone per bit position
    n_ants = 50
    best_rem, best_x = N, 2
    for iteration in range(200):
        for _ in range(n_ants):
            # Construct solution using pheromone
            x = 0
            for b in range(nbits):
                prob = pheromone[b] / (pheromone[b] + 1.0)
                if random.random() < prob:
                    x |= (1 << b)
            if x < 2:
                continue
            rem = N % x
            if rem == 0:
                return x
            # Deposit pheromone inversely proportional to remainder
            quality = 1.0 / (1 + rem)
            for b in range(nbits):
                if x & (1 << b):
                    pheromone[b] += quality
            if rem < best_rem:
                best_rem, best_x = rem, x
        # Evaporate
        pheromone = [p * 0.95 for p in pheromone]
    return None

# ============================================================
# 8. RESERVOIR COMPUTING: Random RNN for smoothness classification
# Hypothesis: A random fixed-weight RNN can separate smooth from non-smooth numbers
# based on their binary representation, acting as a cheap smoothness pre-filter.
# ============================================================
def exp8_reservoir(N, p_true, q_true):
    import numpy as np
    np.random.seed(42)
    dim = 32
    W = np.random.randn(dim, dim) * 0.5  # Reservoir weights
    W_in = np.random.randn(dim, 8) * 0.3
    # Generate training data: is x smooth over small primes?
    def is_smooth(x, B=20):
        if x <= 0: return False
        for p in [2,3,5,7,11,13,17,19]:
            while x % p == 0: x //= p
        return x == 1
    def encode(x):
        return np.array([(x >> i) & 1 for i in range(8)], dtype=float)
    # Train readout
    states, labels = [], []
    for x in range(2, 500):
        h = np.tanh(W @ np.zeros(dim) + W_in @ encode(x % 256))
        for _ in range(3): h = np.tanh(W @ h + W_in @ encode(x % 256))
        states.append(h)
        labels.append(1.0 if is_smooth(abs(x*x - N) if x*x > N else abs(N - x*x)) else 0.0)
    X = np.array(states)
    y = np.array(labels)
    # Ridge regression readout
    readout = np.linalg.lstsq(X.T @ X + 0.01 * np.eye(dim), X.T @ y, rcond=None)[0]
    # Test: how well does it predict?
    preds = X @ readout
    correct = sum((p > 0.5) == (l > 0.5) for p, l in zip(preds, y))
    smooth_rate = sum(labels) / len(labels)
    return {"accuracy": correct / len(labels), "smooth_rate": smooth_rate,
            "baseline": max(smooth_rate, 1 - smooth_rate)}

# ============================================================
# 9. TOPOLOGICAL / ANYONIC BRAIDING (simulated): Period finding
# Hypothesis: Simulate braid group operations on Z/NZ. The braid order relates to
# ord(a, N), which reveals factors via gcd(a^(ord/2)-1, N).
# ============================================================
def exp9_braid_period(N, p_true, q_true):
    # Simulated "braid" = compute order of random element in Z/NZ
    for _ in range(20):
        a = random.randint(2, N - 1)
        g = gcd(a, N)
        if 1 < g < N:
            return g
        # Find order by repeated squaring (simulating braid twists)
        x = a
        for period in range(1, min(10000, N)):
            x = (x * a) % N
            if x == 1:
                # Got period, try gcd(a^(period/2) - 1, N)
                if period % 2 == 0:
                    half = pow(a, period // 2, N)
                    g = gcd(half - 1, N)
                    if 1 < g < N:
                        return g
                    g = gcd(half + 1, N)
                    if 1 < g < N:
                        return g
                break
    return None

# ============================================================
# 10. NEUROMORPHIC / SPIKING NEURAL NETWORK for modular arithmetic
# Hypothesis: Spiking neurons encode N mod d as spike timing. When spike timing
# aligns (zero phase), d divides N. Biological plausibility is irrelevant;
# the encoding might suggest new parallel search structures.
# ============================================================
def exp10_spiking(N, p_true, q_true):
    # Each "neuron" d fires at time t = N mod d
    # When fire time = 0, d | N
    # This is just trial division with a fancy hat, but test if
    # spike correlations between nearby neurons reveal structure
    limit = min(5000, int(N**0.5) + 1)
    spike_times = {}
    for d in range(2, limit):
        spike_times[d] = N % d
        if spike_times[d] == 0:
            return d
    # Check: do spike times cluster near 0 for near-factors?
    near_p = [d for d in spike_times if abs(d - p_true) < 5]
    near_q = [d for d in spike_times if abs(d - q_true) < 5]
    return {"near_p_spikes": [(d, spike_times[d]) for d in near_p],
            "near_q_spikes": [(d, spike_times[d]) for d in near_q]}

# ============================================================
# 11. CELLULAR AUTOMATA RULE 30 as pseudo-random walk
# Hypothesis: Rule 30 is a CSPRNG. Use it to generate the rho walk sequence
# instead of f(x) = x^2 + c. Different mixing might find cycles faster.
# ============================================================
def exp11_rule30_rho(N, p_true, q_true):
    # Rule 30 cellular automaton for walk generation
    width = 64
    state = N % (2**width)
    if state == 0: state = 1
    x, y = 2, 2  # tortoise and hare
    def rule30_step(s):
        new = 0
        for i in range(width):
            l = (s >> ((i+1) % width)) & 1
            c = (s >> i) & 1
            r = (s >> ((i-1) % width)) & 1
            # Rule 30: l XOR (c OR r)
            new |= (l ^ (c | r)) << i
        return new
    state_x = state
    state_y = state
    for step in range(10000):
        state_x = rule30_step(state_x)
        x = (x + (state_x % N)) % N
        state_y = rule30_step(rule30_step(state_y))
        y = (y + (state_y % N)) % N
        g = gcd(abs(x - y), N)
        if 1 < g < N:
            return g
    return None

# ============================================================
# 12. FIBONACCI LATTICE SIEVE
# Hypothesis: Sieve along Fibonacci-spaced points x = floor(k * phi * sqrt(N))
# mod N. Fibonacci spacing has optimal equidistribution (three-distance theorem),
# potentially hitting smooth residues more uniformly.
# ============================================================
def exp12_fibonacci_sieve(N, p_true, q_true):
    phi = (1 + math.sqrt(5)) / 2
    base = int(math.sqrt(N))
    smooth_count = 0
    factor_found = None
    for k in range(1, 5000):
        x = int(k * phi * base) % N
        if x < 2: continue
        g = gcd(x, N)
        if 1 < g < N:
            return g
        # Check smoothness of x^2 - N (or N - x^2)
        r = (x * x) % N
        # Quick gcd check
        for small_p in [2, 3, 5, 7, 11, 13]:
            g = gcd(r, N)
            if 1 < g < N:
                return g
    return None

# ============================================================
# 13. PRIME CONSTELLATION SIEVE
# Hypothesis: Dense prime clusters (twin primes, triplets) in the factor base
# create multiplicative coincidences that boost smoothness probability.
# Test: compare smoothness rate using constellation primes vs random primes.
# ============================================================
def exp13_constellation(N, p_true, q_true):
    # Find prime constellations (twin primes, etc.)
    def sieve_primes(limit):
        is_p = [True] * (limit + 1)
        is_p[0] = is_p[1] = False
        for i in range(2, int(limit**0.5) + 1):
            if is_p[i]:
                for j in range(i*i, limit+1, i): is_p[j] = False
        return [i for i in range(2, limit+1) if is_p[i]]
    primes = sieve_primes(500)
    twins = [p for p in primes if p + 2 in primes]
    # Test: smoothness over twins vs random subset
    def smooth_count(fb, trials):
        count = 0
        for x in trials:
            r = abs(x * x - N)
            if r == 0: continue
            for p in fb:
                while r % p == 0: r //= p
            if r == 1: count += 1
        return count
    trials = list(range(int(math.sqrt(N)) - 2000, int(math.sqrt(N)) + 2000))
    trials = [x for x in trials if x > 0][:2000]
    sc_twins = smooth_count(twins[:20], trials)
    sc_regular = smooth_count(primes[:20], trials)
    return {"twin_smooth": sc_twins, "regular_smooth": sc_regular,
            "twins_used": len(twins[:20]), "regular_used": 20}

# ============================================================
# 14. COLLATZ-LIKE ITERATION on Z/NZ
# Hypothesis: Define T(x) = x/2 if x even, (3x+1) mod N if x odd.
# Fixed points or short cycles might cluster near factors of N.
# ============================================================
def exp14_collatz_mod(N, p_true, q_true):
    for start in range(2, min(50, N)):
        x = start
        seen = {}
        for step in range(10000):
            if x in seen:
                # Found cycle — check gcd of cycle elements with N
                cycle_start = seen[x]
                cycle = []
                y = x
                for _ in range(step - cycle_start + 1):
                    cycle.append(y)
                    y = y // 2 if y % 2 == 0 else (3 * y + 1) % N
                    if y == x: break
                for c in cycle:
                    g = gcd(c, N)
                    if 1 < g < N:
                        return g
                break
            seen[x] = step
            x = x // 2 if x % 2 == 0 else (3 * x + 1) % N
            g = gcd(x, N)
            if 1 < g < N:
                return g
    return None

# ============================================================
# 15. FACTORING VIA DISCRETE LOGARITHM
# Hypothesis: If we can solve DLP in (Z/NZ)*, we can factor N.
# Specifically: find ord(2, N), then gcd(2^(ord/p_i) - 1, N) for prime divisors p_i of ord.
# ============================================================
def exp15_dlog_factor(N, p_true, q_true):
    a = 2
    # Baby-step giant-step for order finding (small N only)
    if N > 10**10:
        return "N too large for BSGS order finding"
    m = int(math.sqrt(N)) + 1
    # Compute order via factoring phi(N) approach
    # For small N, just iterate
    x = a
    for ord_candidate in range(1, min(N, 50000)):
        x = (x * a) % N
        if x == 1:
            order = ord_candidate + 1
            # Factor the order
            o = order
            prime_divs = []
            for p in range(2, int(math.sqrt(o)) + 1):
                if o % p == 0:
                    prime_divs.append(p)
                    while o % p == 0: o //= p
            if o > 1: prime_divs.append(o)
            # Try gcd(a^(order/p) - 1, N) for each prime divisor
            for p in prime_divs:
                exp = order // p
                val = pow(a, exp, N)
                g = gcd(val - 1, N)
                if 1 < g < N:
                    return g
            break
    return None

# ============================================================
# 16. ELLIPTIC CURVE ISOGENY WALK
# Hypothesis: Walk the isogeny graph of elliptic curves over Z/NZ.
# Short paths between curves reveal structure of N's factors.
# Simplified: compute j-invariants mod N, look for collisions mod p vs mod q.
# ============================================================
def exp16_isogeny_walk(N, p_true, q_true):
    # Simplified isogeny: j -> j' via modular polynomial
    # Use j -> (j - 1728)^3 / j^2 mod N as simplified "isogeny step"
    j = 1728  # Starting curve
    seen = {}
    for step in range(5000):
        if j in seen:
            # Cycle detected
            break
        seen[j] = step
        # Simplified isogeny step (not real isogeny, but tests the paradigm)
        if j == 0:
            j = 1
        try:
            j_new = pow(j, 3, N) * pow(j - 1728, 2, N) % N
        except:
            break
        g = gcd(j_new, N)
        if 1 < g < N:
            return g
        g = gcd(j_new - 1728, N)
        if 1 < g < N:
            return g
        j = j_new
    return None

# ============================================================
# 17. HYPERELLIPTIC CURVE JACOBIAN
# Hypothesis: Genus-2 curves y^2 = f(x) over Z/NZ have Jacobian of order ~N^2.
# Random walks in the Jacobian might find factors via group order mismatches.
# ============================================================
def exp17_hyperelliptic(N, p_true, q_true):
    # Simplified: use y^2 = x^5 + ax + b mod N
    # Random point, try to compute order via repeated addition
    a, b = 3, 7
    for trial in range(100):
        x0 = random.randint(0, N - 1)
        rhs = (pow(x0, 5, N) + a * x0 + b) % N
        # Check if rhs is a QR mod N (simplified: just try gcd tricks)
        g = gcd(rhs, N)
        if 1 < g < N:
            return g
        # Euler criterion trick
        half = pow(rhs, (N - 1) // 2, N) if N > 2 else 1
        g = gcd(half - 1, N)
        if 1 < g < N:
            return g
        g = gcd(half + 1, N)
        if 1 < g < N:
            return g
    return None

# ============================================================
# 18. ARITHMETIC CIRCUIT SATISFIABILITY: Reverse N = p * q
# Hypothesis: Encode multiplication as a circuit of AND/XOR gates.
# Use DPLL-like propagation to infer bit values. Unit propagation
# on the circuit constraints might rapidly prune the search space.
# ============================================================
def exp18_circuit_sat(N, p_true, q_true):
    nbits = (N.bit_length() + 1) // 2 + 1
    if nbits > 20:
        return "too many bits for brute SAT"
    # Brute force with bit-level pruning
    # Try all p up to sqrt(N), check if N % p == 0
    # But add "unit propagation": fix known bits of N
    n_bits = bin(N)[2:]
    limit = int(N**0.5) + 1
    # Observation: LSB of p and q must both be 1 (since N is odd, assuming N odd)
    start = 3 if N % 2 != 0 else 2
    step = 2 if N % 2 != 0 else 1
    for p in range(start, min(limit, 50000), step):
        if N % p == 0:
            return p
    return None

# ============================================================
# 19. TROPICAL FACTORING: (min, +) algebra
# Hypothesis: In tropical semiring, multiplication = addition, so
# trop(N) = trop(p) + trop(q). The p-adic valuations v_p(N) = v_p(p) + v_p(q)
# give a "tropical fingerprint". Can we invert this?
# ============================================================
def exp19_tropical(N, p_true, q_true):
    # Compute p-adic valuations of N for small primes
    # These directly reveal prime factors of N that are small
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    valuations = {}
    temp = N
    found_factors = []
    for p in small_primes:
        v = 0
        while temp % p == 0:
            v += 1
            temp //= p
            found_factors.append(p)
        valuations[p] = v
    # Tropical "decoding": the valuations ARE the factorization for small primes
    # For large primes, tropical approach gives no info (valuation = 0 for all small p)
    if temp == 1 and found_factors:
        return found_factors[0]
    # Try: use valuation pattern of N mod p for structure
    # v_p(x^2 - N) pattern might differ for x near p_true vs far
    srt = int(math.sqrt(N))
    patterns = {}
    for x in range(max(2, srt - 100), srt + 100):
        r = abs(x * x - N)
        if r == 0: continue
        pat = tuple(1 if r % p == 0 else 0 for p in small_primes[:5])
        g = gcd(r, N)
        if 1 < g < N:
            return g
    return None

# ============================================================
# 20. ERROR-CORRECTING CODE DECODING
# Hypothesis: Treat N's binary representation as a corrupted codeword.
# The "uncorrupted" words are p and q. Use syndrome decoding:
# S = N XOR (p * q in binary) should have structure we can exploit.
# More concretely: N in some error-correcting code; nearest valid codeword = factor.
# ============================================================
def exp20_ecc_decode(N, p_true, q_true):
    # Reed-Solomon inspired: evaluate N as polynomial over GF(p) for small p
    # Roots reveal factors
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
                    53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    # N mod p = 0 means p | N (trivial but it's the "decoding" step)
    for p in small_primes:
        if N % p == 0:
            return p
    # Deeper: compute "syndrome" = (N mod p, N mod p^2, ...) for small p
    # Look for patterns
    syndromes = {}
    for p in small_primes[:10]:
        syn = []
        for k in range(1, 5):
            syn.append(N % (p ** k))
        syndromes[p] = syn
    # Check: do syndromes cluster for primes related to factors?
    # Hensel lifting: if N mod p is special, lift to N mod p^k
    for p in small_primes:
        r = N % p
        # If r factors nicely mod p, that's a "syndrome match"
        for a in range(1, p):
            if (a * (N // a if N % a == 0 else (r * pow(a, -1, p) if gcd(a, p) == 1 else 0))) % p == r % p:
                g = gcd(a, N)
                if 1 < g < N:
                    return g
    return None


# ============================================================
# MAIN: Run all experiments
# ============================================================
def run_all():
    experiments = [
        ("1. Analog ODE", exp1_analog_ode),
        ("2. DNA Binding", exp2_dna_binding),
        ("3. Optical Interference", exp3_optical_interference),
        ("4. Thermodynamic Annealing", exp4_thermodynamic),
        ("5. Community Detection", exp5_community_detection),
        ("6. Genetic Algorithm", exp6_genetic),
        ("7. Ant Colony", exp7_ant_colony),
        ("8. Reservoir Computing", exp8_reservoir),
        ("9. Braid Period Finding", exp9_braid_period),
        ("10. Spiking Neural Net", exp10_spiking),
        ("11. Rule 30 Rho", exp11_rule30_rho),
        ("12. Fibonacci Sieve", exp12_fibonacci_sieve),
        ("13. Constellation Sieve", exp13_constellation),
        ("14. Collatz mod N", exp14_collatz_mod),
        ("15. DLog Factoring", exp15_dlog_factor),
        ("16. Isogeny Walk", exp16_isogeny_walk),
        ("17. Hyperelliptic Jacobian", exp17_hyperelliptic),
        ("18. Circuit SAT", exp18_circuit_sat),
        ("19. Tropical Factoring", exp19_tropical),
        ("20. ECC Decoding", exp20_ecc_decode),
    ]

    all_results = {}
    print("=" * 70)
    print("FACTORING RESEARCH v5: 20 MOONSHOT PARADIGMS")
    print("=" * 70)

    for name, func in experiments:
        print(f"\n--- {name} ---")
        exp_results = []
        for N, p, q in TEST_NS:
            result, elapsed = timed(func, N, p, q)
            factored = (result == p or result == q) if isinstance(result, int) else False
            exp_results.append({
                "N": N, "bits": N.bit_length(), "p": p, "q": q,
                "result": result, "factored": factored, "time": elapsed
            })
            status = "FACTORED" if factored else f"result={result}"
            print(f"  {N.bit_length():2d}b N={N}: {status} ({elapsed:.4f}s)")
        all_results[name] = exp_results

    return all_results


if __name__ == "__main__":
    all_results = run_all()

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for name, results in all_results.items():
        factored = sum(1 for r in results if r["factored"])
        max_bits = max((r["bits"] for r in results if r["factored"]), default=0)
        avg_time = sum(r["time"] for r in results) / len(results)
        print(f"  {name:35s}: {factored}/{len(results)} factored, max {max_bits}b, avg {avg_time:.4f}s")
