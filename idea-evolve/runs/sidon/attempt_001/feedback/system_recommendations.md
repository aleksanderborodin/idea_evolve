# System Recommendations — Generation 6

**Supersedes:** gen 5 recommendations
**Current best:** 105 (Rokicki-Dogon Bose-Chowla AP q=107, mul=433)
**Algebraic ceiling:** 105 (exhaustively confirmed, all q, all multipliers)
**Perturbation ceiling:** 105 (remove-k k=2-104 with 27K+ trials, structural self-healing property)
**Remaining gap:** ~4 elements to theoretical upper bound (~109)

---

## Priority 1 — Critical (must do before gen 7 agents launch)

### [REC-1] Assign research_1 with web-first ordering enforcement

The F₂(10000) published record has been unknown for **5 consecutive generations**. This must be resolved before any further CP-SAT compute is allocated.

**What to change:** research_1 brief in gen 7 must begin: "FIRST action (before anything else): run `WebSearch('OEIS A003022 Sidon set maximum')` and `WebSearch('F2 10000 Sidon set record')`. SECOND action: read `problems/sidon/helpers/rokicki_data.py` — it may contain tabulated answers. THIRD action: check `papers/summaries/` for prior research. Report your findings from steps 1–3 before any literature review."

**Expected impact:** Resolves 5-generation-old blocking question. If F₂(10000) = 105, halt all CP-SAT and perturbation search. If F₂(10000) ≥ 106, confirms CP-SAT is correctly prioritized.

---

### [REC-2] Assign VLNS formulation fix as first priority in gen 7

The VLNS bug is a 2-line fix with the diagnosis already complete: change `add_abs_equality` domain from [1,N] to [0,N] and add explicit `y[i] != fv` constraints before absolute difference calculation.

**What to change:** Assign a full or exploit agent with explicit brief: "The VLNS formulation has a known bug (see gen006/full_1.md section Phase 2). Fix the domain conflict as described, then run 50+ trials with diverse removal patterns (random-5, random-10, random-15, random-20, targeted-high-blocker). If any trial succeeds (finds 106+), extend to 500+ trials. If all 50 INFEASIBLE, record as genuine (not bug) and archive VLNS."

**Expected impact:** Either finds a path to 106 or conclusively closes the VLNS approach. Either outcome is high-value.

---

### [REC-3] Create helpers/cpsat.py before gen 7 agents launch

Three consecutive generations (gen 4 P2, gen 5 gap, gen 6 gap) have requested this helper. Every CP-SAT session re-derives the same formulation and introduces new bugs.

**What to change:** Assign experimentator_1 in gen 7 with sole focus: create `output/helpers/cpsat.py` with:
- `solve_sidon_cpsat(k, N, hint=None, time_limit=300, num_workers=8)` — standard k-element search with optional warm-start
- `vlns_sidon(fixed_elements, n_free, N, time_limit=120)` — VLNS with **corrected** formulation (domain [0,N], explicit y[i]!=fv constraints, no abs_equality domain conflict)

Include a self-test that runs k=50, N=1000 (should find feasible quickly) to verify formulation correctness. Do not allocate CP-SAT compute to exploration while the helper is being built.

**Expected impact:** Eliminates CP-SAT formulation errors and 5-10 turns of boilerplate per session. VLNS bug class will not recur.

---

### [REC-4] Update State of Affairs for gen 6 findings before gen 7 launches

The SoA header says `generation: 5`. Gen 6 produced definitive new findings that must be in the SoA before gen 7 agents read it. The Consistency Reviewer must run or the Evaluator must update the SoA.

**Critical updates required:**
1. Remove-k perturbation: "exhaustively debunked for k=2-104 (27K+ trials)" — NOT "untested for k≥3"
2. Self-healing property: "structural invariant — any k-element removal opens exactly k slots (the removed elements)" — add as established pattern
3. VLNS: "tested (9 trials), likely formulation bug — INFEASIBLE results not yet confirmed genuine"
4. DFS/backtracking: "confirmed = greedy (27s, baseline 66)" — close idea_005 as debunked
5. CP-SAT status: "6+ runs, all UNKNOWN, formulation may need rethinking"
6. Stale fact files: delete fact_002 and fact_004 from `knowledge/facts/` (stale copies with wrong content)

---

## Priority 2 — High Value (gen 7 strategic directions)

### [REC-5] Do NOT allocate CP-SAT with the same AllDifferent formulation as gen 5-6

**Evidence:** k=104 verification returned UNKNOWN in 30s even with the full hint. The AllDifferent-over-5565-diffs formulation is pathologically hard for OR-Tools CP-SAT presolve. More time with the same formulation will not change this.

**What to change:** Any CP-SAT run in gen 7 must use a DIFFERENT formulation. Options from full_1 gen6 and explore_1 gen6:
- Binary variable formulation: x_i ∈ {0,1} for each candidate element, difference sum uniqueness via explicit pair constraints
- Maximize-k formulation: instead of "find exactly k=106", maximize k — more solver-friendly
- Anti-algebraic: add constraint that solution shares ≤50% elements with 105-mark set

---

### [REC-6] Archive stale ideas before gen 7 knowledge dump

**Evidence:** idea_003, idea_015, idea_016 are 2-3 generations stale and confirmed far below the frontier (ceilings 69-75). They appear in the evaluator knowledge dump and consume context tokens.

**What to change:** Evaluator or Consistency Reviewer should move these to `knowledge/ideas/debunked/`:
- idea_015 (Fibonacci Ordering): ceiling 69, 3 gens stale → archive
- idea_016 (Min-Blocking): ceiling 69, 2 gens stale → archive
- idea_003 (Difference-Aware): ceiling unknown but well below frontier, 2 gens stale → archive
- pattern_009: merge into pattern_012 or archive

---

### [REC-7] Add C-extension helper for inner-loop Sidon validation

**Evidence:** Multiple agents cite ~200 trials/second in Python as a bottleneck. C-extension would give 10-100x speedup, enabling perturbation-style experiments that are currently compute-limited.

**What to change:** Assign experimentator to write `helpers/sidon_fast.c` compiled via ctypes with:
- `is_sidon_fast(arr, n)` — C implementation of difference uniqueness check
- `can_add_fast(arr, n, element)` — O(k) check using hash set
- Python wrapper `helpers/sidon_fast.py` using ctypes

**Note:** This is a multi-turn implementation. If session budget is tight, defer to a dedicated experimentator gen.

---

### [REC-8] Enforce single-agent ownership for external data fetches (carry forward from gen 5)

**Status from gen 5 REC-8:** Was listed as "what to change: Add to architect.md." Status unknown — not confirmed as implemented.

**What to change:** Add to `agents/architect.md` Recurring Helper Needs section: "Any brief that requires fetching external data (web search, paper download, database lookup) must designate exactly ONE agent for the fetch. Other agents that need the data must reference the first agent's output path in their brief, not perform the fetch themselves."

---

## Priority 3 — Process Improvements

### [REC-9] Add decision rule for CP-SAT UNKNOWN to prevent compute waste

**Evidence:** CP-SAT has returned UNKNOWN in 6+ runs across gens 4-6, totaling ~5400s of compute. The current prompt does not tell agents to stop when they see UNKNOWN from the same formulation.

**What to change:** Add to full.md and exploit.md agent templates: "If CP-SAT returns UNKNOWN with the same formulation and k value as a previous session (check `knowledge/experiments/` for prior CP-SAT results), do NOT run it again with the same settings. Either (a) change the formulation, (b) change k, or (c) move to a different approach."

---

### [REC-10] Research brief must cite sources or label claims "training data"

**Evidence:** research_1 gen6 produced Ruzsa-Lindström, GRASP, tabu search recommendations from training data without web search. These may be correct but cannot be verified.

**What to change:** Add to `agents/research.md`: "Every factual claim must be labeled with its source: [OEIS A00xxxx], [paper: Author Year], [web: URL], or [training data: unverified]. Claims labeled 'training data' must be noted as such in findings.md so downstream agents can weigh them appropriately."

---

## Tracking: Previous Recommendations Status

| Recommendation | Status |
|----------------|--------|
| Do NOT assign CP-SAT k≤105 (gen5 REC-1) | RESOLVED — gen6 targeted k=106 only |
| Update SoA before gen6 (gen5 REC-2) | PARTIAL — Consistency Review ran but SoA still gen5 header |
| Fix idea_022 Bose-Chowla formula (gen5 REC-3) | UNKNOWN — not mentioned in gen6 reports |
| Assign remove-k perturbation k=3-10 (gen5 REC-4) | RESOLVED — exploit_1 completed exhaustively |
| Create helpers/extend.py (gen5 REC-5) | RESOLVED — experimentator_1 created |
| Save 105-mark set in helpers/ (gen5 REC-6) | RESOLVED — rokicki_data.py created |
| Test alternative ILP solvers HiGHS/SCIP (gen5 REC-7) | PARTIAL — HiGHS not tested, full_1 used CP-SAT only |
| Single-agent ownership for data fetches (gen5 REC-8) | UNKNOWN — not confirmed in architect.md |
| Require algebraic briefs to specify formulas (gen5 REC-9) | UNKNOWN |
| Archive/test idea_005 backtracking (gen5 REC-10) | RESOLVED — explore_1 confirmed DFS = greedy |
