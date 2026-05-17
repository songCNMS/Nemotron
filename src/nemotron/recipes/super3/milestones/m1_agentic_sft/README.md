# M1 Agentic SFT v0 Data Entry

This milestone entry converts the M0 NeMo-Gym JSONL smoke data into OpenAI
chat/tool records that can be consumed by the existing Super3 SFT data pipeline.

The entry is intentionally narrow:

- Use M0 `train-split.jsonl` as Agentic SFT v0 training input.
- Keep M0 `val-split.jsonl` as a shadow file for inspection and contamination
  checks, not as SFT training data.
- Preserve source dataset, license, M0 environment, reward type, and intended
  M1 use in each SFT record.
- Emit a `data_blend_agentic_sft_v0.json` file that can be passed to
  `nemotron super3 data prep sft`.

## Run

```bash
python src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py \
  --m0-input-dir /mnt/3fs/data/lei.song/nemotron/m0_data_env_foundation/smoke-20260516-100x25 \
  --output-dir /mnt/3fs/data/lei.song/nemotron/m1_agentic_sft_v0/from-m0-smoke-20260516
```

The generated blend can then drive the packed SFT data-prep stage:

```bash
uv run nemotron super3 data prep sft -c agentic_v0 \
  blend_path=/mnt/3fs/data/lei.song/nemotron/m1_agentic_sft_v0/from-m0-smoke-20260516/data_blend_agentic_sft_v0.json
```

After data prep writes packed `splits/`, generate a reproducible training
plan and launch script:

```bash
python src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_m1_agentic_sft_training.py \
  --packed-sft-dir /mnt/3fs/data/lei.song/nemotron/m1_agentic_sft_v0/packed-expanded-20260517-300x80/splits \
  --pretrained-checkpoint /mnt/3fs/data/lei.song/nemotron/checkpoints/super3-pretrain/checkpoints \
  --save-dir /mnt/3fs/data/lei.song/nemotron/m1_agentic_sft_v0/training-runs/m1-agentic-sft-v0/checkpoints \
  --output-dir /mnt/3fs/data/lei.song/nemotron/m1_agentic_sft_v0/train-plans \
  --run-name m1-agentic-sft-v0
```

The planner validates packed train/valid shards, reads `metadata.json`, infers
the tokenizer path, computes `train_iters` from packed train rows when possible,
and writes:

```text
<output-dir>/<run-name>/
├── training_manifest.json
├── run_m1_agentic_sft.sh
└── report.md
```

## Output

```text
<output-dir>/
├── agentic_sft_v0_train.jsonl
├── agentic_sft_v0_val_shadow.jsonl
├── data_blend_agentic_sft_v0.json
├── manifest.json
└── report.md
```

## Supervision Mapping

| M0 environment | M1 supervision |
|---|---|
| `search_grounded_qa` | User prompt with retrieved passages, assistant short answer |
| `code_execution_python` | User coding prompt, assistant reference Python solution |
| `general_tool_calling` | User/tool schema prompt, assistant `tool_calls` |
| `math_reasoning_numeric` | User math prompt, assistant reference reasoning solution |
