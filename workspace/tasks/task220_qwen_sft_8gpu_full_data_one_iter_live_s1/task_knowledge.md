# Task Knowledge

- Direct local CPU task208 full split visibility does not imply NemTron
  visibility. For task220, NemTron could not see the original task208 full
  split path and needed task-owned staging through SSH tar with symlink
  dereference.
- The full task208 split tree is symlink-based. Staging must dereference
  `splits/{train,valid,test}` symlinks so NemTron receives real parquet files.
- Qwen3-30B-A3B 8-GPU launches should use
  `src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py`.
  The generic `qwen_local_train.py` is a 4B-style path and is not the right
  entrypoint for 30B-A3B distributed smoke.
- The task220 30B-A3B one-iteration smoke was run with `finetune=false` and
  no pretrained Megatron checkpoint because PM supplied the HF model/tokenizer
  path but did not supply a pretrained Megatron checkpoint path. This validates
  distributed model construction, packed data loading, forward/backward,
  validation, and checkpoint save, not quality from a pretrained starting point.
- The successful task220 checkpoint is large: about `399G` for one iteration.
  Future runs should account for checkpoint I/O time and storage footprint even
  for one-iteration smoke validation.
