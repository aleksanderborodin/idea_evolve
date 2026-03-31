# Explore Agent 1 — Generation 1 Debrief Report

## Solution Scores

| File   | Fitness (µs) | is_valid | Small (µs) | Medium (µs) | Large (µs) | vs Baseline | Notes |
|--------|-------------|----------|-----------|------------|-----------|-------------|-------|
| sol01  | 654.75      | 1        | 13.27     | 1664.78    | 12705.35  | 0.85x       | NC=512 regressed medium |
| sol02  | 400.68      | 1        | 11.91     | 713.96     | 7563.31   | 1.92x       | Fixed ternarylogic, NC=256 |
| sol03  | 493.42      | 1        | 14.09     | 868.62     | 9817.80   | 1.56x       | 8-row kernel, register pressure |
| sol04  | 381.32      | 1        | 10.56     | 656.54     | 7997.51   | 2.02x       | Direct store (no load) |
| sol05  | 964.47      | 1        | 31.33     | 1180.37    | 24262.05  | 0.80x       | FAIL: memcpy killed large |
| sol06  | 465.65      | 1        | 14.85     | 788.70     | 8621.99   | 1.65x       | NC=512 direct store, still worse |
| sol07  | 306.60      | 1        | 8.42      | 484.19     | 7073.67   | 2.51x       | Vectorized pack_B (zmm) |
| sol08  | 178.28      | 1        | 4.79      | 321.90     | 3674.79   | 4.32x       | Removed memset |
| sol09  | 171.04      | 1        | 5.78      | 239.31     | 3617.45   | 4.50x       | thread_local buffers (TLS hurt small) |
| **sol10** | **148.18** | **1** | **4.49** | **228.26** | **3176.31** | **5.20x** | **Stack buffers, best result** |

Baseline (V14opt): 770 µs geomean. Target: 477 µs. **sol10 achieves 148.18 µs = 19.2% of baseline.**

## What I Tried

### 1. What did you try?
- sol01: AVX-512 with `_mm512_popcnt_epi8`, 4×64 micro-kernel, int16 accum, NC=512
- sol02: Fixed ternarylogic truth tables (0xD8/0xE4), NC=256 — beat target
- sol03: 8-row × 64-col micro-kernel — register pressure hurt it
- sol04: Direct store (no C load-add) — eliminates read-for-ownership
- sol05: Aligned temp C buffer + streaming stores + memcpy — memcpy too expensive
- sol06: NC=512 with direct stores — still worse than NC=256
- sol07: Vectorized pack_B with zmm load+store — major speedup
- sol08: Removed memset (redundant since harness pre-zeros C, direct store overwrites)
- sol09: thread_local buffers + k-loop unroll pragma
- sol10: alignas(64) stack buffers — best overall

### 2. What information did I lack?
- Why NC=512 is consistently slower than NC=256 despite the same number of micro-kernel calls.
  This deserves further investigation (cache line conflict? TLB pressure? B panel alignment?).
- Whether the large size (3176 µs) is truly DRAM-bound or if there's more compute headroom.
- Exact register allocation from the compiler — would help tuning the inner loop.

### 3. What given facts might be wrong?
- fact_004 says `vpdpbusd` has 1c throughput but port 0 with 5c latency. The BITALG popcount
  path seems to still outperform VNNI-based approaches based on brief guidance, but I didn't test.
- The directional "no downclocking" for Tiger Lake AVX-512 (fact_003) appears confirmed by results.

### 4. Was the State of Affairs accurate?
The population had no solutions yet (gen 1). The initial ideas (001, 002, 004, 008) were all
directionally correct and I implemented all of them. The fact files were accurate.

### 5. What would I do differently?
- Start with vectorized pack_B from the beginning — it was by far the biggest win.
- Remove memset earlier — also huge.
- Test NC=128 as well (might be even better for small).

### 6. Specific experiments to run
- Template specialization: `template<int K>` versions for k_bytes=2,4,7 with compile-time unrolling.
- Check if NC=128 improves small or medium (reduces packing overhead further).
- Try 6-row × 64-col micro-kernel (between the 4-row sweet spot and 8-row overload).
- Non-temporal stores: allocate aligned output buffer in caller or align C in the harness.
- Check if `__builtin_prefetch` on next B panel chunk helps large.

### 7. What surprised me?
- memset was costing ~3.5 ms on large — nearly half the total time! Never expected zeroing
  to dominate like that for a compute-bound problem.
- pack_B was a bigger bottleneck than the micro-kernel itself for medium/large.
- NC=512 was consistently slower than NC=256 even with vectorized packing and direct stores.
  This is counterintuitive and deserves investigation.
- The sol10 result (148 µs = 5.2x speedup) far exceeded the target of 477 µs.

### 8. Helper tools feedback
Used `from helpers.core import compute_c` was not needed (C++ solution, not Python).
No helpers were relevant for this task. A useful helper would be: a C++ code template
that shows the packing layout conventions, saving agents from having to reverse-engineer it.

### 9. Time budget
Had enough time but it was tight. With more time I would:
1. Implement template specialization for k_bytes=2,4,7 (compile-time unrolled)
2. Test NC=128 vs NC=256 for small sizes
3. Investigate the NC=512 regression mystery
4. Try 6-row micro-kernel
