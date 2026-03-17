/*
 * siqs_core_c.c -- Full SIQS sieve-to-relation pipeline in C
 *
 * Moves the entire per-polynomial hot path into C:
 *   1. Sieve initialization (presieve + main sieve)
 *   2. Candidate extraction (threshold survivors)
 *   3. Sieve-informed trial division (only primes whose root matches)
 *   4. Cofactor classification (smooth / SLP / DLP via Miller-Rabin + Pollard rho)
 *   5. Relation output (x, sign, exponents, cofactor)
 *
 * Uses GMP for large integer arithmetic (polynomial evaluation, trial division).
 * Uses __int128 fast path when values fit.
 *
 * Compile:
 *   gcc -O3 -march=native -shared -fPIC -o siqs_core_c.so siqs_core_c.c -lgmp -lm
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <gmp.h>

/* ============================================================================
 * Internal helpers: 64-bit and 128-bit arithmetic
 * ============================================================================ */

typedef unsigned __int128 u128;
typedef __int128 s128;

static inline uint64_t mulmod64(uint64_t a, uint64_t b, uint64_t m) {
    return (uint64_t)(((u128)a * (u128)b) % (u128)m);
}

static inline uint64_t addmod64(uint64_t a, uint64_t b, uint64_t m) {
    uint64_t r = a + b;
    if (r >= m || r < a) r -= m;
    return r;
}

static uint64_t gcd64(uint64_t a, uint64_t b) {
    while (b) { uint64_t t = b; b = a % b; a = t; }
    return a;
}

/* ============================================================================
 * Miller-Rabin primality test (deterministic for < 3.317e24)
 * ============================================================================ */
static int miller_rabin_64(uint64_t n) {
    if (n < 2) return 0;
    if (n == 2 || n == 3 || n == 5 || n == 7) return 1;
    if (n % 2 == 0 || n % 3 == 0 || n % 5 == 0) return 0;
    if (n < 49) return 1;

    uint64_t d = n - 1;
    int r = __builtin_ctzll(d);
    d >>= r;

    static const uint64_t witnesses[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37};
    for (int w = 0; w < 12; w++) {
        uint64_t a = witnesses[w];
        if (a >= n) continue;

        uint64_t x = 1, base = a % n, exp = d;
        while (exp > 0) {
            if (exp & 1) x = mulmod64(x, base, n);
            base = mulmod64(base, base, n);
            exp >>= 1;
        }

        if (x == 1 || x == n - 1) continue;

        int composite = 1;
        for (int i = 0; i < r - 1; i++) {
            x = mulmod64(x, x, n);
            if (x == n - 1) { composite = 0; break; }
        }
        if (composite) return 0;
    }
    return 1;
}

/* ============================================================================
 * Pollard rho for DLP cofactor splitting (inline, 64-bit)
 * ============================================================================ */
static uint64_t pollard_rho_64(uint64_t n, int limit) {
    if (n <= 1) return 0;
    if ((n & 1) == 0) return 2;
    if (n % 3 == 0) return 3;
    if (n % 5 == 0) return 5;
    if (n % 7 == 0) return 7;

    static const uint64_t c_vals[] = {1, 3, 5, 7, 11, 13};
    for (int ci = 0; ci < 6; ci++) {
        uint64_t c = c_vals[ci];
        uint64_t y = 2, x = 2, ys = 2, q = 1, g = 1;
        int rr = 1, k, iters = 0;

        while (g == 1 && iters < limit) {
            x = y;
            for (int i = 0; i < rr && iters < limit; i++) {
                y = addmod64(mulmod64(y, y, n), c, n);
                iters++;
            }
            k = 0;
            while (k < rr && g == 1 && iters < limit) {
                ys = y;
                int batch = rr - k;
                if (batch > 128) batch = 128;
                q = 1;
                for (int i = 0; i < batch && iters < limit; i++) {
                    y = addmod64(mulmod64(y, y, n), c, n);
                    uint64_t diff = x > y ? x - y : y - x;
                    if (diff == 0) { iters++; continue; }
                    q = mulmod64(q, diff, n);
                    iters++;
                }
                if (q == 0) { g = n; break; }
                g = gcd64(q, n);
                k += batch;
            }
            rr *= 2;
        }
        if (g == n) {
            g = 1;
            for (int i = 0; i < 200 && g == 1; i++) {
                ys = addmod64(mulmod64(ys, ys, n), c, n);
                uint64_t diff = x > ys ? x - ys : ys - x;
                g = gcd64(diff, n);
            }
        }
        if (g > 1 && g < n) return g;
    }
    return 0;
}

/* ============================================================================
 * Sieve one polynomial: presieve + main sieve
 * ============================================================================ */
static void do_sieve(
    int16_t *sieve, int sz,
    const int32_t *fb, const int16_t *fb_logp,
    const int32_t *off1, const int32_t *off2,
    int n_fb)
{
    /* Phase 1: Presieve pattern for primes 2,3,5,7 (period 210) */
    int16_t pattern[210];
    memset(pattern, 0, sizeof(pattern));
    for (int i = 0; i < n_fb; i++) {
        int p = fb[i];
        if (p > 7) break;
        int16_t lp = fb_logp[i];
        if (off1[i] >= 0) {
            for (int j = off1[i] % p; j < 210; j += p)
                pattern[j] += lp;
        }
        if (off2[i] >= 0 && off2[i] != off1[i]) {
            for (int j = off2[i] % p; j < 210; j += p)
                pattern[j] += lp;
        }
    }
    int pos = 0;
    int full = sz / 210;
    for (int c = 0; c < full; c++) {
        memcpy(sieve + pos, pattern, 210 * sizeof(int16_t));
        pos += 210;
    }
    if (sz - pos > 0)
        memcpy(sieve + pos, pattern, (sz - pos) * sizeof(int16_t));

    /* Phase 2: Primes 11-31 */
    for (int i = 0; i < n_fb; i++) {
        int p = fb[i];
        if (p <= 7) continue;
        if (p >= 32) break;
        int16_t lp = fb_logp[i];
        if (off1[i] >= 0)
            for (int j = off1[i]; j < sz; j += p) sieve[j] += lp;
        if (off2[i] >= 0 && off2[i] != off1[i])
            for (int j = off2[i]; j < sz; j += p) sieve[j] += lp;
    }

    /* Phase 3: Primes >= 32, interleaved double-root */
    for (int i = 0; i < n_fb; i++) {
        int p = fb[i];
        if (p < 32) continue;
        int16_t lp = fb_logp[i];
        int o1 = off1[i], o2 = off2[i];

        if (o1 >= 0 && o2 >= 0 && o2 != o1) {
            int j1 = o1, j2 = o2;
            if (j1 > j2) { int t = j1; j1 = j2; j2 = t; }
            while (j2 < sz) {
                sieve[j1] += lp;
                sieve[j2] += lp;
                j1 += p; j2 += p;
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
 * MAIN: Sieve one polynomial and extract all relations.
 *
 * Relation types in rel_type[]:
 *   0 = smooth (cofactor == 1)
 *   1 = single large prime (cofactor = the prime)
 *   2 = double large prime (cofactor = lp1, rel_cofactor2 = lp2)
 *   3 = direct factor found (rel_x stores sieve_pos, Python recomputes)
 *
 * Returns: number of relations found
 * ============================================================================ */
int siqs_sieve_and_extract(
    /* Factor base */
    const int32_t *fb_primes,
    const int16_t *fb_logs,
    const int32_t *roots1,
    const int32_t *roots2,
    int fb_size,
    /* Sieve params */
    int M,
    int16_t threshold,
    /* Polynomial coefficients as decimal strings */
    const char *a_str,
    const char *b_str,
    const char *n_str,
    int64_t lp_bound,
    /* a-prime FB indices */
    const int32_t *a_prime_indices,
    int n_a_primes,
    /* Output buffers */
    int32_t *rel_x,
    int8_t  *rel_type,
    int8_t  *rel_sign,
    int16_t *rel_exps,
    int64_t *rel_cofactor,
    int64_t *rel_cofactor2,
    int max_rels,
    /* Workspace */
    int16_t *sieve_buf,
    int32_t *cand_buf
)
{
    int sz = 2 * M;
    int n_rels = 0;

    /* Parse polynomial coefficients once (GMP) */
    mpz_t a_mp, b_mp, n_mp;
    mpz_init(a_mp); mpz_init(b_mp); mpz_init(n_mp);
    mpz_set_str(a_mp, a_str, 10);
    mpz_set_str(b_mp, b_str, 10);
    mpz_set_str(n_mp, n_str, 10);

    /* Precompute c = (b^2 - n) / a */
    mpz_t c_mp, two_b;
    mpz_init(c_mp); mpz_init(two_b);
    mpz_mul(c_mp, b_mp, b_mp);
    mpz_sub(c_mp, c_mp, n_mp);
    mpz_tdiv_q(c_mp, c_mp, a_mp);
    mpz_mul_2exp(two_b, b_mp, 1);

    /* Check if g(x) computation can use __int128 fast path.
     * g(x) = a*x^2 + 2*b*x + c.  At max x=M:
     *   |a*M^2| ~ 2^(bits_a + 2*bits_M)
     *   |2*b*M| ~ 2^(bits_b + bits_M + 1)
     * For 69d: a~85b, M~3M -> bits_M=22, so a*M^2 ~ 85+44=129 bits.
     * We need signed 128-bit, so the fast path works up to ~60d.
     * For larger, we use GMP. */
    int bits_a = (int)mpz_sizeinbase(a_mp, 2);
    int bits_M = 0;
    { int t = M; while (t > 0) { bits_M++; t >>= 1; } }
    int use_int128 = (bits_a + 2 * bits_M + 2 < 126);

    /* Extract int64 values of a, b, c for the fast path */
    int64_t a_i64 = 0, b_i64 = 0, c_i64 = 0;
    /* Always extract for ax+b computation (used for x_stored) */
    int a_fits = mpz_fits_slong_p(a_mp);
    int b_fits = mpz_fits_slong_p(b_mp);
    int c_fits = mpz_fits_slong_p(c_mp);
    if (a_fits) a_i64 = mpz_get_si(a_mp);
    if (b_fits) b_i64 = mpz_get_si(b_mp);
    if (c_fits) c_i64 = mpz_get_si(c_mp);

    /* GMP temporaries (only init once, reuse across candidates) */
    mpz_t gx_mp, cof_mp, tmp_mp, ax_b_mp;
    mpz_init(gx_mp); mpz_init(cof_mp);
    mpz_init(tmp_mp); mpz_init(ax_b_mp);

    /* ---- Step 1: Sieve ---- */
    memset(sieve_buf, 0, sz * sizeof(int16_t));
    do_sieve(sieve_buf, sz, fb_primes, fb_logs, roots1, roots2, fb_size);

    /* ---- Step 2: Find candidates above threshold ---- */
    int max_cands = max_rels * 20;
    if (max_cands > sz) max_cands = sz;
    int n_cand = 0;

    /* Unrolled 4x for throughput */
    int i;
    for (i = 0; i + 3 < sz && n_cand < max_cands - 3; i += 4) {
        if (sieve_buf[i]   >= threshold) cand_buf[n_cand++] = i;
        if (sieve_buf[i+1] >= threshold) cand_buf[n_cand++] = i+1;
        if (sieve_buf[i+2] >= threshold) cand_buf[n_cand++] = i+2;
        if (sieve_buf[i+3] >= threshold) cand_buf[n_cand++] = i+3;
    }
    for (; i < sz && n_cand < max_cands; i++) {
        if (sieve_buf[i] >= threshold) cand_buf[n_cand++] = i;
    }

    if (n_cand == 0) goto cleanup;

    /* Precompute lp_bound^2 for DLP range check */
    uint64_t lp_bound_u = (uint64_t)lp_bound;
    u128 lp_bound_sq128 = (u128)lp_bound_u * (u128)lp_bound_u;

    /* ---- Step 3+4+5: Trial division + cofactor classification ---- */
    for (int ci = 0; ci < n_cand && n_rels < max_rels; ci++) {
        int sieve_pos = cand_buf[ci];
        int x = sieve_pos - M;

        /* ---- Compute g(x) = a*x^2 + 2*b*x + c ---- */
        int8_t sign;
        /* We always need a GMP or u128 value of |g(x)| for trial division */

        if (use_int128 && a_fits && b_fits && c_fits) {
            /* Fast path: __int128 arithmetic */
            s128 gx128 = (s128)a_i64 * (s128)x * (s128)x
                       + (s128)(2 * b_i64) * (s128)x
                       + (s128)c_i64;

            if (gx128 == 0) {
                /* Direct factor check */
                mpz_set_si(ax_b_mp, (long)x);
                mpz_mul(ax_b_mp, ax_b_mp, a_mp);
                mpz_add(ax_b_mp, ax_b_mp, b_mp);
                mpz_gcd(tmp_mp, ax_b_mp, n_mp);
                if (mpz_cmp_ui(tmp_mp, 1) > 0 && mpz_cmp(tmp_mp, n_mp) < 0) {
                    int16_t *exps = rel_exps + (int64_t)n_rels * fb_size;
                    memset(exps, 0, fb_size * sizeof(int16_t));
                    rel_type[n_rels] = 3;
                    rel_x[n_rels] = sieve_pos;
                    rel_sign[n_rels] = 0;
                    rel_cofactor[n_rels] = 0;
                    rel_cofactor2[n_rels] = 0;
                    n_rels++;
                }
                continue;
            }

            sign = (gx128 < 0) ? 1 : 0;
            u128 abs_gx;
            if (gx128 < 0)
                abs_gx = (u128)(-gx128);
            else
                abs_gx = (u128)gx128;

            /* Convert to GMP for trial division (needed for large cofactors) */
            /* Split u128 into high64:low64 */
            uint64_t lo = (uint64_t)abs_gx;
            uint64_t hi = (uint64_t)(abs_gx >> 64);
            if (hi == 0) {
                mpz_set_ui(cof_mp, lo);
            } else {
                mpz_set_ui(cof_mp, hi);
                mpz_mul_2exp(cof_mp, cof_mp, 64);
                mpz_add_ui(cof_mp, cof_mp, lo);
            }
        } else {
            /* GMP path for large coefficients */
            mpz_set_si(gx_mp, (long)x);
            mpz_mul_si(gx_mp, gx_mp, (long)x);
            mpz_mul(gx_mp, gx_mp, a_mp);
            mpz_set_si(tmp_mp, (long)x);
            mpz_mul(tmp_mp, tmp_mp, two_b);
            mpz_add(gx_mp, gx_mp, tmp_mp);
            mpz_add(gx_mp, gx_mp, c_mp);

            if (mpz_sgn(gx_mp) == 0) {
                mpz_set_si(ax_b_mp, (long)x);
                mpz_mul(ax_b_mp, ax_b_mp, a_mp);
                mpz_add(ax_b_mp, ax_b_mp, b_mp);
                mpz_gcd(tmp_mp, ax_b_mp, n_mp);
                if (mpz_cmp_ui(tmp_mp, 1) > 0 && mpz_cmp(tmp_mp, n_mp) < 0) {
                    int16_t *exps = rel_exps + (int64_t)n_rels * fb_size;
                    memset(exps, 0, fb_size * sizeof(int16_t));
                    rel_type[n_rels] = 3;
                    rel_x[n_rels] = sieve_pos;
                    rel_sign[n_rels] = 0;
                    rel_cofactor[n_rels] = 0;
                    rel_cofactor2[n_rels] = 0;
                    n_rels++;
                }
                continue;
            }

            sign = (mpz_sgn(gx_mp) < 0) ? 1 : 0;
            mpz_abs(cof_mp, gx_mp);
        }

        /* ---- Sieve-informed trial division ----
         * Only trial-divide by FB primes whose sieve root matches this position.
         * This cuts TD from O(fb_size) to O(~20-30 primes per candidate). */
        int16_t *exps = rel_exps + (int64_t)n_rels * fb_size;
        memset(exps, 0, fb_size * sizeof(int16_t));

        /* Track if cofactor still fits in uint64 for fast-path division */
        int cof_is_u64 = mpz_fits_ulong_p(cof_mp);
        uint64_t cof_u64 = cof_is_u64 ? mpz_get_ui(cof_mp) : 0;

        for (int fi = 0; fi < fb_size; fi++) {
            int32_t p = fb_primes[fi];
            int32_t o1 = roots1[fi];
            if (o1 < 0) continue;

            /* Check if this prime's sieve root matches the candidate position */
            int r = sieve_pos % p;
            if (r != o1 && (roots2[fi] < 0 || r != roots2[fi]))
                continue;

            /* This prime hits -- divide it out */
            if (cof_is_u64) {
                /* Fast path: native uint64 division */
                uint64_t up = (uint64_t)p;
                if (cof_u64 % up == 0) {
                    int e = 0;
                    do { cof_u64 /= up; e++; } while (cof_u64 % up == 0);
                    exps[fi] = (int16_t)e;
                    if (cof_u64 == 1) {
                        mpz_set_ui(cof_mp, 1);
                        break;
                    }
                }
            } else {
                /* GMP path */
                unsigned long pul = (unsigned long)p;
                if (mpz_divisible_ui_p(cof_mp, pul)) {
                    int e = 0;
                    do {
                        mpz_divexact_ui(cof_mp, cof_mp, pul);
                        e++;
                    } while (mpz_divisible_ui_p(cof_mp, pul));
                    exps[fi] = (int16_t)e;
                    /* Check if it now fits in u64 */
                    if (mpz_fits_ulong_p(cof_mp)) {
                        cof_is_u64 = 1;
                        cof_u64 = mpz_get_ui(cof_mp);
                    }
                    if (mpz_cmp_ui(cof_mp, 1) == 0) break;
                }
            }
        }

        /* Sync cof_mp from cof_u64 if needed */
        if (cof_is_u64) mpz_set_ui(cof_mp, cof_u64);

        /* Add a-prime contributions */
        for (int j = 0; j < n_a_primes; j++) {
            exps[a_prime_indices[j]] += 1;
        }

        /* Store sieve position for Python to recompute ax+b mod n */
        rel_x[n_rels] = sieve_pos;
        rel_sign[n_rels] = sign;

        /* ---- Cofactor classification ---- */
        if (cof_is_u64 && cof_u64 == 1) {
            /* Fully smooth */
            rel_type[n_rels] = 0;
            rel_cofactor[n_rels] = 1;
            rel_cofactor2[n_rels] = 0;
            n_rels++;
        }
        else if (cof_is_u64 && cof_u64 < lp_bound_u) {
            /* Possible single large prime */
            if (miller_rabin_64(cof_u64)) {
                rel_type[n_rels] = 1;
                rel_cofactor[n_rels] = (int64_t)cof_u64;
                rel_cofactor2[n_rels] = 0;
                n_rels++;
            }
        }
        else if (cof_is_u64 && (u128)cof_u64 < lp_bound_sq128 && cof_u64 > 1) {
            /* Possible double large prime */
            if (miller_rabin_64(cof_u64)) {
                /* Prime but > lp_bound -- skip (can't use as single LP) */
            }
            else {
                /* Try to split into two large primes */
                uint64_t lp1 = 0, lp2 = 0;

                /* Perfect square check */
                uint64_t sq = (uint64_t)sqrt((double)cof_u64);
                while ((u128)sq * sq > cof_u64) sq--;
                while ((u128)(sq+1) * (sq+1) <= cof_u64) sq++;

                if (sq * sq == cof_u64 && miller_rabin_64(sq)) {
                    lp1 = lp2 = sq;
                } else {
                    /* Quick trial by small primes */
                    static const uint32_t sp[] = {
                        2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,
                        73,79,83,89,97,101,103,107,109,113
                    };
                    for (int s = 0; s < 30; s++) {
                        if (cof_u64 % sp[s] == 0) {
                            lp1 = sp[s];
                            lp2 = cof_u64 / lp1;
                            break;
                        }
                    }
                    if (lp1 == 0) {
                        /* Pollard rho */
                        lp1 = pollard_rho_64(cof_u64, 200);
                        if (lp1 > 1 && lp1 < cof_u64)
                            lp2 = cof_u64 / lp1;
                    }
                }

                if (lp1 > 1 && lp2 > 1 &&
                    lp1 < lp_bound_u && lp2 < lp_bound_u &&
                    miller_rabin_64(lp1) && miller_rabin_64(lp2))
                {
                    rel_type[n_rels] = 2;
                    rel_cofactor[n_rels] = (int64_t)lp1;
                    rel_cofactor2[n_rels] = (int64_t)lp2;
                    n_rels++;
                }
            }
        }
        else if (!cof_is_u64) {
            /* GMP fallback for very large cofactors */
            /* Check if < lp_bound (SLP candidate) */
            if (mpz_cmp_ui(cof_mp, lp_bound_u) < 0) {
                if (mpz_probab_prime_p(cof_mp, 15) > 0) {
                    rel_type[n_rels] = 1;
                    rel_cofactor[n_rels] = mpz_get_si(cof_mp);
                    rel_cofactor2[n_rels] = 0;
                    n_rels++;
                }
            }
            /* DLP with GMP: rare, skip for performance */
        }
    }

cleanup:
    mpz_clear(a_mp); mpz_clear(b_mp); mpz_clear(n_mp);
    mpz_clear(c_mp); mpz_clear(two_b);
    mpz_clear(gx_mp); mpz_clear(cof_mp);
    mpz_clear(tmp_mp); mpz_clear(ax_b_mp);

    return n_rels;
}
