# task246_qwen_aime_v10_real_decontam_corpus_s1 - Real heldout decontam corpus

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_1,SESSION=2 -->

## Background

The V10 static foundation is now merged through PR #317, #318, #319, #320,
and #321. The first Qwen3-4B AIME go/no-go is still blocked because the planner
bundle only has a placeholder heldout decontamination corpus and placeholder
task241-derived M0 input.

The hard rule remains: AIME 2025 prompts and labels are held-out
eval/decontamination material only. They must not appear in train rows, sidecar
rows, packed shards, distillation prompts, or answer-supervision metadata.

## Goal

Produce or locate a lead-reviewable real heldout prompt corpus for
AIME25/HMMT/MATH decontamination, plus the real V10 M0 sidecar/data-prep input
path needed by the Qwen3-4B V10 pilot.

## Scope

- Own corpus/input discovery and data-prep artifact mapping for the next V10
  pilot.
- Use current `origin/main` after PR #321.
- Build a prompt-only heldout corpus if a trusted one does not already exist.
- Record source paths, row counts, prompt hash counts, duplicate handling,
  and exact output paths.
- Confirm the task242 placeholder corpus is replaced before any data prep can
  run.
- Confirm AIME25 labels/answers are not written to trainable outputs.

## Boundaries

- Do not push `main` or self-merge.
- Do not train, launch eval, or start endpoints.
- Do not delete existing files under `/mnt/cephfs/data/processing/lei.song`.
- Do not include AIME25 answer labels in trainable artifacts.
- Do not copy or publish private heldout labels beyond what is required for
  evaluator-owned heldout scoring.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_1/task246_qwen_aime_v10_real_decontam_corpus_s1`.
- PR to `main` if repo docs/scripts need to change; otherwise a docs/artifact
  PR with the report is acceptable.
- Task report in this directory named `real_decontam_corpus_report.md`.
- Task-owned output directory with manifest, corpus path, checksums, and row
  counts, for example:
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/`.
- Mailbox report with branch, head SHA, PR URL if any, artifact paths, counts,
  and blockers.

## Acceptance Criteria

- A lead-approved real heldout decontamination corpus path exists and is not
  the task242 placeholder.
- Corpus manifest records sources, counts, prompt hashes, and whether labels
  are absent or held behind evaluator-only paths.
- Real V10 M0/input path for task242 is identified or a precise blocker is
  reported.
- No existing shared processing files are deleted or overwritten.
- The output is ready for worker_2 to generate a real Qwen3-4B pilot bundle and
  for worker_4/worker_5 to independently audit.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_1`
- Depends on: task241, task242, task245, PR #320, PR #321
- First gate: task248 must not run local data prep until this task publishes a
  non-placeholder heldout corpus/input or reports an explicit blocker.

## Current Worker State

- Branch: `intern_nemotron_worker_1/task246_qwen_aime_v10_real_decontam_corpus_s1`.
- Base: current `origin/main` at
  `20973e78f196d7e5d71993f60dc74a3500223f5f`, after PR #321.
- Task docs source: `origin/intern_nemotron_lead/session1-recovery-task-docs`
  at `5d5e3fa`.
- Status: real heldout corpus and V10 M0 sidecar input produced; PR #325 is
  open for review.
- Output root:
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1`.
- Heldout corpus:
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl`
  (`560` rows, sha256
  `614b2b347d33c1ec00cfd2c33222c26ad1d99b8b837bd7e48ea11fd4fedae6f9`).
- V10 M0 input:
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar`
  (`8` train rows, `0` val rows).
- Leakage status: no AIME25 labels/prompts in M0 sidecar input; heldout corpus
  is prompt-only.
