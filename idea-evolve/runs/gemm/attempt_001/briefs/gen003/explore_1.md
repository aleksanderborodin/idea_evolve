## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/population/best.py` → fitness = 147.26 µs (row-streaming architecture)
Second best: `/home/sasha/Desktop/project_alpha/idea-evolve/population/top/rank02_165.59.py` → fitness = 165.59 µs
Best per-size breakdown: small=3.69 µs, medium=225.55 µs, large=3841.72 µs
Target: 24 µs (geometric mean of 3 per-size median times, lower is better)

**SCORING METRIC CONFIRMED:** Fitness = geometric mean = `(small × medium × large)^(1/3)`. All three sizes matter equally.

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/state_of_affairs.md` — Current strategic overview
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/clusters/cluster_001.md` — AVX-512 micro-kernel compute
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/clusters/cluster_002.md` — Memory & tiling optimization
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/clusters/cluster_003.md` — Alternative architectures (row-streaming)
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/ideas/active/idea_014.md` — Row-streaming architecture
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/ideas/active/idea_015.md` — Size-adaptive NT stores
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/ideas/active/idea_016.md` — 8-row int8 kernel
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/ideas/active/fact_006.md` — C alignment constraint
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/ideas/active/fact_007.md` — Measured DRAM bandwidth
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/experiments/gen002/experimentator_1/observations.md` — Phase timing data, experimental results
- `/home/sasha/Desktop/project_alpha/idea-evolve/population/gen002/explore_1/sol01.py` — Row-streaming best (read for understanding, but build your own)
- `/home/sasha/Desktop/project_alpha/idea-evolve/problem/description.md` — Problem definition and CPU details
- `/home/sasha/Desktop/project_alpha/idea-evolve/problem/constraints.md` — Hard/soft constraints
- `/home/sasha/Desktop/project_alpha/idea-evolve/history/coverage_matrix.md` — What's been tried
- `/home/sasha/Desktop/project_alpha/idea-evolve/feedback/experiment_suggestions/gen002.md` — Prioritized experiments (EXP-2 through EXP-4)

## Directive

**Build a complete full-stack solution FROM SCRATCH** that combines all three major optimizations identified in gen 2 but never implemented together:

1. **Row-streaming architecture** (idea_014): Process rows of A sequentially, sweep across all m columns of B in 64-byte chunks. No BLIS packing.

2. **8-row int8 kernel** (idea_016): Process 8 rows of A simultaneously per B-panel sweep. Accumulate in int8 (safe for k_bytes ≤ 15). Use `_mm512_add_epi8` (1 instruction vs 2 for int16). Flush to int32 every 15 k-iterations. Register budget: 8 acc + 1 B + 16 A = 25 zmm.

3. **Size-adaptive NT stores** (idea_015): For large benchmark (n*m*4 > 8MB), allocate aligned buffer with `std::aligned_alloc(64, ...)`, compute with `_mm512_stream_si512`, `_mm_sfence()`, then `memcpy` back. For small/medium, regular `_mm512_storeu_si512`.

4. **Per-size tuning:**
   - Small (n=32, m=1024, k_bytes=2): B = 2KB fits in L1. Everything fits in registers. Just iterate.
   - Medium (n=64, m=16384, k_bytes=4): B = 64KB fits in L2. Regular stores. Process 8 rows at a time.
   - Large (n=128, m=65536, k_bytes=7): B = 448KB. NT stores via aligned buffer. Consider B micro-packing per 64-col chunk for L1 reuse across 8 rows.

**Target: 40-70 µs geomean.** The physics floor is ~29 µs (research_1 calculation). This requires all three optimizations working together.

### Key implementation details
- vpternlogd truth tables: 0xD8 for pos_contrib, 0xE4 for neg_contrib (verified in gen 2)
- int8 overflow: max ±8 per k-byte step. For k_bytes ≤ 15: max ±120, safe. Flush at 15.
- NT stores need `_mm_sfence()` before memcpy
- Correctness test uses k=256 (k_bytes=32) — handle int8 overflow with periodic flush every 15 iterations
- Function signature: `void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k)`
- Must zero C (or aligned buffer) before accumulating, unless using direct stores

### Build incrementally
1. First: basic 1-row row-streaming (get correctness right)
2. Then: add 8-row kernel
3. Then: add NT stores for large
4. Then: tune and combine

**Evaluate after EACH step.** Run: `python3 evaluate.py output/solNN.py`
Read the detail file for per-size breakdown. Update `# fitness:` header.
