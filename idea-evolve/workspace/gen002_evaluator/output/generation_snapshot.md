# Generation 2 Snapshot

## Summary

**Best score this generation:** 147.26 µs (gen002/explore_1/sol01) — marginal improvement over gen001 best (148.18 µs)
**Best score overall:** 147.26 µs (gen002/explore_1/sol01)
**Target:** 24 µs (6.1x improvement still needed)
**Solutions produced:** 25 valid solutions (12 exploit_1, 8 explore_1, 4 explore_2, 1 experimentator_1)
**Invalid solutions:** 0
**Agents:** 5 active (exploit_1, explore_1, explore_2, research_1, experimentator_1)

## Score Distribution

| Agent | Solutions | Best (µs) | Worst (µs) | Median (µs) |
|-------|----------|-----------|-----------|-------------|
| exploit_1 | 12 | 241.78 | 393.77 | 287.35 |
| explore_1 | 8 | 147.26 | 201.81 | 176.04 |
| explore_2 | 4 | 182.31 | 318.96 | 203.85 |
| experimentator_1 | 1 | 223.17 | 223.17 | 223.17 |
| research_1 | 0 | — | — | — |

## Per-Size Best Times

| Size | Gen001 Best | Gen002 Best | Improvement | Solution |
|------|-----------|-----------|------------|----------|
| Small | 4.49 µs | 3.37 µs | 1.33x | gen002/explore_1/sol05 |
| Medium | 228.26 µs | 225.55 µs | 1.01x | gen002/explore_1/sol01 |
| Large | 3176.31 µs | 3841.72 µs | 0.83x (worse) | gen002/explore_1/sol01 |

Note: The gen002 best geomean (147.26 µs) has better small+medium but slightly
worse large than gen001 best (148.18 µs). The row-streaming architecture trades
large-benchmark B-reuse for simpler code and better small performance.

## Key Discoveries

1. **Row-streaming no-pack architecture (idea_014)** matches BLIS performance at
   147.26 µs. First architectural diversity in the population.

2. **Experimentator_1 provided critical data:**
   - Per-phase timing: kernel+store = 93-95%, packing = 5-7% (pattern_006)
   - NT stores: 2.3x on large, 0.9x on medium (idea_006 updated)
   - int8 accumulation: 11-13% improvement quantified (idea_004 updated)
   - NC sweep: NC=128 best geomean, per-size optimal differs (idea_019)
   - DRAM bandwidth: 24.84 GB/s streaming, 11.38 GB/s regular at 32 MB (fact_007)
   - C alignment: NOT 64-byte aligned in harness (fact_006) — blocks NT stores

3. **BLIS architecture at diminishing returns:** exploit_1 tested 12 variants of
   the gen001 best, none improved (pattern_007).

4. **No-pack direct B (idea_013) tested and found wanting:** explore_2 tested 4
   variants, best was 182.31 µs — 23% worse than BLIS. Packing cost is negligible
   but L1 reuse benefit is real.

5. **24 µs target feasibility:** Research agent calculated geomean floor of ~29 µs
   with ideal NT stores. Experimentator found ~62 µs optimistic floor. The target
   is physically challenging but not impossible.

## New Knowledge Created

- 6 new ideas: idea_014 through idea_019
- 4 new patterns: pattern_005 through pattern_008
- 2 new facts: fact_006, fact_007
- 1 new cluster: cluster_003 (Alternative Architectures)
- 6 updated ideas: idea_004, idea_005, idea_006, idea_009, idea_012, idea_013

## Strategic Assessment

Generation 2 was a **diagnostic generation**. The score improved marginally
(148.18 → 147.26 µs, ~0.6%) but the knowledge gained was substantial:
- The optimization landscape is now well-mapped (NC sweep, phase timing, bandwidth)
- The key constraint (C alignment blocking NT stores) is identified
- Two architectural approaches (BLIS + row-streaming) are established
- The path to the target is clearer: NT stores + 8-row int8 + small optimization

**strategic_shift: false** — No fundamental change in the frontier. The best
approach (AVX-512 popcount + deferred widening) is confirmed, and the new
row-streaming architecture is a peer to BLIS, not a breakthrough. The real
breakthrough will come from solving the NT store alignment problem.
