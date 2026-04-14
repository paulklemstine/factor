#!/usr/bin/env python3
"""Post-process generated TeX files to fix common issues."""
import re
import glob
import os

def fix_file(filepath):
    with open(filepath) as f:
        content = f.read()
    
    original = content
    
    # 1. Fix \mathbf outside math mode
    content = re.sub(r'(?<!\$)\\mathbf\{([^}]+)\}(?!\$)', r'$\\mathbf{\1}$', content)
    content = re.sub(r'(?<!\$)\\mathbb\{([^}]+)\}(?!\$)', r'$\\mathbb{\1}$', content)
    
    # 2. Fix display math with blank lines inside
    def fix_display_math(m):
        inner = m.group(1)
        inner = re.sub(r'\n\s*\n', '\n', inner)
        return '\\[\n' + inner.strip() + '\n\\]'
    
    content = re.sub(r'\\\[\s*\n(.*?)\n\s*\\\]', fix_display_math, content, flags=re.DOTALL)
    
    # 3. Fix \operatorname outside math mode
    content = re.sub(r'(?<!\$)\\operatorname\{([^}]+)\}(?!\$)', r'$\\operatorname{\1}$', content)
    
    # 4. Fix \times outside math mode (but not inside $...$)
    # Simple approach: just replace isolated \times
    content = re.sub(r'(?<!\$)\\times(?![a-zA-Z])(?!\$)', r'$\\times$', content)
    
    # 5. Fix \cdot outside math mode
    content = re.sub(r'(?<!\$)\\cdot(?![a-zA-Z])(?!\$)', r'$\\cdot$', content)
    
    # 6. Remove stray $$ (empty display math)
    content = content.replace('$$', '')
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

count = 0
for f in sorted(glob.glob('/workspace/request-project/book/*.tex')):
    if 'main.tex' in f or 'appendix' in f:
        continue
    if fix_file(f):
        count += 1
        print(f"  Fixed: {os.path.basename(f)}")

print(f"\nFiles fixed: {count}")
