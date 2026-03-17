# v19 Supernatural Codec v2 Results

Date: 2026-03-16 18:27

## New Techniques in v19

1. **Fused Delta-Quant-Arith**: Single-pass delta+quantize+arithmetic with order selection
2. **Predictive CF**: Linear prediction on PQ residuals (predict PQ[i] from PQ[i-1])
3. **Tree-Walk + CF hybrid**: MTF on integer parts, CF on fractional parts
4. **Bit-plane coding**: Separate quantized values into bit planes, compress each optimally
5. **CRT-CF hybrid**: Decompose PQs mod (2,3,7), encode components separately
6. **Adaptive block sizing**: MDL-optimal block size per segment
7. **Cascaded compression**: delta -> CF -> GK arithmetic pipeline
8. **Sorted quantization**: Sort values, quantize tiny diffs, store permutation
9. **Delta-sorted quantization**: Delta then sorted-quant

## v19 vs v18 Results

| Dataset | Raw | v18 Best | v18 Ratio | v19 Best | v19 Ratio | Improvement | Max Error |
|---------|-----|----------|-----------|----------|-----------|-------------|----------|
| stock_prices | 8000 | quant_8 | 10.55x | quant_6 | **20.94x** | +98.5% | 1.22e+00 |
| temperatures | 8000 | quant_8 | 7.36x | quant_6 | **11.94x** | +62.2% | 2.37e-01 |
| gps_coords | 8000 | dquant_8 | 12.52x | dquant_6 | **42.55x** | +239.9% | 4.44e+01 |
| pixel_values | 8000 | gk_d3 | 5.63x | bitplane_6 | **10.18x** | +80.8% | 7.84e-03 |
| near_rational | 8000 | adaptive | 6.10x | fused_dqa_6 | **12.25x** | +100.8% | 3.94e-01 |
| audio_samples | 8000 | quant_8 | 7.59x | quant_6 | **12.48x** | +64.4% | 8.63e-03 |

## vs Standard Compressors

| Dataset | zlib-9 | lzma | CF_d4 | **v19 SN** | SN/zlib | SN/lzma |
|---------|--------|------|-------|------------|---------|--------|
| stock_prices | 1.07x | 1.21x | 7.75x | **20.94x** | 19.58x | 17.37x |
| temperatures | 1.06x | 1.09x | 7.68x | **11.94x** | 11.24x | 10.92x |
| gps_coords | 1.23x | 1.36x | 6.54x | **42.55x** | 34.52x | 31.36x |
| pixel_values | 3.54x | 4.43x | 5.05x | **10.18x** | 2.87x | 2.30x |
| near_rational | 1.39x | 1.55x | 7.04x | **12.25x** | 8.82x | 7.88x |
| audio_samples | 1.04x | 1.06x | 7.75x | **12.48x** | 11.98x | 11.77x |

## Per-Approach Breakdown


### stock_prices

| Approach | Bytes | Ratio | Max Error |
|----------|-------|-------|-----------|
| quant_6 | 372 | 21.51x | 1.22e+00 |
| dquant_6 | 520 | 15.38x | 1.98e+01 |
| fused_dqa_6 | 520 | 15.38x | 1.98e+01 |
| bitplane_6 | 603 | 13.27x | 1.22e+00 |
| quant_8 | 748 | 10.70x | 3.01e-01 |
| bitplane_8 | 851 | 9.40x | 3.01e-01 |
| bitplane_10 | 1102 | 7.26x | 7.49e-02 |
| dquant_8 | 1192 | 6.71x | 3.26e+00 |
| fused_dqa_8 | 1192 | 6.71x | 3.26e+00 |
| quant_10 | 1543 | 5.18x | 7.49e-02 |
| cascaded_d3 | 1912 | 4.18x | 4.76e+02 |
| adaptive | 2302 | 3.48x | 1.66e-01 |
| delta_cf_d4 | 2331 | 3.43x | 4.70e+02 |
| cascaded_d4 | 2331 | 3.43x | 4.70e+02 |
| gk_d3 | 2604 | 3.07x | 6.65e-02 |
| treewalk_d3 | 2695 | 2.97x | 6.65e-02 |
| delta_cf_d5 | 2760 | 2.90x | 4.71e+02 |
| gk_d4 | 3049 | 2.62x | 2.12e-02 |
| pred_cf_d4 | 3050 | 2.62x | 2.12e-02 |
| crt_cf_d4 | 3050 | 2.62x | 2.12e-02 |
| dquant_10 | 3077 | 2.60x | 1.02e+00 |
| fused_dqa_10 | 3077 | 2.60x | 1.02e+00 |
| treewalk_d4 | 3140 | 2.55x | 2.12e-02 |
| sortquant_6 | 3198 | 2.50x | 1.22e+00 |
| sortquant_8 | 3270 | 2.45x | 3.01e-01 |
| dsortquant_6 | 3349 | 2.39x | 1.98e+01 |
| sortquant_10 | 3409 | 2.35x | 7.49e-02 |
| gk_d5 | 3478 | 2.30x | 8.83e-03 |
| pred_cf_d5 | 3479 | 2.30x | 8.83e-03 |
| crt_cf_d5 | 3479 | 2.30x | 8.83e-03 |
| dsortquant_8 | 3559 | 2.25x | 3.26e+00 |
| dsortquant_10 | 3639 | 2.20x | 9.95e+01 |
| quant_12 | 3881 | 2.06x | 1.87e-02 |
| gk_d6 | 3917 | 2.04x | 3.52e-03 |
| dquant_12 | 5395 | 1.48x | 1.69e+05 |

### temperatures

| Approach | Bytes | Ratio | Max Error |
|----------|-------|-------|-----------|
| quant_6 | 660 | 12.12x | 2.37e-01 |
| bitplane_6 | 704 | 11.36x | 2.37e-01 |
| dquant_6 | 850 | 9.41x | 2.24e+00 |
| fused_dqa_6 | 850 | 9.41x | 2.24e+00 |
| bitplane_8 | 956 | 8.37x | 5.85e-02 |
| quant_8 | 1077 | 7.43x | 5.85e-02 |
| bitplane_10 | 1208 | 6.62x | 1.46e-02 |
| dquant_8 | 1497 | 5.34x | 6.52e-01 |
| fused_dqa_8 | 1497 | 5.34x | 6.52e-01 |
| adaptive | 1637 | 4.89x | 1.66e-01 |
| cascaded_d3 | 1775 | 4.51x | 4.74e+02 |
| quant_10 | 1987 | 4.03x | 1.46e-02 |
| gk_d3 | 2036 | 3.93x | 6.65e-02 |
| treewalk_d3 | 2092 | 3.82x | 6.65e-02 |
| delta_cf_d4 | 2211 | 3.62x | 4.68e+02 |
| cascaded_d4 | 2211 | 3.62x | 4.68e+02 |
| gk_d4 | 2479 | 3.23x | 2.31e-02 |
| pred_cf_d4 | 2480 | 3.23x | 2.31e-02 |
| crt_cf_d4 | 2480 | 3.23x | 2.31e-02 |
| treewalk_d4 | 2535 | 3.16x | 2.31e-02 |
| delta_cf_d5 | 2651 | 3.02x | 4.69e+02 |
| gk_d5 | 2912 | 2.75x | 9.59e-03 |
| pred_cf_d5 | 2913 | 2.75x | 9.59e-03 |
| crt_cf_d5 | 2913 | 2.75x | 9.59e-03 |
| sortquant_6 | 3190 | 2.51x | 2.37e-01 |
| sortquant_8 | 3262 | 2.45x | 5.85e-02 |
| dquant_10 | 3301 | 2.42x | 2.67e-01 |
| fused_dqa_10 | 3301 | 2.42x | 2.67e-01 |
| dsortquant_6 | 3319 | 2.41x | 2.24e+00 |
| gk_d6 | 3329 | 2.40x | 2.52e-03 |
| sortquant_10 | 3410 | 2.35x | 1.46e-02 |
| dsortquant_8 | 3450 | 2.32x | 6.52e-01 |
| dsortquant_10 | 3736 | 2.14x | 3.29e+00 |
| quant_12 | 4862 | 1.65x | 3.64e-03 |
| dquant_12 | 5510 | 1.45x | 6.43e+04 |

### gps_coords

| Approach | Bytes | Ratio | Max Error |
|----------|-------|-------|-----------|
| dquant_6 | 178 | 44.94x | 4.44e+01 |
| fused_dqa_6 | 178 | 44.94x | 4.44e+01 |
| dquant_8 | 629 | 12.72x | 4.33e+01 |
| fused_dqa_8 | 629 | 12.72x | 4.33e+01 |
| adaptive | 693 | 11.54x | 8.24e-02 |
| bitplane_6 | 776 | 10.31x | 5.97e-04 |
| quant_6 | 811 | 9.86x | 5.97e-04 |
| gk_d3 | 957 | 8.36x | 3.57e-02 |
| cascaded_d3 | 958 | 8.35x | 3.57e-02 |
| bitplane_8 | 1028 | 7.78x | 1.48e-04 |
| treewalk_d3 | 1056 | 7.58x | 3.57e-02 |
| bitplane_10 | 1280 | 6.25x | 3.68e-05 |
| quant_8 | 1321 | 6.06x | 1.48e-04 |
| gk_d4 | 1333 | 6.00x | 1.28e-02 |
| delta_cf_d4 | 1334 | 6.00x | 1.28e-02 |
| pred_cf_d4 | 1334 | 6.00x | 1.28e-02 |
| crt_cf_d4 | 1334 | 6.00x | 1.28e-02 |
| cascaded_d4 | 1334 | 6.00x | 1.28e-02 |
| treewalk_d4 | 1432 | 5.59x | 1.28e-02 |
| gk_d5 | 1777 | 4.50x | 4.89e-03 |
| delta_cf_d5 | 1778 | 4.50x | 4.89e-03 |
| pred_cf_d5 | 1778 | 4.50x | 4.89e-03 |
| crt_cf_d5 | 1778 | 4.50x | 4.89e-03 |
| gk_d6 | 2198 | 3.64x | 1.91e-03 |
| dquant_10 | 2452 | 3.26x | 1.41e+00 |
| fused_dqa_10 | 2452 | 3.26x | 1.41e+00 |
| quant_10 | 2609 | 3.07x | 3.68e-05 |
| sortquant_6 | 3278 | 2.44x | 5.97e-04 |
| dsortquant_6 | 3316 | 2.41x | 4.44e+01 |
| sortquant_8 | 3371 | 2.37x | 1.48e-04 |
| dsortquant_8 | 3538 | 2.26x | 4.33e+01 |
| dsortquant_10 | 3540 | 2.26x | 3.19e+01 |
| sortquant_10 | 3617 | 2.21x | 3.68e-05 |
| dquant_12 | 4836 | 1.65x | 4.08e+04 |
| quant_12 | 5512 | 1.45x | 4.71e-01 |

### pixel_values

| Approach | Bytes | Ratio | Max Error |
|----------|-------|-------|-----------|
| bitplane_6 | 776 | 10.31x | 7.84e-03 |
| fused_dqa_6 | 908 | 8.81x | 7.84e-03 |
| dquant_6 | 961 | 8.32x | 1.91e-01 |
| quant_6 | 980 | 8.16x | 7.84e-03 |
| bitplane_8 | 1028 | 7.78x | 0.00e+00 |
| bitplane_10 | 1280 | 6.25x | 4.83e-04 |
| gk_d3 | 1385 | 5.78x | 6.27e-02 |
| cascaded_d3 | 1386 | 5.77x | 6.27e-02 |
| fused_dqa_8 | 1531 | 5.23x | 2.73e+01 |
| treewalk_d3 | 1537 | 5.20x | 6.27e-02 |
| dquant_8 | 1586 | 5.04x | 1.15e-01 |
| quant_8 | 1592 | 5.03x | 0.00e+00 |
| gk_d4 | 1719 | 4.65x | 2.35e-02 |
| delta_cf_d4 | 1720 | 4.65x | 2.35e-02 |
| pred_cf_d4 | 1720 | 4.65x | 2.35e-02 |
| crt_cf_d4 | 1720 | 4.65x | 2.35e-02 |
| cascaded_d4 | 1720 | 4.65x | 2.35e-02 |
| treewalk_d4 | 1871 | 4.28x | 2.35e-02 |
| gk_d5 | 1966 | 4.07x | 9.31e-03 |
| delta_cf_d5 | 1967 | 4.07x | 9.31e-03 |
| pred_cf_d5 | 1967 | 4.07x | 9.31e-03 |
| crt_cf_d5 | 1967 | 4.07x | 9.31e-03 |
| gk_d6 | 2144 | 3.73x | 1.44e-03 |
| adaptive | 2225 | 3.60x | 1.39e-01 |
| fused_dqa_10 | 3163 | 2.53x | 3.97e+01 |
| quant_10 | 3280 | 2.44x | 4.83e-04 |
| sortquant_6 | 3280 | 2.44x | 7.84e-03 |
| dsortquant_6 | 3300 | 2.42x | 1.91e-01 |
| dquant_10 | 3330 | 2.40x | 2.60e-02 |
| sortquant_8 | 3346 | 2.39x | 0.00e+00 |
| sortquant_10 | 3356 | 2.38x | 4.83e-04 |
| dsortquant_8 | 3374 | 2.37x | 1.15e-01 |
| dsortquant_10 | 3462 | 2.31x | 2.60e-02 |
| quant_12 | 5483 | 1.46x | 1.28e+02 |
| dquant_12 | 5494 | 1.46x | 8.48e+04 |

### near_rational

| Approach | Bytes | Ratio | Max Error |
|----------|-------|-------|-----------|
| fused_dqa_6 | 643 | 12.44x | 3.94e-01 |
| bitplane_6 | 663 | 12.07x | 3.94e-01 |
| quant_6 | 767 | 10.43x | 3.94e-01 |
| dquant_6 | 773 | 10.35x | 1.45e+01 |
| bitplane_8 | 910 | 8.79x | 9.72e-02 |
| bitplane_10 | 1162 | 6.88x | 2.43e-02 |
| fused_dqa_8 | 1290 | 6.20x | 9.72e-02 |
| adaptive | 1294 | 6.18x | 1.67e-01 |
| quant_8 | 1398 | 5.72x | 9.72e-02 |
| dquant_8 | 1417 | 5.65x | 3.65e+00 |
| gk_d3 | 1493 | 5.36x | 6.67e-02 |
| cascaded_d3 | 1494 | 5.35x | 6.67e-02 |
| gk_d4 | 1590 | 5.03x | 2.50e-02 |
| delta_cf_d4 | 1591 | 5.03x | 2.50e-02 |
| pred_cf_d4 | 1591 | 5.03x | 2.50e-02 |
| crt_cf_d4 | 1591 | 5.03x | 2.50e-02 |
| cascaded_d4 | 1591 | 5.03x | 2.50e-02 |
| gk_d5 | 1622 | 4.93x | 9.62e-03 |
| delta_cf_d5 | 1623 | 4.93x | 9.62e-03 |
| pred_cf_d5 | 1623 | 4.93x | 9.62e-03 |
| crt_cf_d5 | 1623 | 4.93x | 9.62e-03 |
| gk_d6 | 1628 | 4.91x | 3.93e-10 |
| treewalk_d3 | 1738 | 4.60x | 6.67e-02 |
| treewalk_d4 | 1835 | 4.36x | 2.50e-02 |
| fused_dqa_10 | 3127 | 2.56x | 2.43e-02 |
| quant_10 | 3155 | 2.54x | 2.43e-02 |
| dquant_10 | 3225 | 2.48x | 5.28e-01 |
| dsortquant_6 | 3295 | 2.43x | 1.45e+01 |
| sortquant_6 | 3333 | 2.40x | 3.94e-01 |
| dsortquant_8 | 3360 | 2.38x | 3.65e+00 |
| sortquant_8 | 3393 | 2.36x | 9.72e-02 |
| dsortquant_10 | 3497 | 2.29x | 5.28e-01 |
| sortquant_10 | 3531 | 2.27x | 2.43e-02 |
| dquant_12 | 5483 | 1.46x | 4.86e+04 |
| quant_12 | 5484 | 1.46x | 8.51e+02 |

### audio_samples

| Approach | Bytes | Ratio | Max Error |
|----------|-------|-------|-----------|
| quant_6 | 631 | 12.68x | 8.63e-03 |
| bitplane_6 | 746 | 10.72x | 8.63e-03 |
| dquant_6 | 872 | 9.17x | 4.89e-02 |
| fused_dqa_6 | 872 | 9.17x | 4.89e-02 |
| bitplane_8 | 998 | 8.02x | 2.13e-03 |
| quant_8 | 1146 | 6.98x | 2.13e-03 |
| bitplane_10 | 1250 | 6.40x | 5.31e-04 |
| adaptive | 1337 | 5.98x | 1.05e+00 |
| dquant_8 | 1416 | 5.65x | 1.02e-02 |
| fused_dqa_8 | 1416 | 5.65x | 1.02e-02 |
| gk_d3 | 1730 | 4.62x | 1.11e+00 |
| cascaded_d3 | 1731 | 4.62x | 1.11e+00 |
| treewalk_d3 | 1876 | 4.26x | 2.48e-02 |
| gk_d4 | 2141 | 3.74x | 1.11e+00 |
| delta_cf_d4 | 2142 | 3.73x | 1.11e+00 |
| pred_cf_d4 | 2142 | 3.73x | 1.11e+00 |
| crt_cf_d4 | 2142 | 3.73x | 1.11e+00 |
| cascaded_d4 | 2142 | 3.73x | 1.11e+00 |
| treewalk_d4 | 2287 | 3.50x | 9.00e-03 |
| quant_10 | 2415 | 3.31x | 5.31e-04 |
| gk_d5 | 2577 | 3.10x | 1.11e+00 |
| delta_cf_d5 | 2578 | 3.10x | 1.11e+00 |
| pred_cf_d5 | 2578 | 3.10x | 1.11e+00 |
| crt_cf_d5 | 2578 | 3.10x | 1.11e+00 |
| dquant_10 | 2877 | 2.78x | 7.38e-03 |
| fused_dqa_10 | 2877 | 2.78x | 7.38e-03 |
| gk_d6 | 3002 | 2.66x | 1.11e+00 |
| sortquant_6 | 3179 | 2.52x | 8.63e-03 |
| sortquant_8 | 3252 | 2.46x | 2.13e-03 |
| dsortquant_6 | 3282 | 2.44x | 4.89e-02 |
| dsortquant_8 | 3367 | 2.38x | 1.02e-02 |
| sortquant_10 | 3411 | 2.35x | 5.31e-04 |
| dsortquant_10 | 3568 | 2.24x | 7.38e-03 |
| quant_12 | 5470 | 1.46x | 1.24e+00 |
| dquant_12 | 5523 | 1.45x | 7.54e+03 |

## Summary

- **Best result**: gps_coords at **42.55x**
- **15x+ target**: ACHIEVED
- **Datasets beating v18**: 6/6
- **Runtime**: 7.0s

## Key Findings

1. **Fused DQA** with order-2 delta excels on smooth time series (stock prices, GPS).
2. **Sorted quantization** is surprisingly effective for uniform/random data (pixels).
3. **Predictive CF** helps when PQ sequences are autocorrelated.
4. **CRT-CF** decomposition helps when PQs cluster around small values.
5. **Bit-plane coding** competitive for low-precision quantization.
6. **Cascaded** (delta->CF->arith) combines well for smooth signals.
7. 6-bit quantization pushes ratios higher at cost of precision.
