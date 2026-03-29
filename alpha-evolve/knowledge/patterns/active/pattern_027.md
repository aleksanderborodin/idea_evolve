---
type: pattern
id: pattern_027
name: "Intra-round drift dominates at 2000+ modifications per round"
lifecycle: active
confidence: 0.75
first_seen: generation_11
last_updated: generation_11
evidence: [gen011_exploit_2_sol01, gen011_exploit_1_observations]
related_ideas: [idea_019]
tags: [drift, intra-round, incremental-update, FFT-resync, precision]
---

Per-round FFT resync eliminates between-round drift but NOT within-round drift.
With 2000+ modifications per round, intra-round drift exceeds real improvement.

**Gen 11 evidence (exploit_2):**
- Phase 3: All 3 multi-trajectory runs (1964-2619 "improvements" each) ended at
  WORSE verified C than the Phase 2 starting point.
- FFT resync after round revealed true C was 4.7e-13 WORSE than tracked claim.
- The drift at 2000 mods/round ≈ 2000 × 2.7e-16 = 5.4e-13, which exceeds the
  ~1e-13 per-modification real improvement scale.

**Gen 11 evidence (exploit_1 observations):**
- Early rounds with 2019 improvements had net NEGATIVE real improvement
  (drift > gain).
- After 410 rounds of single-pass CD (~50-100 improvements/round), true C
  improvement was only ~1.8e-12 total.

**Correction to pattern_021:** The drift figure of ~1.4e-12/round assumed
per-5-round resync. Per-round resync eliminates between-round drift but
intra-round drift at 2000+ mods/round still exceeds improvement scale.

**Recommendation:** Resync every 500 modifications OR every round, whichever
is smaller. This keeps intra-round drift below ~1.4e-13.
