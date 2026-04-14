#!/usr/bin/env python3
"""Fix the appendix_lean.tex to properly escape underscores."""
import re

with open('/workspace/request-project/book/appendix_lean.tex') as f:
    content = f.read()

# Replace underscores in \texttt{...} blocks (display names)
def fix_texttt(m):
    inner = m.group(1)
    inner = inner.replace('_', '\\_')
    return '\\texttt{' + inner + '}'

content = re.sub(r'\\texttt\{([^}]+)\}', fix_texttt, content)

# But DON'T escape underscores inside \VerbatimInput paths
# Those should have real underscores
def fix_verbatim_path(m):
    path = m.group(1)
    path = path.replace('\\_', '_')  # Undo any escaping in paths
    return '\\VerbatimInput[frame=single,numbers=left,numbersep=3pt,fontsize=\\scriptsize]{' + path + '}'

content = re.sub(
    r'\\VerbatimInput\[frame=single,numbers=left,numbersep=3pt,fontsize=\\scriptsize\]\{([^}]+)\}',
    fix_verbatim_path, content
)

# Remove \begin{small} / \end{small} around VerbatimInput
content = content.replace('\\begin{small}\n', '')
content = content.replace('\\end{small}\n', '')

with open('/workspace/request-project/book/appendix_lean.tex', 'w') as f:
    f.write(content)

print("Fixed appendix")
