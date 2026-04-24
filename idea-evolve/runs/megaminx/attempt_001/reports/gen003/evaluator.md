# Evaluator Report — Generation 003

strategic_shift: false

## Summary

Gen 3 produced a marginal new best score (44094, +20 over gen002) but the generation's
real value is in research_1's 10 findings, which identify the root cause of the predictor
stall (wrong model architecture) and a concrete path forward (combined recipe idea_013).
Three of five agents failed completely with zero output.

## Score Analysis

| Metric | Value |
|--------|-------|
| Gen 3 best | 44094 |
| Gen 2 best | 44114 |
| Improvement | 20 points (0.05%) |
| Total valid solutions | 1 |
| Total failed agents | 3/5 |
| Agent success rate | 40% |

The improvement is statistically negligible. The raw integer MLP predictor saved only 20
moves across 101 puzzles (10 puzzles improved). This is the expected result when the model
architecture treats categorical permutation data as ordinal integers.

## Knowledge Extracted

### New Ideas
1. **idea_010** (BFS exact training data): 19.4M samples with perfect distance labels, computed in 1s. Replaces noisy random walks.
2. **idea_011** (Embedding MLP): Correct categorical representation for permutation states. 5.3x lower loss than raw integer MLP.
3. **idea_012** (Built-in MITM+beam): CayleyPy's `bfs_result_for_mitm` halves required beam depth. Never used.
4. **idea_013** (Combined recipe): BFS + embedding + MITM + compression. The top priority experiment.

### Updated Ideas
- idea_008: Confidence reduced (raw integer MLP is ineffective; architecture fix needed)
- idea_009: Confirmed established (7th confirming solution)
- idea_007: Debunked (classical heuristic search also failed in gen003)

### New Patterns
- pattern_006: Raw integer MLP is ineffective — categorical representation required
- pattern_007: Complex algorithm tasks cause agent timeouts with zero output

## Key Findings

### 1. The Model Architecture Was Wrong All Along

The most important finding of gen003: the `_PredictorMLP` in the helper module treats
permutation positions as ordinal integers. An embedding-based model achieves 5.3x lower
loss. This single insight explains two generations of stalled predictor experiments.

### 2. Three New Verified-But-Uncombined Components

BFS exact training data (idea_010), embedding architecture (idea_011), and MITM backstop
(idea_012) are each individually verified by research_1. The combined pipeline (idea_013)
is the strongest theoretical path forward but has NOT been tested end-to-end.

### 3. Agent Productivity Crisis

3/5 agents produced zero output. Combined waste: ~3+ hours of GPU compute. The pattern
is consistent: agents given complex implementation tasks timeout at all phases (work,
wrap-up, debrief) with nothing recoverable. The system must redesign how complex tasks
are assigned and staged.

### 4. Compression Ceiling Confirmed

7 solutions across 2 generations converge at 44114 ± 4. Gen003 explore_2 confirmed that
even longer patterns (length 6+) and wider beams find no additional savings. The
compression-only era is definitively over.

## Unexplored Regions

1. **idea_013 combined recipe**: The #1 priority. All components verified individually.
2. **A*/phased solving/scramble structure**: explore_1 was supposed to investigate these
   but produced nothing. Four directions remain entirely unexplored.
3. **GNN-based predictors**: research_1 suggested this but didn't implement. The flat
   MLP (even with embeddings) may not capture enough structure for deep puzzle guidance.
4. **Kaggle solution analysis**: We still don't know what the top competitors use. Their
   8050 proxy equivalent suggests a fundamentally different approach than compression+beam.

## Recommendations for Gen 4

1. **Execute idea_013 as the primary task.** Assign an explore agent specifically to
   implement the combined recipe with incremental milestones: (a) BFS + train embedding
   MLP + verify on 1 puzzle, (b) add MITM backstop + test on 10 puzzles, (c) full proxy
   evaluation with compression fallback.

2. **Fix the helper module.** An experimentator should update `trained_predictor_beam_search.py`
   with the embedding architecture, BFS training data generation, and MITM support. This
   is a small, well-specified task that should be achievable.

3. **Stage complex tasks incrementally.** No agent should be asked to "implement the full
   predictor pipeline" in one shot. Break into: verify API → train model → test 1 puzzle →
   scale up. Save partial results at every step.

4. **Investigate agent failures.** Three agents producing nothing is a pipeline problem,
   not an agent problem. Consider shorter per-phase timeouts with faster failover, or
   adding checkpoint saves at intermediate steps.

## Staleness Check

| Idea | last_confirmed_gen | Stale? (5+ gens) |
|------|-------------------|-------------------|
| idea_001 | gen_001 | Yes (2 gens ago, but established) |
| idea_002 | gen_001 | Debunked, N/A |
| idea_003 | gen_002 | No |
| idea_004 | gen_001 | Yes (2 gens stale, not tested since gen1) |
| idea_005 | gen_002 | No |
| idea_006 | gen_002 | Debunked, N/A |
| idea_007 | gen_003 | Debunked this gen |
| idea_008 | gen_003 | No (confirmed this gen) |
| idea_009 | gen_003 | No (confirmed this gen) |

idea_004 (MITM) hasn't been tested since gen001. With the discovery of idea_012 (built-in
MITM), idea_004 is effectively superseded for practical purposes. Consider archiving idea_004
in favor of idea_012.

---

## Debrief

### 1. What did I try?

I read all 5 agent outputs (2 with results, 3 empty), 6 debrief reports, the knowledge dump
(721 lines), existing solution-idea map, coverage matrix, and research findings (349 lines).
I analyzed the single scored solution (gen003_explore_2_sol01, 44094) in detail — its two-phase
compression+predictor architecture, its tail-beam-search strategy, and why it only saved 20 moves.

I cross-referenced research_1's 10 findings against all existing ideas to identify 4 genuinely
new ideas (010–013) that represent verified-but-uncombined advances. I updated 3 existing ideas
(007 debunked, 008 confidence reduced, 009 confirmed established). I created 2 new patterns
documenting the architecture problem and the agent failure mode.

### 2. What information did I lack?

- **The problem description file** (`problem/description.md`) referenced in my prompt does not
  exist at the expected path. I couldn't read the official problem specification. This is a
  minor gap since I had sufficient context from the knowledge base.
- **No light evaluator outputs existed for gen003** — the `knowledge/group_notes/gen003/`
  directory doesn't exist. This suggests the manifest was single-group or light evaluation
  was skipped. No consolidation was needed.
- **I don't know the exact cayleypy API** — my knowledge comes from research_1's findings
  and agent reports, not from reading the library source code myself. I trust research_1's
  analysis but cannot independently verify the BFS layer sizes or MITM interface claims.
- **Helper module contents** — I know the `trained_predictor_beam_search.py` helper exists
  in the experimentator's sandbox, but I didn't read its exact code to verify what changes
  are needed.

### 3. What given facts might be wrong or outdated?

- **State of Affairs says "trained MLP predictor NEVER TESTED end-to-end."** This is now
  outdated — explore_2_sol01 DID test it (with marginal results). The SoA needs updating
  to reflect: tested with raw integer MLP → marginal; corrected architecture untested.
- **idea_008's pipeline code uses random walks for training.** This is suboptimal per
  idea_010 (BFS data is strictly better) but not wrong per se.
- **The architect report mentions "PROXY_SIZE=100 typo" and "CPU-only" claim.** I couldn't
  verify these since description.md is missing. These should be fixed but are low priority.

### 4. Was the State of Affairs accurate?

Mostly yes. The strategic assessment (compression exhausted, predictor is the path) was
correct. The dead ends list was accurate. The coverage matrix correctly reflected what had
been tried.

**Missing from the SoA:**
- The `bfs_result_for_mitm` parameter (idea_012) — a built-in capability no one knew about
- The model architecture problem (idea_011) — two generations of stalled predictor work
  explained by a representation error
- BFS depth 6 as exact training data (idea_010) — superior to random walks in every dimension
- The hasher compatibility requirement — a silent failure mode for MITM

The SoA was accurate about WHAT but incomplete about HOW — it correctly identified the
predictor as the path forward but didn't know about the architectural issues blocking it.

### 5. What would I do differently with more context?

- **Read cayleypy source code myself** to independently verify research_1's API claims about
  `bfs_result_for_mitm`, BFS layer access, and Predictor interface contract. I'm trusting
  one agent's source-code analysis for the most critical findings of the generation.
- **Compute the expected score improvement** from the combined recipe more rigorously. My
  "35000–40000 optimistic" estimate is a guess. With BFS layer sizes and beam width
  estimates, I could project more precisely.
- **Check the experimentator's sandbox helper code** to understand exactly what needs to
  change and whether it can be incrementally fixed vs. rewritten.

### 6. Specific experiments to run?

1. **idea_013 combined recipe benchmark.** BFS depth 6 → train EmbeddingMLP(dim=32) → MITM
   beam search on all 101 proxy puzzles with compression fallback. This is the one experiment
   that matters most.

2. **Architecture A/B test.** Run the same pipeline with (a) raw integer MLP, (b) embedding
   MLP, both on BFS data. Compare beam search success rates and final fitness. This quantifies
   the architecture impact.

3. **MITM depth sweep.** Test MITM depth [0, 4, 5, 6] with fixed predictor. Measure how
   much the backstop helps at each depth.

4. **Beam width scaling with MITM.** Test beam_width=[1024, 2048, 4096, 8192] with MITM
   depth 6 and embedding predictor on a fixed set of puzzles across all buckets.

### 7. What surprised me?

- **The raw integer MLP architecture was wrong for 2 generations.** I expected implementation
  bugs or hyperparameter issues, not a fundamental representation error. The fact that
  research_1's controlled experiment showed 5.3x loss difference is striking.
- **research_1's productivity.** A single research agent produced 10 findings that are each
  individually actionable. This is the highest-value single agent output of the entire run
  despite producing no scored solution.
- **Three agents failing completely.** I expected some failures but 3/5 with zero output is
  alarming. The pattern where all three phases timeout suggests a systemic issue with how
  complex tasks are assigned.
- **The 20-move improvement.** I expected the trained predictor to save more than 20 moves,
  even with the wrong architecture. The predictor's effective range (suffixes ≤12 moves from
  solved) is extremely narrow.

### 8. Helper tools feedback?

I did not directly use any helpers from `problem/helpers/`. My analysis was based on reading
code files, score files, and reports. The helpers I'm aware of:
- `helpers/core.py`: Used by all solution agents. No bugs reported in gen003.
- `helpers/trained_predictor_beam_search.py`: Has the wrong model architecture (idea_011).
  Needs to be updated with embedding-based model before any agent uses it again.

A helper I wish existed: `bfs_exact_training_data(graph, max_depth=6)` that returns
(X, y, bfs_result) in one call. Currently research_1 had to figure this out from source
code and every future agent will need to rediscover it.

### 9. Time budget?

Sufficient. I completed all 10 output files within the session. The analysis was
straightforward — only 1 scored solution to evaluate, and the research findings were
well-structured by research_1. With more time I would have:
- Read the cayleypy source code to independently verify research_1's claims
- Computed the expected score improvement from idea_013 more rigorously
- Checked the experimentator's sandbox helper code for specific changes needed
- Attempted to read the Kaggle competition page for top solution details
