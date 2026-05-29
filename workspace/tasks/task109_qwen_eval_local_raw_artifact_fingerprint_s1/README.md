# task109_qwen_eval_local_raw_artifact_fingerprint_s1 - Qwen eval local raw artifact fingerprint gate

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3,SESSION=14 -->

## Background

`qwen_eval_repro_gate.py` validated local raw artifact path existence and
remote raw artifact PM verification, but local raw artifacts had no content
fingerprint. A local file mutation could change Qwen reproduction evidence
while the gate still passed.

## Goals

- Require SHA256 fingerprints for local `raw_artifact_paths`.
- Validate current local artifact content against those SHA256 fingerprints.
- Add fingerprints for the current local MMLU calibration artifacts.
- Preserve remote `vm4vpn:` / `vpn:` artifact handling via PM-verified
  metadata.
- Keep benchmark alignment ledger behavior unchanged.

## Out Of Scope

- Live benchmark/eval runs, endpoints, W&B, cluster jobs, deployment,
  promotion, direct `main` or `master` push, and self-merge.

## Acceptance Criteria

- [x] Branch created from `origin/main`
  `ac90f15ee5dfbbb9a35ef7f3753581632e1d4d0e`.
- [x] Current local MMLU calibration artifacts have recorded SHA256
  fingerprints in `qwen_eval_repro_gate.yaml`.
- [x] Missing and stale local fingerprints fail validation.
- [x] Remote artifact refs continue to rely on PM-verified metadata.
- [x] Focused pytest, py_compile, Ruff, structured probe, and `git diff --check` pass.
- [ ] PR opened to `main`.

## PR

- Pending
