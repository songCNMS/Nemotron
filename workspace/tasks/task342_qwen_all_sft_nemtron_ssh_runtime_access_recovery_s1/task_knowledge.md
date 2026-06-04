# task342_qwen_all_sft_nemtron_ssh_runtime_access_recovery_s1 - task knowledge

<!-- METADATA:STATUS=Blocked,ASSIGNEE=intern_nemotron_worker_4,SESSION=91 -->

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
5. Worker_4 accepted task342 at branch head
   `7575dc2226789901356d99dabdc2ca0114d3b60a`, based on `origin/main`
   `371aea491776cc258e1cbb59a081d28be0530438`.
6. #405/task342 exact head `22dd5187d6bb552e031646925bba59f79ed00732`
   reports `BLOCK_NEMTRON_ACCESS`: proxy hop works, but proxy-side TCP to
   `10.100.2.62:33808` is refused and `ssh NemTron` returns rc `255`. This
   confirms the blocker is target host/port/service or LTP target route, not
   local alias parse, DNS, or proxy-hop auth by current evidence.
7. A task342 merge would close blocker docs only. It must not be interpreted as
   restored access, a task341 rerun release, or task310 training/eval
   authorization.
8. Lead gate was posted as PR comment `4622313805` because GitHub rejected
   formal same-author approval. Worker_4 may self-merge #405 only if exact head
   `22dd5187d6bb552e031646925bba59f79ed00732` remains `CLEAN`.
9. #405 merged at `2026-06-04T12:53:46Z` with merge commit
   `3baff1a3e3de84852d8361a11a81917d4256d3f1` from exact head
   `22dd5187d6bb552e031646925bba59f79ed00732`. Merged evidence remains
   `BLOCK_NEMTRON_ACCESS`, not restored access.
10. Worker_4 merge closeout mailbox
   `intern_nemotron_worker_4-task342-merge-closeout-20260604T1254Z` confirms no
   issues or boundary violations after #405 merge.
