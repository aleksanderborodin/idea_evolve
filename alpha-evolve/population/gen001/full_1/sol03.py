# fitness: 442.43
"""
Further optimizations over sol02:
1. Template-based k-loop unrolling for k_bytes=2,4,7 — compiler fully unrolls.
2. Dispatch at call site via switch(k_bytes).
3. NC=512 (aligned), streaming stores when C is 64-byte aligned.
Fixed: C indexing in inner loop now correctly includes jc offset.
"""


def entrypoint() -> str:
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>
#include <algorithm>

#define NC 512
#define MC 64

static void pack_B_avx512(int kc, int nc, const uint8_t* B_src, int m, uint8_t* B_packed) {
    for (int j = 0; j < nc; j += 64) {
        int cmax = std::min(64, nc - j);
        for (int k = 0; k < kc; ++k) {
            uint8_t* dst = &B_packed[(j / 64 * kc + k) * 64];
            const uint8_t* src = &B_src[k * m + j];
            if (cmax == 64) {
                _mm512_storeu_si512((void*)dst, _mm512_loadu_si512((const void*)src));
            } else {
                memcpy(dst, src, cmax);
                memset(dst + cmax, 0, 64 - cmax);
            }
        }
    }
}

static void pack_A_all(int n, int kc, const uint8_t* A_src, int k_bytes, uint8_t* A_packed) {
    for (int i = 0; i < n; i += 4) {
        int rmax = std::min(4, n - i);
        for (int k = 0; k < kc; ++k) {
            uint8_t* dst = &A_packed[(i / 4 * kc + k) * 8];
            for (int r = 0; r < 4; ++r) {
                if (r < rmax) {
                    dst[r*2]   = A_src[((i+r)*k_bytes+k)*2];
                    dst[r*2+1] = A_src[((i+r)*k_bytes+k)*2+1];
                } else {
                    dst[r*2] = dst[r*2+1] = 0;
                }
            }
        }
    }
}

#define WIDEN_I8_TO_I32(src, d0, d1, d2, d3) do { \
    d0 = _mm512_cvtepi8_epi32(_mm512_castsi512_si128(src)); \
    d1 = _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(src, 1)); \
    d2 = _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(src, 2)); \
    d3 = _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(src, 3)); \
} while(0)

// Templated 4x64 micro-kernel: KBYTES known at compile time → fully unrolled k-loop
template<int KBYTES, int USE_STREAM>
static __attribute__((always_inline)) inline
void micro_kernel_4x64(const uint8_t* __restrict__ A_p, const uint8_t* __restrict__ B_p,
                        int* __restrict__ C, int m, int cur_mc, int cur_nc) {
    __m512i acc0 = _mm512_setzero_si512();
    __m512i acc1 = _mm512_setzero_si512();
    __m512i acc2 = _mm512_setzero_si512();
    __m512i acc3 = _mm512_setzero_si512();
    const __m512i all_ones = _mm512_set1_epi8(-1);

    for (int k = 0; k < KBYTES; ++k) {
        __m512i v_b     = _mm512_loadu_si512((const void*)(B_p + k * 64));
        __m512i v_not_b = _mm512_xor_si512(v_b, all_ones);
        const uint8_t* a = A_p + k * 8;

        #define ACC_ROW(accN, ri) { \
            __m512i vap = _mm512_set1_epi8((int8_t)a[ri*2]); \
            __m512i van = _mm512_set1_epi8((int8_t)a[ri*2+1]); \
            __m512i up  = _mm512_and_si512(_mm512_or_si512(vap, v_b),     _mm512_or_si512(van, v_not_b)); \
            __m512i un  = _mm512_and_si512(_mm512_or_si512(vap, v_not_b), _mm512_or_si512(van, v_b)); \
            accN = _mm512_add_epi8(accN, _mm512_sub_epi8(_mm512_popcnt_epi8(up), _mm512_popcnt_epi8(un))); \
        }
        ACC_ROW(acc0, 0); ACC_ROW(acc1, 1); ACC_ROW(acc2, 2); ACC_ROW(acc3, 3);
        #undef ACC_ROW
    }

    if (__builtin_expect(cur_nc == 64 && cur_mc == 4, 1)) {
        __m512i r0_0, r0_1, r0_2, r0_3;
        __m512i r1_0, r1_1, r1_2, r1_3;
        __m512i r2_0, r2_1, r2_2, r2_3;
        __m512i r3_0, r3_1, r3_2, r3_3;
        WIDEN_I8_TO_I32(acc0, r0_0, r0_1, r0_2, r0_3);
        WIDEN_I8_TO_I32(acc1, r1_0, r1_1, r1_2, r1_3);
        WIDEN_I8_TO_I32(acc2, r2_0, r2_1, r2_2, r2_3);
        WIDEN_I8_TO_I32(acc3, r3_0, r3_1, r3_2, r3_3);

        if (USE_STREAM) {
            #define SS(r, v0, v1, v2, v3) { int* Cr = C + r*m; \
                _mm512_stream_si512((__m512i*)(Cr+ 0), v0); \
                _mm512_stream_si512((__m512i*)(Cr+16), v1); \
                _mm512_stream_si512((__m512i*)(Cr+32), v2); \
                _mm512_stream_si512((__m512i*)(Cr+48), v3); }
            SS(0, r0_0, r0_1, r0_2, r0_3);
            SS(1, r1_0, r1_1, r1_2, r1_3);
            SS(2, r2_0, r2_1, r2_2, r2_3);
            SS(3, r3_0, r3_1, r3_2, r3_3);
            #undef SS
        } else {
            #define US(r, v0, v1, v2, v3) { int* Cr = C + r*m; \
                _mm512_storeu_si512((void*)(Cr+ 0), v0); \
                _mm512_storeu_si512((void*)(Cr+16), v1); \
                _mm512_storeu_si512((void*)(Cr+32), v2); \
                _mm512_storeu_si512((void*)(Cr+48), v3); }
            US(0, r0_0, r0_1, r0_2, r0_3);
            US(1, r1_0, r1_1, r1_2, r1_3);
            US(2, r2_0, r2_1, r2_2, r2_3);
            US(3, r3_0, r3_1, r3_2, r3_3);
            #undef US
        }
    } else {
        __m512i* accs[4] = {&acc0, &acc1, &acc2, &acc3};
        int32_t temp[64];
        for (int r = 0; r < cur_mc; ++r) {
            __m512i d0, d1, d2, d3;
            WIDEN_I8_TO_I32(*accs[r], d0, d1, d2, d3);
            _mm512_storeu_si512((void*)&temp[ 0], d0);
            _mm512_storeu_si512((void*)&temp[16], d1);
            _mm512_storeu_si512((void*)&temp[32], d2);
            _mm512_storeu_si512((void*)&temp[48], d3);
            for (int c = 0; c < cur_nc; ++c)
                C[r * m + c] = temp[c];
        }
    }
}

// Generic fallback for non-benchmark k_bytes values (e.g. k_bytes=32 in correctness test)
static void micro_kernel_generic(int kc, const uint8_t* A_p, const uint8_t* B_p,
                                  int* C, int m, int cur_mc, int cur_nc) {
    // Use int32 accumulation for safety (kc could be large)
    __m512i acc[4][4];
    for (int r = 0; r < 4; ++r)
        acc[r][0] = acc[r][1] = acc[r][2] = acc[r][3] = _mm512_setzero_si512();
    const __m512i all_ones = _mm512_set1_epi8(-1);
    for (int k = 0; k < kc; ++k) {
        __m512i v_b     = _mm512_loadu_si512((const void*)(B_p + k * 64));
        __m512i v_not_b = _mm512_xor_si512(v_b, all_ones);
        const uint8_t* a = A_p + k * 8;
        for (int r = 0; r < 4; ++r) {
            __m512i vap = _mm512_set1_epi8((int8_t)a[r*2]);
            __m512i van = _mm512_set1_epi8((int8_t)a[r*2+1]);
            __m512i up  = _mm512_and_si512(_mm512_or_si512(vap, v_b),     _mm512_or_si512(van, v_not_b));
            __m512i un  = _mm512_and_si512(_mm512_or_si512(vap, v_not_b), _mm512_or_si512(van, v_b));
            __m512i diff = _mm512_sub_epi8(_mm512_popcnt_epi8(up), _mm512_popcnt_epi8(un));
            __m512i d0, d1, d2, d3;
            d0 = _mm512_cvtepi8_epi32(_mm512_castsi512_si128(diff));
            d1 = _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(diff, 1));
            d2 = _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(diff, 2));
            d3 = _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(diff, 3));
            acc[r][0] = _mm512_add_epi32(acc[r][0], d0);
            acc[r][1] = _mm512_add_epi32(acc[r][1], d1);
            acc[r][2] = _mm512_add_epi32(acc[r][2], d2);
            acc[r][3] = _mm512_add_epi32(acc[r][3], d3);
        }
    }
    int32_t temp[64];
    for (int r = 0; r < cur_mc; ++r) {
        _mm512_storeu_si512((void*)&temp[ 0], acc[r][0]);
        _mm512_storeu_si512((void*)&temp[16], acc[r][1]);
        _mm512_storeu_si512((void*)&temp[32], acc[r][2]);
        _mm512_storeu_si512((void*)&temp[48], acc[r][3]);
        for (int c = 0; c < cur_nc; ++c)
            C[r * m + c] += temp[c];  // += for generic (may be called multiple times if kc > 8)
    }
}

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    int k_bytes = k / 8;
    memset(C, 0, (size_t)n * m * sizeof(int));

    int n_panels = (n + 3) / 4;
    uint8_t* A_packed = (uint8_t*)_mm_malloc((size_t)n_panels * k_bytes * 8, 64);
    pack_A_all(n, k_bytes, A, k_bytes, A_packed);

    uint8_t* B_packed = (uint8_t*)_mm_malloc((size_t)NC * k_bytes, 64);

    bool use_stream = (m >= 16384) &&
                      (((uintptr_t)C & 63) == 0) &&
                      (((size_t)m * sizeof(int)) % 64 == 0) &&
                      (k_bytes == 2 || k_bytes == 4 || k_bytes == 7);

    for (int jc = 0; jc < m; jc += NC) {
        int cur_nc = std::min(NC, m - jc);
        pack_B_avx512(k_bytes, cur_nc, &B[jc], m, B_packed);

        for (int ic = 0; ic < n; ic += MC) {
            int cur_mc = std::min(MC, n - ic);
            for (int jr = 0; jr < cur_nc; jr += 64) {
                int micro_nc = std::min(64, cur_nc - jr);
                const uint8_t* B_ptr = &B_packed[(jr / 64) * k_bytes * 64];
                for (int ir = 0; ir < cur_mc; ir += 4) {
                    int micro_mc = std::min(4, cur_mc - ir);
                    const uint8_t* A_ptr = &A_packed[((ic + ir) / 4) * k_bytes * 8];
                    int* C_tile = &C[(ic + ir) * m + jc + jr];

                    if (use_stream) {
                        switch (k_bytes) {
                            case 2: micro_kernel_4x64<2,1>(A_ptr, B_ptr, C_tile, m, micro_mc, micro_nc); break;
                            case 4: micro_kernel_4x64<4,1>(A_ptr, B_ptr, C_tile, m, micro_mc, micro_nc); break;
                            case 7: micro_kernel_4x64<7,1>(A_ptr, B_ptr, C_tile, m, micro_mc, micro_nc); break;
                            default: micro_kernel_generic(k_bytes, A_ptr, B_ptr, C_tile, m, micro_mc, micro_nc); break;
                        }
                    } else {
                        switch (k_bytes) {
                            case 2: micro_kernel_4x64<2,0>(A_ptr, B_ptr, C_tile, m, micro_mc, micro_nc); break;
                            case 4: micro_kernel_4x64<4,0>(A_ptr, B_ptr, C_tile, m, micro_mc, micro_nc); break;
                            case 7: micro_kernel_4x64<7,0>(A_ptr, B_ptr, C_tile, m, micro_mc, micro_nc); break;
                            default: micro_kernel_generic(k_bytes, A_ptr, B_ptr, C_tile, m, micro_mc, micro_nc); break;
                        }
                    }
                }
            }
        }
    }

    if (use_stream) _mm_sfence();

    _mm_free(A_packed);
    _mm_free(B_packed);
}
"""
