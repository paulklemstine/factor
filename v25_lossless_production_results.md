# v25 Lossless Production — Comprehensive Lossless Compression

Generated: 2026-03-16 20:30:42

# v25 Lossless Production Results

Date: 2026-03-16 20:30:40
Dataset size: 4096 float64 values (32,768 bytes raw)


## Experiment 1: PPT Wavelet Lossless Codec

Testing encode_lossless / decode_lossless API on 10 datasets:

| Dataset | Raw (B) | Encoded (B) | Ratio | Lossless? | Time (ms) |
|---------|---------|-------------|-------|-----------|-----------|
| audio_samples    |   32768 |       31380 | 1.04x | YES       |       7.4 |
| exp_bursts       |   32768 |         328 | 99.90x | YES       |       0.3 |
| gps_coords       |   32768 |       23650 | 1.39x | YES       |       7.0 |
| near_rational    |   32768 |       31150 | 1.05x | YES       |       0.7 |
| pixel_values     |   32768 |       30759 | 1.07x | YES       |       0.7 |
| random_walk      |   32768 |        4629 | 7.08x | YES       |       1.6 |
| sine_wave        |   32768 |       23147 | 1.42x | YES       |       0.6 |
| step_function    |   32768 |         768 | 42.67x | YES       |       1.5 |
| stock_prices     |   32768 |       30691 | 1.07x | YES       |       0.7 |
| temperatures     |   32768 |       30768 | 1.07x | YES       |       0.8 |

API: `encode_lossless(data) -> bytes`, `decode_lossless(bytes) -> np.array`
Falls back to raw IEEE 754 + zlib when fixed-point scaling loses precision.

## Experiment 2: PPT Wavelet + MTF Combo

PPT wavelet coefficients -> zigzag -> MTF -> zlib vs standalone:

| Dataset | Raw (B) | PPT+MTF (B) | Plain PPT (B) | zlib (B) | Best |
|---------|---------|-------------|---------------|----------|------|
| audio_samples    |   32768 |       31382 (OK) |         31387 |    31352 | zlib |
| exp_bursts       |   32768 |         323 (OK) |           328 |      293 | zlib |
| gps_coords       |   32768 |       23662 (OK) |         23667 |    23632 | zlib |
| near_rational    |   32768 |       31132 (OK) |         31137 |    31102 | zlib |
| pixel_values     |   32768 |       30441 (OK) |         30446 |    30411 | zlib |
| random_walk      |   32768 |        4287 (OK) |          4734 |     4967 | PPT+MTF |
| sine_wave        |   32768 |       23142 (OK) |         23147 |    23112 | zlib |
| step_function    |   32768 |         600 (OK) |           756 |      239 | zlib |
| stock_prices     |   32768 |       30673 (OK) |         30678 |    30643 | zlib |
| temperatures     |   32768 |       30774 (OK) |         30779 |    30744 | zlib |

## Experiment 3: IEEE 754 Plane-Separated Encoding

Separate sign/exponent/mantissa planes, compress independently:

| Dataset | Raw (B) | Planes (B) | zlib (B) | Ratio vs zlib | Lossless? |
|---------|---------|-----------|----------|---------------|-----------|
| audio_samples    |   32768 |     32573 |    31353 |          1.04 | YES       |
| exp_bursts       |   32768 |       404 |      293 |          1.38 | YES       |
| gps_coords       |   32768 |     23321 |    23562 |          0.99 | YES       |
| near_rational    |   32768 |     32715 |    31119 |          1.05 | YES       |
| pixel_values     |   32768 |     30729 |    30079 |          1.02 | YES       |
| random_walk      |   32768 |      4593 |     4708 |          0.98 | YES       |
| sine_wave        |   32768 |     21967 |    23112 |          0.95 | YES       |
| step_function    |   32768 |       403 |      243 |          1.66 | YES       |
| stock_prices     |   32768 |     29892 |    30745 |          0.97 | YES       |
| temperatures     |   32768 |     30111 |    30749 |          0.98 | YES       |

Ratio < 1.0 means planes beat zlib, > 1.0 means zlib wins.

## Experiment 4: XOR Delta for Floats

XOR consecutive IEEE 754 representations -> compress:

| Dataset | Raw (B) | XOR+zlib (B) | XOR+varint (B) | zlib (B) | Best |
|---------|---------|-------------|----------------|----------|------|
| audio_samples    |   32768 |   31267 (OK) |    31514 (OK) |    31347 | XOR     |
| exp_bursts       |   32768 |     307 (OK) |      250 (OK) |      293 | XOR+var |
| gps_coords       |   32768 |   23258 (OK) |    20750 (OK) |    23735 | XOR+var |
| near_rational    |   32768 |   31396 (OK) |    31182 (OK) |    31106 | zlib    |
| pixel_values     |   32768 |   29553 (OK) |    27956 (OK) |    29676 | XOR+var |
| random_walk      |   32768 |    4238 (OK) |     4209 (OK) |     4850 | XOR+var |
| sine_wave        |   32768 |   21822 (OK) |    20028 (OK) |    23112 | XOR+var |
| step_function    |   32768 |     310 (OK) |      242 (OK) |      238 | zlib    |
| stock_prices     |   32768 |   29753 (OK) |    27807 (OK) |    30693 | XOR+var |
| temperatures     |   32768 |   30017 (OK) |    28281 (OK) |    30744 | XOR+var |

## Experiment 5: Byte-Level Transpose (Blosc-style)

Transpose byte matrix of float64 -> compress high-order bytes together:

| Dataset | Raw (B) | Transpose (B) | zlib (B) | Ratio vs zlib | Lossless? |
|---------|---------|--------------|----------|---------------|-----------|
| audio_samples    |   32768 |        29091 |    31351 |          0.93 | YES       |
| exp_bursts       |   32768 |          366 |      293 |          1.25 | YES       |
| gps_coords       |   32768 |        20422 |    23570 |          0.87 | YES       |
| near_rational    |   32768 |        29179 |    31071 |          0.94 | YES       |
| pixel_values     |   32768 |        26632 |    29551 |          0.90 | YES       |
| random_walk      |   32768 |         3833 |     4903 |          0.78 | YES       |
| sine_wave        |   32768 |        25350 |    23112 |          1.10 | YES       |
| step_function    |   32768 |          267 |      244 |          1.09 | YES       |
| stock_prices     |   32768 |        26343 |    30684 |          0.86 | YES       |
| temperatures     |   32768 |        26894 |    30755 |          0.87 | YES       |

## Experiment 6: Comprehensive Lossless Benchmark

| Dataset | Raw |     zlib-9 |      bz2-9 |       lzma |   XOR+zlib | XOR+varint | IEEE plane | byte trans | PPT wavele |    PPT+MTF |  delta2+zz |  num delta |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| audio_samples    | 32768 |     1.05x |     1.01x |     1.05x |     1.05x |     1.04x |     1.01x |     1.13x |     1.04x |     1.04x |     1.02x |     3.75x* |
| exp_bursts       | 32768 |   111.84x |    71.86x |   109.23x |   106.74x |   131.07x |    81.11x |    89.53x |    99.90x |   101.45x |   119.16x |   364.09x* |
| gps_coords       | 32768 |     1.39x |     1.35x |     1.59x |     1.41x |     1.58x |     1.41x |     1.61x |     1.38x |     1.38x |     1.58x |     3.23x* |
| near_rational    | 32768 |     1.05x |     1.03x |     1.07x |     1.04x |     1.05x |     1.00x |     1.12x |     1.05x |     1.05x |     1.05x |     3.53x* |
| pixel_values     | 32768 |     1.08x |     1.05x |     1.15x |     1.09x |     1.15x |     1.08x |     1.19x |     1.08x |     1.08x |     1.14x |     4.02x* |
| random_walk      | 32768 |     6.82x |    11.17x |     8.60x |     7.61x |     7.65x |     7.42x |     8.69x |     7.33x |     8.04x |     7.72x |    15.18x |
| sine_wave        | 32768 |     1.42x |     1.25x |     1.77x |     1.50x |     1.64x |     1.49x |     1.29x |     1.42x |     1.42x |     1.89x |     4.78x* |
| step_function    | 32768 |   129.52x |   108.86x |    97.52x |    98.40x |   136.53x |    79.15x |   122.27x |    43.06x |    56.89x |    83.38x |   157.54x |
| stock_prices     | 32768 |     1.07x |     1.03x |     1.20x |     1.10x |     1.18x |     1.10x |     1.24x |     1.07x |     1.07x |     1.18x |     3.49x* |
| temperatures     | 32768 |     1.07x |     1.05x |     1.16x |     1.09x |     1.16x |     1.09x |     1.22x |     1.06x |     1.06x |     1.15x |     3.59x* |

**Best method per dataset:**

- **audio_samples**: byte trans (1.13x, 29086B)
- **exp_bursts**: XOR+varint (131.07x, 250B)
- **gps_coords**: byte trans (1.61x, 20325B)
- **near_rational**: byte trans (1.12x, 29218B)
- **pixel_values**: byte trans (1.19x, 27565B)
- **random_walk**: num delta (15.18x, 2158B)
- **sine_wave**: delta2+zz (1.89x, 17363B)
- **step_function**: num delta (157.54x, 208B)
- **stock_prices**: byte trans (1.24x, 26420B)
- **temperatures**: byte trans (1.22x, 26908B)

## Experiment 7: Auto-Selector

Automatic best-method selection per dataset:

| Dataset | Raw (B) | Best Method | Size (B) | Ratio | vs zlib |
|---------|---------|-------------|----------|-------|---------|
| audio_samples    |   32768 | byte_transpose |    29107 | 1.13x | 1.08x |
| exp_bursts       |   32768 | xor_varint  |      250 | 131.07x | 1.17x |
| gps_coords       |   32768 | byte_transpose |    20370 | 1.61x | 1.16x |
| near_rational    |   32768 | byte_transpose |    29223 | 1.12x | 1.06x |
| pixel_values     |   32768 | byte_transpose |    26676 | 1.23x | 1.12x |
| random_walk      |   32768 | numeric_delta |     2157 | 15.19x | 2.23x |
| sine_wave        |   32768 | delta2_zigzag |    17363 | 1.89x | 1.33x |
| step_function    |   32768 | numeric_delta |      208 | 157.54x | 1.11x |
| stock_prices     |   32768 | byte_transpose |    26376 | 1.24x | 1.16x |
| temperatures     |   32768 | byte_transpose |    26896 | 1.22x | 1.14x |

**Totals**: Raw=327680B, Auto=178626B (1.83x), zlib=205849B (1.59x)
**Auto vs zlib**: 1.15x improvement

## Experiment 8: Production Codec with File I/O


### 1KB test (128 floats)

| Metric | Value |
|--------|-------|
| Raw size | 1,024 B |
| Compressed | 775 B |
| Ratio | 1.32x |
| Encode time | 2.6 ms |
| Decode time | 0.3 ms |
| Lossless | YES |

### 10KB test (1280 floats)

| Metric | Value |
|--------|-------|
| Raw size | 10,240 B |
| Compressed | 6,494 B |
| Ratio | 1.58x |
| Encode time | 8.1 ms |
| Decode time | 1.1 ms |
| Lossless | YES |

### 100KB test (12800 floats)

| Metric | Value |
|--------|-------|
| Raw size | 102,400 B |
| Compressed | 59,622 B |
| Ratio | 1.72x |
| Encode time | 84.4 ms |
| Decode time | 12.9 ms |
| Lossless | YES |

API: `encode_file(input, output, method='auto')`, `decode_file(input, output)`
Supports streaming with configurable chunk size and progress reporting.

---
Total runtime: 1.5s

## Summary of Findings

1. **PPT wavelet lossless**: Clean API, falls back to raw+zlib when scaling loses precision
2. **PPT+MTF combo**: MTF after wavelet coefficients can help on structured data
3. **IEEE 754 planes**: Separating sign/exponent/mantissa — exponent plane compresses well
4. **XOR delta**: Simple and effective for correlated floats (GPS, stock prices)
5. **Byte transpose**: Blosc-style, groups similar bytes — strong on smooth data
6. **Benchmark**: No single method wins all — data-dependent selection is key
7. **Auto-selector**: Picks best per-dataset, always >= zlib
8. **Production codec**: File I/O with chunked streaming, auto method selection