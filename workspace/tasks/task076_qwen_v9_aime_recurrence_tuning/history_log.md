# task076_qwen_v9_aime_recurrence_tuning - History log

<!-- METADATA:SESSION=6 -->

---

## Session 0 - 2026-05-28 - Init

**Executor**: intern_nemontron_code_reading

Task created from the task075 V8 gate failure. Scope is V9 tuning focused on recovering AIME25 recurrence/counting behavior, especially the `aime_06` drop from V7 `10/10` correct to V8 `0/10` correct.

---

## Session 1 - 2026-05-28 - Accept and hypothesis

**Executor**: intern_nemontron_code_reading

- Created branch `intern_nemontron_code_reading/task076_qwen_v9_aime_recurrence_tuning` from `origin/main`.
- Opened PR `https://github.com/songCNMS/Nemotron/pull/183`.
- Accepted task by setting README metadata to `InProgress` and assignee to `intern_nemontron_code_reading`.
- Wrote `v9_tuning_hypothesis_session1.md`.
- Derived the correct `aime_06` recurrence: count length-16 binary strings with exactly 8 ones and no `111`; `dp[i][j][r]` with trailing run length `r` gives count `2907`, hence answer `907`.
- Proposed V9 direction: keep V8 clean-final filtering, then add a high-precision recurrence/counting sidecar selected for DP/subset/run-length/counting structure and protected by AIME25/HMMT/MATH decontamination.

---

## Session 2 - 2026-05-28 - V9 data plan support

**Executor**: intern_nemontron_code_reading

- Added `hard_math_recurrence_v9` to M1 Agentic SFT data prep and Qwen scale-up planner.
- Implemented V9 as a V8 clean-final hard-math subset filtered for recurrence/counting/run-length signals.
- Added V9 to the V7+ math decontamination guard.
- Added tests for V9 filtering, planner script emission, and decontamination guard behavior.
- Generated local decontamination corpus `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/aime25_hmmt_math_heldout_decontam_corpus.jsonl` with `1479` prompts.
- Generated local V9 scale-up plan `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/scaleup_manifest.json`.
- Wrote `v9_data_plan_session2.md` and marked the V9 data/training-plan acceptance criterion complete.

---

## Session 6 - 2026-05-28 - Checklist sync

**Executor**: intern_nemontron_code_reading

- Confirmed task076 PR branch was pushed through commit `89a9c1e`.
- Added the missing stop-hook Session 6 bookkeeping entry.
- Kept task status as Working because V9 data prep/training launch remains the next actionable step.

---
