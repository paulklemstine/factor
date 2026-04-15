#!/usr/bin/env python3
"""
Convert the Pythagorean manuscript from Markdown to a beautifully formatted LaTeX book.
Author: Paul Klemstine
"""

import re
import os
import shutil

PROJECT = "/workspace/request-project"
BOOK_DIR = os.path.join(PROJECT, "book")

# Chapter order and metadata
CHAPTERS = [
    ("Introduction", "Introduction", "The Triangle That Swallowed the Universe"),
    ("Chapter1", "Chapter1", "The Tree That Grew Triangles"),
    ("Chapter2", "Chapter2", "The Tree That Grew Into a Lattice"),
    ("Chapter3", "Chapter3", "Hyperbolic Shortcuts: How Pythagoras Learned to Factor"),
    ("Chapter4", "Chapter4", "Three Roads from Pythagoras"),
    ("Chapter5", "Chapter5", "The Tree That Knew It Was a Spacetime"),
    ("Chapter6", "Chapter6", "The Lock with Seven Keyholes"),
    ("Chapter7", "Chapter7", "The One-Way Corridor"),
    ("Chapter8", "Chapter8", "The Price of Descent"),
    ("Chapter9", "Chapter9", "The Four-Rung Ladder"),
    ("Chapter10", "Chapter10", "The Margin That Shook the World"),
    ("Chapter11", "Chapter11", "The Magnificent Sieve"),
    ("Chapter12", "Chapter12", "The Fourth Dimension of Pythagoras"),
    ("Chapter13", "Chapter13", "The GCD Cascade"),
    ("Chapter14", "Chapter14", "The Tree That Cracks Numbers"),
    ("Chapter15", "Chapter15", "The Algebra Where Two Plus Three Equals Two"),
    ("Chapter16", "Chapter16", "The Relativistic Secret of Right Triangles"),
    ("Conclusion", "Conclusion", "The Rosetta Stone"),
]


def copy_images():
    """Copy all images to book/images/ with chapter prefixes."""
    img_dir = os.path.join(BOOK_DIR, "images")
    os.makedirs(img_dir, exist_ok=True)
    
    for dirname, mdname, _ in CHAPTERS:
        src_dir = os.path.join(PROJECT, dirname, "images")
        if os.path.isdir(src_dir):
            for f in os.listdir(src_dir):
                if f.lower().endswith('.png') and 'Zone' not in f:
                    prefix = dirname.lower()
                    dst = os.path.join(img_dir, f"{prefix}_{f}")
                    shutil.copy2(os.path.join(src_dir, f), dst)
    
    # Copy ISBN files
    isbn_dir = os.path.join(PROJECT, "ISBN")
    for f in os.listdir(isbn_dir):
        shutil.copy2(os.path.join(isbn_dir, f), os.path.join(img_dir, f))


def process_inline(line):
    """Process inline markdown formatting to LaTeX."""
    # Bold+italic
    line = re.sub(r'\*\*\*(.+?)\*\*\*', r'\\textbf{\\textit{\1}}', line)
    # Bold
    line = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', line)
    # Italic (careful around math)
    parts = re.split(r'(\$\$?[^$]+?\$\$?)', line)
    processed = []
    for part in parts:
        if part.startswith('$'):
            processed.append(part)
        else:
            part = re.sub(r'(?<![\\*])\*([^*\n]+?)\*', r'\\textit{\1}', part)
            processed.append(part)
    line = ''.join(processed)
    # Em dash
    line = line.replace(' — ', ' --- ')
    line = line.replace('—', '---')
    return line


def md_to_latex(text, chapter_dir):
    """Convert markdown text to LaTeX."""
    lines = text.split('\n')
    result = []
    in_blockquote = False
    figure_counter = [0]
    
    # Track image files available
    img_dir = os.path.join(PROJECT, chapter_dir, "images")
    available_images = []
    if os.path.isdir(img_dir):
        available_images = sorted([f for f in os.listdir(img_dir) 
                                   if f.lower().endswith('.png') and 'Zone' not in f])
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip the main chapter title line (# ...)
        if line.startswith('# ') and i < 3:
            i += 1
            continue
        
        # Subtitle lines near top
        if i <= 5 and line.startswith('### ') and not line.startswith('### Puzzle'):
            subtitle = line.lstrip('#').strip().strip('*')
            if subtitle:
                result.append(f'\n\\begin{{center}}\\textit{{{process_inline(subtitle)}}}\\end{{center}}\n\\bigskip\n')
            i += 1
            continue
        
        # Horizontal rule
        if line.strip() == '---':
            result.append('\n\\ornbreak\n\n')
            i += 1
            continue
        
        # Section headers
        if line.startswith('## '):
            section_title = line[3:].strip()
            # Remove numbering prefixes
            section_title = re.sub(r'^(?:§?\d+\.?\s*)', '', section_title)
            section_title = re.sub(r'^Section\s+\d+:\s*', '', section_title)
            section_title = section_title.strip()
            result.append(f'\n\\section{{{process_inline(section_title)}}}\n\n')
            i += 1
            continue
        
        if line.startswith('### '):
            sub_title = line[4:].strip().strip('*').strip()
            sub_title = re.sub(r'^(?:§?\d+\.?\s*)', '', sub_title)
            result.append(f'\n\\subsection{{{process_inline(sub_title)}}}\n\n')
            i += 1
            continue
        
        # ILLUSTRATION blocks
        if '[ILLUSTRATION:' in line:
            ill_text = line
            while ']' not in ill_text and i + 1 < len(lines):
                i += 1
                ill_text += ' ' + lines[i]
            
            if available_images and figure_counter[0] < len(available_images):
                img_file = available_images[figure_counter[0]]
                prefix = chapter_dir.lower()
                img_path = f"images/{prefix}_{img_file}"
                
                # Extract caption
                caption = ill_text
                caption = re.sub(r'\[ILLUSTRATION:\s*', '', caption)
                caption = re.sub(r'\]\s*$', '', caption.strip())
                # First sentence for short caption
                sentences = caption.split('. ')
                short_cap = sentences[0].rstrip('.') + '.'
                if len(short_cap) < 15 and len(sentences) > 1:
                    short_cap = '. '.join(sentences[:2]).rstrip('.') + '.'
                
                short_cap = process_inline(short_cap)
                short_cap = short_cap.replace('&', '\\&').replace('#', '\\#').replace('%', '\\%').replace('_', '\\_')
                
                result.append('\\begin{figure}[htbp]\n')
                result.append('\\centering\n')
                result.append(f'\\includegraphics[width=0.82\\textwidth,keepaspectratio]{{{img_path}}}\n')
                result.append(f'\\caption{{{short_cap}}}\n')
                result.append('\\end{figure}\n\n')
                figure_counter[0] += 1
            i += 1
            continue
        
        # Table detection
        if '|' in line and line.strip().startswith('|') and line.count('|') >= 3:
            table_lines = [line]
            i += 1
            while i < len(lines) and '|' in lines[i] and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            result.append(convert_table(table_lines))
            continue
        
        # Blockquote start/continue
        if line.strip().startswith('> '):
            if not in_blockquote:
                result.append('\\begin{quote}\n')
                in_blockquote = True
            content = line.strip()[2:]
            result.append(process_inline(content) + '\n')
            i += 1
            continue
        elif in_blockquote and not line.strip().startswith('>'):
            result.append('\\end{quote}\n')
            in_blockquote = False
        
        # Display math
        if line.strip().startswith('$$') and line.strip().endswith('$$') and len(line.strip()) > 4:
            math_content = line.strip()[2:-2]
            result.append(f'\\[\n{math_content}\n\\]\n')
            i += 1
            continue
        
        if line.strip() == '$$':
            math_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() != '$$':
                math_lines.append(lines[i])
                i += 1
            result.append('\\[\n')
            result.append('\n'.join(math_lines))
            result.append('\n\\]\n')
            i += 1
            continue
        
        # Numbered list
        if re.match(r'^\d+\.\s', line.strip()):
            result.append('\\begin{enumerate}[leftmargin=*]\n')
            while i < len(lines) and re.match(r'^\d+\.\s', lines[i].strip()):
                item_text = re.sub(r'^\d+\.\s', '', lines[i].strip())
                result.append(f'\\item {process_inline(item_text)}\n')
                i += 1
            result.append('\\end{enumerate}\n')
            continue
        
        # Bullet list
        if line.strip().startswith('- ') or (line.strip().startswith('* ') and not line.strip().startswith('*[')):
            result.append('\\begin{itemize}[leftmargin=*]\n')
            while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
                item_text = lines[i].strip()
                item_text = re.sub(r'^[-*]\s', '', item_text)
                result.append(f'\\item {process_inline(item_text)}\n')
                i += 1
            result.append('\\end{itemize}\n')
            continue
        
        # Empty line
        if line.strip() == '':
            result.append('\n')
            i += 1
            continue
        
        # Regular text
        result.append(process_inline(line) + '\n')
        i += 1
    
    if in_blockquote:
        result.append('\\end{quote}\n')
    
    return ''.join(result)


def convert_table(table_lines):
    """Convert markdown table to LaTeX tabular."""
    rows = []
    for line in table_lines:
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        rows.append(cells)
    
    if len(rows) < 2:
        return ''
    
    is_separator = all(re.match(r'^[-:]+$', c.strip()) for c in rows[1] if c.strip())
    ncols = max(len(r) for r in rows)
    col_spec = 'l' * ncols
    
    result = ['\\begin{center}\n\\small\n\\begin{tabular}{' + col_spec + '}\n\\toprule\n']
    
    start = 0
    if is_separator:
        header = rows[0]
        while len(header) < ncols:
            header.append('')
        result.append(' & '.join([process_inline(h) for h in header]) + ' \\\\\n\\midrule\n')
        start = 2
    
    for row in rows[start:]:
        if all(re.match(r'^[-:]+$', c.strip()) for c in row if c.strip()):
            result.append('\\midrule\n')
        else:
            while len(row) < ncols:
                row.append('')
            result.append(' & '.join([process_inline(c) for c in row]) + ' \\\\\n')
    
    result.append('\\bottomrule\n\\end{tabular}\n\\end{center}\n\n')
    return ''.join(result)


def add_index_entries(text, chapter_key):
    """Add comprehensive index entries to chapter text."""
    index_terms = {
        'Pythagorean triple': 'Pythagorean triple',
        'Pythagorean triples': 'Pythagorean triple',
        'Berggren tree': 'Berggren tree',
        'Euclidean algorithm': 'Euclidean algorithm',
        'Lorentz group': 'Lorentz group',
        'Minkowski metric': 'Minkowski metric',
        'null cone': 'null cone',
        'light cone': 'light cone',
        'quadratic form': 'quadratic form',
        'Gaussian integers': 'Gaussian integers',
        'quaternions': 'quaternions',
        'octonions': 'octonions',
        'Cayley-Dickson': 'Cayley--Dickson construction',
        'Brahmagupta-Fibonacci': 'Brahmagupta--Fibonacci identity',
        "Fermat's Last Theorem": "Fermat's Last Theorem",
        'infinite descent': 'infinite descent',
        'lattice reduction': 'lattice reduction',
        'LLL algorithm': 'LLL algorithm',
        'continued fraction': 'continued fractions',
        'continued fractions': 'continued fractions',
        'Pell equation': 'Pell equation',
        'semiprime': 'semiprime',
        'semiprimes': 'semiprime',
        'RSA': 'RSA cryptosystem',
        "Shor's algorithm": "Shor's algorithm",
        "Grover's algorithm": "Grover's algorithm",
        'tropical geometry': 'tropical geometry',
        'congruence of squares': 'congruence of squares',
        'quadratic sieve': 'quadratic sieve',
        'number field sieve': 'number field sieve',
        'elliptic curve': 'elliptic curves',
        'elliptic curves': 'elliptic curves',
        'modular forms': 'modular forms',
        'modular form': 'modular forms',
        'Plimpton 322': 'Plimpton 322',
        'primitive triple': 'primitive triple',
        'coprime': 'coprimality',
        'determinant': 'determinant',
        'Hurwitz': 'Hurwitz theorem',
        'sum of squares': 'sum of squares',
        'difference of squares': 'difference of squares',
        'trial division': 'trial division',
        'factor base': 'factor base',
        'hyperbolic geometry': 'hyperbolic geometry',
        'special relativity': 'special relativity',
        'spacetime': 'spacetime',
        'ternary tree': 'ternary tree',
        'Newton polygon': 'Newton polygon',
        'norm multiplicativity': 'norm multiplicativity',
        'birthday bound': 'birthday bound',
        'smoothness': 'smoothness',
        'exponent vector': 'exponent vector',
        'Gaussian elimination': 'Gaussian elimination',
        'greatest common divisor': 'greatest common divisor',
    }
    
    # People
    people_terms = {
        'Euler': 'Euler, Leonhard',
        'Gauss': 'Gauss, Carl Friedrich',
        'Fermat': 'Fermat, Pierre de',
        'Wiles': 'Wiles, Andrew',
        'Hamilton': 'Hamilton, William Rowan',
        'Sophie Germain': 'Germain, Sophie',
        'Jacobi': 'Jacobi, Carl Gustav Jacob',
        'Chebyshev': 'Chebyshev, Pafnuty',
        'Brahmagupta': 'Brahmagupta',
        'Berggren': 'Berggren, B.',
        'Euclid': 'Euclid',
        'Minkowski': 'Minkowski, Hermann',
        'Lorentz': 'Lorentz, Hendrik',
        'Bellman': 'Bellman, Richard',
        'Hurwitz': 'Hurwitz, Adolf',
        'Dixon': 'Dixon, John D.',
        'Grover': 'Grover, Lov',
        'Shor': 'Shor, Peter',
        'Neugebauer': 'Neugebauer, Otto',
        'Wigner': 'Wigner, Eugene',
    }
    
    added = set()
    lines = text.split('\n')
    result_lines = []
    
    for line in lines:
        # Skip command lines
        if line.startswith('\\') and not line.startswith('\\textit') and not line.startswith('\\textbf'):
            result_lines.append(line)
            continue
        if '$' in line and line.count('$') > 4:
            result_lines.append(line)
            continue
            
        for term, idx in index_terms.items():
            if term in line and term not in added:
                safe_idx = idx.replace("'", "'")
                line = line.replace(term, f'{term}\\index{{{safe_idx}}}', 1)
                added.add(term)
                break  # Only one index per line to avoid nesting issues
        
        for term, idx in people_terms.items():
            if term in line and f'person_{term}' not in added:
                if f'\\index{{{idx}}}' not in line:
                    line = line.replace(term, f'{term}\\index{{{idx}}}', 1)
                    added.add(f'person_{term}')
                    break
        
        result_lines.append(line)
    
    return '\n'.join(result_lines)


def build_main_tex():
    """Generate the main book.tex content."""
    return r"""\documentclass[11pt,twoside,openright]{book}

%% ─────────────────────────────────────────────────────────────
%%  PAGE GEOMETRY  (Royal Octavo: 6.125 × 9.25 in)
%% ─────────────────────────────────────────────────────────────
\usepackage[
  paperwidth=6.125in,
  paperheight=9.25in,
  inner=1in,
  outer=0.75in,
  top=0.85in,
  bottom=1in,
  headheight=14pt,
  headsep=0.3in,
  footskip=0.4in
]{geometry}

%% ─────────────────────────────────────────────────────────────
%%  FONTS & ENCODING
%% ─────────────────────────────────────────────────────────────
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{microtype}

%% ─────────────────────────────────────────────────────────────
%%  MATHEMATICS
%% ─────────────────────────────────────────────────────────────
\usepackage{amsmath,amssymb,amsthm,mathtools}

%% ─────────────────────────────────────────────────────────────
%%  GRAPHICS & COLOR
%% ─────────────────────────────────────────────────────────────
\usepackage[dvipsnames,svgnames,x11names]{xcolor}
\usepackage{graphicx}
\usepackage{tikz}
\usepackage{pdfpages}

%% ─────────────────────────────────────────────────────────────
%%  TABLES
%% ─────────────────────────────────────────────────────────────
\usepackage{booktabs}
\usepackage{array}
\usepackage{longtable}

%% ─────────────────────────────────────────────────────────────
%%  LISTS & FLOATS
%% ─────────────────────────────────────────────────────────────
\usepackage{enumitem}
\usepackage{float}
\usepackage[font={small,it},labelfont={bf},skip=6pt]{caption}

%% ─────────────────────────────────────────────────────────────
%%  HEADERS & FOOTERS
%% ─────────────────────────────────────────────────────────────
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE]{\small\textsc{\leftmark}}
\fancyhead[RO]{\small\textsc{\rightmark}}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.3pt}
\renewcommand{\footrulewidth}{0pt}

\fancypagestyle{plain}{%
  \fancyhf{}%
  \fancyfoot[C]{\thepage}%
  \renewcommand{\headrulewidth}{0pt}%
}

%% ─────────────────────────────────────────────────────────────
%%  CHAPTER & SECTION STYLING
%% ─────────────────────────────────────────────────────────────
\usepackage{titlesec}

\definecolor{chaptercolor}{RGB}{100,20,60}
\definecolor{sectioncolor}{RGB}{80,30,70}

\titleformat{\chapter}[display]
  {\normalfont\huge\bfseries\color{chaptercolor}}
  {\chaptertitlename\ \thechapter}{20pt}{\Huge}
\titlespacing*{\chapter}{0pt}{-20pt}{30pt}

\titleformat{\section}
  {\normalfont\Large\bfseries\color{sectioncolor}}
  {\thesection}{1em}{}
\titlespacing*{\section}{0pt}{2.5ex plus 1ex minus .2ex}{1.2ex plus .2ex}

\titleformat{\subsection}
  {\normalfont\large\bfseries\color{sectioncolor!80!black}}
  {\thesubsection}{1em}{}

%% ─────────────────────────────────────────────────────────────
%%  TABLE OF CONTENTS
%% ─────────────────────────────────────────────────────────────
\usepackage{tocloft}
\renewcommand{\cftchapfont}{\bfseries\color{chaptercolor}}
\renewcommand{\cftchappagefont}{\bfseries\color{chaptercolor}}
\renewcommand{\cftsecfont}{\color{black!80}}
\renewcommand{\cftsecpagefont}{\color{black!80}}
\setlength{\cftbeforechapskip}{8pt}
\setlength{\cftbeforesecskip}{2pt}

%% ─────────────────────────────────────────────────────────────
%%  EPIGRAPH
%% ─────────────────────────────────────────────────────────────
\usepackage{epigraph}
\setlength{\epigraphwidth}{0.7\textwidth}

%% ─────────────────────────────────────────────────────────────
%%  INDEX
%% ─────────────────────────────────────────────────────────────
\usepackage{imakeidx}
\makeindex[columns=2, title=Index, intoc, options=-s book.ist]

%% ─────────────────────────────────────────────────────────────
%%  HYPERLINKS
%% ─────────────────────────────────────────────────────────────
\usepackage[
  colorlinks=true,
  linkcolor=chaptercolor!70!black,
  citecolor=chaptercolor!70!black,
  urlcolor=chaptercolor!50!blue,
  bookmarks=true,
  bookmarksnumbered=true,
  pdfauthor={Paul Klemstine},
  pdftitle={The Triangle That Swallowed the Universe},
  pdfsubject={Mathematics, Number Theory, Pythagorean Triples},
]{hyperref}

%% ─────────────────────────────────────────────────────────────
%%  THEOREM ENVIRONMENTS
%% ─────────────────────────────────────────────────────────────
\theoremstyle{definition}
\newtheorem{theorem}{Theorem}[chapter]
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{corollary}[theorem]{Corollary}
\newtheorem{definition_env}[theorem]{Definition}
\newtheorem{exampleenv}[theorem]{Example}
\newtheorem{remark}[theorem]{Remark}

%% ─────────────────────────────────────────────────────────────
%%  CUSTOM
%% ─────────────────────────────────────────────────────────────
\newcommand{\ornbreak}{%
  \par\bigskip
  \begin{center}
  \begin{tikzpicture}
    \draw[chaptercolor!40, line width=0.6pt] (-1.5,0) -- (-0.3,0);
    \node[chaptercolor!60] at (0,0) {$\diamond$};
    \draw[chaptercolor!40, line width=0.6pt] (0.3,0) -- (1.5,0);
  \end{tikzpicture}
  \end{center}
  \par\bigskip
}

\newcommand{\Z}{\mathbb{Z}}
\newcommand{\Q}{\mathbb{Q}}
\newcommand{\R}{\mathbb{R}}
\newcommand{\CC}{\mathbb{C}}
\newcommand{\N}{\mathbb{N}}
\newcommand{\HH}{\mathbb{H}}
\newcommand{\OO}{\mathbb{O}}

%% =============================================================
\begin{document}

%% ─── HALF-TITLE ──────────────────────────────────────────────
\thispagestyle{empty}
\begin{center}
\vspace*{3in}
{\LARGE\textsc{The Triangle That Swallowed\\[6pt] the Universe}}
\vfill
\end{center}
\cleardoublepage

%% ─── TITLE PAGE ──────────────────────────────────────────────
\thispagestyle{empty}
\begin{center}
\vspace*{1.2in}

{\fontsize{28}{34}\selectfont\bfseries\color{chaptercolor}
The Triangle That Swallowed\\[8pt]
the Universe}

\vspace{0.35in}

{\Large\textit{Pythagorean Triples, Lorentz Symmetry,\\[4pt]
and the Hidden Architecture of Number Theory}}

\vspace{0.9in}

{\Large Paul Klemstine}

\vfill

\begin{tikzpicture}[scale=1.2]
  \fill[chaptercolor!8] (0,0) -- (3,0) -- (3,4) -- cycle;
  \draw[line width=1.8pt, chaptercolor] (0,0) -- (3,0) -- (3,4) -- cycle;
  \node[below, chaptercolor!80!black] at (1.5,-0.15) {\large$a$};
  \node[right, chaptercolor!80!black] at (3.15,2) {\large$b$};
  \node[above left, chaptercolor!80!black] at (1.2,2.3) {\large$c$};
  \draw[chaptercolor, line width=0.8pt] (2.7,0) rectangle (3,0.3);
\end{tikzpicture}

\vspace{0.6in}

{\small\textit{First Edition}}

\vspace{0.3in}
\end{center}
\cleardoublepage

%% ─── COPYRIGHT ───────────────────────────────────────────────
\thispagestyle{empty}
\vspace*{\fill}
\begin{flushleft}
{\small

\textbf{The Triangle That Swallowed the Universe}\\
\textit{Pythagorean Triples, Lorentz Symmetry, and the Hidden Architecture of Number Theory}\\[12pt]

Copyright \textcopyright{} 2025 Paul Klemstine. All rights reserved.\\[6pt]

No part of this publication may be reproduced, distributed, or transmitted
in any form or by any means, including photocopying, recording, or other
electronic or mechanical methods, without the prior written permission of
the author, except in the case of brief quotations embodied in critical
reviews and certain other non-commercial uses permitted by copyright law.\\[12pt]

\textbf{ISBN 978-1-105-41110-6}\\[12pt]

First edition, 2025.\\[6pt]

Typeset in Latin Modern using \LaTeX.\\[6pt]

Printed in the United States of America.\\[12pt]

10\quad 9\quad 8\quad 7\quad 6\quad 5\quad 4\quad 3\quad 2\quad 1
}
\end{flushleft}
\cleardoublepage

%% ─── DEDICATION ──────────────────────────────────────────────
\thispagestyle{empty}
\vspace*{3in}
\begin{center}
{\Large\textit{Soli Deo Gloria}}
\end{center}
\vfill
\cleardoublepage

%% ─── TABLE OF CONTENTS ──────────────────────────────────────
\frontmatter
\tableofcontents
\cleardoublepage

%% ─── MAIN MATTER ────────────────────────────────────────────
\mainmatter

"""


def build_book():
    """Main build function."""
    os.makedirs(os.path.join(BOOK_DIR, "images"), exist_ok=True)
    
    # Copy images
    copy_images()
    
    # Build main tex
    main_tex = build_main_tex()
    
    # Process each chapter
    for dirname, mdname, title in CHAPTERS:
        is_intro = dirname == "Introduction"
        is_conclusion = dirname == "Conclusion"
        
        md_path = os.path.join(PROJECT, dirname, f"{mdname}.md")
        with open(md_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        latex_body = md_to_latex(text, dirname)
        
        # Chapter header
        if is_intro:
            header = (f"\\chapter*{{Introduction: {title}}}\n"
                      f"\\addcontentsline{{toc}}{{chapter}}{{Introduction: {title}}}\n"
                      f"\\markboth{{Introduction}}{{Introduction}}\n\n")
        elif is_conclusion:
            header = (f"\\chapter*{{Conclusion: {title}}}\n"
                      f"\\addcontentsline{{toc}}{{chapter}}{{Conclusion: {title}}}\n"
                      f"\\markboth{{Conclusion}}{{Conclusion}}\n\n")
        else:
            header = f"\\chapter{{{title}}}\n\n"
        
        chapter_tex = header + latex_body
        chapter_tex = add_index_entries(chapter_tex, dirname)
        
        chapter_filename = f"ch_{dirname.lower()}"
        chapter_path = os.path.join(BOOK_DIR, f"{chapter_filename}.tex")
        with open(chapter_path, 'w', encoding='utf-8') as f:
            f.write(chapter_tex)
        
        main_tex += f"\\input{{{chapter_filename}}}\n\n"
    
    # Backmatter
    main_tex += r"""
%% ─── INDEX ──────────────────────────────────────────────────
\backmatter
\cleardoublepage
\printindex

\end{document}
"""
    
    # Write main tex
    with open(os.path.join(BOOK_DIR, "book.tex"), 'w', encoding='utf-8') as f:
        f.write(main_tex)
    
    # Write index style file
    with open(os.path.join(BOOK_DIR, "book.ist"), 'w', encoding='utf-8') as f:
        f.write(r"""heading_flag 1
heading_prefix "\n  \\textbf{\\large "
heading_suffix "}\\nopagebreak\n"
delim_0 " \\dotfill\\ "
delim_1 " \\dotfill\\ "
delim_2 " \\dotfill\\ "
""")
    
    print("Book LaTeX source generated successfully!")


if __name__ == "__main__":
    build_book()
