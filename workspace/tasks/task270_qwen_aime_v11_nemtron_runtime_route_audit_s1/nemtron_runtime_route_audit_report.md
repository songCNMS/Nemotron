# task270 NemTron Runtime Route Audit Report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_5,SESSION=1 -->

## Decision

Recommendation: `BLOCK` for a current no-training rerun of task268 Bridge
import plus fail-closed preflight under worker_5's available permissions and
runtime access.

No complete task-owned `NeMo + Megatron-Bridge` runtime route is available from
the current local host, the `NemTron` SSH host, the visible preloaded-image
artifacts, or LTP/OpenPAI credentials. The smallest external action is to
provide one of these equivalent resources:

1. install or expose `nemo` in the existing `NemTron` Python environment that
   already imports `megatron.bridge.AutoBridge`, then run a task-owned `/root`
   sync and rerun the task268 import/preflight commands;
2. enable a Docker daemon or other launchable container runtime with
   `nvcr.io/nvidia/nemo:26.02.nemotron_3_super`, or another image that proves
   `megatron`, `megatron.bridge.AutoBridge.import_ckpt`, and `nemo`;
3. provide LTP/OpenPAI credentials plus a job template/image that contains the
   same `megatron.bridge` and `nemo` symbols and mounts the Qwen3-4B base path.

The existing `NemTron` Python environment is a useful partial route because
`AutoBridge.import_ckpt` is present, but it is not sufficient for the current
task268 fail-closed script because `nemo` is missing and the script requires
`megatron`, `megatron.bridge`, `nemo`, a `BRIDGE_IMPORT_RC=0` line, and a
positive import/checkpoint-load proof.

## Inputs Reviewed

- task270 README:
  `workspace/tasks/task270_qwen_aime_v11_nemtron_runtime_route_audit_s1/README.md`
- task266 V11 runbook:
  `workspace/tasks/task266_qwen_aime_v11_runbook_repro_gate_s1/v11_runbook_repro_gate_report.md`
- task263 base-load blocker report:
  `workspace/tasks/task263_qwen_aime_v11_base_load_planner_sanity_s1/v11_base_load_gate_report.md`
- task268 repo report:
  `workspace/tasks/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/runtime_probe_report.md`
- task268 final artifact report:
  `/work-agents/intern_nemotron_worker_2/outputs/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/reports/task268_bridge_runtime_report_20260602T002457Z.md`
- task268 final manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/manifests/task268_bridge_runtime_manifest_20260602T002457Z.json`
- task268 final inventory:
  `/work-agents/intern_nemotron_worker_2/outputs/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/manifests/artifact_inventory_20260602T002457Z.sha256`
- task268 generated import script:
  `/work-agents/intern_nemotron_worker_2/outputs/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/scripts/run_bridge_import_probe_20260602T002457Z.sh`
- task268 generated preflight script:
  `/work-agents/intern_nemotron_worker_2/outputs/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/scripts/run_fail_closed_preflight_20260602T002457Z.sh`

## Artifact Integrity Checks

Commands:

```bash
sha256sum \
  /work-agents/intern_nemotron_worker_2/outputs/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/reports/task268_bridge_runtime_report_20260602T002457Z.md \
  /work-agents/intern_nemotron_worker_2/outputs/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/manifests/task268_bridge_runtime_manifest_20260602T002457Z.json \
  /work-agents/intern_nemotron_worker_2/outputs/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/manifests/artifact_inventory_20260602T002457Z.sha256
sha256sum -c \
  /work-agents/intern_nemotron_worker_2/outputs/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/manifests/artifact_inventory_20260602T002457Z.sha256
```

Results:

- report sha256:
  `77f26941742583e028cacc0b93764bb834950a42567cd18ba26aa3ecd28aee80`
- manifest sha256:
  `080bd46eedd9650efc2ca3317be01d826298601543c6d36056f45c51bb3dd001`
- inventory sha256:
  `37a7886cf4336c43cc657c27587b18b918041cc44221e8889bcebe9208fb2d92`
- `sha256sum -c` result: all final `20260602T002457Z` artifacts listed in
  the inventory returned `OK`.

## Required Task268 Runtime Semantics

The repo import helper is:

`scripts/import_qwen3_4b_local_to_megatron.py`

It imports:

```python
from megatron.bridge import AutoBridge
```

and calls:

```python
AutoBridge.import_ckpt(
    args.hf_path,
    args.output_dir,
    torch_dtype=torch.bfloat16,
    device_map="cpu",
    trust_remote_code=True,
)
```

The task268 fail-closed preflight checks all of the following:

- `megatron` is import-discoverable;
- `megatron.bridge` is import-discoverable;
- `nemo` is import-discoverable;
- the Bridge import log contains `IMPORT_DONE` or a checkpoint-load success
  line;
- the Bridge import log contains `BRIDGE_IMPORT_RC=0`.

Therefore, `megatron.bridge` alone is not enough for the current task268
preflight contract.

## Runtime Probes

All probes below were read-only. No import checkpoint command, training,
nonzero-LR smoke, eval, export, endpoint, promotion, 30B/8-GPU job, or shared
deletion was run.

### Local Worker Host

Command summary:

```bash
python3 - <<'PY'
import importlib.util, socket, sys
print("HOST=" + socket.gethostname())
print("PYTHON=" + sys.executable)
for package in ("megatron", "megatron.bridge", "nemo",
                "torch", "transformers", "safetensors"):
    ...
PY
for c in docker podman singularity apptainer enroot nerdctl; do command -v "$c"; done
stat -c '%F %U:%G %a %n' /var/run/docker.sock
```

Observed:

- host: `lg-cmc-b7r201-n09u29-cpu-000191`
- python: `/usr/bin/python3`
- `megatron`: missing
- `megatron.bridge`: `ModuleNotFoundError: No module named 'megatron'`
- `nemo`: missing
- `torch`, `transformers`, `safetensors`: present
- `docker`: `/usr/local/bin/docker`
- `/var/run/docker.sock`: missing
- `podman`, `singularity`, `apptainer`, `enroot`, `nerdctl`: missing

Disposition: not a valid task268 rerun runtime.

### NemTron SSH Host

Command summary:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=no NemTron /bin/bash -s <<'REMOTE'
python3 - <<'PY'
import importlib.util, socket, sys
...
from megatron.bridge import AutoBridge
print("AUTOBRIDGE_IMPORT_CKPT=%s" % hasattr(AutoBridge, "import_ckpt"))
PY
for c in docker podman singularity apptainer enroot nerdctl; do command -v "$c"; done
stat -c '%F %U:%G %a %n' /var/run/docker.sock
REMOTE
```

Observed:

- host: `lg-cmc-b7r201-f08u26-h200-000126`
- python: `/usr/bin/python3`
- `megatron`: present
- `megatron.bridge`: present at
  `/usr/local/lib/python3.12/dist-packages/megatron/bridge/__init__.py`
- `AutoBridge.import_ckpt`: present
- `nemo`: missing
- `torch`, `transformers`, `safetensors`: present
- `docker`, `podman`, `singularity`, `apptainer`, `enroot`, `nerdctl`: missing
- `/var/run/docker.sock`: missing

Additional path check:

```bash
ssh NemTron 'for p in \
  /root/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/run_20260602T002457Z \
  /root/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/run_20260602T002457Z/Nemotron \
  /root/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/run_20260602T002457Z/Nemotron/scripts/import_qwen3_4b_local_to_megatron.py; do \
    test -e "$p" && stat -c "%F %U:%G %a %n" "$p" || echo "MISSING $p"; \
  done'
```

Observed: all three `task268` `/root` sync paths were missing on `NemTron`.

Disposition: partial Python route only. A future rerun needs both a fresh
task-owned `/root` repo sync and `nemo` or a complete container/runtime.

### LTP / OpenPAI

Command:

```bash
python3 /work-agents/Nemotron/workspace/.skill_sources/intern_agent_skills/intern_ltp_skill/scripts/ltp.py whoami
```

Observed:

- rc `2`
- `LTP_TOKEN` and `LTP_HOST` are missing, and no usable `~/.ltp_env` was found.

Disposition: LTP/OpenPAI route cannot be validated or submitted from this
session. The smallest action for that route is to provide credentials plus a
no-training job spec/image that contains `megatron.bridge` and `nemo`.

### Preloaded Image Or Container Artifacts

Bounded checks:

- runtime commands were absent as listed above;
- a broad image-file search over `/mnt/cephfs/data` was stopped after it did
  not yield a usable path within the bounded probe window;
- shallow checks of visible candidate directories were inspected:
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task233/images`
  - `/mnt/cephfs/data/processing/ltp_job_artifacts`
  - `/mnt/cephfs/data/processing/shared_models/nvidia`

Observed:

- `task233/images` contains retained image allowlist and inspect logs only;
- retained refs are `nvcr.io/nvidia/eval-factory/...:26.03`, including
  `nvcr.io/nvidia/eval-factory/nemo-skills:26.03`;
- the required task268 image
  `nvcr.io/nvidia/nemo:26.02.nemotron_3_super` is not listed there;
- no `.sif`, `.sqsh`, container tarball, or local runtime command was found in
  a form that worker_5 can launch;
- `ltp_job_artifacts` contains data fasttext/ray/text-clean tarballs, not a
  NeMo/Megatron-Bridge runtime;
- `shared_models/nvidia` contains model directories, not a launchable runtime.

Disposition: no visible preloaded image route.

## Qwen3-4B Base Path

The required base remains:

`/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`

Task268 final manifest records:

- missing required files: `0`
- safetensor shards: `3`
- total safetensor bytes: `8044982000`
- shard hashes:
  - `model-00001-of-00003.safetensors`
    `75311d91bb08cf0b882913da464a1e722a31fb44db35208663487efb7a3d8ed6`
  - `model-00002-of-00003.safetensors`
    `0b48adbb1f60e901153d91907ba11ce63bd4b8b584482e730f48808d055dfba1`
  - `model-00003-of-00003.safetensors`
    `7dd39ccca5e4de123c74c14af44c9bf2eb75df33b4614382af0134528e060d5d`

## Concrete Rerun Route After Resource Action

This is the bounded no-training protocol once one of the external runtime
actions above is provided. It creates only task-owned `/root` and output paths.

Assumptions:

- the runtime has `python3`, `torch`, `transformers`, `safetensors`,
  `megatron`, `megatron.bridge.AutoBridge.import_ckpt`, and `nemo`;
- `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507` is mounted
  read-only or read-accessible;
- any output path is task-owned and does not overwrite existing shared data;
- lead has authorized only this import/preflight rerun, not training or eval.

Commands:

```bash
TS=$(date -u +%Y%m%dT%H%M%SZ)
REMOTE_RUN=/root/task270_qwen_aime_v11_nemtron_runtime_route_audit_s1/rerun_${TS}
LOCAL_OUT=/work-agents/intern_nemotron_worker_5/outputs/task270_qwen_aime_v11_nemtron_runtime_route_audit_s1/rerun_${TS}
BASE=/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507

mkdir -p "${LOCAL_OUT}/logs" "${LOCAL_OUT}/manifests"
ssh NemTron "mkdir -p '${REMOTE_RUN}/logs' '${REMOTE_RUN}/qwen3_4b_bridge_import_iter0'"
rsync -a --exclude .git \
  /work-agents/intern_nemotron_worker_5/Nemotron/ \
  NemTron:${REMOTE_RUN}/Nemotron/

ssh NemTron /bin/bash -s <<REMOTE
set -euo pipefail
cd ${REMOTE_RUN}/Nemotron
export PYTHONPATH="\${PWD}/src\${PYTHONPATH:+:\${PYTHONPATH}}"
export SUPER3_M1_QWEN_HF_MODEL=${BASE}
python3 - <<PY
import importlib.util
from megatron.bridge import AutoBridge
assert importlib.util.find_spec(\"nemo\") is not None
assert hasattr(AutoBridge, \"import_ckpt\")
print(\"TASK270_RUNTIME_SYMBOL_PREFLIGHT=PASS\")
PY
set +e
python3 scripts/import_qwen3_4b_local_to_megatron.py \
  --hf-path ${BASE} \
  --output-dir ${REMOTE_RUN}/qwen3_4b_bridge_import_iter0 \
  > ${REMOTE_RUN}/logs/bridge_import_probe.log 2>&1
rc=\$?
set -e
echo BRIDGE_IMPORT_RC=\$rc >> ${REMOTE_RUN}/logs/bridge_import_probe.log
exit \$rc
REMOTE

ssh NemTron /bin/bash -s <<REMOTE
set -euo pipefail
cd ${REMOTE_RUN}/Nemotron
export PYTHONPATH="\${PWD}/src\${PYTHONPATH:+:\${PYTHONPATH}}"
python3 - <<PY > ${REMOTE_RUN}/logs/fail_closed_preflight.log 2>&1
import importlib.util
import re
from pathlib import Path

log = Path(\"${REMOTE_RUN}/logs/bridge_import_probe.log\")
errors = []
for package in (\"megatron\", \"megatron.bridge\", \"nemo\"):
    try:
        spec = importlib.util.find_spec(package)
    except Exception as exc:
        errors.append(f\"{package} import probe errored: {type(exc).__name__}: {exc}\")
        continue
    if spec is None:
        errors.append(f\"{package} is missing\")
if not log.is_file():
    errors.append(f\"missing Bridge import log: {log}\")
else:
    text = log.read_text(encoding=\"utf-8\", errors=\"replace\")
    if \"IMPORT_DONE\" not in text and not re.search(r\"successfully loaded checkpoint\", text, re.I):
        errors.append(\"no Bridge-approved import proof or positive checkpoint-load line found\")
    if \"BRIDGE_IMPORT_RC=0\" not in text:
        errors.append(\"Bridge import command did not complete with rc=0\")
if errors:
    print(\"TASK270_FAIL_CLOSED_PREFLIGHT=BLOCK\")
    for error in errors:
        print(f\"- {error}\")
    raise SystemExit(2)
print(\"TASK270_FAIL_CLOSED_PREFLIGHT=PASS\")
PY
REMOTE

rsync -a NemTron:${REMOTE_RUN}/logs/ "${LOCAL_OUT}/logs/"
rsync -a NemTron:${REMOTE_RUN}/qwen3_4b_bridge_import_iter0/ \
  "${LOCAL_OUT}/qwen3_4b_bridge_import_iter0/"
find "${LOCAL_OUT}" -type f -print0 | sort -z | xargs -0 sha256sum \
  > "${LOCAL_OUT}/manifests/artifact_inventory.sha256"
sha256sum -c "${LOCAL_OUT}/manifests/artifact_inventory.sha256"
```

Notes:

- This route intentionally uses a new task-owned output root rather than
  writing into worker_2's historical task268 output directory.
- If the coordinator wants literal task268 script reuse, regenerate the scripts
  with fresh task-owned log/output paths or run them under worker_2 ownership;
  the checked-in task268 scripts hardcode old worker_2 output paths.
- The route is still not authorization for SFT training, nonzero-LR smoke,
  live AIME/task243 eval, export, endpoint launch, promotion, AIME2025 train
  data, task255 reuse, or 30B/8-GPU.

## Output And Checksum Plan

For a future authorized import/preflight rerun, require:

- remote run root:
  `/root/task270_qwen_aime_v11_nemtron_runtime_route_audit_s1/rerun_<UTC>`
- local output root:
  `/work-agents/intern_nemotron_worker_5/outputs/task270_qwen_aime_v11_nemtron_runtime_route_audit_s1/rerun_<UTC>`
- logs:
  - `logs/bridge_import_probe.log`
  - `logs/fail_closed_preflight.log`
- imported checkpoint output:
  `qwen3_4b_bridge_import_iter0/`
- manifest:
  `manifests/artifact_inventory.sha256`
- pass conditions:
  - symbol preflight prints `TASK270_RUNTIME_SYMBOL_PREFLIGHT=PASS`;
  - Bridge import log contains `IMPORT_DONE`;
  - Bridge import log contains `BRIDGE_IMPORT_RC=0`;
  - fail-closed preflight prints `TASK270_FAIL_CLOSED_PREFLIGHT=PASS`;
  - `sha256sum -c` passes for the local artifact inventory.

## Shared Storage Boundary

Command:

```bash
stat -c '%F %U:%G %a %n' /mnt/cephfs/data/processing/lei.song
```

Observed:

```text
directory root:root 755 /mnt/cephfs/data/processing/lei.song
```

Boundary: no file under `/mnt/cephfs/data/processing/lei.song` was deleted,
overwritten, or modified. Future reruns must keep that no-delete rule and use
task-owned output paths only.

## Residual Risk

- The existing `NemTron` Python route has the correct `AutoBridge` symbol, but
  actual `AutoBridge.import_ckpt` was not executed because task270 is an audit
  and because `nemo` is missing.
- Installing `nemo` may reveal additional package-version incompatibilities
  only visible during import. The fail-closed preflight should remain the gate.
- Container image availability is unproven until a daemon/runtime can inspect
  or run the requested image.
- LTP/OpenPAI is unproven until credentials and a no-training job template are
  provided.
- Global Qwen AIME V11 remains `NO-GO/HOLD`; task270 does not change any
  training, eval, promotion, endpoint, task255 reuse, AIME2025 train data, or
  30B/8-GPU boundary.
