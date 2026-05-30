# Task Knowledge

<!-- METADATA:SESSION=1 -->

- Task226 command scripts point at dev_3 paths and task226 output dirs; task227 should use equivalent generated commands from the task227 branch/root while preserving the same runtime flags and task selection.
- Task225 product-interpreter runtime is `/work-agents/.venv/bin/python` with `PYTHONPATH=/mnt/cephfs/data/processing/nemotron-live-validation/task225/product_python_overlay:src` and `PATH=/mnt/cephfs/data/processing/nemotron-live-validation/task225/runtime_venv/bin:$PATH`.
- The approved task subset is `src/nemotron/recipes/super3/stage3_eval/config/m1_full_basket_launcher_available.yaml`, not `m1_full_basket.yaml`.
- For existing external SGLang endpoints, `deployment.type=generic` is not safe for task227 because the local launcher executor generates a deployment/server Docker path. PM accepted the safer equivalent `deployment.type=none` with `target.api_endpoint.url`, `target.api_endpoint.model_id`, and `target.api_endpoint.type` pointed at the existing task227 endpoint.
- Under the urgent boundary correction, do not run any more Docker image pulls, package installs, builds, downloads, or environment mutation. Only already-proven pre-existing images/runtimes may be used; otherwise HOLD and cleanup.
- The VPN probe `docker run --rm --network host curlimages/curl:latest ...` attempted/pulled `curlimages/curl:latest` because only `curlimages/curl:8.10.1` was known pre-existing. Record this as boundary risk and do not use the pulled tag as accepted pre-existing evidence.
