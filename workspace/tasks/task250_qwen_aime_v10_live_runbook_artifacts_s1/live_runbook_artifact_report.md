# task250 Live Runbook Artifact Report

<!-- METADATA:STATUS=Hold,ASSIGNEE=intern_nemotron_worker_5,SESSION=10 -->

## Summary

This report maintains the live artifact/runbook table for the first
Qwen3-4B V10 AIME go/no-go attempt. Scope is read-only: no training, live eval,
endpoint serving, NemTron sync, 30B/8-GPU launch, shared-file deletion, merge,
or `main` push was performed.

Current decision: **NO-GO / HOLD**.

Session 5 refresh: task248 became visible at branch head `2007418` with
`qwen4b_v10_pilot_report.md`, and task249 PR #323 became visible.

Session 6 refresh: task247 has local AIME2025 input/cache files at
`/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache`.
This partially resolves the old "no corrected AIME input/cache path" blocker,
but it is not yet a pushed task247 report or base score artifact. The Qwen3-4B
endpoint probes still fail, so base scoring remains blocked.

Session 7 refresh: task249 PR #323 is open/CLEAN at head
`68a8ee77ee25f5dbbac170c935e8487b88198ce2` and now publishes
`live_gate_review_matrix.md`. The independent matrix keeps the combined first
go/no-go at NO-GO/HOLD: task246 BLOCK/HOLD, task247 BLOCK/HOLD, task248
approved only as a blocked-before-prep report while still HOLD for runtime
evidence, and task250 required this visibility refresh.

Session 10 refresh: task246 PR #325 advanced to head
`266b6a14262278b4fe27f75a3273fc156a5538ce` and is open/CLEAN with lead gate
APPROVE / OK to self-merge. The checksum fix is present: top manifest
final-file sha256 is `0a63ac5c1f019cc20dc2e8d4872f0f886d535defc860f28b13f712f36ba72313`
and the external `manifest.json.sha256` records the same final-file checksum.
Because #325 is not yet merged, task246 is recorded as APPROVED / PENDING
MERGE rather than on-main evidence.
task247 PR #326 is now merged into current `origin/main` at merge commit
`85f2bf5c11062741388ca114a84a2c26535b7df9`, merged at
`2026-06-01T17:21:29Z` from head
`8fb34bd9116e32aa8d191750f2510d2a843e0da5`; the same-harness Qwen3-4B base
pilot score is `11/30`, exact-normalized accuracy
`0.36666666666666664`, with `30/30` requests ok.
task249 PR #323 is open/CLEAN at `b8b2bbd929b20c340dce8e86f81c1252c8d0b02b`;
its matrix is refreshed for #326 on main but still evaluates task246 before
the #325 checksum fix/approval, so it remains stale relative to #325@`266b6a1`.

Promotion and 30B scale remain blocked until task248 candidate artifacts exist,
the task243 same-harness comparison proves non-regression, and lead grants
explicit 30B permission:

```text
ft_exact_normalized_accuracy >= base_exact_normalized_accuracy
```

## Live Artifact Table

| Surface | Owner task | Current evidence | Exact path or blocker | Status |
| --- | --- | --- | --- | --- |
| Real heldout decontam corpus | task246 | PR #325 is open/CLEAN at `266b6a14262278b4fe27f75a3273fc156a5538ce`; lead gate APPROVE / OK to self-merge, not merged yet | Corpus path: `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl`; 560 rows, corpus sha256 `614b2b347d33c1ec00cfd2c33222c26ad1d99b8b837bd7e48ea11fd4fedae6f9`; top manifest final-file sha256 `0a63ac5c1f019cc20dc2e8d4872f0f886d535defc860f28b13f712f36ba72313` verified by sidecar | APPROVED / PENDING MERGE |
| Real V10 M0/input path | task246 | PR #325 publishes approved task-owned M0 sidecar replacement evidence; local files exist; not merged yet | M0 dir: `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar`; train rows `8`, val rows `0`, M0 manifest sha256 `ca7864ce5ddbec20c0e0b1e67fdaefb2b09ef884f430b68fe7158c5b62951477`; train split sha256 `01ac5d1c8571dc956bbae12b7f1a00a4e759d59e503abbf2ddfba3b85aa324e3` | APPROVED / PENDING MERGE |
| Qwen3-4B base score | task247 | PR #326 is merged into current `origin/main` at merge commit `85f2bf5c11062741388ca114a84a2c26535b7df9`, from head `8fb34bd9116e32aa8d191750f2510d2a843e0da5`; `qwen4b_base_smoke_report.md` is on main | Base output dir: `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z`; score `11/30`, exact-normalized accuracy `0.36666666666666664`, `30/30` requests ok, parsed `23/30`; required files `summary.json`, `results.jsonl`, `command.txt`, `endpoint_model_manifest.json` verified | BASE PRESENT / MERGED |
| Corrected AIME input/cache | task247/task243 | Formalized in merged task247 PR #326 and used for the approved base pilot | Local cache: `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache/aime_score_cache.opencompass_a6ad95f.db`; remote runner cache: `/root/task247_qwen_aime2025_qwen4b_base_smoke_s1/input/aime_score_cache.opencompass_a6ad95f.db`; pinned `opencompass/AIME2025` revision `a6ad95f611d72cf628a80b58bd0432ef6638f958`, 30 rows; FT comparison must use this same cache/protocol | PRESENT ON MAIN |
| Qwen3-4B base endpoint evidence | task247/task248 | task247 launched a task-owned NemTron endpoint for the base run and stopped it after artifact collection | Valid command used `http://127.0.0.1:13147/v1/chat/completions` with model path `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`; common local ports `13000` and `30001` remained unavailable; no current listener is required by task250 | BASE EVIDENCE PRESENT / STOPPED |
| Candidate FT data/prep bundle | task248 | Branch `intern_nemotron_worker_2/task248_qwen_aime_v10_4b_pilot_prepare_train_s1` exists at `2007418`; `qwen4b_v10_pilot_report.md` says blocked before local prep/train | BLOCKER: no real local prep output exists under `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/`; task248 candidate prep/train/eval artifacts are still missing even though task247 is merged and task246 is approved pending merge | HOLD |
| Candidate FT checkpoint | task248 | Branch `2007418` documents expected checkpoint path only | BLOCKER: no checkpoint/export/eval/log artifact exists; expected candidate checkpoint path after a future run is `/root/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/checkpoints` | HOLD |
| Independent live review | task249 | PR #323 is open/CLEAN at `b8b2bbd929b20c340dce8e86f81c1252c8d0b02b`; `live_gate_review_matrix.md` is published | Matrix refresh records #326 merged baseline but still evaluates task246 before #325 head `266b6a1` approval; task249 remains stale relative to the current task246 approved-pending-merge state | REVIEW PRESENT / STALE HOLD |
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
| task246 real corpus/M0 PR | `https://github.com/songCNMS/Nemotron/pull/325` | Open/CLEAN at head `266b6a14262278b4fe27f75a3273fc156a5538ce`; lead gate APPROVE / OK to self-merge if CLEAN; not merged at verification time |
| task246 output root | `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1` | Present; corpus rows `560`, prompt hashes `560`, M0 train rows `8`, M0 val rows `0`; top manifest direct sha256 `0a63ac5c1f019cc20dc2e8d4872f0f886d535defc860f28b13f712f36ba72313`; M0 manifest direct sha256 `ca7864ce5ddbec20c0e0b1e67fdaefb2b09ef884f430b68fe7158c5b62951477` |
| task248 blocked pilot report | `origin/intern_nemotron_worker_2/task248_qwen_aime_v10_4b_pilot_prepare_train_s1:workspace/tasks/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/qwen4b_v10_pilot_report.md` | Present at branch head `2007418`; reports blocked before local prep/train |
| task249 review PR | `https://github.com/songCNMS/Nemotron/pull/323` | Open/CLEAN at head `b8b2bbd929b20c340dce8e86f81c1252c8d0b02b`; `live_gate_review_matrix.md` present but still stale for #325@266b6a1 approval |
| task247 base PR | `https://github.com/songCNMS/Nemotron/pull/326` | Merged into current `origin/main` at `2026-06-01T17:21:29Z`; merge commit `85f2bf5c11062741388ca114a84a2c26535b7df9`, merged head `8fb34bd9116e32aa8d191750f2510d2a843e0da5` |
| task247 local AIME2025 input/cache | `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache` | Present and formalized in #326: `aime2025-I.jsonl` 15 rows sha256 `b91b3c96f05d9635d2a0692b124ebe023c1ff59cb19c074275e6c4b349d0659e`, `aime2025-II.jsonl` 15 rows sha256 `16a2dcfbbf9db1b11f8a69a3ba5e4cac73e3641b19a37e2307e9c12240bbed5e`, sqlite cache sha256 `c8b287d9784d1d4ae5d3ea593a70850aea69b289e3d42e05951c5488330eaf74`; evaluator labels remain cache-only |
| task247 base output | `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z` | Present; `summary.json` sha256 `376f189c69a8b13fc7752f2f8c362a734154d43fe717209dedf6d0d1649d8639`, `results.jsonl` sha256 `c24ce2bd4b798b0f5913df1a86a34684315a6ac38e3b19764d0dd75889d43961`, `command.txt` sha256 `bd60cbb4b0ae65ba7cf549e5cde65142d55f9b2dc62181103e75657a937eff40`, `endpoint_model_manifest.json` sha256 `4f17b1b5880e0cfc5697f99df942f31270e9ce5539212cc5494e9034c86ff354` |
| Shared no-delete root | `/mnt/cephfs/data/processing/lei.song` | Exists; read-only listing returned no entries |

## Expected Live Paths

| Stage | Required live path |
| --- | --- |
| task246 output root | `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/` present; #325 approved pending merge |
| task246 corpus report | `origin/pr/325:workspace/tasks/task246_qwen_aime_v10_real_decontam_corpus_s1/real_decontam_corpus_report.md` at head `266b6a14262278b4fe27f75a3273fc156a5538ce` |
| task246 corpus path | `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl` |
| task246 M0 sidecar path | `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar` |
| task247 base report | `origin/main:workspace/tasks/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_smoke_report.md` at merge commit `85f2bf5c11062741388ca114a84a2c26535b7df9` |
| task247 formalized AIME input/cache report | Included in #326 report; local cache path `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache` |
| task247 base output dir | `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z` containing `summary.json`, `results.jsonl`, `command.txt`, `endpoint_model_manifest.json` |
| task248 output root | `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/` |
| task248 remote root | `/root/task248_qwen_aime_v10_4b_pilot_prepare_train_s1` |
| task248 candidate checkpoint/export | Expected checkpoint path after future run: `/root/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/checkpoints`; export path not yet published |
| task249 review matrix | `origin/pr/323:workspace/tasks/task249_qwen_aime_v10_live_contam_gate_review_s1/live_gate_review_matrix.md` at head `b8b2bbd929b20c340dce8e86f81c1252c8d0b02b`; matrix still needs refresh against #325@266b6a1 approval |
| task243 comparison output | `base_vs_ft_gate_decision.json` and `base_vs_ft_gate_report.md` for identical base/FT corrected AIME harness |

## Coordinator Resource Requests

1. Merge task246 #325 if it remains CLEAN and the task246 owner follows the
   lead-approved self-merge path, then refresh task250 against current main.
2. Produce task248 candidate prep/train/eval artifacts from the approved
   task246 corpus/M0 evidence and merged task247 same-harness base protocol.
3. Produce task243 same-harness base-vs-FT comparison only after task248
   candidate artifacts exist.
4. Keep 30B/8-GPU scale blocked until task243 comparison passes and lead grants
   explicit permission.

## Verification Commands Run

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git ls-remote --heads origin '*task246*' '*task247*' '*task248*' '*task249*' '*task250*'
gh pr list --state open --limit 100 --json number,state,title,headRefName,headRefOid,baseRefName,mergeStateStatus,url
gh pr view 323 --json number,state,headRefName,headRefOid,baseRefName,mergeStateStatus,url,title
gh pr view 325 --json number,state,headRefName,headRefOid,baseRefName,mergeStateStatus,mergedAt,mergeCommit,url,title,comments,reviews
gh pr view 326 --json number,state,headRefName,headRefOid,baseRefName,mergeStateStatus,mergedAt,mergeCommit,url,title,comments
gh pr view 324 --json number,state,headRefName,headRefOid,baseRefName,mergeStateStatus,url
git fetch origin main pull/323/head:refs/remotes/origin/pr/323 pull/325/head:refs/remotes/origin/pr/325 pull/326/head:refs/remotes/origin/pr/326
git show origin/pr/325:workspace/tasks/task246_qwen_aime_v10_real_decontam_corpus_s1/real_decontam_corpus_report.md
git show --oneline -1 origin/main
git show origin/main:workspace/tasks/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_smoke_report.md
git fetch origin intern_nemotron_worker_1/task246_qwen_aime_v10_real_decontam_corpus_s1:refs/remotes/origin/intern_nemotron_worker_1/task246_qwen_aime_v10_real_decontam_corpus_s1 intern_nemotron_worker_3/task247_qwen_aime2025_qwen4b_base_smoke_s1:refs/remotes/origin/intern_nemotron_worker_3/task247_qwen_aime2025_qwen4b_base_smoke_s1 pull/322/head:refs/remotes/origin/pr/322
git fetch origin intern_nemotron_worker_2/task248_qwen_aime_v10_4b_pilot_prepare_train_s1:refs/remotes/origin/intern_nemotron_worker_2/task248_qwen_aime_v10_4b_pilot_prepare_train_s1 pull/323/head:refs/remotes/origin/pr/323
git show origin/intern_nemotron_worker_2/task248_qwen_aime_v10_4b_pilot_prepare_train_s1:workspace/tasks/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/qwen4b_v10_pilot_report.md
git ls-tree -r --name-only origin/pr/323 workspace/tasks/task249_qwen_aime_v10_live_contam_gate_review_s1
git show origin/pr/323:workspace/tasks/task249_qwen_aime_v10_live_contam_gate_review_s1/live_gate_review_matrix.md
find /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1 -maxdepth 3 -type f -printf '%p\n'
sha256sum /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/manifest.json /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/prompt_hashes.sha256 /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar/manifest.json /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/task242_replacement_paths.json
wc -l /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/prompt_hashes.sha256 /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar/math_competition_numeric/train-split.jsonl /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar/math_competition_numeric/val-split.jsonl
find /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z -maxdepth 1 -type f -printf '%p\n'
sha256sum /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z/summary.json /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z/results.jsonl /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z/command.txt /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z/endpoint_model_manifest.json
jq '.' /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z/summary.json
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
