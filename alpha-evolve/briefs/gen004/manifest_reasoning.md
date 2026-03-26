# Manifest Reasoning — Generation 4

## Situation Assessment

**Score trajectory:** Gen 1 best 1.5108 → Gen 2 best 1.5091 → Gen 3 best 1.5032. The gen 3 jump was a strategic shift — the 1.5032 score came from retrieving a published AlphaEvolve array, not from gradient-descent improvement. Our gradient-descent pipeline has plateaued at C ≈ 1.509.

**Diversity status:** All gradient-descent solutions cluster tightly in the 1.509x basin (pattern_005, confirmed). The AlphaEvolve solution (1.5032) has qualitatively different structure (sparse, multi-peaked). Two distinct solution families exist but only one (AlphaEvolve) is below target.

**Key finding from gen 3:** The original target (C ≤ 1.5053) is beaten. The new frontier is C < 1.503. Yuksekgonul et al. (2026) report C ≤ 1.5029 as current SOTA.

## Agent Mix Rationale

### exploit_1 (opus, 1500s) — Warm-start smooth-max at native resolution

The #1 priority experiment per the System Critic, Evaluator, and Consistency Reviewer. Apply our best optimization technique (smooth-max Adam with temperature annealing) to the AlphaEvolve solution at its native N=1319 resolution. The hypothesis: smooth-max may find improvements that AlphaEvolve's LP-guided algorithm missed, since the two methods navigate local landscapes differently.

**Opus** because precision matters — this is refinement of the best known solution. Small improvements (0.0001) are meaningful at this frontier.

**1500s timeout** because gen 3 exploit_1 used 1200s work + 111s wrap-up. Multiple seeds × multiple temperature phases will need the full budget.

### exploit_2 (opus, 1500s) — Warm-start at different resolutions

Distinct from exploit_1 by operating at NON-native resolutions. Three strategies: upsample to N=2000+ (higher resolution may reveal fine details), downsample to N=80 then upsample (coarse-to-fine from warm start), and sensitivity-guided coordinate refinement. These test whether resolution is a limiting factor for the AlphaEvolve solution.

**Opus** for the same precision reason as exploit_1.

### research_1 (sonnet, 900s) — Retrieve additional published arrays

Three specific retrieval targets: Cell 46 (N=600, C ≈ 1.5053 — immediately usable at our standard resolution), Cell 91 (~50k elements, possibly ThetaEvolve's 1.503133), and Yuksekgonul 2026 (C ≤ 1.5029). Each successfully retrieved array becomes a new warm-start target.

**Sonnet** because retrieval doesn't require opus-level reasoning. **900s** is sufficient based on gen 3 research_1 completing in 723s.

### explore_1 (sonnet, 1200s) — Calibrated coarse-SA at N=23

One final attempt at coarse-scale SA, this time with MANDATORY temperature calibration before committing to the full run. All 3 gen-3 SA attempts failed because metro_temp was too high (96-100% acceptance). The brief includes an explicit calibration protocol. N=23 is used because Boyer et al. found it effective and it has fewer local minima than the N=30-80 range we tried before.

**Sonnet** because the implementation is straightforward once calibration is done. **1200s** based on gen 3 explore times.

## Parallelization

All 4 agents in one parallel group. Rationale:
- exploit_1 and exploit_2 can warm-start from `population/best.py` immediately (already available).
- research_1 retrieves NEW arrays that feed gen 5, not gen 4.
- explore_1 is independent from all others.

The System Critic recommended sequencing research before exploitation, but that was for gen 3 where the research result wasn't yet available. Now `population/best.py` exists with C=1.5032, so exploit agents don't need to wait.

## What I Deliberately Did NOT Do

1. **No experimentator** — Sensitivity mapping (experiment E7) would be informative but not directly score-improving. The exploit agents will learn about sensitivity through their optimization runs. Budget spent on actual optimization.

2. **No full agent** — The cold-start approach from random initialization is exhausted at C ≈ 1.509. A full agent would waste budget.

3. **No genetic crossover** — The two solution families (AlphaEvolve sparse multi-peak at N=1319 vs gradient-descent smooth at N=600) are structurally incompatible for meaningful crossover. Their representations differ too much.

4. **No second research agent** — One research agent with 3 clear targets is sufficient. Splitting would waste overhead.

5. **Kept to 4 agents** (minimum 3 required, max 8). Four focused agents with high-impact directives is better than 6-8 agents with overlapping scope.

## Risks

1. **Warm-start may fail if the 1.5032 basin is already fully converged.** Mitigation: two exploit agents with different approaches (native resolution vs multi-resolution). If both fail, we know the basin is exhausted and need LP-guided or fundamentally different optimization.

2. **Research may not find new arrays.** Yuksekgonul 2026 may not be publicly available yet. Cell 91 may not be what we think. Mitigation: Cell 46 (the most reliable target) is prioritized first.

3. **Coarse-SA calibration may show SA is fundamentally ineffective at this problem.** Mitigation: this is a one-shot test — if calibrated SA still doesn't find better basins, SA is definitively dead and we stop investing in it.

## Timeout Justification

| Agent | Timeout | Rationale |
|-------|---------|-----------|
| exploit_1 | 1500s | Gen 3 exploit used 1311s total. Multiple seeds × multi-phase schedule needs room. |
| exploit_2 | 1500s | Multiple strategies (A, B, C) sequentially. Same compute needs as exploit_1. |
| research_1 | 900s | Gen 3 research used 723s. Three retrieval targets but each is simple web fetch + eval. |
| explore_1 | 1200s | Calibration step + full SA run + fine-tuning. Gen 3 explore_1 used 1590s but much of that was wasted on uncalibrated runs. 1200s should suffice with the calibration protocol front-loading the important step. |
