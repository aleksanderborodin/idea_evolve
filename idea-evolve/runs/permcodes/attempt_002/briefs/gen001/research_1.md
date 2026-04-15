# Agent Brief — research_1 — Generation 1

## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/permcodes/attempt_002/population/gen000/baseline/sol01.py` → fitness = 262 (greedy baseline)
No top-ranked solutions yet beyond the greedy baseline.

## Context
This is Generation 1, cold start. No clusters, no knowledge base yet.

**Problem:** Maximize M(8,5) — the largest permutation code on {0,...,7} with all pairwise
Hamming distances ≥ 5. Known bounds: 616 ≤ M(8,5) ≤ 926. Target: 624.

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/description.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/README.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/agl18.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/compat.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/constraints.md`

## Directive

**This is a Track B research mission. Find approaches the system has never tried. The only
known solution is the AGL(1,8) orbit clique giving 616. Your job is to identify what could
push M(8,5) above 616 toward the 926 upper bound.**

Your deliverable is a findings report `output/findings.md` that gives future agents concrete,
implementable directions. Be specific: vague suggestions like "try simulated annealing" are
not useful. "Use SA with move operator = swap two positions in one codeword, T_0 = 0.5,
cooling factor 0.999, 5M iterations" IS useful.

**Research questions to answer:**

**1. What is the gap between 616 and 926, and why?**
- The LP bound gives ≤ 926. The best constructive bound is 616. That's a factor of ~1.5x gap.
- What is the structure of permutation codes that allows codes beyond 616?
- Is M(8,5) known to be > 616 in any published work?

**2. What group-theoretic constructions beyond AGL(1,8) are known?**
- The description mentions AGL, PGL, PSL, Mathieu groups.
- PGL(2,7) acts on 8 points (projective line over GF(7)). What permutation code does it give?
- PSL(2,7) ≅ GL(3,2): 168 elements. Can it give larger orbit codes?
- M_8 (sharply 2-transitive on 8 points)? ASL(1,8)?
- Research the "sharply transitive" condition: why does it matter for permutation codes?

**3. Iterative clique-building (VLNS approach):**
- The description mentions "iterative clique building: start from partial code, remove random
  subset, find compatible permutations via clique search on residual graph, iterate."
- What are the best parameters? How many perms to remove per iteration?
- Has this approach been used for M(8,5) specifically? What scores were achieved?

**4. LP/IP relaxation methods:**
- Can the problem be formulated as an Integer Program (IP)?
- Variables: x_i ∈ {0,1} for each of 40320 permutations
- Constraints: x_i + x_j ≤ 1 for each incompatible pair (i,j)
- Objective: maximize sum x_i
- Is this feasible in <30s? (There are 40320 variables and potentially millions of constraints)
- Are there column generation or branch-and-price approaches?

**5. Simulated Annealing specifics:**
- For permutation code SA, what is the standard move operator?
  - Option A: Add/remove one codeword
  - Option B: Swap one codeword for a random compatible one
  - Option C: "Kick" — remove 10 codewords, re-add greedily
- What temperature schedule works? What initial temperature?
- In the literature, what SA approaches have been applied to M(n,d)?

**6. Can M(8,5) be attacked via algebraic lifting?**
- Take a smaller code M(4,3) or M(6,5) with known optimal structure
- Lift/embed it into a code on 8 elements
- What lifting techniques are known for permutation codes?

**Implementation sketch (optional but valued):**
If you find a promising approach, write a quick Python prototype in `output/` and evaluate it:
```bash
python3 /home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/evaluate.py output/sol01.py
```

**Output format:**
Write `output/findings.md` with:
1. Summary of key findings (top 5 approaches, ranked by expected impact)
2. For each approach: description, expected code size, implementation sketch, references
3. Dead ends to avoid (algebraic constructions already tried, approaches with known limits)
4. Specific questions for experimentator agents (e.g., "What is the minimum distance profile
   of the AGL(1,8) 616-code? Are any pairs exactly at distance 5?")

If you write a prototype solution, document its score in the findings report.
