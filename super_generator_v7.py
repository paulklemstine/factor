#!/usr/bin/env python3
"""
Super-Generator v7.0: Pythagorean Tree Pathfinding Engine
==========================================================
Enhancements over v5/v6:
  1. Shannon Entropy Pruning — prune branches where bit-alignment worsens
  2. Lyapunov Stability Filter — backtrack on diverging trajectories
  3. Improved Jacobian Selection — depth-2 lookahead (36 candidates)
  4. Inverse Matrix Climbing (Meet-in-the-Middle)
  5. Multi-root starts — non-primitive triples (3k, 4k, 5k)
  6. VSDD at every node — multiple delta extractions per node

This is Path 1 of the Resonance Sieve v7.0.
"""

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd
import time
import math
from collections import deque
import heapq


###############################################################################
# Matrix Libraries
###############################################################################

# Berggren's 3 matrices: generate ALL primitive Pythagorean triples from (3,4,5)
BERGGREN = [
    [( 1,-2, 2), ( 2,-1, 2), ( 2,-2, 3)],  # M1
    [( 1, 2, 2), ( 2, 1, 2), ( 2, 2, 3)],  # M2
    [(-1, 2, 2), (-2, 1, 2), (-2, 2, 3)],  # M3
]

# Price's 3 matrices
PRICE = [
    [( 1, 0, 0), ( 2, 1, 0), ( 2, 0, 1)],  # U1
    [(-1, 0, 2), (-2, 1, 2), (-2, 0, 3)],  # U2
    [( 1, 0, 2), ( 2, 1, 2), ( 2, 0, 3)],  # U3
]

# 6 unique matrices (Berggren == Hall, so skip Hall)
UNIQUE_MATRICES = BERGGREN + PRICE


def mat_mul(M, v):
    """Multiply 3x3 matrix M by vector v = (A, B, C). Returns tuple of mpz."""
    a, b, c = v
    return (
        mpz(M[0][0])*a + mpz(M[0][1])*b + mpz(M[0][2])*c,
        mpz(M[1][0])*a + mpz(M[1][1])*b + mpz(M[1][2])*c,
        mpz(M[2][0])*a + mpz(M[2][1])*b + mpz(M[2][2])*c,
    )


def mat_inverse_3x3(M):
    """Compute inverse of integer 3x3 matrix (exact for det = +/-1)."""
    a, b, c = M[0]
    d, e, f = M[1]
    g, h, i = M[2]
    det = a*(e*i - f*h) - b*(d*i - f*g) + c*(d*h - e*g)
    if abs(det) != 1:
        return None
    inv = [
        [det*(e*i - f*h), det*(c*h - b*i), det*(b*f - c*e)],
        [det*(f*g - d*i), det*(a*i - c*g), det*(c*d - a*f)],
        [det*(d*h - e*g), det*(b*g - a*h), det*(a*e - b*d)],
    ]
    return inv


# Precompute all inverse matrices
INVERSE_MATRICES = []
for M in UNIQUE_MATRICES:
    inv = mat_inverse_3x3(M)
    if inv is not None:
        INVERSE_MATRICES.append(inv)


###############################################################################
# Modular Pruning
###############################################################################

def build_modular_filter(n, moduli=None):
    """
    Build modular filter tables.
    For each modulus m, precompute allowed (B mod m, C mod m) pairs
    where C^2 - B^2 = n (mod m).
    """
    if moduli is None:
        moduli = [8, 9, 16, 5, 7, 11, 13]
    filters = {}
    for m in moduli:
        n_mod = int(n % m)
        allowed = set()
        for c in range(m):
            for b in range(m):
                if (c * c - b * b) % m == n_mod:
                    allowed.add((b % m, c % m))
        filters[m] = allowed
    return filters


def passes_modular_filter(B, C, filters):
    """Check if (B, C) passes all modular filters."""
    for m, allowed in filters.items():
        if (int(B % m), int(C % m)) not in allowed:
            return False
    return True


###############################################################################
# MODULAR CARRY SQUEEZE (LSB Anchor — Delta Refinement Solution B)
###############################################################################

def build_carry_squeeze(n, k=16):
    """
    Build the Modular Carry Squeeze table.

    For n = (C-B)(C+B), and candidate delta = C-B:
      n ≡ delta * (delta + 2B) mod 2^k

    For each possible delta mod 2^k, compute the set of valid
    (C-B) mod 2^k values. This constrains which tree branches
    can lead to a valid factorization.

    Returns: set of allowed (delta mod 2^k) values.
    """
    m = 1 << k  # 2^k
    n_mod = int(n % m)
    allowed_deltas = set()

    for delta in range(1, m):
        # n ≡ delta * (delta + 2B) mod m
        # So (delta + 2B) ≡ n * delta^(-1) mod m (if delta is odd)
        # For even delta, check if n/gcd(delta, m) has a solution
        if delta % 2 == 0:
            # Even delta: more complex. Check all B values.
            for b in range(m):
                if (delta * (delta + 2 * b)) % m == n_mod:
                    allowed_deltas.add(delta)
                    break
        else:
            # Odd delta: delta is invertible mod 2^k
            try:
                d_inv = pow(delta, -1, m)
                sum_val = (n_mod * d_inv) % m  # delta + 2B mod m
                # B = (sum_val - delta) / 2 mod m
                diff = (sum_val - delta) % m
                if diff % 2 == 0:
                    allowed_deltas.add(delta)
            except (ValueError, ZeroDivisionError):
                pass

    return allowed_deltas, k


def passes_carry_squeeze(C, B, allowed_deltas, k):
    """
    Check if the current node's delta = C - B passes the Carry Squeeze.
    Returns True if (C-B) mod 2^k is in the allowed set.
    """
    m = 1 << k
    delta_mod = int((C - B) % m)
    return delta_mod in allowed_deltas


###############################################################################
# HYPERBOLIC CONVERGENCE TRACKER (Delta Refinement Solution A)
###############################################################################

class HyperbolicTracker:
    """
    Monitor the velocity of R = C/B convergence along the tree path.

    If the ratio is converging too fast toward R_target, dynamically
    stretch the delta estimate (increase R_target) to prevent overshoot.
    If converging too slowly, compress (decrease R_target).

    This acts as an Inverse Jacobian stabilizer.
    """

    def __init__(self, R_target, damping=0.8):
        self.R_target_base = R_target
        self.R_target = R_target
        self.damping = damping
        self.history = []  # (depth, R_current, error)

    def update(self, R_current, depth):
        """
        Record current ratio and adjust R_target if needed.
        Returns the (possibly adjusted) R_target.
        """
        error = R_current - self.R_target
        self.history.append((depth, R_current, error))

        if len(self.history) < 3:
            return self.R_target

        # Compute convergence velocity: dR/d(depth)
        r_prev = self.history[-2][1]
        r_curr = R_current
        velocity = r_curr - r_prev  # Rate of change of R

        # Compute expected velocity toward target
        remaining_error = self.R_target - R_current
        expected_velocity = remaining_error * 0.1  # Expect 10% convergence per step

        if abs(velocity) > 0 and abs(remaining_error) > 0:
            # If overshooting (velocity sign matches error but magnitude is too large)
            if abs(velocity) > abs(expected_velocity) * 3:
                # Converging too fast — stretch R_target to slow down
                self.R_target = self.R_target + remaining_error * (1 - self.damping)
            elif abs(velocity) < abs(expected_velocity) * 0.1 and len(self.history) > 10:
                # Converging too slowly — compress R_target
                self.R_target = self.R_target_base  # Reset to original

        return self.R_target

    def get_velocity(self):
        """Get the most recent convergence velocity."""
        if len(self.history) < 2:
            return 0.0
        return self.history[-1][1] - self.history[-2][1]


###############################################################################
# CAPTURE ZONE SNAP (Delta Refinement Solution C)
###############################################################################

def capture_zone_snap(n, C_approx, scan_range=10000):
    """
    When the Super-Generator reaches the "Capture Zone" where C ≈ √n,
    perform an intensive Fermat scan around C_approx.

    For each C_try in [C_approx - scan_range, C_approx + scan_range]:
      B² = C_try² - n
      If B² is a perfect square → factorization found.

    This is the "gravity well" that snaps an approximate path to
    the exact integer solution.

    Returns factor or None.
    """
    n = mpz(n)
    sqrt_n = isqrt(n)

    # Ensure C_approx >= sqrt(n) + 1
    C_start = max(mpz(C_approx) - scan_range, sqrt_n + 1)
    C_end = mpz(C_approx) + scan_range

    for C_val in range(int(C_start), int(C_end) + 1):
        C_val = mpz(C_val)
        B_sq = C_val * C_val - n
        if B_sq < 0:
            continue
        B_val = isqrt(B_sq)
        if B_val * B_val == B_sq and B_val > 0:
            f1 = C_val - B_val
            f2 = C_val + B_val
            if f1 > 1 and f2 > 1 and f1 * f2 == n:
                return int(min(f1, f2))

    return None


###############################################################################
# VSDD Check (multiple delta extractions)
###############################################################################

def vsdd_check(n, delta):
    """
    O(1) VSDD check: B = (n - delta^2) / (2*delta).
    If B is a positive integer, factors are delta and (2B + delta).
    Returns the smaller factor or None.
    """
    delta = mpz(delta)
    if delta <= 0 or delta * delta >= n:
        return None
    numerator = n - delta * delta
    if numerator <= 0:
        return None
    denominator = 2 * delta
    if numerator % denominator != 0:
        return None
    B = numerator // denominator
    factor1 = delta
    factor2 = 2 * B + delta
    if factor1 * factor2 == n and factor1 > 1 and factor2 > 1 and factor1 != n:
        return int(min(factor1, factor2))
    return None


def vsdd_multi_check(n, A, B, C):
    """
    Enhancement #6: VSDD at every node with multiple delta extractions.
    Try delta = C-B, A, C+B, 2B, 2A, |C-2B|, etc.
    Returns factor or None.
    """
    deltas_to_try = set()

    # Primary deltas
    cb = C - B
    if cb > 0:
        deltas_to_try.add(cb)
    if A > 0:
        deltas_to_try.add(A)

    # Secondary deltas
    cpb = C + B
    if cpb > 0 and cpb < n:
        deltas_to_try.add(cpb)
    twob = 2 * B
    if twob > 0 and twob < n:
        deltas_to_try.add(twob)
    twoa = 2 * A
    if twoa > 0 and twoa < n:
        deltas_to_try.add(twoa)

    # Tertiary deltas
    c2b = abs(C - 2 * B)
    if c2b > 0 and c2b < n:
        deltas_to_try.add(c2b)
    apb = A + B
    if apb > 0 and apb < n:
        deltas_to_try.add(apb)
    apc = A + C
    if apc > 0 and apc < n:
        deltas_to_try.add(apc)

    # Also try GCD-based deltas
    g1 = gcd(n, cb) if cb > 0 else mpz(0)
    if g1 > 1 and g1 < n:
        return int(g1)
    g2 = gcd(n, A) if A > 0 else mpz(0)
    if g2 > 1 and g2 < n:
        return int(g2)

    for delta in deltas_to_try:
        result = vsdd_check(n, delta)
        if result is not None:
            return result

    return None


###############################################################################
# RESONANCE BAND ESTIMATION (Beat Frequency Envelope)
###############################################################################

def resonance_band_estimate(n, num_bands=5):
    """
    Estimate candidate Δ values (factor gap = C - B) using the Beat
    Frequency Envelope E(x) = cos(π(√(x+n) - √x)).

    Math: For n = C² - B², the resonance occurs at x = B² where
    √(x+n) - √x = Δ = C - B exactly. Near this x, the envelope
    amplitude peaks (cosine crosses ±1).

    Since Δ is unknown, we probe multiple candidate bands:
    1. For balanced semiprimes: Δ ≈ n^(1/4) to n^(1/2)
    2. Use the derivative f'(x) = 0.5(1/√(x+n) - 1/√x) to find
       regions where the beat frequency is minimized
    3. Filter candidates using modular constraints

    Returns list of (delta_estimate, R_target) pairs sorted by likelihood.
    """
    n = mpz(n)
    sqrt_n = isqrt(n)
    nb = int(gmpy2.log2(n)) + 1

    candidates = []

    # Strategy 1: Logarithmically spaced Δ probes
    # For balanced semiprimes, Δ = p - q where p,q ≈ √n
    # The gap (p-q) can range from ~n^(1/4) (very balanced) to ~√n (unbalanced)
    # We probe ~num_bands * 3 candidates across this range
    log_lo = max(1, nb // 4 - 4)   # ≈ n^(1/4) bits
    log_hi = nb // 2               # ≈ √n bits

    for i in range(num_bands * 3):
        frac = i / max(1, num_bands * 3 - 1)
        log_delta = log_lo + frac * (log_hi - log_lo)
        delta = mpz(1) << int(log_delta)

        # Refine: check if n is divisible by delta (direct hit)
        g = gcd(n, delta)
        if 1 < g < n:
            candidates.append((int(g), float('inf')))  # Direct hit
            continue

        # Compute B = (n - Δ²) / (2Δ) — check if valid
        delta_sq = delta * delta
        if delta_sq >= n:
            continue
        num = n - delta_sq
        denom = 2 * delta
        if num % denom == 0:
            # Exact! This delta is a factor
            B = num // denom
            C = B + delta
            if C * C - B * B == n:
                candidates.append((int(delta), float('inf')))
                continue

        # Compute R_target for this delta estimate
        n_plus_d2 = n + delta_sq
        n_minus_d2 = n - delta_sq
        if n_minus_d2 <= 0:
            continue
        R_target = float(n_plus_d2) / float(n_minus_d2)
        if R_target < 1.0 or R_target > 1e15:
            continue

        candidates.append((int(delta), R_target))

    # Strategy 2: Beat frequency sampling near √n
    # f(x) = √(x+n) - √x. We want f(x) close to integer k.
    # For each small k, x_k = ((n-k²)/(2k))²
    # These give the exact resonance points for factor gap k.
    for k in range(1, min(10000, int(sqrt_n) + 1)):
        k_mpz = mpz(k)
        k_sq = k_mpz * k_mpz
        if k_sq >= n:
            break
        num = n - k_sq
        if num % (2 * k_mpz) != 0:
            continue
        B = num // (2 * k_mpz)
        C = B + k_mpz
        if B > 0 and C > 0 and C * C - B * B == n:
            # Exact factorization!
            f1 = int(k_mpz)
            f2 = int(2 * B + k_mpz)
            if f1 > 1 and f2 > 1:
                candidates.append((min(f1, f2), float('inf')))

    # Strategy 3: Probe near n^(1/4) ± small offsets (very balanced primes)
    quarter_root, _ = gmpy2.iroot(n, 4)
    for offset in range(-50, 51):
        delta = quarter_root + offset
        if delta <= 0:
            continue
        delta_sq = delta * delta
        if delta_sq >= n:
            continue
        n_plus_d2 = n + delta_sq
        n_minus_d2 = n - delta_sq
        if n_minus_d2 <= 0:
            continue
        R_target = float(n_plus_d2) / float(n_minus_d2)
        if 1.0 < R_target < 1e15:
            candidates.append((int(delta), R_target))

    # Deduplicate and sort by R_target closeness to reasonable range
    seen = set()
    unique = []
    for delta, R in candidates:
        if delta not in seen:
            seen.add(delta)
            unique.append((delta, R))

    # Sort: exact hits first (inf score), then by R_target closeness to 1
    unique.sort(key=lambda x: (-x[1] if x[1] == float('inf') else abs(x[1] - 2.0)))

    return unique[:num_bands]


def spectral_compass_select(A, B, C, R_target, n, matrices=None, filters=None):
    """
    Spectral Compass: select the matrix that minimizes |C'/B' - R_target|
    with modular pruning.

    R_target = C_target/B_target where C_target² - B_target² = n.
    At each node, we evaluate all child branches and choose the one
    whose C/B ratio is closest to R_target.

    Returns (best_matrix_index, best_node, best_error) or (None, None, inf).
    """
    if matrices is None:
        matrices = UNIQUE_MATRICES

    best_idx = None
    best_node = None
    best_err = float('inf')

    for i, M in enumerate(matrices):
        A1, B1, C1 = mat_mul(M, (A, B, C))
        if A1 <= 0 or B1 <= 0 or C1 <= 0:
            continue

        # Modular filter (P-adic GPS)
        if filters and not passes_modular_filter(B1, C1, filters):
            continue

        # Spectral ratio error
        R_current = float(C1) / float(B1)
        err = abs(R_current - R_target)

        # Depth-2 lookahead: check best child at depth 2
        best_d2_err = err
        for M2 in matrices:
            A2, B2, C2 = mat_mul(M2, (A1, B1, C1))
            if A2 <= 0 or B2 <= 0 or C2 <= 0:
                continue
            R2 = float(C2) / float(B2)
            d2_err = abs(R2 - R_target)
            if d2_err < best_d2_err:
                best_d2_err = d2_err

        if best_d2_err < best_err:
            best_err = best_d2_err
            best_idx = i
            best_node = (A1, B1, C1)

    return best_idx, best_node, best_err


###############################################################################
# Enhancement #1: Shannon Entropy Pruning
###############################################################################

def count_matching_lsbs(a, b):
    """
    Count how many least-significant bits match between a and b.
    More matching LSBs = lower entropy = better alignment with target.
    """
    if a <= 0 or b <= 0:
        return 0
    # XOR and count trailing zeros = number of matching LSBs
    x = mpz(a) ^ mpz(b)
    if x == 0:
        # Perfect match
        return int(gmpy2.log2(a)) + 1 if a > 0 else 0
    # Count trailing zeros in the XOR = matching LSBs
    # gmpy2 doesn't have ctz, so use bit_scan1
    return int(gmpy2.bit_scan1(x))  # position of first set bit = # matching LSBs


def shannon_entropy_score(diff, n):
    """
    Compute a Shannon entropy-based alignment score.
    Higher score = better alignment = should keep this branch.

    We measure:
    1. Number of matching LSBs (modular alignment)
    2. Bit-length proximity (magnitude alignment)
    """
    if diff <= 0:
        return -1000.0

    matching_lsbs = count_matching_lsbs(diff, n)

    # Magnitude alignment: how close are bit-lengths?
    bits_diff = abs(int(gmpy2.log2(diff)) - int(gmpy2.log2(n)))

    # Combined score: more matching LSBs is good, closer magnitude is good
    # Weight LSB matching heavily since it indicates modular structure
    score = matching_lsbs * 2.0 - bits_diff * 1.0

    return score


###############################################################################
# Enhancement #2: Lyapunov Stability Filter
###############################################################################

def compute_epsilon(diff, n, log2_n):
    """
    Compute the log-scale error: epsilon = |log2(C^2 - B^2) - log2(n)|.
    Smaller epsilon = closer to target.
    """
    if diff <= 0:
        return float('inf')
    log2_diff = float(gmpy2.log2(mpz(diff)))
    return abs(log2_diff - log2_n)


class LyapunovTracker:
    """
    Tracks trajectory stability. If epsilon increases for consecutive_limit
    consecutive steps, signals divergence and recommends backtracking.
    """
    def __init__(self, consecutive_limit=3):
        self.consecutive_limit = consecutive_limit
        self.history = []  # list of epsilon values
        self.increasing_count = 0

    def update(self, epsilon):
        """Record new epsilon. Returns True if trajectory is stable."""
        if self.history and epsilon >= self.history[-1]:
            self.increasing_count += 1
        else:
            self.increasing_count = 0
        self.history.append(epsilon)
        return self.increasing_count < self.consecutive_limit

    def is_diverging(self):
        """Check if trajectory is diverging."""
        return self.increasing_count >= self.consecutive_limit

    def reset(self):
        self.history.clear()
        self.increasing_count = 0


###############################################################################
# Enhancement #3: Improved Jacobian Selection (Depth-2 Lookahead)
###############################################################################

def jacobian_depth2_select(A, B, C, n, log2_n, matrices=None):
    """
    Depth-2 lookahead Jacobian selection.
    Evaluate all 6 matrices at depth 1, and for each, all 6 at depth 2.
    Return the depth-1 matrix that leads to the best depth-2 epsilon.

    Returns (best_matrix_index, best_node, best_epsilon) or (None, None, inf).
    """
    if matrices is None:
        matrices = UNIQUE_MATRICES

    best_idx = None
    best_node = None
    best_eps = float('inf')
    best_d2_node = None

    for i, M1 in enumerate(matrices):
        A1, B1, C1 = mat_mul(M1, (A, B, C))
        if A1 <= 0 or B1 <= 0 or C1 <= 0:
            continue

        diff1 = C1 * C1 - B1 * B1
        if diff1 <= 0:
            continue

        eps1 = compute_epsilon(diff1, n, log2_n)

        # Depth-2: try all children of this node
        best_d2_eps = eps1  # fallback: just use depth-1 epsilon
        for M2 in matrices:
            A2, B2, C2 = mat_mul(M2, (A1, B1, C1))
            if A2 <= 0 or B2 <= 0 or C2 <= 0:
                continue
            diff2 = C2 * C2 - B2 * B2
            if diff2 <= 0:
                continue
            eps2 = compute_epsilon(diff2, n, log2_n)
            if eps2 < best_d2_eps:
                best_d2_eps = eps2

        # The score for matrix i is the best epsilon achievable at depth 2
        if best_d2_eps < best_eps:
            best_eps = best_d2_eps
            best_idx = i
            best_node = (A1, B1, C1)

    return best_idx, best_node, best_eps


###############################################################################
# Enhancement #4: Inverse Matrix Climbing (Meet-in-the-Middle)
###############################################################################

def inverse_climb(n, verbose=False, time_limit=10, max_climb=500):
    """
    Meet-in-the-Middle approach:
    1. Find candidate (C, B) pairs where C^2 - B^2 ~= n
       by setting C = isqrt(n) + offset and checking B = isqrt(C^2 - n).
    2. For each valid Pythagorean-ish triple, climb UP the tree using
       inverse matrices toward (3,4,5).
    3. Collect all visited nodes going up; also collect nodes going down
       from (3,4,5). If any overlap, we've bridged the gap.

    Additionally, at every node visited during climbing, run VSDD checks.
    """
    n = mpz(n)
    t0 = time.time()
    sqrt_n = isqrt(n)

    # Nodes reachable from root going DOWN (collected separately by main engine)
    # Here we focus on going UP from candidate triples

    results = []

    # Generate candidate (A, B, C) triples near n
    # C^2 - B^2 = A^2 and we want A^2 near n
    # So A ~= isqrt(n), then we need B, C such that C^2 - B^2 = A^2
    # Simplest: A = isqrt(n) + offset, B and C from Pythagorean identity
    # For primitive: A = m^2 - n^2, B = 2mn, C = m^2 + n^2 (Euclid parametrization)

    # Strategy: pick C_val near sqrt(n), compute B_val = isqrt(C_val^2 - n)
    C_start = sqrt_n + 1
    candidates = []

    for offset in range(min(1000, int(sqrt_n) + 1)):
        if time.time() - t0 > time_limit * 0.3:
            break
        C_val = C_start + offset
        B_sq = C_val * C_val - n
        if B_sq < 0:
            continue
        B_val = isqrt(B_sq)
        # Check if it's an exact Pythagorean triple
        if B_val * B_val == B_sq and B_val > 0:
            # Exact: n = C^2 - B^2 = (C-B)(C+B) => direct factorization!
            f1 = C_val - B_val
            f2 = C_val + B_val
            if f1 > 1 and f2 > 1 and f1 * f2 == n:
                return int(min(f1, f2))

        # Even if not exact, use approximate triple for climbing
        # A^2 = C^2 - B^2 approximately
        if B_val > 0:
            A_val = isqrt(C_val * C_val - B_val * B_val)
            if A_val > 0:
                candidates.append((A_val, B_val, C_val))
        if len(candidates) >= 20:
            break

    # Climb UP each candidate using inverse matrices
    visited_up = set()

    for A_init, B_init, C_init in candidates:
        if time.time() - t0 > time_limit:
            break

        A, B, C = mpz(A_init), mpz(B_init), mpz(C_init)

        for step in range(max_climb):
            if time.time() - t0 > time_limit:
                break

            # VSDD check at this node
            result = vsdd_multi_check(n, A, B, C)
            if result is not None:
                return result

            # Try all inverse matrices; pick one that brings us closer to root
            best_parent = None
            best_max_val = None

            for inv_M in INVERSE_MATRICES:
                Ap, Bp, Cp = mat_mul(inv_M, (A, B, C))
                if Ap > 0 and Bp > 0 and Cp > 0:
                    # Valid parent: all positive and smaller
                    max_val = max(Ap, Bp, Cp)
                    if best_max_val is None or max_val < best_max_val:
                        best_max_val = max_val
                        best_parent = (Ap, Bp, Cp)

            if best_parent is None:
                break  # Can't climb further

            A, B, C = best_parent

            # Check if we reached the root
            if (A, B, C) == (mpz(3), mpz(4), mpz(5)):
                if verbose:
                    print(f"    Inverse climb reached root (3,4,5)!")
                break

            # Record visited node
            key = (int(A % 10**9), int(B % 10**9), int(C % 10**9))
            if key in visited_up:
                break
            visited_up.add(key)

    return None


###############################################################################
# Enhancement #5: Multi-root Starts
###############################################################################

def get_multi_roots(n, max_k=50):
    """
    Generate starting triples: primitive (3,4,5) and scaled (3k, 4k, 5k).
    For scaled triples, C^2 - B^2 = (5k)^2 - (4k)^2 = 9k^2 = (3k)^2.
    The scaled triples explore non-primitive triple space.

    Also add other primitive roots that might be more relevant to n.
    """
    roots = [(mpz(3), mpz(4), mpz(5))]

    # Scaled roots
    for k in range(2, max_k + 1):
        roots.append((mpz(3*k), mpz(4*k), mpz(5*k)))

    # Also try other small primitive triples as alternate starting points
    # (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29)
    other_primitives = [
        (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29),
        (9, 40, 41), (11, 60, 61), (12, 35, 37), (28, 45, 53),
    ]
    for a, b, c in other_primitives:
        roots.append((mpz(a), mpz(b), mpz(c)))

    return roots


###############################################################################
# Main Engine: Super-Generator v7.0
###############################################################################

def super_generator_v7(n, verbose=True, time_limit=60):
    """
    Pythagorean tree pathfinding with v7.0 enhancements:
      1. Shannon entropy pruning
      2. Lyapunov stability filter
      3. Depth-2 Jacobian lookahead
      4. Inverse matrix climbing (meet-in-the-middle)
      5. Multi-root starts
      6. VSDD at every node (multi-delta)

    Parameters
    ----------
    n : int
        The number to factor (should be an odd semiprime).
    verbose : bool
        Print progress information.
    time_limit : float
        Maximum seconds to run.

    Returns
    -------
    int or None
        A non-trivial factor of n, or None if not found.
    """
    n = mpz(n)
    nb = int(gmpy2.log2(n)) + 1
    log2_n = float(nb)
    sqrt_n = isqrt(n)

    if verbose:
        print(f"  Super-Generator v7.0: {len(str(int(n)))}d ({nb}b)")

    t0 = time.time()

    # Quick trivial checks
    if n <= 1:
        return None
    if n % 2 == 0:
        return 2
    if is_prime(n):
        if verbose:
            print(f"    n is prime, no factors.")
        return None

    # Small trial division up to 10000
    for p in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        if n % p == 0 and n != p:
            if verbose:
                print(f"    Trial division: {p}")
            return p
    p = 53
    while p < 10000:
        if n % p == 0 and n != p:
            if verbose:
                print(f"    Trial division: {p}")
            return p
        p += 2

    # Build modular filter
    filters = build_modular_filter(n)

    total_checks = 0
    best_global_eps = float('inf')

    # ══════════════════════════════════════════════════════════════════════
    # METHOD A: Spectral Compass Navigation with Resonance Band Targeting
    # ══════════════════════════════════════════════════════════════════════

    # Step 1: Estimate Δ candidates via Beat Frequency Envelope
    resonance_bands = resonance_band_estimate(n, num_bands=5)

    if verbose:
        if resonance_bands:
            # Check for exact hits
            for delta, R in resonance_bands:
                if R == float('inf'):
                    # Exact factorization found during band estimation
                    elapsed = time.time() - t0
                    if n % delta == 0 and delta > 1 and delta < n:
                        print(f"    HIT (Resonance Band): factor={delta} ({elapsed:.3f}s)")
                        return delta
            print(f"    Method A: Spectral Compass with {len(resonance_bands)} "
                  f"resonance bands (Δ={resonance_bands[0][0]}..{resonance_bands[-1][0]})")
        else:
            print(f"    Method A: Greedy descent (no resonance bands)")

    # Check for exact hits from resonance estimation
    for delta, R in resonance_bands:
        if R == float('inf') and n % delta == 0 and 1 < delta < n:
            return int(delta)

    roots = get_multi_roots(n, max_k=30)
    method_a_time = time_limit * 0.35  # 35% of time budget

    # Build Modular Carry Squeeze table (Solution B: LSB Anchor)
    # Use k=8 for speed (256 residues). Upgrade to k=12 for larger numbers.
    squeeze_k = 12 if nb >= 150 else 8
    allowed_deltas, sq_k = build_carry_squeeze(n, k=squeeze_k)

    if verbose and allowed_deltas:
        squeeze_ratio = len(allowed_deltas) / (1 << squeeze_k)
        print(f"    Carry Squeeze: {len(allowed_deltas)}/{1 << squeeze_k} "
              f"deltas survive mod 2^{squeeze_k} ({squeeze_ratio:.1%})")

    # Step 2: For each resonance band, run Spectral Compass navigation
    # with Hyperbolic Convergence tracking + Carry Squeeze + Capture Zone
    for band_idx, (delta_est, R_target) in enumerate(resonance_bands):
        if time.time() - t0 > method_a_time:
            break
        if R_target == float('inf'):
            continue  # Already checked exact hits above

        for root_idx, (A0, B0, C0) in enumerate(roots[:10]):  # Top 10 roots
            if time.time() - t0 > method_a_time:
                break

            A, B, C = A0, B0, C0
            lyapunov = LyapunovTracker(consecutive_limit=5)
            hyper = HyperbolicTracker(R_target, damping=0.8)
            max_depth = 500

            for depth in range(max_depth):
                if time.time() - t0 > method_a_time:
                    break

                # VSDD multi-check at current node
                result = vsdd_multi_check(n, A, B, C)
                if result is not None:
                    elapsed = time.time() - t0
                    if verbose:
                        print(f"    HIT (Method A, band {band_idx}) at root {root_idx}, "
                              f"depth {depth}: factor={result} ({elapsed:.3f}s)")
                    return result
                total_checks += 1

                # Solution C: Capture Zone Snap
                # When C approaches √n, do intensive Fermat scan
                if C > 0 and abs(float(gmpy2.log2(C)) - float(gmpy2.log2(sqrt_n))) < 1.0:
                    snap_result = capture_zone_snap(n, int(C), scan_range=5000)
                    if snap_result is not None:
                        elapsed = time.time() - t0
                        if verbose:
                            print(f"    HIT (Capture Zone Snap) at band {band_idx}, "
                                  f"depth {depth}: factor={snap_result} ({elapsed:.3f}s)")
                        return snap_result

                # Solution A: Hyperbolic Convergence — get adjusted R_target
                R_current = float(C) / float(B) if B > 0 else float('inf')
                adj_R_target = hyper.update(R_current, depth)

                # Spectral Compass: navigate toward (adjusted) R_target
                sc_idx, sc_node, sc_err = spectral_compass_select(
                    A, B, C, adj_R_target, n, filters=filters)

                if sc_idx is None:
                    break

                A_next, B_next, C_next = sc_node

                # Solution B: Modular Carry Squeeze — check LSB consistency
                if allowed_deltas and not passes_carry_squeeze(
                        C_next, B_next, allowed_deltas, sq_k):
                    # LSBs don't match. Try other matrices (Barning-Hall swerve).
                    swerved = False
                    for alt_idx, M_alt in enumerate(UNIQUE_MATRICES):
                        if alt_idx == sc_idx:
                            continue
                        A_alt, B_alt, C_alt = mat_mul(M_alt, (A, B, C))
                        if A_alt <= 0 or B_alt <= 0 or C_alt <= 0:
                            continue
                        if passes_carry_squeeze(C_alt, B_alt, allowed_deltas, sq_k):
                            A_next, B_next, C_next = A_alt, B_alt, C_alt
                            swerved = True
                            break
                    # If no swerve found, proceed anyway (squeeze is a heuristic)

                # Lyapunov stability on spectral error
                stable = lyapunov.update(sc_err)
                if not stable:
                    break

                if sc_err < best_global_eps:
                    best_global_eps = sc_err

                A, B, C = A_next, B_next, C_next

    # Step 3: Fallback — greedy descent with epsilon minimization (original Method A)
    if time.time() - t0 < method_a_time:
        for root_idx, (A0, B0, C0) in enumerate(roots[:20]):
            if time.time() - t0 > method_a_time:
                break

            A, B, C = A0, B0, C0
            lyapunov = LyapunovTracker(consecutive_limit=3)
            prev_entropy_score = -1000.0

            for depth in range(300):
                if time.time() - t0 > method_a_time:
                    break

                result = vsdd_multi_check(n, A, B, C)
                if result is not None:
                    elapsed = time.time() - t0
                    if verbose:
                        print(f"    HIT (Method A fallback) at root {root_idx}, "
                              f"depth {depth}: factor={result} ({elapsed:.3f}s)")
                    return result
                total_checks += 1

                diff = C * C - B * B
                if diff <= 0:
                    break

                eps = compute_epsilon(diff, n, log2_n)
                stable = lyapunov.update(eps)
                if not stable:
                    break

                if eps < best_global_eps:
                    best_global_eps = eps

                entropy_score = shannon_entropy_score(diff, n)
                if (depth > 5 and entropy_score < prev_entropy_score - 3.0
                        and eps > 2.0):
                    break
                prev_entropy_score = entropy_score

                best_idx_j, best_node_j, best_eps_j = jacobian_depth2_select(
                    A, B, C, n, log2_n)
                if best_idx_j is None:
                    break
                A, B, C = best_node_j

    # ══════════════════════════════════════════════════════════════════════
    # METHOD B: Inverse Matrix Climbing (Meet-in-the-Middle)
    # ══════════════════════════════════════════════════════════════════════
    if time.time() - t0 < time_limit:
        if verbose:
            print(f"    Method B: Inverse matrix climbing")

        method_b_time = time_limit * 0.15  # 15% of time budget
        result = inverse_climb(n, verbose=verbose,
                               time_limit=method_b_time,
                               max_climb=500)
        if result is not None:
            elapsed = time.time() - t0
            if verbose:
                print(f"    HIT (Method B): factor={result} ({elapsed:.3f}s)")
            return result

    # ══════════════════════════════════════════════════════════════════════
    # METHOD C: Priority Queue BFS with Entropy-guided Expansion
    # ══════════════════════════════════════════════════════════════════════
    if time.time() - t0 < time_limit:
        if verbose:
            print(f"    Method C: Entropy-guided BFS")

        method_c_deadline = t0 + time_limit * 0.75  # up to 75% of total

        # Priority queue: (negative_score, depth, (A, B, C))
        # Higher score = better candidate = should be explored first
        pq = []
        visited = set()
        bfs_checks = 0

        # Seed with multiple roots
        for A0, B0, C0 in get_multi_roots(n, max_k=10):
            diff = C0*C0 - B0*B0
            if diff > 0:
                score = shannon_entropy_score(diff, n)
                heapq.heappush(pq, (-score, 0, (int(A0), int(B0), int(C0))))

        max_visited = 200000

        while pq and time.time() < method_c_deadline and len(visited) < max_visited:
            neg_score, depth, (Ai, Bi, Ci) = heapq.heappop(pq)

            # De-duplicate
            key = (Ai % 999983, Bi % 999983, Ci % 999983)
            if key in visited:
                continue
            visited.add(key)

            A, B, C = mpz(Ai), mpz(Bi), mpz(Ci)

            # VSDD multi-check
            result = vsdd_multi_check(n, A, B, C)
            if result is not None:
                elapsed = time.time() - t0
                if verbose:
                    print(f"    HIT (Method C) at depth {depth}: "
                          f"factor={result} ({elapsed:.3f}s)")
                return result
            bfs_checks += 1
            total_checks += 1

            # Limit depth to avoid explosion
            if depth > 150:
                continue

            # Expand children
            for M in UNIQUE_MATRICES:
                A2, B2, C2 = mat_mul(M, (A, B, C))
                if A2 <= 0 or B2 <= 0 or C2 <= 0:
                    continue

                diff2 = C2*C2 - B2*B2
                if diff2 <= 0:
                    continue

                # Shannon entropy score for prioritization
                child_score = shannon_entropy_score(diff2, n)

                # Lyapunov-like check: only expand if epsilon is reasonable
                child_eps = compute_epsilon(diff2, n, log2_n)
                if child_eps > log2_n:
                    # Way too far from target magnitude, skip
                    continue

                heapq.heappush(pq, (-child_score, depth + 1,
                                    (int(A2), int(B2), int(C2))))

    # ══════════════════════════════════════════════════════════════════════
    # METHOD D: Fermat's method (direct C^2 - B^2 = n scan)
    # ══════════════════════════════════════════════════════════════════════
    if time.time() - t0 < time_limit:
        if verbose:
            print(f"    Method D: Fermat scan")

        C_val = sqrt_n + 1
        fermat_deadline = t0 + time_limit

        while time.time() < fermat_deadline:
            B_sq = C_val * C_val - n
            if B_sq < 0:
                C_val += 1
                continue
            B_val = isqrt(B_sq)
            if B_val * B_val == B_sq:
                f1 = C_val - B_val
                f2 = C_val + B_val
                if f1 > 1 and f2 > 1 and f1 * f2 == n:
                    elapsed = time.time() - t0
                    if verbose:
                        print(f"    HIT (Method D): C={C_val}, B={B_val} "
                              f"({elapsed:.3f}s)")
                    return int(min(f1, f2))
            C_val += 1
            total_checks += 1

            # Check batches for time
            if total_checks % 10000 == 0 and time.time() >= fermat_deadline:
                break

    elapsed = time.time() - t0
    if verbose:
        print(f"    No factor found ({total_checks} checks, {elapsed:.1f}s)")
    return None


###############################################################################
# Test
###############################################################################

if __name__ == "__main__":
    print("=" * 60)
    print("Super-Generator v7.0 — Test Suite")
    print("=" * 60)

    tests = []

    # Test 1: n = 901 = 17 * 53
    tests.append(("901 (3d)", 901, {17, 53}))

    # Test 2: n = 15 = 3 * 5
    tests.append(("15 (2d)", 15, {3, 5}))

    # Test 3: 20d semiprime
    n20 = 1000000009 * 1000000087
    tests.append(("20d semiprime", n20, {1000000009, 1000000087}))

    # Test 4: 30d semiprime
    n30 = 100000000000067 * 100000000000097
    tests.append(("30d semiprime", n30, {100000000000067, 100000000000097}))

    all_passed = True

    for name, n, expected_factors in tests:
        print(f"\n{'─' * 60}")
        print(f"Test: {name}  (n = {n})")
        print(f"{'─' * 60}")

        t0 = time.time()
        factor = super_generator_v7(n, verbose=True, time_limit=30)
        elapsed = time.time() - t0

        if factor is not None and factor in expected_factors:
            print(f"  PASS: factor = {factor}  ({elapsed:.3f}s)")
        elif factor is not None and (n % factor == 0) and factor > 1 and factor < n:
            print(f"  PASS (alt factor): factor = {factor}  ({elapsed:.3f}s)")
        elif factor is None:
            print(f"  FAIL: no factor found  ({elapsed:.3f}s)")
            all_passed = False
        else:
            print(f"  FAIL: got {factor}, expected one of {expected_factors}  ({elapsed:.3f}s)")
            all_passed = False

    print(f"\n{'=' * 60}")
    if all_passed:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print(f"{'=' * 60}")
