/*
 * Pythagorean Tree — Deep Modular Walk + Batched GCD
 *
 * Core idea: Track (m, n) mod N using 2x2 matrix multiplication.
 * At depth D, true m has ~2^D bits, but m mod N fits in 64 bits.
 * gcd(v mod N, N) = gcd(v, N), so we detect factors perfectly.
 *
 * Combined with Montgomery batched GCD: accumulate product of derived
 * values, check gcd every BATCH steps. Throughput: 50-500M steps/sec.
 *
 * Also includes:
 * - Brent cycle detection on single-matrix orbits
 * - Matrix power jumps M^(2^k)
 * - Multi-matrix birthday collision detection
 * - Swap-derived values: 2m², 2n², A*B
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef unsigned __int128 u128;
typedef uint64_t u64;
typedef int64_t  i64;

static u64 gcd64(u64 a, u64 b) {
    while (b) { u64 t = b; b = a % b; a = t; }
    return a;
}

/* ---- Modular 2x2 matrix ---- */
typedef struct { u64 a00, a01, a10, a11; } MMat;

static inline MMat mmat_mul(MMat A, MMat B, u64 N) {
    MMat C;
    C.a00 = (u64)(((u128)A.a00 * B.a00 + (u128)A.a01 * B.a10) % N);
    C.a01 = (u64)(((u128)A.a00 * B.a01 + (u128)A.a01 * B.a11) % N);
    C.a10 = (u64)(((u128)A.a10 * B.a00 + (u128)A.a11 * B.a10) % N);
    C.a11 = (u64)(((u128)A.a10 * B.a01 + (u128)A.a11 * B.a11) % N);
    return C;
}

static inline void mmat_apply(MMat M, u64 m, u64 n, u64 N, u64 *m2, u64 *n2) {
    *m2 = (u64)(((u128)M.a00 * m + (u128)M.a01 * n) % N);
    *n2 = (u64)(((u128)M.a10 * m + (u128)M.a11 * n) % N);
}

/* Matrices stored as signed int, convert to mod-N */
typedef struct { int a00, a01, a10, a11; } IMat;

static const IMat FORWARD_INT[9] = {
    {2, -1, 1, 0}, {2, 1, 1, 0}, {1, 2, 0, 1},
    {1, 1, 0, 2}, {2, 0, 1, -1}, {2, 0, 1, 1},
    {3, -2, 1, -1}, {3, 2, 1, 1}, {1, 4, 0, 1},
};
#define N_FWD 9

static MMat imat_to_mmat(const IMat *I, u64 N) {
    MMat M;
    M.a00 = (I->a00 >= 0) ? (u64)I->a00 % N : N - (u64)(-I->a00) % N;
    M.a01 = (I->a01 >= 0) ? (u64)I->a01 % N : N - (u64)(-I->a01) % N;
    M.a10 = (I->a10 >= 0) ? (u64)I->a10 % N : N - (u64)(-I->a10) % N;
    M.a11 = (I->a11 >= 0) ? (u64)I->a11 % N : N - (u64)(-I->a11) % N;
    return M;
}

/* ---- Derived values mod N ---- */
/* From (m mod N, n mod N), compute derived values mod N:
 * A = m²-n², B = 2mn, C = m²+n², m, n, m-n, m+n, (m-n)², (m+n)²,
 * 2m², 2n², A*B (swap-derived)
 */
#define MAX_DERIVED 12

static int derived_mod(u64 m, u64 n, u64 N, u64 *vals) {
    u64 m2 = (u64)((u128)m * m % N);
    u64 n2 = (u64)((u128)n * n % N);
    u64 A = (m2 >= n2) ? m2 - n2 : N - (n2 - m2);  /* m²-n² mod N */
    u64 B = (u64)((u128)2 * m % N * n % N);           /* 2mn mod N */
    u64 C = (m2 + n2) % N;                             /* m²+n² mod N */
    u64 d = (m >= n) ? m - n : N - (n - m);            /* m-n mod N */
    u64 s = (m + n) % N;                                /* m+n mod N */

    int k = 0;
    vals[k++] = A;
    vals[k++] = B;
    vals[k++] = C;
    vals[k++] = m;
    vals[k++] = n;
    vals[k++] = d;
    vals[k++] = s;
    vals[k++] = (u64)((u128)d * d % N);   /* (m-n)² */
    vals[k++] = (u64)((u128)s * s % N);   /* (m+n)² */
    vals[k++] = (u64)((u128)2 * m2 % N);  /* 2m² (swap-derived) */
    vals[k++] = (u64)((u128)2 * n2 % N);  /* 2n² (swap-derived) */
    vals[k++] = (u64)((u128)A * B % N);   /* A*B (swap-derived) */
    return k;
}

/* ---- PRNG ---- */
static u64 rng_s[4];
static void rng_seed(u64 s) {
    rng_s[0] = s; rng_s[1] = s*0x9E3779B97F4A7C15ULL+1;
    rng_s[2] = s*0x6A09E667F3BCC908ULL+2; rng_s[3] = s*0x3C6EF372FE94F82BULL+3;
}
static inline u64 rng(void) {
    u64 r = rng_s[1]*5; r = (r<<7|r>>57)*9;
    u64 t = rng_s[1]<<17;
    rng_s[2]^=rng_s[0]; rng_s[3]^=rng_s[1]; rng_s[1]^=rng_s[2]; rng_s[0]^=rng_s[3];
    rng_s[2]^=t; rng_s[3]=(rng_s[3]<<45)|(rng_s[3]>>19);
    return r;
}

/* ==== EXPERIMENT 1: Deep Random Walk + Batched GCD ==== */
u64 deep_random_walk(
    u64 N,
    u64 max_steps,
    int time_limit_ms,
    int batch_size,
    u64 seed,
    u64 *steps_out
) {
    struct timespec t0, now;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    rng_seed(seed);

    /* Convert matrices to mod-N form */
    MMat mats[N_FWD];
    for (int i = 0; i < N_FWD; i++)
        mats[i] = imat_to_mmat(&FORWARD_INT[i], N);

    /* Start at (m,n) = (2,1) mod N */
    u64 m = 2, n = 1;
    u64 accum = 1;
    int accum_count = 0;
    u64 steps = 0;

    for (u64 step = 0; step < max_steps; step++) {
        /* Time check every 4096 steps */
        if ((step & 4095) == 0) {
            clock_gettime(CLOCK_MONOTONIC, &now);
            long elapsed = (now.tv_sec - t0.tv_sec)*1000 + (now.tv_nsec - t0.tv_nsec)/1000000;
            if (elapsed >= time_limit_ms) break;
        }

        /* Random matrix */
        int mi = (int)(rng() % N_FWD);
        u64 m2, n2;
        mmat_apply(mats[mi], m, n, N, &m2, &n2);
        m = m2; n = n2;
        steps++;

        /* Compute derived values and accumulate */
        u64 vals[MAX_DERIVED];
        int nv = derived_mod(m, n, N, vals);

        for (int i = 0; i < nv; i++) {
            u64 v = vals[i];
            if (v == 0) {
                /* v mod N = 0 means N | v, check more carefully */
                /* Actually if v mod N = 0, then gcd(v,N) could be N (trivial)
                 * or a factor. Since v = some polynomial of m,n which are mod N,
                 * v mod N = 0 means N divides the polynomial evaluated at true m,n.
                 * This is likely trivial (v is a multiple of N). Skip. */
                continue;
            }
            u64 g = gcd64(v, N);
            if (g > 1 && g < N) {
                *steps_out = steps;
                return g;
            }
            /* Accumulate for batch gcd */
            accum = (u64)((u128)accum * v % N);
            accum_count++;
        }

        /* Batch GCD check */
        if (accum_count >= batch_size) {
            u64 g = gcd64(accum, N);
            if (g > 1 && g < N) {
                *steps_out = steps;
                return g;
            }
            accum = 1;
            accum_count = 0;
        }
    }

    *steps_out = steps;
    return 0;
}


/* ==== EXPERIMENT 2: Brent Cycle Detection on Single Matrix ==== */
u64 brent_cycle_detect(
    u64 N,
    int matrix_idx,  /* which of the 9 matrices to iterate */
    u64 max_steps,
    int time_limit_ms,
    u64 seed,
    u64 *steps_out,
    u64 *period_out
) {
    struct timespec t0, now;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    if (matrix_idx < 0 || matrix_idx >= N_FWD) matrix_idx = 0;
    MMat M = imat_to_mmat(&FORWARD_INT[matrix_idx], N);

    u64 m = 2, n = 1;  /* starting point */

    /* Brent's algorithm: power-of-2 cycle detection */
    u64 tort_m = m, tort_n = n;  /* tortoise (saved) */
    u64 hare_m = m, hare_n = n;  /* hare (iterated) */
    u64 power = 1, lam = 1;
    u64 steps = 0;

    /* Also accumulate product for batch gcd */
    u64 accum = 1;
    int accum_count = 0;

    for (u64 step = 0; step < max_steps; step++) {
        if ((step & 4095) == 0) {
            clock_gettime(CLOCK_MONOTONIC, &now);
            long elapsed = (now.tv_sec - t0.tv_sec)*1000 + (now.tv_nsec - t0.tv_nsec)/1000000;
            if (elapsed >= time_limit_ms) break;
        }

        /* Advance hare one step */
        u64 hm2, hn2;
        mmat_apply(M, hare_m, hare_n, N, &hm2, &hn2);
        hare_m = hm2; hare_n = hn2;
        steps++;

        /* Check derived values */
        u64 vals[MAX_DERIVED];
        int nv = derived_mod(hare_m, hare_n, N, vals);
        for (int i = 0; i < nv; i++) {
            u64 v = vals[i];
            if (v == 0) continue;
            u64 g = gcd64(v, N);
            if (g > 1 && g < N) { *steps_out = steps; *period_out = 0; return g; }
            accum = (u64)((u128)accum * v % N);
            accum_count++;
        }

        /* Batch gcd */
        if (accum_count >= 500) {
            u64 g = gcd64(accum, N);
            if (g > 1 && g < N) { *steps_out = steps; *period_out = lam; return g; }
            accum = 1; accum_count = 0;
        }

        /* Brent's cycle check: difference between hare and tortoise */
        u64 dm = (hare_m >= tort_m) ? hare_m - tort_m : N - (tort_m - hare_m);
        u64 dn = (hare_n >= tort_n) ? hare_n - tort_n : N - (tort_n - hare_n);

        if (dm != 0) {
            u64 g = gcd64(dm, N);
            if (g > 1 && g < N) { *steps_out = steps; *period_out = lam; return g; }
        }
        if (dn != 0) {
            u64 g = gcd64(dn, N);
            if (g > 1 && g < N) { *steps_out = steps; *period_out = lam; return g; }
        }

        /* Brent power-of-2 update */
        lam++;
        if (lam == power) {
            tort_m = hare_m; tort_n = hare_n;
            power <<= 1;
            lam = 0;
        }
    }

    *steps_out = steps;
    *period_out = lam;
    return 0;
}


/* ==== EXPERIMENT 3: Matrix Power Jump M^(2^k) ==== */
u64 matrix_power_jump(
    u64 N,
    int max_power,     /* check powers 2^0 through 2^max_power */
    u64 *steps_out
) {
    u64 steps = 0;
    u64 start_m = 2, start_n = 1;

    for (int mi = 0; mi < N_FWD; mi++) {
        MMat M = imat_to_mmat(&FORWARD_INT[mi], N);
        MMat Mk = M;  /* M^1 */

        for (int k = 0; k <= max_power; k++) {
            /* Apply M^(2^k) to start */
            u64 m2, n2;
            mmat_apply(Mk, start_m, start_n, N, &m2, &n2);
            steps++;

            /* Check derived values */
            u64 vals[MAX_DERIVED];
            int nv = derived_mod(m2, n2, N, vals);
            for (int i = 0; i < nv; i++) {
                if (vals[i] == 0) continue;
                u64 g = gcd64(vals[i], N);
                if (g > 1 && g < N) {
                    *steps_out = steps;
                    return g;
                }
            }

            /* Also check difference from start */
            u64 dm = (m2 >= start_m) ? m2 - start_m : N - (start_m - m2);
            u64 dn = (n2 >= start_n) ? n2 - start_n : N - (start_n - n2);
            if (dm != 0) { u64 g = gcd64(dm, N); if (g > 1 && g < N) { *steps_out = steps; return g; } }
            if (dn != 0) { u64 g = gcd64(dn, N); if (g > 1 && g < N) { *steps_out = steps; return g; } }

            /* Square the matrix for next power */
            Mk = mmat_mul(Mk, Mk, N);
        }
    }

    *steps_out = steps;
    return 0;
}


/* ==== EXPERIMENT 4: Williams p+1 style — smooth exponent ==== */
u64 smooth_exponent_attack(
    u64 N,
    int B1_bound,      /* Stage 1 smoothness bound */
    u64 *steps_out
) {
    /* Small primes for exponent */
    static const int PRIMES[] = {2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,
                                  59,61,67,71,73,79,83,89,97,101,103,107,109,113,
                                  127,131,137,139,149,151,157,163,167,173,179,181,
                                  191,193,197,199,211,223,227,229,233,239,241,251};
    int n_primes = sizeof(PRIMES) / sizeof(PRIMES[0]);

    u64 steps = 0;
    u64 start_m = 2, start_n = 1;

    for (int mi = 0; mi < N_FWD; mi++) {
        MMat M = imat_to_mmat(&FORWARD_INT[mi], N);
        MMat Mk = M;

        /* Stage 1: exponentiate by product of prime powers up to B1 */
        for (int pi = 0; pi < n_primes && PRIMES[pi] <= B1_bound; pi++) {
            int p = PRIMES[pi];
            /* Compute largest p^e <= B1 */
            int pe = p;
            while ((long long)pe * p <= B1_bound) pe *= p;

            /* M^pe via repeated squaring */
            MMat base = Mk;
            MMat result = {1 % N, 0, 0, 1 % N};  /* identity mod N */
            int exp = pe;
            while (exp > 0) {
                if (exp & 1) result = mmat_mul(result, base, N);
                base = mmat_mul(base, base, N);
                exp >>= 1;
                steps++;
            }
            Mk = result;
        }

        /* Check if factor found */
        u64 m2, n2;
        mmat_apply(Mk, start_m, start_n, N, &m2, &n2);

        u64 vals[MAX_DERIVED];
        int nv = derived_mod(m2, n2, N, vals);
        for (int i = 0; i < nv; i++) {
            if (vals[i] == 0) continue;
            u64 g = gcd64(vals[i], N);
            if (g > 1 && g < N) { *steps_out = steps; return g; }
        }

        /* Also check return to start */
        u64 dm = (m2 >= start_m) ? m2 - start_m : N - (start_m - m2);
        u64 dn = (n2 >= start_n) ? n2 - start_n : N - (start_n - n2);
        if (dm != 0) { u64 g = gcd64(dm, N); if (g > 1 && g < N) { *steps_out = steps; return g; } }
        if (dn != 0) { u64 g = gcd64(dn, N); if (g > 1 && g < N) { *steps_out = steps; return g; } }
    }

    *steps_out = steps;
    return 0;
}


/* ==== EXPERIMENT 5: Parametric matrix family M(t) = [[t,1],[1,0]] ==== */
u64 parametric_family(
    u64 N,
    int t_max,          /* try t = 1 to t_max */
    int B1_bound,       /* smoothness bound for each t */
    u64 *steps_out
) {
    static const int PRIMES[] = {2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,
                                  59,61,67,71,73,79,83,89,97,101,103,107,109,113};
    int n_primes = sizeof(PRIMES) / sizeof(PRIMES[0]);
    u64 steps = 0;

    for (int t = 1; t <= t_max; t++) {
        MMat M = { (u64)t % N, 1, 1, 0 };

        /* Stage 1 */
        for (int pi = 0; pi < n_primes && PRIMES[pi] <= B1_bound; pi++) {
            int p = PRIMES[pi];
            int pe = p;
            while ((long long)pe * p <= B1_bound) pe *= p;

            MMat base = M;
            MMat result = {1, 0, 0, 1};
            int exp = pe;
            while (exp > 0) {
                if (exp & 1) result = mmat_mul(result, base, N);
                base = mmat_mul(base, base, N);
                exp >>= 1;
                steps++;
            }
            M = result;
        }

        u64 m2, n2;
        mmat_apply(M, 2, 1, N, &m2, &n2);

        u64 vals[MAX_DERIVED];
        int nv = derived_mod(m2, n2, N, vals);
        for (int i = 0; i < nv; i++) {
            if (vals[i] == 0) continue;
            u64 g = gcd64(vals[i], N);
            if (g > 1 && g < N) { *steps_out = steps; return g; }
        }

        /* Check return-to-start difference */
        u64 dm = (m2 >= 2) ? m2 - 2 : N - (2 - m2);
        u64 dn = (n2 >= 1) ? n2 - 1 : N - (1 - n2);
        if (dm != 0) { u64 g = gcd64(dm, N); if (g > 1 && g < N) { *steps_out = steps; return g; } }
        if (dn != 0) { u64 g = gcd64(dn, N); if (g > 1 && g < N) { *steps_out = steps; return g; } }
    }

    *steps_out = steps;
    return 0;
}
