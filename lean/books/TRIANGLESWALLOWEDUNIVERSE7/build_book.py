#!/usr/bin/env python3
"""Build the complete LaTeX book from markdown sources."""
import os, sys, re, glob
sys.path.insert(0, '/workspace/request-project')
from md2tex import process_chapter

BASE = '/workspace/request-project'

def get_chapter_title(chapter_num):
    """Extract chapter title from markdown."""
    md_file = os.path.join(BASE, f'Chapter{chapter_num}', f'Chapter{chapter_num}.md')
    with open(md_file) as f:
        first_line = f.readline().strip()
    # Extract title: # Chapter N — *Title*
    m = re.match(r'^#\s+Chapter\s+\d+\s*[—–-]\s*\*?(.+?)\*?\s*$', first_line)
    if m:
        return m.group(1).strip('* ')
    m = re.match(r'^#\s+(.+)', first_line)
    if m:
        return m.group(1).strip('* ')
    return f'Chapter {chapter_num}'

def get_chapter_subtitle(chapter_num):
    """Extract subtitle if present."""
    md_file = os.path.join(BASE, f'Chapter{chapter_num}', f'Chapter{chapter_num}.md')
    with open(md_file) as f:
        lines = f.readlines()
    for line in lines[1:5]:
        m = re.match(r'^###\s+\*(.+?)\*', line.strip())
        if m:
            return m.group(1)
    return None

def build_lean_appendix():
    """Generate LaTeX for the Lean code appendix."""
    lean_dir = os.path.join(BASE, 'lean')
    files = sorted(glob.glob(os.path.join(lean_dir, '*.lean')))
    
    output = []
    output.append(r'\chapter*{Appendix: Formal Proofs in Lean 4}')
    output.append(r'\addcontentsline{toc}{chapter}{Appendix: Formal Proofs in Lean 4}')
    output.append(r'\markboth{Appendix: Lean Proofs}{Appendix: Lean Proofs}')
    output.append('')
    output.append(r'\index{Lean 4}')
    output.append(r'\index{formal verification}')
    output.append('')
    output.append(r"""The following Lean~4 source files contain machine-verified formalizations
of the key theorems developed in this book. Each file corresponds to one or more
chapters and captures the essential mathematical content in a language that a
computer can check for logical correctness. The proofs were developed using the
Mathlib library for Lean~4.""")
    output.append('')
    output.append(r'\bigskip')
    output.append('')
    
    for fpath in files:
        fname = os.path.basename(fpath)
        # Clean name for section title
        name = fname.replace('.lean', '').replace('_', r'\_')
        # Make a readable title
        readable = fname.replace('.lean', '').replace('_', ' ')
        # Remove leading number
        readable = re.sub(r'^\d+\s+', '', readable)
        
        output.append(f'\\section*{{{name}}}')
        output.append(f'\\addcontentsline{{toc}}{{section}}{{{readable}}}')
        output.append(f'\\index{{{readable}}}')
        output.append('')
        
        with open(fpath) as f:
            code = f.read()
        
        # Use lstlisting for code
        output.append(r'\begin{lstlisting}[style=lean]')
        output.append(code)
        output.append(r'\end{lstlisting}')
        output.append('')
        output.append(r'\clearpage')
        output.append('')
    
    return '\n'.join(output)

def build_index_entries():
    """Generate additional index entries to sprinkle through the document."""
    # These will be added via the converter's heading extraction
    # Here we define key terms that should be indexed
    return [
        "Pythagorean triple", "Berggren tree", "Lorentz group",
        "Euclid", "Fermat", "descent", "factoring", "semiprime",
        "quadratic form", "null cone", "Pell equation", "quaternion",
        "octonion", "Cayley-Dickson", "congruence of squares",
        "tropical geometry", "GCD", "lattice", "hyperbolic geometry",
        "Plimpton 322", "Brahmagupta", "Fibonacci", "Euler",
        "Wiles", "modularity", "elliptic curve",
    ]

def main():
    chapters_tex = []
    
    # Process introduction
    print("Processing Introduction...")
    intro_tex = process_chapter(os.path.join(BASE, 'Introduction'), is_intro=True)
    
    # Process chapters 1-16
    for ch in range(1, 17):
        print(f"Processing Chapter {ch}...")
        title = get_chapter_title(ch)
        subtitle = get_chapter_subtitle(ch)
        
        ch_tex = []
        ch_tex.append(f'\\chapter{{\\textit{{{title}}}}}')
        if subtitle:
            ch_tex.append(f'\\begin{{quote}}\\textit{{{subtitle}}}\\end{{quote}}')
        ch_tex.append('')
        
        body = process_chapter(os.path.join(BASE, f'Chapter{ch}'), ch)
        # Remove the first # heading since we added \chapter above
        body_lines = body.split('\n')
        # Skip lines until we get past the chapter heading
        filtered = []
        skip_next_heading = True
        for line in body_lines:
            if skip_next_heading and (line.startswith('\\chapter') or line.startswith('\\markboth')):
                continue
            if skip_next_heading and line.startswith('\\addcontentsline{toc}{chapter}'):
                skip_next_heading = False
                continue
            filtered.append(line)
        
        ch_tex.append('\n'.join(filtered))
        chapters_tex.append('\n'.join(ch_tex))
    
    # Process conclusion
    print("Processing Conclusion...")
    conclusion_tex = process_chapter(os.path.join(BASE, 'Conclusion'), is_conclusion=True)
    
    # Build lean appendix
    print("Building Lean appendix...")
    lean_appendix = build_lean_appendix()
    
    # Assemble the full book
    print("Assembling book...")
    
    book = []
    book.append(PREAMBLE)
    book.append(r'\begin{document}')
    book.append('')
    
    # Front matter
    book.append(r'\frontmatter')
    book.append('')
    
    # Half title
    book.append(r'\thispagestyle{empty}')
    book.append(r'\vspace*{\stretch{1}}')
    book.append(r'\begin{center}')
    book.append(r'{\Huge\scshape The Triangle That\\[0.3em] Swallowed the Universe}')
    book.append(r'\end{center}')
    book.append(r'\vspace*{\stretch{2}}')
    book.append(r'\clearpage')
    book.append('')
    
    # Blank page
    book.append(r'\thispagestyle{empty}\mbox{}\clearpage')
    book.append('')
    
    # Full title page
    book.append(r'\thispagestyle{empty}')
    book.append(r'\vspace*{\stretch{1}}')
    book.append(r'\begin{center}')
    book.append(r'{\fontsize{36}{42}\selectfont\scshape The Triangle That\\[0.4em] Swallowed the Universe}')
    book.append(r'\vspace{1.5cm}')
    book.append(r'{\Large\itshape Pythagorean Triples, Lorentz Symmetry,\\[0.3em] and the Hidden Geometry of Numbers}')
    book.append(r'\vspace{3cm}')
    book.append(r'{\LARGE Paul Klemstine}')
    book.append(r'\end{center}')
    book.append(r'\vspace*{\stretch{2}}')
    book.append(r'\clearpage')
    book.append('')
    
    # Copyright page
    book.append(r'\thispagestyle{empty}')
    book.append(r'\vspace*{\stretch{1}}')
    book.append(r'\begin{center}')
    book.append(r'\small')
    book.append(r'Copyright \copyright\ 2025 Paul Klemstine\\[0.5em]')
    book.append(r'All rights reserved.\\[1em]')
    book.append(r'No part of this publication may be reproduced, distributed, or transmitted')
    book.append(r'in any form or by any means, including photocopying, recording, or other')
    book.append(r'electronic or mechanical methods, without the prior written permission of')
    book.append(r'the author, except in the case of brief quotations embodied in critical')
    book.append(r'reviews and certain other noncommercial uses permitted by copyright law.\\[1.5em]')
    book.append(r'\textbf{ISBN 978-1-105-41110-6}\\[1em]')
    book.append(r'\vspace{0.5cm}')
    book.append(r'\includegraphics[width=4cm]{ISBN/978-1-105-41110-6.png}\\[1.5em]')
    book.append(r'First Edition\\[0.5em]')
    book.append(r'Typeset in \LaTeX\\[0.5em]')
    book.append(r'Printed in the United States of America')
    book.append(r'\end{center}')
    book.append(r'\vspace*{\stretch{1}}')
    book.append(r'\clearpage')
    book.append('')
    
    # Dedication page
    book.append(r'\thispagestyle{empty}')
    book.append(r'\vspace*{\stretch{1}}')
    book.append(r'\begin{center}')
    book.append(r'{\Large\itshape Soli Deo Gloria}')
    book.append(r'\end{center}')
    book.append(r'\vspace*{\stretch{2}}')
    book.append(r'\clearpage')
    book.append('')
    
    # Blank page
    book.append(r'\thispagestyle{empty}\mbox{}\clearpage')
    book.append('')
    
    # Table of Contents
    book.append(r'\tableofcontents')
    book.append(r'\clearpage')
    book.append('')
    
    # Main matter
    book.append(r'\mainmatter')
    book.append('')
    
    # Introduction
    book.append(intro_tex)
    book.append(r'\clearpage')
    book.append('')
    
    # Chapters 1-16
    for i, ch_tex in enumerate(chapters_tex):
        book.append(ch_tex)
        book.append(r'\clearpage')
        book.append('')
    
    # Conclusion
    book.append(conclusion_tex)
    book.append(r'\clearpage')
    book.append('')
    
    # Back matter
    book.append(r'\backmatter')
    book.append('')
    
    # Lean appendix
    book.append(lean_appendix)
    
    # Index
    book.append(r'\clearpage')
    book.append(r'\printindex')
    book.append('')
    
    # Final page with ISBN barcode
    book.append(r'\clearpage')
    book.append(r'\thispagestyle{empty}')
    book.append(r'\vspace*{\stretch{1}}')
    book.append(r'\begin{center}')
    book.append(r'\includegraphics[width=5cm]{ISBN/978-1-105-41110-6.png}\\[0.5em]')
    book.append(r'{\small ISBN 978-1-105-41110-6}')
    book.append(r'\end{center}')
    book.append(r'\vspace*{\stretch{1}}')
    book.append('')
    
    book.append(r'\end{document}')
    
    full_text = '\n'.join(book)
    
    output_file = os.path.join(BASE, 'book.tex')
    with open(output_file, 'w') as f:
        f.write(full_text)
    
    print(f"Wrote {output_file} ({len(full_text)} bytes)")

PREAMBLE = r"""\documentclass[11pt,openany]{book}

% ===== PAGE GEOMETRY =====
% Standard 6x9 trade book
\usepackage[
  paperwidth=6in,
  paperheight=9in,
  inner=0.85in,
  outer=0.65in,
  top=0.75in,
  bottom=0.85in,
  headheight=14pt,
  headsep=0.3in,
  footskip=0.4in
]{geometry}

% ===== FONTS & ENCODING =====
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{microtype}

% ===== MATH =====
\usepackage{amsmath,amssymb,amsthm,mathtools}

% ===== GRAPHICS =====
\usepackage{graphicx}
\graphicspath{{./}}
\usepackage[dvipsnames,svgnames,x11names]{xcolor}

% ===== TABLES =====
\usepackage{booktabs}
\usepackage{array}

% ===== CODE LISTINGS (for Lean) =====
\usepackage{listings}
\lstdefinestyle{lean}{
  basicstyle=\ttfamily\scriptsize,
  breaklines=true,
  breakatwhitespace=false,
  columns=flexible,
  keepspaces=true,
  showstringspaces=false,
  frame=leftline,
  framerule=1.5pt,
  rulecolor=\color{RoyalBlue!40},
  backgroundcolor=\color{gray!5},
  xleftmargin=1em,
  aboveskip=0.8em,
  belowskip=0.8em,
  literate={←}{$\leftarrow$}1 {→}{$\rightarrow$}1 {↔}{$\leftrightarrow$}1
           {∀}{$\forall$}1 {∃}{$\exists$}1 {¬}{$\lnot$}1
           {≤}{$\leq$}1 {≥}{$\geq$}1 {≠}{$\neq$}1
           {∈}{$\in$}1 {∉}{$\notin$}1 {⊆}{$\subseteq$}1
           {∧}{$\wedge$}1 {∨}{$\vee$}1 {⊢}{$\vdash$}1
           {λ}{$\lambda$}1 {α}{$\alpha$}1 {β}{$\beta$}1
           {γ}{$\gamma$}1 {ε}{$\varepsilon$}1 {ℕ}{$\mathbb{N}$}1
           {ℤ}{$\mathbb{Z}$}1 {ℚ}{$\mathbb{Q}$}1 {ℝ}{$\mathbb{R}$}1
           {ℂ}{$\mathbb{C}$}1 {⟨}{$\langle$}1 {⟩}{$\rangle$}1
           {×}{$\times$}1 {∘}{$\circ$}1 {•}{$\bullet$}1
           {⁻¹}{$^{-1}$}2,
  morekeywords={theorem,lemma,def,definition,structure,class,instance,
    where,let,in,have,show,by,sorry,import,open,namespace,end,
    noncomputable,variable,example,section,private,protected,
    inductive,mutual,match,with,if,then,else,do,return,for,
    calc,simp,ring,omega,norm_num,exact,apply,intro,rfl,
    constructor,cases,induction,rw,rewrite,unfold,ext,funext,
    linarith,nlinarith,field_simp,push_neg,contrapose,
    suffices,obtain,rcases,rintro,use,refine,specialize},
  keywordstyle=\color{RoyalBlue}\bfseries,
  commentstyle=\color{OliveGreen}\itshape,
  stringstyle=\color{BrickRed},
  morecomment=[l]{--},
  morecomment=[s]{/-}{-/},
  morestring=[b]",
}

% ===== HEADERS & FOOTERS =====
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE]{\small\itshape\leftmark}
\fancyhead[RO]{\small\itshape\rightmark}
\fancyfoot[C]{\small\thepage}
\renewcommand{\headrulewidth}{0.3pt}
\renewcommand{\footrulewidth}{0pt}

% Plain pages (chapter openings)
\fancypagestyle{plain}{
  \fancyhf{}
  \fancyfoot[C]{\small\thepage}
  \renewcommand{\headrulewidth}{0pt}
}

% ===== CHAPTER STYLING =====
\usepackage{titlesec}
\titleformat{\chapter}[display]
  {\normalfont\huge\bfseries\filcenter}
  {\Large\scshape Chapter~\thechapter}
  {0.5em}
  {\Huge\itshape}
\titlespacing*{\chapter}{0pt}{-20pt}{30pt}

\titleformat{\section}
  {\normalfont\Large\bfseries}
  {\thesection}{1em}{}

\titleformat{\subsection}
  {\normalfont\large\itshape}
  {\thesubsection}{1em}{}

% ===== DROP CAPS =====
% (using manual approach for elegance)

% ===== INDEX =====
\usepackage{makeidx}
\makeindex

% ===== HYPERLINKS =====
\usepackage[
  hidelinks,
  bookmarksnumbered=true,
  bookmarksopen=true,
  bookmarksopenlevel=1,
  pdfauthor={Paul Klemstine},
  pdftitle={The Triangle That Swallowed the Universe},
  pdfsubject={Mathematics, Number Theory, Pythagorean Triples},
]{hyperref}

% ===== THEOREM ENVIRONMENTS =====
\theoremstyle{definition}
\newtheorem{definition}{Definition}[chapter]
\newtheorem{example}{Example}[chapter]
\theoremstyle{plain}
\newtheorem{theorem}{Theorem}[chapter]
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{corollary}[theorem]{Corollary}
\theoremstyle{remark}
\newtheorem{remark}{Remark}[chapter]

% ===== CUSTOM COMMANDS =====
\newcommand{\Z}{\mathbb{Z}}
\newcommand{\N}{\mathbb{N}}
\newcommand{\Q}{\mathbb{Q}}
\newcommand{\R}{\mathbb{R}}
\newcommand{\C}{\mathbb{C}}

% ===== WIDOW/ORPHAN CONTROL =====
\widowpenalty=10000
\clubpenalty=10000

% ===== FLOAT PLACEMENT =====
\renewcommand{\topfraction}{0.85}
\renewcommand{\bottomfraction}{0.70}
\renewcommand{\textfraction}{0.10}
\renewcommand{\floatpagefraction}{0.70}
\setcounter{totalnumber}{5}
"""

if __name__ == '__main__':
    main()
