# task076_qwen_v9_aime_recurrence_tuning - Task knowledge

<!-- METADATA:SESSION=2 -->

> **Writing rule**: one line each, format `N. category: content`
>
> Categories: supervisor request, technical fact, file change, research conclusion

---

## Knowledge entries

1. supervisor request: Start a V9 tuning task focused on recovering `aime_06`-style counting/recurrence behavior after task075 showed V8 failed AIME25 by one correct repeat.
2. technical fact: Task075 V8 corrected eval scored MMLU-Pro `0.5606715425531915`, AIME25 `0.19666666666666666`, and HMMT exact percent `13.333333333333334`.
3. technical fact: Task075 AIME audit found V8 had fewer AIME25 length caps than V7 (`14` vs `27`) but regressed on `aime_06` from V7 `10/10` correct to V8 `0/10` correct.
4. research conclusion: The V9 tuning hypothesis should target recurrence/counting answer quality rather than parser repair or larger generation budget.
5. technical fact: `aime_06` is equivalent to counting length-16 binary strings with exactly 8 ones and no substring `111`; the DP count is `2907`, so the required remainder is `907`.
6. research conclusion: V9 should preserve V8 clean-final filtering and add a focused recurrence/counting sidecar, rather than increasing `max_tokens` or changing exact-final-answer scoring.
7. file change: Added `hard_math_recurrence_v9` data-prep and Qwen scale-up planner support with V9-specific sidecar weights.
8. technical fact: V9 requires V8 clean-final hard-math rows plus recurrence/counting/run-length keyword signals.
9. technical fact: The existing V8 hard sidecar has `220/4546` rows passing the V9 recurrence filter.
10. file change: Generated local V9 scale-up plan at `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/scaleup_manifest.json`.
11. technical fact: The V9 decontamination corpus has `1479` prompts: `30` AIME25, `30` HMMT, and `1419` MATH-style heldout-eval prompts.
12. research conclusion: The V9 continuation plan should start from V8 `iter_0000779` with a short `0.05` epoch, low-LR recurrence sidecar run before any corrected full eval.

---
