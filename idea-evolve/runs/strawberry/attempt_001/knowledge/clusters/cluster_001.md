---
type: cluster
id: cluster_001
name: "Model scale and resolution exploration"
member_ideas: [idea_001, idea_002, idea_006, idea_010]
best_score: 0.8328
best_solution: sol_002
status: active
last_updated: gen_002
---

Ideas related to using larger model variants (yolo11s, yolo11m) and higher input resolution (832, 1024) to capture finer disease details. The cluster's best result (0.8328) came from yolo11s at 640px trained from COCO.

gen_2 updates: idea_002 (imgsz=832) is now disputed — direct fine-tuning at 832 from a 640-converged checkpoint was debunked (severe regression to 0.5453). However, progressive resizing (idea_006) remains active as an alternative approach. idea_010 (imgsz=832 fine-tuning regression) is a new debunked idea documenting the specific failure mode.

Key finding: The most promising direction is NOT combining larger models with exp5 fine-tuning, but rather yolo11s from COCO with longer training. The exp5 starting point provides no advantage in the 20-epoch proxy regime.
