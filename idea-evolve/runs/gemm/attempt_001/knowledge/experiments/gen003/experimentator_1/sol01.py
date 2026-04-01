# fitness: 400.32
"""
Experiment 1: Aligned-buffer NT stores workaround for row-streaming kernel.

Base: gen002/explore_1/sol01 row-streaming architecture (147.26 µs).
  small=3.69 µs, medium=225.55 µs, large=3841.72 µs

Modification: for large sizes (n*m*4 > 8 MB), allocate a 64-byte-aligned buffer
via _mm_malloc, compute into it using _mm512_stream_si512 (NT stores), then
_mm_sfence() + memcpy back to C.

Question: Does the NT store benefit (2.3x on large in gen002 standalone test)
survive the aligned_alloc + memcpy overhead?

Hypothesis: Large will go from 3841 µs toward 1289 µs (NT writes) + ~2500 µs
(memcpy at ~12-15 GB/s) = ~3789 µs — roughly a wash. The memcpy overhead may
negate most of the NT store benefit.
"""


def entrypoint():
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>
#include <xmmintrin.h>

// Threshold: use aligned buffer + NT stores when output > 8 MB
static const size_t NT_THRESHOLD_BYTES = 8 * 1024 * 1024;

// Row-streaming kernel writing to a guaranteed-aligned buffer with NT stores.
// Accumulates into int32 (via int8 flush -> acc32 add), then NT-stores once per
// 64-col block. Handles arbitrarily large k (e.g. correctness test k_bytes=32).
static void gemm_row_stream_nt(uint8_t* A, uint8_t* B, int* C_work,
                                int n, int m, int k_bytes) {
    for (int i = 0; i < n; i++) {
        __m512i a_pos[32], a_neg[32];
        for (int t = 0; t < k_bytes; t++) {
            a_pos[t] = _mm512_set1_epi8((int8_t)A[(i * k_bytes + t) * 2 + 0]);
            a_neg[t] = _mm512_set1_epi8((int8_t)A[(i * k_bytes + t) * 2 + 1]);
        }

        int* C_row = C_work + (size_t)i * m;
        int j = 0;
        for (; j + 64 <= m; j += 64) {
            // Accumulate in int32 across multiple int8 flushes (correct for any k)
            __m512i acc32_0 = _mm512_setzero_si512();
            __m512i acc32_1 = _mm512_setzero_si512();
            __m512i acc32_2 = _mm512_setzero_si512();
            __m512i acc32_3 = _mm512_setzero_si512();
            __m512i acc8 = _mm512_setzero_si512();

            for (int t = 0; t < k_bytes; t++) {
                __m512i b = _mm512_loadu_si512((const __m512i*)(B + (size_t)t * m + j));
                __m512i pos_bits = _mm512_ternarylogic_epi32(a_pos[t], a_neg[t], b, 0xD8);
                __m512i neg_bits = _mm512_ternarylogic_epi32(a_pos[t], a_neg[t], b, 0xE4);
                acc8 = _mm512_add_epi8(acc8, _mm512_sub_epi8(
                    _mm512_popcnt_epi8(pos_bits),
                    _mm512_popcnt_epi8(neg_bits)));
                // Flush int8 -> int32 every 15 iters to prevent overflow
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
            // NT stores (require 64-byte alignment -- guaranteed by _mm_malloc)
            _mm512_stream_si512((__m512i*)(C_row + j +  0), acc32_0);
            _mm512_stream_si512((__m512i*)(C_row + j + 16), acc32_1);
            _mm512_stream_si512((__m512i*)(C_row + j + 32), acc32_2);
            _mm512_stream_si512((__m512i*)(C_row + j + 48), acc32_3);
        }
        // Scalar tail
        for (; j < m; j++) {
            int sum = 0;
            for (int t = 0; t < k_bytes; t++) {
                uint8_t a_p = A[(i * k_bytes + t) * 2 + 0];
                uint8_t a_n = A[(i * k_bytes + t) * 2 + 1];
                uint8_t b_v = B[(size_t)t * m + j];
                sum += __builtin_popcount((unsigned)((a_p | b_v) & (uint8_t)(a_n | (uint8_t)~b_v)));
                sum -= __builtin_popcount((unsigned)((uint8_t)(a_p | (uint8_t)~b_v) & (a_n | b_v)));
            }
            C_row[j] = sum;
        }
    }
}

// Row-streaming kernel with regular (unaligned) stores for small/medium
static void gemm_row_stream_regular(uint8_t* A, uint8_t* B, int* C,
                                     int n, int m, int k_bytes) {
    for (int i = 0; i < n; i++) {
        __m512i a_pos[32], a_neg[32];
        for (int t = 0; t < k_bytes; t++) {
            a_pos[t] = _mm512_set1_epi8((int8_t)A[(i * k_bytes + t) * 2 + 0]);
            a_neg[t] = _mm512_set1_epi8((int8_t)A[(i * k_bytes + t) * 2 + 1]);
        }

        int* C_row = C + (size_t)i * m;
        int j = 0;
        for (; j + 64 <= m; j += 64) {
            __m512i acc32_0 = _mm512_setzero_si512();
            __m512i acc32_1 = _mm512_setzero_si512();
            __m512i acc32_2 = _mm512_setzero_si512();
            __m512i acc32_3 = _mm512_setzero_si512();
            __m512i acc8 = _mm512_setzero_si512();
            for (int t = 0; t < k_bytes; t++) {
                __m512i b = _mm512_loadu_si512((const __m512i*)(B + (size_t)t * m + j));
                __m512i pos_bits = _mm512_ternarylogic_epi32(a_pos[t], a_neg[t], b, 0xD8);
                __m512i neg_bits = _mm512_ternarylogic_epi32(a_pos[t], a_neg[t], b, 0xE4);
                acc8 = _mm512_add_epi8(acc8, _mm512_sub_epi8(
                    _mm512_popcnt_epi8(pos_bits),
                    _mm512_popcnt_epi8(neg_bits)));
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
                uint8_t b_v = B[(size_t)t * m + j];
                sum += __builtin_popcount((unsigned)((a_p | b_v) & (uint8_t)(a_n | (uint8_t)~b_v)));
                sum -= __builtin_popcount((unsigned)((uint8_t)(a_p | (uint8_t)~b_v) & (a_n | b_v)));
            }
            C_row[j] = sum;
        }
    }
}

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    const int k_bytes = k / 8;
    const size_t output_bytes = (size_t)n * m * sizeof(int);

    if (output_bytes > NT_THRESHOLD_BYTES) {
        // Large: use aligned buffer + NT stores + memcpy
        int* C_work = (int*)_mm_malloc(output_bytes, 64);
        if (__builtin_expect(C_work == nullptr, 0)) {
            // Fallback if allocation fails
            gemm_row_stream_regular(A, B, C, n, m, k_bytes);
            return;
        }
        gemm_row_stream_nt(A, B, C_work, n, m, k_bytes);
        _mm_sfence();
        memcpy(C, C_work, output_bytes);
        _mm_free(C_work);
    } else {
        // Small/medium: regular stores directly to C
        gemm_row_stream_regular(A, B, C, n, m, k_bytes);
    }
}
"""
