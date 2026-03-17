# Factoring Project Instructions

## After Major Discoveries
When significant new theorems, proofs, or algorithms are discovered:

1. **Update the website** (`/update-docs` or manually):
   - Add theorem cards to `website/pages/theorems.html` (KaTeX math, badge-proven/badge-high)
   - Create deep-dive pages in `website/pages/theorems/` for top results
   - Generate publication-quality visualizations (dpi=200, dark background)
   - Update `website/index.html` hero stats

2. **Write a research paper** if it's a remarkable proof:
   - Use `\documentclass[12pt]{amsart}`
   - Author: Paul Klemstine, Independent Researcher, Menasha, WI
   - Include AI disclosure in Acknowledgments per Elsevier/Nature standards
   - Include Computational Methods section (Python 3.11, WSL2, RTX 4050, gmpy2/mpmath/numpy)
   - Compile with `pdflatex` twice, save to `website/paper/`

3. **Commit, push, deploy**:
   ```bash
   git add website/ images/ *.py *.md
   git commit -m "Description of changes"
   git push
   cd website && firebase deploy --only hosting
   ```

## Key Constraints
- **RAM limit**: Keep under 6GB total (WSL2 with ~12GB RAM, 5GB practical)
- **Sudo password**: jerusalem
- **Website**: Firebase at https://paulklemstine.web.app
- **Papers**: All in `website/paper/`, amsart class, Paul Klemstine author
- **No AI co-authors** — disclose in Acknowledgments only
