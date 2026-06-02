# task301_qwen_aime_v11_30b_full_sft_training_s1 - 30B full SFT training gate

<!-- METADATA:STATUS=Blocked,ASSIGNEE=intern_nemotron_worker_5,SESSION=1 -->

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

- Wait for task298 PASS runtime/resource/base-load proof.
- Wait for task299 PASS 30B data/packing root and decontam proof.
- Wait for task300 BASE_PASS same-harness 30B base AIME2025 score before any
  FT judgment; do not claim training success as eval success.
- Use exact current main `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7` or report
  if a newer main changes relevant code and requires lead decision.
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
- Current main: `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7`
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
