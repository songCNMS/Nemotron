# Qwen V7 Iter 0782 Math Error Analysis - Session 92

## Scope

- Model: `task071-qwen3-30b-a3b-agentic-sft-hard-math-long-reasoning-v7-full-sidecar-iter0000782-hf`
- Base corrected eval artifacts: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/qwen_v7_iter0782_session91/remote_corrected_eval_outputs`
- Session 92 probe artifacts: `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/qwen_v7_iter0782_session92_error_analysis/remote_error_analysis`
- Protocol baseline: corrected math original prompts, `temperature=0.0`, `top_p=1e-5`, SGLang `context_length=16384`

## AIME25 Failure Clusters

Session 91 full score was `63/300 = 0.21`, parsed rate `0.91`.

| Cluster | Unique Problems | Row Count | Correct Rows | Notes |
|---|---:|---:|---:|---|
| Fully solved | 6 | 60 | 60 | Problems `06`, `10`, `15`, `26`, `27`, `29` were `10/10` correct. |
| Partially solved | 2 | 20 | 3 | Problem `13` was `2/10`; problem `23` was `1/10`. |
| Parsed but consistently wrong | 17 | 170 | 0 | Problems `01`, `02`, `03`, `04`, `05`, `07`, `08`, `11`, `12`, `14`, `16`, `18`, `19`, `20`, `21`, `24`, `30`. |
| Fully length-truncated wrong | 1 | 10 | 0 | Problem `09` hit `length` for all repeats. |
| Partially parsed wrong | 4 | 40 | 0 | Problems `17`, `22`, `25`, `28`; problem `25` had `9/10` length rows. |

Main read:

- The V7 improvement over V5 (`20/300` to `63/300`) is real and comes from more full-problem solves, not just a parser artifact.
- The remaining AIME gap is dominated by stable wrong derivations: `17/30` unique problems are fully parsed and fully wrong.
- Raising generation length may help a small slice (`09`, `25`), but it does not address the larger stable-wrong cluster.

## HMMT Length And Variance Probe

Session 91 full HMMT score was `5/30 = 16.666666666666668%`, parsed rate `17/30`, with `15/30` rows hitting `length`.

| Run | Max Tokens | Parallelism | Correct | Parsed | Finish Summary | Avg Completion Tokens |
|---|---:|---:|---:|---:|---|---:|
| Session 91 full math | 8192 | 16 | 5/30 | 17/30 | stop 15, length 15 | 5846.0 |
| Session 92 HMMT repeat | 8192 | 8 | 4/30 | 18/30 | stop 17, length 13 | 5788.5 |
| Session 92 HMMT probe | 12288 | 8 | 4/30 | 20/30 | stop 19, length 11 | 7562.8 |

Important row-level changes:

- `hmmt_01`, `hmmt_02`, `hmmt_11`, and `hmmt_21` were correct across the repeated runs.
- `hmmt_16` was correct in the Session 91 full run but wrong in both Session 92 HMMT-only runs.
- `12288` changed several unparsed length rows into parsed wrong rows, including `hmmt_10`, `hmmt_20`, and `hmmt_24`.
- No new HMMT row became correct only because of `12288`.

Main read:

- The HMMT result is above the `10%` gate even under the lower repeat score (`4/30 = 13.333333333333334%`), but the benchmark is only 30 rows and has about one-row run variance in this setup.
- Increasing default HMMT `max_tokens` from `8192` to `12288` is not justified by this probe: it improves parsed rate but not exact score.
- HMMT still needs recipe-side work: more concise verified long solutions, better final-line discipline, and filtering of examples that wander without reaching a boxed answer.

## Recommended Actions

- Keep the corrected HMMT gate at `context_length=16384`, `max_tokens=8192` for comparability, and report V7 HMMT as a small-sample band `13.3%-16.7%`.
- For AIME, prioritize data/recipe repair over eval-policy changes: add or upweight verified full-solution rows that resemble the stable-wrong problem families and include concise final boxed answers.
- For HMMT, inspect rows that stay length-unparsed across 8192 and 12288 (`04`, `05`, `07`, `13`, `15`, `18`, `22`, `23`, `29`) and create training-side filters that prefer solutions ending cleanly before the token cap.
- Before running a broad eval basket, run a compact reproducibility check for tiny-row math benchmarks, because one HMMT row changes the exact percent by `3.3333333333333335`.
