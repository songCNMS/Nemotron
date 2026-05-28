# V9 Data Prep Session 7

Date: 2026-05-28
Executor: intern_nemontron_code_reading

## Summary

Session 7 completed local V9 data preparation after fixing two blockers:

- The original M1 decontamination implementation was too slow for uncapped V9 because it compared roughly `859k` math rows against `1479` heldout prompts with a nested scan.
- The generated packing script used `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507`, which is not accessible in this workspace. The user requested switching the checkpoint/model path to `/mnt/cephfs/data/stable/models/Qwen`; the usable model/tokenizer subdirectory is `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.

## Code Changes

- `prepare_m1_agentic_sft.py`: optimized `decontaminate_math_rows` by building an eval n-gram inverted index, then comparing each math prompt only against eval prompts sharing at least one n-gram.
- `plan_qwen_scaleup_run.py`: added `--qwen-tokenizer-model` so local packing/contract validation can use an accessible tokenizer path while preserving the training model path in generated scripts.
- `test_m1_agentic_qwen_scaleup_plan.py`: added coverage for separate Qwen model/tokenizer paths.

## Data Prep Results

- M0 output: `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/m0_agentic`
- M0 conversion errors: `2389`, all from known invalid Hermes rows; every requested dataset still produced valid rows.
- M0 total rows from manifest datasets: `983397` train, `11354` validation.
- M1 output: `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/m1_agentic_sft`
- M1 rows: `983087` train, `11354` val-shadow.
- Decontamination corpus: `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/aime25_hmmt_math_heldout_decontam_corpus.jsonl`
- Decontamination corpus size: `1479` prompts (`30` AIME25, `30` HMMT, `1419` MATH-style heldout).
- Base math train decontamination: scanned `859494`, dropped `310`, blocker findings `310`.
- Sidecar math train decontamination: scanned `859494`, dropped `310`, blocker findings `310`.
- V9 hard recurrence sidecar: `221` hard verified full-solution training rows.
- Heldout eval rows: `1419`, not included in the training blend.

## Qwen Path Fix

Verified tokenizer/config files at:

`/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`

The regenerated scale-up manifest now uses this path for both:

- `training.qwen_hf_model`
- `packing.tokenizer_model`

No generated V9 plan script references `/mnt/3fs`.

## Packing And Training Plan

- Packed data path: `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/packed_qwen/splits`
- Tokenizer URI: `file:///mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- Pack size: `8192`
- Shards: `32`
- Total sequences: `983135`
- Total tokens: `667289202`
- Qwen packed SFT chat contract: passed.

Training plan:

- Manifest: `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/training_plan/task076_qwen30b_a3b_hard_math_recurrence_v9/training_manifest.json`
- Run script: `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/training_plan/task076_qwen30b_a3b_hard_math_recurrence_v9/run_m1_agentic_sft.sh`
- Remote train launcher: `/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/run_nemtron_train.sh`
- Pretrained checkpoint: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8/checkpoints/iter_0000779`
- Train entrypoint: `src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py`
- Train rows: `30699`
- Valid rows: `2571`
- Train iters: `192`
- Epochs: `0.05`
- Global batch size: `8`
- Micro batch size: `1`
- Sequence length: `8192`
- LR: `8e-8`
- Min LR: `3e-8`
- Warmup iters: `20`

## Eval Dry Run

Ran:

`/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/run_eval_basket_dry_run.sh`

Result: `m1_basket` compiled successfully. The compiled task list includes `adlr_aime25`, and eval chat template kwargs keep `enable_thinking=false` and `truncate_history_thinking=false`.

## Next Step

Launch V9 training on NemTron with:

`/work-agents/intern_nemontron_code_reading/outputs/task076_qwen30b_a3b_hard_math_recurrence_v9/run_nemtron_train.sh`
