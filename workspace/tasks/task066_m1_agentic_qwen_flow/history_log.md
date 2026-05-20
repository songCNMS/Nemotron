# task066_m1_agentic_qwen_flow - history

<!-- METADATA:SESSION=1 -->

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
