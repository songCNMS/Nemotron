# task210_nemtron_vpn_endpoint_eval_live_s1

<!-- METADATA:STATUS=ReadyForPM,ASSIGNEE=intern_nem_dev_3,SESSION=2 -->

## Scope

- Evidence-only NemTron/vpn endpoint live-path validation.
- Discover available serving runtime on NemTron without downloads.
- Use vpn only for image/build staging evidence because vpn lacks the cephfs
  Qwen model path.
- Coordinate with dev_2 before heavy H200 serving.
- Start Qwen endpoint and run one minimal sanitized chat request only if GPUs
  are released and serving is feasible.

## Boundaries

- No package/model download on NemTron.
- No full benchmark until endpoint smoke passes.
- No benchmark prompts in live request.
- No training, W&B/cluster deploy, artifact upload, direct `main`/`master`
  push, or self-merge.

## Status

- Baseline SHA: `0460c1f0262875fb27ae530d30cd80d805752851`
- Branch: `intern_nem_dev_3/task210_nemtron_vpn_endpoint_eval_live_s1`
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task210`
- Evidence:
  - NemTron: 8 H200 visible; Qwen model path visible; SGLang 0.5.8 import OK;
    vLLM and TensorRT-LLM imports missing
  - vpn: Docker 29.1.3 available; Qwen cephfs model path missing
  - dev_2 coordination: heavy NemTron GPUs not released because task209 owns
    H200 training/preflight use
  - Endpoint smoke -> skipped; no server started and no live request made
  - Corrected math dry-run -> passed; runtime
    `real 2.252 user 8.953 sys 0.353`
  - Qwen/M1/M2 validator shard -> 136 passed, 8 warnings; runtime
    `real 4.252 user 3.973 sys 0.276`
  - Structured evidence summary:
    `/mnt/cephfs/data/processing/nemotron-live-validation/task210/task210_evidence_summary.md`
  - Structured evidence JSON:
    `/mnt/cephfs/data/processing/nemotron-live-validation/task210/task210_evidence_summary.json`
  - `git diff --check` -> passed
  - `git diff --cached --check` -> passed
