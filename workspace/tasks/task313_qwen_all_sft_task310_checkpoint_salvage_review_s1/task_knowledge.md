# task313_qwen_all_sft_task310_checkpoint_salvage_review_s1 - Task Knowledge

<!-- METADATA:SESSION=78 -->

## Knowledge Entries

1. Task310 final disposition is
   `TRAINING_LOOP_COMPLETE__VALIDATION_HANG_TERMINATED__CHECKPOINT_SALVAGE_CANDIDATE`,
   not `PASS_TRAINING`.
2. PR #373 current exact head for this review is
   `0cbcb3c56df5f097a0fd63ebfa1a3c7cdb36f9b8`; any material head drift must be
   reported before lead approval.
3. The task310 checkpoint candidate is
   `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035`,
   reported as `399G` and `28` files.
4. `train_rc.txt=1` and missing accepted validation metrics are residual risks;
   task311 must remain HOLD until lead accepts independent review evidence and
   explicitly releases checkpoint-load plus non-AIME canary.
5. AIME2025 prompts/labels remain held-out eval/decontam only, and task255
   remains forbidden as training or success evidence.
6. Lead observed the `7561a578..0cbcb3c5` drift as worker_5 status plus task310
   history/task_knowledge bookkeeping only; worker_4 must independently verify
   the report file and artifact/checksum evidence did not change.

---
