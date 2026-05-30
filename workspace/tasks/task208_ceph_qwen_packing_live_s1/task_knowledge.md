# Task Knowledge

<!-- METADATA:SESSION=1 -->

- Task208 uses cephfs model/tokenizer path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Task208 requested artifact root:
  `/mnt/cephfs/data/nemotron-live-validation/task208`.
- The recipe creates a run directory below the requested output root before
  tokenization/packing. If `/mnt/cephfs/data/nemotron-live-validation` cannot be
  created, the packing run fails before producing shards or split artifacts.
- Full packing must not run unless sample packing succeeds and focused
  validators pass.
