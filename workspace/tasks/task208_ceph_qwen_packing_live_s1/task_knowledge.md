# Task Knowledge

<!-- METADATA:SESSION=2 -->

- Task208 uses cephfs model/tokenizer path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- The original artifact root
  `/mnt/cephfs/data/nemotron-live-validation/task208` is unwritable from the
  local CPU process and is historical only.
- The corrected final artifact root is:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208`.
- Sample output nests under `sample-4`; the exact sample split path is:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_sample4/sample-4/splits`.
- Full output split path is:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_full/splits`.
- PM reported that dev_2/NemTron cannot see the local CPU-created corrected-root
  artifacts at the same path. Treat task208 artifacts as local CPU evidence
  until staged to a NemTron-visible task209 input path.
