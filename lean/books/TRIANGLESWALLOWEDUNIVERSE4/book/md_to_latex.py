#!/usr/bin/env python3
"""Convert chapter markdown files to LaTeX chapter files - simplified robust version."""
import re
import os

def process_inline(text):
    """Process inline markdown formatting."""
    # Split on $ delimiters to protect math
    parts = re.split(r'(\$\$[^$]+\$\$|\$[^$]+\$)', text)
    result_parts = []
    for p in parts:
        if p.startswith('$'):
            result_parts.append(p)
        else:
            p = re.sub(r'\*\*\*(.+?)\*\*\*', r'\\textbf{\\textit{\1}}', p)
            p = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', p)
            p = re.sub(r'(?<!\w)\*([^*]+?)\*(?!\w)', r'\\textit{\1}', p)
            p = p.replace('&', '\\&')
            p = p.replace('%', '\\%')
            p = p.replace('#', '\\#')
            p = p.replace('—', '---')
            p = p.replace('–', '--')
            p = p.replace('\u2018', '`')
            p = p.replace('\u2019', "'")
            p = p.replace('\u201c', '``')
            p = p.replace('\u201d', "''")
            result_parts.append(p)
    return ''.join(result_parts)


def make_safe_caption(text, max_len=150):
    """Create a safe caption that won't break LaTeX."""
    text = process_inline(text)
    if len(text) <= max_len:
        cap = text
    else:
        # Find safe truncation point
        depth = 0
        dollar = 0
        last_safe = 0
        for i, c in enumerate(text):
            if i > max_len:
                break
            if c == '{': depth += 1
            elif c == '}': depth -= 1
            elif c == '$': dollar += 1
            if depth == 0 and dollar % 2 == 0:
                last_safe = i + 1
        cap = text[:last_safe] if last_safe > 50 else text[:80]
    
    # Final balance
    depth = sum(1 if c == '{' else (-1 if c == '}' else 0) for c in cap)
    while depth > 0: cap += '}'; depth -= 1
    if cap.count('$') % 2 == 1: cap += '$'
    
    return cap


def md_to_latex(md_text, chapter_dir):
    """Convert markdown to LaTeX."""
    lines = md_text.split('\n')
    output = []
    figure_counter = 0
    
    # Available images
    img_dir = os.path.join(chapter_dir, 'images')
    available_images = set()
    if os.path.isdir(img_dir):
        for f in os.listdir(img_dir):
            if f.endswith('.png') and 'Zone' not in f:
                available_images.add(f)
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Skip blank lines
        if stripped == '':
            output.append('')
            i += 1
            continue
        
        # Skip horizontal rules
        if stripped == '---':
            output.append('\\bigskip')
            i += 1
            continue
        
        # Chapter title (skip - handled by main file)
        if line.startswith('# ') and not line.startswith('## '):
            i += 1
            continue
        
        # Section headers
        if line.startswith('## '):
            title = stripped[3:].strip()
            title = re.sub(r'^§?\d+\.?\s*', '', title)
            title = process_inline(title)
            output.append(f'\\section*{{{title}}}')
            i += 1
            continue
        
        if line.startswith('### '):
            title = stripped[4:].strip()
            title = process_inline(title)
            if title.startswith('\\textit{'):
                output.append(f'\\subsection*{{{title}}}')
            else:
                output.append(f'\\subsection*{{{title}}}')
            i += 1
            continue
        
        if line.startswith('#### '):
            title = stripped[5:].strip()
            title = process_inline(title)
            output.append(f'\\paragraph{{{title}}}')
            i += 1
            continue
        
        # ILLUSTRATION markers
        if stripped.startswith('[ILLUSTRATION:'):
            desc = stripped
            while not desc.endswith(']'):
                i += 1
                if i < len(lines):
                    desc += ' ' + lines[i].strip()
                else:
                    break
            desc_text = desc[14:-1].strip()
            
            figure_counter += 1
            fig_name = None
            fig_num_str = f'fig{figure_counter:02d}'
            for img_f in sorted(available_images):
                if img_f.startswith(fig_num_str):
                    fig_name = img_f
                    break
            
            cap = make_safe_caption(desc_text)
            
            if fig_name:
                rel_path = os.path.join(chapter_dir, 'images', fig_name)
                output.append('')
                output.append('\\begin{figure}[htbp]')
                output.append('\\centering')
                output.append(f'\\includegraphics[width=0.85\\textwidth]{{{rel_path}}}')
                output.append(f'\\caption{{{cap}}}')
                output.append('\\end{figure}')
                output.append('')
            
            i += 1
            continue
        
        # Display math ($$...$$)
        if stripped.startswith('$$'):
            math_content = stripped[2:]
            if math_content.endswith('$$') and len(math_content) > 2:
                # Single line
                output.append('\\[')
                output.append(math_content[:-2])
                output.append('\\]')
            else:
                # Multi-line
                math_lines = [math_content]
                i += 1
                while i < len(lines):
                    ml = lines[i].strip()
                    if ml.endswith('$$'):
                        math_lines.append(ml[:-2])
                        break
                    math_lines.append(ml)
                    i += 1
                output.append('\\[')
                output.append('\n'.join(math_lines))
                output.append('\\]')
            i += 1
            continue
        
        # Tables
        if stripped.startswith('|') and '|' in stripped[1:]:
            rows = [stripped]
            i += 1
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append(lines[i].strip())
                i += 1
            
            # Parse header
            headers = [c.strip() for c in rows[0].strip('|').split('|')]
            ncols = len(headers)
            
            # Skip separator row
            data_rows = [r for r in rows[1:] if not re.match(r'^\|[\s\-:]+\|$', r)]
            
            output.append('\\begin{center}')
            output.append('\\begin{tabular}{' + '|'.join(['c']*ncols) + '}')
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
                if ql == '>':
                    quote_lines.append('')
                else:
                    quote_lines.append(ql[2:])
                i += 1
            
            output.append('')
            output.append('\\begin{displayquote}')
            for ql in quote_lines:
                output.append(process_inline(ql))
            output.append('\\end{displayquote}')
            output.append('')
            continue
        
        # Regular paragraph text
        output.append(process_inline(stripped))
        i += 1
    
    return '\n'.join(output)


def get_chapter_title(md_text):
    for line in md_text.split('\n'):
        if line.startswith('# '):
            title = line[2:].strip()
            title = re.sub(r'^Chapter\s+\d+\s*[—–\-]\s*', '', title)
            title = title.strip('*')
            return title
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
            safe_title = title.replace('&', '\\&').replace('%', '\\%')
            f.write(f'\\chapter{{{safe_title}}}\n')
            if subtitle:
                sub_clean = subtitle.replace('&', '\\&').replace('%', '\\%').replace('—', '---').replace('–', '--')
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
