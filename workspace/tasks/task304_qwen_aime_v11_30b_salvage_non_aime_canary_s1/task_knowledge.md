# task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1 - task knowledge

<!-- METADATA:SESSION=3 -->

## Knowledge Entries

1. task301 checkpoint `iter_0000035` is a salvage candidate, not a clean
   training PASS. Validation did not complete and `train_rc=1`.
2. task303 approved only later non-AIME canary consideration:
   `APPROVE_SALVAGE_CANDIDATE_FOR_LATER_NON_AIME_CANARY_CONSIDERATION_ONLY`.
3. Candidate checkpoint path:
   `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/checkpoints/iter_0000035`.
4. Model/tokenizer path:
   `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
5. task301 saved with TP `4`, PP `2`, EP `4`, ETP `1`, sequence parallel, and
   8x H200. task304 may use only the minimum resources required to load/generate
   from that checkpoint, up to the same 8x H200 route, and must document it.
6. AIME2025/task243 remains blocked until task304 passes and lead creates a
   separate corrected AIME FT-vs-base task.
7. Worker branch starts from `origin/main`
   `c94216b04bc3d71577391883d0cb76aa8c95e621`; task docs came from lead branch
   `b390ac734380b51db7226ebc0890b3778e144b5c`.
8. The accepted synthetic non-AIME prompt source for task304 is
   `src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_v11_export_load_canary_prompts.yaml`
   sha256 `150ee11dc6e8efd3c865a8e9ed8a9ab8ce4f5ee032bed383c73a6cea34f52f1c`.
9. For the 30B task301 checkpoint, `load_megatron_model` must receive explicit
   `mp_overrides` matching the checkpoint parallelism. Without this, the wrapper
   resets model parallelism to 1x and MCore distributed checkpoint validation
   fails on sharded tensor access patterns before generation.
10. Successful task304 canary evidence is under
    `/work-agents/intern_nemotron_worker_3/outputs/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/run_20260602T175458Z`
    and remote
    `/root/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/run_20260602T175458Z`.
    It is a bounded non-AIME canary PASS only, not AIME/task243 or promotion
    clearance.
11. Lead placed task304/#367 on HOLD at exact head
    `a38abd53c897b3c68878abb770cb80f762c20e6f` pending task305 independent
    review. Until lead releases after task305, task304 evidence remains pending
    gate review and must not be self-merged or used to start AIME/task243,
    export, endpoint, promotion, training, task255 reuse, AIME train-data use,
    shared deletion, or main push.
12. Lead follow-up confirmed task304/#367 at
    `e5cc49821d39a014756dfd3ce961bab351a4f0fe` and refreshed task305 worker_4
    review to that exact head. Do not make further #367 head changes, even
    status-only changes, unless lead asks; keep all downstream AIME/task243,
    export, endpoint, promotion, training, task255 reuse, AIME train-data use,
    shared deletion, and main push actions blocked.
