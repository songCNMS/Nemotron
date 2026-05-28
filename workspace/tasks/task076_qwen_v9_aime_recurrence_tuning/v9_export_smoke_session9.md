# V9 Export and AIME06 Smoke - Session 9

## HF Export

- Source NeMo/Megatron checkpoint: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/checkpoints/iter_0000192`
- Source HF metadata/tokenizer: `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- HF export path: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/hf_export_iter_0000192`
- Export log: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/logs/export_iter_0000192.log`
- Export manifest: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/hf_export_iter_0000192/task076_export_manifest.json`
- Model id: `task076-qwen3-30b-a3b-agentic-sft-hard-math-recurrence-v9-iter0000192-hf`

Validation:

- Export log contains `Success: All tensors from the original checkpoint were written.` and `EXPORT_DONE`.
- HF artifact has `16` safetensors shards totaling `61066575144` bytes.
- `AutoConfig` loads as `model_type=qwen3_moe`, `num_hidden_layers=48`, `num_experts=128`, `num_experts_per_tok=8`.
- `AutoTokenizer` loads as `Qwen2TokenizerFast`; chat template is present.

## Serving

- Tmux session: `task076_qwen_v9_iter0192_sglang_smoke`
- SGLang config: `tp=4`, `dp=2`, `context_length=16384`, `mem_fraction_static=0.84`, `max_running_requests=16`
- Serving log: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/logs/sglang_iter0000192_smoke_16384.log`
- `/v1/models` returned the expected model id and `max_model_len=16384`.
- A minimal chat smoke response to `Reply with exactly: ready` was pathological: ` the   the the the the the`.
- The endpoint was stopped after the smoke; port `30000` was clear and GPU memory returned to idle.

## Targeted AIME06 Smoke

- Corrected runner basis: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/Nemotron/workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/run_corrected_math_full_eval.py`
- AIME cache: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/session91_corrected_eval/inputs/aime_score_cache.db`
- Row selection: load all corrected AIME rows, then select sample ids starting with `aime_06_`.
- Expected answer: `907`.
- Output summary: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/targeted_smoke/aime06/summary.json`
- Raw rows: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/targeted_smoke/aime06/results.jsonl`

Protocol:

- Prompt variant: `original`
- `max_tokens=8192`
- `temperature=0.0`
- `top_p=1e-5`
- Parallelism: `4`

Results:

| Metric | Value |
|---|---:|
| Rows | `10` |
| Status `ok` | `10` |
| Finish reason `length` | `10` |
| Parsed rows | `0` |
| Correct rows | `0` |
| Exact normalized accuracy | `0.0` |
| Average completion tokens | `8192` |

Per-row predictions were all `null`: `aime_06_r01` through `aime_06_r10` each ran to the token limit without a final boxed answer.

## Interpretation

V9 does not recover the `aime_06` recurrence behavior. The smoke exposed a broader generation-quality failure: even the trivial chat smoke degenerated, and every `aime_06` repeat hit the `8192` token cap without parsing. A full corrected MMLU-Pro/AIME25/HMMT gate is not useful until the V9 training/export lineage is diagnosed.

Next technical checks:

- Audit the V9 training loss jump against the V8 starting checkpoint and confirm the V8 checkpoint load path was actually used.
- Inspect V9 packed label masks/chat rendering and compare a small decoded sample against the V8 packing contract.
- If the checkpoint lineage is valid, run a lower-risk probe from an earlier V9 checkpoint or rerun a shorter V9 from V8 with corrected data weighting.
