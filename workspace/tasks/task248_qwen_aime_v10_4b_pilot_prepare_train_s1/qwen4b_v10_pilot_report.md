# task248 Qwen3-4B V10 pilot report

<!-- METADATA:STATUS=Blocked,SESSION=9 -->

## Summary

- Branch `intern_nemotron_worker_2/task248_qwen_aime_v10_4b_pilot_prepare_train_s1` was created from current `origin/main` after PR #321 merge commit `20973e78f196d7e5d71993f60dc74a3500223f5f`.
- Qwen3-4B pilot model path exists locally: `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Local output root reserved for this task:
  `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/`.
- NemTron remote root reserved for this task:
  `/root/task248_qwen_aime_v10_4b_pilot_prepare_train_s1`.
- Session 9 lead clearance arrived after task246/#325, task247/#326,
  task250/#324, and task249/#323 merged on current `main`
  `ec467724c2876211cd2bf56b15071e31abd692a4`.
- Planner/script artifacts are generated under the task-owned local output
  root, but local prep is incomplete and blocked before M1/packed/training
  artifacts.

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
- Session 9 update: PR #323 is `MERGED` at `2026-06-01T18:19:00Z` with merge
  commit `ec467724c2876211cd2bf56b15071e31abd692a4`; PR #324 is `MERGED` at
  `2026-06-01T18:12:43Z` with merge commit
  `ff28538c41620a6d8b75b33d70c0c5e69714f42e`.
- Session 9 `origin/main` is `ec467724c2876211cd2bf56b15071e31abd692a4`.

## Prepared command shape

This command was run in Session 9 to generate planner artifacts. It did not run
local prep, sync, train, or eval by itself.

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

- Planner artifacts are generated, but local prep is incomplete.
- Training is blocked until local prep succeeds with task246 inputs.
- FT judgment remains blocked until a future FT artifact exists and task243 comparison can enforce `ft_exact_normalized_accuracy >= base_exact_normalized_accuracy`.
- Current baseline to preserve for later comparison: Qwen3-4B base AIME25 `11/30 = 0.36666666666666664` under the corrected 30x1 same harness.
- 30B/8-GPU planning and launch remain out of scope.

## Session 9 artifact status

Complete planner artifacts:

- Manifest: `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/scaleup_manifest.json`
  (`sha256 78df024dfd1f1b32770573c31b90e403bbcdc81683693602df5accf0f7bc0b1d`)
- Planner report: `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/report.md`
  (`sha256 f6823ab4a0ff8a3b00332b13fc63258394f3c4f2210ea5a6fcdc77deda73787a`)
- Local prep script: `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/run_local_data_prep.sh`
  (`sha256 d587f73278c8d8f603dbe1fb5979f0596b9445dd033f7f5f4c0df1ace49392a2`)
- NemTron sync script: `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/sync_to_nemtron.sh`
  (`sha256 a0840717a6c74a9dd662161fd1a55e8a6ddef7c3bbeefd2b2ebe05bddb7e7f5b`)
- NemTron train script: `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/run_nemtron_train.sh`
  (`sha256 cec3bce9d56c898c73395b7f6de42fa7cfdfd8d066675b0d20a48d8427580c58`)
- Eval dry-run script: `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/run_eval_basket_dry_run.sh`
  (`sha256 28bcc862272e772cc89d54c21664c7cd6cb550d3316cdd0a9c28c2b361d36ca1`)

Manifest checks:

- Qwen model/tokenizer: `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`
- Math strategy: `hard_math_runlength_dp_v10`
- Task246 corpus: `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl`
- Task246 M0 sidecar: `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar`
- Sparse sidecar knobs: `8` train rows and `0` val shadow rows.
- Qwen chat-template packing preserves `enable_thinking=false` and `truncate_history_thinking=false`.
- `math_skip_decontamination_check=false`; `allow_v10_30b_scale=false`.

Partial local prep artifacts:

- `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/m0_agentic/search_grounded_qa/train-split.jsonl`: `100` rows.
- `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/m0_agentic/search_grounded_qa/val-split.jsonl`: `25` rows.
- `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/m0_agentic/search_multihop_qa/train-split.jsonl`: `100` rows.
- `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/m0_agentic/search_multihop_qa/val-split.jsonl`: `25` rows.
- `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/m0_agentic/code_execution_python/train-split.jsonl`: `100` rows.

Missing incomplete-stage artifacts:

- Missing `m0_agentic/manifest.json`.
- Missing `m1_agentic_sft/data_blend_agentic_sft_v0.json`.
- Missing `packed_qwen/splits`.
- Missing `training_plan/task248_qwen4b_v10_pilot/training_manifest.json`.
- Missing local and remote checkpoints/exports.
- Missing FT eval output and task243 same-harness comparison output.

Local prep logs:

- `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/logs/local_data_prep_session9.log`
  (`sha256 ab10b8e64c9941d00d74d2359f6d95753b08b5973557c400c67058c532164019`):
  generated script failed at missing `/work-agents/.venv/bin/activate`.
- `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/logs/local_data_prep_session9_no_venv.log`
  (`sha256 8f3032f8a81e429b62e097d20bbc07d310053b50c684c5b2f2ce1bdaef9fc6c1`):
  retry without venv failed because `datasets` was missing.
- `/work-agents/intern_nemotron_worker_2/outputs/task248_qwen_aime_v10_4b_pilot_prepare_train_s1/logs/local_data_prep_session9_retry_after_deps.log`
  (`sha256 1c53ccbac1dff62ed75dd267b54d1f16b09e2090609023933f0e11ee055ff248`):
  retry after `datasets`/`hydra-core` install stopped in M0 data prep at the
  Hugging Face `datasets` `trust_remote_code` incompatibility for
  `hotpotqa/hotpot_qa`.

Current blocker:

- Need a working local prep environment matching the generated script contract,
  or an update to the M0 data prep path that avoids the installed `datasets`
  `trust_remote_code` incompatibility for `hotpotqa/hotpot_qa`.
- The output is not ready for task243 comparison.

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
- Session 9 refresh: `git fetch origin --prune`, read-only `gh pr view`
  for #323/#324/#325/#326, `git merge --no-edit origin/main`.
- Session 9 planner generation: the prepared command in this report.
- Session 9 local prep attempts:
  - `bash run_local_data_prep.sh`
  - `awk 'NR!=5 {print}' run_local_data_prep.sh | bash`
  - `python -m pip install --user 'datasets>=2.14.0' 'hydra-core>=1.3.2'`
  - retry of `awk 'NR!=5 {print}' run_local_data_prep.sh | bash`

## Commands not run

- Did not sync to NemTron.
- Did not run Qwen3-4B training.
- Did not run live eval or FT comparison.
- Did not launch or plan 30B/8-GPU scale.
- Did not delete any files under `/mnt/cephfs/data/processing/lei.song`.
