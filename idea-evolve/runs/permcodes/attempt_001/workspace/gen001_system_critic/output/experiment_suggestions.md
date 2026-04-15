# Experiment Suggestions — Generation 2

## Pre-Generation Diagnostic Experiments

These experiments should run BEFORE launching any solution agents in gen 2, to confirm the pipeline is functional.

### EXP-DIAG-1: Helper Validation
**Hypothesis:** `helpers.agl18.max_clique_code()` correctly produces 616+ codewords.

**What to run:**
```python
import sys
sys.path.insert(0, '/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes')
from helpers.agl18 import max_clique_code
code = max_clique_code()
print(f"Code size: {len(code)}")
assert len(code) >= 616, f"Expected >= 616, got {len(code)}"
assert all(len(c) == 8 for c in code), "All codewords must be length 8"
from helpers.core import min_distance
d = min_distance(code)
assert d >= 5, f"Min distance {d} < 5"
print("PASS: AGL(1,8) helper produces valid code")
```

**Expected information gain:** Confirmation that the primary building block works. This is the single most important verification.

**If it fails:** The helpers are broken. Stop gen 2 and fix helpers first.

---

### EXP-DIAG-2: Fast Compatible Mask Validation
**Hypothesis:** `fast_compatible_mask` is faster and produces correct results.

**What to run:**
```python
import time
from helpers.core import compatible_permutations
from helpers.compat import fast_compatible_mask, build_all_perms, build_bucket_ids
all_perms = build_all_perms()
bucket_ids = build_bucket_ids(all_perms)
# Take first 100 codewords as a test set
test_code = all_perms[:100]
code_indices = [0] * 100  # indices into all_perms
start = time.time()
fast_result = fast_compatible_mask(code_indices, bucket_ids)
fast_time = time.time() - start
print(f"fast_compatible_mask: {fast_time:.3f}s, {len(fast_result)} compatible")
# Verify correctness against brute force on smaller subset
small_code = all_perms[:20]
small_indices = list(range(20))
brute_result = compatible_permutations(small_code, small_code)
fast_small = fast_compatible_mask(small_indices, bucket_ids)
print(f"Brute force: {len(brute_result)}, fast: {len(fast_small)}")
assert len(brute_result) == len(fast_small), "Results don't match!"
```

**Expected information gain:** Confirms speedup claim and correctness of `fast_compatible_mask`.

---

### EXP-DIAG-3: Agent Harness Smoke Test
**Hypothesis:** The agent harness (claude-code or opencode) can launch and produce output.

**What to run:**
- Launch a minimal test agent with a 60-second timeout
- Directive: "Write 'hello' to output/test.txt and report.md"
- Verify both files exist

**Expected information gain:** Confirms the pipeline can run agents. If this fails, no amount of agent prompt engineering will help.

---

## Solution Experiments (if Diagnostics Pass)

### EXP-SOL-1: Confirm AGL(1,8) Baseline (Priority 1)
**Hypothesis:** AGL(1,8) construction produces exactly 616 codewords.

**What to run:** `full_1` agent implementing:
```python
from helpers.agl18 import max_clique_code
def entrypoint():
    return max_clique_code()
```

**Expected information gain:**
- Confirms 616 is achievable
- Establishes the baseline for all optimization attempts
- If score ≠ 616, something is wrong with the helper

**Score range expected:** 616 (if helper works) or broken (if helper fails)

---

### EXP-SOL-2: ILS Small Destruction (Priority 2)
**Hypothesis:** ILS with destruction size k=30 can find codes larger than 616.

**What to run:** `explore_1` agent implementing ILS with k=30, 20 iterations.

**Expected information gain:**
- Whether 616 is a tight local optimum
- How often ILS finds codes > 616
- What destruction sizes are needed to escape the AGL local optimum

**Score range expected:** 616 (tight) to 650+ (ILS finds improvements)

---

### EXP-SOL-3: ILS Large Destruction (Priority 2)
**Hypothesis:** ILS with destruction size k=100 finds different local optima than k=30.

**What to run:** `explore_1` agent with k=100, 10 iterations.

**Expected information gain:** Whether larger destructions find better solutions (more diverse repair paths).

---

### EXP-SOL-4: AΓL(1,8) Alternative Group (Priority 2)
**Hypothesis:** AΓL(1,8) (semilinear group with Frobenius automorphism) produces different orbit structure and potentially larger codes than AGL(1,8).

**What to run:** `explore_2` implementing the AΓL(1,8) construction.

**Expected information gain:**
- Orbit size (168 vs 56 for AGL)
- Number of orbits (240 expected)
- Whether the max clique is larger or smaller than AGL's 11 orbits

**Score range expected:** Unknown. Could be > 616 or < 616 depending on orbit compatibility structure.

---

### EXP-SOL-5: Partial Orbit Mixing (Priority 3)
**Hypothesis:** Starting from the AGL(1,8) 11-orbit clique, adding partial orbits from other groups can exceed 616.

**What to run:** Modified ILS that allows taking partial permutations from non-clique orbits.

**Expected information gain:** Whether partial orbits are the key to breaking the 616 barrier.

**This is the highest-risk, highest-reward experiment.** If it works, it could push well beyond 616.

---

## Research Experiments

### EXP-RESEARCH-1: Group Theory Survey (Priority 1)
**Hypothesis:** Research agent can produce actionable findings about alternative algebraic groups.

**What to run:** `research_1` with directive to investigate:
- PGL(2,7) orbit structure
- PSL(2,7) vs PGL(2,7) distinction
- Known results on M(8,5) bounds post-2012

**Expected information gain:**
- Whether PGL(2,7) or PSL(2,7) has been tried in literature
- Whether any construction is known to exceed 616
- Algorithmic approaches from max-clique literature

**Failure mode:** Agent produces generic text without specific, actionable recommendations.

---

## Parameter Sweep Recommendations

If ILS shows promise (finds codes > 616 occasionally), the system should sweep:

| Parameter | Values to Try | Rationale |
|-----------|---------------|-----------|
| Destruction size k | {10, 20, 30, 50, 100, 200} | Find sweet spot for escape vs. rebuild |
| Number of iterations | {10, 50, 100, 500} | More iterations → better chance of escape |
| SA temperature | {0.1, 1.0, 10.0} | Affects acceptance of worse solutions |
| SA steps | {1000, 10000, 50000} | Longer runs may find better optima |

---

## Experiment Priority Matrix

| Experiment | Priority | Expected Info Gain | Risk of Failure |
|------------|----------|-------------------|-----------------|
| EXP-DIAG-1 (AGL helper) | P0 | Confirms baseline works | None (just validation) |
| EXP-DIAG-2 (fast_mask) | P0 | Confirms speedup | None (just validation) |
| EXP-DIAG-3 (harness) | P0 | Confirms pipeline | None (just validation) |
| EXP-SOL-1 (AGL baseline) | P1 | Score = 616 | Low (helper should work) |
| EXP-SOL-2 (ILS k=30) | P1 | Whether 616 is tight | Medium (ILS may not escape) |
| EXP-SOL-3 (ILS k=100) | P2 | Larger destruction value | Medium |
| EXP-SOL-4 (AΓL) | P2 | Alternative group results | High (implementation complex) |
| EXP-RESEARCH-1 | P1 | Actionable group theory | Medium (agents may be vague) |
| EXP-SOL-5 (partial orbits) | P3 | Novel construction | Very High (speculative) |

---

## What We'd Learn from a Successful Gen 2

**Best case:** Multiple agents produce validated solutions:
- AGL(1,8) confirms 616 baseline
- ILS variants find 617-700 range
- Research identifies promising next directions

**Partial success:** Some agents produce outputs:
- Only full_1 runs → confirmed 616 baseline
- Only explore_1 runs → ILS parameter guidance

**Failure mode:** Gen 2 repeats gen 1 failure:
- All agents fail again
- Pipeline diagnostics needed
- Potential systemic issue with agent harness
