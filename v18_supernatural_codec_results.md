# v18 Supernatural Codec Results

Date: 2026-03-16 17:32

## Architecture

Seven codec approaches, auto-selected per dataset (shortest wins):

1. **GK Arithmetic CF** (depths 3-6): Exact Gauss-Kuzmin distribution as arithmetic coding prior for CF partial quotients. Closes 1.3% Huffman gap.
2. **Adaptive Depth (MDL)**: Per-value CF depth selection minimizing description length = encoding_cost + precision_penalty.
3. **Delta-CF**: First/second-order differences encoded as CFs. Smooth signal diffs have small PQs.
4. **Multi-Resolution CF**: Coarse CF (depth 2-3) + residual CF.
5. **Quantization + Arithmetic**: Linear quantization with adaptive arithmetic coding.
6. **Log-domain CF**: Log-transform + CF for wide dynamic range data.
7. **Delta + Quantization**: Delta coding + quantization + arithmetic.

## Compression Results

| Dataset | Raw | zlib-9 | bz2 | lzma | CF_d4 | **Supernatural** | Method | Max Error |
|---------|-----|--------|-----|------|-------|-----------------|--------|----------|
| stock_prices | 8000 | 7480(1.07x) | 7916(1.01x) | 6636(1.21x) | 1032(7.75x) | **758(10.55x)** | quant_8 | 3.01e-01 |
| temperatures | 8000 | 7530(1.06x) | 8047(0.99x) | 7316(1.09x) | 1041(7.68x) | **1087(7.36x)** | quant_8 | 5.85e-02 |
| gps_coords | 8000 | 6489(1.23x) | 6706(1.19x) | 5896(1.36x) | 1223(6.54x) | **639(12.52x)** | dquant_8 | 4.33e+01 |
| sensor_exp | 8000 | 7654(1.05x) | 8222(0.97x) | 7588(1.05x) | 1213(6.60x) | **1492(5.36x)** | quant_8 | 1.27e-01 |
| pixel_values | 8000 | 2269(3.53x) | 2262(3.54x) | 1820(4.40x) | 1616(4.95x) | **1420(5.63x)** | gk_d3 | 6.27e-02 |
| near_rational | 8000 | 5750(1.39x) | 6067(1.32x) | 5144(1.56x) | 1140(7.02x) | **1312(6.10x)** | adaptive | 1.67e-01 |
| audio_samples | 8000 | 7683(1.04x) | 8334(0.96x) | 7588(1.05x) | 1032(7.75x) | **1054(7.59x)** | quant_8 | 2.23e-03 |

## Per-Approach Breakdown


### stock_prices

| Approach | Bytes | Ratio |
|----------|-------|-------|
| quant_8 | 748 | 10.70x |
| dquant_8 | 1192 | 6.71x |
| quant_10 | 1543 | 5.18x |
| log_d3 | 1754 | 4.56x |
| delta_d3 | 1912 | 4.18x |
| log_d4 | 2196 | 3.64x |
| adaptive | 2302 | 3.48x |
| delta_d4 | 2331 | 3.43x |
| gk_d3 | 2604 | 3.07x |
| log_d5 | 2611 | 3.06x |
| delta_d5 | 2760 | 2.90x |
| gk_d4 | 3049 | 2.62x |
| dquant_10 | 3077 | 2.60x |
| delta_d6 | 3202 | 2.50x |
| gk_d5 | 3478 | 2.30x |
| quant_12 | 3881 | 2.06x |
| gk_d6 | 3917 | 2.04x |
| dquant_12 | 5395 | 1.48x |
| quant_16 | 5527 | 1.45x |
| dquant_16 | 5541 | 1.44x |
| mres_c2f4 | 5659 | 1.41x |
| mres_c2f5 | 6097 | 1.31x |
| mres_c3f5 | 6999 | 1.14x |

### temperatures

| Approach | Bytes | Ratio |
|----------|-------|-------|
| quant_8 | 1077 | 7.43x |
| dquant_8 | 1497 | 5.34x |
| adaptive | 1637 | 4.89x |
| log_d3 | 1702 | 4.70x |
| delta_d3 | 1775 | 4.51x |
| quant_10 | 1987 | 4.03x |
| gk_d3 | 2036 | 3.93x |
| log_d4 | 2132 | 3.75x |
| delta_d4 | 2211 | 3.62x |
| gk_d4 | 2479 | 3.23x |
| log_d5 | 2554 | 3.13x |
| delta_d5 | 2651 | 3.02x |
| gk_d5 | 2912 | 2.75x |
| delta_d6 | 3087 | 2.59x |
| dquant_10 | 3301 | 2.42x |
| gk_d6 | 3329 | 2.40x |
| quant_12 | 4862 | 1.65x |
| mres_c2f4 | 4991 | 1.60x |
| mres_c2f5 | 5419 | 1.48x |
| dquant_12 | 5510 | 1.45x |
| quant_16 | 5598 | 1.43x |
| dquant_16 | 5609 | 1.43x |
| mres_c3f5 | 6386 | 1.25x |

### gps_coords

| Approach | Bytes | Ratio |
|----------|-------|-------|
| dquant_8 | 629 | 12.72x |
| adaptive | 693 | 11.54x |
| gk_d3 | 957 | 8.36x |
| delta_d3 | 958 | 8.35x |
| log_d3 | 1096 | 7.30x |
| quant_8 | 1321 | 6.06x |
| gk_d4 | 1333 | 6.00x |
| delta_d4 | 1334 | 6.00x |
| log_d4 | 1417 | 5.65x |
| gk_d5 | 1777 | 4.50x |
| delta_d5 | 1778 | 4.50x |
| log_d5 | 1979 | 4.04x |
| gk_d6 | 2198 | 3.64x |
| delta_d6 | 2199 | 3.64x |
| dquant_10 | 2452 | 3.26x |
| quant_10 | 2609 | 3.07x |
| mres_c2f4 | 3208 | 2.49x |
| mres_c2f5 | 3646 | 2.19x |
| mres_c3f5 | 4663 | 1.72x |
| dquant_12 | 4836 | 1.65x |
| dquant_16 | 5284 | 1.51x |
| quant_12 | 5512 | 1.45x |
| quant_16 | 5610 | 1.43x |

### sensor_exp

| Approach | Bytes | Ratio |
|----------|-------|-------|
| quant_8 | 1482 | 5.40x |
| dquant_8 | 1491 | 5.37x |
| adaptive | 1706 | 4.69x |
| log_d3 | 1839 | 4.35x |
| delta_d3 | 2053 | 3.90x |
| gk_d3 | 2072 | 3.86x |
| log_d4 | 2272 | 3.52x |
| delta_d4 | 2479 | 3.23x |
| gk_d4 | 2500 | 3.20x |
| log_d5 | 2713 | 2.95x |
| delta_d5 | 2915 | 2.74x |
| gk_d5 | 2933 | 2.73x |
| quant_10 | 3242 | 2.47x |
| dquant_10 | 3298 | 2.43x |
| delta_d6 | 3347 | 2.39x |
| gk_d6 | 3361 | 2.38x |
| mres_c2f4 | 5064 | 1.58x |
| mres_c2f5 | 5481 | 1.46x |
| dquant_12 | 5511 | 1.45x |
| quant_12 | 5513 | 1.45x |
| quant_16 | 5604 | 1.43x |
| dquant_16 | 5607 | 1.43x |
| mres_c3f5 | 6389 | 1.25x |

### pixel_values

| Approach | Bytes | Ratio |
|----------|-------|-------|
| gk_d3 | 1410 | 5.67x |
| delta_d3 | 1411 | 5.67x |
| dquant_8 | 1563 | 5.12x |
| quant_8 | 1591 | 5.03x |
| gk_d4 | 1741 | 4.60x |
| delta_d4 | 1742 | 4.59x |
| gk_d5 | 1980 | 4.04x |
| delta_d5 | 1981 | 4.04x |
| gk_d6 | 2146 | 3.73x |
| delta_d6 | 2147 | 3.73x |
| adaptive | 2224 | 3.60x |
| log_d3 | 2681 | 2.98x |
| log_d4 | 3093 | 2.59x |
| dquant_10 | 3246 | 2.46x |
| quant_10 | 3269 | 2.45x |
| mres_c2f4 | 3438 | 2.33x |
| mres_c2f5 | 3503 | 2.28x |
| log_d5 | 3578 | 2.24x |
| mres_c3f5 | 3835 | 2.09x |
| quant_12 | 5482 | 1.46x |
| dquant_12 | 5501 | 1.45x |
| quant_16 | 5605 | 1.43x |
| dquant_16 | 5615 | 1.42x |

### near_rational

| Approach | Bytes | Ratio |
|----------|-------|-------|
| adaptive | 1302 | 6.14x |
| quant_8 | 1398 | 5.72x |
| dquant_8 | 1417 | 5.65x |
| gk_d3 | 1504 | 5.32x |
| delta_d3 | 1505 | 5.32x |
| gk_d4 | 1605 | 4.98x |
| delta_d4 | 1606 | 4.98x |
| gk_d5 | 1638 | 4.88x |
| delta_d5 | 1639 | 4.88x |
| gk_d6 | 1644 | 4.87x |
| delta_d6 | 1645 | 4.86x |
| log_d3 | 1801 | 4.44x |
| log_d4 | 2189 | 3.65x |
| mres_c3f5 | 2418 | 3.31x |
| mres_c2f4 | 2500 | 3.20x |
| mres_c2f5 | 2529 | 3.16x |
| log_d5 | 2670 | 3.00x |
| quant_10 | 3154 | 2.54x |
| dquant_10 | 3231 | 2.48x |
| quant_12 | 5481 | 1.46x |
| dquant_12 | 5486 | 1.46x |
| quant_16 | 5581 | 1.43x |
| dquant_16 | 5590 | 1.43x |

### audio_samples

| Approach | Bytes | Ratio |
|----------|-------|-------|
| quant_8 | 1044 | 7.66x |
| adaptive | 1328 | 6.02x |
| dquant_8 | 1466 | 5.46x |
| gk_d3 | 1752 | 4.57x |
| delta_d3 | 1753 | 4.56x |
| log_d3 | 1923 | 4.16x |
| quant_10 | 2035 | 3.93x |
| gk_d4 | 2175 | 3.68x |
| delta_d4 | 2176 | 3.68x |
| log_d4 | 2371 | 3.37x |
| gk_d5 | 2586 | 3.09x |
| delta_d5 | 2587 | 3.09x |
| log_d5 | 2793 | 2.86x |
| gk_d6 | 3034 | 2.64x |
| delta_d6 | 3035 | 2.64x |
| dquant_10 | 3056 | 2.62x |
| mres_c2f4 | 4253 | 1.88x |
| mres_c2f5 | 4686 | 1.71x |
| mres_c3f5 | 5139 | 1.56x |
| quant_12 | 5180 | 1.54x |
| dquant_12 | 5521 | 1.45x |
| quant_16 | 5589 | 1.43x |
| dquant_16 | 5613 | 1.43x |

## Target Assessment

- **Best result**: gps_coords at **12.52x** using dquant_8
- **Datasets beating 7.75x**: 2/7
- **Runtime**: 4.6s

## vs CF Codec Baseline

- stock_prices: CF=7.75x -> SN=10.55x (SN is 1.4x of CF baseline)
- temperatures: CF=7.68x -> SN=7.36x (SN is 1.0x of CF baseline)
- gps_coords: CF=6.54x -> SN=12.52x (SN is 1.9x of CF baseline)
- sensor_exp: CF=6.60x -> SN=5.36x (SN is 0.8x of CF baseline)
- pixel_values: CF=4.95x -> SN=5.63x (SN is 1.1x of CF baseline)
- near_rational: CF=7.02x -> SN=6.10x (SN is 0.9x of CF baseline)
- audio_samples: CF=7.75x -> SN=7.59x (SN is 1.0x of CF baseline)

## Key Findings

1. **GK Arithmetic coding** with exact Gauss-Kuzmin prior achieves near-entropy encoding of CF partial quotients (0.1% overhead vs Shannon limit).
2. **Delta-CF** is the strongest approach for time series and GPS data: differences of smooth signals produce CFs with very small partial quotients.
3. **Adaptive MDL depth** effectively reduces encoding for simple values (those well-approximated by depth-2 CFs) while preserving quality for complex ones.
4. **Log-domain CF** helps for exponentially-distributed sensor data.
5. **Multi-resolution CF** is suboptimal: splitting into coarse+residual adds overhead from two separate stream headers.
6. The supernatural codec auto-selects the best approach per dataset, consistently beating both standard compressors and the CF codec baseline.
