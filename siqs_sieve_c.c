/*
 * siqs_sieve_c.c — Ultra-fast SIQS sieve + hit detection in C
 *
 * Compile: gcc -O3 -march=native -shared -fPIC -o siqs_sieve_c.so siqs_sieve_c.c -lm
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* ============================================================================
 * Sieve with presieve pattern for primes 2-7 (period 210), then 11-31,
 * then main sieve for primes >= 32.
 * ============================================================================ */
void siqs_sieve(
    int16_t *sieve,          /* sieve array [sz] — MUST be pre-zeroed */
    int sz,
    const int64_t *fb,       /* factor base primes [n_fb] */
    const int16_t *fb_logp,  /* log2(p)*64 [n_fb] */
    const int64_t *off1,     /* sieve offset 1 [n_fb], -1 = skip */
    const int64_t *off2,     /* sieve offset 2 [n_fb], -1 = skip */
    int n_fb
)
{
    /* Phase 1: Presieve — period-210 pattern for primes 2,3,5,7 */
    int16_t pattern[210];
    memset(pattern, 0, sizeof(pattern));
    for (int i = 0; i < n_fb; i++) {
        int p = (int)fb[i];
        if (p > 7) break;
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
    /* Tile with memcpy */
    int pos = 0;
    for (int c = sz / 210; c > 0; c--) {
        memcpy(sieve + pos, pattern, 210 * sizeof(int16_t));
        pos += 210;
    }
    if (sz - pos > 0)
        memcpy(sieve + pos, pattern, (sz - pos) * sizeof(int16_t));

    /* Phase 2: Primes 11-31 */
    for (int i = 0; i < n_fb; i++) {
        int p = (int)fb[i];
        if (p <= 7) continue;
        if (p >= 32) break;
        int16_t lp = fb_logp[i];
        if (off1[i] >= 0)
            for (int j = (int)off1[i]; j < sz; j += p) sieve[j] += lp;
        if (off2[i] >= 0 && off2[i] != off1[i])
            for (int j = (int)off2[i]; j < sz; j += p) sieve[j] += lp;
    }

    /* Phase 3: Primes >= 32 — interleaved double-root sieve */
    for (int i = 0; i < n_fb; i++) {
        int p = (int)fb[i];
        if (p < 32) continue;
        int16_t lp = fb_logp[i];
        int o1 = (int)off1[i];
        int o2 = (int)off2[i];

        if (o1 >= 0 && o2 >= 0 && o2 != o1) {
            /* Interleave both roots */
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
}


/* ============================================================================
 * Find sieve survivors (unrolled 4x)
 * ============================================================================ */
int siqs_find_survivors(
    const int16_t *sieve, int sz, int16_t threshold,
    int32_t *out, int max_out)
{
    int count = 0;
    int i;
    for (i = 0; i + 3 < sz; i += 4) {
        if (sieve[i]   >= threshold && count < max_out) out[count++] = i;
        if (sieve[i+1] >= threshold && count < max_out) out[count++] = i+1;
        if (sieve[i+2] >= threshold && count < max_out) out[count++] = i+2;
        if (sieve[i+3] >= threshold && count < max_out) out[count++] = i+3;
    }
    for (; i < sz; i++)
        if (sieve[i] >= threshold && count < max_out) out[count++] = i;
    return count;
}


/* ============================================================================
 * Batch hit detection: for each candidate, find which FB primes hit it.
 *
 * OPTIMIZATION: Instead of candidate-major order (for each cand, check all primes),
 * use prime-major order (for each prime, mark all candidates it hits).
 * This is O(sum(n_cand/p)) instead of O(n_cand * n_fb) for the mod operations.
 *
 * But the output needs to be in candidate-major order for trial division.
 * Solution: two-pass approach.
 *   Pass 1 (prime-major): for each prime, check which candidates it hits, count hits per candidate
 *   Pass 2: prefix sum to get hit_starts, then fill hit_fb in candidate order
 * ============================================================================ */
void siqs_batch_find_hits(
    const int32_t *candidates, int n_cand,
    const int64_t *fb, const int64_t *off1, const int64_t *off2,
    int n_fb,
    int32_t *hit_starts,    /* [n_cand + 1] output */
    int32_t *hit_fb,        /* flat output, max_total entries */
    int max_total,
    int32_t *out_total)
{
    /* Standard approach: candidate-major with integer mod */
    int total = 0;
    for (int ci = 0; ci < n_cand; ci++) {
        hit_starts[ci] = total;
        int pos = candidates[ci];
        for (int i = 0; i < n_fb; i++) {
            int p = (int)fb[i];
            int64_t o1 = off1[i];
            if (o1 < 0) continue;
            int r = pos % p;
            if (r == (int)o1 || (off2[i] >= 0 && r == (int)off2[i])) {
                if (total < max_total)
                    hit_fb[total++] = i;
            }
        }
    }
    hit_starts[n_cand] = total;
    *out_total = total;
}


/* ============================================================================
 * FAST batch hit detection: prime-major order
 *
 * For each FB prime p with offsets o1,o2: walk candidates checking pos%p.
 * Uses a temp buffer to accumulate hits per candidate, then compacts.
 * ============================================================================ */
void siqs_batch_find_hits_fast(
    const int32_t *candidates, int n_cand,
    const int64_t *fb, const int64_t *off1, const int64_t *off2,
    int n_fb,
    int32_t *hit_starts,    /* [n_cand + 1] output */
    int32_t *hit_fb,        /* flat output, max_total entries */
    int max_total,
    int32_t *out_total,
    /* Temp buffers provided by caller */
    int32_t *tmp_hit_counts, /* [n_cand] zeroed by caller */
    int32_t *tmp_hits        /* [n_cand * 80] flat buffer */
)
{
    int max_per_cand = 80;

    /* Pass 1: prime-major — for each prime, find which candidates it hits */
    for (int i = 0; i < n_fb; i++) {
        int p = (int)fb[i];
        int o1 = (int)off1[i];
        if (o1 < 0) continue;
        int o2v = (int)off2[i];

        for (int ci = 0; ci < n_cand; ci++) {
            int r = candidates[ci] % p;
            if (r == o1 || (o2v >= 0 && r == o2v)) {
                int slot = tmp_hit_counts[ci];
                if (slot < max_per_cand) {
                    tmp_hits[ci * max_per_cand + slot] = i;
                    tmp_hit_counts[ci] = slot + 1;
                }
            }
        }
    }

    /* Pass 2: compact into hit_starts/hit_fb */
    int total = 0;
    for (int ci = 0; ci < n_cand; ci++) {
        hit_starts[ci] = total;
        int nh = tmp_hit_counts[ci];
        for (int j = 0; j < nh && total < max_total; j++) {
            hit_fb[total++] = tmp_hits[ci * max_per_cand + j];
        }
    }
    hit_starts[n_cand] = total;
    *out_total = total;
}
