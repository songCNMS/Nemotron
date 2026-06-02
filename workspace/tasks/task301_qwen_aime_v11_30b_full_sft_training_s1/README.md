# task301_qwen_aime_v11_30b_full_sft_training_s1 - 30B full SFT training gate

<!-- METADATA:STATUS=Blocked,ASSIGNEE=intern_nemotron_worker_5,SESSION=15 -->

## Background

The user authorized attempting the full 30B Qwen AIME V11 data -> training ->
testing workflow, but the launch must remain fail-closed. Training may only
start after runtime/resource/base-load, data/packing, and 30B base-score gates
are available.

## Goal

Run the bounded 30B Qwen AIME V11 SFT training after required upstream gates
pass, producing checkpoint, LR/loss/validation, commands/env, logs, checksums,
and an artifact handoff for review before any eval/export/promotion path.

## Scope

- Carry task298 runtime route lead approval with residuals.
- Carry task299/#365 merged 30B data/decontam proof.
- Carry task300/#363 accepted same-harness base comparator `15/30 = 0.5`.
- Use explicit lead launch clearance for `origin/main`
  `e400cea8a1604bc95cc430a194811ff553b99401`.
- Run full 30B SFT with documented model path, packed root, LR, train steps,
  optimizer, parallelism, GPU count/type, validation settings, seed, resume
  policy, output/checkpoint roots, and logs.
- Produce checksum manifests and artifact handoff for checkpoint artifact
  review after the training command returns or after lead-cleared read-only
  collection.

## Boundaries

- Do not train on AIME2025 prompts/labels, reuse task255, delete shared
  `/mnt/cephfs/data/processing/lei.song` files, export for promotion, launch a
  production endpoint, promote, push main, merge, or use a different model/data
  path without reporting and receiving lead gate review.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_5/task301_qwen_aime_v11_30b_full_sft_training_s1`
- Report:
  `workspace/tasks/task301_qwen_aime_v11_30b_full_sft_training_s1/30b_full_sft_training_report.md`
- Artifact root under worker outputs plus remote training root with config,
  launch script, logs, checkpoints, validation/loss summaries, LR proof,
  checksum manifests, and task300 handoff notes.
- Mailbox report with branch/head/PR, upstream gate SHAs/artifacts, exact
  commands/env, resource usage, checkpoint paths, metrics, pass/fail, and
  blockers.

## Acceptance Criteria

- PASS: Upstream gates are satisfied, training completes with a usable 30B
  checkpoint, LR/loss/validation evidence is finite and documented, artifacts
  are checksummed, and task300 can run canary/AIME tests.
- REQUEST-CHANGES: missing upstream gate references, config, LR/loss,
  validation, commands/env, or checksums.
- BLOCK: runtime/data/base gates are absent, training fails without usable
  checkpoint, contamination risk appears, shared deletion would be required, or
  resources are insufficient.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_5`
- Original assignment main: `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7`
- Launch main: `e400cea8a1604bc95cc430a194811ff553b99401`
- Related tasks: task276, task298, task299, task300

## Session 1 Result

- Accepted task301 on branch
  `intern_nemotron_worker_5/task301_qwen_aime_v11_30b_full_sft_training_s1`
  from `origin/main` `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7`.
- Imported task docs from lead branch
  `origin/intern_nemotron_lead/session1-recovery-task-docs` at
  `676d85563e00dfb665b6a911995bd47b4932c370`.
- Checked for task298/task299/task300 branches, PRs, and main task dirs; none
  are visible at this acceptance snapshot.
- Wrote `30b_full_sft_training_report.md` with launch status
  `BLOCKED_UPSTREAM_GATES_MISSING`.
- Did not launch training. Did not use task255, AIME2025 train data, shared
  deletion, export, endpoint, promotion, main push, merge, 30B training, or
  8-GPU execution.

## Session 2 Result

- Pushed remote branch
  `origin/intern_nemotron_worker_5/task301_qwen_aime_v11_30b_full_sft_training_s1`
  at head `b513d769`.
- Opened PR #362:
  `https://github.com/songCNMS/Nemotron/pull/362`.
- Updated worker status, history, and task knowledge with PR #362 and the same
  fail-closed launch blocker.
- Training remains blocked until task298 PASS, task299 PASS, and task300 30B
  base-score artifact are available and lead clears the sequence.
- No training, task255 reuse, AIME2025 train data, shared deletion,
  export-promotion, endpoint-promotion, main push, merge, 30B training, or
  8-GPU execution was performed.

## Session 3 Result

- Refreshed upstream visibility after lead follow-up.
- Confirmed PR #362 is OPEN/base `main`/CLEAN/MERGEABLE at head
  `b8e42b3e748c8c80cb3c4a938f2db06c9cb0b6d6`.
- Recorded visible upstream branches:
  - task298:
    `origin/intern_nemotron_worker_2/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1`
    at `7d24b9295740ef5c21fd443d6399ec9641f8f5c5`;
  - task299:
    `origin/intern_nemotron_worker_1/task299_qwen_aime_v11_30b_data_packing_contract_s1`
    at `ff30fad8e6899b9a98d9530006ef49c52c7d72fb`;
  - task300:
    `origin/intern_nemotron_worker_3/task300_qwen_aime_v11_30b_same_harness_testing_s1`
    at `85a5ba134c486ac36f30b63e9bcae97f51fdc1f6`.
- Exact-branch PR lookups for task298/task299/task300 returned no PRs, and the
  visible branch docs remain `InProgress` without PASS/base-score reports.
- Kept launch disposition `BLOCKED_UPSTREAM_GATES_MISSING`.
- No training, task255 reuse, AIME2025 train data, shared deletion,
  export-promotion, endpoint-promotion, main push, merge, 30B training, or
  8-GPU execution was performed.

## Session 6 Result

- Recorded lead gate update: task298 runtime route is lead-approved with
  residuals, but task301 full 30B SFT training remains HOLD.
- Updated `30b_full_sft_training_report.md` to remove task298 as an active
  launch blocker and keep launch blocked on task299 final 30B data/decontam
  PASS, task300 same-harness 30B base AIME score artifact, and explicit lead
  sequence clearance.
- Did not launch training. Did not use task255, AIME2025 train data, shared
  deletion, export, endpoint, promotion, main push, merge, 30B training, or
  8-GPU execution.

## Session 7 Result

- Recorded lead gate update: task299/#365 has lead approval with residuals,
  pending worker_1 exact-head self-merge/closeout.
- Verified #365 is OPEN/base `main`/CLEAN/MERGEABLE at head
  `b8b760fb8f46cda8f302adbea106f19cc234e038`.
- Verified task300 remains a launch blocker: PR #363 is open at
  `a54fb96e3159ce1a1bc16d2b2c52cf12d553fbe5`, and no accepted same-harness
  30B base AIME score artifact is available to task301.
- Kept launch disposition `BLOCKED_UPSTREAM_GATES_MISSING`.
- Did not launch training. Did not use task255, AIME2025 train data, shared
  deletion, export, endpoint, promotion, main push, merge, 30B training, or
  8-GPU execution.

## Session 8 Result

- Recorded lead gate update: task299/#365 is MERGED into `main` at
  `205fc919a643b1478964a9e91793247c5e821a38`.
- Runtime and data gates are now carried for task301 status purposes.
- Verified task300 remains a launch blocker: PR #363 is OPEN/CLEAN at
  `a54fb96e3159ce1a1bc16d2b2c52cf12d553fbe5`, and no accepted same-harness
  30B base AIME score artifact is available to task301.
- Kept launch disposition `BLOCKED_UPSTREAM_GATES_MISSING`.
- Did not launch training. Did not use task255, AIME2025 train data, shared
  deletion, export, endpoint, promotion, main push, merge, 30B training, or
  8-GPU execution.

## Session 9 Result

- Refreshed #362 docs/status for the lead exact-head request after #362 head
  `efc9aef71c97e53e71eccb3f26416cd479adf1f2` still recorded #365 as
  open/pending.
- Carried task299/#365 as MERGED into `main` at
  `2026-06-02T15:29:15Z` with merge commit
  `205fc919a643b1478964a9e91793247c5e821a38` from head
  `b8b760fb8f46cda8f302adbea106f19cc234e038`.
- Preserved training HOLD until task300 provides an accepted same-harness 30B
  base AIME score artifact and lead gives explicit launch clearance.
- Did not launch training. Did not use task255, AIME2025 train data, shared
  deletion, export, endpoint, promotion, main push, merge, 30B training, or
  8-GPU execution.

## Session 10 Result

- Recorded lead gate update: task300/#363 now has base-score evidence at head
  `155eb0c6845c0bf2b7d40051a9045533ffe00589` reporting 30B base `15/30`
  (`0.5` exact-normalized accuracy).
- Preserved HOLD because the task300 base comparator is not accepted until
  worker_4 independent review and lead gate.
- Kept launch blocked until accepted base comparator and explicit lead launch
  clearance are available.
- Did not launch training. Did not use task255, AIME2025 train data, shared
  deletion, export, endpoint, promotion, main push, merge, 30B training, or
  8-GPU execution.

## Session 11 Result

- Recorded lead gate update: task300/#363 base comparator is lead-approved with
  residuals at exact head `155eb0c6845c0bf2b7d40051a9045533ffe00589`,
  reporting 30B base `15/30 = 0.5`, pending worker_3 exact-head
  self-merge/closeout.
- Preserved training HOLD until #363 is merged/closed out and lead gives
  explicit 30B SFT launch clearance.
- Prepared next launch-plan bindings without launching:
  task299 packed root
  `/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b`
  and base comparator `15/30 = 0.5`.
- Did not launch training. Did not use task255, AIME2025 train data, shared
  deletion, export, endpoint, promotion, main push, merge, 30B training, or
  8-GPU execution.

## Session 12 Result

- Received explicit lead launch clearance after the runtime/resource gate,
  data/packing gate, and same-harness 30B base comparator were accepted or
  merged.
- Synced `origin/main` `e400cea8a1604bc95cc430a194811ff553b99401` to
  `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/Nemotron`.
- Used the lead-accepted task-owned dereferenced packed-data mirror at
  `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/input/task299_packed_qwen_30b_deref_mirror`
  with `391` files, `0` symlinks, and source/remote dereference manifest sha256
  `d80241a9c659c2546591c27941e7c24c32717983250df38c0254113cd28bfc6c`.
- Launched bounded Qwen3-30B-A3B V11 SFT on NemTron with 8x H200,
  `train_iters=35`, LR `5e-7`, min LR `1e-7`, seed `5678`, TP `4`, PP `2`,
  EP `4`, ETP `1`, and checkpoint save interval `5`.
- Training reached iteration `35/35`, saved checkpoint `iter_0000035`, and
  `latest_checkpointed_iteration.txt` reports `35`; skipped iterations and NaN
  iterations remained `0`.
- Current live state is `STILL_RUNNING_VALIDATION_WATCH`: the harness entered
  built-in validation at `Evaluating on 80 samples` / `Evaluating iter 1/10`,
  the log has not advanced since `2026-06-03 00:23:43 +0800`, and no
  `train_rc.txt` or `train_end.txt` exists as of `2026-06-02T16:32:19Z`.
- Process status: launcher, torchrun parent, eight rank processes, and
  TorchInductor compile-worker children are alive; GPU memory remains allocated
  with GPU utilization at `0%` in the snapshot and rank CPU activity visible.
- No kill/restart, canary, corrected AIME FT eval, task243 eval, export,
  endpoint, promotion, follow-on 30B work, task255 reuse, AIME2025 train rows,
  shared deletion, direct main push, or merge was performed.

## Session 13 Result

- Sent official live-status mailbox
  `3bf90a62cca94a939f8e55321fdaea1c` to `intern_nemotron_lead` with disposition
  `STILL_RUNNING_VALIDATION`.
- Fresh read-only snapshot at `2026-06-02T16:35:42Z` still shows no
  `train_rc.txt` or `train_end.txt`; log mtime remains
  `2026-06-03 00:23:43.221057699 +0800`, tailing at
  `Evaluating on 80 samples` / `Evaluating iter 1/10`.
- `latest_checkpointed_iteration.txt` remains `35`, and checkpoint directories
  through `iter_0000035` remain present.
- GPU utilization reads `0%`, but GPU memory remains allocated on all 8x H200;
  rank processes `1258278` through `1258285` are alive with CPU activity and
  `198` TorchInductor compile-worker children were observed.
- Recommended action remains read-only monitoring; if no log or return-code
  progress appears by `2026-06-02T16:53:43Z`, report
  `BLOCKED_VALIDATION_HANG` / validation-teardown blocker and wait for lead
  decision before any termination or checkpoint salvage action.
- No kill/restart/terminate, canary, corrected AIME FT eval, task243 eval,
  export, endpoint, promotion, follow-on 30B work, task255 reuse, AIME2025 train
  rows, shared deletion, direct main push, or merge was performed.

## Session 14 Result

- Sent official publish-status mailbox
  `a8351925601040fa91d7862479201ff8` to `intern_nemotron_lead` with exact
  classification `STILL_RUNNING_VALIDATION_WATCH`.
- Fresh read-only snapshot at `2026-06-02T16:37:54Z` still shows no
  `train_rc.txt` or `train_end.txt`; log mtime remains
  `2026-06-03 00:23:43.221057699 +0800`, tailing at
  `Evaluating on 80 samples` / `Evaluating iter 1/10`.
- `latest_checkpointed_iteration.txt` remains `35`, and checkpoint directories
  through `iter_0000035` remain present.
- GPU utilization reads `0%`, but GPU memory remains allocated on all 8x H200;
  rank processes `1258278` through `1258285` are alive with CPU activity and
  `198` TorchInductor compile-worker children were observed.
- Safe wait threshold is `2026-06-02T16:53:43Z`, 30 minutes after the last log
  mtime. The threshold passed at post-threshold snapshot
  `2026-06-02T16:54:28Z` with no log or return-code progress, so mailbox
  `345316b7e0ed47d8bcf5908a7fdd41b6` reported
  `VALIDATION_TEARDOWN_BLOCKER_NO_LOG_PROGRESS` / `BLOCKED_VALIDATION_HANG` and
  requested lead decision before termination, salvage, restart, eval, export,
  endpoint, promotion, or follow-on work.
- No kill/restart/terminate, canary, corrected AIME FT eval, task243 eval,
  export, endpoint, promotion, follow-on 30B work, task255 reuse, AIME2025 train
  rows, shared deletion, direct main push, or merge was performed.

## Session 15 Result

- Received lead salvage clearance after the validation quiet threshold was
  crossed.
- Took final pre-termination read-only snapshot at `2026-06-02T16:56:37Z`:
  no `train_rc.txt`, no `train_end.txt`, log unchanged past
  `Evaluating iter 1/10`, `latest_checkpointed_iteration.txt=35`, and
  `iter_0000035` present at `399G` with `28` files.
- Sent SIGTERM only to task301 torchrun parent PID `1258209` at
  `2026-06-02T16:58:51Z`; torchrun propagated SIGTERM to rank PIDs `1258278`
  through `1258285`.
- Wrapper wrote `train_rc.txt=1` and
  `train_end.txt=2026-06-02T16:58:51Z`; no matching task301 processes remained
  in the final snapshot, and all 8x H200 GPUs released to `1 MiB` with no
  compute apps.
- Generated final disposition
  `TRAINING_LOOP_COMPLETE__VALIDATION_HANG_TERMINATED__CHECKPOINT_SALVAGE_CANDIDATE`.
  This is not a training PASS.
- Generated artifact inventory/checksums:
  `iter_0000035_inventory.tsv` sha256
  `7c7e60b5bf9a5e747e3115e37701da00b6643cd1c895e3336bef175dc6d13261`,
  `iter_0000035.sha256` sha256
  `c3f2d4b4b5d1c26041d96e5eb8799cf591acef346f75ebfdcdce40a12ec09c03`,
  selected artifact hash manifest sha256
  `1b2a767f72c64764cc481735ac1d2ab1825f92adf6e14ec671a61cae01663692`, and
  copied train log sha256
  `e832845262135dca009d1373f8eeb04a6f3b18e5079f40a6456f20b999b49863`.
- Local copied manifest bundle:
  `/work-agents/intern_nemotron_worker_5/outputs/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/manifests`.
- No canary, corrected AIME FT eval, task243 eval, export, endpoint,
  promotion, follow-on 30B work, task255 reuse, AIME2025 train rows, shared
  deletion, direct main push, or merge was performed.
