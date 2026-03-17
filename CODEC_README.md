# FactorCodec v30 — Production Codec Reference

## Overview

FactorCodec is a production-grade lossless compression system for numerical (float64) data.
It auto-selects the optimal compression technique from 10 algorithms, achieving **86.11x average**
and **1.41x median** compression ratio — **1.66x better than zlib-9**.

All compression is **fully lossless** — bit-exact round-trip verified on 20 data types.

## Quick Start

```python
from v30_final_codec import FactorCodec
import numpy as np

codec = FactorCodec()

# Lossless compression (auto-selects best technique)
data = np.random.normal(0, 100, 10000)
compressed = codec.compress(data, mode='lossless')
recovered = codec.decompress(compressed)
assert np.array_equal(recovered, data)

# Lossy compression (quality: 'low', 'medium', 'high')
compressed = codec.compress(data, mode='lossy', quality='medium')

# Auto mode (currently = lossless)
compressed = codec.compress(data, mode='auto')

# CF-PPT bijection (maps compressed data to Pythagorean triples)
compressed = codec.compress(data, mode='cf_ppt')

# Convert data to Pythagorean triples directly
triples = codec.to_ppt(data)

# Analyze data (entropy, best technique, etc.)
analysis = codec.analyze(data)
print(f"Best technique: {analysis['best_name']}")
print(f"H0={analysis['H0']:.3f}, H1={analysis['H1']:.3f}, achieved={analysis['best_bps']:.3f} bits/byte")
```

## Supported Modes

| Mode | Description | Use When |
|------|-------------|----------|
| `lossless` | Bit-exact compression, auto-selects best technique | Default. Any numerical data. |
| `lossy` | Delta quantization with configurable quality | When some error is acceptable (sensor data, visualization). |
| `auto` | Currently = lossless | General purpose. |
| `cf_ppt` | Compress then map to Pythagorean triples via CF bijection | Mathematical applications, PPT representation. |

## Compression Techniques (Lossless)

| ID | Name | Best For | Speed |
|----|------|----------|-------|
| 0 | zlib-9 | Sparse/mostly-zero data | Fast |
| 1 | BT+zlib | General float64 data (default winner) | Fast |
| 2 | BT+XOR+zlib | Correlated walks (stock, GPS) | Fast |
| 3 | BT+BWT+MTF+zlib | Structured/near-rational data | Medium |
| 4 | Nibble+zlib | Periodic/sawtooth signals | Fast |
| 5 | Nibble+XOR+zlib | Fine periodic structure | Fast |
| 6 | AdaptivePlane | Mixed data types | Medium |
| 7 | FloatAware | Data with few unique exponents | Medium |
| 8 | XOR+varint | Random walks, GPS tracks | Fast |
| 9 | NumDelta | Integer-valued data (counters, steps) | Fast |

## Benchmark Results (20 Data Types, n=10,000)

| Data Type | Ratio | vs zlib | Technique |
|---|---|---|---|
| sawtooth | 987.65x | 8.91x | NumDelta |
| exp_bursts | 258.06x | 1.28x | XOR+varint |
| step_function | 194.65x | 1.30x | NumDelta |
| quantized_audio | 128.00x | 1.93x | NumDelta |
| spike_train | 119.40x | 1.06x | XOR+varint |
| random_walk | 15.22x | 2.17x | NumDelta |
| mixed_transient | 2.16x | 1.24x | Nibble+XOR+zlib |
| log_growth | 1.76x | 1.38x | Nibble+XOR+zlib |
| gps_coords | 1.72x | 1.24x | AdaptivePlane |
| smooth_sine | 1.54x | 1.31x | AdaptivePlane |
| stock_prices | 1.28x | 1.19x | AdaptivePlane |
| temperatures | 1.25x | 1.18x | AdaptivePlane |
| image_block | 1.24x | 1.17x | AdaptivePlane |
| pixel_values | 1.24x | 1.12x | AdaptivePlane |
| chirp | 1.23x | 1.17x | AdaptivePlane |
| uniform | 1.16x | 1.11x | AdaptivePlane |
| audio_440hz | 1.16x | 1.11x | AdaptivePlane |
| near_rational | 1.16x | 1.10x | AdaptivePlane |
| gaussian | 1.14x | 1.09x | AdaptivePlane |
| cauchy | 1.11x | 1.08x | AdaptivePlane |

**Average: 86.11x | Median: 1.41x | vs zlib: 1.66x**

## Theoretical Analysis

For each data type, we compute Shannon entropy H0 (memoryless), conditional entropy H1 (first-order),
and our achieved bits/byte. The gap shows where we're optimal and where improvement remains.

| Data Type | H0 (b/B) | H1 (b/B) | Achieved (b/B) | H1 gap |
|---|---|---|---|---|
| log_growth | 7.317 | 6.243 | 4.540 | -1.703 |
| quantized_audio | 3.160 | 1.592 | 0.062 | -1.530 |
| sawtooth | 2.554 | 1.418 | 0.008 | -1.410 |
| step_function | 2.000 | 1.267 | 0.041 | -1.226 |
| random_walk | 2.553 | 1.690 | 0.526 | -1.164 |
| mixed_transient | 6.647 | 4.807 | 3.709 | -1.098 |
| smooth_sine | 7.557 | 6.289 | 5.194 | -1.095 |
| gps_coords | 6.602 | 4.931 | 4.652 | -0.278 |
| stock_prices | 7.449 | 6.494 | 6.273 | -0.221 |
| chirp | 7.558 | 6.630 | 6.521 | -0.109 |
| exp_bursts | 1.059 | 0.103 | 0.031 | -0.072 |
| temperatures | 7.431 | 6.440 | 6.379 | -0.061 |
| image_block | 7.441 | 6.490 | 6.441 | -0.049 |
| spike_train | 0.080 | 0.015 | 0.067 | +0.052 |
| pixel_values | 7.400 | 6.350 | 6.461 | +0.112 |
| audio_440hz | 7.594 | 6.755 | 6.923 | +0.168 |
| uniform | 7.553 | 6.629 | 6.871 | +0.242 |
| gaussian | 7.603 | 6.766 | 7.022 | +0.256 |
| cauchy | 7.659 | 6.845 | 7.178 | +0.334 |
| near_rational | 7.552 | 6.538 | 6.924 | +0.385 |

**Negative H1 gap** means we compress below first-order conditional entropy (exploiting higher-order structure).

## CF-PPT Pipeline

The CF-PPT pipeline maps compressed data to Pythagorean triples via continued fraction bijection:
1. Compress data losslessly
2. Each compressed byte -> CF partial quotient (PQ = byte + 1)
3. PQ sequence -> Stern-Brocot tree path -> PPT address
4. Overhead: ~1.125x (9 bits per source byte average)

Total ratio = compression_ratio / 1.125

## Wire Format

```
Header (11 bytes):
  Magic: 'FC30' (4 bytes)
  Version: 30 (1 byte)
  Mode: 0=lossless, 1=lossy, 2=cf_ppt (1 byte)
  N_elements: uint32 (4 bytes)
  Technique: uint8 (1 byte)

Payload: technique-specific compressed data
```

## When to Use Each Mode

- **Time series / sensor data**: `mode='lossless'` (auto-selects BT+XOR or NumDelta)
- **Image / pixel data**: `mode='lossless'` (auto-selects BT+zlib or Nibble)
- **Mathematical data**: `mode='cf_ppt'` for PPT representation
- **Streaming / real-time**: `mode='lossy', quality='medium'` for 4-bit quantization
- **Archival**: `mode='lossless'` always

## Dependencies

- Python 3.8+
- NumPy
- zlib (stdlib)

Generated by v30_final_codec.py on {time.strftime('%Y-%m-%d')}.
