# task217 Validation Report

Owner: `intern_nem_dev_3`

Branch:
`intern_nem_dev_3/task217_mamba_causal_conv_train_stack_unblock_probe_s1`

Base / product commit: `1d037329f5a02cdc04f2a09a16e7342721be4c87`

Task216 evidence head from dev_2:
`421ccccae237e5aa90ba896f5aba83741b4c0715`

Artifact root:
`/mnt/cephfs/data/processing/nemotron-live-validation/task217`

## Boundary

No training, benchmark, endpoint, package install into shared/global
environments, model copy/download, W&B/cluster deploy, artifact upload, direct
main/master push, or self-merge was performed. Probes were import/static only.

## Source Evidence

Task216 failure log:
`/mnt/cephfs/data/processing/nemotron-live-validation/task216/session1/logs/03_canonical_one_iter_torchrun.log`

Task216 command used:

```bash
cd /mnt/cephfs/data/processing/nemotron-live-validation/task216/Nemotron
PYTHONPATH="/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv/lib/python3.12/site-packages:/mnt/cephfs/data/processing/nemotron-live-validation/task216/Nemotron/src" \
NEMO_RUN_DIR="/mnt/cephfs/data/processing/nemotron-live-validation/task216/session1" \
SUPER3_M1_AGENTIC_PACKED_DIR="/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits" \
SUPER3_M1_TOKENIZER_MODEL="/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507" \
SUPER3_M1_QWEN_HF_MODEL="/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507" \
SUPER3_M1_TRAINING_PROFILE="qwen" \
SUPER3_M1_SFT_SMOKE_SAVE="/mnt/cephfs/data/processing/nemotron-live-validation/task216/session1/checkpoints_one_iter" \
CUDA_VISIBLE_DEVICES=0 \
/usr/local/bin/torchrun --nproc_per_node=1 --master_addr=127.0.0.1 --master_port=29571 \
  src/nemotron/recipes/super3/stage1_sft/test_train.py \
  --config "/mnt/cephfs/data/processing/nemotron-live-validation/task216/session1/m1_agentic_smoke_qwen_contract.yaml" \
  train.train_iters=1 checkpoint.save_interval=1 artifacts.wandb=false artifacts.manifest.root=null
```

Task216 reached Bridge `gpt_step.forward_step` and Mamba forward. The prior
task215 missing-model state-injection failure did not recur. The new traceback
ended at:

```text
/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target/mamba_ssm/ops/triton/ssd_combined.py", line 840, in forward
  causal_conv1d_fwd_function(...)
TypeError: 'NoneType' object is not callable
```

## Runtime Context Probe

Artifact:
`/mnt/cephfs/data/processing/nemotron-live-validation/task217/logs/01_runtime_context_probe.log`

Host: `lg-cmc-b7r201-f08u26-h200-000126`

Important results:

- Task216 commit marker: `1d037329f5a02cdc04f2a09a16e7342721be4c87`.
- `/usr/local/bin/torchrun` has shebang `#!/usr/bin/python3`.
- Task216's launcher therefore ran under `/usr/bin/python3`, with the
  task209 mamba `pip_target`, task209 venv site-packages, and task216 repo
  `src` provided through `PYTHONPATH`.
- H200s were idle during the no-launch probe.

## Exact Import And Function Probe

Artifact:
`/mnt/cephfs/data/processing/nemotron-live-validation/task217/logs/02_exact_python_import_function_probe.log`

Command:

```bash
PYTHONPATH="/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv/lib/python3.12/site-packages:/mnt/cephfs/data/processing/nemotron-live-validation/task216/Nemotron/src" \
/usr/bin/python3 <inline import probe>
```

Key results:

- `mamba-ssm`: `2.3.2.post1`
- `mamba_ssm` path:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target/mamba_ssm/__init__.py`
- `selective_scan_cuda` path:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target/selective_scan_cuda.cpython-312-x86_64-linux-gnu.so`
- `torch`: `2.9.1+cu129`
- `torch.version.cuda`: `12.9`
- `torch.cuda.is_available`: `true`
- `torch.cuda.device_count`: `8`
- `torch._C._GLIBCXX_USE_CXX11_ABI`: `true`
- `causal-conv1d`: package metadata missing.
- `causal_conv1d`: `ModuleNotFoundError`.
- `causal_conv1d.causal_conv1d_interface`: `ModuleNotFoundError`.
- `causal_conv1d_cuda`: `ModuleNotFoundError`.
- `mamba_ssm.ops.triton.ssd_combined.causal_conv1d_fwd_function`:
  `None`, not callable.
- `mamba_ssm.ops.triton.ssd_combined.causal_conv1d_bwd_function`:
  `None`, not callable.
- `mamba_ssm.ops.triton.ssd_combined.causal_conv1d_update_function`:
  `None`, not callable.

A second probe with the task209 venv Python produced the same causal-conv1d
absence:
`/mnt/cephfs/data/processing/nemotron-live-validation/task217/logs/04_venv_python_import_function_probe.log`.

## Source And Artifact Search

Artifact:
`/mnt/cephfs/data/processing/nemotron-live-validation/task217/logs/03_mamba_source_and_artifact_search.log`

Relevant `ssd_combined.py` import lines:

```text
from causal_conv1d import causal_conv1d_fn
from causal_conv1d.cpp_functions import causal_conv1d_fwd_function, causal_conv1d_bwd_function, causal_conv1d_update_function
...
causal_conv1d_fn = None
causal_conv1d_fwd_function = None
causal_conv1d_bwd_function = None
causal_conv1d_update_function = None
```

The same file later calls `causal_conv1d_fwd_function(...)` at the failing
line, so a missing optional dependency degrades into the observed runtime
`NoneType` call.

Prior task209 artifacts were searched from the local CPU, vpn, and NemTron
views. No `causal-conv1d` wheel, source archive, Python package, or
`causal_conv1d_cuda` extension was found. The only relevant source artifact
found was:

```text
/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/local_source_artifacts/mamba_ssm-2.3.2.post1.tar.gz
```

Task209's earlier internal index probe did see available causal-conv1d versions,
with latest `1.6.2.post1`, but did not download or stage it.

## Package Metadata

Artifact:
`/mnt/cephfs/data/processing/nemotron-live-validation/task217/logs/05_mamba_metadata_dependency_probe.log`

`mamba_ssm-2.3.2.post1` metadata contains:

```text
Provides-Extra: causal-conv1d
Requires-Dist: causal-conv1d>=1.2.0; extra == "causal-conv1d"
```

The bundled README text recommends:

```text
pip install causal-conv1d>=1.4.0 --no-build-isolation
pip install mamba-ssm[causal-conv1d] --no-build-isolation
```

Task209 installed `mamba_ssm` from source into a contained `pip_target`, but
did not install the optional `causal-conv1d` extra. That explains why
`selective_scan_cuda` exists while `causal_conv1d_cuda` does not.

## Root Cause

Root cause is an incomplete contained Mamba train stack, not a product-code
state-injection bug.

The task209/task216 train stack provides `mamba_ssm==2.3.2.post1` and its
`selective_scan_cuda` extension, but lacks the optional `causal-conv1d` package
and compiled `causal_conv1d_cuda` extension required by the Mamba fast path used
by the task216 model forward. Mamba catches the import failure and sets
`causal_conv1d_fwd_function=None`; the training forward then calls that `None`
object inside `ssd_combined.py`.

## Exact Unblock Request

PM assigned dev_1 a separate task218 for the contained causal-conv1d
build/probe. Task217 did not build or install packages.

Use a task-owned contained target, not shared/global site-packages. Recommended
candidate:

```text
causal-conv1d==1.6.2.post1
```

Rationale:

- Task209's package-index probe saw `causal-conv1d 1.6.2.post1` as latest.
- Mamba metadata requires the optional extra `causal-conv1d>=1.2.0`.
- Mamba's own README text recommends `causal-conv1d>=1.4.0`.

Operational plan:

1. On a network-visible host, fetch the `causal-conv1d==1.6.2.post1` source or
   compatible wheel into a task-owned artifact directory.
2. Stage that artifact to NemTron if the fetch is not done from NemTron.
3. Build/install on NemTron into a task-owned target such as:
   `/mnt/cephfs/data/processing/nemotron-live-validation/task217/causal_conv1d_target`
   using the same torch/CUDA context:
   - Python: `/usr/bin/python3` or task209 venv Python
   - torch: `2.9.1+cu129`
   - CUDA runtime: `12.9`
   - CUDA home: `/usr/local/cuda`
   - CXX11 ABI: `true`
4. Prepend the new target to `PYTHONPATH` before the existing task216 entries:
   `<causal_conv1d_target>:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv/lib/python3.12/site-packages:/mnt/cephfs/data/processing/nemotron-live-validation/task216/Nemotron/src`
5. Run a no-launch import probe:

```python
from causal_conv1d.cpp_functions import causal_conv1d_fwd_function
from causal_conv1d.cpp_functions import causal_conv1d_bwd_function
from causal_conv1d.cpp_functions import causal_conv1d_update_function
assert callable(causal_conv1d_fwd_function)
assert callable(causal_conv1d_bwd_function)
assert callable(causal_conv1d_update_function)
```

6. Only after the import/function probe passes, rerun the task216
   one-iteration smoke.

Constraints:

- Local CPU has network/internal package-index visibility and sees task209 local
  wheelhouse artifacts, but does not provide the NemTron H200/CUDA runtime for a
  trustworthy CUDA extension build.
- vpn did not see the task209 cephfs artifact tree in the prior probe and is not
  a direct train-stack host.
- NemTron has the H200/CUDA/torch context needed for the extension build but no
  package download path should be assumed; stage package artifacts to it.

## Estimate

Once the causal-conv1d artifact is available:

- Build/install into a task-owned target on NemTron: estimate 10-30 minutes,
  depending on whether a compatible wheel is available or a source build is
  needed.
- No-launch import/function verification: under 2 minutes.
- Rerun one-iteration smoke after the env is fixed: estimate 5-10 minutes.

## Checks

- No-launch runtime context probe: PASS.
- No-launch exact Python import/function probe: PASS and reproduced
  `causal_conv1d_fwd_function=None`.
- No-launch venv Python import/function probe: PASS and reproduced the same
  missing dependency.
- Prior wheelhouse/source search: PASS; no causal-conv1d artifact found.
- Training launch: not run by boundary.
