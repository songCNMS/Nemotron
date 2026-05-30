# intern_nem_dev_2 - 状态

<!-- METADATA:STATUS=Working,TASK=task206_qwen_sft_train_stack_unblock_probe_s1,ROLE=independent -->

| 字段 | 值 |
|------|-----|
| Name | intern_nem_dev_2 |
| Status | Working |
| Current Task | task206_qwen_sft_train_stack_unblock_probe_s1 |
| PR | Evidence-only branch: intern_nem_dev_2/task206_qwen_sft_train_stack_unblock_probe_s1 |
| Session | 1 |

最近进展：Completed evidence-only `task206_qwen_sft_train_stack_unblock_probe_s1` on branch `intern_nem_dev_2/task206_qwen_sft_train_stack_unblock_probe_s1` from baseline `0460c1f0262875fb27ae530d30cd80d805752851`. Primary and bounded alternate env probes found only `/work-agents/.venv/bin/python`, with `nemo_run` present but `torch`, `megatron`, and `megatron.bridge` absent; `conda` and `nvidia-smi` are not available. Requested Qwen path `/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507` and fresh task205 splits are absent; fallback task071 packed splits/blend exist. Mandatory dry-run passed (`rc=0`, 3s), focused validators passed (`33 passed, 2 skipped`, 2s), and one-iteration smoke was skipped because prerequisites are missing. Evidence logs are under `/tmp/nemotron-live-validation/task206/logs`. Boundaries preserved: no package install, cluster launch, full train/eval, endpoint, W&B/deploy/artifact upload, direct main/master push, or self-merge.
