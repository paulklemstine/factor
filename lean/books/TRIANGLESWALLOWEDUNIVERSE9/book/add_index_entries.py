#!/usr/bin/env python3
"""Add index entries to the LaTeX chapter files."""

import re
import os
import glob

# Key terms to index, mapping display form to search patterns
index_terms = {
    # Core concepts
    'Pythagorean triple': [r'Pythagorean triple'],
    'Pythagorean triple!primitive': [r'primitive Pythagorean triple', r'primitive triple'],
    'Berggren tree': [r'Berggren tree', r'Berggren\'s tree'],
    'Berggren matrices': [r'Berggren matri'],
    'Euclid!parameters': [r'Euclid\'s parameters', r'Euclid parameters'],
    'Euclid!formula': [r'Euclid\'s formula'],
    'quadratic form': [r'quadratic form'],
    'Lorentz group': [r'Lorentz group'],
    'Lorentz transformation': [r'Lorentz transform'],
    'null cone': [r'null cone'],
    'light cone': [r'light cone'],
    'Minkowski space': [r'Minkowski'],
    'spacetime': [r'spacetime'],
    # Number theory
    'factoring': [r'factor(?:ing|ization)'],
    'greatest common divisor': [r'greatest common divisor', r'\\\\gcd'],
    'GCD cascade': [r'GCD cascade'],
    'Fermat!last theorem': [r'Fermat.s Last Theorem', r"Fermat's Last Theorem"],
    'Fermat!method': [r'Fermat.s method'],
    'difference of squares': [r'difference.of.squares', r'difference of squares'],
    'congruence of squares': [r'congruence of squares'],
    'Pell equation': [r'Pell equation'],
    'prime number': [r'prime number'],
    'RSA': [r'\bRSA\b'],
    'semiprime': [r'semiprime'],
    # Algebra
    'Gaussian integers': [r'Gaussian integer'],
    'quaternions': [r'quaternion'],
    'octonions': [r'octonion'],
    'Cayley--Dickson construction': [r'Cayley.Dickson'],
    'Brahmagupta--Fibonacci identity': [r'Brahmagupta.Fibonacci'],
    'complex numbers': [r'complex number'],
    'norm!multiplicativity': [r'norm.*multiplicat', r'multiplicat.*norm'],
    # Tropical
    'tropical geometry': [r'tropical geometry'],
    'tropical semiring': [r'tropical semiring'],
    'semiring': [r'\bsemiring\b'],
    # Computational complexity
    'computational complexity': [r'computational complexity'],
    'square root barrier': [r'square.root barrier', r'\\sqrt\{N\} barrier'],
    'quantum computing': [r'quantum comput'],
    'Grover!algorithm': [r'Grover.s algorithm', r'Grover algorithm'],
    'Shor!algorithm': [r'Shor.s algorithm'],
    # Historical figures
    'Pythagoras': [r'\bPythagoras\b'],
    'Brahmagupta': [r'\bBrahmagupta\b'],
    'Fibonacci': [r'\bFibonacci\b'],
    'Euler, Leonhard': [r'\bEuler\b'],
    'Fermat, Pierre de': [r'Pierre de Fermat', r'\bFermat\b'],
    'Diophantus': [r'\bDiophantus\b'],
    'Wiles, Andrew': [r'\bWiles\b'],
    'Hamilton, William Rowan': [r'\bHamilton\b'],
    'Berggren, B.': [r'\bBerggren\b'],
    'Germain, Sophie': [r'Sophie Germain', r'\bGermain\b'],
    # Objects
    'Plimpton 322': [r'Plimpton 322'],
    'Fano plane': [r'Fano plane'],
    'elliptic curve': [r'elliptic curve'],
    'modularity theorem': [r'modularity theorem'],
    # Matrix/linear algebra
    'matrix': [r'\bmatrix\b', r'\bmatrices\b'],
    'determinant': [r'\bdeterminant\b'],
    'lattice': [r'\blattice\b'],
    'lattice reduction': [r'lattice reduction'],
    # Lean
    'Lean 4': [r'\bLean\b'],
    'Mathlib': [r'\bMathlib\b'],
    'formal verification': [r'formal verif', r'formally verif', r'machine.verified'],
    # Other
    'descent!infinite': [r'infinite descent'],
    'induction': [r'\binduction\b'],
    'Pythagorean quadruple': [r'Pythagorean quadruple'],
    'Pythagorean quintuple': [r'Pythagorean quintuple'],
    'Poincar\\\'e disk': [r'Poincar.* disk'],
    'hyperbolic geometry': [r'hyperbolic geometry'],
}

def add_index_to_file(filepath):
    """Add index entries to a LaTeX chapter file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Track which terms we've already indexed in this file to avoid duplicates
    indexed = set()
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        new_lines.append(line)
        
        # Skip if line is a command, comment, or in math mode
        if line.strip().startswith('\\') and not line.strip().startswith('\\text'):
            continue
        if line.strip().startswith('%'):
            continue
        
        for index_key, patterns in index_terms.items():
            if index_key in indexed:
                continue
            for pattern in patterns:
                try:
                    if re.search(pattern, line, re.IGNORECASE):
                        new_lines.append(f'\\index{{{index_key}}}')
                        indexed.add(index_key)
                        break
                except:
                    pass
    
    with open(filepath, 'w') as f:
        f.write('\n'.join(new_lines))

# Process all chapter files
book_dir = '/workspace/request-project/book'
for texfile in sorted(glob.glob(os.path.join(book_dir, '*.tex'))):
    basename = os.path.basename(texfile)
    if basename in ('main.tex', 'appendix_lean.tex'):
        continue
    add_index_to_file(texfile)
    print(f'Added index entries to {basename}')

print('Done adding index entries.')
