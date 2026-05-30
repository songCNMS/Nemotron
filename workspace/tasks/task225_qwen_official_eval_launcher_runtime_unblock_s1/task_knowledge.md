# Task Knowledge

- `nemo-evaluator-launcher==0.2.5` is the compatible runtime version referenced by the Super3 M1 launcher-available config and historical task071 evidence.
- The product command imports the official runtime at non-dry execution time from `nemo_evaluator_launcher.api.functional import run_eval`.
- Product `nemotron super3 eval --dry-run` does not require the launcher import because it returns before the runtime import.
- A direct task-owned venv works on the local CPU host, but it lacks the full Nemotron CLI dependency set. Use `/work-agents/.venv/bin/python` for product CLI and append the task-owned launcher site-packages through `/mnt/cephfs/data/processing/nemotron-live-validation/task225/product_python_overlay/sitecustomize.py`.
- VPN can run Docker, but it cannot see the `/mnt/cephfs/data/processing/nemotron-live-validation/task225` artifact root. The VPN runtime is staged separately under `/home/leisong/nemotron-live-validation/task225`.
- VPN `python3 -m venv` is not usable because `ensurepip` is missing. The working VPN path is `PYTHONPATH=/home/leisong/nemotron-live-validation/task225/pip_target /home/leisong/nemotron-live-validation/task225/pip_target/bin/nemo-evaluator-launcher ...`.
- The no-endpoint dry-run still prepares Docker shell scripts. It did not execute those scripts, launch containers, call endpoints, or run evaluation.
