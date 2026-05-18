# task018 - task_knowledge

## stage3_rlhf layout

`stage3_rlhf/config/default.yaml` 关键值：

```
nemo_gym.config_paths:
  - responses_api_models/vllm_model/configs/vllm_model_for_training.yaml
  - resources_servers/genrm_compare/configs/genrm_compare.yaml
  - resources_servers/single_step_tool_use_with_argument_comparison/
      configs/single_step_tool_use_with_argument_comparison.yaml

reference_policy_kl_penalty: 1.0e-4           # plan §5.6 acceptance
reference_policy_kl_type: "k3"                # Schulman k3 estimator
use_kl_in_reward: false                       # KL as loss, not reward

genrm_compare.comparison_strategy: circular
genrm_compare.num_judges_per_comparison: 1
genrm_compare.use_principle: true
genrm_compare.aggregator_method: simple_tiebreaker
genrm_compare.reasoning_bonus: 0.5
genrm_compare.answer_bonus: 0.5
genrm_compare.top_percentile: 0.2
genrm_compare.group_*_penalty_coeff: 0.3 / 0.35 / 0.05
genrm_compare.default_score: 3.0
genrm_compare.default_ranking: 3.5

genrm_model.model: "/path/to/genrm_model"     # placeholder
genrm_model.spinup_server: true
genrm_model.router_dp_size: 8
genrm_model.server_args.tensor_parallel_size: 8
genrm_model.server_args.max_model_len: 60000
genrm_model.server_args.reasoning_parser: deepseek_r1
```

GenRM 模型默认是 `nvidia/Qwen3-Nemotron-235B-A22B-GenRM-2603`（在
stage1_rlvr/config/default.yaml 那边看得到，stage3_rlhf 留 placeholder
让 cluster ops 填）。

## KL trio (plan §5.6)

| Key | Value | 语义 |
|---|---|---|
| `reference_policy_kl_penalty` | 1.0e-4 | KL 系数，小 = 让 policy 自由偏离 reference |
| `reference_policy_kl_type` | "k3" | Schulman k3 估计器（无偏，方差低） |
| `use_kl_in_reward` | false | KL 作为 *loss penalty*（separate gradient），不折进 reward signal |

为什么 `use_kl_in_reward=false` 重要：
- 如果 KL 折进 reward，GenRM 的 reward signal 会跟 KL signal 互相竞争，
  policy 同时优化两个有时矛盾的目标
- 折成 loss penalty 让 KL 走独立 gradient path，GenRM reward 还是干净的
  preference signal

`test_rlhf_kl_invariants.py` 直接读 default.yaml 断言这三个值。任何 PR 改
一个值都在 sandbox 上 fail。

## Pref data 候选

| Candidate | HF dataset | License | Pair 形式 | 备注 |
|---|---|---|---|---|
| `helpsteer2` | nvidia/HelpSteer2 | cc-by-4.0 | 推导 (helpfulness + coherence aggregate) | 默认 primary，NVIDIA-authored |
| `ultrafeedback` | openbmb/UltraFeedback | mit | 推导 (4 critic LLM aggregate) | 大 (64K × 4)，secondary blend |
| `distilabel_orca_pairs` | argilla/distilabel-intel-orca-dpo-pairs | apache-2.0 | 直 (chosen + rejected columns) | 小 ~13K，backup |

CC-BY-4.0 license 要 attribution，不传染（vs CC-BY-SA-4.0 share-alike），
所以 HelpSteer-2 不像 Lean (math_formal_lean，task056 Session 2 卡在
share-alike) 那样卡法务。

## Session 2 converter shape

每行 M0 RLHF JSONL：

```json
{
  "environment": "rlhf_helpsteer2",
  "milestone": "M0",
  "question": "<pref prompt>",
  "expected_answer": "A" or "B",        // preference label
  "responses_create_params": {
    "input": [{"role": "system", ...}, {"role": "user", "content": "<pref prompt>"}],
    "tools": []
  },
  "reward_config": {"verifier": "genrm_compare"},
  "extra_env_info": {
    "completion_a": "<chosen completion>",
    "completion_b": "<rejected completion>",
    "preference_label": "A",
    "source_prompt_id": "<helpsteer2 row id>"
  },
  "metadata": {
    "source_dataset": "nvidia/HelpSteer2",
    "hf_revision": "<pinned commit>",
    "license": "cc-by-4.0",
    "license_attribution": "HelpSteer2 — Nvidia 2024, CC-BY-4.0"
  }
}
```

Active 之后 bridge `tag_record` 加 `pref_dataset: helpsteer2`，
`nemo_gym_env: genrm_compare`，`nemo_gym_mix: rlhf`。

## Tool-call validity pairing (Session 2 第二条)

plan §5.6 那条 "tool-call-validity check still passes" — RLHF 阶段 policy
不光要在 prefs 上得高分，还得继续 emit 合法 tool call。

Pairing harness 设计：
- 把 HelpSteer-2 prompts 加一组 tool schema (从 M0 hermes singleturn 取通用集)
- Policy 既要 maximize GenRM reward 又要在 tool-call validity 上不掉
- bridge JSONL 出两类行（或一类带双 verifier）：
  1. 纯 pref pair（verifier = genrm_compare）
  2. tool-call validity pair（verifier = argument_match，跟 M0 hermes 走同款）
- NeMo-Gym 端 router 按 row 的 `nemo_gym_env` 路由

具体 pairing 算法（cross-product? round-robin? interleave?）Session 2 定。

## Bridge auto-pickup

Session 2 落 M0 RLHF env (e.g. `rlhf_helpsteer2`)，registry 改一行：

```yaml
- nemo_gym_env: genrm_compare
  mix: rlhf
  m0_env_id: rlhf_helpsteer2           # 之前 null
  status: active                        # 之前 blocked_external
  pref_dataset_candidate: helpsteer2
  ...
```

`prepare_m1_rlhf_jsonl.py` import 时自动 pickup；`tag_record` 从
`_m0_env_to_pref_dataset` lookup 查到 `pref_dataset: helpsteer2` 加进每行。
`test_prepare_happy_path_with_synthetic_active_registry` 覆盖这条路径。

## Sandbox vs cluster

| 任务 | sandbox? |
|---|---|
| RLHF env registry + pref data candidate registry + bridge | yes |
| KL invariant pytest | yes |
| Session 2 converter unit tests (synthetic HelpSteer-2 rows) | yes |
| Session 2 真 HF 下载 + 全量 convert | partial |
| Session 3 部署 GenRM judge model | no — cluster + GPUs |
| Session 4 端到端 smoke from SWE2 checkpoint | no |

## Four-bridge code duplication

| | m1_rlvr | m1_swe1 | m1_swe2 | m1_rlhf |
|---|---|---|---|---|
| Mixes | 3 | 1 | 1 | 1 |
| NeMo-Gym targets | 21 | 1 | 1 | 2 |
| Module-specific tag | (none) | (none) | sif_source | pref_dataset |
| Module-specific coverage | (none) | (none) | sif_source_breakdown | pref_dataset_breakdown + known_pref_candidates |
| Second registry | (none) | (none) | sif_registry | pref_data_registry |
| Plan-conformance pytest | (none) | (none) | (none) | KL invariants |

task017 Session 4 抽 `_bridge_base.py` 的时候 4 个 module 都摆稳了，抽出
基础 scaffolding 然后让每个 module 加 module-specific hook（`tag_record`
extra fields、`coverage_report` extra fields）。

## Pre-existing sandbox issue

`tests/recipes/super3/test_m1_agentic_sft.py` 在 sandbox 仍因缺 pyarrow
collect-error，pre-existing；非 sandbox 正常跑。
