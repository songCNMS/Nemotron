# task252_qwen_aime_task251_hotpotqa_pr_review_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. task252 reviews PR #328 only; it does not own implementation.
2. The PR #328 gate is local-prep unblock evidence, not FT promotion evidence.
3. The expected successful disposition can still keep the global
   `NO-GO/HOLD` because packed Qwen shards, FT checkpoint/export/live eval, and
   task243 comparison are absent.
4. If the PR head changes from
   `694197c81720dcc157518d8a86b2b5d7a7a2dd05`, worker_4 must report the
   mismatch instead of reviewing stale evidence.
5. worker_4 reviewed the exact assigned head and recommended `APPROVE`; the
   approval is limited to HotpotQA/M0-M1 local prep unblock evidence.
6. worker_4's focused `PYTHONPATH=src` pytest and import-guard probe are enough
   independent evidence for this local PR, but they do not create FT artifacts
   or satisfy task243 base-vs-FT comparison.
7. #328 merged from the reviewed head with merge commit
   `61fa65e9e9a535d531a65072c839760c3488207f`; task252 is complete.
