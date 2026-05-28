# task075_qwen_v8_export_eval - Qwen V8 Export And Corrected Eval

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_code_reading -->

## Background

Task071 produced the Qwen3-30B-A3B V8 hard-math clean-final SFT checkpoint at `iter_0000779`. The next step is to export that Megatron checkpoint to HF, serve it with SGLang using a 16k context, and run the corrected full eval protocol used for the V7 gates.

## Goals

- Export `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8/checkpoints/iter_0000779` to a HF checkpoint on NemTron.
- Serve the export with SGLang using `tp=4`, `dp=2`, and `context_length=16384`.
- Run corrected full MMLU-Pro, AIME25, and HMMT eval using the V7 gate protocol.
- Compare results against the V7 gate thresholds and record artifacts.

## Acceptance Criteria

- [x] HF export exists and passes basic config/tokenizer/shard validation.
- [x] SGLang endpoint smoke passes with the exported V8 model.
- [x] Corrected full MMLU-Pro metrics are recorded.
- [x] Corrected full AIME25 metrics are recorded with `max_tokens=8192`.
- [x] Corrected full HMMT metrics are recorded with `max_tokens=8192`.
- [x] Gate verdict is recorded against V7 thresholds: MMLU-Pro `>=0.55`, AIME25 `>=0.20`, HMMT exact percent `>=10.0`.

## Session 3 Result

- Report: `workspace/tasks/task075_qwen_v8_export_eval/qwen_v8_iter0779_corrected_eval_session3.md`.
- MMLU-Pro: `0.5606715425531915` on 12032 rows, pass against `>=0.55`.
- AIME25: `0.19666666666666666` (`59/300`) with original prompts and `max_tokens=8192`, fail against `>=0.20`.
- HMMT: `13.333333333333334%` (`4/30`) with original prompts and `max_tokens=8192`, pass against `>=10.0`.
- Overall V7-gate verdict: fail due AIME25 missing the threshold by 1 correct repeat.

## Session 4 AIME25 Audit

- Report: `workspace/tasks/task075_qwen_v8_export_eval/qwen_v8_aime25_v7_comparison_session4.md`.
- V8 has fewer AIME25 length-capped rows than V7 (`14` versus `27`) and more parsed rows (`286` versus `273`), so the AIME gate miss is not primarily a truncation artifact.
- Exact-correct overlap: `51` both correct, `229` both wrong, `12` V7-only correct, `8` V8-only correct.
- Main regression: `aime_06` drops from V7 `10/10` correct to V8 `0/10` correct; this accounts for the gate miss despite V8 gains on `aime_13` and `aime_14`.
- Audit conclusion: treat the AIME25 failure as a real V8 gate failure, not scorer noise.
