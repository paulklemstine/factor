/*
 * ec_bsgs_c.c — Fast Baby-Step Giant-Step for secp256k1 ECDLP.
 *
 * Affine EC arithmetic with GMP. Hash table keyed on x-coordinate.
 * For small keys (up to ~48 bits), BSGS is optimal: O(√N) time and space.
 *
 * Compile: gcc -O3 -shared -fPIC -o ec_bsgs_c.so ec_bsgs_c.c -lgmp -lm
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <gmp.h>

static mpz_t PM;
static int inited = 0;
static mpz_t T_dx, T_dy, T_inv, T_lam, T_x3, T_y3, T_nm;

void ec_bsgs_init(const char *p_hex) {
    if (!inited) {
        mpz_init(PM);
        mpz_init(T_dx); mpz_init(T_dy); mpz_init(T_inv);
        mpz_init(T_lam); mpz_init(T_x3); mpz_init(T_y3); mpz_init(T_nm);
        inited = 1;
    }
    mpz_set_str(PM, p_hex, 16);
}

/* Affine point */
typedef struct { mpz_t x, y; int inf; } apt;

static void ap_init(apt *p) { mpz_init(p->x); mpz_init(p->y); p->inf=0; }
static void ap_clear(apt *p) { mpz_clear(p->x); mpz_clear(p->y); }
static void ap_copy(apt *d, const apt *s) { mpz_set(d->x,s->x); mpz_set(d->y,s->y); d->inf=s->inf; }

/* Affine add using pre-allocated temps */
static void ap_add(apt *R, const apt *P, const apt *Q) {
    if (P->inf) { ap_copy(R,Q); return; }
    if (Q->inf) { ap_copy(R,P); return; }

    mpz_sub(T_dx, Q->x, P->x); mpz_mod(T_dx,T_dx,PM);

    if (mpz_sgn(T_dx) == 0) {
        mpz_sub(T_dy, Q->y, P->y); mpz_mod(T_dy,T_dy,PM);
        if (mpz_sgn(T_dy) == 0) {
            if (mpz_sgn(P->y) == 0) { R->inf=1; return; }
            mpz_mul(T_nm, P->x, P->x); mpz_mod(T_nm,T_nm,PM);
            mpz_mul_ui(T_nm,T_nm,3); mpz_mod(T_nm,T_nm,PM);
            mpz_mul_ui(T_dy, P->y, 2); mpz_mod(T_dy,T_dy,PM);
            mpz_invert(T_inv, T_dy, PM);
            mpz_mul(T_lam, T_nm, T_inv); mpz_mod(T_lam,T_lam,PM);
        } else {
            R->inf = 1; return;
        }
    } else {
        mpz_sub(T_dy, Q->y, P->y); mpz_mod(T_dy,T_dy,PM);
        mpz_invert(T_inv, T_dx, PM);
        mpz_mul(T_lam, T_dy, T_inv); mpz_mod(T_lam,T_lam,PM);
    }

    mpz_mul(T_x3, T_lam, T_lam); mpz_mod(T_x3,T_x3,PM);
    mpz_sub(T_x3, T_x3, P->x); mpz_sub(T_x3, T_x3, Q->x);
    mpz_mod(T_x3,T_x3,PM);
    mpz_sub(T_y3, P->x, T_x3);
    mpz_mul(T_y3, T_lam, T_y3); mpz_mod(T_y3,T_y3,PM);
    mpz_sub(T_y3, T_y3, P->y); mpz_mod(T_y3,T_y3,PM);

    mpz_set(R->x, T_x3); mpz_set(R->y, T_y3); R->inf = 0;
}

/* Negate a point */
static void ap_neg(apt *R, const apt *P) {
    if (P->inf) { R->inf=1; return; }
    mpz_set(R->x, P->x);
    mpz_sub(R->y, PM, P->y); mpz_mod(R->y, R->y, PM);
    R->inf = 0;
}

/* Scalar mult (any size k) */
static void ap_smul(apt *R, const mpz_t k, const apt *P) {
    R->inf = 1;
    if (mpz_sgn(k)==0) return;
    apt acc, addend, tmp;
    ap_init(&acc); ap_init(&addend); ap_init(&tmp);
    acc.inf = 1;
    ap_copy(&addend, P);
    size_t bits = mpz_sizeinbase(k, 2);
    for (size_t i = 0; i < bits; i++) {
        if (mpz_tstbit(k, i)) { ap_add(&tmp, &acc, &addend); ap_copy(&acc, &tmp); }
        ap_add(&tmp, &addend, &addend); ap_copy(&addend, &tmp);
    }
    ap_copy(R, &acc);
    ap_clear(&acc); ap_clear(&addend); ap_clear(&tmp);
}

/* ----- Hash table keyed on x-coordinate (lower 64 bits) ----- */

typedef struct ht_entry {
    mpz_t x;          /* full x-coordinate for collision resolution */
    unsigned long j;   /* baby-step index */
    int y_sign;        /* 0 = positive y, 1 = negative y (for ±) */
    struct ht_entry *next;
} ht_entry;

typedef struct {
    ht_entry **buckets;
    size_t size;
} hashtable;

static hashtable *ht_create(size_t size) {
    hashtable *ht = malloc(sizeof(hashtable));
    ht->size = size;
    ht->buckets = calloc(size, sizeof(ht_entry*));
    return ht;
}

static void ht_destroy(hashtable *ht) {
    for (size_t i = 0; i < ht->size; i++) {
        ht_entry *e = ht->buckets[i];
        while (e) {
            ht_entry *next = e->next;
            mpz_clear(e->x);
            free(e);
            e = next;
        }
    }
    free(ht->buckets);
    free(ht);
}

static size_t ht_hash(const mpz_t x, size_t size) {
    /* Use low 64 bits as hash */
    return (size_t)(mpz_get_ui(x) % size);
}

static void ht_insert(hashtable *ht, const mpz_t x, unsigned long j, int y_sign) {
    size_t idx = ht_hash(x, ht->size);
    ht_entry *e = malloc(sizeof(ht_entry));
    mpz_init_set(e->x, x);
    e->j = j;
    e->y_sign = y_sign;
    e->next = ht->buckets[idx];
    ht->buckets[idx] = e;
}

/* Lookup: find entry matching x. Returns j or -1. */
static long ht_lookup(const hashtable *ht, const mpz_t x) {
    size_t idx = ht_hash(x, ht->size);
    ht_entry *e = ht->buckets[idx];
    while (e) {
        if (mpz_cmp(e->x, x) == 0) return (long)e->j;
        e = e->next;
    }
    return -1;
}

/*
 * BSGS: find k in [0, search_bound) such that k*G = P.
 *
 * Baby step: store j*G for j in [0, m)
 * Giant step: check P - i*m*G for i in [0, m)
 * where m = ceil(sqrt(search_bound)).
 *
 * Returns 1 if found (result written), 0 otherwise.
 */
int ec_bsgs_solve(const char *Gx_hex, const char *Gy_hex,
                  const char *Px_hex, const char *Py_hex,
                  const char *search_bound_hex,
                  char *result, size_t result_size) {
    if (!inited) return 0;

    mpz_t bound;
    mpz_init(bound);
    mpz_set_str(bound, search_bound_hex, 16);

    /* m = ceil(sqrt(bound)) */
    mpz_t m;
    mpz_init(m);
    mpz_sqrt(m, bound);
    mpz_add_ui(m, m, 1);
    unsigned long m_ul = mpz_get_ui(m);

    /* Cap at ~2^25 = 33M entries to avoid OOM */
    if (m_ul > 33000000) {
        mpz_clear(bound); mpz_clear(m);
        return 0;
    }

    apt G, P, Q, tmp, mG, neg_mG;
    ap_init(&G); ap_init(&P); ap_init(&Q); ap_init(&tmp);
    ap_init(&mG); ap_init(&neg_mG);
    mpz_set_str(G.x,Gx_hex,16); mpz_set_str(G.y,Gy_hex,16);
    mpz_set_str(P.x,Px_hex,16); mpz_set_str(P.y,Py_hex,16);

    /* Hash table: ~2x the entries for low collision rate */
    hashtable *ht = ht_create(m_ul * 2 + 1);

    /* Baby step: table[j*G.x] = j for j in [0, m) */
    Q.inf = 1;
    for (unsigned long j = 0; j < m_ul; j++) {
        if (!Q.inf) {
            ht_insert(ht, Q.x, j, 0);
        } else if (j == 0) {
            /* Store infinity with a sentinel — handle separately */
        }
        ap_add(&tmp, &Q, &G);
        ap_copy(&Q, &tmp);
    }

    /* Compute -m*G */
    ap_smul(&mG, m, &G);
    ap_neg(&neg_mG, &mG);

    /* Giant step: gamma = P - i*m*G for i in [0, m) */
    ap_copy(&Q, &P);
    int found = 0;

    for (unsigned long i = 0; i < m_ul && !found; i++) {
        if (!Q.inf) {
            long j = ht_lookup(ht, Q.x);
            if (j >= 0) {
                /* Potential match: k = i*m + j */
                mpz_t kc;
                mpz_init(kc);
                mpz_set_ui(kc, i);
                mpz_mul(kc, kc, m);
                mpz_add_ui(kc, kc, (unsigned long)j);

                /* Verify k*G == P */
                apt vR; ap_init(&vR);
                ap_smul(&vR, kc, &G);
                if (!vR.inf && mpz_cmp(vR.x, P.x)==0 && mpz_cmp(vR.y, P.y)==0) {
                    gmp_snprintf(result, result_size, "%Zx", kc);
                    found = 1;
                }
                ap_clear(&vR);
                mpz_clear(kc);
            }
        } else {
            /* Q is infinity, check if P == i*m*G (i.e., j==0) */
        }
        ap_add(&tmp, &Q, &neg_mG);
        ap_copy(&Q, &tmp);
    }

    ht_destroy(ht);
    ap_clear(&G); ap_clear(&P); ap_clear(&Q); ap_clear(&tmp);
    ap_clear(&mG); ap_clear(&neg_mG);
    mpz_clear(bound); mpz_clear(m);
    return found;
}
