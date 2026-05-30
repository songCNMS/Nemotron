# task224 Qwen Pipeline Live Evidence Matrix Refresh

## Scope

- Owner: `intern_nem_dev_1`
- Task: `task224_qwen_pipeline_live_evidence_matrix_refresh_s1`
- Branch: `intern_nem_dev_1/task224_qwen_pipeline_live_evidence_matrix_refresh_s1`
- Base/product commit: `1d037329f5a02cdc04f2a09a16e7342721be4c87`
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task224`
- Boundary: task224 performed no live endpoint, train, eval, benchmark,
  package install/build, model copy, artifact upload, product-code edit,
  main/master push, or self-merge. This report consolidates existing verified
  reports/logs/artifacts only.

## Executive Matrix

| Stage | Source task | Owner | Branch / verified head | Base | Status | Primary artifacts | Residual risk / blocker |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen SFT full packing | task208 | intern_nem_dev_1 | `intern_nem_dev_1/task208_ceph_qwen_packing_live_s1` / `ebf8b427b04ca72d87ca2269d394c473a80b021c` | `0460c1f0262875fb27ae530d30cd80d805752851` | PASS | `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_full/splits` | Local CPU-created task208 artifacts were not directly visible on NemTron, so downstream consumers staged task-owned copies. |
| Endpoint + direct math smoke before train scale | task210 | intern_nem_dev_3 | `intern_nem_dev_3/task210_nemtron_vpn_endpoint_eval_live_s1` / `ba58c8ff9f296a840b9b37a2e46b0d3f7a9c19eb` | `0460c1f0262875fb27ae530d30cd80d805752851` | PASS | `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4` | Full benchmark not run; staged-model serving smoke only. |
| Causal-conv1d train-stack unblock | task218 | intern_nem_dev_1 | `intern_nem_dev_1/task218_causal_conv1d_contained_train_stack_unblock_s1` / `260e849462a93af67afc394dcbf1edc50b3234fa` | `1d037329f5a02cdc04f2a09a16e7342721be4c87` | PASS | `/mnt/cephfs/data/processing/nemotron-live-validation/task218` | Dependency/function probe only; no train launch in task218. |
| Single-GPU one-iter SFT | task219 | intern_nem_dev_2 | `intern_nem_dev_2/task219_qwen_sft_one_iter_post_task218_live_s1` / `9b1a0640d9daca9ab89704ba6ab383e38c6da869` | `1d037329f5a02cdc04f2a09a16e7342721be4c87` | PASS | `/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1` | Proves one single-GPU iteration and checkpoint save, not distributed/full-run stability. |
| 8-H200 full-data one-iter SFT | task220 | intern_nem_dev_2 | `intern_nem_dev_2/task220_qwen_sft_8gpu_full_data_one_iter_live_s1` / `b761477aef25c944a3deecc452c37958334008d4` | `1d037329f5a02cdc04f2a09a16e7342721be4c87` | PASS | `/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1` | Random-init smoke because no pretrained Megatron checkpoint path was supplied; validates runtime/data/checkpointing, not final quality. |
| Full benchmark preparation | task221 | intern_nem_dev_3 | `intern_nem_dev_3/task221_qwen_eval_full_benchmark_prepare_s1` / `3e33821d088f0a74eee7e4c64019b204ceb4f6af` | `1d037329f5a02cdc04f2a09a16e7342721be4c87` | PASS/HOLD | `/mnt/cephfs/data/processing/nemotron-live-validation/task221` | Prepared commands and dry-runs only; live benchmark remains held. |
| Old matrix | task222 | intern_nem_dev_1 | `intern_nem_dev_1/task222_qwen_pipeline_live_evidence_matrix_s1` / `910897c9166a48adf121fb5c229bf0c1d6fb671f` | `1d037329f5a02cdc04f2a09a16e7342721be4c87` | PASS but stale | `/mnt/cephfs/data/processing/nemotron-live-validation/task222/validation_report.md` | Stale because it predates verified task220 and task223 PASS. |
| Endpoint + sanitized smoke + corrected math after train scale | task223 | intern_nem_dev_3 | `intern_nem_dev_3/task223_qwen_endpoint_eval_live_after_task220_s1` / `d852588606c5ddef0f183ace503c67749a302d2e` | `1d037329f5a02cdc04f2a09a16e7342721be4c87` | PASS/HOLD | `/mnt/cephfs/data/processing/nemotron-live-validation/task223` | Endpoint and corrected math PASS; M1 subset/full benchmark held by runner/mapping/M2 blockers and PM re-release. |

## Pipeline Status

End-to-end live validation now has verified PASS evidence for:

- full Qwen SFT packing on the task071 source blend (`task208`);
- staged Qwen base-model endpoint serving and direct corrected-math smoke
  before train-scale validation (`task210`);
- contained causal-conv1d dependency/function unblock for the train stack
  (`task218`);
- canonical single-GPU one-iteration SFT and checkpoint save (`task219`);
- canonical 8-H200 full-data one-iteration SFT, validation, cleanup, and
  checkpoint save (`task220`);
- staged Qwen endpoint serving, sanitized chat smoke, and direct corrected-math
  smoke after task220 (`task223`).

The remaining blockers are benchmark-runner and coverage blockers, not
Qwen model/data/H200 availability blockers:

- `nemo_evaluator_launcher` runtime is missing from the local
  `/work-agents/.venv`, blocking official corrected-math and M1 launcher runs.
- Five M1 targets still lack exact launcher mappings:
  `multichallenge`, `terminalbench`, `mcp_mark`, `tool_decathlon`,
  `swe_bench_verified`.
- M2 coverage still needs runtime assets, APIs, databases, sandboxes, and frozen
  baselines.
- Full benchmark requires fresh PM re-release after those blockers are handled.

## Detailed Evidence

### task208: Qwen full SFT packing PASS

- Owner: `intern_nem_dev_1`
- Branch/head:
  `intern_nem_dev_1/task208_ceph_qwen_packing_live_s1` /
  `ebf8b427b04ca72d87ca2269d394c473a80b021c`
- Base/product commit:
  `0460c1f0262875fb27ae530d30cd80d805752851`
- Model/tokenizer:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- Source blend:
  `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/m1_agentic_sft/data_blend_agentic_sft_v0.json`
- Corrected full split path:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_full/splits`
- Full command:

```bash
PYTHONPATH=src NEMO_RUN_DIR=/mnt/cephfs/data/processing/nemotron-live-validation/task208 SUPER3_M1_QWEN_HF_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 /work-agents/.venv/bin/python -m nemotron super3 data prep sft -c qwen_agentic_v0 blend_path=/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/m1_agentic_sft/data_blend_agentic_sft_v0.json output_dir=/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_full sample=null num_shards=16 observability.wandb_log_pipeline_stats=false
```

- Result: PASS, `total_sequences=987770`, `total_tokens=672687706`,
  `num_shards=16`, `pack_size=4096`,
  `elapsed_sec=253.65463423728943`.
- Validators: focused packing/data-prep shard passed, `53 passed`.
- Key artifacts:
  `packed_qwen_full/blend.json`, `packed_qwen_full/splits/metadata.json`,
  `packed_qwen_full/runs/7f636cefa24d6f6a/config.json`, 32 parquet data files,
  18 split symlinks, and
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/logs/task208_output_checksums.sha256`.
- Residual risk: direct task208 full split path was not NemTron-visible; task220
  staged a dereferenced task-owned copy before 8-GPU training.

### task210: staged-model endpoint and direct math smoke PASS

- Owner: `intern_nem_dev_3`
- Branch/head:
  `intern_nem_dev_3/task210_nemtron_vpn_endpoint_eval_live_s1` /
  `ba58c8ff9f296a840b9b37a2e46b0d3f7a9c19eb`
- Base/product commit:
  `0460c1f0262875fb27ae530d30cd80d805752851`
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4`
- Staged model:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/staged_model/Qwen3-30B-A3B-Instruct-2507`
- SGLang evidence: staged model served as
  `qwen3-30b-a3b-instruct-2507-staged` on port `13000`, TP=8 H200.
- Sanitized endpoint smoke: PASS, HTTP 200, content `OK`, `max_tokens=8`, no
  benchmark prompt, no secrets, Qwen chat kwargs false/false.
- Direct corrected math command:

```bash
/work-agents/.venv/bin/python /mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/eval/direct_corrected_math_live_smoke_with_kwargs_wrapper.py --aime-score-cache /work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/aime_score_cache.db --hmmt-output-jsonl /work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/hmmt_output.jsonl --output-dir /mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/eval/direct_corrected_math_live_smoke_with_kwargs --endpoint-url http://10.100.2.62:13000/v1/chat/completions --model-id qwen3-30b-a3b-instruct-2507-staged --aime-limit-rows 1 --hmmt-limit-rows 1 --parallelism 1 --timeout 900
```

- Direct math result: PASS, 2 requests, AIME 1/1 parsed/correct, HMMT 1/1
  parsed/correct, runtime 37.736 seconds.
- Cleanup: no SGLang, no `:13000`, all 8 H200 idle.
- Residual risk: full 27-target benchmark not run.

### task218: contained causal-conv1d unblock PASS

- Owner: `intern_nem_dev_1`
- Branch/head:
  `intern_nem_dev_1/task218_causal_conv1d_contained_train_stack_unblock_s1` /
  `260e849462a93af67afc394dcbf1edc50b3234fa`
- Base/product commit:
  `1d037329f5a02cdc04f2a09a16e7342721be4c87`
- Evidence root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task218`
- Validation report:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task218/validation_report.md`
  (`sha256=9bcd69ed88e12533d671321bc147fb20157320bd30d9f3c7bcdb7831eb53af09`)
- Built/installed package: `causal-conv1d==1.6.2.post1` into task-owned
  `/mnt/cephfs/data/processing/nemotron-live-validation/task218/pip_target`.
- Provenance:
  sdist `sha256=245e314ea21064ded7a5bf6b3b842b644aa6f92e45cecfe3e935629744c35ff4`;
  wheel `sha256=347a4cf7d1b629162ce891cda40bdf5c20e1fa1da81ccc2e78467828e8f5ce6e`;
  extension
  `sha256=b9b896d914d4dc90284863335bbc10a93099c2c49cdd969c0e57dcbded9e3497`.
- Probes: `TASK218_IMPORT_FUNCTION_PROBE_PASS`,
  `TASK218_TINY_CUDA_SMOKE_PASS`, `TASK218_CONTAINMENT_PROBE_PASS`.
- Residual risk: no training rerun was launched in task218 itself.

### task219: single-GPU one-iteration SFT PASS

- Owner: `intern_nem_dev_2`
- Branch/head:
  `intern_nem_dev_2/task219_qwen_sft_one_iter_post_task218_live_s1` /
  `9b1a0640d9daca9ab89704ba6ab383e38c6da869`
- Base/product commit:
  `1d037329f5a02cdc04f2a09a16e7342721be4c87`
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1`
- Exact command:

```bash
cd /mnt/cephfs/data/processing/nemotron-live-validation/task219/Nemotron
PYTHONPATH="/mnt/cephfs/data/processing/nemotron-live-validation/task218/pip_target:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv/lib/python3.12/site-packages:/mnt/cephfs/data/processing/nemotron-live-validation/task219/Nemotron/src" \
NEMO_RUN_DIR="/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1" \
SUPER3_M1_AGENTIC_PACKED_DIR="/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits" \
SUPER3_M1_TOKENIZER_MODEL="/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507" \
SUPER3_M1_QWEN_HF_MODEL="/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507" \
SUPER3_M1_TRAINING_PROFILE="qwen" \
SUPER3_M1_SFT_SMOKE_SAVE="/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1/checkpoints_one_iter" \
CUDA_VISIBLE_DEVICES=0 \
/usr/local/bin/torchrun --nproc_per_node=1 --master_addr=127.0.0.1 --master_port=29581 \
  src/nemotron/recipes/super3/stage1_sft/test_train.py \
  --config "/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1/m1_agentic_smoke_qwen_contract.yaml" \
  train.train_iters=1 checkpoint.save_interval=1 artifacts.wandb=false artifacts.manifest.root=null
```

- Result: PASS, `task219_torchrun_rc=0`, iteration `1/1`, consumed samples
  `1`, loss `1.195105E+01`, skipped/nan `0/0`.
- Checkpoint:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1/checkpoints_one_iter`,
  size `1.2G`, latest iteration `1`.
- Residual risk: single-GPU one-iteration only.

### task220: 8-H200 full-data one-iteration SFT PASS

- Owner: `intern_nem_dev_2`
- Branch/head:
  `intern_nem_dev_2/task220_qwen_sft_8gpu_full_data_one_iter_live_s1` /
  `b761477aef25c944a3deecc452c37958334008d4`
- Base/product commit:
  `1d037329f5a02cdc04f2a09a16e7342721be4c87`
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1`
- Full staged input:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220/input_task208_full/splits`
- Config:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/m1_agentic_8gpu_full_qwen30b_contract.yaml`
  (`sha256=3114416101d87ef3a3b106da521fd7ac39b1bde5cc2f95f39b1b884a4a8cb048`)
- Exact command:

```bash
cd /mnt/cephfs/data/processing/nemotron-live-validation/task220/Nemotron
PYTHONPATH=/mnt/cephfs/data/processing/nemotron-live-validation/task218/pip_target:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv/lib/python3.12/site-packages:/mnt/cephfs/data/processing/nemotron-live-validation/task220/Nemotron/src NEMO_RUN_DIR=/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1 SUPER3_M1_AGENTIC_PACKED_DIR=/mnt/cephfs/data/processing/nemotron-live-validation/task220/input_task208_full/splits SUPER3_M1_TOKENIZER_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 SUPER3_M1_QWEN_HF_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 SUPER3_M1_TRAINING_PROFILE=qwen SUPER3_M1_SFT_SMOKE_SAVE=/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/checkpoints_one_iter WANDB_DISABLED=true CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 /usr/local/bin/torchrun --nproc_per_node=8 --master_addr=127.0.0.1 --master_port=29591 src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py --config /mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/m1_agentic_8gpu_full_qwen30b_contract.yaml train.train_iters=1 checkpoint.save_interval=1 artifacts.wandb=false artifacts.manifest.root=null
```

- Result: PASS, `task220_torchrun_rc=0`.
- Train metrics: iteration `1/1`, consumed samples `8`,
  `lm loss 1.226097E+01`, `load_balancing_loss 3.226302E+00`, grad norm
  `123.805`, skipped/nan `0/0`.
- Validation metrics: loss `1.043498E+01`, PPL `3.402951E+04`.
- Step timing: log reports elapsed time per iteration `36127.5` ms.
- Checkpoint:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/checkpoints_one_iter`,
  size `399G`, latest iteration `1`, `iter_0000001` present.
- Cleanup: no task220/Qwen/torchrun processes, no H200 compute apps, `:13000`
  and `:29591` clear, `:8000` documented/untouched.
- Key logs:
  `00_full_data_staging.log`, `01_code_config_stage.log`,
  `02_preflight_resource.log`, `03_data_stack_config_probe.log`,
  `04_canonical_8gpu_one_iter_torchrun.log`,
  `05_checkpoint_cleanup_state.log`, `06_local_visibility_manifest.log`.
- Residual risk: random-init smoke because no pretrained Megatron checkpoint
  path was supplied; validates distributed runtime, full packed data path,
  train step, validation, checkpoint save, and cleanup, not final trained-model
  quality.

### task221: full benchmark prepare PASS/HOLD

- Owner: `intern_nem_dev_3`
- Branch/head:
  `intern_nem_dev_3/task221_qwen_eval_full_benchmark_prepare_s1` /
  `3e33821d088f0a74eee7e4c64019b204ceb4f6af`
- Base/product commit:
  `1d037329f5a02cdc04f2a09a16e7342721be4c87`
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task221`
- Validation report:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task221/validation_report.md`
  (`sha256=3cd5fcabf994781597ef101630f7c660e5ddbb35b154c5ce9399081bc1699ff7`)
- Full 27-target plan:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task221/full_27_target_plan.md`
  (`sha256=dc3c8bea99728927a85bf81c9696d208ca6ab9244ad91a911dac75353bf39dcb`)
- Static validators:

```bash
PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q \
  tests/recipes/super3/test_qwen_eval_repro_gate.py \
  tests/recipes/super3/test_benchmark_alignment_path_guards.py \
  tests/recipes/super3/test_m1_eval_full_basket.py \
  tests/recipes/super3/test_m2_eval_basket_s1.py \
  tests/recipes/super3/test_m2_eval_basket_s2.py
```

- Validator result: `136 passed, 8 warnings in 3.51s`.
- Corrected math exact-command dry-run: PASS, artifact
  `readiness/corrected_math_exact_command_dry_run.log`.
- M1 launcher-available exact-command dry-run: PASS, artifact
  `readiness/m1_launcher_available_exact_command_dry_run.log`.
- Prepared artifacts include SGLang command, sanitized endpoint smoke request
  and command, corrected math commands, M1 launcher-available command, M1 full
  basket command, static eval targets JSON, visibility logs, prompt safety scan,
  and full 27-target plan.
- Hold/blockers: no SGLang launch, endpoint request, live eval, benchmark,
  model copy, package install/build, process kill, W&B/cluster/deploy, or
  artifact upload; PM release and runtime blockers remain required.

### task222: old matrix PASS but stale

- Owner: `intern_nem_dev_1`
- Branch/head:
  `intern_nem_dev_1/task222_qwen_pipeline_live_evidence_matrix_s1` /
  `910897c9166a48adf121fb5c229bf0c1d6fb671f`
- Base/product commit:
  `1d037329f5a02cdc04f2a09a16e7342721be4c87`
- Validation report:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task222/validation_report.md`
  (`sha256=a38dd6c784f3b5fa0ee7884705ffdee1d514b2ec29f8b09d8ec7dd3d0b332b37`)
- Verification: PM/test accepted task222 PASS.
- Staleness: task222 predated verified task220 and task223 PASS, so it showed
  task220/task221 pending/readiness notes and did not include task223.

### task223: endpoint, sanitized smoke, corrected math PASS/HOLD

- Owner: `intern_nem_dev_3`
- Branch/head:
  `intern_nem_dev_3/task223_qwen_endpoint_eval_live_after_task220_s1` /
  `d852588606c5ddef0f183ace503c67749a302d2e`
- Base/product commit:
  `1d037329f5a02cdc04f2a09a16e7342721be4c87`
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task223`
- Endpoint command:

```bash
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export TOKENIZERS_PARALLELISM=false
export TASK223_OWNER=intern_nem_dev_3
python3 -m sglang.launch_server \
  --model-path /mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/staged_model/Qwen3-30B-A3B-Instruct-2507 \
  --served-model-name qwen3-30b-a3b-instruct-2507-staged \
  --host 0.0.0.0 \
  --port 13000 \
  --tensor-parallel-size 8 \
  --trust-remote-code \
  --context-length 16384 \
  --reasoning-parser qwen3
```

- Endpoint result: PASS. SGLang launched from NemTron-visible command path on
  `:13000`, TP=8, context 16384, served model
  `qwen3-30b-a3b-instruct-2507-staged`; `/health` and `/v1/models` returned
  200.
- Sanitized endpoint smoke command:

```bash
ROOT=/mnt/cephfs/data/processing/nemotron-live-validation/task223
curl -sS \
  -H 'Content-Type: application/json' \
  --data @"$ROOT/endpoint_smoke/sanitized_endpoint_smoke_request.json" \
  http://127.0.0.1:13000/v1/chat/completions
```

- Sanitized endpoint smoke result: PASS, HTTP 200, content `OK`, non-null
  message content, `max_tokens=8`, no benchmark prompt, no secrets, Qwen kwargs
  false/false.
- Direct corrected math command:

```bash
/work-agents/.venv/bin/python \
  /mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/eval/direct_corrected_math_live_smoke_with_kwargs_wrapper.py \
  --aime-score-cache /work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/aime_score_cache.db \
  --hmmt-output-jsonl /work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/hmmt_output.jsonl \
  --output-dir /mnt/cephfs/data/processing/nemotron-live-validation/task223/eval/direct_corrected_math_live_smoke_with_kwargs \
  --endpoint-url http://10.100.2.62:13000/v1/chat/completions \
  --model-id qwen3-30b-a3b-instruct-2507-staged \
  --aime-limit-rows 1 \
  --hmmt-limit-rows 1 \
  --parallelism 1 \
  --timeout 900
```

- Corrected math result: PASS via validated direct wrapper fallback. AIME 1/1
  parsed/correct, HMMT 1/1 parsed/correct, non-null content, runtime
  37.626 seconds.
- Holds:
  - M1 launcher-available subset HOLD because official launcher runtime is
    unavailable.
  - Full 27-target benchmark HOLD because no fresh PM re-release and M1/M2
    blockers remain.
- Cleanup: PASS. Final state had no SGLang, no `:13000`, no H200 compute apps,
  all 8 H200s idle, only documented `:8000` listener remaining.
- Artifact nuance: first local CPU-created command/request files were not
  visible on NemTron; dev_3 rewrote the same command/request under the
  NemTron-visible task223 artifact path before the successful launch/smoke.

## Namespace and Model Notes

- Canonical local stable model/tokenizer:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- NemTron-visible staged model used for endpoint tasks:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/staged_model/Qwen3-30B-A3B-Instruct-2507`.
- Task208 full output is local CPU visible but not directly NemTron-visible; the
  task220 dereferenced staged input under
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220/input_task208_full/splits`
  is the verified NemTron-visible full-data train input.
- Task223 had the same command/request visibility class: local CPU-created files
  were not sufficient for NemTron launch, so command/request artifacts were
  recreated under a NemTron-visible task-owned path.
- Task219 and task220 checkpoints were verified on NemTron; local CPU
  visibility can differ from NemTron visibility for large/runtime-created
  artifacts.

## Remaining Work and Estimates

### Training

- Verified now: dependency stack, single-GPU one iteration, and 8-H200
  full-data one iteration with checkpoint.
- Remaining training proof: a real production train needs the intended
  pretrained Megatron checkpoint path, target `train_iters`, global batch,
  node/GPU allocation, checkpoint cadence, resume policy, and quality target.
- Task220 measured one smoke iteration at `36127.5` ms/iteration with
  `global_batch_size=8`; one full pass over `987770` packed sequences at this
  exact smoke batch would be about `123472` optimizer steps, which is not a
  production estimate. PM should recompute the full-train ETA from the intended
  production batch/node plan.
- Near-term rerun estimate for the already proven task220-style one-iteration
  gate: about 20-45 minutes including preflight, launch, validation, checkpoint
  inventory, and cleanup if resources are released and no new blocker appears.

### Benchmark

- Verified now: endpoint serving, sanitized chat smoke, and direct corrected
  math smoke after task220.
- Re-launch endpoint and rerun smoke after PM release: 20-45 minutes.
- Corrected math smoke with official launcher runtime: 5-15 minutes; already
  validated direct fallback path runs under 1 minute after endpoint readiness.
- M1 14-target launcher-available subset: task223 estimates 8-24 hours,
  dependent on official evaluator runtime, task parallelism, long-context/code
  workloads, and endpoint throughput.
- Full 27-target M1/M2 benchmark: HOLD; task223 estimates 24-72 hours plus
  setup/debug after `nemo_evaluator_launcher`, missing M1 mappings, M2
  assets/APIs/databases/sandboxes/baselines, and PM re-release are all resolved.

## Sources Read

- `/work-agents/intern_nem_dev_1/report.md`
- `/work-agents/intern_nem_dev_2/report.md`
- `/work-agents/intern_nem_dev_3/report.md`
- `/work-agents/intern_nem_pm/report.md`
- `/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/logs/*`
- `/mnt/cephfs/data/processing/nemotron-live-validation/task221/validation_report.md`
- `/mnt/cephfs/data/processing/nemotron-live-validation/task223/validation_report.md`
- `/mnt/cephfs/data/processing/nemotron-live-validation/task223/commands/*`

## task224 Validation

- `git diff --check`: passed before commit.
- `git diff --cached --check`: passed before commit.
- Product-code edits: none.
- Live operations by task224: none.
