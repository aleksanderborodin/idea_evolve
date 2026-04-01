/*
 * Instruction throughput microbenchmark for Tiger Lake port assignment verification.
 *
 * Testing: Are the port assignments in fact_004 correct?
 * Specifically: is vpopcntb on port 5, or port 0/1 as gen002 asm analysis suggests?
 *
 * Method:
 * - Run 8 INDEPENDENT instances of each instruction (prevents latency chaining)
 * - Repeat M = 1,000,000 iterations
 * - Measure wall-clock time via clock_gettime(CLOCK_MONOTONIC)
 * - Throughput = total_ns / (8 * M) ns/instruction = cycles/instruction * (ns/cycle)
 * - At 2.4 GHz base: 1 cycle = ~0.417 ns; at 4.0 GHz turbo: 1 cycle = 0.25 ns
 *
 * If single-port: throughput = 1 cycle
 * If dual-port (0/5): throughput = 0.5 cycle
 * If dual-port (2/3): load ports, ~0.5 cycle
 *
 * Compile:
 *   g++ -O3 -std=c++17 -march=native -mavx512f -mavx512bw -mavx512vl \
 *       -mavx512vpopcntdq -mavx512bitalg -mavx512vnni \
 *       -o port_bench port_bench.cpp
 *
 * Run:
 *   ./port_bench
 */

#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>
#include <time.h>

static inline long long now_ns() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

// Return throughput: ns per instruction (averaged over 8 independent instances)
// instructions_per_iter = how many instructions are in one iteration (8 by default)
static double measure_throughput(void (*bench_fn)(int), int M) {
    // Warmup
    bench_fn(1000);

    long long t0 = now_ns();
    bench_fn(M);
    long long t1 = now_ns();

    double total_ns = (double)(t1 - t0);
    double ns_per_instr = total_ns / (8.0 * M);
    return ns_per_instr;
}

// ============================================================
// vpopcntb zmm, zmm — per-byte popcount
// fact_004 says: port 5
// gen002 asm analysis says: port 0/1
// ============================================================
static void bench_vpopcntb(int M) {
    __m512i v0 = _mm512_set1_epi8(0x55);
    __m512i v1 = _mm512_set1_epi8(0xAA);
    __m512i v2 = _mm512_set1_epi8(0x0F);
    __m512i v3 = _mm512_set1_epi8(0xF0);
    __m512i v4 = _mm512_set1_epi8(0x33);
    __m512i v5 = _mm512_set1_epi8(0xCC);
    __m512i v6 = _mm512_set1_epi8(0x01);
    __m512i v7 = _mm512_set1_epi8(0xFE);

    for (int i = 0; i < M; i++) {
        // 8 independent vpopcntb instructions
        v0 = _mm512_popcnt_epi8(v0);
        v1 = _mm512_popcnt_epi8(v1);
        v2 = _mm512_popcnt_epi8(v2);
        v3 = _mm512_popcnt_epi8(v3);
        v4 = _mm512_popcnt_epi8(v4);
        v5 = _mm512_popcnt_epi8(v5);
        v6 = _mm512_popcnt_epi8(v6);
        v7 = _mm512_popcnt_epi8(v7);
    }
    // Prevent dead code elimination
    volatile __m512i sink = _mm512_add_epi8(v0, _mm512_add_epi8(v1, v2));
    (void)sink;
}

// ============================================================
// vpternlogq zmm, zmm, zmm, imm8 — ternary logic
// fact_004 says: port 0/5, 0.5c throughput
// gen002 asm analysis agrees
// ============================================================
static void bench_vpternlogq(int M) {
    __m512i v0 = _mm512_set1_epi64(0xAAAAAAAAAAAAAAAALL);
    __m512i v1 = _mm512_set1_epi64(0x5555555555555555LL);
    __m512i a = _mm512_set1_epi64(0x0F0F0F0F0F0F0F0FLL);
    __m512i b = _mm512_set1_epi64(0xF0F0F0F0F0F0F0F0LL);
    __m512i c = _mm512_set1_epi64(0x3333333333333333LL);
    __m512i d = _mm512_set1_epi64(0xCCCCCCCCCCCCCCCCLL);
    __m512i e = _mm512_set1_epi64(0x1234567890ABCDEFLL);
    __m512i f = _mm512_set1_epi64(0xFEDCBA9876543210LL);

    for (int i = 0; i < M; i++) {
        // 8 independent vpternlogq — using 0xD8 (same as in kernel: (a|b)&(c|~b))
        // All independent (reading from constants, writing to v0/v1/a/b/c/d/e/f)
        v0 = _mm512_ternarylogic_epi64(v0, a, b, 0xD8);
        v1 = _mm512_ternarylogic_epi64(v1, c, d, 0xD8);
        a  = _mm512_ternarylogic_epi64(a,  e, f, 0xE4);
        b  = _mm512_ternarylogic_epi64(b,  v0, v1, 0xD8);
        c  = _mm512_ternarylogic_epi64(c,  a, b, 0xE4);
        d  = _mm512_ternarylogic_epi64(d,  c, e, 0xD8);
        e  = _mm512_ternarylogic_epi64(e,  d, f, 0xE4);
        f  = _mm512_ternarylogic_epi64(f,  v0, a, 0xD8);
    }
    volatile __m512i sink = _mm512_add_epi8(v0, v1);
    (void)sink;
}

// ============================================================
// vpbroadcastb zmm, r8 — broadcast byte to all 64 positions
// fact_004 says: port 5 only
// Expected throughput: 1 cycle (single port)
// ============================================================
static void bench_vpbroadcastb(int M) {
    volatile uint8_t vals[8] = {0x55, 0xAA, 0x0F, 0xF0, 0x33, 0xCC, 0x01, 0xFE};
    __m512i v0, v1, v2, v3, v4, v5, v6, v7;

    for (int i = 0; i < M; i++) {
        // 8 independent vpbroadcastb from registers
        v0 = _mm512_set1_epi8((int8_t)vals[0]);
        v1 = _mm512_set1_epi8((int8_t)vals[1]);
        v2 = _mm512_set1_epi8((int8_t)vals[2]);
        v3 = _mm512_set1_epi8((int8_t)vals[3]);
        v4 = _mm512_set1_epi8((int8_t)vals[4]);
        v5 = _mm512_set1_epi8((int8_t)vals[5]);
        v6 = _mm512_set1_epi8((int8_t)vals[6]);
        v7 = _mm512_set1_epi8((int8_t)vals[7]);
    }
    volatile __m512i sink = _mm512_add_epi8(v0, v1);
    (void)sink;
}

// ============================================================
// vpmovsxbw zmm, ymm / _mm512_cvtepi8_epi16 — sign-extend 8->16 bit
// fact_004: port 5, 1c throughput
// gen002 asm analysis: port 5 only, 1c
// ============================================================
static void bench_vpmovsxbw(int M) {
    __m256i v0 = _mm256_set1_epi8(0x55);
    __m256i v1 = _mm256_set1_epi8(0xAA);
    __m256i v2 = _mm256_set1_epi8(0x0F);
    __m256i v3 = _mm256_set1_epi8(0xF0);
    __m512i r0, r1, r2, r3, r4, r5, r6, r7;
    // Only 4 distinct inputs, run 8 ops by mixing

    for (int i = 0; i < M; i++) {
        r0 = _mm512_cvtepi8_epi16(v0);
        r1 = _mm512_cvtepi8_epi16(v1);
        r2 = _mm512_cvtepi8_epi16(v2);
        r3 = _mm512_cvtepi8_epi16(v3);
        r4 = _mm512_cvtepi8_epi16(v0);
        r5 = _mm512_cvtepi8_epi16(v1);
        r6 = _mm512_cvtepi8_epi16(v2);
        r7 = _mm512_cvtepi8_epi16(v3);
    }
    volatile __m512i sink = _mm512_add_epi8(r0, r1);
    (void)sink;
}

// ============================================================
// vpsubb zmm, zmm, zmm — byte subtraction
// fact_004: port 0/5, 0.5c throughput
// ============================================================
static void bench_vpsubb(int M) {
    __m512i v0 = _mm512_set1_epi8(0x55);
    __m512i v1 = _mm512_set1_epi8(0xAA);
    __m512i v2 = _mm512_set1_epi8(0x0F);
    __m512i v3 = _mm512_set1_epi8(0xF0);
    __m512i v4 = _mm512_set1_epi8(0x33);
    __m512i v5 = _mm512_set1_epi8(0xCC);
    __m512i v6 = _mm512_set1_epi8(0x01);
    __m512i v7 = _mm512_set1_epi8(0xFE);

    for (int i = 0; i < M; i++) {
        v0 = _mm512_sub_epi8(v0, v1);
        v1 = _mm512_sub_epi8(v1, v2);
        v2 = _mm512_sub_epi8(v2, v3);
        v3 = _mm512_sub_epi8(v3, v4);
        v4 = _mm512_sub_epi8(v4, v5);
        v5 = _mm512_sub_epi8(v5, v6);
        v6 = _mm512_sub_epi8(v6, v7);
        v7 = _mm512_sub_epi8(v7, v0);
    }
    volatile __m512i sink = _mm512_add_epi8(v0, v1);
    (void)sink;
}

// ============================================================
// cvtepi8_epi32 zmm, xmm — sign-extend 8->32 bit (4 inputs → 16 outputs)
// Used in widening after k-loop in the kernel
// Expected: port 5, 1c
// ============================================================
static void bench_cvtepi8_epi32(int M) {
    __m128i v0 = _mm_set1_epi8(0x55);
    __m128i v1 = _mm_set1_epi8(0xAA);
    __m128i v2 = _mm_set1_epi8(0x0F);
    __m128i v3 = _mm_set1_epi8(0xF0);
    __m512i r0, r1, r2, r3, r4, r5, r6, r7;

    for (int i = 0; i < M; i++) {
        r0 = _mm512_cvtepi8_epi32(v0);
        r1 = _mm512_cvtepi8_epi32(v1);
        r2 = _mm512_cvtepi8_epi32(v2);
        r3 = _mm512_cvtepi8_epi32(v3);
        r4 = _mm512_cvtepi8_epi32(v0);
        r5 = _mm512_cvtepi8_epi32(v1);
        r6 = _mm512_cvtepi8_epi32(v2);
        r7 = _mm512_cvtepi8_epi32(v3);
    }
    volatile __m512i sink = _mm512_add_epi8(r0, r1);
    (void)sink;
}

// ============================================================
// Mixed: popcntb + vpsubb in pair (as in kernel hot path)
// This measures actual throughput WITH port contention
// ============================================================
static void bench_popcnt_sub_pair(int M) {
    __m512i a0 = _mm512_set1_epi8(0x55);
    __m512i a1 = _mm512_set1_epi8(0xAA);
    __m512i a2 = _mm512_set1_epi8(0x0F);
    __m512i a3 = _mm512_set1_epi8(0xF0);
    __m512i d0 = _mm512_setzero_si512();
    __m512i d1 = _mm512_setzero_si512();
    __m512i d2 = _mm512_setzero_si512();
    __m512i d3 = _mm512_setzero_si512();

    for (int i = 0; i < M; i++) {
        // Kernel pattern: diff = popcnt(pos) - popcnt(neg)
        // Using 4 pairs (representing 4 iterations of k-loop or 2 rows)
        d0 = _mm512_sub_epi8(_mm512_popcnt_epi8(a0), _mm512_popcnt_epi8(a1));
        d1 = _mm512_sub_epi8(_mm512_popcnt_epi8(a1), _mm512_popcnt_epi8(a2));
        d2 = _mm512_sub_epi8(_mm512_popcnt_epi8(a2), _mm512_popcnt_epi8(a3));
        d3 = _mm512_sub_epi8(_mm512_popcnt_epi8(a3), _mm512_popcnt_epi8(a0));
    }
    // This counts 8 instructions per iteration (4 popcnt + 4 subb)
    volatile __m512i sink = _mm512_add_epi8(d0, d1);
    (void)sink;
}

int main() {
    const int M = 2000000;

    // At 2.4 GHz: 1 ns = 2.4 cycles → throughput in cycles = ns * 2.4
    // At 4.0 GHz: 1 ns = 4.0 cycles
    // We'll report ns/instr; user can convert knowing CPU freq
    // Also read /proc/cpuinfo for current freq if possible

    // Detect approximate CPU frequency using rdtsc + clock
    {
        long long t0_ns = now_ns();
        unsigned int dummy;
        uint64_t c0 = __rdtsc();
        // Busy spin for ~100ms
        while ((now_ns() - t0_ns) < 100000000LL) {
            __asm__ volatile("" ::: "memory");
        }
        uint64_t c1 = __rdtsc();
        long long t1_ns = now_ns();
        double elapsed_ms = (t1_ns - t0_ns) / 1e6;
        double ghz = (c1 - c0) / (elapsed_ms * 1e6);
        printf("Estimated CPU frequency: %.3f GHz\n", ghz);
        printf("(Note: 1/throughput_ns × freq_GHz = cycles per instruction)\n\n");
        printf("%-30s %10s %10s %10s\n", "Instruction", "ns/instr", "cyc@est", "Expected");
        printf("%-30s %10s %10s %10s\n", "----------", "--------", "-------", "--------");

        auto report = [&](const char* name, double ns, const char* expected) {
            double cycles = ns * ghz;
            printf("%-30s %10.3f %10.3f %10s\n", name, ns, cycles, expected);
        };

        double ns_popcntb   = measure_throughput(bench_vpopcntb, M);
        double ns_ternlog   = measure_throughput(bench_vpternlogq, M);
        double ns_broadcast = measure_throughput(bench_vpbroadcastb, M);
        double ns_movsxbw   = measure_throughput(bench_vpmovsxbw, M);
        double ns_subb      = measure_throughput(bench_vpsubb, M);
        double ns_cvt8to32  = measure_throughput(bench_cvtepi8_epi32, M);
        double ns_mixed_pair = measure_throughput(bench_popcnt_sub_pair, M);

        report("vpopcntb zmm,zmm", ns_popcntb, "port0/1 OR p5");
        report("vpternlogq zmm x3", ns_ternlog, "0.5c (port0/5)");
        report("vpbroadcastb zmm,r8", ns_broadcast, "1c (port5)");
        report("vpmovsxbw zmm,ymm", ns_movsxbw, "1c (port5)");
        report("vpsubb zmm x3", ns_subb, "0.5c (port0/5)");
        report("cvtepi8_epi32 zmm,xmm", ns_cvt8to32, "1c (port5)");

        printf("\n--- Mixed (as in kernel hot path) ---\n");
        // bench_popcnt_sub_pair: 4 popcnt + 4 subb = 8 instructions per iter
        // But measure_throughput divides by 8*M already
        printf("%-30s %10.3f %10.3f %10s\n",
               "popcntb+subb pair x4", ns_mixed_pair,
               ns_mixed_pair * ghz, "port contention");

        printf("\n--- Port Assignment Diagnosis ---\n");
        printf("vpopcntb throughput: %.3f cycles\n", ns_popcntb * ghz);
        if (ns_popcntb * ghz < 0.6) {
            printf("  → DUAL PORT (0/1): vpopcntb has 0.5c throughput → TWO ports available\n");
            printf("  → fact_004 'port 5 only' is WRONG for this instruction\n");
        } else if (ns_popcntb * ghz < 1.1) {
            printf("  → SINGLE PORT: vpopcntb has ~1c throughput\n");
            if (ns_popcntb * ghz < 0.8) {
                printf("  → Close to 0.5c: possibly dual port 0/1\n");
            } else {
                printf("  → ~1c: single port (could be port 0, 1, or 5)\n");
            }
        } else {
            printf("  → Slower than expected: %.3f cycles (possible measurement artifact)\n", ns_popcntb * ghz);
        }

        printf("\nvpbroadcastb throughput: %.3f cycles\n", ns_broadcast * ghz);
        printf("vpternlogq throughput: %.3f cycles\n", ns_ternlog * ghz);
        printf("  → If ternlog ~0.5c: dual-port (port 0/5) confirmed\n");
        printf("  → If broadcast ~1c: single-port 5 confirmed\n");

        printf("\nvpmovsxbw (widening) throughput: %.3f cycles\n", ns_movsxbw * ghz);
        printf("  → If ~1c and same port as broadcast, they contend\n");
        printf("  → int8 accumulation eliminates these from inner loop\n");
    }

    return 0;
}
