# task282 Session 74 Runbook Provenance Pipeline Report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_5,SESSION=1 -->

Generated: 2026-06-02T04:50:06Z

## Decision

Recommendation: `PASS` for runbook/provenance update.

The Session 74 record now points at the merged task276 packed Qwen root and
keeps the combined V11 execution gate at `NO-GO/HOLD`. This report is
documentation and read-only verification only. It does not authorize SFT
training, nonzero-LR smoke, live canary, AIME/task243 eval, export, endpoint,
promotion, task255 reuse, AIME2025 train data, shared deletion, main push, merge,
or 30B/8-GPU.

## Provenance

| Item | Value |
|---|---|
| Worker branch | `intern_nemotron_worker_5/task282_qwen_aime_v11_runbook_provenance_pipeline_s1` |
| Branch base | `origin/main` at `793e7dfa73ed1c5bdc8b7b98df5f31ffdd5e38ea` |
| Assigned lead docs commit | `be45766c6fc127b0ba00e784d84810a378b3e8e4` |
| Current lead docs head checked | `0bb37f4b5dd866096e23fc4c185b8ac3c7686d6a` |
| Related merged PR | #344/task276 |
| #344 merged at | `2026-06-02T04:19:38Z` |
| #344 merge commit | `793e7dfa73ed1c5bdc8b7b98df5f31ffdd5e38ea` |
| #344 merged head | `07efab4fa0d8367e96f54af3d2cdc70768d73595` |
| task276 report | `workspace/tasks/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/v11_rematerialized_packed_qwen_report.md` |

## Merged task276 Artifact Inventory

| Artifact | Path / value | SHA256 / result |
|---|---|---|
| task276 run root | `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z` | present in task276 report |
| packed Qwen root | `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen` | accepted packed-data root |
| splits root | `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen/splits` | 48 exposed parquet symlinks |
| split manifest | `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen/splits/manifest.json` | `65501e0eff31cce77ff2d1e36dd915f66fb6b2fd145e0f59701d251e5b7d02c5` |
| split metadata | `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen/splits/metadata.json` | `e4ac2157760dd50e50798a9095bf3ea1fb6834e5f405cac2f877560f42dbafd9` |
| evidence manifest | `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/evidence/packed_qwen_evidence_manifest.json` | `74f3c58283eef46a3b8f63699d730baa90337b9a7177146822170c22ec29e9ee`; sidecar PASS |
| shard checksum list | `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/evidence/packed_qwen_shard_checksums.sha256` | `bb6107163f366334468b8db9b8e6ca74f8ddbd612f8b90d3e500e0efa3ba0312`; 48 entries PASS |
| task-owned DataBlend input | `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/input/v11_data_blend_agentic_sft_v0.json` | `859da9fb9d12c03d184152da12a9978072902f1390399d67391e885dabc47893` |
| Qwen3-4B tokenizer/model path | `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507` | path exists on this host |
| task276 generation code revision | `745f78b9f1b6b42bb4018c3cf1544663f0e9f579` | recorded in evidence manifest |

## Split And Contract Evidence

| Split | Exposed shards | Packed rows | Input tokens | Supervised tokens | Current disposition |
|---|---:|---:|---:|---:|---|
| train | 46 | 279 | 1,024,646 | 228,927 | accepted packed-data evidence |
| valid | 1 | 1 | 1,491 | 1,428 | accepted sparse risk; carry into preflight/review |
| test | 1 | 0 | 0 | 0 | accepted zero-row risk; carry into preflight/review |

Task276 evidence manifest records:

- `DATA_PREP_RC=0`;
- `QWEN_PACKED_DATA_CONTRACT=PASS`;
- `QWEN_CONTRACT_RC=0`;
- `PY_COMPILE_RC=0`;
- `TARGETED_PYTEST_RC=0`;
- intended-vs-exposed multiset parity PASS for train, valid, and test;
- Qwen tokenizer-native chat template with `enable_thinking=false` and
  `truncate_history_thinking=false`;
- no AIME2025 train-leakage evidence: AIME pattern mentions 0, label-like
  top-level keys 0, task246 prompt-hash overlaps 0, final-answer n-gram blocker
  pairs 0, and final-answer blocked rows 0.

## Read-Only Checks Performed

Commands run for task282:

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs --prune
git rev-parse origin/main origin/intern_nemotron_lead/session1-recovery-task-docs
git merge-base --is-ancestor be45766c6fc127b0ba00e784d84810a378b3e8e4 \
  origin/intern_nemotron_lead/session1-recovery-task-docs
gh pr view 344 --json number,state,baseRefName,headRefName,headRefOid,mergeCommit,mergedAt,mergeable,url

cd /work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/evidence
sha256sum -c packed_qwen_evidence_manifest.json.sha256
sha256sum -c packed_qwen_shard_checksums.sha256

find /work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen/splits \
  -maxdepth 3 -type l -name '*.parquet' | sort | wc -l
wc -l /work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/evidence/packed_qwen_shard_checksums.sha256
jq '.split_counts' /work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/evidence/packed_qwen_evidence_manifest.json
test -d /mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507
```

Results:

- #344 is `MERGED` into `main` at `2026-06-02T04:19:38Z`.
- Assigned docs commit `be45766c6fc127b0ba00e784d84810a378b3e8e4` is an
  ancestor of current lead docs head
  `0bb37f4b5dd866096e23fc4c185b8ac3c7686d6a`.
- `packed_qwen_evidence_manifest.json.sha256`: PASS.
- `packed_qwen_shard_checksums.sha256`: PASS for all 48 actual parquet shard
  files.
- `splits` exposes 48 parquet symlinks: train 46, valid 1, test 1.
- The Qwen3-4B path exists locally.

## Session 74 Gate Matrix

| Gate | Required evidence | Current record | Disposition |
|---|---|---|---|
| task276 packed Qwen evidence | merged #344 with task-owned packed root, manifest, checksums, parity, Qwen contract, no-AIME train-leakage record | #344 merged at `793e7dfa73ed1c5bdc8b7b98df5f31ffdd5e38ea`; packed root and checksums verified read-only by task282 | `PASS` as packed-data provenance only |
| task277 independent packed-data review | classify task276 artifact and sparse valid/test risk before preflight | task282 assignment records task276/task277 accepted residual risk; no repo-visible task277 review artifact is present in current main or lead docs | accepted risk is recorded; not a training/eval approval |
| task278 config/import preflight | no-training config resolution, data readability, Qwen3-4B Bridge/checkpoint import or equivalent load proof, fail-closed guards, logs, host, code revision, NemTron `/root` sync if remote | task278 assigned to worker_2 from current main with task276 root and Qwen3-4B path; no task278 PR/artifact evidence found in repo during task282 | current released execution gate; must complete before any smoke release |
| task279 preflight review | independent read-only review of exact task278 evidence | task279 assigned to worker_4; lead docs state HOLD if task278 exact evidence is missing | `HOLD` until exact task278 evidence exists |
| task280 bounded SFT smoke plan | no-run fail-closed plan for minimal Qwen3-4B nonzero-LR SFT smoke using task276 root | planning hold assigned to worker_1; no training is authorized | planning only; execution blocked until task278/task279 pass and lead releases |
| task281 canary/AIME plan | no-run non-AIME canary and corrected AIME2025 same-harness comparison plan | planning hold assigned to worker_3; accepted base comparator remains `11/30 = 0.36666666666666664` | planning only; live canary/AIME blocked until candidate FT artifact and lead release exist |
| promotion or 30B/8-GPU | FT exact-normalized AIME2025 score `>= 11/30` under same harness, plus separate lead gate | no V11 FT candidate, canary pass, or FT-vs-base artifact exists | `NO-GO/HOLD` |

## Artifact Requirements To Preserve

### task278 Preflight

The next accepted preflight record must include:

- exact worker branch/head/PR or exact blocker;
- host, code revision, environment, and whether code was synced to a
  task-owned `/root` directory on `NemTron`;
- command log proving no optimizer step, training loop, checkpoint save from
  training, export, endpoint, canary, or AIME/task243 eval ran;
- task276 packed root, split manifest, metadata, evidence manifest, and shard
  checksum references;
- Qwen3-4B path
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`;
- Qwen3-4B checkpoint load/import proof or exact runtime/config blocker;
- sparse valid/test risk disposition for preflight only.

### task280 Smoke Plan

The no-run smoke plan must preserve:

- Qwen3-4B only;
- task276 packed root only;
- exact LR, max train steps, global and micro batch, sequence length, output
  root, checkpoint naming, logs, and stop criteria;
- fail-closed proof that AIME2025 prompts/labels are not trainable rows;
- explicit non-reuse of task255 and non-overwrite policy for shared paths.

### task281 Canary And Same-Harness AIME Plan

The no-run canary/AIME plan must preserve:

- non-AIME canary prompt source, hashes, metrics, full-completion retention, and
  non-train proof;
- corrected AIME2025 same-harness comparison against accepted Qwen3-4B base
  `11/30 = 0.36666666666666664`;
- same cache, prompt variant, route, parser, scoring normalization, sampling,
  tokenizer chat template, and all-request denominator;
- base rerun requirement if any comparison protocol changes;
- FT must score at least base before any promotion discussion.

## Residual Risks And Blockers

- The valid split has only one packed hard-math row and the test split has zero
  rows. This is accepted as carried risk for the current preflight sequence,
  not as broad validation readiness.
- No task278 no-training preflight artifact was present in repo-visible state at
  the time of this task282 report.
- No task279 independent approval of task278 exists because task278 evidence is
  not yet present.
- No nonzero-LR SFT smoke artifact, live canary pass, candidate FT checkpoint,
  corrected AIME2025 FT-vs-base artifact, promotion review, endpoint, export,
  or 30B/8-GPU clearance exists.
- Task282 did not inspect mailbox-only task277 evidence directly; it records the
  task282 assignment's accepted residual-risk statement and the merged #344
  state as runbook provenance.

## Boundary Confirmation

Worker_5 performed only read-only artifact checks and documentation updates. No
training, nonzero-LR smoke, live canary, AIME/task243 eval, export, endpoint,
promotion, task255 reuse, AIME2025 train data, shared deletion, main push, merge,
or 30B/8-GPU action was performed.
