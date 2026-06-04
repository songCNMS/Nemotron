# task342_qwen_all_sft_nemtron_ssh_runtime_access_recovery_s1 - task knowledge

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_4,SESSION=91 -->

1. #404/task341 merged blocker evidence at `2026-06-04T12:34:36Z`, merge
   commit `371aea491776cc258e1cbb59a081d28be0530438`.
2. The concrete blocker is `ssh NemTron` returning rc `255` with
   `channel 0: open failed: connect failed: Connection refused`.
3. Passing this task does not authorize training. It only restores the access
   precondition needed to rerun task341 or an equivalent no-training checkpoint
   handoff.
4. The critical remote paths to check, if SSH works, are task337 runtime target,
   task298 checkpoint candidate, and task339 train-only data root listed in the
   README.
5. Worker_4 accepted on branch
   `intern_nemotron_worker_4/task342_qwen_all_sft_nemtron_ssh_runtime_access_recovery_s1`
   from `origin/main` `371aea491776cc258e1cbb59a081d28be0530438`; lead docs
   were imported from
   `origin/intern_nemotron_lead/session1-recovery-task-docs`
   `c7a417d11cde7935be6f7abdc463426504dfbd33`.
6. Worker_4 disposition is `BLOCK_NEMTRON_ACCESS`. `ssh NemTron` still fails
   with rc `255`, while the proxy hop is reachable and proxy-side `/dev/tcp`
   to target `10.100.2.62:33808` returns connection refused.
   Review PR: #405 `https://github.com/songCNMS/Nemotron/pull/405`.
7. Because the route does not reach the target, `/root`, task337 runtime target,
   task298 checkpoint candidate, task339 train-only root, and runtime imports
   were not testable.
