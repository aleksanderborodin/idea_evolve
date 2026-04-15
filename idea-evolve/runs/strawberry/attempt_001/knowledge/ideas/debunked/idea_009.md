---
type: idea
id: idea_009
name: "yolo11s + exp5 via pretrained= causes shape mismatch"
lifecycle: debunked
confidence: 0.9
first_seen: gen_002
last_updated: gen_002
last_confirmed_gen: gen_002
supported_by: [sol_004]
contradicted_by: []
related_ideas: [idea_001]
cluster: cluster_003
tags: [architecture-mismatch, pretrained-flag, yolo11s, exp5]
---

## What It Is

Attempting to combine yolo11s model scale with exp5 domain-adapted weights via Ultralytics' `pretrained=WEIGHTS_EXP5` parameter on a yolo11s model architecture.

## How It Was Supposed to Work

Load `yolo11s-seg.pt` (yolo11s architecture, 10.1M params) and fine-tune it using `pretrained=WEIGHTS_EXP5` to initialize from the converged strawberry-domain checkpoint instead of from COCO weights.

## What Actually Happened

The `pretrained=` parameter performs wholesale weight replacement, not architectural adaptation. Since exp5 weights are yolo11n architecture (different layer shapes than yolo11s), the weight loading causes shape mismatches. The model silently uses yolo11n layer structure despite being instantiated as yolo11s. The resulting model produces scores worse than both baselines (0.8087 vs 0.8328 gen-1 best).

## Evidence

- exploit_1 sol01 (0.8087): yolo11s instantiated, `pretrained=WEIGHTS_EXP5` passed. Score worse than gen-1 best despite explicit AdamW optimizer and TTA.
- The model summary showed yolo11n layers despite loading yolo11s-seg.pt — confirming the architecture mismatch.

## Why This Idea Fails

The pretrained= flag is designed for the case where the checkpoint architecture exactly matches the model architecture. It does not do shape adaptation or intelligent weight transfer across architectures. Combining yolo11s with exp5 requires a different approach (e.g., manual weight loading with shape transposition, or training yolo11s from scratch).

## Lesson

Never use `pretrained=` to load weights from a different architecture family (n vs s vs m vs l). The flag is for loading the same architecture's weights, not bridging architectures.
