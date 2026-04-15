# Manifest Reasoning — Generation 1

## Situation Assessment

**Starting point:** Greedy baseline at 262 codewords (gen000). No knowledge base, no clusters, no explored ideas. Cold start.

**Problem landscape:**
- M(8,5): maximize permutation code size in S₈ with min Hamming distance ≥ 5
- Known bounds: 616 ≤ M(8,5) ≤ 926
- Target in metrics.yaml: 624 (just above the known lower bound)
- Baseline score 262 is well below the known achievable lower bound of 616

**Key asset already available:** `helpers/agl18.py` is a complete, validated implementation of the AGL(1,8) orbit clique construction that achieves exactly 616 codewords. This is the state-of-the-art lower bound from Smith & Montemanni (2012). We can jump from 262 to 616 in generation 1 without any research — it just needs to be run.

**The 616→926 gap:** The interesting region. The algebraic AGL(1,8) construction is likely near-maximal for that specific group. Beating 616 requires either:
1. A different algebraic group with better orbit structure
2. Local search that breaks the group symmetry and finds non-group-structured codes
3. A combination of both

## Agent Mix Decision

**Cold start rules apply:** 2 explore + 1 full + 1 research (per prompt template rules for generation 1).

### full_1 (sonnet) — "Lock in 616"
Rationale: We know AGL(1,8) achieves 616. This agent's job is to use the existing helper and get 616 into the population immediately, establishing our floor. Also runs greedy extension and stochastic restart to probe whether the code can be extended. This is the highest-ROI action: guaranteed large jump from 262→616.

Timeout: 900s. AGL construction takes ~4s, greedy extension is fast. Multiple restart variants should fit easily.

### explore_1 (sonnet) — "ILS destroy-and-repair"
Rationale: Iterative Local Search is the most direct approach to search above 616. Start from AGL(1,8), destroy a fraction, repair with different permutations. The 616-code has a rigid group structure — destroying part of it and rebuilding with non-group permutations might find a larger clique. Uses `fast_compatible_mask` from helpers/compat.py for efficient repair (23x faster than naive). Also tries simulated annealing variant.

Timeout: 1200s. ILS with 40320-vertex graph and fast compatibility checking should run many iterations. 20 destroy-repair iterations take ~20-30s, allowing hundreds of attempts.

### explore_2 (sonnet) — "Alternative algebraic groups"
Rationale: AGL(1,8) is not the only transitive group on 8 points. AΓL(1,8) (semilinear affine, 168 elements) partitions S₈ into 240 orbits of size 168 instead of 720 orbits of size 56. Different orbit structure = different compatibility graph = potentially different/larger clique. Also tries direct probabilistic clique search (beam search) and coset constructions (sharply transitive subgroups). All are orthogonal to AGL(1,8) and to ILS.

Timeout: 1200s. AΓL orbit computation is similar to AGL (~5-10s). Clique search on 240-vertex graph is trivial. Direct search on 40320 vertices is heavier but still manageable.

### research_1 (sonnet) — "Literature + algorithmic landscape"
Rationale: This is generation 1 — no knowledge base exists. The research agent creates the initial knowledge base by surveying what's known about M(8,5), what groups have been tried, what algorithms work for similar max-clique problems, and what adjacent combinatorial theory might apply. The report feeds directly into the Evaluator's knowledge extraction and into generation 2 briefs.

Timeout: 600s. This is a research/writing task with no computation. Should be fast.

## Timeouts

No timing data available (generation 1). Used conservative estimates:
- full_1: 900s — AGL construction is fast, but stochastic restarts might run longer
- explore_1/2: 1200s — ILS and algebraic search both involve iteration; 1200s gives room for 5-10 minutes of actual computation
- research_1: 600s — writing-heavy, no heavy computation

Default work timeout is 2700s, so all agents have ample headroom.

## What I Deliberately Did NOT Launch

**Exploit agent:** Nothing to exploit at generation 1. We have only the greedy baseline at 262. Exploit needs a strong code to refine.

**Genetic agent:** Requires 2 parent solutions. We have only 1. Cannot run.

**Experimentator agent:** No specific open questions from previous generations. No recurring helper requests. Nothing to experiment on yet. Will become relevant in generation 2 if specific algorithmic questions emerge.

**Additional explore agents:** Cold start rules say exactly 2 explore + 1 full + 1 research. Staying within the constraint.

## Risks and Contingencies

**Risk 1:** explore_2's AΓL(1,8) implementation might be incorrect. The Frobenius automorphism in GF(8) requires careful handling. If the agent gets confused about GF(8) arithmetic, the orbit structure will be wrong. Mitigation: The brief gives explicit squaring map values for GF(8).

**Risk 2:** ILS (explore_1) might not beat 616 in this generation. The AGL(1,8) code might be locally maximum — all ILS destructions might reconstruct back to 616. This is fine; it would be valuable negative evidence. The report will capture this.

**Risk 3:** The research agent (research_1) is purely knowledge-generating. If it hallucinates incorrect mathematical facts, future agents might pursue dead ends. Mitigation: The brief asks for concrete group-theoretic constructions, not vague suggestions. Errors in specific claims (group orders, orbit sizes) will be detectable.

**Risk 4:** full_1 might find greedy extension from 616 adds no codewords. This would confirm AGL(1,8) gives a tight local maximum. Important data point either way.

## Expected Outcomes

Best case (probability ~30%): explore_1 or explore_2 finds a code > 616. New record. Generation 2 can exploit it.

Likely case (probability ~60%): full_1 confirms 616 via AGL. ILS finds 616 is tight. Research agent produces useful survey. Generation 2 has solid knowledge base and can attempt more sophisticated approaches (tabu search, column generation, more algebraic groups).

Worst case (probability ~10%): Implementation bugs in explore_2 produce invalid codes. full_1 still saves us at 616.

## Coverage Matrix
Empty at generation 1. After this generation, we'll have coverage on:
- AGL(1,8) orbit clique construction
- ILS destroy-and-repair
- AΓL(1,8) semilinear group
- Direct beam-search clique
- Coset constructions
