# Task Knowledge

<!-- METADATA:SESSION=3 -->

- Baseline commit: `0460c1f0262875fb27ae530d30cd80d805752851`.
- Branch: `intern_nem_dev_2/task209_nemtron_h200_sft_live_s1`.
- NemTron SSH alias: `NemTron`.
- Corrected artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209`.
- Qwen model path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Actual task208 sample split source:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_sample4/sample-4/splits`.
- NemTron-visible staged sample split path:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits`.
- Correct sample staging must use a pipe-through-SSH command that creates and
  extracts in the NemTron namespace:
  `(cd "$SRC" && tar --dereference -cf - blend.json splits) | ssh -o BatchMode=yes NemTron "rm -rf '$DEST' && mkdir -p '$DEST' && tar -C '$DEST' -xf - && find '$DEST' -maxdepth 4 -type f -printf '%p %s\n' && sha256sum '$DEST'/blend.json '$DEST'/splits/metadata.json '$DEST'/splits/train/shard_000000.parquet"`.
- One-iteration checkpoint path:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/checkpoints_one_iter`.
- Intended CLI blocker: NemTron `/usr/bin/python3` lacks `nemo_run`.
- Direct `torchrun` fallback blocker: NemTron `/usr/bin/python3` has
  `torch`, CUDA, `megatron`, and `megatron.bridge`, but lacks
  `megatron.energon`, causing `ModuleNotFoundError` before train start.
- Bounded alternate Python probe found no usable complete environment:
  `/usr/bin/python3` and `/usr/bin/python` both lack `nemo_run` and
  `megatron.energon`; `/opt/conda` and `/opt/venv` are absent.
- PM-reported task208 full split path:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_full/splits`
  (`total_sequences=987770`, `total_tokens=672687706`, `num_shards=16`,
  `pack_size=4096`, `elapsed_sec=254`). Do not launch full/small continuation
  until PM reviews the one-iteration evidence.
- NemTron has no network: do not download packages, models, containers, or run
  `git pull` on NemTron.
- dev_2/task209 owns heavy NemTron GPU usage until release or PM handoff.
- Superseded root: do not write new task209 outputs under
  `/mnt/cephfs/data/nemotron-live-validation/...`.
