## Current Population Status
No solutions evaluated yet. Baseline reference: V14opt ~770 µs (geomean). Target: 477 µs.

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/description.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/constraints.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_001.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_002.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_003.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_004.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_005.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_006.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_007.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_008.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_009.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_001.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_002.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_003.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_004.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_005.md`
- `/home/sasha/Desktop/project_alpha/fast-conv/gemm/V14opt.cpp`
- `/home/sasha/Desktop/project_alpha/fast-conv/gemm/final.cpp`
- `/home/sasha/Desktop/project_alpha/fast-conv/gemm/micro_kernel.cpp`
- `/home/sasha/Desktop/project_alpha/fast-conv/gemm/baseline.cpp`

## Directive

**This is a Track B research mission. Survey the binary/ternary GEMM optimization landscape and
find approaches the system has never tried.**

Your deliverables are a structured findings report with concrete, actionable optimization strategies.
Focus on these research questions:

### Q1: Memory access pattern optimization for huge m
The large benchmark has m=65536 with only 128 rows — the output matrix is 32MB. What are the
best known techniques for GEMM-like operations where one dimension is vastly larger than the
other? Investigate:
- Column-panel traversal orders (JC loop variants)
- Cache-oblivious tiling for asymmetric matrices
- Prefetching strategies (`_mm_prefetch` with `_MM_HINT_T0`/`T1`/`NTA`)
- Write-combining / streaming store patterns

### Q2: Alternative arithmetic formulations
The current approach uses `(pos|b) & (neg|~b)` for the binary-ternary product. Are there
more efficient bitwise formulations? Investigate:
- XOR-based formulations (XOR counts mismatches, which relates to the dot product)
- Using `vpternlogd` (AVX-512 ternary logic, 1 instruction for any 3-input boolean function)
  to compute the pos/neg contributions in fewer instructions
- Whether the VNNI `vpdpbusd` instruction can be used with clever data encoding
- Karatsuba-like tricks for reducing operation count

### Q3: Micro-architectural optimization for Tiger Lake
- Instruction scheduling to avoid port 5 contention (popcount and shuffle both use port 5)
- Register pressure analysis for different µkernel shapes (4×64, 8×64, 4×128)
- Whether software prefetching helps or hurts on Tiger Lake's hardware prefetcher
- Impact of memory alignment on 512-bit loads (64-byte alignment vs unaligned)

### Q4: Non-BLIS tiling strategies
- Is the 5-loop BLIS structure optimal for this problem shape? With k_bytes ≤ 7, the inner
  dimension is trivial. Maybe a simpler 2-level tiling (just over m and n) is better.
- Block-panel or panel-panel multiplication patterns
- What do production binary neural network inference engines (BitNet, XNOR-Net) use?

For each finding, provide: (a) the technique, (b) estimated speedup potential, (c) implementation
difficulty, (d) which benchmark sizes it would most help.
