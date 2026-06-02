# task291_qwen_aime_v11_no_export_canary_route_unblock_s1 - task knowledge

<!-- METADATA:SESSION=2 -->

1. task291 exists because task287 can load the task285 iter2 checkpoint but
   cannot produce retained completions through the allowed no-export/no-endpoint
   route.
2. task291 may run one-GPU no-training in-process generation/canary probes on
   synthetic non-AIME prompts only. It may not run AIME/task243 or export/launch
   an endpoint.
3. A task291 pass is still not an AIME release. It only unblocks a later
   independent review and possible corrected AIME2025 same-harness task.
4. The task291 route pass at source head `dfb6ca64` uses in-process MCore
   static generation with `top_k=1` greedy sampling and no export or endpoint.
5. The task285 iter2 checkpoint load proof is through `load_megatron_model` on
   one visible H200, producing a `Float16Module` on `cuda:0` in bf16 eval mode.
6. One canary row required retaining text by detokenizing `generated_tokens`
   because MCore `request.generated_text` was empty even though token ids
   decoded to `ready, set, go.\n\nFinal Answer: go`.
