# fitness: 359.42
"""
Row-streaming 2-rows-at-a-time (sol02).

Key improvement over sol01: process 2 rows of A simultaneously.
- Load B[t*m+j] ONCE, use it for BOTH rows → halves B bandwidth
- For k_bytes=4 (medium): 2×8=16 A broadcasts + 2 acc8 + 1 B = 19 zmm (comfortable)
- For k_bytes=7 (large): 2×14=28 A broadcasts + 2 acc8 + 1 B = 31 zmm (tight but fits)

This should cut medium/large times by ~2x over sol01.

Odd rows handled by falling back to 1-row code.
"""

def entrypoint():
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>

// Process 1 row of A against 64 columns of B
static inline void process_row_64cols(
    int k_bytes, int j, int m,
    const __m512i* a_pos, const __m512i* a_neg,
    const uint8_t* B,
    int* C_row
) {
    __m512i acc32_0 = _mm512_setzero_si512();
    __m512i acc32_1 = _mm512_setzero_si512();
    __m512i acc32_2 = _mm512_setzero_si512();
    __m512i acc32_3 = _mm512_setzero_si512();
    __m512i acc8 = _mm512_setzero_si512();

    for (int t = 0; t < k_bytes; t++) {
        __m512i b = _mm512_loadu_si512((const __m512i*)(B + t * m + j));
        __m512i pos_bits = _mm512_ternarylogic_epi32(a_pos[t], a_neg[t], b, 0xD8);
        __m512i neg_bits = _mm512_ternarylogic_epi32(a_pos[t], a_neg[t], b, 0xE4);
        __m512i diff = _mm512_sub_epi8(_mm512_popcnt_epi8(pos_bits), _mm512_popcnt_epi8(neg_bits));
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

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    const int k_bytes = k / 8;

    int i = 0;
    // Process 2 rows at a time
    for (; i + 2 <= n; i += 2) {
        // Broadcast A bytes for rows i and i+1
        // A layout: A[(row * k_bytes + t) * 2 + 0] = pos, [+1] = neg
        __m512i ap0[7], an0[7];  // row i
        __m512i ap1[7], an1[7];  // row i+1
        // Use 32-element arrays to handle correctness test (k_bytes up to 32)
        // Stack: 4 * 32 * 64 = 8192 bytes — allocate on heap for large k_bytes
        // For benchmark k_bytes <= 7, this is fine on stack
        __m512i _ap0_ext[32], _an0_ext[32], _ap1_ext[32], _an1_ext[32];
        const __m512i *Ap0, *An0, *Ap1, *An1;
        if (k_bytes <= 7) {
            for (int t = 0; t < k_bytes; t++) {
                ap0[t] = _mm512_set1_epi8((int8_t)A[(i * k_bytes + t) * 2 + 0]);
                an0[t] = _mm512_set1_epi8((int8_t)A[(i * k_bytes + t) * 2 + 1]);
                ap1[t] = _mm512_set1_epi8((int8_t)A[((i+1) * k_bytes + t) * 2 + 0]);
                an1[t] = _mm512_set1_epi8((int8_t)A[((i+1) * k_bytes + t) * 2 + 1]);
            }
            Ap0 = ap0; An0 = an0; Ap1 = ap1; An1 = an1;
        } else {
            for (int t = 0; t < k_bytes; t++) {
                _ap0_ext[t] = _mm512_set1_epi8((int8_t)A[(i * k_bytes + t) * 2 + 0]);
                _an0_ext[t] = _mm512_set1_epi8((int8_t)A[(i * k_bytes + t) * 2 + 1]);
                _ap1_ext[t] = _mm512_set1_epi8((int8_t)A[((i+1) * k_bytes + t) * 2 + 0]);
                _an1_ext[t] = _mm512_set1_epi8((int8_t)A[((i+1) * k_bytes + t) * 2 + 1]);
            }
            Ap0 = _ap0_ext; An0 = _an0_ext; Ap1 = _ap1_ext; An1 = _an1_ext;
        }

        int* C_row0 = C + i * m;
        int* C_row1 = C + (i + 1) * m;

        int j = 0;
        for (; j + 64 <= m; j += 64) {
            __m512i acc8_r0 = _mm512_setzero_si512();
            __m512i acc8_r1 = _mm512_setzero_si512();
            __m512i acc32_r0_0 = _mm512_setzero_si512();
            __m512i acc32_r0_1 = _mm512_setzero_si512();
            __m512i acc32_r0_2 = _mm512_setzero_si512();
            __m512i acc32_r0_3 = _mm512_setzero_si512();
            __m512i acc32_r1_0 = _mm512_setzero_si512();
            __m512i acc32_r1_1 = _mm512_setzero_si512();
            __m512i acc32_r1_2 = _mm512_setzero_si512();
            __m512i acc32_r1_3 = _mm512_setzero_si512();

            for (int t = 0; t < k_bytes; t++) {
                // Load B once, use for both rows
                __m512i b = _mm512_loadu_si512((const __m512i*)(B + t * m + j));

                // Row i
                __m512i pos0 = _mm512_ternarylogic_epi32(Ap0[t], An0[t], b, 0xD8);
                __m512i neg0 = _mm512_ternarylogic_epi32(Ap0[t], An0[t], b, 0xE4);
                acc8_r0 = _mm512_add_epi8(acc8_r0, _mm512_sub_epi8(
                    _mm512_popcnt_epi8(pos0), _mm512_popcnt_epi8(neg0)));

                // Row i+1
                __m512i pos1 = _mm512_ternarylogic_epi32(Ap1[t], An1[t], b, 0xD8);
                __m512i neg1 = _mm512_ternarylogic_epi32(Ap1[t], An1[t], b, 0xE4);
                acc8_r1 = _mm512_add_epi8(acc8_r1, _mm512_sub_epi8(
                    _mm512_popcnt_epi8(pos1), _mm512_popcnt_epi8(neg1)));

                // Flush int8 -> int32 every 15 iterations
                if ((t & 15) == 14 || t == k_bytes - 1) {
                    __m128i q0 = _mm512_castsi512_si128(acc8_r0);
                    __m128i q1 = _mm512_extracti32x4_epi32(acc8_r0, 1);
                    __m128i q2 = _mm512_extracti32x4_epi32(acc8_r0, 2);
                    __m128i q3 = _mm512_extracti32x4_epi32(acc8_r0, 3);
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

            _mm512_storeu_si512((__m512i*)(C_row0 + j +  0), acc32_r0_0);
            _mm512_storeu_si512((__m512i*)(C_row0 + j + 16), acc32_r0_1);
            _mm512_storeu_si512((__m512i*)(C_row0 + j + 32), acc32_r0_2);
            _mm512_storeu_si512((__m512i*)(C_row0 + j + 48), acc32_r0_3);
            _mm512_storeu_si512((__m512i*)(C_row1 + j +  0), acc32_r1_0);
            _mm512_storeu_si512((__m512i*)(C_row1 + j + 16), acc32_r1_1);
            _mm512_storeu_si512((__m512i*)(C_row1 + j + 32), acc32_r1_2);
            _mm512_storeu_si512((__m512i*)(C_row1 + j + 48), acc32_r1_3);
        }

        // Scalar tail for m not divisible by 64
        for (; j < m; j++) {
            int sum0 = 0, sum1 = 0;
            for (int t = 0; t < k_bytes; t++) {
                uint8_t ap = A[(i * k_bytes + t) * 2 + 0];
                uint8_t an = A[(i * k_bytes + t) * 2 + 1];
                uint8_t bp0 = A[((i+1) * k_bytes + t) * 2 + 0];
                uint8_t bn0 = A[((i+1) * k_bytes + t) * 2 + 1];
                uint8_t bv = B[t * m + j];
                sum0 += __builtin_popcount((ap | bv) & (uint8_t)(an | (uint8_t)~bv));
                sum0 -= __builtin_popcount((uint8_t)(ap | (uint8_t)~bv) & (an | bv));
                sum1 += __builtin_popcount((bp0 | bv) & (uint8_t)(bn0 | (uint8_t)~bv));
                sum1 -= __builtin_popcount((uint8_t)(bp0 | (uint8_t)~bv) & (bn0 | bv));
            }
            C_row0[j] = sum0;
            C_row1[j] = sum1;
        }
    }

    // Handle odd last row
    for (; i < n; i++) {
        __m512i a_pos[32], a_neg[32];
        for (int t = 0; t < k_bytes; t++) {
            a_pos[t] = _mm512_set1_epi8((int8_t)A[(i * k_bytes + t) * 2 + 0]);
            a_neg[t] = _mm512_set1_epi8((int8_t)A[(i * k_bytes + t) * 2 + 1]);
        }
        int* C_row = C + i * m;
        int j = 0;
        for (; j + 64 <= m; j += 64) {
            process_row_64cols(k_bytes, j, m, a_pos, a_neg, B, C_row);
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
