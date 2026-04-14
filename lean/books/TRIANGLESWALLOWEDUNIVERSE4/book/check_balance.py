#!/usr/bin/env python3
import glob, os

for f in sorted(glob.glob('/workspace/request-project/book/*.tex')):
    with open(f) as fp:
        content = fp.read()
    
    depth = 0
    dollars = 0
    for c in content:
        if c == '{': depth += 1
        elif c == '}': depth -= 1
        elif c == '$': dollars += 1
    
    name = os.path.basename(f)
    if depth != 0 or dollars % 2 != 0:
        print(f"UNBALANCED: {name}: brace_depth={depth}, odd_dollars={dollars%2}")
