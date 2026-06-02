# task278_qwen_aime_v11_task276_config_import_preflight_s1 - task276 config/import preflight

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_2,SESSION=4 -->

## Background

Coordinator Session 43 authorizes an attempt at the full Qwen AIME V11
data-to-training-to-evaluation pipeline, but the flow must stay gate-driven and
fail-closed. PR #344/task276 is merged on `origin/main`
`793e7dfa73ed1c5bdc8b7b98df5f31ffdd5e38ea` and provides accepted packed-data
evidence only.

The accepted packed root is:

`/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen`

The Qwen3-4B debug/base path is:

`/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`

The accepted base AIME2025 comparator remains `11/30 =
0.36666666666666664`.

## Goal

Run a no-training config/import preflight proving that the current V11 packed
root and Qwen3-4B checkpoint can be wired into the training stack without
starting optimization. This is the only currently released execution gate.

## Scope

- Start from current `origin/main`
  `793e7dfa73ed1c5bdc8b7b98df5f31ffdd5e38ea`.
- Use task276 packed root and split manifest exactly as merged/reviewed.
- Use Qwen3-4B path
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Reconcile and carry the task276/task277 sparse-valid/test risk:
  - valid split has one packed row;
  - test split has one exposed shard and zero rows.
- If remote debug is needed, sync code to `/root` on `NemTron` before running,
  per project rules.
- Run no-training preflight only: config resolution, data path/readability,
  Bridge/checkpoint import or equivalent load proof, fail-closed launch guards,
  and artifact/log capture.

## Required Evidence

Report by mailbox and branch/PR if docs/status/report files change:

- branch/head/PR or exact blocker;
- exact commands, environment, host, code revision, and whether code was synced
  to `/root` on `NemTron`;
- preflight output root and logs;
- task276 packed root, split manifest, metadata, and checksum references;
- Qwen3-4B checkpoint path and load/import proof;
- config path or generated config payload, including packed-data paths,
  tokenizer/model path, batch/sequence settings, optimizer/training-disabled
  guard, and any LR/train-step values if present;
- explicit proof that no training loop, optimizer step, checkpoint save from
  training, export, endpoint, live canary, or AIME/task243 eval was run;
- pass/fail for sparse valid/test acceptability for preflight only;
- exact blocker if any required runtime package, path, permission, config
  schema, Bridge import, or data path fails.

## Boundaries

- Do not train, run nonzero-LR smoke, run live canary, run AIME/task243 eval,
  export, launch endpoint, promote, reuse task255, put AIME2025 prompt/label
  rows into training, delete shared files, push main, merge, or use 30B/8-GPU.
- Do not delete or overwrite anything under
  `/mnt/cephfs/data/processing/lei.song`.
- If a command might start optimization, stop and report the exact command as a
  blocker instead of running it.

## Acceptance Criteria

- PASS: no-training config/import preflight succeeds with complete commands,
  logs, artifact paths, code revision, packed root evidence, Qwen3-4B load/import
  proof, and fail-closed no-training confirmation.
- REQUEST-CHANGES: preflight is plausible but evidence is incomplete, stale, or
  missing required paths/checks.
- BLOCK: runtime/config/data/checkpoint/import issues prevent safe preflight or
  the only available path would start training.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Related tasks: task247, task262, task270, task271, task272, task276, task277
- Related PR: #344
- Current gate: no-training config/import preflight only.
