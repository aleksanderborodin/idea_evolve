# Generation 1 — Strategic Reasoning

## Situation Assessment

This is generation 1 (cold start). No solutions exist yet. The baseline is V14opt at ~770 µs
(geometric mean across 3 benchmark sizes). The target is 477 µs, requiring ~1.6x overall speedup.

The baseline uses AVX2 (256-bit) with BLIS 5-loop tiling and a 4×32 micro-kernel with LUT-based
popcount. The target CPU (Tiger Lake i5-1135G7) supports AVX-512 with hardware popcount
(BITALG), VNNI, and 32 zmm registers — none of which the baseline uses.

The most promising optimization axis is clear: **AVX-512 adoption**. The baseline leaves
substantial performance on the table by using AVX2.

## Agent Mix Rationale

**4 agents: 2 explore + 1 full + 1 research** (per cold-start rules).

### explore_1 — AVX-512 popcount + unrolled k-loop + int16 accumulation
The most straightforward upgrade path. Replace AVX2 LUT popcount with `_mm512_popcnt_epi8`
(1 instruction vs 6), widen to 64-byte operations, and fully unroll the tiny k-loop (2-7 bytes).
This should yield the most reliable speedup — the popcount replacement alone should be worth
~1.5x in the micro-kernel.

### explore_2 — VNNI reformulation + 8×64 µkernel + streaming stores
A fundamentally different approach. Instead of improving the popcount path, try to eliminate
popcount entirely by reformulating as a VNNI dot-product. Also explores wider micro-kernel
(8 rows instead of 4) and streaming stores for the large benchmark. This is higher risk but
potentially higher reward — VNNI has 1c throughput and the wider µkernel reduces call overhead.

### full_1 — Kitchen-sink AVX-512 solution
Combines the most promising ideas into a single well-engineered solution. Unlike the explores
which each focus on one axis, this agent tries to integrate everything: AVX-512 popcount,
re-tuned tile sizes, SIMD packing, streaming stores, unrolled k-loop. Expected to produce
the most competitive overall solution.

### research_1 — Domain survey
Surveys memory access patterns for asymmetric matrices, alternative arithmetic formulations
(vpternlogd, XOR-based), micro-architectural scheduling concerns, and non-BLIS tiling.
This generates actionable ideas for generation 2+ even if gen 1 solutions don't hit the target.

## Timeout Rationale

- **Explore agents (1800s):** No timing data exists. 30 minutes allows ~40+ write-evaluate
  cycles. These agents need time to iterate on correctness (AVX-512 intrinsics are tricky
  to get right, especially data encoding).
- **Full agent (1800s):** Same reasoning — integrating multiple optimizations requires
  careful iterative debugging.
- **Research agent (900s):** Pure investigation, no compilation/benchmarking loop needed.
  15 minutes is generous for reading files and writing findings.

## What I Deliberately Did NOT Do

- **No exploit/genetic agents:** Nothing to refine or crossover yet (cold start).
- **No experimentator:** No pipeline questions to answer yet. Helper tools aren't needed
  until agents identify recurring pain points.
- **No VNNI-only agent:** VNNI reformulation is risky (encoding correctness is hard), so
  it's bundled with a fallback (8×64 popcount µkernel) in explore_2 rather than given its
  own dedicated agent.

## Risks

1. **AVX-512 correctness:** The binary-ternary encoding is subtle. Off-by-one errors in
   bit interpretation will produce wrong results. Agents may spend most turns debugging
   correctness rather than optimizing performance.
2. **VNNI reformulation may be infeasible:** The unsigned×signed semantics of `vpdpbusd`
   may not map cleanly to the ternary {-1,0,+1} encoding. explore_2 has a fallback plan.
3. **Tile size tuning is empirical:** The "right" NC/MC values depend on the specific
   access patterns and can't be predicted analytically. Agents need enough turns to try
   multiple configurations.
