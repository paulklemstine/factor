/*
 * ec_kangaroo_gpu.cu — GPU-accelerated Pollard kangaroo for secp256k1 ECDLP.
 *
 * Each CUDA thread runs one independent kangaroo walk (tame or wild).
 * Field arithmetic: 256-bit using 4x uint64_t limbs with secp256k1 fast reduction.
 * Coordinates: JACOBIAN (X, Y, Z) during walk — eliminates per-step inversion.
 *   Fermat inversion only at DP hits (~1 in 2^D steps).
 * Jump table: 64 Pythagorean hypotenuse jumps in __constant__ memory (affine).
 * DP detection: distinguished points written to global buffer, CPU checks collisions.
 *
 * Compile:
 *   nvcc -O3 -arch=sm_89 -shared -Xcompiler -fPIC -o ec_kangaroo_gpu.so ec_kangaroo_gpu.cu
 *
 * C-callable interface for Python ctypes integration.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

/* ================================================================
 * 256-bit field element: 4 x uint64_t limbs (little-endian)
 * secp256k1: p = 2^256 - 2^32 - 977
 * ================================================================ */

typedef struct { uint64_t v[4]; } fe_t;

/* Distinguished point entry for CPU collision detection */
typedef struct {
    uint64_t x_hash;
    uint64_t x1, x2, x3, x4;
    uint64_t pos_lo;
    uint64_t pos_hi;
    uint32_t is_tame;
    uint32_t thread_id;
} dp_entry_t;

/* ================================================================
 * Constants in __constant__ memory
 * ================================================================ */

__constant__ uint64_t FE_P[4] = {
    0xFFFFFFFEFFFFFC2FULL, 0xFFFFFFFFFFFFFFFFULL,
    0xFFFFFFFFFFFFFFFFULL, 0xFFFFFFFFFFFFFFFFULL
};

#define FE_PC 0x1000003D1ULL

__constant__ uint64_t JUMP_X[64][4];
__constant__ uint64_t JUMP_Y[64][4];
__constant__ uint64_t JUMP_DIST[64];

/* Steps per kernel launch — set by host based on problem size */
static int g_steps_per_launch = 2048;

/* ================================================================
 * Device field arithmetic
 * ================================================================ */

__device__ __forceinline__ void fe_set(fe_t *r, const fe_t *a) {
    r->v[0] = a->v[0]; r->v[1] = a->v[1];
    r->v[2] = a->v[2]; r->v[3] = a->v[3];
}

__device__ __forceinline__ int fe_is_zero(const fe_t *a) {
    return (a->v[0] | a->v[1] | a->v[2] | a->v[3]) == 0;
}

/* r = a + b mod p */
__device__ __forceinline__ void fe_add(fe_t *r, const fe_t *a, const fe_t *b) {
    unsigned __int128 acc;
    uint64_t carry = 0;
    acc = (unsigned __int128)a->v[0] + b->v[0]; r->v[0] = (uint64_t)acc; carry = (uint64_t)(acc >> 64);
    acc = (unsigned __int128)a->v[1] + b->v[1] + carry; r->v[1] = (uint64_t)acc; carry = (uint64_t)(acc >> 64);
    acc = (unsigned __int128)a->v[2] + b->v[2] + carry; r->v[2] = (uint64_t)acc; carry = (uint64_t)(acc >> 64);
    acc = (unsigned __int128)a->v[3] + b->v[3] + carry; r->v[3] = (uint64_t)acc; carry = (uint64_t)(acc >> 64);

    uint64_t borrow = 0; uint64_t t[4]; unsigned __int128 diff;
    diff = (unsigned __int128)r->v[0] - FE_P[0]; t[0] = (uint64_t)diff; borrow = (diff >> 127) ? 1 : 0;
    diff = (unsigned __int128)r->v[1] - FE_P[1] - borrow; t[1] = (uint64_t)diff; borrow = (diff >> 127) ? 1 : 0;
    diff = (unsigned __int128)r->v[2] - FE_P[2] - borrow; t[2] = (uint64_t)diff; borrow = (diff >> 127) ? 1 : 0;
    diff = (unsigned __int128)r->v[3] - FE_P[3] - borrow; t[3] = (uint64_t)diff; borrow = (diff >> 127) ? 1 : 0;

    uint64_t mask = (carry | (borrow ^ 1)) ? 0xFFFFFFFFFFFFFFFFULL : 0;
    r->v[0] = (t[0] & mask) | (r->v[0] & ~mask);
    r->v[1] = (t[1] & mask) | (r->v[1] & ~mask);
    r->v[2] = (t[2] & mask) | (r->v[2] & ~mask);
    r->v[3] = (t[3] & mask) | (r->v[3] & ~mask);
}

/* r = a - b mod p */
__device__ __forceinline__ void fe_sub(fe_t *r, const fe_t *a, const fe_t *b) {
    unsigned __int128 diff;
    uint64_t borrow = 0;
    diff = (unsigned __int128)a->v[0] - b->v[0]; r->v[0] = (uint64_t)diff; borrow = (diff >> 127) ? 1 : 0;
    diff = (unsigned __int128)a->v[1] - b->v[1] - borrow; r->v[1] = (uint64_t)diff; borrow = (diff >> 127) ? 1 : 0;
    diff = (unsigned __int128)a->v[2] - b->v[2] - borrow; r->v[2] = (uint64_t)diff; borrow = (diff >> 127) ? 1 : 0;
    diff = (unsigned __int128)a->v[3] - b->v[3] - borrow; r->v[3] = (uint64_t)diff; borrow = (diff >> 127) ? 1 : 0;
    if (borrow) {
        uint64_t carry = 0; unsigned __int128 acc;
        acc = (unsigned __int128)r->v[0] + FE_P[0]; r->v[0] = (uint64_t)acc; carry = (uint64_t)(acc >> 64);
        acc = (unsigned __int128)r->v[1] + FE_P[1] + carry; r->v[1] = (uint64_t)acc; carry = (uint64_t)(acc >> 64);
        acc = (unsigned __int128)r->v[2] + FE_P[2] + carry; r->v[2] = (uint64_t)acc; carry = (uint64_t)(acc >> 64);
        acc = (unsigned __int128)r->v[3] + FE_P[3] + carry; r->v[3] = (uint64_t)acc;
    }
}

/*
 * Schoolbook 4x4 multiply with secp256k1 fast reduction.
 * Uses loop-based accumulation to avoid __int128 overflow on multi-term columns.
 */
__device__ void fe_mul(fe_t *r, const fe_t *a, const fe_t *b) {
    uint64_t t[8] = {0, 0, 0, 0, 0, 0, 0, 0};
    unsigned __int128 uv;
    uint64_t carry;

    for (int i = 0; i < 4; i++) {
        carry = 0;
        for (int j = 0; j < 4; j++) {
            uv = (unsigned __int128)a->v[i] * b->v[j] + t[i + j] + carry;
            t[i + j] = (uint64_t)uv;
            carry = (uint64_t)(uv >> 64);
        }
        t[i + 4] += carry;
    }

    /* Reduce: r = t[0..3] + t[4..7] * FE_PC mod 2^256, then final reduction */
    uint64_t h[5], cc;
    uv = (unsigned __int128)t[4] * FE_PC; h[0] = (uint64_t)uv; carry = (uint64_t)(uv >> 64);
    uv = (unsigned __int128)t[5] * FE_PC + carry; h[1] = (uint64_t)uv; carry = (uint64_t)(uv >> 64);
    uv = (unsigned __int128)t[6] * FE_PC + carry; h[2] = (uint64_t)uv; carry = (uint64_t)(uv >> 64);
    uv = (unsigned __int128)t[7] * FE_PC + carry; h[3] = (uint64_t)uv; h[4] = (uint64_t)(uv >> 64);

    uint64_t a5[5];
    uv = (unsigned __int128)t[0] + h[0]; a5[0] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
    uv = (unsigned __int128)t[1] + h[1] + cc; a5[1] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
    uv = (unsigned __int128)t[2] + h[2] + cc; a5[2] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
    uv = (unsigned __int128)t[3] + h[3] + cc; a5[3] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
    a5[4] = h[4] + cc;

    /* Fold a5[4] back in */
    if (a5[4]) {
        uv = (unsigned __int128)a5[4] * FE_PC;
        uint64_t ov_lo = (uint64_t)uv, ov_hi = (uint64_t)(uv >> 64);
        uv = (unsigned __int128)a5[0] + ov_lo; a5[0] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
        uv = (unsigned __int128)a5[1] + ov_hi + cc; a5[1] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
        if (cc) { uv = (unsigned __int128)a5[2] + cc; a5[2] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
        if (cc) { uv = (unsigned __int128)a5[3] + cc; a5[3] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
        if (cc) { uv = (unsigned __int128)a5[0] + FE_PC; a5[0] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
        if (cc) { a5[1]++; if (a5[1] == 0) { a5[2]++; if (a5[2] == 0) a5[3]++; } } } } }
    }

    r->v[0] = a5[0]; r->v[1] = a5[1]; r->v[2] = a5[2]; r->v[3] = a5[3];

    /* If r >= p, subtract p */
    int ge_p = 0;
    if (r->v[3] > FE_P[3]) ge_p = 1;
    else if (r->v[3] == FE_P[3]) {
        if (r->v[2] > FE_P[2]) ge_p = 1;
        else if (r->v[2] == FE_P[2]) {
            if (r->v[1] > FE_P[1]) ge_p = 1;
            else if (r->v[1] == FE_P[1]) {
                if (r->v[0] >= FE_P[0]) ge_p = 1;
            }
        }
    }
    if (ge_p) {
        unsigned __int128 d; uint64_t bw = 0;
        d = (unsigned __int128)r->v[0] - FE_P[0]; r->v[0] = (uint64_t)d; bw = (d >> 127) ? 1 : 0;
        d = (unsigned __int128)r->v[1] - FE_P[1] - bw; r->v[1] = (uint64_t)d; bw = (d >> 127) ? 1 : 0;
        d = (unsigned __int128)r->v[2] - FE_P[2] - bw; r->v[2] = (uint64_t)d; bw = (d >> 127) ? 1 : 0;
        d = (unsigned __int128)r->v[3] - FE_P[3] - bw; r->v[3] = (uint64_t)d;
    }
}

/*
 * Dedicated squaring: exploits a*a symmetry.
 * Computes cross-terms once, doubles them, then adds squared diagonals.
 * Uses a clean two-pass approach: first build cross*2, then add diag.
 */
__device__ void fe_sqr(fe_t *r, const fe_t *a) {
    unsigned __int128 uv;
    uint64_t t[8] = {0, 0, 0, 0, 0, 0, 0, 0};
    uint64_t carry;

    /* Pass 1: upper triangle cross-terms (i < j only) */
    for (int i = 0; i < 4; i++) {
        carry = 0;
        for (int j = i + 1; j < 4; j++) {
            uv = (unsigned __int128)a->v[i] * a->v[j] + t[i + j] + carry;
            t[i + j] = (uint64_t)uv;
            carry = (uint64_t)(uv >> 64);
        }
        t[i + 4] += carry;
    }

    /* Double the cross-terms */
    t[7] = (t[7] << 1) | (t[6] >> 63);
    t[6] = (t[6] << 1) | (t[5] >> 63);
    t[5] = (t[5] << 1) | (t[4] >> 63);
    t[4] = (t[4] << 1) | (t[3] >> 63);
    t[3] = (t[3] << 1) | (t[2] >> 63);
    t[2] = (t[2] << 1) | (t[1] >> 63);
    t[1] = t[1] << 1;

    /* Pass 2: add diagonal terms a[i]*a[i] */
    uint64_t cc = 0;
    for (int i = 0; i < 4; i++) {
        uv = (unsigned __int128)a->v[i] * a->v[i];
        uint64_t dlo = (uint64_t)uv, dhi = (uint64_t)(uv >> 64);
        uv = (unsigned __int128)t[2*i] + dlo + cc;
        t[2*i] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
        uv = (unsigned __int128)t[2*i+1] + dhi + cc;
        t[2*i+1] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
    }

    /* Reduce using secp256k1 fast reduction (same as fe_mul) */
    uint64_t h[5];
    uv = (unsigned __int128)t[4] * FE_PC; h[0] = (uint64_t)uv; carry = (uint64_t)(uv >> 64);
    uv = (unsigned __int128)t[5] * FE_PC + carry; h[1] = (uint64_t)uv; carry = (uint64_t)(uv >> 64);
    uv = (unsigned __int128)t[6] * FE_PC + carry; h[2] = (uint64_t)uv; carry = (uint64_t)(uv >> 64);
    uv = (unsigned __int128)t[7] * FE_PC + carry; h[3] = (uint64_t)uv; h[4] = (uint64_t)(uv >> 64);

    uint64_t a5[5];
    uv = (unsigned __int128)t[0] + h[0]; a5[0] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
    uv = (unsigned __int128)t[1] + h[1] + cc; a5[1] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
    uv = (unsigned __int128)t[2] + h[2] + cc; a5[2] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
    uv = (unsigned __int128)t[3] + h[3] + cc; a5[3] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
    a5[4] = h[4] + cc;

    if (a5[4]) {
        uv = (unsigned __int128)a5[4] * FE_PC;
        uint64_t ov_lo = (uint64_t)uv, ov_hi = (uint64_t)(uv >> 64);
        uv = (unsigned __int128)a5[0] + ov_lo; a5[0] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
        uv = (unsigned __int128)a5[1] + ov_hi + cc; a5[1] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
        if (cc) { uv = (unsigned __int128)a5[2] + cc; a5[2] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
        if (cc) { uv = (unsigned __int128)a5[3] + cc; a5[3] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
        if (cc) { uv = (unsigned __int128)a5[0] + FE_PC; a5[0] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
        if (cc) { a5[1]++; if (a5[1] == 0) { a5[2]++; if (a5[2] == 0) a5[3]++; } } } } }
    }

    r->v[0] = a5[0]; r->v[1] = a5[1]; r->v[2] = a5[2]; r->v[3] = a5[3];

    int ge_p = 0;
    if (r->v[3] > FE_P[3]) ge_p = 1;
    else if (r->v[3] == FE_P[3]) {
        if (r->v[2] > FE_P[2]) ge_p = 1;
        else if (r->v[2] == FE_P[2]) {
            if (r->v[1] > FE_P[1]) ge_p = 1;
            else if (r->v[1] == FE_P[1]) {
                if (r->v[0] >= FE_P[0]) ge_p = 1;
            }
        }
    }
    if (ge_p) {
        unsigned __int128 d; uint64_t bw = 0;
        d = (unsigned __int128)r->v[0] - FE_P[0]; r->v[0] = (uint64_t)d; bw = (d >> 127) ? 1 : 0;
        d = (unsigned __int128)r->v[1] - FE_P[1] - bw; r->v[1] = (uint64_t)d; bw = (d >> 127) ? 1 : 0;
        d = (unsigned __int128)r->v[2] - FE_P[2] - bw; r->v[2] = (uint64_t)d; bw = (d >> 127) ? 1 : 0;
        d = (unsigned __int128)r->v[3] - FE_P[3] - bw; r->v[3] = (uint64_t)d;
    }
}

/*
 * Bernstein-Yang constant-time modular inversion via divsteps.
 * Replaces Fermat inversion (a^(p-2) mod p) with shift/add algorithm.
 *
 * Reference: "Fast constant-time gcd computation and modular inversion"
 *            Daniel J. Bernstein, Bo-Yin Yang, 2019
 * Adapted from libsecp256k1 src/modinv64_impl.h
 *
 * Uses 5-limb signed representation (4x62 bits + overflow limb).
 * 12 batches of 62 divsteps = 744 total (need >= 2*256+1 = 513).
 */

/* Signed 5-limb representation: value = sum(v[i] * 2^(62*i)) */
typedef struct { int64_t v[5]; } sd_t;

/* Transition matrix from 62 divsteps */
typedef struct { int64_t u, v, q, r; } trans_t;

/* Compute 62 divsteps on low bits of f, g.
 * Produces transition matrix T such that [f',g'] = T * [f,g] / 2^62.
 * All operations are branchless via bitwise masking.
 *
 * Uses the Bernstein-Yang divstep:
 *   if delta > 0 and g odd: (delta,f,g) = (1-delta, g, (g-f)/2)
 *   elif g odd:             (delta,f,g) = (1+delta, f, (g+f)/2)
 *   else:                   (delta,f,g) = (1+delta, f, g/2)
 *
 * After conditional swap, g is conditionally negated before adding f
 * to implement the subtract-when-swapped semantics. */
__device__ void divsteps_62(int64_t *delta, uint64_t f0, uint64_t g0,
                            trans_t *t) {
    int64_t du = 1, dv = 0, dq = 0, dr = 1;
    int64_t d = *delta;
    uint64_t f = f0, g = g0;

    for (int i = 0; i < 62; i++) {
        /* cond = -1 if (delta > 0 AND g is odd), else 0 */
        int64_t g_odd = -((int64_t)(g & 1));
        int64_t d_pos = -((int64_t)((uint64_t)(-d) >> 63)); /* -1 if d > 0, 0 if d <= 0 */
        int64_t swap = g_odd & d_pos; /* -1 if should swap */

        /* Conditional negate delta: if swap, delta = -delta */
        d = (d ^ swap) - swap;

        /* Conditional swap f <-> g */
        uint64_t tf = ((f ^ g) & (uint64_t)swap);
        f ^= tf; g ^= tf;

        /* Conditional swap (du,dv) <-> (dq,dr) */
        int64_t tt;
        tt = (du ^ dq) & swap; du ^= tt; dq ^= tt;
        tt = (dv ^ dr) & swap; dv ^= tt; dr ^= tt;

        /* When g is odd: conditionally negate g then add f.
         * Implements g-f when swapped, g+f when not swapped.
         * neg_g = swap ? -g : g = (g ^ swap) - swap
         * When g is even (g_odd=0): g stays unchanged, no addition needed. */
        uint64_t neg_g = (g ^ (uint64_t)swap) - (uint64_t)swap;
        g = ((neg_g + f) & (uint64_t)g_odd) | (g & ~(uint64_t)g_odd);
        /* Matrix: same logic for (dq,dr) row */
        int64_t neg_dq = (dq ^ swap) - swap;
        int64_t neg_dr = (dr ^ swap) - swap;
        dq = ((neg_dq + du) & g_odd) | (dq & ~g_odd);
        dr = ((neg_dr + dv) & g_odd) | (dr & ~g_odd);

        /* g >>= 1, scale matrix row */
        g >>= 1;
        du <<= 1;
        dv <<= 1;

        d++;
    }

    *delta = d;
    t->u = du; t->v = dv; t->q = dq; t->r = dr;
}

/* Update (f, g) using transition matrix: [f,g] = T * [f,g] / 2^62.
 * f, g are signed 5-limb (62-bit limbs). Result is exact (no mod). */
__device__ void modinv_update_fg(sd_t *f, sd_t *g, const trans_t *t) {
    /* Compute cf = u*f + v*g and cg = q*f + r*g using 128-bit intermediates.
     * Each limb is 62 bits; matrix entries are at most 62 bits magnitude. */
    int64_t u = t->u, v = t->v, q = t->q, rr = t->r;
    __int128 cf0, cf1, cf2, cf3, cf4;
    __int128 cg0, cg1, cg2, cg3, cg4;

    cf0 = (__int128)u * f->v[0] + (__int128)v * g->v[0];
    cf1 = (__int128)u * f->v[1] + (__int128)v * g->v[1];
    cf2 = (__int128)u * f->v[2] + (__int128)v * g->v[2];
    cf3 = (__int128)u * f->v[3] + (__int128)v * g->v[3];
    cf4 = (__int128)u * f->v[4] + (__int128)v * g->v[4];

    cg0 = (__int128)q * f->v[0] + (__int128)rr * g->v[0];
    cg1 = (__int128)q * f->v[1] + (__int128)rr * g->v[1];
    cg2 = (__int128)q * f->v[2] + (__int128)rr * g->v[2];
    cg3 = (__int128)q * f->v[3] + (__int128)rr * g->v[3];
    cg4 = (__int128)q * f->v[4] + (__int128)rr * g->v[4];

    /* Divide by 2^62: shift right, propagating carries between limbs */
    cf0 >>= 62; cf0 += cf1;
    cf1 = cf0 >> 62; cf1 += cf2;
    cf2 = cf1 >> 62; cf2 += cf3;
    cf3 = cf2 >> 62; cf3 += cf4;
    cf4 = cf3 >> 62;

    f->v[0] = (int64_t)cf0 & 0x3FFFFFFFFFFFFFFFLL;
    f->v[1] = (int64_t)cf1 & 0x3FFFFFFFFFFFFFFFLL;
    f->v[2] = (int64_t)cf2 & 0x3FFFFFFFFFFFFFFFLL;
    f->v[3] = (int64_t)cf3 & 0x3FFFFFFFFFFFFFFFLL;
    f->v[4] = (int64_t)cf4;

    cg0 >>= 62; cg0 += cg1;
    cg1 = cg0 >> 62; cg1 += cg2;
    cg2 = cg1 >> 62; cg2 += cg3;
    cg3 = cg2 >> 62; cg3 += cg4;
    cg4 = cg3 >> 62;

    g->v[0] = (int64_t)cg0 & 0x3FFFFFFFFFFFFFFFLL;
    g->v[1] = (int64_t)cg1 & 0x3FFFFFFFFFFFFFFFLL;
    g->v[2] = (int64_t)cg2 & 0x3FFFFFFFFFFFFFFFLL;
    g->v[3] = (int64_t)cg3 & 0x3FFFFFFFFFFFFFFFLL;
    g->v[4] = (int64_t)cg4;
}

/* Update (d, e) mod p using transition matrix.
 * d_new = (u*d + v*e) mod p, e_new = (q*d + r*e) mod p.
 *
 * We need to compute (u*d + v*e) / 2^62 mod p.
 * Since u*d + v*e ≡ 0 (mod 2^62) by construction,
 * we compute the exact quotient then reduce mod p.
 *
 * To divide by 2^62 mod p, we multiply the low 62 bits
 * by p's inverse mod 2^62, add the correction, then shift.
 */
__device__ void modinv_update_de(sd_t *d, sd_t *e, const trans_t *t) {
    /* secp256k1 p in 62-bit limbs (5 limbs), precomputed */
    const int64_t M62 = 0x3FFFFFFFFFFFFFFFLL;  /* (1 << 62) - 1 */
    const int64_t p0 = 0x3FFFFFFEFFFFFC2FLL;
    const int64_t p1 = 0x3FFFFFFFFFFFFFFFLL;
    const int64_t p2 = 0x3FFFFFFFFFFFFFFFLL;
    const int64_t p3 = 0x3FFFFFFFFFFFFFFFLL;
    const int64_t p4 = 0x00000000000000FFLL;

    int64_t u = t->u, v = t->v, q = t->q, rr = t->r;

    /* Compute u*d + v*e and q*d + r*e (each up to ~320 bits) */
    __int128 cd0 = (__int128)u * d->v[0] + (__int128)v * e->v[0];
    __int128 cd1 = (__int128)u * d->v[1] + (__int128)v * e->v[1];
    __int128 cd2 = (__int128)u * d->v[2] + (__int128)v * e->v[2];
    __int128 cd3 = (__int128)u * d->v[3] + (__int128)v * e->v[3];
    __int128 cd4 = (__int128)u * d->v[4] + (__int128)v * e->v[4];

    __int128 ce0 = (__int128)q * d->v[0] + (__int128)rr * e->v[0];
    __int128 ce1 = (__int128)q * d->v[1] + (__int128)rr * e->v[1];
    __int128 ce2 = (__int128)q * d->v[2] + (__int128)rr * e->v[2];
    __int128 ce3 = (__int128)q * d->v[3] + (__int128)rr * e->v[3];
    __int128 ce4 = (__int128)q * d->v[4] + (__int128)rr * e->v[4];

    /* Compute md = -(cd mod 2^62) * (p_inv mod 2^62) mod 2^62.
     * For secp256k1, p^(-1) mod 2^62 = 0x27C7F6E22DDACACF (precomputed).
     * md * p will cancel the low 62 bits of cd. */
    /* (-p)^(-1) mod 2^62, so that cd0 + md*p ≡ 0 (mod 2^62) */
    const int64_t modp_inv62 = (int64_t)0x1838091DD2253531LL;

    int64_t md = (int64_t)cd0 * modp_inv62;
    md &= M62;
    int64_t me = (int64_t)ce0 * modp_inv62;
    me &= M62;

    /* Add md*p to cd, me*p to ce */
    cd0 += (__int128)md * p0;
    cd1 += (__int128)md * p1;
    cd2 += (__int128)md * p2;
    cd3 += (__int128)md * p3;
    cd4 += (__int128)md * p4;

    ce0 += (__int128)me * p0;
    ce1 += (__int128)me * p1;
    ce2 += (__int128)me * p2;
    ce3 += (__int128)me * p3;
    ce4 += (__int128)me * p4;

    /* Now cd0 and ce0 are divisible by 2^62. Shift right and propagate. */
    cd0 >>= 62; cd0 += cd1;
    cd1 = cd0 >> 62; cd1 += cd2;
    cd2 = cd1 >> 62; cd2 += cd3;
    cd3 = cd2 >> 62; cd3 += cd4;
    cd4 = cd3 >> 62;

    d->v[0] = (int64_t)cd0 & M62;
    d->v[1] = (int64_t)cd1 & M62;
    d->v[2] = (int64_t)cd2 & M62;
    d->v[3] = (int64_t)cd3 & M62;
    d->v[4] = (int64_t)cd4;

    ce0 >>= 62; ce0 += ce1;
    ce1 = ce0 >> 62; ce1 += ce2;
    ce2 = ce1 >> 62; ce2 += ce3;
    ce3 = ce2 >> 62; ce3 += ce4;
    ce4 = ce3 >> 62;

    e->v[0] = (int64_t)ce0 & M62;
    e->v[1] = (int64_t)ce1 & M62;
    e->v[2] = (int64_t)ce2 & M62;
    e->v[3] = (int64_t)ce3 & M62;
    e->v[4] = (int64_t)ce4;
}

/* Normalize a signed 5-limb number mod p to a 4-limb fe_t.
 * Input may be negative or larger than p. */
__device__ void sd_to_fe(fe_t *r, const sd_t *a) {
    const int64_t M62 = 0x3FFFFFFFFFFFFFFFLL;

    /* First normalize limbs so each is in [0, 2^62) */
    int64_t v0 = a->v[0], v1 = a->v[1], v2 = a->v[2], v3 = a->v[3], v4 = a->v[4];

    /* Propagate carries */
    v1 += v0 >> 62; v0 &= M62;
    v2 += v1 >> 62; v1 &= M62;
    v3 += v2 >> 62; v2 &= M62;
    v4 += v3 >> 62; v3 &= M62;

    /* Convert from 62-bit limbs to 64-bit limbs */
    /* 62-bit layout: bits [0..61] in v0, [62..123] in v1, [124..185] in v2, [186..247] in v3, [248..] in v4 */
    uint64_t r0 = ((uint64_t)v0) | (((uint64_t)v1) << 62);
    uint64_t r1 = (((uint64_t)v1) >> 2) | (((uint64_t)v2) << 60);
    uint64_t r2 = (((uint64_t)v2) >> 4) | (((uint64_t)v3) << 58);
    uint64_t r3 = (((uint64_t)v3) >> 6) | (((uint64_t)v4) << 56);

    /* If the number is negative (v4's sign bit set), add p */
    int64_t neg = v4 >> 63;  /* -1 if negative, 0 if positive */
    if (neg) {
        unsigned __int128 acc;
        uint64_t carry = 0;
        acc = (unsigned __int128)r0 + FE_P[0]; r0 = (uint64_t)acc; carry = (uint64_t)(acc >> 64);
        acc = (unsigned __int128)r1 + FE_P[1] + carry; r1 = (uint64_t)acc; carry = (uint64_t)(acc >> 64);
        acc = (unsigned __int128)r2 + FE_P[2] + carry; r2 = (uint64_t)acc; carry = (uint64_t)(acc >> 64);
        acc = (unsigned __int128)r3 + FE_P[3] + carry; r3 = (uint64_t)acc;
    }

    r->v[0] = r0; r->v[1] = r1; r->v[2] = r2; r->v[3] = r3;

    /* Final reduction: if r >= p, subtract p */
    int ge_p = 0;
    if (r->v[3] > FE_P[3]) ge_p = 1;
    else if (r->v[3] == FE_P[3]) {
        if (r->v[2] > FE_P[2]) ge_p = 1;
        else if (r->v[2] == FE_P[2]) {
            if (r->v[1] > FE_P[1]) ge_p = 1;
            else if (r->v[1] == FE_P[1]) {
                if (r->v[0] >= FE_P[0]) ge_p = 1;
            }
        }
    }
    if (ge_p) {
        unsigned __int128 dd; uint64_t bw = 0;
        dd = (unsigned __int128)r->v[0] - FE_P[0]; r->v[0] = (uint64_t)dd; bw = (dd >> 127) ? 1 : 0;
        dd = (unsigned __int128)r->v[1] - FE_P[1] - bw; r->v[1] = (uint64_t)dd; bw = (dd >> 127) ? 1 : 0;
        dd = (unsigned __int128)r->v[2] - FE_P[2] - bw; r->v[2] = (uint64_t)dd; bw = (dd >> 127) ? 1 : 0;
        dd = (unsigned __int128)r->v[3] - FE_P[3] - bw; r->v[3] = (uint64_t)dd;
    }
}

/* Convert fe_t (4x64-bit limbs) to sd_t (5x62-bit signed limbs) */
__device__ void fe_to_sd(sd_t *r, const fe_t *a) {
    const int64_t M62 = 0x3FFFFFFFFFFFFFFFLL;
    r->v[0] = (int64_t)(a->v[0] & (uint64_t)M62);
    r->v[1] = (int64_t)((a->v[0] >> 62) | ((a->v[1] & 0x0FFFFFFFFFFFFFFFULL) << 2));
    r->v[2] = (int64_t)((a->v[1] >> 60) | ((a->v[2] & 0x03FFFFFFFFFFFFFFULL) << 4));
    r->v[3] = (int64_t)((a->v[2] >> 58) | ((a->v[3] & 0x00FFFFFFFFFFFFFFULL) << 6));
    r->v[4] = (int64_t)(a->v[3] >> 56);
}

/*
 * Bernstein-Yang divstep modular inversion: r = a^(-1) mod p.
 * Uses 9 batches of 62 divsteps (558 total, need >= 513).
 */
__device__ void fe_inv(fe_t *r, const fe_t *a) {
    /* Initialize: f = p, g = a, d = 0, e = 1 */
    sd_t f, g, d, e;

    /* f = p in 62-bit limbs (precomputed) */
    f.v[0] = 0x3FFFFFFEFFFFFC2FLL;
    f.v[1] = 0x3FFFFFFFFFFFFFFFLL;
    f.v[2] = 0x3FFFFFFFFFFFFFFFLL;
    f.v[3] = 0x3FFFFFFFFFFFFFFFLL;
    f.v[4] = 0x00000000000000FFLL;

    fe_to_sd(&g, a);

    /* d = 0 */
    d.v[0] = 0; d.v[1] = 0; d.v[2] = 0; d.v[3] = 0; d.v[4] = 0;
    /* e = 1 */
    e.v[0] = 1; e.v[1] = 0; e.v[2] = 0; e.v[3] = 0; e.v[4] = 0;

    int64_t delta = 1;

    for (int i = 0; i < 9; i++) {
        trans_t t;

        /* Get low 62 bits of f and g for the scalar divsteps.
         * f and g have signed limbs, so reconstruct the low 64 bits. */
        uint64_t f0 = (uint64_t)f.v[0] | ((uint64_t)f.v[1] << 62);
        uint64_t g0 = (uint64_t)g.v[0] | ((uint64_t)g.v[1] << 62);

        divsteps_62(&delta, f0, g0, &t);
        modinv_update_fg(&f, &g, &t);
        modinv_update_de(&d, &e, &t);
    }

    /* At this point, |f| = 1 (the GCD).
     * If f = 1, result = d. If f = -1, result = -d mod p. */
    /* Check sign of f: reconstruct from limbs. f should be ±1.
     * For signed-digit representation, check if the value is negative
     * by looking at the top limb's sign. */
    int64_t f_neg = f.v[4] >> 63;  /* -1 if f is negative, 0 if positive */
    /* If f < 0, negate d: value = sum(v[i] * 2^(62*i)), so negate each limb */
    d.v[0] = (d.v[0] ^ f_neg) - f_neg;
    d.v[1] = (d.v[1] ^ f_neg) - f_neg;
    d.v[2] = (d.v[2] ^ f_neg) - f_neg;
    d.v[3] = (d.v[3] ^ f_neg) - f_neg;
    d.v[4] = (d.v[4] ^ f_neg) - f_neg;

    sd_to_fe(r, &d);
}

/* Negation: r = -a mod p */
__device__ __forceinline__ void fe_neg(fe_t *r, const fe_t *a) {
    fe_t zero = {{0, 0, 0, 0}};
    fe_sub(r, &zero, a);
}

/* ================================================================
 * Jacobian mixed addition: (X1,Y1,Z1) + affine (x2,y2)
 *
 * Given Jacobian P1=(X1,Y1,Z1) and affine P2=(x2,y2):
 *   U1 = X1,  U2 = x2*Z1^2,  S1 = Y1,  S2 = y2*Z1^3
 *   H = U2-U1,  R = S2-S1
 *   X3 = R^2 - H^3 - 2*U1*H^2
 *   Y3 = R*(U1*H^2 - X3) - S1*H^3
 *   Z3 = Z1 * H
 *
 * Cost: ~8 mul + 3 sqr.  No inversion!
 * ================================================================ */

__device__ void ec_madd_jacobian(fe_t *X3, fe_t *Y3, fe_t *Z3,
                                  const fe_t *X1, const fe_t *Y1, const fe_t *Z1,
                                  const fe_t *x2, const fe_t *y2) {
    fe_t Z1sq, Z1cu, U2, S2, H, Hsq, Hcu, R, Rsq, U1H2, t;

    fe_sqr(&Z1sq, Z1);           /* Z1^2 */
    fe_mul(&Z1cu, &Z1sq, Z1);    /* Z1^3 */
    fe_mul(&U2, x2, &Z1sq);      /* U2 = x2 * Z1^2 */
    fe_mul(&S2, y2, &Z1cu);      /* S2 = y2 * Z1^3 */

    fe_sub(&H, &U2, X1);         /* H = U2 - U1 (U1 = X1) */
    fe_sub(&R, &S2, Y1);         /* R = S2 - S1 (S1 = Y1) */

    fe_sqr(&Hsq, &H);            /* H^2 */
    fe_mul(&Hcu, &Hsq, &H);      /* H^3 */
    fe_mul(&U1H2, X1, &Hsq);     /* U1 * H^2 */

    fe_sqr(&Rsq, &R);            /* R^2 */
    fe_sub(X3, &Rsq, &Hcu);      /* X3 = R^2 - H^3 */
    fe_sub(X3, X3, &U1H2);       /* X3 -= U1*H^2 */
    fe_sub(X3, X3, &U1H2);       /* X3 -= U1*H^2 (second time: -2*U1*H^2) */

    fe_sub(&t, &U1H2, X3);       /* U1*H^2 - X3 */
    fe_mul(Y3, &R, &t);          /* R * (U1*H^2 - X3) */
    fe_mul(&t, Y1, &Hcu);        /* S1 * H^3 */
    fe_sub(Y3, Y3, &t);          /* Y3 = R*(U1*H^2-X3) - S1*H^3 */

    fe_mul(Z3, Z1, &H);          /* Z3 = Z1 * H */
}

/* ================================================================
 * Main kangaroo kernel — JACOBIAN coordinates
 *
 * Each kangaroo stores (X, Y, Z) in Jacobian form.
 * Walk uses mixed addition (Jacobian + affine jump point).
 * DP prefilter: check X[0] & dp_mask == 0 (cheap).
 * On prefilter hit: compute affine x via Fermat inversion, check real DP.
 * ================================================================ */

__global__ void kangaroo_walk_kernel(
    uint64_t *kang_x, uint64_t *kang_y, uint64_t *kang_z,
    uint64_t *kang_pos, uint64_t *kang_pos_hi, int *kang_inf,
    int num_kangaroos, int n_tame, uint64_t dp_mask,
    dp_entry_t *dp_buf, int *dp_count, int dp_buf_size,
    int *found_flag, int steps_per_launch)
{
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= num_kangaroos) return;
    if (*found_flag) return;

    fe_t cX, cY, cZ;
    cX.v[0] = kang_x[tid * 4 + 0]; cX.v[1] = kang_x[tid * 4 + 1];
    cX.v[2] = kang_x[tid * 4 + 2]; cX.v[3] = kang_x[tid * 4 + 3];
    cY.v[0] = kang_y[tid * 4 + 0]; cY.v[1] = kang_y[tid * 4 + 1];
    cY.v[2] = kang_y[tid * 4 + 2]; cY.v[3] = kang_y[tid * 4 + 3];
    cZ.v[0] = kang_z[tid * 4 + 0]; cZ.v[1] = kang_z[tid * 4 + 1];
    cZ.v[2] = kang_z[tid * 4 + 2]; cZ.v[3] = kang_z[tid * 4 + 3];
    uint64_t pos_lo = kang_pos[tid];
    uint64_t pos_hi = kang_pos_hi[tid];
    int is_inf = kang_inf[tid];
    int is_tame = (tid < n_tame) ? 1 : 0;

    /* Walk in Jacobian coordinates. Every NORM_INTERVAL steps, normalize
     * to affine (1 inversion) and check DP on the true affine x.
     * This amortizes the inversion cost over NORM_INTERVAL steps.
     * Between normalizations, the walk uses affine x for jump index
     * (since Z=1 at the start of each interval). */
    /* Normalization interval: every N steps, convert Jacobian -> affine.
     * This costs 1 inversion per N steps but enables walk merging.
     * N=8 is a good balance: saves 7/8 inversions vs affine walk,
     * at the cost of walk divergence within 8-step windows. */
    #define NORM_INTERVAL 8

    for (int step = 0; step < steps_per_launch; step++) {
        if (*found_flag) break;
        if (is_inf) break;

        /* Murmur3 finalizer: bijective mix for uniform jump selection.
         * Critical for walk quality when using Jacobian X (correlated low bits).
         * ~1.5x faster at 48-52b vs raw `v[0] & 63`. */
        uint64_t hx = cX.v[0];
        hx ^= hx >> 33;
        hx *= 0xff51afd7ed558ccdULL;
        hx ^= hx >> 33;
        hx *= 0xc4ceb9fe1a85ec53ULL;
        hx ^= hx >> 33;
        int ji = (int)(hx & 63);
        fe_t jx, jy;
        jx.v[0] = JUMP_X[ji][0]; jx.v[1] = JUMP_X[ji][1];
        jx.v[2] = JUMP_X[ji][2]; jx.v[3] = JUMP_X[ji][3];
        jy.v[0] = JUMP_Y[ji][0]; jy.v[1] = JUMP_Y[ji][1];
        jy.v[2] = JUMP_Y[ji][2]; jy.v[3] = JUMP_Y[ji][3];

        { uint64_t old_lo = pos_lo; pos_lo += JUMP_DIST[ji]; if (pos_lo < old_lo) pos_hi++; }

        /* Mixed Jacobian + affine addition — NO inversion needed */
        fe_t nX, nY, nZ;
        ec_madd_jacobian(&nX, &nY, &nZ, &cX, &cY, &cZ, &jx, &jy);

        /* Check for degenerate result (Z3 == 0 means point at infinity) */
        if (fe_is_zero(&nZ)) { is_inf = 1; break; }

        fe_set(&cX, &nX); fe_set(&cY, &nY); fe_set(&cZ, &nZ);

        /* Periodic normalization + DP check */
        if (((step + 1) % NORM_INTERVAL) == 0) {
            /* Normalize to affine: x = X/Z^2, y = Y/Z^3 */
            fe_t Zinv, Zinv2, Zinv3;
            fe_inv(&Zinv, &cZ);
            fe_sqr(&Zinv2, &Zinv);
            fe_mul(&Zinv3, &Zinv2, &Zinv);
            fe_mul(&cX, &cX, &Zinv2);
            fe_mul(&cY, &cY, &Zinv3);
            cZ.v[0] = 1; cZ.v[1] = 0; cZ.v[2] = 0; cZ.v[3] = 0;

            /* DP check on true affine x */
            if ((cX.v[0] & dp_mask) == 0) {
                int idx = atomicAdd(dp_count, 1);
                if (idx < dp_buf_size) {
                    dp_buf[idx].x_hash = cX.v[0];
                    dp_buf[idx].x1 = cX.v[0]; dp_buf[idx].x2 = cX.v[1];
                    dp_buf[idx].x3 = cX.v[2]; dp_buf[idx].x4 = cX.v[3];
                    dp_buf[idx].pos_lo = pos_lo;
                    dp_buf[idx].pos_hi = pos_hi;
                    dp_buf[idx].is_tame = is_tame ? 1 : 0;
                    dp_buf[idx].thread_id = (uint32_t)tid;
                }
            }
        }
    }

    /* Final normalization at end of batch */
    if (!is_inf && !fe_is_zero(&cZ)) {
        fe_t Zinv, Zinv2, Zinv3;
        fe_inv(&Zinv, &cZ);
        fe_sqr(&Zinv2, &Zinv);
        fe_mul(&Zinv3, &Zinv2, &Zinv);
        fe_mul(&cX, &cX, &Zinv2);
        fe_mul(&cY, &cY, &Zinv3);
        cZ.v[0] = 1; cZ.v[1] = 0; cZ.v[2] = 0; cZ.v[3] = 0;
    }

    /* Write back normalized affine state (Z=1) */
    kang_x[tid * 4 + 0] = cX.v[0]; kang_x[tid * 4 + 1] = cX.v[1];
    kang_x[tid * 4 + 2] = cX.v[2]; kang_x[tid * 4 + 3] = cX.v[3];
    kang_y[tid * 4 + 0] = cY.v[0]; kang_y[tid * 4 + 1] = cY.v[1];
    kang_y[tid * 4 + 2] = cY.v[2]; kang_y[tid * 4 + 3] = cY.v[3];
    kang_z[tid * 4 + 0] = cZ.v[0]; kang_z[tid * 4 + 1] = cZ.v[1];
    kang_z[tid * 4 + 2] = cZ.v[2]; kang_z[tid * 4 + 3] = cZ.v[3];
    kang_pos[tid] = pos_lo;
    kang_pos_hi[tid] = pos_hi;
    kang_inf[tid] = is_inf;
}

/* ================================================================
 * Host-side field arithmetic (same algorithms, no __device__)
 * ================================================================ */

typedef struct { uint64_t v[4]; } h_fe_t;

static const uint64_t H_FE_P[4] = {
    0xFFFFFFFEFFFFFC2FULL, 0xFFFFFFFFFFFFFFFFULL,
    0xFFFFFFFFFFFFFFFFULL, 0xFFFFFFFFFFFFFFFFULL
};

static void h_fe_set(h_fe_t *r, const h_fe_t *a) {
    r->v[0] = a->v[0]; r->v[1] = a->v[1]; r->v[2] = a->v[2]; r->v[3] = a->v[3];
}

static void h_fe_add(h_fe_t *r, const h_fe_t *a, const h_fe_t *b) {
    unsigned __int128 acc; uint64_t carry = 0;
    acc = (unsigned __int128)a->v[0] + b->v[0]; r->v[0] = (uint64_t)acc; carry = (uint64_t)(acc >> 64);
    acc = (unsigned __int128)a->v[1] + b->v[1] + carry; r->v[1] = (uint64_t)acc; carry = (uint64_t)(acc >> 64);
    acc = (unsigned __int128)a->v[2] + b->v[2] + carry; r->v[2] = (uint64_t)acc; carry = (uint64_t)(acc >> 64);
    acc = (unsigned __int128)a->v[3] + b->v[3] + carry; r->v[3] = (uint64_t)acc; carry = (uint64_t)(acc >> 64);
    uint64_t borrow = 0; uint64_t t[4]; unsigned __int128 diff;
    diff = (unsigned __int128)r->v[0] - H_FE_P[0]; t[0] = (uint64_t)diff; borrow = (diff >> 127) ? 1 : 0;
    diff = (unsigned __int128)r->v[1] - H_FE_P[1] - borrow; t[1] = (uint64_t)diff; borrow = (diff >> 127) ? 1 : 0;
    diff = (unsigned __int128)r->v[2] - H_FE_P[2] - borrow; t[2] = (uint64_t)diff; borrow = (diff >> 127) ? 1 : 0;
    diff = (unsigned __int128)r->v[3] - H_FE_P[3] - borrow; t[3] = (uint64_t)diff; borrow = (diff >> 127) ? 1 : 0;
    uint64_t mask = (carry | (borrow ^ 1)) ? 0xFFFFFFFFFFFFFFFFULL : 0;
    r->v[0] = (t[0] & mask) | (r->v[0] & ~mask);
    r->v[1] = (t[1] & mask) | (r->v[1] & ~mask);
    r->v[2] = (t[2] & mask) | (r->v[2] & ~mask);
    r->v[3] = (t[3] & mask) | (r->v[3] & ~mask);
}

static void h_fe_sub(h_fe_t *r, const h_fe_t *a, const h_fe_t *b) {
    unsigned __int128 diff; uint64_t borrow = 0;
    diff = (unsigned __int128)a->v[0] - b->v[0]; r->v[0] = (uint64_t)diff; borrow = (diff >> 127) ? 1 : 0;
    diff = (unsigned __int128)a->v[1] - b->v[1] - borrow; r->v[1] = (uint64_t)diff; borrow = (diff >> 127) ? 1 : 0;
    diff = (unsigned __int128)a->v[2] - b->v[2] - borrow; r->v[2] = (uint64_t)diff; borrow = (diff >> 127) ? 1 : 0;
    diff = (unsigned __int128)a->v[3] - b->v[3] - borrow; r->v[3] = (uint64_t)diff; borrow = (diff >> 127) ? 1 : 0;
    if (borrow) {
        uint64_t carry = 0; unsigned __int128 acc;
        acc = (unsigned __int128)r->v[0] + H_FE_P[0]; r->v[0] = (uint64_t)acc; carry = (uint64_t)(acc >> 64);
        acc = (unsigned __int128)r->v[1] + H_FE_P[1] + carry; r->v[1] = (uint64_t)acc; carry = (uint64_t)(acc >> 64);
        acc = (unsigned __int128)r->v[2] + H_FE_P[2] + carry; r->v[2] = (uint64_t)acc; carry = (uint64_t)(acc >> 64);
        acc = (unsigned __int128)r->v[3] + H_FE_P[3] + carry; r->v[3] = (uint64_t)acc;
    }
}

static void h_fe_mul(h_fe_t *r, const h_fe_t *a, const h_fe_t *b) {
    uint64_t t[8] = {0, 0, 0, 0, 0, 0, 0, 0};
    unsigned __int128 uv;
    uint64_t carry;

    for (int i = 0; i < 4; i++) {
        carry = 0;
        for (int j = 0; j < 4; j++) {
            uv = (unsigned __int128)a->v[i] * b->v[j] + t[i + j] + carry;
            t[i + j] = (uint64_t)uv;
            carry = (uint64_t)(uv >> 64);
        }
        t[i + 4] += carry;
    }

    uint64_t h[5], cc;
    uv = (unsigned __int128)t[4] * FE_PC; h[0] = (uint64_t)uv; carry = (uint64_t)(uv >> 64);
    uv = (unsigned __int128)t[5] * FE_PC + carry; h[1] = (uint64_t)uv; carry = (uint64_t)(uv >> 64);
    uv = (unsigned __int128)t[6] * FE_PC + carry; h[2] = (uint64_t)uv; carry = (uint64_t)(uv >> 64);
    uv = (unsigned __int128)t[7] * FE_PC + carry; h[3] = (uint64_t)uv; h[4] = (uint64_t)(uv >> 64);

    uint64_t a5[5];
    uv = (unsigned __int128)t[0] + h[0]; a5[0] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
    uv = (unsigned __int128)t[1] + h[1] + cc; a5[1] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
    uv = (unsigned __int128)t[2] + h[2] + cc; a5[2] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
    uv = (unsigned __int128)t[3] + h[3] + cc; a5[3] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
    a5[4] = h[4] + cc;

    if (a5[4]) {
        uv = (unsigned __int128)a5[4] * FE_PC;
        uint64_t ov_lo = (uint64_t)uv, ov_hi = (uint64_t)(uv >> 64);
        uv = (unsigned __int128)a5[0] + ov_lo; a5[0] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
        uv = (unsigned __int128)a5[1] + ov_hi + cc; a5[1] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
        if (cc) { uv = (unsigned __int128)a5[2] + cc; a5[2] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
        if (cc) { uv = (unsigned __int128)a5[3] + cc; a5[3] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
        if (cc) { uv = (unsigned __int128)a5[0] + FE_PC; a5[0] = (uint64_t)uv; cc = (uint64_t)(uv >> 64);
        if (cc) { a5[1]++; if (a5[1] == 0) { a5[2]++; if (a5[2] == 0) a5[3]++; } } } } }
    }

    r->v[0] = a5[0]; r->v[1] = a5[1]; r->v[2] = a5[2]; r->v[3] = a5[3];

    int ge_p = 0;
    if (r->v[3] > H_FE_P[3]) ge_p = 1;
    else if (r->v[3] == H_FE_P[3]) {
        if (r->v[2] > H_FE_P[2]) ge_p = 1;
        else if (r->v[2] == H_FE_P[2]) {
            if (r->v[1] > H_FE_P[1]) ge_p = 1;
            else if (r->v[1] == H_FE_P[1]) {
                if (r->v[0] >= H_FE_P[0]) ge_p = 1;
            }
        }
    }
    if (ge_p) {
        unsigned __int128 d; uint64_t bw = 0;
        d = (unsigned __int128)r->v[0] - H_FE_P[0]; r->v[0] = (uint64_t)d; bw = (d >> 127) ? 1 : 0;
        d = (unsigned __int128)r->v[1] - H_FE_P[1] - bw; r->v[1] = (uint64_t)d; bw = (d >> 127) ? 1 : 0;
        d = (unsigned __int128)r->v[2] - H_FE_P[2] - bw; r->v[2] = (uint64_t)d; bw = (d >> 127) ? 1 : 0;
        d = (unsigned __int128)r->v[3] - H_FE_P[3] - bw; r->v[3] = (uint64_t)d;
    }
}

static void h_fe_sqr(h_fe_t *r, const h_fe_t *a) { h_fe_mul(r, a, a); }

static void h_fe_inv(h_fe_t *r, const h_fe_t *a) {
    h_fe_t x2, x3, x6, x9, x11, x22, x44, x88, x176, x220, x223, t;
    h_fe_sqr(&t, a); h_fe_mul(&x2, &t, a);
    h_fe_sqr(&t, &x2); h_fe_mul(&x3, &t, a);
    h_fe_set(&t, &x3); for (int i = 0; i < 3; i++) h_fe_sqr(&t, &t); h_fe_mul(&x6, &t, &x3);
    h_fe_set(&t, &x6); for (int i = 0; i < 3; i++) h_fe_sqr(&t, &t); h_fe_mul(&x9, &t, &x3);
    h_fe_set(&t, &x9); for (int i = 0; i < 2; i++) h_fe_sqr(&t, &t); h_fe_mul(&x11, &t, &x2);
    h_fe_set(&t, &x11); for (int i = 0; i < 11; i++) h_fe_sqr(&t, &t); h_fe_mul(&x22, &t, &x11);
    h_fe_set(&t, &x22); for (int i = 0; i < 22; i++) h_fe_sqr(&t, &t); h_fe_mul(&x44, &t, &x22);
    h_fe_set(&t, &x44); for (int i = 0; i < 44; i++) h_fe_sqr(&t, &t); h_fe_mul(&x88, &t, &x44);
    h_fe_set(&t, &x88); for (int i = 0; i < 88; i++) h_fe_sqr(&t, &t); h_fe_mul(&x176, &t, &x88);
    h_fe_set(&t, &x176); for (int i = 0; i < 44; i++) h_fe_sqr(&t, &t); h_fe_mul(&x220, &t, &x44);
    h_fe_set(&t, &x220); for (int i = 0; i < 3; i++) h_fe_sqr(&t, &t); h_fe_mul(&x223, &t, &x3);
    h_fe_set(&t, &x223);
    h_fe_sqr(&t, &t);                                                             /* bit 32: 0 */
    for (int i = 0; i < 22; i++) h_fe_sqr(&t, &t); h_fe_mul(&t, &t, &x22);       /* bits 31..10 */
    for (int i = 0; i < 4; i++) h_fe_sqr(&t, &t);                                 /* bits 9..6 */
    h_fe_sqr(&t, &t); h_fe_mul(&t, &t, a);                                        /* bit 5 */
    h_fe_sqr(&t, &t);                                                             /* bit 4 */
    h_fe_sqr(&t, &t); h_fe_mul(&t, &t, a);                                        /* bit 3 */
    h_fe_sqr(&t, &t); h_fe_mul(&t, &t, a);                                        /* bit 2 */
    h_fe_sqr(&t, &t);                                                             /* bit 1 */
    h_fe_sqr(&t, &t); h_fe_mul(&t, &t, a);                                        /* bit 0 */
    h_fe_set(r, &t);
}

/* Host EC point add */
static void h_ec_add(h_fe_t *rx, h_fe_t *ry, int *rinf,
                      const h_fe_t *px, const h_fe_t *py, int pinf,
                      const h_fe_t *qx, const h_fe_t *qy, int qinf) {
    if (pinf) { h_fe_set(rx, qx); h_fe_set(ry, qy); *rinf = qinf; return; }
    if (qinf) { h_fe_set(rx, px); h_fe_set(ry, py); *rinf = pinf; return; }
    h_fe_t dx, dy, inv, lam, lam2, xr, yr;
    h_fe_sub(&dx, qx, px);
    int dxz = (dx.v[0] | dx.v[1] | dx.v[2] | dx.v[3]) == 0;
    if (dxz) {
        h_fe_sub(&dy, qy, py);
        int dyz = (dy.v[0] | dy.v[1] | dy.v[2] | dy.v[3]) == 0;
        if (dyz) {
            int yz = (py->v[0] | py->v[1] | py->v[2] | py->v[3]) == 0;
            if (yz) { *rinf = 1; return; }
            h_fe_t x2, num, den;
            h_fe_sqr(&x2, px);
            h_fe_add(&num, &x2, &x2); h_fe_add(&num, &num, &x2);
            h_fe_add(&den, py, py);
            h_fe_inv(&inv, &den);
            h_fe_mul(&lam, &num, &inv);
        } else { *rinf = 1; return; }
    } else {
        h_fe_sub(&dy, qy, py);
        h_fe_inv(&inv, &dx);
        h_fe_mul(&lam, &dy, &inv);
    }
    h_fe_sqr(&lam2, &lam);
    h_fe_sub(&xr, &lam2, px); h_fe_sub(&xr, &xr, qx);
    h_fe_sub(&yr, px, &xr);
    h_fe_mul(&yr, &lam, &yr);
    h_fe_sub(&yr, &yr, py);
    h_fe_set(rx, &xr); h_fe_set(ry, &yr); *rinf = 0;
}

/* Host scalar mult — 128-bit scalar for 68b+ ECDLP searches */
static void h_ec_smul(h_fe_t *rx, h_fe_t *ry, int *rinf,
                       unsigned __int128 k, const h_fe_t *gx, const h_fe_t *gy) {
    h_fe_t ax = {}, ay = {}; int ainf = 1;
    h_fe_t bx, by; int binf = 0;
    h_fe_set(&bx, gx); h_fe_set(&by, gy);
    while (k > 0) {
        if (k & 1) {
            h_fe_t nx, ny; int ni;
            h_ec_add(&nx, &ny, &ni, &ax, &ay, ainf, &bx, &by, binf);
            h_fe_set(&ax, &nx); h_fe_set(&ay, &ny); ainf = ni;
        }
        h_fe_t nx, ny; int ni;
        h_ec_add(&nx, &ny, &ni, &bx, &by, binf, &bx, &by, binf);
        h_fe_set(&bx, &nx); h_fe_set(&by, &ny); binf = ni;
        k >>= 1;
    }
    h_fe_set(rx, &ax); h_fe_set(ry, &ay); *rinf = ainf;
}

static void h_fe_from_hex(h_fe_t *r, const char *hex) {
    r->v[0] = 0; r->v[1] = 0; r->v[2] = 0; r->v[3] = 0;
    int len = (int)strlen(hex);
    for (int limb = 0; limb < 4; limb++) {
        uint64_t val = 0;
        for (int j = 0; j < 16; j++) {
            int pos = len - 1 - limb * 16 - j;
            if (pos < 0) break;
            char c = hex[pos]; uint64_t d;
            if (c >= '0' && c <= '9') d = c - '0';
            else if (c >= 'a' && c <= 'f') d = c - 'a' + 10;
            else if (c >= 'A' && c <= 'F') d = c - 'A' + 10;
            else d = 0;
            val |= (d << (j * 4));
        }
        r->v[limb] = val;
    }
}

/* ================================================================
 * Pythagorean hypotenuse jump table
 * ================================================================ */

/* Lévy-flight-inspired exponential spread: 1 to 10M (10^7 spread).
 * Wide spread compensates for weak hash (x & 63) jump selection,
 * ensuring correlated indices still produce very different walks.
 * Benchmarked 33-37% faster than original 13.6K-spread table. */
static const uint64_t PYTH_HYPS[64] = {
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    12, 16, 21, 27, 35, 46, 59, 77, 99, 129,
    166, 215, 278, 359, 464, 599, 774, 1000, 1291, 1668,
    2154, 2782, 3593, 4641, 5994, 7742, 9999, 12915, 16681, 21544,
    27825, 35938, 46415, 59948, 77426, 100000, 129154, 166810, 215443, 278255,
    359381, 464158, 599484, 774263, 1000000, 1291549, 1668100, 2154434, 2782559, 3593813,
    4641588, 5994842, 7742636, 10000000
};

/* ================================================================
 * CPU-side DP collision table
 * ================================================================ */

#define CPU_DP_TABLE_SIZE 131072

typedef struct cpu_dp_entry {
    uint64_t x[4];
    uint64_t pos_lo;
    uint64_t pos_hi;
    int is_tame;
    struct cpu_dp_entry *next;
} cpu_dp_entry_t;

typedef struct {
    cpu_dp_entry_t *buckets[CPU_DP_TABLE_SIZE];
} cpu_dp_table_t;

static cpu_dp_table_t *cpu_dp_create(void) {
    return (cpu_dp_table_t *)calloc(1, sizeof(cpu_dp_table_t));
}

static void cpu_dp_destroy(cpu_dp_table_t *t) {
    for (int i = 0; i < CPU_DP_TABLE_SIZE; i++) {
        cpu_dp_entry_t *e = t->buckets[i];
        while (e) { cpu_dp_entry_t *n = e->next; free(e); e = n; }
    }
    free(t);
}

static void cpu_dp_insert(cpu_dp_table_t *t, const uint64_t x[4], uint64_t pos_lo, uint64_t pos_hi, int is_tame) {
    uint64_t h = x[0] % CPU_DP_TABLE_SIZE;
    cpu_dp_entry_t *e = (cpu_dp_entry_t *)malloc(sizeof(cpu_dp_entry_t));
    e->x[0] = x[0]; e->x[1] = x[1]; e->x[2] = x[2]; e->x[3] = x[3];
    e->pos_lo = pos_lo; e->pos_hi = pos_hi; e->is_tame = is_tame;
    e->next = t->buckets[h]; t->buckets[h] = e;
}

static cpu_dp_entry_t *cpu_dp_find(cpu_dp_table_t *t, const uint64_t x[4], int is_tame) {
    uint64_t h = x[0] % CPU_DP_TABLE_SIZE;
    cpu_dp_entry_t *e = t->buckets[h];
    while (e) {
        if (e->is_tame != is_tame &&
            e->x[0] == x[0] && e->x[1] == x[1] && e->x[2] == x[2] && e->x[3] == x[3])
            return e;
        e = e->next;
    }
    return NULL;
}

/* ================================================================
 * Main exported function
 * ================================================================ */

extern "C"
int ec_kang_gpu_solve(const char *Gx_hex, const char *Gy_hex,
                      const char *Px_hex, const char *Py_hex,
                      const char *bound_hex,
                      char *result, size_t result_size) {
    h_fe_t Gx, Gy, Px, Py;
    h_fe_from_hex(&Gx, Gx_hex);
    h_fe_from_hex(&Gy, Gy_hex);
    h_fe_from_hex(&Px, Px_hex);
    h_fe_from_hex(&Py, Py_hex);

    h_fe_t bound_fe;
    h_fe_from_hex(&bound_fe, bound_hex);
    unsigned __int128 bound_val = (unsigned __int128)bound_fe.v[1] << 64 | bound_fe.v[0];
    if (bound_fe.v[2] || bound_fe.v[3])
        bound_val = ((unsigned __int128)1 << 127) - 1;

    unsigned __int128 half = bound_val >> 1;

    /* Newton's method sqrt — works for 128-bit half */
    uint64_t sqrt_half = 1;
    {
        unsigned __int128 hv = half;
        unsigned __int128 x = 1;
        /* Initial guess: 2^(bits/2) */
        int hbits = 0;
        { unsigned __int128 t = hv; while (t > 0) { hbits++; t >>= 1; } }
        if (hbits > 1) x = (unsigned __int128)1 << (hbits / 2);
        if (x == 0) x = 1;
        for (int i = 0; i < 200; i++) {
            unsigned __int128 nx = (x + hv / x) / 2;
            if (nx >= x) break;
            x = nx;
        }
        /* sqrt_half fits in uint64 since half <= 2^127, sqrt <= 2^63.5 */
        sqrt_half = (uint64_t)x;
        if (sqrt_half == 0) sqrt_half = 1;
    }

    /* Jump scaling */
    uint64_t mean_target = sqrt_half / 4;
    if (mean_target < 10) mean_target = 10;
    uint64_t raw_mean = 0;
    for (int i = 0; i < 64; i++) raw_mean += PYTH_HYPS[i];
    raw_mean /= 64;
    uint64_t scale = mean_target / raw_mean;
    if (scale < 1) scale = 1;

    uint64_t jumps_h[64];
    for (int i = 0; i < 64; i++) jumps_h[i] = PYTH_HYPS[i] * scale;
    if (scale > 1) jumps_h[0] = 1;

    /* Precompute jump points */
    uint64_t jx_host[64][4], jy_host[64][4];
    for (int i = 0; i < 64; i++) {
        h_fe_t jpx, jpy; int jinf;
        h_ec_smul(&jpx, &jpy, &jinf, jumps_h[i], &Gx, &Gy);
        if (jinf) { memset(jx_host[i], 0, 32); memset(jy_host[i], 0, 32); }
        else { memcpy(jx_host[i], jpx.v, 32); memcpy(jy_host[i], jpy.v, 32); }
    }

    cudaMemcpyToSymbol(JUMP_X, jx_host, 64 * 4 * sizeof(uint64_t));
    cudaMemcpyToSymbol(JUMP_Y, jy_host, 64 * 4 * sizeof(uint64_t));
    cudaMemcpyToSymbol(JUMP_DIST, jumps_h, 64 * sizeof(uint64_t));

    /* DP parameters */
    int bound_bits = 0;
    { unsigned __int128 t = bound_val; while (t > 0) { bound_bits++; t >>= 1; } }
    /* DP density: smaller D = faster collision detection after merge, but more
     * CPU-side hash table work. Old formula (bits/4) was too sparse.
     * New: (bits-8)/4 — keeps post-merge walk < 10% of total expected walk. */
    int D = (bound_bits - 8) / 4;
    if (D < 6) D = 6;
    if (D > 20) D = 20;
    const char *dp_env = getenv("GPU_DP_BITS");
    if (dp_env) D = atoi(dp_env);
    uint64_t dp_mask = (1ULL << D) - 1;

    /* Kangaroo count — align to GPU SM count for full utilization.
     * 1 block/SM for small problems, 2 blocks/SM for 52b+. */
    int sm_count = 0;
    cudaDeviceGetAttribute(&sm_count, cudaDevAttrMultiProcessorCount, 0);
    if (sm_count <= 0) sm_count = 20; /* fallback for RTX 4050 */
    int threads_pb = 256;
    int num_kangaroos;
    if (bound_bits <= 24) num_kangaroos = sm_count * threads_pb / 4;
    else if (bound_bits <= 32) num_kangaroos = sm_count * threads_pb / 2;
    else num_kangaroos = sm_count * threads_pb;     /* 1 block/SM */
    /* Allow override via env var for tuning */
    const char *nk_env = getenv("GPU_NK");
    if (nk_env) num_kangaroos = atoi(nk_env);
    int n_tame = num_kangaroos / 2;

    /* Host arrays — Jacobian coordinates (X, Y, Z). Z=1 initially (affine). */
    uint64_t *h_kx = (uint64_t *)calloc(num_kangaroos * 4, sizeof(uint64_t));
    uint64_t *h_ky = (uint64_t *)calloc(num_kangaroos * 4, sizeof(uint64_t));
    uint64_t *h_kz = (uint64_t *)calloc(num_kangaroos * 4, sizeof(uint64_t));
    uint64_t *h_kpos = (uint64_t *)calloc(num_kangaroos, sizeof(uint64_t));
    uint64_t *h_kpos_hi = (uint64_t *)calloc(num_kangaroos, sizeof(uint64_t));
    int *h_kinf = (int *)calloc(num_kangaroos, sizeof(int));

    /* Tame kangaroos: evenly spaced, initialized incrementally.
     * T_0 = delta*G, T_i = T_{i-1} + delta_G where delta = half/(n_tame+1) */
    {
        unsigned __int128 delta = half / (unsigned __int128)(n_tame + 1);
        if (delta < 1) delta = 1;
        h_fe_t dGx, dGy; int dGinf;
        h_ec_smul(&dGx, &dGy, &dGinf, delta, &Gx, &Gy);

        h_fe_t cx, cy; int cinf;
        h_fe_set(&cx, &dGx); h_fe_set(&cy, &dGy); cinf = dGinf;
        unsigned __int128 tpos = delta;

        for (int i = 0; i < n_tame; i++) {
            if (cinf) { h_kinf[i] = 1; }
            else {
                memcpy(&h_kx[i * 4], cx.v, 32);
                memcpy(&h_ky[i * 4], cy.v, 32);
                h_kz[i * 4 + 0] = 1; h_kz[i * 4 + 1] = 0;
                h_kz[i * 4 + 2] = 0; h_kz[i * 4 + 3] = 0;
            }
            h_kpos[i] = (uint64_t)tpos;
            h_kpos_hi[i] = (uint64_t)(tpos >> 64);
            /* Advance: next = current + delta_G */
            if (i < n_tame - 1) {
                h_fe_t nx, ny; int ninf;
                h_ec_add(&nx, &ny, &ninf, &cx, &cy, cinf, &dGx, &dGy, dGinf);
                h_fe_set(&cx, &nx); h_fe_set(&cy, &ny); cinf = ninf;
                tpos += delta;
            }
        }
    }

    /* Wild kangaroos: P + i*G, initialized incrementally */
    {
        h_fe_t cx, cy; int cinf;
        h_fe_set(&cx, &Px); h_fe_set(&cy, &Py); cinf = 0;

        for (int i = 0; i < num_kangaroos - n_tame; i++) {
            int idx = n_tame + i;
            if (cinf) { h_kinf[idx] = 1; }
            else {
                memcpy(&h_kx[idx * 4], cx.v, 32);
                memcpy(&h_ky[idx * 4], cy.v, 32);
                h_kz[idx * 4 + 0] = 1; h_kz[idx * 4 + 1] = 0;
                h_kz[idx * 4 + 2] = 0; h_kz[idx * 4 + 3] = 0;
            }
            h_kpos[idx] = (uint64_t)i;
            h_kpos_hi[idx] = 0;
            /* Advance: next = current + G */
            if (i < num_kangaroos - n_tame - 1) {
                h_fe_t nx, ny; int ninf;
                h_ec_add(&nx, &ny, &ninf, &cx, &cy, cinf, &Gx, &Gy, 0);
                h_fe_set(&cx, &nx); h_fe_set(&cy, &ny); cinf = ninf;
            }
        }
    }

    /* Device memory — now includes Z coordinate */
    uint64_t *d_kx, *d_ky, *d_kz, *d_kpos, *d_kpos_hi;
    int *d_kinf, *d_found;
    dp_entry_t *d_dp_buf;
    int *d_dp_count;
    int dp_buf_size = 65536;

    cudaMalloc(&d_kx, num_kangaroos * 4 * sizeof(uint64_t));
    cudaMalloc(&d_ky, num_kangaroos * 4 * sizeof(uint64_t));
    cudaMalloc(&d_kz, num_kangaroos * 4 * sizeof(uint64_t));
    cudaMalloc(&d_kpos, num_kangaroos * sizeof(uint64_t));
    cudaMalloc(&d_kpos_hi, num_kangaroos * sizeof(uint64_t));
    cudaMalloc(&d_kinf, num_kangaroos * sizeof(int));
    cudaMalloc(&d_found, sizeof(int));
    cudaMalloc(&d_dp_buf, dp_buf_size * sizeof(dp_entry_t));
    cudaMalloc(&d_dp_count, sizeof(int));

    cudaMemcpy(d_kx, h_kx, num_kangaroos * 4 * sizeof(uint64_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_ky, h_ky, num_kangaroos * 4 * sizeof(uint64_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_kz, h_kz, num_kangaroos * 4 * sizeof(uint64_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_kpos, h_kpos, num_kangaroos * sizeof(uint64_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_kpos_hi, h_kpos_hi, num_kangaroos * sizeof(uint64_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_kinf, h_kinf, num_kangaroos * sizeof(int), cudaMemcpyHostToDevice);
    int zero = 0;
    cudaMemcpy(d_found, &zero, sizeof(int), cudaMemcpyHostToDevice);
    cudaMemcpy(d_dp_count, &zero, sizeof(int), cudaMemcpyHostToDevice);

    int threads_per_block = threads_pb;
    int num_blocks = (num_kangaroos + threads_per_block - 1) / threads_per_block;

    cpu_dp_table_t *cpu_dpt = cpu_dp_create();

    /* Adaptive steps per launch: more steps for larger problems reduces
     * kernel launch overhead. Scale with sqrt(bound). */
    g_steps_per_launch = 2048;
    if (bound_bits >= 48) g_steps_per_launch = 4096;
    if (bound_bits >= 56) g_steps_per_launch = 8192;
    const char *spl_env = getenv("GPU_SPL");
    if (spl_env) g_steps_per_launch = atoi(spl_env);

    uint64_t max_total_steps = sqrt_half * 32 + 20000;
    if (max_total_steps > 2000000000ULL) max_total_steps = 2000000000ULL;
    uint64_t max_launches = max_total_steps / g_steps_per_launch + 1;

    int found = 0;
    dp_entry_t *h_dp_buf = (dp_entry_t *)malloc(dp_buf_size * sizeof(dp_entry_t));

    for (uint64_t launch = 0; launch < max_launches && !found; launch++) {
        cudaMemcpy(d_dp_count, &zero, sizeof(int), cudaMemcpyHostToDevice);

        kangaroo_walk_kernel<<<num_blocks, threads_per_block>>>(
            d_kx, d_ky, d_kz, d_kpos, d_kpos_hi, d_kinf,
            num_kangaroos, n_tame, dp_mask,
            d_dp_buf, d_dp_count, dp_buf_size,
            d_found, g_steps_per_launch);
        cudaDeviceSynchronize();

        int dp_count = 0;
        cudaMemcpy(&dp_count, d_dp_count, sizeof(int), cudaMemcpyDeviceToHost);
        if (dp_count > dp_buf_size) dp_count = dp_buf_size;

        /* Debug: uncomment to monitor DP rate
        if (launch < 5 || (launch % 500 == 0))
            fprintf(stderr, "  L%llu: dp=%d D=%d\n",
                    (unsigned long long)launch, dp_count, D);
        */

        if (dp_count > 0) {
            cudaMemcpy(h_dp_buf, d_dp_buf, dp_count * sizeof(dp_entry_t), cudaMemcpyDeviceToHost);

            for (int i = 0; i < dp_count && !found; i++) {
                dp_entry_t *e = &h_dp_buf[i];
                uint64_t ex[4] = { e->x1, e->x2, e->x3, e->x4 };
                int is_tame = e->is_tame ? 1 : 0;

                cpu_dp_entry_t *match = cpu_dp_find(cpu_dpt, ex, is_tame);
                if (match) {
                    /* Compute tame_pos - wild_pos using 128-bit unsigned arithmetic. */
                    unsigned __int128 tame_pos = ((unsigned __int128)(is_tame ? e->pos_hi : match->pos_hi) << 64)
                                                | (is_tame ? e->pos_lo : match->pos_lo);
                    unsigned __int128 wild_pos = ((unsigned __int128)(is_tame ? match->pos_hi : e->pos_hi) << 64)
                                                | (is_tame ? match->pos_lo : e->pos_lo);

                    unsigned __int128 candidates[4];
                    int ncand = 0;
                    /* k = tame_pos - wild_pos (unsigned, may wrap) */
                    unsigned __int128 d1 = tame_pos - wild_pos;
                    if (d1 > 0 && d1 <= bound_val) candidates[ncand++] = d1;
                    /* k = wild_pos - tame_pos (if wild walked past tame) */
                    unsigned __int128 d2 = wild_pos - tame_pos;
                    if (d2 > 0 && d2 <= bound_val) candidates[ncand++] = d2;

                    for (int ci = 0; ci < ncand && !found; ci++) {
                        unsigned __int128 k_cand = candidates[ci];
                        if (k_cand == 0 || k_cand > bound_val) continue;
                        h_fe_t vx, vy; int vinf;
                        h_ec_smul(&vx, &vy, &vinf, k_cand, &Gx, &Gy);
                        if (!vinf && vx.v[0] == Px.v[0] && vx.v[1] == Px.v[1] &&
                            vx.v[2] == Px.v[2] && vx.v[3] == Px.v[3] &&
                            vy.v[0] == Py.v[0] && vy.v[1] == Py.v[1] &&
                            vy.v[2] == Py.v[2] && vy.v[3] == Py.v[3]) {
                            uint64_t k_hi = (uint64_t)(k_cand >> 64);
                            uint64_t k_lo = (uint64_t)k_cand;
                            if (k_hi)
                                snprintf(result, result_size, "%llx%016llx",
                                         (unsigned long long)k_hi, (unsigned long long)k_lo);
                            else
                                snprintf(result, result_size, "%llx", (unsigned long long)k_lo);
                            found = 1;
                        }
                    }
                }
                if (!found) cpu_dp_insert(cpu_dpt, ex, e->pos_lo, e->pos_hi, is_tame);
            }
        }
    }

    cpu_dp_destroy(cpu_dpt);
    free(h_dp_buf);
    free(h_kx); free(h_ky); free(h_kz); free(h_kpos); free(h_kpos_hi); free(h_kinf);
    cudaFree(d_kx); cudaFree(d_ky); cudaFree(d_kz); cudaFree(d_kpos); cudaFree(d_kpos_hi);
    cudaFree(d_kinf); cudaFree(d_found);
    cudaFree(d_dp_buf); cudaFree(d_dp_count);

    return found;
}
