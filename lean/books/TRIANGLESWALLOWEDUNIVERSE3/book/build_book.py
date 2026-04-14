#!/usr/bin/env python3
"""
Convert the Pythagorean book project from Markdown to a beautiful LaTeX book.
Handles: illustrations → figure references, math blocks, section hierarchy,
index terms, Lean appendix, and elegant formatting.
"""

import os
import re
import glob
import shutil

PROJECT = "/workspace/request-project"
BOOK = os.path.join(PROJECT, "book")

# ── Chapter ordering ──────────────────────────────────────────────
CHAPTER_ORDER = list(range(1, 17))

CHAPTER_TITLES = {
    1:  "The Tree That Grew Triangles",
    2:  "The Tree That Grew Into a Lattice",
    3:  "Hyperbolic Shortcuts: How Pythagoras Learned to Factor",
    4:  "Three Roads from Pythagoras",
    5:  "The Tree That Knew It Was a Spacetime",
    6:  "The Lock with Seven Keyholes",
    7:  "The One-Way Corridor",
    8:  "The Price of Descent",
    9:  "The Four-Rung Ladder: A Journey Through the Doubling Algebras",
    10: "The Margin That Shook the World",
    11: "The Magnificent Sieve",
    12: "The Fourth Dimension of Pythagoras",
    13: "The GCD Cascade",
    14: "The Tree That Cracks Numbers",
    15: "Tropical Geometry and the Shortest-Path Semiring",
    16: "The Relativistic Secret of Right Triangles",
}

CHAPTER_SUBTITLES = {
    2:  "How an Ancient Algorithm and a Family Tree of Right Triangles Turned Out to Be the Same Thing",
    3:  "In which a party trick reveals a deep identity, an infinite tree hides the symmetries of spacetime, and a greatest common divisor cracks a number wide open",
    4:  "How the World's Oldest Equation Secretly Cracks the World's Hardest Codes",
    5:  "How Three Matrices, a Quadratic Form, and a Pell Equation Reveal That Pythagorean Triples Live in Einstein's Universe",
    6:  "How Pythagorean Quintuplets, Sextuplets, and Octuplets Crack Composite Numbers Wide Open",
    7:  "Why Quantum Shortcuts Aren't Where You'd Expect",
    8:  "How Hard Is It to Factor by Climbing a Tree?",
    10: "How a Scribbled Note Launched Three Centuries of Mathematics — and Why the Proof Would Never Have Fit",
    12: "How Quadruples Crack Numbers",
    13: "Cracking Numbers Open with Pythagorean Channels",
    14: "How a Babylonian Equation Grows a Forest That Can Split Integers Apart",
    16: "In which we discover that the humblest objects in all of mathematics have been hiding a connection to Einstein's spacetime all along",
}

# ── Index terms to auto-detect ────────────────────────────────────
INDEX_TERMS = [
    "Pythagorean triple", "Pythagorean triples",
    "Berggren tree", "Berggren matrices", "Berggren",
    "Lorentz group", "Lorentz boost", "Lorentz", "Minkowski",
    "Euclid", "Euclidean algorithm",
    "Plimpton 322",
    "Fermat", "Fermat's Last Theorem",
    "Gaussian integers", "Gaussian integer",
    "quaternion", "quaternions", "octonion", "octonions",
    "Cayley-Dickson", "Cayley–Dickson",
    "Brahmagupta", "Brahmagupta-Fibonacci",
    "Grover", "Grover's algorithm",
    "Shor's algorithm", "Shor",
    "quadratic sieve", "number field sieve",
    "tropical geometry", "tropical",
    "Pell equation", "Pell",
    "null cone", "light cone",
    "semiprime", "balanced semiprime",
    "greatest common divisor", "GCD",
    "continued fraction", "continued fractions",
    "lattice", "lattice reduction", "LLL algorithm", "LLL",
    "Hurwitz", "Hurwitz's theorem",
    "Wiles", "Andrew Wiles",
    "Euler", "Leonhard Euler",
    "Sophie Germain",
    "Hamilton",
    "Newton polygon",
    "congruence of squares",
    "infinite descent",
    "Fano plane",
    "norm multiplicativity",
    "Chebyshev",
    "modular forms",
    "elliptic curve", "elliptic curves",
    "RSA",
    "primitive triple", "primitive triples",
    "coprime", "coprimality",
    "bijection",
    "ternary tree",
    "descent",
    "hypotenuse",
    "right triangle", "right triangles",
]

def escape_latex(text):
    """Escape special LaTeX chars, but leave math mode alone."""
    # We'll handle this more carefully in the main converter
    return text

def md_to_latex_body(md_text, chapter_num=None, is_intro=False, is_conclusion=False):
    """Convert markdown body text to LaTeX."""
    lines = md_text.split('\n')
    out = []
    in_math_block = False
    in_blockquote = False
    blockquote_lines = []
    fig_counter = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip the chapter title line (we handle it separately)
        if i == 0 and line.startswith('# '):
            i += 1
            continue
        # Skip subtitle lines
        if i <= 3 and line.startswith('### *') and not is_intro and not is_conclusion:
            i += 1
            continue
        
        # Horizontal rules
        if line.strip() == '---':
            out.append('')
            out.append(r'\bigskip')
            out.append('')
            i += 1
            continue
        
        # Math display blocks
        if line.strip() == '$$':
            if not in_math_block:
                in_math_block = True
                out.append(r'\[')
            else:
                in_math_block = False
                out.append(r'\]')
            i += 1
            continue
        
        if in_math_block:
            out.append(sanitize_unicode_for_latex(line))
            i += 1
            continue
        
        # Inline $$ ... $$ on one line
        if line.strip().startswith('$$') and line.strip().endswith('$$') and len(line.strip()) > 4:
            math_content = line.strip()[2:-2]
            out.append(r'\[' + math_content + r'\]')
            i += 1
            continue
        
        # ILLUSTRATION blocks → figure with image
        if line.strip().startswith('[ILLUSTRATION:'):
            # Collect the full illustration description (may span multiple lines)
            desc_lines = [line]
            while not line.strip().endswith(']'):
                i += 1
                if i >= len(lines):
                    break
                line = lines[i]
                desc_lines.append(line)
            desc = ' '.join(desc_lines)
            desc = re.sub(r'\[ILLUSTRATION:\s*', '', desc)
            desc = desc.rstrip(']').strip()
            
            fig_counter += 1
            
            # Determine which image file to use
            if is_intro:
                img_dir = os.path.join(PROJECT, "Introduction", "images")
                prefix = "Introduction"
            elif is_conclusion:
                img_dir = os.path.join(PROJECT, "Conclusion", "images")
                prefix = "Conclusion"
            else:
                img_dir = os.path.join(PROJECT, f"Chapter{chapter_num}", "images")
                prefix = f"Chapter{chapter_num}"
            
            # Find the matching image
            fig_num_str = f"{fig_counter:02d}"
            img_candidates = glob.glob(os.path.join(img_dir, f"fig{fig_num_str}_*.png"))
            if img_candidates:
                img_file = os.path.basename(img_candidates[0])
                img_path = f"{prefix}/images/{img_file}"
                # Clean up the description for caption
                caption = clean_for_caption(desc)
                out.append(r'\begin{figure}[htbp]')
                out.append(r'\centering')
                out.append(r'\includegraphics[width=0.85\textwidth]{' + img_path + '}')
                out.append(r'\caption{' + caption + '}')
                out.append(r'\end{figure}')
            else:
                # No image found, just put description as a framed note
                caption = clean_for_caption(desc)
                out.append(r'\begin{figure}[htbp]')
                out.append(r'\centering')
                out.append(r'\fbox{\parbox{0.8\textwidth}{\small\itshape ' + caption + '}}')
                out.append(r'\end{figure}')
            
            i += 1
            continue
        
        # Blockquotes
        if line.strip().startswith('> '):
            if not in_blockquote:
                in_blockquote = True
                blockquote_lines = []
            bq_text = line.strip()[2:]
            blockquote_lines.append(bq_text)
            i += 1
            continue
        elif in_blockquote:
            in_blockquote = False
            bq_content = ' '.join(blockquote_lines)
            bq_content = process_inline(bq_content)
            out.append(r'\begin{quotation}')
            out.append(r'\noindent\itshape ' + bq_content)
            out.append(r'\end{quotation}')
            # Don't skip current line, fall through
        
        # Section headers
        if line.startswith('## ') and not line.startswith('### '):
            section_title = line[3:].strip()
            # Clean markdown formatting
            section_title = re.sub(r'§\d+\.\s*', '', section_title)
            section_title = re.sub(r'^\d+\.\s*', '', section_title)
            section_title = section_title.strip('*').strip()
            # Remove em dashes for subtitle patterns
            section_title = re.sub(r'\s*—\s*', ' — ', section_title)
            section_title = process_inline_simple(section_title)
            out.append(r'\section{' + section_title + '}')
            i += 1
            continue
        
        if line.startswith('### '):
            subsection_title = line[4:].strip().strip('*').strip()
            subsection_title = process_inline_simple(subsection_title)
            out.append(r'\subsection{' + subsection_title + '}')
            i += 1
            continue
        
        # Bullet lists
        if line.strip().startswith('- **'):
            if i > 0 and not lines[i-1].strip().startswith('- '):
                out.append(r'\begin{itemize}[leftmargin=*]')
            item_text = line.strip()[2:]
            item_text = process_inline(item_text)
            out.append(r'\item ' + item_text)
            # Check if next line is also a bullet
            if i + 1 < len(lines) and not lines[i+1].strip().startswith('- '):
                out.append(r'\end{itemize}')
            i += 1
            continue
        
        if line.strip().startswith('- '):
            if i > 0 and not lines[i-1].strip().startswith('- '):
                out.append(r'\begin{itemize}[leftmargin=*]')
            item_text = line.strip()[2:]
            item_text = process_inline(item_text)
            out.append(r'\item ' + item_text)
            if i + 1 < len(lines) and not lines[i+1].strip().startswith('- '):
                out.append(r'\end{itemize}')
            i += 1
            continue
        
        # Empty lines
        if line.strip() == '':
            out.append('')
            i += 1
            continue
        
        # Regular text
        processed = process_inline(line)
        out.append(processed)
        i += 1
    
    # Close any open blockquote
    if in_blockquote:
        bq_content = ' '.join(blockquote_lines)
        bq_content = process_inline(bq_content)
        out.append(r'\begin{quotation}')
        out.append(r'\noindent\itshape ' + bq_content)
        out.append(r'\end{quotation}')
    
    return '\n'.join(out)


def sanitize_unicode_for_latex(text):
    """Replace problematic Unicode chars in body text."""
    text = text.replace('\u2717', '{$\\times$}')
    text = text.replace('\u2713', '{$\\checkmark$}')
    text = text.replace('\u2714', '{$\\checkmark$}')
    text = text.replace('\u2605', '{$\\star$}')
    text = text.replace('\u220e', '{$\\blacksquare$}')
    text = text.replace('\U0001f422', '(turtle)')  # turtle emoji
    text = text.replace('\U0001f3c6', '(trophy)')   # trophy emoji
    text = text.replace('\U0001f389', '(party)')     # party emoji
    text = text.replace('\U0001f4a1', '(idea)')      # light bulb
    text = text.replace('\U0001f50d', '(search)')    # magnifying glass
    text = text.replace('\U0001f4dd', '(memo)')      # memo
    text = text.replace('\u2014', '---')
    text = text.replace('\u2013', '--')
    text = text.replace('\u2018', "`")
    text = text.replace('\u2019', "'")
    text = text.replace('\u201c', "``")
    text = text.replace('\u201d', "''")
    text = text.replace('\u2026', '...')
    text = text.replace('\u2022', '{$\\bullet$}')
    text = text.replace('\u00a0', '~')  # non-breaking space
    text = text.replace('\u274c', '{$\\times$}')  # cross mark
    # Remove any remaining emoji (4-byte Unicode)
    import re as _re
    text = _re.sub(r'[\U00010000-\U0010FFFF]', '', text)
    return text

def process_inline(text):
    """Process inline markdown formatting."""
    text = sanitize_unicode_for_latex(text)
    # Bold+italic: ***text*** or **_text_**
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\\textbf{\\textit{\1}}', text)
    # Bold: **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
    # Italic: *text* (but not inside math)
    # Be careful not to match inside $...$
    parts = re.split(r'(\$[^$]+\$)', text)
    for j in range(len(parts)):
        if not parts[j].startswith('$'):
            parts[j] = re.sub(r'(?<!\w)\*([^*]+?)\*(?!\w)', r'\\textit{\1}', parts[j])
    text = ''.join(parts)
    
    # Special chars (outside math)
    parts = re.split(r'(\$[^$]+\$)', text)
    for j in range(len(parts)):
        if not parts[j].startswith('$'):
            parts[j] = parts[j].replace('&', r'\&')
            parts[j] = parts[j].replace('#', r'\#')
            parts[j] = parts[j].replace('%', r'\%')
            # Don't escape _ inside \textbf, \textit etc.
    text = ''.join(parts)
    
    return text


def process_inline_simple(text):
    """Process inline markdown for section titles (simpler)."""
    text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
    text = re.sub(r'\*(.+?)\*', r'\\textit{\1}', text)
    text = text.replace('&', r'\&')
    text = text.replace('#', r'\#')
    text = text.replace('%', r'\%')
    return text


def clean_for_caption(text):
    """Clean text for use in a LaTeX caption."""
    text = process_inline(text)
    # Remove problematic chars
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def build_index_commands():
    """Generate index entries as a post-processing step."""
    # We'll add \index{} commands by finding terms in the text
    return INDEX_TERMS


def add_index_entries(latex_text):
    """Add \\index{} entries for key terms found in the text."""
    for term in INDEX_TERMS:
        # Only index the first occurrence per section
        # Use word boundary matching
        pattern = r'(?<![\\{])(\b' + re.escape(term) + r'\b)(?![}])'
        # Add index entry after first occurrence
        latex_text = re.sub(pattern, r'\1\\index{' + term + '}', latex_text, count=3)
    return latex_text


def sanitize_lean_for_latex(content):
    """Replace Unicode chars with ASCII for pdflatex listings."""
    R = {
        '\u2192': '->', '\u2190': '<-', '\u2200': 'forall ', '\u2203': 'exists ',
        '\u03bb': 'fun ', '\u22a2': '|-', '\u2264': '<=', '\u2265': '>=',
        '\u2260': '/=', '\u2227': '/\\\\', '\u2228': '\\\\/', '\u00ac': 'not ',
        '\u2115': 'Nat', '\u2124': 'Int', '\u211d': 'Real', '\u2102': 'Complex',
        '\u27e8': '<', '\u27e9': '>', '\u00d7': 'x', '\u00b7': '.',
        '\u2218': ' o ', '\u207b\u00b9': '^(-1)', '\u00b2': '^2', '\u00b3': '^3',
        '\u2081': '_1', '\u2082': '_2', '\u2083': '_3', '\u2084': '_4',
        '\u1d40': '^T', '\u2208': ' in ', '\u2209': ' notin ',
        '\u2286': ' sub= ', '\u2282': ' sub ', '\u2205': 'empty',
        '\u222a': ' union ', '\u2229': ' inter ', '\u2211': 'sum', '\u220f': 'prod',
        '\u221a': 'sqrt', '\u221e': 'inf', '\u2223': '|',
        '\u2194': '<->', '\u27f9': '=>', '\u27f8': '<=', '\u21a6': '|->',
        '\u22a5': 'False', '\u22a4': 'True',
        '\u00a7': 'S', '\u2014': '--', '\u2013': '-',
        '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
        '\u2026': '...', '\u2717': '[x]', '\u2713': '[ok]', '\u2714': '[ok]',
        '\u2022': '*', '\u2261': '==', '\u2245': '~=',
        '\u2295': '+', '\u2297': '*',
        '\u211a': 'Rat',
        '\u2070': '^0', '\u00b9': '^1', '\u2074': '^4',
        '\u2075': '^5', '\u2076': '^6', '\u2077': '^7',
        '\u2078': '^8', '\u2079': '^9',
        '\u2080': '_0', '\u2085': '_5', '\u2086': '_6',
        '\u2087': '_7', '\u2088': '_8', '\u2089': '_9',
    }
    # Also add Greek letters
    greeks = 'abgdezhqiklmnxoprstufcyw'
    for i, g in enumerate('\u03b1\u03b2\u03b3\u03b4\u03b5\u03b6\u03b7\u03b8\u03b9\u03ba\u03bb\u03bc\u03bd\u03be\u03bf\u03c0\u03c1\u03c3\u03c4\u03c5\u03c6\u03c7\u03c8\u03c9'):
        if g not in R:  # don't override lambda
            R[g] = greeks[i] if i < len(greeks) else '?'
    for uc, asc in R.items():
        content = content.replace(uc, asc)
    content = content.encode('ascii', 'replace').decode('ascii')
    return content

def read_lean_file(filepath):
    """Read a lean file and return its content, sanitized for LaTeX listings."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return sanitize_lean_for_latex(content)


def build_lean_appendix():
    """Build the Lean code appendix."""
    lean_dir = os.path.join(PROJECT, "lean")
    lean_files = sorted(glob.glob(os.path.join(lean_dir, "*.lean")))
    
    sections = []
    for lf in lean_files:
        basename = os.path.basename(lf)
        content = read_lean_file(lf)
        # Extract title from the file
        title_match = re.search(r'#\s+(.+)', content)
        title = title_match.group(1).strip() if title_match else basename.replace('.lean', '').replace('_', ' ')
        # Escape special chars in title for index
        title_idx = title.replace('&', 'and').replace('#', '').replace('%', '')
        
        # Clean the filename for display
        display_name = basename.replace('_', r'\_')
        
        sections.append(f"""
\\subsection*{{{display_name}}}
\\label{{lean:{basename.replace('.lean', '')}}}
\\index{{{title_idx}}}

\\begin{{lstlisting}}[style=lean]
{content}
\\end{{lstlisting}}

\\clearpage
""")
    
    return '\n'.join(sections)


# ── Copy all images to book directory ─────────────────────────────
def copy_images():
    """Copy/symlink image directories into the book build directory."""
    for chapter_num in CHAPTER_ORDER:
        src = os.path.join(PROJECT, f"Chapter{chapter_num}", "images")
        dst = os.path.join(BOOK, f"Chapter{chapter_num}", "images")
        if os.path.exists(src):
            os.makedirs(os.path.join(BOOK, f"Chapter{chapter_num}"), exist_ok=True)
            if os.path.exists(dst) or os.path.islink(dst):
                if os.path.islink(dst):
                    os.remove(dst)
                else:
                    shutil.rmtree(dst)
            os.symlink(src, dst)
    
    # Introduction images
    src = os.path.join(PROJECT, "Introduction", "images")
    dst = os.path.join(BOOK, "Introduction", "images")
    if os.path.exists(src):
        os.makedirs(os.path.join(BOOK, "Introduction"), exist_ok=True)
        if os.path.exists(dst) or os.path.islink(dst):
            os.remove(dst) if os.path.islink(dst) else shutil.rmtree(dst)
        os.symlink(src, dst)
    
    # Conclusion images
    src = os.path.join(PROJECT, "Conclusion", "images")
    dst = os.path.join(BOOK, "Conclusion", "images")
    if os.path.exists(src):
        os.makedirs(os.path.join(BOOK, "Conclusion"), exist_ok=True)
        if os.path.exists(dst) or os.path.islink(dst):
            os.remove(dst) if os.path.islink(dst) else shutil.rmtree(dst)
        os.symlink(src, dst)


# ── Main LaTeX document ──────────────────────────────────────────
def build_latex():
    copy_images()
    
    # Read and convert all chapters
    chapter_bodies = {}
    for ch in CHAPTER_ORDER:
        md_path = os.path.join(PROJECT, f"Chapter{ch}", f"Chapter{ch}.md")
        with open(md_path, 'r', encoding='utf-8') as f:
            md = f.read()
        body = md_to_latex_body(md, chapter_num=ch)
        body = add_index_entries(body)
        chapter_bodies[ch] = body
    
    # Read introduction
    with open(os.path.join(PROJECT, "Introduction", "Introduction.md"), 'r', encoding='utf-8') as f:
        intro_md = f.read()
    intro_body = md_to_latex_body(intro_md, is_intro=True)
    intro_body = add_index_entries(intro_body)
    
    # Read conclusion
    with open(os.path.join(PROJECT, "Conclusion", "Conclusion.md"), 'r', encoding='utf-8') as f:
        conc_md = f.read()
    conc_body = md_to_latex_body(conc_md, is_conclusion=True)
    conc_body = add_index_entries(conc_body)
    
    # Build Lean appendix
    lean_appendix = build_lean_appendix()
    
    # Assemble chapter includes
    chapter_latex = []
    for ch in CHAPTER_ORDER:
        title = CHAPTER_TITLES[ch]
        subtitle = CHAPTER_SUBTITLES.get(ch, "")
        
        chapter_latex.append(f"""
%% ══════════════════════════════════════════════════════════════
%% CHAPTER {ch}
%% ══════════════════════════════════════════════════════════════
\\chapter{{{title}}}
\\label{{ch:{ch}}}
""")
        if subtitle:
            chapter_latex.append(f"""\\begin{{center}}
\\textit{{{subtitle}}}
\\end{{center}}
\\bigskip
""")
        chapter_latex.append(chapter_bodies[ch])
        chapter_latex.append("\\clearpage\n")
    
    all_chapters = '\n'.join(chapter_latex)
    
    # ── The full document ──────────────────────────────────────
    document = r"""\documentclass[11pt,openright,twoside]{book}

%% ══════════════════════════════════════════════════════════════
%% GEOMETRY & LAYOUT
%% ══════════════════════════════════════════════════════════════
\usepackage[
  paperwidth=7.5in,
  paperheight=9.25in,
  inner=1.1in,
  outer=0.9in,
  top=1.0in,
  bottom=1.1in,
  headsep=0.35in,
  footskip=0.45in
]{geometry}

%% ══════════════════════════════════════════════════════════════
%% FONTS — Elegant Garamond text with matching math
%% ══════════════════════════════════════════════════════════════
\usepackage[T1]{fontenc}
\usepackage{ebgaramond}
\usepackage{ebgaramond-maths}
% Fix star symbol conflict
\makeatletter
\@ifundefined{star}{\DeclareMathSymbol{\star}{\mathbin}{symbols}{"3F}}{}
\makeatother
\usepackage{inconsolata}            % monospace for code

%% ══════════════════════════════════════════════════════════════
%% TYPOGRAPHY
%% ══════════════════════════════════════════════════════════════
\usepackage{microtype}
\usepackage{lettrine}               % drop caps
\usepackage{parskip}                % paragraph spacing
\setlength{\parskip}{0.4\baselineskip plus 2pt minus 1pt}
\setlength{\parindent}{1.5em}

%% ══════════════════════════════════════════════════════════════
%% COLOR PALETTE — Rich jewel tones
%% ══════════════════════════════════════════════════════════════
\usepackage[dvipsnames,svgnames,x11names]{xcolor}

\definecolor{chaptercolor}{HTML}{1B3A4B}    % deep teal-navy
\definecolor{sectioncolor}{HTML}{4A1942}    % dark plum
\definecolor{accentgold}{HTML}{C49B2A}      % antique gold
\definecolor{linkcolor}{HTML}{7B2D26}       % deep burgundy
\definecolor{codebg}{HTML}{FAF6F0}          % warm parchment
\definecolor{codeframe}{HTML}{D4C5A9}       % linen border
\definecolor{pullquote}{HTML}{2E5339}       % forest green
\definecolor{pagenum}{HTML}{8B7355}         % warm taupe

%% ══════════════════════════════════════════════════════════════
%% PACKAGES
%% ══════════════════════════════════════════════════════════════
\usepackage{amsmath,amssymb,amsthm}
\usepackage{mathtools}
\usepackage{graphicx}
\usepackage{float}
\usepackage{booktabs}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{tocloft}
\usepackage{imakeidx}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{wrapfig}
\usepackage{listings}
\usepackage{fancyvrb}
\usepackage{tikz}
\usetikzlibrary{decorations.pathmorphing,calc,shadows.blur}
\usepackage{pdfpages}
\usepackage{etoolbox}
\usepackage{epigraph}
\usepackage[
  bookmarks=true,
  colorlinks=true,
  linkcolor=linkcolor,
  citecolor=linkcolor,
  urlcolor=linkcolor,
  pdfauthor={Paul Klemstine},
  pdftitle={The Triangle That Swallowed the Universe},
  pdfsubject={Mathematics, Number Theory, Pythagorean Triples},
]{hyperref}

\makeindex[intoc, title=Index, columns=2]

%% ══════════════════════════════════════════════════════════════
%% CHAPTER & SECTION STYLING
%% ══════════════════════════════════════════════════════════════
\titleformat{\chapter}[display]
  {\normalfont\huge\bfseries\color{chaptercolor}}
  {\chaptertitlename\ \thechapter}
  {0pt}
  {\Huge}
  [\vspace{0.3cm}{\color{accentgold}\titlerule[1.5pt]}]

\titleformat{\section}
  {\normalfont\Large\bfseries\color{sectioncolor}}
  {\thesection}{1em}{}
  [\vspace{2pt}{\color{sectioncolor!30}\titlerule[0.6pt]}]

\titleformat{\subsection}
  {\normalfont\large\bfseries\itshape\color{sectioncolor!80}}
  {\thesubsection}{1em}{}

%% ══════════════════════════════════════════════════════════════
%% HEADERS & FOOTERS — Refined running heads
%% ══════════════════════════════════════════════════════════════
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE]{\small\color{pagenum}\textsc{\nouppercase{\leftmark}}}
\fancyhead[RO]{\small\color{pagenum}\textsc{\nouppercase{\rightmark}}}
\fancyfoot[C]{\small\color{pagenum}\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\headrule}{\hbox to\headwidth{\color{accentgold!50}\leaders\hrule height \headrulewidth\hfill}}
\fancypagestyle{plain}{%
  \fancyhf{}
  \fancyfoot[C]{\small\color{pagenum}\thepage}
  \renewcommand{\headrulewidth}{0pt}
}

%% ══════════════════════════════════════════════════════════════
%% TABLE OF CONTENTS STYLING
%% ══════════════════════════════════════════════════════════════
\renewcommand{\cftchapfont}{\bfseries\color{chaptercolor}}
\renewcommand{\cftchappagefont}{\bfseries\color{chaptercolor}}
\renewcommand{\cftsecfont}{\color{sectioncolor!80}}
\renewcommand{\cftsecpagefont}{\color{sectioncolor!80}}
\renewcommand{\cftchapleader}{\cftdotfill{\cftchapdotsep}}
\renewcommand{\cftchapdotsep}{2.5}
\setlength{\cftbeforechapskip}{8pt}

%% ══════════════════════════════════════════════════════════════
%% FIGURE CAPTIONS
%% ══════════════════════════════════════════════════════════════
\captionsetup{
  font={small,it},
  labelfont={bf,color=chaptercolor},
  format=hang,
  margin=1cm,
  skip=8pt,
}

%% ══════════════════════════════════════════════════════════════
%% BLOCKQUOTE / EPIGRAPH STYLING
%% ══════════════════════════════════════════════════════════════
\renewenvironment{quotation}{%
  \par\vspace{8pt}%
  \begin{list}{}{%
    \setlength{\leftmargin}{2em}%
    \setlength{\rightmargin}{2em}%
  }\item[]\itshape\color{pullquote}%
}{%
  \end{list}%
  \par\vspace{8pt}%
}

%% ══════════════════════════════════════════════════════════════
%% CODE LISTING STYLE (for Lean 4)
%% ══════════════════════════════════════════════════════════════
\lstdefinestyle{lean}{
  backgroundcolor=\color{codebg},
  frame=single,
  rulecolor=\color{codeframe},
  basicstyle=\ttfamily\footnotesize\color{black},
  keywordstyle=\bfseries\color{chaptercolor},
  commentstyle=\itshape\color{pagenum},
  stringstyle=\color{linkcolor},
  breaklines=true,
  breakatwhitespace=true,
  showstringspaces=false,
  tabsize=2,
  numbers=left,
  numberstyle=\tiny\color{pagenum!50},
  numbersep=8pt,
  xleftmargin=16pt,
  framexleftmargin=16pt,
  aboveskip=10pt,
  belowskip=10pt,
  morekeywords={import,def,theorem,lemma,example,instance,structure,class,
    where,with,match,if,then,else,do,return,let,have,show,by,sorry,
    namespace,end,open,section,variable,noncomputable,private,protected,
    inductive,extends,deriving,axiom,opaque,abbrev,set_option,attribute,
    macro,syntax,tactic,Prop,Type,Sort,Nat,Int,Real},
  extendedchars=false,
}

%% ══════════════════════════════════════════════════════════════
%% THEOREM ENVIRONMENTS
%% ══════════════════════════════════════════════════════════════
\theoremstyle{definition}
\newtheorem{theorem}{Theorem}[chapter]
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{corollary}[theorem]{Corollary}
\newtheorem{definition}[theorem]{Definition}
\newtheorem{example}[theorem]{Example}
\newtheorem{remark}[theorem]{Remark}

%% ══════════════════════════════════════════════════════════════
\begin{document}

%% ══════════════════════════════════════════════════════════════
%% FRONT MATTER
%% ══════════════════════════════════════════════════════════════
\frontmatter

%% ── Half Title ───────────────────────────────────────────────
\thispagestyle{empty}
\vspace*{\stretch{2}}
\begin{center}
{\fontsize{24}{28}\selectfont\bfseries\color{chaptercolor}
The Triangle That\\[6pt]Swallowed the Universe}
\end{center}
\vspace*{\stretch{3}}
\clearpage

%% ── Blank page ───────────────────────────────────────────────
\thispagestyle{empty}\mbox{}\clearpage

%% ── Full Title Page ──────────────────────────────────────────
\thispagestyle{empty}
\vspace*{\stretch{1}}
\begin{center}

{\fontsize{32}{38}\selectfont\bfseries\color{chaptercolor}
The Triangle That\\[8pt]Swallowed the Universe}

\vspace{1.5cm}

{\color{accentgold}\rule{0.4\textwidth}{1.5pt}}

\vspace{1.2cm}

{\Large\itshape\color{sectioncolor}
Pythagorean Triples, Berggren Trees,\\[4pt]
Lorentz Symmetry, and the Hidden\\[4pt]
Architecture of Number Theory}

\vspace{2cm}

{\fontsize{18}{22}\selectfont\scshape Paul Klemstine}

\vspace{\stretch{2}}

{\small\color{pagenum} With Machine-Verified Proofs in Lean\,4}

\end{center}
\vspace*{\stretch{1}}
\clearpage

%% ── Copyright page ───────────────────────────────────────────
\thispagestyle{empty}
\vspace*{\stretch{3}}
\begin{flushleft}
\small\color{pagenum}
\textcopyright{} 2025 Paul Klemstine. All rights reserved.\\[8pt]
Typeset in EB Garamond.\\[4pt]
Formal proofs verified with Lean\,4 and Mathlib.\\[4pt]
Illustrations generated computationally.
\end{flushleft}
\vspace*{\stretch{1}}
\clearpage

%% ── Dedication ───────────────────────────────────────────────
\thispagestyle{empty}
\vspace*{\stretch{2}}
\begin{center}
{\large\itshape\color{chaptercolor}
Soli Deo Gloria}

\vspace{0.8cm}

{\color{accentgold}\rule{2cm}{0.5pt}}

\vspace{0.8cm}

{\itshape\color{pagenum}
To God alone be the glory.}
\end{center}
\vspace*{\stretch{3}}
\clearpage

%% ── Table of Contents ────────────────────────────────────────
{
\hypersetup{linkcolor=chaptercolor}
\tableofcontents
}
\clearpage

%% ── List of Figures ──────────────────────────────────────────
\listoffigures
\clearpage

%% ══════════════════════════════════════════════════════════════
%% INTRODUCTION
%% ══════════════════════════════════════════════════════════════
\chapter*{Introduction: The Triangle That Swallowed the Universe}
\addcontentsline{toc}{chapter}{Introduction: The Triangle That Swallowed the Universe}
\markboth{Introduction}{Introduction}

""" + intro_body + r"""

\clearpage

%% ══════════════════════════════════════════════════════════════
%% MAIN MATTER
%% ══════════════════════════════════════════════════════════════
\mainmatter

""" + all_chapters + r"""

%% ══════════════════════════════════════════════════════════════
%% CONCLUSION
%% ══════════════════════════════════════════════════════════════
\chapter*{Conclusion: The Rosetta Stone}
\addcontentsline{toc}{chapter}{Conclusion: The Rosetta Stone}
\markboth{Conclusion}{Conclusion}

""" + conc_body + r"""

\clearpage

%% ══════════════════════════════════════════════════════════════
%% BACK MATTER
%% ══════════════════════════════════════════════════════════════
\backmatter

%% ── Lean 4 Appendix ─────────────────────────────────────────
\chapter*{Appendix: Machine-Verified Proofs in Lean\,4}
\addcontentsline{toc}{chapter}{Appendix: Machine-Verified Proofs in Lean\,4}
\markboth{Appendix: Lean\,4 Proofs}{Appendix: Lean\,4 Proofs}

\vspace{0.5cm}
\noindent
The following appendix contains the complete source code of the Lean\,4
formalizations that accompany this book. Each file corresponds to one or
more chapters and contains machine-verified proofs of the key theorems
discussed in the text. These proofs have been checked against the
Mathlib library, ensuring their correctness beyond any reasonable doubt.

\vspace{0.5cm}

""" + lean_appendix + r"""

%% ── Index ────────────────────────────────────────────────────
\printindex

\end{document}
"""
    
    # Write the LaTeX file
    tex_path = os.path.join(BOOK, "book.tex")
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(document)
    
    print(f"LaTeX file written to {tex_path}")
    print(f"Total document length: {len(document)} characters")
    return tex_path


if __name__ == "__main__":
    build_latex()
