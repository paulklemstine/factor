#!/usr/bin/env python3
"""Convert chapter markdown files to LaTeX - v2 with proper math handling."""
import re
import os

def process_inline(text):
    """Process inline markdown formatting, protecting math mode content."""
    # Use regex to split on math delimiters
    # Pattern matches $...$ (not $$)
    parts = re.split(r'(\$[^$\n]+?\$)', text)
    result = []
    for p in parts:
        if p.startswith('$') and p.endswith('$') and len(p) > 1:
            # Math content - pass through unchanged
            result.append(p)
        else:
            # Non-math content - apply formatting
            p = re.sub(r'\*\*\*(.+?)\*\*\*', r'\\textbf{\\textit{\1}}', p)
            p = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', p)
            p = re.sub(r'(?<!\w)\*([^*\n]+?)\*(?!\w)', r'\\textit{\1}', p)
            p = p.replace('&', '\\&')
            p = p.replace('%', '\\%')
            p = p.replace('#', '\\#')
            p = p.replace('—', '---')
            p = p.replace('–', '--')
            p = p.replace('\u2018', '`')
            p = p.replace('\u2019', "'")
            p = p.replace('\u201c', '``')
            p = p.replace('\u201d', "''")
            result.append(p)
    return ''.join(result)


def safe_caption(text, max_len=160):
    """Create balanced, truncated caption."""
    text = process_inline(text)
    if len(text) <= max_len:
        return ensure_balanced(text)
    depth = 0
    dollar = 0
    last_safe = 80
    for i, c in enumerate(text[:max_len]):
        if c == '{': depth += 1
        elif c == '}': depth -= 1
        elif c == '$': dollar += 1
        if depth == 0 and dollar % 2 == 0 and i > 50:
            last_safe = i + 1
    return ensure_balanced(text[:last_safe])


def ensure_balanced(text):
    depth = 0
    dollar = 0
    for c in text:
        if c == '{': depth += 1
        elif c == '}': depth -= 1
        elif c == '$': dollar += 1
    while depth > 0: text += '}'; depth -= 1
    if dollar % 2 == 1: text += '$'
    return text


def md_to_latex(md_text, chapter_dir):
    lines = md_text.split('\n')
    output = []
    figure_counter = 0

    img_dir = os.path.join(chapter_dir, 'images')
    available_images = set()
    if os.path.isdir(img_dir):
        for f in os.listdir(img_dir):
            if f.endswith('.png') and 'Zone' not in f:
                available_images.add(f)

    i = 0
    in_display_math = False
    math_buffer = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Multi-line display math continuation
        if in_display_math:
            if stripped.endswith('$$'):
                math_buffer.append(stripped[:-2])
                math_content = '\n'.join(l for l in math_buffer if l.strip())
                output.append('\\[')
                output.append(math_content)
                output.append('\\]')
                in_display_math = False
                math_buffer = []
            else:
                math_buffer.append(stripped)
            i += 1
            continue

        if stripped == '':
            output.append('')
            i += 1
            continue

        if stripped == '---':
            output.append('\\bigskip')
            i += 1
            continue

        # Chapter title - skip
        if re.match(r'^#\s+', line) and not re.match(r'^##\s+', line):
            i += 1
            continue

        # Section headers
        if re.match(r'^##\s+', line):
            title = re.sub(r'^##\s+', '', stripped)
            title = re.sub(r'^§?\d+\.?\s*', '', title)
            output.append(f'\\section*{{{process_inline(title)}}}')
            i += 1
            continue

        if re.match(r'^###\s+', line):
            title = re.sub(r'^###\s+', '', stripped)
            output.append(f'\\subsection*{{{process_inline(title)}}}')
            i += 1
            continue

        if re.match(r'^####\s+', line):
            title = re.sub(r'^####\s+', '', stripped)
            output.append(f'\\paragraph{{{process_inline(title)}}}')
            i += 1
            continue

        # ILLUSTRATION
        if stripped.startswith('[ILLUSTRATION:'):
            desc = stripped
            while not desc.endswith(']'):
                i += 1
                if i < len(lines):
                    desc += ' ' + lines[i].strip()
                else:
                    desc += ']'
                    break
            desc_text = desc[14:-1].strip()

            figure_counter += 1
            fig_name = None
            fig_str = f'fig{figure_counter:02d}'
            for img_f in sorted(available_images):
                if img_f.startswith(fig_str):
                    fig_name = img_f
                    break

            if fig_name:
                rel_path = os.path.join(chapter_dir, 'images', fig_name)
                cap = safe_caption(desc_text)
                output.append('')
                output.append('\\begin{figure}[htbp]')
                output.append('\\centering')
                output.append(f'\\includegraphics[width=0.85\\textwidth]{{{rel_path}}}')
                output.append(f'\\caption{{{cap}}}')
                output.append('\\end{figure}')
                output.append('')

            i += 1
            continue

        # Display math
        if stripped.startswith('$$'):
            rest = stripped[2:]
            if rest.endswith('$$') and len(rest) > 2:
                output.append('\\[')
                output.append(rest[:-2])
                output.append('\\]')
                i += 1
                continue
            else:
                in_display_math = True
                math_buffer = [rest] if rest.strip() else []
                i += 1
                continue

        # Tables
        if stripped.startswith('|') and stripped.count('|') >= 2:
            rows = [stripped]
            i += 1
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append(lines[i].strip())
                i += 1

            headers = [c.strip() for c in rows[0].strip('|').split('|')]
            ncols = len(headers)
            data_rows = [r for r in rows[1:] if not re.match(r'^\|[\s\-:|]+\|$', r)]

            output.append('\\begin{center}')
            output.append('\\small')
            output.append('\\begin{tabular}{' + ' '.join(['c'] * ncols) + '}')
            output.append('\\toprule')
            output.append(' & '.join(process_inline(h) for h in headers) + ' \\\\')
            output.append('\\midrule')
            for row in data_rows:
                cells = [c.strip() for c in row.strip('|').split('|')]
                output.append(' & '.join(process_inline(c) for c in cells[:ncols]) + ' \\\\')
            output.append('\\bottomrule')
            output.append('\\end{tabular}')
            output.append('\\end{center}')
            continue

        # Blockquotes
        if stripped.startswith('> '):
            quote_lines = []
            while i < len(lines) and (lines[i].strip().startswith('> ') or lines[i].strip() == '>'):
                ql = lines[i].strip()
                quote_lines.append(ql[2:] if len(ql) > 2 else '')
                i += 1
            output.append('')
            output.append('\\begin{displayquote}')
            for ql in quote_lines:
                output.append(process_inline(ql))
            output.append('\\end{displayquote}')
            output.append('')
            continue

        # Regular text
        output.append(process_inline(stripped))
        i += 1

    return '\n'.join(output)


def get_chapter_title(md_text):
    for line in md_text.split('\n'):
        if line.startswith('# ') and not line.startswith('## '):
            t = line[2:].strip()
            t = re.sub(r'^Chapter\s+\d+\s*[—–\-]\s*', '', t)
            return t.strip('*')
    return "Untitled"


def get_chapter_subtitle(md_text):
    found = False
    for line in md_text.split('\n'):
        if line.startswith('# ') and not line.startswith('## '):
            found = True
            continue
        if found and line.startswith('### '):
            return line[4:].strip().strip('*')
        if found and line.strip() and not line.startswith('#') and line.strip() != '---':
            break
    return None


if __name__ == '__main__':
    base = '/workspace/request-project'

    # Introduction
    with open(f'{base}/Introduction/Introduction.md') as f:
        md = f.read()
    tex = md_to_latex(md, f'{base}/Introduction')
    with open(f'{base}/book/introduction.tex', 'w') as f:
        f.write('\\chapter*{The Triangle That Swallowed the Universe}\n')
        f.write('\\addcontentsline{toc}{chapter}{Introduction: The Triangle That Swallowed the Universe}\n')
        f.write('\\markboth{Introduction}{Introduction}\n\n')
        f.write(tex)
    print("Converted Introduction")

    for i in range(1, 17):
        with open(f'{base}/Chapter{i}/Chapter{i}.md') as f:
            md = f.read()
        title = get_chapter_title(md)
        subtitle = get_chapter_subtitle(md)
        tex = md_to_latex(md, f'{base}/Chapter{i}')

        with open(f'{base}/book/chapter{i}.tex', 'w') as f:
            safe_title = process_inline(title)
            f.write(f'\\chapter{{{safe_title}}}\n')
            if subtitle:
                sub_clean = process_inline(subtitle)
                f.write(f'\\begin{{center}}\\textit{{{sub_clean}}}\\end{{center}}\n\\bigskip\n')
            f.write(tex)
        print(f"Converted Chapter {i}: {title}")

    # Conclusion
    with open(f'{base}/Conclusion/Conclusion.md') as f:
        md = f.read()
    tex = md_to_latex(md, f'{base}/Conclusion')
    with open(f'{base}/book/conclusion.tex', 'w') as f:
        f.write('\\chapter*{The Rosetta Stone}\n')
        f.write('\\addcontentsline{toc}{chapter}{Conclusion: The Rosetta Stone}\n')
        f.write('\\markboth{Conclusion}{Conclusion}\n\n')
        f.write(tex)
    print("Converted Conclusion")
    print("\nAll chapters converted.")
