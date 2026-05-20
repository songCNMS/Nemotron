# task066_m1_agentic_qwen_flow - task_knowledge

<!-- METADATA:SESSION=1 -->

## Notes

- Qwen3 4B 本地路径来自个人知识库：`/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507`。
- Qwen3 4B Megatron-Bridge checkpoint 路径：`/mnt/3fs/data/lei.song/nemotron/checkpoints/qwen3-4b-instruct-2507-megatron-bridge-20260517a`。
- 本次机器上 `/root/nemotron_session5_venv/bin/python` 不存在；`/work-agents/.venv` 可用于 M0/M1/packed data prep，且有 `cosmos_xenna`、`datasets`、`transformers`、`pyarrow`，但缺 `torch`、`megatron.bridge`。
- Qwen tokenizer-only packed data prep 可以在 CPU 上完成；真实 Qwen3 4B SFT 需要带 `torch`、Megatron-Bridge 和可见 NVIDIA GPU 的训练环境。
