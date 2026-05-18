# history_log

<!-- METADATA:SESSION=1 -->

## Session 0 - 2026-05-18 - intern_nemontron_review_cc

由 roadmap §5 critical-path 第 4 条派生。task014 整 task：M0 → RLVR1 数据
bridge + smoke launcher。整块一个 PR 装不下 (launcher 真验证要集群)，所
以拆 Session 1 / Session 2。

## Session 1 - 2026-05-18 - intern_nemontron_review_cc

实现 M0 → RLVR1 JSONL bridge。设计选择 + 实现要点：

- 新模块 `src/nemotron/recipes/super3/milestones/m1_rlvr/prepare_m1_rlvr_jsonl.py`
  完全 parallel `prepare_m1_agentic_sft.py` (sibling 模板)。
- M0 record 本身已经按 NeMo-Gym 合约 shape (`environment`,
  `responses_create_params.{input,tools}`, `reward_config`, `extra_env_info`)
  emit，所以 bridge 不做 shape 转换，只做：
  - **slicing**: 按 `RLVR1_ENV_MAP` 过滤；roadmap §1.3 写死 4 个 M0 env
    → 4 个 NeMo-Gym env (math_reasoning_numeric → math_with_judge / code_execution_python → code_gen / search_grounded_qa → search_grounded_qa / general_tool_calling → general_tool_calling)。
  - **tagging**: 新字段 `nemo_gym_env` + `nemo_gym_mix` (顶层 + metadata 里
    都有冗余拷贝)；**M0 `environment` 字段保留**，所以 health-baseline 跑
    同一份 JSONL 行为不变，lineage walk 也不需要二次映射。
- `MIX_PROFILES` 预留 `rlvr2` / `rlvr3` 槽 (env_map 暂空)，跑这两个 mix
  会显式 raise `ValueError(... task015 territory)`。这样配置错的人不会拿
  到一个空文件就走，而是看到该等的 ticket。
- 输出：`train.jsonl` / `val.jsonl` 单文件 (各 env mix 合并) + `manifest.json`
  + `report.md`。manifest 的 shape 跟 `SplitJsonlDataArtifact` 兼容：未来
  Session 2 让 `_data_prep_base.split_local_jsonl` 直接读这个 artifact。
- Lineage block：artifact_type=`RLVR1`，单个 `manifest`-kind input 指
  `<m0_input_dir>/manifest.json`，outputs 是 `m1_rlvr_train_jsonl` +
  `m1_rlvr_val_jsonl`。这样 `walk_chain(rlvr_manifest)` 能从 RLVR1 一路
  走回 M0 RawDataArtifact，跟 M1 SFT 那条链路 parallel。
- 测试 `tests/recipes/super3/test_m1_rlvr_data_bridge.py` (9 cases):
  env_map coverage / rlvr2 + rlvr3 reserved / tag_record 单测 / prepare
  end-to-end / 非-rlvr1 env 过滤 / missing split 进 manifest.errors /
  lineage 指 M0 / unknown mix raises / rlvr2 unbuildable raise。
- Roadmap §1.3 task014 + §5 critical-path 加 Session 1 ✓ + Session 2 ☐ 切片。

测试基线：66 passed (M0 + lineage + chat_template + rlvr_bridge)。
`test_m1_agentic_sft.py` 因 sandbox 缺 pyarrow 仍 collect-error (pre-existing
issue，main 也复现，不在本 PR 范围)；非 sandbox 环境上跑应该照常通过。

Session 2 (RLVR1 smoke launcher) 不在本 PR：要动
`stage1_rlvr/config/data_prep/rlvr1.yaml` 让 input_path 指 M0 artifact，
加 `config/smoke.yaml`，并跑通真 launch path——后者需要集群 + NeMo-Gym
servers，sandbox 验证不了，等接到 NemTron cluster 再开。

## Session 2 - 2026-05-18 - intern_nemontron_review_cc

Session 1 PR #34 已 squash-merge 为 `4a50941` 进 main —
`prepare_m1_rlvr_jsonl.py` + RLVR1_ENV_MAP + 9 个新 pytest case + lineage
都进了 main。intern status 回 Idle (Session 22)。task014 整 task 仍
InProgress：Session 2 (RLVR1 config wiring + `nemotron super3 rl rlvr1
-c smoke` launcher) 没启动，要 NemTron cluster 跑真 launch path 才能
acceptance。下一个 critical-path 候选 (roadmap §5)：task015 (RLVR 21-env
mix) 或 task016 (M1 SWE1 pivot data)。

