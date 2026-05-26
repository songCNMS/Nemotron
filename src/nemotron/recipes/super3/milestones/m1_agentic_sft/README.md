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

For CPU workspaces that do not have the full Xenna runtime and HuggingFace
tokenizer stack installed, run the lightweight round-trip smoke first. It uses
the same M1 JSONL contract and Super3 chat template, a deterministic local
tokenizer, and writes a packed Parquet shard that is read back for schema and
loss-mask checks:

```bash
python src/nemotron/recipes/super3/milestones/m1_agentic_sft/run_m1_sft_roundtrip_smoke.py \
  --m1-jsonl /mnt/3fs/data/lei.song/nemotron/m1_agentic_sft_v0/from-m0-smoke-20260516/agentic_sft_v0_train.jsonl \
  --output-dir /tmp/nemotron-m1-agentic-sft-roundtrip \
  --require-environment terminal_basic_shell \
  --require-environment swe_pivot_patch_supervision \
  --require-environment tool_call_repair_negative \
  --overwrite
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
├── agentic_sft_v0_math_final_answer_train.jsonl
├── agentic_sft_v0_math_verified_full_solution_train.jsonl
├── agentic_sft_v0_math_final_answer_aux_train.jsonl
├── agentic_sft_v0_math_format_repair_train.jsonl
├── agentic_sft_v0_math_heldout_eval.jsonl
├── agentic_sft_v0_val_shadow.jsonl
├── data_blend_agentic_sft_v0.json
├── manifest.json
└── report.md
```

## Supervision Mapping

| M0 environment | M1 supervision |
|---|---|
| `search_grounded_qa` | User prompt with retrieved passages, assistant emits a grounded template referencing supporting-fact titles (e.g. `"Based on the retrieved passages ([1] Title), the answer is …"`) |
| `code_execution_python` | User coding prompt, assistant reference Python solution |
| `terminal_basic_shell` | User terminal task prompt, assistant emits the expected shell command as content-only supervision |
| `swe_pivot_patch_supervision` | User issue prompt with repo/instance metadata, assistant emits the gold unified diff patch |
| `general_tool_calling` | User/tool schema prompt, assistant `tool_calls` (multi-turn trajectories propagate `tool_call_id` so `tool` turns pair with the originating call) |
| `structured_outputs_json` | User JSON-mode prompt with schema in the system message, assistant emits the reference JSON object |
| `tool_call_repair_negative` | User sees a malformed or hallucinated tool-use artifact, assistant emits a repair message plus corrected `tool_calls` |
| `math_reasoning_numeric` | User math prompt, assistant preserves the reference solution, strips GSM8K `####` verifier markers, and appends `Final answer: \boxed{...}` when the reference lacks a boxed final answer |
| `math_competition_numeric` | User competition-math prompt, assistant preserves the reference solution and keeps or appends parser-readable `\boxed{...}` final-answer supervision |

Numeric math rows are also duplicated into
`agentic_sft_v0_math_final_answer_train.jsonl`. The generated
`data_blend_agentic_sft_v0.json` includes that sidecar as a separate dataset
with weight `1.0`, in addition to the base train JSONL weight `1.0`, so
`math_reasoning_numeric` and `math_competition_numeric` receive an effective
2x exposure for boxed final-answer supervision during packed SFT data prep.

For the Qwen math recovery path, pass
`--math-supervision-strategy reasoning_replay_v3`. This keeps the base
agentic SFT train JSONL, but writes separate math bucket files:

- `verified_full_solution`: rows with trusted solution traces and boxed final answers.
- `final_answer_aux`: answer-only rows, included as a low-weight formatting auxiliary.
- `format_repair`: solution-trace rows that needed an appended boxed final answer.
- `heldout_eval`: math rows reserved for corrected eval/dev, excluded from the training blend.

The v3 path applies those values as deterministic sidecar sampling fractions
before packing, because downstream SFT training consumes packed split
directories and may not preserve JSONL blend weights. Default fractions are
`1.0`, `0.2`, and `0.05` respectively; emitted sidecars use blend weight `1.0`
so their scale is controlled by row count. The legacy
`final_answer_sidecar_v1` strategy remains the default for reproducibility of
earlier runs.

## Difficulty signal (optional)

When the M0 health-baseline report is available, `prepare_m1_agentic_sft.py`
tags every SFT row with a `metadata.difficulty_bucket` ∈ `{trivial, hard,
unknown}` derived from the oracle policy (failing rows → `hard`, passing rows
→ `trivial`, anything we cannot prove failed → `unknown`). The manifest also
gets a per-split `difficulty_buckets` summary so curriculum samplers can
stratify before launching SFT.

```bash
python src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py \
  --m0-input-dir /mnt/3fs/data/lei.song/nemotron/m0_data_env_foundation/smoke-20260516-100x25 \
  --output-dir /mnt/3fs/data/lei.song/nemotron/m1_agentic_sft_v0/from-m0-smoke-20260516 \
  --m0-health-baseline /mnt/3fs/data/lei.song/nemotron/m0_data_env_foundation/smoke-20260516-100x25/health_baseline/health_baseline_report.json
```

When `--m0-health-baseline` is omitted, the script auto-discovers
`<m0-input-dir>/health_baseline/health_baseline_report.json` — the exact path
`run_m0_health_baseline.py` writes by default. If the file is unreadable (bad
JSON, wrong shape, missing fields) `prepare_m1_agentic_sft.py` logs a warning
and falls back to `difficulty_bucket=unknown` for every row instead of
silently downgrading the signal.

### System prompt handling (tool-calling is special)

`prompt_messages` rewrites the system prompt to `TOOL_CALLING_SYSTEM_PROMPT`
only for `general_tool_calling` records — the other environments keep the
M0-prepared system text verbatim. The override scrubs Hermes's verbose
`<tools>[]</tools>` system content so the M1 SFT input doesn't carry the
upstream prompt format. The same scrub is applied to user content so demo
`<tool_call>...</tool_call>` blocks shipped inside Hermes user turns don't
become part of the training prompt. The actual tool schema reaches the model
through the `tools` field rendered by the chat template, not through inline
XML in messages.
