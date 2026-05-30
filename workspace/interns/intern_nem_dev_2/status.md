# intern_nem_dev_2 - 状态

<!-- METADATA:STATUS=Working,TASK=task209_nemtron_h200_sft_live_s1,ROLE=independent -->

| 字段 | 值 |
|------|-----|
| Name | intern_nem_dev_2 |
| Status | Working |
| Current Task | task209_nemtron_h200_sft_live_s1 |
| PR | Evidence-only branch: intern_nem_dev_2/task209_nemtron_h200_sft_live_s1 |
| Session | 7 |

最近进展：Session 7 finalized the evidence-only report after PM directed no further live launches or workarounds. Session 6 evidence remains the final live result: preflight passed for no SGLang/task210 process, no `:13000` listener, no H200 compute apps, and free torchrun master port `29531`; `:8000` stayed documented-only and untouched. The canonical one-GPU Qwen-contract one-iteration smoke launched, reached the training loop, and failed `rc=1` with `TypeError: MambaModel.forward() got an unexpected keyword argument 'packed_seq_params'`; checkpoint path `session6/checkpoints_one_iter` is missing and GPUs were idle after the run. No additional train/full benchmark/package/system mutation was attempted.
