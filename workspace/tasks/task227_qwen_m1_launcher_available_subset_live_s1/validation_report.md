# Validation Report

Artifact root: `/mnt/cephfs/data/processing/nemotron-live-validation/task227`

Status: `HOLD_CLEANED_UP`

Base/product commit: `1d037329f5a02cdc04f2a09a16e7342721be4c87`
Branch: `intern_nem_dev_2/task227_qwen_m1_launcher_available_subset_live_s1`

## Accepted Evidence

- PASS: read-only local/VPN/NemTron preflight completed before launch.
  Logs:
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task227/preflight/00_local_preflight.log`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task227/preflight/01_vpn_preflight.log`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task227/preflight/02_nemtron_preflight.log`
- PASS: task225 official runtime probe imported `nemo_evaluator_launcher` and found the launcher CLI.
  Log: `/mnt/cephfs/data/processing/nemotron-live-validation/task227/official_runtime/00_task225_runtime_probe.log`
- PASS: exactly one task227-owned SGLang endpoint was launched on NemTron at `:13000`.
  Logs:
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task227/endpoint/00_sglang_launch.log`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task227/endpoint/01_sglang_readiness.log`
- PASS: sanitized endpoint smoke returned HTTP 200 with content `OK` and no benchmark prompt/secrets.
  Logs:
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task227/smoke/00_sanitized_endpoint_smoke.log`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task227/smoke/00_sanitized_endpoint_summary.json`

## HOLD Reason

The official corrected-math smoke and 14-task M1 launcher-available subset were not run. PM corrected the boundary after a VPN probe used:

```bash
docker run --rm --network host curlimages/curl:latest ...
```

That probe attempted/pulled `curlimages/curl:latest` because only `curlimages/curl:8.10.1` had been listed as pre-existing. This is recorded as a boundary risk/accidental pull attempt. After the correction, no further Docker image pulls, package installs, builds, downloads, or runtime/environment mutation were performed.

Because the required evaluator client images were not verified as pre-existing under the corrected boundary, the safe action was HOLD and cleanup rather than running the official launcher. PM had approved `deployment.type=none` plus `target.api_endpoint.*` for the existing endpoint, but the evaluator client container availability gate remained unresolved.

## Tunnel Evidence

- A task-owned SSH reverse tunnel attempt was prepared for VPN port `13127` to reach the existing NemTron SGLang endpoint.
- The long control-socket path attempt failed with a Unix-domain socket path-length error.
  Log: `/mnt/cephfs/data/processing/nemotron-live-validation/task227/endpoint_tunnel/02_vpn_reverse_tunnel_detached.log`
- A short control-socket tunnel process was created and then cleaned up after the boundary correction.
  Logs:
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task227/endpoint_tunnel/03_vpn_reverse_tunnel_detached_short_socket.log`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task227/endpoint_tunnel/04_cleanup_tunnel.log`
- VPN-side copied tunnel health artifact:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task227/vpn_copied_artifacts/endpoint_tunnel/01_tunnel_health.log`

## Cleanup

- PASS: task227-owned VPN tunnel listener on `127.0.0.1:13127` was removed.
  Log: `/mnt/cephfs/data/processing/nemotron-live-validation/task227/endpoint_tunnel/04_cleanup_tunnel.log`
- PASS: task227-owned SGLang process tree was terminated explicitly by PID on NemTron.
  Copied log: `/mnt/cephfs/data/processing/nemotron-live-validation/task227/nemtron_copied_artifacts/endpoint/03_cleanup_sglang_explicit_pids.log`
- PASS: post-cleanup NemTron verification found no SGLang process, no `:13000` listener, no H200 compute apps, and `:8000` still documented/untouched.
- Summary and artifact manifests:
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task227/summary/HOLD_CLEANUP_SUMMARY.txt`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task227/summary/artifact_manifest.txt`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task227/summary/key_artifact_sha256.txt`

## Not Run

- Official corrected-math smoke: not run.
- 14-task M1 launcher-available subset: not run.
- Five missing-mapping M1 targets, M2 targets, full 19/full 27: not run, per boundary.
