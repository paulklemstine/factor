/*
 * ec_kangaroo_gpu.cu — GPU-accelerated Pollard kangaroo for secp256k1 ECDLP.
 *
 * Each CUDA thread runs one independent kangaroo walk (tame or wild).
 * Field arithmetic: 256-bit using 4x uint64_t limbs with secp256k1 fast reduction.
 * Inversion: Fermat's little theorem a^(p-2) mod p (~255 squarings + ~15 muls).
 * Jump table: 64 Pythagorean hypotenuse jumps in __constant__ memory.
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
    uint64_t pos;
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

#define STEPS_PER_LAUNCH 2048

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

__device__ __forceinline__ void fe_sqr(fe_t *r, const fe_t *a) { fe_mul(r, a, a); }

/*
 * Fermat inversion: r = a^(p-2) mod p
 * p-2 = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2D
 *
 * Bits 255..33: all 1 (223 ones) -> x223
 * Bit 32: 0
 * Bits 31..10: all 1 (22 ones) -> x22
 * Bits 9..6: 0000
 * Bit 5: 1, Bit 4: 0, Bit 3: 1, Bit 2: 1, Bit 1: 0, Bit 0: 1
 */
__device__ void fe_inv(fe_t *r, const fe_t *a) {
    fe_t x2, x3, x6, x9, x11, x22, x44, x88, x176, x220, x223, t;

    fe_sqr(&t, a); fe_mul(&x2, &t, a);                                          /* x2 = a^3 = a^(2^2-1) */
    fe_sqr(&t, &x2); fe_mul(&x3, &t, a);                                        /* x3 = a^7 = a^(2^3-1) */
    fe_set(&t, &x3); for (int i = 0; i < 3; i++) fe_sqr(&t, &t); fe_mul(&x6, &t, &x3);
    fe_set(&t, &x6); for (int i = 0; i < 3; i++) fe_sqr(&t, &t); fe_mul(&x9, &t, &x3);
    fe_set(&t, &x9); for (int i = 0; i < 2; i++) fe_sqr(&t, &t); fe_mul(&x11, &t, &x2);
    fe_set(&t, &x11); for (int i = 0; i < 11; i++) fe_sqr(&t, &t); fe_mul(&x22, &t, &x11);
    fe_set(&t, &x22); for (int i = 0; i < 22; i++) fe_sqr(&t, &t); fe_mul(&x44, &t, &x22);
    fe_set(&t, &x44); for (int i = 0; i < 44; i++) fe_sqr(&t, &t); fe_mul(&x88, &t, &x44);
    fe_set(&t, &x88); for (int i = 0; i < 88; i++) fe_sqr(&t, &t); fe_mul(&x176, &t, &x88);
    fe_set(&t, &x176); for (int i = 0; i < 44; i++) fe_sqr(&t, &t); fe_mul(&x220, &t, &x44);
    fe_set(&t, &x220); for (int i = 0; i < 3; i++) fe_sqr(&t, &t); fe_mul(&x223, &t, &x3);

    fe_set(&t, &x223);
    fe_sqr(&t, &t);                                                               /* bit 32: 0 */
    for (int i = 0; i < 22; i++) fe_sqr(&t, &t); fe_mul(&t, &t, &x22);           /* bits 31..10 */
    for (int i = 0; i < 4; i++) fe_sqr(&t, &t);                                   /* bits 9..6: 0000 */
    fe_sqr(&t, &t); fe_mul(&t, &t, a);                                            /* bit 5: 1 */
    fe_sqr(&t, &t);                                                               /* bit 4: 0 */
    fe_sqr(&t, &t); fe_mul(&t, &t, a);                                            /* bit 3: 1 */
    fe_sqr(&t, &t); fe_mul(&t, &t, a);                                            /* bit 2: 1 */
    fe_sqr(&t, &t);                                                               /* bit 1: 0 */
    fe_sqr(&t, &t); fe_mul(&t, &t, a);                                            /* bit 0: 1 */

    fe_set(r, &t);
}

/* ================================================================
 * EC point addition (affine, for device)
 * ================================================================ */

__device__ void ec_add_affine(fe_t *rx, fe_t *ry, int *rinf,
                               const fe_t *px, const fe_t *py,
                               const fe_t *qx, const fe_t *qy) {
    fe_t dx, dy, inv, lam, lam2, xr, yr;
    fe_sub(&dx, qx, px);

    if (fe_is_zero(&dx)) {
        fe_sub(&dy, qy, py);
        if (fe_is_zero(&dy)) {
            if (fe_is_zero(py)) { *rinf = 1; return; }
            fe_t x2, num, den;
            fe_sqr(&x2, px);
            fe_add(&num, &x2, &x2); fe_add(&num, &num, &x2); /* 3*x^2 */
            fe_add(&den, py, py);                              /* 2*y */
            fe_inv(&inv, &den);
            fe_mul(&lam, &num, &inv);
        } else { *rinf = 1; return; }
    } else {
        fe_sub(&dy, qy, py);
        fe_inv(&inv, &dx);
        fe_mul(&lam, &dy, &inv);
    }

    fe_sqr(&lam2, &lam);
    fe_sub(&xr, &lam2, px); fe_sub(&xr, &xr, qx);
    fe_sub(&yr, px, &xr);
    fe_mul(&yr, &lam, &yr);
    fe_sub(&yr, &yr, py);
    fe_set(rx, &xr); fe_set(ry, &yr); *rinf = 0;
}

/* ================================================================
 * Main kangaroo kernel
 * ================================================================ */

__global__ void kangaroo_walk_kernel(
    uint64_t *kang_x, uint64_t *kang_y, uint64_t *kang_pos, int *kang_inf,
    int num_kangaroos, int n_tame, uint64_t dp_mask,
    dp_entry_t *dp_buf, int *dp_count, int dp_buf_size,
    int *found_flag, int steps_per_launch)
{
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= num_kangaroos) return;
    if (*found_flag) return;

    fe_t cx, cy;
    cx.v[0] = kang_x[tid * 4 + 0]; cx.v[1] = kang_x[tid * 4 + 1];
    cx.v[2] = kang_x[tid * 4 + 2]; cx.v[3] = kang_x[tid * 4 + 3];
    cy.v[0] = kang_y[tid * 4 + 0]; cy.v[1] = kang_y[tid * 4 + 1];
    cy.v[2] = kang_y[tid * 4 + 2]; cy.v[3] = kang_y[tid * 4 + 3];
    uint64_t pos = kang_pos[tid];
    int is_inf = kang_inf[tid];
    int is_tame = (tid < n_tame) ? 1 : 0;

    for (int step = 0; step < steps_per_launch; step++) {
        if (*found_flag) break;
        if (is_inf) break;

        int ji = (int)(cx.v[0] & 63);
        fe_t jx, jy;
        jx.v[0] = JUMP_X[ji][0]; jx.v[1] = JUMP_X[ji][1];
        jx.v[2] = JUMP_X[ji][2]; jx.v[3] = JUMP_X[ji][3];
        jy.v[0] = JUMP_Y[ji][0]; jy.v[1] = JUMP_Y[ji][1];
        jy.v[2] = JUMP_Y[ji][2]; jy.v[3] = JUMP_Y[ji][3];

        pos += JUMP_DIST[ji];

        fe_t nx, ny; int new_inf = 0;
        ec_add_affine(&nx, &ny, &new_inf, &cx, &cy, &jx, &jy);
        if (new_inf) { is_inf = 1; break; }
        fe_set(&cx, &nx); fe_set(&cy, &ny);

        if ((cx.v[0] & dp_mask) == 0) {
            int idx = atomicAdd(dp_count, 1);
            if (idx < dp_buf_size) {
                dp_buf[idx].x_hash = cx.v[0];
                dp_buf[idx].x1 = cx.v[0]; dp_buf[idx].x2 = cx.v[1];
                dp_buf[idx].x3 = cx.v[2]; dp_buf[idx].x4 = cx.v[3];
                dp_buf[idx].pos = pos;
                dp_buf[idx].is_tame = is_tame ? 1 : 0;
                dp_buf[idx].thread_id = (uint32_t)tid;
            }
        }
    }

    kang_x[tid * 4 + 0] = cx.v[0]; kang_x[tid * 4 + 1] = cx.v[1];
    kang_x[tid * 4 + 2] = cx.v[2]; kang_x[tid * 4 + 3] = cx.v[3];
    kang_y[tid * 4 + 0] = cy.v[0]; kang_y[tid * 4 + 1] = cy.v[1];
    kang_y[tid * 4 + 2] = cy.v[2]; kang_y[tid * 4 + 3] = cy.v[3];
    kang_pos[tid] = pos;
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

/* Host scalar mult */
static void h_ec_smul(h_fe_t *rx, h_fe_t *ry, int *rinf,
                       uint64_t k, const h_fe_t *gx, const h_fe_t *gy) {
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

static const uint64_t PYTH_HYPS[64] = {
    5, 109, 233, 373, 509, 685, 853, 1025, 1189, 1429,
    1649, 1825, 2045, 2273, 2533, 2749, 2953, 3233, 3485, 3697,
    4013, 4285, 4625, 4889, 5197, 5545, 5857, 6121, 6485, 6865,
    7309, 7625, 8005, 8465, 8845, 9529, 10069, 10537, 11065, 11597,
    12193, 12721, 13325, 13997, 14813, 15481, 16237, 16865, 17833, 18797,
    19501, 20813, 22229, 24217, 25805, 27449, 30005, 32657, 34285, 37013,
    42025, 47413, 53057, 67901
};

/* ================================================================
 * CPU-side DP collision table
 * ================================================================ */

#define CPU_DP_TABLE_SIZE 131072

typedef struct cpu_dp_entry {
    uint64_t x[4];
    uint64_t pos;
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

static void cpu_dp_insert(cpu_dp_table_t *t, const uint64_t x[4], uint64_t pos, int is_tame) {
    uint64_t h = x[0] % CPU_DP_TABLE_SIZE;
    cpu_dp_entry_t *e = (cpu_dp_entry_t *)malloc(sizeof(cpu_dp_entry_t));
    e->x[0] = x[0]; e->x[1] = x[1]; e->x[2] = x[2]; e->x[3] = x[3];
    e->pos = pos; e->is_tame = is_tame;
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
    uint64_t bound_val = bound_fe.v[0];
    if (bound_fe.v[1]) bound_val = 0xFFFFFFFFFFFFFFFFULL;

    uint64_t half = bound_val >> 1;

    /* Newton's method sqrt */
    uint64_t sqrt_half = 1;
    {
        uint64_t x = 1ULL << 32;
        if (half < x) x = half;
        if (x == 0) x = 1;
        for (int i = 0; i < 64; i++) {
            uint64_t nx = (x + half / x) / 2;
            if (nx >= x) break;
            x = nx;
        }
        sqrt_half = x;
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
    { uint64_t t = bound_val; while (t > 0) { bound_bits++; t >>= 1; } }
    int D = bound_bits / 4;
    if (D < 1) D = 1;
    if (D > 20) D = 20;
    uint64_t dp_mask = (1ULL << D) - 1;

    /* Kangaroo count */
    int num_kangaroos = 4096;
    if (bound_bits <= 24) num_kangaroos = 512;
    else if (bound_bits <= 32) num_kangaroos = 1024;
    else if (bound_bits <= 40) num_kangaroos = 2048;
    int n_tame = num_kangaroos / 2;

    /* Host arrays */
    uint64_t *h_kx = (uint64_t *)calloc(num_kangaroos * 4, sizeof(uint64_t));
    uint64_t *h_ky = (uint64_t *)calloc(num_kangaroos * 4, sizeof(uint64_t));
    uint64_t *h_kpos = (uint64_t *)calloc(num_kangaroos, sizeof(uint64_t));
    int *h_kinf = (int *)calloc(num_kangaroos, sizeof(int));

    /* Tame kangaroos: evenly spaced */
    for (int i = 0; i < n_tame; i++) {
        uint64_t tpos = half * (uint64_t)(i + 1) / (uint64_t)(n_tame + 1);
        h_fe_t tx, ty; int tinf;
        h_ec_smul(&tx, &ty, &tinf, tpos, &Gx, &Gy);
        if (tinf) { h_kinf[i] = 1; }
        else { memcpy(&h_kx[i * 4], tx.v, 32); memcpy(&h_ky[i * 4], ty.v, 32); }
        h_kpos[i] = tpos;
    }

    /* Wild kangaroos: P + offset*G */
    for (int i = 0; i < num_kangaroos - n_tame; i++) {
        int idx = n_tame + i;
        h_fe_t wx, wy; int winf;
        if (i == 0) {
            h_fe_set(&wx, &Px); h_fe_set(&wy, &Py); winf = 0;
        } else {
            h_fe_t ox, oy; int oinf;
            h_ec_smul(&ox, &oy, &oinf, (uint64_t)i, &Gx, &Gy);
            h_ec_add(&wx, &wy, &winf, &Px, &Py, 0, &ox, &oy, oinf);
        }
        if (winf) { h_kinf[idx] = 1; }
        else { memcpy(&h_kx[idx * 4], wx.v, 32); memcpy(&h_ky[idx * 4], wy.v, 32); }
        h_kpos[idx] = (uint64_t)i;
    }

    /* Device memory */
    uint64_t *d_kx, *d_ky, *d_kpos;
    int *d_kinf, *d_found;
    dp_entry_t *d_dp_buf;
    int *d_dp_count;
    int dp_buf_size = 65536;

    cudaMalloc(&d_kx, num_kangaroos * 4 * sizeof(uint64_t));
    cudaMalloc(&d_ky, num_kangaroos * 4 * sizeof(uint64_t));
    cudaMalloc(&d_kpos, num_kangaroos * sizeof(uint64_t));
    cudaMalloc(&d_kinf, num_kangaroos * sizeof(int));
    cudaMalloc(&d_found, sizeof(int));
    cudaMalloc(&d_dp_buf, dp_buf_size * sizeof(dp_entry_t));
    cudaMalloc(&d_dp_count, sizeof(int));

    cudaMemcpy(d_kx, h_kx, num_kangaroos * 4 * sizeof(uint64_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_ky, h_ky, num_kangaroos * 4 * sizeof(uint64_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_kpos, h_kpos, num_kangaroos * sizeof(uint64_t), cudaMemcpyHostToDevice);
    cudaMemcpy(d_kinf, h_kinf, num_kangaroos * sizeof(int), cudaMemcpyHostToDevice);
    int zero = 0;
    cudaMemcpy(d_found, &zero, sizeof(int), cudaMemcpyHostToDevice);
    cudaMemcpy(d_dp_count, &zero, sizeof(int), cudaMemcpyHostToDevice);

    int threads_per_block = 256;
    int num_blocks = (num_kangaroos + threads_per_block - 1) / threads_per_block;

    cpu_dp_table_t *cpu_dpt = cpu_dp_create();

    uint64_t max_total_steps = sqrt_half * 32 + 20000;
    if (max_total_steps > 500000000ULL) max_total_steps = 500000000ULL;
    uint64_t max_launches = max_total_steps / STEPS_PER_LAUNCH + 1;

    int found = 0;
    dp_entry_t *h_dp_buf = (dp_entry_t *)malloc(dp_buf_size * sizeof(dp_entry_t));

    for (uint64_t launch = 0; launch < max_launches && !found; launch++) {
        cudaMemcpy(d_dp_count, &zero, sizeof(int), cudaMemcpyHostToDevice);

        kangaroo_walk_kernel<<<num_blocks, threads_per_block>>>(
            d_kx, d_ky, d_kpos, d_kinf,
            num_kangaroos, n_tame, dp_mask,
            d_dp_buf, d_dp_count, dp_buf_size,
            d_found, STEPS_PER_LAUNCH);
        cudaDeviceSynchronize();

        int dp_count = 0;
        cudaMemcpy(&dp_count, d_dp_count, sizeof(int), cudaMemcpyDeviceToHost);
        if (dp_count > dp_buf_size) dp_count = dp_buf_size;

        if (dp_count > 0) {
            cudaMemcpy(h_dp_buf, d_dp_buf, dp_count * sizeof(dp_entry_t), cudaMemcpyDeviceToHost);

            for (int i = 0; i < dp_count && !found; i++) {
                dp_entry_t *e = &h_dp_buf[i];
                uint64_t ex[4] = { e->x1, e->x2, e->x3, e->x4 };
                int is_tame = e->is_tame ? 1 : 0;

                cpu_dp_entry_t *match = cpu_dp_find(cpu_dpt, ex, is_tame);
                if (match) {
                    /* Try both signs for k */
                    int64_t diff;
                    if (is_tame) diff = (int64_t)e->pos - (int64_t)match->pos;
                    else diff = (int64_t)match->pos - (int64_t)e->pos;

                    /* Try k_cand = |diff| and also bound_val - |diff| */
                    uint64_t candidates[4];
                    int ncand = 0;
                    if (diff >= 0) {
                        candidates[ncand++] = (uint64_t)diff;
                        if ((uint64_t)diff <= bound_val)
                            candidates[ncand++] = bound_val - (uint64_t)diff;
                    } else {
                        candidates[ncand++] = (uint64_t)(-diff);
                        if ((uint64_t)(-diff) <= bound_val)
                            candidates[ncand++] = bound_val - (uint64_t)(-diff);
                    }

                    for (int ci = 0; ci < ncand && !found; ci++) {
                        uint64_t k_cand = candidates[ci];
                        if (k_cand == 0 || k_cand > bound_val) continue;
                        h_fe_t vx, vy; int vinf;
                        h_ec_smul(&vx, &vy, &vinf, k_cand, &Gx, &Gy);
                        if (!vinf && vx.v[0] == Px.v[0] && vx.v[1] == Px.v[1] &&
                            vx.v[2] == Px.v[2] && vx.v[3] == Px.v[3] &&
                            vy.v[0] == Py.v[0] && vy.v[1] == Py.v[1] &&
                            vy.v[2] == Py.v[2] && vy.v[3] == Py.v[3]) {
                            snprintf(result, result_size, "%llx", (unsigned long long)k_cand);
                            found = 1;
                        }
                    }
                }
                if (!found) cpu_dp_insert(cpu_dpt, ex, e->pos, is_tame);
            }
        }
    }

    cpu_dp_destroy(cpu_dpt);
    free(h_dp_buf);
    free(h_kx); free(h_ky); free(h_kpos); free(h_kinf);
    cudaFree(d_kx); cudaFree(d_ky); cudaFree(d_kpos);
    cudaFree(d_kinf); cudaFree(d_found);
    cudaFree(d_dp_buf); cudaFree(d_dp_count);

    return found;
}
