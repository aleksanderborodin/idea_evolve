/*
 * Experiment 2: Assembly quality inspection
 * Compile with -S to inspect the generated assembly for the micro-kernel.
 * This file contains only the micro-kernel to produce clean assembly output.
 */
#include <immintrin.h>
#include <stdint.h>

// Micro-kernel: 4 rows × 64 columns, k_bytes iterations
// This is the hot loop that dominates 93%+ of execution time.
void micro_kernel_4x64(
    int kc, const uint8_t* __restrict__ A_p,
    const uint8_t* __restrict__ B_p,
    int* __restrict__ C, int m
) {
    __m512i acc[4][2];
    for (int r = 0; r < 4; ++r)
        acc[r][0] = acc[r][1] = _mm512_setzero_si512();

    #pragma GCC unroll 7
    for (int k = 0; k < kc; ++k) {
        __m512i vb = _mm512_loadu_si512((const __m512i*)(B_p + k * 64));
        const uint8_t* a = A_p + k * 8;

        for (int r = 0; r < 4; ++r) {
            __m512i vp = _mm512_set1_epi8((int8_t)a[r * 2]);
            __m512i vn = _mm512_set1_epi8((int8_t)a[r * 2 + 1]);
            __m512i pos = _mm512_popcnt_epi8(
                _mm512_ternarylogic_epi64(vp, vn, vb, 0xD8));
            __m512i neg = _mm512_popcnt_epi8(
                _mm512_ternarylogic_epi64(vp, vn, vb, 0xE4));
            __m512i diff = _mm512_sub_epi8(pos, neg);

            acc[r][0] = _mm512_add_epi16(acc[r][0],
                _mm512_cvtepi8_epi16(_mm512_castsi512_si256(diff)));
            acc[r][1] = _mm512_add_epi16(acc[r][1],
                _mm512_cvtepi8_epi16(_mm512_extracti32x8_epi32(diff, 1)));
        }
    }

    // Store phase: widen int16 -> int32 and write to C
    for (int r = 0; r < 4; ++r) {
        int* Cr = C + r * m;
        _mm512_storeu_si512((__m512i*)(Cr +  0),
            _mm512_cvtepi16_epi32(_mm512_castsi512_si256(acc[r][0])));
        _mm512_storeu_si512((__m512i*)(Cr + 16),
            _mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(acc[r][0], 1)));
        _mm512_storeu_si512((__m512i*)(Cr + 32),
            _mm512_cvtepi16_epi32(_mm512_castsi512_si256(acc[r][1])));
        _mm512_storeu_si512((__m512i*)(Cr + 48),
            _mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(acc[r][1], 1)));
    }
}
