# task094_benchmark_remote_artifact_verification_s1 - Benchmark remote artifact verification

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Background

`qwen_benchmark_alignment_ledger.yaml` records remote raw artifact references
with `vm4vpn:` paths. The benchmark alignment validator accepted any generic
artifact-check status, including `local_workspace_verified`, which is not a
strong enough claim for remote raw evidence.

## Goals

- Require `artifact_check.status: pm_verified` for benchmark alignment evidence
  records whose `raw_artifact_paths` include `vm4vpn:` or `vpn:` refs.
- Normalize the existing benchmark alignment ledger's remote artifact checks to
  describe PM-verified remote evidence rather than local workspace presence.
- Preserve evidence numbers, benchmark lists, raw artifact refs,
  parser/generation contracts, non-Qwen result manifests, and live-run surfaces.
- Add focused tests for rejection of remote raw refs with
  `local_workspace_verified` and acceptance of the current ledger.

## Out Of Scope

- Live benchmark execution, endpoint calls, W&B, cluster jobs, deployment,
  promotion, direct `main` or `master` pushes, and self-merge.

## Acceptance

- `PYTHONPATH=src python -m pytest -q tests/recipes/super3/test_qwen_eval_repro_gate.py` passes.
- `python -m py_compile` passes for the touched validator and test.
- Ruff passes for the touched validator and test.
- `git diff --check` and `git diff --cached --check` pass.
