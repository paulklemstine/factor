#!/usr/bin/env python3
"""Generate the Lean appendix with preprocessed files for listings compatibility."""
import os
import re

LEAN_DIR = "/workspace/request-project/lean"
OUTPUT = "/workspace/request-project/book/lean_appendix.tex"
PROCESSED_DIR = "/workspace/request-project/book/lean_processed"

os.makedirs(PROCESSED_DIR, exist_ok=True)

LEAN_FILES = [
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

# Unicode to ASCII/LaTeX mapping for listings
UNICODE_MAP = {
    '→': '->',
    '←': '<-',
    '↔': '<->',
    '↦': '|->',
    '∀': 'forall',
    '∃': 'exists',
    '∈': 'in',
    '∉': 'notin',
    '∧': '/\\',
    '∨': '\\/',
    '¬': '!',
    '≤': '<=',
    '≥': '>=',
    '≠': '!=',
    '≈': '~=',
    '≡': '===',
    '≢': '!==',
    'ℕ': 'Nat',
    'ℤ': 'Int',
    'ℚ': 'Rat',
    'ℝ': 'Real',
    'ℂ': 'Complex',
    'ℍ': 'Quaternion',
    '𝕆': 'Octonion',
    '⟨': '<',
    '⟩': '>',
    '⟹': '==>',
    '×': 'x',
    '·': '.',
    '•': '*',
    '∘': 'o',
    '√': 'sqrt',
    '∣': '|',
    '∤': '!|',
    '∑': 'Sum',
    '∎': 'QED',
    '⊤': 'True',
    '⋯': '...',
    '²': '^2',
    '³': '^3',
    '¹': '^1',
    '⁴': '^4',
    '⁶': '^6',
    '⁸': '^8',
    'ⁿ': '^n',
    '⁺': '^+',
    '⁻': '^-',
    '₀': '_0',
    '₁': '_1',
    '₂': '_2',
    '₃': '_3',
    '₄': '_4',
    '₇': '_7',
    '₈': '_8',
    'ₖ': '_k',
    'ₙ': '_n',
    'ₚ': '_p',
    'ᵢ': '_i',
    'ᵥ': '_v',
    'ᵀ': '^T',
    '§': 'S',
    '±': '+/-',
    '–': '--',
    '—': '---',
    '‹': '<',
    '›': '>',
    '✓': 'check',
    '▸': '>',
    '═': '=',
    'λ': 'fun',
    'Θ': 'Theta',
    'Σ': 'Sigma',
    'ε': 'eps',
    'ζ': 'zeta',
    'π': 'pi',
    'σ': 'sigma',
    'ω': 'omega',
    'é': 'e',
    '↑': 'up',
    '↓': 'dn',
    '⊢': '|-',
}

def sanitize_lean(text):
    """Replace Unicode characters with ASCII equivalents."""
    result = []
    for ch in text:
        if ord(ch) > 127:
            result.append(UNICODE_MAP.get(ch, '?'))
        else:
            result.append(ch)
    return ''.join(result)

lines = []
lines.append("% Auto-generated Lean appendix\n")

for filename, title in LEAN_FILES:
    filepath = os.path.join(LEAN_DIR, filename)
    if not os.path.isfile(filepath):
        continue
    
    # Read and sanitize
    with open(filepath) as f:
        content = f.read()
    sanitized = sanitize_lean(content)
    
    # Write processed file
    processed_path = os.path.join(PROCESSED_DIR, filename)
    with open(processed_path, 'w') as f:
        f.write(sanitized)
    
    rel_path = os.path.relpath(processed_path, '/workspace/request-project/book')
    
    lines.append(f"\n\\section{{{title}}}")
    lines.append(f"\\label{{lean:{filename.replace('.lean','')}}}")
    lines.append(f"")
    lines.append(f"\\lstinputlisting[")
    lines.append(f"  language=Lean4,")
    lines.append(f"  caption={{{title}}},")
    lines.append(f"  label={{lst:{filename.replace('.lean','')}}},")
    lines.append(f"]{{{rel_path}}}")
    lines.append("")

with open(OUTPUT, 'w') as f:
    f.write('\n'.join(lines))

print(f"Lean appendix written to {OUTPUT}")
