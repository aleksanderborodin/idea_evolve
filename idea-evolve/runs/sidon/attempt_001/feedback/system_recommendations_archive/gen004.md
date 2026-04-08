# System Recommendations — Generation 4

Prioritized by expected impact. Supersedes gen 3 recommendations.

---

## PRIORITY 1 (Critical — Act Before Gen 5 Agents Launch)

### REC-1: Fix Agent Permission Mode to Auto-Approve Workspace Writes

**What to change**: Ensure agent sessions are launched with a permission mode that
auto-approves Write and Edit operations within the agent's workspace directory. The
current configuration apparently permits the first Write but then prompts for approval
on subsequent Edit calls — which blocks headless sessions permanently.

**Concrete action**: In `user/config.yaml` or the orchestrator launch logic, ensure the
`--allowedTools` flag (or equivalent) is paired with a permission setting that doesn't
require per-call interactive approval. If running in a permission mode that prompts the
user, switch to auto-approval for workspace paths or pre-authorize the workspace directory.

**Why**: explore_1's entire session was wasted because it could not edit its own output
files after the first Write. A 1-element bug went unfixed, evaluate.py never ran, no
iterations happened. This is a total waste of an agent slot.

**Expected impact**: Prevent agent slot waste from permission blocking. HIGH probability
of recurrence if not fixed.

---

### REC-2: Assign a Dedicated Data-Fetch Task for Rokicki-Dogon Database

**What to change**: Assign one agent (experimentator or research) in gen 5 with a single,
concrete mission:

```
MISSION: Download cube20.org/golomb-all-00.zip and extract 104-mark and 105-mark
Sidon set entries for spans ≤ 10000.

Step 1: wget/curl cube20.org/golomb-all-00.zip to workspace
Step 2: Parse the zip to find entries with marks=104 and marks=105
Step 3: Extract the integer mark sequences (convert from whatever format the zip uses)
Step 4: Write each sequence to output/sol_rokicki_104.py and output/sol_rokicki_105.py
        in the standard solution format
Step 5: Run evaluate.py on each
```

This is a pure data-engineering task, not a research task. It requires no mathematical
insight — just downloading and parsing a known file.

**Why**: research_1 was 20 minutes away from a 104-105 score. Four consecutive generations
have approached this data without completing the fetch. The pipeline is 3 elements behind
the published state of the art because we haven't downloaded a file.

**Expected impact**: Jump from score 102 to 104 or 105 in a single agent session.
This is the highest-ROI action available to the pipeline.

---

### REC-3: Force a Consistency Review Before Gen 5 Agents Launch

**What to change**: Execute the Consistency Review phase before gen 5 agent work begins.
Set `consistency_review_interval: 1` temporarily in `user/config.yaml`, or have the
orchestrator trigger it as a mandatory pre-condition for gen 5.

**Why**: The State of Affairs (last updated gen 3) does not reflect:
1. CP-SAT ILP formulation (idea_019) — agents need to know this exists and is validated
2. Rokicki-Dogon constructive lower bound of 105 (idea_020) — changes the gap framing
3. Multi-Singer hybrid debunked (idea_013) — prevents agents from wasting time on it
4. Greedy ceiling confirmed at 69 (pattern_011) — establishes baseline for comparison
5. Singer suboptimal for small N (pattern_012) — important for ILP strategy

Gen 5 agents operating without these updates will have a materially wrong picture of
where the pipeline stands and what directions have been closed.

**Expected impact**: All gen 5 agents start with accurate L0 context. High value given
the size of the gen 4 knowledge update.

---

### REC-4: Delete Stale Fact Files in knowledge/facts/ (3rd Generation Without Cleanup)

**What to change**: Delete `knowledge/facts/fact_002` and `knowledge/facts/fact_004`.
These files contain wrong information that has been known-wrong since gen 3:
- fact_002: states upper bound ~100-102 (correct: ~109)
- fact_004: states validator extracts valid subsets (correct: sentinel scoring, no partial credit)

The corrected versions exist in `knowledge/ideas/active/` and are authoritative.

**Concrete action**: This cannot be done via agent prompt warnings — it requires the
Architect (or a pre-gen-5 orchestrator action) to explicitly delete these files. If
agents keep browsing `knowledge/facts/` they will keep finding the wrong information.

**Why**: explore_2 was explicitly misled by fact_002 in gen 4 (reported the wrong upper
bound in its debrief). REC-4 from gen 3 went unimplemented. Warnings in briefs are not
sufficient — agents read files and trust them.

**Expected impact**: Eliminates ongoing knowledge corruption. Prevents gen 5+ agents from
starting with false beliefs about the problem bounds.

---

## PRIORITY 2 (High — Unlock Next Score Tier)

### REC-5: Assign Beam Search Greedy to One Agent in Gen 5

**What to change**: Brief one explore or exploit agent specifically on beam search greedy:

```
Implement beam_search_sidon(N, k_beams, seed=None):
  - Maintain k_beams partial Sidon sets simultaneously
  - At each step, for each beam: enumerate all valid extensions
  - Keep the k_beams sets with the best heuristic score (e.g., min blocking count)
  - Return the best set found

Parameters to try: k_beams = 20, 50, 100
Expected score: 75-85 based on multiple independent estimates
```

**Why**: This direction has been flagged by agents across gens 3-4 as the most promising
untested non-algebraic approach. Expected score 75-85 would set a new non-algebraic ceiling
and validate/disprove the "greedy ceiling is 69" hypothesis. It costs one agent slot.

**Expected impact**: First confirmed non-Singer score above 70. Resolves a 3-generation
knowledge gap about non-algebraic search ceilings.

---

### REC-6: Create solve_sidon_cpsat Helper (Experimentator Task)

**What to change**: Assign an experimentator to package full_1's CP-SAT formulation as
`problem/helpers/cpsat_sidon.py` with function signature:

```python
def solve_sidon_cpsat(k, N, hint=None, time_limit=60, num_workers=8):
    """
    Try to find a k-element Sidon set in {0,...,N}.
    Returns (status, elements) where status is 'FEASIBLE'/'INFEASIBLE'/'UNKNOWN'.
    hint: optional list of elements to use as warm start.
    """
```

**Why**: full_1 and evaluator both independently requested this. The current formulation
is non-obvious and took full_1 significant session time to develop. Future agents using
ILP (the current highest-priority exact direction) will re-derive it from scratch without
this helper. This is exactly the recurring helper need pattern from DESIGN-11.

**Expected impact**: Future ILP experiments start 20-30 turns sooner. CP-SAT becomes
a reusable primitive rather than a one-generation discovery.

---

### REC-7: Schedule an Extended CP-SAT Run Outside Normal Agent Sessions

**What to change**: Run the CP-SAT k=103 search for 4+ hours with 16 workers. This
cannot be done within the normal 900s agent session budget. Options:
1. Orchestrator runs evaluate.py / a standalone script directly with extended timeout
2. A special "long-run" agent session with 4-hour wall clock budget
3. Background process with output written to workspace when done

**Why**: full_1's UNKNOWN result after 600s means k=103 is neither proven possible nor
impossible. A 4+ hour run with more workers may be the difference between UNKNOWN and
FEASIBLE/INFEASIBLE. This is a time-bounded question with a definitive answer.

**Expected impact**: Either (a) proof that 103 is infeasible, closing the ILP direction
below 103, or (b) a 103-element solution, beating the current best. Both are high-value.

---

### REC-8: Investigate "Singer+1" Structure at Small N

**What to change**: Assign one agent (full or exploit) to analyze the ILP-optimal sets
found by full_1:
- N=56 (q=7): Singer=8, ILP optimal=10. What are the 10 elements? How do they differ from Singer?
- N=132 (q=11): Singer=12, ILP finds 13. Same question.
- N=306 (q=17): Expected Singer=18, ILP optimal=?

The goal is to identify a pattern in the "extra" elements that ILP finds beyond Singer.
If there's a generalizable construction rule, it might give 103+ for N=10000.

**Expected impact**: Either reveals a new construction family (potentially high value)
or confirms that Singer+k is not algebraically principled (closes this direction).

---

## PRIORITY 3 (Moderate — Process Hygiene)

### REC-9: Save Singer-102 Set as JSON Seed (3rd Generation Without Implementation)

**What to change**: Extract the 102-element Singer q=101 set (optimal shift d=2337) and
save to `knowledge/seeds/sidon_102.json`. This was REC-10 (gen 3) and REC-6 (gen 2).

**Concrete action**: Run `population/best.py` (or equivalent Singer generator), capture
the element list, save to seeds directory. This is a 2-minute task.

**Why**: CP-SAT warm-start hints, difference analysis, Singer+1 structure analysis — all
require the explicit element list. Currently agents re-derive it each time from solution
files.

---

### REC-10: Archive idea_005 (Backtracking with Pruning) or Assign It

**What to change**: Either (a) test idea_005 in gen 5 (brief one explore agent on it),
or (b) formally move it to `knowledge/ideas/disputed/` with a note that beam search
(idea_015?) is the preferred approach and backtracking-only is computationally impractical
at N=10000.

**Why**: This idea has been in the knowledge base since gen 0 with last_confirmed_gen=0.
Four generations of staleness without testing or archiving creates noise in the coverage
matrix. Beam search (a more general form of backtracking) should supersede it.

---

## What Was Recommended Previously and Remains Unimplemented

| Rec | Gen | Status | Note |
|-----|-----|--------|------|
| Force Consistency Review | gen 3 REC-1 | ❌ STILL NEEDED | Now critical for gen 5 |
| Delete stale fact files | gen 3 REC-4 | ❌ STILL NEEDED | explore_2 misled in gen 4 |
| Save Singer-102 as JSON | gen 3 REC-10 | ❌ STILL NEEDED | 3rd generation without action |

## What Was Recommended and Implemented

| Rec | Gen | Status |
|-----|-----|--------|
| Incremental output for research agents | gen 3 REC-2 | ✅ research_1 wrote findings.md |
| ILP with correct formulation | gen 3 REC-5 | ✅ full_1 succeeded |
| Create idea for ILP/CP-SAT | gen 3 REC-6 | ✅ idea_019 created |
| Architect assigns orthogonal strategies | gen 3 | ✅ four distinct approaches this gen |
