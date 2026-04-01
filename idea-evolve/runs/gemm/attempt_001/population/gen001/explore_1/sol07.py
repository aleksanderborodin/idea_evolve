# fitness: 306.6

"""
AVX-512 sol07: vectorized pack_B using zmm load+store (64x reduction in scalar ops)
Also add software prefetch for next B panel to hide DRAM latency for large.
Same 4x64 micro-kernel with direct store (sol04 approach).
"""


def entrypoint() -> str:
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>
#include <algorithm>

#define MC 64
#define NC 256

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

// Vectorized pack_B: 64 bytes per store using zmm
static void pack_B(int kc, int nc, const uint8_t* B, int m, uint8_t* Bp) {
    for (int j = 0; j < nc; j += 64) {
        int cmax = nc-j;
        uint8_t* dst_base = Bp + (j/64)*kc*64;
        if (cmax >= 64) {
            for (int k = 0; k < kc; ++k) {
                _mm512_storeu_si512((__m512i*)(dst_base + k*64),
                    _mm512_loadu_si512((const __m512i*)(B + k*m + j)));
            }
        } else {
            __mmask64 mask = ((__mmask64)1 << cmax) - 1;
            for (int k = 0; k < kc; ++k) {
                _mm512_storeu_si512((__m512i*)(dst_base + k*64),
                    _mm512_maskz_loadu_epi8(mask, (const __m512i*)(B + k*m + j)));
            }
        }
    }
}

static inline void micro_kernel(
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
            for (int c = 0; c < cur_nc; ++c) C[r*m+c] += tmp[c];
        }
    }
}

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    int k_bytes = k/8;
    memset(C, 0, (size_t)n*m*sizeof(int));
    uint8_t* Ap = (uint8_t*)_mm_malloc((size_t)(MC/4)*k_bytes*8, 64);
    uint8_t* Bp = (uint8_t*)_mm_malloc((size_t)(NC/64)*k_bytes*64, 64);
    for (int jc = 0; jc < m; jc += NC) {
        int cnc = m-jc; if (cnc>NC) cnc=NC;
        pack_B(k_bytes, cnc, B+jc, m, Bp);
        // Prefetch next B panel
        if (jc + NC < m) {
            for (int k2 = 0; k2 < k_bytes; ++k2)
                __builtin_prefetch(B + k2*m + jc + NC, 0, 1);
        }
        for (int ic = 0; ic < n; ic += MC) {
            int cmc = n-ic; if (cmc>MC) cmc=MC;
            pack_A(cmc, k_bytes, A+(ic*k_bytes)*2, k_bytes, Ap);
            for (int jr = 0; jr < cnc; jr += 64) {
                int mnc = cnc-jr; if (mnc>64) mnc=64;
                for (int ir = 0; ir < cmc; ir += 4) {
                    int mmc = cmc-ir; if (mmc>4) mmc=4;
                    micro_kernel(k_bytes, Ap+(ir/4)*k_bytes*8, Bp+(jr/64)*k_bytes*64,
                        C+(ic+ir)*m+(jc+jr), m, mmc, mnc);
                }
            }
        }
    }
    _mm_free(Ap); _mm_free(Bp);
}
"""
