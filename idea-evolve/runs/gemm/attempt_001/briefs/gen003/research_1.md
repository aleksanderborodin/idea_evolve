## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/population/best.py` → fitness = 147.26 µs (row-streaming architecture)
Target: 24 µs (geometric mean of 3 per-size median times, lower is better)
Best per-size: small=3.69 µs, medium=225.55 µs, large=3841.72 µs

**Scoring Metric:** Fitness = `(small × medium × large)^(1/3)` — geometric mean. All sizes matter.

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/problem/description.md` — Problem definition, benchmark sizes, CPU details
- `/home/sasha/Desktop/project_alpha/idea-evolve/problem/constraints.md` — Constraints
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/state_of_affairs.md` — Current strategic overview
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/clusters/cluster_001.md` — Compute cluster
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/clusters/cluster_002.md` — Memory cluster
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/clusters/cluster_003.md` — Alternative architectures
- `/home/sasha/Desktop/project_alpha/idea-evolve/history/coverage_matrix.md` — What has and hasn't been tried
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/research/gen002/research_1/findings.md` — Previous research findings
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/experiments/gen002/experimentator_1/observations.md` — Measured phase timing, bandwidth, port pressure
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/ideas/active/fact_006.md` — C alignment constraint
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/ideas/active/fact_007.md` — Measured DRAM bandwidth

## Directive

**This is a Track B research mission. Find approaches the system has never tried. Read the coverage matrix and dead ends to know what has been tried. Look for ideas from adjacent fields, recent papers, or mathematical theory that could apply.**

### Research Questions (prioritized)

**Q1: How to get small benchmark below 1 µs?**
Current small: 3.69 µs for 32×1024 matrix (128 KB output). At this size, B = 2KB and A = 128 bytes — both fit in L1. The kernel computes 32×1024 = 32K output elements. Research_1 estimated 0.5-1 µs is achievable. How?
- Is the loop overhead (n=32 outer iterations) dominant?
- Can we process all 32 rows simultaneously (32 zmm accumulators, k_bytes=2)?
- What is the theoretical minimum for this computation volume on Tiger Lake?

**Q2: Alternative output strategies for large benchmark**
Current large: 3842 µs for 128×65536 (32 MB output). NT stores can halve this to ~2000 µs. But geomean(0.5, 80, 2000) = 43 µs — still above 24 µs target. What else?
- Can we avoid writing full int32 output? (e.g., int16 output if values fit, with runtime check)
- Compressed output formats?
- Memory-mapped I/O tricks?
- Can the memcpy from aligned buffer be avoided entirely? (e.g., if C is page-aligned by chance)
- What bandwidth does `memset` + `_mm512_stream_si512` actually achieve on Tiger Lake?

**Q3: SIMD tricks for this specific problem**
The binary-ternary structure is very constrained (A ∈ {-1,0,+1}, B ∈ {-1,+1}). Are there tricks specific to this structure?
- Can VNNI be used despite the bit-packed format? (idea_003 was debunked, but was the analysis correct?)
- Can we repack A or B into a format that makes VNNI usable?
- `_mm512_dpbusd_epi32` does 4×uint8·int8 dot products — could B be repacked as int8?
- Any use for `_mm512_gf2p8affine_epi64_epi8` (GFNI)?

**Q4: What do the best BNN/binary neural network inference engines do?**
Search for:
- daBNN, BMXNet, XNOR-Net inference kernels
- How do production BNN frameworks handle binary-ternary GEMM on x86?
- Any published kernel benchmarks for Tiger Lake / Ice Lake?

**Q5: Instruction-level optimization for Tiger Lake specifically**
- What is the actual IPC achievable for this workload on Willow Cove core?
- Does Tiger Lake have micro-op fusion opportunities we're missing?
- Loop buffer / LSD behavior for unrolled kernels of this size?

### Deliverables
Write `output/findings.md` with:
1. For each question: what you found, confidence level, actionable next steps
2. Concrete code sketches or pseudocode for any promising new approach
3. Specific recommendations for gen-4 agents

Write `output/report.md` as your debrief.

### What NOT to do
- Do NOT write solution code or run evaluate.py — this is research only
- Do NOT rehash approaches already in the coverage matrix — find NEW ones
- Do NOT spend more than 20% of your time reading existing code; focus on external research
