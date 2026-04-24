---
type: pattern
id: pattern_009
name: Solution quality scales logarithmically with beam width
lifecycle: active
confidence: 0.85
first_seen: gen_004
last_updated: gen_004
evidence: [gen004_research_1]
related_ideas: [idea_003, idea_015]
tags: [beam_search, beam_width, scaling, logarithmic, dominant_parameter]
---

# Solution Quality Scales Logarithmically with Beam Width

## Observation

The CayleyPy RL paper (arXiv:2502.18663) explicitly states: "solution length is almost
linearly improving on logarithm of beam size." This means doubling beam width produces
a constant improvement in solution quality, regardless of the current width. All our
experiments used beam_width=4096 at most — competitive solutions likely use 65536 or higher.

## Evidence

The CayleyPy team achieves 98% optimality on 3x3 Rubik's cubes. Research_1 (gen004) calculated
that beam_width=65536 with batch_size=2048 should be feasible on our RTX 5060 Ti (16 GB),
using approximately 300 MB per batch with the MlpModel (one-hot encoding).

## Implication

Beam width is likely THE dominant parameter — more impactful than model architecture
(embedding vs one-hot), training data quality (BFS vs random walks), or algorithmic
enhancements (MITM). The priority order should be:
1. Scale beam_width to maximum GPU memory allows (65536+)
2. Use non-backtracking mode (idea_015, 4x success rate)
3. Use library's MlpModel (idea_014)
4. Improve training data depth (idea_016)

Our current beam_width=4096 may be leaving 4+ doublings (16x) of beam-width improvement
on the table. Each doubling likely saves a constant number of moves per puzzle.
