/*
 * CFRAC sieve C extension — fast CF recurrence + trial division
 *
 * The inner loop generates CF terms and trial-divides the residues d_{k+1}
 * by the factor base. This is the bottleneck in Python (~30K terms/s).
 * In C with GMP, we can do ~500K+ terms/s.
 *
 * Compile:
 *   gcc -O3 -shared -fPIC -o cfrac_sieve_c.so cfrac_sieve_c.c -lgmp -lm
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <gmp.h>

/*
 * Batch CF generation + trial division.
 *
 * Inputs:
 *   N_str: string representation of N (the number to factor, or kN)
 *   fb: array of factor base primes (as unsigned longs)
 *   fb_size: number of primes in factor base
 *   batch_size: number of CF terms to generate
 *   lp_bound: large prime bound
 *
 * For each CF term k, compute d_{k+1} and trial divide by FB.
 * Store results in output arrays:
 *   out_smooth_idx: indices of smooth/partial terms (0-based within batch)
 *   out_exps: exponent vectors (fb_size ints per smooth term)
 *   out_cofactors: cofactor after trial division
 *   out_signs: sign bits
 *   out_p_mods: p_k mod N as GMP strings
 *
 * Returns number of smooth/partial terms found.
 */

/* Maximum factor base size */
#define MAX_FB 50000
/* Maximum results per batch */
#define MAX_RESULTS 100000

/* State structure for CF expansion */
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

/* Result structure */
typedef struct {
    int idx;           /* CF step index */
    int sign;          /* 0 or 1 */
    int exps[MAX_FB];  /* exponent vector */
    unsigned long cofactor_lo;  /* low 64 bits of cofactor */
    unsigned long cofactor_hi;  /* high 64 bits (0 if fits in 64 bits) */
    /* p_mod stored separately */
} cf_result_t;

/* Global state — we keep one CF expansion active */
static cf_state_t g_state;
static int g_initialized = 0;
static unsigned long g_fb[MAX_FB];
static int g_fb_size = 0;
static unsigned long g_lp_bound = 0;

/* Temp variables (avoid repeated malloc) */
static mpz_t g_m_next, g_d_next, g_a_next, g_p_new;
static mpz_t g_cof, g_tmp;

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
}

/*
 * Run batch_size CF steps. For each, trial divide d_{k+1} by FB.
 * Returns results in caller-provided arrays.
 *
 * out_count: number of results (smooth + LP partial)
 * out_step: step indices
 * out_sign: sign bits
 * out_cofactor: cofactor values (as strings, null-terminated, concatenated)
 * out_exps: exponent vectors (flat array, fb_size per result)
 * out_p_mod: p_k mod N values (as strings, concatenated)
 *
 * Returns: number of results written.
 */
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
    int max_results = MAX_RESULTS;

    for (int bi = 0; bi < batch_size && n_results < max_results; bi++) {
        /* CF recurrence: m_{k+1} = d_k * a_k - m_k */
        mpz_mul(g_m_next, g_state.d_k, g_state.a_k);
        mpz_sub(g_m_next, g_m_next, g_state.m_k);

        /* d_{k+1} = (N - m_{k+1}^2) / d_k */
        mpz_mul(g_tmp, g_m_next, g_m_next);
        mpz_sub(g_d_next, g_state.N, g_tmp);
        mpz_tdiv_q(g_d_next, g_d_next, g_state.d_k);

        if (mpz_sgn(g_d_next) == 0) break;

        /* a_{k+1} = floor((a0 + m_{k+1}) / d_{k+1}) */
        mpz_add(g_tmp, g_state.a0, g_m_next);
        mpz_tdiv_q(g_a_next, g_tmp, g_d_next);

        /* p_{k+1} = a_{k+1} * p_k + p_{k-1} mod N */
        mpz_mul(g_p_new, g_a_next, g_state.p_prev1);
        mpz_add(g_p_new, g_p_new, g_state.p_prev2);
        mpz_mod(g_p_new, g_p_new, g_state.N);

        /* Trial divide d_{k+1} by FB */
        mpz_abs(g_cof, g_d_next);

        int *exps = out_exps + n_results * g_fb_size;
        memset(exps, 0, g_fb_size * sizeof(int));

        for (int i = 0; i < g_fb_size; i++) {
            unsigned long p = g_fb[i];
            /* Early exit: if p^2 > cofactor, cofactor is prime (or 1) */
            if (mpz_fits_ulong_p(g_cof)) {
                if (p * p > mpz_get_ui(g_cof))
                    break;
            } else {
                /* cofactor doesn't fit in ulong — p^2 can't exceed it
                   for any FB prime (FB primes are small), so continue */
            }
            if (mpz_divisible_ui_p(g_cof, p)) {
                int e = 0;
                while (mpz_divisible_ui_p(g_cof, p)) {
                    mpz_divexact_ui(g_cof, g_cof, p);
                    e++;
                }
                exps[i] = e;
                if (mpz_cmp_ui(g_cof, 1) == 0) break;
            }
        }

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
                    is_lp = 1;  /* LP candidate */
                }
            }
        }

        if (is_smooth || is_lp) {
            out_step[n_results] = g_state.step + bi;
            out_sign[n_results] = (g_state.step + bi) % 2 == 0 ? 1 : 0;

            /* Write cofactor as string */
            char *cof_str = mpz_get_str(NULL, 10, g_cof);
            int cof_len = strlen(cof_str);
            if (cof_offset + cof_len + 1 < cof_buf_size) {
                memcpy(out_cofactor_buf + cof_offset, cof_str, cof_len + 1);
                cof_offset += cof_len + 1;
            }
            free(cof_str);

            /* Write p_mod as string */
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

/* Get current step count */
int cfrac_get_step(void) {
    return g_state.step;
}

/* Cleanup */
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
