# fitness: 419.67
"""
vpshufb 4-row kernel with NT stores.

Key insight from sol01/sol02: vpshufb is ALSO a port-5 instruction (not port 0/1).
The hypothesis in idea_018 was incorrect — port-5 pressure is not relieved.

However, a 4-row kernel amortizes the B load across 4 rows, reducing memory traffic
by 4x. The nibble extraction (AND + srli + AND) is computed once and reused for all
4 rows. This could improve throughput for memory-bandwidth-bound workloads.

This solution tests:
1. Does 4-row amortization compensate for vpshufb's port-5 inefficiency?
2. Do NT stores help for large (32 MB C output)?

Inner loop per k-byte per 4-row block:
- 1 B load (shared for all 4 rows)
- 3 nibble extraction ops (shared)
- 8 stack-LUT loads (2 per row: lo + hi) from L1 cache
- 8 vpshufb + 8 add = 16 compute ops for 4 rows
Total: 20 ops for 4 rows vs 20 for single-row × 4 = 80 (4x reduction in B loads)
"""

def entrypoint():
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>

alignas(64) static int8_t g_nibble_lut[256][16];
static int g_lut_init = 0;

static void init_nibble_lut() {
    for (int ap4 = 0; ap4 < 16; ap4++) {
        for (int an4 = 0; an4 < 16; an4++) {
            int idx = ap4 | (an4 << 4);
            for (int b4 = 0; b4 < 16; b4++) {
                int diff = 0;
                for (int bit = 0; bit < 4; bit++) {
                    int ap_b = (ap4 >> bit) & 1;
                    int an_b = (an4 >> bit) & 1;
                    int b_b  = (b4 >> bit) & 1;
                    int nb_b = 1 - b_b;
                    diff += (ap_b | b_b) & (an_b | nb_b);
                    diff -= (ap_b | nb_b) & (an_b | b_b);
                }
                g_nibble_lut[idx][b4] = (int8_t)diff;
            }
        }
    }
    g_lut_init = 1;
}

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    if (!g_lut_init) init_nibble_lut();

    const int k_bytes = k / 8;
    memset(C, 0, (size_t)n * m * sizeof(int));

    // NT store threshold: only use NT when C > L3 size (8MB) and C is 64-byte aligned
    const bool use_nt = ((size_t)n * m * 4 > 8 * 1024 * 1024) &&
                        (((uintptr_t)C & 63) == 0);

    const __m512i mask_lo = _mm512_set1_epi8(0x0F);

    // LUT storage: [row_in_block][k_byte][nibble], up to 4 rows and 256 k_bytes
    // Stack allocation: 4 × 256 × 2 × 16 = 32 KB
    // For benchmark k_bytes <= 7 and 4 rows: 4 × 7 × 2 × 16 = 896 bytes — tiny
    alignas(64) int8_t lut_lo[4][256][16];
    alignas(64) int8_t lut_hi[4][256][16];

    // Process rows in blocks of 4 (with fallback for remainder)
    int i = 0;
    for (; i + 4 <= n; i += 4) {
        // Precompute LUTs for 4 rows, all k_bytes (outside j-loop)
        for (int r = 0; r < 4; r++) {
            for (int t = 0; t < k_bytes; t++) {
                uint8_t ap = A[((i + r) * k_bytes + t) * 2 + 0];
                uint8_t an = A[((i + r) * k_bytes + t) * 2 + 1];
                int lo_idx = (ap & 0xF) | ((an & 0xF) << 4);
                int hi_idx = (ap >> 4) | ((an >> 4) << 4);
                memcpy(lut_lo[r][t], g_nibble_lut[lo_idx], 16);
                memcpy(lut_hi[r][t], g_nibble_lut[hi_idx], 16);
            }
        }

        int j = 0;
        for (; j + 64 <= m; j += 64) {
            // int8 accumulators, one per row (safe for k_bytes <= 15)
            __m512i acc8_0 = _mm512_setzero_si512();
            __m512i acc8_1 = _mm512_setzero_si512();
            __m512i acc8_2 = _mm512_setzero_si512();
            __m512i acc8_3 = _mm512_setzero_si512();

            // For k_bytes > 15, we need int32 accumulation
            __m512i acc32_0_a = _mm512_setzero_si512();
            __m512i acc32_0_b = _mm512_setzero_si512();
            __m512i acc32_0_c = _mm512_setzero_si512();
            __m512i acc32_0_d = _mm512_setzero_si512();
            __m512i acc32_1_a = _mm512_setzero_si512();
            __m512i acc32_1_b = _mm512_setzero_si512();
            __m512i acc32_1_c = _mm512_setzero_si512();
            __m512i acc32_1_d = _mm512_setzero_si512();
            __m512i acc32_2_a = _mm512_setzero_si512();
            __m512i acc32_2_b = _mm512_setzero_si512();
            __m512i acc32_2_c = _mm512_setzero_si512();
            __m512i acc32_2_d = _mm512_setzero_si512();
            __m512i acc32_3_a = _mm512_setzero_si512();
            __m512i acc32_3_b = _mm512_setzero_si512();
            __m512i acc32_3_c = _mm512_setzero_si512();
            __m512i acc32_3_d = _mm512_setzero_si512();

            for (int t = 0; t < k_bytes; t++) {
                // Load B once, shared by all 4 rows — key amortization
                __m512i vb = _mm512_loadu_si512(B + t * m + j);

                // Nibble extraction (shared, computed once for all rows)
                __m512i lo_idx_v = _mm512_and_si512(vb, mask_lo);
                __m512i hi_idx_v = _mm512_and_si512(
                    _mm512_srli_epi16(vb, 4), mask_lo);

                // Row 0: load LUTs from stack (L1 hits), apply vpshufb
                __m512i ll0 = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_lo[0][t]));
                __m512i lh0 = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_hi[0][t]));
                acc8_0 = _mm512_add_epi8(acc8_0,
                    _mm512_add_epi8(_mm512_shuffle_epi8(ll0, lo_idx_v),
                                    _mm512_shuffle_epi8(lh0, hi_idx_v)));

                // Row 1
                __m512i ll1 = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_lo[1][t]));
                __m512i lh1 = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_hi[1][t]));
                acc8_1 = _mm512_add_epi8(acc8_1,
                    _mm512_add_epi8(_mm512_shuffle_epi8(ll1, lo_idx_v),
                                    _mm512_shuffle_epi8(lh1, hi_idx_v)));

                // Row 2
                __m512i ll2 = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_lo[2][t]));
                __m512i lh2 = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_hi[2][t]));
                acc8_2 = _mm512_add_epi8(acc8_2,
                    _mm512_add_epi8(_mm512_shuffle_epi8(ll2, lo_idx_v),
                                    _mm512_shuffle_epi8(lh2, hi_idx_v)));

                // Row 3
                __m512i ll3 = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_lo[3][t]));
                __m512i lh3 = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_hi[3][t]));
                acc8_3 = _mm512_add_epi8(acc8_3,
                    _mm512_add_epi8(_mm512_shuffle_epi8(ll3, lo_idx_v),
                                    _mm512_shuffle_epi8(lh3, hi_idx_v)));

                // Flush int8 -> int32 every 15 k-bytes
                if ((t & 15) == 14 || t == k_bytes - 1) {
                    acc32_0_a = _mm512_add_epi32(acc32_0_a, _mm512_cvtepi8_epi32(_mm512_castsi512_si128(acc8_0)));
                    acc32_0_b = _mm512_add_epi32(acc32_0_b, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8_0,1)));
                    acc32_0_c = _mm512_add_epi32(acc32_0_c, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8_0,2)));
                    acc32_0_d = _mm512_add_epi32(acc32_0_d, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8_0,3)));
                    acc32_1_a = _mm512_add_epi32(acc32_1_a, _mm512_cvtepi8_epi32(_mm512_castsi512_si128(acc8_1)));
                    acc32_1_b = _mm512_add_epi32(acc32_1_b, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8_1,1)));
                    acc32_1_c = _mm512_add_epi32(acc32_1_c, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8_1,2)));
                    acc32_1_d = _mm512_add_epi32(acc32_1_d, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8_1,3)));
                    acc32_2_a = _mm512_add_epi32(acc32_2_a, _mm512_cvtepi8_epi32(_mm512_castsi512_si128(acc8_2)));
                    acc32_2_b = _mm512_add_epi32(acc32_2_b, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8_2,1)));
                    acc32_2_c = _mm512_add_epi32(acc32_2_c, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8_2,2)));
                    acc32_2_d = _mm512_add_epi32(acc32_2_d, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8_2,3)));
                    acc32_3_a = _mm512_add_epi32(acc32_3_a, _mm512_cvtepi8_epi32(_mm512_castsi512_si128(acc8_3)));
                    acc32_3_b = _mm512_add_epi32(acc32_3_b, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8_3,1)));
                    acc32_3_c = _mm512_add_epi32(acc32_3_c, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8_3,2)));
                    acc32_3_d = _mm512_add_epi32(acc32_3_d, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8_3,3)));
                    acc8_0 = acc8_1 = acc8_2 = acc8_3 = _mm512_setzero_si512();
                }
            }

// Macro to store 64 int32 values to C_row with optional NT stores
#define STORE_ROW(row_offset, a, b, c, d) do { \
    int* dst = C + (i + (row_offset)) * m + j; \
    if (use_nt) { \
        _mm512_stream_si512((__m512i*)(dst +  0), (a)); \
        _mm512_stream_si512((__m512i*)(dst + 16), (b)); \
        _mm512_stream_si512((__m512i*)(dst + 32), (c)); \
        _mm512_stream_si512((__m512i*)(dst + 48), (d)); \
    } else { \
        _mm512_storeu_si512((__m512i*)(dst +  0), (a)); \
        _mm512_storeu_si512((__m512i*)(dst + 16), (b)); \
        _mm512_storeu_si512((__m512i*)(dst + 32), (c)); \
        _mm512_storeu_si512((__m512i*)(dst + 48), (d)); \
    } \
} while(0)

            STORE_ROW(0, acc32_0_a, acc32_0_b, acc32_0_c, acc32_0_d);
            STORE_ROW(1, acc32_1_a, acc32_1_b, acc32_1_c, acc32_1_d);
            STORE_ROW(2, acc32_2_a, acc32_2_b, acc32_2_c, acc32_2_d);
            STORE_ROW(3, acc32_3_a, acc32_3_b, acc32_3_c, acc32_3_d);
#undef STORE_ROW
        }

        // Scalar tail for m not divisible by 64 (correctness)
        for (; j < m; j++) {
            for (int r = 0; r < 4; r++) {
                int sum = 0;
                int row = i + r;
                for (int t = 0; t < k_bytes; t++) {
                    uint8_t ap = A[(row * k_bytes + t) * 2 + 0];
                    uint8_t an = A[(row * k_bytes + t) * 2 + 1];
                    uint8_t bv = B[t * m + j];
                    sum += __builtin_popcount((unsigned)((ap | bv) & (uint8_t)(an | ~bv)));
                    sum -= __builtin_popcount((unsigned)((uint8_t)(ap | ~bv) & (an | bv)));
                }
                C[row * m + j] = sum;
            }
        }
    }

    if (use_nt) _mm_sfence();

    // Handle remaining rows (n not divisible by 4) using single-row approach
    for (; i < n; i++) {
        alignas(16) int8_t rl_lo[256][16], rl_hi[256][16];
        for (int t = 0; t < k_bytes; t++) {
            uint8_t ap = A[(i * k_bytes + t) * 2 + 0];
            uint8_t an = A[(i * k_bytes + t) * 2 + 1];
            memcpy(rl_lo[t], g_nibble_lut[(ap & 0xF) | ((an & 0xF) << 4)], 16);
            memcpy(rl_hi[t], g_nibble_lut[(ap >> 4) | ((an >> 4) << 4)], 16);
        }
        int* C_row = C + i * m;
        int j = 0;
        for (; j + 64 <= m; j += 64) {
            __m512i acc8 = _mm512_setzero_si512();
            __m512i acc32_a = _mm512_setzero_si512();
            __m512i acc32_b = _mm512_setzero_si512();
            __m512i acc32_c = _mm512_setzero_si512();
            __m512i acc32_d = _mm512_setzero_si512();
            for (int t = 0; t < k_bytes; t++) {
                __m512i vb = _mm512_loadu_si512(B + t * m + j);
                __m512i lo = _mm512_and_si512(vb, mask_lo);
                __m512i hi = _mm512_and_si512(_mm512_srli_epi16(vb, 4), mask_lo);
                acc8 = _mm512_add_epi8(acc8, _mm512_add_epi8(
                    _mm512_shuffle_epi8(_mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)rl_lo[t])), lo),
                    _mm512_shuffle_epi8(_mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)rl_hi[t])), hi)));
                if ((t & 15) == 14 || t == k_bytes - 1) {
                    acc32_a = _mm512_add_epi32(acc32_a, _mm512_cvtepi8_epi32(_mm512_castsi512_si128(acc8)));
                    acc32_b = _mm512_add_epi32(acc32_b, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8, 1)));
                    acc32_c = _mm512_add_epi32(acc32_c, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8, 2)));
                    acc32_d = _mm512_add_epi32(acc32_d, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8, 3)));
                    acc8 = _mm512_setzero_si512();
                }
            }
            _mm512_storeu_si512((__m512i*)(C_row + j +  0), acc32_a);
            _mm512_storeu_si512((__m512i*)(C_row + j + 16), acc32_b);
            _mm512_storeu_si512((__m512i*)(C_row + j + 32), acc32_c);
            _mm512_storeu_si512((__m512i*)(C_row + j + 48), acc32_d);
        }
        for (; j < m; j++) {
            int sum = 0;
            for (int t = 0; t < k_bytes; t++) {
                uint8_t ap = A[(i * k_bytes + t) * 2 + 0];
                uint8_t an = A[(i * k_bytes + t) * 2 + 1];
                uint8_t bv = B[t * m + j];
                sum += __builtin_popcount((unsigned)((ap | bv) & (uint8_t)(an | ~bv)));
                sum -= __builtin_popcount((unsigned)((uint8_t)(ap | ~bv) & (an | bv)));
            }
            C_row[j] = sum;
        }
    }
}
"""
