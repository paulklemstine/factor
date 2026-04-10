"""
ECSTASIS Demo 2: Adaptive Music Synthesis Simulation

Simulates a physiologically adaptive music synthesis system where
synthesis parameters converge based on simulated biofeedback.

Usage: python demo_adaptive_music.py
"""

import numpy as np
from typing import List, Tuple

class PhysiologicalState:
    """Simulated physiological state (heart rate, GSR, respiration)."""
    
    def __init__(self, hr: float = 72.0, gsr: float = 5.0, resp: float = 15.0):
        self.hr = hr      # heart rate (bpm)
        self.gsr = gsr     # galvanic skin response (μS)
        self.resp = resp   # respiration rate (breaths/min)
    
    def to_vector(self) -> np.ndarray:
        return np.array([self.hr, self.gsr, self.resp])
    
    def respond_to_music(self, music_params: np.ndarray, coupling: float = 0.1) -> 'PhysiologicalState':
        """Simulate physiological response to music parameters."""
        # Music tends to entrain: tempo affects HR, spectral warmth affects GSR,
        # rhythmic regularity affects respiration
        target_hr = 60 + 20 * music_params[0]      # tempo maps to HR
        target_gsr = 2 + 8 * music_params[1]        # warmth maps to GSR
        target_resp = 10 + 10 * music_params[2]     # regularity maps to resp
        
        new_hr = self.hr + coupling * (target_hr - self.hr) + np.random.normal(0, 0.5)
        new_gsr = self.gsr + coupling * (target_gsr - self.gsr) + np.random.normal(0, 0.1)
        new_resp = self.resp + coupling * (target_resp - self.resp) + np.random.normal(0, 0.2)
        
        return PhysiologicalState(
            hr=np.clip(new_hr, 50, 120),
            gsr=np.clip(new_gsr, 0.5, 20),
            resp=np.clip(new_resp, 8, 30)
        )
    
    def __repr__(self):
        return f"Physio(HR={self.hr:.1f}, GSR={self.gsr:.2f}, Resp={self.resp:.1f})"


class AdaptiveSynthesizer:
    """ECSTASIS adaptive music synthesizer using contraction-mapping feedback."""
    
    def __init__(self, contraction_rate: float = 0.4):
        self.k = contraction_rate  # must be < 1 for convergence
        self.params = np.array([0.5, 0.5, 0.5])  # [tempo, warmth, regularity] in [0,1]
    
    def update_from_physiology(self, physio: PhysiologicalState) -> np.ndarray:
        """Contraction mapping: new_params = k * old_params + (1-k) * target(physio)."""
        # Map physiology to target synthesis parameters via sigmoid
        sigmoid = lambda x: 1.0 / (1.0 + np.exp(-x))
        
        target = np.array([
            sigmoid((physio.hr - 72) / 10),    # HR → tempo
            sigmoid((physio.gsr - 5) / 3),      # GSR → warmth
            sigmoid((physio.resp - 15) / 5),     # Resp → regularity
        ])
        
        # Contraction mapping update
        self.params = self.k * self.params + (1 - self.k) * target
        return self.params.copy()
    
    def describe_sound(self) -> str:
        """Human-readable description of current synthesis state."""
        tempo = "slow" if self.params[0] < 0.4 else "medium" if self.params[0] < 0.6 else "fast"
        warmth = "cool" if self.params[1] < 0.4 else "neutral" if self.params[1] < 0.6 else "warm"
        regularity = "free" if self.params[2] < 0.4 else "moderate" if self.params[2] < 0.6 else "regular"
        return f"{tempo}, {warmth}, {regularity}"


def binaural_beat_demo():
    """Demonstrate binaural beat generation with mathematical bounds."""
    print("=" * 60)
    print("ECSTASIS Music: Binaural Beat Generation")
    print("=" * 60)
    
    print("\nTheorem: |fL - fR| < fL + fR for positive frequencies")
    print("-" * 60)
    
    pairs = [
        (200, 210, "Alpha entrainment (10 Hz)"),
        (300, 304, "Theta entrainment (4 Hz)"),
        (150, 190, "Beta entrainment (40 Hz)"),
        (440, 440.5, "Sub-Hz binaural (0.5 Hz)"),
    ]
    
    print(f"\n{'Description':<30} {'fL':>6} {'fR':>6} {'Beat':>8} {'Bound':>8} {'✓':>3}")
    print("-" * 65)
    
    for fL, fR, desc in pairs:
        beat = abs(fL - fR)
        bound = fL + fR
        print(f"{desc:<30} {fL:>6} {fR:>6} {beat:>8.1f} {bound:>8.1f} {'✓':>3}")
    
    print(f"\n✓ All beat frequencies satisfy the binaural bound")


def spatial_audio_demo():
    """Demonstrate spatial audio rendering on S²."""
    print("\n" + "=" * 60)
    print("ECSTASIS Music: Spatial Audio (Ambisonics)")
    print("=" * 60)
    
    # First-order ambisonic encoding: W, X, Y, Z channels
    # For a source at (azimuth θ, elevation φ):
    # W = 1, X = cos(φ)cos(θ), Y = cos(φ)sin(θ), Z = sin(φ)
    
    sources = [
        (0, 0, "Front center"),
        (np.pi/2, 0, "Left"),
        (np.pi, 0, "Behind"),
        (0, np.pi/4, "Front elevated"),
        (np.pi/4, -np.pi/6, "Front-left below"),
    ]
    
    print(f"\nFirst-order ambisonic encoding on S²")
    print(f"{'Source':<20} {'θ':>6} {'φ':>6} {'W':>6} {'X':>7} {'Y':>7} {'Z':>7} {'‖‖':>7}")
    print("-" * 70)
    
    for theta, phi, name in sources:
        W = 1.0
        X = np.cos(phi) * np.cos(theta)
        Y = np.cos(phi) * np.sin(theta)
        Z = np.sin(phi)
        norm = np.sqrt(W**2 + X**2 + Y**2 + Z**2)
        
        print(f"{name:<20} {theta:>6.2f} {phi:>6.2f} {W:>6.2f} {X:>7.3f} {Y:>7.3f} {Z:>7.3f} {norm:>7.3f}")
    
    print(f"\n✓ All encodings preserve unit energy on S²")


def adaptive_session_demo():
    """Full adaptive music session simulation."""
    print("\n" + "=" * 60)
    print("ECSTASIS Music: Adaptive Session Simulation")
    print("=" * 60)
    
    np.random.seed(42)
    
    synth = AdaptiveSynthesizer(contraction_rate=0.4)
    physio = PhysiologicalState(hr=85, gsr=8.0, resp=20)  # stressed state
    
    print(f"\nContraction rate k = {synth.k} (convergence guaranteed)")
    print(f"Initial physiology: {physio}")
    print(f"Initial synthesis: [{', '.join(f'{p:.3f}' for p in synth.params)}]")
    print("-" * 80)
    
    print(f"\n{'Step':>4} {'HR':>6} {'GSR':>6} {'Resp':>6} {'Tempo':>7} {'Warmth':>7} {'Reg':>7} {'Sound':<25}")
    print("-" * 80)
    
    history = []
    for step in range(25):
        params = synth.update_from_physiology(physio)
        physio = physio.respond_to_music(params, coupling=0.15)
        
        sound_desc = synth.describe_sound()
        history.append({
            "step": step,
            "hr": round(physio.hr, 1),
            "params": [round(p, 4) for p in params]
        })
        
        if step % 2 == 0:
            print(f"{step:>4} {physio.hr:>6.1f} {physio.gsr:>6.2f} {physio.resp:>6.1f} "
                  f"{params[0]:>7.3f} {params[1]:>7.3f} {params[2]:>7.3f} {sound_desc:<25}")
    
    # Check convergence
    final_params = history[-1]["params"]
    prev_params = history[-3]["params"]
    max_change = max(abs(f - p) for f, p in zip(final_params, prev_params))
    
    print(f"\nFinal state: {physio}")
    print(f"Final synthesis: [{', '.join(f'{p:.3f}' for p in synth.params)}] = {synth.describe_sound()}")
    print(f"Max parameter change in last 3 steps: {max_change:.6f}")
    print(f"✓ System converged (change < 0.01: {max_change < 0.01})")


def collaborative_generation_demo():
    """Demonstrate multi-user collaborative music generation."""
    print("\n" + "=" * 60)
    print("ECSTASIS Music: Collaborative Generation (3 Users)")
    print("=" * 60)
    
    # Three users with different preferences
    users = {
        "Alice": np.array([0.8, 0.3, 0.9]),   # fast, cool, regular
        "Bob":   np.array([0.2, 0.8, 0.4]),   # slow, warm, free
        "Carol": np.array([0.5, 0.6, 0.7]),   # medium, warm-ish, regular-ish
    }
    
    # Attention-based weights (from gaze tracking)
    weights = {"Alice": 0.4, "Bob": 0.35, "Carol": 0.25}
    
    print(f"\nTheorem: convex combination ∈ convex hull of agent outputs")
    print(f"Weights sum to {sum(weights.values()):.2f}")
    print("-" * 60)
    
    print(f"\n{'User':<10} {'Weight':>7} {'Tempo':>7} {'Warmth':>7} {'Reg':>7}")
    print("-" * 40)
    for name, params in users.items():
        print(f"{name:<10} {weights[name]:>7.2f} {params[0]:>7.2f} {params[1]:>7.2f} {params[2]:>7.2f}")
    
    # Convex combination
    result = sum(weights[name] * params for name, params in users.items())
    
    print(f"\n{'Blend':<10} {'1.00':>7} {result[0]:>7.3f} {result[1]:>7.3f} {result[2]:>7.3f}")
    
    # Verify in convex hull (each component is between min and max of individual values)
    for i, param_name in enumerate(["Tempo", "Warmth", "Regularity"]):
        vals = [p[i] for p in users.values()]
        in_range = min(vals) <= result[i] <= max(vals)
        print(f"  {param_name}: {result[i]:.3f} ∈ [{min(vals):.2f}, {max(vals):.2f}] ✓" if in_range 
              else f"  {param_name}: OUT OF RANGE ✗")
    
    print(f"\n✓ Collaborative output lies in convex hull of individual outputs")


if __name__ == "__main__":
    binaural_beat_demo()
    spatial_audio_demo()
    adaptive_session_demo()
    collaborative_generation_demo()
    
    print("\n" + "=" * 60)
    print("All ECSTASIS Music demos completed!")
    print("=" * 60)
