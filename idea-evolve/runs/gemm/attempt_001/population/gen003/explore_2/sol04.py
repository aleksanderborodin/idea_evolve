# fitness: 341.78
"""
vpshufb 4-row kernel v2: int8-only accumulation, widen once at end.

Key lesson from sol03: initializing 16 acc32 zmm registers per j-block +
16 flush ops inside k-loop dominated the runtime for small k_bytes.

This version:
1. For benchmark k_bytes (≤7): accumulate entirely in int8 (safe: max = 7×8=56 < 127)
   Widen only once per j-block. 4 acc8 zmm init vs 20 zmm in sol03.
2. For large k (correctness): fall back to sol01 structure with flush.
3. NT stores for large benchmark (only when C is 64-byte aligned).

Register allocation for the 4-row fast path:
- 4 acc8 zmm (one per row)
- 1 vb zmm
- 1 lo_idx zmm (shared across rows)
- 1 hi_idx zmm (shared across rows)
- 1 mask_lo zmm (constant)
- 8 LUT zmm (loaded from stack, 2 per row per k-byte, reused)
Total: 16 zmm registers used simultaneously
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

// Helper: widen zmm int8 → 4×zmm int32 and store (64 int32 values)
static inline void store_int8_as_int32(const __m512i acc8, int* dst, bool use_nt) {
    __m512i r0 = _mm512_cvtepi8_epi32(_mm512_castsi512_si128(acc8));
    __m512i r1 = _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8, 1));
    __m512i r2 = _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8, 2));
    __m512i r3 = _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8, 3));
    if (use_nt) {
        _mm512_stream_si512((__m512i*)(dst +  0), r0);
        _mm512_stream_si512((__m512i*)(dst + 16), r1);
        _mm512_stream_si512((__m512i*)(dst + 32), r2);
        _mm512_stream_si512((__m512i*)(dst + 48), r3);
    } else {
        _mm512_storeu_si512((__m512i*)(dst +  0), r0);
        _mm512_storeu_si512((__m512i*)(dst + 16), r1);
        _mm512_storeu_si512((__m512i*)(dst + 32), r2);
        _mm512_storeu_si512((__m512i*)(dst + 48), r3);
    }
}

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    if (!g_lut_init) init_nibble_lut();

    const int k_bytes = k / 8;
    memset(C, 0, (size_t)n * m * sizeof(int));

    const bool use_nt = ((size_t)n * m * 4 > 8 * 1024 * 1024) &&
                        (((uintptr_t)C & 63) == 0);

    const __m512i mask_lo = _mm512_set1_epi8(0x0F);

    // LUT storage on stack: [row_in_block][k_byte][nibble]
    // For 4 rows × 7 k_bytes × 2 × 16 bytes = 896 bytes — fits in L1
    alignas(64) int8_t lut_lo[4][8][16];
    alignas(64) int8_t lut_hi[4][8][16];

    // Fast path: k_bytes <= 8 (covers all benchmark sizes)
    if (k_bytes <= 8) {
        int i = 0;
        for (; i + 4 <= n; i += 4) {
            // Precompute LUTs for 4 rows outside j-loop
            for (int r = 0; r < 4; r++) {
                for (int t = 0; t < k_bytes; t++) {
                    uint8_t ap = A[((i + r) * k_bytes + t) * 2 + 0];
                    uint8_t an = A[((i + r) * k_bytes + t) * 2 + 1];
                    memcpy(lut_lo[r][t], g_nibble_lut[(ap & 0xF) | ((an & 0xF) << 4)], 16);
                    memcpy(lut_hi[r][t], g_nibble_lut[(ap >> 4) | ((an >> 4) << 4)], 16);
                }
            }

            int j = 0;
            for (; j + 64 <= m; j += 64) {
                // 4 int8 accumulators (one per row), safe for k_bytes <= 15
                __m512i acc8_0 = _mm512_setzero_si512();
                __m512i acc8_1 = _mm512_setzero_si512();
                __m512i acc8_2 = _mm512_setzero_si512();
                __m512i acc8_3 = _mm512_setzero_si512();

                #pragma GCC unroll 8
                for (int t = 0; t < k_bytes; t++) {
                    // Load B once, shared across 4 rows
                    __m512i vb = _mm512_loadu_si512(B + t * m + j);
                    // Nibble extraction (shared, 3 ops)
                    __m512i lo_idx = _mm512_and_si512(vb, mask_lo);
                    __m512i hi_idx = _mm512_and_si512(_mm512_srli_epi16(vb, 4), mask_lo);

                    // Apply LUT for each row (LUT loaded from L1)
                    __m512i ll, lh;
                    ll = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_lo[0][t]));
                    lh = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_hi[0][t]));
                    acc8_0 = _mm512_add_epi8(acc8_0,
                        _mm512_add_epi8(_mm512_shuffle_epi8(ll, lo_idx),
                                        _mm512_shuffle_epi8(lh, hi_idx)));

                    ll = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_lo[1][t]));
                    lh = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_hi[1][t]));
                    acc8_1 = _mm512_add_epi8(acc8_1,
                        _mm512_add_epi8(_mm512_shuffle_epi8(ll, lo_idx),
                                        _mm512_shuffle_epi8(lh, hi_idx)));

                    ll = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_lo[2][t]));
                    lh = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_hi[2][t]));
                    acc8_2 = _mm512_add_epi8(acc8_2,
                        _mm512_add_epi8(_mm512_shuffle_epi8(ll, lo_idx),
                                        _mm512_shuffle_epi8(lh, hi_idx)));

                    ll = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_lo[3][t]));
                    lh = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_hi[3][t]));
                    acc8_3 = _mm512_add_epi8(acc8_3,
                        _mm512_add_epi8(_mm512_shuffle_epi8(ll, lo_idx),
                                        _mm512_shuffle_epi8(lh, hi_idx)));
                }

                // Widen int8 -> int32 and store (once per j-block)
                store_int8_as_int32(acc8_0, C + (i + 0) * m + j, use_nt);
                store_int8_as_int32(acc8_1, C + (i + 1) * m + j, use_nt);
                store_int8_as_int32(acc8_2, C + (i + 2) * m + j, use_nt);
                store_int8_as_int32(acc8_3, C + (i + 3) * m + j, use_nt);
            }

            // Scalar tail
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
                    C[(i + r) * m + j] = sum;
                }
            }
        }

        if (use_nt) _mm_sfence();

        // Remainder rows (single-row fallback)
        for (; i < n; i++) {
            alignas(64) int8_t rl_lo[8][16], rl_hi[8][16];
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
                #pragma GCC unroll 8
                for (int t = 0; t < k_bytes; t++) {
                    __m512i vb = _mm512_loadu_si512(B + t * m + j);
                    __m512i lo = _mm512_and_si512(vb, mask_lo);
                    __m512i hi = _mm512_and_si512(_mm512_srli_epi16(vb, 4), mask_lo);
                    __m512i ll = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)rl_lo[t]));
                    __m512i lh = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)rl_hi[t]));
                    acc8 = _mm512_add_epi8(acc8,
                        _mm512_add_epi8(_mm512_shuffle_epi8(ll, lo),
                                        _mm512_shuffle_epi8(lh, hi)));
                }
                store_int8_as_int32(acc8, C_row + j, false);
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
    } else {
        // Slow path: k_bytes > 8, use flush-based int8->int32 conversion
        alignas(64) int8_t row_lo[256][16], row_hi[256][16];
        for (int i = 0; i < n; i++) {
            for (int t = 0; t < k_bytes; t++) {
                uint8_t ap = A[(i * k_bytes + t) * 2 + 0];
                uint8_t an = A[(i * k_bytes + t) * 2 + 1];
                memcpy(row_lo[t], g_nibble_lut[(ap & 0xF) | ((an & 0xF) << 4)], 16);
                memcpy(row_hi[t], g_nibble_lut[(ap >> 4) | ((an >> 4) << 4)], 16);
            }
            int* C_row = C + i * m;
            int j = 0;
            for (; j + 64 <= m; j += 64) {
                __m512i acc8 = _mm512_setzero_si512();
                __m512i a0 = _mm512_setzero_si512(), a1 = a0, a2 = a0, a3 = a0;
                for (int t = 0; t < k_bytes; t++) {
                    __m512i vb = _mm512_loadu_si512(B + t * m + j);
                    __m512i lo = _mm512_and_si512(vb, mask_lo);
                    __m512i hi = _mm512_and_si512(_mm512_srli_epi16(vb, 4), mask_lo);
                    __m512i ll = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)row_lo[t]));
                    __m512i lh = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)row_hi[t]));
                    acc8 = _mm512_add_epi8(acc8, _mm512_add_epi8(
                        _mm512_shuffle_epi8(ll, lo), _mm512_shuffle_epi8(lh, hi)));
                    if ((t & 15) == 14 || t == k_bytes - 1) {
                        a0 = _mm512_add_epi32(a0, _mm512_cvtepi8_epi32(_mm512_castsi512_si128(acc8)));
                        a1 = _mm512_add_epi32(a1, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8, 1)));
                        a2 = _mm512_add_epi32(a2, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8, 2)));
                        a3 = _mm512_add_epi32(a3, _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8, 3)));
                        acc8 = _mm512_setzero_si512();
                    }
                }
                _mm512_storeu_si512((__m512i*)(C_row + j +  0), a0);
                _mm512_storeu_si512((__m512i*)(C_row + j + 16), a1);
                _mm512_storeu_si512((__m512i*)(C_row + j + 32), a2);
                _mm512_storeu_si512((__m512i*)(C_row + j + 48), a3);
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
}
"""
