## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/best.py` → fitness **44094**.
Compression-only floor: 44114.
Target: **15000 proxy**. Kaggle top-3 full-set ≈ 80499 → ≈ **8050 proxy**.
Gap: we are 5.5× worse than Kaggle top-3.

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/state_of_affairs.md` — current standing + open questions
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/ideas/active/idea_013.md` — what exploit_1 is executing this generation (context only)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/ideas/active/idea_010.md` — BFS training data (context only)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/reports/gen003/research_1.md` — prior research output; do NOT duplicate it
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/megaminx/description.md` — problem spec and evaluation contract

## Directive — Track B RESEARCH MISSION

**This is a Track B research mission.** Find approaches the system has never tried. The gap between our 44094 and Kaggle's ≈8050 is a 5.5× factor — an order-of-magnitude gap. That gap is almost certainly bridged by a qualitatively different paradigm, not by tuning beam_width. Your job is to identify it.

### Two complementary research threads (do both, one report)

#### Thread A — Kaggle winning solutions for `cayley-py-megaminx` (and related Cayley-graph/permutation-puzzle competitions)

Search for:
- Kaggle discussion forums and write-ups for the `cayley-py-megaminx` competition (or its twin Kaggle Santa / permutation-puzzle competitions if the megaminx-specific comp has no public write-ups).
- The top-3 solvers' approach. Did they use: pattern databases? phased/reduction solving (like Thistlethwaite for Rubik's)? neural-network-guided A*? symmetry reduction? precomputed coset tables?
- Specifically look for: **is the top paradigm beam search + learned heuristic, or is it something fundamentally different?** This answers open question #4 in the SoA.
- Any reference to DeepCube / DeepCubeA (UCI's paper on solving Rubik's cube with DRL, published in Nature 2019 "Solving the Rubik's Cube with Deep Reinforcement Learning"). Megaminx is adjacent.

#### Thread B — Algorithmic alternatives to beam search on Cayley graphs

Survey, briefly:
- **IDA\* / iterative-deepening A\***: the classical algorithm for Rubik's-family puzzles (Korf 1997). Works with admissible heuristics (pattern databases). How would it compose with our BFS depth-6 lower bound?
- **Phased/reduction solving**: solve a subgroup first (e.g. all edges placed, ignoring orientation), then refine. Thistlethwaite's algorithm did this for Rubik's (4-phase, each solves one coset). Does an analogous group decomposition exist for the full 120-cell Megaminx permutation group?
- **Pattern databases (PDBs)**: precomputed tables of `state-fragment → exact-distance-to-solved`. Additive PDBs combine multiple fragment tables. Memory/compute tradeoff?
- **GNN-style predictors** on Cayley graphs: treat the state as a graph (cells as nodes, generator-moves as edges), apply a GCN/GIN. Does this outperform flat MLP? Relevant because explore_1 will attempt it.

### Scope and non-goals

- **You do NOT run experiments.** No training, no beam search, no calls to `evaluate.py`. Your output is a findings report that other agents turn into solutions.
- You may use WebFetch/WebSearch liberally — this is a research agent, not a solution agent.
- You may cite papers by arXiv ID or URL. Download PDFs via the `paper-download` skill if you find candidates worth deep-reading (DeepCubeA is almost certainly worth it).
- **Bounded scope:** 6 to 10 findings total. Each finding must be ≤ 300 words. Crisper is better than longer.

### Deliverable: `output/report.md`

Format each finding as:

```
### Finding N — <short title>
**Source:** <paper / kaggle writeup / URL>
**Claim:** <one-sentence claim>
**Evidence:** <what the source actually demonstrates>
**Applicability to megaminx:** <why we can or cannot adapt it>
**Concrete next step a solution agent could take:** <1-2 sentences — specific enough to become a brief>
**Estimated score impact:** <conservative / optimistic, with reasoning>
```

At the top of the report, include a **headline paragraph** (≤ 120 words) answering:

> *"If I had to bet on a single paradigm that closes the 44094 → 8050 gap, which one is it, and why?"*

Be confident. Do not hedge into "many approaches could work." Pick one.

### Mandatory at debrief

- At least 2 of the findings must contain **concrete code-level actionable detail** (API call names, data-structure sketches, or pseudocode) — not just abstract concepts.
- At least 1 finding must address the **very_hard bucket (ids 501–1000, 74.8% of score)** directly. That bucket dominates fitness; if a paradigm doesn't help there, it can't close the gap.
- Explicitly state whether Kaggle top-3 solutions are **public** (write-ups exist) or **private** (no write-up → we are guessing). If public: cite the discussion URL. If private: say so and flag it as a research gap.

### Track B guardrails (from architect.md)

- You are not judged on beating 44114. You are judged on finding genuinely new directions.
- Avoid recommendations already in active ideas (idea_003, idea_008, idea_010–013). Research output that re-derives what research_1 already said in gen003 is wasted. Check `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/reports/gen003/research_1.md` before filing any finding.
