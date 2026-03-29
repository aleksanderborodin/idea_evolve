## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen009/exploit_1/sol01.py` → C = 1.5028628682228971
Second best: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen009/explore_1/sol01.py` → C = 1.5028628683413456

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/clusters/cluster_001.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/patterns/active/pattern_020.md` — ordering matters
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen009/explore_1.md` — 150 triplet improvements after standard CD
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen009/experimentator_1.md` — batch_trial_evaluator, 46x speedup
- `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen009/exploit_1/sol01.py` — current best
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/batch_trial_evaluator.py` — 46x speedup for multi-element pre-filtering
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/incremental_autoconv_update.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/compute_c_f64.py`

## Directive

**Extended triplet search with batch_trial_evaluator integration — the first production use of the 46x speedup helper.**

Gen 9 explore_1 found 150 triplet improvements in only 20k trials, and noted the rate didn't plateau. This session will push to 500k+ triplet trials using the batch evaluator for pre-filtering to find hundreds more improvements.

**Protocol:**

1. **Start from gen 9 best** (C = 1.5028628682228971).

2. **Run standard-delta CD first** (`np.geomspace(1e-7, 1e-1, 30)`). This is a quick warm-up pass (~2-5 min) to ensure the starting point is coordinate-wise optimal at standard deltas.

3. **Extended triplet search with batch pre-filtering:**
   - Import: `from helpers.batch_trial_evaluator import batch_predict_c`
   - Sample K=200 candidate triplets per batch
   - Use `batch_predict_c` to rank candidates by predicted improvement
   - Apply exact `incremental_autoconv_update` only to top 20% (40 candidates)
   - Target: 500k+ screened triplets (= 2500 batches of 200)
   - Rotate through strategies: S0 (3 random nonzero), S1 (1 large + 1 small + 1 random), S3 (2 nonzero + 1 random)
   - Use 9 step sizes log-spaced from 1e-1 to 1e-6

4. **After triplets:** Run quadruplet follow-up (50k screened trials) — quadruplets found 8015 improvements in gen 8 when applied after standard CD.

5. **Final polish:** Ultra-fine CD with `np.geomspace(1e-11, 1e-1, 50)`.

**CRITICAL: Time-budget guard.** Add to `entrypoint()`:
```python
import time
_DEADLINE = time.time() + 500
if time.time() > _DEADLINE:
    break
```

**Report requirements:** Report:
- Triplet hit rate (improvements per 1000 screened trials)
- Whether the hit rate plateaued or was still declining at session end
- Measured speedup from batch pre-filtering vs sequential
- Total improvement delta from triplets alone, then from the full pipeline

**What NOT to do:**
- Do NOT use momentum on perturbations — too slow (gen 9 exploit_2 timeout).
- Do NOT attempt quintuplets — noise floor (pattern_018).
- Do NOT skip the initial standard CD pass — triplets work best starting from a standard-delta-converged array.
- Do NOT recompute `np.argmax(autoconv)` on every trial — use the incremental update return value.
