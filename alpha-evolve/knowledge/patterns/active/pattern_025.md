---
type: pattern
id: pattern_025
name: "Non-IP pair moves amplify subsequent CD gains by ~15x"
lifecycle: active
confidence: 0.7
first_seen: generation_11
last_updated: generation_11
evidence: [gen011_explore_1_sol01]
related_ideas: [idea_024, idea_019]
tags: [amplification, non-integral-preserving, pair-search, coordinate-descent, synergy]
---

Non-integral-preserving 2-element moves applied before ultra-fine CD produce
a multiplicative amplification effect on subsequent CD improvement.

**Gen 11 evidence:**
- Direct Phase 2 improvement: ~2.7e-10 (2300 improvements)
- Subsequent CD improvement: ~4.0e-9 (10995 improvements in 1 round)
- Without Phase 2, same starting point yields: ~5e-10 from CD (gen010_explore_2 data)
- Amplification ratio: ~15x (4.0e-9 / 2.7e-10 direct)

The pair moves appear to shift the solution onto flat ridges that connect to
deeper basins. CD then exploits these new descent paths through its
integral-adjustment mechanism. The combination is synergistic — neither
technique alone achieves what they achieve together.

**Single observation — needs independent replication in gen 12.** If confirmed,
this establishes a two-phase protocol that could sustain improvements for
several more generations.
