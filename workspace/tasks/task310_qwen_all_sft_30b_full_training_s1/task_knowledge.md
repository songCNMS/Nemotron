# task310_qwen_all_sft_30b_full_training_s1 - Task Knowledge

<!-- METADATA:SESSION=78 -->

## Knowledge Entries

1. The previous 30B FT checkpoint cannot be promoted or reused as success
   evidence because task306 scored `14/30`, below the accepted task300 base
   `15/30`.
2. The selected target is
   `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507` unless a
   task308/task309/runtime gate reports an exact blocker.
3. Full training must fail closed rather than downgrading to 4B or switching
   data/model paths silently.
4. Session 78 final task310 worker disposition is
   `TRAINING_LOOP_COMPLETE__VALIDATION_HANG_TERMINATED__CHECKPOINT_SALVAGE_CANDIDATE`,
   not `PASS_TRAINING`; wrapper rc is `1` after lead-cleared SIGTERM during a
   validation hang.
5. PR #373 exact head for the salvage closeout is
   `7561a578f5f624cf1d3b85bef0dd8abb5c787533`; it remains HOLD pending
   task313 independent review.
6. The checkpoint candidate is
   `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035`,
   reported as `399G`/`28` files with payload manifest sha256
   `8cb4e7856f379bc7f1d63d407582bd63981b61c9f346455aa40fb389ef73cbe8`.
7. Task311 checkpoint-load/canary and all benchmark/AIME eval remain HOLD until
   lead accepts task313 review and sends an explicit release.
