# task209_nemtron_h200_sft_live_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

## Goal

Use the supervisor-provided NemTron H200 node to validate the Super3 Qwen SFT
live pipeline beyond local dry-runs.

## Baseline

`0460c1f0262875fb27ae530d30cd80d805752851`

## Resource Facts

- SSH alias: `NemTron`.
- PM observed hostname: `lg-cmc-b7r201-f08u26-h200-000126`.
- Expected GPUs: 8x NVIDIA H200.
- Qwen model path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209`.

## Scope

- Run NemTron hostname, GPU, model, code, and Python import/CUDA preflight.
- Stage a source snapshot to cephfs if repo/code is not available on NemTron;
  do not `git pull` on NemTron.
- Use the corrected task208 sample splits:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_sample4/sample-4/splits`.
- Stage the sample into the NemTron-visible task209 input directory if the
  local task208 path is not visible from NemTron:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits`.
- Run one-iteration `m1_agentic_smoke` with Qwen model path and task208 sample
  splits if prerequisites are present.
- If smoke passes and full task208 splits exist, prepare the smallest safe
  SFT continuation command or report a PM scheduling hold.

## Session 3 Evidence Summary

- Corrected PM single-SSH sample staging succeeded with `staging_rc=0`.
- Staged sample hashes matched local source hashes for `blend.json`,
  `splits/metadata.json`, and `splits/train/shard_000000.parquet`.
- Intended `python -m nemotron ...` CLI remains blocked on NemTron because
  `/usr/bin/python3` lacks `nemo_run`.
- Authorized direct `torchrun` fallback reached Python import setup but failed
  before training with `ModuleNotFoundError: No module named 'megatron.energon'`.
- Bounded alternate Python probe found only `/usr/bin/python3` and
  `/usr/bin/python`, both with CUDA/Megatron Bridge but without `nemo_run` or
  `megatron.energon`; no `/opt/conda` or `/opt/venv` interpreter was present.
- Local focused SFT/Qwen validators passed: `33 passed, 2 skipped`.
- Full task208 splits are available locally at
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_full/splits`,
  but were not staged or launched because the one-iteration smoke is blocked
  before train start and PM review is required before any continuation.

## Session 4 Evidence Summary

- Searched existing NemTron, VPN, and local offline train-stack resources
  without mutating system paths. No ready conda/venv/container/wheelhouse was
  found for the missing train stack.
- Built a user-owned local wheelhouse and staged it to NemTron at
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/wheelhouse`.
- Created a user-owned NemTron venv with `--system-site-packages` at
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv`.
- Installed staged wheels only into that venv. No NemTron network download and
  no `/usr/bin/python3` or system site-packages mutation was performed.
- Final venv import probe passed for `nemo_run`, `megatron.energon`,
  `nvidia_resiliency_ext`, `hydra`, `bracex`, `wcmatch.glob`, `torch`,
  `megatron`, and `megatron.bridge`; `mamba_ssm` remains missing.
- Canonical one-iteration smoke with the Qwen contract config reaches Megatron
  model build, then fails because `MambaSSM is not installed`.
- A bounded attention-only tiny-pattern probe, launched before PM's GPU hold
  arrived, reached the training loop but failed with
  `MambaModel.forward() got an unexpected keyword argument 'packed_seq_params'`.
- PM placed a GPU scheduling hold because task210 SGLang TP=8 is active on all
  H200s. No further train launch is allowed until PM explicitly releases GPUs.

## Boundaries

- No package, model, or container downloads on NemTron.
- Do not write new task209 outputs under the superseded
  `/mnt/cephfs/data/nemotron-live-validation/...` root.
- No W&B, deploy, artifact upload, direct `main`/`master` push, or self-merge.
- Coordinate with dev_3 before any GPU endpoint serving.
