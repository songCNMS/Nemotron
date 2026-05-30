# task228_m1_missing_launcher_mappings_resolution_s1

<!-- METADATA:STATUS=ReadyForPM,ASSIGNEE=intern_nem_dev_1,SESSION=1 -->

## Scope

- Resolve or precisely prove blockers for the five M1 missing exact launcher
  mappings from task226:
  `multichallenge`, `terminalbench`, `mcp_mark`, `tool_decathlon`, and
  `swe_bench_verified`.
- Inspect product configs and task225 runtime package task definitions/mappings
  read-only.
- Make product mapping changes only if exact safe mappings exist.

## Boundaries

- No live endpoint, eval, benchmark, package install/build, model copy, W&B,
  cluster/deploy, artifact upload, direct `main`/`master` push, or self-merge.
- Evidence/status branch only because exact safe mappings were not found.

## Status

- Base/product commit: `1d037329f5a02cdc04f2a09a16e7342721be4c87`.
- Branch:
  `intern_nem_dev_1/task228_m1_missing_launcher_mappings_resolution_s1`.
- PR: N/A, evidence/status branch only.
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task228`.
- Validation report:
  `workspace/tasks/task228_m1_missing_launcher_mappings_resolution_s1/validation_report.md`.
- Decision: no product config/test changes. Existing `status=missing` rows in
  `m1_eval_launcher_mapping.yaml` remain correct for launcher `0.2.5`.

## Evidence

- Product mapping inventory:
  `src/nemotron/recipes/super3/milestones/m1_eval_basket/m1_eval_launcher_mapping.yaml`.
- Full M1 basket config:
  `src/nemotron/recipes/super3/stage3_eval/config/m1_full_basket.yaml`.
- Launcher-available subset:
  `src/nemotron/recipes/super3/stage3_eval/config/m1_full_basket_launcher_available.yaml`.
- Existing guard tests:
  `tests/recipes/super3/test_m1_eval_full_basket.py`.
- Task225 runtime package query:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task228/probes/task225_missing_m1_mapping_resolution_probe.json`
  (`sha256=42997448c977055fe0140879cffed1539d673d85002d5dfb2840950d8c715dde`).

## Result

No exact safe mapping was found in `nemo-evaluator-launcher==0.2.5` for any
of the five missing M1 benchmark IDs. Candidate tasks are semantically
non-equivalent and remain unsafe substitutions:

| benchmark_id | Runtime candidates found | Resolution |
| --- | --- | --- |
| `multichallenge` | `mtbench.mtbench-cor1` | Blocked; Corrected MT-Bench is not MultiChallenge. |
| `terminalbench` | `codec.terminalbench` | Blocked; package describes this as contamination detection, not benchmark evaluation. |
| `mcp_mark` | none | Blocked; no MCP-Mark task/key found. |
| `tool_decathlon` | `tooltalk.tooltalk`, `bfcl.bfclv3_ast_prompting` | Blocked; tool-use tasks are not Tool-Decathlon equivalents. |
| `swe_bench_verified` | `codec.swebench_test` | Blocked; package describes this as SWE-bench contamination detection, not SWE-Bench Verified evaluation. |

## Checks

- Structured task225 runtime package probe -> passed.
- Focused M1 mapping guard pytest:
  `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/recipes/super3/test_m1_eval_full_basket.py -k 'launcher_mapping or launcher_available_config_uses_only_verified_available_tasks or launcher_available_config_expands_into_evaluator_schema'`
  -> `4 passed, 47 deselected, 8 warnings`.
- `git diff --check` -> passed before commit.
- `git diff --cached --check` -> passed before commit.
