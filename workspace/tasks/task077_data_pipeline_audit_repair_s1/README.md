# task077_data_pipeline_audit_repair_s1 - Data pipeline audit repair

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_1 -->

## Background

PM assigned a PR-sized lane to audit and repair the Super3 M1 Agentic SFT data processing and Qwen scale-up data-prep path. The seed risk is that `agentic_v0` defaults to the Nemotron tokenizer and Super3 template, while Qwen target runs depend on overrides to avoid packing Qwen training rows with Super3 defaults.

## Goals

- Add a Qwen-specific data-prep profile and validator so Qwen target packing cannot silently fall back to Super3/Nemotron defaults.
- Keep Qwen planner scripts pinned to the Qwen-safe profile and record that invariant in the generated manifest/report.
- Improve local/static M1 output audit metadata for source pins, license/source metadata, split overlap, duplicate/near-duplicate prompts, deterministic file fingerprints, decontamination, and curriculum visibility.
- Keep changes scoped to data prep, planner, and related tests.

## Acceptance Criteria

- [ ] Qwen scale-up planner emits a Qwen-safe SFT data-prep config path.
- [ ] Qwen data-prep config validation rejects Super3 template or Nemotron tokenizer drift.
- [ ] M1 Agentic SFT manifests/report include source metadata, split routing, duplicate/near-duplicate, and output fingerprint audit blocks.
- [ ] Relevant Super3 data-prep, Qwen planner, contamination, registry validation, compile, and whitespace checks pass.
- [ ] PR opened against `main`; PM receives base SHA, head SHA, changed files, and tests.
