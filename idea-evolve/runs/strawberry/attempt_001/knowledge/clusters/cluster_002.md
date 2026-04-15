---
type: cluster
id: cluster_002
name: "Evaluation-time techniques"
member_ideas: [idea_003, idea_011]
best_score: 0.8271
best_solution: research_1_EXP-1
status: exhausted
last_updated: gen_002
---

Ideas related to improving evaluation without retraining: Test-Time Augmentation (TTA), NMS threshold tuning, and ensemble prediction averaging.

**CLUSTER STATUS: EXHAUSTED — TTA is non-functional**

gen_2 updates: Both idea_003 and the new idea_011 (TTA non-functional) are now debunked. research_1 EXP-2 confirmed that augment=True is completely non-functional with exp5 weights — it silently reverts to single-scale prediction with zero lift. The "free lunch" evaluation improvement is not available.

The only score in this cluster (0.8271 from research_1 EXP-1) is from zero-shot evaluation without TTA. The TTA direction is closed unless a model is specifically trained to support TTA, which requires separate investigation.

No further evaluation-time improvements are available in the current setup. Agents should focus on training-level changes.
