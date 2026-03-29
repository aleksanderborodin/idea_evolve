---
type: pattern
id: pattern_009
name: "SA at coarse scale fails regardless of calibration quality"
lifecycle: active
confidence: 0.9
first_seen: generation_5
last_updated: generation_5
evidence: [gen005_explore_1_sol01, gen005_explore_1_sol02, gen005_explore_1_sol03, gen003_explore_1_sol01, gen003_explore_1_sol02, gen003_explore_1_sol03]
related_ideas: [idea_004, idea_007, idea_008]
tags: [SA, simulated-annealing, coarse-scale, dead-end, calibration]
---

Simulated Annealing at coarse resolutions (N=23-80) is a confirmed dead end for this
problem, regardless of calibration quality. Gen 5's properly calibrated experiments
close the "maybe calibration was the problem" hypothesis.

**Gen 3 evidence (poorly calibrated, 96-100% acceptance):**
- N=40: C=1.5148, N=80: C=1.5155, N=30: C=1.5169

**Gen 5 evidence (properly calibrated, 20% acceptance):**
- N=23 (buggy SA structure): C=1.5227
- N=23 (corrected SA, 20% acceptance): C=1.5227 — identical to buggy version
- N=80 (corrected SA): C=1.5162 — within historical range (1.5148-1.5169)

**Key finding:** The SA structure bug (running inner optimizer before vs after Metropolis
check) made NO difference. Both produce the same score after fine-tuning at N=600. The
fine-tuning step dominates — regardless of what SA does at coarse scale, gradient descent
at N=600 converges to the same basin.

**Conclusion:** The coarse landscape has the same qualitative attractor structure as the
fine landscape. SA at coarse scale cannot find different basins. This technique should
not be revisited.
