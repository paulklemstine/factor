
/*
 * Segmented sieve: L1-cache optimized.
 * Processes sieve in 32KB segments so all data fits in L1 cache.
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int segmented_sieve_c(
    int b_start, int b_end, int A,
    const int64_t *rat_primes, int n_rat, int64_t m,
    const int64_t *alg_primes, const int64_t *alg_roots, int n_alg,
    int rat_frac_x1000, int alg_frac_x1000,
    int poly_degree, int64_t f0_abs, int64_t fd_abs,
    int *out_a, int *out_b, int max_cands
) {
    int size = 2 * A + 1;
    int total = 0;
    double abs_m = (double)(m >= 0 ? m : -m);
    double rat_frac = rat_frac_x1000 / 1000.0;
    double alg_frac = alg_frac_x1000 / 1000.0;
    double log_f0 = (f0_abs > 0) ? log((double)f0_abs) : 0.0;
    double log_fd = (fd_abs > 0) ? log((double)fd_abs) : 0.0;
    double log_leading = (log_fd > log_f0) ? log_fd : log_f0;

    /* Segment size: 16K uint16 = 32KB, fits in L1 cache */
    const int SEG_SIZE = 16 * 1024;

    uint16_t *rat_seg = (uint16_t *)malloc(SEG_SIZE * sizeof(uint16_t));
    uint16_t *alg_seg = (uint16_t *)malloc(SEG_SIZE * sizeof(uint16_t));

    uint16_t *rat_lps = (uint16_t *)malloc(n_rat * sizeof(uint16_t));
    uint16_t *alg_lps = (uint16_t *)malloc(n_alg * sizeof(uint16_t));
    int64_t *rat_next = (int64_t *)malloc(n_rat * sizeof(int64_t));
    int64_t *alg_next = (int64_t *)malloc(n_alg * sizeof(int64_t));

    for (int i = 0; i < n_rat; i++)
        rat_lps[i] = (uint16_t)(log((double)rat_primes[i]) * 128.0 + 0.5);
    for (int i = 0; i < n_alg; i++)
        alg_lps[i] = (uint16_t)(log((double)alg_primes[i]) * 128.0 + 0.5);

    for (int b = b_start; b <= b_end && total < max_cands; b++) {
        double bm = (double)b * abs_m;
        double rat_typical = (bm > (double)A) ? bm : (double)A;
        uint16_t rat_thresh = (uint16_t)(rat_frac * log(rat_typical) * 128.0);

        double dom = ((double)A > (double)b) ? (double)A : (double)b;
        double alg_log_norm = (double)poly_degree * log(dom) + log_leading;
        uint16_t alg_thresh = (alg_log_norm > 1.0)
            ? (uint16_t)(alg_frac * alg_log_norm * 128.0) : 128;

        /* Compute global starts */
        for (int i = 0; i < n_rat; i++) {
            int64_t p = rat_primes[i];
            int64_t bm_mod = ((int64_t)b % p) * (((m % p) + p) % p) % p;
            int64_t start = ((-bm_mod % p) + p) % p;
            rat_next[i] = (start + (int64_t)A) % p;
        }
        for (int i = 0; i < n_alg; i++) {
            int64_t p = alg_primes[i];
            int64_t r = alg_roots[i];
            int64_t br_mod = ((int64_t)b % p) * ((r % p + p) % p) % p;
            int64_t start = ((-br_mod % p) + p) % p;
            alg_next[i] = (start + (int64_t)A) % p;
        }

        /* Process each segment */
        for (int seg_start = 0; seg_start < size; seg_start += SEG_SIZE) {
            int seg_end = seg_start + SEG_SIZE;
            if (seg_end > size) seg_end = size;
            int seg_len = seg_end - seg_start;

            memset(rat_seg, 0, seg_len * sizeof(uint16_t));
            memset(alg_seg, 0, seg_len * sizeof(uint16_t));

            /* Sieve rational primes in this segment */
            for (int i = 0; i < n_rat; i++) {
                int64_t p = rat_primes[i];
                uint16_t lp = rat_lps[i];
                int64_t idx = rat_next[i];
                /* Advance to segment start */
                if (idx < seg_start) {
                    int64_t skip = ((int64_t)seg_start - idx + p - 1) / p;
                    idx += skip * p;
                }
                while (idx < seg_end) {
                    rat_seg[idx - seg_start] += lp;
                    idx += p;
                }
                rat_next[i] = idx;
            }

            /* Sieve algebraic primes in this segment */
            for (int i = 0; i < n_alg; i++) {
                int64_t p = alg_primes[i];
                uint16_t lp = alg_lps[i];
                int64_t idx = alg_next[i];
                if (idx < seg_start) {
                    int64_t skip = ((int64_t)seg_start - idx + p - 1) / p;
                    idx += skip * p;
                }
                while (idx < seg_end) {
                    alg_seg[idx - seg_start] += lp;
                    idx += p;
                }
                alg_next[i] = idx;
            }

            /* Collect candidates */
            for (int j = 0; j < seg_len && total < max_cands; j++) {
                if (rat_seg[j] >= rat_thresh && alg_seg[j] >= alg_thresh) {
                    int a = (seg_start + j) - A;
                    if (a == 0) continue;
                    /* Quick coprimality check */
                    int ga = (a < 0) ? -a : a;
                    int gb = b;
                    while (gb) { int t = gb; gb = ga % gb; ga = t; }
                    if (ga != 1) continue;
                    out_a[total] = a;
                    out_b[total] = b;
                    total++;
                }
            }
        }
    }

    free(rat_seg); free(alg_seg);
    free(rat_lps); free(alg_lps);
    free(rat_next); free(alg_next);
    return total;
}
