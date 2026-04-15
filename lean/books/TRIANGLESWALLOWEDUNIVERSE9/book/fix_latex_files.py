#!/usr/bin/env python3
"""Fix Unicode in converted LaTeX files - global replacement approach.
   This script should be run AFTER convert_md_to_latex.py and add_index_entries.py."""
import os, re, glob

# Use \\ensuremath for math symbols so they work in both text and math mode
replacements = {
    '\u2115': '\\ensuremath{\\mathbb{N}}',   # ℕ
    '\u2124': '\\ensuremath{\\mathbb{Z}}',   # ℤ
    '\u211a': '\\ensuremath{\\mathbb{Q}}',   # ℚ
    '\u211d': '\\ensuremath{\\mathbb{R}}',   # ℝ
    '\u2102': '\\ensuremath{\\mathbb{C}}',   # ℂ
    '\u210d': '\\ensuremath{\\mathbb{H}}',   # ℍ
    '\u2192': '\\ensuremath{\\to}',          # →
    '\u2190': '\\ensuremath{\\leftarrow}',   # ←
    '\u2194': '\\ensuremath{\\leftrightarrow}', # ↔
    '\u21d2': '\\ensuremath{\\Rightarrow}',  # ⇒
    '\u21d0': '\\ensuremath{\\Leftarrow}',   # ⇐
    '\u2200': '\\ensuremath{\\forall}',      # ∀
    '\u2203': '\\ensuremath{\\exists}',      # ∃
    '\u2264': '\\ensuremath{\\leq}',         # ≤
    '\u2265': '\\ensuremath{\\geq}',         # ≥
    '\u2260': '\\ensuremath{\\neq}',         # ≠
    '\u2227': '\\ensuremath{\\wedge}',       # ∧
    '\u2228': '\\ensuremath{\\vee}',         # ∨
    '\u00ac': '\\ensuremath{\\neg}',         # ¬
    '\u22a2': '\\ensuremath{\\vdash}',       # ⊢
    '\u2208': '\\ensuremath{\\in}',          # ∈
    '\u2209': '\\ensuremath{\\notin}',       # ∉
    '\u2286': '\\ensuremath{\\subseteq}',    # ⊆
    '\u2282': '\\ensuremath{\\subset}',      # ⊂
    '\u222a': '\\ensuremath{\\cup}',         # ∪
    '\u2229': '\\ensuremath{\\cap}',         # ∩
    '\u00d7': '\\ensuremath{\\times}',       # ×
    '\u00b7': '\\ensuremath{\\cdot}',        # ·
    '\u2218': '\\ensuremath{\\circ}',        # ∘
    '\u2605': '\\ensuremath{\\star}',        # ★
    '\u2713': '\\ensuremath{\\checkmark}',   # ✓
    '\u2717': '\\ensuremath{\\times}',       # ✗
    '\u274c': '\\ensuremath{\\times}',       # ❌
    '\u220e': '\\ensuremath{\\blacksquare}', # ∎
    '\u221e': '\\ensuremath{\\infty}',       # ∞
    '\u2248': '\\ensuremath{\\approx}',      # ≈
    '\u00b1': '\\ensuremath{\\pm}',          # ±
    '\u00f7': '\\ensuremath{\\div}',         # ÷
    '\u2295': '\\ensuremath{\\oplus}',       # ⊕
    '\u2297': '\\ensuremath{\\otimes}',      # ⊗
    '\u2223': '\\ensuremath{\\mid}',         # ∣
    '\u2020': '\\ensuremath{\\dagger}',      # †
    '\u27e8': '\\ensuremath{\\langle}',      # ⟨
    '\u27e9': '\\ensuremath{\\rangle}',      # ⟩
    '\u1d40': '\\ensuremath{^{\\mathsf{T}}}', # ᵀ
    '\u2016': '\\ensuremath{\\|}',           # ‖
    '\u2211': '\\ensuremath{\\sum}',         # ∑
    '\u220f': '\\ensuremath{\\prod}',        # ∏
    '\u2202': '\\ensuremath{\\partial}',     # ∂
    '\u2207': '\\ensuremath{\\nabla}',       # ∇
    '\u22a5': '\\ensuremath{\\bot}',         # ⊥
    '\u22a4': '\\ensuremath{\\top}',         # ⊤
    '\u27f9': '\\ensuremath{\\Longrightarrow}',
    '\u27f8': '\\ensuremath{\\Longleftarrow}',
    '\u27fa': '\\ensuremath{\\Longleftrightarrow}',
    '\u2261': '\\ensuremath{\\equiv}',       # ≡
    '\u2245': '\\ensuremath{\\cong}',        # ≅
    '\u223c': '\\ensuremath{\\sim}',         # ∼
    '\u2243': '\\ensuremath{\\simeq}',       # ≃
    # Greek
    '\u03b1': '\\ensuremath{\\alpha}',
    '\u03b2': '\\ensuremath{\\beta}',
    '\u03b3': '\\ensuremath{\\gamma}',
    '\u03b4': '\\ensuremath{\\delta}',
    '\u03b5': '\\ensuremath{\\varepsilon}',
    '\u03b6': '\\ensuremath{\\zeta}',
    '\u03b7': '\\ensuremath{\\eta}',
    '\u03b8': '\\ensuremath{\\theta}',
    '\u03b9': '\\ensuremath{\\iota}',
    '\u03ba': '\\ensuremath{\\kappa}',
    '\u03bb': '\\ensuremath{\\lambda}',
    '\u03bc': '\\ensuremath{\\mu}',
    '\u03bd': '\\ensuremath{\\nu}',
    '\u03be': '\\ensuremath{\\xi}',
    '\u03c0': '\\ensuremath{\\pi}',
    '\u03c1': '\\ensuremath{\\rho}',
    '\u03c3': '\\ensuremath{\\sigma}',
    '\u03c4': '\\ensuremath{\\tau}',
    '\u03c5': '\\ensuremath{\\upsilon}',
    '\u03c6': '\\ensuremath{\\varphi}',
    '\u03c7': '\\ensuremath{\\chi}',
    '\u03c8': '\\ensuremath{\\psi}',
    '\u03c9': '\\ensuremath{\\omega}',
    '\u0393': '\\ensuremath{\\Gamma}',
    '\u0394': '\\ensuremath{\\Delta}',
    '\u0398': '\\ensuremath{\\Theta}',
    '\u039b': '\\ensuremath{\\Lambda}',
    '\u03a3': '\\ensuremath{\\Sigma}',
    '\u03a0': '\\ensuremath{\\Pi}',
    '\u03a6': '\\ensuremath{\\Phi}',
    '\u03a8': '\\ensuremath{\\Psi}',
    '\u03a9': '\\ensuremath{\\Omega}',
    # Typography
    '\u2026': '\\ldots{}',     # …
    '\u2014': '---',           # —
    '\u2013': '--',            # –
    '\u2018': "`",             # '
    '\u2019': "'",             # '
    '\u201c': "``",            # "
    '\u201d': "''",            # "
    '\u2022': '\\ensuremath{\\bullet}', # •
    '\u00a0': '~',             # NBSP
    # Diacritics
    '\u00e9': "\\'e",
    '\u00e8': "\\`e",
    '\u00ea': "\\^e",
    '\u00eb': '\\"e',
    '\u00f6': '\\"o',
    '\u00fc': '\\"u',
    '\u00e4': '\\"a',
    '\u00f1': '\\~n',
    '\u0101': '\\={a}',
    '\u012b': '\\={\\i}',
    '\u1e6d': '{\\d{t}}',
    '\u015b': "\\'s",
    '\u016b': '\\={u}',
    '\u0100': '\\={A}',
    '\u1e43': '{\\d{m}}',
    '\u1e47': '{\\d{n}}',
    '\u1e25': '{\\d{h}}',
    '\u1e63': '{\\d{s}}',
    '\u1e45': '{\\d{n}}',
    '\u00e0': '\\`a',
    '\u00e1': "\\'a",
    '\u00ed': "\\'\\i{}",
    '\u00f3': "\\'o",
    '\u00fa': "\\'u",
    '\u00e7': '\\c{c}',
}

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    # Remove any remaining non-ASCII
    cleaned = []
    for ch in content:
        if ord(ch) < 128:
            cleaned.append(ch)
        else:
            cleaned.append('?')
    content = ''.join(cleaned)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

book_dir = '/workspace/request-project/book'
for texfile in sorted(glob.glob(os.path.join(book_dir, '*.tex'))):
    basename = os.path.basename(texfile)
    if basename in ('main.tex', 'appendix_lean.tex', 'test_chapter.tex'):
        continue
    fix_file(texfile)
    print(f'Fixed {basename}')

print('Done.')
