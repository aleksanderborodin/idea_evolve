# Debrief Report — gen002_explore_2

## 1. What did you try?

| Solution | Approach | Fitness | Notes |
|----------|---------|---------|-------|
| sol01.py | Empirical identity mining (336 rules) | **44114** | **BEST** — 4.7% improvement over baseline |
| sol02.py | Systematic commutator enumeration (432 rules) | 44118 | Slightly worse than sol01 |
| sol03.py | Combined systematic + empirical | 44118 | Same as sol02 |
| sol04.py | String substring replacement | INVALID | Bug — corrupted paths with empty moves |
| sol05.py | Systematic + move-list application | 44118 | Same as sol02 |
| sol06.py | Pure internal-cancellation mining (1832 rules) | 46312 | Baseline — useless rules |
| sol07.py | Extended span-6 patterns (888 rules) | 44114 | Tied with sol01 |
| sol08.py | Bucket-aware compression | 44114 | Tied with sol01 |

**Summary**: All valid solutions used the algebraic identity approach. The best achieved **44114** (compression_ratio=0.8723), compared to baseline 46312 (0.9158). Improvement: **4.7%**.

## 2. What information did you lack?

1. **The full Megaminx Cayley graph structure**: Understanding which generators commute or have nice relations would help find more identities faster.

2. **Knowledge of how the test set was generated**: The State of Affairs mentions depth == id for ids 1..1000. Understanding the random walk process better might reveal generation artifacts we could exploit.

3. **What the Kaggle top solutions actually did**: The consistency review mentioned fedimser's beam-search notebook but we haven't studied it.

4. **Per-puzzle optimal path lengths**: Knowing the true optimal for each puzzle would let us measure how far from optimal our compression is.

## 3. What given facts might be wrong or outdated?

The State of Affairs says `very_hard bucket (ids 501-1000) = 74.8% of score`. Looking at my best solution:
- very_hard fitness: 33026 (out of 44114 total = **74.8%**) — confirmed correct.

The `initial_ideas.md` claims "5-15% improvement" from X.-X cancellation. My result shows ~8.4% from basic cancellation and ~4.7% more from algebraic identities. The total possible compression is ~13.1% from the sample_submission floor.

## 4. Was the State of Affairs accurate?

Yes, mostly accurate:
- Best score: 46312 ✓
- Compression baseline established ✓
- Predictor-guided search never tested ✓
- very_hard bucket dominates ✓

The State of Affairs mentioned idea_005 (commutator/identity discovery) was "unexplored" — which was the focus of my work. The result (44114) is a valid new data point for this idea.

## 5. What would you do differently with more or different context?

1. **Start with the empirical approach from sol01 immediately**: The systematic enumeration (sol02-05) was wasted effort — it produced nearly identical or worse results. The empirical approach was clearly superior from the start.

2. **Focus on search-based methods sooner**: The algebraic identity approach has a ceiling around 44114. The gap to target (15000) is ~29K which requires fundamentally different techniques (ML-guided search, pattern databases, etc.).

3. **Test identities on full 1001 set earlier**: All my experiments were on the 101-puzzle proxy. The identities might behave differently at full scale.

## 6. Specific experiments to run

1. **Combine compression + beam search**: Use compressed paths as starting points for beam search, rather than the raw sample_submission paths. This could let beam search explore from better starting positions.

2. **Per-puzzle identity learning**: Instead of global identities, learn which identities apply to which puzzle types (based on depth bucket, scramble structure, etc.).

3. **Higher-order commutator search**: Test 3-generator commutators [A,[B,C]] and similar nested structures.

4. **ML predictor with compressed starting points**: Train a predictor and use compressed paths as starting states for beam search. The compression step is free improvement that could make beam search more effective.

## 7. What surprised you?

1. **Empirical beat systematic**: I expected systematic enumeration to find more/better rules, but empirically observing patterns in sample_submission was more valuable than mathematically valid but rarely-occurring identities.

2. **Very_hard bucket compression is hard**: The very_hard bucket went from 33026 to 33026 (sol01) or 33028-33030 (other attempts). Deep scrambles don't have as many algebraic identities in their paths.

3. **String replacement is catastrophic**: A single misuse of Python string `.replace()` corrupted entire paths. Move-list manipulation is the only safe approach.

4. **The 4.7% ceiling is real**: Multiple independent approaches (empirical, systematic, span-6, bucket-aware) all converged to ~44114. This appears to be the genuine ceiling for algebraic identity compression.

## 8. Helper tools feedback

The `helpers.core` module was correct and complete:
- `apply_path`, `is_solved`, `solved_state` worked perfectly
- `GENERATOR_NAMES` was complete and correct
- No bugs found

**What I wished existed**: A function to enumerate all valid identities of a given span programmatically, rather than having to discover them empirically. Also, a way to compute the Cayley graph distance (optimal path length) for individual puzzles would help measure how sub-optimal our compressed paths are.

## 9. Time budget

**Sufficient time**: ~15 minutes total for 8 solution iterations. All solutions evaluated successfully except sol04 (string replacement bug).

**Key time waste**: sol02-05 (systematic enumeration approaches) took ~10 minutes to evaluate and produced no improvement over sol01. If I had started with the span-6 extension of sol01 immediately, I might have found additional insights.

**With more time**, I would:
1. Test the compressed paths on full 1001-puzzle set
2. Try beam search from compressed starting points
3. Investigate the 2 puzzles that didn't improve (the 2 that stayed at baseline compression ratio = 1.0)
