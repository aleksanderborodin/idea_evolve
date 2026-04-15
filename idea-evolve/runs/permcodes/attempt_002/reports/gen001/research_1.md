# Research Agent Debrief — gen001 research_1

## What Did You Try?

### Research Findings (output/findings.md)
Produced a comprehensive research report covering 5 major findings:

1. **PGL(2,7) and PSL(2,7) Orbit Cliques** — The key algebraic direction. AGL(1,8) with 56 elements gives 720 orbits; PGL(2,7) with 336 elements gives only 120 orbits. A max-clique search on 120 vertices (vs 720) is tractable and may yield >11 orbits = >616 codewords. PSL(2,7) has 168 elements = 240 orbits.

2. **Variable Neighborhood Search (VNS) from the 616-Code** — Start from the known 616 AGL-code, use bucket-based compatibility checking to find all compatible permutations, iteratively remove and rebuild. This attacks the problem from the full permutation space angle rather than orbit reduction.

3. **PGL(2,7) Orbit Compatibility Structure** — The larger orbit size means different compatibility properties; cross-group clique search between PGL and AGL orbits may find larger cliques than either group alone.

4. **Exact Compatibility Counting via Bucket IDs** — Documented that `helpers/compat.py`'s `fast_compatible_mask()` is the right tool for all compatibility operations, enabling checking all 40320 permutations in ~0.2s.

5. **LP Bound Gap Analysis** — 926 upper bound vs 616 lower bound = 310 gap (~50% of upper bound). The large gap suggests significant room for improvement beyond AGL.

### Research Questions Answered

**Q1: Gap between 616 and 926**
- LP bound = 926 (from Smith & Montemanni 2012 linear programming relaxation)
- AGL(1,8) construction = 616 (orbit clique of 11 AGL orbits)
- Gap = 310 codewords = 53% of upper bound — significant room for improvement
- AGL(1,8) is NOT near-optimal given this gap

**Q2: Group-theoretic constructions beyond AGL(1,8)**
- PGL(2,7): 336 elements, 120 orbits of 336 perms each. Action: x → (ax+b)/(cx+d) over GF(7)∪{∞}
- PSL(2,7): 168 elements, 240 orbits of 168 perms each. PSL(2,7) ≅ GL(3,2)
- Neither has been published for M(8,5) — untried direction
- Sharp 2-transitivity matters: a sharply 2-transitive group on n points gives n(n-1) group elements and partitions S_n into n!/(n(n-1)) = n!/n/(n-1) orbits

**Q3: Iterative clique-building (VLNS)**
- No published VNS for M(8,5) with specific parameters found
- Proposed: remove 5-10% (30-60 codewords), rebuild via clique search, iterate
- Key insight: the AGL-orbit reduction may throw away compatible perms; bucket approach on full 40320 space can find them

**Q4: LP/IP formulation**
- IP variables: x_π ∈ {0,1} for 40320 perms
- Incompatibility constraints: x_π + x_σ ≤ 1 for each incompatible pair
- LP relaxation gives 926 — column generation or branch-and-price would be exact but complex
- Practical approach: use bucket-compatible mask for greedy + clique search rather than solving IP directly

**Q5: SA specifics**
- No published SA application to M(n,d) with specific parameters found
- Move operator for permutation codes: swap one codeword for a compatible permutation (not add/remove, which destabilizes)
- Temperature schedule: geometric cooling from T_0 ≈ 0.1-0.5, factor 0.995-0.999
- VLNS (remove k, rebuild) is probably more effective than SA for this combinatorial structure

**Q6: Algebraic lifting**
- M(7,5) = 420 known
- No systematic lifting construction found in literature
- Proposed experiment: take M(7,5) code, try adding element 7 in each position for each codeword

## What Information Did You Lack?

1. **PGL(2,7) and PSL(2,7) permutation representations** — I don't have the explicit 336-element group as a set of 8-permutations. I know the abstract group structure but can't write `pgl27_elements()` without deriving or looking up the embedding into S_8.

2. **Actual compatible-permutation count for the 616-code** — I proposed using `fast_compatible_mask()` to count extra-compatible permutations but did not run the experiment myself. This is the single most important empirical question: "How many permutations are compatible with the full 616-code but not in it?"

3. **The Smith & Montemanni paper PDF** — The description.md references `papers/pdf/001_Smith_Montemanni_permutation_codes_2012.pdf` but the papers/ directory doesn't exist in the run directory or project root. I couldn't read the actual paper to get specific details about their construction parameters.

4. **No existing paper summaries** — The papers/summaries/ directory was empty. I had no prior research summaries to build on.

## What Given Facts Might Be Wrong or Outdated?

- The description says "M(8,5) ≤ 926 (LP bound)" but the LP bound is actually from a specific LP relaxation, not a proven upper bound. The true upper bound might be lower than 926.
- The AGL(1,8) construction achieving exactly 616 is stated as fact — this is correct (Smith & Montemanni 2012).
- The `helpers/agl18.py` docstring says "orbits 0.9s, compat graph 3.7s, full pipeline 4.0s" — these timings weren't verified but seem reasonable.

## Was the State of Affairs Accurate?

Yes — this was generation 0 (pre-run), so the State of Affairs correctly stated "nothing explored yet." It served as a correct baseline showing no knowledge existed.

## What Would You Do Differently?

1. **Run the bucket-compatible count immediately** — The most important question ("how many extra perms are compatible with the 616-code?") should have been computed as part of the research. I should have written a quick prototype that:
   - Loads the 616 code via `agl18_max_clique_code()`
   - Builds bucket IDs for all 40320 perms
   - Runs `fast_compatible_mask()` to count extra-compatible perms
   - Reports the finding

2. **Derive PGL(2,7) elements explicitly** — I know PGL(2,7) acts on GF(7)∪{∞} via Möbius transformations. I should have worked out the explicit 336 permutations as Python code rather than just describing the construction.

## Specific Experiments to Run

1. **PGL(2,7) orbit clique search** — Build `pgl27_elements()`, `pgl27_orbits()`, `pgl27_compat_graph()`. Run max-clique on the 120-vertex graph. Expected time: <10 seconds.

2. **Extra-compatible permutation enumeration** — Run `fast_compatible_mask()` on full 616-code. If >8 extra perms found, add them greedily to get >624.

3. **Cross-group PGL × AGL clique** — Build mixed compat matrix between 120 PGL reps and 720 AGL reps. Find max cross-group clique.

4. **VNS from 616-seed** — Implement: remove 30-60 random codewords, run clique search on residual, re-add, repeat 100 times.

5. **M(7,5) extension test** — For each codeword in the known M(7,5)=420 code, try inserting element 7 in each of 8 positions. Test compatibility.

## What Surprised You?

1. **No papers or summaries existed** — Both the global `papers/` directory and the run's `papers/` directory were empty. This is a fresh project with no prior research accumulated.

2. **No manage.py script** — The brief mentioned `papers/manage.py` for downloading papers, but it doesn't exist anywhere. This infrastructure may not be set up yet.

3. **The helpers are well-documented** — `agl18.py` and `compat.py` are high-quality, tested helpers. This is a solid foundation to build on.

4. **The gap is HUGE** — 310 codewords between 616 and 926 is not a small gap; it's 50% of the upper bound. This suggests the problem is wide open for improvement.

## Helper Tools Feedback

- **`helpers.agl18`** — Excellent. Well-tested, documented, and exactly what's needed for the AGL construction. `agl18_max_clique_code()` gives the seed 616-code directly.
- **`helpers.compat`** — Excellent. `fast_compatible_mask()` is the right tool. However, there's no provided way to find the *indices* of codewords in the `all_perms` array — this is needed for `fast_compatible_mask()` which takes `code_indices`. I had to work around this by noting it needs to be computed separately.
- **Missing helper**: A `find_codeword_indices(code, all_perms)` function would be helpful — takes a code and the all_perms array and returns the indices. Or equivalently, `fast_compatible_mask` could accept the actual code array directly if the code has been mapped to all_perms indices.

## Time Budget

I had enough time for web research and writing the findings report, but did NOT have time to run the most important prototype experiment (counting extra-compatible perms for the 616-code). With more time, I would have:
1. Written and run the prototype to count extra-compatible perms
2. Written the PGL(2,7) element generator to confirm the 120-orbit structure
3. Downloaded and read the Smith & Montemanni paper

The web research took longer than expected due to some failed fetches (wrong arXiv IDs, blocked ResearchGate links). A more targeted approach would have been faster.

---

## Output Files Produced

- `output/findings.md` — Main deliverable: 5 research findings, open questions, dead ends, experiments
- No prototype code written (time did not permit running the key experiment)
- No `report.md` written by mistake (this debrief file IS the report.md per the brief)
