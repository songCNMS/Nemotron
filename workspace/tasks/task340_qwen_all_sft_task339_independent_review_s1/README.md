# task340_qwen_all_sft_task339_independent_review_s1 - Review task339 launch preflight rerun

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_4,SESSION=89 -->

## Background

task339/#402 reports `PASS_LAUNCH_PREFLIGHT_WITH_TASK337_RUNTIME`: a
task335-equivalent no-training Qwen3-30B all-SFT launch/config/import/resource
preflight rerun from current main after #400, using the accepted task333 packed
contract and the approved task337 runtime target.

This is still only a no-training gate. Before lead can accept #402 or assign any
later training-readiness/launch task, the report and artifacts need independent
read-only review.

## Review Target

- PR: #402 `https://github.com/songCNMS/Nemotron/pull/402`.
- Exact head: `0a064f3517e6c10acfaec2c0915e24bc1434ceb1`.
- Base: `main`.
- Observed PR state: `OPEN`, non-draft, `CLEAN`/`MERGEABLE`.
- Report:
  `workspace/tasks/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/task337_runtime_route_30b_launch_preflight_report.md`.
- Report sha256:
  `b7115e42444defdc9e0f44ad15f1e622ad476679148e285da8836a6c8b74969e`.
- Artifact root:
  `/work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z`.
- Remote root:
  `/root/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z`.
- task337 runtime target:
  `/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site`.

## Goal

Return one of:

- `APPROVE_TASK339_NO_TRAINING_PREFLIGHT`: #402 accurately documents a
  no-training 30B launch/config/import/resource preflight PASS. This does not
  release training by itself.
- `REQUEST_CHANGES`: report/artifacts are incomplete, inconsistent, or missing
  evidence required to accept the PASS.
- `BLOCK_REVIEW`: evidence is unsafe, ambiguous, or cannot be reviewed without
  unauthorized runtime/training action.

## Required Checks

- PR metadata: exact #402 head
  `0a064f3517e6c10acfaec2c0915e24bc1434ceb1`, base `main`, non-draft,
  clean/mergeable, no material head drift.
- Diff scope: worker_2 status plus task339 README/history/task_knowledge,
  task-local helper, and task339 report only; no product/source code changes.
- `git diff --check origin/main...origin/intern_nemotron_worker_2/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1`.
- Confirm report sha256 equals
  `b7115e42444defdc9e0f44ad15f1e622ad476679148e285da8836a6c8b74969e`.
- Helper compile:
  `python3 -m py_compile workspace/tasks/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/build_task339_30b_launch_preflight_rerun.py`.
- Artifact checksum validation from the task339 run root:
  `sha256sum -c manifests/artifact_checksums.sha256`.
- Train-only shard checksum validation:
  `sha256sum -c manifests/train_only_shard_checksums.sha256`.
- Confirm final summary disposition
  `PASS_LAUNCH_PREFLIGHT_WITH_TASK337_RUNTIME`.
- Confirm remote probe marker `TASK339_REMOTE_PREFLIGHT=PASS`.
- Confirm current main synced:
  `f083c9566a9f0775c27ae49f16b8b898edfc8d11`.
- Confirm task337 runtime/report handoff:
  report sha match, task337 artifact checksums pass, runtime target exists,
  `megatron.energon` and `megatron.bridge.recipes.qwen.qwen3_moe` import pass.
- Confirm task333 data contract: source root read-only, train-only view has
  84 train shards, 0 valid, 0 test; 78,168 rows; 300,046,415 input tokens;
  33,477,337 supervised tokens; no new AIME2025 prompt/label train rows.
- Confirm 30B model/tokenizer contract: model path exists, `model_type=qwen3_moe`,
  architecture `Qwen3MoeForCausalLM`, tokenizer chat template present,
  trust_remote_code false for probing.
- Confirm Qwen3-30B Bridge config surface passes without model construction,
  weight load, training loop, or optimizer step; record TP/PP/EP and checkpoint
  placeholder status.
- Confirm validation fail-closed route: train-only root has no valid shards,
  expected `do_validation=false`, and any later validation phase must block.
- Confirm resource contract: 8 H200 GPUs visible with no active utilization in
  the probe.
- Classify residuals: missing `nvidia_resiliency_ext`, diagnostic
  `multi_storage_client` import name failure, `multistorageclient` pass from
  task337 runtime target. State whether these block training-readiness even if
  they do not block the no-training preflight.
- Confirm boundaries: no optimizer/training/eval/export/endpoint/promotion/
  task310 release/task255/AIME2025 train rows/shared deletion/main push/merge/
  self-merge.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_4/task340_qwen_all_sft_task339_independent_review_s1`.
- Report:
  `workspace/tasks/task340_qwen_all_sft_task339_independent_review_s1/task339_independent_review_report.md`.
- Mailbox closeout with branch/head/PR, commands run, pass/fail findings,
  residuals, and exact decision for #402.

## Boundaries

- Read-only review only.
- Do not modify task339 artifacts or worker_2 branch.
- Do not run training, optimizer steps, benchmark eval, AIME/task243 eval,
  export, endpoint, promotion, task310, task255, AIME2025 train rows, shared
  deletion/mutation, main push, merge, or self-merge.
- If more runtime action appears needed, report the exact follow-up task; do not
  perform it.

## Assignment

- Team: `nemotron`.
- Team lead: `intern_nemotron_lead`.
- Worker: `intern_nemotron_worker_4`.
- Base: current `origin/main`
  `f083c9566a9f0775c27ae49f16b8b898edfc8d11`.
- Gate state: #402/task339 and task310 remain HOLD pending this review.

## Acceptance

- Worker_4 acceptance mailbox:
  `intern_nemotron_worker_4-task340-accept-20260604T1142Z`.
- Worker branch:
  `origin/intern_nemotron_worker_4/task340_qwen_all_sft_task339_independent_review_s1`.
- Acceptance head:
  `15ee7c871fc02f944ca723aef44590d9e8971fdb`.
- Base: `origin/main`
  `f083c9566a9f0775c27ae49f16b8b898edfc8d11`.
- Lead docs imported from:
  `origin/intern_nemotron_lead/session1-recovery-task-docs`
  `0270526a5197eeb441ac43b5cec62ab46d122d8b`.
- Review target reconfirmed: #402 exact head
  `0a064f3517e6c10acfaec2c0915e24bc1434ceb1`, artifact root
  `/work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z`,
  report sha `b7115e42444defdc9e0f44ad15f1e622ad476679148e285da8836a6c8b74969e`.
- Worker_4 accepted read-only review scope and boundaries; #402/task339 and
  task310 remain HOLD pending approve/request-changes/block report.
