# task249 Live Contamination/Gate Review Matrix

<!-- METADATA:SESSION=4 -->

## Scope

This is an independent review-only artifact. I did not modify product code,
train, run eval, start endpoints, sync to NemTron, merge, push `main`, delete
shared files, or rewrite worker branches.

Branch base: `origin/main` at
`20973e78f196d7e5d71993f60dc74a3500223f5f`, after PR #321.

## Reviewed Inputs

| Task | Owner | Branch / PR | Head inspected | Evidence available | Decision |
| --- | --- | --- | --- | --- | --- |
| task246 real heldout decontam corpus | worker_1 | branch only, no PR found | `a53c913ab80e37197ccfe7525ea04e0ac80c96fe` | README/history/task_knowledge only; no `real_decontam_corpus_report.md`; no task246 output dir found | BLOCK / HOLD |
| task247 Qwen3-4B base AIME smoke | worker_3 | branch only, no PR found | `94c21c9a8cb229f0357a049a698de898963810f1` | Branch has README/history/task_knowledge only; local output has AIME2025 input/cache files but empty `qwen4b_base_smoke` and no `qwen4b_base_smoke_report.md` | BLOCK / HOLD |
| task248 Qwen3-4B V10 pilot prepare/train | worker_2 | branch only, no PR found | `200741802a9ae9cb9f3e16af8f1b7e66fee69857` | `qwen4b_v10_pilot_report.md` exists and correctly blocks before prep/train while task246/task247 evidence is missing; no task248 output dir found | APPROVE blocked-before-prep report / HOLD |
| task250 live runbook artifacts | worker_5 | PR #324 OPEN/CLEAN | `d1525aa617378e407ffa2e99fde44630f9ab43dc` | `live_runbook_artifact_report.md` says NO-GO/HOLD; Session 4 only corrected metadata and the live table still has stale task247 cache, task248 branch, and task249 PR visibility | REQUEST_CHANGES / HOLD |

## Task Findings

### task246

Decision: BLOCK / HOLD for first go/no-go.

Evidence:

- Remote branch exists at `a53c913ab80e37197ccfe7525ea04e0ac80c96fe`.
- The branch contains only `README.md`, `history_log.md`, and
  `task_knowledge.md` under task246.
- No `real_decontam_corpus_report.md` is published.
- No task246 output directory was found under
  `/work-agents/intern_nemotron_worker_1/outputs` with the expected task path.

Gate impact:

- The task242 placeholder decontamination corpus is still the only documented
  corpus artifact. It is explicitly not acceptable live evidence.
- There is no lead-reviewable real AIME25/HMMT/MATH heldout prompt corpus path,
  manifest, row count, hash count, duplicate handling, or no-label-leakage
  evidence.
- There is no real task241-derived V10 M0/input path replacing the task242
  placeholder.

### task247

Decision: BLOCK / HOLD for first go/no-go.

Evidence:

- Remote branch exists at `94c21c9a8cb229f0357a049a698de898963810f1`.
- The branch contains only `README.md`, `history_log.md`, and
  `task_knowledge.md` under task247.
- No `qwen4b_base_smoke_report.md` is published.
- A local output directory now exists at
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1`.
- The visible local output contains an AIME2025 input/cache bundle:
  `aime2025-I.jsonl`, `aime2025-II.jsonl`,
  `aime_score_cache.opencompass_a6ad95f.db`, and
  `aime_score_cache_source_manifest.json`.
- The manifest records source dataset `opencompass/AIME2025` revision
  `a6ad95f611d72cf628a80b58bd0432ef6638f958`, `row_count: 30`,
  `unique_problem_count: 30`, and `labels_stored_in_cache: true`.
- The expected base output directory `qwen4b_base_smoke` is present but empty
  in the read-only file probe.

Gate impact:

- The AIME2025 cache is eval material only; I saw no evidence that it was fed
  into a trainable artifact in task247.
- Cache/input availability does not satisfy the base gate: there is still no
  reachable Qwen3-4B base endpoint evidence and no base score artifact.
- No Qwen3-4B same-harness base score exists.
- No base `summary.json`, `results.jsonl`, `command.txt`, or
  `endpoint_model_manifest.json` is published.
- Without a base score, any FT judgment must remain blocked.

### task248

Decision: APPROVE blocked-before-prep report / HOLD for first go/no-go.

Evidence:

- Remote branch exists at `200741802a9ae9cb9f3e16af8f1b7e66fee69857`.
- The branch publishes
  `workspace/tasks/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/qwen4b_v10_pilot_report.md`.
- The report confirms the Qwen3-4B model path
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507` exists.
- The report reserves task-owned local and NemTron roots, documents the exact
  command shape, and explicitly states not to run it until task246 publishes a
  non-placeholder heldout corpus and real V10 sidecar/M0 input path.
- The report states local prep, training, live eval, FT judgment, 30B/8-GPU
  planning, and shared-file deletion were not run.
- No task248 output directory was found under
  `/work-agents/intern_nemotron_worker_2/outputs` with the expected task path.

Gate impact:

- The blocked-before-prep report is acceptable as a dependency blocker record.
- It is not runtime evidence for the first go/no-go because there is no real
  local data prep, packed shard, NemTron sync, train manifest, checkpoint,
  export, log, or FT eval evidence.
- The task depends on task246 real corpus/input and task247 base artifacts,
  both of which are still missing as accepted evidence.
- No FT result can be judged.

### task250 / PR #324

Decision: REQUEST_CHANGES / HOLD.

Evidence:

- PR #324 is OPEN/CLEAN at `d1525aa617378e407ffa2e99fde44630f9ab43dc`.
- `live_runbook_artifact_report.md` correctly keeps the current live gate at
  NO-GO/HOLD because real task246 corpus/input, task247 base artifacts, task248
  candidate artifacts, task243 comparison output, and 30B permission are
  missing.
- The report records the task242 placeholder bundle and placeholder corpus
  hashes and marks the placeholder corpus as not accepted live evidence.
- Session 4 did not materially refresh the live artifact table; it updated
  metadata/status only and preserved the Session 1 artifact state.

Requested changes before treating #324 as canonical live runbook:

- Refresh task247 corrected input/cache visibility: the task247 output cache is
  now visible at
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache`,
  but no base score artifacts are present.
- Refresh task248 visibility: the task248 branch exists at
  `200741802a9ae9cb9f3e16af8f1b7e66fee69857` and publishes a
  blocked-before-prep `qwen4b_v10_pilot_report.md`; it still lacks runtime FT
  artifacts.
- Refresh task249 visibility: PR #323 exists and this Session 4 matrix is
  published on worker_4 branch.
- Keep the NO-GO/HOLD conclusion unless the missing real runtime artifacts are
  later provided and independently reviewed.

## Combined First Go/No-Go

Decision: NO-GO / HOLD.

The first Qwen3-4B V10 AIME go/no-go cannot pass. Blocking conditions:

- No real heldout AIME25/HMMT/MATH decontamination corpus/input.
- No no-leakage evidence proving heldout prompts/labels are absent from
  trainable artifacts.
- Task247 has an AIME2025 input/cache bundle, but no same-harness Qwen3-4B
  base AIME25 score artifacts.
- No reachable endpoint evidence for base or FT.
- No candidate FT checkpoint/export/eval artifacts.
- No task243 base-vs-FT comparison output proving
  `ft_exact_normalized_accuracy >= base_exact_normalized_accuracy`.
- No explicit 30B/8-GPU permission.

## Verification Commands

Static commands used for this review:

```bash
gh pr list --state all --limit 100 --json number,state,headRefName,headRefOid,baseRefName,mergeStateStatus,title,url
gh pr view 323 --json number,state,headRefOid,mergeStateStatus,url
gh pr view 324 --json number,state,headRefOid,mergeStateStatus,url,files,title,body
git ls-remote --heads origin
git fetch origin intern_nemotron_worker_1/task246_qwen_aime_v10_real_decontam_corpus_s1
git fetch origin intern_nemotron_worker_3/task247_qwen_aime2025_qwen4b_base_smoke_s1
git fetch origin intern_nemotron_worker_2/task248_qwen_aime_v10_4b_pilot_prepare_train_s1
git fetch origin pull/324/head:refs/remotes/origin/pr/324
git show <reviewed-ref>:workspace/tasks/<task>/README.md
git show <reviewed-ref>:workspace/tasks/<task>/history_log.md
git show <reviewed-ref>:workspace/tasks/<task>/task_knowledge.md
find /work-agents/intern_nemotron_worker_1/outputs -maxdepth 3 -path '*task246*' -print
find /work-agents/intern_nemotron_worker_2/outputs -maxdepth 3 -path '*task248*' -print
find /work-agents/intern_nemotron_worker_3/outputs -maxdepth 3 -path '*task247*' -print
find /work-agents/intern_nemotron_worker_5/outputs -maxdepth 3 -path '*task250*' -print
sed -n '1,220p' /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache/aime_score_cache_source_manifest.json
wc -l /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache/aime2025-I.jsonl /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache/aime2025-II.jsonl
```
