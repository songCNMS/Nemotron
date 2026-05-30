# intern_nem_dev_2 - 状态

<!-- METADATA:STATUS=Idle,TASK=none,ROLE=independent -->

| 字段 | 值 |
|------|-----|
| Name | intern_nem_dev_2 |
| Status | Idle |
| Current Task | None |
| PR | evidence-only branch |
| Session | 2 |

最近进展：Completed released task219 one-iteration Qwen-contract SFT smoke on
branch `intern_nem_dev_2/task219_qwen_sft_one_iter_post_task218_live_s1` from
baseline `1d037329f5a02cdc04f2a09a16e7342721be4c87`. Staged task-owned
code/config/commit marker under
`/mnt/cephfs/data/processing/nemotron-live-validation/task219`, re-ran
preflight with no SGLang/task210 process, no `:13000`, no H200 compute apps,
free master port `29581`, and `:8000` documented/untouched. Launched exactly
one torchrun with task218 `pip_target` first in `PYTHONPATH`; it passed with
`task219_torchrun_rc=0`, iteration `1/1`, `lm loss: 1.195105E+01`, skipped/nan
`0/0`, and saved an iteration-1 checkpoint. NemTron checkpoint path exists at
`/mnt/cephfs/data/processing/nemotron-live-validation/task219/session1/checkpoints_one_iter`
with size `1.2G`; local CPU namespace does not see the checkpoint directory, so
local-visible log `04_checkpoint_gpu_state_after_run.log` records full
inventory and sha256 evidence. Post-run cleanup passed and no second run or
workaround was attempted. Dev_2 is Idle / Current Task None.
