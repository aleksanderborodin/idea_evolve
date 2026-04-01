## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/population/best.py` → fitness = 147.26 µs (row-streaming architecture)
Second best: `/home/sasha/Desktop/project_alpha/idea-evolve/population/top/rank02_165.59.py` → fitness = 165.59 µs
Best per-size breakdown: small=3.69 µs, medium=225.55 µs, large=3841.72 µs
Target: 24 µs (geometric mean of 3 per-size median times, lower is better)

**IMPORTANT — Scoring Metric Resolved:** Fitness = geometric mean = `(small × medium × large)^(1/3)`. All three sizes matter equally.

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/problem/description.md` — Problem definition, CPU details, key intrinsics
- `/home/sasha/Desktop/project_alpha/idea-evolve/problem/constraints.md` — Hard/soft constraints
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/ideas/active/idea_018.md` — vpshufb LUT kernel (never tested)
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/clusters/cluster_001.md` — Current micro-kernel compute approaches
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/experiments/gen002/experimentator_1/observations.md` — Port pressure analysis (port 5 bottleneck)
- `/home/sasha/Desktop/project_alpha/idea-evolve/history/coverage_matrix.md` — What has been tried (idea_018 = "never tried")
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/research/gen002/research_1/findings.md` — Research findings including LUT analysis
- `../fast-conv/gemm/baseline.cpp` — Naive reference (gemmV0) for understanding data layout
- `../fast-conv/gemm/V14opt.cpp` — BLIS AVX2 reference (understand packing/kernel structure)

## Directive

**This is a Track B radical exploration. You must NOT use the ternarylogic + popcount compute path that all existing solutions use. You must NOT start from any existing solution. Build from scratch.**

### Your approach: vpshufb Nibble-LUT Kernel (idea_018)

Replace the current `vpternlogd + vpopcntb` compute path with a precomputed lookup table using `_mm512_shuffle_epi8` (vpshufb):

**Core idea:** For each A element (ternary: -1, 0, +1) and each nibble (4 bits) of B, there are only 16 possible popcount-diff results. Precompute these 16 values into a LUT and use vpshufb to look them up.

**Algorithm sketch:**
1. For each A row, precompute LUTs for each k-byte position:
   - Given `a_pos` bit and `a_neg` bit, compute the 16 possible contributions for each B nibble pattern (0x0 through 0xF)
   - Store as `__m512i lut_lo, lut_hi` per k-byte (low nibble and high nibble LUTs)
2. For each B column chunk (64 columns):
   - Load B bytes: `vb = _mm512_loadu_si512(B + t*m + j)`
   - Extract low nibbles: `lo = vb & 0x0F`
   - Extract high nibbles: `hi = (vb >> 4) & 0x0F`  (use `_mm512_srli_epi16` + mask)
   - Look up: `contrib = vpshufb(lut_lo, lo) + vpshufb(lut_hi, hi)`
   - Accumulate across k-bytes

**Why this might work:**
- `vpshufb` runs on port 0/1, NOT port 5. Current approach has 20-28 uops on port 5 per k-iteration (vpbroadcastb, vpmovsxbw, vextracti32x8 all port-5-only). The LUT approach completely eliminates port 5 pressure.
- Each vpshufb processes 64 B elements at once (same as current)
- LUT precomputation for each A row is O(k_bytes × 16) = tiny

**Potential issues:**
- LUT construction overhead per row (mitigate: precompute for all rows once)
- 2 vpshufb instructions per k-byte per row (vs ~5 compute instructions in current approach) — may be slower per element
- Nibble extraction adds instructions (`_mm512_and_si512`, `_mm512_srli_epi16`)

**Even if this is slower than the popcount approach, it provides critical information:** whether port 5 is actually the binding throughput constraint. If vpshufb is faster despite more total instructions, port 5 is confirmed as the bottleneck and future kernels should be designed around it.

### Implementation plan
1. Write a clean, correct implementation first (no optimizations)
2. Evaluate immediately for correctness
3. Optimize: unroll k-loop, try int8 accumulation, try NT stores for large
4. Compare per-size times with the popcount approach

### What NOT to do
- Do NOT use vpternlogd or vpopcntb — that's the existing approach
- Do NOT start from any existing solution file
- Do NOT use BLIS packing for the first variant (add it later if helpful)

### Evaluation
After each solution, run: `python3 evaluate.py output/solNN.py`
Read the detail file for per-size breakdown. Update `# fitness:` header.
