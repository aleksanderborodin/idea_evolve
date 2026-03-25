# Debrief Report — gen002 explore_1

## Solution Scores

| File | C (fitness) | Valid | Notes |
|------|-------------|-------|-------|
| sol01.py | 1.5188 | yes | coarse-to-fine N=40→150→600, cold fine stage — no improvement |
| sol02.py | 1.5093 | yes | **NEW BEST** coarse-to-fine N=80→600, warm fine stage — beats gen001 best by 0.0015 |
| sol03.py | TIMEOUT | — | 3-stage N=80→200→600, 12 restarts — too expensive (>600s) |

**Best solution this session: sol02.py, C = 1.5093**

---

## 1. What did I try?

**Approach:** Coarse-to-fine optimization combined with smooth-max (log-sum-exp temperature annealing), as directed. This was the #1 unexplored high-priority combination from the coverage matrix.

**sol01 (C=1.5188):** 3-stage pipeline (N=40 → N=150 → N=600). Each stage used smooth-max annealing. Critical mistake: fine stage started cold (T=0.001). Result: essentially matched the baseline, no improvement. The cold fine stage negated the benefit of coarse initialization.

**sol02 (C=1.5093):** 2-stage pipeline (N=80 → N=600). Coarse stage: warm temps (T=0.1→0.001), 5 phases × 8k steps. Fine stage: identical to gen001's best sol03 schedule (T=0.05→0.01→0.003→0.001→0.0003, 5 phases × 15k = 75k steps). 8 restarts with multi-bump random asymmetric init. **Beat the generation 1 best (C=1.5108) by 0.0015.**

**sol03 (TIMEOUT):** 3-stage with N=200 intermediate, 6-phase fine annealing (20k steps/temp), 12 restarts. Estimated 2.4M total steps — timed out at 600s.

---

## 2. What information did I lack?

- **Exact time budget per solution:** I had to estimate 600s limit, but the exact per-seed runtime wasn't predictable without profiling. This led to sol03 being over-budgeted by ~4×.
- **The gen001 sol03 score files:** The `# fitness: TBD` header in the reference solution (population/gen001/full_1/sol03.py) meant I had to infer its C=1.5108 from the state_of_affairs rather than its header.
- **Whether GPU/XLA is available:** JAX performance varies dramatically with hardware. Timing estimates assumed CPU.

---

## 3. What given facts might be wrong or outdated?

- The state_of_affairs says best score is 1.5108. This is now surpassed by sol02 (1.5093). The coverage matrix should be updated with the new `idea_007 + idea_004` combination.

---

## 4. Was the State of Affairs accurate?

Yes, accurate. The dead ends list correctly warned about multi-scale with cold gradient descent failing (1.5270-1.5730). The fix (warm smooth-max at coarse stage) was the key. The coverage matrix correctly identified `idea_007 + idea_004` as unexplored.

---

## 5. What would I do differently?

1. Profile a single seed first to estimate per-seed runtime, then set restarts accordingly.
2. Skip the 3-stage approach — 2-stage (coarse→fine) with more restarts is better use of budget.
3. Run a quick grid search over coarse resolution (N=30, 60, 90, 120) with 1 restart each to find the optimal coarse size before committing to many restarts.

---

## 6. Specific experiments to run

1. **Multi-restart coarse selection:** Run 20 coarse restarts (N=80, 10k steps each, cheap), keep top 5 by C at coarse scale, upsample all 5 to N=600 for full fine annealing. Same total budget, more basin diversity.

2. **Warm-start from sol02 result:** Load sol02's output array as initial condition for a new fine-tuning run with tighter schedule (T=0.0003→0.0001→0.00003, 50k steps each). May push from 1.5093 toward 1.505.

3. **Optimal coarse N sweep:** N=30, 50, 80, 120 coarse, 1 restart, evaluate after upsampling. Find which N best preserves basin information.

4. **Add L-BFGS final polish:** After smooth-max converges at fine scale, run scipy L-BFGS-B (which handles box constraints natively) for 1000 steps. Literature suggests this gives a clean final refinement.

---

## 7. What surprised me?

1. **How much the fine-stage temperature matters.** sol01 vs sol02 differ mainly in the fine-stage starting temperature (T=0.001 vs T=0.05), and the result changes from 1.5188 to 1.5093 — a gap of 0.0095. This is bigger than the entire improvement sol03 achieved in gen001.

2. **The wide variance across seeds in sol02** (1.509 to 1.555). Despite the coarse stage finding a good basin, the fine stage still has a strong random-restart dependence. The coarse stage doesn't uniquely determine the fine minimum.

3. **N=40 was too coarse.** Moving to N=80 for the coarse stage (sol02 vs sol01) helped significantly, suggesting 40 parameters is not enough to characterize the basin of attraction.

4. **sol02 beats gen001's best (1.5108) without any additional tricks** — just coarse-to-fine + warm fine stage. This validates the research agent's Finding 3 about coarse-to-fine being the highest-impact strategy.
