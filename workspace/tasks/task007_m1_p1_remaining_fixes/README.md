# task007_m1_p1_remaining_fixes

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_review_cc -->

## 背景

PR #11 (task004) 与 PR #12 (task006) 合主干后，REVIEW_v0.md 的 P0 两条 (#1 #2 N2) 与 P1 中"一行修"两条 (#3 N1) 已 ✓ Fixed。剩余 P1 三条全部牵涉 SFT supervision 设计或端到端验证：

- **#4 empty-content guard for all envs**：PR #10 只给 `general_tool_calling` 加了 metadata.warning，math/code/search 完全没有空 assistant 守卫。M0 task001 已为 hermes 转换加过 `raise ValueError`；M1 同类问题需要 mirror。
- **#11 `search_grounded_qa` supervision 是裸短答案**：`assistant_for_search` 仍只 emit `expected_answer.strip()`，HotpotQA 答案变成"London"这种一两词。plan §8 的 "search pattern" 要训"先看 passages 再答"，需要 grounded template。
- **#14 tool role loss_mask 端到端验证**：PR #10 加了 `tool_call_id` round-trip，但 `tool` 角色 token 在 nano3 chat template + `_tokenize_chunks_with_mask` 全链路中是否 loss_mask=0 仍未端到端测试。`chat_sft_shard_core.py:70` 显示 mask 规则是 `1 if chunk["role"] == "assistant" else 0`，理论上 tool=0 已正确——需要测试断言此契约不被未来重构打破。

## 目标

把这三条 P1 全部收掉，REVIEW_v0.md v5 标 ✓ Fixed。

## 验收

- [ ] `convert_m0_record` 在 supervision_messages 拼装完毕后做一次全局守卫：若没有任何 assistant 消息带非空 content 或 tool_calls，则 raise ValueError（对所有 env，不只 tool_calling）。
- [ ] `assistant_for_search` 改成 grounded template，引用 `extra_env_info.context_documents` 中的 supporting facts 或首段。最终输出形如：
  ```
  Based on the retrieved passages, the answer is <expected_answer>.
  ```
  或更细：`Answer: <ans>\nEvidence: [n] <one sentence>`。具体格式在 PR 描述里说明权衡。
- [ ] 加一个 tool-role loss_mask end-to-end 测试：构造含 tool 角色的 supervision，过 `create_masked_messages` → `_tokenize_chunks_with_mask`（或更轻量的 chunk → role assertion），断言 tool 段全部 loss_mask=0、assistant 段全部 1、system/user 段全部 0。
- [ ] 全套 pytest 绿；REVIEW_v0.md v5 标 #4 / #11 / #14 ✓ Fixed by task007 PR。

## 参考
- task001 history_log 中 hermes 拒空 expected 的实现（M0 prepare_m0_assets.transform_hermes_function_calling）
- M0 hotpotqa converter (`transform_hotpotqa_search`) 已经把 supporting_facts 写入 `extra_env_info.supporting_facts` 与 `extra_env_info.context_documents`，可直接消费
- `src/nemotron/data_prep/core/chat_sft_shard_core.py:60-75` `_tokenize_chunks_with_mask`
- `src/nemotron/data_prep/core/chat_template.py` `create_masked_messages`
