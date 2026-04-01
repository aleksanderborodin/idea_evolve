---
type: idea
id: idea_018
name: "vpshufb Nibble-LUT Kernel"
lifecycle: debunked
confidence: 0.1
first_seen: generation_2
last_updated: generation_3
last_confirmed_gen: 2
supported_by: []
contradicted_by: [gen003/explore_2/sol01, gen003/explore_2/sol02, gen003/explore_2/sol03, gen003/explore_2/sol04, gen003/explore_2/sol05]
related_ideas: [idea_001, idea_011]
cluster: cluster_001
tags: [vpshufb, lut, nibble, compute-kernel, debunked]
---

Replace the ternarylogic + 2×popcnt + sub compute path with a precomputed
16-entry nibble lookup table (LUT) via `vpshufb`.

**DEBUNKED in gen003.** Explore_2 built 5 variants of the vpshufb LUT kernel.
Best result: **341.78 µs** (sol04, 4-row with int8 accum) — **2.3x worse** than
the current best of 141.0 µs (ternlogd+popcnt kernel).

**Root cause:** The original hypothesis that "vpshufb runs on port 0/1, NOT port 5"
was **WRONG**. vpshufb (EVEX 512-bit) is a shuffle instruction that runs on port 5
on Tiger Lake (Willow Cove). This was confirmed by explore_2's empirical results
and corroborated by experimentator_1's port throughput microbenchmark.

The vpshufb approach adds overhead (nibble extraction via mask+shift) on top of
using the same bottleneck port as vpbroadcastb. It is strictly worse than the
ternlogd+vpopcntb approach for this problem.

All 5 variants tested:
- sol01 (533 µs): Single-row, stack LUT reloaded per j
- sol02 (345 µs): Single-row, LUT precomputed outside j-loop
- sol03 (420 µs): 4-row with int32 flush overhead
- sol04 (342 µs): 4-row with int8-only accumulation (best)
- sol05 (347 µs): Adaptive register/stack LUT selection

**Positive knowledge extracted:** The 4-row B-load amortization gave 1.55x medium,
1.67x large improvement even in the vpshufb kernel (sol04 vs sol02). This validates
multi-row B sharing as a general technique applicable to any compute kernel.
