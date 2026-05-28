# V9 AIME06 Trace Audit - Session 12

## Path Check

The user re-stated that the model checkpoint path should use `/mnt/cephfs/data/stable/models/Qwen`.

Current active Qwen HF metadata/tokenizer path is already:

`/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`

This is the path used for:

- Session 7 packing/tokenizer config.
- Session 10 corrected V9 rerun recipe construction.
- Session 11 corrected HF export source metadata/tokenizer.

The SFT continuation checkpoint remains the V8 Megatron checkpoint root:

`/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8/checkpoints`

That path should not be replaced by the Qwen HF model directory; it is the trained V8 starting point, while the cephfs Qwen path supplies HF config/tokenizer metadata.

## Correct Target

The `aime_06` problem asks for binary strings of length `16` with exactly `8` ones and no `111` substring.

A compact count by runs:

- Let `b` be the number of runs of two ones.
- Then the number of one-runs is `r = 8 - b`, and `b` ranges from `0` to `4`.
- Choose which of the `r` runs are length two: `C(r, b)`.
- Place the `r` runs among `8` zeroes with at least one zero between neighboring runs: `C(9, r)`.

Total:

`C(8,0)C(9,8) + C(7,1)C(9,7) + C(6,2)C(9,6) + C(5,3)C(9,5) + C(4,4)C(9,4) = 2907`

The required answer is `907`.

## Corrected V9 Trace Findings

Input artifacts:

- Summary: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9_ckptroot_fix_s10/targeted_smoke/aime06/summary.json`
- Rows: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9_ckptroot_fix_s10/targeted_smoke/aime06/results.jsonl`

Observed output distribution:

| Metric | Value |
|---|---:|
| Rows | `10` |
| Finish `stop` | `10` |
| Parsed | `10` |
| Correct | `0` |
| Prediction `640` | `5` |
| Prediction `830` | `5` |

The `640` traces identify the no-three-consecutive constraint but lose the recurrence. They mention dynamic programming, then fall back to an unsupported final claim.

The `830` traces use the wrong generating function/coefficient model, specifically treating the answer as a coefficient of `(1+x+x^2)^16`. That polynomial does not count length-16 binary strings with exactly eight selected chairs and no three consecutive occupied chairs.

## Sidecar Coverage Audit

The V9 recurrence sidecar has `221` rows:

`/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/m1_agentic_sft/agentic_sft_v0_math_hard_verified_full_solution_train.jsonl`

Exact signal counts over prompt plus solution:

| Signal | Rows |
|---|---:|
| `chairs?` | `1` |
| `binary string(s)` | `1` |
| `no three consecutive` / `three consecutive` | `19` |
| `consecutive ones` | `1` |
| explicit `dynamic programming` / `dp` | `4` |
| `recurrence` | `19` |
| no-111-like binary/chair signal near DP/recurrence signal | `0` |

The filter test includes an `aime_06`-style synthetic row, but the real mined sidecar does not contain enough matching examples. The V9 sidecar mostly teaches broad combinatorics and loose consecutive/adjacent patterns, not the specific run-length binary-string recurrence needed here.

## Decision

Do not spend the full corrected MMLU-Pro/AIME25/HMMT gate on corrected V9. The checkpoint-root fix repaired the random-init pathology and endpoint behavior, but the targeted recovery objective still fails.

Recommended next implementation step:

- Add a focused V10-style recurrence patch rather than another full-gate eval of V9.
- Keep Qwen HF metadata/tokenizer under `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Start from the corrected V8 checkpoint root or corrected V9 checkpoint only after deciding whether the patch should preserve V8 more strongly.
- Build a small decontaminated sidecar of synthetic or mined run-length DP problems that explicitly uses state definitions such as `dp[i][j][r]`, gap/run enumeration, and final modulo extraction.
