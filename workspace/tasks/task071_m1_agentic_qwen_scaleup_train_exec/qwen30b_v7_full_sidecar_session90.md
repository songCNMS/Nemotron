# Qwen30B V7 Full-Sidecar Scale-Up - Session 90

## Run

- Run name: `task071_qwen30b_a3b_hard_math_long_reasoning_v7_full_sidecar`
- Remote root: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_long_reasoning_v7_full_sidecar`
- Output root: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_long_reasoning_v7_full_sidecar`
- Base model: `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- Training entrypoint: `src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py`

## Data

- M1 train rows: `983397`
- M1 val-shadow rows: `11354`
- Packed sequences: `988926`
- Packed tokens: `674237679`
- Packed train rows: `31258`
- Packed valid rows: `2546`
- Pack / seq length: `8192 / 8192`
- Train iters: `782`

## Planner Fix

The first remote launch used the generic `qwen_local_train.py` entrypoint and failed on the first forward pass:

`ValueError: During training, performance may degrade if MoE and tensor parallelism are enabled without also enabling sequence parallelism.`

The fix makes `plan_qwen_scaleup_run.py` auto-select `qwen3_30b_a3b_local_train.py` when the Qwen model path contains `30B-A3B`. That entrypoint sets the 30B-A3B MoE parallelism and `sequence_parallel=True`.

## Training Metrics

| Iteration | Train loss | Validation loss | Validation PPL |
|---:|---:|---:|---:|
| 400 | 0.4681214 | 0.4646536 | 1.591463 |
| 782 | 0.4521494 | 0.4461341 | 1.562261 |

- Final checkpoint: `checkpoints/iter_0000782`
- Checkpoint marker: `782`
- Max skipped iterations: `0`
- Max nan iterations: `0`
- Final metric figure: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_long_reasoning_v7_full_sidecar/metrics/metric_curves_session90_final_iter782.png`
- Health summary: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_long_reasoning_v7_full_sidecar/metrics/health_summary.json`

## HF Export

- Megatron checkpoint: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_long_reasoning_v7_full_sidecar/checkpoints/iter_0000782`
- HF export path: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_long_reasoning_v7_full_sidecar/hf_export_iter_0000782`
- Export log: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_long_reasoning_v7_full_sidecar/logs/export_iter_0000782_gpu5.log`
- Model id: `task071-qwen3-30b-a3b-agentic-sft-hard-math-long-reasoning-v7-full-sidecar-iter0000782-hf`
- Size: `61084232276` bytes
- Safetensors shards: `16`
- Manifest: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_long_reasoning_v7_full_sidecar/hf_export_iter_0000782/task071_export_manifest.json`

HF validation:

- `model_type=qwen3_moe`
- `num_hidden_layers=48`
- `num_experts=128`
- `num_experts_per_tok=8`
- tokenizer class `Qwen2TokenizerFast`
- chat template present

## Eval Entry

Use the corrected long-context protocol:

- Serve with SGLang `tp=4`, `dp=2`, `context_length=16384`
- Use model id `task071-qwen3-30b-a3b-agentic-sft-hard-math-long-reasoning-v7-full-sidecar-iter0000782-hf`
- Run corrected MMLU-Pro plus AIME25/HMMT with AIME `max_tokens=8192`

## Verification

- `pytest -q tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py -k "30b_entrypoint or wires_30b or scaleup_scripts_wire_data_training_and_eval"` -> `2 passed, 11 deselected`
- `ruff check src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_qwen_scaleup_run.py tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py` passed
- `python -m py_compile src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_qwen_scaleup_run.py` passed
