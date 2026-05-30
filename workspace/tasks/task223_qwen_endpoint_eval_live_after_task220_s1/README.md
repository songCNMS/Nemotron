# task223_qwen_endpoint_eval_live_after_task220_s1

Owner: `intern_nem_dev_3`

Status: complete; endpoint/eval smoke passed, M1/full benchmark held.

Base/product commit: `1d037329f5a02cdc04f2a09a16e7342721be4c87`

Branch: `intern_nem_dev_3/task223_qwen_endpoint_eval_live_after_task220_s1`

Artifact root: `/mnt/cephfs/data/processing/nemotron-live-validation/task223`

## Scope

Ran the eval-side live continuation from task221 prepared artifacts after task220 PASS/H200 cleanup. Used the task210 staged Qwen model path on NemTron:

`/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/staged_model/Qwen3-30B-A3B-Instruct-2507`

## Evidence

- Validation report: `/mnt/cephfs/data/processing/nemotron-live-validation/task223/validation_report.md`
- Preflight: `/mnt/cephfs/data/processing/nemotron-live-validation/task223/preflight/nemtron_preflight.log`
- Endpoint readiness: `/mnt/cephfs/data/processing/nemotron-live-validation/task223/endpoint/sglang_readiness_openai.log`
- Sanitized smoke: `/mnt/cephfs/data/processing/nemotron-live-validation/task223/remote_copies/endpoint_smoke/sanitized_endpoint_smoke_sanitized.json`
- Corrected math smoke: `/mnt/cephfs/data/processing/nemotron-live-validation/task223/eval/direct_corrected_math_live_smoke_with_kwargs/summary.json`
- Cleanup verification: `/mnt/cephfs/data/processing/nemotron-live-validation/task223/cleanup/final_cleanup_verification.log`

## Results

- Preflight: PASS. No task220/Qwen/torchrun/SGLang processes, no `:13000` listener, no H200 compute apps, 8 H200s visible, staged model visible with 16 shards and required files. `:8000` was present and left untouched.
- SGLang endpoint: PASS. Launched one task223-owned endpoint on `:13000` with TP=8, context 16384, served model `qwen3-30b-a3b-instruct-2507-staged`, and `--reasoning-parser qwen3`.
- Sanitized endpoint smoke: PASS. HTTP 200, content `OK`, non-null message content, no benchmark prompt, no secrets.
- Corrected math live smoke: PASS via the validated task210 direct wrapper fallback. AIME 1/1 parsed/correct and HMMT 1/1 parsed/correct.
- M1 launcher-available subset: HOLD/not run because the official `nemo_evaluator_launcher` runtime is unavailable in local `/work-agents/.venv`.
- Full 27-target benchmark: HOLD/not run pending fresh PM release and remaining M1/M2 blockers.
- Cleanup: PASS. No SGLang processes, no `:13000` listener, no H200 compute apps, all H200s idle.

## Notes

- Official eval runtime check returned `OFFICIAL_EVAL_RUNTIME_BLOCKED` with `ModuleNotFoundError: No module named 'nemo_evaluator_launcher'`.
- A local CPU-created command/request file was not visible on NemTron; the same command/request was written into the NemTron-visible task223 artifact path before the actual successful endpoint launch/smoke.
- Cleanup required TERM to the task223 wrapper PID and then TERM to the verified task223-owned SGLang child PID.
