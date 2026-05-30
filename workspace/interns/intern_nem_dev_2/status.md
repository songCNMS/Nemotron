# intern_nem_dev_2 - 状态

<!-- METADATA:STATUS=Working,TASK=task209_nemtron_h200_sft_live_s1,ROLE=independent -->

| 字段 | 值 |
|------|-----|
| Name | intern_nem_dev_2 |
| Status | Working |
| Current Task | task209_nemtron_h200_sft_live_s1 |
| PR | Evidence-only branch: intern_nem_dev_2/task209_nemtron_h200_sft_live_s1 |
| Session | 4 |

最近进展：Session 4 built/staged a user-owned offline wheelhouse and `--system-site-packages` venv under `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4` without NemTron network or system mutation. Final import probe passes for `nemo_run`, `megatron.energon`, `nvidia_resiliency_ext`, `hydra`, `bracex`, Torch/CUDA, Megatron, and Megatron Bridge, but `mamba_ssm` is still missing. Canonical Qwen-contract one-iteration smoke reaches Megatron model build and blocks on missing `mamba-ssm`; a pre-hold attention-only probe reached the training loop but failed on `MambaModel.forward(... packed_seq_params)`. PM then placed a GPU hold because task210 SGLang TP=8 owns all H200s; no further train launch is allowed until PM releases GPUs. Boundaries remain: no package/model/container downloads on NemTron, no W&B/deploy/artifact upload, no main/master push, no self-merge.
