# Architect Report — Generation 1

## Confidence: High

The generation 1 plan is straightforward and low-risk. The available helpers make the path to
616 codewords direct and fast. The unknowns (whether ILNS approaches 616, whether orbit cliques
larger than 11 exist) are genuine open questions that generation 1 will resolve.

---

## Data Observations

**Baseline score = 262** (greedy with 20 random restarts). This is well below the algebraic
optimum because greedy construction without structure is inefficient — it gets trapped in
local optima far from the optimal region. The 262 baseline should be immediately superseded
by any agent using `helpers/agl18.py`.

**Rich helper infrastructure already exists:**
- `helpers/agl18.py` — Full AGL(1,8) orbit machinery, tested, achieves 616.
- `helpers/compat.py` — Fast bucket-based compatibility check (23x faster than naive).
  Enables efficient search over 40320-perm space.
- These helpers were presumably built in a prior attempt (attempt_001 also had baseline 262
  with same infrastructure). This generation should leverage them aggressively.

**No prior run data:** No clusters, no facts, no agent reports. All strategic knowledge must
be built from scratch in generation 1. This is expected for a cold start.

---

## What Didn't Fit

**Simulated annealing as a first-class agent:** I considered assigning an SA agent as one
of the explores, but decided ILNS (explore_2) is more interesting for diversity measurement.
SA would likely converge toward the same algebraic solution. ILNS explores whether structure-
free search can compete at all.

**PGL(2,7) construction:** The description mentions PGL(2,7) as a potential approach. I wanted
to assign this to an explore agent but deferred it to research_1 — we should understand the
theory before committing agent compute to it. If research_1 confirms PGL(2,7) gives a larger
code, generation 2 can build it directly.

**IP/LP relaxation:** Potentially powerful but likely too slow for 40320-variable problems
without specialized solvers. Assigned to research_1 to assess feasibility.

---

## Strategic Risks

**Homogeneity risk:** full_1 and explore_1 both use the AGL framework, which means two of
four agents are pursuing the same algebraic direction. If AGL is a dead end beyond 616,
generation 1 will produce two solutions at exactly 616.

This is acceptable because:
1. 616 is already well above the 262 baseline
2. explore_1 searches more deeply in the orbit graph than full_1
3. explore_2 provides genuine diversity (non-algebraic)
4. research_1 will tell us what generation 2 should do differently

**No beyond-616 solution in generation 1:** Likely outcome. The 616-to-926 gap requires
approaches we haven't tried yet (better orbit cliques, mixed construction, SA with clever
operators, LP relaxation). Research_1 findings will guide generation 2.

---

## Open Questions for the System Critic

1. **Is `helpers/agl18.py` fully validated?** The docstring says "validated against
   check_code()" but we should confirm the 616-code output is genuinely valid (all 616
   permutations satisfy pairwise distance ≥ 5).

2. **Is ILNS without group structure fundamentally limited for permutation codes?** If
   explore_2 reaches only 350-450, this suggests algebraic structure is essential, not
   just convenient. The system should be aware of this constraint.

3. **Should generation 2 deploy an experimentator to investigate the orbit graph structure?**
   Specifically: are there 12-orbit cliques in the AGL orbit compatibility graph? The orbit
   graph has 720 vertices with degree 138 — maximum clique size is an open question.

4. **Cost of the `agl18_compat_graph()` call:** It takes ~4s and builds a 720×720 boolean
   matrix. Multiple agents running in parallel may each rebuild it independently. A shared
   precomputed file would save compute in future generations.
