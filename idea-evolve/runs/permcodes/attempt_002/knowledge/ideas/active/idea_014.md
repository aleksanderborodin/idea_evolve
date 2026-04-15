---
type: idea
id: idea_014
name: "Simulated Annealing for Permutation Codes"
lifecycle: active
confidence: 0.4
first_seen: gen_01
last_updated: gen_01
last_confirmed_gen: null
supported_by: []
contradicted_by: []
related_ideas: [idea_006, idea_013]
cluster: cluster_002
tags: [simulated-annealing, SA, stochastic, temperature, unexplored]
---

# Simulated Annealing for Permutation Codes

## What It Is

A stochastic optimization technique that accepts worse solutions with probability exp(-Δ/T), where Δ is the decrease in score and T is the current temperature. Allows escaping local optima that greedy and ILNS get trapped in.

## How It Would Work

1. Start from a greedy code (e.g., 616 AGL-orbit or 262 direct greedy)
2. **Move operator**: swap one codeword for a compatible non-codeword, or add/remove codewords
3. **Acceptance**: If new_score > old_score, accept; else accept with probability exp(-(old-new)/T)
4. **Cooling**: Geometric cooling T_new = α × T_old (α ≈ 0.995-0.999)
5. Repeat until convergence or temperature near zero

## Evidence

- **Not yet implemented** in any generation 1 solution
- Research findings confirm no published SA parameters for M(n,d) specifically
- ILNS (which can be viewed as SA with reheating) caps at ~293
- SA with proper move operators might escape the local optima that ILNS cannot

## Current Status

**Unexplored**. Proposed by multiple agents but not implemented.

## Expected Performance

Unknown. Move operator design is critical. If SA starts from the 616 AGL code and finds even 1 additional compatible permutation, it would be a new result.

## Key Challenges

1. **Move operator**: Adding/removing single codewords destabilizes the code; need clever operators
2. **Temperature tuning**: Too high = random walk; too low = greedy convergence
3. **Acceptance of worse solutions**: May waste compute on poor solutions

## Relationship to Other Ideas

SA can be combined with VNS (systematic neighborhood + SA acceptance criterion). Could also be used to search for individual extensions to the 616 AGL code.
