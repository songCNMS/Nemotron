# task264_qwen_aime_v11_eval_gate_canary_retention_s1 - V11 eval canary and retention gate

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemotron_worker_3,SESSION=1 -->

## Background

task260 showed task255 FT outputs were generation degeneration/corruption, not
an evaluator-only parser issue. The same corrected AIME harness parsed the base
Qwen3-4B on `23/30` rows and scored `11/30`, while task255 FT parsed `0/30`.
The inspected FT artifacts retained only metrics and `response_tail`, limiting
future forensics.

## Goal

Prepare the V11 same-harness evaluation gate so no AIME run is launched on a
corrupted artifact, and future eval artifacts retain enough deterministic
completion evidence for review.

## Scope

- Start from current `origin/main` after #333 merge commit
  `513fefa1f1ace94302b56413769c78fb7224624c`.
- Preserve the accepted Qwen3-4B base comparator:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`, corrected AIME25
  `30x1`, exact-normalized `11/30 = 0.36666666666666664`.
- Define or implement a non-AIME export-load canary gate for future V11 FT
  artifacts before task243/AIME comparison:
  - synthetic prompts only, not AIME2025 and not training rows;
  - require coherent text and a short numeric/final-answer style response;
  - record tokenizer/chat-template/generation config parity with base.
- Improve eval artifact retention plan or implementation so V11 AIME runs save
  full completions or a reviewer-safe deterministic transcript, not only
  `response_tail`.
- Keep score normalization tied to the same-harness base-vs-FT rule.

## Boundaries

- Do not run AIME/task243 live eval until a new accepted V11 candidate artifact
  exists and lead clears the comparison.
- Do not train, export, promote, or clear 30B/8-GPU.
- Do not put AIME2025 prompts or labels into trainable artifacts.
- If code changes are needed, keep them narrowly scoped to eval gate/canary or
  artifact retention.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_3/task264_qwen_aime_v11_eval_gate_canary_retention_s1`.
- PR to `main` if eval code/config/docs change.
- Task-owned output root:
  `/work-agents/intern_nemotron_worker_3/outputs/task264_qwen_aime_v11_eval_gate_canary_retention_s1/`.
- Report containing:
  - branch/head/PR or blocker status;
  - accepted base protocol and artifact paths;
  - canary prompt set source, hashes, and non-AIME/non-train confirmation;
  - artifact retention schema for full completions/debug transcript;
  - commands/checks run or exact blocker;
  - explicit no-training, no AIME live eval, no promotion, no 30B/8-GPU, and no
    AIME2025 train data confirmation.

## Acceptance Criteria

- PASS: future V11 FT artifacts must pass a non-AIME export-load canary before
  any same-harness AIME comparison is requested.
- PASS: V11 AIME eval artifacts will retain enough deterministic completion
  evidence to distinguish parser failure from generation corruption.
- PASS: same-harness FT promotion remains blocked unless FT exact-normalized
  AIME25 score is at least the accepted base under identical protocol.
- BLOCK: exact missing artifact, command, dependency, or code owner blocker is
  reported.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_3`
- Related tasks: task243, task247, task257, task260, task261
- Related PRs: #330, #332, #333
- First gate: canary/retention gate ready for the next V11 candidate; no live
  AIME eval yet.
