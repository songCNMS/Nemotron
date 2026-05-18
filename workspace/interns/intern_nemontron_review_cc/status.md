# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task014_m1_rlvr_data_bridge -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task014_m1_rlvr_data_bridge |
| PR | pending push |
| Session | 21 |

正在做：task014 Session 1 — M0 → RLVR1 数据 bridge。新模块
`src/nemotron/recipes/super3/milestones/m1_rlvr/prepare_m1_rlvr_jsonl.py`
读 M0 split 文件 + 按 `RLVR1_ENV_MAP` 过滤到 4 个 env (math/code/search/
tool-calling)，给每行打 `nemo_gym_env` + `nemo_gym_mix` tag，输出
`train.jsonl` / `val.jsonl` / `manifest.json` (含 lineage block 指 M0
manifest)。`MIX_PROFILES` 预留 rlvr2/rlvr3 槽 (env_map 暂空，task015 接)。
9 个新 pytest case；sandbox 测试基线 60 → 66 passed。Session 2 (RLVR1 config
wiring + smoke launcher) 需要集群，不在本 PR。
