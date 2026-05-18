# task014 - task_knowledge

## M0 contract shape (这里 bridge 不动它)

M0 `prepare_m0_assets.py::make_record` 出来的每行 JSON：

```json
{
  "environment": "<m0_env_id>",
  "milestone": "M0",
  "use_stage": [...],
  "question": "...",
  "expected_answer": "...",
  "responses_create_params": {
    "input": [{"role": "system", ...}, {"role": "user", ...}],
    "tools": []
  },
  "reward_config": {"verifier": "...", ...},
  "extra_env_info": {...},
  "metadata": {"source_dataset": "...", "data_stage": "M0", ...}
}
```

NeMo-Gym 服务端 (`stage2_rl/stage1_rlvr/config/default.yaml`) 的
`nemo_gym_data_processor` 直接消费这个 shape——不需要新的 schema 转换器。

## RLVR1 4-env mix (roadmap §1.3)

| M0 env id | NeMo-Gym env name | M0 dataset |
|---|---|---|
| `math_reasoning_numeric` | `math_with_judge` | gsm8k |
| `code_execution_python` | `code_gen` | mbpp |
| `search_grounded_qa` | `search_grounded_qa` | hotpot_qa distractor |
| `general_tool_calling` | `general_tool_calling` | hermes singleturn |

RLVR2 / RLVR3 是 task015 范围 (剩 17 个 env，要 license audit + verifier
注册)。本 task014 只做 RLVR1。

## Bridge tag (不是 shape 转换)

`tag_record` 干的事很少：
- 顶层加 `nemo_gym_env`（NeMo-Gym 服务端识别字符串）+ `nemo_gym_mix`（混合名 = "rlvr1"）
- metadata 里冗余写一份 + `m0_environment`、`rlvr_row_index`、`rlvr_split`
- M0 `environment` 字段**不动**——这样:
  - health-baseline 跑同一份 JSONL 行为不变
  - lineage walker 能走 M1-RLVR → M0 raw 这条链
  - 万一 bridge 之后又要把行送回 M0 oracle 验证，原始 env id 还在

## 下游 (`SplitJsonlDataArtifact`)

`stage2_rl/_data_prep_base.py::run_substage_data_prep` 走两条路：
1. `resolve_hf_placeholders=True` → `run_resolve_and_split` (pipeline 路径)
2. 否则 → `split_local_jsonl` (直 split 路径)

Bridge 输出已经是 train/val 分文件，所以 Session 2 应该走"直 split 路径"
+ `val_holdout=0` (因为本 bridge 已经分好)，或者改 `_data_prep_base.py` 加
一个 "已分 train/val" 的快捷分支。Session 2 决定怎么接。

## Lineage chain

```
RawDataArtifact (M0 manifest)
    ↓ kind=manifest
SFTDataArtifact (M1 SFT manifest) — task021 Session 2 已接
    ↓ kind=manifest (待将来 RLVR 不从 SFT 走，而是从 M0 走数据 + 从 SFT 走 checkpoint)

RLVR1 (本 task014 Session 1)
    ↑ kind=manifest 指 M0 manifest (数据来源)
    [Session 3+: 加 kind=checkpoint 指 SFT ModelArtifact-sft]
```

注意：RLVR 的 lineage 输入只是数据来源 (M0)，**不是 SFT model**。SFT model
是另一条 `kind=checkpoint` 输入，留给将来 task021 Session 3+ 接。

## sandbox-vs-cluster 分界

| 任务 | sandbox? |
|---|---|
| `prepare_m1_rlvr_jsonl.py` 跑 + 写 manifest + lineage | yes |
| pytest 覆盖 (~9 cases) | yes |
| `nemotron super3 rl rlvr1 -c smoke` 真起 Ray + vLLM | no — 需 NemTron cluster + GPU |
| 验证 NeMo-Gym verifier 对每行 reward 返回数值 | partial — verifier 在外部 repo |

所以 Session 1 走得通；Session 2 接好 config + 在集群验证。

## pre-existing sandbox issue

`tests/recipes/super3/test_m1_agentic_sft.py` 在 sandbox 上 `pyarrow` 缺失
collect-error (main 也复现)。Session 1 不修——属于 pytest 环境治理，不属
于 RLVR bridge 范围；可以单独 PR 加 `pytest.importorskip("pyarrow")`。
