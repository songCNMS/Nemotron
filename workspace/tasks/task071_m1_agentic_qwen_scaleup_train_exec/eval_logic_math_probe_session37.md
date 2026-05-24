# Session 37 Corrected Math Probe

## Purpose

Session 36 showed that the original Qwen3-30B-A3B AIME25/HMMT regression
artifacts are dominated by length finishes and missing final boxed answers. This
probe reruns a small math slice with a longer-context original endpoint and
three prompt variants to test whether parser alignment and output budget explain
the low task071 math scores.

## Inputs

Original full-selected raw run:
`vm4vpn:/tmp/task071_vpn_eval_qwen30b_original_full`

Probe endpoint:

| Field | Value |
|---|---|
| Host | NemTron |
| Model | `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507` |
| Served model id | `qwen3-30b-a3b-instruct-2507-original-math-probe` |
| SGLang context length | `16384` |
| Parallelism | `tp=4`, `dp=2` over 8 H200 GPUs |
| Launcher access | `vm4vpn` SSH tunnel at `http://127.0.0.1:13000/v1/chat/completions` |

Reusable probe script:
`workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/run_corrected_math_probe.py`

Local artifacts:

- Summary: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_probe_session37/summary.json`
- Raw results: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_probe_session37/results.jsonl`

## Protocol

| Setting | Value |
|---|---|
| AIME sample | 3 unique prompts from the prior simple-evals score cache |
| HMMT sample | 3 entries from the prior HMMT output JSONL |
| Prompt variants | `original`, `concise_boxed`, `answer_only` |
| Max tokens | `2048`, `4096`, `8192` |
| Sampling | `temperature=0.0`, `top_p=1e-5` |
| Requests | 54 |
| Runtime | 126.423 seconds |

The AIME score cache available locally does not contain expected answers, so
AIME rows are used only for finish/parse behavior. HMMT rows carry
`expected_answer`, so the probe records exact normalized correctness for that
small slice.

## AIME25 Results

| Prompt | Max tokens | Finish reasons | Parsed | Parsed rate |
|---|---:|---|---:|---:|
| original | 2048 | length=3 | 1/3 | 0.333333 |
| original | 4096 | length=2, stop=1 | 2/3 | 0.666667 |
| original | 8192 | stop=2, length=1 | 3/3 | 1.000000 |
| concise_boxed | 2048 | length=3 | 0/3 | 0.000000 |
| concise_boxed | 4096 | length=3 | 0/3 | 0.000000 |
| concise_boxed | 8192 | stop=2, length=1 | 2/3 | 0.666667 |
| answer_only | 2048 | stop=3 | 3/3 | 1.000000 |
| answer_only | 4096 | stop=3 | 3/3 | 1.000000 |
| answer_only | 8192 | stop=3 | 3/3 | 1.000000 |

Interpretation:

- The original AIME prompt reaches full parseability only at 8192 tokens on this
  sample.
- An answer-only final-answer contract reaches full parseability even at 2048
  tokens.
- The concise boxed prompt still produces length failures at 2048 and 4096, so
  simply asking for a boxed final line is not enough for this model.

## HMMT Results

| Prompt | Max tokens | Finish reasons | Parsed | Correct | Correct rate |
|---|---:|---|---:|---:|---:|
| original | 2048 | stop=2, length=1 | 2/3 | 2/3 | 0.666667 |
| original | 4096 | stop=3 | 3/3 | 2/3 | 0.666667 |
| original | 8192 | stop=3 | 3/3 | 2/3 | 0.666667 |
| concise_boxed | 2048 | length=2, stop=1 | 1/3 | 1/3 | 0.333333 |
| concise_boxed | 4096 | length=2, stop=1 | 1/3 | 1/3 | 0.333333 |
| concise_boxed | 8192 | stop=3 | 3/3 | 2/3 | 0.666667 |
| answer_only | 2048 | length=2, stop=1 | 1/3 | 1/3 | 0.333333 |
| answer_only | 4096 | length=2, stop=1 | 1/3 | 1/3 | 0.333333 |
| answer_only | 8192 | stop=2, length=1 | 2/3 | 2/3 | 0.666667 |

Interpretation:

- The old HMMT `2048`-token setting still truncates one of the three sampled
  original-prompt rows; increasing to 4096 removes truncation on this slice.
- The original prompt and 8192-token concise boxed prompt both reach full
  parser coverage on the HMMT sample.
- Correctness remains 2/3 for the best settings, so corrected math evaluation
  should report both parser coverage and accuracy.

## Conclusion

This probe confirms that the task071 original Qwen3-30B-A3B math scores are not
official-comparable Qwen math scores. They are regression-harness records under a
specific prompt, generation cap, and final-answer parser. A corrected full math
comparison should use a benchmark-consistent chat prompt, a long enough output
budget, and explicit parser-coverage reporting before treating AIME25/HMMT
numbers as model quality metrics.
