# task202_qwen_live_data_prep_packing_smoke_s1

<!-- METADATA:STATUS=Complete,ASSIGNEE=intern_nem_dev_1,SESSION=1 -->

## Scope

- Evidence-only live validation shard for Qwen-safe Super3 M1 SFT
  data-prep/packing smoke.
- Validate the known task071 Qwen data blend and source manifest.
- Run the Qwen data-prep compile dry-run with `sample=4` and `num_shards=1`.
- Attempt actual tiny packing only if the requested Qwen tokenizer/model path is
  available.
- Run the required packing/decontamination/static validator shard.

## Boundaries

- Local data-prep/packing smoke and validators only.
- No product code changes were made.
- No training/eval launch, endpoint calls, W&B, cluster, deploy, artifact upload,
  direct `main`/`master` push, or self-merge.

## Result

- Base / validated product commit:
  `0460c1f0262875fb27ae530d30cd80d805752851`.
- Branch:
  `intern_nem_dev_1/task202_qwen_live_data_prep_packing_smoke_s1`.
- Source blend path: present.
- Source manifest path: present.
- Requested Qwen tokenizer/model path:
  `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507` was absent.
- Qwen data-prep dry-run: passed.
- Actual tiny packing smoke: skipped because the requested tokenizer/model path
  was unavailable.
- Static validators: passed, `53 passed in 2.26s`.

## Artifacts

- Artifact root: `/tmp/nemotron-live-validation/task202`.
- Dry-run log:
  `/tmp/nemotron-live-validation/task202/logs/qwen_data_prep_dry_run.log`.
- Static validator log:
  `/tmp/nemotron-live-validation/task202/logs/static_validators_pytest.log`.
- No `packed_qwen/blend.json`, `packed_qwen/splits/`, or
  `packed_qwen/runs/*/config.json` was created because only dry-run executed and
  actual packing was blocked by the missing tokenizer/model path.

## Source Evidence

- Source blend SHA-256:
  `bd7403286f6736302d9ea1763c238f85f4fda4ca7fc99f4e12fec920ae84a201`.
- Source manifest SHA-256:
  `d5a1101ab5cb3bcb302ac8b6afe6f578adb65c43fb27edbf4a3c806c9042e7b8`.
- Blend input rows: `987943`.
- Blend input bytes: `3408133421`.
- Manifest generated at: `2026-05-27T10:00:07+00:00`.
- Manifest used_in tag: `super3_agentic_sft_v0`.

## Full Data-Prep Estimate

- Current full Qwen config default uses `sample=null`, `num_shards=16`,
  `pack_size=4096`, train/valid/test ratios `0.98/0.01/0.01`, and the Qwen
  tokenizer chat template with `enable_thinking=false`.
- With 16 completed shards, current split logic would produce approximately
  14 train shards, 1 valid shard, and 1 test shard.
- The full run would process the two blend datasets totaling `987943` JSONL
  rows and `3408133421` input bytes. Runtime and packed Parquet size were not
  measured on this host because the Qwen tokenizer/model directory was missing.
