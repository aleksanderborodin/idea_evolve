---
generation: 1
best_score: 148.18
trajectory: improving
last_updated_gen: 1
---

# State of Affairs — Generation 1

## Current Standing

Best score: **148.18 µs** (explore_1/sol10), a 5.20x speedup over the 770 µs AVX2 baseline. Achieved in generation 1 with 14 valid solutions from 2 productive agents (explore_1: 10 solutions, full_1: 4). One agent (explore_2) timed out with zero solutions — 25% of agent capacity was lost to over-reading before coding. **NOTE: The target has changed from 477 µs to 24 µs (geometric median). The old target was easy — 24 µs requires ~32x speedup over baseline and ~6x improvement over current best. Incremental changes will not suffice; fundamentally new strategies are needed.** Also: scoring now uses median (not mean) for stability.

## What Works

**Established (high confidence, use in all new solutions):**
- **AVX-512 popcount** (idea_001, conf 0.95) — `_mm512_popcnt_epi8` replaces 6-instruction LUT. Foundational; all 14 solutions use it.
- **Deferred widening** (idea_004, conf 0.95) — accumulate in int8/int16, widen to int32 once after k-loop. int32-in-loop is 1.5-2x slower (full_1/sol01 vs sol02).
- **Vectorized pack_B** (idea_007, conf 0.85) — zmm load/store for 64-byte B chunks. Pack_B was a bigger bottleneck than the micro-kernel for medium/large.
- **Skip memset** (idea_010, conf 0.95) — direct stores eliminate 32 MB zeroing on large. Single biggest optimization: 1.72x speedup alone (sol07→sol08).
- **Skip KC tiling** (idea_008, conf 0.9) — k_bytes ≤ 7, entire k fits in registers. Universal.

**Confirmed patterns:**
- Memset dominates large benchmark cost (pattern_001). Memory bandwidth, not compute, is the large-size bottleneck.
- NC=256 outperforms NC=512 consistently (pattern_002). Root cause unknown.
- Template specialization causes I-cache regressions (pattern_003). Use `#pragma GCC unroll` instead.

## Current Frontier

**Active ideas under investigation:**
- vpternlogd fused logic (idea_011, conf 0.6) — used by best solution but standalone impact not isolated.
- Stack-allocated buffers (idea_012, conf 0.5) — ~13% improvement over malloc, single data point.
- Streaming stores (idea_006, conf 0.5) — ~6% estimated benefit on large, hard to isolate.
- NC tuning (idea_005, conf 0.5) — only NC=256 and NC=512 tested. NC=128, 192 unexplored.

**Disputed (needs more evidence):**
- 8-row kernel (idea_009, conf 0.4) — failed with int16 accumulators (register pressure). Untested with int8 accumulation, which halves register usage per row.
- Full k-loop unrolling (idea_002, conf 0.4) — pragma unroll helps, template specialization hurts.

## Coverage Map

Most productive combination: **idea_001 + idea_004 + idea_007 + idea_010** (4 trials, best 148.18 µs, avg 169.38 µs).

**Unexplored high-priority:**
- No-packing direct kernel (idea_013) — untested, potentially eliminates pack_B overhead entirely
- 8-row kernel + int8 accumulation (idea_009 + idea_004 int8 variant)
- NC sweep below 256 (NC=128, 192)
- vpternlogd standalone impact isolation
- Software prefetching for B panels

## Dead Ends

- **VNNI** (idea_003, debunked) — bit-packed format incompatible with integer dot-product. Fundamental mismatch.
- **Template k-specialization** — I-cache pressure from multiple kernel copies. Use pragma unroll instead.
- **Aligned temp C + memcpy** — memcpy overhead dominates (explore_1/sol05: 964 µs regression).

## Open Questions

1. **Why does NC=512 regress?** Most-cited open question across all agent reports. Needs `perf stat` with cache/TLB counters. No solution has done hardware profiling.
2. **Is the large benchmark memory-bandwidth-bound?** With 32 MB output at ~30 GB/s, theoretical minimum write time is ~1000 µs. Current large time is 3176 µs — how close is this to the bandwidth ceiling?
3. **Assembly quality:** No solution has inspected compiler output. Register allocation, instruction scheduling, and missed optimizations are unknown.
4. **vpternlogd truth table convention:** Research derived 0xCA/0xAC, explore_1 used 0xD8/0xE4. Both correct (different operand order). Needs standardization to prevent future bugs.
5. **fact_004 instruction latencies:** `vpmovzxbd` 3c latency and other values are user-provided and unverified on this specific Tiger Lake machine.
6. **Per-phase timing breakdown:** No solution measured time in pack_A vs pack_B vs micro-kernel vs stores. This would reveal where remaining optimization effort is best spent.
