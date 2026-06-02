# task303_qwen_aime_v11_30b_task301_salvage_review_s1 - task301 salvage artifact review

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_4,SESSION=82 -->

## Background

Task301 launched the bounded Qwen3-30B-A3B V11 SFT after task298 runtime,
task299 data/packing, and task300 same-harness base comparator gates were
accepted. The run reached `35/35`, saved `iter_0000035`, then hung in built-in
validation at `Evaluating iter 1/10`. After the safe wait threshold, lead
cleared a bounded termination/salvage action. Worker_5 refreshed #362 at head
`c75c584875afdbdde4130775cbdc83355e7639ea` with disposition
`TRAINING_LOOP_COMPLETE__VALIDATION_HANG_TERMINATED__CHECKPOINT_SALVAGE_CANDIDATE`.

## Goal

Independently review #362 exact head `c75c584875afdbdde4130775cbdc83355e7639ea`
and the task301 salvage artifacts, then report whether the salvage checkpoint is
reviewable enough to proceed to a later lead-assigned non-AIME canary gate.

## Scope

- Review #362 exact head `c75c584875afdbdde4130775cbdc83355e7639ea`.
- Confirm the PR diff is docs/status/report only and `git diff --check` passes.
- Review task301 report:
  `workspace/tasks/task301_qwen_aime_v11_30b_full_sft_training_s1/30b_full_sft_training_report.md`.
- Review local artifact root:
  `/work-agents/intern_nemotron_worker_5/outputs/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z`.
- Review remote artifact root:
  `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z`.
- Verify key evidence:
  - launch main `e400cea8a1604bc95cc430a194811ff553b99401`;
  - model/tokenizer `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`;
  - train config values and 8x H200 launch;
  - task299 packed mirror hashes and `0` symlink claim;
  - training reached `35/35`;
  - skipped iterations `0`, NaN iterations `0`;
  - validation did not complete;
  - lead-cleared SIGTERM, `train_rc=1`, `train_end=2026-06-02T16:58:51Z`;
  - `iter_0000035` inventory and checksum manifests;
  - process/GPU release proof;
  - no task255, no AIME2025 train rows, no shared deletion.

## Boundaries

- No training, canary, corrected AIME/task243 eval, export, endpoint, promotion,
  follow-on 30B work, task255 reuse, AIME2025 train data, shared deletion, main
  push, merge, or worker_5 branch rewrite.
- Do not approve #362 for merge directly. Report approve/request-changes/block
  to lead only.
- Treat the checkpoint as a salvage candidate, not as a clean training PASS.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_4/task303_qwen_aime_v11_30b_task301_salvage_review_s1`
- Review report:
  `workspace/tasks/task303_qwen_aime_v11_30b_task301_salvage_review_s1/task301_salvage_review_report.md`
- Mailbox report to lead with:
  - exact #362 head reviewed;
  - artifact paths reviewed;
  - commands used;
  - checksum/inventory verification results;
  - approve/request-changes/block decision;
  - residual risks and whether later non-AIME canary may be assigned.

## Acceptance Criteria

- APPROVE: #362/report/artifacts are internally consistent; the salvage
  checkpoint has inventory/checksums and process-release proof; no forbidden
  action is observed; residual validation-hang risk is explicitly carried; and
  the evidence is sufficient only for lead to consider a later non-AIME canary
  task.
- REQUEST-CHANGES: missing/mismatched artifact paths, manifests, checksums,
  command/env, process/GPU release evidence, or residual-risk wording.
- BLOCK: checkpoint is unreviewable, checksum/inventory evidence is invalid,
  forbidden action is observed, task255/AIME2025 train/shared deletion risk is
  present, or the report claims clean training PASS/promotion/eval clearance.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Related PR: #362
- Related task: task301
- Current main: `e400cea8a1604bc95cc430a194811ff553b99401`
