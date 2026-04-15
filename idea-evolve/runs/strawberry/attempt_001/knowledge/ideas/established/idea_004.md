---
type: idea
id: idea_004
name: "copy_paste > 0.5 causes instability"
lifecycle: established
confidence: 0.7
first_seen: gen_001
last_updated: gen_001
last_confirmed_gen: gen_001
supported_by: [sol_003]
contradicted_by: []
related_ideas: [idea_007]
cluster: cluster_003
tags: [copy-paste, augmentation, instability, class-imbalance]
---

## What It Is

copy_paste values above 0.5 (specifically 0.65 attempted) cause training crashes or broken pipes. The crash manifests as `[Errno 32] Broken pipe` during training/evaluation.

## How It Works

copy_paste=0.65 means 65% of training images have a randomly selected disease instance duplicated somewhere on the image. At very high values, this may cause:
- Memory pressure when many instances are being copied onto already-crowded images
- Dataset loading pipeline issues when copy_paste encounters edge cases in the mask polygons
- Training instability if the resulting images have unrealistic object density

## Current Evidence

- gen_001 explore_2 (sol01): copy_paste=0.65 → is_valid=0, broken pipe error
- Prior exp5 established copy_paste=0.5 as optimal from HPO grid
- NOTE: The crash occurred at exactly 0.65 with limited time logged. Whether it was specifically caused by copy_paste=0.65 or a random CUDA failure is unconfirmed — no training logs are available to diagnose.

## When It Helps

Knowing the ceiling prevents wasted experiments. Future agents should not exceed 0.6 and should test 0.55-0.6 incrementally rather than jumping to 0.65.

## Contraindications

If you need higher rare-class oversampling, consider copy_paste=0.5 combined with a different technique (class-weighted loss, progressive resizing) rather than pushing copy_paste higher.
