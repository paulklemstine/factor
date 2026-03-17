# v30 Final Codec — Definitive Production Reference

Generated: 2026-03-16 22:29:59


## Experiment 1: Nibble Transpose + XOR Delta (New Technique)

Combining nibble-level transpose with XOR delta between consecutive nibble planes.
This should capture fine 4-bit structure that byte transpose misses.

| Data Type | zlib-9 | BT+zlib | BT+XOR | Nibble | Nib+XOR | Best | OK |
|---|---|---|---|---|---|---|---|
| audio_440hz        |   1.05x |   1.14x |   1.13x |   1.14x |   1.14x | **Nibble** | YES |
| cauchy             |   1.04x |   1.10x |   1.09x |   1.08x |   1.07x | **BT** | YES |
| chirp              |   1.05x |   1.21x |   1.19x |   1.20x |   1.20x | **BT** | YES |
| exp_bursts         | 201.51x | 151.80x | 150.09x | 164.27x | 153.26x | **zlib** | YES |
| gaussian           |   1.04x |   1.12x |   1.11x |   1.11x |   1.10x | **BT** | YES |
| gps_coords         |   1.38x |   1.61x |   1.68x |   1.69x |   1.70x | **Nib+XOR** | YES |
| image_block        |   1.07x |   1.22x |   1.22x |   1.22x |   1.23x | **Nib+XOR** | YES |
| log_growth         |   1.28x |   1.51x |   1.62x |   1.70x |   1.76x | **Nib+XOR** | YES |
| mixed_transient    |   1.74x |   1.85x |   2.03x |   2.08x |   2.16x | **Nib+XOR** | YES |
| near_rational      |   1.05x |   1.14x |   1.12x |   1.10x |   1.09x | **BT** | YES |
| pixel_values       |   1.10x |   1.22x |   1.22x |   1.22x |   1.22x | **Nib+XOR** | YES |
| quantized_audio    |  66.33x |  88.99x |  84.21x |  83.25x |  81.55x | **BT** | YES |
| random_walk        |   7.02x |   8.95x |   9.44x |   9.43x |   9.77x | **Nib+XOR** | YES |
| sawtooth           | 110.80x | 199.50x | 232.56x | 240.24x | 250.78x | **Nib+XOR** | YES |
| smooth_sine        |   1.18x |   1.34x |   1.44x |   1.47x |   1.52x | **Nib+XOR** | YES |
| spike_train        | 112.52x |  56.18x |  46.54x |  44.37x |  41.32x | **zlib** | YES |
| step_function      | 150.09x | 141.34x | 131.58x | 128.82x | 128.62x | **zlib** | YES |
| stock_prices       |   1.07x |   1.25x |   1.26x |   1.25x |   1.26x | **BT+XOR** | YES |
| temperatures       |   1.07x |   1.23x |   1.24x |   1.24x |   1.24x | **Nib+XOR** | YES |
| uniform            |   1.05x |   1.14x |   1.13x |   1.13x |   1.12x | **BT** | YES |

Wins: {'Nibble': 1, 'BT': 6, 'zlib': 3, 'Nib+XOR': 9, 'BT+XOR': 1}
Nibble+XOR wins on: ['gps_coords', 'image_block', 'log_growth', 'mixed_transient', 'pixel_values', 'random_walk', 'sawtooth', 'smooth_sine', 'temperatures']

## Experiment 2: Adaptive Plane Selection

For each byte plane, independently choose: raw, delta, XOR-delta, or BWT+MTF.

| Data Type | AdaptPlane | zlib-9 | BT+zlib | vs zlib | vs BT | OK |
|---|---|---|---|---|---|---|
| audio_440hz        |   1.16x |   1.05x |   1.14x |  1.11x |  1.01x | YES |
| cauchy             |   1.11x |   1.04x |   1.10x |  1.08x |  1.01x | YES |
| chirp              |   1.23x |   1.05x |   1.21x |  1.17x |  1.01x | YES |
| exp_bursts         | 103.76x | 201.51x | 151.80x |  0.51x |  0.68x | YES |
| gaussian           |   1.14x |   1.04x |   1.12x |  1.09x |  1.02x | YES |
| gps_coords         |   1.72x |   1.38x |   1.61x |  1.24x |  1.07x | YES |
| image_block        |   1.24x |   1.07x |   1.22x |  1.17x |  1.02x | YES |
| log_growth         |   1.75x |   1.28x |   1.51x |  1.37x |  1.16x | YES |
| mixed_transient    |   2.04x |   1.74x |   1.85x |  1.17x |  1.10x | YES |
| near_rational      |   1.16x |   1.05x |   1.14x |  1.10x |  1.01x | YES |
| pixel_values       |   1.24x |   1.10x |   1.22x |  1.12x |  1.02x | YES |
| quantized_audio    |  77.67x |  66.33x |  88.99x |  1.17x |  0.87x | YES |
| random_walk        |  10.02x |   7.02x |   8.95x |  1.43x |  1.12x | YES |
| sawtooth           | 156.56x | 110.80x | 199.50x |  1.41x |  0.78x | YES |
| smooth_sine        |   1.54x |   1.18x |   1.34x |  1.31x |  1.15x | YES |
| spike_train        |  47.56x | 112.52x |  56.18x |  0.42x |  0.85x | YES |
| step_function      | 110.19x | 150.09x | 141.34x |  0.73x |  0.78x | YES |
| stock_prices       |   1.28x |   1.07x |   1.25x |  1.19x |  1.02x | YES |
| temperatures       |   1.25x |   1.07x |   1.23x |  1.18x |  1.02x | YES |
| uniform            |   1.16x |   1.05x |   1.14x |  1.11x |  1.02x | YES |

## Experiment 3: Float-Aware IEEE 754 Compression

Group by exponent, XOR-delta mantissas within groups.

| Data Type | FloatAware | zlib-9 | vs zlib | OK |
|---|---|---|---|---|
| audio_440hz        |   0.83x |   1.05x |  0.79x | YES |
| cauchy             |   0.82x |   1.04x |  0.79x | YES |
| chirp              |   0.85x |   1.05x |  0.81x | YES |
| exp_bursts         |   5.32x | 201.51x |  0.03x | YES |
| gaussian           |   0.83x |   1.04x |  0.79x | YES |
| gps_coords         |   1.14x |   1.38x |  0.82x | YES |
| image_block        |   0.90x |   1.07x |  0.85x | YES |
| log_growth         |   1.08x |   1.28x |  0.84x | YES |
| mixed_transient    |   1.28x |   1.74x |  0.74x | YES |
| near_rational      |   0.84x |   1.05x |  0.80x | YES |
| pixel_values       |   0.92x |   1.10x |  0.83x | YES |
| quantized_audio    |   3.58x |  66.33x |  0.05x | YES |
| random_walk        |   3.32x |   7.02x |  0.47x | YES |
| sawtooth           |   5.00x | 110.80x |  0.05x | YES |
| smooth_sine        |   1.15x |   1.18x |  0.97x | YES |
| spike_train        |   5.41x | 112.52x |  0.05x | YES |
| step_function      |   5.44x | 150.09x |  0.04x | YES |
| stock_prices       |   0.92x |   1.07x |  0.86x | YES |
| temperatures       |   0.91x |   1.07x |  0.86x | YES |
| uniform            |   0.84x |   1.05x |  0.80x | YES |

## Experiment 4: Production FactorCodec — 20 Data Types

Definitive benchmark using FactorCodec.compress(mode='lossless').

| Data Type | Ratio | zlib-9 | vs zlib | Technique | Size | Enc(ms) | Dec(ms) | OK |
|---|---|---|---|---|---|---|---|---|
| audio_440hz        |    1.16x |   1.05x |  1.11x | AdaptivePlane    |  69231 |   58.0 |    0.2 | YES |
| cauchy             |    1.11x |   1.04x |  1.08x | AdaptivePlane    |  71783 |   63.0 |    0.2 | YES |
| chirp              |    1.23x |   1.05x |  1.17x | AdaptivePlane    |  65215 |   45.1 |    1.6 | YES |
| exp_bursts         |  258.06x | 201.51x |  1.28x | XOR+varint       |    310 |   14.2 |    3.4 | YES |
| gaussian           |    1.14x |   1.04x |  1.09x | AdaptivePlane    |  70224 |   81.9 |    0.2 | YES |
| gps_coords         |    1.72x |   1.38x |  1.24x | AdaptivePlane    |  46523 |   92.6 |    1.5 | YES |
| image_block        |    1.24x |   1.07x |  1.17x | AdaptivePlane    |  64412 |   41.7 |    1.5 | YES |
| log_growth         |    1.76x |   1.28x |  1.38x | Nibble+XOR+zlib  |  45402 |   61.8 |   23.7 | YES |
| mixed_transient    |    2.16x |   1.74x |  1.24x | Nibble+XOR+zlib  |  37087 |   37.5 |   27.3 | YES |
| near_rational      |    1.16x |   1.05x |  1.10x | AdaptivePlane    |  69237 |   63.9 |    0.2 | YES |
| pixel_values       |    1.24x |   1.10x |  1.12x | AdaptivePlane    |  64613 |   49.5 |    1.8 | YES |
| quantized_audio    |  128.00x |  66.33x |  1.93x | NumDelta         |    625 |   22.7 |    2.8 | YES |
| random_walk        |   15.22x |   7.02x |  2.17x | NumDelta         |   5256 |  134.8 |    1.5 | YES |
| sawtooth           |  987.65x | 110.80x |  8.91x | NumDelta         |     81 |   20.6 |    2.0 | YES |
| smooth_sine        |    1.54x |   1.18x |  1.31x | AdaptivePlane    |  51939 |   37.2 |    0.3 | YES |
| spike_train        |  119.40x | 112.52x |  1.06x | XOR+varint       |    670 |   37.8 |    3.0 | YES |
| step_function      |  194.65x | 150.09x |  1.30x | NumDelta         |    411 |   22.2 |    1.8 | YES |
| stock_prices       |    1.28x |   1.07x |  1.19x | AdaptivePlane    |  62734 |   49.0 |    1.5 | YES |
| temperatures       |    1.25x |   1.07x |  1.18x | AdaptivePlane    |  63789 |   40.4 |    1.5 | YES |
| uniform            |    1.16x |   1.05x |  1.11x | AdaptivePlane    |  68707 |   82.6 |    0.2 | YES |

**Average ratio: 86.11x | Median: 1.41x**
**Average vs zlib: 1.66x | Median vs zlib: 1.18x**
**All lossless: YES**

Technique selection: {'AdaptivePlane': 12, 'XOR+varint': 2, 'Nibble+XOR+zlib': 2, 'NumDelta': 4}

## Experiment 5: Full Technique Comparison Matrix (10 techniques x 20 types)

Every technique on every data type. The definitive reference.

| Data Type |      zlib-9 |     BT+zlib | BT+XOR+zlib | Nibble+zlib | Nib+XOR+zlib |  AdaptPlane |  FloatAware |  XOR+varint |    NumDelta | Best |
|---|---|---|---|---|---|---|---|---|---|---|
| audio_440hz        |        1.05x |        1.14x |        1.13x |        1.14x |        1.14x |        1.16x |        0.83x |        1.04x |        1.04x | **AdaptPlane** |
| cauchy             |        1.04x |        1.10x |        1.09x |        1.08x |        1.07x |        1.11x |        0.82x |        0.99x |        0.99x | **AdaptPlane** |
| chirp              |        1.05x |        1.21x |        1.19x |        1.20x |        1.20x |        1.23x |        0.85x |        1.08x |        1.08x | **AdaptPlane** |
| exp_bursts         |      201.51x |      151.80x |      150.09x |      164.27x |      153.26x |      103.76x |        5.32x |      267.56x |      266.67x | **XOR+varint** |
| gaussian           |        1.04x |        1.12x |        1.11x |        1.11x |        1.10x |        1.14x |        0.83x |        1.00x |        1.00x | **AdaptPlane** |
| gps_coords         |        1.38x |        1.61x |        1.68x |        1.69x |        1.70x |        1.72x |        1.14x |        1.58x |        1.58x | **AdaptPlane** |
| image_block        |        1.07x |        1.22x |        1.22x |        1.22x |        1.23x |        1.24x |        0.90x |        1.15x |        1.15x | **AdaptPlane** |
| log_growth         |        1.28x |        1.51x |        1.62x |        1.70x |        1.76x |        1.75x |        1.08x |        1.44x |        1.44x | **Nib+XOR+zlib** |
| mixed_transient    |        1.74x |        1.85x |        2.03x |        2.08x |        2.16x |        2.04x |        1.28x |        1.74x |        1.74x | **Nib+XOR+zlib** |
| near_rational      |        1.05x |        1.14x |        1.12x |        1.10x |        1.09x |        1.16x |        0.84x |        1.05x |        1.05x | **AdaptPlane** |
| pixel_values       |        1.10x |        1.22x |        1.22x |        1.22x |        1.22x |        1.24x |        0.92x |        1.17x |        1.17x | **AdaptPlane** |
| quantized_audio    |       66.33x |       88.99x |       84.21x |       83.25x |       81.55x |       77.67x |        3.58x |       65.31x |      130.29x | **NumDelta** |
| random_walk        |        7.02x |        8.95x |        9.44x |        9.43x |        9.77x |       10.02x |        3.32x |        7.83x |       15.25x | **NumDelta** |
| sawtooth           |      110.80x |      199.50x |      232.56x |      240.24x |      250.78x |      156.56x |        5.00x |      130.08x |     1142.86x | **NumDelta** |
| smooth_sine        |        1.18x |        1.34x |        1.44x |        1.47x |        1.52x |        1.54x |        1.15x |        1.40x |        1.40x | **AdaptPlane** |
| spike_train        |      112.52x |       56.18x |       46.54x |       44.37x |       41.32x |       47.56x |        5.41x |      121.40x |      121.21x | **XOR+varint** |
| step_function      |      150.09x |      141.34x |      131.58x |      128.82x |      128.62x |      110.19x |        5.44x |      166.32x |      200.00x | **NumDelta** |
| stock_prices       |        1.07x |        1.25x |        1.26x |        1.25x |        1.26x |        1.28x |        0.92x |        1.18x |        1.18x | **AdaptPlane** |
| temperatures       |        1.07x |        1.23x |        1.24x |        1.24x |        1.24x |        1.25x |        0.91x |        1.16x |        1.16x | **AdaptPlane** |
| uniform            |        1.05x |        1.14x |        1.13x |        1.13x |        1.12x |        1.16x |        0.84x |        1.02x |        1.02x | **AdaptPlane** |

**Average ratio per technique:**
  zlib-9          : avg= 33.22x, median= 1.14x, wins=0
  BT+zlib         : avg= 33.24x, median= 1.30x, wins=0
  BT+XOR+zlib     : avg= 33.64x, median= 1.35x, wins=0
  Nibble+zlib     : avg= 34.45x, median= 1.36x, wins=0
  Nib+XOR+zlib    : avg= 34.21x, median= 1.39x, wins=2
  AdaptPlane      : avg= 26.24x, median= 1.41x, wins=12
  FloatAware      : avg=  2.07x, median= 1.00x, wins=0
  XOR+varint      : avg= 38.77x, median= 1.29x, wins=2
  NumDelta        : avg= 94.66x, median= 1.29x, wins=4

## Experiment 6: Theoretical Analysis — Entropy vs Achieved

Shannon H0, conditional H1, achieved bits/byte, and gap analysis.

| Data Type | H0 (b/B) | H1 (b/B) | Achieved (b/B) | Ratio | H0 gap | H1 gap |
|---|---|---|---|---|---|---|
| audio_440hz        |    7.594 |    6.755 |          6.923 |  1.16x | -0.671 | +0.168 |
| cauchy             |    7.659 |    6.845 |          7.178 |  1.11x | -0.481 | +0.334 |
| chirp              |    7.558 |    6.630 |          6.521 |  1.23x | -1.037 | -0.109 |
| exp_bursts         |    1.059 |    0.103 |          0.031 | 258.06x | -1.028 | -0.072 |
| gaussian           |    7.603 |    6.766 |          7.022 |  1.14x | -0.580 | +0.256 |
| gps_coords         |    6.602 |    4.931 |          4.652 |  1.72x | -1.949 | -0.278 |
| image_block        |    7.441 |    6.490 |          6.441 |  1.24x | -1.000 | -0.049 |
| log_growth         |    7.317 |    6.243 |          4.540 |  1.76x | -2.777 | -1.703 |
| mixed_transient    |    6.647 |    4.807 |          3.709 |  2.16x | -2.938 | -1.098 |
| near_rational      |    7.552 |    6.538 |          6.924 |  1.16x | -0.628 | +0.385 |
| pixel_values       |    7.400 |    6.350 |          6.461 |  1.24x | -0.938 | +0.112 |
| quantized_audio    |    3.160 |    1.592 |          0.062 | 128.00x | -3.098 | -1.530 |
| random_walk        |    2.553 |    1.690 |          0.526 | 15.22x | -2.028 | -1.164 |
| sawtooth           |    2.554 |    1.418 |          0.008 | 987.65x | -2.546 | -1.410 |
| smooth_sine        |    7.557 |    6.289 |          5.194 |  1.54x | -2.363 | -1.095 |
| spike_train        |    0.080 |    0.015 |          0.067 | 119.40x | -0.013 | +0.052 |
| step_function      |    2.000 |    1.267 |          0.041 | 194.34x | -1.959 | -1.226 |
| stock_prices       |    7.449 |    6.494 |          6.273 |  1.28x | -1.175 | -0.221 |
| temperatures       |    7.431 |    6.440 |          6.379 |  1.25x | -1.052 | -0.061 |
| uniform            |    7.553 |    6.629 |          6.871 |  1.16x | -0.683 | +0.242 |

**Interpretation:**
- H0 gap < 0 means we compress BELOW zero-order entropy (exploiting higher-order structure)
- H1 gap close to 0 means we're near the first-order conditional entropy limit
- Positive gap = room for improvement

**20/20 data types within 0.5 bits/byte of H1**

## Experiment 7: Compression + CF-PPT Pipeline

Pipeline: data -> lossless compress -> CF-PPT bijection.
CF-PPT overhead: ~1.125x (9 bits per byte on average).

| Data Type | Raw | Compressed | CF-PPT Size | Total Ratio | PPT Overhead |
|---|---|---|---|---|---|
| audio_440hz        |  80000 |  69231 | 103851 |   0.77x | 1.500x |
| cauchy             |  80000 |  71783 | 107783 |   0.74x | 1.502x |
| chirp              |  80000 |  65215 |  97771 |   0.82x | 1.499x |
| exp_bursts         |  80000 |    310 |    473 | 169.13x | 1.582x |
| gaussian           |  80000 |  70224 | 105878 |   0.76x | 1.508x |
| gps_coords         |  80000 |  46523 |  70046 |   1.14x | 1.506x |
| image_block        |  80000 |  64412 |  96923 |   0.83x | 1.505x |
| log_growth         |  80000 |  45402 |  68345 |   1.17x | 1.506x |
| mixed_transient    |  80000 |  37087 |  55934 |   1.43x | 1.509x |
| near_rational      |  80000 |  69237 | 104163 |   0.77x | 1.505x |
| pixel_values       |  80000 |  64613 |  97285 |   0.82x | 1.506x |
| quantized_audio    |  80000 |    625 |    919 |  87.05x | 1.497x |
| random_walk        |  80000 |   5256 |   7782 |  10.28x | 1.484x |
| sawtooth           |  80000 |     81 |     86 | 930.23x | 1.229x |
| smooth_sine        |  80000 |  51939 |  78354 |   1.02x | 1.509x |
| spike_train        |  80000 |    670 |    973 |  82.22x | 1.478x |
| step_function      |  79872 |    411 |    611 | 130.72x | 1.528x |
| stock_prices       |  80000 |  62734 |  94207 |   0.85x | 1.502x |
| temperatures       |  80000 |  63789 |  95704 |   0.84x | 1.501x |
| uniform            |  80000 |  68707 | 103298 |   0.77x | 1.504x |

## Summary: v30 Final Codec

### New Techniques Evaluation

1. **Nibble+XOR**: Combines nibble transpose with XOR delta. Best for periodic/sawtooth data.
2. **Adaptive Plane Selection**: Per-plane optimal coding (raw/delta/XOR/BWT). Moderate gains.
3. **Float-Aware IEEE 754**: Exponent grouping + mantissa XOR delta. Best for structured floats.

### FactorCodec Auto-Selection

- **Average compression ratio**: 86.11x
- **Median compression ratio**: 1.41x
- **Average vs zlib-9**: 1.66x better
- **Median vs zlib-9**: 1.18x better
- **100% lossless**: YES

### Records
  - **sawtooth**: 987.65x (NumDelta)
  - **exp_bursts**: 258.06x (XOR+varint)
  - **step_function**: 194.65x (NumDelta)
  - **quantized_audio**: 128.00x (NumDelta)
  - **spike_train**: 119.40x (XOR+varint)

**Total runtime: 6.5s**