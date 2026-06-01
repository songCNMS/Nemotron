# task257_qwen_aime_v10_task255_same_harness_eval_s1 - Task Knowledge

<!-- METADATA:SESSION=2 -->

## Knowledge Entries

1. The accepted Qwen3-4B base score is `11/30` under the corrected AIME2025
   same-harness protocol.
2. A task255 FT score below `11/30` is FAIL, not a promotion candidate.
3. A task255 FT score at or above `11/30` is only a Qwen3-4B pilot gate pass;
   it does not authorize 30B/8-GPU or promotion by itself.
4. Session 2 FT eval of the task255 exact HF export path produced 30/30 ok,
   parsed `0/30`, correct `0/30`, exact-normalized accuracy `0.0`; it is below
   the accepted base `11/30`.
5. Task256 worker_5 branch `9b77d7ee57293697860095791ad7e6661241abca`
   records REQUEST_CHANGES/HOLD because the exact `/root/task255...` artifact
   directories were not independently readable by worker_5. Therefore task257
   should not claim promotion or final PASS; report the measured below-base
   result together with overall gate HOLD/no promotion.
6. Worker `status.md` metadata accepts only `Idle` or `Working`; after
   closeout, use `Idle` and clear `Current Task` rather than recording
   `ReadyForPR`. This compliance correction does not change the task257
   artifacts, score, PR, or gate disposition.
