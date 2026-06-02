# task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1 - Task Knowledge

<!-- METADATA:SESSION=4 -->

## Knowledge Entries

1. task283/#349 plus task284 approval clears only no-training runtime/config
   import readiness. It does not prove `AutoBridge.import_ckpt`, full
   `stage1_sft.train` import, or training execution.
2. task255 failed the hard acceptance rule and showed missing/invalid base-load
   evidence plus zero-LR behavior; task285 must not repeat either failure mode.
3. The accepted task276 packed root is smoke-usable only with its sparse
   valid/test risk carried. Smoke loss/validation output is not a model-quality
   claim.
4. A valid task285 PASS requires first-step LR `> 0`, finite train loss, and
   positive Qwen3-4B base-load/import evidence before optimizer execution.
5. Even a task285 PASS only enables independent review and a separate canary gate;
   it does not authorize AIME/task243 eval, export, endpoint, promotion, 30B, or
   8-GPU scale.
6. task285 retry3 produced bounded smoke evidence despite command rc `1`:
   the two permitted optimizer iterations completed with nonzero LR, finite
   losses, and iter-2 checkpoint artifacts before the process was terminated in
   post-train built-in validation. Treat the checkpoint as smoke evidence with
   residual post-train eval/SIGTERM risk, not as quality or promotion evidence.
