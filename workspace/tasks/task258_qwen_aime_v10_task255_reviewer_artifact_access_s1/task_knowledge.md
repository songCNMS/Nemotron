# task258_qwen_aime_v10_task255_reviewer_artifact_access_s1 - Task Knowledge

<!-- METADATA:SESSION=3 -->

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
5. worker_2 task258 branch `67162453b67f17296e7105e7be06f6e2b953f9bf` records a
   full reviewer-readable copy path under
   `/mnt/cephfs/data/processing/intern_nemotron_worker_2/task258_qwen_aime_v10_task255_reviewer_artifact_access_s1/`,
   but lead is waiting for official mailbox closeout before assigning
   worker_5 re-review.
6. worker_2 official task258 closeout is at PR #331 head
   `d0a05c5e9ad37b831fd75bc9ae852cb121527f83`, disposition
   `PASS_REVIEWER_ACCESS_READY`; #331 remains pending worker_5 task259
   re-review.
7. task259 approved #331; lead approved #331 exact head
   `d0a05c5e9ad37b831fd75bc9ae852cb121527f83` for self-merge, with #329 to be
   closed as superseded rather than merged.
