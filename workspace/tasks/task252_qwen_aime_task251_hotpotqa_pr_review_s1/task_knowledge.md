# task252_qwen_aime_task251_hotpotqa_pr_review_s1 - Task Knowledge

<!-- METADATA:SESSION=0 -->

## Knowledge Entries

1. task252 reviews PR #328 only; it does not own implementation.
2. The PR #328 gate is local-prep unblock evidence, not FT promotion evidence.
3. The expected successful disposition can still keep the global
   `NO-GO/HOLD` because packed Qwen shards, FT checkpoint/export/live eval, and
   task243 comparison are absent.
4. If the PR head changes from
   `694197c81720dcc157518d8a86b2b5d7a7a2dd05`, worker_4 must report the
   mismatch instead of reviewing stale evidence.
