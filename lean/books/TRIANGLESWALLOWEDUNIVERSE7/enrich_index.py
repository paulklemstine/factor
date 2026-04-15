#!/usr/bin/env python3
"""Add index entries for key terms throughout the book."""
import re

with open('/workspace/request-project/book.tex', 'r') as f:
    text = f.read()

# Key terms to index - (search_pattern, index_entry)
# Only index first occurrence per chapter
terms = [
    (r'Pythagorean triple', 'Pythagorean triple'),
    (r'Berggren tree', 'Berggren tree'),
    (r'Lorentz group', 'Lorentz group'),
    (r'Lorentz form', 'Lorentz form'),
    (r'null cone', 'null cone'),
    (r'quadratic form', 'quadratic form'),
    (r'Pell equation', 'Pell equation'),
    (r'quaternion', 'quaternion'),
    (r'octonion', 'octonion'),
    (r'Cayley.Dickson', 'Cayley--Dickson construction'),
    (r'congruence of squares', 'congruence of squares'),
    (r'tropical geometry', 'tropical geometry'),
    (r'greatest common divisor', 'greatest common divisor (GCD)'),
    (r'lattice reduction', 'lattice reduction'),
    (r'hyperbolic geometry', 'hyperbolic geometry'),
    (r'Plimpton 322', 'Plimpton 322'),
    (r'Brahmagupta', 'Brahmagupta'),
    (r'Fibonacci identity', 'Fibonacci identity'),
    (r'Euler', 'Euler, Leonhard'),
    (r'Euclid', 'Euclid'),
    (r'Fermat', 'Fermat, Pierre de'),
    (r'Wiles', 'Wiles, Andrew'),
    (r'modularity', 'modularity theorem'),
    (r'elliptic curve', 'elliptic curve'),
    (r'infinite descent', 'infinite descent'),
    (r'semiprime', 'semiprime'),
    (r'factoring', 'factoring'),
    (r'factorization', 'factorization'),
    (r'Gaussian integer', 'Gaussian integers'),
    (r'Grover', 'Grover search'),
    (r'quadratic sieve', 'quadratic sieve'),
    (r'number field sieve', 'number field sieve'),
    (r'RSA', 'RSA cryptosystem'),
    (r'Diophantine', 'Diophantine equation'),
    (r'Minkowski', 'Minkowski space'),
    (r'Poincar', 'Poincare disk'),
    (r'special relativity', 'special relativity'),
    (r'spacetime', 'spacetime'),
    (r'light cone', 'light cone'),
    (r'ternary tree', 'ternary tree'),
    (r'matrix multiplication', 'matrix multiplication'),
    (r'determinant', 'determinant'),
    (r'eigenvalue', 'eigenvalue'),
    (r'Chebyshev', 'Chebyshev polynomial'),
    (r'norm form', 'norm form'),
    (r'unique factorization', 'unique factorization'),
    (r'Gaussian elimination', 'Gaussian elimination'),
    (r'trial division', 'trial division'),
    (r'continued fraction', 'continued fraction'),
    (r'Jacobi', 'Jacobi, Carl Gustav Jacob'),
    (r'sum of.*squares', 'sum of squares'),
    (r'Bellman', 'Bellman equation'),
    (r'shortest path', 'shortest path'),
    (r'Hamilton', 'Hamilton, William Rowan'),
    (r'Hurwitz theorem', 'Hurwitz theorem'),
    (r'composition algebra', 'composition algebra'),
]

# Split text by chapters
# Insert \index{term} after first occurrence in each chapter
chapter_splits = re.split(r'(\\chapter)', text)

# Simpler approach: just add index entries at specific positions
# For each term, find all occurrences and add \index after the first one per chapter
for pattern, index_entry in terms:
    # Find all matches (case-insensitive, not in commands)
    # Add \index right after the match
    # But only once per chapter
    chapter_positions = [m.start() for m in re.finditer(r'\\chapter', text)]
    chapter_positions.append(len(text))
    
    indexed_chapters = set()
    new_text = []
    last_end = 0
    
    for m in re.finditer(pattern, text, re.IGNORECASE):
        pos = m.start()
        # Find which chapter this is in
        ch_idx = 0
        for j, cp in enumerate(chapter_positions):
            if pos < cp:
                ch_idx = j
                break
        
        if ch_idx not in indexed_chapters:
            # Check we're not inside a \index{}, \chapter{}, lstlisting, etc.
            context_before = text[max(0, pos-30):pos]
            if '\\index{' not in context_before and '\\chapter' not in context_before and 'lstlisting' not in context_before and '\\section' not in context_before:
                indexed_chapters.add(ch_idx)
                # Insert \index after this match
                end = m.end()
                new_text.append(text[last_end:end])
                new_text.append('\\index{' + index_entry + '}')
                last_end = end
    
    new_text.append(text[last_end:])
    text = ''.join(new_text)

with open('/workspace/request-project/book.tex', 'w') as f:
    f.write(text)

# Count index entries
count = text.count('\\index{')
print(f'Total index entries: {count}')
