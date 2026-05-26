# Session 76 Qwen V5 Hard-Math Precision Plan

## Rationale

V4 kept Qwen chat-template alignment and improved MMLU-Pro versus V3, but it did not recover AIME25/HMMT correctness. Session 75 also ruled out a current thinking-template mismatch for the checked Qwen tokenizer/export. The next recipe therefore narrows the math sidecar instead of adding more broad math replay.

## New Strategy

Strategy name: `hard_math_precision_v5`

- Keeps the base M1 agentic SFT train JSONL for search, coding, tool-calling, reasoning, and general coverage.
- Uses the same contamination-safe verified full-solution source pool as V4.
- Promotes only high-confidence hard rows into the hard sidecar:
  - `math_competition_numeric`
  - answer-seeking prompt and no proof-like prompt
  - prompt length `120..2400`
  - solution length `1000..9000`
  - at least `4` non-empty solution lines
  - boxed final answer within the last `1800` characters
  - V4 topic keyword match
- Default pre-pack sample fractions:
  - hard verified full-solution: `0.6`
  - broad verified full-solution: `0.0`
  - final-answer auxiliary: `0.0`
  - format repair: `0.0`

## Sizing Check

Checked against existing V4 prepared JSONLs:

| Source file | Rows | V5 precision rows | Rate |
|---|---:|---:|---:|
| `agentic_sft_v0_math_hard_verified_full_solution_train.jsonl` | 184551 | 114305 | 0.619368 |
| `agentic_sft_v0_math_verified_full_solution_train.jsonl` | 90104 | 0 | 0.000000 |

With default hard fraction `0.6`, the next full data-prep run should duplicate roughly `68583` strict hard-solution rows before packing, plus the unchanged base train JSONL.

## Generated Script Bundle

Output root:

`/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_precision_v5`

Key settings:

- Base model: `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- Megatron checkpoint: `/work-agents/intern_nemontron_code_reading/task071_qwen30b_a3b_sft_train_exec/pretrained_megatron_qwen3_30b_a3b_instruct_2507`
- Chat template: `tokenizer`
- Chat template kwargs: `enable_thinking=false`, `truncate_history_thinking=false`
- Epochs: `0.2`
- GBS: `8`
- LR: `2e-7`
- Min LR: `8e-8`
- Eval/save interval: `400`
- Eval config: `m1_full_basket_launcher_available`

Scripts:

- Local data prep: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_precision_v5/run_local_data_prep.sh`
- Sync to NemTron: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_precision_v5/sync_to_nemtron.sh`
- Remote train: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_precision_v5/run_nemtron_train.sh`
- Eval dry-run: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_precision_v5/run_eval_basket_dry_run.sh`

## Verification

- `py_compile` on changed strategy/planner modules: passed.
- `ruff check` on changed strategy/planner/tests: passed.
- Focused new tests: `4 passed`.
- Full M1 SFT + Qwen scale-up planner tests: `81 passed, 1 skipped`.
