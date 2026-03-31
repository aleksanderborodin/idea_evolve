# fitness: 160.95
"""
Mini-pack B into L1 for medium (sol08).

For medium (k_bytes=4, m=16384): BLIS-style B packing into L1 strips.
- Outer: panels of NC=256 cols. Pack B panel (4×256=1024 bytes) to stack (L1).
- Inner: 2-row micro-kernel reading B from L1 (5c latency vs 12c from L2).
This copies BLIS's key advantage (B in L1 for micro-kernel) without pack_A overhead.

For large (k_bytes>=5): B 64-col micro-pack (sol06 approach).
For small (k_bytes<=2): 2-row, regular stores.
"""

def entrypoint():
    return r"""
#include <immintrin.h>
#include <stdint.h>
#include <string.h>

void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    const int k_bytes = k / 8;
    const bool use_stream = (m >= 4096) && (((uintptr_t)C & 63) == 0);

    if (k_bytes >= 3 && k_bytes <= 4) {
        // Medium: mini-pack B into L1 panels of NC=256 columns
        const int NC = 256;
        alignas(64) uint8_t B_panel[7 * 256]; // k_bytes * NC bytes

        int j0 = 0;
        for (; j0 + NC <= m; j0 += NC) {
            // Pack B panel: k_bytes rows × NC columns into contiguous L1 buffer
            for (int t = 0; t < k_bytes; t++)
                memcpy(B_panel + t * NC, B + t * m + j0, NC);

            // Process 2 rows at a time
            int i = 0;
            for (; i + 2 <= n; i += 2) {
                const uint8_t* A0 = A + i * k_bytes * 2;
                const uint8_t* A1 = A + (i+1) * k_bytes * 2;
                int* C0 = C + i * m;
                int* C1 = C + (i+1) * m;

                // Inner j-loop within panel: 64-col chunks from L1
                for (int j = 0; j < NC; j += 64) {
                    __m512i r00=_mm512_setzero_si512(), r01=_mm512_setzero_si512();
                    __m512i r02=_mm512_setzero_si512(), r03=_mm512_setzero_si512();
                    __m512i r10=_mm512_setzero_si512(), r11=_mm512_setzero_si512();
                    __m512i r12=_mm512_setzero_si512(), r13=_mm512_setzero_si512();
                    __m512i a8_0=_mm512_setzero_si512(), a8_1=_mm512_setzero_si512();

                    #pragma GCC unroll 4
                    for (int t = 0; t < k_bytes; t++) {
                        __m512i ap0=_mm512_set1_epi8((int8_t)A0[t*2]);
                        __m512i an0=_mm512_set1_epi8((int8_t)A0[t*2+1]);
                        __m512i ap1=_mm512_set1_epi8((int8_t)A1[t*2]);
                        __m512i an1=_mm512_set1_epi8((int8_t)A1[t*2+1]);
                        // B loaded from L1 stack buffer
                        __m512i b = _mm512_load_si512((const __m512i*)(B_panel + t*NC + j));
                        a8_0=_mm512_add_epi8(a8_0,_mm512_sub_epi8(
                            _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap0,an0,b,0xD8)),
                            _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap0,an0,b,0xE4))));
                        a8_1=_mm512_add_epi8(a8_1,_mm512_sub_epi8(
                            _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap1,an1,b,0xD8)),
                            _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap1,an1,b,0xE4))));
                    }
                    // Single flush (k_bytes<=4, no overflow in int8)
                    __m128i q0=_mm512_castsi512_si128(a8_0), q1=_mm512_extracti32x4_epi32(a8_0,1);
                    __m128i q2=_mm512_extracti32x4_epi32(a8_0,2), q3=_mm512_extracti32x4_epi32(a8_0,3);
                    r00=_mm512_cvtepi8_epi32(q0); r01=_mm512_cvtepi8_epi32(q1);
                    r02=_mm512_cvtepi8_epi32(q2); r03=_mm512_cvtepi8_epi32(q3);
                    q0=_mm512_castsi512_si128(a8_1); q1=_mm512_extracti32x4_epi32(a8_1,1);
                    q2=_mm512_extracti32x4_epi32(a8_1,2); q3=_mm512_extracti32x4_epi32(a8_1,3);
                    r10=_mm512_cvtepi8_epi32(q0); r11=_mm512_cvtepi8_epi32(q1);
                    r12=_mm512_cvtepi8_epi32(q2); r13=_mm512_cvtepi8_epi32(q3);

                    if (use_stream) {
                        _mm512_stream_si512((__m512i*)(C0+j0+j+ 0),r00);
                        _mm512_stream_si512((__m512i*)(C0+j0+j+16),r01);
                        _mm512_stream_si512((__m512i*)(C0+j0+j+32),r02);
                        _mm512_stream_si512((__m512i*)(C0+j0+j+48),r03);
                        _mm512_stream_si512((__m512i*)(C1+j0+j+ 0),r10);
                        _mm512_stream_si512((__m512i*)(C1+j0+j+16),r11);
                        _mm512_stream_si512((__m512i*)(C1+j0+j+32),r12);
                        _mm512_stream_si512((__m512i*)(C1+j0+j+48),r13);
                    } else {
                        _mm512_storeu_si512((__m512i*)(C0+j0+j+ 0),r00);
                        _mm512_storeu_si512((__m512i*)(C0+j0+j+16),r01);
                        _mm512_storeu_si512((__m512i*)(C0+j0+j+32),r02);
                        _mm512_storeu_si512((__m512i*)(C0+j0+j+48),r03);
                        _mm512_storeu_si512((__m512i*)(C1+j0+j+ 0),r10);
                        _mm512_storeu_si512((__m512i*)(C1+j0+j+16),r11);
                        _mm512_storeu_si512((__m512i*)(C1+j0+j+32),r12);
                        _mm512_storeu_si512((__m512i*)(C1+j0+j+48),r13);
                    }
                }
            }
            // Odd last row in panel
            for (; i < n; i++) {
                const uint8_t* Ar = A + i*k_bytes*2;
                int* Cr = C + i*m;
                for (int j = 0; j < NC; j += 64) {
                    __m512i a8=_mm512_setzero_si512();
                    #pragma GCC unroll 4
                    for (int t = 0; t < k_bytes; t++) {
                        __m512i ap=_mm512_set1_epi8((int8_t)Ar[t*2]), an=_mm512_set1_epi8((int8_t)Ar[t*2+1]);
                        __m512i b=_mm512_load_si512((const __m512i*)(B_panel+t*NC+j));
                        a8=_mm512_add_epi8(a8,_mm512_sub_epi8(
                            _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap,an,b,0xD8)),
                            _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap,an,b,0xE4))));
                    }
                    __m128i q0=_mm512_castsi512_si128(a8),q1=_mm512_extracti32x4_epi32(a8,1);
                    __m128i q2=_mm512_extracti32x4_epi32(a8,2),q3=_mm512_extracti32x4_epi32(a8,3);
                    if (use_stream) {
                        _mm512_stream_si512((__m512i*)(Cr+j0+j+ 0),_mm512_cvtepi8_epi32(q0));
                        _mm512_stream_si512((__m512i*)(Cr+j0+j+16),_mm512_cvtepi8_epi32(q1));
                        _mm512_stream_si512((__m512i*)(Cr+j0+j+32),_mm512_cvtepi8_epi32(q2));
                        _mm512_stream_si512((__m512i*)(Cr+j0+j+48),_mm512_cvtepi8_epi32(q3));
                    } else {
                        _mm512_storeu_si512((__m512i*)(Cr+j0+j+ 0),_mm512_cvtepi8_epi32(q0));
                        _mm512_storeu_si512((__m512i*)(Cr+j0+j+16),_mm512_cvtepi8_epi32(q1));
                        _mm512_storeu_si512((__m512i*)(Cr+j0+j+32),_mm512_cvtepi8_epi32(q2));
                        _mm512_storeu_si512((__m512i*)(Cr+j0+j+48),_mm512_cvtepi8_epi32(q3));
                    }
                }
            }
        }
        // Handle tail (m not multiple of NC)
        for (int j = j0; j + 64 <= m; j += 64) {
            for (int t=0;t<k_bytes;t++) memcpy(B_panel+t*64, B+t*m+j, 64);
            for (int i=0;i<n;i++) {
                const uint8_t* Ar=A+i*k_bytes*2; int* Cr=C+i*m;
                __m512i a8=_mm512_setzero_si512(),r0=_mm512_setzero_si512(),r1=_mm512_setzero_si512(),r2=_mm512_setzero_si512(),r3=_mm512_setzero_si512();
                for (int t=0;t<k_bytes;t++) {
                    __m512i ap=_mm512_set1_epi8((int8_t)Ar[t*2]),an=_mm512_set1_epi8((int8_t)Ar[t*2+1]);
                    __m512i b=_mm512_load_si512((const __m512i*)(B_panel+t*64));
                    a8=_mm512_add_epi8(a8,_mm512_sub_epi8(
                        _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap,an,b,0xD8)),
                        _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap,an,b,0xE4))));
                    if (t==k_bytes-1) {
                        __m128i q0=_mm512_castsi512_si128(a8),q1=_mm512_extracti32x4_epi32(a8,1),q2=_mm512_extracti32x4_epi32(a8,2),q3=_mm512_extracti32x4_epi32(a8,3);
                        r0=_mm512_cvtepi8_epi32(q0); r1=_mm512_cvtepi8_epi32(q1); r2=_mm512_cvtepi8_epi32(q2); r3=_mm512_cvtepi8_epi32(q3);
                    }
                }
                _mm512_storeu_si512((__m512i*)(Cr+j+0),r0); _mm512_storeu_si512((__m512i*)(Cr+j+16),r1);
                _mm512_storeu_si512((__m512i*)(Cr+j+32),r2); _mm512_storeu_si512((__m512i*)(Cr+j+48),r3);
            }
        }

    } else if (k_bytes >= 5) {
        // Large: 64-col B micro-pack (sol06 approach)
        alignas(64) uint8_t B_local[32 * 64];
        int j = 0;
        for (; j + 64 <= m; j += 64) {
            for (int t = 0; t < k_bytes; t++) memcpy(B_local + t*64, B + t*m + j, 64);
            for (int i = 0; i < n; i++) {
                const uint8_t* Ar=A+i*k_bytes*2; int* Cr=C+i*m;
                __m512i acc8=_mm512_setzero_si512(), r0=_mm512_setzero_si512(), r1=_mm512_setzero_si512(), r2=_mm512_setzero_si512(), r3=_mm512_setzero_si512();
                for (int t=0;t<k_bytes;t++) {
                    __m512i ap=_mm512_set1_epi8((int8_t)Ar[t*2]), an=_mm512_set1_epi8((int8_t)Ar[t*2+1]);
                    __m512i b=_mm512_load_si512((const __m512i*)(B_local+t*64));
                    acc8=_mm512_add_epi8(acc8,_mm512_sub_epi8(
                        _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap,an,b,0xD8)),
                        _mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap,an,b,0xE4))));
                    if ((t&15)==14||t==k_bytes-1) {
                        __m128i q0=_mm512_castsi512_si128(acc8),q1=_mm512_extracti32x4_epi32(acc8,1),q2=_mm512_extracti32x4_epi32(acc8,2),q3=_mm512_extracti32x4_epi32(acc8,3);
                        r0=_mm512_add_epi32(r0,_mm512_cvtepi8_epi32(q0)); r1=_mm512_add_epi32(r1,_mm512_cvtepi8_epi32(q1));
                        r2=_mm512_add_epi32(r2,_mm512_cvtepi8_epi32(q2)); r3=_mm512_add_epi32(r3,_mm512_cvtepi8_epi32(q3));
                        acc8=_mm512_setzero_si512();
                    }
                }
                if (use_stream) {
                    _mm512_stream_si512((__m512i*)(Cr+j+0),r0); _mm512_stream_si512((__m512i*)(Cr+j+16),r1);
                    _mm512_stream_si512((__m512i*)(Cr+j+32),r2); _mm512_stream_si512((__m512i*)(Cr+j+48),r3);
                } else {
                    _mm512_storeu_si512((__m512i*)(Cr+j+0),r0); _mm512_storeu_si512((__m512i*)(Cr+j+16),r1);
                    _mm512_storeu_si512((__m512i*)(Cr+j+32),r2); _mm512_storeu_si512((__m512i*)(Cr+j+48),r3);
                }
            }
        }
        for (int i=0;i<n;i++) for (int jj=j;jj<m;jj++) {
            int sum=0;
            for (int t=0;t<k_bytes;t++) {
                uint8_t ap=A[(i*k_bytes+t)*2],an=A[(i*k_bytes+t)*2+1],bv=B[t*m+jj];
                sum+=__builtin_popcount((ap|bv)&(uint8_t)(an|(uint8_t)~bv));
                sum-=__builtin_popcount((uint8_t)(ap|(uint8_t)~bv)&(an|bv));
            }
            C[i*m+jj]=sum;
        }
    } else {
        // Small (k_bytes<=2): 2-row
        int i=0;
        for (; i+2<=n; i+=2) {
            const uint8_t* A0=A+i*k_bytes*2, *A1=A+(i+1)*k_bytes*2;
            int* C0=C+i*m, *C1=C+(i+1)*m;
            for (int j=0; j+64<=m; j+=64) {
                __m512i r00=_mm512_setzero_si512(),r01=_mm512_setzero_si512(),r02=_mm512_setzero_si512(),r03=_mm512_setzero_si512();
                __m512i r10=_mm512_setzero_si512(),r11=_mm512_setzero_si512(),r12=_mm512_setzero_si512(),r13=_mm512_setzero_si512();
                __m512i a0=_mm512_setzero_si512(), a1=_mm512_setzero_si512();
                for (int t=0;t<k_bytes;t++) {
                    __m512i ap0=_mm512_set1_epi8((int8_t)A0[t*2]),an0=_mm512_set1_epi8((int8_t)A0[t*2+1]);
                    __m512i ap1=_mm512_set1_epi8((int8_t)A1[t*2]),an1=_mm512_set1_epi8((int8_t)A1[t*2+1]);
                    __m512i b=_mm512_loadu_si512((const __m512i*)(B+t*m+j));
                    a0=_mm512_add_epi8(a0,_mm512_sub_epi8(_mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap0,an0,b,0xD8)),_mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap0,an0,b,0xE4))));
                    a1=_mm512_add_epi8(a1,_mm512_sub_epi8(_mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap1,an1,b,0xD8)),_mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap1,an1,b,0xE4))));
                    if ((t&15)==14||t==k_bytes-1) {
                        __m128i q0,q1,q2,q3;
                        q0=_mm512_castsi512_si128(a0); q1=_mm512_extracti32x4_epi32(a0,1); q2=_mm512_extracti32x4_epi32(a0,2); q3=_mm512_extracti32x4_epi32(a0,3);
                        r00=_mm512_add_epi32(r00,_mm512_cvtepi8_epi32(q0)); r01=_mm512_add_epi32(r01,_mm512_cvtepi8_epi32(q1));
                        r02=_mm512_add_epi32(r02,_mm512_cvtepi8_epi32(q2)); r03=_mm512_add_epi32(r03,_mm512_cvtepi8_epi32(q3));
                        a0=_mm512_setzero_si512();
                        q0=_mm512_castsi512_si128(a1); q1=_mm512_extracti32x4_epi32(a1,1); q2=_mm512_extracti32x4_epi32(a1,2); q3=_mm512_extracti32x4_epi32(a1,3);
                        r10=_mm512_add_epi32(r10,_mm512_cvtepi8_epi32(q0)); r11=_mm512_add_epi32(r11,_mm512_cvtepi8_epi32(q1));
                        r12=_mm512_add_epi32(r12,_mm512_cvtepi8_epi32(q2)); r13=_mm512_add_epi32(r13,_mm512_cvtepi8_epi32(q3));
                        a1=_mm512_setzero_si512();
                    }
                }
                _mm512_storeu_si512((__m512i*)(C0+j+0),r00); _mm512_storeu_si512((__m512i*)(C0+j+16),r01);
                _mm512_storeu_si512((__m512i*)(C0+j+32),r02); _mm512_storeu_si512((__m512i*)(C0+j+48),r03);
                _mm512_storeu_si512((__m512i*)(C1+j+0),r10); _mm512_storeu_si512((__m512i*)(C1+j+16),r11);
                _mm512_storeu_si512((__m512i*)(C1+j+32),r12); _mm512_storeu_si512((__m512i*)(C1+j+48),r13);
            }
            for (int j=m-(m%64); j<m; j++) {
                int s0=0,s1=0;
                for (int t=0;t<k_bytes;t++) { uint8_t ap0=A0[t*2],an0=A0[t*2+1],ap1=A1[t*2],an1=A1[t*2+1],bv=B[t*m+j];
                    s0+=__builtin_popcount((ap0|bv)&(uint8_t)(an0|(uint8_t)~bv)); s0-=__builtin_popcount((uint8_t)(ap0|(uint8_t)~bv)&(an0|bv));
                    s1+=__builtin_popcount((ap1|bv)&(uint8_t)(an1|(uint8_t)~bv)); s1-=__builtin_popcount((uint8_t)(ap1|(uint8_t)~bv)&(an1|bv)); }
                C0[j]=s0; C1[j]=s1;
            }
        }
        for (;i<n;i++) { const uint8_t* Ar=A+i*k_bytes*2; int* Cr=C+i*m;
            for (int j=0;j+64<=m;j+=64) {
                __m512i acc8=_mm512_setzero_si512(),r0=_mm512_setzero_si512(),r1=_mm512_setzero_si512(),r2=_mm512_setzero_si512(),r3=_mm512_setzero_si512();
                for (int t=0;t<k_bytes;t++) { __m512i ap=_mm512_set1_epi8((int8_t)Ar[t*2]),an=_mm512_set1_epi8((int8_t)Ar[t*2+1]),b=_mm512_loadu_si512((const __m512i*)(B+t*m+j));
                    acc8=_mm512_add_epi8(acc8,_mm512_sub_epi8(_mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap,an,b,0xD8)),_mm512_popcnt_epi8(_mm512_ternarylogic_epi32(ap,an,b,0xE4))));
                    if ((t&15)==14||t==k_bytes-1) { __m128i q0=_mm512_castsi512_si128(acc8),q1=_mm512_extracti32x4_epi32(acc8,1),q2=_mm512_extracti32x4_epi32(acc8,2),q3=_mm512_extracti32x4_epi32(acc8,3);
                        r0=_mm512_add_epi32(r0,_mm512_cvtepi8_epi32(q0)); r1=_mm512_add_epi32(r1,_mm512_cvtepi8_epi32(q1)); r2=_mm512_add_epi32(r2,_mm512_cvtepi8_epi32(q2)); r3=_mm512_add_epi32(r3,_mm512_cvtepi8_epi32(q3)); acc8=_mm512_setzero_si512(); } }
                _mm512_storeu_si512((__m512i*)(Cr+j+0),r0); _mm512_storeu_si512((__m512i*)(Cr+j+16),r1); _mm512_storeu_si512((__m512i*)(Cr+j+32),r2); _mm512_storeu_si512((__m512i*)(Cr+j+48),r3);
            }
            for (int j=m-(m%64);j<m;j++) { int sum=0; for (int t=0;t<k_bytes;t++) { uint8_t ap=Ar[t*2],an=Ar[t*2+1],bv=B[t*m+j]; sum+=__builtin_popcount((ap|bv)&(uint8_t)(an|(uint8_t)~bv)); sum-=__builtin_popcount((uint8_t)(ap|(uint8_t)~bv)&(an|bv)); } Cr[j]=sum; }
        }
    }
    if (use_stream) _mm_sfence();
}
"""
