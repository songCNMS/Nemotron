# task016 - task_knowledge

## NeMo-Gym envs in stage2_swe1/config/default.yaml

只有一个 server config:

```
resources_servers/single_step_tool_use_with_argument_comparison/
  configs/swe_pivot_single_step_tool_use_with_argument_comparison.yaml
```

Verifier 家族跟 RLVR1 的 `single_step_tool_use_with_argument_comparison`
一样：比对 candidate emit 的首个 tool call (name + arguments) vs gold pivot
call。SWE 上下文：从一个 SWE issue 开始，policy 决定第一步去看哪个文件、
search 什么关键字、edit 哪行 — 这一步对了就算成。

## SWE1 ≠ RLVR

虽然 verifier family 一样，但：

| | RLVR1 single_step | SWE1 swe_pivot_single_step |
|---|---|---|
| Source data | Hermes function calling | SWE-Gym / R2E-Gym (待实现) |
| Tool schema | 任意 fn calling | repo-aware (view_file, search, edit, run_tests, ...) |
| Reward signal | arg name+value 严格匹配 | 同 family 但 pivot 决策语义 |
| Mix | rlvr1 | swe1 (单独 stage) |

所以 SWE1 不能复用 RLVR1 的 M0 hermes 数据 — 需要单独的 M0 SWE pivot env。

## 已有 M0 SWE 数据：SWE-bench Lite

M0 `swe_pivot_patch_supervision`:
- 源：`princeton-nlp/SWE-bench_Lite`
- Verifier: `patch_diff_match` (compare emitted unified-diff to gold patch)

这是 patch-diff style，**不是** single-step tool-call pivot。同 domain
不同 reward shape — 登记成 `verifier_mismatch` 让 coverage 看得见，但不
默认 active。

未来如果想 opt-in: 加 `--include-mismatched` flag（Session 3+）。

## Session 2 候选数据源

### SWE-Gym-Lite
- HF: `SWE-Gym/SWE-Gym-Lite`
- License: apache-2.0
- 内容: 类似 SWE-bench 的 issue / solution 对，外加 agent trajectory
- 提取方法：从 trajectory 第一个真实有效 tool call 抽 ground truth

### R2E-Gym
- HF: `nvidia/Nemotron-SWE-v1` 的 `r2e_gym` 子集
- License: CC-BY-4.0
- 内容: R2E (repo-level eval) 环境的 issue / fix 对
- 可能不带 trajectory — 需 hueristic 提 pivot

待 Session 2 看真数据 shape 再决定。

## Bridge auto-pickup 机制

Session 2 把 M0 SWE pivot env 加进 M0 (新 transform + env_registry +
data_registry 行)，然后改 swe1 registry：

```yaml
# swe1_env_registry.yaml
- nemo_gym_env: swe_pivot_single_step_tool_use_with_argument_comparison
  mix: swe1
  m0_env_id: swe_pivot_argument_comparison   # 之前 null
  status: active                              # 之前 m0_missing
  m0_verifier: argument_match
  ...
```

Bridge import 时自动把这行加进 SWE1_ENV_MAP。下一次 prepare() 就 emit
真行；测试 `test_prepare_happy_path_with_synthetic_active_registry` 已经
覆盖了这条路径。

## sandbox vs cluster

| 任务 | sandbox? |
|---|---|
| `swe1_env_registry.yaml` + `prepare_m1_swe1_jsonl.py` + pytest | yes |
| Session 2 converter unit tests (用 synthetic SWE-Gym 行) | yes |
| Session 2 真 HF 下载 + 全量 convert | partial (sandbox 联网受限) |
| Session 3 cluster smoke run | no — NemTron cluster + NeMo-Gym swe_pivot server |

## DRY 决策

`prepare_m1_swe1_jsonl.py` 跟 `prepare_m1_rlvr_jsonl.py` 重复 ~80% (registry
loader, derive_env_map, coverage_report, read/write helpers, tag_record,
collect_rows, prepare 主流程)。

不抽 base 模块的原因：
- task016 Session 1 只是第二份，过早抽象 + 测试覆盖反而拖慢
- 第三份 SWE2 (task017) 落下来时一起抽，结构会更清晰
- registries 字段差别小（SWE1 只 1 个 nemo_gym_env，RLVR 是 21；SWE1 single
  mix，RLVR 3 mixes），base 抽出来要参数化好几条 dimension

抽取时候要考虑：
- 多 mix vs single mix profile shape
- 不同 mix 的字段（rlvr_row_index vs swe1_row_index 这种 metadata key）
- artifact_type / lineage output kinds 命名约定

## Pre-existing sandbox issue

`tests/recipes/super3/test_m1_agentic_sft.py` 在 sandbox 仍因缺 pyarrow
collect-error，main 一样复现 pre-existing；非 sandbox 环境正常跑。不在
本 PR 范围。
