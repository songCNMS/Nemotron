# Validation Report

<!-- METADATA:SESSION=2 -->

## Summary

Status: partial failed/held after PM cleanup directive. Image unblock,
endpoint launch, tunnel, sanitized smoke, and corrected-math official smoke
passed. The 14-target M1 launcher-available subset produced 3 successes,
9 failures, 1 stopped/partial target, and 1 held/not-run target before cleanup.
Cleanup completed for task233-owned resources only.

## Base

- Product commit: `1d037329f5a02cdc04f2a09a16e7342721be4c87`.
- Branch:
  `intern_nem_dev_2/task233_qwen_official_eval_client_image_pull_and_subset_live_s1`.
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233`.

## Commands And Evidence

- Image allowlist validation:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/images/allowlist_validation.txt`.
- VPN pull command:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/commands/vpn_pull_allowlist_images.sh`.
- VPN pull log:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/vpn_copied_artifacts/images/02_vpn_pull_allowlist.log`.
- Final retained image inventory:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/images/final_retained_image_inventory.log`.
- Endpoint command:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/commands/sglang_endpoint_command.sh`.
- Endpoint launch/readiness logs:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/endpoint/`.
- Tunnel launch log:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/endpoint_tunnel/01_vpn_reverse_tunnel_launch.log`.
- Sanitized smoke command:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/commands/vpn_sanitized_endpoint_smoke.sh`.
- Corrected-math command:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/commands/vpn_corrected_math_official_smoke.sh`.
- 14-target subset command:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/commands/vpn_m1_launcher_available_14.sh`.
- Cleanup-decision state:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/cleanup/01_pre_cleanup_current_status.log`.
- Evaluator cleanup:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/cleanup/02_vpn_evaluator_kill.log`,
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/cleanup/04_vpn_launcher_status_after_kill.log`.
- Tunnel cleanup:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/cleanup/07_stop_task233_tunnel.log`,
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/cleanup/13_final_local_tunnel_ps_c_verify.log`.
- Endpoint cleanup:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/cleanup/08_stop_task233_sglang.log`,
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/cleanup/11_final_precise_cleanup_verify.log`.
- Copied eval artifacts:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/vpn_copied_artifacts/eval/`.
- Copied eval manifest/hash:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/vpn_copied_artifacts/eval/final_eval_copied_manifest.txt`,
  `/mnt/cephfs/data/processing/nemotron-live-validation/task233/vpn_copied_artifacts/eval/final_eval_copied_files.sha256`.

## Phase Results

| Area | Result | Evidence |
| --- | --- | --- |
| Image allowlist | PASS | Exactly 11 approved `eval-factory:26.03` refs. |
| Image pull | PASS | VPN pull loop exited `0`; no extra refs. |
| Image inspect | PASS | 11 image IDs/repo digests recorded. |
| Preflight | PASS | No `:13000`, no H200 compute apps; `:8000` documented. |
| Endpoint | PASS | SGLang PID `2354311`, `/health` and `/v1/models` HTTP 200. |
| Tunnel | PASS | VPN `127.0.0.1:13128` health/models HTTP 200. |
| Sanitized smoke | PASS | Response content exactly `OK`. |
| Corrected math | PASS | AIME and HMMT stage exits `0`. |
| M1 14 subset | PARTIAL FAILED/HELD | 3 pass, 9 fail, 1 stopped, 1 held. |
| Cleanup | PASS | Task233 evaluator/tunnel/SGLang stopped; images retained. |

## M1 Launcher-Available Subset Results

| Target | Result | Evidence / Blocker |
| --- | --- | --- |
| `lm-evaluation-harness.mmlu_pro.0` | PASS | Stage exit `0`; copied artifacts under `vpn_copied_artifacts/eval/m1_launcher_available_14/.../lm-evaluation-harness.mmlu_pro.0`. |
| `simple_evals.AIME_2025.1` | FAIL | HTTP 400 client/endpoint route behavior. |
| `nemo_skills.ns_hmmt_feb2025.2` | PASS | Stage exit `0`. |
| `simple_evals.gpqa_diamond.3` | FAIL | Gated dataset auth for `Idavidrein/gpqa`. |
| `hle.hle.4` | FAIL | Gated dataset auth for `cais/hle`. |
| `livecodebench.codegeneration_release_latest.5` | FAIL | Container exit `1`; copied logs retained for triage. |
| `scicode.scicode.6` | PASS | Stage exit `0`. |
| `ifbench.ifbench.7` | FAIL | `ModuleNotFoundError: No module named 'pkg_resources'`. |
| `ruler.ruler-256k-chat.8` | FAIL | `tokenizer_path` / tokenizer config required. |
| `AA-LCR.aa_lcr.9` | FAIL | Inputs exceeded endpoint context length `16384`. |
| `tau2_bench.tau2_bench_airline.10` | FAIL | External/OpenAI auth `401`. |
| `bfcl.bfclv3.11` | FAIL | Missing API keys in `.env`. |
| `lm-evaluation-harness.mmlu_prox_chat.12` | STOPPED/PARTIAL | Killed by cleanup directive; last progress about `10420/11759`. |
| `nemo_skills.ns_wmt24pp.13` | HELD/NOT RUN | Pending at cleanup; launcher kill marked pending job killed. |

## Cleanup State

- Evaluator launcher kill returned `KILL_RC=0`; jobs 12 and 13 were killed,
  while completed/failed jobs stayed terminal.
- VPN Docker verification found no running task233/eval-factory/client
  containers after kill.
- Task233 tunnel stop returned `TUNNEL_STOP_RC=0`; VPN `127.0.0.1:13128`
  returned `health_code=000` after stop and the local control socket was
  absent.
- NemTron SGLang process tree rooted at PID `2354311` was terminated; final
  verification found no `:13000` listener, no task233 SGLang/Qwen process, and
  no H200 compute apps.
- The pre-existing `:8000` listener was documented and left untouched.
- The 11 pulled evaluator images remain on VPN for reproducibility; no image
  prune/delete was run.

## Checks

- `git diff --check`: PASS.
- `git diff --cached --check`: PASS after staging evidence/status docs.

## Residual Risk And Estimate

- Residual risk: the M1 subset evidence is partial by PM direction, and several
  failures require evaluator config/runtime/auth fixes before they can become
  model-quality signals.
- Estimate to rerun corrected-math plus the same 14-task subset after fixes:
  corrected-math is minutes-scale; the M1 subset is day-scale with current
  sequential launcher behavior because `mmlu_prox_chat` alone ran for about
  23 hours before cleanup and still had remaining work.
