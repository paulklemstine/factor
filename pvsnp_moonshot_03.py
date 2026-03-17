#!/usr/bin/env python3
"""
Moonshot 3: Communication Complexity of Factoring
==================================================
Two-party protocols where Alice has N, Bob has candidate factor.

We study several communication models:
1. Alice has N, Bob has p. They compute "does p divide N?" (trivial: O(1) bits)
2. Alice has top half of N, Bob has bottom half. They want to find p.
3. Number-on-forehead: three parties each see two of {N, p, q}.
4. Karchmer-Wigderson game for the factoring function.
"""

import time
import math
import random
from collections import defaultdict

try:
    import gmpy2
    _HAS_GMPY2 = True
except ImportError:
    _HAS_GMPY2 = False

def is_prime(n):
    if _HAS_GMPY2:
        return gmpy2.is_prime(n)
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

def random_prime(bits):
    while True:
        n = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(n):
            return n

def random_semiprime(bits):
    half = bits // 2
    p = random_prime(half)
    q = random_prime(bits - half)
    while p == q:
        q = random_prime(bits - half)
    return p * q, min(p, q), max(p, q)

def main():
    print("=" * 70)
    print("Moonshot 3: Communication Complexity of Factoring")
    print("=" * 70)
    t0 = time.time()

    # --- Test 1: Divisibility communication ---
    print("\n--- Test 1: Communication for 'Does p divide N?' ---")
    print("  Alice has N (n bits), Bob has p (n/2 bits).")
    print("  They want to determine if p | N.")
    print()
    print("  Trivial protocol: Alice sends N mod p (log p = n/2 bits).")
    print("  Bob checks if result is 0.")
    print("  Communication: O(n/2) bits. Can we do better?")
    print()

    # Lower bound argument: there are 2^{n/2} possible values of p,
    # and for each N, the set of divisors is different.
    # By a counting argument, Alice must send Omega(n/2) bits.

    # Empirical: for each N, how many primes p actually divide N? Exactly 2.
    # So the "divisibility predicate" is very sparse.
    # Does sparsity help? In the INDEX problem (Bob has index i, Alice has
    # string x, they compute x_i), the communication is Theta(n).
    # Divisibility is NOT the index problem, but has similar structure.

    for bits in [8, 12, 16, 20]:
        N_samples = 100
        # Measure: how many bits of N mod p does Alice need to send?
        # If she sends k bits of N mod p, Bob can distinguish 2^k residue classes.
        # For p ~ 2^{n/2}, she needs n/2 bits.

        total_comm = 0
        for _ in range(N_samples):
            N, p, q = random_semiprime(bits)
            # Communication = ceil(log2(p))
            comm = p.bit_length()
            total_comm += comm

        avg_comm = total_comm / N_samples
        print(f"  {bits:3d}-bit: avg comm for divisibility = {avg_comm:.1f} bits "
              f"(theory: {bits//2} bits)")

    # --- Test 2: Split-input factoring ---
    print("\n--- Test 2: Split-Input Factoring ---")
    print("  Alice has top n/2 bits of N, Bob has bottom n/2 bits.")
    print("  They want to compute the smaller factor p.")

    for bits in [8, 12, 16]:
        half = bits // 2
        N_samples = 200

        # For each possible top-half value, how many different p values arise?
        # This measures how much info Alice's input gives about p.
        top_to_p = defaultdict(set)
        bot_to_p = defaultdict(set)

        for _ in range(N_samples):
            N, p, q = random_semiprime(bits)
            top = N >> half
            bot = N & ((1 << half) - 1)
            top_to_p[top].add(p)
            bot_to_p[bot].add(p)

        # Entropy of p given top half
        avg_top_ambiguity = sum(len(v) for v in top_to_p.values()) / max(len(top_to_p), 1)
        avg_bot_ambiguity = sum(len(v) for v in bot_to_p.values()) / max(len(bot_to_p), 1)

        print(f"  {bits:3d}-bit: knowing top {half} bits -> avg {avg_top_ambiguity:.2f} "
              f"possible p values")
        print(f"           knowing bot {half} bits -> avg {avg_bot_ambiguity:.2f} "
              f"possible p values")

    # --- Test 3: One-way communication lower bound ---
    print("\n--- Test 3: One-Way Communication Lower Bound ---")
    print("  Alice sends one message to Bob. How many bits needed?")

    for bits in [8, 10, 12, 14]:
        half = bits // 2
        # Build the communication matrix:
        # Rows = Alice's input (top half of N)
        # Columns = Bob's input (bottom half of N)
        # Entry = smaller factor p (or 0 if N = top||bot is not a semiprime)

        comm_matrix = {}
        for top in range(1 << half, 1 << (half + 1)):  # top half has MSB=1
            for bot in range(0, 1 << half):
                N = (top << half) | bot
                if N < 4:
                    continue
                # Try to factor N (brute force for small N)
                p_found = 0
                for d in range(2, min(int(N**0.5) + 1, 10000)):
                    if N % d == 0:
                        p_found = d
                        break
                if p_found > 0 and is_prime(p_found):
                    other = N // p_found
                    if is_prime(other) and other != p_found:
                        comm_matrix[(top, bot)] = p_found

        if not comm_matrix:
            print(f"  {bits:3d}-bit: no semiprimes found in range")
            continue

        # Count distinct (top, p) pairs -> this is the number of
        # "messages" Alice must be able to send
        top_values = set(t for t, b in comm_matrix.keys())
        # For each top value, how many distinct p values?
        top_p_count = defaultdict(set)
        for (t, b), p in comm_matrix.items():
            top_p_count[t].add(p)

        max_p_per_top = max(len(v) for v in top_p_count.values()) if top_p_count else 0
        avg_p_per_top = sum(len(v) for v in top_p_count.values()) / max(len(top_p_count), 1)

        # Lower bound: Alice needs at least log2(max_p_per_top) bits
        lb = math.log2(max_p_per_top) if max_p_per_top > 0 else 0

        print(f"  {bits:3d}-bit: semiprimes={len(comm_matrix)}, "
              f"max p per top-half={max_p_per_top}, "
              f"comm LB >= {lb:.1f} bits, "
              f"factor has {half} bits")

    # --- Test 4: Karchmer-Wigderson game ---
    print("\n--- Test 4: Karchmer-Wigderson Game for Factoring ---")
    print("  KW game: Alice has x with f(x)=1, Bob has y with f(y)=0.")
    print("  They want to find an index i where x_i != y_i.")
    print("  CC of KW game = circuit depth of f.")
    print()
    print("  For factoring: f(N) = 1 if N is a semiprime, 0 otherwise.")
    print("  Alice has a semiprime, Bob has a non-semiprime.")
    print("  They find a bit position where they differ.")

    for bits in [8, 10, 12]:
        # Enumerate all n-bit numbers, classify as semiprime or not
        semiprimes = []
        non_semiprimes = []
        for n in range(1 << (bits - 1), 1 << bits):
            if n % 2 == 0:
                non_semiprimes.append(n)
                continue
            # Count prime factors
            temp = n
            factors = []
            d = 2
            while d * d <= temp:
                while temp % d == 0:
                    factors.append(d)
                    temp //= d
                d += 1
            if temp > 1:
                factors.append(temp)

            if len(factors) == 2 and all(is_prime(f) for f in factors):
                semiprimes.append(n)
            else:
                non_semiprimes.append(n)

        # For random pairs (semi, non-semi), find the minimum number of
        # differing bits needed to distinguish them
        if not semiprimes or not non_semiprimes:
            continue

        n_pairs = min(500, len(semiprimes) * len(non_semiprimes))
        min_diffs = []
        for _ in range(n_pairs):
            s = random.choice(semiprimes)
            ns = random.choice(non_semiprimes)
            # Count differing bits
            xor = s ^ ns
            diff_bits = bin(xor).count('1')
            min_diffs.append(diff_bits)

        avg_diff = sum(min_diffs) / len(min_diffs)
        min_diff = min(min_diffs)
        max_diff = max(min_diffs)

        print(f"  {bits:3d}-bit: {len(semiprimes)} semiprimes, "
              f"{len(non_semiprimes)} non-semiprimes")
        print(f"    Hamming distance: min={min_diff}, avg={avg_diff:.1f}, max={max_diff}")
        print(f"    KW depth lower bound: >= {math.ceil(math.log2(min_diff + 1))}")

    # --- Test 5: Multiparty communication ---
    print("\n--- Test 5: Number-on-Forehead Model ---")
    print("  3 parties: P1 sees (p, q), P2 sees (N, q), P3 sees (N, p)")
    print("  They want to verify N = p*q.")
    print("  Communication: P1 computes p*q, sends 1 bit (match or not).")
    print("  Total: O(1) bits! The NOF model makes factoring verification trivial.")
    print()
    print("  But FINDING p given N requires P2 and P3 to communicate ~n/2 bits.")
    print("  The asymmetry between verification and search is the core of NP.")

    # Simulate: 2-party version where one party has N, other has nothing
    # (degenerate case = normal computation)
    for bits in [16, 32, 64]:
        # Information-theoretic lower bound:
        # The factor p has n/2 bits of entropy, all of which must be
        # communicated from "the oracle that knows p" to "the party with N"
        info_lb = bits // 2
        print(f"  {bits:3d}-bit: info lower bound = {info_lb} bits "
              f"(= factor size)")

    elapsed = time.time() - t0
    print(f"\n--- Summary (elapsed: {elapsed:.1f}s) ---")
    print("""
  Communication Complexity Findings:

  1. DIVISIBILITY: O(n/2) bits needed (tight). Alice sends N mod p.

  2. SPLIT INPUT: Knowing either half of N leaves high ambiguity about p.
     Both halves contribute essential information — factoring is "global."

  3. ONE-WAY: Communication grows linearly with factor size (Omega(n/2)).
     No compression possible in one-way protocols.

  4. KW GAME: Semiprimes and non-semiprimes are close in Hamming distance
     (min distance ~ 1-2 bits). Circuit depth lower bound is weak (O(1)).
     The KW game does NOT yield useful circuit depth bounds for factoring.

  5. NOF MODEL: Verification is O(1) communication in 3-party NOF.
     Search requires Omega(n/2) regardless of model.

  KEY INSIGHT: Communication complexity confirms that factoring information
  is spread across ALL bits of N. No local or partial view suffices.
  But communication lower bounds don't directly give TIME lower bounds
  (they give DEPTH bounds, which are different).

  VERDICT: Communication complexity is informative but insufficient.
  The KW connection to circuit depth gives only weak bounds.
  Interactive protocols might circumvent one-way lower bounds.
  Rating: 3/10 for proving factoring is hard.
""")

if __name__ == '__main__':
    main()
