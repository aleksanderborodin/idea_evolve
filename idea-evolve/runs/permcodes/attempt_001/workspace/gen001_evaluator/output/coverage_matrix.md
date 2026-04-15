# Coverage Matrix

| Idea Combination | Times Tried | Best Score | Avg Score | Last Tried |
|------------------|-------------|------------|-----------|------------|
| greedy alone | 1 | 262 | 262 | gen000 |
| AGL(1,8) construction | 0 | — | — | — |
| ILS perturbation | 0 | — | — | — |
| Alternative algebraic groups | 0 | — | — | — |
| Tabu search | 0 | — | — | — |
| Partial orbit mixing | 0 | — | — | — |

**Summary:** Only one approach has been evaluated (greedy baseline, 262). All strategic approaches (AGL, ILS, alternative groups) have zero trials in gen001 despite being assigned to agents. The coverage matrix is essentially empty.

**Key takeaway:** The most important idea combinations to try are:
1. AGL(1,8) construction (expected 616+)
2. ILS starting from AGL(1,8) code (potential to exceed 616)
3. Alternative groups (AΓL, PGL, PSL) — unknown potential
4. Partial orbit mixing with AGL(1,8) orbits
