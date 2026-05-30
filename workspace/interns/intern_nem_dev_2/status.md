# intern_nem_dev_2 - 状态

<!-- METADATA:STATUS=Idle,TASK=None,ROLE=dev -->

| 字段 | 值 |
|------|-----|
| Name | intern_nem_dev_2 |
| Status | Idle |
| Current Task | None |
| PR | None |
| Session | 1 |

最近进展：Completed evidence-only live validation
`task220_qwen_sft_8gpu_full_data_one_iter_live_s1` on branch
`intern_nem_dev_2/task220_qwen_sft_8gpu_full_data_one_iter_live_s1` from exact
product commit `1d037329f5a02cdc04f2a09a16e7342721be4c87`. One canonical
8-GPU NemTron torchrun using full staged task208 packed data returned
`task220_torchrun_rc=0`, reached iteration `1/1`, reported
`lm loss: 1.226097E+01`, skipped/nan `0/0`, validated, and saved a `399G`
checkpoint at
`/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/checkpoints_one_iter`.
Post-run cleanup found no H200 compute apps, `:13000` and master port `29591`
clear, and `:8000` documented/untouched. No second run, package/system mutation,
process kill, endpoint/eval/benchmark, W&B, cluster/deploy, artifact upload,
main/master push, or self-merge.
