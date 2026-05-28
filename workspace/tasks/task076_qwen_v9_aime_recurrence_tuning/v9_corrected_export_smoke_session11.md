# V9 Corrected Export and AIME06 Smoke - Session 11

## HF Export

- Source corrected Megatron checkpoint: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9_ckptroot_fix_s10/checkpoints/iter_0000192`
- Source HF metadata/tokenizer: `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- HF export path: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9_ckptroot_fix_s10/hf_export_iter_0000192`
- Export log: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9_ckptroot_fix_s10/logs/export_iter_0000192.log`
- Export manifest: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9_ckptroot_fix_s10/hf_export_iter_0000192/task076_export_manifest.json`
- Model id: `task076-qwen3-30b-a3b-agentic-sft-hard-math-recurrence-v9-ckptroot-fix-s10-iter0000192-hf`

Validation:

- Export log contains `Success: All tensors from the original checkpoint were written.` and `EXPORT_DONE`.
- HF artifact has `16` safetensors shards totaling `61066575144` bytes.
- `AutoConfig` loads as `model_type=qwen3_moe`, `num_hidden_layers=48`, `num_experts=128`, `num_experts_per_tok=8`.
- `AutoTokenizer` loads as `Qwen2TokenizerFast`; chat template is present.

## Serving

- Tmux session: `task076_v9_ckptroot_fix_iter0192_sglang_smoke`
- SGLang config: `tp=4`, `dp=2`, `context_length=16384`, `mem_fraction_static=0.84`, `max_running_requests=16`
- Serving log: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9_ckptroot_fix_s10/logs/sglang_iter0000192_ckptroot_fix_smoke_16384.log`
- `/v1/models` returned the expected model id and `max_model_len=16384`.
- Minimal chat smoke to `Reply with exactly: ready` returned exact `ready` with `finish_reason=stop`.
- The endpoint was stopped after the smoke; port `30000` was clear and all 8 H200 GPUs returned to idle.

## Targeted AIME06 Smoke

- Corrected runner basis: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/session91_corrected_eval/scripts/run_corrected_math_full_eval.py`
- AIME cache: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/session91_corrected_eval/inputs/aime_score_cache.db`
- Row selection: load all corrected AIME rows, then select sample ids starting with `aime_06_`.
- Expected answer: `907`.
- Output summary: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9_ckptroot_fix_s10/targeted_smoke/aime06/summary.json`
- Raw rows: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9_ckptroot_fix_s10/targeted_smoke/aime06/results.jsonl`

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
| Finish reason `stop` | `10` |
| Parsed rows | `10` |
| Correct rows | `0` |
| Exact normalized accuracy | `0.0` |
| Average completion tokens | `3540` |

Per-row predictions:

| Sample | Prediction |
|---|---:|
| `aime_06_r01` | `640` |
| `aime_06_r02` | `640` |
| `aime_06_r03` | `830` |
| `aime_06_r04` | `830` |
| `aime_06_r05` | `830` |
| `aime_06_r06` | `640` |
| `aime_06_r07` | `830` |
| `aime_06_r08` | `640` |
| `aime_06_r09` | `830` |
| `aime_06_r10` | `640` |

## Interpretation

The checkpoint-root fix repaired the major generation-quality failure seen in Session 9: the corrected export serves normally, the trivial chat smoke returns `ready`, and `aime_06` responses now stop with boxed parsed answers rather than running to the 8192-token cap. However, the targeted recurrence objective is still not recovered because all 10 repeats miss the expected answer `907`.

A full corrected MMLU-Pro/AIME25/HMMT gate is not justified from this targeted smoke alone. The next useful step is to inspect the corrected `aime_06` reasoning traces against the recurrence target and decide whether V9 needs data weighting/solution-form changes or a new V10 recurrence patch.
