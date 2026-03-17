/*
 * GPU Batch ECM Phase 1
 * Runs 2560 independent ECM curves in parallel using Montgomery form.
 * Each curve uses a different random sigma for curve generation.
 * Phase 1: scalar multiplication by lcm(1..B1) using Montgomery ladder.
 *
 * Compile: nvcc -O3 -arch=sm_89 -o gpu_batch_ecm gpu_batch_ecm.cu
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
#include <cuda_runtime.h>

#define CHECK_CUDA(call) do { \
    cudaError_t err = call; \
    if (err != cudaSuccess) { \
        fprintf(stderr, "CUDA error at %s:%d: %s\n", __FILE__, __LINE__, \
                cudaGetErrorString(err)); \
        exit(1); \
    } \
} while(0)

/* 64-bit modular arithmetic */
__device__ __forceinline__
uint64_t _reduce128(uint64_t hi, uint64_t lo, uint64_t m) {
    uint64_t hm = hi % m;
    uint64_t lm = lo % m;
    uint64_t pow2 = (uint64_t)(-(int64_t)m) % m;
    uint64_t r = 0, aa = hm, bb = pow2;
    while (bb > 0) {
        if (bb & 1) { r += aa; if (r >= m || r < aa) r -= m; }
        aa += aa; if (aa >= m || aa == 0) aa -= m;
        bb >>= 1;
    }
    r += lm;
    if (r >= m || r < lm) r -= m;
    return r;
}

__device__ __forceinline__
uint64_t mulmod(uint64_t a, uint64_t b, uint64_t m) {
    uint64_t hi, lo;
    asm("mul.hi.u64 %0, %1, %2;" : "=l"(hi) : "l"(a), "l"(b));
    asm("mul.lo.u64 %0, %1, %2;" : "=l"(lo) : "l"(a), "l"(b));
    return _reduce128(hi, lo, m);
}

__device__ __forceinline__
uint64_t addmod(uint64_t a, uint64_t b, uint64_t m) {
    uint64_t r = a + b;
    if (r >= m || r < a) r -= m;
    return r;
}

__device__ __forceinline__
uint64_t submod(uint64_t a, uint64_t b, uint64_t m) {
    return a >= b ? a - b : a + m - b;
}

__device__
uint64_t gcd_dev(uint64_t a, uint64_t b) {
    while (b) { uint64_t t = b; b = a % b; a = t; }
    return a;
}

__device__
uint64_t powmod(uint64_t base, uint64_t exp, uint64_t m) {
    uint64_t result = 1;
    base %= m;
    while (exp > 0) {
        if (exp & 1) result = mulmod(result, base, m);
        base = mulmod(base, base, m);
        exp >>= 1;
    }
    return result;
}

__device__
uint64_t modinv(uint64_t a, uint64_t m) {
    // Extended GCD
    int64_t old_r = (int64_t)a, r = (int64_t)m;
    int64_t old_s = 1, s = 0;
    while (r != 0) {
        int64_t q = old_r / r;
        int64_t tmp = r; r = old_r - q * r; old_r = tmp;
        tmp = s; s = old_s - q * s; old_s = tmp;
    }
    if (old_r != 1) return 0;  // not invertible (found factor!)
    return old_s < 0 ? (uint64_t)(old_s + (int64_t)m) : (uint64_t)old_s;
}

/*
 * Montgomery curve ECM:
 * Curve: By^2 = x^3 + Ax^2 + x (mod n)
 * Point represented as (X : Z) in projective coords
 *
 * Montgomery ladder for scalar multiplication:
 * - Double: uses 3M + 2S + 1D
 * - DiffAdd: uses 4M + 2S
 * Where M=modmul, S=modsquare, D=mul by constant
 */

struct MontPoint {
    uint64_t X, Z;
};

// Montgomery curve double
__device__ MontPoint mont_double(MontPoint P, uint64_t A24, uint64_t n) {
    // A24 = (A+2)/4
    uint64_t u = addmod(P.X, P.Z, n);
    uint64_t v = submod(P.X, P.Z, n);
    uint64_t u2 = mulmod(u, u, n);
    uint64_t v2 = mulmod(v, v, n);
    uint64_t diff = submod(u2, v2, n);
    MontPoint R;
    R.X = mulmod(u2, v2, n);
    R.Z = mulmod(diff, addmod(v2, mulmod(A24, diff, n), n), n);
    return R;
}

// Montgomery differential addition: given P, Q, and P-Q, compute P+Q
__device__ MontPoint mont_add(MontPoint P, MontPoint Q, MontPoint PmQ, uint64_t n) {
    uint64_t u = mulmod(submod(P.X, P.Z, n), addmod(Q.X, Q.Z, n), n);
    uint64_t v = mulmod(addmod(P.X, P.Z, n), submod(Q.X, Q.Z, n), n);
    MontPoint R;
    R.X = mulmod(PmQ.Z, mulmod(addmod(u, v, n), addmod(u, v, n), n), n);
    R.Z = mulmod(PmQ.X, mulmod(submod(u, v, n), submod(u, v, n), n), n);
    return R;
}

// Montgomery ladder: compute k*P
__device__ MontPoint mont_ladder(MontPoint P, uint64_t k, uint64_t A24, uint64_t n) {
    if (k == 0) { MontPoint O; O.X = 0; O.Z = 1; return O; }
    if (k == 1) return P;

    MontPoint R0 = P;
    MontPoint R1 = mont_double(P, A24, n);

    // Find highest bit
    int bits = 63;
    while (bits > 0 && !((k >> bits) & 1)) bits--;
    bits--;  // skip highest bit (already processed)

    for (int i = bits; i >= 0; i--) {
        if ((k >> i) & 1) {
            R0 = mont_add(R0, R1, P, n);
            R1 = mont_double(R1, A24, n);
        } else {
            R1 = mont_add(R0, R1, P, n);
            R0 = mont_double(R0, A24, n);
        }
    }
    return R0;
}

/* Primes up to B1 stored in constant memory */
// B1 = 10000 -> about 1229 primes
#define MAX_PRIMES 1300
__constant__ uint32_t d_primes[MAX_PRIMES];
__constant__ int d_num_primes;

/*
 * ECM Phase 1 kernel
 * Each thread runs one independent curve with different sigma
 */
__global__ void ecm_phase1(uint64_t n, uint64_t *factors, int *found_flag,
                            int num_curves) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= num_curves) return;

    // Generate curve from sigma
    uint64_t sigma = (uint64_t)(idx + 6);  // sigma >= 6
    // Suyama's parametrization
    uint64_t u = mulmod(sigma, sigma, n);
    u = submod(u, 5, n);
    uint64_t v = mulmod(4, sigma, n);

    // x0 = u^3 / v^3, but in projective: X0 = u^3, Z0 = v^3
    uint64_t u3 = mulmod(mulmod(u, u, n), u, n);
    uint64_t v3 = mulmod(mulmod(v, v, n), v, n);

    MontPoint P;
    P.X = u3;
    P.Z = v3;

    // A = (v-u)^3 * (3u+v) / (4*u^3*v) - 2
    // A24 = (A+2)/4 = (v-u)^3 * (3u+v) / (16*u^3*v)
    uint64_t vmu = submod(v, u, n);
    uint64_t vmu3 = mulmod(mulmod(vmu, vmu, n), vmu, n);
    uint64_t threeu_v = addmod(mulmod(3, u, n), v, n);
    uint64_t num = mulmod(vmu3, threeu_v, n);
    uint64_t den = mulmod(16, mulmod(u3, v, n), n);

    uint64_t den_inv = modinv(den, n);
    if (den_inv == 0) {
        // GCD(den, n) > 1 -- found factor!
        factors[idx] = gcd_dev(den, n);
        atomicMax(found_flag, 1);
        return;
    }
    uint64_t A24 = mulmod(num, den_inv, n);

    // Phase 1: multiply P by lcm(1..B1)
    // For each prime p <= B1, multiply by p^floor(log(B1)/log(p))
    int np = d_num_primes;
    for (int i = 0; i < np; i++) {
        uint64_t p = d_primes[i];
        // Compute p^a where p^a <= B1
        uint64_t pp = p;
        while (pp <= 10000 / p) pp *= p;  // pp = p^floor(log(B1)/log(p))

        P = mont_ladder(P, pp, A24, n);

        // Check if Z = 0 mod some factor periodically
        if ((i & 63) == 0 && P.Z != 0) {
            uint64_t g = gcd_dev(P.Z, n);
            if (g > 1 && g < n) {
                factors[idx] = g;
                atomicMax(found_flag, 1);
                return;
            }
        }
    }

    // Final check
    uint64_t g = gcd_dev(P.Z, n);
    if (g > 1 && g < n) {
        factors[idx] = g;
        atomicMax(found_flag, 1);
    } else {
        factors[idx] = 0;
    }
}

/* Generate primes up to limit using sieve */
int sieve_primes(uint32_t *primes, int limit) {
    char *is_prime = (char*)calloc(limit + 1, 1);
    for (int i = 2; i <= limit; i++) is_prime[i] = 1;
    for (int i = 2; i * i <= limit; i++)
        if (is_prime[i])
            for (int j = i*i; j <= limit; j += i) is_prime[j] = 0;
    int count = 0;
    for (int i = 2; i <= limit && count < MAX_PRIMES; i++)
        if (is_prime[i]) primes[count++] = i;
    free(is_prime);
    return count;
}

/* CPU ECM reference */
uint64_t cpu_mulmod(uint64_t a, uint64_t b, uint64_t m) {
    unsigned __int128 p = (unsigned __int128)a * b;
    return (uint64_t)(p % m);
}

uint64_t cpu_gcd(uint64_t a, uint64_t b) {
    while (b) { uint64_t t = b; b = a % b; a = t; }
    return a;
}

int main() {
    printf("=== GPU Batch ECM Phase 1 Benchmark ===\n\n");

    // Setup primes
    uint32_t h_primes[MAX_PRIMES];
    int B1 = 10000;
    int nprimes = sieve_primes(h_primes, B1);
    printf("B1 = %d, %d primes\n", B1, nprimes);
    CHECK_CUDA(cudaMemcpyToSymbol(d_primes, h_primes, nprimes * sizeof(uint32_t)));
    CHECK_CUDA(cudaMemcpyToSymbol(d_num_primes, &nprimes, sizeof(int)));

    // Test numbers
    uint64_t test_cases[] = {
        1000000007ULL * 998244353ULL,     // 60-bit
        100000000003ULL * 99999999977ULL, // 74-bit (two 37-bit primes) -- too big for 64-bit!
        202739ULL * 203347ULL,            // 36-bit
        12764787846358441ULL,             // 54-bit
        2567ULL * 3571ULL,               // small test
    };
    // Fix: use only numbers that fit in 64 bits
    test_cases[1] = 10000000019ULL * 9999999967ULL;  // ~67 bit -- check overflow
    // Actually let's be careful: 10^10 * 10^10 = 10^20 > 2^64, so skip
    test_cases[1] = 100003ULL * 100019ULL;  // 34-bit

    const char *labels[] = {"60-bit", "34-bit", "36-bit", "54-bit", "small"};
    int num_tests = 5;

    int NUM_CURVES = 2560;
    int BLOCK = 256;
    int GRID = (NUM_CURVES + BLOCK - 1) / BLOCK;

    uint64_t *d_factors;
    int *d_found;
    uint64_t *h_factors = (uint64_t*)malloc(NUM_CURVES * sizeof(uint64_t));
    CHECK_CUDA(cudaMalloc(&d_factors, NUM_CURVES * sizeof(uint64_t)));
    CHECK_CUDA(cudaMalloc(&d_found, sizeof(int)));

    cudaEvent_t start, stop;
    CHECK_CUDA(cudaEventCreate(&start));
    CHECK_CUDA(cudaEventCreate(&stop));

    for (int t = 0; t < num_tests; t++) {
        uint64_t n = test_cases[t];
        printf("\n--- %s: n = %lu ---\n", labels[t], n);

        int zero = 0;
        CHECK_CUDA(cudaMemset(d_factors, 0, NUM_CURVES * sizeof(uint64_t)));
        CHECK_CUDA(cudaMemcpy(d_found, &zero, sizeof(int), cudaMemcpyHostToDevice));

        // Warmup
        ecm_phase1<<<GRID, BLOCK>>>(n, d_factors, d_found, NUM_CURVES);
        CHECK_CUDA(cudaDeviceSynchronize());

        CHECK_CUDA(cudaMemset(d_factors, 0, NUM_CURVES * sizeof(uint64_t)));
        CHECK_CUDA(cudaMemcpy(d_found, &zero, sizeof(int), cudaMemcpyHostToDevice));

        CHECK_CUDA(cudaEventRecord(start));
        ecm_phase1<<<GRID, BLOCK>>>(n, d_factors, d_found, NUM_CURVES);
        CHECK_CUDA(cudaEventRecord(stop));
        CHECK_CUDA(cudaEventSynchronize(stop));

        float ms;
        CHECK_CUDA(cudaEventElapsedTime(&ms, start, stop));

        CHECK_CUDA(cudaMemcpy(h_factors, d_factors, NUM_CURVES * sizeof(uint64_t),
                              cudaMemcpyDeviceToHost));

        int successes = 0;
        uint64_t first_factor = 0;
        for (int i = 0; i < NUM_CURVES; i++) {
            if (h_factors[i] > 0 && h_factors[i] < n) {
                successes++;
                if (first_factor == 0) first_factor = h_factors[i];
            }
        }

        printf("  GPU: %.3f ms, %d/%d curves found factor\n", ms, successes, NUM_CURVES);
        if (first_factor > 0)
            printf("  Factor: %lu (verify: %lu / %lu = %lu)\n",
                   first_factor, n, first_factor, n / first_factor);
        printf("  Throughput: %d ECM curves in %.3f ms = %.0f curves/sec\n",
               NUM_CURVES, ms, NUM_CURVES / (ms / 1000.0));

        // Estimate CPU equivalent
        // Single ECM curve B1=10000: ~1229 primes * ~13 bits avg * 12 modmuls = ~190K modmuls
        // CPU at ~0.3 Gmodmul/s: ~0.6ms per curve
        double est_cpu_per_curve_ms = 0.6;
        printf("  Est CPU sequential: %.1f ms for %d curves\n",
               est_cpu_per_curve_ms * NUM_CURVES, NUM_CURVES);
        if (ms > 0)
            printf("  Est speedup: %.1fx\n", est_cpu_per_curve_ms * NUM_CURVES / ms);
    }

    // Cleanup
    cudaFree(d_factors); cudaFree(d_found);
    free(h_factors);
    cudaEventDestroy(start); cudaEventDestroy(stop);
    return 0;
}
