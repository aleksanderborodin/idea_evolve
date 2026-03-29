## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen009/exploit_1/sol01.py` → C = 1.5028628682228971
Second best: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen009/explore_1/sol01.py` → C = 1.5028628683413456

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_023.md` — minimax multi-element perturbation (your primary target)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/clusters/cluster_001.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/patterns/active/pattern_017.md` — ultra-fine delta resolution gap
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/patterns/active/pattern_018.md` — quintuplets at noise floor
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen009/exploit_1.md` — 13 plateau positions within 1e-12 of max
- `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen009/exploit_1/sol01.py` — current best
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/compute_c_f64.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/incremental_autoconv_update.py`

## Directive

**Implement and test minimax multi-element perturbation (idea_023) — the highest-priority untested idea.**

Current perturbation methods compute the gradient at a single argmax position. But the gen 9 best has **13 autoconvolution positions within 1e-12 of the max**. After a perturbation reduces the value at argmax, a different plateau position becomes the new max, nullifying the gain. Minimax perturbation addresses this by finding directions that reduce ALL plateau positions simultaneously.

**Implementation plan:**

1. **Analyze the plateau structure.** Load gen 9 best, compute autoconvolution, find all positions where `autoconv >= max(autoconv) * (1 - 1e-12)`. Report how many positions K there are and how tightly they cluster.

2. **Implement minimax triplet perturbation:**
   - For a candidate triplet (i, j, k), compute the gradient of autoconv at EACH of the K plateau positions. This gives K gradient vectors of length 3 (in the sum-zero subspace, 2 free variables).
   - Solve a small LP: minimize t subject to `g_p · d <= t` for all K plateau positions p, with `d1 + d2 + d3 = 0` and `||d||_inf <= step_size`.
   - If optimal t < 0, the direction d reduces max(autoconv) across ALL plateau positions.
   - Apply the perturbation, verify with exact incremental update, accept if C improves.

3. **Run minimax triplet trials:** 50k trials with different index selections (S0/S1/S3 strategies). Compare hit rate to standard single-peak triplets.

4. **If minimax triplets work:** Also try minimax quadruplets (3 free variables, K constraints). The LP is still tiny (K=13, 3 variables).

5. **After minimax:** Run standard ultra-fine CD as a final polish pass.

**CRITICAL: Time-budget guard.** Add to `entrypoint()`:
```python
import time
_DEADLINE = time.time() + 500
if time.time() > _DEADLINE:
    break
```

**For the LP solver:** Use `scipy.optimize.linprog`. The LP is tiny (K≈13 constraints, 2-3 variables) and solves in microseconds.

**What NOT to do:**
- Do NOT use standard single-peak gradient for perturbation — that approach has been exhausted (0 improvements in gen 9 after ultra-fine CD).
- Do NOT attempt quintuplets — definitively at noise floor (pattern_018).
- Do NOT spend more than 30% of your time on implementation; prioritize running trials.

**Key question to answer:** Does minimax perturbation find improvements where single-peak perturbation finds none? If yes, how many and at what magnitude?
