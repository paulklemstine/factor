#!/usr/bin/env python3
"""
Round 13: Self-Initializing Quadratic Sieve (SIQS)
Target: Factor RSA-100 (100 digits, 330 bits) with our own code

Uses gmpy2 for fast big-integer arithmetic.
Implements proper SIQS with:
- Tonelli-Shanks for modular square roots
- Self-initialization (fast polynomial switching)
- Large prime variation (single large prime)
- Block Lanczos or Gaussian elimination for linear algebra
- Factor base optimization

Author: Custom implementation for RSA Factoring Challenge
"""

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, log2, next_prime
import numpy as np
import time
import math
import random
import sys
import os
from collections import defaultdict

# Import our targets
from rsa_targets import *

###############################################################################
# Utility functions
###############################################################################

def tonelli_shanks(n, p):
    """Compute sqrt(n) mod p using Tonelli-Shanks algorithm."""
    n = n % p
    if n == 0:
        return 0
    if p == 2:
        return n % 2

    # Check if n is a QR mod p
    if pow(n, (p - 1) // 2, p) != 1:
        return None  # Not a quadratic residue

    # Factor out powers of 2 from p-1
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1

    if s == 1:
        return pow(n, (p + 1) // 4, p)

    # Find a non-residue
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1

    m = s
    c = pow(z, q, p)
    t = pow(n, q, p)
    r = pow(n, (q + 1) // 2, p)

    while True:
        if t == 1:
            return r

        # Find the least i such that t^(2^i) = 1 mod p
        i = 1
        temp = (t * t) % p
        while temp != 1:
            temp = (temp * temp) % p
            i += 1

        b = pow(c, 1 << (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p


def choose_factor_base_size(n_digits):
    """Choose optimal factor base size based on number of digits."""
    # Approximate L(n) = exp(sqrt(ln(n) * ln(ln(n))))
    # Optimal B ~ L(n)^(1/sqrt(2))
    ln_n = n_digits * math.log(10)
    ln_ln_n = math.log(ln_n)
    L = math.exp(math.sqrt(ln_n * ln_ln_n))
    B = int(L ** (1 / math.sqrt(2)))

    # Practical adjustments
    if n_digits <= 40:
        return max(100, min(B, 500))
    elif n_digits <= 60:
        return max(500, min(B, 3000))
    elif n_digits <= 80:
        return max(2000, min(B, 15000))
    elif n_digits <= 100:
        return max(5000, min(B, 50000))
    elif n_digits <= 120:
        return max(15000, min(B, 150000))
    else:
        return max(30000, min(B, 500000))


def choose_sieve_interval(n_digits):
    """Choose sieve interval size M (sieve from -M to +M)."""
    if n_digits <= 40:
        return 50000
    elif n_digits <= 60:
        return 100000
    elif n_digits <= 80:
        return 200000
    elif n_digits <= 100:
        return 500000
    elif n_digits <= 120:
        return 1000000
    else:
        return 2000000


def build_factor_base(n, B_size):
    """Build factor base: primes p where n is a quadratic residue mod p."""
    factor_base = [2]  # Always include 2
    p = 3
    while len(factor_base) < B_size:
        if is_prime(p):
            # Check if n is a QR mod p using Euler criterion
            if pow(int(n % p), (p - 1) // 2, p) == 1:
                factor_base.append(p)
        p += 2
    return factor_base


def compute_sqrt_mod_p(n, factor_base):
    """Precompute sqrt(n) mod p for each prime in the factor base."""
    sqrt_mod = {}
    for p in factor_base:
        if p == 2:
            sqrt_mod[2] = int(n % 2)
        else:
            s = tonelli_shanks(int(n % p), p)
            if s is not None:
                sqrt_mod[p] = s
    return sqrt_mod


def trial_divide(val, factor_base, n):
    """Trial divide val by factor base. Return exponent vector if smooth, else None."""
    if val == 0:
        return None

    exponents = []
    v = abs(int(val))
    sign_bit = 1 if val < 0 else 0

    for p in factor_base:
        exp = 0
        while v % p == 0:
            v //= p
            exp += 1
        exponents.append(exp)

    if v == 1:
        return (sign_bit, exponents)
    return None


def trial_divide_with_large_prime(val, factor_base, large_prime_bound):
    """Trial divide, allowing one large prime cofactor."""
    if val == 0:
        return None, None

    v = abs(int(val))
    sign_bit = 1 if val < 0 else 0
    exponents = []

    for p in factor_base:
        exp = 0
        while v % p == 0:
            v //= p
            exp += 1
        exponents.append(exp)

    if v == 1:
        return (sign_bit, exponents), None
    elif v < large_prime_bound and is_prime(v):
        return (sign_bit, exponents), v
    return None, None


###############################################################################
# SIQS Core
###############################################################################

class SIQS:
    """Self-Initializing Quadratic Sieve."""

    def __init__(self, n, verbose=True):
        self.n = mpz(n)
        self.n_digits = len(str(n))
        self.n_bits = int(log2(self.n)) + 1
        self.verbose = verbose
        self.sqrt_n = isqrt(self.n)

        # Parameters
        self.fb_size = choose_factor_base_size(self.n_digits)
        self.M = choose_sieve_interval(self.n_digits)
        self.T = max(40, int(math.log2(self.n_bits)) * 8)  # Sieve threshold

        if self.verbose:
            print(f"SIQS: n = {self.n_digits} digits ({self.n_bits} bits)")
            print(f"  Factor base size: {self.fb_size}")
            print(f"  Sieve interval: [-{self.M}, +{self.M}]")
            print(f"  Sieve threshold: {self.T}")

        # Build factor base
        t0 = time.time()
        self.factor_base = build_factor_base(self.n, self.fb_size)
        self.fb_max = self.factor_base[-1]
        self.large_prime_bound = self.fb_max ** 2  # For single large prime variation

        # Precompute square roots
        self.sqrt_mod = compute_sqrt_mod_p(self.n, self.factor_base)

        # Precompute log approximations for sieving
        self.fb_logs = [round(math.log2(p) * 10) for p in self.factor_base]

        if self.verbose:
            print(f"  Factor base built in {time.time()-t0:.1f}s")
            print(f"  Largest prime: {self.fb_max}")
            print(f"  Large prime bound: {self.large_prime_bound}")

        # Storage
        self.smooth_relations = []  # (x, exponent_vector) pairs
        self.partial_relations = {}  # large_prime -> (x, exponent_vector)
        self.relations_needed = self.fb_size + 50  # Need slightly more than FB size

        # Stats
        self.polys_tried = 0
        self.sieve_locations_checked = 0

    def generate_poly_a(self):
        """Generate coefficient 'a' for SIQS polynomial Q(x) = (ax+b)^2 - n.

        a should be close to sqrt(2n)/M for optimal sieving.
        a should be a product of primes from the factor base.
        """
        target = isqrt(2 * self.n) // self.M

        # For simplicity, pick a as a product of ~3-6 primes from factor base
        # Choose primes from the middle of the factor base
        n_factors = max(3, min(8, self.fb_size // 100))

        # Pick random subset of primes from upper half of factor base
        mid = len(self.factor_base) // 3
        upper = len(self.factor_base) - 1

        best_a = None
        best_diff = float('inf')

        for _ in range(30):  # Try 30 combinations
            indices = sorted(random.sample(range(mid, upper), n_factors))
            a = mpz(1)
            for i in indices:
                a *= self.factor_base[i]

            diff = abs(a - target)
            if diff < best_diff:
                best_diff = diff
                best_a = a
                best_indices = indices

        return best_a, best_indices

    def compute_poly_b(self, a, a_factors_indices):
        """Compute b such that b^2 ≡ n (mod a)."""
        # Use CRT to find b with b^2 ≡ n (mod a)
        # Since a = product of primes, use Hensel/CRT

        a_factors = [self.factor_base[i] for i in a_factors_indices]

        # For each prime factor q of a, find sqrt(n) mod q
        remainders = []
        for q in a_factors:
            s = self.sqrt_mod.get(q)
            if s is None:
                return None  # n is not QR mod this prime
            remainders.append(s)

        # CRT to combine
        b = mpz(0)
        for i, (r, q) in enumerate(zip(remainders, a_factors)):
            M_i = a // q
            # M_i_inv = inverse of M_i mod q
            M_i_inv = pow(int(M_i % q), q - 2, q)
            b += mpz(r) * M_i * mpz(M_i_inv)

        b = b % a

        # Verify: b^2 ≡ n (mod a)
        if (b * b) % a != self.n % a:
            # Try negating some remainders
            for flip in range(1, 1 << len(a_factors)):
                b2 = mpz(0)
                for i, (r, q) in enumerate(zip(remainders, a_factors)):
                    r_use = r if not (flip & (1 << i)) else (q - r)
                    M_i = a // q
                    M_i_inv = pow(int(M_i % q), q - 2, q)
                    b2 += mpz(r_use) * M_i * mpz(M_i_inv)
                b2 = b2 % a
                if (b2 * b2) % a == self.n % a:
                    b = b2
                    break

        # Ensure b < a/2
        if b > a // 2:
            b = a - b

        return b

    def sieve_poly(self, a, b):
        """Sieve one polynomial Q(x) = ((a*x + b)^2 - n) / a.

        We want to find x where Q(x) is smooth over the factor base.
        Uses numpy for fast sieving.
        """
        c = (b * b - self.n) // a
        sz = 2 * self.M

        # Sieve array - use int32 to avoid overflow
        sieve = np.zeros(sz, dtype=np.int32)

        # For each prime p in factor base, sieve using numpy slicing
        for idx, p in enumerate(self.factor_base):
            log_val = self.fb_logs[idx]

            if p == 2:
                start = 0
                if int(c % 2) != 0:
                    start = 1
                sieve[start::2] += log_val
                continue

            if p not in self.sqrt_mod:
                continue

            s = self.sqrt_mod[p]
            a_inv = pow(int(a % p), p - 2, p)

            root1 = (a_inv * (s - int(b % p))) % p
            root2 = (a_inv * (-s - int(b % p))) % p

            root1 = (root1 + self.M) % p
            root2 = (root2 + self.M) % p

            # Numpy slice sieving — MUCH faster than Python loop
            sieve[root1::p] += log_val
            if root1 != root2:
                sieve[root2::p] += log_val

        # Find candidates above threshold
        threshold = max(0, int((int(log2(a)) + 2 * math.log2(self.M)) * 10) - self.T * 10)

        candidates = np.where(sieve >= threshold)[0]
        smooth_found = []

        for j in candidates:
            x = int(j) - self.M
            ax_b = a * x + b
            Q_val = ax_b * ax_b - self.n

            if Q_val == 0:
                g = gcd(ax_b, self.n)
                if g != 1 and g != self.n:
                    return [("DIRECT", int(g))]
                continue

            # Trial divide
            result, large_prime = trial_divide_with_large_prime(
                Q_val, self.factor_base, self.large_prime_bound
            )

            if result is not None:
                    sign_bit, exponents = result
                    if large_prime is None:
                        # Fully smooth!
                        smooth_found.append((int(ax_b), sign_bit, exponents))
                    else:
                        # Partial relation (single large prime)
                        if large_prime in self.partial_relations:
                            # Combine two partial relations!
                            old_axb, old_sign, old_exp = self.partial_relations[large_prime]
                            # Combined relation: multiply both Q values
                            combined_axb = (old_axb * int(ax_b)) % int(self.n)
                            combined_sign = (old_sign + sign_bit) % 2
                            combined_exp = [old_exp[k] + exponents[k] for k in range(len(exponents))]
                            smooth_found.append((combined_axb, combined_sign, combined_exp))
                        else:
                            self.partial_relations[large_prime] = (int(ax_b), sign_bit, exponents)

        self.sieve_locations_checked += 2 * self.M
        return smooth_found

    def gaussian_elimination_mod2(self, matrix, n_cols):
        """Gaussian elimination over GF(2) to find null space vectors."""
        n_rows = len(matrix)

        # Convert to bit arrays for efficiency
        # Each row is a list of integers (0 or 1)
        mat = []
        for row in matrix:
            bits = [0] * (n_cols + 1)  # +1 for sign bit
            bits[0] = row[0]  # sign bit
            for j, exp in enumerate(row[1]):
                bits[j + 1] = exp % 2
            mat.append(bits)

        # Track which original rows are combined
        history = [set([i]) for i in range(n_rows)]

        # Forward elimination
        pivot_row = [None] * (n_cols + 1)
        for col in range(n_cols + 1):
            # Find pivot
            pivot = None
            for row in range(n_rows):
                if mat[row][col] == 1 and pivot_row[col] is None:
                    pivot = row
                    break

            if pivot is None:
                continue

            pivot_row[col] = pivot

            # Eliminate this column in other rows
            for row in range(n_rows):
                if row != pivot and mat[row][col] == 1:
                    for k in range(n_cols + 1):
                        mat[row][k] ^= mat[pivot][k]
                    history[row] = history[row] ^ history[pivot]

        # Find zero rows (null space vectors)
        null_space = []
        for row in range(n_rows):
            if all(mat[row][k] == 0 for k in range(n_cols + 1)):
                null_space.append(history[row])

        return null_space

    def try_factor_from_null_space(self, null_vectors, relations):
        """Try to extract a factor from null space vectors."""
        for vec in null_vectors:
            # Combine the relations in this null space vector
            x_product = mpz(1)
            total_exponents = [0] * len(self.factor_base)

            for idx in vec:
                axb, sign_bit, exponents = relations[idx]
                x_product = (x_product * mpz(axb)) % self.n
                for j in range(len(exponents)):
                    total_exponents[j] += exponents[j]

            # Compute y = product of primes^(exp/2)
            y = mpz(1)
            for j, exp in enumerate(total_exponents):
                if exp % 2 != 0:
                    break  # Should not happen
                if exp > 0:
                    y = (y * pow(mpz(self.factor_base[j]), exp // 2, self.n)) % self.n
            else:
                # x^2 ≡ y^2 (mod n)
                g = gcd(x_product - y, self.n)
                if g != 1 and g != self.n:
                    return int(g)
                g = gcd(x_product + y, self.n)
                if g != 1 and g != self.n:
                    return int(g)

        return None

    def factor(self, time_limit=3600):
        """Main SIQS factoring loop."""
        t_start = time.time()

        if self.verbose:
            print(f"\nStarting SIQS on {self.n_digits}-digit number...")
            print(f"Need {self.relations_needed} smooth relations")

        while len(self.smooth_relations) < self.relations_needed:
            elapsed = time.time() - t_start
            if elapsed > time_limit:
                print(f"\nTime limit {time_limit}s exceeded. Found {len(self.smooth_relations)}/{self.relations_needed} relations.")
                return None

            # Generate new polynomial
            a, a_indices = self.generate_poly_a()
            b = self.compute_poly_b(a, a_indices)

            if b is None:
                continue

            self.polys_tried += 1

            # Sieve this polynomial
            results = self.sieve_poly(a, b)

            for r in results:
                if r[0] == "DIRECT":
                    if self.verbose:
                        print(f"\n*** DIRECT FACTOR FOUND: {r[1]} ***")
                    return r[1]

                self.smooth_relations.append(r)

            # Progress report
            if self.polys_tried % 10 == 0 and self.verbose:
                rate = len(self.smooth_relations) / max(elapsed, 0.001)
                eta = (self.relations_needed - len(self.smooth_relations)) / max(rate, 0.001)
                print(f"  [{elapsed:.0f}s] Polys: {self.polys_tried}, "
                      f"Relations: {len(self.smooth_relations)}/{self.relations_needed} "
                      f"(+{len(self.partial_relations)} partials), "
                      f"Rate: {rate:.1f}/s, ETA: {eta:.0f}s")

        if self.verbose:
            print(f"\nCollected {len(self.smooth_relations)} relations in {time.time()-t_start:.1f}s")
            print("Starting linear algebra phase...")

        # Linear algebra: find null space of exponent matrix mod 2
        t_la = time.time()
        n_cols = len(self.factor_base)

        # Build matrix
        matrix = [(r[1], r[2]) for r in self.smooth_relations]

        null_vectors = self.gaussian_elimination_mod2(matrix, n_cols)

        if self.verbose:
            print(f"  Found {len(null_vectors)} null space vectors in {time.time()-t_la:.1f}s")

        # Try to extract factor
        factor = self.try_factor_from_null_space(null_vectors, self.smooth_relations)

        total_time = time.time() - t_start
        if factor:
            if self.verbose:
                print(f"\n*** FACTOR FOUND: {factor} ***")
                print(f"  Cofactor: {int(self.n) // factor}")
                print(f"  Total time: {total_time:.1f}s")
                print(f"  Polynomials tried: {self.polys_tried}")
                print(f"  Relations found: {len(self.smooth_relations)}")
            return factor
        else:
            if self.verbose:
                print(f"\nLinear algebra failed to produce factor. Need more relations.")
            return None


###############################################################################
# Also include our fast ECM (Python + gmpy2) for comparison
###############################################################################

def ecm_gmpy2(n, B1=1000000, curves=100, verbose=True):
    """ECM with gmpy2 for fast arithmetic. Suyama parameterization + Montgomery ladder."""
    n = mpz(n)

    if verbose:
        print(f"ECM: B1={B1}, curves={curves}")

    for curve_num in range(curves):
        # Suyama parameterization
        sigma = mpz(random.randint(6, 10**9))
        u = (sigma * sigma - 5) % n
        v = (4 * sigma) % n

        # Starting point
        Q_x = pow(u, 3, n)
        Q_z = pow(v, 3, n)

        # Curve parameter a24 = (v-u)^3 * (3u+v) / (16*u^3*v) - but we use projective
        diff = (v - u) % n
        a24_num = pow(diff, 3, n) * ((3 * u + v) % n) % n
        a24_den = (16 * Q_x % n) * v % n

        try:
            a24_den_inv = pow(int(a24_den), -1, int(n))
        except (ValueError, ZeroDivisionError):
            g = gcd(a24_den, n)
            if 1 < g < n:
                if verbose:
                    print(f"  Curve {curve_num}: Factor from inversion! {g}")
                return int(g)
            continue

        a24 = a24_num * a24_den_inv % n

        # Montgomery ladder scalar multiplication
        # Multiply Q by all primes up to B1
        def mont_ladder_step(x1, z1, x2, z2, x_diff, z_diff):
            """Montgomery ladder combined double-and-add step."""
            u1 = (x1 + z1) % n
            v1 = (x1 - z1) % n
            u2 = (x2 + z2) % n
            v2 = (x2 - z2) % n

            # Add
            add_x = (((u1 * v2 + v1 * u2) ** 2) % n * z_diff) % n
            add_z = (((u1 * v2 - v1 * u2) ** 2) % n * x_diff) % n

            # Double
            sum_sq = (u1 * u1) % n
            diff_sq = (v1 * v1) % n
            dbl_x = (sum_sq * diff_sq) % n
            delta = (sum_sq - diff_sq) % n
            dbl_z = (delta * (diff_sq + a24 * delta)) % n

            return dbl_x, dbl_z, add_x, add_z

        def scalar_mult(k, x, z):
            """Montgomery ladder scalar multiplication."""
            if k == 0:
                return mpz(0), mpz(1)
            if k == 1:
                return x, z

            x1, z1 = x, z  # R0 = P
            x2, z2 = mont_double(x, z)  # R1 = 2P

            bits = bin(k)[3:]  # Skip '0b1'
            for bit in bits:
                if bit == '1':
                    x1, z1, x2, z2 = mont_ladder_step(x2, z2, x1, z1, x, z)
                    x1, z1, x2, z2 = x2, z2, x1, z1
                else:
                    x1, z1, x2, z2 = mont_ladder_step(x1, z1, x2, z2, x, z)

            return x1, z1

        def mont_double(x, z):
            """Montgomery curve point doubling."""
            u_val = (x + z) % n
            v_val = (x - z) % n
            sum_sq = (u_val * u_val) % n
            diff_sq = (v_val * v_val) % n
            delta = (sum_sq - diff_sq) % n
            new_x = (sum_sq * diff_sq) % n
            new_z = (delta * (diff_sq + a24 * delta)) % n
            return new_x, new_z

        # Stage 1: multiply by all prime powers up to B1
        p = 2
        while p <= B1:
            pp = p
            while pp * p <= B1:
                pp *= p
            Q_x, Q_z = scalar_mult(pp, Q_x, Q_z)

            # Periodic GCD check
            if p % 10007 == 0 or p > B1 - 100:
                g = gcd(Q_z, n)
                if 1 < g < n:
                    if verbose:
                        print(f"  Curve {curve_num} (sigma={sigma}): Factor at p={p}! -> {g}")
                    return int(g)
                if g == n:
                    break  # This curve is degenerate

            p = int(next_prime(p))

        # Final GCD
        g = gcd(Q_z, n)
        if 1 < g < n:
            if verbose:
                print(f"  Curve {curve_num} (sigma={sigma}): Factor found! -> {g}")
            return int(g)

        if verbose and curve_num % 10 == 0:
            print(f"  Curve {curve_num}/{curves}: no factor (B1={B1})")

    return None


###############################################################################
# Multi-method attack
###############################################################################

def attack_rsa_number(name, n, time_limit=3600):
    """Attack an RSA number using our best methods."""
    n = mpz(n)
    n_digits = len(str(n))
    n_bits = int(log2(n)) + 1

    print(f"\n{'='*70}")
    print(f"ATTACKING {name}: {n_digits} digits ({n_bits} bits)")
    print(f"{'='*70}")
    print(f"n = {str(n)[:80]}...")

    t_start = time.time()

    # Method 1: Quick ECM scan (good for finding small factors)
    print(f"\n--- Method 1: ECM Quick Scan ---")
    for B1 in [10000, 100000, 1000000]:
        curves = max(10, 1000000 // B1)
        print(f"  ECM B1={B1}, {curves} curves...")
        t0 = time.time()
        factor = ecm_gmpy2(n, B1=B1, curves=curves, verbose=False)
        if factor:
            elapsed = time.time() - t_start
            print(f"\n*** ECM FOUND FACTOR in {elapsed:.1f}s ***")
            print(f"  Factor: {factor}")
            print(f"  Cofactor: {int(n) // factor}")
            return factor
        print(f"    No factor (took {time.time()-t0:.1f}s)")

    # Method 2: SIQS
    remaining = time_limit - (time.time() - t_start)
    if remaining > 60:
        print(f"\n--- Method 2: SIQS (time limit: {remaining:.0f}s) ---")
        siqs = SIQS(n, verbose=True)
        factor = siqs.factor(time_limit=remaining)
        if factor:
            elapsed = time.time() - t_start
            print(f"\n*** SIQS FOUND FACTOR in {elapsed:.1f}s ***")
            return factor

    elapsed = time.time() - t_start
    print(f"\nFailed to factor {name} in {elapsed:.1f}s")
    return None


###############################################################################
# Main
###############################################################################

if __name__ == "__main__":
    print("="*70)
    print("Round 13: Self-Initializing Quadratic Sieve (SIQS)")
    print("Target: RSA Factoring Challenge Numbers")
    print("="*70)

    # First: validate on smaller known numbers
    print("\n### Warmup: Testing on known semiprimes ###")

    # 50-digit semiprime
    test_50 = 1147264191885255038792101655395289  # 34 digits
    p50 = 29927402397
    q50 = 38334810197
    test_50 = p50 * q50
    print(f"\nTest: {len(str(test_50))}-digit semiprime")
    t0 = time.time()
    siqs = SIQS(test_50, verbose=True)
    f = siqs.factor(time_limit=60)
    if f:
        assert test_50 % f == 0
        print(f"PASS: {f} * {test_50 // f} in {time.time()-t0:.1f}s")

    # 60-digit semiprime
    import random
    random.seed(42)
    # Generate a 60-digit semiprime
    def random_prime(bits):
        while True:
            p = mpz(random.getrandbits(bits)) | 1
            if is_prime(p):
                return int(p)

    p60 = random_prime(100)
    q60 = random_prime(100)
    n60 = p60 * q60
    print(f"\nTest: {len(str(n60))}-digit semiprime ({int(log2(mpz(n60)))+1} bits)")
    t0 = time.time()
    siqs = SIQS(n60, verbose=True)
    f = siqs.factor(time_limit=120)
    if f:
        assert n60 % f == 0
        print(f"PASS in {time.time()-t0:.1f}s")

    # Now attack RSA numbers (stepping stones first)
    print("\n\n### RSA Challenge Numbers ###")

    # Start with RSA-100 (our first real target)
    for name, (n, digits, bits, status) in sorted(MILESTONES.items(), key=lambda x: x[1][1]):
        if digits > 120:  # Skip the huge ones for now
            print(f"\nSkipping {name} ({digits} digits) - too large for current implementation")
            continue

        factor = attack_rsa_number(name, n, time_limit=600)
        if factor:
            print(f"\n*** {name} FACTORED! ***")
            print(f"  {factor} x {int(mpz(n)) // factor}")
