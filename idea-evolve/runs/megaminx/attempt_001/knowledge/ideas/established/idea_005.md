---
type: idea
id: idea_005
name: Megaminx commutator and identity discovery
lifecycle: established
confidence: 0.95
first_seen: gen_001
last_updated: gen_002
last_confirmed_gen: gen_002
supported_by: [gen002_explore_2_sol01, gen002_explore_2_sol02, gen002_explore_2_sol03, gen002_explore_2_sol05, gen002_explore_2_sol07, gen002_explore_2_sol08]
contradicted_by: []
related_ideas: [idea_001, idea_009]
cluster: compression
tags: [algebra, identities, commutators, group_theory]
---

# Megaminx Commutator and Identity Discovery

## Summary

Systematically discover valid move-sequence identities specific to Megaminx's Cayley
graph by empirically scanning sample_submission paths. Apply verified identities to
compress paths beyond basic X.-X cancellation. **CONFIRMED WORKING** with 6 solutions
achieving ~44114 (compression_ratio=0.8723) vs 46312 baseline.

## What Was Established

**gen002 results:**
- gen002_explore_2_sol01 (336 empirical rules) → 44114 — BEST
- gen002_explore_2_sol02 (432 systematic rules) → 44118
- gen002_explore_2_sol03 (combined) → 44118
- gen002_explore_2_sol05 (systematic, move-list) → 44118
- gen002_explore_2_sol07 (span-6) → 44114
- gen002_explore_2_sol08 (bucket-aware) → 44114

**Key finding:** Empirical discovery (rules from sample_submission) outperforms
systematic enumeration (all mathematically valid rules). The test-set-specific rules
are more valuable than comprehensive enumeration.

## Valid Identity Types

1. **Conjugations: X.Y.X⁻¹ → Y** — Confirmed valid for many (X,Y) pairs
2. **Commutators: X.Y.X⁻¹.Y⁻¹ → identity** — Confirmed valid for many (X,Y) pairs
3. **Span-2 overlaps: X.-X.Y → Y** — Adjacent cancellation across a move
4. **X.-X cancellation** — Standard baseline (already in idea_001)

## Why Conjugations Work in Non-Commutative Megaminx

This is non-trivial. In a non-commutative group, conjugation ABA⁻¹ does NOT generally
equal B. The fact that many conjugations DO simplify to just B for Megaminx's specific
Cayley graph means there is special algebraic structure in the generator set. This
was discovered empirically and confirmed across 6 solutions.

## Status

ESTABLISHED. The compression ceiling is ~44114 (compression_ratio=0.8723).
Compression alone cannot reach 15000 target. Beam search + trained predictor is needed.
