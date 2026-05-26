# Qwen Chat-Template Aligned Retrain Session 50

## Why This Run Exists

Session 49 added a Qwen SFT contract guard, then Session 50 checked the previously launched `task071_qwen30b_a3b_math_final_answer_v1` packed run. The artifact metadata lacked chat-template fields, and the underlying `packed_qwen/runs/*/config.json` confirmed the rows were rendered with `chat_template=super3`.

That means metadata repair would be invalid. The packed rows had to be regenerated with Qwen tokenizer chat template.

## New Packed Data

- Output root: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`
- Source M1 blend reused from: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_v1/m1_agentic_sft/data_blend_agentic_sft_v0.json`
- Packed artifact: `packed_qwen/splits`
- Tokenizer: `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- Chat template: `tokenizer`
- Chat kwargs: `{"enable_thinking": false, "truncate_history_thinking": false}`
- Total sequences: `1,850,191`
- Total tokens: `1,144,606,843`
- Train packed rows: `139,840`
- Valid packed rows: `2,576`
- Train iters: `8,740` at `epochs=0.5`, `global_batch_size=8`

Contract guard passed locally and on NemTron:

`validate_qwen_packed_sft_chat_contract(.../packed_qwen/splits, tokenizer_model=/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507)`

## Remote Training

- Remote root: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`
- Tmux session: `task067_task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`
- Train entrypoint: `src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py`
- GPUs: `0,1,2,3,4,5,6,7`
- TP/PP/EP entrypoint: Qwen3 30B-A3B local recipe
- LR settings: `optimizer.lr=1e-6`, `optimizer.min_lr=1e-7`, warmup `100`, cosine decay over `8740`
- Latest observed: iter `110/8740`, lm loss `0.4872709`, step time `2.948s`, skipped iterations `0`, nan iterations `0`
- GPU memory at startup: about `81-88GB` per H200

## Immediate Monitoring Target

- Confirm iter `500` eval/save point completes.
- Generate metric curves from the new train log.
- Compare early validation behavior against the stopped `v1` Super3-template run.
