# task276_qwen_aime_v11_rematerialize_packed_qwen_s1 - Task Knowledge

<!-- METADATA:SESSION=2 -->

## Knowledge Entries

1. task253 packed Qwen root is stale for V11 pilot readiness because train split
   exposure was 8 shards / 79 rows while task262 expected 15 shards / 113 rows.
2. task276 must use the task262 V11 blend plan and merged task262 split logic to
   produce a fresh collision-safe `packed_qwen` root.
3. A successful task276 artifact can only unblock later no-training
   config/import preflight review after independent review; it does not
   authorize training, live canary, AIME/task243 eval, export, endpoint,
   promotion, or 30B/8-GPU.
4. Local dependency probe at acceptance found `cosmos_xenna`, `datasets`,
   `pyarrow`, `transformers`, and `torch` importable, so the initial path is to
   try local no-training data prep/packing before reporting an environment
   blocker.
5. task276 produced a fresh packed root under
   `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen`;
   Qwen contract and split multiset parity passed. The artifact is ready for
   independent review only, not training/eval/export/promotion.
6. The fresh split is sparse in validation: valid has 1 packed hard-math row.
   This should be reviewed before any later config/import preflight treats the
   valid split as representative.
7. Session 2 is a mailbox/status reconciliation only. The authoritative packed
   artifact remains
   `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen`;
   no new packing, training, evaluation, export, or promotion action was run.
