# fitness: 318.96

"""
No-packing, B-panel in zmm registers via template<int KB>, int8 accumulators.

Fix over sol01: B_reg[128] on stack was preventing register promotion.
With template<KB> and always_inline, B_reg[KB] maps to KB zmm registers for KB<=7.
int8 accumulators (safe for KB<=15 since max |sum|=KB*8<=56<127) halve
accumulator pressure: 8 acc + 7 B_reg = 15 zmm (fits in 32).
"""


def entrypoint() -> str:
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>
#include <algorithm>

template<int KB>
static __attribute__((always_inline)) inline
void gemm_core(const uint8_t* __restrict__ A, const uint8_t* __restrict__ B,
               int* __restrict__ C, int n, int m) {
    for (int jc = 0; jc < m; jc += 64) {
        // With KB a compile-time constant <= 7, compiler allocates B_reg as zmm registers.
        __m512i B_reg[KB];
        #pragma GCC unroll 8
        for (int t = 0; t < KB; t++)
            B_reg[t] = _mm512_loadu_si512((const __m512i*)(B + (size_t)t * m + jc));

        // 8-row batches with int8 accumulators.
        int ic = 0;
        for (; ic + 8 <= n; ic += 8) {
            __m512i acc0 = _mm512_setzero_si512();
            __m512i acc1 = _mm512_setzero_si512();
            __m512i acc2 = _mm512_setzero_si512();
            __m512i acc3 = _mm512_setzero_si512();
            __m512i acc4 = _mm512_setzero_si512();
            __m512i acc5 = _mm512_setzero_si512();
            __m512i acc6 = _mm512_setzero_si512();
            __m512i acc7 = _mm512_setzero_si512();

            const uint8_t* r0 = A + (size_t)(ic + 0) * KB * 2;
            const uint8_t* r1 = A + (size_t)(ic + 1) * KB * 2;
            const uint8_t* r2 = A + (size_t)(ic + 2) * KB * 2;
            const uint8_t* r3 = A + (size_t)(ic + 3) * KB * 2;
            const uint8_t* r4 = A + (size_t)(ic + 4) * KB * 2;
            const uint8_t* r5 = A + (size_t)(ic + 5) * KB * 2;
            const uint8_t* r6 = A + (size_t)(ic + 6) * KB * 2;
            const uint8_t* r7 = A + (size_t)(ic + 7) * KB * 2;

            #pragma GCC unroll 8
            for (int t = 0; t < KB; t++) {
                __m512i vb = B_reg[t];
#define DO_ROW(acc, ap) { \
    __m512i vp = _mm512_set1_epi8((int8_t)(ap)[t*2]);   \
    __m512i vn = _mm512_set1_epi8((int8_t)(ap)[t*2+1]); \
    acc = _mm512_add_epi8(acc, _mm512_sub_epi8(          \
        _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp, vn, vb, 0xD8)), \
        _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp, vn, vb, 0xE4)))); \
}
                DO_ROW(acc0, r0)
                DO_ROW(acc1, r1)
                DO_ROW(acc2, r2)
                DO_ROW(acc3, r3)
                DO_ROW(acc4, r4)
                DO_ROW(acc5, r5)
                DO_ROW(acc6, r6)
                DO_ROW(acc7, r7)
#undef DO_ROW
            }

            // Widen int8 -> int32 and store.
#define STORE(acc, row) { \
    int* Cr = C + (size_t)(ic + (row)) * m + jc; \
    _mm512_storeu_si512((__m512i*)(Cr +  0), _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc, 0))); \
    _mm512_storeu_si512((__m512i*)(Cr + 16), _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc, 1))); \
    _mm512_storeu_si512((__m512i*)(Cr + 32), _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc, 2))); \
    _mm512_storeu_si512((__m512i*)(Cr + 48), _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc, 3))); \
}
            STORE(acc0, 0) STORE(acc1, 1) STORE(acc2, 2) STORE(acc3, 3)
            STORE(acc4, 4) STORE(acc5, 5) STORE(acc6, 6) STORE(acc7, 7)
#undef STORE
        }
        // Remainder rows
        for (; ic < n; ic++) {
            __m512i acc = _mm512_setzero_si512();
            const uint8_t* ar = A + (size_t)ic * KB * 2;
            #pragma GCC unroll 8
            for (int t = 0; t < KB; t++) {
                __m512i vp = _mm512_set1_epi8((int8_t)ar[t * 2]);
                __m512i vn = _mm512_set1_epi8((int8_t)ar[t * 2 + 1]);
                acc = _mm512_add_epi8(acc, _mm512_sub_epi8(
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp, vn, B_reg[t], 0xD8)),
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp, vn, B_reg[t], 0xE4))));
            }
            int* Cr = C + (size_t)ic * m + jc;
            _mm512_storeu_si512((__m512i*)(Cr +  0), _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc, 0)));
            _mm512_storeu_si512((__m512i*)(Cr + 16), _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc, 1)));
            _mm512_storeu_si512((__m512i*)(Cr + 32), _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc, 2)));
            _mm512_storeu_si512((__m512i*)(Cr + 48), _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc, 3)));
        }
    }
}

// Generic int16 fallback for large k_bytes (correctness tests).
static void gemm_generic(const uint8_t* A, const uint8_t* B, int* C,
                         int n, int m, int k_bytes) {
    for (int jc = 0; jc < m; jc += 64) {
        for (int ic = 0; ic < n; ic++) {
            __m512i al = _mm512_setzero_si512(), ah = _mm512_setzero_si512();
            const uint8_t* ar = A + (size_t)ic * k_bytes * 2;
            for (int t = 0; t < k_bytes; t++) {
                __m512i vb = _mm512_loadu_si512((const __m512i*)(B + (size_t)t * m + jc));
                __m512i vp = _mm512_set1_epi8((int8_t)ar[t * 2]);
                __m512i vn = _mm512_set1_epi8((int8_t)ar[t * 2 + 1]);
                __m512i d = _mm512_sub_epi8(
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp, vn, vb, 0xD8)),
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp, vn, vb, 0xE4)));
                al = _mm512_add_epi16(al, _mm512_cvtepi8_epi16(_mm512_castsi512_si256(d)));
                ah = _mm512_add_epi16(ah, _mm512_cvtepi8_epi16(_mm512_extracti32x8_epi32(d, 1)));
            }
            int* Cr = C + (size_t)ic * m + jc;
            _mm512_storeu_si512((__m512i*)(Cr +  0), _mm512_cvtepi16_epi32(_mm512_castsi512_si256(al)));
            _mm512_storeu_si512((__m512i*)(Cr + 16), _mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(al, 1)));
            _mm512_storeu_si512((__m512i*)(Cr + 32), _mm512_cvtepi16_epi32(_mm512_castsi512_si256(ah)));
            _mm512_storeu_si512((__m512i*)(Cr + 48), _mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(ah, 1)));
        }
    }
}

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    int k_bytes = k / 8;
    switch (k_bytes) {
        case 2:  gemm_core<2>(A, B, C, n, m); break;
        case 4:  gemm_core<4>(A, B, C, n, m); break;
        case 7:  gemm_core<7>(A, B, C, n, m); break;
        default: gemm_generic(A, B, C, n, m, k_bytes); break;
    }
}
"""
