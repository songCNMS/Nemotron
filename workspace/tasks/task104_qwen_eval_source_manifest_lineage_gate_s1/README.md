# task104_qwen_eval_source_manifest_lineage_gate_s1 - Qwen eval source manifest lineage gate

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3,SESSION=13 -->

## Background

`qwen_eval_repro_gate.py` validated raw artifacts and remote artifact checks,
but source manifests were only checked as non-empty strings. That allowed an
absolute workstation path, typo, or missing repo file in the production gate
YAML to pass validator checks.

## Goals

- Require Qwen eval repro gate `source_manifests` to be repo-relative existing
  files.
- Apply the same repo-relative existing-file rule to evidence-record
  `source_manifest` lineage fields.
- Add non-skip synthetic tests for absolute and missing source-manifest paths.
- Keep the current production gate source manifests valid.

## Out Of Scope

- Live benchmark execution, endpoint calls, W&B, cluster jobs, deployment,
  promotion, direct `main` or `master` push, and self-merge.

## Acceptance Criteria

- [x] Branch created from `origin/main`
  `efcf0e6f5b5c043cc4c9b701d4faabe63ce69156`.
- [x] Production validator rejects absolute source manifest paths.
- [x] Production validator rejects missing repo-relative source manifest paths.
- [x] Current production source manifests are repo-relative existing files.
- [x] Focused pytest, py_compile, Ruff, structured probe, and `git diff --check` pass.
- [ ] PR opened to `main`.

## PR

- Pending
