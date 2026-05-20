# task066_m1_agentic_qwen_flow - task_knowledge

<!-- METADATA:SESSION=2 -->

## Notes

- Qwen3 4B 本地路径来自个人知识库：`/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507`。
- Qwen3 4B Megatron-Bridge checkpoint 路径：`/mnt/3fs/data/lei.song/nemotron/checkpoints/qwen3-4b-instruct-2507-megatron-bridge-20260517a`。
- 本次机器上 `/root/nemotron_session5_venv/bin/python` 不存在；`/work-agents/.venv` 可用于 M0/M1/packed data prep，且有 `cosmos_xenna`、`datasets`、`transformers`、`pyarrow`，但缺 `torch`、`megatron.bridge`。
- Qwen tokenizer-only packed data prep 可以在 CPU 上完成；真实 Qwen3 4B SFT 需要带 `torch`、Megatron-Bridge 和可见 NVIDIA GPU 的训练环境。
- `NemTron` 适合跑真实 Qwen SFT：8x H200，`/root/nemotron_session5_venv` 有 `torch` 和 `megatron.bridge`，但缺 `cosmos_xenna`，所以 M0/M1 packed data prep 仍更适合在本地 `/work-agents/.venv` 完成后同步 artifacts。
- `run_finetune()` 的 dataset 构建路径会直接读取脚本 OmegaConf 的 `dataset` section；CLI overrides 若只应用到 Megatron ConfigContainer，会导致 dataset seq length / packed sequence size 保持 YAML 默认值。
- Qwen local train uses TP=2 in `qwen_local_train.py`; launch with `python -m torch.distributed.run --nproc_per_node=2` and `CUDA_VISIBLE_DEVICES=0,1`.
