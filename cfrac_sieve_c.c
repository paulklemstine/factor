/*
 * CFRAC sieve C extension — fast CF recurrence + trial division
 *
 * Optimizations:
 *   - Small-prime fast path using uint64_t when cofactor fits
 *   - GMP mpz for large cofactors
 *   - Early exit when p^2 > cofactor
 *   - Binary search for cofactor-in-FB
 *
 * Compile:
 *   gcc -O3 -shared -fPIC -o cfrac_sieve_c.so cfrac_sieve_c.c -lgmp -lm
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <gmp.h>

#define MAX_FB 50000
#define MAX_RESULTS 100000

typedef struct {
    mpz_t N;
    mpz_t a0;
    mpz_t m_k;
    mpz_t d_k;
    mpz_t a_k;
    mpz_t p_prev2;
    mpz_t p_prev1;
    int step;
} cf_state_t;

static cf_state_t g_state;
static int g_initialized = 0;
static unsigned long g_fb[MAX_FB];
static int g_fb_size = 0;
static unsigned long g_lp_bound = 0;

/* Temp variables */
static mpz_t g_m_next, g_d_next, g_a_next, g_p_new;
static mpz_t g_cof, g_tmp;

/* Precomputed: index where FB primes exceed small-prime threshold */
static int g_small_prime_count = 0;  /* count of primes that fit in uint32 */

void cfrac_init(const char *N_str) {
    if (!g_initialized) {
        mpz_init(g_state.N);
        mpz_init(g_state.a0);
        mpz_init(g_state.m_k);
        mpz_init(g_state.d_k);
        mpz_init(g_state.a_k);
        mpz_init(g_state.p_prev2);
        mpz_init(g_state.p_prev1);
        mpz_init(g_m_next);
        mpz_init(g_d_next);
        mpz_init(g_a_next);
        mpz_init(g_p_new);
        mpz_init(g_cof);
        mpz_init(g_tmp);
        g_initialized = 1;
    }

    mpz_set_str(g_state.N, N_str, 10);
    mpz_sqrt(g_state.a0, g_state.N);
    mpz_set_ui(g_state.m_k, 0);
    mpz_set_ui(g_state.d_k, 1);
    mpz_set(g_state.a_k, g_state.a0);
    mpz_set_ui(g_state.p_prev2, 1);
    mpz_mod(g_state.p_prev1, g_state.a0, g_state.N);
    g_state.step = 0;
}

void cfrac_set_fb(unsigned long *fb, int fb_size, unsigned long lp_bound) {
    g_fb_size = fb_size < MAX_FB ? fb_size : MAX_FB;
    memcpy(g_fb, fb, g_fb_size * sizeof(unsigned long));
    g_lp_bound = lp_bound;

    /* Find how many primes are "small" (for uint64 fast path) */
    /* Small enough that p*p fits in uint64 and we can use % operator */
    g_small_prime_count = 0;
    for (int i = 0; i < g_fb_size; i++) {
        if (g_fb[i] < 65536) {  /* p < 2^16 so p^2 < 2^32 */
            g_small_prime_count = i + 1;
        } else {
            break;
        }
    }
}

/*
 * Trial divide using uint64_t fast path for small cofactors,
 * falling back to GMP for large ones.
 */
static inline void trial_divide(mpz_t cof, int *exps) {
    int i;

    /* Phase 1: Try to reduce using GMP until cofactor fits in uint64 */
    for (i = 0; i < g_fb_size; i++) {
        unsigned long p = g_fb[i];

        /* Early exit: p^2 > cof */
        if (mpz_fits_ulong_p(cof)) {
            unsigned long cv = mpz_get_ui(cof);
            if (p * p > cv)
                return;
            /* Switch to uint64 fast path */
            goto uint64_path;
        }

        if (mpz_divisible_ui_p(cof, p)) {
            int e = 0;
            do {
                mpz_divexact_ui(cof, cof, p);
                e++;
            } while (mpz_divisible_ui_p(cof, p));
            exps[i] = e;
            if (mpz_cmp_ui(cof, 1) == 0) return;
        }
    }
    return;

uint64_path:
    {
        /* Fast path: cofactor fits in uint64 */
        uint64_t cv = mpz_get_ui(cof);
        if (cv == 1) return;

        for (; i < g_fb_size; i++) {
            uint64_t p = g_fb[i];
            if (p * p > cv)
                break;
            if (cv % p == 0) {
                int e = 0;
                do {
                    cv /= p;
                    e++;
                } while (cv % p == 0);
                exps[i] = e;
                if (cv == 1) {
                    mpz_set_ui(cof, 1);
                    return;
                }
            }
        }
        mpz_set_ui(cof, cv);
    }
}

int cfrac_batch(int batch_size,
                int *out_step,
                int *out_sign,
                char *out_cofactor_buf, int cof_buf_size,
                int *out_exps,
                char *out_pmod_buf, int pmod_buf_size)
{
    int n_results = 0;
    int cof_offset = 0;
    int pmod_offset = 0;
    int max_results = batch_size < MAX_RESULTS ? batch_size : MAX_RESULTS;

    for (int bi = 0; bi < batch_size && n_results < max_results; bi++) {
        /* CF recurrence */
        mpz_mul(g_m_next, g_state.d_k, g_state.a_k);
        mpz_sub(g_m_next, g_m_next, g_state.m_k);

        mpz_mul(g_tmp, g_m_next, g_m_next);
        mpz_sub(g_d_next, g_state.N, g_tmp);
        mpz_tdiv_q(g_d_next, g_d_next, g_state.d_k);

        if (mpz_sgn(g_d_next) == 0) break;

        mpz_add(g_tmp, g_state.a0, g_m_next);
        mpz_tdiv_q(g_a_next, g_tmp, g_d_next);

        mpz_mul(g_p_new, g_a_next, g_state.p_prev1);
        mpz_add(g_p_new, g_p_new, g_state.p_prev2);
        mpz_mod(g_p_new, g_p_new, g_state.N);

        /* Trial divide d_{k+1} by FB */
        mpz_abs(g_cof, g_d_next);

        int *exps = out_exps + n_results * g_fb_size;
        memset(exps, 0, g_fb_size * sizeof(int));

        trial_divide(g_cof, exps);

        /* Check cofactor */
        int is_smooth = (mpz_cmp_ui(g_cof, 1) == 0);
        int is_lp = 0;
        if (!is_smooth && mpz_fits_ulong_p(g_cof)) {
            unsigned long cof_val = mpz_get_ui(g_cof);
            if (cof_val <= g_lp_bound) {
                /* Check if it's in FB (binary search) */
                int lo = 0, hi = g_fb_size - 1;
                int found_in_fb = 0;
                while (lo <= hi) {
                    int mid = (lo + hi) / 2;
                    if (g_fb[mid] == cof_val) {
                        exps[mid]++;
                        is_smooth = 1;
                        found_in_fb = 1;
                        break;
                    } else if (g_fb[mid] < cof_val) lo = mid + 1;
                    else hi = mid - 1;
                }
                if (!found_in_fb) {
                    is_lp = 1;
                }
            }
        }

        if (is_smooth || is_lp) {
            out_step[n_results] = g_state.step + bi;
            out_sign[n_results] = (g_state.step + bi) % 2 == 0 ? 1 : 0;

            char *cof_str = mpz_get_str(NULL, 10, g_cof);
            int cof_len = strlen(cof_str);
            if (cof_offset + cof_len + 1 < cof_buf_size) {
                memcpy(out_cofactor_buf + cof_offset, cof_str, cof_len + 1);
                cof_offset += cof_len + 1;
            }
            free(cof_str);

            char *pmod_str = mpz_get_str(NULL, 10, g_state.p_prev1);
            int pmod_len = strlen(pmod_str);
            if (pmod_offset + pmod_len + 1 < pmod_buf_size) {
                memcpy(out_pmod_buf + pmod_offset, pmod_str, pmod_len + 1);
                pmod_offset += pmod_len + 1;
            }
            free(pmod_str);

            n_results++;
        }

        /* Shift state */
        mpz_set(g_state.m_k, g_m_next);
        mpz_set(g_state.d_k, g_d_next);
        mpz_set(g_state.a_k, g_a_next);
        mpz_set(g_state.p_prev2, g_state.p_prev1);
        mpz_set(g_state.p_prev1, g_p_new);
    }

    g_state.step += batch_size;
    return n_results;
}

int cfrac_get_step(void) {
    return g_state.step;
}

void cfrac_cleanup(void) {
    if (g_initialized) {
        mpz_clear(g_state.N);
        mpz_clear(g_state.a0);
        mpz_clear(g_state.m_k);
        mpz_clear(g_state.d_k);
        mpz_clear(g_state.a_k);
        mpz_clear(g_state.p_prev2);
        mpz_clear(g_state.p_prev1);
        mpz_clear(g_m_next);
        mpz_clear(g_d_next);
        mpz_clear(g_a_next);
        mpz_clear(g_p_new);
        mpz_clear(g_cof);
        mpz_clear(g_tmp);
        g_initialized = 0;
    }
}
