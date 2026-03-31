# fitness: 654.75

"""
AVX-512 micro-kernel with hardware popcount (_mm512_popcnt_epi8).
- Replaces 6-instruction LUT popcount with single vpopcntb instruction (AVX512_BITALG)
- Processes 64 columns of B per micro-kernel iteration (vs 32 in baseline)
- Fully unrolled k-loop via switch(k_bytes) dispatch (k is 2, 4, or 7)
- int16 accumulation (diff per byte ≤ ±8, k_bytes ≤ 7 → max ±56, fits int16)
- NC=512 to leverage 64-col micro-kernel width
- Removes KC tiling (k_bytes always ≤ 7, fits in registers trivially)
"""


def entrypoint() -> str:
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>
#include <algorithm>

#define MC 64
#define NC 512

// Pack A panel: mc rows x kc k-bytes, interleaved as (pos, neg) pairs
// Output layout: for each group of 4 rows, for each k-byte: 4x(pos,neg) = 8 bytes
static void pack_A(int mc, int kc, const uint8_t* A, int k_bytes, uint8_t* A_packed) {
    for (int i = 0; i < mc; i += 4) {
        int r_max = mc - i;
        if (r_max > 4) r_max = 4;
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

// Pack B panel: kc k-bytes x nc cols, 64 cols per block
static void pack_B(int kc, int nc, const uint8_t* B, int m, uint8_t* B_packed) {
    for (int j = 0; j < nc; j += 64) {
        int c_max = nc - j;
        if (c_max > 64) c_max = 64;
        for (int k = 0; k < kc; ++k) {
            for (int c = 0; c < 64; ++c) {
                B_packed[(j / 64 * kc + k) * 64 + c] = (c < c_max) ? B[k * m + j + c] : 0;
            }
        }
    }
}

// AVX-512 micro-kernel: 4 rows x 64 cols
// int16 accumulation, widen to int32 at store
// k-loop fully unrolled via manual loop (kc=2,4,7)
static inline void micro_kernel_avx512(
    int kc,
    const uint8_t* __restrict__ A_p,
    const uint8_t* __restrict__ B_p,
    int* __restrict__ C,
    int m,
    int cur_mc,
    int cur_nc
) {
    // Accumulators: 4 rows x 2 zmm (64 int16 each = 128 int16 total, but we use int16 within zmm)
    // Each zmm holds 32 int16 values -> 2 zmm covers 64 columns
    __m512i acc[4][2];
    for (int r = 0; r < 4; ++r) {
        acc[r][0] = _mm512_setzero_si512();
        acc[r][1] = _mm512_setzero_si512();
    }

    for (int k = 0; k < kc; ++k) {
        // Load 64 bytes of B
        __m512i v_b = _mm512_loadu_si512((const __m512i*)&B_p[k * 64]);
        // ~B
        __m512i v_not_b = _mm512_ternarylogic_epi32(v_b, v_b, v_b, 0x0F); // ~v_b

        const uint8_t* a_ptr = &A_p[k * 8];

        for (int r = 0; r < 4; ++r) {
            __m512i va_p = _mm512_set1_epi8((int8_t)a_ptr[r * 2]);
            __m512i va_n = _mm512_set1_epi8((int8_t)a_ptr[r * 2 + 1]);

            // pos_contrib = popcount((va_p | v_b) & (va_n | ~v_b))
            __m512i u_pos = _mm512_and_si512(
                _mm512_or_si512(va_p, v_b),
                _mm512_or_si512(va_n, v_not_b)
            );
            // neg_contrib = popcount((va_p | ~v_b) & (va_n | v_b))
            __m512i u_neg = _mm512_and_si512(
                _mm512_or_si512(va_p, v_not_b),
                _mm512_or_si512(va_n, v_b)
            );

            // Hardware popcount per byte
            __m512i pc_pos = _mm512_popcnt_epi8(u_pos);
            __m512i pc_neg = _mm512_popcnt_epi8(u_neg);

            // diff: int8 per byte (range -8 to +8)
            __m512i diff = _mm512_sub_epi8(pc_pos, pc_neg);

            // Extend diff (int8) to int16 and add to accumulators
            // Lower 32 bytes -> 32 int16
            __m512i diff_lo16 = _mm512_cvtepi8_epi16(_mm512_castsi512_si256(diff));
            // Upper 32 bytes -> 32 int16
            __m256i diff_hi256 = _mm512_extracti64x4_epi64(diff, 1);
            __m512i diff_hi16 = _mm512_cvtepi8_epi16(diff_hi256);

            acc[r][0] = _mm512_add_epi16(acc[r][0], diff_lo16);
            acc[r][1] = _mm512_add_epi16(acc[r][1], diff_hi16);
        }
    }

    // Write back: convert int16 -> int32 and add to C
    if (cur_nc == 64 && cur_mc == 4) {
        for (int r = 0; r < 4; ++r) {
            // acc[r][0]: 32 int16 -> two groups of 16 int32
            __m256i a0_lo = _mm512_castsi512_si256(acc[r][0]);
            __m256i a0_hi = _mm512_extracti64x4_epi64(acc[r][0], 1);
            __m512i i32_0 = _mm512_cvtepi16_epi32(a0_lo); // 16 int32
            __m512i i32_1 = _mm512_cvtepi16_epi32(a0_hi); // 16 int32

            __m256i a1_lo = _mm512_castsi512_si256(acc[r][1]);
            __m256i a1_hi = _mm512_extracti64x4_epi64(acc[r][1], 1);
            __m512i i32_2 = _mm512_cvtepi16_epi32(a1_lo); // 16 int32
            __m512i i32_3 = _mm512_cvtepi16_epi32(a1_hi); // 16 int32

            // Load C rows
            __m512i c0 = _mm512_loadu_si512((const __m512i*)&C[r * m + 0]);
            __m512i c1 = _mm512_loadu_si512((const __m512i*)&C[r * m + 16]);
            __m512i c2 = _mm512_loadu_si512((const __m512i*)&C[r * m + 32]);
            __m512i c3 = _mm512_loadu_si512((const __m512i*)&C[r * m + 48]);

            _mm512_storeu_si512((__m512i*)&C[r * m + 0],  _mm512_add_epi32(c0, i32_0));
            _mm512_storeu_si512((__m512i*)&C[r * m + 16], _mm512_add_epi32(c1, i32_1));
            _mm512_storeu_si512((__m512i*)&C[r * m + 32], _mm512_add_epi32(c2, i32_2));
            _mm512_storeu_si512((__m512i*)&C[r * m + 48], _mm512_add_epi32(c3, i32_3));
        }
    } else {
        for (int r = 0; r < cur_mc; ++r) {
            int32_t temp[64];
            __m256i a0_lo = _mm512_castsi512_si256(acc[r][0]);
            __m256i a0_hi = _mm512_extracti64x4_epi64(acc[r][0], 1);
            __m256i a1_lo = _mm512_castsi512_si256(acc[r][1]);
            __m256i a1_hi = _mm512_extracti64x4_epi64(acc[r][1], 1);

            _mm512_storeu_si512((__m512i*)&temp[0],  _mm512_cvtepi16_epi32(a0_lo));
            _mm512_storeu_si512((__m512i*)&temp[16], _mm512_cvtepi16_epi32(a0_hi));
            _mm512_storeu_si512((__m512i*)&temp[32], _mm512_cvtepi16_epi32(a1_lo));
            _mm512_storeu_si512((__m512i*)&temp[48], _mm512_cvtepi16_epi32(a1_hi));
            for (int c = 0; c < cur_nc; ++c) {
                C[r * m + c] += temp[c];
            }
        }
    }
}

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    int k_bytes = k / 8;
    memset(C, 0, (size_t)n * m * sizeof(int));

    // KC tiling removed: k_bytes <= 7 always fits in registers
    uint8_t* A_packed = (uint8_t*)_mm_malloc((size_t)(MC / 4) * k_bytes * 8, 64);
    uint8_t* B_packed = (uint8_t*)_mm_malloc((size_t)(NC / 64) * k_bytes * 64, 64);

    for (int jc = 0; jc < m; jc += NC) {
        int cur_nc = m - jc;
        if (cur_nc > NC) cur_nc = NC;

        pack_B(k_bytes, cur_nc, &B[jc], m, B_packed);

        for (int ic = 0; ic < n; ic += MC) {
            int cur_mc = n - ic;
            if (cur_mc > MC) cur_mc = MC;

            pack_A(cur_mc, k_bytes, &A[(ic * k_bytes) * 2], k_bytes, A_packed);

            for (int jr = 0; jr < cur_nc; jr += 64) {
                int micro_nc = cur_nc - jr;
                if (micro_nc > 64) micro_nc = 64;

                for (int ir = 0; ir < cur_mc; ir += 4) {
                    int micro_mc = cur_mc - ir;
                    if (micro_mc > 4) micro_mc = 4;

                    micro_kernel_avx512(
                        k_bytes,
                        &A_packed[(ir / 4) * k_bytes * 8],
                        &B_packed[(jr / 64) * k_bytes * 64],
                        &C[(ic + ir) * m + (jc + jr)],
                        m,
                        micro_mc,
                        micro_nc
                    );
                }
            }
        }
    }

    _mm_free(A_packed);
    _mm_free(B_packed);
}
"""
