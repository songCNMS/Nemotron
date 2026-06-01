# task248_qwen_aime_v10_4b_pilot_prepare_train_s1 - Qwen3-4B V10 pilot

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemotron_worker_2,SESSION=1 -->

## Background

PR #321 merged Qwen3-4B V10 planner/smoke wiring, but no real local data prep,
NemTron sync, Qwen3-4B training, FT export, or FT AIME eval artifact exists.
The first measurable go/no-go still requires a same-harness base score before
any FT judgment.

## Goal

Use the merged V10 planner to prepare the real Qwen3-4B pilot path and, only
after prerequisites are present, run or stage the cheapest task-owned 4B pilot
needed for first AIME non-regression evidence.

## Scope

- Start from current `origin/main` after PR #321.
- Replace placeholder corpus/input paths with task246 real paths.
- Use Qwen3-4B only:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Use task-owned local output and NemTron remote paths:
  `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/`
  and `/root/task248_qwen_aime_v10_4b_pilot_prepare_train_s1`.
- Preserve Qwen tokenizer-native chat-template packing with
  `enable_thinking=false` and `truncate_history_thinking=false`.
- Keep the candidate checkpoint/export path explicit for task250.

## Boundaries

- Do not run or plan 30B/8-GPU scale.
- Do not judge FT until task247 base artifacts exist.
- Do not use AIME25 prompts or labels as training data.
- Do not delete existing files under `/mnt/cephfs/data/processing/lei.song`.
- If task246 or task247 is blocked, stop at a reproducible prepared plan and
  report the blocker instead of forcing a run.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_2/task248_qwen_aime_v10_4b_pilot_prepare_train_s1`.
- PR to `main` for report/docs or small launch/runbook fixes if needed.
- Task report in this directory named `qwen4b_v10_pilot_report.md`.
- If run proceeds: artifact paths for local data, packed shards, NemTron sync
  root, train manifest, checkpoint, export, logs, and FT eval command shape.
- Mailbox report with branch, head SHA, PR URL if any, exact artifact paths,
  commands run, and whether the task stopped before training due blockers.

## Acceptance Criteria

- The pilot uses real task246 decontam corpus/input, not the placeholder.
- Qwen3-4B pilot artifacts are task-owned and reproducible.
- No FT result is judged unless task247 base artifacts are present and task243
  comparison can enforce `ft_exact_normalized_accuracy >= base_exact_normalized_accuracy`.
- No 30B/8-GPU scale is launched or authorized.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Depends on: task242, task246, task247, PR #321
- First gate: produce candidate artifacts only under the Qwen3-4B path; leave
  promotion decision to task249/task250 review after task243 comparison.
