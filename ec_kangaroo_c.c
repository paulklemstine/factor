/*
 * ec_kangaroo_c.c — Pythagorean Kangaroo for secp256k1 ECDLP.
 *
 * Pollard's kangaroo (lambda) method with jump table derived from
 * Berggren tree hypotenuses. Distinguished-point collision detection.
 *
 * Affine GMP arithmetic. secp256k1 (a=0, b=7).
 * Negation map: search [0, N/2], reflect if needed.
 *
 * Compile: gcc -O3 -shared -fPIC -o ec_kangaroo_c.so ec_kangaroo_c.c -lgmp
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <gmp.h>

static mpz_t PM, ORD;
static mpz_t T_dx, T_dy, T_inv, T_lam, T_x3, T_y3, T_nm;
static int inited = 0;

void ec_kang_init(const char *p_hex, const char *order_hex) {
    if (!inited) {
        mpz_init(PM); mpz_init(ORD);
        mpz_init(T_dx); mpz_init(T_dy); mpz_init(T_inv);
        mpz_init(T_lam); mpz_init(T_x3); mpz_init(T_y3); mpz_init(T_nm);
        inited = 1;
    }
    mpz_set_str(PM, p_hex, 16);
    mpz_set_str(ORD, order_hex, 16);
}

typedef struct { mpz_t x, y; int inf; } apt;
static void ap_init(apt *p) { mpz_init(p->x); mpz_init(p->y); p->inf=0; }
static void ap_clear(apt *p) { mpz_clear(p->x); mpz_clear(p->y); }
static void ap_copy(apt *d, const apt *s) { mpz_set(d->x,s->x); mpz_set(d->y,s->y); d->inf=s->inf; }

static void ap_add(apt *R, const apt *P, const apt *Q) {
    if (P->inf) { ap_copy(R,Q); return; }
    if (Q->inf) { ap_copy(R,P); return; }
    mpz_sub(T_dx, Q->x, P->x); mpz_mod(T_dx,T_dx,PM);
    if (mpz_sgn(T_dx)==0) {
        mpz_sub(T_dy, Q->y, P->y); mpz_mod(T_dy,T_dy,PM);
        if (mpz_sgn(T_dy)==0) {
            if (mpz_sgn(P->y)==0) { R->inf=1; return; }
            mpz_mul(T_nm, P->x, P->x); mpz_mod(T_nm,T_nm,PM);
            mpz_mul_ui(T_nm,T_nm,3); mpz_mod(T_nm,T_nm,PM);
            mpz_mul_ui(T_dy, P->y, 2); mpz_mod(T_dy,T_dy,PM);
            mpz_invert(T_inv, T_dy, PM);
            mpz_mul(T_lam, T_nm, T_inv); mpz_mod(T_lam,T_lam,PM);
        } else { R->inf=1; return; }
    } else {
        mpz_sub(T_dy, Q->y, P->y); mpz_mod(T_dy,T_dy,PM);
        mpz_invert(T_inv, T_dx, PM);
        mpz_mul(T_lam, T_dy, T_inv); mpz_mod(T_lam,T_lam,PM);
    }
    mpz_mul(T_x3,T_lam,T_lam); mpz_mod(T_x3,T_x3,PM);
    mpz_sub(T_x3,T_x3,P->x); mpz_sub(T_x3,T_x3,Q->x); mpz_mod(T_x3,T_x3,PM);
    mpz_sub(T_y3, P->x, T_x3);
    mpz_mul(T_y3,T_lam,T_y3); mpz_mod(T_y3,T_y3,PM);
    mpz_sub(T_y3,T_y3,P->y); mpz_mod(T_y3,T_y3,PM);
    mpz_set(R->x,T_x3); mpz_set(R->y,T_y3); R->inf=0;
}

static void ap_smul(apt *R, const mpz_t k, const apt *P) {
    R->inf = 1;
    if (mpz_sgn(k)==0) return;
    apt acc, addend, tmp;
    ap_init(&acc); ap_init(&addend); ap_init(&tmp);
    acc.inf = 1; ap_copy(&addend, P);
    size_t bits = mpz_sizeinbase(k, 2);
    for (size_t i = 0; i < bits; i++) {
        if (mpz_tstbit(k, i)) { ap_add(&tmp, &acc, &addend); ap_copy(&acc, &tmp); }
        ap_add(&tmp, &addend, &addend); ap_copy(&addend, &tmp);
    }
    ap_copy(R, &acc);
    ap_clear(&acc); ap_clear(&addend); ap_clear(&tmp);
}

/* --- Distinguished point hash table --- */
typedef struct dp_entry {
    unsigned long long x_hash;
    mpz_t x_full;
    mpz_t pos;
    int is_tame;
    struct dp_entry *next;
} dp_entry;

#define DP_TABLE_SIZE 65536

typedef struct {
    dp_entry *buckets[DP_TABLE_SIZE];
} dp_table;

static dp_table *dp_create(void) {
    return calloc(1, sizeof(dp_table));
}

static void dp_destroy(dp_table *t) {
    for (int i = 0; i < DP_TABLE_SIZE; i++) {
        dp_entry *e = t->buckets[i];
        while (e) {
            dp_entry *next = e->next;
            mpz_clear(e->x_full);
            mpz_clear(e->pos);
            free(e);
            e = next;
        }
    }
    free(t);
}

static void dp_insert(dp_table *t, const mpz_t x, const mpz_t pos, int is_tame) {
    unsigned long long h = mpz_get_ui(x);
    int idx = h % DP_TABLE_SIZE;
    dp_entry *e = malloc(sizeof(dp_entry));
    e->x_hash = h;
    mpz_init_set(e->x_full, x);
    mpz_init_set(e->pos, pos);
    e->is_tame = is_tame;
    e->next = t->buckets[idx];
    t->buckets[idx] = e;
}

static dp_entry *dp_find(dp_table *t, const mpz_t x, int is_tame) {
    unsigned long long h = mpz_get_ui(x);
    int idx = h % DP_TABLE_SIZE;
    dp_entry *e = t->buckets[idx];
    while (e) {
        if (e->x_hash == h && e->is_tame != is_tame &&
            mpz_cmp(e->x_full, x) == 0) return e;
        e = e->next;
    }
    return NULL;
}

/* --- Pythagorean hypotenuse jump table --- */

/* Berggren tree hypotenuses, geometrically spaced.
   Generated from BFS of ~640 hypotenuses, picking 64 with geometric spacing.
   Range [5, 67901], mean ~ 12756. */
static const unsigned long PYTH_HYPS[] = {
    5, 109, 233, 373, 509, 685, 853, 1025, 1189, 1429,
    1649, 1825, 2045, 2273, 2533, 2749, 2953, 3233, 3485, 3697,
    4013, 4285, 4625, 4889, 5197, 5545, 5857, 6121, 6485, 6865,
    7309, 7625, 8005, 8465, 8845, 9529, 10069, 10537, 11065, 11597,
    12193, 12721, 13325, 13997, 14813, 15481, 16237, 16865, 17833, 18797,
    19501, 20813, 22229, 24217, 25805, 27449, 30005, 32657, 34285, 37013,
    42025, 47413, 53057, 67901
};
#define NUM_JUMPS 64

/*
 * Pythagorean Kangaroo solver.
 *
 * search_bound_hex: search [0, search_bound)
 * Returns 1 on success, 0 on failure.
 */
/* tame_start_hex: if NULL, use bound/4. Otherwise, use the given value. */
int ec_kang_solve_ex(const char *Gx_hex, const char *Gy_hex,
                     const char *Px_hex, const char *Py_hex,
                     const char *search_bound_hex,
                     const char *tame_start_hex,
                     char *result, size_t result_size) {
    if (!inited) return 0;

    mpz_t bound, half;
    mpz_init(bound); mpz_init(half);
    mpz_set_str(bound, search_bound_hex, 16);
    mpz_tdiv_q_2exp(half, bound, 1);

    mpz_t sqrt_half;
    mpz_init(sqrt_half);
    mpz_sqrt(sqrt_half, half);
    unsigned long mean_target = mpz_get_ui(sqrt_half) / 4;
    if (mean_target < 10) mean_target = 10;

    unsigned long raw_mean = 0;
    for (int i = 0; i < NUM_JUMPS; i++) raw_mean += PYTH_HYPS[i];
    raw_mean /= NUM_JUMPS;
    unsigned long scale = mean_target / raw_mean;
    if (scale < 1) scale = 1;

    unsigned long jumps[NUM_JUMPS];
    for (int i = 0; i < NUM_JUMPS; i++) jumps[i] = PYTH_HYPS[i] * scale;
    if (scale > 1) jumps[0] = 1;

    apt G_pt, P_pt;
    ap_init(&G_pt); ap_init(&P_pt);
    mpz_set_str(G_pt.x, Gx_hex, 16);
    mpz_set_str(G_pt.y, Gy_hex, 16);
    mpz_set_str(P_pt.x, Px_hex, 16);
    mpz_set_str(P_pt.y, Py_hex, 16);

    apt jump_pts[NUM_JUMPS];
    for (int i = 0; i < NUM_JUMPS; i++) {
        ap_init(&jump_pts[i]);
        mpz_t jk; mpz_init_set_ui(jk, jumps[i]);
        ap_smul(&jump_pts[i], jk, &G_pt);
        mpz_clear(jk);
    }

    int D = 0;
    { mpz_t tmp; mpz_init_set(tmp, bound);
      while (mpz_sgn(tmp) > 0) { D++; mpz_tdiv_q_2exp(tmp, tmp, 1); }
      mpz_clear(tmp);
    }
    D = D / 4;
    if (D < 1) D = 1;
    if (D > 20) D = 20;
    unsigned long dp_mask = (1UL << D) - 1;

    mpz_t tame_pos, wild_pos, tame_start;
    mpz_init(tame_pos); mpz_init(wild_pos); mpz_init(tame_start);
    if (tame_start_hex && tame_start_hex[0]) {
        mpz_set_str(tame_start, tame_start_hex, 16);
    } else {
        mpz_tdiv_q_2exp(tame_start, bound, 2);
    }
    mpz_set(tame_pos, tame_start);

    apt tame_pt, wild_pt, tmp;
    ap_init(&tame_pt); ap_init(&wild_pt); ap_init(&tmp);
    ap_smul(&tame_pt, tame_start, &G_pt);
    ap_copy(&wild_pt, &P_pt);
    mpz_set_ui(wild_pos, 0);

    dp_table *dpt = dp_create();
    int found = 0;

    /* max_steps: 32√(half) + 20000 */
    mpz_t max_steps_z;
    mpz_init(max_steps_z);
    mpz_mul_ui(max_steps_z, sqrt_half, 32);
    mpz_add_ui(max_steps_z, max_steps_z, 20000);
    unsigned long max_steps = mpz_get_ui(max_steps_z);
    if (max_steps > 500000000UL) max_steps = 500000000UL;

    for (unsigned long step = 0; step < max_steps && !found; step++) {
        /* Tame step */
        {
            int ji = tame_pt.inf ? 0 : (int)(mpz_fdiv_ui(tame_pt.x, NUM_JUMPS));
            mpz_add_ui(tame_pos, tame_pos, jumps[ji]);
            ap_add(&tmp, &tame_pt, &jump_pts[ji]);
            ap_copy(&tame_pt, &tmp);

            if (!tame_pt.inf && (mpz_get_ui(tame_pt.x) & dp_mask) == 0) {
                dp_entry *match = dp_find(dpt, tame_pt.x, 1);
                if (match) {
                    mpz_t k_cand;
                    mpz_init(k_cand);
                    mpz_sub(k_cand, tame_pos, match->pos);
                    mpz_mod(k_cand, k_cand, ORD);

                    apt vR; ap_init(&vR);
                    ap_smul(&vR, k_cand, &G_pt);
                    if (!vR.inf && mpz_cmp(vR.x, P_pt.x)==0 && mpz_cmp(vR.y, P_pt.y)==0) {
                        if (mpz_cmp(k_cand, bound) < 0) {
                            gmp_snprintf(result, result_size, "%Zx", k_cand);
                            found = 1;
                        }
                    }
                    if (!found) {
                        mpz_sub(k_cand, ORD, k_cand);
                        ap_smul(&vR, k_cand, &G_pt);
                        if (!vR.inf && mpz_cmp(vR.x, P_pt.x)==0 && mpz_cmp(vR.y, P_pt.y)==0) {
                            if (mpz_cmp(k_cand, bound) < 0) {
                                gmp_snprintf(result, result_size, "%Zx", k_cand);
                                found = 1;
                            }
                        }
                    }
                    ap_clear(&vR);
                    mpz_clear(k_cand);
                }
                if (!found) dp_insert(dpt, tame_pt.x, tame_pos, 1);
            }
        }

        /* Wild step */
        {
            int ji = wild_pt.inf ? 0 : (int)(mpz_fdiv_ui(wild_pt.x, NUM_JUMPS));
            mpz_add_ui(wild_pos, wild_pos, jumps[ji]);
            ap_add(&tmp, &wild_pt, &jump_pts[ji]);
            ap_copy(&wild_pt, &tmp);

            if (!wild_pt.inf && (mpz_get_ui(wild_pt.x) & dp_mask) == 0) {
                dp_entry *match = dp_find(dpt, wild_pt.x, 0);
                if (match) {
                    mpz_t k_cand;
                    mpz_init(k_cand);
                    mpz_sub(k_cand, match->pos, wild_pos);
                    mpz_mod(k_cand, k_cand, ORD);

                    apt vR; ap_init(&vR);
                    ap_smul(&vR, k_cand, &G_pt);
                    if (!vR.inf && mpz_cmp(vR.x, P_pt.x)==0 && mpz_cmp(vR.y, P_pt.y)==0) {
                        if (mpz_cmp(k_cand, bound) < 0) {
                            gmp_snprintf(result, result_size, "%Zx", k_cand);
                            found = 1;
                        }
                    }
                    if (!found) {
                        mpz_sub(k_cand, ORD, k_cand);
                        ap_smul(&vR, k_cand, &G_pt);
                        if (!vR.inf && mpz_cmp(vR.x, P_pt.x)==0 && mpz_cmp(vR.y, P_pt.y)==0) {
                            if (mpz_cmp(k_cand, bound) < 0) {
                                gmp_snprintf(result, result_size, "%Zx", k_cand);
                                found = 1;
                            }
                        }
                    }
                    ap_clear(&vR);
                    mpz_clear(k_cand);
                }
                if (!found) dp_insert(dpt, wild_pt.x, wild_pos, 0);
            }
        }
    }

    /* Cleanup */
    dp_destroy(dpt);
    for (int i = 0; i < NUM_JUMPS; i++) ap_clear(&jump_pts[i]);
    ap_clear(&G_pt); ap_clear(&P_pt); ap_clear(&tame_pt); ap_clear(&wild_pt); ap_clear(&tmp);
    mpz_clear(bound); mpz_clear(half); mpz_clear(sqrt_half);
    mpz_clear(tame_pos); mpz_clear(wild_pos); mpz_clear(tame_start);
    mpz_clear(max_steps_z);
    return found;
}

/* Original API: tame starts at bound/4 */
int ec_kang_solve(const char *Gx_hex, const char *Gy_hex,
                  const char *Px_hex, const char *Py_hex,
                  const char *search_bound_hex,
                  char *result, size_t result_size) {
    return ec_kang_solve_ex(Gx_hex, Gy_hex, Px_hex, Py_hex,
                            search_bound_hex, NULL, result, result_size);
}
