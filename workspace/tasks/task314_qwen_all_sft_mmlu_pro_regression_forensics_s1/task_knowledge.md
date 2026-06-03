# task314_qwen_all_sft_mmlu_pro_regression_forensics_s1 - Task Knowledge

<!-- METADATA:SESSION=78 -->

## Knowledge Entries

1. Task311 MMLU-Pro base was `6758/12032`; task311 FT was `6756/12032`.
2. A `-2` MMLU-Pro delta prevents a uniform non-regression claim even though
   AIME2025 and HMMT improved.
3. Row-level transitions are required before deciding whether the issue is
   model behavior, parser/prompt artifact, or an evaluator/protocol mismatch.
4. New evaluation or endpoint launch is not authorized by this task.
5. Task314/#380 finding accepted by lead: MMLU-Pro row churn has 92 losses and
   90 gains for net `-2`, with no row-alignment/parser/protocol artifact found.
6. Lead gate comment is #380 issuecomment `4615943272`; no action beyond docs
   forensics is authorized.
