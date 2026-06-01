# task249 Live Contamination/Gate Review Matrix

<!-- METADATA:SESSION=10 -->

## Scope

This is an independent review-only artifact. I did not modify product code,
train, run eval, start endpoints, sync to NemTron, merge, push `main`, delete
shared files, or rewrite worker branches.

Current main reviewed: `origin/main` at
`2775dff05948acce3a35a2d941bbd2f96d074b4a`, which merged task246 PR #325 at
2026-06-01T17:43:24Z from head
`266b6a14262278b4fe27f75a3273fc156a5538ce`. Current main also contains
task247 PR #326 at merge commit
`85f2bf5c11062741388ca114a84a2c26535b7df9`.

PR #323 was OPEN/CLEAN at
`39fe428b531fbbbfcef18a34b58cf56b8406d779` before this Session 10 update.

## Final Disposition

Final static task249 disposition: APPROVE static evidence alignment / HOLD
first Qwen3-4B V10 go/no-go.

The final go/no-go remains NO-GO / HOLD because task248 has no candidate FT
prep/train/checkpoint/export/eval artifacts and task243 has no same-harness
base-vs-FT comparison output proving:

```text
ft_exact_normalized_accuracy >= base_exact_normalized_accuracy
```

No 30B/8-GPU authorization is implied.

## Reviewed Inputs

| Task | Owner | Branch / PR | Head inspected | Evidence available | Decision |
| --- | --- | --- | --- | --- | --- |
| task246 real heldout decontam corpus | worker_1 | PR #325 MERGED into `origin/main` | merged head `266b6a14262278b4fe27f75a3273fc156a5538ce`, merge `2775dff05948acce3a35a2d941bbd2f96d074b4a` | `real_decontam_corpus_report.md` is on current main; outputs publish 560 prompt-only heldout rows, 560 prompt hashes, real M0 sidecar input with 8 train / 0 val rows, corrected manifest checksum sidecars, and no AIME25 exact prompt hits in sidecar train | APPROVE corpus/M0 evidence |
| task247 Qwen3-4B base AIME smoke | worker_3 | PR #326 MERGED into `origin/main` | merged head `8fb34bd9116e32aa8d191750f2510d2a843e0da5`, merge `85f2bf5c11062741388ca114a84a2c26535b7df9` | `qwen4b_base_smoke_report.md` is on current main; same-harness base score is 11/30 exact-normalized accuracy `0.36666666666666664`, 30/30 requests ok, parsed 23/30 | APPROVE base artifact |
| task248 Qwen3-4B V10 pilot prepare/train | worker_2 | branch only, no PR found | `200741802a9ae9cb9f3e16af8f1b7e66fee69857` | `qwen4b_v10_pilot_report.md` exists and correctly blocks before prep/train; no task248 output dir or candidate FT artifacts found | APPROVE blocked-before-prep report / HOLD |
| task250 live runbook artifacts | worker_5 | PR #324 OPEN/CLEAN | `827c8cf6562d28cd0f5bafab97e19783961f1abc` | `live_runbook_artifact_report.md` Session 13 is refreshed against current main with #325 and #326 merged; it preserves NO-GO/HOLD on missing task248 FT artifacts, missing task243 comparison, and blocked 30B/8-GPU | APPROVE current runbook / HOLD |

## Task Findings

### task246 / PR #325

Decision: APPROVE corpus/M0 evidence.

Evidence:

- PR #325 is merged into `origin/main` at
  `2775dff05948acce3a35a2d941bbd2f96d074b4a` from head
  `266b6a14262278b4fe27f75a3273fc156a5538ce`.
- `workspace/tasks/task246_qwen_aime_v10_real_decontam_corpus_s1/real_decontam_corpus_report.md`
  is on current main.
- Local output root:
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1`.
- Top manifest final-file sha256:
  `0a63ac5c1f019cc20dc2e8d4872f0f886d535defc860f28b13f712f36ba72313`.
- Top manifest sidecar records the same checksum and the top manifest no
  longer embeds a self-referential `manifest_sha256` field.
- Heldout corpus path:
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl`.
- Heldout rows: `560`; prompt hashes: `560`; duplicates removed: `0`;
  label fields written: `false`.
- Heldout corpus sha256:
  `614b2b347d33c1ec00cfd2c33222c26ad1d99b8b837bd7e48ea11fd4fedae6f9`.
- M0 sidecar input dir:
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar`.
- M0 manifest sha256:
  `ca7864ce5ddbec20c0e0b1e67fdaefb2b09ef884f430b68fe7158c5b62951477`.
- M0 train split has `8` rows and sha256
  `01ac5d1c8571dc956bbae12b7f1a00a4e759d59e503abbf2ddfba3b85aa324e3`.
- M0 val split has `0` rows and sha256
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- Reported independent validation: heldout label-key leaks `0`, decontam
  blocker findings `0`, and exact AIME25 prompt hits in sidecar train `0`.

Residual risk:

- M0 sidecar evidence is sparse: `8` train rows and `0` val rows.
- MATH-500 license remains a policy note.

### task247 / PR #326

Decision: APPROVE base artifact.

Evidence:

- PR #326 is merged into `origin/main` at
  `85f2bf5c11062741388ca114a84a2c26535b7df9` from head
  `8fb34bd9116e32aa8d191750f2510d2a843e0da5`.
- `qwen4b_base_smoke_report.md` is on current main.
- Base score: `11/30`, exact-normalized accuracy
  `0.36666666666666664`; request status `30/30 ok`; parsed rows `23/30`.
- Valid artifact dir:
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z`.
- Required files are present: `summary.json`, `results.jsonl`, `command.txt`,
  and `endpoint_model_manifest.json`.
- Endpoint manifest records model path
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- The task-owned AIME2025 cache contains evaluator labels only; no evidence
  shows it was used as trainable output.

Protocol constraint:

- Any FT comparison must use this same cache, runner, prompt variant, endpoint
  route, sampling parameters, and all-request denominator.

### task248

Decision: APPROVE blocked-before-prep report / HOLD for first go/no-go.

Evidence:

- Remote branch remains at `200741802a9ae9cb9f3e16af8f1b7e66fee69857`.
- The branch publishes
  `workspace/tasks/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/qwen4b_v10_pilot_report.md`.
- The report reserves task-owned local and NemTron roots and documents expected
  command/checkpoint paths.
- No task248 output directory exists at
  `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1`.

Gate impact:

- No local data prep, packed shards, NemTron sync, train manifest, checkpoint,
  export, log, or FT eval evidence exists.
- The first go/no-go cannot proceed without task248 candidate artifacts.

### task250 / PR #324

Decision: APPROVE current runbook / HOLD.

Evidence:

- PR #324 is OPEN/CLEAN at
  `827c8cf6562d28cd0f5bafab97e19783961f1abc`.
- `live_runbook_artifact_report.md` Session 13 is refreshed against current
  main at `2775dff05948acce3a35a2d941bbd2f96d074b4a`.
- The runbook records task246 #325 as merged, task247 #326 as merged baseline,
  task248 candidate FT artifacts as missing, task243 comparison output as
  missing, and 30B/8-GPU as blocked.
- The runbook cites #323 at `b2ae6d59c106225bdc318ccd3383ecf32cd3c37f`
  while current #323 pre-refresh head is
  `39fe428b531fbbbfcef18a34b58cf56b8406d779`.
- This citation mismatch is non-blocking: `git diff --name-status
  b2ae6d59c106225bdc318ccd3383ecf32cd3c37f..39fe428b531fbbbfcef18a34b58cf56b8406d779`
  changes only `status.md`, `history_log.md`, and `task_knowledge.md`; it
  does not change `live_gate_review_matrix.md` or the gate decision.

## Combined First Go/No-Go

Decision: NO-GO / HOLD.

Accepted current evidence:

- task246 real corpus/M0 evidence is merged into current main.
- task247 same-harness Qwen3-4B base artifact is merged into current main with
  score `11/30 = 0.36666666666666664`.
- task250 current runbook is aligned with current main and the task249 matrix.

Remaining blockers:

- No task248 candidate local data prep, packed shards, checkpoint/export, FT
  eval output, or train/eval logs exist.
- No task243 base-vs-FT comparison output proves non-regression under the same
  cache, runner, prompt, sampling, and denominator as the accepted base.
- No explicit 30B/8-GPU permission exists.

## Verification Commands

Static commands used for this review:

```bash
git fetch origin main pull/324/head:refs/remotes/origin/pr/324 pull/323/head:refs/remotes/origin/pr/323
gh pr view 323 --json number,state,mergeStateStatus,headRefOid,baseRefName,headRefName,title,url
gh pr view 324 --json number,state,mergeStateStatus,headRefOid,baseRefName,headRefName,title,url,comments
git rev-parse origin/main origin/pr/324 origin/pr/323
git show origin/pr/324:workspace/tasks/task250_qwen_aime_v10_live_runbook_artifacts_s1/live_runbook_artifact_report.md
git diff --name-status b2ae6d59c106225bdc318ccd3383ecf32cd3c37f..39fe428b531fbbbfcef18a34b58cf56b8406d779
git diff --stat b2ae6d59c106225bdc318ccd3383ecf32cd3c37f..39fe428b531fbbbfcef18a34b58cf56b8406d779
git show origin/main:workspace/tasks/task246_qwen_aime_v10_real_decontam_corpus_s1/real_decontam_corpus_report.md
git show origin/main:workspace/tasks/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_smoke_report.md
find /work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1 -maxdepth 4 -type f -print
```
