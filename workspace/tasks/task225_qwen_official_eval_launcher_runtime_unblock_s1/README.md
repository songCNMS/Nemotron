# task225_qwen_official_eval_launcher_runtime_unblock_s1

Owner: intern_nem_dev_2
Status: Complete, evidence branch only
Base/product commit: `1d037329f5a02cdc04f2a09a16e7342721be4c87`
Branch: `intern_nem_dev_2/task225_qwen_official_eval_launcher_runtime_unblock_s1`

## Result

`OFFICIAL_EVAL_RUNTIME_BLOCKED` is unblocked for the M1 launcher-available subset at runtime-discovery level.

- Existing local, VPN, and NemTron inventories did not have `nemo-evaluator-launcher` or importable `nemo_evaluator_launcher`.
- Built a contained local task-owned runtime at `/mnt/cephfs/data/processing/nemotron-live-validation/task225/runtime_venv` with `nemo-evaluator-launcher==0.2.5`.
- Built a task-owned wheelhouse at `/mnt/cephfs/data/processing/nemotron-live-validation/task225/wheelhouse` with 110 wheels and SHA256 manifest.
- Validated a product-interpreter overlay using `/work-agents/.venv/bin/python` plus `/mnt/cephfs/data/processing/nemotron-live-validation/task225/product_python_overlay`.
- VPN cannot see the `/mnt/cephfs` task root, so staged the wheelhouse/config to `/home/leisong/nemotron-live-validation/task225`.
- VPN `python3 -m venv` is blocked by missing `ensurepip`, but a task-owned offline `pip --target` install under `/home/leisong/nemotron-live-validation/task225/pip_target` works.
- VPN Docker access was confirmed by `docker ps`; no eval was launched.

## Activation

Local product CLI overlay:

```bash
ROOT=/mnt/cephfs/data/processing/nemotron-live-validation/task225
PYTHONPATH="$ROOT/product_python_overlay:src" /work-agents/.venv/bin/python -m nemotron super3 eval \
  -c m1_full_basket_launcher_available \
  run.model=qwen3-30b-a3b-instruct-2507-staged \
  execution.type=local \
  execution.output_dir="$ROOT/eval/m1_launcher_available" \
  'execution.auto_export.destinations=[]' \
  deployment.type=generic \
  deployment.url=http://10.100.2.62:13000/v1/chat/completions \
  deployment.checkpoint_path=/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/staged_model/Qwen3-30B-A3B-Instruct-2507 \
  evaluation.nemo_evaluator_config.config.params.extra.tokenizer=/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/staged_model/Qwen3-30B-A3B-Instruct-2507 \
  evaluation.nemo_evaluator_config.config.params.extra.chat_template_kwargs.enable_thinking=false \
  evaluation.nemo_evaluator_config.config.params.extra.chat_template_kwargs.truncate_history_thinking=false
```

VPN launcher runtime:

```bash
REMOTE=/home/leisong/nemotron-live-validation/task225
PYTHONPATH="$REMOTE/pip_target" "$REMOTE/pip_target/bin/nemo-evaluator-launcher" --version
```

PM can release the M1 subset using the local product CLI overlay above, or use the staged VPN runtime path if the run is coordinated on `vpn`. A future real run still needs PM release and the approved endpoint/eval execution window.
