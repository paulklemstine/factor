#!/usr/bin/env python3
"""Generate the Lean appendix LaTeX file - using VerbatimInput for safety."""
import os

base = '/workspace/request-project'
lean_dir = f'{base}/lean'
appendix_lean_dir = f'{base}/book/lean_listings'
os.makedirs(appendix_lean_dir, exist_ok=True)

lean_files = sorted([f for f in os.listdir(lean_dir) if f.endswith('.lean')])

chapter_names = {
    '01': 'Berggren--Lorentz Correspondence',
    '02': 'Lattice--Tree Correspondence',
    '03': 'Hyperbolic Shortcuts \\& Factoring',
    '04': 'Three Roads from Pythagoras',
    '05': 'Berggren--Lorentz Paper Proofs',
    '06': 'Higher $K$-Tuple Factoring',
    '07': 'Quantum Grover Tree Factoring',
    '08': 'Complexity Bounds',
    '09': 'Cayley--Dickson Hierarchy',
    '10': "Fermat's Last Theorem",
    '11': 'Congruence of Squares Factoring',
    '12': 'Quadruple Factor Theory',
    '13': 'GCD Cascade Factor Extraction',
    '14': 'Pythagorean Tree Factoring Core',
    '15': 'Tropical Geometry Foundations',
    '16': 'Lorentz Group Structure',
}

with open(f'{base}/book/appendix_lean.tex', 'w') as out:
    for f in lean_files:
        num = f[:2]
        name = chapter_names.get(num, f[3:-5].replace('_', ' '))
        
        out.write(f'\\chapter*{{Appendix {num}: {name}}}\n')
        out.write(f'\\addcontentsline{{toc}}{{chapter}}{{Appendix {num}: {name}}}\n')
        out.write(f'\\markboth{{Appendix {num}}}{{Appendix {num}}}\n\n')
        
        # Read the lean file and sanitize for LaTeX
        filepath = os.path.join(lean_dir, f)
        with open(filepath, encoding='utf-8') as lf:
            content = lf.read()
        
        # Replace problematic Unicode with ASCII approximations for listings
        replacements = {
            '→': '->',
            '←': '<-',
            '↔': '<->',
            '∀': 'forall ',
            '∃': 'exists ',
            '¬': 'not ',
            '∧': '/\\',
            '∨': '\\/',
            '⊢': '|-',
            '≤': '<=',
            '≥': '>=',
            '≠': '!=',
            'ℕ': 'Nat',
            'ℤ': 'Int',
            'ℝ': 'Real',
            'ℂ': 'Complex',
            'λ': 'fun',
            '⟨': '<',
            '⟩': '>',
            '·': '.',
            '₁': '1',
            '₂': '2',
            '₃': '3',
            '₄': '4',
            '₀': '0',
            'α': 'alpha',
            'β': 'beta',
            'γ': 'gamma',
            'δ': 'delta',
            'ε': 'epsilon',
            'η': 'eta',
            'θ': 'theta',
            'ι': 'iota',
            'κ': 'kappa',
            'μ': 'mu',
            'ν': 'nu',
            'π': 'pi',
            'ρ': 'rho',
            'σ': 'sigma',
            'τ': 'tau',
            'φ': 'phi',
            'ψ': 'psi',
            'ω': 'omega',
            '⁻¹': '^(-1)',
            '∈': 'in',
            '∉': 'notin',
            '⊆': 'subset',
            '⊂': 'ssubset',
            '∪': 'union',
            '∩': 'inter',
            '∅': 'empty',
            '∞': 'infty',
            '×': 'x',
            '⊕': '+',
            '⊗': '*',
            '\u2080': '0',
            '\u2081': '1',
            '\u2082': '2',
            '†': '+',
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Truncate very long files
        lines = content.split('\n')
        max_lines = 150
        truncated = len(lines) > max_lines
        if truncated:
            lines = lines[:max_lines]
            lines.append('')
            lines.append(f'-- [... {len(content.split(chr(10))) - max_lines} more lines omitted for brevity ...]')
            lines.append(f'-- See the full source in lean/{f}')
        
        safe_content = '\n'.join(lines)
        
        # Write sanitized file
        safe_path = os.path.join(appendix_lean_dir, f.replace('.lean', '_safe.lean'))
        with open(safe_path, 'w', encoding='ascii', errors='replace') as sf:
            sf.write(safe_content)
        
        out.write(f'\\noindent\\texttt{{\\small {f}}}\n\n')
        out.write(f'\\begin{{small}}\n')
        out.write(f'\\VerbatimInput[frame=single,numbers=left,numbersep=3pt,fontsize=\\scriptsize]{{{safe_path}}}\n')
        out.write(f'\\end{{small}}\n')
        if truncated:
            out.write(f'\\smallskip\\noindent\\textit{{(Truncated --- full source available in \\texttt{{lean/{f}}})}}\n')
        out.write('\\cleardoublepage\n\n')

print(f"Generated appendix with {len(lean_files)} Lean files")
