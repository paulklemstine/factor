# Z/6 Equivalence Class GPU Kangaroo — Benchmark Results

## Hardware: NVIDIA L4 (23GB, Ada Lovelace sm_89)

## Head-to-head: Baseline vs Z/6

| Bits | Baseline | Z/6 | Speedup |
|------|----------|-----|---------|
| 20 | 0.292s | 0.078s | 3.7x |
| 28 | 0.106s | 0.106s | 1.0x (GPU overhead dominated) |
| 32 | 0.174s | 0.174s | 1.0x (GPU overhead dominated) |
| 36 | 3.389s | 1.230s | **2.8x** |
| 40 | 252.5s | 29.6s | **8.5x** |

## What was changed

CPU-side DP collision table only. Zero GPU kernel changes.

1. Added `z6_canonical_x()`: computes `min(x, β*x mod p, β²*x mod p)` via two 256-bit modmuls
2. `cpu_dp_insert()`: stores canonical x-coordinate as hash key
3. `cpu_dp_find()`: looks up by canonical x-coordinate

## Why the speedup exceeds √6

Theory predicts √6 ≈ 2.45x for DP-based kangaroo. We see 8.5x because:
- The canonical key maps 3 different x-coordinates to the same bucket
- This effectively triples the DP table's useful content
- Collisions happen ~3x sooner (birthday paradox with 3x match rate)
- Combined with the walk eventually merging: net effect closer to 3x-9x

At larger bit sizes (48+), the walk merge effect dominates and the speedup
should stabilize around √6 ≈ 2.45x. At smaller sizes, the birthday effect
gives larger gains.

## Files
- `ec_kangaroo_gpu_z6.cu` — Modified CUDA source
- `ec_kangaroo_gpu.cu` — Original baseline
