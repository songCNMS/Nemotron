# task341_qwen_all_sft_30b_training_readiness_checkpoint_handoff_s1 - Training readiness and checkpoint handoff

<!-- METADATA:STATUS=Blocked,ASSIGNEE=intern_nemotron_worker_2,SESSION=90 -->

## Background

task339/#402 is merged as accepted no-training 30B launch/config/import/resource
preflight evidence. It proves the Qwen3-30B all-SFT route can import/configure
under the task337 runtime target with task333 train-only data, but it deliberately
does not release task310 or any optimizer step.

The remaining pre-training blockers are explicit: `nvidia_resiliency_ext` is
missing, training launch placeholders remain unset, and the
`SUPER3_M1_PRETRAINED_CHECKPOINT` / Bridge checkpoint handoff is still a
placeholder. This task must resolve or precisely gate those items before any
training task can be assigned.

## Goal

Produce a no-optimizer training-readiness/checkpoint-handoff report that returns
one of:

- `PASS_TRAINING_READINESS_HANDOFF`: task339 launch route is ready for a later
  lead-gated bounded training task, with resolved or explicitly waived
  `nvidia_resiliency_ext`, exact checkpoint handoff, exact launch placeholders,
  and fail-closed policies.
- `REQUEST_CHANGES`: evidence is plausible but missing exact runtime,
  checkpoint, placeholder, resource, timeout, rc, or artifact proof.
- `BLOCK_TRAINING_READINESS`: a runtime/checkpoint/config/resource gate still
  fails or would require unauthorized optimizer/training/eval/shared mutation/
  product-code change.

## Inputs

- Current main after #402:
  `f16dffdef961b1a6cdb3ae23203f9ae7495b38ab`.
- task339 artifact root:
  `/work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z`.
- task339 remote root:
  `/root/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z`.
- task337 runtime target:
  `/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site`.
- task333 train-only remote root:
  `/root/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/input/packed_qwen_task333_train_only_contract`.
- Target model path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- task339 later launch contract:
  `/work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/manifests/later_launch_contract.json`.
- task339 template, not run:
  `/work-agents/intern_nemotron_worker_2/outputs/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/config/run_later_training_TEMPLATE_DO_NOT_RUN.sh`.

## Required Checks

- Sync current `origin/main` to a new task-owned `/root` run directory on
  `NemTron` before remote debug.
- Revalidate task339 artifact checksums and key pass markers. Do not mutate
  task339 artifacts.
- Determine whether `nvidia_resiliency_ext` is required by the actual later
  training entrypoint/runtime. If required, provide a task-owned remediation or
  fail closed with exact missing package/source/credential blocker. If not
  required, produce a defensible explicit waiver tied to import path, config, and
  launch command evidence.
- Verify the diagnostic `multi_storage_client` residual remains non-blocking for
  the actual launch path, or report a blocker if any import path needs the
  underscore module name.
- Identify and validate the exact 30B Bridge pretrained checkpoint handoff for
  `SUPER3_M1_PRETRAINED_CHECKPOINT`. Acceptable outcomes:
  - an existing lead-approved imported Bridge checkpoint path with manifest and
    checksums; or
  - a no-optimizer checkpoint import/preflight in a task-owned route with logs
    and checksums; or
  - `BLOCK_TRAINING_READINESS` with exact missing checkpoint/import/runtime
    blocker.
- Fill the later launch placeholders in a task-owned manifest, not by editing
  production config:
  `TASK341_TRAIN_ITERS`, `TASK341_LR`, `TASK341_MIN_LR`,
  `TASK341_LR_WARMUP_ITERS`, `TASK341_SAVE_INTERVAL`, and checkpoint path.
  Values must be concrete and justified for a bounded first all-SFT 30B run.
- Re-render the later launch command/env using task339 train-only data and the
  approved runtime route. Do not execute the training command.
- Reconfirm validation fail-closed route, rc policy, timeout policy, checkpoint
  inventory/checksum expectations, process/GPU teardown policy, and same-harness
  eval handoff.
- Produce a task-owned output root with manifests, logs, commands/env,
  checksums, and exact recommendation for the next lead task.

## Boundaries

- No optimizer steps, training loop execution, benchmark eval, AIME/task243 eval,
  export, endpoint, promotion, task255 reuse, AIME2025 train rows, shared
  deletion/mutation, main push, merge, or self-merge.
- Do not silently downgrade to 4B or switch checkpoint/model paths.
- Do not delete or mutate files under `/mnt/cephfs/data/processing/lei.song` or
  any shared model/data roots.
- If checkpoint import or runtime remediation requires system package mutation,
  shared-root mutation, unavailable credentials, product-code edits, or
  destructive data operations, stop and report `BLOCK_TRAINING_READINESS`.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_2/task341_qwen_all_sft_30b_training_readiness_checkpoint_handoff_s1`.
- Report:
  `workspace/tasks/task341_qwen_all_sft_30b_training_readiness_checkpoint_handoff_s1/training_readiness_checkpoint_handoff_report.md`.
- Task-owned artifact root with logs, manifests, checksums, remote path, rendered
  command/env, and pass/block disposition.
- Mailbox closeout with branch/head/PR or blocker, commands/env, artifact paths,
  residuals, and exact recommendation for the next task.

## Assignment

- Team: `nemotron`.
- Team lead: `intern_nemotron_lead`.
- Worker: `intern_nemotron_worker_2`.
- Base: current `origin/main`
  `f16dffdef961b1a6cdb3ae23203f9ae7495b38ab`.
- Gate state: task310/all-SFT 30B launch/training/eval/export/endpoint/
  promotion remain HOLD pending this readiness task and later lead gate.
