# Observations — gen002 explore_1

## Summary

Directive: implement coarse-to-fine optimization combined with smooth-max (log-sum-exp annealing).
The coverage matrix identified this as the #1 unexplored high-priority combination.

---

## sol01 — C = 1.5188 (worse than baseline)

**Approach:** 3-stage coarse-to-fine (N=40 → N=150 → N=600) with smooth-max.
Fine stage started COLD (T=0.001→0.00003). 6 restarts. ~136k steps/restart.

**What happened:** C=1.5188, essentially matching the raw baseline (1.5185). Slightly worse than sol03 (1.5108).

**Why it failed:** The fine stage started at T=0.001, which is much colder than sol03's T=0.05. The coarse-to-fine gave a decent initialization, but the cold fine stage just locked into the local minimum near the initialization without spreading the gradient effectively. The coarse grid (N=40) is also quite sparse — only 40 control points to map out the global basin, which may not capture enough structure.

---

## sol02 — C = 1.5093 (new best — beats sol03 gen001 by 0.0015)

**Approach:** 2-stage coarse-to-fine (N=80 → N=600) with smooth-max.
Fine stage starts WARM (T=0.05, same as sol03's winning schedule). 8 restarts. ~115k steps/restart.

**Key fix:** Fine stage now uses full 5-phase warm-to-cold annealing (0.05→0.01→0.003→0.001→0.0003), same as gen001's best solution. Coarse stage uses warm temps (0.1→0.05→0.02→0.005→0.001).

**What happened:** C=1.5093. Beat the previous best (1.5108) by 0.0015. Individual seeds ranged from 1.509 to 1.555. Seed 6 was exceptional at 1.5093.

**Why it worked:** The coarse optimization at N=80 explores basin structure fast (cheap forward passes), then upsampling gives the fine stage a better-than-random initialization. The warm fine stage still runs full annealing and can escape any residual coarse-scale local minima. This is strictly better than starting from scratch at N=600.

**Key insight confirmed:** The failure of vanilla multi-scale in gen1 (1.5270-1.5730) was entirely due to the cold gradient descent at the coarse stage locking into bad basins. With warm smooth-max at coarse scale, the right basin is found before upsampling.

---

## sol03 — TIMEOUT (did not complete)

**Approach:** 3-stage (N=80 → N=200 → N=600), 6-phase fine annealing, 12 restarts.
Estimated ~200k steps/restart × 12 = 2.4M total steps. Far exceeded 600s timeout.

**Lesson:** 12 restarts × 3 stages is too expensive. Must stay within ~8 restarts × 2 stages OR reduce steps-per-temp significantly.

---

## Key Takeaways

1. **Coarse-to-fine + warm smooth-max works and beats the gen1 best.** C=1.5093 vs 1.5108.
2. **The fine stage MUST start warm (T≥0.01).** Starting cold negates the benefit of coarse initialization.
3. **N=80 coarse is better than N=40.** More structure preserved through upsampling.
4. **3-stage with 12 restarts exceeds timeout.** Budget ~6-8 restarts for 2-stage pipeline within 600s.
5. **Diminishing returns observed:** Seeds within a run vary widely (1.509 to 1.555), suggesting the landscape still has many local minima. More restarts + more budget = more consistent results.

## Unexplored Directions (recommended for next gen)

- **More restarts at coarse stage + pick top-K for fine:** Run 20+ cheap coarse restarts, keep best 5, upsample all 5 to fine. More exploration for same budget.
- **Warm-start from sol02's best function:** Further fine-tuning of C=1.5093 with tighter annealing schedule may reach 1.505-1.503.
- **Adaptive temperature:** If the fine stage C doesn't improve for N steps, increase temperature temporarily (restart from perturbed state).
- **N=600 coarse-to-fine starting from the gen002 best:** Use coarse optimized for diversity (many restarts), then fine-tune only the best few.
