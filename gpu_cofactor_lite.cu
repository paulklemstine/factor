/*
 * gpu_cofactor_lite.cu — Lightweight GPU batch smooth/partial detection.
 * Only returns smooth_flags + cofactors (NOT exponent bits).
 * The caller re-does trial division on CPU only for the ~5% that are smooth.
 * This eliminates the 64MB exponent transfer bottleneck.
 *
 * Compile: nvcc -O3 -arch=sm_89 --shared -Xcompiler -fPIC -o gpu_cofactor_lite.so gpu_cofactor_lite.cu
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <cuda_runtime.h>

#define MAX_FB 8192

__constant__ uint32_t d_fb[MAX_FB];
__constant__ int d_fb_size;

static uint64_t *d_candidates = NULL;
static uint64_t *d_cofactors = NULL;
static int *d_smooth = NULL;
static int d_alloc_size = 0;

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

__device__ int is_probable_prime(uint64_t n) {
    if (n < 2) return 0;
    if (n < 4) return 1;
    if (n % 2 == 0) return 0;
    uint64_t d = n - 1;
    int r = 0;
    while ((d & 1) == 0) { d >>= 1; r++; }
    uint64_t witnesses[] = {2, 3, 5, 7, 11, 13};
    for (int w = 0; w < 6; w++) {
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
 * Lightweight kernel: trial divide, return only smooth flag + cofactor.
 * No exponent bits — those are reconstructed on CPU for the few smooth hits.
 */
__global__ void batch_check_smooth(
    const uint64_t *candidates, int num_candidates,
    uint64_t *cofactors, int *smooth_flags,
    uint64_t lp_bound
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= num_candidates) return;

    uint64_t val = candidates[idx];
    if (val == 0) { smooth_flags[idx] = 0; cofactors[idx] = 0; return; }

    int fb_size = d_fb_size;

    for (int i = 0; i < fb_size; i++) {
        uint32_t p = d_fb[i];
        if (p == 0) break;
        while (val % p == 0) val /= p;
        if (val == 1) break;
    }

    cofactors[idx] = val;
    if (val == 1) {
        smooth_flags[idx] = 1;   /* fully smooth */
    } else if (val <= lp_bound && is_probable_prime(val)) {
        smooth_flags[idx] = 2;   /* single large prime */
    } else if (val <= lp_bound * lp_bound) {
        smooth_flags[idx] = 3;   /* possible DLP candidate */
    } else {
        smooth_flags[idx] = 0;   /* not smooth */
    }
}

extern "C" {

int gpu_lite_init() {
    int count;
    cudaError_t err = cudaGetDeviceCount(&count);
    if (err != cudaSuccess || count == 0) return -1;
    cudaSetDevice(0);
    return 0;
}

int gpu_lite_set_fb(const uint32_t *fb, int fb_size) {
    if (fb_size > MAX_FB) fb_size = MAX_FB;
    cudaError_t e1 = cudaMemcpyToSymbol(d_fb, fb, fb_size * sizeof(uint32_t));
    cudaError_t e2 = cudaMemcpyToSymbol(d_fb_size, &fb_size, sizeof(int));
    if (e1 != cudaSuccess || e2 != cudaSuccess) return -1;
    return 0;
}

static int ensure_alloc(int n) {
    if (n <= d_alloc_size) return 0;
    if (d_candidates) cudaFree(d_candidates);
    if (d_cofactors) cudaFree(d_cofactors);
    if (d_smooth) cudaFree(d_smooth);
    int nn = ((n + 255) / 256) * 256;
    if (cudaMalloc(&d_candidates, nn * sizeof(uint64_t)) != cudaSuccess) return -1;
    if (cudaMalloc(&d_cofactors, nn * sizeof(uint64_t)) != cudaSuccess) return -1;
    if (cudaMalloc(&d_smooth, nn * sizeof(int)) != cudaSuccess) return -1;
    d_alloc_size = nn;
    return 0;
}

int gpu_lite_batch(const uint64_t *cands, int n,
    uint64_t *h_cofactors, int *h_smooth, uint64_t lp_bound)
{
    if (ensure_alloc(n) != 0) return -1;

    cudaMemcpy(d_candidates, cands, n * sizeof(uint64_t), cudaMemcpyHostToDevice);

    int block = 256;
    int grid = (n + block - 1) / block;
    batch_check_smooth<<<grid, block>>>(d_candidates, n,
        d_cofactors, d_smooth, lp_bound);

    cudaError_t err = cudaDeviceSynchronize();
    if (err != cudaSuccess) return -1;

    cudaMemcpy(h_cofactors, d_cofactors, n * sizeof(uint64_t), cudaMemcpyDeviceToHost);
    cudaMemcpy(h_smooth, d_smooth, n * sizeof(int), cudaMemcpyDeviceToHost);

    return 0;
}

void gpu_lite_cleanup() {
    if (d_candidates) { cudaFree(d_candidates); d_candidates = NULL; }
    if (d_cofactors) { cudaFree(d_cofactors); d_cofactors = NULL; }
    if (d_smooth) { cudaFree(d_smooth); d_smooth = NULL; }
    d_alloc_size = 0;
}

} /* extern "C" */
