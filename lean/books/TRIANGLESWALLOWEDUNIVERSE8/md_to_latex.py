#!/usr/bin/env python3
"""Convert markdown chapter files to LaTeX fragments."""

import re
import os
import sys

def md_to_latex(md_text, chapter_num=None, is_intro=False, is_conclusion=False):
    """Convert markdown text to LaTeX."""
    lines = md_text.split('\n')
    output = []
    in_blockquote = False
    list_stack = []
    first_heading_done = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip [ILLUSTRATION: ...] blocks
        if '[ILLUSTRATION:' in line:
            bracket_count = line.count('[') - line.count(']')
            while i < len(lines) and bracket_count > 0:
                i += 1
                if i < len(lines):
                    bracket_count += lines[i].count('[') - lines[i].count(']')
            i += 1
            continue
        
        # Skip horizontal rules
        if line.strip() == '---':
            i += 1
            continue
        
        # Handle headings
        if line.startswith('# ') and not first_heading_done:
            first_heading_done = True
            i += 1
            continue
        
        if line.startswith('### ') and not first_heading_done:
            first_heading_done = True
            i += 1
            continue
        
        if line.startswith('## '):
            close_lists(output, list_stack)
            if in_blockquote:
                output.append('\\end{quote}')
                in_blockquote = False
            heading = clean_text(line[3:].strip())
            heading = re.sub(r'^§?\d+\.\s*', '', heading)
            output.append(f'\\section{{{heading}}}')
            i += 1
            continue
        
        if line.startswith('### '):
            close_lists(output, list_stack)
            if in_blockquote:
                output.append('\\end{quote}')
                in_blockquote = False
            heading = clean_text(line[4:].strip())
            output.append(f'\\subsection{{{heading}}}')
            i += 1
            continue
        
        # Handle blockquotes
        if line.startswith('> '):
            close_lists(output, list_stack)
            if not in_blockquote:
                output.append('\\begin{quote}')
                in_blockquote = True
            content = clean_text(line[2:].strip())
            output.append(content)
            i += 1
            continue
        elif in_blockquote and line.strip() == '':
            output.append('\\end{quote}')
            in_blockquote = False
            i += 1
            continue
        elif in_blockquote and not line.startswith('>'):
            output.append('\\end{quote}')
            in_blockquote = False
        
        # Handle display math blocks
        if line.strip().startswith('$$'):
            close_lists(output, list_stack)
            if line.strip().endswith('$$') and len(line.strip()) > 4:
                math_content = line.strip()[2:-2].strip()
                math_content = fix_math_block(math_content)
                output.append(math_content)
                i += 1
                continue
            else:
                math_lines = []
                rest = line.strip()[2:]
                if rest:
                    math_lines.append(rest)
                i += 1
                while i < len(lines) and not lines[i].strip().endswith('$$'):
                    math_lines.append(lines[i])
                    i += 1
                if i < len(lines):
                    last = lines[i].strip()
                    if last != '$$':
                        math_lines.append(last[:-2])
                    i += 1
                math_content = '\n'.join(math_lines).strip()
                math_content = fix_math_block(math_content)
                output.append(math_content)
                continue
        
        # Handle bullet lists
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            if not list_stack or list_stack[-1] != 'itemize':
                close_lists(output, list_stack)
                output.append('\\begin{itemize}')
                list_stack.append('itemize')
            marker_len = 2
            item_text = clean_text(line.strip()[marker_len:])
            output.append(f'  \\item {item_text}')
            i += 1
            continue
        
        # Handle numbered lists
        numbered_match = re.match(r'^(\d+)\.\s(.+)$', line.strip())
        if numbered_match:
            if not list_stack or list_stack[-1] != 'enumerate':
                close_lists(output, list_stack)
                output.append('\\begin{enumerate}')
                list_stack.append('enumerate')
            item_text = clean_text(numbered_match.group(2))
            output.append(f'  \\item {item_text}')
            i += 1
            continue
        
        # Handle empty lines
        if line.strip() == '':
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                j += 1
            if j < len(lines):
                next_line = lines[j].strip()
                if list_stack and (next_line.startswith('- ') or next_line.startswith('* ') or re.match(r'^\d+\.\s', next_line)):
                    output.append('')
                    i += 1
                    continue
            close_lists(output, list_stack)
            output.append('')
            i += 1
            continue
        
        # Regular text
        text = clean_text(line)
        output.append(text)
        i += 1
    
    if in_blockquote:
        output.append('\\end{quote}')
    close_lists(output, list_stack)
    
    return '\n'.join(output)


def close_lists(output, list_stack):
    """Close all open list environments."""
    while list_stack:
        env = list_stack.pop()
        output.append(f'\\end{{{env}}}')


def fix_math_block(content):
    """Fix math blocks - convert alignment environments properly."""
    if '&' in content or ('\\\\' in content and 'begin{' not in content):
        return f'\\begin{{align*}}\n{content}\n\\end{{align*}}'
    else:
        return f'\\[{content}\\]'


def clean_text(text):
    """Clean and convert inline markdown to LaTeX."""
    # Protect math blocks first
    math_blocks = []
    def save_math(m):
        math_blocks.append(m.group(0))
        return f'MATHPLACEHOLDER{len(math_blocks)-1}END'
    
    text = re.sub(r'\$\$.*?\$\$', save_math, text)
    text = re.sub(r'\$[^$]+?\$', save_math, text)
    
    # Handle bold+italic ***text***
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'\\textbf{\\textit{\1}}', text)
    # Handle bold **text**
    text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
    # Handle italic *text*
    text = re.sub(r'(?<![\\*])\*([^*]+?)\*(?!\*)', r'\\textit{\1}', text)
    
    # Handle inline code `text`
    text = re.sub(r'`([^`]+)`', r'\\texttt{\1}', text)
    
    # Escape special characters (outside math)
    text = text.replace('&', '\\&')
    text = text.replace('#', '\\#')
    text = text.replace('%', '\\%')
    text = text.replace('_', '\\_')
    
    # Handle Unicode characters
    unicode_map = {
        '\u2713': '$\\checkmark$',
        '\u2717': '$\\times$',
        '\u274c': '$\\times$',
        '\u2192': '$\\rightarrow$',
        '\u2190': '$\\leftarrow$',
        '\u2194': '$\\leftrightarrow$',
        '\u21d2': '$\\Rightarrow$',
        '\u2264': '$\\leq$',
        '\u2265': '$\\geq$',
        '\u2260': '$\\neq$',
        '\u221e': '$\\infty$',
        '\u00d7': '$\\times$',
        '\u00b7': '$\\cdot$',
        '\u2026': '\\ldots{}',
        '\u2014': '---',
        '\u2013': '--',
        '\u201c': '``',
        '\u201d': "''",
        '\u2018': '`',
        '\u2019': "'",
        '\u00e9': "\\'e",
        '\u00f6': '\\"o',
        '\u00fc': '\\"u',
        '\u00e4': '\\"a',
        '\u2124': '$\\mathbb{Z}$',
        '\u211d': '$\\mathbb{R}$',
        '\u211a': '$\\mathbb{Q}$',
        '\u2115': '$\\mathbb{N}$',
        '\u2102': '$\\mathbb{C}$',
        '\u03c0': '$\\pi$',
        '\u221a': '$\\sqrt{}$',
        '\u00b1': '$\\pm$',
        '\u2208': '$\\in$',
        '\u2282': '$\\subset$',
        '\u2286': '$\\subseteq$',
        '\u2229': '$\\cap$',
        '\u222a': '$\\cup$',
        '\u2200': '$\\forall$',
        '\u2203': '$\\exists$',
        '\u03b1': '$\\alpha$',
        '\u03b2': '$\\beta$',
        '\u03b3': '$\\gamma$',
        '\u03b4': '$\\delta$',
        '\u03b5': '$\\varepsilon$',
        '\u03b8': '$\\theta$',
        '\u03bb': '$\\lambda$',
        '\u03bc': '$\\mu$',
        '\u03c3': '$\\sigma$',
        '\u03c6': '$\\varphi$',
        '\u03c8': '$\\psi$',
        '\u03c9': '$\\omega$',
        '\u03a3': '$\\Sigma$',
        '\u03a0': '$\\Pi$',
        '\u0394': '$\\Delta$',
        '\u03a9': '$\\Omega$',
        '\u2295': '$\\oplus$',
        '\u2297': '$\\otimes$',
        '\u2248': '$\\approx$',
        '\u223c': '$\\sim$',
        '\u2261': '$\\equiv$',
        '\u221d': '$\\propto$',
        '\u2605': '$\\bigstar$',
        '\u220e': '$\\blacksquare$',
        '\u25a1': '$\\square$',
        '\u2223': '$\\mid$',
        '\u2022': '$\\bullet$',
    }
    
    for char, replacement in unicode_map.items():
        text = text.replace(char, replacement)
    
    # Restore math blocks
    for idx, block in enumerate(math_blocks):
        text = text.replace(f'MATHPLACEHOLDER{idx}END', block)
    
    return text


def get_chapter_images(chapter_dir):
    """Get list of image files for a chapter."""
    img_dir = os.path.join(chapter_dir, 'images')
    if not os.path.exists(img_dir):
        return []
    images = sorted([f for f in os.listdir(img_dir) if f.endswith('.png') and 'Zone' not in f and 'Copy' not in f])
    return images


def get_image_caption(filename):
    """Generate a caption from the image filename."""
    name = re.sub(r'^fig\d+_', '', filename)
    name = name.replace('.png', '')
    name = name.replace('_', ' ').title()
    return name


if __name__ == '__main__':
    with open('/workspace/request-project/Chapter1/Chapter1.md', 'r') as f:
        md = f.read()
    latex = md_to_latex(md, chapter_num=1)
    print(latex[:2000])
