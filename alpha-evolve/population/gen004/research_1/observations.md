# Observations — Research Agent gen004_research_1

## Summary

Primary objective was to retrieve additional published solution arrays: Cell 46 (C≈1.5053, N=600), Cell 91 (~50000 elements), and Yuksekgonul et al. (Jan 2026, C≤1.5029).

**Result: SUCCESS — NEW BEST FOUND.** The TTT-Discover array (Yuksekgonul et al., arXiv:2601.16175) was retrieved and verified at C = **1.502862898255827**, beating our current best of 1.5031635546815612.

## Solution Retrieved

- **sol01.py**: TTT-Discover array (30,000 elements), C = **1.502862898255827**
  - Source: Yuksekgonul et al., "Learning to Discover at Test Time", arXiv:2601.16175, Jan 22 2026
  - GitHub: https://github.com/test-time-training/discover
  - Array file: `results/mathematics/ttt_ac1_sequence.json` (key: "sequence")
  - Improvement over previous best (1.5031635): **−0.000301**
  - Method: LP with heuristic focusing on near-tight constraints (top-K positions where convolution is largest)

## Notebook Structure (AlphaEvolve Repository)

The notebook at `github.com/google-deepmind/alphaevolve_repository_of_problems/experiments/autocorrelation_problems/autocorrelation_problems.ipynb` contains 94 cells total. Key arrays:

| Cell | Score | Elements | Notes |
|------|-------|----------|-------|
| 47 | 1.5053 | 600 | Original AlphaEvolve result; cell ends with `best_sequence[::-1]` reversal |
| 50 | 1.5040 | 600 | Contains np.float64() wrappers, values in [0, 0.25] |
| 52 | 1.5036 | 984 | Oscillating pattern (~0.07/0.17) |
| 54 | 1.5035 | 1444 | Smooth, starts ~0.11-0.12 |
| 56 | 1.5035 | 1416 | Starts ~0.5-0.7 |
| 58 | 1.5033 | 5000 | Very fine-grained, values ~0.01-0.02 |
| 60 | 1.5032 | 1319 | Our current best (retrieved gen003) |
| 92 | — | 50000 | SECOND autocorrelation inequality (different problem — C2 ≥ 0.961, NOT first) |

**Critical note on Cell 92:** This is NOT for the first autocorrelation inequality. It is for the second inequality (C2 problem). The sparse comb structure (9,074 non-zero elements out of 50,000, spacing ~172 indices) confirms this is a different problem entirely. ThetaEvolve's 1.503133 result is actually the same as AlphaEvolve V2's 1319-element array per the TTT-Discover paper's state-of-the-art table.

## SOTA Table (from TTT-Discover paper)

| Method | C1 | n |
|--------|----|---|
| TTT-Discover (gpt-oss-120b) | **1.50286** | 30,000 |
| TTT-Discover (Qwen3-8B) | 1.50287 | — |
| ThetaEvolve | 1.50313 | 1,319 |
| AlphaEvolve V2 | 1.50317 | 1,319 |
| AlphaEvolve | 1.50525 | — |

Note: "ThetaEvolve" at 1.50313 = our current best.py (1.50316). The paper rounds slightly differently.

## Warm-Start Candidates (Not Yet Retrieved)

Cell 47 (N=600, C=1.5053) and Cell 50 (N=600, C=1.5040) were identified but not extracted into solution files due to time constraints. These are high-priority for the next generation's exploit/explore agents: same N=600 resolution as our gradient-descent pipeline, immediately usable as warm-starts without interpolation.

## Key Insight for Next Generation

The TTT-Discover method (LP + near-tight constraint heuristic) achieves C=1.50286 with a 30,000-element array. The array structure is:
- First ~100 elements: uniform ~0.11-0.13
- Elements ~101-200: near-zero (transition region)
- Elements ~200-29999: gradually rising values ~1e-4 to 0.04
- Last element: large spike ~0.91

This is qualitatively different from the AlphaEvolve 1319-element array. Warm-starting smooth-max Adam from the TTT-Discover array at T=0.005→0.0001 is now the highest-priority experiment.
