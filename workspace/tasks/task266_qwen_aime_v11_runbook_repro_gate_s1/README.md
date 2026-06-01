# task266_qwen_aime_v11_runbook_repro_gate_s1 - V11 runbook and reproducibility gate

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemotron_worker_5,SESSION=1 -->

## Background

The V10 task255 artifact failed below base and is invalidated. V11 needs a
single runbook that ties together repaired data/packing, base-load proof,
nonzero-LR pilot schedule, canary preflight, same-harness AIME comparison, and
resource boundaries before any new Qwen3-4B pilot can be judged.

## Goal

Create a V11 artifact/runbook/reproducibility gate that tells lead exactly what
artifacts, commands, paths, hashes, and review evidence must exist before each
stage moves forward.

## Scope

- Start from current `origin/main` after #333 merge commit
  `513fefa1f1ace94302b56413769c78fb7224624c`.
- Build a runbook matrix for task262/task263/task264/task265 evidence.
- Preserve project resource rules:
  - code/debug runs happen on remote node `NemTron`;
  - code must be synced to `/root` before debug on `NemTron`;
  - Qwen3-4B debug checkpoint is
    `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`;
  - downloads happen locally on CPU first, then copy to `NemTron`;
  - `/mnt/cephfs/data/processing/lei.song` is shared and existing files must
    never be deleted.
- Define stage gates:
  - data/packing ready;
  - base-load/import proof ready;
  - non-AIME canary ready;
  - bounded Qwen3-4B pilot allowed;
  - same-harness AIME comparison allowed;
  - promotion/non-regression decision.
- Record exact first measurable V11 go/no-go: a new Qwen3-4B FT candidate can
  only be considered if it has positive base-load/import proof, nonzero LR
  training evidence, canary pass, reviewer-readable artifacts, and same-harness
  AIME25 `ft_exact_normalized_accuracy >= 11/30`.

## Boundaries

- Do not train, eval, export, launch endpoints, merge, or alter worker branches.
- Do not authorize 30B/8-GPU or promotion.
- Do not put AIME2025 prompts/labels into trainable artifacts.
- Do not delete or overwrite shared processing files.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_5/task266_qwen_aime_v11_runbook_repro_gate_s1`.
- PR to `main` if runbook docs are committed.
- Task-owned output root:
  `/work-agents/intern_nemotron_worker_5/outputs/task266_qwen_aime_v11_runbook_repro_gate_s1/`.
- Runbook/report with:
  - required artifacts and hashes by task;
  - command templates and host/resource expectations;
  - go/no-go matrix with HOLD/BLOCK/PASS semantics;
  - exact dependencies and ordering;
  - residual risks and missing evidence;
  - explicit no-AIME-train-data, no promotion, no 30B/8-GPU, and no shared
    deletion confirmation.

## Acceptance Criteria

- PASS: lead can use the runbook to decide whether V11 may proceed from data
  repair to bounded Qwen3-4B pilot, then to task243 comparison, without relying
  on memory or informal artifact paths.
- REQUEST-CHANGES/BLOCK: any missing artifact path, stale upstream task, unclear
  command, resource blocker, or gate ambiguity is documented with owner and
  remediation.
- This task is documentation/repro gate evidence only and does not authorize
  training, eval, promotion, or scale-up by itself.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_5`
- Related tasks: task262, task263, task264, task265, task260, task261
- First gate: V11 runbook with concrete artifact and go/no-go matrix.
