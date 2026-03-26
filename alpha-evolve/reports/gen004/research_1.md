# Research Agent Debrief — gen004_research_1

## Solutions Produced

| File | Score (C) | Elements | Source | Status |
|------|-----------|----------|--------|--------|
| sol01.py | **1.502862898255827** | 30,000 | TTT-Discover (Yuksekgonul et al., arXiv:2601.16175) | NEW BEST |

**Previous best:** 1.5031635546815612 (AlphaEvolve 1319-element array, gen003)
**Improvement:** −0.000301

## 1. What did I try?

**Target 1 — Cell 47 (C≈1.5053, N=600):** Identified in AlphaEvolve notebook. Did not extract to a solution file due to time constraints. Array structure confirmed: 600 elements, values up to ~35, reversed before evaluation.

**Target 2 — Cell 92 (~50000 elements):** Investigated. This is for the **second autocorrelation inequality (C2 problem)**, not the first. Sparse comb structure (9,074 non-zeros, spacing ~172 indices). Not relevant to our problem. Does not correspond to ThetaEvolve's 1.503133 result.

**Target 3 — Yuksekgonul et al. (Jan 2026):** FOUND and RETRIEVED. Paper: "Learning to Discover at Test Time" (TTT-Discover), arXiv:2601.16175, Jan 22 2026. Array: `results/mathematics/ttt_ac1_sequence.json` from `github.com/test-time-training/discover`. 30,000-element array, verified C = **1.502862898255827**.

## 2. What information did I lack?

- The exact URL structure of the TTT-Discover GitHub repo was not in prior knowledge, but WebSearch found it quickly.
- The `ac1_data.py` file referenced in the repo summary did not exist at the expected URL (404). The AlphaEvolve V2 array may exist elsewhere in that repo.
- No information on whether Cell 47 array (N=600) reversal is applied before or after scoring — this matters for warm-start orientation.

## 3. What given facts might be wrong or outdated?

- **"Cell 91 contains ~50000-element ThetaEvolve array"** — WRONG. Cell 92 is for the *second* autocorrelation inequality, not the first. ThetaEvolve's 1.503133 result for the first inequality equals the AlphaEvolve V2 1319-element array per the TTT-Discover SOTA table.
- **"Best known bound: C≤1.5029 by Yuksekgonul"** — NOW VERIFIED at exactly C=1.50286. Slightly worse than the advertised ≤1.5029, but close.
- The SOTA table from the TTT-Discover paper shows ThetaEvolve at 1.50313 and AlphaEvolve V2 at 1.50317. Our current best.py shows 1.5031635, which matches ThetaEvolve (the paper rounds to 5 decimal places).

## 4. Was the State of Affairs accurate?

Mostly yes. The identification of Yuksekgonul 2026 as the new SOTA was correct. The claim that Cell 91 might be ThetaEvolve's 1.503133 was incorrect — it's a different problem. Otherwise the landscape assessment is accurate.

## 5. What would I do differently with more time?

1. Extract and create solution files for ALL intermediate arrays (Cell 47 N=600 at 1.5053, Cell 50 N=600 at 1.5040) — these are immediately usable warm-starts for the gradient pipeline.
2. Search for the AlphaEvolve V2 array specifically (1319-element, C=1.50317) — may be slightly better than our current best.py.
3. Check the TTT-Discover repo for any other array files or improved versions.

## 6. Specific experiments to run next generation

**Highest priority:**
- **Warm-start smooth-max Adam from TTT-Discover 30k array**: Convert to raw_params via inv_softplus, run T=0.005→0.0001 schedule. The 30k-element array gives much finer resolution than the 1319-element one. May find improvements.
- **Extract and evaluate Cell 47 (N=600)**: This is the same resolution as our gradient pipeline. Warm-starting from C=1.5053 with our smooth-max optimizer should get to ~1.505 quickly and may find new basins.
- **Extract and evaluate Cell 50 (N=600)**: C=1.5040, also same resolution, different structure.

## 7. What surprised me?

- The TTT-Discover paper is titled "Learning to Discover at Test Time" — not obviously about autocorrelation. It's a general method that uses LLMs + LP at test time, applied to this problem as one of several math challenges.
- The 30,000-element TTT-Discover array has a very different structure from the AlphaEvolve 1319-element one: mostly uniform low values, near-zero transition, gradual rise, large terminal spike. Almost like a different function family.
- Cell 92 (50k elements) being for the second inequality, not first, resolves a 3-generation mystery.
- Our `best.py` is ThetaEvolve's result (1.50316), not AlphaEvolve V2's (1.50317) — they are the same 1319-element array. The TTT-Discover paper lists them separately but they likely share the array.

## 8. Helper tools feedback

- `problem/helper.py` (`compute_c`) worked correctly and gave consistent results with the notebook's formula.
- `problem/evaluate.py` was fast (0.25s for 30k elements) due to FFT-based computation.
- No helpers from `problem/helpers/` were used.
- A helper that converts a large array to raw_params (inverse softplus) for warm-start optimization would save significant time for the exploit agents.
