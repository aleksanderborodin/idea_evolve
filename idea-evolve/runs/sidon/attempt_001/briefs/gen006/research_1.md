## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` → fitness = 105
Second best: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/top/rank02_105.py` → fitness = 105
Third best: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/top/rank03_104.py` → fitness = 104

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/history/coverage_matrix.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_001.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_004.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/ideas/active/idea_019.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/description.md`

## Directive

**This is a Track B research mission. Find approaches the system has never tried. Read the
coverage matrix and dead ends list in the State of Affairs to know what has been tried. Look
for ideas from adjacent fields, recent papers, or mathematical theory that could apply.**

**Research objectives (in priority order):**

### 1. Find the exact published record for F₂(10000)
This is open question #2 from the State of Affairs — unanswered for 4 generations.
- Search OEIS sequences A003022, A143824, A036563 for tabulated values near N=10000
- Search for papers by Rokicki, Dogon, Shearer, or Dimitromanolakis on optimal Golomb rulers
- Search for the Lunnon/Atkinson tables of B₂ set sizes
- Look for the Modular Golomb Rulers page or similar databases
- If found, this immediately tells us whether 106 is ambitious or conservative

### 2. Find novel construction methods NOT in the knowledge base
The system has tried: Singer (pp), Bose-Chowla (ap), Erdos-Turan, greedy variants, beam
search, SA, LNS, perturbation, CP-SAT. What else exists?

Specific areas to investigate:
- **Cilleruelo's construction** (2010) — uses Sidon sets in Z_p, achieves F(N) ~ sqrt(N).
  Is it computationally different from Singer/Bose-Chowla for finite N?
- **Ruzsa's construction** using perfect difference sets from Galois fields — the Rokicki-Dogon
  database has "rl" (Ruzsa-Lindström?) type rulers. What are these?
- **Modular Sidon sets + Chinese Remainder Theorem** — construct Sidon sets in Z_m and lift
  to integers. Prior attempt (gen 4 explore_2) used CRT incorrectly. Is there a correct formulation?
- **Sidon sets from additive combinatorics / sum-free sets** — any connection to Schur numbers
  or sum-free set constructions?
- **Tabu search or GRASP specifically tuned for Golomb rulers** — any published results?
- **SAT encoding** (not CP-SAT) — direct Boolean encoding with CDCL solver (MiniSat, CaDiCaL).
  Different search strategy from CP-SAT's integer variables.

### 3. Understand the structure of near-optimal Sidon sets
- Do published optimal Sidon sets for moderate N (500-5000) share structural properties?
- Is there a pattern in how optimal sets differ from algebraic constructions?
- The gen 5 small-N analysis showed optimal sets share almost nothing with Singer — does this
  pattern hold for larger N?

**Deliverables:**
1. A findings report with concrete, actionable approaches (not vague suggestions)
2. For each approach found: (a) mathematical description, (b) expected performance for N=10000,
   (c) Python pseudocode if implementable, (d) citation/source
3. If you find the exact F₂(10000) value, highlight it prominently
4. If you find a promising construction, implement it as a solution file and evaluate it

**Do NOT:**
- Revisit Singer/Bose-Chowla theory (exhausted)
- Investigate greedy variants (ceiling 70, confirmed)
- Spend more than 20% of your time on any single approach
