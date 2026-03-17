
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

/*
 * Batch trial division for SIQS.
 *
 * For each candidate: given value v and list of FB prime indices that
 * are "hits" (from sieve), trial divide v by those primes and return
 * the exponent for each prime + the remaining cofactor.
 *
 * Operates on 64-bit values (sufficient for cofactors after partial
 * sieve-informed division — the original value is multi-precision but
 * after dividing out large primes, the cofactor fits in 64 bits).
 *
 * For values > 64 bits: use __int128 intermediate path.
 */

typedef struct {
    int64_t cofactor;  /* remaining cofactor after division */
    int16_t exps[80];  /* exponents for up to 80 hit primes */
    int n_exps;        /* actual number of hits processed */
} td_result_t;

/* Trial divide one candidate against its hit primes.
 * fb: full factor base array
 * hits: array of FB indices that are hits for this candidate
 * n_hits: number of hits
 * val_lo, val_hi: 128-bit value as two 64-bit halves (lo + hi*2^64)
 * result: output structure
 */
void trial_divide_one(const int64_t *fb, const int32_t *hits, int n_hits,
                       uint64_t val_lo, uint64_t val_hi,
                       int64_t *out_exps, int64_t *out_cofactor)
{
    /* Use __int128 for the value */
    __uint128_t v = ((__uint128_t)val_hi << 64) | val_lo;

    int exp_idx = 0;
    for (int i = 0; i < n_hits; i++) {
        int64_t p = fb[hits[i]];
        if (p <= 0) { out_exps[i] = 0; continue; }
        if (v <= 1) { out_exps[i] = 0; continue; }

        __uint128_t q = v / p;
        __uint128_t r = v - q * p;

        if (r == 0) {
            int e = 1;
            v = q;
            q = v / p; r = v - q * p;
            while (r == 0) {
                e++;
                v = q;
                q = v / p; r = v - q * p;
            }
            out_exps[i] = e;
        } else {
            out_exps[i] = 0;
        }
    }

    /* Return cofactor as 64-bit (truncated if > 64 bits) */
    *out_cofactor = (int64_t)(v & 0xFFFFFFFFFFFFFFFFULL);
}

/* Batch: process multiple candidates */
void trial_divide_batch(const int64_t *fb,
                         const int32_t *all_hits,
                         const int32_t *hit_starts,
                         const uint64_t *vals_lo,
                         const uint64_t *vals_hi,
                         int n_cands,
                         int64_t *all_exps,   /* flat: n_cands * max_hits */
                         int64_t *cofactors,
                         int max_hits)
{
    for (int ci = 0; ci < n_cands; ci++) {
        int h_start = hit_starts[ci];
        int h_end = hit_starts[ci + 1];
        int n_hits = h_end - h_start;
        if (n_hits > max_hits) n_hits = max_hits;

        trial_divide_one(fb, all_hits + h_start, n_hits,
                         vals_lo[ci], vals_hi[ci],
                         all_exps + ci * max_hits,
                         cofactors + ci);
    }
}
