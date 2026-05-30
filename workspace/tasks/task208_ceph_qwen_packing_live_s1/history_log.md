# History Log

<!-- METADATA:SESSION=2 -->

## Session 1 - 2026-05-30

- Synced local `main` to baseline
  `0460c1f0262875fb27ae530d30cd80d805752851`.
- Created evidence branch `intern_nem_dev_1/task208_ceph_qwen_packing_live_s1`.
- Verified the cephfs Qwen model path and key tokenizer/model files.
- Started real sample packing without `--dry-run` using the original requested
  root `/mnt/cephfs/data/nemotron-live-validation/task208`.
- The sample command failed before packing because creating
  `/mnt/cephfs/data/nemotron-live-validation` returned permission denied.
- Reran the same sample command with stdout/stderr captured to a local fallback
  log while keeping the original cephfs output path unchanged; it reproduced the
  same permission error.
- Ran the focused validator shard; it passed with `53 passed`.
- Did not start full 16-shard packing because the sample gate failed.
- Pushed historical evidence head
  `e197fb1af7ca4ad48e0573707fbe74edbb935311`.

## Session 2 - 2026-05-30

- Accepted PM correction that `e197fb1` is historical evidence only and the
  final artifact root must be
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208`.
- Created the corrected root and verified it is writable from the local CPU.
- Ran real `sample=4`, `num_shards=1` Qwen packing at the corrected root; it
  passed and produced
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_sample4/sample-4/splits`.
- Reran the focused validator shard; it passed with `53 passed`.
- Ran full `sample=null`, `num_shards=16` Qwen packing at the corrected root; it
  passed and produced
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_full/splits`.
- Generated checksum manifest
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/logs/task208_output_checksums.sha256`.
- Recorded PM's cross-node visibility note: local CPU can see the corrected-root
  artifacts, but dev_2/NemTron cannot see them at the same path; dev_2 is
  staging artifacts to a NemTron-visible task209 input path.
