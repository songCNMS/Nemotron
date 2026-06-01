# task241_qwen_aime_v10_sidecar_data_s1 - Qwen AIME V10 sidecar data

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_1,SESSION=0 -->

## Background

Supervisor priority is to improve Qwen fine-tuning performance on AIME 2025 without promoting any fine-tuned checkpoint that scores below the same base model under the same corrected AIME 2025 evaluator/protocol.

Reuse existing task071/task075/task076 history. PR #178 and PR #183 are merged. V7 30B-A3B passed the corrected gate with AIME25 `0.21`; V8 failed AIME25 at `0.19666666666666666` by regressing `aime_06`; corrected V9 fixed a checkpoint-root bug but still failed `aime_06` with wrong modes `640` and `830`. Task076 concludes the next data step should be a V10-style run-length DP/counting-recursion sidecar or weighting patch, not another unfocused 30B run.

## Goal

Implement the data-prep side of a decontaminated V10 AIME-style hard-math sidecar focused on run-length DP, counting recurrences, constrained binary strings, no-consecutive/run-length constraints, and related combinatorics patterns.

## Scope

- Own data-pipeline changes in `src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py`.
- Preserve tokenizer-native Qwen chat-template packing: `chat_template=tokenizer`, `enable_thinking=false`, `truncate_history_thinking=false`.
- Preserve existing V7/V8/V9 strategies while adding a separate V10 strategy or clearly scoped weighting extension.
- Require decontamination against AIME25/HMMT/MATH heldout prompts. AIME 2025 prompts and labels may only be used as held-out eval/decontamination corpus, never as training or answer-supervision rows.
- Add focused tests for V10 row selection, sidecar bucket counts, decontamination enforcement, and no AIME25 training leakage.

## Boundaries

- Do not push `main` or self-merge.
- Do not train 30B or run 8-GPU scale.
- Do not delete any existing files under `/mnt/cephfs/data/processing/lei.song`.
- Downloads, if any are required, happen on local CPU first and are copied to NemTron only when needed.
- Keep changes scoped to data-prep and tests unless lead explicitly approves a coordination change.

## Expected Output

- Worker branch: `intern_nemotron_worker_1/task241_qwen_aime_v10_sidecar_data_s1`.
- PR to `main` after local validation.
- A data report in this task directory summarizing V10 filters, source row counts, decontamination drops, sidecar row counts, and known residual risk.
- Mailbox report with branch, head SHA, PR URL, files touched, tests/checks run, and whether AIME25/HMMT/MATH heldouts remain excluded from training.

## Acceptance Criteria

- V10 sidecar selection is distinct from V9 and directly targets run-length DP/counting-recursion failure modes.
- Existing V7/V8/V9 tests remain covered or are updated without changing their semantics.
- AIME25 prompts/labels are not written to any train JSONL, sidecar train file, packed train shard, or supervision metadata.
- Data-prep output records decontamination corpus path, scanned rows, dropped rows, and sidecar counts.
- The work is ready for worker_2 to expose in planner scripts and worker_4 to independently audit.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_1`
- Depends on context from: task071, task075, task076, PR #178, PR #183
- First gate: no planner/training scale-up can use this sidecar until worker_4 confirms no AIME25 contamination and worker_3 defines the same-harness base-vs-FT scoring protocol.
