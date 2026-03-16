/*
 * siqs_poly_c.c — SIQS polynomial setup and root computation in C
 *
 * Replaces the ~16% Python overhead for polynomial initialization:
 *   1. B_j computation (GMP for large integers)
 *   2. a_inv mod p precomputation for all FB primes
 *   3. B_j mod p (delta) precomputation for all FB primes
 *   4. Initial sieve root computation
 *   5. Gray code polynomial switching (incremental root updates)
 *
 * Compile:
 *   gcc -O3 -march=native -shared -fPIC -o siqs_poly_c.so siqs_poly_c.c -lgmp
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <gmp.h>

/* Write mpz value as decimal into a caller-provided buffer.
 * buf must be at least bufsize bytes. Returns number of chars written
 * (excluding null terminator), or -1 if buffer too small. */
static int mpz_to_buf(char *buf, int bufsize, const mpz_t val)
{
    /* mpz_sizeinbase gives upper bound on number of digits */
    size_t ndigits = mpz_sizeinbase(val, 10) + 2; /* +2 for sign and NUL */
    if ((int)ndigits > bufsize)
        return -1;
    mpz_get_str(buf, 10, val);
    return (int)strlen(buf);
}

/* ============================================================================
 * Modular arithmetic helpers: all int64 with __int128 intermediates.
 * ============================================================================ */

/* Modular inverse: a^{-1} mod m using extended GCD. Returns 0 if gcd != 1. */
static int64_t modinv64(int64_t a, int64_t m)
{
    if (m == 1) return 0;
    a = a % m;
    if (a < 0) a += m;
    if (a == 0) return 0;

    int64_t g = m, x = 0, y = 1;
    int64_t a0 = a;
    while (a0 != 0) {
        int64_t q = g / a0;
        int64_t tmp = g - q * a0;
        g = a0; a0 = tmp;
        tmp = x - q * y;
        x = y; y = tmp;
    }
    if (g != 1) return 0;
    return x < 0 ? x + m : x;
}

/* ============================================================================
 * gray_code_switch: Update sieve offsets when flipping B_j sign.
 *
 * Only updates non-a-primes. a-prime roots must be recomputed separately.
 * ============================================================================ */
void gray_code_switch(
    const int32_t *fb_primes,     /* [fb_size] */
    int fb_size,
    const int64_t *delta_j,       /* [fb_size] */
    const int32_t *is_a_prime,    /* [fb_size] */
    int offset_dir,               /* +1 or -1 */
    int64_t *o1,                  /* in/out [fb_size] */
    int64_t *o2                   /* in/out [fb_size] */
)
{
    if (offset_dir > 0) {
        for (int i = 0; i < fb_size; i++) {
            if (is_a_prime[i]) continue;
            int64_t p = fb_primes[i];
            if (o1[i] >= 0)
                o1[i] = (o1[i] + delta_j[i]) % p;
            if (o2[i] >= 0)
                o2[i] = (o2[i] + delta_j[i]) % p;
        }
    } else {
        for (int i = 0; i < fb_size; i++) {
            if (is_a_prime[i]) continue;
            int64_t p = fb_primes[i];
            if (o1[i] >= 0)
                o1[i] = (o1[i] - delta_j[i] + p) % p;
            if (o2[i] >= 0)
                o2[i] = (o2[i] - delta_j[i] + p) % p;
        }
    }
}

/* ============================================================================
 * recompute_a_prime_roots: Recompute roots for a-primes after Gray switch.
 * ============================================================================ */
void recompute_a_prime_roots(
    const int32_t *fb_primes,
    const int32_t *a_prime_indices, /* [s] */
    int s,
    const char *b_str,
    const char *c_str,
    int64_t a_int_mod2,
    int M,
    int64_t *o1,
    int64_t *o2
)
{
    mpz_t b_mpz, c_mpz;
    mpz_init(b_mpz);
    mpz_init(c_mpz);
    mpz_set_str(b_mpz, b_str, 10);
    mpz_set_str(c_mpz, c_str, 10);

    for (int j = 0; j < s; j++) {
        int pi = a_prime_indices[j];
        int64_t p = fb_primes[pi];

        if (p == 2) {
            unsigned long c_mod2 = mpz_fdiv_ui(c_mpz, 2);
            unsigned long g1_mod2 = ((unsigned long)a_int_mod2 + c_mod2) % 2;
            o1[pi] = -1;
            o2[pi] = -1;
            if (c_mod2 == 0) {
                o1[pi] = M % 2;
                if (g1_mod2 == 0)
                    o2[pi] = (M + 1) % 2;
            } else if (g1_mod2 == 0) {
                o1[pi] = (M + 1) % 2;
            }
            continue;
        }

        unsigned long b2_mod_p = mpz_fdiv_ui(b_mpz, (unsigned long)p);
        b2_mod_p = (b2_mod_p * 2) % (unsigned long)p;
        if (b2_mod_p == 0) {
            o1[pi] = -1;
            o2[pi] = -1;
            continue;
        }
        int64_t b2_inv = modinv64((int64_t)b2_mod_p, p);
        unsigned long c_mod_p = mpz_fdiv_ui(c_mpz, (unsigned long)p);
        int64_t neg_c = p - (int64_t)c_mod_p;
        if (neg_c == p) neg_c = 0;
        int64_t r = (__int128)neg_c * b2_inv % p;
        o1[pi] = (r + M) % p;
        o2[pi] = -1;
    }

    mpz_clear(b_mpz);
    mpz_clear(c_mpz);
}

/* ============================================================================
 * full_poly_setup: Do everything for one 'a' value in a single C call.
 *
 * String outputs (b, c, B_j) are written into caller-provided buffers.
 * Each string buffer must be at least str_bufsize bytes.
 *
 * Returns 0 on success, -1 on failure.
 * ============================================================================ */
int full_poly_setup(
    const char *n_str,
    const char *a_str,
    const int32_t *a_primes,       /* primes q_j [s] */
    const int32_t *a_prime_indices,/* indices into fb [s] */
    const int32_t *sqrt_n_mod_qj,  /* sqrt(N) mod q_j [s] */
    int s,
    const int32_t *fb_primes,      /* factor base [fb_size] */
    const int32_t *sqrt_n_mod_fb,  /* sqrt(N) mod p for all FB primes [fb_size] */
    int fb_size,
    int M,
    /* Outputs (caller-allocated): */
    int64_t *a_inv_mod,            /* [fb_size] */
    int32_t *is_a_prime,           /* [fb_size] */
    int64_t *deltas,               /* [s * fb_size] */
    int64_t *o1,                   /* [fb_size] */
    int64_t *o2,                   /* [fb_size] */
    char *b_out_buf,               /* buffer for b string [str_bufsize] */
    char *c_out_buf,               /* buffer for c string [str_bufsize] */
    char *Bj_bufs,                 /* s contiguous buffers for B_j strings [s * str_bufsize] */
    int str_bufsize                /* size of each string buffer */
)
{
    mpz_t n_mpz, a_mpz, b_mpz, c_mpz, Bj_sum, A_j, A_j_inv_z, B_j, Bj2;
    mpz_init(n_mpz); mpz_init(a_mpz); mpz_init(b_mpz);
    mpz_init(c_mpz); mpz_init(Bj_sum); mpz_init(A_j);
    mpz_init(A_j_inv_z); mpz_init(B_j); mpz_init(Bj2);

    mpz_set_str(n_mpz, n_str, 10);
    mpz_set_str(a_mpz, a_str, 10);
    mpz_set_ui(Bj_sum, 0);

    /* Keep B_j values in mpz array for delta computation (avoids re-parsing) */
    mpz_t *Bj_vals = (mpz_t *)malloc(s * sizeof(mpz_t));
    if (!Bj_vals) {
        mpz_clear(n_mpz); mpz_clear(a_mpz); mpz_clear(b_mpz);
        mpz_clear(c_mpz); mpz_clear(Bj_sum); mpz_clear(A_j);
        mpz_clear(A_j_inv_z); mpz_clear(B_j); mpz_clear(Bj2);
        return -1;
    }
    for (int j = 0; j < s; j++)
        mpz_init(Bj_vals[j]);

    /* Step 1: Compute B_j values */
    for (int j = 0; j < s; j++) {
        int64_t q = a_primes[j];
        int64_t t_j = sqrt_n_mod_qj[j];

        mpz_tdiv_q_ui(A_j, a_mpz, (unsigned long)q);
        unsigned long A_j_mod_q = mpz_fdiv_ui(A_j, (unsigned long)q);
        int64_t A_j_inv = modinv64((int64_t)A_j_mod_q, q);
        if (A_j_inv == 0 && A_j_mod_q != 1) {
            for (int k = 0; k < s; k++) mpz_clear(Bj_vals[k]);
            free(Bj_vals);
            mpz_clear(n_mpz); mpz_clear(a_mpz); mpz_clear(b_mpz);
            mpz_clear(c_mpz); mpz_clear(Bj_sum); mpz_clear(A_j);
            mpz_clear(A_j_inv_z); mpz_clear(B_j); mpz_clear(Bj2);
            return -1;
        }

        mpz_set_ui(A_j_inv_z, (unsigned long)A_j_inv);
        mpz_mul(B_j, A_j, A_j_inv_z);
        mpz_mul_ui(B_j, B_j, (unsigned long)t_j);
        mpz_mod(B_j, B_j, a_mpz);

        mpz_set(Bj_vals[j], B_j);

        /* Write B_j string into caller buffer */
        char *bj_buf = Bj_bufs + (long)j * str_bufsize;
        if (mpz_to_buf(bj_buf, str_bufsize, B_j) < 0) {
            for (int k = 0; k < s; k++) mpz_clear(Bj_vals[k]);
            free(Bj_vals);
            mpz_clear(n_mpz); mpz_clear(a_mpz); mpz_clear(b_mpz);
            mpz_clear(c_mpz); mpz_clear(Bj_sum); mpz_clear(A_j);
            mpz_clear(A_j_inv_z); mpz_clear(B_j); mpz_clear(Bj2);
            return -1;
        }

        mpz_add(Bj_sum, Bj_sum, B_j);
    }

    /* b = sum(B_j) */
    mpz_set(b_mpz, Bj_sum);

    /* Check: (b^2 - n) must be divisible by a */
    mpz_mul(c_mpz, b_mpz, b_mpz);
    mpz_sub(c_mpz, c_mpz, n_mpz);
    if (!mpz_divisible_p(c_mpz, a_mpz)) {
        /* Try b = -b */
        mpz_neg(b_mpz, b_mpz);
        mpz_mul(c_mpz, b_mpz, b_mpz);
        mpz_sub(c_mpz, c_mpz, n_mpz);
        if (!mpz_divisible_p(c_mpz, a_mpz)) {
            for (int k = 0; k < s; k++) mpz_clear(Bj_vals[k]);
            free(Bj_vals);
            mpz_clear(n_mpz); mpz_clear(a_mpz); mpz_clear(b_mpz);
            mpz_clear(c_mpz); mpz_clear(Bj_sum); mpz_clear(A_j);
            mpz_clear(A_j_inv_z); mpz_clear(B_j); mpz_clear(Bj2);
            return -1;
        }
    }
    mpz_tdiv_q(c_mpz, c_mpz, a_mpz);

    mpz_to_buf(b_out_buf, str_bufsize, b_mpz);
    mpz_to_buf(c_out_buf, str_bufsize, c_mpz);

    /* Step 2: Precompute a_inv mod p */
    memset(is_a_prime, 0, fb_size * sizeof(int32_t));
    for (int j = 0; j < s; j++) {
        is_a_prime[a_prime_indices[j]] = 1;
    }
    for (int i = 0; i < fb_size; i++) {
        if (is_a_prime[i]) {
            a_inv_mod[i] = 0;
        } else {
            int64_t p = fb_primes[i];
            unsigned long a_mod_p = mpz_fdiv_ui(a_mpz, (unsigned long)p);
            a_inv_mod[i] = modinv64((int64_t)a_mod_p, p);
        }
    }

    /* Step 3: Precompute delta arrays (using mpz B_j directly, no re-parse) */
    for (int j = 0; j < s; j++) {
        mpz_mul_ui(Bj2, Bj_vals[j], 2);

        int64_t *dj = deltas + (int64_t)j * fb_size;
        for (int i = 0; i < fb_size; i++) {
            if (is_a_prime[i]) {
                dj[i] = 0;
            } else {
                int64_t p = fb_primes[i];
                unsigned long Bj2_mod_p = mpz_fdiv_ui(Bj2, (unsigned long)p);
                dj[i] = (__int128)Bj2_mod_p * a_inv_mod[i] % p;
            }
        }
    }

    /* Step 4: Compute initial sieve roots */
    int64_t a_mod2 = mpz_fdiv_ui(a_mpz, 2);
    for (int i = 0; i < fb_size; i++) {
        int64_t p = fb_primes[i];

        if (p == 2) {
            unsigned long c_mod2 = mpz_fdiv_ui(c_mpz, 2);
            unsigned long g1_mod2 = ((unsigned long)a_mod2 + c_mod2) % 2;
            o1[i] = -1;
            o2[i] = -1;
            if (c_mod2 == 0) {
                o1[i] = M % 2;
                if (g1_mod2 == 0)
                    o2[i] = (M + 1) % 2;
            } else if (g1_mod2 == 0) {
                o1[i] = (M + 1) % 2;
            }
            continue;
        }

        if (is_a_prime[i]) {
            unsigned long b2_mod_p = mpz_fdiv_ui(b_mpz, (unsigned long)p);
            b2_mod_p = (b2_mod_p * 2) % (unsigned long)p;
            if (b2_mod_p == 0) {
                o1[i] = -1;
                o2[i] = -1;
                continue;
            }
            int64_t b2_inv = modinv64((int64_t)b2_mod_p, p);
            unsigned long c_mod_p = mpz_fdiv_ui(c_mpz, (unsigned long)p);
            int64_t neg_c = p - (int64_t)c_mod_p;
            if (neg_c == p) neg_c = 0;
            int64_t r = (__int128)neg_c * b2_inv % p;
            o1[i] = (r + M) % p;
            o2[i] = -1;
            continue;
        }

        /* Regular prime: two roots */
        int64_t t = sqrt_n_mod_fb[i];
        if (t < 0) {
            o1[i] = -1;
            o2[i] = -1;
            continue;
        }
        int64_t ai = a_inv_mod[i];
        int64_t bm = (int64_t)mpz_fdiv_ui(b_mpz, (unsigned long)p);

        int64_t r1 = (__int128)ai * ((t - bm + p) % p) % p;
        int64_t r2 = (__int128)ai * ((p - t - bm + p) % p) % p;

        o1[i] = (r1 + M) % p;
        o2[i] = (r1 != r2) ? (int64_t)((r2 + M) % p) : -1;
    }

    /* Cleanup */
    for (int k = 0; k < s; k++) mpz_clear(Bj_vals[k]);
    free(Bj_vals);
    mpz_clear(n_mpz); mpz_clear(a_mpz); mpz_clear(b_mpz);
    mpz_clear(c_mpz); mpz_clear(Bj_sum); mpz_clear(A_j);
    mpz_clear(A_j_inv_z); mpz_clear(B_j); mpz_clear(Bj2);
    return 0;
}
