# task248 Qwen3-4B V10 pilot report

<!-- METADATA:STATUS=Hold,SESSION=8 -->

## Summary

- Branch `intern_nemotron_worker_2/task248_qwen_aime_v10_4b_pilot_prepare_train_s1` was created from current `origin/main` after PR #321 merge commit `20973e78f196d7e5d71993f60dc74a3500223f5f`.
- Qwen3-4B pilot model path exists locally: `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Local output root reserved for this task:
  `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/`.
- NemTron remote root reserved for this task:
  `/root/task248_qwen_aime_v10_4b_pilot_prepare_train_s1`.
- The task remains on HOLD before local prep/train/eval until task249/task250
  refresh against current `main` and lead explicitly clears.

## Dependency probes

- `git ls-remote --heads origin intern_nemotron_worker_2/task248_qwen_aime_v10_4b_pilot_prepare_train_s1` shows the task248 branch is pushed at `d0546d04ebe25ab3b9e768805c3e0a637984ca69`.
- `test -d /mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507` passed.
- Session 3 refresh: task246 remote branch is visible at `a53c913ab80e37197ccfe7525ea04e0ac80c96fe`.
- Session 3 refresh: task247 remote branch is visible at `94c21c9a8cb229f0357a049a698de898963810f1`.
- `origin/intern_nemotron_worker_1/task246_qwen_aime_v10_real_decontam_corpus_s1` contains only README/history/task_knowledge under the task directory; it does not contain `real_decontam_corpus_report.md`.
- `origin/intern_nemotron_worker_3/task247_qwen_aime2025_qwen4b_base_smoke_s1` contains only README/history/task_knowledge under the task directory; it does not contain `qwen4b_base_smoke_report.md`.
- `/work-agents/intern_nemotron_worker_1/outputs/` has no task246 output files visible to this worker.
- `/work-agents/intern_nemotron_worker_3/outputs/` has no task247 output files visible to this worker.
- Session 4 sequencing update: PR #325 is visible, `OPEN`, base `main`,
  head `afc276932897743f6b6b5b8aab4c390905cb55f1`, merge state `CLEAN`.
- Session 4 sequencing update: PR #326 is visible, `OPEN`, base `main`,
  head `8fb34bd9116e32aa8d191750f2510d2a843e0da5`, merge state `CLEAN`.
- Session 4 read-only path check: task246 corpus is present at
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl`
  with `560` JSONL rows.
- Session 4 read-only path check: task246 M0 sidecar is present at
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar`.
- Sidecar row counts are sparse by construction: train rows `8`, val rows `0`.
- Session 4 read-only baseline check: task247 corrected 30x1 base artifact is
  visible at
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z/`
  with AIME25 `11/30 = 0.36666666666666664`.
- Session 5 update: PR #326 is now `MERGED` at `2026-06-01T17:21:29Z`
  with merge commit
  `85f2bf5c11062741388ca114a84a2c26535b7df9`; baseline remains Qwen3-4B
  base AIME25 `11/30 = 0.36666666666666664`.
- Session 5 update: PR #325 is still `OPEN` at head
  `afc276932897743f6b6b5b8aab4c390905cb55f1`; lead reports
  `REQUEST_CHANGES`/HOLD on manifest checksum, so task248 remains on HOLD.
- Session 6 update: lead reports task246/#325 is approved after checksum fix
  at head `266b6a14262278b4fe27f75a3273fc156a5538ce` and may self-merge if
  still `CLEAN`.
- Session 6 read-only GitHub check: PR #325 is still `OPEN`/`CLEAN`, head
  `266b6a14262278b4fe27f75a3273fc156a5538ce`, with no `mergedAt` or merge
  commit yet.
- Session 6 read-only GitHub check: task249/#323 is `OPEN`/`CLEAN` at head
  `b8b2bbd929b20c340dce8e86f81c1252c8d0b02b`; task250/#324 is
  `OPEN`/`CLEAN` at head `cd4555199ff67eace4d40d4418eef38511786143`.
- Session 7 update: lead clarified the previous `affafe8064c8529ae0f16ffdec0d4ec61b6ed1a5`
  report crossed with the task246 fix; current #325 is approved pending actual
  merge, not request-changes.
- Session 7 read-only GitHub check: PR #325 remains `OPEN`/`CLEAN` at head
  `266b6a14262278b4fe27f75a3273fc156a5538ce`, with no `mergedAt` or merge
  commit yet.
- Session 7 read-only GitHub list check: task249/#323 and task250/#324 remain
  `OPEN`/`CLEAN`.
- Session 8 update: PR #325 is now `MERGED` at `2026-06-01T17:43:24Z` with
  merge commit `2775dff05948acce3a35a2d941bbd2f96d074b4a`.
- Session 8 read-only fetch: `origin/main` is now
  `2775dff05948acce3a35a2d941bbd2f96d074b4a`.
- Session 8 read-only GitHub check: PR #326 remains `MERGED` at
  `2026-06-01T17:21:29Z` with merge commit
  `85f2bf5c11062741388ca114a84a2c26535b7df9`.
- Session 8 read-only GitHub list check: task249/#323 is `OPEN`/`CLEAN` at
  head `b2ae6d59c106225bdc318ccd3383ecf32cd3c37f`; task250/#324 is
  `OPEN`/`CLEAN` at head `cde927bf407667f198be6848aa0d6d3ff8745d10`.

## Prepared command shape

Do not run this until task249/task250 refresh against current `main` and lead
explicitly clears task248.

```bash
PYTHONPATH=src python src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_qwen_scaleup_run.py \
  --qwen4b-v10-pilot \
  --output-dir /work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1 \
  --remote-root /root/task248_qwen_aime_v10_4b_pilot_prepare_train_s1 \
  --run-name task248_qwen4b_v10_pilot \
  --math-sidecar-m0-input-dir /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar \
  --math-decontaminate-against-corpus /work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl \
  --pack-size 8192 \
  --seq-length 8192 \
  --num-shards 8 \
  --max-train-per-dataset 100 \
  --max-val-per-dataset 25 \
  --math-sidecar-max-records-per-env 8 \
  --math-sidecar-max-val-shadow-per-env 0 \
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

- Local prep is on HOLD until task249/task250 refresh against current `main` and lead explicitly clears task248.
- Training is on HOLD until local prep is explicitly cleared and succeeds with task246 inputs.
- FT judgment remains blocked until a future FT artifact exists and task243 comparison can enforce `ft_exact_normalized_accuracy >= base_exact_normalized_accuracy`.
- Current baseline to preserve for later comparison: Qwen3-4B base AIME25 `11/30 = 0.36666666666666664` under the corrected 30x1 same harness.
- 30B/8-GPU planning and launch remain out of scope.

## Commands run

- `git fetch origin --prune`
- `git switch -c intern_nemotron_worker_2/task248_qwen_aime_v10_4b_pilot_prepare_train_s1 origin/main`
- `git checkout 5d5e3fa -- workspace/tasks/task248_qwen_aime_v10_4b_pilot_prepare_train_s1`
- `git push -u origin intern_nemotron_worker_2/task248_qwen_aime_v10_4b_pilot_prepare_train_s1`
- `test -d /mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`
- Read-only dependency probes against worker_1/worker_3 task docs and output directories.
- Session 3 refresh: `git fetch origin --prune`, `git rev-parse` on task246/task247 branches, read-only `git ls-tree`/`git show`, and read-only output directory probes.
- Session 4 refresh: read-only `gh pr view 325`, `gh pr view 326`, `test`/`find`/`wc`/`sed` probes for task246/task247 artifacts and baseline summary.
- Session 5 refresh: read-only `gh pr view 325` and `gh pr view 326` to record #326 merged and #325 still open.
- Session 6 refresh: `git fetch origin --prune`, read-only `gh pr view 325`,
  read-only `gh pr view 326`, and read-only `gh pr list --search task249/task250`.
- Session 7 refresh: `git fetch origin --prune`, read-only `gh pr view 325`,
  and read-only `gh pr list --search "task249 OR task250"`.
- Session 8 refresh: `git fetch origin --prune`, read-only `gh pr view 325`,
  read-only `gh pr view 326`, and read-only `gh pr list --search "task249 OR task250"`.

## Commands not run

- Did not run local M0/M1 prep.
- Did not sync to NemTron.
- Did not run Qwen3-4B training.
- Did not run live eval or FT comparison.
- Did not launch or plan 30B/8-GPU scale.
- Did not delete any files under `/mnt/cephfs/data/processing/lei.song`.
