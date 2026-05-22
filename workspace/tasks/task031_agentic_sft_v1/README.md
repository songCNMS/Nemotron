# task031_agentic_sft_v1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_1 -->

Session 1 scaffold for the Agentic SFT v1 supervision builder contract.

Scope:
- Add a sandbox-only schema/helper near the M1 Agentic SFT preparation code.
- Preserve multi-turn tool calls and tool observations in repair-supervision
  examples.
- Read local/synthetic task032 `LocalRolloutStore` records as the failure
  rollout source.
- Record self-correction, failure-repair, and compact-reasoning metadata at the
  builder-contract level.

Acceptance:
- Focused pytest for schema shape, failed rollout selection, multi-turn
  observation handling, compact reasoning metadata, and LocalRolloutStore input.
- Run any directly affected M1 Agentic SFT tests that remain sandbox-runnable.
- `python -m py_compile` on new/modified modules.
- `git diff --check`.

Out of scope for Session 1:
- task013 cluster SFT loss/run verification.
- task070 and task026 live cross-harness runtime/data collection.
- OpenHands/OpenCode/Codex production traces.
- Real failure rollout mining.
- Packed SFT generation at scale and cluster training.
- W&B/lineage publication.
- Eval gate against live M1/M2 checkpoints.
