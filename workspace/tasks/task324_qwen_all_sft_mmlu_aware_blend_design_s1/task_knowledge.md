# task324_qwen_all_sft_mmlu_aware_blend_design_s1 - Task Knowledge

<!-- METADATA:SESSION=96 -->

## Knowledge Entries

1. Task314 found the MMLU-Pro regression is real answer-choice drift.
2. Task320 requires preserving math gains while preventing non-math aggregate
   regression.
3. Task319 raw sources are feasible candidates but not packing-ready.
4. This task does not authorize materialization, packing, training, or eval.
5. Task314's accepted signal is math `+13`, non-math aggregate `-15`, and
   `86/92` loss rows outside math; a future blend must not allow math gains to
   mask non-math regression.
6. Task319's largest directly relevant missing configured category is
   `science` with weight `12.8`, mapping to physical sciences and bio-health.
7. Task299/V11 seed is valid only as a continuity seed for this design; it is
   too narrow and math/agentic-heavy to prove MMLU-aware non-math retention by
   itself.
8. Task322 or a successor must provide exact local rows, row manifests,
   checksums, decontam, split exposure, and Qwen supervised-token counts before
   any raw source can enter a later packed contract.
