/*
 * Pythagorean Tree Heuristic Search — C Engine
 *
 * Fast single-path + beam search on (m,n) Pythagorean tree.
 * 12 moves per node: 9 forward + 3 inverse.
 *
 * Heuristic: quad_res — min(N mod v / v, N mod v² / v²) across derived values.
 * Plus coprime check: gcd(v*(v+1) mod N, N).
 *
 * Goal: maximize nodes/sec while maintaining heuristic quality.
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef unsigned __int128 u128;
typedef uint64_t u64;
typedef int64_t  i64;

/* ---- GCD ---- */
static u64 gcd64(u64 a, u64 b) {
    while (b) { u64 t = b; b = a % b; a = t; }
    return a;
}

/* ---- 2x2 Matrix on (m,n) ---- */
typedef struct { int a00, a01, a10, a11; } Mat2;

static const Mat2 FORWARD[9] = {
    {2, -1, 1, 0},   /* B1 */
    {2,  1, 1, 0},   /* B2 */
    {1,  2, 0, 1},   /* B3 */
    {1,  1, 0, 2},   /* P1 */
    {2,  0, 1, -1},  /* P2 */
    {2,  0, 1,  1},  /* P3 */
    {3, -2, 1, -1},  /* F1 */
    {3,  2, 1,  1},  /* F2 */
    {1,  4, 0,  1},  /* F3 */
};

static const Mat2 INVERSE[3] = {
    {0,  1, -1, 2},  /* B1_inv */
    {0,  1,  1, -2}, /* B2_inv */
    {1, -2,  0,  1}, /* B3_inv */
};

#define N_FORWARD 9
#define N_INVERSE 3
#define N_MOVES 12

static inline void apply_mat(const Mat2 *M, i64 m, i64 n, i64 *m2, i64 *n2) {
    *m2 = (i64)M->a00 * m + (i64)M->a01 * n;
    *n2 = (i64)M->a10 * m + (i64)M->a11 * n;
}

static inline int valid_mn(i64 m, i64 n) {
    return m > 0 && n >= 0 && m > n;
}

/* ---- Derived values ---- */
#define MAX_VALS 9

static int derived_values(i64 m, i64 n, u64 *vals) {
    if (m <= 0 || n < 0 || m <= n) return 0;
    u64 um = (u64)m, un = (u64)n;
    u64 a = um*um - un*un;
    u64 b = 2*um*un;
    u64 c = um*um + un*un;
    u64 d = um - un;
    u64 s = um + un;
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

/* ---- Check factor ---- */
static u64 check_factor(u64 N, i64 m, i64 n) {
    u64 vals[MAX_VALS];
    int nv = derived_values(m, n, vals);
    for (int i = 0; i < nv; i++) {
        u64 g = gcd64(vals[i], N);
        if (g > 1 && g < N) return g;
    }
    return 0;
}

/* ---- Heuristic: quad_res + coprime ---- */
/* Returns score * 1e9 as integer (lower = better). Returns 0 if factor found. */
static u64 heuristic_score(u64 N, i64 m, i64 n) {
    u64 vals[MAX_VALS];
    int nv = derived_values(m, n, vals);
    if (nv == 0) return 1000000000ULL;

    double best = 1.0;
    for (int i = 0; i < nv; i++) {
        u64 v = vals[i];
        if (v <= 1) continue;

        /* Linear scent */
        u64 r = N % v;
        u64 near = r < v - r ? r : v - r;
        double s1 = (double)near / (double)v;

        /* Quadratic scent: N mod v² */
        u128 v2 = (u128)v * v;
        if (v2 > 1 && v2 < N) {
            u64 v2_64 = (u64)v2;
            u64 r2 = N % v2_64;
            u64 near2 = r2 < v2_64 - r2 ? r2 : v2_64 - r2;
            double s2 = (double)near2 / (double)v2_64;
            double sq = s2 * 0.8;
            if (sq < s1) s1 = sq;
        }

        if (s1 < best) best = s1;

        /* Coprime consecutive product check */
        u128 prod = (u128)v * (v + 1);
        u64 pm = (u64)(prod % N);
        u64 g = gcd64(pm, N);
        if (g > 1 && g < N) return 0;  /* found factor! */
    }

    return (u64)(best * 1e9);
}

/* ---- Hash table for visited set ---- */
typedef struct {
    u64 *keys;   /* packed (m << 32) | n */
    int capacity;
    int count;
} HashSet;

static void hs_init(HashSet *hs, int cap) {
    hs->capacity = cap;
    hs->count = 0;
    hs->keys = (u64 *)calloc(cap, sizeof(u64));
}

static void hs_free(HashSet *hs) {
    free(hs->keys);
}

#define HS_EMPTY 0xFFFFFFFFFFFFFFFFULL

static void hs_init_empty(HashSet *hs) {
    memset(hs->keys, 0xFF, hs->capacity * sizeof(u64));
}

static inline u64 pack_mn(i64 m, i64 n) {
    /* Pack into u64 — assumes m,n fit in 32 bits */
    return ((u64)(uint32_t)m << 32) | (u64)(uint32_t)n;
}

static inline int hs_contains(HashSet *hs, u64 key) {
    u64 h = key * 0x9E3779B97F4A7C15ULL;
    int idx = (int)(h % (u64)hs->capacity);
    for (int probe = 0; probe < 64; probe++) {
        u64 k = hs->keys[idx];
        if (k == key) return 1;
        if (k == HS_EMPTY) return 0;
        idx = (idx + 1) % hs->capacity;
    }
    return 0;
}

static inline int hs_insert(HashSet *hs, u64 key) {
    if (hs->count * 4 >= hs->capacity * 3) return 0;  /* 75% load */
    u64 h = key * 0x9E3779B97F4A7C15ULL;
    int idx = (int)(h % (u64)hs->capacity);
    for (int probe = 0; probe < 64; probe++) {
        u64 k = hs->keys[idx];
        if (k == key) return 0;  /* already present */
        if (k == HS_EMPTY) {
            hs->keys[idx] = key;
            hs->count++;
            return 1;
        }
        idx = (idx + 1) % hs->capacity;
    }
    return 0;
}

/* ---- Beam node ---- */
typedef struct {
    i64 m, n;
    u64 score;
} BeamNode;

static int cmp_beam(const void *a, const void *b) {
    u64 sa = ((const BeamNode *)a)->score;
    u64 sb = ((const BeamNode *)b)->score;
    if (sa < sb) return -1;
    if (sa > sb) return 1;
    return 0;
}

/* ---- PRNG (xoshiro256**) ---- */
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

/* ==== MAIN SEARCH: beam_restart with batch GCD ==== */
u64 pyth_beam_restart(
    u64 N,
    int beam_width,
    int max_steps,
    int time_limit_ms,
    int restart_patience,
    u64 seed,
    int *nodes_out,
    int *restarts_out
) {
    struct timespec t0, now;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    rng_seed(seed);

    /* Hash table for visited nodes */
    int hs_cap = beam_width * max_steps * 2;
    if (hs_cap < 100000) hs_cap = 100000;
    if (hs_cap > 50000000) hs_cap = 50000000;
    HashSet visited;
    hs_init(&visited, hs_cap);
    hs_init_empty(&visited);

    /* Beam arrays */
    int cand_cap = beam_width * N_MOVES + 100;
    BeamNode *beam = (BeamNode *)malloc(beam_width * sizeof(BeamNode));
    BeamNode *cands = (BeamNode *)malloc(cand_cap * sizeof(BeamNode));

    /* Init with root */
    i64 rm = 2, rn = 1;
    u64 rf = check_factor(N, rm, rn);
    if (rf) { *nodes_out = 1; *restarts_out = 0; free(beam); free(cands); hs_free(&visited); return rf; }

    beam[0].m = rm; beam[0].n = rn;
    beam[0].score = heuristic_score(N, rm, rn);
    int beam_len = 1;
    hs_insert(&visited, pack_mn(rm, rn));

    int total_nodes = 1;
    int restarts = 0;
    u64 best_ever = beam[0].score;
    int stale = 0;

    /* Batch GCD accumulator — Pollard-rho style */
    u64 accum = 1;
    int accum_count = 0;
    #define BATCH_GCD_SIZE 500

    for (int step = 0; step < max_steps; step++) {
        /* Time check every 64 steps */
        if ((step & 63) == 0) {
            clock_gettime(CLOCK_MONOTONIC, &now);
            long elapsed_ms = (now.tv_sec - t0.tv_sec) * 1000 + (now.tv_nsec - t0.tv_nsec) / 1000000;
            if (elapsed_ms >= time_limit_ms) break;
        }

        /* Expand beam */
        int ncand = 0;
        for (int bi = 0; bi < beam_len; bi++) {
            i64 bm = beam[bi].m, bn = beam[bi].n;
            for (int mi = 0; mi < N_MOVES; mi++) {
                const Mat2 *M = mi < N_FORWARD ? &FORWARD[mi] : &INVERSE[mi - N_FORWARD];
                i64 m2, n2;
                apply_mat(M, bm, bn, &m2, &n2);
                if (!valid_mn(m2, n2)) continue;

                u64 pk = pack_mn(m2, n2);
                if (hs_contains(&visited, pk)) continue;
                if (!hs_insert(&visited, pk)) continue;  /* hash table full */

                total_nodes++;

                /* Check for factor */
                u64 f = check_factor(N, m2, n2);
                if (f > 0) {
                    *nodes_out = total_nodes;
                    *restarts_out = restarts;
                    free(beam); free(cands); hs_free(&visited);
                    return f;
                }

                /* Batch GCD accumulation */
                {
                    u64 bvals[MAX_VALS];
                    int bnv = derived_values(m2, n2, bvals);
                    for (int bi2 = 0; bi2 < bnv; bi2++) {
                        u64 bv = bvals[bi2];
                        if (bv > 1) {
                            u128 p128 = (u128)accum * (bv % N);
                            accum = (u64)(p128 % N);
                            accum_count++;
                        }
                    }
                    if (accum_count >= BATCH_GCD_SIZE) {
                        u64 g = gcd64(accum, N);
                        if (g > 1 && g < N) {
                            *nodes_out = total_nodes;
                            *restarts_out = restarts;
                            free(beam); free(cands); hs_free(&visited);
                            return g;
                        }
                        accum = 1;
                        accum_count = 0;
                    }
                }

                /* Score */
                u64 sc = heuristic_score(N, m2, n2);
                if (sc == 0) {
                    /* heuristic found factor via coprime check */
                    /* Verify */
                    u64 vals[MAX_VALS];
                    int nv = derived_values(m2, n2, vals);
                    for (int j = 0; j < nv; j++) {
                        u64 v = vals[j];
                        if (v > 1) {
                            u128 prod = (u128)v * (v + 1);
                            u64 pm = (u64)(prod % N);
                            u64 g = gcd64(pm, N);
                            if (g > 1 && g < N) {
                                *nodes_out = total_nodes;
                                *restarts_out = restarts;
                                free(beam); free(cands); hs_free(&visited);
                                return g;
                            }
                        }
                    }
                    sc = 1;  /* false alarm */
                }

                if (ncand < cand_cap) {
                    cands[ncand].m = m2;
                    cands[ncand].n = n2;
                    cands[ncand].score = sc;
                    ncand++;
                }
            }
        }

        if (ncand == 0 || stale >= restart_patience) {
            /* Restart: clear visited set + random walk from root */
            hs_init_empty(&visited);
            visited.count = 0;

            i64 wm = 2, wn = 1;
            int depth = 8 + (int)(rng_next() % 28);
            for (int d = 0; d < depth; d++) {
                int mi = (int)(rng_next() % N_FORWARD);
                i64 nm, nn;
                apply_mat(&FORWARD[mi], wm, wn, &nm, &nn);
                if (valid_mn(nm, nn)) { wm = nm; wn = nn; }
            }
            beam[0].m = wm; beam[0].n = wn;
            beam[0].score = heuristic_score(N, wm, wn);
            beam_len = 1;
            hs_insert(&visited, pack_mn(wm, wn));
            total_nodes++;
            stale = 0;
            best_ever = beam[0].score;
            restarts++;
            continue;
        }

        /* Sort and select top beam_width */
        qsort(cands, ncand, sizeof(BeamNode), cmp_beam);
        beam_len = ncand < beam_width ? ncand : beam_width;
        memcpy(beam, cands, beam_len * sizeof(BeamNode));

        /* Track staleness */
        if (beam[0].score < best_ever) {
            best_ever = beam[0].score;
            stale = 0;
        } else {
            stale++;
        }
    }

    *nodes_out = total_nodes;
    *restarts_out = restarts;
    free(beam); free(cands); hs_free(&visited);
    return 0;
}

/* ==== GREEDY with restarts ==== */
u64 pyth_greedy_restart(
    u64 N,
    int max_steps,
    int time_limit_ms,
    int restart_patience,
    u64 seed,
    int *nodes_out,
    int *restarts_out
) {
    struct timespec t0, now;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    rng_seed(seed);

    int total_nodes = 0;
    int restarts = 0;
    i64 m = 2, n = 1;
    u64 best_ever = 1000000000ULL;
    int stale = 0;

    /* Visited set */
    int hs_cap = max_steps * 2;
    if (hs_cap < 100000) hs_cap = 100000;
    if (hs_cap > 50000000) hs_cap = 50000000;
    HashSet visited;
    hs_init(&visited, hs_cap);
    hs_init_empty(&visited);
    hs_insert(&visited, pack_mn(m, n));

    u64 rf = check_factor(N, m, n);
    if (rf) { *nodes_out = 1; *restarts_out = 0; hs_free(&visited); return rf; }
    total_nodes = 1;

    for (int step = 0; step < max_steps; step++) {
        if ((step & 63) == 0) {
            clock_gettime(CLOCK_MONOTONIC, &now);
            long elapsed_ms = (now.tv_sec - t0.tv_sec) * 1000 + (now.tv_nsec - t0.tv_nsec) / 1000000;
            if (elapsed_ms >= time_limit_ms) break;
        }

        u64 best_score = 2000000000ULL;
        i64 best_m = 0, best_n = 0;
        int found_any = 0;

        for (int mi = 0; mi < N_MOVES; mi++) {
            const Mat2 *M = mi < N_FORWARD ? &FORWARD[mi] : &INVERSE[mi - N_FORWARD];
            i64 m2, n2;
            apply_mat(M, m, n, &m2, &n2);
            if (!valid_mn(m2, n2)) continue;

            u64 pk = pack_mn(m2, n2);
            if (hs_contains(&visited, pk)) continue;

            total_nodes++;
            u64 f = check_factor(N, m2, n2);
            if (f > 0) { *nodes_out = total_nodes; *restarts_out = restarts; hs_free(&visited); return f; }

            u64 sc = heuristic_score(N, m2, n2);
            if (sc == 0) {
                /* Coprime hit — verify */
                u64 vals[MAX_VALS];
                int nv = derived_values(m2, n2, vals);
                for (int j = 0; j < nv; j++) {
                    u64 v = vals[j];
                    if (v > 1) {
                        u128 prod = (u128)v * (v + 1);
                        u64 pm = (u64)(prod % N);
                        u64 g = gcd64(pm, N);
                        if (g > 1 && g < N) { *nodes_out = total_nodes; *restarts_out = restarts; hs_free(&visited); return g; }
                    }
                }
                sc = 1;
            }

            if (sc < best_score) {
                best_score = sc;
                best_m = m2;
                best_n = n2;
                found_any = 1;
            }
        }

        if (!found_any || stale >= restart_patience) {
            /* Random restart — clear visited to avoid saturation */
            hs_init_empty(&visited);
            visited.count = 0;

            m = 2; n = 1;
            int depth = 5 + (int)(rng_next() % 26);
            for (int d = 0; d < depth; d++) {
                int mi = (int)(rng_next() % N_FORWARD);
                i64 nm, nn;
                apply_mat(&FORWARD[mi], m, n, &nm, &nn);
                if (valid_mn(nm, nn)) { m = nm; n = nn; }
            }
            hs_insert(&visited, pack_mn(m, n));
            total_nodes++;
            stale = 0;
            best_ever = 2000000000ULL;
            restarts++;
            continue;
        }

        m = best_m;
        n = best_n;
        hs_insert(&visited, pack_mn(m, n));

        if (best_score < best_ever) {
            best_ever = best_score;
            stale = 0;
        } else {
            stale++;
        }
    }

    *nodes_out = total_nodes;
    *restarts_out = restarts;
    hs_free(&visited);
    return 0;
}
