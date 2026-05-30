# intern_nem_dev_2 - 状态

<!-- METADATA:STATUS=Working,TASK=task209_nemtron_h200_sft_live_s1,ROLE=independent -->

| 字段 | 值 |
|------|-----|
| Name | intern_nem_dev_2 |
| Status | Working |
| Current Task | task209_nemtron_h200_sft_live_s1 |
| PR | Evidence-only branch: intern_nem_dev_2/task209_nemtron_h200_sft_live_s1 |
| Session | 6 |

最近进展：Session 6 used the tighter port rule and ran exactly one canonical single-GPU Qwen-contract one-iteration smoke with `CUDA_VISIBLE_DEVICES=0` and torchrun master port `29531`. Preflight passed for no SGLang/task210 process, no `:13000` listener, no H200 compute apps, and free `:29531`; `:8000` remained listening and was documented but untouched. The run reached model/dataloader setup and the training loop, then failed with `TypeError: MambaModel.forward() got an unexpected keyword argument 'packed_seq_params'`; no checkpoint was created. Session 5 logs 10-13 and Session 6 logs 01-03 were copied back into the local-visible shared artifact root with a SHA256 manifest. Boundaries observed: no process kill, no system mutation, no package install, no NemTron network, no multi-GPU/full train, no W&B/deploy/artifact upload, no main/master push, no self-merge.
