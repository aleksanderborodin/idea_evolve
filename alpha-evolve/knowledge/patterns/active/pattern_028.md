---
type: pattern
id: pattern_028
name: "Solution entrypoints with deadline-based CD are non-reproducible"
lifecycle: active
confidence: 0.85
first_seen: generation_11
last_updated: generation_11
evidence: [gen011_exploit_1_observations, gen011_exploit_2_sol01]
related_ideas: [idea_019, idea_014]
tags: [reproducibility, entrypoint, deadline, baked-array, non-determinism]
---

Solution entrypoints that run coordinate descent with wall-clock deadlines
produce different arrays on each invocation. The variance is ~5-8e-11,
comparable to 10+ rounds of improvement.

**Gen 11 evidence:**
- exploit_1: Re-ran gen010/explore_2/sol01.py entrypoint. Got C=1.5028628681754832,
  not the cached 1.5028628681165177. Gap: 5.9e-11.
- exploit_2: Re-ran same entrypoint. Got C=1.5028628681772360. Gap: 6.1e-11.
- Both agents independently confirmed the non-reproducibility.

**Root cause:** gen010/explore_2's entrypoint includes a `_DEADLINE` timer.
Under different system load, different numbers of CD rounds complete, producing
different final arrays. Random element ordering adds further variance.

**Impact:** Agents starting from gen010 entrypoint waste ~490s load time AND
get a worse starting point than the cached best. The gap (~6e-11) is larger
than an entire generation's improvement.

**Mandatory fix:** Bake the final array as a numpy literal in the solution file.
This provides instant loading (<1s) and bit-identical results every time.
