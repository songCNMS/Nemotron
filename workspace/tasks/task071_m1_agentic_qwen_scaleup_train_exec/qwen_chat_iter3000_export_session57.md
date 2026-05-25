# Qwen Chat-Aligned Iter 3000 Export - Session 57

## Candidate

Run: `task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`

Selected checkpoint:

- Megatron checkpoint: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/checkpoints/iter_0003000`
- Selection metric: validation loss/PPL `0.3531853/1.423595`
- Latest observed validation during export: iter `5500` loss/PPL `0.3557427/1.427240`
- Decision: iter `3000` remains the best observed validation point through iter `5500`

## Export

CPU-only export was attempted first and failed because TransformerEngine attention requires CUDA in this Megatron-Bridge path. A GPU export was then launched on GPU 5 while the training run continued.

- Export tmux session: `task071_qwen_chat_iter3000_export_gpu5`
- Export device: `CUDA_VISIBLE_DEVICES=5`
- Export log: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/logs/export_iter_0003000_gpu5.log`
- HF export path: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/hf_export_iter_0003000`
- Model id: `task071-qwen3-30b-a3b-agentic-sft-qwen-chat-iter0003000-hf`

The export completed with `Success: All tensors from the original checkpoint were written.` and `EXPORT_DONE`.

## Artifact Validation

- Export size: about `57G`
- Safetensors shards: `16`
- Index: `model.safetensors.index.json`
- Tokenizer/config files: present, including `tokenizer.json`, `tokenizer_config.json`, `config.json`, and `chat_template.jinja`
- HF config validation: `model_type=qwen3_moe`, `num_hidden_layers=48`, `num_experts=128`, `num_experts_per_tok=8`, `vocab_size=151936`
- HF tokenizer validation: `Qwen2TokenizerFast`, tokenizer vocab size `151669`
- Manifest: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/hf_export_iter_0003000/task071_export_manifest.json`

## Metrics Refresh

Refreshed local metrics from the NemTron train log:

- Plot: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/metric_curves_session57_iter5500.png`
- Health summary: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/metrics/health_summary.json`
- Latest parsed train iter: `5570/8740`
- Progress: `63.73%`
- Recent-50 train loss mean: `0.378527694`
- Skipped/nan: `0/0`

Validation trend:

- iter `3000`: `0.3531853/1.423595`
- iter `5000`: `0.3781844/1.459632`
- iter `5500`: `0.3557427/1.427240`

Iter `5500` recovered strongly versus iter `5000`, but it has not beaten iter `3000`.

## Eval Entry Status

No SGLang endpoint is active on NemTron ports `30000/30001` at the end of this session. The training job is still using all 8 H200 GPUs, with roughly 55G-61G free memory per GPU at the latest check.

For corrected comparison, serve the exported HF path with:

- SGLang model path: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_final_answer_qwen_chat_v2/hf_export_iter_0003000`
- Model id: `task071-qwen3-30b-a3b-agentic-sft-qwen-chat-iter0003000-hf`
- Recommended shape for corrected math: `tp=4`, `dp=2`, `context_length=16384`
- Launcher path: expose NemTron `:30000` to `vm4vpn:127.0.0.1:13000`, then run corrected MMLU-Pro/AIME25/HMMT comparison against that endpoint.
