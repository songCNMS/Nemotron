# intern_nem_dev_2 - 状态

<!-- METADATA:STATUS=Working,TASK=task203_qwen_live_sft_train_smoke_s1,ROLE=independent -->

| 字段 | 值 |
|------|-----|
| Name | intern_nem_dev_2 |
| Status | Working |
| Current Task | task203_qwen_live_sft_train_smoke_s1 |
| PR | Evidence-only branch: intern_nem_dev_2/task203_qwen_live_sft_train_smoke_s1 |
| Session | 1 |

最近进展：Completed evidence-only `task203_qwen_live_sft_train_smoke_s1` validation on branch `intern_nem_dev_2/task203_qwen_live_sft_train_smoke_s1` from synced `main` `0460c1f0262875fb27ae530d30cd80d805752851`. Dry-run passed (`rc=0`, 3s) with resolved evidence for `test_train.py`, fallback packed data, Qwen profile, requested tokenizer path, and checkpoint save path. Focused SFT/Qwen validators passed (`33 passed, 2 skipped`, 3s). One-iteration local smoke was not run because `/work-agents/.venv` lacks `torch`, `megatron`, and `megatron.bridge`; the requested `/mnt/3fs` Qwen model path is absent, so CUDA availability cannot be established. Evidence logs are under `/tmp/nemotron-live-validation/task203/logs`. Boundaries preserved: no full training, endpoint evals, W&B/cluster/deploy/artifact upload, direct main/master push, or self-merge.
