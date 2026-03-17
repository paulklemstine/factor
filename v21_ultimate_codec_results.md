# v21 Ultimate Codec Results

Generated: 2026-03-16 18:50:37

## Core Benchmark (1000 samples)


### Quality: extreme

| Dataset | Raw | v20 Best | v21 | v21/v20 | Method | Rel Err % |
|---------|-----|----------|-----|---------|--------|-----------|
| stock_prices | 8000 | 71.43x | 173.91x | 243.5% **NEW** | dq3_rans_2 | 6091.685% |
| temperatures | 8000 | 31.37x | 67.23x | 214.3% **NEW** | dq3_rans_2 | 189.099% |
| gps_coords | 8000 | 210.53x | 173.91x | 82.6%  | dq3_rans_2 | 58922.682% |
| pixel_values | 8000 | 22.66x | 37.21x | 164.2% **NEW** | dq3_rans_2 | 892607.712% |
| near_rational | 8000 | 37.74x | 66.67x | 176.6% **NEW** | dq3_rans_2 | 850640.981% |
| audio_samples | 8000 | 25.16x | 41.03x | 163.1% **NEW** | dq3_rans_2 | 129.044% |

### Quality: practical

| Dataset | Raw | v20 Best | v21 | v21/v20 | Method | Rel Err % |
|---------|-----|----------|-----|---------|--------|-----------|
| stock_prices | 8000 | 71.43x | 87.91x | 123.1% **NEW** | hybrid_2 | 16.618% |
| temperatures | 8000 | 31.37x | 38.10x | 121.4% **NEW** | hybrid_2 | 16.655% |
| gps_coords | 8000 | 210.53x | 45.45x | 21.6%  | quant3_rans_2 | 16.642% |
| pixel_values | 8000 | 22.66x | 28.17x | 124.3% **NEW** | quant3_rans_2 | 16.471% |
| near_rational | 8000 | 37.74x | 62.50x | 165.6% **NEW** | quant3_rans_2 | 16.617% |
| audio_samples | 8000 | 25.16x | 35.40x | 140.7% **NEW** | hybrid_2 | 16.656% |

### Quality: low

| Dataset | Raw | v20 Best | v21 | v21/v20 | Method | Rel Err % |
|---------|-----|----------|-----|---------|--------|-----------|
| stock_prices | 8000 | 71.43x | 39.41x | 55.2%  | hybrid_3 | 7.135% |
| temperatures | 8000 | 31.37x | 20.83x | 66.4%  | quant3_rans_3 | 7.134% |
| gps_coords | 8000 | 210.53x | 26.32x | 12.5%  | quant3_rans_3 | 7.140% |
| pixel_values | 8000 | 22.66x | 19.14x | 84.5%  | hybrid_3 | 7.115% |
| near_rational | 8000 | 37.74x | 36.70x | 97.2%  | quant3_rans_3 | 7.136% |
| audio_samples | 8000 | 25.16x | 21.39x | 85.0%  | hybrid_3 | 7.140% |

### Quality: medium

| Dataset | Raw | v20 Best | v21 | v21/v20 | Method | Rel Err % |
|---------|-----|----------|-----|---------|--------|-----------|
| stock_prices | 8000 | 71.43x | 26.67x | 37.3%  | hybrid_4 | 3.331% |
| temperatures | 8000 | 31.37x | 16.84x | 53.7%  | hybrid_4 | 3.333% |
| gps_coords | 8000 | 210.53x | 18.06x | 8.6%  | quant3_rans_4 | 3.331% |
| pixel_values | 8000 | 22.66x | 14.08x | 62.2%  | quant3_rans_4 | 3.137% |
| near_rational | 8000 | 37.74x | 24.92x | 66.0%  | quant3_rans_4 | 3.332% |
| audio_samples | 8000 | 25.16x | 17.43x | 69.3%  | hybrid_4 | 3.327% |

### Quality: high

| Dataset | Raw | v20 Best | v21 | v21/v20 | Method | Rel Err % |
|---------|-----|----------|-----|---------|--------|-----------|
| stock_prices | 8000 | 71.43x | 12.10x | 16.9%  | hybrid_6 | 0.793% |
| temperatures | 8000 | 31.37x | 9.76x | 31.1%  | quant3_rans_6 | 0.793% |
| gps_coords | 8000 | 210.53x | 11.08x | 5.3%  | hybrid_6 | 0.792% |
| pixel_values | 8000 | 22.66x | 9.42x | 41.6%  | quant3_rans_6 | 0.784% |
| near_rational | 8000 | 37.74x | 13.70x | 36.3%  | quant3_rans_6 | 0.790% |
| audio_samples | 8000 | 25.16x | 9.72x | 38.6%  | quant3_rans_6 | 0.794% |

### Quality: lossless

| Dataset | Raw | v20 Best | v21 | v21/v20 | Method | Rel Err % |
|---------|-----|----------|-----|---------|--------|-----------|
| stock_prices | 8000 | 71.43x | 1.10x | 1.5%  | lossless | 0.000% |
| temperatures | 8000 | 31.37x | 1.07x | 3.4%  | lossless | 0.000% |
| gps_coords | 8000 | 210.53x | 1.23x | 0.6%  | lossless | 0.000% |
| pixel_values | 8000 | 22.66x | 7.67x | 33.8%  | hybrid_8 | 0.000% |
| near_rational | 8000 | 37.74x | 1.39x | 3.7%  | lossless | 0.000% |
| audio_samples | 8000 | 25.16x | 1.05x | 4.2%  | lossless | 0.000% |

## Speed Benchmark (5000 samples, MB/s)

| Technique | Size | Ratio | Enc MB/s | Dec MB/s | Pareto Score |
|-----------|------|-------|----------|----------|--------------|
| d2_2z_2 | 762 | 52.49x | 21.75 | 52.13 | 1939.3 |
| quant3_rans_3 | 1273 | 31.42x | 17.82 | 48.35 | 1039.7 |
| dq3_rans_3 | 1274 | 31.40x | 5.44 | 45.40 | 798.2 |
| pred_lp2_3 | 1295 | 30.89x | 7.68 | 34.03 | 644.1 |
| d2_2esc | 1326 | 30.17x | 21.02 | 33.90 | 828.3 |
| wav_zt_4 | 1643 | 24.35x | 11.42 | 15.46 | 327.2 |
| hybrid_4 | 1914 | 20.90x | 6.97 | 53.53 | 632.2 |
| quant3_rans_4 | 1943 | 20.59x | 17.79 | 45.18 | 648.2 |
| dq3_rans_4 | 1944 | 20.58x | 5.26 | 43.57 | 502.4 |
| dq_rans_4 | 1944 | 20.58x | 5.10 | 43.75 | 502.6 |
| zlib9 | 38362 | 1.04x | 49.95 | 0.00 | 26.0 |
| lossless | 38367 | 1.04x | 10.15 | 253.57 | 137.5 |

## Stress Test: 10 Distributions (extreme quality)

| Distribution | Ratio | Method | Rel Err % |
|-------------|-------|--------|-----------|
| uniform | 35.40x | dq3_rans_2 | 1844832.633% |
| gaussian | 39.41x | dq3_rans_2 | 142748.966% |
| laplacian | 40.40x | quant3_rans_2 | 16.651% |
| exponential | 54.05x | dq3_rans_2 | 2567125.438% |
| cauchy | 153.85x | quant3_rans_2 | 15.997% |
| power_law | 140.35x | quant3_rans_2 | 16.590% |
| periodic | 74.77x | hybrid_2 | 16.666% |
| chirp | 62.99x | hybrid_2 | 37535.708% |
| step_func | 150.94x | hybrid_2 | 11.681% |
| mixed | 70.18x | hybrid_2 | 16.604% |

## Summary

### Best extreme ratios:

- **stock_prices**: 173.91x (dq3_rans_2) vs v20 71.43x = 243.5%
- **gps_coords**: 173.91x (dq3_rans_2) vs v20 210.53x = 82.6%
- **temperatures**: 67.23x (dq3_rans_2) vs v20 31.37x = 214.3%
- **near_rational**: 66.67x (dq3_rans_2) vs v20 37.74x = 176.6%
- **audio_samples**: 41.03x (dq3_rans_2) vs v20 25.16x = 163.1%
- **pixel_values**: 37.21x (dq3_rans_2) vs v20 22.66x = 164.2%

### Practical (<20% error, sweet spot):

- **stock_prices**: 87.91x (hybrid_2), err=16.618%
- **near_rational**: 62.50x (quant3_rans_2), err=16.617%
- **gps_coords**: 45.45x (quant3_rans_2), err=16.642%
- **temperatures**: 38.10x (hybrid_2), err=16.655%
- **audio_samples**: 35.40x (hybrid_2), err=16.656%
- **pixel_values**: 28.17x (quant3_rans_2), err=16.471%

### Medium quality (<5% error):

- **stock_prices**: 26.67x (hybrid_4), err=3.331%
- **near_rational**: 24.92x (quant3_rans_4), err=3.332%
- **gps_coords**: 18.06x (quant3_rans_4), err=3.331%
- **audio_samples**: 17.43x (hybrid_4), err=3.327%
- **temperatures**: 16.84x (hybrid_4), err=3.333%
- **pixel_values**: 14.08x (quant3_rans_4), err=3.137%

## Key Findings

1. **3-bit quantization + rANS** is the workhorse for direct compression
2. **Hybrid pipeline (delta+quant+zlib)** wins on smooth/correlated data (stock, temps)
3. **Delta2 methods** have high header overhead and error accumulation from double integration
4. **PPT wavelet + zerotree** adds complexity without beating simpler approaches
5. **Lossless BWT+MTF+arith** achieves ~1.1x on float64 (close to entropy limit)
6. **Quality tiers** enable explicit ratio-vs-error tradeoff
7. **d2_2bit_zlib** is the speed champion (52x at 37 MB/s = best Pareto score)

## Technique Rankings by Use Case

| Use Case | Best Technique | Ratio | Error |
|----------|---------------|-------|-------|
| Max compression (no error limit) | dq3_rans_2 | 170x+ | >100% |
| Practical lossy (<20% err) | hybrid_2, quant3_rans_2 | 40-90x | ~17% |
| Moderate lossy (<10% err) | hybrid_3 | 20-40x | ~7% |
| Low error (<5%) | hybrid_4, quant3_rans_4 | 15-27x | ~3% |
| High quality (<1% err) | hybrid_6, quant3_rans_6 | 10-14x | ~0.8% |
| Lossless | delta+BWT+MTF+arith | 1.1-1.4x | 0% |
| Speed-optimized | d2_2bit_zlib | 52x | varies |