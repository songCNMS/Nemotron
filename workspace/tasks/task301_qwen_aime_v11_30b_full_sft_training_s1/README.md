# task301_qwen_aime_v11_30b_full_sft_training_s1 - 30B full SFT training gate

<!-- METADATA:STATUS=Blocked,ASSIGNEE=intern_nemotron_worker_5,SESSION=10 -->

## Background

The user authorized attempting the full 30B Qwen AIME V11 data -> training ->
testing workflow, but the launch must remain fail-closed. Training may only
start after runtime/resource/base-load, data/packing, and 30B base-score gates
are available.

## Goal

Run the bounded 30B Qwen AIME V11 SFT training only after required upstream
gates pass, producing checkpoint, LR/loss/validation, commands/env, logs,
checksums, and an artifact handoff for task300 testing.

## Scope

- Carry task298 runtime route lead approval with residuals; do not treat it as
  sufficient for launch by itself.
- Carry task299/#365 merged 30B data/decontam proof at merge commit
  `205fc919a643b1478964a9e91793247c5e821a38`.
- Wait for task300 BASE_PASS same-harness 30B base AIME2025 score to be
  accepted by worker_4 independent review and lead gate before any FT judgment;
  do not claim training success as eval success.
- Wait for explicit lead sequence clearance before launch.
- Current observed `origin/main` is
  `205fc919a643b1478964a9e91793247c5e821a38` after task299/#365 merge; launch
  still requires task300 and lead clearance.
- Run full 30B SFT with documented model path, packed root, LR, train steps,
  optimizer, parallelism, GPU count/type, validation settings, seed, resume
  policy, output/checkpoint roots, and logs.
- Produce checksum manifests and artifact handoff for task300.

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
- Current observed main: `205fc919a643b1478964a9e91793247c5e821a38`
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
