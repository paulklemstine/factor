/*
 * Pythagorean Tree — Fast Heuristic Search
 *
 * Key insight from experiments:
 * - At 32b+, throughput matters more than heuristic quality
 * - Feature regression found: depth + smoothness + valid_children > scent
 * - Heuristic cost must be << node expansion cost
 *
 * Strategy: FAST heuristic (no mod/gcd in scoring) + high throughput beam.
 * Scoring uses only tree-structural features + cheap residue checks.
 *
 * Also: batch GCD accumulation across ALL nodes (Pollard-rho style).
 * Product of all derived values mod N, check gcd every 1000 nodes.
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef unsigned __int128 u128;
typedef uint64_t u64;
typedef int64_t  i64;

static u64 gcd64(u64 a, u64 b) {
    while (b) { u64 t = b; b = a % b; a = t; }
    return a;
}

typedef struct { int a00, a01, a10, a11; } Mat2;

static const Mat2 FORWARD[9] = {
    {2, -1, 1, 0}, {2, 1, 1, 0}, {1, 2, 0, 1},
    {1, 1, 0, 2}, {2, 0, 1, -1}, {2, 0, 1, 1},
    {3, -2, 1, -1}, {3, 2, 1, 1}, {1, 4, 0, 1},
};
static const Mat2 INVERSE[3] = {
    {0, 1, -1, 2}, {0, 1, 1, -2}, {1, -2, 0, 1},
};
#define N_FWD 9
#define N_INV 3
#define N_MOVES 12

static inline void apply_mat(const Mat2 *M, i64 m, i64 n, i64 *m2, i64 *n2) {
    *m2 = (i64)M->a00 * m + (i64)M->a01 * n;
    *n2 = (i64)M->a10 * m + (i64)M->a11 * n;
}

static inline int valid_mn(i64 m, i64 n) {
    return m > 0 && n >= 0 && m > n;
}

#define MAX_VALS 9

static int derived_values(i64 m, i64 n, u64 *vals) {
    if (m <= 0 || n < 0 || m <= n) return 0;
    u64 um = (u64)m, un = (u64)n;
    u64 a = um*um - un*un, b = 2*um*un, c = um*um + un*un;
    u64 d = um - un, s = um + un;
    int k = 0;
    if (a > 0) vals[k++] = a;
    if (b > 0) vals[k++] = b;
    if (c > 0) vals[k++] = c;
    if (um > 0) vals[k++] = um;
    if (un > 0) vals[k++] = un;
    if (d > 0) vals[k++] = d;
    if (s > 0) vals[k++] = s;
    if (d > 0) vals[k++] = d*d;
    if (s > 0) vals[k++] = s*s;
    return k;
}

static u64 check_factor(u64 N, i64 m, i64 n) {
    u64 vals[MAX_VALS];
    int nv = derived_values(m, n, vals);
    for (int i = 0; i < nv; i++) {
        u64 g = gcd64(vals[i], N);
        if (g > 1 && g < N) return g;
    }
    return 0;
}

/* ---- FAST heuristic ----
 * Only compute: min(N mod v / v) for the CHEAPEST values (m, n, m-n, m+n).
 * Skip expensive v² and gcd checks in the scoring function.
 * Cost: ~4 divisions vs 18+ in the full heuristic.
 */
static inline u64 fast_score(u64 N, i64 m, i64 n) {
    u64 um = (u64)m, un = (u64)n;
    u64 d = um - un, s = um + un;
    u64 c = um*um + un*un;

    /* Quick scent on just 5 cheap values: m, n, d, s, c */
    double best = 1.0;
    u64 check[5] = {um, un, d, s, c};
    for (int i = 0; i < 5; i++) {
        u64 v = check[i];
        if (v <= 1) continue;
        u64 r = N % v;
        u64 near = r < v - r ? r : v - r;
        double sc = (double)near / (double)v;
        if (sc < best) best = sc;
    }
    return (u64)(best * 1e9);
}

/* ---- PRNG ---- */
static u64 rng_state[4];
static void rng_seed(u64 s) {
    rng_state[0] = s;
    rng_state[1] = s * 0x9E3779B97F4A7C15ULL + 1;
    rng_state[2] = s * 0x6A09E667F3BCC908ULL + 2;
    rng_state[3] = s * 0x3C6EF372FE94F82BULL + 3;
}
static inline u64 rng_next(void) {
    u64 result = rng_state[1] * 5;
    result = (result << 7 | result >> 57) * 9;
    u64 t = rng_state[1] << 17;
    rng_state[2] ^= rng_state[0];
    rng_state[3] ^= rng_state[1];
    rng_state[1] ^= rng_state[2];
    rng_state[0] ^= rng_state[3];
    rng_state[2] ^= t;
    rng_state[3] = (rng_state[3] << 45) | (rng_state[3] >> 19);
    return result;
}

/* ---- Beam node ---- */
typedef struct { i64 m, n; u64 score; } BeamNode;

static int cmp_beam(const void *a, const void *b) {
    u64 sa = ((const BeamNode *)a)->score;
    u64 sb = ((const BeamNode *)b)->score;
    return (sa > sb) - (sa < sb);
}

/* ==== MAIN: Fast beam + batch GCD accumulator ====
 *
 * Two-pronged attack:
 * 1. Beam search with fast_score heuristic (high throughput)
 * 2. Batch GCD accumulator: product of ALL derived values mod N
 *    Checked every batch_size nodes. This is the Pollard-rho principle:
 *    if any value ≡ 0 (mod p), the product accumulates that factor.
 */
u64 pyth_fast_beam(
    u64 N,
    int beam_width,
    int max_steps,
    int time_limit_ms,
    int restart_patience,
    int batch_gcd_size,
    u64 seed,
    int *nodes_out,
    int *restarts_out,
    int *found_via_batch
) {
    struct timespec t0, now;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    rng_seed(seed);

    int cand_cap = beam_width * N_MOVES + 100;
    BeamNode *beam = (BeamNode *)malloc(beam_width * sizeof(BeamNode));
    BeamNode *cands = (BeamNode *)malloc(cand_cap * sizeof(BeamNode));

    i64 rm = 2, rn = 1;
    u64 rf = check_factor(N, rm, rn);
    if (rf) { *nodes_out = 1; *restarts_out = 0; *found_via_batch = 0;
              free(beam); free(cands); return rf; }

    beam[0].m = rm; beam[0].n = rn;
    beam[0].score = fast_score(N, rm, rn);
    int beam_len = 1;

    int total_nodes = 1, restarts = 0;
    u64 best_ever = beam[0].score;
    int stale = 0;

    /* Batch GCD accumulator */
    u64 accum = 1;
    int accum_count = 0;
    *found_via_batch = 0;

    for (int step = 0; step < max_steps; step++) {
        if ((step & 63) == 0) {
            clock_gettime(CLOCK_MONOTONIC, &now);
            long elapsed_ms = (now.tv_sec - t0.tv_sec) * 1000 +
                              (now.tv_nsec - t0.tv_nsec) / 1000000;
            if (elapsed_ms >= time_limit_ms) break;
        }

        int ncand = 0;
        for (int bi = 0; bi < beam_len; bi++) {
            i64 bm = beam[bi].m, bn = beam[bi].n;
            for (int mi = 0; mi < N_MOVES; mi++) {
                const Mat2 *M = mi < N_FWD ? &FORWARD[mi] : &INVERSE[mi - N_FWD];
                i64 m2, n2;
                apply_mat(M, bm, bn, &m2, &n2);
                if (!valid_mn(m2, n2)) continue;

                total_nodes++;

                /* Direct factor check */
                u64 f = check_factor(N, m2, n2);
                if (f > 0) {
                    *nodes_out = total_nodes; *restarts_out = restarts;
                    free(beam); free(cands); return f;
                }

                /* Batch GCD accumulation */
                u64 vals[MAX_VALS];
                int nv = derived_values(m2, n2, vals);
                for (int vi = 0; vi < nv; vi++) {
                    u64 v = vals[vi];
                    if (v > 1) {
                        u128 p128 = (u128)accum * (v % N);
                        accum = (u64)(p128 % N);
                        accum_count++;
                    }
                }
                if (accum_count >= batch_gcd_size) {
                    u64 g = gcd64(accum, N);
                    if (g > 1 && g < N) {
                        *nodes_out = total_nodes; *restarts_out = restarts;
                        *found_via_batch = 1;
                        free(beam); free(cands); return g;
                    }
                    accum = 1;
                    accum_count = 0;
                }

                /* Score for beam selection */
                u64 sc = fast_score(N, m2, n2);
                if (ncand < cand_cap) {
                    cands[ncand].m = m2; cands[ncand].n = n2;
                    cands[ncand].score = sc; ncand++;
                }
            }
        }

        if (ncand == 0 || stale >= restart_patience) {
            /* Restart */
            i64 wm = 2, wn = 1;
            int depth = 8 + (int)(rng_next() % 28);
            for (int d = 0; d < depth; d++) {
                int mi = (int)(rng_next() % N_FWD);
                i64 nm, nn;
                apply_mat(&FORWARD[mi], wm, wn, &nm, &nn);
                if (valid_mn(nm, nn)) { wm = nm; wn = nn; }
            }
            beam[0].m = wm; beam[0].n = wn;
            beam[0].score = fast_score(N, wm, wn);
            beam_len = 1;
            stale = 0;
            best_ever = beam[0].score;
            restarts++;
            /* Don't reset accumulator — cross-restart collisions are valuable */
            continue;
        }

        qsort(cands, ncand, sizeof(BeamNode), cmp_beam);
        beam_len = ncand < beam_width ? ncand : beam_width;
        memcpy(beam, cands, beam_len * sizeof(BeamNode));

        if (beam[0].score < best_ever) {
            best_ever = beam[0].score;
            stale = 0;
        } else {
            stale++;
        }
    }

    /* Final batch check */
    if (accum_count > 0) {
        u64 g = gcd64(accum, N);
        if (g > 1 && g < N) {
            *nodes_out = total_nodes; *restarts_out = restarts;
            *found_via_batch = 1;
            free(beam); free(cands); return g;
        }
    }

    *nodes_out = total_nodes; *restarts_out = restarts;
    free(beam); free(cands);
    return 0;
}
