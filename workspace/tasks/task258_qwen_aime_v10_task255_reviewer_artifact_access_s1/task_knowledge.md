# task258_qwen_aime_v10_task255_reviewer_artifact_access_s1 - Task Knowledge

<!-- METADATA:SESSION=0 -->

## Knowledge Entries

1. task258 exists because task256 could not independently access task255
   checkpoint/export paths under `/root/task255_...`.
2. Full checkpoint is about `53G` and HF export about `7.6G`; if copying the
   full checkpoint is impractical, worker_2 should provide a reviewer-readable
   manifest/checksum package and a clear rationale.
3. This task is not permission to train, export again, evaluate AIME, promote,
   or scale to 30B/8-GPU.
4. Current observed task257 FT AIME25 result is `0/30`, below the accepted base
   `11/30`; task258 only addresses artifact evidence closure.
