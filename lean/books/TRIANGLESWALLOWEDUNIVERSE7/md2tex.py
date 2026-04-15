#!/usr/bin/env python3
"""Convert the markdown chapters to LaTeX content."""
import re, os, sys, glob

def find_images(chapter_dir):
    img_dir = os.path.join(chapter_dir, "images")
    if not os.path.isdir(img_dir):
        return {}
    images = {}
    for f in sorted(os.listdir(img_dir)):
        if f.endswith('.png'):
            images[f] = os.path.join(img_dir, f)
    return images

def convert_inline(text):
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\\textbf{\\textit{\1}}', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
    parts = re.split(r'(\$[^$]+\$)', text)
    result = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            part = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\\textit{\1}', part)
        result.append(part)
    return ''.join(result)

def escape_caption(text):
    """Escape & in caption text (outside math mode)."""
    out = []
    in_math = False
    for i, ch in enumerate(text):
        if ch == '$':
            in_math = not in_math
            out.append(ch)
        elif ch == '&' and not in_math:
            if i > 0 and text[i-1] == '\\':
                out.append(ch)
            else:
                out.append('\\&')
        else:
            out.append(ch)
    return ''.join(out)

def extract_illustration(lines, start_idx):
    """Extract [ILLUSTRATION: ...] handling nested brackets in math."""
    line = lines[start_idx]
    full = line
    idx = start_idx
    # Count brackets - need to find matching ]
    bracket_depth = 0
    found_end = False
    for ch in full:
        if ch == '[':
            bracket_depth += 1
        elif ch == ']':
            bracket_depth -= 1
            if bracket_depth == 0:
                found_end = True
                break
    
    while not found_end and idx + 1 < len(lines):
        idx += 1
        full += ' ' + lines[idx]
        for ch in lines[idx]:
            if ch == '[':
                bracket_depth += 1
            elif ch == ']':
                bracket_depth -= 1
                if bracket_depth == 0:
                    found_end = True
                    break
    
    # Extract content between [ILLUSTRATION: and last ]
    m = re.match(r'\[ILLUSTRATION:\s*(.+)\]\s*$', full, re.DOTALL)
    if m:
        return m.group(1).strip(), idx
    return full, idx

def convert_md_to_tex(md_text, chapter_dir, chapter_num=None, is_intro=False, is_conclusion=False):
    lines = md_text.split('\n')
    images = find_images(chapter_dir)
    image_keys = sorted(images.keys())
    image_idx = 0
    output = []
    in_table = False
    table_lines = []
    in_blockquote = False
    in_list = False
    list_type = None
    in_display_math = False
    math_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Display math
        if line.strip() == '$$' and not in_display_math:
            in_display_math = True
            math_lines = []
            i += 1
            continue
        elif line.strip() == '$$' and in_display_math:
            in_display_math = False
            output.append('\\[')
            output.append('\n'.join(math_lines))
            output.append('\\]')
            output.append('')
            i += 1
            continue
        elif in_display_math:
            math_lines.append(line)
            i += 1
            continue
        
        # Close blockquote
        if in_blockquote and not line.startswith('>'):
            output.append('\\end{quote}')
            output.append('')
            in_blockquote = False
        
        # Close list
        if in_list and line.strip() and not re.match(r'^(\d+\.|[-*])\s', line.strip()):
            output.append('\\end{enumerate}' if list_type == 'ol' else '\\end{itemize}')
            output.append('')
            in_list = False
        
        # Table
        if '|' in line and not line.strip().startswith('[') and re.match(r'\s*\|', line):
            if not in_table:
                in_table = True
                table_lines = []
            table_lines.append(line)
            i += 1
            continue
        elif in_table:
            in_table = False
            output.append(convert_table(table_lines))
            output.append('')
        
        # Horizontal rule
        if line.strip() in ('---', '***', '___'):
            output.append('\\bigskip\\noindent\\rule{\\textwidth}{0.4pt}\\bigskip')
            output.append('')
            i += 1
            continue
        
        # Chapter title
        m = re.match(r'^#\s+(.+)', line)
        if m and not line.startswith('##'):
            title = m.group(1).strip()
            title = re.sub(r'\*(.+?)\*', r'\\textit{\1}', title)
            if is_intro:
                plain = extract_plain(title)
                output.append('\\chapter*{Introduction: ' + plain + '}')
                output.append('\\addcontentsline{toc}{chapter}{Introduction: ' + plain + '}')
                output.append('\\markboth{Introduction}{Introduction}')
            elif is_conclusion:
                plain = extract_plain(title)
                output.append('\\chapter*{Conclusion: ' + plain + '}')
                output.append('\\addcontentsline{toc}{chapter}{Conclusion: ' + plain + '}')
                output.append('\\markboth{Conclusion}{Conclusion}')
            output.append('')
            i += 1
            continue
        
        # Subsection
        m = re.match(r'^###\s+(.+)', line)
        if m:
            title = clean_heading(m.group(1))
            output.append('\\subsection*{' + title + '}')
            idx = extract_index_term(title)
            if idx:
                output.append('\\index{' + idx + '}')
            output.append('')
            i += 1
            continue
        
        # Section
        m = re.match(r'^##\s+(.+)', line)
        if m:
            title = clean_heading(m.group(1))
            sec_m = re.match(r'^(?:Section\s+)?\d+[\.:]\s*(.+)', title)
            puzzle_m = re.match(r'^(.*\d+)\.\s*(.+)', title)
            if sec_m or puzzle_m:
                output.append('\\section{' + title + '}')
            else:
                output.append('\\section*{' + title + '}')
                output.append('\\addcontentsline{toc}{section}{' + title + '}')
            idx = extract_index_term(title)
            if idx:
                output.append('\\index{' + idx + '}')
            output.append('')
            i += 1
            continue
        
        # ILLUSTRATION
        if line.strip().startswith('[ILLUSTRATION:'):
            caption_text, end_idx = extract_illustration(lines, i)
            i = end_idx
            caption_text = convert_inline(caption_text)
            caption_text = escape_caption(caption_text)
            
            if image_idx < len(image_keys):
                img_file = image_keys[image_idx]
                img_path = images[img_file]
                rel_path = os.path.relpath(img_path, '/workspace/request-project')
                output.append('\\begin{figure}[htbp]')
                output.append('\\centering')
                output.append('\\includegraphics[width=0.85\\textwidth,keepaspectratio]{' + rel_path + '}')
                output.append('\\caption{' + caption_text + '}')
                output.append('\\end{figure}')
                image_idx += 1
            else:
                output.append('\\begin{quote}\\textit{' + caption_text + '}\\end{quote}')
            output.append('')
            i += 1
            continue
        
        # Blockquote
        if line.startswith('>'):
            content = line.lstrip('>').strip()
            content = convert_inline(content)
            if not in_blockquote:
                in_blockquote = True
                output.append('\\begin{quote}')
            output.append(content)
            i += 1
            continue
        
        # Ordered list
        m = re.match(r'^(\d+)\.\s+(.+)', line.strip())
        if m:
            if not in_list or list_type != 'ol':
                if in_list:
                    output.append('\\end{enumerate}' if list_type == 'ol' else '\\end{itemize}')
                output.append('\\begin{enumerate}')
                in_list = True
                list_type = 'ol'
            output.append('\\item ' + convert_inline(m.group(2)))
            i += 1
            continue
        
        # Unordered list
        m = re.match(r'^[-*]\s+(.+)', line.strip())
        if m:
            if not in_list or list_type != 'ul':
                if in_list:
                    output.append('\\end{enumerate}' if list_type == 'ol' else '\\end{itemize}')
                output.append('\\begin{itemize}')
                in_list = True
                list_type = 'ul'
            output.append('\\item ' + convert_inline(m.group(1)))
            i += 1
            continue
        
        # Regular text
        if line.strip():
            output.append(convert_inline(line))
        else:
            if in_list:
                output.append('\\end{enumerate}' if list_type == 'ol' else '\\end{itemize}')
                in_list = False
            output.append('')
        
        i += 1
    
    if in_blockquote:
        output.append('\\end{quote}')
    if in_list:
        output.append('\\end{enumerate}' if list_type == 'ol' else '\\end{itemize}')
    if in_table:
        output.append(convert_table(table_lines))
    
    return '\n'.join(output)

def convert_table(table_lines):
    if not table_lines:
        return ''
    rows = []
    for line in table_lines:
        line = line.strip()
        if line.startswith('|'):
            line = line[1:]
        if line.endswith('|'):
            line = line[:-1]
        cells = [c.strip() for c in line.split('|')]
        rows.append(cells)
    
    data_rows = [r for r in rows if not all(re.match(r'^[-:]+$', c) for c in r)]
    if not data_rows:
        return ''
    
    ncols = max(len(r) for r in data_rows)
    col_spec = '|'.join(['c'] * ncols)
    
    out = []
    out.append('\\begin{center}')
    out.append('\\begin{tabular}{' + col_spec + '}')
    out.append('\\toprule')
    for j, row in enumerate(data_rows):
        cells = [convert_inline(c) for c in row]
        while len(cells) < ncols:
            cells.append('')
        out.append(' & '.join(cells) + ' \\\\')
        if j == 0:
            out.append('\\midrule')
    out.append('\\bottomrule')
    out.append('\\end{tabular}')
    out.append('\\end{center}')
    return '\n'.join(out)

def clean_heading(text):
    text = text.strip()
    text = re.sub(r'\*(.+?)\*', r'\\textit{\1}', text)
    return text

def extract_plain(text):
    text = re.sub(r'\\textit\{(.+?)\}', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    return text.strip()

def extract_index_term(title):
    plain = re.sub(r'\\textit\{(.+?)\}', r'\1', title)
    plain = re.sub(r'\\textbf\{(.+?)\}', r'\1', plain)
    plain = re.sub(r'[§\d.:]+\s*', '', plain).strip()
    plain = re.sub(r'^(The|A|An)\s+', '', plain)
    if 3 < len(plain) < 80:
        return plain
    return None

def process_chapter(chapter_dir, chapter_num=None, is_intro=False, is_conclusion=False):
    if is_intro:
        md_file = os.path.join(chapter_dir, "Introduction.md")
    elif is_conclusion:
        md_file = os.path.join(chapter_dir, "Conclusion.md")
    else:
        md_file = os.path.join(chapter_dir, f"Chapter{chapter_num}.md")
    with open(md_file, 'r') as f:
        md_text = f.read()
    return convert_md_to_tex(md_text, chapter_dir, chapter_num, is_intro, is_conclusion)
