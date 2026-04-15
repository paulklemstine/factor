#!/usr/bin/env python3
"""Generate the Lean appendix LaTeX file using fancyvrb for efficiency."""

import os

lean_dir = '/workspace/request-project/book/lean_clean'
out_file = '/workspace/request-project/book/appendix_lean.tex'

lean_files = [
    ('01_BerggrenLorentzCorrespondence.lean', 'Berggren--Lorentz Correspondence (Chapter~1)'),
    ('02_LatticeTreeCorrespondence.lean', 'Lattice--Tree Correspondence (Chapter~2)'),
    ('03_HyperbolicShortcutsFactoring.lean', 'Hyperbolic Shortcuts and Factoring (Chapter~3)'),
    ('04_ThreeRoadsFromPythagoras.lean', 'Three Roads from Pythagoras (Chapter~4)'),
    ('05_BerggrenLorentzPaperProofs.lean', 'Berggren--Lorentz Paper Proofs (Chapter~5)'),
    ('06_HigherKTupleFactoring.lean', 'Higher $k$-Tuple Factoring (Chapter~6)'),
    ('07_QuantumGroverTreeFactoring.lean', 'Quantum Grover Tree Factoring (Chapter~7)'),
    ('08_ComplexityBoundsProven.lean', 'Complexity Bounds (Chapter~8)'),
    ('09_CayleyDicksonHierarchy.lean', 'Cayley--Dickson Hierarchy (Chapter~9)'),
    ('10_FermatLastTheorem.lean', "Fermat's Last Theorem (Chapter~10)"),
    ('11_CongruenceOfSquaresFactoring.lean', 'Congruence of Squares Factoring (Chapter~11)'),
    ('12_QuadrupleFactorTheory.lean', 'Quadruple Factor Theory (Chapter~12)'),
    ('13_GCDCascadeFactorExtraction.lean', 'GCD Cascade Factor Extraction (Chapter~13)'),
    ('14_PythagoreanTreeFactoringCore.lean', 'Pythagorean Tree Factoring Core (Chapter~14)'),
    ('15_TropicalGeometryFoundations.lean', 'Tropical Geometry Foundations (Chapter~15)'),
    ('16_LorentzGroupStructure.lean', 'Lorentz Group Structure (Chapter~16)'),
]

with open(out_file, 'w') as f:
    for filename, description in lean_files:
        filepath = os.path.join(lean_dir, filename)
        if not os.path.exists(filepath):
            continue
        
        safe_name = filename.replace('_', '\\_')
        
        f.write(f'\\section*{{{description}}}\n')
        f.write(f'\\addcontentsline{{toc}}{{section}}{{{description}}}\n')
        f.write(f'\\label{{lean:{filename.replace(".lean", "")}}}\n\n')
        f.write(f'{{\\small\\texttt{{{safe_name}}}}}\n\n')
        f.write('\\begin{small}\n')
        f.write(f'\\VerbatimInput[frame=leftline,framerule=0.4pt,framesep=1em,numbers=left,numbersep=6pt,fontsize=\\footnotesize]{{lean_clean/{filename}}}\n')
        f.write('\\end{small}\n\n')
        f.write('\\newpage\n\n')

print(f'Wrote {out_file}')
