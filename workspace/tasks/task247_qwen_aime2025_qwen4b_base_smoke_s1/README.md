# task247_qwen_aime2025_qwen4b_base_smoke_s1 - Qwen3-4B base AIME smoke

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemotron_worker_3,SESSION=1 -->

## Background

PR #319 merged the corrected AIME2025 same-harness base-vs-FT gate, but the
first actual Qwen3-4B base score artifact is still missing. No fine-tuned
checkpoint may be judged until the same base model has a same-harness corrected
AIME2025 score.

## Goal

Produce the first same-harness Qwen3-4B base AIME2025 pilot-smoke artifact, or
return a precise resource blocker if corrected AIME input/cache or endpoint
resources are unavailable.

## Scope

- Use base checkpoint/tokenizer:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Use the corrected AIME2025 protocol from task243/#319.
- Pilot scope: 30 AIME 2025 problems x 1 repeat, `8192` max tokens,
  `/v1/chat/completions`, `temperature=0.0`, `top_p=1e-5`, exact-normalized
  scoring over all request rows.
- Persist base artifacts: `summary.json`, `results.jsonl`, `command.txt`,
  `endpoint_model_manifest.json`, plus a short report.
- If blocked, report the exact missing path, endpoint, credential, or command.

## Boundaries

- Do not judge any FT checkpoint in this task.
- Do not train models.
- Do not launch 30B or 8-GPU scale.
- Do not delete existing files under `/mnt/cephfs/data/processing/lei.song`.
- Debug/eval runs that need the remote node must use `NemTron` and task-owned
  `/root` paths.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_3/task247_qwen_aime2025_qwen4b_base_smoke_s1`.
- PR to `main` for report/docs or small runner fixes if required.
- Task report in this directory named `qwen4b_base_smoke_report.md`.
- Base output directory containing the required four minimum artifacts.
- Mailbox report with branch, head SHA, PR URL if any, artifact paths, base
  numerator/denominator/accuracy if available, and blockers.

## Acceptance Criteria

- A same-harness Qwen3-4B base AIME2025 pilot score artifact exists, or the
  blocker is exact and actionable.
- Output denominator includes all request rows, including unparsed, errored,
  and length-capped rows.
- Endpoint/model manifest proves the served model is the approved Qwen3-4B
  base checkpoint/tokenizer.
- This task does not evaluate or promote any FT model.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_3`
- Depends on: task243, PR #319
- First gate: task248/task250 must not judge FT until this base artifact exists.
