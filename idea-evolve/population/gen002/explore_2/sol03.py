# fitness: 200.38

"""
No-packing, B-panel as named zmm variables (force register allocation), int16 accum.

For k_bytes > 7 (correctness test only), falls back to generic path.
For benchmark sizes (k_bytes=2,4,7): 7 named zmm vars loaded once per jc block,
reused for all n/4 row batches. No pack_A, no pack_B.
"""


def entrypoint() -> str:
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>
#include <algorithm>

// Generic fallback for k_bytes > 7 (correctness tests only).
static void gemm_large_k(const uint8_t* A, const uint8_t* B, int* C,
                          int n, int m, int k_bytes) {
    for (int jc = 0; jc < m; jc += 64) {
        for (int ic = 0; ic < n; ic++) {
            __m512i al = _mm512_setzero_si512(), ah = _mm512_setzero_si512();
            const uint8_t* ar = A + (size_t)ic * k_bytes * 2;
            for (int t = 0; t < k_bytes; t++) {
                __m512i vb = _mm512_loadu_si512((const __m512i*)(B + (size_t)t * m + jc));
                __m512i vp = _mm512_set1_epi8((int8_t)ar[t * 2]);
                __m512i vn = _mm512_set1_epi8((int8_t)ar[t * 2 + 1]);
                __m512i d = _mm512_sub_epi8(
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp, vn, vb, 0xD8)),
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp, vn, vb, 0xE4)));
                al = _mm512_add_epi16(al, _mm512_cvtepi8_epi16(_mm512_castsi512_si256(d)));
                ah = _mm512_add_epi16(ah, _mm512_cvtepi8_epi16(_mm512_extracti32x8_epi32(d, 1)));
            }
            int* Cr = C + (size_t)ic * m + jc;
            _mm512_storeu_si512((__m512i*)(Cr +  0), _mm512_cvtepi16_epi32(_mm512_castsi512_si256(al)));
            _mm512_storeu_si512((__m512i*)(Cr + 16), _mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(al, 1)));
            _mm512_storeu_si512((__m512i*)(Cr + 32), _mm512_cvtepi16_epi32(_mm512_castsi512_si256(ah)));
            _mm512_storeu_si512((__m512i*)(Cr + 48), _mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(ah, 1)));
        }
    }
}

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    int k_bytes = k / 8;

    if (k_bytes > 7) {
        gemm_large_k(A, B, C, n, m, k_bytes);
        return;
    }

    // Fast path: k_bytes <= 7.
    // Load B panel as 7 SEPARATE named zmm variables so compiler treats each as a register.
    // Unused vars for k_bytes < 7 are loaded conditionally (zeroed if not needed).
    for (int jc = 0; jc < m; jc += 64) {
        __m512i b0 = _mm512_loadu_si512((const __m512i*)(B + (size_t)0*m+jc));
        __m512i b1 = (k_bytes > 1) ? _mm512_loadu_si512((const __m512i*)(B + (size_t)1*m+jc)) : _mm512_setzero_si512();
        __m512i b2 = (k_bytes > 2) ? _mm512_loadu_si512((const __m512i*)(B + (size_t)2*m+jc)) : _mm512_setzero_si512();
        __m512i b3 = (k_bytes > 3) ? _mm512_loadu_si512((const __m512i*)(B + (size_t)3*m+jc)) : _mm512_setzero_si512();
        __m512i b4 = (k_bytes > 4) ? _mm512_loadu_si512((const __m512i*)(B + (size_t)4*m+jc)) : _mm512_setzero_si512();
        __m512i b5 = (k_bytes > 5) ? _mm512_loadu_si512((const __m512i*)(B + (size_t)5*m+jc)) : _mm512_setzero_si512();
        __m512i b6 = (k_bytes > 6) ? _mm512_loadu_si512((const __m512i*)(B + (size_t)6*m+jc)) : _mm512_setzero_si512();

        for (int ic = 0; ic + 4 <= n; ic += 4) {
            __m512i al0=_mm512_setzero_si512(), ah0=_mm512_setzero_si512();
            __m512i al1=_mm512_setzero_si512(), ah1=_mm512_setzero_si512();
            __m512i al2=_mm512_setzero_si512(), ah2=_mm512_setzero_si512();
            __m512i al3=_mm512_setzero_si512(), ah3=_mm512_setzero_si512();

            const uint8_t* r0 = A + (size_t)(ic+0)*k_bytes*2;
            const uint8_t* r1 = A + (size_t)(ic+1)*k_bytes*2;
            const uint8_t* r2 = A + (size_t)(ic+2)*k_bytes*2;
            const uint8_t* r3 = A + (size_t)(ic+3)*k_bytes*2;

#define ACC4(bv, t) { \
    __m512i d0=_mm512_sub_epi8(_mm512_popcnt_epi8(_mm512_ternarylogic_epi64(_mm512_set1_epi8((int8_t)r0[t*2]),_mm512_set1_epi8((int8_t)r0[t*2+1]),bv,0xD8)),_mm512_popcnt_epi8(_mm512_ternarylogic_epi64(_mm512_set1_epi8((int8_t)r0[t*2]),_mm512_set1_epi8((int8_t)r0[t*2+1]),bv,0xE4))); \
    __m512i d1=_mm512_sub_epi8(_mm512_popcnt_epi8(_mm512_ternarylogic_epi64(_mm512_set1_epi8((int8_t)r1[t*2]),_mm512_set1_epi8((int8_t)r1[t*2+1]),bv,0xD8)),_mm512_popcnt_epi8(_mm512_ternarylogic_epi64(_mm512_set1_epi8((int8_t)r1[t*2]),_mm512_set1_epi8((int8_t)r1[t*2+1]),bv,0xE4))); \
    __m512i d2=_mm512_sub_epi8(_mm512_popcnt_epi8(_mm512_ternarylogic_epi64(_mm512_set1_epi8((int8_t)r2[t*2]),_mm512_set1_epi8((int8_t)r2[t*2+1]),bv,0xD8)),_mm512_popcnt_epi8(_mm512_ternarylogic_epi64(_mm512_set1_epi8((int8_t)r2[t*2]),_mm512_set1_epi8((int8_t)r2[t*2+1]),bv,0xE4))); \
    __m512i d3=_mm512_sub_epi8(_mm512_popcnt_epi8(_mm512_ternarylogic_epi64(_mm512_set1_epi8((int8_t)r3[t*2]),_mm512_set1_epi8((int8_t)r3[t*2+1]),bv,0xD8)),_mm512_popcnt_epi8(_mm512_ternarylogic_epi64(_mm512_set1_epi8((int8_t)r3[t*2]),_mm512_set1_epi8((int8_t)r3[t*2+1]),bv,0xE4))); \
    al0=_mm512_add_epi16(al0,_mm512_cvtepi8_epi16(_mm512_castsi512_si256(d0))); ah0=_mm512_add_epi16(ah0,_mm512_cvtepi8_epi16(_mm512_extracti32x8_epi32(d0,1))); \
    al1=_mm512_add_epi16(al1,_mm512_cvtepi8_epi16(_mm512_castsi512_si256(d1))); ah1=_mm512_add_epi16(ah1,_mm512_cvtepi8_epi16(_mm512_extracti32x8_epi32(d1,1))); \
    al2=_mm512_add_epi16(al2,_mm512_cvtepi8_epi16(_mm512_castsi512_si256(d2))); ah2=_mm512_add_epi16(ah2,_mm512_cvtepi8_epi16(_mm512_extracti32x8_epi32(d2,1))); \
    al3=_mm512_add_epi16(al3,_mm512_cvtepi8_epi16(_mm512_castsi512_si256(d3))); ah3=_mm512_add_epi16(ah3,_mm512_cvtepi8_epi16(_mm512_extracti32x8_epi32(d3,1))); \
}
                         ACC4(b0,0)
            if(k_bytes>1) ACC4(b1,1)
            if(k_bytes>2) ACC4(b2,2)
            if(k_bytes>3) ACC4(b3,3)
            if(k_bytes>4) ACC4(b4,4)
            if(k_bytes>5) ACC4(b5,5)
            if(k_bytes>6) ACC4(b6,6)
#undef ACC4

#define STOREW(al,ah,r) { int* Cr=C+(size_t)(ic+(r))*m+jc; \
    _mm512_storeu_si512((__m512i*)(Cr+ 0),_mm512_cvtepi16_epi32(_mm512_castsi512_si256(al))); \
    _mm512_storeu_si512((__m512i*)(Cr+16),_mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(al,1))); \
    _mm512_storeu_si512((__m512i*)(Cr+32),_mm512_cvtepi16_epi32(_mm512_castsi512_si256(ah))); \
    _mm512_storeu_si512((__m512i*)(Cr+48),_mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(ah,1))); }
            STOREW(al0,ah0,0) STOREW(al1,ah1,1) STOREW(al2,ah2,2) STOREW(al3,ah3,3)
#undef STOREW
        }
        // Remainder rows
        for (int ic = (n/4)*4; ic < n; ic++) {
            __m512i al=_mm512_setzero_si512(), ah=_mm512_setzero_si512();
            const uint8_t* ar = A + (size_t)ic*k_bytes*2;
#define ACC1(bv,t) { \
    __m512i vp=_mm512_set1_epi8((int8_t)ar[t*2]); __m512i vn=_mm512_set1_epi8((int8_t)ar[t*2+1]); \
    __m512i d=_mm512_sub_epi8(_mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp,vn,bv,0xD8)),_mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp,vn,bv,0xE4))); \
    al=_mm512_add_epi16(al,_mm512_cvtepi8_epi16(_mm512_castsi512_si256(d))); ah=_mm512_add_epi16(ah,_mm512_cvtepi8_epi16(_mm512_extracti32x8_epi32(d,1))); }
                         ACC1(b0,0)
            if(k_bytes>1) ACC1(b1,1)
            if(k_bytes>2) ACC1(b2,2)
            if(k_bytes>3) ACC1(b3,3)
            if(k_bytes>4) ACC1(b4,4)
            if(k_bytes>5) ACC1(b5,5)
            if(k_bytes>6) ACC1(b6,6)
#undef ACC1
            int* Cr=C+(size_t)ic*m+jc;
            _mm512_storeu_si512((__m512i*)(Cr+ 0),_mm512_cvtepi16_epi32(_mm512_castsi512_si256(al)));
            _mm512_storeu_si512((__m512i*)(Cr+16),_mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(al,1)));
            _mm512_storeu_si512((__m512i*)(Cr+32),_mm512_cvtepi16_epi32(_mm512_castsi512_si256(ah)));
            _mm512_storeu_si512((__m512i*)(Cr+48),_mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(ah,1)));
        }
    }
}
"""
