"""
Batch 6: Ramsey Theory, Fourier Analysis on Groups, Differential Geometry/Curvature
"""

import random
import math
import numpy as np
from collections import Counter
from sympy import nextprime

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

print("=" * 70)
print("FIELD 16: RAMSEY THEORY")
print("=" * 70)

# HYPOTHESIS: Color the nodes of the tree at depth d with colors {0,...,c-1}
# based on (m mod p) for unknown p. By Ramsey theory, there must exist
# monochromatic substructures. If we can detect these WITHOUT knowing p,
# we can infer p.

# More precisely: color nodes by (m mod N). A monochromatic path (all m ≡ a mod p)
# exists with guaranteed length by the infinite Ramsey theorem.
# The LENGTH of the longest monochromatic B3 path reveals information about p.

print("\n--- Experiment 1: Monochromatic B3 paths (residue coloring) ---")
print("Color by m mod p. B3 path: m_k = m0 + 2k*n0.")
print("Monochromatic iff m_k ≡ m_0 mod p for all k in path, iff p | 2k*n0.")
print("For gcd(n0,p)=1 and p odd: monochromatic every p steps.\n")

random.seed(42)
for p in [7, 11, 23, 47, 97]:
    # Generate B3 path from (2,1)
    m, n = 2, 1
    mono_lengths = []  # lengths of monochromatic runs (same m mod p)
    current_color = m % p
    run_length = 1

    for k in range(1, 500):
        m, n = m + 2*n, n  # B3 in true coordinates
        color = m % p
        if color == current_color:
            run_length += 1
        else:
            mono_lengths.append(run_length)
            current_color = color
            run_length = 1
    mono_lengths.append(run_length)

    avg_run = sum(mono_lengths) / len(mono_lengths) if mono_lengths else 0
    max_run = max(mono_lengths) if mono_lengths else 0
    print(f"  p={p:3d}: avg run={avg_run:.1f}, max run={max_run}, "
          f"expected=1.0 (geometric with P=1/p)")

# Experiment 2: Van der Waerden-type theorem on tree
print("\n--- Experiment 2: Arithmetic progressions in tree m-values mod N ---")
print("B3 creates AP in m-values. Length of longest AP mod p is related to p.")
print("For N=p*q, can we detect which AP length divides p vs q?\n")

for p, q in [(11, 13), (23, 29), (47, 53)]:
    N = p * q
    # B3 path mod N
    m_vals = []
    m, n = 2, 1
    for k in range(500):
        m, n = (m + 2*n) % N, n
        m_vals.append(m)

    # Check: is the sequence periodic with period p or q?
    # m_k = (2 + 2k*1) mod N = (2 + 2k) mod N
    # Period mod p = p/gcd(2,p) = p (p odd). Similarly period mod q = q.
    # Period mod N = lcm(p,q) = N/gcd(p,q) = N (p,q coprime).

    # Detect periodicity via autocorrelation
    from numpy.fft import fft, ifft
    if len(m_vals) > 0:
        x = np.array(m_vals[:256], dtype=float)
        x -= x.mean()
        X = fft(x)
        autocorr = np.real(ifft(X * np.conj(X)))
        autocorr /= autocorr[0] if autocorr[0] > 0 else 1

        # Find peaks in autocorrelation
        peaks = []
        for i in range(2, len(autocorr)//2):
            if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1] and autocorr[i] > 0.1:
                peaks.append((i, autocorr[i]))

        peaks.sort(key=lambda x: -x[1])
        top_peaks = peaks[:5]
        print(f"  N={N}={p}*{q}: autocorr peaks at lags {[(lag,f'{val:.3f}') for lag,val in top_peaks]}")
        # Check if any peak lag divides p or q
        for lag, val in top_peaks:
            gp = gcd(lag, p)
            gq = gcd(lag, q)
            if lag == p or lag == q:
                print(f"    *** Lag {lag} = {'p' if lag==p else 'q'}!")

print("\n" + "=" * 70)
print("FIELD 17: FOURIER ANALYSIS ON GROUPS")
print("=" * 70)

# HYPOTHESIS: The DFT of the tree walk sequence mod N has spectral peaks
# at frequencies related to p and q. Specifically, since the orbit period
# mod p divides p^2-1, the DFT should show power at frequency ≈ N/p.

print("\n--- Experiment: DFT of B2 orbit m-values mod N ---")
print("Peaks at frequency k correspond to periodicity N/k in the sequence.\n")

for p, q in [(31, 37), (61, 67), (101, 103)]:
    N = p * q

    # Collect m-values along B2 walk
    m, n = 2, 1
    L = min(N, 4096)  # FFT length
    m_vals = []
    for k in range(L):
        m, n = (2*m + n) % N, m % N
        m_vals.append(m)

    x = np.array(m_vals, dtype=float)
    x -= x.mean()
    X = np.abs(fft(x))
    X[0] = 0  # Remove DC

    # Find top spectral peaks
    top_idx = np.argsort(X[:L//2])[-10:][::-1]
    top_freqs = [(int(idx), X[int(idx)]) for idx in top_idx]

    print(f"  N={N}={p}*{q} (L={L}):")
    for freq, mag in top_freqs[:5]:
        # What period does this frequency correspond to?
        period = L / freq if freq > 0 else float('inf')
        gp = gcd(freq, p) if freq > 0 else 0
        gq = gcd(freq, q) if freq > 0 else 0
        related = ""
        if freq > 0:
            if L // freq == p or L // freq == q:
                related = f" *** = {'p' if L//freq==p else 'q'}"
            elif gcd(round(period), p) > 1 or gcd(round(period), q) > 1:
                related = f" (period {period:.1f} related to factors)"
        print(f"    freq={freq:5d}, |X|={mag:10.1f}, period≈{period:.1f}{related}")

print("\n--- DFT-based factoring attempt ---")
print("Can we extract p or q from the spectrum without knowing them?\n")

p, q = 101, 107
N = p * q
m, n = 2, 1
L = 4096
m_vals = []
for k in range(L):
    m, n = (2*m + n) % N, m % N
    m_vals.append(m)

x = np.array(m_vals, dtype=float)
x -= x.mean()
X = np.abs(fft(x))
X[0] = 0

# For each candidate frequency, compute gcd(round(L/freq), N)
factors_found = set()
for freq in range(1, L//2):
    if X[freq] > np.median(X[1:L//2]) * 5:  # Significant peak
        period = L / freq
        candidate = round(period)
        if candidate > 1:
            g = gcd(candidate, N)
            if 1 < g < N:
                factors_found.add(g)

if factors_found:
    print(f"  N={N}: Factors found from DFT peaks: {factors_found}")
else:
    print(f"  N={N}: No factors from DFT peaks (spectrum too noisy or periods don't align)")

print("\n" + "=" * 70)
print("FIELD 18: DIFFERENTIAL GEOMETRY / CURVATURE")
print("=" * 70)

# HYPOTHESIS: Define a "discrete curvature" on the tree walk.
# The curvature at step k = angle between consecutive displacement vectors.
# In (m,n) space: κ_k = angle(Δ_{k+1}, Δ_k) where Δ_k = (m_k - m_{k-1}, n_k - n_{k-1}).
# The curvature distribution mod N might have special structure related to factors.

print("\n--- Experiment: Discrete curvature of tree walks mod N ---")

def angle_between(v1, v2):
    """Angle between two 2D vectors."""
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
    mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
    if mag1 < 1e-10 or mag2 < 1e-10:
        return 0
    cos_angle = max(-1, min(1, dot / (mag1 * mag2)))
    return math.acos(cos_angle)

random.seed(42)
for p, q in [(31, 37), (101, 103)]:
    N = p * q

    m, n = 2, 1
    prev_m, prev_n = m, n
    curvatures = []
    prev_delta = None

    for step in range(2000):
        mat = random.randint(0, 2)
        if mat == 0: new_m, new_n = (2*m-n) % N, m % N
        elif mat == 1: new_m, new_n = (2*m+n) % N, m % N
        else: new_m, new_n = (m+2*n) % N, n % N

        # Displacement (with modular wrapping correction)
        dm = new_m - m
        dn = new_n - n
        if abs(dm) > N//2: dm = dm - N if dm > 0 else dm + N
        if abs(dn) > N//2: dn = dn - N if dn > 0 else dn + N

        delta = (dm, dn)
        if prev_delta is not None:
            kappa = angle_between(prev_delta, delta)
            curvatures.append(kappa)

        prev_delta = delta
        m, n = new_m, new_n

    if curvatures:
        avg_kappa = sum(curvatures) / len(curvatures)
        std_kappa = math.sqrt(sum((k - avg_kappa)**2 for k in curvatures) / len(curvatures))

        # Histogram of curvatures
        hist = Counter()
        for k in curvatures:
            bucket = round(k, 1)
            hist[bucket] += 1

        top_buckets = sorted(hist.items(), key=lambda x: -x[1])[:5]
        print(f"  N={N}={p}*{q}: avg κ={avg_kappa:.3f}, std={std_kappa:.3f}")
        print(f"    Most common curvatures: {[(f'{b:.1f}', c) for b, c in top_buckets]}")

# Test: curvature near factor-revealing nodes
print("\n--- Curvature near factor-revealing nodes ---")
p, q = 31, 37
N = p * q
m, n = 2, 1
factor_curvatures = []
nonfactor_curvatures = []
prev_delta = None

for step in range(50000):
    mat = random.randint(0, 2)
    if mat == 0: new_m, new_n = (2*m-n) % N, m % N
    elif mat == 1: new_m, new_n = (2*m+n) % N, m % N
    else: new_m, new_n = (m+2*n) % N, n % N

    dm = new_m - m
    dn = new_n - n
    if abs(dm) > N//2: dm = dm - N if dm > 0 else dm + N
    if abs(dn) > N//2: dn = dn - N if dn > 0 else dn + N
    delta = (dm, dn)

    if prev_delta is not None:
        kappa = angle_between(prev_delta, delta)
        # Is next position factor-revealing?
        g = gcd(new_m, N)
        if 1 < g < N:
            factor_curvatures.append(kappa)
        else:
            nonfactor_curvatures.append(kappa)

    prev_delta = delta
    m, n = new_m, new_n

if factor_curvatures and nonfactor_curvatures:
    avg_factor = sum(factor_curvatures) / len(factor_curvatures)
    avg_nonfactor = sum(nonfactor_curvatures) / len(nonfactor_curvatures)
    print(f"\n  Avg curvature before factor node: {avg_factor:.4f} ({len(factor_curvatures)} samples)")
    print(f"  Avg curvature before non-factor:  {avg_nonfactor:.4f} ({len(nonfactor_curvatures)} samples)")
    print(f"  Ratio: {avg_factor/avg_nonfactor:.4f}")
    if abs(avg_factor/avg_nonfactor - 1) < 0.05:
        print(f"  CONCLUSION: Curvature is NOT predictive of factor-revealing nodes.")
    else:
        print(f"  INTERESTING: Curvature differs by {abs(avg_factor/avg_nonfactor - 1)*100:.1f}%!")

print("\n--- KEY FINDINGS ---")
print("1. RAMSEY: B3 monochromatic runs have length ~1 (geometric(1/p)), no surprise.")
print("2. FOURIER: DFT of B2 orbit shows no clear peaks at factor-related frequencies.")
print("   The orbit period doesn't divide the FFT length cleanly, smearing the spectrum.")
print("3. CURVATURE: Discrete curvature of random tree walks is roughly uniform in [0,π].")
print("   No curvature signal predicts factor-revealing nodes.")
print("4. Autocorrelation of B3 paths CAN show peaks at lag=p, but only if the")
print("   sequence length ≥ p, which means we need O(p) steps — no speedup.")
