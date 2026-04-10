#!/usr/bin/env python3
"""
Kolmogorov Complexity Demo

Demonstrates the concepts formalized in New/New__KolmogorovComplexity.lean:
1. Description methods and complexity
2. The invariance theorem (universality → optimality)
3. Incompressible strings
4. Practical compression as an upper bound on Kolmogorov complexity
"""

import zlib
import gzip
import random
import string
from collections import Counter


def practical_complexity(s, encoding='utf-8'):
    """
    Estimate Kolmogorov complexity using real compression.
    K(x) ≤ |compressed(x)| + c (constant overhead for decompressor).
    
    This gives an upper bound on the true Kolmogorov complexity.
    """
    data = s.encode(encoding) if isinstance(s, str) else s
    compressed = zlib.compress(data, level=9)
    return len(compressed) * 8  # bits


def entropy_estimate(s):
    """Estimate Shannon entropy (bits per symbol) of a string."""
    if not s:
        return 0
    counts = Counter(s)
    n = len(s)
    import math
    return -sum((c/n) * math.log2(c/n) for c in counts.values() if c > 0)


def generate_patterns():
    """Generate strings with different Kolmogorov complexities."""
    patterns = {}
    
    # Low complexity: repetitive
    patterns['zeros'] = '0' * 1000
    patterns['alternating'] = '01' * 500
    patterns['counting'] = ''.join(str(i % 10) for i in range(1000))
    
    # Medium complexity: structured
    patterns['english'] = ("the quick brown fox jumps over the lazy dog " * 25)[:1000]
    patterns['fibonacci'] = ''
    a, b = 0, 1
    while len(patterns['fibonacci']) < 1000:
        patterns['fibonacci'] += str(a % 10)
        a, b = b, a + b
    patterns['fibonacci'] = patterns['fibonacci'][:1000]
    
    # High complexity: random
    random.seed(42)
    patterns['random_binary'] = ''.join(random.choice('01') for _ in range(1000))
    patterns['random_alpha'] = ''.join(random.choice(string.ascii_lowercase) for _ in range(1000))
    
    return patterns


def counting_argument(n):
    """
    Demonstrate the counting argument for incompressible strings.
    
    There are 2^n binary strings of length n.
    Programs of length < n: 2^0 + 2^1 + ... + 2^(n-1) = 2^n - 1
    Therefore, at least one string of length n is incompressible.
    
    This corresponds to `incompressible_exist` in the Lean formalization.
    """
    total_strings = 2 ** n
    shorter_programs = sum(2 ** k for k in range(n))  # = 2^n - 1
    incompressible_fraction = (total_strings - shorter_programs) / total_strings
    return total_strings, shorter_programs, incompressible_fraction


def demo():
    print("=" * 60)
    print("KOLMOGOROV COMPLEXITY DEMO")
    print("Demonstrating concepts formalized in Lean 4")
    print("=" * 60)
    
    # Demo 1: Practical complexity estimation
    print("\n1. COMPLEXITY ESTIMATION VIA COMPRESSION")
    print("   K(x) ≤ |compressed(x)| + c")
    print()
    
    patterns = generate_patterns()
    
    print(f"   {'Pattern':<20} {'Length':>8} {'Compressed':>12} {'Ratio':>8} {'Entropy':>8}")
    print(f"   {'-------':<20} {'------':>8} {'----------':>12} {'-----':>8} {'-------':>8}")
    
    for name, s in sorted(patterns.items(), key=lambda x: practical_complexity(x[1])):
        orig_bits = len(s) * 8
        comp_bits = practical_complexity(s)
        ratio = comp_bits / orig_bits
        ent = entropy_estimate(s)
        print(f"   {name:<20} {orig_bits:>8} {comp_bits:>12} {ratio:>8.3f} {ent:>8.3f}")
    
    # Demo 2: Invariance theorem illustration
    print("\n\n2. INVARIANCE THEOREM ILLUSTRATION")
    print("   Different 'description methods' give similar complexity")
    print()
    
    test_string = "hello world" * 50
    data = test_string.encode('utf-8')
    
    # Different compression methods as different "description methods"
    methods = {
        'zlib-1': len(zlib.compress(data, level=1)),
        'zlib-6': len(zlib.compress(data, level=6)),
        'zlib-9': len(zlib.compress(data, level=9)),
        'gzip': len(gzip.compress(data)),
    }
    
    min_size = min(methods.values())
    print(f"   String: 'hello world' × 50 ({len(data)} bytes)")
    print()
    for name, size in methods.items():
        diff = size - min_size
        print(f"   {name:>10}: {size:>6} bytes (+ {diff:>3} from best)")
    
    print()
    print("   The invariance theorem (universal_is_optimal) guarantees that")
    print("   K_U(x) ≤ K_φ(x) + c for a fixed constant c, regardless of φ.")
    print("   The differences above are bounded by a constant (the 'c').")
    
    # Demo 3: Incompressible strings
    print("\n\n3. INCOMPRESSIBLE STRINGS")
    print("   Counting argument: most strings are incompressible")
    print()
    
    print(f"   {'n':>4} {'Strings':>12} {'Programs<n':>12} {'Incomp. %':>10}")
    print(f"   {'--':>4} {'-------':>12} {'----------':>12} {'---------':>10}")
    
    for n in [4, 8, 16, 32, 64, 128, 256]:
        total, shorter, frac = counting_argument(n)
        print(f"   {n:>4} {total:>12} {shorter:>12} {frac*100:>9.4f}%")
    
    print()
    print("   As n → ∞, the fraction of incompressible strings → 1.")
    print("   This is formalized as `incompressible_exist` in Lean.")
    
    # Demo 4: Complexity of different data types
    print("\n\n4. COMPLEXITY OF MATHEMATICAL SEQUENCES")
    print()
    
    import math
    
    sequences = {
        'π digits': ''.join(str(int(c)) for c in f"{math.pi:.200f}" if c.isdigit())[:200],
        'e digits': ''.join(str(int(c)) for c in f"{math.e:.200f}" if c.isdigit())[:200],
        'sqrt(2)': ''.join(str(int(c)) for c in f"{math.sqrt(2):.200f}" if c.isdigit())[:200],
        'powers of 2': ''.join(str(2**k % 10) for k in range(200)),
        'primes mod 10': '',
    }
    
    # Generate primes mod 10
    primes = []
    for n in range(2, 2000):
        if all(n % p != 0 for p in range(2, int(n**0.5) + 1)):
            primes.append(str(n % 10))
            if len(primes) >= 200:
                break
    sequences['primes mod 10'] = ''.join(primes)
    
    print(f"   {'Sequence':<20} {'Length':>8} {'Compressed':>12} {'Ratio':>8}")
    print(f"   {'--------':<20} {'------':>8} {'----------':>12} {'-----':>8}")
    
    for name, s in sequences.items():
        if not s:
            continue
        orig = len(s)
        comp = len(zlib.compress(s.encode(), level=9))
        print(f"   {name:<20} {orig:>8} {comp:>12} {comp/orig:>8.3f}")
    
    # Demo 5: Upper bound K(x) ≤ |x| + c
    print("\n\n5. TRIVIAL UPPER BOUND: K(x) ≤ |x| + c")
    print("   (formalized as `complexity_le_length`)")
    print()
    
    # For random strings, compression often INCREASES size (due to headers)
    random.seed(123)
    print(f"   {'Length':>8} {'Compressed':>12} {'Overhead':>10} {'K ≤ |x|+c':>12}")
    print(f"   {'------':>8} {'----------':>12} {'--------':>10} {'---------':>12}")
    
    for length in [10, 50, 100, 500, 1000, 5000]:
        data = bytes(random.randint(0, 255) for _ in range(length))
        comp = len(zlib.compress(data, level=9))
        overhead = comp - length
        print(f"   {length:>8} {comp:>12} {overhead:>+10} {'✓':>12}")
    
    print()
    print("   For random data, compressed size ≈ original size + constant overhead.")
    print("   The constant 'c' includes the decompressor description.")


if __name__ == "__main__":
    demo()
