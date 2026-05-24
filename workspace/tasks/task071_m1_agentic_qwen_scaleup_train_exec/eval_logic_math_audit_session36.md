# Session 36 AIME/HMMT Eval Artifact Audit

## Purpose

Session 35 corrected MMLU-Pro by replacing an invalid-heavy completions path
with a parser-aligned chat JSON path. This session audits the existing original
Qwen3-30B-A3B AIME25 and HMMT artifacts to separate model correctness from
output-length and final-answer parsing failures.

## Inputs

Raw run root:
`vm4vpn:/tmp/task071_vpn_eval_qwen30b_original_full`

Audited files copied locally:

- AIME score cache: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/aime_score_cache.db`
- AIME response cache: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/aime_response_cache.db`
- HMMT output JSONL: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/hmmt_output.jsonl`
- Audit summary: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/summary.json`

Reusable audit script:
`workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/analyze_math_eval_artifacts.py`

## AIME25

Current command used `simple_evals.aime_2025_nemo` with chat endpoint,
`max_tokens=2048`, `temperature=0.0`, `top_p=1e-5`, 30 problems x 10 repeats.

| Metric | Value |
|---|---:|
| Score rows | 300 |
| Unique prompts | 30 |
| Score | 0.1666666667 |
| Correct rows | 50 |
| Finish reason: length | 234 |
| Finish reason: stop | 66 |
| Rows with boxed final answer | 76 |
| Correct with boxed answer | 50 |
| Correct without boxed answer | 0 |
| Wrong with boxed answer | 26 |

Interpretation:

- The scored path is not missing chat-template use; it calls a chat endpoint.
- The dominant failure is that most generations never reach a boxed final answer
  within `2048` tokens.
- Every correct AIME row in the score cache contains a boxed answer, which means
  the local exact/sympy scorer depends on the final-answer contract being met.

## HMMT

Current command used `nemo_skills.ns_hmmt_feb2025` with chat endpoint,
`tokens_to_generate=2048`, `temperature=0.0`, `top_p=1e-5`, 30 entries.

| Metric | Value |
|---|---:|
| Rows | 30 |
| Symbolic correct rows | 2 |
| Symbolic correct percent | 6.6666666667 |
| Finish reason: length | 28 |
| Finish reason: stop | 2 |
| Rows with parsed predicted answer | 2 |
| Rows with boxed answer | 2 |
| Rows whose raw generation contains expected answer text | 4 |
| Length rows containing expected answer but no parsed prediction | 2 |

Interpretation:

- HMMT has the same truncation pattern as AIME: `28/30` generations end at the
  token cap.
- There are at least two cases where the raw generation contains the expected
  answer text but the run still records `predicted_answer=null`, because the
  model continues and never emits a parser-readable final boxed answer before
  truncation.
- The `no_answer` rate is therefore partly an output-contract failure, not only
  a math-skill failure.

## Conclusion

AIME25 and HMMT are already using a chat endpoint, so the largest confirmed gap
is not the absence of chat-template routing. The actionable issue is that the
current prompts ask for detailed reasoning while the generation cap is only
2048 tokens, and both scorers require a standardized final answer. A corrected
math eval path should use either much larger output budgets with a long-context
endpoint or a stricter concise prompt that forces `\boxed{...}` and immediate
stop after the final answer.

The current full-selected AIME/HMMT numbers remain valid task071 regression
records, but they should not be read as official-comparable Qwen math benchmark
scores.
