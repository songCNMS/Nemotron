# task298_qwen_aime_v11_30b_runtime_resource_base_load_s1 - task knowledge

<!-- METADATA:SESSION=4 -->

## Knowledge Entries

1. gate: 30B scale-up cannot train or test until a 30B runtime/resource/base-load
   route is proven or explicitly blocked.
2. model-path: Primary candidate is
   `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
3. boundary: Eval-only export/endpoint may be identified if required for
   testing, but it is not promotion or release clearance.
4. evidence: `run_20260602T143838Z` proved current-main 30B no-training
   runtime/config/import and task-owned Bridge base import on NemTron host
   `lg-cmc-b7r201-f08u26-h200-000126`.
5. resource: current 30B entrypoint is
   `src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py`;
   built config uses 8 H200s with TP=4, PP=2, EP=4, ETP=1, sequence parallel,
   GBS=8, and MBS=1.
6. eval-route: base HF model can use an eval-only SGLang endpoint directly;
   future Megatron SFT checkpoint comparison should use eval-only HF export
   plus SGLang endpoint unless a separate 30B no-export MCore load route is
   proven.
