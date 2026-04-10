#!/usr/bin/env python3
"""
Gibbs' Inequality and Information Theory Demo

Demonstrates the properties formalized in InformationTheory/Information__Entropy.lean:
1. Shannon entropy computation
2. Gibbs' inequality (KL divergence ≥ 0)
3. Maximum entropy theorem
4. Source coding lower bound
"""

import math
from collections import Counter


def shannon_entropy(probs):
    """Compute Shannon entropy H(p) = -∑ p(x) log₂ p(x)."""
    return -sum(p * math.log2(p) for p in probs if p > 0)


def kl_divergence(p, q):
    """
    Compute KL divergence D(p || q) = ∑ p(x) log₂(p(x)/q(x)).
    Gibbs' inequality: D(p || q) ≥ 0 (formalized in Lean).
    """
    return sum(pi * math.log2(pi / qi) for pi, qi in zip(p, q) if pi > 0 and qi > 0)


def mutual_information(pXY, pX, pY):
    """Compute mutual information I(X;Y) = H(X) + H(Y) - H(X,Y)."""
    return shannon_entropy(pX) + shannon_entropy(pY) - shannon_entropy(pXY)


def demo():
    print("=" * 60)
    print("GIBBS' INEQUALITY & INFORMATION THEORY DEMO")
    print("Demonstrating properties formalized in Lean 4")
    print("=" * 60)
    
    # Demo 1: Shannon entropy
    print("\n1. SHANNON ENTROPY")
    print()
    
    distributions = {
        'Deterministic (1,0,0)': [1.0, 0.0, 0.0],
        'Uniform (⅓,⅓,⅓)': [1/3, 1/3, 1/3],
        'Skewed (0.7,0.2,0.1)': [0.7, 0.2, 0.1],
        'Binary uniform': [0.5, 0.5],
        'Fair die': [1/6] * 6,
        'Loaded die': [0.3, 0.2, 0.2, 0.15, 0.1, 0.05],
    }
    
    for name, p in distributions.items():
        H = shannon_entropy(p)
        max_H = math.log2(len(p))
        print(f"   {name:<28} H = {H:.4f} bits  (max = {max_H:.4f})")
    
    # Demo 2: Gibbs' inequality
    print("\n\n2. GIBBS' INEQUALITY: D(p || q) ≥ 0")
    print("   (formalized as `gibbs_inequality` in Lean)")
    print()
    
    test_pairs = [
        ('p=uniform, q=uniform', [1/3]*3, [1/3]*3),
        ('p=skewed, q=uniform', [0.7, 0.2, 0.1], [1/3]*3),
        ('p=uniform, q=skewed', [1/3]*3, [0.7, 0.2, 0.1]),
        ('p=(0.9,0.1), q=(0.5,0.5)', [0.9, 0.1], [0.5, 0.5]),
        ('p=(0.5,0.5), q=(0.9,0.1)', [0.5, 0.5], [0.9, 0.1]),
        ('p=(0.99,0.01), q=(0.5,0.5)', [0.99, 0.01], [0.5, 0.5]),
    ]
    
    for name, p, q in test_pairs:
        D = kl_divergence(p, q)
        status = "≥ 0 ✓" if D >= -1e-10 else "< 0 ✗"
        print(f"   {name:<38} D = {D:>8.4f}  {status}")
    
    # Demo 3: Maximum entropy theorem
    print("\n\n3. MAXIMUM ENTROPY THEOREM")
    print("   H(p) ≤ log₂|Ω| with equality iff p is uniform")
    print("   (formalized as `entropy_le_log_card` in Lean)")
    print()
    
    for n in [2, 4, 8, 16]:
        max_H = math.log2(n)
        # Test various distributions on n outcomes
        uniform = [1/n] * n
        H_uniform = shannon_entropy(uniform)
        
        # A peaked distribution
        peaked = [0.5] + [0.5/(n-1)] * (n-1) if n > 1 else [1.0]
        H_peaked = shannon_entropy(peaked)
        
        print(f"   |Ω| = {n:>3}:  log₂|Ω| = {max_H:.4f},  "
              f"H(uniform) = {H_uniform:.4f},  H(peaked) = {H_peaked:.4f}")
    
    # Demo 4: Source coding lower bound
    print("\n\n4. SOURCE CODING LOWER BOUND")
    print("   E[ℓ] ≥ H(p) for any uniquely decodable code")
    print("   (formalized as `source_coding_lower_bound` in Lean)")
    print()
    
    # Example: English letter frequencies (simplified)
    letters = 'etaoinshrdlu'
    freqs = [0.127, 0.091, 0.082, 0.075, 0.070, 0.063, 0.061, 0.053, 0.050, 0.043, 0.040, 0.028]
    # Normalize
    total = sum(freqs)
    freqs = [f/total for f in freqs]
    
    H = shannon_entropy(freqs)
    
    # Huffman-like code lengths (approximate)
    code_lengths = [3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 5]
    
    expected_length = sum(p * l for p, l in zip(freqs, code_lengths))
    
    print(f"   English letter subset: {letters}")
    print(f"   Entropy H(p) = {H:.4f} bits/symbol")
    print(f"   Expected code length = {expected_length:.4f} bits/symbol")
    print(f"   H(p) ≤ E[ℓ]: {H:.4f} ≤ {expected_length:.4f} {'✓' if H <= expected_length + 0.001 else '✗'}")
    
    # Demo 5: Entropy of real text
    print("\n\n5. ENTROPY ESTIMATION OF REAL TEXT")
    print()
    
    texts = {
        'Random': ''.join(chr(ord('a') + (i * 7 + 3) % 26) for i in range(500)),
        'English-like': 'the quick brown fox jumps over the lazy dog ' * 12,
        'Repetitive': 'abcabc' * 83 + 'ab',
        'Binary': '01' * 250,
    }
    
    for name, text in texts.items():
        counts = Counter(text)
        n = len(text)
        probs = [c/n for c in counts.values()]
        H = shannon_entropy(probs)
        max_H = math.log2(len(counts))
        efficiency = H / max_H if max_H > 0 else 0
        
        print(f"   {name:<15} |Σ|={len(counts):>3}  H={H:.3f} bits/sym  "
              f"max={max_H:.3f}  efficiency={efficiency:.3f}")
    
    # Demo 6: Data processing inequality
    print("\n\n6. DATA PROCESSING INEQUALITY (COMBINATORIAL)")
    print("   |image(g∘f)(S)| ≤ |image(f)(S)|")
    print("   (formalized as `data_processing_card` in Lean)")
    print()
    
    S = list(range(10))
    f = lambda x: x % 5  # Maps to {0,1,2,3,4}
    g = lambda x: x % 3  # Maps to {0,1,2}
    
    image_f = set(f(x) for x in S)
    image_gf = set(g(f(x)) for x in S)
    
    print(f"   S = {S}")
    print(f"   f(x) = x mod 5:  image(f)(S) = {sorted(image_f)}  (|·| = {len(image_f)})")
    print(f"   g(x) = x mod 3:  image(g∘f)(S) = {sorted(image_gf)}  (|·| = {len(image_gf)})")
    print(f"   |image(g∘f)| ≤ |image(f)|: {len(image_gf)} ≤ {len(image_f)} {'✓' if len(image_gf) <= len(image_f) else '✗'}")


if __name__ == "__main__":
    demo()
