## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/population/best.py` → fitness = 105 (Bose-Chowla ap q=107, mul=433)
Second best: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/population/top/rank02_105.py` → fitness = 105

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/knowledge/state_of_affairs.md` — Strategic overview (read FIRST for context)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/history/coverage_matrix.md` — What has been tried (know what to avoid researching)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_001.md` — Algebraic constructions (all tried)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_004.md` — Exact methods (CP-SAT history)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/problem/description.md` — Problem definition
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/problem/helpers/rokicki_data.py` — MAY contain F2(10000) data, CHECK THIS
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/papers/summaries/` — Any prior research papers (check what's already downloaded)

## Directive

**This is a Track B research mission. Your PRIMARY objective is to find F₂(10000) — the
published record for the largest known Sidon set in {0, ..., 10000}. This question has been
unanswered for 6 generations due to systemic research agent failure. You MUST resolve it.**

### MANDATORY first actions (do these IN ORDER before anything else)

**Step 1:** Read `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/problem/helpers/rokicki_data.py` — it may contain tabulated Sidon set size
data or references to the Rokicki-Dogon database. This file is already on disk.

**Step 2:** Run web searches for the published record:
- `WebSearch("OEIS A003022 Sidon set maximum size")` — OEIS tracks extremal combinatorics sequences
- `WebSearch("B2 sequence maximum size N=10000")` 
- `WebSearch("Sidon set record 10000 Golomb ruler")` — Sidon sets are equivalent to Golomb rulers
- `WebSearch("optimal Golomb ruler 10000 marks")` 
- `WebSearch("Rokicki Dogon optimal rulers database cube20.org")`
- `WebSearch("F2 N Sidon set upper bound lower bound exact values")`

**Step 3:** Report your findings from Steps 1-2 BEFORE doing any literature review.
Write what you found (or didn't find) at the top of your findings.md.

### What F₂(10000) tells us

- If F₂(10000) = 105: The pipeline is at the known optimum. All CP-SAT and VLNS search
  should be halted. The remaining work is theoretical (proving optimality or finding a new
  construction technique for larger N).
- If F₂(10000) = 106 or 107: CP-SAT/VLNS search is correctly prioritized. Try to find the
  published construction method.
- If F₂(10000) ≥ 108: Major gap — we need to understand what constructions achieve this and
  why our pipeline hasn't found them.
- If F₂(10000) is not published for N=10000: Note this explicitly. Check for nearby values
  (N=9000, N=11000, N=15000) to interpolate.

### Secondary objectives (ONLY after Steps 1-3 are complete)

**4. Find approaches the system has never tried.** Read the coverage matrix and dead ends
in the State of Affairs. Then research:
- Tabu search with "swap then fill" moves (mentioned in gen 6 research findings, never implemented)
- GRASP (Greedy Randomized Adaptive Search) for Sidon sets
- Probabilistic method constructions (Erdos-style random constructions with better bounds)
- Recent papers (2020+) on Sidon sets, B₂ sequences, or Golomb rulers
- Connections to other combinatorial problems (perfect difference sets, planar nearrings)

**5. Check if alternative solver formulations exist in the literature.**
- Has anyone used SAT solvers (not CP-SAT) for Sidon sets?
- Are there ILP formulations that work better than binary variables or AllDifferent?
- Have branch-and-bound codes been published specifically for this problem?

### Source labeling requirement

Every factual claim in your findings must be labeled:
- `[OEIS: A00xxxx]` — from OEIS lookup
- `[paper: Author Year]` — from a specific paper
- `[web: URL]` — from a web search result
- `[training data: unverified]` — from your training knowledge (NOT verified this session)

Claims labeled `[training data]` must be clearly flagged so downstream agents can weigh them.

### Output files

1. `output/findings.md` — Your research findings (PRIMARY deliverable)
2. `output/report.md` — Debrief report
3. Optionally: `output/sol01.py` — If you find a published construction that achieves > 105,
   implement it and evaluate

### What NOT to do

- Do NOT skip Steps 1-3. Previous research agents wrote from training data without web
  searches. This is why F₂(10000) remains unknown after 6 generations.
- Do NOT write findings.md from training data alone. Every finding must have a source.
- Do NOT spend more than 5 minutes on any single web search. If a query returns nothing
  useful, move to the next one.
