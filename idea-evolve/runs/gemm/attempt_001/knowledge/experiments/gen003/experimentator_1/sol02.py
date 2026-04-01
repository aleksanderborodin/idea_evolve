# fitness: 197.33
"""
Experiment 3: Pack-free small benchmark optimization.

Base: row-streaming sol01 (147.26 µs, small=3.69 µs, medium=225.55 µs, large=3841.72 µs)

For small (n=32, m=1024, k_bytes=2):
- B is only 2 KB — fits entirely in L1 cache (48 KB).
- A is only 128 bytes — fits in registers.
- Current overhead includes: per-row broadcast setup, k-loop (2 iters), flush once.

Optimization idea: Process 4 rows simultaneously, sharing the 2 B loads across rows.
This amortizes B loads 4x. Fully unroll k-loop (k_bytes=2 → exactly 2 iterations).
No pack_A, no pack_B — direct broadcast from A source bytes.

For medium (k_bytes=4) and large (k_bytes=7): use the standard row-streaming kernel.

Question: Can small drop from 3.69 µs to < 2 µs?

Per-analysis estimate: 4 rows × 16 blocks × 2 B loads shared → ~0.5 B loads per row-block.
Eliminates the broadcast setup loop overhead by keeping A bytes in registers.
"""


def entrypoint():
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>

// Macro to compute diff = popcnt(pos_bits) - popcnt(neg_bits) and add to acc8
#define COMPUTE_DIFF_ACC(ap, an, bv, acc) \
    do { \
        __m512i _pos = _mm512_ternarylogic_epi32((ap), (an), (bv), 0xD8); \
        __m512i _neg = _mm512_ternarylogic_epi32((ap), (an), (bv), 0xE4); \
        (acc) = _mm512_add_epi8((acc), _mm512_sub_epi8( \
            _mm512_popcnt_epi8(_pos), _mm512_popcnt_epi8(_neg))); \
    } while(0)

// Widen int8 accumulator to 4 zmm int32 registers and store (regular stores)
#define WIDEN_STORE(acc8, dst) \
    do { \
        __m128i _q0 = _mm512_castsi512_si128(acc8); \
        __m128i _q1 = _mm512_extracti32x4_epi32(acc8, 1); \
        __m128i _q2 = _mm512_extracti32x4_epi32(acc8, 2); \
        __m128i _q3 = _mm512_extracti32x4_epi32(acc8, 3); \
        _mm512_storeu_si512((__m512i*)((dst) +  0), _mm512_cvtepi8_epi32(_q0)); \
        _mm512_storeu_si512((__m512i*)((dst) + 16), _mm512_cvtepi8_epi32(_q1)); \
        _mm512_storeu_si512((__m512i*)((dst) + 32), _mm512_cvtepi8_epi32(_q2)); \
        _mm512_storeu_si512((__m512i*)((dst) + 48), _mm512_cvtepi8_epi32(_q3)); \
    } while(0)

// -----------------------------------------------------------------------
// SMALL path: 4-row kernel, k_bytes=2 specialized (fully unrolled k-loop)
// Processes 4 rows at once, sharing 2 B loads across all 4 rows.
// A bytes (8 per 4-row group) are pre-broadcast before the j-loop.
// -----------------------------------------------------------------------
static void gemm_small_4row(uint8_t* __restrict__ A, uint8_t* __restrict__ B,
                             int* __restrict__ C, int n, int m) {
    // k_bytes = 2 for small benchmark
    // A layout: A[(row * 2 + t) * 2 + 0] = pos byte, [...+1] = neg byte
    // B layout: B[t * m + j] for t=0..1, j=0..m-1

    int i = 0;
    for (; i + 4 <= n; i += 4) {
        // Pre-broadcast all A bytes for 4 rows, 2 k-steps = 16 broadcasts
        // Row i:   A[i*4+0]=pos0, A[i*4+1]=neg0, A[i*4+2]=pos1, A[i*4+3]=neg1
        const uint8_t* Ai0 = A + (i + 0) * 2 * 2;
        const uint8_t* Ai1 = A + (i + 1) * 2 * 2;
        const uint8_t* Ai2 = A + (i + 2) * 2 * 2;
        const uint8_t* Ai3 = A + (i + 3) * 2 * 2;

        __m512i ap0_0 = _mm512_set1_epi8((int8_t)Ai0[0]);  // row i+0, k=0, pos
        __m512i an0_0 = _mm512_set1_epi8((int8_t)Ai0[1]);  // row i+0, k=0, neg
        __m512i ap0_1 = _mm512_set1_epi8((int8_t)Ai0[2]);  // row i+0, k=1, pos
        __m512i an0_1 = _mm512_set1_epi8((int8_t)Ai0[3]);  // row i+0, k=1, neg

        __m512i ap1_0 = _mm512_set1_epi8((int8_t)Ai1[0]);
        __m512i an1_0 = _mm512_set1_epi8((int8_t)Ai1[1]);
        __m512i ap1_1 = _mm512_set1_epi8((int8_t)Ai1[2]);
        __m512i an1_1 = _mm512_set1_epi8((int8_t)Ai1[3]);

        __m512i ap2_0 = _mm512_set1_epi8((int8_t)Ai2[0]);
        __m512i an2_0 = _mm512_set1_epi8((int8_t)Ai2[1]);
        __m512i ap2_1 = _mm512_set1_epi8((int8_t)Ai2[2]);
        __m512i an2_1 = _mm512_set1_epi8((int8_t)Ai2[3]);

        __m512i ap3_0 = _mm512_set1_epi8((int8_t)Ai3[0]);
        __m512i an3_0 = _mm512_set1_epi8((int8_t)Ai3[1]);
        __m512i ap3_1 = _mm512_set1_epi8((int8_t)Ai3[2]);
        __m512i an3_1 = _mm512_set1_epi8((int8_t)Ai3[3]);

        int* C0 = C + (i + 0) * m;
        int* C1 = C + (i + 1) * m;
        int* C2 = C + (i + 2) * m;
        int* C3 = C + (i + 3) * m;

        // Sweep across all m columns in 64-col chunks
        // k_bytes=2 → 2 B loads per 64-col chunk, shared across 4 rows
        int j = 0;
        for (; j + 64 <= m; j += 64) {
            // Load B for k=0 and k=1 (shared across all 4 rows)
            __m512i b0 = _mm512_loadu_si512((const __m512i*)(B + 0 * m + j));
            __m512i b1 = _mm512_loadu_si512((const __m512i*)(B + 1 * m + j));

            // Compute diff for each row (k-loop fully unrolled: t=0 then t=1)
            __m512i acc0 = _mm512_setzero_si512();
            __m512i acc1 = _mm512_setzero_si512();
            __m512i acc2 = _mm512_setzero_si512();
            __m512i acc3 = _mm512_setzero_si512();

            COMPUTE_DIFF_ACC(ap0_0, an0_0, b0, acc0);
            COMPUTE_DIFF_ACC(ap0_1, an0_1, b1, acc0);

            COMPUTE_DIFF_ACC(ap1_0, an1_0, b0, acc1);
            COMPUTE_DIFF_ACC(ap1_1, an1_1, b1, acc1);

            COMPUTE_DIFF_ACC(ap2_0, an2_0, b0, acc2);
            COMPUTE_DIFF_ACC(ap2_1, an2_1, b1, acc2);

            COMPUTE_DIFF_ACC(ap3_0, an3_0, b0, acc3);
            COMPUTE_DIFF_ACC(ap3_1, an3_1, b1, acc3);

            // Widen and store
            WIDEN_STORE(acc0, C0 + j);
            WIDEN_STORE(acc1, C1 + j);
            WIDEN_STORE(acc2, C2 + j);
            WIDEN_STORE(acc3, C3 + j);
        }
        // Scalar tail
        for (; j < m; j++) {
            for (int r = 0; r < 4; r++) {
                const uint8_t* Ar = A + (i + r) * 2 * 2;
                int sum = 0;
                for (int t = 0; t < 2; t++) {
                    uint8_t a_p = Ar[t*2+0], a_n = Ar[t*2+1];
                    uint8_t b_v = B[t * m + j];
                    sum += __builtin_popcount((unsigned)((a_p | b_v) & (uint8_t)(a_n | (uint8_t)~b_v)));
                    sum -= __builtin_popcount((unsigned)((uint8_t)(a_p | (uint8_t)~b_v) & (a_n | b_v)));
                }
                C[(i + r) * m + j] = sum;
            }
        }
    }
    // Remaining rows (if n not divisible by 4)
    for (; i < n; i++) {
        const uint8_t* Ai = A + i * 2 * 2;
        __m512i ap0 = _mm512_set1_epi8((int8_t)Ai[0]);
        __m512i an0 = _mm512_set1_epi8((int8_t)Ai[1]);
        __m512i ap1 = _mm512_set1_epi8((int8_t)Ai[2]);
        __m512i an1 = _mm512_set1_epi8((int8_t)Ai[3]);
        int* Ci = C + i * m;
        for (int j = 0; j + 64 <= m; j += 64) {
            __m512i b0 = _mm512_loadu_si512((const __m512i*)(B + 0 * m + j));
            __m512i b1 = _mm512_loadu_si512((const __m512i*)(B + 1 * m + j));
            __m512i acc = _mm512_setzero_si512();
            COMPUTE_DIFF_ACC(ap0, an0, b0, acc);
            COMPUTE_DIFF_ACC(ap1, an1, b1, acc);
            WIDEN_STORE(acc, Ci + j);
        }
        for (int j = (m/64)*64; j < m; j++) {
            int sum = 0;
            for (int t = 0; t < 2; t++) {
                uint8_t a_p = Ai[t*2+0], a_n = Ai[t*2+1];
                uint8_t b_v = B[t * m + j];
                sum += __builtin_popcount((unsigned)((a_p | b_v) & (uint8_t)(a_n | (uint8_t)~b_v)));
                sum -= __builtin_popcount((unsigned)((uint8_t)(a_p | (uint8_t)~b_v) & (a_n | b_v)));
            }
            Ci[j] = sum;
        }
    }
}

// -----------------------------------------------------------------------
// GENERAL path: standard row-streaming for medium/large
// -----------------------------------------------------------------------
static void gemm_row_stream(uint8_t* A, uint8_t* B, int* C,
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
                acc8 = _mm512_add_epi8(acc8, _mm512_sub_epi8(
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(a_pos[t], a_neg[t], b, 0xD8)),
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(a_pos[t], a_neg[t], b, 0xE4))));
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
    if (k_bytes <= 2) {
        // Small benchmark specialized path: 4-row, k_bytes=2, fully unrolled
        gemm_small_4row(A, B, C, n, m);
    } else {
        // Medium/large: standard row-streaming
        gemm_row_stream(A, B, C, n, m, k_bytes);
    }
}
"""
