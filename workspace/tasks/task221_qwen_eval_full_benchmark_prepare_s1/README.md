# task221_qwen_eval_full_benchmark_prepare_s1

Owner: `intern_nem_dev_3`

Status: complete for evidence/preparation; live endpoint/eval remains HOLD pending PM release after task220.

Baseline/product commit: `1d037329f5a02cdc04f2a09a16e7342721be4c87`

Branch: `intern_nem_dev_3/task221_qwen_eval_full_benchmark_prepare_s1`

Artifact root: `/mnt/cephfs/data/processing/nemotron-live-validation/task221`

## Scope

Prepared the post-task219/task220 Qwen endpoint/eval continuation without consuming H200 resources. This used task210 Session 4 evidence and the current product baseline to prepare:

- exact SGLang endpoint command from the task210 staged Qwen model path,
- sanitized endpoint smoke request/command with required Qwen `chat_template_kwargs`,
- corrected math smoke command,
- launcher-available M1 subset command,
- full 27-target M1/M2 run plan and blockers,
- CPU/static validators and readiness artifacts.

## Evidence

- `validation_report.md`: `/mnt/cephfs/data/processing/nemotron-live-validation/task221/validation_report.md`
- Prepared commands: `/mnt/cephfs/data/processing/nemotron-live-validation/task221/commands`
- Target inventory: `/mnt/cephfs/data/processing/nemotron-live-validation/task221/readiness/static_eval_targets.json`
- Model visibility logs:
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task221/readiness/local_model_visibility.log`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task221/readiness/nemtron_staged_model_visibility.log`
- Full plan: `/mnt/cephfs/data/processing/nemotron-live-validation/task221/full_27_target_plan.md`

## Checks

- `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/recipes/super3/test_qwen_eval_repro_gate.py tests/recipes/super3/test_benchmark_alignment_path_guards.py tests/recipes/super3/test_m1_eval_full_basket.py tests/recipes/super3/test_m2_eval_basket_s1.py tests/recipes/super3/test_m2_eval_basket_s2.py` -> 136 passed, 8 warnings.
- Corrected math exact-command dry-run -> passed config compilation.
- M1 launcher-available exact-command dry-run -> passed config compilation.
- Local stable model visibility -> 16 shards and essential files visible.
- NemTron staged model visibility -> 16 shards and essential files visible via non-GPU filesystem check.
- Prompt/no-secret scan -> prepared smoke prompt is non-benchmark and no secret values are in prepared commands; dry-run logs include placeholder env var names only.

## Boundaries

Not run: SGLang endpoint start, endpoint request, live corrected math smoke, M1/M2 benchmark, model copy, package install/build, process kill, W&B, cluster/deploy, artifact upload, main/master push, or self-merge.

## HOLD Items

- PM release is required before H200 endpoint serving.
- Recheck NemTron process/port/GPU state at release time.
- Local CPU cannot see the staged model directory; final launch should use the NemTron-visible path and recheck it there.
- Local `/work-agents/.venv` lacks `nemo_evaluator_launcher`; official eval commands need a runtime with that package.
- M1 full basket still has five targets without exact launcher mappings: `multichallenge`, `terminalbench`, `mcp_mark`, `tool_decathlon`, `swe_bench_verified`.
- M2 targets remain config-only/runtime-deferred and require live assets/APIs/databases/sandboxes/baselines.
