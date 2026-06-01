# task257_qwen_aime_v10_task255_same_harness_eval_s1 - Task Knowledge

<!-- METADATA:SESSION=4 -->

## Knowledge Entries

1. The accepted Qwen3-4B base score is `11/30` under the corrected AIME2025
   same-harness protocol.
2. A task255 FT score below `11/30` is FAIL, not a promotion candidate.
3. A task255 FT score at or above `11/30` is only a Qwen3-4B pilot gate pass;
   it does not authorize 30B/8-GPU or promotion by itself.
4. Lead read-only monitoring observed task257 FT AIME25 `0/30 = 0.0` with
   parsed `0/30`, below base `11/30`; this remains pending official worker_3
   report.
5. task256 currently blocks artifact approval, so no task257 PASS is possible
   until artifact accessibility is resolved.
6. PR #330 at head `4f8f8fcfffe46245070541956a2f44731406f2e6` records the same
   below-base FT result; lead still needs worker_3 mailbox reconciliation before
   approving or merging the docs closeout.
7. worker_3 official mailbox report reconciled #330; lead approved #330 only as
   a docs/report failure closeout at exact head `4f8f8fcfffe46245070541956a2f44731406f2e6`.
   The approval does not change #329 HOLD or global `NO-GO/HOLD`.
8. Approval was refreshed to `da83f014f5e4b22c4410afdf8bda3ccb49a70af3` after a
   docs/status metadata-only compliance fix; the task257 eval report did not
   change.
