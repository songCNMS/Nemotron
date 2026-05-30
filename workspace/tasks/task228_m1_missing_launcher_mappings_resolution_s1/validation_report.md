# task228 M1 Missing Launcher Mappings Resolution

Owner: `intern_nem_dev_1`

Branch: `intern_nem_dev_1/task228_m1_missing_launcher_mappings_resolution_s1`

Base/product commit: `1d037329f5a02cdc04f2a09a16e7342721be4c87`

Artifact root: `/mnt/cephfs/data/processing/nemotron-live-validation/task228`

## Result

Status: `BLOCKED_BY_MISSING_EXACT_LAUNCHER_MAPPINGS`.

No exact safe mapping was found for the five missing M1 launcher targets from
task226. I did not change product configs because all runtime package
candidates are either absent or semantically non-equivalent to the intended M1
benchmark contract.

## Product Inventory

- Full intended M1 config:
  `src/nemotron/recipes/super3/stage3_eval/config/m1_full_basket.yaml`
  contains all 19 M1 targets, including the five missing launcher mappings.
- Runtime subset:
  `src/nemotron/recipes/super3/stage3_eval/config/m1_full_basket_launcher_available.yaml`
  contains 14 exact available launcher tasks.
- Launcher mapping:
  `src/nemotron/recipes/super3/milestones/m1_eval_basket/m1_eval_launcher_mapping.yaml`
  records the five unresolved rows with `status: missing` and warns that
  candidates are not exact substitutes.
- Guard tests:
  `tests/recipes/super3/test_m1_eval_full_basket.py` locks the expected five
  missing IDs and the 14-task launcher-available subset.

## Task225 Runtime Package Probe

Probe files:

- `/mnt/cephfs/data/processing/nemotron-live-validation/task228/logs/task225_task_inventory_probe.log`
- `/mnt/cephfs/data/processing/nemotron-live-validation/task228/logs/task225_missing_m1_mapping_resolution_probe.log`
- `/mnt/cephfs/data/processing/nemotron-live-validation/task228/probes/task225_missing_m1_mapping_resolution_probe.json`
  - `sha256=42997448c977055fe0140879cffed1539d673d85002d5dfb2840950d8c715dde`
  - `size_bytes=10702`

Runtime package:

- Python:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task225/runtime_venv/bin/python`
- Package:
  `nemo-evaluator-launcher==0.2.5`
- Package file:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task225/runtime_venv/lib/python3.12/site-packages/nemo_evaluator_launcher/__init__.py`
- Mapping API:
  `get_task_definition_for_job(*, task_query, base_mapping, container=None, endpoint_type=None)`
- Loaded mapping count: `421`
- `all_tasks_irs.yaml` SHA256:
  `b0e56d00ffddebd60a81cef654e6e037b38f5ed72dc985ded3e94b237649e394`
- `mapping.toml` SHA256:
  `684a594af1f5dbd089d2eb04366579a6ecd43a02cdd09770006badc1aa2325d7`

## Missing Mapping Resolution Table

| benchmark_id | Exact/safe mapping result | Runtime matches/candidates | Decision |
| --- | --- | --- | --- |
| `multichallenge` | Missing | `mtbench.mtbench`, `mtbench.mtbench-cor1`; query found `mtbench.mtbench-cor1` with description `Corrected MT-Bench` | Keep blocked. MT-Bench is related but not MultiChallenge. |
| `terminalbench` | Missing as benchmark eval | `codec.terminalbench`; query `terminalbench` resolves to package harness `codec`, task `terminalbench`, description `Task for detecting contamination with the Terminal-Bench dataset` | Keep blocked. Contamination detection is not TerminalBench benchmark evaluation. |
| `mcp_mark` | Missing | No `mcp`, `mcp_mark`, or `mcp_mark.mcp_mark` mapping/key found | Keep blocked. Needs launcher/runtime package support or owner-provided exact task. |
| `tool_decathlon` | Missing | `tooltalk.tooltalk`, BFCL variants including `bfcl.bfclv3_ast_prompting`, `codec.bfcl_v3`, `nemo_skills.ns_bfcl_v3`, `nemo_skills.ns_bfcl_v4` | Keep blocked. ToolTalk/BFCL are not Tool-Decathlon equivalents. |
| `swe_bench_verified` | Missing | `codec.swebench_test`, `codec.swebench_train`; query found `codec.swebench_test` with description `Task for detecting contamination with the SWE-bench dataset (test split)` | Keep blocked. Contamination detection is not SWE-Bench Verified evaluation. |

## Required Owner/Resource To Unblock

- `multichallenge`: exact MultiChallenge evaluator task or benchmark-owner
  confirmation that a specific launcher task is contract-equivalent.
- `terminalbench`: TerminalBench benchmark evaluator task, not the `codec`
  contamination detector.
- `mcp_mark`: MCP-Mark evaluator package/task plus required MCP server/assets
  contract.
- `tool_decathlon`: Tool-Decathlon evaluator package/task plus tool service
  fleet/scoring contract.
- `swe_bench_verified`: SWE-Bench Verified evaluator task/assets; do not use
  `codec.swebench_test` contamination detection as a substitute.

## Commands And Checks

Structured task225 query command:

```bash
/mnt/cephfs/data/processing/nemotron-live-validation/task225/runtime_venv/bin/python - <<'PY'
# Loaded nemo_evaluator_launcher.common.mapping.load_tasks_mapping()
# and get_task_definition_for_job() against exact names and candidates.
PY
```

Static checks:

- Focused M1 mapping guard pytest:

  ```bash
  PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q \
    tests/recipes/super3/test_m1_eval_full_basket.py \
    -k 'launcher_mapping or launcher_available_config_uses_only_verified_available_tasks or launcher_available_config_expands_into_evaluator_schema'
  ```

  Result: `4 passed, 47 deselected, 8 warnings`.
- `git diff --check`: passed before commit.
- `git diff --cached --check`: passed before commit.

## Boundaries

No endpoint, eval, benchmark, package install/build, model copy, W&B,
cluster/deploy, artifact upload, product code edit, direct `main`/`master`
push, or self-merge was performed.
