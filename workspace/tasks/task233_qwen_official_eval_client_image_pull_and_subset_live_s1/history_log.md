# History Log

<!-- METADATA:SESSION=2 -->

## Session 1 - 2026-05-31

- Created branch
  `intern_nem_dev_2/task233_qwen_official_eval_client_image_pull_and_subset_live_s1`
  from base/product commit `1d037329f5a02cdc04f2a09a16e7342721be4c87`.
- Built the task233 image allowlist from task230 artifacts, recorded source
  hashes, and verified the list was exactly 11 refs under
  `nvcr.io/nvidia/eval-factory/*:26.03`.
- Pulled exactly the 11 approved evaluator client images on VPN using existing
  Docker/NGC credentials. No `latest` refs, extra image refs, Docker build, or
  package install was run.
- Inspected all 11 images after pull and recorded IDs, repo digests, sizes, and
  created times.
- Ran local/VPN/NemTron preflight. VPN direct access to NemTron `:13000`
  timed out, so a bounded reverse tunnel was required. Existing `:8000` was
  documented and left untouched.
- Launched exactly one task233-owned SGLang endpoint on NemTron using the
  staged Qwen model and TP=8. Readiness passed via local `/health` and
  `/v1/models`.
- Created task233 reverse tunnel on VPN `127.0.0.1:13128`; tunnel `/health`
  and `/v1/models` probes passed.
- Ran sanitized endpoint smoke through the VPN tunnel. Response content was
  exactly `OK` and no secret markers were detected.
- Staged an exact tracked source snapshot at product commit
  `1d037329f5a02cdc04f2a09a16e7342721be4c87` to VPN task-owned code path
  because the existing VPN checkout was not at the required commit. No package
  install or external download was performed.
- Ran official corrected-math smoke through `nemo-evaluator-launcher==0.2.5`
  with `deployment.type=none` and task225-approved runtime. Both
  `simple_evals.AIME_2025` and `nemo_skills.ns_hmmt_feb2025` exited `0`.
- Prepared and dry-ran the 14-target M1 launcher-available raw config. Dry-run
  generated evaluator client containers only, all using the 11 approved
  `eval-factory:26.03` images and no deployment/server image.
- Started the official 14-target M1 launcher-available subset.

## Session 2 - 2026-06-01

- Continued from the running task233-owned SGLang endpoint and running M1
  subset after compaction.
- Captured cleanup-decision state: 3 completed successes, 9 completed failures,
  `lm-evaluation-harness.mmlu_prox_chat.12` still running at about
  `10420/11759`, and `nemo_skills.ns_wmt24pp.13` still pending.
- Followed PM cleanup directive and did not start any further endpoint, eval,
  benchmark, Docker pull, package install/build/download, model copy, env
  mutation, W&B/cluster/deploy, artifact upload, main/master push, or
  self-merge.
- Ran `nemo-evaluator-launcher kill 5e3f10e5af8917d7` on VPN. Completed and
  failed jobs stayed in their terminal states; jobs 12 and 13 were killed.
- Verified no running task233/eval-factory evaluator containers remained on
  VPN.
- Stopped the task233-owned reverse tunnel via control socket
  `/tmp/task233_vpn_reverse_tunnel_mux.sock` and verified VPN port `13128`
  was clear.
- Stopped the task233-owned SGLang process tree rooted at PID `2354311` on
  NemTron and verified `:13000` was clear, no task233 SGLang/Qwen process
  remained, and no H200 compute apps remained.
- Verified `:8000` remained documented-only and untouched.
- Copied non-secret VPN eval artifacts to the shared task root, excluding
  `.secrets.env`, and recorded a 1,150-file manifest plus SHA256 hashes.
- Recorded final retained image inventory for all 11 approved evaluator images
  and left the images on VPN for reproducibility.
