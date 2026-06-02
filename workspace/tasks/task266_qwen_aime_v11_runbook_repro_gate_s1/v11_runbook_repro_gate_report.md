# task266 V11 runbook/repro gate report

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_5,SESSION=2 -->

## Summary

- Recommendation for task266: PASS as a static V11 runbook/repro gate.
- Recommendation for V11 execution: HOLD / NO-GO until the remaining
  nonzero-LR training evidence, live canary/candidate artifacts, task265 review,
  same-harness comparison, and lead clearance clear the stage gates.
- Branch:
  `intern_nemotron_worker_5/task266_qwen_aime_v11_runbook_repro_gate_s1`.
- Branch creation base: `origin/main` at
  `513fefa1f1ace94302b56413769c78fb7224624c`.
- Current task282 refresh base `origin/main` after #347 merge:
  `28039222ad5d4054891713d85d05a15a491d8a96`.
- Lead docs source:
  `origin/intern_nemotron_lead/session1-recovery-task-docs` at
  `81253415dd3285ce0eb56e69733d210742edcb50`.
- Scope executed: read-only runbook and reproducibility gate across visible
  task262/task263/task264/task265 evidence, plus task260/task261 root-cause
  reports and task243/task247 same-harness base evidence.
- Request-changes refresh: updated against task262 PR #336 MERGED at head
  `8fd3ff6065290b850c98db5f7abff91aa6880967`, merge commit
  `2ca6541c275d1eb64068e665af24147a796c818a`, task263 branch
  `4af57e0e61703a063c1ef42def44119a7eea5cf9`, and task264 PR #335 MERGED
  at `9d9285fd77820a5187440fbc2234dc36eb56942d` with merge commit
  `98e8aad39af9e705feed581e0ff9f8814073e2d8`.
- Session 40 refresh from task275: coordinator evidence at
  `/work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z`
  proves the no-training Qwen3-4B Bridge import/preflight route now passes with
  `nemo-toolkit==2.7.3`, `IMPORT_DONE`, `BRIDGE_IMPORT_RC=0`, and
  `TASK270_FAIL_CLOSED_PREFLIGHT=PASS`. This clears only the prior runtime
  route blocker; it does not authorize training/eval/promotion.
- Session 74 refresh from task282: PR #344/task276 is merged into main at
  `793e7dfa73ed1c5bdc8b7b98df5f31ffdd5e38ea` from merged head
  `07efab4fa0d8367e96f54af3d2cdc70768d73595`, with accepted packed Qwen root
  `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen`.
  This supplies packed-data evidence for the task278 no-training
  config/import preflight gate only; it does not authorize nonzero-LR training,
  canary, AIME/task243 eval, promotion, or scale.
- Session 74 current gate refresh from task282 Session 4: #345/task281 is merged
  plan-only HOLD at `0d008ddbc8a87445e69f95e02ef9a07ae17791d6`; #346/task280
  is merged plan-only HOLD at
  `7ba65549500e9ca70fc560ed919d6bfa61f088b2`; #347/task278 is merged blocker
  docs only at `28039222ad5d4054891713d85d05a15a491d8a96` from exact head
  `b7e544100ac13eaa908a9d1af6fafaf599bc3310`, with blocker report sha
  `c81208f6af524d117a333495ab4b5a971aeecf36d38000a737318ff346f77f23`.
  task279 approved #347 as blocker/preflight evidence only, lead approval
  comment `4598906687`. task283 is accepted at
  `c1d988e29abafa51a9c3f83a98e21b229135f97e`; task284 is accepted/cleaned at
  `27d28b54342a98a4a336c46661964759f2790619`; they are the next no-training
  remediation/review gates.
- Boundary kept: no training, eval, export, endpoint launch, merge,
  promotion, 30B/8-GPU authorization, AIME2025 train-data use, shared deletion,
  or worker branch alteration.

The first measurable V11 go/no-go remains:

`new_qwen3_4b_ft_exact_normalized_accuracy >= 11/30`

under the same corrected AIME2025 30x1 harness, after base-load/import proof,
nonzero-LR training evidence, non-AIME canary pass, reviewer-readable artifacts,
and independent contamination/regression review exist.

## Evidence Inventory Checked

| Surface | Visible evidence | Current status |
|---|---|---|
| task262 data/packing repair | PR #336 MERGED at head `8fd3ff6065290b850c98db5f7abff91aa6880967`, merge commit `2ca6541c275d1eb64068e665af24147a796c818a`; substantive repair commit `0f825b9357a2a8f7814f693ea4c27027c5fbdd31`; final-answer n-gram decontam evidence commit `5e431f4939799ae52c7d2002682352f2f2df6f3b`; latest head commit is metadata-only reconciliation; report `v11_data_split_sidecar_report.md`; output bundle under `/work-agents/intern_nemotron_worker_1/outputs/task262_qwen_aime_v11_data_split_sidecar_s1/` | STATIC MERGED into main as data/packing repair evidence |
| task276 fresh packed Qwen root | PR #344 MERGED at head `07efab4fa0d8367e96f54af3d2cdc70768d73595`, merge commit `793e7dfa73ed1c5bdc8b7b98df5f31ffdd5e38ea`; report `v11_rematerialized_packed_qwen_report.md`; packed root `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen`; evidence manifest and all 48 shard checksum entries verified by task282 | PACKED DATA EVIDENCE PRESENT for task278 no-training preflight; nonzero-LR training remains HOLD |
| task278 config/import preflight | PR #347 MERGED at `2026-06-02T05:13:14Z` as `28039222ad5d4054891713d85d05a15a491d8a96` from head `b7e544100ac13eaa908a9d1af6fafaf599bc3310`; artifact root `/work-agents/intern_nemotron_worker_2/outputs/task278_qwen_aime_v11_task276_config_import_preflight_s1/run_20260602T045642Z`; report sha `c81208f6af524d117a333495ab4b5a971aeecf36d38000a737318ff346f77f23`; manifest sha `57b0a9d5ce51dd3f48514b802e8cfaff973a8ad297df466ef551d86f84840692`; disposition `CONFIG_IMPORT_PREFLIGHT_BLOCKED_MISSING_MEGATRON_BRIDGE` | MERGED BLOCKER DOCS ONLY; runtime preflight remains blocked |
| task279 preflight review | worker_4 approved #347 exact head `b7e544100ac13eaa908a9d1af6fafaf599bc3310` as blocker/preflight evidence only; lead approval comment `4598906687` | BLOCKER EVIDENCE APPROVED; no runtime pass |
| task263/runtime base-load planner sanity | task263 branch `4af57e0e61703a063c1ef42def44119a7eea5cf9` remains the older local-env blocker record. Coordinator Session 40 at branch `intern_nemotron_coordinator/session1-resume-interrupted-work` head `8c8364101d6adb07f9e67c17fece3e2b2bb280ca` provides newer no-training runtime proof: `nemo=/root/.local/lib/python3.12/site-packages/nemo/__init__.py`, `IMPORT_DONE`, `BRIDGE_IMPORT_RC=0`, `TASK270_FAIL_CLOSED_PREFLIGHT=PASS`, remote imported checkpoint root `/root/task_coordinator_nemotron_coordinator_06b9acba/session40_nemo_install_probe_20260602T015146Z/qwen3_4b_bridge_import_iter0`, local evidence root `/work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z` | RUNTIME PROOF PRESENT for no-training Bridge import/preflight only; live nonzero-LR training evidence and future candidate artifacts remain HOLD |
| task264 canary/retention gate | PR #335 MERGED at `9d9285fd77820a5187440fbc2234dc36eb56942d`; merged at `2026-06-01T23:00:37Z` as `98e8aad39af9e705feed581e0ff9f8814073e2d8`; official closeout report `v11_canary_retention_report.md`; static canary/retention code/config/tests added | STATIC MERGED into main, but HOLD for live use until a future V11 candidate supplies actual canary pass artifacts and task265 review clears exact inputs |
| task280 bounded smoke plan | PR #346 MERGED at `2026-06-02T04:59:45Z` as `7ba65549500e9ca70fc560ed919d6bfa61f088b2`; report `qwen3_4b_v11_sft_smoke_plan_hold_report.md`; disposition `PLAN_READY_HOLD_TASK278_TASK279_RELEASE` | PLAN-ONLY HOLD; no smoke execution authorized |
| task281 canary/AIME plan | PR #345 MERGED at `2026-06-02T04:54:59Z` as `0d008ddbc8a87445e69f95e02ef9a07ae17791d6`; report `canary_aime_eval_plan_hold_report.md`; disposition `PLAN_READY_HOLD` | PLAN-ONLY HOLD; no live canary/AIME authorized |
| task283 runtime remediation | accepted on remote branch `origin/intern_nemotron_worker_2/task283_qwen_aime_v11_bridge_runtime_remediation_preflight_s1` at `c1d988e29abafa51a9c3f83a98e21b229135f97e` for no-training runtime-route remediation/config-import preflight using task276 packed data and Qwen3-4B path | NEXT REMEDIATION GATE |
| task284 task283 review | accepted/cleaned on remote branch `origin/intern_nemotron_worker_4/task284_qwen_aime_v11_task283_runtime_gate_review_s1` at `27d28b54342a98a4a336c46661964759f2790619` for independent read-only review of exact task283 evidence | NEXT REVIEW GATE |
| task265 independent review | Remote branch `origin/intern_nemotron_worker_4/task265_qwen_aime_v11_contam_regression_review_s1` is visible at `ca5ea1c405ef142ee51a43fcbab477a2958e48dc`; no PR or repo-visible task265 report exists; worker_4 status records a mailbox-only task265 read-only matrix refresh for #335/#336 with id `7e718a2c0ea746ed81352db5b5b6fe57` | MAILBOX-ONLY EVIDENCE: current repo cannot inspect the full task265 matrix file; final live execution still HOLD |
| task260 failure forensics | Merged PR #332; report says task255 FT failure is generation degeneration/corruption, not evaluator-only parser failure | Used as V11 canary/retention requirement source |
| task261 root cause | Merged PR #333; report identifies likely missing Qwen base load, zero LR at only step, and split basename collisions | Used as V11 data/base-load/schedule gate source |
| task247 accepted base | Merged base artifact: Qwen3-4B exact-normalized AIME2025 `11/30 = 0.36666666666666664` | Fixed comparator for first V11 go/no-go |

Session 40 runtime proof artifacts now recorded:

- local evidence root:
  `/work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z`;
- remote run root:
  `/root/task_coordinator_nemotron_coordinator_06b9acba/session40_nemo_install_probe_20260602T015146Z`;
- symbol preflight log sha256:
  `bfa15c5b26849ef2c802c03b0303d57ada11922c4872068bd17de2c7d0081534`;
- Bridge import log sha256:
  `170b51d0c846c374a82badf780d478d64a946d3131cdc7032808d7c53db21756`;
- fail-closed preflight log sha256:
  `60db59059560304dc18a6e28498f6be1a08cbc24c26abd6e82241f6e1729c440`;
- remote checkpoint manifest sha256:
  `51b4ab937a5be23f1391cddd5c5c1425a3f8860e84fe81827fc5ebdee2afb522`;
- checkpoint root:
  `/root/task_coordinator_nemotron_coordinator_06b9acba/session40_nemo_install_probe_20260602T015146Z/qwen3_4b_bridge_import_iter0`
  with recorded size `7.5G`.

Task262 #336 details now recorded:

- PR state: #336 MERGED at head
  `8fd3ff6065290b850c98db5f7abff91aa6880967`, merge commit
  `2ca6541c275d1eb64068e665af24147a796c818a`; latest head commit is
  metadata-only reconciliation. The requested final-answer n-gram
  decontamination scan was added at
  `5e431f4939799ae52c7d2002682352f2f2df6f3b`, with substantive split repair at
  `0f825b9357a2a8f7814f693ea4c27027c5fbdd31`;
- worker_1 history records official closeout mailbox id
  `adcbeda5b09d457b949aa51c89747d91` for exact head
  `1a440c155a3049ece488483c1ce99ff4c89a3eb8`; subsequent `69f32c6` was
  status/history/task_knowledge bookkeeping;
- code repair files:
  `src/nemotron/data_prep/utils/splits.py` and
  `src/nemotron/recipes/super3/stage1_sft/qwen_chat_contract.py`;
- focused tests:
  `tests/data_prep/test_split_utils.py` and
  `tests/recipes/super3/test_qwen_chat_contract.py`;
- task-owned output root:
  `/work-agents/intern_nemotron_worker_1/outputs/task262_qwen_aime_v11_data_split_sidecar_s1/`;
- `split_materialization_audit.json` sha256
  `b2009b2c509620c5dde2412ee4dedf4efb8995431ef4bec4d353ba14dc3787b3`;
- `v11_qwen_agentic_sft_blend_plan.json` sha256
  `2b3f0942eb04e077c5025c60be87355bf233b33085660a0b85a0b8b03b569e2a`;
- `task251_source_summaries.json` sha256
  `d0d6b253c2ee9620d2b9c023cdc680b5f6c762e0c163174572fd40e9c1d35e6a`;
- `final_answer_ngram_decontam_scan.json` sha256
  `feffa6c677b1bc86b5f2f9ad8a8c3506582844cdb5b6a25bd8741322a9298370`;
- `final_answer_ngram_decontam_report.md` sha256
  `9f73fb0cbccb048ab8137efc00bc4a9ba76cc87a708796af82b6768e626531fe`;
- `task262_v11_data_split_sidecar_report.md` sha256
  `df5a203628bcb563148d1123a121d0d4f0d3207ab4e52be62f1c6ea00dbc1789`;
- `manifest.json` sha256
  `4c9874c9341b1e286533bd67eafa6a922567e905c9d3bb7bd78e8970eb777383`;
- task253 audit result: train intended 15 shards / 113 rows / 835223 input
  tokens / 156569 supervised tokens, but exposed 8 shards / 79 rows / 596944
  input tokens / 110945 supervised tokens; valid matched 1 shard / 15 rows /
  115993 input tokens / 18998 supervised tokens;
- missing task253 train targets: 7 total, split as 2 M0/general shards and 5
  hard-math sidecar shards;
- V11 sidecar plan: base M0 1100 rows sha256
  `994166eeb83ffb5ebd213db9cc0d6cdd90208251bd2aab9dbb70cec7bf96691a`,
  hard-math 8 rows sha256
  `2039b67b2bcf5cf74b576a640f1f3a198d675e3fbd64a886da4be5753ad515d9`,
  final-answer 200 rows sha256
  `0e5485eae86bf716d0c2e04e8e02595564b38a949d71d31a42874d6e87ef1731`,
  all weight `1.0`;
- decontamination evidence: heldout corpus rows 560, heldout prompt hashes 560,
  exact task246-style prompt-hash overlaps all 0 for base/hard-math/final-answer
  sources, and task251 heldout eval rows 0;
- fresh final-answer full n-gram scan: 200 final-answer rows versus 560 heldout
  prompts, 112000 pair comparisons, 4 overlap pairs, 1 informational pair, 0
  blocker pairs, 0 rows with blocker overlap, max score 0.257143; standard
  `decontaminate_math_rows` scanned 100 `math_competition_numeric` rows, found
  0 blocker findings, and dropped 0 rows;
- reported checks: `python -m py_compile
  src/nemotron/data_prep/utils/splits.py
  src/nemotron/recipes/super3/stage1_sft/qwen_chat_contract.py`,
  `PYTHONPATH=src pytest -q tests/data_prep/test_split_utils.py
  tests/recipes/super3/test_qwen_chat_contract.py`,
  `PYTHONPATH=src python
  workspace/tasks/task262_qwen_aime_v11_data_split_sidecar_s1/build_task262_final_answer_decontam.py`,
  and `git diff --check`;
- no training, export, endpoint launch, AIME/task243 eval, promotion,
  30B/8-GPU, task255 checkpoint/export reuse, AIME2025 train data use, or
  shared deletion is reported.

Task276 #344 details now recorded:

- PR state: #344 MERGED at head
  `07efab4fa0d8367e96f54af3d2cdc70768d73595`, merged at
  `2026-06-02T04:19:38Z` as merge commit
  `793e7dfa73ed1c5bdc8b7b98df5f31ffdd5e38ea`;
- task276 report:
  `workspace/tasks/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/v11_rematerialized_packed_qwen_report.md`;
- task276 run root:
  `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z`;
- accepted packed Qwen root:
  `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen`;
- split manifest sha256:
  `65501e0eff31cce77ff2d1e36dd915f66fb6b2fd145e0f59701d251e5b7d02c5`;
- split metadata sha256:
  `e4ac2157760dd50e50798a9095bf3ea1fb6834e5f405cac2f877560f42dbafd9`;
- evidence manifest sha256:
  `74f3c58283eef46a3b8f63699d730baa90337b9a7177146822170c22ec29e9ee`;
- shard checksum list sha256:
  `bb6107163f366334468b8db9b8e6ca74f8ddbd612f8b90d3e500e0efa3ba0312`;
- task-owned DataBlend input sha256:
  `859da9fb9d12c03d184152da12a9978072902f1390399d67391e885dabc47893`;
- split counts: train 46 exposed shards / 279 rows / 1,024,646 input tokens /
  228,927 supervised tokens; valid 1 exposed shard / 1 row / 1,491 input
  tokens / 1,428 supervised tokens; test 1 exposed shard / 0 rows / 0 tokens;
- accepted residual risk: the valid split has one packed hard-math row and the
  test split has zero rows. Carry this into task278/task279 and any future
  release decision.

Task264 #335 details now recorded:

- PR state: #335 MERGED at head
  `9d9285fd77820a5187440fbc2234dc36eb56942d`, merged at
  `2026-06-01T23:00:37Z` as merge commit
  `98e8aad39af9e705feed581e0ff9f8814073e2d8`;

- canary prompt file:
  `src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_v11_export_load_canary_prompts.yaml`
  sha256 `150ee11dc6e8efd3c865a8e9ed8a9ab8ce4f5ee032bed383c73a6cea34f52f1c`;
- gate config:
  `src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_aime2025_base_vs_ft_gate.yaml`
  sha256 `84eb36c62622aa8c6f83e65608f066492881f996c13eece4ba7b73b92733ae96`;
- gate module:
  `src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_aime2025_base_vs_ft_gate.py`
  sha256 `b84c8c87578b624675e19f6cb97eaf3f927c95ed51988c0372822f71606e67eb`;
- focused test:
  `tests/recipes/super3/test_qwen_aime2025_base_vs_ft_gate.py`
  sha256 `3b1775434ec8acf9adc3f62d83dd22e2b57d30cd85f6fe4f9b732081b546fccd`;
- task264 checks reported: `git diff --check`, `python3 -m py_compile ...`,
  and `PYTHONPATH=src pytest -q
  tests/recipes/super3/test_qwen_aime2025_base_vs_ft_gate.py` with `13 passed`;
- canary prompt set id:
  `qwen_v11_non_aime_export_load_canary_v1`, five synthetic non-AIME prompts;
- retention requirement: future V11 AIME artifacts must include
  `full_completions.jsonl` and `completion_retention_manifest.json`, and these
  retained completions are review-only, not trainable data.

## Required Paths

Stable Qwen3-4B base path:

`/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`

Verified in this review:

- `config.json`:
  `5beea1a4a34c62782bfb2f911c606741a3bab8f92d80a118fa053c28af12e8ba`
- `tokenizer_config.json`:
  `a62ff0a2472a0fa1b8eaabcb57c59b58afa42a22831dc141400b6e0cf2b65ce3`
- `tokenizer.json`:
  `aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4`
- Config shape:
  `Qwen3ForCausalLM`, `model_type=qwen3`, 36 layers, hidden size 2560,
  32 attention heads, 8 KV heads, intermediate size 9728, vocab size 151936.

Corrected AIME2025 base input/cache from task247:

- Local cache:
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache/aime_score_cache.opencompass_a6ad95f.db`
- Remote runner cache:
  `/root/task247_qwen_aime2025_qwen4b_base_smoke_s1/input/aime_score_cache.opencompass_a6ad95f.db`
- Source dataset revision:
  `opencompass/AIME2025@a6ad95f611d72cf628a80b58bd0432ef6638f958`
- Cache sha256 from task247/task260:
  `c8b287d9784d1d4ae5d3ea593a70850aea69b289e3d42e05951c5488330eaf74`

Shared storage boundary:

`/mnt/cephfs/data/processing/lei.song`

Verified in this review as `directory root:root 755`. Existing files under this
tree must not be deleted or overwritten.

Expected V11 task output roots:

- task262:
  `/work-agents/intern_nemotron_worker_1/outputs/task262_qwen_aime_v11_data_split_sidecar_s1/`
- task263:
  `/work-agents/intern_nemotron_worker_2/outputs/task263_qwen_aime_v11_base_load_planner_sanity_s1/`
- task264:
  `/work-agents/intern_nemotron_worker_3/outputs/task264_qwen_aime_v11_eval_gate_canary_retention_s1/`
- task265:
  `/work-agents/intern_nemotron_worker_4/outputs/task265_qwen_aime_v11_contam_regression_review_s1/`
- task266:
  `/work-agents/intern_nemotron_worker_5/outputs/task266_qwen_aime_v11_runbook_repro_gate_s1/`

## Stage Gate Matrix

| Stage | Required evidence | Current visible evidence | Gate |
|---|---|---|---|
| 1. V11 data/packing ready | task262 report with collision-free split materialization or fail-closed assertion; intended-vs-exposed rows/tokens/shards; hard-math/final-answer sidecar paths, counts, hashes; decontamination evidence; no AIME2025 train rows; task276 fresh packed root with manifest/checksum/Qwen contract evidence | task262 PR #336 is MERGED into main as `2ca6541c275d1eb64068e665af24147a796c818a`; task276 PR #344 is MERGED into main as `793e7dfa73ed1c5bdc8b7b98df5f31ffdd5e38ea` and supplies accepted packed root `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen` with Qwen contract PASS, parity PASS, and no-AIME train-leakage evidence | PACKED DATA EVIDENCE PRESENT for task278 no-training preflight; nonzero-LR training remains HOLD |
| 2. Base-load/import proof ready | task263 report proving Qwen3-4B base weight load or Bridge-approved HF import; positive load line or import manifest; base hashes; abort checks for random-init loss, NaN/Inf, zero LR; nonzero first-step LR schedule; NemTron sync path; task278 current preflight accepted or exact blocker reviewed | Coordinator Session 40 provides positive no-training Bridge import/preflight proof, but task278 #347 merged blocker docs record `CONFIG_IMPORT_PREFLIGHT_BLOCKED_MISSING_MEGATRON_BRIDGE` for the available route; task279 accepted this as blocker/preflight evidence only | PRIOR RUNTIME PROOF HISTORY PRESENT; CURRENT RUNTIME REMEDIATION MOVES TO TASK283/TASK284 |
| 3. Non-AIME canary ready | task264 canary prompt set with source/hashes; proof prompts are not AIME2025 and not train rows; config/tokenizer parity checks; retention schema for full completions/debug transcript | task264 PR #335 is MERGED into `origin/main` as `98e8aad39af9e705feed581e0ff9f8814073e2d8`; static canary prompt set and retention schema exist with hashes and focused tests | STATIC MERGED; live AIME remains HOLD until a future candidate passes the canary and task265 review clears exact inputs |
| 4. Bounded Qwen3-4B pilot allowed | Stages 1-3 PASS, task278 no-training preflight evidence, task279 independent approval processed by lead, lead clearance, Qwen3-4B only, code synced to task-owned `/root` run dir on NemTron, no AIME2025 train data, no task255 reuse | #346/task280 plan is merged and task279 approved #347 as blocker evidence only, but task278 remains blocked, task283/task284 are not complete, no lead smoke release exists, and no nonzero-LR smoke/training artifact exists | NO-GO/HOLD |
| 5. Same-harness AIME comparison allowed | New V11 FT artifact is reviewer-readable with manifest/hash checks, canary pass, base protocol parity, task265 review not blocking; use accepted task247 cache/protocol | #345/task281 plan is merged, but no V11 FT candidate, canary pass, endpoint, or AIME artifact exists | NO-GO |
| 6. Promotion/non-regression decision | FT exact-normalized AIME25 score `>= 11/30` under same 30x1 pilot protocol, and full promotion only after lead-defined full protocol; no 30B/8-GPU without explicit permission | no V11 same-harness result exists | NO-GO/HOLD |

## Command Templates

These commands are templates or read-only verification commands. They are not
authorization to train, eval, export, launch endpoints, merge, promote, or use
30B/8-GPU.

### Source And Branch Visibility

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git rev-parse origin/main origin/intern_nemotron_lead/session1-recovery-task-docs
git ls-remote --heads origin 'intern_nemotron_worker_*/task26*_qwen_aime_v11*'
gh pr list --state all --head <branch> --json number,title,state,headRefOid,baseRefName,mergeStateStatus,mergedAt,url
```

### Qwen3-4B Base Path Check

```bash
BASE=/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507
test -d "$BASE"
sha256sum "$BASE/config.json" "$BASE/tokenizer_config.json" "$BASE/tokenizer.json"
jq '{architectures, model_type, num_hidden_layers, hidden_size, num_attention_heads, num_key_value_heads, intermediate_size, vocab_size}' "$BASE/config.json"
```

### Shared Storage No-Delete Check

```bash
stat -c '%F %U:%G %a %n' /mnt/cephfs/data/processing/lei.song
```

Reviewers must reject any plan that uses destructive commands under
`/mnt/cephfs/data/processing/lei.song`. Task-owned new subdirectories may be
created only when the task requires it and must not overwrite existing shared
files.

### NemTron Sync Template

Before any debug run on `NemTron`, code must be synced to a task-owned `/root`
directory. Use a task-owned timestamped destination and avoid deleting shared
storage:

```bash
RUN=/root/task263_qwen_aime_v11_base_load_planner_sanity_s1/run_<UTC>
mkdir -p "$RUN"
rsync -a --exclude .git /work-agents/intern_nemotron_worker_2/Nemotron/ "$RUN/Nemotron/"
```

Any actual smoke launch still requires task262 data readiness and lead
clearance.

### Data/Packing Gate Template

Task262 must publish a manifest and a verification command equivalent to:

```bash
python <task262_verify_script.py> \
  --blend <v11_packed_qwen>/blend.json \
  --metadata <v11_packed_qwen>/splits/metadata.json \
  --exposed-splits <v11_packed_qwen>/splits \
  --fail-on-missing-intended-shards \
  --fail-on-basename-collision \
  --write-report <task262_output>/v11_split_sidecar_report.json
```

Required pass conditions:

- intended and exposed train rows/tokens/shards match, or the pipeline fails
  closed before training;
- hard-math and final-answer sources are decontaminated non-heldout sources;
- AIME2025 prompts/labels appear only as held-out eval/decontamination evidence.

### Base-Load And Nonzero-LR Gate Template

Task263 must publish either an explicit Megatron checkpoint-load proof or a
Bridge-approved HF import proof. Logs must fail closed if all acceptable proof
patterns are absent.

```bash
rg -n 'successfully loaded checkpoint|Bridge-approved HF import|checkpoint.load|load_main_params_from_ckpt|learning rate|nan|inf' <task263_logs>
```

Required pass conditions:

- positive base-load/import proof before SFT;
- no raw-HF-as-Megatron-root silent continuation;
- first logged train step has nonzero LR;
- no random-init-scale first loss/PPL trigger;
- no NaN/Inf trigger;
- configured iterations can consume the intended V11 split at least once.

### Non-AIME Canary And Retention Gate Template

Task264 must publish canary prompt source and hashes, plus an artifact retention
schema.

```bash
sha256sum <task264_canary_prompt_file>
rg -n 'AIME|aime2025|opencompass/AIME2025' <task264_canary_prompt_file>
jq -e '.full_completion or .debug_transcript' <future_eval_results_or_schema>
```

Required pass conditions:

- canary prompts are synthetic, non-AIME, and not train rows;
- canary requires coherent text plus short numeric/final-answer style response;
- future AIME artifacts retain full completions or deterministic debug
  transcripts sufficient for parser-vs-generation forensics.

### Same-Harness AIME Comparison Template

Use task243/task247 corrected protocol only after stages 1-5 pass:

```bash
python3 /root/<task>/eval/run_corrected_math_full_eval.py \
  --aime-score-cache /root/task247_qwen_aime2025_qwen4b_base_smoke_s1/input/aime_score_cache.opencompass_a6ad95f.db \
  --hmmt-output-jsonl /root/<task>/input/not_used_hmmt.jsonl \
  --output-dir /root/<task>/eval/<candidate_ft_aime2025_30x1> \
  --endpoint-url http://127.0.0.1:<port>/v1/chat/completions \
  --model-id <served-v11-ft-model-id> \
  --tasks aime25 \
  --aime-prompt-variant original \
  --aime-max-tokens 8192 \
  --aime-limit-rows 30 \
  --parallelism 4 \
  --timeout 900
```

The comparison is valid only when the base and FT runs use the same cache,
prompt variant, endpoint route, sampling parameters, parser, and all-request
denominator. Parsed rate is diagnostic; the gate is exact-normalized accuracy.

## Required Artifacts By Upstream Task

### task262

Required before stage 1 PASS:

- task262 branch/head/PR or mailbox blocker; current PR #336 is MERGED at
  `8fd3ff6065290b850c98db5f7abff91aa6880967` with merge commit
  `2ca6541c275d1eb64068e665af24147a796c818a`;
- V11 packed root path;
- `blend.json`, `splits/metadata.json`, shard summary, and generated manifest
  hashes;
- intended-vs-exposed row/token/shard table;
- collision check log;
- sidecar source paths, row counts, checksums;
- decontamination evidence against AIME25/HMMT/MATH heldouts;
- no-AIME-train-data confirmation.

Current #336 static evidence:

- output root:
  `/work-agents/intern_nemotron_worker_1/outputs/task262_qwen_aime_v11_data_split_sidecar_s1/`;
- report and manifest hashes:
  `task262_v11_data_split_sidecar_report.md`
  `df5a203628bcb563148d1123a121d0d4f0d3207ab4e52be62f1c6ea00dbc1789`,
  `manifest.json`
  `4c9874c9341b1e286533bd67eafa6a922567e905c9d3bb7bd78e8970eb777383`;
- split audit and sidecar plan hashes:
  `split_materialization_audit.json`
  `b2009b2c509620c5dde2412ee4dedf4efb8995431ef4bec4d353ba14dc3787b3`,
  `v11_qwen_agentic_sft_blend_plan.json`
  `2b3f0942eb04e077c5025c60be87355bf233b33085660a0b85a0b8b03b569e2a`,
  `task251_source_summaries.json`
  `d0d6b253c2ee9620d2b9c023cdc680b5f6c762e0c163174572fd40e9c1d35e6a`;
- final-answer decontam hashes:
  `final_answer_ngram_decontam_scan.json`
  `feffa6c677b1bc86b5f2f9ad8a8c3506582844cdb5b6a25bd8741322a9298370`,
  `final_answer_ngram_decontam_report.md`
  `9f73fb0cbccb048ab8137efc00bc4a9ba76cc87a708796af82b6768e626531fe`;
- current limitation: task262 alone is static repair/report evidence merged into
  main; task276 now supplies the fresh packed Qwen root for no-training
  preflight.

### task276

Required before task278 preflight:

- task276 branch/head/PR or blocker; current PR #344 is MERGED at
  `07efab4fa0d8367e96f54af3d2cdc70768d73595` with merge commit
  `793e7dfa73ed1c5bdc8b7b98df5f31ffdd5e38ea`;
- accepted packed Qwen root:
  `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen`;
- split manifest and metadata hashes;
- evidence manifest and shard checksum list;
- train/valid/test row, token, and shard counts;
- Qwen contract PASS evidence;
- no-AIME train-leakage evidence;
- explicit carry-forward of valid 1-row and test 0-row residual risk.

Current #344 evidence:

- `packed_qwen_evidence_manifest.json` sha256
  `74f3c58283eef46a3b8f63699d730baa90337b9a7177146822170c22ec29e9ee`;
- `packed_qwen_shard_checksums.sha256` sha256
  `bb6107163f366334468b8db9b8e6ca74f8ddbd612f8b90d3e500e0efa3ba0312`;
- task282 read-only check: evidence manifest sidecar PASS and all 48 shard
  checksum entries PASS;
- split counts: train 279 rows, valid 1 row, test 0 rows.

### task263

Required before stage 2 PASS:

- task263 branch/head/PR or blocker; current visible task263 branch remains
  `4af57e0e61703a063c1ef42def44119a7eea5cf9` with no PR and the older local
  `megatron`/`megatron.bridge` environment blocker;
- Session 40 coordinator runtime proof now supplies the missing no-training
  Bridge import/preflight evidence:
  `/work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z`;
- Qwen3-4B base file hashes;
- import/checkpoint-load proof log;
- abort-check script/config and log;
- schedule manifest showing nonzero first-step LR and enough iterations;
- NemTron `/root/<task>/run_<UTC>` sync path;
- resource shape, limited to Qwen3-4B and lead-cleared bounded smoke.

### task264

Required before stage 3 PASS:

- task264 branch/head/PR or blocker; current PR #335 is MERGED at
  `9d9285fd77820a5187440fbc2234dc36eb56942d` with merge commit
  `98e8aad39af9e705feed581e0ff9f8814073e2d8`;
- canary prompt file path and sha256; current static prompt set is
  `qwen_v11_export_load_canary_prompts.yaml` sha256
  `150ee11dc6e8efd3c865a8e9ed8a9ab8ce4f5ee032bed383c73a6cea34f52f1c`;
- non-AIME/non-train proof for canary prompts;
- config/tokenizer/generation parity checklist;
- retention schema requiring full completions or deterministic debug transcript;
- same-harness gate statement preserving `FT >= 11/30`.

### task265

Required before stages 4-6 PASS:

- task265 branch/head/PR or blocker; current branch is
  `ca5ea1c405ef142ee51a43fcbab477a2958e48dc`, no PR, no repo-visible task265
  report, and worker_4 status records mailbox-only matrix refresh id
  `7e718a2c0ea746ed81352db5b5b6fe57`;
- exact task262/task263/task264 heads reviewed;
- contamination verdict;
- regression/gate verdict;
- approve/request-changes/block matrix;
- residual risks and unreviewed surfaces.

### task278

Required before any bounded nonzero-LR smoke release:

- exact branch/head/PR or exact blocker for the no-training config/import
  preflight;
- host, code revision, environment, and whether code was synced to a task-owned
  `/root` directory on `NemTron`;
- task276 packed root, split manifest, metadata, evidence manifest, and shard
  checksum references;
- Qwen3-4B checkpoint path
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`;
- config resolution, data readability, Bridge/checkpoint load or import proof,
  and fail-closed guard logs;
- proof that no optimizer step, training loop, training checkpoint save, export,
  endpoint, canary, or AIME/task243 eval ran;
- explicit disposition of the valid 1-row and test 0-row risk for preflight
  only.

Current state: task278 PR #347 is MERGED at `2026-06-02T05:13:14Z` as
`28039222ad5d4054891713d85d05a15a491d8a96` from exact head
`b7e544100ac13eaa908a9d1af6fafaf599bc3310`. The latest artifact root is
`/work-agents/intern_nemotron_worker_2/outputs/task278_qwen_aime_v11_task276_config_import_preflight_s1/run_20260602T045642Z`;
the report sha is
`c81208f6af524d117a333495ab4b5a971aeecf36d38000a737318ff346f77f23`. Local
packed-data readability, Qwen packed/training contract checks, and Qwen HF
config/tokenizer import pass, but full Megatron-Bridge training-stack import is
blocked by missing `megatron`/`nemo`. #347 is merged blocker docs only, not a
runtime pass.

### task279

Required before any bounded nonzero-LR smoke release:

- independent review of exact task278 branch/head/artifacts;
- pass/fail for data/config/import/no-training proof;
- sparse valid/test risk disposition;
- approve/request-changes/block decision processed by lead.

Current state: task279 approved exact #347 head
`b7e544100ac13eaa908a9d1af6fafaf599bc3310` and the
`run_20260602T045642Z` artifacts as blocker/preflight evidence only. Lead
approval comment is `4598906687`.

### task283

Required before stage 4 can be reconsidered:

- exact task283 branch/head/PR or exact blocker;
- no-training runtime-route remediation/config-import preflight evidence;
- commands, host, Python path, environment, `/root` sync path, logs, and
  task-owned artifact paths;
- reconciliation of coordinator Session 40 positive import proof with task278
  missing-runtime evidence;
- task276 packed root and Qwen3-4B path references;
- proof of Bridge/config/import success or exact package/module blocker;
- proof that no training loop, optimizer step, training checkpoint save, export,
  endpoint, canary, or AIME/task243 eval ran.

Current state: task283 is accepted on worker_2 remote branch
`origin/intern_nemotron_worker_2/task283_qwen_aime_v11_bridge_runtime_remediation_preflight_s1`
at `c1d988e29abafa51a9c3f83a98e21b229135f97e`. No task283 remediation evidence
is recorded in this runbook yet.

### task284

Required before stage 4 can be reconsidered:

- independent review of exact task283 branch/head/artifacts;
- pass/fail for runtime/config/import/no-training proof;
- sparse valid/test risk disposition;
- approve/request-changes/block decision.

Current state: task284 is accepted/cleaned on worker_4 remote branch
`origin/intern_nemotron_worker_4/task284_qwen_aime_v11_task283_runtime_gate_review_s1`
at `27d28b54342a98a4a336c46661964759f2790619` and waits for exact task283
evidence.

### task280

Required before any bounded nonzero-LR smoke release:

- no-run plan for a minimal Qwen3-4B SFT smoke using task276 packed root;
- exact LR, max train steps, global and micro batch, sequence length, output
  root, checkpoint naming, logs, and stop criteria;
- fail-closed proof that AIME2025 prompts/labels are not trainable rows;
- explicit task255 non-reuse and shared-path non-overwrite policy.

Current state: #346 is merged plan-only HOLD at merge commit
`7ba65549500e9ca70fc560ed919d6bfa61f088b2`. No smoke launch is authorized.

### task281

Required before any canary or corrected AIME2025 FT-vs-base comparison:

- no-run non-AIME canary plan with prompt source, hashes, metrics,
  full-completion retention, and non-train proof;
- corrected AIME2025 same-harness comparison plan preserving accepted base
  comparator `11/30 = 0.36666666666666664`;
- same cache, prompt variant, route, parser, scoring normalization, sampling,
  tokenizer chat template, and all-request denominator;
- base rerun requirement if any comparison protocol changes;
- FT score must be at least base before promotion discussion.

Current state: #345 is merged plan-only HOLD at merge commit
`0d008ddbc8a87445e69f95e02ef9a07ae17791d6`. No live canary or AIME/task243 eval
is authorized.

## Residual Risks

- task262 #336 is merged into main with static data/packing repair evidence,
  fresh final-answer n-gram decontamination evidence, and a readable output
  bundle. task276 #344 is also merged and supplies the fresh packed Qwen root
  for task278 no-training preflight only.
- task276/task277 carry accepted sparse-split risk: valid has one packed row and
  test has zero rows. This is not broad validation readiness or training
  clearance.
- task278 #347 now has repo-visible blocker evidence and a verified latest
  artifact root, but its disposition remains
  `CONFIG_IMPORT_PREFLIGHT_BLOCKED_MISSING_MEGATRON_BRIDGE`; it is merged
  blocker docs only, not accepted runtime preflight readiness.
- task279 approved #347 current head as blocker/preflight evidence only, not as
  a runtime pass or smoke release.
- task283/task284 are now the active no-training remediation/review gates:
  task283 accepted at `c1d988e29abafa51a9c3f83a98e21b229135f97e`; task284
  accepted/cleaned at `27d28b54342a98a4a336c46661964759f2790619`.
- task280 #346 and task281 #345 are merged planning records only; they do not
  authorize live execution.
- task263 is visible at `4af57e0e61703a063c1ef42def44119a7eea5cf9`, but it has
  no PR and still records the older local runtime blocker. Coordinator Session
  40 supersedes that blocker for no-training Bridge import/preflight proof, but
  does not provide nonzero-LR training evidence or a future candidate artifact.
- task264 static canary/retention evidence from #335 is merged into main at
  `98e8aad39af9e705feed581e0ff9f8814073e2d8`, but no future V11 candidate has
  produced canary pass artifacts.
- task265 remains the pending independent review input: remote branch is
  `ca5ea1c405ef142ee51a43fcbab477a2958e48dc` and worker_4 status records a
  mailbox-only matrix refresh, but no task265 PR or repo-visible matrix file is
  available for this runbook to inspect.
- Worker-local dirty or in-progress files in other workspaces are not treated as
  accepted evidence because they are not published exact heads.
- The runbook cannot prove future V11 correctness. It only defines the evidence
  needed before lead can permit the next bounded Qwen3-4B stage.

## Final Gate State

| Decision | Status |
|---|---|
| task266 runbook/repro gate | PASS as static documentation |
| V11 data/packing ready | PACKED DATA EVIDENCE PRESENT via #336/#344 for task278 no-training preflight; nonzero-LR training HOLD |
| V11 base-load/import ready | PRIOR RUNTIME PROOF HISTORY PRESENT; task278 #347 merged blocker docs; task283/task284 remediation/review required |
| V11 non-AIME canary ready | STATIC MERGED via #335; live use HOLD |
| Bounded Qwen3-4B pilot allowed | NO-GO/HOLD |
| Same-harness AIME comparison allowed | NO-GO |
| Promotion or 30B/8-GPU | NO-GO |

No stage should move past HOLD until the missing upstream artifacts are
published and independently reviewed at exact branch heads.
