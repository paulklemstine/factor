#!/usr/bin/env python3
"""Fix common issues in generated .tex files."""
import os, re, glob

def fix_tex(content):
    # Fix \& inside display math (\[...\])
    # We need to find display math blocks and un-escape & inside them
    def fix_display_math(m):
        math = m.group(1)
        math = math.replace(r'\&', '&')
        math = math.replace(r'\#', '#')
        math = math.replace(r'\%', '%')
        return r'\[' + math + r'\]'
    
    content = re.sub(r'\\\[(.*?)\\\]', fix_display_math, content, flags=re.DOTALL)
    
    # Fix \& inside inline math $...$
    def fix_inline_math(m):
        math = m.group(0)
        math = math.replace(r'\&', '&')
        math = math.replace(r'\#', '#')
        math = math.replace(r'\%', '%')
        return math
    
    content = re.sub(r'\$[^$]+\$', fix_inline_math, content)
    
    # Fix escaped underscores in normal text that should be real underscores
    # (actually, underscores need escaping in LaTeX text mode)
    # But raw _ in text mode is a problem - let's escape them
    # Split by math and non-math
    parts = re.split(r'(\$[^$]+\$|\\\[.*?\\\])', content, flags=re.DOTALL)
    fixed_parts = []
    for i, part in enumerate(parts):
        if i % 2 == 0:  # Non-math
            # Escape bare underscores (not already escaped)
            part = re.sub(r'(?<!\\)_', r'\\_', part)
            # But don't double-escape
            part = part.replace(r'\\_', r'\_')
        fixed_parts.append(part)
    content = ''.join(fixed_parts)
    
    # Fix the begin{array} blocks that have & alignment
    # These are inside \[...\] and should have raw &
    # Already handled above
    
    # Fix \operatorname inside display math (should be ok with amsmath)
    
    # Remove duplicate \index entries on same line
    
    return content


book_dir = '/workspace/request-project/book'
for f in sorted(glob.glob(os.path.join(book_dir, 'ch_*.tex'))):
    with open(f, 'r') as fh:
        content = fh.read()
    fixed = fix_tex(content)
    with open(f, 'w') as fh:
        fh.write(fixed)
    print(f"Fixed {os.path.basename(f)}")

print("Done.")
