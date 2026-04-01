# Observations — Research Agent 1, Gen 3

## Solutions Produced

None. This was a pure research session. No solution code was written or evaluated.

## Research Conducted

1. **Read all context files**: description.md, state_of_affairs.md, cluster_001–003, coverage_matrix, gen002 research findings, experimentator observations, fact_006, fact_007, active ideas (014–019), patterns 007–008, bench harness source.

2. **Analyzed bench harness alignment**: Confirmed `std::vector<int>` gives 16-byte alignment (glibc). This means `_mm_stream_si128` (SSE 128-bit NT store) works without runtime alignment check, while `_mm512_stream_si512` may fault. This is the root cause of all previous NT store failures.

3. **Bandwidth ceiling analysis**: Using fact_007 measured data, derived theoretical minimums for each benchmark size. Concluded 24 µs geomean is physically impossible given medium (4 MB output, 220–230 µs floor) and large (32 MB output, 1350 µs floor with NT stores). Realistic target: 50–80 µs.

4. **Multi-threading analysis**: Identified that cgexec cgroup includes cores 0 AND 1. Pthreads from within gemmCandidate can use core 1. 2-thread NT stores could achieve 1.3–1.8× bandwidth scaling. Completely unexplored — not in coverage matrix.

5. **Template specialization analysis**: k_bytes ∈ {2, 4, 7} for benchmark sizes. Compile-time dispatch eliminates loop overhead and A-register stack spills for small. Key improvement for small.

6. **Column-outer kernel analysis**: Reduces B reads from 56 MB (repeated L3 reads) to 448 KB, but L3-resident B means savings are only ~278 µs. Strided C writes with NT stores are feasible but WCB-limited. Net benefit similar to row-outer + NT stores; not worth independent pursuit.

7. **vpshufb LUT analysis**: Port 5 already saturated; more port 5 ops would worsen performance.

## Key Score Data

No scores generated. Referencing existing population:
- Current best: 147.26 µs (row-streaming, gen002/explore_1/sol01)
- Per-size: small=3.69, medium=225.55, large=3841.72

## Recommended Priorities for Gen-3 Agents

1. **SSE 128-bit NT stores for large** (idea_015 + 128-bit fix): expected geomean ~105 µs
2. **Multi-threading with 2 cores** (NEW): expected geomean ~87 µs combined with NT stores
3. **k-template specialization for small**: expected small ~1.0–1.5 µs
4. **8-row int8 kernel** (idea_016): expected medium ~200 µs
