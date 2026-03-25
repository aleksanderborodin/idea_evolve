---
id: fact_004
type: fact
name: "Available tools"
confidence: 0.8
first_seen: generation_0
verified: false
source: user-provided
tags: []
---

JAX with optax is available for gradient-based optimization. helper.py provides
a differentiable compute_c function. The initial program uses Adam optimizer
with warmup cosine schedule for 40000 steps.
