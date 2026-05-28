# task078_qwen_training_pipeline_contract_s1 - Task Knowledge

<!-- METADATA:SESSION=2 -->

## Knowledge Entries

1. supervisor request: PM assigned intern_nem_dev_2 to own Qwen SFT/RL training pipeline consistency and keep live training/cluster launches out of scope.
2. technical fact: PR #186 added Qwen data-prep/profile validators using `target_model_family=qwen`, `config_name=qwen_agentic_v0`, `chat_template=tokenizer`, and disabled thinking kwargs.
3. file change: `qwen_chat_contract.py` now composes Qwen data-prep config validation, packed-SFT metadata validation, and resolved training-launch validation.
4. file change: Qwen scale-up scripts now carry both the Qwen data-prep contract and `training_contract.model_profile=qwen` into generated training commands.
5. test evidence: After rebasing on `2489a87d07137fb743d70547e19ca0cf4e309645`, focused Qwen contract/planner tests, RL chat kwargs/stop strings tests, full `test_m1_agentic_sft.py`, py_compile, and `git diff --check` passed.
6. blocker: `test_stage1_sft_train_bridge.py` is skipped in this sandbox because `megatron.bridge.training.config` is not installed.
