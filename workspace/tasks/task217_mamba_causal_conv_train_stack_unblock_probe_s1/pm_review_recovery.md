# task217 PM Review Recovery

Date: 2026-06-01 UTC

Current worker: `intern_nemotron_worker_2`

Old assignee: `intern_nem_dev_3`

Source branch reviewed:
`origin/intern_nem_dev_3/task217_mamba_causal_conv_train_stack_unblock_probe_s1`

Old branch head reviewed: `238b5ee`

Source blocker:
`MAMBA_SSM_CAUSAL_CONV1D_FWD_FUNCTION_NONE`

## Recommendation

Approve and close task217 as a no-launch root-cause diagnosis.

The old task217 conclusion is internally consistent with the task216 failure
evidence: the task216 one-iteration smoke reached the Mamba forward path and
failed because `mamba_ssm.ops.triton.ssd_combined` called
`causal_conv1d_fwd_function(...)` while that symbol was `None`.

No request-changes item is needed for task217 itself. The missing implementation
work was correctly routed out of task217 into task218, and later live evidence
from task218/task219 covers the causal-conv unblock request.

## Evidence Reviewed

- Old task217 docs and validation report from
  `origin/intern_nem_dev_3/task217_mamba_causal_conv_train_stack_unblock_probe_s1`.
- Old task217 branch diff against `origin/main`; it is workspace evidence/docs
  only and does not modify product code.
- Task216 validation report from
  `origin/intern_nem_dev_2/task216_qwen_sft_one_iter_post_task215_live_s1`.
- Task216 local-visible failure log:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task216/session1/logs/03_canonical_one_iter_torchrun.log`.
- Task209 validation report from
  `origin/intern_nem_dev_2/task209_nemtron_h200_sft_live_s1`.
- Task218 docs from
  `origin/intern_nem_dev_1/task218_causal_conv1d_contained_train_stack_unblock_s1`.
- Task218 local-visible validation report and probe logs under
  `/mnt/cephfs/data/processing/nemotron-live-validation/task218`.
- Task219 validation report from
  `origin/intern_nem_dev_2/task219_qwen_sft_one_iter_post_task218_live_s1`.
- Task219 local-visible pre-run and one-iteration smoke logs under
  `/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1/logs`.

## Consistency Check

Task216 recorded the exact blocker as:

```text
TypeError: 'NoneType' object is not callable
```

in the Mamba path:

```text
mamba_ssm/ops/triton/ssd_combined.py
causal_conv1d_fwd_function(...)
```

The local-visible task216 torchrun log still contains the same failure at the
recorded call site.

Old task217 then probed the task216 runtime context using the same important
path ordering:

```text
/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target:
/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv/lib/python3.12/site-packages:
/mnt/cephfs/data/processing/nemotron-live-validation/task216/Nemotron/src
```

The old report states that:

- `mamba_ssm==2.3.2.post1` imported from task209 Session 5.
- `selective_scan_cuda` imported from the same contained target.
- `causal-conv1d` package metadata was missing.
- `causal_conv1d` and `causal_conv1d_cuda` were not importable.
- `ssd_combined.causal_conv1d_fwd_function`,
  `ssd_combined.causal_conv1d_bwd_function`, and
  `ssd_combined.causal_conv1d_update_function` were `None`.

That diagnosis directly explains the task216 traceback and does not conflict
with task209 evidence. Task209 Session 5 produced a contained `mamba_ssm`
source build and `selective_scan_cuda`, but did not install the optional
`causal-conv1d` extra.

## Follow-Up Coverage

Task218 covers the unblock requested by task217.

Task218 built/installed `causal-conv1d==1.6.2.post1` into the task-owned target:

```text
/mnt/cephfs/data/processing/nemotron-live-validation/task218/pip_target
```

and reported:

- `TASK218_IMPORT_FUNCTION_PROBE_PASS`
- `TASK218_TINY_CUDA_SMOKE_PASS`
- `TASK218_CONTAINMENT_PROBE_PASS`

The local-visible task218 validation report hash matches the hash recorded in
task218 README:

```text
9bcd69ed88e12533d671321bc147fb20157320bd30d9f3c7bcdb7831eb53af09
```

The local-visible task218 source artifact hash also matches:

```text
245e314ea21064ded7a5bf6b3b842b644aa6f92e45cecfe3e935629744c35ff4
```

The worker host does not directly see the NemTron-built task218 wheel or
installed extension at the paths recorded in the task218 report, but the
task218 NemTron probe logs are local-visible and show the expected imports and
callable functions from the task218 target. This is also independently covered
by task219 live evidence.

Task219 prepended the task218 target before task209's Mamba target and task209
Session 4 venv:

```text
/mnt/cephfs/data/processing/nemotron-live-validation/task218/pip_target:
/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target:
/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv/lib/python3.12/site-packages:
/mnt/cephfs/data/processing/nemotron-live-validation/task219/Nemotron/src
```

Task219 pre-run probe confirmed:

- `causal_conv1d` resolves from task218 `pip_target`.
- `causal_conv1d_cuda` resolves from task218 `pip_target`.
- `mamba_ssm` and `selective_scan_cuda` resolve from task209 Session 5.
- `ssd_combined_causal_conv1d_fwd_function_is_none` is `false`.

Task219 then ran exactly one canonical one-GPU Qwen-contract torchrun and
reported `task219_torchrun_rc=0`, iteration `1/1`, `lm loss: 1.195105E+01`,
and a checkpoint saved at iteration 1. This later live evidence confirms that
the task217 causal-conv blocker was actually unblocked for the intended
one-iteration smoke path.

## Gate Decision

- Gate result: `APPROVE_CLOSE_TASK217`.
- Closeout reason: task217 correctly diagnosed the missing contained
  causal-conv dependency and routed build/probe work to task218.
- Task218 coverage: sufficient for the no-launch import/function unblock.
- Later live coverage: task219 confirms the fixed path can complete the
  one-iteration smoke.
- Additional task217 follow-up: none.

## Residual Risk

- This recovery task did not build/install packages, launch training, run
  benchmarks/evals/endpoints, copy models, upload artifacts, or mutate product
  code.
- Review is based on existing branch docs and read-only artifact/log inspection,
  not a new implementation test run by the current team lead.
- The worker host cannot directly list the NemTron-built task218 wheel and
  installed extension paths, although the task218 report/probe logs and task219
  successful smoke cover their operational use.
- Task219 proves one-iteration unblock only. Longer small/full training remains
  outside task217 recovery scope.
