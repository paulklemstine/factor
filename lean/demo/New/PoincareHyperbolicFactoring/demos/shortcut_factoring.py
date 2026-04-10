"""
Shortcut Factoring Algorithm: A Practical Factoring Method via Pythagorean Triples

This implements the hyperbolic shortcut factoring algorithm, which uses the
Berggren tree structure and Pythagorean triple identities to factor integers.

The core identity: if a² + b² = c², then (c-b)(c+b) = a²
Finding the right Pythagorean triple for a given N reveals its factors.
"""

from math import gcd, isqrt, log2
import time
from typing import Optional


def is_prime(n: int) -> bool:
    """Simple primality test."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def pythagorean_triple_factor(N: int) -> Optional[int]:
    """
    Factor N using the Pythagorean triple identity.
    
    For each divisor d of N² with d < N and d ≡ N²/d (mod 2):
      - b = (N²/d - d) / 2
      - c = (N²/d + d) / 2
      - Then N² + b² = c² (Pythagorean triple with leg N)
      - Factor candidate: gcd(d, N)
    
    Returns a non-trivial factor of N, or None.
    """
    if N <= 1:
        return None
    if N % 2 == 0:
        return 2
    
    N_sq = N * N
    
    # Iterate over divisors of N²
    for d in range(1, isqrt(N_sq) + 1):
        if N_sq % d == 0:
            e = N_sq // d
            if d >= e:
                continue
            if d % 2 != e % 2:
                continue
            
            # Construct the triple
            b = (e - d) // 2
            c = (e + d) // 2
            
            # Extract factor via GCD
            g = gcd(d, N)
            if 1 < g < N:
                return g
    
    return None


def berggren_descent_factor(N: int) -> Optional[int]:
    """
    Factor N using Berggren tree parent descent.
    
    1. Construct a Pythagorean triple with hypotenuse or leg related to N
    2. Descend to the root of the Berggren tree
    3. At each step, check if gcd(current leg, N) reveals a factor
    
    Returns a non-trivial factor of N, or None.
    """
    if N <= 1:
        return None
    if N % 2 == 0:
        return 2
    
    # Try each divisor pair to construct triples with legs related to N
    N_sq = N * N
    
    for d in range(1, min(N, isqrt(N_sq) + 1)):
        if N_sq % d != 0:
            continue
        e = N_sq // d
        if d >= e or d % 2 != e % 2:
            continue
        
        b = (e - d) // 2
        c = (e + d) // 2
        a = N
        
        if a * a + b * b != c * c:
            continue
        
        # Now descend the Berggren tree from (a, b, c)
        # At each step, check GCD with N
        steps = 0
        max_steps = int(log2(c + 1)) + 10
        
        while steps < max_steps:
            for leg in [a, b]:
                g = gcd(abs(leg), N)
                if 1 < g < N:
                    return g
            
            # Determine parent direction
            # Parent has smaller hypotenuse
            if a <= 0 and b <= 0:
                break
            
            # Apply inverse matrices and find valid parent
            found_parent = False
            for inv_name, transform in [
                ("B1_inv", lambda a,b,c: (a + 2*b - 2*c, -2*a - b + 2*c, -2*a - 2*b + 3*c)),
                ("B2_inv", lambda a,b,c: (a - 2*b - 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c)),
                ("B3_inv", lambda a,b,c: (-a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c)),
            ]:
                na, nb, nc = transform(a, b, c)
                if na > 0 and nb > 0 and nc > 0 and na*na + nb*nb == nc*nc and nc < c:
                    a, b, c = na, nb, nc
                    found_parent = True
                    break
            
            if not found_parent:
                break
            
            steps += 1
    
    return None


def combined_factor(N: int) -> Optional[int]:
    """
    Combined factoring using both the direct Pythagorean method and
    Berggren descent.
    """
    # Quick check
    if N <= 1:
        return None
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if N % p == 0 and N > p:
            return p
    
    # Try Pythagorean triple method
    result = pythagorean_triple_factor(N)
    if result:
        return result
    
    # Try Berggren descent
    result = berggren_descent_factor(N)
    if result:
        return result
    
    return None


def full_factorization(N: int) -> list:
    """Fully factor N into primes."""
    if N <= 1:
        return []
    
    factors = []
    remaining = N
    
    while remaining > 1:
        if is_prime(remaining):
            factors.append(remaining)
            break
        
        factor = combined_factor(remaining)
        if factor is None:
            factors.append(remaining)  # give up
            break
        
        while remaining % factor == 0:
            factors.append(factor)
            remaining //= factor
    
    return sorted(factors)


# ============================================================================
# Demo and Benchmarking
# ============================================================================

def demo():
    """Run factoring demos."""
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  SHORTCUT FACTORING ALGORITHM                           ║")
    print("║  Factoring via Pythagorean Triples & Berggren Tree      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    # Demo 1: Basic factoring
    print("\n1. BASIC FACTORING DEMO")
    print("-" * 50)
    print(f"{'N':<12} {'Factors':<20} {'Time (μs)':<12} {'Verified'}")
    print("-" * 50)
    
    test_numbers = [
        15, 21, 35, 77, 91, 143, 221, 323, 437, 667, 899,
        1001, 1147, 2021, 3599, 5767, 10001, 10403,
        100003, 999983 * 2,  # larger examples
    ]
    
    for N in test_numbers:
        start = time.perf_counter_ns()
        factors = full_factorization(N)
        elapsed_us = (time.perf_counter_ns() - start) / 1000
        
        product = 1
        for f in factors:
            product *= f
        verified = "✓" if product == N else "✗"
        
        factors_str = " × ".join(str(f) for f in factors)
        print(f"{N:<12} {factors_str:<20} {elapsed_us:<12.1f} {verified}")
    
    # Demo 2: The factoring identity
    print("\n2. FACTORING IDENTITY: (c-b)(c+b) = a²")
    print("-" * 50)
    
    triples = [
        (3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25),
        (20, 21, 29), (9, 40, 41), (12, 35, 37), (11, 60, 61),
        (28, 45, 53), (33, 56, 65),
    ]
    
    print(f"{'Triple':<18} {'(c-b)(c+b)':<14} {'a²':<10} {'Match'}")
    print("-" * 50)
    
    for a, b, c in triples:
        lhs = (c - b) * (c + b)
        rhs = a * a
        match = "✓" if lhs == rhs else "✗"
        print(f"({a}, {b}, {c}){'':<{max(0, 12-len(f'({a}, {b}, {c})'))}} "
              f"{lhs:<14} {rhs:<10} {match}")
    
    # Demo 3: Divisor pairs and triple construction
    print("\n3. DIVISOR PAIRS → PYTHAGOREAN TRIPLES → FACTORS")
    print("-" * 65)
    
    for N in [15, 21, 35, 77, 143]:
        N_sq = N * N
        print(f"\nN = {N}, N² = {N_sq}")
        print(f"  {'d':<6} {'e=N²/d':<8} {'b=(e-d)/2':<12} {'c=(e+d)/2':<12} "
              f"{'gcd(d,N)':<10} {'Factor?'}")
        
        for d in range(1, isqrt(N_sq) + 1):
            if N_sq % d == 0:
                e = N_sq // d
                if d < e and d % 2 == e % 2:
                    b = (e - d) // 2
                    c = (e + d) // 2
                    g = gcd(d, N)
                    factor_str = f"→ {g}" if 1 < g < N else ""
                    print(f"  {d:<6} {e:<8} {b:<12} {c:<12} {g:<10} {factor_str}")


if __name__ == "__main__":
    demo()
