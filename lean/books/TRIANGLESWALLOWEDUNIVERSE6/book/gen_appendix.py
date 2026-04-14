#!/usr/bin/env python3
"""Generate the Lean appendix LaTeX file with sanitized code."""
import os
import re

lean_files = [
    ("01_BerggrenLorentzCorrespondence.lean", "Berggren--Lorentz Correspondence"),
    ("02_LatticeTreeCorrespondence.lean", "Lattice--Tree Correspondence"),
    ("03_HyperbolicShortcutsFactoring.lean", "Hyperbolic Shortcuts and Factoring"),
    ("04_ThreeRoadsFromPythagoras.lean", "Three Roads from Pythagoras"),
    ("05_BerggrenLorentzPaperProofs.lean", "Berggren--Lorentz Paper Proofs"),
    ("06_HigherKTupleFactoring.lean", "Higher $k$-Tuple Factoring"),
    ("07_QuantumGroverTreeFactoring.lean", "Quantum Grover Tree Factoring"),
    ("08_ComplexityBoundsProven.lean", "Complexity Bounds"),
    ("09_CayleyDicksonHierarchy.lean", "Cayley--Dickson Hierarchy"),
    ("10_FermatLastTheorem.lean", "Fermat's Last Theorem"),
    ("11_CongruenceOfSquaresFactoring.lean", "Congruence of Squares Factoring"),
    ("12_QuadrupleFactorTheory.lean", "Quadruple Factor Theory"),
    ("13_GCDCascadeFactorExtraction.lean", "GCD Cascade Factor Extraction"),
    ("14_PythagoreanTreeFactoringCore.lean", "Pythagorean Tree Factoring Core"),
    ("15_TropicalGeometryFoundations.lean", "Tropical Geometry Foundations"),
    ("16_LorentzGroupStructure.lean", "Lorentz Group Structure"),
]

base = '/workspace/request-project/lean'
out_dir = '/workspace/request-project/book/lean_sanitized'
os.makedirs(out_dir, exist_ok=True)

REPLACEMENTS = {
    '←': '<-', '→': '->', '↔': '<->', '∀': 'forall ', '∃': 'exists ',
    'λ': 'fun ', 'ℕ': 'Nat', 'ℤ': 'Int', 'ℚ': 'Rat', 'ℝ': 'Real', 'ℂ': 'Complex',
    '≤': '<=', '≥': '>=', '≠': '!=', '⊢': '|-', '⟨': '<', '⟩': '>',
    '∧': '/\\', '∨': '\\/', '¬': 'not ', '×': 'x', '⁻¹': '^(-1)',
    '▸': '>', '²': '^2', '³': '^3', '·': '*', '∈': 'in', '∉': 'not_in',
    '⊆': '<=', '⊂': '<', '∅': 'empty', '∩': 'inter', '∪': 'union',
    '⊤': 'top', '⊥': 'bot', '∘': 'comp', '⟹': '==>', '∣': '|', '‖': '||',
    '↦': '|->', '✓': '[ok]', '❌': '[X]', '∎': '[qed]', '…': '...',
    '—': '--', '–': '-', '\u200b': '', '≡': '===', '⊕': 'oplus',
    '⊗': 'otimes', '√': 'sqrt', '∞': 'inf', '∑': 'sum', '∏': 'prod',
    '⟶': '-->', '↑': 'up', '↓': 'down', '⊔': 'sup', '⊓': 'inf',
    '≃': '~=', '≅': '~=', '≈': '~~', '≫': '>>', '≪': '<<',
}

# Greek letters
for g in ['alpha','beta','gamma','delta','epsilon','zeta','eta','theta',
          'iota','kappa','mu','nu','xi','pi','rho','sigma','tau','phi','chi','psi','omega']:
    pass  # Already ASCII

lines = []
for fname, title in lean_files:
    fpath = os.path.join(base, fname)
    if not os.path.exists(fpath):
        continue
    
    with open(fpath, 'r') as f:
        code = f.read()
    
    for old, new in REPLACEMENTS.items():
        code = code.replace(old, new)
    
    cleaned = []
    for ch in code:
        if ord(ch) < 128:
            cleaned.append(ch)
        else:
            cleaned.append('?')
    code = ''.join(cleaned)
    
    san_path = os.path.join(out_dir, fname)
    with open(san_path, 'w') as f:
        f.write(code)
    
    section_label = fname.replace('.lean', '').replace('_', '-')
    display_name = fname.replace('_', r'\_')
    
    lines.append(f'\\section{{{title}}}')
    lines.append(f'\\label{{app:{section_label}}}')
    lines.append(f'\\index{{{title}}}')
    lines.append(f'\\noindent{{\\small\\ttfamily {display_name}}}')
    lines.append('')
    lines.append(f'\\lstinputlisting[language=Lean]{{lean_sanitized/{fname}}}')
    lines.append('')
    lines.append(r'\clearpage')
    lines.append('')

out_path = '/workspace/request-project/book/appendix_lean.tex'
with open(out_path, 'w') as f:
    f.write('\n'.join(lines))

print(f"Wrote {out_path}")
