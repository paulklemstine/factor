#!/usr/bin/env python3
"""Process pandoc-generated LaTeX files for the book."""
import re
import os
import subprocess

BOOK_DIR = "/workspace/request-project/book"

def get_images(chapter_dir):
    img_dir = os.path.join(chapter_dir, "images")
    if not os.path.isdir(img_dir):
        return []
    files = sorted([f for f in os.listdir(img_dir) if f.endswith('.png') and 'Zone' not in f])
    return [os.path.join(img_dir, f) for f in files]

INDEX_TERMS = [
    ("Pythagorean triples", "Pythagorean triple"),
    ("Pythagorean triple", "Pythagorean triple"),
    ("Berggren tree", "Berggren tree"),
    ("Lorentz group", "Lorentz group"),
    ("Lorentz form", "Lorentz form"),
    ("null cone", "null cone"),
    ("quadratic form", "quadratic form"),
    ("Pell equation", "Pell equation"),
    ("semiprime", "semiprime"),
    ("quaternion", "quaternions"),
    ("octonion", "octonions"),
    ("Fermat's Last Theorem", "Fermat's Last Theorem"),
    ("congruence of squares", "congruence of squares"),
    ("quadratic sieve", "quadratic sieve"),
    ("number field sieve", "number field sieve"),
    ("Plimpton 322", "Plimpton 322"),
    ("lattice reduction", "lattice reduction"),
    ("LLL algorithm", "LLL algorithm"),
    ("infinite descent", "infinite descent"),
    ("special relativity", "special relativity"),
    ("factor base", "factor base"),
    ("Gaussian integers", "Gaussian integers"),
    ("elliptic curve", "elliptic curves"),
]

def add_index_entries(content):
    """Add \\index entries before first body-text occurrence of each term."""
    indexed = set()
    for pattern, index_term in INDEX_TERMS:
        if index_term in indexed:
            continue
        for match in re.finditer(r'(?<![\\{])' + re.escape(pattern), content):
            pos = match.start()
            line_start = content.rfind('\n', 0, pos) + 1
            line = content[line_start:content.find('\n', pos)]
            stripped = line.lstrip()
            if any(stripped.startswith(cmd) for cmd in ['\\section', '\\subsection', '\\label', '\\caption']):
                continue
            # Don't insert inside another \index{}
            before_chunk = content[max(0,pos-50):pos]
            if '\\index{' in before_chunk and '}' not in before_chunk[before_chunk.rfind('\\index{'):]:
                continue
            content = content[:pos] + '\\index{' + index_term + '}' + content[pos:]
            indexed.add(index_term)
            break
    return content

def fix_chapter_tex(tex_file, chapter_dir, is_intro=False, is_conclusion=False):
    with open(tex_file, 'r') as f:
        content = f.read()
    
    images = get_images(chapter_dir)
    img_idx = [0]
    
    if is_intro:
        content = re.sub(r'\\section\{Introduction:.*?\}\\label\{[^}]*\}\n*', '', content, count=1)
    elif is_conclusion:
        content = re.sub(r'\\section\{Conclusion.*?\}\\label\{[^}]*\}\n*', '', content, count=1)
    else:
        content = re.sub(
            r'\\section\{\\texorpdfstring\{Chapter \d+.*?\}\{[^}]*\}\}\\label\{[^}]*\}\n*',
            '', content, count=1)
        content = re.sub(
            r'\\section\{Chapter \d+.*?\}\\label\{[^}]*\}\n*',
            '', content, count=1)
    
    content = content.replace(r'\begin{center}\rule{0.5\linewidth}{0.5pt}\end{center}', '')
    
    # Remove subtitle sections
    content = re.sub(r'\\section\{\\texorpdfstring\{\\emph\{.*?\}\}\{.*?\}\}\\label\{[^}]*\}\n*', '', content)
    
    content = content.replace(r'\subsubsection', r'\subsection')
    content = content.replace(r'\subsection', r'\section')
    
    def replace_illustration(match):
        caption_text = match.group(1).strip()
        caption_text = caption_text.replace('{[}', '[').replace('{]}', ']')
        if img_idx[0] < len(images):
            img_path = images[img_idx[0]]
            img_idx[0] += 1
            rel_path = os.path.relpath(img_path, BOOK_DIR)
            return (f'\n\\begin{{figure}}[htbp]\n'
                    f'\\centering\n'
                    f'\\includegraphics[width=0.82\\textwidth]{{{rel_path}}}\n'
                    f'\\end{{figure}}\n')
        else:
            return ''
    
    # Match {[}ILLUSTRATION: ...{]} — the {]} is the end marker
    content = re.sub(
        r'\{\[\}ILLUSTRATION:\s*(.*?)\{\]\}',
        replace_illustration, content, flags=re.DOTALL)
    # Also match any leftover [ILLUSTRATION: ...] patterns
    content = re.sub(
        r'\[ILLUSTRATION:\s*(.*?)\]',
        replace_illustration, content, flags=re.DOTALL)
    
    content = content.replace(r'\tightlist', '')
    content = add_index_entries(content)
    
    # Make labels unique
    prefix = os.path.basename(tex_file).replace('.tex','').replace('chapter','ch').replace('introduction','intro').replace('conclusion','concl')
    content = re.sub(r'\\label\{([^}]+)\}', lambda m: '\\label{' + prefix + '-' + m.group(1) + '}', content)
    
    with open(tex_file, 'w') as f:
        f.write(content)

# Re-convert from markdown
subprocess.run(['pandoc', 'Introduction/Introduction.md', '-f', 'markdown', '-t', 'latex',
                '--wrap=none', '-o', 'book/introduction.tex'], cwd='/workspace/request-project')
for i in range(1, 17):
    subprocess.run(['pandoc', f'Chapter{i}/Chapter{i}.md', '-f', 'markdown', '-t', 'latex',
                    '--wrap=none', '-o', f'book/chapter{i}.tex'], cwd='/workspace/request-project')
subprocess.run(['pandoc', 'Conclusion/Conclusion.md', '-f', 'markdown', '-t', 'latex',
                '--wrap=none', '-o', 'book/conclusion.tex'], cwd='/workspace/request-project')

print("Processing introduction...")
fix_chapter_tex(os.path.join(BOOK_DIR, 'introduction.tex'),
                '/workspace/request-project/Introduction', is_intro=True)

for i in range(1, 17):
    print(f"Processing chapter {i}...")
    fix_chapter_tex(os.path.join(BOOK_DIR, f'chapter{i}.tex'),
                    f'/workspace/request-project/Chapter{i}')

print("Processing conclusion...")
fix_chapter_tex(os.path.join(BOOK_DIR, 'conclusion.tex'),
                '/workspace/request-project/Conclusion', is_conclusion=True)

print("All chapters processed.")
