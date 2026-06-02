# task288_qwen_aime_v11_task287_canary_gate_review_s1 - task knowledge

1. task288 reviews task287 only after worker_3 provides official evidence for
   an exact task287 head/PR/artifact report.
2. Approval must be for non-AIME canary evidence only. It must not authorize
   corrected AIME2025/task243 comparison, export, endpoint, promotion, 30B, or
   8-GPU.
3. If task287 cannot load/generate from task285 iter2 checkpoint without export
   or endpoint, the correct task288 disposition is `BLOCK`, not a workaround.
