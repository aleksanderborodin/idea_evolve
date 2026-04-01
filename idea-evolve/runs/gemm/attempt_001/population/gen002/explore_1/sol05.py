# fitness: 243.30
"""
Row-streaming with pre-broadcast A + streaming stores (sol05).

Key insight: For k_bytes <= 4 (small + medium benchmark sizes), pre-broadcast ALL A
bytes for 2 rows into zmm registers BEFORE the j-loop. This amortizes 4 broadcast ops
per k-byte across m/64 j-blocks instead of paying them every j-block.

For k_bytes=4, 2 rows: 2*4*2 = 16 zmm for A broadcasts. Leaves 16 zmm for:
- 8 acc32 registers (4 per row)
- 2 acc8 registers (1 per row)
- 1 B load
- 1-3 temporaries for ternarylogic, popcnt results

For k_bytes > 4 (large, k_bytes=7): falls back to inline loading (28 zmm would be needed).

Also: streaming stores for m >= 4096.
"""

def entrypoint():
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>

// Process 2 rows with pre-broadcast A and streaming stores
// Works for k_bytes 1..4 where A broadcasts fit in 16 zmm
static void process_2rows_prebroadcast(
    int k_bytes, int m, int n_rows2,
    const uint8_t* __restrict__ A,
    const uint8_t* __restrict__ B,
    int* __restrict__ C,
    bool use_stream
) {
    for (int i = 0; i < n_rows2; i += 2) {
        const uint8_t* A_row0 = A + i * k_bytes * 2;
        const uint8_t* A_row1 = A + (i + 1) * k_bytes * 2;
        int* C_row0 = C + i * m;
        int* C_row1 = C + (i + 1) * m;

        // Pre-broadcast all A bytes for both rows (at most 4*4=16 zmm)
        __m512i ap0[4], an0[4], ap1[4], an1[4];
        for (int t = 0; t < k_bytes; t++) {
            ap0[t] = _mm512_set1_epi8((int8_t)A_row0[t * 2 + 0]);
            an0[t] = _mm512_set1_epi8((int8_t)A_row0[t * 2 + 1]);
            ap1[t] = _mm512_set1_epi8((int8_t)A_row1[t * 2 + 0]);
            an1[t] = _mm512_set1_epi8((int8_t)A_row1[t * 2 + 1]);
        }

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

            // k-loop: A registers pre-loaded, only B needs loading
            #pragma GCC unroll 4
            for (int t = 0; t < k_bytes; t++) {
                __m512i b = _mm512_loadu_si512((const __m512i*)(B + t * m + j));
                acc8_r0 = _mm512_add_epi8(acc8_r0, _mm512_sub_epi8(
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap0[t], an0[t], b, 0xD8)),
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap0[t], an0[t], b, 0xE4))));
                acc8_r1 = _mm512_add_epi8(acc8_r1, _mm512_sub_epi8(
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap1[t], an1[t], b, 0xD8)),
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap1[t], an1[t], b, 0xE4))));
            }

            // Single flush at end (k_bytes <= 4 < 15, so no overflow)
            __m128i q0 = _mm512_castsi512_si128(acc8_r0);
            __m128i q1 = _mm512_extracti32x4_epi32(acc8_r0, 1);
            __m128i q2 = _mm512_extracti32x4_epi32(acc8_r0, 2);
            __m128i q3 = _mm512_extracti32x4_epi32(acc8_r0, 3);
            acc32_r0_0 = _mm512_cvtepi8_epi32(q0);
            acc32_r0_1 = _mm512_cvtepi8_epi32(q1);
            acc32_r0_2 = _mm512_cvtepi8_epi32(q2);
            acc32_r0_3 = _mm512_cvtepi8_epi32(q3);
            q0 = _mm512_castsi512_si128(acc8_r1);
            q1 = _mm512_extracti32x4_epi32(acc8_r1, 1);
            q2 = _mm512_extracti32x4_epi32(acc8_r1, 2);
            q3 = _mm512_extracti32x4_epi32(acc8_r1, 3);
            acc32_r1_0 = _mm512_cvtepi8_epi32(q0);
            acc32_r1_1 = _mm512_cvtepi8_epi32(q1);
            acc32_r1_2 = _mm512_cvtepi8_epi32(q2);
            acc32_r1_3 = _mm512_cvtepi8_epi32(q3);

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
                uint8_t bv = B[t * m + j];
                uint8_t a_p0 = A_row0[t*2], a_n0 = A_row0[t*2+1];
                uint8_t a_p1 = A_row1[t*2], a_n1 = A_row1[t*2+1];
                sum0 += __builtin_popcount((a_p0|bv)&(uint8_t)(a_n0|(uint8_t)~bv));
                sum0 -= __builtin_popcount((uint8_t)(a_p0|(uint8_t)~bv)&(a_n0|bv));
                sum1 += __builtin_popcount((a_p1|bv)&(uint8_t)(a_n1|(uint8_t)~bv));
                sum1 -= __builtin_popcount((uint8_t)(a_p1|(uint8_t)~bv)&(a_n1|bv));
            }
            C_row0[j] = sum0; C_row1[j] = sum1;
        }
    }
}

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    const int k_bytes = k / 8;
    const bool use_stream = (m >= 4096) && (((uintptr_t)C & 63) == 0);

    if (k_bytes <= 4) {
        // Pre-broadcast path for small/medium
        int n2 = (n / 2) * 2;
        process_2rows_prebroadcast(k_bytes, m, n2, A, B, C, use_stream);
        // Handle odd last row
        if (n & 1) {
            int i = n - 1;
            const uint8_t* A_row = A + i * k_bytes * 2;
            int* C_row = C + i * m;
            __m512i ap[4], an[4];
            for (int t = 0; t < k_bytes; t++) {
                ap[t] = _mm512_set1_epi8((int8_t)A_row[t*2]);
                an[t] = _mm512_set1_epi8((int8_t)A_row[t*2+1]);
            }
            int j = 0;
            for (; j + 64 <= m; j += 64) {
                __m512i acc8 = _mm512_setzero_si512();
                #pragma GCC unroll 4
                for (int t = 0; t < k_bytes; t++) {
                    __m512i b = _mm512_loadu_si512((const __m512i*)(B + t*m + j));
                    acc8 = _mm512_add_epi8(acc8, _mm512_sub_epi8(
                        _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap[t], an[t], b, 0xD8)),
                        _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap[t], an[t], b, 0xE4))));
                }
                __m128i q0 = _mm512_castsi512_si128(acc8);
                __m128i q1 = _mm512_extracti32x4_epi32(acc8, 1);
                __m128i q2 = _mm512_extracti32x4_epi32(acc8, 2);
                __m128i q3 = _mm512_extracti32x4_epi32(acc8, 3);
                if (use_stream) {
                    _mm512_stream_si512((__m512i*)(C_row+j+0),  _mm512_cvtepi8_epi32(q0));
                    _mm512_stream_si512((__m512i*)(C_row+j+16), _mm512_cvtepi8_epi32(q1));
                    _mm512_stream_si512((__m512i*)(C_row+j+32), _mm512_cvtepi8_epi32(q2));
                    _mm512_stream_si512((__m512i*)(C_row+j+48), _mm512_cvtepi8_epi32(q3));
                } else {
                    _mm512_storeu_si512((__m512i*)(C_row+j+0),  _mm512_cvtepi8_epi32(q0));
                    _mm512_storeu_si512((__m512i*)(C_row+j+16), _mm512_cvtepi8_epi32(q1));
                    _mm512_storeu_si512((__m512i*)(C_row+j+32), _mm512_cvtepi8_epi32(q2));
                    _mm512_storeu_si512((__m512i*)(C_row+j+48), _mm512_cvtepi8_epi32(q3));
                }
            }
            for (; j < m; j++) {
                int sum = 0;
                for (int t = 0; t < k_bytes; t++) {
                    uint8_t ap_ = A_row[t*2], an_ = A_row[t*2+1], bv = B[t*m+j];
                    sum += __builtin_popcount((ap_|bv)&(uint8_t)(an_|(uint8_t)~bv));
                    sum -= __builtin_popcount((uint8_t)(ap_|(uint8_t)~bv)&(an_|bv));
                }
                C_row[j] = sum;
            }
        }
    } else {
        // Large k_bytes: inline broadcast, 2-row loop
        int i = 0;
        for (; i + 2 <= n; i += 2) {
            const uint8_t* A_row0 = A + i * k_bytes * 2;
            const uint8_t* A_row1 = A + (i+1) * k_bytes * 2;
            int* C_row0 = C + i * m;
            int* C_row1 = C + (i+1) * m;
            int j = 0;
            for (; j + 64 <= m; j += 64) {
                __m512i acc32_r0_0 = _mm512_setzero_si512(), acc32_r0_1 = _mm512_setzero_si512();
                __m512i acc32_r0_2 = _mm512_setzero_si512(), acc32_r0_3 = _mm512_setzero_si512();
                __m512i acc32_r1_0 = _mm512_setzero_si512(), acc32_r1_1 = _mm512_setzero_si512();
                __m512i acc32_r1_2 = _mm512_setzero_si512(), acc32_r1_3 = _mm512_setzero_si512();
                __m512i acc8_r0 = _mm512_setzero_si512(), acc8_r1 = _mm512_setzero_si512();
                for (int t = 0; t < k_bytes; t++) {
                    __m512i ap0 = _mm512_set1_epi8((int8_t)A_row0[t*2]);
                    __m512i an0 = _mm512_set1_epi8((int8_t)A_row0[t*2+1]);
                    __m512i ap1 = _mm512_set1_epi8((int8_t)A_row1[t*2]);
                    __m512i an1 = _mm512_set1_epi8((int8_t)A_row1[t*2+1]);
                    __m512i b = _mm512_loadu_si512((const __m512i*)(B + t*m + j));
                    acc8_r0 = _mm512_add_epi8(acc8_r0, _mm512_sub_epi8(
                        _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap0, an0, b, 0xD8)),
                        _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap0, an0, b, 0xE4))));
                    acc8_r1 = _mm512_add_epi8(acc8_r1, _mm512_sub_epi8(
                        _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap1, an1, b, 0xD8)),
                        _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap1, an1, b, 0xE4))));
                    if ((t & 15) == 14 || t == k_bytes - 1) {
                        __m128i q0, q1, q2, q3;
                        q0 = _mm512_castsi512_si128(acc8_r0); q1 = _mm512_extracti32x4_epi32(acc8_r0,1);
                        q2 = _mm512_extracti32x4_epi32(acc8_r0,2); q3 = _mm512_extracti32x4_epi32(acc8_r0,3);
                        acc32_r0_0 = _mm512_add_epi32(acc32_r0_0, _mm512_cvtepi8_epi32(q0));
                        acc32_r0_1 = _mm512_add_epi32(acc32_r0_1, _mm512_cvtepi8_epi32(q1));
                        acc32_r0_2 = _mm512_add_epi32(acc32_r0_2, _mm512_cvtepi8_epi32(q2));
                        acc32_r0_3 = _mm512_add_epi32(acc32_r0_3, _mm512_cvtepi8_epi32(q3));
                        acc8_r0 = _mm512_setzero_si512();
                        q0 = _mm512_castsi512_si128(acc8_r1); q1 = _mm512_extracti32x4_epi32(acc8_r1,1);
                        q2 = _mm512_extracti32x4_epi32(acc8_r1,2); q3 = _mm512_extracti32x4_epi32(acc8_r1,3);
                        acc32_r1_0 = _mm512_add_epi32(acc32_r1_0, _mm512_cvtepi8_epi32(q0));
                        acc32_r1_1 = _mm512_add_epi32(acc32_r1_1, _mm512_cvtepi8_epi32(q1));
                        acc32_r1_2 = _mm512_add_epi32(acc32_r1_2, _mm512_cvtepi8_epi32(q2));
                        acc32_r1_3 = _mm512_add_epi32(acc32_r1_3, _mm512_cvtepi8_epi32(q3));
                        acc8_r1 = _mm512_setzero_si512();
                    }
                }
                if (use_stream) {
                    _mm512_stream_si512((__m512i*)(C_row0+j+0),  acc32_r0_0);
                    _mm512_stream_si512((__m512i*)(C_row0+j+16), acc32_r0_1);
                    _mm512_stream_si512((__m512i*)(C_row0+j+32), acc32_r0_2);
                    _mm512_stream_si512((__m512i*)(C_row0+j+48), acc32_r0_3);
                    _mm512_stream_si512((__m512i*)(C_row1+j+0),  acc32_r1_0);
                    _mm512_stream_si512((__m512i*)(C_row1+j+16), acc32_r1_1);
                    _mm512_stream_si512((__m512i*)(C_row1+j+32), acc32_r1_2);
                    _mm512_stream_si512((__m512i*)(C_row1+j+48), acc32_r1_3);
                } else {
                    _mm512_storeu_si512((__m512i*)(C_row0+j+0),  acc32_r0_0);
                    _mm512_storeu_si512((__m512i*)(C_row0+j+16), acc32_r0_1);
                    _mm512_storeu_si512((__m512i*)(C_row0+j+32), acc32_r0_2);
                    _mm512_storeu_si512((__m512i*)(C_row0+j+48), acc32_r0_3);
                    _mm512_storeu_si512((__m512i*)(C_row1+j+0),  acc32_r1_0);
                    _mm512_storeu_si512((__m512i*)(C_row1+j+16), acc32_r1_1);
                    _mm512_storeu_si512((__m512i*)(C_row1+j+32), acc32_r1_2);
                    _mm512_storeu_si512((__m512i*)(C_row1+j+48), acc32_r1_3);
                }
            }
            for (; j < m; j++) {
                int sum0 = 0, sum1 = 0;
                for (int t = 0; t < k_bytes; t++) {
                    uint8_t a_p0=A_row0[t*2], a_n0=A_row0[t*2+1];
                    uint8_t a_p1=A_row1[t*2], a_n1=A_row1[t*2+1];
                    uint8_t bv = B[t*m+j];
                    sum0 += __builtin_popcount((a_p0|bv)&(uint8_t)(a_n0|(uint8_t)~bv));
                    sum0 -= __builtin_popcount((uint8_t)(a_p0|(uint8_t)~bv)&(a_n0|bv));
                    sum1 += __builtin_popcount((a_p1|bv)&(uint8_t)(a_n1|(uint8_t)~bv));
                    sum1 -= __builtin_popcount((uint8_t)(a_p1|(uint8_t)~bv)&(a_n1|bv));
                }
                C_row0[j] = sum0; C_row1[j] = sum1;
            }
        }
        for (; i < n; i++) {
            const uint8_t* A_row = A + i * k_bytes * 2;
            int* C_row = C + i * m;
            int j = 0;
            for (; j + 64 <= m; j += 64) {
                __m512i acc32_0=_mm512_setzero_si512(), acc32_1=_mm512_setzero_si512();
                __m512i acc32_2=_mm512_setzero_si512(), acc32_3=_mm512_setzero_si512();
                __m512i acc8 = _mm512_setzero_si512();
                for (int t = 0; t < k_bytes; t++) {
                    __m512i ap=_mm512_set1_epi8((int8_t)A_row[t*2]), an=_mm512_set1_epi8((int8_t)A_row[t*2+1]);
                    __m512i b=_mm512_loadu_si512((const __m512i*)(B+t*m+j));
                    acc8 = _mm512_add_epi8(acc8, _mm512_sub_epi8(
                        _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap,an,b,0xD8)),
                        _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap,an,b,0xE4))));
                    if ((t&15)==14||t==k_bytes-1) {
                        __m128i q0=_mm512_castsi512_si128(acc8), q1=_mm512_extracti32x4_epi32(acc8,1);
                        __m128i q2=_mm512_extracti32x4_epi32(acc8,2), q3=_mm512_extracti32x4_epi32(acc8,3);
                        acc32_0=_mm512_add_epi32(acc32_0,_mm512_cvtepi8_epi32(q0));
                        acc32_1=_mm512_add_epi32(acc32_1,_mm512_cvtepi8_epi32(q1));
                        acc32_2=_mm512_add_epi32(acc32_2,_mm512_cvtepi8_epi32(q2));
                        acc32_3=_mm512_add_epi32(acc32_3,_mm512_cvtepi8_epi32(q3));
                        acc8=_mm512_setzero_si512();
                    }
                }
                if (use_stream) {
                    _mm512_stream_si512((__m512i*)(C_row+j+0),  acc32_0);
                    _mm512_stream_si512((__m512i*)(C_row+j+16), acc32_1);
                    _mm512_stream_si512((__m512i*)(C_row+j+32), acc32_2);
                    _mm512_stream_si512((__m512i*)(C_row+j+48), acc32_3);
                } else {
                    _mm512_storeu_si512((__m512i*)(C_row+j+0),  acc32_0);
                    _mm512_storeu_si512((__m512i*)(C_row+j+16), acc32_1);
                    _mm512_storeu_si512((__m512i*)(C_row+j+32), acc32_2);
                    _mm512_storeu_si512((__m512i*)(C_row+j+48), acc32_3);
                }
            }
            for (; j < m; j++) {
                int sum = 0;
                for (int t = 0; t < k_bytes; t++) {
                    uint8_t ap=A_row[t*2], an=A_row[t*2+1], bv=B[t*m+j];
                    sum += __builtin_popcount((ap|bv)&(uint8_t)(an|(uint8_t)~bv));
                    sum -= __builtin_popcount((uint8_t)(ap|(uint8_t)~bv)&(an|bv));
                }
                C_row[j] = sum;
            }
        }
    }
    if (use_stream) _mm_sfence();
}
"""
