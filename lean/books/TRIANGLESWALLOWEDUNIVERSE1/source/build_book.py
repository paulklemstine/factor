#!/usr/bin/env python3
"""Convert the book's Markdown chapters + images into a single LaTeX file."""

import os
import re
import subprocess
import glob

PROJECT = "/workspace/request-project"

# Order of parts
PARTS = (
    ["Introduction"] +
    [f"Chapter{i}" for i in range(1, 17)] +
    ["Conclusion"]
)

def get_images(part_dir):
    """Return sorted list of image filenames in part_dir/images/."""
    img_dir = os.path.join(part_dir, "images")
    if not os.path.isdir(img_dir):
        return []
    imgs = sorted(f for f in os.listdir(img_dir) if f.endswith(".png"))
    return imgs

def md_to_latex(md_path):
    """Use pandoc to convert markdown to LaTeX fragment."""
    result = subprocess.run(
        ["pandoc", md_path, "-t", "latex", "--wrap=none"],
        capture_output=True, text=True
    )
    return result.stdout

def process_illustrations(latex_text, part_name, images):
    """Replace [ILLUSTRATION: ...] markers with \\includegraphics commands."""
    img_idx = 0
    
    def replacer(match):
        nonlocal img_idx
        caption_text = match.group(1).strip()
        # Strip any LaTeX math from caption for simplicity - keep it actually
        if img_idx < len(images):
            img_file = images[img_idx]
            img_path = f"{part_name}/images/{img_file}"
            img_idx += 1
            # Clean caption: remove problematic LaTeX from caption text
            # Keep it simple
            clean_caption = caption_text
            # Truncate very long captions
            if len(clean_caption) > 300:
                # Find a good break point
                clean_caption = clean_caption[:297] + "..."
            result = (
                f"\n\\begin{{figure}}[htbp]\n"
                f"\\centering\n"
                f"\\includegraphics[width=0.85\\textwidth]{{{img_path}}}\n"
                f"\\caption{{{clean_caption}}}\n"
                f"\\end{{figure}}\n"
            )
            return result
        else:
            # No more images, just format as italic description
            return f"\n\\begin{{quote}}\\textit{{{caption_text}}}\\end{{quote}}\n"
    
    # Match [ILLUSTRATION: ...] - may span multiple lines in LaTeX output
    # After pandoc conversion, it becomes {[}ILLUSTRATION: ...{]}
    pattern = r'\{?\[?\}?ILLUSTRATION:\s*(.*?)\{?\]?\}?'
    
    # Actually, let's handle both the raw and pandoc-converted forms
    # Pandoc converts [ ] to {[} {]}
    # Pattern for pandoc output:
    latex_text = re.sub(
        r'\{?\[?\}?\s*ILLUSTRATION:\s*((?:(?!\{?\]?\}?).)*)\.?\s*\{?\]?\}?',
        replacer,
        latex_text,
        flags=re.DOTALL
    )
    
    return latex_text

def fix_chapter_heading(latex_text, part_name):
    """Convert the first \\section to \\chapter."""
    if part_name == "Introduction":
        # Make it a chapter* (unnumbered)
        latex_text = re.sub(
            r'\\section\{.*?Introduction.*?\}.*?\n',
            r'\\chapter*{Introduction: The Triangle That Swallowed the Universe}\n\\addcontentsline{toc}{chapter}{Introduction}\n\\markboth{Introduction}{Introduction}\n',
            latex_text,
            count=1
        )
        # Convert remaining \subsection to \section
        latex_text = latex_text.replace('\\subsection{', '\\section*{')
        latex_text = latex_text.replace('\\subsubsection{', '\\subsection*{')
    elif part_name == "Conclusion":
        latex_text = re.sub(
            r'\\section\{.*?Conclusion.*?\}.*?\n',
            r'\\chapter*{Conclusion: The Rosetta Stone}\n\\addcontentsline{toc}{chapter}{Conclusion}\n\\markboth{Conclusion}{Conclusion}\n',
            latex_text,
            count=1
        )
        latex_text = latex_text.replace('\\subsection{', '\\section*{')
        latex_text = latex_text.replace('\\subsubsection{', '\\subsection*{')
    elif part_name.startswith("Chapter"):
        num = part_name.replace("Chapter", "")
        # Extract chapter title from the section heading
        m = re.search(r'\\section\{\\texorpdfstring\{(.*?)\}\{(.*?)\}\}', latex_text)
        if m:
            title_tex = m.group(1)
            title_plain = m.group(2)
            # Remove "Chapter N --- " prefix from title
            title_tex = re.sub(r'Chapter\s+\d+\s*[-—]+\s*', '', title_tex)
            title_plain = re.sub(r'Chapter\s+\d+\s*[-—]+\s*', '', title_plain)
            old_section = m.group(0)
            new_chapter = f'\\chapter{{\\texorpdfstring{{{title_tex}}}{{{title_plain}}}}}'
            latex_text = latex_text.replace(old_section, new_chapter, 1)
        else:
            # Simpler heading
            m2 = re.search(r'\\section\{(.*?)\}', latex_text)
            if m2:
                title = m2.group(1)
                title = re.sub(r'Chapter\s+\d+\s*[-—]+\s*', '', title)
                latex_text = latex_text.replace(m2.group(0), f'\\chapter{{{title}}}', 1)
        
        # Convert subsections to sections
        latex_text = latex_text.replace('\\subsection{', '\\section{')
        latex_text = latex_text.replace('\\subsubsection{', '\\subsection{')
    
    # Remove label lines that pandoc generates
    latex_text = re.sub(r'\\label\{[^}]*\}\n?', '', latex_text)
    
    return latex_text

def build_master_latex():
    """Build the complete LaTeX document."""
    
    chapter_includes = []
    
    for part_name in PARTS:
        part_dir = os.path.join(PROJECT, part_name)
        md_file = os.path.join(part_dir, f"{part_name}.md")
        
        if not os.path.exists(md_file):
            print(f"Warning: {md_file} not found, skipping")
            continue
        
        print(f"Processing {part_name}...")
        
        # Convert markdown to latex
        latex_text = md_to_latex(md_file)
        
        # Get images
        images = get_images(part_dir)
        
        # Process illustrations
        latex_text = process_illustrations(latex_text, part_name, images)
        
        # Fix headings
        latex_text = fix_chapter_heading(latex_text, part_name)
        
        # Remove horizontal rules that pandoc generates
        latex_text = latex_text.replace(
            '\\begin{center}\\rule{0.5\\linewidth}{0.5pt}\\end{center}',
            '\\bigskip\\noindent\\rule{\\linewidth}{0.4pt}\\bigskip'
        )
        
        # Write individual chapter tex file
        tex_file = os.path.join(PROJECT, f"{part_name}.tex")
        with open(tex_file, 'w') as f:
            f.write(latex_text)
        
        chapter_includes.append(f"\\input{{{part_name}.tex}}")
    
    # Build master document
    master = r"""\documentclass[11pt,a4paper,openany]{book}

% Encoding and fonts
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{microtype}

% Math
\usepackage{amsmath,amssymb,amsthm}

% Graphics
\usepackage{graphicx}
\usepackage{xcolor}

% Tables
\usepackage{longtable,booktabs,array}

% Links
\usepackage[colorlinks=true,linkcolor=blue!60!black,urlcolor=blue!70!black,citecolor=green!50!black]{hyperref}

% Page geometry
\usepackage[margin=1in]{geometry}

% Headers
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE]{\textit{\nouppercase{\leftmark}}}
\fancyhead[RO]{\textit{\nouppercase{\rightmark}}}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

% Chapter styling
\usepackage{titlesec}
\titleformat{\chapter}[display]
  {\normalfont\huge\bfseries}
  {\chaptertitlename\ \thechapter}{20pt}{\Huge}
\titlespacing*{\chapter}{0pt}{-20pt}{40pt}

% Quote styling
\usepackage{csquotes}

% Float placement
\usepackage{float}

% Caption styling  
\usepackage[font=small,labelfont=bf]{caption}

% Allow wider figures
\setlength{\textfloatsep}{12pt plus 2pt minus 2pt}

% Fix for pandoc's tightlist
\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

% Custom colors for the book
\definecolor{chaptercolor}{RGB}{0,51,102}

\begin{document}

% ---- Title page ----
\begin{titlepage}
\centering
\vspace*{2cm}
{\Huge\bfseries\color{chaptercolor} The Triangle That\\[0.3cm] Swallowed the Universe\par}
\vspace{1.5cm}
{\Large\itshape Pythagorean Triples, Spacetime Geometry,\\[0.2cm] and the Hidden Architecture of Numbers\par}
\vspace{3cm}
{\large A Mathematical Journey in Sixteen Chapters\par}
\vfill
\vspace{1cm}
\end{titlepage}

% ---- Front matter ----
\frontmatter
\tableofcontents
\clearpage

% ---- Main matter ----
\mainmatter

"""
    
    master += "\n".join(chapter_includes)
    
    master += r"""

% ---- Back matter ----
\backmatter

\end{document}
"""
    
    master_path = os.path.join(PROJECT, "book.tex")
    with open(master_path, 'w') as f:
        f.write(master)
    
    print(f"Master LaTeX file written to {master_path}")
    return master_path

if __name__ == "__main__":
    build_master_latex()
