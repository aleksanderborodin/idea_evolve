---
type: idea
id: idea_009
name: "Wider Micro-Kernel 8x64"
lifecycle: active
confidence: 0.5
first_seen: generation_0
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen002/explore_2/sol01, gen003/explore_1/sol02]
contradicted_by: [explore_1/sol03, gen003/exploit_1/sol04, gen003/exploit_1/sol05]
related_ideas: [idea_001, idea_004, idea_016]
cluster: cluster_001
tags: [micro-kernel, 8x64, register-pressure, avx512]
---

With 32 zmm registers (AVX-512), process 8 rows of A at once instead of 4,
halving the number of B loads.

**Gen003 updates — first 8-row int8 empirical data:**

Explore_1/sol02 tested the 8-row int8 kernel (idea_016): **168.35 µs** — a major
improvement over gen001's 8-row int16 (493 µs) and gen002's 8-row jc-outer (207 µs).
The int8 accumulation resolves the register pressure issue as predicted.

However, 168 µs is still worse than the 1-row best (141 µs). The regression is
NOT from register pressure (resolved by int8) but from **C write scatter** — 8 rows
means stores jump 256 KB apart for large, destroying L1 cache effectiveness.

Exploit_1 also tested 8-row variants with poor results (sol04: 399 µs, sol05: 340 µs),
confirming that C write locality dominates over B-load savings.

**Lifecycle changed from disputed to active.** The original dispute (register pressure
with int16) is resolved. The new challenge (C write scatter) is a different problem
that may be solvable with column-blocked output tiling.

Explore_2's vpshufb experiments showed that 4-row B-sharing gives 1.55-1.67x on
medium/large — suggesting 4-row may be a better tradeoff than 8-row for this
problem's memory access patterns.
