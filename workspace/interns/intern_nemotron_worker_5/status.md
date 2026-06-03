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
| Session | 6 |
| Last Update | Task310 refreshed from current main `004870e7d790778b5cdae5cc574257fdc19ec755` after #374/#372/#375 merged and launched the bounded 30B all-SFT attempt using only constrained task299 packed root. Training reached `35/35`, saved `iter_0000035` at `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035` (`399G`, `28` files), and logged skipped/NaN iterations `0`. Current disposition is `TRAINING_LOOP_COMPLETE__VALIDATION_NO_LOG_PROGRESS_PENDING_LEAD_DECISION__CHECKPOINT_CANDIDATE`: no `train_rc.txt`/`train_end.txt`, log stuck at `Evaluating on 80 samples` / `Evaluating iter 1/10` since `2026-06-03T16:10:22Z`, processes alive. No termination/restart, eval/canary, export, endpoint, promotion, generic raw-stage data, AIME2025 train rows, task255, shared deletion, product-code edit, main push, or merge performed. |
