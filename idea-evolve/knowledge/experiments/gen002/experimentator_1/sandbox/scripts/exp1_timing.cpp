/*
 * Experiment 1: Per-phase timing instrumentation
 * Tests: Where does time go in the best current solution (sol10)?
 * Variable: phase of execution (pack_A, pack_B, micro_kernel, store)
 * Baseline: overall time known (~148 µs geomean)
 */
#include <immintrin.h>
#include <stdint.h>
#include <string.h>
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <time.h>

// ---------- Timing helpers ----------
static inline uint64_t rdtsc_start() {
    unsigned int lo, hi;
    asm volatile("cpuid\n\t"
                 "rdtsc\n\t"
                 "mov %%edx, %0\n\t"
                 "mov %%eax, %1\n\t"
                 : "=r"(hi), "=r"(lo)
                 :: "%rax", "%rbx", "%rcx", "%rdx");
    return ((uint64_t)hi << 32) | lo;
}
static inline uint64_t rdtsc_end() {
    unsigned int lo, hi;
    asm volatile("rdtscp\n\t"
                 "mov %%edx, %0\n\t"
                 "mov %%eax, %1\n\t"
                 "cpuid\n\t"
                 : "=r"(hi), "=r"(lo)
                 :: "%rax", "%rbx", "%rcx", "%rdx");
    return ((uint64_t)hi << 32) | lo;
}

static double get_time_ns() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1e9 + ts.tv_nsec;
}

// ---------- Encoding (from encoder.cpp) ----------
static void encodeTern(int* A, uint8_t* Anew, int n, int m) {
    memset(Anew, 0, n * (m/8) * 2);
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++) {
            int ind = (i * m + j) / 8;
            int off = (i * m + j) % 8;
            Anew[2 * ind] |= (A[i * m + j] == 1) << off;
            Anew[2 * ind + 1] |= (A[i * m + j] == -1) << off;
        }
}

static void encodeBinT(int* B, uint8_t* Bnew, int n, int m) {
    memset(Bnew, 0, (n/8) * m);
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++) {
            int ind = (i / 8) * m + j;
            int off = i % 8;
            Bnew[ind] |= (B[i * m + j] == -1) << off;
        }
}

// ---------- Naive reference ----------
static void gemmV0(int* A, int* B, int* C, int n, int m, int k) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) C[i * m + j] = 0;
        for (int t = 0; t < k; t++)
            for (int j = 0; j < m; j++)
                C[i * m + j] += A[i * k + t] * B[t * m + j];
    }
}

// ---------- Encoded naive reference ----------
static void gemmV0_encoded(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    int k_bytes = k / 8;
    memset(C, 0, n * m * sizeof(int));
    for (int i = 0; i < n; i++)
        for (int t = 0; t < k_bytes; t++)
            for (int j = 0; j < m; j++) {
                uint8_t a0 = A[(i * k_bytes + t) * 2];
                uint8_t a1 = A[(i * k_bytes + t) * 2 + 1];
                uint8_t b = B[t * m + j];
                C[i * m + j] += __builtin_popcount((a0 | b) & (a1 | ~b));
                C[i * m + j] -= __builtin_popcount((a0 | ~b) & (a1 | b));
            }
}

// ---------- Best solution (sol10) with timing instrumentation ----------
#define MC 64
#define NC 256

// Timing accumulators (volatile to prevent optimization)
static volatile uint64_t t_pack_a = 0, t_pack_b = 0, t_kernel = 0, t_store_total = 0;

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

// Separate the store part to measure it
static inline void micro_kernel_compute(
    int kc, const uint8_t* __restrict__ A_p,
    const uint8_t* __restrict__ B_p,
    __m512i acc[4][2]
) {
    for (int r = 0; r < 4; ++r) acc[r][0] = acc[r][1] = _mm512_setzero_si512();

    #pragma GCC unroll 7
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
}

static inline void micro_kernel_store(
    __m512i acc[4][2],
    int* __restrict__ C, int m, int cur_mc, int cur_nc
) {
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

// Instrumented version — accumulates per-phase time
void gemmCandidate_timed(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    int k_bytes = k/8;
    alignas(64) uint8_t Ap[4096];
    alignas(64) uint8_t Bp[8192];

    uint64_t pa_total = 0, pb_total = 0, kern_total = 0, store_total = 0;

    for (int jc = 0; jc < m; jc += NC) {
        int cnc = m-jc; if (cnc>NC) cnc=NC;

        uint64_t t0 = rdtsc_start();
        pack_B(k_bytes, cnc, B+jc, m, Bp);
        uint64_t t1 = rdtsc_end();
        pb_total += t1 - t0;

        for (int ic = 0; ic < n; ic += MC) {
            int cmc = n-ic; if (cmc>MC) cmc=MC;

            t0 = rdtsc_start();
            pack_A(cmc, k_bytes, A+(ic*k_bytes)*2, k_bytes, Ap);
            t1 = rdtsc_end();
            pa_total += t1 - t0;

            for (int jr = 0; jr < cnc; jr += 64) {
                int mnc = cnc-jr; if (mnc>64) mnc=64;
                for (int ir = 0; ir < cmc; ir += 4) {
                    int mmc = cmc-ir; if (mmc>4) mmc=4;

                    __m512i acc[4][2];

                    t0 = rdtsc_start();
                    micro_kernel_compute(k_bytes, Ap+(ir/4)*k_bytes*8, Bp+(jr/64)*k_bytes*64, acc);
                    t1 = rdtsc_end();
                    kern_total += t1 - t0;

                    t0 = rdtsc_start();
                    micro_kernel_store(acc, C+(ic+ir)*m+(jc+jr), m, mmc, mnc);
                    t1 = rdtsc_end();
                    store_total += t1 - t0;
                }
            }
        }
    }

    t_pack_a = pa_total;
    t_pack_b = pb_total;
    t_kernel = kern_total;
    t_store_total = store_total;
}

// Un-instrumented version for correctness check
void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    int k_bytes = k/8;
    alignas(64) uint8_t Ap[4096];
    alignas(64) uint8_t Bp[8192];
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
                    __m512i acc[4][2];
                    micro_kernel_compute(k_bytes, Ap+(ir/4)*k_bytes*8, Bp+(jr/64)*k_bytes*64, acc);
                    micro_kernel_store(acc, C+(ic+ir)*m+(jc+jr), m, mmc, mnc);
                }
            }
        }
    }
}

// ---------- Data generation ----------
static void gen_ternary(int* A, int n, int k, unsigned seed) {
    srand(seed);
    for (int i = 0; i < n * k; i++) A[i] = (rand() % 3) - 1;
}
static void gen_binary(int* B, int k, int m, unsigned seed) {
    srand(seed);
    for (int i = 0; i < k * m; i++) B[i] = (rand() % 2) * 2 - 1;
}

struct BenchSize { int n, m, k_raw; const char* name; };

int main() {
    BenchSize sizes[] = {
        {32,  1024,   9,  "small"},
        {64,  16384,  27, "medium"},
        {128, 65536,  54, "large"},
    };

    // Get TSC frequency by measuring 100ms
    uint64_t tsc0 = rdtsc_start();
    double ns0 = get_time_ns();
    volatile int dummy = 0;
    struct timespec sl = {0, 100000000}; // 100ms
    nanosleep(&sl, nullptr);
    uint64_t tsc1 = rdtsc_end();
    double ns1 = get_time_ns();
    double tsc_freq_ghz = (tsc1 - tsc0) / (ns1 - ns0);
    printf("TSC frequency: %.3f GHz\n\n", tsc_freq_ghz);

    for (int s = 0; s < 3; s++) {
        int n = sizes[s].n;
        int m = sizes[s].m;
        int k_raw = sizes[s].k_raw;
        int k = 8 * (k_raw / 8 + 1);
        int k_bytes = k / 8;

        printf("=== %s: n=%d, m=%d, k=%d (k_bytes=%d) ===\n", sizes[s].name, n, m, k, k_bytes);

        // Allocate
        int* A_int = (int*)calloc(n * k, sizeof(int));
        int* B_int = (int*)calloc(k * m, sizeof(int));
        uint8_t* A_enc = (uint8_t*)calloc(n * k_bytes * 2, 1);
        uint8_t* B_enc = (uint8_t*)calloc(k_bytes * m, 1);
        int* C_ref = (int*)calloc(n * m, sizeof(int));
        int* C_test = (int*)calloc(n * m, sizeof(int));

        gen_ternary(A_int, n, k, 42);
        gen_binary(B_int, k, m, 123);
        encodeTern(A_int, A_enc, n, k);
        encodeBinT(B_int, B_enc, k, m);

        // Correctness check
        gemmV0_encoded(A_enc, B_enc, C_ref, n, m, k);
        gemmCandidate(A_enc, B_enc, C_test, n, m, k);

        int mismatches = 0;
        for (int i = 0; i < n * m; i++)
            if (C_ref[i] != C_test[i]) mismatches++;

        if (mismatches > 0) {
            printf("  CORRECTNESS FAIL: %d mismatches!\n\n", mismatches);
            free(A_int); free(B_int); free(A_enc); free(B_enc); free(C_ref); free(C_test);
            continue;
        }
        printf("  Correctness: PASS\n");

        // Warmup
        for (int w = 0; w < 3; w++)
            gemmCandidate_timed(A_enc, B_enc, C_test, n, m, k);

        // Timed runs
        int REPS = 10;
        double total_ns = 0;
        uint64_t pa_sum = 0, pb_sum = 0, kern_sum = 0, store_sum = 0;

        for (int r = 0; r < REPS; r++) {
            double t0 = get_time_ns();
            gemmCandidate_timed(A_enc, B_enc, C_test, n, m, k);
            double t1 = get_time_ns();
            total_ns += (t1 - t0);
            pa_sum += t_pack_a;
            pb_sum += t_pack_b;
            kern_sum += t_kernel;
            store_sum += t_store_total;
        }

        double avg_us = total_ns / REPS / 1000.0;
        double pa_us = (double)pa_sum / REPS / tsc_freq_ghz / 1000.0;
        double pb_us = (double)pb_sum / REPS / tsc_freq_ghz / 1000.0;
        double kern_us = (double)kern_sum / REPS / tsc_freq_ghz / 1000.0;
        double store_us = (double)store_sum / REPS / tsc_freq_ghz / 1000.0;
        double other_us = avg_us - pa_us - pb_us - kern_us - store_us;

        printf("  Total:      %8.2f µs\n", avg_us);
        printf("  pack_A:     %8.2f µs (%5.1f%%)\n", pa_us, pa_us/avg_us*100);
        printf("  pack_B:     %8.2f µs (%5.1f%%)\n", pb_us, pb_us/avg_us*100);
        printf("  kernel:     %8.2f µs (%5.1f%%)\n", kern_us, kern_us/avg_us*100);
        printf("  store:      %8.2f µs (%5.1f%%)\n", store_us, store_us/avg_us*100);
        printf("  other/loop: %8.2f µs (%5.1f%%)\n", other_us, other_us/avg_us*100);
        printf("\n");

        // Also report absolute counts
        int n_mc_blocks = (n + MC - 1) / MC;
        int n_nc_blocks = (m + NC - 1) / NC;
        int n_jr_blocks_per_nc = (std::min(m, NC) + 63) / 64;
        int n_ir_blocks_per_mc = (std::min(n, MC) + 3) / 4;
        int total_ukernel_calls = n_nc_blocks * n_mc_blocks * n_jr_blocks_per_nc * n_ir_blocks_per_mc;

        printf("  Block counts: NC_blocks=%d, MC_blocks=%d, jr_per_nc=%d, ir_per_mc=%d\n",
               n_nc_blocks, n_mc_blocks, n_jr_blocks_per_nc, n_ir_blocks_per_mc);
        printf("  Total micro-kernel calls: %d\n", total_ukernel_calls);
        printf("  Avg cycles per micro-kernel: %.1f\n",
               (double)kern_sum / REPS / total_ukernel_calls);
        printf("  Avg cycles per store: %.1f\n",
               (double)store_sum / REPS / total_ukernel_calls);
        printf("  Output bytes written: %d (%.2f MB)\n",
               n * m * 4, n * m * 4.0 / 1e6);
        printf("\n");

        free(A_int); free(B_int); free(A_enc); free(B_enc); free(C_ref); free(C_test);
    }

    return 0;
}
