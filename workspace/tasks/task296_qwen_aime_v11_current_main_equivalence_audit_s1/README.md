# task296_qwen_aime_v11_current_main_equivalence_audit_s1 - current-main equivalence audit

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_1,SESSION=75 -->

## Background

The user requested commit/merge of the outstanding PR and then a full
data/training/evaluation pipeline based on current code. Coordinator PR #312
was merged after the V11 runbook closeout:

- post-#351 main: `5d8b8d850d26e785332f8b707c772d99881a1b5d`
- current main after #312: `2d84ec75960fb51ba9091427638b00083625e137`
- #312 mergedAt: `2026-06-02T12:13:44Z`
- #312 merged head: `c7ada6134f63c88d1efcbf993452186d14ae24f3`

Existing merged V11 evidence:

- task285/#350 bounded Qwen3-4B SFT smoke from source head
  `c53095a639f0ccf8ce34afcec1bdf302cf45add6`
- task293/#356 corrected AIME2025 eval from run source head
  `87de0a97e6c0406a4b67520faab6b11d91d9131e`
- task293 metric: FT `12/30 = 0.4` versus accepted task247 Qwen3-4B base
  `11/30 = 0.36666666666666664`
- task294/#357 independent review decision:
  `APPROVE_AIME_GATE_PASS_WITH_RESIDUAL`
- task295/#351 runbook/provenance closeout merged at
  `5d8b8d850d26e785332f8b707c772d99881a1b5d`

Lead preliminary read-only observation: #312 appears coordinator-docs-only, but
this needs worker-owned audit evidence before lead can answer that no fresh
current-main rerun is needed.

## Goal

Determine whether path A is valid:

`A_PROVED_NO_RERUN`: task285/task293 artifacts are product-code-equivalent to
current main `2d84ec75960fb51ba9091427638b00083625e137`, so no new
data/training/non-AIME/AIME run is needed for the user's current-code request.

If this cannot be proven, return:

`B_REQUIRED_RERUN`: lead must launch a fresh current-main bounded pipeline.

## Scope

Read-only audit only. Use git/GitHub/artifact-manifest inspection. Do not run
training, canary, AIME eval, export, endpoint, promotion, 30B, or 8-GPU.

Required checks:

- Fetch current origin state and verify `origin/main` is exactly
  `2d84ec75960fb51ba9091427638b00083625e137`.
- Verify #312 merge metadata: mergedAt, mergeCommit, merged head, and file list.
- Compare #312's merge delta:
  `git diff --name-status 5d8b8d850d26e785332f8b707c772d99881a1b5d..2d84ec75960fb51ba9091427638b00083625e137`
  and classify every changed file.
- Confirm no #312 changed file is under product, data-prep, training, eval,
  harness, source, test, model, recipe, or task285/task293 artifact/script
  paths.
- Compare task285 evidence source head
  `c53095a639f0ccf8ce34afcec1bdf302cf45add6` to current main for relevant
  training/data product paths, including at least `src/`, `recipes/`, `tests/`,
  `workspace/tasks/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/`, and any
  task276/task283/task285 script/config paths referenced in the task285 report.
- Compare task293 run source head
  `87de0a97e6c0406a4b67520faab6b11d91d9131e` to current main for relevant eval
  paths, including at least `src/`, `recipes/`, `tests/`,
  `workspace/tasks/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/`,
  and the task291/task293 route/evaluator scripts referenced in the report.
- Explicitly verify whether
  `workspace/tasks/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_no_export_aime_eval.py`
  changed after task293 run source head.
- Reconfirm the task285 and task293 artifact roots and key checksums from the
  merged reports; read-only checksum recomputation is allowed if local artifacts
  exist.
- Carry residuals forward: task285 post-train built-in eval RC=1, task276 sparse
  valid/test split, task292 detokenized fallback residual, task293
  `sampling_exact_parameter_match=false`.

## Boundaries

- Do not train, run nonzero-LR smoke, run live canary, run AIME/task243 eval,
  export, convert, launch an endpoint, promote, reuse task255, use AIME2025
  prompts/labels as train data, delete shared files, push main, merge, run 30B,
  or use 8 GPUs.
- Do not mutate task285/task293 artifacts.
- Do not claim promotion or release clearance.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_1/task296_qwen_aime_v11_current_main_equivalence_audit_s1`
- PR or branch report containing
  `workspace/tasks/task296_qwen_aime_v11_current_main_equivalence_audit_s1/current_main_equivalence_audit_report.md`
- Mailbox report to lead with:
  - branch/head/PR or blocker;
  - exact commands run;
  - #312 merge metadata and changed-file classification;
  - task285/task293 source-to-current comparisons;
  - artifact roots and checksums checked;
  - decision `A_PROVED_NO_RERUN`, `REQUEST_CHANGES`, or `B_REQUIRED_RERUN`;
  - residual risks and no-clearance boundary statement.

## Acceptance Criteria

- APPROVE: current main differs from accepted V11 evidence only by coordinator
  docs/provenance surfaces, relevant task285/task293 code paths are unchanged or
  proven artifact-equivalent, artifacts/checksums remain consistent, and all
  residuals/boundaries are visible.
- REQUEST-CHANGES: report omits required comparisons, commands, artifact
  metadata, or residuals.
- BLOCK: product/training/eval/data code changed materially, artifact
  equivalence cannot be proven, or any forbidden boundary would be required.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_1`
- Related PRs: #312, #350, #351, #356, #357
- Related tasks: task247, task276, task277, task285, task291, task292, task293,
  task294, task295
