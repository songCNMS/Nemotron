# Qwen V5 Hard-Math Precision Launch - Session 77

## Scope

- Run name: `task071_qwen30b_a3b_hard_math_precision_v5`
- Strategy: `hard_math_precision_v5`
- Output root: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_precision_v5`
- Remote root: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_precision_v5`
- Source model: `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- Pretrained Megatron checkpoint: `/work-agents/intern_nemontron_code_reading/task071_qwen30b_a3b_sft_train_exec/pretrained_megatron_qwen3_30b_a3b_instruct_2507`

## Data Prep

- Local command: `bash /work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_precision_v5/run_local_data_prep.sh`
- M1 V5 hard verified full-solution source/written rows: `114305/68583`
- Broad verified full-solution source/written rows: `430662/0`
- Final-answer aux source/written rows: `29/0`
- Format-repair source/written rows: `321971/0`
- Heldout eval rows: `1419`
- Base agentic train coverage remains present across search, coding, tool-calling, terminal, SWE pivot, JSON structure, and math slices.

## Packing And Plan

- Packed metadata: `chat_template=tokenizer`, `enable_thinking=false`, `truncate_history_thinking=false`
- Packed sequences: `1051807`
- Packed tokens: `717870803`
- Train shards: `32`
- Packed train rows: `69750`
- Packed valid rows: `5116`
- Planned training: `train_iters=1744`, GBS `8`, lr `2e-7`, min lr `8e-8`, warmup `100`, eval/save interval `400`

## Remote Launch

- Sync command: `bash /work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_precision_v5/sync_to_nemtron.sh`
- Train command: `bash /work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_precision_v5/run_nemtron_train.sh`
- Tmux session: `task067_task071_qwen30b_a3b_hard_math_precision_v5`
- Startup evidence: bridge cache created `train_4096_train.npy`, `valid_4096_valid.npy`, and `packed_4096_metadata.json`; pretrained checkpoint loaded successfully; training loop started at iteration `0`.

## Iter 400 Snapshot

| Metric | Value |
|---|---:|
| Latest checkpoint marker | `400` |
| Saved checkpoint | `iter_0000400` |
| Train loss at iter 400 | `0.4834876` |
| Validation loss at iter 400 | `0.4572022` |
| Validation PPL at iter 400 | `1.579648` |
| Max skipped iterations | `0` |
| Max nan iterations | `0` |
| Latest monitored train iteration | `410/1744` |

## Metric Artifacts

- Train log: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_precision_v5/metrics/train.log`
- Health summary: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_precision_v5/metrics/health_summary.json`
- Train CSV: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_precision_v5/metrics/train_loss_points.csv`
- Validation CSV: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_precision_v5/metrics/validation_points.csv`
- Metric figure: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_precision_v5/metrics/metric_curves_session77_iter400.png`

## Tooling Fix

`plot_qwen_sft_metrics.py` now supports train-only startup curves before the first validation point. It still fails hard when no train points are parsed or when a parsed train loss is NaN.

## Verification

- `source /work-agents/.venv/bin/activate && python -m py_compile workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/plot_qwen_sft_metrics.py`
- `source /work-agents/.venv/bin/activate && python -m ruff check workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/plot_qwen_sft_metrics.py`
