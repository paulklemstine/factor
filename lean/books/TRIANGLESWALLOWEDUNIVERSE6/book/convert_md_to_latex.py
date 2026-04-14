#!/usr/bin/env python3
"""Convert the manuscript markdown files into LaTeX chapter files for the book."""

import re
import os
import glob

def protect_math_pipes(text):
    """Replace | inside $...$ with a placeholder before table parsing."""
    result = []
    in_math = False
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == '$' and (i == 0 or text[i-1] != '\\'):
            in_math = not in_math
            result.append(ch)
        elif ch == '|' and in_math:
            result.append('\x01PIPE\x01')
        else:
            result.append(ch)
        i += 1
    return ''.join(result)

def restore_pipes(text):
    """Restore pipe placeholders."""
    return text.replace('\x01PIPE\x01', '|')


def md_to_latex(md_text, chapter_dir, chapter_label):
    """Convert markdown text to LaTeX, handling math, images, formatting."""
    lines = md_text.split('\n')
    out = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip [ILLUSTRATION: ...] blocks
        if line.strip().startswith('[ILLUSTRATION:'):
            desc = line
            while not desc.strip().endswith(']'):
                i += 1
                if i < len(lines):
                    desc += ' ' + lines[i]
                else:
                    break
            i += 1
            continue
        
        # Handle tables - protect math pipes first
        protected_line = protect_math_pipes(line)
        if '|' in protected_line and protected_line.strip().startswith('|'):
            table_rows = []
            while i < len(lines):
                pl = protect_math_pipes(lines[i])
                if not ('|' in pl and pl.strip().startswith('|')):
                    break
                # Skip separator rows
                if re.match(r'^\s*\|[-\s|:]+\|\s*$', pl):
                    i += 1
                    continue
                cells = [restore_pipes(c.strip()) for c in pl.strip().strip('|').split('|')]
                table_rows.append(cells)
                i += 1
            
            if table_rows:
                ncols = max(len(r) for r in table_rows)
                col_spec = 'l' * ncols
                out.append('')
                out.append(r'\begin{center}')
                out.append(r'\begin{tabular}{' + col_spec + '}')
                out.append(r'\toprule')
                for j, row in enumerate(table_rows):
                    while len(row) < ncols:
                        row.append('')
                    row_text = ' & '.join(process_inline(c) for c in row)
                    out.append(row_text + r' \\')
                    if j == 0:
                        out.append(r'\midrule')
                out.append(r'\bottomrule')
                out.append(r'\end{tabular}')
                out.append(r'\end{center}')
                out.append('')
            continue
        
        # Handle blockquotes
        if line.strip().startswith('>'):
            bq_lines = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                bq_lines.append(lines[i].strip()[1:].strip())
                i += 1
            bq_text = ' '.join(bq_lines)
            bq_latex = process_inline(bq_text)
            out.append('')
            out.append(r'\begin{quote}')
            out.append(r'\itshape')
            out.append(bq_latex)
            out.append(r'\end{quote}')
            out.append('')
            continue
        
        # Handle headers
        if line.startswith('# '):
            i += 1
            continue
        
        if line.startswith('## '):
            title = line[3:].strip()
            # Extract clean title for section
            section_title = re.sub(r'\d+\.\s*', '', title)  # Remove numbering
            title = process_inline(title)
            out.append('')
            out.append(r'\section*{' + title + '}')
            clean = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', title)
            clean = re.sub(r'[\\${}]', '', clean)
            if clean.strip() and len(clean.strip()) < 60:
                out.append(r'\index{' + clean.strip() + '}')
            out.append('')
            i += 1
            continue
        
        if line.startswith('### '):
            title = line[4:].strip()
            title = process_inline(title)
            out.append('')
            out.append(r'\subsection*{' + title + '}')
            out.append('')
            i += 1
            continue
        
        # Horizontal rules
        if re.match(r'^-{3,}\s*$', line.strip()):
            out.append('')
            out.append(r'\bigskip\centerline{\rule{0.5\textwidth}{0.4pt}}\bigskip')
            out.append('')
            i += 1
            continue
        
        # Display math blocks
        if line.strip().startswith('$$'):
            math_content = line.strip()[2:]
            if math_content.endswith('$$'):
                math_content = math_content[:-2]
                out.append(r'\[' + math_content + r'\]')
            else:
                math_lines = [math_content]
                i += 1
                while i < len(lines) and '$$' not in lines[i]:
                    math_lines.append(lines[i])
                    i += 1
                if i < len(lines):
                    last = lines[i].replace('$$', '')
                    if last.strip():
                        math_lines.append(last)
                math_text = '\n'.join(math_lines)
                out.append(r'\[' + math_text + r'\]')
            i += 1
            continue
        
        # Empty lines
        if line.strip() == '':
            out.append('')
            i += 1
            continue
        
        # Regular paragraphs
        para = process_inline(line)
        out.append(para)
        i += 1
    
    return '\n'.join(out)


def process_inline(text):
    """Process inline markdown formatting."""
    # First, protect all math expressions
    math_parts = []
    def save_math(m):
        idx = len(math_parts)
        math_parts.append(m.group(0))
        return f'\x00MATH{idx}\x00'
    
    text = re.sub(r'\$\$[^$]+\$\$', save_math, text)
    text = re.sub(r'\$[^$]+\$', save_math, text)
    
    # Bold + italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\\textbf{\\textit{\1}}', text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
    # Italic
    text = re.sub(r'\*([^*]+?)\*', r'\\textit{\1}', text)
    
    # Escape special characters (outside math)
    text = text.replace('&', r'\&')
    text = text.replace('#', r'\#')
    text = text.replace('%', r'\%')
    text = text.replace('_', r'\_')
    
    # Restore math
    for j, mp in enumerate(math_parts):
        text = text.replace(f'\x00MATH{j}\x00', mp)
    
    # Handle em-dash and en-dash
    text = text.replace('—', '---')
    text = text.replace('–', '--')
    
    return text


def get_images_for_chapter(chapter_dir):
    """Get sorted list of PNG images for a chapter."""
    img_dir = os.path.join(chapter_dir, 'images')
    if not os.path.isdir(img_dir):
        return []
    pngs = sorted(glob.glob(os.path.join(img_dir, '*.png')))
    return pngs


def get_chapter_title(md_text):
    """Extract the chapter title from the first line."""
    for line in md_text.split('\n'):
        if line.startswith('# '):
            title = line[2:].strip()
            title = re.sub(r'\*(.+?)\*', r'\1', title)
            m = re.match(r'Chapter\s+\d+\s*[—–\-]\s*', title)
            if m:
                title = title[m.end():]
            return title
    return "Untitled"


def get_chapter_subtitle(md_text):
    """Extract subtitle (### line near top)."""
    for line in md_text.split('\n')[:10]:
        if line.startswith('### '):
            sub = line[4:].strip()
            sub = re.sub(r'\*(.+?)\*', r'\1', sub)
            return sub
    return None


def create_image_figure(img_path, chapter_rel_dir):
    """Create a LaTeX figure for an image."""
    basename = os.path.basename(img_path)
    name = os.path.splitext(basename)[0]
    name = re.sub(r'^fig\d+_', '', name)
    caption = name.replace('_', ' ').title()
    
    rel_path = os.path.join('..', chapter_rel_dir, 'images', basename)
    
    return (
        f'\n\\begin{{figure}}[htbp]\n'
        f'\\centering\n'
        f'\\includegraphics[width=0.82\\textwidth]{{{rel_path}}}\n'
        f'\\caption*{{{caption}}}\n'
        f'\\end{{figure}}\n'
    )


def process_chapter(md_path, chapter_num, chapter_dir_name):
    """Process a single chapter markdown file into LaTeX."""
    with open(md_path, 'r') as f:
        md_text = f.read()
    
    title = get_chapter_title(md_text)
    subtitle = get_chapter_subtitle(md_text)
    
    latex_content = md_to_latex(md_text, os.path.dirname(md_path), chapter_dir_name)
    images = get_images_for_chapter(os.path.dirname(md_path))
    
    chapter_tex = []
    
    if chapter_num == 0:
        chapter_tex.append(r'\chapter*{Introduction: The Triangle That Swallowed the Universe}')
        chapter_tex.append(r'\addcontentsline{toc}{chapter}{Introduction: The Triangle That Swallowed the Universe}')
        chapter_tex.append(r'\markboth{Introduction}{Introduction}')
    elif chapter_num == -1:
        chapter_tex.append(r'\chapter*{Conclusion: The Rosetta Stone}')
        chapter_tex.append(r'\addcontentsline{toc}{chapter}{Conclusion: The Rosetta Stone}')
        chapter_tex.append(r'\markboth{Conclusion}{Conclusion}')
    else:
        safe_title = process_inline(title)
        chapter_tex.append(f'\\chapter{{{safe_title}}}')
        if subtitle:
            safe_sub = process_inline(subtitle)
            chapter_tex.append(f'\\vspace{{-0.5em}}')
            chapter_tex.append(f'\\begin{{center}}\\textit{{{safe_sub}}}\\end{{center}}')
            chapter_tex.append(f'\\vspace{{1em}}')
    
    chapter_tex.append('')
    
    # Interleave images with content
    content_lines = latex_content.split('\n')
    img_latex_list = []
    for img in images:
        img_latex_list.append(create_image_figure(img, chapter_dir_name))
    
    # Insert images at section breaks
    section_indices = [i for i, l in enumerate(content_lines) 
                       if l.strip().startswith(r'\section') or l.strip().startswith(r'\subsection')]
    
    if img_latex_list and section_indices:
        result_lines = []
        img_idx = 0
        for li, cl in enumerate(content_lines):
            result_lines.append(cl)
            if li in section_indices and img_idx < len(img_latex_list):
                for _ in range(min(2, len(img_latex_list) - img_idx)):
                    result_lines.append(img_latex_list[img_idx])
                    img_idx += 1
        while img_idx < len(img_latex_list):
            result_lines.append(img_latex_list[img_idx])
            img_idx += 1
        chapter_tex.append('\n'.join(result_lines))
    else:
        chapter_tex.append(latex_content)
        for il in img_latex_list:
            chapter_tex.append(il)
    
    return '\n'.join(chapter_tex)


def main():
    base = '/workspace/request-project'
    book_dir = os.path.join(base, 'book')
    os.makedirs(book_dir, exist_ok=True)
    
    # Introduction
    intro_md = os.path.join(base, 'Introduction', 'Introduction.md')
    if os.path.exists(intro_md):
        tex = process_chapter(intro_md, 0, 'Introduction')
        with open(os.path.join(book_dir, 'ch_introduction.tex'), 'w') as f:
            f.write(tex)
    
    # Chapters 1-16
    for ch_num in range(1, 17):
        ch_dir = f'Chapter{ch_num}'
        md_path = os.path.join(base, ch_dir, f'{ch_dir}.md')
        if os.path.exists(md_path):
            tex = process_chapter(md_path, ch_num, ch_dir)
            with open(os.path.join(book_dir, f'ch_{ch_num:02d}.tex'), 'w') as f:
                f.write(tex)
    
    # Conclusion
    conc_md = os.path.join(base, 'Conclusion', 'Conclusion.md')
    if os.path.exists(conc_md):
        tex = process_chapter(conc_md, -1, 'Conclusion')
        with open(os.path.join(book_dir, 'ch_conclusion.tex'), 'w') as f:
            f.write(tex)
    
    print("All chapters converted.")


if __name__ == '__main__':
    main()
