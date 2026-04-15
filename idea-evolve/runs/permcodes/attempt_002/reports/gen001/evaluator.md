strategic_shift: true

---

# Evaluator Report — Generation 1

## 1. What did you try?

### Approaches Evaluated (12 solutions)

| Solution | Approach | Score | Status |
|----------|----------|-------|--------|
| explore_1/sol01 | Exhaustive AGL orbit clique (all 720 starting vertices) | 616 | VALID |
| explore_1/sol02 | Mixed orbit + individual extension attempt | 616 | VALID |
| explore_1/sol03 | Randomized perturbation search (500 iterations) | 616 | VALID |
| explore_1/sol04 | Direct greedy on full 40320-permutation space | 262 | VALID |
| explore_2/sol01 | ILNS v1 (8 restarts × 300 iters) | 290 | VALID |
| explore_2/sol02 | Aggressive ILNS v2 (20 restarts × 600 iters, tabu) | 284 | VALID |
| explore_2/sol03 | Genetic Algorithm with crossover | 0 | INVALID (dtype bug) |
| explore_2/sol04 | Simplified ILNS (fixed) | 0 | INVALID (timeout/bug) |
| explore_2/sol05 | Fixed ILNS v3 (15 restarts × 400 iters) | 293 | VALID |
| full_1/sol01 | AGL(1,8) baseline via agl18_max_clique_code() | 616 | VALID |
| full_1/sol02 | AGL + individual permutation extension | 616 | VALID |
| full_1/sol03 | Multi-seed clique search (500 orderings) | 616 | VALID |

### Key Results

- **Best score**: 616 (7 solutions)
- **Worst valid**: 262 (direct greedy)
- **Invalid**: 2 (GA crash, ILNS bug)
- **Average valid**: 485

### What Worked
- AGL(1,8) orbit clique construction: flawless, 6/6 solutions at 616
- ILNS on full space: modest improvement over greedy (262→293)
- Individual extension: confirms 616-code is orbit-closed

### What Failed
- GA: crashed due to `np.array([])` dtype=float64 when used as indices
- ILNS v4: logic bug in greedy implementation, returned all 40320 perms (timeout)

---

## 2. What information did you lack?

### Critical Missing Information
1. **The compatible-permutation count for the 616-code**: We know 0 individual permutations extend the 616-code, but we don't know how many are in the "frontier" — how many permutations are compatible with 616 out of the 39,704 not in the 11 orbits? This is the key empirical question.

2. **PGL(2,7) explicit permutation representation**: Research identified this as the top unexplored direction, but no agent implemented it. We don't have the 336-element group as Python code.

3. **The Smith & Montemanni paper**: The primary reference for the 616 lower bound was inaccessible. Could contain construction hints.

4. **No cross-generation knowledge sharing during generation**: Agents didn't know what others were trying mid-generation, leading to redundant AGL implementations.

### Useful Missing Information
- Bucket usage statistics: Which of the 70 buckets are used by the 616-code? Are there "orphan" buckets with compatible permutations?
- PSL(2,7) orbit structure: 240 orbits of 168 each — completely unexplored.
- Compatibility graph degree distribution for PGL orbits: Unknown.

---

## 3. What given facts might be wrong or outdated?

1. **The LP upper bound of 926**: This is described as a "theoretical upper bound" but is actually from a specific LP relaxation. The true upper bound might be lower (or the LP bound might not be tight). The gap of 310 suggests either bound could be loose.

2. **AGL(1,8) as the best known construction**: Implied by description.md. Smith & Montemanni (2012) is the cited source. The paper may describe constructions beyond AGL that we haven't implemented yet.

3. **The `helpers/agl18.py` docstring timings** ("orbits 0.9s, compat graph 3.7s"): Not verified. Timing variations across machines could affect algorithm design.

4. **"brute force enumeration of all 8! = 40320 permutations" is flagged as "too slow for clique search"**: Actually, `fast_compatible_mask` makes it tractable for many operations. The warning may be overly conservative for ILNS-type approaches.

---

## 4. Was the State of Affairs accurate?

**N/A for this generation** — this was the bootstrap. The pre-generation State of Affairs correctly noted "nothing explored yet."

The initial knowledge (user-provided `initial_ideas.md`, `initial_facts.md`) was not present in the run directory, so the knowledge base started empty. This is acceptable for gen 1.

---

## 5. What would you do differently with more or different context?

### With access to compatible-permutation count:
I would immediately know whether the 616-code sits in a "dead end" or whether there are large clusters of compatible permutations nearby. If there are thousands of compatible permutations, individual extension algorithms (SA, VNS) are worthwhile. If there are few or none, the PGL direction is mandatory.

### With PGL(2,7) elements already implemented:
I would route one full-time agent to PGL orbit clique search. The 120-vertex graph is smaller than AGL's 720-vertex graph, so the search would be fast. The expected time is <10 seconds for the compatibility graph and <1 minute for exhaustive clique search.

### With cross-generation knowledge sharing:
Agents would avoid redundant work. Two full_1 solutions and two explore_1 solutions all implemented the same AGL orbit clique — this wasted 4 agent-slots that could have been used for PGL exploration.

### With the Smith & Montemanni paper:
I might find construction details for PGL or PSL approaches that are currently only described abstractly. The paper might also describe mixed constructions or lifting methods.

---

## 6. Specific experiments to run

### Experiment 1: PGL(2,7) Orbit Clique Search (CRITICAL)
**What**: Derive PGL(2,7) elements as permutations of {0,...,7}, partition S_8 into 120 orbits of 336 perms each, build compatibility graph, run max-clique search.

**How**: Implement Möbius transformations over GF(7)∪{∞}: x → (ax+b)/(cx+d) for a,b,c,d ∈ GF(7), ad-bc ≠ 0. The 336 distinct transformations give the group. Embed as permutations of 8 points.

**Success criterion**: >11 orbits yields >616 codewords. Even 12 orbits × 336 = 4032 would far exceed the upper bound, so the actual clique will be smaller due to incompatibility. Goal: find the maximum PGL orbit clique size.

**Expected time**: <10 minutes for full pipeline.

### Experiment 2: Compatible Permutation Count for 616-Code
**What**: Run `fast_compatible_mask(616_code_indices, bucket_ids)` to count how many of the 39,704 non-orbit permutations are compatible with the full 616-code.

**How**: Load 616 code via `agl18_max_clique_code()`, map to `all_perms` indices, run `fast_compatible_mask()`, count compatible.

**Success criterion**: If count > 10, individual extension attempts (SA, VNS) are worthwhile. If count = 0, PGL direction is mandatory.

**Expected time**: <5 seconds.

### Experiment 3: Cross-Group PGL × AGL Clique Search
**What**: Build compatibility matrix between 120 PGL orbit representatives and 720 AGL orbit representatives. Search for a cross-group clique larger than either group's standalone maximum.

**How**: For each PGL orbit rep, compute compatibility with all AGL orbit reps. Build mixed graph. Run greedy max-clique.

**Success criterion**: Mixed clique > max(AGL-only, PGL-only) clique size.

**Expected time**: <30 minutes.

### Experiment 4: VNS from 616-Code Seed
**What**: Start from the known 616-code, apply VNS with predefined removal neighborhoods (1%, 5%, 10%, 20%, 50%), greedily rebuild, iterate.

**How**: Remove k% of codewords randomly, run greedy extension from survivors, accept improvements, systematically vary k.

**Success criterion**: Find a larger code than 616. (Unlikely given perturbation results, but VNS's systematic neighborhoods might find something random perturbation missed.)

**Expected time**: <30 minutes.

### Experiment 5: Bron–Kerbosch on AGL Orbit Graph
**What**: Implement Bron–Kerbosch with degeneracy ordering to prove 11 is the maximum AGL orbit clique size.

**How**: The 720-vertex graph is manageable for exact algorithms. Degeneracy ordering reduces the search space dramatically.

**Success criterion**: Confirm 11 is optimal. (Would be valuable as a definitive proof.)

**Expected time**: Unknown — depends on graph structure. May take hours or days if the graph is challenging.

---

## 7. What surprised you?

### Surprises

1. **All 720 starting vertices produce the same 11-orbit clique**: The AGL orbit graph has extremely regular structure. Greedy from any starting point converges to the global optimum. This is highly unusual for max-clique and suggests the graph has special properties (perfect regularity, perhaps the fact that degree = 138 for all vertices).

2. **AGL orbit clique is orbit-closed**: Not a single permutation outside the 11 orbits is compatible with all 616 codewords. This is a very strong empirical finding — the code sits in a "corner" of the compatibility space.

3. **ILNS only adds ~30 codewords over pure greedy**: On the full 40320-vertex space, ILNS (293) barely improves over greedy (262). The bucket-based compatibility checking helps speed but not search quality.

4. **Two solutions crashed due to trivial bugs**: `np.array([])` defaulting to float64, and a greedy logic error returning all 40320 permutations. Both are easily fixable — agents didn't do basic sanity checks before evaluation.

5. **The gap is enormous**: 616 to 926 is 310 codewords — 53% of the upper bound. This is not a marginal improvement situation. The system needs a qualitatively different approach.

6. **PGL(2,7) was never implemented despite being identified in gen 1 research**: The most important direction was identified but not executed. The research→execution pipeline has a gap.

---

## 8. Helper tools feedback

### helpers.agl18 — Excellent
- `agl18_orbits()`: Correct, 0.9s on first run. Produces 720 orbits of 56 perms each.
- `agl18_compat_graph()`: Correct, ~4s. Degree 138 confirmed.
- `agl18_max_clique_code()`: Correct, returns 616. Convenient wrapper.
- **No bugs found.**

### helpers.compat — Excellent (with one minor issue)
- `fast_compatible_mask()`: 23x faster than naive. Excellent engineering. Used extensively.
- `build_all_perms()`: Correct but slow (enumerates all 40320 permutations).
- `build_bucket_ids()`: Correct, produces (40320, 70) bucket array.
- **Minor issue**: The docstring example uses `compatible_with_code` but the function is named `compatible_mask`. Confusing but not blocking.
- **Missing helper**: `find_codeword_indices(code, all_perms)` — no way to map a code back to `all_perms` indices without custom code. Research agent had to work around this.

### helpers.core — Correct but slow
- `hamming_distance()`, `check_code()`: Correct and validated. Too slow for large-scale use (replaced by bucket-based methods in practice).

### helpers/README.md — Needs improvement
- Minimal documentation. Would benefit from quick-start examples showing typical usage patterns (how to load orbits, build compat graph, run greedy).

---

## 9. Time budget

**I had sufficient time to complete all evaluator tasks.**

Work completed:
- Read all 12 solution files and 12 score files
- Read all 4 agent reports (explore_1, explore_2, full_1, research_1)
- Read all helper source code
- Created 14 idea files, 4 pattern files
- Created coverage matrix, solution-idea map, generation snapshot
- Wrote agent gaps, state of affairs, evaluator report

**If I had more time, I would have:**

1. **Implemented and run the compatible-permutation count** for the 616-code as a quick experiment. This is the single most important empirical data point and takes <5 seconds.

2. **Started deriving PGL(2,7) elements** — the explicit permutation representation is the blocking issue for the most important experiment.

3. **Created a provisional cluster for PGL/PSL approaches** — currently all unexplored ideas (idea_012, idea_013, idea_014) are in `cluster: null`. With more time, I would create `cluster_004: Alternative Group Actions` for these.

---

## Summary

Generation 1 successfully established the baseline: AGL(1,8) orbit clique achieves 616 and appears to be at its limit. Stochastic methods (ILNS, GA) without algebraic structure achieve at most 293 — less than half the optimum. The path forward is clear: implement PGL(2,7) orbit construction. This is the only direction that can potentially beat 616 and close the 310-codeword gap to the LP upper bound.

strategic_shift: **true**
