#!/bin/bash
cd /workspace/request-project

cat > book/appendix_lean_files.tex << 'EOF'
% Auto-generated appendix of Lean source files
EOF

declare -a titles=(
  "The Berggren--Lorentz Correspondence"
  "Lattice--Tree Correspondence"
  "Hyperbolic Shortcuts for Factoring"
  "Three Roads from Pythagoras"
  "Berggren--Lorentz Paper Proofs"
  "Higher \$k\$-Tuple Factoring"
  "Quantum Grover Tree Factoring"
  "Complexity Bounds, Proven"
  "Cayley--Dickson Hierarchy"
  "Fermat's Last Theorem"
  "Congruence of Squares Factoring"
  "Quadruple Factor Theory"
  "GCD Cascade Factor Extraction"
  "Pythagorean Tree Factoring Core"
  "Tropical Geometry Foundations"
  "Lorentz Group Structure"
)

declare -a files=(
  01_BerggrenLorentzCorrespondence.lean
  02_LatticeTreeCorrespondence.lean
  03_HyperbolicShortcutsFactoring.lean
  04_ThreeRoadsFromPythagoras.lean
  05_BerggrenLorentzPaperProofs.lean
  06_HigherKTupleFactoring.lean
  07_QuantumGroverTreeFactoring.lean
  08_ComplexityBoundsProven.lean
  09_CayleyDicksonHierarchy.lean
  10_FermatLastTheorem.lean
  11_CongruenceOfSquaresFactoring.lean
  12_QuadrupleFactorTheory.lean
  13_GCDCascadeFactorExtraction.lean
  14_PythagoreanTreeFactoringCore.lean
  15_TropicalGeometryFoundations.lean
  16_LorentzGroupStructure.lean
)

for i in "${!files[@]}"; do
  f="${files[$i]}"
  t="${titles[$i]}"
  label=$(echo "$f" | sed 's/.lean//')
  {
    echo ""
    echo "\\section{$t}"
    echo "\\label{app:$label}"
    echo "\\texttt{$f}"
    echo ""
    echo "\\lstinputlisting[language=Lean]{../$f}"
    echo ""
  } >> book/appendix_lean_files.tex
done

echo "Done generating appendix"
