## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/population/best.py` → 148.18 µs (geomean)
Per-size breakdown: small=4.49 µs, medium=228.26 µs, large=3176.31 µs
**TARGET: 24 µs** (~6x improvement over current best needed)

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/problem/description.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/problem/constraints.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/clusters/cluster_001.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/clusters/cluster_002.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/facts/fact_003.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/facts/fact_004.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/facts/fact_005.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/history/coverage_matrix.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/history/solution_idea_map.md`

## Directive

**This is a Track B research mission. Find approaches the system has never tried. Read the coverage matrix and dead ends to know what has been explored. Look for ideas from adjacent fields, recent papers, or mathematical theory that could apply.**

The system has achieved 148 µs with BLIS-style AVX-512 tiling (4×64 micro-kernel, pack A/B, vpternlogd boolean, int8/16 accumulate, skip memset). The target is 24 µs — about 6x faster. All 14 solutions in gen 1 follow the same BLIS template. **Incremental refinement of this template will not reach 24 µs.**

**Research questions (in priority order):**

1. **Theoretical lower bound analysis.** For each benchmark size, compute the minimum possible time based on:
   - Memory bandwidth: how many bytes must be read/written? What is the achievable bandwidth on Tiger Lake for each cache level?
   - Compute throughput: how many operations are needed? What is the peak throughput for vpternlogd + vpopcntb?
   - Is 24 µs theoretically achievable or are we hitting a physical limit? If large benchmark writes 32MB to DRAM at ~30GB/s, that's ~1000 µs minimum — can this be reduced?

2. **How do production BNN inference engines achieve their speed?** Investigate:
   - BitNet.cpp (Microsoft) — what kernel strategy do they use for ternary weight multiplication?
   - XNOR-Net / BMXNet inference kernels
   - TVM/Halide auto-tuned binary convolution kernels
   - How do they handle the bit-packed → int32 accumulation pipeline at scale?

3. **Alternative algorithmic approaches for tiny-k GEMM:**
   - With k only 2-7 bytes, are there approaches that avoid the standard GEMM pattern entirely?
   - Could we use lookup tables: precompute all 256 possible results for each (pos_byte, neg_byte) pair, then for each B column just do table lookups + accumulate?
   - Could we process the computation in a transposed order (column-major, all rows simultaneously)?
   - Is there a way to batch the output writes to be more cache-friendly?

4. **Memory bandwidth optimization techniques:**
   - Non-temporal stores for large output: what's the actual achievable NT store bandwidth on Tiger Lake?
   - Write-combining buffers: how many does Tiger Lake have?
   - Can we reduce output precision (compute in int16 and convert to int32 only at store time)?
   - Output tiling: is there a write order that's more cache-friendly for huge m?

5. **Instruction scheduling and port utilization on Willow Cove:**
   - Which ports execute vpternlogd, vpopcntb, vpmovzxbd?
   - What is the theoretical peak throughput for the critical instruction sequence?
   - Are there instruction combinations that achieve better port utilization?

**Deliverables:**

Write a findings report (`output/report.md`) with:
1. Theoretical minimum times for each benchmark size (with derivation)
2. At least 3 concrete new approach ideas with estimated performance
3. Port utilization analysis for the critical instruction sequence
4. Specific actionable recommendations for gen 3 agents

**What has been tried (do not repeat):**
- BLIS-style tiling with various NC values (debunked: NC=512; working: NC=256)
- AVX-512 popcount replacing LUT (established, all solutions use it)
- VNNI (debunked — bit-packed format incompatible)
- Template k-specialization (debunked — I-cache pressure)
- Aligned temp C + memcpy (debunked — memcpy too expensive)
