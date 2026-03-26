---
type: pattern
id: pattern_005
name: "The 1.509x basin is extremely deep — perturbation cannot escape it"
lifecycle: active
confidence: 0.85
first_seen: generation_3
last_updated: generation_3
evidence: [gen003_exploit_1_sol02, gen003_exploit_1_sol01, gen003_explore_1_sol01, gen003_explore_1_sol02]
related_ideas: [idea_007, idea_008, idea_015]
tags: [basin, attractor, perturbation, convergence, depth]
---

The ~1.509 basin reached by smooth-max + Adam is extremely deep. Evidence from
gen 3:

1. **DCT perturbation:** 10 configs with scales 5%-18% all converge back to
   C = 1.5091 +/- 0.000028. Even perturbations raising C to 1.83 (36% worse)
   converge back to the same basin floor.

2. **Extended low-temp polish:** T=0.00003 with 45k steps yields only 0.000025
   improvement (1.50936 -> 1.50933). The basin floor is effectively flat.

3. **Coarse-scale SA:** All 3 SA solutions (N=30-80) converge to worse scores
   (1.5148-1.5169), suggesting SA perturbations at coarse scale don't find
   better basins — they find worse ones or return to the same one.

4. **Only 25% of seeds find this basin:** exploit_1 found that only seed 0 out
   of 4 reached ~1.509. Seeds 1-3 gave 1.516-1.525. The basin is hard to find
   but once found, impossible to escape.

**Implication:** Any gradient-descent-based approach (with or without smooth-max)
appears limited to C >= 1.509. Reaching C < 1.505 likely requires either
(a) warm-starting from published solutions or (b) fundamentally different
algorithms (LP-guided, genetic crossover at solution level).
