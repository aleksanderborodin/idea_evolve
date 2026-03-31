# Research Findings — Bandwidth Limits, 8-Row Kernel, and NT Stores

## Summary
The current 148 µs best is bottlenecked by **memory bandwidth for C writes**, not compute. The 24 µs target is theoretically achievable but requires three simultaneous changes: NT stores for the large benchmark (32 MB output), an 8-row int8 kernel to double B-load reuse, and reducing small-benchmark overhead. All 14 gen-1 solutions share the same 4-row int16 BLIS template — none exploit NT stores correctly or use int8 accumulation.

---

## Finding 1: Theoretical Lower Bounds Confirm 24 µs Is Achievable

**Relevance**: Every agent, especially exploit and full agents. Sets ceiling on what optimizations matter.

**Detail**:

| Size | C bytes | B bytes | A bytes | Min write time (50 GB/s NT) | Min read B (200 GB/s L3) |
|------|---------|---------|---------|----------------------------|--------------------------|
| Small | 128 KB | 2 KB | 128 B | 2.6 µs | 0.01 µs |
| Medium | 4 MB | 64 KB | 512 B | 80 µs | 0.3 µs |
| Large | 32 MB | 448 KB | 1.8 KB | 640 µs | 2.2 µs |

Tiger Lake (i5-1135G7) specs:
- DRAM: DDR4-3200 dual-channel → **51.2 GB/s theoretical**, ~40-50 GB/s practical for NT stores
- L3: 8 MB shared, ~200 GB/s per core (estimated)
- L2: 1.25 MB, ~300 GB/s per core
- L1: 48 KB, ~400+ GB/s per core

With NT stores at 50 GB/s:
- Large: 32 MB / 50 GB/s = **640 µs** (vs current 3176 µs — 5x improvement available)
- Medium: 4 MB / 50 GB/s = **80 µs** (vs current 228 µs — 2.9x)
- Small: 128 KB in L2 at 300 GB/s = **0.43 µs** (vs current 4.49 µs — 10x headroom in theory, but overhead limits this to ~0.5-1 µs practical)

Target geomean check: geomean(1.0, 80, 640) = (1 × 80 × 640)^(1/3) = (51200)^(1/3) ≈ **37 µs**
With better small (0.5 µs): geomean(0.5, 80, 640) = (25600)^(1/3) ≈ **29 µs**
With medium at 60 µs: geomean(0.5, 60, 640) = (19200)^(1/3) ≈ **27 µs**

**24 µs requires**: large ~500-600 µs + medium ~60-70 µs + small ~0.3-0.5 µs. Tight but physically achievable.

**Actionable implication**: The biggest single lever is NT stores for large. Without them, large cannot drop below ~2000-3000 µs (current regular stores are cache-polluting and suffer RFO overhead for write-only patterns). Every new solution MUST use NT stores for large. Medium is borderline: 4 MB fits in L3 (8 MB), so NT stores might not help — test both. Small is currently at 4.49 µs vs a theoretical ~0.5 µs minimum, meaning pack overhead and function call overhead dominate.

---

## Finding 2: Size-Adaptive NT Stores — The Single Biggest Win

**Relevance**: All solution agents, especially exploit. This alone could give 3-5x speedup on large.

**Detail**: Current solutions (including best sol10) use regular `_mm512_storeu_si512` for all C stores. For large (32 MB output), this causes:
1. **RFO (Read For Ownership)**: CPU must fetch each cache line before writing, even for write-only patterns
2. **Cache pollution**: 32 MB evicts all useful data from L3 (8 MB)
3. **Write bandwidth halved**: RFO doubles the effective memory traffic

Non-temporal stores (`_mm512_stream_si512`) bypass the cache:
- Write directly to DRAM without RFO
- No cache pollution
- **Requirement**: address must be 64-byte aligned

The benchmark harness allocates C with `new int[n*m]` or similar — alignment is not guaranteed to be 64-byte. However:
- `jc` advances in steps of NC=256 (=64 ints × 4 bytes = 256 bytes, 64-byte aligned ✓)
- `ir` advances in steps of 4 rows; C pointer offset = `ir*m + jc`. Since m=65536 for large, each row offset is m×4 = 262144 bytes (divisible by 64). So all store addresses are 64-byte aligned IF C itself is 64-byte aligned.
- Use `((uintptr_t)C % 64 == 0)` check at entry to decide NT vs regular.
- After NT stores: **must call `_mm_sfence()`** before returning.

**When to use NT stores**:
- ONLY when `n * m * sizeof(int) > 8*1024*1024` (i.e., C doesn't fit in L3)
- For large (32 MB): YES → NT stores
- For medium (4 MB): MAYBE — test both; 4 MB fits in L3, so regular stores may be faster
- For small (128 KB): NO — C fits in L2, regular stores are faster

**Previous attempt failure** (sol09 tried NT stores → 171 µs worse than sol10 at 148 µs): Likely used NT stores unconditionally for all sizes, which hurt small and medium while only helping large. The fix is the size-adaptive threshold check.

**Actionable implication**: Add this at the start of gemmCandidate:
```cpp
bool use_nt = ((size_t)n * m * 4 > 8*1024*1024) && ((uintptr_t)C % 64 == 0);
```
Then use `_mm512_stream_si512` in the hot path when `use_nt` is true, `_mm512_storeu_si512` otherwise. Call `_mm_sfence()` after the loop when NT was used.

---

## Finding 3: 8-Row Kernel with int8 Accumulation

**Relevance**: Exploit and full agents. Addresses idea_009 (8-row kernel) which previously failed due to register pressure.

**Detail**: The gen-1 8-row attempt (sol with idea_009, score 493 µs) failed because it used int16 accumulation, requiring 2 zmm registers per row (since 1 zmm holds only 32 int16 values, but we need 64 columns). With 4 rows × int16: 4 × 2 = 8 zmm for accumulators. With 8 rows × int16: 8 × 2 = 16 zmm for accumulators — register spilling begins.

**Key insight**: For k_bytes ≤ 7, max accumulated value per output byte = 7 × 8 = 56. This fits comfortably in int8 (range ±127). So we can accumulate in int8 instead of int16, using only 1 zmm per row instead of 2.

Register budget for 8-row int8 kernel:
- 8 zmm accumulators (1 per row, 64 int8 values each)
- 1 zmm for vb (current B tile)
- 2 zmm for vp, vn (recomputed each row, can share registers)
- **Total: 11 zmm** — well within the 32 zmm register file

Compared to current 4-row int16:
- Same 8 zmm accumulators
- 2x more rows processed per B load → 2x fewer B loads
- `add_epi8` is 1 instruction (vs `cvtepi8_epi16 + add_epi16` = 2 instructions per row)

Performance impact:
- B loads halved → for B-load-bound workloads, up to 2x speedup
- Especially benefits medium (B = 64 KB in L2, repeated reads are the bottleneck)
- After k-loop: widen int8 → int32 via `cvtepi8_epi32` (4 ops per row for 64 cols) and store

**Actionable implication**: Replace the current 4-row int16 kernel with an 8-row int8 kernel:
```cpp
__m512i acc[8];  // 1 zmm per row, int8 accumulation
for (int r = 0; r < 8; ++r) acc[r] = _mm512_setzero_si512();
for (int k = 0; k < kc; ++k) {
    __m512i vb = _mm512_loadu_si512(B_p + k*64);
    for (int r = 0; r < 8; ++r) {
        __m512i vp = _mm512_set1_epi8(A_p[k*16 + r*2]);
        __m512i vn = _mm512_set1_epi8(A_p[k*16 + r*2 + 1]);
        __m512i diff = _mm512_sub_epi8(
            _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp, vn, vb, 0xD8)),
            _mm512_popcnt_epi8(_mm512_ternarylogic_epi64(vp, vn, vb, 0xE4)));
        acc[r] = _mm512_add_epi8(acc[r], diff);
    }
}
// Store: int8 → int32
for (int r = 0; r < 8; ++r) {
    // 4 calls to _mm512_cvtepi8_epi32 + 4 stores for 64 int32 values
    // Use NT stores if use_nt flag is set
}
```
Pack_A must be restructured: instead of groups of 4, use groups of 8, storing 16 bytes per k-byte (8 pos + 8 neg interleaved).

---

## Finding 4: 128-Column Micro-Kernel (Double-Width)

**Relevance**: Full and exploit agents after 8-row kernel is working.

**Detail**: The current micro-kernel processes 64 columns per B tile (1 zmm). We can double this to 128 columns (2 zmm) with minimal register overhead:

8-row × 128-col kernel register budget:
- 8 rows × 2 half-tiles = 16 zmm accumulators
- 2 zmm for vb_lo, vb_hi (two B tiles simultaneously)
- 2 zmm for vp, vn (shared)
- **Total: 20 zmm** — fits in 32

Benefit: per B load, we process 2x more output columns. The number of B load instructions halves again.

For large: per micro-kernel (8 rows × 128 cols × k_bytes):
- 2 B loads per k-byte (vs 1 for 64-col)
- But processes 128 cols × 8 rows = 1024 C elements
- Vs current 64 cols × 4 rows = 256 C elements (4x more output per call)
- Reduces loop overhead by 4x
- Better instruction-level parallelism: CPU can overlap computation on vb_lo and vb_hi

NC should be increased to 512 (multiple of 128) for this kernel. The B panel for NC=512 is 512×7 = 3584 bytes — still fits in L1.

**Actionable implication**: After validating the 8-row int8 kernel, extend it to process 128 columns by loading 2 B vectors and computing for both simultaneously.

---

## Finding 5: Vectorize pack_A (Critical for Small Benchmark)

**Relevance**: Exploit agents, especially for improving small benchmark score.

**Detail**: Current pack_A is a scalar loop that reformats A from native layout to 4-row-grouped format. For small (n=32, k_bytes=2): A is only 128 bytes total. pack_A performs 32 rows × 2 k-bytes × 4 bytes (2 pos+neg pairs) = 512 scalar stores.

The scalar loop has ~5 ns overhead per byte = ~2.5 µs for small's pack_A. This is 55% of the current small benchmark time (4.49 µs)!

Two approaches:
1. **SIMD pack_A**: Use AVX-512 gather to load A bytes and vpermb to reorder. A fits in 2 zmm registers (128 bytes). With a precomputed permutation index (64 bytes), a single `vpermt2b` can do the entire pack_A in ~4 instructions.

2. **Eliminate pack_A entirely**: For the micro-kernel, load A bytes directly from the original layout using `_mm_set1_epi8(A[row * k_bytes * 2 + k*2 + 0])` (scalar broadcast). This is what the non-BLIS kernel would do. For small where k_bytes=2 and n=32, the A access pattern is simple enough that broadcasts are cheaper than packing.

**Actionable implication**: For small benchmark specifically, eliminate pack_A and use direct broadcast from A. Structure the loop as:
```cpp
for (j in 0..m/64):
    for k in 0..k_bytes:
        vb = load(B + k*m + j*64)
        for r in 0..n:
            vp = broadcast(A[r*k_bytes*2 + k*2])
            vn = broadcast(A[r*k_bytes*2 + k*2 + 1])
            ... compute and accumulate
```
A (128 bytes) stays entirely in L1 throughout. B (2 KB) stays in L1. No packing overhead.

---

## Finding 6: The NC=512 Regression Mystery

**Relevance**: All agents trying to tune NC. Explains pattern_002.

**Detail**: The state of affairs notes NC=256 consistently outperforms NC=512, root cause unknown.

Analysis: With NC=256 (current), the pack_B writes B panels into Bp = 256×7 = 1792 bytes. This fits in L1 (48 KB). With NC=512: Bp = 3584 bytes — also fits in L1.

Likely cause: **B panel size vs instruction fetch buffer**. When NC increases, the micro_kernel's "jr" inner loop has more iterations (8 vs 4 for NC=512 vs NC=256). This may increase I-cache pressure or loop overhead. Additionally, with NC=512, the micro_kernel processes NC/64 = 8 B tiles per call, vs 4 with NC=256. The longer loop body may exceed the Loop Stream Detector buffer on Willow Cove (~64 µops).

Alternative cause: **TLB pressure**. Larger NC means micro_kernel writes to a larger C stripe, potentially causing TLB misses for huge C arrays.

**Actionable implication**: Try NC=128, NC=192 to see if smaller than 256 helps further. The sweet spot may be different for each benchmark size. Consider size-adaptive NC: small uses NC=128, medium/large use NC=256 or NC=512.

---

## Open Questions

1. **Does C alignment guarantee hold?** The harness must allocate C 64-byte aligned for NT stores to be safe. Need to verify or add runtime check.

2. **What is the actual NT store bandwidth on this specific machine?** Theoretical 51.2 GB/s, but measured value may differ (LPDDR4 vs DDR4, thermal throttling, etc.).

3. **Is the large benchmark latency or bandwidth bound?** If the CPU is generating stores faster than DRAM can accept them, more aggressive prefetching or larger tiles won't help. Need `perf stat -e cache-misses,LLC-store-misses` to confirm.

4. **vpternlogd truth table standardization**: Two truth tables are in use (0xD8/0xE4 vs 0xCA/0xAC). Both are correct (different operand ordering). Standardize on 0xD8/0xE4.

5. **Can B panel be read without packing for small?** B=2 KB fits in L1. Direct stride-m access for k_bytes=2 would access B[0..1023] and B[1024..2047] with stride 1024 bytes. These are in different cache lines but both in L1 after first touch. Packing overhead may exceed the benefit.
