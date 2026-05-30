# task232_m2_resource_request_release_packet_s1

<!-- METADATA:STATUS=Complete,ASSIGNEE=intern_nem_dev_3,SESSION=1 -->

## Scope

- Convert task229's M2 runtime/asset inventory into a PM-ready release packet
  for all 8 M2 targets.
- Specify missing frozen Qwen3.5-122B-A10B baselines, asset paths,
  credentials/services, databases, sandboxes, env vars, acceptance criteria,
  minimal smoke commands, estimates, and residual risks.
- Keep this evidence/status/docs only.

## Boundaries

- No product code edits.
- No endpoint request, eval/benchmark launch, SGLang, Docker pull/build/run,
  package install/build/download, environment mutation, model copy, process
  kill, artifact upload, direct `main`/`master` push, or self-merge.

## Status

- Base/product commit: `1d037329f5a02cdc04f2a09a16e7342721be4c87`.
- Branch: `intern_nem_dev_3/task232_m2_resource_request_release_packet_s1`.
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task232`.
- Result: release packet complete; all 8 M2 targets remain HOLD pending
  resources and PM release.

## Artifacts

- `validation_report.md`
- `m2_resource_request_release_packet.json`
- `m2_resource_request_release_packet.yaml`
- `artifact_listing.txt`
- `commands/run_<target>_smoke_after_release.sh` for all 8 M2 targets
- `config_templates/<target>_smoke.yaml` for all 8 M2 targets
- `baseline_request_templates/<target>_qwen122b_baseline_manifest.json` for
  all 8 M2 targets

## Checks

- Structured packet probe passed for task id, 8 targets, and PM-ready summary
  sections.
- Secret scan produced false positives only; no secret values were recorded.
- `git diff --check` passed.
- `git diff --cached --check` passed.

## Blockers

- `M2_RELEASE_HELD`: no live smoke/full benchmark can run without fresh PM
  release.
- `M2_122B_BASELINES_MISSING`: all 8 targets require frozen
  Qwen3.5-122B-A10B baseline artifacts.
- `M2_RUN_VISIBLE_ASSETS_MISSING`: accepted assets/databases must be visible
  on the approved evaluator host.
- `M2_CREDENTIALS_AND_SANDBOXES_MISSING`: target-specific credentials,
  services, and sandboxes remain owner-provided resources.
