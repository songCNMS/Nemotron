# task217_mamba_causal_conv_train_stack_unblock_probe_s1

<!-- METADATA:STATUS=ReadyForPMReview,ASSIGNEE=intern_nem_dev_3,SESSION=2 -->

## Scope

- Evidence-only diagnosis for the task216 runtime blocker
  `MAMBA_SSM_CAUSAL_CONV1D_FWD_FUNCTION_NONE`.
- No training launch, benchmark, endpoint, package install into shared/global
  environments, model copy/download, W&B/cluster deploy, artifact upload,
  direct main/master push, or self-merge.

## Status

- Base SHA: `1d037329f5a02cdc04f2a09a16e7342721be4c87`
- Branch:
  `intern_nem_dev_3/task217_mamba_causal_conv_train_stack_unblock_probe_s1`
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task217`
- Result: root cause identified.
- Validation report:
  `workspace/tasks/task217_mamba_causal_conv_train_stack_unblock_probe_s1/validation_report.md`

## Finding

Task216 used `/usr/local/bin/torchrun`, whose shebang is `/usr/bin/python3`,
with:

```text
PYTHONPATH=/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv/lib/python3.12/site-packages:/mnt/cephfs/data/processing/nemotron-live-validation/task216/Nemotron/src
```

In that exact context, `mamba_ssm==2.3.2.post1` imports from the task209
contained target and `selective_scan_cuda` is present, but `causal-conv1d` and
`causal_conv1d_cuda` are absent. `mamba_ssm.ops.triton.ssd_combined` catches the
missing import and sets `causal_conv1d_fwd_function=None`, matching the task216
`TypeError: 'NoneType' object is not callable`.

## Unblock Request

Build/install a compatible `causal-conv1d` package into a task-owned contained
target, not global site-packages. Recommended exact candidate is
`causal-conv1d==1.6.2.post1` from the same internal package source observed in
task209; mamba metadata requires the optional extra `causal-conv1d>=1.2.0` and
the bundled README recommends `causal-conv1d>=1.4.0`.

PM assigned the contained build/probe follow-up to dev_1 as task218. Task217
did not build or install causal-conv1d.

After install, rerun only a no-launch import probe first:

```text
from causal_conv1d.cpp_functions import causal_conv1d_fwd_function
assert callable(causal_conv1d_fwd_function)
```

Then rerun the one-iteration smoke under the same task216 command with the new
contained target prepended to `PYTHONPATH`.
