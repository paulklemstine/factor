#!/usr/bin/env python3
"""Convert the book's Markdown chapters to LaTeX chapter files.
   Robust version with careful handling of math, captions, and special chars."""

import re
import os

DOLLAR = '$'

def safe_caption(text, max_len=200):
    """Truncate a caption safely without breaking LaTeX commands or math mode."""
    if len(text) <= max_len:
        return text
    depth_brace = 0
    depth_math = 0
    last_safe = 0
    i = 0
    while i < len(text) and i < max_len:
        ch = text[i]
        if ch == '{':
            depth_brace += 1
        elif ch == '}':
            depth_brace -= 1
        elif ch == DOLLAR:
            depth_math = 1 - depth_math
        if depth_brace == 0 and depth_math == 0:
            if ch in (' ', ',', '.', ';'):
                last_safe = i
        i += 1
    if last_safe > 50:
        return text[:last_safe] + '\\ldots'
    return text[:max_len]


def process_inline(text):
    """Process inline markdown formatting, respecting math mode."""
    parts = text.split(DOLLAR)
    for idx in range(len(parts)):
        if idx % 2 == 0:  # text mode only
            p = parts[idx]
            p = re.sub(r'\*\*\*(.*?)\*\*\*', r'\\textbf{\\textit{\1}}', p)
            p = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', p)
            p = re.sub(r'(?<![\\*])\*([^*\n]+?)\*(?!\*)', r'\\textit{\1}', p)
            p = re.sub(r'(?<!\\)%', r'\\%', p)
            parts[idx] = p
    return DOLLAR.join(parts)


def md_to_latex(md_text, chapter_dir):
    """Convert markdown text to LaTeX."""
    lines = md_text.split('\n')
    out = []
    img_counter = 0
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip the first # heading (chapter title)
        if stripped.startswith('# ') and not stripped.startswith('## '):
            i += 1
            continue

        # Skip ### subtitle near top
        if stripped.startswith('### ') and i < 10:
            i += 1
            continue

        # Display math block
        if stripped.startswith(DOLLAR + DOLLAR):
            if stripped == DOLLAR + DOLLAR:
                math_lines = []
                i += 1
                while i < len(lines):
                    s = lines[i].strip()
                    if s == DOLLAR + DOLLAR or s.endswith(DOLLAR + DOLLAR):
                        end = s
                        if end != DOLLAR + DOLLAR:
                            math_lines.append(end[:end.rfind(DOLLAR + DOLLAR)])
                        break
                    math_lines.append(lines[i])
                    i += 1
                content = '\n'.join(math_lines)
                out.append('\\[')
                out.append(content)
                out.append('\\]')
                i += 1
                continue
            elif stripped.endswith(DOLLAR + DOLLAR) and len(stripped) > 4:
                content = stripped[2:-2].strip()
                out.append('\\[')
                out.append(content)
                out.append('\\]')
                i += 1
                continue
            else:
                math_lines = [stripped[2:]]
                i += 1
                while i < len(lines):
                    s = lines[i].strip()
                    if s.endswith(DOLLAR + DOLLAR):
                        if s != DOLLAR + DOLLAR:
                            math_lines.append(s[:-2])
                        break
                    math_lines.append(lines[i])
                    i += 1
                content = '\n'.join(math_lines)
                out.append('\\[')
                out.append(content)
                out.append('\\]')
                i += 1
                continue

        # Blockquote
        if stripped.startswith('>'):
            bq_lines = []
            while i < len(lines) and (lines[i].strip().startswith('>') or
                  (lines[i].strip() and bq_lines and not lines[i].strip().startswith('#'))):
                s = re.sub(r'^>\s*', '', lines[i].strip())
                bq_lines.append(s)
                i += 1
            text = ' '.join(bq_lines)
            text = process_inline(text)
            out.append('\\begin{quote}')
            out.append('\\itshape ' + text)
            out.append('\\end{quote}')
            continue

        # Table
        if stripped.startswith('|') and stripped.endswith('|') and '|' in stripped[1:-1]:
            table_rows = []
            while i < len(lines) and lines[i].strip().startswith('|') and lines[i].strip().endswith('|'):
                s = lines[i].strip()
                # Protect | inside $...$ from being parsed as column separator
                protected = []
                in_m = False
                for ch in s:
                    if ch == DOLLAR:
                        in_m = not in_m
                    if ch == '|' and in_m:
                        protected.append('\\vert ')
                    else:
                        protected.append(ch)
                s = ''.join(protected)
                cells = [c.strip() for c in s.split('|')[1:-1]]
                if all(re.match(r'^[-:]+$', c) for c in cells if c):
                    i += 1
                    continue
                table_rows.append(cells)
                i += 1
            if table_rows:
                cols = max(len(r) for r in table_rows)
                out.append('\\begin{center}')
                out.append('\\begin{tabular}{' + ' '.join(['c'] * cols) + '}')
                out.append('\\toprule')
                for j, row in enumerate(table_rows):
                    while len(row) < cols:
                        row.append('')
                    cells = [process_inline(c) for c in row]
                    out.append(' & '.join(cells) + ' \\\\')
                    if j == 0:
                        out.append('\\midrule')
                out.append('\\bottomrule')
                out.append('\\end{tabular}')
                out.append('\\end{center}')
            continue

        # Section headers
        if stripped.startswith('## '):
            title = process_inline(stripped[3:].strip())
            title = re.sub(r'^(?:Section\s+)?\d+[\.:]\s*', '', title)
            title = re.sub(r'^\S\d+[\.:]\s*', '', title)
            out.append('\\section{' + title + '}')
            i += 1
            continue
        if stripped.startswith('### '):
            title = process_inline(stripped[4:].strip())
            out.append('\\subsection*{' + title + '}')
            i += 1
            continue
        if stripped.startswith('#### '):
            title = process_inline(stripped[5:].strip())
            out.append('\\subsubsection*{' + title + '}')
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^---+$', stripped):
            out.append('')
            out.append('\\bigskip')
            out.append('')
            i += 1
            continue

        # Illustration placeholder
        if stripped.startswith('[ILLUSTRATION:'):
            caption_text = stripped
            while not caption_text.rstrip().endswith(']'):
                i += 1
                if i < len(lines):
                    caption_text += ' ' + lines[i].strip()
                else:
                    caption_text += ']'
                    break
            caption = caption_text[14:].rstrip(']').strip()
            caption = process_inline(caption)

            img_counter += 1
            img_name = f"fig{img_counter:02d}"
            img_dir = os.path.join(chapter_dir, 'images')
            img_file = None
            if os.path.isdir(img_dir):
                for f in sorted(os.listdir(img_dir)):
                    if f.startswith(img_name) and f.endswith('.png'):
                        img_file = os.path.join(img_dir, f)
                        break
            if img_file:
                rel_path = os.path.relpath(img_file, '/workspace/request-project/book')
                out.append('\\begin{figure}[htbp]')
                out.append('\\centering')
                out.append('\\includegraphics[width=0.82\\textwidth]{' + rel_path + '}')
                sc = safe_caption(caption)
                out.append('\\caption{' + sc + '}')
                out.append('\\end{figure}')
            i += 1
            continue

        # Unordered list
        if re.match(r'^[-*]\s', stripped):
            out.append('\\begin{itemize}')
            while i < len(lines):
                s = lines[i].strip()
                m = re.match(r'^[-*]\s+(.*)', s)
                if m:
                    out.append('\\item ' + process_inline(m.group(1)))
                    i += 1
                elif s == '':
                    j = i + 1
                    while j < len(lines) and lines[j].strip() == '':
                        j += 1
                    if j < len(lines) and re.match(r'^[-*]\s', lines[j].strip()):
                        i = j
                        continue
                    else:
                        i += 1
                        break
                else:
                    break
            out.append('\\end{itemize}')
            continue

        # Ordered list
        if re.match(r'^\d+\.\s', stripped):
            out.append('\\begin{enumerate}')
            while i < len(lines):
                s = lines[i].strip()
                m = re.match(r'^\d+\.\s+(.*)', s)
                if m:
                    out.append('\\item ' + process_inline(m.group(1)))
                    i += 1
                elif s == '':
                    j = i + 1
                    while j < len(lines) and lines[j].strip() == '':
                        j += 1
                    if j < len(lines) and re.match(r'^\d+\.\s', lines[j].strip()):
                        i = j
                        continue
                    else:
                        i += 1
                        break
                else:
                    break
            out.append('\\end{enumerate}')
            continue

        # Empty line
        if stripped == '':
            out.append('')
            i += 1
            continue

        # Regular paragraph
        out.append(process_inline(stripped))
        i += 1

    return '\n'.join(out)


def extract_title(md_text):
    for line in md_text.split('\n'):
        if line.strip().startswith('# '):
            title = line.strip()[2:].strip()
            title = re.sub(r'^Chapter\s+\d+\s*[\u2014\u2013-]\s*', '', title)
            title = process_inline(title)
            return title
    return "Untitled"


def extract_subtitle(md_text):
    for line in md_text.split('\n')[:10]:
        s = line.strip()
        if s.startswith('### '):
            title = s[4:].strip()
            title = process_inline(title)
            return title
    return None


def process_all():
    base = '/workspace/request-project'
    book_dir = '/workspace/request-project/book'

    chapters = [
        ('Introduction', 'intro', False),
        ('Chapter1', 'ch01', True),
        ('Chapter2', 'ch02', True),
        ('Chapter3', 'ch03', True),
        ('Chapter4', 'ch04', True),
        ('Chapter5', 'ch05', True),
        ('Chapter6', 'ch06', True),
        ('Chapter7', 'ch07', True),
        ('Chapter8', 'ch08', True),
        ('Chapter9', 'ch09', True),
        ('Chapter10', 'ch10', True),
        ('Chapter11', 'ch11', True),
        ('Chapter12', 'ch12', True),
        ('Chapter13', 'ch13', True),
        ('Chapter14', 'ch14', True),
        ('Chapter15', 'ch15', True),
        ('Chapter16', 'ch16', True),
        ('Conclusion', 'conclusion', False),
    ]

    for ch_name, ch_label, is_numbered in chapters:
        ch_dir = os.path.join(base, ch_name)
        md_file = os.path.join(ch_dir, ch_name + '.md')

        with open(md_file, 'r') as f:
            md_text = f.read()

        title = extract_title(md_text)
        subtitle = extract_subtitle(md_text)
        body = md_to_latex(md_text, ch_dir)

        out_file = os.path.join(book_dir, f'{ch_label}.tex')
        with open(out_file, 'w') as f:
            if ch_name == 'Introduction':
                f.write('\\chapter*{' + title + '}\n')
                f.write('\\addcontentsline{toc}{chapter}{Introduction}\n')
                f.write('\\markboth{Introduction}{Introduction}\n')
            elif ch_name == 'Conclusion':
                f.write('\\chapter*{' + title + '}\n')
                f.write('\\addcontentsline{toc}{chapter}{Conclusion}\n')
                f.write('\\markboth{Conclusion}{Conclusion}\n')
            else:
                f.write('\\chapter{' + title + '}\n')
            if subtitle:
                f.write('\\begin{center}\\large\\itshape ' + subtitle + '\\end{center}\n')
                f.write('\\medskip\n')
            f.write('\\label{' + ch_label + '}\n\n')
            f.write(body)
            f.write('\n')
        print(f'Wrote {out_file}')


if __name__ == '__main__':
    process_all()
