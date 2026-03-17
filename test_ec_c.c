/* Quick standalone test of the C rho */
#include <stdio.h>
#include <gmp.h>
#include <time.h>

extern void ec_rho_init(const char *p_hex, const char *order_hex);
extern int ec_rho_solve(const char *Gx, const char *Gy, const char *Px, const char *Py,
                        unsigned long max_steps, char *result, size_t result_size);

int main(void) {
    ec_rho_init(
        "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F",
        "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141"
    );

    /* P = 5*G for secp256k1 */
    /* G */
    const char *Gx = "79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798";
    const char *Gy = "483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8";
    /* 5*G (precomputed) */
    const char *Px = "2F8BDE4D1A07209355B4A7250A5C5128E88B84BDDC619AB7CBA8D569B240EFE4";
    const char *Py = "D8AC222636E5E3D6D4DBA9DDA6C9C426F788271BAB0D6840DCA87D3AA6AC62D6";

    char result[256];
    printf("Starting rho with 100000 steps...\n");
    fflush(stdout);

    clock_t t0 = clock();
    int ret = ec_rho_solve(Gx, Gy, Px, Py, 100000, result, sizeof(result));
    clock_t t1 = clock();

    printf("ret=%d, time=%.3fs\n", ret, (double)(t1-t0)/CLOCKS_PER_SEC);
    if (ret) printf("k = %s (hex) = 0x%s\n", result, result);
    return 0;
}
