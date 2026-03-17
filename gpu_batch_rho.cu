/*
 * GPU Batch Pollard Rho
 * Runs 2560+ independent Pollard rho instances in parallel on GPU.
 * Each instance uses a different c in f(x) = x^2 + c mod n.
 * Uses Brent's cycle detection with GCD batching.
 *
 * Compile: nvcc -O3 -arch=sm_89 -o gpu_batch_rho gpu_batch_rho.cu
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
#include <math.h>
#include <cuda_runtime.h>

#define CHECK_CUDA(call) do { \
    cudaError_t err = call; \
    if (err != cudaSuccess) { \
        fprintf(stderr, "CUDA error at %s:%d: %s\n", __FILE__, __LINE__, \
                cudaGetErrorString(err)); \
        exit(1); \
    } \
} while(0)

/* 64-bit modmul: (a * b) % m, correct for all 64-bit inputs where a,b < m */
__device__ __forceinline__
uint64_t _reduce128(uint64_t hi, uint64_t lo, uint64_t m) {
    // Reduce (hi:lo) mod m using repeated doubling of hi part
    // hi < m guaranteed, so we compute hi * 2^64 mod m + lo mod m
    uint64_t hm = hi % m;
    uint64_t lm = lo % m;
    // Compute hm * (2^64 mod m) mod m via binary method (no overflow)
    uint64_t pow2 = (uint64_t)(-(int64_t)m) % m;  // 2^64 mod m
    uint64_t r = 0;
    uint64_t aa = hm;
    uint64_t bb = pow2;
    // Russian peasant multiplication mod m (64 iterations max, no overflow)
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

/* Pollard rho with Brent's algorithm */
__global__ void pollard_rho_batch(uint64_t n, uint64_t *results, int num_instances,
                                   int max_steps, int *step_counts) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= num_instances) return;

    uint64_t c = (uint64_t)(idx + 1);  // different c for each instance
    uint64_t x = 2;  // starting value
    uint64_t y = 2;
    uint64_t d = 1;
    uint64_t q = 1;  // accumulated product for batch GCD

    int steps = 0;
    int m = 128;  // batch size for GCD
    int r = 1;
    uint64_t ys = 0, saved_x = x;

    // Brent's algorithm with batch GCD
    while (d == 1 && steps < max_steps) {
        saved_x = y;
        // Advance y by r steps
        for (int i = 0; i < r; i++) {
            y = addmod(mulmod(y, y, n), c, n);
            steps++;
        }

        int k = 0;
        while (k < r && d == 1) {
            ys = y;
            int batch = min(m, r - k);
            for (int i = 0; i < batch; i++) {
                y = addmod(mulmod(y, y, n), c, n);
                uint64_t diff = submod(y, saved_x, n);
                if (diff == 0) diff = 1;
                q = mulmod(q, diff, n);
                steps++;
            }
            d = gcd_dev(q, n);
            k += batch;
        }

        if (d == n) {
            // Backtrack
            d = 1;
            y = ys;
            while (d == 1) {
                y = addmod(mulmod(y, y, n), c, n);
                uint64_t diff = submod(y, saved_x, n);
                d = gcd_dev(diff, n);
                steps++;
            }
        }
        r *= 2;
    }

    results[idx] = (d > 1 && d < n) ? d : 0;
    step_counts[idx] = steps;
}

/* CPU reference */
uint64_t cpu_mulmod(uint64_t a, uint64_t b, uint64_t m) {
    unsigned __int128 p = (unsigned __int128)a * b;
    return (uint64_t)(p % m);
}

uint64_t cpu_gcd(uint64_t a, uint64_t b) {
    while (b) { uint64_t t = b; b = a % b; a = t; }
    return a;
}

uint64_t cpu_pollard_rho(uint64_t n, uint64_t c, int *steps) {
    uint64_t x = 2, y = 2, d = 1;
    *steps = 0;
    while (d == 1) {
        x = (cpu_mulmod(x, x, n) + c) % n;
        y = (cpu_mulmod(y, y, n) + c) % n;
        y = (cpu_mulmod(y, y, n) + c) % n;
        uint64_t diff = x > y ? x - y : y - x;
        d = cpu_gcd(diff, n);
        (*steps)++;
        if (*steps > 1000000) break;
    }
    return (d > 1 && d < n) ? d : 0;
}

int main() {
    printf("=== GPU Batch Pollard Rho Benchmark ===\n\n");

    // Test semiprimes of various sizes
    // 48-bit: p*q where p,q ~ 24 bits
    uint64_t test_cases[] = {
        202739ULL * 203347ULL,           // 36-bit (two 18-bit primes)
        12764787846358441ULL,            // 54-bit = 100711423 * 126735607
        247177473923481121ULL,           // 58-bit = 498019321 * 496328801
        2567ULL * 3571ULL,              // small test
        1000000007ULL * 1000000009ULL,   // 60-bit
    };
    const char *labels[] = {"36-bit", "54-bit", "58-bit", "small", "60-bit"};
    int num_tests = 5;

    int NUM_INSTANCES = 2560;  // Match CUDA cores
    int MAX_STEPS = 1 << 20;  // 1M steps max per instance
    int BLOCK = 256;
    int GRID = (NUM_INSTANCES + BLOCK - 1) / BLOCK;

    uint64_t *d_results;
    int *d_steps;
    uint64_t *h_results = (uint64_t*)malloc(NUM_INSTANCES * sizeof(uint64_t));
    int *h_steps = (int*)malloc(NUM_INSTANCES * sizeof(int));
    CHECK_CUDA(cudaMalloc(&d_results, NUM_INSTANCES * sizeof(uint64_t)));
    CHECK_CUDA(cudaMalloc(&d_steps, NUM_INSTANCES * sizeof(int)));

    cudaEvent_t start, stop;
    CHECK_CUDA(cudaEventCreate(&start));
    CHECK_CUDA(cudaEventCreate(&stop));

    for (int t = 0; t < num_tests; t++) {
        uint64_t n = test_cases[t];
        printf("--- %s: n = %lu ---\n", labels[t], n);

        // GPU batch
        // Warmup
        pollard_rho_batch<<<GRID, BLOCK>>>(n, d_results, NUM_INSTANCES, 100, d_steps);
        CHECK_CUDA(cudaDeviceSynchronize());

        CHECK_CUDA(cudaEventRecord(start));
        pollard_rho_batch<<<GRID, BLOCK>>>(n, d_results, NUM_INSTANCES, MAX_STEPS, d_steps);
        CHECK_CUDA(cudaEventRecord(stop));
        CHECK_CUDA(cudaEventSynchronize(stop));

        float ms;
        CHECK_CUDA(cudaEventElapsedTime(&ms, start, stop));

        CHECK_CUDA(cudaMemcpy(h_results, d_results, NUM_INSTANCES * sizeof(uint64_t),
                              cudaMemcpyDeviceToHost));
        CHECK_CUDA(cudaMemcpy(h_steps, d_steps, NUM_INSTANCES * sizeof(int),
                              cudaMemcpyDeviceToHost));

        // Count successes
        int successes = 0;
        uint64_t first_factor = 0;
        int min_steps = MAX_STEPS, total_steps = 0;
        for (int i = 0; i < NUM_INSTANCES; i++) {
            if (h_results[i] > 0) {
                successes++;
                if (first_factor == 0) first_factor = h_results[i];
                if (h_steps[i] < min_steps) min_steps = h_steps[i];
            }
            total_steps += h_steps[i];
        }

        printf("  GPU: %.3f ms, %d/%d found factor, best in %d steps\n",
               ms, successes, NUM_INSTANCES, min_steps);
        if (first_factor > 0)
            printf("  Factor: %lu (verify: %lu / %lu = %lu)\n",
                   first_factor, n, first_factor, n / first_factor);
        printf("  Total steps: %d, avg: %d/instance\n", total_steps, total_steps / NUM_INSTANCES);

        // CPU reference (single instance, c=1)
        struct timespec ts1, ts2;
        clock_gettime(CLOCK_MONOTONIC, &ts1);
        int cpu_steps;
        uint64_t cpu_factor = cpu_pollard_rho(n, 1, &cpu_steps);
        clock_gettime(CLOCK_MONOTONIC, &ts2);
        double cpu_ms = (ts2.tv_sec - ts1.tv_sec) * 1000.0 +
                        (ts2.tv_nsec - ts1.tv_nsec) / 1e6;
        printf("  CPU (single): %.3f ms, %d steps, factor=%lu\n",
               cpu_ms, cpu_steps, cpu_factor);

        // Throughput comparison: GPU finds factor across 2560 instances
        // vs CPU running 2560 sequential instances
        printf("  Throughput speedup: GPU runs %d instances in %.3f ms\n",
               NUM_INSTANCES, ms);
        printf("  Estimated CPU sequential for %d instances: %.1f ms\n",
               NUM_INSTANCES, cpu_ms * NUM_INSTANCES);
        if (ms > 0 && cpu_ms > 0)
            printf("  Speedup: %.1fx\n", (cpu_ms * NUM_INSTANCES) / ms);
        printf("\n");
    }

    // Cleanup
    cudaFree(d_results); cudaFree(d_steps);
    free(h_results); free(h_steps);
    cudaEventDestroy(start); cudaEventDestroy(stop);
    return 0;
}
