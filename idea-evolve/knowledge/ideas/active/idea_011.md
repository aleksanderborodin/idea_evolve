---
type: idea
id: idea_011
name: "vpternlogd for Fused Boolean Logic"
lifecycle: active
confidence: 0.6
first_seen: generation_1
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [explore_1/sol02, explore_1/sol10]
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

explore_1/sol02 used `_mm512_ternarylogic_epi64` with imm8 values 0xD8/0xE4 and
achieved 400.68 µs (1.92x vs baseline). explore_1/sol10 (148.18 µs, best solution)
also uses ternarylogic. Research Finding 7 confirmed the truth table derivation
and noted that vpternlogd runs on port 0, balancing load with popcnt (port 5).

Note: there is some uncertainty about the exact truth table values. explore_1
uses 0xD8/0xE4 while research derived 0xCA/0xAC. The exact value depends on
operand order in `_mm512_ternarylogic_epi64(a, b, c, imm8)`. Both produce
correct results as verified by evaluation. However, truth table verification
should be a priority to avoid subtle correctness bugs.

Active — well-supported but needs isolated benchmarking to quantify the standalone
improvement vs the old OR+AND approach.
