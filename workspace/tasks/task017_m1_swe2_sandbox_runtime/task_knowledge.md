# task017 - task_knowledge

## stage2_swe2 layout

`stage2_swe2/config/default.yaml::nemo_gym.config_paths` 加载两个 server
config:

```
responses_api_models/vllm_model/configs/vllm_model_for_training.yaml
responses_api_agents/swe_agents/configs/swebench_openhands_training.yaml
```

Plus 一个 `swe_agents_train` + `swe_agents_val` 配置块。关键参数：

- `agent_max_turns: 200` — OpenHands loop 最多 200 轮
- `concurrency: 768` — 同时跑这么多 instance
- `swebench_agent_timeout: 3600` — 每 instance 1 小时上限
- `dataset_path: ${data.train.data_path}` — 走 NemoGymDataset 标准接口
- `container_formatter` — 3 个 SIF filename templates，agent 依次试

## SIF 三个 family

```python
swebench = "{sif_dir}/swebench_sweb.eval.x86_64.{instance_id}.sif"
swegym   = "{sif_dir}/swegym_sweb.eval.x86_64.{instance_id}.sif"
r2egym   = "{sif_dir}/r2egym_{instance_id}.sif"
```

| Source | M0 candidate | Upstream | License |
|---|---|---|---|
| swebench | swe_pivot_patch_supervision (existing M0) | princeton-nlp/SWE-bench_Lite | source-repository-specific |
| swegym | (Session 2) | SWE-Gym/SWE-Gym-Lite | apache-2.0 |
| r2egym | (Session 2) | nvidia/Nemotron-SWE-v1 (r2e_gym subset) | cc-by-4.0 |

**SWE2 vs SWE1 用同一个 SWE-bench Lite 数据吗？**

SWE1 是 single-step tool-call pivot（verifier `argument_match`）；SWE2 是
full agent loop（verifier `openhands_loop` — binary patch+tests）。SWE-bench
Lite 数据本身是 problem+gold_patch 对，**SWE2 那边可以直接用**（验证只
要 candidate 提交的 patch 跑通 fail_to_pass / pass_to_pass tests 就行）；
SWE1 那边数据 shape 跟 verifier 不匹配（要 single-step tool call 当 gold，
SWE-bench Lite 没有这个标注）。这就是为什么 swe1_env_registry.yaml 里
SWE-bench Lite 是 `verifier_mismatch`，但 swe2_env_registry.yaml 里同样
数据可以是 `m0_missing`（Session 2 补 trace 字段）而非 mismatch。

## instance_id 安全

`instance_id` 直接 interpolate 进文件路径，必须严格校验。SWE-Bench 实际
id 格式：

```
<org>__<repo>-<num>
e.g. astropy__astropy-12907
     django__django-14999
     scikit-learn__scikit-learn-25500
```

允许 `[A-Za-z0-9_\-]+`。拒 `/`、`\`、`..`、空字符串。`resolve_sif_path` 在
format 前用 regex 检查；test 覆盖 `..`、`a/b`、空串都 raise ValueError。

## Bridge auto-pickup

Session 2 把 M0 SWE2 trace env 加进 M0（新 transform + env_registry +
data_registry），然后改 swe2_env_registry.yaml 一行：

```yaml
- nemo_gym_env: swe_agents
  mix: swe2
  m0_env_id: swe_openhands_swegym   # 之前 null
  status: active                     # 之前 m0_missing
  sif_source: swegym
  ...
```

`prepare_m1_swe2_jsonl.py` import 时自动 pickup；`tag_record` 会从
`_m0_env_to_sif_source` lookup 找到 sif_source 加进每行。
`test_prepare_happy_path_with_synthetic_active_registry` 已经覆盖这条路径
（monkeypatch fake registry，确认 train.jsonl + lineage 都 emit 真行）。

## Three-bridge code duplication

| | m1_rlvr | m1_swe1 | m1_swe2 |
|---|---|---|---|
| Mixes | 3 (rlvr1/2/3) | 1 (swe1) | 1 (swe2) |
| NeMo-Gym targets | 21 | 1 | 1 |
| SIF sources | n/a | n/a | 3 family |
| Coverage extension | none | none | sif_source_breakdown |
| Registry loader signature | identical | identical | identical |
| derive_env_map | identical | identical (single mix) | identical (single mix) |
| coverage_report | identical | identical | extended w/ sif_source_breakdown |
| tag_record | row_index/mix tags | + swe1_* tags | + swe1_* tags + sif_source |
| collect_rows | + per-row sif_source lookup |
| prepare | calling pattern same |

抽 base 的时候要把 SWE2 的 sif_source 当作 module-specific hook，不能硬
塞进 base contract。Session 4 时候把这些 generalize。

## Sandbox vs cluster

| 任务 | sandbox? |
|---|---|
| SIF registry + resolver + validator | yes |
| SWE2 env registry + bridge skeleton + tests | yes |
| Session 2 OpenHands wrapper unit tests (mock Docker) | yes |
| Session 2 真 SWE-Gym HF 下载 | partial (sandbox 联网受限) |
| Session 3 Docker fallback 跑 1 instance smoke | depends (本地 dev workstation yes，sandbox 通常 no) |
| Session 3 cluster smoke run | no — NemTron cluster + SIF images |

## Pre-existing sandbox issue

`tests/recipes/super3/test_m1_agentic_sft.py` 在 sandbox 仍因缺 pyarrow
collect-error，pre-existing；非 sandbox 正常跑。
