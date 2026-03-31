# Observations — gen001_explore_2

## Summary

No solutions were produced in this session. The agent (this session) was interrupted before any code was written. The session began reading reference files (description.md, constraints.md, initial_programs/optimize.py, V14opt.cpp, micro_kernel.cpp, idea files, fact files) to understand the problem and plan the implementation. Before any sol01.py was written, the session was stopped.

## What Was Planned

**Primary approach: AVX-512 8x64 micro-kernel with streaming stores**

Key design decisions formed from reading the reference code:

1. **Wider micro-kernel (8 rows × 64 cols)**: The baseline uses 4×32 (AVX2). Upgrading to 8×64 with AVX-512 zmm registers would:
   - Double the B-columns processed per micro-kernel call (64 vs 32), halving call overhead
   - Process 8 rows instead of 4, reducing A-broadcast overhead
   - Use zmm accumulators: 8 accumulators (one per row) fits easily in 32 zmm registers

2. **AVX-512 BITALG popcount**: Replace the 6-instruction LUT-based popcount with `_mm512_popcnt_epi8` (1-cycle throughput). For 64 columns of B (1 zmm), one instruction replaces 6.

3. **Streaming stores for large m**: For m=65536, output rows are 256KB. Use `_mm512_stream_si512` to bypass cache. Requires the output buffer to be 64-byte aligned.

4. **Skip KC tiling**: k_bytes ≤ 7 always, so the KC loop always runs once. Eliminate KC dimension from tiling entirely.

5. **VNNI reformulation** (lower priority): `_mm512_dpbusd_epi32` could potentially encode the ternary-binary product as int8 dot-products. Encoding: ternary {-1,0,+1} → int8 {-1,0,1}, binary {-1,+1} → uint8 {255,1} or similar. This is theoretically attractive (1-cycle throughput, 5c latency vs popcount's 1c/1c) but the encoding mapping needs careful verification for correctness.

## What Was NOT Done

- No C++ code was written
- No evaluations were run
- No scores were obtained

## Scores

| Solution | Fitness | Notes |
|----------|---------|-------|
| (none)   | —       | No solutions produced |

## Recommendations for Next Agent

1. Implement the 8×64 AVX-512 micro-kernel with `_mm512_popcnt_epi8`. This is the most mechanically straightforward improvement over the baseline.
2. Use `_mm512_stream_si512` for storing C when m is large. Add `_mm_sfence()` after the j-loop.
3. Try tile sizes: MC=128, NC=4096 (or NC=m for small enough m). With k_bytes ≤ 7 always, KC=k_bytes exactly (no KC tiling needed).
4. The B-packing step packs 64 columns at a time (instead of 32) — pack_B should write 64 bytes per k-step.
5. For VNNI: the formula `pos_contrib - neg_contrib` where pos = popcount((a_pos|b) & (a_neg|~b)) and neg = popcount((a_pos|~b) & (a_neg|b)) maps cleanly to signed arithmetic. Encoding A rows as int8 (+1/-1/0) and B bytes as uint8 (each bit = ±1) is non-trivial because VNNI works on byte-level dot products, not bit-level.
