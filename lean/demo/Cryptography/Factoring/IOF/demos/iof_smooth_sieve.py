#!/usr/bin/env python3
"""
IOF Smooth Number Sieve Demo

Demonstrates the smooth number sieve component of IOF:
- Dickman function approximation for smooth number probability
- Factor base construction and relation collection
- GF(2) linear algebra for finding congruences of squares
- Comparison of IOF orbit-based vs. random relation finding

Usage:
    python iof_smooth_sieve.py
"""

import math
import random
from functools import lru_cache


# ─── Dickman Function Approximation ───────────────────────────────

@lru_cache(maxsize=1000)
def dickman_rho(u, steps=100):
    """
    Approximate the Dickman function ρ(u).

    ρ(u) gives the probability that a random integer n is n^(1/u)-smooth.

    For u ≤ 1: ρ(u) = 1
    For u > 1: ρ(u) = ρ(u-1) - integral from u-1 to u of ρ(t-1)/t dt

    We use the approximation ρ(u) ≈ u^(-u) for simplicity.
    """
    if u <= 0:
        return 1.0
    if u <= 1:
        return 1.0
    if u <= 2:
        return 1.0 - math.log(u)

    # Numerical approximation via u^(-u) for larger u
    try:
        return u ** (-u)
    except OverflowError:
        return 0.0


def smooth_probability(x, B):
    """Probability that a random integer ≤ x is B-smooth."""
    if x <= 1 or B <= 1:
        return 0.0
    u = math.log(x) / math.log(B)
    return dickman_rho(round(u * 10) / 10)  # round for caching


# ─── Factor Base and Sieving ──────────────────────────────────────

def sieve_of_eratosthenes(limit):
    """Return list of primes up to limit."""
    if limit < 2:
        return []
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
    return [i for i in range(2, limit + 1) if is_prime[i]]


def trial_divide(n, factor_base):
    """Try to factor n over the factor base. Return (success, exponents)."""
    exponents = [0] * len(factor_base)
    temp = n
    for i, p in enumerate(factor_base):
        while temp % p == 0:
            exponents[i] += 1
            temp //= p
    return temp == 1, exponents


def gaussian_elimination_gf2(matrix):
    """
    Perform Gaussian elimination over GF(2) to find null space vectors.
    Returns a list of sets of row indices whose XOR is zero.
    """
    rows = len(matrix)
    cols = len(matrix[0]) if rows > 0 else 0

    # Augment with identity for tracking
    augmented = [row[:] + [1 if i == j else 0 for j in range(rows)]
                 for i, row in enumerate(matrix)]

    pivot_cols = []
    row_idx = 0

    for col in range(cols):
        # Find pivot
        pivot = None
        for r in range(row_idx, rows):
            if augmented[r][col] == 1:
                pivot = r
                break
        if pivot is None:
            continue

        # Swap
        augmented[row_idx], augmented[pivot] = augmented[pivot], augmented[row_idx]
        pivot_cols.append(col)

        # Eliminate
        for r in range(rows):
            if r != row_idx and augmented[r][col] == 1:
                augmented[r] = [(a + b) % 2 for a, b in zip(augmented[r], augmented[row_idx])]

        row_idx += 1

    # Find null space vectors
    null_vectors = []
    for r in range(row_idx, rows):
        if all(augmented[r][c] == 0 for c in range(cols)):
            indices = {j for j in range(rows) if augmented[r][cols + j] == 1}
            if indices:
                null_vectors.append(indices)

    return null_vectors


# ─── IOF Factoring Engine ─────────────────────────────────────────

class IOFEngine:
    """Integer Orbit Factoring engine with smooth number sieve."""

    def __init__(self, n, B=None, verbose=True):
        self.n = n
        self.verbose = verbose

        if B is None:
            ln_n = math.log(n)
            self.B = max(10, int(math.exp(0.5 * math.sqrt(ln_n * math.log(max(ln_n, 2))))))
        else:
            self.B = B

        self.factor_base = sieve_of_eratosthenes(self.B)
        self.relations = []  # (a, exponents)
        self.log(f"IOF Engine initialized: n={n}, B={self.B}")
        self.log(f"Factor base size: {len(self.factor_base)} primes")
        self.log(f"Need ≥ {len(self.factor_base) + 1} smooth relations")

    def log(self, msg):
        if self.verbose:
            print(f"  [IOF] {msg}")

    def collect_orbit_relations(self, start, max_steps=100):
        """Collect smooth relations from a squaring orbit."""
        current = start % self.n
        found = 0
        for step in range(max_steps):
            residue = pow(current, 2, self.n)
            if residue > 0:
                smooth, exponents = trial_divide(residue, self.factor_base)
                if smooth:
                    self.relations.append((current, exponents, residue))
                    found += 1
                    self.log(f"  Smooth! a={current}, a²≡{residue} (mod {self.n}), "
                            f"factors={self._format_factors(exponents)}")
            current = pow(current, 2, self.n)
            if current <= 1:
                break
        return found

    def collect_random_relations(self, num_trials=1000):
        """Collect smooth relations from random values (for comparison)."""
        found = 0
        for _ in range(num_trials):
            a = random.randint(2, self.n - 1)
            residue = pow(a, 2, self.n)
            if residue > 0:
                smooth, exponents = trial_divide(residue, self.factor_base)
                if smooth:
                    self.relations.append((a, exponents, residue))
                    found += 1
        return found

    def find_congruence(self):
        """Use GF(2) linear algebra to find a congruence of squares."""
        if len(self.relations) <= len(self.factor_base):
            self.log(f"Not enough relations ({len(self.relations)} ≤ {len(self.factor_base)})")
            return None

        # Build GF(2) matrix
        matrix = [[e % 2 for e in rel[1]] for rel in self.relations]
        null_vectors = gaussian_elimination_gf2(matrix)

        if not null_vectors:
            self.log("No null vector found")
            return None

        self.log(f"Found {len(null_vectors)} null vector(s)")
        return null_vectors[0]

    def extract_factor(self, indices):
        """Extract a factor from a set of relation indices."""
        x = 1
        y_sq = 1
        for i in indices:
            a, exponents, residue = self.relations[i]
            x = (x * a) % self.n
            y_sq *= residue

        y = int(math.isqrt(y_sq))
        if y * y != y_sq:
            self.log(f"Warning: y² = {y_sq} is not a perfect square")
            return None

        g1 = math.gcd(x - y, self.n)
        g2 = math.gcd(x + y, self.n)

        for g in [g1, g2]:
            if 1 < g < self.n:
                return g

        return None

    def factor(self):
        """Run the full IOF factoring pipeline."""
        self.log("\n--- Phase 1: Orbit-based relation collection ---")

        for start in range(2, 102):
            self.collect_orbit_relations(start, max_steps=50)
            if len(self.relations) > len(self.factor_base) + 5:
                break

        if len(self.relations) <= len(self.factor_base):
            self.log("\n--- Phase 1b: Random relation collection (fallback) ---")
            self.collect_random_relations(5000)

        self.log(f"\nTotal relations collected: {len(self.relations)}")

        self.log("\n--- Phase 2: GF(2) linear algebra ---")
        indices = self.find_congruence()

        if indices is None:
            return None

        self.log(f"Using relation indices: {indices}")

        self.log("\n--- Phase 3: GCD extraction ---")
        factor = self.extract_factor(indices)

        if factor:
            self.log(f"\n✓ SUCCESS: {self.n} = {factor} × {self.n // factor}")
        else:
            self.log(f"\n✗ Trivial factor. Retrying...")
            # Try other null vectors
            matrix = [[e % 2 for e in rel[1]] for rel in self.relations]
            null_vectors = gaussian_elimination_gf2(matrix)
            for nv in null_vectors[1:]:
                factor = self.extract_factor(nv)
                if factor:
                    self.log(f"✓ SUCCESS: {self.n} = {factor} × {self.n // factor}")
                    return factor

        return factor

    def _format_factors(self, exponents):
        parts = []
        for i, e in enumerate(exponents):
            if e > 0:
                p = self.factor_base[i]
                parts.append(f"{p}^{e}" if e > 1 else str(p))
        return " · ".join(parts) if parts else "1"


# ─── Demo Functions ───────────────────────────────────────────────

def demo_dickman():
    """Show the Dickman function and smooth number probabilities."""
    print("\n" + "=" * 60)
    print("DEMO 1: Dickman Function ρ(u) — Smooth Number Probability")
    print("=" * 60)

    print(f"\nρ(u) ≈ probability that a random integer is x^(1/u)-smooth")
    print(f"\n{'u':>5} {'ρ(u)':>12} {'1/ρ(u)':>12} {'Meaning':>40}")
    print(f"{'─'*5} {'─'*12} {'─'*12} {'─'*40}")

    for u_10 in [10, 15, 20, 30, 50, 80, 100, 150, 200]:
        u = u_10 / 10
        rho = dickman_rho(u)
        inv_rho = 1/rho if rho > 0 else float('inf')
        meaning = f"1 in {inv_rho:.0f} numbers is x^(1/{u:.1f})-smooth"
        print(f"{u:>5.1f} {rho:>12.6f} {inv_rho:>12.1f} {meaning:>40}")


def demo_optimal_B():
    """Show optimal B selection for different key sizes."""
    print("\n" + "=" * 60)
    print("DEMO 2: Optimal Smoothness Bound B for IOF")
    print("=" * 60)

    print(f"\nFor n of b bits, optimal B ≈ L_n[1/2, 1/(2√2)]")
    print(f"\n{'Bits':>6} {'log₂(B)':>10} {'π(B)':>10} {'u':>8} {'log₂(1/ρ)':>12} {'log₂(Total)':>12}")
    print(f"{'─'*6} {'─'*10} {'─'*10} {'─'*8} {'─'*12} {'─'*12}")

    for bits in [64, 128, 256, 512, 1024, 2048]:
        ln_n = bits * math.log(2)
        ln_ln_n = math.log(ln_n)

        # Optimal B = L[1/2, 1/(2√2)]
        log_B = math.sqrt(ln_n * ln_ln_n) / (2 * math.sqrt(2))
        B = math.exp(log_B)
        pi_B = B / log_B  # Prime counting function estimate

        u = ln_n / log_B
        rho_u = dickman_rho(round(u))
        log2_inv_rho = -math.log2(rho_u) if rho_u > 0 else float('inf')

        total_log2 = math.log2(pi_B / rho_u) if rho_u > 0 else float('inf')

        print(f"{bits:>6} {log_B/math.log(2):>10.1f} {math.log2(pi_B):>10.1f} "
              f"{u:>8.1f} {log2_inv_rho:>12.1f} {total_log2:>12.1f}")


def demo_full_factoring():
    """Run the full IOF factoring pipeline on test numbers."""
    print("\n" + "=" * 60)
    print("DEMO 3: Full IOF Factoring Pipeline")
    print("=" * 60)

    test_numbers = [
        (143, "11 × 13"),
        (377, "13 × 29"),
        (1073, "29 × 37"),
        (10403, "101 × 103"),
        (25117, "131 × 191"),
    ]

    for n, expected in test_numbers:
        print(f"\n{'━' * 50}")
        print(f"Factoring n = {n} (expected: {expected})")
        print(f"{'━' * 50}")

        engine = IOFEngine(n, verbose=True)
        result = engine.factor()

        if result is None:
            print(f"  Retrying with larger B...")
            engine = IOFEngine(n, B=50, verbose=False)
            result = engine.factor()
            if result:
                print(f"  ✓ Found: {n} = {result} × {n // result}")
            else:
                print(f"  ✗ Failed to factor {n}")


def demo_orbit_vs_random():
    """Compare IOF orbit-based search vs. random search for smooth numbers."""
    print("\n" + "=" * 60)
    print("DEMO 4: IOF Orbit Search vs. Random Search")
    print("=" * 60)

    n = 10403  # 101 × 103
    B = 30
    factor_base = sieve_of_eratosthenes(B)

    print(f"\nn = {n}, B = {B}, |factor base| = {len(factor_base)}")

    # Orbit-based search
    orbit_smooth = 0
    orbit_total = 0
    for start in range(2, 52):
        current = start
        for step in range(50):
            residue = pow(current, 2, n)
            orbit_total += 1
            if residue > 0:
                smooth, _ = trial_divide(residue, factor_base)
                if smooth:
                    orbit_smooth += 1
            current = pow(current, 2, n)
            if current <= 1:
                break

    # Random search
    random_smooth = 0
    random_total = orbit_total
    random.seed(42)
    for _ in range(random_total):
        a = random.randint(2, n - 1)
        residue = pow(a, 2, n)
        if residue > 0:
            smooth, _ = trial_divide(residue, factor_base)
            if smooth:
                random_smooth += 1

    print(f"\n{'Method':<20} {'Trials':>10} {'Smooth Found':>15} {'Rate':>10}")
    print(f"{'─'*20} {'─'*10} {'─'*15} {'─'*10}")
    print(f"{'IOF Orbit':<20} {orbit_total:>10} {orbit_smooth:>15} "
          f"{orbit_smooth/max(orbit_total,1)*100:>9.2f}%")
    print(f"{'Random':<20} {random_total:>10} {random_smooth:>15} "
          f"{random_smooth/max(random_total,1)*100:>9.2f}%")
    print(f"\nTheoretical ρ({math.log(n)/math.log(B):.1f}) ≈ "
          f"{dickman_rho(round(math.log(n)/math.log(B))):.6f} = "
          f"{dickman_rho(round(math.log(n)/math.log(B)))*100:.4f}%")


if __name__ == "__main__":
    print("╔" + "═" * 58 + "╗")
    print("║  IOF Smooth Number Sieve — Advanced Demo                ║")
    print("║  Dickman function, optimal parameters, and GF(2) LA     ║")
    print("╚" + "═" * 58 + "╝")

    demo_dickman()
    demo_optimal_B()
    demo_full_factoring()
    demo_orbit_vs_random()

    print("\n" + "=" * 60)
    print("All demos completed!")
    print("=" * 60)
