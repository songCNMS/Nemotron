# task312 Qwen all-SFT independent review runbook report

<!-- METADATA:STATUS=HoldWaitingUpstreamEvidence,ASSIGNEE=intern_nemotron_worker_4,SESSION=80 -->

## Decision

Decision: `REQUEST_CHANGES_HOLD_WAITING_UPSTREAM_EVIDENCE`.

This is a current-evidence HOLD snapshot, not a final all-SFT closeout. Lead
subsequently clarified task312 provenance: branch base/current main is
`172cd0e7ceaba8ad2b412d1145441dbb4c5fd122`, while the unchanged product-code
baseline is `ecb14173a820df377270273b9f7d9d92cb5076d2`.

I cannot approve all-SFT closeout or any downstream gate from the currently
visible evidence. At review time, task308, task309, and task311 have
acceptance-only worker branches with no substantive reports or artifact roots,
and task310 has no visible worker branch or training evidence. The safe gate
state is HOLD: no promotion, export, endpoint, benchmark conclusion, further
scale decision, or merge authorization follows from this review.

## Reviewed Refs

- Lead docs branch:
  `origin/intern_nemotron_lead/session1-recovery-task-docs` currently fetched
  at `9f838e94`; task312 baseline reconciliation is recorded by lead commit
  `5f4167dc`.
- Current `origin/main` used for task312 branch:
  `172cd0e7ceaba8ad2b412d1145441dbb4c5fd122`.
- Product-code baseline:
  `ecb14173a820df377270273b9f7d9d92cb5076d2`.
- task308 branch:
  `origin/intern_nemotron_worker_1/task308_qwen_all_sft_pipeline_inventory_audit_s1`
  at `348cba44c02043cd6310a36ec722a68278288db2`.
- task309 branch:
  `origin/intern_nemotron_worker_2/task309_qwen_all_sft_packed_data_contract_s1`
  at `d054925b1792a5365738247eeb8bdec462e1e6c6`.
- task310 evidence: no remote worker branch or PR found; only task-creation
  docs are present on `origin/main` commit `172cd0e7`.
- task311 branch:
  `origin/intern_nemotron_worker_3/task311_qwen_all_sft_benchmark_eval_s1`
  at `dd59d5448c44ba9d04facd2af2ddc4a02b54f899`.
- PR search: no task308/task309/task310/task311 PRs returned by `gh pr list`
  at review time.

## Commands And Checks

Static review commands used:

- `git fetch origin main intern_nemotron_lead/session1-recovery-task-docs`
- `git ls-remote --heads origin '*task308*' '*task309*' '*task310*' '*task311*'`
- `git fetch origin intern_nemotron_worker_1/task308_qwen_all_sft_pipeline_inventory_audit_s1 intern_nemotron_worker_2/task309_qwen_all_sft_packed_data_contract_s1`
- `git fetch origin intern_nemotron_worker_3/task311_qwen_all_sft_benchmark_eval_s1`
- `gh pr list --state all --search 'task308 OR task309 OR task310 OR task311' --limit 100`
- `gh pr list --state all --search task308|task309|task310|task311 --limit 20`
- `git ls-tree` and `git show` against lead docs and upstream worker refs.
- `git diff --name-status` and `git diff --check` for:
  - `origin/main...origin/intern_nemotron_worker_1/task308_qwen_all_sft_pipeline_inventory_audit_s1`
  - `origin/main...origin/intern_nemotron_worker_2/task309_qwen_all_sft_packed_data_contract_s1`
  - `origin/main...origin/intern_nemotron_worker_3/task311_qwen_all_sft_benchmark_eval_s1`
- Local output-root search under:
  - `/work-agents/intern_nemotron_worker_1/outputs`
  - `/work-agents/intern_nemotron_worker_2/outputs`
  - `/work-agents/intern_nemotron_worker_3/outputs`
  - `/work-agents/intern_nemotron_worker_5/outputs`
  - `/root`

No training, packing, eval, export, endpoint launch, promotion, task255 reuse,
AIME2025 train-data use, shared deletion, worker-branch rewrite, product-code
edit, merge, or main push was performed.

## Per-Task Review Matrix

| Task | Exact visible ref | Evidence state | Decision |
|---|---|---|---|
| task308 pipeline/data inventory | `348cba44c02043cd6310a36ec722a68278288db2` | Acceptance-only branch. Diff contains worker_1 status plus task308 README/history/task_knowledge only. Missing `all_sft_pipeline_inventory_audit_report.md`, source inventory tables, commands/env, checksums, decontam/exclusion proof, and task309 input recommendation. | `REQUEST_CHANGES` |
| task309 packed-data contract | `d054925b1792a5365738247eeb8bdec462e1e6c6` | Acceptance-only branch. Diff contains worker_2 status plus task309 README/history/task_knowledge only. Missing packed root, split manifest, source inventory, parity report, checksum manifest, Qwen tokenizer/chat-template proof, decontam proof, and task310 go/no-go. | `REQUEST_CHANGES` |
| task310 30B all-SFT training | `origin/main` `172cd0e7ceaba8ad2b412d1145441dbb4c5fd122` task-creation docs only | No worker branch, PR, report, output root, command/env, resource proof, training log, LR/loss/validation, checkpoint, or checksum evidence visible. Training should remain blocked until task308/task309 pass and task310 provides an exact checkpoint handoff. | `BLOCK_PRETRAINING_GATE` |
| task311 canary/benchmark eval | `dd59d5448c44ba9d04facd2af2ddc4a02b54f899` | Acceptance-only branch. Diff contains worker_3 status plus task311 README/history/task_knowledge only. Missing checkpoint-load canary report, corrected Qwen benchmark report, M1 benchmark availability report, same-harness base-vs-FT artifacts, completions, parser diagnostics, checksums, and unavailable-row table. | `REQUEST_CHANGES` / eval HOLD |

All visible upstream branch diffs pass `git diff --check`.

## Artifact And Checksum Review

No substantive task308-task311 artifact roots were visible under the checked
local roots. Therefore there are no reviewable upstream checksums, row counts,
token counts, supervised-token counts, shard counts, loss curves, checkpoint
manifests, canary outputs, benchmark summaries, completions, parser diagnostics,
or checksum manifests for task312 to approve.

This is not an artifact-integrity failure by itself; it is missing upstream
evidence. The next review should require exact worker branches/PRs, artifact
roots, and checksum manifests before any approval.

## Protocol And Metrics Review

Reviewable metrics from the current all-SFT attempt: none.

Background metrics from prior accepted evidence remain context only:

- task300 accepted 30B base AIME2025: `15/30 = 0.5`.
- task306/task307 fail closeout for task301 FT: `14/30 =
  0.4666666666666667`, below base.

No new all-SFT packed-data metrics, training metrics, checkpoint metrics,
non-AIME canary metrics, or benchmark base-vs-FT metrics are currently
available.

Same-harness protocol proof is also absent for this all-SFT attempt because:

- task308 has not supplied final trainable-source inventory/exclusion proof.
- task309 has not supplied a packed-data contract.
- task310 has not supplied a checkpoint handoff.
- task311 has not supplied canary or benchmark artifacts.

## Unavailable Benchmark Rows

The benchmark surface is unavailable, not partially scored.

| Benchmark group | Current availability | Blocker |
|---|---|---|
| MMLU-Pro | unavailable | No task310 checkpoint handoff, no task311 canary, no same-harness base/FT artifacts. |
| AIME2025 | unavailable for all-SFT comparison | No task310 checkpoint handoff, no task311 corrected eval artifacts. AIME2025 remains held-out eval/decontam only and must not become train data. |
| HMMT | unavailable | No task310 checkpoint handoff, no task311 same-harness artifacts. |
| M1 launcher-available basket | unavailable / not enumerated | Missing task311 `all_sft_m1_benchmark_availability_report.md`; unavailable rows are not yet classified by launcher/model route/dependency/data/resource/protocol blocker. |

Task311 must enumerate every unavailable benchmark row with exact blocker before
an all-SFT benchmark closeout can be approved.

## Boundary Review

No forbidden action was observed in the visible upstream evidence, but the
evidence is acceptance-only. The currently visible docs acknowledge the intended
boundaries:

- no AIME2025 training prompts or labels;
- no task255 reuse;
- no shared deletion;
- no product-code edits;
- no direct main push or merge;
- no promotion/export/endpoint claim.

Because substantive artifacts are missing, these remain branch/report boundary
statements rather than artifact-level proof.

## Required Changes Before Approval

Task308 must provide:

- final all-eligible-SFT source inventory;
- exact source paths/revisions/splits/counts;
- exclusion/decontam proof for held-out/eval/decontam/AIME/task255;
- commands/env and checksum/source manifests;
- concrete task309 input plan or exact blocker.

Task309 must provide:

- task308-derived all-eligible packed root;
- split/source manifests, row/token/supervised-token/shard/source counts;
- intended-vs-exposed parity report;
- Qwen3-30B tokenizer/chat-template contract proof;
- checksum manifest and commands/env;
- explicit task310 go/no-go.

Task310 must provide:

- accepted upstream gate refs;
- exact launch command/env/resource/parallelism/config;
- training logs with LR/loss/validation;
- usable checkpoint path and checksum manifests;
- task311 checkpoint handoff, or an exact fail-closed blocker.

Task311 must provide:

- checkpoint-load and non-AIME canary proof;
- corrected same-harness base-vs-FT artifacts for runnable benchmarks;
- completions/parser diagnostics/results/summaries/checksums;
- explicit unavailable benchmark row table and blockers;
- boundary proof for eval-only export/endpoint if used.

## Runbook Recommendation

Recommended lead wording:

`REQUEST_CHANGES/HOLD for task312 at current evidence state. task308, task309, and task311 are acceptance-only branches and task310 has no visible worker branch/report/artifacts. No data, packing, training, checkpoint, canary, or benchmark evidence is currently sufficient for all-SFT closeout. Keep all-SFT gate blocked: no promotion, export, endpoint, benchmark comparison, further scale decision, training continuation, or merge authorization until task308-task311 provide exact reports, artifact roots, commands/env, checksums, metrics, unavailable benchmark rows, and boundary proof.`

Residual risks:

- Upstream branches may advance after this review; task312 must refresh exact
  heads before any final approval.
- No mailbox-only upstream closeout evidence was independently available in the
  repo/PR/artifact surface reviewed here.
- Current lead docs now distinguish branch base/current main `172cd0e7` from
  unchanged product-code baseline `ecb14173`; upstream closeouts should keep the
  same distinction.
