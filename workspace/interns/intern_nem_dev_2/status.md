# intern_nem_dev_2 - 状态

<!-- METADATA:STATUS=Working,TASK=task078_qwen_training_pipeline_contract_s1 -->

| 字段 | 值 |
|------|-----|
| Name | intern_nem_dev_2 |
| Status | Working |
| Current Task | task078_qwen_training_pipeline_contract_s1 |
| PR | https://github.com/songCNMS/Nemotron/pull/185 |
| Session | 1 |

最近进展：PM requested PR #185 rebase after PR #186; fetched `origin/main` at `2489a87d07137fb743d70547e19ca0cf4e309645`, rebased `intern_nem_dev_2/task078_qwen_training_pipeline_contract_s1`, and resolved conflicts by composing PR #186 Qwen data-prep/profile guards with PR #185 training-contract/profile plumbing. Required Qwen/RL/M1 checks, py_compile, and `git diff --check` passed; `test_stage1_sft_train_bridge.py` is skipped because `megatron` is not installed.
