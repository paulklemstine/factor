#!/usr/bin/env python3
"""Master build script: convert, index, fix unicode, postfix."""
import subprocess, sys

steps = [
    ['python3', 'book/convert_md_to_latex.py'],
    ['python3', 'book/add_index_entries.py'],
    ['python3', 'book/fix_latex_files.py'],
    ['python3', 'book/postfix.py'],
]

for cmd in steps:
    print(f"\n=== Running: {' '.join(cmd)} ===")
    r = subprocess.run(cmd, cwd='/workspace/request-project', 
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FAILED: {r.stderr}")
        sys.exit(1)
    # Only print last few lines
    lines = r.stdout.strip().split('\n')
    for l in lines[-3:]:
        print(l)

print("\n=== All build steps complete ===")
