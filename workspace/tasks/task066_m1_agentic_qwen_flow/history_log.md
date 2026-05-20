# task066_m1_agentic_qwen_flow - history

<!-- METADATA:SESSION=2 -->

## Session 1

- 从 Idle 接手用户请求：修复 M1 Agentic SFT packed sequence 测试问题，并用 Qwen3 4B 跑 M0→M1→packed→training 入口验证。
- 分支：`intern_nemontron_code_reading/task066_m1_agentic_qwen_flow`。
- 修复 `tests/data_prep/test_packing_builder.py::test_loss_mask_multi_subsequence_no_bleed`：测试不再假设 `first_fit_shuffle` 保持插入顺序，而是按 packed subsequence 边界验证各自的 loss mask。
- 测试：`pytest -q tests/data_prep/test_packing_builder.py tests/recipes/super3/test_m1_agentic_sft.py tests/data_prep/test_chat_template_super3.py tests/recipes/super3/test_sft_forward_step_dispatch.py` → 73 passed, 2 skipped。
- M0 数据：`prepare_m0_assets.py --max-train-per-dataset 2 --max-val-per-dataset 1` 成功，14 datasets，0 errors。
- M1 Agentic SFT：使用 11 个 agentic SFT 支持环境转换，输出 22 train rows、11 val-shadow rows、0 errors。
- Roundtrip smoke：22 records tokenized，17 packed rows，total_tokens=7,697，total_loss_tokens=379。
- Qwen tokenizer packed data prep：本地 Qwen3 4B tokenizer 路径 `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507`，4 shards，total_sequences=22，total_tokens=7,665，train rows=13，valid rows=4。
- Training planner：本地 Bridge checkpoint `/mnt/3fs/data/lei.song/nemotron/checkpoints/qwen3-4b-instruct-2507-megatron-bridge-20260517a`，生成 `run_m1_agentic_sft.sh`，推导 `train_iters=13`。
- Qwen local training entry 实际启动尝试失败：`ModuleNotFoundError: No module named 'torch'`。当前 `/work-agents/.venv` 同时缺 `megatron.bridge`，`nvidia-smi` 不可用，无法在本机继续真实 Qwen 4B finetune。
- PR opened: https://github.com/songCNMS/Nemotron/pull/92

## Session 2

- 用户要求到远端机器 `NemTron` 上运行。
- 远端环境检查：host `lg-cmc-b7r202-e09u26-h200-000459`，8x NVIDIA H200，`/root/nemotron_session5_venv/bin/python` 存在，`torch==2.9.1+cu129`、`megatron.bridge` 可导入；远端缺 `cosmos_xenna`，因此复用 Session 1 已生成的 Qwen packed artifacts。
- 远端无法访问 GitHub 443，无法直接 clone PR 分支；通过 `tar | ssh tar` 同步当前工作树和 `/work-agents/intern_nemontron_code_reading/task066_qwen_flow` artifacts。
- 第一次远端训练启动进入 Megatron-Bridge validation 后失败：`model.seq_length=512`，但 dataset 仍是 4096。定位到 `run_finetune()` 只把 CLI overrides 应用到 Megatron ConfigContainer，`_build_dataset_config()` 仍读取未应用 overrides 的脚本 YAML。
- 修复 `src/nemotron/recipes/super3/stage1_sft/train.py`：提前仅应用 `dataset.*` / `tokenizer.*` CLI overrides 到脚本 OmegaConf，避免 dataset/tokenizer 构建读到旧值，同时保留 train/model/checkpoint overrides 走原 Megatron ConfigContainer merge。
- 本地验证：`pytest -q tests/data_prep/test_packing_builder.py tests/recipes/super3/test_m1_agentic_sft.py tests/data_prep/test_chat_template_super3.py tests/recipes/super3/test_sft_forward_step_dispatch.py` → 73 passed, 2 skipped。
- 远端最终命令使用 GPUs 0/1、TP=2、Qwen3 4B local HF model、Qwen Bridge checkpoint、Qwen packed data，完成 13/13 train iterations。
- 远端最终结果：final validation loss `3.309570E-01`，PPL `1.392300E+00`，checkpoint saved at `/work-agents/intern_nemontron_code_reading/outputs/task066_qwen_sft/checkpoints/iter_0000013`，latest checkpoint iteration `13`。
- 远端日志：`/work-agents/intern_nemontron_code_reading/outputs/task066_qwen_sft/session2_qwen_train.log`。失败重试日志保留为 `session2_qwen_train_seq_mismatch.log` 和 `session2_qwen_train_struct_override.log`。
