# task244 Initial Independent Review Matrix

<!-- METADATA:SESSION=1 -->

## Scope And Inputs

This review is read-only. I did not modify product code, run training, run eval,
run implementation tests, merge, push `main`, or alter worker branches.

Base reviewed: `origin/main` at `f5a844765c5ac1a756b7f7e94d27ee466fe25a9b`.

Reviewed inputs:

| Owner | Task | Branch / PR | Head inspected | Diff scope | Decision |
| --- | --- | --- | --- | --- | --- |
| worker_1 | `task241_qwen_aime_v10_sidecar_data_s1` | branch only, no PR found | `233a0e006bbf90bfac4344374748a107d71a5952` | task/status docs only | BLOCK: not reviewable as data implementation |
| worker_2 | `task242_qwen_aime_v10_planner_smoke_s1` | branch only, no PR found | `b2d16a7300b218354debc23e22ae7faa7015fe34` | task/status docs only | BLOCK: not reviewable as planner implementation |
| worker_3 | `task243_qwen_aime2025_base_vs_ft_eval_gate_s1` | branch only, no PR found | `c02b09a6c9cba928117d89ca03fb2f073c584733` | task/status docs only | BLOCK: not reviewable as eval-gate implementation |
| worker_5 | `task245_qwen_aime_v10_artifact_runbook_verify_s1` | PR #317 | `aa071c46690c5f30614102f7bcf149c38e86d428` | task/status docs only | REQUEST_CHANGES / HOLD: runbook evidence absent |

## Evidence Baseline

Task071/task075/task076 history establishes the review bar:

- V7 corrected AIME25 result was `0.21` and passed the old AIME `>=0.20` gate,
  but still trailed the original base model.
- V8 corrected AIME25 result was `0.19666666666666666`, a real regression
  concentrated on `aime_06`, not parser noise or truncation alone.
- V9 checkpoint-root repair fixed a launch/checkpoint pathology, but targeted
  `aime_06` still failed with wrong modes `640` and `830`.
- Task076 concluded the next data step should be a focused run-length DP /
  counting-recursion V10 sidecar or weighting patch, with AIME25/HMMT/MATH held
  out as decontamination/eval material only.

## Review Matrix

| Surface | Required V10 evidence | Current finding | Risk |
| --- | --- | --- | --- |
| Data sidecar | Distinct V10 row selection targeting run-length DP, counting recurrences, constrained binary strings, no-consecutive/run-length constraints | No task241 product diff, sidecar report, generated sidecar, row counts, or tests are present in the reviewed branch | Cannot verify that V10 exists or targets the V9 `aime_06` failure mode |
| Decontamination | AIME25/HMMT/MATH heldout prompts used only as eval/decontam corpus; no prompts, labels, or answer keys in train sidecars, packed shards, distillation prompts, or manifests | No V10 decontam corpus path, scanned/dropped counts, training JSONL, packed shard manifest, or no-leakage test evidence is present | Cannot rule out AIME25/HMMT/MATH leakage |
| Qwen chat-template packing | Preserve tokenizer-native chat template with `enable_thinking=false` and `truncate_history_thinking=false` | No task241/task242/task243 implementation diff touches this surface yet | Existing guards remain, but V10-specific preservation is unproven |
| Planner / 4B first | Generate Qwen3-4B pilot bundle using `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`; hold any 30B/8-GPU scale until same-harness 4B non-regression | No task242 planner diff, manifest, script bundle, fail-closed missing-corpus behavior, or 4B go/no-go plan is present | 4B-first enforcement is not encoded in reviewed artifacts |
| Eval gate | Require same-family same-harness base score before judging FT; fail promotion if FT exact-normalized AIME25 is below base; include parsed/finish diagnostics | No task243 eval-gate diff, protocol report, score normalization schema, or base/FT artifact schema is present | Hard non-regression rule is not enforceable from current task243 artifacts |
| Artifact/runbook | Exact base path, candidate FT path, data/packed/train/eval/log artifact paths, safe NemTron sync/runbook, no deletion of shared data | PR #317 only contains task docs/status and says report will be added; no verification report exists yet | First go/no-go evidence is not reproducible from current PR #317 |

## Decision Details

### worker_1 task241

Decision: BLOCK until implementation and evidence exist.

Required before approval:

- Add a V10 data-prep implementation or scoped weighting extension distinct from
  V7/V8/V9.
- Record source row counts, decontamination scanned/dropped counts, V10 sidecar
  row counts, and output paths.
- Provide no-leakage evidence for AIME25/HMMT/MATH heldouts across train rows,
  sidecar rows, packed shards, supervision metadata, and manifests.
- Preserve existing V7/V8/V9 semantics and Qwen chat-template packing.

### worker_2 task242

Decision: BLOCK until implementation and evidence exist.

Required before approval:

- Add V10 planner/script support that can generate a Qwen3-4B pilot bundle
  without 30B weights.
- Encode the base model path
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`, candidate FT
  output path, corrected AIME evaluator config, and same-harness non-regression
  rule in the manifest.
- Fail closed when the V10 decontamination corpus is missing.
- Keep any 30B/8-GPU plan held until the 4B pilot satisfies the same-harness
  non-regression gate or identifies a concrete fix.

### worker_3 task243

Decision: BLOCK until implementation and evidence exist.

Required before approval:

- Implement or document a corrected AIME25 base-vs-FT gate that refuses to judge
  FT without the matching base result.
- Define pilot-smoke and final-full protocols with identical model family,
  prompt set, repeats, max tokens, parser, endpoint route, temperature/top_p,
  scorer normalization, and diagnostics for base and FT.
- Record numerator, denominator, parsed count, finish reasons, per-problem rows,
  and exact-normalized accuracy.

### worker_5 task245 / PR #317

Decision: REQUEST_CHANGES for PR #317 as a persistent review input; HOLD as gate
evidence until the runbook report is added.

Required before approval:

- Add the runbook verification report promised in the PR body.
- List exact base, candidate FT, prepared data, packed shard, train manifest,
  checkpoint/export, eval output, and log paths.
- Show reproducible same-harness base-vs-FT smoke commands or exact blockers.
- Confirm no step deletes existing shared data and 30B/8-GPU scale remains held.

## Current Gate Verdict

The hard non-regression rule is not enforceable from the proposed V10 artifacts
as currently published. The available branches/PR do not yet contain the V10
data implementation, planner enforcement, eval-gate implementation, or runbook
evidence needed to approve a pilot result.

No upstream V10 PR should be approved for merge or trusted pilot scoring until
the missing evidence above is present and independently re-reviewed.

## Session 2 Hold Note

After this initial matrix, task243 PR #319 appeared with base-vs-FT gate
code/protocol at head `bfb49a86e7e0976da681aff4fedad02a22e0a848`. Lead
reported that #319 still needs a path correction from `/mnt/3fs` to the
required `/mnt/cephfs` Qwen3-4B checkpoint before approval. This note updates
availability only; the matrix remains on hold and should be refreshed after
task241/task242 PRs appear and task243 updates #319.
