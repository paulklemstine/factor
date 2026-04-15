#!/usr/bin/env python3
"""Post-process LaTeX files to fix common conversion issues."""
import os, re, glob

def fix_captions(content):
    """Fix broken captions by ensuring math mode is balanced."""
    def fix_caption_match(m):
        cap = m.group(1)
        # Count $ signs - if odd, we have unbalanced math mode
        dollar_count = cap.count('$') - cap.count('\\$')
        if dollar_count % 2 != 0:
            # Truncate to last balanced position
            depth = 0
            last_safe = 0
            for i, ch in enumerate(cap):
                if ch == '$' and (i == 0 or cap[i-1] != '\\'):
                    depth = 1 - depth
                if depth == 0 and ch in (' ', ',', '.'):
                    last_safe = i
            if last_safe > 10:
                cap = cap[:last_safe]
        # Also fix unbalanced braces
        brace_depth = 0
        last_safe = len(cap)
        for i, ch in enumerate(cap):
            if ch == '{':
                brace_depth += 1
            elif ch == '}':
                brace_depth -= 1
            if brace_depth < 0:
                last_safe = i
                break
        cap = cap[:last_safe]
        # Close any open braces
        brace_depth = 0
        for ch in cap:
            if ch == '{':
                brace_depth += 1
            elif ch == '}':
                brace_depth -= 1
        while brace_depth > 0:
            cap += '}'
            brace_depth -= 1
        return '\\caption{' + cap + '}'
    
    content = re.sub(r'\\caption\{((?:[^{}]|\{[^{}]*\})*)\}', fix_caption_match, content)
    return content

def fix_bare_subscripts(content):
    """Fix bare subscripts/superscripts outside math mode."""
    lines = content.split('\n')
    fixed = []
    for line in lines:
        # Skip lines that are LaTeX commands or in environments
        stripped = line.strip()
        if stripped.startswith('\\') or stripped.startswith('%'):
            fixed.append(line)
            continue
        
        # Check for bare _ or ^ outside math mode
        parts = line.split('$')
        new_parts = []
        for idx, part in enumerate(parts):
            if idx % 2 == 0:  # text mode
                # Fix bare T_ patterns (from \text{T_...})
                part = re.sub(r'(?<![\\])_', '\\_', part)
            new_parts.append(part)
        fixed.append('$'.join(new_parts))
    return '\n'.join(fixed)

def fix_misc(content):
    """Fix miscellaneous issues."""
    # Fix \ensuremath nested inside math
    # $...\ensuremath{X}...$ -> $...X...$
    # This is hard to do perfectly, but \ensuremath is safe inside math mode
    
    # Fix empty display math (\[ \] with nothing between)
    content = re.sub(r'\\\[\s*\\\]', '', content)
    
    # Fix \time -> \times (common truncation issue)
    content = re.sub(r'\\time(?!s)', r'\times', content)
    
    # Fix na"ive
    content = content.replace('na\\"ive', 'na\\"{\\i}ve')
    content = content.replace('na\\"\\i ve', 'na\\"{\\i}ve')
    
    return content

book_dir = '/workspace/request-project/book'
for texfile in sorted(glob.glob(os.path.join(book_dir, '*.tex'))):
    basename = os.path.basename(texfile)
    if basename in ('main.tex', 'appendix_lean.tex', 'test_chapter.tex'):
        continue
    
    with open(texfile, 'r') as f:
        content = f.read()
    
    content = fix_captions(content)
    content = fix_misc(content)
    # Don't run fix_bare_subscripts as it might break things in math
    
    with open(texfile, 'w') as f:
        f.write(content)
    
    print(f'Post-fixed {basename}')

print('Done.')
