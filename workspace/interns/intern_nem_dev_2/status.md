# intern_nem_dev_2 - 状态

<!-- METADATA:STATUS=Idle,TASK=none,ROLE=independent -->

| 字段 | 值 |
|------|-----|
| Name | intern_nem_dev_2 |
| Status | Idle |
| Current Task | None |
| PR | evidence-only branch |
| Session | 1 |

最近进展：Completed task216 evidence-only live validation on branch
`intern_nem_dev_2/task216_qwen_sft_one_iter_post_task215_live_s1`. The
canonical single-GPU Qwen-contract Stage1 SFT one-iteration smoke ran on
NemTron from exact merged main `1d037329f5a02cdc04f2a09a16e7342721be4c87`
using a task-owned checkout, task-owned config with
`step_function: super3_packed_seq_compat_gpt_step`, task208 sample packed data
staged under task209, and the task209 train stack. Preflight passed with no
SGLang/task210 process, no `:13000`, no H200 compute apps, free master port
`29571`, and `:8000` documented/untouched. Exactly one torchrun was launched.
It reached upstream Bridge `gpt_step` and Mamba model forward, confirming the
task215 state-injection path advanced past the prior missing-`model` failure,
then failed with `TypeError: 'NoneType' object is not callable` at
`mamba_ssm/ops/triton/ssd_combined.py` calling `causal_conv1d_fwd_function`.
Checkpoint path is missing and post-run GPU/port cleanup passed. Current
blocker: `MAMBA_SSM_CAUSAL_CONV1D_FWD_FUNCTION_NONE`. No second run or
workaround was attempted; dev_2 is Idle / Current Task None.
