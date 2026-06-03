# task313_qwen_all_sft_task310_checkpoint_salvage_review_s1 - Review task310 checkpoint salvage candidate

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_4,SESSION=80 -->

## Background

Task310 attempted the gate-driven all-SFT Qwen3-30B-A3B training run after the
task308 inventory audit, task309 constrained packed-data contract, and task312
pre-launch review/runbook evidence were merged. Worker_5 refreshed current
main, used only the constrained task299 packed root, launched a bounded
35-iteration run, and reached iteration `35/35` with finite training loss and
checkpoint candidate `iter_0000035`.

The run did not cleanly complete. Built-in validation stopped making log
progress at `Evaluating on 80 samples` / `Evaluating iter 1/10`. After lead
clearance, worker_5 performed fail-closed checkpoint salvage: final snapshot,
SIGTERM to the task310 torchrun parent, rc/timestamp recording, process/GPU
release check, artifact sync, docs update, and PR #373 refresh.

## Goal

Independently review whether PR #373 current exact head
`0cbcb3c56df5f097a0fd63ebfa1a3c7cdb36f9b8` and the task310 artifacts are
internally consistent salvage evidence, and recommend whether the preserved
`iter_0000035` checkpoint candidate may be released only to task311
checkpoint-load plus non-AIME canary, or must remain blocked.

## Scope

- Review PR #373 current exact head
  `0cbcb3c56df5f097a0fd63ebfa1a3c7cdb36f9b8`; check that the diff is
  docs/status-only and that task310 report wording is not a clean
  `PASS_TRAINING`.
- Also review drift range
  `7561a578f5f624cf1d3b85bef0dd8abb5c787533..0cbcb3c56df5f097a0fd63ebfa1a3c7cdb36f9b8`;
  lead observed it as worker_5 status plus task310 history/task_knowledge
  bookkeeping only, with `all_sft_30b_full_training_report.md` unchanged.
- Review worker_5 mailbox closeout records:
  - `081adfd36b6741c0af3137bd1bb32d22` is superseded by typo-corrected
    mailbox `b3768110fba243bda67737fa88d3923b`;
  - disposition must remain
    `TRAINING_LOOP_COMPLETE__VALIDATION_HANG_TERMINATED__CHECKPOINT_SALVAGE_CANDIDATE`.
- Review local evidence root:
  `/work-agents/intern_nemotron_worker_5/outputs/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z`.
- Review remote run root:
  `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z`.
- Confirm checkpoint candidate path:
  `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035`.
- Confirm the reported key evidence:
  - preflight summary sha256
    `cff95dc1c07325b9192677670d68fe3b64a54759919879c5ce5db0b82d1b10b3`;
  - launch command sha256
    `c50bdeca383359aa6656884df707089321813efbf36bd01933e2b58389910777`;
  - final checkpoint inventory sha256
    `b30d83f641118da8d7a24438e6c379ba9a5e8e03793ef5ff26514d751d9fa676`;
  - checkpoint payload manifest sha256
    `8cb4e7856f379bc7f1d63d407582bd63981b61c9f346455aa40fb389ef73cbe8`;
  - final pre-termination snapshot sha256
    `700f72dd76ebc1b179da38ed711d7e7651cef862ff2aadaf2d7b722661f20b25`;
  - termination log sha256
    `81428d3b12cab8a465344d416e3e818af260deafee4c87cff6bcc6279c761643`;
  - final local copied evidence sha256
    `ab102b7647ab30498ea7f482dd7a7582d6139f1c8b8ee0709cc2ded12de1f189`.
- Confirm training metrics through iter 35 are finite, skipped iterations are
  `0`, NaN iterations are `0`, `train_rc.txt` is `1`, and no validation metric
  was accepted.
- Verify boundary claims: no task311/canary/benchmark/AIME/task243 eval,
  export, endpoint, promotion, generic raw-stage data, AIME2025 train rows,
  task255 reuse, shared deletion, product-code edit, direct main push, or merge.
- Recommend one of:
  - `APPROVE_SALVAGE_HANDOFF_TO_TASK311_LOAD_CANARY_ONLY`;
  - `REQUEST_CHANGES`;
  - `BLOCK_SALVAGE_CHECKPOINT`.

## Boundaries

- Read-only review and docs/status/report only.
- Do not train, eval, export, create endpoints, promote, modify product code,
  push main, merge, rewrite worker branches, reuse task255, use AIME2025 train
  data, or delete shared files.
- Do not release task311 yourself. The lead will decide after your mailbox
  report.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_4/task313_qwen_all_sft_task310_checkpoint_salvage_review_s1`.
- Report:
  `workspace/tasks/task313_qwen_all_sft_task310_checkpoint_salvage_review_s1/task310_checkpoint_salvage_review_report.md`.
- Mailbox report with branch/head/PR or exact blocker, evidence reviewed,
  commands/env used for read-only review, artifact paths, checksum/protocol
  results, disposition, residual risks, and a clear recommendation for task311
  checkpoint-load/canary release or continued HOLD.

## Acceptance Criteria

- `APPROVE_SALVAGE_HANDOFF_TO_TASK311_LOAD_CANARY_ONLY`: #373 exact head is
  docs/status-only, artifact/checksum/termination evidence is internally
  consistent, boundaries held, and the checkpoint candidate is acceptable for
  checkpoint-load plus non-AIME canary only.
- `REQUEST_CHANGES`: evidence is likely valid but report/checksum/artifact path,
  command/env, residual-risk, or PR/head detail is incomplete.
- `BLOCK_SALVAGE_CHECKPOINT`: checkpoint evidence is inconsistent, validation
  hang/rc=1 makes checkpoint-load unsafe without additional remediation,
  artifact checks fail, or any boundary violation is observed.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Current main: `004870e7d790778b5cdae5cc574257fdc19ec755`
- Review target PR: #373
- Review target head: `0cbcb3c56df5f097a0fd63ebfa1a3c7cdb36f9b8`
- Prior evidence head: `7561a578f5f624cf1d3b85bef0dd8abb5c787533`
- Drift to review: `7561a578..0cbcb3c5` bookkeeping-only claim
- Upstream task: task310
- Downstream task: task311
- Gate state: task311 remains HOLD until lead accepts this review and sends an
  explicit release for checkpoint-load plus non-AIME canary.
