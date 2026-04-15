# Manifest Reasoning — Generation 1

## Situation Assessment

**Generation 1 cold start.** Only one solution exists: the greedy baseline (`gen000/baseline/sol01.py`)
with fitness = 262. No clusters, no knowledge base, no prior agent reports.

The problem is M(8,5): find the largest permutation code of length 8 with min Hamming
distance ≥ 5. The target is 624 (beating the known lower bound of 616).

**Key infrastructure already available:**
- `helpers/agl18.py` — Provides `agl18_max_clique_code()` which directly achieves 616
  using the AGL(1,8) orbit clique construction (takes ~4s). This is the fastest known
  path to a state-of-the-art solution.
- `helpers/compat.py` — Fast bucket-based compatibility checking (23x faster than naive),
  enabling rapid search over all 40320 permutations.
- `helpers/core.py` — Basic Hamming distance, check_code utilities.

The greedy baseline score of 262 is far below the algebraic optimum of 616. Generation 1's
primary goal is to close this gap immediately using the available infrastructure, while also
exploring whether non-algebraic approaches can compete.

---

## Agent Mix Rationale

**Cold start rules mandate: 2 explore + 1 full + 1 research.** This is exactly what I've assigned.

### full_1 (sonnet, 2700s)
**Role:** Reliable 616+ baseline using the AGL(1,8) construction.

The full agent has the most direct path to quality: call `agl18_max_clique_code()` → 616.
Then attempt greedy extension using `fast_compatible_mask` to find individual permutations
compatible with the entire 616-code. Even adding 1 permutation (→ 617) would be a new record.

**Why full and not exploit:** No exploit agents in generation 1 (cold start rule — nothing
to refine yet). The full agent serves as the "get a good baseline fast" role.

### explore_1 (sonnet, 2700s)
**Role:** Orbit-level exhaustive search to find larger cliques in the AGL orbit graph.

The standard `agl18_max_clique_code()` only tries 50 starting vertices out of 720 orbits.
A full exhaustive greedy search over all 720 starting vertices has a real chance of finding
a 12-orbit clique (→ 672 codewords). This is a high-value, well-defined search task.

Additionally, perturbation-based clique improvement (remove 1-3 orbits, rebuild) may find
larger cliques than the greedy baseline.

**Distinguishing from full_1:** full_1 uses the standard `agl18_max_clique_code()` as a
black box and focuses on individual-perm extension afterward. explore_1 opens up the orbit
graph and searches more deeply at the orbit level.

### explore_2 (sonnet, 2700s)
**Role:** Track B radical exploration — non-algebraic ILNS on raw permutation space.

This agent must NOT use AGL group structure. It implements Iterated Large Neighborhood Search
(ILNS) directly on the 40320-perm space using `helpers/compat.py` for fast compatibility
checking. Key questions:
- Can non-algebraic ILNS approach 616 without group theory?
- What code sizes does stochastic search find? 400? 550? 600?
- If ILNS reaches e.g. 580, it's useful context. If it reaches 616+, it's a breakthrough.

The results will inform how much algebraic structure is "necessary" vs "convenient." If ILNS
reaches 590-616 range, future agents can combine algebraic seeding with ILNS refinement.

**Why this is genuinely different from explore_1:** explore_1 works entirely within the AGL
orbit framework. explore_2 abandons group theory entirely and works in raw permutation space.

### research_1 (sonnet, 2700s)
**Role:** Survey what's known about going beyond M(8,5) = 616.

The system needs to know:
1. Whether any published work has achieved M(8,5) > 616
2. What alternative group-theoretic constructions are known (PGL, PSL, Mathieu)
3. What stochastic algorithms have been applied to permutation codes and with what results
4. Whether LP/IP formulations are feasible for this problem size

Findings feed directly into generation 2 agent briefs.

---

## What I Deliberately Did NOT Do

**No exploit agent:** Cold start rules forbid it. Nothing to refine yet.
**No genetic agent:** Needs 2 parents; we only have a 262-score baseline.
**No experimentator:** Too early. No baseline established to experiment against.

**No more than 4 agents:** Budget discipline. 4 agents saturate the logical work of
generation 1 (baseline, algebraic extension, non-algebraic search, literature).

---

## Timeout Rationale

All agents get the default 2700s (45 minutes). Reasoning:
- `agl18_orbits()` takes ~1s, `agl18_compat_graph()` takes ~4s. Most computation is in
  the search, not setup.
- explore_1 may need significant time for 720-vertex orbit search (minutes).
- explore_2 ILNS needs many iterations (hundreds of destroy-repair cycles).
- research_1 is I/O bound (reading files, thinking), likely finishes within 1800s.
- No timing data from previous generations — using defaults is correct.

---

## Risks and Contingencies

**Risk 1 — explore_1 search is too slow:**
720-vertex orbit graph search: each vertex requires scanning ~138 candidates with inner
degree computation. Estimated runtime: ~720 * 138 * 138 / 2 ≈ 7M operations. In Python,
this could be 5-10 minutes. Should complete within 2700s, but may need to time-box.
*Contingency:* explore_1 directive includes a time-box instruction.

**Risk 2 — explore_2 ILNS doesn't approach 616:**
If ILNS without group structure only reaches ~400-500, that's still useful information.
We learn that the AGL structure is essential and pure stochastic search is insufficient.
*Contingency:* Still valuable as a null result. Informs generation 2 strategy.

**Risk 3 — full_1 finds no extensions beyond 616:**
The 616-code might be maximal in the individual permutation sense (all compatible single
perms are already in it). In that case, full_1 just confirms 616 as a local maximum and
documents that extension isn't straightforward.
*Contingency:* Still useful. Establishes 616 as a solid baseline for generation 2.

**Risk 4 — No agent beats 616 in generation 1:**
Likely! This is a hard combinatorial problem. Generation 1 aims to establish 616 and
understand the search landscape. Beating 616 would be a bonus.

---

## Expected Outcomes

- **high confidence:** full_1 and explore_1 both reach 616 via AGL construction
- **medium confidence:** explore_1 finds evidence about whether orbit cliques > 11 exist
- **medium confidence:** explore_2 reaches 400-550 via ILNS
- **high confidence:** research_1 identifies concrete approaches for generation 2

The knowledge base will be bootstrapped from agent debrief reports, giving generation 2
clusters and ideas to work from.
