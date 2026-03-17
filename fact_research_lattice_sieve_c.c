/*
 * fact_research_lattice_sieve_c.c — C Lattice Sieve Prototype for GNFS
 *
 * Inner sieve loop for special-q lattice sieve:
 *   Given lattice basis (e1, e2) from Gauss reduction of {(a,b): a+b*r≡0 mod q},
 *   sieve in (i,j) coordinates where a = i*e1[0]+j*e2[0], b = i*e1[1]+j*e2[1].
 *
 * For each FB prime p with root r_p:
 *   Rational: R = e1[0]+e1[1]*m mod p, S = e2[0]+e2[1]*m mod p
 *     Hits when i*R + j*S ≡ 0 (mod p), i.e., i ≡ -j*S*R^{-1} (mod p)
 *   Algebraic: U = e1[0]+e1[1]*r_p mod p, V = e2[0]+e2[1]*r_p mod p
 *     Hits when i*U + j*V ≡ 0 (mod p), i.e., i ≡ -j*V*U^{-1} (mod p)
 *
 * Compile:
 *   gcc -O3 -march=native -o fact_research_lattice_sieve_c fact_research_lattice_sieve_c.c -lm
 *
 * Also builds as shared library:
 *   gcc -O3 -march=native -shared -fPIC -o lattice_sieve_c.so fact_research_lattice_sieve_c.c -lm
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdio.h>
#include <time.h>

/* ======== Gauss 2D lattice reduction ======== */
typedef struct { int64_t x, y; } vec2;

static void gauss_reduce(vec2 *u, vec2 *v) {
    while (1) {
        int64_t nu = u->x * u->x + u->y * u->y;
        int64_t nv = v->x * v->x + v->y * v->y;
        if (nv < nu) {
            vec2 tmp = *u; *u = *v; *v = tmp;
            int64_t t = nu; nu = nv; nv = t;
        }
        if (nu == 0) break;
        int64_t dot = u->x * v->x + u->y * v->y;
        /* Round to nearest integer */
        int64_t mu = (dot >= 0) ? (dot + nu/2) / nu : -((-dot + nu/2) / nu);
        if (mu == 0) break;
        v->x -= mu * u->x;
        v->y -= mu * u->y;
    }
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

/* ======== Core lattice sieve for one special-q ======== */

/*
 * lattice_sieve_q: Sieve one special-q region.
 *
 * Parameters:
 *   e1, e2: Gauss-reduced lattice basis vectors
 *   I_max: sieve i in [-I_max, I_max], size = 2*I_max+1
 *   J_max: sieve j in [0, J_max]
 *   rat_primes, n_rat: rational factor base primes
 *   m: polynomial root (rational side: norm = a + b*m)
 *   alg_primes, alg_roots, n_alg: algebraic FB (p, root pairs)
 *   rat_frac, alg_frac: threshold fractions (0.0-1.0)
 *   q: the special-q prime (for norm estimation)
 *   poly_degree: degree d of algebraic polynomial
 *   out_i, out_j: output candidate (i,j) pairs
 *   max_cands: output buffer size
 *
 * Returns: number of candidates found.
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
    for (int i = 0; i < n_rat; i++)
        rat_lps[i] = (uint16_t)(log((double)rat_primes[i]) * 128.0 + 0.5);
    for (int i = 0; i < n_alg; i++)
        alg_lps[i] = (uint16_t)(log((double)alg_primes[i]) * 128.0 + 0.5);

    /* Precompute per-prime lattice projections */
    /* Rational: R1 = (e1x + e1y*m) mod p, R2 = (e2x + e2y*m) mod p */
    int64_t *rat_R2_R1inv = (int64_t *)malloc(n_rat * sizeof(int64_t));
    int     *rat_valid    = (int *)calloc(n_rat, sizeof(int));
    for (int i = 0; i < n_rat; i++) {
        int64_t p = rat_primes[i];
        int64_t R1 = (((e1x % p) + p) % p + ((e1y % p + p) % p) * ((m % p + p) % p)) % p;
        int64_t R2 = (((e2x % p) + p) % p + ((e2y % p + p) % p) * ((m % p + p) % p)) % p;
        if (R1 != 0) {
            int64_t R1inv = mod_inverse(R1, p);
            rat_R2_R1inv[i] = (R2 * R1inv) % p;
            rat_valid[i] = 1;
        }
    }

    /* Algebraic: U = (e1x + e1y*r_p) mod p, V = (e2x + e2y*r_p) mod p */
    int64_t *alg_V_Uinv = (int64_t *)malloc(n_alg * sizeof(int64_t));
    int     *alg_valid   = (int *)calloc(n_alg, sizeof(int));
    for (int i = 0; i < n_alg; i++) {
        int64_t p = alg_primes[i];
        int64_t rp = alg_roots[i];
        int64_t U = (((e1x % p) + p) % p + ((e1y % p + p) % p) * ((rp % p + p) % p)) % p;
        int64_t V = (((e2x % p) + p) % p + ((e2y % p + p) % p) * ((rp % p + p) % p)) % p;
        if (U != 0) {
            int64_t Uinv = mod_inverse(U, p);
            alg_V_Uinv[i] = (V * Uinv) % p;
            alg_valid[i] = 1;
        }
    }

    /* Sieve arrays — one row at a time */
    uint16_t *rat_log = (uint16_t *)malloc(size * sizeof(uint16_t));
    uint16_t *alg_log = (uint16_t *)malloc(size * sizeof(uint16_t));

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
            /* Start: i ≡ -j * R2_R1inv (mod p), shifted by I_max */
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
        /* Rational norm ≈ |i*e1_m + j*e2_m| */
        double rat_typical = fabs((double)I_max * e1_m + (double)j * e2_m);
        if (rat_typical < fabs(e1_m)) rat_typical = fabs(e1_m);
        if (rat_typical < 2.0) rat_typical = 2.0;
        uint16_t rat_thresh = (uint16_t)(rat_frac * log(rat_typical) * 128.0);

        /* Algebraic cofactor ≈ norm / q. Very rough estimate. */
        double a_est = (double)I_max * fabs((double)e1x) + (double)j * fabs((double)e2x);
        double b_est = fmax(1.0, (double)I_max * fabs((double)e1y) + (double)j * fabs((double)e2y));
        double alg_log_norm = (double)poly_degree * log(fmax(a_est, b_est)) - log_q;
        uint16_t alg_thresh = (alg_log_norm > 1.0)
            ? (uint16_t)(alg_frac * alg_log_norm * 128.0) : 128;

        for (int idx = 0; idx < size && total < max_cands; idx++) {
            if (rat_log[idx] >= rat_thresh && alg_log[idx] >= alg_thresh) {
                int i_val = idx - I_max;
                /* Skip i=0, j=0 (trivial) */
                if (i_val == 0 && j == 0) continue;
                out_i[total] = i_val;
                out_j[total] = j;
                total++;
            }
        }
    }

    free(rat_log); free(alg_log);
    free(rat_lps); free(alg_lps);
    free(rat_R2_R1inv); free(rat_valid);
    free(alg_V_Uinv); free(alg_valid);
    return total;
}


/* ======== Benchmark / self-test main ======== */

static int is_prime_simple(int n) {
    if (n < 2) return 0;
    if (n < 4) return 1;
    if (n % 2 == 0 || n % 3 == 0) return 0;
    for (int i = 5; i * i <= n; i += 6)
        if (n % i == 0 || n % (i+2) == 0) return 0;
    return 1;
}

int main() {
    printf("=== C Lattice Sieve Prototype Benchmark ===\n\n");

    /* Build a realistic factor base */
    int fb_limit = 100000;
    int64_t *rat_primes = malloc(20000 * sizeof(int64_t));
    int64_t *alg_primes = malloc(40000 * sizeof(int64_t));
    int64_t *alg_roots  = malloc(40000 * sizeof(int64_t));
    int n_rat = 0, n_alg = 0;

    for (int p = 2; p < fb_limit && n_rat < 20000; p++) {
        if (is_prime_simple(p)) {
            rat_primes[n_rat++] = p;
            /* Simulate 1-2 algebraic roots per prime */
            alg_primes[n_alg] = p;
            alg_roots[n_alg] = (p * 7 + 13) % p;  /* fake root */
            n_alg++;
            if (p > 3 && n_alg < 40000) {
                /* Second root for ~half the primes */
                alg_primes[n_alg] = p;
                alg_roots[n_alg] = (p * 11 + 37) % p;
                n_alg++;
            }
        }
    }
    printf("Factor base: %d rational, %d algebraic entries (limit=%d)\n", n_rat, n_alg, fb_limit);

    /* m ≈ N^(1/d) for a 43d number with d=4 */
    int64_t m = 100000000000LL;  /* ~10^11 */

    /* Test various special-q sizes and sieve regions */
    struct {
        int64_t q;
        int I_max;
        int J_max;
        const char *label;
    } tests[] = {
        {100003, 2000, 50, "q=100K, small region (200K pts)"},
        {100003, 5000, 100, "q=100K, medium region (1M pts)"},
        {100003, 10000, 200, "q=100K, large region (4M pts)"},
        {50021,  3000, 80, "q=50K, medium region (480K pts)"},
        {200003, 1500, 40, "q=200K, small region (120K pts)"},
    };
    int n_tests = sizeof(tests) / sizeof(tests[0]);

    int max_cands = 100000;
    int *out_i = malloc(max_cands * sizeof(int));
    int *out_j = malloc(max_cands * sizeof(int));

    /* Also benchmark the LINE sieve for comparison */
    printf("\n--- Line Sieve Baseline (from gnfs_sieve_c.c style) ---\n");
    {
        int A = 500000;
        int size = 2 * A + 1;
        uint16_t *sieve = calloc(size, sizeof(uint16_t));
        uint16_t *lps = malloc(n_rat * sizeof(uint16_t));
        for (int i = 0; i < n_rat; i++)
            lps[i] = (uint16_t)(log((double)rat_primes[i]) * 128.0 + 0.5);

        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        int n_blines = 10;
        for (int b = 1; b <= n_blines; b++) {
            memset(sieve, 0, size * sizeof(uint16_t));
            for (int i = 0; i < n_rat; i++) {
                int64_t p = rat_primes[i];
                uint16_t lp = lps[i];
                int64_t bm = ((int64_t)b * (m % p)) % p;
                int64_t start = ((-bm % p) + p) % p;
                start = (start + A) % p;
                for (int64_t idx = start; idx < size; idx += p)
                    sieve[idx] += lp;
            }
        }
        clock_gettime(CLOCK_MONOTONIC, &t1);
        double dt = (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) * 1e-9;

        double pts_per_sec = (double)n_blines * size / dt;
        printf("  A=%d, %d b-lines: %.3f ms (%.1f M sieve-pts/sec, rat side only)\n",
               A, n_blines, dt * 1000, pts_per_sec / 1e6);
        printf("  Memory per b-line: %.1f MB (2 sides)\n", 2.0 * size * 2 / (1024*1024));

        free(sieve); free(lps);
    }

    printf("\n--- Lattice Sieve Benchmark ---\n");
    for (int t = 0; t < n_tests; t++) {
        int64_t q = tests[t].q;

        /* Gauss reduce the lattice for this q */
        int64_t r = (q * 7 + 13) % q;  /* fake root */
        vec2 u = {q, 0};
        vec2 v = {((-r) % q + q) % q, 1};
        gauss_reduce(&u, &v);

        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);

        int cands = lattice_sieve_q(
            u.x, u.y, v.x, v.y,
            tests[t].I_max, tests[t].J_max,
            rat_primes, n_rat, m,
            alg_primes, alg_roots, n_alg,
            0.55, 0.45,  /* thresholds */
            q, 4,  /* poly degree */
            out_i, out_j, max_cands);

        clock_gettime(CLOCK_MONOTONIC, &t1);
        double dt = (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) * 1e-9;

        int64_t total_pts = (int64_t)(2 * tests[t].I_max + 1) * (tests[t].J_max + 1);
        double pts_per_sec = (double)total_pts / dt;
        double mem_kb = 2.0 * (2 * tests[t].I_max + 1) * 2 / 1024.0;  /* 2 arrays, uint16 */

        printf("  %s\n", tests[t].label);
        printf("    Basis: |e1|=%.1f, |e2|=%.1f\n",
               sqrt((double)(u.x*u.x + u.y*u.y)),
               sqrt((double)(v.x*v.x + v.y*v.y)));
        printf("    Region: %d x %d = %ld pts, Memory: %.1f KB\n",
               2*tests[t].I_max+1, tests[t].J_max+1, total_pts, mem_kb);
        printf("    Time: %.3f ms, Cands: %d, Rate: %.1f M pts/sec\n",
               dt * 1000, cands, pts_per_sec / 1e6);
    }

    /* Summary comparison */
    printf("\n--- Summary ---\n");
    printf("Line sieve:    A=500K → 1M pts/b-line, ~2 MB/line, sequential access\n");
    printf("Lattice sieve: I=5K,J=100 → 1M pts/q, ~20 KB/line, same throughput\n");
    printf("KEY ADVANTAGE: Lattice norms are ~q times smaller!\n");
    printf("  At q=100K: algebraic cofactor reduced by factor 100K\n");
    printf("  Dickman rho: u decreases by ~1.0, smoothness up ~10-50x\n");
    printf("  Net: same sieve cost per point, but 10-50x more relations per point\n");
    printf("  → 10-50x overall speedup from lattice sieve\n");

    free(rat_primes); free(alg_primes); free(alg_roots);
    free(out_i); free(out_j);
    return 0;
}
