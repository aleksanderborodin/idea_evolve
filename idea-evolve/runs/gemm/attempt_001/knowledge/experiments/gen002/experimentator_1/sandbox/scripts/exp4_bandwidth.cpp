/*
 * Experiment 4: Memory bandwidth measurement
 * Question: What is the actual DRAM write bandwidth? Is large hitting the ceiling?
 * Tests:
 *   1. Streaming store bandwidth (NT writes to 32 MB buffer)
 *   2. Regular store bandwidth (same)
 *   3. memset bandwidth
 *   4. Read bandwidth (sequential load from 32 MB buffer)
 *   5. Combined read+write (simulating kernel: read B, write C)
 */
#include <immintrin.h>
#include <stdint.h>
#include <string.h>
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <time.h>

static double get_time_us() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1e6 + ts.tv_nsec / 1000.0;
}

// Test 1: Streaming store bandwidth
double test_stream_write(void* buf, size_t bytes, int reps) {
    __m512i zero = _mm512_setzero_si512();
    double best = 1e18;
    for (int r = 0; r < reps; r++) {
        double t0 = get_time_us();
        char* p = (char*)buf;
        for (size_t i = 0; i < bytes; i += 64) {
            _mm512_stream_si512((__m512i*)(p + i), zero);
        }
        _mm_sfence();
        double t1 = get_time_us();
        best = std::min(best, t1 - t0);
    }
    return best;
}

// Test 2: Regular store bandwidth
double test_regular_write(void* buf, size_t bytes, int reps) {
    __m512i zero = _mm512_setzero_si512();
    double best = 1e18;
    for (int r = 0; r < reps; r++) {
        double t0 = get_time_us();
        char* p = (char*)buf;
        for (size_t i = 0; i < bytes; i += 64) {
            _mm512_storeu_si512((__m512i*)(p + i), zero);
        }
        double t1 = get_time_us();
        best = std::min(best, t1 - t0);
    }
    return best;
}

// Test 3: memset bandwidth
double test_memset(void* buf, size_t bytes, int reps) {
    double best = 1e18;
    for (int r = 0; r < reps; r++) {
        double t0 = get_time_us();
        memset(buf, 0, bytes);
        double t1 = get_time_us();
        best = std::min(best, t1 - t0);
    }
    return best;
}

// Test 4: Read bandwidth (load and accumulate to prevent optimization)
double test_read(void* buf, size_t bytes, int reps) {
    __m512i acc = _mm512_setzero_si512();
    double best = 1e18;
    for (int r = 0; r < reps; r++) {
        double t0 = get_time_us();
        char* p = (char*)buf;
        for (size_t i = 0; i < bytes; i += 64) {
            acc = _mm512_xor_si512(acc, _mm512_loadu_si512((__m512i*)(p + i)));
        }
        double t1 = get_time_us();
        best = std::min(best, t1 - t0);
    }
    // Prevent optimization of acc
    volatile int x = _mm512_reduce_add_epi32(acc);
    (void)x;
    return best;
}

// Test 5: Read small + write large (simulates kernel reading B from cache + writing C to DRAM)
double test_read_small_write_large(void* rbuf, size_t rbytes, void* wbuf, size_t wbytes, int reps) {
    double best = 1e18;
    __m512i acc = _mm512_setzero_si512();
    for (int r = 0; r < reps; r++) {
        double t0 = get_time_us();
        char* wp = (char*)wbuf;
        char* rp = (char*)rbuf;
        size_t ri = 0;
        for (size_t wi = 0; wi < wbytes; wi += 64) {
            acc = _mm512_xor_si512(acc, _mm512_loadu_si512((__m512i*)(rp + ri)));
            _mm512_stream_si512((__m512i*)(wp + wi), acc);
            ri += 64;
            if (ri >= rbytes) ri = 0;
        }
        _mm_sfence();
        double t1 = get_time_us();
        best = std::min(best, t1 - t0);
    }
    volatile int x = _mm512_reduce_add_epi32(acc);
    (void)x;
    return best;
}

int main() {
    // Buffer sizes matching benchmark scenarios
    struct { const char* name; size_t bytes; } sizes[] = {
        {"128 KB (L1/L2)", 128 * 1024},
        {"4 MB (medium C)", 4 * 1024 * 1024},
        {"32 MB (large C)", 32 * 1024 * 1024},
        {"64 MB (2x large)", 64 * 1024 * 1024},
    };
    int n_sizes = sizeof(sizes) / sizeof(sizes[0]);
    int REPS = 20;

    printf("=== Write Bandwidth (GB/s) ===\n");
    printf("%-18s  %12s  %12s  %12s\n", "Size", "stream_wr", "regular_wr", "memset");
    for (int s = 0; s < n_sizes; s++) {
        void* buf = _mm_malloc(sizes[s].bytes, 64);
        memset(buf, 0, sizes[s].bytes); // warm up pages

        double t_stream = test_stream_write(buf, sizes[s].bytes, REPS);
        double t_regular = test_regular_write(buf, sizes[s].bytes, REPS);
        double t_memset = test_memset(buf, sizes[s].bytes, REPS);

        double bw_stream = sizes[s].bytes / (t_stream * 1e-6) / 1e9;
        double bw_regular = sizes[s].bytes / (t_regular * 1e-6) / 1e9;
        double bw_memset = sizes[s].bytes / (t_memset * 1e-6) / 1e9;

        printf("%-18s  %10.2f    %10.2f    %10.2f\n",
               sizes[s].name, bw_stream, bw_regular, bw_memset);
        _mm_free(buf);
    }

    printf("\n=== Read Bandwidth (GB/s) ===\n");
    printf("%-18s  %12s\n", "Size", "seq_read");
    for (int s = 0; s < n_sizes; s++) {
        void* buf = _mm_malloc(sizes[s].bytes, 64);
        memset(buf, 0xAA, sizes[s].bytes);

        double t_read = test_read(buf, sizes[s].bytes, REPS);
        double bw_read = sizes[s].bytes / (t_read * 1e-6) / 1e9;

        printf("%-18s  %10.2f\n", sizes[s].name, bw_read);
        _mm_free(buf);
    }

    printf("\n=== Theoretical Minimum Times for GEMM Output ===\n");
    struct { const char* name; int n, m; } gemm_sizes[] = {
        {"small",  32,  1024},
        {"medium", 64,  16384},
        {"large",  128, 65536},
    };

    // Use 32 MB bandwidth measurement for large, 4 MB for medium
    void* buf32 = _mm_malloc(32 * 1024 * 1024, 64);
    memset(buf32, 0, 32 * 1024 * 1024);
    double t_stream_32mb = test_stream_write(buf32, 32 * 1024 * 1024, REPS);
    double bw_stream_32mb = (32 * 1024 * 1024) / (t_stream_32mb * 1e-6) / 1e9;
    _mm_free(buf32);

    void* buf4 = _mm_malloc(4 * 1024 * 1024, 64);
    memset(buf4, 0, 4 * 1024 * 1024);
    double t_stream_4mb = test_stream_write(buf4, 4 * 1024 * 1024, REPS);
    double bw_stream_4mb = (4 * 1024 * 1024) / (t_stream_4mb * 1e-6) / 1e9;
    _mm_free(buf4);

    printf("Stream write BW @ 4 MB:  %.2f GB/s\n", bw_stream_4mb);
    printf("Stream write BW @ 32 MB: %.2f GB/s\n", bw_stream_32mb);
    printf("\n");

    for (int s = 0; s < 3; s++) {
        size_t output_bytes = (size_t)gemm_sizes[s].n * gemm_sizes[s].m * sizeof(int);
        double bw = (output_bytes > 8 * 1024 * 1024) ? bw_stream_32mb : bw_stream_4mb;
        double min_time_us = output_bytes / (bw * 1e9) * 1e6;
        printf("%-8s  output=%7.2f MB  min_write_time=%8.2f µs (at %.1f GB/s)\n",
               gemm_sizes[s].name,
               output_bytes / 1e6,
               min_time_us, bw);
    }

    // Also measure combined read+write which is closer to actual kernel behavior
    printf("\n=== Combined Read+Write (simulates kernel) ===\n");
    // For large: read ~458 KB of B (7 k_bytes × 65536 cols, fits L2), write 32 MB of C
    void* rbuf = _mm_malloc(512 * 1024, 64);
    void* wbuf = _mm_malloc(32 * 1024 * 1024, 64);
    memset(rbuf, 0xAA, 512 * 1024);
    memset(wbuf, 0, 32 * 1024 * 1024);

    double t_combined = test_read_small_write_large(rbuf, 512 * 1024, wbuf, 32 * 1024 * 1024, REPS);
    double bw_combined = (32 * 1024 * 1024) / (t_combined * 1e-6) / 1e9;
    printf("Read 512KB (cyclic) + stream write 32MB: %.2f µs (%.2f GB/s effective write)\n",
           t_combined, bw_combined);

    _mm_free(rbuf);
    _mm_free(wbuf);

    return 0;
}
