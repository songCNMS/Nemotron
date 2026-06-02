# task278_qwen_aime_v11_task276_config_import_preflight_s1 - Task Knowledge

<!-- METADATA:SESSION=0 -->

## Knowledge Entries

1. task278 uses task276 packed root
   `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen`.
2. task278 must use Qwen3-4B path
   `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
3. task278 may only prove no-training config/import readiness; it cannot run
   nonzero-LR training, live canary, AIME eval, export, endpoint, or promotion.
4. Sparse valid/test risk is accepted for packed-data evidence only and must be
   carried into preflight evidence.
