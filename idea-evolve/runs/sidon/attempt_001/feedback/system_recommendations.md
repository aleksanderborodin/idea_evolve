# System Recommendations — Generation 7

**Supersedes:** gen 6 recommendations
**Current best:** 105 (Rokicki-Dogon Bose-Chowla AP q=107, mul=433, confirmed gen7)
**Confirmed:** VLNS from BEST_105 → INFEASIBLE at 106 (85+ trials, genuine infeasibility)
**Confirmed:** F₂(10000) = 105 with ~0.90 confidence (no published 106-mark construction anywhere)
**Remaining gap:** ~4 elements to theoretical upper bound (~109)
**Pipeline state:** Terminal convergence — one viable experiment remains

---

## Priority 0 — Structural Fixes (require orchestrator changes, not prompts)

### [REC-0A] Add `to_delete/` routing in Evaluator output

**What to change:** Add an `output/to_delete/` directory that the orchestrator reads during
`move_evaluator_outputs()`. Each file in `to_delete/` contains a list of absolute paths to
delete from the knowledge base. After processing, the orchestrator deletes the listed paths.

**Why:** `knowledge/facts/fact_002.md` and `knowledge/facts/fact_004.md` have been WRONG
since generation 0 and cannot be removed by any existing agent workflow. No orchestrator
routing path touches `knowledge/facts/`. The stale files will persist indefinitely without
this structural fix.

**Immediate fix (manual):** Delete `knowledge/facts/fact_002.md` and `knowledge/facts/fact_004.md`
directly. The corrected versions of both facts exist in `knowledge/ideas/active/` and in
the evaluator's gen6/gen7 updates. Removing the originals eliminates the data poisoning risk.

**Expected impact:** Eliminates the longest-standing data integrity failure in the pipeline.

---

### [REC-0B] Add `to_move/` routing in Evaluator output for file relocation

**What to change:** Add an `output/to_move/` directory. Each file contains `source: path`
and `destination: path` pairs. Orchestrator moves files during post-processing.

**Why:** `knowledge/ideas/active/pattern_009.md` and `knowledge/ideas/confirmed/pattern_011.md`
are in the wrong directory and cannot be moved by any existing workflow.

**Immediate fix (manual):** Move pattern_009.md to `knowledge/patterns/confirmed/` and
pattern_011.md to `knowledge/patterns/confirmed/`.

---

## Priority 1 — Critical (gen 8 must-do before agents launch)

### [REC-1] Gen 8 full_1 brief must include CP-SAT formulation INLINE

**What to change:** The gen 8 brief for full_1 (or whatever agent runs EXP-5) must include:

```
DO NOT read state_of_affairs.md or prior reports. Start immediately with the following code:

from helpers.cpsat import solve_sidon_cpsat
from problems.sidon.helpers.rokicki_data import BEST_105

# Binary variable maximize-k formulation
# Variables: x_i ∈ {0,1} for each i in {0,...,10000}
# Objective: MAXIMIZE sum(x_i)
# Constraints: for each sum s, at most one pair (i,j) with i<j, i+j=s, x_i=x_j=1
# Warm-start: x_i=1 for i in BEST_105, x_i=0 otherwise
# Time limit: 3600s, workers: 8

status, solution = solve_sidon_cpsat(k=None, N=10000, hint=BEST_105,
    time_limit=3600, num_workers=8, maximize=True)
```

**Why:** full_1 was interrupted during context reading for the SECOND consecutive generation.
The agent's own debrief says: "Skip context reading entirely and immediately implement." The
brief design is causing the failure. Providing the formulation inline eliminates the reading phase.

**Expected impact:** Executes the only remaining viable experiment that could either find 106
or definitively prove 105 optimal.

---

### [REC-2] Consistency Reviewer MUST run in gen 8

**What to change:** Force the Consistency Reviewer to run in gen 8 (override the 3-gen
interval if needed). The SoA is now factually wrong on 4 key points:
1. "VLNS: 0 valid trials (formulation bug)" → should be "85+ trials, INFEASIBLE genuine"
2. "CRITICAL: Fix abs-equality domain bug" → should be "no bug; infeasibility confirmed"
3. "helpers/cpsat.py still missing" → should be "delivered gen7, self-tested"
4. "idea_025 (Ruzsa-Lindström): 0 trials" → should be "tested, ceiling 75, same basin as ET"

Agents reading the current SoA will waste compute on a "CRITICAL" bug that doesn't exist.

**Expected impact:** Prevents one generation of misdirected work.

---

### [REC-3] Delete stale fact files immediately (pre-gen8 action)

**What to change:** Manually delete or overwrite:
- `knowledge/facts/fact_002.md` — says upper bound "~100-102" (WRONG: ~109)
- `knowledge/facts/fact_004.md` — says validator extracts subsets (WRONG: sentinel scoring)

These files have been wrong for 7 generations and flagged for 5. They are the highest
data integrity risk in the knowledge base. Any agent that reads them receives misinformation
that could fundamentally alter their strategy (believing the ceiling is 100-102 when it's ~109,
or believing invalid solutions get partial credit).

**Expected impact:** Eliminates active misinformation that has persisted 7 generations.

---

## Priority 2 — High Value (gen 8 strategic directions)

### [REC-4] Create helpers/extend.py before gen 8 agents launch

**What to change:** Assign experimentator or system operator to create
`problems/sidon/helpers/extend.py` with:
```python
def greedy_extend(base_set, N):
    """Extend a valid Sidon set greedily up to N."""
    s = set(base_set)
    diffs = set()
    for a in s:
        for b in s:
            if a != b:
                diffs.add(abs(a-b))
    for candidate in range(N+1):
        if candidate in s:
            continue
        new_diffs = {abs(candidate - x) for x in s}
        if not new_diffs & diffs and len(new_diffs) == len(s):
            s.add(candidate)
            diffs |= new_diffs
    return sorted(s)
```

**Why:** explore_1 and research_1 both flagged `helpers/extend.py` as missing for the
second consecutive generation. Every explore agent reimplements this inline. It is the
single most-requested helper after cpsat.py.

**Expected impact:** Saves 2-5 turns per explore/exploit session. Eliminates a class of
inline reimplementation bugs.

---

### [REC-5] Retire "look up F₂(10000)" from research_1 briefs

**What to change:** Remove all references to "find F₂(10000) via literature search" from
research_1 briefs. The question has been conclusively answered: it is not tabulated anywhere
accessible. The research agent has confirmed this via live web searches in gen7.

Replace with one of:
- "Investigate why BEST_105 has the self-healing property — is this a known algebraic result?"
- "Survey tabu search methods for combinatorial optimization — specifically swap-then-fill for
  constraint satisfaction"
- "Analyze the structure of Sidon sets near the theoretical upper bound"

**Why:** 7 generations of research attempts on this question have consumed compute with
diminishing returns. The question is inherently unanswerable with available tools.

**Expected impact:** Research slot becomes productive again.

---

### [REC-6] Define pipeline exit criteria

**What to change:** Add to `user/config.yaml` or CLAUDE.md:
```yaml
exit_criteria:
  - condition: "binary_cpsat_maximize_returns_INFEASIBLE_at_106"
    action: "halt — F₂(10000) = 105 confirmed computationally"
  - condition: "binary_cpsat_maximize_finds_106"
    action: "continue — record breakthrough, explore 107+"
  - condition: "plateau_generations >= 5 AND all_experiments_exhausted"
    action: "recommend halt to user"
```

**Why:** The Architect explicitly asked for exit criteria. Without formal criteria, the
pipeline may continue running well past the point of useful exploration. After gen8's
EXP-5, one of two outcomes defines the pipeline's future:
- INFEASIBLE → halt (F₂(10000) = 105 proven)
- Found 106 → major reorientation

**Expected impact:** Prevents indefinite compute waste after the search space is exhausted.

---

### [REC-7] Add VLNS-from-BEST_104 to gen 8 experiments

**What to change:** Add a VLNS trial from BEST_104 (Singer q=103, mul=400, 104 elements)
to either exploit_1 or explore_1 brief in gen 8.

**Why:** The self-healing property has been confirmed for BEST_105 only. If BEST_104 is also
self-healing, the property is structural (applies to all near-optimal Sidon sets in [0,10000]).
If BEST_104 VLNS finds a 105-element replacement that IS NOT BEST_105, we have a second
independently discovered 105-mark construction — which may have different algebraic properties.
Experimentator_1 specifically requested this in their gen7 debrief.

**Expected impact:** Takes <30min. Either confirms self-healing universality or finds new
105-mark construction. High information/cost ratio.

---

## Priority 3 — Process Improvements

### [REC-8] Distinguish "diagnosis proposed" from "diagnosis confirmed" in SoA

**What to change:** Add a convention to the State of Affairs: when an approach is labeled
as having a "bug" or "flaw," include a confidence label:
- `[DIAGNOSIS: proposed, 1 agent]` — plausible, unverified
- `[DIAGNOSIS: confirmed, N agents]` — multiple independent confirmations

**Why:** The gen6 VLNS "formulation bug" was labeled "CRITICAL" and "almost certainly" correct
based on one agent's analysis. Three gen7 agents independently refuted it. One generation of
compute was spent pursuing a phantom bug. The knowledge system needs better uncertainty markers.

---

### [REC-9] Carry forward from gen6 (still not confirmed resolved)

| From gen6 | Status |
|-----------|--------|
| REC-8: Single-agent ownership for external data fetches → Add to architect.md | **UNKNOWN** — not confirmed |
| REC-9: Add CP-SAT UNKNOWN decision rule → Add to full.md, exploit.md | **UNKNOWN** — full_1 spent turns on UNKNOWN-equivalent in gen7 |
| REC-10: Research cites sources or labels as "training data" → Add to research.md | **RESOLVED in gen7** — research_1 performed live searches and labeled OEIS, arXiv, cube20.org |

---

## Tracking: Gen 6 Recommendations Status

| Recommendation | Status | Notes |
|----------------|--------|-------|
| REC-1: Research web-first ordering | **RESOLVED** | research_1 performed live web searches (first time in 7 gens) |
| REC-2: VLNS formulation fix as gen7 priority | **RESOLVED** (finding: no bug) | exploit_1 confirmed 85+ trials INFEASIBLE, genuine |
| REC-3: Create helpers/cpsat.py | **RESOLVED** | experimentator_1 delivered, self-tested |
| REC-4: Update SoA before gen7 | **PARTIAL** | SoA not updated; Consistency Reviewer did not run gen7 |
| REC-5: Different CP-SAT formulation | **PARTIAL** | Binary VLNS used; binary maximize-k NOT run (full_1 failed) |
| REC-6: Archive stale ideas (idea_015, idea_016, idea_003) | **UNKNOWN** | Not mentioned in gen7 reports |
| REC-7: C-extension helper for validation | **NOT STARTED** | No experimentator slot available |
| REC-8: Single-agent ownership for data fetches | **UNKNOWN** | Not confirmed in architect.md |
| REC-9: CP-SAT UNKNOWN decision rule | **NOT STARTED** | full_1 still ran same-class formulations |
| REC-10: Research source labeling | **RESOLVED** | research_1 cited OEIS, arXiv, cube20.org URLs |
