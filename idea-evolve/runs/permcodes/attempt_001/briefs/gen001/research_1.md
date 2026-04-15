## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/permcodes/attempt_001/population/gen000/baseline/sol01.py` → fitness 262 (greedy baseline)
No top/ directory yet — this is generation 1.

## Read First
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/description.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/agl18.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/compat.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/core.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/README.md`

## Directive

**This is a Track B research mission.** Your deliverable is a structured findings report — NOT solutions. You are surveying the mathematical and algorithmic landscape for concrete approaches that could beat M(8,5) ≥ 616. The other agents in this generation are implementing known constructions; your job is to find what else is known, what theoretical structures exist, and what algorithms from adjacent fields could apply.

**Questions to answer:**

1. **What are the best known M(8,5) bounds?** Smith & Montemanni (2012) report 616 ≤ M(8,5) ≤ 926. Has anything improved these bounds since 2012? What specific construction achieves the 616 lower bound — is it exactly the AGL(1,8) orbit clique with 11 orbits? Are there other groups that achieve the same 616?

2. **What algebraic structures beyond AGL(1,8) might help?**
   - AΓL(1,8) (semilinear): 168 elements, 240 orbits. Has this been tried?
   - PGL(2,7): acts on 8 points (the projective line PG(1,7)), order 336. Orbits of size 336? Worth trying?
   - The Mathieu group M₈: doesn't quite exist, but M₉ and related groups?
   - Sharply transitive sets: does S₈ contain sharply transitive subsets of size > 56?
   - What is the structure of the 616-codeword code? Is it a union of exactly 11 AGL orbits, or can partial orbits contribute?

3. **What computational approaches have been used for similar problems?**
   - Max-clique algorithms on sparse graphs: what are the state-of-the-art solvers? (Bron-Kerbosch variants, branch-and-bound clique solvers)
   - Tabu search for maximum clique: how does it work? Has it been applied to permutation code graphs?
   - Column generation / integer programming for packing problems
   - DPLL-style branching strategies for maximum independent set (dual of clique)

4. **Are there construction methods from latin squares or combinatorial design theory?**
   - Mutually orthogonal latin squares (MOLS): connection to permutation codes?
   - Transversals of latin squares
   - Frequency squares, F-squares
   - Room squares or other combinatorial structures

5. **What is known about the gap [616, 926]?**
   - Are there any constructions known that give > 616 for M(8,5)?
   - What does the LP bound of 926 come from? Is it tight?
   - Are there other upper bound techniques (semidefinite programming, Delsarte bounds)?

**Deliverable format — write `output/report.md` with these sections:**

```markdown
# Research Findings: M(8,5) Permutation Codes

## 1. Current Best Known Bounds
[What the literature says, with specific construction details for the 616 bound]

## 2. Algebraic Structures to Try
[Concrete list: group name, order, expected orbit size, number of orbits, rationale for why it might do better than AGL(1,8)]

## 3. Algorithmic Approaches
[Concrete algorithms with pseudocode or key parameters — not just "use tabu search" but "tabu search with tenure T=20, neighborhood = swap one codeword for a random compatible one, restart from best known solution every 500 steps"]

## 4. Combinatorial Structure Insights
[Anything from latin squares, designs, or coding theory that gives a construction path]

## 5. Priority Ranking
[Which of the above directions is most likely to yield > 616, and why. Top 3 ranked with rationale]

## 6. Open Mathematical Questions
[Questions whose answers would fundamentally change our strategy — e.g., "Is the 11-orbit AGL clique the unique maximum clique, or are there others of the same size?"]
```

**You are a research agent, not a coding agent.** Do NOT write or evaluate solutions. Write only `output/report.md`. Use your knowledge of combinatorics, group theory, and combinatorial optimization. Be specific and concrete — "try the Mathieu group M₂₃" is useless, but "the automorphism group of the extended Golay code acts on 24 points, but there are degree-8 permutation representations of M₁₁..." is useful.

This report will be read by the next generation's agents who will implement your recommendations.
