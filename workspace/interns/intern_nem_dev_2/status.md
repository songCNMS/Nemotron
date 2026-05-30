# intern_nem_dev_2 - 状态

<!-- METADATA:STATUS=Idle,TASK=none,ROLE=independent -->

| 字段 | 值 |
|------|-----|
| Name | intern_nem_dev_2 |
| Status | Idle |
| Current Task | None |
| PR | evidence-only branch |
| Session | 2 |

最近进展：Finalized and pushed task214 evidence on branch
`intern_nem_dev_2/task214_qwen_sft_one_iter_post_task213_live_s1` at head
`4abf9bc08bc7aec966bcc3645e2b65b64a5bca43`. The canonical single-GPU
Qwen-contract Stage1 SFT
one-iteration smoke on NemTron from exact merged main
`4fe9454e46343821f68e43c47cdeba1aaf0fef84` using a task-owned checkout,
task-owned config with `step_function: super3_packed_seq_compat_gpt_step`,
task208 sample packed data staged under task209, and the task209 train stack.
Preflight passed with no SGLang/task210 process, no `:13000`, no H200 compute
apps, free master port `29561`, and `:8000` documented/untouched. Exactly one
torchrun was launched and failed after reaching training loop iteration 0 with
`TypeError: forward_step() missing 1 required positional argument: 'model'`
from `packed_compat_step.py`; checkpoint path is missing and post-run GPU/port
cleanup passed. Current blocker:
`PACKED_COMPAT_STEP_BRIDGE_STATE_INJECTION_DETECTION`: Bridge did not inject
`GlobalState` because the adapter first parameter was `state_or_data_iterator`,
then the two-argument branch delegated to state-aware upstream `gpt_step`
without state. No second run or workaround was attempted. PM routed the product
fix to dev_1 task215; dev_2 is Idle / Current Task None.
