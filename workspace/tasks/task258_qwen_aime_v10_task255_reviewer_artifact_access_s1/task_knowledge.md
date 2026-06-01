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
5. Acceptance branch for task258 is based on current `origin/main`
   `61fa65e9e9a535d531a65072c839760c3488207f`; task docs were imported from
   lead docs branch `a6a56c61186a71279cfef993589989bf77d0d687`.
6. Final task258 reviewer path is
   `/mnt/cephfs/data/processing/intern_nemotron_worker_2/task258_qwen_aime_v10_task255_reviewer_artifact_access_s1/task255_run_20260601T202339Z_full_artifacts_20260601T2109Z`.
   It contains the full copied task255 checkpoint, full HF export, source logs,
   export helper, and `review_manifest/` inventories.
7. Shared permission probe found no non-world-readable files and no
   non-world-executable directories in the final reviewer path; worker_5 should
   be able to review directly if their environment can read normal CephFS
   `/mnt/cephfs/data/processing` paths.
8. Mailbox reports for artifact-heavy tasks must stay concise; the full
   per-file inventory/checksum detail should be referenced by path
   (`review_manifest/` and local task output root) instead of pasted into the
   mailbox body.
