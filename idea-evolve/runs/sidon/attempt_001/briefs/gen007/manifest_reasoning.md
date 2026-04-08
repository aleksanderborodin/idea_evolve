# Manifest Reasoning — Generation 7

## Situation Assessment

**Score: 105, plateaued for 2 generations.** The 105-mark Bose-Chowla ap q=107 set is:
- The algebraic ceiling (exhaustive multiplier search, all primes q<=109, all construction types)
- Perfectly self-healing under perturbation (27K+ trials for k=2-104, pattern_014)
- Greedy-maximal (zero addable elements)

**Remaining paths to 106+** (in order of expected value):
1. VLNS with corrected formulation — 9 trials returned INFEASIBLE due to a diagnosed bug, not genuine infeasibility
2. CP-SAT with binary variable formulation — AllDifferent formulation failed 6000+ seconds; binary may be tractable
3. F₂(10000) lookup — if the published record is 105, all search is futile
4. Non-algebraic constructions — Ruzsa-Lindström untested, different algebraic seed may reach different basin

**Score trajectory:** 66→102→102→105→105→105. Jumps came from algebraic constructions (Singer, then Bose-Chowla). The plateau coincides with algebraic ceiling being confirmed. Breaking through requires either exact methods (CP-SAT/VLNS) or an entirely new approach.

## Agent Allocation (5 agents)

### Track A — Directed Exploitation (3 agents)

**experimentator_1 (opus, 1200s):** Build `helpers/cpsat.py` with corrected VLNS and binary CP-SAT.
- **Why MANDATORY:** REC-3 — requested for 3 consecutive generations. Every CP-SAT session
  re-derives the formulation and introduces bugs. The gen 6 VLNS bug is a direct consequence
  of not having a validated helper.
- **Why opus:** Helper quality matters — a buggy helper is worse than no helper. Opus for
  precision on implementation + self-testing.
- **Timeout 1200s:** experimentator_1 gen 6 took 201s (simpler helpers). cpsat.py is more
  complex with formulation + self-test. 1200s is generous.

**exploit_1 (sonnet, 1500s):** Fix VLNS formulation bug directly and run 50+ trials.
- **Why:** VLNS fix is the single highest-expected-value experiment (EXP-1 rated CRITICAL).
  The bug is diagnosed, the fix is 2 lines, and each trial is cheap (<1s if INFEASIBLE,
  ~30-120s if solver actually searches). 50+ diverse trials give statistical power.
- **Why separate from experimentator_1:** experimentator_1 builds the reusable helper;
  exploit_1 uses the fix immediately for mass experimentation. Both run in parallel.
- **Why sonnet:** The implementation is straightforward (bug fix + loop). Sonnet is sufficient.
- **Timeout 1500s:** exploit_1 gen 6 took 1994s but was doing exhaustive perturbation (27K trials).
  VLNS trials are faster per trial but we want many. 1500s allows ~50-100 trials.

**full_1 (sonnet, 2700s):** Binary variable CP-SAT with maximize-k objective.
- **Why:** AllDifferent formulation failed across 6000+ seconds (gens 4-6). Binary variable
  formulation is fundamentally different — CP-SAT may handle binary propagation much better.
  Maximize-k gives the solver objective gradient (vs. feasibility's pass/fail). Anti-algebraic
  constraint forces search in non-algebraic region.
- **Why sonnet:** CP-SAT implementation is well-defined. The challenge is runtime, not coding.
- **Timeout 2700s:** full_1 gen 6 took 2843s (timed out). Binary formulation may have larger
  model size (more constraints) but CP-SAT has good handling of binary variables. 2700s allows
  1800s solver time + 900s for setup/alternatives.

### Track B — Radical Exploration (2 agents, MANDATORY)

**explore_1 (sonnet, 1500s):** Ruzsa-Lindström construction + SA from non-algebraic seed.
- **Why:** idea_025 (Ruzsa-Lindström) has been in the knowledge base since gen 6 with ZERO
  trials. It's a genuinely different algebraic construction (quadratic residues vs. primitive
  roots). Even if it achieves ~70-75 as a base, SA from this starting point is in a different
  basin of attraction than anything tried before.
- **Explicitly forbidden:** Reading population/best.py, using Singer/Bose-Chowla, importing
  BEST_105. Must start from scratch.
- **Timeout 1500s:** Explore_1 gen 6 took 989s. Ruzsa-Lindström + greedy + SA needs more room.

**research_1 (sonnet, 900s):** Web-first F₂(10000) lookup + novel approaches.
- **Why:** F₂(10000) has been unknown for **6 generations** due to systemic research agent
  failure (sessions terminated before web searches, findings written from training data).
  This is the single most important piece of missing information — it determines whether 106
  is a goal or a fantasy.
- **Enforcement:** Brief has MANDATORY ordered steps (Step 1: read rokicki_data.py, Step 2:
  web searches, Step 3: report before anything else). Source labeling required.
- **Timeout 900s:** research_1 gen 6 took 1127s (timed out, no web searches done). 900s
  should be sufficient for focused web lookup + synthesis. The timeout pressure prevents
  the agent from drifting into training-data literature review before doing web searches.

## What I Chose NOT To Do

1. **No second explore agent.** With 105 confirmed as algebraic ceiling and search methods
   exhausted, additional explores would likely repeat known-bad approaches. One Track B
   explore (Ruzsa-Lindström) is sufficient for diversity.
2. **No genetic crossover.** All top solutions are algebraic (105) or ET-based (75). Crossing
   these produces nothing useful — the construction methods are incompatible.
3. **No C-extension helper (REC-7).** Lower priority than cpsat.py helper. Perturbation is
   debunked anyway, so faster is_sidon() would only benefit future computational search.
   Defer to gen 8 if VLNS/CP-SAT show promise.
4. **No dedicated anti-algebraic agent.** full_1 will try anti-algebraic as Phase 2 after
   the main binary CP-SAT run. A separate agent for this is not warranted.
5. **No overnight CP-SAT.** Agent sessions max at ~45 minutes. True overnight runs need
   user intervention (separate process). Not actionable in this framework.

## Risks

1. **Binary CP-SAT may have too many constraints.** N=10000 means ~25M pair-sum collisions.
   Model building alone could exhaust the session. full_1's brief includes fallback strategies.
2. **VLNS fix may not resolve the bug.** The diagnosis is plausible but untested. If the fix
   doesn't work, exploit_1 needs to debug further rather than running 50 trials on a broken formulation.
3. **Research_1 may fail again.** Web search quality depends on query formulation and whether
   the information exists online. F₂(10000) may genuinely not be tabulated anywhere.
4. **Ruzsa-Lindström may be equivalent to Singer.** For certain parameter choices, different
   constructions can produce the same set. explore_1 should verify distinctness.
5. **experimentator_1 and exploit_1 both implement VLNS.** Potential redundancy — but
   experimentator_1 builds a reusable helper while exploit_1 runs experiments. The overlap
   is acceptable because both are independently valuable.

## Recommendations Addressed

| Recommendation | Agent | Status |
|----------------|-------|--------|
| REC-1 (web-first research) | research_1 | Brief has mandatory ordered steps |
| REC-2 (VLNS fix) | exploit_1 | Primary directive |
| REC-3 (helpers/cpsat.py) | experimentator_1 | **MANDATORY** — 3 consecutive gens |
| REC-4 (SoA update) | N/A | Evaluator/Consistency Reviewer job, not agent |
| REC-5 (no AllDifferent) | full_1 | Brief explicitly forbids AllDifferent |
| REC-6 (archive stale ideas) | N/A | Evaluator/Consistency Reviewer job |
| REC-7 (C-extension) | Deferred | Lower priority than cpsat.py |
| REC-8 (single-agent ownership) | N/A | No external data fetches needed this gen |
| REC-9 (CP-SAT UNKNOWN rule) | full_1 | Brief mandates different formulation |
| REC-10 (source labeling) | research_1 | Brief requires source labels |
