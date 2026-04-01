# fitness: 257.92
"""
Row-streaming no-pack kernel (sol01).

Approach: For each row i of A, broadcast all k_bytes of pos/neg bytes into zmm registers.
Then sweep across all m columns of B in chunks of 64, accumulating per-byte int8 diffs,
then widen to int32 and store. No packing, no tiling, no buffers.

Key idea: k is tiny (2-7 bytes), so A row fits in ~14 zmm registers permanently.
Process 64 columns of B per iteration using AVX-512 popcnt_epi8.

Truth table correction: Intel vpternlog index = (src1<<2)|(src2<<1)|(src3<<0)
so pos_contrib=(a_pos|b)&(a_neg|~b) uses imm8=0xD8 (NOT 0xCA),
   neg_contrib=(a_pos|~b)&(a_neg|b) uses imm8=0xE4 (NOT 0xAC).

Accumulation: int8 up to 15 k_bytes, then flush to int32 for correctness with larger k_bytes.
For benchmark sizes (k_bytes<=7), flush fires once at the end only.
"""

def entrypoint():
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    const int k_bytes = k / 8;

    for (int i = 0; i < n; i++) {
        // Broadcast each k_byte of A row i into zmm registers
        // A layout: A[(i * k_bytes + t) * 2 + 0] = pos byte
        //           A[(i * k_bytes + t) * 2 + 1] = neg byte
        __m512i a_pos[32], a_neg[32];
        for (int t = 0; t < k_bytes; t++) {
            a_pos[t] = _mm512_set1_epi8((int8_t)A[(i * k_bytes + t) * 2 + 0]);
            a_neg[t] = _mm512_set1_epi8((int8_t)A[(i * k_bytes + t) * 2 + 1]);
        }

        int* C_row = C + i * m;

        // Process m columns 64 at a time
        int j = 0;
        for (; j + 64 <= m; j += 64) {
            // int32 accumulators for the 64 output columns (4 groups of 16)
            __m512i acc32_0 = _mm512_setzero_si512();
            __m512i acc32_1 = _mm512_setzero_si512();
            __m512i acc32_2 = _mm512_setzero_si512();
            __m512i acc32_3 = _mm512_setzero_si512();

            // int8 running accumulator — safe for up to 15 k_bytes before overflow
            __m512i acc8 = _mm512_setzero_si512();

            for (int t = 0; t < k_bytes; t++) {
                // Load 64 consecutive bytes of B at column block j, k-row t
                __m512i b = _mm512_loadu_si512((const __m512i*)(B + t * m + j));

                // pos_contrib bits = (a_pos | b) & (a_neg | ~b)
                // Intel vpternlog index=(src1<<2)|(src2<<1)|(src3<<0), imm8=0xD8
                __m512i pos_bits = _mm512_ternarylogic_epi32(a_pos[t], a_neg[t], b, 0xD8);

                // neg_contrib bits = (a_pos | ~b) & (a_neg | b)
                // Intel vpternlog index=(src1<<2)|(src2<<1)|(src3<<0), imm8=0xE4
                __m512i neg_bits = _mm512_ternarylogic_epi32(a_pos[t], a_neg[t], b, 0xE4);

                // Per-byte popcount diff, accumulate in int8
                __m512i diff = _mm512_sub_epi8(
                    _mm512_popcnt_epi8(pos_bits),
                    _mm512_popcnt_epi8(neg_bits)
                );
                acc8 = _mm512_add_epi8(acc8, diff);

                // Flush int8 -> int32 every 15 iterations to prevent overflow
                // For k_bytes <= 7 (benchmark sizes), fires only once at the last t
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

            // Store 64 int32 results to C
            _mm512_storeu_si512((__m512i*)(C_row + j +  0), acc32_0);
            _mm512_storeu_si512((__m512i*)(C_row + j + 16), acc32_1);
            _mm512_storeu_si512((__m512i*)(C_row + j + 32), acc32_2);
            _mm512_storeu_si512((__m512i*)(C_row + j + 48), acc32_3);
        }

        // Scalar tail for m not divisible by 64
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
