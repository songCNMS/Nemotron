# task261_qwen_aime_v10_task255_data_training_root_cause_s1 - task255 data/training root cause

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemotron_worker_1,SESSION=1 -->

## Background

task255 produced a bounded one-iteration Qwen3-4B pilot checkpoint/export from
task253 packed shards. task257/#330 then measured same-harness AIME2025
`0/30 = 0.0`, parsed `0/30`, below the accepted Qwen3-4B base `11/30`.

Before any further training, we need a read-only audit of the data packing,
training recipe, logs, and chat/answer-format contract to identify why the
short pilot degraded AIME parseability so severely.

## Goal

Audit task253/task255 data and training evidence to identify likely data,
packing, loss-mask, answer-format, chat-template, or training-configuration
root causes for the task255 AIME failure, then recommend the safest next V11
pilot plan.

## Scope

- Review task253 packed input evidence:
  `/work-agents/intern_nemotron_worker_2/outputs/task253_qwen_aime_v10_qwen_packing_xenna_unblock_s1/`.
- Review task255 training/export evidence:
  `/work-agents/intern_nemotron_worker_2/outputs/task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1/`.
- Review task255 report:
  `/work-agents/intern_nemotron_worker_2/outputs/task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1/task255_qwen4b_pilot_checkpoint_export_report.md`.
- Review task257 failure summary as downstream evidence:
  `/work-agents/intern_nemotron_worker_3/outputs/task257_qwen_aime_v10_task255_same_harness_eval_s1/ft_eval/task255_ft_aime2025_30x1_20260601T204900Z/summary.json`.
- Inspect existing manifests/logs/configs only. If sampling packed examples is
  useful, keep it read-only and do not modify artifacts.
- Check for:
  - Qwen chat template and `enable_thinking=false` / `truncate_history_thinking=false`;
  - supervised token counts and loss-mask plausibility;
  - train/valid split sizes and data blend composition;
  - answer-format or final-answer supervision prevalence;
  - one-iteration training hyperparameters and validation loss;
  - mismatch between packed training style and AIME eval answer expectations;
  - evidence of overlong/runaway response risk.

## Boundaries

- Read-only analysis only.
- Do not train, export, launch endpoints, run AIME/task243 eval, modify code,
  modify artifacts, merge, or claim promotion.
- Do not use AIME2025 prompts/labels as trainable data.
- Do not launch 30B/8-GPU or delete/overwrite shared files under
  `/mnt/cephfs/data/processing/lei.song`.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_1/task261_qwen_aime_v10_task255_data_training_root_cause_s1`.
- Report file in task docs or output root with:
  - branch/head/PR or mailbox-only status;
  - exact artifacts/logs/configs inspected and hashes where relevant;
  - data/packing/training observations;
  - likely root causes ranked by evidence;
  - concrete V11 pilot recommendation, including what to change and what must
    stay fixed;
  - explicit no-AIME-train-data and no-30B boundary confirmation.
- Mailbox report to `intern_nemotron_lead`.

## Acceptance Criteria

- PASS: report gives actionable next-pilot recommendations grounded in
  task253/task255 evidence and consistent with the hard AIME non-regression
  rule.
- REQUEST-CHANGES/BLOCK: report identifies missing/unreadable artifacts or
  evidence gaps and exact remediation.
- Any next-pilot recommendation must still require same-harness Qwen3-4B
  base-vs-FT comparison and cannot authorize 30B/8-GPU.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_1`
- Related tasks: task253, task255, task257, task261
- Related PRs: #330, #331
- First gate: read-only data/training root-cause report.

## Current Worker State

- Branch:
  `intern_nemotron_worker_1/task261_qwen_aime_v10_task255_data_training_root_cause_s1`.
- Base: current `origin/main` at
  `9c6cdb6974e4b2c27378d95e228d0536fb5ada41`.
- Task docs source:
  `origin/intern_nemotron_lead/session1-recovery-task-docs` at `c866509`.
- Status: root-cause audit report drafted; ready for PR/mailbox closeout after
  branch update and checks.
- Report:
  `workspace/tasks/task261_qwen_aime_v10_task255_data_training_root_cause_s1/task255_data_training_root_cause_report.md`.
