# fitness: 182.31

"""
ic-outer, jc-inner with streaming NT stores (64-byte alignment checked at runtime).

Sequential C write pattern: write C[row0, 0..m], C[row1, 0..m], ...
This enables streaming stores that bypass cache and avoid write-allocate penalty.
For large C (32MB): write-allocate doubles DRAM traffic; streaming halves it.

Alignment check: streaming stores need 64-byte aligned C. If not aligned, falls
back to regular stores (still benefits from sequential write pattern).
"""


def entrypoint() -> str:
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>
#include <algorithm>

static void gemm_fallback(const uint8_t* A, const uint8_t* B, int* C,
                          int n, int m, int k_bytes) {
    for (int ic = 0; ic < n; ic++) {
        for (int jc = 0; jc < m; jc += 64) {
            __m512i al=_mm512_setzero_si512(), ah=_mm512_setzero_si512();
            const uint8_t* ar = A + (size_t)ic*k_bytes*2;
            for (int t = 0; t < k_bytes; t++) {
                __m512i vb = _mm512_loadu_si512((const __m512i*)(B+(size_t)t*m+jc));
                __m512i vp=_mm512_set1_epi8((int8_t)ar[t*2]);
                __m512i vn=_mm512_set1_epi8((int8_t)ar[t*2+1]);
                __m512i d=_mm512_sub_epi8(
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp,vn,vb,0xD8)),
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp,vn,vb,0xE4)));
                al=_mm512_add_epi16(al,_mm512_cvtepi8_epi16(_mm512_castsi512_si256(d)));
                ah=_mm512_add_epi16(ah,_mm512_cvtepi8_epi16(_mm512_extracti32x8_epi32(d,1)));
            }
            int* Cr=C+(size_t)ic*m+jc;
            _mm512_storeu_si512((__m512i*)(Cr+ 0),_mm512_cvtepi16_epi32(_mm512_castsi512_si256(al)));
            _mm512_storeu_si512((__m512i*)(Cr+16),_mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(al,1)));
            _mm512_storeu_si512((__m512i*)(Cr+32),_mm512_cvtepi16_epi32(_mm512_castsi512_si256(ah)));
            _mm512_storeu_si512((__m512i*)(Cr+48),_mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(ah,1)));
        }
    }
}

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    int k_bytes = k/8;
    if (k_bytes > 7) { gemm_fallback(A,B,C,n,m,k_bytes); return; }

    // Check C alignment for streaming stores (64-byte required).
    // Also need row stride m*4 to be 64-byte aligned (m must be multiple of 16).
    bool can_stream = ((((uintptr_t)C) & 63) == 0) && ((m & 15) == 0);
    bool use_large_path = ((size_t)n*m*4 > 8*1024*1024UL) && can_stream;

    // ic-outer, jc-inner: sequential writes along C rows.
    for (int ic = 0; ic + 4 <= n; ic += 4) {
        const uint8_t* r0=A+(size_t)(ic+0)*k_bytes*2;
        const uint8_t* r1=A+(size_t)(ic+1)*k_bytes*2;
        const uint8_t* r2=A+(size_t)(ic+2)*k_bytes*2;
        const uint8_t* r3=A+(size_t)(ic+3)*k_bytes*2;

        for (int jc = 0; jc < m; jc += 64) {
            __m512i al0=_mm512_setzero_si512(), ah0=_mm512_setzero_si512();
            __m512i al1=_mm512_setzero_si512(), ah1=_mm512_setzero_si512();
            __m512i al2=_mm512_setzero_si512(), ah2=_mm512_setzero_si512();
            __m512i al3=_mm512_setzero_si512(), ah3=_mm512_setzero_si512();

            #pragma GCC unroll 8
            for (int t = 0; t < k_bytes; t++) {
                __m512i vb=_mm512_loadu_si512((const __m512i*)(B+(size_t)t*m+jc));
#define R(al,ah,rp) { \
    __m512i vp=_mm512_set1_epi8((int8_t)(rp)[t*2]); \
    __m512i vn=_mm512_set1_epi8((int8_t)(rp)[t*2+1]); \
    __m512i d=_mm512_sub_epi8( \
        _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp,vn,vb,0xD8)), \
        _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp,vn,vb,0xE4))); \
    al=_mm512_add_epi16(al,_mm512_cvtepi8_epi16(_mm512_castsi512_si256(d))); \
    ah=_mm512_add_epi16(ah,_mm512_cvtepi8_epi16(_mm512_extracti32x8_epi32(d,1))); \
}
                R(al0,ah0,r0) R(al1,ah1,r1) R(al2,ah2,r2) R(al3,ah3,r3)
#undef R
            }

            // Widen int16->int32
            __m512i v00=_mm512_cvtepi16_epi32(_mm512_castsi512_si256(al0));
            __m512i v01=_mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(al0,1));
            __m512i v02=_mm512_cvtepi16_epi32(_mm512_castsi512_si256(ah0));
            __m512i v03=_mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(ah0,1));
            __m512i v10=_mm512_cvtepi16_epi32(_mm512_castsi512_si256(al1));
            __m512i v11=_mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(al1,1));
            __m512i v12=_mm512_cvtepi16_epi32(_mm512_castsi512_si256(ah1));
            __m512i v13=_mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(ah1,1));
            __m512i v20=_mm512_cvtepi16_epi32(_mm512_castsi512_si256(al2));
            __m512i v21=_mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(al2,1));
            __m512i v22=_mm512_cvtepi16_epi32(_mm512_castsi512_si256(ah2));
            __m512i v23=_mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(ah2,1));
            __m512i v30=_mm512_cvtepi16_epi32(_mm512_castsi512_si256(al3));
            __m512i v31=_mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(al3,1));
            __m512i v32=_mm512_cvtepi16_epi32(_mm512_castsi512_si256(ah3));
            __m512i v33=_mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(ah3,1));

            int* C0=C+(size_t)(ic+0)*m+jc;
            int* C1=C+(size_t)(ic+1)*m+jc;
            int* C2=C+(size_t)(ic+2)*m+jc;
            int* C3=C+(size_t)(ic+3)*m+jc;

            if (use_large_path) {
                _mm512_stream_si512((__m512i*)(C0+ 0),v00); _mm512_stream_si512((__m512i*)(C0+16),v01);
                _mm512_stream_si512((__m512i*)(C0+32),v02); _mm512_stream_si512((__m512i*)(C0+48),v03);
                _mm512_stream_si512((__m512i*)(C1+ 0),v10); _mm512_stream_si512((__m512i*)(C1+16),v11);
                _mm512_stream_si512((__m512i*)(C1+32),v12); _mm512_stream_si512((__m512i*)(C1+48),v13);
                _mm512_stream_si512((__m512i*)(C2+ 0),v20); _mm512_stream_si512((__m512i*)(C2+16),v21);
                _mm512_stream_si512((__m512i*)(C2+32),v22); _mm512_stream_si512((__m512i*)(C2+48),v23);
                _mm512_stream_si512((__m512i*)(C3+ 0),v30); _mm512_stream_si512((__m512i*)(C3+16),v31);
                _mm512_stream_si512((__m512i*)(C3+32),v32); _mm512_stream_si512((__m512i*)(C3+48),v33);
            } else {
                _mm512_storeu_si512((__m512i*)(C0+ 0),v00); _mm512_storeu_si512((__m512i*)(C0+16),v01);
                _mm512_storeu_si512((__m512i*)(C0+32),v02); _mm512_storeu_si512((__m512i*)(C0+48),v03);
                _mm512_storeu_si512((__m512i*)(C1+ 0),v10); _mm512_storeu_si512((__m512i*)(C1+16),v11);
                _mm512_storeu_si512((__m512i*)(C1+32),v12); _mm512_storeu_si512((__m512i*)(C1+48),v13);
                _mm512_storeu_si512((__m512i*)(C2+ 0),v20); _mm512_storeu_si512((__m512i*)(C2+16),v21);
                _mm512_storeu_si512((__m512i*)(C2+32),v22); _mm512_storeu_si512((__m512i*)(C2+48),v23);
                _mm512_storeu_si512((__m512i*)(C3+ 0),v30); _mm512_storeu_si512((__m512i*)(C3+16),v31);
                _mm512_storeu_si512((__m512i*)(C3+32),v32); _mm512_storeu_si512((__m512i*)(C3+48),v33);
            }
        }
    }
    // Remainder rows
    for (int ic=(n/4)*4; ic<n; ic++) {
        const uint8_t* ar=A+(size_t)ic*k_bytes*2;
        for (int jc=0; jc<m; jc+=64) {
            __m512i al=_mm512_setzero_si512(), ah=_mm512_setzero_si512();
            #pragma GCC unroll 8
            for (int t=0; t<k_bytes; t++) {
                __m512i vb=_mm512_loadu_si512((const __m512i*)(B+(size_t)t*m+jc));
                __m512i vp=_mm512_set1_epi8((int8_t)ar[t*2]);
                __m512i vn=_mm512_set1_epi8((int8_t)ar[t*2+1]);
                __m512i d=_mm512_sub_epi8(
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp,vn,vb,0xD8)),
                    _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp,vn,vb,0xE4)));
                al=_mm512_add_epi16(al,_mm512_cvtepi8_epi16(_mm512_castsi512_si256(d)));
                ah=_mm512_add_epi16(ah,_mm512_cvtepi8_epi16(_mm512_extracti32x8_epi32(d,1)));
            }
            int* Cr=C+(size_t)ic*m+jc;
            _mm512_storeu_si512((__m512i*)(Cr+ 0),_mm512_cvtepi16_epi32(_mm512_castsi512_si256(al)));
            _mm512_storeu_si512((__m512i*)(Cr+16),_mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(al,1)));
            _mm512_storeu_si512((__m512i*)(Cr+32),_mm512_cvtepi16_epi32(_mm512_castsi512_si256(ah)));
            _mm512_storeu_si512((__m512i*)(Cr+48),_mm512_cvtepi16_epi32(_mm512_extracti32x8_epi32(ah,1)));
        }
    }
    if (use_large_path) _mm_sfence();
}
"""
