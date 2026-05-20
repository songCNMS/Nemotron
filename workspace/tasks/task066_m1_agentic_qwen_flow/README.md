# task066_m1_agentic_qwen_flow

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_code_reading -->

## Background

用户要求在上一轮检查的基础上执行下一步，并使用 Qwen 模型跑完整 M1 Agentic SFT 任务流程。上一轮发现 packed sequence builder 的一个测试把 `first_fit_shuffle` 的输出顺序当成固定顺序断言，导致非功能性失败。

## Goals

- 修复或调整 packing builder 回归测试，使其验证 loss mask 在 packed subsequence 边界不串扰，而不是依赖 shuffle 后的顺序。
- 跑通 M0 数据准备、M1 Agentic SFT JSONL 转换、packed roundtrip smoke、training planner。
- 在当前环境能力允许范围内尝试 Qwen3 4B 本地训练入口，并明确记录是否受 GPU/runtime 阻塞。

## Acceptance

- [x] 相关 Python 测试通过。
- [x] Qwen 模型路径、checkpoint 路径和完整 pipeline 命令有实际执行记录。
- [x] 若无法完成真实 Qwen 4B 训练，必须给出具体环境阻塞，而不是只停在代码检查。

## Results

- M0 public data smoke: 14 datasets, 0 errors, output at `/work-agents/intern_nemontron_code_reading/task066_qwen_flow/m0`.
- M1 Agentic SFT conversion: 22 train rows, 11 val-shadow rows, 0 errors.
- Lightweight roundtrip smoke: pass, 22 records tokenized, 17 packed rows.
- Qwen tokenizer packed data prep: pass with local model `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507`, 4 shards, 7,665 tokens.
- Training planner: pass, train=13 rows / valid=4 rows, derived `train_iters=13`.
- Qwen training entry: blocked by runtime, `/work-agents/.venv` lacks `torch` and `megatron.bridge`; host also has no visible NVIDIA GPU.
