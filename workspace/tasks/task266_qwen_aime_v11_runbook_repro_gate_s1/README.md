# task266_qwen_aime_v11_runbook_repro_gate_s1 - V11 runbook and reproducibility gate

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_5,SESSION=1 -->

## Background

The V10 task255 artifact failed below base and is invalidated. V11 needs a
single runbook that ties together repaired data/packing, base-load proof,
nonzero-LR pilot schedule, canary preflight, same-harness AIME comparison, and
resource boundaries before any new Qwen3-4B pilot can be judged.

## Goal

Create a V11 artifact/runbook/reproducibility gate that tells lead exactly what
artifacts, commands, paths, hashes, and review evidence must exist before each
stage moves forward.

## Session 1 Closeout

- Report:
  `workspace/tasks/task266_qwen_aime_v11_runbook_repro_gate_s1/v11_runbook_repro_gate_report.md`.
- Task-owned output copy:
  `/work-agents/intern_nemotron_worker_5/outputs/task266_qwen_aime_v11_runbook_repro_gate_s1/v11_runbook_repro_gate_report.md`.
- Report sha256:
  `12f892f98ec57b696619be6615ad2454e6e7889529614af28c1f1f50b4dd933b`.
- Recommendation: task266 PASS as a static runbook/repro gate; V11 execution
  remains HOLD/NO-GO because task262/#336 and task264/#335 are merged static
  gates only, task263 still lacks base-load/import proof, task265 is
  mailbox-only evidence in this repo, and no V11 candidate/pilot/comparison
  artifact exists.
- Current visible upstream state:
  - task262 PR #336 MERGED at head
    `8fd3ff6065290b850c98db5f7abff91aa6880967`, merge commit
    `2ca6541c275d1eb64068e665af24147a796c818a`; substantive repair
    `0f825b9357a2a8f7814f693ea4c27027c5fbdd31`; final-answer n-gram evidence
    commit `5e431f4939799ae52c7d2002682352f2f2df6f3b`; static data/packing
    repair report, final-answer n-gram decontam PASS artifacts, and output
    bundle exist;
  - task263 branch `4af57e0e61703a063c1ef42def44119a7eea5cf9`, no PR, local
    `megatron`/`megatron.bridge` blocker recorded and no NemTron proof yet;
  - task264 PR #335 MERGED at
    `9d9285fd77820a5187440fbc2234dc36eb56942d`, merge commit
    `98e8aad39af9e705feed581e0ff9f8814073e2d8`, with official static
    canary/retention closeout;
  - task265 remote branch remains
    `ca5ea1c405ef142ee51a43fcbab477a2958e48dc`, with no PR or repo-visible
    task265 report; worker_4 status records mailbox-only matrix refresh id
    `7e718a2c0ea746ed81352db5b5b6fe57`.
- Boundaries kept: no training, eval, export, endpoint launch, merge,
  promotion, 30B/8-GPU authorization, AIME2025 train-data use, worker branch
  alteration, or shared deletion.

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
