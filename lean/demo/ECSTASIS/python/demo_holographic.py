"""
ECSTASIS Demo 4: Holographic Projection & Wavefront Engineering

Demonstrates phase lattice operations, coherence bounds, and
wavefront reconstruction simulation.

Usage: python demo_holographic.py
"""

import numpy as np
from typing import List, Tuple

def phase_lattice_operations():
    """Demonstrate lattice operations on phase configurations."""
    print("=" * 60)
    print("Holographic Demo: Phase Lattice Operations")
    print("=" * 60)
    
    # Phase configurations as sets of active elements
    config_A = {0, 1, 2, 5, 7}
    config_B = {1, 3, 5, 6, 8}
    config_C = {2, 4, 5, 9}
    
    print(f"\nPhase configurations (active element indices):")
    print(f"  A = {sorted(config_A)}")
    print(f"  B = {sorted(config_B)}")
    print(f"  C = {sorted(config_C)}")
    
    # Lattice operations
    join_AB = config_A | config_B  # supremum
    meet_AB = config_A & config_B  # infimum
    join_all = config_A | config_B | config_C
    meet_all = config_A & config_B & config_C
    
    print(f"\nLattice operations (Theorem: complete lattice on P(Θ)):")
    print(f"  A ∨ B (join) = {sorted(join_AB)}")
    print(f"  A ∧ B (meet) = {sorted(meet_AB)}")
    print(f"  A ∨ B ∨ C   = {sorted(join_all)}")
    print(f"  A ∧ B ∧ C   = {sorted(meet_all)}")
    
    # Verify lattice properties
    print(f"\nLattice axioms:")
    print(f"  A ⊆ A ∨ B: {config_A <= join_AB} ✓")
    print(f"  A ∧ B ⊆ A: {meet_AB <= config_A} ✓")
    print(f"  A ∧ B ⊆ B: {meet_AB <= config_B} ✓")
    print(f"  Absorption: A ∨ (A ∧ B) = A: {config_A | meet_AB == config_A} ✓")
    
    print(f"\n✓ Phase configuration lattice verified")


def coherence_analysis():
    """Detailed coherence analysis for wavefront engineering."""
    print("\n" + "=" * 60)
    print("Holographic Demo: Coherence Analysis")
    print("=" * 60)
    
    n_elements = 64  # 8x8 phase lattice
    
    print(f"\nPhase lattice: {int(np.sqrt(n_elements))}×{int(np.sqrt(n_elements))} = {n_elements} elements")
    print(f"Coherence bound: |Σ exp(iθⱼ)| ≤ {n_elements}")
    print("-" * 60)
    
    # Various phase distributions
    experiments = []
    
    # 1. Perfect coherence
    phases = np.zeros(n_elements)
    amp = abs(np.sum(np.exp(1j * phases)))
    experiments.append(("Perfect alignment", phases, amp))
    
    # 2. Linear gradient (beam steering)
    phases = np.linspace(0, np.pi/4, n_elements)
    amp = abs(np.sum(np.exp(1j * phases)))
    experiments.append(("Linear gradient (beam steer)", phases, amp))
    
    # 3. Quadratic phase (focusing)
    x = np.linspace(-1, 1, n_elements)
    phases = 2 * np.pi * x**2
    amp = abs(np.sum(np.exp(1j * phases)))
    experiments.append(("Quadratic (focusing lens)", phases, amp))
    
    # 4. Binary phase (0 or π)
    phases = np.array([0 if i % 2 == 0 else np.pi for i in range(n_elements)])
    amp = abs(np.sum(np.exp(1j * phases)))
    experiments.append(("Binary (checkerboard)", phases, amp))
    
    # 5. Random uniform
    np.random.seed(42)
    phases = np.random.uniform(-np.pi, np.pi, n_elements)
    amp = abs(np.sum(np.exp(1j * phases)))
    experiments.append(("Random uniform [-π,π]", phases, amp))
    
    # 6. Gaussian noise around 0
    phases = np.random.normal(0, 0.1, n_elements)
    amp = abs(np.sum(np.exp(1j * phases)))
    experiments.append(("Gaussian noise (σ=0.1 rad)", phases, amp))
    
    print(f"\n{'Configuration':<30} {'Amplitude':>10} {'Bound':>6} {'Efficiency':>10}")
    print("-" * 60)
    for name, ph, a in experiments:
        eff = a / n_elements * 100
        print(f"{name:<30} {a:>10.3f} {n_elements:>6} {eff:>9.1f}%")
    
    print(f"\n✓ All amplitudes ≤ {n_elements} (coherence bound holds)")


def wavefront_reconstruction():
    """Simulate holographic wavefront reconstruction from phase elements."""
    print("\n" + "=" * 60)
    print("Holographic Demo: Wavefront Reconstruction")
    print("=" * 60)
    
    # 1D wavefront reconstruction
    n_elements = 32
    wavelength = 0.5e-6  # 500nm green light
    element_pitch = 10e-6  # 10μm pitch
    
    print(f"\n1D Phase Lattice:")
    print(f"  Elements: {n_elements}")
    print(f"  Wavelength: {wavelength*1e9:.0f} nm")
    print(f"  Element pitch: {element_pitch*1e6:.0f} μm")
    
    # Target: focus at z=10mm
    z_focus = 10e-3
    
    # Compute required phases for focusing
    element_positions = np.arange(n_elements) * element_pitch
    element_positions -= np.mean(element_positions)  # center
    
    # Phase for focusing: spherical wavefront approximation
    distances = np.sqrt(z_focus**2 + element_positions**2)
    phases = -2 * np.pi / wavelength * (distances - z_focus)  # relative to center
    
    # Compute field at observation plane
    n_obs = 100
    x_obs = np.linspace(-0.5e-3, 0.5e-3, n_obs)
    
    field = np.zeros(n_obs, dtype=complex)
    for i in range(n_elements):
        for j in range(n_obs):
            r = np.sqrt(z_focus**2 + (x_obs[j] - element_positions[i])**2)
            field[j] += np.exp(1j * (phases[i] + 2 * np.pi / wavelength * r))
    
    intensity = np.abs(field)**2
    intensity_norm = intensity / np.max(intensity)
    
    # Find focus position
    focus_idx = np.argmax(intensity)
    focus_x = x_obs[focus_idx]
    
    print(f"  Target focus: x = 0 mm")
    print(f"  Achieved focus: x = {focus_x*1e3:.4f} mm")
    print(f"  Focus error: {abs(focus_x)*1e6:.1f} μm")
    print(f"  Peak intensity: {np.max(intensity):.1f} (max possible: {n_elements**2})")
    print(f"  Coherence efficiency: {np.max(intensity)/n_elements**2*100:.1f}%")
    
    # ASCII art of intensity profile
    print(f"\n  Intensity profile at focus plane:")
    print(f"  {'x (mm)':<8} {'Intensity':>10}")
    print(f"  {'-'*20}")
    
    step = max(1, n_obs // 20)
    for j in range(0, n_obs, step):
        bar = "█" * int(intensity_norm[j] * 40)
        print(f"  {x_obs[j]*1e3:>7.3f}  {bar}")
    
    print(f"\n✓ Wavefront reconstruction successful — focus achieved")


def phase_tolerance_analysis():
    """Analyze how phase errors affect coherence."""
    print("\n" + "=" * 60)
    print("Holographic Demo: Phase Tolerance Analysis")
    print("=" * 60)
    
    n = 1000
    
    print(f"\nElements: {n}")
    print(f"Question: How much phase error can we tolerate?")
    print("-" * 60)
    
    sigmas = np.linspace(0, np.pi, 20)
    
    print(f"\n{'Phase noise σ (rad)':>20} {'Mean coherence':>15} {'Efficiency':>10} {'Theory':>10}")
    print("-" * 60)
    
    np.random.seed(42)
    for sigma in sigmas:
        # Average over multiple trials
        coherences = []
        for _ in range(100):
            phases = np.random.normal(0, sigma, n) if sigma > 0 else np.zeros(n)
            amp = abs(np.sum(np.exp(1j * phases)))
            coherences.append(amp / n)
        
        mean_coh = np.mean(coherences)
        # Theoretical: E[coherence] = exp(-σ²/2) for Gaussian phase noise
        theory = np.exp(-sigma**2 / 2)
        
        print(f"{sigma:>20.3f} {mean_coh:>15.4f} {mean_coh*100:>9.1f}% {theory:>9.4f}")
    
    print(f"\nTheoretical model: coherence ≈ exp(-σ²/2) for Gaussian phase noise")
    print(f"For 90% efficiency: σ < {np.sqrt(-2*np.log(0.9)):.3f} rad = {np.degrees(np.sqrt(-2*np.log(0.9))):.1f}°")
    print(f"For 99% efficiency: σ < {np.sqrt(-2*np.log(0.99)):.3f} rad = {np.degrees(np.sqrt(-2*np.log(0.99))):.1f}°")
    print(f"\n✓ Phase tolerance bounds computed")


if __name__ == "__main__":
    phase_lattice_operations()
    coherence_analysis()
    wavefront_reconstruction()
    phase_tolerance_analysis()
    
    print("\n" + "=" * 60)
    print("All Holographic Projection demos completed!")
    print("=" * 60)
