# v26 Lossless Compression Frontier Results
## Summary
8 approaches tested on 15 data types (10,000 float64 values = 80,000 bytes raw).
All approaches are **fully lossless** — verified by round-trip decompression.

## Winners by Data Type
| Data Type | Best Approach | Ratio | vs zlib-9 |
|-----------|---------------|-------|----------|
| stock | 2. BT+XOR+zlib | 1.489x | 1.19x |
| gps | 1. BT+zlib | 1.702x | 1.17x |
| temp | 6. Nibble+zlib | 1.238x | 1.16x |
| audio | 1. BT+zlib | 3.127x | 1.58x |
| pixels | 1. BT+zlib | 5.985x | 1.24x |
| near_rational | 3. BT+BWT+MTF+zlib | 4.115x | 1.09x |
| sine | 6. Nibble+zlib | 1.401x | 1.21x |
| random_walk | 2. BT+XOR+zlib | 17.917x | 1.27x |
| step | 1. BT+zlib | 1.272x | 1.15x |
| exp_bursts | zlib-9 (baseline) | 112.360x | 1.00x |
| chirp | 1. BT+zlib | 1.235x | 1.18x |
| sawtooth | 6. Nibble+zlib | 6.315x | 4.19x |
| gaussian | 1. BT+zlib | 1.115x | 1.07x |
| uniform | 1. BT+zlib | 1.166x | 1.10x |
| cauchy | 1. BT+zlib | 1.092x | 1.06x |

## Average Ratio by Approach
| Approach | Avg Ratio | Median | Min | Max | Wins |
|----------|-----------|--------|-----|-----|------|
| zlib-9 (baseline) | 9.916x | 1.252x | 1.030x | 112.360x | 1 |
| 4. IEEE754 split | 8.092x | 1.258x | 0.971x | 88.692x | 0 |
| 1. BT+zlib | 6.499x | 1.321x | 1.092x | 54.795x | 8 |
| 3. BT+BWT+MTF+zlib | 6.382x | 1.475x | 1.085x | 52.910x | 1 |
| 2. BT+XOR+zlib | 5.990x | 1.351x | 1.085x | 46.003x | 2 |
| 5. Predict+BT+zlib | 5.990x | 1.351x | 1.085x | 46.003x | 0 |
| 6. Nibble+zlib | 5.701x | 1.401x | 1.064x | 42.804x | 3 |
| 7. Bitplane | 3.344x | 1.310x | 0.995x | 16.967x | 0 |
| 8. Sort+BT+zlib | 1.825x | 1.150x | 0.933x | 5.214x | 0 |

## Full Results Matrix (compression ratio)
| Data Type | zlib-9 (baselin | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|---|
| stock | 1.25 | 1.47 | **1.49** | 1.48 | 1.26 | 1.49 | 1.48 | 1.44 | 1.15 |
| gps | 1.45 | **1.70** | 1.69 | 1.69 | 1.44 | 1.69 | 1.69 | 1.69 | 1.34 |
| temp | 1.07 | 1.23 | 1.24 | 1.22 | 1.09 | 1.24 | **1.24** | 1.23 | 0.99 |
| audio | 1.98 | **3.13** | 3.09 | 2.37 | 1.88 | 3.09 | 2.71 | 1.39 | 1.59 |
| pixels | 4.82 | **5.99** | 5.51 | 5.78 | 4.35 | 5.51 | 5.93 | 5.80 | 3.18 |
| near_rational | 3.78 | 1.28 | 1.17 | **4.11** | 1.62 | 1.17 | 1.16 | 1.15 | 2.23 |
| sine | 1.16 | 1.32 | 1.35 | 1.30 | 1.22 | 1.35 | **1.40** | 1.31 | 1.04 |
| random_walk | 14.08 | 17.40 | **17.92** | 17.39 | 13.25 | 17.92 | 14.98 | 10.27 | 3.93 |
| step | 1.11 | **1.27** | 1.27 | 1.27 | 1.10 | 1.27 | 1.26 | 1.24 | 1.06 |
| exp_bursts | **112.36** | 54.79 | 46.00 | 52.91 | 88.69 | 46.00 | 42.80 | 16.97 | 5.21 |
| chirp | 1.05 | **1.23** | 1.23 | 1.20 | 1.06 | 1.23 | 1.23 | 1.17 | 0.96 |
| sawtooth | 1.51 | 3.30 | 4.56 | 1.68 | 1.45 | 4.56 | **6.32** | 3.28 | 1.84 |
| gaussian | 1.04 | **1.12** | 1.11 | 1.11 | 0.98 | 1.11 | 1.10 | 1.07 | 0.94 |
| uniform | 1.06 | **1.17** | 1.16 | 1.16 | 1.01 | 1.16 | 1.16 | 1.15 | 0.97 |
| cauchy | 1.03 | **1.09** | 1.09 | 1.09 | 0.97 | 1.09 | 1.06 | 0.99 | 0.93 |

## Timing (ms per encode+decode+verify)
| Data Type | zlib-9 (baselin | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|---|
| stock | 4 | 1 | 14 | 46 | 24 | 4 | 22 | 129 | 6 |
| gps | 26 | 1 | 13 | 41 | 33 | 3 | 20 | 142 | 10 |
| temp | 2 | 1 | 13 | 55 | 6 | 5 | 20 | 125 | 9 |
| audio | 1 | 1 | 14 | 52 | 4 | 2 | 20 | 128 | 10 |
| pixels | 40 | 5 | 21 | 22 | 42 | 5 | 19 | 141 | 10 |
| near_rational | 4 | 1 | 15 | 38 | 8 | 3 | 21 | 131 | 12 |
| sine | 2 | 2 | 13 | 55 | 6 | 4 | 23 | 132 | 6 |
| random_walk | 9 | 2 | 17 | 26 | 18 | 5 | 20 | 145 | 5 |
| step | 2 | 2 | 14 | 53 | 6 | 4 | 20 | 125 | 7 |
| exp_bursts | 1 | 4 | 15 | 18 | 3 | 5 | 24 | 127 | 5 |
| chirp | 2 | 2 | 13 | 54 | 5 | 3 | 22 | 124 | 9 |
| sawtooth | 2 | 1 | 13 | 54 | 12 | 3 | 18 | 124 | 8 |
| gaussian | 2 | 8 | 18 | 56 | 7 | 8 | 29 | 138 | 9 |
| uniform | 3 | 1 | 13 | 59 | 8 | 3 | 20 | 134 | 9 |
| cauchy | 2 | 3 | 14 | 66 | 8 | 5 | 29 | 143 | 10 |

## Key Findings

**Note**: Average ratio is skewed by exp_bursts (mostly zeros, 112x zlib). Median ratio is more representative.

1. **Best median ratio**: BT+BWT+MTF+zlib (1.475x median) and BT+XOR+zlib / Predict+BT (1.351x median)
2. **Most consistent winner**: BT+zlib wins 8/15 data types — the safest default
3. **Nibble transpose is the surprise star**: Wins 3 types including sawtooth (6.32x, 4.19x over zlib!) and sine (1.40x). Finer 4-bit granularity captures structure that 8-bit byte planes miss.
4. **BT+XOR+zlib = best on correlated data**: stock (1.49x), random_walk (17.92x), sawtooth (4.56x). XOR delta removes byte-plane correlation.
5. **BWT+MTF dominates near-rational**: 4.11x vs zlib's 3.78x. BWT excels when byte patterns repeat in sorted context. Only approach to beat zlib on near_rational.
6. **IEEE754 split underperforms**: Splitting sign/exponent/mantissa is worse than byte transpose in 14/15 cases. The mantissa XOR-deltas don't compress as well as hoped.
7. **Bitplane coding too fine**: 64 bit-planes have too much overhead (per-plane zlib headers). Worse than byte transpose everywhere.
8. **Sort+BT always loses**: Permutation storage cost exceeds the sorting benefit. Net negative on 4 data types.
9. **exp_bursts: zlib wins outright (112x)**: Sparse data is already ideal for LZ77. All transforms add overhead.
10. **Speed**: BT+zlib is fastest (1-8ms). Nibble is 20ms. BWT+MTF is 40-66ms. Bitplane is 125-145ms.

## Recommendations for Auto-Selector

| Data Pattern | Best Approach | Expected Gain vs zlib |
|---|---|---|
| Sparse/mostly-zero | Plain zlib-9 | 1.0x (already optimal) |
| Smooth/periodic (sine, chirp, audio) | Nibble+zlib or BT+zlib | 1.2-1.6x |
| Correlated walk (stock, random_walk) | BT+XOR+zlib | 1.2-1.3x |
| Quantized (pixels, near_rational) | BT+BWT+MTF+zlib or BT+zlib | 1.1-1.2x |
| Sawtooth/ramp | Nibble+zlib | 4.2x (!!) |
| Random (gaussian, uniform, cauchy) | BT+zlib | 1.06-1.10x |

**New state of the art**: Nibble transpose on sawtooth achieves 6.32x (vs prior 3.30x from BT+zlib).
BT+XOR+zlib on random_walk achieves 17.92x (vs prior 17.40x from BT+zlib).
Overall auto-selector using best-per-type: **median 1.49x** vs zlib's median 1.25x = **1.19x improvement**.
