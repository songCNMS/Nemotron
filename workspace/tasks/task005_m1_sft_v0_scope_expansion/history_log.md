# history_log

<!-- METADATA:SESSION=5 -->

## Session 0 - 2026-05-17 - intern_nemontron_review_cc

- 由 review 流程登记任务，覆盖 plan 文档 §8 中 v0 仍未实现的 4 类 supervision。
- 未 assign，等待资源（数据源 license 复核 + 合成负例 prompt）。

## Session 1 - 2026-05-18 - intern_nemontron_code_reading

- 按 `docs/implementation-roadmap.md` 推荐顺序接手 task005。
- 本轮先实现 structured output 最小闭环：复用 Hermes `json_mode_singleturn`，新增 `structured_outputs_json` M0 环境、converter、`json_value_exact_match` verifier、M1 SFT builder、README 和单元测试。
- 合并 PR #18，将 structured output 最小闭环进入 `main`。
- 继续补齐 terminal basics、short SWE traces、repair negatives 三个切片：
  - `terminal_basic_shell` 使用 `aelhalili/bash-commands-dataset`，新增 bash command converter、`command_substring_match` verifier、M1 content-only command builder。
  - `swe_pivot_patch_supervision` 使用 `princeton-nlp/SWE-bench_Lite` issue + gold patch，新增 patch converter、`patch_diff_match` verifier、M1 unified-diff builder。
  - `tool_call_repair_negative` 从 Hermes `func_calling_singleturn` 派生 malformed / hallucinated repair negatives，写出 `negative_kind`、`repair_target`、repair message 和 corrected `tool_calls`。
- 单元测试扩展到 M0 converter、health verifier、M1 supervision builder 三层；本地目标测试为 `83 passed, 2 skipped`。
- 小样本 smoke 已跑通：三个新 slice 各生成 `2 train / 1 val`，M0 health baseline `status=pass`，M1 SFT 输出 `6 train / 3 val_shadow` 且 `errors=0`。
- 代码已提交到 PR #19：`intern_nemontron_code_reading/task005_remaining_agentic_sft_v0_envs`。

## Session 2 - 2026-05-18 - intern_nemontron_code_reading

- 合并 PR #19，将 terminal basics、short SWE traces、repair negatives 三个切片进入 `main`，merge commit 为 `3e376167881fa8c07f1deb1a2d9262d1fcb68bb5`。
- 进入 M1 SFT packed data round-trip 验证入口；当前 CPU venv 缺少完整 data-prep 运行依赖 `cosmos_xenna` 和 `transformers`，因此先新增轻量 `run_m1_sft_roundtrip_smoke.py`。
- round-trip smoke 复用 M1 JSONL、Nano3 chat template、assistant loss mask、packed parquet 写入/读回 schema 检查，避免在完整 Xenna pipeline 前遗漏格式问题。
- 验证中发现并修复 repair-negative 两个问题：
  - malformed artifact 的 raw `<tool_call>` 会触发 data-prep validator，被改为 prompt 中转义标签，`extra_env_info.invalid_artifact` 仍保留原始 artifact。
  - repair-negative 原先连续两个 user turn，会导致 Nano3 增量渲染 mismatch，被改为单个 user turn 合并原始请求与 repair 指令。
- 小样本验证已跑通：三个新 slice 各生成 `2 train / 1 val`，M0 health baseline `status=pass`，M1 SFT 输出 `6 train / 3 val_shadow`，round-trip packed parquet 输出 `1` 个 row、`3978` tokens、`802` assistant loss tokens。
- 本地目标测试：`PYTHONPATH=src pytest -q tests/recipes/super3` 为 `84 passed, 2 skipped`；`git diff --check` 通过；`ruff` 在 `/work-agents/.venv` 中不可用。
- 代码已提交到 PR #21：`intern_nemontron_code_reading/task005_m1_sft_roundtrip_session2`。

## Session 3 - 2026-05-18 - intern_nemontron_code_reading

- 合并 PR #21，将 M1 SFT round-trip smoke 与 repair-negative template 兼容修复进入 `main`，merge commit 为 `905de2db13620eeab05ccebd2e3eff68f599cb1d`。
- 从最新 `main` 创建 `intern_nemontron_code_reading/task005_full_agentic_v0_dataprep_session3`，继续做真实 `agentic_v0` data-prep 验证。
- 补齐 CPU venv 的完整运行依赖：`cosmos_xenna`、`transformers 5.8.1`、`ray 2.49.2`、`pydantic-settings`、`nemo-run`；根 CLI eager import `data sdg long-document` 时还需要 `data-designer` optional extra。
- 生成本轮完整覆盖的小样本 M0/M1 数据：
  - M0 公开数据覆盖 8 个环境：search、coding、terminal、SWE patch、general tool calling、repair negative、structured output、reasoning；每个 dataset 输出 `2 train / 1 val`。
  - M0 health baseline `status=pass`。
  - M1 Agentic SFT blend 输出 `16 train / 8 val_shadow`，`errors=0`，blend path 为 `../outputs/task005-session3/m1/data_blend_agentic_sft_v0.json`。
- 先用 HF 真实 tokenizer `Qwen/Qwen3-0.6B` 跑通 CLI 实际执行：`PYTHONPATH=src python -m nemotron super3 data prep sft -c agentic_v0 ... sample=8 num_shards=1`，产出 `8` sequences、`5279` tokens；单 shard 场景按实现只生成 train split。
- 按 project rule 改用本地真实 tokenizer `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507`，运行不带 `sample` 的完整小 blend 命令：`PYTHONPATH=src python -m nemotron super3 data prep sft -c agentic_v0 ... force=true observability.wandb_log_pipeline_stats=false`。
- 完整小 blend packed artifact 校验通过：
  - output path：`../outputs/task005-session3/packed-agentic-v0-full/splits`。
  - metadata：`num_shards=16`、`total_sequences=16`、`total_tokens=10332`、`pack_size=4096`、`tokenizer_uri=file:///mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507`。
  - split 目录覆盖 `train`、`valid`、`test`；共 `16` 个 parquet symlink。
  - parquet schema 为 `input_ids: list<int32>`、`loss_mask: list<uint8>`、`seq_start_id: list<int32>`；读回统计 `loss_tokens=1775`，`empty_loss_rows=0`。
- `data-designer 0.6.0` 安装时会把 `pyarrow` 降到 `19.0.1`，与当前 `datasets 4.8.5` 的 `pyarrow>=21` 声明冲突；本轮验证后已恢复 `pyarrow 24.0.0`，并确认 `agentic_v0 --dry-run` 仍可编译。
- 本地目标测试：`PYTHONPATH=src pytest -q tests/recipes/super3` 为 `85 passed, 1 skipped`。
- 记录更新已提交到 PR #23：`intern_nemontron_code_reading/task005_full_agentic_v0_dataprep_session3`。

## Session 4 - 2026-05-18 - intern_nemontron_code_reading

- 响应“拉取主干最新代码”，先确认当前分支为 `intern_nemontron_code_reading/task005_full_agentic_v0_dataprep_session3`、PR #23 仍为 open、工作区无未提交改动。
- 执行 `git fetch origin --prune`，清理远端已删除的旧 task 分支引用。
- 切到本地 `main` 并执行 `git pull --ff-only origin main`，本地 `main` 从 `905de2d` fast-forward 到 `3ef7942`。
- 主干本次新增内容包括 M1 RLVR/RLHF/SWE bridge、Super3 chat template、sample-level SFT loss/step dispatch、以及相关 tests/workspace task 文档。
- 切回 PR #23 分支并执行 `git rebase origin/main`，分支已基于最新主干重放，rebase 无冲突。
- 本轮不改业务代码，仅更新 Session 4 状态记录并推送到 PR #23 分支。

## Session 5 - 2026-05-18 - intern_nemontron_code_reading

- 按“review 代码尤其是修改的代码，debug 并从数据到 m1 训练跑流程任务验证”复查 PR #23 分支与最新 `origin/main` 的 M0/M1/SFT 相关改动。
- 发现并修复 M1 环境 scope 测试退步：`multi_turn_tool_use` 已纳入 `M1_USE_BY_ENV`，但测试 fixture 没提供 assistant supervision，导致 converter 正确报 empty supervision；已让 fixture 与 `general_tool_calling` 共用合法 tool-call trajectory。
- 发现并修复 M0 registry 两个失效 HF revision：
  - `dgslibisey/MuSiQue` 改为当前 main commit `c8f4f8c9465fb69d31a8eae894c3fd509c4ca321`。
  - `AI-MO/NuminaMath-CoT` 改为当前 main commit `9d8d210c9f6a36c8f3cd84045668c9b7800ef517`。
- 重新跑 M0 小样本公开数据链路，覆盖 11 个 dataset/env slice：search grounded QA、search multihop QA、MBPP coding、terminal bash、SWE patch lite、Hermes tool calling、Hermes multi-turn tool calling、tool-call repair negative、structured outputs JSON、GSM8K reasoning、NuminaMath competition。
- M0 health baseline 通过；M1 Agentic SFT 输出 `train_rows=11`、`val_shadow_rows=11`、`errors=0`，blend path 为 `/mnt/3fs/data/lei.song/nemotron/task005_session5_flow_20260518T171138Z_fixed/m1_agentic_sft/data_blend_agentic_sft_v0.json`。
- 用项目规则指定 tokenizer/model `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507` 跑通真实 `nemotron super3 data prep sft -c agentic_v0`：
  - output path：`/mnt/3fs/data/lei.song/nemotron/task005_session5_flow_20260518T171138Z_fixed/packed_agentic_v0_super3/splits`。
  - metadata：`total_sequences=11`、`total_tokens=9477`、`pack_size=4096`、`num_shards=16`、`tokenizer_uri=file:///mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507`。
  - 读回 parquet：`rows=11`、`loss_tokens=1278`、`empty_loss_rows=0`，schema 为 `input_ids list<int32>`、`loss_mask list<uint8>`、`seq_start_id list<int32>`。
- 生成 M1 SFT training plan：`/mnt/3fs/data/lei.song/nemotron/task005_session5_flow_20260518T171138Z_fixed/m1_train_smoke/plans/session5_smoke/training_manifest.json`，`train_iters=1`、`train_shards=14`、`train_rows=9`。
- 远端 `NemTron` 环境 debug：
  - 系统 Python 有 `torch 2.9.1+cu129`、Megatron-Bridge、Transformers，但缺 `cosmos_xenna` / `megatron.energon`。
  - 新建 `/root/nemotron_session5_venv --system-site-packages`，补 `megatron-energon==7.3.2`、`nvidia-resiliency-ext==0.6.0`、`hydra-core==1.3.2`；`mamba-ssm` / `causal-conv1d` 因无 GitHub wheel 访问且远端无 `nvcc` 未能安装。
- 修复当前 Megatron-Bridge API drift：
  - `megatron.bridge.recipes.common._sft_common` 已不存在；`test_train.py` 改为直接构造 tiny SFT `ConfigContainer`，`qwen_local_train.py` 改用当前 Bridge 的 `qwen3_4b_finetune_config`。
  - `qwen_local_train.py` 原本写入不存在的 `cfg.validation.eval_interval`，改为 `cfg.train.eval_interval`。
  - `tiny_model.py` fallback 扩展到当前 Bridge 的 `NemotronHModelProvider`，并保留 coverage 降级 warning。
- 修复当前 Bridge packed SFT 契约差异：
  - `PackedSequenceSpecs` 只接受单个 `.npy` packed 文件，不能直接读 `super3 data prep sft` 输出的 parquet shard 目录。
  - `stage1_sft/train.py` 在训练启动时将 packed parquet shards 懒转换为 Bridge 可读的 `.npy` list-of-dicts，并生成 current Bridge builder 会打开的 packed metadata JSON。
- 修复 smoke 训练调度差异：当前 Bridge `finetune()` 强制要求 `pretrained_checkpoint` 或 `load`；当 `checkpoint.finetune=false` 且无 load/pretrained 时，`run_finetune()` 改走 `pretrain()` loop，以符合随机初始化 smoke 配置语义。
- 远端 Super/NemotronH tiny smoke 已推进到 Megatron 初始化、tokenizer、模型构造阶段；因缺 `mamba-ssm` 停在 Mamba layer instantiation。由于远端没有 `nvcc`，没有继续用源码编译绕过。
- 为完成数据到训练主链路验证，改用 Qwen3 4B local SFT 入口跑 1-step M1 smoke：
  - 命令使用同一份 packed M1 数据、同一 Qwen tokenizer/model，`CUDA_VISIBLE_DEVICES=0`、`global_batch_size=1`、`micro_batch_size=1`、`tensor_model_parallel_size=1`。
  - 训练完成：`iteration 1/1`，`lm loss=1.237886E+01`，`grad norm=268.659`，`skipped=0`，`nan=0`。
  - checkpoint 成功保存到 `/mnt/3fs/data/lei.song/nemotron/task005_session5_flow_20260518T171138Z_fixed/m1_train_qwen4b_smoke/checkpoints/iter_0000001`。
  - validation 完成 32 samples：`lm loss=1.214117E+01`，`PPL=1.874315E+05`。
- 本地目标测试最终通过：`PYTHONPATH=src pytest -q tests/data_prep/test_chat_template_super3.py tests/recipes/super3` 为 `183 passed, 3 skipped`。
