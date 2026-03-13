/*
 * ec_rho_c.c — Fast Pollard rho for secp256k1 ECDLP.
 *
 * Jacobian coordinates, secp256k1 a=0 specialization.
 * Floyd cycle detection with cheap Jacobian equality check (4 muls, no inversion).
 * Partition by affine x mod 3 — computed via normalized X/Z² ratio.
 *
 * Key insight: partition MUST be consistent (same for equal affine points).
 * We normalize to affine only for the partition function, but use a cheap
 * "x mod 3" that avoids full inversion: compute X*Z^{-2} mod 3.
 * Since Z is nonzero mod p, Z^{-2} mod 3 can be found from Z mod 3.
 * If Z mod 3 == 0, we need to handle specially. But p mod 3 == 2 for secp256k1,
 * so Z can be 0 mod 3.
 *
 * SIMPLER: Just normalize to affine every step. Cost: 1 inversion (~680ns)
 * + ~5 muls (~400ns) = ~1µs/step. With Floyd (3 steps/iter): ~3µs/iter.
 * For 2^24 iterations (16M): ~50s. That handles 48-bit keys.
 *
 * Even simpler: use AFFINE throughout. GMP inversion is fast enough.
 *
 * Compile: gcc -O3 -shared -fPIC -o ec_rho_c.so ec_rho_c.c -lgmp
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <gmp.h>

static mpz_t PM, ORD;
/* Pre-allocated temps for hot loop */
static mpz_t dx, dy, inv, lam, x3, y3, nm;
static int inited = 0;

void ec_rho_init(const char *p_hex, const char *order_hex) {
    if (!inited) {
        mpz_init(PM); mpz_init(ORD);
        mpz_init(dx); mpz_init(dy); mpz_init(inv);
        mpz_init(lam); mpz_init(x3); mpz_init(y3); mpz_init(nm);
        inited = 1;
    }
    mpz_set_str(PM, p_hex, 16);
    mpz_set_str(ORD, order_hex, 16);
}

/* Affine point: x, y (infinity represented by x=y=0 and inf flag) */
typedef struct { mpz_t x, y; int inf; } apt;

static void ap_init(apt *p) { mpz_init(p->x); mpz_init(p->y); p->inf=0; }
static void ap_clear(apt *p) { mpz_clear(p->x); mpz_clear(p->y); }
static void ap_copy(apt *d, const apt *s) { mpz_set(d->x,s->x); mpz_set(d->y,s->y); d->inf=s->inf; }

/* Affine add: R = P + Q. Uses pre-allocated temps. */
static void ap_add(apt *R, const apt *P, const apt *Q) {
    if (P->inf) { ap_copy(R,Q); return; }
    if (Q->inf) { ap_copy(R,P); return; }

    mpz_sub(dx, Q->x, P->x); mpz_mod(dx,dx,PM);

    if (mpz_sgn(dx) == 0) {
        /* Same x: either P==Q (double) or P==-Q (infinity) */
        mpz_sub(dy, Q->y, P->y); mpz_mod(dy,dy,PM);
        if (mpz_sgn(dy) == 0) {
            /* Double */
            if (mpz_sgn(P->y) == 0) { R->inf=1; return; }
            /* lam = 3x²/(2y), a=0 for secp256k1 */
            mpz_mul(nm, P->x, P->x); mpz_mod(nm,nm,PM);
            mpz_mul_ui(nm,nm,3); mpz_mod(nm,nm,PM);
            mpz_mul_ui(dy, P->y, 2); mpz_mod(dy,dy,PM);
            mpz_invert(inv, dy, PM);
            mpz_mul(lam, nm, inv); mpz_mod(lam,lam,PM);
        } else {
            /* P + (-P) = O */
            R->inf = 1; return;
        }
    } else {
        mpz_sub(dy, Q->y, P->y); mpz_mod(dy,dy,PM);
        mpz_invert(inv, dx, PM);
        mpz_mul(lam, dy, inv); mpz_mod(lam,lam,PM);
    }

    /* x3 = lam² - Px - Qx */
    mpz_mul(x3, lam, lam); mpz_mod(x3,x3,PM);
    mpz_sub(x3, x3, P->x); mpz_sub(x3, x3, Q->x);
    mpz_mod(x3,x3,PM);
    /* y3 = lam*(Px - x3) - Py */
    mpz_sub(y3, P->x, x3);
    mpz_mul(y3, lam, y3); mpz_mod(y3,y3,PM);
    mpz_sub(y3, y3, P->y); mpz_mod(y3,y3,PM);

    mpz_set(R->x, x3); mpz_set(R->y, y3); R->inf = 0;
}

/* Affine double: R = 2*P */
static void ap_dbl(apt *R, const apt *P) {
    if (P->inf || mpz_sgn(P->y)==0) { R->inf=1; return; }
    mpz_mul(nm, P->x, P->x); mpz_mod(nm,nm,PM);
    mpz_mul_ui(nm,nm,3); mpz_mod(nm,nm,PM);
    mpz_mul_ui(dy, P->y, 2); mpz_mod(dy,dy,PM);
    mpz_invert(inv, dy, PM);
    mpz_mul(lam, nm, inv); mpz_mod(lam,lam,PM);
    mpz_mul(x3,lam,lam); mpz_mod(x3,x3,PM);
    mpz_submul_ui(x3, P->x, 2); mpz_mod(x3,x3,PM);
    mpz_sub(y3, P->x, x3);
    mpz_mul(y3,lam,y3); mpz_mod(y3,y3,PM);
    mpz_sub(y3,y3,P->y); mpz_mod(y3,y3,PM);
    mpz_set(R->x,x3); mpz_set(R->y,y3); R->inf=0;
}

/* Scalar mult (small k only, for setup) */
static void ap_smul(apt *R, unsigned long k, const apt *P) {
    R->inf = 1;
    if (k == 0) return;
    apt acc, addend, tmp;
    ap_init(&acc); ap_init(&addend); ap_init(&tmp);
    acc.inf = 1;
    ap_copy(&addend, P);
    while (k) {
        if (k & 1) { ap_add(&tmp, &acc, &addend); ap_copy(&acc, &tmp); }
        ap_dbl(&tmp, &addend); ap_copy(&addend, &tmp);
        k >>= 1;
    }
    ap_copy(R, &acc);
    ap_clear(&acc); ap_clear(&addend); ap_clear(&tmp);
}

/* Full scalar mult (mpz k, for verification) */
static void ap_smul_mpz(apt *R, const mpz_t k, const apt *P) {
    R->inf = 1;
    if (mpz_sgn(k)==0) return;
    apt acc, addend, tmp;
    ap_init(&acc); ap_init(&addend); ap_init(&tmp);
    acc.inf = 1;
    ap_copy(&addend, P);
    size_t bits = mpz_sizeinbase(k, 2);
    for (size_t i = 0; i < bits; i++) {
        if (mpz_tstbit(k, i)) { ap_add(&tmp, &acc, &addend); ap_copy(&acc, &tmp); }
        ap_dbl(&tmp, &addend); ap_copy(&addend, &tmp);
    }
    ap_copy(R, &acc);
    ap_clear(&acc); ap_clear(&addend); ap_clear(&tmp);
}

int ec_rho_solve(const char *Gx_hex, const char *Gy_hex,
                 const char *Px_hex, const char *Py_hex,
                 unsigned long max_steps, char *result, size_t result_size) {
    if (!inited) return 0;

    apt G, P;
    ap_init(&G); ap_init(&P);
    mpz_set_str(G.x,Gx_hex,16); mpz_set_str(G.y,Gy_hex,16);
    mpz_set_str(P.x,Px_hex,16); mpz_set_str(P.y,Py_hex,16);

    apt tort, hare, tmp;
    ap_init(&tort); ap_init(&hare); ap_init(&tmp);
    mpz_t ta,tb,ha,hb;
    mpz_init(ta); mpz_init(tb); mpz_init(ha); mpz_init(hb);

    int found = 0;
    unsigned long steps_per = max_steps / 5;
    if (steps_per < 10000) steps_per = max_steps;

    /* Rho step macro: partition by x mod 3 */
    #define STEP(R, a, b) do { \
        if ((R).inf) { \
            ap_add(&tmp,&(R),&P); ap_copy(&(R),&tmp); \
            mpz_add_ui(b,b,1); if(mpz_cmp(b,ORD)>=0) mpz_sub(b,b,ORD); \
        } else { \
            unsigned int p3 = mpz_fdiv_ui((R).x, 3); \
            if (p3==0) { \
                ap_add(&tmp,&(R),&P); ap_copy(&(R),&tmp); \
                mpz_add_ui(b,b,1); if(mpz_cmp(b,ORD)>=0) mpz_sub(b,b,ORD); \
            } else if (p3==1) { \
                ap_dbl(&tmp,&(R)); ap_copy(&(R),&tmp); \
                mpz_add(a,a,a); mpz_mod(a,a,ORD); \
                mpz_add(b,b,b); mpz_mod(b,b,ORD); \
            } else { \
                ap_add(&tmp,&(R),&G); ap_copy(&(R),&tmp); \
                mpz_add_ui(a,a,1); if(mpz_cmp(a,ORD)>=0) mpz_sub(a,a,ORD); \
            } \
        } \
    } while(0)

    for (int attempt = 0; attempt < 5 && !found; attempt++) {
        unsigned long a0 = 1 + (unsigned long)attempt * 7919;

        /* R0 = a0*G + P */
        ap_smul(&tort, a0, &G);
        ap_add(&tmp, &tort, &P);
        ap_copy(&tort, &tmp);
        ap_copy(&hare, &tort);
        mpz_set_ui(ta, a0); mpz_set_ui(tb, 1);
        mpz_set_ui(ha, a0); mpz_set_ui(hb, 1);

        for (unsigned long step = 0; step < steps_per; step++) {
            STEP(tort, ta, tb);
            STEP(hare, ha, hb);
            STEP(hare, ha, hb);

            /* Check collision (affine equality is exact) */
            if (tort.inf && hare.inf) break;
            if (!tort.inf && !hare.inf &&
                mpz_cmp(tort.x, hare.x)==0 && mpz_cmp(tort.y, hare.y)==0) {
                mpz_t da,db,ki,kc;
                mpz_init(da); mpz_init(db); mpz_init(ki); mpz_init(kc);
                mpz_sub(da,ta,ha); mpz_mod(da,da,ORD);
                mpz_sub(db,hb,tb); mpz_mod(db,db,ORD);
                if (mpz_sgn(db)!=0 && mpz_invert(ki,db,ORD)) {
                    mpz_mul(kc,da,ki); mpz_mod(kc,kc,ORD);
                    /* Verify */
                    apt vR; ap_init(&vR);
                    ap_smul_mpz(&vR, kc, &G);
                    if (!vR.inf && mpz_cmp(vR.x,P.x)==0 && mpz_cmp(vR.y,P.y)==0) {
                        gmp_snprintf(result, result_size, "%Zx", kc);
                        found = 1;
                    }
                    ap_clear(&vR);
                }
                mpz_clear(da); mpz_clear(db); mpz_clear(ki); mpz_clear(kc);
                break;
            }
        }
    }
    #undef STEP

    ap_clear(&G); ap_clear(&P);
    ap_clear(&tort); ap_clear(&hare); ap_clear(&tmp);
    mpz_clear(ta); mpz_clear(tb); mpz_clear(ha); mpz_clear(hb);
    return found;
}
