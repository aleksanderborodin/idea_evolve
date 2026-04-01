# fitness: 347.49
"""
vpshufb adaptive kernel: register LUTs for small, stack LUTs for medium/large.

Key observation from sol02/sol04:
- sol02 (1-row, register LUTs): fast for small (5.29µs) but slow for medium/large
- sol04 (4-row, stack LUTs): fast for medium/large (530/5682µs) but slow for small (13.24µs)

This solution combines both:
- k_bytes <= 2 (small benchmark): 4-row with ALL LUT zmm in registers (16 zmm total)
  → No memory loads inside hot loop, maximum throughput
- 2 < k_bytes <= 8 (medium/large benchmark): 4-row with stack LUTs
  → B-load amortization saves bandwidth

For small (n=32, k_bytes=2, 4 rows):
  4 rows × 2 k-bytes × 2 (lo+hi) = 16 zmm for LUTs
  + 4 acc8 + vb + lo + hi + mask = 23 zmm total → fits in 32!
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

static inline void widen_store(const __m512i acc8, int* dst) {
    _mm512_storeu_si512((__m512i*)(dst +  0), _mm512_cvtepi8_epi32(_mm512_castsi512_si128(acc8)));
    _mm512_storeu_si512((__m512i*)(dst + 16), _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8, 1)));
    _mm512_storeu_si512((__m512i*)(dst + 32), _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8, 2)));
    _mm512_storeu_si512((__m512i*)(dst + 48), _mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8, 3)));
}

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    if (!g_lut_init) init_nibble_lut();

    const int k_bytes = k / 8;
    memset(C, 0, (size_t)n * m * sizeof(int));
    const __m512i mask_lo = _mm512_set1_epi8(0x0F);

    if (k_bytes <= 2) {
        // FAST PATH: small benchmark (k_bytes=2), 4-row with register LUTs
        // 4 rows × 2 k-bytes × 2 (lo+hi) = 16 zmm for LUTs → stays in register file
        int i = 0;
        for (; i + 4 <= n; i += 4) {
            // Precompute 16 zmm LUT registers for 4 rows and k_bytes LUT pairs
            __m512i lz0[2], hz0[2];  // row 0 lo/hi LUTs per k-byte
            __m512i lz1[2], hz1[2];  // row 1
            __m512i lz2[2], hz2[2];  // row 2
            __m512i lz3[2], hz3[2];  // row 3
            for (int t = 0; t < k_bytes; t++) {
                auto make_lut = [&](int row, int kt, __m512i& lz, __m512i& hz) {
                    uint8_t ap = A[((i + row) * k_bytes + kt) * 2 + 0];
                    uint8_t an = A[((i + row) * k_bytes + kt) * 2 + 1];
                    lz = _mm512_broadcast_i32x4(_mm_load_si128(
                        (const __m128i*)g_nibble_lut[(ap & 0xF) | ((an & 0xF) << 4)]));
                    hz = _mm512_broadcast_i32x4(_mm_load_si128(
                        (const __m128i*)g_nibble_lut[(ap >> 4) | ((an >> 4) << 4)]));
                };
                make_lut(0, t, lz0[t], hz0[t]);
                make_lut(1, t, lz1[t], hz1[t]);
                make_lut(2, t, lz2[t], hz2[t]);
                make_lut(3, t, lz3[t], hz3[t]);
            }

            int j = 0;
            for (; j + 64 <= m; j += 64) {
                __m512i acc0 = _mm512_setzero_si512();
                __m512i acc1 = _mm512_setzero_si512();
                __m512i acc2 = _mm512_setzero_si512();
                __m512i acc3 = _mm512_setzero_si512();

                // Fully unrolled k_bytes loop (k_bytes = 2 for this path)
                #pragma GCC unroll 2
                for (int t = 0; t < k_bytes; t++) {
                    __m512i vb = _mm512_loadu_si512(B + t * m + j);
                    __m512i lo = _mm512_and_si512(vb, mask_lo);
                    __m512i hi = _mm512_and_si512(_mm512_srli_epi16(vb, 4), mask_lo);
                    // All 4 LUT lookups use register-resident LUTs — no memory loads!
                    acc0 = _mm512_add_epi8(acc0,
                        _mm512_add_epi8(_mm512_shuffle_epi8(lz0[t], lo),
                                        _mm512_shuffle_epi8(hz0[t], hi)));
                    acc1 = _mm512_add_epi8(acc1,
                        _mm512_add_epi8(_mm512_shuffle_epi8(lz1[t], lo),
                                        _mm512_shuffle_epi8(hz1[t], hi)));
                    acc2 = _mm512_add_epi8(acc2,
                        _mm512_add_epi8(_mm512_shuffle_epi8(lz2[t], lo),
                                        _mm512_shuffle_epi8(hz2[t], hi)));
                    acc3 = _mm512_add_epi8(acc3,
                        _mm512_add_epi8(_mm512_shuffle_epi8(lz3[t], lo),
                                        _mm512_shuffle_epi8(hz3[t], hi)));
                }

                widen_store(acc0, C + (i + 0) * m + j);
                widen_store(acc1, C + (i + 1) * m + j);
                widen_store(acc2, C + (i + 2) * m + j);
                widen_store(acc3, C + (i + 3) * m + j);
            }

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
        // Remainder rows
        for (; i < n; i++) {
            __m512i lz[2], hz[2];
            for (int t = 0; t < k_bytes; t++) {
                uint8_t ap = A[(i * k_bytes + t) * 2 + 0];
                uint8_t an = A[(i * k_bytes + t) * 2 + 1];
                lz[t] = _mm512_broadcast_i32x4(_mm_load_si128(
                    (const __m128i*)g_nibble_lut[(ap & 0xF) | ((an & 0xF) << 4)]));
                hz[t] = _mm512_broadcast_i32x4(_mm_load_si128(
                    (const __m128i*)g_nibble_lut[(ap >> 4) | ((an >> 4) << 4)]));
            }
            int* C_row = C + i * m;
            int j = 0;
            for (; j + 64 <= m; j += 64) {
                __m512i acc = _mm512_setzero_si512();
                #pragma GCC unroll 2
                for (int t = 0; t < k_bytes; t++) {
                    __m512i vb = _mm512_loadu_si512(B + t * m + j);
                    __m512i lo = _mm512_and_si512(vb, mask_lo);
                    __m512i hi = _mm512_and_si512(_mm512_srli_epi16(vb, 4), mask_lo);
                    acc = _mm512_add_epi8(acc, _mm512_add_epi8(
                        _mm512_shuffle_epi8(lz[t], lo),
                        _mm512_shuffle_epi8(hz[t], hi)));
                }
                widen_store(acc, C_row + j);
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
    } else if (k_bytes <= 8) {
        // MEDIUM PATH: 4-row with stack LUTs (sol04 approach)
        alignas(64) int8_t lut_lo[4][8][16], lut_hi[4][8][16];
        int i = 0;
        for (; i + 4 <= n; i += 4) {
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
                __m512i acc0 = _mm512_setzero_si512();
                __m512i acc1 = _mm512_setzero_si512();
                __m512i acc2 = _mm512_setzero_si512();
                __m512i acc3 = _mm512_setzero_si512();
                #pragma GCC unroll 8
                for (int t = 0; t < k_bytes; t++) {
                    __m512i vb = _mm512_loadu_si512(B + t * m + j);
                    __m512i lo = _mm512_and_si512(vb, mask_lo);
                    __m512i hi = _mm512_and_si512(_mm512_srli_epi16(vb, 4), mask_lo);
                    __m512i ll, lh;
                    ll = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_lo[0][t]));
                    lh = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_hi[0][t]));
                    acc0 = _mm512_add_epi8(acc0, _mm512_add_epi8(_mm512_shuffle_epi8(ll,lo),_mm512_shuffle_epi8(lh,hi)));
                    ll = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_lo[1][t]));
                    lh = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_hi[1][t]));
                    acc1 = _mm512_add_epi8(acc1, _mm512_add_epi8(_mm512_shuffle_epi8(ll,lo),_mm512_shuffle_epi8(lh,hi)));
                    ll = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_lo[2][t]));
                    lh = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_hi[2][t]));
                    acc2 = _mm512_add_epi8(acc2, _mm512_add_epi8(_mm512_shuffle_epi8(ll,lo),_mm512_shuffle_epi8(lh,hi)));
                    ll = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_lo[3][t]));
                    lh = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)lut_hi[3][t]));
                    acc3 = _mm512_add_epi8(acc3, _mm512_add_epi8(_mm512_shuffle_epi8(ll,lo),_mm512_shuffle_epi8(lh,hi)));
                }
                widen_store(acc0, C + (i + 0) * m + j);
                widen_store(acc1, C + (i + 1) * m + j);
                widen_store(acc2, C + (i + 2) * m + j);
                widen_store(acc3, C + (i + 3) * m + j);
            }
            for (; j < m; j++) {
                for (int r = 0; r < 4; r++) {
                    int sum = 0; int row = i + r;
                    for (int t = 0; t < k_bytes; t++) {
                        uint8_t ap = A[(row*k_bytes+t)*2+0], an = A[(row*k_bytes+t)*2+1];
                        uint8_t bv = B[t*m+j];
                        sum += __builtin_popcount((unsigned)((ap|bv)&(uint8_t)(an|~bv)));
                        sum -= __builtin_popcount((unsigned)((uint8_t)(ap|~bv)&(an|bv)));
                    }
                    C[row*m+j] = sum;
                }
            }
        }
        for (; i < n; i++) {
            __m512i lz[8], hz[8];
            for (int t = 0; t < k_bytes; t++) {
                uint8_t ap = A[(i*k_bytes+t)*2+0], an = A[(i*k_bytes+t)*2+1];
                lz[t] = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)g_nibble_lut[(ap&0xF)|((an&0xF)<<4)]));
                hz[t] = _mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)g_nibble_lut[(ap>>4)|((an>>4)<<4)]));
            }
            int* C_row = C + i * m;
            int j = 0;
            for (; j + 64 <= m; j += 64) {
                __m512i acc = _mm512_setzero_si512();
                #pragma GCC unroll 8
                for (int t = 0; t < k_bytes; t++) {
                    __m512i vb = _mm512_loadu_si512(B + t * m + j);
                    __m512i lo = _mm512_and_si512(vb, mask_lo);
                    __m512i hi = _mm512_and_si512(_mm512_srli_epi16(vb, 4), mask_lo);
                    acc = _mm512_add_epi8(acc, _mm512_add_epi8(
                        _mm512_shuffle_epi8(lz[t], lo), _mm512_shuffle_epi8(hz[t], hi)));
                }
                widen_store(acc, C_row + j);
            }
            for (; j < m; j++) {
                int sum = 0;
                for (int t = 0; t < k_bytes; t++) {
                    uint8_t ap=A[(i*k_bytes+t)*2+0], an=A[(i*k_bytes+t)*2+1], bv=B[t*m+j];
                    sum += __builtin_popcount((unsigned)((ap|bv)&(uint8_t)(an|~bv)));
                    sum -= __builtin_popcount((unsigned)((uint8_t)(ap|~bv)&(an|bv)));
                }
                C_row[j] = sum;
            }
        }
    } else {
        // SLOW PATH: large k_bytes, single-row with flush
        alignas(64) int8_t row_lo[256][16], row_hi[256][16];
        for (int i = 0; i < n; i++) {
            for (int t = 0; t < k_bytes; t++) {
                uint8_t ap=A[(i*k_bytes+t)*2+0], an=A[(i*k_bytes+t)*2+1];
                memcpy(row_lo[t], g_nibble_lut[(ap&0xF)|((an&0xF)<<4)], 16);
                memcpy(row_hi[t], g_nibble_lut[(ap>>4)|((an>>4)<<4)], 16);
            }
            int* C_row = C + i * m;
            int j = 0;
            for (; j + 64 <= m; j += 64) {
                __m512i acc8 = _mm512_setzero_si512();
                __m512i a0=_mm512_setzero_si512(),a1=a0,a2=a0,a3=a0;
                for (int t = 0; t < k_bytes; t++) {
                    __m512i vb=_mm512_loadu_si512(B+t*m+j);
                    __m512i lo=_mm512_and_si512(vb,mask_lo);
                    __m512i hi=_mm512_and_si512(_mm512_srli_epi16(vb,4),mask_lo);
                    __m512i ll=_mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)row_lo[t]));
                    __m512i lh=_mm512_broadcast_i32x4(_mm_load_si128((const __m128i*)row_hi[t]));
                    acc8=_mm512_add_epi8(acc8,_mm512_add_epi8(_mm512_shuffle_epi8(ll,lo),_mm512_shuffle_epi8(lh,hi)));
                    if((t&15)==14||t==k_bytes-1){
                        a0=_mm512_add_epi32(a0,_mm512_cvtepi8_epi32(_mm512_castsi512_si128(acc8)));
                        a1=_mm512_add_epi32(a1,_mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8,1)));
                        a2=_mm512_add_epi32(a2,_mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8,2)));
                        a3=_mm512_add_epi32(a3,_mm512_cvtepi8_epi32(_mm512_extracti32x4_epi32(acc8,3)));
                        acc8=_mm512_setzero_si512();
                    }
                }
                _mm512_storeu_si512((__m512i*)(C_row+j+ 0),a0);
                _mm512_storeu_si512((__m512i*)(C_row+j+16),a1);
                _mm512_storeu_si512((__m512i*)(C_row+j+32),a2);
                _mm512_storeu_si512((__m512i*)(C_row+j+48),a3);
            }
            for(;j<m;j++){
                int sum=0;
                for(int t=0;t<k_bytes;t++){
                    uint8_t ap=A[(i*k_bytes+t)*2+0],an=A[(i*k_bytes+t)*2+1],bv=B[t*m+j];
                    sum+=__builtin_popcount((unsigned)((ap|bv)&(uint8_t)(an|~bv)));
                    sum-=__builtin_popcount((unsigned)((uint8_t)(ap|~bv)&(an|bv)));
                }
                C_row[j]=sum;
            }
        }
    }
}
"""
