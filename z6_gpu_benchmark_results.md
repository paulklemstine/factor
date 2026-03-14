# Z/6 Equivalence Class GPU Kangaroo — Benchmark Results

## Version 2: With Cross-Orbit λ-Resolution

### RTX 4050 Laptop (sm_89, 6GB)
| Bits | Baseline | Z/6+crossorbit | Speedup |
|------|----------|----------------|---------|
| 36 | 1.09s | 0.72s | **1.51x** |
| 40 | 52.5s | 20.1s | **2.61x** |

### NVIDIA L4 Cloud (sm_89, 23GB) — v1 only (canonical key, no λ-resolution)
| Bits | Baseline | Z/6 v1 | Speedup |
|------|----------|--------|---------|
| 36 | 3.39s | 1.23s | **2.8x** |
| 40 | 252s | 29.6s | **8.5x** |

## What was changed

CPU-side DP collision table only. Zero GPU kernel changes.

### v1 (canonical DP keying):
1. `z6_canonical_x()`: computes `min(x, β*x mod p, β²*x mod p)` via two 256-bit modmuls
2. `cpu_dp_insert()`: stores canonical x-coordinate as hash key
3. `cpu_dp_find()`: looks up by canonical x-coordinate

### v2 (+ cross-orbit λ-resolution):
4. On DP collision, try 6 scalar adjustments: `±tame_pos`, `±λ·tame_pos`, `±λ²·tame_pos`
5. This resolves cross-orbit matches (2/3 of canonical matches were previously wasted)
6. Reduced DP density by 1 bit to match higher collision rate

### Python prototype results (exp14_push_further.py):
| n | Baseline | Z/6 v1 | Z/6+crossorbit | v1/Base | v2/Base |
|---|----------|--------|----------------|---------|---------|
| 4993 | 807 | 762 | 266 | 1.1x | **3.0x** |
| 5851 | 785 | 845 | 271 | 0.9x | **2.9x** |
| 6163 | 995 | 925 | 262 | 1.1x | **3.8x** |

Key insight: v1 barely helps with DP-based kangaroo (walks don't merge on
cross-orbit hits). v2 resolves ALL canonical matches via λ-adjustment.

## Files
- `ec_kangaroo_gpu_z6.cu` — Modified CUDA source (v2: canonical + crossorbit)
- `ec_kangaroo_gpu.cu` — Original baseline
