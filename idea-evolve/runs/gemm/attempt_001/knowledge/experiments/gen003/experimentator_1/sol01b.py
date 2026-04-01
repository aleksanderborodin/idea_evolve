# fitness: 250.98
"""
Experiment 1b: NT stores with STATIC pre-allocated buffer (no per-call malloc overhead).

Purpose: isolate the true NT store + memcpy overhead from the malloc/mmap cost.

In sol01.py, _mm_malloc(32 MB) is called inside gemmCandidate on every benchmark rep.
For 32 MB allocations, glibc uses mmap/munmap which has massive overhead:
- Page fault handling for 8192 new 4 KB pages
- TLB flushes on munmap
- OS kernel time for mmap syscall

This variant uses a BSS static buffer (allocated once at program load, pages demand-faulted
on first use). The median of 10 benchmark reps will capture steady-state (reps 2-10 have
no page fault overhead).

Expected result: eliminates malloc overhead but the memcpy (32 MB cold DRAM → C) still
dominates. Estimated: compute(1029µs) + NT-writes(1289µs) + memcpy(2100-3000µs) = 4418-5318µs
vs baseline 3841µs. Still likely WORSE than regular stores.
"""


def entrypoint():
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>
#include <xmmintrin.h>

// Static aligned buffer — allocated in BSS, no per-call malloc.
// Large enough for the largest benchmark (128 * 65536 * 4 = 32 MB).
// 64-byte aligned via alignas.
alignas(64) static int nt_buf[128 * 65536];

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    const int k_bytes = k / 8;
    const size_t output_bytes = (size_t)n * m * sizeof(int);
    const bool use_nt = (output_bytes > 8ULL * 1024 * 1024);

    int* C_dest = use_nt ? nt_buf : C;

    // Single monolithic row-streaming kernel (no helper function call overhead)
    for (int i = 0; i < n; i++) {
        __m512i a_pos[32], a_neg[32];
        for (int t = 0; t < k_bytes; t++) {
            a_pos[t] = _mm512_set1_epi8((int8_t)A[(i * k_bytes + t) * 2 + 0]);
            a_neg[t] = _mm512_set1_epi8((int8_t)A[(i * k_bytes + t) * 2 + 1]);
        }

        int* C_row = C_dest + (size_t)i * m;
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

            if (use_nt) {
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

    // If we used NT stores, sfence + memcpy back to caller's C
    if (use_nt) {
        _mm_sfence();
        memcpy(C, nt_buf, output_bytes);
    }
}
"""
