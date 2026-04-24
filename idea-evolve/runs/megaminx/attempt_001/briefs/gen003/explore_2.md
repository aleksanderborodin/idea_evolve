## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/best.py` → fitness 44114 (compression_ratio=0.8723)
Second best: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/top/rank02_44114.py`

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/ideas/active/idea_008.md` — Trained MLP predictor (primary path)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/ideas/active/idea_009.md` — Empirical compression (current best)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/megaminx/description.md` — Problem specification
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/gen002/explore_2/sol01.py` — Best compression code (336 rules, 44114)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/history/coverage_matrix.md` — Coverage map (avoid saturated areas)

## Directive

**Combine compression + predictor-guided beam search in a two-phase approach.** This is REC-7 from the system critic: nobody has tried applying beam search to already-compressed paths. The hypothesis is that beam search starting from a better baseline should find shorter paths more easily.

**Phase 1 — Compression (proven):**
Import and use the compression approach from explore_2/sol01 (or re-implement the 336 empirical identity rules). This gets every path to ~44114 level.

**Phase 2 — Trained predictor beam search on compressed paths:**
1. Generate training data: `graph.random_walks(width=50000, length=20, mode='bfs')`
2. Train MLP: `Linear(120, 256) → ReLU → Linear(256, 128) → ReLU → Linear(128, 1)`, MSE, 10 epochs
3. For each compressed path, get the intermediate state, then run beam_search with the trained predictor
4. If beam finds a shorter path → use it. If not → keep the compressed path.

**Critical details:**
- Use `beam_mode='simple'` only (advanced has path-return bug)
- States must be `int8` tensors on CUDA (same device as model) — exploit_1 hit errors here
- `random_walks` is keyword-only: `width=`, `length=`, `mode=`
- Focus on hard/very_hard buckets (ids 101-1000) — 74.8% of score is very_hard
- Do NOT use string replacement for moves — use move-list manipulation

**Evaluation strategy:**
1. Write the combined solution to `output/sol01.py`
2. Run `python3 evaluate.py output/sol01.py` immediately
3. Verify `.score` file created
4. If combined approach beats 44114, that's a breakthrough
5. If it doesn't beat 44114, the result is still critical information

**Fallback:** If the trained predictor pipeline doesn't work (state encoding errors, etc.), try unguided beam search from compressed paths. Even unguided beam from a compressed baseline might find improvements that unguided beam from raw paths doesn't.

**Off-limits:**
- Do NOT try Hamming predictor (debunked)
- Do NOT try MITM (useless for deep puzzles)
- Do NOT try more compression tuning (exhausted at 44114)
