# V9 Tuning Hypothesis - Session 1

## Failure Target

Task075 showed V8 misses the AIME25 gate by one repeat (`59/300`, threshold `60/300`). The row audit says this is not a length-cap or parser failure:

- V7 AIME25 exact-correct: `63/300`
- V8 AIME25 exact-correct: `59/300`
- V7 length-capped rows: `27`
- V8 length-capped rows: `14`
- V7 parsed rows: `273`
- V8 parsed rows: `286`

The net loss is concentrated in `aime_06`, where V7 is `10/10` and V8 is `0/10`.

## `aime_06` Correct Reasoning Shape

Problem summary: choose 8 occupied chairs from 16 in a row such that no occupied chair has two occupied neighbors. In binary-string terms, count length-16 strings with exactly 8 ones and no substring `111`.

Correct recurrence:

- Let `dp[i][j][r]` be the number of prefixes of length `i` with `j` occupied chairs, where `r` is the trailing run length of occupied chairs (`0`, `1`, or `2`).
- Transition by placing an empty chair:
  - `dp[i+1][j][0] += dp[i][j][r]`
- Transition by placing an occupied chair only if it does not create a run of 3:
  - if `r < 2`, then `dp[i+1][j+1][r+1] += dp[i][j][r]`
- Answer:
  - `sum_r dp[16][8][r] = 2907`
  - `2907 mod 1000 = 907`

V8's representative wrong answer `870` came from concluding `N=12870`, not from malformed output. This is an enumeration/recurrence error.

## Working Hypothesis

V8's `hard_math_clean_final_v8` filter tightened to clean final boxed answers and removed broad diversity. That improved finish behavior, but it likely over-emphasized polished long solutions and under-preserved compact dynamic-programming/counting recurrences. The V9 intervention should recover recurrence/counting patterns without reintroducing broad noisy rows.

V9 should not target:

- More generation budget: V8 length-capped fewer rows than V7.
- Parser repair: V8 parsed more rows than V7.
- Contains-expected scoring: `aime_24` demonstrates expected answers can appear in intermediate text while the final boxed answer is wrong.

V9 should target:

- DP state definitions over prefixes/positions.
- Binary string or subset encoding.
- Run-length constrained counting.
- Recurrence transitions with small state variables.
- Modular final answer extraction after exact count.

## Proposed V9 Data Shape

Add a focused recurrence-counting sidecar on top of V8:

- Keep V8 clean-final requirement for final answer quality.
- Add a new high-priority recurrence/counting slice selected from decontaminated `math_competition_numeric` rows.
- Selection heuristic:
  - Prompt or solution contains recurrence/counting terms: `sequence`, `subsets`, `arranged in a row`, `no adjacent`, `chairs`, `binary string`, `dynamic programming`, `recurrence`, `states`, `modulo`, `remainder`.
  - Solution includes an explicit count recurrence or structured enumeration.
  - Final answer is scalar numeric and clean boxed.
  - Exclude rows blocked by AIME25/HMMT/MATH heldout decontamination.
- Initial target size: small and high precision, not broad replay. Prefer a few hundred to a few thousand recurrence/counting rows if available after decontamination.
- Initial weighting: duplicate as a sidecar with higher effective weight than V8 hard clean rows, but keep the base agentic blend unchanged.

## Proposed Implementation Path

1. Add a V9 strategy name such as `hard_math_recurrence_v9`.
2. Reuse V8's `is_hard_math_clean_final_row` as a prerequisite.
3. Add `is_hard_math_recurrence_row` with recurrence/counting keyword checks over prompt and solution.
4. Add a V9 bucket/weight flag in `prepare_m1_agentic_sft.py` and planner plumbing in `plan_qwen_scaleup_run.py`.
5. Generate a local V9 data-prep plan using the existing V8 sidecar source root.
6. Before full training, inspect bucket counts and sample rows for decontamination and recurrence quality.
7. Train a short V9 continuation or full candidate from the V8 lineage if the bucket is sufficient.
8. Run targeted corrected AIME smoke that includes `aime_06`; require at least one of:
   - `aime_06` improves materially versus V8 (`0/10`), ideally `>=5/10`.
   - AIME25 smoke recovers the missing repeat without large regressions on known V8 gains (`aime_14`).
9. If targeted smoke passes, run the full corrected MMLU-Pro/AIME25/HMMT gate protocol.

## Immediate Acceptance Mapping

This hypothesis satisfies the first task076 acceptance criterion: the V7/V8 audit has been converted into a concrete V9 tuning hypothesis, including why `aime_06` failed and what data/weighting should address it.
