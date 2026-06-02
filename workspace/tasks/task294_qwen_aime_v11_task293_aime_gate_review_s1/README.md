# task294_qwen_aime_v11_task293_aime_gate_review_s1 - task293 AIME gate review

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_4,SESSION=76 -->

## Background

task293 produced read-only final artifacts for the V11 task285 Qwen3-4B iter2
checkpoint corrected AIME2025 FT-vs-base comparison.

Lead-observed task293 artifact summary:

- task293 branch head:
  `87de0a97e6c0406a4b67520faab6b11d91d9131e`
- local artifact root:
  `/work-agents/intern_nemotron_worker_3/outputs/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z`
- remote artifact root:
  `/root/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z/artifacts`
- candidate checkpoint:
  `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3/iter_0000002`
- accepted base comparator: task247 Qwen3-4B corrected AIME2025
  `11/30 = 0.36666666666666664`
- task293 artifact metric: FT `12/30 = 0.4`, delta `+1/30`,
  disposition `PASS`

This metric pass does not authorize export, endpoint, promotion, 30B, or 8-GPU.
Worker_3 official closeout/PR may still be pending; review the exact artifacts
and state whether the evidence is sufficient for lead gate wording.

## Goal

Independently review the exact task293 artifacts and same-harness proof, then
return one decision:

- `APPROVE_AIME_GATE_PASS_WITH_RESIDUAL`
- `REQUEST_CHANGES`
- `BLOCK_REVIEW`

## Evidence To Review

- `aime_eval/summary.json`
- `aime_eval/results.jsonl`
- `aime_eval/full_completions.jsonl`
- `manifests/aime_prompt_manifest.json`
- `manifests/checkpoint_load_manifest.json`
- `manifests/command_env_manifest.json`
- `manifests/checksum_manifest.json`
- task293 log:
  `/work-agents/intern_nemotron_worker_3/outputs/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z/logs/remote_no_export_aime_eval.log`

Lead-observed checksums from task293 manifest:

- `aime_eval/full_completions.jsonl`:
  `5cb1e11ab8d331127c7c12f2cd8c04d83d2e6bd93445a5ebffc62363e2a818b4`
- `aime_eval/results.jsonl`:
  `4cbc2a9543a658df6a3e18e3128c5a5c9a173f9a575372095cfcbe5d6232aca5`
- `aime_eval/summary.json`:
  `64a378ca54534ec426b92a7b6bc436edb4fddd2ea1ba831f61afeed4e1ad39b7`
- `manifests/aime_prompt_manifest.json`:
  `93146086fcc2214fc3c866354e23358d320377caddb6d2b5a2bd58954e85b919`
- `manifests/checkpoint_load_manifest.json`:
  `243044f2e548e0c8b1b539e9c11fee17a39b4d45898e1a6601382716e4d90c74`
- `manifests/command_env_manifest.json`:
  `5b128b5cc84159b8603b07fc92475ebc768152b7c0ea0fae0897c6635a502ccf`

## Scope

- Read-only review only.
- Verify artifact row counts, checksums, summary metrics, accepted base reuse,
  corrected parser/normalizer proof, prompt/cache/denominator/max-token proof,
  command/env boundaries, and no forbidden route.
- Pay special attention to the residual protocol issue:
  `sampling_exact_parameter_match=false`. Decide whether the artifact's
  deterministic greedy semantic-match explanation is acceptable for the hard
  FT >= base gate, or whether lead must request changes/HOLD.
- If worker_3 official closeout/PR is missing at review time, state whether that
  blocks approval or is a closeout dependency after artifact review.

## Boundaries

- Do not edit code.
- Do not run training, optimizer steps, live eval, AIME re-eval, export,
  endpoint launch, promotion, task255 reuse, AIME2025 train data, shared
  deletion, 30B, or 8-GPU.
- Do not merge or push main.
- Do not rewrite worker_3 branches or artifacts.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_4/task294_qwen_aime_v11_task293_aime_gate_review_s1`.
- PR only if docs/status/review report files change.
- Official mailbox report with:
  - exact task293 head and artifact roots reviewed;
  - commands/checks run;
  - checksum and row-count verification;
  - metric verification: FT correct/total/score versus base;
  - same-harness proof assessment;
  - decision: `APPROVE_AIME_GATE_PASS_WITH_RESIDUAL`, `REQUEST_CHANGES`, or
    `BLOCK_REVIEW`;
  - residual risks and required follow-up;
  - explicit boundary confirmation.

## Acceptance Criteria

- APPROVE: artifacts consistently prove corrected AIME2025 FT `>= 11/30`, with
  complete rows/checksums/protocol evidence and no boundary violation. Residual
  sampling semantic-match risk must be explicitly accepted or bounded.
- REQUEST_CHANGES: evidence likely passes but worker_3 must clarify protocol,
  closeout, artifacts, checksums, row counts, or boundary statements.
- BLOCK_REVIEW: evidence is inconsistent, below base, violates boundaries, or
  cannot prove same corrected evaluator/protocol.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Related tasks: task247, task285, task291, task292, task293
- Gate: this review may support an AIME metric pass only. It does not authorize
  export, endpoint, promotion, 30B, or 8-GPU.
