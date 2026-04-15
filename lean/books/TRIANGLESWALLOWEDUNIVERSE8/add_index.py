#!/usr/bin/env python3
"""Post-process book.tex to add \\index{} commands for key terms."""

import re

# Index terms to search for in text (case-insensitive where appropriate)
# Format: (search_pattern, index_entry)
index_terms = [
    (r'\bPythagorean triple', 'Pythagorean triple'),
    (r'\bPythagorean triples\b', 'Pythagorean triple'),
    (r'\bBerggren tree\b', 'Berggren tree'),
    (r'\bBerggren matrices\b', 'Berggren tree!matrices'),
    (r'\bLorentz group\b', 'Lorentz group'),
    (r'\bLorentz boost\b', 'Lorentz group!boost'),
    (r'\bLorentz form\b', 'Lorentz group!form'),
    (r'\bMinkowski\b', 'Minkowski metric'),
    (r'\bnull cone\b', 'null cone'),
    (r'\blight cone\b', 'light cone'),
    (r'\bEuclidean algorithm\b', 'Euclidean algorithm'),
    (r'\bPell equation\b', 'Pell equation'),
    (r'\bquadratic form\b', 'quadratic form'),
    (r'\bsemiprime\b', 'semiprime'),
    (r'\bRSA\b', 'RSA cryptography'),
    (r'\bcryptography\b', 'cryptography'),
    (r'\bquaternion', 'quaternions'),
    (r'\boctonion', 'octonions'),
    (r'\bCayley.Dickson\b', 'Cayley--Dickson construction'),
    (r"Fermat's Last Theorem", "Fermat's Last Theorem"),
    (r'\binfinite descent\b', 'infinite descent'),
    (r'\bcongruence of squares\b', 'congruence of squares'),
    (r'\bquadratic sieve\b', 'quadratic sieve'),
    (r'\bnumber field sieve\b', 'number field sieve'),
    (r'\bBrahmagupta\b', 'Brahmagupta--Fibonacci identity'),
    (r'\bGaussian integer', 'Gaussian integers'),
    (r'\bEisenstein integer', 'Eisenstein integers'),
    (r'\btropical geometry\b', 'tropical geometry'),
    (r'\bLLL algorithm\b', 'LLL algorithm'),
    (r'\blattice reduction\b', 'lattice reduction'),
    (r"\bGrover's algorithm\b", "Grover's algorithm"),
    (r'\bquantum computing\b', 'quantum computing'),
    (r'\bPlimpton 322\b', 'Plimpton 322'),
    (r'\bChebyshev\b', 'Chebyshev polynomials'),
    (r'\bcontinued fraction', 'continued fractions'),
    (r'\bunique factorization\b', 'unique factorization'),
    (r'\bternary tree\b', 'ternary tree'),
    (r'\bgnomon\b', 'gnomon'),
    (r'\bBellman\b', 'Bellman equation'),
    (r'\bshortest path\b', 'shortest path problem'),
    (r'\btrial division\b', 'trial division'),
    (r'\belliptic curve', 'elliptic curves'),
    (r'\bmodular form', 'modular forms'),
    (r'\bdeterminant\b', 'determinant'),
    (r'\bEuler\b', 'Euler, Leonhard'),
    (r'\bGauss\b', 'Gauss, Carl Friedrich'),
    (r'\bHamilton\b', 'Hamilton, William Rowan'),
    (r'\bWiles\b', 'Wiles, Andrew'),
    (r'\bSophie Germain\b', 'Germain, Sophie'),
    (r'\bJacobi\b', 'Jacobi, Carl Gustav'),
    (r'\bdiophantine\b', 'Diophantine equation'),
    (r'\bDiophantine\b', 'Diophantine equation'),
    (r'\bprimitive triple\b', 'primitive Pythagorean triple'),
    (r'\bprimitive Pythagorean\b', 'primitive Pythagorean triple'),
    (r'\bhyperbolic geometry\b', 'hyperbolic geometry'),
    (r'\bhyperbolic plane\b', 'hyperbolic geometry!plane'),
    (r"Poincar\\'e disk", 'Poincar\\'+"e disk"),
    (r'\bfactor base\b', 'factor base'),
    (r'\bDixon\b', 'Dixon\'s method'),
    (r'\bfour.square identity\b', 'four-square identity'),
    (r'\beight.square identity\b', 'eight-square identity'),
    (r'\bHurwitz\b', 'Hurwitz theorem'),
    (r'\bnorm form\b', 'norm form'),
]

def add_index_entries(tex_content):
    """Add \\index{} commands to the LaTeX content."""
    lines = tex_content.split('\n')
    new_lines = []
    in_lstlisting = False
    in_math = False
    
    # Track which terms have been indexed (limit to first occurrence per chapter)
    chapter_terms = set()
    
    for line in lines:
        # Track lstlisting environment
        if '\\begin{lstlisting}' in line:
            in_lstlisting = True
            new_lines.append(line)
            continue
        if '\\end{lstlisting}' in line:
            in_lstlisting = False
            new_lines.append(line)
            continue
        
        if in_lstlisting:
            new_lines.append(line)
            continue
        
        # Reset terms at each chapter
        if '\\chapter' in line:
            chapter_terms = set()
            new_lines.append(line)
            continue
        
        # Skip math environments
        if line.strip().startswith('\\[') or line.strip().startswith('\\begin{align'):
            new_lines.append(line)
            continue
        
        # Add index entries
        modified_line = line
        for pattern, entry in index_terms:
            if entry in chapter_terms:
                continue
            match = re.search(pattern, modified_line)
            if match:
                # Add index entry after the match
                pos = match.end()
                modified_line = modified_line[:pos] + f'\\index{{{entry}}}' + modified_line[pos:]
                chapter_terms.add(entry)
        
        new_lines.append(modified_line)
    
    return '\n'.join(new_lines)


if __name__ == '__main__':
    with open('/workspace/request-project/book.tex', 'r') as f:
        content = f.read()
    
    content = add_index_entries(content)
    
    with open('/workspace/request-project/book.tex', 'w') as f:
        f.write(content)
    
    print("Index entries added successfully.")
