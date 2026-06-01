# task250 Live Runbook Artifact Report

<!-- METADATA:STATUS=Hold,ASSIGNEE=intern_nemotron_worker_5,SESSION=6 -->

## Summary

This report maintains the live artifact/runbook table for the first
Qwen3-4B V10 AIME go/no-go attempt. Scope is read-only: no training, live eval,
endpoint serving, NemTron sync, 30B/8-GPU launch, shared-file deletion, merge,
or `main` push was performed.

Current decision: **NO-GO / HOLD**.

Session 5 refresh: task248 is now visible at branch head `2007418` with
`qwen4b_v10_pilot_report.md`, and task249 PR #323 is open/CLEAN at head
`65c2bda`. Both remain HOLD because task248 is blocked before prep/train and
task249 has not published `live_gate_review_matrix.md`.

Session 6 refresh: task247 has local AIME2025 input/cache files at
`/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache`.
This partially resolves the old "no corrected AIME input/cache path" blocker,
but it is not yet a pushed task247 report or base score artifact. The Qwen3-4B
endpoint probes still fail, so base scoring remains blocked.

Promotion and 30B scale remain blocked until all live evidence is present and
the task243 same-harness comparison proves:

```text
ft_exact_normalized_accuracy >= base_exact_normalized_accuracy
```

## Live Artifact Table

| Surface | Owner task | Current evidence | Exact path or blocker | Status |
| --- | --- | --- | --- | --- |
| Real heldout decontam corpus | task246 | Remote branch exists at `a53c913`; no PR or `real_decontam_corpus_report.md` found | BLOCKER: lead-approved AIME25/HMMT/MATH heldout corpus path is not published; task242 placeholder remains non-acceptable | HOLD |
| Real V10 M0/input path | task246 | Remote branch exists at `a53c913`; no published report artifact found | BLOCKER: real task241-derived input replacing `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/task241_v10_math_sidecar_m0_PENDING` is not published | HOLD |
| Qwen3-4B base score | task247 | Remote branch exists at `94c21c9`; no PR or `qwen4b_base_smoke_report.md` found; local AIME input/cache path now exists | BLOCKER: Qwen3-4B endpoint is unreachable and base output dir with `summary.json`, `results.jsonl`, `command.txt`, and `endpoint_model_manifest.json` is not published | HOLD |
| Corrected AIME input/cache | task247/task243 | Local task247 cache path exists with 30 AIME2025 rows and sqlite cache; no pushed task247 report yet | PARTIAL: `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache` exists, but worker_3 still needs to formalize it in task247 report/PR before it is accepted live evidence | PARTIAL |
| Qwen3-4B endpoint | task247/task248 | Local curl probes failed | BLOCKER: `127.0.0.1:13000/v1/models` and `127.0.0.1:30001/v1/models` returned connection refused | HOLD |
| Candidate FT data/prep bundle | task248 | Branch `intern_nemotron_worker_2/task248_qwen_aime_v10_4b_pilot_prepare_train_s1` exists at `2007418`; `qwen4b_v10_pilot_report.md` says blocked before local prep/train | BLOCKER: task246 real corpus/input and task247 base artifacts are missing; no real local prep output exists under `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/` | HOLD |
| Candidate FT checkpoint | task248 | Branch `2007418` documents expected checkpoint path only | BLOCKER: no checkpoint/export/eval/log artifact exists; expected candidate checkpoint path after a future run is `/root/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/checkpoints` | HOLD |
| Independent live review | task249 | PR #323 is open/CLEAN at `65c2bda`; task docs are visible | BLOCKER: `live_gate_review_matrix.md` is not published in PR #323, so no approve/request-changes/block review exists yet | HOLD |
| Same-harness comparison | task243 | PR #319 merged gate/protocol; PR #322 closeout is open/CLEAN at `f7cc324` | BLOCKER: no base-vs-FT comparison output with `base_vs_ft_gate_decision.json` and `base_vs_ft_gate_report.md` exists | HOLD |
| 30B/8-GPU scale | lead/task248 | No explicit permission observed | BLOCKER: scale remains held until Qwen3-4B same-harness gate passes and lead grants permission | HOLD |

## Existing Static/Placeholder Evidence

| Artifact | Path | Verification |
| --- | --- | --- |
| Qwen3-4B base model | `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507` | Exists; `du -sh` reported `7.6G` |
| Qwen3-30B-A3B model | `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507` | Exists; `du -sh` reported `57G`; not used |
| task242 placeholder bundle root | `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot` | Contains `scaleup_manifest.json`, `report.md`, generated scripts, and placeholder decontam corpus |
| task242 placeholder corpus | `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/aime25_hmmt_math_heldout_decontam_corpus.PLACEHOLDER.jsonl` | Present, one placeholder row, sha256 `5c9ad17afa40472223c90564a8e55f58b2c5db50b33d69800e31de9e92ea2f38`; not accepted as live corpus |
| task242 manifest | `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/scaleup_manifest.json` | Present, sha256 `0fab954e33563ad30477b8d3878155fb9088367034ed14be3a6ca42899ef4552` |
| task242 report | `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/report.md` | Present, sha256 `615da5a3d3c0529fec495219a958fb992f5c8f42f6d50cd227ca2da32a7385bc` |
| task248 blocked pilot report | `origin/intern_nemotron_worker_2/task248_qwen_aime_v10_4b_pilot_prepare_train_s1:workspace/tasks/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/qwen4b_v10_pilot_report.md` | Present at branch head `2007418`; reports blocked before local prep/train |
| task249 review PR | `https://github.com/songCNMS/Nemotron/pull/323` | Open/CLEAN at head `65c2bda`; review matrix file missing |
| task247 local AIME2025 input/cache | `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache` | Present locally: `aime2025-I.jsonl` 15 rows sha256 `b91b3c96f05d9635d2a0692b124ebe023c1ff59cb19c074275e6c4b349d0659e`, `aime2025-II.jsonl` 15 rows sha256 `16a2dcfbbf9db1b11f8a69a3ba5e4cac73e3641b19a37e2307e9c12240bbed5e`, sqlite cache sha256 `c8b287d9784d1d4ae5d3ea593a70850aea69b289e3d42e05951c5488330eaf74`; manifest says `labels_stored_in_cache=true`, so this is evaluator/cache evidence only |
| Shared no-delete root | `/mnt/cephfs/data/processing/lei.song` | Exists; read-only listing returned no entries |

## Expected Live Paths

| Stage | Required live path |
| --- | --- |
| task246 output root | `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/` |
| task246 corpus report | `workspace/tasks/task246_qwen_aime_v10_real_decontam_corpus_s1/real_decontam_corpus_report.md` |
| task247 base report | `workspace/tasks/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_smoke_report.md` |
| task247 formalized AIME input/cache report | A pushed task247 report that records `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache`, source manifest, row counts, checksums, and evaluator-only label handling |
| task247 base output dir | Directory containing `summary.json`, `results.jsonl`, `command.txt`, `endpoint_model_manifest.json` |
| task248 output root | `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/` |
| task248 remote root | `/root/task248_qwen_aime_v10_4b_pilot_prepare_train_s1` |
| task248 candidate checkpoint/export | Expected checkpoint path after future run: `/root/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/checkpoints`; export path not yet published |
| task249 review matrix | `workspace/tasks/task249_qwen_aime_v10_live_contam_gate_review_s1/live_gate_review_matrix.md` |
| task243 comparison output | `base_vs_ft_gate_decision.json` and `base_vs_ft_gate_report.md` for identical base/FT corrected AIME harness |

## Coordinator Resource Requests

1. Assign/publish task246 PR or mailbox evidence with the real non-placeholder
   heldout corpus path and real V10 M0/input path.
2. Have task247 formalize the local AIME2025 input/cache path in a pushed
   report/PR, and provide a reachable Qwen3-4B endpoint or exact endpoint
   resource blocker.
3. Hold task248 training/prep beyond planning until task246 and task247
   prerequisites are concrete and reviewable.
4. Keep 30B/8-GPU scale blocked until task249 review and task243 comparison
   pass.

## Verification Commands Run

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git ls-remote --heads origin '*task246*' '*task247*' '*task248*' '*task249*' '*task250*'
gh pr list --state open --limit 100 --json number,state,title,headRefName,headRefOid,baseRefName,mergeStateStatus,url
gh pr view 323 --json number,state,headRefName,headRefOid,baseRefName,mergeStateStatus,url,title
gh pr view 324 --json number,state,headRefName,headRefOid,baseRefName,mergeStateStatus,url
git fetch origin intern_nemotron_worker_1/task246_qwen_aime_v10_real_decontam_corpus_s1:refs/remotes/origin/intern_nemotron_worker_1/task246_qwen_aime_v10_real_decontam_corpus_s1 intern_nemotron_worker_3/task247_qwen_aime2025_qwen4b_base_smoke_s1:refs/remotes/origin/intern_nemotron_worker_3/task247_qwen_aime2025_qwen4b_base_smoke_s1 pull/322/head:refs/remotes/origin/pr/322
git fetch origin intern_nemotron_worker_2/task248_qwen_aime_v10_4b_pilot_prepare_train_s1:refs/remotes/origin/intern_nemotron_worker_2/task248_qwen_aime_v10_4b_pilot_prepare_train_s1 pull/323/head:refs/remotes/origin/pr/323
git show origin/intern_nemotron_worker_2/task248_qwen_aime_v10_4b_pilot_prepare_train_s1:workspace/tasks/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/qwen4b_v10_pilot_report.md
git ls-tree -r --name-only origin/pr/323 workspace/tasks/task249_qwen_aime_v10_live_contam_gate_review_s1
find /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache -maxdepth 2 -type f -printf '%p\n'
wc -l /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache/*.jsonl
sha256sum /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache/*
sed -n '1,160p' /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache/README.md
jq '.' /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache/aime_score_cache_source_manifest.json
find /work-agents -path '*/outputs/task246*' -o -path '*/outputs/task247*' -o -path '*/outputs/task248*' -o -path '*/outputs/task249*' -o -path '*/outputs/task250*'
find /work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot -maxdepth 2 -type f -printf '%p\n'
sha256sum /work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/scaleup_manifest.json /work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/report.md /work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/aime25_hmmt_math_heldout_decontam_corpus.PLACEHOLDER.jsonl
test -f /work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/aime_score_cache.db
curl -sS --connect-timeout 2 --max-time 4 http://127.0.0.1:13000/v1/models
curl -sS --connect-timeout 2 --max-time 4 http://127.0.0.1:30001/v1/models
test -d /mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507
du -sh /mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507
test -d /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507
du -sh /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507
test -d /mnt/cephfs/data/processing/lei.song
find /mnt/cephfs/data/processing/lei.song -maxdepth 1 -mindepth 1 -printf '%f\n'
```
