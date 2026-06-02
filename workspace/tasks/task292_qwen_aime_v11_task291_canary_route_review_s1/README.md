# task292_qwen_aime_v11_task291_canary_route_review_s1 - task291 canary route review

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_4,SESSION=76 -->

## Background

task291 is the bounded no-export/no-endpoint route-unblock task after
task287/#352 merged a non-AIME canary `BLOCK`. worker_2 has advanced the route
probe to current head `dfb6ca64a5479990be9d4f54defb9f294c09866f`, and lead
read-only evidence now shows a synthetic non-AIME canary pass artifact root.

This is not yet an AIME release. The evidence must be independently reviewed,
and worker_2 still needs official report/PR closeout for any final code/report
changes.

## Goal

Independently review the exact task291 branch head and artifact root, then
return `APPROVE_CANARY_ROUTE_PASS`, `REQUEST_CHANGES`, or `BLOCK_REVIEW`.

## Evidence To Review

- task291 PR:
  `https://github.com/songCNMS/Nemotron/pull/354`
- task291 branch:
  `origin/intern_nemotron_worker_2/task291_qwen_aime_v11_no_export_canary_route_unblock_s1`
- Exact PR head to review:
  `2fda1ed46da4c82712a5c22c85bf124c26c6376f`
- Evidence source head:
  `dfb6ca64a5479990be9d4f54defb9f294c09866f`
- Local artifact root:
  `/work-agents/intern_nemotron_worker_2/outputs/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/run_20260602T081136Z`
- Remote artifact root:
  `/root/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/run_20260602T081136Z`
- Candidate checkpoint:
  `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3/iter_0000002`
- Base model path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`
- Prompt YAML sha:
  `150ee11dc6e8efd3c865a8e9ed8a9ab8ce4f5ee032bed383c73a6cea34f52f1c`

Observed lead read-only metrics from `run_20260602T081136Z`:

- rc `0`
- disposition `PASS`
- `canary_pass=true`
- prompts requested `5`
- result rows `5`
- full completion rows `5`
- completions retained `5`
- exact expected-answer matches `5`
- final-answer marker count `9`
- route `direct_in_process_mcore_static_engine_no_export_no_endpoint_topk1_greedy`
- `LOAD_MEGATRON_MODEL=PASS`
- `CUDA_VISIBLE_DEVICES=0`
- command/env boundary confirmations true for Qwen3-4B only, no training,
  no AIME/task243, no AIME2025 train prompts/labels, no task255, no export, no
  endpoint, no promotion, no shared deletion, no 30B, and no 8-GPU.

Observed hashes:

- `canary_summary.json`:
  `dd855c2c32b0b7411ee1cd365311363f1d3338753560107768b684b8fb660d40`
- `canary_decision.json`:
  `c3c9964b6024e1fb137c0db66d255e773727dc8d30fde75c56834b34778c0bca`
- `canary_results.jsonl`:
  `67e6304786f5bb79fee07f5253ff4de2e449d2756aa6fd2d38762322bdad3dc7`
- `canary_full_completions.jsonl`:
  `b2768f75415abfeb268b58ba425abe41a7b169fdacbd07e9aa27422e46d7611d`
- `remote_no_export_canary_probe.log`:
  `e2044aae855a7a660968e3d2940c946ca874198bef2a04e05163c4235707f17b`

## Scope

- Read-only review only.
- Review exact #354 PR head, task291 helper-script changes, artifact paths,
  checksums, command/env, checkpoint-load manifest, prompt provenance, retained
  completion rows, and per-prompt metrics.
- Determine whether the evidence is sufficient to close task291 as an accepted
  non-AIME canary route pass, or whether worker_2 must fix/report more.
- If worker_2 has not opened an official task291 PR/report by review time,
  state whether that is a blocker or only a closeout requirement.

## Boundaries

- Do not edit code, run canary, run training, run AIME/task243 eval, export,
  launch an endpoint, promote, reuse task255, use AIME2025 train data, delete
  shared files, merge, push main, use 30B, or use 8-GPU.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_4/task292_qwen_aime_v11_task291_canary_route_review_s1`.
- PR only if docs/status/review report files change.
- Official mailbox report with:
  - exact branch/head/PR/artifact root reviewed;
  - commands/checks run;
  - checksum validation;
  - metric verification;
  - decision: `APPROVE_CANARY_ROUTE_PASS`, `REQUEST_CHANGES`, or
    `BLOCK_REVIEW`;
  - residual risks, especially detokenized fallback use on the word prompt and
    worker_2 official report/PR status;
  - explicit boundary confirmation.

## Acceptance Criteria

- APPROVE: exact task291 head and artifacts prove an allowed no-export/no-endpoint
  synthetic non-AIME canary pass with retained coherent completions, 5/5 exact
  expected-answer matches, clear command/env evidence, and no boundary violation.
- REQUEST_CHANGES: route may be valid, but report/PR, checksums, prompt
  provenance, completion retention, metric clarity, fallback semantics, or
  boundary evidence are incomplete.
- BLOCK_REVIEW: artifacts are inconsistent, imply a boundary violation, or do
  not prove the route pass.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Related tasks: task285, task287, task288, task291
- Gate: task292 approval may only allow lead to consider assigning corrected
  AIME2025 same-harness FT-vs-base eval. It does not itself authorize AIME,
  export, endpoint, promotion, 30B, or 8-GPU.
