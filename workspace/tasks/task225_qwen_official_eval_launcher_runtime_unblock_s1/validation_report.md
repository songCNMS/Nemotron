# Validation Report

Artifact root: `/mnt/cephfs/data/processing/nemotron-live-validation/task225`
Remote VPN root: `/home/leisong/nemotron-live-validation/task225`

## Evidence

- `logs/00_local_env_inventory.log`: local inventory, no launcher runtime found.
- `logs/01_vpn_env_inventory.log`: VPN inventory, no launcher runtime found.
- `logs/01_nemtron_env_inventory.log`: NemTron inventory, no launcher runtime found.
- `logs/02_local_runtime_venv_build.log`: local task-owned venv build, `VENV_BUILD_OK=true`.
- `logs/03_local_runtime_import_cli_validation.log`: local import, CLI help/version, packaged task listing.
- `logs/05b_m1_subset_task_mapping_probe_kwonly.log`: all 14 M1 launcher-available task names resolved.
- `logs/07_launcher_m1_subset_raw_dry_run.log`: raw launcher no-endpoint dry-run returned `DRY_RUN_RC=0`.
- `logs/10_product_venv_overlay_import_probe.log`: product interpreter overlay imports `nemo_evaluator_launcher==0.2.5`.
- `logs/11_nemotron_cli_product_venv_overlay_dry_run.log`: product CLI dry-run for the task221 command shape returned `NEMOTRON_CLI_DRY_RUN_RC=0`.
- `logs/13_local_wheelhouse_build.log` and `logs/13_local_wheelhouse_sha256.txt`: local wheelhouse build and hashes.
- `logs/15_vpn_offline_venv_install_validate.log`: VPN venv blocked by missing `ensurepip`; no system mutation attempted.
- `logs/16_vpn_offline_pip_target_validate.log`: VPN offline `pip_target` import, CLI, Docker probe, and no-endpoint dry-run returned `VPN_PIP_TARGET_LAUNCHER_DRY_RUN_RC=0`.
- `vpn_copied_logs/16_vpn_launcher_dry_run.log`: local-visible copy of VPN launcher dry-run log.
- `vpn_copied_logs/17_vpn_remote_artifact_manifest.txt`: local-visible manifest of VPN artifacts.

## Commands

Local product-interpreter import probe:

```bash
PYTHONPATH=/mnt/cephfs/data/processing/nemotron-live-validation/task225/product_python_overlay:src \
  /work-agents/.venv/bin/python -c 'from nemo_evaluator_launcher.api.functional import run_eval; print(run_eval)'
```

Local product CLI dry-run:

```bash
PYTHONPATH=/mnt/cephfs/data/processing/nemotron-live-validation/task225/product_python_overlay:src \
  /work-agents/.venv/bin/python -m nemotron super3 eval \
  -c m1_full_basket_launcher_available --dry-run \
  run.model=qwen3-30b-a3b-instruct-2507-staged \
  execution.type=local \
  execution.output_dir=/mnt/cephfs/data/processing/nemotron-live-validation/task225/eval/m1_launcher_available \
  'execution.auto_export.destinations=[]' \
  deployment.type=generic \
  deployment.url=http://10.100.2.62:13000/v1/chat/completions \
  deployment.checkpoint_path=/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/staged_model/Qwen3-30B-A3B-Instruct-2507 \
  evaluation.nemo_evaluator_config.config.params.extra.tokenizer=/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/staged_model/Qwen3-30B-A3B-Instruct-2507 \
  evaluation.nemo_evaluator_config.config.params.extra.chat_template_kwargs.enable_thinking=false \
  evaluation.nemo_evaluator_config.config.params.extra.chat_template_kwargs.truncate_history_thinking=false
```

VPN no-endpoint dry-run:

```bash
REMOTE=/home/leisong/nemotron-live-validation/task225
PYTHONPATH="$REMOTE/pip_target" "$REMOTE/pip_target/bin/nemo-evaluator-launcher" run \
  --config "$REMOTE/static_check/m1_launcher_available_raw_static_generic.yaml" \
  --config-mode raw \
  --dry-run true \
  --config-output "$REMOTE/static_check/run_config_dump"
```

## Outcome

Pass. A contained official launcher runtime is available locally and on the VPN node without system mutation. The M1 launcher-available 14-task subset resolved and the launcher prepared scripts in no-endpoint dry-run mode.

Residual risk: a real evaluator run was intentionally not launched. The future released run still needs PM-controlled endpoint/eval scheduling, and the product config's `deployment.type=generic` dry-run prepares Docker scripts rather than contacting the staged endpoint during dry-run.
