---
id: fact_003
type: fact
name: "Computation method"
confidence: 0.8
first_seen: generation_0
verified: false
source: user-provided
tags: []
---

Autoconvolution is computed via FFT with zero-padding. The function is discretized
on [-1/4, 1/4] with uniform grid spacing dx = 0.5/N where N is array length.
C = max(f*f * dx) / (sum(f)*dx)^2.
