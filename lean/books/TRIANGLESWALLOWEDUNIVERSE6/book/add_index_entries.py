#!/usr/bin/env python3
"""Add index entries for key mathematical terms throughout the chapter .tex files."""
import os, re, glob

# Key terms to index (term -> index entry)
KEY_TERMS = {
    'Pythagorean triple': 'Pythagorean triple',
    'Pythagorean triples': 'Pythagorean triple',
    'primitive Pythagorean': 'Pythagorean triple!primitive',
    'Berggren tree': 'Berggren tree',
    'Berggren matrices': 'Berggren matrices',
    'Lorentz': 'Lorentz group',
    'Lorentz group': 'Lorentz group',
    'Lorentz transformation': 'Lorentz transformation',
    'Minkowski': 'Minkowski metric',
    'null cone': 'null cone',
    'light cone': 'light cone',
    'quadratic form': 'quadratic form',
    'Euclid': 'Euclid',
    'Euclidean algorithm': 'Euclidean algorithm',
    'continued fraction': 'continued fraction',
    'Pell equation': 'Pell equation',
    'Fermat': 'Fermat, Pierre de',
    "Fermat's Last Theorem": "Fermat's Last Theorem",
    'infinite descent': 'infinite descent',
    'descent': 'descent',
    'difference of squares': 'difference of squares',
    'factoring': 'factoring',
    'factorization': 'factorization',
    'semiprime': 'semiprime',
    'Gaussian integer': 'Gaussian integers',
    'Gaussian integers': 'Gaussian integers',
    'quaternion': 'quaternions',
    'quaternions': 'quaternions',
    'octonion': 'octonions',
    'octonions': 'octonions',
    'Cayley-Dickson': 'Cayley--Dickson construction',
    'Cayley--Dickson': 'Cayley--Dickson construction',
    'Brahmagupta': 'Brahmagupta--Fibonacci identity',
    'Hurwitz': 'Hurwitz theorem',
    'Grover': "Grover's algorithm",
    "Grover's algorithm": "Grover's algorithm",
    'quantum': 'quantum computation',
    'Shor': "Shor's algorithm",
    'lattice': 'lattice',
    'LLL algorithm': 'LLL algorithm',
    'tropical': 'tropical geometry',
    'tropical geometry': 'tropical geometry',
    'semiring': 'semiring',
    'congruence of squares': 'congruence of squares',
    'quadratic sieve': 'quadratic sieve',
    'number field sieve': 'number field sieve',
    'hyperbolic': 'hyperbolic geometry',
    'Poincaré disk': 'Poincaré disk model',
    'GCD': 'greatest common divisor',
    'gcd': 'greatest common divisor',
    'coprime': 'coprimality',
    'Plimpton 322': 'Plimpton 322',
    'Einstein': 'Einstein, Albert',
    'special relativity': 'special relativity',
    'Wiles': 'Wiles, Andrew',
    'modular form': 'modular forms',
    'modular forms': 'modular forms',
    'elliptic curve': 'elliptic curves',
    'Cayley graph': 'Cayley graph',
    'ternary tree': 'ternary tree',
    'Lean': 'Lean 4',
    'Lean 4': 'Lean 4',
    'Mathlib': 'Mathlib',
    'norm multiplicativity': 'norm multiplicativity',
    'Euler': 'Euler, Leonhard',
    'Gauss': 'Gauss, Carl Friedrich',
    'Wigner': 'Wigner, Eugene',
    'Newton polygon': 'Newton polygon',
    'Bellman-Ford': 'Bellman--Ford algorithm',
    'RSA': 'RSA cryptosystem',
    'cryptography': 'cryptography',
    'Sophie Germain': 'Germain, Sophie',
    'Kummer': 'Kummer, Ernst',
    'ideal': 'ideal (ring theory)',
    'regular prime': 'regular prime',
}

def add_index(tex_content):
    """Add index entries at first occurrence of each key term in the chapter."""
    indexed = set()
    lines = tex_content.split('\n')
    new_lines = []
    
    for line in lines:
        # Don't add index entries inside commands or math
        if line.strip().startswith('\\') and not line.strip().startswith('\\text'):
            new_lines.append(line)
            continue
        
        for term, entry in KEY_TERMS.items():
            if entry in indexed:
                continue
            # Check if term appears in this line (case-insensitive for first char)
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            if pattern.search(line):
                # Add index entry after this line
                line = line + r'\index{' + entry + '}'
                indexed.add(entry)
                break  # Only one index entry per line
        
        new_lines.append(line)
    
    return '\n'.join(new_lines)


book_dir = '/workspace/request-project/book'
for f in sorted(glob.glob(os.path.join(book_dir, 'ch_*.tex'))):
    with open(f, 'r') as fh:
        content = fh.read()
    new_content = add_index(content)
    with open(f, 'w') as fh:
        fh.write(new_content)
    print(f"Indexed {os.path.basename(f)}")

print("Done adding index entries.")
