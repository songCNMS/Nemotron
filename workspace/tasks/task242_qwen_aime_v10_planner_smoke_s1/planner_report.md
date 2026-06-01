# task242 planner report

<!-- METADATA:STATUS=ReadyForPR,SESSION=2 -->

## Summary

- Added planner support for `hard_math_runlength_dp_v10`.
- Added a Qwen3-4B V10 pilot profile using `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Encoded the same-harness AIME25 base-vs-FT non-regression gate in the manifest before any 30B/8-GPU scale is allowed.
- Generated a task-owned smoke bundle under `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot`.
- Did not run training, live eval, or any 30B/8-GPU job.

## Generated command

```bash
PYTHONPATH=src python src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_qwen_scaleup_run.py \
  --qwen4b-v10-pilot \
  --run-name task242_qwen4b_v10_pilot \
  --math-sidecar-m0-input-dir /work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/task241_v10_math_sidecar_m0_PENDING \
  --math-decontaminate-against-corpus /work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/aime25_hmmt_math_heldout_decontam_corpus.PLACEHOLDER.jsonl \
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

## Generated artifacts

- Manifest: `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/scaleup_manifest.json`
- Planner report: `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/report.md`
- Local data-prep script: `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/run_local_data_prep.sh`
- NemTron sync script: `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/sync_to_nemtron.sh`
- NemTron train script: `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/run_nemtron_train.sh`
- Eval dry-run script: `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/run_eval_basket_dry_run.sh`

## Pilot contract

- Pilot model/checkpoint/tokenizer path: `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`
- Math strategy: `hard_math_runlength_dp_v10`
- Default V10 weights: hard verified full-solution `1.0`, broad verified `0.0`, final-answer aux `0.0`, format repair `0.0`
- Local output root: `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot`
- NemTron remote root: `/root/task242_qwen_aime_v10_planner_smoke_s1`
- Remote run root: `/root/task242_qwen_aime_v10_planner_smoke_s1/task242_qwen_aime_v10_4b_pilot`
- Train tmux session name: `task242_task242_qwen4b_v10_pilot`

## Safety checks

- V10 manifest creation fails if `--math-decontaminate-against-corpus` is missing, not a file, or empty.
- Generated local data-prep script refuses the task242 placeholder corpus marker before running M0/M1 data prep.
- Generated sync script refuses non-`/root/*` V10 pilot remote roots.
- Generated sync script only removes the task-owned `/root/task242_qwen_aime_v10_planner_smoke_s1/...` paths and prints that it does not delete `/mnt/cephfs/data/processing/lei.song`.

## AIME gate

- Gate id: `qwen3_4b_v10_aime25_same_harness_non_regression`
- Base model path: `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`
- Candidate FT output path: `/root/task242_qwen_aime_v10_planner_smoke_s1/task242_qwen_aime_v10_4b_pilot/checkpoints`
- Corrected evaluator config: `src/nemotron/recipes/super3/stage3_eval/config/m1_corrected_math_comparison.yaml`
- Pilot protocol: AIME25 held-out prompts, 1 repeat per problem, `8192` max tokens, `/v1/chat/completions`, `temperature=0.0`, `top_p=1e-5`
- Non-regression rule: `ft_exact_normalized_accuracy >= base_exact_normalized_accuracy`
- Required diagnostics: numerator, denominator, parsed count, finish reasons, per-problem rows
- 30B hold: Qwen3-30B-A3B / 8-GPU planning is refused unless `--allow-v10-30b-scale` is explicitly supplied after the Qwen3-4B same-harness gate is documented as passing.

## Checks

- `python -m py_compile src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_qwen_scaleup_run.py` passed.
- `PYTHONPATH=src pytest -q tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py` passed: 29 passed.
- `ruff check src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_qwen_scaleup_run.py tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py` passed.
- `git diff --check` passed.
- Verified `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507` exists in this worker environment.

## Blockers and residual risk

- Real AIME25/HMMT/MATH held-out decontamination corpus is not visible in this worker workspace. The generated bundle uses a task-owned placeholder only to materialize paths; the generated local data-prep script fails closed until it is replaced.
- The task241 V10 data-prep interface is on `origin/intern_nemotron_worker_1/task241_qwen_aime_v10_sidecar_data_s1` and is not on `origin/main` at this report time. The planner is wired to the worker_1 interface, but local data prep will not run on main until that code lands or is explicitly combined.
- No same-harness Qwen3-4B base or FT AIME25 live score was produced here. Task243 owns that gate; this task only records the required manifest contract and script-side hold.
- No training, sync, or live eval commands were executed.
