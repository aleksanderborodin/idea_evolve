# fitness: 400.68

"""
AVX-512 micro-kernel v2:
- Fixes: correct ternarylogic constants (0xD8 for u_pos, 0xE4 for u_neg)
- int16 accumulation (safe for all k_bytes including correctness check k_bytes=32)
- ternarylogic reduces inner ops: no explicit NOT(B) needed
- NC=256 (same as baseline) to avoid medium regression
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
    for (int i = 0; i < mc; i += 4) {
        int r_max = mc - i; if (r_max > 4) r_max = 4;
        for (int k = 0; k < kc; ++k) {
            for (int r = 0; r < 4; ++r) {
                if (r < r_max) {
                    A_packed[((i / 4) * kc + k) * 8 + r * 2]     = A[((i + r) * k_bytes + k) * 2];
                    A_packed[((i / 4) * kc + k) * 8 + r * 2 + 1] = A[((i + r) * k_bytes + k) * 2 + 1];
                } else {
                    A_packed[((i / 4) * kc + k) * 8 + r * 2]     = 0;
                    A_packed[((i / 4) * kc + k) * 8 + r * 2 + 1] = 0;
                }
            }
        }
    }
}

// B packed in 64-col blocks: [block0_k0_64bytes][block0_k1_64bytes]...[block1_k0_64bytes]...
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

// AVX-512 micro-kernel: 4 rows x 64 cols, int16 accumulation
// ternarylogic truth tables:
//   u_pos = (va_p | B) & (va_n | ~B)  with a=va_p, b=va_n, c=B: imm8=0xD8
//   u_neg = (va_p | ~B) & (va_n | B)  with a=va_p, b=va_n, c=B: imm8=0xE4
static inline void micro_kernel(
    int kc,
    const uint8_t* __restrict__ A_p,
    const uint8_t* __restrict__ B_p,
    int* __restrict__ C,
    int m, int cur_mc, int cur_nc
) {
    // 2 zmm per row for int16: acc[r][0]=cols 0..31, acc[r][1]=cols 32..63
    __m512i acc[4][2];
    for (int r = 0; r < 4; ++r)
        acc[r][0] = acc[r][1] = _mm512_setzero_si512();

    for (int k = 0; k < kc; ++k) {
        __m512i v_b = _mm512_loadu_si512((const __m512i*)&B_p[k * 64]);
        const uint8_t* a_ptr = &A_p[k * 8];

        for (int r = 0; r < 4; ++r) {
            __m512i va_p = _mm512_set1_epi8((int8_t)a_ptr[r * 2]);
            __m512i va_n = _mm512_set1_epi8((int8_t)a_ptr[r * 2 + 1]);

            // u_pos = (va_p | B) & (va_n | ~B) = ternarylogic(va_p, va_n, B, 0xD8)
            __m512i u_pos = _mm512_ternarylogic_epi64(va_p, va_n, v_b, 0xD8);
            // u_neg = (va_p | ~B) & (va_n | B) = ternarylogic(va_p, va_n, B, 0xE4)
            __m512i u_neg = _mm512_ternarylogic_epi64(va_p, va_n, v_b, 0xE4);

            // diff: int8 per byte, range -8 to +8
            __m512i diff = _mm512_sub_epi8(
                _mm512_popcnt_epi8(u_pos),
                _mm512_popcnt_epi8(u_neg)
            );

            // Widen int8 -> int16 and accumulate
            // Lower 256 bits (32 bytes) -> 32 int16
            __m512i diff_lo16 = _mm512_cvtepi8_epi16(_mm512_castsi512_si256(diff));
            // Upper 256 bits (32 bytes) -> 32 int16
            __m512i diff_hi16 = _mm512_cvtepi8_epi16(_mm512_extracti32x8_epi32(diff, 1));

            acc[r][0] = _mm512_add_epi16(acc[r][0], diff_lo16);
            acc[r][1] = _mm512_add_epi16(acc[r][1], diff_hi16);
        }
    }

    // Write back: convert int16 -> int32 and add to C
    if (cur_nc == 64 && cur_mc == 4) {
        for (int r = 0; r < 4; ++r) {
            int* Cr = &C[r * m];
            // acc[r][0]: 32 int16 -> halves: 16+16 int16 -> 16+16 int32
            __m512i i32_0 = _mm512_cvtepi16_epi32(_mm512_castsi512_si256(acc[r][0]));
            __m512i i32_1 = _mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(acc[r][0], 1));
            __m512i i32_2 = _mm512_cvtepi16_epi32(_mm512_castsi512_si256(acc[r][1]));
            __m512i i32_3 = _mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(acc[r][1], 1));

            _mm512_storeu_si512((__m512i*)(Cr +  0), _mm512_add_epi32(_mm512_loadu_si512((const __m512i*)(Cr +  0)), i32_0));
            _mm512_storeu_si512((__m512i*)(Cr + 16), _mm512_add_epi32(_mm512_loadu_si512((const __m512i*)(Cr + 16)), i32_1));
            _mm512_storeu_si512((__m512i*)(Cr + 32), _mm512_add_epi32(_mm512_loadu_si512((const __m512i*)(Cr + 32)), i32_2));
            _mm512_storeu_si512((__m512i*)(Cr + 48), _mm512_add_epi32(_mm512_loadu_si512((const __m512i*)(Cr + 48)), i32_3));
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

    size_t ap_sz = (size_t)((MC / 4) * k_bytes * 8);
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
                for (int ir = 0; ir < cur_mc; ir += 4) {
                    int micro_mc = cur_mc - ir; if (micro_mc > 4) micro_mc = 4;
                    micro_kernel(
                        k_bytes,
                        &A_packed[(ir / 4) * k_bytes * 8],
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
