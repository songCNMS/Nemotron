# task033_env_scheduler

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_1 -->

Session 1 scaffold for the M2 environment scheduler quota/backpressure policy.

Scope:
- Build a sandbox-only scheduler interface under
  `src/nemotron/recipes/super3/milestones/m2_env_scheduler/`.
- Model fast/slow queue classification, including slow SWE/browser/GUI envs.
- Model per-env quotas, local backpressure signals, and deterministic next-item
  decisions against synthetic/local rollout records.
- Consume task032-style local rollout traces only as plain local records; no live
  rollout service is required.

Acceptance:
- Focused pytest for queue routing, quota exhaustion, backpressure, rollout
  signal summarization, and deterministic decisions.
- `python -m py_compile` on the new scheduler modules.
- `git diff --check`.

Out of scope for Session 1:
- task021 Session 4 launch path validation.
- Real Ray/NeMo-RL/vLLM/NeMo-Gym scheduler hookup.
- Kubernetes/cluster resource probes.
- Live queue workers.
- Retry/accounting integration.
- Production deployment.
