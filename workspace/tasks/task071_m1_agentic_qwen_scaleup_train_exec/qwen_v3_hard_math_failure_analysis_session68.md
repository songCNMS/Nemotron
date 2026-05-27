# Qwen v3 Hard-Math Failure Analysis - Session 68

## Inputs

- V3 results: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/qwen_v3_iter2200_session67/math_corrected_full/results.jsonl`
- Iter3000 comparison: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/qwen_chat_iter3000_session59/math_corrected_full/results.jsonl`
- M1 data artifact: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_math_reasoning_replay_v3/m1_agentic_sft`

## Metric Summary

| Task | Rows | Accuracy | Parsed rate | Contains expected | Avg completion tokens |
|---|---:|---:|---:|---:|---:|
| aime25 | 300 | 0.086667 | 0.940000 | 41 | 1054.6 |
| hmmt | 30 | 0.000000 | 1.000000 | 1 | 719.7 |

## Failure Clusters

| Task | Cluster | Problems | Rows |
|---|---|---:|---:|
| aime25 | deterministic_wrong_final | 17 | 170 |
| aime25 | mixed_or_variable_wrong | 6 | 60 |
| aime25 | length_or_unparsed | 3 | 30 |
| aime25 | all_repeats_correct | 2 | 20 |
| aime25 | expected_mentioned_final_wrong | 2 | 20 |
| hmmt | deterministic_wrong_final | 29 | 29 |
| hmmt | expected_mentioned_final_wrong | 1 | 1 |

Key readout:

- AIME25 has high parseability but repeated wrong reasoning: most problem groups have a stable wrong boxed answer across repeats.
- AIME25 length failures are concentrated in a small number of problem groups rather than spread across the benchmark.
- HMMT is the cleanest signal: every row is parsed and stops normally, yet every exact-normalized answer is wrong.
- The error shape rules out a parser-only fix. The next run needs harder verified solution replay, not more boxed-answer-only data.

## Representative AIME Problem Groups

| Problem | Topic | Cluster | Correct/Rows | Parsed/Rows | Length | Modal prediction | Iter3000 correct |
|---|---|---|---:|---:|---:|---|---:|
| aime_01 | geometry | deterministic_wrong_final | 0/10 | 10/10 | 0 | `73` | 0 |
| aime_02 | number_theory | deterministic_wrong_final | 0/10 | 10/10 | 0 | `32812` | 0 |
| aime_03 | geometry | deterministic_wrong_final | 0/10 | 10/10 | 0 | `27` | 0 |
| aime_04 | number_theory | mixed_or_variable_wrong | 0/10 | 10/10 | 0 | `1000` | 0 |
| aime_05 | geometry | mixed_or_variable_wrong | 0/10 | 10/10 | 0 | `159` | 0 |
| aime_06 | number_theory | deterministic_wrong_final | 0/10 | 10/10 | 0 | `513` | 0 |
| aime_07 | geometry | deterministic_wrong_final | 0/10 | 10/10 | 0 | `Thefinalansweris\binom{24}{12}\times\binom{12}{6}\times\binom...` | 0 |
| aime_08 | geometry | deterministic_wrong_final | 0/10 | 10/10 | 0 | `100` | 0 |
| aime_09 | number_theory | length_or_unparsed | 0/10 | 1/10 | 9 | `36` | 0 |
| aime_11 | geometry | deterministic_wrong_final | 0/10 | 10/10 | 0 | `147` | 0 |
| aime_12 | algebra | deterministic_wrong_final | 0/10 | 10/10 | 0 | `188` | 0 |
| aime_13 | geometry | mixed_or_variable_wrong | 0/10 | 10/10 | 0 | `540` | 0 |

## Training Data Diagnosis

- Existing V3 verified full-solution sidecar rows read: `544967`.
- Estimated AIME/HMMT-style hard verified candidates: `196168` (35.9963%).
- Existing V3 format-repair sampled rows read: `16099`.
- Heuristic unparseable final segment count in sampled format-repair rows: `0`.

Hard candidate topics:

| Topic | Rows |
|---|---:|
| algebra | 56705 |
| combinatorics_probability | 29255 |
| geometry | 61663 |
| number_theory | 48545 |

## Next Recipe

Run name: `task071_qwen30b_a3b_hard_math_recovery_v4`

| Component | Setting |
|---|---|
| Start checkpoint | `original_qwen3_30b_a3b_instruct_2507` |
| Hard verified sidecar | sample fraction `1.0`, blend weight `1.0` after prepack sampling |
| Broad verified sidecar | sample fraction `0.25`, blend weight `1.0` after prepack sampling |
| Format repair sidecar | disabled |
| Final-answer auxiliary sidecar | disabled |
| LR | `3e-07` with min `8e-08` |
| Epochs | `0.2` |
| Eval/save interval | `400` |

Promotion criteria:

- MMLU-Pro full accuracy at least `0.55`.
- AIME25 full accuracy at least `0.2`.
- HMMT full exact percent at least `10.0`.

Execution note: use `hard_math_recovery_v4` as a pre-pack sampling strategy before packing. Do not train on AIME25/HMMT eval prompts or answers; use the failure clusters only as diagnostics and gate definitions.
