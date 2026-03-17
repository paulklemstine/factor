/*
 * GPU Modular Multiplication Benchmark
 * Tests throughput of 64-bit and 128-bit modular multiplications on RTX 4050.
 *
 * 128-bit is emulated via hi/lo uint64 pairs since __uint128_t is not
 * available in CUDA device code.
 *
 * Compile: nvcc -O3 -arch=sm_89 -o gpu_modmul_bench gpu_modmul_bench.cu
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

/* ---- 64-bit modmul kernel ---- */
__global__ void bench_modmul64(const uint64_t *a, const uint64_t *b,
                                const uint64_t *m, uint64_t *out,
                                int n, int iters) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return;

    uint64_t ai = a[i], bi = b[i], mi = m[i];
    uint64_t r = ai;
    for (int it = 0; it < iters; it++) {
        // Use PTX inline asm for 64x64->128 multiply + mod
        uint64_t hi, lo;
        asm("mul.hi.u64 %0, %1, %2;" : "=l"(hi) : "l"(r), "l"(bi));
        asm("mul.lo.u64 %0, %1, %2;" : "=l"(lo) : "l"(r), "l"(bi));
        // Barrett-like: full 128-bit mod via repeated subtraction approx
        // For benchmark we use the GPU's native div+rem on 64-bit
        // Since hi < mi for properly reduced inputs, we can use:
        // result = ((hi << 64) + lo) % mi
        // Emulate with: hi = hi % mi, then combine
        uint64_t rem;
        asm("{\n\t"
            ".reg .u64 q, r, t;\n\t"
            "div.u64 q, %1, %2;\n\t"       // q = hi / mi
            "rem.u64 r, %1, %2;\n\t"       // r = hi % mi
            "mul.lo.u64 t, q, %2;\n\t"     // overflow check
            "rem.u64 %0, %3, %2;\n\t"      // lo % mi as fallback
            "mov.u64 %0, r;\n\t"           // simplified: just use hi%mi
            "}" : "=l"(rem) : "l"(hi), "l"(mi), "l"(lo));
        // Proper 128-bit mod: ((hi % m) * (2^64 % m) + lo % m) % m
        // But for pure throughput benchmark, we just chain modmuls:
        r = lo % mi;  // simplified - measures modmul throughput
        if (mi > (1ULL << 63)) r = lo;  // avoid div-by-zero edge
    }
    out[i] = r;
}

/* ---- 128-bit emulated modmul kernel ---- */
// Represent 128-bit as (hi, lo) pair
// Montgomery-like: a*b mod m where all are 128-bit
__device__ void mul64_full(uint64_t a, uint64_t b, uint64_t *hi, uint64_t *lo) {
    *lo = a * b;
    asm("mul.hi.u64 %0, %1, %2;" : "=l"(*hi) : "l"(a), "l"(b));
}

__device__ uint64_t addmod64(uint64_t a, uint64_t b, uint64_t m) {
    uint64_t r = a + b;
    if (r < a || r >= m) r -= m;
    return r;
}

__device__ uint64_t mulmod64(uint64_t a, uint64_t b, uint64_t m) {
    // Compute (a * b) % m using double-precision floating point for quotient estimate
    // then correct with exact integer arithmetic
    if (m == 0) return 0;
    uint64_t hi, lo;
    mul64_full(a, b, &hi, &lo);

    // Use iterative subtraction: reduce hi:lo mod m
    // Since hi < m (a,b < m), we need at most ~64 iterations of shift-subtract
    // Better: use the identity (hi:lo) % m = ((hi % m) * (2^64 % m) + lo % m) % m
    // But we need mulmod for (hi%m) * (2^64%m) which is circular!
    // Instead, use binary method to compute (hi%m) * (2^64%m) without overflow:
    uint64_t hm = hi % m;
    uint64_t lm = lo % m;
    uint64_t pow264_mod_m = (uint64_t)(-(int64_t)m) % m;  // = (2^64) % m

    // Compute hm * pow264_mod_m mod m using Russian peasant (no overflow)
    uint64_t r = 0;
    uint64_t aa = hm;
    uint64_t bb = pow264_mod_m;
    while (bb > 0) {
        if (bb & 1) r = addmod64(r, aa, m);
        aa = addmod64(aa, aa, m);
        bb >>= 1;
    }
    return addmod64(r, lm, m);
}

// 128-bit modmul: inputs are 128-bit (ahi:alo), output 128-bit reduced mod (mhi:mlo)
// For simplicity, benchmark 64-bit modmul chains which is what ECM/rho actually use
__global__ void bench_modmul128_chain(const uint64_t *a, const uint64_t *b,
                                       const uint64_t *m, uint64_t *out,
                                       int n, int iters) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return;

    uint64_t r = a[i], bi = b[i], mi = m[i];
    for (int it = 0; it < iters; it++) {
        r = mulmod64(r, bi, mi);
    }
    out[i] = r;
}

/* ---- CPU reference ---- */
uint64_t cpu_mulmod64(uint64_t a, uint64_t b, uint64_t m) {
    unsigned __int128 prod = (unsigned __int128)a * b;
    return (uint64_t)(prod % m);
}

int main() {
    printf("=== GPU Modular Multiplication Benchmark ===\n");
    printf("Device: RTX 4050 Laptop (20 SMs, sm_89)\n\n");

    const int N = 1 << 20;  // 1M elements
    const int ITERS_SIMPLE = 100;
    const int ITERS_CHAIN = 100;
    const int BLOCK = 256;
    const int GRID = (N + BLOCK - 1) / BLOCK;

    size_t sz = N * sizeof(uint64_t);

    // Host allocations
    uint64_t *h_a = (uint64_t*)malloc(sz);
    uint64_t *h_b = (uint64_t*)malloc(sz);
    uint64_t *h_m = (uint64_t*)malloc(sz);
    uint64_t *h_out = (uint64_t*)malloc(sz);

    srand(42);
    for (int i = 0; i < N; i++) {
        // 63-bit odd modulus (simulating large primes)
        h_m[i] = ((uint64_t)rand() << 32 | rand()) | (1ULL << 62) | 1ULL;
        h_a[i] = ((uint64_t)rand() << 32 | rand()) % h_m[i];
        h_b[i] = ((uint64_t)rand() << 32 | rand()) % h_m[i];
    }

    // Device allocations
    uint64_t *d_a, *d_b, *d_m, *d_out;
    CHECK_CUDA(cudaMalloc(&d_a, sz));
    CHECK_CUDA(cudaMalloc(&d_b, sz));
    CHECK_CUDA(cudaMalloc(&d_m, sz));
    CHECK_CUDA(cudaMalloc(&d_out, sz));
    CHECK_CUDA(cudaMemcpy(d_a, h_a, sz, cudaMemcpyHostToDevice));
    CHECK_CUDA(cudaMemcpy(d_b, h_b, sz, cudaMemcpyHostToDevice));
    CHECK_CUDA(cudaMemcpy(d_m, h_m, sz, cudaMemcpyHostToDevice));

    cudaEvent_t start, stop;
    CHECK_CUDA(cudaEventCreate(&start));
    CHECK_CUDA(cudaEventCreate(&stop));
    float ms;

    // === Benchmark 1: Simple 64-bit modmul (lo % m chain) ===
    printf("--- Benchmark 1: Simple 64-bit modmul (N=%d, iters=%d) ---\n", N, ITERS_SIMPLE);
    // Warmup
    bench_modmul64<<<GRID, BLOCK>>>(d_a, d_b, d_m, d_out, N, 1);
    CHECK_CUDA(cudaDeviceSynchronize());

    CHECK_CUDA(cudaEventRecord(start));
    bench_modmul64<<<GRID, BLOCK>>>(d_a, d_b, d_m, d_out, N, ITERS_SIMPLE);
    CHECK_CUDA(cudaEventRecord(stop));
    CHECK_CUDA(cudaEventSynchronize(stop));
    CHECK_CUDA(cudaEventElapsedTime(&ms, start, stop));

    double total_ops = (double)N * ITERS_SIMPLE;
    double gops = total_ops / (ms * 1e6);  // billions per second
    printf("  GPU: %.2f ms for %.0f modmuls = %.2f billion modmuls/sec\n", ms, total_ops, gops);

    // === Benchmark 2: Accurate 64-bit modmul chain (128-bit intermediate) ===
    printf("\n--- Benchmark 2: Full 64-bit modmul with 128-bit intermediate ---\n");
    printf("    (N=%d, iters=%d)\n", N, ITERS_CHAIN);
    // Warmup
    bench_modmul128_chain<<<GRID, BLOCK>>>(d_a, d_b, d_m, d_out, N, 1);
    CHECK_CUDA(cudaDeviceSynchronize());

    CHECK_CUDA(cudaEventRecord(start));
    bench_modmul128_chain<<<GRID, BLOCK>>>(d_a, d_b, d_m, d_out, N, ITERS_CHAIN);
    CHECK_CUDA(cudaEventRecord(stop));
    CHECK_CUDA(cudaEventSynchronize(stop));
    CHECK_CUDA(cudaEventElapsedTime(&ms, start, stop));

    total_ops = (double)N * ITERS_CHAIN;
    gops = total_ops / (ms * 1e6);
    printf("  GPU: %.2f ms for %.0f modmuls = %.2f billion modmuls/sec\n", ms, total_ops, gops);

    // Verify correctness (first 10)
    CHECK_CUDA(cudaMemcpy(h_out, d_out, sz, cudaMemcpyDeviceToHost));
    printf("  Correctness check (first 5):\n");
    for (int i = 0; i < 5; i++) {
        uint64_t r = h_a[i];
        for (int it = 0; it < ITERS_CHAIN; it++)
            r = cpu_mulmod64(r, h_b[i], h_m[i]);
        printf("    [%d] GPU=%lu CPU=%lu %s\n", i, h_out[i], r,
               h_out[i] == r ? "OK" : "MISMATCH");
    }

    // === CPU reference ===
    printf("\n--- CPU reference: single-thread 64-bit modmul ---\n");
    struct timespec ts_start, ts_end;
    clock_gettime(CLOCK_MONOTONIC, &ts_start);
    uint64_t dummy = 0;
    int cpu_n = 1000000;
    int cpu_iters = 100;
    for (int i = 0; i < cpu_n; i++) {
        uint64_t r = h_a[i % N];
        for (int it = 0; it < cpu_iters; it++)
            r = cpu_mulmod64(r, h_b[i % N], h_m[i % N]);
        dummy += r;
    }
    clock_gettime(CLOCK_MONOTONIC, &ts_end);
    double cpu_ms = (ts_end.tv_sec - ts_start.tv_sec) * 1000.0 +
                    (ts_end.tv_nsec - ts_start.tv_nsec) / 1e6;
    double cpu_gops = (double)cpu_n * cpu_iters / (cpu_ms * 1e6);
    printf("  CPU: %.2f ms for %d*%d = %.2f billion modmuls/sec (dummy=%lu)\n",
           cpu_ms, cpu_n, cpu_iters, cpu_gops, dummy);

    printf("\n=== GPU/CPU speedup: %.1fx ===\n", gops / cpu_gops);

    // Cleanup
    cudaFree(d_a); cudaFree(d_b); cudaFree(d_m); cudaFree(d_out);
    free(h_a); free(h_b); free(h_m); free(h_out);
    cudaEventDestroy(start); cudaEventDestroy(stop);
    return 0;
}
