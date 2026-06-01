# Validation Report

<!-- METADATA:SESSION=1 -->

## Summary

Status: triage complete; next live eval remains HOLD pending PM release and
targeted fixes/resources. This task converted task233's verified partial
failed/held M1 subset evidence into a PM-ready fix/resource/release plan.

No live eval, endpoint, SGLang, Docker run/pull/build, package
install/build/download, environment mutation, model copy, process kill, image
delete/prune, artifact upload, product code edit, main/master push, or
self-merge was performed for task234. Task233's pulled evaluator images were
left untouched.

## Source Evidence

- Product/base commit:
  `1d037329f5a02cdc04f2a09a16e7342721be4c87`.
- Source task233 verified branch/head:
  `intern_nem_dev_2/task233_qwen_official_eval_client_image_pull_and_subset_live_s1`
  at `ba6636d1f365d5e94641d675ec3d743ed485d7f7`.
- Source artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233`.
- Task233 failure summary:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/failure_summaries/failed_targets_summary_20260531T052143Z.md`.
- Task233 M1 copied eval root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/vpn_copied_artifacts/eval/m1_launcher_available_14/20260530_171752-5e3f10e5af8917d7`.
- Task233 corrected-math copied eval root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/vpn_copied_artifacts/eval/corrected_math_official_smoke/20260530_170910-ecedfe2ecb91fa99`.
- Task234 artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task234`.
- Structured matrix:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task234/triage_matrix.json`.

## Non-Pass Triage

| Target | Classification | Evidence marker | Proposed next action |
| --- | --- | --- | --- |
| `simple_evals.AIME_2025.1` | Product config bug / endpoint capacity blocker | HTTP 400: requested `16660` tokens against `16384` context because subset used `max_new_tokens: 16384`; corrected-math PASS used `max_new_tokens: 8192`, `parallelism: 1`, `limit_samples: 1`. | Cap AIME `max_new_tokens` to `8192` or residual-budget aware value, then rerun a target-scoped smoke. |
| `simple_evals.gpqa_diamond.3` | Credential-resource blocker | `Dataset 'Idavidrein/gpqa' is a gated dataset on the Hub.` | Provide approved HF token with GPQA access or a mounted approved dataset cache. |
| `hle.hle.4` | Credential-resource blocker | `Dataset 'cais/hle' is a gated dataset on the Hub.` | Provide approved HF token with HLE access or a mounted approved dataset cache. |
| `livecodebench.codegeneration_release_latest.5` | Evaluator runtime/resource blocker | `Killed livecodebench ...`; subprocess return code `137` after generating the release_latest test split. | Run a reduced LiveCodeBench smoke or approve larger memory/container resources before full `release_latest`. |
| `ifbench.ifbench.7` | Evaluator runtime gap | `ModuleNotFoundError: No module named 'pkg_resources'` via `syllapy.data_loader`. | Release an official image fix or approved offline overlay with `setuptools`/`pkg_resources`, then import-probe before live eval. |
| `ruler.ruler-256k-chat.8` | Product eval config bug | Command used `--tokenizer_path "None"`; data prep raised tokenizer path/config requirement. | Set `config.params.extra.tokenizer` to a container-visible Qwen tokenizer path and add the needed mount/staging. |
| `AA-LCR.aa_lcr.9` | Endpoint capacity blocker | Inputs of about `102k` to `118k` tokens exceeded the `16384` endpoint context. | HOLD on the 16k endpoint; choose an official shorter/truncated variant or validate a >=128k context endpoint first. |
| `tau2_bench.tau2_bench_airline.10` | Credential-resource blocker | External user simulator `openai/nvdev/qwen/qwen-235b` returned `401 Unauthorized`. | Provide approved NVIDIA Integrate `USER_API_KEY` and any required judge key. |
| `bfcl.bfclv3.11` | Credential-resource blocker | `NoAPIKeyError: Please fill in the API keys in the .env file.` | Provide BFCL executable-category API keys through secure task-owned injection, or approve a non-executable subset. |
| `lm-evaluation-harness.mmlu_prox_chat.12` | Scheduling blocker | PM cleanup killed it with stage exit `137` after about `10420/11759` progress; metrics show `57400` successful HTTP 200 responses. | Run separately with timeout above 30h or split/shard if supported. |
| `nemo_skills.ns_wmt24pp.13` | Scheduling blocker / unknown until run | Pending job was killed before execution; `client_stdout.log` is empty. | Release separately after scheduling/assets/credentials preflight and after `mmlu_prox_chat` no longer blocks the sequence. |

## PM-Ready Priorities

1. Offline/config fixes that can be prepared without live resources:
   AIME token budget cap, RULER tokenizer path/mount, IFBench image/runtime
   fix proposal, and a LiveCodeBench reduced-smoke/resource-sized plan.
2. Resource requests:
   HF gated dataset access/cache for GPQA and HLE, NVIDIA Integrate
   user-simulator credentials for tau2, and BFCL executable API keys.
3. HOLD decisions:
   AA-LCR requires endpoint capacity or official shorter variant;
   `mmlu_prox_chat` needs a separate long window or shard/resume plan;
   `ns_wmt24pp` should not be released until it has its own window and asset
   preflight.

## Minimal Release Commands

These are proposed future command shapes only; none were run in task234.

- For target-scoped config fixes:
  `nemo-evaluator-launcher run --config <task_root>/eval_configs/<target>_raw.yaml --config-mode raw`.
- For credential-gated targets:
  use the same `deployment.type=none` endpoint/tunnel pattern as task233, with
  PM-approved secret injection and target-scoped output roots.
- For long/scheduling targets:
  run the target alone with a PM-approved timeout, or with a deterministic
  shard/resume plan if the evaluator supports it.

The exact per-target proposals and acceptance criteria are in
`triage_matrix.json`.

## Cleanup State

- Task234 started no endpoint, SGLang process, evaluator client, Docker
  container, tunnel, package operation, or model copy.
- Task233 cleanup remains the cleanup source of truth: no task233 `:13000`,
  no task233 evaluator/SGLang/Qwen compute process, no task233 H200 compute
  app, tunnel ports clear, and `:8000` documented/untouched.
- Task233 pulled evaluator images remain retained for reproducibility and were
  not inspected with mutating commands, deleted, pruned, or otherwise touched
  by task234.

## Checks

- `git diff --check`: PASS.
- `git diff --cached --check`: PASS.

## Residual Risk

- Several failures are not model-quality signals yet; they require evaluator
  config, runtime, credentials, or endpoint capacity fixes before rerun.
- `mmlu_prox_chat` dominates wall clock. Based on the task233 partial run,
  sequential completion is estimated at roughly 26-30 hours.
- `ns_wmt24pp` did not start, so its runtime/assets remain unknown until a
  separately released target-scoped run.
