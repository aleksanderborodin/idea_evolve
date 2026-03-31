---
type: idea
id: idea_018
name: "vpshufb Nibble-LUT Kernel"
lifecycle: active
confidence: 0.2
first_seen: generation_2
last_updated: generation_2
last_confirmed_gen: 2
supported_by: []
contradicted_by: []
related_ideas: [idea_001, idea_011]
cluster: cluster_001
tags: [vpshufb, lut, nibble, compute-kernel, alternative]
---

Replace the ternarylogic + 2×popcnt + sub compute path with a precomputed
16-entry nibble lookup table (LUT) via `vpshufb`. For each nibble (4 bits)
of the AND/ANDNOT result, look up the contribution directly.

The current compute path per k-byte per row uses:
- 2× vpternlogd (port 0/5)
- 2× vpopcntb (port 0/1)
- 1× vpsubb (port 0/5)

A vpshufb-based approach would precompute: for each ternary row value and
each possible 4-bit pattern of B, the contribution. Then use vpshufb as a
parallel nibble lookup.

This was suggested by explore_2 but never implemented. The potential benefit
is changing the instruction mix to use different execution ports, potentially
alleviating the port 5 bottleneck identified by experimentator_1.

Risk: vpshufb operates on 128-bit lanes on AVX-512 (not cross-lane), which
may complicate the mapping. Also, the LUT approach requires splitting bytes
into nibbles (mask + shift), adding instructions that may offset the gains.

Untested. Low confidence. Needs empirical evaluation to determine if the
instruction mix change actually improves throughput.
