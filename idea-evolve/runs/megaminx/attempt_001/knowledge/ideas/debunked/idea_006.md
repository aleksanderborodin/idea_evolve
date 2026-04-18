---
type: idea
id: idea_006
name: Hamming-distance predictor baseline — DEBUNKED
lifecycle: debunked
confidence: 1.0
first_seen: gen_001
last_updated: gen_002
last_confirmed_gen: gen_002
supported_by: []
contradicted_by: [gen002_research_1]
related_ideas: [idea_003, idea_008]
cluster: machine_learning
tags: [predictor, heuristic, zero_training, debunked]
---

# Hamming-Distance Predictor Baseline — DEBUNKED

## What Was Claimed

`Predictor(graph, 'hamming')` is a zero-cost predictor using Hamming distance (number
of positions differing from solved state) as the distance estimate. No training required.
Claimed to be a useful admissible heuristic.

## Why It Fails

**CRITICAL FINDING from research_1 gen002:** Hamming distance provides ZERO advantage
over unguided search at identical beam widths. Controlled experiments:

| Puzzle (depth) | Beam Width | Unguided Path Len | Hamming Path Len | Sample Len |
|---|---|---|---|---|
| sid=10 (depth 10) | 2048 | 14 | 14 | 10 |
| sid=10 (depth 10) | 8192 | 12 | 12 | 10 |
| sid=10 (depth 10) | 32768 | 10 | 10 | 10 |

Both guided and unguided find identical path lengths at every beam width. The hamming
distance to solved state does not correlate with actual shortest-path distance for the
Megaminx Cayley graph.

## Implication

Do not spend any time on idea_006. The zero-cost experiment answer is: hamming doesn't
help. This definitively answers the first priority question from gen001's state of affairs.

The entire beam search improvement ceiling depends on a **trained MLP predictor** that
learns actual distance from random walk data. Only idea_008 (trained MLP) is viable.

## Evidence

gen002_research_1 findings.md — controlled experiments with identical beam widths
comparing hamming-guided vs unguided beam search.

## Status

DEBUNKED. Hamming predictor should not be used in place of compression for any bucket.
