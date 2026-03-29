## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen010/explore_2/sol01.py` → C = 1.5028628681165177
Second best: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen010/explore_1/sol01.py` → C = 1.5028628681659377

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/clusters/cluster_001.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/patterns/active/pattern_024.md` — CD works via integral adjustment, not peak reduction. This is the KEY insight for this task.
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/patterns/confirmed/pattern_020.md` — integral-preserving multi-element moves exhausted (348k+ trials, 0 improvements)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen010/explore_1.md` — minimax LP null result, CD mechanism discovery
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen010/explore_2.md` — 0 triplet/quad improvements after ultra-fine CD
- `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen010/explore_2/sol01.py` — current best
- `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen009/exploit_1/sol01.py` — base array
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/incremental_autoconv_update.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/compute_c_f64.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/plateau_analyzer.py` — finds near-max autoconv positions and per-element gradients

## Directive

**Test non-integral-preserving multi-element moves.** This is the highest-priority untested direction identified independently by 3 agents and the evaluator in gen 10.

**Background:** All tested multi-element approaches (triplets, quadruplets, minimax LP) required integral preservation (d1 + d2 + ... + dk = 0). They all found 0 improvements. But CD works precisely because it changes the integral (pattern_024). The question: can coordinated 2-element moves that also change the integral find improvements that single-element CD cannot?

**Phase 1 — Load array and analyze plateau** (~500s):
1. Run gen010_explore_2/sol01.py's entrypoint() to get the 30k array (~490s).
2. Use `plateau_analyzer.plateau_analysis(f)` to find near-max autoconv positions and gradients.
3. Record K (number of near-max positions at various thresholds).

**Phase 2 — Non-integral-preserving 2-element optimization** (~800s):
For pairs (i, j), find the (d_i, d_j) that minimizes C_new without constraining d_i + d_j = 0:

```python
# For each candidate pair (i, j):
# C = max(autoconv) / integral^2
# Try a grid of (d_i, d_j) values, both free
# Use top-K pre-screening to quickly check if any (d_i, d_j) improves C
# Key: unlike integral-preserving moves, both elements can move in the same direction
```

**Pair selection strategies to try:**
1. **Gradient-guided:** Use plateau_analyzer gradients. Select pairs where gradient directions suggest coordinated moves could reduce multiple plateau positions.
2. **High-sensitivity pairs:** Elements with largest |∂C/∂f_i| (from sensitivity helper or finite differences).
3. **Neighboring elements:** Adjacent elements (i, i+1) where coordinated change preserves local smoothness.
4. **Random pairs from nonzero elements:** Broad sampling for discovery.

For each pair, try a 2D grid of perturbations: d_i, d_j ∈ geomspace(1e-13, 1e-6, 20) × {+, -} = 1600 combinations per pair. Use top-K screening (K=30) for fast rejection.

Target: test at least 10,000 pairs across all strategies.

**Phase 3 — Follow-up CD** (remaining time):
Regardless of Phase 2 results, run ultra-fine CD (geomspace 1e-14 to 1e-1, 100 values, per-round FFT resync) on the array to squeeze out additional improvements. Bake final array into sol01.py.

**What to report:**
- How many pairs tested per strategy
- How many improvements found (if any) — this is the critical data point
- If improvements found: what's the typical magnitude? Are they in regions CD couldn't reach?
- If zero improvements: this confirms the solution is locally optimal for ALL 2-element perturbations (much stronger than the current integral-preserving-only null result)

**What NOT to do:**
- Do NOT constrain d_i + d_j = 0 (that's the old approach — already dead)
- Do NOT skip Phase 3 CD even if Phase 2 finds nothing — we still want score improvement
