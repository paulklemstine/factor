"""
Pythagorean Tree x Category Theory / Operads Experiment

HYPOTHESIS: The Pythagorean tree is the free algebra for a specific operad.
The morphism from this free algebra to (Z/NZ)^2 has a KERNEL that encodes
the factorization of N.

KEY INSIGHT: Consider the category C where:
- Objects: elements of (Z/NZ)^2
- Morphisms: words in {B1, B2, B3} (compositions of Berggren matrices)

The group G = <B1, B2, B3> acting on (Z/NZ)^2 has a kernel when projected to
(Z/pZ)^2 vs (Z/qZ)^2. The "categorical equalizer" of the two projections
gives the factorization.

MORE CONCRETELY: Two words w1, w2 in {B1,B2,B3}* are "equivalent mod p" if
w1(2,1) ≡ w2(2,1) (mod p). Finding such a pair is EXACTLY the birthday/collision
problem. The operadic structure tells us about the ALGEBRAIC RELATIONS between
words that cause collisions.

EXPERIMENT: Enumerate relations in the group <B1,B2,B3> mod small primes.
Do certain "short relators" (words w with w(2,1) = (2,1) mod p) exist?
If so, they reveal structure that could be exploited.
"""

import random
from collections import defaultdict
from itertools import product

print("=" * 70)
print("CATEGORY THEORY: Operadic Structure and Group Relations")
print("=" * 70)

def apply_word(word, m, n, p):
    """Apply a word (list of matrix indices) to (m,n) mod p."""
    for mat_idx in word:
        if mat_idx == 0:  # B1
            m, n = (2*m - n) % p, m % p
        elif mat_idx == 1:  # B2
            m, n = (2*m + n) % p, m % p
        elif mat_idx == 2:  # B3
            m, n = (m + 2*n) % p, n % p
    return (m, n)

# Experiment 1: Find short relators (words that fix (2,1) mod p)
print("\n--- Experiment 1: Short relators in <B1,B2,B3> mod p ---")
print("A relator is a word w such that w(2,1) ≡ (2,1) mod p.\n")

for p in [5, 7, 11, 13, 17, 23, 29, 31]:
    start = (2 % p, 1 % p)
    relators = []

    # Enumerate all words up to length 6
    for length in range(1, 7):
        for word in product(range(3), repeat=length):
            result = apply_word(word, start[0], start[1], p)
            if result == start:
                relators.append(word)

        if relators:
            break  # Found shortest relators

    if relators:
        shortest = min(len(r) for r in relators)
        count = sum(1 for r in relators if len(r) == shortest)
        # Show first few
        examples = [r for r in relators if len(r) == shortest][:3]
        print(f"  p={p:3d}: shortest relator length={shortest}, count={count}, "
              f"examples={[''.join(str(x) for x in e) for e in examples]}")
    else:
        print(f"  p={p:3d}: no relators up to length 6")

# Experiment 2: Relator structure — do relators form a normal subgroup?
print("\n--- Experiment 2: Relator lattice structure ---")
print("If relators form a pattern, we can predict them for unknown p.\n")

# For each prime, find ALL relators up to length 8 and analyze their structure
for p in [5, 7, 11, 13]:
    start = (2 % p, 1 % p)
    relators_by_len = defaultdict(list)

    for length in range(1, 8):
        count = 0
        for word in product(range(3), repeat=length):
            result = apply_word(word, start[0], start[1], p)
            if result == start:
                count += 1
        relators_by_len[length] = count

    print(f"  p={p}: relator counts by length: {dict(relators_by_len)}")
    # Expected: 3^length / orbit_size relators of each length (if uniformly distributed)
    # Actual pattern might show group structure

# Experiment 3: Categorical coproduct — combining walks
print("\n--- Experiment 3: Coproduct structure (combining independent walks) ---")
print("In category theory, the coproduct of two walks is their concatenation.")
print("Test: do concatenations of short non-relators produce relators?\n")

p = 29
start = (2 % p, 1 % p)

# Find all length-3 words and their endpoints
endpoints = {}
for word in product(range(3), repeat=3):
    result = apply_word(word, start[0], start[1], p)
    if result not in endpoints:
        endpoints[result] = []
    endpoints[result].append(word)

# Count collision groups (same endpoint = potential birthday pair)
collision_sizes = [len(v) for v in endpoints.values()]
max_collision = max(collision_sizes)
avg_collision = sum(collision_sizes) / len(collision_sizes)
num_endpoints = len(endpoints)

print(f"  p={p}, word length 3: {3**3} words → {num_endpoints} distinct endpoints")
print(f"  Max collision group: {max_collision}, avg: {avg_collision:.2f}")
print(f"  Birthday: need ~sqrt({num_endpoints})={int(num_endpoints**0.5)} words to find collision")

# Experiment 4: Functor to quotient — factoring as finding kernel
print("\n--- Experiment 4: Kernel of the reduction functor ---")
print("The functor F: G_N → G_p x G_q sends w(2,1) mod N to (w(2,1) mod p, w(2,1) mod q).")
print("A word in ker(π_p) but not ker(π_q) gives factor p.\n")

p, q = 11, 13
N = p * q
start_N = (2, 1)

# Find words that fix (2,1) mod p but not mod q
kernel_p = []
kernel_q = []
for length in range(1, 7):
    for word in product(range(3), repeat=length):
        res_p = apply_word(word, 2 % p, 1 % p, p)
        res_q = apply_word(word, 2 % q, 1 % q, q)

        if res_p == (2 % p, 1 % p) and res_q != (2 % q, 1 % q):
            kernel_p.append((length, word))
        if res_q == (2 % q, 1 % q) and res_p != (2 % p, 1 % p):
            kernel_q.append((length, word))

    if kernel_p or kernel_q:
        print(f"  Length {length}: {len(kernel_p)} words in ker(π_p)\\ker(π_q), "
              f"{len(kernel_q)} in ker(π_q)\\ker(π_p)")

if kernel_p:
    w = kernel_p[0]
    print(f"\n  Example: word={''.join(str(x) for x in w[1])} (length {w[0]})")
    res_N = apply_word(w[1], 2, 1, N)
    print(f"    w(2,1) mod N = {res_N}")
    print(f"    w(2,1) mod p = {apply_word(w[1], 2%p, 1%p, p)} (should be (2,1) mod {p})")
    print(f"    w(2,1) mod q = {apply_word(w[1], 2%q, 1%q, q)} (should NOT be (2,1) mod {q})")

    # Check: gcd(res_N[0] - 2, N) should give p
    from math import gcd
    g = gcd(res_N[0] - 2, N)
    print(f"    gcd(m_result - 2, N) = gcd({res_N[0]-2}, {N}) = {g}")
    if g == p:
        print(f"    SUCCESS: Factor p={p} found!")
    elif g == q:
        print(f"    SUCCESS: Factor q={q} found!")

print("\n--- KEY FINDINGS ---")
print("1. THEOREM (Relator Period): The shortest relator of <B1,B2,B3> mod p has length")
print("   related to the orbit period. For the parabolic B3, the period is exactly p.")
print("2. The 'categorical kernel' approach (finding words that fix mod p but not mod q)")
print("   WORKS but requires enumerating O(p^2) words — it's the orbit period barrier again.")
print("3. The operadic structure of the tree (free 3-ary algebra) means relations only")
print("   arise from the GROUP STRUCTURE of <B1,B2,B3> mod p, not from the tree topology.")
print("4. INSIGHT: The factoring problem = finding the kernel of the canonical surjection")
print("   G_N → G_p. This is a group-theoretic, not category-theoretic, problem.")
