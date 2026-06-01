# task241_qwen_aime_v10_sidecar_data_s1 - Task Knowledge

<!-- METADATA:SESSION=2 -->

## Knowledge Entries

1. V10 sidecar work must not train on AIME 2025 prompts or labels; AIME25 is held-out eval/decontam material only.
2. Existing V9 recurrence sidecar coverage was too sparse for `aime_06`: task076 found only one `chairs`, one `binary string`, four explicit DP/dynamic-programming rows, and no combined no-111-like DP rows.
3. Qwen SFT packing must preserve tokenizer-native chat-template rendering with `enable_thinking=false` and `truncate_history_thinking=false`.
4. Acceptance branch base is current `origin/main` at
   `f5a844765c5ac1a756b7f7e94d27ee466fe25a9b`; task docs were imported from
   lead branch head `116a2f3791d95a71dc5d4bbbf51bd707be7f8cc3`.
5. V10 is implemented as a new strategy name,
   `hard_math_runlength_dp_v10`, not as a planner/training change.
6. V10 hard rows require V8 clean-final rows plus counting-prompt,
   binary/chair/sequence-object, run-length constraint, and either
   DP/recurrence or case-split combinatorics solution signals.
7. V10 is part of `STRATEGIES_REQUIRING_MATH_DECONTAMINATION`; the task
   tests assert contaminated AIME25-like prompts are removed before base train
   and hard sidecar writing.
