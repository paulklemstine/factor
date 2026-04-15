#!/usr/bin/env python3
"""Build the complete LaTeX book from markdown chapters."""

import os
import re
import sys

sys.path.insert(0, '/workspace/request-project')
from md_to_latex import md_to_latex, get_chapter_images, get_image_caption

BASE = '/workspace/request-project'

def sanitize_lean_code(code):
    """Replace Unicode characters in Lean code with ASCII equivalents for lstlisting."""
    replacements = {
        '←': '<-', '→': '->', '⟨': '<', '⟩': '>',
        '∀': 'forall ', '∃': 'exists ', 'λ': 'fun ',
        'α': 'alpha', 'β': 'beta', 'γ': 'gamma', 'δ': 'delta',
        'ε': 'epsilon', 'ζ': 'zeta', 'η': 'eta', 'θ': 'theta',
        'ι': 'iota', 'κ': 'kappa', 'μ': 'mu', 'ν': 'nu',
        'ξ': 'xi', 'π': 'pi', 'ρ': 'rho', 'σ': 'sigma',
        'τ': 'tau', 'φ': 'phi', 'χ': 'chi', 'ψ': 'psi', 'ω': 'omega',
        'Α': 'Alpha', 'Β': 'Beta', 'Γ': 'Gamma', 'Δ': 'Delta',
        'Σ': 'Sigma', 'Π': 'Pi', 'Ω': 'Omega', 'Φ': 'Phi', 'Ψ': 'Psi',
        'ℕ': 'Nat', 'ℤ': 'Int', 'ℝ': 'Real', 'ℚ': 'Rat', 'ℂ': 'Complex',
        '≤': '<=', '≥': '>=', '≠': '!=', '≡': '==',
        '∧': '/\\', '∨': '\\/', '¬': 'not ',
        '⊢': '|-', '⊣': '-|', '⊥': 'False', '⊤': 'True',
        '×': 'x', '∘': '.', '·': '*', '•': '*',
        '₁': '1', '₂': '2', '₃': '3', '₄': '4', '₅': '5',
        '₆': '6', '₇': '7', '₈': '8', '₉': '9', '₀': '0',
        '⁻': '^-', '⁺': '^+',
        '▸': '>', '▹': '>',
        '∣': '|', '∤': '!|',
        '⬝': '[]', '□': '[]',
        '↦': '|->',
        '⇒': '=>', '⟹': '=>',
        '↔': '<->',
        '∅': 'empty',
        '∞': 'infinity',
        '∑': 'sum', '∏': 'prod',
        '∈': 'in', '∉': 'notin',
        '⊂': 'subset', '⊆': 'subseteq', '⊇': 'supseteq',
        '∩': 'inter', '∪': 'union',
        '⊕': '+', '⊗': '*',
        '√': 'sqrt',
        '∎': '--QED',
        '★': '*',
        '❌': 'X',
        '✓': 'ok',
        '✗': 'X',
        '…': '...',
        '—': '--',
        '–': '-',
        '\u200b': '',  # zero-width space
        '\ufeff': '',  # BOM
    }
    for k, v in replacements.items():
        code = code.replace(k, v)
    # Remove any remaining non-ASCII characters
    code = code.encode('ascii', 'replace').decode('ascii')
    return code

# Chapter titles and subtitles
chapters = [
    (1, "The Tree That Grew Triangles", ""),
    (2, "The Tree That Grew Into a Lattice", "How an Ancient Algorithm and a Family Tree of Right Triangles Turned Out to Be the Same Thing"),
    (3, "Hyperbolic Shortcuts: How Pythagoras Learned to Factor", ""),
    (4, "Three Roads from Pythagoras", "How the World's Oldest Equation Secretly Cracks the World's Hardest Codes"),
    (5, "The Tree That Knew It Was a Spacetime", "How Three Matrices, a Quadratic Form, and a Pell Equation Reveal That Pythagorean Triples Live in Einstein's Universe"),
    (6, "The Lock with Seven Keyholes", "How Pythagorean Quintuplets, Sextuplets, and Octuplets Crack Composite Numbers Wide Open"),
    (7, "The One-Way Corridor", "Why Quantum Shortcuts Aren't Where You'd Expect"),
    (8, "The Price of Descent", "How Hard Is It to Factor by Climbing a Tree?"),
    (9, "The Four-Rung Ladder: A Journey Through the Doubling Algebras", ""),
    (10, "The Margin That Shook the World", "How a Scribbled Note Launched Three Centuries of Mathematics --- and Why the Proof Would Never Have Fit"),
    (11, "The Magnificent Sieve", "How Squares Conspire to Break Numbers Apart"),
    (12, "The Fourth Dimension of Pythagoras", "How Quadruples Crack Numbers"),
    (13, "The GCD Cascade", "Cracking Numbers Open with Pythagorean Channels"),
    (14, "The Tree That Cracks Numbers", "How a Babylonian Equation Grows a Forest That Can Split Integers Apart"),
    (15, "The Algebra Where Two Plus Three Equals Two", "Tropical Geometry and the Shortest-Path Semiring"),
    (16, "The Relativistic Secret of Right Triangles", ""),
]

def build_chapter_latex(num, title, subtitle):
    """Build LaTeX for one chapter."""
    md_path = os.path.join(BASE, f'Chapter{num}', f'Chapter{num}.md')
    with open(md_path, 'r') as f:
        md = f.read()
    
    # Convert markdown to LaTeX body
    body = md_to_latex(md, chapter_num=num)
    
    # Get images
    img_dir = os.path.join(BASE, f'Chapter{num}', 'images')
    images = get_chapter_images(os.path.join(BASE, f'Chapter{num}'))
    
    # Build chapter header
    lines = []
    if subtitle:
        lines.append(f'\\chapter[{title}]{{{title}}}')
        lines.append(f'\\vspace{{-0.5em}}')
        lines.append(f'\\begin{{center}}\\textit{{{subtitle}}}\\end{{center}}')
        lines.append(f'\\vspace{{1em}}')
    else:
        lines.append(f'\\chapter{{{title}}}')
    
    lines.append('')
    lines.append(body)
    
    # Add figures at end of chapter (select key figures)
    if images:
        lines.append('')
        lines.append('\\clearpage')
        # Include up to 4 key figures per chapter
        selected = images[:4] if len(images) > 4 else images
        for img_file in selected:
            caption = get_image_caption(img_file)
            img_path = f'Chapter{num}/images/{img_file}'
            lines.append(f'\\begin{{figure}}[htbp]')
            lines.append(f'  \\centering')
            lines.append(f'  \\includegraphics[width=0.85\\textwidth,keepaspectratio]{{{img_path}}}')
            lines.append(f'  \\caption{{{caption}}}')
            lines.append(f'\\end{{figure}}')
            lines.append('')
    
    return '\n'.join(lines)


def build_intro_latex():
    """Build LaTeX for introduction."""
    md_path = os.path.join(BASE, 'Introduction', 'Introduction.md')
    with open(md_path, 'r') as f:
        md = f.read()
    body = md_to_latex(md, is_intro=True)
    
    images = get_chapter_images(os.path.join(BASE, 'Introduction'))
    
    lines = []
    lines.append('\\chapter*{Introduction: The Triangle That Swallowed the Universe}')
    lines.append('\\addcontentsline{toc}{chapter}{Introduction: The Triangle That Swallowed the Universe}')
    lines.append('\\markboth{Introduction}{Introduction}')
    lines.append('')
    lines.append(body)
    
    if images:
        lines.append('\\clearpage')
        for img_file in images[:3]:
            caption = get_image_caption(img_file)
            img_path = f'Introduction/images/{img_file}'
            lines.append(f'\\begin{{figure}}[htbp]')
            lines.append(f'  \\centering')
            lines.append(f'  \\includegraphics[width=0.85\\textwidth,keepaspectratio]{{{img_path}}}')
            lines.append(f'  \\caption{{{caption}}}')
            lines.append(f'\\end{{figure}}')
            lines.append('')
    
    return '\n'.join(lines)


def build_conclusion_latex():
    """Build LaTeX for conclusion."""
    md_path = os.path.join(BASE, 'Conclusion', 'Conclusion.md')
    with open(md_path, 'r') as f:
        md = f.read()
    body = md_to_latex(md, is_conclusion=True)
    
    images = get_chapter_images(os.path.join(BASE, 'Conclusion'))
    
    lines = []
    lines.append('\\chapter*{Conclusion: The Rosetta Stone}')
    lines.append('\\addcontentsline{toc}{chapter}{Conclusion: The Rosetta Stone}')
    lines.append('\\markboth{Conclusion}{Conclusion}')
    lines.append('')
    lines.append(body)
    
    if images:
        lines.append('\\clearpage')
        for img_file in images[:3]:
            caption = get_image_caption(img_file)
            img_path = f'Conclusion/images/{img_file}'
            lines.append(f'\\begin{{figure}}[htbp]')
            lines.append(f'  \\centering')
            lines.append(f'  \\includegraphics[width=0.85\\textwidth,keepaspectratio]{{{img_path}}}')
            lines.append(f'  \\caption{{{caption}}}')
            lines.append(f'\\end{{figure}}')
            lines.append('')
    
    return '\n'.join(lines)


def build_lean_appendix():
    """Build LaTeX for the Lean code appendix."""
    lean_dir = os.path.join(BASE, 'lean')
    lean_files = sorted([f for f in os.listdir(lean_dir) if f.endswith('.lean')])
    
    lines = []
    lines.append('\\chapter*{Appendix: Formal Lean~4 Proofs}')
    lines.append('\\addcontentsline{toc}{chapter}{Appendix: Formal Lean~4 Proofs}')
    lines.append('\\markboth{Appendix: Lean Proofs}{Appendix: Lean Proofs}')
    lines.append('')
    lines.append('The following Lean~4 source files provide machine-verified formalizations of the key theorems discussed throughout this book. These proofs were developed using the Lean~4 theorem prover with the Mathlib library.')
    lines.append('')
    
    for lean_file in lean_files:
        filepath = os.path.join(lean_dir, lean_file)
        with open(filepath, 'r') as f:
            code = f.read()
        
        # Clean filename for section title
        title = lean_file.replace('.lean', '').replace('_', ' ')
        # Remove leading number
        title = re.sub(r'^\d+\s+', '', title)
        
        safe_name = lean_file.replace('_', '\\_')
        lines.append(f'\\section*{{{safe_name}}}')
        lines.append(f'\\addcontentsline{{toc}}{{section}}{{{safe_name}}}')
        lines.append('')
        lines.append('\\begin{lstlisting}[style=lean]')
        # Replace Unicode characters that lstlisting can't handle
        code = sanitize_lean_code(code)
        lines.append(code)
        lines.append('\\end{lstlisting}')
        lines.append('')
        lines.append('\\clearpage')
        lines.append('')
    
    return '\n'.join(lines)


def build_index_entries():
    """Generate index entries by scanning all chapter content."""
    # Key terms to index
    terms = {
        'Pythagorean triple': 'Pythagorean triple',
        'Pythagorean triples': 'Pythagorean triple',
        'Berggren tree': 'Berggren tree',
        'Berggren': 'Berggren tree',
        'Lorentz': 'Lorentz group',
        'Lorentz group': 'Lorentz group',
        'Minkowski': 'Minkowski metric',
        'null cone': 'null cone',
        'light cone': 'light cone',
        'Euclidean algorithm': 'Euclidean algorithm',
        'Euclid': 'Euclid',
        'Pell equation': 'Pell equation',
        'quadratic form': 'quadratic form',
        'semiprime': 'semiprime',
        'factoring': 'factoring',
        'factorization': 'factorization',
        'RSA': 'RSA cryptography',
        'cryptography': 'cryptography',
        'quaternion': 'quaternions',
        'quaternions': 'quaternions',
        'octonion': 'octonions',
        'octonions': 'octonions',
        'Cayley-Dickson': 'Cayley--Dickson construction',
        'Fermat': "Fermat's Last Theorem",
        "Fermat's Last Theorem": "Fermat's Last Theorem",
        'infinite descent': 'infinite descent',
        'descent': 'descent',
        'congruence of squares': 'congruence of squares',
        'quadratic sieve': 'quadratic sieve',
        'number field sieve': 'number field sieve',
        'Brahmagupta': 'Brahmagupta--Fibonacci identity',
        'Fibonacci': 'Fibonacci',
        'Euler': 'Euler',
        'Wiles': 'Wiles, Andrew',
        'elliptic curve': 'elliptic curves',
        'modular form': 'modular forms',
        'Gaussian integer': 'Gaussian integers',
        'Eisenstein integer': 'Eisenstein integers',
        'tropical geometry': 'tropical geometry',
        'tropical': 'tropical geometry',
        'LLL algorithm': 'LLL algorithm',
        'lattice': 'lattice',
        'lattice reduction': 'lattice reduction',
        'Grover': "Grover's algorithm",
        'quantum': 'quantum computing',
        'GCD': 'greatest common divisor (GCD)',
        'greatest common divisor': 'greatest common divisor (GCD)',
        'Plimpton 322': 'Plimpton 322',
        'Babylon': 'Babylon',
        'Babylonian': 'Babylon',
        'Chebyshev': 'Chebyshev polynomials',
        'Poincaré': 'Poincar\\\'e disk',
        'hyperbolic': 'hyperbolic geometry',
        'continued fraction': 'continued fractions',
        'Gauss': 'Gauss, Carl Friedrich',
        'Hamilton': 'Hamilton, William Rowan',
        'Jacobi': 'Jacobi',
        'Sophie Germain': 'Germain, Sophie',
        'unique factorization': 'unique factorization',
        'norm': 'norm (algebraic)',
        'determinant': 'determinant',
        'matrix': 'matrix',
        'ternary tree': 'ternary tree',
        'gnomon': 'gnomon',
        'Bellman': 'Bellman equation',
        'shortest path': 'shortest path problem',
        'complexity': 'computational complexity',
        'trial division': 'trial division',
    }
    return terms


# Now build the main LaTeX document
def build_main_tex():
    """Build the complete main.tex file."""
    
    # Preamble
    preamble = r"""\documentclass[11pt,twoside,openright]{book}

% Page geometry - 6x9 inch trim size (standard book)
\usepackage[
  paperwidth=6in,
  paperheight=9in,
  inner=0.875in,
  outer=0.625in,
  top=0.75in,
  bottom=0.875in,
  headheight=14pt,
  headsep=0.3in,
  footskip=0.4in
]{geometry}

% Typography
\usepackage[T1]{fontenc}
\usepackage{ebgaramond}
\usepackage[scaled=0.85]{beramono}
\usepackage{microtype}

% Math
\usepackage{amsmath,amssymb,amsthm,mathtools}

% Graphics
\usepackage{graphicx}
\usepackage[dvipsnames,svgnames]{xcolor}

% Headers and footers
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE]{\small\scshape\leftmark}
\fancyhead[RO]{\small\scshape\rightmark}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0pt}

\fancypagestyle{plain}{
  \fancyhf{}
  \fancyfoot[C]{\thepage}
  \renewcommand{\headrulewidth}{0pt}
}

% Chapter styling
\usepackage{titlesec}
\titleformat{\chapter}[display]
  {\normalfont\huge\bfseries\color{MidnightBlue}}
  {\chaptertitlename\ \thechapter}{20pt}{\Huge}
\titleformat{name=\chapter,numberless}[display]
  {\normalfont\huge\bfseries\color{MidnightBlue}}
  {}{0pt}{\Huge}
\titlespacing*{\chapter}{0pt}{-20pt}{30pt}

% Section styling
\titleformat{\section}
  {\normalfont\Large\bfseries\color{MidnightBlue!80!black}}
  {\thesection}{1em}{}
\titleformat{\subsection}
  {\normalfont\large\bfseries\color{MidnightBlue!60!black}}
  {\thesubsection}{1em}{}

% Code listings for Lean
\usepackage{listings}
\lstdefinestyle{lean}{
  basicstyle=\ttfamily\scriptsize,
  breaklines=true,
  breakatwhitespace=false,
  columns=flexible,
  keepspaces=true,
  frame=single,
  framesep=4pt,
  rulecolor=\color{gray!40},
  backgroundcolor=\color{gray!5},
  numbers=left,
  numberstyle=\tiny\color{gray},
  numbersep=6pt,
  tabsize=2,
  showstringspaces=false,
  literate={←}{$\leftarrow$}1 {→}{$\rightarrow$}1 {⟨}{$\langle$}1 {⟩}{$\rangle$}1 {∀}{$\forall$}1 {∃}{$\exists$}1 {λ}{$\lambda$}1 {α}{$\alpha$}1 {β}{$\beta$}1 {γ}{$\gamma$}1 {ε}{$\varepsilon$}1 {ℕ}{$\mathbb{N}$}1 {ℤ}{$\mathbb{Z}$}1 {ℝ}{$\mathbb{R}$}1 {ℚ}{$\mathbb{Q}$}1 {≤}{$\leq$}1 {≥}{$\geq$}1 {≠}{$\neq$}1 {⊢}{$\vdash$}1 {∧}{$\wedge$}1 {∨}{$\vee$}1 {¬}{$\neg$}1 {×}{$\times$}1 {⬝}{$\square$}1 {∘}{$\circ$}1 {·}{$\cdot$}1 {₁}{$_1$}1 {₂}{$_2$}1 {₃}{$_3$}1 {⁻}{$^{-}$}1 {▸}{$\blacktriangleright$}1,
  escapeinside={(*@}{@*)},
}

% Table of contents depth
\setcounter{tocdepth}{1}
\setcounter{secnumdepth}{2}

% Index
\usepackage{makeidx}
\makeindex

% Hyperlinks
\usepackage[
  colorlinks=true,
  linkcolor=MidnightBlue,
  citecolor=MidnightBlue,
  urlcolor=MidnightBlue,
  bookmarks=true,
  bookmarksnumbered=true,
  pdfstartview=FitH
]{hyperref}

% Better float placement
\usepackage{float}
\usepackage[font=small,labelfont=bf,textfont=it]{caption}

% Epigraphs
\usepackage{epigraph}
\setlength{\epigraphwidth}{0.75\textwidth}

% Drop caps
\usepackage{lettrine}

% Ornamental breaks
\newcommand{\ornbreak}{\begin{center}\pgfornament[width=2cm]{88}\end{center}}
\newcommand{\simplebreak}{\begin{center}$\ast\quad\ast\quad\ast$\end{center}}

% Theorem environments
\theoremstyle{definition}
\newtheorem{theorem}{Theorem}[chapter]
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{corollary}[theorem]{Corollary}
\newtheorem{definition}[theorem]{Definition}

\theoremstyle{remark}
\newtheorem{remark}[theorem]{Remark}
\newtheorem{example}[theorem]{Example}

% PDF metadata
\hypersetup{
  pdftitle={The Triangle That Swallowed the Universe},
  pdfauthor={Paul Klemstine},
  pdfsubject={Mathematics},
  pdfkeywords={Pythagorean triples, number theory, Lorentz group, factoring, Berggren tree}
}

% Custom colors
\definecolor{ChapterGold}{RGB}{180,140,20}
\definecolor{DeepBlue}{RGB}{20,40,100}

\begin{document}

% =================================================================
% FRONT MATTER
% =================================================================
\frontmatter

% Half-title page
\thispagestyle{empty}
\vspace*{\fill}
\begin{center}
  {\Huge\bfseries\color{MidnightBlue} The Triangle That\\[0.3em] Swallowed the Universe}
\end{center}
\vspace*{\fill}
\clearpage

% Blank page
\thispagestyle{empty}
\mbox{}
\clearpage

% Full title page
\thispagestyle{empty}
\vspace*{1.5in}
\begin{center}
  {\fontsize{32}{38}\selectfont\bfseries\color{MidnightBlue} The Triangle That\\[0.4em] Swallowed the Universe}\\[1.5em]
  {\Large\itshape From Pythagoras to Einstein:\\[0.3em]
  How the World's Oldest Equation\\[0.3em]
  Secretly Rules Mathematics}\\[3em]
  {\LARGE Paul Klemstine}\\[4em]
  \rule{2in}{0.5pt}
\end{center}
\vspace*{\fill}
\clearpage

% Copyright page
\thispagestyle{empty}
\vspace*{\fill}
\begin{small}
\noindent\textbf{The Triangle That Swallowed the Universe}\\[0.5em]
\noindent Copyright \copyright\ 2025 Paul Klemstine. All rights reserved.\\[1em]
\noindent No part of this publication may be reproduced, distributed, or transmitted in any form or by any means, including photocopying, recording, or other electronic or mechanical methods, without the prior written permission of the author, except in the case of brief quotations embodied in critical reviews and certain other noncommercial uses permitted by copyright law.\\[1.5em]
\noindent The Lean~4 source code included in the Appendix is provided under the Apache License 2.0.\\[1.5em]
\noindent\textbf{ISBN 978-1-105-41110-6}\\[1.5em]
\noindent First Edition, 2025\\[0.5em]
\noindent Typeset in EB Garamond using \LaTeX.\\[0.5em]
\noindent Cover design by the author.\\[0.5em]
\noindent Illustrations generated with Python, Matplotlib, and Pillow.\\[2em]
\noindent Printed in the United States of America.\\[1em]
\noindent\begin{center}
  \includegraphics[width=1.5in]{ISBN/978-1-105-41110-6.png}
\end{center}
\end{small}
\vspace*{\fill}
\clearpage

% Dedication page
\thispagestyle{empty}
\vspace*{\fill}
\begin{center}
  {\Large\itshape Soli Deo Gloria}
\end{center}
\vspace*{\fill}
\clearpage

% Blank page after dedication
\thispagestyle{empty}
\mbox{}
\clearpage

% Table of Contents
\tableofcontents
\clearpage

"""

    # Build all chapter content
    chapter_content = []
    
    # Introduction
    intro = build_intro_latex()
    
    # Main chapters
    ch_texts = []
    for num, title, subtitle in chapters:
        ch_texts.append(build_chapter_latex(num, title, subtitle))
    
    # Conclusion
    conclusion = build_conclusion_latex()
    
    # Lean appendix
    appendix = build_lean_appendix()
    
    # Main matter
    main_matter = r"""
% =================================================================
% MAIN MATTER
% =================================================================
\mainmatter

"""
    main_matter += intro + '\n\n'
    
    for ch_text in ch_texts:
        main_matter += ch_text + '\n\n'
    
    main_matter += conclusion + '\n\n'
    
    # Back matter
    back_matter = r"""
% =================================================================
% BACK MATTER
% =================================================================
\backmatter

"""
    back_matter += appendix + '\n\n'
    
    # Index
    back_matter += r"""
% Index
\clearpage
\printindex

"""
    
    # Final page with ISBN barcode
    back_matter += r"""
% Final page with ISBN barcode
\clearpage
\thispagestyle{empty}
\vspace*{\fill}
\begin{center}
  \includegraphics[width=2in]{ISBN/978-1-105-41110-6.png}\\[0.5em]
  {\small ISBN 978-1-105-41110-6}
\end{center}
\vspace*{\fill}

\end{document}
"""
    
    full_doc = preamble + main_matter + back_matter
    return full_doc


if __name__ == '__main__':
    tex = build_main_tex()
    output_path = os.path.join(BASE, 'book.tex')
    with open(output_path, 'w') as f:
        f.write(tex)
    print(f"Written {len(tex)} chars to {output_path}")
