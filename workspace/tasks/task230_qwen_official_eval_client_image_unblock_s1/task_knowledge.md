# Task Knowledge

<!-- METADATA:SESSION=2 -->

- `nemo-evaluator-launcher` maps the task227 corrected-math smoke and 14-task
  M1 launcher-available subset to 11 unique `nvcr.io/nvidia/eval-factory/*:26.03`
  client images.
- VPN is the only currently Docker-capable host observed in task230, but it has
  none of the required official evaluator client images.
- Local has a Docker CLI but no reachable daemon. NemTron has no Docker command.
- `docker image inspect <image>` is safe/read-only for presence checks and does
  not pull missing images; `docker run <image>` is not safe under the corrected
  boundary unless the image has already been proven pre-existing.
