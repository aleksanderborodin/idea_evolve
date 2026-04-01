---
type: idea
id: idea_011
name: "vpternlogd for Fused Boolean Logic"
lifecycle: active
confidence: 0.75
first_seen: generation_1
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [explore_1/sol02, explore_1/sol04, explore_1/sol10, gen002/explore_1/sol01, gen002/explore_1/sol02, gen002/explore_1/sol03, gen002/explore_1/sol04, gen002/explore_1/sol05, gen002/explore_1/sol06, gen002/explore_1/sol07, gen002/explore_1/sol08, gen003/exploit_1/sol02, gen003/explore_1/sol01, gen003/explore_1/sol02, gen003/explore_1/sol03, gen003/explore_1/sol04]
contradicted_by: []
related_ideas: [idea_001]
cluster: cluster_001
tags: [vpternlogd, ternary-logic, instruction-reduction, avx512]
---

`vpternlogd` computes any 3-input boolean function in one instruction using an
8-bit truth table. The core binary-ternary formula:
- `(a_pos | b) & (a_neg | ~b)` = `vpternlogd(a_pos, a_neg, b, 0xD8)` or `0xCA`
- `(a_pos | ~b) & (a_neg | b)` = `vpternlogd(a_pos, a_neg, b, 0xE4)` or `0xAC`

This replaces 6-7 bitwise instructions (including pre-computing ~b) with 2
ternary logic instructions per row per k-step. It also eliminates the need for
a dedicated `v_not_b` register, saving one register.

**Gen003 consistency review:** Confidence raised from 0.6 to 0.75. This idea is
used centrally by 12+ solutions across all 3 generations, including the overall
best (gen003/exploit_1/sol02, 141.0 µs). The supported_by list was incomplete —
updated to include all gen002 and gen003 solutions that use vpternlogd centrally.

The standalone improvement has still not been isolated (no A/B test of ternlogd
vs OR+AND with all else equal), which prevents promotion to established. However,
the consistent presence in all top solutions and the theoretical instruction
count reduction (6-7 → 2 per row per k-step) make it very likely to be
beneficial.

Note on truth tables: explore_1 uses 0xD8/0xE4 while research derived 0xCA/0xAC.
Both are correct — operand order differs. All solutions produce correct results.

vpternlogd runs on port 0/5 with ~0.5c throughput (fact_008), which helps balance
load with vpopcntb (port 0/1).
