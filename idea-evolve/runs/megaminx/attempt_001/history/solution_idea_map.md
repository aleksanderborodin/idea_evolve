# Solution-Idea Map — Gen 004

## Solution gen004_exploit_1_sol01 (score: 44111, compression_ratio: 0.8722)

**Pipeline:** Compression (336 rules) → BFS depth 6 (MITM backstop) → Embedding MLP
predictor (random walks depth 50, 2.3M samples, 15 epochs) → Beam search (beam_width=4096,
max_steps=60) → compression fallback.

- **Central:** idea_009 (empirical algebraic identity compression, Phase 1) + idea_008
  (trained MLP predictor beam search concept) + idea_011 (embedding MLP — used directly
  in this solution) + idea_012 (MITM backstop via bfs_result_for_mitm)
- **Peripheral:** idea_001 (X.-X baseline cancellation), idea_010 (BFS data for MITM only —
  NOT used as training data here; random walks were used instead)
- **Novel elements:** First solution to test idea_013 (combined recipe) end-to-end. Result
  reveals the bottleneck is training data depth: predictor trained on depth ≤50 data
  cannot guide beam search for hard/very_hard puzzles. Only 2/101 puzzles improved.
- **Key finding:** BFS-only predictor (depth 0–5) predicts every state as ~4 — completely
  useless for deep puzzles. Directly refutes idea_010's "strictly superior" training claim.

## Agent gen004_explore_1 (score: N/A — zero output)

- **Central:** N/A (assigned: GNN predictor + embedding MLP comparison)
- **Peripheral:** N/A
- **Novel elements:** None. Context reading consumed all turns — agent confirmed API
  details and architectural constraints but produced no code. Raised idea of GNN predictor
  using generator-induced adjacency with hand-rolled message passing.

## Agent gen004_explore_2 (score: N/A — no report found)

- **Status:** No debrief report found in reports/gen004/. Agent either produced no output
  or report was not written. No solutions evaluated.

## Agent gen004_experimentator_1 (score: N/A — zero output)

- **Central:** N/A (assigned: write embedding_predictor_beam.py helper)
- **Peripheral:** N/A
- **Novel elements:** None. **Third consecutive generation** with zero experimentator output
  on the helper-writing task. The helper module remains broken (raw-integer MLP). The
  architect should stop routing this task to experimentator role — it's been failing for
  3 straight gens.

## Agent gen004_research_1 (no score — research agent)

- **Central:** research findings (no solution produced)
- **Peripheral:** None
- **Novel elements:** Major literature findings: (1) CayleyPy's MlpModel uses one-hot
  encoding, NOT raw integers — corrects our 2-gen assumption; (2) non-backtracking beam
  search quadruples success rate (17.6% → 69.7%); (3) beam width is the dominant
  parameter (log-linear relationship — paper explicit); (4) random walk training is the
  CayleyPy team's actual approach, not BFS-only. Three new ideas (014, 015, 016) and
  two new patterns (008, 009) created from these findings.

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total agents launched | 5 |
| Agents with output | 2 (exploit_1, research_1) |
| Agents with zero output | 3 (explore_1, explore_2, experimentator_1) |
| Valid solutions scored | 1 (gen004_exploit_1_sol01) |
| Best score this generation | 44111 (gen004_exploit_1_sol01) |
| Overall best score | 44094 (gen003_explore_2_sol01) — unchanged |
| Improvement vs previous best | -17 (REGRESSION) |
| Solutions using idea_009 | 1 |
| Solutions using idea_008/idea_011 | 1 (marginal — training data issue) |
| Solutions using idea_012 (MITM) | 1 (in pipeline but benefit not measured separately) |
| Solutions using idea_013 (recipe) | 1 (confirmed tested — disappointing) |
| Solutions using idea_014 | 0 (not yet tried in solution) |
| Solutions using idea_015 | 0 (not yet tried) |
| Solutions using idea_016 | 0 (not yet tried — TOP PRIORITY) |

---

## Cumulative Map (all generations)

| Solution | Score | Central Ideas | Notes |
|----------|-------|---------------|-------|
| gen001_explore_1_sol01..05 | 46312 | idea_001 | Basic cancellation, 5 variants |
| gen001_explore_2_sol01..08 | 46312 | idea_001 | MITM attempt, all fall back to cancellation |
| gen001_full_1_sol01 | 46312 | idea_001 | Ensemble, same floor |
| gen002_explore_1_sol01..03 | 46312 | idea_001 | Tried IDA*, fell back |
| gen002_explore_2_sol01 | 44114 | idea_005, idea_009 | BEST compression — 336 empirical rules |
| gen002_explore_2_sol02..08 | 44114–44118 | idea_005, idea_009 | Variants of identity compression |
| gen003_explore_2_sol01 | **44094** | idea_009, idea_008 | **ALL-TIME BEST** — compression + raw-integer predictor tail |
| gen004_exploit_1_sol01 | 44111 | idea_009, idea_008, idea_011, idea_012 | Combined recipe — REGRESSION from gen003 |
