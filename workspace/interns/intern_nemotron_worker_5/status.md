# intern_nemotron_worker_5 - status

<!-- METADATA:STATUS=Working,TASK=task310_qwen_all_sft_30b_full_training_s1,ROLE=worker,TEAM_ID=nemotron -->

| Field | Value |
|------|-----|
| Name | intern_nemotron_worker_5 |
| Status | Working |
| Role | worker |
| Team | nemotron |
| Current Task | task310_qwen_all_sft_30b_full_training_s1 |
| PR | #373 |
| Session | 7 |
| Last Update | Lead-cleared task310 fail-closed salvage completed. Sent SIGTERM to task310 torchrun PID `1389032` at `2026-06-03T16:36:35Z`; wrapper wrote `train_rc.txt=1` and `train_end.txt=2026-06-03T16:36:36Z`. Fresh post-check showed zero matching training processes and all eight H200s at `1 MiB` / `0%`. Disposition is `TRAINING_LOOP_COMPLETE__VALIDATION_HANG_TERMINATED__CHECKPOINT_SALVAGE_CANDIDATE`, not PASS. Preserved `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035` (`399G`, `28` files); full checksum manifest sha256 `8cb4e7856f379bc7f1d63d407582bd63981b61c9f346455aa40fb389ef73cbe8`. No task311 canary/eval/export/endpoint/promotion, generic raw-stage data, AIME2025 train rows, task255, shared deletion, product-code edit, main push, or merge performed. |
