## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` → fitness = 102 (Singer q=101 truncation)
Target: 109. Gap: 7 elements. Singer approaches proven exhausted.

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/history/coverage_matrix.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_001.md`

## Directive

**This is a Track B research mission. Find approaches the system has never tried. The coverage matrix and dead ends below tell you what has been tried. Look for ideas from adjacent fields, recent papers, or mathematical theory that could apply.**

### PRIMARY OBJECTIVE (CRITICAL — this has been the #1 priority for 3 generations and has FAILED 3 times)

Find the published best Sidon set size for N=10000 (or the closest available data point).

**CRITICAL WORKFLOW RULE:**
After EVERY web fetch, paper download, or OEIS query, **immediately** write your current findings to `output/findings.md`. Do not accumulate results in memory and write at the end. Structure findings.md as an append log:
```
## Query 1: [what you searched]
### Result: [what you found]
...
```

Your FIRST actions (before any analysis) must be:
1. Search for arXiv paper math/0407117 (O'Bryant 2004 "A complete annotated bibliography of work related to Sidon sets") — look for computational tables of F(N) for large N
2. Search for arXiv paper 2310.20032 (Carter/Hunter/O'Bryant 2023) — upper bound paper
3. Search OEIS sequence A003022 (optimal Sidon/B2 set sizes) — check the b-file for large N values
4. Search OEIS sequence A143824 — maximum size of Sidon set in {1,...,n}
5. Web search: "Sidon set N=10000 best known", "B2 sequence record 10000", "perfect difference set size 10000"
6. Web search: "Cilleruelo Sidon" — algebraic geometry constructions
7. Web search: "Helm 2006 Sidon database computational"

Write to findings.md after EACH query. If the session ends prematurely, partial findings are still valuable.

### SECONDARY OBJECTIVE

Search for algebraic constructions for Sidon sets beyond Singer and Erdos-Turan:
- **Cilleruelo 2011** — "Sidon sets in N²", algebraic geometry construction
- **Paley difference sets** — do they produce Sidon sets? Under what conditions?
- **Twin-prime constructions** — related perfect difference sets
- **Hall's sextic residue difference sets**
- **Ruzsa's construction** — S = {(x, x² mod p)} type constructions
- **Bose-Chowla** — how it relates to and differs from Singer
- Any construction giving >102 elements in {0,...,10000}

### What the system already knows
- Singer q=101 gives 102 elements (optimal Singer for N=10000). Exhausted.
- Erdos-Turan gives 75 elements. Far from competitive.
- SA, greedy, perturbation all fail to improve. Proven dead ends.
- The theoretical upper bound is ~109 (Carter/Hunter/O'Bryant 2023, √N + 0.98·N^{1/4}).
- The gap between 102 and 109 is the critical challenge.

### Deliverables
Write to `output/findings.md`:
1. Published F(10000) or best available approximation
2. List of algebraic construction families with their performance for N near 10000
3. Any construction method that provably or computationally achieves >102 for N=10000
4. References (with arXiv IDs or DOIs) for all claims

Write to `output/report.md`: your structured debrief following the standard 9-section format.
