# task210_nemtron_vpn_endpoint_eval_live_s1

<!-- METADATA:STATUS=ReadyForPMReview,ASSIGNEE=intern_nem_dev_3,SESSION=5 -->

## Scope

- Evidence-only NemTron/vpn endpoint live-path validation.
- Discover available serving runtime on NemTron without downloads.
- Use vpn only for image/build staging evidence because vpn lacks the cephfs
  Qwen model path.
- Coordinate with dev_2 before heavy H200 serving.
- Start Qwen endpoint and run one minimal sanitized chat request only if GPUs
  are released and serving is feasible.

## Boundaries

- No package/model download on NemTron.
- No full benchmark until endpoint smoke passes.
- No benchmark prompts in live request.
- No training, W&B/cluster deploy, artifact upload, direct `main`/`master`
  push, or self-merge.

## Status

- Baseline SHA: `0460c1f0262875fb27ae530d30cd80d805752851`
- Branch: `intern_nem_dev_3/task210_nemtron_vpn_endpoint_eval_live_s1`
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task210`
- Evidence:
  - NemTron: 8 H200 visible; Qwen model path visible; SGLang 0.5.8 import OK;
    vLLM and TensorRT-LLM imports missing
  - vpn: Docker 29.1.3 available; Qwen cephfs model path missing
  - dev_2 coordination: heavy NemTron GPUs not released because task209 owns
    H200 training/preflight use
  - Endpoint smoke -> skipped; no server started and no live request made
  - Corrected math dry-run -> passed; runtime
    `real 2.252 user 8.953 sys 0.353`
  - Qwen/M1/M2 validator shard -> 136 passed, 8 warnings; runtime
    `real 4.252 user 3.973 sys 0.276`
  - Structured evidence summary:
    `/mnt/cephfs/data/processing/nemotron-live-validation/task210/task210_evidence_summary.md`
  - Structured evidence JSON:
    `/mnt/cephfs/data/processing/nemotron-live-validation/task210/task210_evidence_summary.json`
  - `git diff --check` -> passed
  - `git diff --cached --check` -> passed

## Session 4 Staged Endpoint Smoke

- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4`
- PM-authorized staged model path:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/staged_model/Qwen3-30B-A3B-Instruct-2507`
- Staging result: PASS. Copy exit `0`; destination has 16 safetensor shards;
  file-size manifest match `true`; small-file SHA256 match `true`.
- SGLang relaunch result: PASS from the staged model path.
  - PID: `1430020`
  - Port: `13000`
  - Served model: `qwen3-30b-a3b-instruct-2507-staged`
  - Tensor parallel: 8 H200 GPUs
- Corrected sanitized `/v1/chat/completions` smoke result: PASS.
  - Request used `max_tokens=8`, no benchmark prompt, and
    `chat_template_kwargs={enable_thinking:false, truncate_history_thinking:false}`.
  - HTTP `200`; `message.content` was non-null (`OK`);
    `message.reasoning_content` was null; usage was 12 prompt, 2 completion,
    14 total tokens.
- Corrected direct math smoke result: PASS with the same
  `chat_template_kwargs`, using an artifact-local wrapper and 1 AIME + 1 HMMT
  sample.
  - Total requests: 2
  - Status: 2/2 `ok`
  - Content: 2/2 non-null, 0 null
  - AIME: parsed 1/1, correct 1/1
  - HMMT: parsed 1/1, correct 1/1
  - Runtime: 37.736 seconds in the runner summary
- Full 27-target benchmark: held; not run without fresh PM approval.
- Cleanup: PASS. SGLang was stopped after the smoke runs; final verification
  shows no `:13000` listener, no SGLang processes, and all 8 H200s idle at
  1 MiB used / 0% utilization.
- Session 4 evidence summary:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/task210_session4_evidence_summary.md`
- Key artifacts:
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/copy/manifest_compare_result.log`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/nemtron/session4_sglang_relaunch_command.txt`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/nemtron/session4_relaunch_ready_state.log`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/endpoint_smoke/session4_chat_smoke_with_kwargs_sanitized.json`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/eval/direct_corrected_math_live_smoke_with_kwargs_command.txt`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/eval/direct_corrected_math_live_smoke_with_kwargs/summary.json`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/eval/direct_corrected_math_live_smoke_with_kwargs/results.jsonl`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/gpu/final_cleanup_verification_after_with_kwargs.log`

## Session 3 Live Continuation

- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session3`
- Prelaunch state: NemTron had no compute apps, no `:13000` listener, and 8
  H200 GPUs idle at 1 MiB used / 0% utilization.
- Launch attempted with SGLang PID `1359959` on port `13000`, GPUs `0-7`,
  `tensor_parallel_size=8`, model path
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Launch failed before readiness: SGLang exited while loading weights with
  `RuntimeError: Cannot find any model weights with` the requested model path.
- Model-path blocker: NemTron sees config/tokenizer files and
  `model.safetensors.index.json`, but no `model-000xx-of-00016.safetensors`
  shards. The local CPU view of the same path has all 16 safetensor shards.
- Endpoint smoke -> not run because no endpoint became ready.
- Corrected math live eval and launcher-available M1 subset -> not run because
  endpoint smoke did not pass.
- Cleanup state: no SGLang process, no port `13000` listener, no compute apps,
  all 8 H200s back to 1 MiB used / 0% utilization.
- Session 3 evidence summary:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session3/task210_session3_evidence_summary.md`
