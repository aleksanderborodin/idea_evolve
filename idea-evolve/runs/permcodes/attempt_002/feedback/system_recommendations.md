# System Recommendations — Generation 2

Priority-ordered list. Fix the most impactful problems first.

---

## R1 (CRITICAL): Fix knowledge persistence — move evaluator outputs to knowledge/

**What**: The orchestrator must move ideas, patterns, and clusters from evaluator workspace output to the knowledge base after evaluator completes. Specifically:
- `briefs/gen001/evaluator/output/new_ideas/*.md` → `knowledge/ideas/`
- `briefs/gen001/evaluator/output/new_patterns/*.md` → `knowledge/patterns/`
- `briefs/gen001/evaluator/output/new_clusters/*.md` → `knowledge/clusters/`

**Why**: Currently 14 ideas and 4 patterns are stranded in evaluator output. Gen 2 starts with the same empty knowledge base as gen 1. This is a pipeline contract violation — knowledge produced but not stored.

**Expected impact**: Gen 2 agents can read prior ideas and build on them. Eliminates redundant discovery of AGL baseline.

---

## R2 (CRITICAL): Architect must assign PGL(2,7) experiment as a dedicated agent task

**What**: The Architect's prompt must require that at least one agent in gen 2 is explicitly tasked with:
1. Deriving PGL(2,7) elements as permutations of {0,...,7} via Möbius transformations over GF(7)∪{∞}
2. Computing PGL(2,7) orbit partition (120 orbits of 336 perms)
3. Building the 120×120 compatibility graph
4. Running max-clique search (target: >11 orbits = >616 codewords)

This should be a **full** or **experimentator** agent — not research. Research should complete in gen 1. Gen 2 needs execution.

**Why**: PGL was identified as the single most promising direction in gen 1. It was fully described (research_1 findings.md has explicit implementation sketch). Zero agents executed it. The pipeline needs enforcement, not just description.

**Expected impact**: If PGL orbit clique >11, we beat the known 616 lower bound — the first improvement in the problem's known optimum. If ≤11, we know PGL is not the answer and can pivot.

---

## R3 (HIGH): Run the compatible-permutation count immediately

**What**: Before gen 2 agents start, a quick experiment should be run:
```python
code = agl18_max_clique_code()  # 616 codewords
code_indices = find_codeword_indices(code, all_perms)  # needs helper or workaround
compatible_mask = fast_compatible_mask(code_indices, bucket_ids)
extra_count = compatible_mask.sum() - 616
```

**Why**: This binary fact determines the entire gen 2 strategy:
- If extra_count > 0: there are extendable permutations → SA/VNS approaches are viable
- If extra_count = 0: the 616-code is truly isolated → PGL is mandatory, SA/VNS are waste of time

Currently we don't know. The evaluator identified this as "the key empirical question" and never ran it.

**Expected impact**: Eliminates wasted agent compute on the wrong strategy. Enables informed allocation of agent effort.

---

## R4 (HIGH): Reduce AGL redundancy in gen 2

**What**: Architect should assign at most 1 agent to AGL variants. The architect's brief already flagged homogeneity risk (`architect.md:49-58`). The orchestrator should enforce it:
- If manifest has >1 agent doing AGL orbit clique, flag a warning
- Alternatively: give the Architect visibility into how many agents are doing each idea (via coverage matrix summary in the brief)

**Why**: AGL direction is confirmed at its limit (11 orbits = 616). Additional AGL agents will produce 616 again. Redundant compute.

**Expected impact**: Frees agent slots for PGL, VNS, SA, or cross-group experiments.

---

## R5 (HIGH): Add `find_codeword_indices` helper

**What**: In `helpers/compat.py`, add:
```python
def find_codeword_indices(code, all_perms):
    """Return indices of codewords in the all_perms array."""
    # code is array of permutations, all_perms is (40320, 8)
    # Return indices for use in fast_compatible_mask
```

Or equivalently, modify `fast_compatible_mask` to accept the code array directly (not indices) so agents don't need the mapping.

**Why**: `research_1.md:56` and `evaluator.md:178` both note this helper is missing. Agents needed it for the compatible-permutation count experiment and work-arounded it instead of running the experiment.

**Expected impact**: Enables agents to run the compatible-permutation count experiment. This is prerequisite for informed SA/VNS strategy selection.

---

## R6 (MEDIUM): Fix GA crossover operator design

**What**: Redesign the crossover operator before gen 2 genetic agents run. Current union+prune loses too many codewords (`agent_gaps/gen001.md:39-43`). Suggested alternatives:
- Orbit-level crossover: crossover selects which orbits to include from each parent, then fills within orbits
- Compatibility-preserving crossover: only combine codewords that are mutually compatible
- Two-point crossover on the sorted orbit representation

**Why**: Genetic is an important search paradigm. With the current operator design, any genetic agent attempting crossover will fail. The genetic direction is dead unless the operator is fixed.

**Expected impact**: Enables a genetic search direction that doesn't exist today.

---

## R7 (MEDIUM): Add sanity-check requirement to agent prompts

**What**: Agent prompts (explore, exploit, full, genetic) should instruct agents to run basic validation before marking a solution complete:
```python
# Before submission, run:
assert len(code) >= expected_min, f"Code too small: {len(code)}"
assert check_code(code), "Code failed validation"
```

**Why**: Two solutions crashed due to trivial bugs (dtype error, logic error returning all perms). Basic sanity checks would catch these before evaluation, saving agent evaluation cycles.

**Expected impact**: Reduces invalid solution rate. Currently 2/12 = 17% failure.

---

## R8 (MINOR): Fix compatible_mask docstring in compat.py

**What**: The docstring example shows `compatible_with_code` but the function is `compatible_mask`. Fix the example to match the actual function name.

**Why**: Low impact but creates confusion. `explore_1.md:48` notes "confusing naming." This is a 1-line fix in the docstring.

**Expected impact**: Minor friction reduction for agents reading helper documentation.

---

## R9 (MINOR): Clarify brief target score

**What**: Update the brief template to show the actual situation: known lower bound = 616, upper bound = 926, target = beat 616. Not "target 624" with no explanation of why 624 is special.

**Why**: Misleading target could cause a naive agent to stop at 624 instead of pushing higher. Currently agents correctly identified the situation, but the brief should be accurate.

**Expected impact**: Prevents confusion in future problems with similar bound structure.

---

## R10 (LOW): Populate problem/initial_programs/ or acknowledge it's not used

**What**: Either populate `problem/initial_programs/` with reference implementations, or remove the reference from agent prompts. `explore_2.md:16` notes the directory was empty and caused confusion.

**Why**: Empty directory with no explanation wastes agent time investigating it.

**Expected impact**: Minor friction reduction.

---

## Priority Summary

| Priority | Recommendation | Expected Impact |
|----------|----------------|-----------------|
| CRITICAL | R1: Fix knowledge persistence | Gen 2 starts with accumulated knowledge |
| CRITICAL | R2: Assign PGL as dedicated agent task | Executes the top strategic direction |
| HIGH | R3: Run compatible-permutation count | Binary strategy decision: SA vs PGL |
| HIGH | R4: Reduce AGL redundancy | Frees compute for unexplored directions |
| HIGH | R5: Add find_codeword_indices helper | Enables critical experiment |
| MEDIUM | R6: Fix GA crossover operator | Opens genetic search direction |
| MEDIUM | R7: Add sanity-check requirement | Reduces invalid solution rate |
| MINOR | R8: Fix compatible_mask docstring | Minor friction reduction |
| MINOR | R9: Clarify brief target score | Accurate guidance |
| LOW | R10: Populate initial_programs/ | Minor friction reduction |