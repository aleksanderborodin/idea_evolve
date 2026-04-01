# Observations — gen002_explore_2

## Directive
Track B: radical exploration — no BLIS tiling, no packing, start from scratch.
Assigned approach: transposed/column-major computation with output-stationary accumulation.

## What I tried

### Core idea: no-packing, direct B access
All solutions eliminate pack_A and pack_B entirely. Instead of copying data into aligned
panels, they load B columns directly from memory and keep them in zmm registers (or L1/L2).
The hypothesis: packing overhead is large enough that direct access is faster.

**This hypothesis was wrong.** All 4 solutions scored worse than the current best (148.18 µs).
The packing overhead is small; the benefit of sequential L1-resident Bp access in the
micro-kernel outweighs the cost.

---

### sol01 — jc-outer, 8-row batch, int16, B_reg[128] on stack — 207.32 µs
- B_reg declared as `alignas(64) __m512i B_reg[128]` (8192 bytes on stack)
- Compiler cannot promote B_reg to zmm registers (array too large, unknown size at compile time)
- B_reg accesses go through L1 cache, not zmm registers — extra memory latency per access
- No `#pragma GCC unroll` on k-loop → scalar loop overhead for k_bytes iterations
- large=5421 µs (70% worse than best 3176 µs)
- **Bug encountered**: int8 accumulators overflow for k_bytes=32 (correctness test). Fixed to int16.

### sol02 — template<KB> + always_inline, int8, switch dispatch — 318.96 µs
- Used `template<int KB>` with `__attribute__((always_inline))` to force B_reg[KB] into registers
- Three instantiations (KB=2,4,7) inlined into gemmCandidate via switch
- Result: I-cache pressure from three large inlined code blocks WORSE than sol01
- Confirms pattern_003: template specialization with multiple instantiations hurts I-cache
- int8 accumulators reduce register pressure but the I-cache penalty dominates

### sol03 — named zmm variables (b0..b6), k<=7 fast path — 200.38 µs
- Named scalar zmm variables instead of array: `__m512i b0, b1, b2, b3, b4, b5, b6`
- Forces compiler to allocate each as a zmm register (no array indirection)
- `if (k_bytes > N) ACCUM(bN, N)` pattern: runtime-conditional unrolled k-loop
- Slightly better than sol01 (200 vs 207 µs) — confirms named vars help register allocation
- Still significantly worse than BLIS best. The B reuse benefit is real but insufficient.

### sol04 — ic-outer + jc-inner + streaming NT stores — 182.31 µs ← BEST of this session
- Flipped loop order: row-outer, column-inner → sequential C writes along each row
- Streaming NT stores (`_mm512_stream_si512`) for large C (>8MB) — avoids write-allocate RFO
- Alignment check at runtime: only streams when C is 64-byte aligned
- **small=3.66 µs (better than best 4.49!)**, medium=281.17 µs, large=5887 µs
- Large is WORSE than jc-outer — sequential C writes don't help enough because:
  - B is now read 32 times (n/4 row batches × all m) vs once in jc-outer
  - B (448KB) fits in L2 but 32x re-reads cost ~70 µs total — less than expected
  - The large degradation suggests streaming stores aren't firing (C alignment not met)
    or the B re-read cost is higher than estimated
- Small improvement confirms: sequential C writes + streaming stores help for small case

---

## Key learnings

1. **Packing is efficient**: pack_B overhead (448KB from L2 → L1) is tiny (~2 µs). The
   micro-kernel reading from L1-resident Bp is faster than reading B from L2 directly.

2. **jc-outer vs ic-outer tradeoff**: jc-outer minimizes B reads (once per 64-col block)
   but scatters C writes. ic-outer gives sequential C writes but reads B n/4 times.
   Neither is strictly better — C write bandwidth and B re-read costs roughly balance.

3. **Streaming stores**: only effective if C is 64-byte aligned (which isn't guaranteed by
   the benchmark harness `new int[]`). The small improvement on sol04-small suggests they
   sometimes fire. An aligned allocation path would help more.

4. **Register allocation**: named zmm variables > small array > large array. With k_bytes=7
   and named b0..b6, the compiler uses 7 zmm registers directly. With B_reg[128], all
   accesses go through stack memory.

5. **int8 vs int16 accumulators**: int8 halves accumulator register count (8 vs 16 zmm for
   8 rows), but int8→int32 expansion at store requires 4×extract vs int16→int32's 2×extract.
   Net benefit is small; int16 is safer for general k_bytes.

6. **Template instantiation bloat**: 3 inlined switch branches is worse than one general
   loop with pragma unroll. Confirms pattern_003 recommendation.

---

## What I did NOT try (hypotheses for future)

- **vpshufb 4-bit LUT**: precompute nibble LUTs for each (pos_nibble, neg_nibble) pair,
  then use vpshufb to look up 4-bit contributions in one cycle. Could replace ternarylogic
  + 2×popcnt + sub with 2×vpshufb + add. Tiger Lake has vpshufb at port 5 (1 cycle).

- **Aligned C allocation**: if the problem could guarantee 64-byte aligned C, streaming
  stores could give the full 2x write-bandwidth improvement on large.

- **Prefetching B**: `_mm_prefetch(B + (t+1)*m + jc, _MM_HINT_T1)` in inner loop might
  hide the L2→register latency for B loads in the no-packing approach.

- **Register-blocked A transposed**: pack A into A_transposed[k_bytes][n] layout once
  before main loop; then each k-level's n pos/neg bytes are contiguous and can be loaded
  as 2 zmm vectors (for n=128), processed against all m columns without broadcasts.

- **Combining packing + streaming stores**: keep BLIS pack_B but add streaming stores
  for C writes to get the best of both worlds.

---

## State of Affairs accuracy
Accurate. Skip-memset (idea_010) confirmed critical. The "No-packing direct kernel"
(idea_013) was correctly listed as "untested" — now tested, and found to be slower.
The streaming-stores benefit (idea_006) is real but alignment requirements make it
unreliable without controlling C allocation.

## What I'd do with more time
1. Try vpshufb 4-bit LUT approach — may give 1.5-2x speedup on compute-bound sizes
2. Keep BLIS packing but add streaming NT stores for C (aligned alloc workaround)
3. Profile with `perf stat` to confirm whether large is bandwidth-bound or compute-bound
4. Measure pack_B vs micro_kernel timing breakdown
