# fitness: 602.29
"""
AVX-512 4x64 micro-kernel with hardware _mm512_popcnt_epi8.
Key ideas:
- Replace AVX2 LUT popcount (6 instr) with single _mm512_popcnt_epi8
- Widen micro-kernel from 4x32 (AVX2) to 4x64 (AVX-512)
- 32 zmm registers available: 16 accumulators (4 rows x 4 chunks of 16 int32)
- Pack B with SIMD (single _mm512_loadu + store per 64-byte block)
- Pack A once upfront (tiny: n*k_bytes*2 <= 1792 bytes)
- NC=512 (multiple of 64), MC=64
"""


def entrypoint() -> str:
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>
#include <algorithm>

#define NC 512
#define MC 64

// Pack B: nc columns (padded to multiple of 64), kc k-bytes
// B_packed[(j_blk * kc + k) * 64 + c] = B[k * m + j_start + j_blk*64 + c]
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

// Pack A: mc rows of A into panel format [panel * kc + k] * 8 + r*2
// A_packed[(panel * kc + k) * 8 + r*2]     = A[(panel*4+r) * k_bytes + k] * 2    (pos byte)
// A_packed[(panel * kc + k) * 8 + r*2 + 1] = A[(panel*4+r) * k_bytes + k] * 2 + 1 (neg byte)
static void pack_A_all(int n, int kc, const uint8_t* A_src, int k_bytes, uint8_t* A_packed) {
    for (int i = 0; i < n; i += 4) {
        int rmax = std::min(4, n - i);
        for (int k = 0; k < kc; ++k) {
            uint8_t* dst = &A_packed[(i / 4 * kc + k) * 8];
            for (int r = 0; r < 4; ++r) {
                if (r < rmax) {
                    dst[r * 2]     = A_src[((i + r) * k_bytes + k) * 2];
                    dst[r * 2 + 1] = A_src[((i + r) * k_bytes + k) * 2 + 1];
                } else {
                    dst[r * 2] = dst[r * 2 + 1] = 0;
                }
            }
        }
    }
}

// 4x64 AVX-512 micro-kernel
// A_p: packed A panel [k * 8 + r*2], kc k-bytes
// B_p: packed B panel [k * 64 + c], kc k-bytes, 64 columns
// C: output row-major with stride m
static __attribute__((always_inline)) inline
void micro_kernel_4x64(int kc, const uint8_t* A_p, const uint8_t* B_p,
                        int* C, int m, int cur_mc, int cur_nc) {
    __m512i acc0_0 = _mm512_setzero_si512(), acc0_1 = _mm512_setzero_si512();
    __m512i acc0_2 = _mm512_setzero_si512(), acc0_3 = _mm512_setzero_si512();
    __m512i acc1_0 = _mm512_setzero_si512(), acc1_1 = _mm512_setzero_si512();
    __m512i acc1_2 = _mm512_setzero_si512(), acc1_3 = _mm512_setzero_si512();
    __m512i acc2_0 = _mm512_setzero_si512(), acc2_1 = _mm512_setzero_si512();
    __m512i acc2_2 = _mm512_setzero_si512(), acc2_3 = _mm512_setzero_si512();
    __m512i acc3_0 = _mm512_setzero_si512(), acc3_1 = _mm512_setzero_si512();
    __m512i acc3_2 = _mm512_setzero_si512(), acc3_3 = _mm512_setzero_si512();

    const __m512i all_ones = _mm512_set1_epi8(-1);

    for (int k = 0; k < kc; ++k) {
        __m512i v_b     = _mm512_loadu_si512((const void*)&B_p[k * 64]);
        __m512i v_not_b = _mm512_xor_si512(v_b, all_ones);
        const uint8_t* a = &A_p[k * 8];

        // Row 0
        {
            __m512i va_p = _mm512_set1_epi8((int8_t)a[0]);
            __m512i va_n = _mm512_set1_epi8((int8_t)a[1]);
            __m512i u_pos = _mm512_and_si512(_mm512_or_si512(va_p, v_b), _mm512_or_si512(va_n, v_not_b));
            __m512i u_neg = _mm512_and_si512(_mm512_or_si512(va_p, v_not_b), _mm512_or_si512(va_n, v_b));
            __m512i diff  = _mm512_sub_epi8(_mm512_popcnt_epi8(u_pos), _mm512_popcnt_epi8(u_neg));
            acc0_0 = _mm512_add_epi32(acc0_0, _mm512_cvtepi8_epi32(_mm512_castsi512_si128(diff)));
            acc0_1 = _mm512_add_epi32(acc0_1, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(diff, 1)));
            acc0_2 = _mm512_add_epi32(acc0_2, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(diff, 2)));
            acc0_3 = _mm512_add_epi32(acc0_3, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(diff, 3)));
        }
        // Row 1
        {
            __m512i va_p = _mm512_set1_epi8((int8_t)a[2]);
            __m512i va_n = _mm512_set1_epi8((int8_t)a[3]);
            __m512i u_pos = _mm512_and_si512(_mm512_or_si512(va_p, v_b), _mm512_or_si512(va_n, v_not_b));
            __m512i u_neg = _mm512_and_si512(_mm512_or_si512(va_p, v_not_b), _mm512_or_si512(va_n, v_b));
            __m512i diff  = _mm512_sub_epi8(_mm512_popcnt_epi8(u_pos), _mm512_popcnt_epi8(u_neg));
            acc1_0 = _mm512_add_epi32(acc1_0, _mm512_cvtepi8_epi32(_mm512_castsi512_si128(diff)));
            acc1_1 = _mm512_add_epi32(acc1_1, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(diff, 1)));
            acc1_2 = _mm512_add_epi32(acc1_2, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(diff, 2)));
            acc1_3 = _mm512_add_epi32(acc1_3, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(diff, 3)));
        }
        // Row 2
        {
            __m512i va_p = _mm512_set1_epi8((int8_t)a[4]);
            __m512i va_n = _mm512_set1_epi8((int8_t)a[5]);
            __m512i u_pos = _mm512_and_si512(_mm512_or_si512(va_p, v_b), _mm512_or_si512(va_n, v_not_b));
            __m512i u_neg = _mm512_and_si512(_mm512_or_si512(va_p, v_not_b), _mm512_or_si512(va_n, v_b));
            __m512i diff  = _mm512_sub_epi8(_mm512_popcnt_epi8(u_pos), _mm512_popcnt_epi8(u_neg));
            acc2_0 = _mm512_add_epi32(acc2_0, _mm512_cvtepi8_epi32(_mm512_castsi512_si128(diff)));
            acc2_1 = _mm512_add_epi32(acc2_1, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(diff, 1)));
            acc2_2 = _mm512_add_epi32(acc2_2, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(diff, 2)));
            acc2_3 = _mm512_add_epi32(acc2_3, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(diff, 3)));
        }
        // Row 3
        {
            __m512i va_p = _mm512_set1_epi8((int8_t)a[6]);
            __m512i va_n = _mm512_set1_epi8((int8_t)a[7]);
            __m512i u_pos = _mm512_and_si512(_mm512_or_si512(va_p, v_b), _mm512_or_si512(va_n, v_not_b));
            __m512i u_neg = _mm512_and_si512(_mm512_or_si512(va_p, v_not_b), _mm512_or_si512(va_n, v_b));
            __m512i diff  = _mm512_sub_epi8(_mm512_popcnt_epi8(u_pos), _mm512_popcnt_epi8(u_neg));
            acc3_0 = _mm512_add_epi32(acc3_0, _mm512_cvtepi8_epi32(_mm512_castsi512_si128(diff)));
            acc3_1 = _mm512_add_epi32(acc3_1, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(diff, 1)));
            acc3_2 = _mm512_add_epi32(acc3_2, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(diff, 2)));
            acc3_3 = _mm512_add_epi32(acc3_3, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(diff, 3)));
        }
    }

    if (cur_nc == 64 && cur_mc == 4) {
        // Fast path: full 4x64 tile
        #define STORE_ROW(r, a0, a1, a2, a3) { \
            int* Cr = &C[r * m]; \
            _mm512_storeu_si512((void*)(Cr+ 0), _mm512_add_epi32(a0, _mm512_loadu_si512((const void*)(Cr+ 0)))); \
            _mm512_storeu_si512((void*)(Cr+16), _mm512_add_epi32(a1, _mm512_loadu_si512((const void*)(Cr+16)))); \
            _mm512_storeu_si512((void*)(Cr+32), _mm512_add_epi32(a2, _mm512_loadu_si512((const void*)(Cr+32)))); \
            _mm512_storeu_si512((void*)(Cr+48), _mm512_add_epi32(a3, _mm512_loadu_si512((const void*)(Cr+48)))); \
        }
        STORE_ROW(0, acc0_0, acc0_1, acc0_2, acc0_3);
        STORE_ROW(1, acc1_0, acc1_1, acc1_2, acc1_3);
        STORE_ROW(2, acc2_0, acc2_1, acc2_2, acc2_3);
        STORE_ROW(3, acc3_0, acc3_1, acc3_2, acc3_3);
        #undef STORE_ROW
    } else {
        // Partial tile path
        __m512i* accs[4][4] = {
            {&acc0_0, &acc0_1, &acc0_2, &acc0_3},
            {&acc1_0, &acc1_1, &acc1_2, &acc1_3},
            {&acc2_0, &acc2_1, &acc2_2, &acc2_3},
            {&acc3_0, &acc3_1, &acc3_2, &acc3_3},
        };
        int32_t temp[64];
        for (int r = 0; r < cur_mc; ++r) {
            _mm512_storeu_si512((void*)&temp[ 0], *accs[r][0]);
            _mm512_storeu_si512((void*)&temp[16], *accs[r][1]);
            _mm512_storeu_si512((void*)&temp[32], *accs[r][2]);
            _mm512_storeu_si512((void*)&temp[48], *accs[r][3]);
            for (int c = 0; c < cur_nc; ++c)
                C[r * m + c] += temp[c];
        }
    }
}

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    int k_bytes = k / 8;
    memset(C, 0, (size_t)n * m * sizeof(int));

    // Pack all of A upfront (tiny: max 128*7*2 = 1792 bytes)
    int n_panels = (n + 3) / 4;
    uint8_t* A_packed = (uint8_t*)_mm_malloc((size_t)n_panels * k_bytes * 8, 64);
    pack_A_all(n, k_bytes, A, k_bytes, A_packed);

    // B packed panel: NC * k_bytes bytes (512 * 7 = 3584 bytes max)
    uint8_t* B_packed = (uint8_t*)_mm_malloc((size_t)NC * k_bytes, 64);

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

                    micro_kernel_4x64(k_bytes, A_ptr, B_ptr,
                                      &C[(ic + ir) * m + (jc + jr)], m,
                                      micro_mc, micro_nc);
                }
            }
        }
    }

    _mm_free(A_packed);
    _mm_free(B_packed);
}
"""
