---
type: pattern
id: pattern_007
name: "Published solutions are local minima for smooth-max Adam"
lifecycle: confirmed
confidence: 0.95
first_seen: generation_4
last_updated: generation_6
evidence: [gen004_exploit_1_sol01, gen004_exploit_1_sol02, gen004_exploit_2_sol01, gen006_exploit_2_sol01]
related_ideas: [idea_014, idea_007, idea_009, idea_017]
tags: [warm-start, local-minimum, smooth-max, basin, convergence]
---

Published solutions (AlphaEvolve and TTT-Discover arrays) are already at the floor
of their basin for smooth-max Adam optimization. **Now confirmed with float64 rigor.**

**Gen 4 evidence (float32 accept/reject):**
1. Conservative warm-start (exploit_1/sol01): 4 seeds, T=0.005→0.0001. Score moved by 3.8e-9 — noise.
2. Aggressive warm-start (exploit_1/sol02): sigma=0.1. C=1.5242 — destroyed solution.
3. Upsample to N=2000 (exploit_2/sol01): C=1.5159 — cubic interpolation destroyed sparse structure.

**Gen 6 evidence (float64 accept/reject) — DEFINITIVE:**
4. exploit_2 tested smooth-max Adam on AlphaEvolve Cell 49 (N=600, C=1.5040):
   - ALL 6 temperature phases rejected in float64: T=0.005→C=1.5414, T=0.0001→C=1.5057
   - Even the coldest temperature worsens C by +1.72e-03
   - Perturbed seed (sigma=0.007212) also rejected — recovered to 1.5086 but never baseline

5. **inv_softplus confound identified and controlled:** Default clip_min=-10 caused +5.66e-04
   round-trip error. Using clip_min=-20 reduces error to +1.66e-07. Gen 4 had this confound
   but it does NOT change the conclusion — even from the correct baseline, smooth-max Adam
   makes things worse at every temperature.

**PROMOTED TO CONFIRMED.** Confidence raised from 0.85 to 0.95. Six independent data points
across 2 generations, 2 different published solution families (1319-element and 600-element),
both float32 and float64 precision. Smooth-max Adam is definitively closed for published solutions.

**Implication:** Breaking below C=1.503 requires coordinate descent (idea_019) or LP-based
methods (idea_020). Smooth-max Adam should never be applied to published solutions again.
