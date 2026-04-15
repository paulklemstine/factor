#!/usr/bin/env python3
"""Copy Lean files replacing ALL non-ASCII with ASCII equivalents."""
import os

src = '/workspace/request-project/lean'
dst = '/workspace/request-project/book/lean_clean'
os.makedirs(dst, exist_ok=True)

# Complete mapping of ALL Unicode chars used in Lean to ASCII
char_map = {
    'α': 'alpha', 'β': 'beta', 'γ': 'gamma', 'δ': 'delta',
    'ε': 'epsilon', 'ζ': 'zeta', 'η': 'eta', 'θ': 'theta',
    'ι': 'iota', 'κ': 'kappa', 'λ': 'lam', 'μ': 'mu',
    'ν': 'nu', 'ξ': 'xi', 'π': 'pi', 'ρ': 'rho',
    'σ': 'sigma', 'τ': 'tau', 'φ': 'phi', 'χ': 'chi',
    'ψ': 'psi', 'ω': 'omega',
    'Γ': 'Gamma', 'Δ': 'Delta', 'Θ': 'Theta', 'Λ': 'Lambda',
    'Σ': 'Sigma', 'Π': 'Pi', 'Φ': 'Phi', 'Ψ': 'Psi', 'Ω': 'Omega',
    'ℕ': 'Nat', 'ℤ': 'Int', 'ℚ': 'Rat', 'ℝ': 'Real', 'ℂ': 'Complex',
    'ℍ': 'Quaternion',
    '→': '->', '←': '<-', '↔': '<->', '⇒': '=>', '⇐': '<=',
    '∀': 'forall', '∃': 'exists',
    '≤': '<=', '≥': '>=', '≠': '!=',
    '∧': '/\\', '∨': '\\/', '¬': '!',
    '⊢': '|-',
    '∈': 'in', '∉': 'not_in',
    '⊆': 'subset_eq', '⊂': 'subset',
    '∪': 'union', '∩': 'inter',
    '×': 'x', '·': '.', '∘': 'comp',
    '⟨': '<', '⟩': '>',
    '▸': '>',
    'ᵀ': '^T',
    '⊕': '(+)', '⊗': '(*)',
    '⊥': 'bot', '⊤': 'top',
    '∣': '|', '∅': 'empty',
    '†': '+', '‖': '||',
    '⁻': '^-', '¹': '1', '²': '2', '³': '3',
    '₀': '_0', '₁': '_1', '₂': '_2', '₃': '_3',
    '₄': '_4', '₅': '_5', '₆': '_6', '₇': '_7',
    '₈': '_8', '₉': '_9',
    '∑': 'sum', '∏': 'prod',
    '∂': 'partial', '∇': 'nabla',
    '∞': 'inf',
    '≈': '~=', '≡': '===', '≅': '~=',
    '«': '<<', '»': '>>',
    '‹': '<', '›': '>',
    '—': '--', '–': '-',
    '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
    '…': '...',
    '\xa0': ' ', '\u200b': '', '\ufeff': '',
    'é': 'e', 'ö': 'o', 'ü': 'u', 'ä': 'a',
    '∎': 'QED',
}

for fname in sorted(os.listdir(src)):
    if not fname.endswith('.lean'):
        continue
    with open(os.path.join(src, fname), 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in char_map.items():
        content = content.replace(old, new)
    
    # Replace any remaining non-ASCII
    cleaned = []
    for ch in content:
        if ord(ch) < 128:
            cleaned.append(ch)
        else:
            cleaned.append('?')
    content = ''.join(cleaned)
    
    with open(os.path.join(dst, fname), 'w', encoding='ascii') as f:
        f.write(content)

print(f'Sanitized {len([f for f in os.listdir(dst) if f.endswith(".lean")])} files')
