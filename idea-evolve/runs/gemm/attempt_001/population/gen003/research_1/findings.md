# Research Findings — NT Stores via SSE, Multi-Threading, k-Template Specialization, Bandwidth Ceiling

## Summary
This session investigated five priority questions. The most actionable findings are: (1) 128-bit SSE NT stores (`_mm_stream_si128`) bypass the 64-byte alignment constraint since glibc guarantees 16-byte alignment for `std::vector`, (2) multi-threading with 2 cores is completely unexplored and could reduce large by 40–60%, (3) template specialization on k_bytes can cut small overhead significantly, (4) the 24 µs target is bandwidth-impossible given measured constraints — the realistic achievable ceiling is ~50–80 µs.

---

## Finding 1: SSE 128-bit NT Stores Bypass the Alignment Constraint

**Relevance**: All agents attempting NT stores for large benchmark (idea_015).

**Detail**: Every NT store attempt so far has used `_mm512_stream_si512` which requires 64-byte alignment. The harness allocates `std::vector<int> res`, and glibc's `malloc` guarantees **16-byte alignment** (not 64-byte). This causes either runtime faults or fallback to regular stores.

However, `_mm_stream_si128` (MOVNTDQ, 128-bit form) requires only **16-byte alignment**. Since glibc guarantees 16-byte alignment for any `std::vector<int>`, this ALWAYS works without a runtime alignment check or temp buffer.

Implementation: after computing a 512-bit int8 accumulator and widening to 4×128-bit int32 chunks, store each chunk with `_mm_stream_si128`:

```cpp
// Widen acc8 → 4 × zmm_128bit_int32
__m128i q0 = _mm512_castsi512_si128(acc8_widened);
__m128i q1 = _mm512_extracti32x4_epi32(acc8_widened, 1);
__m128i q2 = _mm512_extracti32x4_epi32(acc8_widened, 2);
__m128i q3 = _mm512_extracti32x4_epi32(acc8_widened, 3);
_mm_stream_si128((__m128i*)(C_row + j),    q0);
_mm_stream_si128((__m128i*)(C_row + j+4),  q1);
_mm_stream_si128((__m128i*)(C_row + j+8),  q2);
_mm_stream_si128((__m128i*)(C_row + j+12), q3);
```

Must call `_mm_sfence()` after the full loop.

**The runtime check becomes**: `bool use_nt = ((size_t)n * m * 4 > 8*1024*1024);` — no alignment check needed since 16-byte alignment is guaranteed!

The bandwidth penalty: `_mm_stream_si128` achieves the same peak DRAM write bandwidth as `_mm512_stream_si512` (both saturate the write-combining buffers the same way). The extra instructions (4× per cache line instead of 1×) add CPU overhead but do not reduce memory bandwidth.

**Actionable implication**: Replace the `_mm512_stream_si512` NT store attempts (which faulted) with `_mm_stream_si128`. Apply size-adaptively: ONLY when `n*m*sizeof(int) > 8MB` (i.e., large benchmark only). This is the single most important correctness fix for idea_015.

Estimated large improvement: 3841 µs → ~1300–1500 µs (2.3–2.9× speedup on large alone). Geomean effect: (3.69 × 225.55 × 1400)^(1/3) ≈ **105 µs**.

---

## Finding 2: Multi-Threading with 2 Cores — Completely Unexplored

**Relevance**: All agents targeting large benchmark. This is the highest-risk, highest-reward unexplored direction.

**Detail**: The benchmark uses `cgexec -g cpu:bench_group`. This cgroup contains **cores 0 and 1** (not just core 0). Any `pthread` or `std::thread` launched from within `gemmCandidate` will be scheduled by the Linux scheduler within the cgroup, meaning it CAN run on core 1 simultaneously.

Intel i5-1135G7 has DDR4-3200 **dual-channel** memory. Single-thread NT store bandwidth measured at 24.84 GB/s. However:
- Dual-channel memory can service 2 independent address streams concurrently
- Literature shows 2-thread write bandwidth is typically 1.3–1.8× single-thread on dual-channel DDR4
- If 2 threads collectively achieve 40 GB/s: large (32 MB) drops from ~1350 µs to **~840 µs**

Multi-threading also parallelizes compute: with 2 threads each handling 64 rows, compute time (estimated 680 µs single-thread) drops to ~340 µs per thread. Since compute and stores can overlap: bottleneck = max(compute/2, bandwidth/2) per thread.

**Implementation pattern**:
```cpp
#include <pthread.h>
static pthread_t thr_pool[2];
static std::once_flag pool_init;

// Thread 0: rows 0..n/2-1, Thread 1: rows n/2..n-1
// Use a simple barrier (pthread_barrier_t) to synchronize
// Create threads ONCE (static), reuse across calls to avoid creation overhead
// Call _mm_sfence() in each thread after NT stores
// Call _mm_sfence() in main thread after join
```

**Critical: thread pool pattern** — the benchmark calls gemmCandidate 10× per size. `pthread_create` overhead is ~5–20 µs per call. If threads are created fresh each call: overhead ≈ 10× 20 µs = 200 µs per size. Must use a **persistent thread pool** with `pthread_once`/`std::call_once` to create threads on the first call and reuse them via semaphore/condvar signaling.

**Actionable implication**: This is completely unexplored — the coverage matrix shows zero solutions use multi-threading. Priority for gen-3 exploit or full agents:
1. Implement 2-thread row split with static thread pool
2. Each thread computes its row range and NT-stores using `_mm_stream_si128`
3. Main thread waits for both to finish, then `_mm_sfence()`
4. Apply only for large (n*m*4 > 8MB)

If 2-thread bandwidth scales to 40 GB/s: geomean(3.69, 225.55, 840) = (3.69 × 225.55 × 840)^(1/3) ≈ **87 µs**. Combined with SSE NT stores: potentially similar.

**Risk**: Thread creation/sync overhead. Mitigated by static thread pool. Must validate correctness with the harness's 64×64×256 test case.

---

## Finding 3: Template Specialization on k_bytes for Small Benchmark

**Relevance**: All agents targeting small benchmark. Directly addresses the 3.69 µs → target 1.0 µs gap.

**Detail**: The small benchmark has k_bytes=2, medium has k_bytes=4, large has k_bytes=7. These are known at COMPILE TIME for each benchmark call. The current kernel has a loop `for (int t = 0; t < k_bytes; t++)` that is NOT fully unrolled by the compiler because k_bytes is a runtime parameter.

For small (k_bytes=2): the k-loop runs exactly 2 iterations. With a compile-time constant:
- The compiler can fully unroll: 0 loop overhead, 0 branch prediction misses
- The `a_pos[32]` / `a_neg[32]` stack arrays collapse to `a_pos_0`, `a_pos_1`, `a_neg_0`, `a_neg_1` — 4 zmm registers kept in register file (no stack spills)
- The `if ((t & 15) == 14 || t == k_bytes - 1)` flush check is resolved at compile time (only fires at t=1)

Implementation via dispatch switch (avoids I-cache penalty from multiple large templates):
```cpp
void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k) {
    const int k_bytes = k / 8;
    switch (k_bytes) {
        case 2: gemm_impl<2>(A, B, C, n, m); return;
        case 4: gemm_impl<4>(A, B, C, n, m); return;
        case 7: gemm_impl<7>(A, B, C, n, m); return;
        default: gemm_impl_runtime(A, B, C, n, m, k_bytes);
    }
}
```

Pattern_003 warns that template specialization causes I-cache regressions. HOWEVER: the regression occurred when ALL specializations are called in the same benchmark run. Here, EACH benchmark size uses exactly ONE specialization (k_bytes=2 for small, 4 for medium, 7 for large). The other templates exist in code but are never executed — they don't pollute the I-cache during execution.

The correctness test includes a 64×64×256 (k_bytes=32) case. The `default:` branch handles this. Only benchmark sizes get the optimized templates.

**Estimated small improvement**: The k=2 case has 2 zmm broadcasts per row per k-byte (4 total outside j-loop). Without stack spills and with full unrolling, the inner j-loop becomes essentially free of loop overhead. Estimated reduction: 3.69 µs → 1.0–1.5 µs.

**Actionable implication**: Implement `gemm_impl<int KB>` with compile-time k_bytes. Dispatch at function entry. Combine with SSE NT stores (different template instantiation for large). This is a prerequisite for any further small optimization.

---

## Finding 4: Bandwidth Ceiling Analysis — 24 µs Target is Physically Impossible

**Relevance**: All agents setting expectations. This changes how gen-3 should allocate effort.

**Detail**: Using fact_007 measured bandwidth:
- Large (32 MB C, NT stores): 32 MB / 24.84 GB/s = **1351 µs minimum**
- Medium (4 MB C, L3-warm regular stores): current best 225.55 µs is within 3% of floor (**220–230 µs minimum**)
- Small (128 KB C, L1-resident): compute-limited, theoretical ~0.3 µs, practical ≥ 0.5 µs

Target analysis: geomean(small, medium, large) = 24 requires `small × medium × large = 13,824`.
With medium_min=220 and large_min=1351: `small = 13824 / (220 × 1351) = 0.046 µs`.

**0.046 µs for small is ~125 CPU cycles — impossible.** Function call overhead alone is ~30 cycles.

The correct achievable targets with all optimizations:

| Scenario | small | medium | large | geomean |
|----------|-------|--------|-------|---------|
| Current best | 3.69 | 225.55 | 3841.72 | 147.26 |
| + SSE NT stores (large) | 3.69 | 225.55 | ~1350 | ~105 |
| + k-template (small) | ~1.5 | 225.55 | ~1350 | ~80 |
| + 8-row int8 kernel | ~1.5 | ~200 | ~1200 | ~71 |
| + 2-thread for large | ~1.5 | ~200 | ~700 | ~57 |
| Theoretical minimum | ~0.5 | ~220 | ~840 | ~52 |

**The realistic target for gen-3 is 70–105 µs**, not 24 µs. Gen-3 agents should focus on:
1. SSE NT stores (largest single impact)
2. Multi-threading for large (second largest)
3. k-template for small (third)

**Actionable implication**: Do NOT spend effort trying to reduce medium below 220 µs — it's at the bandwidth floor. Do NOT waste turns on medium-focused optimizations. Focus all effort on large (NT stores, multi-threading) and small (template unrolling).

---

## Finding 5: Column-Outer Kernel — Reduces B Reads, But Strided C Writes May Negate Benefit

**Relevance**: Full and exploit agents willing to implement a new architecture variant.

**Detail**: Current row-outer loop: for each row i (n=128), sweep j=0..65535 in 64-col blocks. B is read 128 times (once per row). Total B data transferred: 128 × 448 KB = 56 MB.

Alternative column-outer: for each j-block, process ALL rows. B is loaded ONCE per j-block.

```
for j in 0..m, step 64:          // 1024 iterations for large
    for t in 0..k_bytes:
        vb[t] = load B[t*m + j]  // 7 zmm loads, kept in register
    for ir in 0..n, step 8:       // 16 groups of 8 rows
        compute 8 rows using vb[0..6]  // all in registers
        store 8 rows of C at C[ir*m+j..] — STRIDED by m=65536
```

Register budget: 7 zmm for vb + 8 zmm acc + 2 zmm temp = 17 zmm. Comfortable.
B total reads: (m/64) × k_bytes = 1024 × 7 = 7168 zmm loads = 448 KB. B read ONCE total!

**Problem**: C stores are strided by `m*sizeof(int) = 65536*4 = 256 KB` between rows. With regular stores, each write goes to a different 4 KB page → TLB thrashing + cache set conflicts. With NT stores, strided writes still work (bypasses cache), but the write-combining buffers (10–12 WCBs on Intel) can only hold 10–12 simultaneous cache-line writes. With stride 256 KB, 8 consecutive row stores go to 8 different WCBs — this exceeds the WCB count and causes partial writes without coalescing.

**However**: with `_mm_stream_si128` (128-bit stores), each store fills one WCB entry with 16 bytes. Four stores per row-column fill one 64-byte WCB. 8 rows × 4 stores = 32 stores = 8 WCBs simultaneously. This matches the WCB count. So column-outer with 8-row blocking and 128-bit NT stores might work IF WCBs are managed correctly.

**Expected benefit**: B read from DRAM drops from 56 MB to 448 KB (56 MB saved at 12.9 GB/s = 4.3 ms theoretical savings — far more than the 3.8 µs current large time). But this analysis is wrong: the current row-outer already benefits from B being in L3 cache (448 KB << 8 MB L3). B is read from L3 at ~200 GB/s, not DRAM. So B read savings are only: 56 MB at L3 = 280 µs vs 448 KB at L3 = 2.2 µs. Savings: 278 µs from B reads alone.

**This is potentially significant**: if B reuse in L3 currently contributes 278 µs, the column-outer approach could save this. Combined with NT stores for C writes: large target = 1350 (C write) + 2 (B read) + 50 (compute) ≈ 1400 µs — essentially the same as row-outer with NT stores.

**Conclusion**: Column-outer is no better than row-outer with NT stores for large (both are bounded by C write bandwidth). Not worth implementing unless row-outer + NT stores is validated first.

---

## Finding 6: vpshufb LUT Kernel — Low Confidence, Skip for Now

**Relevance**: Agents considering alternative compute paths (idea_018).

**Detail**: `vpshufb` performs a 4-bit-indexed table lookup on 16-byte blocks. Using it for the binary-ternary kernel would require a 16-entry LUT per (a_pos_nibble, a_neg_nibble) combination, computed before the j-loop. The current `vpternlogd + vpopcntb` approach uses 2+2=4 port-0 instructions per k-byte per row per 64 columns. The vpshufb approach would use 2 vpshufb (port 5) + additions — trading port 0 pressure for port 5.

Given that pattern_008 identifies port 5 as the current bottleneck (vpbroadcastb already saturates it), adding more port 5 ops via vpshufb would worsen performance.

**Actionable implication**: Skip vpshufb LUT kernel until port pressure analysis shows port 0 is the bottleneck. Current evidence suggests port 5 is saturated.

---

## Open Questions

1. **Does 2-thread NT store actually achieve >24.84 GB/s combined on this Tiger Lake?** Must be measured empirically. The theoretical dual-channel benefit is 1.3–1.8× but depends on memory controller arbitration. Cgroup allows core 1 — but does the OS scheduler actually place the thread on core 1 vs core 0 (hyperthread)?

2. **What is the actual large time with 128-bit SSE NT stores on the current row-streaming best?** The previous NT store attempt (sol04, 195 µs) used a 2-row variant and likely wasn't size-adaptive. The 1-row variant with size-adaptive 128-bit NT stores is untested.

3. **Does `posix_memalign` + aligned buffer + memcpy outperform 128-bit NT stores?** For 32 MB: aligned buffer with 512-bit NT stores achieves 24.84 GB/s write bandwidth. But the memcpy FROM the aligned buffer TO C (unaligned) must use regular stores at 11.38 GB/s. Total time = computation + 32 MB/24.84 GB/s + 32 MB/11.38 GB/s = 1351 + 2947 = 4298 µs. WORSE. Avoid.

4. **Tiger Lake micro-op fusion**: Does the compiler use macro-fusion for `popcnt + sub` pairs? Any uop-level optimization beyond current `-O3` flags?

5. **Can the harness `std::vector<int>` alignment be exploited?** Is the 16-byte alignment exactly at offset 0, or could it be any 16-byte boundary? (Answer: the `.data()` pointer is guaranteed to return a 16-byte aligned address in practice on glibc, so `(uintptr_t)C % 16 == 0` should always hold.)
