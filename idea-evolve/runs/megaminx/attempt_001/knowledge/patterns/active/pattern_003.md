---
type: pattern
id: pattern_003
name: very_hard bucket dominates score — 76.7% of fitness
lifecycle: active
confidence: 1.0
first_seen: gen_001
last_updated: gen_001
evidence: [gen001_full_1_sol01]
related_ideas: [idea_003]
tags: [bucket_analysis, very_hard, score_distribution]
---

# very_hard Bucket Dominates Score — 76.7% of Fitness

## Observation

The per-bucket fitness breakdown for all gen_001 solutions:
- very_hard (ids 501-1000, 50 puzzles): 34634/46312 = 74.8% of total fitness
- hard (ids 101-500, 40 puzzles): ~24% of total fitness
- medium (ids 26-100, 8 puzzles): ~1% of total fitness
- short + special: negligible

The very_hard bucket is where the score is won or lost. Even a 50% improvement there (17k → 8.7k) would bring fitness from 46312 to ~28k, close to the 15k target.

## Implication

Optimization effort should be almost entirely focused on the very_hard bucket. Improving short/medium/hard buckets from 46312 → 40000 would require significant work; improving very_hard from 46312 → 15000 would achieve the target.

The practical implication: solutions that spend beam search budget on short/medium puzzles are optimizing the wrong part of the problem.