/*
 * siqs_sieve_fast.c — High-performance SIQS sieve kernel in C
 *
 * Drop-in replacement for the numba jit_presieve + jit_sieve + jit_find_smooth
 * hot path in siqs_engine.py. Called via ctypes from Python.
 *
 * Strategy: straight sieve (no blocking) with these optimizations:
 *   1. Presieve period-210 pattern for p=2,3,5,7 via memcpy tiling
 *   2. Direct sieve for primes 11-31 (too small to skip)
 *   3. Interleaved double-root sieve for primes >= 32
 *   4. 4x unrolled threshold scan with integrated candidate collection
 *   5. All in one C call to eliminate Python/ctypes overhead per phase
 *
 * At 60d (FB=4500, M=1.5M, sz=3M): targets ~2-3ms per polynomial.
 *
 * Compile:
 *   gcc -O3 -march=native -shared -fPIC -o siqs_sieve_fast.so siqs_sieve_fast.c -lm
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>


/* ============================================================================
 * Combined sieve + threshold scan.
 *
 * Phase 1: Presieve — tile period-210 pattern for primes 2,3,5,7
 * Phase 2: Sieve primes 11-31 directly
 * Phase 3: Sieve primes >= 32 with interleaved double-root inner loop
 * Phase 4: Threshold scan — 8-wide unroll
 *
 * Returns number of candidates found.
 * ============================================================================ */
int siqs_sieve_fast(
    int16_t *sieve,          /* sieve array [sz] — written by this function */
    int sz,
    const int64_t *fb,       /* factor base primes [n_fb] */
    const int16_t *fb_logp,  /* log2(p)*64 as int16 [n_fb] */
    const int64_t *off1,     /* sieve offset 1 [n_fb], -1 = skip */
    const int64_t *off2,     /* sieve offset 2 [n_fb], -1 = skip */
    int n_fb,
    int16_t threshold,
    int32_t *out_cands,      /* output: candidate sieve positions */
    int max_cands)
{
    /* Phase 1: Presieve — build period-210 pattern for primes 2,3,5,7 */
    int16_t pattern[210];
    memset(pattern, 0, sizeof(pattern));
    int idx_ge8 = 0;  /* first FB entry with p > 7 */
    for (int i = 0; i < n_fb; i++) {
        int p = (int)fb[i];
        if (p > 7) { idx_ge8 = i; break; }
        int16_t lp = fb_logp[i];
        if (off1[i] >= 0) {
            for (int j = (int)(off1[i] % p); j < 210; j += p)
                pattern[j] += lp;
        }
        if (off2[i] >= 0 && off2[i] != off1[i]) {
            for (int j = (int)(off2[i] % p); j < 210; j += p)
                pattern[j] += lp;
        }
    }

    /* Tile pattern into sieve array using memcpy (fast) */
    {
        int pos = 0;
        while (pos + 210 <= sz) {
            memcpy(sieve + pos, pattern, 210 * sizeof(int16_t));
            pos += 210;
        }
        if (pos < sz)
            memcpy(sieve + pos, pattern, (sz - pos) * sizeof(int16_t));
    }

    /* Phase 2: Sieve primes 11-31 (p > 7, p < 32) */
    for (int i = idx_ge8; i < n_fb; i++) {
        int p = (int)fb[i];
        if (p >= 32) break;
        int16_t lp = fb_logp[i];
        if (off1[i] >= 0)
            for (int j = (int)off1[i]; j < sz; j += p) sieve[j] += lp;
        if (off2[i] >= 0 && off2[i] != off1[i])
            for (int j = (int)off2[i]; j < sz; j += p) sieve[j] += lp;
    }

    /* Phase 3: Sieve primes >= 32 — interleaved double-root */
    for (int i = 0; i < n_fb; i++) {
        int p = (int)fb[i];
        if (p < 32) continue;
        int16_t lp = fb_logp[i];
        int o1 = (int)off1[i];
        int o2 = (int)off2[i];

        if (o1 >= 0 && o2 >= 0 && o2 != o1) {
            /* Interleave both roots — keep sorted for predictable access */
            int j1 = o1, j2 = o2;
            if (j1 > j2) { int t = j1; j1 = j2; j2 = t; }
            while (j2 < sz) {
                sieve[j1] += lp;
                sieve[j2] += lp;
                j1 += p;
                j2 += p;
            }
            if (j1 < sz) sieve[j1] += lp;
        } else if (o1 >= 0) {
            for (int j = o1; j < sz; j += p) sieve[j] += lp;
        } else if (o2 >= 0) {
            for (int j = o2; j < sz; j += p) sieve[j] += lp;
        }
    }

    /* Phase 4: Threshold scan — 8-wide unrolled for throughput */
    int n_cands = 0;
    int i;
    for (i = 0; i + 7 < sz; i += 8) {
        if (sieve[i]   >= threshold && n_cands < max_cands) out_cands[n_cands++] = i;
        if (sieve[i+1] >= threshold && n_cands < max_cands) out_cands[n_cands++] = i+1;
        if (sieve[i+2] >= threshold && n_cands < max_cands) out_cands[n_cands++] = i+2;
        if (sieve[i+3] >= threshold && n_cands < max_cands) out_cands[n_cands++] = i+3;
        if (sieve[i+4] >= threshold && n_cands < max_cands) out_cands[n_cands++] = i+4;
        if (sieve[i+5] >= threshold && n_cands < max_cands) out_cands[n_cands++] = i+5;
        if (sieve[i+6] >= threshold && n_cands < max_cands) out_cands[n_cands++] = i+6;
        if (sieve[i+7] >= threshold && n_cands < max_cands) out_cands[n_cands++] = i+7;
    }
    for (; i < sz; i++)
        if (sieve[i] >= threshold && n_cands < max_cands) out_cands[n_cands++] = i;

    return n_cands;
}


/* ============================================================================
 * Batch hit detection: for each candidate, find which FB primes divide it.
 *
 * Candidate-major order: for each candidate position, scan all FB primes
 * and check if off1[i] or off2[i] matches pos % p.
 *
 * Returns total number of hit entries written.
 * ============================================================================ */
int siqs_batch_hits(
    const int32_t *candidates, int n_cand,
    const int64_t *fb, const int64_t *off1, const int64_t *off2,
    int n_fb,
    int32_t *hit_starts,    /* [n_cand + 1] output: start index per candidate */
    int32_t *hit_fb,        /* flat output: FB indices that hit each candidate */
    int max_total)
{
    int total = 0;
    for (int ci = 0; ci < n_cand; ci++) {
        hit_starts[ci] = total;
        int pos = candidates[ci];
        for (int i = 0; i < n_fb; i++) {
            int64_t o1 = off1[i];
            if (o1 < 0) continue;
            int p = (int)fb[i];
            int r = pos % p;
            if (r == (int)o1 || (off2[i] >= 0 && r == (int)off2[i])) {
                if (total < max_total)
                    hit_fb[total++] = i;
            }
        }
    }
    hit_starts[n_cand] = total;
    return total;
}


/* ============================================================================
 * Convenience: allocate sieve buffer, run sieve + find, return candidates.
 * Single entry point for Python ctypes — minimizes call overhead.
 * ============================================================================ */
int siqs_sieve_and_find(
    int sz,
    const int64_t *fb,
    const int16_t *fb_logp,
    const int64_t *off1,
    const int64_t *off2,
    int n_fb,
    int16_t threshold,
    int32_t *out_cands,
    int max_cands)
{
    int16_t *sieve = (int16_t *)malloc(sz * sizeof(int16_t));
    if (!sieve) return 0;
    int n = siqs_sieve_fast(sieve, sz, fb, fb_logp, off1, off2,
                             n_fb, threshold, out_cands, max_cands);
    free(sieve);
    return n;
}
