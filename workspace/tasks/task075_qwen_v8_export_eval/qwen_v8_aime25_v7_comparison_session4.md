# Qwen V8 AIME25 V7 Comparison - Session 4

## Scope

This audit compares corrected full AIME25 row-level outputs for:

- V7: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/session91_corrected_eval/outputs/math_corrected_full/results.jsonl`
- V8: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/session75_v8_corrected_eval/outputs/math_corrected_full/results.jsonl`

Both runs used the corrected original-prompt AIME25 protocol with `max_tokens=8192`.

## Aggregate Comparison

| Metric | V7 iter0782 | V8 iter0779 | Delta |
|---|---:|---:|---:|
| Exact-correct rows | 63/300 | 59/300 | -4 |
| Accuracy | 0.21 | 0.19666666666666666 | -0.013333333333333336 |
| Parsed rows | 273/300 | 286/300 | +13 |
| Length-capped rows | 27/300 | 14/300 | -13 |
| Contains-expected rows | 83/300 | 73/300 | -10 |

Correctness overlap:

| Bucket | Rows |
|---|---:|
| Both wrong | 229 |
| Both correct | 51 |
| V7 correct, V8 wrong | 12 |
| V7 wrong, V8 correct | 8 |

The V8 gate miss is not primarily truncation: V8 has fewer length-capped rows and more parsed rows than V7. The exact-correct drop comes from answer quality shifts.

## Problem-Level Deltas

Only three AIME problem ids changed net exact-correct count:

| Problem id | Expected | V7 correct | V8 correct | Delta | Notes |
|---|---:|---:|---:|---:|---|
| `aime_06` | 907 | 10/10 | 0/10 | -10 | Real regression. V7 consistently predicted `907`; V8 predicted wrong answers `870`, `456`, or `128`, and never contained the expected answer. |
| `aime_13` | 588 | 2/10 | 3/10 | +1 | Small V8 gain; V8 also eliminated one V7 length cap. |
| `aime_14` | 16 | 0/10 | 5/10 | +5 | V8 partially fixes this combinatorics problem; V7 mostly predicted `772`. |

There is also sample-level churn with zero net problem-level delta. For `aime_23`, V7 and V8 each got `1/10`, but on different repeats.

## Length-Cap Audit

| Category | Rows |
|---|---:|
| V7 length-capped | 27 |
| V8 length-capped | 14 |
| Length-capped in both | 12 |
| V7-only length-capped | 15 |
| V8-only length-capped | 2 |

V8 length-capped sample ids:

`aime_09_r01`, `aime_09_r02`, `aime_09_r03`, `aime_09_r04`, `aime_09_r05`, `aime_09_r06`, `aime_09_r07`, `aime_09_r09`, `aime_09_r10`, `aime_17_r08`, `aime_25_r01`, `aime_25_r04`, `aime_25_r05`, `aime_25_r07`.

The length-cap profile improved versus V7, but not enough to offset the `aime_06` content regression.

## Contains-Expected Audit

V8 has 14 rows where `contains_expected=True` but `correct=False`:

- `aime_13_r02`, `aime_13_r03`, `aime_13_r04`, `aime_13_r07`
- `aime_24_r01` through `aime_24_r10`

This does not justify overriding exact scoring. `aime_24` has expected answer `60`, and response text can include `60` from the problem's angle statements or intermediate reasoning while still boxing an incorrect final answer. The corrected gate should remain exact-normalized final boxed answer.

## Representative Regression

`aime_06` asks for chair subsets where no selected chair has selected neighbors on both sides. V7 returned the expected remainder `907` for all 10 repeats. V8 returned:

- `870` for 6 repeats
- `456` for 3 repeats
- `128` for 1 repeat

The representative V8 tail for `aime_06_r01` concludes:

> the number of valid subsets is \(N = 12870\), so \(12870 \mod 1000 = 870\), boxed `870`.

That is a genuine wrong final answer, not a parsing failure.

## Conclusion

The AIME25 failure should be treated as a real V8 regression against the V7 gate, not as noise from the scorer or the 8192-token cap. V8 is one correct repeat below the threshold (`59/300`; gate requires `60/300`), but the miss is backed by a concentrated `aime_06` problem-level loss of 10 repeats.

Recommended next action: do not count V8 as gate-passing from this run. Either close task075 with the recorded gate failure, or use this audit to drive a V9/tuning pass focused on recovering `aime_06`-style counting/recurrence behavior while preserving the V8 gains on `aime_14` and the improved length-cap profile.
