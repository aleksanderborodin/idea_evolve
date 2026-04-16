---
type: idea
id: idea_006
name: Hamming-distance predictor baseline
lifecycle: active
confidence: 0.8
first_seen: gen_001
last_updated: gen_001
last_confirmed_gen: gen_001
supported_by: [gen001_research_1]
contradicted_by: []
related_ideas: [idea_003]
cluster: machine_learning
tags: [predictor, heuristic, zero_training]
---

# Hamming-Distance Predictor Baseline

## Concept

`Predictor(graph, 'hamming')` is a built-in zero-cost predictor in cayleypy that uses Hamming distance (number of positions differing from solved state) as the distance estimate. No training data or model training required.

## Evidence

research_1 confirmed this shortcut exists. It provides a crude but admissible heuristic: Hamming distance is always ≤ true optimal distance.

## Why It Matters

Before investing time in training an MLP predictor, compare against this zero-cost baseline. If Hamming-guided beam search doesn't beat cancellation, the MLP needs significant quality to matter. If it does beat cancellation, even marginally, that validates the predictor-guided approach.

## Usage

```python
predictor = Predictor(graph, 'hamming')
result = graph.beam_search(start_state=list(state), beam_width=2000, max_steps=200, predictor=predictor)
```

## Status

Not yet tested in any solution. research_1 discovered it but didn't run experiments with it. This is the cheapest possible predictor experiment.