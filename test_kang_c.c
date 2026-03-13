/* Test C kangaroo with k=16777199 (0xFFFFEF) */
#include <stdio.h>
#include <stdlib.h>
#include <gmp.h>

extern void ec_kang_init(const char *, const char *);
extern int ec_kang_solve(const char *, const char *, const char *, const char *,
                         const char *, char *, size_t);

int main(void) {
    ec_kang_init(
        "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F",
        "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141"
    );
    const char *Gx = "79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798";
    const char *Gy = "483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8";
    /* P = 16777199*G (0xFFFFEF) */
    const char *Px = "4AA1A838C9F74A7B70B736E75F3E1393780661B79C222DACE61DDFFB874253EA";
    const char *Py = "A836D8FF2176EE8F42B0C451E2252EB22201CEC309A8B240B4FE32CFADBA1E3D";
    /* bound = 2^25 = 33554432 = 0x2000000 */
    char result[256];
    printf("Testing kangaroo with k=16777199...\n");
    int ret = ec_kang_solve(Gx, Gy, Px, Py, "2000000", result, sizeof(result));
    printf("ret=%d\n", ret);
    if (ret) printf("k = 0x%s = %lu\n", result, strtoul(result, NULL, 16));
    return 0;
}
