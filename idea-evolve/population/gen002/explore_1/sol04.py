# fitness: 162.34
"""
Row-streaming 2-rows + streaming stores (sol04).

Key change: use _mm512_stream_si512 (non-temporal stores) for C output.
For large (C=32MB) and medium (C=4MB), write-allocate forces each store to first
read a cache line from DRAM, doubling effective bandwidth. Streaming stores bypass
cache entirely, halving the effective write bandwidth cost.

Correctness: stream stores require 64-byte alignment. C is allocated as std::vector<int>
which on Linux gets aligned to at least 16 bytes. For large allocations (>4KB), the
allocator typically returns page-aligned (4096 byte) memory, which is 64-byte aligned.
We check alignment and fall back to regular stores if not aligned.
"""

def entrypoint():
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    const int k_bytes = k / 8;
    // Use streaming stores when C is large enough that write-allocate is costly
    // and C pointer is 64-byte aligned
    const bool use_stream = (m >= 4096) && (((uintptr_t)C & 63) == 0);

    int i = 0;
    // 2-row loop
    for (; i + 2 <= n; i += 2) {
        const uint8_t* A_row0 = A + i * k_bytes * 2;
        const uint8_t* A_row1 = A + (i + 1) * k_bytes * 2;
        int* C_row0 = C + i * m;
        int* C_row1 = C + (i + 1) * m;

        int j = 0;
        for (; j + 64 <= m; j += 64) {
            __m512i acc32_r0_0 = _mm512_setzero_si512();
            __m512i acc32_r0_1 = _mm512_setzero_si512();
            __m512i acc32_r0_2 = _mm512_setzero_si512();
            __m512i acc32_r0_3 = _mm512_setzero_si512();
            __m512i acc32_r1_0 = _mm512_setzero_si512();
            __m512i acc32_r1_1 = _mm512_setzero_si512();
            __m512i acc32_r1_2 = _mm512_setzero_si512();
            __m512i acc32_r1_3 = _mm512_setzero_si512();
            __m512i acc8_r0 = _mm512_setzero_si512();
            __m512i acc8_r1 = _mm512_setzero_si512();

            for (int t = 0; t < k_bytes; t++) {
                __m512i ap0 = _mm512_set1_epi8((int8_t)A_row0[t * 2 + 0]);
                __m512i an0 = _mm512_set1_epi8((int8_t)A_row0[t * 2 + 1]);
                __m512i ap1 = _mm512_set1_epi8((int8_t)A_row1[t * 2 + 0]);
                __m512i an1 = _mm512_set1_epi8((int8_t)A_row1[t * 2 + 1]);
                __m512i b = _mm512_loadu_si512((const __m512i*)(B + t * m + j));

                __m512i pos0 = _mm512_ternarylogic_epi32(ap0, an0, b, 0xD8);
                __m512i neg0 = _mm512_ternarylogic_epi32(ap0, an0, b, 0xE4);
                acc8_r0 = _mm512_add_epi8(acc8_r0,
                    _mm512_sub_epi8(_mm512_popcnt_epi8(pos0), _mm512_popcnt_epi8(neg0)));

                __m512i pos1 = _mm512_ternarylogic_epi32(ap1, an1, b, 0xD8);
                __m512i neg1 = _mm512_ternarylogic_epi32(ap1, an1, b, 0xE4);
                acc8_r1 = _mm512_add_epi8(acc8_r1,
                    _mm512_sub_epi8(_mm512_popcnt_epi8(pos1), _mm512_popcnt_epi8(neg1)));

                if ((t & 15) == 14 || t == k_bytes - 1) {
                    __m128i q0, q1, q2, q3;
                    q0 = _mm512_castsi512_si128(acc8_r0);
                    q1 = _mm512_extracti32x4_epi32(acc8_r0, 1);
                    q2 = _mm512_extracti32x4_epi32(acc8_r0, 2);
                    q3 = _mm512_extracti32x4_epi32(acc8_r0, 3);
                    acc32_r0_0 = _mm512_add_epi32(acc32_r0_0, _mm512_cvtepi8_epi32(q0));
                    acc32_r0_1 = _mm512_add_epi32(acc32_r0_1, _mm512_cvtepi8_epi32(q1));
                    acc32_r0_2 = _mm512_add_epi32(acc32_r0_2, _mm512_cvtepi8_epi32(q2));
                    acc32_r0_3 = _mm512_add_epi32(acc32_r0_3, _mm512_cvtepi8_epi32(q3));
                    acc8_r0 = _mm512_setzero_si512();
                    q0 = _mm512_castsi512_si128(acc8_r1);
                    q1 = _mm512_extracti32x4_epi32(acc8_r1, 1);
                    q2 = _mm512_extracti32x4_epi32(acc8_r1, 2);
                    q3 = _mm512_extracti32x4_epi32(acc8_r1, 3);
                    acc32_r1_0 = _mm512_add_epi32(acc32_r1_0, _mm512_cvtepi8_epi32(q0));
                    acc32_r1_1 = _mm512_add_epi32(acc32_r1_1, _mm512_cvtepi8_epi32(q1));
                    acc32_r1_2 = _mm512_add_epi32(acc32_r1_2, _mm512_cvtepi8_epi32(q2));
                    acc32_r1_3 = _mm512_add_epi32(acc32_r1_3, _mm512_cvtepi8_epi32(q3));
                    acc8_r1 = _mm512_setzero_si512();
                }
            }

            if (use_stream) {
                _mm512_stream_si512((__m512i*)(C_row0 + j +  0), acc32_r0_0);
                _mm512_stream_si512((__m512i*)(C_row0 + j + 16), acc32_r0_1);
                _mm512_stream_si512((__m512i*)(C_row0 + j + 32), acc32_r0_2);
                _mm512_stream_si512((__m512i*)(C_row0 + j + 48), acc32_r0_3);
                _mm512_stream_si512((__m512i*)(C_row1 + j +  0), acc32_r1_0);
                _mm512_stream_si512((__m512i*)(C_row1 + j + 16), acc32_r1_1);
                _mm512_stream_si512((__m512i*)(C_row1 + j + 32), acc32_r1_2);
                _mm512_stream_si512((__m512i*)(C_row1 + j + 48), acc32_r1_3);
            } else {
                _mm512_storeu_si512((__m512i*)(C_row0 + j +  0), acc32_r0_0);
                _mm512_storeu_si512((__m512i*)(C_row0 + j + 16), acc32_r0_1);
                _mm512_storeu_si512((__m512i*)(C_row0 + j + 32), acc32_r0_2);
                _mm512_storeu_si512((__m512i*)(C_row0 + j + 48), acc32_r0_3);
                _mm512_storeu_si512((__m512i*)(C_row1 + j +  0), acc32_r1_0);
                _mm512_storeu_si512((__m512i*)(C_row1 + j + 16), acc32_r1_1);
                _mm512_storeu_si512((__m512i*)(C_row1 + j + 32), acc32_r1_2);
                _mm512_storeu_si512((__m512i*)(C_row1 + j + 48), acc32_r1_3);
            }
        }

        // Scalar tail
        for (; j < m; j++) {
            int sum0 = 0, sum1 = 0;
            for (int t = 0; t < k_bytes; t++) {
                uint8_t a_p0 = A_row0[t * 2 + 0], a_n0 = A_row0[t * 2 + 1];
                uint8_t a_p1 = A_row1[t * 2 + 0], a_n1 = A_row1[t * 2 + 1];
                uint8_t bv = B[t * m + j];
                sum0 += __builtin_popcount((a_p0 | bv) & (uint8_t)(a_n0 | (uint8_t)~bv));
                sum0 -= __builtin_popcount((uint8_t)(a_p0 | (uint8_t)~bv) & (a_n0 | bv));
                sum1 += __builtin_popcount((a_p1 | bv) & (uint8_t)(a_n1 | (uint8_t)~bv));
                sum1 -= __builtin_popcount((uint8_t)(a_p1 | (uint8_t)~bv) & (a_n1 | bv));
            }
            C_row0[j] = sum0;
            C_row1[j] = sum1;
        }
    }

    // Odd last row
    if (use_stream) _mm_sfence();
    for (; i < n; i++) {
        const uint8_t* A_row = A + i * k_bytes * 2;
        int* C_row = C + i * m;
        int j = 0;
        for (; j + 64 <= m; j += 64) {
            __m512i acc32_0 = _mm512_setzero_si512();
            __m512i acc32_1 = _mm512_setzero_si512();
            __m512i acc32_2 = _mm512_setzero_si512();
            __m512i acc32_3 = _mm512_setzero_si512();
            __m512i acc8 = _mm512_setzero_si512();
            for (int t = 0; t < k_bytes; t++) {
                __m512i ap = _mm512_set1_epi8((int8_t)A_row[t * 2 + 0]);
                __m512i an = _mm512_set1_epi8((int8_t)A_row[t * 2 + 1]);
                __m512i b = _mm512_loadu_si512((const __m512i*)(B + t * m + j));
                __m512i pos = _mm512_ternarylogic_epi32(ap, an, b, 0xD8);
                __m512i neg = _mm512_ternarylogic_epi32(ap, an, b, 0xE4);
                acc8 = _mm512_add_epi8(acc8, _mm512_sub_epi8(
                    _mm512_popcnt_epi8(pos), _mm512_popcnt_epi8(neg)));
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
            if (use_stream) {
                _mm512_stream_si512((__m512i*)(C_row + j +  0), acc32_0);
                _mm512_stream_si512((__m512i*)(C_row + j + 16), acc32_1);
                _mm512_stream_si512((__m512i*)(C_row + j + 32), acc32_2);
                _mm512_stream_si512((__m512i*)(C_row + j + 48), acc32_3);
            } else {
                _mm512_storeu_si512((__m512i*)(C_row + j +  0), acc32_0);
                _mm512_storeu_si512((__m512i*)(C_row + j + 16), acc32_1);
                _mm512_storeu_si512((__m512i*)(C_row + j + 32), acc32_2);
                _mm512_storeu_si512((__m512i*)(C_row + j + 48), acc32_3);
            }
        }
        for (; j < m; j++) {
            int sum = 0;
            for (int t = 0; t < k_bytes; t++) {
                uint8_t a_p = A_row[t * 2 + 0], a_n = A_row[t * 2 + 1];
                uint8_t bv = B[t * m + j];
                sum += __builtin_popcount((a_p | bv) & (uint8_t)(a_n | (uint8_t)~bv));
                sum -= __builtin_popcount((uint8_t)(a_p | (uint8_t)~bv) & (a_n | bv));
            }
            C_row[j] = sum;
        }
    }
    if (use_stream) _mm_sfence();
}
"""
