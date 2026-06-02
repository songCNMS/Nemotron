# task278_qwen_aime_v11_task276_config_import_preflight_s1 - Task Knowledge

<!-- METADATA:SESSION=4 -->

## Knowledge Entries

1. task278 uses task276 packed root
   `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen`.
2. task278 must use Qwen3-4B path
   `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
3. task278 may only prove no-training config/import readiness; it cannot run
   nonzero-LR training, live canary, AIME eval, export, endpoint, or promotion.
4. Sparse valid/test risk is accepted for packed-data evidence only and must be
   carried into preflight evidence.
5. The task starts from `origin/main`
   `793e7dfa73ed1c5bdc8b7b98df5f31ffdd5e38ea`, immediately after task276/#344
   merged.
6. Local CPU host `lg-cmc-b7r201-n09u29-cpu-000191` can validate task276 packed
   data, Qwen contracts, and Qwen HF config/tokenizer import, but cannot import
   the full training stack because `nemo` and `megatron` are not installed.
7. task278 official artifact root
   `/work-agents/intern_nemotron_worker_2/outputs/task278_qwen_aime_v11_task276_config_import_preflight_s1/run_20260602T044941Z`
   has disposition `CONFIG_IMPORT_PREFLIGHT_BLOCKED_MISSING_MEGATRON_BRIDGE`;
   next remediation is a task-owned NemTron/NeMo/Megatron-Bridge no-training
   import preflight, not a training launch.
8. Session 3 synced the branch to
   `/root/task278_qwen_aime_v11_task276_config_import_preflight_s1/Nemotron`
   and reran the same helper from `/root`; the result remains blocked because
   Docker daemon, `nvidia-smi`, `srun`, `enroot`, `singularity`, `nemo`, and
   `megatron` are unavailable on the host.
9. Current strongest task278 artifact is
   `/work-agents/intern_nemotron_worker_2/outputs/task278_qwen_aime_v11_task276_config_import_preflight_s1/run_20260602T045642Z`,
   with manifest sha256
   `57b0a9d5ce51dd3f48514b802e8cfaff973a8ad297df466ef551d86f84840692`.
10. PR #347 merged as blocker/preflight evidence only at approved exact head
    `b7e544100ac13eaa908a9d1af6fafaf599bc3310` with merge commit
    `28039222ad5d4054891713d85d05a15a491d8a96`; it does not release runtime
    remediation or any training/eval/export/promotion action.
