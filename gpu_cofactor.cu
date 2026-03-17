/*
 * GPU Batch Cofactor Checking for SIQS
 * After sieve identifies candidates, each needs:
 * 1. Trial division by factor base primes
 * 2. Cofactor primality test (Miller-Rabin)
 *
 * GPU batch: send thousands of candidates, each divided by FB primes in parallel.
 *
 * Compile: nvcc -O3 -arch=sm_89 -o gpu_cofactor gpu_cofactor.cu
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

/* Factor base primes stored in constant memory (up to 16K entries) */
#define MAX_FB 8192
__constant__ uint32_t d_fb[MAX_FB];
__constant__ int d_fb_size;

/* 64-bit modmul */
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

/* Miller-Rabin primality test */
__device__ int is_probable_prime(uint64_t n) {
    if (n < 2) return 0;
    if (n < 4) return 1;
    if (n % 2 == 0) return 0;

    // Write n-1 = d * 2^r
    uint64_t d = n - 1;
    int r = 0;
    while ((d & 1) == 0) { d >>= 1; r++; }

    // Deterministic witnesses for n < 3.317e14
    uint64_t witnesses[] = {2, 3, 5, 7, 11, 13};
    int nw = 6;

    for (int w = 0; w < nw; w++) {
        uint64_t a = witnesses[w];
        if (a >= n) continue;
        uint64_t x = powmod(a, d, n);
        if (x == 1 || x == n - 1) continue;
        int found = 0;
        for (int i = 0; i < r - 1; i++) {
            x = mulmod(x, x, n);
            if (x == n - 1) { found = 1; break; }
        }
        if (!found) return 0;
    }
    return 1;
}

/*
 * Kernel: Trial division + cofactor check
 * Each thread processes one candidate value.
 * Input: array of candidate Q(x) values (absolute values)
 * Output: for each candidate:
 *   - smooth flag (1 if fully smooth or has small cofactor)
 *   - cofactor after trial division
 *   - exponent vector (packed bits for FB primes)
 */
__global__ void batch_trial_divide(
    const uint64_t *candidates,   // Q(x) values
    int num_candidates,
    uint64_t *cofactors,          // remaining cofactor
    int *smooth_flags,            // 1=smooth, 2=partial (1-LP), 0=not smooth
    uint32_t *exponent_bits,      // packed exponent parity bits (32 primes per uint32)
    uint64_t lp_bound             // large prime bound
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= num_candidates) return;

    uint64_t val = candidates[idx];
    if (val == 0) { smooth_flags[idx] = 0; cofactors[idx] = 0; return; }

    int fb_size = d_fb_size;
    int exp_words = (fb_size + 31) / 32;

    // Clear exponent bits
    for (int w = 0; w < exp_words && w < 256; w++)  // max 256 words = 8192 primes
        exponent_bits[idx * 256 + w] = 0;

    // Handle sign (Q(x) can be negative, passed as |Q(x)|)
    // In SIQS, the sign is tracked separately

    // Trial divide by each FB prime
    for (int i = 0; i < fb_size; i++) {
        uint32_t p = d_fb[i];
        if (p == 0) break;
        int exp = 0;
        while (val % p == 0) {
            val /= p;
            exp++;
        }
        // Store parity of exponent
        if (exp & 1) {
            int word = i / 32;
            int bit = i % 32;
            if (word < 256)
                exponent_bits[idx * 256 + word] |= (1U << bit);
        }
        if (val == 1) break;
    }

    cofactors[idx] = val;

    if (val == 1) {
        smooth_flags[idx] = 1;  // fully smooth
    } else if (val <= lp_bound && is_probable_prime(val)) {
        smooth_flags[idx] = 2;  // 1-large-prime partial
    } else {
        smooth_flags[idx] = 0;  // not smooth
    }
}

/* CPU reference implementation */
uint64_t cpu_mulmod(uint64_t a, uint64_t b, uint64_t m) {
    unsigned __int128 p = (unsigned __int128)a * b;
    return (uint64_t)(p % m);
}

int cpu_trial_divide(uint64_t val, const uint32_t *fb, int fb_size, uint64_t lp_bound) {
    for (int i = 0; i < fb_size; i++) {
        while (val % fb[i] == 0) val /= fb[i];
        if (val == 1) return 1;
    }
    if (val <= lp_bound) return 2;
    return 0;
}

int main() {
    printf("=== GPU Batch Cofactor Checking Benchmark ===\n\n");

    // Generate a realistic factor base (first N primes)
    int fb_sizes[] = {500, 2000, 5000};
    int num_fb_tests = 3;

    // Generate primes
    uint32_t all_primes[MAX_FB];
    int prime_count = 0;
    {
        char *sieve = (char*)calloc(200000, 1);
        for (int i = 2; i < 200000; i++) sieve[i] = 1;
        for (int i = 2; i * i < 200000; i++)
            if (sieve[i])
                for (int j = i*i; j < 200000; j += i) sieve[j] = 0;
        for (int i = 2; i < 200000 && prime_count < MAX_FB; i++)
            if (sieve[i]) all_primes[prime_count++] = i;
        free(sieve);
    }
    printf("Generated %d primes (max = %u)\n", prime_count, all_primes[prime_count-1]);

    // Generate candidate values that simulate SIQS Q(x) values
    // Mix of smooth and non-smooth numbers
    int NUM_CANDIDATES = 1 << 16;  // 65536 candidates (realistic batch)
    uint64_t *h_candidates = (uint64_t*)malloc(NUM_CANDIDATES * sizeof(uint64_t));
    srand(42);
    for (int i = 0; i < NUM_CANDIDATES; i++) {
        // Create values that are products of small primes (smooth) ~30% of the time
        if (rand() % 100 < 30) {
            uint64_t v = 1;
            for (int j = 0; j < 8 + rand() % 8; j++) {
                v *= all_primes[rand() % 500];
                if (v > (1ULL << 60)) break;
            }
            h_candidates[i] = v > 0 ? v : 1;
        } else {
            // Random 60-bit value (mostly not smooth)
            h_candidates[i] = ((uint64_t)rand() << 32 | rand()) | (1ULL << 59);
        }
    }

    // Device allocations
    uint64_t *d_candidates, *d_cofactors;
    int *d_smooth;
    uint32_t *d_exp_bits;
    CHECK_CUDA(cudaMalloc(&d_candidates, NUM_CANDIDATES * sizeof(uint64_t)));
    CHECK_CUDA(cudaMalloc(&d_cofactors, NUM_CANDIDATES * sizeof(uint64_t)));
    CHECK_CUDA(cudaMalloc(&d_smooth, NUM_CANDIDATES * sizeof(int)));
    CHECK_CUDA(cudaMalloc(&d_exp_bits, (size_t)NUM_CANDIDATES * 256 * sizeof(uint32_t)));
    CHECK_CUDA(cudaMemcpy(d_candidates, h_candidates, NUM_CANDIDATES * sizeof(uint64_t),
                          cudaMemcpyHostToDevice));

    uint64_t *h_cofactors = (uint64_t*)malloc(NUM_CANDIDATES * sizeof(uint64_t));
    int *h_smooth = (int*)malloc(NUM_CANDIDATES * sizeof(int));

    cudaEvent_t start, stop;
    CHECK_CUDA(cudaEventCreate(&start));
    CHECK_CUDA(cudaEventCreate(&stop));

    int BLOCK = 256;

    for (int ft = 0; ft < num_fb_tests; ft++) {
        int fb_size = fb_sizes[ft];
        printf("\n--- FB size = %d (largest prime = %u) ---\n", fb_size, all_primes[fb_size-1]);

        // Upload factor base
        CHECK_CUDA(cudaMemcpyToSymbol(d_fb, all_primes, fb_size * sizeof(uint32_t)));
        CHECK_CUDA(cudaMemcpyToSymbol(d_fb_size, &fb_size, sizeof(int)));

        uint64_t lp_bound = (uint64_t)all_primes[fb_size-1] * 100;

        int GRID = (NUM_CANDIDATES + BLOCK - 1) / BLOCK;

        // Warmup
        batch_trial_divide<<<GRID, BLOCK>>>(d_candidates, NUM_CANDIDATES,
                                             d_cofactors, d_smooth, d_exp_bits, lp_bound);
        CHECK_CUDA(cudaDeviceSynchronize());

        // Benchmark GPU
        CHECK_CUDA(cudaEventRecord(start));
        batch_trial_divide<<<GRID, BLOCK>>>(d_candidates, NUM_CANDIDATES,
                                             d_cofactors, d_smooth, d_exp_bits, lp_bound);
        CHECK_CUDA(cudaEventRecord(stop));
        CHECK_CUDA(cudaEventSynchronize(stop));

        float ms;
        CHECK_CUDA(cudaEventElapsedTime(&ms, start, stop));

        CHECK_CUDA(cudaMemcpy(h_smooth, d_smooth, NUM_CANDIDATES * sizeof(int),
                              cudaMemcpyDeviceToHost));
        CHECK_CUDA(cudaMemcpy(h_cofactors, d_cofactors, NUM_CANDIDATES * sizeof(uint64_t),
                              cudaMemcpyDeviceToHost));

        int gpu_full = 0, gpu_partial = 0, gpu_fail = 0;
        for (int i = 0; i < NUM_CANDIDATES; i++) {
            if (h_smooth[i] == 1) gpu_full++;
            else if (h_smooth[i] == 2) gpu_partial++;
            else gpu_fail++;
        }

        printf("  GPU: %.3f ms for %d candidates\n", ms, NUM_CANDIDATES);
        printf("  Results: %d smooth, %d partial, %d not smooth\n",
               gpu_full, gpu_partial, gpu_fail);
        printf("  Throughput: %.0f candidates/ms = %.2f M candidates/sec\n",
               NUM_CANDIDATES / ms, NUM_CANDIDATES / (ms * 1000.0));

        // CPU reference
        struct timespec ts1, ts2;
        clock_gettime(CLOCK_MONOTONIC, &ts1);
        int cpu_full = 0, cpu_partial = 0;
        for (int i = 0; i < NUM_CANDIDATES; i++) {
            int r = cpu_trial_divide(h_candidates[i], all_primes, fb_size, lp_bound);
            if (r == 1) cpu_full++;
            else if (r == 2) cpu_partial++;
        }
        clock_gettime(CLOCK_MONOTONIC, &ts2);
        double cpu_ms = (ts2.tv_sec - ts1.tv_sec) * 1000.0 +
                        (ts2.tv_nsec - ts1.tv_nsec) / 1e6;

        printf("  CPU: %.3f ms for %d candidates (%d smooth, %d partial)\n",
               cpu_ms, NUM_CANDIDATES, cpu_full, cpu_partial);
        printf("  Speedup: %.1fx\n", cpu_ms / ms);

        // Verify agreement
        if (cpu_full != gpu_full)
            printf("  WARNING: smooth count mismatch: CPU=%d GPU=%d\n", cpu_full, gpu_full);
    }

    // Cleanup
    cudaFree(d_candidates); cudaFree(d_cofactors);
    cudaFree(d_smooth); cudaFree(d_exp_bits);
    free(h_candidates); free(h_cofactors); free(h_smooth);
    cudaEventDestroy(start); cudaEventDestroy(stop);
    return 0;
}
