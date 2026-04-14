#!/usr/bin/env python3
"""Add index entries to the chapter LaTeX files and generate a standalone index file."""
import os
import re

base = '/workspace/request-project/book'

# Index terms organized by category
index_terms = {
    # People
    'Pythagoras': ['introduction', 'chapter1', 'chapter4', 'chapter16'],
    'Euclid': ['introduction', 'chapter1', 'chapter2', 'chapter4'],
    'Fermat, Pierre de': ['chapter10', 'conclusion'],
    'Berggren, Barning': ['chapter1', 'chapter2', 'chapter3', 'chapter5', 'chapter14'],
    'Einstein, Albert': ['chapter5', 'chapter16', 'conclusion'],
    'Minkowski, Hermann': ['chapter5', 'chapter16', 'conclusion'],
    'Wiles, Andrew': ['chapter10', 'conclusion'],
    'Euler, Leonhard': ['chapter4', 'chapter9', 'chapter10'],
    'Gauss, Carl Friedrich': ['chapter2', 'chapter4'],
    'Grover, Lov': ['chapter7'],
    'Shor, Peter': ['chapter8', 'conclusion'],
    'Cayley, Arthur': ['chapter9'],
    'Dickson, Leonard': ['chapter9'],
    'Hamilton, William Rowan': ['chapter9'],
    'Brahmagupta': ['chapter9', 'chapter13', 'conclusion'],
    'Germain, Sophie': ['chapter10'],
    'Hurwitz, Adolf': ['chapter9', 'conclusion'],
    'Wigner, Eugene': ['conclusion'],
    'Gardner, Martin': ['conclusion'],
    'Neugebauer, Otto': ['introduction'],
    
    # Mathematical objects
    'Pythagorean triple': ['introduction', 'chapter1', 'chapter3', 'chapter14', 'conclusion'],
    'Pythagorean triple!primitive': ['introduction', 'chapter1', 'chapter4'],
    'Berggren tree': ['chapter1', 'chapter2', 'chapter3', 'chapter5', 'chapter14', 'conclusion'],
    'Lorentz group': ['chapter5', 'chapter16', 'conclusion'],
    'light cone': ['chapter3', 'chapter5', 'chapter16', 'conclusion'],
    'null cone': ['chapter5', 'chapter16', 'conclusion'],
    'Minkowski metric': ['chapter5', 'chapter16', 'conclusion'],
    'quadratic form': ['chapter5', 'chapter16'],
    'Euclidean algorithm': ['chapter2', 'chapter3', 'conclusion'],
    'continued fractions': ['chapter2'],
    'lattice': ['chapter2', 'chapter12'],
    'lattice!basis reduction': ['chapter2', 'conclusion'],
    'LLL algorithm': ['chapter2', 'conclusion'],
    'Gaussian integers': ['chapter4', 'chapter9', 'conclusion'],
    'quaternions': ['chapter9', 'conclusion'],
    'octonions': ['chapter9', 'conclusion'],
    'Cayley--Dickson construction': ['chapter9', 'conclusion'],
    'Pell equation': ['chapter5'],
    'Plimpton 322': ['introduction', 'chapter1'],
    
    # Factoring
    'factoring': ['chapter3', 'chapter4', 'chapter8', 'chapter11', 'chapter14'],
    'factoring!difference of squares': ['chapter3', 'chapter11', 'conclusion'],
    'factoring!quadratic sieve': ['chapter11', 'conclusion'],
    'factoring!number field sieve': ['conclusion'],
    'greatest common divisor': ['chapter3', 'chapter13', 'conclusion'],
    'GCD cascade': ['chapter13'],
    'congruence of squares': ['chapter11'],
    'semiprime': ['chapter8', 'chapter14'],
    
    # Quantum
    'quantum computing': ['chapter7', 'conclusion'],
    'Grover\'s algorithm': ['chapter7', 'conclusion'],
    'Shor\'s algorithm': ['chapter8', 'conclusion'],
    
    # Algebra
    'Brahmagupta--Fibonacci identity': ['chapter9', 'conclusion'],
    'Euler four-square identity': ['chapter9', 'conclusion'],
    'norm multiplicativity': ['chapter9'],
    'Hurwitz\'s theorem': ['chapter9', 'conclusion'],
    'Fermat\'s Last Theorem': ['chapter10', 'conclusion'],
    'infinite descent': ['chapter10', 'conclusion'],
    'modular forms': ['chapter10'],
    'elliptic curves': ['chapter10'],
    
    # Geometry
    'hyperbolic geometry': ['chapter3', 'chapter5', 'chapter16'],
    'Poincar\\\'e disk': ['chapter16'],
    'tropical geometry': ['chapter15', 'conclusion'],
    'min-plus semiring': ['chapter15', 'conclusion'],
    'Newton polygon': ['chapter15'],
    
    # Misc
    'Pythagorean quadruple': ['chapter12', 'chapter13', 'conclusion'],
    'Lean 4': ['conclusion'],
    'complexity!$O(\\sqrt{N})$': ['chapter8', 'conclusion'],
    'complexity!$O(N^{1/4})$': ['chapter7', 'conclusion'],
    'RSA cryptography': ['chapter4', 'chapter8'],
    'Euclid parametrization': ['introduction', 'chapter1', 'chapter4'],
}

# For each chapter file, add index entries at the beginning
for chapfile in os.listdir(base):
    if not chapfile.endswith('.tex'):
        continue
    
    filepath = os.path.join(base, chapfile)
    chapname = chapfile[:-4]  # Remove .tex
    
    entries = []
    for term, chapters in index_terms.items():
        if chapname in chapters:
            entries.append(f'\\index{{{term}}}')
    
    if entries:
        with open(filepath) as f:
            content = f.read()
        
        # Add index entries after the first \chapter line
        idx_block = '\n'.join(entries) + '\n'
        
        # Find first \chapter and insert after it
        match = re.search(r'(\\chapter\*?\{[^}]+\})', content)
        if match:
            pos = match.end()
            content = content[:pos] + '\n' + idx_block + content[pos:]
        
        with open(filepath, 'w') as f:
            f.write(content)

print("Index entries added to all chapter files")
