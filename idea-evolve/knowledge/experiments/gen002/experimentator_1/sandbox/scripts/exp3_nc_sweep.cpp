/*
 * Experiment 3: NC sweep
 * Question: What is the optimal NC for each benchmark size?
 * Control: same micro-kernel, same data, only NC varies
 * NC values: 64, 128, 192, 256, 384, 512, 1024, m (no tiling)
 */
#include <immintrin.h>
#include <stdint.h>
#include <string.h>
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <time.h>

static double get_time_us() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1e6 + ts.tv_nsec / 1000.0;
}

static void encodeTern(int* A, uint8_t* Anew, int n, int m) {
    memset(Anew, 0, n * (m/8) * 2);
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++) {
            int ind = (i * m + j) / 8, off = (i * m + j) % 8;
            Anew[2 * ind] |= (A[i * m + j] == 1) << off;
            Anew[2 * ind + 1] |= (A[i * m + j] == -1) << off;
        }
}

static void encodeBinT(int* B, uint8_t* Bnew, int n, int m) {
    memset(Bnew, 0, (n/8) * m);
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++) {
            int ind = (i / 8) * m + j, off = i % 8;
            Bnew[ind] |= (B[i * m + j] == -1) << off;
        }
}

static void gemmV0_encoded(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    int k_bytes = k / 8;
    memset(C, 0, n * m * sizeof(int));
    for (int i = 0; i < n; i++)
        for (int t = 0; t < k_bytes; t++)
            for (int j = 0; j < m; j++) {
                uint8_t a0 = A[(i * k_bytes + t) * 2];
                uint8_t a1 = A[(i * k_bytes + t) * 2 + 1];
                uint8_t b = B[t * m + j];
                C[i * m + j] += __builtin_popcount((a0 | b) & (a1 | ~b));
                C[i * m + j] -= __builtin_popcount((a0 | ~b) & (a1 | b));
            }
}

#define MC 64

static void pack_A(int mc, int kc, const uint8_t* A, int k_bytes, uint8_t* Ap) {
    for (int i = 0; i < mc; i += 4) {
        int rmax = mc-i; if (rmax>4) rmax=4;
        for (int k = 0; k < kc; ++k)
            for (int r = 0; r < 4; ++r) {
                if (r < rmax) {
                    Ap[((i/4)*kc+k)*8+r*2]   = A[((i+r)*k_bytes+k)*2];
                    Ap[((i/4)*kc+k)*8+r*2+1] = A[((i+r)*k_bytes+k)*2+1];
                } else {
                    Ap[((i/4)*kc+k)*8+r*2] = Ap[((i/4)*kc+k)*8+r*2+1] = 0;
                }
            }
    }
}

static void pack_B(int kc, int nc, const uint8_t* B, int m, uint8_t* Bp) {
    for (int j = 0; j < nc; j += 64) {
        int cmax = nc-j;
        uint8_t* dst = Bp + (j/64)*kc*64;
        if (cmax >= 64) {
            for (int k = 0; k < kc; ++k)
                _mm512_storeu_si512((__m512i*)(dst+k*64),
                    _mm512_loadu_si512((const __m512i*)(B+k*m+j)));
        } else {
            __mmask64 mask = ((__mmask64)1 << cmax) - 1;
            for (int k = 0; k < kc; ++k)
                _mm512_storeu_si512((__m512i*)(dst+k*64),
                    _mm512_maskz_loadu_epi8(mask, (const __m512i*)(B+k*m+j)));
        }
    }
}

static inline void micro_kernel(
    int kc, const uint8_t* __restrict__ A_p,
    const uint8_t* __restrict__ B_p,
    int* __restrict__ C, int m, int cur_mc, int cur_nc
) {
    __m512i acc[4][2];
    for (int r = 0; r < 4; ++r) acc[r][0] = acc[r][1] = _mm512_setzero_si512();
    #pragma GCC unroll 7
    for (int k = 0; k < kc; ++k) {
        __m512i vb = _mm512_loadu_si512((const __m512i*)(B_p+k*64));
        const uint8_t* a = A_p+k*8;
        for (int r = 0; r < 4; ++r) {
            __m512i vp = _mm512_set1_epi8((int8_t)a[r*2]);
            __m512i vn = _mm512_set1_epi8((int8_t)a[r*2+1]);
            __m512i diff = _mm512_sub_epi8(
                _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp, vn, vb, 0xD8)),
                _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp, vn, vb, 0xE4))
            );
            acc[r][0] = _mm512_add_epi16(acc[r][0], _mm512_cvtepi8_epi16(_mm512_castsi512_si256(diff)));
            acc[r][1] = _mm512_add_epi16(acc[r][1], _mm512_cvtepi8_epi16(_mm512_extracti32x8_epi32(diff,1)));
        }
    }
    if (cur_nc == 64 && cur_mc == 4) {
        for (int r = 0; r < 4; ++r) {
            int* Cr = C+r*m;
            _mm512_storeu_si512((__m512i*)(Cr+ 0), _mm512_cvtepi16_epi32(_mm512_castsi512_si256(acc[r][0])));
            _mm512_storeu_si512((__m512i*)(Cr+16), _mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(acc[r][0],1)));
            _mm512_storeu_si512((__m512i*)(Cr+32), _mm512_cvtepi16_epi32(_mm512_castsi512_si256(acc[r][1])));
            _mm512_storeu_si512((__m512i*)(Cr+48), _mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(acc[r][1],1)));
        }
    } else {
        for (int r = 0; r < cur_mc; ++r) {
            int32_t tmp[64];
            _mm512_storeu_si512((__m512i*)&tmp[ 0], _mm512_cvtepi16_epi32(_mm512_castsi512_si256(acc[r][0])));
            _mm512_storeu_si512((__m512i*)&tmp[16], _mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(acc[r][0],1)));
            _mm512_storeu_si512((__m512i*)&tmp[32], _mm512_cvtepi16_epi32(_mm512_castsi512_si256(acc[r][1])));
            _mm512_storeu_si512((__m512i*)&tmp[48], _mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(acc[r][1],1)));
            for (int c = 0; c < cur_nc; ++c) C[r*m+c] = tmp[c];
        }
    }
}

void gemmWithNC(uint8_t* A, uint8_t* B, int* C, int n, int m, int k, int NC_val) {
    int k_bytes = k/8;
    // Dynamic Bp allocation for large NC
    int bp_size = (NC_val / 64) * k_bytes * 64;
    if (bp_size < 64) bp_size = 64;
    uint8_t* Bp = (uint8_t*)_mm_malloc(bp_size + 4096, 64);
    alignas(64) uint8_t Ap[4096];

    for (int jc = 0; jc < m; jc += NC_val) {
        int cnc = m-jc; if (cnc>NC_val) cnc=NC_val;
        pack_B(k_bytes, cnc, B+jc, m, Bp);
        for (int ic = 0; ic < n; ic += MC) {
            int cmc = n-ic; if (cmc>MC) cmc=MC;
            pack_A(cmc, k_bytes, A+(ic*k_bytes)*2, k_bytes, Ap);
            for (int jr = 0; jr < cnc; jr += 64) {
                int mnc = cnc-jr; if (mnc>64) mnc=64;
                for (int ir = 0; ir < cmc; ir += 4) {
                    int mmc = cmc-ir; if (mmc>4) mmc=4;
                    micro_kernel(k_bytes, Ap+(ir/4)*k_bytes*8, Bp+(jr/64)*k_bytes*64,
                        C+(ic+ir)*m+(jc+jr), m, mmc, mnc);
                }
            }
        }
    }
    _mm_free(Bp);
}

static void gen_ternary(int* A, int n, int k, unsigned seed) {
    srand(seed); for (int i = 0; i < n * k; i++) A[i] = (rand() % 3) - 1;
}
static void gen_binary(int* B, int k, int m, unsigned seed) {
    srand(seed); for (int i = 0; i < k * m; i++) B[i] = (rand() % 2) * 2 - 1;
}

struct BenchSize { int n, m, k_raw; const char* name; };

static double benchmark_nc(int nc, uint8_t* A, uint8_t* B, int* C, int n, int m, int k, int reps) {
    for (int w = 0; w < 3; w++) gemmWithNC(A, B, C, n, m, k, nc);
    double times[100];
    for (int r = 0; r < reps; r++) {
        double t0 = get_time_us();
        gemmWithNC(A, B, C, n, m, k, nc);
        double t1 = get_time_us();
        times[r] = t1 - t0;
    }
    std::sort(times, times + reps);
    return times[reps / 2];
}

int main() {
    BenchSize sizes[] = {
        {32,  1024,   9,  "small"},
        {64,  16384,  27, "medium"},
        {128, 65536,  54, "large"},
    };

    int nc_values[] = {64, 128, 192, 256, 384, 512, 1024};
    int n_nc = sizeof(nc_values) / sizeof(nc_values[0]);
    int REPS = 15;

    printf("%-8s", "NC");
    for (int s = 0; s < 3; s++) printf("  %12s", sizes[s].name);
    printf("  %12s\n", "geomean");
    printf("%-8s", "----");
    for (int s = 0; s < 4; s++) printf("  %12s", "--------");
    printf("\n");

    for (int nc_idx = 0; nc_idx < n_nc; nc_idx++) {
        int nc = nc_values[nc_idx];
        printf("%-8d", nc);
        double times[3];

        for (int s = 0; s < 3; s++) {
            int n = sizes[s].n, m = sizes[s].m, k_raw = sizes[s].k_raw;
            int k = 8 * (k_raw / 8 + 1), k_bytes = k / 8;

            if (nc > m) { printf("  %10.2f µs", 0.0); times[s] = 0; continue; }

            int* A_int = (int*)calloc(n * k, sizeof(int));
            int* B_int = (int*)calloc(k * m, sizeof(int));
            uint8_t* A_enc = (uint8_t*)calloc(n * k_bytes * 2, 1);
            uint8_t* B_enc = (uint8_t*)calloc(k_bytes * m, 1);
            int* C = (int*)_mm_malloc(n * m * sizeof(int), 64);

            gen_ternary(A_int, n, k, 42);
            gen_binary(B_int, k, m, 123);
            encodeTern(A_int, A_enc, n, k);
            encodeBinT(B_int, B_enc, k, m);

            double t = benchmark_nc(nc, A_enc, B_enc, C, n, m, k, REPS);
            times[s] = t;
            printf("  %10.2f µs", t);

            free(A_int); free(B_int); free(A_enc); free(B_enc); _mm_free(C);
        }

        // Geomean of all 3
        if (times[0] > 0 && times[1] > 0 && times[2] > 0) {
            double gm = exp((log(times[0]) + log(times[1]) + log(times[2])) / 3.0);
            printf("  %10.2f µs", gm);
        }
        printf("\n");
    }

    // Also test NC = m (no NC tiling at all) for each size
    printf("\n--- NC = m (no tiling) ---\n");
    for (int s = 0; s < 3; s++) {
        int n = sizes[s].n, m = sizes[s].m, k_raw = sizes[s].k_raw;
        int k = 8 * (k_raw / 8 + 1), k_bytes = k / 8;

        int* A_int = (int*)calloc(n * k, sizeof(int));
        int* B_int = (int*)calloc(k * m, sizeof(int));
        uint8_t* A_enc = (uint8_t*)calloc(n * k_bytes * 2, 1);
        uint8_t* B_enc = (uint8_t*)calloc(k_bytes * m, 1);
        int* C = (int*)_mm_malloc(n * m * sizeof(int), 64);

        gen_ternary(A_int, n, k, 42);
        gen_binary(B_int, k, m, 123);
        encodeTern(A_int, A_enc, n, k);
        encodeBinT(B_int, B_enc, k, m);

        double t = benchmark_nc(m, A_enc, B_enc, C, n, m, k, REPS);
        printf("  %s (NC=%d): %10.2f µs\n", sizes[s].name, m, t);

        free(A_int); free(B_int); free(A_enc); free(B_enc); _mm_free(C);
    }

    return 0;
}
