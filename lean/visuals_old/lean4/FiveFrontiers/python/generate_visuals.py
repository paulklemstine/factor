#!/usr/bin/env python3
"""
Visual Generator: ASCII and SVG Visualizations for All Five Research Problems
==============================================================================

Generates publication-quality visual diagrams as SVG files for each research
problem, plus ASCII art summaries for the research notes.
"""

import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "visuals")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =============================================================================
# 1. Tropical Neural Compilation Diagram
# =============================================================================

def tropical_diagram():
    svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" font-family="monospace">
  <defs>
    <linearGradient id="tropGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#2196F3;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#4CAF50;stop-opacity:1" />
    </linearGradient>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
    </marker>
  </defs>
  
  <rect width="800" height="500" fill="#f5f5f5" rx="10"/>
  <text x="400" y="35" text-anchor="middle" font-size="20" font-weight="bold" fill="#333">
    Tropical Neural Compilation: ReLU → (max, +) Semiring
  </text>
  
  <!-- ReLU Network Side -->
  <rect x="30" y="60" width="330" height="380" fill="white" stroke="#2196F3" stroke-width="2" rx="8"/>
  <text x="195" y="85" text-anchor="middle" font-size="16" font-weight="bold" fill="#2196F3">ReLU Network</text>
  
  <!-- Input neurons -->
  <circle cx="100" cy="180" r="20" fill="#E3F2FD" stroke="#2196F3" stroke-width="2"/>
  <text x="100" y="185" text-anchor="middle" font-size="12">x₁</text>
  <circle cx="100" cy="280" r="20" fill="#E3F2FD" stroke="#2196F3" stroke-width="2"/>
  <text x="100" y="285" text-anchor="middle" font-size="12">x₂</text>
  
  <!-- Hidden neurons -->
  <circle cx="220" cy="140" r="20" fill="#BBDEFB" stroke="#2196F3" stroke-width="2"/>
  <text x="220" y="145" text-anchor="middle" font-size="10">ReLU</text>
  <circle cx="220" cy="230" r="20" fill="#BBDEFB" stroke="#2196F3" stroke-width="2"/>
  <text x="220" y="235" text-anchor="middle" font-size="10">ReLU</text>
  <circle cx="220" cy="320" r="20" fill="#BBDEFB" stroke="#2196F3" stroke-width="2"/>
  <text x="220" y="325" text-anchor="middle" font-size="10">ReLU</text>
  
  <!-- Output -->
  <circle cx="310" cy="230" r="20" fill="#90CAF9" stroke="#2196F3" stroke-width="2"/>
  <text x="310" y="235" text-anchor="middle" font-size="12">y</text>
  
  <!-- Connections -->
  <line x1="120" y1="180" x2="200" y2="140" stroke="#666" stroke-width="1.5"/>
  <line x1="120" y1="180" x2="200" y2="230" stroke="#666" stroke-width="1.5"/>
  <line x1="120" y1="180" x2="200" y2="320" stroke="#666" stroke-width="1.5"/>
  <line x1="120" y1="280" x2="200" y2="140" stroke="#666" stroke-width="1.5"/>
  <line x1="120" y1="280" x2="200" y2="230" stroke="#666" stroke-width="1.5"/>
  <line x1="120" y1="280" x2="200" y2="320" stroke="#666" stroke-width="1.5"/>
  <line x1="240" y1="140" x2="290" y2="230" stroke="#666" stroke-width="1.5"/>
  <line x1="240" y1="230" x2="290" y2="230" stroke="#666" stroke-width="1.5"/>
  <line x1="240" y1="320" x2="290" y2="230" stroke="#666" stroke-width="1.5"/>
  
  <!-- Core Identity -->
  <rect x="60" y="370" width="270" height="50" fill="#E8F5E9" stroke="#4CAF50" stroke-width="2" rx="5"/>
  <text x="195" y="400" text-anchor="middle" font-size="14" font-weight="bold" fill="#2E7D32">
    ReLU(x) = max(x, 0) = x ⊕ₜ 0
  </text>

  <!-- Arrow -->
  <line x1="370" y1="250" x2="430" y2="250" stroke="#333" stroke-width="3" marker-end="url(#arrow)"/>
  <text x="400" y="240" text-anchor="middle" font-size="12" fill="#333">compile</text>
  
  <!-- Tropical Side -->
  <rect x="440" y="60" width="330" height="380" fill="white" stroke="#4CAF50" stroke-width="2" rx="8"/>
  <text x="605" y="85" text-anchor="middle" font-size="16" font-weight="bold" fill="#4CAF50">Tropical Polynomial</text>
  
  <!-- Tropical formula -->
  <text x="605" y="130" text-anchor="middle" font-size="13" fill="#333">f(x) = ⊕ᵢ (cᵢ ⊙ x^{aᵢ})</text>
  <text x="605" y="155" text-anchor="middle" font-size="13" fill="#333">= maxᵢ(cᵢ + aᵢ · x)</text>
  
  <!-- Piecewise linear graph -->
  <rect x="480" y="170" width="250" height="150" fill="#F1F8E9" stroke="#8BC34A" stroke-width="1" rx="3"/>
  <text x="605" y="190" text-anchor="middle" font-size="11" fill="#666">Piecewise Linear Function</text>
  
  <!-- Draw PWL function -->
  <polyline points="490,310 530,290 570,260 610,220 650,200 690,190 720,185" 
            fill="none" stroke="#4CAF50" stroke-width="3"/>
  <!-- Breakpoints -->
  <circle cx="530" cy="290" r="4" fill="#FF5722"/>
  <circle cx="610" cy="220" r="4" fill="#FF5722"/>
  <circle cx="690" cy="190" r="4" fill="#FF5722"/>
  <text x="605" y="340" text-anchor="middle" font-size="10" fill="#666">Breakpoints = tropical corners</text>
  
  <!-- Semiring box -->
  <rect x="470" y="360" width="280" height="60" fill="#E8F5E9" stroke="#4CAF50" stroke-width="2" rx="5"/>
  <text x="610" y="383" text-anchor="middle" font-size="13" font-weight="bold" fill="#2E7D32">
    𝕋 = (ℝ ∪ {-∞}, max, +)
  </text>
  <text x="610" y="408" text-anchor="middle" font-size="12" fill="#555">
    ⊕ = max  |  ⊙ = +  |  0ₜ = -∞  |  1ₜ = 0
  </text>
</svg>'''
    
    with open(os.path.join(OUTPUT_DIR, "tropical_compilation.svg"), "w") as f:
        f.write(svg)
    print("✅ Generated: tropical_compilation.svg")


# =============================================================================
# 2. Octonionic Quantum Computing Diagram
# =============================================================================

def octonionic_diagram():
    svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" font-family="monospace">
  <rect width="800" height="600" fill="#f5f5f5" rx="10"/>
  <text x="400" y="35" text-anchor="middle" font-size="20" font-weight="bold" fill="#333">
    Octonionic Quantum Computing: Triality Gates
  </text>
  
  <!-- Fano Plane -->
  <text x="200" y="70" text-anchor="middle" font-size="14" font-weight="bold" fill="#9C27B0">
    Fano Plane (Octonion Multiplication)
  </text>
  
  <!-- Fano plane vertices (heptagon) -->
  <circle cx="200" cy="120" r="15" fill="#E1BEE7" stroke="#9C27B0" stroke-width="2"/>
  <text x="200" y="125" text-anchor="middle" font-size="11" font-weight="bold">e₁</text>
  
  <circle cx="270" cy="155" r="15" fill="#E1BEE7" stroke="#9C27B0" stroke-width="2"/>
  <text x="270" y="160" text-anchor="middle" font-size="11" font-weight="bold">e₂</text>
  
  <circle cx="280" cy="235" r="15" fill="#E1BEE7" stroke="#9C27B0" stroke-width="2"/>
  <text x="280" y="240" text-anchor="middle" font-size="11" font-weight="bold">e₃</text>
  
  <circle cx="230" cy="290" r="15" fill="#E1BEE7" stroke="#9C27B0" stroke-width="2"/>
  <text x="230" y="295" text-anchor="middle" font-size="11" font-weight="bold">e₄</text>
  
  <circle cx="170" cy="290" r="15" fill="#E1BEE7" stroke="#9C27B0" stroke-width="2"/>
  <text x="170" y="295" text-anchor="middle" font-size="11" font-weight="bold">e₅</text>
  
  <circle cx="120" cy="235" r="15" fill="#E1BEE7" stroke="#9C27B0" stroke-width="2"/>
  <text x="120" y="240" text-anchor="middle" font-size="11" font-weight="bold">e₆</text>
  
  <circle cx="130" cy="155" r="15" fill="#E1BEE7" stroke="#9C27B0" stroke-width="2"/>
  <text x="130" y="160" text-anchor="middle" font-size="11" font-weight="bold">e₇</text>
  
  <!-- Some Fano lines -->
  <line x1="200" y1="135" x2="270" y2="155" stroke="#9C27B0" stroke-width="1.5" opacity="0.5"/>
  <line x1="270" y1="170" x2="230" y2="275" stroke="#9C27B0" stroke-width="1.5" opacity="0.5"/>
  <line x1="200" y1="135" x2="230" y2="275" stroke="#9C27B0" stroke-width="1.5" opacity="0.5"/>
  
  <!-- Triality -->
  <text x="200" y="340" text-anchor="middle" font-size="13" fill="#666">
    eᵢeⱼ = ±eₖ (Fano rules)
  </text>
  <text x="200" y="360" text-anchor="middle" font-size="13" fill="#666">
    Non-associative: (eᵢeⱼ)eₖ ≠ eᵢ(eⱼeₖ)
  </text>

  <!-- Triality Gate Diagram -->
  <rect x="400" y="60" width="370" height="250" fill="white" stroke="#FF5722" stroke-width="2" rx="8"/>
  <text x="585" y="85" text-anchor="middle" font-size="14" font-weight="bold" fill="#FF5722">
    Triality: τ ∈ Out(Spin(8)), τ³ = 1
  </text>
  
  <!-- Three representations -->
  <circle cx="500" cy="150" r="35" fill="#FFEBEE" stroke="#F44336" stroke-width="2"/>
  <text x="500" y="145" text-anchor="middle" font-size="11" font-weight="bold">8ᵥ</text>
  <text x="500" y="160" text-anchor="middle" font-size="9">vector</text>
  
  <circle cx="660" cy="150" r="35" fill="#E8F5E9" stroke="#4CAF50" stroke-width="2"/>
  <text x="660" y="145" text-anchor="middle" font-size="11" font-weight="bold">8ₛ</text>
  <text x="660" y="160" text-anchor="middle" font-size="9">spinor+</text>
  
  <circle cx="580" cy="260" r="35" fill="#E3F2FD" stroke="#2196F3" stroke-width="2"/>
  <text x="580" y="255" text-anchor="middle" font-size="11" font-weight="bold">8_c</text>
  <text x="580" y="270" text-anchor="middle" font-size="9">spinor-</text>
  
  <!-- Triality arrows -->
  <path d="M 535 145 Q 580 120 625 145" fill="none" stroke="#FF5722" stroke-width="2.5" 
        marker-end="url(#arrow2)"/>
  <path d="M 665 185 Q 640 230 615 255" fill="none" stroke="#FF5722" stroke-width="2.5"/>
  <path d="M 545 260 Q 510 220 505 185" fill="none" stroke="#FF5722" stroke-width="2.5"/>
  
  <text x="580" y="200" text-anchor="middle" font-size="16" font-weight="bold" fill="#FF5722">τ</text>
  
  <!-- Quantum Circuit -->
  <rect x="30" y="400" width="740" height="170" fill="white" stroke="#333" stroke-width="2" rx="8"/>
  <text x="400" y="425" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">
    Octonionic Quantum Circuit
  </text>
  
  <!-- Qubit line -->
  <line x1="80" y1="480" x2="720" y2="480" stroke="#333" stroke-width="2"/>
  <text x="60" y="485" text-anchor="middle" font-size="12">|e₀⟩</text>
  
  <!-- Gates -->
  <rect x="150" y="455" width="80" height="50" fill="#E8EAF6" stroke="#3F51B5" stroke-width="2" rx="4"/>
  <text x="190" y="478" text-anchor="middle" font-size="11" font-weight="bold">R₀₁(π/4)</text>
  <text x="190" y="495" text-anchor="middle" font-size="9">Spin(8)</text>
  
  <rect x="280" y="455" width="80" height="50" fill="#FCE4EC" stroke="#E91E63" stroke-width="2" rx="4"/>
  <text x="320" y="478" text-anchor="middle" font-size="11" font-weight="bold">τ</text>
  <text x="320" y="495" text-anchor="middle" font-size="9">Triality</text>
  
  <rect x="410" y="455" width="80" height="50" fill="#FFF3E0" stroke="#FF9800" stroke-width="2" rx="4"/>
  <text x="450" y="478" text-anchor="middle" font-size="11" font-weight="bold">σ₀</text>
  <text x="450" y="495" text-anchor="middle" font-size="9">Fano Refl.</text>
  
  <rect x="540" y="455" width="80" height="50" fill="#E0F7FA" stroke="#00BCD4" stroke-width="2" rx="4"/>
  <text x="580" y="478" text-anchor="middle" font-size="11" font-weight="bold">Measure</text>
  <text x="580" y="495" text-anchor="middle" font-size="9">→ {e₀,...,e₇}</text>
  
  <!-- Result -->
  <text x="680" y="485" text-anchor="middle" font-size="12" fill="#333">|eₖ⟩</text>
  
  <!-- Bottom note -->
  <text x="400" y="555" text-anchor="middle" font-size="11" fill="#666">
    Octonionic qubit: 7 degrees of freedom (vs 2 for standard qubit)
  </text>
</svg>'''
    
    with open(os.path.join(OUTPUT_DIR, "octonionic_quantum.svg"), "w") as f:
        f.write(svg)
    print("✅ Generated: octonionic_quantum.svg")


# =============================================================================
# 3. Holographic Proof Compression Diagram
# =============================================================================

def holographic_diagram():
    svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" font-family="monospace">
  <rect width="800" height="500" fill="#f5f5f5" rx="10"/>
  <text x="400" y="35" text-anchor="middle" font-size="20" font-weight="bold" fill="#333">
    Holographic Proof Compression: The Area Law
  </text>
  
  <!-- AdS/CFT side -->
  <rect x="30" y="55" width="340" height="410" fill="white" stroke="#795548" stroke-width="2" rx="8"/>
  <text x="200" y="80" text-anchor="middle" font-size="14" font-weight="bold" fill="#795548">
    Holographic Principle (Physics)
  </text>
  
  <!-- Bulk circle (AdS) -->
  <circle cx="200" cy="250" r="130" fill="#EFEBE9" stroke="#795548" stroke-width="2"/>
  <text x="200" y="200" text-anchor="middle" font-size="12" fill="#5D4037">Bulk (AdS)</text>
  <text x="200" y="220" text-anchor="middle" font-size="11" fill="#795548">Geometry</text>
  
  <!-- Minimal surface -->
  <path d="M 130 180 Q 200 280 270 180" fill="none" stroke="#FF5722" stroke-width="3" 
        stroke-dasharray="5,3"/>
  <text x="200" y="275" text-anchor="middle" font-size="11" fill="#FF5722" font-weight="bold">
    Minimal Surface (RT)
  </text>
  
  <!-- Boundary -->
  <text x="200" y="130" text-anchor="middle" font-size="11" fill="#1B5E20" font-weight="bold">
    Boundary (CFT)
  </text>
  
  <!-- Area law formula -->
  <rect x="60" y="400" width="280" height="50" fill="#FFF3E0" stroke="#FF9800" stroke-width="2" rx="5"/>
  <text x="200" y="423" text-anchor="middle" font-size="13" font-weight="bold" fill="#E65100">
    S(A) = |∂A| / (4G_N)
  </text>
  <text x="200" y="443" text-anchor="middle" font-size="11" fill="#BF360C">
    Ryu-Takayanagi Formula
  </text>
  
  <!-- Arrow -->
  <line x1="380" y1="260" x2="420" y2="260" stroke="#333" stroke-width="3" 
        marker-end="url(#arrow)"/>
  <text x="400" y="250" text-anchor="middle" font-size="10" fill="#333">analogy</text>
  
  <!-- Proof side -->
  <rect x="430" y="55" width="340" height="410" fill="white" stroke="#1565C0" stroke-width="2" rx="8"/>
  <text x="600" y="80" text-anchor="middle" font-size="14" font-weight="bold" fill="#1565C0">
    Proof Compression (Math)
  </text>
  
  <!-- Proof tree -->
  <circle cx="600" cy="140" r="15" fill="#BBDEFB" stroke="#1565C0" stroke-width="2"/>
  <text x="600" y="145" text-anchor="middle" font-size="9">⊢ φ</text>
  
  <line x1="590" y1="155" x2="550" y2="185" stroke="#1565C0" stroke-width="1.5"/>
  <line x1="610" y1="155" x2="650" y2="185" stroke="#1565C0" stroke-width="1.5"/>
  
  <circle cx="550" cy="200" r="12" fill="#BBDEFB" stroke="#1565C0" stroke-width="1.5"/>
  <text x="550" y="204" text-anchor="middle" font-size="8">MP</text>
  <circle cx="650" cy="200" r="12" fill="#BBDEFB" stroke="#1565C0" stroke-width="1.5"/>
  <text x="650" y="204" text-anchor="middle" font-size="8">∧I</text>
  
  <line x1="540" y1="212" x2="510" y2="242" stroke="#1565C0" stroke-width="1.5"/>
  <line x1="560" y1="212" x2="580" y2="242" stroke="#1565C0" stroke-width="1.5"/>
  <line x1="640" y1="212" x2="620" y2="242" stroke="#1565C0" stroke-width="1.5"/>
  <line x1="660" y1="212" x2="690" y2="242" stroke="#1565C0" stroke-width="1.5"/>
  
  <!-- Leaves (boundary) -->
  <rect x="495" y="245" width="35" height="20" fill="#C8E6C9" stroke="#4CAF50" stroke-width="1.5" rx="3"/>
  <text x="512" y="259" text-anchor="middle" font-size="8" fill="#2E7D32">hyp</text>
  <rect x="563" y="245" width="35" height="20" fill="#C8E6C9" stroke="#4CAF50" stroke-width="1.5" rx="3"/>
  <text x="580" y="259" text-anchor="middle" font-size="8" fill="#2E7D32">hyp</text>
  <rect x="605" y="245" width="35" height="20" fill="#C8E6C9" stroke="#4CAF50" stroke-width="1.5" rx="3"/>
  <text x="622" y="259" text-anchor="middle" font-size="8" fill="#2E7D32">hyp</text>
  <rect x="673" y="245" width="35" height="20" fill="#C8E6C9" stroke="#4CAF50" stroke-width="1.5" rx="3"/>
  <text x="690" y="259" text-anchor="middle" font-size="8" fill="#2E7D32">hyp</text>
  
  <!-- Minimal cut -->
  <line x1="470" y1="225" x2="740" y2="225" stroke="#FF5722" stroke-width="2" stroke-dasharray="5,3"/>
  <text x="600" y="296" text-anchor="middle" font-size="11" fill="#FF5722" font-weight="bold">
    Minimal Cut = RT Surface
  </text>
  
  <!-- Labels -->
  <text x="600" y="325" text-anchor="middle" font-size="11" fill="#333">
    Bulk = internal proof steps
  </text>
  <text x="600" y="345" text-anchor="middle" font-size="11" fill="#333">
    Boundary = hypotheses + conclusion
  </text>
  <text x="600" y="365" text-anchor="middle" font-size="11" fill="#333">
    Area = cut complexity
  </text>
  
  <!-- Compression formula -->
  <rect x="460" y="400" width="280" height="50" fill="#E8F5E9" stroke="#4CAF50" stroke-width="2" rx="5"/>
  <text x="600" y="423" text-anchor="middle" font-size="13" font-weight="bold" fill="#2E7D32">
    |proof| ≤ c · |boundary| · log |bulk|
  </text>
  <text x="600" y="443" text-anchor="middle" font-size="11" fill="#1B5E20">
    Holographic Compression Bound
  </text>
</svg>'''
    
    with open(os.path.join(OUTPUT_DIR, "holographic_compression.svg"), "w") as f:
        f.write(svg)
    print("✅ Generated: holographic_compression.svg")


# =============================================================================
# 4. Self-Learning Oracle Diagram
# =============================================================================

def oracle_diagram():
    svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" font-family="monospace">
  <rect width="800" height="500" fill="#f5f5f5" rx="10"/>
  <text x="400" y="35" text-anchor="middle" font-size="20" font-weight="bold" fill="#333">
    Self-Learning Oracles: Fixed Points as Truth
  </text>
  
  <!-- Oracle O box -->
  <rect x="50" y="60" width="300" height="200" fill="white" stroke="#673AB7" stroke-width="2" rx="8"/>
  <text x="200" y="85" text-anchor="middle" font-size="14" font-weight="bold" fill="#673AB7">
    Oracle O : X → X
  </text>
  
  <!-- Idempotency -->
  <text x="200" y="120" text-anchor="middle" font-size="13" fill="#333">O² = O (idempotent)</text>
  <text x="200" y="145" text-anchor="middle" font-size="13" fill="#333">Fix(O) = Im(O)</text>
  <text x="200" y="170" text-anchor="middle" font-size="13" fill="#333">O(O(x)) = O(x) ∀x</text>
  
  <!-- Self-learning arrow -->
  <path d="M 300 200 Q 350 240 300 250" fill="none" stroke="#673AB7" stroke-width="2"/>
  <text x="340" y="240" font-size="10" fill="#673AB7">self-apply</text>
  
  <!-- ML Connection -->
  <rect x="450" y="60" width="300" height="200" fill="white" stroke="#FF5722" stroke-width="2" rx="8"/>
  <text x="600" y="85" text-anchor="middle" font-size="14" font-weight="bold" fill="#FF5722">
    ML Connection
  </text>
  
  <text x="600" y="115" text-anchor="middle" font-size="12" fill="#333">Autoencoder: E∘D ≈ idempotent</text>
  <text x="600" y="140" text-anchor="middle" font-size="12" fill="#333">PCA: projection = oracle</text>
  <text x="600" y="165" text-anchor="middle" font-size="12" fill="#333">Training → Fix(O) = manifold</text>
  <text x="600" y="190" text-anchor="middle" font-size="12" fill="#333">ReLU oracle = tropical poly</text>
  
  <!-- Arrow between -->
  <line x1="355" y1="160" x2="445" y2="160" stroke="#333" stroke-width="2" 
        marker-end="url(#arrow)"/>
  <line x1="445" y1="160" x2="355" y2="160" stroke="#333" stroke-width="2"/>
  <text x="400" y="150" text-anchor="middle" font-size="10" fill="#333">≅</text>
  
  <!-- Team of Oracles -->
  <rect x="50" y="290" width="700" height="180" fill="white" stroke="#009688" stroke-width="2" rx="8"/>
  <text x="400" y="315" text-anchor="middle" font-size="14" font-weight="bold" fill="#009688">
    Oracle Team: Collaborative Self-Learning
  </text>
  
  <!-- Individual oracles -->
  <circle cx="150" cy="390" r="35" fill="#E0F2F1" stroke="#009688" stroke-width="2"/>
  <text x="150" y="385" text-anchor="middle" font-size="11" font-weight="bold">O_α</text>
  <text x="150" y="400" text-anchor="middle" font-size="9">Research</text>
  
  <circle cx="300" cy="390" r="35" fill="#E0F2F1" stroke="#009688" stroke-width="2"/>
  <text x="300" y="385" text-anchor="middle" font-size="11" font-weight="bold">O_β</text>
  <text x="300" y="400" text-anchor="middle" font-size="9">Hypothesize</text>
  
  <circle cx="450" cy="390" r="35" fill="#E0F2F1" stroke="#009688" stroke-width="2"/>
  <text x="450" y="385" text-anchor="middle" font-size="11" font-weight="bold">O_γ</text>
  <text x="450" y="400" text-anchor="middle" font-size="9">Experiment</text>
  
  <circle cx="600" cy="390" r="35" fill="#E0F2F1" stroke="#009688" stroke-width="2"/>
  <text x="600" y="385" text-anchor="middle" font-size="11" font-weight="bold">O_δ</text>
  <text x="600" y="400" text-anchor="middle" font-size="9">Validate</text>
  
  <!-- Arrows between oracles -->
  <line x1="185" y1="390" x2="265" y2="390" stroke="#009688" stroke-width="1.5"/>
  <line x1="335" y1="390" x2="415" y2="390" stroke="#009688" stroke-width="1.5"/>
  <line x1="485" y1="390" x2="565" y2="390" stroke="#009688" stroke-width="1.5"/>
  
  <!-- Feedback loop -->
  <path d="M 600 425 Q 600 460 150 460 Q 100 460 120 425" fill="none" 
        stroke="#009688" stroke-width="1.5" stroke-dasharray="4,3"/>
  <text x="400" y="455" text-anchor="middle" font-size="10" fill="#009688">
    iterate until T² = T (team convergence)
  </text>
</svg>'''
    
    with open(os.path.join(OUTPUT_DIR, "self_learning_oracle.svg"), "w") as f:
        f.write(svg)
    print("✅ Generated: self_learning_oracle.svg")


# =============================================================================
# 5. Unified Research Map
# =============================================================================

def unified_diagram():
    svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 700" font-family="monospace">
  <rect width="900" height="700" fill="#FAFAFA" rx="10"/>
  <text x="450" y="35" text-anchor="middle" font-size="22" font-weight="bold" fill="#333">
    Five Frontiers: A Unified Research Program
  </text>
  
  <!-- Central node -->
  <circle cx="450" cy="350" r="60" fill="#FFF9C4" stroke="#F9A825" stroke-width="3"/>
  <text x="450" y="340" text-anchor="middle" font-size="13" font-weight="bold" fill="#F57F17">Formal</text>
  <text x="450" y="358" text-anchor="middle" font-size="13" font-weight="bold" fill="#F57F17">Verification</text>
  <text x="450" y="376" text-anchor="middle" font-size="11" fill="#F57F17">(Lean 4)</text>
  
  <!-- 1. Millennium Problems -->
  <circle cx="450" cy="120" r="55" fill="#FFEBEE" stroke="#C62828" stroke-width="2.5"/>
  <text x="450" y="112" text-anchor="middle" font-size="11" font-weight="bold" fill="#C62828">Millennium</text>
  <text x="450" y="128" text-anchor="middle" font-size="11" font-weight="bold" fill="#C62828">Problems</text>
  <line x1="450" y1="175" x2="450" y2="290" stroke="#C62828" stroke-width="2"/>
  
  <!-- 2. Tropical Neural -->
  <circle cx="180" cy="220" r="55" fill="#E3F2FD" stroke="#1565C0" stroke-width="2.5"/>
  <text x="180" y="212" text-anchor="middle" font-size="11" font-weight="bold" fill="#1565C0">Tropical</text>
  <text x="180" y="228" text-anchor="middle" font-size="11" font-weight="bold" fill="#1565C0">Neural</text>
  <line x1="232" y1="247" x2="395" y2="325" stroke="#1565C0" stroke-width="2"/>
  
  <!-- 3. Octonionic Quantum -->
  <circle cx="720" cy="220" r="55" fill="#F3E5F5" stroke="#7B1FA2" stroke-width="2.5"/>
  <text x="720" y="212" text-anchor="middle" font-size="11" font-weight="bold" fill="#7B1FA2">Octonionic</text>
  <text x="720" y="228" text-anchor="middle" font-size="11" font-weight="bold" fill="#7B1FA2">Quantum</text>
  <line x1="668" y1="247" x2="505" y2="325" stroke="#7B1FA2" stroke-width="2"/>
  
  <!-- 4. Holographic Compression -->
  <circle cx="180" cy="480" r="55" fill="#E8F5E9" stroke="#2E7D32" stroke-width="2.5"/>
  <text x="180" y="472" text-anchor="middle" font-size="11" font-weight="bold" fill="#2E7D32">Holographic</text>
  <text x="180" y="488" text-anchor="middle" font-size="11" font-weight="bold" fill="#2E7D32">Compression</text>
  <line x1="232" y1="453" x2="395" y2="375" stroke="#2E7D32" stroke-width="2"/>
  
  <!-- 5. Self-Learning Oracles -->
  <circle cx="720" cy="480" r="55" fill="#FFF3E0" stroke="#E65100" stroke-width="2.5"/>
  <text x="720" y="472" text-anchor="middle" font-size="11" font-weight="bold" fill="#E65100">Self-Learning</text>
  <text x="720" y="488" text-anchor="middle" font-size="11" font-weight="bold" fill="#E65100">Oracles</text>
  <line x1="668" y1="453" x2="505" y2="375" stroke="#E65100" stroke-width="2"/>
  
  <!-- Cross-connections (dashed) -->
  <line x1="232" y1="240" x2="665" y2="240" stroke="#999" stroke-width="1" stroke-dasharray="4,4"/>
  <line x1="232" y1="460" x2="665" y2="460" stroke="#999" stroke-width="1" stroke-dasharray="4,4"/>
  <line x1="180" y1="275" x2="180" y2="425" stroke="#999" stroke-width="1" stroke-dasharray="4,4"/>
  <line x1="720" y1="275" x2="720" y2="425" stroke="#999" stroke-width="1" stroke-dasharray="4,4"/>
  
  <!-- Key connections labeled -->
  <text x="450" y="235" text-anchor="middle" font-size="9" fill="#666">ReLU = tropical ⊕ octonion gates</text>
  <text x="450" y="460" text-anchor="middle" font-size="9" fill="#666">area law bounds oracle truth sets</text>
  <text x="110" y="355" text-anchor="middle" font-size="9" fill="#666" transform="rotate(-90,110,355)">
    tropical = oracle polynomial
  </text>
  <text x="790" y="355" text-anchor="middle" font-size="9" fill="#666" transform="rotate(90,790,355)">
    quantum error = oracle gap
  </text>
  
  <!-- Bottom summary -->
  <rect x="100" y="600" width="700" height="80" fill="white" stroke="#333" stroke-width="1.5" rx="8"/>
  <text x="450" y="625" text-anchor="middle" font-size="13" font-weight="bold" fill="#333">
    Unifying Theme: Every computable function has a tropical representation,
  </text>
  <text x="450" y="645" text-anchor="middle" font-size="13" fill="#333">
    every oracle is idempotent, every proof has a holographic dual,
  </text>
  <text x="450" y="665" text-anchor="middle" font-size="13" fill="#333">
    and Lean 4 can verify them all.
  </text>
</svg>'''
    
    with open(os.path.join(OUTPUT_DIR, "unified_research_map.svg"), "w") as f:
        f.write(svg)
    print("✅ Generated: unified_research_map.svg")


if __name__ == "__main__":
    print("Generating SVG Visualizations...")
    print("=" * 50)
    tropical_diagram()
    octonionic_diagram()
    holographic_diagram()
    oracle_diagram()
    unified_diagram()
    print("\nAll visualizations generated in Research/visuals/")
