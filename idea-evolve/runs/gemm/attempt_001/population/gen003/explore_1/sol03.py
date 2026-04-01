# fitness: 204.52
"""
Sol08: 4-row kernel with int8 accumulation.
Less register pressure than 8-row (4 acc8 vs 8).
Test whether better register allocation gives faster inner loop.
"""

def entrypoint():
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    const int k_bytes = k / 8;

    int i = 0;
    for (; i + 4 <= n; i += 4) {
        int j = 0;
        for (; j + 64 <= m; j += 64) {
            __m512i acc8_0 = _mm512_setzero_si512();
            __m512i acc8_1 = _mm512_setzero_si512();
            __m512i acc8_2 = _mm512_setzero_si512();
            __m512i acc8_3 = _mm512_setzero_si512();

            int flush_count = 0;
            for (int t = 0; t < k_bytes; t++) {
                __m512i b = _mm512_loadu_si512((const __m512i*)(B + t * m + j));

                __m512i vp0 = _mm512_set1_epi8((int8_t)A[((i + 0) * k_bytes + t) * 2 + 0]);
                __m512i vn0 = _mm512_set1_epi8((int8_t)A[((i + 0) * k_bytes + t) * 2 + 1]);
                acc8_0 = _mm512_add_epi8(acc8_0, _mm512_sub_epi8(
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(vp0, vn0, b, 0xD8)),
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(vp0, vn0, b, 0xE4))));

                __m512i vp1 = _mm512_set1_epi8((int8_t)A[((i + 1) * k_bytes + t) * 2 + 0]);
                __m512i vn1 = _mm512_set1_epi8((int8_t)A[((i + 1) * k_bytes + t) * 2 + 1]);
                acc8_1 = _mm512_add_epi8(acc8_1, _mm512_sub_epi8(
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(vp1, vn1, b, 0xD8)),
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(vp1, vn1, b, 0xE4))));

                __m512i vp2 = _mm512_set1_epi8((int8_t)A[((i + 2) * k_bytes + t) * 2 + 0]);
                __m512i vn2 = _mm512_set1_epi8((int8_t)A[((i + 2) * k_bytes + t) * 2 + 1]);
                acc8_2 = _mm512_add_epi8(acc8_2, _mm512_sub_epi8(
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(vp2, vn2, b, 0xD8)),
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(vp2, vn2, b, 0xE4))));

                __m512i vp3 = _mm512_set1_epi8((int8_t)A[((i + 3) * k_bytes + t) * 2 + 0]);
                __m512i vn3 = _mm512_set1_epi8((int8_t)A[((i + 3) * k_bytes + t) * 2 + 1]);
                acc8_3 = _mm512_add_epi8(acc8_3, _mm512_sub_epi8(
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(vp3, vn3, b, 0xD8)),
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(vp3, vn3, b, 0xE4))));

                flush_count++;
                if (flush_count == 15 || t == k_bytes - 1) {
                    bool first = (t < 15);

                    #define FLUSH_ROW(acc, row_idx) do { \
                        int* dst = C + (i + (row_idx)) * m + j; \
                        __m128i q0 = _mm512_castsi512_si128(acc); \
                        __m128i q1 = _mm512_extracti32x4_epi32(acc, 1); \
                        __m128i q2 = _mm512_extracti32x4_epi32(acc, 2); \
                        __m128i q3 = _mm512_extracti32x4_epi32(acc, 3); \
                        if (first) { \
                            _mm512_storeu_si512((__m512i*)(dst +  0), _mm512_cvtepi8_epi32(q0)); \
                            _mm512_storeu_si512((__m512i*)(dst + 16), _mm512_cvtepi8_epi32(q1)); \
                            _mm512_storeu_si512((__m512i*)(dst + 32), _mm512_cvtepi8_epi32(q2)); \
                            _mm512_storeu_si512((__m512i*)(dst + 48), _mm512_cvtepi8_epi32(q3)); \
                        } else { \
                            _mm512_storeu_si512((__m512i*)(dst +  0), _mm512_add_epi32(_mm512_loadu_si512((__m512i*)(dst +  0)), _mm512_cvtepi8_epi32(q0))); \
                            _mm512_storeu_si512((__m512i*)(dst + 16), _mm512_add_epi32(_mm512_loadu_si512((__m512i*)(dst + 16)), _mm512_cvtepi8_epi32(q1))); \
                            _mm512_storeu_si512((__m512i*)(dst + 32), _mm512_add_epi32(_mm512_loadu_si512((__m512i*)(dst + 32)), _mm512_cvtepi8_epi32(q2))); \
                            _mm512_storeu_si512((__m512i*)(dst + 48), _mm512_add_epi32(_mm512_loadu_si512((__m512i*)(dst + 48)), _mm512_cvtepi8_epi32(q3))); \
                        } \
                        acc = _mm512_setzero_si512(); \
                    } while(0)

                    FLUSH_ROW(acc8_0, 0);
                    FLUSH_ROW(acc8_1, 1);
                    FLUSH_ROW(acc8_2, 2);
                    FLUSH_ROW(acc8_3, 3);

                    #undef FLUSH_ROW
                    flush_count = 0;
                }
            }
        }

        for (int jj = j; jj < m; jj++) {
            for (int r = 0; r < 4; r++) {
                int sum = 0;
                for (int t = 0; t < k_bytes; t++) {
                    uint8_t a_p = A[((i + r) * k_bytes + t) * 2 + 0];
                    uint8_t a_n = A[((i + r) * k_bytes + t) * 2 + 1];
                    uint8_t b_v = B[t * m + jj];
                    sum += __builtin_popcount((unsigned)((a_p | b_v) & (uint8_t)(a_n | (uint8_t)~b_v)));
                    sum -= __builtin_popcount((unsigned)((uint8_t)(a_p | (uint8_t)~b_v) & (a_n | b_v)));
                }
                C[(i + r) * m + jj] = sum;
            }
        }
    }

    // Remaining rows (1 at a time)
    for (; i < n; i++) {
        __m512i a_pos[32], a_neg[32];
        for (int t = 0; t < k_bytes; t++) {
            a_pos[t] = _mm512_set1_epi8((int8_t)A[(i * k_bytes + t) * 2 + 0]);
            a_neg[t] = _mm512_set1_epi8((int8_t)A[(i * k_bytes + t) * 2 + 1]);
        }
        int* C_row = C + i * m;
        int j = 0;
        for (; j + 64 <= m; j += 64) {
            __m512i acc32_0 = _mm512_setzero_si512(), acc32_1 = _mm512_setzero_si512();
            __m512i acc32_2 = _mm512_setzero_si512(), acc32_3 = _mm512_setzero_si512();
            __m512i acc8 = _mm512_setzero_si512();
            for (int t = 0; t < k_bytes; t++) {
                __m512i b = _mm512_loadu_si512((const __m512i*)(B + t * m + j));
                __m512i pos = _mm512_ternarylogic_epi32(a_pos[t], a_neg[t], b, 0xD8);
                __m512i neg = _mm512_ternarylogic_epi32(a_pos[t], a_neg[t], b, 0xE4);
                acc8 = _mm512_add_epi8(acc8, _mm512_sub_epi8(_mm512_popcnt_epi8(pos), _mm512_popcnt_epi8(neg)));
                if ((t & 15) == 14 || t == k_bytes - 1) {
                    acc32_0 = _mm512_add_epi32(acc32_0, _mm512_cvtepi8_epi32(_mm512_castsi512_si128(acc8)));
                    acc32_1 = _mm512_add_epi32(acc32_1, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8, 1)));
                    acc32_2 = _mm512_add_epi32(acc32_2, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8, 2)));
                    acc32_3 = _mm512_add_epi32(acc32_3, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8, 3)));
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
