## Current Population Status
No solutions evaluated yet. Baseline reference: V14opt ~770 µs (geomean). Target: 477 µs.

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/description.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/constraints.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/initial_programs/optimize.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_003.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_005.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_006.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_009.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_003.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_004.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_005.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/README.md`
- `/home/sasha/Desktop/project_alpha/fast-conv/gemm/V14opt.cpp`
- `/home/sasha/Desktop/project_alpha/fast-conv/gemm/baseline.cpp`
- `/home/sasha/Desktop/project_alpha/fast-conv/gemm/micro_kernel.cpp`

## Directive

**Primary direction: VNNI-based reformulation + streaming stores + wider micro-kernel (8x64).**

This is a fundamentally different approach from explore_1. Instead of using popcount for the
binary-ternary multiply, try to reformulate the computation to use VNNI instructions:

1. **VNNI reformulation (`_mm512_dpbusd_epi32`)**: The binary-ternary product can potentially
   be expressed as an int8 dot-product. Consider encoding: ternary values as {255, 0, 1}
   (for {-1, 0, +1}) and binary values as {255, 1} (for {-1, +1}), then using VNNI unsigned×signed
   dot-product accumulate. Or find another encoding that maps the operation to VNNI semantics.
   VNNI has 5c latency but 1c throughput — pipeline it across multiple rows.

2. **Wider micro-kernel (8x64)**: With 32 zmm registers, try processing 8 rows of A × 64 columns
   of B simultaneously. That's 8 accumulators + B data + temporaries = ~12-16 registers, well
   within the 32-register budget. This halves µkernel call overhead.

3. **Streaming stores** for the large benchmark (m=65536): output rows are 256KB, far exceeding
   L2. Use `_mm512_stream_si512` to bypass cache on stores, freeing cache for B-panel data.

4. **Skip KC tiling**: Since k_bytes ≤ 7 always, the KC loop always has 1 iteration. Eliminate
   the KC dimension from the tiling entirely. Just tile over m (NC) and n (MC).

If VNNI reformulation proves too difficult to get correct, fall back to AVX-512 popcount but
with the wider 8x64 µkernel + streaming stores. The key differentiator from explore_1 is
the wider µkernel and the streaming store optimization for large m.

**Off-limits:** Do NOT use the 4x64 micro-kernel shape with standard popcount (that's explore_1's
territory). Your µkernel must be either VNNI-based or 8x64 wide.

Read the detail_file after each evaluation to see which benchmark sizes benefit most.
