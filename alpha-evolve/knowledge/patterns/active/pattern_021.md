---
type: pattern
id: pattern_021
name: "Incremental autoconvolution updates accumulate drift requiring periodic FFT resync"
lifecycle: active
confidence: 0.85
first_seen: generation_10
last_updated: generation_10
evidence: [gen010_exploit_1_sol01]
related_ideas: [idea_019]
tags: [incremental-update, drift, FFT, resync, float64, precision, engineering]
---

When performing coordinate descent using incremental autoconvolution updates (O(N) per
modification vs O(N log N) for full FFT), floating-point errors accumulate at a rate of
~2.7e-16 per accepted modification (~1.4e-12 per round of ~5000 modifications).

**Gen 10 evidence (exploit_1):**
- After 5 rounds (~25k modifications), drift = 7e-12 while true improvement was only ~2e-12
- The incremental method "hallucinates" 3.5x more improvement than actually exists
- Run 1 (no resync): 72 rounds, incremental C = 1.50286286809259, verified C = 1.50286286819757.
  Drift = 1.05e-10.
- Run 2 (FFT resync every 5 rounds): 71 rounds, verified C = 1.50286286819877.

**Implication:** Without periodic FFT resync, the accept/reject criterion becomes
increasingly unreliable. Modifications may be accepted because the drifted max_ac is
artificially low, not because the modification is genuinely improving. Conversely,
good modifications may be rejected because drift has already "claimed" the improvement.

**Recommended mitigation:** FFT resync every 1-5 rounds. Overhead is ~0.2s per resync
for N=30k (negligible vs 6-12s/round for CD). Per-round resync eliminates drift entirely.
