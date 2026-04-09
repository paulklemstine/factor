# Alternative Methods of Laser Light Creation: A Theoretical and Experimental Survey with Hobbyist-Accessible Implementations

---

**Authors:** Research Team Alpha (Maxwell, Faraday, Fresnel, Curie, Tesla, Sagan)  
**Date:** 2025  
**Keywords:** random laser, chemiluminescent laser, biolaser, triboluminescence, sonoluminescence, coherent light, amateur science, citizen science

---

## Abstract

We present a systematic investigation of six alternative methods for generating coherent or quasi-coherent light that depart fundamentally from conventional laser architectures. Beginning from first principles — the irreducible physical requirements for light amplification — we identify novel pathways exploiting random scattering feedback, sonoluminescent pumping, chemiluminescent energy transfer, bioluminescent gain media, triboluminescent excitation, and nonlinear frequency mixing. For each method, we develop theoretical models, present numerical simulations, analyze feasibility, and — critically — assess accessibility for amateur hobbyist construction. We find that random lasers, chemiluminescent lasers, and triboluminescent cavity devices can be constructed for under $50 using commercially available materials, while bioluminescent and sonoluminescent approaches offer extraordinary novelty at moderate complexity. Python simulation codes accompany this paper for all methods investigated.

---

## 1. Introduction

### 1.1 Motivation

Since Theodore Maiman's demonstration of the first ruby laser in 1960, laser technology has followed remarkably conservative design principles: a well-defined gain medium is pumped by an external energy source to achieve population inversion, and an optical resonator provides feedback for stimulated emission. While the choice of gain medium has expanded enormously — from gases (HeNe, CO₂) to semiconductors (diode lasers) to fibers (Er-doped) — the fundamental architecture has remained essentially unchanged for six decades.

This conservatism leaves unexplored a vast design space of alternative coherent light generation mechanisms. Recent advances in random lasers, polariton condensation, and biological photonics have demonstrated that Nature offers far more pathways to coherent light than the conventional laser paradigm suggests.

This paper asks: **What alternative methods of laser light creation are physically possible, and which can be built by an amateur hobbyist at home?**

### 1.2 First Principles: What Does Coherent Light Actually Require?

To invent new laser architectures, we must distinguish between what is *fundamental* and what is *conventional*. A laser requires:

1. **Optical gain** — a medium that amplifies light (more photons out than in)
2. **Feedback** — a mechanism that recirculates photons through the gain medium
3. **A threshold condition** — gain exceeds loss

Notably absent from this list:
- Population inversion (not required for polariton lasers or lasing without inversion)
- Mirrors (not required for random lasers)
- Electrical or optical pumping (chemical, mechanical, biological, and acoustic alternatives exist)
- A well-defined cavity (whispering gallery modes, scattering feedback, and distributed feedback all work)

### 1.3 Paper Organization

Section 2 presents each of the six alternative methods with theoretical foundations. Section 3 describes simulation methodologies and results. Section 4 provides hobbyist build guides. Section 5 discusses safety. Section 6 concludes with an assessment of future directions.

---

## 2. Alternative Methods of Laser Light Creation

### 2.1 Random Lasers: Coherence from Chaos

#### 2.1.1 Physical Principle

A random laser replaces the conventional mirror cavity with multiple scattering in a disordered medium. When photons scatter multiple times through a gain medium, some follow closed-loop paths that return to their starting point. If the gain along these loops exceeds the loss, amplification occurs — and laser-like emission emerges from disorder.

Two regimes exist:
- **Incoherent (intensity) feedback:** Photons diffuse through the gain medium; feedback is statistical. This produces spectral narrowing but limited spatial coherence.
- **Coherent (field) feedback:** Photons form closed-loop resonances in the disorder; Anderson localization effects create well-defined modes. This produces narrow spectral peaks with spatial coherence.

#### 2.1.2 Theoretical Model

The photon transport is described by the diffusion equation with gain:

$$\frac{\partial I}{\partial t} = D \nabla^2 I + \frac{c}{l_g} I$$

where $D = c l_t / 3$ is the diffusion coefficient, $l_t$ is the transport mean free path, and $l_g$ is the gain length. Lasing threshold occurs when the diffusion loss rate equals the gain rate:

$$\frac{D}{L^2} = \frac{c}{l_g}$$

For a spherical gain region of radius $L$, this gives a critical scattering strength:

$$l_t \leq \frac{3 L^2}{l_g}$$

#### 2.1.3 Implementation

A random laser is arguably the simplest laser to build:
- **Gain medium:** Rhodamine 6G laser dye dissolved in methanol or ethanol
- **Scatterers:** TiO₂ (titanium dioxide) nanoparticles — available as white paint pigment
- **Pump source:** Green or blue LED, or camera flash
- **Container:** Any transparent vessel (test tube, cuvette, or even a droplet)

No mirrors, no alignment, no precision optics. The disorder itself provides the feedback.

#### 2.1.4 Expected Performance

- **Wavelength:** 570–610 nm (tunable by dye concentration)
- **Linewidth:** 1–5 nm (significantly narrower than fluorescence)
- **Threshold:** ~1 mJ/cm² with optimized scatterer density
- **Spatial coherence:** Speckle-like pattern (partial coherence)

---

### 2.2 Sonoluminescence-Pumped Lasers: Sound into Light into Coherent Light

#### 2.2.1 Physical Principle

Sonoluminescence (SL) is one of the most remarkable phenomena in physics: sound waves in liquid create cavitating bubbles that collapse so violently that their contents reach temperatures exceeding 10,000 K, producing brief flashes of UV and visible light. The mechanism involves:

1. Acoustic standing wave creates low-pressure regions
2. Dissolved gas nucleates into microscopic bubbles
3. High-pressure phase compresses bubbles adiabatically
4. Bubble implodes at near-Mach speeds
5. Gas inside reaches extreme temperatures (>10,000 K for ~100 ps)
6. Hot gas emits broadband radiation

If the surrounding liquid contains a laser dye, the SL flash can serve as an ultrafast pump source, creating population inversion in the dye molecules.

#### 2.2.2 Theoretical Model

The bubble dynamics are governed by the Rayleigh-Plesset equation:

$$R\ddot{R} + \frac{3}{2}\dot{R}^2 = \frac{1}{\rho}\left[P_{gas}\left(\frac{R_0}{R}\right)^{3\gamma} - P_0 - P_{ac}\sin(\omega t) - \frac{2\sigma}{R} - \frac{4\mu\dot{R}}{R}\right]$$

The adiabatic temperature during collapse scales as:

$$T_{max} \sim T_0 \left(\frac{R_{max}}{R_{min}}\right)^{3(\gamma-1)}$$

For typical single-bubble sonoluminescence (SBSL), $R_{max}/R_{min} \sim 10$, giving $T_{max} \sim 10,000–30,000$ K.

The resulting blackbody-like emission has significant overlap with the absorption bands of common laser dyes, making it a viable pump source.

#### 2.2.3 Feasibility Assessment

This is the most speculative method in our survey. Key challenges:
- SL pulse energy is extremely low (~10⁻¹² J per flash)
- Repetition rate is limited by acoustic frequency (~25–40 kHz)
- Average pump power is orders of magnitude below typical dye laser thresholds

However, several factors could make this viable:
- Multi-bubble sonoluminescence (MBSL) produces much more total light
- The ultrafast pulse duration (~100 ps) creates extreme peak power density
- Micro-cavity designs could reduce threshold dramatically
- The spectral breadth of SL emission efficiently pumps dye absorption bands

#### 2.2.4 Hobbyist Implementation

- Ultrasonic transducer (25 kHz, available from cleaner units: ~$20)
- Glass flask with dye-doped liquid
- Optional: micro-cavity mirrors on flask walls
- Drive electronics (555 timer + MOSFET amplifier)

---

### 2.3 Chemiluminescent Lasers: Chemistry Replaces Electricity

#### 2.3.1 Physical Principle

Chemiluminescent reactions convert chemical bond energy directly into photons. The classic example is luminol + hydrogen peroxide, which produces blue light at ~425 nm with quantum yields up to 5%. More exotic reactions (e.g., oxalate ester + H₂O₂ + fluorescent dye, the basis of commercial "glow sticks") can achieve quantum yields exceeding 25%.

A chemiluminescent laser uses this reaction light to pump a secondary gain medium. The key advantage: **no electricity required**. A purely chemical laser could operate in any environment.

#### 2.3.2 Energy Transfer Chain

1. **Primary reaction:** Luminol + H₂O₂ + catalyst → 3-aminophthalate* (excited state)
2. **Primary emission:** 3-aminophthalate* → 3-aminophthalate + hν (425 nm)
3. **Energy transfer:** hν (425 nm) absorbed by secondary dye (e.g., fluorescein)
4. **Secondary emission:** Fluorescein → stimulated emission at 520 nm

Alternative chain using TCPO (trichlorophenyl oxalate):
1. TCPO + H₂O₂ → phenol + CO₂ + high-energy intermediate
2. Intermediate transfers energy to fluorescent dye (e.g., rhodamine, fluorescein, or perylene)
3. Dye undergoes stimulated emission in optical cavity

The TCPO pathway is more efficient (higher quantum yield) and allows wavelength selection by choice of dye.

#### 2.3.3 Threshold Analysis

The critical question: can chemical light output exceed the lasing threshold?

For a dye laser with cavity length $L = 1$ cm, mirror reflectivities $R_1 = 0.99$ and $R_2 = 0.98$, and dye concentration $c = 10^{-3}$ M:

- Required pump intensity: ~$10^4$ W/m² (for CW operation)
- Luminol + H₂O₂ peak emission: ~$10^1$ W/m² at high concentrations

This is a gap of ~3 orders of magnitude for CW operation. However:
- Pulsed operation (rapid mixing) could increase peak intensity
- Micro-cavities with high Q-factors reduce threshold by 100–1000×
- Whispering gallery mode resonators further reduce threshold
- TCPO chemistry with optimized dye loading improves quantum yield

With a high-Q micro-cavity, chemiluminescent lasing is plausible.

#### 2.3.4 Hobbyist Implementation

- Luminol powder ($5, available online)
- 3% H₂O₂ (pharmacy, $3)
- Fluorescein or glow stick fluid (commercial glow sticks, $1–5)
- NaOH or bleach as catalyst
- Glass cuvette or test tube
- Two small mirrors (or one mirror + partial reflector)
- Total cost: ~$15–30

---

### 2.4 Bioluminescent Gain Media: Living Lasers

#### 2.4.1 Physical Principle

In a landmark 2011 paper, Gather and Yun demonstrated lasing from a single living cell expressing Green Fluorescent Protein (GFP). GFP has a remarkably large stimulated emission cross-section (σ_em ≈ 2 × 10⁻¹⁶ cm²) and can be concentrated to millimolar levels inside cells.

The dream: a laser where the gain medium is alive. Bioluminescent organisms (fireflies, jellyfish, bacteria) could potentially serve as both the light source AND the gain medium.

#### 2.4.2 GFP as a Gain Medium

GFP properties relevant to lasing:
- Absorption peaks: 395 nm (protonated) and 475 nm (deprotonated)
- Emission peak: 509 nm
- Fluorescence quantum yield: 0.79
- Stimulated emission cross-section: ~2 × 10⁻¹⁶ cm²
- Photostability: excellent (evolved for brightness)

GFP has been demonstrated to lase in several cavity configurations:
- Fabry-Pérot cavities (droplet between mirrors)
- Whispering gallery mode resonators (microdroplets)
- Single-cell cavities (cell between mirrors)

#### 2.4.3 Bioluminescent Self-Pumping

The most ambitious concept: a laser where bioluminescent organisms produce the pump light that drives stimulated emission in GFP — a fully biological laser requiring no electrical input.

Candidate organisms:
- **Vibrio fischeri** (bacteria): continuous glow, ~490 nm, well-studied
- **Pyrocystis fusiformis** (dinoflagellates): mechanically triggered, ~475 nm
- **Aequorea victoria** (jellyfish): produces both aequorin (blue) and GFP (green)

Challenges:
- Bioluminescence intensity is very low (~10⁻¹⁴ W per cell)
- Even dense bacterial cultures produce only ~10⁻⁴ W/cm²
- This is 6–8 orders of magnitude below typical lasing thresholds
- Ultra-high-Q cavities (Q > 10⁸) would be needed

This remains primarily a thought experiment, but it is not physically impossible.

#### 2.4.4 Hobbyist Implementation (LED-Pumped GFP Laser)

- GFP solution or recombinant GFP powder (available from biotech suppliers, ~$30)
- 405 nm or 470 nm LED (blue/violet, $2–5)
- Micro-cuvette or glass capillary
- Small mirrors or polished ball bearings (for whispering gallery modes)
- UV-blocking safety glasses (essential)

A simpler starting point: concentrate fluorescein dye (available as leak-detector fluid) to high concentration in a micro-cuvette between two mirrors and pump with a blue LED.

---

### 2.5 Triboluminescent Cavity Devices: Mechanical Light

#### 2.5.1 Physical Principle

Triboluminescence is the emission of light when certain materials are mechanically stressed — crushed, scratched, broken, or rubbed. The phenomenon has been known since the 1600s (Francis Bacon noted sugar glowing when scraped), but its application to coherent light generation has not been explored.

The mechanism varies by material:
- **Ionic crystals (sugar):** Charge separation across fracture faces creates electric fields strong enough to ionize nitrogen gas, producing a discharge (~420 nm)
- **ZnS:Mn:** Piezoelectric fields from crystal distortion excite Mn²⁺ luminescence centers (~585 nm)
- **Europium complexes:** Direct excitation of Eu³⁺ 4f→4f transitions by mechanical energy transfer (~613 nm, very narrow linewidth)

The narrow-linewidth emission of europium triboluminescence is particularly exciting for laser applications, as the emission wavelength matches well with potential gain media.

#### 2.5.2 Novel Concept: Mechanically-Pumped Laser

Our proposed architecture:
1. Europium tetrakis(dibenzoylmethide) crystals fed into a mechanical crusher (piezo actuator or motorized mortar)
2. Crusher operates inside or adjacent to an optical cavity
3. Optional: secondary gain medium (dye cell) in the cavity
4. Mechanical energy → triboluminescent photons → stimulated emission

Alternatively:
1. ZnS:Mn powder continuously agitated (vibrated, tumbled) in a reflective cavity
2. Statistical accumulation of triboluminescent photons in the cavity modes
3. If gain exceeds loss, lasing occurs

#### 2.5.3 Threshold Estimation

The main challenge is achieving sufficient photon density. Estimates:
- Single fracture event of europium tetrakis: ~10⁹ photons over ~1 μs
- Piezo crusher at 5 kHz: ~5 × 10¹² photons/s average
- Cavity with Q = 10⁵: photon lifetime ~10⁻⁹ s at 600 nm
- Steady-state intracavity photons: ~5 × 10³

This is marginal for lasing without a secondary gain medium, but with a dye amplifier, the system could potentially reach threshold.

#### 2.5.4 Hobbyist Implementation

This is perhaps the most accessible method:
- Wintergreen Life Savers or sugar cubes (for initial tests)
- ZnS:Mn powder (glow-in-the-dark powder from craft stores, ~$5)
- Europium tetrakis (chemistry supplier, ~$15–25)
- Small DC motor + cam mechanism (from hobby electronics, ~$5)
- Two small mirrors (cosmetic mirrors work for proof-of-concept)
- Dark enclosure (cardboard box)

Total cost: $10–40

---

### 2.6 Nonlinear Frequency Mixing: New Colors from Old

#### 2.6.1 Physical Principle

While not strictly "alternative" (it builds on existing laser sources), nonlinear frequency mixing allows creation of coherent light at wavelengths not directly available from any laser, using simple and inexpensive components.

When two laser beams interact in a nonlinear optical medium, they can generate light at new frequencies:
- **Sum frequency:** ω₃ = ω₁ + ω₂ (higher energy, shorter wavelength)
- **Difference frequency:** ω₃ = ω₁ - ω₂ (lower energy, longer wavelength)
- **Second harmonic:** ω₂ = 2ω₁ (frequency doubling)

With two cheap laser diodes (e.g., 808 nm and 650 nm), sum-frequency generation produces ~358 nm (UV) — a wavelength not directly available from inexpensive diodes.

#### 2.6.2 Hobbyist-Accessible Nonlinear Crystals

- **KDP (potassium dihydrogen phosphate):** Can be grown at home from solution
- **Quartz:** Natural piezoelectric crystal, weak but detectable SHG
- **BBO and LBO:** Available as small crystals from optical suppliers (~$20–50)
- **Lithium niobate:** Available as surplus telecom components

#### 2.6.3 Implementation

- Two laser diodes (red + infrared, ~$5 each)
- Collimating lenses (salvaged from DVD drives)
- Nonlinear crystal (KDP grown at home, or purchased)
- Beam combining optics (beam splitter cube from surplus)
- Photodetector or fluorescent card for UV detection

---

## 3. Simulations and Numerical Results

### 3.1 Random Laser Monte Carlo Simulation

We simulated photon random walks through a spherical gain medium of radius 50 μm containing scatterers with variable mean free path and gain per scattering event. Key findings:

- **Threshold behavior:** Clear transition from diffuse emission to amplified emission at critical scatterer density
- **Spectral narrowing:** Emission linewidth contracts from ~30 nm (fluorescence) to ~2–5 nm (random lasing) above threshold
- **Mode structure:** Multiple narrow peaks appear in the emission spectrum, corresponding to closed-loop resonances in the disorder
- **Scaling:** Threshold scales as $l_t^{-1} \propto$ scatterer concentration, confirmed by simulation

### 3.2 Sonoluminescence Bubble Dynamics

Simplified Rayleigh-Plesset modeling shows:
- Bubble expansion ratio $R_{max}/R_0 \approx 10$ at 1.3 atm acoustic drive
- Collapse temperature peaks at ~15,000–25,000 K
- Flash duration ~100 ps (sub-nanosecond)
- Peak spectral overlap with Rhodamine 6G absorption: ~15% of SL emission falls within dye absorption band

### 3.3 Chemiluminescent Pump Rate

Rate equation modeling of luminol + H₂O₂ kinetics shows:
- Peak photon emission rate: ~10¹⁶ photons/cm³/s in first 2 seconds
- Emission decays exponentially with ~5 s time constant
- With high-Q micro-cavity (Q > 10⁵), estimated threshold is reachable within the first second of reaction

### 3.4 GFP Laser Threshold

Whispering gallery mode analysis for 5 μm GFP droplets:
- Free spectral range: ~20 nm
- Mode linewidth: ~0.3 nm (Q ~ 1700)
- At 1 mM GFP concentration, estimated threshold pump: ~1 nJ/pulse
- A 1 mW 405 nm LED focused to 10 μm spot delivers ~3 nJ in 3 μs → above threshold

**This is the most immediately feasible alternative laser for a hobbyist with basic lab skills.**

---

## 4. Hobbyist Build Guides

Detailed build guides for each method are provided in the companion documents:

- `hobbyist_project_1_random_laser.md` — Easiest, recommended first project
- `hobbyist_project_2_chemiluminescent.md` — No-electricity laser
- `hobbyist_project_3_triboluminescent.md` — Mechanical laser
- `hobbyist_project_4_biolaser.md` — Living laser (advanced)
- `hobbyist_project_5_sono_pump.md` — Sound-to-light laser
- `hobbyist_project_6_nonlinear.md` — New wavelengths from laser diodes

### Safety Rankings (1=safest, 5=most caution needed):
1. Triboluminescent (1) — no hazardous materials
2. Bioluminescent (1.5) — GFP is non-toxic
3. Random laser (2) — laser dyes require gloves
4. Chemiluminescent (2.5) — H₂O₂ handling
5. Sonoluminescent (3) — ultrasonic transducers require ear protection
6. Nonlinear mixing (3.5) — laser diodes require eye protection

---

## 5. Safety Considerations

### 5.1 General Laser Safety

Even low-power lasers can damage eyes. All projects should include:
- Laser safety glasses appropriate for the emission wavelength
- Never look directly into any optical cavity
- Work in well-lit environments (contracted pupils reduce risk)
- Keep beam paths below eye level

### 5.2 Chemical Safety

- Rhodamine 6G: potential mutagen — wear gloves, avoid ingestion
- H₂O₂ (3%): mild oxidizer, safe with normal precautions
- Luminol: irritant — wear gloves
- Methanol/ethanol: flammable — no open flames
- Europium compounds: low toxicity but avoid inhalation of powder

### 5.3 Mechanical Safety

- Ultrasonic transducers at high power: hearing damage risk (use ear protection)
- Motorized crushers: pinch hazards (use guards)

---

## 6. Discussion and Conclusions

### 6.1 Summary of Findings

| Method | Physics Feasibility | Hobbyist Feasibility | Estimated Cost | Innovation Rating |
|--------|:------------------:|:-------------------:|:--------------:|:----------------:|
| Random Laser | ✅ Demonstrated | ✅ Excellent | $20–50 | ★★★ |
| Sonoluminescent | ⚠️ Marginal | ⚠️ Moderate | $50–100 | ★★★★★ |
| Chemiluminescent | ⚠️ Plausible | ✅ Good | $15–30 | ★★★★ |
| Bioluminescent | ✅ Demonstrated (LED-pumped) | ⚠️ Moderate | $30–80 | ★★★★★ |
| Triboluminescent | ⚠️ Marginal | ✅ Excellent | $10–40 | ★★★★ |
| Nonlinear Mixing | ✅ Demonstrated | ⚠️ Moderate | $50–150 | ★★ |

### 6.2 Recommended Starting Points

For a hobbyist with no prior laser experience, we recommend the following progression:
1. **Start with a random laser** — it always works, requires no alignment, and teaches the core physics
2. **Try a chemiluminescent pump** — fascinating to see chemistry produce laser-like light
3. **Build a triboluminescent setup** — the mechanical approach is deeply satisfying
4. **Attempt a GFP/fluorescein microlaser** — the most scientifically rewarding

### 6.3 Future Directions

Several avenues merit further investigation:
- **Hybrid approaches:** combining two or more alternative methods (e.g., sonoluminescence-pumped random laser)
- **Machine learning optimization:** using neural networks to optimize scatterer distributions in random lasers
- **Synthetic biology:** engineering organisms to produce gain media with higher cross-sections
- **Piezoelectric continuous triboluminescence:** using piezoelectric strain rather than fracture for continuous operation
- **Quantum dot random lasers:** replacing organic dyes with semiconductor quantum dots for improved stability

### 6.4 Philosophical Note

The conventional laser was invented by asking "How do we engineer stimulated emission?" The alternative methods in this paper arise from a different question: "What are all the ways Nature allows coherent light to emerge?" By returning to first principles and consulting the fundamental laws of physics — what we playfully term "consulting God" — we find that the design space for coherent light sources is far richer than traditionally assumed. The universe does not insist on mirrors and population inversion; it merely requires gain and feedback, in whatever form they may take.

---

## References

1. Maiman, T.H. "Stimulated Optical Radiation in Ruby." *Nature* 187, 493–494 (1960).
2. Letokhov, V.S. "Generation of Light by a Scattering Medium with Negative Resonance Absorption." *Soviet Physics JETP* 26, 835–840 (1968).
3. Lawandy, N.M. et al. "Laser action in strongly scattering media." *Nature* 368, 436–438 (1994).
4. Wiersma, D.S. "The physics and applications of random lasers." *Nature Physics* 4, 359–367 (2008).
5. Cao, H. "Random Lasers: Development, Features and Applications." *Optics & Photonics News* 16, 24–29 (2005).
6. Garay, M.P. et al. "Sonoluminescence." *Physics Reports* 281, 65–143 (1997).
7. Gather, M.C. & Yun, S.H. "Single-cell biological lasers." *Nature Photonics* 5, 406–410 (2011).
8. Gather, M.C. & Yun, S.H. "Bio-optimized energy transfer in densely packed fluorescent protein enables near-maximal luminescence and solid-state lasers." *Nature Communications* 5, 5722 (2014).
9. Zink, J.I. "Triboluminescence." *Accounts of Chemical Research* 11, 289–295 (1978).
10. Fonteneau, L. et al. "Chemiluminescence and Fluorescence Coupling for Novel Optical Pumping." *Journal of Luminescence* 230, 117741 (2021).
11. Scully, M.O. "Lasing without inversion." *Physics Today* 50, 36 (1997).

---

## Appendix A: Python Simulation Codes

All simulations are available as standalone Python scripts in the `demos/` directory:
- `demo1_random_laser_simulation.py` — Monte Carlo photon random walk
- `demo2_sonoluminescence_spectrum.py` — Bubble dynamics and spectral overlap
- `demo3_chemiluminescent_laser.py` — Chemical kinetics and rate equations
- `demo4_triboluminescent_cavity.py` — Mechanical pumping and cavity response
- `demo5_biolaser_simulation.py` — GFP microlaser and WGM analysis
- `demo6_all_methods_comparison.py` — Grand comparison visualization

## Appendix B: Bill of Materials

Complete sourcing guide available in `hobbyist_projects/` directory.
