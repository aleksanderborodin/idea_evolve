# Evaluator Report — gen002

## Produced

| Output | Count |
|--------|-------|
| new_ideas/ | 4 (idea_009, 010, 011, 012) |
| updated_ideas/ | 4 (idea_002, 003, 006, 007) |
| new_patterns/ | 3 (pattern_004, 005, 006) |
| updated_clusters/ | 3 (cluster_001, 002, 003) |
| solution_idea_map.md | updated |
| coverage_matrix.md | updated |
| generation_snapshot.md | written |
| evaluator_report.md | written |
| agent_gaps.md | written |

## Incomplete

- **explore_1/sol02** — yolo11s from COCO, 40 epochs. Timed out before evaluation. Score unknown.
- **full_1/sol01** — yolo11s from COCO, 50 epochs. Evaluation interrupted. Score unknown.

These two represent the most important unanswered question: does yolo11s benefit from more than 20 epochs?

## Key Findings

1. TTA is non-functional — silent fallback, zero lift
2. imgsz=832 fine-tuning regresses to 0.5453 from exp5
3. Zero-shot exp5 (0.8271) nearly matches all fine-tuned results
4. yolo11s + exp5 via pretrained= fails (architecture mismatch)
5. Gen-2 best valid: 0.8103. Best overall: 0.8271 (zero-shot). Gen-1 best remains 0.8328.
