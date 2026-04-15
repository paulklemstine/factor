#!/usr/bin/env python3
"""Fix the generated book.tex for XeLaTeX compilation."""
import re

with open('/workspace/request-project/book.tex', 'r') as f:
    text = f.read()

# Switch to XeLaTeX
text = text.replace(r'\usepackage[T1]{fontenc}', '')
text = text.replace(r'\usepackage[utf8]{inputenc}', '')
text = text.replace(r'\usepackage{lmodern}', r'\usepackage{fontspec}')

# Replace ∎
text = text.replace('\u220e', r'\(\square\)')

# Remove emoji
text = re.sub(r'[\U0001F300-\U0001F9FF]', '', text)
text = re.sub(r'[\U00002600-\U000027BF]', '', text)
text = re.sub(r'[\U0000FE00-\U0000FE0F]', '', text)
text = re.sub(r'[\U0000200D]', '', text)
text = text.replace('\u274C', 'No')  # ❌
text = text.replace('\u2705', 'Yes')  # ✅
text = text.replace('\u2713', r'\checkmark{}')  # ✓

# Add extendedchars to listings
text = text.replace(
    'literate={',
    'extendedchars=true,\n  literate={'
)

# Fix captions: escape & that aren't already escaped
lines = text.split('\n')
result = []
i = 0
while i < len(lines):
    line = lines[i]
    if r'\caption{' in line:
        # Collect full caption (tracking braces)
        caption_buf = [line]
        depth = 0
        for ch in line:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
        while depth > 0 and i + 1 < len(lines):
            i += 1
            caption_buf.append(lines[i])
            for ch in lines[i]:
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
        
        full_caption = '\n'.join(caption_buf)
        
        # Escape unescaped & in caption (not in math mode)
        # Process character by character
        out = []
        in_math = False
        j = 0
        while j < len(full_caption):
            ch = full_caption[j]
            if ch == '$':
                in_math = not in_math
                out.append(ch)
            elif ch == '&' and not in_math:
                if j > 0 and full_caption[j-1] == '\\':
                    out.append(ch)
                else:
                    out.append('\\&')
            else:
                out.append(ch)
            j += 1
        
        result.append(''.join(out))
    else:
        result.append(line)
    i += 1

text = '\n'.join(result)

# Fix specific broken patterns from markdown conversion
# The markdown converter sometimes loses ] when it appears after [
# in contexts like $\mathbb{Z}[i]$
# These show up as $\mathbb{Z}[i} in the tex (missing ])
text = text.replace(r'\mathbb{Z}[i}', r'\mathbb{Z}[i]')
text = text.replace(r'\mathbb{Z}[\omega}', r'\mathbb{Z}[\omega]')
text = text.replace(r'\mathbb{Z}[\sqrt{-5}}', r'\mathbb{Z}[\sqrt{-5}]')
# Also fix pattern where the dollar sign might be involved
text = re.sub(r'\\mathbb\{Z\}\[([^\]]*?)\}(?!\])', r'\\mathbb{Z}[\1]', text)

# Fix continued fraction patterns
text = re.sub(
    r'\[1;\s*1,\s*1,\s*1,\s*1,\s*1,\s*\\ldots\}',
    r'[1; 1, 1, 1, 1, 1, \\ldots]',
    text
)

# Verify brace balance
opens = text.count('{')
closes = text.count('}')
print(f'Braces: {opens} open, {closes} close, diff={opens-closes}')

if opens != closes:
    # Find where imbalance occurs
    depth = 0
    last_positive_line = 0
    for idx, ch in enumerate(text):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
    
    if depth > 0:
        # Find last caption or figure with unclosed brace
        print(f'Warning: {depth} unclosed braces')

with open('/workspace/request-project/book.tex', 'w') as f:
    f.write(text)
print('Done with fixes')
