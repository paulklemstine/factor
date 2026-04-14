#!/usr/bin/env python3
import re, glob, os

def fix_file(path):
    with open(path) as f:
        c = f.read()
    
    orig = c
    
    # Fix: remove \index{} entries that appear inside \[...\] display math
    def fix_dm(m):
        inner = m.group(1)
        inner = re.sub(r'\\index\{[^}]*\}', '', inner)
        return '\\[' + inner + '\\]'
    
    c = re.sub(r'\\\[(.*?)\\\]', fix_dm, c, flags=re.DOTALL)
    
    # Fix em/en dashes outside math
    parts = re.split(r'(\$[^$]+\$|\\\[.*?\\\])', c, flags=re.DOTALL)
    result = []
    for i, p in enumerate(parts):
        if i % 2 == 0:  # non-math
            p = p.replace('\u2014', '---')
            p = p.replace('\u2013', '--')
            p = p.replace('\u2018', '`')
            p = p.replace('\u2019', "'")
            p = p.replace('\u201c', '``')
            p = p.replace('\u201d', "''")
        result.append(p)
    c = ''.join(result)
    
    if c != orig:
        with open(path, 'w') as f:
            f.write(c)
        return True
    return False

for f in sorted(glob.glob('/workspace/request-project/book/ch_*.tex')):
    changed = fix_file(f)
    if changed:
        print(f"Fixed {os.path.basename(f)}")

print("Done.")
