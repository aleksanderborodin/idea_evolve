---
type: idea
id: idea_003
name: "Individual Permutation Extension"
lifecycle: established
confidence: 0.9
first_seen: gen_01
last_updated: gen_01
last_confirmed_gen: gen_01
supported_by: [gen001_explore_1_sol02, gen001_full_1_sol02]
contradicted_by: []
related_ideas: [idea_001]
cluster: cluster_001
tags: [extension, greedy, orbit, M(8,5)]
---

# Individual Permutation Extension

## What It Is

After finding a clique of orbits, try to add individual permutations that are NOT in any of the selected orbits but are compatible with all existing codewords. Uses `fast_compatible_mask()` for efficient compatibility checking against the full 40320-permutation space.

## How It Works

1. Find the maximum orbit clique (e.g., 11 AGL orbits → 616 codewords)
2. Identify all 40320 permutations NOT in the orbit clique
3. Compute `fast_compatible_mask()` for the current code
4. Filter to non-orbit permutations that are compatible
5. Greedily add compatible permutations

## Evidence

- **2 attempts**: explore_1/sol02 and full_1/sol02
- **Result**: Both found exactly **0 compatible non-orbit permutations**
- The 616 AGL-code is "orbit-closed" — no individual extension exists
- This strongly suggests 616 is maximal for any AGL-based construction

## Current Performance

**0 extensions added** across all attempts. The orbit clique appears to be maximal within the AGL structure.

## When It Helps

If a different group action (PGL, PSL) yields a larger orbit clique, individual extension might add more codewords from outside that group's orbits.

## Implications for Strategy

This idea is valuable as a diagnostic: running individual extension on a code tells you whether that code is maximal. Future agents should run this check as a matter of course on any promising code.
