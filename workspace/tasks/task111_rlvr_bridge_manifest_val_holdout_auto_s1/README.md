# task111_rlvr_bridge_manifest_val_holdout_auto_s1 - RLVR bridge manifest val holdout auto

<!-- METADATA:STATUS=Working,ASSIGNEE=intern_nem_dev_2,SESSION=14 -->

## Background

Task107 made SWE1, SWE2, and RLHF stage2 RL bridge consumers infer
`val_holdout` from sibling bridge manifests. RLVR1, RLVR2, and RLVR3 still used
fixed `val_holdout: 100`, and their data-prep path runs placeholder
resolution before splitting. A resolved intermediate JSONL does not have the
original bridge `manifest.json` beside it, so auto holdout must be resolved
from the original bridge input before placeholder resolution.

## Goals

- Set RLVR1/RLVR2/RLVR3 data-prep defaults to `val_holdout: auto`.
- Resolve auto holdout against the original bridge `combined.jsonl` sibling
  `manifest.json` before placeholder resolution.
- Carry the resolved bridge-manifest holdout through the final local split.
- Preserve explicit numeric holdouts for manual/non-bridge inputs.
- Add focused tests for RLVR defaults, auto through the resolve-and-split path,
  and numeric holdout compatibility.

## Out Of Scope

- Live bridge data prep against production data, RL training, eval, endpoint
  calls, W&B, cluster jobs, deployment, direct `main` or `master` push, and
  self-merge.

## Acceptance Criteria

- [x] Branch created from `origin/main`
  `4bb920fd0e942a4d807394893c8bba5f2bb87952`.
- [x] RLVR1/RLVR2/RLVR3 defaults use bridge `combined.jsonl` and
  `val_holdout: auto`.
- [x] `run_resolve_and_split()` resolves auto holdout from the original bridge
  input manifest before placeholder resolution.
- [x] Explicit numeric holdout still works for plain local JSONL.
- [x] Focused pytest, py_compile, Ruff, structured fixture probe, static config
  probe, and diff whitespace checks pass.
- [x] PR opened to `main`.

## PR

- https://github.com/songCNMS/Nemotron/pull/218
