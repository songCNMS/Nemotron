# task231 M1 Missing Launcher New Runtime Scan

Owner: `intern_nem_dev_1`

Branch: `intern_nem_dev_1/task231_m1_missing_launcher_new_runtime_scan_s1`

Base/product commit: `1d037329f5a02cdc04f2a09a16e7342721be4c87`

Artifact root: `/mnt/cephfs/data/processing/nemotron-live-validation/task231`

## Result

Status: `HOLD_EXACT_M1_MAPPINGS_STILL_MISSING`.

No newer approved/local/VPN evaluator runtime or package resource was found
that resolves the five missing M1 exact launcher mappings. Product configs were
not edited. The task228 blocker state remains valid for the current approved
runtime evidence.

## Runtime And Package Inventory

Inspected read-only:

- Local project venv:
  `/work-agents/.venv/bin/python`
  - Result: no `nemo_evaluator_launcher` module or package metadata.
- Task225 approved local runtime:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task225/runtime_venv/bin/python`
  - `nemo-evaluator-launcher==0.2.5`
  - Package file:
    `/mnt/cephfs/data/processing/nemotron-live-validation/task225/runtime_venv/lib/python3.12/site-packages/nemo_evaluator_launcher/__init__.py`
  - Mapping count: `421`
- Task225 wheelhouse:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task225/wheelhouse/nemo_evaluator_launcher-0.2.5-py3-none-any.whl`
  - Wheel SHA256:
    `035b2bc32ea083cf3ab8e902e1da963b276b54fa4454bb654b8b247b29574706`
- Task225 VPN evidence:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task225/logs/16_vpn_offline_pip_target_validate.log`
  and
  `/mnt/cephfs/data/processing/nemotron-live-validation/task225/vpn_copied_logs/16_vpn_pip_target_freeze.txt`
  - Result: VPN pip target also used `nemo-evaluator-launcher==0.2.5`.
- Task227 official runtime probe:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task227/official_runtime/00_task225_runtime_probe.log`
  - Result: task227 official runtime was the same task225 runtime,
    `nemo_evaluator_launcher: 0.2.5`.

Bounded artifact search found only:

- `/mnt/cephfs/data/processing/nemotron-live-validation/task225/runtime_venv/bin/nemo-evaluator-launcher`
- `/mnt/cephfs/data/processing/nemotron-live-validation/task225/runtime_venv/lib/python3.12/site-packages/nemo_evaluator_launcher/__init__.py`
- `/mnt/cephfs/data/processing/nemotron-live-validation/task225/wheelhouse/nemo_evaluator_launcher-0.2.5-py3-none-any.whl`

Package resource hashes:

- Runtime `all_tasks_irs.yaml` SHA256:
  `b0e56d00ffddebd60a81cef654e6e037b38f5ed72dc985ded3e94b237649e394`
- Runtime `mapping.toml` SHA256:
  `684a594af1f5dbd089d2eb04366579a6ecd43a02cdd09770006badc1aa2325d7`
- Wheel-embedded `all_tasks_irs.yaml` SHA256:
  `b0e56d00ffddebd60a81cef654e6e037b38f5ed72dc985ded3e94b237649e394`
- Wheel-embedded `mapping.toml` SHA256:
  `684a594af1f5dbd089d2eb04366579a6ecd43a02cdd09770006badc1aa2325d7`

## Probe Artifacts

- Runtime inventory log:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task231/logs/runtime_inventory.log`
  - SHA256:
    `dc3067435820265879200dc93a508cba70f8abfe2c00cc7c080f1193c885bfba`
- Structured package-resource probe:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task231/probes/new_runtime_mapping_scan.json`
  - SHA256:
    `ed8aa2fc82f77214fd11f31a223f9835baf94f50fdf95bcb1720e93a56276610`

## Per-Target Resolution Table

| M1 target | Exact mapping found? | Nearest package matches | Why unsafe | Proposed resolution |
| --- | --- | --- | --- | --- |
| `multichallenge` | No | `mtbench.mtbench`, `mtbench.mtbench-cor1` | MT-Bench is a related chat/judge benchmark, not MultiChallenge. | Add an exact MultiChallenge launcher task, or obtain benchmark-owner written equivalence approval for a specific task and scoring contract. |
| `terminalbench` | No | `codec.terminalbench` | Package description says `Task for detecting contamination with the Terminal-Bench dataset`; contamination detection is not TerminalBench benchmark evaluation. | Add a TerminalBench benchmark evaluator task/assets entry, not a `codec` detector. |
| `mcp_mark` | No | none | No `mcp`, `mcp_mark`, or `mcp_mark.mcp_mark` task/key appeared in the package mapping. | Add MCP-Mark evaluator task plus MCP server/assets/credential contract. |
| `tool_decathlon` | No | `tooltalk.tooltalk`, BFCL variants including `bfcl.bfclv3_ast_prompting` | ToolTalk/BFCL are tool-use benchmarks, not Tool-Decathlon with its scoring rubric/tool suite. | Add exact Tool-Decathlon evaluator task and tool-service/scoring contract, or obtain benchmark-owner equivalence approval. |
| `swe_bench_verified` | No | `codec.swebench_test`, `codec.swebench_train` | Package descriptions are SWE-bench contamination detection for test/train splits, not SWE-Bench Verified repair evaluation. | Add exact SWE-Bench Verified evaluator task/assets entry. |

## Config-Only Proposal

No safe config-only mapping can be proposed from current package resources.
When exact mappings exist, the minimal product plan is:

1. Update
   `src/nemotron/recipes/super3/milestones/m1_eval_basket/m1_eval_launcher_mapping.yaml`
   by changing only the resolved rows from `status: missing` to
   `status: available` with exact `launcher_task` values.
2. Add those exact task names to
   `src/nemotron/recipes/super3/stage3_eval/config/m1_full_basket_launcher_available.yaml`
   only if PM wants the launcher-available config to expand from 14 targets.
3. Update focused guard tests in
   `tests/recipes/super3/test_m1_eval_full_basket.py` to reduce
   `EXPECTED_LAUNCHER_MISSING_IDS` and assert the exact task names.
4. Run focused M1 mapping pytest plus a dry-run/schema probe. Live eval remains
   a separate PM-released task.

## Checks

- Structured runtime/package resource scan: passed.
- Focused M1 mapping guard:

  ```bash
  PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q \
    tests/recipes/super3/test_m1_eval_full_basket.py \
    -k 'launcher_mapping or launcher_available_config_uses_only_verified_available_tasks or launcher_available_config_expands_into_evaluator_schema'
  ```

  Result: `4 passed, 47 deselected, 8 warnings`.
- `git diff --check`: passed before commit.
- `git diff --cached --check`: passed before commit.
- Py_compile/Ruff: not applicable; docs/status branch only.

## Residual Risk And Estimate

- Residual risk: scan is limited to local approved artifacts and bounded
  task225/task227/VPN copied evidence available on this machine. A newer
  launcher package may exist outside these artifacts, but none is currently
  staged/approved locally.
- Estimate once exact mappings exist:
  - Config/test update and static dry-run probe: 1-2 hours.
  - PM gate on the mapping PR: 1-2 hours plus independent test queue.
  - Full 19-target M1 runtime after mapping merge: still needs PM re-release;
    the existing estimate remains 8-24 hours depending endpoint throughput,
    evaluator runtime, task parallelism, and long-context/code task duration.

## Boundaries

No endpoint, eval, benchmark, Docker pull/build/run, package install/build or
download, environment mutation, model copy, process kill, artifact upload,
product code edit, direct `main`/`master` push, or self-merge was performed.
