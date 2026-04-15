# Research Findings — M(8,5) Permutation Codes: Beyond AGL(1,8) = 616

## Summary

M(8,5) has known bounds 616 ≤ M(8,5) ≤ 926. The AGL(1,8) construction achieves 616 — any score >616 is a new result. The 310-codeword gap (53% of upper bound) represents significant room for improvement. The most promising directions are (1) using larger primitive permutation groups (PGL(2,7), PSL(2,7)) to find larger orbit cliques, and (2) Variable Neighborhood Search (VNS) starting from the 616-code to find additional compatible codewords.

---

## Finding 1: PGL(2,7) and PSL(2,7) Orbit Cliques
**Relevance**: Any agent attempting an algebraic construction
**Detail**: AGL(1,8) = 56 elements gives 720 orbits of size 56 → clique of 11 orbits → 616 codewords. PGL(2,7) has 336 elements and acts sharply 2-transitively on 8 points. PSL(2,7) ≅ GL(3,2) has 168 elements. These larger groups partition S₈ into fewer, larger orbits:

- AGL(1,8): 40320/56 = 720 orbits (each orbit = 56 perms)
- PSL(2,7): 40320/168 = 240 orbits (each orbit = 168 perms)
- PGL(2,7): 40320/336 = 120 orbits (each orbit = 336 perms)

With fewer orbits, the max clique search is on a 120-vertex or 240-vertex graph (vs 720 for AGL), but the compatibility within and between these orbits is different. A code from PSL(2,7) orbits alone could be larger than 616, or a mixed clique combining orbits from multiple groups could beat the AGL-only clique.

The projective action PGL(2,7): x → (ax+b)/(cx+d) over GF(7) ∪ {∞} with a,c ≠ 0 or ad-bc ≠ 0.

**Actionable implication**: Build a helper `pgl27.py` analogous to `agl18.py` that generates PGL(2,7) elements as permutations of {0,...,7}, computes orbit representatives, and builds a compatibility graph across all 120 PGL(2,7) orbits. Run max-clique search on this graph. If >11 orbits found, we have >616 codewords. Also try mixed-group clique search between PGL(2,7) orbits and AGL(1,8) reps — a code combining orbits from both groups may be larger than either alone.

**Implementation sketch**:
```python
from helpers.pgl27 import pgl27_elements, pgl27_orbits, pgl27_compat_graph
orbits = pgl27_orbits()  # 120 orbits
G = pgl27_compat_graph()  # 120×120 compat matrix
# max-clique search on G
# Also try cross-group compat between pgl27 reps and agl18 reps
```

**Reference**: Smith & Montemanni (2012) only report AGL(1,8) results for M(8,5). No published M(8,5) result using PGL(2,7) or PSL(2,7) is known — this is an untried direction.

---

## Finding 2: Variable Neighborhood Search (VNS) from the 616-Code
**Relevance**: Any agent doing local search or iterative improvement
**Detail**: Start from the known 616-code, then iteratively:
1. Randomly remove k codewords (k ≈ 5-10% of code size, i.e., 30-60 codewords)
2. On the residual graph of compatible permutations, run clique search
3. Re-add the newly found compatible codewords
4. Repeat

The key insight: the 616-code is a max-clique on the AGL-orbit graph but is NOT necessarily a max-clique on the full permutation graph (40320 vertices). Some permutations outside the 616 may be compatible with the 616-code — the AGL orbit reduction may have thrown away compatible perms that don't orbit-represent under AGL.

**Actionable implication**: Use `helpers.agl18.agl18_max_clique_code()` to generate the seed 616-code, then use `helpers.compat.build_bucket_ids()` + `fast_compatible_mask()` to find ALL permutations compatible with the 616-code (using the exact bucket method). The number of compatible perms that are NOT in the 616-code itself tells us the "slack" — if there are even 5-10 compatible perms, we can add them and break through 616. If there are many more, the VNS approach of removing and rebuilding should find them.

**Implementation sketch**:
```python
from helpers.agl18 import agl18_max_clique_code
from helpers.compat import build_all_perms, build_bucket_ids, fast_compatible_mask
code = agl18_max_clique_code()  # 616 codewords
all_perms = build_all_perms(8)
bids = build_bucket_ids(all_perms)
code_indices = ...  # find indices of code in all_perms
compatible_mask = fast_compatible_mask(code_indices, bids)
# compatible_mask.sum() tells us how many perms are compatible with full code
# If compatible_mask.sum() > 616, we can augment the code
```

**Expected improvement**: Even finding 8-10 extra compatible permutations beyond 616 would be a new record. Target: reach 624 (the problem's stated target).

---

## Finding 3: PGL(2,7) Orbit Size Means Different Compatibility Structure
**Relevance**: Max-clique search agents
**Detail**: The AGL(1,8) orbit clique of 11 orbits uses the fact that each orbit is small (56 elements) and the compatibility between two orbits is checked by comparing all 56×56 pairs. With PGL(2,7), orbits are larger (168 elements), so the min-distance between two orbits (checked across all 168×168 pairs) is more likely to be <5. BUT larger orbits also mean the compatibility graph is smaller (120 vertices instead of 720), making exhaustive max-clique search feasible — we can use an exact branch-and-bound instead of heuristics.

The PGL(2,7) group includes transformations of the form x → (ax+b)/(cx+d) where a,b,c,d ∈ GF(7), ad-bc ≠ 0, and the group acts on the 8-element projective line GF(7) ∪ {∞}. This gives different structural properties than the affine-linear group AGL.

**Actionable implication**: For PGL(2,7) orbits, use an exact max-clique algorithm (e.g., branch-and-bound with bitset adjacency) on the 120-vertex graph. The graph is small enough for optimal search. If the optimal PGL-clique has fewer than 11 orbits, try cross-group clique search combining PGL and AGL orbits — some cross-group combinations may be larger than intra-group cliques.

**Implementation sketch**:
```python
from itertools import combinations
# For 120-vertex graph, use bitSET representation for adjacency
# Branch-and-bound: order vertices by degree, bound by max degree of remaining
# For cross-group: build compat matrix between 120 PGL reps and 720 AGL reps
```

---

## Finding 4: Exact Compatibility Counting via Bucket IDs
**Relevance**: All agents doing compatibility checking
**Detail**: `helpers/compat.py` provides `fast_compatible_mask()` which is 23x faster than naive row-by-row checking at K=616. The key insight (documented in compat.py lines 95-131): for n=8, d=5, two permutations are incompatible iff they agree on ≥4 positions, which happens iff they share the same bucket ID on any of the C(8,4)=70 four-position subsets.

**Actionable implication**: Every agent doing local search should use `build_bucket_ids()` once, then call `fast_compatible_mask()` for all compatibility checks. For finding codewords compatible with a partial code, this enables checking all 40320 permutations against a 616-word code in ~0.2s instead of ~5s.

**Reference**: This is already in `helpers/compat.py` but may be underutilized by agents using naive approaches.

---

## Finding 5: LP Bound = 926, Gap Analysis
**Relevance**: Strategic planning, knowing how much headroom exists
**Detail**: The LP upper bound of 926 gives us a sense of the gap. From the literature, the bound is derived via the Linear Programming relaxation of the max-clique IP:
- Variables: x_π ∈ {0,1} for each of 40320 permutations
- Constraints: x_π + x_σ ≤ 1 for each incompatible pair (π,σ)  (they agree on ≥4 positions)
- Objective: maximize sum x_π

The LP relaxation replaces integrality with 0 ≤ x_π ≤ 1, giving bound 926. This means at least 40320-926 = 39394 permutations must be excluded in any optimal solution. The gap of 310 (926-616) is ~50% of the bound — suggesting the problem structure admits significant packing beyond the AGL construction.

**Actionable implication**: The large gap suggests AGL(1,8) is not near-optimal. The "right" group or combination of groups should be able to push toward 700+. The VNS approach or exact IP methods (column generation) are the most likely paths to close this gap.

---

## Open Questions

1. **What is the PGL(2,7) orbit structure for M(8,5)?** We don't know if PGL(2,7) orbits are all mutually incompatible (giving a small clique) or if some are compatible (giving a large clique). This needs to be computed.

2. **Are there any permutations compatible with the AGL(1,8) 616-code that are outside the AGL orbits?** If yes, the "orbit reduction" threw away useful codewords. The bucket-based compatibility count will answer this.

3. **What is the "intersection profile" of the 616-code?** No agent has computed which orbit pairs contribute the most compatible codewords. A distance-profile analysis of the 616-code would reveal which orbit types are most "friendly" toward adding more codewords.

4. **Can M(8,5) be expressed as a known combinatorial design?** Permutation codes relate to resolvable Steiner systems, BIBDs, and mutually orthogonal Latin squares (MOLS). The existence of 7 MOLS of order 8 is known (since 8 is a prime power). Could an 8×8 Latin square set be used to construct a larger permutation code?

5. **Is there a lifting construction from M(7,5) to M(8,5)?** M(7,5) = 420 (known). Can this be extended by 1 element to reach M(8,5)?

---

## Dead Ends to Avoid

- **Pure greedy construction**: The baseline greedy reaches ~262, far below 616. Without group structure, greedy is not competitive.
- **Brute-force clique search on all 40320 vertices**: NP-hard, not feasible in <30s even with heuristics. The group-orbit reduction is essential.
- **AGL(1,8) alone**: Already fully explored — max clique is 11 orbits = 616. No more can be found in AGL-only orbits.
- **Simulated annealing with random-walk move operators**: SA without good structure exploitation will plateau at the same ~262 greedy level. SA needs to be guided by group structure or compatibility graphs.

---

## Specific Questions for Experimentator Agents

1. **Compute the PGL(2,7) orbit compatibility graph**: How many orbits? What is the max clique size? Is it >11 orbits?

2. **Find all permutations compatible with the 616-code**: Using `fast_compatible_mask()`, count how many of the 40320 permutations are compatible with the full 616-code. If there are 10+ outside the code, which specific permutations are they?

3. **Cross-group clique between PGL and AGL**: Build a mixed compatibility graph between PGL(2,7) orbit representatives and AGL(1,8) orbit representatives. What is the max cross-group clique?

4. **Distance profile of 616-code**: Compute pairwise distances within each AGL orbit and between orbits. Which orbit types are "dense" (many internal close pairs at distance 5) and which are "sparse"?

5. **Test M(7,5) → M(8,5) lifting**: Is there a systematic way to extend a 420-code on {0,...,6} to an 8-element code? Try extending each codeword by the missing element in various positions.
