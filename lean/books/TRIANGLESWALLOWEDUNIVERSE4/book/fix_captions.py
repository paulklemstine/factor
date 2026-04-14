#!/usr/bin/env python3
"""Fix LaTeX captions to ensure balanced braces and math delimiters."""
import glob
import os

def balance_caption(text, max_len=180):
    """Truncate caption safely, ensuring balanced braces and $ delimiters."""
    if len(text) <= max_len:
        # Just check balance
        pass
    else:
        # Find safe truncation point
        depth = 0
        dollar_count = 0
        last_safe = 0
        
        for i, c in enumerate(text):
            if i > max_len:
                break
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
            elif c == '$':
                dollar_count += 1
            
            # A safe point: balanced braces and even dollars
            if depth == 0 and dollar_count % 2 == 0 and i > 50:
                last_safe = i + 1
        
        if last_safe > 50:
            text = text[:last_safe]
        else:
            text = text[:max_len]
    
    # Final balance check
    depth = 0
    dollar_count = 0
    for c in text:
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
        elif c == '$':
            dollar_count += 1
    
    # Close open braces
    while depth > 0:
        text += '}'
        depth -= 1
    
    # Close open math
    if dollar_count % 2 == 1:
        text += '$'
    
    # If negative depth, remove trailing }
    while depth < 0:
        idx = text.rfind('}')
        if idx >= 0:
            text = text[:idx] + text[idx+1:]
        depth += 1
    
    return text


def process_file(filepath):
    with open(filepath) as f:
        content = f.read()
    
    result = []
    i = 0
    changes = 0
    
    while i < len(content):
        # Look for \caption{
        if content[i:i+9] == '\\caption{':
            start = i + 9
            depth = 1
            j = start
            while j < len(content) and depth > 0:
                if content[j] == '{':
                    depth += 1
                elif content[j] == '}':
                    depth -= 1
                j += 1
            
            cap_text = content[start:j-1]
            fixed = balance_caption(cap_text)
            
            if fixed != cap_text:
                changes += 1
            
            result.append('\\caption{' + fixed + '}')
            i = j
        else:
            result.append(content[i])
            i += 1
    
    new_content = ''.join(result)
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    return changes


total = 0
for f in sorted(glob.glob('/workspace/request-project/book/*.tex')):
    if 'main.tex' in f or 'appendix' in f:
        continue
    changes = process_file(f)
    if changes:
        print(f"  Fixed {changes} caption(s) in {os.path.basename(f)}")
        total += changes

print(f"\nTotal captions fixed: {total}")
