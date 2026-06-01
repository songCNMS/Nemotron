# task262_qwen_aime_v11_data_split_sidecar_s1 - V11 data split and sidecar repair

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_1,SESSION=0 -->

## Background

task260/#332 and task261/#333 invalidated the task255 Qwen3-4B pilot. The
task261 data audit found that task253 intended 15 dataset-qualified train shard
entries, but the exposed `splits/train` path presented only 8 basename symlinks,
omitting M0 shards 5-6 and hard-math shards 0-4. The run therefore trained on
79 rows and only 3 hard-math rows, while AIME2025 remained held out.

## Goal

Build a V11 data/packing repair that preserves dataset-qualified shard identity,
removes the basename-collision risk, and rebuilds the decontaminated hard-math
and final-answer sidecar inputs for a future Qwen3-4B pilot.

## Scope

- Start from current `origin/main` after #333 merge commit
  `513fefa1f1ace94302b56413769c78fb7224624c`.
- Inspect the task253/task251 packing artifacts and the current data prep code
  that materializes `packed_qwen/splits`.
- Fix or propose the minimal code/config/docs change needed so exposed train and
  valid splits preserve dataset-qualified shard identity or otherwise cannot
  collide on shard basenames.
- Add or update manifest assertions that compare intended blend entries with
  exposed split rows/tokens/shards before training can start.
- Rebuild or document the V11 hard-math/final-answer sidecar plan using only
  decontaminated non-heldout sources. Include all reviewed hard-math rows and
  intentional final-answer supervision weighting.
- Preserve Qwen tokenizer-native packing, `enable_thinking=false`, and
  `truncate_history_thinking=false`.

## Boundaries

- Do not train, export, launch endpoints, run AIME/task243 eval, promote, or
  clear 30B/8-GPU.
- Do not include AIME2025 prompts or labels in trainable data. AIME2025 may be
  used only as held-out eval/decontamination corpus.
- Do not delete or overwrite existing files under
  `/mnt/cephfs/data/processing/lei.song`.
- Do not reuse task255 checkpoint/export as a training starting point.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_1/task262_qwen_aime_v11_data_split_sidecar_s1`.
- PR to `main` if code/config/docs change. If no code change is needed, provide
  a docs/artifact PR or mailbox-only blocker report with exact evidence.
- Task-owned output root:
  `/work-agents/intern_nemotron_worker_1/outputs/task262_qwen_aime_v11_data_split_sidecar_s1/`.
- Report containing:
  - branch/head/PR or blocker status;
  - files/configs touched;
  - input artifact paths and checksums used for task251/task253 review;
  - intended versus exposed split row/token/shard counts;
  - hard-math and final-answer sidecar sources, row counts, and checksums;
  - decontamination evidence against AIME25/HMMT/MATH heldouts;
  - commands run and environment;
  - explicit no-AIME-train-data, no training/eval, no promotion, no 30B/8-GPU,
    and no shared deletion confirmation.

## Acceptance Criteria

- PASS: V11 split materialization is demonstrably collision-free or has a
  fail-closed assertion that prevents training on incomplete exposed shards.
- PASS: V11 sidecar plan/artifact intentionally includes reviewed hard-math and
  final-answer supervision from decontaminated non-heldout sources.
- BLOCK: exact missing source, dependency, permission, or data-integrity blocker
  is reported with commands/logs and a remediation path.
- This task does not authorize training. It only supplies reviewed V11 data and
  packing readiness evidence for later task263/task266 gates.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_1`
- Related tasks: task246, task251, task253, task254, task260, task261
- Related PRs: #328, #332, #333
- First gate: collision-free V11 data/packing evidence or exact blocker.
