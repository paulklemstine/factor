#!/usr/bin/env python3
import re

with open('/workspace/request-project/book/ch_conclusion.tex') as f:
    c = f.read()

# Fix: remove \index{} entries that appear inside \[...\] display math
def fix_dm(m):
    inner = m.group(1)
    inner = re.sub(r'\\index\{[^}]*\}', '', inner)
    inner = inner.replace('\u2014', '{-}')  # em dash
    return '\\[' + inner + '\\]'

c = re.sub(r'\\\[(.*?)\\\]', fix_dm, c, flags=re.DOTALL)
c = c.replace('\u2014', '---')
c = c.replace('\u2013', '--')

with open('/workspace/request-project/book/ch_conclusion.tex', 'w') as f:
    f.write(c)
print('Fixed conclusion')
