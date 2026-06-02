# intern_nemotron_worker_2 - personal knowledge base

<!-- METADATA:SESSION=0 -->

---

## Knowledge entries

1. task283: A task-owned `NemTron` venv using `--system-site-packages` plus
   targeted `--no-deps` installs through `webdataset==1.0.2` can import
   `megatron.bridge.recipes.qwen.qwen3` and build a Qwen3-4B `ConfigContainer`
   against task276 packed data without running training.
2. task283: This route is not a full training environment; `pip check` remains
   rc `1`, `stage1_sft.train` still needs `nvidia_resiliency_ext`, and
   `nemo.collections.llm` still needs `lightning`.
