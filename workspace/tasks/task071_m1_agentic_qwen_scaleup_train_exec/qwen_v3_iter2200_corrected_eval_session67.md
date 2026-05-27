# Qwen v3 Iter 2200 Corrected Eval - Session 67

Run: `task071_qwen30b_a3b_math_reasoning_replay_v3`

Selected checkpoint: `iter_0002200`

Remote run root: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_reasoning_replay_v3`

## Export

- Megatron checkpoint: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_reasoning_replay_v3/checkpoints/iter_0002200`
- HF export path: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_reasoning_replay_v3/hf_export_iter_0002200`
- Export tmux session: `task071_qwen_v3_iter2200_export_gpu5`
- Export device: `CUDA_VISIBLE_DEVICES=5`
- Export log: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_reasoning_replay_v3/logs/export_iter_0002200_gpu5.log`
- Model id: `task071-qwen3-30b-a3b-agentic-sft-math-reasoning-replay-v3-iter0002200-hf`

Megatron-Bridge export completed with `Success: All tensors from the original checkpoint were written.` and `EXPORT_DONE`.

HF artifact validation:

| Check | Value |
|---|---:|
| Export size | about `57G` |
| Safetensors shards | `16` |
| Has `model.safetensors.index.json` | yes |
| Has `chat_template.jinja` | yes |
| HF `model_type` | `qwen3_moe` |
| Hidden layers | `48` |
| Experts | `128` |
| Experts per token | `8` |
| Vocab size | `151936` |
| Tokenizer | `Qwen2TokenizerFast` |
| Tokenizer vocab size | `151669` |

Manifest: `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_math_reasoning_replay_v3/hf_export_iter_0002200/task071_export_manifest.json`

## Serving

- Tmux session: `task071_qwen_v3_iter2200_sglang_full_eval`
- Endpoint: `NemTron:30000`, exposed locally through SSH tunnel as `http://127.0.0.1:13000`
- SGLang config: `tp=4`, `dp=2`, `context_length=16384`, `mem_fraction_static=0.84`, `max_running_requests=16`
- `/v1/models`: returned `max_model_len=16384`
- Chat smoke: prompt `Reply with exactly: ready` returned exact `ready`

The endpoint and local tunnel were stopped after eval. Final GPU check showed all 8 H200 GPUs idle with about `1 MiB` used each, and port `30000` was clear.

## Corrected Eval

MMLU-Pro full:

- Output: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/qwen_v3_iter2200_session67/mmlu_corrected_full`
- Rows: `12032`
- Prompting: chat JSON answer-only
- Generation: `max_tokens=64`, `temperature=0.0`, `top_p=1e-5`
- Status: `ok=12032/12032`
- Finish: `stop=12032/12032`
- Parsed rate: `1.0`
- Accuracy: `0.5525265957446809`

MMLU-Pro 20-per-category slice:

- Output: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/qwen_v3_iter2200_session67/mmlu_corrected_20percat`
- Rows: `280`
- Accuracy: `0.6107142857142858`
- Parsed rate: `1.0`
- Finish: `stop=280/280`

Math full:

- Output: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/qwen_v3_iter2200_session67/math_corrected_full`
- Rows: AIME25 `300`, HMMT `30`
- Prompting: original benchmark prompts
- Generation: `max_tokens=8192`, `temperature=0.0`, `top_p=1e-5`

| Task | Rows | Status OK | Stop | Length | Parsed rate | Score |
|---|---:|---:|---:|---:|---:|---:|
| AIME25 | 300 | 300 | 282 | 18 | 0.94 | 0.08666666666666667 |
| HMMT | 30 | 30 | 30 | 0 | 1.0 | 0.0 |

Auxiliary math slices:

- `math_corrected_5each`: AIME25 `0/5`, HMMT `0/5`; both parsed rate `1.0`.
- `math_corrected_30each`: AIME25 `0/30`, HMMT `0/30`; both parsed rate `1.0`.

## Comparison

Original reference uses Session 47 corrected metrics. Iter3000 is Session 59 `task071_qwen30b_a3b_math_final_answer_qwen_chat_v2`.

| Metric | Original Qwen3-30B-A3B | Iter3000 qwen-chat | V3 iter2200 | V3 delta vs original | V3 delta vs iter3000 |
|---|---:|---:|---:|---:|---:|
| MMLU-Pro corrected accuracy | 0.562001329787234 | 0.5340757978723404 | 0.5525265957446809 | -0.009474734042553168 | +0.018450797872340496 |
| AIME25 corrected accuracy | 0.5333333333333333 | 0.06666666666666667 | 0.08666666666666667 | -0.44666666666666666 | +0.020000000000000004 |
| HMMT corrected exact percent | 43.333333333333336 | 0.0 | 0.0 | -43.333333333333336 | 0.0 |

Parser coverage:

| Metric | Original | Iter3000 qwen-chat | V3 iter2200 |
|---|---:|---:|---:|
| MMLU-Pro parsed rate | 1.0 | 1.0 | 1.0 |
| AIME25 parsed rate | 0.65 | 0.9266666666666666 | 0.94 |
| HMMT parsed rate | 0.6666666666666666 | 1.0 | 1.0 |

## Gate Readout

- MMLU-Pro passes the Session 60 gate: V3 full score `0.5525265957446809` is above `0.55` and only `0.00947` below original corrected.
- AIME25 fails the Session 60 math correctness gate: V3 reaches `0.08666666666666667`, below the target `0.20`, though it improves over iter3000 by `0.02`.
- HMMT fails the Session 60 math correctness gate: V3 remains at `0.0`.
- AIME/HMMT parser coverage passes the parser gate, so the remaining blocker is reasoning correctness rather than final-answer extraction.

## Decision

`reasoning_replay_v3` materially improves corrected MMLU-Pro versus iter3000 and keeps output formatting healthy. It does not recover hard math reasoning enough for promotion: AIME25 remains far below original and HMMT is still zero under the corrected exact-normalized protocol.

The next code/data step should analyze the V3 corrected math outputs by problem cluster and prepare a narrower hard-math recovery recipe: more verified full-solution replay for AIME/HMMT-like rows, stronger rejection of shallow or copied solutions, and a checkpoint gate that requires AIME/HMMT correctness improvement before a long run is promoted.
