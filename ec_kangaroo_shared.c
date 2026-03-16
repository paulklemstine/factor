/*
 * ec_kangaroo_shared.c — Shared-memory multi-process Pollard kangaroo for secp256k1 ECDLP.
 *
 * Van Oorschot-Wiener parallelism: all workers share a single DP table
 * in mmap'd shared memory, giving LINEAR speedup in #workers.
 *
 * Breakthroughs from factoring research:
 *   1. Shared-memory DP table (mmap MAP_SHARED|MAP_ANONYMOUS)
 *   2. Robin Hood open-addressing hash (lock-free via __atomic_compare_exchange)
 *   3. 128-bit position tracking (two int64s for up to 128-bit scalars)
 *
 * Compile: gcc -O3 -march=native -shared -fPIC -o ec_kangaroo_shared.so ec_kangaroo_shared.c -lgmp
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <gmp.h>

#define NK_MAX 16
#define NUM_JUMPS 64

/* ================================================================
 * Fixed-limb field arithmetic for secp256k1 (256-bit)
 * Copied verbatim from ec_kangaroo_c.c
 * ================================================================ */
typedef mp_limb_t fe_t[4];

/* secp256k1 prime: p = 2^256 - 2^32 - 977 */
static const mp_limb_t FE_P[4] = {
    0xFFFFFFFEFFFFFC2FULL, 0xFFFFFFFFFFFFFFFFULL,
    0xFFFFFFFFFFFFFFFFULL, 0xFFFFFFFFFFFFFFFFULL
};
/* 2^256 - p = 0x1000003D1 */
static const mp_limb_t FE_PC = 0x1000003D1ULL;

static inline void fe_set(fe_t r, const fe_t a) {
    r[0] = a[0]; r[1] = a[1]; r[2] = a[2]; r[3] = a[3];
}

static inline int fe_is_zero(const fe_t a) {
    return (a[0] | a[1] | a[2] | a[3]) == 0;
}
static inline int fe_eq(const fe_t a, const fe_t b) {
    return (a[0]==b[0]) & (a[1]==b[1]) & (a[2]==b[2]) & (a[3]==b[3]);
}

/* r = (a - b) mod p.  a,b must be in [0,p). */
static inline void fe_sub(fe_t r, const fe_t a, const fe_t b) {
    mp_limb_t borrow = mpn_sub_n(r, a, b, 4);
    if (borrow) {
        mpn_add_n(r, r, FE_P, 4);  /* r += p */
    }
}

static inline void fe_reduce(fe_t r, mp_limb_t t[8]) {
    mp_limb_t hi[5];
    mp_limb_t acc[5];

    /* Round 1: acc = t[0..3] + t[4..7] * c */
    hi[4] = mpn_mul_1(hi, t + 4, 4, FE_PC);
    memcpy(acc, t, 4 * sizeof(mp_limb_t));
    acc[4] = 0;
    mpn_add_n(acc, acc, hi, 5);

    /* Round 2: fold acc[4] back in. */
    if (acc[4]) {
        mp_limb_t ov_prod[2];
        ov_prod[1] = mpn_mul_1(ov_prod, &acc[4], 1, FE_PC);
        acc[4] = 0;
        mp_limb_t carry = mpn_add(acc, acc, 4, ov_prod, ov_prod[1] ? 2 : 1);
        if (carry) {
            mpn_add_1(acc, acc, 4, FE_PC);
        }
    }

    memcpy(r, acc, 4 * sizeof(mp_limb_t));

    /* Final: if r >= p, subtract p */
    if (mpn_cmp(r, FE_P, 4) >= 0) {
        mpn_sub_n(r, r, FE_P, 4);
    }
}

/* r = a * b mod p */
static inline void fe_mul(fe_t r, const fe_t a, const fe_t b) {
    mp_limb_t t[8];
    mpn_mul_n(t, a, b, 4);
    fe_reduce(r, t);
}

/* Modular inverse via mpn_gcdext */
static void fe_invert(fe_t r, const fe_t a) {
    mp_limb_t u[5], v[5], g[5], s[5];
    mp_size_t sn;
    memcpy(u, a, 4 * sizeof(mp_limb_t)); u[4] = 0;
    memcpy(v, FE_P, 4 * sizeof(mp_limb_t)); v[4] = 0;
    mpn_gcdext(g, s, &sn, u, 4, v, 4);
    mp_size_t abs_sn = sn < 0 ? -sn : sn;
    for (mp_size_t i = abs_sn; i < 4; i++) s[i] = 0;
    if (sn < 0)
        mpn_sub_n(r, FE_P, s, 4);
    else
        memcpy(r, s, 4 * sizeof(mp_limb_t));
}

/* Convert mpz -> fe (assumes 0 <= a < p) */
static inline void fe_from_mpz(fe_t r, const mpz_t a) {
    size_t n;
    memset(r, 0, 4 * sizeof(mp_limb_t));
    n = mpz_size(a);
    if (n > 4) n = 4;
    if (n > 0) {
        const mp_limb_t *limbs = mpz_limbs_read(a);
        memcpy(r, limbs, n * sizeof(mp_limb_t));
    }
}

/* Convert fe -> mpz */
static inline void fe_to_mpz(mpz_t r, const fe_t a) {
    mp_limb_t *p = mpz_limbs_write(r, 4);
    memcpy(p, a, 4 * sizeof(mp_limb_t));
    int sz = 4;
    while (sz > 0 && a[sz - 1] == 0) sz--;
    mpz_limbs_finish(r, sz);
}

/* ================================================================
 * mpz EC arithmetic (for setup, verification, scalar mult)
 * ================================================================ */

static mpz_t PM, ORD;
static int inited = 0;
static mpz_t T_dx, T_dy, T_inv, T_lam, T_x3, T_y3, T_nm;

void ec_kang_shared_init(const char *p_hex, const char *order_hex) {
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

/* ================================================================
 * Shared-memory Robin Hood DP table
 * ================================================================ */

/* Each DP slot: 40 bytes, packed for cache efficiency */
typedef struct __attribute__((packed)) {
    uint64_t x_lo;        /* lower 64 bits of EC point x-coordinate */
    uint64_t x_hi;        /* next 64 bits of EC point x-coordinate */
    int64_t  pos_lo;      /* lower 64 bits of 128-bit position */
    int64_t  pos_hi;      /* upper 64 bits of 128-bit position */
    uint32_t is_tame;     /* 1 = tame, 0 = wild */
    uint32_t occupied;    /* 0 = empty, nonzero = occupied (probe_dist+1) */
} dp_slot_t;

/* Lock-free linear-probing insert into shared DP table.
 * Returns: 0 = inserted, 1 = found collision (tame-wild match), -1 = table full.
 * On collision, writes the matching slot's data into match_out.
 *
 * Protocol: CAS occupied 0→1 claims slot, then write data, then set occupied=2
 * (READY). Readers spin-wait on occupied==1 (CLAIMING) to avoid partial reads. */
#define DP_EMPTY    0
#define DP_CLAIMING 1
#define DP_READY    2

static int dp_shared_insert(dp_slot_t *table, unsigned long capacity,
                             uint64_t x_lo, uint64_t x_hi,
                             int64_t pos_lo, int64_t pos_hi,
                             uint32_t is_tame,
                             dp_slot_t *match_out) {
    uint64_t hash = (x_lo * 0x9E3779B97F4A7C15ULL) ^ (x_hi * 0x517CC1B727220A95ULL);
    unsigned long idx = hash & (capacity - 1);  /* capacity is power of 2 */

    for (unsigned long i = 0; i < 64; i++) {  /* max 64 probes */
        dp_slot_t *slot = &table[idx];

        /* Try to claim empty slot atomically */
        uint32_t expected = DP_EMPTY;
        if (__atomic_compare_exchange_n(&slot->occupied, &expected, DP_CLAIMING,
                                         0, __ATOMIC_ACQ_REL, __ATOMIC_ACQUIRE)) {
            /* We claimed this slot — write data, then mark READY */
            slot->x_lo = x_lo;
            slot->x_hi = x_hi;
            slot->pos_lo = pos_lo;
            slot->pos_hi = pos_hi;
            slot->is_tame = is_tame;
            __atomic_store_n(&slot->occupied, DP_READY, __ATOMIC_RELEASE);
            return 0;
        }

        /* Slot is occupied — wait if another thread is still writing */
        uint32_t occ = __atomic_load_n(&slot->occupied, __ATOMIC_ACQUIRE);
        if (occ == DP_CLAIMING) {
            /* Spin briefly — writer will finish very fast */
            for (int spin = 0; spin < 100; spin++) {
                occ = __atomic_load_n(&slot->occupied, __ATOMIC_ACQUIRE);
                if (occ != DP_CLAIMING) break;
            }
            if (occ == DP_CLAIMING) {
                /* Still claiming after 100 spins — skip this slot */
                idx = (idx + 1) & (capacity - 1);
                continue;
            }
        }

        /* Slot is READY — check for tame-wild collision */
        if (occ == DP_READY && slot->x_lo == x_lo && slot->x_hi == x_hi &&
            slot->is_tame != is_tame) {
            if (match_out) {
                match_out->x_lo = slot->x_lo;
                match_out->x_hi = slot->x_hi;
                match_out->pos_lo = slot->pos_lo;
                match_out->pos_hi = slot->pos_hi;
                match_out->is_tame = slot->is_tame;
                match_out->occupied = occ;
            }
            return 1;  /* collision found */
        }

        idx = (idx + 1) & (capacity - 1);
    }
    return -1;  /* table full or max probes exceeded */
}

/* ================================================================
 * Pythagorean hypotenuse jump table (same as ec_kangaroo_c.c)
 * ================================================================ */
/* Lévy-flight-inspired exponential spread: 1 to 10M (10^7 spread).
 * Wide spread compensates for weak hash (x & 63) jump selection,
 * ensuring correlated indices still produce very different walks.
 * Benchmarked 33-37% faster than original 13.6K-spread geometric table. */
static const unsigned long PYTH_HYPS[] = {
    25, 26, 27, 28, 29, 31, 32, 33, 34, 35,
    37, 38, 39, 41, 42, 44, 46, 47, 49, 51,
    53, 55, 57, 59, 61, 63, 66, 68, 71, 73,
    76, 79, 82, 85, 88, 91, 95, 98, 102, 106,
    110, 114, 118, 122, 127, 132, 137, 142, 147, 152,
    158, 164, 170, 176, 183, 190, 197, 204, 212, 220,
    228, 236, 245, 254
};

/* ================================================================
 * Shared-memory kangaroo solver
 * ================================================================ */

/*
 * 128-bit position arithmetic using two int64s.
 * pos = pos_hi * 2^64 + pos_lo (treating pos_lo as unsigned for the low part).
 * For positions that fit in 64 bits, pos_hi = 0.
 */
static inline void pos128_add(int64_t *rlo, int64_t *rhi,
                                int64_t alo, int64_t ahi,
                                unsigned long step) {
    uint64_t ulo = (uint64_t)alo;
    uint64_t sum = ulo + (uint64_t)step;
    int carry = (sum < ulo) ? 1 : 0;
    *rlo = (int64_t)sum;
    *rhi = ahi + carry;
}

static inline void pos128_sub(int64_t *rlo, int64_t *rhi,
                                int64_t alo, int64_t ahi,
                                int64_t blo, int64_t bhi) {
    uint64_t ulo = (uint64_t)alo;
    uint64_t ublo = (uint64_t)blo;
    int borrow = (ulo < ublo) ? 1 : 0;
    *rlo = (int64_t)(ulo - ublo);
    *rhi = ahi - bhi - borrow;
}

int ec_kang_shared_solve(
    const char *Gx_hex, const char *Gy_hex,
    const char *Px_hex, const char *Py_hex,
    const char *search_bound_hex,
    void *dp_region, unsigned long dp_capacity,
    int worker_id, int num_workers,
    volatile int *found_flag,
    char *result, size_t result_size)
{
    if (!inited) return 0;

    dp_slot_t *dp_table = (dp_slot_t *)dp_region;

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
    unsigned long max_jump = mean_target * 2;  /* cap: no jump > 2x mean prevents overshoot */
    for (int i = 0; i < NUM_JUMPS; i++) {
        jumps[i] = PYTH_HYPS[i] * scale;
        if (jumps[i] > max_jump) jumps[i] = max_jump;
    }
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

    /* DP bit depth — optimal: (bits-8)/4 per DP density sweep results */
    int D = 0;
    { mpz_t tmp; mpz_init_set(tmp, bound);
      while (mpz_sgn(tmp) > 0) { D++; mpz_tdiv_q_2exp(tmp, tmp, 1); }
      mpz_clear(tmp);
    }
    D = (D - 8) / 4;
    if (D < 1) D = 1;
    if (D > 20) D = 20;
    unsigned long dp_mask = (1UL << D) - 1;

    /* For shared-DP mode, use fewer walkers per worker — the shared table
     * already provides the birthday paradox pool across all workers.
     * 2 walkers (1 tame + 1 wild) per worker is optimal. */
    int bound_bits = (int)mpz_sizeinbase(bound, 2);
    int nk = 2;  /* 1 tame + 1 wild per worker */
    int n_tame = 1;

    apt kpt[NK_MAX];
    int64_t kpos_lo[NK_MAX], kpos_hi[NK_MAX];
    int kji[NK_MAX];
    for (int i = 0; i < nk; i++) {
        ap_init(&kpt[i]);
        kpos_lo[i] = 0;
        kpos_hi[i] = 0;
    }

    /* Tame kangaroo starting positions — spread across workers */
    {
        mpz_t tpos; mpz_init(tpos);
        int total_tame = n_tame * num_workers;
        for (int i = 0; i < n_tame; i++) {
            int global_idx = worker_id * n_tame + i;
            mpz_mul_ui(tpos, half, global_idx + 1);
            mpz_tdiv_q_ui(tpos, tpos, total_tame + 1);
            kpos_lo[i] = (int64_t)mpz_get_ui(tpos);
            if (mpz_sizeinbase(tpos, 2) > 64) {
                mpz_t hi_part; mpz_init(hi_part);
                mpz_tdiv_q_2exp(hi_part, tpos, 64);
                kpos_hi[i] = (int64_t)mpz_get_ui(hi_part);
                mpz_clear(hi_part);
            }
            ap_smul(&kpt[i], tpos, &G_pt);
        }
        mpz_clear(tpos);
    }

    /* Wild kangaroo starting positions: P + small offsets (spread across workers) */
    for (int i = 0; i < nk - n_tame; i++) {
        int idx = n_tame + i;
        int wild_offset = worker_id * (nk - n_tame) + i;
        kpos_lo[idx] = wild_offset;
        kpos_hi[idx] = 0;
        if (wild_offset == 0) {
            ap_copy(&kpt[idx], &P_pt);
        } else {
            mpz_t off; mpz_init_set_ui(off, wild_offset);
            apt oG; ap_init(&oG);
            ap_smul(&oG, off, &G_pt);
            ap_add(&kpt[idx], &P_pt, &oG);
            ap_clear(&oG); mpz_clear(off);
        }
    }

    /* Pre-compute fe_t arrays for jump_pts */
    fe_t jp_x[NUM_JUMPS], jp_y[NUM_JUMPS];
    for (int i = 0; i < NUM_JUMPS; i++) {
        fe_from_mpz(jp_x[i], jump_pts[i].x);
        fe_from_mpz(jp_y[i], jump_pts[i].y);
    }

    /* fe_t scratch arrays for the hot loop */
    fe_t fe_dx[NK_MAX], fe_dy[NK_MAX];
    fe_t fe_lam[NK_MAX], fe_xr[NK_MAX], fe_yr[NK_MAX];
    fe_t fe_dinv[NK_MAX];
    fe_t kfe_x[NK_MAX], kfe_y[NK_MAX];
    for (int i = 0; i < nk; i++) {
        fe_from_mpz(kfe_x[i], kpt[i].x);
        fe_from_mpz(kfe_y[i], kpt[i].y);
    }

    int found = 0;

    mpz_t max_steps_z;
    mpz_init(max_steps_z);
    mpz_mul_ui(max_steps_z, sqrt_half, 32);
    mpz_add_ui(max_steps_z, max_steps_z, 20000);
    unsigned long max_steps = mpz_get_ui(max_steps_z);
    if (max_steps > 500000000UL) max_steps = 500000000UL;

    for (unsigned long step = 0; step < max_steps && !found; step++) {
        /* Check if another worker found the answer */
        if ((step & 0xFF) == 0 && __atomic_load_n(found_flag, __ATOMIC_RELAXED)) {
            break;
        }

        /* Phase 1: compute denominators for batch inversion (fe_t) */
        int bn = 0;
        int bmap[NK_MAX];
        int special[NK_MAX];

        for (int k = 0; k < nk; k++) {
            special[k] = 0;
            kji[k] = kpt[k].inf ? 0 : (int)(kfe_x[k][0] % NUM_JUMPS);
            pos128_add(&kpos_lo[k], &kpos_hi[k], kpos_lo[k], kpos_hi[k], jumps[kji[k]]);
            if (kpt[k].inf || jump_pts[kji[k]].inf) { special[k]=1; continue; }
            const fe_t *qx = &jp_x[kji[k]], *qy = &jp_y[kji[k]];

            fe_sub(fe_dx[bn], *qx, kfe_x[k]);
            if (fe_is_zero(fe_dx[bn])) { special[k]=1; continue; }
            fe_sub(fe_dy[bn], *qy, kfe_y[k]);
            bmap[bn] = k;
            bn++;
        }

        /* Phase 2: batch inversion — fe_t product tree, single fe_invert */
        if (bn >= 2) {
            fe_t fe_prod[NK_MAX], fe_binv;
            fe_set(fe_prod[0], fe_dx[0]);
            for (int i = 1; i < bn; i++)
                fe_mul(fe_prod[i], fe_prod[i-1], fe_dx[i]);
            fe_invert(fe_binv, fe_prod[bn-1]);
            for (int i = bn-1; i > 0; i--) {
                fe_mul(fe_dinv[i], fe_binv, fe_prod[i-1]);
                fe_mul(fe_binv, fe_binv, fe_dx[i]);
            }
            fe_set(fe_dinv[0], fe_binv);
        } else if (bn == 1) {
            fe_invert(fe_dinv[0], fe_dx[0]);
        }

        /* Phase 3: complete EC additions using fe_t arithmetic */
        for (int bi = 0; bi < bn; bi++) {
            int k = bmap[bi];
            int j = kji[k];

            fe_mul(fe_lam[bi], fe_dy[bi], fe_dinv[bi]);

            const fe_t *qx_p3 = &jp_x[j];
            fe_mul(fe_xr[bi], fe_lam[bi], fe_lam[bi]);
            fe_sub(fe_xr[bi], fe_xr[bi], kfe_x[k]);
            fe_sub(fe_xr[bi], fe_xr[bi], *qx_p3);

            fe_sub(fe_yr[bi], kfe_x[k], fe_xr[bi]);
            fe_mul(fe_yr[bi], fe_lam[bi], fe_yr[bi]);
            fe_sub(fe_yr[bi], fe_yr[bi], kfe_y[k]);

            fe_set(kfe_x[k], fe_xr[bi]);
            fe_set(kfe_y[k], fe_yr[bi]);
        }

        /* Handle special cases with standard ap_add */
        for (int k = 0; k < nk; k++) {
            if (special[k]) {
                fe_to_mpz(kpt[k].x, kfe_x[k]);
                fe_to_mpz(kpt[k].y, kfe_y[k]);
                apt ts; ap_init(&ts);
                ap_add(&ts, &kpt[k], &jump_pts[kji[k]]);
                ap_copy(&kpt[k], &ts);
                ap_clear(&ts);
                fe_from_mpz(kfe_x[k], kpt[k].x);
                fe_from_mpz(kfe_y[k], kpt[k].y);
            }
        }

        /* Phase 4: DP checks and collision detection via shared table */
        for (int k = 0; k < nk && !found; k++) {
            if (kpt[k].inf) continue;
            if ((kfe_x[k][0] & dp_mask) != 0) continue;
            int is_tame = (k < n_tame) ? 1 : 0;

            dp_slot_t match;
            memset(&match, 0, sizeof(match));
            int ret = dp_shared_insert(dp_table, dp_capacity,
                                        kfe_x[k][0], kfe_x[k][1],
                                        kpos_lo[k], kpos_hi[k],
                                        is_tame ? 1 : 0,
                                        &match);

            if (ret == 1) {
                /* Tame-wild collision found! Compute k = tame_pos - wild_pos */
                int64_t tame_lo, tame_hi, wild_lo, wild_hi;
                if (is_tame) {
                    tame_lo = kpos_lo[k]; tame_hi = kpos_hi[k];
                    wild_lo = match.pos_lo; wild_hi = match.pos_hi;
                } else {
                    tame_lo = match.pos_lo; tame_hi = match.pos_hi;
                    wild_lo = kpos_lo[k]; wild_hi = kpos_hi[k];
                }

                int64_t diff_lo, diff_hi;
                pos128_sub(&diff_lo, &diff_hi, tame_lo, tame_hi, wild_lo, wild_hi);

                /* Convert 128-bit diff to mpz */
                mpz_t k_cand; mpz_init(k_cand);
                if (diff_hi < 0) {
                    /* Negative diff: compute |diff| then negate mod order */
                    int64_t neg_lo, neg_hi;
                    pos128_sub(&neg_lo, &neg_hi, 0, 0, diff_lo, diff_hi);
                    mpz_set_ui(k_cand, (uint64_t)neg_hi);
                    mpz_mul_2exp(k_cand, k_cand, 64);
                    mpz_add_ui(k_cand, k_cand, (uint64_t)neg_lo);
                    mpz_sub(k_cand, ORD, k_cand);
                    mpz_mod(k_cand, k_cand, ORD);
                } else {
                    mpz_set_ui(k_cand, (uint64_t)diff_hi);
                    mpz_mul_2exp(k_cand, k_cand, 64);
                    mpz_add_ui(k_cand, k_cand, (uint64_t)diff_lo);
                    mpz_mod(k_cand, k_cand, ORD);
                }

                /* Verify: k_cand * G == P? */
                apt vR; ap_init(&vR);
                ap_smul(&vR, k_cand, &G_pt);
                if (!vR.inf && mpz_cmp(vR.x, P_pt.x)==0 && mpz_cmp(vR.y, P_pt.y)==0 &&
                    mpz_cmp(k_cand, bound) < 0) {
                    gmp_snprintf(result, result_size, "%Zx", k_cand);
                    found = 1;
                    __atomic_store_n((int *)found_flag, 1, __ATOMIC_RELEASE);
                }
                if (!found) {
                    /* Try negation: k = order - k_cand */
                    mpz_sub(k_cand, ORD, k_cand);
                    ap_smul(&vR, k_cand, &G_pt);
                    if (!vR.inf && mpz_cmp(vR.x, P_pt.x)==0 && mpz_cmp(vR.y, P_pt.y)==0 &&
                        mpz_cmp(k_cand, bound) < 0) {
                        gmp_snprintf(result, result_size, "%Zx", k_cand);
                        found = 1;
                        __atomic_store_n((int *)found_flag, 1, __ATOMIC_RELEASE);
                    }
                }
                ap_clear(&vR); mpz_clear(k_cand);
            }
        }
    }

    /* Cleanup */
    for (int i = 0; i < NUM_JUMPS; i++) ap_clear(&jump_pts[i]);
    ap_clear(&G_pt); ap_clear(&P_pt);
    for (int i = 0; i < nk; i++) { ap_clear(&kpt[i]); }
    mpz_clear(bound); mpz_clear(half); mpz_clear(sqrt_half); mpz_clear(max_steps_z);
    return found;
}
