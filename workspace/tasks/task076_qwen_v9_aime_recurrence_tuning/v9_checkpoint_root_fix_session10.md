# V9 Checkpoint Root Fix - Session 10

## Root Cause

The Session 8/9 V9 run did not load the V8 checkpoint weights. Its launch script exported:

`SUPER3_M1_PRETRAINED_CHECKPOINT=/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8/checkpoints/iter_0000779`

Megatron-Bridge expects the checkpoint root directory, not the `iter_XXXXXXX` child directory, because it resolves the active iteration from `latest_checkpointed_iteration.txt`. With `exit_on_missing_checkpoint=false`, the invalid child path did not crash; it silently trained from random initialization.

Evidence:

- Invalid V9 log has no `successfully loaded checkpoint` line.
- Invalid V9 iter 10 train lm loss was `12.25112`; final validation loss/PPL was `8.960094/7786.093`.
- V8/V7 continuation logs using checkpoint roots include `successfully loaded checkpoint ... at iteration 0` and train at normal SFT loss scale.

## Code Fix

Updated both Qwen scale-up planning layers to normalize an input checkpoint path ending in `iter_XXXXXXX` to its parent checkpoint root before writing manifests or launch scripts:

- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_qwen_scaleup_run.py`
- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_m1_agentic_sft_training.py`

Added regression coverage:

- `tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py::test_scaleup_planner_normalizes_iter_checkpoint_to_root`
- `tests/recipes/super3/test_m1_agentic_sft.py::test_build_plan_normalizes_iter_checkpoint_to_root`

Verification:

- `python -m py_compile src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_qwen_scaleup_run.py src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_m1_agentic_sft_training.py`
- `PYTHONPATH=$PWD/src pytest -q tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py -k 'normalizes_iter_checkpoint or auto_selects_30b_a3b_entrypoint' tests/recipes/super3/test_m1_agentic_sft.py -k 'normalizes_iter_checkpoint'`
- `PYTHONPATH=$PWD/src pytest -q tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py -k '30b_entrypoint or normalizes_iter_checkpoint or wires_30b'`
- `PYTHONPATH=$PWD/src ruff check src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_qwen_scaleup_run.py src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_m1_agentic_sft_training.py tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py tests/recipes/super3/test_m1_agentic_sft.py`

## Corrected Rerun

- Run root: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9_ckptroot_fix_s10`
- Training log: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9_ckptroot_fix_s10/logs/train.log`
- Manifest: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9_ckptroot_fix_s10/session10_corrected_rerun_manifest.json`
- Source packed SFT data: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9/packed_qwen/splits`
- Source Qwen metadata/tokenizer: `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- Corrected V8 checkpoint root: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8/checkpoints`
- Final corrected checkpoint: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9_ckptroot_fix_s10/checkpoints/iter_0000192`

Corrected training confirmed checkpoint load:

`successfully loaded checkpoint from /work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_clean_final_v8/checkpoints [ t 1/4, p 1/2 ] at iteration 0`

Metrics:

| Iteration | Train lm loss | Validation loss | Validation PPL |
|---:|---:|---:|---:|
| 10 | `0.4368270` | | |
| 100 | `0.4449203` | `0.4531137` | `1.573203` |
| 190 | `0.4447130` | | |
| 192 | | `0.4252748` | `1.530011` |

- Checkpoint marker: `192`
- Final checkpoint size: about `399G`
- Skipped/nan remained `0/0` in observed train log.
- The corrected run stopped cleanly and GPUs returned to idle.

## Next Step

Export `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task076_qwen30b_a3b_hard_math_recurrence_v9_ckptroot_fix_s10/checkpoints/iter_0000192` to HF, then rerun the targeted corrected `aime_06` smoke before deciding whether to spend the full corrected gate.
