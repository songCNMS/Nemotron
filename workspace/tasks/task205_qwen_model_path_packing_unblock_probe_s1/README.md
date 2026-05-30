# task205_qwen_model_path_packing_unblock_probe_s1

<!-- METADATA:STATUS=Complete,ASSIGNEE=intern_nem_dev_1,SESSION=1 -->

## Scope

- Evidence-only probe for the Qwen3-30B-A3B-Instruct-2507 tokenizer/model
  resource needed to unblock task202's tiny Qwen packing smoke.
- Run actual `sample=4`, `num_shards=1` Qwen SFT data-prep packing only if a
  usable Qwen3-30B-A3B-Instruct-2507 tokenizer/model directory is mounted.
- If absent, rerun the Qwen data-prep compile dry-run under the task205 artifact
  root and report the exact mount request.
- Run the focused static packing/decontamination validator shard.

## Boundaries

- No model download, product code edit, training/eval launch, endpoint call,
  W&B, cluster, deploy, artifact upload, direct `main`/`master` push, or
  self-merge.

## Result

- Baseline / validated product commit:
  `0460c1f0262875fb27ae530d30cd80d805752851`.
- Branch: `intern_nem_dev_1/task205_qwen_model_path_packing_unblock_probe_s1`.
- Exact requested path:
  `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507` was absent.
- `/mnt/3fs` itself was absent, so the expected shared model mount is not
  present on this host.
- Bounded nearby checks found no usable replacement in
  `/work-agents/shared_models` or `/work-agents/models` because those paths were
  absent.
- A bounded check of the previously observed local candidate
  `/work-agents/AxisAgentic/agentic/model_assets/qwen3_thinking_a3b` found only
  `tokenizer_config.json` and no usable tokenizer/model files, so it was not
  used.
- Qwen dry-run: passed.
- Actual tiny packing smoke: skipped because no usable Qwen3-30B-A3B-Instruct
  tokenizer/model directory was available.
- Focused validators: passed, `53 passed in 2.18s`.

## Artifacts

- Artifact root: `/tmp/nemotron-live-validation/task205`.
- Model path probe log:
  `/tmp/nemotron-live-validation/task205/logs/model_path_probe.log`.
- Qwen dry-run log:
  `/tmp/nemotron-live-validation/task205/logs/qwen_data_prep_dry_run.log`.
- Static validator log:
  `/tmp/nemotron-live-validation/task205/logs/static_validators_pytest.log`.
- No `/tmp/nemotron-live-validation/task205/packed_qwen` directory,
  `blend.json`, `splits/`, `runs/*/config.json`, packed shards, manifest, or
  parquet checksums were produced because actual packing was blocked.

## Mount Request

Mount or provide a local equivalent for the Qwen model/tokenizer snapshot at:

`/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507`

The directory should be a usable Hugging Face model/tokenizer directory for
Qwen3-30B-A3B-Instruct-2507, including tokenizer files such as
`tokenizer_config.json` and `tokenizer.json`, model config such as
`config.json`, and the Qwen chat-template metadata needed by
`chat_template=tokenizer`. If the canonical path cannot be mounted, provide an
explicit approved local path for `SUPER3_M1_QWEN_HF_MODEL` or
`SUPER3_M1_TOKENIZER_MODEL`; do not substitute a different model family.

## Full Data-Prep Estimate

- Current full `qwen_agentic_v0` defaults are `sample=null`, `num_shards=16`,
  `pack_size=4096`, `algorithm=first_fit_shuffle`, train/valid/test ratios
  `0.98/0.01/0.01`, `chat_template=tokenizer`, and
  `chat_template_kwargs.enable_thinking=false`.
- With 16 completed shards, current split logic would assign approximately
  14 train shards, 1 valid shard, and 1 test shard.
- The current task071 blend contains `987943` JSONL rows and `3408133421`
  input bytes across two weighted datasets.
- Runtime and packed Parquet size remain unmeasured until the Qwen
  tokenizer/model directory is mounted.
