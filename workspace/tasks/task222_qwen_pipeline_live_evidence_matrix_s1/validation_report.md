# task222 Qwen Pipeline Evidence Matrix

## Scope

- Owner: `intern_nem_dev_1`
- Branch: `intern_nem_dev_1/task222_qwen_pipeline_live_evidence_matrix_s1`
- Base: `1d037329f5a02cdc04f2a09a16e7342721be4c87`
- Evidence artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task222`
- Boundary: no GPU, endpoint, train, eval, benchmark, package install, model
  copy/download, W&B, cluster/deploy, artifact upload, product-code edit,
  main/master push, or self-merge was performed for task222. This report only
  consolidates existing verified evidence and read-only logs.

## Executive Matrix

| Pipeline stage | Source task | Owner | Branch / verified head | Base | Status | Primary artifacts | Blocker / residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen SFT packing, full data | task208 | intern_nem_dev_1 | `intern_nem_dev_1/task208_ceph_qwen_packing_live_s1` / `ebf8b427b04ca72d87ca2269d394c473a80b021c` | `0460c1f0262875fb27ae530d30cd80d805752851` | PASS | `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_full/splits` | Local CPU can see corrected-root artifacts; NemTron needed explicit staging because the same namespace was not visible there. |
| Qwen endpoint and math eval smoke | task210 | intern_nem_dev_3 | `intern_nem_dev_3/task210_nemtron_vpn_endpoint_eval_live_s1` / `ba58c8ff9f296a840b9b37a2e46b0d3f7a9c19eb` | `0460c1f0262875fb27ae530d30cd80d805752851` | PASS | `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4` | Full 27-target benchmark not run; endpoint/model was staged for smoke only. |
| Train dependency stack unblock | task218 | intern_nem_dev_1 | `intern_nem_dev_1/task218_causal_conv1d_contained_train_stack_unblock_s1` / `260e849462a93af67afc394dcbf1edc50b3234fa` | `1d037329f5a02cdc04f2a09a16e7342721be4c87` | PASS | `/mnt/cephfs/data/processing/nemotron-live-validation/task218` | No train rerun in task218; it proves contained import/function/CUDA-extension readiness only. |
| Canonical single-GPU one-iter SFT | task219 | intern_nem_dev_2 | `intern_nem_dev_2/task219_qwen_sft_one_iter_post_task218_live_s1` / `9b1a0640d9daca9ab89704ba6ab383e38c6da869` | `1d037329f5a02cdc04f2a09a16e7342721be4c87` | PASS | `/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1` | Proves one single-GPU iteration and checkpoint save, not multi-GPU/full-run stability. |
| 8-H200 full-data one-iter SFT | task220 | intern_nem_dev_2 | `intern_nem_dev_2/task220_qwen_sft_8gpu_full_data_one_iter_live_s1` / local branch currently at base `1d037329f5a02cdc04f2a09a16e7342721be4c87` | `1d037329f5a02cdc04f2a09a16e7342721be4c87` | PENDING | `/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1` staging logs | Full task208 splits and config are staged; no verified 8-GPU torchrun result was present in existing reports/logs read for task222. |
| Full benchmark prepare/run | task221 | intern_nem_dev_3 | `intern_nem_dev_3/task221_qwen_eval_full_benchmark_prepare_s1` / local branch currently at base `1d037329f5a02cdc04f2a09a16e7342721be4c87` | `1d037329f5a02cdc04f2a09a16e7342721be4c87` | PENDING | `/mnt/cephfs/data/processing/nemotron-live-validation/task221/readiness` | Prepare-only; local launcher probe reports `No module named 'nemo_evaluator_launcher'`; no endpoint/eval/benchmark should run until PM release. |

## Detailed Evidence

### task208: full Qwen SFT packing PASS

- Owner: `intern_nem_dev_1`
- Branch/head:
  `intern_nem_dev_1/task208_ceph_qwen_packing_live_s1` /
  `ebf8b427b04ca72d87ca2269d394c473a80b021c`
- Superseded historical head:
  `e197fb1af7ca4ad48e0573707fbe74edbb935311`
- Base/product commit:
  `0460c1f0262875fb27ae530d30cd80d805752851`
- Model/tokenizer path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- Source blend:
  `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/m1_agentic_sft/data_blend_agentic_sft_v0.json`
- Corrected sample split path:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_sample4/sample-4/splits`
- Corrected full split path:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_full/splits`
- Full command:

```bash
PYTHONPATH=src NEMO_RUN_DIR=/mnt/cephfs/data/processing/nemotron-live-validation/task208 SUPER3_M1_QWEN_HF_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 /work-agents/.venv/bin/python -m nemotron super3 data prep sft -c qwen_agentic_v0 blend_path=/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_clean_final_v8/m1_agentic_sft/data_blend_agentic_sft_v0.json output_dir=/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_full sample=null num_shards=16 observability.wandb_log_pipeline_stats=false
```

- Result: PASS, `2026-05-30T16:17:24Z` to `2026-05-30T16:21:46Z`.
- Metrics: `total_sequences=987770`, `total_tokens=672687706`,
  `num_shards=16`, `pack_size=4096`, `elapsed_sec=253.65463423728943`.
- Artifacts: `blend.json` 6308 bytes, `splits/metadata.json` 3239 bytes,
  `runs/7f636cefa24d6f6a/config.json` 1652 bytes, 32 parquet data files,
  18 split symlinks (`train=16`, `valid=1`, `test=1`), corrected root about
  4.0G.
- Logs:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/logs/qwen_full_packing.log`,
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/logs/static_validators_pytest.log`,
  and
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/logs/task208_output_checksums.sha256`.
- Validators: focused packing/data-prep validator shard passed,
  `53 passed in 2.09s`.
- Historical blocker: old root
  `/mnt/cephfs/data/nemotron-live-validation/task208` failed with
  `PermissionError: [Errno 13] Permission denied`; old head is retained only as
  superseded evidence.
- Residual risk: PM reported local CPU visibility for the corrected root but
  NemTron could not see local CPU-created task208 artifacts at the same path.
  Downstream tasks therefore staged sample/full splits into NemTron-visible
  task-owned paths.

### task210: endpoint and direct math eval smoke PASS

- Owner: `intern_nem_dev_3`
- Branch/head:
  `intern_nem_dev_3/task210_nemtron_vpn_endpoint_eval_live_s1` /
  `ba58c8ff9f296a840b9b37a2e46b0d3f7a9c19eb`
- Base/product commit:
  `0460c1f0262875fb27ae530d30cd80d805752851`
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4`
- Staged model path:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/staged_model/Qwen3-30B-A3B-Instruct-2507`
- Staging command:

```bash
cd /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 && tar -cf - LICENSE README.md config.json config_1m.json configuration.json generation_config.json merges.txt model.safetensors.index.json tokenizer.json tokenizer_config.json vocab.json model-000??-of-00016.safetensors | ssh NemTron 'mkdir -p /mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/staged_model/Qwen3-30B-A3B-Instruct-2507 && tar -C /mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/staged_model/Qwen3-30B-A3B-Instruct-2507 -xpf -'
```

- Staging result: PASS, copy exit `0`, 16 safetensor shards visible on NemTron,
  `file_size_manifest_match=true`, `small_file_sha256_match=true`.
- SGLang launch evidence: process command used staged model, served model
  `qwen3-30b-a3b-instruct-2507-staged`, port `13000`, TP=8 H200, and
  `--reasoning-parser qwen3`.
- Endpoint smoke: PASS, HTTP `200`, content `OK`, `reasoning_content=null`,
  `max_tokens=8`, no benchmark prompt, and
  `chat_template_kwargs={enable_thinking:false, truncate_history_thinking:false}`.
- Direct math smoke command:

```bash
/work-agents/.venv/bin/python /mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/eval/direct_corrected_math_live_smoke_with_kwargs_wrapper.py --aime-score-cache /work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/aime_score_cache.db --hmmt-output-jsonl /work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/hmmt_output.jsonl --output-dir /mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/eval/direct_corrected_math_live_smoke_with_kwargs --endpoint-url http://10.100.2.62:13000/v1/chat/completions --model-id qwen3-30b-a3b-instruct-2507-staged --aime-limit-rows 1 --hmmt-limit-rows 1 --parallelism 1 --timeout 900
```

- Direct math result: PASS, 2/2 status `ok`, content non-null 2/2,
  reasoning content non-null 0/2, AIME parsed/correct 1/1, HMMT parsed/correct
  1/1, runtime 37.736 seconds.
- Cleanup: task210 report records SGLang stopped after smoke runs and final
  verification showed no `:13000` listener, no SGLang processes, and all
  8 H200s idle.
- Key artifacts:
  `task210_session4_evidence_summary.md/json`,
  `copy/manifest_compare_result.log`,
  `nemtron_artifact_copies/chat_smoke_with_kwargs_sanitized.json`,
  `eval/direct_corrected_math_live_smoke_with_kwargs_command.txt`,
  `eval/direct_corrected_math_live_smoke_with_kwargs/summary.json`,
  `eval/direct_corrected_math_live_smoke_with_kwargs/results.jsonl`, and
  `nemtron_artifact_copies/final_cleanup_verification_after_with_kwargs.log`.
- Residual risk: full 27-target benchmark was not run and remains held without
  fresh PM approval.

### task218: contained causal-conv1d train-stack unblock PASS

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
- Built package: `causal-conv1d==1.6.2.post1` on NemTron against Python
  3.12.3, torch `2.9.1+cu129`, CUDA 12.9, triton 3.5.1.
- Contained install target:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task218/pip_target`
- Source/wheel/extension hashes:
  - sdist `sha256=245e314ea21064ded7a5bf6b3b842b644aa6f92e45cecfe3e935629744c35ff4`
  - wheel `sha256=347a4cf7d1b629162ce891cda40bdf5c20e1fa1da81ccc2e78467828e8f5ce6e`
  - installed extension
    `sha256=b9b896d914d4dc90284863335bbc10a93099c2c49cdd969c0e57dcbded9e3497`
- Required next-train `PYTHONPATH` prefix:

```bash
/mnt/cephfs/data/processing/nemotron-live-validation/task218/pip_target:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target:/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv/lib/python3.12/site-packages:<src>
```

- Probes: `TASK218_IMPORT_FUNCTION_PROBE_PASS`,
  `TASK218_TINY_CUDA_SMOKE_PASS`, `TASK218_CONTAINMENT_PROBE_PASS`.
- Residual risk: task218 intentionally did not launch training; it only proved
  contained dependency availability and callable causal-conv1d functions for
  the train stack.

### task219: single-GPU one-iteration SFT PASS

- Owner: `intern_nem_dev_2`
- Branch/head:
  `intern_nem_dev_2/task219_qwen_sft_one_iter_post_task218_live_s1` /
  verified head `9b1a0640d9daca9ab89704ba6ab383e38c6da869`
- Base/product commit:
  `1d037329f5a02cdc04f2a09a16e7342721be4c87`
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task219`
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
  `1`, loss `1.195105E+01`, skipped/nan `0/0`, checkpoint saved.
- Checkpoint path:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1/checkpoints_one_iter`
- Checkpoint evidence: `iter_0000001`, latest iteration `1`, size `1.2G`,
  hashes recorded in
  `/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1/logs/04_checkpoint_gpu_state_after_run.log`.
- Cleanup: PM/test verification reports no H200 compute apps, `:13000` and
  `:29581` clear, and `:8000` documented/untouched.
- Residual risk: validates canonical single-GPU one-iteration training and
  checkpoint save only. It does not prove 8-GPU distributed behavior, longer
  train stability, full-data throughput, checkpoint conversion, serving a
  trained checkpoint, or benchmark quality.

### task220: 8-GPU full-data one-iter PENDING

- Owner: `intern_nem_dev_2`
- Branch:
  `intern_nem_dev_2/task220_qwen_sft_8gpu_full_data_one_iter_live_s1`
- Local branch/base observed by task222:
  `1d037329f5a02cdc04f2a09a16e7342721be4c87`
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220`
- Existing staging evidence:
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/logs/00_full_data_staging.log`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/logs/01_code_config_stage.log`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/m1_agentic_8gpu_full_qwen30b_contract.yaml`
- Full-data stage command:

```bash
(cd "$SRC" && tar --dereference -cf - blend.json splits) | ssh -o BatchMode=yes NemTron "rm -rf /mnt/cephfs/data/processing/nemotron-live-validation/task220/input_task208_full && mkdir -p /mnt/cephfs/data/processing/nemotron-live-validation/task220/input_task208_full && tar -C /mnt/cephfs/data/processing/nemotron-live-validation/task220/input_task208_full -xf - && ..."
```

- Staging result: PASS, `staging_rc=0`; remote inventory and hashes match the
  task208 full split files under
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220/input_task208_full/splits`.
- Code/config staging result: PASS, `code_stage_rc=0`, `config_stage_rc=0`,
  remote code marker `1d037329f5a02cdc04f2a09a16e7342721be4c87`, and config
  SHA-256
  `3114416101d87ef3a3b106da521fd7ac39b1bde5cc2f95f39b1b884a4a8cb048`.
- Pending proof: no existing report/log read for task222 showed the 8-H200
  `torchrun` launch, pass/fail result, checkpoint, or cleanup evidence.

### task221: full benchmark prepare/run PENDING

- Owner: `intern_nem_dev_3`
- Branch:
  `intern_nem_dev_3/task221_qwen_eval_full_benchmark_prepare_s1`
- Local branch/base observed by task222:
  `1d037329f5a02cdc04f2a09a16e7342721be4c87`
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task221`
- Existing readiness artifacts:
  - `readiness/local_model_visibility.log`
  - `readiness/nemtron_staged_model_visibility.log`
  - `readiness/launcher_runtime_availability.log`
- Model visibility:
  - local stable model path
    `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`
    is visible locally with 16 shards.
  - task210 staged model path is reported visible on NemTron with 16 shards
    and essential files present.
  - task210 staged model path is not visible from the local CPU mount.
- Launcher readiness:
  `python_module_nemo_evaluator_launcher_available=false` with
  `ModuleNotFoundError: No module named 'nemo_evaluator_launcher'`.
- Pending proof: task221 is prepare-only by PM instruction and had no endpoint,
  eval, benchmark, or H200-consuming run in the evidence read for task222.

## Namespace and Model Notes

- Canonical stable Qwen model/tokenizer path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Endpoint smoke used the task210 NemTron-visible staged model path:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/staged_model/Qwen3-30B-A3B-Instruct-2507`.
- Task208 full packing output is locally visible at the corrected root, but
  PM observed that NemTron could not see those CPU-created artifacts under the
  same `/mnt/cephfs/data/processing` path.
- Task209/task219 used staged sample splits at:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4/splits`.
- Task220 staged full splits at:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220/input_task208_full/splits`.
- Task219 checkpoint is visible from NemTron and verified by read-only
  inspection, while the local CPU manifest records checkpoint visibility as
  `MISSING`; local-visible logs preserve checkpoint inventory/hash evidence.
- Task218 also encountered CPU/NemTron namespace differences for staged source
  artifacts and used tar-over-SSH into task-owned paths.

## Remaining Proof Gaps

- Run and verify task220 8-H200 distributed one-iteration SFT on the full
  task208 packed data, including loss, checkpoint, and cleanup evidence.
- Measure full-data distributed throughput from task220 before projecting full
  SFT duration with confidence.
- Prove longer-run SFT stability, checkpoint cadence, resume behavior, and any
  full-train completion criteria PM defines.
- If required by the pipeline, prove checkpoint conversion/export and serving
  from a trained checkpoint, not only base-model endpoint smoke.
- Run task221 full benchmark path after PM release, including endpoint
  availability, target coverage, parsers, artifact capture, and cleanup.
- Establish quality metrics and any W&B/artifact-publication steps only if PM
  explicitly authorizes those live surfaces.

## Estimates

- Next 8-GPU one-iteration gate: task220 staging already exists; the remaining
  gate is the single authorized distributed smoke plus validation/log
  collection. Prior PM estimates and task219 timing suggest a planning range of
  roughly 20-45 minutes once H200s are released and no new dependency/runtime
  blocker appears.
- Full Qwen SFT: not reliably estimable from the current evidence alone. The
  packed dataset contains `672687706` tokens and `987770` packed sequences, but
  only one single-GPU iteration has passed. Prior planning estimates remain
  12-36 wall-clock hours on the intended multi-GPU allocation plus queue time;
  this should be recalculated from task220 full-data 8-GPU throughput.
- Full benchmark: prior eval planning identifies 27 target IDs total
  (19 M1 plus 8 M2), with 14 M1 IDs currently launcher-available and M2
  config-only. Stage3 eval walltime is configured as `04:00:00` per job; a
  corrected-math / M1-available / M2-config split implies at least 12 hours of
  scheduler allocation before endpoint throughput, asset, and launcher/runtime
  blockers are considered. Task210 ran only a 2-request direct math smoke in
  37.736 seconds and does not bound the full benchmark.

## Sources Read

- `/work-agents/intern_nem_dev_1/report.md`
- `/work-agents/intern_nem_dev_3/report.md`
- `/work-agents/intern_nem_pm/report.md`
- `/mnt/cephfs/data/processing/nemotron-live-validation/task208/logs/*`
- `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/*`
- `/mnt/cephfs/data/processing/nemotron-live-validation/task218/validation_report.md`
- `/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1/logs/*`
- `/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/logs/*`
- `/mnt/cephfs/data/processing/nemotron-live-validation/task221/readiness/*`

## task222 Validation

- `git diff --check`: passed before commit.
- `git diff --cached --check`: passed before commit.
- Product-code edits: none.
- Live operations by task222: none.
