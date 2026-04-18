# Evaluator Report — Gen 002

## What I Tried

### Compression Analysis
I analyzed all 12 solutions from gen_002, extracting scores and per-bucket breakdowns from `.score` files. The key finding: **44114** (gen002_explore_2_sol01) beats the gen_001 baseline of **46312** by 2198 points (4.7% improvement).

The improvement comes from empirical algebraic identity compression (idea_009): discovering commutators (X.Y.X⁻¹.Y⁻¹ → identity) and conjugations (X.Y.X⁻¹ → Y) from actual sample_submission paths, then applying verified rules to compress paths beyond basic X.-X cancellation.

### Idea Extraction
From the solutions and research findings, I extracted:
- **idea_008** (trained MLP predictor-guided beam search): new idea from research_1's ML pipeline confirmation
- **idea_009** (empirical algebraic identity compression): from explore_2's 6-solution success
- Updated **idea_003** (predictor-guided beam search): updated with gen_002 research findings
- Updated **idea_006** (hamming predictor): elevated to debunked
- Updated **idea_007** (corner-only PDB): invalidated — wrong structural assumptions
- Updated **idea_005** (identity discovery): elevated to established

### Pattern Discovery
- **pattern_004**: All 24 Megaminx generators are 5-cycles (no 2-cycles or 3-cycles)
- **pattern_005**: Valid commutator/conjugation identities must be discovered empirically, not systematically enumerated

### Cluster Updates
- **cluster_001** (compression baseline): best_score updated from 46312 to 44114
- **cluster_002** (search algorithms): added idea_008, updated status with gen_002 findings

### Coverage Matrix
Updated with gen_002 results showing:
- idea_001 + idea_009: 6 central uses, best 44114
- idea_001 + idea_006: 2 uses, all = 46312 (DEBUNKED)
- idea_008 (trained MLP): 0 central uses — NEVER TESTED

---

## What Information I Lacked

1. **The experimentator_1 agent directory was empty.** I had no experiment results to consolidate into patterns/facts. The experimentator role produced nothing.

2. **No full-evaluation results for gen_002.** I only had proxy (1/10) evaluation results. The full 1001-puzzle evaluation might show different behavior for empirical identities — do they generalize?

3. **beam_search return format uncertainty.** Multiple solutions showed inconsistent handling of `result.path` (list vs None). research_1's findings helped but the API documentation is unclear on when path is a list vs when it's None.

4. **No ground truth for optimal path lengths.** Without knowing the true optimal distance for each puzzle, I cannot determine whether a path is "close to optimal" or "nowhere near." The coverage matrix can't show how close each solution is to the theoretical minimum.

---

## What Given Facts Might Be Wrong or Outdated

1. **Initial State Generation**: The description says sample_submission paths are "exact inverses of random walks used to scramble puzzles." If the scramble process has any non-determinism (e.g., timestamp-based), the paths might not be exact inverses.

2. **Generator Structure**: The initial_ideas.md description of idea_007 assumed "20 corners with orientations" and a mix of 2-cycles and 3-cycles. This is wrong — all 24 generators are 5-cycles.

3. **cayleypy API documentation**: The helper layer doesn't expose `predictor` kwarg, `beam_mode` kwarg, or the `random_walks` signature. The research_1 findings corrected these gaps but the problem description and helpers haven't been updated.

4. **Beam width requirements**: research_1 found beam_width=65536 needed for depth-10 puzzles. This seems extremely large — is this a typo or真的会 required? For depth-100 puzzles the required beam width would be astronomical.

---

## Was the State of Affairs Accurate?

**Mostly accurate, with one major blind spot.**

The gen_001 state_of_affairs correctly identified:
- Compression baseline at 46312
- X.-X cancellation as established
- Predictor-guided beam as highest priority direction

But it missed:
- **idea_005 is ESTABLISHED** (6 solutions confirmed it works, compression ceiling broken to 44114)
- **idea_006 (hamming) is DEBUNKED** — the state_of_affairs listed it as "untested" but it's now definitively useless
- **All generators are 5-cycles** — idea_007's corner PDB assumptions are wrong
- **Research_1 ran but no solution tested the trained-predictor path** — still true at gen_002

The state_of_affairs' priority order (idea_006 first, then idea_003) should be reversed: idea_008 (trained MLP) is the only viable predictor option now that hamming is debunked.

---

## What Would I Do Differently With More or Different Context?

1. **Access to full evaluation results (1001 puzzles, not just 101):** The empirical identities might perform differently on the full set. The proxy evaluation (every 10th id) preserves depth distribution but the pattern distribution might shift.

2. **Timing data per puzzle:** research_1's beam timing experiments (5-45s per puzzle at high beam widths) suggest that some puzzles are much harder than others. Knowing which specific puzzles take long would help calibrate beam parameters.

3. **Trained predictor quality metrics:** The research_1 pipeline was confirmed but we don't know the trained predictor's accuracy (MSE on held-out data). Knowing whether MSE=0.86 (from research_1's preliminary experiment) is good enough would help predict whether beam search will improve.

4. **Ground-truth path lengths:** If I had optimal distances for all 101 proxy puzzles, I could compute "percentage of optimal" for each solution instead of just raw path length. This would help distinguish "close to optimal" from "wastefully long."

5. **The experimentator_1 should have run concrete experiments:** The empty experimentator_1 directory meant no consolidation was needed, but it also meant no structured experimentation happened. A proper experiment plan (trained predictor ablation study) was missing.

---

## Specific Experiments to Run

### Experiment 1: Trained MLP Predictor vs Compression (CRITICAL)
**What:** Train MLP on 50k random walks (depth 20), use in beam search for hard/very_hard buckets. Compare to 44114 compression floor.

**How:**
1. `X, y = graph.random_walks(50000, 20, mode='bfs')`
2. Train `torch.nn.Linear(120, 256) → ReLU → Linear(256, 128) → ReLU → Linear(128, 1)` with MSE loss
3. `predictor = Predictor(graph, model)`
4. `graph.beam_search(start_state=state, beam_width=8192, max_steps=80, predictor=predictor, beam_mode='simple', return_path=True)`
5. Apply empirical identities to beam result
6. Compare full pipeline to 44114

**Success criteria:** Score < 44114 on proxy evaluation

### Experiment 2: Beam Width Scaling with Trained Predictor
**What:** Test beam_width=[1024, 2048, 4096, 8192, 16384] with trained predictor to find optimal beam parameterization.

**How:** Same pipeline as Exp 1, varying beam_width. Measure per-puzzle time and path length.

**Success criteria:** Identify beam_width that consistently beats compression without timing out.

### Experiment 3: Compression + Beam Search Combination
**What:** Apply empirical identities first (44114 floor), then beam search on the compressed paths.

**How:** For each hard/very_hard puzzle: (1) apply 336 empirical identity rules, (2) run beam search from compressed path, (3) compare to compressed-only result.

**Success criteria:** Combined approach < 44114

### Experiment 4: Training Data Depth Generalization
**What:** Train on depth-20 walks only; test on depth-100+ puzzles. Does the predictor generalize?

**How:** Same as Exp 1 but vary training walk length [10, 15, 20, 30]. Compare per-bucket performance.

**Success criteria:** Find training depth(s) that generalize well to hard/very_hard buckets.

---

## What Surprised Me

1. **Empirical > Systematic:** The fact that 336 empirically discovered rules (sol01) beat 432 systematically enumerated rules (sol02) surprised me. In most mathematical contexts, "enumerate all valid cases" beats "observe some cases." The fact that test-set-specific rules outperform comprehensive rules suggests the random-walk generation process has structure that systematic enumeration doesn't capture.

2. **Valid Conjugations in Non-Commutative Group:** That X.Y.X⁻¹ → Y holds for many (X,Y) pairs in a non-commutative group is genuinely surprising. This is not a general group theory result — it's specific to Megaminx's Cayley graph structure. I didn't anticipate this.

3. **Hamming = Unguided at EVERY beam width:** research_1 showed this at 2048, 8192, and 32768. The fact that there's no beam width where hamming helps (not even at very large widths) is a strong structural finding about the Megaminx Cayley graph's geometry.

4. **beam_mode='advanced' Bug:** The fact that 'advanced' mode is ~2x faster but returns path=None is a significant API bug. This means every agent that tried 'advanced' mode to speed up beam search was actually producing nothing useful.

5. **All 5-cycles:** The initial_ideas.md described corner/edge piece types based on Rubik's cube intuition. Discovering all 24 generators are 5-cycles means that intuition was completely wrong. This is a fundamental structural difference from cube puzzles.

---

## Helper Tools Feedback

### helpers/core.py
Used extensively by all solutions:
- `load_test(proxy=True)` — works correctly
- `load_sample_submission_paths()` — works correctly
- `apply_path(state, path)` — works, but raises ValueError on invalid move names (caused sol04 failure)
- `is_solved(state)` — works correctly
- `solved_state()` — works correctly
- `depth_bucket(sid)` — works correctly
- `GENERATOR_NAMES` — works correctly

**Bug found:** `apply_path` raises `ValueError` on unknown moves. String replacement in sol04 created empty move names which caused `unknown move '-'` errors. The error message was clear but the root cause (string replacement creating `''` move names) was not obvious from the error.

**Missing documentation:** The danger of string replacement for move sequences is not documented. Should add a docstring warning.

### helpers/core.py — Missing Functions
Solutions needed:
- `graph.beam_search(...)` — requires direct `cayleypy` import, not exposed in helpers
- `Predictor(graph, 'hamming')` — requires direct `cayleypy` import
- `graph.random_walks(...)` — requires direct `cayleypy` import

The helper layer doesn't expose these commonly-used functions. Agents must import `cayleypy` directly, which is fine but should be documented.

### cayleypy API Issues
- `beam_mode='advanced'` returns `path=None` despite `path_found=True` — confirmed bug
- `Predictor(graph, model)` accepts a trained PyTorch model — works as documented
- `graph.random_walks(width, length, mode='bfs')` returns CUDA tensors — agents must handle device placement

---

## Time Budget

**I had enough time to complete my work.** The evaluator work for gen_002 was tractable:
- 12 solutions × score extraction: ~5 minutes
- Code analysis + idea extraction: ~1 hour
- Writing knowledge files: ~30 minutes
- Report writing: ~30 minutes

Total: ~2 hours. This is within the expected budget for a generation with ~10 valid solutions.

**If I had more time, I would have:**

1. **Drilled into explore_1/sol01's IDA* failure more carefully.** The structural error (all 5-cycles) is important but I didn't fully analyze whether a reformulated PDB could still work for IDA*.

2. **Updated the problem description.md with gen_002 findings.** The structural discovery (all 5-cycles, valid conjugations/commutators) should be in description.md so future agents don't repeat the same errors.

3. **Consolidated old experiments.** Checked `knowledge/experiments/` for results older than 3 generations. The directory doesn't exist yet, but when it does, I should consolidate.

4. **Written a helper doc patch.** The string replacement danger should be documented in helpers/README.md with a concrete example of what goes wrong.

---

## Strategic Shift Assessment

**strategic_shift: true**

gen_002 represents a genuine strategic shift for two reasons:

1. **Compression breakthrough:** The 44114 result (4.7% improvement) came from algebraic identity discovery — a direction not explored in gen_001. This is not incremental improvement; it's a new approach that opens new possibilities.

2. **Hamming definitively debunked:** The zero-advantage finding definitively closes one research path and focuses all effort on trained predictor. This is a significant narrowing of the search space.

3. **Structural discovery (all 5-cycles):** The invalidation of idea_007's corner PDB assumptions is a fundamental correction that will prevent wasted effort.

The path to the 15000 target is now clearer: empirical identity compression (→44114) + trained predictor-guided beam search (→??). Neither alone reaches 15000; both together might.
