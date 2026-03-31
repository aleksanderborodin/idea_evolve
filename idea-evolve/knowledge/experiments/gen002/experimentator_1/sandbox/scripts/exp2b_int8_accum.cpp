/*
 * Experiment 2b: int8 accumulation vs int16 accumulation
 * Question: Does accumulating in int8 (deferring widening to after k-loop) improve throughput?
 * k_bytes ≤ 7, max accumulated value = ±8*7 = ±56, fits in int8 (-128..127)
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
#define NC 256

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

// CURRENT: int16 accumulation (as in best.py)
static inline void micro_kernel_int16(
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

// NEW: int8 accumulation (defer ALL widening to after k-loop)
static inline void micro_kernel_int8(
    int kc, const uint8_t* __restrict__ A_p,
    const uint8_t* __restrict__ B_p,
    int* __restrict__ C, int m, int cur_mc, int cur_nc
) {
    // 4 rows × 1 zmm each (64 bytes of int8 accumulators per row)
    __m512i acc[4];
    for (int r = 0; r < 4; ++r) acc[r] = _mm512_setzero_si512();

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
            acc[r] = _mm512_add_epi8(acc[r], diff);
        }
    }

    // Post-loop: widen int8 → int32 and store
    // Each zmm has 64 int8 values → need 4 zmm of int32 per row
    if (cur_nc == 64 && cur_mc == 4) {
        for (int r = 0; r < 4; ++r) {
            int* Cr = C + r * m;
            // Extract 4 groups of 16 bytes, sign-extend each to 16 int32s
            __m128i lo16 = _mm512_castsi512_si128(acc[r]);        // bytes 0-15
            __m128i hi16 = _mm512_extracti32x4_epi32(acc[r], 1); // bytes 16-31
            __m128i lo16b = _mm512_extracti32x4_epi32(acc[r], 2); // bytes 32-47
            __m128i hi16b = _mm512_extracti32x4_epi32(acc[r], 3); // bytes 48-63

            _mm512_storeu_si512((__m512i*)(Cr +  0), _mm512_cvtepi8_epi32(lo16));
            _mm512_storeu_si512((__m512i*)(Cr + 16), _mm512_cvtepi8_epi32(hi16));
            _mm512_storeu_si512((__m512i*)(Cr + 32), _mm512_cvtepi8_epi32(lo16b));
            _mm512_storeu_si512((__m512i*)(Cr + 48), _mm512_cvtepi8_epi32(hi16b));
        }
    } else {
        for (int r = 0; r < cur_mc; ++r) {
            int32_t tmp[64];
            __m128i lo16 = _mm512_castsi512_si128(acc[r]);
            __m128i hi16 = _mm512_extracti32x4_epi32(acc[r], 1);
            __m128i lo16b = _mm512_extracti32x4_epi32(acc[r], 2);
            __m128i hi16b = _mm512_extracti32x4_epi32(acc[r], 3);
            _mm512_storeu_si512((__m512i*)&tmp[ 0], _mm512_cvtepi8_epi32(lo16));
            _mm512_storeu_si512((__m512i*)&tmp[16], _mm512_cvtepi8_epi32(hi16));
            _mm512_storeu_si512((__m512i*)&tmp[32], _mm512_cvtepi8_epi32(lo16b));
            _mm512_storeu_si512((__m512i*)&tmp[48], _mm512_cvtepi8_epi32(hi16b));
            for (int c = 0; c < cur_nc; ++c) C[r*m+c] = tmp[c];
        }
    }
}

typedef void (*ukernel_fn)(int, const uint8_t*, const uint8_t*, int*, int, int, int);

void gemmWithKernel(ukernel_fn kern, uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    int k_bytes = k/8;
    alignas(64) uint8_t Ap[4096], Bp[8192];
    for (int jc = 0; jc < m; jc += NC) {
        int cnc = m-jc; if (cnc>NC) cnc=NC;
        pack_B(k_bytes, cnc, B+jc, m, Bp);
        for (int ic = 0; ic < n; ic += MC) {
            int cmc = n-ic; if (cmc>MC) cmc=MC;
            pack_A(cmc, k_bytes, A+(ic*k_bytes)*2, k_bytes, Ap);
            for (int jr = 0; jr < cnc; jr += 64) {
                int mnc = cnc-jr; if (mnc>64) mnc=64;
                for (int ir = 0; ir < cmc; ir += 4) {
                    int mmc = cmc-ir; if (mmc>4) mmc=4;
                    kern(k_bytes, Ap+(ir/4)*k_bytes*8, Bp+(jr/64)*k_bytes*64,
                        C+(ic+ir)*m+(jc+jr), m, mmc, mnc);
                }
            }
        }
    }
}

static void gen_ternary(int* A, int n, int k, unsigned seed) {
    srand(seed); for (int i = 0; i < n * k; i++) A[i] = (rand() % 3) - 1;
}
static void gen_binary(int* B, int k, int m, unsigned seed) {
    srand(seed); for (int i = 0; i < k * m; i++) B[i] = (rand() % 2) * 2 - 1;
}

struct BenchSize { int n, m, k_raw; const char* name; };

int main() {
    BenchSize sizes[] = {
        {32,  1024,   9,  "small"},
        {64,  16384,  27, "medium"},
        {128, 65536,  54, "large"},
    };
    int REPS = 21;

    for (int s = 0; s < 3; s++) {
        int n = sizes[s].n, m = sizes[s].m, k_raw = sizes[s].k_raw;
        int k = 8 * (k_raw / 8 + 1), k_bytes = k / 8;
        printf("=== %s: n=%d, m=%d, k=%d (k_bytes=%d) ===\n", sizes[s].name, n, m, k, k_bytes);

        int* A_int = (int*)calloc(n * k, sizeof(int));
        int* B_int = (int*)calloc(k * m, sizeof(int));
        uint8_t* A_enc = (uint8_t*)calloc(n * k_bytes * 2, 1);
        uint8_t* B_enc = (uint8_t*)calloc(k_bytes * m, 1);
        int* C_ref = (int*)calloc(n * m, sizeof(int));
        int* C_test = (int*)_mm_malloc(n * m * sizeof(int), 64);

        gen_ternary(A_int, n, k, 42);
        gen_binary(B_int, k, m, 123);
        encodeTern(A_int, A_enc, n, k);
        encodeBinT(B_int, B_enc, k, m);

        // Correctness check for int8 accumulation
        gemmV0_encoded(A_enc, B_enc, C_ref, n, m, k);
        gemmWithKernel(micro_kernel_int8, A_enc, B_enc, C_test, n, m, k);
        int mismatches = 0;
        for (int i = 0; i < n * m; i++)
            if (C_ref[i] != C_test[i]) mismatches++;
        printf("  int8 correctness: %s (%d mismatches)\n", mismatches ? "FAIL" : "PASS", mismatches);

        // Benchmark both
        // Warmup
        for (int w = 0; w < 5; w++) {
            gemmWithKernel(micro_kernel_int16, A_enc, B_enc, C_test, n, m, k);
            gemmWithKernel(micro_kernel_int8, A_enc, B_enc, C_test, n, m, k);
        }

        double times16[100], times8[100];
        for (int r = 0; r < REPS; r++) {
            double t0 = get_time_us();
            gemmWithKernel(micro_kernel_int16, A_enc, B_enc, C_test, n, m, k);
            double t1 = get_time_us();
            gemmWithKernel(micro_kernel_int8, A_enc, B_enc, C_test, n, m, k);
            double t2 = get_time_us();
            times16[r] = t1 - t0;
            times8[r] = t2 - t1;
        }
        std::sort(times16, times16 + REPS);
        std::sort(times8, times8 + REPS);
        double t16 = times16[REPS/2], t8 = times8[REPS/2];

        printf("  int16 accum: %10.2f µs\n", t16);
        printf("  int8 accum:  %10.2f µs (%.2fx)\n", t8, t16 / t8);
        printf("\n");

        free(A_int); free(B_int); free(A_enc); free(B_enc); free(C_ref); _mm_free(C_test);
    }
    return 0;
}
