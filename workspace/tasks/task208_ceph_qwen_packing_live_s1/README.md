# task208_ceph_qwen_packing_live_s1

<!-- METADATA:STATUS=Complete,ASSIGNEE=intern_nem_dev_1,SESSION=2 -->

## Scope

- Evidence-only live Qwen SFT data-prep packing using the supervisor-provided
  cephfs Qwen model/tokenizer path.
- First run real `sample=4`, `num_shards=1` packing without `--dry-run`.
- If sample packing and focused validators pass, run full `sample=null`,
  `num_shards=16` packing.
- Preserve the original unwritable-root failure as historical evidence, but use
  the corrected `/mnt/cephfs/data/processing/...` root as the final artifact
  root.

## Boundaries

- No model download, GPU training, eval, endpoint call, W&B, cluster deploy,
  artifact upload, direct `main`/`master` push, or self-merge.
- No product code edits were made.

## Result

- Baseline / validated product commit:
  `0460c1f0262875fb27ae530d30cd80d805752851`.
- Branch: `intern_nem_dev_1/task208_ceph_qwen_packing_live_s1`.
- Superseded historical evidence head:
  `e197fb1af7ca4ad48e0573707fbe74edbb935311`.
- Corrected artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208`.
- Cephfs model path was present:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Corrected-root sample packing: passed.
- Focused validators after sample: passed, `53 passed in 2.09s`.
- Corrected-root full 16-shard packing: passed.

## Final Artifacts

- Sample splits:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_sample4/sample-4/splits`.
- Sample metrics: `total_sequences=8`, `total_tokens=5488`,
  `num_shards=1`, `pack_size=4096`, `elapsed_sec=115.67831802368164`.
- Sample artifacts include:
  - `packed_qwen_sample4/sample-4/blend.json`
  - `packed_qwen_sample4/sample-4/splits/metadata.json`
  - `packed_qwen_sample4/sample-4/runs/eb259e9d416487c5/config.json`
  - 2 parquet data files and 1 train split symlink.
- Full splits:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_full/splits`.
- Full metrics: `total_sequences=987770`, `total_tokens=672687706`,
  `num_shards=16`, `pack_size=4096`, `elapsed_sec=253.65463423728943`.
- Full artifacts include:
  - `packed_qwen_full/blend.json`
  - `packed_qwen_full/splits/metadata.json`
  - `packed_qwen_full/runs/7f636cefa24d6f6a/config.json`
  - 32 parquet data files and 18 split symlinks
    (`train=16`, `valid=1`, `test=1`).
- Artifact sizes:
  - task208 root: `4.0G`
  - sample output: `57K`
  - full output: `4.0G`
  - logs: `94K`
- Checksum manifest:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/logs/task208_output_checksums.sha256`
  with 47 entries.
- Logs:
  - `logs/qwen_sample4_packing.log`
  - `logs/static_validators_pytest.log`
  - `logs/qwen_full_packing.log`

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

## Historical Root Failure

- The first task208 root
  `/mnt/cephfs/data/nemotron-live-validation/task208` was unwritable from the
  local CPU process.
- The historical sample command failed before packing with:
  `PermissionError: [Errno 13] Permission denied:
  '/mnt/cephfs/data/nemotron-live-validation'`.
- Local fallback historical log:
  `/tmp/nemotron-live-validation/task208/logs/qwen_sample4_packing_ceph_permission_failure.log`.

## Residual Risk

- PM reported a cross-node visibility mismatch: local CPU can see the corrected
  root artifacts under `/mnt/cephfs/data/processing/...`, but dev_2/NemTron
  cannot see those local CPU-created task208 artifacts at the same path.
- dev_2 has been told to stage sample/full artifacts to a NemTron-visible
  task209 input path via SSH tar/rsync.
