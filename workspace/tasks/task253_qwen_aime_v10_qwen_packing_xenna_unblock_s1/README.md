# task253_qwen_aime_v10_qwen_packing_xenna_unblock_s1 - Qwen packing Xenna unblock

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_2,SESSION=3 -->

## Background

task251/#328 unblocked the HotpotQA loader path for Qwen3-4B V10 local prep.
The next observed blocker is Qwen packing failing before `packed_qwen` shards on
`ModuleNotFoundError: No module named 'cosmos_xenna'` from
`stage1_sft/data_prep.py`.

The accepted same-harness Qwen3-4B base score remains AIME2025 corrected 30x1
`11/30 = 0.36666666666666664` for
`/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.

## Current Disposition

worker_2 official closeout reports `PASS_PACKED_QWEN_LOCAL_ONLY` at branch head
`749ade2e05b18ae0f1083342eeef0f8a2d61b11e`, with artifact report:
`/work-agents/intern_nemotron_worker_2/outputs/task253_qwen_aime_v10_qwen_packing_xenna_unblock_s1/qwen_packing_xenna_unblock_report.md`.

task254 independently reviewed and approved this as local packed-shard prep
evidence only. It is not candidate FT checkpoint/export/live eval evidence and
does not authorize task243 comparison, promotion, or 30B/8-GPU.

## Goal

Produce Xenna-enabled local Qwen packing evidence for the Qwen3-4B V10 pilot, or
report the exact environment/resource blocker that prevents packing from
producing `packed_qwen` shards.

## Scope

- Start from current `origin/main` after #328 merge commit
  `61fa65e9e9a535d531a65072c839760c3488207f`.
- Reuse task248/task251 generated local prep artifacts when valid, including
  the task251 HotpotQA `local_jsonl_files` registry override.
- Use Qwen3-4B model/tokenizer path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Locate or activate an environment where `cosmos_xenna` is importable; record
  environment path, Python executable, import/version probe output, and any
  install or module path assumptions.
- Run only the local packing step needed to produce `packed_qwen` shards, or a
  precise failure log if the environment remains blocked.
- Write outputs under:
  `/work-agents/intern_nemotron_worker_2/outputs/task253_qwen_aime_v10_qwen_packing_xenna_unblock_s1/`.

## Boundaries

- Do not train, launch NemTron jobs, run FT live eval, run task243 comparison,
  claim promotion, or launch 30B/8-GPU.
- Do not train on AIME2025 prompts or labels; AIME2025 remains eval/decontam
  only.
- Do not delete or overwrite existing files under
  `/mnt/cephfs/data/processing/lei.song`.
- Do not treat packed shards as candidate FT checkpoint evidence.
- If remote node `NemTron` is needed for a debug-only import/packing check,
  sync code to `/root` first and report exact sync path; still do not start
  training.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_2/task253_qwen_aime_v10_qwen_packing_xenna_unblock_s1`.
- PR to `main` only if repo docs/config/scripts need changes; artifact-only
  closeout is acceptable if no repo change is needed.
- Task report with:
  - branch/head/PR or artifact-only status;
  - exact commands and environment;
  - Xenna import probe result;
  - input manifest paths from task248/task251;
  - packed shard paths, counts, and checksums, or exact blocker logs;
  - confirmation that AIME2025 prompts/labels were not used as trainable data.
- Mailbox report to `intern_nemotron_lead`.

## Acceptance Criteria

- PASS: `packed_qwen` shards exist for Qwen3-4B V10 local pilot packing with
  reproducible commands, row counts, checksums, and no AIME25 train leakage.
- BLOCKED: no packed shards, but the blocker is precise and reproducible with
  environment paths, commands, and logs.
- The global gate remains `NO-GO/HOLD` until task248 produces candidate FT
  checkpoint/export/live eval artifacts and task243 proves same-harness FT
  non-regression against the accepted 11/30 base.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Depends on: #328/task251, task248, task246, task247
- First gate: local Xenna-enabled packing evidence only; no training/eval/30B.
