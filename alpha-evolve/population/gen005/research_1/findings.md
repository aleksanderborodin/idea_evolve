# Research Findings — AlphaEvolve Intermediate Array Extraction

## Summary

All 5 intermediate arrays from the AlphaEvolve notebook have been extracted and verified as solution files. The two highest-priority arrays (N=600, C≈1.5053 and C≈1.5040) are now immediately usable as warm-starts for the existing gradient pipeline at native resolution. This completes the extraction task deferred from gen 4.

---

## Finding 1: Two N=600 Warm-Start Candidates Now Available

**Relevance**: Exploit and explore agents using gradient descent at N=600

**Detail**: The AlphaEvolve notebook contains two published solutions at N=600 (same resolution as our gradient pipeline):
- `sol01.py`: C = **1.5052939** (Cell 46) — spiky, sparse structure, values in [0, 9.0]
- `sol02.py`: C = **1.5039528** (Cell 49) — uniform structure, values in [0, 1.17]

Both are verified valid, all-non-negative arrays of length exactly 600. They represent two structurally distinct solution families that LP-guided search found early in its optimization trajectory.

**Actionable implication**: Exploit agents should warm-start from these arrays using inv_softplus conversion + smooth-max Adam at T=0.005→0.0001. No interpolation required. Starting from C=1.5053 or C=1.5040 vs the gradient basin at C~1.509 means agents begin much closer to the competitive region. The different structural families (spiky vs uniform) may lead to different optimization basins.

---

## Finding 2: Higher-Resolution Arrays Available (N=984 to N=5000)

**Relevance**: Agents willing to run optimization at higher resolution

**Detail**: Three additional arrays were extracted at higher resolutions:
- `sol03.py`: N=984, C = **1.5035598** (Cell 52) — oscillating pattern
- `sol04.py`: N=1444, C = **1.5034847** (Cell 54) — smooth structure
- `sol05.py`: N=5000, C = **1.5032245** (Cell 58) — fine-grained values ~0.01-0.04

The N=5000 array at C=1.5032 is comparable quality to our best population member (rank02, 1319 elements at C=1.5032). However it represents a different structural approach — very fine-grained values vs. the 1319-element array's more concentrated structure.

**Actionable implication**: For agents with compute budget for N>600: warm-start from sol05.py (N=5000) with smooth-max Adam at native resolution. The N=5000 fine-grained structure may be more amenable to gradient refinement than the 1319-element sparse structure. Also: interpolating sol05 down to N=1319 and comparing structures might reveal useful patterns.

---

## Finding 3: AlphaEvolve Optimization Trajectory Shows C Decreasing from 1.5053 to 1.5032

**Relevance**: All agents — understanding what LP-guided search accomplishes

**Detail**: The verified scores form a monotonic descent:
```
Cell 46 → C=1.5053 (N=600)
Cell 49 → C=1.5040 (N=600)
Cell 52 → C=1.5036 (N=984)
Cell 54 → C=1.5035 (N=1444)
Cell 58 → C=1.5033 (N=5000)
Cell 60 → C=1.5032 (N=1319, our rank02)
```

This is the LP-guided memetic algorithm's trajectory. The improvement from C=1.5053 to C=1.5033 happens as the algorithm refines its LP relaxation and explores higher-resolution grids. Importantly, the improvement from C=1.5053 to C=1.5040 at the SAME resolution (N=600) demonstrates that gradient-style refinement at fixed N can find meaningful improvements.

**Actionable implication**: The gap between C=1.5053 and C=1.5040 at N=600 (0.0013) was achieved by LP refinement. Our smooth-max Adam may be able to replicate or exceed this. Additionally, the gap from C=1.5033 (N=5000) to C=1.5029 (TTT-Discover, N=30000) suggests higher resolution is one path to improvement.

---

## Finding 4: Cell 46 Array Has Reversed Orientation in Notebook

**Relevance**: Exploit agents warm-starting from sol01.py

**Detail**: The AlphaEvolve notebook Cell 46 stores `best_sequence` and then evaluates `best_sequence[::-1]` for verification. Since autoconvolution is symmetric (max(f★f) is unchanged by reversing f), both orientations give the same C value. Our sol01.py uses the original (non-reversed) orientation.

**Actionable implication**: If structurally combining sol01.py with other solutions (e.g., genetic crossover), be aware that the "effective" orientation used in the notebook's optimization was the reversed version. This may matter if the LP algorithm's local neighborhood assumed a particular orientation. Running optimization on both `arr` and `arr[::-1]` from sol01.py as separate warm-starts might explore both orientations.

---

## Open Questions

1. **Can smooth-max Adam improve on C=1.5040 (sol02) at N=600?** The LP algorithm went from C=1.5053 to C=1.5040 at N=600. Can our gradient optimizer starting from C=1.5053 reach C=1.5040 or better? What is the gradient landscape near these published solutions?

2. **Is the N=5000 array (sol05) in a different basin from the 1319-element array (rank02)?** Both are near C=1.5032 but structurally different. Do they converge to the same local minimum under gradient optimization, or lead to different attractors?

3. **Can cross-interpolating the two N=600 arrays generate useful warm-starts?** sol01 (spiky) and sol02 (uniform) are structurally very different. Linear combinations may create solutions in unexplored regions of the function space.
