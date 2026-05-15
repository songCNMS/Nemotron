# Multi-Environment RL Post-Training 计划中文版（文本与 Agentic-only）

最后更新：2026-05-15

## 1. 背景与目标

这份计划基于当前 Nemotron 仓库中已经存在的 Super3 和 Nano3 post-training recipe。仓库里已经具备一条可以复用的后训练主线：

- Super3 路线：SFT -> 3 轮 RLVR -> 2 轮 SWE-RL -> RLHF -> Eval。
- RLVR 路线：多环境可验证奖励训练，覆盖数学、代码、STEM、安全、指令遵循、长上下文、工具使用、终端使用和 reasoning-gym 类任务。
- SWE-RL 路线：面向软件工程任务的 sandbox 交互式强化学习，包括 SWE-pivot 和完整 SWE-bench 风格的仓库修复环境。
- RLHF 路线：使用 GenRM 作为奖励模型做最终行为对齐。
- Infra 路线：已有 NeMo-RL、Ray、vLLM、NeMo-Gym、Megatron backend、W&B artifact lineage 和 nemo-runspec orchestration。

本版本明确不纳入多模态训练与评估，不考虑 Omni/MPO、vision RL、OCR、图表、视频、音频、ASR 或多模态 benchmark。计划范围只覆盖文本、代码、工具调用、软件工程、浏览器/搜索、终端、SQL、长上下文、多语言和安全/对齐。

本计划的目标是围绕 post-training 之后的 Multi-environment RL，建立一条从基础数据收集、环境构建、Agentic SFT、Agentic RL 到 Agentic RL Infra 的完整路线，并分成三个主要里程碑：

1. **M1：达到 Nemotron 3 Super 相当性能。**
2. **M2：持续提升，匹配 Qwen/Qwen3.5-122B-A10B。**
3. **M3：在 2026 年底匹配 Qwen/Qwen3.5-397B-A17B。**

## 2. 关键假设

- 起始 checkpoint 至少是 Super-class 的 pretraining/SFT 后模型。如果 base model 明显弱于这个等级，仅靠 post-training/RL 很难在年底前追平 Qwen3.5-397B-A17B。
- 训练资源需要支持 Super3 级别 RL：完整 async GRPO 需要数百到约 1K GPU；SWE、browser、GUI 等慢速环境需要单独容量。
- 性能目标不只看数学和代码，还要覆盖 agentic tool use、软件工程、chat/IF、长上下文、多语言、安全和开放式对齐能力；多模态能力不在本版本 scope 内。
- Qwen/Qwen3.5-122B-A10B 和 Qwen/Qwen3.5-397B-A17B 是外部对齐目标。最终 benchmark basket 需要在执行早期冻结，避免训练过程中反复移动目标。

## 3. 总体里程碑

| 时间 | 目标 | 核心工作 | 验收口径 |
|---|---|---|---|
| 2026-05-14 到 2026-07-31 | **M1：达到 Nemotron 3 Super-level performance** | 完成数据 inventory、license/质量标签、难度分桶和去重。复用 Super3 SFT 与 6-stage RL flow。搭建 21-env RLVR、SWE1/SWE2 sandbox、GenRM RLHF。Agentic SFT v0 覆盖 tool call、terminal、search、structured output 和 SWE traces。执行 small-run -> full RLVR -> SWE -> RLHF。 | 在 Super3 eval basket 上接近 Super3：MMLU-Pro、AIME/HMMT/GPQA、LiveCodeBench、TerminalBench、SWE-Bench、TauBench、IFBench/MultiChallenge、RULER、MMLU-ProX/WMT。目标是加权均分 within 1-2%，且没有关键类别大回退。 |
| 2026-08-01 到 2026-10-16 | **M2：匹配 Qwen/Qwen3.5-122B-A10B** | 环境扩到 35-50 个：browser/search、TauBench 多域、BIRD/SQL、TerminalBench v2、SWE multi-harness、多语言 IF/code、长上下文、安全、jailbreak、over-refusal。Agentic SFT v1 加入 multi-turn tool traces、自纠错和失败修复轨迹。RL 使用 curriculum、dynamic sampling 和 fast/slow env 分队列。加入 reward calibration、judge ensemble、rollout store 和 env health dashboard。 | 在选定 text/agentic/coding basket 上匹配 Qwen3.5-122B-A10B：MMLU-Pro、GPQA、HLE、LiveCodeBench、SWE-Bench Verified、IFBench、MultiChallenge、AA-LCR/LongBench、TerminalBench、TauBench。目标是加权 parity，关键单项 gap 不超过 3-5%。 |
| 2026-10-17 到 2026-12-31 | **M3：年底匹配 Qwen/Qwen3.5-397B-A17B** | 环境扩到 70-100+，rollout 规模提升到百万级以上。加入 GUI/MCP/browser、deep SWE、代码安全、long-horizon workplace assistant、多语言 agent、更难长上下文任务和更强安全/对齐任务。Agentic SFT v2 使用 M2 成功轨迹、负例修复、teacher reranking 和 GenRM reranking。最终 RL 分三波：高信号 RLVR、慢速 SWE/browser/GUI、最终 GenRM/RLHF。Infra 升级到 1K GPU-class async GRPO、env quota scheduler、sandbox pool、shadow eval 和自动回滚。 | 2026-12-31 前冻结最终 checkpoint。在约定 text/agent/coding basket 上匹配 Qwen3.5-397B-A17B，例如 BFCL、TAU2、VITA、DeepPlanning、Tool Decathlon、MCP-Mark、SWE-Bench、TerminalBench、HLE、GPQA、LiveCodeBench、长上下文和多语言评估。 |

## 4. 执行时间表

| 阶段 | 日期 | 交付物 |
|---|---:|---|
| Foundation | 2026-05-14 到 2026-05-31 | 数据目录、环境目录、冻结 eval basket、artifact/W&B lineage、sandbox/SIF 准备、Super3 dry-run 和 small-run。 |
| Agentic SFT v0 | 2026-06-01 到 2026-06-21 | tool、terminal、search、SWE trajectory SFT。统一 OpenAI responses/tool schema。确定 loss mask 和 reasoning mode 规范。 |
| M1 RL | 2026-06-22 到 2026-07-31 | RLVR1-3、SWE1-2、RLHF、Super3-parity checkpoint、regression report。 |
| M2 Environment Expansion | 2026-08-01 到 2026-08-31 | 新环境接入、失败样本挖掘、reward/judge calibration、rollout store、env health dashboard。 |
| M2 Training Sprint | 2026-09-01 到 2026-10-16 | 大规模 Agentic RL v1、Qwen3.5-122B-A10B parity checkpoint、gap analysis。 |
| M3 Expansion | 2026-10-17 到 2026-11-15 | GUI/browser/MCP/SWE/long-context/multilingual/safety 环境扩展、Agentic SFT v2。 |
| M3 Convergence | 2026-11-16 到 2026-12-31 | 最终 RLVR/SWE/browser/GUI/RLHF 训练、全量 eval、quantization/serving validation、checkpoint freeze。 |

## 5. 主训练流水线详解：SFT -> 3 轮 RLVR -> 2 轮 SWE-RL -> RLHF -> Eval

这一节展开主 post-training pipeline 中每个阶段的输入、输出、数据格式、算法和关键验收点。整体 artifact 流向如下：

| 阶段 | 输入 | 输出 | 主要算法/系统 | 目的 |
|---|---|---|---|---|
| SFT | `ModelArtifact-pretrain` + OpenAI chat/tool 数据 | `ModelArtifact-sft` + `SFTDataArtifact-sft` | Megatron-Bridge SFT，assistant-token next-token loss | 建立指令遵循、工具格式、agent 初始行为。 |
| RLVR 1 | SFT checkpoint + RLVR1 JSONL | RLVR1 checkpoint | Async GRPO + NeMo-Gym verifiable rewards | 从 SFT 模型开始做第一轮多环境可验证奖励对齐。 |
| RLVR 2 | RLVR1 checkpoint + RLVR2 JSONL | RLVR2 checkpoint | Async GRPO + second data blend | 继续强化难题、薄弱域和更高难度 curriculum。 |
| RLVR 3 | RLVR2 checkpoint + RLVR3 JSONL | RLVR3 checkpoint | Async GRPO + final RLVR blend | 稳定多环境能力，为慢速 SWE-RL 做准备。 |
| SWE-RL 1 | RLVR3 checkpoint + SWE1 JSONL | SWE1 checkpoint | Async GRPO + SWE-pivot/tool comparison | 从通用工具/代码能力过渡到软件工程任务。 |
| SWE-RL 2 | SWE1 checkpoint + SWE2 JSONL + sandbox images | SWE2 checkpoint | Async GRPO + OpenHands loop + test reward | 完整 repo 修复、patch 生成、测试执行。 |
| RLHF | SWE2 checkpoint + RLHF JSONL | final RL checkpoint | GRPO/RLHF + GenRM reward + KL penalty | 最终行为对齐，改善开放式回答、安全和交互质量。 |
| Eval | final checkpoint 或中间 checkpoint | eval report + W&B metrics | NeMo Evaluator + benchmark harnesses | 验证是否达到 M1/M2/M3 gate。 |

### 5.1 SFT：Supervised Fine-Tuning

**目标。** SFT 是 RL 前的行为初始化阶段。它让模型学会目标 chat template、工具调用格式、结构化输出、基础 agent 轨迹和领域任务解法。没有足够稳定的 SFT，后续 RL 会把大量采样预算浪费在格式错误、无效工具调用和无意义探索上。

**输入数据格式。** 当前 Super3 SFT recipe 使用 OpenAI chat 格式，数据集由 `config/data_prep/data_blend_raw.json` 定义，每个 dataset 记录 `name`、`path`、`split`、`weight` 等字段。单条样本的核心格式如下：

```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Solve the task ..."},
    {"role": "assistant", "content": "Here is the answer ..."}
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "run_python",
        "parameters": {"type": "object", "properties": {}}
      }
    }
  ],
  "used_in": ["super_v3"],
  "metadata": {
    "source": "dataset-name",
    "domain": "agentic_tool_use"
  }
}
```

`tools`、`used_in`、`metadata` 可按数据源变化；关键是 `messages` 必须能被 chat template 渲染。Super3 recipe 会用 `used_in_filter: super_v3` 选择训练样本。

**数据准备。** SFT data prep 使用 `SftPlanStage -> DownloadStage -> PackedSftParquetStage`：

1. 应用 `super3` chat template，把 system/user/assistant 分成带 role 的 chunks。
2. tokenize 成 `input_ids`，并保留 role boundaries。
3. 构造 `loss_mask`：system/user token 为 0，assistant token 为 1。
4. 按 `pack_size` 做 sequence packing，减少 padding 浪费。
5. 按 train/valid/test ratio 切分并写成 Parquet shards。

输出 Parquet 至少包含：

```text
input_ids      # packed token ids
loss_mask      # 仅 assistant tokens 参与 SFT loss
seq_start_id   # packed sequence 内每条原始样本的起点
```

**训练算法。** 主要是 supervised next-token prediction：对 `loss_mask=1` 的 assistant token 计算交叉熵 loss。Super3 文档中还描述了两阶段 SFT loss 思路：先做 token-level 行为学习，再做 sample-level 调整，以减少长短样本和不同任务形态带来的 loss 偏置。训练入口是 Megatron-Bridge 的 Super3 finetune recipe，输出 `ModelArtifact-sft`，供 RLVR1 使用。

**本计划中的 Agentic SFT 扩展。**

- v0：tool call syntax、terminal basics、search pattern、structured output、短 SWE trace。
- v1：multi-turn tool trace、observation 处理、自纠错、失败修复轨迹。
- v2：从高 reward rollout 中蒸馏成功轨迹，并加入 hard negative repair。

### 5.2 RL 通用数据格式与 NeMo-Gym 接口

RLVR、SWE-RL 和 RLHF 在当前 recipe 中最终都会变成 train/val JSONL。data prep 输出 `manifest.json`，并通过 `SplitJsonlDataArtifact` 注册 lineage。

JSONL 的单条记录会被 NeMo-Gym loader 读入，并作为 `extra_env_info` 传给具体 reward environment。不同环境字段不完全相同，但最小推荐结构如下：

```json
{
  "environment": "math_with_judge",
  "question": "What is ...?",
  "expected_answer": "42",
  "responses_create_params": {
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What is ...?"}
    ],
    "tools": []
  },
  "reward_config": {
    "verifier": "exact_or_judge",
    "max_score": 1.0
  },
  "metadata": {
    "source": "dataset-name",
    "difficulty": "hard",
    "split": "train"
  }
}
```

对不同环境，常见扩展字段包括：

- code/codegen：`test_cases`、`language`、`timeout`、`checker`。
- SWE：`instance_id`、`repo`、`base_commit`、`problem_statement`、`container_image` 或可映射到 SIF 的 image key。
- tool use：`tools`、`expected_tool_name`、`expected_arguments`、`argument_matcher`。
- SQL：`db_id`、`schema`、`expected_result`、`execution_timeout`。
- safety：`policy`、`risk_category`、`judge_model`。
- GenRM/RLHF：`principle`、`reference_answer`、`candidate_metadata`。

RL data prep 有两条路径：

- **Pipeline path：** RLVR 使用，处理带 `_hf_placeholder` 的记录，解析 DAPO/Skywork 等外部 Hugging Face 数据引用，然后输出 resolved JSONL。
- **Direct path：** SWE/RLHF 使用，直接读取本地 JSONL，按 `val_holdout` 从末尾切出 validation rows。

### 5.3 RLVR 1-3：Multi-Environment RL from Verifiable Rewards

**目标。** RLVR 是整个 RL 阶段的主干。它把多个可验证 reward environment 混合训练，避免模型只在单一环境上变强、同时在其他能力上回退。Super3 的 RLVR 覆盖数学、代码、STEM、IF、安全、长上下文、agentic tool use、terminal use 和 reasoning-gym 等环境。

**三轮设计。**

| 子阶段 | 输入 checkpoint | 数据 | 训练重点 | 输出 |
|---|---|---|---|---|
| RLVR 1 | SFT checkpoint | `rlvr1/train-split.jsonl` + `val-split.jsonl` | 从 SFT 开始建立多环境 reward 对齐，优先稳定格式、工具有效性和基础正确率。 | RLVR1 checkpoint |
| RLVR 2 | RLVR1 checkpoint | `rlvr2/train-split.jsonl` + `val-split.jsonl` | 加强难样本和薄弱环境，继续提升 math/code/STEM/tool/IF。 | RLVR2 checkpoint |
| RLVR 3 | RLVR2 checkpoint | `rlvr3/train-split.jsonl` + `val-split.jsonl` | 最终 RLVR 混合，降低跨域回退，准备进入慢速 SWE-RL。 | RLVR3 checkpoint |

**典型环境。** 当前配置中可见的环境/资源包括 `math_with_judge`、`code_gen`、`workplace_assistant`、`mcqa`、`instruction_following`、`structured_outputs_json`、`calendar`、`reasoning_gym`、`terminal_pivot`、`ns_tools`、`math_formal_lean`、`jailbreak_detection`、`over_refusal_detection`、`multichallenge`、`inverse_if`、`search_pivot_single_step_tool_use_with_argument_comparison`、`toolcall_schema_single_step_tool_use_with_argument_comparison` 等。

**算法：Async GRPO。**

1. vLLM generation workers 对每个 prompt 生成 `num_generations_per_prompt` 个候选。
2. NeMo-Gym 把候选送到对应 reward environment，得到 reward、工具调用有效性、verifier logs 和环境 metrics。
3. 对同一 prompt 的候选做 group-relative advantage 计算；可使用 normalized rewards、leave-one-out baseline、advantage clipping。
4. policy trainer 用 clipped policy gradient 更新模型，当前配置启用 token-level loss、importance sampling correction 和 ratio clipping。
5. training 与 inference 解耦：inference workers 持续生产 rollout，training workers 消费 rollout；in-flight weight updates 可在 rollout 过程中推送新权重。
6. RLVR/SWE 阶段通常设置 KL penalty 为 0；通过 ratio clipping、importance sampling 和多环境 eval gate 控制训练稳定性。

**Super3 级参数参考。**

| 参数 | RLVR 1-3 |
|---|---|
| Nodes | 109 |
| Prompts/step | 256 |
| Generations/prompt | 16 |
| Train batch size | 4096 |
| Max sequence length | 49K 到 65K |
| Learning rate | 3e-6 |
| KL penalty | 0 |
| Overlong filtering | false |

**关键监控。**

- 每环境 reward mean/std、pass@1、best@k。
- invalid tool call rate。
- malformed thinking rate。
- overlong rate。
- rollout latency、timeout、crash。
- policy lag、importance ratio、clip fraction。
- 每个 benchmark family 的 shadow eval 回归。

### 5.4 SWE-RL 1：SWE Pivot

**目标。** SWE-RL 1 是从通用 RLVR 过渡到完整软件工程 agent 的中间阶段。它更像 SWE-pivot 或单步/轻量多步工具比较任务：模型面对代码问题，需要生成解决方案或工具调用，reward 由 ground truth comparison、schema/tool argument comparison 或轻量代码执行给出。

**数据格式。** SWE1 使用本地 JSONL direct split，不需要 HF placeholder resolution。推荐样本结构：

```json
{
  "environment": "swe_pivot_single_step_tool_use_with_argument_comparison",
  "question": "Fix the following bug ...",
  "responses_create_params": {
    "messages": [
      {"role": "system", "content": "You are a coding agent."},
      {"role": "user", "content": "Problem statement ..."}
    ],
    "tools": []
  },
  "expected_answer": "patch or canonical solution",
  "reward_config": {
    "comparison": "argument_or_solution_match",
    "max_score": 1.0
  },
  "metadata": {
    "source": "swe1",
    "difficulty": "medium"
  }
}
```

实际字段可以随环境变化，但必须能让 NeMo-Gym 构造 prompt、运行比较逻辑并返回 reward。

**算法。** 仍使用 Async GRPO，但环境比普通 RLVR 更慢、更长。SWE1 的重点是提高代码修复、patch 表达、工具调用和问题定位能力，同时把上下文长度提升到 SWE 所需范围。

**Super3 级参数参考。**

| 参数 | SWE-RL 1 |
|---|---|
| Nodes | 64 |
| Prompts/step | 64 |
| Generations/prompt | 16 |
| Train batch size | 1024 |
| Max sequence length | 131K |
| Learning rate | 1e-6 |
| KL penalty | 0 |
| Overlong filtering | true |

### 5.5 SWE-RL 2：Full SWE-Bench / Repo Repair

**目标。** SWE-RL 2 是完整软件工程 agent 训练。模型需要在隔离 repo 环境中读代码、执行命令、修改文件、生成 patch，并用 ground-truth tests 得到 binary reward。

**数据格式。** SWE2 同样使用本地 JSONL direct split，但每条样本必须能定位一个隔离执行环境。推荐结构：

```json
{
  "environment": "swebench_openhands_training",
  "instance_id": "django__django-12345",
  "repo": "django/django",
  "base_commit": "abcdef123",
  "problem_statement": "Bug report or issue text ...",
  "responses_create_params": {
    "messages": [
      {"role": "system", "content": "You are a software engineering agent."},
      {"role": "user", "content": "Resolve this issue in the repository."}
    ]
  },
  "container": {
    "formatter": "swebench_sweb.eval.x86_64.{instance_id}.sif"
  },
  "reward_config": {
    "test_command": "run ground-truth tests",
    "reward_type": "binary_pass_fail"
  },
  "metadata": {
    "source": "swebench_or_r2egym",
    "harness": "openhands"
  }
}
```

**环境执行流程。** OpenHands-style agent loop 负责：

1. 初始化隔离 runtime。
2. 向模型展示 problem statement。
3. 运行 agent step loop，最多可到 200 turns。
4. 通过 bash/file operations 与 repo workspace 交互。
5. 提取 git patch。
6. 运行 ground-truth tests。
7. 根据测试是否通过给 binary reward。
8. 清理环境并记录日志。

**Sandbox 与容器。**

- SLURM/HPC 场景常用 Apptainer/SIF；每个 `instance_id` 映射到对应 `.sif` image。
- Docker/Podman 也可用，但需要 root 或相应容器权限。
- 需要 memory watchdog 和 command blocklist，防止 runaway process 或危险命令影响训练节点。
- OpenHands 中可以接入 OpenCode/Codex agent classes，提供 harness diversity，避免模型只适配单一工具格式。

**算法。** 仍是 Async GRPO，但 reward 变成昂贵的 binary pass/fail，rollout 长度和环境 latency 显著增加。实践上需要独立队列、较低 prompts/step、更高 generations/prompt、长上下文和严格 timeout。

**Super3 级参数参考。**

| 参数 | SWE-RL 2 |
|---|---|
| Nodes | 64 |
| Prompts/step | 16 |
| Generations/prompt | 32 |
| Train batch size | 512 |
| Max sequence length | 196K |
| Learning rate | 1e-6 |
| KL penalty | 0 |
| Overlong filtering | true |
| Agent max turns | 200 |
| Agent concurrency | 768 |
| Agent timeout | 3600s |

### 5.6 RLHF：GenRM-Based Final Alignment

**目标。** RLHF 是最后的行为对齐阶段，重点不是继续刷单一可验证任务，而是改善开放式回答质量、原则遵循、安全边界、拒答合理性、工具使用礼貌性和交互体验，同时尽量保持 RLVR/SWE 获得的能力。

**数据格式。** RLHF 数据仍是 JSONL direct split。样本通常包含 prompt、可选 reference/principle、GenRM 所需 judge instruction，以及工具比较任务所需字段：

```json
{
  "environment": "genrm_compare",
  "responses_create_params": {
    "messages": [
      {"role": "system", "content": "Follow the user instruction carefully."},
      {"role": "user", "content": "Open-ended user request ..."}
    ]
  },
  "principle": "Evaluate helpfulness, correctness, relevance, concision, safety ...",
  "reference_answer": "Optional reference or rubric anchor",
  "reward_config": {
    "judge": "genrm_compare",
    "length_penalty": true
  },
  "metadata": {
    "source": "helpsteer_or_preference_data",
    "domain": "chat_alignment"
  }
}
```

**奖励。**

- `genrm_compare`：GenRM 先生成或参考自己的判断，再做 pairwise/quality comparison。
- `single_step_tool_use_with_argument_comparison`：继续约束工具调用正确性，避免 RLHF 后 tool-use 退化。
- 可加入 length penalty，避免开放式任务中生成冗长但低价值的回答。

**算法。** 使用 GRPO/RLHF 风格训练，但与 RLVR/SWE 的关键区别是引入 KL penalty。Super3 文档中的 RLHF KL penalty 为 `1e-4`，用于限制 final model 不要偏离 reference policy 太远，减少能力漂移。

**Super3 级参数参考。**

| 参数 | RLHF |
|---|---|
| Nodes | 72 |
| Prompts/step | 128 |
| Generations/prompt | 16 |
| Train batch size | 2048 |
| Max sequence length | 49K |
| Learning rate | 1e-6 |
| KL penalty | 1e-4 |
| Overlong filtering | false |
| GenRM router DP size | 8 |

### 5.7 Eval：Benchmark Evaluation and Promotion Gate

**目标。** Eval 是每个 checkpoint promotion 的硬门槛。它不参与训练，只负责验证模型是否达到 M1/M2/M3 的目标，并检测回退、reward hacking 和格式漂移。

**输入与执行。**

- 输入 checkpoint：可以是 SFT、RLVR1/2/3、SWE1/2、RLHF final。
- 部署：通过 NeMo Evaluator / nemo-evaluator-launcher，把模型部署成 OpenAI-compatible endpoint 或 NeMo Ray deployment。
- 配置：eval YAML 指定 deployment、tasks、parallelism、export/W&B。
- 输出：W&B metrics、eval report、per-task logs、regression summary。

**评估类别。**

| 类别 | 代表 benchmark |
|---|---|
| General Knowledge | MMLU-Pro |
| Reasoning | AIME25、HMMT、GPQA、HLE |
| Coding | LiveCodeBench、SciCode |
| Agentic | TerminalBench、TauBench、BrowseComp、BIRD、BFCL、MCP-Mark、Tool Decathlon |
| SWE | SWE-Bench OpenHands/OpenCode/Codex harness、SWE-Bench Verified、多语言 SWE |
| Chat/IF | IFBench、MultiChallenge、Arena-Hard-style prompts |
| Long Context | AA-LCR、RULER 256K/512K/1M |
| Multilingual | MMLU-ProX、WMT24++ |

**promotion gate。**

- M1：加权均分达到 Super3 parity，且关键类别无大回退。
- M2：选定 basket 上匹配 Qwen3.5-122B-A10B，关键单项 gap 控制在 3-5% 内。
- M3：年底 checkpoint 在 text/agent/coding basket 上匹配 Qwen3.5-397B-A17B；本版本不设置多模态 gate。
- 任何阶段如果出现 SWE、tool validity、安全、长上下文、多语言等关键指标明显回退，应触发 rollback 或重新调 mix。

## 6. 工作流 1：基础数据收集、梳理与创建

目标是建立统一的数据资产层，让 SFT、RL、评估和失败样本回流能够共享同一套元数据。

需要完成：

- 建立统一 data registry，记录 source、license、domain、difficulty、format、tool requirements、reward type、contamination risk 和 eval overlap。
- 将 SFT 数据归一到 OpenAI chat/responses 格式，显式保留 tool schema、tool output 和 role-based loss mask。
- 将 RL 数据归一到 NeMo-Gym-compatible JSONL，包含 `responses_create_params`、expected answer 或 verifier metadata、environment name 和 reward config。
- 建立 difficulty curriculum：先用当前 SFT 模型过滤掉稳定做对的样本，再按 pass rate、judge confidence、rollout length 排序。
- 每个环境维护 train/dev/shadow-eval split，避免 reward overfitting。
- 将 M1/M2 失败 rollout 回流为 SFT repair data 和 RL replay candidate。

## 7. 工作流 2：交互式 RL 环境构建

初始环境族：

| 环境族 | 说明 | 奖励信号 |
|---|---|---|
| Math/Formal Reasoning | 数学题、Python tool 辅助解题、Lean/formal proof verification。 | 答案匹配、程序执行结果、形式化证明验证。 |
| Code Generation | 竞赛编程、单元测试执行、代码 critique、repair。 | 测试通过率、隐藏测试、judge score。 |
| SWE | SWE-pivot、SWE-bench-style repo repair、OpenHands/OpenCode/Codex 多 harness。 | patch 是否通过目标测试、任务是否解决。 |
| Tool Use | 单步/多步 function calling、argument comparison、schema adherence。 | tool call 是否有效、参数是否正确、最终结果是否满足任务。 |
| Search/Browser | web retrieval、BrowseComp-style browsing、grounded QA。 | 答案正确性、引用/证据匹配、浏览路径有效性。 |
| Terminal/Workplace Assistant | shell task、calendar/workplace API、多轮事务任务。 | 状态变更是否正确、命令是否安全、任务是否完成。 |
| SQL/Data | BIRD/text-to-SQL、data science notebook/script execution。 | SQL execution accuracy、结果表匹配、脚本输出正确性。 |
| Safety/Robustness | jailbreak detection、over-refusal reduction、safe tool use。 | 安全 judge 分数、拒答合理性、危险 tool use 惩罚。 |
| Long Context | 长文档检索、长上下文 reasoning、memory-heavy agent workflow。 | 检索命中、答案 groundedness、长上下文任务正确率。 |
| Multilingual | 多语言 IF、code、translation、本地化 tool-use。 | 多语言 benchmark 分数、任务成功率。 |

每个环境都必须定义：

- reward range。
- pass/fail semantics。
- timeout 和 max turns。
- 需要的 tools 和 sandbox type。
- 预期 runtime。
- 常见 failure modes。
- local small-run mode。
- health check。
- telemetry。
- held-out shadow eval split。

fast environments 可以混在 RLVR 中统一训练；SWE、browser、GUI 等 slow environments 应该单独排队或单独 stage 训练。

## 8. 工作流 3：Agentic SFT

### Agentic SFT v0

- 训练 tool-call syntax、terminal basics、search pattern、structured output 和短 SWE traces。
- 保持现有 reasoning mode 与 chat template 一致。
- 加入 malformed tool call、hallucinated tool output 等负例。
- 目标是让模型具备稳定的工具格式、基本交互能力和初始 agent 行为。

### Agentic SFT v1

- 加入 multi-turn tool traces、自纠错、环境 observation 处理、失败后修复轨迹。
- 加入 cross-harness SWE traces，避免模型过拟合单一 agent loop。
- 加入 compact reasoning / low-effort variants，用于低延迟任务。
- 目标是让模型能稳定处理多轮环境反馈，而不是只会一次性回答。

### Agentic SFT v2

- 蒸馏 M2 中高质量成功轨迹。
- 将 high-reward rollout 过滤后转成 supervised traces。
- 加入 SWE/browser/tool 失败的 hard negative repair。
- 使用 teacher 或 GenRM reranking 选出简洁、鲁棒的轨迹。
- 目标是在 M3 之前提升复杂 agent 任务的先验行为，降低 RL 探索成本。

## 9. 工作流 4：Agentic RL

### M1 RL

- 复现 Super3-style RL flow：RLVR1 -> RLVR2 -> RLVR3 -> SWE1 -> SWE2 -> RLHF。
- 第一目标是打通 full stack，并避免某个类别提升时其他类别大幅回退。
- 跟踪 reward distribution、pass@1、best@k、rollout length、tool-call validity、overlong rate、KL/drift。

### M2 RL

- 按 environment gap 做 dynamic sampling。
- 将 fast verifiable RLVR 与 slow SWE/browser queue 分离。
- 为非二值 reward 引入 judge ensemble 和 calibration。
- 加 per-environment quota，避免高吞吐环境主导梯度。
- 把失败样本自动写入 rollout store，供下一轮 SFT/RL replay 使用。

### M3 RL

- 按 curriculum 分波训练：高置信 verifiable rewards -> 慢速 agentic tasks -> 最终 GenRM/RLHF。
- 每次 checkpoint promotion 前都跑 shadow eval。
- 对 SWE、tool validity、安全、长上下文、多语言等关键类别设置 rollback rule。
- 最终阶段使用 KL 和 GenRM 控制行为漂移。

## 10. 工作流 5：Agentic RL Infra

### M1 必需 infra

- 验证 NeMo-RL/Ray/vLLM/NeMo-Gym launch path 的 small 和 full scale 路径。
- 准备 code execution、Lean/formal、terminal、SWE 所需 sandbox container。
- 准备 SWE container，包含 prefetched venvs 和 SIF/Docker/Podman image support。
- 对 raw data、prepared data、model checkpoint 和 eval report 建立 W&B/artifact lineage。
- 基础环境 telemetry：reward、latency、timeout、crash、invalid tool call、malformed reasoning、overlong stats。

### M2 必需 infra

- Central rollout store：保存 prompt、response、environment observation、reward、verifier logs、model version。
- Environment scheduler：支持 quota、backpressure、fast/slow queue 分离。
- Judge service pool：支持 model versioning 和 calibration set。
- 自动 contamination check 和 eval-overlap report。
- Canary 与 shadow-eval pipeline，用于每个 promoted checkpoint。

### M3 必需 infra

- 1K GPU-class async GRPO，包含 training/inference 解耦、policy-lag monitoring 和 automatic recovery。
- Sandbox pool manager：管理 SWE/browser/GUI 的 resource limit、timeout、filesystem isolation 和 artifact capture。
- Environment replay/debug UI：用于定位失败 rollout。
- Automatic checkpoint promotion/rollback gates。
- BF16 与量化候选的 serving validation。

## 11. Evaluation Gates

每个 milestone 都应该产出：

- 一个 frozen checkpoint。
- 一份完整 eval report。
- 一份相对上一 checkpoint 的 regression report。
- 每个 environment 的 training metrics 和 reward health。
- 一份 data lineage report，列出所有 dataset、filter 和 generated sample。
- 一份 known-gap list，包含 owner 和 next action。

建议 benchmark families：

| 类别 | Benchmarks |
|---|---|
| General Knowledge | MMLU-Pro |
| Reasoning | AIME25、HMMT、GPQA、HLE |
| Coding | LiveCodeBench、SciCode、competitive programming pass@k |
| Agentic | TerminalBench、TauBench、BrowseComp、BIRD、BFCL、MCP-Mark、Tool Decathlon |
| SWE | SWE-Bench Verified、SWE-Bench multi-harness、multilingual SWE |
| Chat/IF | IFBench、MultiChallenge、Arena-Hard-style prompts |
| Long Context | AA-LCR、RULER 256K/512K/1M、long-document QA |
| Multilingual | MMLU-ProX、WMT24++、multilingual IF/code/tool tasks |

## 12. 风险与缓解

| 风险 | 影响 | 缓解策略 |
|---|---|---|
| Base checkpoint 能力不足 | RL 无法补齐到 397B-class target | 增加强 teacher distillation、延长 SFT，或在 M2 前调整目标范围。 |
| Reward hacking | 训练 reward 上升但真实 eval 不涨 | 使用 held-out shadow eval、judge ensemble、adversarial checks、reward audit set。 |
| 慢环境拖垮吞吐 | RL wall clock 过长，训练效率下降 | slow queue/stage 单独训练，使用 replay buffer，限制 per-env quota，优化 sandbox pool。 |
| SWE/browser sandbox 不稳定 | 训练中断、reward 噪声大 | health check、memory watchdog、command blocklist、retry policy、per-env failure accounting。 |
| Tool-call format drift | Agentic benchmark 回退 | 保持 tool syntax SFT replay、invalid-tool penalty、schema-specific eval gate。 |
| RL 后类别回退 | 某些能力提升但其他能力下降 | multi-environment mixing、per-category eval gate、rollback rule、final GenRM/RLHF with KL。 |
| 数据污染或 eval leakage | benchmark 结论失效 | 数据 provenance、eval 去重、早期冻结 eval holdout。 |

## 13. Terms 术语说明

| Term | 中文说明 |
|---|---|
| Post-training | 预训练之后的训练阶段，通常包括 SFT、RLHF、RLVR、DPO、distillation 等，用来提升指令遵循、推理、工具使用和安全性。 |
| SFT | Supervised Fine-Tuning，监督微调。用高质量标注或合成样本训练模型按照目标格式和行为回答。 |
| Chat Template | 聊天模板。把 `system/user/assistant/tool` 等角色消息渲染成模型实际看到的 token 序列。 |
| Loss Mask | 损失掩码。SFT 中常让 system/user token 的 loss 为 0，只让 assistant token 参与训练。 |
| Packed Parquet | 打包后的 Parquet 训练数据。多个短样本被拼进固定长度 token block，提升训练吞吐并减少 padding。 |
| Next-token Loss | 下一个 token 预测损失。SFT 中最常见的交叉熵训练目标。 |
| Cross Entropy | 交叉熵损失。衡量模型预测 token 分布与目标 token 的差距。 |
| Agentic SFT | 面向 agent 行为的 SFT。数据通常包含多轮工具调用、环境 observation、命令执行、错误修复和最终答案。 |
| RL | Reinforcement Learning，强化学习。模型在环境中生成行为，环境返回 reward，模型用 reward 更新策略。 |
| Agentic RL | 面向 agent 任务的 RL。模型不是只回答问题，而是需要调用工具、浏览网页、操作终端、修改代码或执行多步任务。 |
| Multi-environment RL | 多环境强化学习。训练时同时或分阶段混合多个 reward environment，避免模型只在单一任务上过拟合。 |
| RLVR | Reinforcement Learning from Verifiable Rewards，可验证奖励强化学习。reward 来自明确 verifier，例如答案匹配、代码测试、SQL 执行结果、形式化证明验证。 |
| RLHF | Reinforcement Learning from Human Feedback，人类反馈强化学习。通常用 reward model 或 preference model 近似人类偏好，再用于 RL。 |
| GRPO | Group Relative Policy Optimization。一类不依赖传统 value model 的策略优化方法，对同一 prompt 的多条生成进行组内相对比较来估计 advantage。 |
| Async GRPO | 异步 GRPO。生成 rollout 和训练更新解耦，inference workers 持续生成，training workers 持续消费，适合大规模 GPU 训练。 |
| Policy Gradient | 策略梯度。强化学习中直接优化模型生成策略的梯度方法。GRPO 属于这类策略优化范式。 |
| Ratio Clipping | 比率裁剪。限制新旧策略概率比的范围，避免一次 RL 更新过大。 |
| Importance Sampling Correction | 重要性采样修正。异步 rollout 使用旧策略生成时，用概率比修正训练目标，降低 off-policy 偏差。 |
| Leave-one-out Baseline | 留一基线。对同一 prompt 的多条候选，计算某条候选 advantage 时用其他候选的平均 reward 作为基线。 |
| Token-level Loss | token 级损失。RL 更新时对每个 token 的 logprob/ratio 计算损失，而不是只对整条序列给一个标量损失。 |
| Rollout | 模型在某个 prompt/environment 中完整执行一次得到的轨迹，包括生成内容、工具调用、环境反馈、reward 和日志。 |
| Trajectory | 与 rollout 类似，强调多步行为序列，例如 plan -> tool call -> observation -> repair -> final answer。 |
| DatumSpec | NeMo-RL 内部的数据结构，用来承载一条训练样本的 message log、token ids、task name 和 `extra_env_info`。 |
| extra_env_info | NeMo-Gym 传给具体环境的样本元数据，通常包含 question、expected answer、环境参数、reward config 等。 |
| Reward Environment | 奖励环境。负责接收模型输出、执行工具或验证逻辑，并返回 reward、metadata 和错误信息。 |
| Verifier | 验证器。用于判断输出是否正确，例如数学答案 checker、unit tests、SQL executor、schema validator。 |
| Binary Reward | 二值奖励。常见于 SWE-Bench/code execution，测试通过给 1，否则给 0。 |
| Reward Model | 奖励模型。用模型预测人类偏好或回答质量，输出 reward score。 |
| GenRM | Generative Reward Model，生成式奖励模型。它通常先生成评价或参考答案，再比较候选回答，适合难以写规则 verifier 的开放式任务。 |
| KL Penalty | KL 惩罚项。限制 RL 后模型不要偏离 reference policy 太远，减少能力漂移和行为失控。 |
| Reference Policy | 参考策略。通常是 RL 开始前的 SFT 或上一阶段 checkpoint，用于计算 KL 或做对比。 |
| Policy Lag | 策略滞后。异步训练中，rollout 使用的模型权重可能落后于最新训练权重。policy lag 太大可能导致训练不稳定。 |
| Advantage | 强化学习里的优势值，表示某个动作/回答相对基线有多好。GRPO 中常用组内相对 reward 计算。 |
| Dynamic Sampling | 动态采样。根据模型在各环境上的表现、训练缺口、reward 稳定性和吞吐动态调整采样比例。 |
| Prompt/Step | 每个 RL training step 采样的 prompt 数量。 |
| Generations/Prompt | 每个 prompt 生成的候选数量。GRPO 需要多个候选来做组内相对比较。 |
| Curriculum | 课程学习。按难度或训练阶段组织数据，从简单/高置信任务逐步转向更难任务。 |
| Pass@1 | 单次生成的通过率。常用于代码、SWE、数学等 benchmark。 |
| Best@K | 生成 K 个候选后取最好结果的指标或训练信号。可衡量模型搜索空间里是否存在正确解。 |
| Overlong | 输出过长或超过最大 token/turn 限制。RL 中常需要惩罚 overlong，避免模型用冗长推理刷 reward。 |
| Low-effort Reasoning | 低推理预算模式。要求模型用更少 token 得出正确答案，适合低延迟和成本敏感场景。 |
| Tool Calling | 工具调用。模型输出结构化函数调用，由外部系统执行，再把结果返回给模型。 |
| Tool Schema | 工具的参数结构定义，通常是 JSON schema。模型必须按 schema 调用工具。 |
| responses_create_params | RL JSONL 中常用的字段，描述 OpenAI-style response/chat 创建参数，例如 messages、tools、tool choice 等。 |
| Structured Output | 结构化输出，例如 JSON、XML、表格或特定字段格式。 |
| MCP | Model Context Protocol，一种连接模型与外部工具/资源的协议生态。这里作为 agent 工具接入和 benchmark 方向。 |
| BFCL | Berkeley Function Calling Leaderboard，函数调用/工具调用能力评测。 |
| NeMo-RL | NVIDIA NeMo 的 RL 训练框架，用于 GRPO/RLHF 等大规模后训练。 |
| NeMo-Gym | 多环境 reward evaluation 层，负责管理 reward environment、resource server、agent server 等。 |
| Ray | 分布式执行框架，用于调度训练、推理、环境和 judge 服务。 |
| vLLM | 高吞吐 LLM inference engine，用于 rollout generation。 |
| Megatron | 大规模模型训练框架。这里主要指 Megatron-Core/Megatron-Bridge 相关训练后端。 |
| W&B | Weights & Biases，用于实验追踪、指标记录和 artifact 管理。 |
| Artifact Lineage | 数据、模型、评估结果之间的血缘关系。用于追踪某个 checkpoint 使用了哪些数据和配置。 |
| Sandbox | 沙盒执行环境。隔离运行代码、终端命令或浏览器任务，避免影响训练节点和宿主系统。 |
| Apptainer/SIF | HPC/SLURM 常用的容器方案。SIF 是 Apptainer 镜像格式，适合无 root 权限的集群环境。 |
| SWE-RL | 面向软件工程任务的 RL，模型需要读 repo、改代码、跑测试并得到 reward。 |
| SWE-Bench | 软件工程 benchmark，任务通常来自真实 GitHub issue，目标是生成 patch 并通过测试。 |
| SWE-pivot | SWE-RL 的较轻量阶段，常用于从简单代码修复或单步 tool use 过渡到完整 SWE-Bench。 |
| OpenHands | Agent loop/软件工程 agent 框架，能管理 repo 初始化、工具调用、patch 提取和测试执行。 |
| Harness | 评测或训练执行框架。不同 harness 可能有不同工具格式、agent loop 和 reward 计算方式。 |
| TerminalBench | 终端使用 benchmark，评估模型在 shell/terminal 环境中完成任务的能力。 |
| TauBench | 多轮工具使用/事务型 agent benchmark，常见领域包括 airline、retail、telecom。 |
| BrowseComp | 浏览器/网页检索理解任务，要求模型通过浏览和检索得到答案。 |
| BIRD | Text-to-SQL benchmark，通常用 SQL 执行正确性衡量结果。 |
| IFBench | Instruction Following benchmark，评估模型遵循复杂指令的能力。 |
| MultiChallenge | 多约束复杂指令 benchmark，考察同时满足多个要求的能力。 |
| MMLU-Pro | 更难版本的多学科知识 benchmark。 |
| GPQA | 研究生级科学问答 benchmark，常用于衡量高难推理和专业知识。 |
| AIME/HMMT | 高难数学竞赛 benchmark。 |
| HLE | Humanity's Last Exam，覆盖广泛且难度高的综合推理评测。 |
| LiveCodeBench | 代码能力 benchmark，使用较新的竞赛编程题以降低污染风险。 |
| SciCode | 科学编程 benchmark，偏科学计算和代码推理。 |
| RULER | 长上下文检索与推理 benchmark，可测试 256K、512K、1M 等上下文长度。 |
| AA-LCR | 长上下文 reasoning benchmark，用于衡量长文档或长上下文下的推理能力。 |
| MMLU-ProX | 多语言 MMLU-Pro 风格 benchmark。 |
| WMT24++ | 机器翻译 benchmark，评估多语言翻译能力。 |
| Shadow Eval | 影子评估。训练中不用于调参的 held-out evaluation，用来检测真实泛化和 reward hacking。 |
| Canary | 小规模预警评估或灰度 checkpoint，用于在大规模训练/推广前发现明显回退。 |
| Checkpoint Promotion | 将某个 checkpoint 晋升为下一阶段训练输入或候选发布模型。 |
| Rollback Rule | 回滚规则。如果关键 eval 或安全指标回退超过阈值，则放弃当前 checkpoint 或回退到上一版本。 |
| Reward Calibration | 奖励校准。让不同 judge、不同环境和不同 reward scale 的分数更可比较。 |
| Judge Ensemble | 多个 judge/verifier/reward model 组合，降低单个 judge 偏差或被 reward hacking 的风险。 |
| Contamination Check | 数据污染检查。检测训练数据是否与 eval benchmark 重叠，避免虚高结果。 |
| Eval Basket | 一组固定评测集合，用于代表目标能力面。应在 milestone 早期冻结。 |
| Parity | 性能持平。通常指在选定 benchmark basket 上与目标模型加权均分相当，且关键单项没有明显落后。 |
