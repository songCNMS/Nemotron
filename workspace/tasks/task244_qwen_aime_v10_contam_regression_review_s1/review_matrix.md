# task244 Independent Review Matrix

<!-- METADATA:SESSION=4 -->

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

## Session 1 Gate Verdict

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

## Session 3 Refresh

This refresh is still read-only. I reviewed PR metadata and diffs statically;
I did not run training, live evals, implementation tests, or merge/push `main`.

Base for availability checks: `origin/main` at
`f5a844765c5ac1a756b7f7e94d27ee466fe25a9b`, fetched on 2026-06-01.

| Owner | Task | Branch / PR | Head inspected | Diff scope | Decision |
| --- | --- | --- | --- | --- | --- |
| worker_1 | `task241_qwen_aime_v10_sidecar_data_s1` | PR #320 | `57537133bed6bdd5773e6678b48086a8fc6a87b4` | V10 data-prep strategy, decontamination tests, V10 report | APPROVE for data-prep contamination surface; HOLD full go/no-go pending task242 planner wiring and real generated artifacts |
| worker_2 | `task242_qwen_aime_v10_planner_smoke_s1` | no open PR found | remote branch only | no reviewable planner PR | HOLD: cannot verify 4B-first planner enforcement or hidden 30B bypass controls |
| worker_3 | `task243_qwen_aime2025_base_vs_ft_eval_gate_s1` | PR #319 | `61a12dd8b96e51785a3ece76d5883a419b30dd39` | AIME25 base-vs-FT gate module/config/tests/report | APPROVE for static gate/protocol; HOLD live promotion until same-harness base artifacts exist |
| worker_5 | `task245_qwen_aime_v10_artifact_runbook_verify_s1` | PR #317 | `ba3c2a14efc8a710a504cbf601132a5b82d04bf7` | runbook report/task docs | REQUEST_CHANGES / HOLD: runbook still carries stale task243 `/mnt/3fs` blocker statements and must refresh against #319 `61a12dd` |

### PR #320 task241 data and decontamination review

Decision: APPROVE for the data-prep contamination surface.

Evidence:

- Adds `hard_math_runlength_dp_v10` as a separate math supervision strategy and
  includes it in the strategy lists, hard-bucket lists, and
  `STRATEGIES_REQUIRING_MATH_DECONTAMINATION`.
- V10 weights default to hard verified full solution `1.0` and broad/final
  auxiliary/format repair `0.0`, keeping the sidecar focused.
- The V10 filter keeps the V8 clean-final contract, then requires counting
  prompt signal, binary/chair/sequence object signal, run-length constraint
  signal, and either DP/recurrence or case-split combinatorics signal.
- `prepare()` refuses V10 without `--decontaminate-math-against-corpus` unless
  the explicit skip flag is set; tests cover the required-corpus error.
- The AIME25 heldout/decontam test creates an AIME25-like prompt with answer
  `907` and a clean V10 prompt with answer `441`, writes both as candidate
  math train input, puts the AIME25-like prompt in the heldout corpus, and
  asserts `dropped_rows == 1`.
- The same test reads the produced base train JSONL and V10 hard sidecar JSONL,
  asserts the AIME25-like prompt is absent from both, and asserts the clean
  prompt remains in both.
- The task241 report states no AIME25 prompts or labels were added as training
  data; the AIME25-like prompt appears only as heldout/decontam corpus content
  and as an input row intentionally removed by decontamination.

Residual risk:

- I did not run the reported tests or full uncapped M0/sidecar generation, so
  real corpus V10 row counts and real decontam drop counts remain unverified.
- The keyword-based V10 filter is intentionally conservative and may miss
  equivalent run-length DP rows that avoid the configured signal words.
- The skip flag remains present for exceptional use; production planner/runbook
  must not use it for V10.
- Planner/training launch wiring is outside PR #320 and remains blocked on
  task242.

### PR #319 task243 eval-gate review

Decision: APPROVE for static gate/protocol; HOLD live promotion until base
artifacts exist.

Evidence:

- The config now pins Qwen3-4B base checkpoint and tokenizer to
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- The config requires `base_score_required: true`,
  `ft_must_be_at_least_base: true`, and
  `parsed_rate_is_diagnostic_only: true`.
- Pilot and final protocols use `/v1/chat/completions`, Qwen checkpoint chat
  template, `enable_thinking=false`, `truncate_history_thinking=false`,
  `max_tokens=8192`, `temperature=0.0`, `top_p=1e-5`,
  exact-normalized scoring, and denominator policy `all_requests`.
- The gate module validates route/scorer/denominator/chat-template kwargs,
  normalizes all request rows including unparsed, length-capped, and error rows
  into the denominator, and records parsed/finish/status/per-problem
  diagnostics.
- `evaluate_base_vs_ft_gate()` blocks on missing base score, fails if FT
  exact-normalized accuracy is below base, and passes only when FT is at least
  base under the same harness.
- Tests cover config loading, route/thinking drift, all-request denominator and
  diagnostics, missing-base block, FT-below-base fail, pass-at-base, and
  protocol mismatch rejection.

Residual risk:

- No live base score, FT score, or comparison artifact is present. The gate is
  reviewable as code/protocol only; it is not yet evidence that a candidate FT
  passed AIME25 non-regression.
- The task243 report still records historical `/mnt/3fs` probe commands, but
  it also records the Session 2 correction: `/mnt/cephfs` present and old
  `/mnt/3fs` missing. The active config path is corrected.

### task242 planner status

Decision: HOLD / no PR.

No open PR exists for `intern_nemotron_worker_2/task242_qwen_aime_v10_planner_smoke_s1`.
Without a planner PR, I cannot verify that V10 is wired into a Qwen3-4B pilot
bundle, that the decontam corpus is fail-closed in the runnable config, that
the same-harness base-vs-FT gate is invoked before FT judgment, or that
30B/8-GPU scale remains blocked until the 4B pilot satisfies the gate.

### PR #317 task245 runbook status

Decision: REQUEST_CHANGES / HOLD until refreshed.

Evidence:

- PR #317 head `ba3c2a14efc8a710a504cbf601132a5b82d04bf7` has a runbook
  report, but it still lists task243 PR #319 at old head `bfb49a8` and states
  the task243 config uses `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507`.
- The runbook report and task knowledge still describe the task243 `/mnt/3fs`
  path as a current blocker, which is stale after #319 head `61a12dd` corrected
  the config to `/mnt/cephfs`.

Residual risk:

- Until #317 is refreshed, its artifact/runbook gate evidence may route
  operators toward an obsolete blocker and should not be treated as current
  first go/no-go instructions.

## Session 3 Gate Verdict

Static review now supports approving #320 for the V10 data-prep contamination
surface and #319 for the corrected base-vs-FT gate/protocol. The overall V10
pilot remains on hold because task242 has no planner PR, real V10 generated
data/artifacts were not reviewed, no live Qwen3-4B base score exists, and #317
runbook evidence still needs to refresh the stale task243 `/mnt/3fs` blocker.

## Session 4 Refresh

Lead reported task242 PR #321 is now open/CLEAN at
`12ee98ccf7475c2ee77a92b3f1390df06d9edcd0`. This section supersedes the
Session 3 `task242 no PR` hold. Review remains static-only: I did not run
training, live evals, implementation tests, sync scripts, or merge/push `main`.

Base for availability checks: `origin/main` at
`f5a844765c5ac1a756b7f7e94d27ee466fe25a9b`, fetched on 2026-06-01.

| Owner | Task | Branch / PR | Head inspected | Diff scope | Decision |
| --- | --- | --- | --- | --- | --- |
| worker_1 | `task241_qwen_aime_v10_sidecar_data_s1` | PR #320 | `57537133bed6bdd5773e6678b48086a8fc6a87b4` | V10 data-prep strategy, decontamination tests, V10 report | APPROVE for data-prep contamination handling; HOLD full go/no-go pending real corpus/data artifacts and integration with planner |
| worker_2 | `task242_qwen_aime_v10_planner_smoke_s1` | PR #321 | `12ee98ccf7475c2ee77a92b3f1390df06d9edcd0` | planner Qwen3-4B V10 smoke wiring, tests, planner report | APPROVE for planner smoke wiring; HOLD first go/no-go pending real heldout corpus, task241 integration, and live base/FT artifacts |
| worker_3 | `task243_qwen_aime2025_base_vs_ft_eval_gate_s1` | PR #319 | `61a12dd8b96e51785a3ece76d5883a419b30dd39` | AIME25 base-vs-FT gate module/config/tests/report | APPROVE for static gate/protocol; HOLD live promotion until same-harness base artifacts exist |
| worker_5 | `task245_qwen_aime_v10_artifact_runbook_verify_s1` | PR #317 | `b8d3c98237a83008d08abb8e2a39bbe3aa5dc772` | refreshed runbook report/task docs | REQUEST_CHANGES / HOLD: task243 path is refreshed, but runbook still treats task242 as no-PR and should refresh against #321 |

### PR #321 task242 planner review

Decision: APPROVE for planner smoke wiring; HOLD first measurable go/no-go.

Evidence:

- `--qwen4b-v10-pilot` defaults Qwen model/checkpoint/tokenizer to
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507` and uses the
  non-30B Qwen train entrypoint.
- The planner maps the pilot to `hard_math_runlength_dp_v10`, V10 weights
  `1.0/0.0/0.0/0.0`, pack/sequence length `8192`, task-owned local output
  root, and remote root `/root/task242_qwen_aime_v10_planner_smoke_s1`.
- Manifest construction rejects V10 when
  `--math-decontaminate-against-corpus` is missing, not a file, empty, or when
  `--math-skip-decontamination-check` is supplied.
- The generated local data-prep script rechecks that the decontam corpus is
  non-empty and refuses the task242 placeholder marker before running M0/M1
  data prep, so the published placeholder path cannot proceed into training.
- The changed planner/test/report text contains no concrete AIME25 prompt,
  label, answer key, `aime_06`, or `907` leakage; #321 only adds generic
  heldout corpus strings and the placeholder marker.
- The manifest records an AIME gate with same-harness base required,
  `/v1/chat/completions`, AIME25 held-out prompts only, `8192` max tokens,
  exact-normalized pass condition
  `ft_exact_normalized_accuracy >= base_exact_normalized_accuracy`, and
  required diagnostics.
- The sync script rejects V10 pilot remote roots outside `/root/*`, removes
  only `<remote_root>/Nemotron` and the task-owned remote run root, and prints
  that it does not delete `/mnt/cephfs/data/processing/lei.song`.
- 30B planning with V10 is refused unless `--allow-v10-30b-scale` is supplied
  after the Qwen3-4B same-harness AIME gate is documented as passing.
- Reported tests cover Qwen4B pilot bundle, missing/missing-file/empty corpus
  fail-closed cases, 30B hold, 30B override after gate, and sync-script guards.
  I did not execute those tests.

Residual risk and first go/no-go blockers:

- A real AIME25/HMMT/MATH heldout decontam corpus is not present in the PR;
  the generated bundle uses a task-owned placeholder solely to materialize
  paths and must be replaced before data prep.
- PR #321 is based on `main` while task241 V10 data-prep support is in #320, so
  the runnable pilot needs #320 landed or an explicit combined branch.
- No local data prep, packing, NemTron sync, training, live eval, base score,
  FT score, or comparison artifact was run or reviewed.
- The candidate FT checkpoint path is planned as the remote checkpoint root;
  the exact served/exported FT path still must be supplied before endpoint
  eval.

### PR #320 task241 data refresh

Decision: APPROVE for data-prep contamination handling; HOLD full go/no-go.

Session 4 does not change the #320 contamination finding: V10 is
decontam-required by default, the AIME25-like prompt/answer appears only as
heldout/decontam test material and an input row intentionally dropped from
train and V10 hard sidecar, and the clean V10 row remains. Remaining blockers
are real corpus generation/counts and integration with #321.

### PR #319 task243 gate refresh

Decision: APPROVE for static gate/protocol; HOLD live promotion.

Session 4 does not change the #319 gate finding: the active config points to
the approved `/mnt/cephfs` Qwen3-4B path and enforces same-harness
base-required FT-at-least-base AIME25 scoring. Remaining blockers are the
corrected AIME input/cache visibility, a reachable Qwen3-4B base endpoint, and
persisted base/FT comparison artifacts.

### PR #317 task245 runbook refresh

Decision: REQUEST_CHANGES / HOLD until refreshed against #321.

PR #317 head `b8d3c98237a83008d08abb8e2a39bbe3aa5dc772` has corrected the
task243 base path to `/mnt/cephfs`, so the old Session 3 `/mnt/3fs` blocker is
no longer the active issue. However, it still says task242 has no published PR,
points at old task242 branch head `b2d16a7`, and treats task242 planner
artifacts as unpublished. It needs a refresh against #321 head `12ee98c`
before it can be used as current runbook/go-no-go guidance.

## Session 4 Gate Verdict

Static review now supports:

- APPROVE #320 for V10 data-prep contamination handling.
- APPROVE #321 for Qwen3-4B V10 planner smoke wiring.
- APPROVE #319 for static same-harness AIME25 gate/protocol.
- REQUEST_CHANGES / HOLD #317 until the runbook refreshes against #321.

The first go/no-go remains blocked until a real heldout decontam corpus is
available, #320 and #321 are integrated on a runnable branch, task243 produces
same-harness Qwen3-4B base artifacts before FT judgment, the candidate FT
serve/export path is explicit, and #317's runbook matches the current PR heads.
