## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/best.py` → fitness 44114 (compression_ratio=0.8723)
Second best: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/top/rank02_44114.py`
Target: 15000. Kaggle top-3: ~8050 proxy equivalent.

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/state_of_affairs.md` — Current standing
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/ideas/active/idea_008.md` — Trained MLP predictor (untested)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/ideas/active/idea_003.md` — Predictor-guided beam search
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/history/coverage_matrix.md` — What has been tried
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/megaminx/description.md` — Problem specification

## Directive

**This is a Track B research mission. Find approaches the system has never tried. Read the coverage matrix and dead ends list to know what has been tried. Look for ideas from adjacent fields, recent papers, or mathematical theory that could apply.**

The system has tried and exhausted:
- Basic X.-X cancellation (established, ~8.4% improvement)
- Empirical algebraic identities (established, further ~4.7% improvement, ceiling at 44114)
- Unguided beam search (dead end — same as compression)
- Hamming predictor (debunked — zero advantage)
- MITM (dead end for depth > 12)
- Corner-only PDB (invalid assumptions for Megaminx)

The system has NOT tried:
- Trained MLP predictor (other agents covering this generation)
- Layered/phased solving
- Graph neural networks
- Reinforcement learning approaches

**Research priorities:**

1. **Study the Kaggle top solutions.** gen002 research_1 fetched 3 notebook titles but couldn't access the actual code. Try to fetch and analyze:
   - `alexandervc/cayleypy-megaminx-beamsearch-hamming` — what beam params did they use?
   - `mitchell11/cayleypy-megaminx-first-steps` (13 votes) — the MLP recipe. What architecture? How much training data?
   - Any other top notebooks from the leaderboard
   - If notebooks aren't accessible, search for blog posts, GitHub repos, or forum discussions about the competition

2. **Investigate cayleypy's internal beam_search implementation.** Read the source code (it's installed in the venv). Understand:
   - What state encoding does beam_search actually expect?
   - What does the Predictor wrapper do to the model's output?
   - Are there any undocumented parameters that could help?
   - What's the exact contract for `predictor=` in beam_search?

3. **Research GNN / graph-based approaches for permutation puzzles.** Cayley graphs are natural graph structures. Can a GNN learn better distance estimates than a flat MLP?

4. **Look for alternatives to beam search.** Are there other search algorithms that work well on Cayley graphs? Monte Carlo tree search? Best-first search with learned heuristic?

**Deliverable:** A findings report (`output/findings.md`) with concrete, actionable approaches. Each finding should include:
- What the approach is
- Why it might beat 44114
- How to implement it (API calls, architecture, etc.)
- Estimated compute cost

Do NOT produce a solution file — focus entirely on research quality.
