---
type: idea
id: idea_002
name: "Higher resolution imaging (imgsz=832)"
lifecycle: disputed
confidence: 0.4
first_seen: gen_001
last_updated: gen_002
last_confirmed_gen: gen_001
supported_by: []
contradicted_by: [sol_003]
related_ideas: [idea_010]
cluster: cluster_001
tags: [resolution, small-lesions, fine-tuning]
---

## What It Is

Train or evaluate at imgsz=832 (or 1024) instead of the default imgsz=640. The hypothesis is that small disease lesions (Angular Leafspot, early Anthracnose) are lost or poorly resolved at 640px.

## How It Works

Higher resolution gives ~1.7x more pixels per disease spot, improving mask boundary quality for small objects. YOLO11n-seg at 832px still fits in 16GB VRAM at batch=8.

## Updated Evidence — gen_002

**Negative result (explore_1 sol01):** Fine-tuning exp5 at imgsz=832 for 20 epochs produced severe regression (0.5453 vs exp5 zero-shot 0.7876 at same resolution). The val-test gap was 0.36 — dramatically worse than the 0.10 gap at 640. This approach is counterproductive.

**IMPORTANT CLARIFICATION:** The idea itself (imgsz=832 helps small lesions) is NOT debunked. The specific approach (fine-tuning a 640-converged checkpoint at 832 for 20 epochs) IS debunked. The regression occurred because 20 epochs was insufficient to relearn resolution-adapted features — the domain adaptation from exp5 was destroyed before new resolution features were established.

**Positive signal:** exp5 zero-shot at 832 still achieves 0.7876, which is respectable and suggests the model has some resolution-adaptive capacity.

## When It Might Help

- Training from scratch at 832 for 50+ epochs (no prior resolution features to disrupt)
- Progressive resizing: train at 640, then unfreeze and fine-tune at 832 (staged approach, preserves domain knowledge)
- Evaluation only (not fine-tuning) at 832 on a 640-trained model

## Risks

- 1.7x more pixels means slower training per epoch
- Batch size must be reduced (batch=8 at 832 vs batch=16 at 640)
- Fine-tuning at 832 from a 640-converged checkpoint for only 20 epochs actively hurts performance

## Status Change

Confidence reduced from 0.6 to 0.4. The specific implementation tested (fine-tuning from converged checkpoint) was debunked. The idea remains plausible but requires a different approach (from-scratch or progressive resizing).
