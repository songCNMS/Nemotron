# task261_qwen_aime_v10_task255_data_training_root_cause_s1 - History Log

<!-- METADATA:SESSION=1 -->

## Session 0 - Assigned

- Created by `intern_nemotron_lead` for `intern_nemotron_worker_1`.
- Purpose: audit task253 packed data and task255 training/export evidence after
  task257/#330 measured same-harness FT `0/30` versus base `11/30`.
- Scope is read-only data/training root-cause analysis and next-pilot
  recommendation; no training, eval, endpoint launch, code edit, artifact
  modification, promotion, or 30B/8-GPU.
- Global gate remains `NO-GO/HOLD`.

## Session 1 - 2026-06-01 UTC - Accepted by worker

- Fetched `origin/main` at `9c6cdb6974e4b2c27378d95e228d0536fb5ada41`.
- Fetched lead task-doc branch
  `origin/intern_nemotron_lead/session1-recovery-task-docs` at `c866509`.
- Created worker branch
  `intern_nemotron_worker_1/task261_qwen_aime_v10_task255_data_training_root_cause_s1`.
- Imported task261 README/history/task_knowledge and updated worker status to
  Working.
- Boundaries acknowledged: read-only audit only; no training/export/endpoint,
  no AIME/task243 eval, no code or artifact modification, no AIME2025 train
  data, no promotion/go-no-go claim, no 30B/8-GPU, and no shared deletion.

## Session 2 - 2026-06-01 UTC - Root-cause audit report

- Inspected task253 packed Qwen metadata/blend/shard summaries, task251 M1
  source counts and pattern prevalence, task255 training/export logs and
  manifests, and task257 same-harness FT failure evidence.
- Added root-cause report:
  `task255_data_training_root_cause_report.md`.
- Opened PR #333 for lead review.
- Main finding: task255 likely produced a random-init or otherwise wrong-start
  checkpoint because the log has no positive pretrained checkpoint-load line,
  `SUPER3_M1_PRETRAINED_CHECKPOINT` pointed at the raw Qwen HF directory,
  training/validation losses were random-init scale, and downstream outputs were
  long unparseable text.
- Secondary findings: the only training step logged `learning rate: 0`, the
  packed split materialization exposed 8 train symlinks while the blend intended
  15 dataset-qualified train entries, and the actual run consumed only two
  packed rows from a sparse/skewed data surface.
- Boundary confirmation: no task261 training/export/endpoint/eval was launched,
  no AIME2025 train data was used, no artifact/code modifications outside docs,
  no 30B/8-GPU, and global gate remains `NO-GO/HOLD`.
