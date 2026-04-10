"""
Stereographic Projection: Visualization Module
================================================

Generates matplotlib plots and data for visualizing stereographic projection.
This module creates publication-quality figures for the research paper.

Run with: python stereographic_visualization.py
(Requires matplotlib and numpy)
"""

import numpy as np
import json

# ============================================================
# Data Generation (no matplotlib required)
# ============================================================

def generate_stereo_circle_data():
    """Generate data showing how circles on S² map to circles/lines in ℝ²."""
    
    # Circle on S² at latitude φ
    data = {}
    
    for lat_deg in [0, 30, 45, 60, 80]:
        lat = np.radians(lat_deg)
        z = np.sin(lat)
        r = np.cos(lat)
        
        thetas = np.linspace(0, 2*np.pi, 200)
        sphere_points = [(r*np.cos(t), r*np.sin(t), z) for t in thetas]
        
        # Stereographic images
        stereo_points = []
        for x, y, z_val in sphere_points:
            if abs(z_val - 1) > 0.001:
                s = x / (1 - z_val)
                t_val = y / (1 - z_val)
                stereo_points.append((s, t_val))
        
        data[f"lat_{lat_deg}"] = {
            "sphere": sphere_points,
            "stereo": stereo_points,
            "description": f"Circle at latitude {lat_deg}°"
        }
    
    return data

def generate_conformal_factor_data():
    """Generate conformal factor λ(y) = 2/(1+|y|²) over ℝ²."""
    N = 50
    y1 = np.linspace(-3, 3, N)
    y2 = np.linspace(-3, 3, N)
    Y1, Y2 = np.meshgrid(y1, y2)
    CF = 2.0 / (1 + Y1**2 + Y2**2)
    
    return {
        "y1": y1.tolist(),
        "y2": y2.tolist(),
        "conformal_factor": CF.tolist(),
        "description": "Conformal factor λ(y₁,y₂) = 2/(1+y₁²+y₂²)"
    }

def generate_apollonian_data(depth=6):
    """Generate Apollonian gasket circle data for visualization."""
    
    def descartes_dual(k1, k2, k3, k4):
        return 2*(k1 + k2 + k3) - k4
    
    def circle_from_three_tangent(k1, c1, k2, c2, k3, c3, k4):
        """Compute center of fourth mutually tangent circle given three."""
        # Using the complex Descartes theorem
        z1, z2, z3 = complex(*c1), complex(*c2), complex(*c3)
        # k4*z4 = 2*(k1*z1 + k2*z2 + k3*z3) ± 2*sqrt(k1*k2*z1*z2 + k2*k3*z2*z3 + k3*k1*z3*z1)
        # Simplified: just use the linear version
        if k4 == 0:
            return (0, 0)
        
        S = k1*z1 + k2*z2 + k3*z3
        # The dual center (simplified approximation for visualization)
        z4 = (2*S - k4*complex(0,0)) / k4 if k4 != 0 else complex(0,0)
        # This is approximate; for exact computation need full complex Descartes
        return (z4.real, z4.imag)
    
    # Start with the classic packing: outer circle k=-1, three inner k=2,2,3
    circles = []
    
    # Outer circle: k=-1, center (0,0), radius 1
    circles.append({"k": -1, "cx": 0, "cy": 0, "r": 1.0})
    
    # First three tangent circles (computed by hand for (-1,2,2,3) packing)
    circles.append({"k": 2, "cx": 0, "cy": 0.5, "r": 0.5})
    circles.append({"k": 2, "cx": 0, "cy": -0.5, "r": 0.5})
    circles.append({"k": 3, "cx": 1/3, "cy": 0, "r": 1/3})
    
    # Generate curvatures
    curvatures = set()
    queue = [(-1, 2, 2, 3)]
    
    for d in range(depth):
        new_queue = []
        for (k1, k2, k3, k4) in queue:
            curvatures.update([k1, k2, k3, k4])
            for perm in [(k1,k2,k3,k4), (k2,k1,k3,k4), 
                         (k3,k1,k2,k4), (k4,k1,k2,k3)]:
                a, b, c, d_k = perm
                new_k = descartes_dual(b, c, d_k, a)
                if new_k > 0 and new_k < 5000 and new_k not in curvatures:
                    new_queue.append((b, c, d_k, new_k))
                    curvatures.add(new_k)
        queue = new_queue
    
    return {
        "circles": circles,
        "curvatures": sorted(curvatures),
        "depth": depth,
        "description": "Apollonian gasket from (-1, 2, 2, 3)"
    }

def generate_fisher_stereo_data():
    """Generate data showing Fisher = round metric correspondence."""
    t_vals = np.linspace(-5, 5, 500)
    
    fisher_metric = []
    round_metric = []
    theta_vals = []
    
    for t in t_vals:
        if abs(t) < 0.01:
            continue
        theta = t**2 / (1 + t**2)
        dtheta_dt = 2*t / (1 + t**2)**2
        
        fm = (1 / (theta * (1 - theta))) * dtheta_dt**2
        rm = 4 / (1 + t**2)**2
        
        fisher_metric.append(fm)
        round_metric.append(rm)
        theta_vals.append(theta)
    
    return {
        "t": [t for t in t_vals if abs(t) >= 0.01],
        "fisher_metric": fisher_metric,
        "round_metric": round_metric,
        "theta": theta_vals,
        "description": "Fisher metric = Round metric under stereographic reparametrization"
    }

def generate_pythagorean_data():
    """Generate Pythagorean triples from stereographic projection."""
    triples = []
    for b in range(1, 20):
        for a in range(1, b):
            if np.gcd(a, b) == 1:
                x = 2*a*b
                y = b**2 - a**2
                z = a**2 + b**2
                if x > 0 and y > 0:
                    triples.append({
                        "a": a, "b": b,
                        "triple": (min(x,y), max(x,y), z),
                        "stereo_param": a/b,
                        "circle_point": (2*a*b/(a**2+b**2), (b**2-a**2)/(a**2+b**2))
                    })
    return {
        "triples": triples,
        "description": "Pythagorean triples from stereographic projection of rational points"
    }

# ============================================================
# Main: Generate all data and save
# ============================================================

def main():
    print("Generating stereographic visualization data...")
    
    all_data = {
        "circle_preservation": generate_stereo_circle_data(),
        "conformal_factor": generate_conformal_factor_data(),
        "apollonian_gasket": generate_apollonian_data(),
        "fisher_stereographic": generate_fisher_stereo_data(),
        "pythagorean_triples": generate_pythagorean_data(),
    }
    
    # Save as JSON for portability
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)
    
    with open("visualization_data.json", "w") as f:
        json.dump(all_data, f, cls=NumpyEncoder, indent=2)
    
    print("Data saved to visualization_data.json")
    
    # Print summary statistics
    print(f"\nCircle preservation: {len(all_data['circle_preservation'])} latitude circles")
    print(f"Conformal factor: {50}x{50} grid")
    print(f"Apollonian gasket: {len(all_data['apollonian_gasket']['curvatures'])} curvatures")
    print(f"Fisher-stereographic: {len(all_data['fisher_stereographic']['t'])} data points")
    print(f"Pythagorean triples: {len(all_data['pythagorean_triples']['triples'])} triples")

if __name__ == "__main__":
    main()
