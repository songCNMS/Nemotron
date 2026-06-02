# task268 Runtime Probe Report

- Disposition: `NEMTRON_BRIDGE_RUNTIME_BLOCKED`
- Generated artifact run: `20260602T002457Z`
- Repo head used for probe: `9a9619f05d1fc93ec188b483fa6edd0c2af3bb1a`
- Base main: `8fb1a1cb042fca0a0ca3491363fb0e5616909010`
- Host: `lg-cmc-b7r201-n09u29-cpu-000191`
- Requested image: `nvcr.io/nvidia/nemo:26.02.nemotron_3_super`

## Commands

```bash
python3 -m py_compile workspace/tasks/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/build_task268_bridge_runtime_probe.py
python3 workspace/tasks/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/build_task268_bridge_runtime_probe.py --hash-model-shards
```

Generated probe scripts:

- `/work-agents/intern_nemotron_worker_2/outputs/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/scripts/run_bridge_import_probe_20260602T002457Z.sh`
- `/work-agents/intern_nemotron_worker_2/outputs/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/scripts/run_fail_closed_preflight_20260602T002457Z.sh`

## Result

- Repo sync to `/root/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/run_20260602T002457Z/Nemotron`: rc `0`.
- Docker version probe: rc `1`; Docker client cannot connect to `/var/run/docker.sock`.
- Docker image inspect for `nvcr.io/nvidia/nemo:26.02.nemotron_3_super`: rc `1`; same daemon blocker.
- Local Bridge import from the synced `/root` repo: rc `1`, `ModuleNotFoundError: No module named 'megatron'`.
- Fail-closed preflight: rc `2`; blocked because `megatron`/`nemo` are missing, `megatron.bridge` errors, and no positive Bridge import/checkpoint-load proof exists.

## Artifacts

- Report:
  `/work-agents/intern_nemotron_worker_2/outputs/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/reports/task268_bridge_runtime_report_20260602T002457Z.md`
  sha256 `77f26941742583e028cacc0b93764bb834950a42567cd18ba26aa3ecd28aee80`
- Manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/manifests/task268_bridge_runtime_manifest_20260602T002457Z.json`
  sha256 `080bd46eedd9650efc2ca3317be01d826298601543c6d36056f45c51bb3dd001`
- Inventory:
  `/work-agents/intern_nemotron_worker_2/outputs/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/manifests/artifact_inventory_20260602T002457Z.sha256`
  sha256 `37a7886cf4336c43cc657c27587b18b918041cc44221e8889bcebe9208fb2d92`

The earlier `20260602T002335Z` artifact set should not be used as final
checksum evidence: manifest/report were hashed before their final rewrite,
which caused the internal artifact table to disagree with sidecars. The helper
was fixed and rerun; the `20260602T002457Z` inventory validates with
`sha256sum -c`.

## Qwen3-4B Base

- Base path: `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`
- Required-file missing count: `0`
- Safetensor shards: `3`; total bytes `8044982000`
- Core file and safetensor shard hashes are recorded in the full report and manifest.

## Boundary Confirmation

No SFT training, nonzero-LR smoke, export, endpoint serving, live AIME/task243
eval, promotion/go-no-go, task255 reuse, AIME2025 train prompt/label use,
30B/8-GPU launch, or shared deletion/overwrite was performed.

## Smallest Remediation

Provide a task-owned NemTron/NeMo/Megatron-Bridge runtime with Docker daemon
access or a preloaded/launchable `nvcr.io/nvidia/nemo:26.02.nemotron_3_super`
image, then rerun the generated Bridge import and fail-closed preflight scripts.
No downstream training/eval/export step should proceed without lead clearance.
