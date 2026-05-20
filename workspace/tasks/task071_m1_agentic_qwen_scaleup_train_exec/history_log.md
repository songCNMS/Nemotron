# task071_m1_agentic_qwen_scaleup_train_exec - history

<!-- METADATA:SESSION=3 -->

## Session 1

- 从 Idle 接手用户请求：拉取最新主干，创建训练执行任务，并按 local data prep -> sync NemTron -> remote train -> eval 顺序启动正式 scale-up。
- 已从 `origin/main` 快进到 `5cb4541`，并创建分支 `intern_nemontron_code_reading/task071_m1_agentic_qwen_scaleup_train_exec`。
- 创建 PR #96，并生成正式 scale-up scripts 到 `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen_scaleup_train_exec`，配置为 11 个 M0 slices、train=100/val=25 per dataset、pack/seq length 4096、32 shards、`m1_full_basket`。
- local data prep 分段完成：M0 11 slices -> M1 Agentic SFT train 1100 / val shadow 273 -> Qwen packed 32 shards、944,050 tokens、train 244 rows、valid 8 rows。
- 发现 `plan_qwen_scaleup_run.py` 默认 `global_batch_size=1` 会让 formal planner 在 `gpus_per_node=2` 下失败；已将默认值修为 2，并补测试覆盖 `train.global_batch_size=2`。
- sync 到 NemTron 后启动 tmux session `task067_task071_qwen_scaleup_train_exec`，训练参数展开为 `train_iters=122`、`global_batch_size=2`。
- 训练完成：iteration 122/122，最终 validation loss `2.835580E-01`，PPL `1.327846E+00`，最终 checkpoint 为 `/work-agents/intern_nemontron_code_reading/task071_qwen_scaleup_train_exec/task071_qwen_scaleup_train_exec/checkpoints/iter_0000122`。
- 验证：ruff passed；`pytest -q tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py tests/recipes/super3/test_m1_agentic_sft.py` → 54 passed, 1 skipped；训练完成后 `m1_full_basket` eval dry-run passed。

## Session 2

- 主管要求合并 PR #96，并基于 `iter_0000122` 做 checkpoint export/register，再启动 `m1_full_basket` 非 dry-run 评测获取真实 benchmark metrics。
- merge 前确认 PR #96 open 且 mergeable；按 playbook 将 task071 README 标记 Completed，将 intern status 切回 Idle，并准备合并。
- 已 squash merge PR #96 到 `main`，merge commit `8336c3e74e42eb805aacbeee5be67d0cb57cdf77`，mergedAt `2026-05-20T02:52:49Z`。
- 在 NemTron 上用 Megatron-Bridge `AutoBridge.export_ckpt` 将 `/work-agents/intern_nemontron_code_reading/task071_qwen_scaleup_train_exec/task071_qwen_scaleup_train_exec/checkpoints/iter_0000122` 导出为 HF checkpoint：`/work-agents/intern_nemontron_code_reading/task071_qwen_scaleup_train_exec/task071_qwen_scaleup_train_exec/hf_export_iter_0000122`。
- HF export 完成并写出 3 个 `safetensors` shard、`config.json`、`tokenizer.json` 等文件；导出日志在 `/work-agents/intern_nemontron_code_reading/task071_qwen_scaleup_train_exec/task071_qwen_scaleup_train_exec/logs/export_iter_0000122_hf.log`。
- 已将导出模型注册到 manifest artifact：`task071-qwen3-4b-agentic-sft-iter0000122-hf:v1`，manifest root 为 `/work-agents/intern_nemontron_code_reading/task071_qwen_scaleup_train_exec/task071_qwen_scaleup_train_exec/artifacts`。
- 按 project rule 将最新 main 代码同步到 NemTron `/root/Nemotron_task071_eval`，并在 `/root/nemotron_session5_venv` 安装 `nemo-evaluator-launcher==0.2.5`。
- 已在 NemTron 启动 SGLang endpoint：tmux session `task071_sglang_eval`，URL `http://127.0.0.1:30000/v1/chat/completions`，model id `task071-qwen3-4b-agentic-sft-iter0000122-hf`；smoke request 返回 `ready`。
- 已对 `m1_full_basket` 做非 dry-run 提交尝试；未产出 benchmark metrics，原因是当前 19 个 `adlr_*` task name 均无法在 `nemo-evaluator-launcher` 421-task mapping 中解析，且 NemTron 无 Docker/Slurm，local executor 非 dry-run 报 `Docker is not installed or not in PATH`。
- 已创建 PR #102 记录本轮 export/register 与 eval 阻塞结果。

## Session 3

- 继续 PR #102，针对 `m1_full_basket` eval 阻塞拆解 launcher task mapping 与配置展开问题。
- 新增 `m1_eval_launcher_mapping.yaml`，记录 `nemo-evaluator-launcher==0.2.5` 中 M1 full basket 的真实 task name 覆盖情况：14 个 available，5 个 missing（`multichallenge`、`terminalbench`、`swe_bench_verified`、`mcp_mark`、`tool_decathlon`）。
- 新增 `m1_full_basket_launcher_available.yaml`，只选择 14 个已验证的真实 launcher task；没有用 MT-Bench、codec contamination 或 ToolTalk 伪替 missing benchmark。
- 修复 `nemotron super3 eval` 对 compact basket overlay 的处理：`defaults: default.yaml` 现在会合并完整 evaluator schema，顶层 `tasks` 会展开为 `evaluation.tasks[*].name`。
- 修复当前 launcher 0.2.5 兼容性：将旧式 `execution.env_vars` 归一化到 deployment/evaluation/top-level env var scope，并在 local+generic deployment 下设置 `execution.mode=sequential`。
- 已重刷 `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen_scaleup_train_exec` 的 scale-up scripts，eval dry-run 配置改为 `m1_full_basket_launcher_available`。
- 同时修正 scale-up eval script 的 `run.model` 生成逻辑，去掉旧的 `sft:task067-qwen-scaleup` 硬编码，改为基于当前 `run_name` 输出 `sft:task071_qwen_scaleup_train_exec`。
- 本地验证：`ruff check` touched files + `git diff --check` 通过；`PYTHONPATH=src python -m pytest tests/recipes/super3/test_m1_eval_full_basket.py tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py` -> 23 passed。
- 远端验证：同步代码到 NemTron `/root/Nemotron_task071_eval`；14 个 task name 全部可由 launcher mapping 解析；`run_eval(..., dry_run=True)` 使用 dummy env vars 成功生成 sequential scripts，invocation id `f0c3d45f10b2f225`。
- 真实 benchmark metrics 仍未产出：NemTron 节点缺 Docker/Slurm，launcher non-dry-run 的 local executor 生成脚本后会执行 `command -v docker`，当前环境无法启动 eval-factory containers。
