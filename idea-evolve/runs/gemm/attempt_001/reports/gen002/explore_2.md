# Debrief Report — gen002_explore_2

**Agent:** explore_2, Generation 2
**Directive:** Track B radical exploration — no BLIS tiling, no packing. Transposed/column-major computation with output-stationary accumulation.

---

## Solution Scores

| File   | Fitness (µs) | Valid | small (µs) | medium (µs) | large (µs) | Description |
|--------|-------------|-------|-----------|------------|-----------|-------------|
| sol01  | 207.32      | ✓     | 5.71      | 287.77     | 5421.37   | jc-outer, 8-row, int16, B_reg[128] stack |
| sol02  | 318.96      | ✓     | 8.32      | 618.11     | 6310.98   | template<KB> + always_inline, int8, switch |
| sol03  | 200.38      | ✓     | 5.75      | 270.06     | 5185.88   | named b0..b6 zmm vars, k<=7 fast path |
| **sol04**  | **182.31** | ✓  | **3.66**  | 281.17     | 5887.91   | ic-outer, jc-inner, streaming NT stores |

**Current population best:** 148.18 µs (gen001/explore_1/sol10)
**Best this session:** 182.31 µs (sol04) — 24% worse than population best.

---

## What I tried

### Approach: No-packing, direct B access (all 4 solutions)
All solutions share the same core idea: eliminate pack_A and pack_B entirely. The B panel
(k_bytes zmm registers) is loaded directly from B memory and reused across row batches.

The hypothesis was that packing overhead is large enough to eliminate. **This was wrong.**
The BLIS packing cost (reading 448KB of B once into L1) is ~2 µs. The benefit — L1-speed
access to Bp in the micro-kernel vs L2-speed direct B access — dominates.

**Loop order experiments:**
- **jc-outer, ic-inner (sol01, sol02, sol03):** B loaded once per 64-col block, reused for
  all n/8 row batches. Minimal B traffic (448KB total). But C writes are scattered (rows
  256KB apart), causing write-allocate overhead.
- **ic-outer, jc-inner (sol04):** Sequential C writes along each row; enables streaming
  NT stores. B is re-read 32 times (fits in L2). Achieved best small (3.66 µs) but
  large degraded (5887 µs) — B re-reads likely hurt more than expected.

**Register allocation experiments:**
- B_reg[128] (sol01): too large for zmm registers, compiler spills to stack
- template<KB> + always_inline (sol02): I-cache bloat from 3 inlined switch branches
- Named b0..b6 vars (sol03): best register allocation, slight improvement over sol01

---

## Answers to debrief questions

### 1. What did you try?
See table above. Four variations on no-packing direct-B-access approach, varying:
loop order (jc-outer vs ic-outer), accumulator width (int8 vs int16), B-register
strategy (array vs template vs named vars), store type (regular vs streaming NT).

### 2. What information did I lack?
- Whether the benchmark harness allocates C with 64-byte alignment (critical for streaming stores)
- Per-phase timing breakdown (pack_B vs micro-kernel vs store) in the current best
- Hardware counter data: is large actually bandwidth-bound or compute-bound?
- Whether `_mm512_stream_si512` is firing (alignment check might always fail)

### 3. What given facts might be wrong?
- The claim that large is "memory-bandwidth-bound" needs verification. If C write
  bandwidth floor is 800 µs but actual time is 3176 µs, something else is happening.
  The write-allocate theory (2x DRAM traffic) explains 1600 µs, not 3176 µs.
- fact_003 (Tiger Lake no downclocking): appears correct, no anomalies seen.

### 4. Was State of Affairs accurate?
Yes. idea_013 ("no-packing direct kernel") was correctly listed as untested — now
confirmed slower than BLIS. The streaming-stores idea (idea_006, conf 0.5) is real
but alignment constraints make it hard to exploit reliably.

### 5. What would I do differently?
- Not pursue the no-packing approach — packing cost is negligible, L1 reuse benefit is real.
- Instead: keep BLIS packing, add streaming NT stores on top (bigger win).
- Or: try the vpshufb 4-bit LUT approach which changes the compute kernel entirely.

### 6. Specific experiments to run
1. **Streaming stores on BLIS best**: take population/best.py, replace `_mm512_storeu_si512`
   with `_mm512_stream_si512` (with runtime alignment check). If C is aligned, expect
   ~1.5-2x speedup on large benchmark.
2. **vpshufb LUT kernel**: precompute 16-entry nibble LUTs for each row×k-level pair,
   use vpshufb to replace ternarylogic+2popcnt+sub. Measure throughput vs current.
3. **perf stat on best solution**: `perf stat -e cache-misses,L1-dcache-load-misses,mem-stores`
   to confirm memory vs compute bottleneck hypothesis.
4. **Aligned C allocation**: modify validate.py to use posix_memalign(64) for C and
   measure impact of streaming stores.

### 7. What surprised me?
- sol04 (ic-outer) achieved **small=3.66 µs** — beating population best (4.49 µs) on the
  small benchmark. This suggests ic-outer + streaming stores genuinely helps for small.
  For small C (128KB fits in L2), streaming stores bypass L2 and might hurt; the small
  improvement is puzzling. Perhaps it's sequential prefetcher behavior.
- sol02 (template+always_inline) was WORSE than the large B_reg[128] array (318 vs 207 µs).
  Three inlined code paths created more I-cache pressure than one general path with stack spills.
- The large benchmark degraded for ALL no-packing approaches. Even the best no-packing
  solution (sol03, 5185 µs) is 63% worse than BLIS (3176 µs). The packed B panel in L1
  is crucial for large-benchmark throughput.

### 8. Helper tools feedback
Did not use any helpers from problem/helpers/. None were relevant to this C++ kernel work.
A helper that would save significant time: `helpers/perf_profile.py` — a wrapper around
`perf stat` that runs the benchmark and returns hardware counter data (cache misses,
bandwidth utilization) to inform optimization decisions.

### 9. Time budget
Did not have enough time. The approach investigation consumed most turns debugging the
no-packing hypothesis. With more time, I would have:
1. Tried vpshufb LUT approach (most promising unexplored direction)
2. Tried adding streaming stores to population best without changing pack structure
3. Properly profiled the large benchmark to understand bandwidth vs compute split

---

## Summary for future agents

The no-packing approach is a dead end for this problem. BLIS packing is cheap and
provides essential L1-speed B access. The best unexplored directions are:
1. **streaming NT stores on top of BLIS** (sol04 showed small=3.66 µs improvement)
2. **vpshufb nibble-LUT kernel** replacing ternarylogic+popcnt compute
3. **hardware profiling** to confirm bandwidth vs compute bottleneck before investing more

Best solution this session: **sol04** at 182.31 µs (beats previous best on small benchmark
at 3.66 µs but regresses on large/medium).
