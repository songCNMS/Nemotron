# Session 32 Eval Logic Debug

## Scope

User observed that the original Qwen3-30B-A3B-Instruct-2507 baseline scores are
far below Qwen official numbers. This note records the root-cause check for the
task071 full-selected non-dry eval artifacts.

## Official Reference

Qwen official model card for `Qwen3-30B-A3B-Instruct-2507` reports:

| Benchmark | Official score |
|---|---:|
| MMLU-Pro | 78.4 |
| AIME25 | 61.3 |
| HMMT25 | 43.0 |

The same model card recommends using chat-template based inference, enough
generation length, and standardized final-answer formats for benchmarks:
16,384 output tokens for most queries, boxed final answers for math, and a
structured answer field for multiple-choice tasks.

## Raw Artifact Findings

Raw run root:
`vm4vpn:/tmp/task071_vpn_eval_qwen30b_original_full`

| Task | Current task071 setting | Evidence | Diagnosis |
|---|---|---|---|
| MMLU-Pro | `lm-eval` `local-completions`, `num_fewshot=5`, `max_gen_toks=32`, prompt asks to think step by step and finish with `the answer is (X)` | `12030/12032` samples had `filtered_resps=["[invalid]"]`; all `12032/12032` completions finished by length | Severe metric/harness mismatch. The model starts reasoning but cannot reach the final letter in 32 tokens. |
| AIME25 | `aime_2025_nemo`, chat endpoint, `max_tokens=2048` | `finish_reason.length=234/300`, avg completion `1950.45` tokens | Many original-model generations hit the cap before a scorer-parseable boxed answer. |
| HMMT | `nemo_skills.ns_hmmt_feb2025`, chat endpoint, `tokens_to_generate=2048` | `finish_reason.length=28/30`, `no_answer=93.33333333333333` | Most generations hit the cap or fail final-answer extraction. First raw sample reaches the value `103` in text but continues and is recorded with `predicted_answer=null`. |

## Probe

Probe artifacts:

- `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/original_probe_inputs.json`
- `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/original_probe_results.json`

Debug endpoint:
`qwen3-30b-a3b-instruct-2507-original-debug` served on NemTron with SGLang,
TP=4, context length 8192.

MMLU-Pro first biology sample target is `B`.

| Probe | Result |
|---|---|
| Same lm-eval completions prompt, `max_tokens=32` | `finish_reason=length`, no extracted letter |
| Same lm-eval completions prompt, `max_tokens=512` | `finish_reason=stop`, output contains `The answer is (B)`, extracted letter `B` |
| Chat answer-only prompt, `max_tokens=16` | output `B` |

AIME first problem with the same chat prompt and `max_tokens=4096` still ended
with `finish_reason=length`, which confirms that the 2048-token full run is
not a fair official-comparable math setting for this model.

## Conclusion

The original Qwen results in the task071 manifests are not official-comparable
benchmark results. They are regression scores under a currently misaligned
launcher configuration. The biggest confirmed issue is MMLU-Pro: the metric is
mostly measuring whether the model can emit a final answer within 32 tokens
after a chain-of-thought prompt, not whether it can solve MMLU-Pro.

## Corrective Plan

1. Keep the existing manifests as regression-run records but mark their
   official comparability status explicitly.
2. Build a corrected baseline eval path for Qwen-style instruct models:
   chat-template endpoint, standardized answer-only or JSON answer format for
   multiple-choice tasks, and substantially larger generation caps for math.
3. Rerun a small calibration slice first, then rerun the full selected basket
   for original, iter0009119, and final only after the parser and truncation
   rates are acceptable.
