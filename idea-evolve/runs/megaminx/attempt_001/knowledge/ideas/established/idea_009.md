---
type: idea
id: idea_009
name: Empirical algebraic identity compression
lifecycle: established
confidence: 0.95
first_seen: gen_002
last_updated: gen_004
last_confirmed_gen: gen_004
supported_by: [gen002_explore_2_sol01, gen002_explore_2_sol02, gen002_explore_2_sol03, gen002_explore_2_sol05, gen002_explore_2_sol07, gen002_explore_2_sol08, gen003_explore_2_sol01, gen004_exploit_1_sol01]
contradicted_by: []
related_ideas: [idea_005, idea_001]
cluster: compression
tags: [compression, algebraic, identities, commutators, conjugations, empirical]
---

# Empirical Algebraic Identity Compression

## Summary

Discover valid Megaminx-specific rewrite rules (commutators, conjugations, cancellations)
by empirically scanning sample_submission paths for subsequences that simplify to identity
or shorter forms. Apply the verified rules to compress paths beyond basic X.-X cancellation.
Best result: **44114** (compression_ratio=0.8723) from gen002. Used as Phase 1 baseline
in gen003 and gen004 solutions.

## Evidence

**CONFIRMED WORKING (8 solutions across 3 generations):**
- gen002_explore_2_sol01: 44114 (336 rules) — BEST compression-only
- gen002_explore_2_sol02: 44118 (432 rules)
- gen002_explore_2_sol03: 44118 (combined)
- gen002_explore_2_sol05: 44118 (systematic)
- gen002_explore_2_sol07: 44114 (span-6)
- gen002_explore_2_sol08: 44114 (bucket-aware)
- gen003_explore_2_sol01: 44114 (Phase 1, then predictor brought to 44094)
- gen004_exploit_1_sol01: 44114 (Phase 1, full recipe brought to 44111)

**Total: 8 solutions confirm this compression floor. Ceiling firmly established.**

## Status

ESTABLISHED. This is the compression-only floor. All future solutions should use this as
a baseline and layer additional techniques (predictor beam search, MITM) on top. No further
compression-only work is warranted.
