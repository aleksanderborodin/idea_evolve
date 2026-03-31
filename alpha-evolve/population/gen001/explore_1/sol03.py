# fitness: 493.42

"""
AVX-512 micro-kernel v3: 8 rows x 64 cols (vs 4x64 in sol02)
- Doubles the row count per micro-kernel call to better hide latency
- Same int16 accumulation, ternarylogic
- NC=256, MC=64 (8 ir iterations with 8-row kernel, 8 jr iterations)
"""


def entrypoint() -> str:
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>
#include <algorithm>

#define MC 64
#define NC 256

static void pack_A(int mc, int kc, const uint8_t* A, int k_bytes, uint8_t* A_packed) {
    // Pack 8 rows at a time: for each k-byte, store 8*(pos,neg) = 16 bytes
    for (int i = 0; i < mc; i += 8) {
        int r_max = mc - i; if (r_max > 8) r_max = 8;
        for (int k = 0; k < kc; ++k) {
            for (int r = 0; r < 8; ++r) {
                int dst = ((i / 8) * kc + k) * 16 + r * 2;
                if (r < r_max) {
                    A_packed[dst]     = A[((i + r) * k_bytes + k) * 2];
                    A_packed[dst + 1] = A[((i + r) * k_bytes + k) * 2 + 1];
                } else {
                    A_packed[dst] = A_packed[dst + 1] = 0;
                }
            }
        }
    }
}

static void pack_B(int kc, int nc, const uint8_t* B, int m, uint8_t* B_packed) {
    for (int j = 0; j < nc; j += 64) {
        int c_max = nc - j; if (c_max > 64) c_max = 64;
        for (int k = 0; k < kc; ++k) {
            for (int c = 0; c < 64; ++c) {
                B_packed[(j / 64 * kc + k) * 64 + c] = (c < c_max) ? B[k * m + j + c] : 0;
            }
        }
    }
}

// 8 rows x 64 cols micro-kernel, int16 accumulators
static inline void micro_kernel(
    int kc,
    const uint8_t* __restrict__ A_p,
    const uint8_t* __restrict__ B_p,
    int* __restrict__ C,
    int m, int cur_mc, int cur_nc
) {
    __m512i acc[8][2];
    for (int r = 0; r < 8; ++r)
        acc[r][0] = acc[r][1] = _mm512_setzero_si512();

    for (int k = 0; k < kc; ++k) {
        __m512i v_b = _mm512_loadu_si512((const __m512i*)&B_p[k * 64]);
        const uint8_t* a_ptr = &A_p[k * 16];  // 16 bytes per k: 8 rows * 2 bytes each

        for (int r = 0; r < 8; ++r) {
            __m512i va_p = _mm512_set1_epi8((int8_t)a_ptr[r * 2]);
            __m512i va_n = _mm512_set1_epi8((int8_t)a_ptr[r * 2 + 1]);

            __m512i u_pos = _mm512_ternarylogic_epi64(va_p, va_n, v_b, 0xD8);
            __m512i u_neg = _mm512_ternarylogic_epi64(va_p, va_n, v_b, 0xE4);

            __m512i diff = _mm512_sub_epi8(_mm512_popcnt_epi8(u_pos), _mm512_popcnt_epi8(u_neg));

            acc[r][0] = _mm512_add_epi16(acc[r][0], _mm512_cvtepi8_epi16(_mm512_castsi512_si256(diff)));
            acc[r][1] = _mm512_add_epi16(acc[r][1], _mm512_cvtepi8_epi16(_mm512_extracti32x8_epi32(diff, 1)));
        }
    }

    if (cur_nc == 64 && cur_mc == 8) {
        for (int r = 0; r < 8; ++r) {
            int* Cr = &C[r * m];
            __m512i i32_0 = _mm512_cvtepi16_epi32(_mm512_castsi512_si256(acc[r][0]));
            __m512i i32_1 = _mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(acc[r][0], 1));
            __m512i i32_2 = _mm512_cvtepi16_epi32(_mm512_castsi512_si256(acc[r][1]));
            __m512i i32_3 = _mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(acc[r][1], 1));
            _mm512_storeu_si512((__m512i*)(Cr+ 0),_mm512_add_epi32(_mm512_loadu_si512((const __m512i*)(Cr+ 0)),i32_0));
            _mm512_storeu_si512((__m512i*)(Cr+16),_mm512_add_epi32(_mm512_loadu_si512((const __m512i*)(Cr+16)),i32_1));
            _mm512_storeu_si512((__m512i*)(Cr+32),_mm512_add_epi32(_mm512_loadu_si512((const __m512i*)(Cr+32)),i32_2));
            _mm512_storeu_si512((__m512i*)(Cr+48),_mm512_add_epi32(_mm512_loadu_si512((const __m512i*)(Cr+48)),i32_3));
        }
    } else {
        for (int r = 0; r < cur_mc; ++r) {
            int32_t temp[64];
            _mm512_storeu_si512((__m512i*)&temp[ 0], _mm512_cvtepi16_epi32(_mm512_castsi512_si256(acc[r][0])));
            _mm512_storeu_si512((__m512i*)&temp[16], _mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(acc[r][0], 1)));
            _mm512_storeu_si512((__m512i*)&temp[32], _mm512_cvtepi16_epi32(_mm512_castsi512_si256(acc[r][1])));
            _mm512_storeu_si512((__m512i*)&temp[48], _mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(acc[r][1], 1)));
            for (int c = 0; c < cur_nc; ++c) C[r * m + c] += temp[c];
        }
    }
}

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    int k_bytes = k / 8;
    memset(C, 0, (size_t)n * m * sizeof(int));

    size_t ap_sz = (size_t)((MC / 8) * k_bytes * 16);
    size_t bp_sz = (size_t)((NC / 64) * k_bytes * 64);
    uint8_t* A_packed = (uint8_t*)_mm_malloc(ap_sz, 64);
    uint8_t* B_packed = (uint8_t*)_mm_malloc(bp_sz, 64);

    for (int jc = 0; jc < m; jc += NC) {
        int cur_nc = m - jc; if (cur_nc > NC) cur_nc = NC;
        pack_B(k_bytes, cur_nc, &B[jc], m, B_packed);

        for (int ic = 0; ic < n; ic += MC) {
            int cur_mc = n - ic; if (cur_mc > MC) cur_mc = MC;
            pack_A(cur_mc, k_bytes, &A[(ic * k_bytes) * 2], k_bytes, A_packed);

            for (int jr = 0; jr < cur_nc; jr += 64) {
                int micro_nc = cur_nc - jr; if (micro_nc > 64) micro_nc = 64;
                for (int ir = 0; ir < cur_mc; ir += 8) {
                    int micro_mc = cur_mc - ir; if (micro_mc > 8) micro_mc = 8;
                    micro_kernel(
                        k_bytes,
                        &A_packed[(ir / 8) * k_bytes * 16],
                        &B_packed[(jr / 64) * k_bytes * 64],
                        &C[(ic + ir) * m + (jc + jr)],
                        m, micro_mc, micro_nc
                    );
                }
            }
        }
    }
    _mm_free(A_packed);
    _mm_free(B_packed);
}
"""
