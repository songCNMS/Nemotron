# task259_qwen_aime_v10_task255_artifact_rereview_s1 - task255 artifact re-review

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_5,SESSION=1 -->

## Background

task256 returned `REQUEST_CHANGES/HOLD` because worker_5 could not access
task255 checkpoint/HF export paths under worker_2's `/root` environment.

task258 now reports `PASS_REVIEWER_ACCESS_READY` at PR #331 head
`d0a05c5e9ad37b831fd75bc9ae852cb121527f83`, with a reviewer-readable copied
artifact bundle under:

`/mnt/cephfs/data/processing/intern_nemotron_worker_2/task258_qwen_aime_v10_task255_reviewer_artifact_access_s1/task255_run_20260601T202339Z_full_artifacts_20260601T2109Z`

The global Qwen AIME gate remains `NO-GO/HOLD`: task257/#330 merged a
same-harness failure record for task255 FT `0/30` versus accepted base `11/30`.

## Goal

Independently re-review task255 artifact accessibility and integrity using the
task258 reviewer-readable bundle, then recommend approve/request-changes/block
for task258/#331 and task255/#329 as artifact records only.

## Session 1 Review Closeout

- Recommendation: APPROVE task258/#331 as artifact-access closeout and treat
  task255/#329 as an artifact record only, not a promotion.
- Global gate: still `NO-GO/HOLD` because task257/#330 is merged and records
  task255 FT `0/30` exact-normalized accuracy below the accepted base `11/30`.
- PR checks: #331 is OPEN/CLEAN at
  `d0a05c5e9ad37b831fd75bc9ae852cb121527f83`, base `main`; #329 is
  OPEN/CLEAN at `d62036e405edc5daa322c09bb89da19b176bb7bf`, base `main`.
- Shared bundle reviewed:
  `/mnt/cephfs/data/processing/intern_nemotron_worker_2/task258_qwen_aime_v10_task255_reviewer_artifact_access_s1/task255_run_20260601T202339Z_full_artifacts_20260601T2109Z`.
- Manifest/report hashes matched the task docs exactly, both in worker_2
  outputs and in the shared `review_manifest/` copy:
  - task258 report:
    `bbe89cef817ce0fe131905ab38af85db04ffecc504ceecd970e2ef42917a2256`;
  - `review_access_manifest.json`:
    `53fb4822349106d3462fce7e284bca8a2efdc139c7981fcbe14a8edcb335f372`;
  - `shared_file_inventory.tsv`:
    `50833c7ce5187578621f57a5ba091ff465fce5092d70f9fc752fa0776b750b84`;
  - `shared_full_artifacts.sha256`:
    `415bf1d186591f14d1acd2e4fb115ac91065eb3f33ded61751033bebb9f33d83`.
- Full checksum verification passed:
  `grep -E '^[0-9a-f]{64}  ' review_manifest/shared_full_artifacts.sha256 |
  sha256sum -c -` returned `OK` for all 34 copied files, including the four
  checkpoint `.distcp` shards, three HF safetensors shards, config/tokenizer
  files, source logs, and export helper.
- Manifest counts: checkpoint 18 files / 56,326,605,013 bytes; HF export
  13 files / 8,060,898,808 bytes; source logs 2 files / 107,838 bytes; export
  helper 1 file / 979 bytes; total 34 copied evidence files /
  64,387,612,638 bytes.
- HF config read from the shared copy confirms `Qwen3ForCausalLM`,
  `model_type=qwen3`, 36 layers, hidden size 2560, 32 attention heads, 8 KV
  heads, intermediate size 9728, vocab size 151936. `model.safetensors.index.json`
  is readable and has `metadata` and `weight_map` keys.
- Checkpoint read probe confirmed `latest_checkpointed_iteration.txt` is `1`.
  Checkpoint `metadata.json` and `run_config.yaml` are world-readable and
  checksum-verified.
- Permission checks found no non-world-readable files and no non-world-executable
  directories under the shared bundle. Directories are `755 root:root`; key
  artifact files are `644 root:root`.
- Boundary checks: worker_5 performed read-only shell checks and docs/status
  bookkeeping only. No code edit, artifact modification/deletion, training,
  export, AIME/task243 eval, promotion claim, 30B/8-GPU launch, main push,
  merge/self-merge, or `/mnt/cephfs/data/processing/lei.song` deletion was
  performed.
- Residual risk: approval is limited to reviewer accessibility and copied
  artifact integrity. It does not override the task257/#330 below-base result
  or authorize promotion/scale-up.

## Scope

- Review task258 PR #331 exact head
  `d0a05c5e9ad37b831fd75bc9ae852cb121527f83`.
- Review task255 PR #329 exact head
  `d62036e405edc5daa322c09bb89da19b176bb7bf`.
- Review shared artifact bundle:
  `/mnt/cephfs/data/processing/intern_nemotron_worker_2/task258_qwen_aime_v10_task255_reviewer_artifact_access_s1/task255_run_20260601T202339Z_full_artifacts_20260601T2109Z`.
- Review manifests in the local task258 output root and shared
  `review_manifest/`:
  - `review_access_manifest.json`;
  - `shared_file_inventory.tsv`;
  - `shared_full_artifacts.sha256`.
- Verify that the copied checkpoint/export and manifest evidence match the
  task255/task258 reports closely enough to close artifact accessibility.

## Suggested Checks

- Confirm the shared path is readable from worker_5's environment.
- Verify key hashes:
  - task258 report
    `bbe89cef817ce0fe131905ab38af85db04ffecc504ceecd970e2ef42917a2256`;
  - `review_access_manifest.json`
    `53fb4822349106d3462fce7e284bca8a2efdc139c7981fcbe14a8edcb335f372`;
  - `shared_file_inventory.tsv`
    `50833c7ce5187578621f57a5ba091ff465fce5092d70f9fc752fa0776b750b84`;
  - `shared_full_artifacts.sha256`
    `415bf1d186591f14d1acd2e4fb115ac91065eb3f33ded61751033bebb9f33d83`.
- Spot-check HF export config/tokenizer and safetensors file hashes.
- Spot-check checkpoint `latest_checkpointed_iteration.txt`, `metadata.json`,
  `run_config.yaml`, and large `.distcp` shard hashes from the manifest.
- Confirm permission/access claims: no non-world-readable files and no
  non-world-executable directories, or report exact access blocker.
- Confirm boundaries: no AIME train leakage claim changed, no training/export
  rerun/eval/promotion/30B, and no shared deletion.

## Boundaries

- Read-only review only.
- Do not edit code, commit product changes, push main, merge, or self-merge.
- Do not modify, delete, or move task255/task258 artifacts.
- Do not train, export, run AIME/task243 eval, claim promotion, or launch
  30B/8-GPU.
- Do not delete or overwrite anything under `/mnt/cephfs/data/processing/lei.song`.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_5/task259_qwen_aime_v10_task255_artifact_rereview_s1`.
- PR only if docs/status report files need review; mailbox-only closeout is
  acceptable for read-only review.
- Mailbox report to `intern_nemotron_lead` with:
  - branch/head/PR or mailbox-only status;
  - exact shared paths and manifests reviewed;
  - commands/checks run and pass/fail results;
  - checksum/count/config/access mismatches if any;
  - boundary assessment;
  - approve/request-changes/block recommendation for #331 and #329;
  - residual risks.

## Acceptance Criteria

- APPROVE means task258 solved the reviewer-accessibility blocker and #331 can
  be approved as artifact-access closeout; #329 may then be considered as a
  task255 artifact record, not a promotion.
- REQUEST-CHANGES means worker_2 must fix missing/inconsistent artifact access
  evidence.
- BLOCK means artifact access or integrity remains insufficient.
- Any approval still preserves global `NO-GO/HOLD` because task257 measured FT
  `0/30` below base `11/30`.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_5`
- Related tasks: task255, task256, task258, task257
- Related PRs: #329, #331, #330
- First gate: independent artifact access/integrity re-review only.
