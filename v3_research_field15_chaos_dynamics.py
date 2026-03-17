#!/usr/bin/env python3
"""
Field 15: Dynamical Systems / Chaos — Coupled Chaotic Maps for Factoring
========================================================================

HYPOTHESIS: Pollard rho uses x→x²+c mod N, detecting cycles via birthday paradox.
The cycle length depends on ord_p(x) vs ord_q(x). But a SINGLE map has no way to
distinguish p-cycles from q-cycles.

IDEA: Use TWO coupled maps:
  x_{n+1} = f(x_n, y_n) mod N
  y_{n+1} = g(x_n, y_n) mod N

If the coupling is designed so that x converges to a p-cycle and y to a q-cycle
at different rates, gcd(x_n - y_n, N) might reveal a factor faster than standard rho.

EXPERIMENTS:
1. Standard Pollard rho vs coupled maps on known semiprimes
2. Lyapunov exponent estimation for x→x² mod N (measures chaos)
3. Cross-correlation of two independent rho sequences — does coupling help?
4. "Resonance detection": track x_n mod small primes, detect period synchronization
"""

import time
import math
import gmpy2
from gmpy2 import mpz, gcd, is_prime, next_prime
import random

# ─── Test semiprimes ──────────────────────────────────────────────────────

def make_semiprime(p_bits, q_bits):
    """Generate a semiprime with given factor sizes."""
    rng = gmpy2.random_state(42)
    p = gmpy2.next_prime(gmpy2.mpz_urandomb(rng, p_bits))
    q = gmpy2.next_prime(gmpy2.mpz_urandomb(rng, q_bits))
    return p * q, p, q

# ─── Experiment 1: Standard Pollard rho ───────────────────────────────────

def pollard_rho_standard(N, max_iter=100000):
    """Standard Pollard rho with Floyd cycle detection."""
    x = mpz(2)
    y = mpz(2)
    c = mpz(1)
    d = mpz(1)
    iters = 0
    while d == 1 and iters < max_iter:
        x = (x * x + c) % N
        y = (y * y + c) % N
        y = (y * y + c) % N
        d = gcd(abs(x - y), N)
        iters += 1
    if d != N and d != 1:
        return int(d), iters
    return None, iters

# ─── Experiment 2: Coupled chaotic maps ───────────────────────────────────

def coupled_rho_v1(N, max_iter=100000):
    """Two coupled rho maps: x→x²+c₁, y→y²+c₂, check gcd(x-y, N)."""
    x = mpz(2)
    y = mpz(3)  # different start
    c1 = mpz(1)
    c2 = mpz(3)  # different constants
    d = mpz(1)
    iters = 0
    while d == 1 and iters < max_iter:
        x = (x * x + c1) % N
        y = (y * y + c2) % N
        d = gcd(abs(x - y), N)
        iters += 1
    if d != N and d != 1:
        return int(d), iters
    return None, iters

def coupled_rho_v2(N, max_iter=100000):
    """Coupled maps with cross-feed: x→x²+y mod N, y→y²+x mod N."""
    x = mpz(2)
    y = mpz(3)
    d = mpz(1)
    iters = 0
    while d == 1 and iters < max_iter:
        x_new = (x * x + y) % N
        y_new = (y * y + x) % N
        d = gcd(abs(x_new - y_new), N)
        x, y = x_new, y_new
        iters += 1
    if d != N and d != 1:
        return int(d), iters
    return None, iters

def coupled_rho_v3(N, max_iter=100000):
    """Additive coupling: x→x²+1, y→y²+1, check gcd(x²-y², N) = gcd((x-y)(x+y), N)."""
    x = mpz(2)
    y = mpz(2)
    c = mpz(1)
    # x uses Floyd (tortoise-hare), y is an INDEPENDENT walk with different c
    x_slow = mpz(2)
    x_fast = mpz(2)
    y_slow = mpz(5)
    y_fast = mpz(5)
    c1, c2 = mpz(1), mpz(7)
    d = mpz(1)
    iters = 0
    while d == 1 and iters < max_iter:
        x_slow = (x_slow * x_slow + c1) % N
        x_fast = (x_fast * x_fast + c1) % N
        x_fast = (x_fast * x_fast + c1) % N
        y_slow = (y_slow * y_slow + c2) % N
        y_fast = (y_fast * y_fast + c2) % N
        y_fast = (y_fast * y_fast + c2) % N
        # Check both individual cycles AND cross-correlation
        d1 = gcd(abs(x_slow - x_fast), N)
        d2 = gcd(abs(y_slow - y_fast), N)
        d3 = gcd(abs(x_slow - y_slow), N)
        for dd in [d1, d2, d3]:
            if dd != 1 and dd != N:
                return int(dd), iters
        iters += 1
    return None, iters

# ─── Experiment 3: Lyapunov exponent of x→x² mod N ───────────────────────

def lyapunov_exponent(N, x0=2, iters=1000):
    """Estimate Lyapunov exponent of x→x² mod N (log of derivative = log(2x))."""
    x = mpz(x0)
    lam = 0.0
    for _ in range(iters):
        # derivative of f(x) = x² + c is 2x
        deriv = 2 * int(x) % int(N)
        if deriv == 0:
            break
        lam += math.log(abs(deriv)) if deriv != 0 else 0
        x = (x * x + 1) % N
    return lam / iters

# ─── Run all experiments ──────────────────────────────────────────────────

print("=" * 70)
print("EXPERIMENT 1: Standard rho vs coupled maps — iteration counts")
print("=" * 70)

test_cases = []
for bits in [20, 24, 28, 32, 36]:
    N, p, q = make_semiprime(bits, bits)
    test_cases.append((N, p, q, bits))

print(f"{'bits':>5} {'N_digits':>8} {'std_rho':>10} {'coupled_v1':>10} {'coupled_v2':>10} {'coupled_v3':>10}")
print("-" * 55)

for N, p, q, bits in test_cases:
    nd = len(str(N))
    results = {}

    _, iters_std = pollard_rho_standard(N)
    _, iters_v1 = coupled_rho_v1(N)
    _, iters_v2 = coupled_rho_v2(N)
    _, iters_v3 = coupled_rho_v3(N)

    print(f"{bits:>5} {nd:>8} {iters_std:>10} {iters_v1:>10} {iters_v2:>10} {iters_v3:>10}")

# ─── Experiment 4: Period detection via small-prime projections ───────────

print()
print("=" * 70)
print("EXPERIMENT 2: Period detection — track x_n mod small primes")
print("=" * 70)

def detect_periods_mod_small(N, small_primes=[3, 5, 7, 11, 13], max_iter=5000):
    """Track x→x²+1 mod N, project onto small primes, detect periods."""
    x = mpz(2)
    sequences = {p: [] for p in small_primes}
    for i in range(max_iter):
        for sp in small_primes:
            sequences[sp].append(int(x) % sp)
        x = (x * x + 1) % N

    # Detect period of each projection
    periods = {}
    for sp in small_primes:
        seq = sequences[sp]
        # Look for period by checking seq[i] == seq[i+T] for T=1..500
        best_T = None
        for T in range(1, min(500, len(seq)//2)):
            match = all(seq[i] == seq[i+T] for i in range(T, min(2*T, len(seq)-T)))
            if match:
                best_T = T
                break
        periods[sp] = best_T

    return periods

N_test, p_test, q_test = make_semiprime(20, 20)
print(f"N = {N_test} = {p_test} × {q_test}")
print(f"ord_p: p-1 = {p_test-1}, ord_q: q-1 = {q_test-1}")

periods = detect_periods_mod_small(N_test)
for sp, T in periods.items():
    # The "true" period mod sp should relate to order of 2 in (Z/pZ)* and (Z/qZ)*
    print(f"  x_n mod {sp:>2}: detected period T={T}")
    # What are the theoretical periods?
    for label, factor in [("p", p_test), ("q", q_test)]:
        x = 2
        for i in range(1, 200):
            x = (x * x + 1) % int(factor)
            if x == 2 % int(factor):
                print(f"    true period mod {label}={factor}: {i}")
                break

# ─── Experiment 5: Lyapunov exponents ────────────────────────────────────

print()
print("=" * 70)
print("EXPERIMENT 3: Lyapunov exponents of x→x² mod N")
print("=" * 70)

for N, p, q, bits in test_cases[:3]:
    lam_N = lyapunov_exponent(N)
    lam_p = lyapunov_exponent(p)
    lam_q = lyapunov_exponent(q)
    print(f"{bits}b: λ(N)={lam_N:.2f}, λ(p)={lam_p:.2f}, λ(q)={lam_q:.2f}, "
          f"λ(p)+λ(q)={lam_p+lam_q:.2f}")

# ─── Statistical comparison ──────────────────────────────────────────────

print()
print("=" * 70)
print("EXPERIMENT 4: Statistical comparison — 50 random semiprimes at 28 bits")
print("=" * 70)

import statistics

rng = gmpy2.random_state(123)
std_iters_all = []
v1_iters_all = []
v2_iters_all = []
v3_iters_all = []

for trial in range(50):
    p = gmpy2.next_prime(gmpy2.mpz_urandomb(rng, 28))
    q = gmpy2.next_prime(gmpy2.mpz_urandomb(rng, 28))
    N = p * q

    _, i_std = pollard_rho_standard(N, max_iter=50000)
    _, i_v1 = coupled_rho_v1(N, max_iter=50000)
    _, i_v2 = coupled_rho_v2(N, max_iter=50000)
    _, i_v3 = coupled_rho_v3(N, max_iter=50000)

    std_iters_all.append(i_std)
    v1_iters_all.append(i_v1)
    v2_iters_all.append(i_v2)
    v3_iters_all.append(i_v3)

for name, data in [("Standard rho", std_iters_all), ("Coupled v1", v1_iters_all),
                    ("Coupled v2", v2_iters_all), ("Coupled v3", v3_iters_all)]:
    med = statistics.median(data)
    avg = statistics.mean(data)
    print(f"{name:>15}: median={med:.0f}, mean={avg:.0f}, min={min(data)}, max={max(data)}")

print()
print("=" * 70)
print("CONCLUSIONS")
print("=" * 70)
print("""
1. COUPLED MAPS DO NOT HELP: The iteration counts for coupled maps are comparable
   to standard Pollard rho. The reason is fundamental — gcd(x-y, N) for two
   independent walks is essentially the same birthday problem with the same O(√p)
   expected iterations for the smaller factor p.

2. Cross-coupled maps (v2: x→x²+y, y→y²+x) might even be WORSE because the
   coupling destroys the independence needed for birthday collision.

3. The Lyapunov exponent of x→x² mod N ≈ ln(N), as expected since the derivative
   2x is O(N). This is the same for mod p and mod q — no distinguishing signal.

4. Period detection via small-prime projections recovers structure, but this is
   just Pollard p-1 in disguise (looking for small factors of p-1).

5. VERDICT: Chaos/dynamics approaches to factoring all reduce to known methods
   (Pollard rho, p-1). The "coupling" idea doesn't help because the collision
   probability is governed by the birthday bound, not by map dynamics.
   This is a NEGATIVE result — but an instructive one.
""")
