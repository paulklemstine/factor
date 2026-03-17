/*
 * Pythagorean Tree — Hybrid Factoring Approaches
 *
 * Three combined strategies:
 * 1. Smooth exponent (Williams p+1 style) + ECM Stage 2
 * 2. Multi-curve smooth exponent with random matrices + batch GCD
 * 3. Smooth exponent warm-start + random walk continuation
 *
 * All operate on 2x2 matrices mod N tracking (m,n) generators.
 * Derived values: A=m^2-n^2, B=2mn, C=m^2+n^2, m, n, m-n, m+n, etc.
 * Factor detected when gcd(derived_value, N) is nontrivial.
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef unsigned __int128 u128;
typedef uint64_t u64;
typedef int64_t  i64;

/* ---- GCD ---- */
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

static inline MMat mmat_identity(u64 N) {
    MMat I = {1 % N, 0, 0, 1 % N};
    return I;
}

static inline void mmat_apply(MMat M, u64 m, u64 n, u64 N, u64 *m2, u64 *n2) {
    *m2 = (u64)(((u128)M.a00 * m + (u128)M.a01 * n) % N);
    *n2 = (u64)(((u128)M.a10 * m + (u128)M.a11 * n) % N);
}

/* Matrix exponentiation by repeated squaring: M^exp mod N */
static MMat mmat_pow(MMat M, u64 exp, u64 N) {
    MMat result = mmat_identity(N);
    MMat base = M;
    while (exp > 0) {
        if (exp & 1) result = mmat_mul(result, base, N);
        base = mmat_mul(base, base, N);
        exp >>= 1;
    }
    return result;
}

/* ---- 9 forward matrices (signed int form) ---- */
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
#define MAX_DERIVED 12

static int derived_mod(u64 m, u64 n, u64 N, u64 *vals) {
    u64 m2 = (u64)((u128)m * m % N);
    u64 n2 = (u64)((u128)n * n % N);
    u64 A = (m2 >= n2) ? m2 - n2 : N - (n2 - m2);
    u64 B = (u64)((u128)2 * m % N * n % N);
    u64 C = (m2 + n2) % N;
    u64 d = (m >= n) ? m - n : N - (n - m);
    u64 s = (m + n) % N;

    int k = 0;
    vals[k++] = A;
    vals[k++] = B;
    vals[k++] = C;
    vals[k++] = m;
    vals[k++] = n;
    vals[k++] = d;
    vals[k++] = s;
    vals[k++] = (u64)((u128)d * d % N);
    vals[k++] = (u64)((u128)s * s % N);
    vals[k++] = (u64)((u128)2 * m2 % N);
    vals[k++] = (u64)((u128)2 * n2 % N);
    vals[k++] = (u64)((u128)A * B % N);
    return k;
}

/* ---- PRNG (xoshiro256**) ---- */
static u64 rng_s[4];

static void rng_seed(u64 s) {
    rng_s[0] = s;
    rng_s[1] = s * 0x9E3779B97F4A7C15ULL + 1;
    rng_s[2] = s * 0x6A09E667F3BCC908ULL + 2;
    rng_s[3] = s * 0x3C6EF372FE94F82BULL + 3;
}

static inline u64 rng(void) {
    u64 r = rng_s[1] * 5;
    r = (r << 7 | r >> 57) * 9;
    u64 t = rng_s[1] << 17;
    rng_s[2] ^= rng_s[0];
    rng_s[3] ^= rng_s[1];
    rng_s[1] ^= rng_s[2];
    rng_s[0] ^= rng_s[3];
    rng_s[2] ^= t;
    rng_s[3] = (rng_s[3] << 45) | (rng_s[3] >> 19);
    return r;
}

/* ---- Prime sieve for smooth exponent ---- */
/* Sieve primes up to B using simple trial division.
 * Returns count of primes stored in out[]. */
static int sieve_primes(int B, int *out, int max_out) {
    if (B < 2) return 0;
    /* Simple sieve of Eratosthenes */
    int sz = B + 1;
    char *is_prime = (char *)calloc(sz, 1);
    if (!is_prime) return 0;
    memset(is_prime, 1, sz);
    is_prime[0] = is_prime[1] = 0;
    for (int i = 2; (long long)i * i <= B; i++) {
        if (is_prime[i]) {
            for (int j = i * i; j <= B; j += i)
                is_prime[j] = 0;
        }
    }
    int cnt = 0;
    for (int i = 2; i <= B && cnt < max_out; i++) {
        if (is_prime[i]) out[cnt++] = i;
    }
    free(is_prime);
    return cnt;
}

/* ---- Stage 1: Raise matrix M to smooth exponent E = prod(p^k for p<=B1) ---- */
/* Returns the resulting matrix M^E mod N. steps_out accumulates step count. */
static MMat smooth_stage1(MMat M, u64 N, int B1, const int *primes, int nprimes, u64 *steps) {
    MMat Mk = M;
    for (int pi = 0; pi < nprimes && primes[pi] <= B1; pi++) {
        int p = primes[pi];
        /* Compute p^e where p^e <= B1 */
        long long pe = p;
        while (pe * p <= (long long)B1) pe *= p;

        /* Mk = Mk ^ pe via repeated squaring */
        MMat base = Mk;
        MMat result = mmat_identity(N);
        long long exp = pe;
        while (exp > 0) {
            if (exp & 1) result = mmat_mul(result, base, N);
            base = mmat_mul(base, base, N);
            exp >>= 1;
            (*steps)++;
        }
        Mk = result;
    }
    return Mk;
}

/* ---- Check derived values for factor, return factor or 0 ---- */
static u64 check_derived(u64 m, u64 n, u64 N) {
    u64 vals[MAX_DERIVED];
    int nv = derived_mod(m, n, N, vals);
    for (int i = 0; i < nv; i++) {
        if (vals[i] == 0 || vals[i] == N) continue;
        u64 g = gcd64(vals[i], N);
        if (g > 1 && g < N) return g;
    }
    return 0;
}

/* ---- Accumulate derived values into batch product ---- */
/* Returns factor if batch GCD finds one, otherwise 0.
 * accum and accum_count are updated in place. */
static u64 accum_derived(u64 m, u64 n, u64 N, u64 *accum, int *accum_count, int batch_size) {
    u64 vals[MAX_DERIVED];
    int nv = derived_mod(m, n, N, vals);
    for (int i = 0; i < nv; i++) {
        u64 v = vals[i];
        if (v == 0 || v == N) continue;
        *accum = (u64)((u128)(*accum) * v % N);
        (*accum_count)++;
    }
    if (*accum_count >= batch_size) {
        u64 g = gcd64(*accum, N);
        if (g > 1 && g < N) return g;
        *accum = 1;
        *accum_count = 0;
    }
    return 0;
}


/* ================================================================
 * APPROACH 1: Smooth Exponent + ECM-style Stage 2
 *
 * Stage 1: M^E where E = prod(p^k, p<=B1) — catches smooth-period orbits.
 * Stage 2: For each prime q in (B1, B2], compute M^(E*q) and check.
 *          This catches periods with one large prime factor q.
 *
 * Tries all 9 base matrices + parametric M(t) for t=1..t_max.
 * ================================================================ */
u64 smooth_stage2(
    u64 N,
    int B1,
    int B2,
    int t_max,        /* parametric family size, e.g. 100 */
    u64 *steps_out
) {
    u64 steps = 0;
    u64 start_m = 2, start_n = 1;

    /* Sieve all primes up to B2 */
    int max_primes = B2 + 100;
    int *primes = (int *)malloc(max_primes * sizeof(int));
    if (!primes) { *steps_out = 0; return 0; }
    int nprimes = sieve_primes(B2, primes, max_primes);

    /* Find index where primes cross B1 (for Stage 2 start) */
    int stage2_start = 0;
    for (int i = 0; i < nprimes; i++) {
        if (primes[i] > B1) { stage2_start = i; break; }
    }

    /* Batch GCD accumulator across ALL matrices */
    u64 accum = 1;
    int accum_count = 0;
    #define BATCH_SZ 256

    /* --- Try the 9 fixed Pythagorean tree matrices --- */
    for (int mi = 0; mi < N_FWD; mi++) {
        MMat M = imat_to_mmat(&FORWARD_INT[mi], N);

        /* Stage 1 */
        MMat Mk = smooth_stage1(M, N, B1, primes, nprimes, &steps);

        /* Check Stage 1 result */
        u64 m2, n2;
        mmat_apply(Mk, start_m, start_n, N, &m2, &n2);
        u64 f = check_derived(m2, n2, N);
        if (f) { free(primes); *steps_out = steps; return f; }

        /* Accumulate into batch */
        f = accum_derived(m2, n2, N, &accum, &accum_count, BATCH_SZ);
        if (f) { free(primes); *steps_out = steps; return f; }

        /* Stage 2: for each prime q in (B1, B2], check M^(E*q) */
        for (int qi = stage2_start; qi < nprimes; qi++) {
            /* M^(E*q) = (M^E)^q */
            MMat Mq = mmat_pow(Mk, (u64)primes[qi], N);
            steps += 16; /* ~log2(q) squarings */

            u64 qm, qn;
            mmat_apply(Mq, start_m, start_n, N, &qm, &qn);

            f = check_derived(qm, qn, N);
            if (f) { free(primes); *steps_out = steps; return f; }

            f = accum_derived(qm, qn, N, &accum, &accum_count, BATCH_SZ);
            if (f) { free(primes); *steps_out = steps; return f; }
        }
    }

    /* --- Parametric family M(t) = [[t,1],[1,0]] for t=1..t_max --- */
    for (int t = 1; t <= t_max; t++) {
        MMat M = { (u64)t % N, 1, 1, 0 };

        /* Stage 1 */
        MMat Mk = smooth_stage1(M, N, B1, primes, nprimes, &steps);

        /* Check Stage 1 result */
        u64 m2, n2;
        mmat_apply(Mk, start_m, start_n, N, &m2, &n2);
        u64 f = check_derived(m2, n2, N);
        if (f) { free(primes); *steps_out = steps; return f; }

        f = accum_derived(m2, n2, N, &accum, &accum_count, BATCH_SZ);
        if (f) { free(primes); *steps_out = steps; return f; }

        /* Stage 2 */
        for (int qi = stage2_start; qi < nprimes; qi++) {
            MMat Mq = mmat_pow(Mk, (u64)primes[qi], N);
            steps += 16;

            u64 qm, qn;
            mmat_apply(Mq, start_m, start_n, N, &qm, &qn);

            f = check_derived(qm, qn, N);
            if (f) { free(primes); *steps_out = steps; return f; }

            f = accum_derived(qm, qn, N, &accum, &accum_count, BATCH_SZ);
            if (f) { free(primes); *steps_out = steps; return f; }
        }
    }

    /* Final batch GCD flush */
    if (accum_count > 0) {
        u64 g = gcd64(accum, N);
        if (g > 1 && g < N) { free(primes); *steps_out = steps; return g; }
    }

    free(primes);
    *steps_out = steps;
    return 0;
}


/* ================================================================
 * APPROACH 2: Multi-Curve Smooth Exponent
 *
 * Generate num_curves random 2x2 matrices with entries in [1, N).
 * Run smooth exponent Stage 1 on each.
 * Accumulate all derived values into one batch GCD product.
 *
 * More "curves" = higher probability that one has smooth period mod p.
 * Analogous to ECM running many curves.
 * ================================================================ */
u64 multi_curve_smooth(
    u64 N,
    int num_curves,
    int B1,
    u64 seed,
    u64 *steps_out
) {
    u64 steps = 0;
    u64 start_m = 2, start_n = 1;
    rng_seed(seed);

    /* Sieve primes up to B1 */
    int max_primes = B1 + 100;
    int *primes = (int *)malloc(max_primes * sizeof(int));
    if (!primes) { *steps_out = 0; return 0; }
    int nprimes = sieve_primes(B1, primes, max_primes);

    /* Batch GCD accumulator */
    u64 accum = 1;
    int accum_count = 0;

    /* First do the 9 fixed matrices (free — always good to include) */
    for (int mi = 0; mi < N_FWD; mi++) {
        MMat M = imat_to_mmat(&FORWARD_INT[mi], N);
        MMat Mk = smooth_stage1(M, N, B1, primes, nprimes, &steps);

        u64 m2, n2;
        mmat_apply(Mk, start_m, start_n, N, &m2, &n2);

        u64 f = check_derived(m2, n2, N);
        if (f) { free(primes); *steps_out = steps; return f; }

        f = accum_derived(m2, n2, N, &accum, &accum_count, BATCH_SZ);
        if (f) { free(primes); *steps_out = steps; return f; }
    }

    /* Now generate random curves */
    for (int ci = 0; ci < num_curves; ci++) {
        /* Random 2x2 matrix with entries in [1, N) */
        MMat M;
        M.a00 = rng() % N; if (M.a00 == 0) M.a00 = 1;
        M.a01 = rng() % N; if (M.a01 == 0) M.a01 = 1;
        M.a10 = rng() % N; if (M.a10 == 0) M.a10 = 1;
        M.a11 = rng() % N; if (M.a11 == 0) M.a11 = 1;

        /* Stage 1 */
        MMat Mk = smooth_stage1(M, N, B1, primes, nprimes, &steps);

        /* Check with multiple starting vectors for diversity */
        /* Start 1: (2, 1) */
        u64 m2, n2;
        mmat_apply(Mk, start_m, start_n, N, &m2, &n2);
        u64 f = check_derived(m2, n2, N);
        if (f) { free(primes); *steps_out = steps; return f; }
        f = accum_derived(m2, n2, N, &accum, &accum_count, BATCH_SZ);
        if (f) { free(primes); *steps_out = steps; return f; }

        /* Start 2: (1, 0) — extracts first column */
        mmat_apply(Mk, 1, 0, N, &m2, &n2);
        f = check_derived(m2, n2, N);
        if (f) { free(primes); *steps_out = steps; return f; }
        f = accum_derived(m2, n2, N, &accum, &accum_count, BATCH_SZ);
        if (f) { free(primes); *steps_out = steps; return f; }

        /* Start 3: (0, 1) — extracts second column */
        mmat_apply(Mk, 0, 1, N, &m2, &n2);
        f = check_derived(m2, n2, N);
        if (f) { free(primes); *steps_out = steps; return f; }
        f = accum_derived(m2, n2, N, &accum, &accum_count, BATCH_SZ);
        if (f) { free(primes); *steps_out = steps; return f; }

        /* Also check matrix entries directly */
        u64 g = gcd64(Mk.a00, N);
        if (g > 1 && g < N) { free(primes); *steps_out = steps; return g; }
        g = gcd64(Mk.a01, N);
        if (g > 1 && g < N) { free(primes); *steps_out = steps; return g; }
        g = gcd64(Mk.a10, N);
        if (g > 1 && g < N) { free(primes); *steps_out = steps; return g; }
        g = gcd64(Mk.a11, N);
        if (g > 1 && g < N) { free(primes); *steps_out = steps; return g; }

        /* Check (entry - identity) for detecting period = E */
        u64 d00 = (Mk.a00 >= 1) ? Mk.a00 - 1 : N - 1 + Mk.a00;
        u64 d11 = (Mk.a11 >= 1) ? Mk.a11 - 1 : N - 1 + Mk.a11;
        if (d00 > 0 && d00 < N) {
            g = gcd64(d00, N);
            if (g > 1 && g < N) { free(primes); *steps_out = steps; return g; }
        }
        if (d11 > 0 && d11 < N) {
            g = gcd64(d11, N);
            if (g > 1 && g < N) { free(primes); *steps_out = steps; return g; }
        }
        if (Mk.a01 > 0 && Mk.a01 < N) {
            g = gcd64(Mk.a01, N);
            if (g > 1 && g < N) { free(primes); *steps_out = steps; return g; }
        }
        if (Mk.a10 > 0 && Mk.a10 < N) {
            g = gcd64(Mk.a10, N);
            if (g > 1 && g < N) { free(primes); *steps_out = steps; return g; }
        }

        /* Accumulate matrix entries into batch product */
        if (d00 > 0) accum = (u64)((u128)accum * d00 % N), accum_count++;
        if (d11 > 0) accum = (u64)((u128)accum * d11 % N), accum_count++;
        if (Mk.a01 > 0) accum = (u64)((u128)accum * Mk.a01 % N), accum_count++;
        if (Mk.a10 > 0) accum = (u64)((u128)accum * Mk.a10 % N), accum_count++;
        if (accum_count >= BATCH_SZ) {
            g = gcd64(accum, N);
            if (g > 1 && g < N) { free(primes); *steps_out = steps; return g; }
            accum = 1; accum_count = 0;
        }
    }

    /* Final flush */
    if (accum_count > 0) {
        u64 g = gcd64(accum, N);
        if (g > 1 && g < N) { free(primes); *steps_out = steps; return g; }
    }

    free(primes);
    *steps_out = steps;
    return 0;
}


/* ================================================================
 * APPROACH 3: Smooth Exponent Warm-Start + Random Walk
 *
 * For each starting matrix:
 *   1. Stage 1: smooth exponent up to B1 (advances orbit position)
 *   2. Random walk from resulting (m,n) state for walk_steps
 *   3. Batch GCD on accumulated derived values
 *
 * The smooth exponent "teleports" the walk to a position deep in
 * the orbit, then random walk explores locally. This combines the
 * algebraic structure of smooth exponent with brute-force coverage.
 * ================================================================ */
u64 smooth_then_walk(
    u64 N,
    int B1,
    u64 walk_steps,
    int num_starts,
    u64 seed,
    u64 *steps_out
) {
    u64 steps = 0;
    rng_seed(seed);

    /* Sieve primes up to B1 */
    int max_primes = B1 + 100;
    int *primes = (int *)malloc(max_primes * sizeof(int));
    if (!primes) { *steps_out = 0; return 0; }
    int nprimes = sieve_primes(B1, primes, max_primes);

    /* Convert forward matrices to mod-N form */
    MMat fwd_mats[N_FWD];
    for (int i = 0; i < N_FWD; i++)
        fwd_mats[i] = imat_to_mmat(&FORWARD_INT[i], N);

    /* Batch GCD accumulator */
    u64 accum = 1;
    int accum_count = 0;

    for (int si = 0; si < num_starts; si++) {
        MMat M;

        if (si < N_FWD) {
            /* First 9 starts: use the fixed forward matrices */
            M = fwd_mats[si];
        } else if (si < N_FWD + 100) {
            /* Next 100: parametric family M(t) = [[t,1],[1,0]] */
            int t = si - N_FWD + 1;
            M.a00 = (u64)t % N;
            M.a01 = 1;
            M.a10 = 1;
            M.a11 = 0;
        } else {
            /* Rest: random matrices */
            M.a00 = rng() % N; if (M.a00 == 0) M.a00 = 1;
            M.a01 = rng() % N; if (M.a01 == 0) M.a01 = 1;
            M.a10 = rng() % N; if (M.a10 == 0) M.a10 = 1;
            M.a11 = rng() % N; if (M.a11 == 0) M.a11 = 1;
        }

        /* Stage 1: smooth exponent */
        MMat Mk = smooth_stage1(M, N, B1, primes, nprimes, &steps);

        /* Get warm-start position */
        u64 m = 2, n = 1;
        u64 m2, n2;
        mmat_apply(Mk, m, n, N, &m2, &n2);
        m = m2; n = n2;

        /* Check warm-start position */
        u64 f = check_derived(m, n, N);
        if (f) { free(primes); *steps_out = steps; return f; }
        f = accum_derived(m, n, N, &accum, &accum_count, BATCH_SZ);
        if (f) { free(primes); *steps_out = steps; return f; }

        /* Random walk from warm-start position */
        for (u64 w = 0; w < walk_steps; w++) {
            int mi = (int)(rng() % N_FWD);
            mmat_apply(fwd_mats[mi], m, n, N, &m2, &n2);
            m = m2; n = n2;
            steps++;

            f = check_derived(m, n, N);
            if (f) { free(primes); *steps_out = steps; return f; }

            f = accum_derived(m, n, N, &accum, &accum_count, BATCH_SZ);
            if (f) { free(primes); *steps_out = steps; return f; }
        }
    }

    /* Final flush */
    if (accum_count > 0) {
        u64 g = gcd64(accum, N);
        if (g > 1 && g < N) { free(primes); *steps_out = steps; return g; }
    }

    free(primes);
    *steps_out = steps;
    return 0;
}


/* ================================================================
 * APPROACH 4 (bonus): Combined All-In-One
 *
 * Runs Stage 1 + Stage 2 + walk continuation on a wide set of
 * matrices, with a shared batch accumulator. Maximum coverage.
 * ================================================================ */
u64 combined_attack(
    u64 N,
    int B1,
    int B2,
    int num_random_curves,
    u64 walk_steps_per_curve,
    u64 seed,
    u64 *steps_out
) {
    u64 steps = 0;
    rng_seed(seed);

    /* Sieve primes up to B2 */
    int max_primes = B2 + 100;
    int *primes = (int *)malloc(max_primes * sizeof(int));
    if (!primes) { *steps_out = 0; return 0; }
    int nprimes = sieve_primes(B2, primes, max_primes);

    int stage2_start = 0;
    for (int i = 0; i < nprimes; i++) {
        if (primes[i] > B1) { stage2_start = i; break; }
    }

    /* Convert forward matrices to mod-N form */
    MMat fwd_mats[N_FWD];
    for (int i = 0; i < N_FWD; i++)
        fwd_mats[i] = imat_to_mmat(&FORWARD_INT[i], N);

    /* Shared batch accumulator */
    u64 accum = 1;
    int accum_count = 0;
    u64 start_m = 2, start_n = 1;

    /* Total curves = 9 fixed + parametric + random */
    int total_curves = N_FWD + 200 + num_random_curves;

    for (int ci = 0; ci < total_curves; ci++) {
        MMat M;
        if (ci < N_FWD) {
            M = fwd_mats[ci];
        } else if (ci < N_FWD + 200) {
            int t = ci - N_FWD + 1;
            M.a00 = (u64)t % N; M.a01 = 1; M.a10 = 1; M.a11 = 0;
        } else {
            M.a00 = rng() % N; if (M.a00 == 0) M.a00 = 1;
            M.a01 = rng() % N; if (M.a01 == 0) M.a01 = 1;
            M.a10 = rng() % N; if (M.a10 == 0) M.a10 = 1;
            M.a11 = rng() % N; if (M.a11 == 0) M.a11 = 1;
        }

        /* Stage 1 */
        MMat Mk = smooth_stage1(M, N, B1, primes, nprimes, &steps);

        u64 m2, n2;
        mmat_apply(Mk, start_m, start_n, N, &m2, &n2);

        u64 f = check_derived(m2, n2, N);
        if (f) { free(primes); *steps_out = steps; return f; }
        f = accum_derived(m2, n2, N, &accum, &accum_count, BATCH_SZ);
        if (f) { free(primes); *steps_out = steps; return f; }

        /* Also check M^E - I for period detection */
        u64 d00 = (Mk.a00 >= 1) ? Mk.a00 - 1 : N - 1 + Mk.a00;
        u64 d11 = (Mk.a11 >= 1) ? Mk.a11 - 1 : N - 1 + Mk.a11;
        if (d00 > 0 && d00 < N) {
            u64 g = gcd64(d00, N);
            if (g > 1 && g < N) { free(primes); *steps_out = steps; return g; }
            accum = (u64)((u128)accum * d00 % N); accum_count++;
        }
        if (d11 > 0 && d11 < N) {
            u64 g = gcd64(d11, N);
            if (g > 1 && g < N) { free(primes); *steps_out = steps; return g; }
            accum = (u64)((u128)accum * d11 % N); accum_count++;
        }
        if (Mk.a01 > 0 && Mk.a01 < N) {
            accum = (u64)((u128)accum * Mk.a01 % N); accum_count++;
        }
        if (Mk.a10 > 0 && Mk.a10 < N) {
            accum = (u64)((u128)accum * Mk.a10 % N); accum_count++;
        }
        if (accum_count >= BATCH_SZ) {
            u64 g = gcd64(accum, N);
            if (g > 1 && g < N) { free(primes); *steps_out = steps; return g; }
            accum = 1; accum_count = 0;
        }

        /* Stage 2: primes in (B1, B2] */
        for (int qi = stage2_start; qi < nprimes; qi++) {
            MMat Mq = mmat_pow(Mk, (u64)primes[qi], N);
            steps += 16;

            u64 qm, qn;
            mmat_apply(Mq, start_m, start_n, N, &qm, &qn);

            f = check_derived(qm, qn, N);
            if (f) { free(primes); *steps_out = steps; return f; }
            f = accum_derived(qm, qn, N, &accum, &accum_count, BATCH_SZ);
            if (f) { free(primes); *steps_out = steps; return f; }
        }

        /* Walk continuation from Stage 1 end-state */
        u64 wm = m2, wn = n2;
        for (u64 w = 0; w < walk_steps_per_curve; w++) {
            int mi = (int)(rng() % N_FWD);
            u64 wm2, wn2;
            mmat_apply(fwd_mats[mi], wm, wn, N, &wm2, &wn2);
            wm = wm2; wn = wn2;
            steps++;

            f = check_derived(wm, wn, N);
            if (f) { free(primes); *steps_out = steps; return f; }
            f = accum_derived(wm, wn, N, &accum, &accum_count, BATCH_SZ);
            if (f) { free(primes); *steps_out = steps; return f; }
        }
    }

    /* Final flush */
    if (accum_count > 0) {
        u64 g = gcd64(accum, N);
        if (g > 1 && g < N) { free(primes); *steps_out = steps; return g; }
    }

    free(primes);
    *steps_out = steps;
    return 0;
}


/* ================================================================
 * APPROACH 5: Time-Limited Combined Attack
 *
 * Like combined_attack but with a wall-clock time limit.
 * Phases run in priority order within the time budget:
 *   Phase A: 9 fixed matrices + Stage1 + Stage2 + short walk
 *   Phase B: parametric family t=1..t_max + Stage1 + Stage2
 *   Phase C: random curves + Stage1 + Stage2
 *   Phase D: long random walks from all warm-start positions
 *
 * This ensures the highest-value work runs first.
 * ================================================================ */
u64 combined_timed(
    u64 N,
    int B1,
    int B2,
    int t_max,
    int num_random_curves,
    u64 walk_steps_per_start,
    int time_limit_ms,
    u64 seed,
    u64 *steps_out
) {
    struct timespec t0, now;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    u64 steps = 0;
    rng_seed(seed);

    /* Sieve primes up to B2 */
    int max_primes = B2 + 100;
    int *primes = (int *)malloc(max_primes * sizeof(int));
    if (!primes) { *steps_out = 0; return 0; }
    int nprimes = sieve_primes(B2, primes, max_primes);

    int stage2_start = 0;
    for (int i = 0; i < nprimes; i++) {
        if (primes[i] > B1) { stage2_start = i; break; }
    }

    /* Convert forward matrices to mod-N form */
    MMat fwd_mats[N_FWD];
    for (int i = 0; i < N_FWD; i++)
        fwd_mats[i] = imat_to_mmat(&FORWARD_INT[i], N);

    /* Shared batch accumulator */
    u64 accum = 1;
    int accum_count = 0;
    u64 start_m = 2, start_n = 1;

    /* Save warm-start positions for Phase D walk */
    int max_warm = N_FWD + t_max + num_random_curves;
    if (max_warm > 10000) max_warm = 10000;
    u64 *warm_m = (u64 *)malloc(max_warm * sizeof(u64));
    u64 *warm_n = (u64 *)malloc(max_warm * sizeof(u64));
    if (!warm_m || !warm_n) { free(primes); free(warm_m); free(warm_n); *steps_out = 0; return 0; }
    int n_warm = 0;

    /* Macros for cleanup/return/time-check to reduce boilerplate */
    #define CT_FREE() do { free(primes); free(warm_m); free(warm_n); } while(0)

    /* ---- Phase A: 9 fixed Pythagorean matrices ---- */
    for (int mi = 0; mi < N_FWD; mi++) {
        MMat M = fwd_mats[mi];
        MMat Mk = smooth_stage1(M, N, B1, primes, nprimes, &steps);

        u64 m2, n2;
        mmat_apply(Mk, start_m, start_n, N, &m2, &n2);

        u64 f = check_derived(m2, n2, N);
        if (f) { CT_FREE(); *steps_out = steps; return f; }
        f = accum_derived(m2, n2, N, &accum, &accum_count, BATCH_SZ);
        if (f) { CT_FREE(); *steps_out = steps; return f; }

        /* Check M^E - I */
        u64 d00 = (Mk.a00 >= 1) ? Mk.a00 - 1 : N - 1 + Mk.a00;
        u64 d11 = (Mk.a11 >= 1) ? Mk.a11 - 1 : N - 1 + Mk.a11;
        if (d00 > 0 && d00 < N) {
            u64 g = gcd64(d00, N);
            if (g > 1 && g < N) { CT_FREE(); *steps_out = steps; return g; }
            accum = (u64)((u128)accum * d00 % N); accum_count++;
        }
        if (d11 > 0 && d11 < N) {
            u64 g = gcd64(d11, N);
            if (g > 1 && g < N) { CT_FREE(); *steps_out = steps; return g; }
            accum = (u64)((u128)accum * d11 % N); accum_count++;
        }
        if (Mk.a01 > 0) { accum = (u64)((u128)accum * Mk.a01 % N); accum_count++; }
        if (Mk.a10 > 0) { accum = (u64)((u128)accum * Mk.a10 % N); accum_count++; }
        if (accum_count >= BATCH_SZ) {
            u64 g = gcd64(accum, N);
            if (g > 1 && g < N) { CT_FREE(); *steps_out = steps; return g; }
            accum = 1; accum_count = 0;
        }

        /* Stage 2 */
        for (int qi = stage2_start; qi < nprimes; qi++) {
            MMat Mq = mmat_pow(Mk, (u64)primes[qi], N);
            steps += 16;
            u64 qm, qn;
            mmat_apply(Mq, start_m, start_n, N, &qm, &qn);
            f = check_derived(qm, qn, N);
            if (f) { CT_FREE(); *steps_out = steps; return f; }
            f = accum_derived(qm, qn, N, &accum, &accum_count, BATCH_SZ);
            if (f) { CT_FREE(); *steps_out = steps; return f; }
        }

        /* Save warm-start */
        if (n_warm < max_warm) { warm_m[n_warm] = m2; warm_n[n_warm] = n2; n_warm++; }

        /* Short walk (1000 steps) from warm-start */
        {
            u64 wm = m2, wn = n2;
            for (int w = 0; w < 1000; w++) {
                int wi = (int)(rng() % N_FWD);
                u64 wm2, wn2;
                mmat_apply(fwd_mats[wi], wm, wn, N, &wm2, &wn2);
                wm = wm2; wn = wn2;
                steps++;
                f = check_derived(wm, wn, N);
                if (f) { CT_FREE(); *steps_out = steps; return f; }
                f = accum_derived(wm, wn, N, &accum, &accum_count, BATCH_SZ);
                if (f) { CT_FREE(); *steps_out = steps; return f; }
            }
        }

        clock_gettime(CLOCK_MONOTONIC, &now);
        if ((now.tv_sec - t0.tv_sec)*1000 + (now.tv_nsec - t0.tv_nsec)/1000000 >= time_limit_ms) goto ct_done;
    }

    /* ---- Phase B: Parametric family t=1..t_max ---- */
    for (int t = 1; t <= t_max; t++) {
        MMat M = { (u64)t % N, 1, 1, 0 };
        MMat Mk = smooth_stage1(M, N, B1, primes, nprimes, &steps);

        u64 m2, n2;
        mmat_apply(Mk, start_m, start_n, N, &m2, &n2);

        u64 f = check_derived(m2, n2, N);
        if (f) { CT_FREE(); *steps_out = steps; return f; }
        f = accum_derived(m2, n2, N, &accum, &accum_count, BATCH_SZ);
        if (f) { CT_FREE(); *steps_out = steps; return f; }

        /* M^E - I checks */
        u64 d00 = (Mk.a00 >= 1) ? Mk.a00 - 1 : N - 1 + Mk.a00;
        u64 d11 = (Mk.a11 >= 1) ? Mk.a11 - 1 : N - 1 + Mk.a11;
        if (d00 > 0 && d00 < N) {
            u64 g = gcd64(d00, N);
            if (g > 1 && g < N) { CT_FREE(); *steps_out = steps; return g; }
            accum = (u64)((u128)accum * d00 % N); accum_count++;
        }
        if (d11 > 0 && d11 < N) {
            u64 g = gcd64(d11, N);
            if (g > 1 && g < N) { CT_FREE(); *steps_out = steps; return g; }
            accum = (u64)((u128)accum * d11 % N); accum_count++;
        }
        if (Mk.a01 > 0) { accum = (u64)((u128)accum * Mk.a01 % N); accum_count++; }
        if (Mk.a10 > 0) { accum = (u64)((u128)accum * Mk.a10 % N); accum_count++; }
        if (accum_count >= BATCH_SZ) {
            u64 g = gcd64(accum, N);
            if (g > 1 && g < N) { CT_FREE(); *steps_out = steps; return g; }
            accum = 1; accum_count = 0;
        }

        /* Stage 2 */
        for (int qi = stage2_start; qi < nprimes; qi++) {
            MMat Mq = mmat_pow(Mk, (u64)primes[qi], N);
            steps += 16;
            u64 qm, qn;
            mmat_apply(Mq, start_m, start_n, N, &qm, &qn);
            f = check_derived(qm, qn, N);
            if (f) { CT_FREE(); *steps_out = steps; return f; }
            f = accum_derived(qm, qn, N, &accum, &accum_count, BATCH_SZ);
            if (f) { CT_FREE(); *steps_out = steps; return f; }
        }

        if (n_warm < max_warm) { warm_m[n_warm] = m2; warm_n[n_warm] = n2; n_warm++; }

        if ((t & 31) == 0) {
            clock_gettime(CLOCK_MONOTONIC, &now);
            if ((now.tv_sec - t0.tv_sec)*1000 + (now.tv_nsec - t0.tv_nsec)/1000000 >= time_limit_ms) goto ct_done;
        }
    }

    /* ---- Phase C: Random curves ---- */
    for (int ci = 0; ci < num_random_curves; ci++) {
        MMat M;
        M.a00 = rng() % N; if (M.a00 == 0) M.a00 = 1;
        M.a01 = rng() % N; if (M.a01 == 0) M.a01 = 1;
        M.a10 = rng() % N; if (M.a10 == 0) M.a10 = 1;
        M.a11 = rng() % N; if (M.a11 == 0) M.a11 = 1;

        MMat Mk = smooth_stage1(M, N, B1, primes, nprimes, &steps);

        /* Check multiple starting vectors */
        u64 svecs[3][2] = {{2,1}, {1,0}, {0,1}};
        int sv;
        for (sv = 0; sv < 3; sv++) {
            u64 m2, n2;
            mmat_apply(Mk, svecs[sv][0], svecs[sv][1], N, &m2, &n2);
            u64 f = check_derived(m2, n2, N);
            if (f) { CT_FREE(); *steps_out = steps; return f; }
            f = accum_derived(m2, n2, N, &accum, &accum_count, BATCH_SZ);
            if (f) { CT_FREE(); *steps_out = steps; return f; }
            if (sv == 0 && n_warm < max_warm) { warm_m[n_warm] = m2; warm_n[n_warm] = n2; n_warm++; }
        }

        /* M^E - I checks */
        u64 d00 = (Mk.a00 >= 1) ? Mk.a00 - 1 : N - 1 + Mk.a00;
        u64 d11 = (Mk.a11 >= 1) ? Mk.a11 - 1 : N - 1 + Mk.a11;
        if (d00 > 0 && d00 < N) {
            accum = (u64)((u128)accum * d00 % N); accum_count++;
            u64 g = gcd64(d00, N);
            if (g > 1 && g < N) { CT_FREE(); *steps_out = steps; return g; }
        }
        if (d11 > 0 && d11 < N) {
            accum = (u64)((u128)accum * d11 % N); accum_count++;
            u64 g = gcd64(d11, N);
            if (g > 1 && g < N) { CT_FREE(); *steps_out = steps; return g; }
        }
        if (Mk.a01 > 0) { accum = (u64)((u128)accum * Mk.a01 % N); accum_count++; }
        if (Mk.a10 > 0) { accum = (u64)((u128)accum * Mk.a10 % N); accum_count++; }
        if (accum_count >= BATCH_SZ) {
            u64 g = gcd64(accum, N);
            if (g > 1 && g < N) { CT_FREE(); *steps_out = steps; return g; }
            accum = 1; accum_count = 0;
        }

        /* Stage 2 for random curves */
        for (int qi = stage2_start; qi < nprimes; qi++) {
            MMat Mq = mmat_pow(Mk, (u64)primes[qi], N);
            steps += 16;
            u64 qm, qn;
            mmat_apply(Mq, start_m, start_n, N, &qm, &qn);
            u64 f = check_derived(qm, qn, N);
            if (f) { CT_FREE(); *steps_out = steps; return f; }
            f = accum_derived(qm, qn, N, &accum, &accum_count, BATCH_SZ);
            if (f) { CT_FREE(); *steps_out = steps; return f; }
        }

        if ((ci & 15) == 0) {
            clock_gettime(CLOCK_MONOTONIC, &now);
            if ((now.tv_sec - t0.tv_sec)*1000 + (now.tv_nsec - t0.tv_nsec)/1000000 >= time_limit_ms) goto ct_done;
        }
    }

    /* ---- Phase D: Long random walks from ALL warm-start positions ---- */
    /* Round-robin across all warm starts to spread coverage */
    for (u64 w = 0; w < walk_steps_per_start; w++) {
        int si;
        for (si = 0; si < n_warm; si++) {
            int wi = (int)(rng() % N_FWD);
            u64 wm2, wn2;
            mmat_apply(fwd_mats[wi], warm_m[si], warm_n[si], N, &wm2, &wn2);
            warm_m[si] = wm2; warm_n[si] = wn2;
            steps++;

            u64 f = check_derived(wm2, wn2, N);
            if (f) { CT_FREE(); *steps_out = steps; return f; }
            f = accum_derived(wm2, wn2, N, &accum, &accum_count, BATCH_SZ);
            if (f) { CT_FREE(); *steps_out = steps; return f; }
        }

        if ((w & 4095) == 0) {
            clock_gettime(CLOCK_MONOTONIC, &now);
            if ((now.tv_sec - t0.tv_sec)*1000 + (now.tv_nsec - t0.tv_nsec)/1000000 >= time_limit_ms) goto ct_done;
        }
    }

ct_done:
    /* Final flush */
    if (accum_count > 0) {
        u64 g = gcd64(accum, N);
        if (g > 1 && g < N) { CT_FREE(); *steps_out = steps; return g; }
    }

    CT_FREE();
    *steps_out = steps;
    return 0;
    #undef CT_FREE
}
