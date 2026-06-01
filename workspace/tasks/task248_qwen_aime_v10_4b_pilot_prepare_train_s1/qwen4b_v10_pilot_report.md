# task248 Qwen3-4B V10 pilot report

<!-- METADATA:STATUS=Blocked,SESSION=3 -->

## Summary

- Branch `intern_nemotron_worker_2/task248_qwen_aime_v10_4b_pilot_prepare_train_s1` was created from current `origin/main` after PR #321 merge commit `20973e78f196d7e5d71993f60dc74a3500223f5f`.
- Qwen3-4B pilot model path exists locally: `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Local output root reserved for this task:
  `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/`.
- NemTron remote root reserved for this task:
  `/root/task248_qwen_aime_v10_4b_pilot_prepare_train_s1`.
- The task is blocked before local prep/train because task246 real corpus/input and task247 base artifacts are still not available in this worker environment.

## Dependency probes

- `git ls-remote --heads origin intern_nemotron_worker_2/task248_qwen_aime_v10_4b_pilot_prepare_train_s1` shows the task248 branch is pushed at `d0546d04ebe25ab3b9e768805c3e0a637984ca69`.
- `test -d /mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507` passed.
- Session 3 refresh: task246 remote branch is visible at `a53c913ab80e37197ccfe7525ea04e0ac80c96fe`.
- Session 3 refresh: task247 remote branch is visible at `94c21c9a8cb229f0357a049a698de898963810f1`.
- `origin/intern_nemotron_worker_1/task246_qwen_aime_v10_real_decontam_corpus_s1` contains only README/history/task_knowledge under the task directory; it does not contain `real_decontam_corpus_report.md`.
- `origin/intern_nemotron_worker_3/task247_qwen_aime2025_qwen4b_base_smoke_s1` contains only README/history/task_knowledge under the task directory; it does not contain `qwen4b_base_smoke_report.md`.
- `/work-agents/intern_nemotron_worker_1/outputs/` has no task246 output files visible to this worker.
- `/work-agents/intern_nemotron_worker_3/outputs/` has no task247 output files visible to this worker.

## Prepared command shape

Do not run this until task246 publishes a non-placeholder heldout corpus path
and real V10 sidecar/M0 input path.

```bash
PYTHONPATH=src python src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_qwen_scaleup_run.py \
  --qwen4b-v10-pilot \
  --output-dir /work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1 \
  --remote-root /root/task248_qwen_aime_v10_4b_pilot_prepare_train_s1 \
  --run-name task248_qwen4b_v10_pilot \
  --math-sidecar-m0-input-dir <task246_real_v10_m0_or_sidecar_input_dir> \
  --math-decontaminate-against-corpus <task246_real_aime25_hmmt_math_prompt_only_corpus> \
  --pack-size 8192 \
  --seq-length 8192 \
  --num-shards 8 \
  --max-train-per-dataset 100 \
  --max-val-per-dataset 25 \
  --math-sidecar-max-records-per-env 500 \
  --math-sidecar-max-val-shadow-per-env 25 \
  --epochs 0.05 \
  --eval-interval 20 \
  --save-interval 20 \
  --overwrite
```

Expected generated paths after the dependencies exist:

- Manifest: `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/scaleup_manifest.json`
- Local data-prep script: `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/run_local_data_prep.sh`
- NemTron sync script: `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/sync_to_nemtron.sh`
- NemTron train script: `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/run_nemtron_train.sh`
- Eval dry-run script: `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/run_eval_basket_dry_run.sh`
- Remote run root: `/root/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/task248_qwen_aime_v10_4b_pilot_prepare_train_s1`
- Candidate checkpoint path for task250:
  `/root/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/checkpoints`

## Gate status

- Local prep is blocked until task246 publishes a real non-placeholder corpus and V10 input.
- Training is blocked until local prep succeeds with task246 inputs.
- FT judgment is blocked until task247 publishes same-harness Qwen3-4B base artifacts and task243 comparison can enforce `ft_exact_normalized_accuracy >= base_exact_normalized_accuracy`.
- 30B/8-GPU planning and launch remain out of scope.

## Commands run

- `git fetch origin --prune`
- `git switch -c intern_nemotron_worker_2/task248_qwen_aime_v10_4b_pilot_prepare_train_s1 origin/main`
- `git checkout 5d5e3fa -- workspace/tasks/task248_qwen_aime_v10_4b_pilot_prepare_train_s1`
- `git push -u origin intern_nemotron_worker_2/task248_qwen_aime_v10_4b_pilot_prepare_train_s1`
- `test -d /mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`
- Read-only dependency probes against worker_1/worker_3 task docs and output directories.
- Session 3 refresh: `git fetch origin --prune`, `git rev-parse` on task246/task247 branches, read-only `git ls-tree`/`git show`, and read-only output directory probes.

## Commands not run

- Did not run local M0/M1 prep.
- Did not sync to NemTron.
- Did not run Qwen3-4B training.
- Did not run live eval or FT comparison.
- Did not launch or plan 30B/8-GPU scale.
- Did not delete any files under `/mnt/cephfs/data/processing/lei.song`.
