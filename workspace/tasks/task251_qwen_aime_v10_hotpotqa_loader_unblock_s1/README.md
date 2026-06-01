# task251_qwen_aime_v10_hotpotqa_loader_unblock_s1 - HotpotQA loader unblock

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_2,SESSION=0 -->

## Background

task248 reached Qwen3-4B V10 pilot prep but stopped before complete local data
prep. PR #327 merged the worker report as `PARTIAL_PREP_BLOCKED`: the generated
planner artifacts exist, but local M0 prep stops on Hugging Face `datasets`
`trust_remote_code` incompatibility for `hotpotqa/hotpot_qa`.

The accepted base score remains Qwen3-4B AIME2025 corrected 30x1
`11/30 = 0.36666666666666664`; no candidate FT checkpoint/export/eval artifact
exists yet.

## Goal

Create the smallest worker-owned data-source/config workaround that lets the
task248 Qwen3-4B V10 local prep proceed past `hotpotqa/hotpot_qa`, while keeping
AIME2025 held out and preserving the corrected same-harness non-regression gate.

## Scope

- Start from current `origin/main` after #327 merge commit
  `419c8b9fe6415d13ba48c5130a9ecf5e816ceb8e`.
- Keep Qwen3-4B model/tokenizer path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Prefer a task-owned standard-format HotpotQA cache or registry override; if
  using the proposed pinned HotpotQA revision
  `1908d6afbbead072334abe2965f91bd2709910ab`, record source path, row counts,
  split mapping, and checksums.
- Reuse task248 generated scripts when possible, but write new task251 logs and
  manifests under:
  `/work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/`.
- If the workaround succeeds, update the task248 readiness report with the new
  artifact paths and exact next step for pilot continuation.

## Boundaries

- Do not train on AIME2025 prompts or labels; AIME2025 remains eval/decontam
  only.
- Do not delete or overwrite existing files under
  `/mnt/cephfs/data/processing/lei.song`.
- Do not launch 30B/8-GPU scale.
- Do not claim FT promotion or go/no-go pass.
- Do not run task243 base-vs-FT comparison until a real candidate FT artifact
  exists.
- Stop before NemTron training or FT live eval unless lead explicitly clears
  continuation after local prep artifacts are valid.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_2/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1`.
- PR to `main` for any repo config/script/doc changes needed by the workaround.
- Task report:
  `workspace/tasks/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/hotpotqa_loader_unblock_report.md`.
- Task-owned output directory with:
  - cache or registry manifest;
  - row counts and checksums;
  - exact commands and environment;
  - local prep logs;
  - explicit pass/fail result for getting past the HotpotQA blocker.
- Mailbox report with branch/head/PR, artifact paths, commands run, and whether
  task248 outputs are ready for lead review before any training continuation.

## Acceptance Criteria

- Local prep either completes through the HotpotQA stage with reproducible
  manifests, or reports the next precise blocker with logs.
- The workaround avoids unsupported `trust_remote_code` reliance for
  `hotpotqa/hotpot_qa`.
- AIME2025 prompt/label leakage into trainable rows is not introduced.
- Qwen tokenizer-native chat-template packing settings remain
  `enable_thinking=false` and `truncate_history_thinking=false`.
- The global gate remains `NO-GO/HOLD` until task248 produces candidate FT
  artifacts and task243 proves same-harness FT non-regression against the
  accepted 11/30 base.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Depends on: task248, PR #327, task246, task247
- First gate: task251 local prep unblock evidence only; no FT judgment and no
  30B/8-GPU scale.
