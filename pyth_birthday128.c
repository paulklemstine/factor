/*
 * Pythagorean Tree — Multi-Walk Birthday GCD Factoring (128-bit N)
 *
 * Uses Montgomery multiplication for fast 128-bit modular arithmetic.
 * Matrix entries are small (0-4), so mat_apply uses additions only.
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef unsigned __int128 u128;
typedef uint64_t u64;
typedef int64_t  i64;
typedef uint32_t u32;

/* ---- 256-bit type (4 x u64 limbs, little-endian) ---- */
typedef struct { u64 w[4]; } u256;

/* ---- Montgomery context ---- */
typedef struct {
    u128 N;       /* modulus */
    u128 Ninv;    /* -N^(-1) mod 2^128 */
    u128 R2;      /* R^2 mod N, R = 2^128 */
} MontCtx;

/* Compute N^(-1) mod 2^128 via Hensel lifting (N must be odd) */
static u128 compute_ninv(u128 N) {
    /* Start with N^(-1) mod 2 = 1 (since N is odd) */
    u128 inv = 1;
    /* Each iteration doubles the number of correct bits */
    for (int i = 0; i < 127; i++) {
        inv = inv * (2 - N * inv);  /* truncated to 128 bits automatically */
    }
    return (u128)0 - inv;  /* return -N^(-1) mod 2^128 */
}

/* Compute R^2 mod N using shift-and-subtract (done once at init) */
static u128 compute_R2(u128 N) {
    /* R = 2^128. We want 2^256 mod N. */
    /* Start with 2^128 mod N = (2^128 - N) if N < 2^128 */
    u128 r = (u128)0 - N;  /* 2^128 - N mod 2^128 = -N mod 2^128 = 2^128 mod N (since N < 2^128) */
    r %= N;  /* ensure r < N */
    /* Now square: r = r^2 mod N... but that requires mod_mul which we're trying to avoid.
     * Instead, double r 128 times: r = r * 2^128 mod N */
    for (int i = 0; i < 128; i++) {
        r <<= 1;
        if (r >= N) r -= N;
    }
    return r;
}

static void mont_init(MontCtx *ctx, u128 N) {
    ctx->N = N;
    ctx->Ninv = compute_ninv(N);
    ctx->R2 = compute_R2(N);
}

/* Convert to Montgomery form: a_bar = a * R mod N */
static inline u128 to_mont(u128 a, MontCtx *ctx);

/* Convert from Montgomery form: a = a_bar * R^(-1) mod N */
static inline u128 from_mont(u128 a_bar, MontCtx *ctx);

/* ---- Montgomery multiplication ---- */
/* Compute a_bar * b_bar * R^(-1) mod N using schoolbook 64-bit limbs */
static inline u128 mont_mul(u128 a, u128 b, MontCtx *ctx) {
    u64 a_lo = (u64)a, a_hi = (u64)(a >> 64);
    u64 b_lo = (u64)b, b_hi = (u64)(b >> 64);

    /* Schoolbook 256-bit product */
    u128 p00 = (u128)a_lo * b_lo;
    u128 p01 = (u128)a_lo * b_hi;
    u128 p10 = (u128)a_hi * b_lo;
    u128 p11 = (u128)a_hi * b_hi;

    /* Assemble into 4 limbs */
    u64 T0 = (u64)p00;
    u128 carry = (p00 >> 64) + (u64)p01 + (u64)p10;
    u64 T1 = (u64)carry;
    carry = (carry >> 64) + (p01 >> 64) + (p10 >> 64) + (u64)p11;
    u64 T2 = (u64)carry;
    u64 T3 = (u64)(carry >> 64) + (u64)(p11 >> 64);

    /* Montgomery reduction: m = T_lo * (-N^{-1}) mod R */
    u128 T_lo = ((u128)T1 << 64) | T0;
    u128 m = T_lo * ctx->Ninv;  /* truncated to 128 bits = mod R */

    /* Compute m * N (256-bit) */
    u64 m_lo = (u64)m, m_hi = (u64)(m >> 64);
    u64 n_lo = (u64)ctx->N, n_hi = (u64)(ctx->N >> 64);

    u128 q00 = (u128)m_lo * n_lo;
    u128 q01 = (u128)m_lo * n_hi;
    u128 q10 = (u128)m_hi * n_lo;
    u128 q11 = (u128)m_hi * n_hi;

    /* Add T + m*N, only need upper 128 bits (lower 128 are 0 by construction) */
    /* Process limb 0: T0 + q00_lo → carry only */
    u128 c = (u128)T0 + (u64)q00;
    /* Limb 1: T1 + q00_hi + q01_lo + q10_lo + carry */
    c = (c >> 64) + (u128)T1 + (q00 >> 64) + (u64)q01 + (u64)q10;
    /* Limb 2 (first result limb): T2 + q01_hi + q10_hi + q11_lo + carry */
    c = (c >> 64) + (u128)T2 + (q01 >> 64) + (q10 >> 64) + (u64)q11;
    u64 r0 = (u64)c;
    /* Limb 3: T3 + q11_hi + carry */
    c = (c >> 64) + (u128)T3 + (q11 >> 64);
    u64 r1 = (u64)c;

    u128 result = ((u128)r1 << 64) | r0;
    if (result >= ctx->N) result -= ctx->N;
    return result;
}

/* Convert to Montgomery form using precomputed R^2 */
static inline u128 to_mont(u128 a, MontCtx *ctx) {
    return mont_mul(a % ctx->N, ctx->R2, ctx);
}

/* Convert from Montgomery form */
static inline u128 from_mont(u128 a_bar, MontCtx *ctx) {
    /* mont_mul(a_bar, 1) = a_bar * 1 * R^(-1) mod N = a */
    /* Implement as reduction of a_bar (256-bit with high 128 = 0) */
    u64 T0 = (u64)a_bar, T1 = (u64)(a_bar >> 64);
    u128 T_lo = a_bar;
    u128 m = T_lo * ctx->Ninv;

    u64 m_lo = (u64)m, m_hi = (u64)(m >> 64);
    u64 n_lo = (u64)ctx->N, n_hi = (u64)(ctx->N >> 64);

    u128 q00 = (u128)m_lo * n_lo;
    u128 q01 = (u128)m_lo * n_hi;
    u128 q10 = (u128)m_hi * n_lo;
    u128 q11 = (u128)m_hi * n_hi;

    u128 c = (u128)T0 + (u64)q00;
    c = (c >> 64) + (u128)T1 + (q00 >> 64) + (u64)q01 + (u64)q10;
    c = (c >> 64) + (q01 >> 64) + (q10 >> 64) + (u64)q11;
    u64 r0 = (u64)c;
    c = (c >> 64) + (q11 >> 64);
    u64 r1 = (u64)c;

    u128 result = ((u128)r1 << 64) | r0;
    if (result >= ctx->N) result -= ctx->N;
    return result;
}

/* ---- GCD for 128-bit ---- */
static u128 gcd128(u128 a, u128 b) {
    while (b) { u128 t = b; b = a % b; a = t; }
    return a;
}

/* ---- Modular add/sub (plain, not Montgomery) ---- */
static inline u128 mod_add(u128 a, u128 b, u128 N) {
    u128 s = a + b;
    return s >= N ? s - N : s;
}

static inline u128 mod_sub(u128 a, u128 b, u128 N) {
    return a >= b ? a - b : N - (b - a);
}

/* ---- 2x2 Matrix ---- */
typedef struct { int a00, a01, a10, a11; } IMat;

static const IMat FORWARD_MATS[9] = {
    {2, -1, 1,  0},
    {2,  1, 1,  0},
    {1,  2, 0,  1},
    {1,  1, 0,  2},
    {2,  0, 1, -1},
    {2,  0, 1,  1},
    {3, -2, 1, -1},
    {3,  2, 1,  1},
    {1,  4, 0,  1},
};
#define N_FWD 9

/* Small coefficient multiply using additions only (max coeff = 4) */
static inline u128 small_mul_mod(int coeff, u128 val, u128 N) {
    if (coeff == 0) return 0;
    if (coeff == 1) return val;
    if (coeff == 2) return mod_add(val, val, N);
    if (coeff == 3) return mod_add(mod_add(val, val, N), val, N);
    if (coeff == 4) { u128 d = mod_add(val, val, N); return mod_add(d, d, N); }
    if (coeff == -1) return val == 0 ? 0 : N - val;
    if (coeff == -2) { u128 d = mod_add(val, val, N); return d == 0 ? 0 : N - d; }
    return 0; /* unreachable for our matrices */
}

static inline void mat_apply_fast(const IMat *M, u128 m, u128 n, u128 N,
                                   u128 *m_out, u128 *n_out) {
    *m_out = mod_add(small_mul_mod(M->a00, m, N), small_mul_mod(M->a01, n, N), N);
    *n_out = mod_add(small_mul_mod(M->a10, m, N), small_mul_mod(M->a11, n, N), N);
}

/* ---- PRNG ---- */
typedef struct { u64 s[4]; } RNG;

static void rng_init(RNG *r, u64 seed) {
    r->s[0] = seed ^ 0x9E3779B97F4A7C15ULL;
    r->s[1] = seed * 0x6A09E667F3BCC908ULL + 1;
    r->s[2] = seed * 0x3C6EF372FE94F82BULL + 2;
    r->s[3] = seed * 0xBB67AE8584CAA73BULL + 3;
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

/* ===========================================================
 * birthday_multi_gcd_128 — Montgomery-accelerated
 * ===========================================================
 */
int birthday_multi_gcd_128(
    u64 N_hi, u64 N_lo,
    int num_walks,
    u64 max_rounds,
    u64 seed,
    int time_limit_ms,
    u64 *total_steps,
    u64 *factor_hi,
    u64 *factor_lo
) {
    struct timespec t0, now;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    u128 N = ((u128)N_hi << 64) | (u128)N_lo;

    /* N must be odd for Montgomery (semiprimes are always odd) */
    if ((N & 1) == 0) {
        *factor_hi = 0; *factor_lo = 2;
        *total_steps = 0;
        return 1;
    }

    /* Initialize Montgomery context */
    MontCtx mc;
    mont_init(&mc, N);

    if (num_walks < 2) num_walks = 2;
    if (num_walks > 4096) num_walks = 4096;

    u128 *wm = (u128 *)calloc(num_walks, sizeof(u128));
    u128 *wn = (u128 *)calloc(num_walks, sizeof(u128));
    RNG *rngs = (RNG *)calloc(num_walks, sizeof(RNG));

    /* Initialize walks in Montgomery form.
     * small_mul_mod (additions only) is correct for Montgomery values.
     * Differences of Montgomery values are Montgomery differences.
     * gcd(a*R mod N, N) = gcd(a, N) for odd N — no conversion needed. */
    for (int i = 0; i < num_walks; i++) {
        rng_init(&rngs[i], seed + (u64)i * 0x517CC1B727220A95ULL);
        u128 m = 2, n = 1;
        int warmup = 3 + (int)(rng_next(&rngs[i]) % 25);
        for (int j = 0; j < warmup; j++) {
            int mi = (int)(rng_next(&rngs[i]) % N_FWD);
            mat_apply_fast(&FORWARD_MATS[mi], m, n, N, &m, &n);
        }
        /* Convert to Montgomery form (once per walk) */
        wm[i] = to_mont(m, &mc);
        wn[i] = to_mont(n, &mc);
    }

    u64 steps_done = 0;
    int found = 0;
    u128 result_factor = 0;

    /* Montgomery form of 1 for product init */
    u128 mont_one = to_mont(1, &mc);

    for (u64 s = 0; s < max_rounds; s++) {
        if ((s & 255) == 0 && s > 0) {
            clock_gettime(CLOCK_MONOTONIC, &now);
            long elapsed = (now.tv_sec - t0.tv_sec) * 1000 +
                          (now.tv_nsec - t0.tv_nsec) / 1000000;
            if (elapsed >= time_limit_ms) break;
        }

        /* Advance all walks (small_mul_mod = additions, correct in Montgomery) */
        for (int w = 0; w < num_walks; w++) {
            int mi = (int)(rng_next(&rngs[w]) % N_FWD);
            u128 m2, n2;
            mat_apply_fast(&FORWARD_MATS[mi], wm[w], wn[w], N, &m2, &n2);
            wm[w] = m2;
            wn[w] = n2;
            steps_done++;
        }

        /* Pairwise GCD via Montgomery product accumulation.
         * Differences are already Montgomery form → direct mont_mul.
         * gcd(prod_mont, N) = gcd(prod, N) since gcd(R, N)=1 for odd N. */
        u128 prod = mont_one;
        int prod_count = 0;

        for (int i = 0; i < num_walks; i++) {
            for (int j = i + 1; j < num_walks; j++) {
                u128 dm = mod_sub(wm[i], wm[j], N);
                if (dm != 0) {
                    prod = mont_mul(prod, dm, &mc);
                    prod_count++;
                }
                u128 dn = mod_sub(wn[i], wn[j], N);
                if (dn != 0) {
                    prod = mont_mul(prod, dn, &mc);
                    prod_count++;
                }

                if (prod_count >= 32) {
                    u128 g = gcd128(prod, N);
                    if (g > 1 && g < N) {
                        result_factor = g;
                        found = 1;
                        goto done128;
                    }
                    if (g == N) {
                        /* Overshot — check individual pairs */
                        for (int ii = 0; ii < num_walks; ii++) {
                            for (int jj = ii + 1; jj < num_walks; jj++) {
                                u128 d = mod_sub(wm[ii], wm[jj], N);
                                if (d != 0) {
                                    g = gcd128(d, N);
                                    if (g > 1 && g < N) {
                                        result_factor = g;
                                        found = 1;
                                        goto done128;
                                    }
                                }
                                d = mod_sub(wn[ii], wn[jj], N);
                                if (d != 0) {
                                    g = gcd128(d, N);
                                    if (g > 1 && g < N) {
                                        result_factor = g;
                                        found = 1;
                                        goto done128;
                                    }
                                }
                            }
                        }
                    }
                    prod = mont_one;
                    prod_count = 0;
                }
            }
        }

        if (prod_count > 0) {
            u128 g = gcd128(prod, N);
            if (g > 1 && g < N) {
                result_factor = g;
                found = 1;
                goto done128;
            }
            if (g == N) {
                for (int i = 0; i < num_walks; i++) {
                    for (int j = i + 1; j < num_walks; j++) {
                        u128 d = mod_sub(wm[i], wm[j], N);
                        if (d != 0) {
                            u128 g2 = gcd128(d, N);
                            if (g2 > 1 && g2 < N) {
                                result_factor = g2;
                                found = 1;
                                goto done128;
                            }
                        }
                        d = mod_sub(wn[i], wn[j], N);
                        if (d != 0) {
                            u128 g2 = gcd128(d, N);
                            if (g2 > 1 && g2 < N) {
                                result_factor = g2;
                                found = 1;
                                goto done128;
                            }
                        }
                    }
                }
            }
        }
    }

done128:
    *total_steps = steps_done;
    *factor_hi = (u64)(result_factor >> 64);
    *factor_lo = (u64)result_factor;

    free(wm); free(wn); free(rngs);
    return found;
}
