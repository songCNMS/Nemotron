# task272_qwen_aime_v11_post_bridge_pilot_plan_s1 - Post-Bridge pilot readiness plan

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_2,SESSION=1 -->

## Background

Coordinator Session 40 appears to clear the prior NemTron runtime blocker for a
no-training Qwen3-4B Bridge import/preflight proof. The global Qwen AIME gate is
still `NO-GO/HOLD`: there is no new V11 FT checkpoint, no same-harness FT-vs-base
AIME comparison, no promotion clearance, and no 30B/8-GPU clearance.

## Goal

Prepare a worker-owned, no-training readiness plan for the next Qwen3-4B V11
pilot step after task271 independently reviews the Bridge proof.

## Scope

- Review task262/task263/task264/task266/task268/task270 outcomes and Session 40
  evidence.
- Identify the exact next worker-executable route from positive Bridge import
  proof toward a Qwen3-4B V11 pilot, including required commands, environment,
  dependency gaps, and artifact paths.
- Explicitly assess whether missing `hydra` blocks planner/training launch
  scripts or only unrelated paths.
- Propose any needed branch/PR changes for planner/smoke launch scripts or
  runbooks, without running training.

## Boundaries

- Do not run SFT training, nonzero-LR smoke, live AIME/task243 eval, export,
  endpoint, promotion, task255 reuse, AIME2025 train data, 30B/8-GPU, merge, or
  main push.
- Do not claim the Session 40 proof is accepted until task271 and lead gate
  accept it.
- Do not delete or overwrite shared files.

## Expected Output

- Branch:
  `intern_nemotron_worker_2/task272_qwen_aime_v11_post_bridge_pilot_plan_s1`.
- PR if repo-visible planner/runbook/status changes are made; otherwise mailbox
  report is acceptable.
- Mailbox report with exact next-step plan, dependencies, command skeleton,
  artifact paths, task271 dependency, risks, and boundary confirmation.

## Session 1 Closeout

Disposition: `PLAN_READY_HOLD_TASK271_LEAD_GATE`.

- Report:
  `workspace/tasks/task272_qwen_aime_v11_post_bridge_pilot_plan_s1/post_bridge_pilot_readiness_plan.md`.
- Branch:
  `intern_nemotron_worker_2/task272_qwen_aime_v11_post_bridge_pilot_plan_s1`.
- Session 40 read-only Bridge evidence was inspected from
  `/work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z/`.
  The observed logs contain `TASK270_RUNTIME_SYMBOL_PREFLIGHT=PASS`,
  `IMPORT_DONE`, `BRIDGE_IMPORT_RC=0`, and
  `TASK270_FAIL_CLOSED_PREFLIGHT=PASS`. Acceptance of that proof remains gated
  on task271 and lead review.
- Current next blocking dependency before any pilot execution is V11 packed data:
  task262 has a V11 blend plan and audit evidence, but no accepted fresh V11
  packed Qwen train/valid root. The older task253 packed split audit records a
  train mismatch: intended 15 shards / 113 rows, exposed 8 shards / 79 rows.
- `hydra` classification: not a blocker for local planner help or for the
  observed Session 40 Bridge import evidence; still a residual launch-risk item
  for any future Megatron-Bridge/Hydra-style training command until an
  authorized no-training config/import preflight proves the exact path.
- No SFT training, nonzero-LR smoke, live AIME/task243 eval, export, endpoint,
  promotion, task255 reuse, AIME2025 train data, 30B/8-GPU, main push, merge, or
  shared deletion was performed.

## Acceptance Criteria

- PASS: a bounded, no-training pilot readiness path is documented and any
  remaining blockers are exact.
- BLOCK: downstream launch readiness is still impossible due a precise missing
  dependency/resource.
- FAIL: any training/eval/promotion/AIME2025 train-data/30B action occurs.
