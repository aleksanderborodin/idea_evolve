## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/population/best.py` → fitness = 105 (Bose-Chowla ap q=107, mul=433)
Second best: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/population/top/rank02_105.py` → fitness = 105

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/knowledge/state_of_affairs.md` — Current strategic overview
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_001.md` — Algebraic constructions (what has been tried)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_002.md` — Search-based methods (all exhausted)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/knowledge/ideas/active/idea_025.md` — Ruzsa-Lindstrom construction (UNTESTED)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/history/coverage_matrix.md` — What combinations have been tried (avoid repeating)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/problem/description.md` — Problem definition (N=10000, Sidon set)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/problem/helpers/core.py` — is_sidon, can_add, count_violations, is_prime
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/problem/helpers/extend.py` — greedy_extend, random_perturbation

## Directive

**This is a Track B radical exploration. You must NOT use the current best solution
(Bose-Chowla ap q=107), any file in `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/population/top/` or `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/population/best.py` as a
starting point. You must NOT refine, tweak, or extend the current dominant technique.
Start from scratch.**

The system is stuck at 105 using algebraic constructions (Singer, Bose-Chowla). All perturbation,
greedy, and search methods are exhausted. You must try something **genuinely orthogonal**.

### Approaches to explore (pick 1-2, go deep)

**Option A: Ruzsa-Lindstrom construction (idea_025, NEVER TESTED)**
The Ruzsa-Lindstrom construction builds Sidon sets using a different algebraic structure than
Singer/Bose-Chowla. It uses quadratic residues in finite fields:
- Choose a prime p
- S = {2ip + (i^2 mod p) : i = 0, 1, ..., p-1}
- This gives a p-element Sidon set in {0, ..., 2p^2 - p}
- For N=10000: p=70 gives 70 elements in span ~9730; p=71 gives 71 in ~9941
- This is different from Singer/Bose-Chowla — it uses quadratic residues, not primitive roots
- After constructing the base set, apply greedy extension: add elements not in the base that
  maintain the Sidon property
- Then try simulated annealing from this starting point — it's in a DIFFERENT basin of
  attraction than the algebraic constructions

**Option B: Projective plane incidence construction**
Use the incidence structure of a projective plane of order q to construct Sidon sets.
Points of PG(2,q) can be mapped to integers; lines give Sidon sets. This is related to
but distinct from Singer difference sets. Try q=97, 101, 103 with different point/line mappings.

**Option C: Modular Sidon sets with CRT lifting**
Construct Sidon sets in Z_m for several small moduli m, then use CRT to lift to Z_N.
This is a completely different approach — additive combinatorics rather than multiplicative.
Previous CRT attempt (gen 4) failed with 312 violations, but the concept may work with
correct implementation.

**Option D: Random algebraic construction**
Generate random polynomials f(x) = ax^2 + bx + c over GF(p) and construct
S = {f(i) mod N : i = 0, ..., p-1}. Quadratic polynomials over finite fields naturally
produce structures with few repeated differences. Search over random coefficients.

### Requirements

- Build your solution from scratch — do NOT read or import the 105-mark set
- Construct an initial set using one of the approaches above
- Apply greedy extension (`from helpers.extend import greedy_extend`) to fill gaps
- Try SA or perturbation from your constructed starting point (you're in a different basin)
- Evaluate each solution: `python3 evaluate.py output/solXX.py`
- Even if your best score is below 105, report what you found — a 90+ from a completely
  different construction is more valuable than another 105 from Bose-Chowla

### Output files

Write solutions to `output/sol01.py`, `output/sol02.py`, etc. Run evaluate.py after each.

### What NOT to do

- Do NOT read `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/population/best.py` or any file in `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/population/top/`
- Do NOT use Singer difference sets or Bose-Chowla constructions (these are the dominant technique)
- Do NOT use `from helpers.rokicki_data import BEST_105` or any variant
- Do NOT import or hardcode the known 105-element set
- Do NOT do greedy-from-scratch (ceiling 66-70, exhaustively confirmed)
- Do NOT do ET(71)+1-opt (ceiling 75, exhaustively confirmed)
