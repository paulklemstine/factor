/*
 * GF(2) Linear Algebra — C shared library for SIQS/GNFS
 *
 * gauss_gf2_c: O(n^3/64) bitpacked Gauss elimination
 *   - Cache-friendly row layout (contiguous uint64 words)
 *   - All XOR operations on full uint64 words
 *   - ~2-5x faster than numpy-based Python Gauss
 *
 * block_lanczos: O(n^2*w/64) Block Lanczos (Montgomery 1995)
 *   - Experimental; not yet reliable for production use
 *   - Falls back gracefully (returns 0 deps, caller uses Gauss)
 *
 * Compile: gcc -O3 -march=native -shared -fPIC -o block_lanczos_c.so block_lanczos_c.c
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* ================================================================== */
/* Sparse matrix (CSR) and operations                                  */
/* ================================================================== */
typedef struct {
    int nrows, ncols, nnz;
    int *row_ptr, *col_idx;
} sparse_t;

/* y = A * x  (block of 64 vectors) */
static void spmv(const sparse_t *A, const uint64_t *x, uint64_t *y)
{
    for (int i = 0; i < A->nrows; i++) {
        uint64_t acc = 0;
        for (int j = A->row_ptr[i]; j < A->row_ptr[i + 1]; j++)
            acc ^= x[A->col_idx[j]];
        y[i] = acc;
    }
}

/* y = A^T * x  (block of 64 vectors) */
static void spmv_t(const sparse_t *A, const uint64_t *x, uint64_t *y)
{
    memset(y, 0, (size_t)A->ncols * sizeof(uint64_t));
    for (int i = 0; i < A->nrows; i++) {
        uint64_t xi = x[i];
        if (!xi) continue;
        for (int j = A->row_ptr[i]; j < A->row_ptr[i + 1]; j++)
            y[A->col_idx[j]] ^= xi;
    }
}

/* y = B*x = A * A^T * x */
static void mul_B(const sparse_t *A, const uint64_t *x, uint64_t *y,
                  uint64_t *tmp)
{
    spmv_t(A, x, tmp);
    spmv(A, tmp, y);
}

/* ================================================================== */
/* 64x64 GF(2) matrix operations                                      */
/* ================================================================== */
static void inner_prod(const uint64_t *a, const uint64_t *b, int n,
                       uint64_t *C)
{
    memset(C, 0, 64 * sizeof(uint64_t));
    for (int i = 0; i < n; i++) {
        uint64_t ai = a[i], bi = b[i];
        if (!ai) continue;
        while (ai) {
            C[__builtin_ctzll(ai)] ^= bi;
            ai &= ai - 1;
        }
    }
}

static inline uint64_t m64v(const uint64_t *M, uint64_t x)
{
    uint64_t r = 0;
    while (x) { r ^= M[__builtin_ctzll(x)]; x &= x - 1; }
    return r;
}

static void m64_mul(const uint64_t *A, const uint64_t *B, uint64_t *C)
{
    for (int i = 0; i < 64; i++) C[i] = m64v(B, A[i]);
}

static void m64_transpose(const uint64_t *A, uint64_t *B)
{
    memset(B, 0, 64 * sizeof(uint64_t));
    for (int i = 0; i < 64; i++) {
        uint64_t row = A[i];
        while (row) {
            int j = __builtin_ctzll(row);
            B[j] |= (uint64_t)1 << i;
            row &= row - 1;
        }
    }
}

static int m64_partial_inv(const uint64_t *S, uint64_t *Sinv, uint64_t *mask)
{
    uint64_t w[64], inv[64];
    memcpy(w, S, 64 * sizeof(uint64_t));
    for (int i = 0; i < 64; i++) inv[i] = (uint64_t)1 << i;
    uint64_t used = 0;
    int rank = 0;
    for (int col = 0; col < 64; col++) {
        uint64_t cb = (uint64_t)1 << col;
        int piv = -1;
        for (int r = 0; r < 64; r++)
            if (!(used & ((uint64_t)1 << r)) && (w[r] & cb)) { piv = r; break; }
        if (piv < 0) continue;
        used |= (uint64_t)1 << piv;
        rank++;
        for (int r = 0; r < 64; r++)
            if (r != piv && (w[r] & cb)) { w[r] ^= w[piv]; inv[r] ^= inv[piv]; }
    }
    memset(Sinv, 0, 64 * sizeof(uint64_t));
    for (int i = 0; i < 64; i++)
        if (used & ((uint64_t)1 << i)) Sinv[i] = inv[i];
    *mask = used;
    return rank;
}

static void apply_mask(uint64_t *v, int n, uint64_t mask)
{
    for (int i = 0; i < n; i++) v[i] &= mask;
}

static int is_zero(const uint64_t *v, int n)
{
    for (int i = 0; i < n; i++) if (v[i]) return 0;
    return 1;
}

/* Helper: extract null space columns from a candidate n-vector.
 * Checks A^T * cand = 0 for each of the 64 columns, and appends
 * the valid ones to deps[]. */
static int extract_null_cols(const sparse_t *A, const uint64_t *cand,
                             int n, uint64_t *deps, int nwords_dep,
                             int max_deps, int ndeps, uint64_t *tmpc)
{
    if (is_zero(cand, n)) return ndeps;

    spmv_t(A, cand, tmpc);
    uint64_t good = ~(uint64_t)0;
    for (int j = 0; j < A->ncols; j++) good &= ~tmpc[j];

    while (good && ndeps < max_deps) {
        int c = __builtin_ctzll(good);
        good &= good - 1;
        uint64_t cbit = (uint64_t)1 << c;
        uint64_t *dep = deps + (size_t)ndeps * nwords_dep;
        memset(dep, 0, (size_t)nwords_dep * sizeof(uint64_t));
        int nz = 0;
        for (int i = 0; i < n; i++)
            if (cand[i] & cbit) { dep[i/64] |= (uint64_t)1 << (i%64); nz = 1; }
        if (nz) ndeps++;
    }
    return ndeps;
}

/* ================================================================== */
/* Block Lanczos — Montgomery (1995)                                   */
/*                                                                     */
/* Finds left null space of A: vectors x with A^T*x = 0.              */
/* Works on B = A*A^T (nrows x nrows, symmetric).                     */
/*                                                                     */
/* EXPERIMENTAL: May not find all null vectors. The SIQS engine        */
/* falls back to Gauss if this returns too few.                        */
/* ================================================================== */
int block_lanczos(const int *row_ptr, const int *col_idx,
                  int nrows, int ncols,
                  uint64_t *deps, int max_deps)
{
    sparse_t A;
    A.nrows = nrows;
    A.ncols = ncols;
    A.row_ptr = (int *)row_ptr;
    A.col_idx = (int *)col_idx;
    A.nnz = row_ptr[nrows];

    int n = nrows;
    /* Max iterations: rank(B) / 64. Since rank(B) <= min(nrows,ncols),
     * we use ncols/64 + slack. */
    int max_iter = (ncols < nrows ? ncols : nrows) / 64 + 20;
    if (max_iter < 10) max_iter = 10;

    uint64_t *V0    = (uint64_t *)calloc(n, sizeof(uint64_t));
    uint64_t *V1    = (uint64_t *)calloc(n, sizeof(uint64_t));
    uint64_t *V2    = (uint64_t *)calloc(n, sizeof(uint64_t));
    uint64_t *BV    = (uint64_t *)calloc(n, sizeof(uint64_t));
    uint64_t *BBV   = (uint64_t *)calloc(n, sizeof(uint64_t));
    uint64_t *tmpc  = (uint64_t *)calloc(ncols > 0 ? ncols : 1, sizeof(uint64_t));
    uint64_t *x_acc = (uint64_t *)calloc(n, sizeof(uint64_t));
    uint64_t *y0    = (uint64_t *)malloc((size_t)n * sizeof(uint64_t));

    if (!V0 || !V1 || !V2 || !BV || !BBV || !tmpc || !x_acc || !y0) {
        free(V0); free(V1); free(V2); free(BV); free(BBV);
        free(tmpc); free(x_acc); free(y0);
        return -1;
    }

    int ndeps = 0;
    int nwords_dep = (nrows + 63) / 64;

    /* Random seed */
    {
        uint64_t s = 0xDEADBEEFCAFEBABEULL;
        for (int i = 0; i < n; i++) {
            s ^= s << 13; s ^= s >> 7; s ^= s << 17;
            y0[i] = s;
            V1[i] = s;
        }
    }

    uint64_t S[64], Sinv[64], prevSinv[64], mask;

    mul_B(&A, V1, BV, tmpc);
    inner_prod(V1, BV, n, S);
    int rk = m64_partial_inv(S, Sinv, &mask);

    if (rk == 0) goto extract;

    /* Save dropped columns */
    if (rk < 64) {
        for (int i = 0; i < n; i++) V2[i] = V1[i] & ~mask;
        ndeps = extract_null_cols(&A, V2, n, deps, nwords_dep, max_deps, ndeps, tmpc);
    }

    apply_mask(V1, n, mask);
    mul_B(&A, V1, BV, tmpc);
    inner_prod(V1, BV, n, S);
    rk = m64_partial_inv(S, Sinv, &mask);

    /* Accumulate */
    {
        uint64_t Vty[64], W[64];
        inner_prod(V1, y0, n, Vty);
        m64_mul(Sinv, Vty, W);
        for (int i = 0; i < n; i++) x_acc[i] ^= m64v(W, V1[i]);
    }

    memset(prevSinv, 0, sizeof(prevSinv));

    for (int iter = 0; iter < max_iter; iter++) {
        mul_B(&A, BV, BBV, tmpc);

        uint64_t VtBBV[64], D[64];
        inner_prod(V1, BBV, n, VtBBV);
        m64_mul(Sinv, VtBBV, D);

        uint64_t VpBV[64], VpBVt[64], E[64];
        inner_prod(V0, BV, n, VpBV);
        m64_transpose(VpBV, VpBVt);
        m64_mul(prevSinv, VpBVt, E);

        for (int i = 0; i < n; i++)
            V2[i] = BV[i] ^ m64v(D, V1[i]) ^ m64v(E, V0[i]);

        if (is_zero(V2, n)) break;

        uint64_t Snew[64], Snewinv[64], masknew;
        mul_B(&A, V2, BV, tmpc);
        inner_prod(V2, BV, n, Snew);
        int rknew = m64_partial_inv(Snew, Snewinv, &masknew);

        if (rknew == 0) {
            ndeps = extract_null_cols(&A, V2, n, deps, nwords_dep, max_deps, ndeps, tmpc);
            break;
        }

        /* Save dropped columns */
        if (rknew < 64) {
            uint64_t drop_mask = ~masknew;
            /* Need a temp copy since we're about to mask V2 */
            for (int i = 0; i < n; i++) BBV[i] = V2[i] & drop_mask;
            ndeps = extract_null_cols(&A, BBV, n, deps, nwords_dep, max_deps, ndeps, tmpc);
            /* Restore BBV for next iteration's use (it gets recomputed) */
        }

        apply_mask(V2, n, masknew);
        mul_B(&A, V2, BV, tmpc);
        inner_prod(V2, BV, n, Snew);
        rknew = m64_partial_inv(Snew, Snewinv, &masknew);

        {
            uint64_t Vty[64], W[64];
            inner_prod(V2, y0, n, Vty);
            m64_mul(Snewinv, Vty, W);
            for (int i = 0; i < n; i++) x_acc[i] ^= m64v(W, V2[i]);
        }

        uint64_t *tmp = V0; V0 = V1; V1 = V2; V2 = tmp;
        memcpy(prevSinv, Sinv, sizeof(Sinv));
        memcpy(Sinv, Snewinv, sizeof(Sinv));

        if (rknew <= 1 && iter > 3) break;
    }

extract:
    /* z = B*x_acc ^ y0 */
    mul_B(&A, x_acc, V2, tmpc);
    for (int i = 0; i < n; i++) V2[i] ^= y0[i];
    ndeps = extract_null_cols(&A, V2, n, deps, nwords_dep, max_deps, ndeps, tmpc);

    /* Also try x_acc and V1 */
    ndeps = extract_null_cols(&A, x_acc, n, deps, nwords_dep, max_deps, ndeps, tmpc);
    ndeps = extract_null_cols(&A, V1, n, deps, nwords_dep, max_deps, ndeps, tmpc);

    free(V0); free(V1); free(V2); free(BV); free(BBV);
    free(tmpc); free(x_acc); free(y0);
    return ndeps;
}


/* ================================================================== */
/* Gauss elimination in C — PRODUCTION                                 */
/*                                                                     */
/* O(n^3/64) with cache-friendly row layout. ~2-5x faster than numpy. */
/* Finds ALL null vectors (complete null space).                       */
/* ================================================================== */
int gauss_gf2_c(const int *row_ptr, const int *col_idx,
                int nrows, int ncols,
                uint64_t *deps, int max_deps)
{
    int nwords = (ncols + 63) / 64;
    int cwords = (nrows + 63) / 64;

    uint64_t *mat   = (uint64_t *)calloc((size_t)nrows * nwords, sizeof(uint64_t));
    uint64_t *combo = (uint64_t *)calloc((size_t)nrows * cwords, sizeof(uint64_t));
    int *used = (int *)calloc(nrows, sizeof(int));

    if (!mat || !combo || !used) {
        free(mat); free(combo); free(used);
        return -1;
    }

    /* Build from CSR */
    for (int i = 0; i < nrows; i++) {
        for (int j = row_ptr[i]; j < row_ptr[i + 1]; j++) {
            int c = col_idx[j];
            mat[(size_t)i * nwords + c / 64] |= (uint64_t)1 << (c % 64);
        }
        combo[(size_t)i * cwords + i / 64] = (uint64_t)1 << (i % 64);
    }

    /* Row reduction */
    for (int col = 0; col < ncols; col++) {
        int w = col / 64;
        uint64_t bit = (uint64_t)1 << (col % 64);

        /* Find pivot */
        int piv = -1;
        for (int i = 0; i < nrows; i++) {
            if (!used[i] && (mat[(size_t)i * nwords + w] & bit)) {
                piv = i; break;
            }
        }
        if (piv < 0) continue;
        used[piv] = 1;

        /* Eliminate: XOR pivot row into all others that have this bit */
        uint64_t *pm = mat + (size_t)piv * nwords;
        uint64_t *pc = combo + (size_t)piv * cwords;
        for (int i = 0; i < nrows; i++) {
            if (i != piv && (mat[(size_t)i * nwords + w] & bit)) {
                uint64_t *rm = mat + (size_t)i * nwords;
                uint64_t *rc = combo + (size_t)i * cwords;
                for (int j = 0; j < nwords; j++) rm[j] ^= pm[j];
                for (int j = 0; j < cwords; j++) rc[j] ^= pc[j];
            }
        }
    }

    /* Extract null vectors: rows that became all-zero */
    int ndeps = 0;
    int nwords_dep = (nrows + 63) / 64;
    for (int i = 0; i < nrows && ndeps < max_deps; i++) {
        int zero = 1;
        for (int j = 0; j < nwords; j++) {
            if (mat[(size_t)i * nwords + j]) { zero = 0; break; }
        }
        if (!zero) continue;

        int nonzero = 0;
        uint64_t *ci = combo + (size_t)i * cwords;
        for (int j = 0; j < cwords; j++) {
            if (ci[j]) { nonzero = 1; break; }
        }
        if (!nonzero) continue;

        uint64_t *dep = deps + (size_t)ndeps * nwords_dep;
        memset(dep, 0, (size_t)nwords_dep * sizeof(uint64_t));
        for (int j = 0; j < cwords && j < nwords_dep; j++)
            dep[j] = ci[j];
        ndeps++;
    }

    free(mat); free(combo); free(used);
    return ndeps;
}
