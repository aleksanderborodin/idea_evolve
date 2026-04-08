---
type: idea
id: idea_023
name: "Multiplier Optimization for Algebraic Constructions"
lifecycle: established
confidence: 0.9
first_seen: generation_5
last_updated: generation_5
last_confirmed_gen: 5
supported_by: [gen005_experimentator_1_sol01, gen005_experimentator_1_sol02, gen005_research_1_sol02]
contradicted_by: []
related_ideas: [idea_006, idea_022, idea_008]
cluster: cluster_001
tags: [algebraic, multiplier, optimization, span-minimization]
---

When constructing Sidon sets from algebraic difference sets (Singer pp, Bose-Chowla ap),
applying a multiplier k to all elements modulo the group order can dramatically change the
span of the resulting set. Searching for the optimal multiplier is essential for fitting
the most marks into a bounded range.

**Generation 5 evidence**:
- **Singer q=103 (pp) with multiplier=400**: span=9581, fits 104 marks in {0..10000}.
  Previous pipeline implementations used multiplier=1, getting span ~10290 and only 102
  marks fitting. **The 4-generation mystery of why q=103 scored 102 is solved**: wrong
  multiplier.
- **Bose-Chowla q=107 (ap) with multiplier=433**: span=9884, fits 105 marks.
- **Exhaustive multiplier search for 106 marks**: experimentator_1 tested ALL coprime
  multipliers for q=107 (pp: 9072, ap: ~5700) and q=109 (pp: ~9900). Best 106-mark
  span is 10135 > 10000. No multiplier works for 106 marks.

**Why this matters**: The helpers/singer.py implementation does NOT search multiplier
space adequately. It produces raw Singer sets (effectively multiplier=1 or searches a
small subset). Future algebraic constructions MUST include exhaustive multiplier search
to find minimum span.

**Implication**: The pipeline was leaving 2-3 elements on the table for 4 generations
because it didn't know to search multipliers. This is a generalizable lesson: any
algebraic construction's "usable size for bounded N" depends critically on multiplier
optimization, not just the construction itself.
