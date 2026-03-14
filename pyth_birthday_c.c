/*
 * Pythagorean Tree — Multi-Walk Birthday Collision Factoring
 *
 * Core idea: Run K independent random walks on the Pythagorean tree mod N.
 * Each walk tracks (m, n) mod N under random matrix steps.
 * If two walks collide mod p (but not mod q), gcd(m1-m2, N) reveals a factor.
 *
 * Birthday paradox: with K walkers taking S steps each, collision probability
 * is ~(K*S)^2 / (2p). Setting K*S = O(sqrt(p)) gives constant probability.
 *
 * Detection method: Distinguished points.
 * When hash(m,n) has k leading zeros, store (m,n, walk_id, step) in a table.
 * Two walks colliding mod p will eventually hit the same distinguished point
 * (mod p), and gcd of their m-difference with N gives a factor.
 *
 * Also: accumulate pairwise products for batch GCD as a secondary method.
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef unsigned __int128 u128;
typedef uint64_t u64;
typedef int64_t  i64;
typedef uint32_t u32;

/* ---- GCD ---- */
static u64 gcd64(u64 a, u64 b) {
    while (b) { u64 t = b; b = a % b; a = t; }
    return a;
}

/* ---- Modular arithmetic helpers ---- */
static inline u64 mod_add(u64 a, u64 b, u64 N) {
    u64 s = a + b;
    return s >= N ? s - N : s;
}

static inline u64 mod_sub(u64 a, u64 b, u64 N) {
    return a >= b ? a - b : N - (b - a);
}

static inline u64 mod_mul(u64 a, u64 b, u64 N) {
    return (u64)((u128)a * b % N);
}

/* ---- 2x2 Matrix on (m,n) mod N ---- */
/* Stored as signed ints, converted to mod-N for application */
typedef struct { int a00, a01, a10, a11; } IMat;

static const IMat FORWARD_MATS[9] = {
    {2, -1, 1,  0},  /* B1: (2m-n, m)   */
    {2,  1, 1,  0},  /* B2: (2m+n, m)   */
    {1,  2, 0,  1},  /* B3: (m+2n, n)   */
    {1,  1, 0,  2},  /* P1: (m+n, 2n)   */
    {2,  0, 1, -1},  /* P2: (2m, m-n)   */
    {2,  0, 1,  1},  /* P3: (2m, m+n)   */
    {3, -2, 1, -1},  /* F1: (3m-2n, m-n) */
    {3,  2, 1,  1},  /* F2: (3m+2n, m+n) */
    {1,  4, 0,  1},  /* F3: (m+4n, n)   */
};
#define N_FWD 9

/* Apply matrix: (m', n') = M * (m, n) mod N */
static inline void mat_apply_mod(const IMat *M, u64 m, u64 n, u64 N,
                                  u64 *m_out, u64 *n_out) {
    /* Each entry: a*m + b*n mod N, where a,b are small signed ints */
    u128 r0 = 0, r1 = 0;

    /* Row 0 */
    if (M->a00 >= 0) r0 += (u128)(u64)M->a00 * m;
    else r0 += (u128)(N - (u64)(-M->a00) % N) * m;  /* (-a)*m => (N-a)*m mod N... no */

    /* Safer: compute each term mod N individually */
    u64 t00 = (M->a00 >= 0) ? mod_mul((u64)M->a00, m, N)
                             : mod_mul(N - ((u64)(-M->a00) % N), m, N);
    u64 t01 = (M->a01 >= 0) ? mod_mul((u64)M->a01, n, N)
                             : mod_mul(N - ((u64)(-M->a01) % N), n, N);
    *m_out = mod_add(t00, t01, N);

    /* Row 1 */
    u64 t10 = (M->a10 >= 0) ? mod_mul((u64)M->a10, m, N)
                             : mod_mul(N - ((u64)(-M->a10) % N), m, N);
    u64 t11 = (M->a11 >= 0) ? mod_mul((u64)M->a11, n, N)
                             : mod_mul(N - ((u64)(-M->a11) % N), n, N);
    *n_out = mod_add(t10, t11, N);
}

/* ---- PRNG: xoshiro256** (per-walk, seeded from walk_id) ---- */
typedef struct {
    u64 s[4];
} RNG;

static void rng_init(RNG *r, u64 seed) {
    r->s[0] = seed ^ 0x9E3779B97F4A7C15ULL;
    r->s[1] = seed * 0x6A09E667F3BCC908ULL + 1;
    r->s[2] = seed * 0x3C6EF372FE94F82BULL + 2;
    r->s[3] = seed * 0xBB67AE8584CAA73BULL + 3;
    /* Warmup */
    for (int i = 0; i < 8; i++) {
        u64 t = r->s[1] << 17;
        r->s[2] ^= r->s[0]; r->s[3] ^= r->s[1];
        r->s[1] ^= r->s[2]; r->s[0] ^= r->s[3];
        r->s[2] ^= t; r->s[3] = (r->s[3] << 45) | (r->s[3] >> 19);
    }
}

static inline u64 rng_next(RNG *r) {
    u64 result = r->s[1] * 5;
    result = (result << 7 | result >> 57) * 9;
    u64 t = r->s[1] << 17;
    r->s[2] ^= r->s[0]; r->s[3] ^= r->s[1];
    r->s[1] ^= r->s[2]; r->s[0] ^= r->s[3];
    r->s[2] ^= t;
    r->s[3] = (r->s[3] << 45) | (r->s[3] >> 19);
    return result;
}

/* ---- FNV-1a hash for (m, n) ---- */
static inline u64 hash_mn(u64 m, u64 n) {
    u64 h = 14695981039346656037ULL;
    /* Hash m byte by byte */
    for (int i = 0; i < 8; i++) {
        h ^= (m >> (i * 8)) & 0xFF;
        h *= 1099511628211ULL;
    }
    for (int i = 0; i < 8; i++) {
        h ^= (n >> (i * 8)) & 0xFF;
        h *= 1099511628211ULL;
    }
    return h;
}

/* ---- Distinguished Point Table ---- */
/* Stores (m, n, walk_id, step) for each distinguished point hit. */
typedef struct {
    u64 m;
    u64 n;
    u32 walk_id;
    u32 step;
} DPEntry;

typedef struct {
    DPEntry *entries;
    u64 *hashes;       /* hash(m,n) for fast lookup */
    int capacity;
    int count;
    int mask;
} DPTable;

static void dp_init(DPTable *dp, int capacity) {
    int cap = 1;
    while (cap < capacity) cap <<= 1;
    dp->entries = (DPEntry *)calloc(cap, sizeof(DPEntry));
    dp->hashes = (u64 *)calloc(cap, sizeof(u64));
    dp->capacity = cap;
    dp->count = 0;
    dp->mask = cap - 1;
}

static void dp_free(DPTable *dp) {
    free(dp->entries);
    free(dp->hashes);
}

/* Insert or find collision. Returns:
 *  0 = inserted new entry
 *  1 = collision found with SAME walk (cycle, ignore)
 *  2 = collision found with DIFFERENT walk (potential factor!)
 *      sets *coll_m, *coll_n to the colliding entry's values
 *      sets *coll_walk_id to the colliding walk
 */
static int dp_insert(DPTable *dp, u64 m, u64 n, u32 walk_id, u32 step,
                     u64 *coll_m, u64 *coll_n, u32 *coll_walk_id) {
    if (dp->count >= (dp->capacity * 3 / 4)) return 0; /* table full, skip */

    u64 h = hash_mn(m, n);
    if (h == 0) h = 1; /* reserve 0 for empty */

    int idx = (int)(h & dp->mask);
    for (int probe = 0; probe < 128; probe++) {
        u64 existing_h = dp->hashes[idx];
        if (existing_h == 0) {
            /* Empty slot — insert */
            dp->hashes[idx] = h;
            dp->entries[idx].m = m;
            dp->entries[idx].n = n;
            dp->entries[idx].walk_id = walk_id;
            dp->entries[idx].step = step;
            dp->count++;
            return 0;
        }
        if (existing_h == h &&
            dp->entries[idx].m == m &&
            dp->entries[idx].n == n) {
            /* Exact match on (m, n) mod N */
            if (dp->entries[idx].walk_id == walk_id) {
                return 1; /* same walk, cycle */
            }
            /* Different walk! Potential collision */
            *coll_m = dp->entries[idx].m;
            *coll_n = dp->entries[idx].n;
            *coll_walk_id = dp->entries[idx].walk_id;
            return 2;
        }
        idx = (idx + 1) & dp->mask;
    }
    return 0; /* too many probes, skip */
}

/* ---- Walk state ---- */
typedef struct {
    u64 m, n;      /* current position mod N */
    RNG rng;       /* per-walk RNG */
    u64 accum;     /* product accumulator for batch GCD */
    u32 walk_id;
    u32 step_count;
} Walk;

/* ---- Derived values mod N for secondary GCD checks ---- */
static int derived_mod(u64 m, u64 n, u64 N, u64 *vals) {
    u64 m2 = mod_mul(m, m, N);
    u64 n2 = mod_mul(n, n, N);
    u64 A = mod_sub(m2, n2, N);          /* m^2 - n^2 */
    u64 B = mod_mul(mod_mul(2, m, N), n, N); /* 2mn */
    u64 C = mod_add(m2, n2, N);          /* m^2 + n^2 */
    u64 d = mod_sub(m, n, N);            /* m - n */
    u64 s = mod_add(m, n, N);            /* m + n */

    int k = 0;
    vals[k++] = A;
    vals[k++] = B;
    vals[k++] = C;
    vals[k++] = m;
    vals[k++] = n;
    vals[k++] = d;
    vals[k++] = s;
    return k;
}

/* ===========================================================
 * MAIN FUNCTION: birthday_collision_factor
 *
 * Multi-walk birthday collision on the Pythagorean tree mod N.
 *
 * Parameters:
 *   N                - semiprime to factor (must fit u64)
 *   num_walks        - number of independent walks (K)
 *   steps_per_walk   - max steps per walk (S)
 *   dp_bits          - distinguished point threshold: point is "distinguished"
 *                      if hash(m,n) has dp_bits leading zeros (lower = more DPs)
 *   seed             - random seed
 *   total_steps      - output: total steps taken across all walks
 *   dp_count         - output: total distinguished points stored
 *   collision_count  - output: total collisions detected (same + different walk)
 *
 * Returns: factor of N if found, 0 otherwise.
 * ===========================================================
 */
u64 birthday_collision_factor(
    u64 N,
    int num_walks,
    u64 steps_per_walk,
    int dp_bits,
    u64 seed,
    int time_limit_ms,
    u64 *total_steps,
    int *dp_count_out,
    int *collision_count_out
) {
    struct timespec t0, now;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    /* Distinguished point mask: hash & mask == 0 means distinguished */
    u64 dp_mask = ((u64)1 << dp_bits) - 1;

    /* Allocate walk states */
    Walk *walks = (Walk *)calloc(num_walks, sizeof(Walk));
    for (int i = 0; i < num_walks; i++) {
        walks[i].walk_id = (u32)i;
        walks[i].step_count = 0;
        walks[i].accum = 1;
        rng_init(&walks[i].rng, seed + (u64)i * 0x9E3779B97F4A7C15ULL);
        /* Random starting point: random walk from (2,1) for a few steps */
        u64 m = 2, n = 1;
        int warmup = 5 + (int)(rng_next(&walks[i].rng) % 20);
        for (int j = 0; j < warmup; j++) {
            int mi = (int)(rng_next(&walks[i].rng) % N_FWD);
            u64 m2, n2;
            mat_apply_mod(&FORWARD_MATS[mi], m, n, N, &m2, &n2);
            m = m2; n = n2;
        }
        walks[i].m = m;
        walks[i].n = n;
    }

    /* Distinguished point table.
     * Expected DPs: num_walks * steps_per_walk / 2^dp_bits.
     * Size table at 4x expected for low load factor. */
    u64 expected_dp = (u64)num_walks * steps_per_walk / ((u64)1 << dp_bits);
    int dp_cap = (int)(expected_dp * 4);
    if (dp_cap < 1024) dp_cap = 1024;
    if (dp_cap > 64 * 1024 * 1024) dp_cap = 64 * 1024 * 1024;
    DPTable dp;
    dp_init(&dp, dp_cap);

    u64 steps_done = 0;
    int collisions = 0;
    u64 result = 0;

    /* Cross-walk product accumulator for batch GCD */
    u64 cross_accum = 1;
    int cross_count = 0;

    /* Main loop: round-robin steps across all walks */
    for (u64 s = 0; s < steps_per_walk; s++) {
        /* Time check every 4096 steps */
        if ((s & 4095) == 0 && s > 0) {
            clock_gettime(CLOCK_MONOTONIC, &now);
            long elapsed = (now.tv_sec - t0.tv_sec) * 1000 +
                          (now.tv_nsec - t0.tv_nsec) / 1000000;
            if (elapsed >= time_limit_ms) break;
        }

        for (int w = 0; w < num_walks; w++) {
            Walk *wk = &walks[w];

            /* Choose random matrix and step */
            int mi = (int)(rng_next(&wk->rng) % N_FWD);
            u64 m2, n2;
            mat_apply_mod(&FORWARD_MATS[mi], wk->m, wk->n, N, &m2, &n2);
            wk->m = m2;
            wk->n = n2;
            wk->step_count++;
            steps_done++;

            /* Quick direct GCD checks on derived values */
            u64 vals[7];
            int nv = derived_mod(m2, n2, N, vals);
            for (int i = 0; i < nv; i++) {
                u64 v = vals[i];
                if (v == 0 || v == N) continue;
                u64 g = gcd64(v, N);
                if (g > 1 && g < N) {
                    result = g;
                    goto done;
                }
            }

            /* Accumulate product for per-walk batch GCD */
            if (m2 != 0 && m2 != N) {
                wk->accum = mod_mul(wk->accum, m2, N);
            }

            /* Per-walk batch GCD every 256 steps */
            if ((wk->step_count & 255) == 0) {
                u64 g = gcd64(wk->accum, N);
                if (g > 1 && g < N) {
                    result = g;
                    goto done;
                }
                wk->accum = 1;
            }

            /* Check if this is a distinguished point */
            u64 h = hash_mn(m2, n2);
            if ((h & dp_mask) == 0) {
                u64 cm, cn;
                u32 cw;
                int r = dp_insert(&dp, m2, n2, (u32)w, wk->step_count,
                                  &cm, &cn, &cw);
                if (r == 2) {
                    /* Collision between walk w and walk cw! */
                    collisions++;

                    /* Try gcd of differences */
                    u64 dm = mod_sub(m2, cm, N);
                    u64 dn = mod_sub(n2, cn, N);

                    if (dm != 0) {
                        u64 g = gcd64(dm, N);
                        if (g > 1 && g < N) {
                            result = g;
                            goto done;
                        }
                    }
                    if (dn != 0) {
                        u64 g = gcd64(dn, N);
                        if (g > 1 && g < N) {
                            result = g;
                            goto done;
                        }
                    }

                    /* Try derived value differences */
                    u64 vals2[7];
                    int nv2 = derived_mod(cm, cn, N, vals2);
                    for (int i = 0; i < nv && i < nv2; i++) {
                        u64 diff = mod_sub(vals[i], vals2[i], N);
                        if (diff != 0) {
                            u64 g = gcd64(diff, N);
                            if (g > 1 && g < N) {
                                result = g;
                                goto done;
                            }
                        }
                    }
                } else if (r == 1) {
                    /* Same walk cycle — detected but not useful for factoring */
                }
            }

            /* Cross-walk product: accumulate m values from all walks */
            if (m2 != 0 && m2 != N) {
                cross_accum = mod_mul(cross_accum, m2, N);
                cross_count++;
                if (cross_count >= 512) {
                    u64 g = gcd64(cross_accum, N);
                    if (g > 1 && g < N) {
                        result = g;
                        goto done;
                    }
                    cross_accum = 1;
                    cross_count = 0;
                }
            }
        }

        /* Pairwise difference GCD every 1024 steps */
        if ((s & 1023) == 0 && s > 0) {
            for (int i = 0; i < num_walks && i < 32; i++) {
                for (int j = i + 1; j < num_walks && j < 32; j++) {
                    u64 dm = mod_sub(walks[i].m, walks[j].m, N);
                    u64 dn = mod_sub(walks[i].n, walks[j].n, N);
                    if (dm != 0) {
                        u64 g = gcd64(dm, N);
                        if (g > 1 && g < N) { result = g; goto done; }
                    }
                    if (dn != 0) {
                        u64 g = gcd64(dn, N);
                        if (g > 1 && g < N) { result = g; goto done; }
                    }
                    /* Also check m*n derived product diffs */
                    u64 p1 = mod_mul(walks[i].m, walks[i].n, N);
                    u64 p2 = mod_mul(walks[j].m, walks[j].n, N);
                    u64 dp2 = mod_sub(p1, p2, N);
                    if (dp2 != 0) {
                        u64 g = gcd64(dp2, N);
                        if (g > 1 && g < N) { result = g; goto done; }
                    }
                }
            }
        }
    }

done:
    *total_steps = steps_done;
    *dp_count_out = dp.count;
    *collision_count_out = collisions;

    free(walks);
    dp_free(&dp);
    return result;
}


/* ===========================================================
 * VARIANT 2: Pollard-rho style with single deterministic walk function
 *
 * Instead of random matrix choice per step, use the current (m,n) to
 * deterministically choose the next matrix. This makes the walk a
 * pseudo-random function, enabling Floyd/Brent cycle detection and
 * ensuring walks that collide mod p stay synchronized.
 *
 * This is the "proper" Pollard-rho adaptation to the Pythagorean tree.
 * ===========================================================
 */

/* Deterministic step: choose matrix based on current state */
static inline void det_step(u64 m, u64 n, u64 N, u64 *m_out, u64 *n_out) {
    /* Use m mod 9 to pick matrix — deterministic from state */
    int mi = (int)(m % N_FWD);
    mat_apply_mod(&FORWARD_MATS[mi], m, n, N, m_out, n_out);
}

/* Pollard-rho style: Brent's cycle detection with multi-walk */
u64 birthday_rho_factor(
    u64 N,
    int num_walks,
    u64 max_steps,
    u64 seed,
    int time_limit_ms,
    u64 *total_steps
) {
    struct timespec t0, now;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    u64 steps_done = 0;
    u64 result = 0;

    for (int w = 0; w < num_walks; w++) {
        /* Each walk starts from a different random point */
        RNG rng;
        rng_init(&rng, seed + (u64)w * 0xBB67AE8584CAA73BULL);

        u64 m = 2, n = 1;
        int warmup = 5 + (int)(rng_next(&rng) % 30);
        for (int j = 0; j < warmup; j++) {
            int mi = (int)(rng_next(&rng) % N_FWD);
            mat_apply_mod(&FORWARD_MATS[mi], m, n, N, &m, &n);
        }

        /* Brent's algorithm */
        u64 tort_m = m, tort_n = n;
        u64 hare_m = m, hare_n = n;
        u64 power = 1, lam = 0;
        u64 accum = 1;
        int accum_count = 0;

        u64 steps_per = max_steps / (u64)num_walks;
        if (steps_per < 1000) steps_per = 1000;

        for (u64 s = 0; s < steps_per; s++) {
            /* Time check */
            if ((s & 8191) == 0 && s > 0) {
                clock_gettime(CLOCK_MONOTONIC, &now);
                long elapsed = (now.tv_sec - t0.tv_sec) * 1000 +
                              (now.tv_nsec - t0.tv_nsec) / 1000000;
                if (elapsed >= time_limit_ms) goto rho_done;
            }

            /* Advance hare one deterministic step */
            u64 hm2, hn2;
            det_step(hare_m, hare_n, N, &hm2, &hn2);
            hare_m = hm2; hare_n = hn2;
            steps_done++;
            lam++;

            /* Accumulate difference between hare and tortoise */
            u64 dm = mod_sub(hare_m, tort_m, N);
            u64 dn = mod_sub(hare_n, tort_n, N);

            if (dm != 0) {
                accum = mod_mul(accum, dm, N);
                accum_count++;
            }
            if (dn != 0) {
                accum = mod_mul(accum, dn, N);
                accum_count++;
            }

            /* Batch GCD every 128 accumulated values */
            if (accum_count >= 128) {
                u64 g = gcd64(accum, N);
                if (g > 1 && g < N) {
                    result = g;
                    goto rho_done;
                }
                if (g == N) {
                    /* Overshot — backtrack: recompute step by step */
                    u64 bt_m = tort_m, bt_n = tort_n;
                    for (u64 bs = 0; bs < lam; bs++) {
                        u64 bm2, bn2;
                        det_step(bt_m, bt_n, N, &bm2, &bn2);
                        bt_m = bm2; bt_n = bn2;
                        u64 d = mod_sub(bt_m, tort_m, N);
                        if (d != 0) {
                            g = gcd64(d, N);
                            if (g > 1 && g < N) {
                                result = g;
                                goto rho_done;
                            }
                        }
                    }
                }
                accum = 1;
                accum_count = 0;
            }

            /* Brent's power-of-2 update */
            if (lam == power) {
                tort_m = hare_m;
                tort_n = hare_n;
                power <<= 1;
                lam = 0;
                /* Also flush accumulator at power boundary */
                if (accum_count > 0) {
                    u64 g = gcd64(accum, N);
                    if (g > 1 && g < N) {
                        result = g;
                        goto rho_done;
                    }
                    accum = 1;
                    accum_count = 0;
                }
            }
        }
    }

rho_done:
    *total_steps = steps_done;
    return result;
}


/* ===========================================================
 * VARIANT 3: Multi-walk with additive combination
 *
 * Run K walks. Periodically, for each pair (i,j), compute
 * gcd(m_i - m_j, N). With K walks, there are K*(K-1)/2 pairs,
 * so the birthday effect is strong.
 *
 * Optimized: accumulate the product of all pairwise (m_i - m_j)
 * and do a single GCD per round.
 * ===========================================================
 */
u64 birthday_multi_gcd(
    u64 N,
    int num_walks,
    u64 max_steps,
    u64 seed,
    int time_limit_ms,
    u64 *total_steps
) {
    struct timespec t0, now;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    if (num_walks < 2) num_walks = 2;
    if (num_walks > 4096) num_walks = 4096;

    /* Allocate walk states */
    u64 *wm = (u64 *)calloc(num_walks, sizeof(u64));
    u64 *wn = (u64 *)calloc(num_walks, sizeof(u64));
    RNG *rngs = (RNG *)calloc(num_walks, sizeof(RNG));

    for (int i = 0; i < num_walks; i++) {
        rng_init(&rngs[i], seed + (u64)i * 0x517CC1B727220A95ULL);
        u64 m = 2, n = 1;
        int warmup = 3 + (int)(rng_next(&rngs[i]) % 25);
        for (int j = 0; j < warmup; j++) {
            int mi = (int)(rng_next(&rngs[i]) % N_FWD);
            mat_apply_mod(&FORWARD_MATS[mi], m, n, N, &m, &n);
        }
        wm[i] = m;
        wn[i] = n;
    }

    u64 steps_done = 0;
    u64 result = 0;

    /* Steps per walk */
    u64 spw = max_steps / (u64)num_walks;
    if (spw < 100) spw = 100;

    /* GCD check interval: check every `check_interval` steps.
     * Every step for accuracy; the O(K^2) pairwise is amortized. */
    int check_interval = 1;

    for (u64 s = 0; s < spw; s++) {
        /* Time check */
        if ((s & 4095) == 0 && s > 0) {
            clock_gettime(CLOCK_MONOTONIC, &now);
            long elapsed = (now.tv_sec - t0.tv_sec) * 1000 +
                          (now.tv_nsec - t0.tv_nsec) / 1000000;
            if (elapsed >= time_limit_ms) break;
        }

        /* Advance all walks one step */
        for (int w = 0; w < num_walks; w++) {
            int mi = (int)(rng_next(&rngs[w]) % N_FWD);
            u64 m2, n2;
            mat_apply_mod(&FORWARD_MATS[mi], wm[w], wn[w], N, &m2, &n2);
            wm[w] = m2;
            wn[w] = n2;
            steps_done++;
        }

        /* Pairwise GCD check via product accumulation */
        if ((s % check_interval) == 0) {
            u64 prod = 1;
            int prod_count = 0;

            for (int i = 0; i < num_walks; i++) {
                for (int j = i + 1; j < num_walks; j++) {
                    u64 dm = mod_sub(wm[i], wm[j], N);
                    if (dm != 0) {
                        prod = mod_mul(prod, dm, N);
                        prod_count++;
                    }
                    u64 dn = mod_sub(wn[i], wn[j], N);
                    if (dn != 0) {
                        prod = mod_mul(prod, dn, N);
                        prod_count++;
                    }

                    if (prod_count >= 64) {
                        u64 g = gcd64(prod, N);
                        if (g > 1 && g < N) {
                            result = g;
                            goto multi_done;
                        }
                        if (g == N) {
                            /* Overshot — check individual pairs */
                            for (int ii = 0; ii < num_walks; ii++) {
                                for (int jj = ii + 1; jj < num_walks; jj++) {
                                    u64 d = mod_sub(wm[ii], wm[jj], N);
                                    if (d != 0) {
                                        g = gcd64(d, N);
                                        if (g > 1 && g < N) {
                                            result = g;
                                            goto multi_done;
                                        }
                                    }
                                    d = mod_sub(wn[ii], wn[jj], N);
                                    if (d != 0) {
                                        g = gcd64(d, N);
                                        if (g > 1 && g < N) {
                                            result = g;
                                            goto multi_done;
                                        }
                                    }
                                }
                            }
                        }
                        prod = 1;
                        prod_count = 0;
                    }
                }
            }

            /* Flush remaining product */
            if (prod_count > 0) {
                u64 g = gcd64(prod, N);
                if (g > 1 && g < N) {
                    result = g;
                    goto multi_done;
                }
                if (g == N) {
                    /* Overshot — individual check */
                    for (int i = 0; i < num_walks; i++) {
                        for (int j = i + 1; j < num_walks; j++) {
                            u64 d = mod_sub(wm[i], wm[j], N);
                            if (d != 0) {
                                u64 g2 = gcd64(d, N);
                                if (g2 > 1 && g2 < N) {
                                    result = g2;
                                    goto multi_done;
                                }
                            }
                            d = mod_sub(wn[i], wn[j], N);
                            if (d != 0) {
                                u64 g2 = gcd64(d, N);
                                if (g2 > 1 && g2 < N) {
                                    result = g2;
                                    goto multi_done;
                                }
                            }
                        }
                    }
                }
            }
        }
    }

multi_done:
    *total_steps = steps_done;
    free(wm); free(wn); free(rngs);
    return result;
}
