/*
 * GF(2) Linear Algebra — Wiedemann + Gauss
 *
 * 1. gauss_gf2_c: O(n^3/64) bitpacked Gauss (proven, for n < ~15K)
 * 2. block_lanczos_v2: Wiedemann algorithm (for large matrices, n up to 500K+)
 *    - Phase 1: Block Krylov sequence + Berlekamp-Massey
 *    - Phase 2: Block extraction of null vectors
 *    - Complexity: O(n * w * rank / 64) total
 *    - Memory: O(n + rank) — about 16 MB for n=500K
 *
 * Compile: gcc -O3 -march=native -shared -fPIC -o block_lanczos_c.so block_lanczos_v2.c
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* ================================================================== */
/* Sparse matrix (CSR)                                                 */
/* ================================================================== */
typedef struct {
    int nrows, ncols, nnz;
    int *row_ptr, *col_idx;
} sparse_t;

/* ================================================================== */
/* Block (64-wide) sparse mat-vec                                      */
/*                                                                     */
/* Each vector element is a uint64 representing 64 GF(2) values.       */
/* This is the core hot loop — optimized for throughput.               */
/* ================================================================== */

/* y = A * x  (block of 64 vectors) */
static void spmv_block(const sparse_t *A, const uint64_t *x, uint64_t *y)
{
    for (int i = 0; i < A->nrows; i++) {
        uint64_t acc = 0;
        int end = A->row_ptr[i + 1];
        for (int j = A->row_ptr[i]; j < end; j++)
            acc ^= x[A->col_idx[j]];
        y[i] = acc;
    }
}

/* y = A^T * x  (block of 64 vectors, transpose) */
static void spmv_t_block(const sparse_t *A, const uint64_t *x, uint64_t *y)
{
    memset(y, 0, (size_t)A->ncols * sizeof(uint64_t));
    for (int i = 0; i < A->nrows; i++) {
        uint64_t xi = x[i];
        if (!xi) continue;
        int end = A->row_ptr[i + 1];
        for (int j = A->row_ptr[i]; j < end; j++)
            y[A->col_idx[j]] ^= xi;
    }
}

/* y = B*x = A*(A^T*x), the core expensive operation */
static void mul_B_block(const sparse_t *A, const uint64_t *x, uint64_t *y,
                        uint64_t *tmp)
{
    spmv_t_block(A, x, tmp);  /* tmp = A^T * x  (ncols) */
    spmv_block(A, tmp, y);     /* y   = A * tmp  (nrows) */
}

/* ================================================================== */
/* Berlekamp-Massey over GF(2)                                         */
/*                                                                     */
/* Returns degree L of the minimal polynomial, or -1 on error.         */
/* poly[0..L] are the coefficients with poly[0] = 1.                   */
/* ================================================================== */
static int berlekamp_massey(const uint8_t *s, int N, uint8_t *poly)
{
    uint8_t *c = (uint8_t *)calloc(N + 1, 1);
    uint8_t *b = (uint8_t *)calloc(N + 1, 1);
    uint8_t *t_arr = (uint8_t *)calloc(N + 1, 1);
    if (!c || !b || !t_arr) {
        free(c); free(b); free(t_arr);
        return -1;
    }

    c[0] = 1;
    b[0] = 1;
    int L = 0, m = 1;

    for (int i = 0; i < N; i++) {
        int d = s[i];
        for (int j = 1; j <= L; j++)
            d ^= (c[j] & s[i - j]);
        d &= 1;

        if (d == 0) {
            m++;
        } else {
            memcpy(t_arr, c, N + 1);
            for (int j = m; j <= N; j++)
                c[j] ^= b[j - m];
            if (2 * L <= i) {
                L = i + 1 - L;
                memcpy(b, t_arr, N + 1);
                m = 1;
            } else {
                m++;
            }
        }
    }

    memcpy(poly, c, L + 1);
    free(c); free(b); free(t_arr);
    return L;
}

/* ================================================================== */
/* Wiedemann null-space finder                                          */
/*                                                                     */
/* Phase 1: Krylov sequence computation                                */
/*   Use block mat-vec (64-wide) for speed. Embed x as a single        */
/*   column (bit 0) of the block. The GF(2) dot product x^T * B^i * x */
/*   is extracted from the parity of (x & v) at bit position 0.        */
/*   Cost: O(n * w * rank / 64) — same as one pass of block mat-vec.  */
/*                                                                     */
/* Phase 2: Berlekamp-Massey to find minimal polynomial                */
/*   Reverse and factor out t to get r(t) such that r(B)*y in null(B). */
/*                                                                     */
/* Phase 3: Block extraction                                           */
/*   Apply r(B) to 64 random vectors simultaneously.                   */
/*   Cost: O(n * w * rank / 64).                                       */
/*                                                                     */
/* Total: O(n * w * rank / 32) — two passes of block mat-vec.          */
/* Memory: O(n + rank) — vectors + polynomial.                         */
/* ================================================================== */
int block_lanczos_v2(const int *row_ptr, const int *col_idx,
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
    int ndeps = 0;
    int nwords_dep = (nrows + 63) / 64;

    /* Block vectors for both Phase 1 and Phase 3 */
    uint64_t *v_blk  = (uint64_t *)calloc(n, sizeof(uint64_t));
    uint64_t *Bv_blk = (uint64_t *)calloc(n, sizeof(uint64_t));
    uint64_t *V_blk  = (uint64_t *)calloc(n, sizeof(uint64_t));
    uint64_t *tmp_nc = (uint64_t *)calloc(ncols > 0 ? ncols : 1, sizeof(uint64_t));

    if (!v_blk || !Bv_blk || !V_blk || !tmp_nc) {
        free(v_blk); free(Bv_blk); free(V_blk); free(tmp_nc);
        return -1;
    }

    /* Sequence and polynomial buffers */
    int rank_bound = ncols < nrows ? ncols : nrows;
    int seq_len = 2 * rank_bound + 200;

    uint8_t *seq  = (uint8_t *)calloc(seq_len, 1);
    uint8_t *poly = (uint8_t *)calloc(seq_len + 1, 1);
    if (!seq || !poly) {
        free(v_blk); free(Bv_blk); free(V_blk); free(tmp_nc);
        free(seq); free(poly);
        return -1;
    }

    /* Multiple rounds with different seeds */
    for (int round = 0; round < 10 && ndeps < max_deps; round++) {

        /* === Phase 1: Block Krylov sequence ===
         *
         * We embed x in bit 0 of the block vector. Then B^i * x is
         * tracked in bit 0 of each element. The other 63 bits are
         * garbage from the block mat-vec, but we only look at bit 0
         * for the sequence computation.
         *
         * s_i = x^T * B^i * x = parity of {j : x[j]=1 AND (B^i*x)[j]=1}
         * = popcount(x_block & v_block) restricted to bit 0
         * = popcount of (x_block[j] & v_block[j] & 1) for all j
         * But since x_block[j] is either 0 or 1 (bit 0 only), and v_block[j]
         * has bit 0 = (B^i*x)[j], we want: XOR over j of (x[j] & v[j] & 1).
         * = parity of popcount({j : x_block[j] & v_block[j] & 1}).
         *
         * Optimization: store x separately and compute the dot product
         * using bit 0 masks.
         */

        /* Generate x as bit-0-only block vector */
        {
            uint64_t s = 0xB5A1D2F3E4C6A7B8ULL +
                         (uint64_t)round * 0x123456789ABCDEFULL;
            for (int i = 0; i < n; i++) {
                s ^= s << 13; s ^= s >> 7; s ^= s << 17;
                s += (uint64_t)i * 0x9E3779B97F4A7C15ULL;
                v_blk[i] = s & 1;  /* bit 0 only */
            }
        }

        /* Store x for dot products (we'll modify v_blk in-place) */
        /* Use V_blk temporarily to store x */
        memcpy(V_blk, v_blk, (size_t)n * sizeof(uint64_t));

        for (int i = 0; i < seq_len; i++) {
            /* s[i] = x^T * v (bit 0 only) */
            int parity = 0;
            for (int j = 0; j < n; j++)
                parity += (int)(V_blk[j] & v_blk[j] & 1);
            seq[i] = (uint8_t)(parity & 1);

            if (i < seq_len - 1) {
                mul_B_block(&A, v_blk, Bv_blk, tmp_nc);
                /* Mask to bit 0 only to prevent pollution from other bits */
                for (int j = 0; j < n; j++)
                    Bv_blk[j] &= 1;
                uint64_t *t = v_blk; v_blk = Bv_blk; Bv_blk = t;
            }
        }

        /* === Phase 2: Berlekamp-Massey === */
        memset(poly, 0, seq_len + 1);
        int deg = berlekamp_massey(seq, seq_len, poly);
        if (deg <= 0) continue;

        /* Reverse polynomial and factor out t^k */
        /* Reuse seq buffer for reversed poly (BM is done with seq) */
        uint8_t *poly_rev = seq;
        for (int i = 0; i <= deg; i++)
            poly_rev[i] = poly[deg - i];

        int k = 0;
        while (k <= deg && poly_rev[k] == 0) k++;
        if (k == 0) continue;  /* No t factor — cannot extract null vectors */

        int r_deg = deg - k;
        uint8_t *r_poly = poly_rev + k;

        /* === Phase 3: Block extraction via r(B) * Y ===
         *
         * Generate a random 64-wide block Y and compute V = r(B) * Y.
         * Each column of V is independently in null(B).
         * Verify with A^T * V = 0 column-by-column.
         */
        {
            uint64_t s = 0xCAFEBABEDEADBEEFULL +
                         (uint64_t)round * 0xFEDCBA9876543210ULL;
            for (int i = 0; i < n; i++) {
                s ^= s << 13; s ^= s >> 7; s ^= s << 17;
                s += (uint64_t)i * 0x6A09E667F3BCC908ULL;
                v_blk[i] = s;  /* Full 64-bit random for block */
            }
        }

        /* V = r(B) * Y = sum_{j=0}^{r_deg} r[j] * B^j * Y */
        memset(V_blk, 0, (size_t)n * sizeof(uint64_t));

        for (int j = 0; j <= r_deg; j++) {
            if (r_poly[j]) {
                for (int i = 0; i < n; i++)
                    V_blk[i] ^= v_blk[i];
            }
            if (j < r_deg) {
                mul_B_block(&A, v_blk, Bv_blk, tmp_nc);
                uint64_t *t = v_blk; v_blk = Bv_blk; Bv_blk = t;
            }
        }

        /* Verify: find columns of V_blk in null(A^T) */
        {
            uint64_t *AtV = (uint64_t *)calloc(ncols > 0 ? ncols : 1,
                                                sizeof(uint64_t));
            if (AtV) {
                spmv_t_block(&A, V_blk, AtV);

                uint64_t good = ~(uint64_t)0;
                for (int j = 0; j < ncols; j++)
                    good &= ~AtV[j];

                while (good && ndeps < max_deps) {
                    int c = __builtin_ctzll(good);
                    good &= good - 1;
                    uint64_t cbit = (uint64_t)1 << c;

                    /* Check non-zero */
                    int nz = 0;
                    for (int i = 0; i < n; i++) {
                        if (V_blk[i] & cbit) { nz = 1; break; }
                    }
                    if (!nz) continue;

                    /* Pack as bitpacked dependency */
                    uint64_t *dep = deps + (size_t)ndeps * nwords_dep;
                    memset(dep, 0, (size_t)nwords_dep * sizeof(uint64_t));
                    for (int i = 0; i < n; i++) {
                        if (V_blk[i] & cbit)
                            dep[i / 64] |= (uint64_t)1 << (i % 64);
                    }
                    ndeps++;
                }
                free(AtV);
            }
        }

        if (ndeps >= max_deps) break;
    }

    free(v_blk); free(Bv_blk); free(V_blk); free(tmp_nc);
    free(seq); free(poly);
    return ndeps;
}


/* ================================================================== */
/* Gauss elimination in C — PRODUCTION                                 */
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

    for (int i = 0; i < nrows; i++) {
        for (int j = row_ptr[i]; j < row_ptr[i + 1]; j++) {
            int c = col_idx[j];
            mat[(size_t)i * nwords + c / 64] |= (uint64_t)1 << (c % 64);
        }
        combo[(size_t)i * cwords + i / 64] = (uint64_t)1 << (i % 64);
    }

    for (int col = 0; col < ncols; col++) {
        int w = col / 64;
        uint64_t bit = (uint64_t)1 << (col % 64);

        int piv = -1;
        for (int i = 0; i < nrows; i++) {
            if (!used[i] && (mat[(size_t)i * nwords + w] & bit)) {
                piv = i; break;
            }
        }
        if (piv < 0) continue;
        used[piv] = 1;

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
