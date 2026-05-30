# Task Knowledge

- Task226 command scripts point at dev_3 paths and task226 output dirs; task227 should use equivalent generated commands from the task227 branch/root while preserving the same runtime flags and task selection.
- Task225 product-interpreter runtime is `/work-agents/.venv/bin/python` with `PYTHONPATH=/mnt/cephfs/data/processing/nemotron-live-validation/task225/product_python_overlay:src` and `PATH=/mnt/cephfs/data/processing/nemotron-live-validation/task225/runtime_venv/bin:$PATH`.
- The approved task subset is `src/nemotron/recipes/super3/stage3_eval/config/m1_full_basket_launcher_available.yaml`, not `m1_full_basket.yaml`.
