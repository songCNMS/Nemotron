# task112_benchmark_alignment_local_artifact_fingerprint_s1 - Benchmark alignment local artifact fingerprint gate

<!-- METADATA:STATUS=InReview,ASSIGNEE=intern_nem_dev_3,SESSION=15 -->

## Background

Task109 made the Qwen eval reproduction gate require SHA256 fingerprints for
local raw artifact evidence. The benchmark alignment ledger reused only the raw
path existence helper, so future local benchmark-improvement evidence could
pass with mutable local files and no content fingerprint.

## Goals

- Reuse the Qwen local raw-artifact SHA256 validator in benchmark alignment.
- Require exact-path SHA256 mappings for local benchmark alignment
  `raw_artifact_paths`.
- Preserve remote `vm4vpn:` / `vpn:` artifact behavior through
  `artifact_check.status: pm_verified`.
- Keep the current production benchmark alignment ledger valid.

## Out Of Scope

- Live benchmark/eval runs, endpoint calls, remote artifact access, W&B,
  cluster jobs, deployment, promotion, direct `main` or `master` push, and
  self-merge.

## Acceptance Criteria

- [x] Branch created from `origin/main`
  `4bb920fd0e942a4d807394893c8bba5f2bb87952`.
- [x] Production benchmark alignment ledger validates.
- [x] Synthetic local raw artifact evidence without `raw_artifact_sha256`
  fails.
- [x] Synthetic stale/wrong local SHA fails.
- [x] Remote-only evidence remains valid with PM-verified metadata and no local
  SHA mapping.
- [x] Focused pytest, py_compile, Ruff, structured probe, and `git diff --check`
  pass.
- [x] PR opened to `main`.

## PR

- https://github.com/songCNMS/Nemotron/pull/217
