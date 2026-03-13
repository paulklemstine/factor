/*
 * ec_kangaroo_c.c — Pythagorean Kangaroo for secp256k1 ECDLP.
 *
 * Multi-kangaroo with batch Montgomery inversion.
 * Adaptive NK: 2 for small searches, 4 for larger.
 * Batch-inverts all NK denominators per step with 1 inversion.
 *
 * secp256k1 (a=0, b=7). Negation map: search [0, N/2].
 *
 * Compile: gcc -O3 -shared -fPIC -o ec_kangaroo_c.so ec_kangaroo_c.c -lgmp
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <gmp.h>

#define NK_MAX 8
#define NUM_JUMPS 64

static mpz_t PM, ORD;
static int inited = 0;

/* Scratch for ap_add */
static mpz_t T_dx, T_dy, T_inv, T_lam, T_x3, T_y3, T_nm;
/* Scratch for batch hot loop */
static mpz_t H_d[NK_MAX], H_dy[NK_MAX], H_lam[NK_MAX], H_xr[NK_MAX], H_yr[NK_MAX];
static mpz_t H_prod[NK_MAX], H_dinv[NK_MAX], H_binv;

void ec_kang_init(const char *p_hex, const char *order_hex) {
    if (!inited) {
        mpz_init(PM); mpz_init(ORD);
        mpz_init(T_dx); mpz_init(T_dy); mpz_init(T_inv);
        mpz_init(T_lam); mpz_init(T_x3); mpz_init(T_y3); mpz_init(T_nm);
        for (int i = 0; i < NK_MAX; i++) {
            mpz_init(H_d[i]); mpz_init(H_dy[i]); mpz_init(H_lam[i]);
            mpz_init(H_xr[i]); mpz_init(H_yr[i]);
            mpz_init(H_prod[i]); mpz_init(H_dinv[i]);
        }
        mpz_init(H_binv);
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

/* --- DP hash table --- */
typedef struct dp_entry {
    unsigned long long x_hash;
    mpz_t x_full, pos;
    int is_tame;
    struct dp_entry *next;
} dp_entry;
#define DP_TABLE_SIZE 65536
typedef struct { dp_entry *buckets[DP_TABLE_SIZE]; } dp_table;
static dp_table *dp_create(void) { return calloc(1, sizeof(dp_table)); }
static void dp_destroy(dp_table *t) {
    for (int i = 0; i < DP_TABLE_SIZE; i++) {
        dp_entry *e = t->buckets[i];
        while (e) { dp_entry *n=e->next; mpz_clear(e->x_full); mpz_clear(e->pos); free(e); e=n; }
    }
    free(t);
}
static void dp_insert(dp_table *t, const mpz_t x, const mpz_t pos, int is_tame) {
    unsigned long long h = mpz_get_ui(x);
    dp_entry *e = malloc(sizeof(dp_entry));
    e->x_hash=h; mpz_init_set(e->x_full,x); mpz_init_set(e->pos,pos);
    e->is_tame=is_tame; e->next=t->buckets[h%DP_TABLE_SIZE]; t->buckets[h%DP_TABLE_SIZE]=e;
}
static dp_entry *dp_find(dp_table *t, const mpz_t x, int is_tame) {
    unsigned long long h = mpz_get_ui(x);
    dp_entry *e = t->buckets[h%DP_TABLE_SIZE];
    while (e) { if (e->x_hash==h && e->is_tame!=is_tame && mpz_cmp(e->x_full,x)==0) return e; e=e->next; }
    return NULL;
}

/* --- Pythagorean hypotenuse jump table --- */
static const unsigned long PYTH_HYPS[] = {
    5, 109, 233, 373, 509, 685, 853, 1025, 1189, 1429,
    1649, 1825, 2045, 2273, 2533, 2749, 2953, 3233, 3485, 3697,
    4013, 4285, 4625, 4889, 5197, 5545, 5857, 6121, 6485, 6865,
    7309, 7625, 8005, 8465, 8845, 9529, 10069, 10537, 11065, 11597,
    12193, 12721, 13325, 13997, 14813, 15481, 16237, 16865, 17833, 18797,
    19501, 20813, 22229, 24217, 25805, 27449, 30005, 32657, 34285, 37013,
    42025, 47413, 53057, 67901
};

/*
 * Multi-kangaroo solver with batch Montgomery inversion.
 * tame_start_hex: if NULL, use evenly-spaced tame starts.
 */
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

    /* Adaptive NK: 2 for tiny searches, 4 for larger */
    int bound_bits = (int)mpz_sizeinbase(bound, 2);
    int nk = (bound_bits <= 28) ? 2 : 4;
    /* If tame_start_hex given, use 2-kangaroo (for parallel multiprocessing) */
    if (tame_start_hex && tame_start_hex[0]) nk = 2;
    int n_tame = nk / 2;

    apt kpt[NK_MAX];
    mpz_t kpos[NK_MAX];
    int kji[NK_MAX];
    for (int i = 0; i < nk; i++) { ap_init(&kpt[i]); mpz_init(kpos[i]); }

    /* Tame kangaroo starting positions */
    if (tame_start_hex && tame_start_hex[0]) {
        /* Single tame at given position (for parallel wrapper) */
        mpz_set_str(kpos[0], tame_start_hex, 16);
        ap_smul(&kpt[0], kpos[0], &G_pt);
    } else {
        /* Evenly spaced in [0, half] */
        for (int i = 0; i < n_tame; i++) {
            mpz_mul_ui(kpos[i], half, i + 1);
            mpz_tdiv_q_ui(kpos[i], kpos[i], n_tame + 1);
            ap_smul(&kpt[i], kpos[i], &G_pt);
        }
    }

    /* Wild kangaroo starting positions: P + small offsets */
    for (int i = 0; i < nk - n_tame; i++) {
        int idx = n_tame + i;
        mpz_set_ui(kpos[idx], i);
        if (i == 0) {
            ap_copy(&kpt[idx], &P_pt);
        } else {
            mpz_t off; mpz_init_set_ui(off, i);
            apt oG; ap_init(&oG);
            ap_smul(&oG, off, &G_pt);
            ap_add(&kpt[idx], &P_pt, &oG);
            ap_clear(&oG); mpz_clear(off);
        }
    }

    dp_table *dpt = dp_create();
    int found = 0;

    mpz_t max_steps_z;
    mpz_init(max_steps_z);
    mpz_mul_ui(max_steps_z, sqrt_half, 32);
    mpz_add_ui(max_steps_z, max_steps_z, 20000);
    unsigned long max_steps = mpz_get_ui(max_steps_z);
    if (max_steps > 500000000UL) max_steps = 500000000UL;

    for (unsigned long step = 0; step < max_steps && !found; step++) {
        /* Phase 1: compute denominators for batch inversion */
        int bn = 0;
        int bmap[NK_MAX];
        int special[NK_MAX];

        for (int k = 0; k < nk; k++) {
            kji[k] = kpt[k].inf ? 0 : (int)(mpz_fdiv_ui(kpt[k].x, NUM_JUMPS));
            mpz_add_ui(kpos[k], kpos[k], jumps[kji[k]]);
            special[k] = 0;
            if (kpt[k].inf || jump_pts[kji[k]].inf) { special[k]=1; continue; }
            mpz_sub(H_d[bn], jump_pts[kji[k]].x, kpt[k].x);
            mpz_mod(H_d[bn], H_d[bn], PM);
            if (mpz_sgn(H_d[bn])==0) { special[k]=1; continue; }
            mpz_sub(H_dy[bn], jump_pts[kji[k]].y, kpt[k].y);
            mpz_mod(H_dy[bn], H_dy[bn], PM);
            bmap[bn] = k;
            bn++;
        }

        /* Phase 2: batch Montgomery inversion */
        if (bn >= 2) {
            mpz_set(H_prod[0], H_d[0]);
            for (int i = 1; i < bn; i++) {
                mpz_mul(H_prod[i], H_prod[i-1], H_d[i]);
                mpz_mod(H_prod[i], H_prod[i], PM);
            }
            mpz_invert(H_binv, H_prod[bn-1], PM);
            for (int i = bn-1; i > 0; i--) {
                mpz_mul(H_dinv[i], H_binv, H_prod[i-1]);
                mpz_mod(H_dinv[i], H_dinv[i], PM);
                mpz_mul(H_binv, H_binv, H_d[i]);
                mpz_mod(H_binv, H_binv, PM);
            }
            mpz_set(H_dinv[0], H_binv);
        } else if (bn == 1) {
            mpz_invert(H_dinv[0], H_d[0], PM);
        }

        /* Phase 3: complete EC additions using batch inverses */
        for (int bi = 0; bi < bn; bi++) {
            int k = bmap[bi];
            int j = kji[k];
            mpz_mul(H_lam[bi], H_dy[bi], H_dinv[bi]); mpz_mod(H_lam[bi], H_lam[bi], PM);
            mpz_mul(H_xr[bi], H_lam[bi], H_lam[bi]); mpz_mod(H_xr[bi], H_xr[bi], PM);
            mpz_sub(H_xr[bi], H_xr[bi], kpt[k].x);
            mpz_sub(H_xr[bi], H_xr[bi], jump_pts[j].x);
            mpz_mod(H_xr[bi], H_xr[bi], PM);
            mpz_sub(H_yr[bi], kpt[k].x, H_xr[bi]);
            mpz_mul(H_yr[bi], H_lam[bi], H_yr[bi]); mpz_mod(H_yr[bi], H_yr[bi], PM);
            mpz_sub(H_yr[bi], H_yr[bi], kpt[k].y); mpz_mod(H_yr[bi], H_yr[bi], PM);
            mpz_set(kpt[k].x, H_xr[bi]); mpz_set(kpt[k].y, H_yr[bi]); kpt[k].inf=0;
        }

        /* Handle special cases (doubling, infinity) with standard ap_add */
        for (int k = 0; k < nk; k++) {
            if (special[k]) {
                apt ts; ap_init(&ts);
                ap_add(&ts, &kpt[k], &jump_pts[kji[k]]);
                ap_copy(&kpt[k], &ts);
                ap_clear(&ts);
            }
        }

        /* Phase 4: DP checks and collision detection */
        for (int k = 0; k < nk && !found; k++) {
            if (kpt[k].inf) continue;
            if ((mpz_get_ui(kpt[k].x) & dp_mask) != 0) continue;
            int is_tame = (k < n_tame) ? 1 : 0;
            dp_entry *match = dp_find(dpt, kpt[k].x, is_tame);
            if (match) {
                mpz_t k_cand; mpz_init(k_cand);
                if (is_tame) mpz_sub(k_cand, kpos[k], match->pos);
                else         mpz_sub(k_cand, match->pos, kpos[k]);
                mpz_mod(k_cand, k_cand, ORD);
                apt vR; ap_init(&vR);
                ap_smul(&vR, k_cand, &G_pt);
                if (!vR.inf && mpz_cmp(vR.x, P_pt.x)==0 && mpz_cmp(vR.y, P_pt.y)==0 &&
                    mpz_cmp(k_cand, bound) < 0) {
                    gmp_snprintf(result, result_size, "%Zx", k_cand);
                    found = 1;
                }
                if (!found) {
                    mpz_sub(k_cand, ORD, k_cand);
                    ap_smul(&vR, k_cand, &G_pt);
                    if (!vR.inf && mpz_cmp(vR.x, P_pt.x)==0 && mpz_cmp(vR.y, P_pt.y)==0 &&
                        mpz_cmp(k_cand, bound) < 0) {
                        gmp_snprintf(result, result_size, "%Zx", k_cand);
                        found = 1;
                    }
                }
                ap_clear(&vR); mpz_clear(k_cand);
            }
            if (!found) dp_insert(dpt, kpt[k].x, kpos[k], is_tame);
        }
    }

    /* Cleanup */
    dp_destroy(dpt);
    for (int i = 0; i < NUM_JUMPS; i++) ap_clear(&jump_pts[i]);
    ap_clear(&G_pt); ap_clear(&P_pt);
    for (int i = 0; i < nk; i++) { ap_clear(&kpt[i]); mpz_clear(kpos[i]); }
    mpz_clear(bound); mpz_clear(half); mpz_clear(sqrt_half); mpz_clear(max_steps_z);
    return found;
}

/* Original API: uses default tame starts */
int ec_kang_solve(const char *Gx_hex, const char *Gy_hex,
                  const char *Px_hex, const char *Py_hex,
                  const char *search_bound_hex,
                  char *result, size_t result_size) {
    return ec_kang_solve_ex(Gx_hex, Gy_hex, Px_hex, Py_hex,
                            search_bound_hex, NULL, result, result_size);
}
