# task208_ceph_qwen_packing_live_s1

<!-- METADATA:STATUS=Complete,ASSIGNEE=intern_nem_dev_1,SESSION=1 -->

## Scope

- Evidence-only live Qwen SFT data-prep packing attempt using the supervisor
  provided cephfs Qwen model/tokenizer path.
- Run real `sample=4`, `num_shards=1` packing first into the requested cephfs
  artifact root, without `--dry-run`.
- Run full `sample=null`, `num_shards=16` packing only if sample packing and
  validators pass.
- Run the focused static packing/decontamination validator shard.

## Boundaries

- No model download, GPU training, eval, endpoint call, W&B, cluster deploy,
  artifact upload, direct `main`/`master` push, or self-merge.
- No product code edits were made.

## Result

- Baseline / validated product commit:
  `0460c1f0262875fb27ae530d30cd80d805752851`.
- Branch: `intern_nem_dev_1/task208_ceph_qwen_packing_live_s1`.
- Cephfs model path was present:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Verified model files: `config.json`, `tokenizer.json`,
  `tokenizer_config.json`, `model.safetensors.index.json`, and 16 safetensors
  shards.
- Sample packing failed before tokenization/packing because the process cannot
  create the requested artifact root:
  `PermissionError: [Errno 13] Permission denied:
  '/mnt/cephfs/data/nemotron-live-validation'`.
- Focused validators passed: `53 passed in 2.12s`.
- Full 16-shard packing was not started because the sample packing gate did not
  pass.

## Artifacts

- Requested artifact root:
  `/mnt/cephfs/data/nemotron-live-validation/task208`.
- Requested cephfs artifact root and both requested output directories are
  absent:
  - `/mnt/cephfs/data/nemotron-live-validation`
  - `/mnt/cephfs/data/nemotron-live-validation/task208`
  - `/mnt/cephfs/data/nemotron-live-validation/task208/packed_qwen_sample4`
  - `/mnt/cephfs/data/nemotron-live-validation/task208/packed_qwen_full`
- Local fallback logs, because cephfs log creation failed:
  - `/tmp/nemotron-live-validation/task208/logs/qwen_sample4_packing_ceph_permission_failure.log`
  - `/tmp/nemotron-live-validation/task208/logs/qwen_sample4_packing_failure_summary.txt`
  - `/tmp/nemotron-live-validation/task208/logs/static_validators_pytest.log`
- Local generated job configs from the failed sample command:
  - `.nemotron/jobs/20260530-160629-super3-data-prep-sft/job.yaml`
  - `.nemotron/jobs/20260530-160629-super3-data-prep-sft/train.yaml`
  - `.nemotron/jobs/20260530-160845-super3-data-prep-sft/job.yaml`
  - `.nemotron/jobs/20260530-160845-super3-data-prep-sft/train.yaml`

No `blend.json`, `splits/`, `runs/*/config.json`, packed shards, manifest, or
parquet checksum files were produced.

## Resource Evidence

- `config.json` SHA-256:
  `a1ee086a68d0cbfc87316da00ba4b8507bd1292978108e2496201a30a450f438`.
- `tokenizer_config.json` SHA-256:
  `a62ff0a2472a0fa1b8eaabcb57c59b58afa42a22831dc141400b6e0cf2b65ce3`.
- `tokenizer.json` SHA-256:
  `aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4`.
- `model.safetensors.index.json` SHA-256:
  `8dde190b862c7c80ec7403c6495de00c60bbaf246ed479cee4506284989c584c`.
- Safetensors shard count: `16`.
- Safetensors total bytes: `61066575656`.
- Source blend SHA-256:
  `bd7403286f6736302d9ea1763c238f85f4fda4ca7fc99f4e12fec920ae84a201`.
- Source manifest SHA-256:
  `d5a1101ab5cb3bcb302ac8b6afe6f578adb65c43fb27edbf4a3c806c9042e7b8`.
- Source blend workload: `987943` rows, `3408133421` input bytes.

## Blocker

Grant this host/process write permission to create and write below:

`/mnt/cephfs/data/nemotron-live-validation`

Then rerun the sample command first. Full 16-shard packing should remain gated
on sample packing success plus validator success.
