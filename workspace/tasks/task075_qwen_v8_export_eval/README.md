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

- [ ] HF export exists and passes basic config/tokenizer/shard validation.
- [ ] SGLang endpoint smoke passes with the exported V8 model.
- [ ] Corrected full MMLU-Pro metrics are recorded.
- [ ] Corrected full AIME25 metrics are recorded with `max_tokens=8192`.
- [ ] Corrected full HMMT metrics are recorded with `max_tokens=8192`.
- [ ] Gate verdict is recorded against V7 thresholds: MMLU-Pro `>=0.55`, AIME25 `>=0.20`, HMMT exact percent `>=10.0`.
