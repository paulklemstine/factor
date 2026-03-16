/*
 * lattice_sieve_c.c — Fast GNFS lattice sieve in C
 *
 * For each special-q, sieves in reduced (i,j) lattice coordinates.
 * Returns candidate (i,j) pairs that pass combined log threshold.
 * Verification (trial division) is done by the caller using the existing
 * verify_candidates_c from gnfs_sieve_c.so or Python fallback.
 *
 * Compile: gcc -O3 -march=native -shared -fPIC -o lattice_sieve_c.so lattice_sieve_c.c -lm
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

/* ======== GCD for coprimality check ======== */
static int64_t gcd64(int64_t a, int64_t b) {
    if (a < 0) a = -a;
    if (b < 0) b = -b;
    while (b) { int64_t t = b; b = a % b; a = t; }
    return a;
}

/* ======== Modular inverse (extended GCD) ======== */
static int64_t mod_inverse(int64_t a, int64_t p) {
    int64_t g = p, x = 0, y = 1;
    int64_t a0 = ((a % p) + p) % p;
    int64_t g0 = a0;
    while (g0 != 0) {
        int64_t q = g / g0;
        int64_t tmp;
        tmp = g - q * g0; g = g0; g0 = tmp;
        tmp = x - q * y; x = y; y = tmp;
    }
    if (g != 1) return 0;  /* no inverse */
    return ((x % p) + p) % p;
}

/* ======== Gauss 2D lattice reduction ======== */
void gauss_reduce_c(int64_t *ux, int64_t *uy, int64_t *vx, int64_t *vy) {
    while (1) {
        int64_t nu = (*ux) * (*ux) + (*uy) * (*uy);
        int64_t nv = (*vx) * (*vx) + (*vy) * (*vy);
        if (nv < nu) {
            int64_t t;
            t = *ux; *ux = *vx; *vx = t;
            t = *uy; *uy = *vy; *vy = t;
            t = nu; nu = nv; nv = t;
        }
        if (nu == 0) break;
        int64_t dot = (*ux) * (*vx) + (*uy) * (*vy);
        int64_t mu = (dot >= 0) ? (dot + nu / 2) / nu : -((-dot + nu / 2) / nu);
        if (mu == 0) break;
        *vx -= mu * (*ux);
        *vy -= mu * (*uy);
    }
}

/*
 * lattice_sieve_q: Sieve one special-q region in (i,j) lattice coords.
 *
 * For each row j in [0, J_max]:
 *   Rational hits:  i = -j * (R2 * R1^{-1}) mod p, stride p
 *   Algebraic hits: i = -j * (V * U^{-1}) mod p, stride p
 *
 * Returns number of candidates found. Outputs (i,j) pairs.
 */
int lattice_sieve_q(
    int64_t e1x, int64_t e1y, int64_t e2x, int64_t e2y,
    int I_max, int J_max,
    const int64_t *rat_primes, int n_rat, int64_t m,
    const int64_t *alg_primes, const int64_t *alg_roots, int n_alg,
    double rat_frac, double alg_frac,
    int64_t q, int poly_degree,
    int *out_i, int *out_j, int max_cands)
{
    int size = 2 * I_max + 1;
    int total = 0;

    /* Precompute log(p)*128 for each FB prime */
    uint16_t *rat_lps = (uint16_t *)malloc(n_rat * sizeof(uint16_t));
    uint16_t *alg_lps = (uint16_t *)malloc(n_alg * sizeof(uint16_t));
    if (!rat_lps || !alg_lps) { free(rat_lps); free(alg_lps); return 0; }

    for (int i = 0; i < n_rat; i++)
        rat_lps[i] = (uint16_t)(log((double)rat_primes[i]) * 128.0 + 0.5);
    for (int i = 0; i < n_alg; i++)
        alg_lps[i] = (uint16_t)(log((double)alg_primes[i]) * 128.0 + 0.5);

    /* Precompute per-prime lattice projections */
    /* Rational: R1 = (e1x + e1y*m) mod p, R2 = (e2x + e2y*m) mod p */
    int64_t *rat_R2_R1inv = (int64_t *)malloc(n_rat * sizeof(int64_t));
    int     *rat_valid    = (int *)calloc(n_rat, sizeof(int));
    if (!rat_R2_R1inv || !rat_valid) goto cleanup;

    for (int i = 0; i < n_rat; i++) {
        int64_t p = rat_primes[i];
        int64_t e1xp = ((e1x % p) + p) % p;
        int64_t e1yp = ((e1y % p) + p) % p;
        int64_t mp   = ((m % p) + p) % p;
        int64_t R1 = (e1xp + e1yp * mp % p) % p;
        int64_t e2xp = ((e2x % p) + p) % p;
        int64_t e2yp = ((e2y % p) + p) % p;
        int64_t R2 = (e2xp + e2yp * mp % p) % p;
        if (R1 != 0) {
            int64_t R1inv = mod_inverse(R1, p);
            rat_R2_R1inv[i] = (R2 * R1inv) % p;
            rat_valid[i] = 1;
        }
    }

    /* Algebraic: U = (e1x + e1y*r_p) mod p, V = (e2x + e2y*r_p) mod p */
    int64_t *alg_V_Uinv = (int64_t *)malloc(n_alg * sizeof(int64_t));
    int     *alg_valid   = (int *)calloc(n_alg, sizeof(int));
    if (!alg_V_Uinv || !alg_valid) goto cleanup;

    for (int i = 0; i < n_alg; i++) {
        int64_t p = alg_primes[i];
        int64_t rp = alg_roots[i];
        int64_t e1xp = ((e1x % p) + p) % p;
        int64_t e1yp = ((e1y % p) + p) % p;
        int64_t rpp  = ((rp % p) + p) % p;
        int64_t U = (e1xp + e1yp * rpp % p) % p;
        int64_t e2xp = ((e2x % p) + p) % p;
        int64_t e2yp = ((e2y % p) + p) % p;
        int64_t V = (e2xp + e2yp * rpp % p) % p;
        if (U != 0) {
            int64_t Uinv = mod_inverse(U, p);
            alg_V_Uinv[i] = (V * Uinv) % p;
            alg_valid[i] = 1;
        }
    }

    /* Sieve arrays — one row at a time (memory: 2 * size * 2 bytes) */
    uint16_t *rat_log = (uint16_t *)malloc(size * sizeof(uint16_t));
    uint16_t *alg_log = (uint16_t *)malloc(size * sizeof(uint16_t));
    if (!rat_log || !alg_log) goto cleanup;

    /* Norm estimates for thresholds */
    double e1_m = (double)e1x + (double)e1y * (double)m;
    double e2_m = (double)e2x + (double)e2y * (double)m;
    double log_q = log((double)q);

    for (int j = 0; j <= J_max && total < max_cands; j++) {
        memset(rat_log, 0, size * sizeof(uint16_t));
        memset(alg_log, 0, size * sizeof(uint16_t));

        /* --- Rational sieve for row j --- */
        for (int pi = 0; pi < n_rat; pi++) {
            if (!rat_valid[pi]) continue;
            int64_t p = rat_primes[pi];
            uint16_t lp = rat_lps[pi];
            int64_t start = ((-(int64_t)j * rat_R2_R1inv[pi]) % p + p) % p;
            start = (start + I_max) % p;
            for (int64_t idx = start; idx < size; idx += p)
                rat_log[idx] += lp;
        }

        /* --- Algebraic sieve for row j --- */
        for (int pi = 0; pi < n_alg; pi++) {
            if (!alg_valid[pi]) continue;
            int64_t p = alg_primes[pi];
            uint16_t lp = alg_lps[pi];
            int64_t start = ((-(int64_t)j * alg_V_Uinv[pi]) % p + p) % p;
            start = (start + I_max) % p;
            for (int64_t idx = start; idx < size; idx += p)
                alg_log[idx] += lp;
        }

        /* --- Threshold and collect --- */
        double rat_typical = fabs((double)I_max * e1_m + (double)j * e2_m);
        if (rat_typical < fabs(e1_m)) rat_typical = fabs(e1_m);
        if (rat_typical < 2.0) rat_typical = 2.0;
        uint16_t rat_thresh = (uint16_t)(rat_frac * log(rat_typical) * 128.0);

        double a_est = (double)I_max * fabs((double)e1x) + (double)j * fabs((double)e2x);
        double b_est = fmax(1.0, (double)I_max * fabs((double)e1y) + (double)j * fabs((double)e2y));
        double alg_log_norm = (double)poly_degree * log(fmax(a_est, b_est)) - log_q;
        uint16_t alg_thresh = (alg_log_norm > 1.0)
            ? (uint16_t)(alg_frac * alg_log_norm * 128.0) : 128;

        for (int idx = 0; idx < size && total < max_cands; idx++) {
            if (rat_log[idx] >= rat_thresh && alg_log[idx] >= alg_thresh) {
                int i_val = idx - I_max;
                if (i_val == 0 && j == 0) continue;
                out_i[total] = i_val;
                out_j[total] = j;
                total++;
            }
        }
    }

cleanup:
    free(rat_log); free(alg_log);
    free(rat_lps); free(alg_lps);
    free(rat_R2_R1inv); free(rat_valid);
    free(alg_V_Uinv); free(alg_valid);
    return total;
}

/*
 * lattice_sieve_batch: Process multiple special-q primes in one call.
 *
 * For each special-q in the array, finds roots, Gauss-reduces, sieves,
 * and returns (a, b) pairs (already converted from lattice coords).
 *
 * q_primes: array of special-q primes to process
 * q_roots:  corresponding roots of f(x) mod q  (one root per entry)
 * n_q:      number of special-q entries
 *
 * Output: out_a, out_b are the (a,b) pairs in original coordinates.
 *         out_q stores which special-q produced each relation.
 *
 * Returns total candidates across all q.
 */
int lattice_sieve_batch(
    const int64_t *q_primes, const int64_t *q_roots, int n_q,
    const int64_t *rat_primes, int n_rat, int64_t m,
    const int64_t *alg_primes, const int64_t *alg_roots, int n_alg,
    double rat_frac, double alg_frac,
    int poly_degree,
    int sieve_radius,   /* I_max for sieve region */
    int sieve_height,   /* J_max for sieve region */
    int *out_a, int *out_b, int64_t *out_q, int max_cands)
{
    int total = 0;

    /* Temp buffers for per-q sieve output (lattice coords) */
    int batch_max = max_cands > 50000 ? 50000 : max_cands;
    int *tmp_i = (int *)malloc(batch_max * sizeof(int));
    int *tmp_j = (int *)malloc(batch_max * sizeof(int));
    if (!tmp_i || !tmp_j) { free(tmp_i); free(tmp_j); return 0; }

    for (int qi = 0; qi < n_q && total < max_cands; qi++) {
        int64_t q = q_primes[qi];
        int64_t r = q_roots[qi];

        /* Gauss reduce lattice basis for this (q, r) */
        int64_t ux = q, uy = 0;
        int64_t vx = ((-r) % q + q) % q, vy = 1;
        gauss_reduce_c(&ux, &uy, &vx, &vy);

        /* Adaptive sieve region based on basis vector lengths */
        double len_e1 = sqrt((double)(ux * ux + uy * uy));
        double len_e2 = sqrt((double)(vx * vx + vy * vy));
        int I_max = (int)(50000.0 / fmax(len_e1, 1.0));
        if (I_max < 50) I_max = 50;
        if (I_max > sieve_radius) I_max = sieve_radius;
        int J_max = (int)(200.0 / fmax(len_e2, 1.0));
        if (J_max < 2) J_max = 2;
        if (J_max > sieve_height) J_max = sieve_height;

        int remaining = max_cands - total;
        int this_max = remaining < batch_max ? remaining : batch_max;

        int n_cands = lattice_sieve_q(
            ux, uy, vx, vy,
            I_max, J_max,
            rat_primes, n_rat, m,
            alg_primes, alg_roots, n_alg,
            rat_frac, alg_frac,
            q, poly_degree,
            tmp_i, tmp_j, this_max);

        /* Convert (i,j) lattice coords to (a,b) original coords */
        for (int k = 0; k < n_cands && total < max_cands; k++) {
            int64_t a = (int64_t)tmp_i[k] * ux + (int64_t)tmp_j[k] * vx;
            int64_t b = (int64_t)tmp_i[k] * uy + (int64_t)tmp_j[k] * vy;
            if (b <= 0 || a == 0) continue;
            /* Coprimality filter: skip gcd(|a|,b) != 1 — saves ~41% verify work */
            if (gcd64(a < 0 ? -a : a, b) != 1) continue;
            out_a[total] = (int)a;
            out_b[total] = (int)b;
            out_q[total] = q;
            total++;
        }
    }

    free(tmp_i);
    free(tmp_j);
    return total;
}
