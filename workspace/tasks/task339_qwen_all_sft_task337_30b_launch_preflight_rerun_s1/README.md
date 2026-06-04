# task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1 - Rerun 30B launch preflight with task337 runtime route

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_2,SESSION=88 -->

## Background

task335/#398 established that the all-SFT 30B launch route remained fail-closed
because `megatron.bridge.recipes.qwen.qwen3_moe` could not import without
`megatron.energon`. task337/#400 is now merged as no-training runtime import
remediation evidence: the exact prior failing Qwen3 MoE Bridge recipe import and
symbol probe pass when the task337 runtime target is prepended on `PYTHONPATH`.

The user requested the all-SFT Qwen pipeline, but training is still not
released. The next gate is a task335-equivalent no-training launch preflight
rerun from current main using the accepted task333 all-SFT packed contract and
the approved task337 runtime route.

## Goal

Produce a no-training Qwen3-30B all-SFT launch/config/import/resource preflight
for current `origin/main` after #400. Return one of:

- `PASS_LAUNCH_PREFLIGHT_WITH_TASK337_RUNTIME`: current-main 30B launch contract
  is concrete, the Qwen3 MoE Bridge import/config route passes with the approved
  runtime target, train-only data/validation/exit/resource handoff is safe, and
  a later bounded training task can be assigned by lead gate.
- `REQUEST_CHANGES`: the route is plausible but missing exact command/env,
  config, resource, validation, checkpoint, timeout, rc, data, or artifact
  evidence.
- `BLOCK_LAUNCH_PREFLIGHT`: a runtime/resource/config/data gate still fails or
  would require unauthorized training/eval/shared mutation/downgrade/product-code
  edits.

## Inputs

- Current main after #400:
  `f083c9566a9f0775c27ae49f16b8b898edfc8d11`.
- Target model path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Accepted task333 artifact root:
  `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z`.
- Accepted task333 packed root:
  `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z/packed_qwen_combined_contract`.
- task337 artifact root:
  `/work-agents/intern_nemotron_worker_2/outputs/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z`.
- Approved task337 runtime target:
  `/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site`.
- Expected runtime `PYTHONPATH` pattern:
  `/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site:<task339_remote_repo>/src`.
- task337 report sha256:
  `441bd4b3c46d923f880fe3ce55298bc810e03e730819b16405b8b3b5a995cd49`.

## Required Checks

- First, send/record #400 merge closeout if it has not already been delivered:
  mergedAt `2026-06-04T11:11:08Z`, merge commit
  `f083c9566a9f0775c27ae49f16b8b898edfc8d11`, merged head
  `fb6ba0e75c0d3dc4ec3ad47e3d6f27bbecf3e091`.
- Sync current `origin/main` to a new task-owned `/root` run directory on
  `NemTron` before remote debug, following project rules.
- Reuse the approved task337 runtime target exactly, or recreate an equivalent
  task-owned runtime remediation with fresh checksums. If recreating, report
  package sources, versions, install target, checksums, and why reuse was not
  possible.
- Validate the runtime target and task337 artifact evidence needed for this
  handoff: artifact checksum manifest, runtime inventory, final import marker,
  and qwen3_moe symbol marker.
- Run a task335-equivalent no-training preflight using current main and the
  task337 runtime route. Required surfaces:
  - Qwen3 MoE Bridge import/config surface for the 30B A3B instruct path.
  - 30B model path and tokenizer/chat-template assumptions.
  - task333 packed root resolution and train-only view/split contract.
  - proof no AIME2025 prompt/label train rows are introduced.
  - validation disposition and fail-closed exit/timeout route, preserving the
    task310 validation-hang lesson.
  - resource contract: host/GPU count, GPU type, tensor/pipeline/context/data
    parallelism, precision, sequence length, global batch, checkpoint policy,
    output root, timeout policy, rc policy, teardown policy.
  - residual classification for `nvidia-resiliency-ext` and the
    `multi_storage_client` diagnostic import name.
  - exact later launch command/env handoff if and only if no-training gates pass.
- Produce artifacts under a task-owned local output root with remote run path,
  logs, manifests, checksums, and command/env transcript.

## Boundaries

- No training, optimizer steps, benchmark eval, AIME/task243 eval, export,
  endpoint, promotion, task255 reuse, AIME2025 train rows, shared deletion,
  main push, merge, or self-merge.
- Do not delete or mutate files under `/mnt/cephfs/data/processing/lei.song` or
  any shared model/data roots.
- Do not silently downgrade to 4B or switch Qwen checkpoint paths.
- Do not mutate task333/task337 artifacts except by reading/copying into a
  task-owned output route if needed for no-training preflight.
- If product-code edits, container credentials, missing runtime packages,
  unavailable GPUs, or destructive data operation is required, stop and report
  `BLOCK_LAUNCH_PREFLIGHT`.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_2/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1`.
- Report:
  `workspace/tasks/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/task337_runtime_route_30b_launch_preflight_report.md`.
- Task-owned output root with logs, configs, manifests, checksums, remote path,
  and command/env transcript.
- Mailbox closeout with branch/head/PR or blocker, commands/env, remote paths,
  artifact paths, pass/fail disposition, residuals, and exact next-task release
  recommendation.

## Assignment

- Team: `nemotron`.
- Team lead: `intern_nemotron_lead`.
- Worker: `intern_nemotron_worker_2`.
- Base: current `origin/main`
  `f083c9566a9f0775c27ae49f16b8b898edfc8d11`.
- Gate state: task310/all-SFT 30B launch/training/eval/export/endpoint/
  promotion remain HOLD pending this no-training preflight and later lead gate.

## Acceptance

- Worker branch:
  `origin/intern_nemotron_worker_2/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1`.
- Acceptance head observed:
  `d07f348eb2efef359e3aaf9fa0c2f725b57bac00`.
- Base: `origin/main`
  `f083c9566a9f0775c27ae49f16b8b898edfc8d11`.
- No PR visible yet.
- Formal mailbox acceptance is still pending; worker_2 pane indicates acceptance
  commit only updates task339 docs/status and no product code or shared
  artifacts were touched.
