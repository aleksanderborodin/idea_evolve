# Solution-Idea Map — Gen 002

## Solution gen002_explore_1_sol01 (score: INVALID, syntax error)
- **Central:** idea_007 (IDA* with corner-only PDB)
- **Peripheral:** None
- **Novel elements:** Attempted IDA* with corner-only pattern database — FAILED due to structural error in corner/edge classification assumptions. All 24 Megaminx generators are 5-cycles, not a mix of 2-cycles and 3-cycles.

## Solution gen002_explore_1_sol02 (score: INVALID, syntax error in file write)
- **Central:** idea_006 (Hamming-predictor guided beam search)
- **Peripheral:** None
- **Novel elements:** Attempted hamming-guided beam search — FAILED due to UTF-8 file corruption. Score = sentinel 1e9. This was the zero-cost experiment to test idea_006.

## Solution gen002_explore_1_sol03 (score: 46312, compression_ratio: 0.9158)
- **Central:** idea_001 (multi-pass enhanced compression) + idea_006 (hamming-guided beam fallback)
- **Peripheral:** idea_006 (hamming predictor for hard/very_hard)
- **Novel elements:** Hybrid approach: multi-pass compression for all, hamming-guided beam for hard/very_hard. No improvement over baseline — hamming provides no advantage.

## Solution gen002_explore_1_sol04 (score: 46312, compression_ratio: 0.9158)
- **Central:** idea_001 (timing-budget-aware beam + enhanced compression)
- **Peripheral:** idea_006 (hamming predictor)
- **Novel elements:** Timing-budget-aware approach: timed beam on deepest very_hard puzzles. No improvement — beam search ceiling confirmed.

## Solution gen002_explore_2_sol01 (score: 44114, compression_ratio: 0.8723) — NEW BEST
- **Central:** idea_009 (empirical algebraic identity compression)
- **Peripheral:** idea_001 (baseline X.-X cancellation)
- **Novel elements:** Discovered 336 empirically verified rewrite rules from sample_submission. Commutators and conjugations confirmed valid in Megaminx. 2198 points better than baseline.

## Solution gen002_explore_2_sol02 (score: 44118, compression_ratio: 0.8724)
- **Central:** idea_009 (systematic commutator enumeration, 432 rules)
- **Peripheral:** idea_001
- **Novel elements:** Same approach but systematic enumeration of ALL commutators/conjugations. Slightly worse than empirical (44118 > 44114) — extra systematic rules were noise.

## Solution gen002_explore_2_sol03 (score: 44118, compression_ratio: 0.8724)
- **Central:** idea_009 (combined systematic + empirical)
- **Peripheral:** idea_001
- **Novel elements:** Combined empirical + systematic rules. Same as sol02.

## Solution gen002_explore_2_sol04 (score: INVALID, unknown move '-')
- **Central:** idea_009 (string replacement for identity rules)
- **Peripheral:** None
- **Novel elements:** Attempted string replacement to apply rules. FAILED — string replacement creates empty move names at pattern boundaries, corrupting paths. Never use string replacement for move sequences.

## Solution gen002_explore_2_sol05 (score: 44118, compression_ratio: 0.8724)
- **Central:** idea_009 (systematic rules, move-list application)
- **Peripheral:** idea_001
- **Novel elements:** Same systematic enumeration as sol02 but with move-list (not string replacement). Confirms that string replacement is the failure mode.

## Solution gen002_explore_2_sol06 (score: 46312, compression_ratio: 0.9158)
- **Central:** idea_001 (pure empirical internal-cancellation mining, 1832 rules)
- **Peripheral:** None
- **Novel elements:** Attempted to find patterns with internal X.-X cancellation. FAILED — any pattern with internal cancellation is already caught by X.-X pass. 1832 rules were noise, no improvement.

## Solution gen002_explore_2_sol07 (score: 44114, compression_ratio: 0.8723)
- **Central:** idea_009 (span-6 extended patterns, 888 rules)
- **Peripheral:** idea_001
- **Novel elements:** Extended to span-6 patterns (sol01 was span-2 to span-5). Matched sol01 (44114) — additional span-6 patterns too specific.

## Solution gen002_explore_2_sol08 (score: 44114, compression_ratio: 0.8723)
- **Central:** idea_009 (bucket-aware compression with same rules)
- **Peripheral:** idea_001
- **Novel elements:** Same rules applied uniformly to all buckets. Matched sol01 — bucket-aware approach didn't help, rules universally applicable.

## Solution gen002_exploit_1_sol02 (score: 46312, compression_ratio: 0.9158)
- **Central:** idea_006 (narrow hamming-guided search on hard/very_hard)
- **Peripheral:** idea_001
- **Novel elements:** Narrow hamming-guided search with small beam budgets on hard/very_hard. 293s eval time. Same as baseline — hamming provides no advantage (confirmed by research_1).

## Solution gen002_research_1 (no score — research agent)
- **Central:** research findings (no solution produced)
- **Peripheral:** None
- **Novel elements:** CRITICAL FINDINGS: (1) hamming = unguided at all beam widths, (2) beam_mode='simple' required, (3) trained MLP pipeline confirmed, (4) beam_width must be 4x-32x larger, (5) all generators are 5-cycles, (6) GPU automatically used

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total solutions | 12 |
| Valid solutions | 10 |
| Invalid solutions | 2 (sol01 syntax, sol04 move error) |
| Best score | 44114 (gen002_explore_2_sol01) |
| Best valid score | 44114 |
| Previous best | 46312 (gen001 baseline) |
| Improvement | 2198 points (4.7%) |
| Solutions using idea_001 | 10 |
| Solutions using idea_003 | 0 (beam used but not central) |
| Solutions using idea_005/009 | 6 |
| Solutions using idea_006 | 3 (all = 46312, debunked) |
| Solutions using idea_007 | 1 (invalid assumptions) |
| Solutions using idea_008 | 0 (never tested) |
