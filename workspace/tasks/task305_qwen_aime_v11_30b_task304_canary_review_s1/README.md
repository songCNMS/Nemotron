# task305_qwen_aime_v11_30b_task304_canary_review_s1 - task304 canary gate review

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_4,SESSION=85 -->

## Background

Task304 produced PR #367 for a bounded synthetic non-AIME canary against the
task301 Qwen3-30B-A3B salvage checkpoint `iter_0000035`.

Current observed state:

- `origin/main`: `c94216b04bc3d71577391883d0cb76aa8c95e621`.
- PR #367: OPEN, base `main`, CLEAN/MERGEABLE, non-draft.
- PR #367 current head:
  `a38abd53c897b3c68878abb770cb80f762c20e6f`.
- Worker branch:
  `intern_nemotron_worker_3/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1`.
- Task304 report disposition: `PASS`.
- The task304 report names evidence source head
  `d8e58461ca1cede2569589f95414c360e0ddd9bc`. PR head first reached
  `773aff2cc9eaa7d0900b06f5d49dc29515cae709`, then advanced to `a38abd53`
  after worker_3 status/history hygiene. These later deltas must be confirmed
  by this review.

Lead has not yet approved #367. No corrected AIME2025/task243 evaluation,
export, endpoint, promotion, or FT-vs-base claim is cleared by task304 alone.

## Goal

Independently review #367 exact head
`a38abd53c897b3c68878abb770cb80f762c20e6f` and the task304 canary artifacts.
Return an approve/request-changes/block gate decision for whether lead may
accept task304 as a non-AIME checkpoint-load/completion-retention canary and
then consider a separate corrected AIME2025 FT-vs-base task.

## Scope

- Review PR #367 exact head
  `a38abd53c897b3c68878abb770cb80f762c20e6f`.
- Confirm #367 is base `main`, CLEAN/MERGEABLE, non-draft, and diff-check
  clean.
- Confirm PR diff scope is task304 docs/report/runner plus worker_3 status, and
  that no unrelated product training/eval path is changed.
- Compare the task304 report evidence source
  `d8e58461ca1cede2569589f95414c360e0ddd9bc` with PR head `a38abd53`; state
  whether the later delta is only report/docs/status/hygiene closeout.
- Separately compare `773aff2cc9eaa7d0900b06f5d49dc29515cae709..a38abd53` and
  confirm whether it is only worker status plus task304 history hygiene.
- Review task304 report:
  `workspace/tasks/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/30b_salvage_non_aime_canary_report.md`.
- Review local task304 artifact root:
  `/work-agents/intern_nemotron_worker_3/outputs/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/run_20260602T175458Z`.
- Review remote task304 root if needed, read-only:
  `/root/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/run_20260602T175458Z`.
- Verify key artifacts and checksums:
  - `artifacts/canary/canary_summary.json`
    `be1a1b544a8f007c4ffceaa5dc758434f8452b4dace0c4f054ca43c8d9ca7c5f`;
  - `artifacts/canary/canary_decision.json`
    `7678a8f8f3445882a1e5ea575169d37aae7f7ad9ead14b4f5d788fa5c5cb3ba5`;
  - `artifacts/canary/canary_results.jsonl`
    `35bde0394601c94a278c81600ab9fd5039ac9985ea47219226a138041f81a462`;
  - `artifacts/canary/canary_full_completions.jsonl`
    `7589dced789173f3956712ca0c0c17215e03d90cb71419ce22209d8aa9bad957`;
  - `artifacts/manifests/canary_prompt_manifest.json`
    `7b8de981e7d55bd146c557edffd689ed7d1c4af76a14037a0bdfa7770f262da5`;
  - `artifacts/manifests/checkpoint_load_manifest_rank0.json`
    `2989b432df6e804c6afe11e86ee0baafaed1ea42c2d6b24f9de1317abb92d901`;
  - `artifacts/manifests/command_env_manifest_rank0.json`
    `d5e282347975d510d2d58b57f26dd8628566d16893b0cd41aba2a8f7a3ee55d8`;
  - `artifacts/manifests/checksum_manifest.json`
    `0bdbdd6cc28c7c76d6966d1e60832f048c7eb64dff3931c84e269c1a1c2be27b`;
  - `artifacts/logs/ranks/rank00_events.jsonl`
    `702b1640e2861b45a7811e0bfc31fa705f2b8cca9fc413b7b85cd797f4b26132`;
  - `logs/remote_no_export_canary.log`
    `18d8dbd021f72f4117f0e183da910a6242ca5d75efe6509816c54a09f5f6d872`;
  - `logs/remote_no_export_canary_command.txt`
    `83721a5516e716452427e1c72cea3a67fca4f533a418872b3f1cc688b1e9ac20`;
  - `logs/remote_no_export_canary.rc`
    `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`.
- Verify canary metrics and schema:
  - disposition `PASS`;
  - `remote_no_export_canary.rc=0`;
  - prompts requested `5`;
  - retained completions `5`;
  - non-empty responses `5`;
  - exact expected-answer matches `5/5`;
  - final-answer marker count `9`;
  - empty, mixed-script, and degeneration counts `0`;
  - all aggregate and per-rank results/completions have 5 rows.
- Verify checkpoint-load proof:
  - `load_megatron_model=PASS`;
  - model dtype `torch.bfloat16`;
  - model eval `true`;
  - TP `4`, PP `2`, EP `4`, ETP `1`, sequence parallel true;
  - rank event logs record effective `mp_overrides`.
- Verify prompt provenance:
  - prompt YAML
    `src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_v11_export_load_canary_prompts.yaml`;
  - prompt sha256
    `150ee11dc6e8efd3c865a8e9ed8a9ab8ce4f5ee032bed383c73a6cea34f52f1c`;
  - prompt set id `qwen_v11_non_aime_export_load_canary_v1`;
  - prompt manifest confirms synthetic non-AIME, excludes AIME2025, excludes
    training rows, and contains no AIME2025 prompt or label text.
- Verify residuals are accurately carried:
  - task301 checkpoint remains a salvage candidate, not a clean training PASS;
  - task304 is synthetic non-AIME only, not benchmark-quality evidence;
  - no-export greedy route uses `top_k=1`, `temperature=1.0`, `top_p=0.0`;
  - `command_env_manifest_rank0.json` has the known `mp_overrides` null-field
    residual while rank events/checkpoint manifest prove effective overrides.

## Boundaries

- Do not train or run optimizer steps.
- Do not run AIME2025/task243, corrected AIME, canary reruns, benchmark eval,
  export, endpoint, promotion, or FT-vs-base comparison.
- Do not use AIME2025 prompts or labels as trainable data.
- Do not reuse task255 artifacts.
- Do not delete shared files, especially under
  `/mnt/cephfs/data/processing/lei.song`.
- Do not push main, merge, approve #367 directly, rewrite worker_3 branch, or
  modify product code.
- Read files, run static git/artifact/checksum inspection commands, and write
  review docs/status only.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_4/task305_qwen_aime_v11_30b_task304_canary_review_s1`.
- Review report:
  `workspace/tasks/task305_qwen_aime_v11_30b_task304_canary_review_s1/task304_canary_review_report.md`.
- Mailbox report to lead with:
  - exact #367 head reviewed;
  - branch/head/PR or mailbox-only status;
  - commands used and output summary;
  - artifact paths and checksum verification results;
  - PR diff scope plus `d8e58461..a38abd53` and `773aff2c..a38abd53`
    assessments;
  - canary metrics and checkpoint-load proof;
  - prompt-provenance/decontam/boundary verification;
  - approve/request-changes/block decision;
  - residual risks and whether lead may accept task304 only as a non-AIME
    canary before a later separate AIME task.

## Acceptance Criteria

- APPROVE: #367 exact head and task304 artifacts are internally consistent;
  canary metrics/checksums/prompt provenance/checkpoint-load proof pass; no
  forbidden action is observed; residuals are explicitly carried; and evidence
  is sufficient only for lead to consider a later separate corrected AIME
  FT-vs-base task.
- REQUEST_CHANGES: PR/report/artifacts likely represent a valid canary but
  missing or inconsistent head evidence, checksums, prompt provenance, metrics,
  boundary wording, residuals, or schema interpretation prevents acceptance.
- BLOCK: artifact checksums or metrics fail, PR scope is unsafe, checkpoint load
  proof is invalid, AIME/task243/export/endpoint/promotion/training/task255/
  shared-deletion boundary is violated, or the evidence makes an unsupported
  benchmark/promotion claim.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Related PR: #367
- Related tasks: task301, task303, task304
- Current main: `c94216b04bc3d71577391883d0cb76aa8c95e621`
- Next gate: corrected AIME2025 same-harness 30B FT-vs-base comparison remains
  blocked until task304 is accepted through this independent review and lead
  creates a separate AIME evaluation task.
