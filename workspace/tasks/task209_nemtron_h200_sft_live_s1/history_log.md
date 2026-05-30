# History Log

<!-- METADATA:SESSION=3 -->

## Session 3 - 2026-05-30

- Applied PM corrections for task209 sample staging after the local CPU and
  NemTron `/mnt/cephfs` namespaces diverged.
- Recorded the actual task208 sample source as
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_sample4/sample-4`.
- Reran sample staging with a single pipe-through-SSH command into
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4`.
  The command returned `staging_rc=0` and remote hashes matched local source
  hashes:
  - `blend.json`:
    `91e2b11d0fcee641141d1b4dd48d93adf9a7aa354bb6923fe5794386e2479d52`
  - `splits/metadata.json`:
    `f8d80620c2266b8e6e804b77770b8119844ce2171deb0a59516e4e9baf566cbd`
  - `splits/train/shard_000000.parquet`:
    `a5bb516ff83dcd88526062ec95ae2aec853455bde5520e82813e60cc76080ca4`
- Ran the PM-authorized direct one-iteration `torchrun` fallback on
  `CUDA_VISIBLE_DEVICES=0` using the staged sample splits. It failed with
  `fallback_rc=1` before training because NemTron `/usr/bin/python3` imports
  `megatron.bridge` but then raises
  `ModuleNotFoundError: No module named 'megatron.energon'`.
- Confirmed the intended CLI path is also blocked because NemTron
  `/usr/bin/python3` lacks `nemo_run`.
- Probed bounded alternate Python environments on NemTron. Only
  `/usr/bin/python3` and `/usr/bin/python` were available; both expose
  `torch`, CUDA, `megatron`, and `megatron.bridge`, but neither has
  `nemo_run` or `megatron.energon`.
- Reran the local focused SFT/Qwen validator shard:
  `33 passed, 2 skipped`.
- Confirmed NemTron H200 GPUs were idle after the failed fallback: eight H200s,
  1 MiB used each, 0% utilization, no compute processes.
- Recorded PM's full split completion notice:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_full/splits`
  with `total_sequences=987770`, `total_tokens=672687706`, `num_shards=16`,
  `pack_size=4096`, `elapsed_sec=254`. Full artifacts were not staged because
  the one-iteration smoke is blocked and PM review is required before any
  continuation.

## Session 2 - 2026-05-30

- PM corrected the artifact root and task208 handoff path while task209 setup
  was in progress.
- Updated task209 docs/status to use corrected artifact root
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209`.
- Updated the task208 sample split wait path to
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_sample4/splits`.
- Recorded that the earlier `/mnt/cephfs/data/nemotron-live-validation/...`
  root is superseded and must not receive new task209 outputs.
- Continued holding heavy NemTron GPU usage for dev_2/task209 until release or
  PM handoff.

## Session 1 - 2026-05-30

- Accepted PM assignment `task209_nemtron_h200_sft_live_s1`.
- Started from baseline `0460c1f0262875fb27ae530d30cd80d805752851`.
- Created evidence-only branch
  `intern_nem_dev_2/task209_nemtron_h200_sft_live_s1`.
- Recorded task scope and boundaries before running NemTron commands.
- Coordinated with dev_3 that dev_2/task209 owns heavy NemTron GPU usage until
  release or PM handoff; dev_3 may do only non-heavy discovery.
