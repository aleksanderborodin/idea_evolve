## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` → fitness = 99 (Singer q=97 + perturbation)
Target: 100. Theoretical upper bound: ~109 (Carter, Hunter, O'Bryant 2025).

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_001.md` — Algebraic constructions
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_002.md` — Search methods (confirmed inferior)
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_003.md` — Hybrid approaches
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/history/coverage_matrix.md` — What has been tried
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/ideas/active/idea_008.md` — Singer q=101 truncation (being implemented by exploit_1)
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/ideas/active/idea_009.md` — Erdos-Turan construction
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/reports/gen001/research_1.md` — Previous research findings (build on these, don't repeat)

## Directive

**This is a Track B research mission. Find approaches the system has never tried. Read the coverage matrix and dead ends list to know what has been tried. Look for ideas from adjacent fields, recent papers, or mathematical theory that could apply.**

### What We Already Know (DO NOT repeat this research):
- Singer difference sets (q=97 gives 98, q=101 gives 102) — well understood
- Greedy construction gives 66 — explained by Erdos-Turan
- SA from greedy baseline caps at 68
- Perturbation of Singer-97 caps at 99

### Research Questions (ordered by priority):

1. **What is the actual largest known Sidon set in {0, ..., 10000}?** Are there published tables or computational records? If someone has found 100+ elements, knowing the explicit construction would be invaluable.

2. **Non-Singer algebraic constructions for large Sidon sets.** Specifically:
   - Bose-Chowla constructions — how do they compare to Singer for N=10000?
   - Ruzsa constructions — different structure, potentially different extension properties?
   - Lindström's construction — does it give larger sets than Singer in certain ranges?
   - Modular Sidon sets from elliptic curves or higher-genus curves?

3. **Computer search techniques specifically for Sidon sets.** Are there published algorithms that beat random local search? Techniques like:
   - Constraint programming / SAT formulations
   - Branch-and-bound with good pruning
   - Algebraic-geometric search over cyclic shifts
   - Evolutionary algorithms specialized for combinatorial design problems

4. **The Singer q=101 truncation problem.** What's the expected number of elements retained after optimal cyclic shift? Are there theoretical results on this "intersection of a perfect difference set with an interval" problem?

5. **Hybrid constructions.** Are there known techniques for "stitching" two Sidon sets together (one covering the low range, one the high range) while maintaining the Sidon property?

6. **Upper bounds tighter than ~109 for {0, ..., 10000} specifically.** The ~109 is the asymptotic bound. Are there computed exact bounds or ILP-derived bounds for N=10000?

### Deliverables:
Write `output/report.md` with:
- For each finding: the construction/technique, its expected performance for N=10000, implementation complexity, and whether it's been tried in our system.
- Concrete actionable recommendations for gen 3 agents.
- Any explicit Sidon set constructions you can find (element lists, formulas, algorithms).
- References (paper titles, authors, years) for each finding.
