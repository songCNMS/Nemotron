# task071_m1_agentic_qwen_scaleup_train_exec - history

<!-- METADATA:SESSION=26 -->

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

## Session 4

- 回答用户关于 non-dry eval 是否需要 GPU 的问题。
- 结论：当前默认 `deployment.type=generic` + local executor 会在 non-dry eval 中启动模型服务 Docker，并使用 `docker run --gpus all`，因此模型服务侧需要 GPU；eval client/harness 容器本身主要是 CPU/IO/网络负载。
- 如果改为 `deployment.type=none` 并指向已经运行的 OpenAI-compatible endpoint（例如现有 SGLang endpoint），eval launcher 所在节点可以不分配 GPU，但外部 endpoint 仍必须由 GPU 支撑并在评测期间保持可用。
- 对 task071 当前 NemTron 状态的判断：GPU0 上的 SGLang endpoint 已经承担模型推理，真正阻塞 non-dry eval 的不是 GPU，而是缺 Docker/Slurm/Lepton 这类可执行 eval-factory containers 的 executor。

## Session 5

- 按用户要求检查 `deployment.type=none` 下，`vpn`/CPU node 是否能作为 eval launcher。
- 直接 `ssh vpn` 失败：本地 SSH config 没有 `vpn` alias；当前工作节点为 CPU node `lg-cmc-b7r201-a01u17-cpu-000006`，符合用户描述的 CPU launcher 候选环境。
- 网络检查通过：CPU node 可以访问 NemTron SGLang endpoint，`curl http://10.100.14.21:30000/v1/models` 和 `http://10.100.15.21:30000/v1/models` 均返回 `task071-qwen3-4b-agentic-sft-iter0000122-hf`。
- 工具检查：CPU node 有 Docker client 和 `dockerd` 二进制，但没有运行中的 Docker daemon；没有 `sbatch`/`srun`、`singularity`/`apptainer`/`enroot`/`nerdctl`/`lepton` CLI；本地 `/work-agents/.venv` 也未安装 `nemo_evaluator_launcher`。
- Docker 权限探测：默认 `dockerd` 启动失败在 `docker0` bridge network 权限；`--bridge=none --iptables=false --storage-driver=vfs` 可以启动 daemon，但实际 `docker run` 失败于只读 cgroup 或 sandbox 权限，不能运行 eval-factory client container。
- 在 NemTron 上生成 `deployment.type=none` dry-run 脚本验证 launcher 形态：必须设置顶层 `target.api_endpoint.url/model_id/type`；脚本仍执行 `docker run nvcr.io/nvidia/eval-factory/...`，且默认不加 `--network host`。
- 结论：当前 CPU/vpn node 网络可达模型 endpoint，但不能作为 non-dry eval launcher；要使用它需要一个可运行 Docker/container executor 的 CPU job 环境，或改用 Slurm/Lepton 等可执行 eval-factory containers 的 executor。

## Session 6

- 用户要求重新尝试 `deployment.type=none` 的 CPU/vpn launcher 路径。
- `vpn` alias 现在可解析到 `89.208.244.190`，临时 known_hosts 连接成功，主机为 `vm4vpn`、用户 `leisong`。
- `vm4vpn` Docker client 存在，但当前用户不在 `docker` 组，`/var/run/docker.sock` 为 `root:docker`，`sudo -n docker info` 需要密码；没有可直接运行 eval-factory container 的权限。
- `vm4vpn` 不能访问 NemTron endpoint：到 `10.100.14.21:30000`、`10.100.15.21:30000`、`10.100.192.16:30000` 的 TCP 检查均失败；`ssh NemTron` 在 `vm4vpn` 上也不可解析，直连 `root@10.100.14.21` 超时。
- `vm4vpn` Python 环境无 `nemo_evaluator_launcher`，且系统 Python 无 pip；即使补包，Docker 权限和网络路由仍是硬阻塞。
- 重新尝试当前 CPU node 的私有 `dockerd`：`--bridge=none --iptables=false --storage-driver=vfs --default-cgroupns-mode=host` 可以启动 daemon，但 `docker run --network host` 仍失败 `failed to create default sandbox: operation not permitted`。
- 本轮未启动真实 benchmark eval，未产出 metrics；结论保持：现有 `vpn` 与当前 CPU node 都不能作为 non-dry eval launcher，除非提供 Docker 组权限/免密 sudo/可用 Slurm 或 Lepton，并确保 launcher host 能访问 NemTron endpoint。

## Session 7

- 用户为 `vpn` 增加 Docker 权限并扩容磁盘后，重新尝试 `deployment.type=none` 非 dry-run eval。
- `vm4vpn` 上 `leisong` 已在 `docker` 组，`docker run hello-world` 与 eval-factory 容器均可执行；根分区扩容为 38G，约 18G 可用。
- `vm4vpn` 仍不能直连 NemTron 私网 endpoint，因此在当前 CPU node 建立 SSH remote forward：`vm4vpn:127.0.0.1:13000 -> 10.100.14.21:30000`，并验证 Docker host network 容器可访问 `/v1/models`。
- 用 NemTron 侧 `nemo-evaluator-launcher==0.2.5` 生成 `deployment.type=none` dry-run 脚本，再同步到 `vm4vpn` 并将 Docker run patch 为 `--network host`。
- `ifbench.ifbench` 先暴露 eval image 内 `syllapy` 依赖 `pkg_resources` 问题；容器内安装 `setuptools<81` 可恢复该模块，说明该问题是 harness image 兼容性而非 endpoint 链路。
- `simple_evals.AIME_2025` 初次失败于磁盘不足；扩容后成功拉取 `nvcr.io/nvidia/eval-factory/simple-evals:26.03` 并进入真实请求阶段。
- 针对 SGLang endpoint 兼容性修正 AIME smoke 配置：去掉 `/v1/chat/completions/` 尾斜杠，将 `max_new_tokens` 从 launcher 默认 16384 降到 2048，以适配当前 endpoint 4096 context limit。
- AIME_2025 non-dry smoke 成功：`stage.exit=0`，`score=1.0`，`n_repeats=10`，`successful_responses=10/10`，`avg_latency_ms=3341.95`，artifacts 位于 `vm4vpn:/tmp/task071_vpn_eval_aime/evaluations/20260520_174300-8a645eca228ad5d3/simple_evals.AIME_2025.0/artifacts`。

## Session 8

- 按用户要求执行下一步，继续基于 `vm4vpn` + SSH remote forward + `deployment.type=none` 路径扩展真实 eval smoke。
- 重新建立 `vm4vpn:127.0.0.1:13000 -> 10.100.14.21:30000` tunnel，并验证 endpoint 返回 `task071-qwen3-4b-agentic-sft-iter0000122-hf`、`max_model_len=4096`。
- 修正并运行 `ifbench.ifbench` 1-sample non-dry：脚本包含 Docker `--network host`、`setuptools<81`、无尾斜杠 endpoint、`max_new_tokens=2048`，并补 `OPENAI_API_KEY=dummy` 以满足 LangChain OpenAI client 初始化。
- ifbench 成功完成：`stage.exit=0`，`successful_responses=1/1`，`avg_latency_ms=3124.77`，strict/loose prompt-level 与 instruction-level 均为 `0.0`；artifacts 位于 `vm4vpn:/tmp/task071_vpn_eval/evaluations/20260520_173914-319a71866969dc8a/ifbench.ifbench.0/artifacts`。
- 尝试 `gpqa_diamond` 1-sample smoke，复用 AIME dry-run 注入的非空 `HF_TOKEN` 后仍失败于 `Dataset 'Idavidrein/gpqa' is a gated dataset on the Hub. You must be authenticated to access it.`，未打到模型 endpoint。
- 本轮结束时清理 eval 容器；`vm4vpn` 上仅保留原有 `chromium` 容器，根分区约 16G 可用。

## Session 9

- 用户提供新的 HF token 后，按要求重跑 `gpqa_diamond` 1-sample non-dry smoke。
- 重新建立 `vm4vpn:127.0.0.1:13000 -> 10.100.14.21:30000` tunnel，并确认 NemTron SGLang endpoint 返回 `task071-qwen3-4b-agentic-sft-iter0000122-hf`、`max_model_len=4096`。
- 使用新 token 作为临时环境变量运行 `simple-evals:26.03` 的 `gpqa_diamond`；eval 仍在 `load_dataset("Idavidrein/gpqa", "gpqa_diamond")` 阶段失败，错误为 gated dataset 需在 HF dataset 页面申请 access，`total_responses=0`。
- 追加最小 dataset probe：在同一容器中同时设置 `HF_TOKEN`、`HUGGING_FACE_HUB_TOKEN`、`HUGGINGFACE_HUB_TOKEN`、`HF_HUB_TOKEN`，直接加载 `Idavidrein/gpqa` 仍返回 gated dataset access failure。
- 本轮未产生 GPQA benchmark metrics；临时 SSH tunnel 已清理，`vm4vpn` 上仅保留原有 `chromium` 容器。

## Session 10

- 用户确认已申请 `Idavidrein/gpqa` 权限后，重新使用同一 HF token 作为临时环境变量验证 gated dataset 访问。
- 直接 dataset probe 已成功：`load_dataset("Idavidrein/gpqa", "gpqa_diamond", split="train[:1]")` 返回 1 行，说明权限已生效。
- 复用 `vm4vpn:127.0.0.1:13000 -> 10.100.14.21:30000` tunnel，确认 SGLang endpoint 继续服务 `task071-qwen3-4b-agentic-sft-iter0000122-hf`。
- 运行 `gpqa_diamond` 1-sample non-dry smoke：`simple-evals:26.03` 成功下载 GPQA diamond，完成 1 次模型请求并写出 `/tmp/task071_vpn_eval_gpqa/results.yml` 与 `/tmp/task071_vpn_eval_gpqa/eval_factory_metrics.json`。
- GPQA smoke 结果：`docker_exit=0`，`score=0.0`，`successful_responses=1/1`，`avg_prompt_tokens=153`，`avg_completion_tokens=370`，`avg_total_tokens=523`，`avg_latency_ms=1786.24`。
- 远端清理检查：`vm4vpn` 上仅保留原有 `chromium` 容器，根分区约 16G 可用。

## Session 11

- 按“进行下一步”执行 GPQA 小批量放大：从 1-sample smoke 扩到 `limit_samples=10` 的 `gpqa_diamond` non-dry run。
- 重新建立 `vm4vpn:127.0.0.1:13000 -> 10.100.14.21:30000` tunnel，并通过 Docker host network 验证 endpoint 返回 `task071-qwen3-4b-agentic-sft-iter0000122-hf`、`max_model_len=4096`。
- 运行配置保持 `max_new_tokens=2048`、`parallelism=1`、`n_samples=1`，并关闭 request/response body logging 以减少评测日志和 artifacts 体积。
- GPQA 10-sample 结果：`docker_exit=0`，`score=0.3`，`stddev=0.4582575695`，`stderr=0.1527525232`，`successful_responses=10/10`。
- Response stats：`avg_prompt_tokens=234.5`，`avg_completion_tokens=336.9`，`avg_total_tokens=571.4`，`avg_latency_ms=1992.3`，`max_latency_ms=2360.88`，`finish_reason.stop=10`。
- Artifacts 写在 `vm4vpn:/tmp/task071_vpn_eval_gpqa10`；本轮结束清理临时 SSH tunnel，`vm4vpn` 上仅保留原有 `chromium` 容器，根分区约 16G 可用。

## Session 12

- 用户要求切到 `m1_full_basket_launcher_available` 中下一个已映射 task 做 non-dry；按配置顺序从 `simple_evals.gpqa_diamond` 后继续。
- 尝试 `hle.hle` 1-sample non-dry：镜像 `nvcr.io/nvidia/eval-factory/hle:26.03` 启动成功，但 `cais/hle` 是 Hugging Face gated dataset，当前 token 无访问权限；失败发生在 dataset load 阶段，`total_responses=0`。
- 顺延尝试 `livecodebench.codegeneration_release_latest` 1-sample non-dry：镜像启动成功，但 `release_latest` 即使带 `--first_n 1` 仍会下载并构建多份大 JSONL，进程在生成 dataset split 时被 OOM kill，退出码 137，未请求模型。
- 继续顺延到 `scicode.scicode` 1-sample non-dry：镜像 `nvcr.io/nvidia/eval-factory/scicode:26.03` 运行成功，`docker_exit=0`，产出 `/tmp/task071_vpn_eval_scicode1/results.yml` 和 `/tmp/task071_vpn_eval_scicode1/eval_factory_metrics.json`。
- SciCode 指标：`problems_pass@1=0.0`，`steps_pass@1=0.1666666667`；response stats 为 `count=19`、`successful_count=5`、`status_codes.200=5`、`status_codes.400=14`、`avg_latency_ms=825.31`。
- SciCode 的 400 响应来自当前 endpoint `max_model_len=4096`：后续 step prompt 加上 `max_new_tokens=2048` 后超过 context limit，部分请求报 6033/6081 tokens total 或 input 4104/4287/4375/4716 tokens。
- 本轮结束清理临时 SSH tunnel；`vm4vpn` 上仅保留原有 `chromium` 容器，根分区约 12G 可用。

## Session 13

- 用户要求按 `m1_full_basket_launcher_available` 顺序把所有 mapped eval benchmarks 做 non-dry eval；重新建立 `vm4vpn:127.0.0.1:13000 -> 10.100.14.21:30000` tunnel，并确认 endpoint 仍服务 `task071-qwen3-4b-agentic-sft-iter0000122-hf`、`max_model_len=4096`。
- `lm-evaluation-harness.mmlu_pro` 1-sample-per-category non-dry 完成：`docker_exit=0`，14 个 MMLU-Pro category 各 1 条，group exact_match `0.0`，`successful_responses=14/14`，`avg_latency_ms=834.27`；artifacts 位于 `vm4vpn:/tmp/task071_vpn_eval_mmlu_pro1`。
- `nemo_skills.ns_hmmt_feb2025` 1-sample non-dry 完成：镜像名需用 `nvcr.io/nvidia/eval-factory/nemo-skills:26.03`，`docker_exit=0`，`symbolic_correct=100.0`，`num_entries=1`，`successful_responses=1/1`，`avg_latency_ms=8411.62`；artifacts 位于 `vm4vpn:/tmp/task071_vpn_eval_hmmt1`。
- `ruler.ruler-256k-chat` 使用 `nvcr.io/nvidia/eval-factory/long-context-eval:26.03` 进入真实 256k 数据准备和请求阶段，但当前 4096-token endpoint 对长上下文请求全部返回 400；手动清理占满磁盘的容器后命令退出 `docker_exit=137`，metrics 为 `count=300`、`successful_count=0`、`status_codes.400=300`；artifacts 位于 `vm4vpn:/tmp/task071_vpn_eval_ruler1`。
- `AA-LCR.aa_lcr` 1-sample non-dry 进入真实请求，但首条样本输入约 `101423` tokens，超过 4096 context；`docker_exit=1`，metrics 为 `count=30`、`successful_count=0`、`status_codes.400=30`；artifacts 位于 `vm4vpn:/tmp/task071_vpn_eval_aa_lcr1`。
- `tau2_bench.tau2_bench_airline` 1 task / 1 trial / 5 max steps non-dry 进入真实 agent 请求，但首步输入 `4827` tokens 超过 4096 context；`docker_exit=1`，metrics 为 `count=3`、`successful_count=0`、`status_codes.400=3`；artifacts 位于 `vm4vpn:/tmp/task071_vpn_eval_tau2_airline1`。
- `bfcl.bfclv3` `task=all` 初次失败于 executable category 缺少外部 API credential；补 dummy `GEOCODE_API_KEY`、`RAPID_API_KEY`、`OMDB_API_KEY`、`EXCHANGERATE_API_KEY` 后重新跑，生成阶段成功发出 1 个模型请求，评估阶段卡在 executable ground-truth 外部 API 响应结构，`docker_exit=1`，metrics 为 `count=1`、`successful_count=1`、`status_codes.200=1`；artifacts 位于 `vm4vpn:/tmp/task071_vpn_eval_bfclv3_all1_dummykeys`。
- `lm-evaluation-harness.mmlu_prox_chat` non-dry 进入多语言数据下载和请求，`limit_samples=1` 仍展开为 196 个 language/category 请求；第 44 个请求输入 `4563` tokens 超过 4096 context 后失败，`docker_exit=1`，metrics 为 `count=45`、`successful_count=43`、`status_codes.200=43`、`status_codes.400=2`；artifacts 位于 `vm4vpn:/tmp/task071_vpn_eval_mmlu_prox1`。
- `nemo_skills.ns_wmt24pp` 1-sample non-dry 成功：`docker_exit=0`，BLEU `64.31870218238025`，`successful_responses=1/1`，`avg_prompt_tokens=51`，`avg_completion_tokens=38`，`avg_latency_ms=711.0`；artifacts 位于 `vm4vpn:/tmp/task071_vpn_eval_wmt24pp1`。
- 至此 `m1_full_basket_launcher_available` 14 个 mapped benchmarks 均已按配置顺序做过 non-dry attempt：AIME/GPQA/ifbench/HLE/LiveCodeBench/SciCode 的结果沿用 Sessions 7-12，本轮补齐 mmlu_pro、HMMT、RULER、AA-LCR、tau2、BFCL、MMLU-ProX、WMT24++；阻塞集中在 gated dataset、vm4vpn 内存/磁盘、external executable credentials 和当前 4096-token context limit。

## Session 14

- 按用户要求拉取主干最新代码：在当前 PR 分支 `intern_nemontron_code_reading/task071_eval_register_results` 上执行 `git fetch origin main`，将 `origin/main` 从 `6270724` 更新到 `9f26f42`。
- 已通过 `git merge --no-edit origin/main` 将最新 main 合入当前分支，合并过程无冲突；新增主干内容包含 M0/M1 数据与 lineage 相关 scripts、milestone modules 和测试。
- 本轮未启动新的训练或评测任务；工作重点是保持 PR #102 分支与最新主干同步，并更新 Session 14 workspace 记录。

## Session 15

- 按“继续下一步”从 PR #102 的剩余缺口切入：此前 14 个 `m1_full_basket_launcher_available` benchmark 的 non-dry attempt 只记录在人工日志里，缺少机器可校验的结果 manifest。
- 新增 `src/nemotron/recipes/super3/milestones/m1_eval_basket/m1_full_basket_non_dry_results_task071_iter0000122.yaml`，登记 task071 iter_0000122 导出模型、launcher 版本、vm4vpn + endpoint tunnel 执行形态、14 个 benchmark 的 attempt 状态、指标、artifacts 和阻塞原因。
- 在 `tests/recipes/super3/test_m1_eval_full_basket.py` 增加结果 manifest 校验：要求结果顺序覆盖 `m1_full_basket_launcher_available.yaml` 的全部 14 个 launcher task，要求 benchmark/source_basket 与 mapping 对齐，要求 scored 与 blocked/partial 状态显式，并检查不写入 HF token。
- 验证：`PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/recipes/super3/test_m1_eval_full_basket.py` -> 22 passed；`/work-agents/.venv/bin/ruff check tests/recipes/super3/test_m1_eval_full_basket.py` passed；`git diff --check` passed。

## Session 16

- 按用户要求在 HLE 权限更新后重试 HLE：先在 `vm4vpn` 上用 `nvcr.io/nvidia/eval-factory/hle:26.03` 做 dataset probe，不带 token 仍显示 `cais/hle` gated，需要显式 credential。
- 使用当前 Hugging Face credential 重新 probe，`load_dataset("cais/hle", split="test[:1]")` 成功，返回 1 条样本和列名，确认 HLE 数据权限已生效。
- 检查 task071 标准模型 endpoint：NemTron `127.0.0.1:30000` 已无 Qwen SGLang 服务；`vm4vpn:127.0.0.1:13000 -> 10.100.14.21:30000` remote-forward 后，host curl 和 Docker curl 均返回 connection reset。
- 检查 NemTron GPU 状态：8 张 H200 均被独立 `gpt-oss-120b` SGLang 服务占满，服务端口为 `10.100.14.21:39454`，不是 task071 的 Qwen checkpoint；本轮没有直接停止该服务。
- 更新 `m1_full_basket_non_dry_results_task071_iter0000122.yaml` 中 HLE 的 blocker：从 `gated_dataset` 改为 `model_endpoint_unavailable`，并记录 dataset probe 通过、endpoint probe 失败；本轮未产生 task071 HLE benchmark score。

## Session 17

- 按用户要求重新启动 task071 Qwen SGLang endpoint 并复跑 `hle.hle` non-dry。当前 `NemTron` alias 指向空闲 H200 节点 `10.100.2.62:33808`，该节点 8 张 H200 空闲但没有 task071 artifacts。
- 从旧 task071 节点 `10.100.14.21:19355` 将 `/work-agents/intern_nemontron_code_reading/task071_qwen_scaleup_train_exec/task071_qwen_scaleup_train_exec/hf_export_iter_0000122` 流式复制到新空闲节点，校验大小约 7.6G 且 safetensors/tokenizer/config 文件齐全。
- 在新节点用 tmux session `task071_sglang_eval` 启动 SGLang：model id `task071-qwen3-4b-agentic-sft-iter0000122-hf`，端口 `30000`，`context-length=4096`，GPU0；`/v1/models` 和 chat smoke 均通过。
- 重建 `vm4vpn:127.0.0.1:13000 -> NemTron 10.100.2.62:30000` remote forward，宿主和 Docker 容器内均可访问 task071 endpoint。
- 运行 `hle.hle` 1-sample text-only non-dry：`limit_samples=1`、`parallelism=1`、`max_new_tokens=2048`、HLE 数据访问通过，模型 generation 成功并写出 `/tmp/task071_vpn_eval_hle1_retry/hle_task071-qwen3-4b-agentic-sft-iter0000122-hf.json`。
- HLE 官方 judge 阶段失败：`run_judge_results.py` 需要 `OPENAI_CLIENT_ID` 和 `OPENAI_CLIENT_SECRET` 做 Azure/OpenAI OAuth，当前本地、vm4vpn 和 NemTron 环境均未找到这些变量。
- 已对该 multiple-choice 样本用标准答案核对：模型回答 `C`，标准答案 `D`，manual multiple-choice accuracy 为 `0.0`；response stats 为 `successful_responses=1/1`、`avg_prompt_tokens=117`、`avg_completion_tokens=157`、`avg_latency_ms=986.5`。
- 更新结构化结果 manifest：HLE 从 `model_endpoint_unavailable` 改为 `partial` / `official_judge_credentials`，记录 artifacts、generation 成功、manual MC score 0.0 和 official judge blocker。

## Session 18

- 按用户要求梳理 evaluation pool 中全部 benchmark 的 ready/blocked 状态，基于 `m1_eval_launcher_mapping.yaml` 和 `m1_full_basket_non_dry_results_task071_iter0000122.yaml` 汇总。
- Pool 总览：M1 intended full basket 共 19 个 benchmark；`nemo-evaluator-launcher==0.2.5` 当前有 14 个 exact launcher task mapping，另有 5 个 mapping gap。
- task071 non-dry 结果总览：14 个 mapped benchmark 均已 attempt；7 个 scored，3 个 partial，4 个 blocked。
- live runtime 检查：当前 `NemTron` 为 `lg-cmc-b7r201-f08u26-h200-000126`，tmux session `task071_sglang_eval` 正在运行，`/v1/models` 返回 `task071-qwen3-4b-agentic-sft-iter0000122-hf`，`max_model_len=4096`；`vm4vpn` Docker 可用，根分区约 19G 可用。
- 当前仍需处理的 blockers：official HLE judge OAuth credentials、LiveCodeBench launcher host memory/disk、RULER/AA-LCR/tau2/MMLU-ProX 的 4096 context limit、BFCL executable external API credentials，以及 5 个 launcher mapping gaps。

## Session 19

- 按用户问题核对现有 Qwen checkpoint 是否完整跑完 SFT 数据：检查本地 `training_manifest.json`、packed split metadata、task README，以及旧训练节点上的 `train.log` 和 checkpoint directory。
- 结论：`iter_0000122` 完整跑完了 task071 formal scale-up 配置生成的全部 prepared packed train split。证据是 packed train rows `244`、`global_batch_size=2`、`train_iters=122`，几何上正好覆盖 `244` 个 packed train rows；远端 train log 显示 `train_iters: 122`、training loop 到 iteration 122、成功保存 `iter_0000122`，并在 iteration 122 上完成 validation loss `2.835580E-01` / PPL `1.327846E+00`。
- 该 checkpoint 不是“所有上游 HF 原始数据全集”的 SFT：task071 scale-up manifest 明确设置 11 个 M0 slices，每个 dataset 最多 `100` 条 train、`25` 条 val shadow；最终 M1 train JSONL 为 `1100` 行，val shadow 为 `273` 行，packing 后为 `944,050` tokens、`244` train packed rows、`8` valid packed rows。
- 远端证据：旧训练节点 `10.100.14.21:19355` 上存在 `/work-agents/intern_nemontron_code_reading/task071_qwen_scaleup_train_exec/task071_qwen_scaleup_train_exec/checkpoints/iter_0000122`，大小约 `53G`，`latest_checkpointed_iteration.txt` 为 `122`。

## Session 20

- 按用户要求重新生成 uncapped M0/M1 prepared data：为 `prepare_m0_assets.py` 增加 `--uncapped`，并让 `plan_qwen_scaleup_run.py` 能生成 uncapped M0 数据准备脚本；同时补充单测覆盖 uncapped 参数透传。
- 本地数据结果：M0 11 个 agentic slice 合计写出 `983397` 条 train 可用记录和 `11354` 条 val-shadow 来源记录；最大 slice 为 NuminaMath `859494` train / `100` val。Hermes 源中 `2389` 条不可验证空 assistant/tool-call 行被 converter reject，保留有效 tool-call/repair/json 数据。
- M1 与 packing 结果：`prepare_m1_agentic_sft.py` 产出 `983397` train rows、`11354` val-shadow rows；Qwen tokenizer packing 产出 `302049374` tokens、`72947` packed train rows、`1159` packed valid rows。
- 修复执行链路问题：`wandb_kit.finish_run()` 兼容无 `wandb.run` 的本地 stub；scale-up planner 增加 `eval_interval`；remote train script 通过 `tmux set-environment -g TRAIN_ITERS "$TRAIN_ITERS"` 避免 tmux 内 `TRAIN_ITERS` 为空。
- 初次 2-GPU 启动是为了沿用 Qwen local recipe 的 `tensor_model_parallel_size=2` 并快速验证全量数据链路；用户指出 GPU 利用不足后，保留 2-GPU `iter_0001000` 到 `checkpoints_2gpu_iter1000_interrupted_20260521_1107`，改为 GPU1-6 的 6-GPU run。GPU0 保留给既有 SGLang eval endpoint，GPU7 因 TP=2 需要偶数 world size未纳入。
- 远端依赖补齐：当前 NemTron 新节点无原 session venv，创建 `/root/nemotron_session5_venv --system-site-packages` 后补 `nvidia-resiliency-ext`、`hydra-core`、`megatron-energon`，Qwen training import 与 Megatron checkpoint load 均通过。
- 6-GPU 训练配置：`CUDA_VISIBLE_DEVICES=1,2,3,4,5,6`，`nproc_per_node=6`，TP=2、DP=3，`global_batch_size=6`，`micro_batch_size=1`，`train_iters=12158`，`eval_interval=1000`，`save_interval=1000`。
- 训练完成：最终 checkpoint 为 `iter_0012158`，远端大小约 `53G`，`latest_checkpointed_iteration.txt=12158`。最终 validation loss/PPL 为 `0.3308907` / `1.392208`；最佳 validation 为 iter `11000` 的 `0.3213488` / `1.378986`。
- 指标产物：已拉取远端 train log 并生成 `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen_uncapped_sft_train_exec/metrics/train_6gpu_metrics.json`、`train_6gpu_train_loss.csv`、`train_6gpu_validation.csv`、`train_6gpu_loss_curve.png`。
- 验证：`pytest -q tests/kit/test_wandb_patch.py tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py tests/recipes/super3/test_m1_agentic_sft.py tests/recipes/super3/test_m0_data_env.py` -> `88 passed, 3 skipped`；ruff touched files passed；`git diff --check` passed。
- 使用 Megatron-Bridge `AutoBridge.export_ckpt` 将 `iter_0012158` 导出为 HF checkpoint：`/work-agents/intern_nemontron_code_reading/task071_qwen_uncapped_sft_train_exec/task071_qwen_uncapped_sft_train_exec/hf_export_iter_0012158`；导出目录约 `7.6G`，包含 3 个 safetensors shard、`config.json`、`tokenizer.json` 和 `model.safetensors.index.json`。
- 已写入导出 manifest 和 `ModelArtifact` metadata，artifact id 记录为 `task071-qwen3-4b-agentic-sft-iter0012158-hf:v1`；`AutoConfig`/`AutoTokenizer` 校验通过，`model_type=qwen3`、`vocab_size=151643`。
- 已停掉旧 `iter_0000122` SGLang endpoint，并在 NemTron GPU0 重新启动 `task071_sglang_eval`，model id 为 `task071-qwen3-4b-agentic-sft-iter0012158-hf`，`/v1/models` 和 chat smoke 均通过，`max_model_len=4096`。
- 重建 `vm4vpn:127.0.0.1:13000 -> NemTron 10.100.2.62:30000` remote forward，并确认宿主与 Docker host-network 容器均可访问新 endpoint。
- 对不需要 gated HF token 或长上下文的 5 个 regression tasks 做 non-dry 对比评测：AIME25、MMLU-Pro、HMMT、IFBench、WMT24++ 均 `docker_exit=0`，artifacts 位于 `vm4vpn:/tmp/task071_vpn_eval_iter0012158`。
- 与 `iter_0000122` 对比：AIME25 1-sample/10-repeats 从 `1.0` 到 `0.0`；MMLU-Pro 14 requests 仍为 `0.0`；HMMT 1-sample symbolic_correct 从 `100.0` 到 `0.0` 且 no_answer `100.0`；IFBench 1-sample 仍为全 `0.0`；WMT24++ 1-sample BLEU 仍为 `64.31870218238025`。AIME/HMMT 都是单样本口径，结论只作为回归信号。
- 新增结构化结果记录 `src/nemotron/recipes/super3/milestones/m1_eval_basket/m1_full_basket_non_dry_results_task071_iter0012158.yaml`；本轮未重跑 GPQA/HLE，因为当前 `vm4vpn` active shell 没有 HF token，且 HLE 仍需要官方 judge OAuth credential 才能得到 official score。
- 运行中处理了 `vm4vpn` 磁盘满：AIME/MMLU 完成后 HMMT 首次因 Docker image/log 写入触发 no space，清理不再需要的 eval-factory images 后重新运行 HMMT/WMT，再移除 `nemo-skills` image 后运行 IFBench；最终根分区恢复到约 `18G` 可用。
- 按用户要求从 `vm4vpn:/tmp/task071_vpn_eval_iter0012158` 抽取并返回 5 个任务的完整原始结果字段，包括每个任务的 `results.yml` 核心 metrics、`eval_factory_metrics.json` response stats、额外 `metrics.json` 和 `docker_exit=0` 状态。
- 用户指出上述 5 个 eval benchmark 只有少量数据后，确认原因是前一轮 manifest 明确使用 1-sample / 1-per-category 的 quick regression 口径，不是完整 benchmark 口径。
- 在 `vm4vpn:/tmp/task071_vpn_eval_iter0012158_full` 启动同一 iter0012158 endpoint 的 full-selected non-dry eval：IFBench、AIME25、HMMT、WMT24++、MMLU-Pro 五项均去掉 sample limit。
- IFBench 官方 full 配置的 `max_new_tokens=2048` 在 293/294 后触发 4096-token endpoint context limit；兼容性重跑使用 `max_new_tokens=1536` 完成 294/294，strict prompt-level `0.2755102040816326`、loose prompt-level `0.2857142857142857`。
- AIME25 官方 `simple_evals.AIME_2025` full 尝试失败于外部 judge credential；采用同一 AIME 2025 30 题 x10 repeats 的 `aime_2025_nemo` 本地 exact/sympy scorer，score `0.11`、stderr `0.015425013273341405`。
- HMMT full 30 题完成，`symbolic_correct=0.0`、`no_answer=93.33333333333333`；WMT24++ full output JSONL 为 4990 行，`xx->xx` BLEU `29.295411202064134`。
- MMLU-Pro full 首轮 parallelism=8 在 7166/12032 成功响应后 aiohttp timeout；保留 cache 后用 parallelism=4、request_timeout=300、max_retries=8 续跑完成 12032/12032，group exact_match `0.1346409574468085`。
- 新增 full-selected 结果 manifest `src/nemotron/recipes/super3/milestones/m1_eval_basket/m1_full_basket_full_non_dry_results_task071_iter0012158.yaml`，并在 `tests/recipes/super3/test_m1_eval_full_basket.py` 中锁定样本限制已移除、关键 metrics 和 secret scan。
- 按用户要求在原始 Qwen3-4B-Instruct-2507 上运行同一组 full-selected non-dry benchmarks：在 NemTron GPU1 启动 `qwen3-4b-instruct-2507-original` SGLang endpoint，通过 `vm4vpn:127.0.0.1:13001` 两跳 tunnel 运行 IFBench、AIME25 local scorer、HMMT、WMT24++、MMLU-Pro 五项。
- 原始 Qwen 五项均 `docker_exit=0`：IFBench strict prompt-level `0.30612244897959184`；AIME25 score `0.09333333333333335`；HMMT symbolic_correct `6.666666666666667`、no_answer `83.33333333333333`；WMT24++ `xx->xx` BLEU `28.361839067434847`；MMLU-Pro group exact_match `0.0078125`。
- 与 iter0012158 SFT 的 primary metric delta（original minus SFT）：IFBench `+0.03061224489795924`、AIME25 `-0.01666666666666665`、HMMT `+6.666666666666667`、WMT24++ `-0.933572134629287`、MMLU-Pro `-0.1268284574468085`。
- 新增原始 Qwen baseline manifest `src/nemotron/recipes/super3/milestones/m1_eval_basket/m1_full_basket_full_non_dry_results_qwen3_4b_instruct_2507_original.yaml`，并扩展 `tests/recipes/super3/test_m1_eval_full_basket.py` 锁定 baseline 样本范围、关键 metrics、SFT delta 和 secret scan。
- 清理本轮临时资源：关闭原始 Qwen 的两跳 SSH tunnel，停止 NemTron `task071_sglang_original_qwen` tmux endpoint，保留 GPU0 上 iter0012158 SFT endpoint `task071_sglang_eval`；`vm4vpn` 仅保留既有 chromium 容器且根分区约 20G 可用。
- 审计 uncapped SFT 数据完整性：`scaleup_manifest.json` 记录 11 个 M0 registry 数据集 `uncapped=true` 且无 train/val cap；M0 经过 converter 校验后写出 `983397` 条 train 可用记录和 `11354` 条 val-shadow 来源记录，其中 Hermes 三个切片合计 `2389` 条不可验证 assistant/tool-call 目标被 reject。
- 确认 M1 与 packing 覆盖：M1 curriculum 保持 `983397 -> 983397` train rows 且无 solved-rate drop；Qwen packing 读入全部 `983397` 行，产出 `983224` 条 tokenized sequences 和 `74106` 条 packed sequences，过滤 `173` 条无效/tokenization 行，并有 `211` 条截断到 4096 pack size。
- 确认训练覆盖：packed split 为 `72947` train rows / `1159` valid rows；planner 使用 `train_iters=ceil(72947/6)=12158`、`global_batch_size=6`，训练日志保存到 `iter_0012158`，最终 validation loss/PPL 为 `0.3308907` / `1.392208`。
- 按用户指定路径检查 CephFS Qwen 模型：`/mnt/cephfs/datasprocessing/shared_models/Qwen` 在本机和 NemTron 均不存在；本机实际可见的相近目录 `/mnt/cephfs/data/processing/shared_models` 为空且无 `Qwen` 子目录。
- 额外核对 CephFS 上可用的 Qwen 模型树：`/mnt/cephfs/data/stable/models/Qwen` 存在，按 `config.json` 和顶层 safetensors/bin 权重过滤出 41 个可加载模型目录，覆盖 Qwen2.5、Qwen3、Qwen3.5、Qwen3.6、Qwen3-Coder、Qwen3-Next、QwenLong 等系列。
- 按用户要求停止 NemTron 上旧 task071 服务：kill 掉 `task071_sglang_eval`，释放 GPU0；复核后 NemTron 无 task071 SGLang/torchrun 残留进程。
- 新增 `qwen3_30b_a3b_local_train.py`，使用 Megatron-Bridge Qwen3-MoE common finetune builder 接入本地 `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507`，并固定 full SFT 并行形态 TP=4/PP=2/EP=4、sequence_parallel=true；补充 env var resolver 单测。
- 验证 Qwen3-4B-Instruct-2507 与 Qwen3-30B-A3B-Instruct-2507 的 `tokenizer.json`、`tokenizer_config.json` sha256 完全一致，因此复用 task071 uncapped Qwen packed split；远端 packed split 为 63 train parquet + 1 valid parquet，并已有 Bridge `.npy` cache。
- 在 NemTron 上用 Bridge `AutoBridge.import_ckpt` 将 Qwen3-30B-A3B-Instruct-2507 HF checkpoint 导入 Megatron torch_dist：输出 `/work-agents/intern_nemontron_code_reading/task071_qwen30b_a3b_sft_train_exec/pretrained_megatron_qwen3_30b_a3b_instruct_2507`，大小约 `57G`，日志出现 `IMPORT_DONE`。
- 启动 8-GPU 30B-A3B full SFT：tmux session `task071_qwen30b_train`，`CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7`，GBS=8、MBS=1、seq=4096、`train_iters=9119`，checkpoint 输出到 `/work-agents/intern_nemontron_code_reading/task071_qwen30b_a3b_sft_train_exec/checkpoints`。
- 首次训练启动因 CLI 传入 `dataset.super3_packed_sft_dir` 在第二次 Hydra merge 阶段被最终 `FinetuningDatasetConfig` struct 拒绝而失败；修正为只通过 `SUPER3_M1_AGENTIC_PACKED_DIR` 环境变量传 packed dir 后重启成功。
- 训练已从 imported checkpoint 成功 reshard/load 到 TP=4/PP=2，进入 iteration；iter 40 时 loss `0.5799908`、load_balancing_loss `1.689439`，无 skipped/nan，8 卡显存约 `81-87GB`。
- 继续监控到 iter `80/9119`：consumed samples `640`，lm loss `0.4858986`，load_balancing_loss `1.648061`，无 skipped/nan；当前每 10 iter 约 24s，完整 1 epoch 预计为数小时量级，eval benchmark 对比需等待 final checkpoint export 后执行。
- Stop-hook 补充复核：`history_log.md` metadata 已更正为 `SESSION=20`；训练仍在 `task071_qwen30b_train` 中运行，最新观测 iter `150/9119`、consumed samples `1200`，lm loss `0.4167098`，无 skipped/nan。

## Session 21

- 接续监控 Qwen3-30B-A3B full SFT：训练已完成到 `iter_0009119`，最终 checkpoint 位于 `/work-agents/intern_nemontron_code_reading/task071_qwen30b_a3b_sft_train_exec/checkpoints/iter_0009119`，`latest_checkpointed_iteration.txt=9119`，最终 validation loss/PPL 为 `0.3001248` / `1.350027`。
- 使用 Megatron-Bridge `AutoBridge.export_ckpt` 将 `iter_0009119` 导出为 HF checkpoint：`/work-agents/intern_nemontron_code_reading/task071_qwen30b_a3b_sft_train_exec/hf_export_iter_0009119`，导出目录约 `57G`，含 16 个 safetensors shard，`AutoConfig` 显示 `model_type=qwen3_moe`、`num_hidden_layers=48`、`num_experts=128`。
- 在 NemTron 8 张 H200 上启动 SGLang endpoint：model id `task071-qwen3-30b-a3b-agentic-sft-iter0009119-hf`，`tp=4`、`dp=2`、`context_length=4096`，通过 `vm4vpn:127.0.0.1:13000 -> NemTron 10.100.2.62:30000` remote forward 暴露给 eval launcher。
- 对 Qwen3-30B-A3B SFT 跑完五项 full-selected non-dry eval：IFBench、AIME25 local scorer、HMMT、WMT24++、MMLU-Pro 全部 `docker_exit=0`；raw artifacts 位于 `vm4vpn:/tmp/task071_vpn_eval_qwen30b_iter0009119_full`。
- SFT 五项主指标：IFBench strict prompt-level `0.30272108843537415`；AIME25 score `0.0`；HMMT symbolic_correct `0.0`、no_answer `93.33333333333333`；WMT24++ `xx->xx` BLEU `33.332009385866584`；MMLU-Pro group exact_match `0.07737699468085106`。
- 切换同一 8-GPU SGLang endpoint 到原始 `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507`，model id `qwen3-30b-a3b-instruct-2507-original`，复用同一 vpn tunnel，并运行同一五项 full-selected non-dry baseline；raw artifacts 位于 `vm4vpn:/tmp/task071_vpn_eval_qwen30b_original_full`。
- 原始 30B 五项主指标：IFBench strict prompt-level `0.3197278911564626`；AIME25 score `0.16666666666666666`；HMMT symbolic_correct `6.666666666666667`、no_answer `93.33333333333333`；WMT24++ `xx->xx` BLEU `33.03998831072459`；MMLU-Pro group exact_match `0.00008311170212765957`。
- 与 SFT 的 primary metric delta（original minus SFT）：IFBench `+0.017006802721088454`、AIME25 `+0.16666666666666666`、HMMT `+6.666666666666667`、WMT24++ `-0.2920210751419958`、MMLU-Pro `-0.0772938829787234`。
- 新增结构化结果 manifest：`m1_full_basket_full_non_dry_results_task071_qwen3_30b_a3b_iter0009119.yaml` 和 `m1_full_basket_full_non_dry_results_qwen3_30b_a3b_instruct_2507_original.yaml`；扩展 `tests/recipes/super3/test_m1_eval_full_basket.py` 锁定 30B SFT/original 样本范围、关键 metrics、delta 和 secret scan。
- 清理运行资源：停止原始 30B SGLang tmux endpoint，NemTron 8 张 GPU 均回到空闲；`vm4vpn` 仅保留既有 chromium 容器，根分区约 `20G` 可用。
- 验证：`PYTHONPATH=src pytest -q tests/recipes/super3/test_m1_eval_full_basket.py` -> `38 passed, 8 warnings`；`ruff check tests/recipes/super3/test_m1_eval_full_basket.py` passed；`git diff --check` passed。

## Session 22

- 按用户要求合并 PR #151：`gh pr merge 151 --squash --delete-branch=false` 成功，合并时间 `2026-05-22T05:34:44Z`，merge commit 为 `b05f851f8e2cd8c9ee5e5bbb21b4eb10605d9c1b`。
- 从最新 `main` 创建分支 `intern_nemontron_code_reading/task071_sft_strategy_adjust_session22`，分析 30B-A3B SFT 在 AIME/HMMT 退化的可能原因：M1 math/reasoning target 原先优先使用短 `expected_answer`，会把 GSM8K/NuminaMath 的 full solution supervision 压缩成 answer-only。
- 调整 `prepare_m1_agentic_sft.py`：`math_reasoning_numeric` 与 `math_competition_numeric` 在 `extra_env_info.reference_solution` 存在时保留完整解法，去掉 GSM8K `####` verifier marker，并在参考解法缺少 normalized final answer 时追加 `Final answer: ...`。
- 调整训练策略入口：`plan_m1_agentic_sft_training.py` 支持 `--optimizer-lr`、`--scheduler-min-lr`、`--lr-warmup-iters`、`--lr-decay-iters` 并写入 torchrun overrides；`plan_qwen_scaleup_run.py` 支持 `--train-entrypoint`、LR/scheduler overrides 和 `--allow-missing-checkpoint`，可生成 30B-A3B conservative run 脚本。
- 补齐 `qwen_local_train.py` 对 optimizer/scheduler CLI overrides 的读取，避免 4B debug path 忽略 planner 输出的训练策略参数；30B path 已通过 `qwen3_30b_a3b_local_train.py` 读取同类 override。
- 已生成 conservative Qwen3-30B-A3B 策略脚本：`/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_sft_strategy_conservative_v2/`，配置为 uncapped M0/M1、30B entrypoint、8 GPU、GBS=8、MBS=1、0.5 epoch、`optimizer.lr=1e-6`、`scheduler.min_lr=1e-7`、warmup 100、eval/save interval 500，remote root 为 `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs`。
- 远端路径核验：NemTron 上存在 `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507` 与 `/work-agents/intern_nemontron_code_reading/task071_qwen30b_a3b_sft_train_exec/pretrained_megatron_qwen3_30b_a3b_instruct_2507`，因此生成脚本指向真实 30B HF model 与 Megatron bridge checkpoint。
- 验证：`PYTHONPATH=src pytest -q tests/recipes/super3/test_m1_agentic_sft.py tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py` -> `61 passed, 1 skipped`；targeted regression tests -> `3 passed`；ruff touched files passed；`git diff --check` passed。
- 已提交并推送分支，创建 PR #152：`https://github.com/songCNMS/Nemotron/pull/152`。

## Session 23

- 按用户要求合并 PR #152：`gh pr merge 152 --squash --delete-branch=false` 成功，随后快进本地 `main` 到 `origin/main` 的合并提交 `537d89d`，并创建执行分支 `intern_nemontron_code_reading/task071_conservative_30b_train_session23`。
- 执行 conservative 30B 脚本链路。原始 `run_local_data_prep.sh` 在 M0 阶段因 `prepare_m0_assets.py` 记录 2389 条 Hermes invalid source rows 返回 2 而中断；这些 rows 已进入 M0 manifest errors，M1 转换使用 valid rows 继续执行。
- 手动续跑 M1 与 packing：M1 输出 `983397` train rows、`11354` val-shadow rows、`errors=0`；Qwen3-30B tokenizer packing 输出 `665,777,436` tokens、`161757` packed train rows、`2552` valid rows。
- 重新运行 planner：0.5 epoch、GBS=8、MBS=1 计算得到 `train_iters=10110`；training plan 位于 `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_sft_strategy_conservative_v2/training_plan/task071_qwen30b_a3b_sft_strategy_conservative_v2/training_manifest.json`。
- 完成 `sync_to_nemtron.sh`：远端 run root 为 `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_sft_strategy_conservative_v2`，packed data 约 `3.9G`；NemTron 8 张 H200 在训练前为空闲。
- 首次 `run_nemtron_train.sh` 失败于 `tmux set-environment` 在无 tmux server 时触发 `set -e`；修复 planner 生成器为 `tmux set-environment ... 2>/dev/null || true`。
- 第二次启动失败于 Hydra struct：`scheduler.min_lr` 不是基础 YAML 字段；将 optional overrides 改为 Hydra `++` 语义。第三次启动显示 `scheduler.lr_decay_iters` 已存在，因此进一步保留 `++scheduler.lr_decay_iters` 覆盖逻辑。
- 发现 `min_lr` 最终应落到 `optimizer.min_lr` 而不是 `scheduler.min_lr`；修复 `plan_m1_agentic_sft_training.py`、`plan_qwen_scaleup_run.py` 和 Qwen local entry 的 min-lr 映射，重新生成 scripts 后重启训练。
- 当前 NemTron tmux session `task067_task071_qwen30b_a3b_sft_strategy_conservative_v2` 正常运行；最终 config 确认 `optimizer.lr=1e-6`、`optimizer.min_lr=1e-7`、`scheduler.lr_warmup_iters=100`、`scheduler.lr_decay_iters=10110`。
- 最新观测：训练到 iter `100/10110`，consumed samples `800`，LR `1.0e-6`，lm loss `0.4876802`，load_balancing_loss `1.508493`，无 skipped/nan；8 卡显存约 `81-88GB`，GPU util 正常。
- 新建 PR #153：`https://github.com/songCNMS/Nemotron/pull/153`，包含 local data prep exit-2 容错、tmux env 容错、Hydra `++` override 和 `optimizer.min_lr` 映射修复。
- 验证：`pytest -q tests/recipes/super3/test_m1_agentic_sft.py::test_plan_m1_torchrun_command_includes_strategy_overrides tests/recipes/super3/test_m1_agentic_qwen_scaleup_plan.py tests/recipes/super3/test_m1_agentic_sft.py::test_qwen30b_a3b_local_train_requires_env_var tests/recipes/super3/test_m1_agentic_sft.py::test_qwen30b_a3b_local_train_uses_env_var_when_set` -> `10 passed`；ruff touched files passed；`git diff --check` passed。

## Session 24

- 按“执行下一步”继续监控 NemTron conservative Qwen3-30B-A3B 训练到首个 eval/save 点；PR #153 当前仍 open 且 `mergeable=MERGEABLE`。
- 远端 tmux session `task067_task071_qwen30b_a3b_sft_strategy_conservative_v2` 持续运行；训练日志确认 `optimizer.lr=1e-6`、`optimizer.min_lr=1e-7`、`scheduler.lr_warmup_iters=100`、`scheduler.lr_decay_iters=10110`。
- iter `500/10110` 已完成：consumed samples `4000`，LR `9.964587e-7`，train lm loss `0.4050700`，load_balancing_loss `1.440887`，grad norm `0.759`，无 skipped/nan。
- iter 500 validation 完成：validation lm loss `0.3861638`，PPL `1.471326`；evaluate timing 记录在 train log 中。
- iter 500 checkpoint 保存成功：远端 checkpoint root `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_sft_strategy_conservative_v2/checkpoints`，`latest_checkpointed_iteration.txt=500`，存在 `iter_0000500`，目录大小约 `399G`。
- 训练在 checkpoint 后继续运行；最新观测到 iter `600/10110`，consumed samples `4800`，LR `9.944708e-7`，lm loss `0.3932771`，load_balancing_loss `1.426876`，无 skipped/nan；8 张 H200 显存约 `81-88GB` 且 GPU util 正常。

## Session 25

- 按“执行下一步”继续监控 NemTron conservative Qwen3-30B-A3B 训练；PR #153 当前 `state=OPEN`、`mergeable=MERGEABLE`，本轮保持 PR 打开以继续跟随完整 conservative run。
- 远端 tmux session `task067_task071_qwen30b_a3b_sft_strategy_conservative_v2` 持续运行；checkpoint root `/work-agents/intern_nemontron_code_reading/task071_sft_strategy_runs/task071_qwen30b_a3b_sft_strategy_conservative_v2/checkpoints` 的 `latest_checkpointed_iteration.txt=1500`，存在 `iter_0000500`、`iter_0001000`、`iter_0001500`。
- validation points：iter `500` loss/PPL `0.3861638` / `1.471326`，iter `1000` loss/PPL `0.4025858` / `1.495687`，iter `1500` loss/PPL `0.4071296` / `1.502499`。
- 最新解析到 train iter `1530/10110`；训练日志内 max skipped iterations `0`、max nan iterations `0`；8 张 H200 显存约 `81-88GB`，GPU util 正常。
- 生成当前训练健康 artifacts：`/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_sft_strategy_conservative_v2/metrics/train_loss_points.csv`、`validation_points.csv`、`health_summary.json`、`loss_validation_curve.png`。

## Session 26

- 按用户要求将 conservative Qwen3-30B-A3B loss 曲线返回到飞书；先从 NemTron 刷新 train log 并重生成本地 artifacts。
- 最新曲线覆盖 train iter `1670/10110`；validation points 仍为 iter `500` loss/PPL `0.3861638` / `1.471326`、iter `1000` loss/PPL `0.4025858` / `1.495687`、iter `1500` loss/PPL `0.4071296` / `1.502499`。
- 训练健康摘要：max skipped iterations `0`，max nan iterations `0`，saved checkpoints `[500, 1000, 1500]`。
- 飞书图片发送成功：`loss_validation_curve.png` 发往主管群 `oc_85148c845ddf7f30b7d7d7944596cccc`，image message id `om_x100b6e366d1830a4b3664059f07ff3f`，follow-up text message id `om_x100b6e366d3478e8b3ef574d8000f01`。
- 本地 artifacts 路径：`/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_sft_strategy_conservative_v2/metrics/loss_validation_curve.png`、`health_summary.json`、`train_loss_points.csv`、`validation_points.csv`。
