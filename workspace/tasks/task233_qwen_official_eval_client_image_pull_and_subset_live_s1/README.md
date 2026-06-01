# task233_qwen_official_eval_client_image_pull_and_subset_live_s1

<!-- METADATA:STATUS=Done,ASSIGNEE=intern_nem_dev_2,SESSION=2 -->

## Scope

- Pull exactly the 11 task230-approved `nvcr.io/nvidia/eval-factory/*:26.03`
  evaluator client images on VPN.
- Inspect and record image IDs, repo digests, sizes, and created times.
- Start exactly one task233-owned SGLang endpoint on NemTron using the staged
  Qwen model, with a bounded task233-owned VPN reverse tunnel only because VPN
  could not reach NemTron `:13000` directly.
- Run the official corrected-math smoke and then the 14 M1
  launcher-available subset through the task225-approved evaluator runtime.
- Stop after the PM cleanup directive and finalize partial evidence.

## Boundaries

- No extra Docker image refs, `latest` refs, builds, package installs, model
  copy, env mutation, W&B, cluster/deploy, artifact upload, product code edits,
  direct `main`/`master` push, or self-merge.
- No model/deployment Docker container or second endpoint.
- After the cleanup directive, no further endpoint/eval/benchmark runs were
  started.
- Pulled evaluator images were retained on VPN for reproducibility; no Docker
  image deletion, purge, prune, or unrelated process kill was performed.

## Status

- Final result: partial failed/held after supervisor selected Cleanup now.
- Base/product commit: `1d037329f5a02cdc04f2a09a16e7342721be4c87`.
- Branch:
  `intern_nem_dev_2/task233_qwen_official_eval_client_image_pull_and_subset_live_s1`.
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233`.
- Image pull/inspect: PASS, exactly 11 allowlisted refs pulled and inspected.
- Preflight: PASS on local, VPN, and NemTron; `:8000` documented and
  untouched.
- Endpoint: exactly one task233 SGLang endpoint launched on NemTron
  PID `2354311`; `/health` and `/v1/models` passed.
- Tunnel: task233 reverse tunnel exposed VPN `127.0.0.1:13128` to the
  NemTron endpoint; tunnel `/health` and `/v1/models` passed.
- Sanitized endpoint smoke: PASS with exact content `OK`.
- Corrected-math official smoke: PASS for `simple_evals.AIME_2025` and
  `nemo_skills.ns_hmmt_feb2025`.
- M1 launcher-available subset: partial failed/held at cleanup decision:
  3 success, 9 failed, 1 stopped/partial, 1 not run/held.
- Cleanup: PASS. Task233 evaluator jobs 12/13 were killed, the task233 tunnel
  was stopped, the task233 SGLang process tree was stopped, `:13000` and the
  VPN tunnel port were clear, no task233 H200 compute apps remained, and
  `:8000` remained untouched.

## M1 Subset Results At Cleanup

| Target | Result | Notes |
| --- | --- | --- |
| `lm-evaluation-harness.mmlu_pro.0` | PASS | Stage exit `0`. |
| `simple_evals.AIME_2025.1` | FAIL | HTTP 400 client/endpoint route error. |
| `nemo_skills.ns_hmmt_feb2025.2` | PASS | Stage exit `0`. |
| `simple_evals.gpqa_diamond.3` | FAIL | Gated HF dataset auth. |
| `hle.hle.4` | FAIL | Gated HF dataset auth. |
| `livecodebench.codegeneration_release_latest.5` | FAIL | Container exited `1`; see failure summary and copied logs. |
| `scicode.scicode.6` | PASS | Stage exit `0`. |
| `ifbench.ifbench.7` | FAIL | Missing `pkg_resources` in evaluator image/runtime. |
| `ruler.ruler-256k-chat.8` | FAIL | Missing tokenizer path/config. |
| `AA-LCR.aa_lcr.9` | FAIL | Inputs exceeded 16k endpoint context. |
| `tau2_bench.tau2_bench_airline.10` | FAIL | External/OpenAI auth `401`. |
| `bfcl.bfclv3.11` | FAIL | Missing API keys. |
| `lm-evaluation-harness.mmlu_prox_chat.12` | STOPPED/PARTIAL | Killed by PM cleanup directive at about `10420/11759`. |
| `nemo_skills.ns_wmt24pp.13` | HELD/NOT RUN | Pending at cleanup; launcher kill marked the pending job killed. |

## Key Artifacts

- Allowlist:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/images/allowlist_images.txt`.
- Source allowlist provenance:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/images/task230_source_artifacts.sha256`.
- Pull log:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/vpn_copied_artifacts/images/02_vpn_pull_allowlist.log`.
- Final retained image inventory:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/images/final_retained_image_inventory.log`.
- Endpoint command:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/commands/sglang_endpoint_command.sh`.
- Corrected-math command:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/commands/vpn_corrected_math_official_smoke.sh`.
- M1 subset command:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/commands/vpn_m1_launcher_available_14.sh`.
- Failure summary:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/failure_summaries/failed_targets_summary_20260531T052143Z.md`.
- Copied eval artifacts:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/vpn_copied_artifacts/eval/`.
- Copied eval manifest and hashes:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/vpn_copied_artifacts/eval/final_eval_copied_manifest.txt`,
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/vpn_copied_artifacts/eval/final_eval_copied_files.sha256`.
- Cleanup logs:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/cleanup/02_vpn_evaluator_kill.log`,
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/cleanup/07_stop_task233_tunnel.log`,
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/cleanup/08_stop_task233_sglang.log`,
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/cleanup/11_final_precise_cleanup_verify.log`,
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/cleanup/13_final_local_tunnel_ps_c_verify.log`.

## Residual Risk

- The official M1 subset result is partial because PM directed cleanup before
  `mmlu_prox_chat` completed and before `ns_wmt24pp` started.
- Several failures are evaluator/runtime/config/auth issues rather than model
  quality signals. A rerun after targeted fixes should expect at least a
  day-scale wall clock if `mmlu_prox_chat` remains in scope.
