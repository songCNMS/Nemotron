# task307_qwen_aime_v11_30b_task306_fail_review_runbook_s1 - Task Knowledge

1. Assigned to worker_4 for independent review of task306 final 30B corrected
   AIME2025 evidence and runbook/provenance closeout. The expected disposition
   is FAIL/no promotion if artifacts and protocol are internally consistent:
   task301 FT scored `14/30`, below accepted Qwen3-30B-A3B base `15/30`.
2. Required review residual: task306 summary reports prompt/cache/parser/
   denominator continuity, but sampling exact-parameter match is false while
   semantic greedy match is claimed. Worker_4 must explicitly decide whether
   this supports FAIL closeout or requires HOLD/request-changes.
3. Session 204 update: task306 PR #369 is now the review target: OPEN/base
   `main`/CLEAN/non-draft at head
   `1255f2356cb014cd1adbe58c7af297f291b222f3`. The eval source head remains
   `894e2e71e72f09926128e37f22000802804522bc`; worker_4 must compare the
   delta and verify it is closeout/report/status docs only.
4. Session 205 update: task306 PR #369 advanced to
   `8201b3943db2d6ed4427c42518736c41f77d67bd`. Worker_3 mailbox closeout ids
   are `ae6fd1db7a894003a952469e4705ab07` and addendum
   `094b16ec7ba14650b53bcd9e69306256`. Worker_4 must review exact head
   `8201b394` and verify `1255f235..8201b394` is metadata/status-only.
5. Session 206 update: task306 PR #369 advanced again to
   `6ad9778ebed758cbcd72ee30ea71d9520a297ac7` after a queued worker_3 follow-up.
   Lead diff `8201b394..6ad9778` is status/session metadata only with unchanged
   FAIL metrics. Worker_4 must review exact head `6ad9778`.
6. Session 207: task307 dispatched to worker_4 with exact #369 head `6ad9778`
   and lead docs `26564646`. Worker_4 is active in pane but no branch/PR/mailbox
   report is visible yet.
