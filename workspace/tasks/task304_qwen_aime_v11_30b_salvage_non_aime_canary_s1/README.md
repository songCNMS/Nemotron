# task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1 - 30B salvage non-AIME canary

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemotron_worker_3,SESSION=1 -->

## Background

The 30B V11 training/evidence gate has reached salvage-candidate status:

- #366/task303 merged independent review evidence at merge commit
  `d59161cb01f23d48446dcfee3e65b1266b402c19` from head
  `24157f3c7534845a6959b4760c2cdcec245b3253`.
- #362/task301 merged task301 salvage closeout at merge commit
  `c94216b04bc3d71577391883d0cb76aa8c95e621` from head
  `c75c584875afdbdde4130775cbdc83355e7639ea`.
- task301 reached `35/35`, saved `iter_0000035`, skipped `0`, NaN `0`, then
  hung in built-in validation and was lead-terminated with `train_rc=1`.
- task303 approved the checkpoint as
  `APPROVE_SALVAGE_CANDIDATE_FOR_LATER_NON_AIME_CANARY_CONSIDERATION_ONLY`.

This is not a clean training PASS. The next allowed technical gate is a bounded
non-AIME checkpoint-load/completion-retention canary before any corrected
AIME2025/task243 comparison.

## Goal

Run or precisely block a synthetic non-AIME canary/completion-retention check
for the task301 30B salvage checkpoint `iter_0000035`.

The task must prove whether the salvage checkpoint can load and produce retained,
coherent non-AIME completions under a documented route. It must not run AIME2025
or make any promotion/export/endpoint claim.

## Inputs

- Current main after #362:
  `c94216b04bc3d71577391883d0cb76aa8c95e621`.
- Model/tokenizer:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- task301 remote run root:
  `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z`.
- task301 local output root:
  `/work-agents/intern_nemotron_worker_5/outputs/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z`.
- Candidate checkpoint:
  `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/checkpoints/iter_0000035`.
- Candidate checkpoint root:
  `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/checkpoints`.
- task301 train parallelism/config:
  TP `4`, PP `2`, EP `4`, ETP `1`, sequence parallel enabled, 8x H200.
- task303 review report:
  `workspace/tasks/task303_qwen_aime_v11_30b_task301_salvage_review_s1/task301_salvage_review_report.md`.
- Existing 4B route references:
  task287/task291/task292/task293, especially task291 route
  `direct_in_process_mcore_static_engine_no_export_no_endpoint_topk1_greedy`
  and task292 accepted canary-review evidence.

## Scope

- Start from current `origin/main` after #362.
- Create worker branch:
  `intern_nemotron_worker_3/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1`.
- Sync code to `/root` before any NemTron run, per project rule.
- Use Qwen3-30B-A3B-Instruct-2507 and the task301 `iter_0000035` salvage
  checkpoint only.
- Resolve the current synthetic non-AIME canary prompt source from merged V11
  canary route/runbook history. If no current prompt source exists, fail closed
  with a prompt-provenance blocker.
- Prefer a no-export/no-endpoint in-process checkpoint-load/generation route
  adapted from task291. If no-export/no-endpoint is not possible for 30B, stop
  and report the exact blocker and whether export/endpoint would be required for
  eval-only testing.
- Use the minimum necessary resources for checkpoint load/generation, up to the
  same 8x H200 parallelism used by task301. Document GPUs, parallelism, and why
  they are required.
- Retain full completion artifacts for every synthetic prompt:
  prompt text/hash, expected answer if any, generation config, full response,
  response hash, finish reason, extracted final answer, exact-match status,
  final-answer marker count, and degeneration flags.

## Boundaries

- Do not train or run optimizer steps.
- Do not run AIME2025/task243 eval.
- Do not use AIME2025 prompts or labels as trainable data.
- Do not reuse task255 artifacts.
- Do not promote, claim FT>=base, push main, merge, or delete shared files.
- Do not delete existing files under `/mnt/cephfs/data/processing/lei.song`.
- Do not export, convert, or launch an endpoint unless the no-export route is
  impossible; if export/endpoint appears necessary, stop and report the blocker
  for lead authorization. Any future export/endpoint would be eval-only, never
  promotion.
- Do not run corrected AIME after this canary without a later explicit lead
  assignment.

## Expected Output

- Worker branch and PR if docs/status/report files are added or changed.
- Task-owned local output root:
  `/work-agents/intern_nemotron_worker_3/outputs/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/`.
- Remote task-owned run root under `/root`.
- Report:
  `workspace/tasks/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/30b_salvage_non_aime_canary_report.md`.
- Mailbox report with:
  - branch/head/PR or exact blocker;
  - source commit, local and NemTron paths, commands/env, GPUs, and parallelism;
  - prompt source/provenance/hash and proof prompts are synthetic non-AIME and
    not training rows;
  - checkpoint-load proof or exact blocker;
  - canary route description;
  - per-prompt retained completion artifact paths and checksums;
  - metrics: prompts requested, completions retained, non-empty responses,
    exact matches if expected answers exist, final-answer marker count,
    empty/null/length-stop/mixed-script/degeneration counts;
  - PASS/REQUEST_CHANGES/BLOCK decision;
  - explicit boundary confirmation.

## Acceptance Criteria

- PASS: the 30B `iter_0000035` salvage checkpoint loads under documented
  allowed resources, synthetic non-AIME canary prompts produce retained coherent
  completions, artifacts/checksums are complete, and no boundary violation is
  observed.
- REQUEST_CHANGES: route likely works but artifacts, checksums, prompt
  provenance, metrics, or boundary evidence are incomplete.
- BLOCK: checkpoint cannot load or canary cannot run without AIME data, extra
  training, task255, shared deletion, unapproved export/endpoint, promotion, or
  another boundary/resource violation.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_3`
- Related tasks: task291, task292, task300, task301, task303
- Related PRs: #362, #366
- Next gate: corrected AIME2025 same-harness FT-vs-base comparison remains
  blocked until this task passes and lead explicitly assigns the AIME task.
