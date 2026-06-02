# task266 V11 runbook/repro gate report

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_5,SESSION=2 -->

## Summary

- Recommendation for task266: PASS as a static V11 runbook/repro gate.
- Recommendation for V11 execution: HOLD for export, endpoint, promotion,
  task255 reuse, AIME2025 train-data use, shared deletion, 30B, and 8-GPU. The
  task293 corrected AIME2025 metric beats the accepted base comparator, #357
  independently approved it with residual, and #356 merged the metric report
  into main.
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
  comment `4598906687`. At that time, task283 was accepted at
  `c1d988e29abafa51a9c3f83a98e21b229135f97e`; task284 is accepted/cleaned at
  `27d28b54342a98a4a336c46661964759f2790619`. The post-smoke refresh below
  supersedes this with merged #349/#350 provenance.
- task289/task295 post-smoke/post-AIME refresh: #349/task283 is merged
  no-training preflight PASS at merge commit
  `f82f8f73c39bc93ff268f45845a94060585b8290`; #350/task285 is merged bounded
  Qwen3-4B smoke evidence at merge commit
  `5d32f07698249d9d352e7ba6da9c6d3bd88eb3f0`; task286 approved #350 exact head
  `fc379240c8517de10e37a5438f87b6b0994399f0` as bounded smoke evidence only.
  #352/task287 is now merged at `2026-06-02T07:39:18Z` as
  `ca1ab63588651351b3e669450659abd2ad2c73e8` from exact head
  `52834d74c79ab98b5e125434160843752c34d47a`, with official `BLOCK` evidence:
  checkpoint load proof passed, but no retained completions or accepted canary
  pass exist. task288 approved blocker closeout as evidence only at branch head
  `a4afc814554f92039d886548a8979cf847e6265e`; #353/task290 is merged at
  `2026-06-02T07:52:08Z` as
  `a372dcd7cd866dc02951f4f1c86eaf05a4c885b4` from exact head
  `daad63efe77f19b8d56c62eca9d9f9331efd6e22`. #354/task291 is merged as
  `34de04ff06cc2921ef1c65cde347b1f6e1b54bcf` from head
  `2fda1ed46da4c82712a5c22c85bf124c26c6376f` with retained synthetic non-AIME
  route-pass evidence; #355/task292 is merged as
  `228ffd741bb9fa4eae6abf8d37bc171397151d7a` from head
  `e519fecc1065bd055a69fdf271bd21994facd13b` with decision
  `APPROVE_CANARY_ROUTE_PASS`. #357/task294 is merged as
  `24268157bd7088fea0f37d149cfc6ec042aa0e5a` from head
  `f1c00a0cc8e2a9cda5e2caef9bc5137cda7835a1` with decision
  `APPROVE_AIME_GATE_PASS_WITH_RESIDUAL`. #356/task293 is merged as
  `31a3e962544202954f0afba211888f7414b38d7c` from head
  `672d0101681a5d9c4b6c34814c75fcc0d97b4fcb` and reports corrected AIME2025
  FT `12/30 = 0.4` versus accepted base `11/30 = 0.36666666666666664`.
- Boundary kept: no training, eval, export, endpoint launch, merge,
  promotion, 30B/8-GPU authorization, AIME2025 train-data use, shared deletion,
  or worker branch alteration.

The first measurable V11 corrected AIME result now satisfies:

`task293_qwen3_4b_ft_exact_normalized_accuracy = 12/30 >= 11/30`

under the corrected AIME2025 30x1 harness. This is an eval-metric pass with
accepted residual only; export, endpoint, promotion, task255 reuse, AIME2025
train-data use, shared deletion, 30B, and 8-GPU remain held pending explicit
lead release for those actions.

## Evidence Inventory Checked

| Surface | Visible evidence | Current status |
|---|---|---|
| task262 data/packing repair | PR #336 MERGED at head `8fd3ff6065290b850c98db5f7abff91aa6880967`, merge commit `2ca6541c275d1eb64068e665af24147a796c818a`; substantive repair commit `0f825b9357a2a8f7814f693ea4c27027c5fbdd31`; final-answer n-gram decontam evidence commit `5e431f4939799ae52c7d2002682352f2f2df6f3b`; latest head commit is metadata-only reconciliation; report `v11_data_split_sidecar_report.md`; output bundle under `/work-agents/intern_nemotron_worker_1/outputs/task262_qwen_aime_v11_data_split_sidecar_s1/` | STATIC MERGED into main as data/packing repair evidence |
| task276 fresh packed Qwen root | PR #344 MERGED at head `07efab4fa0d8367e96f54af3d2cdc70768d73595`, merge commit `793e7dfa73ed1c5bdc8b7b98df5f31ffdd5e38ea`; report `v11_rematerialized_packed_qwen_report.md`; packed root `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen`; evidence manifest and all 48 shard checksum entries verified by task282 | PACKED DATA EVIDENCE PRESENT and used by task283/task285; sparse valid/test risk remains carried |
| task278 config/import preflight | PR #347 MERGED at `2026-06-02T05:13:14Z` as `28039222ad5d4054891713d85d05a15a491d8a96` from head `b7e544100ac13eaa908a9d1af6fafaf599bc3310`; artifact root `/work-agents/intern_nemotron_worker_2/outputs/task278_qwen_aime_v11_task276_config_import_preflight_s1/run_20260602T045642Z`; report sha `c81208f6af524d117a333495ab4b5a971aeecf36d38000a737318ff346f77f23`; manifest sha `57b0a9d5ce51dd3f48514b802e8cfaff973a8ad297df466ef551d86f84840692`; disposition `CONFIG_IMPORT_PREFLIGHT_BLOCKED_MISSING_MEGATRON_BRIDGE` | MERGED BLOCKER DOCS ONLY; runtime preflight remains blocked |
| task279 preflight review | worker_4 approved #347 exact head `b7e544100ac13eaa908a9d1af6fafaf599bc3310` as blocker/preflight evidence only; lead approval comment `4598906687` | BLOCKER EVIDENCE APPROVED; no runtime pass |
| task263/runtime base-load planner sanity | task263 branch `4af57e0e61703a063c1ef42def44119a7eea5cf9` remains the older local-env blocker record. Coordinator Session 40 at branch `intern_nemotron_coordinator/session1-resume-interrupted-work` head `8c8364101d6adb07f9e67c17fece3e2b2bb280ca` provides newer no-training runtime proof: `nemo=/root/.local/lib/python3.12/site-packages/nemo/__init__.py`, `IMPORT_DONE`, `BRIDGE_IMPORT_RC=0`, `TASK270_FAIL_CLOSED_PREFLIGHT=PASS`, remote imported checkpoint root `/root/task_coordinator_nemotron_coordinator_06b9acba/session40_nemo_install_probe_20260602T015146Z/qwen3_4b_bridge_import_iter0`, local evidence root `/work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z` | RUNTIME PROOF PRESENT for no-training Bridge import/preflight only; live nonzero-LR training evidence and future candidate artifacts remain HOLD |
| task264 canary/retention gate | PR #335 MERGED at `9d9285fd77820a5187440fbc2234dc36eb56942d`; merged at `2026-06-01T23:00:37Z` as `98e8aad39af9e705feed581e0ff9f8814073e2d8`; official closeout report `v11_canary_retention_report.md`; static canary/retention code/config/tests added | STATIC MERGED into main; #352/task287 is the merged canary execution/blocker record for the task285 checkpoint |
| task280 bounded smoke plan | PR #346 MERGED at `2026-06-02T04:59:45Z` as `7ba65549500e9ca70fc560ed919d6bfa61f088b2`; report `qwen3_4b_v11_sft_smoke_plan_hold_report.md`; disposition `PLAN_READY_HOLD_TASK278_TASK279_RELEASE` | PLAN SUPERSEDED by #350 bounded smoke evidence; future training remains held |
| task281 canary/AIME plan | PR #345 MERGED at `2026-06-02T04:54:59Z` as `0d008ddbc8a87445e69f95e02ef9a07ae17791d6`; report `canary_aime_eval_plan_hold_report.md`; disposition `PLAN_READY_HOLD` | PLAN-ONLY RECORD; task287/task288/task290 gates must clear before AIME/task243 |
| task283 runtime remediation | PR #349 MERGED at `2026-06-02T06:03:58Z` as `f82f8f73c39bc93ff268f45845a94060585b8290` from head `2d042cedb0c4cc448c89d57d7b18986d92361349`; report `bridge_runtime_remediation_preflight_report.md`; local root `/work-agents/intern_nemotron_worker_2/outputs/task283_qwen_aime_v11_bridge_runtime_remediation_preflight_s1/run_20260602T052346Z`; disposition `CONFIG_IMPORT_PREFLIGHT_PASS_NO_TRAINING_NO_CHECKPOINT_SAVE` | NO-TRAINING PREFLIGHT PASS; not a training/export/eval release |
| task284 task283 review | prior worker_4 review gate for task283; task283 subsequently merged as #349 with lead processing | REVIEW GATE PROCESSED for no-training preflight only |
| task285 bounded Qwen3-4B smoke | PR #350 MERGED at `2026-06-02T06:53:14Z` as `5d32f07698249d9d352e7ba6da9c6d3bd88eb3f0` from head `fc379240c8517de10e37a5438f87b6b0994399f0`; local root `/work-agents/intern_nemotron_worker_2/outputs/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z`; two optimizer iterations with nonzero LR and finite loss; latest checkpoint iteration `2`; checkpoint inventory sha `d4cc3d1e5a047e321e98896996610f1ace0b5c45acd3cbe11bb0a8389ea97b78` | BOUNDED SMOKE EVIDENCE ONLY; post-train eval/SIGTERM RC=1 risk |
| task286 smoke review | worker_4 branch `origin/intern_nemotron_worker_4/task286_qwen_aime_v11_task285_smoke_gate_review_s1` at `a0db36c1d6831744cd972ac65b90817cfbcfefdc`; mailboxes `71d5ac1b1bb44bae8163f014563714cf` and `9b673d61cf6e4ce5a64d84f7f6198230` approve #350 exact head as bounded smoke evidence only | APPROVED SMOKE-ONLY; next gate is non-AIME canary |
| task287 non-AIME canary | PR #352 MERGED at `2026-06-02T07:39:18Z` as `ca1ab63588651351b3e669450659abd2ad2c73e8` from exact head `52834d74c79ab98b5e125434160843752c34d47a`; report `non_aime_canary_retention_report.md`; local root `/work-agents/intern_nemotron_worker_3/outputs/task287_qwen_aime_v11_non_aime_canary_retention_s1/run_20260602T070403Z`; disposition `BLOCK`; checkpoint load proof passed, but retained completion rows are `0` and `canary_summary.json` is absent | MERGED BLOCK; no canary pass accepted |
| task288 task287 review | worker_4 branch `origin/intern_nemotron_worker_4/task288_qwen_aime_v11_task287_canary_gate_review_s1` fetched at `a4afc814554f92039d886548a8979cf847e6265e`; no PR; Session 27 mailed `APPROVE_BLOCKER_CLOSEOUT` as `a7667e01d0cb4188aa0e5dc222ae7da0` | APPROVED BLOCKER EVIDENCE ONLY |
| task290 task287 blocker review | PR #353 MERGED at `2026-06-02T07:52:08Z` as `a372dcd7cd866dc02951f4f1c86eaf05a4c885b4` from exact head `daad63efe77f19b8d56c62eca9d9f9331efd6e22`; lead approval comment `4599915303`; report decision `APPROVE_BLOCKER_CLOSEOUT` | MERGED BLOCKER REVIEW; no AIME/task243 release |
| task291 route unblock | PR #354 MERGED at `2026-06-02T08:30:04Z` as `34de04ff06cc2921ef1c65cde347b1f6e1b54bcf` from exact head `2fda1ed46da4c82712a5c22c85bf124c26c6376f`; artifact root `/work-agents/intern_nemotron_worker_2/outputs/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/run_20260602T081136Z`; retained synthetic non-AIME prompts `5/5`; canary summary sha `dd855c2c32b0b7411ee1cd365311363f1d3338753560107768b684b8fb660d40`; checksum manifest sha `08477bf8be669314a54359edeeca16de4605262ce5d553944e3477e4ff46f97d` | MERGED ROUTE PASS for no-export/no-endpoint synthetic non-AIME route only |
| task292 route review | PR #355 MERGED at `2026-06-02T08:37:35Z` as `228ffd741bb9fa4eae6abf8d37bc171397151d7a` from exact head `e519fecc1065bd055a69fdf271bd21994facd13b`; report `task291_canary_route_review_report.md`; decision `APPROVE_CANARY_ROUTE_PASS`; all task291 checksum manifest entries recomputed and matched | MERGED INDEPENDENT ROUTE REVIEW; detokenized fallback residual carried |
| task293 corrected AIME eval | PR #356 MERGED at `2026-06-02T11:22:34Z` as `31a3e962544202954f0afba211888f7414b38d7c` from exact head `672d0101681a5d9c4b6c34814c75fcc0d97b4fcb`; report `task285_iter2_same_harness_aime_eval_report.md`; local output root `/work-agents/intern_nemotron_worker_3/outputs/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z`; remote root `/root/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z`; FT `12/30 = 0.4`; accepted base `11/30 = 0.36666666666666664`; summary sha `64a378ca54534ec426b92a7b6bc436edb4fddd2ea1ba831f61afeed4e1ad39b7` | MERGED PASS for corrected AIME eval metric only |
| task294 task293 review | PR #357 MERGED at `2026-06-02T11:16:53Z` as `24268157bd7088fea0f37d149cfc6ec042aa0e5a` from exact head `f1c00a0cc8e2a9cda5e2caef9bc5137cda7835a1`; report `task293_aime_gate_review_report.md`; decision `APPROVE_AIME_GATE_PASS_WITH_RESIDUAL` | MERGED INDEPENDENT AIME GATE REVIEW; residual accepted for metric-gate evidence only |
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
| 1. V11 data/packing ready | task262 report with collision-free split materialization or fail-closed assertion; intended-vs-exposed rows/tokens/shards; hard-math/final-answer sidecar paths, counts, hashes; decontamination evidence; no AIME2025 train rows; task276 fresh packed root with manifest/checksum/Qwen contract evidence | task262 PR #336 is MERGED into main as `2ca6541c275d1eb64068e665af24147a796c818a`; task276 PR #344 is MERGED into main as `793e7dfa73ed1c5bdc8b7b98df5f31ffdd5e38ea` and supplies accepted packed root `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen` with Qwen contract PASS, parity PASS, and no-AIME train-leakage evidence | PACKED DATA EVIDENCE PRESENT and used by task283/task285; sparse valid/test risk remains carried |
| 2. Base-load/import proof ready | task263 report proving Qwen3-4B base weight load or Bridge-approved HF import; positive load line or import manifest; base hashes; abort checks for random-init loss, NaN/Inf, zero LR; nonzero first-step LR schedule; NemTron sync path; task283 no-training preflight accepted | Coordinator Session 40 provides positive no-training Bridge import/preflight proof, and #349/task283 is MERGED with `CONFIG_IMPORT_PREFLIGHT_PASS_NO_TRAINING_NO_CHECKPOINT_SAVE`; #350/task285 also records Bridge base import rc `0` before optimizer execution | NO-TRAINING/BASE IMPORT EVIDENCE PRESENT; training/eval/export still gated |
| 3. Non-AIME canary ready | task264 canary prompt set with source/hashes; proof prompts are not AIME2025 and not train rows; config/tokenizer parity checks; retention schema for full completions/debug transcript; task287 pass or reviewed route repair | task264 static prompt/retention contract is merged; #352/task287 is MERGED at `ca1ab63588651351b3e669450659abd2ad2c73e8` with `BLOCK`; task288/#353-task290 approved blocker evidence; #354/task291 is MERGED route pass with `5/5` retained synthetic non-AIME completions; #355/task292 approved the route pass | ROUTE PASS PRESENT for no-export/no-endpoint synthetic non-AIME route only |
| 4. Bounded Qwen3-4B pilot allowed | Stages 1-3 pre-smoke gates, task283 preflight PASS, task286 approval, lead smoke release, Qwen3-4B only, code synced to task-owned `/root` run dir on NemTron, no AIME2025 train data, no task255 reuse | #350/task285 is MERGED and task286 approved it as bounded smoke evidence only: two optimizer iterations, nonzero LR, finite loss, iter2 checkpoint; post-train built-in eval/SIGTERM returned RC=1 | SMOKE EVIDENCE PRESENT ONLY; no clean train/eval pass |
| 5. Corrected AIME2025 metric evidence | New V11 FT artifact is reviewer-readable with manifest/hash checks, reviewed route evidence, base protocol parity, accepted task247 cache/protocol, and explicit lead release | #356/task293 is MERGED at `31a3e962544202954f0afba211888f7414b38d7c` and reports FT `12/30 = 0.4` versus accepted base `11/30 = 0.36666666666666664`; #357/task294 accepted task293 `sampling_exact_parameter_match=false` as bounded residual | PASS_EVAL_METRIC_WITH_RESIDUAL |
| 6. Promotion/non-regression decision | FT exact-normalized AIME25 score `>= 11/30` under corrected 30x1 pilot protocol, full promotion only after lead-defined full protocol, and no 30B/8-GPU without explicit permission | task293 metric beats base by `+1/30`, but no export/endpoint/promotion/scale release exists | HOLD/NO-GO for release, export, endpoint, promotion, 30B, and 8-GPU |

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

Current state: task283 PR #349 is MERGED at `2026-06-02T06:03:58Z` with merge
commit `f82f8f73c39bc93ff268f45845a94060585b8290` from head
`2d042cedb0c4cc448c89d57d7b18986d92361349`. The accepted artifact root is
`/work-agents/intern_nemotron_worker_2/outputs/task283_qwen_aime_v11_bridge_runtime_remediation_preflight_s1/run_20260602T052346Z`,
with disposition `CONFIG_IMPORT_PREFLIGHT_PASS_NO_TRAINING_NO_CHECKPOINT_SAVE`.
This is no-training preflight evidence only.

### task284

Required before stage 4 can be reconsidered:

- independent review of exact task283 branch/head/artifacts;
- pass/fail for runtime/config/import/no-training proof;
- sparse valid/test risk disposition;
- approve/request-changes/block decision.

Current state: task284 was the independent review gate for task283. task283 has
since merged as #349 after lead processing. This remains no-training preflight
review provenance only and does not release training, eval, export, endpoint, or
promotion.

### task285

Required before post-smoke canary can be considered:

- exact task285 branch/head/PR and merged report;
- Bridge-approved Qwen3-4B base import proof before optimizer execution;
- fail-closed pre-optimizer guard and no AIME2025 train-data proof;
- bounded command showing Qwen3-4B only, at most two GPUs, bounded iterations,
  nonzero LR, finite loss, and retained task-owned checkpoint artifacts;
- residual risk statement for any nonzero command return after checkpoint save.

Current state: task285 PR #350 is MERGED at `2026-06-02T06:53:14Z` with merge
commit `5d32f07698249d9d352e7ba6da9c6d3bd88eb3f0` from head
`fc379240c8517de10e37a5438f87b6b0994399f0`. Its local root is
`/work-agents/intern_nemotron_worker_2/outputs/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z`.
Retry3 logged two optimizer iterations with nonzero LR and finite loss, then
saved checkpoint iteration `2` under
`/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3`.
The checkpoint inventory sha is
`d4cc3d1e5a047e321e98896996610f1ace0b5c45acd3cbe11bb0a8389ea97b78`; checksum
manifest sha is `802ef28a30b7ae5a2359b481fc6c8882d1cc2804d0f1edd25cca84973f7794c4`.
The smoke is bounded evidence only because post-train built-in validation
received SIGTERM and returned `SMOKE_RETRY3_COMMAND_RC=1`.

### task286

Required before post-smoke canary can be considered:

- independent exact-head review of task285 artifacts;
- pass/fail on base import, command bounds, nonzero LR, finite loss, checkpoint
  artifact retention, AIME holdout, task255 non-reuse, and sparse split risk;
- lead-processed approval or blocker.

Current state: task286 approved #350 exact head
`fc379240c8517de10e37a5438f87b6b0994399f0` as bounded Qwen3-4B smoke evidence
only. The detailed mailbox is `71d5ac1b1bb44bae8163f014563714cf`; the official
exact-head confirmation mailbox is `9b673d61cf6e4ce5a64d84f7f6198230`.

### task287

Required before same-harness AIME comparison can be considered:

- official task287 branch/head/PR or mailbox artifact report;
- no-export/no-endpoint non-AIME canary/completion-retention result or exact
  blocker for the task285 iter2 checkpoint;
- prompt provenance proving prompts are synthetic non-AIME and not train rows;
- retained full completions, response hashes, final-answer extraction, and
  degeneration flags.

Current state: #352/task287 is merged at `2026-06-02T07:39:18Z` as
`ca1ab63588651351b3e669450659abd2ad2c73e8` from exact head
`52834d74c79ab98b5e125434160843752c34d47a` with official disposition `BLOCK`.
The report records `LOAD_MEGATRON_MODEL=PASS`, prompt source sha
`150ee11dc6e8efd3c865a8e9ed8a9ab8ce4f5ee032bed383c73a6cea34f52f1c`, prompt
manifest sha `69d6634c47eea160548fe2779b6dd6038dc7605e8c9a894660a385efc9ae7cc2`,
local output root
`/work-agents/intern_nemotron_worker_3/outputs/task287_qwen_aime_v11_non_aime_canary_retention_s1/run_20260602T070403Z`,
and remote run root
`/root/task287_qwen_aime_v11_non_aime_canary_retention_s1/run_20260602T070403Z`.
The final attempt hit a CUDA device-side assert during sampling, retained no
completions, wrote no `canary_summary.json`, and recorded correct canary
answers `0/5`. Therefore same-harness AIME remains blocked.

### task288

Required before same-harness AIME comparison can be considered:

- independent review of exact task287 evidence;
- approve/request-changes/block decision processed by lead;
- confirmation no export, endpoint, AIME/task243 eval, additional training,
  task255 reuse, 30B, or 8-GPU was used.

Current state: task288 is active on worker_4 branch
`origin/intern_nemotron_worker_4/task288_qwen_aime_v11_task287_canary_gate_review_s1`
at fetched head `a4afc814554f92039d886548a8979cf847e6265e`. No task288 PR is
visible. Session 27 approved #352 exact head as blocker closeout evidence only
and mailed decision `a7667e01d0cb4188aa0e5dc222ae7da0`.

### task290

Required before same-harness AIME comparison can be considered:

- independent review of task287 blocker artifacts at #352 exact head;
- confirmation whether the no-retained-completions blocker is sufficient
  blocker evidence or needs corrections;
- confirmation no export, endpoint, AIME/task243 eval, additional training,
  task255 reuse, 30B, or 8-GPU was used.

Current state: task290 is merged via PR #353 from worker_1 branch
`origin/intern_nemotron_worker_1/task290_qwen_aime_v11_task287_blocker_review_s1`
at exact head `daad63efe77f19b8d56c62eca9d9f9331efd6e22`. It merged at
`2026-06-02T07:52:08Z` as
`a372dcd7cd866dc02951f4f1c86eaf05a4c885b4`, and lead approval comment
`4599915303` approved it as read-only blocker review docs/evidence only.

### task291

Required before same-harness AIME comparison can be considered:

- bounded one-GPU Qwen3-4B no-export/no-endpoint route unblock or precise
  blocker for the task285 iter2 checkpoint;
- retained non-AIME canary artifacts if route succeeds:
  `canary_summary.json`, `canary_results.jsonl`, and
  `canary_full_completions.jsonl`;
- independent review and lead processing before any AIME/task243 release.

Current state: task291 is active on worker_2 branch
`origin/intern_nemotron_worker_2/task291_qwen_aime_v11_no_export_canary_route_unblock_s1`
at fetched head `ec099d2e523064640c676e2f682e54f44ccd6098`; lead
request-changes comment `4600040776` records earlier head
`4dffb40caea801503b8c39241f9afbe321887760` with read-only observed
no-export canary blockers and no retained completions. No task291 PR or
official report is visible in this refresh. Its task docs scope one-GPU
Qwen3-4B local route repair or precise blocker only, with no training, export,
endpoint, AIME/task243 eval, task255 reuse, 30B, or 8-GPU.

### task280

Required before any bounded nonzero-LR smoke release:

- no-run plan for a minimal Qwen3-4B SFT smoke using task276 packed root;
- exact LR, max train steps, global and micro batch, sequence length, output
  root, checkpoint naming, logs, and stop criteria;
- fail-closed proof that AIME2025 prompts/labels are not trainable rows;
- explicit task255 non-reuse and shared-path non-overwrite policy.

Current state: #346 is merged plan-only HOLD at merge commit
`7ba65549500e9ca70fc560ed919d6bfa61f088b2`. Its bounded-smoke planning role is
superseded by #350/task285 smoke evidence; future training remains held.

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
  for task283 no-training preflight and task285 bounded smoke only.
- task276/task277 carry accepted sparse-split risk: valid has one packed row and
  test has zero rows. This is not broad validation readiness or training
  clearance.
- task278 #347 remains historical blocker evidence for the local route. It is
  superseded for current runtime gating by task283 #349 no-training preflight
  PASS, but it remains useful context for why runtime remediation was needed.
- task279 approved #347 current head as blocker/preflight evidence only, not as
  a runtime pass or smoke release.
- task283 #349 is merged no-training preflight PASS. It does not authorize
  training, checkpoint save, export, endpoint, live canary, AIME/task243 eval,
  promotion, 30B, or 8-GPU.
- task285 #350 is merged bounded Qwen3-4B smoke evidence only. The post-train
  built-in eval/SIGTERM `RC=1` prevents any clean end-to-end train/eval pass or
  quality claim.
- task286 approved #350 as bounded smoke evidence only and only for a
  separately authorized non-AIME canary/completion-retention gate.
- #352/task287 is the merged official non-AIME canary blocker record. It passed
  checkpoint load proof but retained no completions and has no accepted canary
  pass. task288 and merged #353/task290 approve blocker closeout as evidence
  only.
- #354/task291 is the merged route-unblock pass for bounded one-GPU Qwen3-4B
  no-export/no-endpoint local generation with retained synthetic non-AIME
  completions. #355/task292 independently approved that route pass.
- #357/task294 is the merged independent AIME gate review with decision
  `APPROVE_AIME_GATE_PASS_WITH_RESIDUAL`.
- #356/task293 is the merged corrected AIME2025 metric report for task285 iter2:
  FT `12/30 = 0.4` versus accepted base `11/30 = 0.36666666666666664`.
  This is an eval-metric pass with accepted residual only.
- task280 #346 and task281 #345 are merged planning records only; task285
  supplies the bounded smoke evidence but does not release AIME/task243.
- task263 is visible at `4af57e0e61703a063c1ef42def44119a7eea5cf9`, but it has
  no PR and still records the older local runtime blocker. Coordinator Session
  40 supersedes that blocker for no-training Bridge import/preflight proof, but
  does not provide nonzero-LR training evidence or a future candidate artifact.
- task264 static canary/retention evidence from #335 is merged into main at
  `98e8aad39af9e705feed581e0ff9f8814073e2d8`; #352/task287 is now the
  merged non-AIME canary blocker record for the task285 checkpoint, with no
  retained completions.
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
| V11 data/packing ready | PACKED DATA EVIDENCE PRESENT via #336/#344 and used by #349/#350 |
| V11 base-load/import ready | TASK283 #349 NO-TRAINING PREFLIGHT PASS plus task285 Bridge import proof |
| V11 non-AIME route ready | ROUTE PASS PRESENT: #354/task291 is merged route-pass evidence and #355/task292 is merged independent route review |
| Bounded Qwen3-4B pilot allowed | SMOKE EVIDENCE PRESENT ONLY via #350/#286; no clean train/eval pass |
| Same-harness AIME metric | PASS_EVAL_METRIC_WITH_RESIDUAL: #356/task293 is merged and reports FT `12/30 = 0.4` versus base `11/30 = 0.36666666666666664`; #357/task294 approved with residual |
| Promotion, export, endpoint, or 30B/8-GPU | NO-GO/HOLD |

No release stage should move past HOLD until lead explicitly releases the
requested action.
