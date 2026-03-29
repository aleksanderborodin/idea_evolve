# Observations — Research Agent gen005_research_1

## Summary

Successfully extracted and verified all 5 intermediate published arrays from the AlphaEvolve notebook. Primary objective achieved: Cell 46 (N=600, C=1.5053) and Cell 49 (N=600, C=1.5040) are now solution files ready for warm-start optimization. Additionally extracted Cell 52 (N=984, C=1.5036), Cell 54 (N=1444, C=1.5035), and Cell 58 (N=5000, C=1.5033).

## Verified Solutions

| File | Cell | N | Verified C | Expected C | Notes |
|------|------|---|------------|------------|-------|
| sol01.py | 46 | 600 | **1.5052939684401607** | 1.5053 | PRIMARY warm-start candidate |
| sol02.py | 49 | 600 | **1.5039528121183459** | 1.5040 | PRIMARY warm-start candidate |
| sol03.py | 52 | 984 | **1.5035598601465194** | 1.5036 | Oscillating structure |
| sol04.py | 54 | 1444 | **1.5034847157116410** | 1.5035 | Smooth structure |
| sol05.py | 58 | 5000 | **1.5032244982597613** | 1.5033 | Near-AlphaEvolve V2 quality |

All scores match expected values within rounding.

## Array Structure Analysis

### Cell 46 (sol01.py, N=600, C=1.5053)
- Values in range [0, ~9.0] — large dynamic range
- Sparse: many near-zero values in the middle
- Spiky at start and end (multi-peaked structure)
- Original notebook stores as `best_sequence` with a `best_sequence[::-1]` reversal in the verification step. Autoconvolution is symmetric so reversal doesn't affect C.

### Cell 49 (sol02.py, N=600, C=1.5040)
- Values in range [0, ~1.17] — moderate dynamic range
- More uniform than Cell 46, values mostly in [0.07, 0.18]
- Near-zero transition region in the middle
- Different structural family from Cell 46

### Cell 52 (sol03.py, N=984, C=1.5036)
- Oscillating pattern (~0.07/0.17), regular alternation
- Denser spacing than N=600

### Cell 54 (sol04.py, N=1444, C=1.5035)
- Smooth values starting ~0.11-0.12
- Values in [0, ~0.95]

### Cell 58 (sol05.py, N=5000, C=1.5033)
- Very fine-grained, values ~0.01-0.04
- Similar score to AlphaEvolve V2 (1.5032)

## Key Insight for Exploit Agents

The N=600 arrays (sol01, sol02) are **immediately usable** as warm-starts for the existing gradient pipeline without any interpolation. The pipeline already operates at N=600. These represent two distinct solution families at the same resolution as our optimizer, starting at C=1.5053 and C=1.5040 respectively — well above our gradient baseline of 1.5090 but potentially in different basins.

The N=5000 array (sol05) at C=1.5033 is close to the AlphaEvolve V2 result (1.5032). Warm-starting from this at high resolution could yield improvements if the optimizer can find the same or better basin.

## AlphaEvolve V2 Note

The gen4 research checked for an AlphaEvolve V2 array distinct from the 1319-element one (rank02). Based on the SOTA table from TTT-Discover paper: ThetaEvolve at 1.50313 = AlphaEvolve V2 at 1.50317 — they appear to be the same array. Our current best.py (1.5031635) is this array. No new AlphaEvolve V2 array was found or needed.
