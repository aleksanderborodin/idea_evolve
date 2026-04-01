# fitness: 533.93
"""
vpshufb Nibble-LUT Kernel — idea_018 implementation.

Approach: Replace the ternarylogic + 2×popcntb compute path with a precomputed
16-entry nibble lookup table (LUT) via _mm512_shuffle_epi8 (vpshufb).

The insight: for any 4-bit nibble combination of (a_pos nibble, a_neg nibble),
the contribution lookup table across all 16 possible B nibble values is fixed.
We precompute a 4KB global table indexed by (ap_nibble, an_nibble) → 16-byte LUT.
Then per row per k-byte, we do a 16-byte memcpy (2 table lookups) to get the LUT,
and broadcast it to all 4 lanes of a zmm for use with vpshufb.

Key hypothesis: vpshufb runs on ports 0/1 (NOT port 5), while vpternlogd runs on
port 0/5. This shifts the instruction mix away from port 5, potentially eliminating
the bottleneck identified by experimentator_1's port-pressure analysis.

int8 accumulation (safe for k_bytes<=15 per flush interval, flush every 15 k-bytes).
For benchmark sizes (k_bytes<=7), flush fires once at end.
"""

def entrypoint():
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>

// Global 4KB table: g_nibble_lut[idx][b4] where idx = ap_nibble | (an_nibble << 4)
// Contains contribution (pos_contrib - neg_contrib) for 4-bit B nibble b4
// given 4-bit a_pos and a_neg nibbles.
// 256 × 16 = 4096 bytes = 4KB (fits in L1d)
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
                    // pos: (ap|b) & (an|~b), neg: (ap|~b) & (an|b)
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

    const __m512i mask_lo = _mm512_set1_epi8(0x0F);

    // Per-row LUT storage on stack (16 bytes per k-byte, two arrays lo/hi)
    // Max k_bytes for correctness checks: k=256 → k_bytes=32
    alignas(64) int8_t row_lut_lo[256][16];
    alignas(64) int8_t row_lut_hi[256][16];

    for (int i = 0; i < n; i++) {
        // Precompute LUTs for this row via global table (L1 lookups, fast)
        for (int t = 0; t < k_bytes; t++) {
            uint8_t ap = A[(i * k_bytes + t) * 2 + 0];
            uint8_t an = A[(i * k_bytes + t) * 2 + 1];
            // lo nibble: low 4 bits of ap/an
            int lo_idx = (ap & 0xF) | ((an & 0xF) << 4);
            // hi nibble: high 4 bits of ap/an
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
                // Load LUT from stack and broadcast to all 4 zmm lanes
                __m512i lut_lo_z = _mm512_broadcast_i32x4(
                    _mm_load_si128((const __m128i*)row_lut_lo[t]));
                __m512i lut_hi_z = _mm512_broadcast_i32x4(
                    _mm_load_si128((const __m128i*)row_lut_hi[t]));

                __m512i vb = _mm512_loadu_si512(B + t * m + j);

                // Extract lo nibble (bits 0-3): AND with 0x0F
                __m512i lo_idx_v = _mm512_and_si512(vb, mask_lo);
                // Extract hi nibble (bits 4-7) → shift right 4 in 16-bit lanes,
                // then mask to 0x0F to get values 0-15 per byte
                __m512i hi_idx_v = _mm512_and_si512(
                    _mm512_srli_epi16(vb, 4), mask_lo);

                // vpshufb: parallel nibble lookup (within 128-bit lanes)
                __m512i contrib = _mm512_add_epi8(
                    _mm512_shuffle_epi8(lut_lo_z, lo_idx_v),
                    _mm512_shuffle_epi8(lut_hi_z, hi_idx_v));
                acc8 = _mm512_add_epi8(acc8, contrib);

                // Flush int8 -> int32 every 15 k-bytes (max safe: 15×8=120 < 127)
                // For benchmark sizes (k_bytes<=7), fires exactly once at end
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

        // Scalar tail for m not divisible by 64
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
