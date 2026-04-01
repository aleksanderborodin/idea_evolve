# fitness: 223.17

"""
Experimentator sol01: int8 accumulation + NC=128
Two optimizations from controlled experiments:
1. int8 accumulation when k_bytes <= 15 (defer widening to after k-loop) - ~11-13% kernel speedup
2. NC=128 (optimal from sweep) - ~10% medium improvement
Note: streaming stores removed — harness uses unaligned std::vector for C.
"""


def entrypoint() -> str:
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>
#include <algorithm>

#define MC 64
#define NC 128

static void pack_A(int mc, int kc, const uint8_t* A, int k_bytes, uint8_t* Ap) {
    for (int i = 0; i < mc; i += 4) {
        int rmax = mc-i; if (rmax>4) rmax=4;
        for (int k = 0; k < kc; ++k)
            for (int r = 0; r < 4; ++r) {
                if (r < rmax) {
                    Ap[((i/4)*kc+k)*8+r*2]   = A[((i+r)*k_bytes+k)*2];
                    Ap[((i/4)*kc+k)*8+r*2+1] = A[((i+r)*k_bytes+k)*2+1];
                } else {
                    Ap[((i/4)*kc+k)*8+r*2] = Ap[((i/4)*kc+k)*8+r*2+1] = 0;
                }
            }
    }
}

static void pack_B(int kc, int nc, const uint8_t* B, int m, uint8_t* Bp) {
    for (int j = 0; j < nc; j += 64) {
        int cmax = nc-j;
        uint8_t* dst = Bp + (j/64)*kc*64;
        if (cmax >= 64) {
            for (int k = 0; k < kc; ++k)
                _mm512_storeu_si512((__m512i*)(dst+k*64),
                    _mm512_loadu_si512((const __m512i*)(B+k*m+j)));
        } else {
            __mmask64 mask = ((__mmask64)1 << cmax) - 1;
            for (int k = 0; k < kc; ++k)
                _mm512_storeu_si512((__m512i*)(dst+k*64),
                    _mm512_maskz_loadu_epi8(mask, (const __m512i*)(B+k*m+j)));
        }
    }
}

// int8 accumulation: used when k_bytes <= 15 (max accumulated = +-120, within int8)
static inline void micro_kernel_int8(
    int kc, const uint8_t* __restrict__ A_p,
    const uint8_t* __restrict__ B_p,
    int* __restrict__ C, int m, int cur_mc, int cur_nc
) {
    __m512i acc[4];
    for (int r = 0; r < 4; ++r) acc[r] = _mm512_setzero_si512();

    #pragma GCC unroll 15
    for (int k = 0; k < kc; ++k) {
        __m512i vb = _mm512_loadu_si512((const __m512i*)(B_p+k*64));
        const uint8_t* a = A_p+k*8;
        for (int r = 0; r < 4; ++r) {
            __m512i vp = _mm512_set1_epi8((int8_t)a[r*2]);
            __m512i vn = _mm512_set1_epi8((int8_t)a[r*2+1]);
            __m512i diff = _mm512_sub_epi8(
                _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp, vn, vb, 0xD8)),
                _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp, vn, vb, 0xE4))
            );
            acc[r] = _mm512_add_epi8(acc[r], diff);
        }
    }

    if (cur_nc == 64 && cur_mc == 4) {
        for (int r = 0; r < 4; ++r) {
            int* Cr = C + r * m;
            __m128i q0 = _mm512_castsi512_si128(acc[r]);
            __m128i q1 = _mm512_extracti32x4_epi32(acc[r], 1);
            __m128i q2 = _mm512_extracti32x4_epi32(acc[r], 2);
            __m128i q3 = _mm512_extracti32x4_epi32(acc[r], 3);
            _mm512_storeu_si512((__m512i*)(Cr +  0), _mm512_cvtepi8_epi32(q0));
            _mm512_storeu_si512((__m512i*)(Cr + 16), _mm512_cvtepi8_epi32(q1));
            _mm512_storeu_si512((__m512i*)(Cr + 32), _mm512_cvtepi8_epi32(q2));
            _mm512_storeu_si512((__m512i*)(Cr + 48), _mm512_cvtepi8_epi32(q3));
        }
    } else {
        for (int r = 0; r < cur_mc; ++r) {
            int32_t tmp[64];
            __m128i q0 = _mm512_castsi512_si128(acc[r]);
            __m128i q1 = _mm512_extracti32x4_epi32(acc[r], 1);
            __m128i q2 = _mm512_extracti32x4_epi32(acc[r], 2);
            __m128i q3 = _mm512_extracti32x4_epi32(acc[r], 3);
            _mm512_storeu_si512((__m512i*)&tmp[ 0], _mm512_cvtepi8_epi32(q0));
            _mm512_storeu_si512((__m512i*)&tmp[16], _mm512_cvtepi8_epi32(q1));
            _mm512_storeu_si512((__m512i*)&tmp[32], _mm512_cvtepi8_epi32(q2));
            _mm512_storeu_si512((__m512i*)&tmp[48], _mm512_cvtepi8_epi32(q3));
            for (int c = 0; c < cur_nc; ++c) C[r*m+c] = tmp[c];
        }
    }
}

// int16 accumulation: fallback for large k_bytes
static inline void micro_kernel_int16(
    int kc, const uint8_t* __restrict__ A_p,
    const uint8_t* __restrict__ B_p,
    int* __restrict__ C, int m, int cur_mc, int cur_nc
) {
    __m512i acc[4][2];
    for (int r = 0; r < 4; ++r) acc[r][0] = acc[r][1] = _mm512_setzero_si512();

    for (int k = 0; k < kc; ++k) {
        __m512i vb = _mm512_loadu_si512((const __m512i*)(B_p+k*64));
        const uint8_t* a = A_p+k*8;
        for (int r = 0; r < 4; ++r) {
            __m512i vp = _mm512_set1_epi8((int8_t)a[r*2]);
            __m512i vn = _mm512_set1_epi8((int8_t)a[r*2+1]);
            __m512i diff = _mm512_sub_epi8(
                _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp, vn, vb, 0xD8)),
                _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp, vn, vb, 0xE4))
            );
            acc[r][0] = _mm512_add_epi16(acc[r][0], _mm512_cvtepi8_epi16(_mm512_castsi512_si256(diff)));
            acc[r][1] = _mm512_add_epi16(acc[r][1], _mm512_cvtepi8_epi16(_mm512_extracti32x8_epi32(diff,1)));
        }
    }

    if (cur_nc == 64 && cur_mc == 4) {
        for (int r = 0; r < 4; ++r) {
            int* Cr = C+r*m;
            _mm512_storeu_si512((__m512i*)(Cr+ 0), _mm512_cvtepi16_epi32(_mm512_castsi512_si256(acc[r][0])));
            _mm512_storeu_si512((__m512i*)(Cr+16), _mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(acc[r][0],1)));
            _mm512_storeu_si512((__m512i*)(Cr+32), _mm512_cvtepi16_epi32(_mm512_castsi512_si256(acc[r][1])));
            _mm512_storeu_si512((__m512i*)(Cr+48), _mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(acc[r][1],1)));
        }
    } else {
        for (int r = 0; r < cur_mc; ++r) {
            int32_t tmp[64];
            _mm512_storeu_si512((__m512i*)&tmp[ 0], _mm512_cvtepi16_epi32(_mm512_castsi512_si256(acc[r][0])));
            _mm512_storeu_si512((__m512i*)&tmp[16], _mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(acc[r][0],1)));
            _mm512_storeu_si512((__m512i*)&tmp[32], _mm512_cvtepi16_epi32(_mm512_castsi512_si256(acc[r][1])));
            _mm512_storeu_si512((__m512i*)&tmp[48], _mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(acc[r][1],1)));
            for (int c = 0; c < cur_nc; ++c) C[r*m+c] = tmp[c];
        }
    }
}

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    int k_bytes = k/8;
    alignas(64) uint8_t Ap[4096];
    alignas(64) uint8_t Bp[16384];
    bool use_int8 = (k_bytes <= 15);

    for (int jc = 0; jc < m; jc += NC) {
        int cnc = m-jc; if (cnc>NC) cnc=NC;
        pack_B(k_bytes, cnc, B+jc, m, Bp);
        for (int ic = 0; ic < n; ic += MC) {
            int cmc = n-ic; if (cmc>MC) cmc=MC;
            pack_A(cmc, k_bytes, A+(ic*k_bytes)*2, k_bytes, Ap);
            for (int jr = 0; jr < cnc; jr += 64) {
                int mnc = cnc-jr; if (mnc>64) mnc=64;
                for (int ir = 0; ir < cmc; ir += 4) {
                    int mmc = cmc-ir; if (mmc>4) mmc=4;
                    if (use_int8) {
                        micro_kernel_int8(k_bytes, Ap+(ir/4)*k_bytes*8, Bp+(jr/64)*k_bytes*64,
                            C+(ic+ir)*m+(jc+jr), m, mmc, mnc);
                    } else {
                        micro_kernel_int16(k_bytes, Ap+(ir/4)*k_bytes*8, Bp+(jr/64)*k_bytes*64,
                            C+(ic+ir)*m+(jc+jr), m, mmc, mnc);
                    }
                }
            }
        }
    }
}
"""
