---
type: idea
id: idea_010
name: "imgsz=832 fine-tuning causes severe regression from converged checkpoint"
lifecycle: debunked
confidence: 0.85
first_seen: gen_002
last_updated: gen_002
last_confirmed_gen: gen_002
supported_by: [sol_003]
contradicted_by: []
related_ideas: [idea_002]
cluster: cluster_001
tags: [resolution, fine-tuning, regression, imgsz-832]
---

## What It Is

Fine-tuning the exp5 converged checkpoint (trained at imgsz=640) at imgsz=832 for 20 epochs as a way to improve small-lesion detection.

## How It Was Supposed to Work

Higher resolution (832) provides ~1.7x more pixels per disease spot, potentially capturing finer disease features. Fine-tuning the domain-adapted exp5 checkpoint at the new resolution would preserve domain knowledge while improving resolution-specific detail.

## What Actually Happened

explore_1 sol01: Fine-tuned exp5 at imgsz=832 for 20 epochs. Result: mAP50 = 0.5453 — a severe regression. For reference:
- exp5 zero-shot at 832: 0.7876 (same resolution, no fine-tuning)
- exp5 zero-shot at 640: 0.8271
- Gen-1 best (yolo11s from COCO at 640): 0.8328

The fine-tuned model (0.5453) was dramatically WORSE than the original exp5 evaluated at the same resolution (0.7876), confirming that 20 epochs of fine-tuning at a different resolution actively destroyed the domain adaptation.

## Why This Happens

When fine-tuning at a different resolution from the converged checkpoint:
1. The model's learned features are resolution-specific (features learned at 640 don't transfer well to 832 spatial dimensions)
2. 20 epochs is insufficient to relearn resolution-adapted features from scratch
3. The domain adaptation from exp5 is disrupted before the new resolution features can be established
4. Result: both the original domain knowledge AND resolution adaptation are lost

## When It Might Work

- Training from scratch at 832 for 50+ epochs (no prior resolution-specific features to disrupt)
- Progressive resizing: train at 640, then unfreeze and train at 832 (staged approach)
- Very long fine-tuning (100+ epochs) might eventually recover, but 20 epochs definitely does not

## Implications

imgsz=832 as a fine-tuning approach from a converged 640 checkpoint is counterproductive. The idea_002 hypothesis ("imgsz=832 improves small-lesion detection") is NOT debunked — but the specific approach of fine-tuning at 832 from a 640-converged checkpoint is debunked. Future attempts should use from-scratch 832 training or progressive resizing.
