# fitness: 220.33
"""
Sol01: Row-streaming 1-row baseline with int8 accumulation.
No memset (direct stores overwrite C completely). No packing.
small=5.47, med=365.87, large=5349.45
"""

def entrypoint():
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    const int k_bytes = k / 8;

    for (int i = 0; i < n; i++) {
        __m512i a_pos[32], a_neg[32];
        for (int t = 0; t < k_bytes; t++) {
            a_pos[t] = _mm512_set1_epi8((int8_t)A[(i * k_bytes + t) * 2 + 0]);
            a_neg[t] = _mm512_set1_epi8((int8_t)A[(i * k_bytes + t) * 2 + 1]);
        }

        int* C_row = C + i * m;

        int j = 0;
        for (; j + 64 <= m; j += 64) {
            __m512i acc32_0 = _mm512_setzero_si512();
            __m512i acc32_1 = _mm512_setzero_si512();
            __m512i acc32_2 = _mm512_setzero_si512();
            __m512i acc32_3 = _mm512_setzero_si512();
            __m512i acc8 = _mm512_setzero_si512();

            for (int t = 0; t < k_bytes; t++) {
                __m512i b = _mm512_loadu_si512((const __m512i*)(B + t * m + j));
                __m512i pos_bits = _mm512_ternarylogic_epi32(a_pos[t], a_neg[t], b, 0xD8);
                __m512i neg_bits = _mm512_ternarylogic_epi32(a_pos[t], a_neg[t], b, 0xE4);
                __m512i diff = _mm512_sub_epi8(
                    _mm512_popcnt_epi8(pos_bits),
                    _mm512_popcnt_epi8(neg_bits)
                );
                acc8 = _mm512_add_epi8(acc8, diff);

                if ((t & 15) == 14 || t == k_bytes - 1) {
                    __m128i q0 = _mm512_castsi512_si128(acc8);
                    __m128i q1 = _mm512_extracti32x4_epi32(acc8, 1);
                    __m128i q2 = _mm512_extracti32x4_epi32(acc8, 2);
                    __m128i q3 = _mm512_extracti32x4_epi32(acc8, 3);
                    acc32_0 = _mm512_add_epi32(acc32_0, _mm512_cvtepi8_epi32(q0));
                    acc32_1 = _mm512_add_epi32(acc32_1, _mm512_cvtepi8_epi32(q1));
                    acc32_2 = _mm512_add_epi32(acc32_2, _mm512_cvtepi8_epi32(q2));
                    acc32_3 = _mm512_add_epi32(acc32_3, _mm512_cvtepi8_epi32(q3));
                    acc8 = _mm512_setzero_si512();
                }
            }

            _mm512_storeu_si512((__m512i*)(C_row + j +  0), acc32_0);
            _mm512_storeu_si512((__m512i*)(C_row + j + 16), acc32_1);
            _mm512_storeu_si512((__m512i*)(C_row + j + 32), acc32_2);
            _mm512_storeu_si512((__m512i*)(C_row + j + 48), acc32_3);
        }

        for (; j < m; j++) {
            int sum = 0;
            for (int t = 0; t < k_bytes; t++) {
                uint8_t a_p = A[(i * k_bytes + t) * 2 + 0];
                uint8_t a_n = A[(i * k_bytes + t) * 2 + 1];
                uint8_t b_v = B[t * m + j];
                sum += __builtin_popcount((unsigned)((a_p | b_v) & (uint8_t)(a_n | (uint8_t)~b_v)));
                sum -= __builtin_popcount((unsigned)((uint8_t)(a_p | (uint8_t)~b_v) & (a_n | b_v)));
            }
            C_row[j] = sum;
        }
    }
}
"""
