# fitness: 345.25
"""
vpshufb Nibble-LUT Kernel v2 — LUTs precomputed into zmm registers outside j-loop.

sol01 was valid but slow (533 µs) due to 2 stack-load+broadcast ops per k-byte
per j-block. This version moves LUT loading outside the j-loop by precomputing
all k_bytes LUT zmm registers before the j sweep.

For benchmark sizes (k_bytes <= 7): store in 14 zmm registers (7 lo + 7 hi).
This fits in the 32-zmm register file alongside 4 acc32 + 1 acc8 + temporaries.
The inner loop then only does: load vb, extract nibbles (2 AND + 1 srli), 2 shuffles,
2 adds, accumulate. No memory loads inside the k-byte loop.

For k_bytes > 7 (correctness-only test cases): fall back to sol01-style stack loads.

Port analysis:
- vpshufb: port 0/1 (key hypothesis, vs port 5 for vpternlogd)
- This reduces port-5 pressure at the cost of 1 extra srli instruction
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

// Fast path: k_bytes <= 8, keep all LUTs in zmm registers throughout j-loop
static void gemm_fast(uint8_t* A, uint8_t* B, int* C,
                      int n, int m, int k_bytes)
{
    const __m512i mask_lo = _mm512_set1_epi8(0x0F);

    for (int i = 0; i < n; i++) {
        // Precompute zmm LUT registers for this row (stays in register file)
        __m512i lut_lo_z[8], lut_hi_z[8];
        for (int t = 0; t < k_bytes; t++) {
            uint8_t ap = A[(i * k_bytes + t) * 2 + 0];
            uint8_t an = A[(i * k_bytes + t) * 2 + 1];
            int lo_idx = (ap & 0xF) | ((an & 0xF) << 4);
            int hi_idx = (ap >> 4) | ((an >> 4) << 4);
            lut_lo_z[t] = _mm512_broadcast_i32x4(
                _mm_load_si128((const __m128i*)g_nibble_lut[lo_idx]));
            lut_hi_z[t] = _mm512_broadcast_i32x4(
                _mm_load_si128((const __m128i*)g_nibble_lut[hi_idx]));
        }

        int* C_row = C + i * m;
        int j = 0;

        for (; j + 64 <= m; j += 64) {
            __m512i acc8 = _mm512_setzero_si512();

            #pragma GCC unroll 8
            for (int t = 0; t < k_bytes; t++) {
                __m512i vb = _mm512_loadu_si512(B + t * m + j);
                __m512i lo_idx_v = _mm512_and_si512(vb, mask_lo);
                __m512i hi_idx_v = _mm512_and_si512(
                    _mm512_srli_epi16(vb, 4), mask_lo);
                acc8 = _mm512_add_epi8(acc8,
                    _mm512_add_epi8(
                        _mm512_shuffle_epi8(lut_lo_z[t], lo_idx_v),
                        _mm512_shuffle_epi8(lut_hi_z[t], hi_idx_v)));
            }

            // int8 is safe for k_bytes <= 7 (max per-byte value = 7*8 = 56 < 127)
            // Widen int8 -> int32 and store
            __m128i q0 = _mm512_castsi512_si128(acc8);
            __m128i q1 = _mm512_extracti32x4_epi32(acc8, 1);
            __m128i q2 = _mm512_extracti32x4_epi32(acc8, 2);
            __m128i q3 = _mm512_extracti32x4_epi32(acc8, 3);
            _mm512_storeu_si512((__m512i*)(C_row + j +  0), _mm512_cvtepi8_epi32(q0));
            _mm512_storeu_si512((__m512i*)(C_row + j + 16), _mm512_cvtepi8_epi32(q1));
            _mm512_storeu_si512((__m512i*)(C_row + j + 32), _mm512_cvtepi8_epi32(q2));
            _mm512_storeu_si512((__m512i*)(C_row + j + 48), _mm512_cvtepi8_epi32(q3));
        }

        // Scalar tail
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

// Slow path: k_bytes > 8, use stack-based LUT storage
static void gemm_slow(uint8_t* A, uint8_t* B, int* C,
                       int n, int m, int k_bytes)
{
    const __m512i mask_lo = _mm512_set1_epi8(0x0F);
    alignas(64) int8_t row_lut_lo[256][16];
    alignas(64) int8_t row_lut_hi[256][16];

    for (int i = 0; i < n; i++) {
        for (int t = 0; t < k_bytes; t++) {
            uint8_t ap = A[(i * k_bytes + t) * 2 + 0];
            uint8_t an = A[(i * k_bytes + t) * 2 + 1];
            int lo_idx = (ap & 0xF) | ((an & 0xF) << 4);
            int hi_idx = (ap >> 4) | ((an >> 4) << 4);
            memcpy(row_lut_lo[t], g_nibble_lut[lo_idx], 16);
            memcpy(row_lut_hi[t], g_nibble_lut[hi_idx], 16);
        }

        int* C_row = C + i * m;
        int j = 0;

        for (; j + 64 <= m; j += 64) {
            __m512i acc32_0 = _mm512_setzero_si512();
            __m512i acc32_1 = _mm512_setzero_si512();
            __m512i acc32_2 = _mm512_setzero_si512();
            __m512i acc32_3 = _mm512_setzero_si512();
            __m512i acc8 = _mm512_setzero_si512();

            for (int t = 0; t < k_bytes; t++) {
                __m512i lut_lo_z = _mm512_broadcast_i32x4(
                    _mm_load_si128((const __m128i*)row_lut_lo[t]));
                __m512i lut_hi_z = _mm512_broadcast_i32x4(
                    _mm_load_si128((const __m128i*)row_lut_hi[t]));
                __m512i vb = _mm512_loadu_si512(B + t * m + j);
                __m512i lo_idx_v = _mm512_and_si512(vb, mask_lo);
                __m512i hi_idx_v = _mm512_and_si512(
                    _mm512_srli_epi16(vb, 4), mask_lo);
                __m512i contrib = _mm512_add_epi8(
                    _mm512_shuffle_epi8(lut_lo_z, lo_idx_v),
                    _mm512_shuffle_epi8(lut_hi_z, hi_idx_v));
                acc8 = _mm512_add_epi8(acc8, contrib);
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

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    if (!g_lut_init) init_nibble_lut();
    const int k_bytes = k / 8;
    memset(C, 0, (size_t)n * m * sizeof(int));
    if (k_bytes <= 8) {
        gemm_fast(A, B, C, n, m, k_bytes);
    } else {
        gemm_slow(A, B, C, n, m, k_bytes);
    }
}
"""
