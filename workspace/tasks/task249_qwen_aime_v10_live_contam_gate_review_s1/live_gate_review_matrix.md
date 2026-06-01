# task249 Live Contamination/Gate Review Matrix

<!-- METADATA:SESSION=7 -->

## Scope

This is an independent review-only artifact. I did not modify product code,
train, run eval, start endpoints, sync to NemTron, merge, push `main`, delete
shared files, or rewrite worker branches.

Current main reviewed: `origin/main` at
`85f2bf5c11062741388ca114a84a2c26535b7df9`, which merged task247 PR #326
at 2026-06-01T17:21:29Z. PR #323 pre-refresh head was open/CLEAN at
`b8b2bbd929b20c340dce8e86f81c1252c8d0b02b` before this Session 7 update.

## Reviewed Inputs

| Task | Owner | Branch / PR | Head inspected | Evidence available | Decision |
| --- | --- | --- | --- | --- | --- |
| task246 real heldout decontam corpus | worker_1 | PR #325 OPEN/CLEAN | `266b6a14262278b4fe27f75a3273fc156a5538ce` | `real_decontam_corpus_report.md` and local outputs publish 560 prompt-only heldout rows, 560 prompt hashes, real M0 sidecar input with 8 train / 0 val rows, no AIME25 exact prompt hits in sidecar train, and corrected manifest checksum sidecars; lead gate comment approves if #325 remains CLEAN | APPROVE pending merge / HOLD for combined gate |
| task247 Qwen3-4B base AIME smoke | worker_3 | PR #326 MERGED into `origin/main` | merged head `8fb34bd9116e32aa8d191750f2510d2a843e0da5`, merge `85f2bf5c11062741388ca114a84a2c26535b7df9` | `qwen4b_base_smoke_report.md` is on current main; lead approval comment verifies same-harness base score 11/30 exact-normalized accuracy `0.36666666666666664`, 30/30 requests ok, parsed 23/30, endpoint manifest served `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507` | APPROVE base artifact |
| task248 Qwen3-4B V10 pilot prepare/train | worker_2 | branch only, no PR found | `200741802a9ae9cb9f3e16af8f1b7e66fee69857` | `qwen4b_v10_pilot_report.md` exists and correctly blocks before prep/train while task246 acceptance and task247/base inputs were not both accepted; no task248 output dir or candidate artifacts found | APPROVE blocked-before-prep report / HOLD |
| task250 live runbook artifacts | worker_5 | PR #324 OPEN/CLEAN | `cd4555199ff67eace4d40d4418eef38511786143` | Session 7 runbook refreshed task249 visibility, but it is stale after task246 PR #325 advanced to approved-pending-merge and task247 PR #326 merged; table still records older task246/task247 state | REQUEST_CHANGES / HOLD |

## Task Findings

### task246 / PR #325

Decision: APPROVE pending merge / HOLD for combined first go/no-go.

Evidence:

- PR #325 is OPEN/CLEAN at
  `266b6a14262278b4fe27f75a3273fc156a5538ce`.
- The branch publishes
  `workspace/tasks/task246_qwen_aime_v10_real_decontam_corpus_s1/real_decontam_corpus_report.md`.
- Local output root exists at
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1`.
- Top manifest final-file sha256 is now
  `0a63ac5c1f019cc20dc2e8d4872f0f886d535defc860f28b13f712f36ba72313`.
- Top manifest sidecar
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/manifest.json.sha256`
  records the same final-file checksum.
- The top manifest no longer embeds a self-referential `manifest_sha256`
  field, per the updated report and lead gate comment.
- Heldout corpus path:
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl`.
- Heldout corpus row count is `560`; prompt hash count is `560`.
- Heldout corpus sha256 matches the report:
  `614b2b347d33c1ec00cfd2c33222c26ad1d99b8b837bd7e48ea11fd4fedae6f9`.
- Prompt hashes sha256 matches the report:
  `a2a348ee12f962d5dd7ed7cf0e5d034ebea4a76a2287804e97ade331b552a78d`.
- M0 sidecar train split has `8` rows; val split has `0` rows.
- M0 manifest sha256 and sidecar now match:
  `ca7864ce5ddbec20c0e0b1e67fdaefb2b09ef884f430b68fe7158c5b62951477`.
- M0 train sha256 matches the report:
  `01ac5d1c8571dc956bbae12b7f1a00a4e759d59e503abbf2ddfba3b85aa324e3`.
- M0 val sha256 matches the report:
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- Reported independent validation says heldout label-key leaks `0`,
  decontam blocker findings `0`, and AIME25 exact prompt hits in sidecar
  train JSONL `0`.

Approval state:

- Lead comment after head `266b6a1` says APPROVE / OK to self-merge if #325
  remains CLEAN.
- #325 is still open at this review checkpoint, so I record task246 as
  approved-pending-merge rather than current-main evidence.
- Residual risks remain sparse sidecar `8` train rows and the MATH-500 license
  note; no training/eval/FT judgment/30B authorization is implied.

Gate impact:

- The prior missing-corpus and manifest-checksum blockers are closed at the PR
  gate level, pending merge of #325.
- After #325 merges, the matrix should be refreshed against current `main`.
- This approval does not create task248 FT artifacts or task243 comparison
  output, so the combined first go/no-go remains HOLD.

### task247 / PR #326

Decision: APPROVE base artifact.

Evidence:

- PR #326 is MERGED into `origin/main` at merge commit
  `85f2bf5c11062741388ca114a84a2c26535b7df9`; merged head is
  `8fb34bd9116e32aa8d191750f2510d2a843e0da5`.
- `qwen4b_base_smoke_report.md` is now on current main.
- Lead approval comment verifies the Qwen3-4B base AIME2025 pilot as:
  `11/30` exact-normalized accuracy `0.36666666666666664`, `30/30` requests
  ok, parsed `23/30`.
- Valid local artifact directory:
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z`.
- Required files are present: `summary.json`, `results.jsonl`, `command.txt`,
  and `endpoint_model_manifest.json`.
- Artifact hashes match the report:
  `summary.json` `376f189c69a8b13fc7752f2f8c362a734154d43fe717209dedf6d0d1649d8639`,
  `results.jsonl` `c24ce2bd4b798b0f5913df1a86a34684315a6ac38e3b19764d0dd75889d43961`,
  `command.txt` `bd60cbb4b0ae65ba7cf549e5cde65142d55f9b2dc62181103e75657a937eff40`,
  and `endpoint_model_manifest.json`
  `4f17b1b5880e0cfc5697f99df942f31270e9ce5539212cc5494e9034c86ff354`.
- Endpoint manifest records model path
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- The task-owned AIME2025 cache contains evaluator labels only; no evidence
  shows it was used as trainable output.

Gate impact:

- The same-harness Qwen3-4B base score dependency is now accepted.
- Any FT comparison must use this same cache, runner, prompt variant, endpoint
  route, sampling parameters, and all-request denominator.
- The residual risk is that this is a `30 x 1` pilot base artifact, not a
  repeated 300-request evaluation.

### task248

Decision: APPROVE blocked-before-prep report / HOLD for first go/no-go.

Evidence:

- Remote branch remains at `200741802a9ae9cb9f3e16af8f1b7e66fee69857`.
- The branch publishes
  `workspace/tasks/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/qwen4b_v10_pilot_report.md`.
- The report confirms the Qwen3-4B model path
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507` exists.
- The report reserves task-owned local and NemTron roots and explicitly stops
  before local prep/train until task246 real corpus/input and task247 base
  artifacts are accepted.
- No task248 output directory exists at
  `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1`.

Gate impact:

- The blocked-before-prep report remains acceptable as a dependency blocker
  record.
- It is not runtime evidence for first go/no-go: no local data prep, packed
  shard, NemTron sync, train manifest, checkpoint, export, log, or FT eval
  evidence exists.
- With task247 accepted and task246 approved-pending-merge, task248 still must
  remain held for candidate prep/train/eval until accepted inputs are on main
  or explicitly authorized and task248 produces runtime artifacts.

### task250 / PR #324

Decision: REQUEST_CHANGES / HOLD.

Evidence:

- PR #324 is OPEN/CLEAN at
  `cd4555199ff67eace4d40d4418eef38511786143`.
- `live_runbook_artifact_report.md` Session 7 correctly captures task249 PR
  #323 visibility at `68a8ee77ee25f5dbbac170c935e8487b88198ce2`.
- The table is stale after task246 PR #325 advanced to approved-pending-merge
  and task247 PR #326 merged into main.
- The latest lead comment on #324 still requests a freshness update for #325
  and #326 state; no newer #324 refresh was visible in this review.

Requested changes before treating #324 as the current runbook:

- Record task246 PR #325 at `266b6a14262278b4fe27f75a3273fc156a5538ce` with
  real heldout corpus/M0 paths and approved-pending-merge state.
- Record task247 PR #326 as merged into `origin/main` with accepted base score
  `11/30 = 0.36666666666666664`.
- Preserve HOLD on task248 candidate artifacts, task243 comparison output, and
  30B/8-GPU permission.

## Combined First Go/No-Go

Decision: NO-GO / HOLD.

The first Qwen3-4B V10 AIME go/no-go cannot pass. Current blockers:

- task246 corpus/M0 evidence is approved at PR #325 head `266b6a1`, but #325
  has not merged into `main` at this review checkpoint.
- No task248 candidate local data prep, packed shards, checkpoint/export, FT
  eval output, or train/eval logs exist.
- No task243 base-vs-FT comparison output proves
  `ft_exact_normalized_accuracy >= base_exact_normalized_accuracy` under the
  same cache, runner, prompt, sampling, and denominator as the accepted base.
- task250 PR #324 is stale against current #325/#326 evidence and needs a
  runbook refresh.
- No explicit 30B/8-GPU permission exists.

Accepted current evidence:

- task246 real corpus/M0 evidence is approved-pending-merge at #325 head
  `266b6a14262278b4fe27f75a3273fc156a5538ce`.
- task247 base artifact is accepted on current main with score
  `11/30 = 0.36666666666666664`.
- task248 blocked-before-prep report is acceptable as a blocker record only.

## Verification Commands

Static commands used for this review:

```bash
git fetch origin main pull/324/head:refs/remotes/origin/pr/324 pull/325/head:refs/remotes/origin/pr/325 pull/326/head:refs/remotes/origin/pr/326
gh pr view 323 --json number,state,mergeStateStatus,headRefOid,baseRefName,headRefName,title,url
gh pr view 324 --json number,state,mergeStateStatus,headRefOid,baseRefName,headRefName,title,url,comments
gh pr view 325 --json number,state,mergeStateStatus,headRefOid,baseRefName,headRefName,title,url,comments
gh pr view 326 --json number,state,mergedAt,mergeCommit,headRefOid,baseRefName,headRefName,title,url,comments
git rev-parse origin/main origin/pr/324 origin/pr/325 origin/pr/326
git show origin/pr/325:workspace/tasks/task246_qwen_aime_v10_real_decontam_corpus_s1/real_decontam_corpus_report.md
git show origin/main:workspace/tasks/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_smoke_report.md
git show origin/pr/324:workspace/tasks/task250_qwen_aime_v10_live_runbook_artifacts_s1/live_runbook_artifact_report.md
find /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1 -maxdepth 4 -type f -print
sha256sum /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/manifest.json /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/prompt_hashes.sha256 /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar/manifest.json /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar/math_competition_numeric/train-split.jsonl /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar/math_competition_numeric/val-split.jsonl
cat /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/manifest.json.sha256 /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar/manifest.json.sha256
wc -l /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/prompt_hashes.sha256 /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar/math_competition_numeric/train-split.jsonl /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar/math_competition_numeric/val-split.jsonl
find /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1 -maxdepth 4 -type f -print
jq '.' /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z/summary.json
jq '.' /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z/endpoint_model_manifest.json
sha256sum /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z/summary.json /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z/results.jsonl /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z/command.txt /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z/endpoint_model_manifest.json
find /work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1 -maxdepth 4 -type f -print
```
