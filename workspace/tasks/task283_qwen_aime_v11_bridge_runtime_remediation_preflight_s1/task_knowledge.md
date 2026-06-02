# task283_qwen_aime_v11_bridge_runtime_remediation_preflight_s1 - Task Knowledge

<!-- METADATA:SESSION=2 -->

## Knowledge Entries

1. task283 exists because task278/task279 proved the current no-training
   config/import preflight is blocked by missing NeMo/Megatron-Bridge runtime
   imports, not by task276 packed data.
2. task283 may reconcile environment differences and produce no-training
   import/config/load proof, but it must not start optimization or run any
   training/eval path.
3. A PASS requires reviewer-readable proof of a usable Qwen3-4B
   NeMo/Megatron-Bridge route against task276 packed data and fail-closed
   no-training guards.
4. A BLOCK is acceptable if no route exists without forbidden system changes,
   scheduler credentials, or training/eval execution.
5. Even a PASS does not by itself authorize nonzero-LR smoke. It must be
   independently reviewed by task284 and then processed by lead.
6. task283 starts after task278/#347 merged into main as
   `28039222ad5d4054891713d85d05a15a491d8a96`; the task278 branch-only
   closeout is not required for task283 evidence.
7. `NemTron` can currently import `nemo`, `megatron.bridge`,
   `megatron.bridge.training.config`, and `AutoBridge.import_ckpt`, but Qwen
   recipe import needs a task-owned venv layer with `megatron-energon` and its
   small import-time support packages.
8. A minimal task-owned `--system-site-packages` venv with targeted `--no-deps`
   installs through `webdataset==1.0.2` is enough for
   `megatron.bridge.recipes.qwen.qwen3` import and Qwen `ConfigContainer`
   build against task276 packed data.
9. The current route is not a full training environment: `pip check` remains
   rc `1`, full `stage1_sft.train` import still needs
   `nvidia_resiliency_ext`, and `nemo.collections.llm` still needs
   `lightning`.
