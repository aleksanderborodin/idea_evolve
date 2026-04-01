# fitness: 184.84
"""
Sol09: Hybrid kernel selection:
- Small/medium/unaligned: 8-row regular stores (compute-efficient)
- Large+aligned: 1-row NT stores (WC-buffer friendly, sequential writes)

8-row NT stores failed because writing to 8 scattered cache lines
overwhelms the 12 WC buffers. 1-row writes 4 contiguous cache lines.
"""

def entrypoint():
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    const int k_bytes = k / 8;
    const size_t c_bytes = (size_t)n * m * sizeof(int);
    const bool use_nt = (c_bytes > 8 * 1024 * 1024) && ((uintptr_t)C % 64 == 0);

    if (use_nt) {
        // 1-row with NT stores for large
        for (int i = 0; i < n; i++) {
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

                _mm512_stream_si512((__m512i*)(C_row + j +  0), acc32_0);
                _mm512_stream_si512((__m512i*)(C_row + j + 16), acc32_1);
                _mm512_stream_si512((__m512i*)(C_row + j + 32), acc32_2);
                _mm512_stream_si512((__m512i*)(C_row + j + 48), acc32_3);
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
        _mm_sfence();
    } else {
        // 8-row with regular stores for small/medium
        int i = 0;
        for (; i + 8 <= n; i += 8) {
            int j = 0;
            for (; j + 64 <= m; j += 64) {
                __m512i acc8[8];
                for (int r = 0; r < 8; r++) acc8[r] = _mm512_setzero_si512();

                int flush_count = 0;
                for (int t = 0; t < k_bytes; t++) {
                    __m512i b = _mm512_loadu_si512((const __m512i*)(B + t * m + j));
                    for (int r = 0; r < 8; r++) {
                        __m512i vp = _mm512_set1_epi8((int8_t)A[((i + r) * k_bytes + t) * 2 + 0]);
                        __m512i vn = _mm512_set1_epi8((int8_t)A[((i + r) * k_bytes + t) * 2 + 1]);
                        __m512i pos = _mm512_ternarylogic_epi32(vp, vn, b, 0xD8);
                        __m512i neg = _mm512_ternarylogic_epi32(vp, vn, b, 0xE4);
                        acc8[r] = _mm512_add_epi8(acc8[r], _mm512_sub_epi8(_mm512_popcnt_epi8(pos), _mm512_popcnt_epi8(neg)));
                    }
                    flush_count++;
                    if (flush_count == 15 || t == k_bytes - 1) {
                        bool first = (t < 15);
                        for (int r = 0; r < 8; r++) {
                            int* dst = C + (i + r) * m + j;
                            __m128i q0 = _mm512_castsi512_si128(acc8[r]);
                            __m128i q1 = _mm512_extracti32x4_epi32(acc8[r], 1);
                            __m128i q2 = _mm512_extracti32x4_epi32(acc8[r], 2);
                            __m128i q3 = _mm512_extracti32x4_epi32(acc8[r], 3);
                            if (first) {
                                _mm512_storeu_si512((__m512i*)(dst +  0), _mm512_cvtepi8_epi32(q0));
                                _mm512_storeu_si512((__m512i*)(dst + 16), _mm512_cvtepi8_epi32(q1));
                                _mm512_storeu_si512((__m512i*)(dst + 32), _mm512_cvtepi8_epi32(q2));
                                _mm512_storeu_si512((__m512i*)(dst + 48), _mm512_cvtepi8_epi32(q3));
                            } else {
                                _mm512_storeu_si512((__m512i*)(dst +  0), _mm512_add_epi32(_mm512_loadu_si512((__m512i*)(dst +  0)), _mm512_cvtepi8_epi32(q0)));
                                _mm512_storeu_si512((__m512i*)(dst + 16), _mm512_add_epi32(_mm512_loadu_si512((__m512i*)(dst + 16)), _mm512_cvtepi8_epi32(q1)));
                                _mm512_storeu_si512((__m512i*)(dst + 32), _mm512_add_epi32(_mm512_loadu_si512((__m512i*)(dst + 32)), _mm512_cvtepi8_epi32(q2)));
                                _mm512_storeu_si512((__m512i*)(dst + 48), _mm512_add_epi32(_mm512_loadu_si512((__m512i*)(dst + 48)), _mm512_cvtepi8_epi32(q3)));
                            }
                            acc8[r] = _mm512_setzero_si512();
                        }
                        flush_count = 0;
                    }
                }
            }
            for (int jj = j; jj < m; jj++) {
                for (int r = 0; r < 8; r++) {
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
}
"""
