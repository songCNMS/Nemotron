# Qwen V4 Iter 0800 Corrected Eval - Session 74

Run: `task071_qwen30b_a3b_hard_math_recovery_v4`

Selected checkpoint: `iter_0000800`

Remote run root: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_recovery_v4`

## Export

- Megatron checkpoint: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_recovery_v4/checkpoints/iter_0000800`
- HF export path: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_recovery_v4/hf_export_iter_0000800`
- Export tmux session: `task071_qwen_v4_iter0800_export_gpu5`
- Export device: `CUDA_VISIBLE_DEVICES=5`
- Export log: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_recovery_v4/logs/export_iter_0000800_gpu5.log`
- Model id: `task071-qwen3-30b-a3b-agentic-sft-hard-math-recovery-v4-iter0000800-hf`

Megatron-Bridge export completed with `Success: All tensors from the original checkpoint were written.` and `EXPORT_DONE`.

HF artifact validation:

| Check | Value |
|---|---:|
| Export size | about `57G` |
| Safetensors shards | `16` |
| Has `model.safetensors.index.json` | yes |
| HF `model_type` | `qwen3_moe` |
| Hidden layers | `48` |
| Experts | `128` |
| Experts per token | `8` |
| Vocab size | `151936` |
| Tokenizer | `Qwen2TokenizerFast` |
| Tokenizer vocab size | `151669` |

Manifest: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_recovery_v4/hf_export_iter_0000800/task071_export_manifest.json`

## Serving

- Tmux session: `task071_qwen_v4_iter0800_sglang_full_eval`
- Endpoint: `NemTron:30000`, exposed through a live SSH tunnel as `http://127.0.0.1:13000`
- SGLang config: `tp=4`, `dp=2`, `context_length=16384`, `mem_fraction_static=0.84`, `max_running_requests=16`
- `/v1/models`: returned `max_model_len=16384`
- Chat smoke: prompt `Reply exactly: ready` returned exact `ready`

The endpoint and tunnel were stopped after eval. Final GPU check showed all 8 H200 GPUs idle, and port `30000` was clear.

## Corrected Eval

MMLU-Pro 20-per-category slice:

- Output: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/qwen_v4_iter0800_session74/mmlu_corrected_20percat_live_tunnel`
- Rows: `280`
- Accuracy: `0.6321428571428571`
- Parsed rate: `1.0`
- Finish: `stop=280/280`

MMLU-Pro full:

- Output: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/qwen_v4_iter0800_session74/mmlu_corrected_full`
- Rows: `12032`
- Prompting: chat JSON answer-only
- Generation: `max_tokens=64`, `temperature=0.0`, `top_p=1e-5`
- Status: `ok=12032/12032`
- Finish: `stop=12032/12032`
- Parsed rate: `1.0`
- Accuracy: `0.5587599734042553`

Math 30-each slice:

| Task | Rows | Status OK | Stop | Length | Parsed rate | Score |
|---|---:|---:|---:|---:|---:|---:|
| AIME25 | 30 | 30 | 30 | 0 | 1.0 | 0.0 |
| HMMT | 30 | 30 | 29 | 1 | 0.9666666666666667 | 3.3333333333333335 |

Math full:

- Output: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/qwen_v4_iter0800_session74/math_corrected_full`
- Rows: AIME25 `300`, HMMT `30`
- Prompting: original benchmark prompts
- Generation: `max_tokens=8192`, `temperature=0.0`, `top_p=1e-5`

| Task | Rows | Status OK | Stop | Length | Parsed rate | Score |
|---|---:|---:|---:|---:|---:|---:|
| AIME25 | 300 | 300 | 284 | 16 | 0.9466666666666667 | 0.08333333333333333 |
| HMMT | 30 | 30 | 29 | 1 | 0.9666666666666667 | 3.3333333333333335 |

## Comparison

Original reference uses Session 47 corrected metrics. V3 reference is Session 67 `iter_0002200`.

| Metric | Original Qwen3-30B-A3B | V3 iter2200 | V4 iter0800 | V4 delta vs original | V4 delta vs V3 |
|---|---:|---:|---:|---:|---:|
| MMLU-Pro corrected accuracy | 0.562001329787234 | 0.5525265957446809 | 0.5587599734042553 | -0.003241356382978733 | +0.006233377659574435 |
| AIME25 corrected accuracy | 0.5333333333333333 | 0.08666666666666667 | 0.08333333333333333 | -0.45 | -0.003333333333333341 |
| HMMT corrected exact percent | 43.333333333333336 | 0.0 | 3.3333333333333335 | -40.0 | +3.3333333333333335 |

Parser coverage:

| Metric | Original | V3 iter2200 | V4 iter0800 |
|---|---:|---:|---:|
| MMLU-Pro parsed rate | 1.0 | 1.0 | 1.0 |
| AIME25 parsed rate | 0.65 | 0.94 | 0.9466666666666667 |
| HMMT parsed rate | 0.6666666666666666 | 1.0 | 0.9666666666666667 |

## Gate Readout

- MMLU-Pro passes the gate: V4 full score `0.5587599734042553` is above `0.55` and only `0.00324` below original corrected.
- AIME25 fails the math correctness gate: V4 reaches `0.08333333333333333`, below target `0.20` and slightly below V3.
- HMMT fails the math correctness gate: V4 improves from V3 `0.0` to `3.3333333333333335`, still below target `10.0`.

## Decision

V4 hard-math recovery improves MMLU-Pro versus V3 and keeps parser coverage healthy. It does not recover AIME25, and HMMT gains only one correct row. This run should not be promoted as a hard-math win. The next data step should inspect V4 full math failures against V3 clusters and decide whether the hard-verified filter is too broad, too easy, or still missing verified AIME/HMMT-style solution trajectories.
