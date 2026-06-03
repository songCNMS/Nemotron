# task310_qwen_all_sft_30b_full_training_s1 - Task Knowledge

<!-- METADATA:SESSION=77 -->

## Knowledge Entries

1. The previous 30B FT checkpoint cannot be promoted or reused as success
   evidence because task306 scored `14/30`, below the accepted task300 base
   `15/30`.
2. The selected target is
   `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507` unless a
   task308/task309/runtime gate reports an exact blocker.
3. Full training must fail closed rather than downgrading to 4B or switching
   data/model paths silently.
