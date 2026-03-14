"""
H22: Tensor Network Decomposition for ECDLP
H27: Szegedy Quantum-Inspired Walk for ECDLP

Tests on toy curves (p=1009, 10007) and secp256k1 (28-36 bit keys).
"""

import time
import random
import hashlib
import numpy as np
import gmpy2
from gmpy2 import mpz, invert as gmp_invert
from collections import defaultdict


# ============================================================================
# Elliptic Curve Arithmetic (lightweight, self-contained)
# ============================================================================

class ECPoint:
    __slots__ = ('x', 'y', 'inf')
    def __init__(self, x, y, inf=False):
        self.x = x
        self.y = y
        self.inf = inf

    @staticmethod
    def infinity():
        return ECPoint(0, 0, inf=True)

    def __eq__(self, other):
        if self.inf and other.inf: return True
        if self.inf or other.inf: return False
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        if self.inf: return hash(("INF",))
        return hash((int(self.x), int(self.y)))

    def __repr__(self):
        if self.inf: return "O"
        return f"({self.x}, {self.y})"


class EC:
    """y^2 = x^3 + ax + b mod p. Integer arithmetic."""
    def __init__(self, a, b, p):
        self.a = a
        self.b = b
        self.p = p

    def on_curve(self, P):
        if P.inf: return True
        return (P.y*P.y - P.x*P.x*P.x - self.a*P.x - self.b) % self.p == 0

    def add(self, P, Q):
        if P.inf: return Q
        if Q.inf: return P
        if P.x == Q.x and P.y == Q.y:
            return self.double(P)
        if P.x == Q.x:
            return ECPoint.infinity()
        dx = (Q.x - P.x) % self.p
        inv_dx = pow(dx, self.p - 2, self.p)
        lam = ((Q.y - P.y) * inv_dx) % self.p
        x3 = (lam*lam - P.x - Q.x) % self.p
        y3 = (lam*(P.x - x3) - P.y) % self.p
        return ECPoint(x3, y3)

    def double(self, P):
        if P.inf or P.y == 0: return ECPoint.infinity()
        num = (3*P.x*P.x + self.a) % self.p
        den = (2*P.y) % self.p
        inv_den = pow(den, self.p - 2, self.p)
        lam = (num * inv_den) % self.p
        x3 = (lam*lam - 2*P.x) % self.p
        y3 = (lam*(P.x - x3) - P.y) % self.p
        return ECPoint(x3, y3)

    def neg(self, P):
        if P.inf: return P
        return ECPoint(P.x, (-P.y) % self.p)

    def mul(self, k, P):
        if k == 0: return ECPoint.infinity()
        if k < 0: P = self.neg(P); k = -k
        R = ECPoint.infinity()
        A = P
        while k:
            if k & 1: R = self.add(R, A)
            A = self.double(A)
            k >>= 1
        return R

    def enumerate_points(self):
        """Enumerate all points on the curve (toy curves only)."""
        pts = [ECPoint.infinity()]
        for x in range(self.p):
            rhs = (x*x*x + self.a*x + self.b) % self.p
            if rhs == 0:
                pts.append(ECPoint(x, 0))
                continue
            if pow(rhs, (self.p - 1) // 2, self.p) == 1:
                if self.p % 4 == 3:
                    y = pow(rhs, (self.p + 1) // 4, self.p)
                else:
                    y = _tonelli_shanks(rhs, self.p)
                    if y is None: continue
                pts.append(ECPoint(x, y))
                pts.append(ECPoint(x, (-y) % self.p))
        return pts

    def find_generator(self):
        """Find a generator point and order for toy curve."""
        for x in range(1, self.p):
            rhs = (x*x*x + self.a*x + self.b) % self.p
            if rhs == 0: continue
            if pow(rhs, (self.p - 1) // 2, self.p) != 1: continue
            if self.p % 4 == 3:
                y = pow(rhs, (self.p + 1) // 4, self.p)
            else:
                y = _tonelli_shanks(rhs, self.p)
                if y is None: continue
            P = ECPoint(x, y)
            # find order
            Q = P
            for i in range(1, self.p + self.p):
                if Q.inf:
                    return P, i
                Q = self.add(Q, P)
        return None, None


def _tonelli_shanks(n, p):
    """Square root mod p via Tonelli-Shanks."""
    if pow(n, (p-1)//2, p) != 1:
        return None
    Q, S = p - 1, 0
    while Q % 2 == 0:
        Q //= 2; S += 1
    if S == 1:
        return pow(n, (p+1)//4, p)
    z = 2
    while pow(z, (p-1)//2, p) != p - 1:
        z += 1
    M, c, t, R = S, pow(z, Q, p), pow(n, Q, p), pow(n, (Q+1)//2, p)
    while True:
        if t == 1: return R
        i = 1
        tmp = (t*t) % p
        while tmp != 1:
            tmp = (tmp*tmp) % p; i += 1
        b = pow(c, 1 << (M - i - 1), p)
        M, c, t, R = i, (b*b)%p, (t*b*b)%p, (R*b)%p


# ============================================================================
# FastCurve for secp256k1 (gmpy2 + Jacobian)
# ============================================================================

class FastCurve:
    """secp256k1 with gmpy2 Jacobian coords."""
    def __init__(self, a, b, p, G=None, n=None):
        self.a = mpz(a)
        self.b = mpz(b)
        self.p = mpz(p)
        self.G = G
        self.n = n

    def _to_jac(self, P):
        if P.inf: return (mpz(0), mpz(1), mpz(0))
        return (mpz(P.x), mpz(P.y), mpz(1))

    def _to_aff(self, J):
        X, Y, Z = J
        if Z == 0: return ECPoint.infinity()
        Zi = gmpy2.invert(Z, self.p)
        Zi2 = Zi * Zi % self.p
        Zi3 = Zi2 * Zi % self.p
        return ECPoint(int(X * Zi2 % self.p), int(Y * Zi3 % self.p))

    def _jac_double(self, J):
        X, Y, Z = J
        if Y == 0: return (mpz(0), mpz(1), mpz(0))
        p = self.p
        YY = Y*Y % p
        S = 4*X*YY % p
        M = 3*X*X % p  # a=0 for secp256k1
        X3 = (M*M - 2*S) % p
        Y3 = (M*(S - X3) - 8*YY*YY) % p
        Z3 = 2*Y*Z % p
        return (X3, Y3, Z3)

    def _jac_add(self, J1, J2):
        X1,Y1,Z1 = J1
        X2,Y2,Z2 = J2
        if Z1 == 0: return J2
        if Z2 == 0: return J1
        p = self.p
        Z1Z1 = Z1*Z1 % p
        Z2Z2 = Z2*Z2 % p
        U1 = X1*Z2Z2 % p
        U2 = X2*Z1Z1 % p
        S1 = Y1*Z2*Z2Z2 % p
        S2 = Y2*Z1*Z1Z1 % p
        if U1 == U2:
            if S1 == S2: return self._jac_double(J1)
            return (mpz(0), mpz(1), mpz(0))
        H = (U2 - U1) % p
        HH = H*H % p
        HHH = H*HH % p
        r = (S2 - S1) % p
        X3 = (r*r - HHH - 2*U1*HH) % p
        Y3 = (r*(U1*HH - X3) - S1*HHH) % p
        Z3 = Z1*Z2*H % p
        return (X3, Y3, Z3)

    def mul(self, k, P):
        if k == 0: return ECPoint.infinity()
        neg = False
        if k < 0: k = -k; neg = True
        J = self._to_jac(P)
        R = (mpz(0), mpz(1), mpz(0))
        while k:
            if k & 1: R = self._jac_add(R, J)
            J = self._jac_double(J)
            k >>= 1
        pt = self._to_aff(R)
        if neg: pt = ECPoint(pt.x, int((-mpz(pt.y)) % self.p))
        return pt

    def add(self, P, Q):
        return self._to_aff(self._jac_add(self._to_jac(P), self._to_jac(Q)))

    def neg(self, P):
        if P.inf: return P
        return ECPoint(P.x, int((-mpz(P.y)) % self.p))


# ============================================================================
# secp256k1 parameters
# ============================================================================

SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP256K1_GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
SECP256K1_GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

def make_secp256k1():
    G = ECPoint(SECP256K1_GX, SECP256K1_GY)
    return FastCurve(0, 7, SECP256K1_P, G=G, n=SECP256K1_N)


# ============================================================================
# H22: Tensor Network Decomposition
# ============================================================================

def h22_build_tensors(curve, G, order):
    """
    Build doubling tensor D and double-add tensor A as permutation mappings.
    D[i] = index of [2]P_i
    A[i] = index of [2]P_i + G
    """
    pts = [ECPoint.infinity()]
    Q = G
    for _ in range(1, order):
        pts.append(Q)
        Q = curve.add(Q, G)

    # Map point -> index
    pt_to_idx = {}
    for i, P in enumerate(pts):
        pt_to_idx[P] = i

    n = len(pts)
    D = np.zeros(n, dtype=np.int32)  # doubling permutation
    A = np.zeros(n, dtype=np.int32)  # double-and-add permutation

    for i, P in enumerate(pts):
        dbl = curve.double(P)
        dbl_add = curve.add(dbl, G)
        D[i] = pt_to_idx.get(dbl, 0)
        A[i] = pt_to_idx.get(dbl_add, 0)

    return pts, pt_to_idx, D, A


def h22_tensor_solve_brute(D, A, target_idx, nbits):
    """Brute force: try all 2^nbits bit strings, apply tensor train."""
    for k in range(1, 1 << nbits):
        # Apply tensor train: start at O (index 0), apply bits high to low
        state = 0  # index of O
        bits = []
        tmp = k
        for _ in range(nbits):
            bits.append(tmp & 1)
            tmp >>= 1
        bits.reverse()  # high to low

        for bit in bits:
            if bit == 0:
                state = D[state]
            else:
                state = A[state]

        if state == target_idx:
            return k
    return None


def h22_dmrg_sweep(D, A, target_idx, nbits, max_sweeps=50):
    """
    DMRG-style sweep: optimize one bit at a time, holding others fixed.
    Start with random bit string, sweep left-right optimizing each bit.
    """
    best_k = None

    for trial in range(10):  # multiple random starts
        bits = [random.randint(0, 1) for _ in range(nbits)]
        # Ensure not all zeros
        bits[-1] = 1

        for sweep in range(max_sweeps):
            changed = False
            for pos in range(nbits):
                best_bit = bits[pos]
                best_dist = float('inf')

                for b in [0, 1]:
                    bits[pos] = b
                    # Evaluate: apply tensor train
                    state = 0
                    for bit in bits:
                        state = D[state] if bit == 0 else A[state]
                    if state == target_idx:
                        # Found it!
                        k = 0
                        for bit in bits:
                            k = (k << 1) | bit
                        return k, sweep + 1, trial + 1
                    # Distance metric: difference in indices (cyclic)
                    n = len(D)
                    dist = min(abs(state - target_idx), n - abs(state - target_idx))
                    if dist < best_dist:
                        best_dist = dist
                        best_bit = b

                if bits[pos] != best_bit:
                    bits[pos] = best_bit
                    changed = True

            if not changed:
                break

    return None, max_sweeps, 10


def h22_belief_propagation(D, A, target_idx, nbits, order, max_iters=100):
    """
    Belief propagation on the tensor train factor graph.
    Variables: bits b_0,...,b_{B-1}
    Factors: f_i constrains state transition at step i

    We maintain messages: for each bit position, a distribution over {0,1}.
    Update by checking which bit value is more consistent with reaching target.
    """
    n = order
    # Forward-backward style BP
    # forward[i] = distribution over states after applying bits 0..i-1
    # backward[i] = distribution over states that lead to target from step i

    beliefs = np.ones((nbits, 2)) * 0.5  # uniform prior

    for iteration in range(max_iters):
        # Forward pass: compute state distributions
        forward = np.zeros((nbits + 1, n))
        forward[0][0] = 1.0  # start at O

        for i in range(nbits):
            for s in range(n):
                if forward[i][s] < 1e-10:
                    continue
                # bit=0: go to D[s]
                forward[i+1][D[s]] += forward[i][s] * beliefs[i][0]
                # bit=1: go to A[s]
                forward[i+1][A[s]] += forward[i][s] * beliefs[i][1]
            # Normalize
            total = forward[i+1].sum()
            if total > 0:
                forward[i+1] /= total

        # Backward pass
        backward = np.zeros((nbits + 1, n))
        backward[nbits][target_idx] = 1.0

        for i in range(nbits - 1, -1, -1):
            # For each state s at position i, what's the prob of reaching target?
            for s in range(n):
                # If bit=0: next state = D[s]
                backward[i][s] += backward[i+1][D[s]] * beliefs[i][0]
                # If bit=1: next state = A[s]
                backward[i][s] += backward[i+1][A[s]] * beliefs[i][1]
            total = backward[i].sum()
            if total > 0:
                backward[i] /= total

        # Update beliefs
        old_beliefs = beliefs.copy()
        for i in range(nbits):
            for b in [0, 1]:
                T = D if b == 0 else A
                score = 0.0
                for s in range(n):
                    if forward[i][s] < 1e-10:
                        continue
                    score += forward[i][s] * backward[i+1][T[s]]
                beliefs[i][b] = max(score, 1e-10)
            # Normalize
            total = beliefs[i].sum()
            beliefs[i] /= total

        # Check convergence
        if np.max(np.abs(beliefs - old_beliefs)) < 1e-6:
            break

    # Extract most likely bits
    bits = [int(beliefs[i][1] > beliefs[i][0]) for i in range(nbits)]
    k = 0
    for bit in bits:
        k = (k << 1) | bit

    # Verify
    state = 0
    for bit in bits:
        state = D[state] if bit == 0 else A[state]

    return k, state == target_idx, iteration + 1


def h22_permutation_cycle_analysis(D, A, order):
    """Analyze cycle structure of doubling and double-add permutations."""
    def find_cycles(perm):
        visited = set()
        cycles = []
        for start in range(len(perm)):
            if start in visited:
                continue
            cycle = []
            cur = start
            while cur not in visited:
                visited.add(cur)
                cycle.append(cur)
                cur = perm[cur]
            cycles.append(len(cycle))
        return sorted(cycles, reverse=True)

    d_cycles = find_cycles(D)
    a_cycles = find_cycles(A)
    return d_cycles, a_cycles


def test_h22_toy(p_val):
    """Test H22 on a toy curve y^2 = x^3 + 7 mod p."""
    print(f"\n{'='*60}")
    print(f"H22: Tensor Network Decomposition — toy curve p={p_val}")
    print(f"{'='*60}")

    curve = EC(0, 7, p_val)
    G, order = curve.find_generator()
    if G is None:
        print(f"  No generator found for p={p_val}")
        return {}
    print(f"  Generator: {G}, Order: {order}")

    # Build tensors
    t0 = time.time()
    pts, pt_to_idx, D, A = h22_build_tensors(curve, G, order)
    build_time = time.time() - t0
    print(f"  Tensor build time: {build_time:.3f}s")

    # Cycle analysis
    d_cycles, a_cycles = h22_permutation_cycle_analysis(D, A, order)
    print(f"  Doubling permutation cycles: {d_cycles[:10]}{'...' if len(d_cycles)>10 else ''}")
    print(f"  Double-add permutation cycles: {a_cycles[:10]}{'...' if len(a_cycles)>10 else ''}")

    nbits = max(1, order.bit_length())
    results = {}

    # Test multiple random targets
    num_tests = min(20, order - 1)
    test_keys = random.sample(range(1, order), num_tests)

    for method_name, method_fn in [
        ("brute_force", lambda ti, nb: (h22_tensor_solve_brute(D, A, ti, nb), True, 0)),
        ("dmrg_sweep", lambda ti, nb: h22_dmrg_sweep(D, A, ti, nb)),
        ("belief_prop", lambda ti, nb: h22_belief_propagation(D, A, ti, nb, order)),
    ]:
        successes = 0
        total_time = 0.0
        for k in test_keys:
            K = curve.mul(k, G)
            target_idx = pt_to_idx.get(K, -1)
            if target_idx < 0:
                continue

            t0 = time.time()
            result = method_fn(target_idx, nbits)
            elapsed = time.time() - t0
            total_time += elapsed

            if method_name == "brute_force":
                found_k, _, _ = result
                if found_k is not None and found_k % order == k % order:
                    successes += 1
            elif method_name == "dmrg_sweep":
                found_k, sweeps, trials = result
                if found_k is not None and found_k % order == k % order:
                    successes += 1
            else:
                found_k, correct, iters = result
                if correct and found_k % order == k % order:
                    successes += 1

        rate = successes / num_tests * 100
        avg_time = total_time / num_tests
        print(f"  {method_name}: {successes}/{num_tests} solved ({rate:.0f}%), avg {avg_time:.4f}s")
        results[method_name] = {"success_rate": rate, "avg_time": avg_time}

    return results


def test_h22_scaling():
    """Analyze scaling: are permutation tensors exploitable?"""
    print(f"\n{'='*60}")
    print(f"H22: Scaling Analysis — Permutation Structure")
    print(f"{'='*60}")

    for p_val in [101, 503, 1009, 2003, 5003]:
        curve = EC(0, 7, p_val)
        G, order = curve.find_generator()
        if G is None or order is None:
            print(f"  p={p_val}: no generator found")
            continue
        _, _, D, A = h22_build_tensors(curve, G, order)
        d_cycles, a_cycles = h22_permutation_cycle_analysis(D, A, order)
        print(f"  p={p_val}, order={order}, nbits={order.bit_length()}")
        print(f"    D cycles: {len(d_cycles)} cycles, max={d_cycles[0]}")
        print(f"    A cycles: {len(a_cycles)} cycles, max={a_cycles[0]}")
        # Key insight: if largest cycle is close to order, permutation is "almost cyclic"
        # and the tensor train is essentially a shift register — no shortcut.
        ratio = d_cycles[0] / order
        print(f"    D max_cycle/order = {ratio:.3f} ({'nearly cyclic' if ratio > 0.5 else 'structured'})")


# ============================================================================
# H27: Szegedy Quantum-Inspired Walk (Population Kangaroo)
# ============================================================================

def _walk_step_toy(curve, G, P, order):
    """One step of deterministic walk on toy curve."""
    # Partition based on x-coordinate
    if P.inf:
        return curve.add(P, G)  # step by G
    r = P.x % 16
    if r < 4:
        return curve.add(P, G)
    elif r < 8:
        return curve.add(P, curve.mul(2, G))
    elif r < 12:
        return curve.add(P, curve.mul(4, G))
    else:
        return curve.add(P, curve.mul(8, G))


def _walk_step_size_toy(P):
    """Return the step size corresponding to _walk_step_toy."""
    if P.inf:
        return 1
    r = P.x % 16
    if r < 4: return 1
    elif r < 8: return 2
    elif r < 12: return 4
    else: return 8


def h27_standard_kangaroo_toy(curve, G, order, K, max_steps=None):
    """Standard 2-walker kangaroo on toy curve. Returns (k, steps)."""
    if max_steps is None:
        max_steps = 4 * int(order ** 0.5) + 100

    # Tame kangaroo: starts at known point, walks forward
    tame_pos = order // 2
    tame_pt = curve.mul(tame_pos, G)

    # Wild kangaroo: starts at K
    wild_pos = 0  # relative to K: wild_pt = K + wild_pos * G
    wild_pt = K

    tame_trail = {}
    wild_trail = {}

    for step in range(max_steps):
        # Record distinguished points (x mod 32 == 0)
        if not tame_pt.inf and tame_pt.x % 32 == 0:
            tame_trail[tame_pt] = tame_pos
        if not wild_pt.inf and wild_pt.x % 32 == 0:
            wild_trail[wild_pt] = wild_pos

        # Check for collision
        if tame_pt in wild_trail:
            wild_d = wild_trail[tame_pt]
            k = (tame_pos - wild_d) % order
            if curve.mul(k, G) == K:
                return k, step
        if wild_pt in tame_trail:
            tame_d = tame_trail[wild_pt]
            k = (tame_d - wild_pos) % order
            if curve.mul(k, G) == K:
                return k, step

        # Walk
        ts = _walk_step_size_toy(tame_pt)
        tame_pos = (tame_pos + ts) % order
        tame_pt = curve.add(tame_pt, curve.mul(ts, G))

        ws = _walk_step_size_toy(wild_pt)
        wild_pos = (wild_pos + ws) % order
        wild_pt = curve.add(wild_pt, curve.mul(ws, G))

    return None, max_steps


def h27_population_kangaroo_toy(curve, G, order, K, pop_size=100, max_steps=None):
    """
    Population-based kangaroo (Szegedy-inspired).
    Maintain pop_size walkers, detect collisions via birthday paradox.
    """
    if max_steps is None:
        max_steps = max(4 * int(order ** 0.5) // pop_size + 10, 50)

    # Precompute step points
    step_sizes = [1, 2, 4, 8]
    step_pts = [curve.mul(s, G) for s in step_sizes]

    # Initialize: half tame, half wild
    n_tame = pop_size // 2
    n_wild = pop_size - n_tame

    tame_pts = []
    tame_pos = []
    for i in range(n_tame):
        pos = random.randint(0, order - 1)
        tame_pts.append(curve.mul(pos, G))
        tame_pos.append(pos)

    wild_pts = []
    wild_pos = []
    for i in range(n_wild):
        pos = random.randint(0, order - 1)
        wild_pts.append(curve.add(K, curve.mul(pos, G)))
        wild_pos.append(pos)

    dp_tame = {}  # point -> scalar position
    dp_wild = {}

    total_steps = 0
    for step in range(max_steps):
        # Record distinguished points and check collisions
        for i in range(n_tame):
            pt = tame_pts[i]
            if not pt.inf and pt.x % 8 == 0:
                dp_tame[pt] = tame_pos[i]
                if pt in dp_wild:
                    k = (tame_pos[i] - dp_wild[pt]) % order
                    if curve.mul(k, G) == K:
                        return k, total_steps

        for i in range(n_wild):
            pt = wild_pts[i]
            if not pt.inf and pt.x % 8 == 0:
                dp_wild[pt] = wild_pos[i]
                if pt in dp_tame:
                    k = (dp_tame[pt] - wild_pos[i]) % order
                    if curve.mul(k, G) == K:
                        return k, total_steps

        # Walk all walkers
        for i in range(n_tame):
            r = tame_pts[i].x % 4 if not tame_pts[i].inf else 0
            ss = step_sizes[r]
            tame_pos[i] = (tame_pos[i] + ss) % order
            tame_pts[i] = curve.add(tame_pts[i], step_pts[r])

        for i in range(n_wild):
            r = wild_pts[i].x % 4 if not wild_pts[i].inf else 0
            ss = step_sizes[r]
            wild_pos[i] = (wild_pos[i] + ss) % order
            wild_pts[i] = curve.add(wild_pts[i], step_pts[r])

        total_steps += pop_size

    return None, total_steps


def h27_walk_cycle_analysis(curve, G, order, num_samples=20):
    """Analyze cycle structure of the kangaroo walk on toy curve."""
    cycle_lengths = []
    tail_lengths = []

    for _ in range(num_samples):
        start_pos = random.randint(0, order - 1)
        start_pt = curve.mul(start_pos, G)

        # Floyd's cycle detection
        slow = start_pt
        slow_pos = start_pos
        fast = start_pt
        fast_pos = start_pos

        for step in range(order + 10):
            # slow: 1 step
            ss = _walk_step_size_toy(slow)
            slow_pos = (slow_pos + ss) % order
            slow = curve.add(slow, curve.mul(ss, G))

            # fast: 2 steps
            for _ in range(2):
                fs = _walk_step_size_toy(fast)
                fast_pos = (fast_pos + fs) % order
                fast = curve.add(fast, curve.mul(fs, G))

            if slow == fast:
                # Found cycle meeting point. Find cycle length.
                cycle_len = 1
                tmp = slow
                ts = _walk_step_size_toy(tmp)
                tmp = curve.add(tmp, curve.mul(ts, G))
                while tmp != slow:
                    ts = _walk_step_size_toy(tmp)
                    tmp = curve.add(tmp, curve.mul(ts, G))
                    cycle_len += 1

                # Find tail length
                s1 = start_pt
                s2 = slow
                tail = 0
                while s1 != s2:
                    ts1 = _walk_step_size_toy(s1)
                    s1 = curve.add(s1, curve.mul(ts1, G))
                    ts2 = _walk_step_size_toy(s2)
                    s2 = curve.add(s2, curve.mul(ts2, G))
                    tail += 1

                cycle_lengths.append(cycle_len)
                tail_lengths.append(tail)
                break

    return cycle_lengths, tail_lengths


def test_h27_toy(p_val):
    """Test H27 population kangaroo on toy curve."""
    print(f"\n{'='*60}")
    print(f"H27: Szegedy Population Kangaroo — toy curve p={p_val}")
    print(f"{'='*60}")

    curve = EC(0, 7, p_val)
    G, order = curve.find_generator()
    if G is None:
        print(f"  No generator found")
        return {}
    print(f"  Generator: {G}, Order: {order}")

    # Walk cycle analysis
    cycle_lens, tail_lens = h27_walk_cycle_analysis(curve, G, order, num_samples=10)
    if cycle_lens:
        avg_cycle = sum(cycle_lens) / len(cycle_lens)
        avg_tail = sum(tail_lens) / len(tail_lens)
        print(f"  Walk cycle analysis: avg_cycle={avg_cycle:.0f}, avg_tail={avg_tail:.0f}")
        print(f"    cycle/order = {avg_cycle/order:.3f}")

    num_tests = min(20, order - 1)
    test_keys = random.sample(range(1, order), num_tests)
    results = {}

    # Standard 2-walker
    successes_std = 0
    total_steps_std = 0
    t0 = time.time()
    for k in test_keys:
        K = curve.mul(k, G)
        found, steps = h27_standard_kangaroo_toy(curve, G, order, K)
        if found is not None:
            successes_std += 1
        total_steps_std += steps
    std_time = time.time() - t0
    print(f"  Standard 2-walker: {successes_std}/{num_tests} solved, "
          f"avg_steps={total_steps_std/num_tests:.0f}, time={std_time:.3f}s")
    results["standard"] = {"solved": successes_std, "avg_steps": total_steps_std / num_tests}

    # Population kangaroo with various sizes
    for pop_size in [10, 50, 100, 500]:
        if pop_size > order // 2:
            continue
        successes = 0
        total_steps = 0
        t0 = time.time()
        for k in test_keys:
            K = curve.mul(k, G)
            found, steps = h27_population_kangaroo_toy(curve, G, order, K, pop_size=pop_size)
            if found is not None:
                successes += 1
            total_steps += steps
        elapsed = time.time() - t0
        print(f"  Population W={pop_size}: {successes}/{num_tests} solved, "
              f"avg_steps={total_steps/num_tests:.0f}, time={elapsed:.3f}s")
        results[f"pop_{pop_size}"] = {"solved": successes, "avg_steps": total_steps / num_tests}

    return results


# ============================================================================
# secp256k1 tests (28-36 bit keys)
# ============================================================================

def _secp_walk_step(curve, P, step_pts, step_sizes):
    """Walk step for secp256k1 using x mod 32."""
    if P.inf:
        r = 0
    else:
        r = P.x % len(step_sizes)
    return curve.add(P, step_pts[r]), step_sizes[r]


def h27_standard_kangaroo_secp(curve, G, K, key_bits, max_steps=None):
    """
    Standard 2-walker Pollard kangaroo on secp256k1 for key_bits-bit key.
    Tame walks from midpoint of [0, 2^key_bits), wild walks from K.
    Both use same deterministic walk based on point x-coordinate.
    When they land on the same point, tame_pos = k + wild_pos, so k = tame_pos - wild_pos.
    """
    n = curve.n
    search_range = 1 << key_bits
    sqrt_range = int(search_range ** 0.5)

    if max_steps is None:
        max_steps = 8 * sqrt_range

    # Step table: powers of 2, mean step ~ sqrt(range) / num_steps
    num_steps = 16
    step_sizes = []
    for i in range(num_steps):
        step_sizes.append(1 << (i * key_bits // (2 * num_steps)))
    step_pts = [curve.mul(s, G) for s in step_sizes]

    # Tame: starts at midpoint, walks with known scalar
    tame_scalar = search_range // 2
    tame_pt = curve.mul(tame_scalar, G)

    # Wild: starts at K, walks with unknown scalar k + wild_offset
    wild_offset = 0
    wild_pt = K  # = k*G

    # Use direct collision detection (no DP for simplicity)
    tame_seen = {}  # x -> scalar
    wild_seen = {}  # x -> offset

    for step in range(max_steps):
        # Record
        tx = tame_pt.x
        tame_seen[tx] = tame_scalar
        if tx in wild_seen:
            # tame_scalar*G == (k + wild_seen[tx])*G => k = tame_scalar - wild_seen[tx]
            k_cand = (tame_scalar - wild_seen[tx]) % n
            if 0 < k_cand < search_range:
                return k_cand, step

        wx = wild_pt.x
        wild_seen[wx] = wild_offset
        if wx in tame_seen:
            k_cand = (tame_seen[wx] - wild_offset) % n
            if 0 < k_cand < search_range:
                return k_cand, step

        # Walk (deterministic based on x)
        r = tx % num_steps
        tame_scalar += step_sizes[r]
        tame_pt = curve.add(tame_pt, step_pts[r])

        r = wx % num_steps
        wild_offset += step_sizes[r]
        wild_pt = curve.add(wild_pt, step_pts[r])

    return None, max_steps


def h27_population_kangaroo_secp(curve, G, K, key_bits, pop_size=100, max_steps=None):
    """
    Population kangaroo on secp256k1.
    Uses x-coordinate collision detection across all walkers.
    """
    n = curve.n
    search_range = 1 << key_bits
    sqrt_range = int(search_range ** 0.5)

    if max_steps is None:
        max_steps = max(8 * sqrt_range // pop_size + 10, 500)

    num_steps = 16
    step_sizes = []
    for i in range(num_steps):
        step_sizes.append(1 << (i * key_bits // (2 * num_steps)))
    step_pts = [curve.mul(s, G) for s in step_sizes]

    n_tame = pop_size // 2
    n_wild = pop_size - n_tame

    tame_pts = []
    tame_scalars = []
    for i in range(n_tame):
        s = random.randint(0, search_range - 1)
        tame_pts.append(curve.mul(s, G))
        tame_scalars.append(s)

    wild_pts = []
    wild_offsets = []
    for i in range(n_wild):
        s = random.randint(0, search_range - 1)
        wild_pts.append(curve.add(K, curve.mul(s, G)))
        wild_offsets.append(s)

    # x -> scalar (for tame) or offset (for wild)
    tame_seen = {}
    wild_seen = {}

    for step in range(max_steps):
        # Record and check collisions
        for i in range(n_tame):
            tx = tame_pts[i].x
            tame_seen[tx] = tame_scalars[i]
            if tx in wild_seen:
                k_cand = (tame_scalars[i] - wild_seen[tx]) % n
                if 0 < k_cand < search_range:
                    return k_cand, step * pop_size

        for i in range(n_wild):
            wx = wild_pts[i].x
            wild_seen[wx] = wild_offsets[i]
            if wx in tame_seen:
                k_cand = (tame_seen[wx] - wild_offsets[i]) % n
                if 0 < k_cand < search_range:
                    return k_cand, step * pop_size

        # Walk all
        for i in range(n_tame):
            r = tame_pts[i].x % num_steps if not tame_pts[i].inf else 0
            tame_scalars[i] += step_sizes[r]
            tame_pts[i] = curve.add(tame_pts[i], step_pts[r])

        for i in range(n_wild):
            r = wild_pts[i].x % num_steps if not wild_pts[i].inf else 0
            wild_offsets[i] += step_sizes[r]
            wild_pts[i] = curve.add(wild_pts[i], step_pts[r])

    return None, max_steps * pop_size


def test_h27_secp256k1():
    """Test H27 on secp256k1 with 28-36 bit keys."""
    print(f"\n{'='*60}")
    print(f"H27: Population Kangaroo on secp256k1")
    print(f"{'='*60}")

    curve = make_secp256k1()
    G = curve.G

    results = {}
    for bits in [28, 30, 32, 34, 36]:
        print(f"\n  --- {bits}-bit keys ---")
        num_tests = 5 if bits <= 32 else 3

        for method_name, method_fn in [
            ("2-walker", lambda K, b: h27_standard_kangaroo_secp(curve, G, K, b)),
            ("pop-50", lambda K, b: h27_population_kangaroo_secp(curve, G, K, b, pop_size=50)),
            ("pop-200", lambda K, b: h27_population_kangaroo_secp(curve, G, K, b, pop_size=200)),
        ]:
            successes = 0
            total_time = 0
            total_steps = 0
            for _ in range(num_tests):
                k = random.randint(1, (1 << bits) - 1)
                K = curve.mul(k, G)
                t0 = time.time()
                found, steps = method_fn(K, bits)
                elapsed = time.time() - t0
                total_time += elapsed
                total_steps += steps
                if found is not None and found == k:
                    successes += 1

            avg_time = total_time / num_tests
            avg_steps = total_steps / num_tests
            print(f"    {method_name}: {successes}/{num_tests} solved, "
                  f"avg_steps={avg_steps:.0f}, avg_time={avg_time:.2f}s")
            results[f"{bits}b_{method_name}"] = {
                "solved": successes, "total": num_tests,
                "avg_time": avg_time, "avg_steps": avg_steps
            }

    return results


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    random.seed(42)
    print("=" * 60)
    print("ECDLP Hypothesis Testing: H22 (Tensor) + H27 (Szegedy Walk)")
    print("=" * 60)

    all_results = {}

    # H22 toy tests
    for p_val in [1009, 10007]:
        r = test_h22_toy(p_val)
        all_results[f"h22_p{p_val}"] = r

    # H22 scaling
    test_h22_scaling()

    # H27 toy tests
    for p_val in [1009, 10007]:
        r = test_h27_toy(p_val)
        all_results[f"h27_p{p_val}"] = r

    # H27 secp256k1
    r = test_h27_secp256k1()
    all_results["h27_secp256k1"] = r

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    print("\nH22 (Tensor Network Decomposition):")
    print("  - Tensors D and A are PERMUTATION MATRICES (sparse, one-to-one)")
    print("  - Finding k is equivalent to finding a path in a permutation composition graph")
    print("  - DMRG sweep: local optimization, gets stuck in local minima")
    print("  - Belief propagation: message passing on tensor train factor graph")
    print("  - Scaling: for secp256k1, tensor dimension = curve order (~2^256)")
    print("    Dense representation impossible. Sparse (permutation) representation")
    print("    reduces to the same problem as brute-force search.")
    print("  VERDICT: Tensor decomposition does NOT provide speedup over brute force")
    print("           for generic EC groups. The permutations lack exploitable structure.")

    print("\nH27 (Szegedy Population Kangaroo):")
    print("  - Population kangaroo uses birthday paradox: W walkers, T steps each")
    print("  - Collision probability ~ (W*T)^2 / n, so W*T ~ sqrt(n)")
    print("  - With W=200, need T = sqrt(n)/200 steps per walker")
    print("  - Total work = W*T = sqrt(n), same as 2-walker!")
    print("  - Advantage: more parallelism, but same total EC operations")
    print("  VERDICT: Population kangaroo is a parallelism strategy, not a speedup.")
    print("           Total work remains O(sqrt(n)). Useful for GPU/distributed settings.")

    print("\nDone.")
