# task342_qwen_all_sft_nemtron_ssh_runtime_access_recovery_s1 - task knowledge

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_4,SESSION=91 -->

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
