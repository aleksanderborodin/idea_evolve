---
type: idea
id: idea_004
name: "cls_pw parameter invalid above 1.0"
lifecycle: established
confidence: 1.0
first_seen: gen_001
last_updated: gen_001
last_confirmed_gen: gen_001
supported_by: ["gen001_explore_1_sol01"]
contradicted_by: []
related_ideas: []
cluster: null
tags: ["class-weighting", "failure-mode", "YOLO-constraint"]
---

## What

YOLO's `cls_pw` parameter (class probability weight) accepts values only in [0, 1]. Values above 1.0 are rejected with AssertionError.

## Evidence

gen001_explore_1_sol01: cls_pw=2.0 → is_valid=0, error "cls_pw must be in the range [0, 1]"

## Implication

Class-aware sampling via cls_pw is NOT a viable approach for addressing the 15x class imbalance. The parameter is a probability weight, not a multiplier.

## Alternative approaches needed

1. Custom class weights via dataset YAML modification
2. Custom loss function (BCE-Dice-Lovász composite with inverse-frequency weighting)
3. Two-stage training: oversample rare classes in dataset YAML
4. Progressive class weighting via custom loss injection (YOLO monkey-patching)