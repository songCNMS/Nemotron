# task248_qwen_aime_v10_4b_pilot_prepare_train_s1 - Task Knowledge

<!-- METADATA:SESSION=9 -->

## Knowledge Entries

1. PR #321 merged planner support but did not run local prep, sync, train,
   live eval, or FT comparison.
2. The task242 placeholder corpus marker must not be used for data prep.
3. FT judgment is blocked until task247 publishes a same-harness Qwen3-4B base
   artifact and task243 comparison can be run with identical protocol.
4. Local output root required by task248 is
   `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/`;
   NemTron remote root is `/root/task248_qwen_aime_v10_4b_pilot_prepare_train_s1`.
5. Session 2 dependency probes found no visible task246 real corpus/input files
   and no visible task247 base artifact files; task248 must remain blocked
   before local prep/train until those dependencies publish artifact paths.
6. Session 3 refresh found task246 and task247 branches visible at
   `a53c913ab80e37197ccfe7525ea04e0ac80c96fe` and
   `94c21c9a8cb229f0357a049a698de898963810f1`, but the required reports and
   output artifacts are still missing.
7. Session 4 lead sequencing keeps task248 on HOLD until task246/#325 checksum
   correction is accepted and task247/#326 baseline is merged/available.
8. Planned task246 inputs are corpus
   `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl`
   and M0 sidecar
   `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar`.
9. The task246 sidecar is sparse: `8` train rows and `0` val rows; planned
   pilot knobs are math-sidecar train cap `8` and val shadow cap `0`.
10. Task247 baseline for later comparison is Qwen3-4B base AIME25
    `11/30 = 0.36666666666666664` under the corrected 30x1 same harness.
11. Task247/#326 baseline merged into `main` with merge commit
    `85f2bf5c11062741388ca114a84a2c26535b7df9`; the baseline score remains
    `11/30 = 0.36666666666666664`.
12. Session 5 historical state: task248 remained on HOLD because task246/#325
    was still open with lead-reported `REQUEST_CHANGES`/HOLD on manifest
    checksum before the later task246 fix.
13. Session 6 lead update says task246/#325 checksum fix is approved at head
    `266b6a14262278b4fe27f75a3273fc156a5538ce`, but task248 still cannot run
    prep/sync/train/eval until #325 is actually merged plus task249/task250
    refreshed reviews land or lead gives explicit clearance.
14. Session 6 read-only checks found task249/#323 and task250/#324 still
    `OPEN`/`CLEAN`, so their refreshed review state remains a task248 hold
    condition.
15. Session 7 lead clarification: current task246/#325 head
    `266b6a14262278b4fe27f75a3273fc156a5538ce` is approved pending actual
    merge, not request-changes; task248 HOLD still blocks prep/sync/train/eval
    until #325 merges and task249/task250 refreshed reviews or explicit lead
    clearance arrive.
16. Session 8 update: task246/#325 is now merged into `main` at
    `2026-06-01T17:43:24Z` with merge commit
    `2775dff05948acce3a35a2d941bbd2f96d074b4a`.
17. After #325 merge, task248 remains HOLD until task249/task250 refresh against
    current `main` and lead explicitly clears; do not start local prep,
    NemTron sync, training, or eval before that clearance.
18. Session 9 clearance: task246/#325, task247/#326, task250/#324, and
    task249/#323 are merged on `main` at
    `ec467724c2876211cd2bf56b15071e31abd692a4`, so task248 may resume only
    Qwen3-4B V10 prep/smoke under the existing scope.
19. Session 9 generated task-owned planner artifacts under
    `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/`,
    but local prep is incomplete: no M0 manifest, M1 blend, packed shards,
    training manifest, checkpoint/export, FT eval, or task243 comparison exists.
20. Session 9 local prep blockers observed in order: missing
    `/work-agents/.venv/bin/activate`, missing `datasets`, then after minimal
    user-site dependency install, Hugging Face `datasets` `trust_remote_code`
    incompatibility for `hotpotqa/hotpot_qa`; output is not ready for task243
    comparison.
