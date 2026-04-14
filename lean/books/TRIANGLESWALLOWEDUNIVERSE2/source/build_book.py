#!/usr/bin/env python3
"""
Convert all Markdown chapters into a single LaTeX book and compile to PDF.
Author: Paul Klemstine
"""

import re
import os
import glob

PROJECT = "/workspace/request-project"

PARTS = [("Introduction", "Introduction/Introduction.md", "Introduction/images")]
for i in range(1, 17):
    PARTS.append((f"Chapter{i}", f"Chapter{i}/Chapter{i}.md", f"Chapter{i}/images"))
PARTS.append(("Conclusion", "Conclusion/Conclusion.md", "Conclusion/images"))

UNICODE_MAP = [
    ('\U0001F389', r'{$\star$}'),
    ('\u2713', r'{$\checkmark$}'),
    ('\u2717', r'{$\times$}'),
    ('\U0001F3C6', r'{$\bigstar$}'),
    ('\U0001F422', r'{$\sim$}'),
    ('\u220E', r'{$\blacksquare$}'),
    ('\u274C', r'{$\times$}'),
    ('\u2605', r'{$\bigstar$}'),
    ('\u2192', r'{$\to$}'),
    ('\u2190', r'{$\leftarrow$}'),
    ('\u2194', r'{$\leftrightarrow$}'),
    ('\u2248', r'{$\approx$}'),
    ('\u2264', r'{$\leq$}'),
    ('\u2265', r'{$\geq$}'),
    ('\u2260', r'{$\neq$}'),
    ('\u00D7', r'{$\times$}'),
    ('\u00F7', r'{$\div$}'),
    ('\u00B1', r'{$\pm$}'),
    ('\u221E', r'{$\infty$}'),
    ('\u2026', r'{\ldots}'),
    ('\u2013', '--'),
    ('\u2014', '---'),
    ('\u201C', '``'),
    ('\u201D', "''"),
    ('\u2018', '`'),
    ('\u2019', "'"),
    ('\u00B7', r'{$\cdot$}'),
    ('\u2022', r'{$\bullet$}'),
    ('\u2003', '~'),
    ('\u2002', '~'),
    ('\u00A0', '~'),
    ('\u00B0', r'\ensuremath{^{\circ}}'),
]


def replace_unicode(text):
    for char, rep in UNICODE_MAP:
        text = text.replace(char, rep)
    return text


def split_table_row(line):
    """Split a markdown table row on | but respect $...$ math mode."""
    line = line.strip()
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]
    cells = []
    current = ""
    in_math = False
    for c in line:
        if c == '$':
            in_math = not in_math
            current += c
        elif c == '|' and not in_math:
            cells.append(current.strip())
            current = ""
        else:
            current += c
    cells.append(current.strip())
    return cells


def process_inline(text):
    """Process inline markdown formatting to LaTeX, respecting math mode."""
    text = replace_unicode(text)
    segments = []
    current = ""
    i = 0
    in_math = False
    while i < len(text):
        c = text[i]
        if c == '$' and not in_math:
            segments.append(('text', current))
            current = '$'
            in_math = True
            i += 1
        elif c == '$' and in_math:
            current += '$'
            segments.append(('math', current))
            current = ''
            in_math = False
            i += 1
        elif c == '\\' and i + 1 < len(text) and not in_math:
            current += c + text[i+1]
            i += 2
        else:
            current += c
            i += 1
    if current:
        segments.append(('text' if not in_math else 'math', current))
    result_parts = []
    for seg_type, seg_text in segments:
        if seg_type == 'text':
            seg_text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\\textbf{\\textit{\1}}', seg_text)
            seg_text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', seg_text)
            seg_text = re.sub(r'\*([^\*\n]+?)\*', r'\\textit{\1}', seg_text)
        result_parts.append(seg_text)
    return ''.join(result_parts)


def process_table_cell(text):
    """Process a table cell - process_inline + escape &."""
    result = process_inline(text)
    out = ""
    in_math = False
    for c in result:
        if c == '$':
            in_math = not in_math
            out += c
        elif c == '&' and not in_math:
            out += r'\&'
        else:
            out += c
    return out


def escape_latex_text_in_caption(text):
    text = replace_unicode(text)
    result = []
    in_math = False
    for c in text:
        if c == '$':
            in_math = not in_math
            result.append(c)
        elif not in_math:
            if c == '&':
                result.append(r'\&')
            elif c == '%':
                result.append(r'\%')
            elif c == '#':
                result.append(r'\#')
            elif c == '_':
                result.append(r'\_')
            else:
                result.append(c)
        else:
            result.append(c)
    return ''.join(result)


def illustration_block_complete(text):
    start = text.find('[ILLUSTRATION')
    if start < 0:
        return False
    in_math = False
    depth = 0
    for j in range(start, len(text)):
        c = text[j]
        if c == '$':
            in_math = not in_math
        elif not in_math:
            if c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    return True
    return False


def extract_illustration_caption(text):
    start = text.find('[ILLUSTRATION')
    if start < 0:
        return "Illustration"
    colon_pos = text.find(':', start + 13)
    if colon_pos < 0:
        return "Illustration"
    in_math = False
    depth = 0
    for j in range(start, len(text)):
        c = text[j]
        if c == '$':
            in_math = not in_math
        elif not in_math:
            if c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    return text[colon_pos+1:j].strip()
    return text[colon_pos+1:].strip()


def get_image_files(img_dir):
    full_path = os.path.join(PROJECT, img_dir)
    if not os.path.isdir(full_path):
        return []
    return sorted(glob.glob(os.path.join(full_path, "*.png")))


def md_to_latex(md_text, img_dir, part_name):
    lines = md_text.split('\n')
    image_files = get_image_files(img_dir)
    img_idx = 0
    latex_lines = []
    in_table = False
    table_rows = []
    in_blockquote = False
    skip_title = True
    i = 0
    while i < len(lines):
        line = lines[i]
        if skip_title and line.startswith('# '):
            skip_title = False
            i += 1
            continue
        if '[ILLUSTRATION:' in line or '[ILLUSTRATION :' in line:
            illustration_text = line
            while not illustration_block_complete(illustration_text) and i + 1 < len(lines):
                i += 1
                illustration_text += ' ' + lines[i]
            caption = extract_illustration_caption(illustration_text)
            caption = caption.replace('\n', ' ')
            caption = escape_latex_text_in_caption(caption)
            if img_idx < len(image_files):
                img_path = os.path.relpath(image_files[img_idx], PROJECT)
                latex_lines.append('')
                latex_lines.append(r'\begin{figure}[htbp]')
                latex_lines.append(r'\centering')
                latex_lines.append(r'\includegraphics[width=0.85\textwidth,height=0.75\textheight,keepaspectratio]{' + img_path + '}')
                latex_lines.append(r'\caption{' + caption + '}')
                latex_lines.append(r'\end{figure}')
                latex_lines.append('')
                img_idx += 1
            else:
                latex_lines.append('')
                latex_lines.append(r'\begin{quote}')
                latex_lines.append(r'\textit{[Illustration: ' + caption + ']}')
                latex_lines.append(r'\end{quote}')
                latex_lines.append('')
            i += 1
            continue
        if in_blockquote and not line.startswith('>'):
            latex_lines.append(r'\end{quote}')
            latex_lines.append('')
            in_blockquote = False
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                in_table = True
                table_rows = []
            if re.match(r'^\s*\|[\s\-:|]+\|\s*$', line):
                i += 1
                continue
            cells = split_table_row(line)
            table_rows.append(cells)
            if i + 1 >= len(lines) or not lines[i+1].strip().startswith('|'):
                if table_rows:
                    ncols = max(len(r) for r in table_rows)
                    col_spec = '|' + '|'.join(['c'] * ncols) + '|'
                    latex_lines.append('')
                    latex_lines.append(r'\begin{center}')
                    latex_lines.append(r'\begin{tabular}{' + col_spec + '}')
                    latex_lines.append(r'\hline')
                    for ri, row in enumerate(table_rows):
                        while len(row) < ncols:
                            row.append('')
                        row_text = ' & '.join(process_table_cell(c) for c in row) + r' \\'
                        latex_lines.append(row_text)
                        if ri == 0:
                            latex_lines.append(r'\hline')
                    latex_lines.append(r'\hline')
                    latex_lines.append(r'\end{tabular}')
                    latex_lines.append(r'\end{center}')
                    latex_lines.append('')
                in_table = False
                table_rows = []
            i += 1
            continue
        if line.startswith('>'):
            content = line.lstrip('>').strip()
            if not in_blockquote:
                in_blockquote = True
                latex_lines.append('')
                latex_lines.append(r'\begin{quote}')
            if content:
                latex_lines.append(process_inline(content))
            else:
                latex_lines.append('')
            i += 1
            continue
        if line.startswith('## '):
            latex_lines.append('')
            latex_lines.append(r'\section*{' + process_inline(line[3:].strip()) + '}')
            latex_lines.append('')
            i += 1
            continue
        if line.startswith('### '):
            latex_lines.append('')
            latex_lines.append(r'\subsection*{' + process_inline(line[4:].strip()) + '}')
            latex_lines.append('')
            i += 1
            continue
        if line.startswith('#### '):
            latex_lines.append('')
            latex_lines.append(r'\paragraph{' + process_inline(line[5:].strip()) + '}')
            latex_lines.append('')
            i += 1
            continue
        if re.match(r'^---+\s*$', line.strip()):
            latex_lines.append('')
            latex_lines.append(r'\bigskip\noindent\rule{\textwidth}{0.4pt}\bigskip')
            latex_lines.append('')
            i += 1
            continue
        if line.strip().startswith('$$'):
            math_content = line.strip()
            if math_content == '$$':
                math_lines = []
                i += 1
                while i < len(lines) and lines[i].strip() != '$$':
                    math_lines.append(lines[i])
                    i += 1
                latex_lines.append(r'\[')
                latex_lines.extend(math_lines)
                latex_lines.append(r'\]')
            elif math_content.endswith('$$') and len(math_content) > 4:
                latex_lines.append(r'\[')
                latex_lines.append(math_content[2:-2])
                latex_lines.append(r'\]')
            else:
                math_lines = [math_content[2:]]
                i += 1
                while i < len(lines):
                    l = lines[i]
                    if '$$' in l:
                        idx = l.index('$$')
                        math_lines.append(l[:idx])
                        break
                    math_lines.append(l)
                    i += 1
                latex_lines.append(r'\[')
                latex_lines.extend(math_lines)
                latex_lines.append(r'\]')
            i += 1
            continue
        if line.strip() == '':
            latex_lines.append('')
            i += 1
            continue
        latex_lines.append(process_inline(line))
        i += 1
    if in_blockquote:
        latex_lines.append(r'\end{quote}')
    return '\n'.join(latex_lines)


def get_chapter_title(md_text):
    for line in md_text.split('\n'):
        if line.startswith('# '):
            title = line[2:].strip()
            title = replace_unicode(title)
            title = re.sub(r'\*(.+?)\*', r'\\textit{\1}', title)
            return title
    return "Untitled"


PREAMBLE = r"""\documentclass[12pt, letterpaper, openany]{book}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath, amssymb, amsthm, mathtools}
\usepackage{graphicx}
\graphicspath{{./}}
\usepackage[dvipsnames]{xcolor}
\usepackage[margin=1in, headheight=15pt]{geometry}
\usepackage{setspace}
\onehalfspacing
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE]{\leftmark}
\fancyhead[RO]{\rightmark}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\usepackage[colorlinks=true, linkcolor=MidnightBlue, urlcolor=MidnightBlue, citecolor=MidnightBlue]{hyperref}
\usepackage[font=small, labelfont=bf, skip=8pt]{caption}
\usepackage{csquotes}
\usepackage{booktabs}
\usepackage{array}
\usepackage{titlesec}
\titleformat{\chapter}[display]
  {\normalfont\huge\bfseries}{\chaptertitlename\ \thechapter}{20pt}{\Huge}
\titlespacing*{\chapter}{0pt}{-20pt}{40pt}

\newtheorem{theorem}{Theorem}[chapter]
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{corollary}[theorem]{Corollary}
\theoremstyle{definition}
\newtheorem{definition}[theorem]{Definition}
\theoremstyle{remark}
\newtheorem{remark}[theorem]{Remark}

\allowdisplaybreaks

\begin{document}

\begin{titlepage}
\centering
\vspace*{2cm}
{\Huge\bfseries The Triangle That\\[0.3em] Swallowed the Universe\par}
\vspace{1.5cm}
{\Large\itshape From Pythagorean Triples to Spacetime Symmetry\\[0.3em]
--- and the Tree That Connects Them All\par}
\vspace{3cm}
{\LARGE Paul Klemstine\par}
\vfill
{\large\itshape Soli Deo Gloria\par}
\vspace{2cm}
\end{titlepage}

\thispagestyle{empty}
\vspace*{\fill}
\begin{center}
\Large\itshape
Dedicated to God\\[1em]
\normalsize
\textit{Soli Deo Gloria}\\[0.5em]
--- To God Alone Be the Glory ---
\end{center}
\vspace*{\fill}
\newpage

\tableofcontents
\newpage

"""


def build_latex():
    body_parts = []
    for idx, (part_name, md_path, img_dir) in enumerate(PARTS):
        full_md_path = os.path.join(PROJECT, md_path)
        with open(full_md_path, 'r', encoding='utf-8') as f:
            md_text = f.read()
        title = get_chapter_title(md_text)
        if part_name == "Introduction":
            body_parts.append(r'\chapter*{' + title + '}')
            body_parts.append(r'\addcontentsline{toc}{chapter}{Introduction}')
            body_parts.append(r'\markboth{Introduction}{Introduction}')
        elif part_name == "Conclusion":
            body_parts.append(r'\chapter*{' + title + '}')
            body_parts.append(r'\addcontentsline{toc}{chapter}{Conclusion}')
            body_parts.append(r'\markboth{Conclusion}{Conclusion}')
        else:
            body_parts.append(r'\chapter{' + title + '}')
        body_parts.append('')
        body_parts.append(md_to_latex(md_text, img_dir, part_name))
        body_parts.append('')
        body_parts.append(r'\clearpage')
        body_parts.append('')
    return PREAMBLE + '\n'.join(body_parts) + '\n\\end{document}\n'


if __name__ == '__main__':
    print("Building LaTeX document...")
    latex_content = build_latex()
    output_path = os.path.join(PROJECT, "book.tex")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    print(f"LaTeX file written to {output_path}")
    print(f"Total length: {len(latex_content)} characters")
